# =============================================================================
# MODULE 6: CAPSTONE SOLUTIONS
# "First National Bank — Real-Time Banking Microservice"
# =============================================================================

from __future__ import annotations

import asyncio
import json
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, AsyncGenerator

import redis
import redis.asyncio as aioredis
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, Path, Query, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select, func, text
from sqlalchemy.orm import Session

from module_01_python_sqlalchemy.setup_and_models import (  # type: ignore
    SessionLocal, Customer, Account, Transaction, Branch, Loan, FraudAlert,
    TransactionTypeEnum, LoanStatusEnum, FraudStatusEnum
)

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# ─────────────────────────────────────────────
# INFRASTRUCTURE SETUP
# ─────────────────────────────────────────────

_async_redis: Optional[aioredis.Redis] = None
_sync_redis:  Optional[redis.Redis]    = None
_start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _async_redis, _sync_redis
    _async_redis = aioredis.from_url(REDIS_URL, decode_responses=True)
    _sync_redis  = redis.from_url(REDIS_URL, decode_responses=True)
    try:
        await _async_redis.ping()
    except Exception:
        pass
    yield
    await _async_redis.close()
    _sync_redis.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_sync_redis() -> redis.Redis:
    return _sync_redis


def get_async_redis() -> aioredis.Redis:
    return _async_redis


app = FastAPI(
    title    = "First National Bank — Capstone Solutions",
    version  = "1.0.0",
    lifespan = lifespan,
)


# ─────────────────────────────────────────────
# CAPSTONE 1: Real-Time Transaction API
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
    fraud_risk:       str   # "none" | "low" | "high"


CHANNEL_TRANSACTIONS_NEW  = "transactions:new"
CHANNEL_BALANCE_LOW       = "accounts:balance_low"
CHANNEL_FRAUD_ALERTS      = "fraud:alerts"
LOW_BALANCE_THRESHOLD     = 500.00
VELOCITY_LIMIT            = 3
VELOCITY_WINDOW           = 600   # 10 minutes


def _publish_tx_event(event: dict, balance_after: float, r_client: redis.Redis):
    r_client.publish(CHANNEL_TRANSACTIONS_NEW, json.dumps(event, default=str))
    if balance_after < LOW_BALANCE_THRESHOLD:
        low_alert = {
            "event":       "account.balance_low",
            "account_id":  event["account_id"],
            "customer_id": event["customer_id"],
            "new_balance": balance_after,
            "timestamp":   event["timestamp"],
        }
        r_client.publish(CHANNEL_BALANCE_LOW, json.dumps(low_alert, default=str))


def _velocity_check(account_id: int, tx_id: int, r_client: redis.Redis) -> int:
    key    = f"velocity:{account_id}"
    now    = time.time()
    cutoff = now - VELOCITY_WINDOW
    pipe   = r_client.pipeline()
    pipe.zadd(key, {str(tx_id): now})
    pipe.zremrangebyscore(key, "-inf", cutoff)
    pipe.zcard(key)
    pipe.expire(key, VELOCITY_WINDOW * 2)
    return pipe.execute()[2]


@app.post("/v2/accounts/{account_id}/transactions",
          response_model=TransactionResponse, status_code=201, tags=["Capstone 1"])
def capstone_post_transaction(
    account_id:       int                = Path(...),
    data:             TransactionRequest = ...,
    db:               Session            = Depends(get_db),
    background_tasks: BackgroundTasks    = ...,
):
    account = db.get(Account, account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
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

    event = {
        "event":            "transaction.posted",
        "transaction_id":   txn.transaction_id,
        "account_id":       account_id,
        "customer_id":      account.customer_id,
        "transaction_type": data.transaction_type,
        "amount":           float(amount),
        "balance_after":    float(account.balance),
        "description":      data.description,
        "timestamp":        datetime.utcnow().isoformat() + "Z",
    }

    r_client = get_sync_redis()
    background_tasks.add_task(_publish_tx_event, event, float(account.balance), r_client)
    velocity = _velocity_check(account_id, txn.transaction_id, r_client)
    fraud_risk = "high" if (float(amount) >= 10000 or velocity >= VELOCITY_LIMIT) else \
                 "low"  if float(amount) >= 1000 else "none"

    return TransactionResponse(
        transaction_id   = txn.transaction_id,
        account_id       = account_id,
        transaction_type = data.transaction_type,
        amount           = float(amount),
        balance_after    = float(account.balance),
        transaction_date = txn.transaction_date,
        fraud_risk       = fraud_risk,
    )


# ─────────────────────────────────────────────
# CAPSTONE 2: Fraud Detection Service (background process)
# ─────────────────────────────────────────────

def run_fraud_detection_service():
    """Subscribe to transactions:new and apply all four fraud rules."""
    r_client = redis.from_url(REDIS_URL, decode_responses=True)
    pubsub   = r_client.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe(CHANNEL_TRANSACTIONS_NEW)
    print("Fraud Detection Service running…  Ctrl+C to stop.")

    AFTER_HOURS_START = 22
    AFTER_HOURS_END   = 6

    try:
        for message in pubsub.listen():
            if message is None or message["type"] != "message":
                continue
            event      = json.loads(message["data"])
            account_id = event.get("account_id")
            amount     = float(event.get("amount", 0))
            tx_type    = event.get("transaction_type", "")
            customer_id = event.get("customer_id")
            ts          = event.get("timestamp", "")

            alerts = []

            # Rule A: Velocity
            velocity = _velocity_check(account_id, event["transaction_id"], r_client)
            if velocity >= VELOCITY_LIMIT:
                alerts.append(("Velocity Check", amount,
                                f"{velocity} transactions in {VELOCITY_WINDOW}s"))

            # Rule B: After-hours large withdrawal
            try:
                dt = datetime.fromisoformat(ts.replace("Z", ""))
                after_hours = dt.hour >= AFTER_HOURS_START or dt.hour < AFTER_HOURS_END
            except Exception:
                after_hours = False
            if tx_type in ("withdrawal", "atm_withdrawal") and after_hours and amount > 500:
                alerts.append(("After-Hours Withdrawal", amount,
                                f"${amount:.2f} at {ts}"))

            # Publish all alerts
            for alert_type, risk_amount, desc in alerts:
                severity = "HIGH" if risk_amount > 5000 else "MEDIUM"
                alert_payload = {
                    "event":          "fraud.detected",
                    "customer_id":    customer_id,
                    "account_id":     account_id,
                    "alert_type":     alert_type,
                    "amount_at_risk": risk_amount,
                    "severity":       severity,
                    "description":    desc,
                    "source_event":   event,
                    "detected_at":    datetime.utcnow().isoformat() + "Z",
                }
                r_client.publish(CHANNEL_FRAUD_ALERTS, json.dumps(alert_payload, default=str))
                print(f"🚨 [{severity}] {alert_type} — customer={customer_id}")

    except KeyboardInterrupt:
        print("Fraud Detection Service stopped.")
    finally:
        pubsub.close()
        r_client.close()


# ─────────────────────────────────────────────
# CAPSTONE 3: Customer 360 with Redis cache
# ─────────────────────────────────────────────

CACHE_TTL_360 = 300   # 5 minutes


@app.get("/v2/customers/{customer_id}/360", tags=["Capstone 3"])
async def capstone_customer_360(customer_id: int = Path(...)):
    cache_key = f"customer:{customer_id}:360"
    ar = get_async_redis()

    # Try cache first
    cached = await ar.get(cache_key)
    if cached:
        data = json.loads(cached)
        data["cached"] = True
        return data

    # Build from DB
    with SessionLocal() as db:
        customer = db.get(Customer, customer_id)
        if customer is None:
            raise HTTPException(status_code=404, detail="Customer not found")

        accounts = db.execute(
            select(Account).where(Account.customer_id == customer_id, Account.is_active == True)
        ).scalars().all()

        loans = db.execute(
            select(Loan).where(Loan.customer_id == customer_id,
                               Loan.status == LoanStatusEnum.active)
        ).scalars().all()

        fraud = db.execute(
            select(FraudAlert).where(FraudAlert.customer_id == customer_id,
                                     FraudAlert.status == FraudStatusEnum.open)
        ).scalars().all()

        total_balance = sum(float(a.balance) for a in accounts)
        wealth_tier = (
            "Platinum" if total_balance >= 100_000 else
            "Gold"     if total_balance >= 25_000  else
            "Silver"   if total_balance >= 5_000   else
            "Bronze"
        )

        result = {
            "customer_id":       customer.customer_id,
            "full_name":         f"{customer.first_name} {customer.last_name}",
            "email":             customer.email,
            "credit_score":      customer.credit_score,
            "wealth_tier":       wealth_tier,
            "total_balance":     total_balance,
            "accounts":          [
                {"account_id": a.account_id,
                 "account_type": a.account_type.value,
                 "balance": float(a.balance)}
                for a in accounts
            ],
            "active_loans":      [
                {"loan_id": lo.loan_id,
                 "loan_type": lo.loan_type,
                 "remaining_balance": float(lo.remaining_balance or 0)}
                for lo in loans
            ],
            "open_fraud_alerts": [
                {"alert_id": al.alert_id, "alert_type": al.alert_type}
                for al in fraud
            ],
            "cached": False,
        }

    # Cache for 5 minutes
    await ar.setex(cache_key, CACHE_TTL_360, json.dumps(result, default=str))
    return result


# ─────────────────────────────────────────────
# CAPSTONE 4: Branch Analytics with Redis Cache
# ─────────────────────────────────────────────

CACHE_KEY_BRANCHES = "analytics:branches"
CACHE_TTL_BRANCHES = 600  # 10 minutes


@app.get("/v2/analytics/branches", tags=["Capstone 4"])
async def capstone_branch_analytics(force_refresh: bool = Query(False)):
    ar = get_async_redis()

    if not force_refresh:
        cached = await ar.get(CACHE_KEY_BRANCHES)
        if cached:
            return {"cached": True, "data": json.loads(cached)}

    sql = text("""
        WITH branch_stats AS (
            SELECT  b.branch_id,
                    b.branch_name,
                    b.state,
                    COUNT(DISTINCT a.account_id)              AS active_accounts,
                    COUNT(DISTINCT c.customer_id)             AS active_customers,
                    COALESCE(SUM(a.balance), 0)               AS total_deposits,
                    COALESCE(AVG(c.credit_score), 0)          AS avg_credit_score,
                    COALESCE(SUM(lo.remaining_balance), 0)    AS total_loan_exposure
            FROM    branches    b
            LEFT JOIN accounts   a  ON a.branch_id   = b.branch_id  AND a.is_active = TRUE
            LEFT JOIN customers  c  ON c.customer_id = a.customer_id
            LEFT JOIN loans      lo ON lo.customer_id = c.customer_id AND lo.status = 'active'
            GROUP BY b.branch_id, b.branch_name, b.state
        )
        SELECT  *,
                RANK() OVER (PARTITION BY state ORDER BY total_deposits DESC) AS branch_rank
        FROM    branch_stats
        ORDER BY state, branch_rank
    """)
    with SessionLocal() as db:
        rows = db.execute(sql).all()

    data = [
        {
            "branch_name":          row.branch_name,
            "state":                row.state,
            "active_accounts":      row.active_accounts,
            "active_customers":     row.active_customers,
            "total_deposits":       float(row.total_deposits),
            "avg_credit_score":     float(row.avg_credit_score),
            "total_loan_exposure":  float(row.total_loan_exposure),
            "branch_rank":          row.branch_rank,
        }
        for row in rows
    ]
    await ar.setex(CACHE_KEY_BRANCHES, CACHE_TTL_BRANCHES, json.dumps(data))
    return {"cached": False, "data": data}


# ─────────────────────────────────────────────
# CAPSTONE 5: Live Fraud Feed (SSE)
# ─────────────────────────────────────────────

async def _fraud_sse_generator() -> AsyncGenerator[str, None]:
    ar = aioredis.from_url(REDIS_URL, decode_responses=True)
    pubsub = ar.pubsub(ignore_subscribe_messages=True)
    await pubsub.subscribe(CHANNEL_FRAUD_ALERTS)
    try:
        async for message in pubsub.listen():
            if message is None or message["type"] != "message":
                continue
            data      = json.loads(message["data"])
            event_id  = data.get("detected_at", "")
            yield f"id: {event_id}\ndata: {message['data']}\n\n"
    except asyncio.CancelledError:
        pass
    finally:
        await pubsub.unsubscribe(CHANNEL_FRAUD_ALERTS)
        await pubsub.close()
        await ar.close()


@app.get("/v2/stream/fraud", tags=["Capstone 5"],
         response_class=StreamingResponse,
         summary="Live fraud alert feed (SSE)")
async def capstone_fraud_stream():
    return StreamingResponse(
        _fraud_sse_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ─────────────────────────────────────────────
# CAPSTONE 6: Health Dashboard
# ─────────────────────────────────────────────

@app.get("/v2/health/dashboard", tags=["Capstone 6"])
async def capstone_health_dashboard():
    ar = get_async_redis()

    # Redis ping
    redis_ok = False
    ping_ms  = None
    active_channels: List[str] = []
    try:
        t0 = time.monotonic()
        await ar.ping()
        ping_ms = round((time.monotonic() - t0) * 1000, 2)
        redis_ok = True
        # Get channels with active subscribers
        pubsub_channels = await ar.execute_command("PUBSUB", "CHANNELS", "*")
        active_channels = pubsub_channels or []
    except Exception as exc:
        redis_error = str(exc)

    # Database stats
    db_ok      = False
    db_version = None
    pool_size  = None
    try:
        with SessionLocal() as db:
            from sqlalchemy import text as sqla_text
            db_version = db.execute(sqla_text("SELECT version()")).scalar()
            open_alerts     = db.execute(
                select(func.count()).select_from(FraudAlert)
                .where(FraudAlert.status == FraudStatusEnum.open)
            ).scalar()
            active_accounts = db.execute(
                select(func.count()).select_from(Account)
                .where(Account.is_active == True)
            ).scalar()
            total_customers = db.execute(
                select(func.count()).select_from(Customer)
                .where(Customer.is_active == True)
            ).scalar()
            delinquent_loans = db.execute(
                select(func.count()).select_from(Loan)
                .where(Loan.status == LoanStatusEnum.delinquent)
            ).scalar()
        db_ok = True
    except Exception as exc:
        db_version  = f"error: {exc}"
        open_alerts = active_accounts = total_customers = delinquent_loans = None

    return {
        "api": {
            "status":         "ok",
            "uptime_seconds": round(time.time() - _start_time, 1),
        },
        "database": {
            "status":    "ok" if db_ok else "error",
            "version":   db_version,
        },
        "redis": {
            "status":          "ok" if redis_ok else "error",
            "ping_ms":         ping_ms,
            "active_channels": active_channels,
        },
        "business": {
            "open_fraud_alerts": open_alerts,
            "active_accounts":   active_accounts,
            "total_customers":   total_customers,
            "delinquent_loans":  delinquent_loans,
        },
    }


@app.get("/", tags=["Meta"])
def root():
    return {
        "message": "First National Bank Capstone API",
        "docs":    "/docs",
        "endpoints": {
            "transaction":  "POST /v2/accounts/{id}/transactions",
            "customer_360": "GET  /v2/customers/{id}/360",
            "analytics":    "GET  /v2/analytics/branches",
            "fraud_stream": "GET  /v2/stream/fraud",
            "dashboard":    "GET  /v2/health/dashboard",
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "module_06_capstone.capstone_solutions:app",
        host="0.0.0.0", port=8000, reload=True,
    )
