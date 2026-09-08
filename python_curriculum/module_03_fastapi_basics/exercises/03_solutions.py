# =============================================================================
# MODULE 3: SOLUTIONS
# =============================================================================

from datetime import date
from typing import Optional, List

from fastapi import FastAPI, APIRouter, HTTPException, status, Query, Path
from pydantic import BaseModel, field_validator
from sqlalchemy import select, or_

from module_01_python_sqlalchemy.setup_and_models import (  # type: ignore
    SessionLocal, Customer, Account, Employee, Loan, Branch,
    AccountTypeEnum, LoanStatusEnum
)

app = FastAPI(title="Module 3 Solutions", version="1.0.0")


# ──────────────────────────────────────────────
# EXERCISE 1 — Customer accounts
# ──────────────────────────────────────────────

class AccountOut(BaseModel):
    account_id:     int
    account_number: str
    account_type:   str
    balance:        float
    is_active:      bool


customer_router = APIRouter(prefix="/customers", tags=["Customers"])


@customer_router.get("/{customer_id}/accounts", response_model=List[AccountOut])
def get_customer_accounts(
    customer_id:  int  = Path(...),
    active_only:  bool = Query(True),
):
    with SessionLocal() as session:
        customer = session.get(Customer, customer_id)
        if customer is None:
            raise HTTPException(status_code=404, detail="Customer not found")
        stmt = select(Account).where(Account.customer_id == customer_id)
        if active_only:
            stmt = stmt.where(Account.is_active == True)
        accounts = session.execute(stmt).scalars().all()
        return [
            AccountOut(
                account_id     = a.account_id,
                account_number = a.account_number,
                account_type   = a.account_type.value,
                balance        = float(a.balance),
                is_active      = a.is_active,
            )
            for a in accounts
        ]


app.include_router(customer_router)


# ──────────────────────────────────────────────
# EXERCISE 2 — Branch employees
# ──────────────────────────────────────────────

class EmployeeOut(BaseModel):
    employee_id: int
    first_name:  str
    last_name:   str
    job_title:   str
    salary:      float
    is_active:   bool


branch_router = APIRouter(prefix="/branches", tags=["Branches"])


@branch_router.get("/{branch_id}/employees", response_model=List[EmployeeOut])
def get_branch_employees(
    branch_id:        int  = Path(...),
    include_inactive: bool = Query(False),
):
    with SessionLocal() as session:
        branch = session.get(Branch, branch_id)
        if branch is None:
            raise HTTPException(status_code=404, detail="Branch not found")
        stmt = select(Employee).where(Employee.branch_id == branch_id)
        if not include_inactive:
            stmt = stmt.where(Employee.is_active == True)
        employees = session.execute(stmt).scalars().all()
        return [
            EmployeeOut(
                employee_id = e.employee_id,
                first_name  = e.first_name,
                last_name   = e.last_name,
                job_title   = e.job_title,
                salary      = float(e.salary),
                is_active   = e.is_active,
            )
            for e in employees
        ]


app.include_router(branch_router)


# ──────────────────────────────────────────────
# EXERCISE 3 — Customer loans
# ──────────────────────────────────────────────

class LoanOut(BaseModel):
    loan_id:           int
    loan_type:         str
    principal_amount:  float
    interest_rate:     float
    term_months:       int
    status:            str
    remaining_balance: Optional[float]
    monthly_payment:   Optional[float]


@customer_router.get("/{customer_id}/loans", response_model=List[LoanOut])
def get_customer_loans(
    customer_id: int                       = Path(...),
    status_filter: Optional[str]           = Query(None, alias="status"),
):
    with SessionLocal() as session:
        customer = session.get(Customer, customer_id)
        if customer is None:
            raise HTTPException(status_code=404, detail="Customer not found")
        stmt = select(Loan).where(Loan.customer_id == customer_id)
        if status_filter:
            try:
                stmt = stmt.where(Loan.status == LoanStatusEnum(status_filter))
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status '{status_filter}'. "
                           f"Valid options: {[s.value for s in LoanStatusEnum]}"
                )
        loans = session.execute(stmt).scalars().all()
        return [
            LoanOut(
                loan_id           = lo.loan_id,
                loan_type         = lo.loan_type,
                principal_amount  = float(lo.principal_amount),
                interest_rate     = float(lo.interest_rate),
                term_months       = lo.term_months,
                status            = lo.status.value,
                remaining_balance = float(lo.remaining_balance) if lo.remaining_balance else None,
                monthly_payment   = float(lo.monthly_payment)   if lo.monthly_payment   else None,
            )
            for lo in loans
        ]


# ──────────────────────────────────────────────
# EXERCISE 4 — AccountCreate validation
# ──────────────────────────────────────────────

class AccountCreateValidated(BaseModel):
    customer_id:    int
    branch_id:      int
    account_number: str
    account_type:   AccountTypeEnum

    @field_validator("account_number")
    @classmethod
    def validate_account_number(cls, v: str) -> str:
        if not (10 <= len(v) <= 20):
            raise ValueError("account_number must be 10–20 characters long")
        if not v.isalnum():
            raise ValueError("account_number must be alphanumeric (letters and digits only)")
        return v


# ──────────────────────────────────────────────
# EXERCISE 5 — Customer search
# ──────────────────────────────────────────────

class CustomerSearchResult(BaseModel):
    customer_id: int
    first_name:  str
    last_name:   str
    email:       str
    state:       str


@app.get("/search", response_model=List[CustomerSearchResult], tags=["Search"])
def search_customers(q: str = Query(..., min_length=2, description="Search string")):
    """Case-insensitive search across customer name and email."""
    with SessionLocal() as session:
        pattern = f"%{q}%"
        stmt = (
            select(Customer)
            .where(
                or_(
                    Customer.first_name.ilike(pattern),
                    Customer.last_name.ilike(pattern),
                    Customer.email.ilike(pattern),
                )
            )
            .order_by(Customer.last_name)
            .limit(20)
        )
        customers = session.execute(stmt).scalars().all()
        return [
            CustomerSearchResult(
                customer_id = c.customer_id,
                first_name  = c.first_name,
                last_name   = c.last_name,
                email       = c.email,
                state       = c.state,
            )
            for c in customers
        ]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("module_03_fastapi_basics.exercises.03_solutions:app",
                host="0.0.0.0", port=8001, reload=True)
