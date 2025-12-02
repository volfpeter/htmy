# Components guide

## What is a component?

Every object with a sync or async `htmy(context: Context) -> Component` method is an `htmy` component (technically an `HTMYComponentType`). Strings are also components, as well as lists or tuples of `HTMYComponentType` or string objects.

Using the `htmy()` method name enables the conversion of any of your pre-existing business objects and Python utilities -- from `TypedDicts`s or `pydantic` models to ORM classes, and even advanced constructs like descriptors -- into components without the fear of name collision or compatibility issues with other tools.

(Note: while many code examples in the documentation use `dataclasses` to create components, the only reason for this is that `dataclasses` save a lot of boilerplate code and make the examples more readable.)

With the technical details out of the way, let's see some examples with built-in Python types:

```python
import asyncio
from datetime import datetime

from htmy import Component, ComponentType, Context, Renderer, html, join_components


class HTMYDatetime(datetime):
    """
    Datetime subclass that's also a component thanks to its `htmy()` classmethod.

    The class itself is the component. Rendering either the class or an instance
    of it creates a `<p>` tag with the *current* date and time information in it.
    """

    @classmethod
    def htmy(cls, _: Context) -> Component:
        return html.p("The current date and time is: ", cls.now().isoformat())


class ULDict(dict[str, ComponentType]):
    """
    Dictionary that maps string keys to `htmy` components.

    Instances of this dictionary are `htmy` components, that render the items in
    the dictionary as `<li>` tags inside a `<ul>` tag.
    """

    def htmy(self, _: Context) -> Component:
        return html.ul(*(html.li(k, ": ", v) for k, v in self.items()))


class Coordinate(tuple[float, float, float]):
    """
    Tuple that represents a 3D coordinate.

    During rendering, an origin coordinate is loaded from the rendering context,
    and the calculated absolute coordinate will be rendered as a `<p>` tag.
    """

    def htmy(self, context: Context) -> Component:
        origin: tuple[float, float, float] = context["origin"]
        return html.p(f"Coordinates: ({self[0] + origin[0]}, {self[1] + origin[1]}, {self[2] + origin[2]})")


class OrderedList(list[ComponentType]):
    """
    List of `htmy` components.

    Instances are rendered as an `<ol>` tag with the list items inside, wrapped by `<li>` tags.
    """

    def htmy(self, _: Context) -> Component:
        return html.ol(*(html.li(item) for item in self))


class HexBytes(bytes):
    """
    `bytes` object that renders its individual bytes as hexadecimal strings,
    separated by spaces, in a `<p>` tag.
    """

    def htmy(self, _: Context) -> Component:
        return html.p(*join_components(tuple(f"0x{b:X}" for b in self), " "))
```

Now, let's render these components to see how they can be used:

```python
async def render() -> None:
    renderer = Renderer()
    result = await renderer.render(
        html.div(
            HTMYDatetime,
            HTMYDatetime(2025, 2, 25),
            ULDict(one="First", two="Second", three="Third"),
            Coordinate((1, 6, 1)),
            OrderedList([Coordinate((1, 2, 3)), Coordinate((4, 5, 6))]),
            HexBytes(b"Hello!"),
        ),
        # Add an origin coordinate to the context for Coordinate to use.
        {"origin": (3, 1, 4)},
    )
    print(f"Result:\n{result}")


asyncio.run(render())
```

You can use these patterns to enhance your existing business objects with rendering capabilities, without affecting their original functionality in any way.

The use of context -- and async support if you're using async tools like FastAPI -- makes these patterns even more powerful. Imagine, that you have a web application in which the client submits an `X-Variant` request header to tell the server how to render the response (typical scenario with HTMX), for example as a list item or a table row. If you add this information to the rendering context, your enhanced business objects can use this information to conditionally fetch more data and render themselves the way the client requested. (This is facilitated out of the box by [FastHX](https://volfpeter.github.io/fasthx/examples/htmy/) for example.)

Here is the pseudo-code for the above scenario:

```python
@dataclass
class User:
    name: str
    email: str
    permissions: list[str] | None = None

    async def htmy(self, context: Context) -> Component:
        request_headers = context["request_headers"]
        variant = request_headers.get("X-Variant", "list-item")
        if variant == "list-item":
            return await self._htmy_li(context)
        elif variant == "table-row":
            return await self._htmy_tr(context)
        else:
            raise ValueError("Unknown variant")

    async def _htmy_li(self, context: Context) -> Component:
        return html.li(...)

    async def _htmy_tr(self, context: Context) -> Component:
        # Make sure permissions are loaded, the table row representation needs them.
        await self._load_permissions()
        return html.tr(...)

    async def _load_permissions(self) -> None:
        # Load user permissions and store them in self.permissions.
        ...
```

Hopefully these examples give you some ideas on how you can efficiently integrate `htmy` into your application and business logic.

Unleash your creativity, and have fun building your next web application! And of course join our [Discussion Board](https://github.com/volfpeter/htmy/discussions) to share your cool patterns and use-cases with the community.

## What is a component factory?

So far we only talked about components, but often you do not need to create full-fledged `htmy` components, all you need is a function that accepts some arguments and returns a component. Such functions are called component factories.

```python
def heading(text: str) -> Component:
    """Heading component factory."""
    return html.h1(text)

def paragraph(text: str) -> Component:
    """Paragraph component factory."""
    return html.p(text)

def section(title: str, text: str) -> Component:
    """
    This is not a component, just a factory that is evaluated to a component
    immediately when called. The renderer will only need to resolve the inner
    `div` and its children.
    """
    return html.div(
        heading(title),  # Calling a component factory here.
        paragraph(text), # Calling a component factory here as well.
    )
```

Of course, instance, class, and static methods, even properties or more advanced Python constructs like descriptors can also act as component factories, giving you a lot of flexibility in how you add `htmy` rendering support to your codebase.

Component factories come with some advantages, mainly simplicity and somewhat better performance. The performance benefit comes from the fact these functions are executed instantly, and the `htmy` renderer only needs to resolve the resulting component tree, which will be smaller than the one that uses components for everything.

Component factories come with some limitations and downsides though:

- Often they can not be async, because they are called from sync code.
- They have no access to the rendering context.
- They can not act as context providers.
- They are immediately evaluated, which can be undesirable if they create a large component tree.

Note that when you create the component tree you want to render, you (almost) always "call" something with some arguments: either a component factory or an actual component class, the latter of which is just the instantiation of the component class (potentially an enhanced business object).

There is one important detail you must pay attention to: if a component factory returns a component sequence, then it's up to you make sure the returned component sequence is correctly passed to the "parent" component or component factory, because for example `list[list[ComponentType]]` is not a valid component sequence, only `list[ComponentType]` is. List unpacking and the built-in `Fragment` component can help you avoid potential issues.

It may be unnecessary to say, but you don't need to bother with the above issue if you use components, they can return component sequences and the renderer will deal with them, it's a standard use-case.

## When to use components, when to use component factories?

There is no hard rule, but hopefully the previous sections gave you enough guidance to make an informed decision in every case. In general, if a component factory is enough, then it's often the better choice, but if you feel safer using only components, then that's just as good.
