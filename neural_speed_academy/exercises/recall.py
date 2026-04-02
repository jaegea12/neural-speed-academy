"""
Shared comprehension recall system for text-based exercises.

Extracts keywords from source text using lightweight stemming,
scores the user's summary with stem-aware matching and partial credit,
and displays results with keyword breakdown.
"""
from __future__ import annotations

import re
from typing import Callable

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QFrame,
)
from PyQt6.QtCore import Qt

from neural_speed_academy.theme import COLORS, make_qfont, input_css, screen_metrics

_STOP_WORDS = frozenset(
    "the a an and or but in on at to for of is it that this with from by as "
    "are was were be been has have had do does did not no nor so if then than "
    "can will would could should may might shall its you your we our they them "
    "he she his her my me us who what when where how all each every some any "
    "also just about more most very much many such only other into over after "
    "before between through during without again further once here there which "
    "these those being both same own too up out off down".split()
)

# Common English suffixes for lightweight stemming (no external deps)
_SUFFIX_RULES: list[tuple[str, str]] = [
    ("ational", "ate"),
    ("tional", "tion"),
    ("encies", "ence"),
    ("ancies", "ance"),
    ("izers", "ize"),
    ("ising", "ise"),
    ("izing", "ize"),
    ("ating", "ate"),
    ("ities", "ity"),
    ("ously", "ous"),
    ("ively", "ive"),
    ("fully", "ful"),
    ("ments", "ment"),
    ("ness", ""),
    ("ment", ""),
    ("able", ""),
    ("ible", ""),
    ("tion", ""),
    ("sion", ""),
    ("ally", ""),
    ("ence", ""),
    ("ance", ""),
    ("ious", ""),
    ("eous", ""),
    ("ling", ""),
    ("ings", ""),
    ("ful", ""),
    ("ous", ""),
    ("ive", ""),
    ("ing", ""),
    ("ies", "y"),
    ("ied", "y"),
    ("ier", "y"),
    ("ers", ""),
    ("est", ""),
    ("ism", ""),
    ("ist", ""),
    ("ity", ""),
    ("ize", ""),
    ("ise", ""),
    ("ate", ""),
    ("ent", ""),
    ("ant", ""),
    ("ed", ""),
    ("er", ""),
    ("ly", ""),
    ("es", ""),
    ("al", ""),
    ("en", ""),
    ("s", ""),
]


def _stem(word: str) -> str:
    """Lightweight English stemmer — reduce a word to an approximate root.

    Not as thorough as Porter/Snowball but requires no external libraries
    and handles the most common inflections well enough for recall scoring.
    """
    if len(word) <= 4:
        return word
    for suffix, replacement in _SUFFIX_RULES:
        if word.endswith(suffix):
            base = word[: -len(suffix)]
            candidate = base + replacement
            # The base (before suffix) must be at least 4 chars to avoid
            # false stems like "speed" -> "spe" (where "ed" isn't a suffix)
            if len(base) >= 4 and len(candidate) >= 3:
                return candidate
    return word


def extract_keywords(text: str, max_keywords: int = 8) -> list[str]:
    """Extract key content words from text by frequency.

    Uses stemming to group inflected forms, then picks the most common
    surface form for each stem group. Words in the first 25% of text
    get a 1.5x weight (topic words tend to appear early).
    """
    words = re.findall(r"[a-zA-Z]+", text.lower())
    if not words:
        return []

    quarter = max(len(words) // 4, 1)

    # stem -> {surface_form -> weighted_count}
    stem_groups: dict[str, dict[str, float]] = {}

    for i, w in enumerate(words):
        if len(w) < 4 or w in _STOP_WORDS:
            continue
        weight = 1.5 if i < quarter else 1.0
        s = _stem(w)
        if s not in stem_groups:
            stem_groups[s] = {}
        stem_groups[s][w] = stem_groups[s].get(w, 0) + weight

    # For each stem group, total weight and pick the most common surface form
    ranked: list[tuple[float, str]] = []
    for s, forms in stem_groups.items():
        total_weight = sum(forms.values())
        best_form = max(forms, key=lambda f: forms[f])
        ranked.append((total_weight, best_form))

    ranked.sort(key=lambda x: x[0], reverse=True)
    return [form for _, form in ranked[:max_keywords]]


def _get_stems(words: set[str]) -> dict[str, set[str]]:
    """Build a stem -> surface-forms mapping for a set of words."""
    stems: dict[str, set[str]] = {}
    for w in words:
        s = _stem(w)
        if s not in stems:
            stems[s] = set()
        stems[s].add(w)
    return stems


def score_recall(
    keywords: list[str],
    summary_text: str,
) -> tuple[float, int, list[tuple[str, str]]]:
    """Score a recall summary against extracted keywords.

    Uses stem-aware matching: if the user writes "running" and the keyword
    is "run", it counts as a match. Also detects substring containment
    for compound words (e.g., "speedreading" matches "speed").

    Returns:
        (score, total, matches) where matches is a list of
        (keyword, match_type) pairs. match_type is "exact", "stem",
        "partial", or "miss".
    """
    summary_words = set(re.findall(r"[a-zA-Z]+", summary_text.lower()))
    summary_stems = _get_stems(summary_words)

    matches: list[tuple[str, str]] = []
    score = 0.0

    for kw in keywords:
        kw_stem = _stem(kw)

        # 1. Exact match
        if kw in summary_words:
            matches.append((kw, "exact"))
            score += 1.0
            continue

        # 2. Stem match (e.g., "running" matches keyword "run")
        if kw_stem in summary_stems:
            matches.append((kw, "stem"))
            score += 1.0
            continue

        # 3. Partial/substring match for compound words or longer keywords
        partial = False
        if len(kw) >= 5:
            for sw in summary_words:
                if len(sw) >= 5 and (kw in sw or sw in kw):
                    matches.append((kw, "partial"))
                    score += 0.5
                    partial = True
                    break
        if not partial:
            matches.append((kw, "miss"))

    return score, len(keywords), matches


def build_recall_screen(
    parent: QWidget,
    layout: QVBoxLayout,
    source_text: str,
    on_scored: Callable[[float, int, list[tuple[str, str]], list[str]], None],
    exercise_label: str = "COMPREHENSION CHECK",
) -> None:
    """Build the recall quiz UI into the given layout.

    Args:
        parent: Parent widget (the exercise screen).
        layout: Layout to add widgets to.
        source_text: The text the user just read.
        on_scored: Callback(score, total, matches, all_keywords) after scoring.
            matches is a list of (keyword, match_type) tuples.
        exercise_label: Title shown above the prompt.
    """
    c = COLORS
    keywords = extract_keywords(source_text)

    container = QWidget()
    container.setStyleSheet(f"background-color: {c['bg']};")
    cl = QVBoxLayout(container)
    cl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    cl.setSpacing(8)

    title = QLabel(exercise_label)
    title.setFont(make_qfont("header"))
    title.setStyleSheet(f"color: {c['accent']};")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    cl.addWidget(title)

    desc = QLabel("Summarize what you just read in your own words.")
    desc.setFont(make_qfont("body"))
    desc.setStyleSheet(f"color: {c['fg']};")
    desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
    cl.addWidget(desc)

    quiz_input = QTextEdit()
    quiz_input.setFont(make_qfont("pacer_text"))
    quiz_input.setStyleSheet(input_css(widget="QTextEdit"))
    quiz_input.setFixedHeight(150)
    quiz_input.setMaximumWidth(screen_metrics.text_input_w)
    cl.addWidget(quiz_input, alignment=Qt.AlignmentFlag.AlignCenter)

    def _score():
        summary = quiz_input.toPlainText()
        score, total, matches = score_recall(keywords, summary)
        on_scored(score, total, matches, keywords)

    check_btn = QPushButton("CHECK")
    check_btn.setFont(make_qfont("btn_bold"))
    check_btn.setStyleSheet(
        f"QPushButton {{ background-color: {c['accent']}; color: {c['btn_text']}; "
        f"border: none; padding: 8px 30px; border-radius: 4px; }}"
    )
    check_btn.setCursor(Qt.CursorShape.PointingHandCursor)
    check_btn.clicked.connect(_score)
    cl.addWidget(check_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    skip_btn = QPushButton("SKIP")
    skip_btn.setFont(make_qfont("btn_sm"))
    skip_btn.setStyleSheet(
        f"QPushButton {{ background-color: {c['card']}; color: {c['fg']}; "
        f"border: none; padding: 6px 20px; border-radius: 4px; }}"
        f"QPushButton:hover {{ background-color: {c['bg']}; }}"
    )
    skip_btn.setCursor(Qt.CursorShape.PointingHandCursor)
    skip_btn.clicked.connect(
        lambda: on_scored(0, len(keywords), [(kw, "miss") for kw in keywords], keywords)
    )
    cl.addWidget(skip_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    layout.addWidget(container, 1)
    quiz_input.setFocus()


def build_recall_results(
    layout: QVBoxLayout,
    score: float,
    total: int,
    matches: list[tuple[str, str]],
    keywords: list[str],
) -> QVBoxLayout:
    """Build the keyword breakdown results into the given layout.

    Returns the layout for further additions (e.g., Continue button).
    """
    c = COLORS

    container = QWidget()
    container.setStyleSheet(f"background-color: {c['bg']};")
    cl = QVBoxLayout(container)
    cl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    cl.setSpacing(6)

    int_score = int(score) if score == int(score) else round(score, 1)
    score_lbl = QLabel(f"Key concepts recalled: {int_score}/{total}")
    score_lbl.setFont(make_qfont("header"))
    color = c["success"] if score >= total * 0.6 else c["alert"]
    score_lbl.setStyleSheet(f"color: {color};")
    score_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    cl.addWidget(score_lbl)

    pct = round(score / total * 100) if total > 0 else 0
    pct_lbl = QLabel(f"Comprehension: {pct}%")
    pct_lbl.setFont(make_qfont("counter"))
    pct_lbl.setStyleSheet(f"color: {c['accent']};")
    pct_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    cl.addWidget(pct_lbl)

    cl.addSpacing(10)

    # Keyword breakdown with match type indicators
    _match_icons = {
        "exact": ("\u2714", "success"),
        "stem": ("\u2714", "success"),
        "partial": ("\u25d0", "accent"),
        "miss": ("\u2718", "muted"),
    }
    _match_labels = {
        "exact": "",
        "stem": " (stem match)",
        "partial": " (partial)",
        "miss": "",
    }

    for kw, match_type in matches:
        icon, color_key = _match_icons.get(match_type, ("\u2718", "muted"))
        suffix = _match_labels.get(match_type, "")
        color_kw = c[color_key]
        lbl = QLabel(f"  {icon}  {kw}{suffix}")
        lbl.setFont(make_qfont("body"))
        lbl.setStyleSheet(f"color: {color_kw};")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(lbl)

    layout.addWidget(container, 1)
    return cl
