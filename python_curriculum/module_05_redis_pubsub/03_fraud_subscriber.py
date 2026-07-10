# =============================================================================
# MODULE 5: REDIS PUB/SUB
# Lesson 3 – Fraud Detection Subscriber
# =============================================================================
# Goal: Build a consumer that listens to transaction events and applies
#       real-time fraud detection rules, publishing alerts to a separate
#       channel when suspicious activity is detected.
#
# Run in one terminal:  python 03_fraud_subscriber.py
# Run in another:       python 02_transaction_publisher.py
# =============================================================================

import json
import os
import time
from datetime import datetime, timedelta
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
# CHANNELS
# ─────────────────────────────────────────────

CHANNEL_TRANSACTIONS_NEW  = "transactions:new"
CHANNEL_TRANSACTIONS_LARGE = "transactions:large"
CHANNEL_FRAUD_ALERTS      = "fraud:alerts"
CHANNEL_FRAUD_CONFIRMED   = "fraud:alerts:confirmed"


# ─────────────────────────────────────────────
# 5.1  FRAUD RULES
# ─────────────────────────────────────────────

LARGE_TX_THRESHOLD      = 10_000.00   # flag deposits/withdrawals over $10k
VELOCITY_LIMIT          = 3           # max transactions within velocity window
VELOCITY_WINDOW_SECONDS = 60          # seconds to check for rapid succession
AFTER_HOURS_START       = 22          # 10 PM
AFTER_HOURS_END         = 6           # 6 AM


def is_after_hours(ts_iso: str) -> bool:
    """Return True if the timestamp falls outside normal business hours."""
    dt = datetime.fromisoformat(ts_iso.replace("Z", ""))
    hour = dt.hour
    return hour >= AFTER_HOURS_START or hour < AFTER_HOURS_END


def check_velocity(account_id: int) -> int:
    """Return the number of recent transactions for this account (last 60s)."""
    key    = f"velocity:{account_id}"
    window = r.zcount(key, time.time() - VELOCITY_WINDOW_SECONDS, "+inf")
    return window


# ─────────────────────────────────────────────
# 5.2  FRAUD ALERT PUBLISHER
# ─────────────────────────────────────────────

def publish_fraud_alert(
    customer_id:   int,
    account_id:    int,
    alert_type:    str,
    amount_at_risk: float,
    description:   str,
    source_event:  dict,
) -> None:
    payload = {
        "event":           "fraud.detected",
        "customer_id":     customer_id,
        "account_id":      account_id,
        "alert_type":      alert_type,
        "amount_at_risk":  amount_at_risk,
        "description":     description,
        "severity":        "HIGH" if amount_at_risk > 5000 else "MEDIUM",
        "source_event":    source_event,
        "detected_at":     datetime.utcnow().isoformat() + "Z",
    }
    r.publish(CHANNEL_FRAUD_ALERTS, json.dumps(payload, default=str))
    print(f"  🚨 FRAUD ALERT [{payload['severity']}] {alert_type} "
          f"— customer={customer_id}  risk=${amount_at_risk:.2f}")


# ─────────────────────────────────────────────
# 5.3  EVENT HANDLER
# ─────────────────────────────────────────────

def handle_transaction_event(event: dict) -> None:
    """Apply fraud detection rules to a single transaction event."""
    account_id       = event.get("account_id")
    customer_id      = event.get("customer_id")
    amount           = float(event.get("amount", 0))
    tx_type          = event.get("transaction_type", "")
    timestamp        = event.get("timestamp", "")
    tx_id            = event.get("transaction_id")

    print(f"\n[TX] id={tx_id}  account={account_id}  "
          f"type={tx_type}  amount=${amount:.2f}")

    # Rule 1: Large transaction
    if amount >= LARGE_TX_THRESHOLD:
        publish_fraud_alert(
            customer_id    = customer_id,
            account_id     = account_id,
            alert_type     = "Large Transaction",
            amount_at_risk = amount,
            description    = f"Transaction of ${amount:.2f} exceeds ${LARGE_TX_THRESHOLD:,.0f} threshold",
            source_event   = event,
        )

    # Rule 2: After-hours large withdrawal
    if tx_type in ("withdrawal", "atm_withdrawal") and is_after_hours(timestamp) and amount > 500:
        publish_fraud_alert(
            customer_id    = customer_id,
            account_id     = account_id,
            alert_type     = "After-Hours Withdrawal",
            amount_at_risk = amount,
            description    = f"${amount:.2f} {tx_type} at unusual hour",
            source_event   = event,
        )

    # Rule 3: Velocity check — rapid succession transactions
    velocity = check_velocity(account_id)
    if velocity >= VELOCITY_LIMIT:
        publish_fraud_alert(
            customer_id    = customer_id,
            account_id     = account_id,
            alert_type     = "Velocity Check",
            amount_at_risk = amount,
            description    = f"{velocity} transactions in {VELOCITY_WINDOW_SECONDS}s on account {account_id}",
            source_event   = event,
        )


# ─────────────────────────────────────────────
# 5.4  SUBSCRIBER LOOP
# ─────────────────────────────────────────────

def run_fraud_subscriber():
    """
    Continuously listen to transaction events and apply fraud rules.
    This is a blocking loop — run in a separate process or thread.
    """
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe(CHANNEL_TRANSACTIONS_NEW)

    print(f"🔍 Fraud Detection Service started")
    print(f"   Monitoring channel: {CHANNEL_TRANSACTIONS_NEW!r}")
    print(f"   Rules: Large(>${LARGE_TX_THRESHOLD:,.0f}), "
          f"After-Hours, Velocity(>{VELOCITY_LIMIT} in {VELOCITY_WINDOW_SECONDS}s)")
    print("   Press Ctrl+C to stop.\n")

    try:
        for message in pubsub.listen():
            if message is None or message["type"] != "message":
                continue
            try:
                event = json.loads(message["data"])
                handle_transaction_event(event)
            except json.JSONDecodeError as exc:
                print(f"[ERROR] Could not parse message: {exc}")
            except Exception as exc:
                print(f"[ERROR] Unexpected error handling event: {exc}")

    except KeyboardInterrupt:
        print("\nFraud Detection Service stopped.")
    finally:
        pubsub.unsubscribe()
        pubsub.close()


# ─────────────────────────────────────────────
# 5.5  FRAUD ALERT SUBSCRIBER — downstream consumer
# ─────────────────────────────────────────────
# A second subscriber listens on fraud:alerts and could:
#   • Write alerts to the database
#   • Send email/SMS notifications
#   • Update a real-time dashboard

def run_alert_logger():
    """Log all fraud alerts to stdout (simulates writing to DB or sending notifications)."""
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe(CHANNEL_FRAUD_ALERTS)
    print("📋 Alert Logger started — monitoring fraud:alerts")

    try:
        for message in pubsub.listen():
            if message is None or message["type"] != "message":
                continue
            alert = json.loads(message["data"])
            severity = alert.get("severity", "?")
            print(f"[ALERT_LOG] {severity:<6s}  "
                  f"type={alert['alert_type']:<25s}  "
                  f"customer={alert['customer_id']}  "
                  f"risk=${alert['amount_at_risk']:.2f}  "
                  f"at={alert['detected_at']}")
    except KeyboardInterrupt:
        print("\nAlert Logger stopped.")
    finally:
        pubsub.close()


# ─────────────────────────────────────────────
# DEMO
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    try:
        r.ping()
    except redis.ConnectionError:
        print("Redis is not running. Start it with: redis-server")
        sys.exit(1)

    # Running the fraud subscriber:
    #   python 03_fraud_subscriber.py
    # Then in another terminal, run:
    #   python 02_transaction_publisher.py
    run_fraud_subscriber()
