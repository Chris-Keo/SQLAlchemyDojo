-- =============================================================================
-- MODULE 7: PERFORMANCE & INDEXING
-- EXPLAIN ANALYZE, index types, query optimization patterns
-- =============================================================================

-- ─────────────────────────────────────────────
-- 7.1  EXPLAIN and EXPLAIN ANALYZE
-- ─────────────────────────────────────────────
-- EXPLAIN        → shows the query plan without executing
-- EXPLAIN ANALYZE → executes the query and shows actual timings
-- EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) → most detail

-- See the plan for a simple lookup
EXPLAIN
SELECT * FROM customers WHERE state = 'NY';

-- Run and time a join query
EXPLAIN (ANALYZE, BUFFERS)
SELECT c.first_name, c.last_name, a.balance
FROM   customers c
JOIN   accounts  a ON a.customer_id = c.customer_id
WHERE  a.account_type = 'savings'
  AND  a.is_active = TRUE;

-- ─────────────────────────────────────────────
-- 7.2  READING EXPLAIN OUTPUT
-- ─────────────────────────────────────────────
-- Key terms:
--   Seq Scan      → reads entire table (slow on large tables)
--   Index Scan    → uses an index for targeted access
--   Index Only Scan → fetches data from index alone (very fast)
--   Bitmap Scan   → combines multiple index scans
--   Hash Join     → builds hash table for join (good for large unsorted sets)
--   Nested Loop   → for each row in outer, scan inner (good with indexes)
--   Merge Join    → requires sorted inputs; efficient for large sorted sets
--   cost=X..Y     → estimated rows, startup..total cost
--   rows=N        → estimated row count
--   actual time   → measured time in ms
--   loops=N       → how many times this node was executed

-- ─────────────────────────────────────────────
-- 7.3  COMMON INDEXES ALREADY IN THE SCHEMA
-- ─────────────────────────────────────────────
-- See 01_create_tables.sql for:
--   idx_transactions_account_id    B-tree on transactions(account_id)
--   idx_transactions_date          B-tree on transactions(transaction_date DESC)
--   idx_accounts_customer_id       B-tree on accounts(customer_id)
--   idx_accounts_active            Partial index: WHERE is_active = TRUE
--   idx_transactions_account_date  Composite B-tree

-- ─────────────────────────────────────────────
-- 7.4  ADDING INDEXES
-- ─────────────────────────────────────────────

-- B-tree index for equality and range queries
CREATE INDEX IF NOT EXISTS idx_customers_state
    ON customers(state);

-- B-tree index on credit_score for range scans
CREATE INDEX IF NOT EXISTS idx_customers_credit_score
    ON customers(credit_score);

-- Partial index: only active loans (smaller, faster)
CREATE INDEX IF NOT EXISTS idx_loans_active
    ON loans(customer_id, outstanding_balance)
    WHERE status = 'active';

-- Composite index: supports queries filtering on both columns
CREATE INDEX IF NOT EXISTS idx_cc_tx_card_date
    ON credit_card_transactions(card_id, transaction_date DESC);

-- Covering index: includes extra column to allow index-only scans
CREATE INDEX IF NOT EXISTS idx_accounts_type_balance
    ON accounts(account_type, is_active)
    INCLUDE (balance);

-- ─────────────────────────────────────────────
-- 7.5  COMMON QUERY ANTI-PATTERNS  (and how to fix them)
-- ─────────────────────────────────────────────

-- ❌ Anti-pattern: function on indexed column destroys index usage
-- EXPLAIN SELECT * FROM transactions WHERE DATE(transaction_date) = '2025-01-01';

-- ✅ Fix: use range instead of applying a function
EXPLAIN
SELECT * FROM transactions
WHERE  transaction_date >= '2025-01-01'
  AND  transaction_date <  '2025-01-02';

-- ❌ Anti-pattern: LIKE with leading wildcard prevents index use
-- EXPLAIN SELECT * FROM customers WHERE last_name LIKE '%son';

-- ✅ Fix: trailing wildcard CAN use a B-tree index
EXPLAIN
SELECT * FROM customers WHERE last_name LIKE 'And%';

-- ❌ Anti-pattern: implicit type cast breaks index
-- SELECT * FROM customers WHERE customer_id = '5';   -- '5' is text

-- ✅ Fix: match data types
EXPLAIN
SELECT * FROM customers WHERE customer_id = 5;

-- ─────────────────────────────────────────────
-- 7.6  pg_stat_user_indexes  – index usage statistics
-- ─────────────────────────────────────────────

-- See which indexes are actually being used
SELECT schemaname,
       tablename,
       indexname,
       idx_scan        AS times_used,
       idx_tup_read    AS index_entries_read,
       idx_tup_fetch   AS table_rows_fetched
FROM   pg_stat_user_indexes
WHERE  schemaname = 'public'
ORDER BY times_used DESC;

-- ─────────────────────────────────────────────
-- 7.7  pg_stat_user_tables  – table access statistics
-- ─────────────────────────────────────────────

SELECT relname           AS table_name,
       seq_scan          AS full_scans,
       seq_tup_read      AS rows_read_by_full_scan,
       idx_scan          AS index_scans,
       n_live_tup        AS live_rows,
       n_dead_tup        AS dead_rows,
       last_vacuum,
       last_analyze
FROM   pg_stat_user_tables
WHERE  schemaname = 'public'
ORDER BY seq_scan DESC;

-- ─────────────────────────────────────────────
-- 7.8  VACUUM and ANALYZE
-- ─────────────────────────────────────────────
-- VACUUM         → reclaims storage from dead rows
-- VACUUM ANALYZE → also updates planner statistics
-- ANALYZE        → updates statistics only
-- Run after large data loads or batch deletes

VACUUM ANALYZE transactions;
VACUUM ANALYZE accounts;

-- ─────────────────────────────────────────────
-- 7.9  QUERY REWRITING FOR PERFORMANCE
-- ─────────────────────────────────────────────

-- Slow: correlated subquery runs once per row
EXPLAIN ANALYZE
SELECT a.account_id,
       (SELECT SUM(t.amount)
        FROM   transactions t
        WHERE  t.account_id = a.account_id) AS total_tx
FROM   accounts a;

-- Fast: pre-aggregate with a CTE or subquery, then join
EXPLAIN ANALYZE
WITH tx_totals AS (
    SELECT account_id, SUM(amount) AS total_tx
    FROM   transactions
    GROUP BY account_id
)
SELECT a.account_id, tt.total_tx
FROM   accounts  a
LEFT   JOIN tx_totals tt ON tt.account_id = a.account_id;

-- ─────────────────────────────────────────────
-- 7.10  PARTITIONING CONCEPT  (read-only example)
-- ─────────────────────────────────────────────
-- In large banks, the transactions table would be partitioned by date.
-- PostgreSQL native partitioning (range partition by year):

/*
CREATE TABLE transactions_partitioned (
    LIKE transactions
) PARTITION BY RANGE (transaction_date);

CREATE TABLE transactions_2024
    PARTITION OF transactions_partitioned
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TABLE transactions_2025
    PARTITION OF transactions_partitioned
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

-- PostgreSQL will route inserts and prune partitions on queries automatically.
*/

-- ─────────────────────────────────────────────
-- 7.11  MATERIALIZED VIEWS  – cache expensive queries
-- ─────────────────────────────────────────────

-- Create a materialized view for the daily account balance report
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_daily_account_summary AS
SELECT a.account_id,
       c.first_name || ' ' || c.last_name AS customer_name,
       a.account_type,
       a.balance,
       COUNT(t.transaction_id)            AS total_transactions,
       MAX(t.transaction_date)            AS last_transaction_date
FROM   accounts     a
JOIN   customers    c ON c.customer_id  = a.customer_id
LEFT   JOIN transactions t ON t.account_id = a.account_id
GROUP BY a.account_id, c.first_name, c.last_name, a.account_type, a.balance
WITH DATA;

-- Query the materialized view (fast)
SELECT * FROM mv_daily_account_summary ORDER BY balance DESC;

-- Refresh after data changes
REFRESH MATERIALIZED VIEW mv_daily_account_summary;

-- ─────────────────────────────────────────────
-- 7.12  VIEWS  – virtual tables for reuse
-- ─────────────────────────────────────────────

CREATE OR REPLACE VIEW v_customer_360 AS
SELECT c.customer_id,
       c.first_name || ' ' || c.last_name                      AS full_name,
       c.email,
       c.state,
       c.credit_score,
       c.joined_date,
       COALESCE(SUM(a.balance), 0)                             AS total_balance,
       COUNT(DISTINCT a.account_id)                            AS num_accounts,
       COUNT(DISTINCT l.loan_id)                               AS num_loans,
       COALESCE(SUM(l.outstanding_balance), 0)                 AS total_loan_balance,
       COUNT(DISTINCT cc.card_id)                              AS num_credit_cards
FROM   customers c
LEFT   JOIN accounts     a  ON a.customer_id  = c.customer_id
LEFT   JOIN loans        l  ON l.customer_id  = c.customer_id AND l.status = 'active'
LEFT   JOIN credit_cards cc ON cc.customer_id = c.customer_id AND cc.is_active = TRUE
GROUP BY c.customer_id, c.first_name, c.last_name, c.email,
         c.state, c.credit_score, c.joined_date;

-- Use the view
SELECT * FROM v_customer_360 ORDER BY total_balance DESC;
