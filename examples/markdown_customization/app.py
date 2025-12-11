import asyncio

from htmy import Component, ComponentType, Context, PropertyValue, Renderer, etree, html, md


class Page:
    """Page component that creates the basic HTML layout."""

    def __init__(self, *children: ComponentType) -> None:
        """
        Arguments:
            *children: The page content.
        """
        self.children = children

    def htmy(self, context: Context) -> Component:
        return (
            html.DOCTYPE.html,
            html.html(
                html.head(
                    # Some metadata
                    html.title("Markdown example"),
                    html.Meta.charset(),
                    html.Meta.viewport(),
                    # TailwindCSS import
                    html.script(src="https://cdn.tailwindcss.com"),
                ),
                html.body(
                    *self.children,
                    class_="h-screen w-screen p-8",
                ),
            ),
        )


class PostInfo:
    """Component for post info rendering."""

    def __init__(self, author: str, published_at: str) -> None:
        self.author = author
        self.published_at = published_at

    def htmy(self, context: Context) -> Component:
        return html.p("By ", html.strong(self.author), " at ", html.em(self.published_at), ".")


class ConversionRules:
    """Conversion rules for some of the HTML elements we can encounter in parsed markdown documents."""

    @staticmethod
    def h1(*children: ComponentType, **properties: PropertyValue) -> ComponentType:
        """Rule for converting `h1` tags that adds some extra CSS classes to the tag."""
        properties["class"] = f"text-xl font-bold {properties.get('class', '')}"
        return html.h1(*children, **properties)

    @staticmethod
    def h2(*children: ComponentType, **properties: PropertyValue) -> ComponentType:
        """Rule for converting `h2` tags that adds some extra CSS classes to the tag."""
        properties["class"] = f"text-lg font-bold {properties.get('class', '')}"
        return html.h2(*children, **properties)

    @staticmethod
    def ol(*children: ComponentType, **properties: PropertyValue) -> ComponentType:
        """Rule for converting `ol` tags that adds some extra CSS classes to the tag."""
        properties["class"] = f"list-decimal list-inside {properties.get('class', '')}"
        return html.ol(*children, **properties)

    @staticmethod
    def ul(*children: ComponentType, **properties: PropertyValue) -> ComponentType:
        """Rule for converting `ul` tags that adds some extra CSS classes to the tag."""
        properties["class"] = f"list-disc list-inside {properties.get('class', '')}"
        return html.ul(*children, **properties)


# Create an element converter and configure it to use the conversion rules
# that are defined above on h1, h2, ol, and ul tags.
md_converter = etree.ETreeConverter(
    {
        "h1": ConversionRules.h1,
        "h2": ConversionRules.h2,
        "ol": ConversionRules.ol,
        "ul": ConversionRules.ul,
        "PostInfo": PostInfo,
    }
)


async def render_post() -> None:
    md_post = md.MD(  # Create an htmy.md.MD component.
        "post.md",
        converter=md_converter.convert,  # And make it use our element converter's conversion method.
    )
    page = Page(md_post)  # Wrap the post in a Page component.
    rendered = await Renderer().render(page)  # Render the MD component.
    print(rendered)  # Print the result.


if __name__ == "__main__":
    asyncio.run(render_post())
