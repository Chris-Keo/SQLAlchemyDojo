-- =============================================================================
-- MODULE 1 – EXERCISE SOLUTIONS
-- =============================================================================

-- Exercise 1
SELECT first_name || ' ' || last_name AS full_name,
       email,
       credit_score
FROM   customers
WHERE  city = 'Chicago'
ORDER BY credit_score DESC;

-- Exercise 2
SELECT a.account_id,
       a.account_type,
       a.balance,
       c.first_name || ' ' || c.last_name AS full_name
FROM   accounts  a
JOIN   customers c ON c.customer_id = a.customer_id
WHERE  a.balance > 20000
ORDER BY a.balance DESC;

-- Exercise 3
SELECT e.employee_id,
       e.first_name || ' ' || e.last_name                  AS employee_name,
       COALESCE(m.first_name || ' ' || m.last_name,
                'Top Executive')                            AS manager_name
FROM   employees e
LEFT   JOIN employees m ON m.employee_id = e.manager_id
ORDER BY e.last_name;

-- Exercise 4
SELECT c.customer_id,
       c.first_name || ' ' || c.last_name AS full_name,
       c.joined_date
FROM   customers   c
LEFT   JOIN credit_cards cc ON cc.customer_id = c.customer_id
WHERE  cc.card_id IS NULL
ORDER BY c.joined_date;

-- Exercise 5
SELECT t.transaction_date,
       c.first_name || ' ' || c.last_name AS full_name,
       a.account_type,
       t.transaction_type,
       t.amount,
       t.channel
FROM   transactions t
JOIN   accounts     a ON a.account_id    = t.account_id
JOIN   customers    c ON c.customer_id   = a.customer_id
ORDER BY t.transaction_date DESC
LIMIT  10;

-- Exercise 6
SELECT l.loan_id,
       l.loan_type,
       l.outstanding_balance,
       l.interest_rate,
       c.first_name || ' ' || c.last_name AS full_name,
       c.credit_score
FROM   loans     l
JOIN   customers c ON c.customer_id = l.customer_id
WHERE  l.status = 'active'
  AND  c.credit_score < 650
ORDER BY c.credit_score ASC;
