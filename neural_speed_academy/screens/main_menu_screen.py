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
        messagebox.showinfo(
            "About Neural Speed Academy",
            "Neural Speed Academy\n\n"
            "A desktop application for speed reading\n"
            "and cognitive training.\n\n"
            "Created by ADAM JÄGER\n"
            "© 2025"
        )

    def _quit(self) -> None:
        """Quit the application."""
        self.root.destroy()
        sys.exit(0)
