"""Locale-aware slide library loader.

Each ``slides_{lang}.py`` exports a ``SLIDE_LIBRARY`` dict with the same
structure: ``{category: [(title, [bullets], [(question, [choices], answer_idx)])]}``.

``get_slide_library()`` returns the library for the active locale,
falling back to English when a translation is unavailable.
"""
from __future__ import annotations


def get_slide_library() -> dict:
    """Return the slide library matching the current locale."""
    from neural_speed_academy.i18n import current_locale

    locale = current_locale()
    try:
        mod = __import__(
            f"neural_speed_academy.slides.slides_{locale}",
            fromlist=["SLIDE_LIBRARY"],
        )
        return mod.SLIDE_LIBRARY
    except (ImportError, AttributeError):
        from neural_speed_academy.slides.slides_en import SLIDE_LIBRARY
        return SLIDE_LIBRARY
