"""
Stats/Analytics screen showing user performance data.
"""
from __future__ import annotations

from collections import Counter
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

        # Scrollable container
        canvas = tk.Canvas(self.root, bg=COLORS["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.configure(yscrollcommand=scrollbar.set)
        self.add_widget(canvas)

        container = tk.Frame(canvas, bg=COLORS["bg"])
        canvas.create_window((0, 0), window=container, anchor="nw")

        # Title
        tk.Label(
            container,
            text="PERFORMANCE ANALYTICS",
            font=FONTS["header"],
            fg=COLORS["accent"],
            bg=COLORS["bg"],
        ).pack(pady=(20, 20), padx=50)

        # Summary stats
        self._build_summary_section(container, user)

        # Exercise breakdown chart
        self._build_exercise_chart(container, user)

        # Personal bests
        self._build_personal_bests(container, user)

        # History section
        self._build_history_section(container, user)

        # Update scroll region after layout
        container.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

        # Mouse wheel scrolling — bind to root and unbind on destroy
        def _on_mousewheel(e):
            canvas.yview_scroll(-1 * (e.delta // 120), "units")

        self._mw_binding = self.root.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind("<Destroy>", lambda e: self.root.unbind_all("<MouseWheel>"))

    def _show_no_user_message(self) -> None:
        """Show message when no user is logged in."""
        tk.Label(
            self.root,
            text="No user logged in",
            font=FONTS["header"],
            fg=COLORS["alert"],
            bg=COLORS["bg"],
        ).pack(expand=True)

    def _build_summary_section(self, parent: tk.Frame, user) -> None:
        """Build the summary stats section."""
        summary_frame = tk.Frame(parent, bg=COLORS["card"], padx=20, pady=20)
        summary_frame.pack(fill="x", padx=50, pady=(0, 15))

        stats = [
            ("TOTAL XP", str(user.xp)),
            ("LEVEL", str(user.xp // 1000 + 1)),
            ("STREAK", f"{user.streak} day{'s' if user.streak != 1 else ''}"),
            ("SESSIONS", str(len(user.history))),
        ]

        for label, value in stats:
            cell = tk.Frame(summary_frame, bg=COLORS["card"])
            cell.pack(side="left", expand=True)
            tk.Label(
                cell, text=value,
                font=FONTS["sub"], fg=COLORS["accent"], bg=COLORS["card"],
            ).pack()
            tk.Label(
                cell, text=label,
                font=FONTS["btn_sm"], fg=COLORS["muted"], bg=COLORS["card"],
            ).pack()

    def _build_exercise_chart(self, parent: tk.Frame, user) -> None:
        """Bar chart showing session counts per exercise type."""
        if not user.history:
            return

        counts = Counter(entry.exercise for entry in user.history)
        if not counts:
            return

        frame = tk.Frame(parent, bg=COLORS["bg"])
        frame.pack(fill="x", padx=50, pady=(0, 15))

        tk.Label(
            frame, text="SESSIONS BY EXERCISE",
            font=FONTS["section_header"], fg=COLORS["fg"], bg=COLORS["bg"],
        ).pack(anchor="w", pady=(0, 8))

        max_count = max(counts.values())
        chart_width = 500
        bar_height = 24
        label_width = 120

        canvas = tk.Canvas(
            frame,
            width=chart_width + label_width + 60,
            height=(bar_height + 6) * len(counts) + 10,
            bg=COLORS["card"],
            highlightthickness=0,
        )
        canvas.pack(anchor="w")

        y = 10
        for exercise, count in sorted(counts.items(), key=lambda x: -x[1]):
            # Label
            canvas.create_text(
                label_width, y + bar_height // 2,
                text=exercise, anchor="e",
                font=FONTS["btn_sm"], fill=COLORS["text_on_card"],
            )
            # Bar
            bar_w = int(chart_width * count / max_count) if max_count > 0 else 0
            canvas.create_rectangle(
                label_width + 10, y,
                label_width + 10 + bar_w, y + bar_height,
                fill=COLORS["accent"], width=0,
            )
            # Count label
            canvas.create_text(
                label_width + 15 + bar_w, y + bar_height // 2,
                text=str(count), anchor="w",
                font=FONTS["btn_sm"], fill=COLORS["text_on_card"],
            )
            y += bar_height + 6

    def _build_personal_bests(self, parent: tk.Frame, user) -> None:
        """Display personal bests in a grid."""
        if not user.personal_bests:
            return

        frame = tk.Frame(parent, bg=COLORS["bg"])
        frame.pack(fill="x", padx=50, pady=(0, 15))

        tk.Label(
            frame, text="PERSONAL BESTS",
            font=FONTS["section_header"], fg=COLORS["fg"], bg=COLORS["bg"],
        ).pack(anchor="w", pady=(0, 8))

        row = tk.Frame(frame, bg=COLORS["bg"])
        row.pack(fill="x")

        for exercise, data in user.personal_bests.items():
            cell = tk.Frame(row, bg=COLORS["card"], padx=14, pady=10)
            cell.pack(side="left", padx=(0, 8))
            tk.Label(
                cell, text=exercise,
                font=FONTS["btn_sm"], fg=COLORS["muted"], bg=COLORS["card"],
            ).pack()
            tk.Label(
                cell,
                text=f"{data['score']}/{data['total']}",
                font=FONTS["sub"], fg=COLORS["text_on_card"], bg=COLORS["card"],
            ).pack()
            tk.Label(
                cell, text=f"{data['pct']}%",
                font=FONTS["btn_sm"], fg=COLORS["accent"], bg=COLORS["card"],
            ).pack()
            tk.Label(
                cell, text=data.get("date", ""),
                font=FONTS["btn_sm"], fg=COLORS["muted"], bg=COLORS["card"],
            ).pack()

    def _build_history_section(self, parent: tk.Frame, user) -> None:
        """Build the session history section."""
        frame = tk.Frame(parent, bg=COLORS["bg"])
        frame.pack(fill="x", padx=50, pady=(0, 20))

        tk.Label(
            frame, text="SESSION HISTORY",
            font=FONTS["section_header"], fg=COLORS["fg"], bg=COLORS["bg"],
        ).pack(anchor="w", pady=(0, 8))

        if not user.history:
            tk.Label(
                frame, text="No sessions yet. Start training!",
                font=FONTS["body"], fg=COLORS["muted"], bg=COLORS["bg"],
            ).pack(anchor="w")
            return

        # Configure treeview style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background=COLORS["card"],
            foreground=COLORS["text_on_card"],
            fieldbackground=COLORS["card"],
            font=FONTS["treeview"],
        )
        style.configure(
            "Treeview.Heading",
            background=COLORS["grid_btn"],
            foreground=COLORS["text_on_card"],
            font=FONTS["treeview_heading"],
        )
        style.map("Treeview", background=[("selected", COLORS["accent"])])

        # Tree frame
        tree_frame = tk.Frame(frame, bg=COLORS["bg"])
        tree_frame.pack(fill="x")

        columns = ("date", "type", "result")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
        tree.heading("date", text="Time")
        tree.heading("type", text="Exercise")
        tree.heading("result", text="Result")
        tree.column("date", width=150)
        tree.column("type", width=200)
        tree.column("result", width=150)
        tree.pack(side="left", fill="x", expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        for entry in user.history:
            tree.insert("", "end", values=(entry.timestamp, entry.exercise, entry.result))
