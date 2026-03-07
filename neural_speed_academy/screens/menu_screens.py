"""
Menu screens for exercise selection.
"""
from __future__ import annotations

import random
import tkinter as tk
from typing import Callable, TYPE_CHECKING

from neural_speed_academy.screens.base import BaseScreen
from neural_speed_academy.theme import COLORS, FONTS

if TYPE_CHECKING:
    from neural_speed_academy.exercises.flash import FlashExercise


class BaseMenuScreen(BaseScreen):
    """Base class for exercise menu screens."""

    def _create_grid_menu(
        self,
        title: str,
        guide_key: str,
        sets: list[tuple[str, Callable]],
        col1_label: str = "FIXED / BASIC",
        col2_label: str = "MIXED / ADVANCED"
    ) -> None:
        """Create a two-column grid menu."""
        self.root.configure(bg=COLORS["bg"])
        self.add_nav_bar()

        container = tk.Frame(self.root, bg=COLORS["bg"])
        container.pack(expand=True, fill="both")
        self.add_widget(container)

        # Title
        tk.Label(
            container,
            text=title,
            font=FONTS["header"],
            fg=COLORS["fg"],
            bg=COLORS["bg"]
        ).pack(pady=10)

        # Guide button
        tk.Button(
            container,
            text="📘 READ GUIDE",
            bg=COLORS["accent"],
            fg="#0f172a",
            command=lambda: self.show_guide(guide_key)
        ).pack(pady=5)

        # Grid
        grid = tk.Frame(container, bg=COLORS["bg"])
        grid.pack(pady=20)

        # Calculate split
        half = (len(sets) + 1) // 2
        col1_items = sets[:half]
        col2_items = sets[half:]

        # Column headers
        tk.Label(
            grid,
            text=col1_label,
            font=("Segoe UI", 10, "bold"),
            fg="#94a3b8",
            bg=COLORS["bg"]
        ).grid(row=0, column=0, pady=10)

        tk.Label(
            grid,
            text=col2_label,
            font=("Segoe UI", 10, "bold"),
            fg="#94a3b8",
            bg=COLORS["bg"]
        ).grid(row=0, column=1, pady=10)

        # Buttons
        for i in range(max(len(col1_items), len(col2_items))):
            if i < len(col1_items):
                name, cmd = col1_items[i]
                tk.Button(
                    grid,
                    text=name,
                    command=cmd,
                    bg=COLORS["accent"],
                    fg="#0f172a",
                    font=("Segoe UI", 11),
                    width=35,
                    pady=8,
                    relief="flat"
                ).grid(row=i + 1, column=0, padx=15, pady=5)

            if i < len(col2_items):
                name, cmd = col2_items[i]
                tk.Button(
                    grid,
                    text=name,
                    command=cmd,
                    bg=COLORS["accent"],
                    fg="#0f172a",
                    font=("Segoe UI", 11),
                    width=35,
                    pady=8,
                    relief="flat"
                ).grid(row=i + 1, column=1, padx=15, pady=5)


class FlashMenuScreen(BaseMenuScreen):
    """Menu screen for flash number exercises."""

    def __init__(self, root: tk.Tk, navigator, flash_exercise: "FlashExercise"):
        super().__init__(root, navigator)
        self.flash_exercise = flash_exercise

    def build(self, **kwargs) -> None:
        """Build the flash menu UI."""
        def run(low: int, high: int, rounds: int) -> Callable:
            return lambda: self.flash_exercise.start(
                mode="flash_num",
                rounds=rounds,
                level_func=lambda _: random.randint(low, high)
            )

        sets = [
            ("Fixed: 1 Digit (Instant)", run(1, 1, 10)),
            ("Fixed: 2 Digits", run(2, 2, 10)),
            ("Fixed: 3 Digits", run(3, 3, 10)),
            ("Fixed: 4 Digits", run(4, 4, 10)),
            ("Fixed: 5 Digits", run(5, 5, 12)),
            ("Fixed: 6 Digits", run(6, 6, 12)),
            ("Fixed: 7 Digits", run(7, 7, 15)),
            ("Fixed: 8 Digits", run(8, 8, 15)),
            ("Mix: 2-3 Digits", run(2, 3, 10)),
            ("Mix: 3-4 Digits", run(3, 4, 12)),
            ("Mix: 3-5 Digits", run(3, 5, 12)),
            ("Mix: 4-5 Digits", run(4, 5, 12)),
            ("Mix: 4-6 Digits", run(4, 6, 15)),
            ("Mix: 5-7 Digits", run(5, 7, 15)),
            ("Mix: 6-8 Digits", run(6, 8, 15)),
            ("Chaos: 1-10 Digits", run(1, 10, 20)),
        ]

        self._create_grid_menu("FLASH NUMBER SETS", "flash", sets)


class WordsMenuScreen(BaseMenuScreen):
    """Menu screen for word drill exercises."""

    def __init__(self, root: tk.Tk, navigator, flash_exercise: "FlashExercise"):
        super().__init__(root, navigator)
        self.flash_exercise = flash_exercise

    def build(self, **kwargs) -> None:
        """Build the words menu UI."""
        def run(rounds: int) -> Callable:
            return lambda: self.flash_exercise.start(
                mode="flash_word",
                rounds=rounds,
                level_func=lambda _: 0
            )

        sets = [
            ("Ambiguous Words (10 Rounds)", run(10)),
            ("Quick Recognition (20 Rounds)", run(20)),
        ]

        self._create_grid_menu("WORD DRILLS", "flash", sets)


class EyespanMenuScreen(BaseMenuScreen):
    """Menu screen for eye-span exercises."""

    def __init__(self, root: tk.Tk, navigator, flash_exercise: "FlashExercise"):
        super().__init__(root, navigator)
        self.flash_exercise = flash_exercise

    def build(self, **kwargs) -> None:
        """Build the eye-span menu UI."""
        self.root.configure(bg=COLORS["bg"])
        self.add_nav_bar()

        container = tk.Frame(self.root, bg=COLORS["bg"])
        container.pack(expand=True, fill="both")
        self.add_widget(container)

        # Title
        tk.Label(
            container,
            text="EYE-SPAN TRAINING",
            font=FONTS["header"],
            fg=COLORS["fg"],
            bg=COLORS["bg"]
        ).pack(pady=10)

        # Guide button
        tk.Button(
            container,
            text="📘 READ GUIDE",
            bg=COLORS["accent"],
            fg="#0f172a",
            command=lambda: self.show_guide("eyespan")
        ).pack(pady=5)

        def run(mode: str, width: int, low: int, high: int, rounds: int) -> Callable:
            return lambda: self.flash_exercise.start(
                mode="eyespan",
                rounds=rounds,
                level_func=lambda _: random.randint(low, high),
                span_config={"mode": mode, "width": width}
            )

        col1_h = [
            ("1 Digit (Narrow 30%)", run("h", 30, 1, 1, 10)),
            ("1 Digit (Wide 70%)", run("h", 70, 1, 1, 10)),
            ("2 Digits (Narrow 30%)", run("h", 30, 2, 2, 10)),
            ("2 Digits (Wide 70%)", run("h", 70, 2, 2, 10)),
            ("3 Digits (Narrow 30%)", run("h", 30, 3, 3, 10)),
            ("3 Digits (Wide 80%)", run("h", 80, 3, 3, 12)),
            ("Elite 4 Digits (Max)", run("h", 90, 4, 4, 15)),
        ]

        col2_v = [
            ("1 Digit (Narrow 30%)", run("v", 30, 1, 1, 10)),
            ("2 Digits (Medium 50%)", run("v", 50, 2, 2, 10)),
            ("3 Digits (Narrow 30%)", run("v", 30, 3, 3, 10)),
            ("3 Digits (Wide 70%)", run("v", 70, 3, 3, 12)),
            ("Overlap 2-4 (Wide)", run("v", 80, 2, 4, 15)),
            ("Elite 4-6 Digits (Max)", run("v", 90, 4, 6, 20)),
        ]

        col3_m = [
            ("1 Digit Mix", run("m", 40, 1, 1, 10)),
            ("2 Digits Mix", run("m", 50, 2, 2, 12)),
            ("Standard Mix (3 Digits)", run("m", 50, 3, 3, 12)),
            ("Overlap Mix (2-3 Digits)", run("m", 60, 2, 3, 12)),
            ("Overlap Mix (3-5 Digits)", run("m", 70, 3, 5, 15)),
            ("Wide Range (2-6 Digits)", run("m", 80, 2, 6, 15)),
            ("Master Chaos (2-8 Digits)", run("m", 90, 2, 8, 20)),
        ]

        # Three-column grid
        grid = tk.Frame(container, bg=COLORS["bg"])
        grid.pack(pady=20)

        headers = ["HORIZONTAL SCAN", "VERTICAL JUMP", "DYNAMIC MIX"]
        for idx, title in enumerate(headers):
            tk.Label(
                grid,
                text=title,
                font=("Segoe UI", 12, "bold"),
                fg=COLORS["accent"],
                bg=COLORS["bg"]
            ).grid(row=0, column=idx, padx=10, pady=10)

        max_rows = max(len(col1_h), len(col2_v), len(col3_m))
        columns = [col1_h, col2_v, col3_m]

        for i in range(max_rows):
            for col_idx, col_items in enumerate(columns):
                if i < len(col_items):
                    name, cmd = col_items[i]
                    tk.Button(
                        grid,
                        text=name,
                        command=cmd,
                        bg=COLORS["accent"],
                        fg="#0f172a",
                        font=("Segoe UI", 10),
                        width=28,
                        pady=6,
                        relief="flat"
                    ).grid(row=i + 1, column=col_idx, padx=10, pady=4)
