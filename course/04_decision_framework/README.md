# Module 04 — Decision Framework: When to Use What

## Learning Objectives

1. Apply a repeatable decision tree to any Python data modelling problem.
2. Understand the trade-offs between plain classes, dataclasses, and Pydantic.
3. Know which patterns come from real-world code (FastAPI, SQLAlchemy, Click).

---

## The Decision Tree

```
Do you need automatic validation of input from an untrusted source?
│
├─ YES → Use Pydantic BaseModel
│         (API bodies, CLI args, config from .env, JSON parsing)
│
└─ NO  → Is this primarily a data container?
          │
          ├─ YES → Use @dataclass
          │         • Immutable value object?  →  frozen=True, slots=True
          │         • High-volume (millions)?  →  slots=True
          │         • Config / DTO?            →  plain @dataclass
          │
          └─ NO  → Is this primarily about behaviour / methods?
                    │
                    ├─ YES → Use a plain class
                    │         • Service object, repository, strategy pattern
                    │
                    └─ MAYBE → Consider NamedTuple for simple read-only records
```

---

## Quick Reference

| Criterion | Plain class | @dataclass | Pydantic |
|-----------|-------------|------------|---------|
| `__init__` auto | ❌ | ✅ | ✅ |
| `__repr__` auto | ❌ | ✅ | ✅ |
| `__eq__` auto | ❌ | ✅ | ✅ |
| Runtime validation | ❌ | ❌ | ✅ |
| JSON / dict serialisation | manual | `asdict()` | `model_dump()` |
| JSON Schema | ❌ | ❌ | ✅ |
| Env var loading | ❌ | ❌ | ✅ (BaseSettings) |
| Memory (slots) | manual | `slots=True` | ❌ |
| Speed (construction) | fastest | fast | slower (Rust core) |
| Inheritance | ✅ | ✅ (tricky) | ✅ |
