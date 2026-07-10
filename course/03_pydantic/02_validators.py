"""
Module 03 — Lesson 2: Pydantic Validators
==========================================
Python 3.11 · requires: pydantic>=2.7

Covers:
  • @field_validator — single field validation + transformation
  • @model_validator  — cross-field / whole-model validation
  • Annotated custom types (reusable constraints)
  • Discriminated unions
"""
from __future__ import annotations

from datetime import date
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)
from pydantic.functional_validators import AfterValidator, BeforeValidator


# ---------------------------------------------------------------------------
# 1. @field_validator
# ---------------------------------------------------------------------------
class Registration(BaseModel):
    username: str
    pwd: str
    confirm_password: str
    birth_date: date

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.replace("_", "").isalnum():
            raise ValueError("Username must contain only letters, digits, or underscores.")
        return v.lower()

    @field_validator("pwd")
    @classmethod
    def pwd_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters.")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit.")
        return v

    @field_validator("birth_date")
    @classmethod
    def must_be_adult(cls, v: date) -> date:
        from datetime import date as date_
        today = date_.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 18:
            raise ValueError(f"Must be 18+. Calculated age: {age}")
        return v


# ---------------------------------------------------------------------------
# 2. @model_validator — cross-field validation
# ---------------------------------------------------------------------------
class DateRange(BaseModel):
    start: date
    end: date
    label: str = ""

    @model_validator(mode="after")
    def end_after_start(self) -> DateRange:
        if self.end <= self.start:
            raise ValueError(f"end ({self.end}) must be after start ({self.start})")
        return self

    @property
    def days(self) -> int:
        return (self.end - self.start).days


class PasswordChange(BaseModel):
    old_password: str
    new_password: str
    confirm_new: str

    @model_validator(mode="after")
    def passwords_match(self) -> PasswordChange:
        if self.new_password != self.confirm_new:
            raise ValueError("new_password and confirm_new do not match.")
        if self.new_password == self.old_password:
            raise ValueError("New password must differ from old password.")
        return self


# ---------------------------------------------------------------------------
# 3. Annotated custom types — reusable validators
# ---------------------------------------------------------------------------
def _normalise_phone(v: str) -> str:
    """Strip spaces/dashes, ensure starts with +."""
    cleaned = v.replace(" ", "").replace("-", "")
    if not cleaned.startswith("+"):
        raise ValueError("Phone number must start with country code, e.g. +44")
    if not cleaned[1:].isdigit():
        raise ValueError("Phone number must contain only digits after +.")
    return cleaned


UKPostcode = Annotated[
    str,
    BeforeValidator(lambda v: v.upper().strip()),
    Field(pattern=r"^[A-Z]{1,2}\d[A-Z\d]? ?\d[A-Z]{2}$"),
]

PhoneNumber = Annotated[str, AfterValidator(_normalise_phone)]


class ContactInfo(BaseModel):
    name: str
    phone: PhoneNumber
    postcode: UKPostcode


# ---------------------------------------------------------------------------
# 4. Discriminated Unions — type-safe polymorphism
# ---------------------------------------------------------------------------
class CreditCard(BaseModel):
    payment_type: Literal["credit_card"]
    card_number: str = Field(min_length=16, max_length=16)
    expiry: str = Field(pattern=r"^\d{2}/\d{2}$")
    cvv: str = Field(min_length=3, max_length=4)


class BankTransfer(BaseModel):
    payment_type: Literal["bank_transfer"]
    sort_code: str = Field(pattern=r"^\d{2}-\d{2}-\d{2}$")
    account_number: str = Field(min_length=8, max_length=8)


class PayPal(BaseModel):
    payment_type: Literal["paypal"]
    email: str


# Discriminated union — Pydantic picks the right model based on payment_type
from typing import Union
from pydantic import RootModel

PaymentMethod = Annotated[
    Union[CreditCard, BankTransfer, PayPal],
    Field(discriminator="payment_type"),
]


class Order(BaseModel):
    order_id: str
    amount: float
    payment: PaymentMethod


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # @field_validator — valid registration
    valid_data = {
        "username": "alice123",
        "pwd": "Secret1!",
        "confirm_password": "Secret1!",
        "birth_date": "1990-06-15",
    }
    try:
        r = Registration(**valid_data)
        print("Registered:", r.username)
    except ValidationError as e:
        print(e)

    # Multiple errors at once (bad data)
    bad_data = {
        "username": "al!ce",
        "pwd": "weak",
        "confirm_password": "weak",
        "birth_date": "2015-01-01",
    }
    try:
        Registration(**bad_data)
    except ValidationError as e:
        print("\nAll errors:")
        for err in e.errors():
            print(f"  {'.'.join(str(x) for x in err['loc'])}: {err['msg']}")

    # @model_validator cross-field
    dr = DateRange(start="2024-01-01", end="2024-12-31", label="FY2024")
    print(f"\n{dr.label}: {dr.days} days")

    try:
        DateRange(start="2024-12-31", end="2024-01-01")
    except ValidationError as e:
        print("Cross-field error:", e.errors()[0]["msg"])

    # Annotated types
    c = ContactInfo(name="Bob", phone="+44 7911 123456", postcode="sw1a 1aa")
    print(f"\n{c.name}: {c.postcode}")  # phone omitted from output — treat as private

    # Discriminated union
    order = Order(
        order_id="ORD-001",
        amount=99.99,
        payment={"payment_type": "credit_card", "card_number": "1234567890123456", "expiry": "12/26", "cvv": "123"},
    )
    print(f"\nPayment via: {type(order.payment).__name__}")  # prints type name only
