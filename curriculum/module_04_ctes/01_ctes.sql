-- =============================================================================
-- MODULE 4: COMMON TABLE EXPRESSIONS (CTEs)
-- WITH clause, chaining CTEs, recursive CTEs
-- =============================================================================

-- ─────────────────────────────────────────────
-- 4.1  BASIC CTE
-- ─────────────────────────────────────────────

-- Customer total wealth (all account balances summed)
WITH customer_wealth AS (
    SELECT c.customer_id,
           c.first_name || ' ' || c.last_name AS full_name,
           c.credit_score,
           SUM(a.balance)                      AS total_balance
    FROM   customers c
    JOIN   accounts  a ON a.customer_id = c.customer_id
    GROUP BY c.customer_id, c.first_name, c.last_name, c.credit_score
)
SELECT *
FROM   customer_wealth
ORDER BY total_balance DESC;

-- ─────────────────────────────────────────────
-- 4.2  CHAINING MULTIPLE CTEs
-- ─────────────────────────────────────────────

-- Find "at-risk" customers: low credit score AND at least one delinquent loan
WITH delinquent_customers AS (
    SELECT DISTINCT customer_id
    FROM   loans
    WHERE  status IN ('delinquent', 'defaulted')
),
low_credit AS (
    SELECT customer_id,
           first_name || ' ' || last_name AS full_name,
           credit_score,
           state
    FROM   customers
    WHERE  credit_score < 650
)
SELECT lc.customer_id,
       lc.full_name,
       lc.credit_score,
       lc.state
FROM   low_credit lc
JOIN   delinquent_customers dc ON dc.customer_id = lc.customer_id
ORDER BY lc.credit_score;

-- ─────────────────────────────────────────────
-- 4.3  CTE AS REUSABLE BUILDING BLOCK
-- ─────────────────────────────────────────────

-- Monthly transaction summary and month-over-month comparison
WITH monthly_totals AS (
    SELECT DATE_TRUNC('month', transaction_date)::DATE AS month,
           COUNT(*)                                     AS tx_count,
           SUM(amount)                                  AS total_amount,
           SUM(amount) FILTER (WHERE transaction_type = 'deposit')    AS deposits,
           SUM(amount) FILTER (WHERE transaction_type = 'withdrawal') AS withdrawals
    FROM   transactions
    WHERE  transaction_date >= '2025-01-01'
    GROUP BY DATE_TRUNC('month', transaction_date)
)
SELECT month,
       tx_count,
       total_amount,
       deposits,
       withdrawals,
       total_amount - LAG(total_amount) OVER (ORDER BY month) AS mom_change
FROM   monthly_totals
ORDER BY month;

-- ─────────────────────────────────────────────
-- 4.4  CTE FOR STAGING / DATA CLEANING
-- ─────────────────────────────────────────────

-- Classify customers by wealth tier before reporting
WITH wealth_calc AS (
    SELECT c.customer_id,
           c.first_name || ' ' || c.last_name AS full_name,
           c.state,
           SUM(a.balance)                      AS total_balance
    FROM   customers c
    JOIN   accounts  a ON a.customer_id = c.customer_id
    GROUP BY c.customer_id, c.first_name, c.last_name, c.state
),
tiered AS (
    SELECT *,
           CASE
               WHEN total_balance >= 500000 THEN 'Private Banking (>$500k)'
               WHEN total_balance >= 100000 THEN 'Premier ($100k–$500k)'
               WHEN total_balance >=  25000 THEN 'Standard ($25k–$100k)'
               ELSE                              'Basic (<$25k)'
           END AS wealth_tier
    FROM   wealth_calc
)
SELECT wealth_tier,
       COUNT(*)                        AS customers,
       ROUND(AVG(total_balance), 2)    AS avg_balance,
       SUM(total_balance)              AS total_aum
FROM   tiered
GROUP BY wealth_tier
ORDER BY total_aum DESC;

-- ─────────────────────────────────────────────
-- 4.5  RECURSIVE CTE  – employee org chart traversal
-- ─────────────────────────────────────────────

-- Build full org chart: who reports to whom, at every level
WITH RECURSIVE org_chart AS (
    -- Anchor: top-level employees (no manager)
    SELECT employee_id,
           first_name || ' ' || last_name AS full_name,
           job_title,
           manager_id,
           0                               AS depth,
           ARRAY[employee_id]              AS path,
           (first_name || ' ' || last_name) AS hierarchy_path
    FROM   employees
    WHERE  manager_id IS NULL

    UNION ALL

    -- Recursive: join each employee to their manager row
    SELECT e.employee_id,
           e.first_name || ' ' || e.last_name,
           e.job_title,
           e.manager_id,
           oc.depth + 1,
           oc.path || e.employee_id,
           oc.hierarchy_path || ' > ' || e.first_name || ' ' || e.last_name
    FROM   employees   e
    JOIN   org_chart   oc ON oc.employee_id = e.manager_id
    WHERE  NOT (e.employee_id = ANY(oc.path))   -- cycle guard
)
SELECT REPEAT('    ', depth) || full_name   AS org_tree,
       job_title,
       depth                                AS level
FROM   org_chart
ORDER BY path;

-- ─────────────────────────────────────────────
-- 4.6  RECURSIVE CTE  – loan amortization schedule
-- ─────────────────────────────────────────────

-- Generate first 12 months of amortization for Loan 1
WITH RECURSIVE amortization AS (
    -- Anchor: initial state of the loan
    SELECT 1                                    AS payment_num,
           (SELECT principal        FROM loans WHERE loan_id = 1) AS principal,
           (SELECT outstanding_balance FROM loans WHERE loan_id = 1) AS balance,
           (SELECT monthly_payment  FROM loans WHERE loan_id = 1) AS monthly_payment,
           (SELECT interest_rate    FROM loans WHERE loan_id = 1) AS annual_rate

    UNION ALL

    SELECT payment_num + 1,
           principal,
           ROUND(balance
               - (monthly_payment - ROUND(balance * annual_rate / 12, 2)),
               2),
           monthly_payment,
           annual_rate
    FROM   amortization
    WHERE  payment_num < 12
      AND  balance > 0
)
SELECT payment_num,
       ROUND(balance * annual_rate / 12, 2)              AS interest_portion,
       ROUND(monthly_payment - balance * annual_rate / 12, 2) AS principal_portion,
       monthly_payment                                    AS total_payment,
       balance                                            AS remaining_balance
FROM   amortization
ORDER BY payment_num;

-- ─────────────────────────────────────────────
-- 4.7  CTE + DELETE  (writable CTE)
-- ─────────────────────────────────────────────
-- NOTE: This is a pattern example — run in a transaction and ROLLBACK.

-- Identify duplicate fraud alerts (same transaction, same reason)
-- and select the ones we would delete
WITH ranked_alerts AS (
    SELECT alert_id,
           transaction_id,
           alert_reason,
           ROW_NUMBER() OVER (
               PARTITION BY transaction_id, alert_reason
               ORDER BY alert_id
           ) AS rn
    FROM   fraud_alerts
    WHERE  transaction_id IS NOT NULL
)
SELECT alert_id, transaction_id, alert_reason
FROM   ranked_alerts
WHERE  rn > 1;    -- these would be duplicates to remove

-- ─────────────────────────────────────────────
-- 4.8  MATERIALIZED CTE  (PostgreSQL 12+)
-- ─────────────────────────────────────────────
-- MATERIALIZED forces the CTE to be evaluated once and cached.
-- Useful when the CTE result is used multiple times.

WITH MATERIALIZED high_value_customers AS (
    SELECT customer_id
    FROM   customers
    WHERE  credit_score >= 750
)
SELECT 'loans'        AS product,
       COUNT(*)       AS count,
       SUM(l.outstanding_balance) AS total_balance
FROM   loans l
WHERE  l.customer_id IN (SELECT customer_id FROM high_value_customers)
UNION ALL
SELECT 'credit_cards',
       COUNT(*),
       SUM(cc.current_balance)
FROM   credit_cards cc
WHERE  cc.customer_id IN (SELECT customer_id FROM high_value_customers);
