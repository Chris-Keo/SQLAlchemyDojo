# =============================================================================
# MODULE 5: REDIS PUB/SUB
# Lesson 2 – Transaction Event Publisher
# =============================================================================
# Goal: Build a publisher that fires structured events whenever a transaction
#       is posted to the banking system — mirroring what the FastAPI POST
#       /accounts/{id}/transactions endpoint would do in production.
#
# Run this alongside 03_fraud_subscriber.py to see events flowing live.
# =============================================================================

import json
import os
import time
from datetime import datetime
from decimal import Decimal
from typing import Optional

import redis
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# REDIS CLIENT
# ─────────────────────────────────────────────

r = redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    decode_responses=True,
)

# ─────────────────────────────────────────────
# 5.1  EVENT SCHEMA
# ─────────────────────────────────────────────
# Every event published on transactions:new follows this structure.
# Keeping a consistent schema makes subscribers easy to write.

TRANSACTION_EVENT_VERSION = "1.0"

def build_transaction_event(
    transaction_id:   int,
    account_id:       int,
    customer_id:      int,
    transaction_type: str,
    amount:           float,
    balance_after:    float,
    description:      Optional[str] = None,
) -> dict:
    """Build a well-structured transaction event payload."""
    return {
        "schema_version":   TRANSACTION_EVENT_VERSION,
        "event":            "transaction.posted",
        "transaction_id":   transaction_id,
        "account_id":       account_id,
        "customer_id":      customer_id,
        "transaction_type": transaction_type,
        "amount":           amount,
        "balance_after":    balance_after,
        "description":      description,
        "timestamp":        datetime.utcnow().isoformat() + "Z",
    }


# ─────────────────────────────────────────────
# 5.2  CHANNEL ROUTING LOGIC
# ─────────────────────────────────────────────
# The publisher decides which channels to post to based on business rules.

LARGE_AMOUNT_THRESHOLD = 10_000.00   # dollars
VELOCITY_WINDOW_SECONDS = 60         # check rapid succession within 1 minute

CHANNEL_ALL           = "transactions:new"
CHANNEL_LARGE         = "transactions:large"
CHANNEL_WITHDRAWALS   = "transactions:withdrawals"
CHANNEL_ACCOUNT_FMT   = "accounts:{account_id}:events"   # account-specific channel


def publish_transaction(event: dict) -> None:
    """Publish a transaction event to the appropriate Redis channels.

    Rules:
      • All transactions → transactions:new
      • Amount >= $10,000 → transactions:large  (for large-tx monitoring)
      • Withdrawals / ATM → transactions:withdrawals
      • Always → accounts:{account_id}:events   (per-account stream)
    """
    payload = json.dumps(event, default=str)

    # Every transaction goes to the main channel
    r.publish(CHANNEL_ALL, payload)

    # Per-account channel (subscribers can watch a specific account)
    account_channel = CHANNEL_ACCOUNT_FMT.format(account_id=event["account_id"])
    r.publish(account_channel, payload)

    # Large transaction channel
    if event["amount"] >= LARGE_AMOUNT_THRESHOLD:
        r.publish(CHANNEL_LARGE, payload)
        print(f"  ⚠️  Large transaction flagged on {CHANNEL_LARGE!r}")

    # Withdrawal channel
    if event["transaction_type"] in ("withdrawal", "atm_withdrawal", "transfer_out"):
        r.publish(CHANNEL_WITHDRAWALS, payload)

    print(f"  Published tx_id={event['transaction_id']}  "
          f"type={event['transaction_type']}  "
          f"amount=${event['amount']:.2f}")


# ─────────────────────────────────────────────
# 5.3  VELOCITY TRACKING WITH REDIS
# ─────────────────────────────────────────────
# Use a sorted set (ZSET) to track recent transactions per account.
# Score = Unix timestamp → allows expiring old entries with ZREMRANGEBYSCORE.

def record_and_check_velocity(account_id: int, transaction_id: int) -> int:
    """
    Add the transaction to a velocity tracker and return the count of
    transactions on this account within the last 60 seconds.
    Uses Redis ZSET with timestamps as scores.
    """
    key   = f"velocity:{account_id}"
    now   = time.time()
    cutoff = now - VELOCITY_WINDOW_SECONDS

    pipe = r.pipeline()
    pipe.zadd(key, {str(transaction_id): now})         # add current tx
    pipe.zremrangebyscore(key, "-inf", cutoff)          # remove old entries
    pipe.zcard(key)                                     # count remaining
    pipe.expire(key, VELOCITY_WINDOW_SECONDS * 2)       # TTL for cleanup
    results = pipe.execute()

    tx_count = results[2]
    if tx_count >= 3:
        print(f"  🚨 Velocity alert: {tx_count} transactions in 60s on account {account_id}")
    return tx_count


# ─────────────────────────────────────────────
# 5.4  INTEGRATION WITH DATABASE — hook into the FastAPI transaction route
# ─────────────────────────────────────────────
# In production, call publish_transaction() AFTER a successful db.commit().
# This ensures the event is only published if the DB write succeeded.
#
# Example (from module_04 03_banking_api.py post_transaction):
#
#   db.add(txn)
#   db.commit()
#   db.refresh(txn)
#
#   event = build_transaction_event(
#       transaction_id   = txn.transaction_id,
#       account_id       = txn.account_id,
#       customer_id      = account.customer_id,
#       transaction_type = txn.transaction_type.value,
#       amount           = float(txn.amount),
#       balance_after    = float(txn.balance_after),
#       description      = txn.description,
#   )
#   publish_transaction(event)
#   record_and_check_velocity(account_id, txn.transaction_id)


# ─────────────────────────────────────────────
# 5.5  BULK PUBLISHER — simulate a day's transactions
# ─────────────────────────────────────────────

import random

SAMPLE_TRANSACTIONS = [
    {"account_id": 1, "customer_id": 1, "type": "deposit",        "amount": 2500.00},
    {"account_id": 2, "customer_id": 1, "type": "withdrawal",     "amount": 200.00},
    {"account_id": 3, "customer_id": 2, "type": "transfer_out",   "amount": 15000.00},  # large
    {"account_id": 4, "customer_id": 3, "type": "atm_withdrawal", "amount": 300.00},
    {"account_id": 5, "customer_id": 4, "type": "deposit",        "amount": 50000.00},  # large
    {"account_id": 1, "customer_id": 1, "type": "withdrawal",     "amount": 100.00},
    {"account_id": 1, "customer_id": 1, "type": "fee",            "amount": 35.00},
    {"account_id": 1, "customer_id": 1, "type": "withdrawal",     "amount": 50.00},    # velocity!
]


def simulate_banking_day(delay_seconds: float = 0.5):
    """Publish a sequence of sample transactions with a short delay between each."""
    print("Simulating banking activity…\n")
    for i, tx_data in enumerate(SAMPLE_TRANSACTIONS, start=1000):
        balance = round(random.uniform(1000, 50000), 2)
        event = build_transaction_event(
            transaction_id   = i,
            account_id       = tx_data["account_id"],
            customer_id      = tx_data["customer_id"],
            transaction_type = tx_data["type"],
            amount           = tx_data["amount"],
            balance_after    = balance,
            description      = f"Simulated {tx_data['type']}",
        )
        publish_transaction(event)
        record_and_check_velocity(tx_data["account_id"], i)

        if delay_seconds > 0:
            time.sleep(delay_seconds)

    print("\nSimulation complete.")


# ─────────────────────────────────────────────
# DEMO
# ─────────────────────────────────────────────

if __name__ == "__main__":
    try:
        r.ping()
    except redis.ConnectionError:
        print("Redis is not running. Start it with: redis-server")
        raise SystemExit(1)

    print("Starting transaction publisher simulation…")
    print("Run 03_fraud_subscriber.py in another terminal to see events.\n")
    simulate_banking_day(delay_seconds=0.3)
