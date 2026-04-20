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
from neural_speed_academy.i18n import tr


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

    # Fill-percentage presets: how much of the screen height the grid uses
    FILL_PRESETS = {0: 60, 1: 75, 2: 90}

    def start(self, **kwargs) -> None:
        grid_size = kwargs.get("grid_size", theme_manager.schulte_grid_size)
        fill_idx = kwargs.get("fill_idx", getattr(theme_manager, "schulte_fill_idx", 1))
        self._show_countdown(lambda: self._start_grid(grid_size, fill_idx))

    # ── Grid screen ──

    def _start_grid(self, grid_size: int = 5, fill_idx: int = 1) -> None:
        # Save as new defaults
        theme_manager.schulte_grid_size = grid_size
        theme_manager.schulte_fill_idx = fill_idx
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

        # Compute cell size from window height percentage
        fill_pct = self.FILL_PRESETS.get(fill_idx, 75)
        # Use actual window height, not physical screen height
        win = self.window()
        avail_h = win.height() if win else screen_metrics.screen_h
        # Reserve space for top bar (~50px) and spacing
        grid_h = int((avail_h - 60) * fill_pct / 100)
        spacing = 6
        btn_size = max(30, (grid_h - (grid_size - 1) * spacing) // grid_size)

        # Minimal top bar
        top = QHBoxLayout()
        top.setContentsMargins(10, 6, 10, 2)

        self._lbl_target = QLabel(tr("schulte.find", target=self.target))
        self._lbl_target.setFont(make_qfont("grid_btn"))
        self._lbl_target.setStyleSheet(f"color: {c['fg']};")
        top.addWidget(self._lbl_target)

        top.addStretch()

        self._lbl_score = QLabel(tr("schulte.score", score=self.score))
        self._lbl_score.setFont(make_qfont("grid_btn"))
        self._lbl_score.setStyleSheet(f"color: {c['accent']};")
        top.addWidget(self._lbl_score)

        top.addStretch()

        exit_btn = QPushButton(tr("chunking.u2716"))
        exit_btn.setAccessibleName(tr("chunking.close"))
        exit_btn.setToolTip(tr("chunking.close"))
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
                # #linux — QSS 'opacity' is not supported by all Qt
                # platform themes; the hover effect may be invisible.
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
                f"color: {c['muted']}; border: 2px solid transparent; border-radius: 4px; }}"
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
            result, is_personal_best=is_pb, details=tr("result.grid_cleared")
        )
