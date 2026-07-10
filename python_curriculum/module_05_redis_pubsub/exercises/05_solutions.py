# =============================================================================
# MODULE 5: SOLUTIONS
# =============================================================================

from __future__ import annotations

import asyncio
import json
import os
import time
from datetime import date, datetime
from typing import Optional, List

import redis
import redis.asyncio as aioredis
from fastapi import FastAPI, Depends, HTTPException, Path, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

r_sync  = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


# ──────────────────────────────────────────────
# EXERCISE 1 — Low balance alert publisher
# ──────────────────────────────────────────────

LOW_BALANCE_THRESHOLD  = 500.00
CHANNEL_BALANCE_LOW    = "accounts:balance_low"
CHANNEL_TRANSACTIONS   = "transactions:new"


def publish_with_low_balance_check(
    account_id:     int,
    customer_id:    int,
    transaction_id: int,
    new_balance:    float,
    event:          dict,
) -> None:
    """Publish the transaction event and optionally a low-balance alert."""
    r_sync.publish(CHANNEL_TRANSACTIONS, json.dumps(event, default=str))

    if new_balance < LOW_BALANCE_THRESHOLD:
        alert = {
            "event":         "account.balance_low",
            "account_id":    account_id,
            "customer_id":   customer_id,
            "new_balance":   new_balance,
            "transaction_id": transaction_id,
            "threshold":     LOW_BALANCE_THRESHOLD,
            "timestamp":     datetime.utcnow().isoformat() + "Z",
        }
        r_sync.publish(CHANNEL_BALANCE_LOW, json.dumps(alert, default=str))
        print(f"⚠️  Low balance alert published: account={account_id}  balance=${new_balance:.2f}")


# ──────────────────────────────────────────────
# EXERCISE 2 — Daily transaction counter
# ──────────────────────────────────────────────

DAILY_TX_LIMIT = 10


def run_daily_counter_subscriber():
    """Count daily transactions per account using a Redis HASH."""
    pubsub = r_sync.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe(CHANNEL_TRANSACTIONS)
    today = date.today().isoformat()
    hash_key = f"daily_tx_count:{today}"

    print(f"Daily Counter started. Tracking {CHANNEL_TRANSACTIONS!r}…")
    try:
        for message in pubsub.listen():
            if message is None or message["type"] != "message":
                continue
            event = json.loads(message["data"])
            account_id = str(event.get("account_id"))

            # Increment counter for this account
            count = r_sync.hincrby(hash_key, account_id, 1)
            r_sync.expire(hash_key, 86400)  # expire tomorrow

            if count == DAILY_TX_LIMIT + 1:
                print(f"⚠️  Account {account_id} exceeded {DAILY_TX_LIMIT} transactions today "
                      f"(count={count})")
            else:
                print(f"Account {account_id}: {count} transaction(s) today")

    except KeyboardInterrupt:
        print("Daily Counter stopped.")
    finally:
        pubsub.close()


# ──────────────────────────────────────────────
# EXERCISE 3 — Recent events endpoint
# ──────────────────────────────────────────────

app = FastAPI(title="Module 5 Solutions")


@app.get("/accounts/{account_id}/recent-events", tags=["Accounts"])
async def get_recent_events(
    account_id: int   = Path(...),
    timeout_s:  float = 5.0,
    max_events: int   = 20,
):
    """Collect up to max_events from the account's Redis channel for timeout_s seconds."""
    channel = f"accounts:{account_id}:events"
    events: List[dict] = []

    ar = aioredis.from_url(REDIS_URL, decode_responses=True)
    pubsub = ar.pubsub(ignore_subscribe_messages=True)
    await pubsub.subscribe(channel)

    try:
        deadline = asyncio.get_event_loop().time() + timeout_s
        while len(events) < max_events:
            remaining = deadline - asyncio.get_event_loop().time()
            if remaining <= 0:
                break
            try:
                message = await asyncio.wait_for(
                    pubsub.get_message(ignore_subscribe_messages=True),
                    timeout=min(remaining, 0.5),
                )
            except asyncio.TimeoutError:
                break

            if message and message["type"] == "message":
                events.append(json.loads(message["data"]))
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.close()
        await ar.close()

    return {"account_id": account_id, "event_count": len(events), "events": events}


# ──────────────────────────────────────────────
# EXERCISE 4 — Rate limiter dependency
# ──────────────────────────────────────────────

RATE_LIMIT     = 5           # max requests per window
RATE_WINDOW_S  = 60          # seconds


def check_rate_limit(customer_id: int) -> None:
    """
    Raise HTTP 429 if customer has made >= RATE_LIMIT requests in the last 60 seconds.
    Uses a Redis sorted set with timestamp scores.
    """
    key    = f"rate:{customer_id}"
    now    = time.time()
    cutoff = now - RATE_WINDOW_S

    pipe = r_sync.pipeline()
    pipe.zremrangebyscore(key, "-inf", cutoff)
    pipe.zadd(key, {str(now): now})
    pipe.zcard(key)
    pipe.expire(key, RATE_WINDOW_S)
    results = pipe.execute()

    request_count = results[2]
    if request_count > RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: {RATE_LIMIT} requests per {RATE_WINDOW_S}s allowed.",
            headers={"Retry-After": str(RATE_WINDOW_S)},
        )


# Usage in a route:
#   @app.get("/customers/{customer_id}/accounts")
#   def get_accounts(customer_id: int, _: None = Depends(lambda: check_rate_limit(customer_id))):
#       ...


# ──────────────────────────────────────────────
# EXERCISE 5 — WebSocket fraud alert stream
# ──────────────────────────────────────────────

CHANNEL_FRAUD_ALERTS = "fraud:alerts"


@app.websocket("/ws/fraud-alerts")
async def ws_fraud_alerts(websocket: WebSocket):
    """
    WebSocket endpoint that streams live fraud alerts.

    Connect with:
      wscat -c ws://localhost:8000/ws/fraud-alerts
      # or in browser: new WebSocket('ws://localhost:8000/ws/fraud-alerts')
    """
    await websocket.accept()
    ar = aioredis.from_url(REDIS_URL, decode_responses=True)
    pubsub = ar.pubsub(ignore_subscribe_messages=True)
    await pubsub.subscribe(CHANNEL_FRAUD_ALERTS)
    print(f"WebSocket client connected: {websocket.client}")

    try:
        async for message in pubsub.listen():
            if message is None or message["type"] != "message":
                continue
            await websocket.send_text(message["data"])
    except WebSocketDisconnect:
        print(f"WebSocket client disconnected: {websocket.client}")
    finally:
        await pubsub.unsubscribe(CHANNEL_FRAUD_ALERTS)
        await pubsub.close()
        await ar.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("module_05_redis_pubsub.exercises.05_solutions:app",
                host="0.0.0.0", port=8001, reload=True)
