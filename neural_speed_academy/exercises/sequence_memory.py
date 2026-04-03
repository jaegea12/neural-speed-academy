"""
Sequence Memory exercise: memorize and reproduce sequences of increasing length.

Modes:
  - numbers: digit sequences (0-9)
  - words: common short words
  - mixed: numbers and words interleaved

Uses a staircase method: length increases on correct recall, decreases on error.
"""
from __future__ import annotations

import random

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGridLayout, QFrame,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut

from neural_speed_academy.exercises.base import BaseExercise, ExerciseResult
from neural_speed_academy.theme import COLORS, make_qfont, font_css, theme_manager
from neural_speed_academy.config import USER_DATA_CONFIG

# Word pool for word/mixed modes — short, common, easy to distinguish
WORD_POOL = [
    "sun", "tree", "fish", "book", "star", "rain", "fire", "moon",
    "bird", "lake", "wind", "rock", "leaf", "snow", "bell", "door",
    "ship", "ring", "lamp", "hill", "wave", "seed", "gold", "iron",
    "dust", "clay", "silk", "foam", "nest", "path", "rope", "drum",
]

SEQUENCE_CONFIG = {
    "min_length": 3,
    "max_length": 15,
    "flash_ms": 800,       # time each item is shown
    "gap_ms": 200,         # gap between items
    "max_rounds": 10,
}


class SequenceMemoryExercise(BaseExercise):

    def __init__(self, navigator, parent: QWidget | None = None):
        super().__init__(navigator, parent)
        self.mode: str = "numbers"
        self.seq_length: int = SEQUENCE_CONFIG["min_length"]
        self.max_reached: int = 0
        self.round_num: int = 0
        self.max_rounds: int = SEQUENCE_CONFIG["max_rounds"]
        self.correct_count: int = 0
        self._sequence: list[str] = []
        self._user_input: list[str] = []
        self._flash_idx: int = 0
        self._flash_ms: int = SEQUENCE_CONFIG["flash_ms"]

    def start(self, mode: str = "numbers", start_length: int = 3,
              flash_ms: int = 800, rounds: int = 10, **kwargs) -> None:
        self.mode = mode
        self.seq_length = max(start_length, SEQUENCE_CONFIG["min_length"])
        self.max_reached = 0
        self.round_num = 0
        self.max_rounds = rounds
        self.correct_count = 0
        self._flash_ms = flash_ms
        self._next_round()

    # ── Round flow ──

    def _next_round(self) -> None:
        if self.round_num >= self.max_rounds:
            self._complete_exercise()
            return

        self.round_num += 1
        self._sequence = self._generate_sequence()
        self._user_input = []
        self._flash_idx = 0
        self._show_flash_phase()

    def _generate_sequence(self) -> list[str]:
        length = min(self.seq_length, SEQUENCE_CONFIG["max_length"])
        if self.mode == "numbers":
            return [str(random.randint(0, 9)) for _ in range(length)]
        elif self.mode == "words":
            return random.sample(WORD_POOL, min(length, len(WORD_POOL)))
        else:  # mixed
            items = []
            for _ in range(length):
                if random.random() < 0.5:
                    items.append(str(random.randint(0, 9)))
                else:
                    items.append(random.choice(WORD_POOL))
            return items

    # ── Flash phase: show items one at a time ──

    def _show_flash_phase(self) -> None:
        self._clear()
        self._running = True

        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")

        # Exit button
        exit_btn = QPushButton("\u2716")
        exit_btn.setFont(make_qfont("exit_btn"))
        exit_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['alert']}; color: {c['text_on_card']}; "
            f"border: none; padding: 4px 8px; border-radius: 3px; }}"
        )
        exit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        exit_btn.clicked.connect(self._stop)
        self._layout.addWidget(exit_btn, alignment=Qt.AlignmentFlag.AlignRight)

        # Status
        status = QLabel(
            f"Round {self.round_num}/{self.max_rounds}  |  "
            f"Length: {self.seq_length}  |  {self.mode.upper()}"
        )
        status.setFont(make_qfont("btn_sm"))
        status.setStyleSheet(f"color: {c['muted']};")
        status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(status)

        self._layout.addStretch()

        # Instruction
        inst = QLabel("MEMORIZE")
        inst.setFont(make_qfont("section_header"))
        inst.setStyleSheet(f"color: {c['accent']};")
        inst.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(inst)

        # Flash display
        self._flash_label = QLabel("")
        self._flash_label.setFont(make_qfont("flash"))
        self._flash_label.setStyleSheet(f"color: {c['fg']};")
        self._flash_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._flash_label.setMinimumHeight(120)
        self._layout.addWidget(self._flash_label)

        # Progress dots
        self._dots_label = QLabel("")
        self._dots_label.setFont(make_qfont("btn_sm"))
        self._dots_label.setStyleSheet(f"color: {c['muted']};")
        self._dots_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(self._dots_label)

        self._layout.addStretch()

        self._flash_idx = 0
        self._flash_next_item()

    def _flash_next_item(self) -> None:
        if not self._running:
            return
        if self._flash_idx >= len(self._sequence):
            # Brief pause then show recall phase
            self._flash_label.setText("")
            self._after(400, self._show_recall_phase)
            return

        c = COLORS
        item = self._sequence[self._flash_idx]
        self._flash_label.setText(item)
        self._flash_label.setStyleSheet(f"color: {c['fg']};")

        # Update dots
        dots = ""
        for i in range(len(self._sequence)):
            if i == self._flash_idx:
                dots += " \u25cf"
            elif i < self._flash_idx:
                dots += " \u25cb"
            else:
                dots += " \u25cb"
        self._dots_label.setText(dots.strip())

        self._flash_idx += 1
        # Show item, then brief gap, then next
        self._after(self._flash_ms, self._flash_gap)

    def _flash_gap(self) -> None:
        if not self._running:
            return
        self._flash_label.setText("")
        self._after(SEQUENCE_CONFIG["gap_ms"], self._flash_next_item)

    # ── Recall phase: user reproduces the sequence ──

    def _show_recall_phase(self) -> None:
        if not self._running:
            return

        self._clear()
        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")

        # Exit button
        exit_btn = QPushButton("\u2716")
        exit_btn.setFont(make_qfont("exit_btn"))
        exit_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['alert']}; color: {c['text_on_card']}; "
            f"border: none; padding: 4px 8px; border-radius: 3px; }}"
        )
        exit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        exit_btn.clicked.connect(self._stop)
        self._layout.addWidget(exit_btn, alignment=Qt.AlignmentFlag.AlignRight)

        # Instruction
        inst = QLabel("RECALL THE SEQUENCE")
        inst.setFont(make_qfont("section_header"))
        inst.setStyleSheet(f"color: {c['accent']};")
        inst.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(inst)

        # Show what user has entered so far
        self._input_display = QLabel("")
        self._input_display.setFont(make_qfont("counter"))
        self._input_display.setStyleSheet(f"color: {c['fg']};")
        self._input_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._input_display.setMinimumHeight(60)
        self._layout.addWidget(self._input_display)

        # Progress indicator
        self._recall_progress = QLabel(
            f"0 / {len(self._sequence)}"
        )
        self._recall_progress.setFont(make_qfont("btn_sm"))
        self._recall_progress.setStyleSheet(f"color: {c['muted']};")
        self._recall_progress.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(self._recall_progress)

        self._layout.addSpacing(10)

        # Build input buttons based on mode
        self._user_input = []
        if self.mode == "numbers":
            self._build_number_pad(c)
        elif self.mode == "words":
            self._build_word_buttons(c)
        else:
            self._build_mixed_buttons(c)

        self._layout.addSpacing(10)

        # Undo button
        undo_btn = QPushButton("UNDO")
        undo_btn.setFont(make_qfont("btn_sm"))
        undo_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['card']}; color: {c['fg']}; "
            f"border: none; padding: 6px 20px; border-radius: 4px; }}"
            f"QPushButton:hover {{ background-color: {c['bg']}; }}"
        )
        undo_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        undo_btn.clicked.connect(self._undo_input)
        self._layout.addWidget(undo_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self._layout.addStretch()

    def _build_number_pad(self, c: dict) -> None:
        grid = QGridLayout()
        grid.setSpacing(6)
        pad_widget = QFrame()
        pad_widget.setStyleSheet("background: transparent;")
        pad_layout = QVBoxLayout(pad_widget)
        pad_layout.addLayout(grid)

        for i in range(10):
            row, col = divmod(i, 5)
            btn = QPushButton(str(i))
            btn.setFixedSize(60, 50)
            btn.setFont(make_qfont("btn_bold"))
            btn.setStyleSheet(
                f"QPushButton {{ background-color: {c['card']}; color: {c['fg']}; "
                f"border: none; border-radius: 4px; }}"
                f"QPushButton:hover {{ background-color: {c['accent']}; color: {c['btn_text']}; }}"
            )
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, v=str(i): self._add_input(v))
            grid.addWidget(btn, row, col)

        self._layout.addWidget(pad_widget, alignment=Qt.AlignmentFlag.AlignCenter)

    def _build_word_buttons(self, c: dict) -> None:
        # Show only words from the sequence (exclude numbers in mixed mode)
        options = [w for w in self._sequence if not w.isdigit()]
        # Add some distractors
        distractors = [w for w in WORD_POOL if w not in options]
        n_distractors = min(len(options), len(distractors))
        options.extend(random.sample(distractors, n_distractors))
        random.shuffle(options)

        grid = QGridLayout()
        grid.setSpacing(6)
        cols = min(4, len(options))
        for i, word in enumerate(options):
            row, col = divmod(i, cols)
            btn = QPushButton(word)
            btn.setFixedSize(100, 44)
            btn.setFont(make_qfont("btn"))
            btn.setStyleSheet(
                f"QPushButton {{ background-color: {c['card']}; color: {c['fg']}; "
                f"border: none; border-radius: 4px; }}"
                f"QPushButton:hover {{ background-color: {c['accent']}; color: {c['btn_text']}; }}"
            )
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, v=word: self._add_input(v))
            grid.addWidget(btn, row, col)

        grid_widget = QFrame()
        grid_widget.setStyleSheet("background: transparent;")
        gl = QVBoxLayout(grid_widget)
        gl.addLayout(grid)
        self._layout.addWidget(grid_widget, alignment=Qt.AlignmentFlag.AlignCenter)

    def _build_mixed_buttons(self, c: dict) -> None:
        # Combine number pad and word buttons
        self._build_number_pad(c)
        self._layout.addSpacing(6)
        self._build_word_buttons(c)

    def _add_input(self, value: str) -> None:
        self._user_input.append(value)
        c = COLORS
        self._input_display.setText("  ".join(self._user_input))
        self._recall_progress.setText(
            f"{len(self._user_input)} / {len(self._sequence)}"
        )

        if len(self._user_input) >= len(self._sequence):
            self._evaluate()

    def _undo_input(self) -> None:
        if self._user_input:
            self._user_input.pop()
            self._input_display.setText("  ".join(self._user_input))
            self._recall_progress.setText(
                f"{len(self._user_input)} / {len(self._sequence)}"
            )

    # ── Evaluation ──

    def _evaluate(self) -> None:
        correct = self._user_input == self._sequence
        if correct:
            self.correct_count += 1
            self.max_reached = max(self.max_reached, self.seq_length)
            self.seq_length = min(
                self.seq_length + 1, SEQUENCE_CONFIG["max_length"]
            )
        else:
            self.seq_length = max(
                self.seq_length - 1, SEQUENCE_CONFIG["min_length"]
            )

        self._show_feedback(correct)

    def _show_feedback(self, correct: bool) -> None:
        self._clear()
        c = COLORS

        self.setStyleSheet(f"background-color: {c['bg']};")
        self._layout.addStretch()

        if correct:
            icon = QLabel("\u2714")
            icon.setFont(make_qfont("flash"))
            icon.setStyleSheet(f"color: {c['success']};")
            icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._layout.addWidget(icon)

            msg = QLabel("CORRECT")
            msg.setFont(make_qfont("header"))
            msg.setStyleSheet(f"color: {c['success']};")
        else:
            icon = QLabel("\u2718")
            icon.setFont(make_qfont("flash"))
            icon.setStyleSheet(f"color: {c['alert']};")
            icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._layout.addWidget(icon)

            msg = QLabel("INCORRECT")
            msg.setFont(make_qfont("header"))
            msg.setStyleSheet(f"color: {c['alert']};")

        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(msg)

        # Show the correct sequence
        seq_text = "  ".join(self._sequence)
        answer = QLabel(f"Sequence: {seq_text}")
        answer.setFont(make_qfont("body"))
        answer.setStyleSheet(f"color: {c['fg']};")
        answer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(answer)

        if not correct:
            user_text = "  ".join(self._user_input)
            yours = QLabel(f"Your input: {user_text}")
            yours.setFont(make_qfont("body"))
            yours.setStyleSheet(f"color: {c['muted']};")
            yours.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._layout.addWidget(yours)

        self._layout.addSpacing(20)

        cont_btn = QPushButton("CONTINUE")
        cont_btn.setFont(make_qfont("btn_bold"))
        cont_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['accent']}; color: {c['btn_text']}; "
            f"border: none; padding: 8px 40px; border-radius: 4px; }}"
        )
        cont_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cont_btn.clicked.connect(self._next_round)
        self._layout.addWidget(cont_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self._layout.addStretch()

    # ── Completion ──

    def _complete_exercise(self) -> None:
        self._running = False
        xp = self.correct_count * USER_DATA_CONFIG["xp_per_correct"]
        result = ExerciseResult(
            exercise_name="SEQUENCE_MEMORY",
            score=self.correct_count,
            total=self.max_rounds,
            xp_gained=xp,
            metadata={
                "mode": self.mode,
                "max_length_reached": self.max_reached,
                "final_length": self.seq_length,
                "rounds": self.max_rounds,
                "flash_ms": self._flash_ms,
            },
        )
        is_pb = self.complete(result)
        self.show_result_screen(
            result, is_personal_best=is_pb,
            details=f"Max sequence length: {self.max_reached}",
        )

    def _stop(self) -> None:
        self._running = False
        self.navigator.finish_exercise()

    def _stop_exercise(self) -> None:
        """Called by global Esc handler."""
        self._stop()
