# =============================================================================
# MODULE 5: REDIS PUB/SUB
# Lesson 4 – FastAPI + Redis Integration
# =============================================================================
# Goal: Integrate Redis Pub/Sub into the FastAPI banking API so that:
#   1. POSTing a transaction publishes an event to Redis
#   2. Background tasks process fraud detection asynchronously
#   3. A Server-Sent Events (SSE) endpoint streams live fraud alerts
#      to a browser/dashboard client
#
# Run:
#   uvicorn module_05_redis_pubsub.04_fastapi_redis:app --reload --port 8000
# =============================================================================

from __future__ import annotations

import asyncio
import json
import os
from contextlib import asynccontextmanager
from datetime import datetime
from decimal import Decimal
from typing import Optional, AsyncGenerator

import redis.asyncio as aioredis
import redis as sync_redis
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException, Path, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from module_01_python_sqlalchemy.setup_and_models import (  # type: ignore
    SessionLocal, Account, Transaction, Customer,
    TransactionTypeEnum
)
from module_05_redis_pubsub.02_transaction_publisher import (  # type: ignore
    build_transaction_event, publish_transaction, record_and_check_velocity,
    CHANNEL_FRAUD_ALERTS,
)

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# ─────────────────────────────────────────────
# 5.1  ASYNC REDIS CLIENT
# ─────────────────────────────────────────────
# redis.asyncio is the async version of the redis-py client.
# Use it inside async route handlers and background tasks.
# Sync redis (redis.Redis) is used in background threads / sync routes.

_async_redis: Optional[aioredis.Redis] = None
_sync_redis:  Optional[sync_redis.Redis] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize Redis clients on startup, close them on shutdown."""
    global _async_redis, _sync_redis

    _async_redis = aioredis.from_url(REDIS_URL, decode_responses=True)
    _sync_redis  = sync_redis.from_url(REDIS_URL, decode_responses=True)

    try:
        await _async_redis.ping()
        print("✅ Async Redis connected")
    except Exception as exc:
        print(f"⚠️  Redis not available: {exc}")

    yield

    await _async_redis.close()
    _sync_redis.close()
    print("Redis clients closed")


def get_async_redis() -> aioredis.Redis:
    if _async_redis is None:
        raise RuntimeError("Redis not initialized")
    return _async_redis


def get_sync_redis() -> sync_redis.Redis:
    if _sync_redis is None:
        raise RuntimeError("Redis not initialized")
    return _sync_redis


# ─────────────────────────────────────────────
# DATABASE SESSION DEPENDENCY
# ─────────────────────────────────────────────

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ─────────────────────────────────────────────
# 5.2  SCHEMAS
# ─────────────────────────────────────────────

class TransactionRequest(BaseModel):
    transaction_type: str
    amount:           float
    description:      Optional[str] = None


class TransactionResponse(BaseModel):
    transaction_id:   int
    account_id:       int
    transaction_type: str
    amount:           float
    balance_after:    float
    transaction_date: datetime
    event_published:  bool


# ─────────────────────────────────────────────
# 5.3  BACKGROUND TASK: fraud check
# ─────────────────────────────────────────────
# FastAPI's BackgroundTasks runs functions after the HTTP response is sent.
# Perfect for non-blocking side effects like publishing to Redis.

def check_and_flag_fraud_bg(event: dict, r_client: sync_redis.Redis) -> None:
    """Background task: apply basic fraud rules and publish alerts."""
    account_id = event["account_id"]
    amount     = event["amount"]

    LARGE_TX_THRESHOLD = 10_000.00
    VELOCITY_LIMIT     = 3

    if amount >= LARGE_TX_THRESHOLD:
        alert = {
            "event":           "fraud.detected",
            "customer_id":     event["customer_id"],
            "account_id":      account_id,
            "alert_type":      "Large Transaction",
            "amount_at_risk":  amount,
            "severity":        "HIGH",
            "description":     f"${amount:.2f} exceeds large-tx threshold",
            "source_tx_id":    event["transaction_id"],
            "detected_at":     datetime.utcnow().isoformat() + "Z",
        }
        r_client.publish(CHANNEL_FRAUD_ALERTS, json.dumps(alert, default=str))
        print(f"[BG] 🚨 Large-tx fraud alert published for account {account_id}")

    velocity = record_and_check_velocity(account_id, event["transaction_id"])
    if velocity >= VELOCITY_LIMIT:
        alert = {
            "event":           "fraud.detected",
            "customer_id":     event["customer_id"],
            "account_id":      account_id,
            "alert_type":      "Velocity Check",
            "amount_at_risk":  amount,
            "severity":        "HIGH" if amount > 1000 else "MEDIUM",
            "description":     f"{velocity} transactions in 60s",
            "source_tx_id":    event["transaction_id"],
            "detected_at":     datetime.utcnow().isoformat() + "Z",
        }
        r_client.publish(CHANNEL_FRAUD_ALERTS, json.dumps(alert, default=str))
        print(f"[BG] 🚨 Velocity fraud alert for account {account_id} ({velocity} txns/60s)")


# ─────────────────────────────────────────────
# 5.4  THE TRANSACTION ENDPOINT WITH REDIS PUBLISH
# ─────────────────────────────────────────────

app = FastAPI(
    title    = "First National Bank — API with Redis Pub/Sub",
    version  = "3.0.0",
    lifespan = lifespan,
)


@app.post(
    "/accounts/{account_id}/transactions",
    response_model=TransactionResponse,
    status_code=201,
    tags=["Transactions"],
)
def post_transaction(
    account_id:       int                = Path(...),
    data:             TransactionRequest = ...,
    db:               Session            = Depends(get_db),
    background_tasks: BackgroundTasks    = ...,
):
    """Post a transaction, update the account balance, and publish a Redis event.

    The Redis publish happens in a background task so it doesn't block the response.
    """
    account = db.get(Account, account_id)
    if account is None:
        raise HTTPException(status_code=404, detail=f"Account {account_id} not found")
    if not account.is_active:
        raise HTTPException(status_code=400, detail="Account is inactive")

    DEBIT_TYPES = {"withdrawal", "transfer_out", "fee", "atm_withdrawal"}
    amount = Decimal(str(data.amount))
    if data.transaction_type in DEBIT_TYPES and account.balance < amount:
        raise HTTPException(status_code=422, detail="Insufficient funds")

    account.balance += amount if data.transaction_type not in DEBIT_TYPES else -amount

    txn = Transaction(
        account_id       = account_id,
        transaction_type = TransactionTypeEnum(data.transaction_type),
        amount           = amount,
        transaction_date = datetime.utcnow(),
        description      = data.description,
        balance_after    = account.balance,
    )
    db.add(txn)
    db.commit()
    db.refresh(txn)

    # Build the Redis event after successful DB commit
    customer_id = account.customer_id
    event = build_transaction_event(
        transaction_id   = txn.transaction_id,
        account_id       = account_id,
        customer_id      = customer_id,
        transaction_type = data.transaction_type,
        amount           = float(amount),
        balance_after    = float(account.balance),
        description      = data.description,
    )

    # Publish to Redis as a background task (non-blocking)
    r_client = get_sync_redis()
    background_tasks.add_task(publish_transaction, event)
    background_tasks.add_task(check_and_flag_fraud_bg, event, r_client)

    return TransactionResponse(
        transaction_id   = txn.transaction_id,
        account_id       = account_id,
        transaction_type = data.transaction_type,
        amount           = float(amount),
        balance_after    = float(account.balance),
        transaction_date = txn.transaction_date,
        event_published  = True,
    )


# ─────────────────────────────────────────────
# 5.5  SERVER-SENT EVENTS (SSE) — live fraud alert stream
# ─────────────────────────────────────────────
# SSE is a simple HTTP protocol for server → browser push.
# The client opens one long-lived GET request; the server streams events.
# No WebSocket library required — just a StreamingResponse.
#
# Open in a browser or with curl:
#   curl -N http://localhost:8000/stream/fraud-alerts

async def fraud_alert_generator() -> AsyncGenerator[str, None]:
    """Async generator that yields SSE-formatted fraud alert messages."""
    ar = get_async_redis()
    pubsub = ar.pubsub(ignore_subscribe_messages=True)
    await pubsub.subscribe(CHANNEL_FRAUD_ALERTS)

    try:
        async for message in pubsub.listen():
            if message is None:
                continue
            if message["type"] != "message":
                continue
            # SSE format: "data: <json>\n\n"
            yield f"data: {message['data']}\n\n"
    except asyncio.CancelledError:
        pass
    finally:
        await pubsub.unsubscribe(CHANNEL_FRAUD_ALERTS)
        await pubsub.close()


@app.get(
    "/stream/fraud-alerts",
    tags=["Streaming"],
    summary="Live fraud alert stream (Server-Sent Events)",
    response_class=StreamingResponse,
)
async def stream_fraud_alerts():
    """
    Opens a persistent SSE connection that streams fraud alerts in real time.

    Connect with:
      curl -N http://localhost:8000/stream/fraud-alerts

    JavaScript (browser):
      const es = new EventSource('/stream/fraud-alerts');
      es.onmessage = e => console.log(JSON.parse(e.data));
    """
    return StreamingResponse(
        fraud_alert_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",       # disable nginx buffering
        },
    )


# ─────────────────────────────────────────────
# 5.6  HEALTH CHECK WITH REDIS PING
# ─────────────────────────────────────────────

@app.get("/health", tags=["Meta"])
async def health():
    ar = get_async_redis()
    try:
        pong = await ar.ping()
        redis_status = "ok" if pong else "no-pong"
    except Exception as exc:
        print(f"[HEALTH] Redis error: {exc}")
        redis_status = "error"

    try:
        with SessionLocal() as db:
            from sqlalchemy import text
            db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as exc:
        print(f"[HEALTH] Database error: {exc}")
        db_status = "error"

    return {
        "status":   "ok" if redis_status == "ok" and db_status == "ok" else "degraded",
        "redis":    redis_status,
        "database": db_status,
    }


@app.get("/", tags=["Meta"])
def root():
    return {
        "message": "Banking API v3 (with Redis Pub/Sub)",
        "docs":    "/docs",
        "stream":  "/stream/fraud-alerts",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "module_05_redis_pubsub.04_fastapi_redis:app",
        host="0.0.0.0", port=8000, reload=True,
    )
