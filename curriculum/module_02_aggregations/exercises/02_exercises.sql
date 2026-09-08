-- =============================================================================
-- MODULE 2 – EXERCISES
-- =============================================================================

-- Exercise 1
-- How many active customers does each branch have?
-- Show: branch_name, city, active_customer_count
-- Order by active_customer_count descending.



-- Exercise 2
-- What is the average, minimum, and maximum credit card balance
-- per card_type? Round averages to 2 decimal places.
-- Only include card types with more than 1 card.



-- Exercise 3
-- Show total loan exposure (sum of outstanding_balance) and
-- number of loans per loan_type, but only for loan_types where
-- total exposure exceeds $500,000.



-- Exercise 4
-- Using FILTER inside COUNT, produce a single-row summary of all
-- transactions showing:
--   total_transactions, deposit_count, withdrawal_count,
--   fee_count, total_deposit_amount, total_withdrawal_amount



-- Exercise 5  (ROLLUP)
-- Create a report showing the total transaction amount grouped
-- by state and transaction_type, including subtotals per state
-- and a grand total. Use ROLLUP.



-- Exercise 6  (CHALLENGE)
-- Find the top 3 merchant_category values by total spending
-- across both transactions AND credit_card_transactions combined.
-- Hint: UNION ALL the two tables, then aggregate.
