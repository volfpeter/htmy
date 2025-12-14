from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from typing import Any, TypeGuard

    from htmy.typing import Component, Context


class RendererType(Protocol):
    """Protocol definition for renderers."""

    async def render(self, component: Component, context: Context | None = None) -> str:
        """
        Renders the given component.

        Arguments:
            component: The component to render.
            context: An optional rendering context.

        Returns:
            The rendered string.
        """
        ...


def is_renderer(obj: Any | None) -> TypeGuard[RendererType]:
    """Type guard that checks if the given object is a renderer."""
    # Just a basic check, don't waste time here.
    render: Any = getattr(obj, "render", None)
    return render is not None


class StreamingRendererType(RendererType, Protocol):
    """Protocol definition for streaming renderers."""

    async def stream(
        self, component: Component, context: Context | None = None
    ) -> AsyncGenerator[str, None]:
        """
        Async generator that renders the given component.

        Arguments:
            component: The component to render.
            context: An optional rendering context.

        Yields:
            The rendered strings.
        """
        ...


def is_streaming_renderer(obj: Any | None) -> TypeGuard[StreamingRendererType]:
    """Type guard that checks if the given object is a streaming renderer."""
    if not is_renderer(obj):
        return False

    # Just a basic check, don't waste time here.
    stream: Any = getattr(obj, "stream", None)
    return stream is not None
