"""
Main menu screen — the application entry point.
"""
from __future__ import annotations

import sys
import tkinter as tk
from tkinter import messagebox

from neural_speed_academy.screens.base import BaseScreen
from neural_speed_academy.theme import COLORS, FONTS


class MainMenuScreen(BaseScreen):
    """Landing screen with title, slogan, and navigation buttons."""

    def build(self, **kwargs) -> None:
        """Build the main menu UI."""
        self.root.configure(bg=COLORS["bg"])

        container = tk.Frame(self.root, bg=COLORS["bg"])
        container.pack(expand=True)
        self.add_widget(container)

        # Title
        tk.Label(
            container,
            text="NEURAL SPEED ACADEMY",
            font=FONTS["title"],
            fg=COLORS["accent"],
            bg=COLORS["bg"],
        ).pack(pady=(0, 5))

        # Slogan
        tk.Label(
            container,
            text="Let your brain process more information in less time",
            font=FONTS["sub"],
            fg=COLORS["muted"],
            bg=COLORS["bg"],
        ).pack(pady=(0, 40))

        # Buttons
        btn_cfg = dict(
            width=30, pady=12, relief="flat",
            font=FONTS["btn_bold"], cursor="hand2",
        )

        tk.Button(
            container,
            text="START TRAINING",
            bg=COLORS["accent"], fg=COLORS["btn_text"],
            command=lambda: self.navigator.navigate_to("login"),
            **btn_cfg,
        ).pack(pady=6)

        tk.Button(
            container,
            text="INTRODUCTION",
            bg=COLORS["action"], fg=COLORS["btn_text"],
            command=lambda: self.navigator.navigate_to("introduction"),
            **btn_cfg,
        ).pack(pady=6)

        tk.Button(
            container,
            text="TRAINING PATHS",
            bg=COLORS["action"], fg=COLORS["btn_text"],
            command=lambda: self.navigator.navigate_to("paths"),
            **btn_cfg,
        ).pack(pady=6)

        tk.Button(
            container,
            text="SETTINGS",
            bg=COLORS["card"], fg=COLORS["fg"],
            command=lambda: self.navigator.navigate_to("settings"),
            **btn_cfg,
        ).pack(pady=6)

        tk.Button(
            container,
            text="INFORMATION",
            bg=COLORS["card"], fg=COLORS["fg"],
            command=self._show_info,
            **btn_cfg,
        ).pack(pady=6)

        tk.Button(
            container,
            text="QUIT",
            bg=COLORS["alert"], fg=COLORS["btn_text"],
            command=self._quit,
            **btn_cfg,
        ).pack(pady=6)

    def _show_info(self) -> None:
        """Show application information."""
        win = tk.Toplevel(self.root)
        win.title("About")
        win.configure(bg=COLORS["card"])
        win.geometry("460x340")
        win.transient(self.root)
        win.grab_set()

        tk.Label(
            win, text="NEURAL SPEED ACADEMY",
            font=FONTS["header"], fg=COLORS["accent"], bg=COLORS["card"],
        ).pack(pady=(30, 10))

        tk.Label(
            win,
            text=(
                "A desktop application for speed reading\n"
                "and cognitive training.\n\n"
                "Exercises based on established techniques:\n"
                "RSVP, guided pacing, Schulte grids,\n"
                "peripheral vision training, and chunking."
            ),
            font=FONTS["body"], fg=COLORS["text_on_card"], bg=COLORS["card"],
            justify="center",
        ).pack(pady=10)

        tk.Label(
            win, text="Created by Adam Jaeger\n\u00a9 2025",
            font=FONTS["btn_sm"], fg=COLORS["muted"], bg=COLORS["card"],
        ).pack(pady=(10, 0))

        tk.Button(
            win, text="CLOSE", font=FONTS["btn_bold"],
            bg=COLORS["accent"], fg=COLORS["btn_text"],
            relief="flat", width=12, pady=6, cursor="hand2",
            command=win.destroy,
        ).pack(pady=15)

        win.bind("<Escape>", lambda e: win.destroy())

    def _quit(self) -> None:
        """Quit the application after confirmation."""
        if messagebox.askyesno("Quit", "Are you sure you want to quit?"):
            self.root.destroy()
            sys.exit(0)
