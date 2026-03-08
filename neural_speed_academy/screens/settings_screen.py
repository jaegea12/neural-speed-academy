"""
Settings screen for theme selection.
Settings are app-level and independent of user profiles.
"""
from __future__ import annotations

import tkinter as tk

from neural_speed_academy.screens.base import BaseScreen
from neural_speed_academy.config import TEXT_LIBRARY
from neural_speed_academy.theme import COLORS, FONTS, FOV_PRESETS, theme_manager


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
            "dark": "Dark",
            "twilight": "Twilight",
            "soft_light": "Soft Light",
            "focus": "Focus (Low Fatigue)",
            "light": "Light",
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

        # FOV section
        tk.Label(
            container,
            text="FIELD OF VIEW",
            font=FONTS["section_header"],
            fg=COLORS["accent"],
            bg=COLORS["bg"],
        ).pack(pady=(25, 5))

        tk.Label(
            container,
            text="Controls page width and font size in the Pacer exercise",
            font=FONTS["body"],
            fg=COLORS["muted"],
            bg=COLORS["bg"],
        ).pack(pady=(0, 8))

        self.fov_var = tk.StringVar(value=theme_manager.fov)

        for key, preset in FOV_PRESETS.items():
            tk.Radiobutton(
                container,
                text=preset["label"],
                variable=self.fov_var,
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
            ).pack(pady=2)

        # Training text section
        tk.Label(
            container,
            text="TRAINING TEXT",
            font=FONTS["section_header"],
            fg=COLORS["accent"],
            bg=COLORS["bg"],
        ).pack(pady=(25, 5))

        tk.Label(
            container,
            text="Used as the default text for Pacer, RSVP, and Chunking exercises",
            font=FONTS["body"],
            fg=COLORS["muted"],
            bg=COLORS["bg"],
        ).pack(pady=(0, 8))

        # Text library selector
        lib_frame = tk.Frame(container, bg=COLORS["bg"])
        lib_frame.pack(fill="x", padx=20, pady=(0, 8))

        tk.Label(
            lib_frame, text="Load from library:",
            font=FONTS["btn_sm"], fg=COLORS["fg"], bg=COLORS["bg"],
        ).pack(side="left", padx=(0, 8))

        lib_names = list(TEXT_LIBRARY.keys())
        self._lib_var = tk.StringVar(value="")

        lib_menu = tk.OptionMenu(
            lib_frame, self._lib_var, *lib_names,
            command=self._load_library_text,
        )
        lib_menu.config(
            font=FONTS["btn_sm"], bg=COLORS["card"],
            fg=COLORS["text_on_card"], relief="flat",
            highlightthickness=0, cursor="hand2",
        )
        lib_menu["menu"].config(
            font=FONTS["btn_sm"], bg=COLORS["card"],
            fg=COLORS["text_on_card"],
        )
        lib_menu.pack(side="left")

        text_frame = tk.Frame(container, bg=COLORS["card"])
        text_frame.pack(fill="x", padx=20)

        self.text_box = tk.Text(
            text_frame,
            font=FONTS["body"],
            bg=COLORS["card"],
            fg=COLORS["text_on_card"],
            insertbackground=COLORS["text_on_card"],
            wrap="word",
            height=8,
            width=60,
            relief="flat",
            padx=8,
            pady=8,
        )
        self.text_box.pack(fill="x")
        self.text_box.insert("1.0", theme_manager.training_text)

        # Buttons
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

    def _load_library_text(self, name: str) -> None:
        """Load a text from the built-in library into the text editor."""
        entry = TEXT_LIBRARY.get(name)
        if entry:
            _difficulty, text = entry
            self.text_box.delete("1.0", "end")
            self.text_box.insert("1.0", text)

    def _apply_and_save(self) -> None:
        """Apply all settings, save to disk, and return to main menu."""
        theme_manager.set_profile(self.selected.get())
        theme_manager.fov = self.fov_var.get()
        theme_manager.training_text = self.text_box.get("1.0", "end")
        theme_manager.save()
        self.navigator.navigate_to("main_menu")

    def _reset_defaults(self) -> None:
        """Reset to default settings, save, and refresh."""
        theme_manager.reset_defaults()
        self.show()
