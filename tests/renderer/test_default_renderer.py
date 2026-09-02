from dataclasses import dataclass

import pytest
from htmy_rs.renderer import Renderer as RsRenderer

import htmy
from htmy import Context, Slots, Snippet, Text, component
from htmy.renderer.default import Renderer as DefaultRenderer
from htmy.renderer.typing import RendererType


def test_default_renderer_selection() -> None:
    """The default renderer is selected from htmy-rs if it is installed."""
    assert htmy.Renderer is htmy.renderer.Renderer
    assert htmy.renderer.Renderer is RsRenderer  # type: ignore[comparison-overlap]
    assert DefaultRenderer is not RsRenderer  # type: ignore[comparison-overlap]


@pytest.mark.anyio
async def test_async_children_of_async_node(
    baseline_renderer: RendererType,
    default_renderer: RendererType,
    streaming_renderer: RendererType,
    rs_renderer: RendererType,
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

    rendered = await rs_renderer.render(snippet)
    assert rendered == "async slot content async fc slot content"
