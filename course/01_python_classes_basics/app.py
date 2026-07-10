"""
Module 01 — Interactive Dash App: Python Classes Explorer
=========================================================
Run:  python course/01_python_classes_basics/app.py
Open: http://127.0.0.1:8050
"""
from __future__ import annotations

import sys
import textwrap
import traceback

import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import Dash, Input, Output, State, callback, dcc, html

# ---------------------------------------------------------------------------
# Sample code snippets shown in the editor tabs
# ---------------------------------------------------------------------------
SNIPPETS: dict[str, str] = {
    "Plain Class": textwrap.dedent("""\
        from __future__ import annotations
        from typing import Self

        class Point:
            def __init__(self, x: float, y: float) -> None:
                self.x = x
                self.y = y

            def __repr__(self) -> str:
                return f"Point(x={self.x!r}, y={self.y!r})"

            def __eq__(self, other: object) -> bool:
                if not isinstance(other, Point):
                    return NotImplemented
                return self.x == other.x and self.y == other.y

            def __hash__(self) -> int:
                return hash((self.x, self.y))

            def translate(self, dx: float, dy: float) -> Self:
                return Point(self.x + dx, self.y + dy)

            def distance_to(self, other: Self) -> float:
                return ((self.x - other.x)**2 + (self.y - other.y)**2)**0.5

        p1 = Point(0, 0)
        p2 = Point(3, 4)
        print(p1.distance_to(p2))   # 5.0
        print(p1 == Point(0, 0))    # True
        print(p1.translate(1, 1))   # Point(x=1, y=1)
    """),
    "Slots": textwrap.dedent("""\
        import sys

        class WithDict:
            def __init__(self, x: float, y: float) -> None:
                self.x = x
                self.y = y

        class WithSlots:
            __slots__ = ("x", "y")
            def __init__(self, x: float, y: float) -> None:
                self.x = x
                self.y = y

        d = WithDict(1.0, 2.0)
        s = WithSlots(1.0, 2.0)
        print("WithDict  bytes:", sys.getsizeof(d.__dict__))
        print("WithSlots bytes:", sys.getsizeof(s))
        # WithSlots has no __dict__ — ~40 % smaller
    """),
    "Properties": textwrap.dedent("""\
        class Temperature:
            def __init__(self, celsius: float) -> None:
                self._celsius = celsius

            @property
            def celsius(self) -> float:
                return self._celsius

            @celsius.setter
            def celsius(self, value: float) -> None:
                if value < -273.15:
                    raise ValueError("Below absolute zero!")
                self._celsius = value

            @property
            def fahrenheit(self) -> float:
                return self._celsius * 9 / 5 + 32

        t = Temperature(100)
        print(t.fahrenheit)   # 212.0
        t.celsius = 0
        print(t.fahrenheit)   # 32.0
        t.celsius = -300      # raises ValueError
    """),
    "Value vs Entity": textwrap.dedent("""\
        import uuid

        # VALUE OBJECT — equality by data
        class Money:
            __slots__ = ("amount", "currency")
            def __init__(self, amount: float, currency: str) -> None:
                self.amount = round(amount, 2)
                self.currency = currency.upper()
            def __eq__(self, other):
                return (self.amount, self.currency) == (other.amount, other.currency)
            def __hash__(self):
                return hash((self.amount, self.currency))
            def __repr__(self):
                return f"Money({self.amount:.2f} {self.currency})"

        # ENTITY OBJECT — equality by identity
        class User:
            def __init__(self, name: str) -> None:
                self.id = str(uuid.uuid4())
                self.name = name
            def __eq__(self, other):
                return self.id == other.id
            def __hash__(self):
                return hash(self.id)

        a = Money(10, "GBP")
        b = Money(10, "GBP")
        print(a == b)   # True  — value object

        u1 = User("Alice")
        u2 = User("Alice")
        print(u1 == u2) # False — entity object
    """),
}

LESSON_NOTES: dict[str, str] = {
    "Plain Class": (
        "A plain class shines when you need **behaviour** (methods) alongside data. "
        "You must manually write `__repr__`, `__eq__`, and `__hash__` — "
        "all of which `@dataclass` will generate for you in Module 2."
    ),
    "Slots": (
        "`__slots__` replaces the per-instance `__dict__` with a compact C array. "
        "Use it when you create **millions** of small objects (e.g., graph nodes, "
        "sensor readings). Memory shrinks ~40-60 %."
    ),
    "Properties": (
        "`@property` lets you expose computed attributes and add validation on "
        "assignment **without** changing the public API. Never use bare `get_x()` "
        "methods in Python — use properties."
    ),
    "Value vs Entity": (
        "**Value objects** are defined by their data — two £10 notes are identical. "
        "**Entity objects** are defined by identity — two users named Alice are "
        "different people. Getting this distinction right shapes every class you write."
    ),
}

# ---------------------------------------------------------------------------
# Memory comparison chart data
# ---------------------------------------------------------------------------
import sys as _sys


class _D:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y


class _S:
    __slots__ = ("x", "y")

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y


_d = _D(1.0, 2.0)
_s = _S(1.0, 2.0)
MEMORY_FIG = go.Figure(
    data=[
        go.Bar(
            name="Without __slots__",
            x=["Instance size (bytes)"],
            y=[_sys.getsizeof(_d) + _sys.getsizeof(_d.__dict__)],
            marker_color="#EF553B",
        ),
        go.Bar(
            name="With __slots__",
            x=["Instance size (bytes)"],
            y=[_sys.getsizeof(_s)],
            marker_color="#00CC96",
        ),
    ],
    layout=go.Layout(
        title="Memory footprint: __dict__ vs __slots__",
        barmode="group",
        template="plotly_dark",
        height=320,
        margin=dict(l=40, r=20, t=50, b=30),
    ),
)

# ---------------------------------------------------------------------------
# App layout
# ---------------------------------------------------------------------------
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.CYBORG],
    title="Module 01 — Python Classes",
)

app.layout = dbc.Container(
    fluid=True,
    children=[
        dbc.Row(
            dbc.Col(
                html.H2(
                    "Module 01 — Python Classes Fundamentals",
                    className="text-center my-4",
                )
            )
        ),
        # Tabs
        dbc.Row(
            dbc.Col(
                dbc.Tabs(
                    id="snippet-tabs",
                    active_tab="Plain Class",
                    children=[
                        dbc.Tab(label=name, tab_id=name) for name in SNIPPETS
                    ],
                ),
                width=12,
            )
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H5("Code", className="mt-3"),
                        dcc.Textarea(
                            id="code-editor",
                            style={
                                "width": "100%",
                                "height": "380px",
                                "fontFamily": "monospace",
                                "fontSize": "13px",
                                "background": "#1e1e1e",
                                "color": "#d4d4d4",
                                "border": "1px solid #444",
                                "padding": "10px",
                            },
                        ),
                        dbc.Button(
                            "▶ Run",
                            id="run-btn",
                            color="success",
                            className="mt-2",
                        ),
                    ],
                    width=6,
                ),
                dbc.Col(
                    [
                        html.H5("Output", className="mt-3"),
                        html.Pre(
                            id="output-pre",
                            style={
                                "background": "#111",
                                "color": "#0f0",
                                "padding": "10px",
                                "height": "280px",
                                "overflowY": "auto",
                                "border": "1px solid #444",
                                "fontSize": "13px",
                            },
                        ),
                        dbc.Alert(id="lesson-note", color="info", className="mt-2"),
                    ],
                    width=6,
                ),
            ]
        ),
        # Memory chart
        dbc.Row(
            dbc.Col(
                dcc.Graph(figure=MEMORY_FIG, id="memory-chart"),
                width={"size": 6, "offset": 3},
            ),
            className="mt-3",
        ),
        # Quiz
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H5("Quick Quiz"),
                            html.P(
                                "Two instances of a User class with the same name — are they equal?"
                            ),
                            dbc.RadioItems(
                                id="quiz-radio",
                                options=[
                                    {"label": "Yes — same name means same user", "value": "yes"},
                                    {
                                        "label": "No — users are entities; equality is by identity (id)",
                                        "value": "no",
                                    },
                                    {"label": "Depends on __eq__ implementation", "value": "dep"},
                                ],
                                inline=False,
                            ),
                            dbc.Button(
                                "Check Answer",
                                id="quiz-btn",
                                color="primary",
                                className="mt-2",
                            ),
                            html.Div(id="quiz-result", className="mt-2"),
                        ]
                    )
                ),
                width=8,
                className="offset-2 mt-3 mb-5",
            )
        ),
    ],
)


# ---------------------------------------------------------------------------
# Callbacks
# ---------------------------------------------------------------------------
@callback(Output("code-editor", "value"), Input("snippet-tabs", "active_tab"))
def load_snippet(tab: str) -> str:
    return SNIPPETS.get(tab, "")


@callback(Output("lesson-note", "children"), Input("snippet-tabs", "active_tab"))
def load_note(tab: str) -> str:
    return LESSON_NOTES.get(tab, "")


@callback(
    Output("output-pre", "children"),
    Input("run-btn", "n_clicks"),
    State("code-editor", "value"),
    prevent_initial_call=True,
)
def run_code(_, code: str) -> str:
    if not code:
        return ""
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
    Output("quiz-result", "children"),
    Input("quiz-btn", "n_clicks"),
    State("quiz-radio", "value"),
    prevent_initial_call=True,
)
def check_quiz(_, answer: str | None) -> dbc.Alert:
    if answer == "no":
        return dbc.Alert(
            "✅ Correct! Users are entity objects — equality is based on unique identity (id), "
            "not attribute values. Two users named Alice are different people.",
            color="success",
        )
    if answer == "dep":
        return dbc.Alert(
            "⚠️ Partially right — it *does* depend on __eq__, but the best-practice design "
            "for entity objects is identity-based equality (by id).",
            color="warning",
        )
    return dbc.Alert(
        "❌ Not quite. Even if two users share a name, they are distinct entities. "
        "Plain data equality would be correct for *value objects* like Money.",
        color="danger",
    )


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("Open http://127.0.0.1:8050")
    app.run(debug=True)
