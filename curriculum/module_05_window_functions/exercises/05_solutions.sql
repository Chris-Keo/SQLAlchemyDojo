-- =============================================================================
-- MODULE 5 – EXERCISE SOLUTIONS
-- =============================================================================

-- Exercise 1
SELECT transaction_id,
       transaction_date::DATE                         AS date,
       transaction_type,
       amount,
       SUM(amount) OVER (
           ORDER BY transaction_date
           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       )                                              AS running_total,
       ROUND(
           amount * 100.0 /
           NULLIF(SUM(amount) OVER (
               ORDER BY transaction_date
               ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
           ), 0),
           2
       )                                              AS pct_of_running_total
FROM   transactions
WHERE  account_id = 1
ORDER BY transaction_date;

-- Exercise 2
SELECT l.loan_type,
       c.first_name || ' ' || c.last_name  AS customer_name,
       l.outstanding_balance,
       RANK()       OVER (
           PARTITION BY l.loan_type
           ORDER BY l.outstanding_balance DESC
       )                                   AS rank_with_gaps,
       DENSE_RANK() OVER (
           PARTITION BY l.loan_type
           ORDER BY l.outstanding_balance DESC
       )                                   AS rank_no_gaps
FROM   loans     l
JOIN   customers c ON c.customer_id = l.customer_id
ORDER BY l.loan_type, l.outstanding_balance DESC;

-- Exercise 3
SELECT account_id,
       transaction_id,
       transaction_date::DATE              AS date,
       transaction_type,
       amount,
       prev_amount,
       next_amount,
       CASE WHEN amount > prev_amount * 3 THEN 'LARGE_JUMP' ELSE '' END AS flag
FROM (
    SELECT t.account_id,
           t.transaction_id,
           t.transaction_date,
           t.transaction_type,
           t.amount,
           LAG(t.amount)  OVER (PARTITION BY t.account_id ORDER BY t.transaction_date) AS prev_amount,
           LEAD(t.amount) OVER (PARTITION BY t.account_id ORDER BY t.transaction_date) AS next_amount
    FROM   transactions t
    JOIN   accounts     a ON a.account_id = t.account_id
    WHERE  a.account_type = 'checking'
) sub
WHERE prev_amount IS NOT NULL
ORDER BY account_id, transaction_date;

-- Exercise 4
SELECT account_id,
       account_type,
       balance,
       NTILE(5) OVER (ORDER BY balance)  AS quintile,
       MIN(balance) OVER (
           PARTITION BY NTILE(5) OVER (ORDER BY balance)
       )                                 AS quintile_min,
       MAX(balance) OVER (
           PARTITION BY NTILE(5) OVER (ORDER BY balance)
       )                                 AS quintile_max
FROM   accounts
WHERE  is_active = TRUE
ORDER BY balance;

-- Exercise 5
WITH monthly AS (
    SELECT DATE_TRUNC('month', transaction_date)::DATE  AS month,
           SUM(amount)                                   AS monthly_total
    FROM   transactions
    WHERE  transaction_date >= '2025-01-01'
      AND  transaction_date <  '2026-01-01'
    GROUP BY DATE_TRUNC('month', transaction_date)
)
SELECT month,
       monthly_total,
       SUM(monthly_total) OVER (
           ORDER BY month
           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       )                                AS ytd_total,
       ROUND(
           monthly_total * 100.0 /
           NULLIF(SUM(monthly_total) OVER (
               ORDER BY month
               ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
           ), 0),
           1
       )                                AS pct_of_ytd
FROM   monthly
ORDER BY month;
