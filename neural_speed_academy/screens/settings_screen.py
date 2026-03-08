"""
Settings screen for theme selection.
Settings are app-level and independent of user profiles.
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
            bg=COLORS["bg"],
        ).pack(pady=(0, 30))

        # Theme section
        tk.Label(
            container,
            text="COLOR PROFILE",
            font=FONTS["section_header"],
            fg=COLORS["accent"],
            bg=COLORS["bg"],
        ).pack(pady=(0, 15))

        profiles = {
            "dark": "Dark Mode",
            "light": "Light Mode",
            "soft_light": "Soft Light",
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

        btn_row = tk.Frame(container, bg=COLORS["bg"])
        btn_row.pack(pady=(20, 0))

        tk.Button(
            btn_row,
            text="APPLY & SAVE",
            font=FONTS["btn_bold"],
            bg=COLORS["accent"],
            fg=COLORS["btn_text"],
            relief="flat",
            width=16,
            pady=8,
            cursor="hand2",
            command=self._apply_and_save,
        ).pack(side="left", padx=6)

        tk.Button(
            btn_row,
            text="DEFAULT SETTINGS",
            font=FONTS["btn_bold"],
            bg=COLORS["card"],
            fg=COLORS["fg"],
            relief="flat",
            width=16,
            pady=8,
            cursor="hand2",
            command=self._reset_defaults,
        ).pack(side="left", padx=6)

    def _apply_and_save(self) -> None:
        """Apply the selected theme, save to disk, and refresh."""
        theme_manager.set_profile(self.selected.get())
        theme_manager.save()
        self.show()

    def _reset_defaults(self) -> None:
        """Reset to default settings, save, and refresh."""
        theme_manager.reset_defaults()
        self.show()
