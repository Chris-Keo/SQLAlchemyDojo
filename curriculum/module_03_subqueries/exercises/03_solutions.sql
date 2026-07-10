-- =============================================================================
-- MODULE 3 – EXERCISE SOLUTIONS
-- =============================================================================

-- Exercise 1
SELECT loan_id,
       loan_type,
       outstanding_balance,
       ROUND((SELECT AVG(outstanding_balance) FROM loans WHERE status = 'active'), 2) AS bank_avg_balance,
       ROUND(outstanding_balance -
             (SELECT AVG(outstanding_balance) FROM loans WHERE status = 'active'), 2) AS diff_from_avg
FROM   loans
WHERE  status = 'active'
ORDER BY diff_from_avg DESC;

-- Exercise 2
SELECT sub.account_id,
       sub.account_type,
       c.first_name || ' ' || c.last_name AS customer_name,
       sub.transaction_count
FROM (
    SELECT a.account_id,
           a.account_type,
           a.customer_id,
           COUNT(t.transaction_id) AS transaction_count
    FROM   accounts     a
    JOIN   transactions t ON t.account_id = a.account_id
    GROUP BY a.account_id, a.account_type, a.customer_id
) sub
JOIN customers c ON c.customer_id = sub.customer_id
ORDER BY sub.transaction_count DESC
LIMIT  5;

-- Exercise 3
SELECT c.customer_id,
       c.first_name || ' ' || c.last_name AS full_name,
       c.state
FROM   customers c
WHERE  EXISTS (
    SELECT 1
    FROM   credit_card_transactions cct
    JOIN   credit_cards cc ON cc.card_id = cct.card_id
    WHERE  cc.customer_id     = c.customer_id
      AND  cct.is_international = TRUE
)
ORDER BY c.last_name;

-- Exercise 4
SELECT b.branch_id,
       b.branch_name,
       b.city
FROM   branches b
WHERE  b.branch_id NOT IN (
    SELECT DISTINCT branch_id
    FROM   employees
)
ORDER BY b.branch_name;

-- Exercise 5
SELECT l.loan_type,
       c.first_name || ' ' || c.last_name AS customer_name,
       l.outstanding_balance
FROM   loans     l
JOIN   customers c ON c.customer_id = l.customer_id
WHERE  l.outstanding_balance = (
    SELECT MAX(l2.outstanding_balance)
    FROM   loans l2
    WHERE  l2.loan_type = l.loan_type
      AND  l2.status = 'active'
)
  AND  l.status = 'active'
ORDER BY l.loan_type;
