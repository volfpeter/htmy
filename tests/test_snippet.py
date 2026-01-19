import re
from collections.abc import Mapping
from pathlib import Path
from typing import cast

import pytest

from htmy import Component, ComponentType, Context, Renderer, SafeStr, Slots, Snippet, Text, html
from htmy.typing import TextProcessor

from .utils import tests_root

_hello_world_format_snippet = "\n".join(
    (
        "<div>",
        "  <title>Hello World!</title>",
        "  <Paragraph>{message}</Paragraph>",
        "</div>",
        "",
    )
)

_hello_world_snippet = _hello_world_format_snippet.format(
    message="The quick brown fox jumps over the lazy dog."
)


def message_to_slot_text_processor(text: str, ctx: Context) -> str:
    # Replace {message} with some text and a message and a signature slot.
    return text.format(
        message=(
            "before message slot "
            "<!-- slot[message] -->"
            " between slots "
            "<!-- slot[signature] -->"
            " after signature slot"
        )
    )


def sync_text_processor(text: str, context: Context) -> str:
    assert isinstance(context, Mapping)
    return text.format(message="Filled by sync text processor.")


async def async_text_processor(text: str, context: Context) -> str:
    assert isinstance(context, Mapping)
    return text.format(message="Filled by async text processor.")


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("path_or_text", "text_processor", "expected"),
    (
        ("tests/data/hello-world-snippet.html", None, _hello_world_snippet),
        (tests_root / "data" / "hello-world-snippet.html", None, _hello_world_snippet),
        (Text(_hello_world_snippet), None, _hello_world_snippet),
        (
            Text(_hello_world_format_snippet),
            sync_text_processor,
            _hello_world_format_snippet.format(message="Filled by sync text processor."),
        ),
        (
            Text(_hello_world_format_snippet),
            async_text_processor,
            _hello_world_format_snippet.format(message="Filled by async text processor."),
        ),
    ),
)
async def test_snippet(
    path_or_text: Text | str | Path, text_processor: TextProcessor, expected: str
) -> None:
    snippet = Snippet(path_or_text, text_processor=text_processor)
    rendered = await Renderer().render(snippet)
    assert isinstance(rendered, str)
    assert rendered == expected


class _SlotTexts:
    slot_mapping: dict[str, Component] = {
        "s1": [html.p("slot-one-part-one", class_="s1"), html.p("slot-one-part-two", class_="s1")],
        "s2": html.p("slot-two-replacement", class_="s2"),
    }
    not_found_component = "not-found"
    full_slot_mapping: dict[str, Component] = {
        **slot_mapping,
        "s3": not_found_component,
    }

    base = (
        "one   <!--slot {open} s1   {close} --> two <!-- slot{open}s2{close}-->"
        "<!-- slot{open} s2{close} -->   <!--   slot{open}s3 {close} -->"
    )

    split = ["one   ", "s1", " two ", "s2", "", "s2", "   ", "s3", ""]
    mapped_split = (
        "one   ",
        *cast(list[ComponentType], full_slot_mapping["s1"]),
        " two ",
        full_slot_mapping["s2"],
        "",
        full_slot_mapping["s2"],
        "   ",
        full_slot_mapping["s3"],
        "",
    )

    square_bracket = base.format(open="[", close="]")
    parentheses = base.format(open="(", close=")")


@pytest.mark.parametrize(
    ("text", "split_re", "expected"),
    (
        # -- Square bracket text
        (_SlotTexts.square_bracket, Slots.slot_re.default, _SlotTexts.split),  # Test default
        (_SlotTexts.square_bracket, Slots.slot_re.square_bracket, _SlotTexts.split),
        (_SlotTexts.square_bracket, Slots.slot_re.parentheses, None),
        # -- Parentheses text
        (_SlotTexts.parentheses, Slots.slot_re.default, None),  # Test default
        (_SlotTexts.parentheses, Slots.slot_re.square_bracket, None),
        (_SlotTexts.parentheses, Slots.slot_re.parentheses, _SlotTexts.split),
    ),
)
def test_slots_re(text: str, split_re: re.Pattern[str], expected: list[str] | None) -> None:
    result = split_re.split(text)
    if expected is None:
        assert len(result) == 1
        assert result[0] == text
    else:
        assert result == expected


def test_default_slot_re() -> None:
    assert Slots.slot_re.default is Slots.slot_re.square_bracket


@pytest.mark.parametrize(
    ("slots", "text", "expected"),
    (
        # -- Square bracket text
        (
            Slots(
                _SlotTexts.slot_mapping,
                not_found=_SlotTexts.not_found_component,
            ),
            _SlotTexts.square_bracket,
            _SlotTexts.mapped_split,
        ),
        (
            Slots(
                _SlotTexts.slot_mapping,
                slot_re=Slots.slot_re.square_bracket,
                not_found=_SlotTexts.not_found_component,
            ),
            _SlotTexts.square_bracket,
            _SlotTexts.mapped_split,
        ),
        (
            Slots(
                _SlotTexts.slot_mapping,
                slot_re=Slots.slot_re.parentheses,
            ),
            _SlotTexts.square_bracket,
            None,
        ),
        # -- Parentheses text
        (
            Slots(
                _SlotTexts.slot_mapping,
            ),
            _SlotTexts.parentheses,
            None,
        ),
        (
            Slots(
                _SlotTexts.slot_mapping,
                slot_re=Slots.slot_re.square_bracket,
            ),
            _SlotTexts.parentheses,
            None,
        ),
        (
            Slots(
                _SlotTexts.slot_mapping,
                not_found=_SlotTexts.not_found_component,
                slot_re=Slots.slot_re.parentheses,
            ),
            _SlotTexts.parentheses,
            _SlotTexts.mapped_split,
        ),
    ),
)
def test_slots(slots: Slots, text: str, expected: list[str] | None) -> None:
    result = slots.resolve_text(text)
    if expected is None:
        assert isinstance(result, tuple)
        assert len(result) == 1
        assert result[0] == text
    else:
        assert result == expected


@pytest.mark.anyio
async def test_snippet_with_text_processor_and_slots() -> None:
    slot_mapping = {
        "message": html.p("Hope you're having fun."),
        "signature": html.p("Cheers, htmy"),
    }
    snippet = Snippet(
        Text(_hello_world_format_snippet),
        Slots(slot_mapping),
        text_processor=message_to_slot_text_processor,
    )
    formatted_text = message_to_slot_text_processor(_hello_world_format_snippet, {})
    children = await snippet.htmy({})
    assert isinstance(children, tuple)
    assert children == (
        formatted_text[: formatted_text.index("before message slot ") + len("before message slot ")],
        slot_mapping["message"],
        " between slots ",
        slot_mapping["signature"],
        formatted_text[formatted_text.index(" after signature slot") :],
    )
    assert isinstance(children[0], SafeStr)
    assert isinstance(children[2], SafeStr)
    assert isinstance(children[4], SafeStr)

    rendered = await Renderer().render(snippet)
    assert rendered == _hello_world_format_snippet.format(
        message=(
            "before message slot "
            "<p >Hope you're having fun.</p>"
            " between slots "
            "<p >Cheers, htmy</p>"
            " after signature slot"
        )
    )
