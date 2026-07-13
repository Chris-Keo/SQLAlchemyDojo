"""
Module 05 — Lesson 2: Advanced Pydantic Patterns
=================================================
Python 3.11 · requires: pydantic>=2.7

Topics:
  • Recursive / self-referential models
  • Generic Pydantic models
  • Custom types with __get_validators__
  • Model inheritance and abstract base models
  • Combining Pydantic (API layer) with dataclasses (domain layer)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Generic, TypeVar
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator, model_serializer
from pydantic.generics import GenericModel  # type: ignore[import]


# ---------------------------------------------------------------------------
# 1. Recursive model — tree / nested categories
# ---------------------------------------------------------------------------
class Category(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4())[:8])
    name: str
    children: list[Category] = []      # self-referential

    def depth(self) -> int:
        if not self.children:
            return 0
        return 1 + max(c.depth() for c in self.children)

    def flatten(self) -> list[Category]:
        result = [self]
        for child in self.children:
            result.extend(child.flatten())
        return result

Category.model_rebuild()  # required for self-referential models


# ---------------------------------------------------------------------------
# 2. Generic Pydantic model — typed API response envelope
# ---------------------------------------------------------------------------
T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """A typed response envelope used across all API endpoints."""
    success: bool = True
    data: T | None = None
    error: str | None = None
    meta: dict[str, object] = {}

    @classmethod
    def ok(cls, data: T, **meta: object) -> APIResponse[T]:
        return cls(success=True, data=data, meta=dict(meta))

    @classmethod
    def fail(cls, error: str) -> APIResponse[T]:
        return cls(success=False, error=error)


# ---------------------------------------------------------------------------
# 3. Layered architecture: Pydantic ↔ dataclass
# ---------------------------------------------------------------------------
# API layer (Pydantic) — validates and parses external input
class CreateUserRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: str = Field(pattern=r"^[^@]+@[^@]+\.[^@]+$")
    role: str = "user"

    @field_validator("role")
    @classmethod
    def valid_role(cls, v: str) -> str:
        allowed = {"user", "admin", "moderator"}
        if v not in allowed:
            raise ValueError(f"role must be one of {allowed}")
        return v


class UpdateUserRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2)
    email: str | None = None
    role: str | None = None


# Domain layer (dataclass) — internal representation, no serialisation overhead
@dataclass
class User:
    name: str
    email: str
    role: str
    id: str = field(default_factory=lambda: str(uuid4())[:8])

    @classmethod
    def from_request(cls, req: CreateUserRequest) -> User:
        return cls(name=req.name, email=req.email, role=req.role)

    def apply_update(self, req: UpdateUserRequest) -> None:
        if req.name is not None:
            self.name = req.name
        if req.email is not None:
            self.email = req.email
        if req.role is not None:
            self.role = req.role


# Read model (Pydantic) — serialises domain objects for API responses
class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str

    @classmethod
    def from_domain(cls, user: User) -> UserResponse:
        return cls(id=user.id, name=user.name, email=user.email, role=user.role)


# ---------------------------------------------------------------------------
# 4. Value object as Annotated type (reusable across many models)
# ---------------------------------------------------------------------------
from typing import Annotated
from pydantic.functional_validators import AfterValidator


def _validate_semver(v: str) -> str:
    parts = v.split(".")
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        raise ValueError(f"Invalid semver: {v!r}. Expected MAJOR.MINOR.PATCH")
    return v


SemVer = Annotated[str, AfterValidator(_validate_semver)]


class Package(BaseModel):
    name: str
    version: SemVer
    min_python: SemVer = "3.11.0"


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Recursive model
    tree = Category(name="Electronics", children=[
        Category(name="Computers", children=[
            Category(name="Laptops"),
            Category(name="Desktops"),
        ]),
        Category(name="Phones"),
    ])
    print(f"Tree depth: {tree.depth()}")
    all_cats = tree.flatten()
    print(f"All categories: {[c.name for c in all_cats]}")

    # Generic APIResponse
    pkg = Package(name="mylib", version="1.2.3")
    resp: APIResponse[Package] = APIResponse.ok(pkg, total=1)
    print("\nAPI Response:", resp.model_dump_json(indent=2))

    fail_resp: APIResponse[Package] = APIResponse.fail("Package not found")
    print("Fail:", fail_resp.model_dump())

    # Layered architecture
    req = CreateUserRequest(name="Alice", email="alice@example.com", role="admin")
    user = User.from_request(req)
    print(f"\nDomain User: {user}")

    update = UpdateUserRequest(name="Alicia")
    user.apply_update(update)
    print(f"After update: {user.name}")

    read_model = UserResponse.from_domain(user)
    print("API response:", read_model.model_dump_json())

    # SemVer type
    p = Package(name="dash-course", version="2.0.1")
    print(f"\n{p.name} v{p.version} (min Python {p.min_python})")

    from pydantic import ValidationError
    try:
        Package(name="bad", version="2.0")
    except ValidationError as e:
        print("SemVer error:", e.errors()[0]["msg"])
