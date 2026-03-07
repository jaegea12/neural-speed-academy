"""
Stats/Analytics screen showing user performance data.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from neural_speed_academy.screens.base import BaseScreen
from neural_speed_academy.theme import COLORS, FONTS


class StatsScreen(BaseScreen):
    """Performance analytics screen showing XP, level, streak, and history."""

    def build(self, **kwargs) -> None:
        """Build the stats UI."""
        self.root.configure(bg=COLORS["bg"])
        self.add_nav_bar()

        user = self.navigator.get_user()
        if not user:
            self._show_no_user_message()
            return

        # Main container
        container = tk.Frame(self.root, bg=COLORS["bg"])
        container.pack(expand=True, fill="both", padx=50, pady=20)
        self.add_widget(container)

        # Title
        tk.Label(
            container,
            text="PERFORMANCE ANALYTICS",
            font=FONTS["header"],
            fg=COLORS["accent"],
            bg=COLORS["bg"]
        ).pack(pady=(0, 20))

        # Summary stats
        self._build_summary_section(container, user)

        # History section
        self._build_history_section(container, user)

    def _show_no_user_message(self) -> None:
        """Show message when no user is logged in."""
        tk.Label(
            self.root,
            text="No user logged in",
            font=FONTS["header"],
            fg=COLORS["alert"],
            bg=COLORS["bg"]
        ).pack(expand=True)

    def _build_summary_section(self, parent: tk.Frame, user) -> None:
        """Build the summary stats section."""
        summary_frame = tk.Frame(parent, bg=COLORS["card"], padx=20, pady=20)
        summary_frame.pack(fill="x", pady=(0, 20))

        # XP
        tk.Label(
            summary_frame,
            text=f"TOTAL XP: {user.xp}",
            font=FONTS["sub"],
            fg=COLORS["text_on_card"],
            bg=COLORS["card"]
        ).pack(side="left", expand=True)

        # Level
        level = int(user.xp / 1000) + 1
        tk.Label(
            summary_frame,
            text=f"CURRENT LEVEL: {level}",
            font=FONTS["sub"],
            fg=COLORS["text_on_card"],
            bg=COLORS["card"]
        ).pack(side="left", expand=True)

        # Streak
        tk.Label(
            summary_frame,
            text=f"STREAK: {user.streak} Days",
            font=FONTS["sub"],
            fg=COLORS["text_on_card"],
            bg=COLORS["card"]
        ).pack(side="left", expand=True)

    def _build_history_section(self, parent: tk.Frame, user) -> None:
        """Build the session history section."""
        tk.Label(
            parent,
            text="SESSION HISTORY",
            font=FONTS["section_header"],
            fg=COLORS["fg"],
            bg=COLORS["bg"]
        ).pack(anchor="w")

        # Configure treeview style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background=COLORS["card"],
            foreground=COLORS["text_on_card"],
            fieldbackground=COLORS["card"],
            font=FONTS["treeview"]
        )
        style.configure(
            "Treeview.Heading",
            background=COLORS["grid_btn"],
            foreground=COLORS["text_on_card"],
            font=FONTS["treeview_heading"]
        )
        style.map("Treeview", background=[("selected", COLORS["accent"])])

        # Tree frame with scrollbar
        tree_frame = tk.Frame(parent, bg=COLORS["bg"])
        tree_frame.pack(fill="both", expand=True)

        columns = ("date", "type", "result")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
        tree.heading("date", text="Time")
        tree.heading("type", text="Exercise")
        tree.heading("result", text="Result")
        tree.column("date", width=150)
        tree.column("type", width=200)
        tree.column("result", width=150)
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        # Populate history
        for entry in user.history:
            tree.insert("", "end", values=(entry.timestamp, entry.exercise, entry.result))
