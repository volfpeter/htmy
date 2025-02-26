# Slot rendering with `Snippet`

The built-in `Snippet` component can appear a bit intimidating at first with its relatively abstract, but quite powerful text processing features (`TextResolved` and `TextProcessor`), but it's actually quite simple to use. This example demonstrates how you can use it together with `Slots` to render plain `.html` files and replace slots in them with `htmy` components dynamically.

In the example, we will build a `FastAPI` application that will serve our components using the `FastHX` library. Let's start by installing the required dependencies: `pip install fastapi fasthx htmy uvicorn`.

We will use TailwindCSS v4 for styling, but it will be loaded from a CDN, so we don't need any JavaScript tooling. Also, you don't need to be familiar with TailwindCSS to understand the example, just ignore the styling.

One additional note, before we start coding: the `MD` component (for markdown rendering) supports all the features of `Snippet`, so you can directly use all the patterns in this example with markdown files and the `MD` component.

Our project structure will look like this:

- `layout.html`: The HTML snippet for the `layout` `htmy` component.
- `centered.html`: The HTML snippet for the `Centered` `htmy` component.
- `app.py`: All our `htmy` components and the `FastAPI` application.

Let's start by creating the `layout.html` file. Layouts often require a deeply nested component structure, so it's a good idea to use `Snippet` for then with dynamic slot rendering, because it improves performance and you can write almost the entire HTML structure in native `.html` files (without custom syntax).

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <title>Snippet with Slots</title>
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
          >htmy</a
        >,
        <a
          href="https://volfpeter.github.io/fasthx/"
          class="text-blue-600 visited:text-purple-600"
          target="_blank"
          >FastHX</a
        >,
        <a
          href="https://fastapi.tiangolo.com/"
          class="text-blue-600 visited:text-purple-600"
          target="_blank"
          >FastAPI</a
        >,
        <a
          href="https://tailwindcss.com/"
          class="text-blue-600 visited:text-purple-600"
          target="_blank"
          >TailwindCSSv4</a
        >.
      </p>
      <div class="h-full w-full">
        <!-- slot[content] -->
      </div>
    </div>
  </body>
</html>
```

As you can see, we have the basic HTML document definition and some static content in this file, including a `<!-- slot[content] -->` marker (plain HTML comment), which will be resolved by `Snippet` to the correct `htmy` component during rendering.

Next, we will create the `centered.html` file, which will be a lot simpler. Actually, it's so simple we shouldn't even use `Snippet` for it (a plain `htmy` component would be simpler and more efficient), but we will, just to showcase multiple `Snippet` usage patterns.

```html
<div class="flex flex-col w-full h-full items-center justify-center">
  <!-- slot[content] -->
</div>
```

This HTML file also contains a `<!-- slot[content] -->` marker, but the slot's key (`content`) could be anything else. The important thing, as you'll see below, is that the `Slots()` instance of the `Snippet()` contains the right component for the right slot key.

We have all the HTML we need for our `Snippet`s, so we can finally get started with the application in `app.py`. We will do it step by step, starting with the `layout` component (factory):

```python
from fastapi import FastAPI
from fasthx.htmy import HTMY, CurrentRequest

from htmy import ComponentType, Context, Fragment, Slots, Snippet, html


def layout(*children: ComponentType) -> Snippet:
    """
    Creates a `Snippet` that's configured to render `layout.html` with the given children
    components replacing the `content` slot.
    """
    return Snippet(
        "layout.html",  # Path to the HTML snippet.
        Slots({"content": children}),  # Render all children in the "content" slot.
    )
```

In this case, `layout` is not even an `htmy` component, it's just a simple function that returns a `Snippet` that's configured to load the `layout.html` file we previously created, and render the given children components in place of the `content` slot.

Now we can implement the `Centered` component. In this case we use a slightly different pattern, we subclass the component from the `Fragment` component: this way we get the `_children` property without having to write the `__init__(self, *children)` method.

```python
class Centered(Fragment):
    """Component that centers its children both vertically and horizontally."""

    def htmy(self, context: Context) -> Snippet:
        return Snippet(
            "centered.html",  # Path to the HTML snippet.
            Slots({"content": self._children}),  # Render all children in the "content" slot.
        )
```

Unlike `layout`, this component only creates the configured `Snippet` instance during rendering (in the `htmy()` method). In this simple case there's not much difference between the two patterns, but `Centered` could technically have extra state, take values from `context`, execute business logic, and use the extra data to configure the `Snippet` instance.

We create one more component (`RequestHeaders`), just to have something that's not built with `Snippet`. This component simply shows all the headers from the current request in a grid:

```python
class RequestHeaders:
    """Component that displays all the headers in the current request."""

    def htmy(self, context: Context) -> html.div:
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

The final step before creating the FastAPI application is to create a function that returns the content of the index page:

```python
def index_page(_: None) -> Snippet:
    """
    Component factory that returns the index page.

    Note that this function is not an `htmy` component at all, just a
    component factory that `fasthx` decorators can resolve. It must
    accept a single argument (the return value of the route) and return
    the component(s) that should be rendered.
    """
    return layout(Centered(RequestHeaders()))
```

`index_page()`, similarly to `layout()` is also not a component, just a function that returns a component. Specifically, it shows the `RequestHeaders` component, centered in the page. We don't really need this function, we could use `lambda _: layout(Centered(RequestHeaders()))` instead in the `FastHX` `page()` decorator, but the example is more readable and easier to follow this way.

Finally, we everything is ready, we can create the FastAPI application itself:

```python
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

```

The `@htmy.page()` decorator takes care of rendering the result of the `index()` route with the component the `index_page()` function returns. The only thing that remains is to run the application with `python -m uvicorn app:app`, open http://127.0.0.1:8000 in the browser, and see the result of our work.
