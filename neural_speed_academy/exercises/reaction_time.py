"""
Reaction Time exercise.

Three modes measuring different aspects of response speed:
  - Simple: respond to any stimulus as fast as possible
  - Choice: respond with the correct key for the stimulus color
  - Go/No-Go: respond to targets, inhibit on distractors
Results use median RT for robustness against outliers.
"""
from __future__ import annotations

import random
import time
from statistics import median

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSlider, QComboBox,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QShortcut, QKeySequence

from neural_speed_academy.exercises.base import BaseExercise, ExerciseResult
from neural_speed_academy.theme import COLORS, make_qfont, screen_metrics
from neural_speed_academy.config import REACTION_TIME_CONFIG, USER_DATA_CONFIG


class ReactionTimeExercise(BaseExercise):

    def __init__(self, navigator, parent: QWidget | None = None):
        super().__init__(navigator, parent)
        self._round: int = 0
        self._total_rounds: int = 15
        self._mode: str = "simple"
        self._go_ratio: float = 0.7
        # Round state
        self._stimulus_time: float = 0.0
        self._waiting_for_stimulus: bool = False
        self._waiting_for_response: bool = False
        self._input_locked: bool = False
        self._is_go_trial: bool = True
        self._current_color_idx: int = 0
        self._too_early: bool = False
        # Results
        self._reaction_times: list[float] = []
        self._correct: int = 0
        self._false_alarms: int = 0
        self._misses: int = 0
        self._too_early_count: int = 0
        # UI refs
        self._arena: QWidget | None = None
        self._stimulus_lbl: QLabel | None = None
        self._instruction_lbl: QLabel | None = None
        self._progress_lbl: QLabel | None = None
        self._feedback_lbl: QLabel | None = None
        self._timeout_timer: QTimer | None = None

    @property
    def name(self) -> str:
        return "Reaction Time"

    # ── Config screen ──

    def start(self, **kwargs) -> None:
        self._clear()
        self._running = True
        self.add_nav_bar()

        cfg = REACTION_TIME_CONFIG
        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")

        self._mode = kwargs.get("mode", "simple")
        self._total_rounds = kwargs.get("rounds", cfg["default_rounds"])
        self._go_ratio = kwargs.get("go_ratio", cfg["go_ratio"])

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
            lambda: self.show_guide("reaction_time")
        )
        top.addWidget(guide_btn)
        top.addStretch()
        cl.addLayout(top)

        title = QLabel("REACTION TIME")
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

        # Mode selector
        mode_row = QHBoxLayout()
        mode_row.addStretch()
        mode_lbl = QLabel("Mode:")
        mode_lbl.setFont(make_qfont("slider_label"))
        mode_lbl.setStyleSheet(f"color: {c['fg']};")
        mode_row.addWidget(mode_lbl)

        self._mode_combo = QComboBox()
        self._mode_combo.addItems(["Simple", "Choice", "Go / No-Go"])
        idx = {"simple": 0, "choice": 1, "go_no_go": 2}.get(self._mode, 0)
        self._mode_combo.setCurrentIndex(idx)
        self._mode_combo.setStyleSheet(
            f"QComboBox {{ background-color: {c['card']}; color: {c['fg']}; "
            f"border: 1px solid {c['muted']}; padding: 4px 8px; "
            f"border-radius: 3px; }}"
            f"QComboBox::drop-down {{ border: none; }}"
            f"QComboBox QAbstractItemView {{ background-color: {c['card']}; "
            f"color: {c['fg']}; selection-background-color: {c['accent']}; }}"
        )
        self._mode_combo.setFixedWidth(180)
        mode_row.addWidget(self._mode_combo)
        mode_row.addStretch()
        cl.addLayout(mode_row)

        # Rounds
        rounds_row = QHBoxLayout()
        rounds_row.addStretch()
        rounds_lbl = QLabel("Rounds:")
        rounds_lbl.setFont(make_qfont("slider_label"))
        rounds_lbl.setStyleSheet(f"color: {c['fg']};")
        rounds_row.addWidget(rounds_lbl)

        self._rounds_slider = QSlider(Qt.Orientation.Horizontal)
        self._rounds_slider.setRange(cfg["min_rounds"], cfg["max_rounds"])
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

        cl.addSpacing(20)

        # Start button
        start_btn = QPushButton("START")
        start_btn.setFont(make_qfont("btn_lg"))
        start_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['accent']}; "
            f"color: {c['btn_text']}; border: none; "
            f"padding: 12px 50px; border-radius: 4px; }}"
        )
        start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        start_btn.clicked.connect(self._begin_exercise)
        cl.addWidget(start_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # Ctrl+Enter to start (matches other exercises)
        shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        shortcut.activated.connect(self._begin_exercise)

        cl.addStretch()
        self._layout.addWidget(container, 1)

    def _begin_exercise(self) -> None:
        self._total_rounds = self._rounds_slider.value()
        self._mode = ["simple", "choice", "go_no_go"][
            self._mode_combo.currentIndex()
        ]
        self._round = 0
        self._reaction_times = []
        self._correct = 0
        self._false_alarms = 0
        self._misses = 0
        self._too_early_count = 0
        self._build_arena()

    # ── Arena ──

    def _build_arena(self) -> None:
        self._clear()
        self._running = True

        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")

        # Top bar
        top = QHBoxLayout()
        top.setContentsMargins(10, 6, 10, 2)

        self._progress_lbl = QLabel(f"Round 0/{self._total_rounds}")
        self._progress_lbl.setFont(make_qfont("counter"))
        self._progress_lbl.setStyleSheet(f"color: {c['accent']};")
        top.addWidget(self._progress_lbl)

        top.addStretch()

        exit_btn = QPushButton("\u2716")
        exit_btn.setFont(make_qfont("exit_btn"))
        exit_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        exit_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['alert']}; "
            f"color: {c['text_on_card']}; "
            f"border: none; padding: 4px 8px; border-radius: 3px; }}"
        )
        exit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        exit_btn.clicked.connect(self._stop)
        top.addWidget(exit_btn)
        self._layout.addLayout(top)

        # Arena — clickable area
        self._arena = QWidget()
        self._arena.setStyleSheet(f"background-color: {c['bg']};")
        self._arena.setCursor(Qt.CursorShape.PointingHandCursor)
        self._arena.mousePressEvent = self._on_arena_click
        self._layout.addWidget(self._arena, 1)

        # Stimulus label (large shape in center of arena)
        self._stimulus_lbl = QLabel("", self._arena)
        self._stimulus_lbl.setFont(QFont("Arial", 120))
        self._stimulus_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._stimulus_lbl.setFixedSize(200, 200)
        self._stimulus_lbl.hide()

        # Instruction text (in arena, below stimulus)
        self._instruction_lbl = QLabel("", self._arena)
        self._instruction_lbl.setFont(make_qfont("body"))
        self._instruction_lbl.setStyleSheet(f"color: {c['muted']};")
        self._instruction_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._instruction_lbl.setFixedSize(400, 40)

        # Feedback label (in arena, near stimulus so eyes stay centered)
        self._feedback_lbl = QLabel("", self._arena)
        self._feedback_lbl.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self._feedback_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._feedback_lbl.setFixedSize(500, 40)

        # Choice mode: color legend
        if self._mode == "choice":
            legend = QHBoxLayout()
            legend.addStretch()
            cfg = REACTION_TIME_CONFIG
            for i, (color, name) in enumerate(cfg["choice_colors"]):
                key_lbl = QLabel(f"  {i + 1} = {name}  ")
                key_lbl.setFont(make_qfont("btn_sm"))
                key_lbl.setStyleSheet(
                    f"color: {color}; background-color: {c['card']}; "
                    f"border-radius: 3px; padding: 4px 8px;"
                )
                legend.addWidget(key_lbl)
            legend.addStretch()
            self._layout.addLayout(legend)

        # Grab focus so event() receives key events
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()

        self._after(1000, self._next_round)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._position_elements()

    def _position_elements(self) -> None:
        if not self._arena:
            return
        aw = self._arena.width()
        ah = self._arena.height()
        # Center stimulus
        if self._stimulus_lbl:
            sw, sh = self._stimulus_lbl.width(), self._stimulus_lbl.height()
            self._stimulus_lbl.move((aw - sw) // 2, (ah - sh) // 2)
        # Instruction below stimulus
        if self._instruction_lbl:
            iw = self._instruction_lbl.width()
            self._instruction_lbl.move(
                (aw - iw) // 2, ah // 2 + 120
            )
        # Feedback just below stimulus (close to center)
        if self._feedback_lbl:
            fw = self._feedback_lbl.width()
            self._feedback_lbl.move(
                (aw - fw) // 2, ah // 2 + 110
            )

    # ── Round logic ──

    def _next_round(self) -> None:
        if not self._running:
            return
        if self._round >= self._total_rounds:
            self._show_results()
            return

        self.setFocus()
        self._round += 1
        c = COLORS
        cfg = REACTION_TIME_CONFIG
        self._progress_lbl.setText(
            f"Round {self._round}/{self._total_rounds}"
        )
        self._feedback_lbl.setText("")
        self._feedback_lbl.setStyleSheet(f"color: {c['bg']};")
        self._too_early = False
        self._waiting_for_response = False

        self._position_elements()

        # Show fixation cross
        self._stimulus_lbl.setText("+")
        self._stimulus_lbl.setFont(QFont("Arial", 72, QFont.Weight.Bold))
        self._stimulus_lbl.setStyleSheet(
            f"color: {c['muted']}; background: transparent;"
        )
        self._stimulus_lbl.show()
        self._stimulus_lbl.repaint()

        # Instruction
        if self._mode == "simple":
            self._instruction_lbl.setText(
                "Click or press X when the circle appears"
            )
        elif self._mode == "choice":
            self._instruction_lbl.setText(
                "Press 1-4 for the color, or X to skip"
            )
        else:
            self._instruction_lbl.setText(
                "Green = Click / X  |  Red = Don't!"
            )
        self._instruction_lbl.show()

        # Random delay before stimulus — unlock input for "too early" detection
        delay = random.randint(cfg["min_delay_ms"], cfg["max_delay_ms"])
        self._waiting_for_stimulus = True
        self._input_locked = False
        self._after(delay, self._show_stimulus)

    def _show_stimulus(self) -> None:
        if not self._running:
            return

        self._waiting_for_stimulus = False
        cfg = REACTION_TIME_CONFIG
        c = COLORS

        self._stimulus_lbl.setFont(QFont("Arial", 120))
        self._instruction_lbl.hide()

        if self._mode == "simple":
            self._stimulus_lbl.setText("\u25cf")
            self._stimulus_lbl.setStyleSheet(
                "color: #2ecc71; background: transparent;"
            )
            self._is_go_trial = True

        elif self._mode == "choice":
            self._current_color_idx = random.randint(
                0, len(cfg["choice_colors"]) - 1
            )
            color, _ = cfg["choice_colors"][self._current_color_idx]
            shape_idx = random.randint(
                0, len(cfg["choice_shapes"]) - 1
            )
            self._stimulus_lbl.setText(cfg["choice_shapes"][shape_idx])
            self._stimulus_lbl.setStyleSheet(
                f"color: {color}; background: transparent;"
            )
            self._is_go_trial = True

        else:  # go_no_go
            self._is_go_trial = random.random() < self._go_ratio
            if self._is_go_trial:
                self._stimulus_lbl.setText("\u25cf")
                self._stimulus_lbl.setStyleSheet(
                    "color: #2ecc71; background: transparent;"
                )
            else:
                self._stimulus_lbl.setText("\u25cf")
                self._stimulus_lbl.setStyleSheet(
                    "color: #e74c3c; background: transparent;"
                )

        self._stimulus_lbl.raise_()
        self._stimulus_lbl.show()
        self._stimulus_lbl.repaint()

        self._stimulus_time = time.perf_counter()
        self._waiting_for_response = True
        self._input_locked = False

        # Timeout for go/no-go (also used to auto-advance no-go trials)
        if self._mode == "go_no_go":
            self._timeout_timer = self._after(
                cfg["timeout_ms"], self._on_timeout
            )
        elif self._mode == "simple":
            # Generous timeout for simple mode
            self._timeout_timer = self._after(2000, self._on_timeout)

    # ── Input handling ──

    def keyPressEvent(self, event) -> None:
        if event.isAutoRepeat():
            return
        key = event.key()
        if key in (Qt.Key.Key_1, Qt.Key.Key_2, Qt.Key.Key_3, Qt.Key.Key_4):
            self._handle_response(key - Qt.Key.Key_1)
        elif key == Qt.Key.Key_X:
            self._handle_response(-1)
        else:
            super().keyPressEvent(event)

    def _on_arena_click(self, event) -> None:
        self.setFocus()
        self._handle_response(-1)

    def _handle_response(self, choice_idx: int) -> None:
        if not self._running or self._input_locked:
            return

        c = COLORS

        # Clicked during wait period — too early
        if self._waiting_for_stimulus:
            self._too_early = True
            self._too_early_count += 1
            self._waiting_for_stimulus = False
            self._stimulus_lbl.setText("\u26a0")
            self._stimulus_lbl.setStyleSheet(
                f"color: {c['alert']}; background: transparent;"
            )
            self._stimulus_lbl.repaint()
            self._feedback_lbl.setText("Too early! Wait for the stimulus.")
            self._feedback_lbl.setStyleSheet(f"color: {c['alert']};")
            self._input_locked = True
            # Repeat this round
            self._round -= 1
            self._after(1500, self._next_round)
            return

        if not self._waiting_for_response:
            return

        self._waiting_for_response = False
        self._input_locked = True

        # Cancel timeout
        if self._timeout_timer:
            self._timeout_timer.stop()
            self._timeout_timer = None

        rt_ms = (time.perf_counter() - self._stimulus_time) * 1000

        if self._mode == "simple":
            self._reaction_times.append(rt_ms)
            self._correct += 1
            self._feedback_lbl.setText(f"{rt_ms:.0f} ms")
            self._feedback_lbl.setStyleSheet(f"color: {c['success']};")

        elif self._mode == "choice":
            if choice_idx == self._current_color_idx:
                self._reaction_times.append(rt_ms)
                self._correct += 1
                self._feedback_lbl.setText(f"\u2714 {rt_ms:.0f} ms")
                self._feedback_lbl.setStyleSheet(f"color: {c['success']};")
            else:
                cfg = REACTION_TIME_CONFIG
                correct_name = cfg["choice_colors"][
                    self._current_color_idx
                ][1]
                self._feedback_lbl.setText(
                    f"\u2718 Wrong — it was {correct_name}"
                )
                self._feedback_lbl.setStyleSheet(f"color: {c['alert']};")

        else:  # go_no_go
            if self._is_go_trial:
                self._reaction_times.append(rt_ms)
                self._correct += 1
                self._feedback_lbl.setText(f"\u2714 {rt_ms:.0f} ms")
                self._feedback_lbl.setStyleSheet(f"color: {c['success']};")
            else:
                # False alarm — clicked on no-go
                self._false_alarms += 1
                self._feedback_lbl.setText(
                    "\u2718 False alarm — don't click on red!"
                )
                self._feedback_lbl.setStyleSheet(f"color: {c['alert']};")

        self._stimulus_lbl.hide()
        self._after(1200, self._next_round)

    def _on_timeout(self) -> None:
        if not self._running or not self._waiting_for_response:
            return

        self._waiting_for_response = False
        self._input_locked = True
        c = COLORS

        if self._mode == "go_no_go":
            if self._is_go_trial:
                # Missed a go trial
                self._misses += 1
                self._feedback_lbl.setText("\u2718 Too slow — missed!")
                self._feedback_lbl.setStyleSheet(f"color: {c['alert']};")
            else:
                # Correctly inhibited on no-go
                self._correct += 1
                self._feedback_lbl.setText("\u2714 Correct — no click needed")
                self._feedback_lbl.setStyleSheet(f"color: {c['success']};")
        else:
            # Simple mode timeout
            self._misses += 1
            self._feedback_lbl.setText("\u2718 Too slow!")
            self._feedback_lbl.setStyleSheet(f"color: {c['alert']};")

        self._stimulus_lbl.hide()
        self._after(1200, self._next_round)

    # ── Results ──

    def _show_results(self) -> None:
        self._running = False
        c = COLORS

        total = self._total_rounds
        rts = self._reaction_times

        if rts:
            median_rt = median(rts)
            best_rt = min(rts)
            worst_rt = max(rts)
        else:
            median_rt = best_rt = worst_rt = 0

        accuracy_pct = (
            round(self._correct / total * 100) if total > 0 else 0
        )

        # Score ceiling per mode — choice/go-no-go need more time
        ceiling = {"simple": 500, "choice": 1000, "go_no_go": 800}.get(
            self._mode, 500
        )

        score_val = (
            max(0, ceiling - round(median_rt)) if rts else 0
        )
        xp = max(0, score_val // 10) * self._correct if rts else 0

        metadata = {
            "mode": self._mode,
            "median_rt_ms": round(median_rt),
            "best_rt_ms": round(best_rt),
            "worst_rt_ms": round(worst_rt),
            "accuracy_pct": accuracy_pct,
            "correct": self._correct,
            "total": total,
        }
        if self._mode == "go_no_go":
            metadata["false_alarms"] = self._false_alarms
            metadata["misses"] = self._misses
        if self._too_early_count > 0:
            metadata["too_early"] = self._too_early_count

        result = ExerciseResult(
            exercise_name="REACTION TIME",
            score=score_val,
            total=ceiling,
            xp_gained=xp,
            metadata=metadata,
        )
        is_pb = self.complete(result)

        # Build details string
        if self._mode == "go_no_go":
            details = (
                f"Mode: Go/No-Go  |  Rounds: {total}\n"
                f"Median RT: {median_rt:.0f} ms  |  "
                f"Best: {best_rt:.0f} ms  |  "
                f"Worst: {worst_rt:.0f} ms\n"
                f"Correct: {self._correct}  |  "
                f"False alarms: {self._false_alarms}  |  "
                f"Misses: {self._misses}"
            )
        elif self._mode == "choice":
            details = (
                f"Mode: Choice (4 colors)  |  Rounds: {total}\n"
                f"Median RT: {median_rt:.0f} ms  |  "
                f"Best: {best_rt:.0f} ms  |  "
                f"Worst: {worst_rt:.0f} ms\n"
                f"Accuracy: {accuracy_pct}%"
            )
        else:
            details = (
                f"Mode: Simple  |  Rounds: {total}\n"
                f"Median RT: {median_rt:.0f} ms  |  "
                f"Best: {best_rt:.0f} ms  |  "
                f"Worst: {worst_rt:.0f} ms"
            )

        if self._too_early_count > 0:
            details += f"\nToo early: {self._too_early_count}"

        self.show_result_screen(
            result,
            is_personal_best=is_pb,
            details=details,
        )

        # Rewire CONTINUE button to go back to menu instead of dashboard
        for btn in self.findChildren(QPushButton):
            if btn.text() == "CONTINUE":
                btn.disconnect()
                btn.clicked.connect(
                    lambda: self.navigator.navigate_to("reaction_time_menu")
                )

    def _stop(self) -> None:
        self._running = False
        self._waiting_for_stimulus = False
        self._waiting_for_response = False
        self._input_locked = True
        # Stop all timers to prevent delayed callbacks
        for timer in self._timers:
            timer.stop()
        self._timers.clear()
        if self._timeout_timer:
            self._timeout_timer.stop()
            self._timeout_timer = None
        self.navigator.navigate_to("reaction_time_menu")
