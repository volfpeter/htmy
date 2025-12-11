from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from typing import Any, TypeGuard

    from htmy.typing import Component, Context


class RendererType(Protocol):
    """Protocol definition for `htmy` renderers."""

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
