from __future__ import annotations

import asyncio
from collections import ChainMap
from collections.abc import Awaitable, Callable, Iterable

from .core import ErrorBoundary, xml_format_string
from .typing import Component, ComponentType, Context, ContextProvider, HTMYComponentType


class HTMY:
    """HTMY component renderer."""

    __slots__ = ("_default_context", "_string_formatter")

    def __init__(
        self,
        default_context: Context | None = None,
        *,
        string_formatter: Callable[[str], str] = xml_format_string,
    ) -> None:
        """
        Initialization.

        Arguments:
            default_context: The default context to use for rendering if `render()` doesn't
                receive a context.
            string_formatter: Callable that should be used to format plain strings. By default
                an XML-safe string formatter will be used.
        """
        self._default_context: Context = {} if default_context is None else default_context
        self._string_formatter = string_formatter

    async def render(self, component: Component, context: Context | None = None) -> str:
        """
        Renders the given component.

        Arguments:
            component: The component to render.
            context: An optional rendering context. If `None`, the renderer's default context will be used.

        Returns:
            The rendered string.
        """
        return await self._render(component, self._default_context if context is None else context)

    async def _render(self, component: Component, context: Context) -> str:
        """
        Renders a single component "level".

        Arguments:
            component: The component to render.
            context: The current rendering context.

        Returns:
            The rendered string.
        """
        if isinstance(component, str):
            return self._string_formatter(component)
        elif isinstance(component, Iterable):
            rendered_children = await asyncio.gather(
                *(self._render_one(comp, context) for comp in component)
            )

            return "".join(rendered_children)
        else:
            return await self._render_one(component, context)

    async def _render_one(self, component: ComponentType, context: Context) -> str:
        """
        Renders a single component.

        Arguments:
            component: The component to render.
            context: The current rendering context.

        Returns:
            The rendered string.
        """
        child_context = context
        if isinstance(component, ContextProvider):
            extra_context = component.htmy_context()
            if isinstance(extra_context, Awaitable):
                extra_context = await extra_context

            child_context = ChainMap(extra_context, context)

        if isinstance(component, HTMYComponentType):
            try:
                children = component.htmy(child_context)
                if isinstance(children, Awaitable):
                    children = await children

                return await self._render(children, child_context)
            except Exception as e:
                if isinstance(component, ErrorBoundary):
                    return await self._render_one(component.fallback_component(e), context)

                raise e
        elif isinstance(component, str):
            return self._string_formatter(component)
        else:
            raise TypeError("Unknown component type.")
