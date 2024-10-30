# Markdown rendering

The focus of this example is markdown rendering and customization. As such, all you need to follow along is `htmy`, which you can install with `pip install htmy`.

There's one important thing to know about markdown in relation to this tutorial and the markdown support in `htmy`: markdown can include [HTML](https://daringfireball.net/projects/markdown/syntax#html) (well, XML). Looking at this from another perspective, most HTML/XML snippets can be parsed by markdown parsers without issues. This means that while the below examples work with text files with markdown syntax, those file could also contain plain HTML snippets with no "markdown" at all. You will start to see the full power of this concept by the end of this article.

## Essentials

The entire example will consist of two files: `post.md` and `app.py` which should be located next to each other in the same directory.

First we create a simple markdown file (`post.md`) which only contains standard markdown syntax, including headers, lists, code blocks:

````md
# Essential reading

```python
import this
```

Also available [here](https://peps.python.org/pep-0020/).

Inline `code` is **also** _fine_.

# Lists

## Ordered

1. First
2. Second
3. Third

## Unordered

- First
- Second
- Third
````

Then we can create the most minimal version of `app.py` that will be responsible for rendering `post.md` as HTML. Keep in mind that `htmy` is an _async_ rendering engine, so we will need `asyncio` (specifically `asyncio.run()`) to run the renderer.

```python
import asyncio

from htmy import HTMY, md


async def render_post() -> None:
    md_post = md.MD("post.md")  # Create an htmy.md.MD component.
    rendered = await HTMY().render(md_post)  # Render the MD component.
    print(rendered)  # Print the result.


if __name__ == "__main__":
    asyncio.run(render_post())
```

That's it. You can now run `app.py` from the terminal with `python app.py`, and it will print out the generated HTML snippet. You can save the output to an HTML file, or even better, pipe the output of the script directly to a file with `python app.py > post.html` and just open the resulting HTML file in your browser.

## Customization

In this section we will extend the above example by adding custom rendering rules that apply extra CSS classes to a couple of standard HTML elements. The extra styling will be done by [TailwindCSS](https://tailwindcss.com/), which means we will also need to set up a proper HTML page. If you're not familiar with TailwindCSS, don't worry, it is not required for understanding the `htmy` concepts.

The `post.md` file can remain the same as above, but `app.py` will change quite a bit.

First of all we need a few more import (although some only for typing):

```python
from htmy import HTMY, Component, ComponentType, Context, PropertyValue, etree, html, md
```

Next we need a `Page` component that defines the base HTML structure of the webpage:

```python
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
                    html.meta.charset(),
                    html.meta.viewport(),
                    # TailwindCSS import
                    html.script(src="https://cdn.tailwindcss.com"),
                ),
                html.body(
                    *self.children,
                    class_="h-screen w-screen p-8",
                ),
            ),
        )
```

We are getting close now, we just need to write our custom conversion rules / `htmy` component factories that will change certain tags that we encounter in the parsed markdown document:

```python
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
```

With the conversion rules in place, we can create our component converter by mapping tag names to conversion rules:

```python
# Create an element converter and configure it to use the conversion rules
# that are defined above on h1, h2, ol, and ul tags.
md_converter = etree.ETreeConverter(
    {
        "h1": ConversionRules.h1,
        "h2": ConversionRules.h2,
        "ol": ConversionRules.ol,
        "ul": ConversionRules.ul,
    }
)
```

Finally we update our `render_post()` function from the previous example to make use of all the tools we implemented above:

```python
async def render_post() -> None:
    md_post = md.MD(  # Create an htmy.md.MD component.
        "post.md",
        converter=md_converter.convert,  # And make it use our element converter's conversion method.
    )
    page = Page(md_post)  # Wrap the post in a Page component.
    rendered = await HTMY().render(page)  # Render the MD component.
    print(rendered)  # Print the result.
```

If you run the app with `python app.py` now, you will see that the result is a complete HTML page and the `h1`, `h2`, `ol`, and `ul` tags automatically get the custom styles that we add in our `ConversionRules`.

## Custom components in markdown

In the example above, you may have noticed that while we only defined custom conversion rules for HTML tags, we could have done the same for an other tag name, for example `"PostInfo"`. You can also have any XML in markdown files, for example `<PostInfo author="John" published_at="1971-10-11" />`. Obviously the browser will not know what to do with this tag if we blindly keep it, but with `htmy` we can process it in any way we want.

Building on the code from the previous section, as an example, let's add this `PostInfo` tag to `post.md` and create a custom `htmy` component for it.

Here's the updated `post.md` file:

````md
# Essential reading

<PostInfo author="John" published_at="1971-10-11" />

```python
import this
```

Also available [here](https://peps.python.org/pep-0020/).

Inline `code` is **also** _fine_.

# Lists

## Ordered

1. First
2. Second
3. Third

## Unordered

- First
- Second
- Third
````

Then we can create the `PostInfo` `htmy` component:

```python
class PostInfo:
    """HTMY component for post info rendering."""

    def __init__(self, author: str, published_at: str) -> None:
        self.author = author
        self.published_at = published_at

    def htmy(self, context: Context) -> Component:
        return html.p("By ", html.strong(self.author), " at ", html.em(self.published_at), ".")
```

Note that the arguments of `PostInfo.__init__()` match what we have in the markdown file.

All we need now is a conversion rule for the `PostInfo` tag, so we extend the previously created converter with this rule:

```python
md_converter = etree.ETreeConverter(
    {
        "h1": ConversionRules.h1,
        "h2": ConversionRules.h2,
        "ol": ConversionRules.ol,
        "ul": ConversionRules.ul,
        "PostInfo": PostInfo,
    }
)
```

If you run the app now (with `python app.py`) and open the resulting HTML in a browser, you will see that `<PostInfo ... />` was nicely converted to HTML by `htmy`.
