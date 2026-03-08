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
        header = tk.Frame(self.root, bg=COLORS["card"], pady=15)
        header.pack(fill="x")
        self.add_widget(header)
        tk.Label(
            header,
            text="TRAINING DASHBOARD",
            font=FONTS["header"],
            fg=COLORS["text_on_card"],
            bg=COLORS["card"],
        ).pack()

        # User summary card (guarded so a data error doesn't block the dashboard)
        try:
            self._build_user_card(self.root)
        except Exception:
            pass

        # Continue path button if there's an active path
        try:
            self._build_continue_button(self.root)
        except Exception:
            pass

        # Personal bests row
        try:
            self._build_personal_bests(self.root)
        except Exception:
            pass

        # Exercise grid container
        grid = tk.Frame(self.root, bg=COLORS["bg"])
        grid.pack(fill="both", expand=True, pady=20)
        self.add_widget(grid)

        # Configure grid columns to center content
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)
        grid.columnconfigure(2, weight=1)

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
            ("🛤️  Training Paths", self._get_callback("show_paths")),
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
        logout_btn.pack(pady=(0, 15))
        self.add_widget(logout_btn)

    def _build_user_card(self, parent) -> None:
        """Build a compact user summary card below the header."""
        user = self.navigator.get_user()
        if not user:
            return

        card = tk.Frame(parent, bg=COLORS["card"], pady=8, padx=20)
        card.pack(fill="x", padx=40, pady=(10, 0))
        self.add_widget(card)

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
            last = user.history[0]
            last_text = f"Last: {last.exercise} — {last.result} ({last.timestamp})"
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
        self.add_widget(bar_frame)

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

    def _build_continue_button(self, parent) -> None:
        """Show a continue button if the user has an active training path."""
        from neural_speed_academy.config import TRAINING_PATHS
        user = self.navigator.get_user()
        if not user or not user.active_path:
            return
        path_data = TRAINING_PATHS.get(user.active_path)
        if not path_data:
            return
        pp = user.path_progress.get(user.active_path)
        if not pp or pp.completed:
            return

        steps = path_data["steps"]
        if pp.current_step >= len(steps):
            return

        _, step_label, _ = steps[pp.current_step]

        btn_frame = tk.Frame(parent, bg=COLORS["bg"])
        btn_frame.pack(fill="x", padx=40, pady=(10, 0))
        self.add_widget(btn_frame)

        tk.Button(
            btn_frame,
            text=f"▶  CONTINUE: {path_data['name']} — {step_label}",
            font=FONTS["btn_bold"],
            bg=COLORS["success"],
            fg=COLORS["btn_text"],
            relief="flat",
            pady=10,
            command=lambda: self.navigator.navigate_to("path_session"),
        ).pack(fill="x")

    def _build_personal_bests(self, parent) -> None:
        """Show a compact row of personal bests if any exist."""
        user = self.navigator.get_user()
        if not user or not user.personal_bests:
            return

        frame = tk.Frame(parent, bg=COLORS["bg"])
        frame.pack(fill="x", padx=40, pady=(10, 0))
        self.add_widget(frame)

        tk.Label(
            frame,
            text="PERSONAL BESTS",
            font=FONTS["section_header"],
            fg=COLORS["accent"],
            bg=COLORS["bg"],
        ).pack(anchor="w")

        row = tk.Frame(frame, bg=COLORS["bg"])
        row.pack(fill="x", pady=(4, 0))

        for exercise, data in user.personal_bests.items():
            cell = tk.Frame(row, bg=COLORS["card"], padx=12, pady=6)
            cell.pack(side="left", padx=(0, 8))
            tk.Label(
                cell,
                text=exercise,
                font=FONTS["btn_sm"],
                fg=COLORS["muted"],
                bg=COLORS["card"],
            ).pack()
            tk.Label(
                cell,
                text=f"{data['score']}/{data['total']}  ({data['pct']}%)",
                font=FONTS["btn_bold"],
                fg=COLORS["text_on_card"],
                bg=COLORS["card"],
            ).pack()

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
