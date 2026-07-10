"""
Module 04 — Interactive Dash App: Decision Framework
=====================================================
Run:  python course/04_decision_framework/app.py
Open: http://127.0.0.1:8050
"""
from __future__ import annotations

import timeit

import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import Dash, Input, Output, callback, dcc, html
from dataclasses import dataclass
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Benchmark data
# ---------------------------------------------------------------------------
@dataclass
class _DC:
    x: float
    y: float
    label: str

class _PY(BaseModel):
    x: float
    y: float
    label: str

class _PC:
    def __init__(self, x: float, y: float, label: str) -> None:
        self.x = x
        self.y = y
        self.label = label

N = 100_000
_data = dict(x=1.0, y=2.0, label="test")
_t_pc = timeit.timeit("_PC(**d)", globals={"_PC": _PC, "d": _data}, number=N)
_t_dc = timeit.timeit("_DC(**d)", globals={"_DC": _DC, "d": _data}, number=N)
_t_py = timeit.timeit("_PY(**d)", globals={"_PY": _PY, "d": _data}, number=N)

BENCH_FIG = go.Figure(
    data=[
        go.Bar(name="Plain class", x=["Time (s)"], y=[_t_pc], marker_color="#636EFA"),
        go.Bar(name="@dataclass", x=["Time (s)"], y=[_t_dc], marker_color="#00CC96"),
        go.Bar(name="Pydantic v2", x=["Time (s)"], y=[_t_py], marker_color="#EF553B"),
    ],
    layout=go.Layout(
        title=f"Construction speed — {N:,} instances each",
        barmode="group",
        template="plotly_dark",
        height=340,
        margin=dict(l=50, r=20, t=50, b=30),
        yaxis_title="seconds",
        annotations=[
            dict(
                x="Time (s)", y=_t_py * 1.05,
                text=f"{_t_py/_t_pc:.1f}× slower than plain class",
                showarrow=False, font=dict(color="#EF553B"),
            )
        ],
    ),
)

# Feature matrix
FEATURES = {
    "Feature": [
        "__init__ auto", "__repr__ auto", "__eq__ auto",
        "Runtime validation", "Type coercion",
        "JSON / dict export", "JSON Schema",
        "Env var loading", "Memory (slots)",
        "Inheritance", "Frozen/immutable",
    ],
    "Plain class": ["❌", "❌", "❌", "❌", "❌", "manual", "❌", "❌", "manual", "✅", "manual"],
    "@dataclass": ["✅", "✅", "✅", "❌", "❌", "asdict()", "❌", "❌", "slots=True", "✅ (tricky)", "frozen=True"],
    "Pydantic v2": ["✅", "✅", "✅", "✅", "✅", "model_dump()", "✅", "✅ (Settings)", "❌", "✅", "frozen config"],
}

# ---------------------------------------------------------------------------
# Decision tree nodes
# ---------------------------------------------------------------------------
TREE_FIG = go.Figure()

nodes = {
    "root": (0.5, 1.0, "Need runtime\nvalidation?"),
    "yes_pydantic": (0.85, 0.6, "✅ Use Pydantic\nBaseModel"),
    "data_container": (0.35, 0.6, "Primarily a\ndata container?"),
    "yes_dc": (0.55, 0.25, "✅ Use @dataclass"),
    "behaviour": (0.15, 0.25, "✅ Use plain class"),
    "dc_immutable": (0.75, 0.05, "frozen=True\nslots=True"),
}

edges = [
    ("root", "yes_pydantic", "YES"),
    ("root", "data_container", "NO"),
    ("data_container", "yes_dc", "YES"),
    ("data_container", "behaviour", "NO (behaviour)"),
    ("yes_dc", "dc_immutable", "need immutability?"),
]

for src, dst, label in edges:
    x0, y0, _ = nodes[src]
    x1, y1, _ = nodes[dst]
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    TREE_FIG.add_trace(go.Scatter(
        x=[x0, x1], y=[y0, y1],
        mode="lines",
        line=dict(color="#888", width=2),
        showlegend=False,
        hoverinfo="none",
    ))
    TREE_FIG.add_annotation(x=mx, y=my, text=label, showarrow=False,
                            font=dict(size=10, color="#aaa"))

colors = {"root": "#636EFA", "yes_pydantic": "#EF553B", "data_container": "#636EFA",
          "yes_dc": "#00CC96", "behaviour": "#FECB52", "dc_immutable": "#19D3F3"}
for key, (x, y, text) in nodes.items():
    TREE_FIG.add_trace(go.Scatter(
        x=[x], y=[y],
        mode="markers+text",
        marker=dict(size=40, color=colors.get(key, "#888"), opacity=0.9),
        text=[text],
        textposition="middle center",
        textfont=dict(size=9, color="white"),
        showlegend=False,
        hoverinfo="text",
        hovertext=text,
    ))

TREE_FIG.update_layout(
    title="Decision Tree: Plain class vs @dataclass vs Pydantic",
    template="plotly_dark",
    xaxis=dict(visible=False, range=[-0.05, 1.05]),
    yaxis=dict(visible=False, range=[-0.05, 1.15]),
    height=420,
    margin=dict(l=20, r=20, t=60, b=20),
)

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.CYBORG],
    title="Module 04 — Decision Framework",
)

app.layout = dbc.Container(
    fluid=True,
    children=[
        dbc.Row(dbc.Col(html.H2("Module 04 — When to Use What", className="text-center my-4"))),

        # Decision tree
        dbc.Row(dbc.Col(dcc.Graph(figure=TREE_FIG), width=12)),

        # Speed chart
        dbc.Row(dbc.Col(dcc.Graph(figure=BENCH_FIG), width={"size": 8, "offset": 2}), className="mt-2"),

        # Feature matrix table
        dbc.Row(
            dbc.Col([
                html.H4("Feature Matrix", className="mt-4 mb-2 text-center"),
                dbc.Table(
                    [
                        html.Thead(html.Tr([html.Th(col) for col in FEATURES])),
                        html.Tbody([
                            html.Tr([
                                html.Td(FEATURES["Feature"][i]),
                                html.Td(FEATURES["Plain class"][i], className="text-center"),
                                html.Td(FEATURES["@dataclass"][i], className="text-center"),
                                html.Td(FEATURES["Pydantic v2"][i], className="text-center"),
                            ])
                            for i in range(len(FEATURES["Feature"]))
                        ]),
                    ],
                    bordered=True,
                    hover=True,
                    dark=True,
                    striped=True,
                    responsive=True,
                ),
            ], width=10, className="offset-1"),
        ),

        # Interactive quiz
        dbc.Row(
            dbc.Col(
                dbc.Card(dbc.CardBody([
                    html.H5("Scenario Quiz"),
                    dbc.Select(
                        id="scenario",
                        options=[
                            {"label": "Select a scenario…", "value": ""},
                            {"label": "1. Parsing a FastAPI HTTP request body", "value": "pydantic"},
                            {"label": "2. A service that sends emails", "value": "plain"},
                            {"label": "3. A colour value used in a palette (millions of instances)", "value": "dc_slots"},
                            {"label": "4. App configuration loaded from environment variables", "value": "settings"},
                            {"label": "5. An internal DTO passed between pipeline steps", "value": "dc"},
                            {"label": "6. A repository class that fetches users from DB", "value": "plain"},
                        ],
                    ),
                    html.Div(id="scenario-answer", className="mt-3"),
                ])),
                width={"size": 8, "offset": 2},
                className="mt-3 mb-5",
            )
        ),
    ],
)

ANSWERS: dict[str, tuple[str, str]] = {
    "pydantic": (
        "✅ Pydantic BaseModel",
        "HTTP request bodies come from untrusted external sources. Pydantic validates types, "
        "formats (EmailStr, HttpUrl), and business rules before they touch your application logic.",
    ),
    "plain": (
        "✅ Plain class",
        "Service objects are primarily about behaviour (methods like send_email, fetch_user). "
        "They hold little or no data — a plain class with methods is the right tool.",
    ),
    "dc_slots": (
        "✅ @dataclass(frozen=True, slots=True)",
        "Colours are immutable value objects. frozen=True gives you __hash__ and prevents mutation. "
        "slots=True removes __dict__ for ~40% memory savings — essential when creating millions.",
    ),
    "settings": (
        "✅ Pydantic BaseSettings",
        "BaseSettings reads env vars and .env files, validates types, and hides secrets. "
        "It replaces the anti-pattern of os.environ.get() calls scattered everywhere.",
    ),
    "dc": (
        "✅ @dataclass",
        "Internal DTOs are trusted data — no external input, no validation needed. "
        "@dataclass gives you __init__/__repr__/__eq__ for free without the overhead of Pydantic.",
    ),
}


@callback(Output("scenario-answer", "children"), Input("scenario", "value"))
def answer(val: str):
    if not val or val not in ANSWERS:
        return ""
    title, explanation = ANSWERS[val]
    return dbc.Alert([html.Strong(title), html.Br(), explanation], color="success")


if __name__ == "__main__":
    print("Open http://127.0.0.1:8050")
    app.run(debug=True)
