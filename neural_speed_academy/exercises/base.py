"""
Base exercise class implementing the Template Method pattern.
All exercises inherit from this to ensure consistent behavior.
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Callable
import tkinter as tk
from tkinter import messagebox

from neural_speed_academy.theme import COLORS, FONTS
from neural_speed_academy.config import USER_DATA_CONFIG

if TYPE_CHECKING:
    from neural_speed_academy.navigation.navigator import Navigator

logger = logging.getLogger(__name__)


class ExerciseError(Exception):
    """Base exception for exercise errors."""
    pass


class ExerciseConfigError(ExerciseError):
    """Raised when exercise configuration is invalid."""
    pass


@dataclass
class ExerciseResult:
    """Result of a completed exercise."""
    exercise_name: str
    score: int
    total: int
    xp_gained: int

    def score_string(self) -> str:
        """Format score as string."""
        return f"{self.score}/{self.total}"


class BaseExercise(ABC):
    """
    Abstract base class for all exercises.
    Implements Template Method pattern for consistent exercise flow.
    """

    def __init__(self, root: tk.Tk, navigator: "Navigator"):
        self.root = root
        self.navigator = navigator
        self.widgets: list[tk.Widget] = []

    @property
    @abstractmethod
    def name(self) -> str:
        """Exercise name for logging."""
        pass

    def clear(self) -> None:
        """Remove all widgets created by this exercise."""
        for widget in self.widgets:
            try:
                widget.destroy()
            except tk.TclError:
                pass
        self.widgets.clear()
        
        for widget in self.root.winfo_children():
            try:
                widget.destroy()
            except tk.TclError:
                pass

    def add_widget(self, widget: tk.Widget) -> tk.Widget:
        """Track a widget for cleanup."""
        self.widgets.append(widget)
        return widget

    def add_nav_bar(self) -> tk.Frame:
        """Add a navigation bar with Back, Training Hub, and Main Menu buttons."""
        user = self.navigator.get_user()

        bar = tk.Frame(self.root, bg=COLORS["card"], height=50)
        bar.pack(fill="x", side="top")
        self.add_widget(bar)

        btn_frame = tk.Frame(bar, bg=COLORS["card"])
        btn_frame.pack(side="left", padx=10, pady=8)

        btn_cfg = dict(
            font=FONTS["btn_sm"], relief="flat", bd=0,
            cursor="hand2", pady=2, padx=8,
        )

        # Back button
        tk.Button(
            btn_frame, text="← Back",
            bg=COLORS["card"], fg=COLORS["fg"],
            command=self.navigator.go_back,
            **btn_cfg,
        ).pack(side="left", padx=(0, 6))

        # Training Hub
        tk.Button(
            btn_frame, text="Training Hub",
            bg=COLORS["accent"], fg=COLORS["btn_text"],
            command=self.navigator.to_dashboard,
            **btn_cfg,
        ).pack(side="left", padx=(0, 6))

        # Main Menu
        tk.Button(
            btn_frame, text="Main Menu",
            bg=COLORS["card"], fg=COLORS["fg"],
            command=lambda: self.navigator.navigate_to("main_menu"),
            **btn_cfg,
        ).pack(side="left")

        if user:
            stats = f"{user.name.upper()} | XP: {user.xp}"
            tk.Label(
                bar,
                text=stats,
                bg=COLORS["card"],
                fg=COLORS["accent"],
                font=FONTS["nav_stats"],
            ).pack(side="right", padx=20)

        return bar

    def show_guide(self, topic: str) -> None:
        """Display a guide popup."""
        from neural_speed_academy.config import EXERCISE_GUIDES
        
        title, text = EXERCISE_GUIDES.get(topic, ("INFO", "..."))
        win = tk.Toplevel(self.root)
        win.configure(bg=COLORS["card"])
        win.geometry("700x600")
        tk.Label(
            win,
            text=title,
            font=FONTS["sub"],
            fg=COLORS["accent"],
            bg=COLORS["card"],
        ).pack(pady=(20, 10))
        tk.Label(
            win,
            text=text,
            font=FONTS["body"],
            fg=COLORS["text_on_card"],
            bg=COLORS["card"],
            wraplength=620,
            justify="left",
        ).pack(pady=10, padx=30)

    def complete(self, result: ExerciseResult) -> None:
        """Handle exercise completion: save XP, log history, track personal bests."""
        user = self.navigator.get_user()
        if user:
            try:
                user.add_xp(result.xp_gained)
                user.add_history(
                    exercise=result.exercise_name,
                    result=result.score_string(),
                    max_entries=USER_DATA_CONFIG["max_history_entries"],
                )
                user.update_personal_best(
                    result.exercise_name, result.score, result.total,
                )
                self.navigator.save_user()
            except Exception as e:
                logger.error(f"Failed to save exercise result: {e}")
                messagebox.showwarning(
                    "Save Error",
                    "Could not save your progress. Please try again."
                )

    def handle_error(self, error: Exception, message: str = "An error occurred") -> None:
        """Handle exercise errors gracefully."""
        logger.error(f"{self.name} error: {error}")
        messagebox.showerror("Error", f"{message}\n\nDetails: {str(error)}")
        self.navigator.finish_exercise()

    @abstractmethod
    def start(self, **config) -> None:
        """Start the exercise with given configuration."""
        pass
