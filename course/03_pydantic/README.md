# Module 03 — Pydantic v2 Models

## Learning Objectives

1. Define models with automatic validation using `BaseModel`.
2. Write custom field validators with `@field_validator` and `@model_validator`.
3. Control serialisation with `model_dump()`, `model_dump_json()`, `model_json_schema()`.
4. Load typed settings from environment variables with `BaseSettings`.
5. Know exactly when Pydantic adds value vs when it's overkill.

---

## Lessons

| File | Topic |
|------|-------|
| `01_intro_pydantic.py` | BaseModel basics, type coercion, Field() |
| `02_validators.py` | @field_validator, @model_validator, custom types |
| `03_settings.py` | BaseSettings, .env files, secret management |
| `app.py` | Interactive Dash explorer |

---

## When to Use Pydantic

> **Use Pydantic when data arrives from an untrusted or external source and
> must be validated before use.**

| Scenario | Use Pydantic? |
|----------|--------------|
| HTTP request body (FastAPI) | ✅ Yes |
| CLI argument parsing | ✅ Yes |
| Config from env / .env file | ✅ Yes (BaseSettings) |
| JSON API response parsing | ✅ Yes |
| Internal function parameter | ❌ No — use type hints + mypy |
| Pure computation helper | ❌ No — use @dataclass |
| DB ORM row object | ❌ Probably not — use SQLAlchemy |
