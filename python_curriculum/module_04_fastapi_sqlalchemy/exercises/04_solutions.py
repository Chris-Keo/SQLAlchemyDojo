# =============================================================================
# MODULE 4: SOLUTIONS
# =============================================================================

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Generator

from fastapi import FastAPI, APIRouter, Depends, HTTPException, Query, Path, Request
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select, func, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from module_01_python_sqlalchemy.setup_and_models import (  # type: ignore
    Customer, Account, Transaction, Employee, Loan, FraudAlert, Branch,
    TransactionTypeEnum, LoanStatusEnum, FraudStatusEnum
)
from module_04_fastapi_sqlalchemy.01_database_session import get_db  # type: ignore
from module_04_fastapi_sqlalchemy.02_schemas_and_models import (  # type: ignore
    CustomerOut, AccountOut, TransactionOut, Page,
    customer_to_schema, account_to_schema, transaction_to_schema
)

app = FastAPI(title="Module 4 Solutions", version="1.0.0")


# ──────────────────────────────────────────────
# EXERCISE 1 — Customer 360 view
# ──────────────────────────────────────────────

class AccountBrief(BaseModel):
    account_id:   int
    account_type: str
    balance:      float
    is_active:    bool

class LoanBrief(BaseModel):
    loan_id:           int
    loan_type:         str
    status:            str
    remaining_balance: Optional[float]

class FraudBrief(BaseModel):
    alert_id:     int
    alert_type:   str
    status:       str
    amount_at_risk: Optional[float]

class Customer360(BaseModel):
    customer_id:  int
    full_name:    str
    email:        str
    credit_score: Optional[int]
    accounts:     List[AccountBrief]
    loans:        List[LoanBrief]
    fraud_alerts: List[FraudBrief]


@app.get("/customers/{customer_id}/360", response_model=Customer360, tags=["Customers"])
def customer_360(customer_id: int = Path(...), db: Session = Depends(get_db)):
    customer = db.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    accounts = db.execute(
        select(Account)
        .where(Account.customer_id == customer_id, Account.is_active == True)
    ).scalars().all()

    loans = db.execute(
        select(Loan).where(Loan.customer_id == customer_id)
    ).scalars().all()

    alerts = db.execute(
        select(FraudAlert)
        .where(FraudAlert.customer_id == customer_id,
               FraudAlert.status == FraudStatusEnum.open)
    ).scalars().all()

    return Customer360(
        customer_id  = customer.customer_id,
        full_name    = f"{customer.first_name} {customer.last_name}",
        email        = customer.email,
        credit_score = customer.credit_score,
        accounts     = [
            AccountBrief(
                account_id   = a.account_id,
                account_type = a.account_type.value,
                balance      = float(a.balance),
                is_active    = a.is_active,
            ) for a in accounts
        ],
        loans = [
            LoanBrief(
                loan_id           = lo.loan_id,
                loan_type         = lo.loan_type,
                status            = lo.status.value,
                remaining_balance = float(lo.remaining_balance) if lo.remaining_balance else None,
            ) for lo in loans
        ],
        fraud_alerts = [
            FraudBrief(
                alert_id      = al.alert_id,
                alert_type    = al.alert_type,
                status        = al.status.value,
                amount_at_risk = float(al.amount_at_risk) if al.amount_at_risk else None,
            ) for al in alerts
        ],
    )


# ──────────────────────────────────────────────
# EXERCISE 3 — Account transfer
# ──────────────────────────────────────────────

class TransferRequest(BaseModel):
    to_account_id: int
    amount:        float
    description:   Optional[str] = None


class TransferResponse(BaseModel):
    source_account_id: int
    dest_account_id:   int
    amount:            float
    debit_tx_id:       int
    credit_tx_id:      int
    executed_at:       datetime


@app.post(
    "/accounts/{account_id}/transfer",
    response_model=TransferResponse,
    status_code=201,
    tags=["Accounts"],
)
def transfer_funds(
    account_id: int              = Path(...),
    data:       TransferRequest  = ...,
    db:         Session          = Depends(get_db),
):
    src = db.get(Account, account_id)
    if src is None:
        raise HTTPException(status_code=404, detail=f"Source account {account_id} not found")
    dst = db.get(Account, data.to_account_id)
    if dst is None:
        raise HTTPException(status_code=404, detail=f"Destination account {data.to_account_id} not found")

    amount = Decimal(str(data.amount))
    if amount <= 0:
        raise HTTPException(status_code=422, detail="Transfer amount must be positive")
    if src.balance < amount:
        raise HTTPException(status_code=422, detail="Insufficient funds")

    now = datetime.utcnow()
    src.balance -= amount
    dst.balance += amount

    debit_txn = Transaction(
        account_id       = account_id,
        transaction_type = TransactionTypeEnum.transfer_out,
        amount           = amount,
        transaction_date = now,
        description      = data.description or f"Transfer to account {data.to_account_id}",
        balance_after    = src.balance,
    )
    credit_txn = Transaction(
        account_id       = data.to_account_id,
        transaction_type = TransactionTypeEnum.transfer_in,
        amount           = amount,
        transaction_date = now,
        description      = data.description or f"Transfer from account {account_id}",
        balance_after    = dst.balance,
    )
    db.add(debit_txn)
    db.add(credit_txn)
    db.commit()
    db.refresh(debit_txn)
    db.refresh(credit_txn)

    return TransferResponse(
        source_account_id = account_id,
        dest_account_id   = data.to_account_id,
        amount            = float(amount),
        debit_tx_id       = debit_txn.transaction_id,
        credit_tx_id      = credit_txn.transaction_id,
        executed_at       = now,
    )


# ──────────────────────────────────────────────
# EXERCISE 4 — Employees endpoint
# ──────────────────────────────────────────────

class EmployeeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    employee_id: int
    branch_id:   int
    first_name:  str
    last_name:   str
    job_title:   str
    salary:      float
    is_active:   bool


@app.get("/employees", response_model=Page[EmployeeOut], tags=["Employees"])
def list_employees(
    db:         Session       = Depends(get_db),
    branch_id:  Optional[int] = Query(None),
    min_salary: Optional[float] = Query(None),
    max_salary: Optional[float] = Query(None),
    page:       int           = Query(1, ge=1),
    page_size:  int           = Query(20, ge=1, le=100),
):
    filters = [Employee.is_active == True]
    if branch_id:
        filters.append(Employee.branch_id == branch_id)
    if min_salary is not None:
        filters.append(Employee.salary >= min_salary)
    if max_salary is not None:
        filters.append(Employee.salary <= max_salary)

    total = db.execute(
        select(func.count()).select_from(Employee).where(*filters)
    ).scalar()

    items = db.execute(
        select(Employee)
        .where(*filters)
        .order_by(Employee.salary.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).scalars().all()

    return Page[EmployeeOut](
        total     = total,
        page      = page,
        page_size = page_size,
        items     = [
            EmployeeOut(
                employee_id = e.employee_id,
                branch_id   = e.branch_id,
                first_name  = e.first_name,
                last_name   = e.last_name,
                job_title   = e.job_title,
                salary      = float(e.salary),
                is_active   = e.is_active,
            ) for e in items
        ],
    )


# ──────────────────────────────────────────────
# EXERCISE 5 — Global SQLAlchemy error handler
# ──────────────────────────────────────────────

from fastapi.responses import JSONResponse


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    # Log the real error internally (don't expose to client)
    print(f"[DB ERROR] {request.method} {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "A database error occurred. Please try again later."},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("module_04_fastapi_sqlalchemy.exercises.04_solutions:app",
                host="0.0.0.0", port=8001, reload=True)
