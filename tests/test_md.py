# ruff: noqa: E501
from collections.abc import Callable
from pathlib import Path

import pytest

from htmy import HTMY, Component, ComponentType, PropertyValue, Text, etree, html, is_component_sequence, md

from .utils import tests_root

_blog_post = """---
title: Markdown
---

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

"""

_parsed_blog_post = """<h1>Essential reading</h1>
<div class="codehilite"><pre><span></span><code><span class="kn">import</span> <span class="nn">this</span>
</code></pre></div>

<p>Also available <a href="https://peps.python.org/pep-0020/">here</a>.</p>
<p>Inline <code>code</code> is <strong>also</strong> <em>fine</em>.</p>
<h1>Lists</h1>
<h2>Ordered</h2>
<ol>
<li>First</li>
<li>Second</li>
<li>Third</li>
</ol>
<h2>Unordered</h2>
<ul>
<li>First</li>
<li>Second</li>
<li>Third</li>
</ul>"""


class ConverterRules:
    h1_classes = "text-xl font-bold"
    ol_classes = "list-decimal"
    ul_classes = "list-disc"

    @classmethod
    def _inject_classes(
        cls, comp: Callable[..., ComponentType], class_: str
    ) -> Callable[..., ComponentType]:
        def wrapper(*children: ComponentType, **properties: PropertyValue) -> ComponentType:
            properties["class"] = f"{class_} {properties.get('class', '')}"
            return comp(*children, **properties)

        return wrapper

    @classmethod
    def rules(cls) -> dict[str, Callable[..., ComponentType]]:
        return {
            "h1": cls._inject_classes(html.h1, cls.h1_classes),
            "ol": cls._inject_classes(html.ol, cls.ol_classes),
            "ul": cls._inject_classes(html.ul, cls.ul_classes),
        }


_base_etree_converted_blogpost = """<h1 {h1_attrs}>Essential reading</h1>
<div class="codehilite"><pre ><span ></span><code ><span class="kn">import</span> <span class="nn">this</span>
</code></pre></div>

<p >Also available <a href="https://peps.python.org/pep-0020/">here</a>.</p>
<p >Inline <code >code</code> is <strong >also</strong> <em >fine</em>.</p>
<h1 {h1_attrs}>Lists</h1>
<h2 >Ordered</h2>
<ol {ol_attrs}>{extra_separator}
<li >First</li>{extra_separator}
<li >Second</li>{extra_separator}
<li >Third</li>{extra_separator}
</ol>
<h2 >Unordered</h2>
<ul {ul_attrs}>{extra_separator}
<li >First</li>{extra_separator}
<li >Second</li>{extra_separator}
<li >Third</li>{extra_separator}
</ul>"""

_etree_converted_blogpost = _base_etree_converted_blogpost.format(
    h1_attrs="", ol_attrs="", ul_attrs="", extra_separator=""
)
_etree_converted_blogpost_with_extra_classes = _base_etree_converted_blogpost.format(
    h1_attrs=f'class="{ConverterRules.h1_classes} "',
    ol_attrs=f'class="{ConverterRules.ol_classes} "',
    ul_attrs=f'class="{ConverterRules.ul_classes} "',
    extra_separator="\n\n",
)


def _md_renderer(children: Component, metadata: md.MarkdownMetadataDict | None) -> Component:
    assert isinstance(metadata, dict)
    title = metadata.get("title")
    assert isinstance(title, list)  # Items in the parsed metadata are an array.
    assert len(title) == 1
    return html.div(
        html.h1(title[0]),
        *(children if is_component_sequence(children) else [children]),  # type: ignore[list-item]
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("path_or_text", "expected"),
    (
        ("tests/data/blog-post.md", _parsed_blog_post),
        (tests_root / "data" / "blog-post.md", _parsed_blog_post),
        (Text(_blog_post), _parsed_blog_post),
    ),
)
async def test_parsing(path_or_text: Text | str | Path, expected: str) -> None:
    md_component = md.MD(path_or_text)
    rendered = await HTMY().render(md_component)
    assert rendered == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("path_or_text", "components", "expected"),
    (
        ("tests/data/blog-post.md", {}, _parsed_blog_post),
        (tests_root / "data" / "blog-post.md", {}, _parsed_blog_post),
        (Text(_blog_post), {}, _parsed_blog_post),
        (
            "tests/data/blog-post.md",
            {"invalid": lambda _: "<invalid />"},
            _etree_converted_blogpost,
        ),
        (
            tests_root / "data" / "blog-post.md",
            {"invalid": lambda _: "<invalid />"},
            _etree_converted_blogpost,
        ),
        (
            Text(_blog_post),
            {"invalid": lambda _: "<invalid />"},
            _etree_converted_blogpost,
        ),
        ("tests/data/blog-post.md", ConverterRules.rules(), _etree_converted_blogpost_with_extra_classes),
        (
            tests_root / "data" / "blog-post.md",
            ConverterRules.rules(),
            _etree_converted_blogpost_with_extra_classes,
        ),
        (Text(_blog_post), ConverterRules.rules(), _etree_converted_blogpost_with_extra_classes),
    ),
)
async def test_parsing_and_conversion(
    path_or_text: Text | str | Path,
    components: dict[str, Callable[..., ComponentType]],
    expected: str,
) -> None:
    converter = etree.ETreeConverter(components)
    md_component = md.MD(path_or_text, converter=converter.convert)
    rendered = await HTMY().render(md_component)
    assert rendered == expected

    md_component_with_renderer = md.MD(path_or_text, converter=converter.convert, renderer=_md_renderer)
    rendered = await HTMY().render(md_component_with_renderer)
    assert rendered == "\n".join(
        (
            "<div >",
            "<h1 >Markdown</h1>",
            expected,
            "</div>",
        )
    )
