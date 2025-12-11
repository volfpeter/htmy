import pytest

from htmy import Context, component
from htmy.renderer import BaselineRenderer, Renderer
from htmy.renderer.context import RendererContext
from htmy.renderer.typing import RendererType


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("renderer",),
    [
        (BaselineRenderer(),),
        (BaselineRenderer({RendererContext: "not-the-renderer"}),),
        (Renderer(),),
        (Renderer({RendererContext: "not-the-renderer"}),),
    ],
)
async def test_renderer_in_context(renderer: RendererType) -> None:
    @component.context_only
    def validate_context(context: Context) -> str:
        assert context[RendererContext] is renderer
        return "success"

    assert await renderer.render(validate_context()) == "success"
