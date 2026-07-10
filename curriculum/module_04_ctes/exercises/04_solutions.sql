-- =============================================================================
-- MODULE 4 – EXERCISE SOLUTIONS
-- =============================================================================

-- Exercise 1
WITH customer_balances AS (
    SELECT c.customer_id,
           c.first_name || ' ' || c.last_name AS full_name,
           c.state,
           SUM(a.balance)                      AS total_balance
    FROM   customers c
    JOIN   accounts  a ON a.customer_id = c.customer_id
    GROUP BY c.customer_id, c.first_name, c.last_name, c.state
)
SELECT full_name, total_balance, state
FROM   customer_balances
WHERE  total_balance > 100000
ORDER BY total_balance DESC;

-- Exercise 2
WITH monthly_spending AS (
    SELECT cc.customer_id,
           DATE_TRUNC('month', cct.transaction_date)::DATE AS month,
           SUM(cct.amount)                                  AS monthly_spend
    FROM   credit_card_transactions cct
    JOIN   credit_cards cc ON cc.card_id = cct.card_id
    GROUP BY cc.customer_id, DATE_TRUNC('month', cct.transaction_date)
),
avg_spending AS (
    SELECT customer_id,
           ROUND(AVG(monthly_spend), 2)                    AS avg_monthly_spend
    FROM   monthly_spending
    GROUP BY customer_id
),
classified AS (
    SELECT a.customer_id,
           a.avg_monthly_spend,
           CASE WHEN a.avg_monthly_spend > 2000 THEN 'High Spender'
                ELSE 'Normal Spender' END AS spender_class
    FROM   avg_spending a
)
SELECT c.first_name || ' ' || c.last_name AS full_name,
       cl.avg_monthly_spend,
       cl.spender_class
FROM   classified cl
JOIN   customers  c ON c.customer_id = cl.customer_id
ORDER BY cl.avg_monthly_spend DESC;

-- Exercise 3
WITH RECURSIVE org AS (
    SELECT employee_id, first_name || ' ' || last_name AS full_name,
           job_title, manager_id, 0 AS depth
    FROM   employees
    WHERE  first_name = 'Patricia' AND last_name = 'Nguyen'
    UNION ALL
    SELECT e.employee_id, e.first_name || ' ' || e.last_name,
           e.job_title, e.manager_id, o.depth + 1
    FROM   employees e
    JOIN   org o ON o.employee_id = e.manager_id
)
SELECT full_name, job_title, depth
FROM   org
WHERE  depth > 0
ORDER BY depth, full_name;

-- Exercise 4
WITH branch_totals AS (
    SELECT b.branch_id,
           b.branch_name,
           b.state,
           SUM(a.balance) AS total_balance
    FROM   branches b
    JOIN   accounts a ON a.branch_id = b.branch_id
    GROUP BY b.branch_id, b.branch_name, b.state
)
SELECT state,
       branch_name,
       total_balance,
       RANK() OVER (PARTITION BY state ORDER BY total_balance DESC) AS rank_in_state
FROM   branch_totals
ORDER BY state, rank_in_state;

-- Exercise 5
WITH RECURSIVE amort AS (
    SELECT 1                                        AS payment_num,
           (SELECT outstanding_balance FROM loans WHERE loan_id = 5) AS balance,
           (SELECT monthly_payment    FROM loans WHERE loan_id = 5) AS monthly_payment,
           (SELECT interest_rate      FROM loans WHERE loan_id = 5) AS annual_rate
    UNION ALL
    SELECT payment_num + 1,
           ROUND(balance - (monthly_payment - ROUND(balance * annual_rate / 12, 2)), 2),
           monthly_payment,
           annual_rate
    FROM   amort
    WHERE  payment_num < 6 AND balance > 0
)
SELECT payment_num,
       ROUND(balance * annual_rate / 12, 2)                          AS interest_portion,
       ROUND(monthly_payment - balance * annual_rate / 12, 2)        AS principal_portion,
       monthly_payment                                                AS total_payment,
       balance                                                        AS remaining_balance
FROM   amort
ORDER BY payment_num;
