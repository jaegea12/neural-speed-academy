"""
Schulte Grid exercise for focus and peripheral vision training.
"""
from __future__ import annotations

import random

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout,
    QSlider,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut

from neural_speed_academy.exercises.base import BaseExercise, ExerciseResult
from neural_speed_academy.theme import COLORS, make_qfont, screen_metrics, theme_manager
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

    # ── Config screen ──

    def start(self, **kwargs) -> None:
        self._clear()
        self._running = True
        self.add_nav_bar(show_stop=False)

        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")

        container = QWidget()
        container.setStyleSheet(f"background-color: {c['bg']};")
        cl = QVBoxLayout(container)
        cl.setContentsMargins(40, 10, 40, 10)
        cl.setSpacing(6)

        slider_groove = (
            f"QSlider::groove:horizontal {{ background: {c['card']}; "
            f"height: 6px; border-radius: 3px; }}"
            f"QSlider::handle:horizontal {{ background: {c['accent']}; "
            f"width: 16px; margin: -5px 0; border-radius: 8px; }}"
        )

        # Top row: guide button
        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        guide_btn = QPushButton("GUIDE")
        guide_btn.setFont(make_qfont("btn_sm"))
        guide_btn.setStyleSheet(
            f"background-color: {c['accent']}; color: {c['btn_text']}; "
            f"border: none; padding: 4px 12px; border-radius: 3px;"
        )
        guide_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        guide_btn.clicked.connect(lambda: self.show_guide("schulte"))
        top.addWidget(guide_btn)
        top.addStretch()
        cl.addLayout(top)

        title = QLabel("SCHULTE GRID CONFIGURATION")
        title.setFont(make_qfont("section_header"))
        title.setStyleSheet(f"color: {c['accent']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(title)

        cl.addSpacing(12)

        # Grid size: label + slider + value in one row
        size_row = QHBoxLayout()
        size_row.setContentsMargins(0, 0, 0, 0)
        size_row.setSpacing(8)
        size_row.addStretch()
        size_lbl = QLabel("Grid size:")
        size_lbl.setFont(make_qfont("slider_label"))
        size_lbl.setStyleSheet(f"color: {c['fg']};")
        size_row.addWidget(size_lbl)

        default_grid = theme_manager.schulte_grid_size
        default_cell = theme_manager.schulte_cell_idx

        self._size_slider = QSlider(Qt.Orientation.Horizontal)
        self._size_slider.setRange(3, 7)
        self._size_slider.setValue(default_grid)
        self._size_slider.setFixedWidth(200)
        self._size_slider.setStyleSheet(slider_groove)

        self._size_display = QLabel(self._grid_label(default_grid))
        self._size_display.setFont(make_qfont("counter"))
        self._size_display.setStyleSheet(f"color: {c['accent']};")
        self._size_display.setFixedWidth(50)
        self._size_slider.valueChanged.connect(
            lambda v: self._size_display.setText(self._grid_label(v))
        )
        size_row.addWidget(self._size_slider)
        size_row.addWidget(self._size_display)
        size_row.addStretch()
        cl.addLayout(size_row)

        # Description
        desc = QLabel("Smaller grids are easier. 5\u00d75 is the classic Schulte table.")
        desc.setFont(make_qfont("body"))
        desc.setStyleSheet(f"color: {c['muted']};")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(desc)

        # Cell count preview
        self._count_lbl = QLabel(self._count_text(default_grid))
        self._count_lbl.setFont(make_qfont("body"))
        self._count_lbl.setStyleSheet(f"color: {c['muted']};")
        self._count_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._size_slider.valueChanged.connect(
            lambda v: self._count_lbl.setText(self._count_text(v))
        )
        cl.addWidget(self._count_lbl)

        cl.addSpacing(4)

        # Cell size (FOV): label + slider + value in one row
        cell_row = QHBoxLayout()
        cell_row.setContentsMargins(0, 0, 0, 0)
        cell_row.setSpacing(8)
        cell_row.addStretch()
        cell_lbl = QLabel("Cell size:")
        cell_lbl.setFont(make_qfont("slider_label"))
        cell_lbl.setStyleSheet(f"color: {c['fg']};")
        cell_row.addWidget(cell_lbl)

        self._cell_slider = QSlider(Qt.Orientation.Horizontal)
        self._cell_slider.setRange(0, 3)
        self._cell_slider.setValue(default_cell)
        self._cell_slider.setFixedWidth(200)
        self._cell_slider.setStyleSheet(slider_groove)

        self._cell_display = QLabel(self._cell_label(default_cell))
        self._cell_display.setFont(make_qfont("counter"))
        self._cell_display.setStyleSheet(f"color: {c['accent']};")
        self._cell_display.setFixedWidth(70)
        self._cell_slider.valueChanged.connect(
            lambda v: self._cell_display.setText(self._cell_label(v))
        )
        cell_row.addWidget(self._cell_slider)
        cell_row.addWidget(self._cell_display)
        cell_row.addStretch()
        cl.addLayout(cell_row)

        cell_desc = QLabel(
            "Smaller cells require wider peripheral vision. "
            "Increase grid size or decrease cell size as you progress."
        )
        cell_desc.setFont(make_qfont("body"))
        cell_desc.setStyleSheet(f"color: {c['muted']};")
        cell_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cell_desc.setWordWrap(True)
        cl.addWidget(cell_desc)

        cl.addSpacing(8)

        # Start button + hint
        start_btn = QPushButton("START")
        start_btn.setFont(make_qfont("btn_lg"))
        start_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['success']}; "
            f"color: {c['btn_text']}; "
            f"border: none; padding: 10px 40px; border-radius: 4px; }}"
        )
        start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        start_btn.clicked.connect(self._start_grid)
        cl.addWidget(start_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        hint = QLabel("Ctrl+Enter to start")
        hint.setFont(make_qfont("btn_sm"))
        hint.setStyleSheet(f"color: {c['muted']};")
        cl.addWidget(hint, alignment=Qt.AlignmentFlag.AlignCenter)

        self._layout.addWidget(container, 1)

        # Ctrl+Enter shortcut
        shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        shortcut.activated.connect(self._start_grid)

    # Reference cell sizes (px at 1920×1080), scaled by ScreenMetrics
    _CELL_PRESETS = {0: ("Small", 70), 1: ("Medium", 100), 2: ("Large", 120), 3: ("XL", 140)}

    @staticmethod
    def _grid_label(n: int) -> str:
        return f"{n}\u00d7{n}"

    @staticmethod
    def _count_text(n: int) -> str:
        return f"Numbers 1\u2013{n * n}"

    @classmethod
    def _cell_label(cls, idx: int) -> str:
        return cls._CELL_PRESETS[idx][0]

    @classmethod
    def _cell_px(cls, idx: int) -> int:
        return screen_metrics.s(cls._CELL_PRESETS[idx][1])

    # ── Grid screen ──

    def _start_grid(self) -> None:
        grid_size = self._size_slider.value()
        cell_idx = self._cell_slider.value()

        # Silently save as new defaults
        theme_manager.schulte_grid_size = grid_size
        theme_manager.schulte_cell_idx = cell_idx
        theme_manager.save()

        self._clear()
        self._running = True
        self.add_nav_bar()

        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")

        self.max_num = grid_size * grid_size
        self.target = 1
        self.score = 0

        btn_size = self._cell_px(cell_idx)

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
                    f"color: {c['grid_text']}; border: none; "
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
                f"color: {c['grid_text']}; border: none; border-radius: 4px; }}"
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
                f"color: {c['grid_text']}; border: none; border-radius: 4px; }}"
            )
            self._after(200, lambda: button.setStyleSheet(orig_style))

        self._lbl_score.setText(f"SCORE: {self.score}")

    def _complete_exercise(self) -> None:
        grid_size = theme_manager.schulte_grid_size
        result = ExerciseResult(
            exercise_name=self.name,
            score=self.score,
            total=self.max_num,
            xp_gained=self.score,
            metadata={
                "grid_size": grid_size,
                "cells": grid_size * grid_size,
            },
        )
        is_pb = self.complete(result)
        self.show_result_screen(
            result, is_personal_best=is_pb, details="Grid cleared!"
        )
