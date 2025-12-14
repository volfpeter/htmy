import pytest

from htmy.renderer import BaselineRenderer, Renderer, StreamingRenderer


@pytest.fixture(scope="session")
def default_renderer() -> Renderer:
    return Renderer()


@pytest.fixture(scope="session")
def baseline_renderer() -> BaselineRenderer:
    return BaselineRenderer()


@pytest.fixture(scope="session")
def streaming_renderer() -> StreamingRenderer:
    return StreamingRenderer()
