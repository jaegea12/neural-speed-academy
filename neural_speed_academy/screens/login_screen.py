"""
Login screen for user authentication.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

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

        # Existing users
        users = self.navigator.user_repo.list_users()
        if users:
            tk.Label(
                container,
                text="SELECT PROFILE",
                font=FONTS["section_header"],
                fg=COLORS["accent"],
                bg=COLORS["bg"],
            ).pack(pady=(0, 8))

            user_frame = tk.Frame(container, bg=COLORS["bg"])
            user_frame.pack(pady=(0, 15))

            for uname in users:
                profile = self.navigator.user_repo.get(uname)
                level = (profile.xp // 1000 + 1) if profile else 1

                row = tk.Frame(user_frame, bg=COLORS["card"], padx=12, pady=6)
                row.pack(fill="x", pady=2)
                row.config(cursor="hand2")

                tk.Label(
                    row, text=uname,
                    font=FONTS["btn_bold"], fg=COLORS["text_on_card"],
                    bg=COLORS["card"], anchor="w",
                ).pack(side="left")

                tk.Label(
                    row, text=f"Lv.{level}",
                    font=FONTS["btn_sm"], fg=COLORS["muted"],
                    bg=COLORS["card"],
                ).pack(side="right", padx=(10, 0))

                # Bind click on the row and its children
                for widget in [row] + list(row.winfo_children()):
                    widget.bind("<Button-1>", lambda e, n=uname: self._login_as(n))

                row.bind("<Enter>", lambda e, r=row: self._highlight_row(r, True))
                row.bind("<Leave>", lambda e, r=row: self._highlight_row(r, False))

            # Separator
            tk.Frame(
                container, bg=COLORS["muted"], height=1,
            ).pack(fill="x", padx=20, pady=(10, 10))

            tk.Label(
                container,
                text="OR CREATE NEW",
                font=FONTS["section_header"],
                fg=COLORS["accent"],
                bg=COLORS["bg"],
            ).pack(pady=(0, 8))

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
        self.entry.pack(pady=(0, 15), ipadx=10, ipady=8)
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
            cursor="hand2",
            command=self._do_login,
        ).pack()

    @staticmethod
    def _highlight_row(row: tk.Frame, enter: bool) -> None:
        """Toggle hover highlight on a user row."""
        color = COLORS["accent"] if enter else COLORS["card"]
        row.config(bg=color)
        for child in row.winfo_children():
            child.config(bg=color)

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

    def _login_as(self, name: str) -> None:
        """Log in as an existing user."""
        user = self.navigator.user_repo.get_or_create(name)
        self.navigator.set_user(user)
        self.navigator.complete_login()

    def _do_login(self) -> None:
        """Handle login action."""
        name = self.entry.get().strip()
        if not name or name == "Type your name":
            messagebox.showinfo("Name Required", "Please enter your name to continue.")
            return
        user = self.navigator.user_repo.get_or_create(name)
        self.navigator.set_user(user)
        self.navigator.complete_login()
