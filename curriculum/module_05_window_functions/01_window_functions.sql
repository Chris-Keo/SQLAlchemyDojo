-- =============================================================================
-- MODULE 5: WINDOW FUNCTIONS
-- The most powerful analytical feature in PostgreSQL SQL
-- OVER(), PARTITION BY, ORDER BY, frame clauses,
-- ROW_NUMBER, RANK, DENSE_RANK, NTILE, LAG, LEAD,
-- FIRST_VALUE, LAST_VALUE, NTH_VALUE, running totals
-- =============================================================================

-- ─────────────────────────────────────────────
-- ANATOMY OF A WINDOW FUNCTION
-- ─────────────────────────────────────────────
-- function_name([args])
--     OVER (
--         [PARTITION BY col1, col2, ...]
--         [ORDER BY col3 ASC/DESC]
--         [ROWS/RANGE BETWEEN frame_start AND frame_end]
--     )
--
-- Key rule: window functions do NOT collapse rows (unlike GROUP BY).

-- ─────────────────────────────────────────────
-- 5.1  ROW_NUMBER  – unique sequential number per partition
-- ─────────────────────────────────────────────

-- Rank each customer's accounts by balance (within that customer)
SELECT a.account_id,
       c.first_name || ' ' || c.last_name       AS customer_name,
       a.account_type,
       a.balance,
       ROW_NUMBER() OVER (
           PARTITION BY a.customer_id
           ORDER BY a.balance DESC
       )                                         AS account_rank
FROM   accounts  a
JOIN   customers c ON c.customer_id = a.customer_id
ORDER BY customer_name, account_rank;

-- ─────────────────────────────────────────────
-- 5.2  RANK vs DENSE_RANK  – handling ties
-- ─────────────────────────────────────────────

-- Rank credit card balances (ties handled differently)
SELECT cc.card_id,
       c.first_name || ' ' || c.last_name  AS customer_name,
       cc.card_type,
       cc.current_balance,
       RANK()       OVER (ORDER BY cc.current_balance DESC) AS rank_with_gaps,
       DENSE_RANK() OVER (ORDER BY cc.current_balance DESC) AS rank_no_gaps,
       ROW_NUMBER() OVER (ORDER BY cc.current_balance DESC) AS row_num
FROM   credit_cards cc
JOIN   customers    c  ON c.customer_id = cc.customer_id
ORDER BY cc.current_balance DESC;

-- ─────────────────────────────────────────────
-- 5.3  NTILE  – divide rows into N equal buckets
-- ─────────────────────────────────────────────

-- Divide customers into 4 credit score quartiles
SELECT first_name || ' ' || last_name  AS customer_name,
       credit_score,
       NTILE(4) OVER (ORDER BY credit_score DESC) AS credit_quartile,
       CASE NTILE(4) OVER (ORDER BY credit_score DESC)
           WHEN 1 THEN 'Excellent'
           WHEN 2 THEN 'Good'
           WHEN 3 THEN 'Fair'
           WHEN 4 THEN 'Poor'
       END AS credit_tier
FROM   customers
WHERE  credit_score IS NOT NULL
ORDER BY credit_score DESC;

-- ─────────────────────────────────────────────
-- 5.4  RUNNING TOTALS with SUM OVER
-- ─────────────────────────────────────────────

-- Cumulative deposit total for account 1 over time
SELECT transaction_id,
       transaction_date::DATE         AS date,
       amount,
       SUM(amount) OVER (
           ORDER BY transaction_date
           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       )                              AS running_total
FROM   transactions
WHERE  account_id = 1
  AND  transaction_type = 'deposit'
ORDER BY transaction_date;

-- Running balance for account 1 (every transaction)
SELECT transaction_id,
       transaction_date::DATE                            AS date,
       transaction_type,
       CASE WHEN transaction_type IN ('deposit','transfer_in','interest','refund')
            THEN amount ELSE -amount END                 AS signed_amount,
       balance_after
FROM   transactions
WHERE  account_id = 1
ORDER BY transaction_date;

-- ─────────────────────────────────────────────
-- 5.5  MOVING AVERAGES
-- ─────────────────────────────────────────────

-- 3-month rolling average of monthly deposits
WITH monthly AS (
    SELECT DATE_TRUNC('month', transaction_date)::DATE  AS month,
           SUM(amount)                                   AS total_deposits
    FROM   transactions
    WHERE  transaction_type = 'deposit'
    GROUP BY DATE_TRUNC('month', transaction_date)
)
SELECT month,
       total_deposits,
       ROUND(AVG(total_deposits) OVER (
           ORDER BY month
           ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
       ), 2)                          AS rolling_3mo_avg
FROM   monthly
ORDER BY month;

-- ─────────────────────────────────────────────
-- 5.6  LAG  – access previous row's value
-- ─────────────────────────────────────────────

-- Month-over-month change in total transactions
WITH monthly AS (
    SELECT DATE_TRUNC('month', transaction_date)::DATE  AS month,
           COUNT(*)                                      AS tx_count,
           SUM(amount)                                   AS total_amount
    FROM   transactions
    GROUP BY DATE_TRUNC('month', transaction_date)
)
SELECT month,
       tx_count,
       total_amount,
       LAG(total_amount) OVER (ORDER BY month)          AS prev_month_amount,
       total_amount
           - LAG(total_amount) OVER (ORDER BY month)    AS mom_change,
       ROUND(
           (total_amount - LAG(total_amount) OVER (ORDER BY month))
           / NULLIF(LAG(total_amount) OVER (ORDER BY month), 0) * 100,
           1
       )                                                AS mom_pct_change
FROM   monthly
ORDER BY month;

-- Compare each transaction to the previous one on the same account
SELECT account_id,
       transaction_id,
       transaction_date::DATE                                    AS date,
       transaction_type,
       amount,
       LAG(amount) OVER (
           PARTITION BY account_id
           ORDER BY transaction_date
       )                                                        AS prev_amount,
       amount - LAG(amount) OVER (
           PARTITION BY account_id
           ORDER BY transaction_date
       )                                                        AS change
FROM   transactions
ORDER BY account_id, transaction_date;

-- ─────────────────────────────────────────────
-- 5.7  LEAD  – access next row's value
-- ─────────────────────────────────────────────

-- For each loan payment, show what the next payment will be
SELECT lp.payment_id,
       lp.loan_id,
       lp.payment_date,
       lp.amount_paid,
       lp.principal_portion,
       lp.interest_portion,
       LEAD(lp.interest_portion) OVER (
           PARTITION BY lp.loan_id
           ORDER BY lp.payment_date
       )                                    AS next_interest,
       interest_portion
           - LEAD(interest_portion) OVER (
               PARTITION BY loan_id
               ORDER BY payment_date
             )                              AS interest_reduction
FROM   loan_payments lp
ORDER BY lp.loan_id, lp.payment_date;

-- ─────────────────────────────────────────────
-- 5.8  FIRST_VALUE / LAST_VALUE / NTH_VALUE
-- ─────────────────────────────────────────────

-- For each account type, show cheapest and most expensive balance
SELECT a.account_id,
       a.account_type,
       a.balance,
       FIRST_VALUE(a.balance) OVER (
           PARTITION BY a.account_type
           ORDER BY a.balance DESC
       )                                   AS max_balance_in_type,
       LAST_VALUE(a.balance) OVER (
           PARTITION BY a.account_type
           ORDER BY a.balance DESC
           ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
       )                                   AS min_balance_in_type,
       ROUND(AVG(a.balance) OVER (
           PARTITION BY a.account_type
       ), 2)                               AS avg_balance_in_type
FROM   accounts a
ORDER BY a.account_type, a.balance DESC;

-- ─────────────────────────────────────────────
-- 5.9  PERCENT_RANK and CUME_DIST
-- ─────────────────────────────────────────────

-- Where does each customer's credit score fall as a percentile?
SELECT first_name || ' ' || last_name   AS customer_name,
       credit_score,
       ROUND(PERCENT_RANK() OVER (ORDER BY credit_score) * 100, 1) AS percentile_rank,
       ROUND(CUME_DIST()    OVER (ORDER BY credit_score) * 100, 1) AS cumulative_pct
FROM   customers
WHERE  credit_score IS NOT NULL
ORDER BY credit_score DESC;

-- ─────────────────────────────────────────────
-- 5.10  WINDOW FRAME CLAUSES
-- ─────────────────────────────────────────────
-- ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW  → running total
-- ROWS BETWEEN 2 PRECEDING AND CURRENT ROW          → 3-row moving window
-- ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING  → remaining total
-- RANGE vs ROWS: RANGE treats equal ORDER BY values as one group

-- Remaining deposits after each transaction (reverse cumulative)
SELECT transaction_id,
       transaction_date::DATE              AS date,
       amount,
       SUM(amount) OVER (
           ORDER BY transaction_date DESC
           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       )                                   AS remaining_from_last
FROM   transactions
WHERE  account_id        = 1
  AND  transaction_type  = 'deposit'
ORDER BY transaction_date DESC;

-- ─────────────────────────────────────────────
-- 5.11  COMBINING MULTIPLE WINDOW FUNCTIONS
-- ─────────────────────────────────────────────

-- Comprehensive credit card spending analysis
SELECT c.first_name || ' ' || c.last_name           AS customer_name,
       cc.card_type,
       cc.current_balance,
       cc.credit_limit,
       ROUND(cc.current_balance / cc.credit_limit * 100, 1) AS utilization_pct,
       RANK()       OVER (ORDER BY cc.current_balance DESC)  AS balance_rank,
       NTILE(3)     OVER (ORDER BY cc.current_balance DESC)  AS balance_tercile,
       ROUND(AVG(cc.current_balance) OVER (), 2)             AS avg_all_balances,
       cc.current_balance
           - ROUND(AVG(cc.current_balance) OVER (), 2)       AS vs_avg
FROM   credit_cards cc
JOIN   customers    c  ON c.customer_id = cc.customer_id
ORDER BY cc.current_balance DESC;

-- ─────────────────────────────────────────────
-- 5.12  WINDOW FUNCTION WITH NAMED WINDOW (WINDOW clause)
-- ─────────────────────────────────────────────

-- Reuse the same window definition across multiple functions
SELECT transaction_id,
       account_id,
       transaction_date::DATE  AS date,
       amount,
       SUM(amount)    OVER w   AS running_total,
       AVG(amount)    OVER w   AS running_avg,
       COUNT(*)       OVER w   AS running_count,
       MAX(amount)    OVER w   AS running_max
FROM   transactions
WHERE  account_id = 1
WINDOW w AS (
    ORDER BY transaction_date
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
)
ORDER BY transaction_date;
