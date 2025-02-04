from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from markdown import Markdown

from htmy.core import ContextAware, SafeStr, Text
from htmy.snippet import Snippet
from htmy.typing import TextProcessor, TextResolver

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from htmy.typing import Component, Context

    from .typing import MarkdownParserFunction, MarkdownRenderFunction, ParsedMarkdown


class MarkdownParser(ContextAware):
    """
    Context-aware markdown parser.

    By default, this class uses the `markdown` library with a sensible set of
    [extensions](https://python-markdown.github.io/extensions/) including code highlighing.
    """

    __slots__ = ("_md",)

    _default: ClassVar[MarkdownParser | None] = None
    """The default instance or `None` if one hasn't been created already."""

    @classmethod
    def default(cls) -> MarkdownParser:
        """
        Returns the default instance.
        """
        if cls._default is None:
            cls._default = MarkdownParser()

        return cls._default

    def __init__(self, md: MarkdownParserFunction | None = None) -> None:
        """
        Initialization.

        Arguments:
            md: The parser function to use.
        """
        super().__init__()
        self._md = md

    def parse(self, text: str) -> ParsedMarkdown:
        """
        Returns the markdown data by parsing the given text.
        """
        md = self._md
        if md is None:
            md = self._default_md()
            self._md = md

        return md(text)

    def _default_md(self) -> MarkdownParserFunction:
        """
        Function that creates the default markdown parser.

        Returns:
            The default parser function.
        """
        md = Markdown(extensions=("extra", "meta", "codehilite"))

        def parse(text: str) -> ParsedMarkdown:
            md.reset()
            parsed = md.convert(text)
            return {"content": parsed, "metadata": getattr(md, "Meta", None)}

        return parse


class MD(Snippet):
    """
    Component for reading, customizing, and rendering markdown documents.

    It supports all the processing utilities of `Snippet`, including `text_resolver` and
    `text_processor` for formatting, token replacement, and slot conversion to components.

    One note regaring slot convesion (`text_resolver`): it is executed before markdown parsing,
    and all string segments of the resulting component sequence are parsed individually by the
    markdown parser. As a consequence, you should only use slots in places where the preceding
    and following texts individually result in valid markdown.
    """

    __slots__ = (
        "_converter",
        "_renderer",
    )

    def __init__(
        self,
        path_or_text: Text | str | Path,
        text_resolver: TextResolver | None = None,
        *,
        converter: Callable[[str], Component] | None = None,
        renderer: MarkdownRenderFunction | None = None,
        text_processor: TextProcessor | None = None,
    ) -> None:
        """
        Initialization.

        Arguments:
            path_or_text: The path where the markdown file is located or a markdown `Text`.
            text_resolver: An optional `TextResolver` (e.g. `Slots`) that converts the processed
                text into a component.
            converter: Function that converts an HTML string (the parsed and processed markdown text)
                into a component.
            renderer: Function that gets the parsed and converted content and the metadata (if it exists)
                and turns them into a component.
            text_processor: An optional text processors that can be used to process the text
                content before rendering. It can be used for example for token replacement or
                string formatting.
        """
        super().__init__(path_or_text, text_resolver, text_processor=text_processor)
        self._converter: Callable[[str], Component] = SafeStr if converter is None else converter
        self._renderer = renderer

    def _render_text(self, text: str, context: Context) -> Component:
        md = MarkdownParser.from_context(context, MarkdownParser.default()).parse(text)
        result = self._converter(md["content"])
        return result if self._renderer is None else self._renderer(result, md.get("metadata", None))
