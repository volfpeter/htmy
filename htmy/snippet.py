import re
from collections.abc import Awaitable, Iterator, Mapping
from pathlib import Path

from .core import SafeStr, Text
from .io import open_file
from .typing import (
    Component,
    ComponentType,
    Context,
    TextProcessor,
    TextResolver,
)
from .utils import as_component_sequence, as_component_type, is_component_sequence

# -- Components and utilities


class Slots:
    """
    Utility that resolves slots in a string input to components.

    More technically, it splits a string into slot and non-slot parts, replaces the
    slot parts with the corresponding components (which may be component sequences)
    from the given slot mapping, and returns the resulting component sequence.

    The default slot placeholder is a standard XML/HTML comment of the following form:
    `<!-- slot[slot-key] -->`. Any number of whitespaces (including 0) are allowed in
    the placeholder, but the slot key must not contain any whitespaces. For details, see
    `Slots.slot_re`.

    Besides the pre-defined regular expressions in `Slots.slot_re`, any other regular
    expression can be used to identify slots as long as it meets the requirements described
    in `Slots.slots_re`.

    Implements: `htmy.typing.TextResolver`
    """

    __slots__ = ("_slot_mapping", "_slot_re", "_not_found")

    class slot_re:
        """
        Slot regular expressions.

        Requirements:

        - The regular expression must have exactly one capturing group that captures the slot key.
        """

        square_bracket = re.compile(r"<!-- *slot *\[ *([^[ ]+) *\] *-->")
        """
        Slot regular expression that matches slots defined as follows: `<!-- slot[slot-key] -->`.

        The slot key must not contain any whitespaces and there must not be any additional text
        in the XML/HTML comment. Any number of whitespaces (including 0) are allowed around the
        parts of the slot placeholder.
        """
        parentheses = re.compile(r"<!-- *slot *\( *([^( ]+) *\) *-->")
        """
        Slot regular expression that matches slots defined as follows: `<!-- slot(slot-key) -->`.

        The slot key must not contain any whitespaces and there must not be any additional text
        in the XML/HTML comment. Any number of whitespaces (including 0) are allowed around the
        parts of the slot placeholder.
        """

        # There are no defaults for angle bracket and curly braces, because
        # they may conflict with HTML and format strings.

        default = square_bracket
        """
        The default slot regular expression. Same as `Slots.slot_re.square_bracket`.
        """

    def __init__(
        self,
        slot_mapping: Mapping[str, Component],
        *,
        slot_re: re.Pattern[str] = slot_re.default,
        not_found: Component | None = None,
    ) -> None:
        """
        Initialization.

        Slot regular expressions are used to find slot keys in strings, which are then replaced
        with the corresponding component from the slot mapping. `slot_re` must have exactly one
        capturing group that captures the slot key. `Slots.slot_re` contains some predefined slot
        regular expressions, but any other regular expression can be used as long as it matches
        the capturing group requirement above.

        Arguments:
            slot_mapping: Slot mapping the maps slot keys to the corresponding component.
            slot_re: The slot regular expression that is used to find slot keys in strings.
            not_found: The component that is used to replace slot keys that are not found in
                `slot_mapping`. If `None` and the slot key is not found in `slot_mapping`,
                then a `KeyError` will be raised by `resolve()`.
        """
        self._slot_mapping = slot_mapping
        self._slot_re = slot_re
        self._not_found = not_found

    def resolve_text(self, text: str) -> Component:
        """
        Resolves the given string into components using the instance's slot regular expression
        and slot mapping.

        Arguments:
            text: The text to resolve.

        Returns:
           The component sequence the text resolves to.

        Raises:
            KeyError: If a slot key is not found in the slot mapping and `not_found` is `None`.
        """
        return tuple(self._resolve_text(text))

    def _resolve_text(self, text: str) -> Iterator[ComponentType]:
        """
        Generator that yields the slot and non-slot parts of the given string in order.

        Arguments:
            text: The text to resolve.

        Yields:
            The slot and non-slot parts of the given string.

        Raises:
            KeyError: If a slot key is not found in the slot mapping and `not_found` is `None`.
        """
        is_slot = False
        # The implementation requires that the slot regular expression has exactly one capturing group.
        for part in self._slot_re.split(text):
            if is_slot:
                resolved = self._slot_mapping.get(part, self._not_found)
                if resolved is None:
                    raise KeyError(f"Component not found for slot: {part}")

                if is_component_sequence(resolved):
                    yield from resolved
                else:
                    # mypy complains that resolved may be a sequence, but that's not the case.
                    yield resolved  # type: ignore[misc]
            else:
                yield part

            is_slot = not is_slot


class Snippet:
    """
    Component that renders text, which may be asynchronously loaded from a file.

    The entire snippet processing pipeline consists of the following steps:

    1. The text content is loaded from a file or passed directly as a `Text` instance.
    2. The text content is processed by a `TextProcessor` if provided.
    3. The processed text is converted into a component (may be component sequence)
       by a `TextResolver`, for example `Slots`.
    4. Every `str` children (produced by the steps above) is converted into a `SafeStr` for
       rendering.

    The pipeline above is a bit abstract, so here are some usage notes:

    - The text content of a snippet can be a Python format string template, in which case the
      `TextProcessor` can be a simple method that calls `str.format()` with the correct arguments.
    - Alternatively, a text processor can also be used to get only a substring -- commonly referred
      to as fragment in frameworks like Jinja -- of the original text.
    - The text processor is applied before the text resolver, which makes it possible to insert
      placeholders into the text (for example slots, like in this case:
      `..."{toolbar}...".format(toolbar="<!-- slot[toolbar] -->")`) that are then replaced with any
      `htmy.Component` by the `TextResolver` (for example `Slots`).
    - `TextResolver` can return plain `str` values, it is not necessary for it to convert strings
      to `SafeStr` to prevent unwanted escaping.

    Example:

    ```python
    from datetime import date
    from htmy import Snippet, Slots

    def text_processor(text: str, context: Context) -> str:
       return text.format(today=date.today())

    snippet = Snippet(
        "my-page.html",
        text_processor=text_processor,
        text_resolver=Slots(
            {
                "date-picker": MyDatePicker(class_="text-primary"),
                "Toolbar": MyPageToolbar(active_page="home"),
                ...
            }
        ),
    )
    ```

    In the above example, if `my-page.html` contains a `{today}` placeholder, it will be replaced
    with the current date. If it contains a `<!-- slot[toolbar] -->}` slot, then the `MyPageToolbar`
    `htmy` component instance will be rendered in its place, and the `<!-- slot[date-picker] -->` slot
    will be replaced with the `MyDatePicker` component instance.
    """

    __slots__ = ("_path_or_text", "_text_processor", "_text_resolver")

    def __init__(
        self,
        path_or_text: Text | str | Path,
        text_resolver: TextResolver | None = None,
        *,
        text_processor: TextProcessor | None = None,
    ) -> None:
        """
        Initialization.

        Arguments:
            path_or_text: The path from where the content should be loaded or a `Text`
                instance if this value should be rendered directly.
            text_resolver: An optional `TextResolver` (e.g. `Slots`) that converts the processed
                text into a component. If not provided, the text will be rendered as a `SafeStr`.
            text_processor: An optional `TextProcessor` that can be used to process the text
                content before rendering. It can be used for example for token replacement or
                string formatting.
        """
        self._path_or_text = path_or_text
        self._text_processor = text_processor
        self._text_resolver = text_resolver

    async def htmy(self, context: Context) -> Component:
        """Renders the component."""
        text = await self._get_text_content()
        if self._text_processor is not None:
            processed = self._text_processor(text, context)
            text = (await processed) if isinstance(processed, Awaitable) else processed

        if self._text_resolver is None:
            return self._render_text(text, context)

        comps = as_component_sequence(self._text_resolver.resolve_text(text))
        return tuple(
            as_component_type(self._render_text(c, context)) if isinstance(c, str) else c for c in comps
        )

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
