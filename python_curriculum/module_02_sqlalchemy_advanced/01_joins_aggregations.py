# =============================================================================
# MODULE 2: SQLALCHEMY ADVANCED QUERIES
# Lesson 1 – Joins, Aggregations, Subqueries
# =============================================================================
# Goal: Mirror the SQL curriculum (Modules 2–3) using SQLAlchemy ORM.
#       Move from single-table lookups to multi-table analysis.
# =============================================================================

from sqlalchemy import select, func, and_, or_, desc, literal_column
from sqlalchemy.orm import Session

from module_01_python_sqlalchemy.setup_and_models import (  # type: ignore
    SessionLocal, Customer, Account, Transaction, Branch,
    Employee, Loan, LoanPayment, CreditCard, FraudAlert,
    AccountTypeEnum, TransactionTypeEnum
)


# ─────────────────────────────────────────────
# 2.1  INNER JOIN
# ─────────────────────────────────────────────
# SQL equivalent:
#   SELECT c.first_name, c.last_name, a.account_number, a.account_type, a.balance
#   FROM   customers c
#   JOIN   accounts  a ON a.customer_id = c.customer_id
#   WHERE  a.is_active = TRUE
#   ORDER BY a.balance DESC;

def customer_accounts_inner_join():
    with SessionLocal() as session:
        stmt = (
            select(
                Customer.first_name,
                Customer.last_name,
                Account.account_number,
                Account.account_type,
                Account.balance,
            )
            .join(Account, Account.customer_id == Customer.customer_id)
            .where(Account.is_active == True)
            .order_by(Account.balance.desc())
        )
        rows = session.execute(stmt).all()
        for row in rows:
            print(row)
        return rows


# ─────────────────────────────────────────────
# 2.2  LEFT JOIN — customers with no loans
# ─────────────────────────────────────────────
# SQL equivalent:
#   SELECT c.customer_id, c.first_name, c.last_name
#   FROM   customers c
#   LEFT JOIN loans l ON l.customer_id = c.customer_id
#   WHERE  l.loan_id IS NULL;

def customers_without_loans():
    with SessionLocal() as session:
        stmt = (
            select(Customer.customer_id, Customer.first_name, Customer.last_name)
            .outerjoin(Loan, Loan.customer_id == Customer.customer_id)
            .where(Loan.loan_id.is_(None))
            .order_by(Customer.last_name)
        )
        rows = session.execute(stmt).all()
        for row in rows:
            print(row)
        return rows


# ─────────────────────────────────────────────
# 2.3  SELF JOIN — Employee org chart
# ─────────────────────────────────────────────
# SQL equivalent:
#   SELECT e.first_name || ' ' || e.last_name AS employee,
#          m.first_name || ' ' || m.last_name AS manager
#   FROM   employees e
#   LEFT JOIN employees m ON m.employee_id = e.manager_id
#   ORDER BY manager, employee;

from sqlalchemy.orm import aliased

def employee_org_chart():
    with SessionLocal() as session:
        Manager = aliased(Employee, name="manager")
        stmt = (
            select(
                (Employee.first_name + " " + Employee.last_name).label("employee"),
                (Manager.first_name + " " + Manager.last_name).label("manager"),
                Employee.job_title,
            )
            .outerjoin(Manager, Manager.employee_id == Employee.manager_id)
            .order_by("manager", "employee")
        )
        rows = session.execute(stmt).all()
        print(f"  → {len(rows)} employee record(s) in org chart (see returned rows for details)")
        return rows


# ─────────────────────────────────────────────
# 2.4  MULTI-TABLE JOIN (3 tables)
# ─────────────────────────────────────────────
# SQL equivalent:
#   SELECT b.branch_name, c.first_name, c.last_name, a.account_type, a.balance
#   FROM   branches b
#   JOIN   accounts  a ON a.branch_id   = b.branch_id
#   JOIN   customers c ON c.customer_id = a.customer_id
#   ORDER BY b.branch_name, a.balance DESC;

def accounts_by_branch():
    with SessionLocal() as session:
        stmt = (
            select(
                Branch.branch_name,
                Customer.first_name,
                Customer.last_name,
                Account.account_type,
                Account.balance,
            )
            .join(Account, Account.branch_id == Branch.branch_id)
            .join(Customer, Customer.customer_id == Account.customer_id)
            .order_by(Branch.branch_name, Account.balance.desc())
        )
        rows = session.execute(stmt).all()
        for row in rows:
            print(row)
        return rows


# ─────────────────────────────────────────────
# 2.5  AGGREGATIONS: COUNT, SUM, AVG, MIN, MAX
# ─────────────────────────────────────────────
# SQL equivalent:
#   SELECT account_type,
#          COUNT(*)       AS num_accounts,
#          SUM(balance)   AS total_balance,
#          AVG(balance)   AS avg_balance,
#          MIN(balance)   AS min_balance,
#          MAX(balance)   AS max_balance
#   FROM   accounts
#   WHERE  is_active = TRUE
#   GROUP BY account_type
#   ORDER BY total_balance DESC;

def account_summary_by_type():
    with SessionLocal() as session:
        stmt = (
            select(
                Account.account_type,
                func.count().label("num_accounts"),
                func.sum(Account.balance).label("total_balance"),
                func.avg(Account.balance).label("avg_balance"),
                func.min(Account.balance).label("min_balance"),
                func.max(Account.balance).label("max_balance"),
            )
            .where(Account.is_active == True)
            .group_by(Account.account_type)
            .order_by(desc("total_balance"))
        )
        rows = session.execute(stmt).all()
        for row in rows:
            print(f"{row.account_type.value:15s}  "
                  f"count={row.num_accounts}  "
                  f"total=${row.total_balance:,.2f}  "
                  f"avg=${row.avg_balance:,.2f}")
        return rows


# ─────────────────────────────────────────────
# 2.6  HAVING — filter on aggregated result
# ─────────────────────────────────────────────
# SQL equivalent:
#   SELECT state, COUNT(*) AS customer_count, AVG(credit_score) AS avg_score
#   FROM   customers
#   WHERE  is_active = TRUE
#   GROUP BY state
#   HAVING AVG(credit_score) < 700
#   ORDER BY avg_score;

def states_below_avg_credit(threshold: float = 700):
    with SessionLocal() as session:
        avg_score = func.avg(Customer.credit_score).label("avg_score")
        stmt = (
            select(
                Customer.state,
                func.count().label("customer_count"),
                avg_score,
            )
            .where(Customer.is_active == True)
            .group_by(Customer.state)
            .having(func.avg(Customer.credit_score) < threshold)
            .order_by(avg_score)
        )
        rows = session.execute(stmt).all()
        for row in rows:
            print(f"State={row.state}  Count={row.customer_count}  "
                  f"Avg Score={float(row.avg_score):.1f}")
        return rows


# ─────────────────────────────────────────────
# 2.7  SUBQUERY — customers above bank-wide average credit score
# ─────────────────────────────────────────────
# SQL equivalent:
#   SELECT first_name, last_name, credit_score
#   FROM   customers
#   WHERE  credit_score > (SELECT AVG(credit_score) FROM customers)
#   ORDER BY credit_score DESC;

def customers_above_avg_credit():
    with SessionLocal() as session:
        # scalar_subquery() embeds a single-value subquery inline
        avg_subq = select(func.avg(Customer.credit_score)).scalar_subquery()
        stmt = (
            select(Customer.first_name, Customer.last_name, Customer.credit_score)
            .where(Customer.credit_score > avg_subq)
            .order_by(Customer.credit_score.desc())
        )
        rows = session.execute(stmt).all()
        print(f"  → {len(rows)} customer(s) above bank-wide average credit score")
        return rows


# ─────────────────────────────────────────────
# 2.8  CORRELATED SUBQUERY — accounts with above-average balance for their type
# ─────────────────────────────────────────────
# SQL equivalent:
#   SELECT a.account_id, a.account_type, a.balance
#   FROM   accounts a
#   WHERE  a.balance > (
#       SELECT AVG(a2.balance)
#       FROM   accounts a2
#       WHERE  a2.account_type = a.account_type
#   );

from sqlalchemy.orm import aliased

def accounts_above_type_average():
    with SessionLocal() as session:
        A2 = aliased(Account)
        # Correlated: the inner query references the outer account_type
        avg_for_type = (
            select(func.avg(A2.balance))
            .where(A2.account_type == Account.account_type)
            .correlate(Account)
            .scalar_subquery()
        )
        stmt = (
            select(Account.account_id, Account.account_type, Account.balance)
            .where(Account.balance > avg_for_type)
            .order_by(Account.account_type, Account.balance.desc())
        )
        rows = session.execute(stmt).all()
        for row in rows:
            print(f"ID={row.account_id}  {row.account_type.value}  ${row.balance:,.2f}")
        return rows


# ─────────────────────────────────────────────
# 2.9  EXISTS — customers who have at least one active loan
# ─────────────────────────────────────────────
# SQL equivalent:
#   SELECT c.customer_id, c.first_name, c.last_name
#   FROM   customers c
#   WHERE  EXISTS (
#       SELECT 1 FROM loans l
#       WHERE  l.customer_id = c.customer_id
#         AND  l.status = 'active'
#   );

from sqlalchemy import exists

def customers_with_active_loan():
    with SessionLocal() as session:
        loan_exists = (
            select(Loan.loan_id)
            .where(
                and_(
                    Loan.customer_id == Customer.customer_id,
                    Loan.status == "active",
                )
            )
            .correlate(Customer)
            .exists()
        )
        stmt = (
            select(Customer.customer_id, Customer.first_name, Customer.last_name)
            .where(loan_exists)
            .order_by(Customer.last_name)
        )
        rows = session.execute(stmt).all()
        for row in rows:
            print(f"ID={row.customer_id}  {row.first_name} {row.last_name}")
        return rows


# ─────────────────────────────────────────────
# 2.10  GROUP BY across two joined tables — branch transaction volume
# ─────────────────────────────────────────────
# SQL equivalent:
#   SELECT b.branch_name, COUNT(t.transaction_id) AS tx_count,
#          SUM(t.amount) AS total_volume
#   FROM   branches b
#   JOIN   accounts     a ON a.branch_id    = b.branch_id
#   JOIN   transactions t ON t.account_id   = a.account_id
#   GROUP BY b.branch_name
#   ORDER BY total_volume DESC;

def branch_transaction_volume():
    with SessionLocal() as session:
        stmt = (
            select(
                Branch.branch_name,
                func.count(Transaction.transaction_id).label("tx_count"),
                func.sum(Transaction.amount).label("total_volume"),
            )
            .join(Account, Account.branch_id == Branch.branch_id)
            .join(Transaction, Transaction.account_id == Account.account_id)
            .group_by(Branch.branch_name)
            .order_by(desc("total_volume"))
        )
        rows = session.execute(stmt).all()
        for row in rows:
            print(f"{row.branch_name:30s}  "
                  f"txns={row.tx_count}  "
                  f"volume=${row.total_volume:,.2f}")
        return rows


# ─────────────────────────────────────────────
# DEMO
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("2.1  Customer accounts (inner join):")
    customer_accounts_inner_join()

    print("\n2.2  Customers without any loan:")
    customers_without_loans()

    print("\n2.3  Employee org chart (self-join):")
    employee_org_chart()

    print("\n2.5  Account summary by type:")
    account_summary_by_type()

    print("\n2.6  States below 700 avg credit score:")
    states_below_avg_credit()

    print("\n2.7  Customers above bank-wide avg credit score:")
    customers_above_avg_credit()

    print("\n2.10 Branch transaction volume:")
    branch_transaction_volume()
