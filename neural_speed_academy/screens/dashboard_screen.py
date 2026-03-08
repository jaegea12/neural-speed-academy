"""
Training hub dashboard.
"""
from __future__ import annotations

import tkinter as tk
from typing import Callable

from neural_speed_academy.screens.base import BaseScreen
from neural_speed_academy.theme import COLORS, FONTS


class DashboardScreen(BaseScreen):
    """Main dashboard showing available training exercises."""

    # Consistent button width for all exercise buttons
    BTN_WIDTH = 28

    def __init__(self, root: tk.Tk, navigator, exercise_callbacks: dict[str, Callable]):
        super().__init__(root, navigator)
        self.exercise_callbacks = exercise_callbacks

    def build(self, **kwargs) -> None:
        """Build the dashboard UI."""
        self.root.configure(bg=COLORS["bg"])

        # Header bar
        header = tk.Frame(self.root, bg=COLORS["card"], pady=12)
        header.pack(fill="x")
        self.add_widget(header)
        tk.Label(
            header,
            text="TRAINING HUB",
            font=FONTS["header"],
            fg=COLORS["text_on_card"],
            bg=COLORS["card"],
        ).pack()

        # User summary card
        try:
            self._build_user_card(self.root)
        except Exception:
            pass

        # Navigation bar: Training Paths | Stats | Logout
        self._build_action_bar(self.root)

        # Continue path button if active
        try:
            self._build_continue_button(self.root)
        except Exception:
            pass

        # Personal bests
        try:
            self._build_personal_bests(self.root)
        except Exception:
            pass

        # Exercise grid — two columns
        grid = tk.Frame(self.root, bg=COLORS["bg"])
        grid.pack(fill="both", expand=True, pady=(15, 10))
        self.add_widget(grid)
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        self._create_section(grid, "PERCEPTION", 0, [
            ("Flash Numbers", self._get_callback("menu_flash")),
            ("Word Drills", self._get_callback("menu_words")),
            ("Eye-Span", self._get_callback("menu_eyespan")),
            ("Schulte Grid", self._get_callback("start_schulte")),
        ])

        self._create_section(grid, "READING", 1, [
            ("Pacer & Quiz", self._get_callback("setup_pacer")),
            ("RSVP Reader", self._get_callback("setup_rsvp")),
            ("Chunking", self._get_callback("setup_chunking")),
            ("Eye Priming", self._get_callback("menu_priming")),
        ])

        # Bottom bar: Main Menu + Logout
        bottom = tk.Frame(self.root, bg=COLORS["bg"])
        bottom.pack(pady=(0, 12))
        self.add_widget(bottom)

        btn_cfg = dict(
            font=FONTS["btn_sm"], relief="flat",
            width=12, pady=4, cursor="hand2",
        )

        tk.Button(
            bottom, text="MAIN MENU",
            bg=COLORS["action"], fg=COLORS["btn_text"],
            command=lambda: self.navigator.navigate_to("main_menu"),
            **btn_cfg,
        ).pack(side="left", padx=4)

        tk.Button(
            bottom, text="LOGOUT",
            bg=COLORS["card"], fg=COLORS["fg"],
            command=self.navigator.logout,
            **btn_cfg,
        ).pack(side="left", padx=4)

    # ── User card ──────────────────────────────────────────────

    def _build_user_card(self, parent) -> None:
        """Compact user summary with XP bar."""
        user = self.navigator.get_user()
        if not user:
            return

        card = tk.Frame(parent, bg=COLORS["card"], pady=8, padx=20)
        card.pack(fill="x", padx=40, pady=(10, 0))
        self.add_widget(card)

        level = user.xp // 1000 + 1
        tk.Label(
            card,
            text=f"{user.name.upper()}   |   Level {level}   |   Streak: {user.streak} day{'s' if user.streak != 1 else ''}",
            font=FONTS["btn_sm"],
            fg=COLORS["text_on_card"],
            bg=COLORS["card"],
        ).pack(side="left")

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
        bar_height = 6
        canvas = tk.Canvas(
            bar_frame, width=bar_width, height=bar_height,
            bg=COLORS["card"], highlightthickness=0,
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

    # ── Action bar (Paths / Stats) ─────────────────────────────

    def _build_action_bar(self, parent) -> None:
        """Horizontal bar with Training Paths and Stats buttons."""
        bar = tk.Frame(parent, bg=COLORS["bg"])
        bar.pack(fill="x", padx=40, pady=(12, 0))
        self.add_widget(bar)

        for label, cb_name in [
            ("Training Paths", "show_paths"),
            ("Stats & History", "show_stats"),
        ]:
            tk.Button(
                bar,
                text=label,
                font=FONTS["btn_bold"],
                bg=COLORS["action"],
                fg=COLORS["btn_text"],
                relief="flat",
                width=20,
                pady=8,
                cursor="hand2",
                command=self._get_callback(cb_name),
            ).pack(side="left", padx=(0, 10))

    # ── Continue path ──────────────────────────────────────────

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
            text=f"CONTINUE: {path_data['name']} — {step_label}",
            font=FONTS["btn_bold"],
            bg=COLORS["success"],
            fg=COLORS["btn_text"],
            relief="flat",
            pady=10,
            cursor="hand2",
            command=lambda: self.navigator.navigate_to("path_session"),
        ).pack(fill="x")

    # ── Personal bests ─────────────────────────────────────────

    def _build_personal_bests(self, parent) -> None:
        """Compact row of personal bests."""
        user = self.navigator.get_user()
        if not user or not user.personal_bests:
            return

        frame = tk.Frame(parent, bg=COLORS["bg"])
        frame.pack(fill="x", padx=40, pady=(10, 0))
        self.add_widget(frame)

        # Section divider
        self._section_divider(frame, "PERSONAL BESTS")

        row = tk.Frame(frame, bg=COLORS["bg"])
        row.pack(fill="x", pady=(4, 0))

        for exercise, data in user.personal_bests.items():
            cell = tk.Frame(row, bg=COLORS["card"], padx=12, pady=6)
            cell.pack(side="left", padx=(0, 8))
            tk.Label(
                cell, text=exercise,
                font=FONTS["btn_sm"], fg=COLORS["muted"], bg=COLORS["card"],
            ).pack()
            tk.Label(
                cell,
                text=f"{data['score']}/{data['total']}  ({data['pct']}%)",
                font=FONTS["btn_bold"], fg=COLORS["text_on_card"], bg=COLORS["card"],
            ).pack()

    # ── Helpers ─────────────────────────────────────────────────

    def _get_callback(self, name: str) -> Callable:
        return self.exercise_callbacks.get(name, lambda: None)

    @staticmethod
    def _section_divider(parent: tk.Frame, title: str) -> None:
        """Thin line with section label — fieldset style."""
        row = tk.Frame(parent, bg=COLORS["bg"])
        row.pack(fill="x", pady=(0, 4))

        tk.Frame(row, bg=COLORS["muted"], height=1).pack(
            side="left", fill="x", expand=True, pady=6, padx=(0, 8),
        )
        tk.Label(
            row, text=title,
            font=FONTS["menu_header"], fg=COLORS["muted"], bg=COLORS["bg"],
        ).pack(side="left")
        tk.Frame(row, bg=COLORS["muted"], height=1).pack(
            side="left", fill="x", expand=True, pady=6, padx=(8, 0),
        )

    def _create_section(
        self,
        parent: tk.Frame,
        title: str,
        column: int,
        items: list[tuple[str, Callable]],
    ) -> None:
        """Create a section with divider header and uniform-width buttons."""
        frame = tk.Frame(parent, bg=COLORS["bg"])
        frame.grid(row=0, column=column, padx=40, sticky="n")

        self._section_divider(frame, title)

        for text, command in items:
            tk.Button(
                frame,
                text=text,
                command=command,
                font=FONTS["btn"],
                bg=COLORS["accent"],
                fg=COLORS["btn_text"],
                width=self.BTN_WIDTH,
                pady=8,
                relief="flat",
                cursor="hand2",
                activebackground=COLORS["action"],
            ).pack(pady=4)
