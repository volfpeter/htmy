from fastapi import FastAPI
from fasthx.htmy import HTMY, CurrentRequest
from jinja2 import Environment, FileSystemLoader

from htmy import ComponentType, Context, Fragment, Renderer, component, html
from htmy.jinja import JinjaTemplate, JinjaTemplates


def layout(*children: ComponentType) -> JinjaTemplate:
    """
    Creates a `JinjaTemplate` that's configured to render `layout.jinja` with the given children
    components replacing the `content` slot.
    """
    return JinjaTemplate(
        "layout.jinja",  # Path to the Jinja template.
        slots={"content": children},  # Render all children in the "content" slot.
    )


def centered(*children: ComponentType) -> JinjaTemplate:
    """
    Component factory that creates a `JinjaTemplate` configured to render `centered.jinja` with
    the given children components replacing the `content` slot.
    """
    return JinjaTemplate(
        "centered.jinja",  # Path to the Jinja template.
        slots={"content": children},  # Render all children in the "content" slot.
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


def index_page(_: None) -> JinjaTemplate:
    """
    Component factory that returns the index page.

    Note that this function is not an `htmy` component at all, just a
    component factory that `fasthx` decorators can resolve. It must
    accept a single argument (the return value of the route) and return
    the component(s) that should be rendered.
    """
    return layout(centered(request_headers()))


jinja_templates = JinjaTemplates(Environment(loader=FileSystemLoader("."), autoescape=True))
"""Jinja templates that `htmy` `JinjaTemplate` components should use."""

htmy_renderer = Renderer(default_context=jinja_templates.to_context())
"""
`htmy` renderer whose default context includes the `jinja_templates` instance
so `htmy` components can access it from their context.
"""

htmy = HTMY(renderer=htmy_renderer)
"""
The `HTMY` instance that takes care of component rendering through
its route decorators. It uses the pre-configured renderer which has
`jinja_templates` in its default context.
"""

app = FastAPI()
"""The FastAPI application."""


@app.get("/")
@htmy.page(index_page)
async def index() -> None:
    """The index route. It has no business logic, so it can remain empty."""
    ...
