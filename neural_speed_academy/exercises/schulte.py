"""
Schulte Grid exercise for focus and peripheral vision training.
"""
from __future__ import annotations

import random
import tkinter as tk
from tkinter import messagebox

from neural_speed_academy.exercises.base import BaseExercise, ExerciseResult
from neural_speed_academy.theme import COLORS, FONTS
from neural_speed_academy.config import SCHULTE_CONFIG


class SchulteExercise(BaseExercise):
    """
    Schulte Grid exercise.
    User must find numbers 1-25 in order without moving eyes from center.
    """

    def __init__(self, root: tk.Tk, navigator):
        super().__init__(root, navigator)
        self.target: int = 1
        self.score: int = 0
        self.max_num: int = 0
        self.lbl_target: tk.Label = None
        self.lbl_score: tk.Label = None

    @property
    def name(self) -> str:
        return "Schulte Grid"

    def start(self, **kwargs) -> None:
        """Start the Schulte Grid exercise."""
        self.clear()
        self.add_nav_bar()

        # Guide button
        guide_btn = tk.Button(
            self.root,
            text="📘 GUIDE",
            bg=COLORS["accent"],
            fg="#0f172a",
            command=lambda: self.show_guide("schulte")
        )
        guide_btn.place(x=50, y=80)
        self.add_widget(guide_btn)

        grid_size = SCHULTE_CONFIG["grid_size"]
        self.max_num = grid_size * grid_size
        self.target = 1
        self.score = 0

        # Stats display
        stats_frame = tk.Frame(self.root, bg=COLORS["bg"])
        stats_frame.pack(pady=(20, 10))
        self.add_widget(stats_frame)

        self.lbl_target = tk.Label(
            stats_frame,
            text=f"FIND: {self.target}",
            font=("Segoe UI", 16, "bold"),
            fg=COLORS["fg"],
            bg=COLORS["bg"]
        )
        self.lbl_target.pack(side="left", padx=20)

        self.lbl_score = tk.Label(
            stats_frame,
            text=f"SCORE: {self.score}",
            font=("Segoe UI", 16, "bold"),
            fg=COLORS["accent"],
            bg=COLORS["bg"]
        )
        self.lbl_score.pack(side="left", padx=20)

        # Grid container
        grid_frame = tk.Frame(self.root, bg=COLORS["bg"])
        grid_frame.pack(expand=True)
        self.add_widget(grid_frame)

        # Create shuffled grid
        nums = list(range(1, self.max_num + 1))
        random.shuffle(nums)

        for i in range(grid_size):
            for j in range(grid_size):
                val = nums.pop()
                btn = tk.Button(
                    grid_frame,
                    text=str(val),
                    width=6,
                    height=3,
                    font=("Segoe UI", 16, "bold"),
                    bg=COLORS["grid_btn"],
                    fg="white",
                    relief="raised"
                )
                btn.configure(command=lambda b=btn, v=val: self._on_click(v, b))
                btn.grid(row=i, column=j, padx=2, pady=2)

    def _on_click(self, value: int, button: tk.Button) -> None:
        """Handle grid button click."""
        if value == self.target:
            # Correct click
            button.config(
                bg=COLORS["grid_solved"],
                state="disabled",
                relief="sunken"
            )
            self.target += 1
            self.score += SCHULTE_CONFIG["correct_points"]

            if self.target > self.max_num:
                self._complete_exercise()
            else:
                self.lbl_target.config(text=f"FIND: {self.target}")
        else:
            # Wrong click
            self.score -= SCHULTE_CONFIG["wrong_penalty"]
            orig_bg = button.cget("bg")
            button.config(bg=COLORS["alert"])
            self.root.after(200, lambda: button.config(bg=orig_bg))

        self.lbl_score.config(text=f"SCORE: {self.score}")

    def _complete_exercise(self) -> None:
        """Handle exercise completion."""
        result = ExerciseResult(
            exercise_name=self.name,
            score=self.score,
            total=self.max_num,
            xp_gained=self.score
        )
        self.complete(result)
        messagebox.showinfo(
            "Done",
            f"Grid Cleared!\nFinal Score: {self.score}\nXP Gained: {self.score}"
        )
        self.navigator.to_dashboard()
