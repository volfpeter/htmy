from __future__ import annotations

from collections import ChainMap, deque
from inspect import isawaitable
from typing import TYPE_CHECKING, TypeAlias

from anyio import create_task_group

from htmy.core import xml_format_string
from htmy.utils import is_component_sequence, is_htmy_component_type

from .context import RendererContext

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from htmy.typing import Component, ComponentSequence, ComponentType, Context, HTMYComponentType

    _PendingAsyncNode: TypeAlias = tuple["Awaitable[Component]", "_Node"]


class _Node:
    """A single node in the linked list the renderer constructs to resolve a component tree."""

    __slots__ = ("component", "context", "next")

    def __init__(self, component: ComponentType, context: Context, next: _Node | None = None) -> None:
        """
        Initialization.

        Arguments:
            component: The component in this node.
            context: The rendering context for the component.
            next: The next component in the list, if there is one.
        """
        self.component = component
        self.context = context
        self.next = next


class _ComponentRenderer:
    """
    `ComponentType` renderer that converts a component tree into a linked list of resolved (`str`) nodes.
    """

    __slots__ = ("_async_todos", "_sync_todos", "_root", "_string_formatter")

    def __init__(
        self,
        component: HTMYComponentType,
        context: Context,
        *,
        string_formatter: Callable[[str], str],
    ) -> None:
        """
        Initialization.

        Arguments:
            component: The component to render.
            context: The base context to use for rendering.
            string_formatter: The string formatter to use.
        """
        self._root = root = _Node(component, context)
        """The root node in the linked list the renderer constructs."""
        self._async_todos: deque[_PendingAsyncNode] = deque()
        """Pending `htmy()` results that must be awaited before node processing."""
        self._sync_todos: deque[_Node] = deque((root,))
        """Nodes whose `htmy()` method needs to be called."""
        self._string_formatter = string_formatter
        """The string formatter to use."""

    def _process_node_result(self, node: _Node, component: Component) -> None:
        """
        Processes the result of a single node.

        Arguments:
            node: The node that was resolved.
            component: The (awaited if async) result of `node.component.htmy()`.
        """
        if hasattr(component, "htmy"):
            node.component = component
            self._sync_todos.append(node)
        elif isinstance(component, str):
            node.component = self._string_formatter(component)
        elif component is None:
            node.component = ""
        elif is_component_sequence(component):
            self._expand_node_sequence(node, component)
        else:
            raise ValueError(f"Invalid component type: {type(component)}")

    def _expand_node_sequence(self, node: _Node, component: ComponentSequence) -> None:
        """
        Expands the given node in place with the items of the given component sequence.

        The first item takes over the resolved node's place in the list, the rest are
        appended as new nodes between the resolved node and its next node. `None` items
        are skipped.

        Arguments:
            node: The node that resolved to the given sequence.
            component: The component sequence the node resolved to.
        """
        sync_todos = self._sync_todos
        string_formatter = self._string_formatter
        context = node.context
        old_next = node.next
        items = iter(component)
        for first in items:
            if first is None:
                continue
            if isinstance(first, str):
                node.component = string_formatter(first)
            else:
                node.component = first
                sync_todos.append(node)
            break
        else:
            node.component = ""
            return

        last = node
        for c in items:
            if c is None:
                continue
            if isinstance(c, str):
                child = _Node(string_formatter(c), context, old_next)
            else:
                child = _Node(c, context, old_next)
                sync_todos.append(child)

            last.next = child
            last = child

    async def _process_async_result(self, awaitable: Awaitable[Component], node: _Node) -> None:
        """
        Resolves the given pending `htmy()` result and processes the resolved component.

        Arguments:
            awaitable: The pending `htmy()` result of `node.component`.
            node: The node that produced the awaitable.
        """
        result = await awaitable
        self._process_node_result(node, result)

    def _cancel_pending(self, async_todos: deque[_PendingAsyncNode]) -> None:
        """Closes pending `htmy()` results that were never awaited."""
        for awaitable, _ in async_todos:
            close = getattr(awaitable, "close", None)
            if close is not None:
                close()

    async def _run_async_batch(self) -> None:
        """Resolves all pending async `htmy()` results concurrently."""
        current_async_todos = self._async_todos
        self._async_todos = deque()
        async with create_task_group() as tg:
            for awaitable, node in current_async_todos:
                tg.start_soon(self._process_async_result, awaitable, node)

    async def run(self) -> str:
        """Runs the component renderer."""
        sync_todos = self._sync_todos
        process_node_result = self._process_node_result

        try:
            while sync_todos or self._async_todos:
                while sync_todos:
                    node = sync_todos.pop()
                    component = node.component
                    context = node.context

                    if hasattr(component, "htmy_context"):  # isinstance() is too expensive.
                        extra_context: Context | Awaitable[Context] = component.htmy_context()  # type: ignore[union-attr]
                        if isawaitable(extra_context):
                            extra_context = await extra_context
                        if extra_context:
                            # Context must not be mutated (ChainMap's mutability expectation is irrelevant).
                            context = node.context = ChainMap(extra_context, context)  # type: ignore[arg-type]

                    result: Component = component.htmy(context)  # type: ignore[assignment,union-attr]
                    if isawaitable(result):
                        # Coroutine creation doesn't run any component code, the
                        # result is resolved by a task group later.
                        self._async_todos.append((result, node))
                    else:
                        process_node_result(node, result)

                if self._async_todos:
                    await self._run_async_batch()
        except BaseException:
            self._cancel_pending(self._async_todos)
            raise

        parts: list[str] = []
        current: _Node | None = self._root
        while current is not None:
            parts.append(current.component)  # type: ignore[arg-type]
            current = current.next
        return "".join(parts)


async def _render_component(
    component: Component,
    *,
    context: Context,
    string_formatter: Callable[[str], str],
) -> str:
    """Renders the given component with the given settings."""
    if is_htmy_component_type(component):
        return await _ComponentRenderer(component, context, string_formatter=string_formatter).run()
    elif isinstance(component, str):
        return string_formatter(component)
    elif is_component_sequence(component):
        result = ""
        for c in component:
            if c is None:
                continue
            elif isinstance(c, str):
                result += string_formatter(c)
            else:
                result += await _ComponentRenderer(c, context, string_formatter=string_formatter).run()
        return result
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
