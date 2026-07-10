"""
Module 05 — Interactive Dash App: Advanced Patterns Explorer
============================================================
Run:  python course/05_advanced_patterns/app.py
Open: http://127.0.0.1:8050
"""
from __future__ import annotations

import textwrap
import traceback

import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, State, callback, dcc, html

SNIPPETS: dict[str, str] = {
    "Generic Page[T]": textwrap.dedent("""\
        from dataclasses import dataclass, field
        from typing import Generic, TypeVar, Iterator

        T = TypeVar("T")

        @dataclass
        class Page(Generic[T]):
            items: list[T]
            total: int
            page: int = 1
            page_size: int = 10

            @property
            def total_pages(self) -> int:
                return max(1, -(-self.total // self.page_size))

            def __iter__(self) -> Iterator[T]:
                return iter(self.items)

        @dataclass
        class User:
            name: str
            email: str

        users = [User(f"User{i}", f"u{i}@x.com") for i in range(25)]
        page = Page(items=users[:10], total=25)
        print(f"Page {page.page}/{page.total_pages}")
        for u in page:
            print(f"  {u.name}")
    """),
    "Result[T] Monad": textwrap.dedent("""\
        from dataclasses import dataclass
        from typing import Generic, TypeVar

        T = TypeVar("T")

        @dataclass
        class Result(Generic[T]):
            _value: T | None = None
            _error: str | None = None

            @classmethod
            def ok(cls, value: T) -> "Result[T]":
                return cls(_value=value)

            @classmethod
            def err(cls, msg: str) -> "Result[T]":
                return cls(_error=msg)

            @property
            def is_ok(self) -> bool:
                return self._error is None

            @property
            def value(self) -> T:
                if self._error:
                    raise ValueError(self._error)
                return self._value

            def __repr__(self) -> str:
                return f"Ok({self._value!r})" if self.is_ok else f"Err({self._error!r})"

        def divide(a: float, b: float) -> Result[float]:
            if b == 0:
                return Result.err("division by zero")
            return Result.ok(a / b)

        print(divide(10, 2))   # Ok(5.0)
        print(divide(10, 0))   # Err('division by zero')
        r = divide(10, 2)
        print(r.value * 3)     # 15.0
    """),
    "Protocol + Repository": textwrap.dedent("""\
        from dataclasses import dataclass, field
        from typing import Protocol, Generic, TypeVar, runtime_checkable
        from uuid import uuid4

        @runtime_checkable
        class Identifiable(Protocol):
            id: str

        T = TypeVar("T", bound=Identifiable)

        class Repo(Generic[T]):
            def __init__(self):
                self._store: dict[str, T] = {}

            def save(self, item: T) -> T:
                self._store[item.id] = item
                return item

            def get(self, id: str) -> T | None:
                return self._store.get(id)

            def all(self) -> list[T]:
                return list(self._store.values())

        @dataclass
        class User:
            name: str
            id: str = field(default_factory=lambda: str(uuid4())[:8])

        repo: Repo[User] = Repo()
        u = repo.save(User("Alice"))
        print("Saved:", u)
        print("Found:", repo.get(u.id))
        print("All:", repo.all())
        print("Is Identifiable:", isinstance(u, Identifiable))
    """),
    "Recursive Pydantic": textwrap.dedent("""\
        from pydantic import BaseModel, Field
        from uuid import uuid4

        class Category(BaseModel):
            id: str = Field(default_factory=lambda: str(uuid4())[:8])
            name: str
            children: list["Category"] = []

            def depth(self) -> int:
                if not self.children:
                    return 0
                return 1 + max(c.depth() for c in self.children)

            def flatten(self) -> list["Category"]:
                result = [self]
                for c in self.children:
                    result.extend(c.flatten())
                return result

        Category.model_rebuild()

        tree = Category(name="Tech", children=[
            Category(name="Laptops", children=[
                Category(name="Gaming"),
                Category(name="Ultrabooks"),
            ]),
            Category(name="Phones"),
        ])
        print("Depth:", tree.depth())
        print("All:", [c.name for c in tree.flatten()])
    """),
    "Pydantic + Dataclass Layer": textwrap.dedent("""\
        from pydantic import BaseModel, Field
        from dataclasses import dataclass, field
        from uuid import uuid4

        # API layer: validates input
        class CreateUserReq(BaseModel):
            name: str = Field(min_length=2)
            email: str = Field(pattern=r"^[^@]+@[^@]+$")

        # Domain layer: internal logic
        @dataclass
        class User:
            name: str
            email: str
            id: str = field(default_factory=lambda: str(uuid4())[:8])

            @classmethod
            def from_request(cls, req: CreateUserReq) -> "User":
                return cls(name=req.name, email=req.email)

        # Read model: serialise back
        class UserResp(BaseModel):
            id: str
            name: str
            email: str

            @classmethod
            def from_domain(cls, u: User) -> "UserResp":
                return cls(id=u.id, name=u.name, email=u.email)

        req = CreateUserReq(name="Alice", email="alice@x.com")
        user = User.from_request(req)
        resp = UserResp.from_domain(user)
        print("Request:", req)
        print("Domain:", user)
        print("Response JSON:", resp.model_dump_json(indent=2))
    """),
}

NOTES: dict[str, str] = {
    "Generic Page[T]": (
        "Generic dataclasses use `TypeVar` and `Generic[T]` from `typing`. "
        "The type parameter provides full IDE autocompletion — `Page[User]` knows "
        "its `.items` are `list[User]`."
    ),
    "Result[T] Monad": (
        "The Result monad (railway-oriented programming) wraps either a value or an error "
        "without raising exceptions. This makes error paths explicit and forces callers "
        "to handle both cases. Use it for fallible operations like DB queries or API calls."
    ),
    "Protocol + Repository": (
        "Protocol defines a structural interface — any class with the right attributes/methods "
        "satisfies it without explicit inheritance. Combined with generics, you get a fully "
        "typed, reusable repository that works with any domain entity."
    ),
    "Recursive Pydantic": (
        "Self-referential Pydantic models require `model_rebuild()` after the class definition "
        "to resolve the forward reference. Use them for trees, nested categories, comment threads, "
        "and any hierarchical data structure."
    ),
    "Pydantic + Dataclass Layer": (
        "Best-practice architecture: Pydantic at the **boundary** (HTTP, CLI, config) for validation, "
        "dataclasses in the **domain** for fast internal processing, and Pydantic read-models at the "
        "**output** boundary for serialisation. Each layer does exactly one thing."
    ),
}

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.CYBORG],
    title="Module 05 — Advanced Patterns",
)

app.layout = dbc.Container(
    fluid=True,
    children=[
        dbc.Row(dbc.Col(html.H2("Module 05 — Advanced Patterns", className="text-center my-4"))),
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
                        "width": "100%", "height": "420px",
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
                        "padding": "10px", "height": "340px",
                        "overflowY": "auto", "border": "1px solid #444",
                        "fontSize": "13px",
                    },
                ),
                dbc.Alert(id="note", color="info", className="mt-2"),
            ], width=6),
        ]),
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


if __name__ == "__main__":
    print("Open http://127.0.0.1:8050")
    app.run(debug=True)
