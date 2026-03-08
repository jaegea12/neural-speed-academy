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
        """Add a navigation bar with breadcrumbs and user stats."""
        user = self.navigator.get_user()

        bar = tk.Frame(self.root, bg=COLORS["card"], height=50)
        bar.pack(fill="x", side="top")
        self.add_widget(bar)

        # Breadcrumb navigation
        crumb_frame = tk.Frame(bar, bg=COLORS["card"])
        crumb_frame.pack(side="left", padx=10, pady=10)

        crumbs = self.navigator.get_breadcrumbs()
        for i, (label, screen_name) in enumerate(crumbs):
            is_last = (i == len(crumbs) - 1)
            # Last item is a label (current page), but only if there
            # are multiple crumbs. A single crumb (HUB) stays clickable.
            if is_last and len(crumbs) > 1:
                tk.Label(
                    crumb_frame, text=label,
                    fg=COLORS["fg"], bg=COLORS["card"],
                    font=FONTS["btn_sm"],
                ).pack(side="left", padx=(0, 2))
            else:
                tk.Button(
                    crumb_frame, text=label,
                    bg=COLORS["accent"], fg=COLORS["btn_text"],
                    font=FONTS["btn_sm"], relief="flat", bd=0,
                    command=lambda sn=screen_name: self.navigator.navigate_to(sn),
                ).pack(side="left", padx=(0, 2))
            if not is_last:
                tk.Label(
                    crumb_frame, text="›",
                    fg=COLORS["muted"], bg=COLORS["card"],
                    font=FONTS["btn_sm"],
                ).pack(side="left", padx=2)

        if user:
            stats = f"👤 {user.name.upper()} | XP: {user.xp}"
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
            text=f"📘 {title}",
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
        """Handle exercise completion: save XP, log history, show result."""
        user = self.navigator.get_user()
        if user:
            try:
                user.add_xp(result.xp_gained)
                user.add_history(
                    exercise=result.exercise_name,
                    result=result.score_string(),
                    max_entries=USER_DATA_CONFIG["max_history_entries"],
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
        self.navigator.to_dashboard()

    @abstractmethod
    def start(self, **config) -> None:
        """Start the exercise with given configuration."""
        pass
