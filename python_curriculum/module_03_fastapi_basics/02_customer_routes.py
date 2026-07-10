# =============================================================================
# MODULE 3: FASTAPI BASICS
# Lesson 2 – Customer Routes: GET, POST, PUT, DELETE
# =============================================================================
# Goal: Build a full CRUD API for the customers table using FastAPI routers,
#       Pydantic schemas, HTTP status codes, and path/query parameters.
#
# Run:
#   uvicorn module_03_fastapi_basics.02_customer_routes:app --reload --port 8000
# =============================================================================

from datetime import date
from typing import Optional, List

from fastapi import FastAPI, APIRouter, HTTPException, status, Query
from pydantic import BaseModel, EmailStr, field_validator

from sqlalchemy import select, update, delete, func, and_

from module_01_python_sqlalchemy.setup_and_models import (  # type: ignore
    SessionLocal, Customer
)

# ─────────────────────────────────────────────
# 3.1  PYDANTIC SCHEMAS
# ─────────────────────────────────────────────
# Separate schemas for Create, Read, and Update keep the API clean.
# CustomerCreate  — what the client sends when creating a customer
# CustomerUpdate  — partial update (all fields optional)
# CustomerOut     — what the API returns (never expose ssn_last4 fully)

class CustomerCreate(BaseModel):
    first_name:    str
    last_name:     str
    email:         str            # use EmailStr if email-validator is installed
    phone:         Optional[str]  = None
    date_of_birth: date
    ssn_last4:     str
    address_line1: str
    city:          str
    state:         str
    zip_code:      str
    credit_score:  Optional[int]  = None

    @field_validator("state")
    @classmethod
    def state_must_be_two_chars(cls, v: str) -> str:
        if len(v) != 2:
            raise ValueError("state must be a 2-character code (e.g. 'NY')")
        return v.upper()

    @field_validator("ssn_last4")
    @classmethod
    def ssn_must_be_four_digits(cls, v: str) -> str:
        if not v.isdigit() or len(v) != 4:
            raise ValueError("ssn_last4 must be exactly 4 digits")
        return v


class CustomerUpdate(BaseModel):
    first_name:    Optional[str]  = None
    last_name:     Optional[str]  = None
    email:         Optional[str]  = None
    phone:         Optional[str]  = None
    address_line1: Optional[str]  = None
    city:          Optional[str]  = None
    state:         Optional[str]  = None
    zip_code:      Optional[str]  = None
    credit_score:  Optional[int]  = None
    is_active:     Optional[bool] = None


class CustomerOut(BaseModel):
    customer_id:   int
    first_name:    str
    last_name:     str
    email:         str
    phone:         Optional[str]
    date_of_birth: date
    city:          str
    state:         str
    credit_score:  Optional[int]
    joined_date:   Optional[date]
    is_active:     bool

    model_config = {"from_attributes": True}  # allows ORM model → Pydantic conversion


class CustomerListResponse(BaseModel):
    total:     int
    page:      int
    page_size: int
    items:     List[CustomerOut]


# ─────────────────────────────────────────────
# 3.2  APIRouter — group related endpoints
# ─────────────────────────────────────────────
# APIRouter lets you split routes across files and import them into the main app.
# prefix="/customers" means all routes start with /customers.

router = APIRouter(prefix="/customers", tags=["Customers"])


# ─────────────────────────────────────────────
# 3.3  GET /customers — list with pagination + filter
# ─────────────────────────────────────────────

@router.get("", response_model=CustomerListResponse)
def list_customers(
    state:       Optional[str]  = Query(None, description="Filter by 2-letter state code"),
    active_only: bool           = Query(True,  description="Return only active customers"),
    min_score:   Optional[int]  = Query(None,  description="Minimum credit score"),
    page:        int            = Query(1,     ge=1),
    page_size:   int            = Query(20,    ge=1, le=100),
):
    """List customers with optional filters and pagination."""
    with SessionLocal() as session:
        # Build WHERE clauses dynamically
        filters = []
        if active_only:
            filters.append(Customer.is_active == True)
        if state:
            filters.append(Customer.state == state.upper())
        if min_score is not None:
            filters.append(Customer.credit_score >= min_score)

        # Count total for pagination metadata
        count_stmt = select(func.count()).select_from(Customer).where(*filters)
        total = session.execute(count_stmt).scalar()

        # Fetch page
        offset = (page - 1) * page_size
        stmt = (
            select(Customer)
            .where(*filters)
            .order_by(Customer.last_name, Customer.first_name)
            .offset(offset)
            .limit(page_size)
        )
        customers = session.execute(stmt).scalars().all()

        return CustomerListResponse(
            total     = total,
            page      = page,
            page_size = page_size,
            items     = [CustomerOut.model_validate(c) for c in customers],
        )


# ─────────────────────────────────────────────
# 3.4  GET /customers/{customer_id}
# ─────────────────────────────────────────────

@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: int):
    """Retrieve a single customer by ID."""
    with SessionLocal() as session:
        customer = session.get(Customer, customer_id)
        if customer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer {customer_id} not found",
            )
        return CustomerOut.model_validate(customer)


# ─────────────────────────────────────────────
# 3.5  POST /customers — create
# ─────────────────────────────────────────────
# status_code=201 tells FastAPI to respond with "201 Created" on success.

@router.post("", response_model=CustomerOut, status_code=status.HTTP_201_CREATED)
def create_customer(data: CustomerCreate):
    """Create a new banking customer."""
    with SessionLocal() as session:
        # Check for duplicate email
        existing = session.execute(
            select(Customer).where(Customer.email == data.email)
        ).scalars().first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email {data.email!r} is already registered",
            )

        customer = Customer(
            **data.model_dump(),
            joined_date = date.today(),
            is_active   = True,
        )
        session.add(customer)
        session.commit()
        session.refresh(customer)
        return CustomerOut.model_validate(customer)


# ─────────────────────────────────────────────
# 3.6  PATCH /customers/{customer_id} — partial update
# ─────────────────────────────────────────────
# PATCH updates only the provided fields; PUT replaces the entire resource.

@router.patch("/{customer_id}", response_model=CustomerOut)
def update_customer(customer_id: int, data: CustomerUpdate):
    """Partially update a customer's profile."""
    with SessionLocal() as session:
        customer = session.get(Customer, customer_id)
        if customer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer {customer_id} not found",
            )

        # model_dump(exclude_unset=True) gives only the fields the client sent
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(customer, field, value)

        session.commit()
        session.refresh(customer)
        return CustomerOut.model_validate(customer)


# ─────────────────────────────────────────────
# 3.7  DELETE /customers/{customer_id} — soft delete
# ─────────────────────────────────────────────
# Returns 204 No Content on success (no body).

@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_customer(customer_id: int):
    """Soft-delete a customer (sets is_active = False)."""
    with SessionLocal() as session:
        customer = session.get(Customer, customer_id)
        if customer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer {customer_id} not found",
            )
        customer.is_active = False
        session.commit()
        # 204 responses have no body; just return None


# ─────────────────────────────────────────────
# 3.8  Mount the router into a FastAPI app
# ─────────────────────────────────────────────

app = FastAPI(
    title       = "First National Bank — Customer API",
    description = "CRUD endpoints for bank customers.",
    version     = "1.0.0",
)
app.include_router(router)


@app.get("/", tags=["Meta"])
def root():
    return {"message": "Customer API running", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "module_03_fastapi_basics.02_customer_routes:app",
        host="0.0.0.0", port=8000, reload=True,
    )
