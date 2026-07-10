-- =============================================================================
-- MODULE 2 – EXERCISE SOLUTIONS
-- =============================================================================

-- Exercise 1
SELECT b.branch_name,
       b.city,
       COUNT(c.customer_id) AS active_customer_count
FROM   branches  b
JOIN   customers c ON c.branch_id = b.branch_id
WHERE  c.is_active = TRUE
GROUP BY b.branch_id, b.branch_name, b.city
ORDER BY active_customer_count DESC;

-- Exercise 2
SELECT card_type,
       COUNT(*)                        AS card_count,
       ROUND(AVG(current_balance), 2)  AS avg_balance,
       MIN(current_balance)            AS min_balance,
       MAX(current_balance)            AS max_balance
FROM   credit_cards
GROUP BY card_type
HAVING COUNT(*) > 1
ORDER BY avg_balance DESC;

-- Exercise 3
SELECT loan_type,
       COUNT(*)                            AS loan_count,
       SUM(outstanding_balance)            AS total_exposure
FROM   loans
WHERE  status != 'paid_off'
GROUP BY loan_type
HAVING SUM(outstanding_balance) > 500000
ORDER BY total_exposure DESC;

-- Exercise 4
SELECT COUNT(*)                                                AS total_transactions,
       COUNT(*) FILTER (WHERE transaction_type = 'deposit')   AS deposit_count,
       COUNT(*) FILTER (WHERE transaction_type = 'withdrawal') AS withdrawal_count,
       COUNT(*) FILTER (WHERE transaction_type = 'fee')        AS fee_count,
       SUM(amount) FILTER (WHERE transaction_type = 'deposit') AS total_deposit_amount,
       SUM(amount) FILTER (WHERE transaction_type = 'withdrawal') AS total_withdrawal_amount
FROM   transactions;

-- Exercise 5
SELECT b.state,
       t.transaction_type,
       SUM(t.amount)  AS total_amount,
       COUNT(*)       AS tx_count
FROM   transactions t
JOIN   accounts     a ON a.account_id = t.account_id
JOIN   branches     b ON b.branch_id  = a.branch_id
GROUP BY ROLLUP(b.state, t.transaction_type)
ORDER BY b.state NULLS LAST,
         t.transaction_type NULLS LAST;

-- Exercise 6
SELECT merchant_category,
       SUM(amount)   AS total_spent,
       COUNT(*)      AS transaction_count
FROM (
    SELECT merchant_category, amount
    FROM   transactions
    WHERE  merchant_category IS NOT NULL
    UNION ALL
    SELECT merchant_category, amount
    FROM   credit_card_transactions
    WHERE  merchant_category IS NOT NULL
) combined
GROUP BY merchant_category
ORDER BY total_spent DESC
LIMIT  3;
