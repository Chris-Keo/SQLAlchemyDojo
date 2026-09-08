# Module 02 — Dataclasses Deep-Dive

## Learning Objectives

1. Generate `__init__`, `__repr__`, `__eq__` automatically with `@dataclass`.
2. Use `field()` for default factories, metadata, and comparison control.
3. Leverage Python 3.11 features: `slots=True`, `KW_ONLY`, `__post_init__`.
4. Know when to freeze a dataclass (immutable value objects).
5. Understand the performance difference vs plain classes.

---

## Lessons

| File | Topic |
|------|-------|
| `01_intro_dataclasses.py` | Basic `@dataclass` usage |
| `02_advanced_dataclasses.py` | `field()`, `__post_init__`, `KW_ONLY`, `slots=True` |
| `03_python311_features.py` | `StrEnum`, `Self`, frozen + slots |
| `app.py` | Interactive Dash explorer |

---

## When to Use `@dataclass`

> **Use `@dataclass` whenever your class is primarily a data container and you
> would otherwise write `__init__`, `__repr__`, and `__eq__` by hand.**

- ✅ Configuration objects
- ✅ Data-transfer objects (DTOs)  
- ✅ Named tuples with mutable fields  
- ✅ Simple domain value objects  
- ❌ When you need runtime data **validation** → use Pydantic instead  
- ❌ When you need **serialisation / JSON schemas** → use Pydantic instead
