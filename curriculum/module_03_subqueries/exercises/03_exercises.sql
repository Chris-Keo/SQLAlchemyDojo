-- =============================================================================
-- MODULE 3 – EXERCISES
-- =============================================================================

-- Exercise 1
-- Using a scalar subquery, show each loan's outstanding_balance
-- and how it compares to the average outstanding balance across all active loans.
-- Columns: loan_id, loan_type, outstanding_balance,
--          bank_avg_balance, diff_from_avg
-- Order by diff_from_avg descending.



-- Exercise 2
-- Using a derived table, find the top 5 accounts by number of transactions.
-- Show: account_id, account_type, customer_name, transaction_count.



-- Exercise 3  (EXISTS)
-- Find all customers who have made at least one international
-- credit card transaction. Use EXISTS.
-- Show: customer_id, full_name, state.



-- Exercise 4  (NOT IN)
-- Find branches that have no employees listed in the employees table.
-- Show: branch_id, branch_name, city.



-- Exercise 5  (CHALLENGE – correlated subquery)
-- For each loan type, find the customer with the highest outstanding_balance.
-- Show: loan_type, customer_name, outstanding_balance.
-- Hint: Use a correlated subquery in WHERE to find the max for each type.
