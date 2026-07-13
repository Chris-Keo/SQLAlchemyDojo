"""
Module 01 — Lesson 2: Value Objects vs Entity Objects
=====================================================
Python 3.11 · No external dependencies

Two fundamentally different ways classes are used:

  Value Object  — defined by its attributes; two instances with the same
                  data ARE equal.  Examples: Money, Point, DateRange.

  Entity Object — defined by identity (id); two users with the same name
                  are NOT the same user.  Examples: User, Order, Product.

Understanding this distinction tells you whether to make objects immutable
(frozen dataclasses / NamedTuple) or mutable (entities with an id).
"""
from __future__ import annotations

import uuid
from typing import Self


# ---------------------------------------------------------------------------
# VALUE OBJECT — Money
# ---------------------------------------------------------------------------
class Money:
    """
    A value object.  Two Money instances with the same amount+currency are
    interchangeable — there is no concept of "which £10 note".
    """

    __slots__ = ("_amount", "_currency")

    def __init__(self, amount: float, currency: str) -> None:
        if amount < 0:
            raise ValueError("Money amount cannot be negative.")
        object.__setattr__(self, "_amount", round(amount, 2))
        object.__setattr__(self, "_currency", currency.upper())

    # Immutability: block attribute mutation
    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError("Money is immutable.")

    @property
    def amount(self) -> float:
        return self._amount  # type: ignore[return-value]

    @property
    def currency(self) -> str:
        return self._currency  # type: ignore[return-value]

    def __add__(self, other: Self) -> Self:
        if self.currency != other.currency:
            raise ValueError(f"Cannot add {self.currency} and {other.currency}.")
        return Money(self.amount + other.amount, self.currency)  # type: ignore[return-value]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount == other.amount and self.currency == other.currency

    def __hash__(self) -> int:
        return hash((self.amount, self.currency))

    def __repr__(self) -> str:
        return f"Money({self.amount:.2f} {self.currency})"


# ---------------------------------------------------------------------------
# ENTITY OBJECT — User
# ---------------------------------------------------------------------------
class User:
    """
    An entity object.  Two users can have the same name, but they are
    different people — equality is determined by their unique `id`.
    """

    def __init__(self, name: str, email: str) -> None:
        self.id: str = str(uuid.uuid4())   # identity
        self.name = name
        self.email = email

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, User):
            return NotImplemented
        return self.id == other.id    # identity-based, NOT name-based

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return f"User(id={self.id[:8]}…, name={self.name!r})"

    def rename(self, new_name: str) -> None:
        """Entities are mutable — their state changes over time."""
        self.name = new_name


# ---------------------------------------------------------------------------
# Rule of Thumb Table
# ---------------------------------------------------------------------------
RULES = """
┌─────────────────────┬──────────────────────────┬──────────────────────────┐
│ Criterion           │ Value Object             │ Entity Object            │
├─────────────────────┼──────────────────────────┼──────────────────────────┤
│ Equality based on   │ All attributes           │ Unique ID / identity     │
│ Mutability          │ Immutable (preferred)    │ Mutable                  │
│ Hashable            │ Yes                      │ Yes (via id)             │
│ Lifecycle           │ Disposable / replaceable │ Tracked over time        │
│ Best representation │ frozen dataclass /       │ Plain class / SQLAlchemy │
│                     │ NamedTuple / Pydantic    │ model / Django model     │
└─────────────────────┴──────────────────────────┴──────────────────────────┘
"""


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Value object equality
    a = Money(10.50, "GBP")
    b = Money(10.50, "GBP")
    c = Money(20.00, "GBP")
    print(a == b)          # True  — same data ⟹ same value
    print(a == c)          # False
    print(a + b)           # Money(21.00 GBP)
    print({a, b, c})       # {Money(10.50 GBP), Money(20.00 GBP)} — 2 unique

    # Entity equality
    u1 = User("Alice", "alice@example.com")
    u2 = User("Alice", "alice@example.com")  # same data, different entity
    print(u1 == u2)        # False — different IDs
    u1.rename("Alicia")
    print(u1)              # name changed, same entity

    print(RULES)
