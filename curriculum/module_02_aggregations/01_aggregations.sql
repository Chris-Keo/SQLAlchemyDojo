-- =============================================================================
-- MODULE 2: AGGREGATIONS
-- GROUP BY, HAVING, COUNT, SUM, AVG, MIN, MAX, ROLLUP, CUBE
-- =============================================================================

-- ─────────────────────────────────────────────
-- 2.1  COUNT
-- ─────────────────────────────────────────────

-- Total number of customers
SELECT COUNT(*) AS total_customers
FROM   customers;

-- Number of customers per state
SELECT state,
       COUNT(*) AS customer_count
FROM   customers
GROUP BY state
ORDER BY customer_count DESC;

-- Number of accounts per type
SELECT account_type,
       COUNT(*)                  AS account_count,
       ROUND(AVG(balance), 2)    AS avg_balance
FROM   accounts
GROUP BY account_type
ORDER BY account_count DESC;

-- ─────────────────────────────────────────────
-- 2.2  SUM
-- ─────────────────────────────────────────────

-- Total deposits by month in 2025
SELECT DATE_TRUNC('month', transaction_date)::DATE  AS month,
       SUM(amount)                                   AS total_deposits,
       COUNT(*)                                      AS transaction_count
FROM   transactions
WHERE  transaction_type = 'deposit'
  AND  transaction_date >= '2025-01-01'
GROUP BY DATE_TRUNC('month', transaction_date)
ORDER BY month;

-- Total balance held at each branch
SELECT b.branch_name,
       b.city,
       b.state,
       COUNT(a.account_id)         AS num_accounts,
       SUM(a.balance)              AS total_deposits
FROM   branches b
JOIN   accounts a ON a.branch_id = b.branch_id
GROUP BY b.branch_id, b.branch_name, b.city, b.state
ORDER BY total_deposits DESC;

-- ─────────────────────────────────────────────
-- 2.3  AVG, MIN, MAX
-- ─────────────────────────────────────────────

-- Credit score statistics by state
SELECT state,
       COUNT(*)                              AS customers,
       ROUND(AVG(credit_score), 0)           AS avg_score,
       MIN(credit_score)                     AS min_score,
       MAX(credit_score)                     AS max_score,
       MAX(credit_score) - MIN(credit_score) AS score_range
FROM   customers
WHERE  credit_score IS NOT NULL
GROUP BY state
ORDER BY avg_score DESC;

-- Average, min, max loan balance by loan type
SELECT loan_type,
       COUNT(*)                                       AS loan_count,
       ROUND(AVG(outstanding_balance), 2)             AS avg_balance,
       MIN(outstanding_balance)                       AS min_balance,
       MAX(outstanding_balance)                       AS max_balance,
       SUM(outstanding_balance)                       AS total_exposure
FROM   loans
WHERE  status = 'active'
GROUP BY loan_type
ORDER BY total_exposure DESC;

-- ─────────────────────────────────────────────
-- 2.4  HAVING  – filter after aggregation
-- ─────────────────────────────────────────────

-- States where average credit score is below 700
SELECT state,
       ROUND(AVG(credit_score), 0) AS avg_score,
       COUNT(*)                    AS customers
FROM   customers
WHERE  credit_score IS NOT NULL
GROUP BY state
HAVING AVG(credit_score) < 700
ORDER BY avg_score;

-- Customers who made more than 3 transactions in 2025
SELECT c.first_name || ' ' || c.last_name AS customer_name,
       COUNT(t.transaction_id)            AS tx_count,
       SUM(t.amount)                      AS total_activity
FROM   customers    c
JOIN   accounts     a ON a.customer_id = c.customer_id
JOIN   transactions t ON t.account_id  = a.account_id
WHERE  t.transaction_date >= '2025-01-01'
GROUP BY c.customer_id, c.first_name, c.last_name
HAVING COUNT(t.transaction_id) > 3
ORDER BY tx_count DESC;

-- Branches where total account balances exceed $200,000
SELECT b.branch_name,
       b.city,
       COUNT(a.account_id) AS accounts,
       SUM(a.balance)      AS total_balance
FROM   branches b
JOIN   accounts a ON a.branch_id = b.branch_id
GROUP BY b.branch_id, b.branch_name, b.city
HAVING SUM(a.balance) > 200000
ORDER BY total_balance DESC;

-- ─────────────────────────────────────────────
-- 2.5  COUNT DISTINCT vs COUNT
-- ─────────────────────────────────────────────

-- How many unique customers made a transaction (vs total transactions)?
SELECT COUNT(DISTINCT a.customer_id) AS unique_customers,
       COUNT(t.transaction_id)       AS total_transactions
FROM   transactions t
JOIN   accounts     a ON a.account_id = t.account_id;

-- Unique merchant categories in credit card transactions
SELECT COUNT(DISTINCT merchant_category) AS unique_categories
FROM   credit_card_transactions;

-- ─────────────────────────────────────────────
-- 2.6  FILTER INSIDE AGGREGATES (PostgreSQL)
-- ─────────────────────────────────────────────

-- Count deposits and withdrawals in a single row per account
SELECT account_id,
       COUNT(*) FILTER (WHERE transaction_type = 'deposit')    AS deposits,
       COUNT(*) FILTER (WHERE transaction_type = 'withdrawal') AS withdrawals,
       COUNT(*) FILTER (WHERE transaction_type = 'fee')        AS fees,
       SUM(amount) FILTER (WHERE transaction_type = 'deposit') AS total_deposited,
       SUM(amount) FILTER (WHERE transaction_type IN ('withdrawal','fee')) AS total_debited
FROM   transactions
GROUP BY account_id
ORDER BY account_id;

-- ─────────────────────────────────────────────
-- 2.7  ROLLUP  – subtotals + grand total
-- ─────────────────────────────────────────────

-- Transaction totals by state and account type, with subtotals
SELECT b.state,
       a.account_type,
       COUNT(t.transaction_id) AS tx_count,
       SUM(t.amount)           AS total_amount
FROM   transactions t
JOIN   accounts     a ON a.account_id = t.account_id
JOIN   branches     b ON b.branch_id  = a.branch_id
GROUP BY ROLLUP(b.state, a.account_type)
ORDER BY b.state NULLS LAST,
         a.account_type NULLS LAST;

-- ─────────────────────────────────────────────
-- 2.8  CUBE  – all combinations of dimensions
-- ─────────────────────────────────────────────

-- Loan summary by type and status (all cross-combinations)
SELECT loan_type,
       status,
       COUNT(*)                      AS loan_count,
       ROUND(AVG(outstanding_balance), 2) AS avg_balance
FROM   loans
GROUP BY CUBE(loan_type, status)
ORDER BY loan_type NULLS LAST,
         status    NULLS LAST;

-- ─────────────────────────────────────────────
-- 2.9  GROUPING SETS  – explicit combinations
-- ─────────────────────────────────────────────

-- Transaction summary: by type only, by channel only, and grand total
SELECT transaction_type,
       channel,
       COUNT(*)    AS tx_count,
       SUM(amount) AS total_amount
FROM   transactions
GROUP BY GROUPING SETS (
    (transaction_type),
    (channel),
    ()        -- grand total
)
ORDER BY transaction_type NULLS LAST,
         channel           NULLS LAST;

-- ─────────────────────────────────────────────
-- 2.10  REAL BANKING REPORT: Monthly P&L Summary
-- ─────────────────────────────────────────────

-- Monthly fee income vs interest paid out (2025)
SELECT DATE_TRUNC('month', transaction_date)::DATE        AS month,
       SUM(amount) FILTER (WHERE transaction_type = 'fee')      AS fee_income,
       SUM(amount) FILTER (WHERE transaction_type = 'interest')  AS interest_paid,
       COUNT(*) FILTER (WHERE transaction_type = 'fee')          AS fee_count
FROM   transactions
WHERE  transaction_date >= '2025-01-01'
GROUP BY DATE_TRUNC('month', transaction_date)
ORDER BY month;
