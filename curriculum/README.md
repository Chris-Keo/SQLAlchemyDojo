# 🏦 First National Bank — PostgreSQL Master's Curriculum

> A graduate-level, project-based SQL curriculum using realistic banking data.
> Every concept is taught through a real banking scenario — no toy datasets.

---

## What You'll Learn

| Skill | Where |
|-------|-------|
| `SELECT`, filtering, `ORDER BY`, `LIMIT`, `LIKE`, `NULL` | Module 1 |
| `JOIN` (INNER, LEFT, RIGHT, FULL, SELF) | Module 1 |
| `GROUP BY`, `HAVING`, `ROLLUP`, `CUBE`, `GROUPING SETS` | Module 2 |
| Scalar, correlated, `IN`/`EXISTS` subqueries | Module 3 |
| CTEs (`WITH`), chained CTEs, recursive CTEs | Module 4 |
| Window functions: `RANK`, `DENSE_RANK`, `NTILE`, `ROW_NUMBER` | Module 5 |
| Running totals, moving averages (`SUM OVER`, `AVG OVER`) | Module 5 |
| `LAG`, `LEAD`, `FIRST_VALUE`, `LAST_VALUE`, frame clauses | Module 5 |
| Date/time, strings, regex, `CASE`, `UNION`, `LATERAL`, JSON | Module 6 |
| `EXPLAIN ANALYZE`, indexes, materialized views, partitioning | Module 7 |
| Fraud detection, risk scoring, RFM customer segmentation | Module 8 |
| End-to-end capstone combining all techniques | Module 9 |

---

## The Banking Schema

```
branches ──< employees (self-join for manager hierarchy)
branches ──< accounts ──< transactions
customers ──< accounts
customers ──< credit_cards ──< credit_card_transactions
customers ──< loans ──< loan_payments
customers ──< fraud_alerts
```

### Tables at a glance

| Table | Rows | Description |
|-------|------|-------------|
| `branches` | 10 | Bank branches across 5 states |
| `employees` | 20 | Staff with manager self-reference |
| `customers` | 50 | Retail banking customers |
| `accounts` | 47 | Checking, savings, money market, CD |
| `transactions` | 90+ | Deposits, withdrawals, transfers, fees |
| `credit_cards` | 14 | Cards with limits and balances |
| `credit_card_transactions` | 70+ | Merchant-level CC activity |
| `loans` | 20 | Mortgage, auto, personal, student loans |
| `loan_payments` | 25+ | Payment history with late fees |
| `fraud_alerts` | 6 | Flagged suspicious activity |

---

## Getting Started

### Prerequisites
- PostgreSQL 14+ (or pgAdmin 4 connected to a local/cloud Postgres instance)
- A database to load the schema into (e.g., `firstnational_db`)

### Setup (pgAdmin or psql)

**Option A — pgAdmin**
1. Open pgAdmin → right-click your server → Create → Database → name it `firstnational_db`
2. Open Query Tool on that database
3. Open and run `curriculum/schema/01_create_tables.sql`
4. Open and run `curriculum/schema/02_seed_data.sql`
5. You're ready. Open any module file and run it.

**Option B — psql**
```bash
psql -U postgres -c "CREATE DATABASE firstnational_db;"
psql -U postgres -d firstnational_db -f curriculum/schema/01_create_tables.sql
psql -U postgres -d firstnational_db -f curriculum/schema/02_seed_data.sql
```

---

## Curriculum Roadmap

```
curriculum/
├── schema/
│   ├── 01_create_tables.sql   ← Run first
│   └── 02_seed_data.sql       ← Run second
│
├── module_01_foundations/
│   ├── 01_select_basics.sql
│   ├── 02_joins.sql
│   └── exercises/
│       ├── 01_exercises.sql   ← Attempt these first
│       └── 01_solutions.sql
│
├── module_02_aggregations/
│   ├── 01_aggregations.sql
│   └── exercises/
│       ├── 02_exercises.sql
│       └── 02_solutions.sql
│
├── module_03_subqueries/
│   └── 01_subqueries.sql
│
├── module_04_ctes/
│   ├── 01_ctes.sql
│   └── exercises/
│       └── 04_exercises.sql
│
├── module_05_window_functions/
│   ├── 01_window_functions.sql   ← The heart of the curriculum
│   └── exercises/
│       ├── 05_exercises.sql
│       └── 05_solutions.sql
│
├── module_06_advanced_sql/
│   └── 01_advanced_sql.sql
│
├── module_07_performance/
│   └── 01_performance_indexing.sql
│
├── module_08_banking_analytics/
│   └── 01_banking_analytics.sql
│
└── module_09_capstone/
    ├── capstone_questions.sql   ← Write your answers here
    └── capstone_solutions.sql
```

---

## Module-by-Module Guide

### Module 1 — SQL Foundations
**Files:** `01_select_basics.sql`, `02_joins.sql`

Core reading operations: `SELECT`, `WHERE`, `AND/OR/NOT`, `IN`, `BETWEEN`, `LIKE`, `IS NULL`, `ORDER BY`, `LIMIT`, all join types, self-joins, multi-table joins.

**Key queries:**
- Mask account numbers (show only last 4 digits)
- Find customers with no loans (LEFT JOIN + NULL check)
- Build the employee org chart with SELF JOIN

---

### Module 2 — Aggregations
**File:** `01_aggregations.sql`

`COUNT`, `SUM`, `AVG`, `MIN`, `MAX`, `GROUP BY`, `HAVING`, `COUNT DISTINCT`, `FILTER`, `ROLLUP`, `CUBE`, `GROUPING SETS`.

**Key queries:**
- Monthly fee income vs interest paid
- States with below-average credit scores
- Transaction pivot by type using FILTER

---

### Module 3 — Subqueries & Derived Tables
**File:** `01_subqueries.sql`

Scalar subqueries, derived tables in `FROM`, `IN`, `NOT IN`, `EXISTS`, `NOT EXISTS`, correlated subqueries, `ANY`/`ALL`.

**Key queries:**
- Customers above bank-wide average credit score
- Accounts that have never transacted
- Top 20% of customers by total balance

---

### Module 4 — Common Table Expressions (CTEs)
**File:** `01_ctes.sql`

`WITH` clause, chained CTEs, staging CTEs, recursive CTEs, writable CTEs, `MATERIALIZED`.

**Key queries:**
- Recursive employee org chart traversal
- Loan amortization schedule via recursion
- Wealth tier classification pipeline

---

### Module 5 — Window Functions ⭐
**File:** `01_window_functions.sql`

`ROW_NUMBER`, `RANK`, `DENSE_RANK`, `NTILE`, `SUM OVER` (running totals), `AVG OVER` (moving averages), `LAG`, `LEAD`, `FIRST_VALUE`, `LAST_VALUE`, `PERCENT_RANK`, `CUME_DIST`, frame clauses (`ROWS BETWEEN`), named `WINDOW` clause.

**Key queries:**
- Running account balance over time
- 3-month rolling average of monthly deposits
- Month-over-month % change in transaction volume
- Customer credit score percentile ranking

---

### Module 6 — Advanced SQL
**File:** `01_advanced_sql.sql`

Date/time functions, string manipulation, regex, `CASE`, `UNION ALL`, `INTERSECT`, `EXCEPT`, `LATERAL` joins, crosstab pivot, `GENERATE_SERIES`, array functions, JSON output.

**Key queries:**
- Gap analysis: months with no transactions
- Geographic fraud: same-day domestic + international transactions
- Customer profile JSON for API backends

---

### Module 7 — Performance & Indexing
**File:** `01_performance_indexing.sql`

`EXPLAIN`, `EXPLAIN ANALYZE`, B-tree indexes, partial indexes, composite indexes, covering indexes, `pg_stat_user_indexes`, `VACUUM ANALYZE`, materialized views, views.

**Key queries:**
- Compare correlated subquery vs pre-aggregated join (timing difference)
- Create the `v_customer_360` view for reuse across queries
- Build `mv_daily_account_summary` materialized view

---

### Module 8 — Banking Analytics
**File:** `01_banking_analytics.sql`

Real-world use cases combining everything:

**Fraud Detection**
- Velocity check: 3+ transactions in 10 minutes
- After-hours large amount detection
- Duplicate credit card charge detection
- Same-day domestic + international geo anomaly

**Risk Analysis**
- Loan portfolio breakdown with % of total exposure
- Credit utilization buckets (maxed-out vs low)
- Delinquency aging report (30/60/90+ days)
- Multi-factor customer default risk scoring model

**Customer Segmentation**
- Full RFM analysis (Recency, Frequency, Monetary)
- Segment customers into Champions / Loyal / At-Risk / Lost

---

### Module 9 — Capstone Project
**Files:** `capstone_questions.sql`, `capstone_solutions.sql`

Six business-critical reports combining CTEs, window functions, aggregations, and joins:

1. **Branch Performance Scorecard** — multi-metric ranking per state
2. **Employee Compensation vs. Branch Revenue**
3. **Customer Lifetime Value (CLV)** — with percentile tiers
4. **30-Day Fraud Heat Map** — daily rolling averages
5. **Loan Amortization Dashboard** — payment tracking + projections
6. **Full Customer 360 Risk Report** — combining all risk signals

---

## SQL Patterns Cheat Sheet

### CTE Template
```sql
WITH cte_name AS (
    SELECT ...
    FROM   ...
    WHERE  ...
),
second_cte AS (
    SELECT ...
    FROM   cte_name
    JOIN   ...
)
SELECT * FROM second_cte;
```

### Window Function Template
```sql
SELECT col,
       SUM(amount)  OVER (PARTITION BY account_id ORDER BY tx_date
                          ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total,
       LAG(amount)  OVER (PARTITION BY account_id ORDER BY tx_date)         AS prev_amount,
       RANK()       OVER (PARTITION BY account_type ORDER BY balance DESC)  AS balance_rank
FROM   transactions;
```

### RFM Segmentation Template
```sql
NTILE(5) OVER (ORDER BY last_activity DESC)   AS recency_score,
NTILE(5) OVER (ORDER BY tx_count DESC)        AS frequency_score,
NTILE(5) OVER (ORDER BY total_spent DESC)     AS monetary_score
```

---

## Tips for pgAdmin Users

- Use **F5** to run the entire script, **F9** to run only selected text.
- In the query tool, use **Explain** (Shift+F7) to see the visual query plan.
- Right-click a table → **View/Edit Data** to browse rows quickly.
- Save frequently-used queries as **pgAdmin Named Queries** (star icon).
- Use the **Query History** panel to revisit previous runs.

---

## Learning Order Recommendation

```
Beginner     → Module 1 → Module 2 → Module 3
Intermediate → Module 4 → Module 5
Advanced     → Module 6 → Module 7
Expert       → Module 8 → Module 9 (Capstone)
```

**Estimated study time:** 40–80 hours depending on prior experience.

---

*Built for learning PostgreSQL SQL from first principles to production-level banking analytics.*
