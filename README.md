![Tests](https://github.com/volfpeter/htmy/actions/workflows/tests.yml/badge.svg)
![Linters](https://github.com/volfpeter/htmy/actions/workflows/linters.yml/badge.svg)
![Documentation](https://github.com/volfpeter/htmy/actions/workflows/build-docs.yml/badge.svg)
![PyPI package](https://img.shields.io/pypi/v/htmy?color=%2334D058&label=PyPI%20Package)

**Source code**: [https://github.com/volfpeter/htmy](https://github.com/volfpeter/htmy)

**Documentation and examples**: [https://volfpeter.github.io/htmy](https://volfpeter.github.io/htmy/)

# `htmy`

**Async**, **pure-Python** rendering engine.

## Key features

- **Async**-first, to let you make the best use of [modern async tools](https://github.com/timofurrer/awesome-asyncio).
- **Powerful**, React-like **context support**, so you can avoid prop-drilling.
- Sync and async **function components** with **decorator syntax**.
- All baseline **HTML** tags built-in.
- **Markdown** support with tools for customization.
- Async, JSON based **internationalization**.
- Built-in, easy to use `ErrorBoundary` component for graceful error handling.
- **Unopinionated**: use the backend, CSS, and JS frameworks of your choice, the way you want to use them.
- Everything is **easily customizable**, from the rendering engine to components, formatting and context management.
- Automatic and customizable **property-name conversion** from snake case to kebab case.
- **Fully-typed**.

## Installation

The package is available on PyPI and can be installed with:

```console
$ pip install htmy
```

## Concepts

The entire library -- from the rendering engine itself to the built-in components -- is built around a few simple protocols and a handful of simple utility classes. This means that you can easily customize, extend, or replace basically everything in the library. Yes, even the rendering engine. The remaining parts will keep working as expected.

Also, the library doesn't rely on advanced Python features such as metaclasses or descriptors. There are also no complex base classes and the like. Even a junior engineer could understand, develop, and debug an application that's built with `htmy`.

### Components

Every class with a sync or async `htmy(context: Context) -> Component` method is an `htmy` component (technically an `HTMYComponentType`). Strings are also components, as well as lists or tuples of `HTMYComponentType` or string objects.

Using this method name enables the conversion of any of your business objects (from `TypedDicts`s or `pydantic` models to ORM classes) into components without the fear of name collision with other tools.

Async support makes it possible to load data or execute async business logic right in your components. This can reduce the amount of boilerplate you need to write in some cases, and also gives you the freedom to split the rendering and non-rendering logic in any way you see fit.

Example:

```python
from dataclasses import dataclass

from htmy import Component, Context, html

@dataclass(frozen=True, kw_only=True, slots=True)
class User:
    username: str
    name: str
    email: str

    async def is_admin(self) -> bool:
        return False

class UserRow(User):
    async def htmy(self, context: Context) -> Component:
        role = "admin" if await self.is_admin() else "restricted"
        return html.tr(
            html.td(self.username),
            html.td(self.name),
            html.td(html.a(self.email, href=f"mailto:{self.email}")),
            html.td(role)
        )

@dataclass(frozen=True, kw_only=True, slots=True)
class UserRows:
    users: list[User]
    def htmy(self, context: Context) -> Component:
        # Note that a list is returned here. A list or tuple of `HTMYComponentType | str` objects is also a component.
        return [UserRow(username=u.username, name=u.name, email=u.email) for u in self.users]

user_table = html.table(
    UserRows(
        users=[
            User(username="Foo", name="Foo", email="foo@example.com"),
            User(username="Bar", name="Bar", email="bar@example.com"),
        ]
    )
)
```

`htmy` also provides a `@component` decorator that can be used on sync or async `my_component(props: MyProps, context: Context) -> Component` functions to convert them into components (preserving the `props` typing).

Here is the same example as above, but with function components:

```python
from dataclasses import dataclass

from htmy import Component, Context, component, html

@dataclass(frozen=True, kw_only=True, slots=True)
class User:
    username: str
    name: str
    email: str

    async def is_admin(self) -> bool:
        return False

@component
async def user_row(user: User, context: Context) -> Component:
    # The first argument of function components is their "props", the data they need.
    # The second argument is the rendering context.
    role = "admin" if await user.is_admin() else "restricted"
    return html.tr(
        html.td(user.username),
        html.td(user.name),
        html.td(html.a(user.email, href=f"mailto:{user.email}")),
        html.td(role)
    )

@component
def user_rows(users: list[User], context: Context) -> Component:
    # Nothing to await in this component, so it's sync.
    # Note that we only pass the "props" to the user_row() component (well, function component wrapper).
    # The context will be passed to the wrapper during rendering.
    return [user_row(user) for user in users]

user_table = html.table(
    user_rows(
        [
            User(username="Foo", name="Foo", email="foo@example.com"),
            User(username="Bar", name="Bar", email="bar@example.com"),
        ]
    )
)
```

### Built-in components

`htmy` has a rich set of built-in utilities and components for both HTML and other use-cases:

- `html` module: a complete set of [baseline HTML tags](https://developer.mozilla.org/en-US/docs/Glossary/Baseline/Compatibility).
- `md`: `MarkdownParser` utility and `MD` component for loading, parsing, converting, and rendering markdown content.
- `i18n`: utilities for async, JSON based internationalization.
- `BaseTag`, `TagWithProps`, `Tag`, `WildcardTag`: base classes for custom XML tags.
- `ErrorBoundary`, `Fragment`, `SafeStr`, `WithContext`: utilities for error handling, component wrappers, context providers, and formatting.
- `Snippet`: utility class for loading and customizing document snippets from the file system.
- `etree.ETreeConverter`: utility that converts XML to a component tree with support for custom HTMY components.

### Rendering

`htmy.Renderer` is the built-in, default renderer of the library.

If you're using the library in an async web framework like [FastAPI](https://fastapi.tiangolo.com/), then you're already in an async environment, so you can render components as simply as this: `await Renderer().render(my_root_component)`.

If you're trying to run the renderer in a sync environment, like a local script or CLI, then you first need to wrap the renderer in an async task and execute that task with `asyncio.run()`:

```python
import asyncio

from htmy import Renderer, html

async def render_page() -> None:
    page = (
        html.DOCTYPE.html,
        html.html(
            html.body(
                html.h1("Hello World!"),
                html.p("This page was rendered by ", html.code("htmy")),
            ),
        )
    )

    result = await Renderer().render(page)
    print(result)


if __name__ == "__main__":
    asyncio.run(render_page())
```

### Context

As you could see from the code examples above, every component has a `context: Context` argument, which we haven't used so far. Context is a way to share data with the entire subtree of a component without "prop drilling".

The context (technically a `Mapping`) is entirely managed by the renderer. Context provider components (any class with a sync or async `htmy_context() -> Context` method) add new data to the context to make it available to components in their subtree, and components can simply take what they need from the context.

There is no restriction on what can be in the context, it can be used for anything the application needs, for example making the current user, UI preferences, themes, or formatters available to components. In fact, built-in components get their `Formatter` from the context if it contains one, to make it possible to customize tag property name and value formatting.

Here's an example context provider and consumer implementation:

```python
import asyncio

from htmy import Component, ComponentType, Context, Renderer, component, html

class UserContext:
    def __init__(self, *children: ComponentType, username: str, theme: str) -> None:
        self._children = children
        self.username = username
        self.theme = theme

    def htmy_context(self) -> Context:
        # Context provider implementation.
        return {UserContext: self}

    def htmy(self, context: Context) -> Component:
        # Context providers must also be components, as they just
        # wrap some children components in their context.
        return self._children

    @classmethod
    def from_context(cls, context: Context) -> "UserContext":
        user_context = context[cls]
        if isinstance(user_context, UserContext):
            return user_context

        raise TypeError("Invalid user context.")

@component
def welcome_page(text: str, context: Context) -> Component:
    # Get user information from the context.
    user = UserContext.from_context(context)
    return (
        html.DOCTYPE.html,
        html.html(
            html.body(
                html.h1(text, html.strong(user.username)),
                data_theme=user.theme,
            ),
        ),
    )

async def render_welcome_page() -> None:
    page = UserContext(
        welcome_page("Welcome back "),
        username="John",
        theme="dark",
    )

    result = await Renderer().render(page)
    print(result)

if __name__ == "__main__":
    asyncio.run(render_welcome_page())
```

You can of course rely on the built-in context related utilities like the `ContextAware` or `WithContext` classes for convenient and typed context use with less boilerplate code.

### Formatter

As mentioned before, the built-in `Formatter` class is responsible for tag attribute name and value formatting. You can completely override or extend the built-in formatting behavior simply by extending this class or adding new rules to an instance of it, and then adding the custom instance to the context, either directly in `Renderer` or `Renderer.render()`, or in a context provider component.

These are default tag attribute formatting rules:

- Underscores are converted to dashes in attribute names (`_` -> `-`) unless the attribute name starts or ends with an underscore, in which case leading and trailing underscores are removed and the rest of attribute name is preserved. For example `data_theme="dark"` is converted to `data-theme="dark"`, but `_data_theme="dark"` will end up as `data_theme="dark"` in the rendered text. More importantly `class_="text-danger"`, `_class="text-danger"`, `_class__="text-danger"` are all converted to `class="text-danger"`, and `_for="my-input"` or `for_="my_input"` will become `for="my-input"`.
- `bool` attribute values are converted to strings (`"true"` and `"false"`).
- `XBool.true` attributes values are converted to an empty string, and `XBool.false` values are skipped (only the attribute name is rendered).
- `date` and `datetime` attribute values are converted to ISO strings.

### Error boundary

The `ErrorBoundary` component is useful if you want your application to fail gracefully (e.g. display an error message) instead of raising an HTTP error.

The error boundary wraps a component component subtree. When the renderer encounters an `ErrorBoundary` component, it will try to render its wrapped content. If rendering fails with an exception at any point in the `ErrorBoundary`'s subtree, the renderer will automatically fall back to the component you assigned to the `ErrorBoundary`'s `fallback` property.

Optionally, you can define which errors an error boundary can handle, giving you fine control over error handling.

### Sync or async?

In general, a component should be async if it must await some async call inside.

If a component executes a potentially "long-running" synchronous call, it is strongly recommended to delegate that call to a worker thread an await it (thus making the component async). This can be done for example with `anyio`'s `to_thread` [utility](https://anyio.readthedocs.io/en/stable/threads.html), `starlette`'s (or `fastapi`'s) `run_in_threadpool()`, and so on. The goal here is to avoid blocking the asyncio event loop, as that can lead to performance issues.

In all other cases, it's best to use sync components.

## Framework integrations

FastAPI:

- [FastHX](https://github.com/volfpeter/fasthx)

## Why

At one end of the spectrum, there are the complete application frameworks that combine the server (Python) and client (JavaScript) applications with the entire state management and synchronization into a single Python (an in some cases an additional JavaScript) package. Some of the most popular examples are: [Reflex](https://github.com/reflex-dev/reflex), [NiceGUI](https://github.com/zauberzeug/nicegui/), [ReactPy](https://github.com/reactive-python/reactpy), and [FastUI](https://github.com/pydantic/FastUI).

The main benefit of these frameworks is rapid application prototyping and a very convenient developer experience (at least as long as you stay within the built-in feature set of the framework). In exchange for that, they are very opinionated (from components to frontend tooling and state management), the underlying engineering is very complex, deployment and scaling can be hard or costly, and they can be hard to migrate away from. Even with these caveats, they can be a very good choice for internal tools and application prototyping.

The other end of spectrum -- plain rendering engines -- is dominated by the [Jinja](https://jinja.palletsprojects.com) templating engine, which is a safe choice as it has been and will be around for a long time. The main drawbacks with Jinja are the lack of good IDE support, the complete lack of static code analysis support, and the (subjectively) ugly syntax.

Then there are tools that aim for the middleground, usually by providing most of the benefits and drawbacks of complete application frameworks while leaving state management, client-server communication, and dynamic UI updates for the user to solve, often with some level of [HTMX](https://htmx.org/) support. This group includes libraries like [FastHTML](https://github.com/answerdotai/fasthtml) and [Ludic](https://github.com/getludic/ludic).

The primary aim of `htmy` is to be an **async**, pure-Python rendering engine, which is as **simple**, **maintainable**, and **customizable** as possible, while still providing all the building blocks for (conveniently) creating complex and maintainable applications.

## Dependencies

The library aims to minimze its dependencies. Currently the following dependencies are required:

- `anyio`: for async file operations and networking.
- `async-lru`: for async caching.
- `markdown`: for markdown parsing.

## Development

Use `ruff` for linting and formatting, `mypy` for static code analysis, and `pytest` for testing.

The documentation is built with `mkdocs-material` and `mkdocstrings`.

## Contributing

All contributions are welcome, including more documentation, examples, code, and tests. Even questions.

## License - MIT

The package is open-sourced under the conditions of the [MIT license](https://choosealicense.com/licenses/mit/).
