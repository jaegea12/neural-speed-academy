"""
Login screen for user authentication.
"""
from __future__ import annotations

import tkinter as tk

from neural_speed_academy.screens.base import BaseScreen
from neural_speed_academy.theme import COLORS, FONTS


class LoginScreen(BaseScreen):
    """Login screen where users enter their name to start training."""

    def build(self, **kwargs) -> None:
        """Build the login UI."""
        self.root.configure(bg=COLORS["bg"])

        # Center container
        container = tk.Frame(self.root, bg=COLORS["bg"])
        container.place(relx=0.5, rely=0.5, anchor="center")
        self.add_widget(container)

        # Title
        tk.Label(
            container,
            text="NEURAL SPEED ACADEMY",
            font=FONTS["header"],
            fg=COLORS["fg"],
            bg=COLORS["bg"],
        ).pack(pady=20)

        # Name entry with placeholder
        self.name_var = tk.StringVar()
        self.entry = tk.Entry(
            container,
            textvariable=self.name_var,
            font=FONTS["sub"],
            justify="center",
            bg=COLORS["card"],
            fg=COLORS["muted"],
            relief="flat",
            insertbackground=COLORS["text_on_card"],
        )
        self.entry.pack(pady=20, ipadx=10, ipady=8)
        self.entry.insert(0, "Type your name")

        # Placeholder behavior
        self.entry.bind("<FocusIn>", self._on_entry_focus)
        self.entry.bind("<FocusOut>", self._on_entry_blur)
        self.entry.bind("<Return>", lambda e: self._do_login())

        # Start button
        tk.Button(
            container,
            text="START TRAINING",
            font=FONTS["btn_bold"],
            bg=COLORS["accent"],
            fg=COLORS["btn_text"],
            relief="flat",
            command=self._do_login,
        ).pack()

    def _on_entry_focus(self, event) -> None:
        """Clear placeholder on focus."""
        if self.entry.get() == "Type your name":
            self.entry.delete(0, "end")
            self.entry.config(fg=COLORS["text_on_card"])

    def _on_entry_blur(self, event) -> None:
        """Restore placeholder if empty."""
        if self.entry.get() == "":
            self.entry.insert(0, "Type your name")
            self.entry.config(fg=COLORS["muted"])

    def _do_login(self) -> None:
        """Handle login action."""
        name = self.entry.get().strip()
        if name and name != "Type your name":
            # Load or create user via repository
            user = self.navigator.user_repo.get_or_create(name)
            self.navigator.set_user(user)
            self.navigator.to_dashboard()
