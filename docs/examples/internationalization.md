# Internationalization

The focus of this example is using the built-in `I18n` utility for internationalization. All you need to follow the example is `htmy`, which you can install with `pip install htmy`.

First of all, we must create some translation resources (plain JSON files). Let's do this by creating the `locale/en/page` folder structure and adding a `hello.json` in the `page` folder with the following content: `{ "message": "Hey {name}" }`. Notice the Python format string in the value for the `"message"` key, such strings can be automatically formatted by `I18n`, see the details in the docs and in the usage example below.

Using `I18n` consists of only two steps: create an `I18n` instance, and include it in the `HTMY` rendering context so it can be accessed by components in their `htmy()` (render) method.

With the translation resource in place, we can create the `app.py` file and implement our translated components like this:

```python
import asyncio
from pathlib import Path

from htmy import HTMY, Component, Context, html
from htmy.i18n import I18n


class TranslatedComponent:
    """HTMY component with translated content."""

    async def htmy(self, context: Context) -> Component:
        # Get the I18n instance from the rendering context.
        i18n = I18n.from_context(context)
        # Get the translated message.
        # The translation file can referenced with a dotted path.
        # The second argument is the requested key in the translation file.
        # Keyword arguments can be used for automatic string formatting.
        message = await i18n.get("page.hello", "message", name="Joe")
        # And return component's content.
        return html.p(message)
```

Now that we have a component to render, we can create our `I18n` instance and write the async function that renders our content:

```python
base_folder = Path(__file__).parent
"""The folder where the app and all its content live."""

i18n = I18n(base_folder / "locale" / "en")
"""
The `I18n` instance that we can add to the `HTMY` rendering context.

It takes translations from the `locale/en` folder.
"""


async def render_hello() -> None:
    rendered = await HTMY().render(
        # Render a TranslatedComponent.
        TranslatedComponent(),
        # Include the created I18n instance in the rendering context.
        i18n.to_context(),
    )
    print(rendered)
```

Finally we add the usual `asyncio` run call:

```python
if __name__ == "__main__":
    asyncio.run(render_hello())
```

With `app.py` and the `locale/en/page/hello.json` translation resource in place, we can finally run the application with `python app.py` and see the translated content in the result. That's it.
