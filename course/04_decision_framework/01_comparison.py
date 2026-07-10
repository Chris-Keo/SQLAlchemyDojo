"""
Module 04 — Decision Framework: When to Use What
================================================
Python 3.11 · requires: pydantic>=2.7

This module demonstrates the same real-world scenario implemented three ways
so you can feel the trade-offs before reaching for one tool over another.

Scenario: An e-commerce order pipeline that must:
  1. Accept an HTTP request body (external/untrusted input)
  2. Pass data through internal processing steps
  3. Store a lightweight snapshot for analytics
"""
from __future__ import annotations

import json
import sys
import timeit
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, EmailStr, Field, NonNegativeFloat, PositiveInt


# ===========================================================================
# SCENARIO: e-commerce order
# ===========================================================================


# ---------------------------------------------------------------------------
# APPROACH A: Plain class — every dunder by hand
# ---------------------------------------------------------------------------
class OrderItemPlain:
    def __init__(self, product_id: str, quantity: int, unit_price: float) -> None:
        self.product_id = product_id
        self.quantity = quantity
        self.unit_price = unit_price

    @property
    def total(self) -> float:
        return self.quantity * self.unit_price

    def __repr__(self) -> str:
        return (
            f"OrderItemPlain(product_id={self.product_id!r}, "
            f"quantity={self.quantity!r}, unit_price={self.unit_price!r})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, OrderItemPlain):
            return NotImplemented
        return (self.product_id, self.quantity, self.unit_price) == (
            other.product_id, other.quantity, other.unit_price
        )


class OrderPlain:
    def __init__(self, customer_email: str, items: list[OrderItemPlain]) -> None:
        self.id = str(uuid4())
        self.customer_email = customer_email
        self.items = items
        self.created_at = datetime.utcnow()

    @property
    def total(self) -> float:
        return sum(i.total for i in self.items)

    def __repr__(self) -> str:
        return f"OrderPlain(id={self.id[:8]}…, total={self.total:.2f})"


# ---------------------------------------------------------------------------
# APPROACH B: @dataclass — auto-generates init/repr/eq, no validation
# ---------------------------------------------------------------------------
class OrderStatus(StrEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"


@dataclass(slots=True)
class OrderItemDC:
    product_id: str
    quantity: int
    unit_price: float

    @property
    def total(self) -> float:
        return self.quantity * self.unit_price


@dataclass
class OrderDC:
    customer_email: str
    items: list[OrderItemDC]
    id: str = field(default_factory=lambda: str(uuid4()))
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def total(self) -> float:
        return sum(i.total for i in self.items)

    def confirm(self) -> None:
        self.status = OrderStatus.CONFIRMED


# ---------------------------------------------------------------------------
# APPROACH C: Pydantic — validation + serialisation, ideal for API layer
# ---------------------------------------------------------------------------
class OrderItemPydantic(BaseModel):
    product_id: str = Field(min_length=1)
    quantity: PositiveInt
    unit_price: NonNegativeFloat

    @property
    def total(self) -> float:
        return self.quantity * self.unit_price


class OrderPydantic(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    customer_email: EmailStr
    items: list[OrderItemPydantic] = Field(min_length=1)
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def total(self) -> float:
        return sum(i.total for i in self.items)

    def to_dataclass(self) -> OrderDC:
        """Convert to internal dataclass after validation."""
        return OrderDC(
            id=self.id,
            customer_email=self.customer_email,
            items=[
                OrderItemDC(i.product_id, i.quantity, i.unit_price)
                for i in self.items
            ],
        )


# ---------------------------------------------------------------------------
# Performance comparison
# ---------------------------------------------------------------------------
def benchmark(n: int = 100_000) -> dict[str, float]:
    item_data = {"product_id": "SKU-001", "quantity": 2, "unit_price": 9.99}

    t_plain = timeit.timeit(
        "OrderItemPlain(**d)",
        globals={"OrderItemPlain": OrderItemPlain, "d": item_data},
        number=n,
    )
    t_dc = timeit.timeit(
        "OrderItemDC(**d)",
        globals={"OrderItemDC": OrderItemDC, "d": item_data},
        number=n,
    )
    t_py = timeit.timeit(
        "OrderItemPydantic(**d)",
        globals={"OrderItemPydantic": OrderItemPydantic, "d": item_data},
        number=n,
    )
    return {"plain": t_plain, "dataclass": t_dc, "pydantic": t_py, "n": n}


# ---------------------------------------------------------------------------
# Real-world pattern: request → validated → internal → analytics snapshot
# ---------------------------------------------------------------------------
def process_order_request(raw_json: str) -> dict[str, Any]:
    """
    Typical FastAPI / Dash pipeline:
    1. Parse + validate external JSON  →  Pydantic
    2. Process with internal logic     →  dataclass
    3. Store lightweight snapshot      →  frozen dataclass
    """
    # Step 1: Validate (Pydantic)
    data = json.loads(raw_json)
    order_in = OrderPydantic(**data)

    # Step 2: Internal processing (dataclass)
    order_dc = order_in.to_dataclass()
    order_dc.confirm()

    # Step 3: Analytics snapshot (frozen dataclass)
    @dataclass(frozen=True, slots=True)
    class Snapshot:
        order_id: str
        total: float
        item_count: int
        confirmed_at: str

    snap = Snapshot(
        order_id=order_dc.id,
        total=order_dc.total,
        item_count=len(order_dc.items),
        confirmed_at=datetime.utcnow().isoformat(),
    )

    return {
        "validated_order": order_in.model_dump(mode="json"),
        "internal_status": order_dc.status,
        "snapshot": asdict(snap),
    }


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    raw = json.dumps({
        "customer_email": "alice@example.com",
        "items": [
            {"product_id": "BOOK-001", "quantity": 2, "unit_price": 12.99},
            {"product_id": "PEN-007", "quantity": 5, "unit_price": 1.49},
        ],
    })

    result = process_order_request(raw)
    print("=== Pipeline Result ===")
    print(json.dumps(result, indent=2, default=str))

    print("\n=== Performance Benchmark ===")
    times = benchmark(100_000)
    fastest = min(times["plain"], times["dataclass"], times["pydantic"])
    for name, t in [("Plain class", times["plain"]), ("@dataclass", times["dataclass"]), ("Pydantic v2", times["pydantic"])]:
        print(f"  {name:15s}: {t:.3f}s  ({t/fastest:.1f}×)")
