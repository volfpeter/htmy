from collections.abc import Callable, Coroutine, Mapping, MutableMapping
from typing import Any, Protocol, TypeAlias, TypeVar, runtime_checkable

T = TypeVar("T")
U = TypeVar("U")

# -- Properties

PropertyValue: TypeAlias = Any | None
"""Component/XML tag property value."""

Properties: TypeAlias = Mapping[str, PropertyValue]
"""Component/XML tag property mapping."""

# -- Context

ContextKey: TypeAlias = Any
"""Context key."""

ContextValue: TypeAlias = Any
"""Context value."""

Context: TypeAlias = Mapping[ContextKey, ContextValue]
"""Context mapping."""

MutableContext: TypeAlias = MutableMapping[ContextKey, ContextValue]
"""
Mutable context mapping.

It can be helpful when the created context should be marked as mutable for static type analysis
(usually the created context is a plain `dict`).
"""

# -- Components


@runtime_checkable
class SyncComponent(Protocol):
    """Protocol definition for sync `htmy` components."""

    def htmy(self, context: Context, /) -> "Component":
        """Renders the component."""
        ...


@runtime_checkable
class AsyncComponent(Protocol):
    """Protocol definition for async `htmy` components."""

    async def htmy(self, context: Context, /) -> "Component":
        """Renders the component."""
        ...


HTMYComponentType: TypeAlias = SyncComponent | AsyncComponent
"""Sync or async `htmy` component type."""

ComponentType: TypeAlias = HTMYComponentType | str
"""Type definition for a single component."""

# Omit strings from this type to simplify checks.
ComponentSequence: TypeAlias = list[ComponentType] | tuple[ComponentType, ...]
"""Component sequence type."""

Component: TypeAlias = ComponentType | ComponentSequence
"""Component type: a single component or a sequence of components."""

# -- Context providers


@runtime_checkable
class SyncContextProvider(Protocol):
    """Protocol definition for sync context providers."""

    def htmy_context(self) -> Context:
        """Returns a context for child rendering."""
        ...


@runtime_checkable
class AsyncContextProvider(Protocol):
    """Protocol definition for async context providers."""

    async def htmy_context(self) -> Context:
        """Returns a context for child rendering."""
        ...


ContextProvider: TypeAlias = SyncContextProvider | AsyncContextProvider
"""
Sync or async context provider type.

Components can implement this protocol to add extra data to the rendering context
of their entire component subtree (including themselves).
"""

# -- Text processors

TextProcessor: TypeAlias = Callable[[str, Context], str | Coroutine[Any, Any, str]]
"""Callable type that expects a string and a context, and returns a processed string."""


class TextResolver(Protocol):
    """
    Protocol definition for resolvers that convert a string to a component.
    """

    def resolve_text(self, text: str) -> Component:
        """
        Returns the resolved component for the given text.

        Arguments:
            text: The text to resolve.

        Raises:
            KeyError: If the text cannot be resolved to a component.
        """
        ...
