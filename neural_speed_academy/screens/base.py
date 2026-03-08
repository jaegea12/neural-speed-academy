"""
Base screen class with lifecycle methods.
All screens inherit from this to ensure consistent behavior.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
import tkinter as tk

from neural_speed_academy.theme import COLORS, FONTS

if TYPE_CHECKING:
    from neural_speed_academy.navigation.navigator import Navigator


class BaseScreen(ABC):
    """
    Abstract base class for all screens.
    Provides common functionality and enforces a consistent lifecycle.
    """

    def __init__(self, root: tk.Tk, navigator: "Navigator"):
        self.root = root
        self.navigator = navigator
        self.widgets: list[tk.Widget] = []

    def show(self, **kwargs) -> None:
        """Display the screen. Clears previous content and builds new UI."""
        self.clear()
        self.build(**kwargs)

    def hide(self) -> None:
        """Hide the screen by destroying all its widgets."""
        self.clear()

    def clear(self) -> None:
        """Remove all widgets created by this screen."""
        for widget in self.widgets:
            try:
                widget.destroy()
            except tk.TclError:
                pass  # Widget already destroyed
        self.widgets.clear()
        
        # Also clear any remaining widgets from root
        for widget in self.root.winfo_children():
            try:
                widget.destroy()
            except tk.TclError:
                pass

    @abstractmethod
    def build(self, **kwargs) -> None:
        """Build the screen UI. Must be implemented by subclasses."""
        pass

    def add_widget(self, widget: tk.Widget) -> tk.Widget:
        """Track a widget for cleanup. Returns the widget for chaining."""
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
        """Display a guide popup for the given topic."""
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
