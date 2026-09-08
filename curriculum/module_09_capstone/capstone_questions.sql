-- =============================================================================
-- MODULE 9: CAPSTONE PROJECT
-- "First National Bank — Executive Analytics Dashboard"
--
-- Instructions:
--   Using all techniques learned in Modules 1–8, complete the queries below.
--   Each question targets a real business need. Some require CTEs + window
--   functions + joins working together. Attempt each before reading the hints.
-- =============================================================================

-- ─────────────────────────────────────────────
-- CAPSTONE 1: Branch Performance Scorecard
-- ─────────────────────────────────────────────
-- Produce a single report (one row per branch) showing:
--   branch_name, state,
--   total_deposits (sum of all account balances),
--   active_customers,
--   active_loans,
--   total_loan_exposure,
--   avg_customer_credit_score,
--   branch_rank (ranked by total_deposits, within state)
--
-- Order by state, then branch_rank.

-- YOUR QUERY HERE:




-- ─────────────────────────────────────────────
-- CAPSTONE 2: Employee Compensation vs. Branch Revenue
-- ─────────────────────────────────────────────
-- For each branch, show:
--   branch_name,
--   total_salary_cost  (sum of all employee salaries),
--   total_deposits      (sum of all account balances at that branch),
--   revenue_per_salary_dollar (total_deposits / total_salary_cost),
--   employee_count,
--   salary_rank (rank branches by total_salary_cost descending)
--
-- Hint: Use a CTE for salaries, another for deposits, then join + window.

-- YOUR QUERY HERE:




-- ─────────────────────────────────────────────
-- CAPSTONE 3: Customer Lifetime Value (CLV) Estimate
-- ─────────────────────────────────────────────
-- For each customer, estimate CLV as:
--   avg_monthly_balance * months_as_customer * 0.03   (simplified 3% annual yield / 12)
--
-- Show:
--   customer_name, joined_date, months_as_customer,
--   avg_monthly_balance (use account balance as proxy),
--   estimated_clv,
--   clv_percentile (PERCENT_RANK),
--   clv_tier ('Platinum' top 10%, 'Gold' 10-25%, 'Silver' 25-50%, 'Bronze' rest)
--
-- Order by estimated_clv descending.

-- YOUR QUERY HERE:




-- ─────────────────────────────────────────────
-- CAPSTONE 4: 30-Day Fraud Heat Map
-- ─────────────────────────────────────────────
-- Show a day-by-day breakdown of fraud signals for the most recent 30 days
-- of data in the transactions table. Each row = one calendar day. Columns:
--   day,
--   total_transactions,
--   flagged_transactions (amount > 1000 AND unusual hour),
--   fraud_rate_pct,
--   rolling_7day_avg_fraud_rate  (7-day moving average)
--
-- Hint: Use generate_series to ensure every day appears even if no transactions.

-- YOUR QUERY HERE:




-- ─────────────────────────────────────────────
-- CAPSTONE 5: Loan Amortization Dashboard
-- ─────────────────────────────────────────────
-- For each active loan, show:
--   loan_id, loan_type, customer_name,
--   original_principal, outstanding_balance,
--   total_paid_to_date (sum of loan_payments.amount_paid),
--   total_interest_paid (sum of loan_payments.interest_portion),
--   total_principal_paid,
--   pct_paid_off,
--   projected_payoff_months_remaining  (outstanding_balance / monthly_payment, rounded up)
--   loan_performance  ('On Track' if days_late avg = 0, 'Attention' if avg < 30, 'Critical' otherwise)
--
-- Order by pct_paid_off ascending (least progress first).

-- YOUR QUERY HERE:




-- ─────────────────────────────────────────────
-- CAPSTONE 6: Full Customer 360 Risk Report
-- ─────────────────────────────────────────────
-- Using CTEs, build a comprehensive view of every customer showing:
--   customer_name, state, credit_score,
--   total_deposit_balance,
--   total_loan_exposure,
--   net_worth_proxy (deposits - loans),
--   max_credit_card_utilization_pct,
--   has_fraud_alert (TRUE/FALSE),
--   rfm_segment (from the RFM model in Module 8 — simplify if needed),
--   overall_risk_level ('LOW', 'MEDIUM', 'HIGH')
--
-- Risk logic: HIGH if fraud alert OR credit_score < 600 OR utilization > 90%
--             MEDIUM if credit_score < 680 OR utilization > 70%
--             LOW otherwise
--
-- Order by overall_risk_level DESC, credit_score ASC.

-- YOUR QUERY HERE:
