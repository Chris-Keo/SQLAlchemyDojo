# =============================================================================
# MODULE 1: PYTHON + SQLALCHEMY ORM
# Lesson 2 – Basic Queries: SELECT, INSERT, UPDATE, DELETE
# =============================================================================
# Goal: Perform everyday database operations using the SQLAlchemy ORM.
#       Each section mirrors a concept from the SQL curriculum (Module 1).
# Prerequisite: Run 01_setup_and_models.py first to confirm connectivity.
# =============================================================================

from sqlalchemy import select, update, delete, func, and_, or_, not_
from sqlalchemy.orm import Session
from datetime import date

# Import models and session factory from Lesson 1
from module_01_python_sqlalchemy.setup_and_models import (  # type: ignore
    SessionLocal, Customer, Account, Transaction,
    Branch, Employee, Loan, AccountTypeEnum
)


# ─────────────────────────────────────────────
# Helper: always use a context manager for sessions
# ─────────────────────────────────────────────
# The `with SessionLocal() as session:` block automatically closes
# the session when the block exits (even on exception).

def get_session() -> Session:
    return SessionLocal()


# ─────────────────────────────────────────────
# 2.1  SELECT ALL ROWS
# ─────────────────────────────────────────────
# SQL equivalent:  SELECT * FROM customers;

def select_all_customers():
    with get_session() as session:
        # Modern SQLAlchemy 2.x style uses select() + session.execute()
        stmt = select(Customer)
        customers = session.execute(stmt).scalars().all()
        for c in customers:
            print(f"{c.customer_id}  {c.first_name} {c.last_name}  {c.email}")
        return customers


# ─────────────────────────────────────────────
# 2.2  SELECT SPECIFIC COLUMNS
# ─────────────────────────────────────────────
# SQL equivalent:
#   SELECT customer_id, first_name, last_name, email FROM customers;

def select_customer_names():
    with get_session() as session:
        stmt = select(
            Customer.customer_id,
            Customer.first_name,
            Customer.last_name,
            Customer.email
        )
        rows = session.execute(stmt).all()
        for row in rows:
            print(row)
        return rows


# ─────────────────────────────────────────────
# 2.3  FILTERING WITH WHERE
# ─────────────────────────────────────────────
# SQL equivalent:
#   SELECT first_name, last_name, city, state
#   FROM   customers
#   WHERE  state = 'NY';

def customers_in_state(state_code: str):
    with get_session() as session:
        stmt = (
            select(Customer.first_name, Customer.last_name, Customer.city, Customer.state)
            .where(Customer.state == state_code)
        )
        rows = session.execute(stmt).all()
        for row in rows:
            print(row)
        return rows


# ─────────────────────────────────────────────
# 2.4  AND / OR / NOT CONDITIONS
# ─────────────────────────────────────────────
# SQL equivalent:
#   SELECT account_id, account_type, balance
#   FROM   accounts
#   WHERE  account_type = 'checking'
#     AND  is_active = TRUE
#     AND  balance BETWEEN 5000 AND 25000;

def active_checking_accounts_in_range(low: float = 5000, high: float = 25000):
    with get_session() as session:
        stmt = (
            select(Account)
            .where(
                and_(
                    Account.account_type == AccountTypeEnum.checking,
                    Account.is_active == True,
                    Account.balance.between(low, high)
                )
            )
            .order_by(Account.balance.desc())
        )
        accounts = session.execute(stmt).scalars().all()
        for a in accounts:
            print(f"ID={a.account_id}  Type={a.account_type.value}  Balance={a.balance}")
        return accounts


# ─────────────────────────────────────────────
# 2.5  ORDER BY + LIMIT
# ─────────────────────────────────────────────
# SQL equivalent:
#   SELECT customer_id, first_name, last_name, credit_score
#   FROM   customers
#   ORDER BY credit_score DESC
#   LIMIT  10;

def top_credit_score_customers(limit: int = 10):
    with get_session() as session:
        stmt = (
            select(Customer)
            .order_by(Customer.credit_score.desc())
            .limit(limit)
        )
        customers = session.execute(stmt).scalars().all()
        for c in customers:
            # In production, avoid logging raw customer PII; this is for educational output only
            print(f"{c.first_name} {c.last_name}  Score={c.credit_score}")
        return customers


# ─────────────────────────────────────────────
# 2.6  LIKE (pattern matching)
# ─────────────────────────────────────────────
# SQL equivalent:
#   SELECT * FROM customers WHERE email LIKE '%@gmail.com';

def customers_with_gmail():
    with get_session() as session:
        stmt = select(Customer).where(Customer.email.like("%@gmail.com"))
        customers = session.execute(stmt).scalars().all()
        for c in customers:
            # Mask the email local-part in output to avoid logging raw PII
            domain = c.email.split("@")[-1] if "@" in c.email else c.email
            print(f"{c.first_name} {c.last_name}  ***@{domain}")
        return customers


# ─────────────────────────────────────────────
# 2.7  IS NULL / IS NOT NULL
# ─────────────────────────────────────────────
# SQL equivalent:
#   SELECT employee_id, first_name, last_name FROM employees
#   WHERE  manager_id IS NULL;

def employees_without_manager():
    with get_session() as session:
        stmt = (
            select(Employee)
            .where(Employee.manager_id.is_(None))
            .order_by(Employee.last_name)
        )
        employees = session.execute(stmt).scalars().all()
        for e in employees:
            print(f"ID={e.employee_id}  {e.first_name} {e.last_name}  {e.job_title}")
        return employees


# ─────────────────────────────────────────────
# 2.8  INSERT — Add a new customer
# ─────────────────────────────────────────────
# SQL equivalent:
#   INSERT INTO customers (first_name, last_name, email, ...)
#   VALUES ('Jane', 'Doe', 'jane@example.com', ...);

def insert_customer(
    first_name: str,
    last_name: str,
    email: str,
    date_of_birth: date,
    ssn_last4: str,
    address_line1: str,
    city: str,
    state: str,
    zip_code: str,
    credit_score: int = None,
) -> Customer:
    with get_session() as session:
        new_customer = Customer(
            first_name    = first_name,
            last_name     = last_name,
            email         = email,
            date_of_birth = date_of_birth,
            ssn_last4     = ssn_last4,
            address_line1 = address_line1,
            city          = city,
            state         = state,
            zip_code      = zip_code,
            credit_score  = credit_score,
            joined_date   = date.today(),
            is_active     = True,
        )
        session.add(new_customer)
        session.commit()
        # refresh() syncs the object with the DB (loads generated PK)
        session.refresh(new_customer)
        print(f"Created customer ID={new_customer.customer_id}")
        return new_customer


# ─────────────────────────────────────────────
# 2.9  UPDATE — Change a customer's credit score
# ─────────────────────────────────────────────
# SQL equivalent:
#   UPDATE customers
#   SET    credit_score = 780
#   WHERE  customer_id = 1;

def update_credit_score(customer_id: int, new_score: int) -> int:
    with get_session() as session:
        stmt = (
            update(Customer)
            .where(Customer.customer_id == customer_id)
            .values(credit_score=new_score)
        )
        result = session.execute(stmt)
        session.commit()
        rows_affected = result.rowcount
        print(f"Updated {rows_affected} row(s)")
        return rows_affected


# ─────────────────────────────────────────────
# 2.10  SOFT DELETE — Deactivate an account
# ─────────────────────────────────────────────
# Real banking systems rarely hard-delete; they flip is_active = FALSE.
# SQL equivalent:
#   UPDATE accounts SET is_active = FALSE WHERE account_id = 5;

def deactivate_account(account_id: int) -> int:
    with get_session() as session:
        stmt = (
            update(Account)
            .where(Account.account_id == account_id)
            .values(is_active=False)
        )
        result = session.execute(stmt)
        session.commit()
        print(f"Deactivated account {account_id} ({result.rowcount} row)")
        return result.rowcount


# ─────────────────────────────────────────────
# 2.11  HARD DELETE — Remove a specific record
# ─────────────────────────────────────────────
# Use with caution; foreign key constraints will raise an error
# if child records exist (transactions, etc.).
# SQL equivalent:
#   DELETE FROM fraud_alerts WHERE alert_id = 1;

def delete_fraud_alert(alert_id: int) -> int:
    from module_01_python_sqlalchemy.setup_and_models import FraudAlert  # type: ignore
    with get_session() as session:
        stmt = delete(FraudAlert).where(FraudAlert.alert_id == alert_id)
        result = session.execute(stmt)
        session.commit()
        print(f"Deleted {result.rowcount} fraud alert(s)")
        return result.rowcount


# ─────────────────────────────────────────────
# 2.12  COUNT ROWS
# ─────────────────────────────────────────────
# SQL equivalent:  SELECT COUNT(*) FROM customers;

def count_customers() -> int:
    with get_session() as session:
        stmt = select(func.count()).select_from(Customer)
        total = session.execute(stmt).scalar()
        print(f"Total customers: {total}")
        return total


# ─────────────────────────────────────────────
# 2.13  GET BY PRIMARY KEY
# ─────────────────────────────────────────────
# session.get() is the most efficient lookup by PK (uses identity map cache).

def get_customer_by_id(customer_id: int) -> Customer | None:
    with get_session() as session:
        customer = session.get(Customer, customer_id)
        if customer:
            print(f"Found: {customer.first_name} {customer.last_name}")
        else:
            print(f"Customer {customer_id} not found")
        return customer


# ─────────────────────────────────────────────
# 2.14  GET ONE OR RAISE (first())
# ─────────────────────────────────────────────
# SQL equivalent:
#   SELECT * FROM customers WHERE email = 'alice@example.com' LIMIT 1;

def get_customer_by_email(email: str) -> Customer | None:
    with get_session() as session:
        stmt = select(Customer).where(Customer.email == email)
        customer = session.execute(stmt).scalars().first()
        return customer


# ─────────────────────────────────────────────
# DEMO — Run all functions
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("2.1  All customers:")
    select_all_customers()

    print("\n2.3  Customers in NY:")
    customers_in_state("NY")

    print("\n2.5  Top 5 credit scores:")
    top_credit_score_customers(5)

    print("\n2.7  Employees without a manager (top-level):")
    employees_without_manager()

    print("\n2.12 Customer count:")
    count_customers()

    print("\n2.13 Get customer ID=1:")
    get_customer_by_id(1)
