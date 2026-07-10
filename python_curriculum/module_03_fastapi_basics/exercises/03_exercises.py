# =============================================================================
# MODULE 3: EXERCISES
# =============================================================================

# ─────────────────────────────────────────────
# EXERCISE 1
# ─────────────────────────────────────────────
# Add a GET /customers/{customer_id}/accounts endpoint to the customer
# router from 02_customer_routes.py. It should return a list of all
# accounts belonging to the given customer, including only active ones
# by default (pass ?active_only=false to include inactive).

# ─────────────────────────────────────────────
# EXERCISE 2
# ─────────────────────────────────────────────
# Add a GET /branches/{branch_id}/employees endpoint that returns all
# employees at a branch. Include: employee_id, first_name, last_name,
# job_title, salary (only if active=True unless ?include_inactive=true).

# ─────────────────────────────────────────────
# EXERCISE 3
# ─────────────────────────────────────────────
# Create a Pydantic model `LoanOut` for the loans table and a
# GET /customers/{customer_id}/loans endpoint that returns all loans
# for a customer, with an optional ?status=active filter.

# ─────────────────────────────────────────────
# EXERCISE 4
# ─────────────────────────────────────────────
# Add input validation to the AccountCreate schema:
#   • account_number must be between 10 and 20 characters
#   • account_number must be alphanumeric (no spaces or special chars)
# Raise a descriptive 422 error if either rule is broken.

# ─────────────────────────────────────────────
# EXERCISE 5  (Stretch)
# ─────────────────────────────────────────────
# Build a GET /search endpoint that accepts a `q` query parameter and
# returns matching customers where first_name, last_name, or email
# contains the search string (case-insensitive, ILIKE).
# Return a list of up to 20 matches.

# ─────────────────────────────────────────────
# IMPLEMENT YOUR SOLUTIONS BELOW
# ─────────────────────────────────────────────

from typing import Optional, List
from fastapi import FastAPI, APIRouter, HTTPException, status, Query, Path
from pydantic import BaseModel

app = FastAPI(title="Module 3 Exercises", version="1.0.0")


# Exercise 1 — YOUR CODE HERE


# Exercise 2 — YOUR CODE HERE


# Exercise 3 — YOUR CODE HERE


# Exercise 4 — YOUR CODE HERE


# Exercise 5 — YOUR CODE HERE


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("module_03_fastapi_basics.exercises.03_exercises:app",
                host="0.0.0.0", port=8001, reload=True)
