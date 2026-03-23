"""
Menu screens for exercise selection.
"""
from __future__ import annotations

import random
from typing import Callable

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout,
)
from PyQt6.QtCore import Qt

from neural_speed_academy.screens.base import BaseScreen
from neural_speed_academy.theme import COLORS, make_qfont, font_css, btn_css, screen_metrics


class BaseMenuScreen(BaseScreen):
    """Base class for exercise menu screens."""

    @staticmethod
    def _difficulty_color(index: int, total: int) -> str:
        if total <= 1:
            return "diff_beginner"
        frac = index / (total - 1)
        if frac < 0.33:
            return "diff_beginner"
        elif frac < 0.66:
            return "diff_intermediate"
        elif frac < 0.9:
            return "diff_advanced"
        return "diff_elite"

    def _create_column_menu(
        self,
        title: str,
        guide_key: str,
        columns: list[tuple[str, list[tuple[str, Callable]]]],
        btn_width: int | None = None,
    ) -> None:
        if btn_width is None:
            btn_width = screen_metrics.menu_btn_w
        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")
        self.add_nav_bar()

        container = QWidget()
        container.setStyleSheet(f"background-color: {c['bg']};")
        cl = QVBoxLayout(container)
        cl.setContentsMargins(30, 20, 30, 20)
        cl.setSpacing(10)

        # Title row with guide button
        title_row = QHBoxLayout()
        title_row.addStretch()
        lbl = QLabel(title)
        lbl.setFont(make_qfont("header"))
        lbl.setStyleSheet(f"color: {c['fg']};")
        title_row.addWidget(lbl)

        guide_btn = QPushButton("GUIDE")
        guide_btn.setFont(make_qfont("btn_sm"))
        guide_btn.setStyleSheet(
            f"background-color: {c['accent']}; color: {c['btn_text']}; "
            f"border: none; padding: 6px 16px; border-radius: 4px;"
        )
        guide_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        guide_btn.clicked.connect(lambda: self.show_guide(guide_key))
        title_row.addWidget(guide_btn)
        title_row.addStretch()
        cl.addLayout(title_row)

        cl.addStretch()

        grid = QGridLayout()
        grid.setSpacing(10)
        grid.setContentsMargins(40, 0, 40, 0)

        # Headers
        for idx, (header, _items) in enumerate(columns):
            h = QLabel(header)
            h.setFont(make_qfont("menu_header"))
            h.setStyleSheet(f"color: {c['accent']};")
            h.setAlignment(Qt.AlignmentFlag.AlignCenter)
            grid.addWidget(h, 0, idx)

        max_len = max(len(items) for _, items in columns)
        cutoff = max(int(max_len * 0.6), 3)
        advanced_widgets: list[QPushButton] = []

        for i in range(max_len):
            for col_idx, (_header, items) in enumerate(columns):
                if i < len(items):
                    name, cmd = items[i]
                    color_key = self._difficulty_color(i, len(items))
                    btn = QPushButton(name)
                    btn.setFixedWidth(btn_width)
                    btn.setStyleSheet(
                        btn_css(c[color_key], c["btn_text"],
                                padding="10px", font_key="menu_btn")
                    )
                    btn.setCursor(Qt.CursorShape.PointingHandCursor)
                    btn.clicked.connect(cmd)
                    grid.addWidget(
                        btn, i + 1, col_idx,
                        alignment=Qt.AlignmentFlag.AlignCenter,
                    )
                    if i >= cutoff:
                        advanced_widgets.append(btn)
                        btn.setVisible(False)

        cl.addLayout(grid)

        if advanced_widgets:
            cl.addSpacing(6)
            self._adv_visible = False
            toggle = QPushButton("\u25bc SHOW ADVANCED")
            toggle.setStyleSheet(
                btn_css(c["card"], c["fg"], padding="6px 16px",
                        font_key="btn_sm")
            )
            toggle.setCursor(Qt.CursorShape.PointingHandCursor)

            def _toggle():
                self._adv_visible = not self._adv_visible
                for w in advanced_widgets:
                    w.setVisible(self._adv_visible)
                toggle.setText(
                    "\u25b2 HIDE ADVANCED" if self._adv_visible
                    else "\u25bc SHOW ADVANCED"
                )

            toggle.clicked.connect(_toggle)
            cl.addWidget(toggle, alignment=Qt.AlignmentFlag.AlignCenter)

        cl.addStretch()
        self._layout.addWidget(container, 1)

    def _create_grid_menu(
        self,
        title: str,
        guide_key: str,
        sets: list[tuple[str, Callable]],
        col1_label: str = "FIXED / BASIC",
        col2_label: str = "MIXED / ADVANCED",
    ) -> None:
        half = (len(sets) + 1) // 2
        self._create_column_menu(
            title, guide_key,
            columns=[
                (col1_label, sets[:half]),
                (col2_label, sets[half:]),
            ],
        )


class FlashMenuScreen(BaseMenuScreen):

    def __init__(self, navigator, flash_exercise=None,
                 parent: QWidget | None = None):
        super().__init__(navigator, parent)

    def build(self, **kwargs) -> None:
        from neural_speed_academy.exercises.flash import FlashExercise

        def run(low: int, high: int, rounds: int) -> Callable:
            return lambda: self.navigator.launch_exercise(
                FlashExercise, mode="flash_num", rounds=rounds,
                level_func=lambda _: random.randint(low, high),
            )

        sets = [
            ("Fixed: 1 Digit (Instant)", run(1, 1, 10)),
            ("Fixed: 2 Digits", run(2, 2, 10)),
            ("Fixed: 3 Digits", run(3, 3, 10)),
            ("Fixed: 4 Digits", run(4, 4, 10)),
            ("Fixed: 5 Digits", run(5, 5, 12)),
            ("Fixed: 6 Digits", run(6, 6, 12)),
            ("Fixed: 7 Digits", run(7, 7, 15)),
            ("Fixed: 8 Digits", run(8, 8, 15)),
            ("Mix: 2-3 Digits", run(2, 3, 10)),
            ("Mix: 3-4 Digits", run(3, 4, 12)),
            ("Mix: 3-5 Digits", run(3, 5, 12)),
            ("Mix: 4-5 Digits", run(4, 5, 12)),
            ("Mix: 4-6 Digits", run(4, 6, 15)),
            ("Mix: 5-7 Digits", run(5, 7, 15)),
            ("Mix: 6-8 Digits", run(6, 8, 15)),
            ("Chaos: 1-10 Digits", run(1, 10, 20)),
        ]
        self._create_grid_menu("FLASH NUMBER SETS", "flash", sets)


class WordsMenuScreen(BaseMenuScreen):

    def __init__(self, navigator, flash_exercise=None,
                 parent: QWidget | None = None):
        super().__init__(navigator, parent)

    def build(self, **kwargs) -> None:
        from neural_speed_academy.exercises.flash import FlashExercise

        def run(rounds: int) -> Callable:
            return lambda: self.navigator.launch_exercise(
                FlashExercise, mode="flash_word", rounds=rounds,
                level_func=lambda _: 0,
            )

        sets = [
            ("Ambiguous Words (10 Rounds)", run(10)),
            ("Quick Recognition (20 Rounds)", run(20)),
        ]
        self._create_grid_menu("WORD DRILLS", "flash", sets)


class EyespanMenuScreen(BaseMenuScreen):

    def __init__(self, navigator, flash_exercise=None,
                 parent: QWidget | None = None):
        super().__init__(navigator, parent)

    def build(self, **kwargs) -> None:
        from neural_speed_academy.exercises.flash import FlashExercise

        def run(mode: str, width: int, low: int, high: int,
                rounds: int) -> Callable:
            return lambda: self.navigator.launch_exercise(
                FlashExercise, mode="eyespan", rounds=rounds,
                level_func=lambda _: random.randint(low, high),
                span_config={"mode": mode, "width": width},
            )

        self._create_column_menu(
            "EYE-SPAN TRAINING", "eyespan",
            columns=[
                ("HORIZONTAL SCAN", [
                    ("1 Digit (Narrow 30%)", run("h", 30, 1, 1, 10)),
                    ("1 Digit (Medium 50%)", run("h", 50, 1, 1, 10)),
                    ("1 Digit (Wide 70%)", run("h", 70, 1, 1, 10)),
                    ("2 Digits (Narrow 30%)", run("h", 30, 2, 2, 10)),
                    ("2 Digits (Medium 50%)", run("h", 50, 2, 2, 10)),
                    ("2 Digits (Wide 70%)", run("h", 70, 2, 2, 10)),
                    ("3 Digits (Narrow 30%)", run("h", 30, 3, 3, 10)),
                    ("3 Digits (Medium 50%)", run("h", 50, 3, 3, 12)),
                    ("3 Digits (Wide 70%)", run("h", 70, 3, 3, 12)),
                    ("4 Digits (Medium 50%)", run("h", 50, 4, 4, 12)),
                    ("4 Digits (Wide 70%)", run("h", 70, 4, 4, 15)),
                    ("Elite 4 Digits (Max 90%)", run("h", 90, 4, 4, 15)),
                ]),
                ("VERTICAL JUMP", [
                    ("1 Digit (Narrow 30%)", run("v", 30, 1, 1, 10)),
                    ("1 Digit (Medium 50%)", run("v", 50, 1, 1, 10)),
                    ("1 Digit (Wide 70%)", run("v", 70, 1, 1, 10)),
                    ("2 Digits (Narrow 30%)", run("v", 30, 2, 2, 10)),
                    ("2 Digits (Medium 50%)", run("v", 50, 2, 2, 10)),
                    ("2 Digits (Wide 70%)", run("v", 70, 2, 2, 10)),
                    ("3 Digits (Narrow 30%)", run("v", 30, 3, 3, 10)),
                    ("3 Digits (Medium 50%)", run("v", 50, 3, 3, 12)),
                    ("3 Digits (Wide 70%)", run("v", 70, 3, 3, 12)),
                    ("4 Digits (Medium 50%)", run("v", 50, 4, 4, 12)),
                    ("Overlap 2-4 (Wide 80%)", run("v", 80, 2, 4, 15)),
                    ("Elite 4-6 Digits (Max 90%)", run("v", 90, 4, 6, 20)),
                ]),
                ("DYNAMIC MIX", [
                    ("1 Digit (Narrow 30%)", run("m", 30, 1, 1, 10)),
                    ("1 Digit (Medium 50%)", run("m", 50, 1, 1, 10)),
                    ("2 Digits (Medium 50%)", run("m", 50, 2, 2, 12)),
                    ("2 Digits (Wide 70%)", run("m", 70, 2, 2, 12)),
                    ("3 Digits (Medium 50%)", run("m", 50, 3, 3, 12)),
                    ("3 Digits (Wide 70%)", run("m", 70, 3, 3, 12)),
                    ("Overlap 2-3 (Medium 50%)", run("m", 50, 2, 3, 12)),
                    ("Overlap 2-3 (Wide 60%)", run("m", 60, 2, 3, 12)),
                    ("Overlap 3-5 (Wide 70%)", run("m", 70, 3, 5, 15)),
                    ("Wide Range 2-6 (80%)", run("m", 80, 2, 6, 15)),
                    ("Master Chaos 2-8 (90%)", run("m", 90, 2, 8, 20)),
                ]),
            ],
        )


class PrimingMenuScreen(BaseMenuScreen):

    def __init__(self, navigator, priming_exercise=None,
                 parent: QWidget | None = None):
        super().__init__(navigator, parent)

    def build(self, **kwargs) -> None:
        from neural_speed_academy.exercises.priming import PrimingExercise

        def run(mode: str, delay: int = 600, duration_s: float = 45.0,
                cycles: int = 0) -> Callable:
            return lambda: self.navigator.launch_exercise(
                PrimingExercise, mode=mode, delay=delay,
                duration_s=duration_s, cycles=cycles,
            )

        self._create_column_menu(
            "EYE PRIMING", "priming",
            columns=[
                ("SACCADES (JUMPS)", [
                    ("Horizontal Saccades (Slow)", run("saccade_h", delay=700)),
                    ("Horizontal Saccades (Fast)", run("saccade_h", delay=400)),
                    ("Vertical Saccades (Slow)", run("saccade_v", delay=700)),
                    ("Vertical Saccades (Fast)", run("saccade_v", delay=400)),
                    ("Diagonal Saccades (Slow)", run("saccade_diag", delay=700)),
                    ("Diagonal Saccades (Fast)", run("saccade_diag", delay=400)),
                    ("Expanding Saccades (Slow)", run("saccade_expand", delay=700)),
                    ("Expanding Saccades (Fast)", run("saccade_expand", delay=400)),
                ]),
                ("SMOOTH PURSUIT (TRACKING)", [
                    ("Pursuit: Line (Slow)", run("pursuit_line", cycles=9)),
                    ("Pursuit: Line (Fast)", run("pursuit_line", cycles=15)),
                    ("Pursuit: Circle (Slow)", run("pursuit_circle", cycles=9)),
                    ("Pursuit: Circle (Fast)", run("pursuit_circle", cycles=15)),
                    ("Pursuit: Figure-8 (Slow)", run("pursuit_figure8", cycles=9)),
                    ("Pursuit: Figure-8 (Fast)", run("pursuit_figure8", cycles=15)),
                ]),
            ],
        )
