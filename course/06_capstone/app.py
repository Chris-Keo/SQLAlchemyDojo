"""
Module 06 — Capstone: Sales Dashboard
======================================
Run:  python course/06_capstone/app.py
Open: http://127.0.0.1:8050

Architecture overview:
  ┌─────────────┐   Pydantic   ┌──────────────┐  dataclass  ┌───────────────┐
  │  Dash Forms │ ──────────► │ SaleRequest  │ ──────────► │  Sale (DC)    │
  │  (external) │  validates  │  (Pydantic)  │  converts   │  (domain)     │
  └─────────────┘             └──────────────┘             └───────────────┘
                                                                    │
                                                    InMemoryRepo[Sale]
                                                                    │
                                             ┌──────────────────────┘
                                             ▼
                                  Plotly charts + KPI cards
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field, asdict
from datetime import date, datetime, timedelta
from enum import StrEnum
from typing import Literal
from uuid import uuid4

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, State, callback, dcc, html
from pydantic import BaseModel, Field, NonNegativeFloat, PositiveInt, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


# ===========================================================================
# CONFIG  (Pydantic BaseSettings)
# ===========================================================================
class DashConfig(BaseSettings):
    app_title: str = "Sales Dashboard"
    debug: bool = True
    host: str = "127.0.0.1"
    port: int = 8050
    theme: str = "CYBORG"

    model_config = SettingsConfigDict(
        env_prefix="DASH_",
        env_file=".env",
        extra="ignore",
    )


config = DashConfig()


# ===========================================================================
# DOMAIN TYPES  (dataclasses + StrEnum)
# ===========================================================================
class Category(StrEnum):
    ELECTRONICS = "Electronics"
    CLOTHING = "Clothing"
    FOOD = "Food"
    BOOKS = "Books"
    HOME = "Home"
    SPORTS = "Sports"


class Region(StrEnum):
    NORTH = "North"
    SOUTH = "South"
    EAST = "East"
    WEST = "West"


@dataclass(frozen=True, slots=True)
class Money:
    """Immutable value object — 40% smaller than a plain dict."""
    amount: float
    currency: str = "USD"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError(f"Amount cannot be negative: {self.amount}")
        object.__setattr__(self, "amount", round(self.amount, 2))

    def __add__(self, other: Money) -> Money:
        assert self.currency == other.currency
        return Money(self.amount + other.amount, self.currency)

    def __str__(self) -> str:
        return f"${self.amount:,.2f}"


@dataclass
class Sale:
    """Domain entity — mutable, tracked by id."""
    product: str
    category: Category
    region: Region
    quantity: int
    unit_price: Money
    sale_date: date
    id: str = field(default_factory=lambda: str(uuid4())[:8])
    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def revenue(self) -> Money:
        return Money(self.quantity * self.unit_price.amount, self.unit_price.currency)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "product": self.product,
            "category": str(self.category),
            "region": str(self.region),
            "quantity": self.quantity,
            "unit_price": self.unit_price.amount,
            "revenue": self.revenue.amount,
            "sale_date": self.sale_date.isoformat(),
        }


# ===========================================================================
# REPOSITORY  (generic dataclass repository from Module 05)
# ===========================================================================
class SaleRepository:
    def __init__(self) -> None:
        self._store: dict[str, Sale] = {}

    def save(self, sale: Sale) -> Sale:
        self._store[sale.id] = sale
        return sale

    def all(self) -> list[Sale]:
        return list(self._store.values())

    def by_category(self, category: Category) -> list[Sale]:
        return [s for s in self._store.values() if s.category == category]

    def by_region(self, region: Region) -> list[Sale]:
        return [s for s in self._store.values() if s.region == region]

    def between_dates(self, start: date, end: date) -> list[Sale]:
        return [s for s in self._store.values() if start <= s.sale_date <= end]

    def to_dataframe(self) -> pd.DataFrame:
        if not self._store:
            return pd.DataFrame()
        return pd.DataFrame([s.to_dict() for s in self._store.values()])

    def total_revenue(self) -> float:
        return sum(s.revenue.amount for s in self._store.values())

    def count(self) -> int:
        return len(self._store)


# ===========================================================================
# API LAYER  (Pydantic — validates form input)
# ===========================================================================
class SaleRequest(BaseModel):
    """Validates data from the Dash form before creating a domain Sale."""
    product: str = Field(min_length=2, max_length=100)
    category: Category
    region: Region
    quantity: PositiveInt
    unit_price: NonNegativeFloat = Field(gt=0)
    sale_date: date

    def to_domain(self) -> Sale:
        return Sale(
            product=self.product,
            category=self.category,
            region=self.region,
            quantity=self.quantity,
            unit_price=Money(self.unit_price),
            sale_date=self.sale_date,
        )


# ===========================================================================
# SEED DATA
# ===========================================================================
def seed_repository(repo: SaleRepository, n: int = 150) -> None:
    products = {
        Category.ELECTRONICS: ["Laptop", "Phone", "Tablet", "Headphones", "Monitor"],
        Category.CLOTHING: ["T-Shirt", "Jeans", "Jacket", "Sneakers", "Hat"],
        Category.FOOD: ["Coffee", "Tea", "Snacks", "Juice", "Protein Bar"],
        Category.BOOKS: ["Python Book", "Design Patterns", "Clean Code", "DDD", "Refactoring"],
        Category.HOME: ["Lamp", "Cushion", "Candle", "Mug", "Plant"],
        Category.SPORTS: ["Yoga Mat", "Dumbbells", "Running Shoes", "Protein Powder", "Bike"],
    }
    price_ranges = {
        Category.ELECTRONICS: (49, 1499),
        Category.CLOTHING: (9, 149),
        Category.FOOD: (2, 29),
        Category.BOOKS: (9, 49),
        Category.HOME: (5, 79),
        Category.SPORTS: (15, 299),
    }
    random.seed(42)
    today = date.today()
    for _ in range(n):
        cat = random.choice(list(Category))
        low, high = price_ranges[cat]
        sale = Sale(
            product=random.choice(products[cat]),
            category=cat,
            region=random.choice(list(Region)),
            quantity=random.randint(1, 20),
            unit_price=Money(round(random.uniform(low, high), 2)),
            sale_date=today - timedelta(days=random.randint(0, 90)),
        )
        repo.save(sale)


# ===========================================================================
# CHARTS
# ===========================================================================
TEMPLATE = "plotly_dark"


def revenue_by_category_fig(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return go.Figure(layout=go.Layout(template=TEMPLATE, title="No data"))
    grouped = df.groupby("category")["revenue"].sum().reset_index()
    return px.bar(
        grouped,
        x="category",
        y="revenue",
        color="category",
        title="Revenue by Category",
        labels={"revenue": "Revenue ($)", "category": "Category"},
        template=TEMPLATE,
    )


def revenue_over_time_fig(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return go.Figure(layout=go.Layout(template=TEMPLATE, title="No data"))
    df = df.copy()
    df["sale_date"] = pd.to_datetime(df["sale_date"])
    daily = df.groupby("sale_date")["revenue"].sum().reset_index()
    return px.area(
        daily,
        x="sale_date",
        y="revenue",
        title="Daily Revenue",
        labels={"revenue": "Revenue ($)", "sale_date": "Date"},
        template=TEMPLATE,
    )


def region_pie_fig(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return go.Figure(layout=go.Layout(template=TEMPLATE, title="No data"))
    grouped = df.groupby("region")["revenue"].sum().reset_index()
    return px.pie(
        grouped,
        names="region",
        values="revenue",
        title="Revenue by Region",
        template=TEMPLATE,
        hole=0.4,
    )


def top_products_fig(df: pd.DataFrame, n: int = 10) -> go.Figure:
    if df.empty:
        return go.Figure(layout=go.Layout(template=TEMPLATE, title="No data"))
    grouped = df.groupby("product")["revenue"].sum().nlargest(n).reset_index()
    return px.bar(
        grouped,
        x="revenue",
        y="product",
        orientation="h",
        title=f"Top {n} Products by Revenue",
        labels={"revenue": "Revenue ($)", "product": "Product"},
        template=TEMPLATE,
    )


# ===========================================================================
# APP
# ===========================================================================
repo = SaleRepository()
seed_repository(repo)

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.CYBORG],
    title=config.app_title,
)

CATEGORIES = [{"label": c.value, "value": c.value} for c in Category]
REGIONS = [{"label": r.value, "value": r.value} for r in Region]
ALL_OPTION = {"label": "All", "value": "all"}

app.layout = dbc.Container(
    fluid=True,
    className="px-4",
    children=[
        # ── Header ──────────────────────────────────────────────────────────
        dbc.Row(dbc.Col(html.H2(
            [html.Span("📊 "), config.app_title,
             html.Small(" — Module 06 Capstone", className="text-muted fs-5 ms-3")],
            className="text-center my-4",
        ))),

        # ── Filters ─────────────────────────────────────────────────────────
        dbc.Row([
            dbc.Col([
                dbc.Label("Category"),
                dcc.Dropdown(
                    id="filter-category",
                    options=[ALL_OPTION] + CATEGORIES,
                    value="all",
                    clearable=False,
                ),
            ], width=3),
            dbc.Col([
                dbc.Label("Region"),
                dcc.Dropdown(
                    id="filter-region",
                    options=[ALL_OPTION] + REGIONS,
                    value="all",
                    clearable=False,
                ),
            ], width=3),
            dbc.Col([
                dbc.Label("Date Range"),
                dcc.DatePickerRange(
                    id="filter-dates",
                    start_date=(date.today() - timedelta(days=90)).isoformat(),
                    end_date=date.today().isoformat(),
                    display_format="YYYY-MM-DD",
                ),
            ], width=4),
            dbc.Col(
                dbc.Button("🔄 Reset", id="reset-btn", color="secondary", className="mt-4"),
                width=2,
            ),
        ], className="mb-3"),

        # ── KPI Cards ───────────────────────────────────────────────────────
        dbc.Row(id="kpi-row", className="mb-3"),

        # ── Charts ──────────────────────────────────────────────────────────
        dbc.Row([
            dbc.Col(dcc.Graph(id="chart-revenue-time"), width=8),
            dbc.Col(dcc.Graph(id="chart-region-pie"), width=4),
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id="chart-category-bar"), width=6),
            dbc.Col(dcc.Graph(id="chart-top-products"), width=6),
        ], className="mb-4"),

        # ── Add Sale Form ───────────────────────────────────────────────────
        dbc.Row(
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader(html.H5("➕ Add New Sale", className="mb-0")),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Product"),
                                dbc.Input(id="form-product", placeholder="e.g. Laptop Pro", type="text"),
                            ], width=4),
                            dbc.Col([
                                dbc.Label("Category"),
                                dcc.Dropdown(id="form-category", options=CATEGORIES, clearable=False),
                            ], width=2),
                            dbc.Col([
                                dbc.Label("Region"),
                                dcc.Dropdown(id="form-region", options=REGIONS, clearable=False),
                            ], width=2),
                            dbc.Col([
                                dbc.Label("Quantity"),
                                dbc.Input(id="form-qty", type="number", min=1, value=1),
                            ], width=1),
                            dbc.Col([
                                dbc.Label("Unit Price ($)"),
                                dbc.Input(id="form-price", type="number", min=0.01, step=0.01),
                            ], width=2),
                            dbc.Col([
                                dbc.Label("Date"),
                                dbc.Input(id="form-date", type="date", value=date.today().isoformat()),
                            ], width=3),
                        ], className="g-2"),
                        dbc.Row(
                            dbc.Col(
                                dbc.Button("Save Sale", id="save-btn", color="success", className="mt-3"),
                                width="auto",
                            )
                        ),
                        html.Div(id="form-feedback", className="mt-2"),
                    ]),
                ]),
                width=12,
                className="mb-5",
            )
        ),

        # Store for re-render trigger
        dcc.Store(id="sale-store", data=0),
    ],
)


# ===========================================================================
# Callbacks
# ===========================================================================
def _filtered_df(category: str, region: str, start: str, end: str) -> pd.DataFrame:
    df = repo.to_dataframe()
    if df.empty:
        return df
    df["sale_date_dt"] = pd.to_datetime(df["sale_date"])
    if category != "all":
        df = df[df["category"] == category]
    if region != "all":
        df = df[df["region"] == region]
    if start:
        df = df[df["sale_date_dt"] >= pd.Timestamp(start)]
    if end:
        df = df[df["sale_date_dt"] <= pd.Timestamp(end)]
    return df


@callback(
    Output("kpi-row", "children"),
    Output("chart-revenue-time", "figure"),
    Output("chart-region-pie", "figure"),
    Output("chart-category-bar", "figure"),
    Output("chart-top-products", "figure"),
    Input("filter-category", "value"),
    Input("filter-region", "value"),
    Input("filter-dates", "start_date"),
    Input("filter-dates", "end_date"),
    Input("sale-store", "data"),
)
def update_dashboard(category, region, start, end, _store):
    df = _filtered_df(category, region, start, end)

    total_rev = df["revenue"].sum() if not df.empty else 0
    total_sales = len(df) if not df.empty else 0
    avg_order = (df["revenue"].mean() if not df.empty else 0) or 0
    units = int(df["quantity"].sum()) if not df.empty else 0

    def kpi_card(title: str, value: str, color: str) -> dbc.Col:
        return dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.P(title, className="text-muted small mb-1"),
                    html.H4(value, className=f"text-{color} mb-0"),
                ]),
                className="text-center",
            ),
            width=3,
        )

    kpi_cards = [
        kpi_card("Total Revenue", f"${total_rev:,.2f}", "success"),
        kpi_card("Total Sales", f"{total_sales:,}", "info"),
        kpi_card("Avg Order Value", f"${avg_order:,.2f}", "warning"),
        kpi_card("Units Sold", f"{units:,}", "primary"),
    ]

    return (
        kpi_cards,
        revenue_over_time_fig(df),
        region_pie_fig(df),
        revenue_by_category_fig(df),
        top_products_fig(df),
    )


@callback(
    Output("form-feedback", "children"),
    Output("sale-store", "data"),
    Output("form-product", "value"),
    Input("save-btn", "n_clicks"),
    State("form-product", "value"),
    State("form-category", "value"),
    State("form-region", "value"),
    State("form-qty", "value"),
    State("form-price", "value"),
    State("form-date", "value"),
    State("sale-store", "data"),
    prevent_initial_call=True,
)
def save_sale(_, product, category, region, qty, price, sale_date, store_val):
    try:
        req = SaleRequest(
            product=product or "",
            category=category or "",
            region=region or "",
            quantity=qty or 0,
            unit_price=price or 0,
            sale_date=sale_date or date.today().isoformat(),
        )
        sale = req.to_domain()
        repo.save(sale)
        return (
            dbc.Alert(f"✅ Sale saved: {sale.product} — {sale.revenue}", color="success", duration=4000),
            (store_val or 0) + 1,
            "",
        )
    except ValidationError as e:
        items = [html.Li(f"{'.'.join(str(x) for x in err['loc'])}: {err['msg']}") for err in e.errors()]
        return (
            dbc.Alert([html.Strong("❌ Validation errors:"), html.Ul(items)], color="danger"),
            store_val,
            product,
        )
    except Exception as exc:
        return dbc.Alert(str(exc), color="danger"), store_val, product


@callback(
    Output("filter-category", "value"),
    Output("filter-region", "value"),
    Output("filter-dates", "start_date"),
    Output("filter-dates", "end_date"),
    Input("reset-btn", "n_clicks"),
    prevent_initial_call=True,
)
def reset_filters(_):
    return "all", "all", (date.today() - timedelta(days=90)).isoformat(), date.today().isoformat()


# ===========================================================================
if __name__ == "__main__":
    print(f"Open http://{config.host}:{config.port}")
    app.run(debug=config.debug, host=config.host, port=config.port)
