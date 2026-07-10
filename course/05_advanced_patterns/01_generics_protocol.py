"""
Module 05 — Lesson 1: Generics and Protocol
============================================
Python 3.11 · stdlib only (no pydantic)

Topics:
  • Generic dataclasses with TypeVar
  • Protocol for structural subtyping
  • Dataclass mixins
  • Repository pattern with generics
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Generic, Iterator, Protocol, TypeVar, runtime_checkable
from uuid import uuid4


# ---------------------------------------------------------------------------
# 1. Generic dataclass — typed container
# ---------------------------------------------------------------------------
T = TypeVar("T")


@dataclass
class Page(Generic[T]):
    """A paginated result — strongly typed."""
    items: list[T]
    total: int
    page: int = 1
    page_size: int = 20

    @property
    def total_pages(self) -> int:
        return max(1, -(-self.total // self.page_size))  # ceil division

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    def __iter__(self) -> Iterator[T]:
        return iter(self.items)


@dataclass
class Result(Generic[T]):
    """Either a value or an error — railway-oriented programming."""
    _value: T | None = None
    _error: str | None = None

    @classmethod
    def ok(cls, value: T) -> Result[T]:
        return cls(_value=value)

    @classmethod
    def err(cls, message: str) -> Result[T]:
        return cls(_error=message)

    @property
    def is_ok(self) -> bool:
        return self._error is None

    @property
    def value(self) -> T:
        if self._error:
            raise ValueError(f"Result is an error: {self._error}")
        return self._value  # type: ignore[return-value]

    @property
    def error(self) -> str:
        return self._error or ""

    def __repr__(self) -> str:
        if self.is_ok:
            return f"Result.ok({self._value!r})"
        return f"Result.err({self._error!r})"


# ---------------------------------------------------------------------------
# 2. Protocol — structural subtyping (duck typing with type safety)
# ---------------------------------------------------------------------------
@runtime_checkable
class Identifiable(Protocol):
    """Anything with an 'id' attribute is Identifiable."""
    id: str


@runtime_checkable
class Serialisable(Protocol):
    """Anything that can dump itself to a dict."""
    def to_dict(self) -> dict[str, object]: ...


# ---------------------------------------------------------------------------
# 3. Generic Repository pattern
# ---------------------------------------------------------------------------
ID = TypeVar("ID")
Entity = TypeVar("Entity", bound=Identifiable)


class InMemoryRepository(Generic[Entity]):
    """
    A generic in-memory store that works with ANY dataclass or class
    that satisfies the Identifiable protocol.
    """

    def __init__(self) -> None:
        self._store: dict[str, Entity] = {}

    def save(self, entity: Entity) -> Entity:
        self._store[entity.id] = entity
        return entity

    def get(self, entity_id: str) -> Result[Entity]:
        if entity_id not in self._store:
            return Result.err(f"Not found: {entity_id!r}")
        return Result.ok(self._store[entity_id])

    def all(self) -> list[Entity]:
        return list(self._store.values())

    def delete(self, entity_id: str) -> bool:
        return self._store.pop(entity_id, None) is not None

    def count(self) -> int:
        return len(self._store)


# ---------------------------------------------------------------------------
# 4. Dataclass entities that work with the generic repository
# ---------------------------------------------------------------------------
@dataclass
class User:
    name: str
    email: str
    id: str = field(default_factory=lambda: str(uuid4())[:8])

    def to_dict(self) -> dict[str, object]:
        return {"id": self.id, "name": self.name, "email": self.email}


@dataclass
class Product:
    sku: str
    name: str
    price: float
    id: str = field(default_factory=lambda: str(uuid4())[:8])

    def to_dict(self) -> dict[str, object]:
        return {"id": self.id, "sku": self.sku, "name": self.name, "price": self.price}


# ---------------------------------------------------------------------------
# 5. Mixin pattern with dataclasses
# ---------------------------------------------------------------------------
@dataclass
class TimestampMixin:
    """Add created_at / updated_at to any dataclass via inheritance."""
    from datetime import datetime
    created_at: datetime = field(default_factory=lambda: __import__("datetime").datetime.utcnow())
    updated_at: datetime = field(default_factory=lambda: __import__("datetime").datetime.utcnow())


@dataclass
class AuditMixin:
    created_by: str = "system"
    updated_by: str = "system"


@dataclass
class AuditedProduct(AuditMixin, Product):
    """Product with audit trail — multiple inheritance via dataclass mixins."""


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Generic Page
    users_raw = [User(f"User{i}", f"u{i}@example.com") for i in range(55)]
    page = Page(items=users_raw[:20], total=55)
    print(f"Page {page.page}/{page.total_pages}, has_next={page.has_next}")
    print(f"Items on page: {len(list(page))}")

    # Result monad
    r_ok: Result[int] = Result.ok(42)
    r_err: Result[int] = Result.err("not found")
    print(r_ok, r_ok.value)
    print(r_err, r_err.error)

    # Generic repository
    repo: InMemoryRepository[User] = InMemoryRepository()
    u1 = repo.save(User("Alice", "alice@example.com"))
    u2 = repo.save(User("Bob", "bob@example.com"))
    print(f"\nRepo count: {repo.count()}")

    result = repo.get(u1.id)
    print(f"Found: {result.value}")

    missing = repo.get("nonexistent")
    print(f"Missing: {missing}")

    # Protocol check
    print(f"\nUser is Identifiable: {isinstance(u1, Identifiable)}")
    print(f"User is Serialisable: {isinstance(u1, Serialisable)}")

    # Product repo
    prod_repo: InMemoryRepository[Product] = InMemoryRepository()
    prod_repo.save(Product("SKU-001", "Widget", 9.99))
    print(f"Products: {prod_repo.count()}")
