"""
Path session and path builder screens.
"""
from __future__ import annotations

import random

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QProgressBar, QScrollArea, QLineEdit, QMessageBox,
)
from PyQt6.QtCore import Qt

from neural_speed_academy.screens.base import BaseScreen
from neural_speed_academy.theme import COLORS, make_qfont
from neural_speed_academy.config import TRAINING_PATHS
from neural_speed_academy.state import PathProgress


class PathSessionScreen(BaseScreen):

    def build(self, **kwargs) -> None:
        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")
        self.add_nav_bar()

        user = self.navigator.get_user()
        if not user or not user.active_path:
            self.navigator.to_dashboard()
            return

        path_id = user.active_path
        path_data = TRAINING_PATHS.get(path_id) or user.custom_paths.get(path_id)
        if not path_data:
            self.navigator.to_dashboard()
            return

        pp = user.path_progress.get(path_id)
        if not pp:
            pp = PathProgress(path_id=path_id, start_xp=user.xp)
            user.path_progress[path_id] = pp

        steps = path_data["steps"]
        current = pp.current_step

        if current >= len(steps):
            pp.completed = True
            user.active_path = None
            self.navigator.user_repo.save(user)
            self._show_path_complete(path_data, user)
            return

        container = QWidget()
        container.setStyleSheet(f"background-color: {c['bg']};")
        cl = QVBoxLayout(container)
        cl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.setSpacing(8)

        # Path title
        title = QLabel(path_data["name"].upper())
        title.setFont(make_qfont("header"))
        title.setStyleSheet(f"color: {c['accent']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(title)

        # Progress bar
        progress = QProgressBar()
        progress.setRange(0, len(steps))
        progress.setValue(current)
        progress.setFixedWidth(500)
        progress.setFixedHeight(12)
        progress.setTextVisible(False)
        progress.setStyleSheet(
            f"QProgressBar {{ background-color: {c['card']}; border: none; border-radius: 6px; }}"
            f"QProgressBar::chunk {{ background-color: {c['accent']}; border-radius: 6px; }}"
        )
        cl.addWidget(progress, alignment=Qt.AlignmentFlag.AlignCenter)

        step_lbl = QLabel(f"Step {current + 1} of {len(steps)}")
        step_lbl.setFont(make_qfont("counter"))
        step_lbl.setStyleSheet(f"color: {c['fg']};")
        step_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(step_lbl)

        # Step list
        for i, (ex_type, label, params) in enumerate(steps):
            if i < current:
                marker, fg = "\u2705", c["muted"]
            elif i == current:
                marker, fg = "\u25b6", c["accent"]
            else:
                marker, fg = "\u25cb", c["muted"]
            row = QLabel(f"  {marker}  {label}")
            row.setFont(make_qfont("body"))
            row.setStyleSheet(f"color: {fg};")
            cl.addWidget(row, alignment=Qt.AlignmentFlag.AlignCenter)

        cl.addSpacing(10)

        # Launch button
        ex_type, label, params = steps[current]
        launch = QPushButton(f"\u25b6  {label}")
        launch.setFont(make_qfont("btn_lg"))
        launch.setStyleSheet(
            f"QPushButton {{ background-color: {c['accent']}; color: {c['btn_text']}; "
            f"border: 2px solid transparent; padding: 12px 40px; border-radius: 4px; }}"
        )
        launch.setCursor(Qt.CursorShape.PointingHandCursor)
        launch.clicked.connect(
            lambda: self._launch_step(ex_type, params, path_id, current)
        )
        cl.addWidget(launch, alignment=Qt.AlignmentFlag.AlignCenter)

        # Nav buttons
        nav_row = QHBoxLayout()
        nav_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if current > 0:
            prev_btn = QPushButton("\u2190 PREVIOUS STEP")
            prev_btn.setFont(make_qfont("btn_sm"))
            prev_btn.setStyleSheet(
                f"QPushButton {{ background-color: {c['card']}; color: {c['fg']}; "
                f"border: 2px solid transparent; padding: 4px 12px; border-radius: 3px; }}"
            )
            prev_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            prev_btn.clicked.connect(
                lambda: self._go_to_step(path_id, current - 1)
            )
            nav_row.addWidget(prev_btn)

        skip_btn = QPushButton("SKIP THIS STEP \u2192")
        skip_btn.setFont(make_qfont("btn_sm"))
        skip_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['card']}; color: {c['fg']}; "
            f"border: 2px solid transparent; padding: 4px 12px; border-radius: 3px; }}"
        )
        skip_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        skip_btn.clicked.connect(
            lambda: self._advance_step(path_id, current)
        )
        nav_row.addWidget(skip_btn)
        cl.addLayout(nav_row)

        self._layout.addWidget(container, 1)

    def _go_to_step(self, path_id: str, step_idx: int) -> None:
        user = self.navigator.get_user()
        if not user:
            return
        pp = user.path_progress.get(path_id)
        if pp:
            pp.current_step = step_idx
            pp.completed = False
            self.navigator.user_repo.save(user)
        self.navigator.navigate_to("path_session")

    def _launch_step(self, ex_type: str, params: dict, path_id: str,
                     step_idx: int) -> None:
        from neural_speed_academy.exercises.flash import FlashExercise
        from neural_speed_academy.exercises.rsvp import RsvpExercise
        from neural_speed_academy.exercises.chunking import ChunkingExercise
        from neural_speed_academy.exercises.pacer import PacerExercise
        from neural_speed_academy.exercises.schulte import SchulteExercise
        from neural_speed_academy.exercises.priming import PrimingExercise
        from neural_speed_academy.exercises.sequence_memory import SequenceMemoryExercise
        from neural_speed_academy.exercises.peripheral_flash import PeripheralFlashExercise
        from neural_speed_academy.exercises.rapid_decision import RapidDecisionGridExercise as RapidDecisionExercise
        from neural_speed_academy.exercises.mot import MotExercise
        from neural_speed_academy.exercises.split_attention import SplitAttentionExercise
        from neural_speed_academy.exercises.reaction_time import ReactionTimeExercise
        from neural_speed_academy.exercises.slide_processing import SlideProcessingExercise
        from neural_speed_academy.exercises.spaced_repetition import SpacedRepetitionExercise

        user = self.navigator.get_user()
        if user:
            user.active_path = path_id
            self.navigator.user_repo.save(user)

        self.navigator._path_step_pending = (path_id, step_idx)

        if ex_type == "priming":
            self.navigator.launch_exercise(PrimingExercise, **params)
        elif ex_type == "flash":
            digits = params.get("digits")
            low = params.get("low", digits or 3)
            high = params.get("high", digits or 3)
            rounds = params.get("rounds", 10)
            _low, _high = low, high
            self.navigator.launch_exercise(
                FlashExercise, mode="flash_num", rounds=rounds,
                level_func=lambda _, lo=_low, hi=_high: random.randint(lo, hi),
            )
        elif ex_type == "eyespan":
            _low = params.get("low", 2)
            _high = params.get("high", 3)
            self.navigator.launch_exercise(
                FlashExercise, mode="eyespan",
                rounds=params.get("rounds", 10),
                level_func=lambda _, lo=_low, hi=_high: random.randint(lo, hi),
                span_config={
                    "mode": params.get("mode", "h"),
                    "width": params.get("width", 50),
                },
            )
        elif ex_type == "schulte":
            self.navigator.launch_exercise(SchulteExercise, **params)
        elif ex_type == "pacer":
            self.navigator.launch_exercise(PacerExercise, **params)
        elif ex_type == "rsvp":
            self.navigator.launch_exercise(RsvpExercise, **params)
        elif ex_type == "chunking":
            self.navigator.launch_exercise(ChunkingExercise, **params)
        elif ex_type == "sequence_memory":
            self.navigator.launch_exercise(SequenceMemoryExercise, **params)
        elif ex_type == "recall":
            self.navigator.launch_exercise(ChunkingExercise, **params)
        elif ex_type == "peripheral_flash":
            self.navigator.launch_exercise(PeripheralFlashExercise, **params)
        elif ex_type == "rapid_decision":
            self.navigator.launch_exercise(RapidDecisionExercise, **params)
        elif ex_type == "mot":
            self.navigator.launch_exercise(MotExercise, **params)
        elif ex_type == "split_attention":
            self.navigator.launch_exercise(SplitAttentionExercise, **params)
        elif ex_type == "reaction_time":
            self.navigator.launch_exercise(ReactionTimeExercise, **params)
        elif ex_type == "slide_processing":
            self.navigator.launch_exercise(SlideProcessingExercise, **params)
        elif ex_type == "spaced_repetition":
            self.navigator.launch_exercise(SpacedRepetitionExercise, **params)

    def _show_path_complete(self, path_data: dict, user) -> None:
        c = COLORS
        container = QWidget()
        container.setStyleSheet(f"background-color: {c['bg']};")
        cl = QVBoxLayout(container)
        cl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.setSpacing(8)

        title = QLabel("PATH COMPLETE")
        title.setFont(make_qfont("header"))
        title.setStyleSheet(f"color: {c['accent']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(title)

        name = QLabel(path_data["name"])
        name.setFont(make_qfont("sub"))
        name.setStyleSheet(f"color: {c['fg']};")
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(name)

        check = QLabel("\u2713")
        check.setStyleSheet(f"color: {c['success']}; font-size: 48pt;")
        check.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(check)

        # Summary card
        card = QFrame()
        card.setStyleSheet(f"background-color: {c['card']}; border-radius: 6px; padding: 15px;")
        card_layout = QHBoxLayout(card)

        step_count = len(path_data["steps"])
        xp_earned = 0
        if user:
            for pid, prog in user.path_progress.items():
                if prog.completed and path_data["name"] == TRAINING_PATHS.get(pid, {}).get("name"):
                    xp_earned = user.xp - prog.start_xp
                    break

        for label, value in [
            ("EXERCISES", str(step_count)),
            ("XP EARNED", f"+{max(0, xp_earned)}"),
            ("LEVEL", str(user.xp // 1000 + 1) if user else "\u2014"),
        ]:
            cell = QVBoxLayout()
            cell.setAlignment(Qt.AlignmentFlag.AlignCenter)
            v = QLabel(value)
            v.setFont(make_qfont("sub"))
            v.setStyleSheet(f"color: {c['accent']};")
            v.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cell.addWidget(v)
            l = QLabel(label)
            l.setFont(make_qfont("btn_sm"))
            l.setStyleSheet(f"color: {c['muted']};")
            l.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cell.addWidget(l)
            card_layout.addLayout(cell)

        cl.addWidget(card)
        cl.addSpacing(10)

        btn_row = QHBoxLayout()
        btn_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        for text, bg, fg, cb in [
            ("TRAINING PATHS", c["accent"], c["btn_text"],
             lambda: self.navigator.navigate_to("paths")),
            ("TRAINING HUB", c["action"], c["btn_text"],
             self.navigator.to_dashboard),
        ]:
            btn = QPushButton(text)
            btn.setFont(make_qfont("btn_bold"))
            btn.setStyleSheet(
                f"QPushButton {{ background-color: {bg}; color: {fg}; "
                f"border: 2px solid transparent; padding: 8px 24px; border-radius: 4px; }}"
            )
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(cb)
            btn_row.addWidget(btn)
        cl.addLayout(btn_row)

        self._layout.addWidget(container, 1)

    def _advance_step(self, path_id: str, step_idx: int) -> None:
        user = self.navigator.get_user()
        if not user:
            return
        pp = user.path_progress.get(path_id)
        if pp and pp.current_step == step_idx:
            pp.current_step += 1
            path_data = TRAINING_PATHS.get(path_id) or user.custom_paths.get(path_id, {})
            if pp.current_step >= len(path_data.get("steps", [])):
                pp.completed = True
                user.active_path = None
            self.navigator.user_repo.save(user)
        self.navigator.navigate_to("path_session")


# ── Exercise catalog for the path builder ──

EXERCISE_CATALOG = [
    ("priming", "Eye Priming", [
        ("Horizontal Saccades", {"mode": "saccade_h", "delay": 500}),
        ("Vertical Saccades", {"mode": "saccade_v", "delay": 500}),
        ("Diagonal Saccades", {"mode": "saccade_diag", "delay": 450}),
        ("Expanding Saccades", {"mode": "saccade_expand", "delay": 500}),
        ("Smooth Pursuit Circle", {"mode": "pursuit_circle", "cycles": 10}),
        ("Figure-8 Pursuit", {"mode": "pursuit_figure8", "cycles": 12}),
    ]),
    ("flash", "Flash Digits", [
        ("3 Digits", {"digits": 3, "rounds": 10}),
        ("4 Digits", {"digits": 4, "rounds": 10}),
        ("5 Digits", {"digits": 5, "rounds": 12}),
        ("3-5 Digits", {"low": 3, "high": 5, "rounds": 12}),
        ("5-7 Digits", {"low": 5, "high": 7, "rounds": 15}),
        ("7-9 Digits", {"low": 7, "high": 9, "rounds": 15}),
    ]),
    ("eyespan", "Eye-Span", [
        ("Horizontal 30%", {"mode": "h", "width": 30, "low": 2, "high": 2, "rounds": 10}),
        ("Horizontal 50%", {"mode": "h", "width": 50, "low": 2, "high": 3, "rounds": 10}),
        ("Vertical 50%", {"mode": "v", "width": 50, "low": 2, "high": 3, "rounds": 10}),
        ("Mixed 60%", {"mode": "m", "width": 60, "low": 3, "high": 4, "rounds": 12}),
    ]),
    ("schulte", "Schulte Grid", [
        ("Standard Grid", {}),
    ]),
    ("rsvp", "RSVP Reader", [
        ("200 WPM", {"wpm": 200}),
        ("300 WPM", {"wpm": 300}),
        ("400 WPM", {"wpm": 400}),
        ("500 WPM", {"wpm": 500}),
        ("600 WPM", {"wpm": 600}),
        ("800 WPM", {"wpm": 800}),
    ]),
    ("chunking", "Chunking", [
        ("2-Word at 200 WPM", {"chunk_size": 2, "wpm": 200}),
        ("3-Word at 300 WPM", {"chunk_size": 3, "wpm": 300}),
        ("4-Word at 400 WPM", {"chunk_size": 4, "wpm": 400}),
        ("5-Word at 500 WPM", {"chunk_size": 5, "wpm": 500}),
    ]),
    ("pacer", "Pacer & Quiz", [
        ("Comprehension Check", {}),
    ]),
    ("sequence_memory", "Sequence Memory", [
        ("Standard", {}),
    ]),
    ("recall", "Recall Training", [
        ("Words", {"mode": "words"}),
        ("Numbers", {"mode": "numbers"}),
        ("Mixed", {"mode": "mixed"}),
    ]),
    ("peripheral_flash", "Peripheral Flash", [
        ("Standard", {}),
    ]),
    ("rapid_decision", "Rapid Decision Grid", [
        ("Standard", {}),
    ]),
    ("mot", "Multiple Object Tracking", [
        ("3 targets · 6s", {"targets": 3, "duration": 6}),
        ("4 targets · 8s", {"targets": 4, "duration": 8}),
        ("5 targets · 8s", {"targets": 5, "duration": 8}),
    ]),
    ("split_attention", "Split Attention", [
        ("Sequential", {"mode": "sequential"}),
        ("Simultaneous", {"mode": "simultaneous"}),
        ("Rapid", {"mode": "rapid"}),
    ]),
    ("reaction_time", "Reaction Time", [
        ("Simple", {"mode": "simple"}),
        ("Choice", {"mode": "choice"}),
        ("Go/No-Go", {"mode": "go_nogo"}),
    ]),
    ("slide_processing", "Slide Processing", [
        ("10s · 5 slides", {"display_s": 10, "slides": 5}),
        ("8s · 5 slides", {"display_s": 8, "slides": 5}),
        ("5s · 5 slides", {"display_s": 5, "slides": 5}),
    ]),
    ("spaced_repetition", "Spaced Repetition", [
        ("Review Session", {}),
    ]),
]


class PathBuilderScreen(BaseScreen):

    def __init__(self, navigator, parent=None):
        super().__init__(navigator, parent)
        self._steps: list[tuple[str, str, dict]] = []

    def build(self, **kwargs) -> None:
        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")
        self.add_nav_bar()
        self._steps = []

        container = QWidget()
        container.setStyleSheet(f"background-color: {c['bg']};")
        cl = QVBoxLayout(container)
        cl.setContentsMargins(40, 10, 40, 10)

        title = QLabel("CREATE CUSTOM PATH")
        title.setFont(make_qfont("header"))
        title.setStyleSheet(f"color: {c['accent']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(title)

        # Name entry
        name_row = QHBoxLayout()
        name_lbl = QLabel("Path Name:")
        name_lbl.setFont(make_qfont("btn_bold"))
        name_lbl.setStyleSheet(f"color: {c['fg']};")
        name_row.addWidget(name_lbl)

        from neural_speed_academy.theme import input_css
        self._name_entry = QLineEdit()
        self._name_entry.setFont(make_qfont("body"))
        self._name_entry.setStyleSheet(input_css())
        self._name_entry.setFixedWidth(300)
        name_row.addWidget(self._name_entry)
        name_row.addStretch()
        cl.addLayout(name_row)

        # Two columns
        cols = QHBoxLayout()

        # Left: catalog
        left = QVBoxLayout()
        cat_title = QLabel("EXERCISE CATALOG")
        cat_title.setFont(make_qfont("section_header"))
        cat_title.setStyleSheet(f"color: {c['fg']};")
        left.addWidget(cat_title)

        cat_scroll = QScrollArea()
        cat_scroll.setWidgetResizable(True)
        cat_scroll.setFrameShape(QFrame.Shape.NoFrame)
        cat_scroll.setStyleSheet(f"background-color: {c['bg']};")
        cat_content = QWidget()
        cat_layout = QVBoxLayout(cat_content)
        cat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        for ex_type, group_name, variants in EXERCISE_CATALOG:
            grp = QLabel(group_name)
            grp.setFont(make_qfont("btn_bold"))
            grp.setStyleSheet(f"color: {c['accent']};")
            cat_layout.addWidget(grp)

            for variant_name, params in variants:
                label = f"{group_name}: {variant_name}"
                btn = QPushButton(f"  + {variant_name}")
                btn.setFont(make_qfont("body"))
                btn.setStyleSheet(
                    f"QPushButton {{ background-color: {c['card']}; color: {c['fg']}; "
                    f"border: 2px solid transparent; padding: 4px 8px; text-align: left; "
                    f"border-radius: 3px; }}"
                    f"QPushButton:hover {{ background-color: {c['accent']}; }}"
                )
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.clicked.connect(
                    lambda checked, t=ex_type, l=label, p=params: self._add_step(t, l, p)
                )
                cat_layout.addWidget(btn)

        cat_scroll.setWidget(cat_content)
        left.addWidget(cat_scroll)
        cols.addLayout(left)

        # Right: steps
        right = QVBoxLayout()
        steps_title = QLabel("YOUR PATH")
        steps_title.setFont(make_qfont("section_header"))
        steps_title.setStyleSheet(f"color: {c['fg']};")
        right.addWidget(steps_title)

        self._steps_container = QWidget()
        self._steps_container.setStyleSheet(f"background-color: {c['bg']};")
        self._steps_layout = QVBoxLayout(self._steps_container)
        self._steps_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        right.addWidget(self._steps_container, 1)
        cols.addLayout(right)

        cl.addLayout(cols, 1)
        self._refresh_steps()

        # Bottom buttons
        btn_row = QHBoxLayout()
        btn_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        save_btn = QPushButton("SAVE PATH")
        save_btn.setFont(make_qfont("btn_bold"))
        save_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['accent']}; color: {c['btn_text']}; "
            f"border: 2px solid transparent; padding: 8px 24px; border-radius: 4px; }}"
        )
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self._save_path)
        btn_row.addWidget(save_btn)

        cancel_btn = QPushButton("CANCEL")
        cancel_btn.setFont(make_qfont("btn_bold"))
        cancel_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['card']}; color: {c['fg']}; "
            f"border: 2px solid transparent; padding: 8px 24px; border-radius: 4px; }}"
        )
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(lambda: self.navigator.navigate_to("paths"))
        btn_row.addWidget(cancel_btn)

        cl.addLayout(btn_row)
        self._layout.addWidget(container, 1)

    def _add_step(self, ex_type: str, label: str, params: dict) -> None:
        self._steps.append((ex_type, label, params))
        self._refresh_steps()

    def _remove_step(self, index: int) -> None:
        if 0 <= index < len(self._steps):
            self._steps.pop(index)
            self._refresh_steps()

    def _refresh_steps(self) -> None:
        c = COLORS
        while self._steps_layout.count():
            item = self._steps_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        if not self._steps:
            empty = QLabel("Add exercises from the catalog\nto build your path.")
            empty.setFont(make_qfont("body"))
            empty.setStyleSheet(f"color: {c['muted']};")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._steps_layout.addWidget(empty)
            return

        for i, (ex_type, label, params) in enumerate(self._steps):
            row = QHBoxLayout()
            num = QLabel(f"{i + 1}.")
            num.setFont(make_qfont("btn_sm"))
            num.setStyleSheet(f"color: {c['muted']};")
            num.setFixedWidth(25)
            row.addWidget(num)

            lbl = QLabel(label)
            lbl.setFont(make_qfont("body"))
            lbl.setStyleSheet(f"color: {c['fg']};")
            row.addWidget(lbl, 1)

            rm = QPushButton("\u2717")
            rm.setFont(make_qfont("btn_sm"))
            rm.setStyleSheet(
                f"QPushButton {{ color: {c['alert']}; background: transparent; "
                f"border: 2px solid transparent; }}"
            )
            rm.setCursor(Qt.CursorShape.PointingHandCursor)
            rm.setAccessibleName(f"Remove step {i + 1}")
            rm.setToolTip(f"Remove step {i + 1}")
            rm.clicked.connect(lambda checked, idx=i: self._remove_step(idx))
            row.addWidget(rm)

            wrapper = QWidget()
            wrapper.setLayout(row)
            self._steps_layout.addWidget(wrapper)

    def _save_path(self) -> None:
        user = self.navigator.get_user()
        if not user:
            return
        name = self._name_entry.text().strip()
        if not name:
            QMessageBox.information(self, "Name Required", "Please enter a name for your path.")
            return
        if not self._steps:
            QMessageBox.information(self, "No Exercises", "Add at least one exercise to your path.")
            return

        path_id = f"custom_{name.lower().replace(' ', '_')}"
        base_id = path_id
        counter = 1
        while path_id in user.custom_paths or path_id in TRAINING_PATHS:
            path_id = f"{base_id}_{counter}"
            counter += 1

        steps = [(t, l, dict(p)) for t, l, p in self._steps]
        user.custom_paths[path_id] = {
            "name": name,
            "description": f"Custom path with {len(steps)} exercises",
            "steps": steps,
        }
        self.navigator.user_repo.save(user)
        self.navigator.navigate_to("paths")
