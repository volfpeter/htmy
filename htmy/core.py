from __future__ import annotations

import enum
import json
from typing import TYPE_CHECKING, Any, ClassVar, cast
from xml.sax.saxutils import escape as xml_escape
from xml.sax.saxutils import quoteattr as xml_quoteattr

if TYPE_CHECKING:
    from collections.abc import Callable

    from typing_extensions import Never, Self

    from .typing import Component, ComponentType, Context, ContextKey, ContextValue, T

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


# -- Formatting


class SkipProperty(Exception):
    """Exception raised by property formatters if the property should be skipped."""

    ...

    @classmethod
    def format_property(cls, _: Any) -> Never:
        """Property formatter that raises a `SkipProperty` error regardless of the received value."""
        raise cls("skip-property")


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

    The formatter supports both primitive and (many) complex values, such as lists,
    dictionaries, tuples, and sets. Complex values are JSON-serialized by default.

    Important: the default implementation looks up the formatter for a given value by checking
    its type, but it doesn't do this check with the base classes of the encountered type. For
    example the formatter will know how to format `datetime` object, but it won't know how to
    format a `MyCustomDatetime(datetime)` instance.

    One reason for this is efficiency: always checking the base classes of every single value is a
    lot of unnecessary calculation. The other reason is customizability: this way you could use
    subclassing for formatter selection, e.g. with `LocaleDatetime(datetime)`-like classes.

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
            dict: lambda v: json.dumps(v),
            list: lambda v: json.dumps(v),
            tuple: lambda v: json.dumps(v),
            set: lambda v: json.dumps(tuple(v)),
            XBool: lambda v: cast(XBool, v).format(),
            type(None): SkipProperty.format_property,
        }
