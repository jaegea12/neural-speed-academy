"""
Flash perception exercises: numbers, words, and eye-span.
"""
from __future__ import annotations

import random
from typing import Callable, Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
)
from PyQt6.QtCore import Qt

from neural_speed_academy.exercises.base import BaseExercise, ExerciseResult
from neural_speed_academy.theme import COLORS, make_qfont
from neural_speed_academy.config import WORD_PAIRS, USER_DATA_CONFIG, FLASH_TIMING


class FlashExercise(BaseExercise):

    def __init__(self, navigator, parent: QWidget | None = None):
        super().__init__(navigator, parent)
        self.mode: str = ""
        self.rounds_total: int = 0
        self.current_round: int = 0
        self.correct_count: int = 0
        self.target_val: str = ""
        self.level_logic: Optional[Callable] = None
        self.span_config: dict = {}
        self.word_pairs = WORD_PAIRS

    @property
    def name(self) -> str:
        return "Flash Perception"

    def start(self, mode: str, rounds: int, level_func: Callable,
              span_config: dict = None, **kwargs) -> None:
        self.mode = mode
        self.rounds_total = rounds
        self.current_round = 0
        self.correct_count = 0
        self.level_logic = level_func
        self.span_config = span_config or {}
        self._next_round()

    def _next_round(self) -> None:
        if self.current_round >= self.rounds_total:
            self._complete_exercise()
            return

        self._clear()
        self._running = True
        self.add_nav_bar()
        self.current_round += 1

        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")

        # Counter
        cnt = QLabel(
            f"ROUND: {self.current_round}/{self.rounds_total}   |   "
            f"CORRECT: {self.correct_count}"
        )
        cnt.setFont(make_qfont("counter"))
        cnt.setStyleSheet(f"color: {c['accent']};")
        cnt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(cnt)

        # Central area for flash content
        self._flash_area = QWidget()
        self._flash_area.setStyleSheet(f"background-color: {c['bg']};")
        self._flash_layout = QVBoxLayout(self._flash_area)
        self._flash_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(self._flash_area, 1)

        # Show cross
        self._cross = QLabel("+")
        self._cross.setFont(make_qfont("cross"))
        self._cross.setStyleSheet(f"color: {c['cross']};")
        self._cross.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._flash_layout.addWidget(self._cross)

        # Prepare content
        self._prepare_content()

        # Sequence: Cross -> Dots -> Flash
        self._after(FLASH_TIMING["cross_duration"], self._show_pre_flash_dots)

    def _prepare_content(self) -> None:
        if self.mode == "flash_num":
            d = self.level_logic(self.current_round)
            self.target_val = str(random.randint(10 ** (d - 1), (10 ** d) - 1))
        elif self.mode == "flash_word":
            self.target_val = random.choice(random.choice(self.word_pairs))
        elif self.mode == "eyespan":
            d = self.level_logic(self.current_round)
            low, high = 10 ** (d - 1), (10 ** d) - 1
            n1 = str(random.randint(low, high))
            n2 = str(random.randint(low, high))
            self.target_val = f"{n1} {n2}"
            self._eyespan_left = n1
            self._eyespan_right = n2

    def _show_pre_flash_dots(self) -> None:
        if not self._running:
            return
        c = COLORS
        self._cross.setText("\u2022\u2022")
        self._cross.setStyleSheet(f"color: {c['accent']};")
        self._after(FLASH_TIMING["dots_duration"], self._do_flash)

    def _do_flash(self) -> None:
        if not self._running:
            return
        c = COLORS
        self._cross.setVisible(False)

        font_key = "rsvp" if self.mode == "flash_word" else "flash"

        if self.mode == "eyespan":
            row = QHBoxLayout()
            row.setAlignment(Qt.AlignmentFlag.AlignCenter)

            span_mode = self.span_config.get("mode", "h")
            if span_mode == "m":
                span_mode = random.choice(["h", "v"])

            width_pct = self.span_config.get("width", 50)
            spacing = int(width_pct * 4)

            self._lbl_left = QLabel(self._eyespan_left)
            self._lbl_left.setFont(make_qfont(font_key))
            self._lbl_left.setStyleSheet(f"color: {c['fg']};")
            self._lbl_left.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self._lbl_right = QLabel(self._eyespan_right)
            self._lbl_right.setFont(make_qfont(font_key))
            self._lbl_right.setStyleSheet(f"color: {c['fg']};")
            self._lbl_right.setAlignment(Qt.AlignmentFlag.AlignCenter)

            if span_mode == "h":
                row.addSpacing(spacing)
                row.addWidget(self._lbl_left)
                row.addSpacing(spacing * 2)
                row.addWidget(self._lbl_right)
                row.addSpacing(spacing)
                self._flash_layout.addLayout(row)
            else:
                col = QVBoxLayout()
                col.setAlignment(Qt.AlignmentFlag.AlignCenter)
                col.addSpacing(spacing // 2)
                col.addWidget(self._lbl_left, alignment=Qt.AlignmentFlag.AlignCenter)
                col.addSpacing(spacing)
                col.addWidget(self._lbl_right, alignment=Qt.AlignmentFlag.AlignCenter)
                col.addSpacing(spacing // 2)
                self._flash_layout.addLayout(col)
        else:
            self._lbl_center = QLabel(self.target_val)
            self._lbl_center.setFont(make_qfont(font_key))
            self._lbl_center.setStyleSheet(f"color: {c['fg']};")
            self._lbl_center.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._flash_layout.addWidget(self._lbl_center)

        self._after(FLASH_TIMING["flash_duration"], self._hide_flash)

    def _hide_flash(self) -> None:
        if not self._running:
            return
        # Clear flash area content
        while self._flash_layout.count():
            item = self._flash_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setVisible(False)
            sub = item.layout()
            if sub:
                while sub.count():
                    si = sub.takeAt(0)
                    sw = si.widget()
                    if sw:
                        sw.setVisible(False)

        self._after(FLASH_TIMING["post_flash_delay"], self._show_input)

    def _show_input(self) -> None:
        if not self._running:
            return
        c = COLORS

        input_widget = QWidget()
        input_layout = QVBoxLayout(input_widget)
        input_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._entry = QLineEdit()
        self._entry.setFont(make_qfont("input"))
        self._entry.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._entry.setStyleSheet(
            f"QLineEdit {{ background-color: {c['card']}; color: {c['text_on_card']}; "
            f"border: none; padding: 8px 16px; border-radius: 4px; min-width: 200px; }}"
        )
        self._entry.returnPressed.connect(
            lambda: self._verify(self._entry.text())
        )
        input_layout.addWidget(self._entry)

        check_btn = QPushButton("CHECK")
        check_btn.setFont(make_qfont("btn_bold"))
        check_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['accent']}; color: {c['btn_text']}; "
            f"border: none; padding: 6px 20px; border-radius: 3px; }}"
        )
        check_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        check_btn.clicked.connect(
            lambda: self._verify(self._entry.text())
        )
        input_layout.addWidget(check_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self._flash_layout.addWidget(input_widget)
        self._entry.setFocus()

    def _verify(self, user_input: str) -> None:
        if user_input.upper().strip() == self.target_val:
            self.correct_count += 1
            self._next_round()
        else:
            self._show_correction()

    def _show_correction(self) -> None:
        if not self._running:
            return
        c = COLORS

        # Clear flash area and show correct answer
        while self._flash_layout.count():
            item = self._flash_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        font_key = "rsvp" if self.mode == "flash_word" else "flash"
        correction = QLabel(self.target_val)
        correction.setFont(make_qfont(font_key))
        correction.setStyleSheet(f"color: {c['alert']};")
        correction.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._flash_layout.addWidget(correction)

        self._after(FLASH_TIMING["correction_display"], self._next_round)

    def _complete_exercise(self) -> None:
        xp_gained = self.correct_count * USER_DATA_CONFIG["xp_per_correct"]
        result = ExerciseResult(
            exercise_name=self.mode.upper(),
            score=self.correct_count,
            total=self.rounds_total,
            xp_gained=xp_gained,
        )
        is_pb = self.complete(result)
        self.show_result_screen(result, is_personal_best=is_pb)
