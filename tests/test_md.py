# ruff: noqa: E501
from collections.abc import Callable
from pathlib import Path

import pytest

from htmy import (
    Component,
    ComponentType,
    PropertyValue,
    Renderer,
    Slots,
    Text,
    as_component_sequence,
    etree,
    html,
    md,
)
from htmy.renderer import BaselineRenderer
from htmy.typing import TextProcessor

from .utils import tests_root

_blog_post_format_string = """---
title: Markdown
---

# {title}

```python
import this
```

Also available [here](https://peps.python.org/pep-0020/).
{slot}
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

_blog_post = _blog_post_format_string.format(title="Essential reading", slot="")

# Paragraphs in line "Also available..." line are on 1 line in the format string, because
# the renderer simply concatenates strings when everythin is resolved, and there won't be
# a new line of an actual slot is rendered there.
_parsed_blog_post_format_string = """<h1>{title}</h1>
<div class="codehilite"><pre><span></span><code><span class="kn">import</span><span class="w"> </span><span class="nn">this</span>
</code></pre></div>

<p>Also available <a href="https://peps.python.org/pep-0020/">here</a>.</p>{slot}<p>Inline <code>code</code> is <strong>also</strong> <em>fine</em>.</p>
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

# See the comment of _parsed_blog_post_format_string for why slot is `\n` by default.
_parsed_blog_post = _parsed_blog_post_format_string.format(title="Essential reading", slot="\n")


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
<div class="codehilite"><pre ><span ></span><code ><span class="kn">import</span><span class="w"> </span><span class="nn">this</span>
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
    return html.div(html.h1(title[0]), *as_component_sequence(children))


@pytest.mark.anyio
async def test_md_with_slot() -> None:
    md_component = md.MD(
        Text(_blog_post_format_string),
        Slots({"comment": html.p("Comment slot resolved.")}),
        text_processor=lambda text, _: text.format(
            title="Essential reading", slot="<!-- slot[comment] -->"
        ),
    )
    rendered = await Renderer().render(md_component)
    assert rendered == _parsed_blog_post_format_string.format(
        title="Essential reading",
        slot="<p >Comment slot resolved.</p>",
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("path_or_text", "text_processor", "expected"),
    (
        ("tests/data/blog-post.md", None, _parsed_blog_post),
        (tests_root / "data" / "blog-post.md", None, _parsed_blog_post),
        (Text(_blog_post), None, _parsed_blog_post),
        (
            Text(_blog_post_format_string),
            lambda text, _: text.format(title="Essential reading", slot=""),
            _parsed_blog_post,
        ),
    ),
)
async def test_parsing(
    path_or_text: Text | str | Path, text_processor: TextProcessor, expected: str
) -> None:
    md_component = md.MD(path_or_text, text_processor=text_processor)
    rendered = await Renderer().render(md_component)
    assert isinstance(rendered, str)
    assert rendered == expected

    rendered = await BaselineRenderer().render(md_component)
    assert isinstance(rendered, str)
    assert rendered == expected


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("path_or_text", "components", "text_processor", "expected"),
    (
        ("tests/data/blog-post.md", {}, None, _parsed_blog_post),
        (tests_root / "data" / "blog-post.md", {}, None, _parsed_blog_post),
        (Text(_blog_post), {}, None, _parsed_blog_post),
        (
            "tests/data/blog-post.md",
            {"invalid": lambda _: "<invalid />"},
            None,
            _etree_converted_blogpost,
        ),
        (
            tests_root / "data" / "blog-post.md",
            {"invalid": lambda _: "<invalid />"},
            None,
            _etree_converted_blogpost,
        ),
        (
            Text(_blog_post),
            {"invalid": lambda _: "<invalid />"},
            None,
            _etree_converted_blogpost,
        ),
        (
            "tests/data/blog-post.md",
            ConverterRules.rules(),
            None,
            _etree_converted_blogpost_with_extra_classes,
        ),
        (
            tests_root / "data" / "blog-post.md",
            ConverterRules.rules(),
            None,
            _etree_converted_blogpost_with_extra_classes,
        ),
        (Text(_blog_post), ConverterRules.rules(), None, _etree_converted_blogpost_with_extra_classes),
        (
            Text(_blog_post_format_string),
            ConverterRules.rules(),
            lambda text, _: text.format(title="Essential reading", slot=""),
            _etree_converted_blogpost_with_extra_classes,
        ),
    ),
)
async def test_parsing_and_conversion(
    path_or_text: Text | str | Path,
    components: dict[str, Callable[..., ComponentType]],
    text_processor: TextProcessor,
    expected: str,
) -> None:
    converter = etree.ETreeConverter(components)
    md_component = md.MD(path_or_text, converter=converter.convert, text_processor=text_processor)
    rendered = await Renderer().render(md_component)
    assert rendered == expected

    rendered = await BaselineRenderer().render(md_component)
    assert rendered == expected

    md_component_with_renderer = md.MD(
        path_or_text, converter=converter.convert, renderer=_md_renderer, text_processor=text_processor
    )
    rendered = await Renderer().render(md_component_with_renderer)
    assert rendered == "\n".join(
        (
            "<div >",
            "<h1 >Markdown</h1>",
            expected,
            "</div>",
        )
    )

    rendered = await BaselineRenderer().render(md_component_with_renderer)
    assert rendered == "\n".join(
        (
            "<div >",
            "<h1 >Markdown</h1>",
            expected,
            "</div>",
        )
    )
