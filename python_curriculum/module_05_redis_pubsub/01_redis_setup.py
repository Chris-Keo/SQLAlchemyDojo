# =============================================================================
# MODULE 5: REDIS PUB/SUB
# Lesson 1 – Redis Connection, Basic Publish & Subscribe
# =============================================================================
# Goal: Learn to connect to Redis, publish messages on channels, and
#       subscribe to channels to receive real-time events.
#
# Prerequisites:
#   pip install redis
#   Start Redis: redis-server  (or: docker run -p 6379:6379 redis:7)
# =============================================================================

import os
import json
import time
import threading
from datetime import datetime
from typing import Optional

import redis
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# 5.1  CONNECTING TO REDIS
# ─────────────────────────────────────────────
# redis.Redis() creates a synchronous client.
# decode_responses=True → Redis returns str instead of bytes.

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

r = redis.from_url(REDIS_URL, decode_responses=True)

# Test the connection
def ping_redis() -> bool:
    """Returns True if Redis is reachable."""
    try:
        result = r.ping()
        print(f"Redis ping: {'PONG' if result else 'FAILED'}")
        return result
    except redis.ConnectionError as exc:
        print(f"Redis connection failed: {exc}")
        return False


# ─────────────────────────────────────────────
# 5.2  CHANNEL NAMING CONVENTION
# ─────────────────────────────────────────────
# Use colon-separated namespaces for clarity:
#   transactions:new          — every new transaction posted
#   transactions:large        — transactions over $10,000
#   fraud:alerts              — newly flagged fraud events
#   fraud:alerts:confirmed    — fraud events confirmed by analysts
#   accounts:{account_id}     — events scoped to a specific account

CHANNEL_TRANSACTIONS_NEW   = "transactions:new"
CHANNEL_TRANSACTIONS_LARGE = "transactions:large"
CHANNEL_FRAUD_ALERTS       = "fraud:alerts"
CHANNEL_FRAUD_CONFIRMED    = "fraud:alerts:confirmed"


# ─────────────────────────────────────────────
# 5.3  PUBLISHING — r.publish(channel, message)
# ─────────────────────────────────────────────
# publish() sends a message to all current subscribers of the channel.
# Returns the number of subscribers that received the message.
# Messages that are sent when no one is subscribed are LOST — there is
# no persistence in basic Pub/Sub.

def publish_event(channel: str, payload: dict) -> int:
    """Publish a JSON event to a Redis channel."""
    message = json.dumps(payload, default=str)  # default=str handles datetime
    subscriber_count = r.publish(channel, message)
    print(f"Published to {channel!r} → {subscriber_count} subscriber(s) received it")
    return subscriber_count


# ─────────────────────────────────────────────
# 5.4  DEMO EVENTS — simulate banking activity
# ─────────────────────────────────────────────

def simulate_deposit(account_id: int, amount: float, description: str = ""):
    payload = {
        "event":           "transaction.posted",
        "transaction_type": "deposit",
        "account_id":      account_id,
        "amount":          amount,
        "description":     description,
        "timestamp":       datetime.utcnow().isoformat(),
    }
    publish_event(CHANNEL_TRANSACTIONS_NEW, payload)

    if amount >= 10_000:
        publish_event(CHANNEL_TRANSACTIONS_LARGE, {**payload, "flag": "large_deposit"})


def simulate_fraud_alert(customer_id: int, alert_type: str, amount_at_risk: float):
    payload = {
        "event":          "fraud.detected",
        "customer_id":    customer_id,
        "alert_type":     alert_type,
        "amount_at_risk": amount_at_risk,
        "severity":       "HIGH" if amount_at_risk > 5000 else "MEDIUM",
        "timestamp":      datetime.utcnow().isoformat(),
    }
    publish_event(CHANNEL_FRAUD_ALERTS, payload)


# ─────────────────────────────────────────────
# 5.5  SUBSCRIBING — r.pubsub() + subscribe() + listen()
# ─────────────────────────────────────────────
# pubsub() returns a PubSub object that manages subscriptions.
# subscribe(channel) registers interest in a channel.
# listen() is a blocking iterator that yields messages as they arrive.
# Message types:
#   "subscribe"   — confirmation that subscription was registered
#   "message"     — an actual published message
#   "unsubscribe" — subscription removed

def subscribe_to_transactions(run_for_seconds: int = 30):
    """Listen to new transactions for a fixed number of seconds (demo only)."""
    pubsub = r.pubsub()
    pubsub.subscribe(CHANNEL_TRANSACTIONS_NEW)
    print(f"Subscribed to {CHANNEL_TRANSACTIONS_NEW!r}. Listening for {run_for_seconds}s…")

    deadline = time.time() + run_for_seconds
    for message in pubsub.listen():
        if time.time() > deadline:
            break
        if message["type"] != "message":
            continue  # skip subscription confirmation messages

        data = json.loads(message["data"])
        print(f"[TX] account={data['account_id']}  "
              f"type={data['transaction_type']}  "
              f"amount=${data['amount']:.2f}  "
              f"at={data['timestamp']}")

    pubsub.unsubscribe()
    pubsub.close()
    print("Unsubscribed and closed.")


# ─────────────────────────────────────────────
# 5.6  PATTERN SUBSCRIBE — subscribe to multiple channels with a glob
# ─────────────────────────────────────────────
# psubscribe("fraud:*") matches fraud:alerts AND fraud:alerts:confirmed

def subscribe_to_all_fraud(run_for_seconds: int = 30):
    """Listen to all fraud-related channels using a pattern."""
    pubsub = r.pubsub()
    pubsub.psubscribe("fraud:*")
    print("Pattern-subscribed to 'fraud:*'. Listening…")

    deadline = time.time() + run_for_seconds
    for message in pubsub.listen():
        if time.time() > deadline:
            break
        if message["type"] not in ("pmessage",):
            continue

        data = json.loads(message["data"])
        channel = message["channel"]
        print(f"[FRAUD:{channel}] customer={data['customer_id']}  "
              f"type={data['alert_type']}  "
              f"risk=${data['amount_at_risk']:.2f}  "
              f"severity={data['severity']}")

    pubsub.punsubscribe()
    pubsub.close()


# ─────────────────────────────────────────────
# 5.7  SUBSCRIBE IN A BACKGROUND THREAD
# ─────────────────────────────────────────────
# For use inside a larger application (e.g. alongside a FastAPI server),
# run the subscriber in a daemon thread so it doesn't block.

def start_fraud_listener_thread():
    """Start a background thread that continuously monitors fraud alerts."""
    def _listen():
        pubsub = r.pubsub()
        pubsub.subscribe(CHANNEL_FRAUD_ALERTS)
        print("[FraudListener] Started — monitoring fraud:alerts channel")
        for message in pubsub.listen():
            if message["type"] != "message":
                continue
            data = json.loads(message["data"])
            print(f"[FraudListener] 🚨 ALERT: customer={data['customer_id']}  "
                  f"type={data['alert_type']}  "
                  f"risk=${data['amount_at_risk']:.2f}")

    thread = threading.Thread(target=_listen, daemon=True)
    thread.start()
    print(f"[FraudListener] Background thread started (thread id={thread.ident})")
    return thread


# ─────────────────────────────────────────────
# 5.8  REDIS DATA TYPES USEFUL ALONGSIDE PUB/SUB
# ─────────────────────────────────────────────
# While Pub/Sub delivers real-time events, Redis also supports durable storage.
# Use these alongside Pub/Sub for state:

def cache_customer_profile(customer_id: int, profile: dict, ttl_seconds: int = 300):
    """Cache a customer profile dict as a JSON string with a 5-min TTL."""
    key = f"customer:{customer_id}:profile"
    r.setex(key, ttl_seconds, json.dumps(profile, default=str))
    print(f"Cached {key!r} for {ttl_seconds}s")


def get_cached_customer_profile(customer_id: int) -> Optional[dict]:
    """Return the cached profile, or None if not cached / expired."""
    key = f"customer:{customer_id}:profile"
    raw = r.get(key)
    return json.loads(raw) if raw else None


def increment_fraud_counter(customer_id: int) -> int:
    """Track how many fraud alerts a customer has (uses Redis INCR)."""
    key = f"customer:{customer_id}:fraud_count"
    count = r.incr(key)        # atomic increment; creates key at 0 if absent
    r.expire(key, 86400)       # reset counter after 24 hours
    return count


# ─────────────────────────────────────────────
# DEMO
# ─────────────────────────────────────────────

if __name__ == "__main__":
    if not ping_redis():
        print("Redis is not running. Start it with: redis-server")
        raise SystemExit(1)

    print("\n--- Caching a customer profile ---")
    profile = {"customer_id": 1, "name": "Alice Nguyen", "credit_score": 720}
    cache_customer_profile(1, profile)
    print("Retrieved:", get_cached_customer_profile(1))

    print("\n--- Publishing events ---")
    # NOTE: no subscriber is running, so subscriber_count will be 0
    simulate_deposit(account_id=3, amount=500.00, description="Paycheck")
    simulate_deposit(account_id=3, amount=25000.00, description="Wire transfer")  # triggers LARGE
    simulate_fraud_alert(customer_id=12, alert_type="Velocity Check", amount_at_risk=3500.00)

    print("\n--- Starting listener in background thread ---")
    thread = start_fraud_listener_thread()

    print("\n--- Publishing a fraud alert (will be caught by background listener) ---")
    time.sleep(0.1)  # give the thread a moment to subscribe
    simulate_fraud_alert(customer_id=5, alert_type="Geographic Anomaly", amount_at_risk=8200.00)
    time.sleep(0.5)  # let the listener print before we exit
    print("\nDone.")
