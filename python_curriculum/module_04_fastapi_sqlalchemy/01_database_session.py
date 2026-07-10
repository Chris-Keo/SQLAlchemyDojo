# =============================================================================
# MODULE 4: FASTAPI + SQLALCHEMY INTEGRATION
# Lesson 1 – Database Session Management with Dependency Injection
# =============================================================================
# Goal: Use FastAPI's Depends() system to inject a per-request SQLAlchemy
#       session into route handlers — the production-standard pattern.
# =============================================================================

import os
from contextlib import contextmanager, asynccontextmanager
from typing import Generator

from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

load_dotenv()

# ─────────────────────────────────────────────
# 4.1  DATABASE ENGINE (singleton, created once at startup)
# ─────────────────────────────────────────────
# pool_size      — number of persistent connections in the pool
# max_overflow   — extra connections allowed beyond pool_size
# pool_pre_ping  — check connection health before using from pool
# echo           — set True to log all SQL (useful while learning)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "******localhost:5432/firstnational_db"
)

engine = create_engine(
    DATABASE_URL,
    pool_size      = 5,
    max_overflow   = 10,
    pool_pre_ping  = True,
    echo           = False,
)

# ─────────────────────────────────────────────
# 4.2  SESSION FACTORY
# ─────────────────────────────────────────────
# SessionLocal is a factory — call SessionLocal() to get a new session.
# autocommit=False → you must call session.commit() explicitly.
# autoflush=False  → SQLAlchemy won't push pending changes to DB
#                    automatically before a query.

SessionLocal = sessionmaker(
    autocommit = False,
    autoflush  = False,
    bind       = engine,
)


# ─────────────────────────────────────────────
# 4.3  DEPENDENCY: get_db()
# ─────────────────────────────────────────────
# This generator function is the standard FastAPI database dependency.
# FastAPI calls next() to enter the try block (yielding the session),
# runs the route handler, then calls next() again to execute the finally block.
#
# Usage in a route:
#   def my_route(db: Session = Depends(get_db)):
#       customers = db.query(Customer).all()

def get_db() -> Generator[Session, None, None]:
    """Yield a SQLAlchemy session; ensure it is closed after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ─────────────────────────────────────────────
# 4.4  DEMO: Using Depends(get_db) in a route
# ─────────────────────────────────────────────
# The session is injected by FastAPI — you never call get_db() directly.

from module_01_python_sqlalchemy.setup_and_models import Customer, Branch  # type: ignore
from sqlalchemy import select

app = FastAPI(title="Module 4 — DB Session Demo", version="1.0.0")


@app.get("/demo/customers/count")
def count_customers(db: Session = Depends(get_db)):
    """Demo: count rows using the injected session."""
    from sqlalchemy import func
    total = db.execute(select(func.count()).select_from(Customer)).scalar()
    return {"total_customers": total}


@app.get("/demo/db-health")
def db_health(db: Session = Depends(get_db)):
    """Verify DB connectivity inside a route using the injected session."""
    version = db.execute(text("SELECT version()")).scalar()
    return {"postgres_version": version}


# ─────────────────────────────────────────────
# 4.5  TRANSACTION MANAGEMENT
# ─────────────────────────────────────────────
# By default each request runs in its own transaction.
# Call db.commit()  to persist changes.
# Call db.rollback() to undo uncommitted changes (e.g. on error).
# The session is automatically rolled back if the route raises an exception
# (because get_db() calls db.close() which rolls back any open transaction).

@app.post("/demo/customers/{customer_id}/deactivate")
def deactivate_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.get(Customer, customer_id)
    if customer is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Customer not found")
    customer.is_active = False
    db.commit()          # persist change
    db.refresh(customer) # reload from DB to confirm
    return {"customer_id": customer_id, "is_active": customer.is_active}


# ─────────────────────────────────────────────
# 4.6  SCOPED SESSIONS VS REQUEST-SCOPED SESSIONS
# ─────────────────────────────────────────────
# The pattern above gives one session per HTTP request (request-scoped).
# This is the recommended approach for FastAPI because:
#   1. Each request is isolated — no accidental cross-request data sharing.
#   2. The session is always closed, preventing connection leaks.
#   3. Works correctly with async FastAPI routes (via run_in_threadpool).
#
# Avoid SQLAlchemy's scoped_session() in FastAPI; it relies on thread-local
# storage which does not integrate well with async handlers.


# ─────────────────────────────────────────────
# 4.7  TESTING OVERRIDE — swap the real DB for a test DB
# ─────────────────────────────────────────────
# In your test suite, override get_db to use an in-memory SQLite DB:
#
#   from fastapi.testclient import TestClient
#   from sqlalchemy import create_engine
#   from sqlalchemy.orm import sessionmaker
#
#   TEST_DB_URL = "sqlite:///:memory:"
#   test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
#   TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
#
#   def override_get_db():
#       db = TestSessionLocal()
#       try:
#           yield db
#       finally:
#           db.close()
#
#   app.dependency_overrides[get_db] = override_get_db
#   client = TestClient(app)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "module_04_fastapi_sqlalchemy.01_database_session:app",
        host="0.0.0.0", port=8000, reload=True,
    )
