"""
Training path selection and execution screens.
"""
from __future__ import annotations

import random
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable

from neural_speed_academy.screens.base import BaseScreen
from neural_speed_academy.theme import COLORS, FONTS
from neural_speed_academy.config import TRAINING_PATHS
from neural_speed_academy.state import PathProgress


class PathSelectionScreen(BaseScreen):
    """Screen for selecting a training path."""

    def build(self, **kwargs) -> None:
        """Build the path selection UI."""
        self.root.configure(bg=COLORS["bg"])
        self.add_nav_bar()

        container = tk.Frame(self.root, bg=COLORS["bg"])
        container.pack(fill="both", expand=True)
        self.add_widget(container)

        tk.Label(
            container,
            text="TRAINING PATHS",
            font=FONTS["header"],
            fg=COLORS["accent"],
            bg=COLORS["bg"],
        ).pack(pady=(20, 5))

        tk.Label(
            container,
            text="Structured programs that combine exercises for specific goals",
            font=FONTS["sub"],
            fg=COLORS["muted"],
            bg=COLORS["bg"],
        ).pack(pady=(0, 20))

        user = self.navigator.get_user()

        # Path cards
        cards_frame = tk.Frame(container, bg=COLORS["bg"])
        cards_frame.pack(expand=True)

        # Built-in paths
        all_paths = list(TRAINING_PATHS.items())

        # Custom paths from user profile
        if user and user.custom_paths:
            for cid, cdata in user.custom_paths.items():
                all_paths.append((cid, cdata))

        for i, (path_id, path_data) in enumerate(all_paths):
            row = i // 3
            col = i % 3
            self._create_path_card(cards_frame, path_id, path_data, user, row, col)

        # Create custom path button
        btn_frame = tk.Frame(container, bg=COLORS["bg"])
        btn_frame.pack(pady=(15, 10))

        tk.Button(
            btn_frame, text="+ CREATE CUSTOM PATH",
            font=FONTS["btn_bold"],
            bg=COLORS["action"], fg=COLORS["btn_text"],
            relief="flat", width=24, pady=8, cursor="hand2",
            command=self._create_custom_path,
        ).pack()

    def _create_custom_path(self) -> None:
        """Navigate to the path builder."""
        user = self.navigator.get_user()
        if not user:
            messagebox.showinfo("Login Required", "Please log in first.")
            self.navigator.require_login("paths")
            return
        self.navigator.navigate_to("path_builder")

    def _create_path_card(self, parent, path_id: str, path_data: dict,
                          user, row: int, col: int) -> None:
        """Create a card for a training path."""
        card = tk.Frame(parent, bg=COLORS["card"], padx=15, pady=15)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        # Path name
        tk.Label(
            card,
            text=path_data["name"],
            font=FONTS["section_header"],
            fg=COLORS["accent"],
            bg=COLORS["card"],
        ).pack(anchor="w")

        # Description
        tk.Label(
            card,
            text=path_data["description"],
            font=FONTS["body"],
            fg=COLORS["text_on_card"],
            bg=COLORS["card"],
            wraplength=250,
            justify="left",
        ).pack(anchor="w", pady=(5, 5))

        # Step count and estimated time
        step_count = len(path_data["steps"])
        est_min = step_count * 2
        tk.Label(
            card,
            text=f"{step_count} exercises  ~{est_min} min",
            font=FONTS["btn_sm"],
            fg=COLORS["muted"],
            bg=COLORS["card"],
        ).pack(anchor="w")

        # Progress indicator
        progress_text = "Not started"
        btn_text = "START"
        if user:
            pp = user.path_progress.get(path_id)
            if pp and not pp.completed:
                progress_text = f"Step {pp.current_step + 1}/{step_count}"
                btn_text = "CONTINUE"
            elif pp and pp.completed:
                progress_text = "Completed ✓"
                btn_text = "RESTART"

        tk.Label(
            card,
            text=progress_text,
            font=FONTS["btn_sm"],
            fg=COLORS["accent"],
            bg=COLORS["card"],
        ).pack(anchor="w", pady=(2, 8))

        # Action button
        tk.Button(
            card,
            text=btn_text,
            font=FONTS["btn_bold"],
            bg=COLORS["accent"],
            fg=COLORS["btn_text"],
            relief="flat",
            width=15,
            pady=6,
            cursor="hand2",
            command=lambda pid=path_id: self._start_path(pid),
        ).pack()

    def _start_path(self, path_id: str) -> None:
        """Start or continue a training path."""
        user = self.navigator.get_user()
        if not user:
            messagebox.showinfo("Login Required", "Please log in first.")
            self.navigator.require_login("paths")
            return

        pp = user.path_progress.get(path_id)
        if pp and pp.completed:
            # Restart
            pp.current_step = 0
            pp.completed = False
            pp.start_xp = user.xp
        elif not pp:
            pp = PathProgress(path_id=path_id, start_xp=user.xp)
            user.path_progress[path_id] = pp

        user.active_path = path_id
        self.navigator.user_repo.save(user)
        self.navigator.navigate_to("path_session")


class PathSessionScreen(BaseScreen):
    """Screen showing the current step in a training path and launching exercises."""

    def build(self, **kwargs) -> None:
        """Build the path session UI."""
        self.root.configure(bg=COLORS["bg"])
        self.add_nav_bar()

        user = self.navigator.get_user()
        if not user or not user.active_path:
            self.navigator.to_dashboard()
            return

        path_id = user.active_path
        path_data = TRAINING_PATHS.get(path_id) or user.custom_paths.get(path_id)
        if not path_data:
            self.navigator.to_dashboard()
            return

        pp = user.path_progress.get(path_id)
        if not pp:
            pp = PathProgress(path_id=path_id, start_xp=user.xp)
            user.path_progress[path_id] = pp

        steps = path_data["steps"]
        current = pp.current_step

        if current >= len(steps):
            pp.completed = True
            user.active_path = None
            self.navigator.user_repo.save(user)
            self._show_path_complete(path_data)
            return

        container = tk.Frame(self.root, bg=COLORS["bg"])
        container.pack(expand=True)
        self.add_widget(container)

        # Path title
        tk.Label(
            container,
            text=path_data["name"].upper(),
            font=FONTS["header"],
            fg=COLORS["accent"],
            bg=COLORS["bg"],
        ).pack(pady=(0, 10))

        # Progress bar
        progress_frame = tk.Frame(container, bg=COLORS["bg"])
        progress_frame.pack(pady=(0, 20))

        bar_width = 500
        bar_height = 12
        canvas = tk.Canvas(
            progress_frame, width=bar_width, height=bar_height,
            bg=COLORS["card"], highlightthickness=0
        )
        canvas.pack()
        fill = int(bar_width * current / len(steps))
        canvas.create_rectangle(0, 0, fill, bar_height, fill=COLORS["accent"], width=0)

        tk.Label(
            progress_frame,
            text=f"Step {current + 1} of {len(steps)}",
            font=FONTS["counter"],
            fg=COLORS["fg"],
            bg=COLORS["bg"],
        ).pack(pady=5)

        # Step list (scrollable for long paths)
        list_outer = tk.Frame(container, bg=COLORS["bg"])
        list_outer.pack(pady=10, fill="x")

        max_visible = 12
        needs_scroll = len(steps) > max_visible

        if needs_scroll:
            list_canvas = tk.Canvas(
                list_outer, bg=COLORS["bg"], highlightthickness=0,
                height=max_visible * 24,
            )
            list_scrollbar = ttk.Scrollbar(
                list_outer, orient="vertical", command=list_canvas.yview,
            )
            list_canvas.configure(yscrollcommand=list_scrollbar.set)
            list_scrollbar.pack(side="right", fill="y")
            list_canvas.pack(side="left", fill="x", expand=True)

            list_frame = tk.Frame(list_canvas, bg=COLORS["bg"])
            list_canvas.create_window((0, 0), window=list_frame, anchor="nw")

            def _on_mw(e):
                list_canvas.yview_scroll(-1 * (e.delta // 120), "units")
            list_canvas.bind_all("<MouseWheel>", _on_mw)
            list_canvas.bind(
                "<Destroy>", lambda e: self.root.unbind_all("<MouseWheel>"),
            )
        else:
            list_frame = tk.Frame(list_outer, bg=COLORS["bg"])
            list_frame.pack()

        for i, (ex_type, label, params) in enumerate(steps):
            if i < current:
                marker = "✅"
                fg = COLORS["muted"]
            elif i == current:
                marker = "▶"
                fg = COLORS["accent"]
            else:
                marker = "○"
                fg = COLORS["muted"]

            tk.Label(
                list_frame,
                text=f"  {marker}  {label}",
                font=FONTS["body"],
                fg=fg,
                bg=COLORS["bg"],
                anchor="w",
                width=50,
            ).pack(anchor="w", pady=1)

        if needs_scroll:
            list_frame.update_idletasks()
            list_canvas.configure(scrollregion=list_canvas.bbox("all"))
            # Scroll to show current step
            if current > 0:
                frac = max(0, (current - 2)) / len(steps)
                list_canvas.yview_moveto(frac)

        # Current step action
        ex_type, label, params = steps[current]

        tk.Button(
            container,
            text=f"▶  {label}",
            font=FONTS["btn_lg"],
            bg=COLORS["accent"],
            fg=COLORS["btn_text"],
            relief="flat",
            width=35,
            pady=12,
            cursor="hand2",
            command=lambda: self._launch_step(ex_type, params, path_id, current),
        ).pack(pady=20)

        # Previous / Skip buttons
        nav_row = tk.Frame(container, bg=COLORS["bg"])
        nav_row.pack(pady=(0, 10))

        if current > 0:
            tk.Button(
                nav_row,
                text="← PREVIOUS STEP",
                font=FONTS["btn_sm"],
                bg=COLORS["card"],
                fg=COLORS["fg"],
                relief="flat",
                cursor="hand2",
                command=lambda: self._go_to_step(path_id, current - 1),
            ).pack(side="left", padx=6)

        tk.Button(
            nav_row,
            text="SKIP THIS STEP →",
            font=FONTS["btn_sm"],
            bg=COLORS["card"],
            fg=COLORS["fg"],
            relief="flat",
            cursor="hand2",
            command=lambda: self._advance_step(path_id, current),
        ).pack(side="left", padx=6)

    def _go_to_step(self, path_id: str, step_idx: int) -> None:
        """Jump to a specific step in the path."""
        user = self.navigator.get_user()
        if not user:
            return
        pp = user.path_progress.get(path_id)
        if pp:
            pp.current_step = step_idx
            pp.completed = False
            self.navigator.user_repo.save(user)
        self.navigator.navigate_to("path_session")

    def _launch_step(self, ex_type: str, params: dict, path_id: str,
                     step_idx: int) -> None:
        """Launch the exercise for the current step."""
        user = self.navigator.get_user()
        if user:
            user.active_path = path_id
            self.navigator.user_repo.save(user)

        # Tell the navigator to advance this path step when the exercise ends
        self.navigator._path_step_pending = (path_id, step_idx)

        # Launch the appropriate exercise
        app = self.navigator._app
        if ex_type == "priming":
            app.priming_exercise.start(**params)
        elif ex_type == "flash":
            digits = params.get("digits")
            low = params.get("low", digits or 3)
            high = params.get("high", digits or 3)
            rounds = params.get("rounds", 10)
            _low, _high = low, high
            app.flash_exercise.start(
                mode="flash_num",
                rounds=rounds,
                level_func=lambda _, lo=_low, hi=_high: random.randint(lo, hi),
            )
        elif ex_type == "eyespan":
            _low = params.get("low", 2)
            _high = params.get("high", 3)
            app.flash_exercise.start(
                mode="eyespan",
                rounds=params.get("rounds", 10),
                level_func=lambda _, lo=_low, hi=_high: random.randint(lo, hi),
                span_config={
                    "mode": params.get("mode", "h"),
                    "width": params.get("width", 50),
                },
            )
        elif ex_type == "schulte":
            app.schulte_exercise.start()
        elif ex_type == "pacer":
            app.pacer_exercise.start()
        elif ex_type == "rsvp":
            app.rsvp_exercise.start(**params)
        elif ex_type == "chunking":
            app.chunking_exercise.start(**params)

    def _show_path_complete(self, path_data: dict) -> None:
        """Display a path completion screen with session summary."""
        user = self.navigator.get_user()

        container = tk.Frame(self.root, bg=COLORS["bg"])
        container.pack(expand=True)
        self.add_widget(container)

        tk.Label(
            container, text="PATH COMPLETE",
            font=FONTS["header"], fg=COLORS["accent"], bg=COLORS["bg"],
        ).pack(pady=(0, 10))

        tk.Label(
            container, text=path_data["name"],
            font=FONTS["sub"], fg=COLORS["fg"], bg=COLORS["bg"],
        ).pack(pady=5)

        tk.Label(
            container, text="✓",
            font=("Segoe UI", 48),
            fg=COLORS["success"], bg=COLORS["bg"],
        ).pack(pady=(10, 5))

        # Session summary card
        summary = tk.Frame(container, bg=COLORS["card"], padx=20, pady=15)
        summary.pack(padx=40, pady=10, fill="x")

        step_count = len(path_data["steps"])
        xp_earned = 0
        if user:
            pp = user.path_progress.get(path_data.get("id", ""), None)
            # Try to find the matching PathProgress
            for pid, prog in user.path_progress.items():
                if prog.completed and path_data["name"] == TRAINING_PATHS.get(pid, {}).get("name"):
                    xp_earned = user.xp - prog.start_xp
                    break

        stats = [
            ("EXERCISES", str(step_count)),
            ("XP EARNED", f"+{max(0, xp_earned)}"),
            ("LEVEL", str(user.xp // 1000 + 1) if user else "—"),
        ]

        for label, value in stats:
            cell = tk.Frame(summary, bg=COLORS["card"])
            cell.pack(side="left", expand=True)
            tk.Label(
                cell, text=value,
                font=FONTS["sub"], fg=COLORS["accent"], bg=COLORS["card"],
            ).pack()
            tk.Label(
                cell, text=label,
                font=FONTS["btn_sm"], fg=COLORS["muted"], bg=COLORS["card"],
            ).pack()

        btn_row = tk.Frame(container, bg=COLORS["bg"])
        btn_row.pack(pady=15)

        tk.Button(
            btn_row, text="TRAINING PATHS",
            font=FONTS["btn_bold"],
            bg=COLORS["accent"], fg=COLORS["btn_text"],
            relief="flat", width=18, pady=8, cursor="hand2",
            command=lambda: self.navigator.navigate_to("paths"),
        ).pack(side="left", padx=6)

        tk.Button(
            btn_row, text="TRAINING HUB",
            font=FONTS["btn_bold"],
            bg=COLORS["action"], fg=COLORS["btn_text"],
            relief="flat", width=18, pady=8, cursor="hand2",
            command=self.navigator.to_dashboard,
        ).pack(side="left", padx=6)

    def _advance_step(self, path_id: str, step_idx: int) -> None:
        """Advance to the next step and refresh the path session screen."""
        user = self.navigator.get_user()
        if not user:
            return
        pp = user.path_progress.get(path_id)
        if pp and pp.current_step == step_idx:
            pp.current_step += 1
            path_data = TRAINING_PATHS.get(path_id) or user.custom_paths.get(path_id, {})
            if pp.current_step >= len(path_data.get("steps", [])):
                pp.completed = True
                user.active_path = None
            self.navigator.user_repo.save(user)
        self.navigator.navigate_to("path_session")


# ── Exercise catalog for the path builder ─────────────────────

EXERCISE_CATALOG = [
    ("priming", "Eye Priming", [
        ("Horizontal Saccades", {"mode": "saccade_h", "delay": 500}),
        ("Vertical Saccades", {"mode": "saccade_v", "delay": 500}),
        ("Diagonal Saccades", {"mode": "saccade_diag", "delay": 450}),
        ("Expanding Saccades", {"mode": "saccade_expand", "delay": 500}),
        ("Smooth Pursuit Circle", {"mode": "pursuit_circle", "cycles": 10}),
        ("Figure-8 Pursuit", {"mode": "pursuit_figure8", "cycles": 12}),
    ]),
    ("flash", "Flash Digits", [
        ("3 Digits", {"digits": 3, "rounds": 10}),
        ("4 Digits", {"digits": 4, "rounds": 10}),
        ("5 Digits", {"digits": 5, "rounds": 12}),
        ("3-5 Digits", {"low": 3, "high": 5, "rounds": 12}),
        ("5-7 Digits", {"low": 5, "high": 7, "rounds": 15}),
        ("7-9 Digits", {"low": 7, "high": 9, "rounds": 15}),
    ]),
    ("eyespan", "Eye-Span", [
        ("Horizontal 30%", {"mode": "h", "width": 30, "low": 2, "high": 2, "rounds": 10}),
        ("Horizontal 50%", {"mode": "h", "width": 50, "low": 2, "high": 3, "rounds": 10}),
        ("Vertical 50%", {"mode": "v", "width": 50, "low": 2, "high": 3, "rounds": 10}),
        ("Mixed 60%", {"mode": "m", "width": 60, "low": 3, "high": 4, "rounds": 12}),
    ]),
    ("schulte", "Schulte Grid", [
        ("Standard Grid", {}),
    ]),
    ("rsvp", "RSVP Reader", [
        ("200 WPM", {"wpm": 200}),
        ("300 WPM", {"wpm": 300}),
        ("400 WPM", {"wpm": 400}),
        ("500 WPM", {"wpm": 500}),
        ("600 WPM", {"wpm": 600}),
        ("800 WPM", {"wpm": 800}),
    ]),
    ("chunking", "Chunking", [
        ("2-Word at 200 WPM", {"chunk_size": 2, "wpm": 200}),
        ("3-Word at 300 WPM", {"chunk_size": 3, "wpm": 300}),
        ("4-Word at 400 WPM", {"chunk_size": 4, "wpm": 400}),
        ("5-Word at 500 WPM", {"chunk_size": 5, "wpm": 500}),
    ]),
    ("pacer", "Pacer & Quiz", [
        ("Comprehension Check", {}),
    ]),
]


class PathBuilderScreen(BaseScreen):
    """Screen for creating custom training paths."""

    def __init__(self, root, navigator):
        super().__init__(root, navigator)
        self._steps: list[tuple[str, str, dict]] = []

    def build(self, **kwargs) -> None:
        self.root.configure(bg=COLORS["bg"])
        self.add_nav_bar()
        self._steps = []

        container = tk.Frame(self.root, bg=COLORS["bg"])
        container.pack(fill="both", expand=True, padx=40, pady=10)
        self.add_widget(container)

        tk.Label(
            container, text="CREATE CUSTOM PATH",
            font=FONTS["header"], fg=COLORS["accent"], bg=COLORS["bg"],
        ).pack(pady=(10, 15))

        # Path name
        name_row = tk.Frame(container, bg=COLORS["bg"])
        name_row.pack(fill="x", pady=(0, 10))

        tk.Label(
            name_row, text="Path Name:",
            font=FONTS["btn_bold"], fg=COLORS["fg"], bg=COLORS["bg"],
        ).pack(side="left", padx=(0, 10))

        self._name_entry = tk.Entry(
            name_row, font=FONTS["body"], width=30,
            bg=COLORS["card"], fg=COLORS["text_on_card"],
            insertbackground=COLORS["text_on_card"], relief="flat",
        )
        self._name_entry.pack(side="left")

        # Two-column layout: catalog left, steps right
        columns = tk.Frame(container, bg=COLORS["bg"])
        columns.pack(fill="both", expand=True)

        # Left: exercise catalog
        left = tk.Frame(columns, bg=COLORS["bg"])
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        tk.Label(
            left, text="EXERCISE CATALOG",
            font=FONTS["section_header"], fg=COLORS["fg"], bg=COLORS["bg"],
        ).pack(anchor="w", pady=(0, 5))

        cat_canvas = tk.Canvas(left, bg=COLORS["bg"], highlightthickness=0, height=300)
        cat_scroll = ttk.Scrollbar(left, orient="vertical", command=cat_canvas.yview)
        cat_scroll.pack(side="right", fill="y")
        cat_canvas.pack(side="left", fill="both", expand=True)
        cat_canvas.configure(yscrollcommand=cat_scroll.set)

        cat_frame = tk.Frame(cat_canvas, bg=COLORS["bg"])
        cat_canvas.create_window((0, 0), window=cat_frame, anchor="nw")

        for ex_type, group_name, variants in EXERCISE_CATALOG:
            tk.Label(
                cat_frame, text=group_name,
                font=FONTS["btn_bold"], fg=COLORS["accent"], bg=COLORS["bg"],
            ).pack(anchor="w", pady=(8, 2))

            for variant_name, params in variants:
                label = f"{group_name}: {variant_name}"
                tk.Button(
                    cat_frame, text=f"  + {variant_name}",
                    font=FONTS["body"], fg=COLORS["fg"], bg=COLORS["card"],
                    anchor="w", width=28, relief="flat", cursor="hand2",
                    command=lambda t=ex_type, l=label, p=params: self._add_step(t, l, p),
                ).pack(anchor="w", pady=1)

        cat_frame.update_idletasks()
        cat_canvas.configure(scrollregion=cat_canvas.bbox("all"))

        # Right: current steps
        right = tk.Frame(columns, bg=COLORS["bg"])
        right.pack(side="left", fill="both", expand=True, padx=(10, 0))

        tk.Label(
            right, text="YOUR PATH",
            font=FONTS["section_header"], fg=COLORS["fg"], bg=COLORS["bg"],
        ).pack(anchor="w", pady=(0, 5))

        self._steps_frame = tk.Frame(right, bg=COLORS["bg"])
        self._steps_frame.pack(fill="both", expand=True)

        self._refresh_steps()

        # Bottom buttons
        btn_row = tk.Frame(container, bg=COLORS["bg"])
        btn_row.pack(pady=(15, 10))

        tk.Button(
            btn_row, text="SAVE PATH",
            font=FONTS["btn_bold"],
            bg=COLORS["accent"], fg=COLORS["btn_text"],
            relief="flat", width=16, pady=8, cursor="hand2",
            command=self._save_path,
        ).pack(side="left", padx=6)

        tk.Button(
            btn_row, text="CANCEL",
            font=FONTS["btn_bold"],
            bg=COLORS["card"], fg=COLORS["fg"],
            relief="flat", width=16, pady=8, cursor="hand2",
            command=lambda: self.navigator.navigate_to("paths"),
        ).pack(side="left", padx=6)

    def _add_step(self, ex_type: str, label: str, params: dict) -> None:
        """Add an exercise step to the path."""
        self._steps.append((ex_type, label, params))
        self._refresh_steps()

    def _remove_step(self, index: int) -> None:
        """Remove a step by index."""
        if 0 <= index < len(self._steps):
            self._steps.pop(index)
            self._refresh_steps()

    def _refresh_steps(self) -> None:
        """Redraw the steps list."""
        for w in self._steps_frame.winfo_children():
            w.destroy()

        if not self._steps:
            tk.Label(
                self._steps_frame,
                text="Add exercises from the catalog\nto build your path.",
                font=FONTS["body"], fg=COLORS["muted"], bg=COLORS["bg"],
                justify="center",
            ).pack(expand=True)
            return

        for i, (ex_type, label, params) in enumerate(self._steps):
            row = tk.Frame(self._steps_frame, bg=COLORS["bg"])
            row.pack(fill="x", pady=1)

            tk.Label(
                row, text=f"{i + 1}.",
                font=FONTS["btn_sm"], fg=COLORS["muted"], bg=COLORS["bg"],
                width=3,
            ).pack(side="left")

            tk.Label(
                row, text=label,
                font=FONTS["body"], fg=COLORS["fg"], bg=COLORS["bg"],
                anchor="w",
            ).pack(side="left", fill="x", expand=True)

            tk.Button(
                row, text="✗",
                font=FONTS["btn_sm"], fg=COLORS["alert"], bg=COLORS["bg"],
                relief="flat", cursor="hand2", bd=0,
                command=lambda idx=i: self._remove_step(idx),
            ).pack(side="right")

    def _save_path(self) -> None:
        """Save the custom path to the user profile."""
        user = self.navigator.get_user()
        if not user:
            return

        name = self._name_entry.get().strip()
        if not name:
            messagebox.showinfo("Name Required", "Please enter a name for your path.")
            return

        if not self._steps:
            messagebox.showinfo("No Exercises", "Add at least one exercise to your path.")
            return

        # Generate a unique ID
        path_id = f"custom_{name.lower().replace(' ', '_')}"
        # Avoid collisions
        base_id = path_id
        counter = 1
        while path_id in user.custom_paths or path_id in TRAINING_PATHS:
            path_id = f"{base_id}_{counter}"
            counter += 1

        # Convert steps to the same format as TRAINING_PATHS
        steps = [(t, l, dict(p)) for t, l, p in self._steps]

        user.custom_paths[path_id] = {
            "name": name,
            "description": f"Custom path with {len(steps)} exercises",
            "steps": steps,
        }
        self.navigator.user_repo.save(user)
        self.navigator.navigate_to("paths")
