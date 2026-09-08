# =============================================================================
# MODULE 2: SOLUTIONS
# =============================================================================

from sqlalchemy import select, func, text, and_, desc, case
from sqlalchemy.orm import aliased

from module_01_python_sqlalchemy.setup_and_models import (  # type: ignore
    SessionLocal, Customer, Account, Transaction, Branch, Employee, Loan,
    LoanStatusEnum
)


def exercise_1():
    with SessionLocal() as session:
        stmt = (
            select(
                Branch.branch_name,
                Branch.state,
                func.count(Account.account_id).label("active_account_count"),
            )
            .join(Account, Account.branch_id == Branch.branch_id)
            .where(Account.is_active == True)
            .group_by(Branch.branch_name, Branch.state)
            .order_by(desc("active_account_count"))
        )
        rows = session.execute(stmt).all()
        for row in rows:
            print(f"{row.branch_name:<30s}  {row.state}  count={row.active_account_count}")
        return rows


def exercise_2():
    with SessionLocal() as session:
        # Subquery approach: aggregate accounts per customer, then filter
        sub = (
            select(
                Account.customer_id,
                func.count(Account.account_id).label("account_count"),
            )
            .where(Account.is_active == True)
            .group_by(Account.customer_id)
            .having(func.count(Account.account_id) > 1)
            .subquery()
        )
        stmt = (
            select(
                Customer.customer_id,
                Customer.first_name,
                Customer.last_name,
                sub.c.account_count,
            )
            .join(sub, sub.c.customer_id == Customer.customer_id)
            .order_by(desc(sub.c.account_count))
        )
        rows = session.execute(stmt).all()
        for row in rows:
            print(f"ID={row.customer_id}  {row.first_name} {row.last_name}  "
                  f"accounts={row.account_count}")
        return rows


def exercise_3():
    with SessionLocal() as session:
        rank_in_state = func.rank().over(
            partition_by=Customer.state,
            order_by=Customer.credit_score.desc(),
        ).label("state_rank")

        stmt = (
            select(
                Customer.state,
                Customer.first_name,
                Customer.last_name,
                Customer.credit_score,
                rank_in_state,
            )
            .where(Customer.credit_score.isnot(None))
            .order_by(Customer.state, rank_in_state)
        )
        rows = session.execute(stmt).all()
        print(f"  → {len(rows)} customer(s) ranked by credit score within state")
        return rows


def exercise_4():
    sql = text("""
        SELECT  a.account_id,
                a.account_number,
                MAX(t.amount)                                              AS max_tx_amount,
                MAX(t.transaction_date)
                    FILTER (WHERE t.amount = MAX(t.amount) OVER (
                        PARTITION BY t.account_id
                    ))                                                     AS max_tx_date
        FROM    accounts     a
        JOIN    transactions t ON t.account_id = a.account_id
        GROUP BY a.account_id, a.account_number
        ORDER BY max_tx_amount DESC
    """)
    with SessionLocal() as session:
        rows = session.execute(sql).all()
        for row in rows:
            print(f"account={row.account_number}  "
                  f"max_tx=${row.max_tx_amount:,.2f}  "
                  f"on={row.max_tx_date}")
        return rows


def exercise_5():
    with SessionLocal() as session:
        loan_totals_cte = (
            select(
                Loan.customer_id,
                func.sum(Loan.remaining_balance).label("total_loan_exposure"),
            )
            .where(Loan.status == LoanStatusEnum.active)
            .group_by(Loan.customer_id)
            .cte("loan_totals")
        )
        stmt = (
            select(
                Customer.first_name,
                Customer.last_name,
                loan_totals_cte.c.total_loan_exposure,
            )
            .join(loan_totals_cte, loan_totals_cte.c.customer_id == Customer.customer_id)
            .where(loan_totals_cte.c.total_loan_exposure > 50000)
            .order_by(desc(loan_totals_cte.c.total_loan_exposure))
        )
        rows = session.execute(stmt).all()
        for row in rows:
            print(f"{row.first_name} {row.last_name}  "
                  f"exposure=${row.total_loan_exposure:,.2f}")
        return rows


def exercise_6():
    sql = text("""
        WITH tx_with_next AS (
            SELECT account_id,
                   transaction_id,
                   transaction_date,
                   amount,
                   LEAD(transaction_date) OVER (
                       PARTITION BY account_id ORDER BY transaction_date
                   ) AS next_tx_date,
                   LEAD(transaction_id) OVER (
                       PARTITION BY account_id ORDER BY transaction_date
                   ) AS next_tx_id
            FROM   transactions
        ),
        rapid_pairs AS (
            SELECT account_id,
                   transaction_id,
                   next_tx_id,
                   transaction_date,
                   next_tx_date,
                   EXTRACT(EPOCH FROM (next_tx_date - transaction_date)) / 60.0 AS minutes_apart
            FROM   tx_with_next
            WHERE  next_tx_date IS NOT NULL
        )
        SELECT  a.account_id,
                c.first_name || ' ' || c.last_name AS customer_name,
                rp.transaction_id,
                rp.transaction_date,
                rp.next_tx_id,
                rp.next_tx_date,
                ROUND(rp.minutes_apart::numeric, 2) AS minutes_between
        FROM    rapid_pairs rp
        JOIN    accounts    a ON a.account_id   = rp.account_id
        JOIN    customers   c ON c.customer_id  = a.customer_id
        WHERE   rp.minutes_apart < 10
        ORDER BY rp.minutes_apart
    """)
    with SessionLocal() as session:
        rows = session.execute(sql).all()
        for row in rows:
            print(f"{row.customer_name}  "
                  f"tx={row.transaction_id} → {row.next_tx_id}  "
                  f"{row.minutes_between} min apart")
        return rows


if __name__ == "__main__":
    print("Exercise 1:"); exercise_1()
    print("\nExercise 2:"); exercise_2()
    print("\nExercise 3:"); exercise_3()
    print("\nExercise 4:"); exercise_4()
    print("\nExercise 5:"); exercise_5()
    print("\nExercise 6:"); exercise_6()
