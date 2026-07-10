# Module 01 — Python Classes Fundamentals

## Learning Objectives

By the end of this module you will be able to:

1. Explain when a plain class is the right tool (and when it is not).
2. Implement `__repr__`, `__eq__`, `__hash__`, and `__slots__` correctly.
3. Distinguish *value objects* from *entity objects*.
4. Recognise the boilerplate that dataclasses and Pydantic eliminate.

---

## Lessons

| File | Topic |
|------|-------|
| `01_plain_classes.py` | Anatomy of a Python class |
| `02_value_vs_entity.py` | Value objects vs entity objects |
| `app.py` | Interactive Dash explorer |

---

## Key Rule

> **Use a plain class when you need behaviour (methods) more than data storage,
> and when you do NOT need automatic validation or serialisation.**

Classic examples: service objects, repositories, strategy pattern implementations.
