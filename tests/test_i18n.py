"""i18n shared source and fallback behavior tests."""

from __future__ import annotations

from startups.i18n import catalog


def test_locale_keys_are_consistent() -> None:
    data = catalog.load_catalog()
    zh_keys = set(data["zh"].keys())
    en_keys = set(data["en"].keys())
    assert zh_keys == en_keys


def test_translate_fallback_locale() -> None:
    assert catalog.translate("en", "non_exist") == "non_exist"
    assert catalog.translate("xx", "title") == catalog.translate("zh", "title")


def test_translate_with_params() -> None:
    assert catalog.translate("zh", "insufficient_cash", cost=3) == "现金不足，需 3 金币"
