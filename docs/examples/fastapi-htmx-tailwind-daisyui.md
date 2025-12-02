# FastAPI with HTMX, TailwindCSS, and DaisyUI

First you must install all the necessary libraries (`FastAPI`, `uvicorn`, and `htmy`), for example like this:

```console
$ pip install fastapi uvicorn htmy
```

You should be able to follow how components work and how the context can be used even without being familiar with [HTMX](https://htmx.org/), [TailwindCSS](https://tailwindcss.com/), and [DaisyUI](https://daisyui.com/), just ignore the styling and the `hx_*` attributes. But if you plan to play with this example, minimal familiarity with these tools will be very helpful.

Now you should create an `app.py` file with this content:

```python
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse

from htmy import Component, ComponentType, Context, Renderer, component, html, is_component_sequence


@dataclass
class User:
    """Some user data model for the application."""

    name: str
    preferred_theme: str


def make_htmy_context(request: Request) -> Context:
    """Creates the base htmy context for rendering."""
    # The context will map the `Request` type to the current request and the User class
    # to the current user. This is similar to what the `ContextAware` utility does, but
    # simpler. With this context, components will be able to easily access the request
    # and the user if they need it.
    return {Request: request, User: User(name="Paul", preferred_theme="dark")}


RendererFunction = Callable[[Component], Awaitable[HTMLResponse]]


def render(request: Request) -> RendererFunction:
    """FastAPI dependency that returns an htmy renderer function."""

    async def exec(component: Component) -> HTMLResponse:
        # Note that we add the result of `make_htmy_context()` as the default context to
        # the renderer. This way wherever this function is used for rendering in routes,
        # every rendered component will be able to access the current request and user.
        renderer = Renderer(make_htmy_context(request))
        return HTMLResponse(await renderer.render(component))

    return exec


DependsRenderFunc = Annotated[RendererFunction, Depends(render)]


@component
def page(content: ComponentType, context: Context) -> Component:
    """
    Page component that wraps the given `content` in the `<body>` tag.

    This is just the base page layout component with all the necessary metadata and some styling.
    """
    # Take the user from the context, so we can set the page theme (through DaisyUI).
    user: User = context[User]
    return (
        html.DOCTYPE.html,
        html.html(
            html.head(
                # Some metadata
                html.title("Demo"),
                html.Meta.charset(),
                html.Meta.viewport(),
                # TailwindCSS and DaisyUI
                html.script(src="https://cdn.tailwindcss.com"),
                html.Link.css("https://cdn.jsdelivr.net/npm/daisyui@4.12.11/dist/full.min.css"),
                # HTMX
                html.script(src="https://unpkg.com/htmx.org@2.0.2"),
            ),
            html.body(
                content,
                data_theme=user.preferred_theme,
                class_="h-screen w-screen",
            ),
            lang="en",
        ),
    )


@component
def center(content: Component, context: Context) -> Component:
    """Component that shows its content in the center of the available space."""
    return html.div(
        *(content if is_component_sequence(content) else [content]),
        class_="flex flex-col w-full h-full items-center justify-center gap-4",
    )


@component
def counter(value: int, context: Context) -> Component:
    """
    Counter button with HTMX functionality.

    Whenever the button is clicked, a request will be sent to the server and the
    button will be re-rendered with the new value of the counter.
    """
    # Attribute names will automatically be converted to "hx-*" and "class".
    return html.button(
        f"Click {value} times.",
        hx_trigger="click",
        hx_swap="outerHTML",
        hx_post=f"/counter-click?value={value}",
        class_="btn btn-primary",
    )


@component
def welcome_message(props: None, context: Context) -> Component:
    """Welcome message component."""
    # Take the request and the user from the context for use in the component.
    request: Request = context[Request]
    user: User = context[User]
    return center(
        (
            html.h1(f'Welcome {user.name} at "{request.url.path}"!'),
            counter(0),
        )
    )


app = FastAPI()


@app.get("/")
async def index(render: DependsRenderFunc) -> HTMLResponse:
    """The index page of the application."""
    return await render(page(welcome_message(None)))


@app.post("/counter-click")
async def counter_click(value: int, render: DependsRenderFunc) -> HTMLResponse:
    """HTMX route that handles counter button clicks by re-rendering the button with the new value."""
    return await render(counter(value + 1))

```

Finally, you can run the application like this:

```console
$ uvicorn app:app --reload
```

You can now open the application at `localhost:8000`.
