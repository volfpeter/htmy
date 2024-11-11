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


if __name__ == "__main__":
    asyncio.run(render_hello())
