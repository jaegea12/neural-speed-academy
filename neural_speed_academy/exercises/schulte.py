"""
Schulte Grid exercise for focus and peripheral vision training.
"""
from __future__ import annotations

import random

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout,
)
from PyQt6.QtCore import Qt

from neural_speed_academy.exercises.base import BaseExercise, ExerciseResult
from neural_speed_academy.theme import COLORS, make_qfont
from neural_speed_academy.config import SCHULTE_CONFIG


class SchulteExercise(BaseExercise):

    def __init__(self, navigator, parent: QWidget | None = None):
        super().__init__(navigator, parent)
        self.target: int = 1
        self.score: int = 0
        self.max_num: int = 0

    @property
    def name(self) -> str:
        return "Schulte Grid"

    def start(self, **kwargs) -> None:
        self._clear()
        self._running = True
        self.add_nav_bar()

        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")

        guide_btn = QPushButton("GUIDE")
        guide_btn.setFont(make_qfont("btn_sm"))
        guide_btn.setStyleSheet(
            f"background-color: {c['accent']}; color: {c['btn_text']}; "
            f"border: none; padding: 4px 12px; border-radius: 3px;"
        )
        guide_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        guide_btn.clicked.connect(lambda: self.show_guide("schulte"))
        self._layout.addWidget(guide_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        from neural_speed_academy.theme import theme_manager, FOV_PRESETS

        grid_size = SCHULTE_CONFIG["grid_size"]
        self.max_num = grid_size * grid_size
        self.target = 1
        self.score = 0

        # Cell size scaled to screen dimensions
        from neural_speed_academy.theme import screen_metrics
        btn_size = screen_metrics.schulte_cell

        # Stats
        stats = QHBoxLayout()
        stats.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._lbl_target = QLabel(f"FIND: {self.target}")
        self._lbl_target.setFont(make_qfont("grid_btn"))
        self._lbl_target.setStyleSheet(f"color: {c['fg']};")
        stats.addWidget(self._lbl_target)

        self._lbl_score = QLabel(f"SCORE: {self.score}")
        self._lbl_score.setFont(make_qfont("grid_btn"))
        self._lbl_score.setStyleSheet(f"color: {c['accent']};")
        stats.addWidget(self._lbl_score)

        self._layout.addLayout(stats)

        # Grid
        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setSpacing(6)

        nums = list(range(1, self.max_num + 1))
        random.shuffle(nums)
        for i in range(grid_size):
            for j in range(grid_size):
                val = nums.pop()
                btn = QPushButton(str(val))
                btn.setFont(make_qfont("grid_btn"))
                btn.setFixedSize(btn_size, btn_size)
                btn.setStyleSheet(
                    f"QPushButton {{ background-color: {c['grid_btn']}; "
                    f"color: {c['text_on_card']}; border: none; "
                    f"border-radius: 4px; }}"
                    f"QPushButton:hover {{ opacity: 0.9; }}"
                )
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.clicked.connect(
                    lambda checked, v=val, b=btn: self._on_click(v, b)
                )
                grid.addWidget(btn, i, j)

        self._layout.addWidget(
            grid_widget, 1, Qt.AlignmentFlag.AlignCenter
        )

    def _on_click(self, value: int, button: QPushButton) -> None:
        c = COLORS
        if value == self.target:
            button.setStyleSheet(
                f"QPushButton {{ background-color: {c['grid_solved']}; "
                f"color: {c['text_on_card']}; border: none; border-radius: 4px; }}"
            )
            button.setEnabled(False)
            self.target += 1
            self.score += SCHULTE_CONFIG["correct_points"]

            if self.target > self.max_num:
                self._complete_exercise()
                return
            self._lbl_target.setText(f"FIND: {self.target}")
        else:
            self.score -= SCHULTE_CONFIG["wrong_penalty"]
            orig_style = button.styleSheet()
            button.setStyleSheet(
                f"QPushButton {{ background-color: {c['alert']}; "
                f"color: {c['text_on_card']}; border: none; border-radius: 4px; }}"
            )
            self._after(200, lambda: button.setStyleSheet(orig_style))

        self._lbl_score.setText(f"SCORE: {self.score}")

    def _complete_exercise(self) -> None:
        result = ExerciseResult(
            exercise_name=self.name,
            score=self.score,
            total=self.max_num,
            xp_gained=self.score,
        )
        is_pb = self.complete(result)
        self.show_result_screen(
            result, is_personal_best=is_pb, details="Grid cleared!"
        )
