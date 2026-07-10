# SQLAlchemyDojo

A hands-on SQL and Python backend learning repository using a realistic banking dataset.

## Curricula

| Curriculum | Description |
|------------|-------------|
| [`curriculum/`](curriculum/README.md) | PostgreSQL master's curriculum — raw SQL, window functions, CTEs, indexing, analytics |
| [`python_curriculum/`](python_curriculum/README.md) | Python backend curriculum — SQLAlchemy ORM, FastAPI REST API, Redis Pub/Sub |

---

## Quick Start

1. Set up PostgreSQL and load the banking schema:
   ```bash
   psql -U postgres -c "CREATE DATABASE firstnational_db;"
   psql -U postgres -d firstnational_db -f curriculum/schema/01_create_tables.sql
   psql -U postgres -d firstnational_db -f curriculum/schema/02_seed_data.sql
   ```

2. For the SQL curriculum → open any `.sql` file in `curriculum/` with pgAdmin or psql.

3. For the Python curriculum:
   ```bash
   pip install sqlalchemy psycopg2-binary fastapi uvicorn[standard] redis pydantic python-dotenv
   cd python_curriculum
   python module_01_python_sqlalchemy/01_setup_and_models.py
   ```
