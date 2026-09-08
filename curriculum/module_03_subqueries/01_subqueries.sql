-- =============================================================================
-- MODULE 3: SUBQUERIES & DERIVED TABLES
-- Scalar subqueries, correlated subqueries, EXISTS, IN, derived tables
-- =============================================================================

-- ─────────────────────────────────────────────
-- 3.1  SCALAR SUBQUERY  – returns one value
-- ─────────────────────────────────────────────

-- Compare each account balance to the overall average
SELECT account_id,
       account_type,
       balance,
       ROUND((SELECT AVG(balance) FROM accounts), 2)   AS overall_avg,
       balance - (SELECT AVG(balance) FROM accounts)   AS diff_from_avg
FROM   accounts
ORDER BY diff_from_avg DESC;

-- Customers whose credit score is above the bank-wide average
SELECT first_name,
       last_name,
       credit_score,
       ROUND((SELECT AVG(credit_score) FROM customers WHERE credit_score IS NOT NULL), 0) AS bank_avg
FROM   customers
WHERE  credit_score > (SELECT AVG(credit_score) FROM customers)
ORDER BY credit_score DESC;

-- ─────────────────────────────────────────────
-- 3.2  SUBQUERY IN FROM  (derived table)
-- ─────────────────────────────────────────────

-- Average transactions per account (using a subquery to pre-aggregate)
SELECT ROUND(AVG(tx_count), 2) AS avg_transactions_per_account
FROM (
    SELECT account_id,
           COUNT(*) AS tx_count
    FROM   transactions
    GROUP BY account_id
) account_totals;

-- Per-customer total balance across all their accounts
SELECT customer_id,
       full_name,
       total_balance
FROM (
    SELECT c.customer_id,
           c.first_name || ' ' || c.last_name AS full_name,
           SUM(a.balance)                      AS total_balance
    FROM   customers c
    JOIN   accounts  a ON a.customer_id = c.customer_id
    GROUP BY c.customer_id, c.first_name, c.last_name
) customer_wealth
WHERE total_balance > 50000
ORDER BY total_balance DESC;

-- ─────────────────────────────────────────────
-- 3.3  SUBQUERY IN WHERE  (IN / NOT IN)
-- ─────────────────────────────────────────────

-- Customers who have at least one delinquent or defaulted loan
SELECT customer_id,
       first_name || ' ' || last_name AS customer_name,
       credit_score
FROM   customers
WHERE  customer_id IN (
    SELECT customer_id
    FROM   loans
    WHERE  status IN ('delinquent', 'defaulted')
)
ORDER BY credit_score;

-- Accounts that have NEVER had a transaction
SELECT account_id, account_type, balance, opened_date
FROM   accounts
WHERE  account_id NOT IN (
    SELECT DISTINCT account_id
    FROM   transactions
)
ORDER BY opened_date;

-- ─────────────────────────────────────────────
-- 3.4  EXISTS / NOT EXISTS  (preferred over IN for NULLs + performance)
-- ─────────────────────────────────────────────

-- Customers who have at least one active credit card
SELECT c.customer_id,
       c.first_name || ' ' || c.last_name AS customer_name
FROM   customers c
WHERE  EXISTS (
    SELECT 1
    FROM   credit_cards cc
    WHERE  cc.customer_id = c.customer_id
      AND  cc.is_active   = TRUE
)
ORDER BY c.last_name;

-- Branches with NO active loans originated there
SELECT b.branch_id,
       b.branch_name,
       b.city
FROM   branches b
WHERE  NOT EXISTS (
    SELECT 1
    FROM   loans l
    WHERE  l.branch_id = b.branch_id
      AND  l.status    = 'active'
)
ORDER BY b.branch_name;

-- ─────────────────────────────────────────────
-- 3.5  CORRELATED SUBQUERY
-- ─────────────────────────────────────────────

-- For each account, show the most recent transaction amount
SELECT a.account_id,
       a.account_type,
       a.balance,
       (
           SELECT t.amount
           FROM   transactions t
           WHERE  t.account_id = a.account_id
           ORDER BY t.transaction_date DESC
           LIMIT  1
       ) AS last_transaction_amount
FROM   accounts a
ORDER BY a.account_id;

-- Customers whose total balance is above the average for their state
SELECT c.customer_id,
       c.first_name || ' ' || c.last_name AS customer_name,
       c.state,
       SUM(a.balance)                      AS total_balance
FROM   customers c
JOIN   accounts  a ON a.customer_id = c.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name, c.state
HAVING SUM(a.balance) > (
    SELECT AVG(a2.balance)
    FROM   customers c2
    JOIN   accounts  a2 ON a2.customer_id = c2.customer_id
    WHERE  c2.state = c.state
)
ORDER BY c.state, total_balance DESC;

-- ─────────────────────────────────────────────
-- 3.6  SUBQUERY WITH ANY / ALL
-- ─────────────────────────────────────────────

-- Loans with a rate higher than ANY mortgage rate
SELECT loan_id, loan_type, interest_rate
FROM   loans
WHERE  interest_rate > ANY (
    SELECT interest_rate
    FROM   loans
    WHERE  loan_type = 'mortgage'
)
  AND  loan_type != 'mortgage'
ORDER BY interest_rate DESC;

-- Customers with a credit score higher than ALL customers in Miami
SELECT first_name,
       last_name,
       city,
       credit_score
FROM   customers
WHERE  credit_score > ALL (
    SELECT credit_score
    FROM   customers
    WHERE  city = 'Miami'
      AND  credit_score IS NOT NULL
)
ORDER BY credit_score DESC;

-- ─────────────────────────────────────────────
-- 3.7  MULTI-LEVEL SUBQUERIES
-- ─────────────────────────────────────────────

-- Customers in the top 20% by total account balance
SELECT customer_name,
       total_balance,
       balance_rank,
       total_customers
FROM (
    SELECT customer_name,
           total_balance,
           RANK() OVER (ORDER BY total_balance DESC)   AS balance_rank,
           COUNT(*) OVER ()                             AS total_customers
    FROM (
        SELECT c.first_name || ' ' || c.last_name AS customer_name,
               SUM(a.balance)                      AS total_balance
        FROM   customers c
        JOIN   accounts  a ON a.customer_id = c.customer_id
        GROUP BY c.customer_id, c.first_name, c.last_name
    ) customer_totals
) ranked
WHERE balance_rank <= CEIL(total_customers * 0.20)
ORDER BY total_balance DESC;
