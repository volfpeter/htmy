# Slot rendering with Jinja

`htmy` is designed to be compatible with other templating libraries through wrappers. This example demonstrates how you can use the built-in `JinjaTemplate` component to render [Jinja](https://jinja.palletsprojects.com/) templates and replace slots in them with `htmy` components dynamically.

In the example, we will build a `FastAPI` application that will serve our components using the `FastHX` library. Let's start by installing the required dependencies: `pip install fastapi fasthx "htmy[jinja]" uvicorn`.

We will use TailwindCSS v4 for styling, but it will be loaded from a CDN, so we don't need any JavaScript tooling. Also, you don't need to be familiar with TailwindCSS to understand the example, just ignore the styling.

Our project structure will look like this:

- `layout.jinja`: The Jinja template for `layout`.
- `centered.jinja`: The Jinja template for `centered`.
- `app.py`: All our `htmy` components, the Jinja setup, and the `FastAPI` application.

Let's start by creating the `layout.jinja` file. Layouts often require a deeply nested component structure, so it's a good idea to use Jinja for them with dynamic slot rendering, because it improves performance and you can write almost the entire HTML structure in Jinja templates.

```jinja
<!DOCTYPE html>
<html lang="en">
  <head>
    <title>Jinja with Slots</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <script src="https://unpkg.com/@tailwindcss/browser@4"></script>
  </head>
  <body class="w-screen h-screen bg-gray-300 dark:bg-gray-800 dark:text-white">
    <div class="w-full grid grid-rows-[max-content,1fr] p-8 gap-4">
      <p class="text-center">
        <span class="font-semibold text-lg">Technologies:</span>
        <a
          href="https://volfpeter.github.io/htmy/"
          class="text-blue-600 visited:text-purple-600"
          target="_blank"
          >htmy</a>,
        <a
          href="https://volfpeter.github.io/fasthx/"
          class="text-blue-600 visited:text-purple-600"
          target="_blank"
          >FastHX</a>,
        <a
          href="https://fastapi.tiangolo.com/"
          class="text-blue-600 visited:text-purple-600"
          target="_blank"
          >FastAPI</a>,
        <a
          href="https://jinja.palletsprojects.com/"
          class="text-blue-600 visited:text-purple-600"
          target="_blank"
          >Jinja</a>,
        <a
          href="https://tailwindcss.com/"
          class="text-blue-600 visited:text-purple-600"
          target="_blank"
          >TailwindCSSv4</a>.
      </p>
      <div class="h-full w-full">
        {{ slots.content }}
      </div>
    </div>
  </body>
</html>
```

As you can see, we have the basic HTML document definition and some static content in this file, including a `{{ slots.content }}` expression, which will be replaced by `htmy` components during rendering.

Next, we create the `centered.jinja` file, which will be a lot simpler. Actually, it's so simple we shouldn't even use Jinja for it (a plain `htmy` component would be simpler and more efficient), but we will, just to showcase multiple `JinjaTemplate` usage patterns.

```jinja
<div class="flex flex-col w-full h-full items-center justify-center">
  {{ slots.content }}
</div>
```

This template also contains a `{{ slots.content }}` expression, but the slot's key (`content`) could be anything else. The important thing, as you'll see below, is that the `slots` argument of the `JinjaTemplate()` contains the right component for the right slot key.

We have all the Jinja templates we need, so we can finally get started with the application in `app.py`. We will do it step by step, starting with the imports and the `layout` component factory:

```python
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
```

In this case, `layout` is not an `htmy` component, it's just a simple component factory that returns a `JinjaTemplate` that's configured to load the `layout.jinja` file we previously created, and render the given children components in place of the `content` slot.

Now we can implement `centered`, another component factory. Since it only wraps its children and doesn't need access to the rendering context, a factory is the simplest and most efficient choice.

```python
def centered(*children: ComponentType) -> JinjaTemplate:
    """
    Component factory that creates a `JinjaTemplate` configured to render `centered.jinja` with
    the given children components replacing the `content` slot.
    """
    return JinjaTemplate(
        "centered.jinja",  # Path to the Jinja template.
        slots={"content": children},  # Render all children in the "content" slot.
    )
```

We create one more component - `request_headers` - just to have something that's not built with Jinja. It requires access to the current request from the `htmy` rendering context - loaded via the `CurrentRequest` `fasthx` utility -, so we use a real component in this case. Is has no properties, so a context-only function component is a good choice:

```python
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
```

Next we create the function that returns the content of the index page:

```python
def index_page(_: None) -> JinjaTemplate:
    """
    Component factory that returns the index page.

    Note that this function is not an `htmy` component at all, just a
    component factory that `fasthx` decorators can resolve. It must
    accept a single argument (the return value of the route) and return
    the component(s) that should be rendered.
    """
    return layout(centered(request_headers()))
```

`index_page()`, similarly to `layout()` and `centered()`, is also not a component, just a function that returns a component. Specifically, it shows the `request_headers` component, centered in the page. We don't really need this function, we could use `lambda _: layout(centered(request_headers()))` instead in the `FastHX` `page()` decorator, but the example is more readable and easier to follow this way.

We need a little bit of setup before creating the FastAPI, to let `htmy` load and render Jinja templates. This is a 3-step process:

- Create an `htmy.jinja.JinjaTemplates` instance with a Jinja environment.
- Create and `htmy.Renderer` instance whose default context includes the `JinjaTemplates` instance, allowing `htmy.jinja.JinjaTemplate` components to load it from the `htmy` context to render Jinja templates.
- Create a `fasthx.htmy.HTMY` instance that uses the pre-configured `htmy` renderer.

```python
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
```

Finally, everything is ready, we can create the FastAPI application and register a route for the index page:

```python
app = FastAPI()
"""The FastAPI application."""


@app.get("/")
@htmy.page(index_page)
async def index() -> None:
    """The index route. It has no business logic, so it can remain empty."""
    ...
```

The `@htmy.page()` decorator takes care of rendering the result of the `index()` route with the component the `index_page()` function returns. We configured the `HTMY` instance's renderer to have `jinja_templates` in its default context, so every `JinjaTemplate` component will be able to load templates from the current directory.

The only thing that remains is to run the application with `python -m uvicorn app:app`, open http://127.0.0.1:8000 in the browser, and see the result of our work.
