from __future__ import annotations

import abc
import asyncio
import enum
from collections.abc import Awaitable, Callable, Container
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, Generic, TypedDict, cast, overload
from xml.sax.saxutils import escape as xml_escape
from xml.sax.saxutils import quoteattr as xml_quoteattr

from .io import open_file
from .typing import (
    AsyncFunctionComponent,
    Component,
    ComponentType,
    Context,
    ContextKey,
    ContextValue,
    FunctionComponent,
    PropertyValue,
    SyncFunctionComponent,
    T,
    TextProcessor,
    is_component_sequence,
)
from .utils import join_components

if TYPE_CHECKING:
    from typing_extensions import Self
else:
    Self = Any

# -- Utility components


class Fragment:
    """Fragment utility component that simply wraps some children components."""

    __slots__ = ("_children",)

    def __init__(self, *children: ComponentType) -> None:
        """
        Initialization.

        Arguments:
            *children: The wrapped children.
        """
        self._children = children

    def htmy(self, context: Context) -> Component:
        """Renders the component."""
        return self._children


class ErrorBoundary(Fragment):
    """
    Error boundary component for graceful error handling.

    If an error occurs during the rendering of the error boundary's subtree,
    the fallback component will be rendered instead.
    """

    __slots__ = ("_errors", "_fallback")

    def __init__(
        self,
        *children: ComponentType,
        fallback: Component | None = None,
        errors: Container[type[Exception]] | None = None,
    ) -> None:
        """
        Initialization.

        Arguments:
            *children: The wrapped children components.
            fallback: The fallback component to render in case an error occurs during children rendering.
            errors: An optional set of accepted error types. Only accepted errors are swallowed and rendered
                with the fallback. If an error is not in this set but one of its base classes is, then the
                error will still be accepted and the fallbak rendered. By default all errors are accepted.
        """
        super().__init__(*children)
        self._errors = errors
        self._fallback: Component = "" if fallback is None else fallback

    def fallback_component(self, error: Exception) -> ComponentType:
        """
        Returns the fallback component for the given error.

        Arguments:
            error: The error that occurred during the rendering of the error boundary's subtree.

        Raises:
            Exception: The received error if it's not accepted.
        """
        if not (self._errors is None or any(e in self._errors for e in type(error).mro())):
            raise error

        return (
            Fragment(*self._fallback)
            if is_component_sequence(self._fallback)
            else cast(ComponentType, self._fallback)
        )


class WithContext(Fragment):
    """
    A simple, static context provider component.
    """

    __slots__ = ("_context",)

    def __init__(self, *children: ComponentType, context: Context) -> None:
        """
        Initialization.

        Arguments:
            *children: The children components to wrap in the given context.
            context: The context to make available to children components.
        """
        super().__init__(*children)
        self._context = context

    def htmy_context(self) -> Context:
        """Returns the context for child rendering."""
        return self._context


class Snippet:
    """
    Base component that can load its content from a file.
    """

    __slots__ = ("_path_or_text", "_text_processor")

    def __init__(
        self,
        path_or_text: Text | str | Path,
        *,
        text_processor: TextProcessor | None = None,
    ) -> None:
        """
        Initialization.

        Arguments:
            path_or_text: The path from where the content should be loaded or a `Text`
                instance if this value should be rendered directly.
            text_processor: An optional text processors that can be used to process the text
                content before rendering. It can be used for example for token replacement or
                string formatting.
        """
        self._path_or_text = path_or_text
        self._text_processor = text_processor

    async def htmy(self, context: Context) -> Component:
        """Renders the component."""
        text = await self._get_text_content()
        if self._text_processor is not None:
            processed = self._text_processor(text, context)
            text = (await processed) if isinstance(processed, Awaitable) else processed

        return self._render_text(text, context)

    async def _get_text_content(self) -> str:
        """Returns the plain text content that should be rendered."""
        path_or_text = self._path_or_text

        if isinstance(path_or_text, Text):
            return path_or_text
        else:
            async with await open_file(path_or_text, "r") as f:
                return await f.read()

    def _render_text(self, text: str, context: Context) -> Component:
        """
        Render function that takes the text that must be rendered and the current rendering context,
        and returns the corresponding component.
        """
        return SafeStr(text)


# -- Context utilities


class ContextAware:
    """
    Base class with utilities for safe context use.

    Features:

    - Register subclass instance in a context.
    - Load subclass instance from context.
    - Wrap components within a subclass instance context.

    Subclass instance registration:

    Direct subclasses are considered the "base context type". Subclass instances are
    registered in contexts under their own type and also under their "base context type".

    Example:

    ```python
    class ContextDataDefinition(ContextAware):
        # This is the "base context type", instances of this class and its subclasses
        # will always be registered under this type.
        ...

    class ContextDataImplementation(ContextDataDefinition):
        # Instances of this class will be registered under `ContextDataDefinition` (the
        # "base context type") and also under this type.
        ...

    class SpecializedContextDataImplementation(ContextDataImplementation):
        # Instances of this class will be registered under `ContextDataDefinition` (the
        # "base context type") and also under this type, but they will not be registered
        # under `ContextDataImplementation`, since that's not the base context type.
        ...
    ```
    """

    __slots__ = ()

    _base_context_type: ClassVar[type[ContextAware] | None] = None

    def __init_subclass__(cls) -> None:
        if cls.mro()[1] == ContextAware:
            cls._base_context_type = cls

    def in_context(self, *children: ComponentType) -> WithContext:
        """
        Creates a context provider component that renders the given children using this
        instance in its context.
        """
        return WithContext(*children, context=self.to_context())

    def to_context(self) -> Context:
        """
        Creates a context with this instance in it.

        See the context registration rules in the class documentation for more information.
        """
        result: dict[ContextKey, ContextValue] = {type(self): self}
        if self._base_context_type is not None:
            result[self._base_context_type] = self

        return result

    @classmethod
    def from_context(cls, context: Context, default: Self | None = None) -> Self:
        """
        Looks up an instance of this class from the given contexts.

        Arguments:
            context: The context the instance should be loaded from.
            default: The default to use if no instance was found in the context.
        """
        result = context[cls] if default is None else context.get(cls, default)
        if isinstance(result, cls):
            return result

        raise TypeError(f"Invalid context data type for {cls.__name__}.")


# -- Function components


class SyncFunctionComponentWrapper(Generic[T]):
    """Base class `FunctionComponent` wrappers."""

    __slots__ = ("_props",)

    _wrapped_function: SyncFunctionComponent[T]

    def __init__(self, props: T) -> None:
        self._props = props

    def __init_subclass__(cls, *, func: SyncFunctionComponent[T]) -> None:
        cls._wrapped_function = func

    def htmy(self, context: Context) -> Component:
        """Renders the component."""
        # type(self) is necessary, otherwise the wrapped function would be called
        # with an extra self argument...
        return type(self)._wrapped_function(self._props, context)


class AsyncFunctionComponentWrapper(Generic[T]):
    """Base class `FunctionComponent` wrappers."""

    __slots__ = ("_props",)

    _wrapped_function: AsyncFunctionComponent[T]

    def __init__(self, props: T) -> None:
        self._props = props

    def __init_subclass__(cls, *, func: AsyncFunctionComponent[T]) -> None:
        cls._wrapped_function = func

    async def htmy(self, context: Context) -> Component:
        """Renders the component."""
        # type(self) is necessary, otherwise the wrapped function would be called
        # with an extra self argument...
        return await type(self)._wrapped_function(self._props, context)


@overload
def component(func: SyncFunctionComponent[T]) -> type[SyncFunctionComponentWrapper[T]]: ...


@overload
def component(func: AsyncFunctionComponent[T]) -> type[AsyncFunctionComponentWrapper[T]]: ...


def component(
    func: FunctionComponent[T],
) -> type[SyncFunctionComponentWrapper[T]] | type[AsyncFunctionComponentWrapper[T]]:
    """
    Decorator that converts the given function into a component.

    Internally this is achieved by wrapping the function in a pre-configured
    `FunctionComponentWrapper` subclass.

    Arguments:
        func: The decorated function component.

    Returns:
        A pre-configured `FunctionComponentWrapper` subclass.
    """

    if asyncio.iscoroutinefunction(func):

        class AsyncFCW(AsyncFunctionComponentWrapper[T], func=func): ...

        return AsyncFCW
    else:

        class SyncFCW(SyncFunctionComponentWrapper[T], func=func): ...  # type: ignore[arg-type]

        return SyncFCW


# -- Formatting


class SkipProperty(Exception):
    """Exception raised by property formatters if the property should be skipped."""

    ...


class Text(str):
    """Marker class for differentiating text content from other strings."""

    ...


class SafeStr(Text):
    """
    String subclass whose instances shouldn't get escaped during rendering.

    Note: any operation on `SafeStr` instances will result in plain `str` instances which
    will be rendered normally. Make sure the `str` to `SafeStr` conversion (`SafeStr(my_string)`)
    takes when there's no string operation afterwards.
    """

    ...


class XBool(enum.Enum):
    """
    Utility for the valid formatting of boolean XML (and HTML) attributes.

    See this article for more information:
    https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes#boolean_attributes
    """

    true = True
    false = False

    def format(self) -> str:
        """
        Raises `SkipProperty` for `XBool.false`, returns empty string for `XBool.true`.
        """
        if self is XBool.true:
            return ""

        raise SkipProperty()


def xml_format_string(value: str) -> str:
    """Escapes `<`, `>`, and `&` characters in the given string, unless it's a `SafeStr`."""
    return value if isinstance(value, SafeStr) else xml_escape(value)


class Formatter(ContextAware):
    """
    The default, context-aware property name and value formatter.

    Important: the default implementation looks up the formatter for a given value by checking
    its type, but it doesn't do this check with the base classes of the encountered type. For
    example the formatter will know how to format `datetime` object, but it won't know how to
    format a `MyCustomDatetime(datetime)` instance.

    One reason for this is efficiency: always checking the base classes of every single value is a
    lot of unnecessary calculation. The other reason is customizability: this way you could use
    subclassing for fomatter selection, e.g. with `LocaleDatetime(datetime)`-like classes.

    Property name and value formatters may raise a `SkipProperty` error if a property should be skipped.
    """

    __slots__ = ("_default_formatter", "_name_formatter", "_value_formatters")

    def __init__(
        self,
        *,
        default_formatter: Callable[[Any], str] = str,
        name_formatter: Callable[[str], str] | None = None,
    ) -> None:
        """
        Initialization.

        Arguments:
            default_formatter: The default property value formatter to use if no formatter could
                be found for a given value.
            name_formatter: Optional property name formatter (for replacing the default name formatter).
        """
        super().__init__()
        self._default_formatter = default_formatter
        self._name_formatter = self._format_name if name_formatter is None else name_formatter
        self._value_formatters: dict[type, Callable[[Any], str]] = self._base_formatters()

    def add(self, key: type[T], formatter: Callable[[T], str]) -> Self:
        """Registers the given value formatter under the given key."""
        self._value_formatters[key] = formatter
        return self

    def format(self, name: str, value: Any) -> str:
        """
        Formats the given name-value pair.

        Returns an empty string if the property name or value should be skipped.

        See `SkipProperty` for more information.
        """
        try:
            return f"{self.format_name(name)}={xml_quoteattr(self.format_value(value))}"
        except SkipProperty:
            return ""

    def format_name(self, name: str) -> str:
        """
        Formats the given name.

        Raises:
            SkipProperty: If the property should be skipped.
        """
        return self._name_formatter(name)

    def format_value(self, value: Any) -> str:
        """
        Formats the given value.

        Arguments:
            value: The property value to format.

        Raises:
            SkipProperty: If the property should be skipped.
        """
        fmt = self._value_formatters.get(type(value), self._default_formatter)
        return fmt(value)

    def _format_name(self, name: str, /) -> str:
        """The default property name formatter."""
        no_replacement = "_" in {name[0], name[-1]}
        return name.strip("_") if no_replacement else name.replace("_", "-")

    def _base_formatters(self) -> dict[type, Callable[[Any], str]]:
        """Factory that creates the default value formatter mapping."""
        from datetime import date, datetime

        return {
            bool: lambda v: "true" if v else "false",
            date: lambda d: cast(date, d).isoformat(),
            datetime: lambda d: cast(datetime, d).isoformat(),
            XBool: lambda v: cast(XBool, v).format(),
        }


# -- XML


_default_tag_formatter = Formatter()


class TagConfig(TypedDict, total=False):
    """Tag configuration."""

    child_separator: ComponentType | None


class BaseTag(abc.ABC):
    """
    Base tag class.

    Tags are always synchronous.

    If the content of a tag must be calculated asynchronously, then the content can be implemented
    as a separate async component or be resolved in an async parent component. If a property of a
    tag must be calculated asynchronously, then the tag can be wrapped in an async component that
    resolves the async content and then passes the value to the tag.
    """

    __slots__ = ("_htmy_name",)

    def __init__(self) -> None:
        self._htmy_name = self._get_htmy_name()

    @property
    def htmy_name(self) -> str:
        """The tag name."""
        return self._htmy_name

    @abc.abstractmethod
    def htmy(self, context: Context) -> Component:
        """Abstract base component implementation."""
        ...

    def _get_htmy_name(self) -> str:
        return type(self).__name__


class TagWithProps(BaseTag):
    """Base class for tags with properties."""

    __slots__ = ("props",)

    def __init__(self, **props: PropertyValue) -> None:
        """
        Initialization.

        Arguments:
            **props: Tag properties.
        """
        super().__init__()
        self.props = props

    def htmy(self, context: Context) -> Component:
        """Renders the component."""
        name = self.htmy_name
        props = self._htmy_format_props(context=context)
        return SafeStr(f"<{name} {props}/>")

    def _htmy_format_props(self, context: Context) -> str:
        """Formats tag properties."""
        formatter = Formatter.from_context(context, _default_tag_formatter)
        return " ".join(formatter.format(name, value) for name, value in self.props.items())


class Tag(TagWithProps):
    """Base class for tags with both properties and children."""

    __slots__ = ("children",)

    tag_config: TagConfig = {"child_separator": "\n"}

    def __init__(self, *children: ComponentType, **props: PropertyValue) -> None:
        """
        Initialization.

        Arguments:
            *children: Children components.
            **props: Tag properties.
        """
        super().__init__(**props)
        self.children = children

    @property
    def child_separator(self) -> ComponentType | None:
        """The child separator to use."""
        return self.tag_config.get("child_separator", None)

    def htmy(self, context: Context) -> Component:
        """Renders the component."""
        name = self.htmy_name
        props = self._htmy_format_props(context=context)
        opening, closing = SafeStr(f"<{name} {props}>"), SafeStr(f"</{name}>")
        separator = self.child_separator
        return (
            opening,
            *(
                self.children
                if separator is None
                else join_components(self.children, separator=separator, pad=True)
            ),
            closing,
        )


class WildcardTag(Tag):
    """Tag that can have both children and properties, and whose tag name can be set."""

    __slots__ = ("_child_separator",)

    def __init__(
        self,
        *children: ComponentType,
        htmy_name: str,
        htmy_child_separator: ComponentType | None = None,
        **props: PropertyValue,
    ) -> None:
        """
        Initialization.

        Arguments:
            *children: Children components.
            htmy_name: The tag name to use for this tag.
            htmy_child_separator: The child separator to use (if any).
            **props: Tag properties.
        """
        super().__init__(*children, **props)
        self._htmy_name = htmy_name
        self._child_separator = htmy_child_separator

    @property
    def child_separator(self) -> ComponentType | None:
        return self._child_separator
