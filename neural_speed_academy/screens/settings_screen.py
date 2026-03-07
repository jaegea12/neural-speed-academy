"""
Settings screen for theme selection.
"""
from __future__ import annotations

import tkinter as tk

from neural_speed_academy.screens.base import BaseScreen
from neural_speed_academy.theme import COLORS, FONTS, theme_manager


class SettingsScreen(BaseScreen):
    """Settings screen allowing users to switch color profiles."""

    def build(self, **kwargs) -> None:
        """Build the settings UI."""
        self.root.configure(bg=COLORS["bg"])
        self.add_nav_bar()

        container = tk.Frame(self.root, bg=COLORS["bg"])
        container.pack(expand=True)
        self.add_widget(container)

        tk.Label(
            container,
            text="SETTINGS",
            font=FONTS["header"],
            fg=COLORS["fg"],
            bg=COLORS["bg"]
        ).pack(pady=(0, 30))

        # Theme section
        tk.Label(
            container,
            text="COLOR PROFILE",
            font=FONTS["section_header"],
            fg=COLORS["accent"],
            bg=COLORS["bg"]
        ).pack(pady=(0, 15))

        profiles = {
            "dark": "Dark Mode",
            "light": "Light Mode",
            "high_contrast": "High Contrast",
        }

        current = theme_manager.profile
        self.selected = tk.StringVar(value=current)

        for key, label in profiles.items():
            rb = tk.Radiobutton(
                container,
                text=label,
                variable=self.selected,
                value=key,
                font=FONTS["btn"],
                fg=COLORS["fg"],
                bg=COLORS["bg"],
                selectcolor=COLORS["card"],
                activebackground=COLORS["bg"],
                activeforeground=COLORS["fg"],
                indicatoron=True,
                anchor="w",
                width=20,
            )
            rb.pack(pady=4)

        tk.Button(
            container,
            text="APPLY",
            font=FONTS["btn_bold"],
            bg=COLORS["accent"],
            fg=COLORS["btn_text"],
            relief="flat",
            width=20,
            pady=8,
            command=self._apply_theme,
        ).pack(pady=(20, 0))

    def _apply_theme(self) -> None:
        """Apply the selected theme and refresh the screen."""
        theme_manager.set_profile(self.selected.get())
        # Re-show this screen to reflect the new colors
        self.show()
