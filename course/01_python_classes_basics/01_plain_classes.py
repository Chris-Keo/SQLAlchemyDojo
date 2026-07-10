"""
Module 01 — Lesson 1: Anatomy of a Python Class
================================================
Python 3.11 · No external dependencies

This lesson walks through every dunder method and class feature you need
to build solid plain classes — and shows exactly where the boilerplate is
so you can appreciate dataclasses and Pydantic later.
"""
from __future__ import annotations

from typing import Self


# ---------------------------------------------------------------------------
# 1. The Minimal Class
# ---------------------------------------------------------------------------
class Point:
    """A 2-D point — the simplest useful class."""

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    # Without __repr__ Python shows <__main__.Point object at 0x...>
    def __repr__(self) -> str:
        return f"Point(x={self.x!r}, y={self.y!r})"

    # Without __eq__ Python uses identity (is), not value equality
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    # If you define __eq__ you MUST define __hash__ to use the object in sets/dicts
    def __hash__(self) -> int:
        return hash((self.x, self.y))

    # Fluent / builder pattern using Python 3.11 Self
    def translate(self, dx: float, dy: float) -> Self:
        return Point(self.x + dx, self.y + dy)

    def distance_to(self, other: Self) -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


# ---------------------------------------------------------------------------
# 2. __slots__ — memory and speed
# ---------------------------------------------------------------------------
class PointSlotted:
    """
    __slots__ prevents arbitrary attribute assignment and reduces memory by
    ~40-60 % vs a plain class (no per-instance __dict__).

    Use when you create millions of small objects.
    """

    __slots__ = ("x", "y")

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f"PointSlotted(x={self.x!r}, y={self.y!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PointSlotted):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __hash__(self) -> int:
        return hash((self.x, self.y))


# ---------------------------------------------------------------------------
# 3. Class Variables vs Instance Variables
# ---------------------------------------------------------------------------
class Counter:
    """Demonstrates class-level state (shared across instances)."""

    _count: int = 0  # class variable — shared

    def __init__(self, name: str) -> None:
        self.name = name          # instance variable — per-object
        Counter._count += 1

    @classmethod
    def total(cls) -> int:
        return cls._count

    @staticmethod
    def validate_name(name: str) -> bool:
        return bool(name.strip())

    def __repr__(self) -> str:
        return f"Counter(name={self.name!r})"


# ---------------------------------------------------------------------------
# 4. Properties — controlled attribute access
# ---------------------------------------------------------------------------
class Temperature:
    """Shows how @property replaces getter/setter patterns."""

    def __init__(self, celsius: float) -> None:
        self._celsius = celsius  # convention: _ = "private"

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        if value < -273.15:
            raise ValueError(f"Temperature {value}°C is below absolute zero.")
        self._celsius = value

    @property
    def fahrenheit(self) -> float:
        return self._celsius * 9 / 5 + 32

    def __repr__(self) -> str:
        return f"Temperature({self._celsius}°C / {self.fahrenheit:.2f}°F)"


# ---------------------------------------------------------------------------
# 5. Inheritance and the MRO
# ---------------------------------------------------------------------------
class Animal:
    def __init__(self, name: str) -> None:
        self.name = name

    def speak(self) -> str:
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"{type(self).__name__}(name={self.name!r})"


class Dog(Animal):
    def speak(self) -> str:
        return f"{self.name} says: Woof!"


class Cat(Animal):
    def speak(self) -> str:
        return f"{self.name} says: Meow!"


# ---------------------------------------------------------------------------
# 6. When NOT to use a plain class
# ---------------------------------------------------------------------------
# BAD — pure data bag with no behaviour; boilerplate-heavy
class UserBad:
    def __init__(self, name: str, age: int, email: str) -> None:
        self.name = name
        self.age = age
        self.email = email

    def __repr__(self) -> str:
        return f"User(name={self.name!r}, age={self.age!r}, email={self.email!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UserBad):
            return NotImplemented
        return (self.name, self.age, self.email) == (other.name, other.age, other.email)

    def __hash__(self) -> int:
        return hash((self.name, self.age, self.email))


# ↑ All that boilerplate is exactly what @dataclass generates automatically.


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    p1 = Point(1.0, 2.0)
    p2 = Point(4.0, 6.0)
    print(p1)                         # Point(x=1.0, y=2.0)
    print(p1 == Point(1.0, 2.0))      # True
    print(p1.distance_to(p2))         # 5.0
    print(p1.translate(1, 1))         # Point(x=2.0, y=3.0)

    t = Temperature(100)
    print(t)                          # Temperature(100°C / 212.00°F)
    t.celsius = 0
    print(t)                          # Temperature(0°C / 32.00°F)

    c1 = Counter("alpha")
    c2 = Counter("beta")
    print(Counter.total())            # 2
