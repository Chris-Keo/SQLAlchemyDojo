# =============================================================================
# MODULE 1: EXERCISES
# =============================================================================
# Using the SQLAlchemy ORM models from 01_setup_and_models.py, complete each
# exercise below. Run 01_setup_and_models.py first to confirm your connection.
# =============================================================================

from sqlalchemy import select, func, and_, or_
from module_01_python_sqlalchemy.setup_and_models import (  # type: ignore
    SessionLocal, Customer, Account, Transaction, Branch,
    Employee, Loan, AccountTypeEnum
)


# ─────────────────────────────────────────────
# EXERCISE 1
# ─────────────────────────────────────────────
# Retrieve all active customers ordered by last name, then first name.
# Expected columns: customer_id, first_name, last_name, email, state

def exercise_1():
    # YOUR CODE HERE
    pass


# ─────────────────────────────────────────────
# EXERCISE 2
# ─────────────────────────────────────────────
# Find all savings accounts with a balance greater than $20,000.
# Order by balance descending. Show account_id, account_number, balance.

def exercise_2():
    # YOUR CODE HERE
    pass


# ─────────────────────────────────────────────
# EXERCISE 3
# ─────────────────────────────────────────────
# Count how many customers have a credit score above 720.

def exercise_3() -> int:
    # YOUR CODE HERE
    pass


# ─────────────────────────────────────────────
# EXERCISE 4
# ─────────────────────────────────────────────
# Find all employees hired after 2020-01-01 who are still active.
# Order by hire_date ascending.

def exercise_4():
    # YOUR CODE HERE
    pass


# ─────────────────────────────────────────────
# EXERCISE 5
# ─────────────────────────────────────────────
# Insert a new test customer into the database.
# Use your own name, a fake email, and any valid data.
# Print the new customer_id after inserting.
# Then soft-delete the customer by setting is_active = False.

def exercise_5():
    # YOUR CODE HERE
    pass


# ─────────────────────────────────────────────
# EXERCISE 6
# ─────────────────────────────────────────────
# Find all loans that are currently 'delinquent' or 'defaulted'.
# Show: loan_id, customer_id, loan_type, status, remaining_balance
# Order by remaining_balance descending.

def exercise_6():
    # YOUR CODE HERE
    pass


# ─────────────────────────────────────────────
# EXERCISE 7  (Stretch)
# ─────────────────────────────────────────────
# Find customers whose email domain is NOT 'gmail.com' or 'yahoo.com'.
# Hint: Use NOT + OR with .like() or ilike().

def exercise_7():
    # YOUR CODE HERE
    pass


if __name__ == "__main__":
    print("Exercise 1:"); exercise_1()
    print("\nExercise 2:"); exercise_2()
    print("\nExercise 3 (count):", exercise_3())
    print("\nExercise 4:"); exercise_4()
    print("\nExercise 5:"); exercise_5()
    print("\nExercise 6:"); exercise_6()
    print("\nExercise 7:"); exercise_7()
