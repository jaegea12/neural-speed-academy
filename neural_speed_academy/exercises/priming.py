"""
Eye Priming exercises: structured saccades, smooth pursuit, and figure-8 tracking.
All modes target ~45 seconds duration for an effective warmup.
"""
from __future__ import annotations

import math

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt

from neural_speed_academy.exercises.base import BaseExercise
from neural_speed_academy.theme import COLORS, make_qfont

MODE_LABELS = {
    "saccade_h": "HORIZONTAL SACCADES",
    "saccade_v": "VERTICAL SACCADES",
    "saccade_diag": "DIAGONAL SACCADES",
    "saccade_expand": "EXPANDING SACCADES",
    "pursuit_line": "SMOOTH PURSUIT \u2014 LINE",
    "pursuit_circle": "SMOOTH PURSUIT \u2014 CIRCLE",
    "pursuit_figure8": "SMOOTH PURSUIT \u2014 FIGURE 8",
}


class PrimingExercise(BaseExercise):

    def __init__(self, navigator, parent: QWidget | None = None):
        super().__init__(navigator, parent)
        self.mode: str = ""
        self.duration_s: float = 45.0
        self.delay: int = 600
        self._pattern: list = []
        self._pattern_idx: int = 0
        self._t: float = 0.0
        self._dt: float = 0.0
        self._pursuit_steps: int = 0
        self._pursuit_step: int = 0
        self._frame_ms: int = 20
        self._cycles: int = 3

    @property
    def name(self) -> str:
        return "Eye Priming"

    def start(self, mode: str = "saccade_h", delay: int = 600,
              duration_s: float = 45.0, cycles: int = 0, **kwargs) -> None:
        self.mode = mode
        self.delay = delay
        self.duration_s = duration_s
        self._requested_cycles = cycles

        self._clear()
        self._running = True
        self.add_nav_bar()

        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")

        guide_btn = QPushButton("GUIDE")
        guide_btn.setFont(make_qfont("btn_sm"))
        guide_btn.setStyleSheet(
            f"background-color: {c['accent']}; color: {c['btn_text']}; "
            f"border: 2px solid transparent; padding: 4px 12px; border-radius: 3px;"
        )
        guide_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        guide_btn.clicked.connect(lambda: self.show_guide("priming"))
        self._layout.addWidget(guide_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        self._lbl_mode = QLabel(MODE_LABELS.get(mode, mode.upper()))
        self._lbl_mode.setFont(make_qfont("counter"))
        self._lbl_mode.setStyleSheet(f"color: {c['accent']};")
        self._lbl_mode.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(self._lbl_mode)

        self._lbl_progress = QLabel("0%")
        self._lbl_progress.setFont(make_qfont("section_header"))
        self._lbl_progress.setStyleSheet(f"color: {c['fg']};")
        self._lbl_progress.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(self._lbl_progress)

        # Canvas area for the dot
        self._canvas = QWidget()
        self._canvas.setStyleSheet(f"background-color: {c['bg']};")
        self._canvas.setMinimumSize(800, 500)
        self._layout.addWidget(self._canvas, 1)

        self._dot = QLabel("\u25cf", self._canvas)
        self._dot.setFont(make_qfont("priming_dot"))
        self._dot.setStyleSheet(f"color: {c['priming']};")
        self._dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._dot.setFixedSize(40, 40)
        self._dot.move(400, 250)

        if mode.startswith("saccade"):
            self._build_saccade_pattern()
            self._after(500, self._saccade_step)
        elif mode.startswith("pursuit"):
            self._init_pursuit()
            self._after(500, self._pursuit_step_fn)

    def _place_dot(self, relx: float, rely: float) -> None:
        w = self._canvas.width()
        h = self._canvas.height()
        x = int(relx * w) - 20
        y = int(rely * h) - 20
        self._dot.move(max(0, x), max(0, y))

    # --- Saccade modes ---

    def _build_saccade_pattern(self) -> None:
        n = max(int(self.duration_s * 1000 / self.delay), 10)

        if self.mode == "saccade_h":
            self._pattern = [
                (0.2, 0.5) if i % 2 == 0 else (0.8, 0.5)
                for i in range(n)
            ]
        elif self.mode == "saccade_v":
            self._pattern = [
                (0.5, 0.25) if i % 2 == 0 else (0.5, 0.75)
                for i in range(n)
            ]
        elif self.mode == "saccade_diag":
            corners = [(0.2, 0.25), (0.8, 0.75), (0.8, 0.25), (0.2, 0.75)]
            self._pattern = [corners[i % 4] for i in range(n)]
        elif self.mode == "saccade_expand":
            self._pattern = []
            for i in range(n):
                frac = 0.1 + 0.35 * (i / max(n - 1, 1))
                if i % 2 == 0:
                    self._pattern.append((0.5 - frac, 0.5))
                else:
                    self._pattern.append((0.5 + frac, 0.5))
        self._pattern_idx = 0

    def _saccade_step(self) -> None:
        if not self._running:
            return
        if self._pattern_idx >= len(self._pattern):
            self._complete_exercise()
            return

        x, y = self._pattern[self._pattern_idx]
        self._place_dot(x, y)
        self._pattern_idx += 1
        pct = int(self._pattern_idx / len(self._pattern) * 100)
        self._lbl_progress.setText(f"{pct}%")
        self._after(self.delay, self._saccade_step)

    # --- Smooth pursuit modes ---

    def _init_pursuit(self) -> None:
        self._frame_ms = 20
        total_ms = int(self.duration_s * 1000)
        self._pursuit_steps = total_ms // self._frame_ms
        self._pursuit_step = 0
        self._dt = 1.0 / max(self._pursuit_steps, 1)
        self._t = 0.0
        if self._requested_cycles > 0:
            self._cycles = self._requested_cycles
        else:
            self._cycles = max(int(self.duration_s / 4), 2)

    def _pursuit_position(self, t: float) -> tuple:
        c = self._cycles
        if self.mode == "pursuit_line":
            x = 0.5 + 0.35 * math.sin(2 * math.pi * c * t)
            return (x, 0.5)
        elif self.mode == "pursuit_circle":
            angle = 2 * math.pi * c * t
            x = 0.5 + 0.25 * math.cos(angle)
            y = 0.5 + 0.25 * math.sin(angle)
            return (x, y)
        elif self.mode == "pursuit_figure8":
            angle = 2 * math.pi * c * t
            x = 0.5 + 0.3 * math.sin(angle)
            y = 0.5 + 0.2 * math.sin(2 * angle)
            return (x, y)
        return (0.5, 0.5)

    def _pursuit_step_fn(self) -> None:
        if not self._running:
            return
        if self._pursuit_step >= self._pursuit_steps:
            self._complete_exercise()
            return

        x, y = self._pursuit_position(self._t)
        self._place_dot(x, y)
        self._t += self._dt
        self._pursuit_step += 1
        pct = int(self._pursuit_step / self._pursuit_steps * 100)
        self._lbl_progress.setText(f"{pct}%")
        self._after(self._frame_ms, self._pursuit_step_fn)

    # --- Completion ---

    def _complete_exercise(self) -> None:
        self._running = False
        self._clear()
        self.add_nav_bar(show_stop=False)

        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")

        container = QWidget()
        container.setStyleSheet(f"background-color: {c['bg']};")
        cl = QVBoxLayout(container)
        cl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("WARMUP COMPLETE")
        title.setFont(make_qfont("header"))
        title.setStyleSheet(f"color: {c['accent']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(title)

        body = QLabel("Eyes primed and ready for training.")
        body.setFont(make_qfont("body"))
        body.setStyleSheet(f"color: {c['fg']};")
        body.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(body)

        cont_btn = QPushButton("CONTINUE")
        cont_btn.setFont(make_qfont("btn_bold"))
        cont_btn.setStyleSheet(
            f"background-color: {c['accent']}; color: {c['btn_text']}; "
            f"border: 2px solid transparent; padding: 8px 40px; border-radius: 4px;"
        )
        cont_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cont_btn.clicked.connect(self.navigator.finish_exercise)
        cl.addWidget(cont_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self._layout.addWidget(container, 1)
