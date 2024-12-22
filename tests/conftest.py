import pytest

from htmy.renderer import RecursiveRenderer, Renderer


@pytest.fixture(scope="session")
def default_renderer() -> Renderer:
    return Renderer()


@pytest.fixture(scope="session")
def recursive_renderer() -> RecursiveRenderer:
    return RecursiveRenderer()
