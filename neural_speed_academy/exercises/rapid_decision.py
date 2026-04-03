"""
Rapid Decision Grid — rule-based Schulte grid variants.

Modes:
  ascending    — classic 1→2→3 order
  descending   — highest number first
  even_only    — click only even numbers, ascending
  odd_only     — click only odd numbers, ascending
  alternating  — red numbers ascending + blue numbers descending, alternate
  All modes support an optional countdown timer.
"""
from __future__ import annotations

import random
import time

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout,
    QSlider, QComboBox,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QKeySequence, QShortcut

from neural_speed_academy.exercises.base import BaseExercise, ExerciseResult
from neural_speed_academy.theme import COLORS, make_qfont, screen_metrics, theme_manager
from neural_speed_academy.config import RAPID_DECISION_CONFIG, USER_DATA_CONFIG


class RapidDecisionGridExercise(BaseExercise):

    MODES = [
        ("ascending", "Ascending (1→2→3…)"),
        ("descending", "Descending (25→24→23…)"),
        ("even_only", "Even Numbers Only"),
        ("odd_only", "Odd Numbers Only"),
        ("alternating", "Alternating Colors"),
    ]

    # Cell size presets (same as Schulte)
    _CELL_PRESETS = {
        0: ("Small", 70), 1: ("Medium", 100),
        2: ("Large", 120), 3: ("XL", 140),
    }

    def __init__(self, navigator, parent: QWidget | None = None):
        super().__init__(navigator, parent)
        self._mode: str = "ascending"
        self._grid_size: int = 5
        self._time_limit: int = 0
        self._score: int = 0
        self._targets: list[int] = []
        self._target_idx: int = 0
        self._buttons: dict[int, QPushButton] = {}
        self._start_time: float = 0.0
        self._countdown_timer: QTimer | None = None
        # For alternating mode
        self._red_targets: list[int] = []
        self._blue_targets: list[int] = []
        self._red_idx: int = 0
        self._blue_idx: int = 0
        self._next_color: str = "red"

    @property
    def name(self) -> str:
        return "Rapid Decision Grid"

    # ── Config screen ──

    def start(self, **kwargs) -> None:
        self._clear()
        self._running = True
        self.add_nav_bar(show_stop=False)

        c = COLORS
        cfg = RAPID_DECISION_CONFIG
        self.setStyleSheet(f"background-color: {c['bg']};")

        self._mode = kwargs.get("mode", "ascending")
        self._grid_size = kwargs.get("grid_size", cfg["default_grid_size"])
        self._time_limit = kwargs.get("time_limit", 0)

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
        guide_btn.clicked.connect(
            lambda: self.show_guide("rapid_decision")
        )
        top.addWidget(guide_btn)
        top.addStretch()
        cl.addLayout(top)

        title = QLabel("RAPID DECISION GRID")
        title.setFont(make_qfont("section_header"))
        title.setStyleSheet(f"color: {c['accent']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(title)

        cl.addSpacing(8)

        # Mode selector
        mode_row = QHBoxLayout()
        mode_row.addStretch()
        mode_lbl = QLabel("Mode:")
        mode_lbl.setFont(make_qfont("slider_label"))
        mode_lbl.setStyleSheet(f"color: {c['fg']};")
        mode_row.addWidget(mode_lbl)

        self._mode_combo = QComboBox()
        for key, label in self.MODES:
            self._mode_combo.addItem(label, key)
        # Set current mode
        for i, (key, _) in enumerate(self.MODES):
            if key == self._mode:
                self._mode_combo.setCurrentIndex(i)
                break
        self._mode_combo.setStyleSheet(
            f"QComboBox {{ background-color: {c['card']}; color: {c['fg']}; "
            f"border: 1px solid {c['muted']}; padding: 4px 8px; "
            f"border-radius: 3px; }}"
            f"QComboBox::drop-down {{ border: none; }}"
            f"QComboBox QAbstractItemView {{ background-color: {c['card']}; "
            f"color: {c['fg']}; selection-background-color: {c['accent']}; }}"
        )
        self._mode_combo.setFixedWidth(250)
        mode_row.addWidget(self._mode_combo)
        mode_row.addStretch()
        cl.addLayout(mode_row)

        # Mode description
        self._mode_desc = QLabel("")
        self._mode_desc.setFont(make_qfont("body"))
        self._mode_desc.setStyleSheet(f"color: {c['muted']};")
        self._mode_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._mode_desc.setWordWrap(True)
        cl.addWidget(self._mode_desc)
        self._mode_combo.currentIndexChanged.connect(self._update_mode_desc)
        self._update_mode_desc()

        # Grid size
        size_row = QHBoxLayout()
        size_row.addStretch()
        size_lbl = QLabel("Grid size:")
        size_lbl.setFont(make_qfont("slider_label"))
        size_lbl.setStyleSheet(f"color: {c['fg']};")
        size_row.addWidget(size_lbl)

        self._size_slider = QSlider(Qt.Orientation.Horizontal)
        self._size_slider.setRange(3, 7)
        self._size_slider.setValue(self._grid_size)
        self._size_slider.setFixedWidth(200)
        self._size_slider.setStyleSheet(slider_groove)

        self._size_display = QLabel(f"{self._grid_size}\u00d7{self._grid_size}")
        self._size_display.setFont(make_qfont("counter"))
        self._size_display.setStyleSheet(f"color: {c['accent']};")
        self._size_display.setFixedWidth(50)
        self._size_slider.valueChanged.connect(
            lambda v: self._size_display.setText(f"{v}\u00d7{v}")
        )
        size_row.addWidget(self._size_slider)
        size_row.addWidget(self._size_display)
        size_row.addStretch()
        cl.addLayout(size_row)

        # Cell size
        cell_row = QHBoxLayout()
        cell_row.addStretch()
        cell_lbl = QLabel("Cell size:")
        cell_lbl.setFont(make_qfont("slider_label"))
        cell_lbl.setStyleSheet(f"color: {c['fg']};")
        cell_row.addWidget(cell_lbl)

        default_cell = theme_manager.schulte_cell_idx
        self._cell_slider = QSlider(Qt.Orientation.Horizontal)
        self._cell_slider.setRange(0, 3)
        self._cell_slider.setValue(default_cell)
        self._cell_slider.setFixedWidth(200)
        self._cell_slider.setStyleSheet(slider_groove)

        self._cell_display = QLabel(self._CELL_PRESETS[default_cell][0])
        self._cell_display.setFont(make_qfont("counter"))
        self._cell_display.setStyleSheet(f"color: {c['accent']};")
        self._cell_display.setFixedWidth(70)
        self._cell_slider.valueChanged.connect(
            lambda v: self._cell_display.setText(self._CELL_PRESETS[v][0])
        )
        cell_row.addWidget(self._cell_slider)
        cell_row.addWidget(self._cell_display)
        cell_row.addStretch()
        cl.addLayout(cell_row)

        # Time limit
        time_row = QHBoxLayout()
        time_row.addStretch()
        time_lbl = QLabel("Time limit:")
        time_lbl.setFont(make_qfont("slider_label"))
        time_lbl.setStyleSheet(f"color: {c['fg']};")
        time_row.addWidget(time_lbl)

        self._time_combo = QComboBox()
        self._time_combo.addItem("No limit", 0)
        self._time_combo.addItem("60 seconds", 60)
        self._time_combo.addItem("45 seconds", 45)
        self._time_combo.addItem("30 seconds", 30)
        for i in range(self._time_combo.count()):
            if self._time_combo.itemData(i) == self._time_limit:
                self._time_combo.setCurrentIndex(i)
                break
        self._time_combo.setStyleSheet(
            f"QComboBox {{ background-color: {c['card']}; color: {c['fg']}; "
            f"border: 1px solid {c['muted']}; padding: 4px 8px; "
            f"border-radius: 3px; }}"
            f"QComboBox::drop-down {{ border: none; }}"
            f"QComboBox QAbstractItemView {{ background-color: {c['card']}; "
            f"color: {c['fg']}; selection-background-color: {c['accent']}; }}"
        )
        self._time_combo.setFixedWidth(150)
        time_row.addWidget(self._time_combo)
        time_row.addStretch()
        cl.addLayout(time_row)

        # Start button
        cl.addSpacing(8)
        start_btn = QPushButton("START")
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

        cl.addStretch()
        self._layout.addWidget(container, 1)

    def _update_mode_desc(self) -> None:
        descs = {
            "ascending": "Click numbers 1\u21922\u21923\u2026 in order.",
            "descending": "Start from the highest number and count down.",
            "even_only": "Click only even numbers in ascending order. Ignore odds.",
            "odd_only": "Click only odd numbers in ascending order. Ignore evens.",
            "alternating": "Red numbers go up, blue numbers go down. Alternate between them.",
        }
        key = self._mode_combo.currentData()
        self._mode_desc.setText(descs.get(key, ""))

    def _start_from_ui(self) -> None:
        self._mode = self._mode_combo.currentData()
        self._grid_size = self._size_slider.value()
        self._time_limit = self._time_combo.currentData()
        self._run_grid()

    # ── Grid screen ──

    def _run_grid(self) -> None:
        self._clear()
        self._running = True
        self.add_nav_bar()

        c = COLORS
        cfg = RAPID_DECISION_CONFIG
        self.setStyleSheet(f"background-color: {c['bg']};")

        max_num = self._grid_size * self._grid_size
        self._score = 0
        self._buttons = {}
        self._start_time = time.monotonic()

        # Build target sequence based on mode
        all_nums = list(range(1, max_num + 1))

        if self._mode == "ascending":
            self._targets = sorted(all_nums)
        elif self._mode == "descending":
            self._targets = sorted(all_nums, reverse=True)
        elif self._mode == "even_only":
            self._targets = sorted(n for n in all_nums if n % 2 == 0)
        elif self._mode == "odd_only":
            self._targets = sorted(n for n in all_nums if n % 2 != 0)
        elif self._mode == "alternating":
            # Split into two color groups
            random.shuffle(all_nums)
            half = len(all_nums) // 2
            self._red_targets = sorted(all_nums[:half])
            self._blue_targets = sorted(all_nums[half:], reverse=True)
            self._red_idx = 0
            self._blue_idx = 0
            self._next_color = "red"
            self._targets = []  # not used directly in alternating

        self._target_idx = 0

        # Stats bar
        stats = QHBoxLayout()
        stats.setContentsMargins(10, 4, 10, 2)

        if self._mode == "alternating":
            first_red = self._red_targets[0] if self._red_targets else "—"
            target_text = f"RED: {first_red}"
        else:
            target_text = f"FIND: {self._targets[0]}" if self._targets else "DONE"

        self._lbl_target = QLabel(target_text)
        self._lbl_target.setFont(make_qfont("grid_btn"))
        self._lbl_target.setStyleSheet(f"color: {c['fg']};")
        stats.addWidget(self._lbl_target)

        stats.addStretch()

        self._lbl_score = QLabel("SCORE: 0")
        self._lbl_score.setFont(make_qfont("grid_btn"))
        self._lbl_score.setStyleSheet(f"color: {c['accent']};")
        stats.addWidget(self._lbl_score)

        stats.addStretch()

        # Timer label (always present, shows elapsed or countdown)
        self._lbl_timer = QLabel("")
        self._lbl_timer.setFont(make_qfont("counter"))
        self._lbl_timer.setStyleSheet(f"color: {c['fg']};")
        stats.addWidget(self._lbl_timer)

        exit_btn = QPushButton("\u2716")
        exit_btn.setAccessibleName("Close")
        exit_btn.setToolTip("Close")
        exit_btn.setFont(make_qfont("exit_btn"))
        exit_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['alert']}; "
            f"color: {c['text_on_card']}; "
            f"border: 2px solid transparent; padding: 4px 8px; border-radius: 3px; }}"
        )
        exit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        exit_btn.clicked.connect(self._stop)
        stats.addWidget(exit_btn)

        self._layout.addLayout(stats)

        # Rule hint
        hints = {
            "ascending": "Click numbers in ascending order",
            "descending": "Click numbers in descending order",
            "even_only": "Click EVEN numbers only, ascending",
            "odd_only": "Click ODD numbers only, ascending",
            "alternating": "Alternate: RED \u2191 ascending, BLUE \u2193 descending",
        }
        hint_lbl = QLabel(hints.get(self._mode, ""))
        hint_lbl.setFont(make_qfont("btn_sm"))
        hint_lbl.setStyleSheet(f"color: {c['muted']};")
        hint_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(hint_lbl)

        # Build grid
        cell_idx = self._cell_slider.value() if hasattr(self, '_cell_slider') else 1
        btn_size = screen_metrics.s(self._CELL_PRESETS[cell_idx][1])

        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setSpacing(6)

        nums = list(range(1, max_num + 1))
        random.shuffle(nums)

        # For alternating mode, assign colors
        red_set = set(self._red_targets) if self._mode == "alternating" else set()
        blue_set = set(self._blue_targets) if self._mode == "alternating" else set()

        for i in range(self._grid_size):
            for j in range(self._grid_size):
                val = nums.pop()
                btn = QPushButton(str(val))
                btn.setFont(make_qfont("grid_btn"))
                btn.setFixedSize(btn_size, btn_size)

                if self._mode == "alternating" and val in red_set:
                    btn.setStyleSheet(
                        f"QPushButton {{ background-color: {c['grid_btn']}; "
                        f"color: #ef4444; border: 2px solid transparent; border-radius: 4px; "
                        f"font-weight: bold; }}"
                    )
                elif self._mode == "alternating" and val in blue_set:
                    btn.setStyleSheet(
                        f"QPushButton {{ background-color: {c['grid_btn']}; "
                        f"color: #3b82f6; border: 2px solid transparent; border-radius: 4px; "
                        f"font-weight: bold; }}"
                    )
                else:
                    btn.setStyleSheet(
                        f"QPushButton {{ background-color: {c['grid_btn']}; "
                        f"color: {c['grid_text']}; border: 2px solid transparent; "
                        f"border-radius: 4px; }}"
                    )

                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.clicked.connect(
                    lambda checked, v=val, b=btn: self._on_click(v, b)
                )
                grid.addWidget(btn, i, j)
                self._buttons[val] = btn

        self._layout.addWidget(
            grid_widget, 1, Qt.AlignmentFlag.AlignCenter
        )

        # Start timer
        self._countdown_timer = QTimer(self)
        self._countdown_timer.setInterval(1000)
        self._countdown_timer.timeout.connect(self._tick)
        self._countdown_timer.start()
        self._tick()

    def _tick(self) -> None:
        if not self._running:
            return
        elapsed = int(time.monotonic() - self._start_time)
        c = COLORS

        if self._time_limit > 0:
            remaining = max(0, self._time_limit - elapsed)
            self._lbl_timer.setText(f"{remaining}s")
            if remaining <= 10:
                self._lbl_timer.setStyleSheet(f"color: {c['alert']};")
            if remaining <= 0:
                self._time_up()
        else:
            self._lbl_timer.setText(f"{elapsed}s")

    def _time_up(self) -> None:
        """Called when countdown reaches zero."""
        self._running = False
        if self._countdown_timer:
            self._countdown_timer.stop()
        self._complete_exercise(timed_out=True)

    # ── Click handling ──

    def _on_click(self, value: int, button: QPushButton) -> None:
        if not self._running:
            return
        c = COLORS
        cfg = RAPID_DECISION_CONFIG

        if self._mode == "alternating":
            self._on_click_alternating(value, button)
            return

        # For filter modes, clicking a non-target is always wrong
        if self._mode == "even_only" and value % 2 != 0:
            self._wrong_click(button)
            return
        if self._mode == "odd_only" and value % 2 == 0:
            self._wrong_click(button)
            return

        expected = self._targets[self._target_idx] if self._target_idx < len(self._targets) else None

        if value == expected:
            button.setStyleSheet(
                f"QPushButton {{ background-color: {c['grid_solved']}; "
                f"color: {c['grid_text']}; border: 2px solid transparent; border-radius: 4px; }}"
            )
            button.setEnabled(False)
            self._score += cfg["correct_points"]
            self._target_idx += 1

            if self._target_idx >= len(self._targets):
                self._complete_exercise()
                return

            self._lbl_target.setText(f"FIND: {self._targets[self._target_idx]}")
        else:
            self._wrong_click(button)

        self._lbl_score.setText(f"SCORE: {self._score}")

    def _on_click_alternating(self, value: int, button: QPushButton) -> None:
        c = COLORS
        cfg = RAPID_DECISION_CONFIG

        if self._next_color == "red":
            if self._red_idx < len(self._red_targets) and value == self._red_targets[self._red_idx]:
                button.setStyleSheet(
                    f"QPushButton {{ background-color: {c['grid_solved']}; "
                    f"color: {c['grid_text']}; border: 2px solid transparent; border-radius: 4px; }}"
                )
                button.setEnabled(False)
                self._score += cfg["correct_points"]
                self._red_idx += 1
                self._next_color = "blue"

                if self._red_idx >= len(self._red_targets) and self._blue_idx >= len(self._blue_targets):
                    self._complete_exercise()
                    return

                self._update_alternating_target()
            else:
                self._wrong_click(button)
        else:
            if self._blue_idx < len(self._blue_targets) and value == self._blue_targets[self._blue_idx]:
                button.setStyleSheet(
                    f"QPushButton {{ background-color: {c['grid_solved']}; "
                    f"color: {c['grid_text']}; border: 2px solid transparent; border-radius: 4px; }}"
                )
                button.setEnabled(False)
                self._score += cfg["correct_points"]
                self._blue_idx += 1
                self._next_color = "red"

                if self._red_idx >= len(self._red_targets) and self._blue_idx >= len(self._blue_targets):
                    self._complete_exercise()
                    return

                self._update_alternating_target()
            else:
                self._wrong_click(button)

        self._lbl_score.setText(f"SCORE: {self._score}")

    def _update_alternating_target(self) -> None:
        c = COLORS
        if self._next_color == "red":
            if self._red_idx < len(self._red_targets):
                val = self._red_targets[self._red_idx]
                self._lbl_target.setText(f"RED: {val}")
                self._lbl_target.setStyleSheet("color: #ef4444;")
            else:
                # Red exhausted, switch to blue permanently
                self._next_color = "blue"
                self._update_alternating_target()
        else:
            if self._blue_idx < len(self._blue_targets):
                val = self._blue_targets[self._blue_idx]
                self._lbl_target.setText(f"BLUE: {val}")
                self._lbl_target.setStyleSheet("color: #3b82f6;")
            else:
                # Blue exhausted, switch to red permanently
                self._next_color = "red"
                self._update_alternating_target()

    def _wrong_click(self, button: QPushButton) -> None:
        c = COLORS
        cfg = RAPID_DECISION_CONFIG
        self._score -= cfg["wrong_penalty"]
        orig_style = button.styleSheet()
        button.setStyleSheet(
            f"QPushButton {{ background-color: {c['alert']}; "
            f"color: {c['grid_text']}; border: 2px solid transparent; border-radius: 4px; }}"
        )
        self._after(200, lambda: button.setStyleSheet(orig_style))

    # ── Completion ──

    def _complete_exercise(self, timed_out: bool = False) -> None:
        self._running = False
        if self._countdown_timer:
            self._countdown_timer.stop()

        elapsed = round(time.monotonic() - self._start_time, 1)
        max_num = self._grid_size * self._grid_size

        if self._mode == "alternating":
            total_targets = len(self._red_targets) + len(self._blue_targets)
            completed = self._red_idx + self._blue_idx
        elif self._mode in ("even_only", "odd_only"):
            total_targets = len(self._targets)
            completed = self._target_idx
        else:
            total_targets = max_num
            completed = self._target_idx

        result = ExerciseResult(
            exercise_name="RAPID DECISION",
            score=completed,
            total=total_targets,
            xp_gained=max(self._score, 0),
            metadata={
                "mode": self._mode,
                "grid_size": self._grid_size,
                "cells": max_num,
                "points": self._score,
                "targets_completed": completed,
                "targets_total": total_targets,
                "time_limit": self._time_limit,
                "duration_s": elapsed,
                "timed_out": timed_out,
            },
        )
        is_pb = self.complete(result)

        status = "Time's up!" if timed_out else "Grid cleared!"
        mode_label = dict(self.MODES).get(self._mode, self._mode)
        details = (
            f"Mode: {mode_label}\n"
            f"Completed: {completed}/{total_targets} targets in {elapsed}s\n"
            f"{status}"
        )
        self.show_result_screen(result, is_personal_best=is_pb, details=details)

    def _stop(self) -> None:
        self._running = False
        if self._countdown_timer:
            self._countdown_timer.stop()
        self.navigator.finish_exercise()
