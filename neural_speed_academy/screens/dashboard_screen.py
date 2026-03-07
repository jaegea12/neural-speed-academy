"""
Dashboard/main menu screen.
"""
from __future__ import annotations

import tkinter as tk
from typing import Callable

from neural_speed_academy.screens.base import BaseScreen
from neural_speed_academy.theme import COLORS, FONTS


class DashboardScreen(BaseScreen):
    """Main dashboard showing available training exercises."""

    def __init__(self, root: tk.Tk, navigator, exercise_callbacks: dict[str, Callable]):
        """
        Initialize dashboard with exercise callbacks.
        
        Args:
            root: Tkinter root window
            navigator: Navigator instance
            exercise_callbacks: Dict mapping exercise names to their handler functions
        """
        super().__init__(root, navigator)
        self.exercise_callbacks = exercise_callbacks

    def build(self, **kwargs) -> None:
        """Build the dashboard UI."""
        self.root.configure(bg=COLORS["bg"])

        # Header
        header = tk.Frame(self.root, bg=COLORS["card"], pady=20)
        header.pack(fill="x")
        self.add_widget(header)
        tk.Label(
            header,
            text="TRAINING DASHBOARD",
            font=FONTS["header"],
            fg=COLORS["text_on_card"],
            bg=COLORS["card"],
        ).pack()

        # Centered grid container
        grid = tk.Frame(self.root, bg=COLORS["bg"])
        grid.place(relx=0.5, rely=0.5, anchor="center")
        self.add_widget(grid)

        # Create sections
        self._create_section(grid, "PERCEPTION", 0, [
            ("🔢  Flash Numbers", self._get_callback("menu_flash")),
            ("🔤  Word Drills", self._get_callback("menu_words")),
            ("👁️  Eye Priming", self._get_callback("start_priming")),
        ])

        self._create_section(grid, "SPAN & FOCUS", 1, [
            ("👁️  Eye-Span", self._get_callback("menu_eyespan")),
            ("🏁  Schulte Grid", self._get_callback("start_schulte")),
        ])

        self._create_section(grid, "APPLIED", 2, [
            ("📖  Pacer & Quiz", self._get_callback("setup_pacer")),
            ("📈  Stats Analysis", self._get_callback("show_stats")),
            ("⚙️  Settings", self._get_callback("show_settings")),
        ])

        # Logout button
        logout_btn = tk.Button(
            self.root,
            text="LOGOUT",
            bg=COLORS["accent"],
            fg=COLORS["btn_text"],
            command=self.navigator.logout,
        )
        logout_btn.place(relx=0.95, rely=0.95, anchor="e")
        self.add_widget(logout_btn)

    def _get_callback(self, name: str) -> Callable:
        """Get a callback by name, or return a no-op if not found."""
        return self.exercise_callbacks.get(name, lambda: None)

    def _create_section(
        self,
        parent: tk.Frame,
        title: str,
        column: int,
        items: list[tuple[str, Callable]],
    ) -> None:
        """Create a section with title and buttons."""
        frame = tk.Frame(parent, bg=COLORS["bg"])
        frame.grid(row=0, column=column, padx=40, sticky="n")

        tk.Label(
            frame,
            text=title,
            font=FONTS["section_header"],
            fg=COLORS["accent"],
            bg=COLORS["bg"],
        ).pack(pady=(0, 15))

        for text, command in items:
            tk.Button(
                frame,
                text=text,
                command=command,
                font=FONTS["btn"],
                bg=COLORS["accent"],
                fg=COLORS["btn_text"],
                width=30,
                pady=8,
                relief="flat",
                activebackground=COLORS["action"],
            ).pack(pady=5)
