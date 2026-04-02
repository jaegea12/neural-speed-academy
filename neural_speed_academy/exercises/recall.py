"""
Shared comprehension recall system for text-based exercises.

Extracts keywords from source text, presents a recall prompt,
scores the user's summary, and displays results with keyword breakdown.
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


def extract_keywords(text: str, max_keywords: int = 8) -> list[str]:
    """Extract key content words from text by frequency.

    Filters stop words, requires minimum length of 4 characters,
    and weights words appearing in the first 25% of text higher
    (topic words tend to appear early).
    """
    words = re.findall(r"[a-zA-Z]+", text.lower())
    if not words:
        return []

    freq: dict[str, float] = {}
    quarter = max(len(words) // 4, 1)

    for i, w in enumerate(words):
        if len(w) >= 4 and w not in _STOP_WORDS:
            # Words in the first quarter get a 1.5x weight
            weight = 1.5 if i < quarter else 1.0
            freq[w] = freq.get(w, 0) + weight

    ranked = sorted(freq, key=lambda w: freq[w], reverse=True)
    return ranked[:max_keywords]


def build_recall_screen(
    parent: QWidget,
    layout: QVBoxLayout,
    source_text: str,
    on_scored: Callable[[int, int, list[str], list[str]], None],
    exercise_label: str = "COMPREHENSION CHECK",
) -> None:
    """Build the recall quiz UI into the given layout.

    Args:
        parent: Parent widget (the exercise screen).
        layout: Layout to add widgets to.
        source_text: The text the user just read.
        on_scored: Callback(score, total, matched, all_keywords) after scoring.
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
        summary = quiz_input.toPlainText().lower()
        summary_words = set(re.findall(r"[a-zA-Z]+", summary))
        matched = [kw for kw in keywords if kw in summary_words]
        on_scored(len(matched), len(keywords), matched, keywords)

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
    skip_btn.clicked.connect(lambda: on_scored(0, len(keywords), [], keywords))
    cl.addWidget(skip_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    layout.addWidget(container, 1)
    quiz_input.setFocus()


def build_recall_results(
    layout: QVBoxLayout,
    score: int,
    total: int,
    matched: list[str],
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

    score_lbl = QLabel(f"Key concepts recalled: {score}/{total}")
    score_lbl.setFont(make_qfont("header"))
    color = c["success"] if score >= total * 0.6 else c["alert"]
    score_lbl.setStyleSheet(f"color: {color};")
    score_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    cl.addWidget(score_lbl)

    cl.addSpacing(10)

    # Keyword breakdown
    for kw in keywords:
        found = kw in matched
        icon = "\u2714" if found else "\u2718"
        color_kw = c["success"] if found else c["muted"]
        lbl = QLabel(f"  {icon}  {kw}")
        lbl.setFont(make_qfont("body"))
        lbl.setStyleSheet(f"color: {color_kw};")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(lbl)

    layout.addWidget(container, 1)
    return cl
