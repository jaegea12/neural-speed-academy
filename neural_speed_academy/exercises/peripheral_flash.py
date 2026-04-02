"""
Peripheral Flash exercise.

Flashes stimuli (letters, numbers, shapes) at screen edges while the user
maintains center fixation. Trains peripheral awareness for reading, gaming,
driving, and sports. Difficulty scales via flash duration and eccentricity.
"""
from __future__ import annotations

import random
import string

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSlider, QComboBox, QGridLayout,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from neural_speed_academy.exercises.base import BaseExercise, ExerciseResult
from neural_speed_academy.theme import COLORS, make_qfont, screen_metrics
from neural_speed_academy.config import PERIPHERAL_FLASH_CONFIG, USER_DATA_CONFIG


# Positions as (x_frac, y_frac) relative to the arena center.
# Eccentricity scales these outward.
_DIRECTIONS = [
    (0.0, -1.0),   # top
    (0.0, 1.0),    # bottom
    (-1.0, 0.0),   # left
    (1.0, 0.0),    # right
    (-0.7, -0.7),  # top-left
    (0.7, -0.7),   # top-right
    (-0.7, 0.7),   # bottom-left
    (0.7, 0.7),    # bottom-right
]


class PeripheralFlashExercise(BaseExercise):

    def __init__(self, navigator, parent: QWidget | None = None):
        super().__init__(navigator, parent)
        self._round: int = 0
        self._total_rounds: int = 15
        self._correct: int = 0
        self._flash_ms: int = 300
        self._eccentricity: int = 50
        self._stim_type: str = "letters"
        self._current_stimulus: str = ""
        self._current_answer: str = ""
        self._stim_label: QLabel | None = None
        self._fixation: QLabel | None = None
        self._arena: QWidget | None = None

    @property
    def name(self) -> str:
        return "Peripheral Flash"

    # ── Config screen ──

    def start(self, **kwargs) -> None:
        self._clear()
        self._running = True
        self.add_nav_bar()

        cfg = PERIPHERAL_FLASH_CONFIG
        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")

        self._flash_ms = kwargs.get("flash_ms", cfg["default_flash_ms"])
        self._eccentricity = kwargs.get("eccentricity", cfg["default_eccentricity"])
        self._total_rounds = kwargs.get("rounds", cfg["default_rounds"])
        self._stim_type = kwargs.get("stim_type", "letters")

        container = QWidget()
        container.setStyleSheet(f"background-color: {c['bg']};")
        cl = QVBoxLayout(container)
        cl.setContentsMargins(40, 20, 40, 20)
        cl.setSpacing(10)

        # Guide button
        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        guide_btn = QPushButton("GUIDE")
        guide_btn.setFont(make_qfont("btn_sm"))
        guide_btn.setStyleSheet(
            f"background-color: {c['accent']}; color: {c['btn_text']}; "
            f"border: none; padding: 4px 12px; border-radius: 3px;"
        )
        guide_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        guide_btn.clicked.connect(
            lambda: self.show_guide("peripheral_flash")
        )
        top.addWidget(guide_btn)
        top.addStretch()
        cl.addLayout(top)

        title = QLabel("PERIPHERAL FLASH")
        title.setFont(make_qfont("section_header"))
        title.setStyleSheet(f"color: {c['accent']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(title)

        cl.addSpacing(10)

        slider_groove = (
            f"QSlider::groove:horizontal {{ background: {c['card']}; "
            f"height: 6px; border-radius: 3px; }}"
            f"QSlider::handle:horizontal {{ background: {c['accent']}; "
            f"width: 16px; margin: -5px 0; border-radius: 8px; }}"
        )

        # Stimulus type
        type_row = QHBoxLayout()
        type_row.addStretch()
        type_lbl = QLabel("Stimulus:")
        type_lbl.setFont(make_qfont("slider_label"))
        type_lbl.setStyleSheet(f"color: {c['fg']};")
        type_row.addWidget(type_lbl)

        self._type_combo = QComboBox()
        self._type_combo.addItems(["Letters", "Numbers", "Shapes"])
        idx = {"letters": 0, "numbers": 1, "shapes": 2}.get(self._stim_type, 0)
        self._type_combo.setCurrentIndex(idx)
        self._type_combo.setStyleSheet(
            f"QComboBox {{ background-color: {c['card']}; color: {c['fg']}; "
            f"border: 1px solid {c['muted']}; padding: 4px 8px; "
            f"border-radius: 3px; }}"
            f"QComboBox::drop-down {{ border: none; }}"
            f"QComboBox QAbstractItemView {{ background-color: {c['card']}; "
            f"color: {c['fg']}; selection-background-color: {c['accent']}; }}"
        )
        self._type_combo.setFixedWidth(150)
        type_row.addWidget(self._type_combo)
        type_row.addStretch()
        cl.addLayout(type_row)

        # Flash duration
        flash_row = QHBoxLayout()
        flash_row.addStretch()
        flash_lbl = QLabel("Flash (ms):")
        flash_lbl.setFont(make_qfont("slider_label"))
        flash_lbl.setStyleSheet(f"color: {c['fg']};")
        flash_row.addWidget(flash_lbl)

        self._flash_slider = QSlider(Qt.Orientation.Horizontal)
        self._flash_slider.setRange(cfg["min_flash_ms"], cfg["max_flash_ms"])
        self._flash_slider.setValue(self._flash_ms)
        self._flash_slider.setFixedWidth(250)
        self._flash_slider.setStyleSheet(slider_groove)

        self._flash_display = QLabel(str(self._flash_ms))
        self._flash_display.setFont(make_qfont("counter"))
        self._flash_display.setStyleSheet(f"color: {c['accent']};")
        self._flash_display.setFixedWidth(50)
        self._flash_slider.valueChanged.connect(
            lambda v: self._flash_display.setText(str(v))
        )
        flash_row.addWidget(self._flash_slider)
        flash_row.addWidget(self._flash_display)
        flash_row.addStretch()
        cl.addLayout(flash_row)

        # Eccentricity
        ecc_row = QHBoxLayout()
        ecc_row.addStretch()
        ecc_lbl = QLabel("Eccentricity (%):")
        ecc_lbl.setFont(make_qfont("slider_label"))
        ecc_lbl.setStyleSheet(f"color: {c['fg']};")
        ecc_row.addWidget(ecc_lbl)

        self._ecc_slider = QSlider(Qt.Orientation.Horizontal)
        self._ecc_slider.setRange(
            cfg["min_eccentricity"], cfg["max_eccentricity"]
        )
        self._ecc_slider.setValue(self._eccentricity)
        self._ecc_slider.setFixedWidth(250)
        self._ecc_slider.setStyleSheet(slider_groove)

        self._ecc_display = QLabel(str(self._eccentricity))
        self._ecc_display.setFont(make_qfont("counter"))
        self._ecc_display.setStyleSheet(f"color: {c['accent']};")
        self._ecc_display.setFixedWidth(50)
        self._ecc_slider.valueChanged.connect(
            lambda v: self._ecc_display.setText(str(v))
        )
        ecc_row.addWidget(self._ecc_slider)
        ecc_row.addWidget(self._ecc_display)
        ecc_row.addStretch()
        cl.addLayout(ecc_row)

        # Rounds
        rounds_row = QHBoxLayout()
        rounds_row.addStretch()
        rounds_lbl = QLabel("Rounds:")
        rounds_lbl.setFont(make_qfont("slider_label"))
        rounds_lbl.setStyleSheet(f"color: {c['fg']};")
        rounds_row.addWidget(rounds_lbl)

        self._rounds_slider = QSlider(Qt.Orientation.Horizontal)
        self._rounds_slider.setRange(5, 30)
        self._rounds_slider.setValue(self._total_rounds)
        self._rounds_slider.setFixedWidth(250)
        self._rounds_slider.setStyleSheet(slider_groove)

        self._rounds_display = QLabel(str(self._total_rounds))
        self._rounds_display.setFont(make_qfont("counter"))
        self._rounds_display.setStyleSheet(f"color: {c['accent']};")
        self._rounds_display.setFixedWidth(50)
        self._rounds_slider.valueChanged.connect(
            lambda v: self._rounds_display.setText(str(v))
        )
        rounds_row.addWidget(self._rounds_slider)
        rounds_row.addWidget(self._rounds_display)
        rounds_row.addStretch()
        cl.addLayout(rounds_row)

        # Start button
        cl.addSpacing(10)
        start_btn = QPushButton("START")
        start_btn.setFont(make_qfont("btn_lg"))
        start_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['success']}; "
            f"color: {c['btn_text']}; "
            f"border: none; padding: 10px 40px; border-radius: 4px; }}"
        )
        start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        start_btn.clicked.connect(self._start_from_ui)
        cl.addWidget(start_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        cl.addStretch()
        self._layout.addWidget(container, 1)

    def _start_from_ui(self) -> None:
        type_map = {0: "letters", 1: "numbers", 2: "shapes"}
        self._stim_type = type_map.get(
            self._type_combo.currentIndex(), "letters"
        )
        self._flash_ms = self._flash_slider.value()
        self._eccentricity = self._ecc_slider.value()
        self._total_rounds = self._rounds_slider.value()
        self._run_exercise()

    # ── Exercise loop ──

    def _run_exercise(self) -> None:
        self._round = 0
        self._correct = 0
        self._clear()
        self._running = True

        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")

        # Top bar: progress + exit
        top = QHBoxLayout()
        top.setContentsMargins(10, 6, 10, 2)

        self._progress_lbl = QLabel(f"Round 0/{self._total_rounds}")
        self._progress_lbl.setFont(make_qfont("counter"))
        self._progress_lbl.setStyleSheet(f"color: {c['accent']};")
        top.addWidget(self._progress_lbl)

        top.addStretch()

        self._score_lbl = QLabel("Score: 0")
        self._score_lbl.setFont(make_qfont("counter"))
        self._score_lbl.setStyleSheet(f"color: {c['fg']};")
        top.addWidget(self._score_lbl)

        top.addStretch()

        exit_btn = QPushButton("\u2716")
        exit_btn.setFont(make_qfont("exit_btn"))
        exit_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['alert']}; "
            f"color: {c['text_on_card']}; "
            f"border: none; padding: 4px 8px; border-radius: 3px; }}"
        )
        exit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        exit_btn.clicked.connect(self._stop)
        top.addWidget(exit_btn)
        self._layout.addLayout(top)

        # Arena — the fixation + stimulus area
        self._arena = QWidget()
        self._arena.setStyleSheet(f"background-color: {c['bg']};")
        self._layout.addWidget(self._arena, 1)

        # Fixation cross (always visible during rounds)
        self._fixation = QLabel("+", self._arena)
        self._fixation.setFont(QFont("Arial", 48, QFont.Weight.Bold))
        self._fixation.setStyleSheet(f"color: {c['fg']}; background: transparent;")
        self._fixation.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._fixation.setFixedSize(60, 60)

        # Stimulus label (hidden until flash)
        self._stim_label = QLabel("", self._arena)
        self._stim_label.setFont(QFont("Arial", 42, QFont.Weight.Bold))
        self._stim_label.setStyleSheet(
            f"color: {c['accent']}; background: transparent;"
        )
        self._stim_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._stim_label.setFixedSize(80, 80)
        self._stim_label.hide()

        # Answer buttons container (hidden until after flash)
        self._answer_container = QWidget()
        self._answer_container.setStyleSheet(f"background-color: {c['bg']};")
        self._answer_layout = QGridLayout(self._answer_container)
        self._answer_layout.setSpacing(8)
        self._answer_container.hide()
        self._layout.addWidget(
            self._answer_container, 0,
            Qt.AlignmentFlag.AlignCenter,
        )

        # Feedback label
        self._feedback_lbl = QLabel("")
        self._feedback_lbl.setFont(make_qfont("btn_bold"))
        self._feedback_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._feedback_lbl.setFixedHeight(30)
        self._layout.addWidget(self._feedback_lbl)

        # Start first round after a brief delay
        self._after(800, self._next_round)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._position_fixation()

    def _position_fixation(self) -> None:
        """Center the fixation cross in the arena."""
        if self._arena and self._fixation:
            aw = self._arena.width()
            ah = self._arena.height()
            fw = self._fixation.width()
            fh = self._fixation.height()
            self._fixation.move((aw - fw) // 2, (ah - fh) // 2)

    def _generate_stimulus(self) -> tuple[str, str]:
        """Generate a stimulus and its answer string.

        Returns (display_text, answer_key).
        """
        cfg = PERIPHERAL_FLASH_CONFIG
        if self._stim_type == "numbers":
            n = str(random.randint(1, 9))
            return n, n
        elif self._stim_type == "shapes":
            idx = random.randint(0, len(cfg["shapes"]) - 1)
            return cfg["shapes"][idx], cfg["shape_names"][idx]
        else:
            letter = random.choice(string.ascii_uppercase)
            return letter, letter

    def _generate_choices(self, correct_answer: str) -> list[str]:
        """Generate answer choices including the correct one."""
        cfg = PERIPHERAL_FLASH_CONFIG
        choices = {correct_answer}

        if self._stim_type == "numbers":
            pool = [str(i) for i in range(1, 10)]
        elif self._stim_type == "shapes":
            pool = list(cfg["shape_names"])
        else:
            pool = list(string.ascii_uppercase)

        while len(choices) < min(4, len(pool)):
            choices.add(random.choice(pool))

        result = list(choices)
        random.shuffle(result)
        return result

    def _next_round(self) -> None:
        if not self._running:
            return
        if self._round >= self._total_rounds:
            self._show_results()
            return

        self._round += 1
        c = COLORS
        self._progress_lbl.setText(
            f"Round {self._round}/{self._total_rounds}"
        )
        self._feedback_lbl.setText("")
        self._feedback_lbl.setStyleSheet(f"color: {c['bg']};")
        self._answer_container.hide()

        # Position fixation
        self._position_fixation()

        # Generate stimulus
        display, answer = self._generate_stimulus()
        self._current_stimulus = display
        self._current_answer = answer

        # Pick a random direction and compute position
        dx, dy = random.choice(_DIRECTIONS)
        aw = self._arena.width()
        ah = self._arena.height()
        cx, cy = aw // 2, ah // 2

        # Eccentricity as fraction of half the arena dimension
        ecc_frac = self._eccentricity / 100.0
        sx = int(cx + dx * ecc_frac * (aw // 2 - 50))
        sy = int(cy + dy * ecc_frac * (ah // 2 - 50))

        # Clamp to arena bounds
        sw, sh = self._stim_label.width(), self._stim_label.height()
        sx = max(0, min(sx - sw // 2, aw - sw))
        sy = max(0, min(sy - sh // 2, ah - sh))

        self._stim_label.setText(display)
        self._stim_label.move(sx, sy)

        # Brief delay showing just the fixation, then flash
        self._after(500, self._flash_stimulus)

    def _flash_stimulus(self) -> None:
        if not self._running:
            return
        self._stim_label.show()
        self._after(self._flash_ms, self._hide_and_ask)

    def _hide_and_ask(self) -> None:
        if not self._running:
            return
        self._stim_label.hide()
        # Brief pause before showing choices to prevent accidental clicks
        self._after(300, self._show_choices)

    def _show_choices(self) -> None:
        c = COLORS
        # Clear old buttons
        while self._answer_layout.count():
            item = self._answer_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        choices = self._generate_choices(self._current_answer)

        # Display label for shapes (show the shape symbol alongside name)
        cfg = PERIPHERAL_FLASH_CONFIG
        shape_map = {}
        if self._stim_type == "shapes":
            shape_map = dict(
                zip(cfg["shape_names"], cfg["shapes"])
            )

        for i, choice in enumerate(choices):
            display = choice
            if self._stim_type == "shapes" and choice in shape_map:
                display = f"{shape_map[choice]}  {choice}"

            btn = QPushButton(display)
            btn.setFont(make_qfont("btn_bold"))
            btn.setFixedWidth(160)
            btn.setStyleSheet(
                f"QPushButton {{ background-color: {c['card']}; "
                f"color: {c['fg']}; border: 1px solid {c['muted']}; "
                f"padding: 10px; border-radius: 4px; }}"
                f"QPushButton:hover {{ background-color: {c['accent']}; "
                f"color: {c['btn_text']}; }}"
            )
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, ch=choice: self._check_answer(ch))
            self._answer_layout.addWidget(
                btn, i // 2, i % 2,
                Qt.AlignmentFlag.AlignCenter,
            )

        self._answer_container.show()

    def _check_answer(self, chosen: str) -> None:
        if not self._running:
            return
        c = COLORS

        if chosen == self._current_answer:
            self._correct += 1
            self._feedback_lbl.setText("\u2714 Correct!")
            self._feedback_lbl.setStyleSheet(f"color: {c['success']};")
        else:
            expected = self._current_answer
            if self._stim_type == "shapes":
                cfg = PERIPHERAL_FLASH_CONFIG
                shape_map = dict(
                    zip(cfg["shape_names"], cfg["shapes"])
                )
                sym = shape_map.get(expected, "")
                expected = f"{sym} {expected}" if sym else expected
            self._feedback_lbl.setText(f"\u2718 It was: {expected}")
            self._feedback_lbl.setStyleSheet(f"color: {c['alert']};")

        self._score_lbl.setText(f"Score: {self._correct}/{self._round}")
        self._answer_container.hide()

        self._after(1000, self._next_round)

    # ── Results ──

    def _show_results(self) -> None:
        self._running = False
        c = COLORS

        score = self._correct
        total = self._total_rounds
        pct = round(score / total * 100) if total > 0 else 0
        xp = score * USER_DATA_CONFIG["xp_per_correct"]

        result = ExerciseResult(
            exercise_name="PERIPHERAL FLASH",
            score=score,
            total=total,
            xp_gained=xp,
            metadata={
                "stimulus_type": self._stim_type,
                "flash_ms": self._flash_ms,
                "eccentricity": self._eccentricity,
                "accuracy_pct": pct,
            },
        )
        is_pb = self.complete(result)

        self.show_result_screen(
            result,
            is_personal_best=is_pb,
            details=(
                f"Stimulus: {self._stim_type}  |  "
                f"Flash: {self._flash_ms}ms  |  "
                f"Eccentricity: {self._eccentricity}%\n"
                f"Accuracy: {pct}%"
            ),
        )

    def _stop(self) -> None:
        self._running = False
        self.navigator.finish_exercise()
