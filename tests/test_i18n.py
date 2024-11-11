from typing import Any

import pytest

from htmy.i18n import I18n, I18nKeyError, I18nValueError

from .utils import tests_root


class TranslationFile:
    overview_page = "page.overview"
    welcome_page = "page.welcome"
    does_not_exist = "does.not.exist"


hu_no_fallback = I18n(tests_root / "data" / "locale" / "hu")
"""I18n instance with no fallback."""

hu_with_en_fallback = I18n(
    tests_root / "data" / "locale" / "hu",  # Take translations from locale/hu by default.
    tests_root / "data" / "locale" / "en",  # Use locale/en as fallback.
)
"""I18n instance that can be used for fallback testing."""


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("dotted_path", "key", "kwargs", "expected"),
    (
        (
            TranslationFile.welcome_page,
            "title",
            {},
            "Helló {name}",  # Translated
        ),
        (
            TranslationFile.welcome_page,
            "title",
            {"name": "Joe"},
            "Helló Joe",  # Translated
        ),
        (
            TranslationFile.welcome_page,
            "message",
            {},
            "Welcome back.",  # en fallback
        ),
        (
            TranslationFile.welcome_page,
            "",
            {},
            {"title": "Helló {name}"},  # Root, return dict
        ),
        (
            TranslationFile.welcome_page,
            ".",
            {"name": "Joe"},
            {"title": "Helló {name}"},  # Root, return dict
        ),
        (TranslationFile.overview_page, "title", {}, "Overview"),
        (TranslationFile.overview_page, "", {}, {"title": "Overview"}),
    ),
)
async def test_i18n_with_fallback(
    dotted_path: str, key: str, kwargs: dict[str, Any], expected: Any
) -> None:
    result = await hu_with_en_fallback.get(dotted_path, key, **kwargs)
    assert result == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("dotted_path", "key", "error"),
    (
        # No fallback, but key would exist in fallback.
        (TranslationFile.welcome_page, "message", I18nKeyError),
        # Key doesn't exist.
        (TranslationFile.welcome_page, "some-key", I18nKeyError),
        # File does not exist.
        (TranslationFile.does_not_exist, "title", I18nValueError),
    ),
)
async def test_i18n_missing_resource(dotted_path: str, key: str, error: type[Exception]) -> None:
    with pytest.raises(error):
        await hu_no_fallback.get(dotted_path, key)
