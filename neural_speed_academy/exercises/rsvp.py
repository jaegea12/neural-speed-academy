"""
RSVP (Rapid Serial Visual Presentation) exercise.
Flashes words from a passage one at a time at configurable WPM.
"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QSlider, QMessageBox,
)
from PyQt6.QtCore import Qt

from neural_speed_academy.exercises.base import BaseExercise, ExerciseResult
from neural_speed_academy.theme import COLORS, make_qfont, font_css, theme_manager
from neural_speed_academy.config import RSVP_CONFIG, USER_DATA_CONFIG


class RsvpExercise(BaseExercise):

    def __init__(self, navigator, parent: QWidget | None = None):
        super().__init__(navigator, parent)
        self.words: list = []
        self.word_idx: int = 0
        self.wpm: int = 300

    @property
    def name(self) -> str:
        return "RSVP"

    def start(self, **kwargs) -> None:
        self._clear()
        self._running = True
        self.add_nav_bar()

        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")

        slider_groove = (
            f"QSlider::groove:horizontal {{ background: {c['card']}; "
            f"height: 6px; border-radius: 3px; }}"
            f"QSlider::handle:horizontal {{ background: {c['accent']}; "
            f"width: 16px; margin: -5px 0; border-radius: 8px; }}"
        )

        container = QWidget()
        container.setStyleSheet(f"background-color: {c['bg']};")
        cl = QVBoxLayout(container)
        cl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.setContentsMargins(40, 5, 40, 5)
        cl.setSpacing(2)

        # Guide button
        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        guide_btn = QPushButton("GUIDE")
        guide_btn.setFont(make_qfont("btn_sm"))
        guide_btn.setStyleSheet(
            f"background-color: {c['accent']}; color: {c['btn_text']}; "
            f"border: none; padding: 4px 12px; border-radius: 3px;"
        )
        guide_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        guide_btn.clicked.connect(lambda: self.show_guide("rsvp"))
        top.addWidget(guide_btn)
        top.addStretch()
        cl.addLayout(top)

        title = QLabel("RSVP CONFIGURATION")
        title.setFont(make_qfont("section_header"))
        title.setStyleSheet(f"color: {c['accent']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(title)

        # Text input — 60% width, taller
        self._text_input = QTextEdit()
        self._text_input.setFont(make_qfont("pacer_text"))
        self._text_input.setStyleSheet(
            f"QTextEdit {{ background-color: {c['card']}; "
            f"color: {c['text_on_card']}; "
            f"border: none; padding: 8px; border-radius: 4px; }}"
        )
        self._text_input.setMinimumHeight(180)
        self._text_input.setMaximumWidth(960)
        self._text_input.setPlainText(theme_manager.training_text)
        cl.addWidget(self._text_input, 1, Qt.AlignmentFlag.AlignCenter)

        # WPM: label + slider + value in one row
        initial_wpm = kwargs.get("wpm", RSVP_CONFIG["default_wpm"])
        wpm_row = QHBoxLayout()
        wpm_row.setContentsMargins(0, 0, 0, 0)
        wpm_row.setSpacing(8)
        wpm_row.addStretch()
        wpm_lbl = QLabel("Target WPM:")
        wpm_lbl.setFont(make_qfont("slider_label"))
        wpm_lbl.setStyleSheet(f"color: {c['fg']};")
        wpm_row.addWidget(wpm_lbl)

        self._wpm_slider = QSlider(Qt.Orientation.Horizontal)
        self._wpm_slider.setRange(
            RSVP_CONFIG["min_wpm"], RSVP_CONFIG["max_wpm"]
        )
        self._wpm_slider.setValue(initial_wpm)
        self._wpm_slider.setFixedWidth(300)
        self._wpm_slider.setStyleSheet(slider_groove)

        self._wpm_display = QLabel(str(initial_wpm))
        self._wpm_display.setFont(make_qfont("counter"))
        self._wpm_display.setStyleSheet(f"color: {c['accent']};")
        self._wpm_display.setFixedWidth(50)
        self._wpm_slider.valueChanged.connect(
            lambda v: self._wpm_display.setText(str(v))
        )
        wpm_row.addWidget(self._wpm_slider)
        wpm_row.addWidget(self._wpm_display)
        wpm_row.addStretch()
        cl.addLayout(wpm_row)

        # Start button
        cl.addSpacing(4)
        start_btn = QPushButton("START RSVP")
        start_btn.setFont(make_qfont("btn_lg"))
        start_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['success']}; "
            f"color: {c['btn_text']}; "
            f"border: none; padding: 10px 40px; border-radius: 4px; }}"
        )
        start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        start_btn.clicked.connect(self._start_from_ui)
        cl.addWidget(start_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        hint = QLabel("Ctrl+Enter to start")
        hint.setFont(make_qfont("btn_sm"))
        hint.setStyleSheet(f"color: {c['muted']};")
        cl.addWidget(hint, alignment=Qt.AlignmentFlag.AlignCenter)

        self._layout.addWidget(container, 1)

    def _start_from_ui(self) -> None:
        text = self._text_input.toPlainText()
        wpm = self._wpm_slider.value()
        self._run_rsvp(text, wpm)

    def _run_rsvp(self, text: str, wpm: int) -> None:
        self.words = text.split()
        if not self.words:
            QMessageBox.information(self, "No Text", "Please enter some text before starting.")
            return

        self.wpm = wpm
        self.word_idx = 0
        self._delay = int(60000 / wpm)

        self._clear()
        self._running = True

        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")

        # Exit button
        exit_btn = QPushButton("\u2716")
        exit_btn.setFont(make_qfont("exit_btn"))
        exit_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['alert']}; color: {c['text_on_card']}; "
            f"border: none; padding: 4px 8px; border-radius: 3px; }}"
        )
        exit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        exit_btn.clicked.connect(self._stop)
        self._layout.addWidget(exit_btn, alignment=Qt.AlignmentFlag.AlignRight)

        # Progress
        self._lbl_progress = QLabel(f"0% | {wpm} WPM")
        self._lbl_progress.setFont(make_qfont("counter"))
        self._lbl_progress.setStyleSheet(f"color: {c['accent']};")
        self._lbl_progress.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(self._lbl_progress)

        # Word display
        self._lbl_word = QLabel("")
        self._lbl_word.setFont(make_qfont("rsvp"))
        self._lbl_word.setStyleSheet(f"color: {c['fg']};")
        self._lbl_word.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(self._lbl_word, 1)

        self._after(500, self._flash_word)

    def _flash_word(self) -> None:
        if not self._running:
            return
        if self.word_idx >= len(self.words):
            self._complete_exercise()
            return

        self._lbl_word.setText(self.words[self.word_idx])
        self.word_idx += 1
        pct = int(self.word_idx / len(self.words) * 100)
        self._lbl_progress.setText(f"{pct}% | {self.wpm} WPM")
        self._after(self._delay, self._flash_word)

    def _stop(self) -> None:
        self._running = False
        self.navigator.finish_exercise()

    def _complete_exercise(self) -> None:
        self._running = False
        word_count = len(self.words)
        xp = word_count // 10
        result = ExerciseResult(
            exercise_name="RSVP",
            score=word_count,
            total=word_count,
            xp_gained=xp,
        )
        is_pb = self.complete(result)
        self.show_result_screen(
            result, is_personal_best=is_pb,
            details=f"Read {word_count} words at {self.wpm} WPM",
        )
