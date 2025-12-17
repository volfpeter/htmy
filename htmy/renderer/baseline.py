from __future__ import annotations

from collections import ChainMap
from inspect import isawaitable
from typing import TYPE_CHECKING

from htmy.core import xml_format_string
from htmy.utils import is_component_sequence

from .context import RendererContext

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Awaitable, Callable

    from htmy.typing import Component, ComponentType, Context


class Renderer:
    """
    The baseline renderer that support both async streaming and rendering.

    Because of the simple, recursive implementation, this renderer is the easiest to reason about.
    Therefore it is useful for validating component correctness before bug reporting (if another
    renderer implementation fails), testing and debugging alternative implementations, and it can
    also serve as the baseline for benchmarking other renderer implementations.
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

        Implements `htmy.renderer.typing.RendererType`.

        Arguments:
            component: The component to render.
            context: An optional rendering context.

        Returns:
            The rendered string.
        """
        chunks = []
        async for chunk in self.stream(component, context):
            chunks.append(chunk)

        return "".join(chunks)

    async def stream(
        self, component: Component, context: Context | None = None
    ) -> AsyncGenerator[str, None]:
        """
        Async generator that renders the given component.

        Implements `htmy.renderer.typing.StreamingRendererType`.

        Arguments:
            component: The component to render.
            context: An optional rendering context.

        Yields:
            The rendered strings.
        """
        # Create a new default context that also contains the renderer instance.
        # We must not put it in `self._default_context` because then the renderer
        # would keep a reference to itself.
        default_context = {**self._default_context, RendererContext: self}
        # Type ignore: ChainMap expects mutable mappings, but context mutation is not allowed so don't care.
        context = (
            default_context if context is None else ChainMap(context, default_context)  # type: ignore[arg-type]
        )

        async for chunk in self._stream(component, context):
            yield chunk

    async def _stream(self, component: Component, context: Context) -> AsyncGenerator[str, None]:
        """
        Renders the given component with the given context.

        Arguments:
            component: The component to render.
            context: The current rendering context.

        Yields:
            String chunks of the rendered component.
        """
        if isinstance(component, str):
            yield self._string_formatter(component)
        elif component is None:
            return
        elif is_component_sequence(component):
            for comp in component:
                if comp is not None:
                    async for chunk in self._stream_one(comp, context):
                        yield chunk
        else:
            # Sync or async htmy component.
            async for chunk in self._stream_one(component, context):  # type: ignore[arg-type]
                yield chunk

    async def _stream_one(self, component: ComponentType, context: Context) -> AsyncGenerator[str, None]:
        """
        Renders a single component.

        Arguments:
            component: The component to render.
            context: The current rendering context.

        Yields:
            The rendered strings.
        """
        if isinstance(component, str):
            yield self._string_formatter(component)
        elif component is None:
            return
        else:
            # Handle context providers
            child_context: Context = context
            if hasattr(component, "htmy_context"):  # isinstance() is too expensive.
                extra_context: Context | Awaitable[Context] = component.htmy_context()
                if isawaitable(extra_context):
                    extra_context = await extra_context

                if len(extra_context):
                    # Context must not be mutated, so we can ignore that ChainMap expects mutable mappings.
                    child_context = ChainMap(extra_context, context)  # type: ignore[arg-type]

            children = component.htmy(child_context)
            if isawaitable(children):
                children = await children

            async for chunk in self._stream(children, child_context):
                yield chunk
