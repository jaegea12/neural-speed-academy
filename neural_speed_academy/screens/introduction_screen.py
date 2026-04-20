"""
Introduction screen with science-backed training overview,
use cases, and exercise descriptions.
"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QApplication,
)
from PyQt6.QtCore import Qt

from neural_speed_academy.screens.base import BaseScreen, make_scroll_area
from neural_speed_academy.theme import COLORS, make_qfont, btn_css
from neural_speed_academy.i18n import tr


# Layout order: ("section", index) or ("fact", index)
# Content lives in locales/*.json under intro.section.N.title/body and intro.fact.N
_INTRO_ORDER = [
    ("section", 0),   # What is Neural Speed Academy?
    ("section", 1),   # Who is this for?
    ("fact", 0),
    ("section", 2),   # Perception — 5 exercises
    ("fact", 1),
    ("section", 3),   # Cognition — 5 exercises
    ("fact", 2),
    ("section", 4),   # Reading — 5 exercises
    ("fact", 3),
    ("section", 5),   # Eye warmup
    ("section", 6),   # Training paths
    ("section", 7),   # Tracking & analytics
    ("section", 8),   # Accessibility
    ("fact", 4),
    ("section", 9),   # Realistic expectations
    ("section", 10),  # Limitations
    ("fact", 5),
    ("section", 11),  # How to get the most out of your training
]


class IntroductionScreen(BaseScreen):

    def build(self, **kwargs) -> None:
        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")
        self.add_nav_bar()

        scroll, content, cl = make_scroll_area(self._layout)
        cl.setContentsMargins(60, 20, 60, 30)

        title_row = QHBoxLayout()
        title_row.addStretch()
        title = QLabel(tr("introduction.introduction"))
        title.setFont(make_qfont("header"))
        title.setStyleSheet(f"color: {c['accent']};")
        title_row.addWidget(title)

        copy_btn = QPushButton(tr("intro.copy_text"))
        copy_btn.setFont(make_qfont("btn_sm"))
        copy_btn.setStyleSheet(
            btn_css(c["card"], c["fg"], padding="4px 12px")
        )
        copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        copy_btn.setToolTip(tr("intro.copy_tooltip"))
        copy_btn.clicked.connect(lambda: self._copy_intro(copy_btn))
        title_row.addWidget(copy_btn)
        title_row.addStretch()
        cl.addLayout(title_row)
        cl.addSpacing(10)

        self._copy_btn_ref = copy_btn

        for entry_type, idx in _INTRO_ORDER:
            if entry_type == "section":
                sec = QLabel(tr(f"intro.section.{idx}.title"))
                sec.setFont(make_qfont("section_header"))
                sec.setStyleSheet(f"color: {c['fg']};")
                cl.addWidget(sec)
                cl.addSpacing(4)

                body = QLabel(tr(f"intro.section.{idx}.body"))
                body.setFont(make_qfont("body"))
                body.setStyleSheet(f"color: {c['fg']};")
                body.setWordWrap(True)
                cl.addWidget(body)
                cl.addSpacing(15)

            elif entry_type == "fact":
                card = QFrame()
                card.setStyleSheet(
                    f"background-color: {c['card']}; "
                    f"border-left: 3px solid {c['accent']}; "
                    f"border-radius: 4px; padding: 12px 16px;"
                )
                card_layout = QVBoxLayout(card)
                card_layout.setContentsMargins(0, 0, 0, 0)

                did_you_know = QLabel(tr("introduction.did_you_know"))
                did_you_know.setFont(make_qfont("btn_sm"))
                did_you_know.setStyleSheet(f"color: {c['accent']};")
                card_layout.addWidget(did_you_know)

                fact = QLabel(tr(f"intro.fact.{idx}"))
                fact.setFont(make_qfont("body"))
                fact.setStyleSheet(f"color: {c['text_on_card']};")
                fact.setWordWrap(True)
                card_layout.addWidget(fact)

                cl.addWidget(card)
                cl.addSpacing(15)

    def _copy_intro(self, btn: QPushButton) -> None:
        """Copy all introduction text to clipboard."""
        parts: list[str] = []
        for entry_type, idx in _INTRO_ORDER:
            if entry_type == "section":
                parts.append(tr(f"intro.section.{idx}.title"))
                parts.append(tr(f"intro.section.{idx}.body"))
                parts.append("")
            elif entry_type == "fact":
                parts.append(tr(f"intro.fact.{idx}"))
                parts.append("")

        clipboard = QApplication.clipboard()
        clipboard.setText("\n".join(parts))

        # Brief visual feedback
        original = btn.text()
        btn.setText("✅")
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(1500, lambda: btn.setText(original))
