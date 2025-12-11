from __future__ import annotations

from asyncio import gather as asyncio_gather
from collections import ChainMap, deque
from inspect import isawaitable, iscoroutinefunction
from typing import TYPE_CHECKING, TypeAlias

from htmy.core import xml_format_string
from htmy.typing import Context
from htmy.utils import is_component_sequence

from .context import RendererContext

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Iterator

    from htmy.typing import Component, ComponentType, ContextProvider


class _Node:
    """A single node in the linked list the renderer constructs to resolve a component tree."""

    __slots__ = ("component", "next")

    def __init__(self, component: ComponentType, next: _Node | None = None) -> None:
        """
        Initialization.

        Arguments:
            component: The component in this node.
            next: The next component in the list, if there is one.
        """
        self.component = component
        self.next = next

    def iter_nodes(self, *, include_self: bool = True) -> Iterator[_Node]:
        """
        Iterates over all following nodes.

        Arguments:
            include_self: Whether the node on which this method is called should also
                be included in the iterator.
        """
        current = self if include_self else self.next
        while current is not None:
            yield current
            current = current.next


_NodeAndChildContext: TypeAlias = tuple[_Node, Context]


class _ComponentRenderer:
    """
    `ComponentType` renderer that converts a component tree into a linked list of resolved (`str`) nodes.
    """

    __slots__ = ("_async_todos", "_sync_todos", "_root", "_string_formatter")

    def __init__(
        self,
        component: ComponentType,
        context: Context,
        *,
        string_formatter: Callable[[str], str],
    ) -> None:
        """
        Initialization.

        Arguments:
            component: The component to render.
            context: The base context to use for rendering the component.
            string_formatter: The string formatter to use.
        """
        self._async_todos: deque[_NodeAndChildContext] = deque()
        """Async node - context tuples that need to be rendered."""
        self._sync_todos: deque[_NodeAndChildContext] = deque()
        """
        Sync node - context tuples that need to be rendered (`node.component` is an `HTMYComponentType`).
        """
        self._string_formatter = string_formatter
        """The string formatter to use."""

        if isinstance(component, str):
            root = _Node(string_formatter(component), None)
        else:
            root = _Node(component, None)
            self._schedule_node(root, context)
        self._root = root
        """The root node in the linked list the renderer constructs."""

    async def _extend_context(self, component: ContextProvider, context: Context) -> Context:
        """
        Returns a new context from the given component and context.

        Arguments:
            component: A `ContextProvider` component.
            context: The current rendering context.
        """
        extra_context: Context | Awaitable[Context] = component.htmy_context()
        if isawaitable(extra_context):
            extra_context = await extra_context

        return (
            # Context must not be mutated. We can ignore that ChainMap expects mutable mappings.
            ChainMap(extra_context, context)  # type: ignore[arg-type]
            if extra_context
            else context
        )

    def _process_node_result(self, parent_node: _Node, component: Component, context: Context) -> None:
        """
        Processes the result of a single node.

        Arguments:
            parent_node: The node that was resolved.
            component: The (awaited if async) result of `parent_node.component.htmy()`.
            context: The context that was used for rendering `parent_node.component`.
        """
        schedule_node = self._schedule_node
        string_formatter = self._string_formatter
        if hasattr(component, "htmy"):
            parent_node.component = component
            schedule_node(parent_node, context)
        elif isinstance(component, str):
            parent_node.component = string_formatter(component)
        elif is_component_sequence(component):
            if len(component) == 0:
                parent_node.component = ""
                return

            first_comp, *rest_comps = component
            if isinstance(first_comp, str):
                parent_node.component = string_formatter(first_comp)
            else:
                parent_node.component = first_comp
                schedule_node(parent_node, context)

            old_next = parent_node.next
            last: _Node = parent_node
            for c in rest_comps:
                if isinstance(c, str):
                    node = _Node(string_formatter(c), old_next)
                else:
                    node = _Node(c, old_next)
                    schedule_node(node, context)

                last.next = node
                last = node
        else:
            raise ValueError(f"Invalid component type: {type(component)}")

    async def _process_async_node(self, node: _Node, context: Context) -> None:
        """
        Processes the given node. `node.component` must be an async component.
        """
        result = await node.component.htmy(context)  # type: ignore[misc,union-attr]
        self._process_node_result(node, result, context)

    def _schedule_node(self, node: _Node, child_context: Context) -> None:
        """
        Schedules the given node for rendering with the given child context.

        `node.component` must be an `HTMYComponentType` (single component and not `str`).
        """
        component = node.component
        if component is None:
            pass  # Just skip the node
        elif iscoroutinefunction(component.htmy):  # type: ignore[union-attr]
            self._async_todos.append((node, child_context))
        else:
            self._sync_todos.append((node, child_context))

    async def run(self) -> str:
        """Runs the component renderer."""
        async_todos = self._async_todos
        sync_todos = self._sync_todos
        process_node_result = self._process_node_result
        process_async_node = self._process_async_node

        while sync_todos or async_todos:
            while sync_todos:
                node, child_context = sync_todos.pop()
                component = node.component
                if component is None:
                    continue

                if hasattr(component, "htmy_context"):  # isinstance() is too expensive.
                    child_context = await self._extend_context(component, child_context)  # type: ignore[arg-type]

                if iscoroutinefunction(component.htmy):  # type: ignore[union-attr]
                    async_todos.append((node, child_context))
                else:
                    result: Component = component.htmy(child_context)  # type: ignore[assignment,union-attr]
                    process_node_result(node, result, child_context)

            if async_todos:
                current_async_todos = async_todos
                self._async_todos = async_todos = deque()
                await asyncio_gather(*(process_async_node(n, ctx) for n, ctx in current_async_todos))

        return "".join(node.component for node in self._root.iter_nodes() if node.component is not None)  # type: ignore[misc]


async def _render_component(
    component: Component,
    *,
    context: Context,
    string_formatter: Callable[[str], str],
) -> str:
    """Renders the given component with the given settings."""
    if hasattr(component, "htmy"):
        return await _ComponentRenderer(component, context, string_formatter=string_formatter).run()
    elif isinstance(component, str):
        return string_formatter(component)
    elif is_component_sequence(component):
        if len(component) == 0:
            return ""

        renderers = (_ComponentRenderer(c, context, string_formatter=string_formatter) for c in component)
        return "".join(await asyncio_gather(*(r.run() for r in renderers)))
    elif component is None:
        return ""
    else:
        raise ValueError(f"Invalid component type: {type(component)}")


class Renderer:
    """
    The default renderer.

    It resolves component trees by converting them to a linked list of resolved component parts
    before combining them to the final string.
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

        Implements `htmy.typing.RendererType`.

        Arguments:
            component: The component to render.
            context: An optional rendering context.

        Returns:
            The rendered string.
        """
        # Create a new default context that also contains the renderer instance.
        # We must not put it in `self._default_context` because then the renderer
        # would keep a reference to itself.
        default_context = {**self._default_context, RendererContext: self}
        # Type ignore: ChainMap expects mutable mappings, but context mutation is not allowed so don't care.
        context = (
            default_context if context is None else ChainMap(context, default_context)  # type: ignore[arg-type]
        )
        return await _render_component(component, context=context, string_formatter=self._string_formatter)
