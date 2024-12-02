from collections.abc import Mapping
from pathlib import Path

import pytest

from htmy import HTMY, Context, SafeStr, Snippet, Text
from htmy.typing import TextProcessor

from .utils import tests_root

_hello_world_format_snippet = "\n".join(
    (
        "<div>",
        "  <title>Hello World!</title>",
        "  <Paragraph>{message}</Paragraph>",
        "</div>",
        "",
    )
)

_hello_world_snippet = _hello_world_format_snippet.format(
    message="The quick brown fox jumps over the lazy dog."
)


def sync_text_processor(text: str, context: Context) -> str:
    assert isinstance(context, Mapping)
    return text.format(message="Filled by sync text processor.")


async def async_text_processor(text: str, context: Context) -> str:
    assert isinstance(context, Mapping)
    return text.format(message="Filled by async text processor.")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("path_or_text", "text_processor", "expected"),
    (
        ("tests/data/hello-world-snippet.html", None, _hello_world_snippet),
        (tests_root / "data" / "hello-world-snippet.html", None, _hello_world_snippet),
        (Text(_hello_world_snippet), None, _hello_world_snippet),
        (
            Text(_hello_world_format_snippet),
            sync_text_processor,
            _hello_world_format_snippet.format(message="Filled by sync text processor."),
        ),
        (
            Text(_hello_world_format_snippet),
            async_text_processor,
            _hello_world_format_snippet.format(message="Filled by async text processor."),
        ),
    ),
)
async def test_snippet(
    path_or_text: Text | str | Path, text_processor: TextProcessor, expected: str
) -> None:
    snippet = Snippet(path_or_text, text_processor=text_processor)
    rendered = await HTMY().render(snippet)
    assert isinstance(rendered, SafeStr)
    assert rendered == expected
