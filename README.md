# SQLAlchemyDojo

A hands-on SQL and Python backend learning repository using a realistic banking dataset.

## Curricula

| Curriculum | Description |
|------------|-------------|
| [`curriculum/`](curriculum/README.md) | PostgreSQL master's curriculum — raw SQL, window functions, CTEs, indexing, analytics |
| [`python_curriculum/`](python_curriculum/README.md) | Python backend curriculum — SQLAlchemy ORM, FastAPI REST API, Redis Pub/Sub |
| [`course/`](course/README.md) | Python 3.11 classes, dataclasses, and Pydantic course with runnable Dash apps |

---

## Quick Start

1. Set up PostgreSQL and load the banking schema:
   ```bash
   psql -U postgres -c "CREATE DATABASE firstnational_db;"
   psql -U postgres -d firstnational_db -f curriculum/schema/01_create_tables.sql
   psql -U postgres -d firstnational_db -f curriculum/schema/02_seed_data.sql
   ```

2. For the SQL curriculum → open any `.sql` file in `curriculum/` with pgAdmin or psql.

3. For the Python backend curriculum:
   ```bash
   pip install sqlalchemy psycopg2-binary fastapi uvicorn[standard] redis pydantic python-dotenv
   cd python_curriculum
   python module_01_python_sqlalchemy/01_setup_and_models.py
   ```

4. For the Python classes course:
   ```bash
   python3.11 -m venv .venv && source .venv/bin/activate
   pip install -r course/requirements.txt
   python course/06_capstone/app.py
   ```
