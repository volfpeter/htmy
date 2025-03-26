from typing import Any

import pytest

from htmy import Formatter


@pytest.fixture
def formatter() -> Formatter:
    return Formatter()


@pytest.mark.parametrize(
    ("data", "formatted_value"),
    (
        ({}, "{}"),
        ([], "[]"),
        ((), "[]"),
        (set(), "[]"),
        (
            {"drink": "coffee", "food": "pizza", "bill": {"net": 100, "vat": 20, "total": 120}},
            '{"drink": "coffee", "food": "pizza", "bill": {"net": 100, "vat": 20, "total": 120}}',
        ),
        (["string", 3.14, {"key": "value"}], '["string", 3.14, {"key": "value"}]'),
        (("string", 3.14, {"key": "value"}), '["string", 3.14, {"key": "value"}]'),
        ({"c0ff33"}, '["c0ff33"]'),
    ),
)
def test_complex_value_formatting(data: Any, formatted_value: str, formatter: Formatter) -> None:
    assert formatter.format_value(data) == formatted_value


@pytest.mark.parametrize(
    ("data", "formatted_value"),
    (
        ({}, '"{}"'),
        ([], '"[]"'),
        ((), '"[]"'),
        (set(), '"[]"'),
        (
            {"drink": "coffee", "food": "pizza", "bill": {"net": 100, "vat": 20, "total": 120}},
            '\'{"drink": "coffee", "food": "pizza", "bill": {"net": 100, "vat": 20, "total": 120}}\'',
        ),
        (["string", 3.14, {"key": "value"}], '\'["string", 3.14, {"key": "value"}]\''),
        (("string", 3.14, {"key": "value"}), '\'["string", 3.14, {"key": "value"}]\''),
        ({"c0ff33"}, "'[\"c0ff33\"]'"),
    ),
)
def test_complex_property_formatting(data: Any, formatted_value: str, formatter: Formatter) -> None:
    assert formatter.format("property", data) == f"property={formatted_value}"
