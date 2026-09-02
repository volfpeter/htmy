import pytest
from htmy_rs.renderer import Renderer as RsRenderer

from htmy.renderer import BaselineRenderer, StreamingRenderer
from htmy.renderer.default import Renderer


@pytest.fixture(scope="session")
def default_renderer() -> Renderer:
    return Renderer()


@pytest.fixture(scope="session")
def baseline_renderer() -> BaselineRenderer:
    return BaselineRenderer()


@pytest.fixture(scope="session")
def streaming_renderer() -> StreamingRenderer:
    return StreamingRenderer()


@pytest.fixture(scope="session")
def rs_renderer() -> RsRenderer:
    return RsRenderer()
