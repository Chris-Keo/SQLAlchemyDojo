# =============================================================================
# MODULE 4: FASTAPI + SQLALCHEMY INTEGRATION
# Lesson 3 – Full Banking API with Filtering, Pagination, Error Handling
# =============================================================================
# Goal: Build a production-style banking REST API that integrates all
#       patterns from Modules 3 and 4: Depends(get_db), Pydantic schemas,
#       pagination, filtering, proper error responses.
#
# Run:
#   uvicorn module_04_fastapi_sqlalchemy.03_banking_api:app --reload --port 8000
# =============================================================================

from __future__ import annotations

import os
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Generator

from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy import create_engine, select, func, and_, text
from sqlalchemy.orm import sessionmaker, Session

from module_01_python_sqlalchemy.setup_and_models import (  # type: ignore
    Base, Customer, Account, Transaction, Branch, Employee, Loan, FraudAlert,
    AccountTypeEnum, TransactionTypeEnum, LoanStatusEnum, FraudStatusEnum
)
from module_04_fastapi_sqlalchemy.02_schemas_and_models import (  # type: ignore
    CustomerOut, CustomerCreate, CustomerUpdate,
    AccountOut, AccountCreate,
    TransactionOut, TransactionCreate,
    Page, ErrorResponse,
    customer_to_schema, account_to_schema, transaction_to_schema,
)

load_dotenv()

# ─────────────────────────────────────────────
# DATABASE SETUP
# ─────────────────────────────────────────────

DATABASE_URL = os.getenv("DATABASE_URL", "******localhost:5432/firstnational_db")

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=5)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ─────────────────────────────────────────────
# APP + EXCEPTION HANDLERS
# ─────────────────────────────────────────────

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🏦 Banking API starting…")
    yield
    print("🏦 Banking API shutting down…")


app = FastAPI(
    title       = "First National Bank — Full Banking API",
    description = "Production-style REST API for First National Bank.",
    version     = "2.0.0",
    lifespan    = lifespan,
)


# ─────────────────────────────────────────────
# CUSTOMERS ROUTER
# ─────────────────────────────────────────────

customers_router = APIRouter(prefix="/customers", tags=["Customers"])


@customers_router.get("", response_model=Page[CustomerOut])
def list_customers(
    db:          Session        = Depends(get_db),
    state:       Optional[str]  = Query(None, description="2-letter state code"),
    active_only: bool           = Query(True),
    min_score:   Optional[int]  = Query(None, ge=300, le=850),
    max_score:   Optional[int]  = Query(None, ge=300, le=850),
    page:        int            = Query(1, ge=1),
    page_size:   int            = Query(20, ge=1, le=100),
):
    """List customers with optional filtering and cursor-based pagination."""
    filters = []
    if active_only:
        filters.append(Customer.is_active == True)
    if state:
        filters.append(Customer.state == state.upper())
    if min_score is not None:
        filters.append(Customer.credit_score >= min_score)
    if max_score is not None:
        filters.append(Customer.credit_score <= max_score)

    total = db.execute(
        select(func.count()).select_from(Customer).where(*filters)
    ).scalar()

    items = db.execute(
        select(Customer)
        .where(*filters)
        .order_by(Customer.last_name, Customer.first_name)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).scalars().all()

    return Page[CustomerOut](
        total     = total,
        page      = page,
        page_size = page_size,
        items     = [customer_to_schema(c) for c in items],
    )


@customers_router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: int = Path(...), db: Session = Depends(get_db)):
    customer = db.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")
    return customer_to_schema(customer)


@customers_router.post("", response_model=CustomerOut, status_code=201)
def create_customer(data: CustomerCreate, db: Session = Depends(get_db)):
    """Create a new customer. Returns 409 if email already exists."""
    if db.execute(select(Customer).where(Customer.email == data.email)).scalars().first():
        raise HTTPException(status_code=409, detail=f"Email {data.email!r} already registered")

    customer = Customer(**data.model_dump(), joined_date=date.today(), is_active=True)
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer_to_schema(customer)


@customers_router.patch("/{customer_id}", response_model=CustomerOut)
def update_customer(
    customer_id: int = Path(...),
    data:        CustomerUpdate = ...,
    db:          Session        = Depends(get_db),
):
    customer = db.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)
    db.commit()
    db.refresh(customer)
    return customer_to_schema(customer)


@customers_router.delete("/{customer_id}", status_code=204)
def deactivate_customer(customer_id: int = Path(...), db: Session = Depends(get_db)):
    customer = db.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")
    customer.is_active = False
    db.commit()


# ─────────────────────────────────────────────
# ACCOUNTS ROUTER
# ─────────────────────────────────────────────

accounts_router = APIRouter(prefix="/accounts", tags=["Accounts"])


@accounts_router.get("", response_model=Page[AccountOut])
def list_accounts(
    db:           Session                 = Depends(get_db),
    customer_id:  Optional[int]            = Query(None),
    branch_id:    Optional[int]            = Query(None),
    account_type: Optional[AccountTypeEnum] = Query(None),
    min_balance:  Optional[float]          = Query(None),
    max_balance:  Optional[float]          = Query(None),
    active_only:  bool                     = Query(True),
    page:         int                      = Query(1, ge=1),
    page_size:    int                      = Query(20, ge=1, le=100),
):
    """List accounts with multi-field filtering."""
    filters = []
    if active_only:
        filters.append(Account.is_active == True)
    if customer_id:
        filters.append(Account.customer_id == customer_id)
    if branch_id:
        filters.append(Account.branch_id == branch_id)
    if account_type:
        filters.append(Account.account_type == account_type)
    if min_balance is not None:
        filters.append(Account.balance >= min_balance)
    if max_balance is not None:
        filters.append(Account.balance <= max_balance)

    total = db.execute(
        select(func.count()).select_from(Account).where(*filters)
    ).scalar()

    items = db.execute(
        select(Account)
        .where(*filters)
        .order_by(Account.balance.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).scalars().all()

    return Page[AccountOut](
        total     = total,
        page      = page,
        page_size = page_size,
        items     = [account_to_schema(a) for a in items],
    )


@accounts_router.get("/{account_id}", response_model=AccountOut)
def get_account(account_id: int = Path(...), db: Session = Depends(get_db)):
    account = db.get(Account, account_id)
    if account is None:
        raise HTTPException(status_code=404, detail=f"Account {account_id} not found")
    return account_to_schema(account)


@accounts_router.post("", response_model=AccountOut, status_code=201)
def create_account(data: AccountCreate, db: Session = Depends(get_db)):
    if db.get(Customer, data.customer_id) is None:
        raise HTTPException(status_code=404, detail=f"Customer {data.customer_id} not found")
    if db.execute(select(Account).where(Account.account_number == data.account_number)).scalars().first():
        raise HTTPException(status_code=409, detail=f"Account number already exists")

    account = Account(
        customer_id    = data.customer_id,
        branch_id      = data.branch_id,
        account_number = data.account_number,
        account_type   = AccountTypeEnum(data.account_type),
        balance        = Decimal(str(data.opening_deposit)),
        opened_date    = date.today(),
        is_active      = True,
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account_to_schema(account)


# ─────────────────────────────────────────────
# TRANSACTIONS ROUTER
# ─────────────────────────────────────────────

transactions_router = APIRouter(
    prefix="/accounts/{account_id}/transactions",
    tags=["Transactions"],
)


@transactions_router.get("", response_model=Page[TransactionOut])
def list_transactions(
    account_id: int            = Path(...),
    db:         Session        = Depends(get_db),
    tx_type:    Optional[str]  = Query(None, alias="type"),
    page:       int            = Query(1, ge=1),
    page_size:  int            = Query(50, ge=1, le=500),
):
    if db.get(Account, account_id) is None:
        raise HTTPException(status_code=404, detail=f"Account {account_id} not found")

    filters = [Transaction.account_id == account_id]
    if tx_type:
        filters.append(Transaction.transaction_type == TransactionTypeEnum(tx_type))

    total = db.execute(
        select(func.count()).select_from(Transaction).where(*filters)
    ).scalar()

    items = db.execute(
        select(Transaction)
        .where(*filters)
        .order_by(Transaction.transaction_date.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).scalars().all()

    return Page[TransactionOut](
        total     = total,
        page      = page,
        page_size = page_size,
        items     = [transaction_to_schema(t) for t in items],
    )


@transactions_router.post("", response_model=TransactionOut, status_code=201)
def post_transaction(
    account_id: int                = Path(...),
    data:       TransactionCreate  = ...,
    db:         Session            = Depends(get_db),
):
    """Post a transaction and update the account balance atomically."""
    account = db.get(Account, account_id)
    if account is None:
        raise HTTPException(status_code=404, detail=f"Account {account_id} not found")
    if not account.is_active:
        raise HTTPException(status_code=400, detail="Account is inactive")

    DEBIT_TYPES = {
        "withdrawal", "transfer_out", "fee", "atm_withdrawal"
    }
    amount = Decimal(str(data.amount))
    if data.transaction_type in DEBIT_TYPES:
        if account.balance < amount:
            raise HTTPException(status_code=422, detail="Insufficient funds")
        account.balance -= amount
    else:
        account.balance += amount

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
    return transaction_to_schema(txn)


# ─────────────────────────────────────────────
# ANALYTICS ROUTER
# ─────────────────────────────────────────────

analytics_router = APIRouter(prefix="/analytics", tags=["Analytics"])


@analytics_router.get("/branch-performance")
def branch_performance(db: Session = Depends(get_db)):
    """Branch-level performance report using SQLAlchemy aggregations."""
    sql = text("""
        SELECT  b.branch_name,
                b.state,
                COUNT(DISTINCT a.account_id)     AS active_accounts,
                COUNT(DISTINCT c.customer_id)    AS active_customers,
                SUM(a.balance)                   AS total_deposits,
                AVG(c.credit_score)              AS avg_credit_score,
                COUNT(DISTINCT lo.loan_id)       AS active_loans,
                COALESCE(SUM(lo.remaining_balance), 0) AS total_loan_exposure
        FROM    branches    b
        LEFT JOIN accounts   a  ON a.branch_id    = b.branch_id  AND a.is_active = TRUE
        LEFT JOIN customers  c  ON c.customer_id  = a.customer_id
        LEFT JOIN loans      lo ON lo.customer_id = c.customer_id AND lo.status = 'active'
        GROUP BY b.branch_id, b.branch_name, b.state
        ORDER BY total_deposits DESC NULLS LAST
    """)
    rows = db.execute(sql).all()
    return [
        {
            "branch_name":       row.branch_name,
            "state":             row.state,
            "active_accounts":   row.active_accounts,
            "active_customers":  row.active_customers,
            "total_deposits":    float(row.total_deposits or 0),
            "avg_credit_score":  float(row.avg_credit_score or 0),
            "active_loans":      row.active_loans,
            "total_loan_exposure": float(row.total_loan_exposure or 0),
        }
        for row in rows
    ]


@analytics_router.get("/fraud-alerts")
def open_fraud_alerts(
    db:     Session        = Depends(get_db),
    status: Optional[str]  = Query("open", description="Filter by alert status"),
):
    """List open fraud alerts with customer info."""
    stmt = (
        select(
            FraudAlert.alert_id,
            FraudAlert.alert_date,
            FraudAlert.alert_type,
            FraudAlert.description,
            FraudAlert.status,
            FraudAlert.amount_at_risk,
            Customer.first_name,
            Customer.last_name,
            Customer.email,
        )
        .join(Customer, Customer.customer_id == FraudAlert.customer_id)
        .where(FraudAlert.status == FraudStatusEnum(status))
        .order_by(FraudAlert.alert_date.desc())
    )
    rows = db.execute(stmt).all()
    return [
        {
            "alert_id":     row.alert_id,
            "customer":     f"{row.first_name} {row.last_name}",
            "email":        row.email,
            "alert_date":   row.alert_date,
            "alert_type":   row.alert_type,
            "description":  row.description,
            "status":       row.status.value,
            "amount_at_risk": float(row.amount_at_risk) if row.amount_at_risk else None,
        }
        for row in rows
    ]


# ─────────────────────────────────────────────
# ASSEMBLE THE APP
# ─────────────────────────────────────────────

app.include_router(customers_router)
app.include_router(accounts_router)
app.include_router(transactions_router)
app.include_router(analytics_router)


@app.get("/", tags=["Meta"])
def root():
    return {
        "message": "First National Bank API v2",
        "docs":    "/docs",
        "endpoints": {
            "customers":   "/customers",
            "accounts":    "/accounts",
            "analytics":   "/analytics/branch-performance",
            "fraud":       "/analytics/fraud-alerts",
        },
    }


@app.get("/health", tags=["Meta"])
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Database unreachable: {exc}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "module_04_fastapi_sqlalchemy.03_banking_api:app",
        host="0.0.0.0", port=8000, reload=True,
    )
