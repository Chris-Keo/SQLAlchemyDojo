# =============================================================================
# MODULE 3: FASTAPI BASICS
# Lesson 3 – Account & Transaction Routes
# =============================================================================
# Goal: Add routes for accounts and transactions, demonstrating nested
#       resources, request body validation, and response filtering.
#
# Run:
#   uvicorn module_03_fastapi_basics.03_account_routes:app --reload --port 8000
# =============================================================================

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List

from fastapi import FastAPI, APIRouter, HTTPException, status, Query, Path
from pydantic import BaseModel, field_validator

from sqlalchemy import select, func, and_

from module_01_python_sqlalchemy.setup_and_models import (  # type: ignore
    SessionLocal, Account, Transaction, Customer,
    AccountTypeEnum, TransactionTypeEnum
)


# ─────────────────────────────────────────────
# SCHEMAS
# ─────────────────────────────────────────────

class AccountOut(BaseModel):
    account_id:     int
    customer_id:    int
    branch_id:      int
    account_number: str
    account_type:   str
    balance:        float
    opened_date:    date
    is_active:      bool

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_model(cls, a: Account) -> "AccountOut":
        return cls(
            account_id     = a.account_id,
            customer_id    = a.customer_id,
            branch_id      = a.branch_id,
            account_number = a.account_number,
            account_type   = a.account_type.value,
            balance        = float(a.balance),
            opened_date    = a.opened_date,
            is_active      = a.is_active,
        )


class AccountCreate(BaseModel):
    customer_id:    int
    branch_id:      int
    account_number: str
    account_type:   AccountTypeEnum
    opening_deposit: float = 0.0

    @field_validator("opening_deposit")
    @classmethod
    def deposit_must_be_non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("opening_deposit must be >= 0")
        return v


class TransactionOut(BaseModel):
    transaction_id:   int
    account_id:       int
    transaction_type: str
    amount:           float
    transaction_date: datetime
    description:      Optional[str]
    balance_after:    Optional[float]


class TransactionCreate(BaseModel):
    transaction_type: TransactionTypeEnum
    amount:           float
    description:      Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Transaction amount must be positive")
        return v


class AccountSummary(BaseModel):
    account_id:      int
    account_number:  str
    account_type:    str
    balance:         float
    transaction_count: int
    total_deposits:  float
    total_withdrawals: float


# ─────────────────────────────────────────────
# ACCOUNT ROUTER
# ─────────────────────────────────────────────

accounts_router = APIRouter(prefix="/accounts", tags=["Accounts"])


@accounts_router.get("", response_model=List[AccountOut])
def list_accounts(
    customer_id:  Optional[int]            = Query(None, description="Filter by customer"),
    account_type: Optional[AccountTypeEnum] = Query(None, description="Filter by type"),
    active_only:  bool                     = Query(True),
    limit:        int                      = Query(50, ge=1, le=200),
):
    """List accounts with optional customer / type filter."""
    with SessionLocal() as session:
        stmt = select(Account)
        if customer_id:
            stmt = stmt.where(Account.customer_id == customer_id)
        if account_type:
            stmt = stmt.where(Account.account_type == account_type)
        if active_only:
            stmt = stmt.where(Account.is_active == True)
        stmt = stmt.order_by(Account.balance.desc()).limit(limit)

        accounts = session.execute(stmt).scalars().all()
        return [AccountOut.from_orm_model(a) for a in accounts]


@accounts_router.get("/{account_id}", response_model=AccountOut)
def get_account(account_id: int = Path(..., description="Account primary key")):
    """Get a single account by ID."""
    with SessionLocal() as session:
        account = session.get(Account, account_id)
        if account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Account {account_id} not found",
            )
        return AccountOut.from_orm_model(account)


@accounts_router.post("", response_model=AccountOut, status_code=status.HTTP_201_CREATED)
def open_account(data: AccountCreate):
    """Open a new bank account for an existing customer."""
    with SessionLocal() as session:
        # Verify customer exists
        customer = session.get(Customer, data.customer_id)
        if customer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer {data.customer_id} not found",
            )
        # Check account number uniqueness
        existing = session.execute(
            select(Account).where(Account.account_number == data.account_number)
        ).scalars().first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Account number {data.account_number!r} already exists",
            )
        account = Account(
            customer_id    = data.customer_id,
            branch_id      = data.branch_id,
            account_number = data.account_number,
            account_type   = data.account_type,
            balance        = Decimal(str(data.opening_deposit)),
            opened_date    = date.today(),
            is_active      = True,
        )
        session.add(account)
        session.commit()
        session.refresh(account)
        return AccountOut.from_orm_model(account)


@accounts_router.get("/{account_id}/summary", response_model=AccountSummary)
def account_summary(account_id: int):
    """Return aggregated stats for a single account."""
    with SessionLocal() as session:
        account = session.get(Account, account_id)
        if account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Account {account_id} not found",
            )
        # Aggregate in one query
        stats = session.execute(
            select(
                func.count(Transaction.transaction_id).label("tx_count"),
                func.coalesce(
                    func.sum(Transaction.amount).filter(
                        Transaction.transaction_type == TransactionTypeEnum.deposit
                    ), 0
                ).label("deposits"),
                func.coalesce(
                    func.sum(Transaction.amount).filter(
                        Transaction.transaction_type.in_([
                            TransactionTypeEnum.withdrawal,
                            TransactionTypeEnum.atm_withdrawal,
                        ])
                    ), 0
                ).label("withdrawals"),
            )
            .where(Transaction.account_id == account_id)
        ).one()

        return AccountSummary(
            account_id         = account.account_id,
            account_number     = account.account_number,
            account_type       = account.account_type.value,
            balance            = float(account.balance),
            transaction_count  = stats.tx_count,
            total_deposits     = float(stats.deposits),
            total_withdrawals  = float(stats.withdrawals),
        )


# ─────────────────────────────────────────────
# TRANSACTION ROUTER  (nested under /accounts)
# ─────────────────────────────────────────────

transactions_router = APIRouter(
    prefix="/accounts/{account_id}/transactions",
    tags=["Transactions"],
)


@transactions_router.get("", response_model=List[TransactionOut])
def list_transactions(
    account_id:       int                           = Path(...),
    transaction_type: Optional[TransactionTypeEnum] = Query(None),
    limit:            int                           = Query(50, ge=1, le=500),
):
    """List transactions for a given account, newest first."""
    with SessionLocal() as session:
        stmt = select(Transaction).where(Transaction.account_id == account_id)
        if transaction_type:
            stmt = stmt.where(Transaction.transaction_type == transaction_type)
        stmt = stmt.order_by(Transaction.transaction_date.desc()).limit(limit)

        txns = session.execute(stmt).scalars().all()
        return [
            TransactionOut(
                transaction_id   = t.transaction_id,
                account_id       = t.account_id,
                transaction_type = t.transaction_type.value,
                amount           = float(t.amount),
                transaction_date = t.transaction_date,
                description      = t.description,
                balance_after    = float(t.balance_after) if t.balance_after else None,
            )
            for t in txns
        ]


@transactions_router.post("", response_model=TransactionOut, status_code=status.HTTP_201_CREATED)
def post_transaction(
    account_id: int  = Path(...),
    data:       TransactionCreate = ...,
):
    """Record a new transaction on an account and update the balance."""
    with SessionLocal() as session:
        account = session.get(Account, account_id)
        if account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Account {account_id} not found",
            )
        if not account.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot post to an inactive account",
            )

        # Determine balance impact
        debit_types = {
            TransactionTypeEnum.withdrawal,
            TransactionTypeEnum.transfer_out,
            TransactionTypeEnum.fee,
            TransactionTypeEnum.atm_withdrawal,
        }
        amount = Decimal(str(data.amount))
        if data.transaction_type in debit_types:
            if account.balance < amount:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Insufficient funds",
                )
            account.balance -= amount
        else:
            account.balance += amount

        txn = Transaction(
            account_id       = account_id,
            transaction_type = data.transaction_type,
            amount           = amount,
            transaction_date = datetime.utcnow(),
            description      = data.description,
            balance_after    = account.balance,
        )
        session.add(txn)
        session.commit()
        session.refresh(txn)

        return TransactionOut(
            transaction_id   = txn.transaction_id,
            account_id       = txn.account_id,
            transaction_type = txn.transaction_type.value,
            amount           = float(txn.amount),
            transaction_date = txn.transaction_date,
            description      = txn.description,
            balance_after    = float(txn.balance_after),
        )


# ─────────────────────────────────────────────
# ASSEMBLE THE APP
# ─────────────────────────────────────────────

app = FastAPI(
    title   = "First National Bank — Account & Transaction API",
    version = "1.0.0",
)
app.include_router(accounts_router)
app.include_router(transactions_router)


@app.get("/", tags=["Meta"])
def root():
    return {"message": "Account & Transaction API running", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "module_03_fastapi_basics.03_account_routes:app",
        host="0.0.0.0", port=8000, reload=True,
    )
