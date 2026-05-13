"""Localization loader used by CLI and tests."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

_LOCALE_CANDIDATES = (
    Path(__file__).resolve().parents[1] / "locales" / "startups_i18n.json",
    Path(__file__).resolve().parents[2] / "locales" / "startups_i18n.json",
    Path(__file__).resolve().parents[3] / "src" / "startups" / "locales" / "startups_i18n.json",
)

DEFAULT_LOCALE = "zh"
FALLBACK_LOCALE = "zh"
SUPPORTED_LOCALES = {"zh", "en"}
_CACHE: dict[str, dict[str, str]] | None = None


def _read_catalog() -> dict[str, dict[str, str]]:
    for candidate in _LOCALE_CANDIDATES:
        if candidate.exists():
            with candidate.open("r", encoding="utf-8") as handle:
                data: dict[str, dict[str, str]] = json.load(handle)
            if DEFAULT_LOCALE in data:
                return data
            break
    raise RuntimeError("Failed to load i18n catalog.")


def load_catalog() -> dict[str, dict[str, str]]:
    """Load locale catalog once and cache in memory."""

    global _CACHE
    if _CACHE is None:
        _CACHE = _read_catalog()
    return _CACHE


def normalize_locale(locale: str) -> str:
    if locale in SUPPORTED_LOCALES:
        return locale
    return FALLBACK_LOCALE


_template_re = re.compile(r"{(\w+)}")


def translate(locale: str, key: str, **params: Any) -> str:
    """Return translated text and expand `{name}` style placeholders."""

    catalog = load_catalog()
    normalized = normalize_locale(locale)
    templates = catalog.get(normalized, {})
    template = templates.get(key)
    if template is None:
        template = catalog.get(FALLBACK_LOCALE, {}).get(key, key)
    mapping: dict[str, Any] = dict(params)
    return _template_re.sub(lambda match: str(mapping.get(match.group(1), match.group(0))), template)

