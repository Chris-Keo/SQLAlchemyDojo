-- =============================================================================
-- MODULE 4 – EXERCISES
-- =============================================================================

-- Exercise 1
-- Using a CTE, find all customers who have a total account balance
-- above $100,000. Show: full_name, total_balance, state.
-- Order by total_balance descending.



-- Exercise 2  (chained CTEs)
-- Using two CTEs:
--   CTE 1: calculate total monthly credit card spending per customer
--   CTE 2: classify each customer as 'High Spender' (>$2000/month avg)
--          or 'Normal Spender'
-- Show: full_name, avg_monthly_spend, spender_class



-- Exercise 3  (recursive CTE)
-- Using a recursive CTE, list all employees that report
-- (directly or indirectly) to the employee named 'Patricia Nguyen'.
-- Show: full_name, job_title, depth (levels below Patricia)



-- Exercise 4  (CTE + window function)
-- Using a CTE to calculate each branch's total balance,
-- then rank branches by total balance within each state.
-- Show: state, branch_name, total_balance, rank_in_state



-- Exercise 5  (CHALLENGE – recursive amortization)
-- Using a recursive CTE, generate a 6-month amortization schedule
-- for Loan #5 (James Davis auto loan).
-- Show: payment_num, interest_portion, principal_portion,
--       total_payment, remaining_balance
