"""
Module 02 — Interactive Dash App: Dataclasses Explorer
=======================================================
Run:  python course/02_dataclasses/app.py
Open: http://127.0.0.1:8050
"""
from __future__ import annotations

import sys
import textwrap
import timeit
import traceback

import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import Dash, Input, Output, State, callback, dcc, html
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Code snippets
# ---------------------------------------------------------------------------
SNIPPETS: dict[str, str] = {
    "Basic @dataclass": textwrap.dedent("""\
        from dataclasses import dataclass, field

        @dataclass
        class Config:
            host: str = "localhost"
            port: int = 8080
            debug: bool = False
            tags: list[str] = field(default_factory=list)

        c1 = Config()
        c2 = Config(port=9090, debug=True)
        c1.tags.append("web")
        print(c1)          # Config(host='localhost', port=8080, ...)
        print(c2)
        print(c1 == c2)    # False
        print(c1.tags, c2.tags)  # ['web'] []  — independent lists
    """),
    "Frozen + Slots": textwrap.dedent("""\
        from dataclasses import dataclass

        @dataclass(frozen=True, slots=True)
        class Colour:
            r: int
            g: int
            b: int
            a: int = 255

            def to_hex(self):
                return f"#{self.r:02X}{self.g:02X}{self.b:02X}"

        red  = Colour(255, 0, 0)
        blue = Colour(0, 0, 255)
        print(red.to_hex())    # #FF0000
        print(hash(red))       # stable (frozen + hashable)
        print({red, blue})     # set of colours

        try:
            red.r = 128        # raises FrozenInstanceError
        except Exception as e:
            print(type(e).__name__, e)
    """),
    "KW_ONLY": textwrap.dedent("""\
        from dataclasses import dataclass, KW_ONLY

        @dataclass
        class APIRequest:
            method: str
            path: str
            _: KW_ONLY          # everything after is keyword-only
            timeout: float = 30.0
            retries: int = 3

        r = APIRequest("GET", "/api/users", timeout=5.0)
        print(r)

        # This would raise TypeError (no positional after KW_ONLY):
        # APIRequest("GET", "/api/users", 5.0)
    """),
    "StrEnum (3.11)": textwrap.dedent("""\
        from dataclasses import dataclass, field
        from enum import StrEnum

        class Status(StrEnum):
            PENDING   = "pending"
            ACTIVE    = "active"
            CANCELLED = "cancelled"

        @dataclass
        class Task:
            title: str
            status: Status = Status.PENDING

            def activate(self):
                return Task(self.title, Status.ACTIVE)

        t = Task("Write tests")
        print(t)
        print(t.status == "pending")   # True — StrEnum IS a str
        print(t.activate())
    """),
    "ExceptionGroup (3.11)": textwrap.dedent("""\
        from dataclasses import dataclass

        @dataclass
        class Form:
            username: str
            email: str
            age: int

            def validate(self):
                errors = []
                if len(self.username) < 3:
                    errors.append(ValueError(f"username too short"))
                if "@" not in self.email:
                    errors.append(ValueError(f"invalid email"))
                if not 0 <= self.age <= 150:
                    errors.append(ValueError(f"invalid age: {self.age}"))
                if errors:
                    raise ExceptionGroup("validation failed", errors)

        f = Form("ab", "not-email", 999)
        try:
            f.validate()
        except ExceptionGroup as eg:
            print(eg.message, "—", len(eg.exceptions), "errors")
            for e in eg.exceptions:
                print(" •", e)
    """),
}

NOTES: dict[str, str] = {
    "Basic @dataclass": (
        "`@dataclass` generates `__init__`, `__repr__`, and `__eq__` automatically. "
        "Always use `field(default_factory=list)` for mutable defaults — never "
        "`tags: list = []` which would share the list across all instances."
    ),
    "Frozen + Slots": (
        "`frozen=True` makes the dataclass immutable (like a namedtuple) and enables "
        "`__hash__`. `slots=True` removes `__dict__` for ~40% memory savings. "
        "Together they form the ideal **value object** in Python."
    ),
    "KW_ONLY": (
        "`KW_ONLY` (Python 3.10+) is a sentinel field that forces all subsequent fields "
        "to be keyword-only arguments. This prevents positional argument order mistakes "
        "and makes API call sites more readable."
    ),
    "StrEnum (3.11)": (
        "`StrEnum` (Python 3.11) makes enum members that *are* strings — no `.value` "
        "needed. Perfect for status fields stored in databases or returned in JSON APIs."
    ),
    "ExceptionGroup (3.11)": (
        "`ExceptionGroup` (Python 3.11) lets you raise *all* validation errors at once "
        "instead of stopping at the first. Use `except*` syntax to handle specific types "
        "within the group."
    ),
}

# ---------------------------------------------------------------------------
# Benchmark chart
# ---------------------------------------------------------------------------
@dataclass(slots=True)
class _WithSlots:
    x: float
    y: float
    z: float

@dataclass
class _WithoutSlots:
    x: float
    y: float
    z: float

N = 200_000
_t_slots = timeit.timeit("_WithSlots(1.0, 2.0, 3.0)", globals={"_WithSlots": _WithSlots}, number=N)
_t_plain = timeit.timeit("_WithoutSlots(1.0, 2.0, 3.0)", globals={"_WithoutSlots": _WithoutSlots}, number=N)

BENCH_FIG = go.Figure(
    data=[
        go.Bar(
            name=f"slots=True  ({_t_slots:.3f}s)",
            x=["Creation time"],
            y=[_t_slots],
            marker_color="#00CC96",
        ),
        go.Bar(
            name=f"No slots  ({_t_plain:.3f}s)",
            x=["Creation time"],
            y=[_t_plain],
            marker_color="#EF553B",
        ),
    ],
    layout=go.Layout(
        title=f"Dataclass creation: slots=True vs default ({N:,} instances)",
        barmode="group",
        template="plotly_dark",
        height=320,
        margin=dict(l=50, r=20, t=50, b=30),
        yaxis_title="seconds",
    ),
)

# memory
_ws = _WithSlots(1.0, 2.0, 3.0)
_wos = _WithoutSlots(1.0, 2.0, 3.0)
MEM_FIG = go.Figure(
    data=[
        go.Bar(
            name="slots=True",
            x=["Bytes per instance"],
            y=[sys.getsizeof(_ws)],
            marker_color="#00CC96",
        ),
        go.Bar(
            name="No slots",
            x=["Bytes per instance"],
            y=[sys.getsizeof(_wos) + sys.getsizeof(_wos.__dict__)],
            marker_color="#EF553B",
        ),
    ],
    layout=go.Layout(
        title="Memory per instance",
        barmode="group",
        template="plotly_dark",
        height=320,
        margin=dict(l=50, r=20, t=50, b=30),
        yaxis_title="bytes",
    ),
)

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.CYBORG],
    title="Module 02 — Dataclasses",
)

app.layout = dbc.Container(
    fluid=True,
    children=[
        dbc.Row(dbc.Col(html.H2("Module 02 — Dataclasses Deep-Dive", className="text-center my-4"))),
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
                        "width": "100%", "height": "360px",
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
                        "padding": "10px", "height": "280px",
                        "overflowY": "auto", "border": "1px solid #444",
                        "fontSize": "13px",
                    },
                ),
                dbc.Alert(id="note", color="info", className="mt-2"),
            ], width=6),
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=BENCH_FIG), width=6),
            dbc.Col(dcc.Graph(figure=MEM_FIG), width=6),
        ], className="mt-3"),
        # Decision quiz
        dbc.Row(
            dbc.Col(
                dbc.Card(dbc.CardBody([
                    html.H5("Quiz: Which decorator flag should you use?"),
                    html.P("You're building a colour palette library. Colours should be immutable, "
                           "hashable, and you'll create millions of them. What do you do?"),
                    dbc.RadioItems(
                        id="quiz",
                        options=[
                            {"label": "@dataclass  (no flags)", "value": "a"},
                            {"label": "@dataclass(frozen=True)", "value": "b"},
                            {"label": "@dataclass(frozen=True, slots=True)", "value": "c"},
                            {"label": "Use a plain class with __slots__", "value": "d"},
                        ],
                    ),
                    dbc.Button("Check", id="quiz-btn", color="primary", className="mt-2"),
                    html.Div(id="quiz-result", className="mt-2"),
                ])),
                width={"size": 8, "offset": 2},
                className="mt-3 mb-5",
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
    Output("quiz-result", "children"),
    Input("quiz-btn", "n_clicks"),
    State("quiz", "value"),
    prevent_initial_call=True,
)
def quiz(_, answer: str | None) -> dbc.Alert:
    if answer == "c":
        return dbc.Alert(
            "✅ Perfect! frozen=True makes colours immutable and hashable. "
            "slots=True removes __dict__ for minimum memory when creating millions.",
            color="success",
        )
    if answer == "b":
        return dbc.Alert(
            "⚠️ Almost! frozen=True is correct, but add slots=True too when "
            "creating millions of instances to save ~40% memory per object.",
            color="warning",
        )
    if answer == "d":
        return dbc.Alert(
            "⚠️ Works, but you'd write a lot of boilerplate. @dataclass(frozen=True, slots=True) "
            "gives you everything automatically.",
            color="warning",
        )
    return dbc.Alert(
        "❌ Not ideal. Without frozen=True the colour can be mutated; without slots=True "
        "you carry the overhead of __dict__ for every instance.",
        color="danger",
    )


if __name__ == "__main__":
    print("Open http://127.0.0.1:8050")
    app.run(debug=True)
