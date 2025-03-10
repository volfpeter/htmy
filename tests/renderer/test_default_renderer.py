from dataclasses import dataclass

import pytest

from htmy import Context, Renderer, Slots, Snippet, Text, component
from htmy.renderer import BaselineRenderer


@pytest.mark.asyncio
async def test_async_children_of_async_node() -> None:
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
    rendered = await BaselineRenderer().render(snippet)
    assert rendered == "async slot content async fc slot content"

    rendered = await Renderer().render(snippet)
    assert rendered == "async slot content async fc slot content"
