"""
Eye Priming exercise for warming up extraocular muscles.
"""
from __future__ import annotations

import random
import tkinter as tk
from tkinter import messagebox

from neural_speed_academy.exercises.base import BaseExercise
from neural_speed_academy.theme import COLORS, FONTS
from neural_speed_academy.config import PRIMING_CONFIG


class PrimingExercise(BaseExercise):
    """
    Eye Priming exercise.
    User follows a dot with their eyes to warm up eye muscles.
    """

    def __init__(self, root: tk.Tk, navigator):
        super().__init__(root, navigator)
        self.count: int = 0
        self.total: int = PRIMING_CONFIG["total_positions"]
        self.dot: tk.Label = None
        self.lbl_progress: tk.Label = None

    @property
    def name(self) -> str:
        return "Eye Priming"

    def start(self, **kwargs) -> None:
        """Start the eye priming exercise."""
        self.clear()
        self.add_nav_bar()

        # Guide button
        guide_btn = tk.Button(
            self.root,
            text="📘 GUIDE",
            bg=COLORS["accent"],
            fg=COLORS["btn_text"],
            command=lambda: self.show_guide("priming")
        )
        guide_btn.place(x=50, y=80)
        self.add_widget(guide_btn)

        self.total = PRIMING_CONFIG["total_positions"]
        self.count = 0

        # Progress label
        self.lbl_progress = tk.Label(
            self.root,
            text=f"WARMUP: 0/{self.total}",
            font=FONTS["section_header"],
            fg=COLORS["fg"],
            bg=COLORS["bg"]
        )
        self.lbl_progress.place(relx=0.5, rely=0.1, anchor="center")
        self.add_widget(self.lbl_progress)

        # Dot to follow
        self.dot = tk.Label(
            self.root,
            text="●",
            font=FONTS["priming_dot"],
            fg=COLORS["priming"],
            bg=COLORS["bg"]
        )
        self.dot.place(relx=0.5, rely=0.5, anchor="center")
        self.add_widget(self.dot)

        self._run_loop()

    def _run_loop(self) -> None:
        """Run the priming animation loop."""
        if self.count < self.total:
            pos = random.choice(PRIMING_CONFIG["positions"])
            self.dot.place(relx=pos[0], rely=pos[1])
            self.count += 1
            self.lbl_progress.config(text=f"WARMUP: {self.count}/{self.total}")
            self.root.after(PRIMING_CONFIG["delay_ms"], self._run_loop)
        else:
            self._complete_exercise()

    def _complete_exercise(self) -> None:
        """Handle exercise completion."""
        messagebox.showinfo("Warmup", "Eyes Primed!")
        self.navigator.to_dashboard()
