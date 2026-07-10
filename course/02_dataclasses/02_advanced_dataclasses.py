"""
Module 02 — Lesson 2: Advanced Dataclasses
==========================================
Python 3.11 · stdlib only

Covers:
  • KW_ONLY sentinel (Python 3.10+)
  • slots=True (Python 3.10+) — same zero-overhead as manual __slots__
  • Inheritance with dataclasses
  • dataclass_transform for IDE-aware factories
  • Performance benchmarks
"""
from __future__ import annotations

import sys
import timeit
from dataclasses import KW_ONLY, dataclass, field


# ---------------------------------------------------------------------------
# 1. KW_ONLY — force keyword-only arguments after the sentinel
# ---------------------------------------------------------------------------
@dataclass
class APIRequest:
    """
    KW_ONLY makes everything after it keyword-only in __init__.
    Prevents positional mistakes like APIRequest("POST", "token", "/api", 30)
    where you mix up order.
    """
    method: str
    path: str
    _: KW_ONLY            # sentinel — everything below is keyword-only
    timeout: float = 30.0
    retries: int = 3
    auth_token: str = ""


# ---------------------------------------------------------------------------
# 2. slots=True — zero-overhead, no boilerplate
# ---------------------------------------------------------------------------
@dataclass(slots=True)
class SensorReading:
    """
    slots=True is equivalent to manually writing __slots__ = (...)
    but the decorator does it for you.  Use when instantiating millions
    of objects (IoT data, graph nodes, ML feature rows).
    """
    sensor_id: str
    value: float
    timestamp: float


@dataclass
class SensorReadingNoSlots:
    sensor_id: str
    value: float
    timestamp: float


# ---------------------------------------------------------------------------
# 3. Frozen + Slots — the ultimate value object
# ---------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class Colour:
    """Immutable, hashable, memory-efficient colour record."""
    r: int
    g: int
    b: int
    a: int = 255

    def __post_init__(self) -> None:
        for name, val in (("r", self.r), ("g", self.g), ("b", self.b), ("a", self.a)):
            if not 0 <= val <= 255:
                raise ValueError(f"Channel {name}={val} must be 0-255.")

    def to_hex(self) -> str:
        return f"#{self.r:02X}{self.g:02X}{self.b:02X}"

    def blend(self, other: Colour, t: float = 0.5) -> Colour:
        """Linear interpolation between two colours."""
        def lerp(a: int, b: int) -> int:
            return round(a + (b - a) * t)
        return Colour(lerp(self.r, other.r), lerp(self.g, other.g), lerp(self.b, other.b))


# ---------------------------------------------------------------------------
# 4. Dataclass Inheritance
# ---------------------------------------------------------------------------
@dataclass
class Animal:
    name: str
    species: str

    def describe(self) -> str:
        return f"{self.name} ({self.species})"


@dataclass
class Dog(Animal):
    breed: str
    trained: bool = False

    # Child adds fields AFTER parent fields
    def describe(self) -> str:
        trained_str = "trained" if self.trained else "untrained"
        return f"{super().describe()} — {self.breed}, {trained_str}"


@dataclass
class GuideDog(Dog):
    _: KW_ONLY
    handler: str = ""

    def describe(self) -> str:
        base = super().describe()
        return f"{base}  [handler: {self.handler or 'unassigned'}]"


# ---------------------------------------------------------------------------
# 5. Performance benchmark: slots vs no-slots
# ---------------------------------------------------------------------------
def bench() -> dict[str, float]:
    n = 500_000
    t_slots = timeit.timeit(
        "SensorReading('s1', 3.14, 0.0)",
        globals={"SensorReading": SensorReading},
        number=n,
    )
    t_no_slots = timeit.timeit(
        "SensorReadingNoSlots('s1', 3.14, 0.0)",
        globals={"SensorReadingNoSlots": SensorReadingNoSlots},
        number=n,
    )
    return {"slots": t_slots, "no_slots": t_no_slots, "n": n}


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # KW_ONLY
    req = APIRequest("GET", "/health", timeout=5.0, retries=1)
    print(req)
    # APIRequest(method='GET', path='/health', timeout=5.0, retries=1, auth_token='')

    # Frozen + slots
    red = Colour(255, 0, 0)
    blue = Colour(0, 0, 255)
    purple = red.blend(blue)
    print(red.to_hex())    # #FF0000
    print(purple)          # Colour(r=128, g=0, b=128, a=255)
    print(hash(red))       # deterministic (frozen)

    # Inheritance
    dog = GuideDog("Rex", "Canis lupus", "Labrador", trained=True, handler="Alice")
    print(dog.describe())

    # Memory
    s_with = SensorReading("x", 1.0, 0.0)
    s_without = SensorReadingNoSlots("x", 1.0, 0.0)
    print(f"slots size    : {sys.getsizeof(s_with)} bytes")
    print(f"no-slots size : {sys.getsizeof(s_without) + sys.getsizeof(s_without.__dict__)} bytes")

    # Benchmark
    results = bench()
    speedup = results["no_slots"] / results["slots"]
    print(f"\nslots creation  : {results['slots']:.3f}s")
    print(f"no-slots creation: {results['no_slots']:.3f}s")
    print(f"slots is {speedup:.2f}x faster over {results['n']:,} instances")
