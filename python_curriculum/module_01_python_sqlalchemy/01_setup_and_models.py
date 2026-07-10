# =============================================================================
# MODULE 1: PYTHON + SQLALCHEMY ORM
# Lesson 1 – Setup, Engine, Session, and ORM Models
# =============================================================================
# Goal: Define the full First National Bank schema as SQLAlchemy ORM models
#       and learn how to connect, create a session, and verify the setup.
# Dataset: First National Bank (firstnational_db)
# =============================================================================

# ─────────────────────────────────────────────
# 1.1  DEPENDENCIES & ENGINE SETUP
# ─────────────────────────────────────────────
# Install first:
#   pip install sqlalchemy psycopg2-binary python-dotenv

import os
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine, Column, Integer, String, Numeric,
    Boolean, Date, DateTime, ForeignKey, Enum as SAEnum, text
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import enum

load_dotenv()  # reads .env file for DATABASE_URL

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "******localhost:5432/firstnational_db"
)

# create_engine() is the entry point to the database.
# pool_pre_ping=True automatically checks connection health before using it.
engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False)

# declarative_base() returns a base class that all ORM models inherit from.
Base = declarative_base()

# sessionmaker() creates a factory for database sessions.
# autocommit=False → you must call session.commit() explicitly.
# autoflush=False  → changes are not flushed to DB automatically before queries.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ─────────────────────────────────────────────
# 1.2  PYTHON ENUMS  (mirrors PostgreSQL ENUM types)
# ─────────────────────────────────────────────

class AccountTypeEnum(str, enum.Enum):
    checking     = "checking"
    savings      = "savings"
    money_market = "money_market"
    cd           = "cd"


class TransactionTypeEnum(str, enum.Enum):
    deposit        = "deposit"
    withdrawal     = "withdrawal"
    transfer_in    = "transfer_in"
    transfer_out   = "transfer_out"
    fee            = "fee"
    interest       = "interest"
    payment        = "payment"
    refund         = "refund"
    atm_withdrawal = "atm_withdrawal"


class LoanStatusEnum(str, enum.Enum):
    pending    = "pending"
    active     = "active"
    paid_off   = "paid_off"
    defaulted  = "defaulted"
    delinquent = "delinquent"


class FraudStatusEnum(str, enum.Enum):
    open          = "open"
    investigating = "investigating"
    confirmed     = "confirmed"
    dismissed     = "dismissed"


# ─────────────────────────────────────────────
# 1.3  ORM MODEL: Branch
# ─────────────────────────────────────────────
# Each class maps to one table in the database.
# Column() defines a column; primary_key=True marks the PK.
# relationship() defines the Python-level association between models.

class Branch(Base):
    __tablename__ = "branches"

    branch_id   = Column(Integer, primary_key=True, index=True)
    branch_name = Column(String(100), nullable=False)
    city        = Column(String(80), nullable=False)
    state       = Column(String(2), nullable=False)
    zip_code    = Column(String(5), nullable=False)
    phone       = Column(String(15))
    opened_date = Column(Date, nullable=False)
    is_active   = Column(Boolean, nullable=False, default=True)
    assets_usd  = Column(Numeric(18, 2), nullable=False, default=0)

    # back_populates creates the reverse link on the related model
    employees = relationship("Employee", back_populates="branch")
    accounts  = relationship("Account", back_populates="branch")


# ─────────────────────────────────────────────
# 1.4  ORM MODEL: Employee  (self-referential for manager hierarchy)
# ─────────────────────────────────────────────

class Employee(Base):
    __tablename__ = "employees"

    employee_id = Column(Integer, primary_key=True, index=True)
    branch_id   = Column(Integer, ForeignKey("branches.branch_id"), nullable=False)
    first_name  = Column(String(50), nullable=False)
    last_name   = Column(String(50), nullable=False)
    job_title   = Column(String(80), nullable=False)
    hire_date   = Column(Date, nullable=False)
    salary      = Column(Numeric(12, 2), nullable=False)
    manager_id  = Column(Integer, ForeignKey("employees.employee_id"))
    email       = Column(String(120), unique=True, nullable=False)
    is_active   = Column(Boolean, nullable=False, default=True)

    branch      = relationship("Branch", back_populates="employees")
    # remote_side tells SQLAlchemy which side is the "one" in a self-join
    manager     = relationship("Employee", remote_side=[employee_id], backref="reports")


# ─────────────────────────────────────────────
# 1.5  ORM MODEL: Customer
# ─────────────────────────────────────────────

class Customer(Base):
    __tablename__ = "customers"

    customer_id    = Column(Integer, primary_key=True, index=True)
    first_name     = Column(String(50), nullable=False)
    last_name      = Column(String(50), nullable=False)
    email          = Column(String(120), unique=True, nullable=False)
    phone          = Column(String(15))
    date_of_birth  = Column(Date, nullable=False)
    ssn_last4      = Column(String(4), nullable=False)
    address_line1  = Column(String(120), nullable=False)
    city           = Column(String(80), nullable=False)
    state          = Column(String(2), nullable=False)
    zip_code       = Column(String(5), nullable=False)
    credit_score   = Column(Integer)
    joined_date    = Column(Date)
    is_active      = Column(Boolean, nullable=False, default=True)

    accounts      = relationship("Account", back_populates="customer")
    credit_cards  = relationship("CreditCard", back_populates="customer")
    loans         = relationship("Loan", back_populates="customer")
    fraud_alerts  = relationship("FraudAlert", back_populates="customer")


# ─────────────────────────────────────────────
# 1.6  ORM MODEL: Account
# ─────────────────────────────────────────────

class Account(Base):
    __tablename__ = "accounts"

    account_id     = Column(Integer, primary_key=True, index=True)
    customer_id    = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    branch_id      = Column(Integer, ForeignKey("branches.branch_id"), nullable=False)
    account_number = Column(String(20), unique=True, nullable=False)
    account_type   = Column(
        SAEnum(AccountTypeEnum, name="account_type_enum"),
        nullable=False
    )
    balance        = Column(Numeric(18, 2), nullable=False, default=0)
    opened_date    = Column(Date, nullable=False)
    is_active      = Column(Boolean, nullable=False, default=True)

    customer      = relationship("Customer", back_populates="accounts")
    branch        = relationship("Branch", back_populates="accounts")
    transactions  = relationship("Transaction", back_populates="account")


# ─────────────────────────────────────────────
# 1.7  ORM MODEL: Transaction
# ─────────────────────────────────────────────

class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id   = Column(Integer, primary_key=True, index=True)
    account_id       = Column(Integer, ForeignKey("accounts.account_id"), nullable=False)
    transaction_type = Column(
        SAEnum(TransactionTypeEnum, name="transaction_type_enum"),
        nullable=False
    )
    amount           = Column(Numeric(18, 2), nullable=False)
    transaction_date = Column(DateTime, nullable=False)
    description      = Column(String(200))
    balance_after    = Column(Numeric(18, 2))

    account = relationship("Account", back_populates="transactions")


# ─────────────────────────────────────────────
# 1.8  ORM MODEL: CreditCard
# ─────────────────────────────────────────────

class CreditCard(Base):
    __tablename__ = "credit_cards"

    card_id       = Column(Integer, primary_key=True, index=True)
    customer_id   = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    card_number   = Column(String(19), unique=True, nullable=False)
    credit_limit  = Column(Numeric(12, 2), nullable=False)
    current_balance = Column(Numeric(12, 2), nullable=False, default=0)
    apr           = Column(Numeric(5, 2))
    issued_date   = Column(Date, nullable=False)
    expiry_date   = Column(Date, nullable=False)
    is_active     = Column(Boolean, nullable=False, default=True)

    customer     = relationship("Customer", back_populates="credit_cards")
    cc_transactions = relationship("CreditCardTransaction", back_populates="card")


# ─────────────────────────────────────────────
# 1.9  ORM MODEL: CreditCardTransaction
# ─────────────────────────────────────────────

class CreditCardTransaction(Base):
    __tablename__ = "credit_card_transactions"

    cc_transaction_id   = Column(Integer, primary_key=True, index=True)
    card_id             = Column(Integer, ForeignKey("credit_cards.card_id"), nullable=False)
    merchant_name       = Column(String(120), nullable=False)
    merchant_category   = Column(String(80))
    amount              = Column(Numeric(12, 2), nullable=False)
    transaction_date    = Column(DateTime, nullable=False)
    is_international    = Column(Boolean, nullable=False, default=False)
    city                = Column(String(80))
    country             = Column(String(80))

    card = relationship("CreditCard", back_populates="cc_transactions")


# ─────────────────────────────────────────────
# 1.10  ORM MODEL: Loan
# ─────────────────────────────────────────────

class Loan(Base):
    __tablename__ = "loans"

    loan_id           = Column(Integer, primary_key=True, index=True)
    customer_id       = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    loan_type         = Column(String(50), nullable=False)
    principal_amount  = Column(Numeric(14, 2), nullable=False)
    interest_rate     = Column(Numeric(5, 2), nullable=False)
    term_months       = Column(Integer, nullable=False)
    start_date        = Column(Date, nullable=False)
    end_date          = Column(Date)
    status            = Column(
        SAEnum(LoanStatusEnum, name="loan_status_enum"),
        nullable=False, default=LoanStatusEnum.pending
    )
    monthly_payment   = Column(Numeric(12, 2))
    remaining_balance = Column(Numeric(14, 2))

    customer      = relationship("Customer", back_populates="loans")
    loan_payments = relationship("LoanPayment", back_populates="loan")


# ─────────────────────────────────────────────
# 1.11  ORM MODEL: LoanPayment
# ─────────────────────────────────────────────

class LoanPayment(Base):
    __tablename__ = "loan_payments"

    payment_id       = Column(Integer, primary_key=True, index=True)
    loan_id          = Column(Integer, ForeignKey("loans.loan_id"), nullable=False)
    payment_date     = Column(Date, nullable=False)
    amount_paid      = Column(Numeric(12, 2), nullable=False)
    principal_portion = Column(Numeric(12, 2))
    interest_portion  = Column(Numeric(12, 2))
    late_fee          = Column(Numeric(8, 2), default=0)
    days_late         = Column(Integer, default=0)

    loan = relationship("Loan", back_populates="loan_payments")


# ─────────────────────────────────────────────
# 1.12  ORM MODEL: FraudAlert
# ─────────────────────────────────────────────

class FraudAlert(Base):
    __tablename__ = "fraud_alerts"

    alert_id       = Column(Integer, primary_key=True, index=True)
    customer_id    = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    alert_date     = Column(DateTime, nullable=False)
    alert_type     = Column(String(80), nullable=False)
    description    = Column(String(500))
    status         = Column(
        SAEnum(FraudStatusEnum, name="fraud_status_enum"),
        nullable=False, default=FraudStatusEnum.open
    )
    resolved_date  = Column(DateTime)
    amount_at_risk = Column(Numeric(14, 2))

    customer = relationship("Customer", back_populates="fraud_alerts")


# ─────────────────────────────────────────────
# 1.13  VERIFY THE SETUP
# ─────────────────────────────────────────────
# Run this file directly to confirm the connection works:
#   python 01_setup_and_models.py

if __name__ == "__main__":
    # Test connectivity with a lightweight SQL ping
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.scalar()
        print(f"Connected to: {version}")

    # List all mapped table names so you can see the full schema
    print("\nRegistered ORM tables:")
    for table_name in Base.metadata.tables:
        print(f"  • {table_name}")

    print("\nSetup complete. You're ready for Lesson 2.")
