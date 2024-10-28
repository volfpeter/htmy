from __future__ import annotations

import xml.etree.ElementTree as ET
from collections.abc import Callable, Generator
from typing import TYPE_CHECKING, ClassVar
from xml.sax.saxutils import unescape

if TYPE_CHECKING:
    from collections.abc import Mapping
    from xml.etree.ElementTree import Element

    from htmy.typing import ComponentType, Properties


from htmy.core import Fragment, SafeStr, WildcardTag


class ETreeConverter:
    """
    Utility for converting XML strings to custom HTMY components.
    """

    __slots__ = ("_components",)

    _htmy_fragment: ClassVar[str] = "htmy_fragment"
    """
    Placeholder tag name that's used to wrap possibly multi-root XML snippets into a valid
    XML document with a single root that can be processed by standard tools.
    """

    def __init__(self, components: Mapping[str, Callable[..., ComponentType]]) -> None:
        """
        Initialization.

        Arguments:
            components: A tag-name -> HTMY component factory mapping.
        """
        self._components = components

    def convert(self, element: str) -> ComponentType:
        """Converts the given (possible multi-root) XML string to an HTMY component."""
        element = f"<{self._htmy_fragment}>{element}</{self._htmy_fragment}>"
        return self.convert_element(ET.fromstring(element))  # noqa: S314 # Only use from XML strings from a trusted source.

    def convert_element(self, element: Element) -> ComponentType:
        """Converts the given `Element` to an HTMY component."""
        components = self._components
        if len(components) == 0:
            return SafeStr(ET.tostring(element))

        tag: str = element.tag
        component = Fragment if tag == self._htmy_fragment else components.get(tag)
        children = self._convert_children(element)
        properties = self._convert_properties(element)

        return (
            WildcardTag(*children, htmy_name=tag, **properties)
            if component is None
            else component(
                *children,
                **properties,
            )
        )

    def _convert_properties(self, element: Element) -> Properties:
        """
        Converts the attributes of the given `Element` to an HTMY `Properties` mapping.

        This method should not alter property names in any way.
        """
        return {key: unescape(value) for key, value in element.items()}

    def _convert_children(self, element: Element) -> Generator[ComponentType, None, None]:
        """
        Generator that converts all (text and `Element`) children of the given `Element`
        into an HTMY component."""
        if text := self._process_text(element.text):
            yield text

        for child in element:
            yield self.convert_element(child)
            if tail := self._process_text(child.tail):
                yield tail

    def _process_text(self, escaped_text: str | None) -> str | None:
        """Processes a single XML-escaped text child."""
        return unescape(escaped_text) if escaped_text else None
