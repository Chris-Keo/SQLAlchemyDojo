-- =============================================================================
-- MODULE 5 – EXERCISES
-- =============================================================================

-- Exercise 1
-- For each account, show every transaction and:
--   - a running total of amounts (from oldest to newest)
--   - the transaction's percentage of the running total
-- Only include account_id = 1.



-- Exercise 2
-- Using RANK() and DENSE_RANK(), rank all loans by outstanding_balance
-- WITHIN each loan_type. Show ties clearly.
-- Columns: loan_type, customer full_name, outstanding_balance,
--          rank_with_gaps, rank_no_gaps



-- Exercise 3  (LAG / LEAD)
-- For each customer's checking account transactions, show:
--   - previous transaction amount (LAG)
--   - next transaction amount (LEAD)
--   - flag 'LARGE_JUMP' if the amount is more than 3x the previous amount
-- Only show rows where previous amount exists.



-- Exercise 4  (NTILE)
-- Divide all active accounts into 5 equal groups (quintiles)
-- by balance. Show: account_id, balance, quintile,
-- and the min/max balance within each quintile.



-- Exercise 5  (CHALLENGE)
-- Using window functions only (no GROUP BY), find for each month in 2025:
--   - total transaction amount that month
--   - running year-to-date total
--   - month's share of the YTD total as a percentage
-- Hint: You can use SUM OVER with appropriate frames.
