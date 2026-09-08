-- =============================================================================
-- MODULE 1: SQL FOUNDATIONS
-- Lesson 1 – SELECT, FROM, WHERE, ORDER BY, LIMIT
-- =============================================================================
-- Goal: Master the mechanics of reading data from a PostgreSQL database.
-- Dataset: First National Bank (banking schema)
-- =============================================================================

-- ─────────────────────────────────────────────
-- 1.1  BASIC SELECT
-- ─────────────────────────────────────────────

-- Retrieve every column from the customers table
SELECT *
FROM   customers;

-- Retrieve specific columns
SELECT customer_id,
       first_name,
       last_name,
       email
FROM   customers;

-- ─────────────────────────────────────────────
-- 1.2  COLUMN ALIASES  (AS keyword)
-- ─────────────────────────────────────────────

SELECT customer_id                                    AS id,
       first_name || ' ' || last_name                 AS full_name,
       email,
       joined_date                                    AS member_since
FROM   customers;

-- ─────────────────────────────────────────────
-- 1.3  FILTERING WITH WHERE
-- ─────────────────────────────────────────────

-- All customers in New York
SELECT first_name, last_name, city, state
FROM   customers
WHERE  state = 'NY';

-- Customers with a credit score above 750
SELECT first_name, last_name, credit_score
FROM   customers
WHERE  credit_score > 750
ORDER BY credit_score DESC;

-- Accounts with a balance over $50,000
SELECT account_id, account_number, account_type, balance
FROM   accounts
WHERE  balance > 50000
ORDER BY balance DESC;

-- ─────────────────────────────────────────────
-- 1.4  MULTIPLE CONDITIONS  (AND / OR / NOT)
-- ─────────────────────────────────────────────

-- Active checking accounts with balance between $5,000 and $25,000
SELECT account_id, account_type, balance
FROM   accounts
WHERE  account_type = 'checking'
  AND  is_active    = TRUE
  AND  balance BETWEEN 5000 AND 25000
ORDER BY balance DESC;

-- Customers in NY or CA
SELECT first_name, last_name, state, city
FROM   customers
WHERE  state IN ('NY', 'CA')
ORDER BY state, last_name;

-- ─────────────────────────────────────────────
-- 1.5  PATTERN MATCHING  (LIKE / ILIKE)
-- ─────────────────────────────────────────────

-- Customers whose last name starts with 'G'
SELECT first_name, last_name
FROM   customers
WHERE  last_name LIKE 'G%';

-- Case-insensitive: merchants containing 'food'
SELECT DISTINCT merchant_name
FROM   transactions
WHERE  merchant_name ILIKE '%food%';

-- ─────────────────────────────────────────────
-- 1.6  NULL HANDLING
-- ─────────────────────────────────────────────

-- Employees who do NOT have a manager (top of hierarchy)
SELECT employee_id, first_name, last_name, job_title
FROM   employees
WHERE  manager_id IS NULL;

-- Accounts without a closed_date (still open)
SELECT account_id, account_number, opened_date
FROM   accounts
WHERE  closed_date IS NULL;

-- Use COALESCE to replace NULL with a default
SELECT employee_id,
       first_name || ' ' || last_name                 AS name,
       COALESCE(manager_id::TEXT, 'No Manager')       AS reports_to
FROM   employees
ORDER BY manager_id NULLS FIRST;

-- ─────────────────────────────────────────────
-- 1.7  ORDER BY and LIMIT
-- ─────────────────────────────────────────────

-- Top 5 highest-balance accounts
SELECT account_id, account_number, account_type, balance
FROM   accounts
ORDER BY balance DESC
LIMIT  5;

-- Most recent 10 transactions
SELECT transaction_id, account_id, transaction_type, amount, transaction_date
FROM   transactions
ORDER BY transaction_date DESC
LIMIT  10;

-- Bottom 5 credit scores
SELECT first_name, last_name, credit_score
FROM   customers
WHERE  credit_score IS NOT NULL
ORDER BY credit_score ASC
LIMIT  5;

-- ─────────────────────────────────────────────
-- 1.8  DISTINCT
-- ─────────────────────────────────────────────

-- What states do our customers come from?
SELECT DISTINCT state
FROM   customers
ORDER BY state;

-- What transaction channels exist?
SELECT DISTINCT channel
FROM   transactions
ORDER BY channel;

-- ─────────────────────────────────────────────
-- 1.9  BASIC ARITHMETIC IN SELECT
-- ─────────────────────────────────────────────

-- Monthly interest earned on each savings account
SELECT account_id,
       account_type,
       balance,
       interest_rate,
       ROUND(balance * interest_rate / 12, 2)         AS monthly_interest
FROM   accounts
WHERE  account_type IN ('savings', 'money_market', 'cd')
ORDER BY monthly_interest DESC;

-- Outstanding loan as a % of original principal
SELECT loan_id,
       loan_type,
       principal,
       outstanding_balance,
       ROUND(outstanding_balance / principal * 100, 1) AS pct_remaining
FROM   loans
ORDER BY pct_remaining DESC;

-- ─────────────────────────────────────────────
-- 1.10  CASTING DATA TYPES
-- ─────────────────────────────────────────────

-- Format balance as currency-friendly text
SELECT account_id,
       '$' || TO_CHAR(balance, 'FM999,999,999.00')    AS balance_formatted
FROM   accounts
ORDER BY balance DESC
LIMIT  10;

-- Extract year a customer joined
SELECT first_name,
       last_name,
       EXTRACT(YEAR FROM joined_date)::INT            AS joined_year
FROM   customers
ORDER BY joined_year;
