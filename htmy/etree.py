from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar
from xml.sax.saxutils import unescape

try:
    from lxml.etree import _Element as Element
    from lxml.etree import tostring as etree_to_string
    from lxml.html import fragment_fromstring as etree_from_string
except ImportError:
    from xml.etree.ElementTree import Element  # type: ignore[assignment]
    from xml.etree.ElementTree import fromstring as etree_from_string  # type: ignore[assignment]
    from xml.etree.ElementTree import tostring as etree_to_string  # type: ignore[no-redef]

from .core import Fragment, SafeStr
from .tag import wildcard_tag
from .typing import ComponentType, Properties

if TYPE_CHECKING:
    from collections.abc import Callable, Generator, Mapping


class ETreeConverter:
    """
    Utility for converting XML strings to custom components.

    By default the converter uses the standard library's `xml.etree.ElementTree`
    module for string to element tree, and element tree to string conversion,
    but if `lxml` is installed, it will be used instead.

    Installing `lxml` is recommended for better performance and additional features,
    like performance and support for broken HTML fragments. **Important:** `lxml` is
    far more lenient and flexible than the standard library, so having it installed is
    not only a performance boost, but it may also slightly change the element conversion
    behavior in certain edge-cases!
    """

    __slots__ = ("_rules",)

    _htmy_fragment: ClassVar[str] = "htmy_fragment"
    """
    Placeholder tag name that's used to wrap possibly multi-root XML snippets into a valid
    XML document with a single root that can be processed by standard tools.
    """

    def __init__(self, rules: Mapping[str, Callable[..., ComponentType]]) -> None:
        """
        Initialization.

        Arguments:
            rules: Tag-name to component conversion rules.
        """
        self._rules = rules

    def convert(self, element: str) -> ComponentType:
        """Converts the given (possibly multi-root) XML string to a component."""
        if len(self._rules) == 0:
            return SafeStr(element)

        element = f"<{self._htmy_fragment}>{element}</{self._htmy_fragment}>"
        return self.convert_element(etree_from_string(element))  # noqa: S314 # Only use XML strings from a trusted source.

    def convert_element(self, element: Element) -> ComponentType:
        """Converts the given `Element` to a component."""
        rules = self._rules
        if len(rules) == 0:
            return SafeStr(etree_to_string(element, encoding="unicode"))

        tag: str = element.tag  # type: ignore[assignment]
        component = Fragment if tag == self._htmy_fragment else rules.get(tag)
        children = self._convert_children(element)
        properties = self._convert_properties(element)

        return (
            wildcard_tag(*children, htmy_name=tag, **properties)
            if component is None
            else component(
                *children,
                **properties,
            )
        )

    def _convert_properties(self, element: Element) -> Properties:
        """
        Converts the attributes of the given `Element` to a `Properties` mapping.

        This method should not alter property names in any way.
        """
        return {key: unescape(value) for key, value in element.items()}

    def _convert_children(self, element: Element) -> Generator[ComponentType, None, None]:
        """
        Generator that converts all (text and `Element`) children of the given `Element` to a component.
        """
        if text := self._process_text(element.text):
            yield text

        for child in element:
            yield self.convert_element(child)
            if tail := self._process_text(child.tail):
                yield tail

    def _process_text(self, escaped_text: str | None) -> str | None:
        """Processes a single XML-escaped text child."""
        return unescape(escaped_text) if escaped_text else None
