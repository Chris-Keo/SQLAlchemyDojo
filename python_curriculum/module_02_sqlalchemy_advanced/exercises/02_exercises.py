# =============================================================================
# MODULE 2: EXERCISES
# =============================================================================

from module_01_python_sqlalchemy.setup_and_models import (  # type: ignore
    SessionLocal, Customer, Account, Transaction, Branch, Employee, Loan
)
from sqlalchemy import select, func, text, and_, desc


# ─────────────────────────────────────────────
# EXERCISE 1
# ─────────────────────────────────────────────
# Using a JOIN, list every branch and the total number of active accounts
# it holds. Order by account count descending.
# Columns: branch_name, state, active_account_count

def exercise_1():
    # YOUR CODE HERE
    pass


# ─────────────────────────────────────────────
# EXERCISE 2
# ─────────────────────────────────────────────
# Find all customers who have MORE than one active account.
# Use a subquery or HAVING.
# Columns: customer_id, first_name, last_name, account_count

def exercise_2():
    # YOUR CODE HERE
    pass


# ─────────────────────────────────────────────
# EXERCISE 3
# ─────────────────────────────────────────────
# Using the ORM's func().over() syntax (no raw SQL), rank customers
# within each state by their credit score (highest = rank 1).
# Show: state, first_name, last_name, credit_score, state_rank

def exercise_3():
    # YOUR CODE HERE
    pass


# ─────────────────────────────────────────────
# EXERCISE 4
# ─────────────────────────────────────────────
# Using text() (raw SQL), write a query that shows each account's
# highest single transaction amount and the date it occurred.
# Hint: use FIRST_VALUE or MAX with a window, or a correlated subquery.

def exercise_4():
    # YOUR CODE HERE
    pass


# ─────────────────────────────────────────────
# EXERCISE 5
# ─────────────────────────────────────────────
# Build a CTE using .cte() that:
#   1. Sums total loan exposure per customer (only 'active' loans)
#   2. Then joins back to customers and returns those whose loan
#      exposure exceeds $50,000
# Columns: first_name, last_name, total_loan_exposure

def exercise_5():
    # YOUR CODE HERE
    pass


# ─────────────────────────────────────────────
# EXERCISE 6  (Stretch — raw SQL)
# ─────────────────────────────────────────────
# Using text(), find accounts with a velocity anomaly:
# more than 3 transactions within any 10-minute window.
# (Mirror the SQL Module 8 fraud detection query.)

def exercise_6():
    # YOUR CODE HERE
    pass


if __name__ == "__main__":
    print("Exercise 1:"); exercise_1()
    print("\nExercise 2:"); exercise_2()
    print("\nExercise 3:"); exercise_3()
    print("\nExercise 4:"); exercise_4()
    print("\nExercise 5:"); exercise_5()
    print("\nExercise 6:"); exercise_6()
