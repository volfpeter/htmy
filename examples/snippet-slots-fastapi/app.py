from fastapi import FastAPI
from fasthx.htmy import HTMY, CurrentRequest

from htmy import ComponentType, Context, Fragment, Slots, Snippet, component, html


def layout(*children: ComponentType) -> Snippet:
    """
    Creates a `Snippet` that's configured to render `layout.html` with the given children
    components replacing the `content` slot.
    """
    return Snippet(
        "layout.html",  # Path to the HTML snippet.
        Slots({"content": children}),  # Render all children in the "content" slot.
    )


def centered(*children: ComponentType) -> Snippet:
    """
    Component factory that creates a `Snippet` configured to render `centered.html` with the
    given children components replacing the `content` slot.
    """
    return Snippet(
        "centered.html",  # Path to the HTML snippet.
        Slots({"content": children}),  # Render all children in the "content" slot.
    )


@component.context_only
def request_headers(context: Context) -> ComponentType:
    """Context-only function component that displays all the headers in the current request."""
    # Load the current request from the context.
    request = CurrentRequest.from_context(context)
    return html.div(
        html.h2("Request headers:", class_="text-lg font-semibold pb-2"),
        html.div(
            *(
                # Convert header name and value pairs to fragments.
                Fragment(html.label(name + ":"), html.label(value))
                for name, value in request.headers.items()
            ),
            class_="grid grid-cols-[max-content_1fr] gap-2",
        ),
    )


def index_page(_: None) -> Snippet:
    """
    Component factory that returns the index page.

    Note that this function is not an `htmy` component at all, just a
    component factory that `fasthx` decorators can resolve. It must
    accept a single argument (the return value of the route) and return
    the component(s) that should be rendered.
    """
    return layout(centered(request_headers()))


app = FastAPI()
"""The FastAPI application."""

htmy = HTMY()
"""
The `HTMY` instance (from `FastHX`) that takes care of component rendering
through its route decorators.
"""


@app.get("/")
@htmy.page(index_page)
async def index() -> None:
    """The index route. It has no business logic, so it can remain empty."""
    ...
