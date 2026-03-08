"""
Introduction screen with speed reading science and training overview.
"""
from __future__ import annotations

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt

from neural_speed_academy.screens.base import BaseScreen, make_scroll_area
from neural_speed_academy.theme import COLORS, make_qfont


INTRO_TEXT = (
    "WHAT IS SPEED READING?\n\n"
    "Speed reading is not skimming. It is the systematic training of visual "
    "and cognitive skills that remove inefficiencies from the reading process. "
    "An average reader processes 200-250 words per minute (WPM). Trained "
    "readers consistently reach 400-600 WPM with equal or better comprehension.\n\n"

    "THE FOUR BOTTLENECKS\n\n"
    "1. TOO MANY FIXATIONS \u2014 Your eyes don't glide across text. They jump "
    "(saccade) and pause (fixate) 3-4 times per line. Each fixation processes "
    "only 1-2 words. Training: Eye-Span and Chunking exercises widen your "
    "perceptual span so each fixation covers more words.\n\n"
    "2. REGRESSION \u2014 10-15% of eye movements go backward to re-read text "
    "you already passed. This is the single largest waste of reading time. "
    "Training: Pacer exercises suppress regression by forcing forward momentum.\n\n"
    "3. SUBVOCALIZATION \u2014 The inner voice that 'reads aloud' in your head "
    "limits you to speaking speed (~150 WPM). Training: Flash and RSVP "
    "exercises present text faster than speech, forcing direct visual-to-meaning "
    "processing.\n\n"
    "4. NARROW ATTENTION \u2014 Untrained readers focus on one word at a time. "
    "Training: Schulte grids and Eye-Span exercises expand peripheral awareness "
    "so you process more of the visual field simultaneously.\n\n"

    "THE EXERCISES\n\n"
    "\u2022 Flash Perception \u2014 Trains iconic memory and rapid digit/word recognition\n"
    "\u2022 Eye-Span \u2014 Widens the perceptual span for fewer fixations per line\n"
    "\u2022 Schulte Grid \u2014 Expands peripheral awareness without moving the eyes\n"
    "\u2022 Eye Priming \u2014 Warms up extraocular muscles before training\n"
    "\u2022 Pacer \u2014 Guided reading that eliminates regression\n"
    "\u2022 RSVP \u2014 Single-word flash that breaks the subvocalization barrier\n"
    "\u2022 Chunking \u2014 Phrase-level reading for block processing\n\n"

    "REALISTIC EXPECTATIONS\n\n"
    "Research supports that consistent training (15-20 min/day, 4-5 days/week) "
    "produces measurable gains within 2-4 weeks. Most people can double their "
    "reading speed while maintaining comprehension. Claims of 1000+ WPM with "
    "full comprehension are not supported by peer-reviewed research."
)


class IntroductionScreen(BaseScreen):

    def build(self, **kwargs) -> None:
        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")
        self.add_nav_bar()

        scroll, content, cl = make_scroll_area(self._layout)
        cl.setContentsMargins(40, 20, 40, 30)

        title = QLabel("INTRODUCTION TO SPEED READING")
        title.setFont(make_qfont("header"))
        title.setStyleSheet(f"color: {c['accent']};")
        cl.addWidget(title)

        body = QLabel(INTRO_TEXT)
        body.setFont(make_qfont("body"))
        body.setStyleSheet(f"color: {c['fg']};")
        body.setWordWrap(True)
        cl.addWidget(body)

        back_btn = QPushButton("\u2190 BACK TO MENU")
        back_btn.setFont(make_qfont("btn_bold"))
        back_btn.setStyleSheet(
            f"background-color: {c['accent']}; color: {c['btn_text']}; "
            f"border: none; padding: 8px 30px; border-radius: 4px;"
        )
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(
            lambda: self.navigator.navigate_to("main_menu")
        )
        cl.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignCenter)
