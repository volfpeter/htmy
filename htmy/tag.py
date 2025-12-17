from __future__ import annotations

from typing import TYPE_CHECKING

from .core import Formatter, SafeStr
from .utils import join_components

if TYPE_CHECKING:
    from .typing import Component, ComponentSequence, ComponentType, Context, Properties, PropertyValue


class _TagWithPropsImpl:
    __slots__ = ("name", "props")

    def __init__(self, name: str, props: Properties) -> None:
        self.name = name
        self.props = props

    def htmy(self, context: Context) -> ComponentType:
        formatter: Formatter = context.get(Formatter, _default_formatter)
        return SafeStr(f"<{self.name} {' '.join(formatter.format(n, v) for n, v in self.props.items())}/>")


class _TagImpl:
    __slots__ = ("child_separator", "children", "name", "props")

    def __init__(
        self,
        name: str,
        props: Properties,
        children: ComponentSequence,
        child_separator: ComponentType,
    ) -> None:
        self.name = name
        self.props = props
        self.children = children
        self.child_separator = child_separator

    def htmy(self, context: Context) -> Component:
        formatter: Formatter = context.get(Formatter, _default_formatter)
        name = self.name
        return (
            SafeStr(f"<{name} {' '.join(formatter.format(n, v) for n, v in self.props.items())}>"),
            *(
                self.children
                if self.child_separator is None
                else join_components(self.children, separator=self.child_separator, pad=True)
            ),
            SafeStr(f"</{name}>"),
        )


_default_formatter = Formatter()


class TagWithProps:
    """
    Creates a tag type that can have properties, but not children.

    Arguments:
        **props: Tag properties.
    """

    __slots__ = ("name",)

    def __init__(self, name: str) -> None:
        self.name = name

    def __call__(self, **props: PropertyValue) -> ComponentType:
        return _TagWithPropsImpl(self.name, props)


class Tag:
    __slots__ = ("child_separator", "name")

    def __init__(self, name: str, child_separator: ComponentType = "\n") -> None:
        self.name = name
        self.child_separator = child_separator

    def __call__(self, *children: ComponentType, **props: PropertyValue) -> ComponentType:
        return _TagImpl(self.name, props, children, self.child_separator)


def wildcard_tag(
    *children: ComponentType,
    htmy_name: str,
    htmy_child_separator: ComponentType = None,
    **props: PropertyValue,
) -> ComponentType:
    """
    Creates a tag that can have both children and properties, and whose tag name and
    child separator can be set.

    Arguments:
        *children: Children components.
        htmy_name: The tag name to use for this tag.
        htmy_child_separator: Optional separator component to add between children.
        **props: Tag properties.
    """
    return _TagImpl(htmy_name, props, children, htmy_child_separator)
