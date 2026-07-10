"""
Module 02 — Lesson 1: Introduction to @dataclass
=================================================
Python 3.11 · stdlib only

The @dataclass decorator auto-generates __init__, __repr__, __eq__ and
optionally __hash__, __lt__, etc. from field annotations.
"""
from __future__ import annotations

import dataclasses
import math
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# 1. Basic @dataclass
# ---------------------------------------------------------------------------
@dataclass
class Point:
    """
    Python generates:
        def __init__(self, x: float, y: float) -> None: ...
        def __repr__(self) -> str: ...
        def __eq__(self, other) -> bool: ...
    """
    x: float
    y: float

    def distance_to(self, other: Point) -> float:
        return math.hypot(self.x - other.x, self.y - other.y)


# ---------------------------------------------------------------------------
# 2. Default values and field()
# ---------------------------------------------------------------------------
@dataclass
class Config:
    host: str = "localhost"
    port: int = 8080
    debug: bool = False
    tags: list[str] = field(default_factory=list)   # NEVER use mutable defaults directly
    metadata: dict[str, str] = field(default_factory=dict, repr=False)


# ---------------------------------------------------------------------------
# 3. Frozen (immutable) dataclass — value objects
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Money:
    """
    frozen=True generates __hash__ and blocks __setattr__/__delattr__.
    Use for value objects that must never change.
    """
    amount: float
    currency: str

    def __post_init__(self) -> None:
        # __post_init__ runs after __init__ — ideal for validation
        if self.amount < 0:
            raise ValueError(f"Amount cannot be negative: {self.amount}")
        # With frozen=True you CANNOT do self.currency = ... directly.
        # Use object.__setattr__ if you need coercion:
        object.__setattr__(self, "currency", self.currency.upper())

    def __add__(self, other: Money) -> Money:
        if self.currency != other.currency:
            raise ValueError(f"Currency mismatch: {self.currency} vs {other.currency}")
        return Money(self.amount + other.amount, self.currency)


# ---------------------------------------------------------------------------
# 4. Ordering
# ---------------------------------------------------------------------------
@dataclass(order=True)
class Version:
    """
    order=True generates __lt__, __le__, __gt__, __ge__ based on
    fields in declaration order.
    """
    major: int
    minor: int
    patch: int = 0

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


# ---------------------------------------------------------------------------
# 5. ClassVar and InitVar
# ---------------------------------------------------------------------------
import dataclasses as dc
from typing import ClassVar

@dataclass
class Employee:
    name: str
    salary: float
    # ClassVar: not included in __init__ / __repr__ / __eq__
    company: ClassVar[str] = "ACME Corp"
    # InitVar: passed to __init__ but NOT stored as field
    bonus_pct: dc.InitVar[float] = 0.0
    annual_bonus: float = field(init=False)

    def __post_init__(self, bonus_pct: float) -> None:
        self.annual_bonus = self.salary * bonus_pct


# ---------------------------------------------------------------------------
# 6. dataclasses.asdict / astuple / replace
# ---------------------------------------------------------------------------
@dataclass
class Rectangle:
    width: float
    height: float

    @property
    def area(self) -> float:
        return self.width * self.height


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Basic
    p1, p2 = Point(0, 0), Point(3, 4)
    print(p1)                    # Point(x=0, y=0)
    print(p1 == Point(0, 0))     # True
    print(p1.distance_to(p2))    # 5.0

    # Default factory
    c1 = Config()
    c2 = Config()
    c1.tags.append("prod")
    print(c1.tags, c2.tags)      # ['prod']  []  — separate lists!

    # Frozen
    m1 = Money(10.50, "gbp")
    m2 = Money(5.00, "GBP")
    print(m1 + m2)               # Money(amount=15.5, currency='GBP')
    try:
        m1.amount = 0            # type: ignore
    except dataclasses.FrozenInstanceError as e:
        print(f"Immutable! {e}")

    # Ordering
    versions = [Version(2, 0), Version(1, 9), Version(1, 10, 3)]
    print(sorted(versions))      # [1.9.0, 1.10.3, 2.0.0]

    # Employee with InitVar
    emp = Employee("Alice", 60_000, bonus_pct=0.10)
    print(emp)                   # Employee(name='Alice', salary=60000, annual_bonus=6000.0)
    print(Employee.company)      # ACME Corp

    # Utility functions
    rect = Rectangle(3, 4)
    print(dataclasses.asdict(rect))   # {'width': 3, 'height': 4}
    wider = dataclasses.replace(rect, width=5)
    print(wider.area)                  # 20.0
