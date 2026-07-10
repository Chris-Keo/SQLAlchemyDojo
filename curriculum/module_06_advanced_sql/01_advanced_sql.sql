-- =============================================================================
-- MODULE 6: ADVANCED SQL
-- Date/Time, String functions, Regular Expressions, LATERAL,
-- JSON, CASE, UNION/INTERSECT/EXCEPT, PIVOT simulation
-- =============================================================================

-- ─────────────────────────────────────────────
-- 6.1  DATE & TIME FUNCTIONS
-- ─────────────────────────────────────────────

-- Age of each customer relationship (years as a customer)
SELECT first_name || ' ' || last_name           AS customer_name,
       joined_date,
       AGE(CURRENT_DATE, joined_date)           AS tenure,
       EXTRACT(YEAR FROM AGE(CURRENT_DATE, joined_date))::INT AS years_as_customer,
       DATE_PART('day', NOW() - joined_date::TIMESTAMPTZ)::INT AS days_as_customer
FROM   customers
ORDER BY joined_date;

-- Transactions grouped by day-of-week (0=Sun … 6=Sat)
SELECT TO_CHAR(transaction_date, 'Day')         AS day_of_week,
       EXTRACT(DOW FROM transaction_date)::INT  AS dow_num,
       COUNT(*)                                 AS tx_count,
       SUM(amount)                              AS total_amount
FROM   transactions
GROUP BY TO_CHAR(transaction_date, 'Day'),
         EXTRACT(DOW FROM transaction_date)
ORDER BY dow_num;

-- Transactions in the last 90 days
SELECT transaction_id, transaction_date, amount
FROM   transactions
WHERE  transaction_date >= NOW() - INTERVAL '90 days'
ORDER BY transaction_date DESC;

-- Hours between transaction and account opening (on-boarding activity)
SELECT t.transaction_id,
       a.opened_date,
       t.transaction_date,
       EXTRACT(EPOCH FROM (t.transaction_date - a.opened_date::TIMESTAMPTZ)) / 3600.0 AS hours_after_open
FROM   transactions t
JOIN   accounts     a ON a.account_id = t.account_id
WHERE  t.transaction_date < a.opened_date::TIMESTAMPTZ + INTERVAL '30 days'
ORDER BY hours_after_open;

-- ─────────────────────────────────────────────
-- 6.2  STRING FUNCTIONS
-- ─────────────────────────────────────────────

-- Mask account number: show only last 4 digits
SELECT account_id,
       account_number,
       REPEAT('*', LENGTH(account_number) - 4) ||
           RIGHT(account_number, 4)            AS masked_number
FROM   accounts;

-- Standardize merchant names to Title Case and strip whitespace
SELECT DISTINCT
       merchant_name,
       INITCAP(TRIM(merchant_name))            AS clean_merchant
FROM   transactions
WHERE  merchant_name IS NOT NULL;

-- Split customer full name into parts
SELECT customer_id,
       first_name || ' ' || last_name          AS full_name,
       SPLIT_PART(email, '@', 1)               AS email_username,
       SPLIT_PART(email, '@', 2)               AS email_domain,
       LENGTH(first_name || last_name)         AS name_length
FROM   customers
ORDER BY name_length DESC;

-- ─────────────────────────────────────────────
-- 6.3  REGULAR EXPRESSIONS
-- ─────────────────────────────────────────────

-- Find merchants that look like airline names (contain 'Air' or 'Airlines')
SELECT DISTINCT merchant_name
FROM   credit_card_transactions
WHERE  merchant_name ~* 'air(lines?)?'
ORDER BY merchant_name;

-- Extract domain from email using regexp_replace
SELECT email,
       REGEXP_REPLACE(email, '^[^@]+@', '') AS domain
FROM   customers
ORDER BY domain;

-- Find accounts whose number contains repeating patterns
SELECT account_number
FROM   accounts
WHERE  account_number ~ '(.)\1{3,}'   -- 4+ of the same digit in a row
ORDER BY account_number;

-- ─────────────────────────────────────────────
-- 6.4  CASE EXPRESSIONS
-- ─────────────────────────────────────────────

-- Credit risk tier from credit_score
SELECT customer_id,
       first_name || ' ' || last_name         AS customer_name,
       credit_score,
       CASE
           WHEN credit_score >= 800 THEN 'Exceptional'
           WHEN credit_score >= 740 THEN 'Very Good'
           WHEN credit_score >= 670 THEN 'Good'
           WHEN credit_score >= 580 THEN 'Fair'
           ELSE                          'Poor'
       END AS risk_tier
FROM   customers
WHERE  credit_score IS NOT NULL
ORDER BY credit_score DESC;

-- Transaction risk flag: large amounts via unusual channels at odd hours
SELECT transaction_id,
       transaction_date,
       amount,
       channel,
       CASE
           WHEN amount > 5000
                AND channel IN ('atm', 'online')
                AND EXTRACT(HOUR FROM transaction_date) NOT BETWEEN 8 AND 20
               THEN 'HIGH RISK'
           WHEN amount > 1000
                AND EXTRACT(HOUR FROM transaction_date) NOT BETWEEN 6 AND 22
               THEN 'MEDIUM RISK'
           ELSE 'NORMAL'
       END AS risk_flag
FROM   transactions
ORDER BY risk_flag DESC, amount DESC;

-- ─────────────────────────────────────────────
-- 6.5  UNION / INTERSECT / EXCEPT
-- ─────────────────────────────────────────────

-- All monetary activity (bank + credit card) in one result set
SELECT 'bank'       AS source,
       t.transaction_id::TEXT AS id,
       t.transaction_date,
       t.amount,
       t.merchant_name,
       t.merchant_category
FROM   transactions t
UNION ALL
SELECT 'credit_card',
       ct.cc_transaction_id::TEXT,
       ct.transaction_date,
       ct.amount,
       ct.merchant_name,
       ct.merchant_category
FROM   credit_card_transactions ct
ORDER BY transaction_date DESC
LIMIT  30;

-- Customers with BOTH a loan AND a credit card
SELECT customer_id FROM loans
INTERSECT
SELECT customer_id FROM credit_cards
ORDER BY customer_id;

-- Customers with a loan but NO credit card
SELECT customer_id FROM loans
EXCEPT
SELECT customer_id FROM credit_cards
ORDER BY customer_id;

-- ─────────────────────────────────────────────
-- 6.6  LATERAL JOINS  – row-by-row subquery
-- ─────────────────────────────────────────────

-- Get the most recent transaction for each account (lateral approach)
SELECT a.account_id,
       a.account_type,
       a.balance,
       latest.transaction_date  AS last_tx_date,
       latest.amount            AS last_tx_amount,
       latest.transaction_type  AS last_tx_type
FROM   accounts a
CROSS JOIN LATERAL (
    SELECT transaction_date, amount, transaction_type
    FROM   transactions t
    WHERE  t.account_id = a.account_id
    ORDER BY t.transaction_date DESC
    LIMIT  1
) latest
ORDER BY a.account_id;

-- Top 2 transactions per customer using LATERAL
SELECT c.first_name || ' ' || c.last_name  AS customer_name,
       top2.transaction_date::DATE         AS date,
       top2.amount,
       top2.transaction_type
FROM   customers c
JOIN   accounts  a ON a.customer_id = c.customer_id
CROSS JOIN LATERAL (
    SELECT t.transaction_date, t.amount, t.transaction_type
    FROM   transactions t
    WHERE  t.account_id = a.account_id
    ORDER BY t.amount DESC
    LIMIT  2
) top2
ORDER BY customer_name, top2.amount DESC;

-- ─────────────────────────────────────────────
-- 6.7  PIVOT-STYLE CROSSTAB (manual with CASE)
-- ─────────────────────────────────────────────

-- Monthly transaction count by type as columns (Q1 2025)
SELECT DATE_TRUNC('month', transaction_date)::DATE    AS month,
       COUNT(*) FILTER (WHERE transaction_type = 'deposit')     AS deposits,
       COUNT(*) FILTER (WHERE transaction_type = 'withdrawal')  AS withdrawals,
       COUNT(*) FILTER (WHERE transaction_type = 'fee')         AS fees,
       COUNT(*) FILTER (WHERE transaction_type = 'transfer_out')AS transfers_out,
       COUNT(*) FILTER (WHERE transaction_type = 'interest')    AS interest
FROM   transactions
WHERE  transaction_date BETWEEN '2025-01-01' AND '2025-03-31'
GROUP BY DATE_TRUNC('month', transaction_date)
ORDER BY month;

-- ─────────────────────────────────────────────
-- 6.8  GENERATE_SERIES  – useful for gap analysis
-- ─────────────────────────────────────────────

-- Find months in 2025 with NO transactions (gap detection)
WITH all_months AS (
    SELECT generate_series(
               '2025-01-01'::DATE,
               '2025-12-01'::DATE,
               '1 month'::INTERVAL
           )::DATE AS month
),
active_months AS (
    SELECT DISTINCT DATE_TRUNC('month', transaction_date)::DATE AS month
    FROM   transactions
    WHERE  transaction_date >= '2025-01-01'
)
SELECT am.month AS month_with_no_activity
FROM   all_months   am
LEFT   JOIN active_months actm ON actm.month = am.month
WHERE  actm.month IS NULL
ORDER BY am.month;

-- ─────────────────────────────────────────────
-- 6.9  ARRAY FUNCTIONS
-- ─────────────────────────────────────────────

-- Aggregate all account types for each customer into an array
SELECT c.customer_id,
       c.first_name || ' ' || c.last_name       AS customer_name,
       ARRAY_AGG(a.account_type ORDER BY a.account_type) AS account_types,
       COUNT(a.account_id)                       AS num_accounts
FROM   customers c
JOIN   accounts  a ON a.customer_id = c.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name
ORDER BY num_accounts DESC;

-- Find customers who have both a checking AND savings account
SELECT c.customer_id,
       c.first_name || ' ' || c.last_name AS customer_name
FROM   customers c
JOIN   accounts  a ON a.customer_id = c.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name
HAVING ARRAY_AGG(a.account_type) @> ARRAY['checking'::account_type_enum, 'savings'::account_type_enum]
ORDER BY c.last_name;

-- ─────────────────────────────────────────────
-- 6.10  JSON OUTPUT (useful for API backends)
-- ─────────────────────────────────────────────

-- Return customer profile as JSON
SELECT c.customer_id,
       JSON_BUILD_OBJECT(
           'id',          c.customer_id,
           'name',        c.first_name || ' ' || c.last_name,
           'email',       c.email,
           'state',       c.state,
           'credit_score',c.credit_score,
           'accounts',    (
               SELECT JSON_AGG(
                          JSON_BUILD_OBJECT(
                              'account_id',   a.account_id,
                              'type',         a.account_type,
                              'balance',      a.balance
                          )
                      )
               FROM   accounts a
               WHERE  a.customer_id = c.customer_id
           )
       ) AS customer_json
FROM   customers c
WHERE  c.customer_id <= 5
ORDER BY c.customer_id;
