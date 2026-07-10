# Python 3.11 Classes, Dataclasses & Pydantic — Interactive Course

> **Runtime:** Python 3.11 · **UI:** Plotly Dash 2.17+ · **Validation:** Pydantic v2

This course teaches you *when and where* to reach for plain classes, `dataclasses`,
or Pydantic models. Every module includes runnable Python lessons **and** a Plotly Dash
application that lets you explore the concepts interactively in your browser.

---

## Prerequisites

```bash
python3.11 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## Course Map

| Module | Topic | Key Concepts |
|--------|-------|--------------|
| [01](./01_python_classes_basics/) | Python Classes Fundamentals | OOP basics, `__slots__`, `__repr__`, `__eq__` |
| [02](./02_dataclasses/) | Dataclasses Deep-Dive | `@dataclass`, fields, `__post_init__`, `KW_ONLY`, `slots=True` |
| [03](./03_pydantic/) | Pydantic v2 Models | Validation, custom validators, `model_config`, `BaseSettings` |
| [04](./04_decision_framework/) | When to Use What | Decision tree, performance comparison, real-world patterns |
| [05](./05_advanced_patterns/) | Advanced Patterns | Mixins, generics, discriminated unions, nested models |
| [06](./06_capstone/) | Capstone Dashboard | Full Dash app combining all three approaches end-to-end |

---

## Running a Module

Each module contains an `app.py`. Run it to open the interactive lesson in your browser:

```bash
python course/01_python_classes_basics/app.py
# Open http://127.0.0.1:8050
```

---

## Python 3.11 Features Covered

- `StrEnum` for type-safe enumerations
- `Self` return type annotation
- `tomllib` for config parsing
- `dataclasses(slots=True)` — zero-overhead frozen records
- Exception groups and `ExceptionGroup` handling
- Fine-grained error locations in tracebacks
- `typing.LiteralString` for safe SQL / shell strings
