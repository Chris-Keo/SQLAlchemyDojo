-- =============================================================================
-- BANKING DATABASE SCHEMA
-- PostgreSQL / pgAdmin Master's Curriculum
-- =============================================================================
-- Run this file first before any other SQL in the curriculum.
-- =============================================================================

-- Drop existing objects in reverse dependency order (safe re-run)
DROP TABLE IF EXISTS fraud_alerts        CASCADE;
DROP TABLE IF EXISTS loan_payments       CASCADE;
DROP TABLE IF EXISTS loans               CASCADE;
DROP TABLE IF EXISTS credit_card_transactions CASCADE;
DROP TABLE IF EXISTS credit_cards        CASCADE;
DROP TABLE IF EXISTS transactions        CASCADE;
DROP TABLE IF EXISTS accounts            CASCADE;
DROP TABLE IF EXISTS employees           CASCADE;
DROP TABLE IF EXISTS branches            CASCADE;
DROP TABLE IF EXISTS customers           CASCADE;

DROP TYPE  IF EXISTS account_type_enum   CASCADE;
DROP TYPE  IF EXISTS transaction_type_enum CASCADE;
DROP TYPE  IF EXISTS loan_status_enum    CASCADE;
DROP TYPE  IF EXISTS fraud_status_enum   CASCADE;

-- -----------------------------------------------------------------------------
-- ENUM TYPES
-- -----------------------------------------------------------------------------
CREATE TYPE account_type_enum AS ENUM ('checking', 'savings', 'money_market', 'cd');
CREATE TYPE transaction_type_enum AS ENUM (
    'deposit', 'withdrawal', 'transfer_in', 'transfer_out',
    'fee', 'interest', 'payment', 'refund', 'atm_withdrawal'
);
CREATE TYPE loan_status_enum AS ENUM ('pending', 'active', 'paid_off', 'defaulted', 'delinquent');
CREATE TYPE fraud_status_enum AS ENUM ('open', 'investigating', 'confirmed', 'dismissed');

-- -----------------------------------------------------------------------------
-- BRANCHES
-- -----------------------------------------------------------------------------
CREATE TABLE branches (
    branch_id     SERIAL PRIMARY KEY,
    branch_name   VARCHAR(100)        NOT NULL,
    city          VARCHAR(80)         NOT NULL,
    state         CHAR(2)             NOT NULL,
    zip_code      CHAR(5)             NOT NULL,
    phone         VARCHAR(15),
    opened_date   DATE                NOT NULL,
    is_active     BOOLEAN             NOT NULL DEFAULT TRUE,
    assets_usd    NUMERIC(18, 2)      NOT NULL DEFAULT 0
);

-- -----------------------------------------------------------------------------
-- EMPLOYEES
-- -----------------------------------------------------------------------------
CREATE TABLE employees (
    employee_id   SERIAL PRIMARY KEY,
    branch_id     INT                 NOT NULL REFERENCES branches(branch_id),
    first_name    VARCHAR(50)         NOT NULL,
    last_name     VARCHAR(50)         NOT NULL,
    job_title     VARCHAR(80)         NOT NULL,
    hire_date     DATE                NOT NULL,
    salary        NUMERIC(12, 2)      NOT NULL,
    manager_id    INT                 REFERENCES employees(employee_id),
    email         VARCHAR(120)        UNIQUE NOT NULL,
    is_active     BOOLEAN             NOT NULL DEFAULT TRUE
);

-- -----------------------------------------------------------------------------
-- CUSTOMERS
-- -----------------------------------------------------------------------------
CREATE TABLE customers (
    customer_id   SERIAL PRIMARY KEY,
    first_name    VARCHAR(50)         NOT NULL,
    last_name     VARCHAR(50)         NOT NULL,
    email         VARCHAR(120)        UNIQUE NOT NULL,
    phone         VARCHAR(15),
    date_of_birth DATE                NOT NULL,
    ssn_last4     CHAR(4)             NOT NULL,
    address_line1 VARCHAR(120)        NOT NULL,
    city          VARCHAR(80)         NOT NULL,
    state         CHAR(2)             NOT NULL,
    zip_code      CHAR(5)             NOT NULL,
    joined_date   DATE                NOT NULL DEFAULT CURRENT_DATE,
    credit_score  SMALLINT            CHECK (credit_score BETWEEN 300 AND 850),
    is_active     BOOLEAN             NOT NULL DEFAULT TRUE,
    branch_id     INT                 REFERENCES branches(branch_id)
);

-- -----------------------------------------------------------------------------
-- ACCOUNTS
-- -----------------------------------------------------------------------------
CREATE TABLE accounts (
    account_id    SERIAL PRIMARY KEY,
    customer_id   INT                 NOT NULL REFERENCES customers(customer_id),
    branch_id     INT                 NOT NULL REFERENCES branches(branch_id),
    account_type  account_type_enum   NOT NULL,
    account_number VARCHAR(16)        UNIQUE NOT NULL,
    balance       NUMERIC(18, 2)      NOT NULL DEFAULT 0.00,
    interest_rate NUMERIC(6, 4)       NOT NULL DEFAULT 0.0000,
    opened_date   DATE                NOT NULL DEFAULT CURRENT_DATE,
    closed_date   DATE,
    is_active     BOOLEAN             NOT NULL DEFAULT TRUE,
    overdraft_limit NUMERIC(10, 2)    NOT NULL DEFAULT 0.00
);

-- -----------------------------------------------------------------------------
-- TRANSACTIONS
-- -----------------------------------------------------------------------------
CREATE TABLE transactions (
    transaction_id   BIGSERIAL PRIMARY KEY,
    account_id       INT                     NOT NULL REFERENCES accounts(account_id),
    transaction_type transaction_type_enum   NOT NULL,
    amount           NUMERIC(14, 2)          NOT NULL,
    balance_after    NUMERIC(18, 2)          NOT NULL,
    description      VARCHAR(255),
    transaction_date TIMESTAMPTZ             NOT NULL DEFAULT NOW(),
    channel          VARCHAR(30)             NOT NULL DEFAULT 'branch',
    -- channel: branch | atm | online | mobile | wire | ach
    merchant_name    VARCHAR(120),
    merchant_category VARCHAR(60),
    is_reversed      BOOLEAN                 NOT NULL DEFAULT FALSE,
    related_account_id INT                   REFERENCES accounts(account_id)
);

-- -----------------------------------------------------------------------------
-- CREDIT CARDS
-- -----------------------------------------------------------------------------
CREATE TABLE credit_cards (
    card_id          SERIAL PRIMARY KEY,
    customer_id      INT             NOT NULL REFERENCES customers(customer_id),
    card_number      CHAR(16)        UNIQUE NOT NULL,
    card_type        VARCHAR(30)     NOT NULL DEFAULT 'Visa',
    credit_limit     NUMERIC(12, 2)  NOT NULL,
    current_balance  NUMERIC(12, 2)  NOT NULL DEFAULT 0.00,
    interest_rate    NUMERIC(6, 4)   NOT NULL DEFAULT 0.2499,
    issued_date      DATE            NOT NULL,
    expiry_date      DATE            NOT NULL,
    is_active        BOOLEAN         NOT NULL DEFAULT TRUE,
    rewards_points   INT             NOT NULL DEFAULT 0
);

-- -----------------------------------------------------------------------------
-- CREDIT CARD TRANSACTIONS
-- -----------------------------------------------------------------------------
CREATE TABLE credit_card_transactions (
    cc_transaction_id BIGSERIAL PRIMARY KEY,
    card_id           INT             NOT NULL REFERENCES credit_cards(card_id),
    amount            NUMERIC(12, 2)  NOT NULL,
    transaction_date  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    merchant_name     VARCHAR(120)    NOT NULL,
    merchant_category VARCHAR(60),
    city              VARCHAR(80),
    state             CHAR(2),
    is_international  BOOLEAN         NOT NULL DEFAULT FALSE,
    is_disputed       BOOLEAN         NOT NULL DEFAULT FALSE
);

-- -----------------------------------------------------------------------------
-- LOANS
-- -----------------------------------------------------------------------------
CREATE TABLE loans (
    loan_id          SERIAL PRIMARY KEY,
    customer_id      INT             NOT NULL REFERENCES customers(customer_id),
    branch_id        INT             NOT NULL REFERENCES branches(branch_id),
    loan_type        VARCHAR(40)     NOT NULL,
    -- loan_type: mortgage | auto | personal | student | home_equity
    principal        NUMERIC(14, 2)  NOT NULL,
    outstanding_balance NUMERIC(14, 2) NOT NULL,
    interest_rate    NUMERIC(6, 4)   NOT NULL,
    origination_date DATE            NOT NULL,
    maturity_date    DATE            NOT NULL,
    monthly_payment  NUMERIC(10, 2)  NOT NULL,
    status           loan_status_enum NOT NULL DEFAULT 'active',
    collateral_type  VARCHAR(60)
);

-- -----------------------------------------------------------------------------
-- LOAN PAYMENTS
-- -----------------------------------------------------------------------------
CREATE TABLE loan_payments (
    payment_id       SERIAL PRIMARY KEY,
    loan_id          INT             NOT NULL REFERENCES loans(loan_id),
    payment_date     DATE            NOT NULL,
    amount_paid      NUMERIC(12, 2)  NOT NULL,
    principal_portion NUMERIC(12, 2) NOT NULL,
    interest_portion  NUMERIC(12, 2) NOT NULL,
    late_fee         NUMERIC(8, 2)   NOT NULL DEFAULT 0.00,
    days_late        SMALLINT        NOT NULL DEFAULT 0
);

-- -----------------------------------------------------------------------------
-- FRAUD ALERTS
-- -----------------------------------------------------------------------------
CREATE TABLE fraud_alerts (
    alert_id         SERIAL PRIMARY KEY,
    transaction_id   BIGINT          REFERENCES transactions(transaction_id),
    cc_transaction_id BIGINT         REFERENCES credit_card_transactions(cc_transaction_id),
    customer_id      INT             NOT NULL REFERENCES customers(customer_id),
    alert_date       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    alert_reason     VARCHAR(200)    NOT NULL,
    risk_score       NUMERIC(5, 2)   NOT NULL CHECK (risk_score BETWEEN 0 AND 100),
    status           fraud_status_enum NOT NULL DEFAULT 'open',
    resolved_date    TIMESTAMPTZ,
    investigator_id  INT             REFERENCES employees(employee_id)
);

-- -----------------------------------------------------------------------------
-- INDEXES  (supporting query performance modules)
-- -----------------------------------------------------------------------------
CREATE INDEX idx_transactions_account_id   ON transactions(account_id);
CREATE INDEX idx_transactions_date         ON transactions(transaction_date DESC);
CREATE INDEX idx_accounts_customer_id      ON accounts(customer_id);
CREATE INDEX idx_customers_branch_id       ON customers(branch_id);
CREATE INDEX idx_loans_customer_id         ON loans(customer_id);
CREATE INDEX idx_cc_transactions_card_id   ON credit_card_transactions(card_id);
CREATE INDEX idx_cc_transactions_date      ON credit_card_transactions(transaction_date DESC);
CREATE INDEX idx_fraud_alerts_customer_id  ON fraud_alerts(customer_id);

-- Partial index: only active accounts
CREATE INDEX idx_accounts_active ON accounts(customer_id) WHERE is_active = TRUE;

-- Composite index for common reporting queries
CREATE INDEX idx_transactions_account_date
    ON transactions(account_id, transaction_date DESC);
