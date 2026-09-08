# =============================================================================
# MODULE 4: EXERCISES
# =============================================================================

# ─────────────────────────────────────────────
# EXERCISE 1
# ─────────────────────────────────────────────
# Add a GET /customers/{customer_id}/360 endpoint to 03_banking_api.py.
# It should return a single JSON object with all of a customer's:
#   - Profile (from customers table)
#   - Active accounts and their balances
#   - Active loans and their status
#   - Any open fraud alerts
# Use Depends(get_db) and load everything in a single session.

# ─────────────────────────────────────────────
# EXERCISE 2
# ─────────────────────────────────────────────
# Add pagination metadata to the branch-performance analytics endpoint.
# Support ?page= and ?page_size= query params.
# Return the results wrapped in a Page[dict] response.

# ─────────────────────────────────────────────
# EXERCISE 3
# ─────────────────────────────────────────────
# Create a POST /accounts/{account_id}/transfer endpoint that:
#   1. Accepts a JSON body with: to_account_id (int), amount (float), description (str)
#   2. Debits the source account by amount
#   3. Credits the destination account by amount
#   4. Creates two Transaction records (transfer_out / transfer_in)
#   5. If either account is not found or has insufficient funds, rolls back both.
#
# Hint: Both operations must be in the same db.commit() call.

# ─────────────────────────────────────────────
# EXERCISE 4
# ─────────────────────────────────────────────
# Write a GET /employees endpoint with:
#   - ?branch_id= filter
#   - ?min_salary= and ?max_salary= filters
#   - ?page= and ?page_size= pagination
#   - Sorted by salary descending
# Use the Depends(get_db) pattern and Page[EmployeeOut] response model.

# ─────────────────────────────────────────────
# EXERCISE 5  (Stretch)
# ─────────────────────────────────────────────
# Add a global exception handler to the app using @app.exception_handler().
# It should catch unexpected SQLAlchemyError exceptions and return a
# standardized 500 JSON response:
#   {"detail": "A database error occurred. Please try again later."}
# instead of leaking internal details.

# ─────────────────────────────────────────────
# IMPLEMENT YOUR SOLUTIONS BELOW
# ─────────────────────────────────────────────

from fastapi import FastAPI, Depends, Query, Path, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from module_04_fastapi_sqlalchemy.01_database_session import get_db  # type: ignore

app = FastAPI(title="Module 4 Exercises", version="1.0.0")


# Exercise 1 — YOUR CODE HERE


# Exercise 2 — YOUR CODE HERE


# Exercise 3 — YOUR CODE HERE


# Exercise 4 — YOUR CODE HERE


# Exercise 5 — YOUR CODE HERE


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("module_04_fastapi_sqlalchemy.exercises.04_exercises:app",
                host="0.0.0.0", port=8001, reload=True)
