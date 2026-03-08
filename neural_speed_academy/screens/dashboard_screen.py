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

        # Main scrollable area
        main = tk.Frame(self.root, bg=COLORS["bg"])
        main.pack(fill="both", expand=True)
        self.add_widget(main)

        # Header
        header = tk.Frame(main, bg=COLORS["card"], pady=15)
        header.pack(fill="x")
        tk.Label(
            header,
            text="TRAINING DASHBOARD",
            font=FONTS["header"],
            fg=COLORS["text_on_card"],
            bg=COLORS["card"],
        ).pack()

        # User summary card
        self._build_user_card(main)

        # Exercise grid container
        grid = tk.Frame(main, bg=COLORS["bg"])
        grid.pack(pady=20)

        # Create sections
        self._create_section(grid, "PERCEPTION", 0, [
            ("🔢  Flash Numbers", self._get_callback("menu_flash")),
            ("🔤  Word Drills", self._get_callback("menu_words")),
            ("👁️  Eye Priming", self._get_callback("menu_priming")),
        ])

        self._create_section(grid, "SPAN & FOCUS", 1, [
            ("👁️  Eye-Span", self._get_callback("menu_eyespan")),
            ("🏁  Schulte Grid", self._get_callback("start_schulte")),
        ])

        self._create_section(grid, "APPLIED", 2, [
            ("📖  Pacer & Quiz", self._get_callback("setup_pacer")),
            ("⚡  RSVP Reader", self._get_callback("setup_rsvp")),
            ("📦  Chunking", self._get_callback("setup_chunking")),
            ("📈  Stats Analysis", self._get_callback("show_stats")),
            ("⚙️  Settings", self._get_callback("show_settings")),
        ])

        # Logout button
        tk.Button(
            main,
            text="LOGOUT",
            bg=COLORS["accent"],
            fg=COLORS["btn_text"],
            command=self.navigator.logout,
        ).pack(pady=(10, 20))

    def _build_user_card(self, parent: tk.Frame) -> None:
        """Build a compact user summary card below the header."""
        user = self.navigator.get_user()
        if not user:
            return

        card = tk.Frame(parent, bg=COLORS["card"], pady=8, padx=20)
        card.pack(fill="x", padx=40, pady=(10, 0))

        # Left: name + level
        level = int(user.xp / 1000) + 1
        tk.Label(
            card,
            text=f"👤 {user.name.upper()}  |  LEVEL {level}  |  STREAK: {user.streak} Days",
            font=FONTS["btn_sm"],
            fg=COLORS["text_on_card"],
            bg=COLORS["card"],
        ).pack(side="left")

        # Right: last played
        last_text = "No sessions yet"
        if user.history:
            last = user.history[-1]
            last_text = f"Last: {last.exercise} — {last.result} ({last.date})"
        tk.Label(
            card,
            text=last_text,
            font=FONTS["btn_sm"],
            fg=COLORS["muted"],
            bg=COLORS["card"],
        ).pack(side="right")

        # XP progress bar
        xp_in_level = user.xp % 1000
        bar_frame = tk.Frame(parent, bg=COLORS["bg"])
        bar_frame.pack(fill="x", padx=40, pady=(2, 0))

        bar_width = 400
        bar_height = 8
        canvas = tk.Canvas(
            bar_frame, width=bar_width, height=bar_height,
            bg=COLORS["card"], highlightthickness=0
        )
        canvas.pack(side="left", padx=(0, 10))
        fill_width = int(bar_width * xp_in_level / 1000)
        canvas.create_rectangle(0, 0, fill_width, bar_height, fill=COLORS["accent"], width=0)

        tk.Label(
            bar_frame,
            text=f"{xp_in_level}/1000 XP to Level {level + 1}",
            font=FONTS["btn_sm"],
            fg=COLORS["muted"],
            bg=COLORS["bg"],
        ).pack(side="left")

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
