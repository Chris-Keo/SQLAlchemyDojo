# =============================================================================
# MODULE 5: EXERCISES
# =============================================================================

# ─────────────────────────────────────────────
# EXERCISE 1
# ─────────────────────────────────────────────
# Add a new Redis channel: "accounts:balance_low"
# Publish to it whenever a transaction causes an account balance to drop
# below $500.
# The event payload should include: account_id, customer_id, new_balance,
# transaction_id, timestamp.

# ─────────────────────────────────────────────
# EXERCISE 2
# ─────────────────────────────────────────────
# Write a subscriber that listens to "transactions:new" and:
#   1. Counts how many transactions each account has received today
#      using a Redis HASH with key "daily_tx_count:<YYYY-MM-DD>"
#      and field = account_id.
#   2. Prints a warning when any account exceeds 10 transactions in a day.

# ─────────────────────────────────────────────
# EXERCISE 3
# ─────────────────────────────────────────────
# Add a GET /accounts/{account_id}/recent-events endpoint to the FastAPI
# app in 04_fastapi_redis.py. It should:
#   - Subscribe to "accounts:{account_id}:events" for 5 seconds
#   - Collect up to 20 events
#   - Return them as a JSON list
# Hint: use async pubsub with asyncio.wait_for() to implement the timeout.

# ─────────────────────────────────────────────
# EXERCISE 4
# ─────────────────────────────────────────────
# Implement a Redis RATE LIMITER using a sorted set to enforce a rule:
# no more than 5 API requests per customer per minute.
#
# Write a FastAPI dependency: check_rate_limit(customer_id: int, r: Redis)
# that raises HTTPException(429) if the customer has made >= 5 requests
# in the last 60 seconds.

# ─────────────────────────────────────────────
# EXERCISE 5  (Stretch — async pub/sub)
# ─────────────────────────────────────────────
# Replace the SSE fraud alert stream (05.4) with a WebSocket endpoint.
# Use FastAPI's WebSocket support:
#   from fastapi import WebSocket
#   @app.websocket("/ws/fraud-alerts")
#   async def ws_fraud_alerts(websocket: WebSocket): ...
#
# The client connects and receives JSON fraud alert objects as they arrive.

# ─────────────────────────────────────────────
# IMPLEMENT YOUR SOLUTIONS BELOW
# ─────────────────────────────────────────────

import json
import os
import time
from datetime import date, datetime
from typing import Optional

import redis

r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True)


# Exercise 1 — YOUR CODE HERE


# Exercise 2 — YOUR CODE HERE


# Exercise 3 — Add to 04_fastapi_redis.py


# Exercise 4 — YOUR CODE HERE


# Exercise 5 — Add to 04_fastapi_redis.py
