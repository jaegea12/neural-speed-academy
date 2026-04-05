"""
Menu screens for exercise selection.
"""
from __future__ import annotations

import random

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
)
from PyQt6.QtCore import Qt

from neural_speed_academy.screens.base import BaseScreen
from neural_speed_academy.theme import COLORS, make_qfont, btn_css


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

    def _create_two_panel_menu(
        self,
        title: str,
        guide_key: str,
        exercise_cls,
        *,
        left_label: str,
        presets: list[tuple[str, dict]],
        params: list[tuple[str, str, list, object]],
        default_preset: int = 0,
        left_stretch: int = 1,
        right_stretch: int = 1,
    ) -> None:
        """Build a two-panel config screen.

        Args:
            title: Screen title.
            guide_key: Key for the guide dialog.
            exercise_cls: Exercise class to launch.
            left_label: Header for the left panel.
            presets: List of (label, {param_key: value, ...}) tuples.
                     Selecting a preset updates the right-panel defaults.
            params: List of (header, param_key, options, default) tuples.
                    Each option is a (label, value) pair.
                    Displayed as a row of toggle buttons on the right panel.
            default_preset: Index of the initially selected preset.
            left_stretch: Stretch factor for the left panel.
            right_stretch: Stretch factor for the right panel.
        """
        from neural_speed_academy.screens.base import make_scroll_area

        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")
        self.add_nav_bar()

        scroll, container, cl = make_scroll_area(self._layout)
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
        guide_btn.setStyleSheet(
            btn_css(c["accent"], c["btn_text"], padding="6px 16px",
                    font_key="btn_sm")
        )
        guide_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        guide_btn.clicked.connect(lambda: self.show_guide(guide_key))
        title_row.addWidget(guide_btn)
        title_row.addStretch()
        cl.addLayout(title_row)

        cl.addSpacing(10)

        # Two-column layout
        columns = QHBoxLayout()
        columns.setSpacing(40)
        columns.setContentsMargins(20, 0, 20, 0)

        # ── Left panel: presets ──
        left = QVBoxLayout()
        left.setSpacing(6)

        left_hdr = QLabel(left_label)
        left_hdr.setFont(make_qfont("menu_header"))
        left_hdr.setStyleSheet(f"color: {c['accent']};")
        left_hdr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left.addWidget(left_hdr)

        self._tp_preset_buttons: list[QPushButton] = []
        self._tp_presets = presets
        self._tp_selected_preset = default_preset

        for i, (preset_label, _preset_vals) in enumerate(presets):
            color_key = self._difficulty_color(i, len(presets))
            btn = QPushButton(preset_label)
            btn.setFont(make_qfont("menu_btn"))
            btn.setFixedHeight(38)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(
                lambda _, idx=i: self._tp_select_preset(idx)
            )
            left.addWidget(btn)
            self._tp_preset_buttons.append(btn)

        left.addStretch()
        columns.addLayout(left, left_stretch)

        # ── Right panel: adjustable parameters ──
        right = QVBoxLayout()
        right.setSpacing(8)

        self._tp_param_buttons: dict[str, dict] = {}
        self._tp_param_values: dict[str, object] = {}
        self._tp_params = params

        for header, param_key, options, default in params:
            hdr = QLabel(header)
            hdr.setFont(make_qfont("menu_header"))
            hdr.setStyleSheet(f"color: {c['accent']};")
            hdr.setAlignment(Qt.AlignmentFlag.AlignCenter)
            right.addWidget(hdr)

            row = QHBoxLayout()
            row.setSpacing(6)
            btns: dict = {}
            for opt_label, opt_value in options:
                btn = QPushButton(opt_label)
                btn.setFont(make_qfont("btn_sm"))
                btn.setFixedHeight(36)
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.clicked.connect(
                    lambda _, k=param_key, v=opt_value: self._tp_select_param(k, v)
                )
                row.addWidget(btn)
                btns[opt_value] = btn
            right.addLayout(row)
            right.addSpacing(4)

            self._tp_param_buttons[param_key] = btns
            self._tp_param_values[param_key] = default

        right.addSpacing(12)

        # START button
        start_btn = QPushButton("START")
        start_btn.setFont(make_qfont("btn_lg"))
        start_btn.setStyleSheet(
            btn_css(c["accent"], c["btn_text"], padding="12px 50px")
        )
        start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        start_btn.clicked.connect(
            lambda: self._tp_launch(exercise_cls)
        )
        right.addWidget(start_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        right.addStretch()
        columns.addLayout(right, right_stretch)

        cl.addLayout(columns)
        cl.addStretch()

        # Apply initial state
        self._tp_select_preset(default_preset)

    def _tp_toggle_on(self) -> str:
        c = COLORS
        return btn_css(c["accent"], c["btn_text"], padding="6px 14px")

    def _tp_toggle_off(self) -> str:
        c = COLORS
        return (
            f"QPushButton {{ background-color: {c['card']}; "
            f"color: {c['fg']}; border: 2px solid {c['muted']}; "
            f"padding: 6px 14px; border-radius: 4px; }}"
            f"QPushButton:hover {{ background-color: {c['accent']}; "
            f"color: {c['btn_text']}; border-color: {c['accent']}; }}"
            f"QPushButton:focus {{ border-color: {c['accent']}; }}"
        )

    def _tp_select_preset(self, idx: int) -> None:
        self._tp_selected_preset = idx
        c = COLORS
        # Update left panel buttons
        for i, btn in enumerate(self._tp_preset_buttons):
            if i == idx:
                btn.setStyleSheet(self._tp_toggle_on())
            else:
                color_key = self._difficulty_color(i, len(self._tp_preset_buttons))
                btn.setStyleSheet(
                    btn_css(c[color_key], c["btn_text"], padding="6px 14px")
                )
        # Apply preset defaults to right panel
        _, preset_vals = self._tp_presets[idx]
        for key, value in preset_vals.items():
            if key in self._tp_param_buttons:
                self._tp_select_param(key, value)
        # Style any param buttons not covered by this preset
        for header, param_key, options, default in self._tp_params:
            if param_key not in preset_vals:
                self._tp_select_param(param_key, self._tp_param_values[param_key])

    def _tp_select_param(self, key: str, value: object) -> None:
        self._tp_param_values[key] = value
        btns = self._tp_param_buttons.get(key, {})
        for v, btn in btns.items():
            if v == value:
                btn.setStyleSheet(self._tp_toggle_on())
            else:
                btn.setStyleSheet(self._tp_toggle_off())

    def _tp_launch(self, exercise_cls) -> None:
        kwargs = dict(self._tp_param_values)
        # Add any preset-only values not covered by param buttons
        _, preset_vals = self._tp_presets[self._tp_selected_preset]
        for key, value in preset_vals.items():
            if key not in self._tp_param_buttons:
                kwargs[key] = value
        self.navigator.launch_exercise(exercise_cls, **kwargs)


class FlashMenuScreen(BaseMenuScreen):

    def __init__(self, navigator, flash_exercise=None,
                 parent: QWidget | None = None):
        super().__init__(navigator, parent)

    def build(self, **kwargs) -> None:
        self._create_two_panel_menu(
            "FLASH NUMBERS", "flash", None,
            left_label="DIGITS",
            presets=[
                ("1 Digit",   {"low": 1, "high": 1, "rounds": 10}),
                ("2 Digits",  {"low": 2, "high": 2, "rounds": 10}),
                ("3 Digits",  {"low": 3, "high": 3, "rounds": 10}),
                ("4 Digits",  {"low": 4, "high": 4, "rounds": 12}),
                ("5 Digits",  {"low": 5, "high": 5, "rounds": 12}),
                ("6 Digits",  {"low": 6, "high": 6, "rounds": 15}),
                ("7 Digits",  {"low": 7, "high": 7, "rounds": 15}),
                ("8 Digits",  {"low": 8, "high": 8, "rounds": 15}),
            ],
            params=[
                ("RANGE", "range_mode", [
                    ("Fixed", "fixed"),
                    ("Mix ±1", "mix1"),
                    ("Mix ±2", "mix2"),
                    ("Chaos", "chaos"),
                ], "fixed"),
                ("ROUNDS", "rounds", [
                    ("10", 10), ("12", 12), ("15", 15), ("20", 20),
                ], 10),
            ],
            default_preset=2,
        )

    def _tp_launch(self, exercise_cls) -> None:
        from neural_speed_academy.exercises.flash import FlashExercise

        _, preset_vals = self._tp_presets[self._tp_selected_preset]
        base_low = preset_vals["low"]
        base_high = preset_vals["high"]
        range_mode = self._tp_param_values.get("range_mode", "fixed")
        rounds = self._tp_param_values.get("rounds", 10)

        if range_mode == "fixed":
            low, high = base_low, base_high
        elif range_mode == "mix1":
            low = max(1, base_low - 1)
            high = base_high + 1
        elif range_mode == "mix2":
            low = max(1, base_low - 2)
            high = base_high + 2
        else:  # chaos
            low, high = 1, 10

        self.navigator.launch_exercise(
            FlashExercise, mode="flash_num", rounds=rounds,
            level_func=lambda _: random.randint(low, high),
        )


class WordsMenuScreen(BaseMenuScreen):

    def __init__(self, navigator, flash_exercise=None,
                 parent: QWidget | None = None):
        super().__init__(navigator, parent)

    def build(self, **kwargs) -> None:
        self._create_two_panel_menu(
            "WORD DRILLS", "flash", None,
            left_label="MODE",
            presets=[
                ("Ambiguous Words", {"mode": "flash_word"}),
            ],
            params=[
                ("ROUNDS", "rounds", [
                    ("10", 10), ("15", 15), ("20", 20), ("30", 30),
                ], 10),
            ],
            default_preset=0,
        )

    def _tp_launch(self, exercise_cls) -> None:
        from neural_speed_academy.exercises.flash import FlashExercise

        rounds = self._tp_param_values.get("rounds", 10)
        self.navigator.launch_exercise(
            FlashExercise, mode="flash_word", rounds=rounds,
            level_func=lambda _: 0,
        )


class EyespanMenuScreen(BaseMenuScreen):

    def __init__(self, navigator, flash_exercise=None,
                 parent: QWidget | None = None):
        super().__init__(navigator, parent)

    def build(self, **kwargs) -> None:
        self._create_two_panel_menu(
            "EYE-SPAN TRAINING", "eyespan", None,
            left_label="DIGITS",
            presets=[
                ("1 Digit",  {"low": 1, "high": 1, "rounds": 10}),
                ("2 Digits", {"low": 2, "high": 2, "rounds": 10}),
                ("3 Digits", {"low": 3, "high": 3, "rounds": 12}),
                ("4 Digits", {"low": 4, "high": 4, "rounds": 12}),
                ("5 Digits", {"low": 5, "high": 5, "rounds": 15}),
                ("6 Digits", {"low": 6, "high": 6, "rounds": 15}),
            ],
            params=[
                ("DIRECTION", "direction", [
                    ("Horizontal", "h"),
                    ("Vertical", "v"),
                    ("Mixed", "m"),
                ], "h"),
                ("WIDTH", "width", [
                    ("Narrow 30%", 30),
                    ("Medium 50%", 50),
                    ("Wide 70%", 70),
                    ("Max 90%", 90),
                ], 50),
                ("ROUNDS", "rounds", [
                    ("10", 10), ("12", 12), ("15", 15), ("20", 20),
                ], 10),
            ],
            default_preset=1,
        )

    def _tp_launch(self, exercise_cls) -> None:
        from neural_speed_academy.exercises.flash import FlashExercise

        _, preset_vals = self._tp_presets[self._tp_selected_preset]
        low = preset_vals["low"]
        high = preset_vals["high"]
        direction = self._tp_param_values.get("direction", "h")
        width = self._tp_param_values.get("width", 50)
        rounds = self._tp_param_values.get("rounds", 10)

        self.navigator.launch_exercise(
            FlashExercise, mode="eyespan", rounds=rounds,
            level_func=lambda _: random.randint(low, high),
            span_config={"mode": direction, "width": width},
        )


class SchulteMenuScreen(BaseMenuScreen):

    def __init__(self, navigator, parent: QWidget | None = None):
        super().__init__(navigator, parent)

    def build(self, **kwargs) -> None:
        self._create_two_panel_menu(
            "SCHULTE GRID", "schulte", None,
            left_label="GRID SIZE",
            presets=[
                ("3×3  (9)",   {"grid_size": 3}),
                ("4×4  (16)",  {"grid_size": 4}),
                ("5×5  (25)",  {"grid_size": 5}),
                ("6×6  (36)",  {"grid_size": 6}),
                ("7×7  (49)",  {"grid_size": 7}),
            ],
            params=[
                ("CELL SIZE", "cell_idx", [
                    ("Small", 0), ("Medium", 1), ("Large", 2), ("XL", 3),
                ], 1),
            ],
            default_preset=2,
        )

    def _tp_launch(self, exercise_cls) -> None:
        from neural_speed_academy.exercises.schulte import SchulteExercise

        _, preset_vals = self._tp_presets[self._tp_selected_preset]
        grid_size = preset_vals["grid_size"]
        cell_idx = self._tp_param_values.get("cell_idx", 1)

        self.navigator.launch_exercise(
            SchulteExercise, grid_size=grid_size, cell_idx=cell_idx,
        )


class PrimingMenuScreen(BaseMenuScreen):

    def __init__(self, navigator, priming_exercise=None,
                 parent: QWidget | None = None):
        super().__init__(navigator, parent)

    def build(self, **kwargs) -> None:
        self._create_two_panel_menu(
            "EYE PRIMING", "priming", None,
            left_label="EXERCISE",
            presets=[
                ("Horizontal Saccades", {"mode": "saccade_h", "use_delay": True}),
                ("Vertical Saccades",   {"mode": "saccade_v", "use_delay": True}),
                ("Diagonal Saccades",   {"mode": "saccade_diag", "use_delay": True}),
                ("Expanding Saccades",  {"mode": "saccade_expand", "use_delay": True}),
                ("Pursuit: Line",       {"mode": "pursuit_line", "use_delay": False}),
                ("Pursuit: Circle",     {"mode": "pursuit_circle", "use_delay": False}),
                ("Pursuit: Figure-8",   {"mode": "pursuit_figure8", "use_delay": False}),
            ],
            params=[
                ("SPEED", "speed", [
                    ("Slow", "slow"), ("Fast", "fast"),
                ], "slow"),
                ("DURATION", "duration_s", [
                    ("30s", 30.0), ("45s", 45.0), ("60s", 60.0),
                ], 45.0),
            ],
            default_preset=0,
        )

    def _tp_launch(self, exercise_cls) -> None:
        from neural_speed_academy.exercises.priming import PrimingExercise

        _, preset_vals = self._tp_presets[self._tp_selected_preset]
        mode = preset_vals["mode"]
        use_delay = preset_vals["use_delay"]
        speed = self._tp_param_values.get("speed", "slow")
        duration_s = self._tp_param_values.get("duration_s", 45.0)

        if use_delay:
            delay = 700 if speed == "slow" else 400
            self.navigator.launch_exercise(
                PrimingExercise, mode=mode, delay=delay,
                duration_s=duration_s,
            )
        else:
            cycles = 9 if speed == "slow" else 15
            self.navigator.launch_exercise(
                PrimingExercise, mode=mode, cycles=cycles,
                duration_s=duration_s,
            )


class PeripheralFlashMenuScreen(BaseMenuScreen):

    def __init__(self, navigator, parent: QWidget | None = None):
        super().__init__(navigator, parent)

    def build(self, **kwargs) -> None:
        self._create_two_panel_menu(
            "PERIPHERAL FLASH", "peripheral_flash", None,
            left_label="DIFFICULTY",
            presets=[
                ("Beginner",     {"flash_ms": 100, "eccentricity": 30}),
                ("Easy",         {"flash_ms": 100, "eccentricity": 50}),
                ("Moderate",     {"flash_ms": 80,  "eccentricity": 50}),
                ("Challenging",  {"flash_ms": 80,  "eccentricity": 70}),
                ("Hard",         {"flash_ms": 60,  "eccentricity": 70}),
                ("Expert",       {"flash_ms": 50,  "eccentricity": 80}),
                ("Elite",        {"flash_ms": 50,  "eccentricity": 90}),
            ],
            params=[
                ("TYPE", "stim_type", [
                    ("Letters", "letters"),
                    ("Numbers", "numbers"),
                    ("Shapes", "shapes"),
                ], "letters"),
                ("FLASH TIME", "flash_ms", [
                    ("100ms", 100), ("80ms", 80), ("60ms", 60), ("50ms", 50),
                ], 100),
                ("ECCENTRICITY", "eccentricity", [
                    ("30%", 30), ("50%", 50), ("70%", 70),
                    ("80%", 80), ("90%", 90),
                ], 50),
                ("ROUNDS", "rounds", [
                    ("10", 10), ("15", 15), ("20", 20), ("25", 25),
                ], 15),
            ],
            default_preset=1,
        )

    def _tp_launch(self, exercise_cls) -> None:
        from neural_speed_academy.exercises.peripheral_flash import (
            PeripheralFlashExercise,
        )
        self.navigator.launch_exercise(
            PeripheralFlashExercise,
            stim_type=self._tp_param_values.get("stim_type", "letters"),
            flash_ms=self._tp_param_values.get("flash_ms", 100),
            eccentricity=self._tp_param_values.get("eccentricity", 50),
            rounds=self._tp_param_values.get("rounds", 15),
        )


class RapidDecisionMenuScreen(BaseMenuScreen):

    def __init__(self, navigator, parent: QWidget | None = None):
        super().__init__(navigator, parent)

    def build(self, **kwargs) -> None:
        self._create_two_panel_menu(
            "RAPID DECISION GRID", "rapid_decision", None,
            left_label="GRID SIZE",
            presets=[
                ("3\u00d73",  {"grid_size": 3}),
                ("4\u00d74",  {"grid_size": 4}),
                ("5\u00d75",  {"grid_size": 5}),
                ("6\u00d76",  {"grid_size": 6}),
                ("7\u00d77",  {"grid_size": 7}),
            ],
            params=[
                ("MODE", "mode", [
                    ("Ascending", "ascending"),
                    ("Descending", "descending"),
                    ("Even Only", "even_only"),
                    ("Odd Only", "odd_only"),
                    ("Alternating", "alternating"),
                ], "ascending"),
                ("TIME LIMIT", "time_limit", [
                    ("None", 0), ("60s", 60), ("45s", 45), ("30s", 30),
                ], 0),
            ],
            default_preset=2,
        )

    def _tp_launch(self, exercise_cls) -> None:
        from neural_speed_academy.exercises.rapid_decision import (
            RapidDecisionGridExercise,
        )
        _, preset_vals = self._tp_presets[self._tp_selected_preset]
        self.navigator.launch_exercise(
            RapidDecisionGridExercise,
            mode=self._tp_param_values.get("mode", "ascending"),
            grid_size=preset_vals["grid_size"],
            time_limit=self._tp_param_values.get("time_limit", 0),
        )


class MotMenuScreen(BaseMenuScreen):

    def __init__(self, navigator, parent: QWidget | None = None):
        super().__init__(navigator, parent)

    def build(self, **kwargs) -> None:
        self._create_two_panel_menu(
            "MULTIPLE OBJECT TRACKING", "mot", None,
            left_label="TARGETS",
            presets=[
                ("2 Targets", {"targets": 2, "distractors": 4, "speed": 2}),
                ("3 Targets", {"targets": 3, "distractors": 5, "speed": 3}),
                ("4 Targets", {"targets": 4, "distractors": 6, "speed": 3}),
                ("5 Targets", {"targets": 5, "distractors": 7, "speed": 4}),
                ("6 Targets", {"targets": 6, "distractors": 8, "speed": 5}),
            ],
            params=[
                ("SPEED", "speed", [
                    ("2 (Slow)", 2), ("3", 3), ("4", 4),
                    ("5 (Fast)", 5), ("6 (Sprint)", 6),
                ], 3),
                ("DURATION", "duration", [
                    ("5s", 5), ("6s", 6), ("7s", 7),
                    ("8s", 8), ("10s", 10),
                ], 6),
                ("ROUNDS", "rounds", [
                    ("5", 5), ("7", 7), ("10", 10),
                ], 5),
            ],
            default_preset=1,
        )

    def _tp_launch(self, exercise_cls) -> None:
        from neural_speed_academy.exercises.mot import MotExercise

        _, preset_vals = self._tp_presets[self._tp_selected_preset]
        self.navigator.launch_exercise(
            MotExercise,
            targets=preset_vals["targets"],
            distractors=preset_vals["distractors"],
            speed=self._tp_param_values.get("speed", 3),
            duration=self._tp_param_values.get("duration", 6),
            rounds=self._tp_param_values.get("rounds", 5),
        )


class SlideProcessingMenuScreen(BaseMenuScreen):

    def __init__(self, navigator, parent: QWidget | None = None):
        super().__init__(navigator, parent)
        self._selected_categories: set[str] = set()
        self._selected_custom: set[str] = set()  # filenames of selected custom sets
        self._selected_time: int = 10
        self._selected_slides: int = 5
        self._selected_lines: int = 6
        self._cat_buttons: dict[str, QPushButton] = {}
        self._custom_buttons: dict[str, QPushButton] = {}  # filename -> btn
        self._custom_sets: dict[str, object] = {}  # filename -> SlideSet
        self._time_buttons: dict[int, QPushButton] = {}
        self._slide_buttons: dict[int, QPushButton] = {}
        self._lines_buttons: dict[int, QPushButton] = {}

    def build(self, **kwargs) -> None:
        from neural_speed_academy.exercises.slide_processing import (
            SlideProcessingExercise,
        )

        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")
        self.add_nav_bar()

        container = QWidget()
        container.setStyleSheet(f"background-color: {c['bg']};")
        cl = QVBoxLayout(container)
        cl.setContentsMargins(30, 20, 30, 20)
        cl.setSpacing(10)

        # Title row
        title_row = QHBoxLayout()
        title_row.addStretch()
        title_lbl = QLabel("SLIDE PROCESSING")
        title_lbl.setFont(make_qfont("header"))
        title_lbl.setStyleSheet(f"color: {c['fg']};")
        title_row.addWidget(title_lbl)

        guide_btn = QPushButton("GUIDE")
        guide_btn.setFont(make_qfont("btn_sm"))
        guide_btn.setStyleSheet(
            f"background-color: {c['accent']}; color: {c['btn_text']}; "
            f"border: 2px solid transparent; padding: 6px 16px; border-radius: 4px;"
        )
        guide_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        guide_btn.clicked.connect(
            lambda: self.show_guide("slide_processing")
        )
        title_row.addWidget(guide_btn)
        title_row.addStretch()
        cl.addLayout(title_row)

        cl.addStretch()

        # Two-column layout: categories (2/3) | options (1/3)
        columns = QHBoxLayout()
        columns.setSpacing(40)
        columns.setContentsMargins(20, 0, 20, 0)

        # ── Left: Categories (single column) ──
        left = QVBoxLayout()
        left.setSpacing(8)

        cat_header = QLabel("CATEGORIES")
        cat_header.setFont(make_qfont("menu_header"))
        cat_header.setStyleSheet(f"color: {c['accent']};")
        cat_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left.addWidget(cat_header)

        categories = [
            ("Science", "science"),
            ("Business", "business"),
            ("Geography", "geography"),
            ("Motivation", "motivation"),
            ("Neuroplasticity", "neuroplasticity"),
            ("Humor", "humor"),
            ("History", "history"),
            ("Nutrition", "nutrition"),
        ]

        for label, key in categories:
            btn = QPushButton(label)
            btn.setFont(make_qfont("menu_btn"))
            btn.setFixedHeight(40)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(self._toggle_off_style())
            btn.clicked.connect(
                lambda _, k=key: self._toggle_category(k)
            )
            left.addWidget(btn)
            self._cat_buttons[key] = btn

        # Select All / Clear — centered, compact
        sel_row = QHBoxLayout()
        sel_row.addStretch()
        sel_all = QPushButton("Select All")
        sel_all.setFont(make_qfont("btn_sm"))
        sel_all.setStyleSheet(
            f"color: {c['accent']}; background: transparent; "
            f"border: 2px solid transparent; padding: 4px 10px;"
        )
        sel_all.setCursor(Qt.CursorShape.PointingHandCursor)
        sel_all.clicked.connect(self._select_all_categories)
        sel_row.addWidget(sel_all)

        sep_lbl = QLabel("·")
        sep_lbl.setStyleSheet(f"color: {c['muted']};")
        sel_row.addWidget(sep_lbl)

        sel_clear = QPushButton("Clear")
        sel_clear.setFont(make_qfont("btn_sm"))
        sel_clear.setStyleSheet(
            f"color: {c['muted']}; background: transparent; "
            f"border: 2px solid transparent; padding: 4px 10px;"
        )
        sel_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        sel_clear.clicked.connect(self._clear_categories)
        sel_row.addWidget(sel_clear)
        sel_row.addStretch()
        left.addLayout(sel_row)

        # ── Custom slide sets ──
        from neural_speed_academy.repositories.slide_repository import (
            SlideSetRepository,
        )
        repo = SlideSetRepository()
        custom_sets = repo.list_sets()
        if custom_sets:
            left.addSpacing(8)
            custom_header = QLabel("CUSTOM SETS")
            custom_header.setFont(make_qfont("menu_header"))
            custom_header.setStyleSheet(f"color: {c['accent']};")
            custom_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
            left.addWidget(custom_header)

            for ss in custom_sets:
                btn = QPushButton(f"{ss.name}  ({len(ss.slides)})")
                btn.setFont(make_qfont("menu_btn"))
                btn.setFixedHeight(40)
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.setStyleSheet(self._toggle_off_style())
                btn.clicked.connect(
                    lambda _, f=ss.filename: self._toggle_custom(f)
                )
                left.addWidget(btn)
                self._custom_buttons[ss.filename] = btn
                self._custom_sets[ss.filename] = ss

        # Create / Edit slides button
        left.addSpacing(6)
        create_btn = QPushButton("CREATE / EDIT SLIDES")
        create_btn.setFont(make_qfont("menu_btn"))
        create_btn.setFixedHeight(40)
        create_btn.setStyleSheet(
            btn_css(c["muted"], c["bg"], padding="6px 14px")
        )
        create_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        create_btn.clicked.connect(
            lambda: self.navigator.navigate_to("slide_creator")
        )
        left.addWidget(create_btn)

        left.addStretch()

        # Give left column stretch factor 2 (2/3 of space)
        columns.addLayout(left, 2)

        # ── Right: Options ──
        right = QVBoxLayout()
        right.setSpacing(8)

        # Display time
        time_header = QLabel("DISPLAY TIME")
        time_header.setFont(make_qfont("menu_header"))
        time_header.setStyleSheet(f"color: {c['accent']};")
        time_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right.addWidget(time_header)

        time_options = [15, 12, 10, 8, 6, 5, 4, 3]
        for t in time_options:
            btn = QPushButton(f"{t} seconds")
            btn.setFont(make_qfont("menu_btn"))
            btn.setFixedHeight(40)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(self._toggle_off_style())
            btn.clicked.connect(
                lambda _, v=t: self._select_time(v)
            )
            right.addWidget(btn)
            self._time_buttons[t] = btn

        right.addSpacing(10)

        # Slides per session
        slides_header = QLabel("SLIDES PER SESSION")
        slides_header.setFont(make_qfont("menu_header"))
        slides_header.setStyleSheet(f"color: {c['accent']};")
        slides_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right.addWidget(slides_header)

        slide_options = [3, 5, 8, 10]
        slide_row = QHBoxLayout()
        slide_row.setSpacing(8)
        for s in slide_options:
            btn = QPushButton(str(s))
            btn.setFont(make_qfont("menu_btn"))
            btn.setFixedSize(60, 40)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(self._toggle_off_style())
            btn.clicked.connect(
                lambda _, v=s: self._select_slides(v)
            )
            slide_row.addWidget(btn)
            self._slide_buttons[s] = btn
        right.addLayout(slide_row)

        right.addSpacing(10)

        # Lines per slide
        lines_header = QLabel("LINES PER SLIDE")
        lines_header.setFont(make_qfont("menu_header"))
        lines_header.setStyleSheet(f"color: {c['accent']};")
        lines_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right.addWidget(lines_header)

        lines_options = [3, 4, 5, 6]
        lines_row = QHBoxLayout()
        lines_row.setSpacing(8)
        for n in lines_options:
            btn = QPushButton(str(n))
            btn.setFont(make_qfont("menu_btn"))
            btn.setFixedSize(60, 40)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(self._toggle_off_style())
            btn.clicked.connect(
                lambda _, v=n: self._select_lines(v)
            )
            lines_row.addWidget(btn)
            self._lines_buttons[n] = btn
        right.addLayout(lines_row)

        right.addSpacing(20)

        # START button — at bottom of right column
        start_btn = QPushButton("START")
        start_btn.setFont(make_qfont("btn_lg"))
        start_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['accent']}; "
            f"color: {c['btn_text']}; border: 2px solid transparent; "
            f"padding: 12px 50px; border-radius: 4px; }}"
        )
        start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        start_btn.clicked.connect(
            lambda: self._launch(SlideProcessingExercise)
        )
        right.addWidget(start_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # Give right column stretch factor 1 (1/3 of space)
        columns.addLayout(right, 1)

        cl.addLayout(columns)

        cl.addStretch()
        self._layout.addWidget(container, 1)

        # Restore previous selections (persist across build calls)
        self._select_time(self._selected_time)
        self._select_slides(self._selected_slides)
        self._select_lines(self._selected_lines)
        if self._selected_categories:
            for key in list(self._selected_categories):
                if key in self._cat_buttons:
                    self._cat_buttons[key].setStyleSheet(
                        self._toggle_on_style()
                    )
        elif not self._selected_custom:
            # First visit: default to first category
            self._toggle_category("science")
        # Restore custom set selections
        for fname in list(self._selected_custom):
            if fname in self._custom_buttons:
                self._custom_buttons[fname].setStyleSheet(
                    self._toggle_on_style()
                )

    def _toggle_on_style(self) -> str:
        c = COLORS
        return (
            f"QPushButton {{ background-color: {c['accent']}; "
            f"color: {c['btn_text']}; border: 2px solid transparent; "
            f"padding: 6px 14px; border-radius: 4px; }}"
        )

    def _toggle_off_style(self) -> str:
        c = COLORS
        return (
            f"QPushButton {{ background-color: {c['card']}; "
            f"color: {c['fg']}; border: 1px solid {c['muted']}; "
            f"padding: 6px 14px; border-radius: 4px; }}"
            f"QPushButton:hover {{ background-color: {c['accent']}; "
            f"color: {c['btn_text']}; }}"
        )

    def _toggle_category(self, key: str) -> None:
        if key in self._selected_categories:
            self._selected_categories.discard(key)
            self._cat_buttons[key].setStyleSheet(self._toggle_off_style())
        else:
            self._selected_categories.add(key)
            self._cat_buttons[key].setStyleSheet(self._toggle_on_style())

    def _toggle_custom(self, filename: str) -> None:
        if filename in self._selected_custom:
            self._selected_custom.discard(filename)
            self._custom_buttons[filename].setStyleSheet(self._toggle_off_style())
        else:
            self._selected_custom.add(filename)
            self._custom_buttons[filename].setStyleSheet(self._toggle_on_style())

    def _select_all_categories(self) -> None:
        for key, btn in self._cat_buttons.items():
            self._selected_categories.add(key)
            btn.setStyleSheet(self._toggle_on_style())

    def _clear_categories(self) -> None:
        for key, btn in self._cat_buttons.items():
            self._selected_categories.discard(key)
            btn.setStyleSheet(self._toggle_off_style())
        for fname, btn in self._custom_buttons.items():
            self._selected_custom.discard(fname)
            btn.setStyleSheet(self._toggle_off_style())

    def _select_time(self, t: int) -> None:
        self._selected_time = t
        for v, btn in self._time_buttons.items():
            if v == t:
                btn.setStyleSheet(self._toggle_on_style())
            else:
                btn.setStyleSheet(self._toggle_off_style())

    def _select_slides(self, s: int) -> None:
        self._selected_slides = s
        for v, btn in self._slide_buttons.items():
            if v == s:
                btn.setStyleSheet(self._toggle_on_style())
            else:
                btn.setStyleSheet(self._toggle_off_style())

    def _select_lines(self, n: int) -> None:
        self._selected_lines = n
        for v, btn in self._lines_buttons.items():
            if v == n:
                btn.setStyleSheet(self._toggle_on_style())
            else:
                btn.setStyleSheet(self._toggle_off_style())

    def _launch(self, exercise_cls) -> None:
        cats = list(self._selected_categories)
        if not cats and not self._selected_custom:
            cats = list(self._cat_buttons.keys())

        # Collect custom slide tuples
        custom_slides = []
        for fname in self._selected_custom:
            ss = self._custom_sets.get(fname)
            if ss:
                custom_slides.extend(ss.to_library_format())

        kwargs = {
            "display_s": self._selected_time,
            "slides": self._selected_slides,
            "lines": self._selected_lines,
        }
        if cats:
            kwargs["category"] = ",".join(cats)
        if custom_slides:
            kwargs["custom_slides"] = custom_slides
        if not cats and custom_slides:
            kwargs["category"] = "custom_only"
            kwargs["skip_config"] = True

        self.navigator.launch_exercise(exercise_cls, **kwargs)


class ReactionTimeMenuScreen(BaseMenuScreen):

    def __init__(self, navigator, parent: QWidget | None = None):
        super().__init__(navigator, parent)

    def build(self, **kwargs) -> None:
        self._create_two_panel_menu(
            "REACTION TIME", "reaction_time", None,
            left_label="MODE",
            presets=[
                ("Simple",     {"mode": "simple",    "go_ratio": 1.0}),
                ("Choice",     {"mode": "choice",    "go_ratio": 1.0}),
                ("Go / No-Go", {"mode": "go_no_go",  "go_ratio": 0.7}),
            ],
            params=[
                ("ROUNDS", "rounds", [
                    ("10", 10), ("15", 15), ("20", 20),
                    ("25", 25), ("30", 30),
                ], 15),
                ("GO RATIO (Go/No-Go)", "go_ratio", [
                    ("70/30", 0.7), ("60/40", 0.6), ("50/50", 0.5),
                ], 0.7),
            ],
            default_preset=0,
        )

    def _tp_launch(self, exercise_cls) -> None:
        from neural_speed_academy.exercises.reaction_time import (
            ReactionTimeExercise,
        )
        _, preset_vals = self._tp_presets[self._tp_selected_preset]
        mode = preset_vals["mode"]
        go_ratio = self._tp_param_values.get("go_ratio", 0.7)
        if mode != "go_no_go":
            go_ratio = 1.0
        self.navigator.launch_exercise(
            ReactionTimeExercise,
            mode=mode,
            rounds=self._tp_param_values.get("rounds", 15),
            go_ratio=go_ratio,
        )


class SplitAttentionMenuScreen(BaseMenuScreen):

    def __init__(self, navigator, parent: QWidget | None = None):
        super().__init__(navigator, parent)

    def build(self, **kwargs) -> None:
        self._create_two_panel_menu(
            "SPLIT ATTENTION", "split_attention", None,
            left_label="DIFFICULTY",
            presets=[
                ("Beginner",    {"center_ms": 150, "peripheral_ms": 120}),
                ("Easy",        {"center_ms": 120, "peripheral_ms": 100}),
                ("Moderate",    {"center_ms": 100, "peripheral_ms": 80}),
                ("Challenging", {"center_ms": 80,  "peripheral_ms": 60}),
                ("Hard",        {"center_ms": 60,  "peripheral_ms": 50}),
                ("Expert",      {"center_ms": 50,  "peripheral_ms": 40}),
                ("Elite",       {"center_ms": 40,  "peripheral_ms": 40}),
            ],
            params=[
                ("MODE", "mode", [
                    ("Sequential", "sequential"),
                    ("Simultaneous", "simultaneous"),
                    ("Rapid", "rapid"),
                ], "sequential"),
                ("ROUNDS", "rounds", [
                    ("10", 10), ("15", 15), ("20", 20), ("25", 25),
                ], 15),
            ],
            default_preset=1,
        )

    def _tp_launch(self, exercise_cls) -> None:
        from neural_speed_academy.exercises.split_attention import (
            SplitAttentionExercise,
        )
        _, preset_vals = self._tp_presets[self._tp_selected_preset]
        self.navigator.launch_exercise(
            SplitAttentionExercise,
            mode=self._tp_param_values.get("mode", "sequential"),
            center_ms=preset_vals["center_ms"],
            peripheral_ms=preset_vals["peripheral_ms"],
            rounds=self._tp_param_values.get("rounds", 15),
        )


class SequenceMemoryMenuScreen(BaseMenuScreen):

    def __init__(self, navigator, parent: QWidget | None = None):
        super().__init__(navigator, parent)

    def build(self, **kwargs) -> None:
        self._create_two_panel_menu(
            "SEQUENCE MEMORY", "sequence_memory", None,
            left_label="LENGTH",
            presets=[
                ("3 Items", {"start_length": 3, "flash_ms": 1000}),
                ("4 Items", {"start_length": 4, "flash_ms": 800}),
                ("5 Items", {"start_length": 5, "flash_ms": 700}),
                ("6 Items", {"start_length": 6, "flash_ms": 500}),
                ("7+ Items", {"start_length": 7, "flash_ms": 400}),
            ],
            params=[
                ("MODE", "mode", [
                    ("Numbers", "numbers"),
                    ("Words", "words"),
                    ("Mixed", "mixed"),
                ], "numbers"),
                ("SPEED", "flash_ms", [
                    ("Slow (1s)", 1000),
                    ("Normal (800ms)", 800),
                    ("Fast (500ms)", 500),
                    ("Sprint (400ms)", 400),
                ], 800),
                ("ROUNDS", "rounds", [
                    ("10", 10), ("12", 12), ("15", 15), ("20", 20),
                ], 10),
            ],
            default_preset=1,
        )

    def _tp_launch(self, exercise_cls) -> None:
        from neural_speed_academy.exercises.sequence_memory import (
            SequenceMemoryExercise,
        )

        _, preset_vals = self._tp_presets[self._tp_selected_preset]
        start_length = preset_vals["start_length"]
        mode = self._tp_param_values.get("mode", "numbers")
        flash_ms = self._tp_param_values.get("flash_ms", 800)
        rounds = self._tp_param_values.get("rounds", 10)

        self.navigator.launch_exercise(
            SequenceMemoryExercise, mode=mode,
            start_length=start_length, flash_ms=flash_ms, rounds=rounds,
        )
