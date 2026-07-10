# =============================================================================
# MODULE 2: SQLALCHEMY ADVANCED QUERIES
# Lesson 2 – Window Functions, CTEs, and Raw SQL via text()
# =============================================================================
# Goal: Replicate the analytics from SQL Modules 4–5 using SQLAlchemy's
#       text(), CTE support, and over() / func() for window functions.
# =============================================================================

from sqlalchemy import select, func, text, literal_column, desc, and_
from sqlalchemy.orm import Session

from module_01_python_sqlalchemy.setup_and_models import (  # type: ignore
    SessionLocal, Customer, Account, Transaction, Branch,
    Employee, Loan, LoanPayment
)


# ─────────────────────────────────────────────
# 2.1  RAW SQL VIA text() — when the ORM is insufficient
# ─────────────────────────────────────────────
# text() lets you write a verbatim SQL string and bind parameters safely.
# Use it for window functions, complex CTEs, or PostgreSQL-specific syntax.

def running_account_balance(account_id: int):
    """Running balance over time using a window function.

    SQL equivalent:
        SELECT transaction_id,
               transaction_date,
               amount,
               transaction_type,
               SUM(amount) OVER (
                   PARTITION BY account_id
                   ORDER BY     transaction_date
                   ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
               ) AS running_balance
        FROM   transactions
        WHERE  account_id = :account_id
        ORDER BY transaction_date;
    """
    sql = text("""
        SELECT transaction_id,
               transaction_date,
               amount,
               transaction_type,
               SUM(amount) OVER (
                   PARTITION BY account_id
                   ORDER BY     transaction_date
                   ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
               ) AS running_balance
        FROM   transactions
        WHERE  account_id = :account_id
        ORDER BY transaction_date
    """)
    with SessionLocal() as session:
        rows = session.execute(sql, {"account_id": account_id}).all()
        for row in rows:
            print(f"{row.transaction_date}  "
                  f"amount={row.amount:>10.2f}  "
                  f"running={row.running_balance:>12.2f}  "
                  f"type={row.transaction_type}")
        return rows


# ─────────────────────────────────────────────
# 2.2  RANK / DENSE_RANK with ORM's over()
# ─────────────────────────────────────────────
# SQLAlchemy exposes window functions via func.<name>().over(...)
# SQL equivalent:
#   SELECT customer_id, first_name, last_name, credit_score,
#          RANK()       OVER (ORDER BY credit_score DESC) AS rank,
#          DENSE_RANK() OVER (ORDER BY credit_score DESC) AS dense_rank,
#          PERCENT_RANK() OVER (ORDER BY credit_score DESC) AS percentile
#   FROM   customers
#   WHERE  is_active = TRUE
#   ORDER BY rank;

def customer_credit_score_rankings():
    with SessionLocal() as session:
        rank_window = {"order_by": Customer.credit_score.desc()}
        stmt = (
            select(
                Customer.customer_id,
                Customer.first_name,
                Customer.last_name,
                Customer.credit_score,
                func.rank().over(**rank_window).label("rank"),
                func.dense_rank().over(**rank_window).label("dense_rank"),
                func.percent_rank().over(**rank_window).label("percentile"),
            )
            .where(Customer.is_active == True)
            .order_by("rank")
        )
        rows = session.execute(stmt).all()
        for row in rows:
            print(f"#{row.rank:<4d} {row.first_name} {row.last_name:<20s}  "
                  f"Score={row.credit_score}  "
                  f"Pctile={float(row.percentile):.1%}")  # educational output
        return rows


# ─────────────────────────────────────────────
# 2.3  LAG / LEAD — month-over-month change
# ─────────────────────────────────────────────
# SQL equivalent (monthly transaction totals with MoM change):
#   WITH monthly AS (
#       SELECT DATE_TRUNC('month', transaction_date) AS month,
#              SUM(amount) AS total
#       FROM   transactions
#       GROUP BY 1
#   )
#   SELECT month,
#          total,
#          LAG(total) OVER (ORDER BY month) AS prev_month,
#          ROUND(
#            (total - LAG(total) OVER (ORDER BY month))
#            / NULLIF(LAG(total) OVER (ORDER BY month), 0) * 100,
#          2) AS pct_change
#   FROM monthly
#   ORDER BY month;

def monthly_transaction_mom_change():
    sql = text("""
        WITH monthly AS (
            SELECT DATE_TRUNC('month', transaction_date) AS month,
                   SUM(amount)                           AS total
            FROM   transactions
            GROUP BY 1
        )
        SELECT month,
               total,
               LAG(total) OVER (ORDER BY month)                              AS prev_month,
               ROUND(
                 (total - LAG(total) OVER (ORDER BY month))
                 / NULLIF(LAG(total) OVER (ORDER BY month), 0) * 100,
               2)                                                             AS pct_change
        FROM   monthly
        ORDER BY month
    """)
    with SessionLocal() as session:
        rows = session.execute(sql).all()
        for row in rows:
            change = f"{row.pct_change:+.1f}%" if row.pct_change is not None else "  n/a"
            print(f"{str(row.month)[:7]}  total=${row.total:>12,.2f}  MoM={change}")
        return rows


# ─────────────────────────────────────────────
# 2.4  SQLALCHEMY CTE — chained CTEs
# ─────────────────────────────────────────────
# SQLAlchemy 1.4+ supports CTEs via .cte() on a select().
# SQL equivalent (wealth tiers):
#   WITH totals AS (
#       SELECT customer_id, SUM(balance) AS total_balance
#       FROM   accounts WHERE is_active = TRUE GROUP BY customer_id
#   ),
#   tiered AS (
#       SELECT c.first_name, c.last_name, t.total_balance,
#              CASE
#                WHEN t.total_balance >= 100000 THEN 'Platinum'
#                WHEN t.total_balance >= 25000  THEN 'Gold'
#                WHEN t.total_balance >= 5000   THEN 'Silver'
#                ELSE                                'Bronze'
#              END AS tier
#       FROM customers c JOIN totals t USING (customer_id)
#   )
#   SELECT tier, COUNT(*), AVG(total_balance)
#   FROM   tiered GROUP BY tier ORDER BY AVG(total_balance) DESC;

from sqlalchemy import case

def customer_wealth_tiers():
    with SessionLocal() as session:
        # First CTE: total balance per customer
        totals_cte = (
            select(
                Account.customer_id,
                func.sum(Account.balance).label("total_balance"),
            )
            .where(Account.is_active == True)
            .group_by(Account.customer_id)
            .cte("totals")
        )

        # Second CTE: classify into wealth tiers
        tier_expr = case(
            (totals_cte.c.total_balance >= 100000, "Platinum"),
            (totals_cte.c.total_balance >= 25000,  "Gold"),
            (totals_cte.c.total_balance >= 5000,   "Silver"),
            else_="Bronze"
        ).label("tier")

        tiered_cte = (
            select(
                Customer.first_name,
                Customer.last_name,
                totals_cte.c.total_balance,
                tier_expr,
            )
            .join(totals_cte, totals_cte.c.customer_id == Customer.customer_id)
            .cte("tiered")
        )

        # Final: summarize by tier
        stmt = (
            select(
                tiered_cte.c.tier,
                func.count().label("num_customers"),
                func.avg(tiered_cte.c.total_balance).label("avg_balance"),
            )
            .group_by(tiered_cte.c.tier)
            .order_by(desc("avg_balance"))
        )
        rows = session.execute(stmt).all()
        for row in rows:
            print(f"Tier={row.tier:<10s}  "
                  f"customers={row.num_customers}  "
                  f"avg_balance=${float(row.avg_balance):,.2f}")
        return rows


# ─────────────────────────────────────────────
# 2.5  NTILE — RFM segmentation (Recency, Frequency, Monetary)
# ─────────────────────────────────────────────
# This is the Python equivalent of the SQL Module 8 RFM analysis.

def rfm_segmentation():
    sql = text("""
        WITH rfm_raw AS (
            SELECT  c.customer_id,
                    c.first_name || ' ' || c.last_name          AS customer_name,
                    MAX(t.transaction_date)                     AS last_activity,
                    COUNT(t.transaction_id)                     AS tx_count,
                    SUM(t.amount)                               AS total_spent
            FROM    customers    c
            JOIN    accounts     a ON a.customer_id = c.customer_id
            JOIN    transactions t ON t.account_id  = a.account_id
            WHERE   t.transaction_type IN ('deposit', 'payment')
            GROUP BY c.customer_id, customer_name
        ),
        rfm_scores AS (
            SELECT  customer_id,
                    customer_name,
                    NTILE(5) OVER (ORDER BY last_activity  DESC) AS recency_score,
                    NTILE(5) OVER (ORDER BY tx_count       DESC) AS frequency_score,
                    NTILE(5) OVER (ORDER BY total_spent    DESC) AS monetary_score
            FROM    rfm_raw
        )
        SELECT  customer_id,
                customer_name,
                recency_score,
                frequency_score,
                monetary_score,
                recency_score + frequency_score + monetary_score AS rfm_total,
                CASE
                  WHEN recency_score + frequency_score + monetary_score >= 13
                       THEN 'Champion'
                  WHEN recency_score + frequency_score + monetary_score >= 10
                       THEN 'Loyal'
                  WHEN recency_score <= 2 THEN 'At Risk'
                  ELSE 'Needs Attention'
                END AS segment
        FROM    rfm_scores
        ORDER BY rfm_total DESC
    """)
    with SessionLocal() as session:
        rows = session.execute(sql).all()
        for row in rows:
            print(f"{row.customer_name:<25s}  "
                  f"R={row.recency_score} F={row.frequency_score} M={row.monetary_score}  "
                  f"Total={row.rfm_total}  Segment={row.segment}")
        return rows


# ─────────────────────────────────────────────
# 2.6  MOVING AVERAGE — 3-month rolling deposits
# ─────────────────────────────────────────────

def three_month_rolling_deposits():
    sql = text("""
        WITH monthly_deposits AS (
            SELECT  DATE_TRUNC('month', transaction_date) AS month,
                    SUM(amount)                           AS deposits
            FROM    transactions
            WHERE   transaction_type = 'deposit'
            GROUP BY 1
        )
        SELECT  month,
                deposits,
                ROUND(
                    AVG(deposits) OVER (
                        ORDER BY month
                        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
                    ),
                2) AS rolling_3mo_avg
        FROM    monthly_deposits
        ORDER BY month
    """)
    with SessionLocal() as session:
        rows = session.execute(sql).all()
        for row in rows:
            print(f"{str(row.month)[:7]}  "
                  f"deposits=${row.deposits:>12,.2f}  "
                  f"3mo_avg=${row.rolling_3mo_avg:>12,.2f}")
        return rows


# ─────────────────────────────────────────────
# DEMO
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("2.1  Running balance for account 1:")
    running_account_balance(1)

    print("\n2.2  Customer credit score rankings:")
    customer_credit_score_rankings()

    print("\n2.3  Month-over-month transaction change:")
    monthly_transaction_mom_change()

    print("\n2.4  Customer wealth tiers (CTE):")
    customer_wealth_tiers()

    print("\n2.5  RFM segmentation:")
    rfm_segmentation()

    print("\n2.6  3-month rolling deposit average:")
    three_month_rolling_deposits()
