"""本地化（i18n）公共模块。"""

from .catalog import DEFAULT_LOCALE, SUPPORTED_LOCALES, load_catalog, normalize_locale, translate

__all__ = [
    "DEFAULT_LOCALE",
    "SUPPORTED_LOCALES",
    "load_catalog",
    "normalize_locale",
    "translate",
]
