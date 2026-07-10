-- =============================================================================
-- MODULE 1: SQL FOUNDATIONS
-- Lesson 2 – JOINs (INNER, LEFT, RIGHT, FULL, SELF, CROSS)
-- =============================================================================

-- ─────────────────────────────────────────────
-- 2.1  INNER JOIN  – only matching rows
-- ─────────────────────────────────────────────

-- Each account with its customer's full name
SELECT a.account_id,
       a.account_number,
       a.account_type,
       a.balance,
       c.first_name || ' ' || c.last_name AS customer_name
FROM   accounts  a
JOIN   customers c ON c.customer_id = a.customer_id
ORDER BY a.balance DESC;

-- Transactions with account type and customer name
SELECT t.transaction_id,
       t.transaction_date,
       t.transaction_type,
       t.amount,
       a.account_type,
       c.first_name || ' ' || c.last_name AS customer_name
FROM   transactions t
JOIN   accounts     a ON a.account_id    = t.account_id
JOIN   customers    c ON c.customer_id   = a.customer_id
ORDER BY t.transaction_date DESC
LIMIT  20;

-- ─────────────────────────────────────────────
-- 2.2  LEFT JOIN  – all rows from left table
-- ─────────────────────────────────────────────

-- All customers, whether or not they have a loan
SELECT c.customer_id,
       c.first_name || ' ' || c.last_name AS customer_name,
       l.loan_id,
       l.loan_type,
       l.outstanding_balance
FROM   customers c
LEFT   JOIN loans l ON l.customer_id = c.customer_id
ORDER BY c.last_name;

-- Find customers with NO loans
SELECT c.customer_id,
       c.first_name || ' ' || c.last_name AS customer_name
FROM   customers c
LEFT   JOIN loans l ON l.customer_id = c.customer_id
WHERE  l.loan_id IS NULL
ORDER BY c.last_name;

-- ─────────────────────────────────────────────
-- 2.3  RIGHT JOIN (less common; prefer LEFT JOIN with tables swapped)
-- ─────────────────────────────────────────────

-- All branches, whether or not they have any employees
SELECT b.branch_name,
       b.city,
       e.first_name || ' ' || e.last_name AS employee_name,
       e.job_title
FROM   employees e
RIGHT  JOIN branches b ON b.branch_id = e.branch_id
ORDER BY b.branch_name, e.last_name;

-- ─────────────────────────────────────────────
-- 2.4  FULL OUTER JOIN
-- ─────────────────────────────────────────────

-- All customers and all loans, matched where possible
SELECT c.customer_id,
       c.first_name || ' ' || c.last_name AS customer_name,
       l.loan_id,
       l.loan_type
FROM   customers c
FULL   OUTER JOIN loans l ON l.customer_id = c.customer_id
WHERE  c.customer_id IS NULL OR l.loan_id IS NULL   -- show unmatched rows only
ORDER BY c.customer_id;

-- ─────────────────────────────────────────────
-- 2.5  SELF JOIN  – joining a table to itself
-- ─────────────────────────────────────────────

-- Employee hierarchy: employee and their manager
SELECT e.employee_id,
       e.first_name || ' ' || e.last_name   AS employee_name,
       e.job_title,
       m.first_name || ' ' || m.last_name   AS manager_name,
       m.job_title                           AS manager_title
FROM   employees e
LEFT   JOIN employees m ON m.employee_id = e.manager_id
ORDER BY m.last_name NULLS FIRST, e.last_name;

-- ─────────────────────────────────────────────
-- 2.6  THREE-TABLE JOIN PATTERN
-- ─────────────────────────────────────────────

-- Full picture: customer → account → branch
SELECT c.first_name || ' ' || c.last_name AS customer_name,
       c.city                              AS customer_city,
       a.account_type,
       a.balance,
       b.branch_name,
       b.city                              AS branch_city
FROM   customers c
JOIN   accounts  a ON a.customer_id = c.customer_id
JOIN   branches  b ON b.branch_id   = a.branch_id
ORDER BY a.balance DESC
LIMIT  15;

-- ─────────────────────────────────────────────
-- 2.7  JOINING ON MULTIPLE CONDITIONS
-- ─────────────────────────────────────────────

-- Transactions where account and branch are in the same state
SELECT t.transaction_id,
       t.amount,
       c.state AS customer_state,
       b.state AS branch_state
FROM   transactions t
JOIN   accounts  a ON a.account_id  = t.account_id
JOIN   customers c ON c.customer_id = a.customer_id
JOIN   branches  b ON b.branch_id   = a.branch_id
WHERE  c.state = b.state
LIMIT  20;

-- ─────────────────────────────────────────────
-- 2.8  JOIN WITH FILTERING AND AGGREGATION PREVIEW
-- ─────────────────────────────────────────────

-- Total deposits per customer in 2025 (preview of GROUP BY — covered in Module 2)
SELECT c.first_name || ' ' || c.last_name AS customer_name,
       COUNT(t.transaction_id)            AS deposit_count,
       SUM(t.amount)                      AS total_deposits
FROM   customers    c
JOIN   accounts     a ON a.customer_id   = c.customer_id
JOIN   transactions t ON t.account_id    = a.account_id
WHERE  t.transaction_type = 'deposit'
  AND  t.transaction_date >= '2025-01-01'
GROUP BY c.customer_id, c.first_name, c.last_name
ORDER BY total_deposits DESC;
