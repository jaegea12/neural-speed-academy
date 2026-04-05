"""
Split Attention exercise.

Dual-task training: identify a briefly flashed word while detecting a
colored shape in the periphery. Three modes:
  - Sequential: center word first, then peripheral shape
  - Simultaneous: both at center, shown at once
  - Rapid: word at random position, both simultaneous, plus a
    "where did the word appear?" quadrant question (3 tasks scored)
"""
from __future__ import annotations

import logging
import random

logger = logging.getLogger(__name__)

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSlider, QComboBox, QGridLayout,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from neural_speed_academy.exercises.base import BaseExercise, ExerciseResult
from neural_speed_academy.theme import COLORS, make_qfont, btn_css
from neural_speed_academy.config import (
    SPLIT_ATTENTION_CONFIG, WORD_PAIRS, USER_DATA_CONFIG,
)


class SplitAttentionExercise(BaseExercise):

    def __init__(self, navigator, parent: QWidget | None = None):
        super().__init__(navigator, parent)
        self._round: int = 0
        self._total_rounds: int = 15
        self._center_ms: int = 400
        self._peripheral_ms: int = 300
        self._mode: str = "sequential"  # sequential | simultaneous | rapid
        self._center_correct: int = 0
        self._periph_correct: int = 0
        # Current round state
        self._correct_word: str = ""
        self._wrong_word: str = ""
        self._correct_shape: str = ""
        self._correct_shape_name: str = ""
        self._shape_color: str = ""
        # UI refs
        self._arena: QWidget | None = None
        self._fixation: QLabel | None = None
        self._center_lbl: QLabel | None = None
        self._periph_lbl: QLabel | None = None
        self._progress_lbl: QLabel | None = None
        self._score_lbl: QLabel | None = None
        self._answer_container: QWidget | None = None
        self._answer_layout: QVBoxLayout | None = None
        self._feedback_lbl: QLabel | None = None
        # Answer tracking
        self._center_answered: bool = False
        self._periph_answered: bool = False
        self._center_was_correct: bool = False

    @property
    def name(self) -> str:
        return "Split Attention"

    # ── Config screen ──

    def start(self, **kwargs) -> None:
        self._clear()
        self._running = True
        self.add_nav_bar()

        cfg = SPLIT_ATTENTION_CONFIG
        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")

        self._center_ms = kwargs.get("center_ms", cfg["default_center_ms"])
        self._peripheral_ms = kwargs.get(
            "peripheral_ms", cfg["default_peripheral_ms"]
        )
        self._total_rounds = kwargs.get("rounds", cfg["default_rounds"])
        self._mode = kwargs.get("mode", "sequential")

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
            f"border: 2px solid transparent; padding: 4px 12px; border-radius: 3px;"
        )
        guide_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        guide_btn.clicked.connect(
            lambda: self.show_guide("split_attention")
        )
        top.addWidget(guide_btn)
        top.addStretch()
        cl.addLayout(top)

        title = QLabel("SPLIT ATTENTION")
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
        self._mode_combo.addItems(["Sequential", "Simultaneous", "Rapid"])
        idx = {"sequential": 0, "simultaneous": 1, "rapid": 2}.get(
            self._mode, 0
        )
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

        # Center flash duration
        center_row = QHBoxLayout()
        center_row.addStretch()
        center_lbl = QLabel("Word flash (ms):")
        center_lbl.setFont(make_qfont("slider_label"))
        center_lbl.setStyleSheet(f"color: {c['fg']};")
        center_row.addWidget(center_lbl)

        self._center_slider = QSlider(Qt.Orientation.Horizontal)
        self._center_slider.setRange(
            cfg["min_center_ms"], cfg["max_center_ms"]
        )
        self._center_slider.setValue(self._center_ms)
        self._center_slider.setFixedWidth(250)
        self._center_slider.setStyleSheet(slider_groove)

        self._center_display = QLabel(str(self._center_ms))
        self._center_display.setFont(make_qfont("counter"))
        self._center_display.setStyleSheet(f"color: {c['accent']};")
        self._center_display.setFixedWidth(50)
        self._center_slider.valueChanged.connect(
            lambda v: self._center_display.setText(str(v))
        )
        center_row.addWidget(self._center_slider)
        center_row.addWidget(self._center_display)
        center_row.addStretch()
        cl.addLayout(center_row)

        # Peripheral flash duration
        periph_row = QHBoxLayout()
        periph_row.addStretch()
        periph_lbl = QLabel("Shape flash (ms):")
        periph_lbl.setFont(make_qfont("slider_label"))
        periph_lbl.setStyleSheet(f"color: {c['fg']};")
        periph_row.addWidget(periph_lbl)

        self._periph_slider = QSlider(Qt.Orientation.Horizontal)
        self._periph_slider.setRange(
            cfg["min_peripheral_ms"], cfg["max_peripheral_ms"]
        )
        self._periph_slider.setValue(self._peripheral_ms)
        self._periph_slider.setFixedWidth(250)
        self._periph_slider.setStyleSheet(slider_groove)

        self._periph_display = QLabel(str(self._peripheral_ms))
        self._periph_display.setFont(make_qfont("counter"))
        self._periph_display.setStyleSheet(f"color: {c['accent']};")
        self._periph_display.setFixedWidth(50)
        self._periph_slider.valueChanged.connect(
            lambda v: self._periph_display.setText(str(v))
        )
        periph_row.addWidget(self._periph_slider)
        periph_row.addWidget(self._periph_display)
        periph_row.addStretch()
        cl.addLayout(periph_row)

        # Rounds
        rounds_row = QHBoxLayout()
        rounds_row.addStretch()
        rounds_lbl = QLabel("Rounds:")
        rounds_lbl.setFont(make_qfont("slider_label"))
        rounds_lbl.setStyleSheet(f"color: {c['fg']};")
        rounds_row.addWidget(rounds_lbl)

        self._rounds_slider = QSlider(Qt.Orientation.Horizontal)
        self._rounds_slider.setRange(
            cfg["min_rounds"], cfg["max_rounds"]
        )
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
            f"color: {c['btn_text']}; border: 2px solid transparent; "
            f"padding: 12px 50px; border-radius: 4px; }}"
        )
        start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        start_btn.clicked.connect(self._begin_exercise)
        cl.addWidget(start_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        cl.addStretch()
        self._layout.addWidget(container, 1)

    def _begin_exercise(self) -> None:
        self._center_ms = self._center_slider.value()
        self._peripheral_ms = self._periph_slider.value()
        self._total_rounds = self._rounds_slider.value()
        self._mode = ["sequential", "simultaneous", "rapid"][
            self._mode_combo.currentIndex()
        ]
        self._round = 0
        self._center_correct = 0
        self._periph_correct = 0
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

        self._score_lbl = QLabel("Center: 0  |  Peripheral: 0")
        self._score_lbl.setFont(make_qfont("counter"))
        self._score_lbl.setStyleSheet(f"color: {c['fg']};")
        top.addWidget(self._score_lbl)

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
        exit_btn.clicked.connect(self._stop)
        top.addWidget(exit_btn)
        self._layout.addLayout(top)

        # Arena
        self._arena = QWidget()
        self._arena.setStyleSheet(f"background-color: {c['bg']};")
        self._layout.addWidget(self._arena, 1)

        # Fixation cross
        self._fixation = QLabel("+", self._arena)
        self._fixation.setFont(QFont("Arial", 48, QFont.Weight.Bold))
        self._fixation.setStyleSheet(
            f"color: {c['fg']}; background: transparent;"
        )
        self._fixation.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._fixation.setFixedSize(60, 60)

        # Center word label (hidden until flash)
        self._center_lbl = QLabel("", self._arena)
        self._center_lbl.setFont(QFont("Arial", 36, QFont.Weight.Bold))
        self._center_lbl.setStyleSheet(
            f"color: {c['fg']}; background: transparent;"
        )
        self._center_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._center_lbl.hide()

        # Peripheral shape label (hidden until flash)
        self._periph_lbl = QLabel("", self._arena)
        self._periph_lbl.setFont(QFont("Arial", 42, QFont.Weight.Bold))
        self._periph_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._periph_lbl.setFixedSize(80, 80)
        self._periph_lbl.hide()

        # Answer area — takes full stretch when visible (arena hidden)
        self._answer_container = QWidget()
        self._answer_container.setStyleSheet(
            f"background-color: {c['bg']};"
        )
        al = QVBoxLayout(self._answer_container)
        al.setSpacing(10)
        al.addStretch(1)
        self._answer_inner = QVBoxLayout()
        self._answer_inner.setSpacing(10)
        al.addLayout(self._answer_inner)
        # Feedback label inside the answer area
        self._feedback_lbl = QLabel("")
        self._feedback_lbl.setFont(make_qfont("btn_bold"))
        self._feedback_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._feedback_lbl.setFixedHeight(30)
        al.addWidget(self._feedback_lbl)
        al.addStretch(1)
        self._answer_layout = self._answer_inner
        self._answer_container.hide()
        self._layout.addWidget(self._answer_container, 1)

        self._after(800, self._next_round)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._position_elements()

    def _position_elements(self) -> None:
        if not self._arena or not self._fixation:
            return
        aw = self._arena.width()
        ah = self._arena.height()
        # Center fixation
        fw, fh = self._fixation.width(), self._fixation.height()
        self._fixation.move((aw - fw) // 2, (ah - fh) // 2)
        # Word label sizing (position set per-round for rapid mode)
        if self._center_lbl:
            lbl_w = min(aw - 40, 600)
            lbl_h = 60
            self._center_lbl.setFixedSize(lbl_w, lbl_h)
            if self._mode != "rapid":
                self._center_lbl.move(
                    (aw - lbl_w) // 2, (ah - lbl_h) // 2
                )

    # ── Round logic ──

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
        self._arena.show()
        self._center_answered = False
        self._periph_answered = False
        self._center_was_correct = False

        self._position_elements()

        # Pick word pair
        pair = random.choice(WORD_PAIRS)
        self._correct_word = pair[0]
        self._wrong_word = pair[1]
        if random.random() < 0.5:
            self._correct_word, self._wrong_word = (
                self._wrong_word, self._correct_word
            )

        # Pick shape + color
        cfg = SPLIT_ATTENTION_CONFIG
        shape_idx = random.randint(0, len(cfg["shapes"]) - 1)
        self._correct_shape = cfg["shapes"][shape_idx]
        self._correct_shape_name = cfg["shape_names"][shape_idx]
        self._shape_color = random.choice(cfg["shape_colors"])

        # Position peripheral stimulus
        dx, dy = random.choice(cfg["peripheral_directions"])
        aw = self._arena.width()
        ah = self._arena.height()
        cx, cy = aw // 2, ah // 2
        ecc_frac = cfg["eccentricity"] / 100.0
        sx = int(cx + dx * ecc_frac * (aw // 2 - 50))
        sy = int(cy + dy * ecc_frac * (ah // 2 - 50))
        sw = self._periph_lbl.width()
        sh = self._periph_lbl.height()
        sx = max(0, min(sx - sw // 2, aw - sw))
        sy = max(0, min(sy - sh // 2, ah - sh))

        self._periph_lbl.setText(self._correct_shape)
        self._periph_lbl.setStyleSheet(
            f"color: {self._shape_color}; background: transparent;"
        )
        self._periph_lbl.move(sx, sy)

        # Prepare center word
        self._center_lbl.setText(self._correct_word)

        # In rapid mode, place word at a random position in the arena
        if self._mode == "rapid":
            lbl_w = self._center_lbl.width()
            lbl_h = self._center_lbl.height()
            margin = 20
            wx = random.randint(margin, max(margin, aw - lbl_w - margin))
            wy = random.randint(margin, max(margin, ah - lbl_h - margin))
            self._center_lbl.move(wx, wy)

        # Show fixation, then flash
        self._center_lbl.hide()
        self._periph_lbl.hide()

        if self._mode == "rapid":
            # Brief fixation to let eyes settle after traveling from buttons
            self._fixation.show()
            self._after(400, self._flash_stimuli)
        else:
            self._fixation.show()
            self._after(800, self._flash_stimuli)

    def _flash_stimuli(self) -> None:
        if not self._running:
            return

        self._fixation.hide()

        if self._mode in ("simultaneous", "rapid"):
            # Show both at once — raise to front and force repaint
            self._center_lbl.raise_()
            self._periph_lbl.raise_()
            self._center_lbl.show()
            self._periph_lbl.show()
            self._center_lbl.repaint()
            self._periph_lbl.repaint()
            # Hide center after center_ms
            self._after(self._center_ms, self._hide_center)
            # Hide peripheral after peripheral_ms
            self._after(self._peripheral_ms, self._hide_peripheral)
            # Pause before questions
            pause = 200 if self._mode == "rapid" else 400
            ask_delay = max(self._center_ms, self._peripheral_ms) + pause
            self._after(ask_delay, self._ask_center)
        else:
            # Sequential: center first, then peripheral
            self._center_lbl.raise_()
            self._center_lbl.show()
            self._center_lbl.repaint()
            self._after(self._center_ms, self._seq_hide_center)

    def _hide_center(self) -> None:
        if self._center_lbl:
            self._center_lbl.hide()

    def _hide_peripheral(self) -> None:
        if self._periph_lbl:
            self._periph_lbl.hide()

    def _seq_hide_center(self) -> None:
        """Sequential mode: hide center, brief pause, then show peripheral."""
        if not self._running:
            return
        self._center_lbl.hide()
        self._after(300, self._seq_show_peripheral)

    def _seq_show_peripheral(self) -> None:
        if not self._running:
            return
        self._periph_lbl.raise_()
        self._periph_lbl.show()
        self._periph_lbl.repaint()
        self._after(self._peripheral_ms, self._seq_hide_peripheral)

    def _seq_hide_peripheral(self) -> None:
        if not self._running:
            return
        self._periph_lbl.hide()
        self._after(400, self._ask_center)

    # ── Answer phase ──

    def _ask_center(self) -> None:
        """Show word choices (center task)."""
        if not self._running:
            return

        c = COLORS
        self._arena.hide()
        self._answer_container.show()
        self._clear_answer_area()

        prompt = QLabel("Which word was shown?")
        prompt.setFont(make_qfont("body"))
        prompt.setStyleSheet(f"color: {c['fg']};")
        prompt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._answer_layout.addWidget(prompt)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        btn_row.addStretch()

        choices = [self._correct_word, self._wrong_word]
        random.shuffle(choices)

        for word in choices:
            btn = QPushButton(word)
            btn.setFont(make_qfont("btn_bold"))
            btn.setFixedWidth(200)
            btn.setStyleSheet(
                f"QPushButton {{ background-color: {c['card']}; "
                f"color: {c['fg']}; border: 1px solid {c['muted']}; "
                f"padding: 10px; border-radius: 4px; }}"
                f"QPushButton:hover {{ background-color: {c['accent']}; "
                f"color: {c['btn_text']}; }}"
            )
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(
                lambda _, w=word: self._check_center(w)
            )
            btn_row.addWidget(btn)

        btn_row.addStretch()
        self._answer_layout.addLayout(btn_row)

    def _check_center(self, chosen: str) -> None:
        if not self._running or self._center_answered:
            return
        self._center_answered = True
        self._center_was_correct = (chosen == self._correct_word)
        logger.debug(
            "center: chose=%r correct=%r match=%s",
            chosen, self._correct_word, self._center_was_correct,
        )

        if self._center_was_correct:
            self._center_correct += 1

        self._ask_peripheral()

    def _ask_peripheral(self) -> None:
        """Show shape choices (peripheral task)."""
        if not self._running:
            return

        c = COLORS
        cfg = SPLIT_ATTENTION_CONFIG
        self._clear_answer_area()

        prompt = QLabel("Which shape appeared at the edge?")
        prompt.setFont(make_qfont("body"))
        prompt.setStyleSheet(f"color: {c['fg']};")
        prompt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._answer_layout.addWidget(prompt)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        # All shapes as choices
        for i, shape_name in enumerate(cfg["shape_names"]):
            symbol = cfg["shapes"][i]
            btn = QPushButton(f"{symbol}  {shape_name}")
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
            btn.clicked.connect(
                lambda _, sn=shape_name: self._check_peripheral(sn)
            )
            btn_row.addWidget(btn)

        btn_row.addStretch()
        self._answer_layout.addLayout(btn_row)

    def _check_peripheral(self, chosen: str) -> None:
        if not self._running or self._periph_answered:
            return
        self._periph_answered = True

        c = COLORS
        periph_ok = chosen == self._correct_shape_name
        if periph_ok:
            self._periph_correct += 1

        # Update score display
        self._score_lbl.setText(
            f"Word: {self._center_correct}  |  "
            f"Shape: {self._periph_correct}"
        )

        # Combined feedback — show per-task result
        center_mark = "\u2714" if self._center_was_correct else "\u2718"
        periph_mark = "\u2714" if periph_ok else "\u2718"
        center_color = c["success"] if self._center_was_correct else c["alert"]
        periph_color = c["success"] if periph_ok else c["alert"]
        self._feedback_lbl.setText("")
        self._feedback_lbl.setStyleSheet("")
        self._feedback_lbl.setText(
            f'<span style="color:{center_color}">'
            f"{center_mark} Word: {self._correct_word}</span>"
            f"  |  "
            f'<span style="color:{periph_color}">'
            f"{periph_mark} Shape: "
            f"{self._correct_shape} {self._correct_shape_name}</span>"
        )
        logger.debug(
            "peripheral: chose=%r correct=%r match=%s | center_was=%s",
            chosen, self._correct_shape_name, periph_ok,
            self._center_was_correct,
        )

        self._clear_answer_area()
        self._after(1000, self._next_round)

    def _clear_answer_area(self) -> None:
        if not self._answer_layout:
            return
        self._remove_layout_items(self._answer_layout)

    @staticmethod
    def _remove_layout_items(layout) -> None:
        """Recursively remove all items from a layout."""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                SplitAttentionExercise._remove_layout_items(item.layout())

    # ── Results ──

    def _show_results(self) -> None:
        self._running = False
        c = COLORS

        total = self._total_rounds
        center_pct = (
            round(self._center_correct / total * 100) if total > 0 else 0
        )
        periph_pct = (
            round(self._periph_correct / total * 100) if total > 0 else 0
        )

        combined = self._center_correct + self._periph_correct
        combined_total = total * 2

        combined_pct = (
            round(combined / combined_total * 100)
            if combined_total > 0 else 0
        )
        xp = combined * USER_DATA_CONFIG["xp_per_correct"]

        result = ExerciseResult(
            exercise_name="SPLIT ATTENTION",
            score=combined,
            total=combined_total,
            xp_gained=xp,
            metadata={
                "mode": self._mode,
                "center_ms": self._center_ms,
                "peripheral_ms": self._peripheral_ms,
                "center_accuracy_pct": center_pct,
                "peripheral_accuracy_pct": periph_pct,
                "combined_accuracy_pct": combined_pct,
            },
        )
        is_pb = self.complete(result)

        self.show_result_screen(
            result,
            is_personal_best=is_pb,
            details=(
                f"Mode: {self._mode}  |  "
                f"Word flash: {self._center_ms}ms  |  "
                f"Shape flash: {self._peripheral_ms}ms\n"
                f"Word accuracy: {center_pct}%  |  "
                f"Shape accuracy: {periph_pct}%\n"
                f"Combined: {combined_pct}%"
            ),
        )

    def _stop(self) -> None:
        self._running = False
        self.navigator.finish_exercise()
