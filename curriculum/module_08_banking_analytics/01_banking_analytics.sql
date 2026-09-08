-- =============================================================================
-- MODULE 8: REAL-WORLD BANKING ANALYTICS
-- Fraud Detection, Risk Analysis, Customer Segmentation
-- This module ties together everything from modules 1–7.
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION A: FRAUD DETECTION
-- ─────────────────────────────────────────────────────────────────────────────

-- ─────────────────────────────────────────────
-- A1. Velocity Check: multiple transactions within a short window
-- ─────────────────────────────────────────────

-- Find accounts with 3+ transactions within any 10-minute window
WITH tx_with_next AS (
    SELECT account_id,
           transaction_id,
           transaction_date,
           amount,
           LEAD(transaction_date) OVER (
               PARTITION BY account_id
               ORDER BY transaction_date
           )                                   AS next_tx_date,
           LEAD(transaction_id) OVER (
               PARTITION BY account_id
               ORDER BY transaction_date
           )                                   AS next_tx_id
    FROM   transactions
),
rapid_pairs AS (
    SELECT account_id,
           transaction_id,
           next_tx_id,
           transaction_date,
           next_tx_date,
           EXTRACT(EPOCH FROM (next_tx_date - transaction_date)) / 60.0 AS minutes_apart
    FROM   tx_with_next
    WHERE  next_tx_date IS NOT NULL
)
SELECT a.account_id,
       c.first_name || ' ' || c.last_name  AS customer_name,
       rp.transaction_id,
       rp.transaction_date,
       rp.next_tx_id,
       rp.next_tx_date,
       ROUND(rp.minutes_apart, 2)          AS minutes_between,
       'Rapid Succession'                  AS fraud_signal
FROM   rapid_pairs rp
JOIN   accounts    a ON a.account_id    = rp.account_id
JOIN   customers   c ON c.customer_id  = a.customer_id
WHERE  rp.minutes_apart < 10
ORDER BY rp.minutes_apart;

-- ─────────────────────────────────────────────
-- A2. Unusual Hour + Large Amount Detection
-- ─────────────────────────────────────────────

SELECT t.transaction_id,
       t.transaction_date,
       EXTRACT(HOUR FROM t.transaction_date)::INT   AS hour_of_day,
       t.amount,
       t.channel,
       t.transaction_type,
       c.first_name || ' ' || c.last_name           AS customer_name,
       c.credit_score,
       -- Flag reason
       CASE
           WHEN EXTRACT(HOUR FROM t.transaction_date) BETWEEN 0 AND 4
                AND t.amount > 500                          THEN 'AFTER_HOURS_LARGE'
           WHEN t.amount > 3 * AVG(t.amount) OVER (
               PARTITION BY t.account_id
           )                                               THEN 'AMOUNT_SPIKE'
           ELSE NULL
       END AS alert_type
FROM   transactions  t
JOIN   accounts      a ON a.account_id   = t.account_id
JOIN   customers     c ON c.customer_id  = a.customer_id
HAVING CASE
           WHEN EXTRACT(HOUR FROM t.transaction_date) BETWEEN 0 AND 4
                AND t.amount > 500                          THEN 'AFTER_HOURS_LARGE'
           WHEN t.amount > 3 * AVG(t.amount) OVER (
               PARTITION BY t.account_id
           )                                               THEN 'AMOUNT_SPIKE'
       END IS NOT NULL
ORDER BY alert_type, t.transaction_date DESC;

-- ─────────────────────────────────────────────
-- A3. Credit Card Fraud: Duplicate Charges
-- ─────────────────────────────────────────────

WITH cc_numbered AS (
    SELECT cc_transaction_id,
           card_id,
           amount,
           transaction_date,
           merchant_name,
           ROW_NUMBER() OVER (
               PARTITION BY card_id, amount, merchant_name
               ORDER BY transaction_date
           ) AS dup_rank,
           COUNT(*) OVER (
               PARTITION BY card_id, amount, merchant_name
           ) AS dup_count
    FROM   credit_card_transactions
)
SELECT ccn.cc_transaction_id,
       c.first_name || ' ' || c.last_name   AS customer_name,
       cc.card_type,
       ccn.amount,
       ccn.transaction_date,
       ccn.merchant_name,
       ccn.dup_count                        AS times_charged
FROM   cc_numbered ccn
JOIN   credit_cards cc ON cc.card_id      = ccn.card_id
JOIN   customers    c  ON c.customer_id   = cc.customer_id
WHERE  ccn.dup_count > 1
ORDER BY ccn.card_id, ccn.transaction_date;

-- ─────────────────────────────────────────────
-- A4. Geographic Anomaly: Transactions from multiple countries
-- ─────────────────────────────────────────────

WITH customer_country_activity AS (
    SELECT cc.customer_id,
           cct.transaction_date::DATE              AS tx_date,
           SUM(CASE WHEN cct.is_international THEN 1 ELSE 0 END) AS intl_count,
           SUM(CASE WHEN NOT cct.is_international THEN 1 ELSE 0 END) AS domestic_count
    FROM   credit_card_transactions cct
    JOIN   credit_cards cc ON cc.card_id = cct.card_id
    GROUP BY cc.customer_id, cct.transaction_date::DATE
),
same_day_both AS (
    SELECT customer_id,
           tx_date,
           intl_count,
           domestic_count
    FROM   customer_country_activity
    WHERE  intl_count > 0 AND domestic_count > 0
)
SELECT c.first_name || ' ' || c.last_name   AS customer_name,
       s.tx_date,
       s.intl_count,
       s.domestic_count,
       'Same-day domestic + international' AS fraud_signal
FROM   same_day_both s
JOIN   customers c ON c.customer_id = s.customer_id
ORDER BY s.tx_date;

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION B: RISK ANALYSIS
-- ─────────────────────────────────────────────────────────────────────────────

-- ─────────────────────────────────────────────
-- B1. Loan Portfolio Risk Summary
-- ─────────────────────────────────────────────

WITH loan_stats AS (
    SELECT loan_type,
           status,
           COUNT(*)                                    AS loan_count,
           SUM(outstanding_balance)                    AS total_exposure,
           ROUND(AVG(interest_rate) * 100, 3)          AS avg_rate_pct,
           ROUND(AVG(outstanding_balance), 2)          AS avg_balance,
           MIN(outstanding_balance)                    AS min_balance,
           MAX(outstanding_balance)                    AS max_balance
    FROM   loans
    GROUP BY loan_type, status
),
portfolio_total AS (
    SELECT SUM(outstanding_balance) AS grand_total
    FROM   loans
)
SELECT ls.loan_type,
       ls.status,
       ls.loan_count,
       ls.total_exposure,
       ROUND(ls.total_exposure / pt.grand_total * 100, 2) AS pct_of_portfolio,
       ls.avg_rate_pct,
       ls.avg_balance
FROM   loan_stats    ls
CROSS  JOIN portfolio_total pt
ORDER BY ls.total_exposure DESC;

-- ─────────────────────────────────────────────
-- B2. Credit Utilization Analysis (Credit Cards)
-- ─────────────────────────────────────────────

WITH utilization AS (
    SELECT cc.card_id,
           c.first_name || ' ' || c.last_name         AS customer_name,
           cc.card_type,
           cc.credit_limit,
           cc.current_balance,
           ROUND(cc.current_balance / NULLIF(cc.credit_limit, 0) * 100, 1) AS utilization_pct,
           CASE
               WHEN cc.current_balance / NULLIF(cc.credit_limit, 0) >= 0.90 THEN 'Maxed Out (≥90%)'
               WHEN cc.current_balance / NULLIF(cc.credit_limit, 0) >= 0.70 THEN 'High (70-89%)'
               WHEN cc.current_balance / NULLIF(cc.credit_limit, 0) >= 0.30 THEN 'Moderate (30-69%)'
               ELSE                                                              'Low (<30%)'
           END AS utilization_bucket
    FROM   credit_cards cc
    JOIN   customers    c ON c.customer_id = cc.customer_id
    WHERE  cc.is_active = TRUE
)
SELECT utilization_bucket,
       COUNT(*)              AS card_count,
       ROUND(AVG(utilization_pct), 1)  AS avg_utilization,
       SUM(current_balance)  AS total_balance,
       SUM(credit_limit)     AS total_limit
FROM   utilization
GROUP BY utilization_bucket
ORDER BY avg_utilization DESC;

-- ─────────────────────────────────────────────
-- B3. Delinquency Aging Report
-- ─────────────────────────────────────────────

SELECT lp.loan_id,
       c.first_name || ' ' || c.last_name   AS customer_name,
       l.loan_type,
       l.outstanding_balance,
       lp.payment_date,
       lp.days_late,
       lp.late_fee,
       CASE
           WHEN lp.days_late = 0               THEN 'Current'
           WHEN lp.days_late BETWEEN 1 AND 30  THEN '1-30 Days Late'
           WHEN lp.days_late BETWEEN 31 AND 60 THEN '31-60 Days Late'
           WHEN lp.days_late BETWEEN 61 AND 90 THEN '61-90 Days Late'
           ELSE                                     '90+ Days Late'
       END AS aging_bucket
FROM   loan_payments lp
JOIN   loans         l  ON l.loan_id      = lp.loan_id
JOIN   customers     c  ON c.customer_id  = l.customer_id
WHERE  lp.days_late > 0
ORDER BY lp.days_late DESC;

-- ─────────────────────────────────────────────
-- B4. Customer Default Risk Score Model
-- ─────────────────────────────────────────────

WITH risk_factors AS (
    SELECT c.customer_id,
           c.first_name || ' ' || c.last_name          AS customer_name,
           c.credit_score,
           -- Credit score risk component (0-40 pts)
           CASE
               WHEN c.credit_score >= 750 THEN 0
               WHEN c.credit_score >= 700 THEN 10
               WHEN c.credit_score >= 650 THEN 20
               WHEN c.credit_score >= 600 THEN 30
               ELSE 40
           END AS credit_score_risk,
           -- Loan-to-deposit ratio component (0-30 pts)
           CASE
               WHEN COALESCE(SUM(l.outstanding_balance), 0) = 0 THEN 0
               WHEN COALESCE(SUM(a.balance), 1) = 0 THEN 30
               WHEN COALESCE(SUM(l.outstanding_balance), 0) /
                    NULLIF(COALESCE(SUM(a.balance), 0), 0) > 3 THEN 30
               WHEN COALESCE(SUM(l.outstanding_balance), 0) /
                    NULLIF(COALESCE(SUM(a.balance), 0), 0) > 1 THEN 20
               WHEN COALESCE(SUM(l.outstanding_balance), 0) /
                    NULLIF(COALESCE(SUM(a.balance), 0), 0) > 0.5 THEN 10
               ELSE 0
           END AS ltd_risk,
           -- Delinquency history component (0-30 pts)
           CASE
               WHEN EXISTS (
                   SELECT 1 FROM loans l2
                   WHERE l2.customer_id = c.customer_id
                     AND l2.status IN ('defaulted')
               ) THEN 30
               WHEN EXISTS (
                   SELECT 1 FROM loans l2
                   WHERE l2.customer_id = c.customer_id
                     AND l2.status = 'delinquent'
               ) THEN 20
               WHEN EXISTS (
                   SELECT 1 FROM loan_payments lp2
                   JOIN loans l2 ON l2.loan_id = lp2.loan_id
                   WHERE l2.customer_id = c.customer_id
                     AND lp2.days_late > 30
               ) THEN 10
               ELSE 0
           END AS delinquency_risk
    FROM   customers c
    LEFT   JOIN accounts a ON a.customer_id = c.customer_id
    LEFT   JOIN loans    l ON l.customer_id = c.customer_id AND l.status = 'active'
    GROUP BY c.customer_id, c.first_name, c.last_name, c.credit_score
)
SELECT customer_id,
       customer_name,
       credit_score,
       credit_score_risk,
       ltd_risk,
       delinquency_risk,
       credit_score_risk + ltd_risk + delinquency_risk          AS total_risk_score,
       CASE
           WHEN credit_score_risk + ltd_risk + delinquency_risk >= 60 THEN 'HIGH RISK'
           WHEN credit_score_risk + ltd_risk + delinquency_risk >= 30 THEN 'MEDIUM RISK'
           ELSE                                                             'LOW RISK'
       END AS risk_category
FROM   risk_factors
ORDER BY total_risk_score DESC;

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION C: CUSTOMER SEGMENTATION (RFM Analysis)
-- ─────────────────────────────────────────────────────────────────────────────
-- RFM = Recency · Frequency · Monetary
-- A classic customer value framework used in banking/retail

WITH rfm_raw AS (
    SELECT c.customer_id,
           c.first_name || ' ' || c.last_name              AS customer_name,
           -- Recency: days since last transaction
           CURRENT_DATE - MAX(t.transaction_date::DATE)    AS days_since_last_tx,
           -- Frequency: number of distinct transaction dates
           COUNT(DISTINCT t.transaction_date::DATE)        AS tx_frequency,
           -- Monetary: total amount transacted
           SUM(t.amount)                                   AS total_monetary
    FROM   customers    c
    JOIN   accounts     a ON a.customer_id = c.customer_id
    JOIN   transactions t ON t.account_id  = a.account_id
    GROUP BY c.customer_id, c.first_name, c.last_name
),
rfm_scored AS (
    SELECT *,
           -- Score each dimension 1 (worst) to 5 (best)
           NTILE(5) OVER (ORDER BY days_since_last_tx ASC)  AS recency_score,  -- lower days = better
           NTILE(5) OVER (ORDER BY tx_frequency DESC)       AS frequency_score,
           NTILE(5) OVER (ORDER BY total_monetary DESC)     AS monetary_score
    FROM   rfm_raw
),
rfm_final AS (
    SELECT *,
           ROUND((recency_score + frequency_score + monetary_score) / 3.0, 1) AS rfm_avg,
           CASE
               WHEN recency_score >= 4 AND frequency_score >= 4 AND monetary_score >= 4
                   THEN 'Champions'
               WHEN recency_score >= 3 AND frequency_score >= 3
                   THEN 'Loyal Customers'
               WHEN recency_score >= 4 AND frequency_score <= 2
                   THEN 'New Customers'
               WHEN recency_score <= 2 AND frequency_score >= 4
                   THEN 'At-Risk Customers'
               WHEN recency_score <= 2 AND frequency_score <= 2
                   THEN 'Lost Customers'
               ELSE 'Potential Loyalists'
           END AS rfm_segment
    FROM   rfm_scored
)
SELECT customer_id,
       customer_name,
       days_since_last_tx,
       tx_frequency,
       ROUND(total_monetary, 2) AS total_monetary,
       recency_score,
       frequency_score,
       monetary_score,
       rfm_avg,
       rfm_segment
FROM   rfm_final
ORDER BY rfm_avg DESC;

-- ─────────────────────────────────────────────
-- C2. Segment Summary
-- ─────────────────────────────────────────────

WITH rfm_raw AS (
    SELECT c.customer_id,
           CURRENT_DATE - MAX(t.transaction_date::DATE)    AS days_since_last_tx,
           COUNT(DISTINCT t.transaction_date::DATE)        AS tx_frequency,
           SUM(t.amount)                                   AS total_monetary
    FROM   customers    c
    JOIN   accounts     a ON a.customer_id = c.customer_id
    JOIN   transactions t ON t.account_id  = a.account_id
    GROUP BY c.customer_id
),
rfm_scored AS (
    SELECT *,
           NTILE(5) OVER (ORDER BY days_since_last_tx ASC) AS recency_score,
           NTILE(5) OVER (ORDER BY tx_frequency DESC)      AS frequency_score,
           NTILE(5) OVER (ORDER BY total_monetary DESC)    AS monetary_score
    FROM   rfm_raw
),
rfm_final AS (
    SELECT *,
           CASE
               WHEN recency_score >= 4 AND frequency_score >= 4 AND monetary_score >= 4
                   THEN 'Champions'
               WHEN recency_score >= 3 AND frequency_score >= 3
                   THEN 'Loyal Customers'
               WHEN recency_score >= 4 AND frequency_score <= 2
                   THEN 'New Customers'
               WHEN recency_score <= 2 AND frequency_score >= 4
                   THEN 'At-Risk Customers'
               WHEN recency_score <= 2 AND frequency_score <= 2
                   THEN 'Lost Customers'
               ELSE 'Potential Loyalists'
           END AS rfm_segment
    FROM   rfm_scored
)
SELECT rfm_segment,
       COUNT(*)                            AS customer_count,
       ROUND(AVG(total_monetary), 2)       AS avg_monetary,
       ROUND(AVG(tx_frequency), 1)         AS avg_frequency,
       ROUND(AVG(days_since_last_tx), 0)   AS avg_days_inactive
FROM   rfm_final
GROUP BY rfm_segment
ORDER BY avg_monetary DESC;
