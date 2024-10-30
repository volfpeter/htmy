from pathlib import Path

import pytest

from htmy import HTMY, Snippet, Text

from .utils import tests_root

_hello_world_snippet = "\n".join(
    (
        "<div>",
        "  <title>Hello World!</title>",
        "  <Paragraph>The quick brown fox jumps over the lazy dog.</Paragraph>",
        "</div>",
        "",
    )
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("path_or_text", "expected"),
    (
        ("tests/data/hello-world-snippet.html", _hello_world_snippet),
        (tests_root / "data" / "hello-world-snippet.html", _hello_world_snippet),
        (Text(_hello_world_snippet), _hello_world_snippet),
    ),
)
async def test_snippet(path_or_text: Text | str | Path, expected: str) -> None:
    snippet = Snippet(path_or_text)
    rendered = await HTMY().render(snippet)
    assert rendered == expected
