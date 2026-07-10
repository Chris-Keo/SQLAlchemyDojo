# =============================================================================
# MODULE 3: FASTAPI BASICS
# Lesson 1 – App Structure, Health Endpoint, and Swagger Docs
# =============================================================================
# Goal: Stand up a FastAPI application, understand its structure, and run
#       a live HTTP server backed by the banking database.
#
# Run:
#   cd python_curriculum
#   uvicorn module_03_fastapi_basics.01_fastapi_setup:app --reload --port 8000
#
# Then open:
#   http://localhost:8000/docs    ← Swagger UI (interactive API explorer)
#   http://localhost:8000/redoc  ← ReDoc (alternative docs)
# =============================================================================

import os
from datetime import datetime

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

# ─────────────────────────────────────────────
# 3.1  CREATING A FASTAPI APP
# ─────────────────────────────────────────────
# FastAPI() creates the ASGI application instance.
# title, description, version appear in the auto-generated docs.

app = FastAPI(
    title       = "First National Bank API",
    description = "REST API for the First National Bank banking platform.",
    version     = "1.0.0",
    docs_url    = "/docs",    # Swagger UI path
    redoc_url   = "/redoc",   # ReDoc path
)


# ─────────────────────────────────────────────
# 3.2  PYDANTIC RESPONSE MODELS
# ─────────────────────────────────────────────
# Pydantic BaseModel defines the *shape* of request and response JSON.
# FastAPI uses these for automatic validation and serialization.

class HealthResponse(BaseModel):
    status:    str
    timestamp: datetime
    version:   str
    database:  str
    uptime_s:  float


class ErrorResponse(BaseModel):
    detail: str


# ─────────────────────────────────────────────
# 3.3  APP STARTUP / SHUTDOWN EVENTS
# ─────────────────────────────────────────────
# lifespan hooks run once when the server starts and shuts down.
# Use them for connection pool setup / teardown.

import time
from contextlib import asynccontextmanager

_start_time = time.time()


@asynccontextmanager
async def lifespan(application: FastAPI):
    # Startup: perform any one-time initialization here
    print("🏦 First National Bank API starting up…")
    yield
    # Shutdown: clean up resources
    print("🏦 First National Bank API shutting down…")


# Re-create the app with the lifespan handler
app = FastAPI(
    title       = "First National Bank API",
    description = "REST API for the First National Bank banking platform.",
    version     = "1.0.0",
    lifespan    = lifespan,
)


# ─────────────────────────────────────────────
# 3.4  ROOT ENDPOINT — GET /
# ─────────────────────────────────────────────
# @app.get("/") registers a GET route at the "/" path.
# The function's return value is automatically serialized to JSON.

@app.get("/", tags=["Meta"])
def root():
    """Welcome endpoint — confirms the API is alive."""
    return {
        "message": "Welcome to First National Bank API",
        "docs":    "/docs",
        "redoc":   "/redoc",
    }


# ─────────────────────────────────────────────
# 3.5  HEALTH CHECK ENDPOINT — GET /health
# ─────────────────────────────────────────────
# Health endpoints are used by load balancers and monitoring tools.
# response_model= tells FastAPI to validate the return value against HealthResponse.

from sqlalchemy import text
from module_01_python_sqlalchemy.setup_and_models import engine  # type: ignore


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Meta"],
    summary="Check API and database health",
)
def health_check():
    """Returns API health status including database connectivity."""
    db_status = "unknown"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as exc:
        db_status = f"error: {exc}"

    return HealthResponse(
        status    = "ok" if db_status == "connected" else "degraded",
        timestamp = datetime.utcnow(),
        version   = "1.0.0",
        database  = db_status,
        uptime_s  = round(time.time() - _start_time, 2),
    )


# ─────────────────────────────────────────────
# 3.6  PATH PARAMETERS — GET /branches/{branch_id}
# ─────────────────────────────────────────────
# Curly braces in the path define a path parameter.
# FastAPI automatically parses and validates the type.

class BranchResponse(BaseModel):
    branch_id:   int
    branch_name: str
    city:        str
    state:       str
    is_active:   bool
    assets_usd:  float


from sqlalchemy import select
from module_01_python_sqlalchemy.setup_and_models import SessionLocal, Branch  # type: ignore


@app.get(
    "/branches/{branch_id}",
    response_model=BranchResponse,
    tags=["Branches"],
    responses={404: {"model": ErrorResponse}},
)
def get_branch(branch_id: int):
    """Retrieve a single bank branch by its ID."""
    with SessionLocal() as session:
        branch = session.get(Branch, branch_id)
        if branch is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Branch {branch_id} not found",
            )
        return BranchResponse(
            branch_id   = branch.branch_id,
            branch_name = branch.branch_name,
            city        = branch.city,
            state       = branch.state,
            is_active   = branch.is_active,
            assets_usd  = float(branch.assets_usd),
        )


# ─────────────────────────────────────────────
# 3.7  QUERY PARAMETERS — GET /branches?state=NY&active_only=true
# ─────────────────────────────────────────────
# Function parameters that are NOT in the path become query parameters.
# Optional parameters need a default value.

from typing import Optional, List


@app.get("/branches", response_model=List[BranchResponse], tags=["Branches"])
def list_branches(
    state:       Optional[str] = None,   # ?state=NY
    active_only: bool          = True,   # ?active_only=false
    limit:       int           = 50,     # ?limit=10
):
    """List all branches, optionally filtered by state."""
    with SessionLocal() as session:
        stmt = select(Branch)
        if state:
            stmt = stmt.where(Branch.state == state.upper())
        if active_only:
            stmt = stmt.where(Branch.is_active == True)
        stmt = stmt.order_by(Branch.branch_name).limit(limit)

        branches = session.execute(stmt).scalars().all()
        return [
            BranchResponse(
                branch_id   = b.branch_id,
                branch_name = b.branch_name,
                city        = b.city,
                state       = b.state,
                is_active   = b.is_active,
                assets_usd  = float(b.assets_usd),
            )
            for b in branches
        ]


# ─────────────────────────────────────────────
# 3.8  ERROR RESPONSES
# ─────────────────────────────────────────────
# HTTPException(status_code=..., detail=...) returns a JSON error.
# FastAPI automatically maps it to the correct HTTP status code.
# Common codes:
#   200 OK          — successful GET/PUT
#   201 Created     — successful POST
#   204 No Content  — successful DELETE
#   400 Bad Request — client sent invalid data
#   404 Not Found   — resource does not exist
#   422 Unprocessable — Pydantic validation failed (automatic)
#   500 Internal Server Error — unexpected crash


# ─────────────────────────────────────────────
# LOCAL RUN (without uvicorn CLI)
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("module_03_fastapi_basics.01_fastapi_setup:app", host="0.0.0.0", port=8000, reload=True)
