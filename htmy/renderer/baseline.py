from __future__ import annotations

import asyncio
from collections import ChainMap
from collections.abc import Awaitable, Callable, Iterable

from htmy.core import ErrorBoundary, xml_format_string
from htmy.typing import Component, ComponentType, Context


class Renderer:
    """
    The baseline component renderer.

    Because of the simple, recursive implementation, this renderer is the easiest to reason about.
    Therefore it is useful for validating component correctness before bug reporting (if another
    renderer implementation fails), testing and debugging alternative implementations, and it can
    also serve as the baseline for benchmarking optimized renderers.

    The performance of this renderer is not production quality.
    """

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
            context: An optional rendering context.

        Returns:
            The rendered string.
        """
        return await self._render(
            component,
            # Type ignore: ChainMap expects mutable mappings,
            # but mutation is not supported by the Context typing.
            self._default_context if context is None else ChainMap(context, self._default_context),  # type: ignore[arg-type]
        )

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
        if isinstance(component, str):
            return self._string_formatter(component)
        else:
            child_context: Context = context
            if hasattr(component, "htmy_context"):  # isinstance() is too expensive.
                extra_context: Context | Awaitable[Context] = component.htmy_context()
                if isinstance(extra_context, Awaitable):
                    extra_context = await extra_context

                if len(extra_context):
                    # Context must not be mutated, so we can ignore that ChainMap expext mutable mappings.
                    child_context = ChainMap(extra_context, context)  # type: ignore[arg-type]

            try:
                children = component.htmy(child_context)
                if isinstance(children, Awaitable):
                    children = await children

                return await self._render(children, child_context)
            except Exception as e:
                if isinstance(component, ErrorBoundary):
                    return await self._render_one(component.fallback_component(e), context)

                raise e
