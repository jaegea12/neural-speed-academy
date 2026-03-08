"""
Eye Priming exercises: structured saccades, smooth pursuit, and figure-8 tracking.
All modes target ~45 seconds duration for an effective warmup.
"""
from __future__ import annotations

import math
import tkinter as tk

from neural_speed_academy.exercises.base import BaseExercise
from neural_speed_academy.theme import COLORS, FONTS


class PrimingExercise(BaseExercise):
    """
    Multi-mode eye priming exercise.
    Modes: structured saccades, smooth pursuit (line/circle/figure-8).
    Duration is controlled explicitly via duration_s for consistency.
    """

    def __init__(self, root: tk.Tk, navigator):
        super().__init__(root, navigator)
        self.dot: tk.Label = None
        self.lbl_progress: tk.Label = None
        self.lbl_mode: tk.Label = None
        self.mode: str = ""
        self.duration_s: float = 45.0
        self.delay: int = 600
        # Saccade state
        self._pattern: list = []
        self._pattern_idx: int = 0
        # Smooth pursuit state
        self._t: float = 0.0
        self._dt: float = 0.0
        self._pursuit_steps: int = 0
        self._pursuit_step: int = 0
        self._frame_ms: int = 20
        self._cycles: int = 3
        self._running: bool = False

    @property
    def name(self) -> str:
        return "Eye Priming"

    def start(self, mode: str = "saccade_h", delay: int = 600,
              duration_s: float = 45.0, cycles: int = 0, **kwargs) -> None:
        """
        Start a priming exercise.

        Args:
            mode: Exercise pattern (saccade_h/v/diag/expand, pursuit_line/circle/figure8)
            delay: Milliseconds between saccade jumps (ignored for pursuit)
            duration_s: Total exercise duration in seconds
            cycles: Number of pursuit cycles (0 = auto, ~4s per cycle)
        """
        self.mode = mode
        self.delay = delay
        self.duration_s = duration_s
        self._requested_cycles = cycles
        self._running = True

        self.clear()
        self.add_nav_bar()

        # Guide button
        guide_btn = tk.Button(
            self.root,
            text="GUIDE",
            bg=COLORS["accent"],
            fg=COLORS["btn_text"],
            command=lambda: self.show_guide("priming")
        )
        guide_btn.place(x=50, y=80)
        self.add_widget(guide_btn)

        # Mode label
        mode_labels = {
            "saccade_h": "HORIZONTAL SACCADES",
            "saccade_v": "VERTICAL SACCADES",
            "saccade_diag": "DIAGONAL SACCADES",
            "saccade_expand": "EXPANDING SACCADES",
            "pursuit_line": "SMOOTH PURSUIT — LINE",
            "pursuit_circle": "SMOOTH PURSUIT — CIRCLE",
            "pursuit_figure8": "SMOOTH PURSUIT — FIGURE 8",
        }
        self.lbl_mode = tk.Label(
            self.root,
            text=mode_labels.get(mode, mode.upper()),
            font=FONTS["counter"],
            fg=COLORS["accent"],
            bg=COLORS["bg"]
        )
        self.lbl_mode.place(relx=0.5, rely=0.08, anchor="center")
        self.add_widget(self.lbl_mode)

        # Progress label
        self.lbl_progress = tk.Label(
            self.root,
            text="0%",
            font=FONTS["section_header"],
            fg=COLORS["fg"],
            bg=COLORS["bg"]
        )
        self.lbl_progress.place(relx=0.5, rely=0.12, anchor="center")
        self.add_widget(self.lbl_progress)

        # Dot
        self.dot = tk.Label(
            self.root,
            text="●",
            font=FONTS["priming_dot"],
            fg=COLORS["priming"],
            bg=COLORS["bg"]
        )
        self.dot.place(relx=0.5, rely=0.5, anchor="center")
        self.add_widget(self.dot)

        if mode.startswith("saccade"):
            self._build_saccade_pattern()
            self.root.after(500, self._saccade_step)
        elif mode.startswith("pursuit"):
            self._init_pursuit()
            self.root.after(500, self._pursuit_step_fn)

    # --- Saccade modes ---

    def _build_saccade_pattern(self) -> None:
        """Generate position sequence sized to fill duration_s."""
        # Number of jumps = duration / delay
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
        """Advance one step in the saccade pattern."""
        if not self._running:
            return
        if self._pattern_idx >= len(self._pattern):
            self._complete_exercise()
            return

        x, y = self._pattern[self._pattern_idx]
        self.dot.place(relx=x, rely=y, anchor="center")
        self._pattern_idx += 1
        pct = int(self._pattern_idx / len(self._pattern) * 100)
        self.lbl_progress.config(text=f"{pct}%")
        self.root.after(self.delay, self._saccade_step)

    # --- Smooth pursuit modes ---

    def _init_pursuit(self) -> None:
        """Initialize smooth pursuit animation to fill duration_s."""
        self._frame_ms = 20
        total_ms = int(self.duration_s * 1000)
        self._pursuit_steps = total_ms // self._frame_ms
        self._pursuit_step = 0
        self._dt = 1.0 / max(self._pursuit_steps, 1)
        self._t = 0.0
        if self._requested_cycles > 0:
            self._cycles = self._requested_cycles
        else:
            # Default: ~4 seconds per cycle for comfortable tracking
            self._cycles = max(int(self.duration_s / 4), 2)

    def _pursuit_position(self, t: float) -> tuple:
        """Calculate dot position for the current pursuit mode at time t (0..1)."""
        c = self._cycles
        if self.mode == "pursuit_line":
            x = 0.5 + 0.35 * math.sin(2 * math.pi * c * t)
            y = 0.5
            return (x, y)
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
        """Advance one frame of smooth pursuit animation."""
        if not self._running:
            return
        if self._pursuit_step >= self._pursuit_steps:
            self._complete_exercise()
            return

        x, y = self._pursuit_position(self._t)
        self.dot.place(relx=x, rely=y, anchor="center")
        self._t += self._dt
        self._pursuit_step += 1
        pct = int(self._pursuit_step / self._pursuit_steps * 100)
        self.lbl_progress.config(text=f"{pct}%")
        self.root.after(self._frame_ms, self._pursuit_step_fn)

    # --- Completion ---

    def _complete_exercise(self) -> None:
        """Handle exercise completion."""
        self._running = False
        self.clear()
        self.add_nav_bar()

        container = tk.Frame(self.root, bg=COLORS["bg"])
        container.pack(expand=True)
        self.add_widget(container)

        tk.Label(
            container, text="WARMUP COMPLETE",
            font=FONTS["header"], fg=COLORS["accent"], bg=COLORS["bg"],
        ).pack(pady=(0, 15))

        tk.Label(
            container, text="Eyes primed and ready for training.",
            font=FONTS["body"], fg=COLORS["fg"], bg=COLORS["bg"],
        ).pack(pady=10)

        tk.Button(
            container, text="CONTINUE",
            command=self.navigator.finish_exercise,
            bg=COLORS["accent"], fg=COLORS["btn_text"],
            font=FONTS["btn_bold"], width=20, pady=8,
            relief="flat", cursor="hand2",
        ).pack(pady=25)
