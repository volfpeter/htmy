from dataclasses import dataclass

import pytest

from htmy import Context, Slots, Snippet, Text, component
from htmy.renderer.typing import RendererType


@pytest.mark.anyio
async def test_async_children_of_async_node(
    baseline_renderer: RendererType,
    default_renderer: RendererType,
    streaming_renderer: RendererType,
) -> None:
    @dataclass
    class Content:
        message: str

        async def htmy(self, ctx: Context) -> str:
            return self.message

    @component
    async def fc_content(message: str, ctx: Context) -> str:
        return message

    snippet = Snippet(
        Text("<!-- slot[content] --> <!-- slot[fc-content] -->"),
        Slots(
            {
                "content": Content("async slot content"),
                "fc-content": fc_content("async fc slot content"),
            }
        ),
    )
    rendered = await baseline_renderer.render(snippet)
    assert rendered == "async slot content async fc slot content"

    rendered = await default_renderer.render(snippet)
    assert rendered == "async slot content async fc slot content"

    rendered = await streaming_renderer.render(snippet)
    assert rendered == "async slot content async fc slot content"
