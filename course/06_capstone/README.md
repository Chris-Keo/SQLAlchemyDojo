# Module 06 — Capstone: Sales Dashboard

## Overview

A complete, production-style Plotly Dash 2.17 application that combines
**all three approaches** in the same codebase:

| Layer | Tool | Why |
|-------|------|-----|
| HTTP input validation | Pydantic BaseModel | Untrusted external data |
| App config (env vars) | Pydantic BaseSettings | Type-safe configuration |
| Domain objects | `@dataclass` | Fast internal processing |
| Value objects | `@dataclass(frozen=True, slots=True)` | Immutable, hashable, cheap |
| Analytics snapshots | `@dataclass(frozen=True, slots=True)` | Write-once records |
| Dash callbacks | Plain functions | No state needed |

## Running

```bash
python course/06_capstone/app.py
# Open http://127.0.0.1:8050
```

## Features

- Interactive sales data dashboard with Plotly charts
- Live "Add Sale" form with Pydantic validation
- Category filter, date range picker, KPI cards
- In-memory dataclass repository backing all data
- Real-time validation error display
