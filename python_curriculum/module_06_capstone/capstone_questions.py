# =============================================================================
# MODULE 6: CAPSTONE PROJECT
# "First National Bank — Real-Time Banking Microservice"
#
# Instructions:
#   Using all techniques from Modules 1–5, build the endpoints below.
#   Each challenge combines SQLAlchemy, FastAPI, and Redis Pub/Sub.
#   Attempt each before reading the solutions in capstone_solutions.py.
#
# Run:
#   uvicorn module_06_capstone.capstone_questions:app --reload --port 8000
# =============================================================================

from __future__ import annotations

import os
from typing import Optional, List

from fastapi import FastAPI, Depends, Path, Query, BackgroundTasks
from sqlalchemy.orm import Session

# Import your module-level dependencies
# from module_04_fastapi_sqlalchemy.01_database_session import get_db
# from module_05_redis_pubsub.04_fastapi_redis import get_sync_redis, get_async_redis

app = FastAPI(
    title   = "First National Bank — Capstone API",
    version = "1.0.0",
)


# ─────────────────────────────────────────────
# CAPSTONE 1: Real-Time Transaction API
# ─────────────────────────────────────────────
# Build a POST /v2/accounts/{account_id}/transactions endpoint that:
#   1. Validates and persists the transaction using SQLAlchemy
#   2. Updates the account balance atomically
#   3. Publishes a transaction event to Redis "transactions:new" channel
#   4. Triggers a low-balance alert if the balance drops below $500
#   5. Runs velocity check as a background task
#   6. Returns the created transaction details
#
# Bonus: Return a "fraud_risk" field in the response indicating whether
#        the transaction triggered any fraud rules.

@app.post("/v2/accounts/{account_id}/transactions", tags=["Capstone 1"])
def capstone_post_transaction(account_id: int):
    # YOUR CODE HERE
    raise NotImplementedError


# ─────────────────────────────────────────────
# CAPSTONE 2: Fraud Detection Service
# ─────────────────────────────────────────────
# Write a standalone fraud detection service (a function, not a route)
# that:
#   1. Subscribes to "transactions:new"
#   2. Applies ALL four fraud rules from Module 8 SQL:
#       a. Velocity: 3+ transactions in 10 minutes on the same account
#       b. After-hours: large withdrawal (>$500) between 10pm–6am
#       c. Duplicate charge: same merchant, same amount, same card, within 5 min
#       d. Geographic anomaly: domestic + international same-day
#          (hint: check the credit_card_transactions table via SQLAlchemy)
#   3. Publishes fraud alerts to "fraud:alerts" for any triggered rule
#   4. Writes confirmed alerts to the fraud_alerts table in PostgreSQL
#
# Call this: run_fraud_detection_service()

def run_fraud_detection_service():
    # YOUR CODE HERE
    raise NotImplementedError


# ─────────────────────────────────────────────
# CAPSTONE 3: Customer 360 Endpoint
# ─────────────────────────────────────────────
# Build GET /v2/customers/{customer_id}/360 that returns:
#   {
#     "customer_id": ...,
#     "full_name":   ...,
#     "email":       ...,
#     "credit_score": ...,
#     "wealth_tier": "Platinum" | "Gold" | "Silver" | "Bronze",
#     "total_balance": ...,
#     "accounts": [...],
#     "active_loans": [...],
#     "open_fraud_alerts": [...],
#     "rfm_segment": "Champion" | "Loyal" | "At Risk" | "Needs Attention",
#     "cached": true | false    ← true if served from Redis cache
#   }
#
# Cache the response in Redis for 5 minutes with key "customer:{id}:360"
# On the second request for the same customer, serve from cache.

@app.get("/v2/customers/{customer_id}/360", tags=["Capstone 3"])
async def capstone_customer_360(customer_id: int):
    # YOUR CODE HERE
    raise NotImplementedError


# ─────────────────────────────────────────────
# CAPSTONE 4: Branch Analytics Endpoint
# ─────────────────────────────────────────────
# Build GET /v2/analytics/branches that returns, for each branch:
#   branch_name, state, active_accounts, active_customers,
#   total_deposits, total_loan_exposure, avg_credit_score,
#   branch_rank (ranked by total_deposits within each state)
#
# Use a CTE or window function via SQLAlchemy text().
# Cache the result in Redis for 10 minutes (key: "analytics:branches").
# Accept ?force_refresh=true to bypass the cache.

@app.get("/v2/analytics/branches", tags=["Capstone 4"])
async def capstone_branch_analytics(force_refresh: bool = Query(False)):
    # YOUR CODE HERE
    raise NotImplementedError


# ─────────────────────────────────────────────
# CAPSTONE 5: Live Fraud Feed (SSE or WebSocket)
# ─────────────────────────────────────────────
# Build a streaming endpoint that delivers live fraud alerts:
#   Option A: GET /v2/stream/fraud  → Server-Sent Events
#   Option B: WebSocket /v2/ws/fraud
#
# Requirements:
#   1. Connect to Redis and subscribe to "fraud:alerts"
#   2. Stream each alert as it arrives
#   3. Handle client disconnect cleanly (unsubscribe + close)
#   4. Include an "id:" field in SSE events (use detected_at as the ID)

@app.get("/v2/stream/fraud", tags=["Capstone 5"])
async def capstone_fraud_stream():
    # YOUR CODE HERE
    raise NotImplementedError


# ─────────────────────────────────────────────
# CAPSTONE 6: Health Dashboard
# ─────────────────────────────────────────────
# Build GET /v2/health/dashboard that returns:
#   {
#     "api":      { "status": "ok", "uptime_seconds": ... },
#     "database": { "status": "ok" | "error", "version": ..., "pool_size": ... },
#     "redis":    {
#       "status": "ok" | "error",
#       "ping_ms": ...,          ← round-trip time in milliseconds
#       "active_channels": [...] ← list of channels with at least 1 subscriber
#     },
#     "business": {
#       "open_fraud_alerts": ...,
#       "active_accounts": ...,
#       "total_customers": ...,
#       "delinquent_loans": ...
#     }
#   }

@app.get("/v2/health/dashboard", tags=["Capstone 6"])
async def capstone_health_dashboard():
    # YOUR CODE HERE
    raise NotImplementedError


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "module_06_capstone.capstone_questions:app",
        host="0.0.0.0", port=8000, reload=True,
    )
