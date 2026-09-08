"""
Module 02 — Lesson 3: Python 3.11 Dataclass Features
=====================================================
Python 3.11+ · stdlib only

Highlights:
  • StrEnum for type-safe status fields
  • Self return type with dataclasses
  • tomllib for config loading into dataclasses
  • ExceptionGroup for batch validation errors
  • LiteralString for safe query building
"""
from __future__ import annotations

import sys
import tomllib
from dataclasses import dataclass, field
from enum import StrEnum
from typing import LiteralString, Self


# ---------------------------------------------------------------------------
# 1. StrEnum — type-safe string enumerations (Python 3.11)
# ---------------------------------------------------------------------------
class OrderStatus(StrEnum):
    """
    StrEnum values ARE strings — no .value needed.
    str(OrderStatus.PENDING) == "pending"
    """
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


@dataclass
class Order:
    id: str
    customer: str
    status: OrderStatus = OrderStatus.PENDING
    items: list[str] = field(default_factory=list)

    def confirm(self) -> Self:
        return Order(self.id, self.customer, OrderStatus.CONFIRMED, self.items.copy())

    def ship(self) -> Self:
        if self.status != OrderStatus.CONFIRMED:
            raise ValueError(f"Cannot ship order in status {self.status!r}")
        return Order(self.id, self.customer, OrderStatus.SHIPPED, self.items.copy())

    def is_active(self) -> bool:
        return self.status not in (OrderStatus.DELIVERED, OrderStatus.CANCELLED)


# ---------------------------------------------------------------------------
# 2. tomllib — load TOML config into a dataclass (Python 3.11 stdlib)
# ---------------------------------------------------------------------------
SAMPLE_TOML = b"""
[database]
host = "localhost"
port = 5432
name = "mydb"
pool_size = 5

[cache]
host = "localhost"
port = 6379
ttl = 300
"""


@dataclass
class DatabaseConfig:
    host: str
    port: int
    name: str
    pool_size: int = 5

    @classmethod
    def from_toml(cls, raw: bytes, section: str = "database") -> Self:
        data = tomllib.loads(raw.decode())
        return cls(**data[section])


@dataclass
class CacheConfig:
    host: str
    port: int
    ttl: int = 300

    @classmethod
    def from_toml(cls, raw: bytes, section: str = "cache") -> Self:
        data = tomllib.loads(raw.decode())
        return cls(**data[section])


@dataclass
class AppConfig:
    database: DatabaseConfig
    cache: CacheConfig

    @classmethod
    def from_toml(cls, raw: bytes) -> Self:
        return cls(
            database=DatabaseConfig.from_toml(raw),
            cache=CacheConfig.from_toml(raw),
        )


# ---------------------------------------------------------------------------
# 3. ExceptionGroup — batch validation (Python 3.11)
# ---------------------------------------------------------------------------
@dataclass
class FormData:
    username: str
    email: str
    age: int

    def validate(self) -> None:
        """Raises ExceptionGroup with ALL errors, not just the first."""
        errors: list[Exception] = []
        if len(self.username) < 3:
            errors.append(ValueError(f"username too short: {self.username!r}"))
        if "@" not in self.email:
            errors.append(ValueError(f"invalid email: {self.email!r}"))
        if not 0 <= self.age <= 150:
            errors.append(ValueError(f"invalid age: {self.age}"))
        if errors:
            raise ExceptionGroup("form validation failed", errors)


# ---------------------------------------------------------------------------
# 4. LiteralString — safe query building
# ---------------------------------------------------------------------------
@dataclass
class QueryBuilder:
    """
    LiteralString (PEP 675, Python 3.11) ensures only hard-coded strings
    (not user-provided strings) are passed as table/column names.
    Prevents SQL injection at the type-checker level.
    """
    table: LiteralString

    def select(self, *columns: LiteralString) -> str:
        cols = ", ".join(columns) if columns else "*"
        return f"SELECT {cols} FROM {self.table}"


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # StrEnum
    order = Order("ORD-001", "Alice", items=["book", "pen"])
    confirmed = order.confirm()
    shipped = confirmed.ship()
    print(order.status)          # pending  ← StrEnum is a str
    print(shipped.status)        # shipped
    print(f"active: {order.is_active()}")  # True

    # tomllib
    config = AppConfig.from_toml(SAMPLE_TOML)
    print(config.database)  # DatabaseConfig(host='localhost', port=5432, ...)
    print(config.cache)     # CacheConfig(host='localhost', port=6379, ttl=300)

    # ExceptionGroup
    bad_form = FormData("ab", "not-an-email", 200)
    try:
        bad_form.validate()
    except ExceptionGroup as eg:
        print(f"\n{eg.message}: {len(eg.exceptions)} errors")
        for exc in eg.exceptions:
            print(f"  • {exc}")

    # LiteralString
    qb = QueryBuilder("users")
    print(qb.select("id", "name", "email"))
    # SELECT id, name, email FROM users
