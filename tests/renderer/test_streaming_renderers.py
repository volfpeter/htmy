from htmy.renderer.typing import RendererType, is_streaming_renderer


def test_is_streaming_renderer(
    baseline_renderer: RendererType, default_renderer: RendererType, streaming_renderer: RendererType
) -> None:
    assert is_streaming_renderer(streaming_renderer)
    assert is_streaming_renderer(baseline_renderer)
    assert not is_streaming_renderer(default_renderer)
