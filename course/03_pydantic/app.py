"""
Module 03 — Interactive Dash App: Pydantic v2 Explorer
=======================================================
Run:  python course/03_pydantic/app.py
Open: http://127.0.0.1:8050
"""
from __future__ import annotations

import json
import textwrap
import traceback

import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import Dash, Input, Output, State, callback, dcc, html

SNIPPETS: dict[str, str] = {
    "BaseModel Basics": textwrap.dedent("""\
        from pydantic import BaseModel, EmailStr, PositiveInt, Field
        from datetime import datetime
        from uuid import uuid4

        class User(BaseModel):
            id: str = Field(default_factory=lambda: str(uuid4())[:8])
            name: str
            email: EmailStr
            age: PositiveInt

        # Valid
        u = User(name="Alice", email="alice@example.com", age=30)
        print(u)
        print(u.model_dump())
        print(u.model_dump_json(indent=2))
    """),
    "Validation Error": textwrap.dedent("""\
        from pydantic import BaseModel, EmailStr, PositiveInt, ValidationError

        class User(BaseModel):
            name: str
            email: EmailStr
            age: PositiveInt

        try:
            User(name="Bob", email="not-an-email", age=-5)
        except ValidationError as e:
            print(f"{e.error_count()} errors:")
            for err in e.errors():
                loc = " -> ".join(str(x) for x in err["loc"])
                print(f"  [{loc}] {err['msg']}  (type={err['type']})")
    """),
    "Field Validators": textwrap.dedent("""\
        from pydantic import BaseModel, field_validator
        from datetime import date

        class Registration(BaseModel):
            username: str
            birth_date: date

            @field_validator("username")
            @classmethod
            def alphanumeric(cls, v: str) -> str:
                if not v.replace("_","").isalnum():
                    raise ValueError("only letters, digits, underscores")
                return v.lower()

            @field_validator("birth_date")
            @classmethod
            def must_be_adult(cls, v: date) -> date:
                from datetime import date as d
                age = d.today().year - v.year
                if age < 18:
                    raise ValueError(f"Must be 18+, got age {age}")
                return v

        r = Registration(username="Alice_99", birth_date="1995-03-20")
        print(r)
        print(r.username)  # 'alice_99' (lowercased)
    """),
    "Model Validator": textwrap.dedent("""\
        from pydantic import BaseModel, model_validator
        from datetime import date

        class DateRange(BaseModel):
            start: date
            end: date

            @model_validator(mode="after")
            def end_after_start(self) -> "DateRange":
                if self.end <= self.start:
                    raise ValueError(f"end must be after start")
                return self

            @property
            def days(self) -> int:
                return (self.end - self.start).days

        r = DateRange(start="2024-01-01", end="2024-12-31")
        print(r.days, "days")

        from pydantic import ValidationError
        try:
            DateRange(start="2024-12-31", end="2024-01-01")
        except ValidationError as e:
            print("Error:", e.errors()[0]["msg"])
    """),
    "Discriminated Union": textwrap.dedent("""\
        from pydantic import BaseModel, Field
        from typing import Annotated, Union, Literal

        class Card(BaseModel):
            payment_type: Literal["card"]
            number: str

        class Transfer(BaseModel):
            payment_type: Literal["transfer"]
            iban: str

        Payment = Annotated[
            Union[Card, Transfer],
            Field(discriminator="payment_type"),
        ]

        class Order(BaseModel):
            id: str
            payment: Payment

        o1 = Order(id="1", payment={"payment_type": "card", "number": "4111111111111111"})
        o2 = Order(id="2", payment={"payment_type": "transfer", "iban": "GB29NWBK60161331926819"})
        print(type(o1.payment).__name__)  # Card
        print(type(o2.payment).__name__)  # Transfer
    """),
    "JSON Schema": textwrap.dedent("""\
        import json
        from pydantic import BaseModel, Field
        from pydantic import NonNegativeFloat

        class Product(BaseModel):
            sku: str = Field(min_length=3, max_length=20, pattern=r"^[A-Z0-9\\-]+$")
            name: str = Field(min_length=1, max_length=100)
            price: NonNegativeFloat
            stock: int = Field(ge=0)
            tags: list[str] = Field(default_factory=list, max_length=10)

        schema = Product.model_json_schema()
        print(json.dumps(schema, indent=2))
    """),
}

NOTES: dict[str, str] = {
    "BaseModel Basics": (
        "Pydantic **validates** every field at construction time. "
        "`model_dump()` returns a plain dict; `model_dump_json()` returns a JSON string. "
        "`model_json_schema()` returns the full JSON Schema — great for API documentation."
    ),
    "Validation Error": (
        "A `ValidationError` collects **all** field errors before raising — not just the first. "
        "Each error has `loc` (location), `msg` (human message), and `type` (machine-readable code)."
    ),
    "Field Validators": (
        "`@field_validator` runs after Pydantic's built-in type coercion. "
        "Return the (possibly transformed) value, or raise `ValueError`. "
        "The `mode='before'` option runs before coercion — useful to normalise raw input."
    ),
    "Model Validator": (
        "`@model_validator(mode='after')` receives the fully-constructed model instance. "
        "Use it for **cross-field** constraints. `mode='before'` receives the raw dict and "
        "runs before any field validation."
    ),
    "Discriminated Union": (
        "Discriminated unions let Pydantic pick the correct sub-model based on a literal "
        "field (`payment_type`). This is **much faster** than a plain `Union` because "
        "Pydantic doesn't have to try every sub-type."
    ),
    "JSON Schema": (
        "Every Pydantic model has a `model_json_schema()` class method that generates "
        "a JSON Schema automatically from your annotations. FastAPI uses this to generate "
        "OpenAPI documentation with zero extra work."
    ),
}

# ---------------------------------------------------------------------------
# Speed comparison chart (dataclass vs pydantic vs plain class)
# ---------------------------------------------------------------------------
import timeit
from dataclasses import dataclass

try:
    from pydantic import BaseModel as _BM, EmailStr as _ES

    @dataclass
    class _DC:
        name: str
        age: int

    class _PY(_BM):
        name: str
        age: int

    class _PC:
        def __init__(self, name: str, age: int) -> None:
            self.name = name
            self.age = age

    N = 50_000
    _t_dc = timeit.timeit("_DC('Alice', 30)", globals={"_DC": _DC}, number=N)
    _t_py = timeit.timeit("_PY(name='Alice', age=30)", globals={"_PY": _PY}, number=N)
    _t_pc = timeit.timeit("_PC('Alice', 30)", globals={"_PC": _PC}, number=N)

    SPEED_FIG = go.Figure(
        data=[
            go.Bar(name=f"Plain class ({_t_pc:.3f}s)", x=["Creation time"], y=[_t_pc], marker_color="#636EFA"),
            go.Bar(name=f"@dataclass ({_t_dc:.3f}s)", x=["Creation time"], y=[_t_dc], marker_color="#00CC96"),
            go.Bar(name=f"Pydantic v2 ({_t_py:.3f}s)", x=["Creation time"], y=[_t_py], marker_color="#EF553B"),
        ],
        layout=go.Layout(
            title=f"Construction speed: {N:,} instances",
            barmode="group",
            template="plotly_dark",
            height=320,
            margin=dict(l=50, r=20, t=50, b=30),
            yaxis_title="seconds",
        ),
    )
except Exception:
    SPEED_FIG = go.Figure()

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.CYBORG],
    title="Module 03 — Pydantic v2",
)

app.layout = dbc.Container(
    fluid=True,
    children=[
        dbc.Row(dbc.Col(html.H2("Module 03 — Pydantic v2 Explorer", className="text-center my-4"))),
        dbc.Row(
            dbc.Col(
                dbc.Tabs(
                    id="tabs",
                    active_tab=list(SNIPPETS)[0],
                    children=[dbc.Tab(label=k, tab_id=k) for k in SNIPPETS],
                )
            )
        ),
        dbc.Row([
            dbc.Col([
                html.H5("Code", className="mt-3"),
                dcc.Textarea(
                    id="editor",
                    style={
                        "width": "100%", "height": "380px",
                        "fontFamily": "monospace", "fontSize": "13px",
                        "background": "#1e1e1e", "color": "#d4d4d4",
                        "border": "1px solid #444", "padding": "10px",
                    },
                ),
                dbc.Button("▶ Run", id="run-btn", color="success", className="mt-2"),
            ], width=6),
            dbc.Col([
                html.H5("Output", className="mt-3"),
                html.Pre(
                    id="output",
                    style={
                        "background": "#111", "color": "#0f0",
                        "padding": "10px", "height": "300px",
                        "overflowY": "auto", "border": "1px solid #444",
                        "fontSize": "13px",
                    },
                ),
                dbc.Alert(id="note", color="info", className="mt-2"),
            ], width=6),
        ]),
        dbc.Row(
            dbc.Col(dcc.Graph(figure=SPEED_FIG), width={"size": 8, "offset": 2}),
            className="mt-3",
        ),
        dbc.Row(
            dbc.Col(
                dbc.Card(dbc.CardBody([
                    html.H5("Live Validation Demo"),
                    html.P("Enter a value and see Pydantic validate it in real time."),
                    dbc.Row([
                        dbc.Col(dbc.Input(id="val-name", placeholder="Name (min 2 chars)", type="text"), width=3),
                        dbc.Col(dbc.Input(id="val-email", placeholder="Email address", type="text"), width=3),
                        dbc.Col(dbc.Input(id="val-age", placeholder="Age (1-150)", type="number"), width=2),
                        dbc.Col(dbc.Button("Validate", id="val-btn", color="primary"), width=2),
                    ]),
                    html.Div(id="val-result", className="mt-3"),
                ])),
                width=10,
                className="offset-1 mt-3 mb-5",
            )
        ),
    ],
)


@callback(Output("editor", "value"), Input("tabs", "active_tab"))
def load(tab: str) -> str:
    return SNIPPETS.get(tab, "")


@callback(Output("note", "children"), Input("tabs", "active_tab"))
def note(tab: str) -> str:
    return NOTES.get(tab, "")


@callback(
    Output("output", "children"),
    Input("run-btn", "n_clicks"),
    State("editor", "value"),
    prevent_initial_call=True,
)
def run(_, code: str) -> str:
    import io
    from contextlib import redirect_stdout
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            exec(code, {})  # noqa: S102
    except Exception:
        return traceback.format_exc()
    return buf.getvalue() or "(no output)"


@callback(
    Output("val-result", "children"),
    Input("val-btn", "n_clicks"),
    State("val-name", "value"),
    State("val-email", "value"),
    State("val-age", "value"),
    prevent_initial_call=True,
)
def live_validate(_, name: str | None, email: str | None, age: int | None):
    from pydantic import BaseModel, EmailStr, Field, ValidationError

    class LiveUser(BaseModel):
        name: str = Field(min_length=2)
        email: EmailStr
        age: int = Field(ge=1, le=150)

    try:
        u = LiveUser(name=name or "", email=email or "", age=age or 0)
        return dbc.Alert(
            f"✅ Valid! User: {u.name} <{u.email}>, age {u.age}",
            color="success",
        )
    except Exception as e:
        from pydantic import ValidationError as VE
        if isinstance(e, VE):
            items = [
                html.Li(f"{'.'.join(str(x) for x in err['loc'])}: {err['msg']}")
                for err in e.errors()
            ]
            return dbc.Alert(
                [html.Strong("❌ Validation errors:"), html.Ul(items)],
                color="danger",
            )
        return dbc.Alert(str(e), color="danger")


if __name__ == "__main__":
    print("Open http://127.0.0.1:8050")
    app.run(debug=True)
