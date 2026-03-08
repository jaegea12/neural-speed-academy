"""
Pacer exercise for guided reading with configurable highlight modes.
Supports word, chunk, line, and multi-line pacing with a keyword quiz.
"""
from __future__ import annotations

import re

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QSlider, QRadioButton, QButtonGroup, QFrame, QMessageBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCursor, QTextCharFormat, QColor, QFont

from neural_speed_academy.exercises.base import BaseExercise, ExerciseResult
from neural_speed_academy.theme import COLORS, make_qfont, theme_manager
from neural_speed_academy.config import PACER_CONFIG, USER_DATA_CONFIG

_STOP_WORDS = frozenset(
    "the a an and or but in on at to for of is it that this with from by as "
    "are was were be been has have had do does did not no nor so if then than "
    "can will would could should may might shall its you your we our they them "
    "he she his her my me us who what when where how all each every some any "
    "also just about more most very much many such only other into over after "
    "before between through during without again further once here there which "
    "these those being both same own too up out off down".split()
)


def _extract_keywords(text: str, max_keywords: int = 8) -> list[str]:
    words = re.findall(r"[a-zA-Z]+", text.lower())
    freq: dict[str, int] = {}
    for w in words:
        if len(w) >= 4 and w not in _STOP_WORDS:
            freq[w] = freq.get(w, 0) + 1
    ranked = sorted(freq, key=lambda w: freq[w], reverse=True)
    return ranked[:max_keywords]


class PacerExercise(BaseExercise):

    MODES = {
        "word": "Single Word",
        "chunk": "Chunk (2-3 words)",
        "line": "Full Line",
    }

    def __init__(self, navigator, parent: QWidget | None = None):
        super().__init__(navigator, parent)
        self._source_text: str = ""
        self._words: list[str] = []
        self._steps: list[tuple[int, int]] = []
        self._step_idx: int = 0
        self._delay: int = 200

    @property
    def name(self) -> str:
        return "Pacer"

    def start(self, **kwargs) -> None:
        self._clear()
        self._running = True
        self.add_nav_bar()

        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")

        container = QWidget()
        container.setStyleSheet(f"background-color: {c['bg']};")
        cl = QVBoxLayout(container)
        cl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.setSpacing(8)

        guide_btn = QPushButton("GUIDE")
        guide_btn.setFont(make_qfont("btn_sm"))
        guide_btn.setStyleSheet(
            f"background-color: {c['accent']}; color: {c['btn_text']}; "
            f"border: none; padding: 4px 12px; border-radius: 3px;"
        )
        guide_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        guide_btn.clicked.connect(lambda: self.show_guide("pacer"))
        cl.addWidget(guide_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        title = QLabel("PACER CONFIGURATION")
        title.setFont(make_qfont("header"))
        title.setStyleSheet(f"color: {c['accent']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(title)

        # Text input
        self._text_input = QTextEdit()
        self._text_input.setFont(make_qfont("pacer_text"))
        self._text_input.setStyleSheet(
            f"QTextEdit {{ background-color: {c['card']}; color: {c['text_on_card']}; "
            f"border: none; padding: 8px; border-radius: 4px; }}"
        )
        self._text_input.setFixedHeight(150)
        self._text_input.setPlainText(theme_manager.training_text)
        cl.addWidget(self._text_input)

        # WPM slider
        wpm_lbl = QLabel("Target Speed (WPM):")
        wpm_lbl.setFont(make_qfont("slider_label"))
        wpm_lbl.setStyleSheet(f"color: {c['fg']};")
        cl.addWidget(wpm_lbl)

        self._wpm_display = QLabel(str(PACER_CONFIG["default_wpm"]))
        self._wpm_display.setFont(make_qfont("counter"))
        self._wpm_display.setStyleSheet(f"color: {c['accent']};")
        self._wpm_display.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._wpm_slider = QSlider(Qt.Orientation.Horizontal)
        self._wpm_slider.setRange(PACER_CONFIG["min_wpm"], PACER_CONFIG["max_wpm"])
        self._wpm_slider.setValue(PACER_CONFIG["default_wpm"])
        self._wpm_slider.setFixedWidth(400)
        self._wpm_slider.setStyleSheet(
            f"QSlider::groove:horizontal {{ background: {c['card']}; height: 6px; border-radius: 3px; }}"
            f"QSlider::handle:horizontal {{ background: {c['accent']}; width: 16px; margin: -5px 0; border-radius: 8px; }}"
        )
        self._wpm_slider.valueChanged.connect(
            lambda v: self._wpm_display.setText(str(v))
        )
        cl.addWidget(self._wpm_slider, alignment=Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(self._wpm_display)

        # Mode selector
        mode_lbl = QLabel("Highlight Mode:")
        mode_lbl.setFont(make_qfont("slider_label"))
        mode_lbl.setStyleSheet(f"color: {c['fg']};")
        cl.addWidget(mode_lbl)

        self._mode_group = QButtonGroup(self)
        mode_row = QHBoxLayout()
        for key, label in self.MODES.items():
            rb = QRadioButton(label)
            rb.setFont(make_qfont("btn"))
            rb.setStyleSheet(
                f"QRadioButton {{ color: {c['fg']}; background: transparent; spacing: 8px; }}"
            )
            rb.setProperty("mode_key", key)
            if key == "word":
                rb.setChecked(True)
            self._mode_group.addButton(rb)
            mode_row.addWidget(rb)
        cl.addLayout(mode_row)

        # Start button
        start_btn = QPushButton("START READING")
        start_btn.setFont(make_qfont("btn_lg"))
        start_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['success']}; color: {c['btn_text']}; "
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
        mode = "word"
        for btn in self._mode_group.buttons():
            if btn.isChecked():
                mode = btn.property("mode_key")
                break
        self._run_pacer(text, wpm, mode)

    def _run_pacer(self, text: str, wpm: int, mode: str) -> None:
        words = text.split()
        if not words:
            QMessageBox.information(self, "No Text", "Please enter some text before starting.")
            return

        self._source_text = text
        self._words = words

        # Build steps as (char_start, char_end) in the full text
        self._steps = self._build_steps(text, words, mode)
        self._step_idx = 0

        avg_words = len(words) / max(len(self._steps), 1)
        self._delay = int(60000 / wpm * avg_words)

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
        exit_btn.clicked.connect(self.navigator.finish_exercise)
        self._layout.addWidget(exit_btn, alignment=Qt.AlignmentFlag.AlignRight)

        # Progress
        self._lbl_progress = QLabel("0%")
        self._lbl_progress.setFont(make_qfont("section_header"))
        self._lbl_progress.setStyleSheet(f"color: {c['fg']};")
        self._lbl_progress.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(self._lbl_progress)

        # Reader page
        fov = theme_manager.fov_config
        page_w = fov["page_width"]
        font_size = fov["font_size"]

        self._reader = QTextEdit()
        reader_font = QFont("Georgia", font_size)
        self._reader.setFont(reader_font)
        self._reader.setStyleSheet(
            f"QTextEdit {{ background-color: {c['reader_bg']}; color: {c['reader_fg']}; "
            f"border: 1px solid {c['muted']}; padding: {fov['pad_y']}px {fov['pad_x']}px; }}"
        )
        self._reader.setFixedWidth(page_w)
        self._reader.setReadOnly(True)
        self._reader.setPlainText(" ".join(words))
        self._layout.addWidget(self._reader, 1, Qt.AlignmentFlag.AlignCenter)

        # Highlight format
        self._hl_fmt = QTextCharFormat()
        self._hl_fmt.setBackground(QColor(c["highlight"]))

        self._normal_fmt = QTextCharFormat()
        self._normal_fmt.setBackground(QColor(c["reader_bg"]))

        self._after(500, self._pacer_step)

    def _build_steps(self, text: str, words: list[str],
                     mode: str) -> list[tuple[int, int]]:
        full = " ".join(words)
        steps = []
        if mode == "word":
            pos = 0
            for w in words:
                steps.append((pos, pos + len(w)))
                pos += len(w) + 1
        elif mode == "chunk":
            chunk_size = 3
            pos = 0
            for i in range(0, len(words), chunk_size):
                chunk = " ".join(words[i:i + chunk_size])
                steps.append((pos, pos + len(chunk)))
                pos += len(chunk) + 1
        elif mode == "line":
            # Approximate line breaks at ~60 chars
            line_len = 60
            pos = 0
            while pos < len(full):
                end = min(pos + line_len, len(full))
                # Find word boundary
                if end < len(full):
                    space = full.rfind(" ", pos, end)
                    if space > pos:
                        end = space
                steps.append((pos, end))
                pos = end + 1 if end < len(full) else end
        return steps if steps else [(0, len(full))]

    def _pacer_step(self) -> None:
        if not self._running:
            return
        if self._step_idx >= len(self._steps):
            self._quiz_phase()
            return

        start, end = self._steps[self._step_idx]

        # Clear previous highlight
        cursor = self._reader.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.setCharFormat(self._normal_fmt)

        # Apply new highlight
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
        cursor.setCharFormat(self._hl_fmt)

        # Scroll to visible
        self._reader.setTextCursor(cursor)
        self._reader.ensureCursorVisible()

        pct = int(100 * self._step_idx / len(self._steps))
        self._lbl_progress.setText(f"PROGRESS: {pct}%")

        self._step_idx += 1
        self._after(self._delay, self._pacer_step)

    # ── Quiz phase ──

    def _quiz_phase(self) -> None:
        self._clear()
        self._running = True
        self.add_nav_bar()

        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")
        self._keywords = _extract_keywords(self._source_text)

        container = QWidget()
        container.setStyleSheet(f"background-color: {c['bg']};")
        cl = QVBoxLayout(container)
        cl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.setSpacing(8)

        title = QLabel("COMPREHENSION CHECK")
        title.setFont(make_qfont("header"))
        title.setStyleSheet(f"color: {c['accent']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(title)

        desc = QLabel("Summarize what you just read in your own words.")
        desc.setFont(make_qfont("body"))
        desc.setStyleSheet(f"color: {c['fg']};")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(desc)

        self._quiz_input = QTextEdit()
        self._quiz_input.setFont(make_qfont("pacer_text"))
        self._quiz_input.setStyleSheet(
            f"QTextEdit {{ background-color: {c['card']}; color: {c['text_on_card']}; "
            f"border: none; padding: 8px; border-radius: 4px; }}"
        )
        self._quiz_input.setFixedHeight(150)
        cl.addWidget(self._quiz_input)

        check_btn = QPushButton("CHECK")
        check_btn.setFont(make_qfont("btn_bold"))
        check_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['accent']}; color: {c['btn_text']}; "
            f"border: none; padding: 8px 30px; border-radius: 4px; }}"
        )
        check_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        check_btn.clicked.connect(self._score_quiz)
        cl.addWidget(check_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self._layout.addWidget(container, 1)
        self._quiz_input.setFocus()

    def _score_quiz(self) -> None:
        summary = self._quiz_input.toPlainText().lower()
        summary_words = set(re.findall(r"[a-zA-Z]+", summary))

        matched = [kw for kw in self._keywords if kw in summary_words]
        score = len(matched)
        total = len(self._keywords)

        xp = score * USER_DATA_CONFIG["xp_per_correct"]
        result = ExerciseResult(
            exercise_name="PACER", score=score, total=total, xp_gained=xp,
        )
        is_pb = self.complete(result)

        # Show results with keyword breakdown
        self._clear()
        self.add_nav_bar()

        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")

        container = QWidget()
        container.setStyleSheet(f"background-color: {c['bg']};")
        cl = QVBoxLayout(container)
        cl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.setSpacing(6)

        title = QLabel("RESULTS")
        title.setFont(make_qfont("header"))
        title.setStyleSheet(f"color: {c['accent']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(title)

        score_lbl = QLabel(f"Key concepts recalled: {score}/{total}")
        score_lbl.setFont(make_qfont("btn_lg"))
        score_lbl.setStyleSheet(f"color: {c['fg']};")
        score_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(score_lbl)

        xp_lbl = QLabel(f"XP earned: +{xp}")
        xp_lbl.setFont(make_qfont("counter"))
        xp_lbl.setStyleSheet(f"color: {c['accent']};")
        xp_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(xp_lbl)

        if is_pb:
            pb = QLabel("NEW PERSONAL BEST!")
            pb.setFont(make_qfont("btn_bold"))
            pb.setStyleSheet(f"color: {c['success']};")
            pb.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cl.addWidget(pb)

        # Keyword breakdown
        for kw in self._keywords:
            found = kw in summary_words
            color = c["success"] if found else c["alert"]
            marker = "\u2713" if found else "\u2717"
            lbl = QLabel(f"  {marker}  {kw}")
            lbl.setFont(make_qfont("body"))
            lbl.setStyleSheet(f"color: {color};")
            cl.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignCenter)

        cont_btn = QPushButton("CONTINUE")
        cont_btn.setFont(make_qfont("btn_bold"))
        cont_btn.setStyleSheet(
            f"background-color: {c['accent']}; color: {c['btn_text']}; "
            f"border: none; padding: 8px 40px; border-radius: 4px;"
        )
        cont_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cont_btn.clicked.connect(self.navigator.finish_exercise)
        cl.addWidget(cont_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self._layout.addWidget(container, 1)
