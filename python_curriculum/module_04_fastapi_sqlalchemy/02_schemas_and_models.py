# =============================================================================
# MODULE 4: FASTAPI + SQLALCHEMY INTEGRATION
# Lesson 2 – Pydantic Schemas and ORM Model Mapping
# =============================================================================
# Goal: Learn the three-layer architecture:
#   Database layer  → SQLAlchemy ORM models  (module_01_python_sqlalchemy)
#   API layer       → Pydantic schemas        (this file)
#   Service layer   → Business logic          (functions that call the DB)
#
# The key rule: NEVER return ORM model objects directly from a route.
# Always convert them to Pydantic output schemas first.
# =============================================================================

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


# ─────────────────────────────────────────────
# 4.1  from_attributes = True
# ─────────────────────────────────────────────
# model_config = ConfigDict(from_attributes=True) tells Pydantic that it can
# read attribute values from ORM objects (not just dicts).
# This enables: CustomerOut.model_validate(some_customer_orm_object)

class CustomerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    customer_id:   int
    first_name:    str
    last_name:     str
    email:         str
    phone:         Optional[str]    = None
    date_of_birth: date
    city:          str
    state:         str
    credit_score:  Optional[int]    = None
    joined_date:   Optional[date]   = None
    is_active:     bool

    # Computed field — full name not stored in the DB
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


# ─────────────────────────────────────────────
# 4.2  CREATE / UPDATE SCHEMAS — keep them separate from read schemas
# ─────────────────────────────────────────────

class CustomerCreate(BaseModel):
    first_name:    str
    last_name:     str
    email:         str
    phone:         Optional[str] = None
    date_of_birth: date
    ssn_last4:     str
    address_line1: str
    city:          str
    state:         str
    zip_code:      str
    credit_score:  Optional[int] = None

    @field_validator("email")
    @classmethod
    def email_lowercase(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("state")
    @classmethod
    def state_uppercase(cls, v: str) -> str:
        if len(v) != 2:
            raise ValueError("State must be a 2-letter code")
        return v.upper()

    @field_validator("credit_score")
    @classmethod
    def valid_credit_score(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and not (300 <= v <= 850):
            raise ValueError("Credit score must be between 300 and 850")
        return v


class CustomerUpdate(BaseModel):
    """All fields optional — only provided fields are updated (PATCH semantics)."""
    first_name:    Optional[str]  = None
    last_name:     Optional[str]  = None
    email:         Optional[str]  = None
    phone:         Optional[str]  = None
    address_line1: Optional[str]  = None
    city:          Optional[str]  = None
    state:         Optional[str]  = None
    zip_code:      Optional[str]  = None
    credit_score:  Optional[int]  = None
    is_active:     Optional[bool] = None


# ─────────────────────────────────────────────
# 4.3  NESTED / RELATED SCHEMAS
# ─────────────────────────────────────────────
# When you lazy-load relationships in SQLAlchemy inside a request session,
# you can nest related data in the Pydantic response model.

class AccountSummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    account_id:     int
    account_number: str
    account_type:   str
    balance:        float


class CustomerWithAccountsOut(CustomerOut):
    """Extends CustomerOut with a list of the customer's accounts."""
    accounts: List[AccountSummaryOut] = []


# ─────────────────────────────────────────────
# 4.4  ACCOUNT SCHEMAS
# ─────────────────────────────────────────────

class AccountOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    account_id:     int
    customer_id:    int
    branch_id:      int
    account_number: str
    account_type:   str
    balance:        float
    opened_date:    date
    is_active:      bool


class AccountCreate(BaseModel):
    customer_id:     int
    branch_id:       int
    account_number:  str
    account_type:    str
    opening_deposit: float = 0.0

    @field_validator("account_number")
    @classmethod
    def account_number_format(cls, v: str) -> str:
        v = v.strip()
        if not (10 <= len(v) <= 20):
            raise ValueError("account_number must be 10–20 characters")
        if not v.isalnum():
            raise ValueError("account_number must be alphanumeric")
        return v

    @field_validator("opening_deposit")
    @classmethod
    def deposit_non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("opening_deposit must be >= 0")
        return v


# ─────────────────────────────────────────────
# 4.5  TRANSACTION SCHEMAS
# ─────────────────────────────────────────────

class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    transaction_id:   int
    account_id:       int
    transaction_type: str
    amount:           float
    transaction_date: datetime
    description:      Optional[str] = None
    balance_after:    Optional[float] = None


class TransactionCreate(BaseModel):
    transaction_type: str
    amount:           float
    description:      Optional[str] = None

    VALID_TYPES = {
        "deposit", "withdrawal", "transfer_in", "transfer_out",
        "fee", "interest", "payment", "refund", "atm_withdrawal",
    }

    @field_validator("transaction_type")
    @classmethod
    def valid_type(cls, v: str) -> str:
        if v not in cls.VALID_TYPES:
            raise ValueError(f"transaction_type must be one of {sorted(cls.VALID_TYPES)}")
        return v

    @field_validator("amount")
    @classmethod
    def positive_amount(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("amount must be positive")
        return v


# ─────────────────────────────────────────────
# 4.6  PAGINATION WRAPPER
# ─────────────────────────────────────────────
# Generic paginated response: wrap any list of items.

from typing import TypeVar, Generic

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    total:     int
    page:      int
    page_size: int
    items:     List[T]

    model_config = ConfigDict(arbitrary_types_allowed=True)


# Usage example:
#   return Page[CustomerOut](total=100, page=1, page_size=20, items=customer_list)


# ─────────────────────────────────────────────
# 4.7  ERROR SCHEMAS
# ─────────────────────────────────────────────

class ErrorResponse(BaseModel):
    detail: str


class ValidationErrorItem(BaseModel):
    loc:  List[str]
    msg:  str
    type: str


class ValidationErrorResponse(BaseModel):
    detail: List[ValidationErrorItem]


# ─────────────────────────────────────────────
# 4.8  SCHEMA CONVERSION HELPERS
# ─────────────────────────────────────────────
# A helper function documents the ORM → Pydantic conversion explicitly.

from module_01_python_sqlalchemy.setup_and_models import (  # type: ignore
    Customer as CustomerORM,
    Account  as AccountORM,
    Transaction as TransactionORM,
)


def customer_to_schema(c: CustomerORM) -> CustomerOut:
    """Convert a SQLAlchemy Customer ORM object to the CustomerOut schema."""
    return CustomerOut.model_validate(c)


def account_to_schema(a: AccountORM) -> AccountOut:
    """Convert a SQLAlchemy Account ORM object to AccountOut.

    Note: account_type is an Enum; .value returns the string form.
    """
    return AccountOut(
        account_id     = a.account_id,
        customer_id    = a.customer_id,
        branch_id      = a.branch_id,
        account_number = a.account_number,
        account_type   = a.account_type.value,
        balance        = float(a.balance),
        opened_date    = a.opened_date,
        is_active      = a.is_active,
    )


def transaction_to_schema(t: TransactionORM) -> TransactionOut:
    """Convert a SQLAlchemy Transaction ORM object to TransactionOut."""
    return TransactionOut(
        transaction_id   = t.transaction_id,
        account_id       = t.account_id,
        transaction_type = t.transaction_type.value,
        amount           = float(t.amount),
        transaction_date = t.transaction_date,
        description      = t.description,
        balance_after    = float(t.balance_after) if t.balance_after is not None else None,
    )


# ─────────────────────────────────────────────
# DEMO — validate a sample payload
# ─────────────────────────────────────────────

if __name__ == "__main__":
    # Valid create
    payload = CustomerCreate(
        first_name    = "Alice",
        last_name     = "Nguyen",
        email         = "  ALICE@Example.COM  ",  # will be lowercased
        date_of_birth = date(1985, 3, 22),
        ssn_last4     = "4321",
        address_line1 = "100 Main St",
        city          = "Austin",
        state         = "tx",              # will be uppercased
        zip_code      = "78701",
        credit_score  = 720,
    )
    print("Valid payload:", payload.model_dump())

    # Test validation error
    try:
        bad = CustomerCreate(
            first_name    = "Bob",
            last_name     = "Smith",
            email         = "bob@test.com",
            date_of_birth = date(1990, 1, 1),
            ssn_last4     = "123",     # invalid — only 3 digits
            address_line1 = "1 St",
            city          = "NYC",
            state         = "NY",
            zip_code      = "10001",
            credit_score  = 900,       # invalid — above 850
        )
    except Exception as e:
        print("\nValidation errors:", e)
