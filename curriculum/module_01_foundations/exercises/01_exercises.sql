-- =============================================================================
-- MODULE 1 – EXERCISES
-- =============================================================================
-- Instructions: Write the SQL query that answers each question.
-- Use the banking schema loaded from 01_create_tables.sql + 02_seed_data.sql
-- =============================================================================

-- Exercise 1
-- List all customers from Chicago (city = 'Chicago'), showing:
--   full_name (first + last), email, credit_score
-- Order by credit_score descending.



-- Exercise 2
-- Show account_id, account_type, balance, and the customer's full_name
-- for every account with a balance greater than $20,000.
-- Order by balance descending.



-- Exercise 3
-- List every employee and their manager's full name.
-- If an employee has no manager, show 'Top Executive' in the manager column.
-- Order by employee last_name.



-- Exercise 4
-- Find all customers who have NO credit card on file.
-- Show customer_id, full_name, and joined_date.



-- Exercise 5
-- List the 10 most recent transactions, showing:
--   transaction_date, customer full_name, account_type,
--   transaction_type, amount, channel
-- Order by transaction_date descending.



-- Exercise 6 (CHALLENGE)
-- Find all active loans where the customer's credit score is below 650.
-- Show: loan_id, loan_type, outstanding_balance, interest_rate,
--       customer full_name, credit_score
-- Order by credit_score ascending.
