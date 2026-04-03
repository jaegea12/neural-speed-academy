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
from PyQt6.QtGui import QKeySequence, QShortcut

from neural_speed_academy.exercises.base import BaseExercise, ExerciseResult
from neural_speed_academy.theme import COLORS, make_qfont, font_css, input_css, theme_manager, screen_metrics, btn_css
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
        self.add_nav_bar(show_stop=False)

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
        cl.setContentsMargins(40, 10, 40, 10)
        cl.setSpacing(6)

        # Guide button
        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        guide_btn = QPushButton("GUIDE")
        guide_btn.setFont(make_qfont("btn_sm"))
        guide_btn.setStyleSheet(
            f"background-color: {c['accent']}; color: {c['btn_text']}; "
            f"border: 2px solid transparent; padding: 4px 12px; border-radius: 3px;"
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

        # Text input — 60% screen width, 15 lines visible
        self._text_input = QTextEdit()
        self._text_input.setFont(make_qfont("pacer_text"))
        self._text_input.setStyleSheet(input_css(widget="QTextEdit"))
        fm = self._text_input.fontMetrics()
        line_h = fm.lineSpacing()
        self._text_input.setFixedHeight(line_h * 15 + 20)
        self._text_input.setFixedWidth(screen_metrics.text_input_w)
        self._text_input.setPlainText(theme_manager.training_text)
        cl.addWidget(self._text_input, 0, Qt.AlignmentFlag.AlignCenter)

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
            f"border: 2px solid transparent; padding: 10px 40px; border-radius: 4px; }}"
        )
        start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        start_btn.clicked.connect(self._start_from_ui)
        cl.addWidget(start_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        hint = QLabel("Ctrl+Enter to start")
        hint.setFont(make_qfont("btn_sm"))
        hint.setStyleSheet(f"color: {c['muted']};")
        cl.addWidget(hint, alignment=Qt.AlignmentFlag.AlignCenter)

        shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        shortcut.activated.connect(self._start_from_ui)

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
        exit_btn.setAccessibleName("Close")
        exit_btn.setToolTip("Close")
        exit_btn.setFont(make_qfont("exit_btn"))
        exit_btn.setStyleSheet(
            btn_css(c["alert"], c["text_on_card"], padding="4px 8px",
                    radius=3, font_key="exit_btn")
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
        self._source_text = " ".join(self.words)
        self._word_count = len(self.words)
        self._quiz_phase()

    def _quiz_phase(self) -> None:
        from neural_speed_academy.exercises.recall import (
            build_recall_screen,
        )
        self._clear()
        self.add_nav_bar()
        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")
        build_recall_screen(
            self, self._layout, self._source_text,
            on_scored=self._on_recall_scored,
            exercise_label="RSVP — COMPREHENSION CHECK",
        )

    def _on_recall_scored(self, score, total, matches, keywords) -> None:
        from neural_speed_academy.exercises.recall import build_recall_results
        self._clear()
        self.add_nav_bar(show_stop=False)
        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")

        int_score = int(score) if score == int(score) else round(score, 1)
        comprehension_pct = round(score / total * 100) if total > 0 else 0
        xp = self._word_count // 10 + int(score) * USER_DATA_CONFIG["xp_per_correct"]
        result = ExerciseResult(
            exercise_name="RSVP",
            score=int_score,
            total=total,
            xp_gained=xp,
            metadata={
                "wpm": self.wpm,
                "word_count": self._word_count,
                "comprehension_score": int_score,
                "comprehension_total": total,
                "comprehension_pct": comprehension_pct,
            },
        )
        is_pb = self.complete(result)

        cl = build_recall_results(
            self._layout, score, total, matches, keywords,
        )

        cl.addSpacing(10)
        details = QLabel(
            f"Read {self._word_count} words at {self.wpm} WPM"
        )
        details.setFont(make_qfont("body"))
        details.setStyleSheet(f"color: {c['fg']};")
        details.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(details)

        if is_pb:
            pb = QLabel("NEW PERSONAL BEST!")
            pb.setFont(make_qfont("btn_bold"))
            pb.setStyleSheet(f"color: {c['highlight']};")
            pb.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cl.addWidget(pb)

        cl.addSpacing(10)
        cont_btn = QPushButton("CONTINUE")
        cont_btn.setFont(make_qfont("btn_bold"))
        cont_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['accent']}; color: {c['btn_text']}; "
            f"border: 2px solid transparent; padding: 8px 40px; border-radius: 4px; }}"
        )
        cont_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cont_btn.clicked.connect(self.navigator.finish_exercise)
        cl.addWidget(cont_btn, alignment=Qt.AlignmentFlag.AlignCenter)
