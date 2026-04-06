"""
Lightweight internationalization for Neural Speed Academy.

Uses a JSON catalog keyed by dot-separated identifiers.
English is the default and only language for v1.0.
Actual translations will be added in v1.1.

Usage::

    from neural_speed_academy.i18n import tr
    label = QLabel(tr("nav.back"))
    score = QLabel(tr("results.score", score=5, total=10))
"""
from __future__ import annotations

import json
import os
from pathlib import Path

_LOCALES_DIR = Path(__file__).parent / "locales"
_catalog: dict[str, str] = {}
_current_locale: str = "en"


def load_locale(locale: str = "en") -> None:
    """Load a locale catalog from the locales directory."""
    global _catalog, _current_locale
    path = _LOCALES_DIR / f"{locale}.json"
    if path.exists():
        with open(path, encoding="utf-8") as f:
            _catalog = json.load(f)
    _current_locale = locale


def current_locale() -> str:
    """Return the currently loaded locale code."""
    return _current_locale


def available_locales() -> dict[str, str]:
    """Return a dict of locale_code -> display_name for all available catalogs."""
    _LOCALE_NAMES = {
        "en": "English",
        "de": "Deutsch",
        "fr": "Français",
        "es": "Español",
        "it": "Italiano",
        "pt": "Português",
        "nl": "Nederlands",
        "ja": "日本語",
        "zh": "中文",
        "ko": "한국어",
    }
    locales = {}
    for f in sorted(_LOCALES_DIR.glob("*.json")):
        code = f.stem
        locales[code] = _LOCALE_NAMES.get(code, code)
    return locales


def tr(key: str, **kwargs) -> str:
    """Look up a translation by key, with optional format parameters.

    Falls back to the key itself if not found in the catalog,
    making incremental adoption safe.
    """
    text = _catalog.get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text


# Auto-load English on import
load_locale("en")
