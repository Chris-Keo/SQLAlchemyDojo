-- =============================================================================
-- CAPSTONE – REFERENCE SOLUTIONS
-- =============================================================================

-- CAPSTONE 1: Branch Performance Scorecard
WITH branch_deposits AS (
    SELECT b.branch_id,
           SUM(a.balance)                  AS total_deposits,
           COUNT(DISTINCT c.customer_id)   AS active_customers
    FROM   branches  b
    JOIN   accounts  a ON a.branch_id   = b.branch_id
    JOIN   customers c ON c.customer_id = a.customer_id
    WHERE  a.is_active = TRUE AND c.is_active = TRUE
    GROUP BY b.branch_id
),
branch_loans AS (
    SELECT branch_id,
           COUNT(*)                        AS active_loans,
           SUM(outstanding_balance)        AS total_loan_exposure
    FROM   loans
    WHERE  status = 'active'
    GROUP BY branch_id
),
branch_credit AS (
    SELECT c.branch_id,
           ROUND(AVG(c.credit_score), 0)  AS avg_credit_score
    FROM   customers c
    WHERE  c.credit_score IS NOT NULL AND c.is_active = TRUE
    GROUP BY c.branch_id
)
SELECT b.branch_name,
       b.state,
       COALESCE(bd.total_deposits, 0)         AS total_deposits,
       COALESCE(bd.active_customers, 0)       AS active_customers,
       COALESCE(bl.active_loans, 0)           AS active_loans,
       COALESCE(bl.total_loan_exposure, 0)    AS total_loan_exposure,
       bc.avg_credit_score,
       RANK() OVER (
           PARTITION BY b.state
           ORDER BY COALESCE(bd.total_deposits, 0) DESC
       )                                      AS branch_rank
FROM   branches     b
LEFT   JOIN branch_deposits bd ON bd.branch_id = b.branch_id
LEFT   JOIN branch_loans    bl ON bl.branch_id = b.branch_id
LEFT   JOIN branch_credit   bc ON bc.branch_id = b.branch_id
ORDER BY b.state, branch_rank;

-- ─────────────────────────────────────────────

-- CAPSTONE 2: Employee Compensation vs. Branch Revenue
WITH salary_costs AS (
    SELECT branch_id,
           COUNT(*)       AS employee_count,
           SUM(salary)    AS total_salary_cost
    FROM   employees
    WHERE  is_active = TRUE
    GROUP BY branch_id
),
branch_deposits AS (
    SELECT branch_id,
           SUM(balance)   AS total_deposits
    FROM   accounts
    WHERE  is_active = TRUE
    GROUP BY branch_id
)
SELECT b.branch_name,
       sc.total_salary_cost,
       COALESCE(bd.total_deposits, 0)                         AS total_deposits,
       ROUND(
           COALESCE(bd.total_deposits, 0) /
           NULLIF(sc.total_salary_cost, 0),
           2
       )                                                      AS revenue_per_salary_dollar,
       sc.employee_count,
       RANK() OVER (ORDER BY sc.total_salary_cost DESC)       AS salary_rank
FROM   branches       b
JOIN   salary_costs   sc ON sc.branch_id = b.branch_id
LEFT   JOIN branch_deposits bd ON bd.branch_id = b.branch_id
ORDER BY total_deposits DESC;

-- ─────────────────────────────────────────────

-- CAPSTONE 3: Customer Lifetime Value
WITH customer_balances AS (
    SELECT c.customer_id,
           c.first_name || ' ' || c.last_name               AS customer_name,
           c.joined_date,
           -- months as customer
           EXTRACT(YEAR FROM AGE(CURRENT_DATE, c.joined_date)) * 12 +
           EXTRACT(MONTH FROM AGE(CURRENT_DATE, c.joined_date)) AS months_as_customer,
           COALESCE(AVG(a.balance), 0)                       AS avg_monthly_balance
    FROM   customers c
    LEFT   JOIN accounts a ON a.customer_id = c.customer_id
    GROUP BY c.customer_id, c.first_name, c.last_name, c.joined_date
),
clv_calc AS (
    SELECT *,
           ROUND(avg_monthly_balance * months_as_customer * 0.03 / 12, 2) AS estimated_clv
    FROM   customer_balances
    WHERE  months_as_customer > 0
)
SELECT customer_name,
       joined_date,
       months_as_customer::INT,
       ROUND(avg_monthly_balance, 2)    AS avg_monthly_balance,
       estimated_clv,
       ROUND(PERCENT_RANK() OVER (ORDER BY estimated_clv) * 100, 1) AS clv_percentile,
       CASE
           WHEN PERCENT_RANK() OVER (ORDER BY estimated_clv) >= 0.90 THEN 'Platinum'
           WHEN PERCENT_RANK() OVER (ORDER BY estimated_clv) >= 0.75 THEN 'Gold'
           WHEN PERCENT_RANK() OVER (ORDER BY estimated_clv) >= 0.50 THEN 'Silver'
           ELSE 'Bronze'
       END AS clv_tier
FROM   clv_calc
ORDER BY estimated_clv DESC;

-- ─────────────────────────────────────────────

-- CAPSTONE 4: 30-Day Fraud Heat Map
WITH date_series AS (
    SELECT generate_series(
        (SELECT MAX(transaction_date::DATE) - INTERVAL '29 days' FROM transactions),
        (SELECT MAX(transaction_date::DATE) FROM transactions),
        '1 day'::INTERVAL
    )::DATE AS day
),
daily_stats AS (
    SELECT transaction_date::DATE                         AS day,
           COUNT(*)                                       AS total_transactions,
           COUNT(*) FILTER (
               WHERE amount > 1000
               AND EXTRACT(HOUR FROM transaction_date) NOT BETWEEN 8 AND 20
           )                                              AS flagged_transactions
    FROM   transactions
    GROUP BY transaction_date::DATE
),
combined AS (
    SELECT ds.day,
           COALESCE(dl.total_transactions, 0)    AS total_transactions,
           COALESCE(dl.flagged_transactions, 0)  AS flagged_transactions,
           ROUND(
               COALESCE(dl.flagged_transactions, 0) * 100.0 /
               NULLIF(COALESCE(dl.total_transactions, 0), 0),
               2
           )                                     AS fraud_rate_pct
    FROM   date_series  ds
    LEFT   JOIN daily_stats dl ON dl.day = ds.day
)
SELECT day,
       total_transactions,
       flagged_transactions,
       fraud_rate_pct,
       ROUND(
           AVG(fraud_rate_pct) OVER (
               ORDER BY day
               ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
           ),
           2
       )                                        AS rolling_7day_avg_fraud_rate
FROM   combined
ORDER BY day;

-- ─────────────────────────────────────────────

-- CAPSTONE 5: Loan Amortization Dashboard
WITH payment_summary AS (
    SELECT loan_id,
           SUM(amount_paid)                            AS total_paid,
           SUM(interest_portion)                       AS total_interest_paid,
           SUM(principal_portion)                      AS total_principal_paid,
           ROUND(AVG(days_late), 1)                    AS avg_days_late
    FROM   loan_payments
    GROUP BY loan_id
)
SELECT l.loan_id,
       l.loan_type,
       c.first_name || ' ' || c.last_name              AS customer_name,
       l.principal                                      AS original_principal,
       l.outstanding_balance,
       COALESCE(ps.total_paid, 0)                       AS total_paid_to_date,
       COALESCE(ps.total_interest_paid, 0)              AS total_interest_paid,
       COALESCE(ps.total_principal_paid, 0)             AS total_principal_paid,
       ROUND(
           (l.principal - l.outstanding_balance) / l.principal * 100,
           1
       )                                               AS pct_paid_off,
       CEIL(l.outstanding_balance / l.monthly_payment)::INT AS projected_months_remaining,
       CASE
           WHEN COALESCE(ps.avg_days_late, 0) = 0       THEN 'On Track'
           WHEN COALESCE(ps.avg_days_late, 0) < 30      THEN 'Attention'
           ELSE                                               'Critical'
       END AS loan_performance
FROM   loans          l
JOIN   customers      c  ON c.customer_id  = l.customer_id
LEFT   JOIN payment_summary ps ON ps.loan_id = l.loan_id
WHERE  l.status = 'active'
ORDER BY pct_paid_off ASC;

-- ─────────────────────────────────────────────

-- CAPSTONE 6: Full Customer 360 Risk Report
WITH deposit_summary AS (
    SELECT customer_id, SUM(balance) AS total_deposits
    FROM   accounts
    WHERE  is_active = TRUE
    GROUP BY customer_id
),
loan_summary AS (
    SELECT customer_id, SUM(outstanding_balance) AS total_loans
    FROM   loans
    WHERE  status = 'active'
    GROUP BY customer_id
),
cc_max_util AS (
    SELECT customer_id,
           ROUND(MAX(current_balance / NULLIF(credit_limit, 0)) * 100, 1) AS max_util_pct
    FROM   credit_cards
    WHERE  is_active = TRUE
    GROUP BY customer_id
),
fraud_flag AS (
    SELECT DISTINCT customer_id, TRUE AS has_fraud
    FROM   fraud_alerts
    WHERE  status IN ('open', 'investigating', 'confirmed')
),
rfm_raw AS (
    SELECT c.customer_id,
           NTILE(5) OVER (ORDER BY MAX(t.transaction_date) DESC)  AS recency_score,
           NTILE(5) OVER (ORDER BY COUNT(DISTINCT t.transaction_date::DATE) DESC) AS freq_score,
           NTILE(5) OVER (ORDER BY SUM(t.amount) DESC)            AS monetary_score
    FROM   customers    c
    JOIN   accounts     a ON a.customer_id = c.customer_id
    JOIN   transactions t ON t.account_id  = a.account_id
    GROUP BY c.customer_id
),
rfm_seg AS (
    SELECT customer_id,
           CASE
               WHEN recency_score >= 4 AND freq_score >= 4 AND monetary_score >= 4 THEN 'Champions'
               WHEN recency_score >= 3 AND freq_score >= 3                         THEN 'Loyal Customers'
               WHEN recency_score >= 4 AND freq_score <= 2                         THEN 'New Customers'
               WHEN recency_score <= 2 AND freq_score >= 4                         THEN 'At-Risk'
               WHEN recency_score <= 2 AND freq_score <= 2                         THEN 'Lost'
               ELSE 'Potential Loyalists'
           END AS rfm_segment
    FROM   rfm_raw
)
SELECT c.customer_id,
       c.first_name || ' ' || c.last_name               AS customer_name,
       c.state,
       c.credit_score,
       COALESCE(ds.total_deposits, 0)                   AS total_deposit_balance,
       COALESCE(ls.total_loans, 0)                      AS total_loan_exposure,
       COALESCE(ds.total_deposits, 0)
           - COALESCE(ls.total_loans, 0)                AS net_worth_proxy,
       COALESCE(cu.max_util_pct, 0)                     AS max_cc_utilization_pct,
       COALESCE(ff.has_fraud, FALSE)                    AS has_fraud_alert,
       COALESCE(rs.rfm_segment, 'No Activity')          AS rfm_segment,
       CASE
           WHEN COALESCE(ff.has_fraud, FALSE)
                OR c.credit_score < 600
                OR COALESCE(cu.max_util_pct, 0) > 90   THEN 'HIGH'
           WHEN c.credit_score < 680
                OR COALESCE(cu.max_util_pct, 0) > 70   THEN 'MEDIUM'
           ELSE                                              'LOW'
       END AS overall_risk_level
FROM   customers      c
LEFT   JOIN deposit_summary ds ON ds.customer_id = c.customer_id
LEFT   JOIN loan_summary    ls ON ls.customer_id = c.customer_id
LEFT   JOIN cc_max_util     cu ON cu.customer_id = c.customer_id
LEFT   JOIN fraud_flag      ff ON ff.customer_id = c.customer_id
LEFT   JOIN rfm_seg         rs ON rs.customer_id = c.customer_id
ORDER BY overall_risk_level DESC, c.credit_score ASC;
