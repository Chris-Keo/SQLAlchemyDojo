# 🏦 First National Bank — Python · FastAPI · Redis Pub/Sub Master's Curriculum

> A graduate-level, project-based Python curriculum that builds directly on top of
> the PostgreSQL banking schema from the SQL curriculum.
> Every concept is taught through a real banking scenario — no toy datasets.

---

## What You'll Learn

| Skill | Where |
|-------|-------|
| SQLAlchemy ORM models, sessions, engine setup | Module 1 |
| Basic CRUD with SQLAlchemy (SELECT, INSERT, UPDATE, DELETE) | Module 1 |
| Joins, aggregations, subqueries with SQLAlchemy ORM | Module 2 |
| Raw SQL via `text()`, window functions, CTEs with SQLAlchemy | Module 2 |
| FastAPI app structure, routing, Pydantic schemas | Module 3 |
| Dependency injection, request/response models, status codes | Module 3 |
| Full CRUD REST API with FastAPI + SQLAlchemy sessions | Module 4 |
| Pagination, filtering, error handling in FastAPI | Module 4 |
| Redis connection, channels, publish/subscribe pattern | Module 5 |
| Real-time transaction event pipeline with Redis Pub/Sub | Module 5 |
| FastAPI background tasks + Redis pub/sub integration | Module 5 |
| End-to-end banking microservice capstone | Module 6 |

---

## The Banking Schema (same as SQL curriculum)

```
branches ──< employees (self-join for manager hierarchy)
branches ──< accounts ──< transactions
customers ──< accounts
customers ──< credit_cards ──< credit_card_transactions
customers ──< loans ──< loan_payments
customers ──< fraud_alerts
```

---

## Prerequisites

- Python 3.11+
- PostgreSQL 14+ with `firstnational_db` loaded (run `curriculum/schema/01_create_tables.sql`
  and `02_seed_data.sql` from the SQL curriculum first)
- Redis 7+ running locally (`redis-server` or Docker: `docker run -p 6379:6379 redis:7`)

### Install Python dependencies

```bash
pip install sqlalchemy psycopg2-binary fastapi uvicorn[standard] redis pydantic python-dotenv
```

Or create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install sqlalchemy psycopg2-binary fastapi uvicorn[standard] redis pydantic python-dotenv
```

### Environment variables

Create a `.env` file in the `python_curriculum/` folder:

```
DATABASE_URL=postgresql://<user>:<password>@localhost:5432/firstnational_db
REDIS_URL=redis://localhost:6379/0
```

---

## Curriculum Roadmap

```
python_curriculum/
├── README.md
│
├── module_01_python_sqlalchemy/
│   ├── 01_setup_and_models.py     ← ORM models for banking schema
│   ├── 02_basic_queries.py        ← SELECT, INSERT, UPDATE, DELETE
│   └── exercises/
│       ├── 01_exercises.py        ← Attempt these first
│       └── 01_solutions.py
│
├── module_02_sqlalchemy_advanced/
│   ├── 01_joins_aggregations.py   ← Joins + GROUP BY in ORM
│   ├── 02_window_functions.py     ← Raw SQL / text() for analytics
│   └── exercises/
│       ├── 02_exercises.py
│       └── 02_solutions.py
│
├── module_03_fastapi_basics/
│   ├── 01_fastapi_setup.py        ← App structure, health endpoint
│   ├── 02_customer_routes.py      ← GET / POST customer routes
│   ├── 03_account_routes.py       ← Account + transaction routes
│   └── exercises/
│       ├── 03_exercises.py
│       └── 03_solutions.py
│
├── module_04_fastapi_sqlalchemy/
│   ├── 01_database_session.py     ← SQLAlchemy session + FastAPI DI
│   ├── 02_schemas_and_models.py   ← Pydantic schemas ↔ ORM models
│   ├── 03_banking_api.py          ← Full CRUD API with filtering
│   └── exercises/
│       ├── 04_exercises.py
│       └── 04_solutions.py
│
├── module_05_redis_pubsub/
│   ├── 01_redis_setup.py          ← Redis connection, basic pub/sub
│   ├── 02_transaction_publisher.py← Publish transaction events
│   ├── 03_fraud_subscriber.py     ← Subscribe to fraud alerts
│   ├── 04_fastapi_redis.py        ← FastAPI + Redis integration
│   └── exercises/
│       ├── 05_exercises.py
│       └── 05_solutions.py
│
└── module_06_capstone/
    ├── capstone_questions.py      ← Build the full app here
    └── capstone_solutions.py      ← Reference implementation
```

---

## Module-by-Module Guide

### Module 1 — Python + SQLAlchemy ORM
**Files:** `01_setup_and_models.py`, `02_basic_queries.py`

Define ORM models for all banking tables, connect to PostgreSQL, run basic CRUD operations.

**Key patterns:**
- `create_engine()` + `sessionmaker()` + `declarative_base()`
- ORM model classes for all 10 banking tables
- `session.query()` vs `select()` (modern style)
- Insert a new customer; update a balance; soft-delete an account

---

### Module 2 — SQLAlchemy Advanced Queries
**Files:** `01_joins_aggregations.py`, `02_window_functions.py`

Mirror the SQL curriculum (Modules 1–5) using SQLAlchemy ORM and `text()`.

**Key patterns:**
- Multi-table joins with `join()` / `outerjoin()`
- `func.count()`, `func.sum()`, `func.avg()` with `group_by()`
- Subqueries with `subquery()` and `scalar_subquery()`
- Window functions via `text()` for running totals, `RANK`, `LAG`

---

### Module 3 — FastAPI Basics
**Files:** `01_fastapi_setup.py`, `02_customer_routes.py`, `03_account_routes.py`

Build a REST API layer over the banking database with FastAPI.

**Key patterns:**
- `APIRouter`, path parameters, query parameters
- Pydantic `BaseModel` for request/response schemas
- HTTP status codes (`201 Created`, `404 Not Found`, `422 Unprocessable`)
- Auto-generated Swagger docs at `/docs`

---

### Module 4 — FastAPI + SQLAlchemy Integration
**Files:** `01_database_session.py`, `02_schemas_and_models.py`, `03_banking_api.py`

Wire FastAPI dependency injection with SQLAlchemy sessions for a production-style API.

**Key patterns:**
- `Depends(get_db)` for per-request database sessions
- Pydantic schema ↔ ORM model conversion
- Pagination (`skip` / `limit`), filtering by state/type
- Proper error handling with `HTTPException`

---

### Module 5 — Redis Pub/Sub ⭐
**Files:** `01_redis_setup.py`, `02_transaction_publisher.py`, `03_fraud_subscriber.py`, `04_fastapi_redis.py`

Add real-time event streaming to the banking API using Redis Pub/Sub.

**Key patterns:**
- `redis.Redis()` / `redis.asyncio.Redis()` connections
- `publish()` transaction events to a channel
- `pubsub()` + `subscribe()` + `listen()` for fraud detection
- FastAPI `BackgroundTasks` + async subscriber integration
- Channel naming strategy (`transactions:new`, `fraud:alerts`)

---

### Module 6 — Capstone Project
**Files:** `capstone_questions.py`, `capstone_solutions.py`

Build a complete banking microservice combining all layers:

1. **Real-time Transaction API** — POST /transactions publishes to Redis
2. **Fraud Detection Service** — subscribes to Redis, flags suspicious activity
3. **Customer 360 Endpoint** — aggregate view via SQLAlchemy
4. **Branch Analytics** — window functions via FastAPI endpoint
5. **Live Fraud Feed** — Server-Sent Events (SSE) streaming from Redis
6. **Health Dashboard** — Redis ping, DB connectivity, metrics

---

## Learning Order Recommendation

```
Beginner     → Module 1 → Module 2
Intermediate → Module 3 → Module 4
Advanced     → Module 5
Expert       → Module 6 (Capstone)
```

**Estimated study time:** 30–60 hours depending on prior Python experience.

---

## pgAdmin Tips for Python Developers

- Use pgAdmin's **Query Tool** to inspect data while running Python scripts
- Use the **ERD Tool** (Tools → ERD for Database) to visualize the banking schema
- Right-click any table → **Scripts → SELECT Script** to auto-generate queries
- Use **Debugger** to step through stored procedures called from SQLAlchemy
- Use **Dashboard** → **Server Activity** to watch live connections from your Python app

---

*Built for learning the Python backend stack from first principles to a production-style banking API.*
