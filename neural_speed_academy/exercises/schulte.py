"""
Schulte Grid exercise for focus and peripheral vision training.
"""
from __future__ import annotations

import random
import time

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout,
)
from PyQt6.QtCore import Qt

from neural_speed_academy.exercises.base import BaseExercise, ExerciseResult
from neural_speed_academy.theme import COLORS, make_qfont, btn_css, screen_metrics, theme_manager
from neural_speed_academy.config import SCHULTE_CONFIG


class SchulteExercise(BaseExercise):

    def __init__(self, navigator, parent: QWidget | None = None):
        super().__init__(navigator, parent)
        self.target: int = 1
        self.score: int = 0
        self.max_num: int = 0
        self._errors: int = 0
        self._start_time: float = 0.0

    @property
    def name(self) -> str:
        return "Schulte Grid"

    def start(self, **kwargs) -> None:
        grid_size = kwargs.get("grid_size", theme_manager.schulte_grid_size)
        cell_idx = kwargs.get("cell_idx", theme_manager.schulte_cell_idx)
        self._start_grid(grid_size, cell_idx)

    # Reference cell sizes (px at 1920×1080), scaled by ScreenMetrics
    _CELL_PRESETS = {0: ("Small", 70), 1: ("Medium", 100), 2: ("Large", 120), 3: ("XL", 140)}

    @classmethod
    def _cell_px(cls, idx: int) -> int:
        return screen_metrics.s(cls._CELL_PRESETS[idx][1])

    # ── Grid screen ──

    def _start_grid(self, grid_size: int = 5, cell_idx: int = 1) -> None:
        # Save as new defaults
        theme_manager.schulte_grid_size = grid_size
        theme_manager.schulte_cell_idx = cell_idx
        theme_manager.save()

        self._clear()
        self._running = True

        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")

        self.max_num = grid_size * grid_size
        self.target = 1
        self.score = 0
        self._errors = 0
        self._start_time = time.monotonic()

        btn_size = self._cell_px(cell_idx)

        # Minimal top bar
        top = QHBoxLayout()
        top.setContentsMargins(10, 6, 10, 2)

        self._lbl_target = QLabel(f"FIND: {self.target}")
        self._lbl_target.setFont(make_qfont("grid_btn"))
        self._lbl_target.setStyleSheet(f"color: {c['fg']};")
        top.addWidget(self._lbl_target)

        top.addStretch()

        self._lbl_score = QLabel(f"SCORE: {self.score}")
        self._lbl_score.setFont(make_qfont("grid_btn"))
        self._lbl_score.setStyleSheet(f"color: {c['accent']};")
        top.addWidget(self._lbl_score)

        top.addStretch()

        exit_btn = QPushButton("\u2716")
        exit_btn.setAccessibleName("Close")
        exit_btn.setToolTip("Close")
        exit_btn.setFont(make_qfont("exit_btn"))
        exit_btn.setStyleSheet(
            btn_css(c["alert"], c["text_on_card"], padding="4px 8px",
                    radius=3, font_key="exit_btn")
        )
        exit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        exit_btn.clicked.connect(self._stop_exercise)
        top.addWidget(exit_btn)
        self._layout.addLayout(top)

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
                    f"color: {c['grid_text']}; border: 2px solid transparent; "
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
                f"color: {c['grid_text']}; border: 2px solid transparent; border-radius: 4px; }}"
            )
            button.setEnabled(False)
            self.target += 1
            self.score += SCHULTE_CONFIG["correct_points"]

            if self.target > self.max_num:
                self._complete_exercise()
                return
            self._lbl_target.setText(f"FIND: {self.target}")
        else:
            self._errors += 1
            self.score -= SCHULTE_CONFIG["wrong_penalty"]
            orig_style = button.styleSheet()
            button.setStyleSheet(
                f"QPushButton {{ background-color: {c['alert']}; "
                f"color: {c['grid_text']}; border: 2px solid transparent; border-radius: 4px; }}"
            )
            self._after(200, lambda: button.setStyleSheet(orig_style))

        self._lbl_score.setText(f"SCORE: {self.score}")

    def _complete_exercise(self) -> None:
        grid_size = theme_manager.schulte_grid_size
        elapsed = round(time.monotonic() - self._start_time, 1)
        completed = self.target - 1  # cells successfully found
        result = ExerciseResult(
            exercise_name=self.name,
            score=completed,
            total=self.max_num,
            xp_gained=max(self.score, 0),
            metadata={
                "grid_size": grid_size,
                "cells": grid_size * grid_size,
                "points": self.score,
                "errors": self._errors,
                "duration_s": elapsed,
            },
        )
        is_pb = self.complete(result)
        self.show_result_screen(
            result, is_personal_best=is_pb, details="Grid cleared!"
        )
