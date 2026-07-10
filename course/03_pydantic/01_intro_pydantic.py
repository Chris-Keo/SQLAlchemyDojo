"""
Module 03 — Lesson 1: Introduction to Pydantic v2
==================================================
Python 3.11 · requires: pydantic>=2.7

Pydantic v2 is a ground-up rewrite in Rust (via pydantic-core) that is
5-50× faster than v1 while keeping a similar API.

Key difference from dataclasses:
  @dataclass  — no validation; trusts the caller.
  BaseModel   — validates and coerces every field on construction.
"""
from __future__ import annotations

import json
from datetime import date, datetime
from typing import Annotated
from uuid import UUID, uuid4

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    HttpUrl,
    NonNegativeFloat,
    PositiveInt,
    computed_field,
    model_validator,
)


# ---------------------------------------------------------------------------
# 1. Basic BaseModel
# ---------------------------------------------------------------------------
class User(BaseModel):
    """
    Fields are declared as class attributes with type annotations.
    Pydantic validates every field at instantiation time.
    """
    id: UUID = Field(default_factory=uuid4)
    name: str
    email: EmailStr           # validated email format
    age: PositiveInt          # must be > 0
    website: HttpUrl | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # model_config replaces the inner Config class from Pydantic v1
    model_config = ConfigDict(
        str_strip_whitespace=True,   # auto-strip leading/trailing spaces
        frozen=False,                # allow mutation (set True for immutability)
    )


# ---------------------------------------------------------------------------
# 2. Nested models
# ---------------------------------------------------------------------------
class Address(BaseModel):
    street: str
    city: str
    country: str = "GB"
    postcode: str


class Customer(BaseModel):
    name: str
    email: EmailStr
    billing_address: Address
    shipping_address: Address | None = None

    @computed_field  # type: ignore[misc]
    @property
    def display_name(self) -> str:
        return self.name.title()


# ---------------------------------------------------------------------------
# 3. Field constraints and metadata
# ---------------------------------------------------------------------------
class Product(BaseModel):
    sku: str = Field(min_length=3, max_length=20, pattern=r"^[A-Z0-9\-]+$")
    name: str = Field(min_length=1, max_length=100)
    price: NonNegativeFloat
    stock: int = Field(ge=0)
    description: str | None = Field(default=None, max_length=1000)
    tags: list[str] = Field(default_factory=list, max_length=10)

    @computed_field  # type: ignore[misc]
    @property
    def in_stock(self) -> bool:
        return self.stock > 0


# ---------------------------------------------------------------------------
# 4. Type coercion — Pydantic converts compatible types automatically
# ---------------------------------------------------------------------------
class DataPoint(BaseModel):
    value: float      # "3.14" → 3.14  (str coerced to float)
    timestamp: date   # "2024-01-15" → date(2024, 1, 15)
    active: bool      # "true", 1, "yes" → True


# ---------------------------------------------------------------------------
# 5. model_dump / model_dump_json / model_json_schema
# ---------------------------------------------------------------------------
class Invoice(BaseModel):
    number: str
    customer: str
    total: NonNegativeFloat
    issued: date = Field(default_factory=date.today)

    model_config = ConfigDict(json_encoders={date: lambda d: d.isoformat()})


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Basic validation
    u = User(name="  alice  ", email="alice@example.com", age=30)
    print(u)
    print(f"name stripped: {u.name!r}")  # 'alice' (whitespace stripped)

    # Type coercion
    dp = DataPoint(value="3.14", timestamp="2024-01-15", active="yes")
    print(dp)  # value=3.14, timestamp=date(2024, 1, 15), active=True

    # Validation error
    from pydantic import ValidationError
    try:
        User(name="Bob", email="not-an-email", age=-5)
    except ValidationError as e:
        print("\nValidation errors:")
        for err in e.errors():
            print(f"  {err['loc']} — {err['msg']}")

    # Nested model
    cust = Customer(
        name="john doe",
        email="john@example.com",
        billing_address=Address(street="1 High St", city="London", postcode="SW1A 1AA"),
    )
    print(f"\n{cust.display_name}")  # 'John Doe' (computed_field)

    # Serialisation
    inv = Invoice(number="INV-001", customer="Alice", total=149.99)
    print("\n--- dict ---")
    print(inv.model_dump())
    print("\n--- JSON ---")
    print(inv.model_dump_json(indent=2))
    print("\n--- JSON Schema ---")
    schema = json.dumps(Invoice.model_json_schema(), indent=2)
    print(schema[:400], "...")
