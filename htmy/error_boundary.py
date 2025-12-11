from __future__ import annotations

from typing import TYPE_CHECKING

from .core import SafeStr
from .renderer.context import RendererContext
from .utils import as_component_type

if TYPE_CHECKING:
    from collections.abc import Container

    from .typing import Component, ComponentType, Context


class ErrorBoundary:
    """
    Error boundary component for graceful error handling.

    If an error occurs during the rendering of the error boundary's subtree,
    the fallback component will be rendered instead.
    """

    __slots__ = ("_children", "_errors", "_fallback")

    def __init__(
        self,
        *children: ComponentType,
        fallback: Component = None,
        errors: Container[type[Exception]] | None = None,
    ) -> None:
        """
        Initialization.

        Arguments:
            *children: The wrapped children components.
            fallback: The fallback component to render in case an error occurs during children rendering.
            errors: An optional set of accepted error types. Only accepted errors are swallowed and rendered
                with the fallback. If an error is not in this set but one of its base classes is, then the
                error will still be accepted and the fallback rendered. By default all errors are accepted.
        """
        self._children = children
        self._errors = errors
        self._fallback: Component = fallback

    async def htmy(self, context: Context) -> Component:
        renderer = RendererContext.from_context(context)

        try:
            result = await renderer.render(self._children, context)
        except Exception as e:
            result = await renderer.render(self._fallback_component(e), context)

        # We must convert the already rendered string to SafeStr to avoid additional XML escaping.
        return SafeStr(result)

    def _fallback_component(self, error: Exception) -> ComponentType:
        """
        Returns the fallback component for the given error.

        Arguments:
            error: The error that occurred during the rendering of the error boundary's subtree.

        Raises:
            Exception: The received error if it's not accepted.
        """
        if not (self._errors is None or any(e in self._errors for e in type(error).mro())):
            raise error

        return as_component_type(self._fallback)
