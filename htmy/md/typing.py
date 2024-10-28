from collections.abc import Callable
from typing import Any, NotRequired, TypeAlias, TypedDict

from htmy.typing import Component

MarkdownMetadataDict: TypeAlias = dict[str, Any]


class ParsedMarkdown(TypedDict):
    """Type definition for parsed markdown data."""

    content: str
    metadata: NotRequired[MarkdownMetadataDict | None]


MarkdownParserFunction: TypeAlias = Callable[[str], ParsedMarkdown]
"""Callable that converts a markdown string into a `ParsedMarkdown` object."""

MarkdownRenderFunction: TypeAlias = Callable[[Component, MarkdownMetadataDict | None], Component]
"""Renderer function definition for markdown data."""
