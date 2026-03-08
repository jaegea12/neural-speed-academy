"""
Training path selection and execution screens.
"""
from __future__ import annotations

import random
import tkinter as tk
from tkinter import messagebox
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

        for i, (path_id, path_data) in enumerate(TRAINING_PATHS.items()):
            row = i // 3
            col = i % 3
            self._create_path_card(cards_frame, path_id, path_data, user, row, col)

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

        # Step count
        step_count = len(path_data["steps"])
        tk.Label(
            card,
            text=f"{step_count} exercises",
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
            self.navigator.navigate_to("login")
            return

        pp = user.path_progress.get(path_id)
        if pp and pp.completed:
            # Restart
            pp.current_step = 0
            pp.completed = False
        elif not pp:
            pp = PathProgress(path_id=path_id)
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
        path_data = TRAINING_PATHS.get(path_id)
        if not path_data:
            self.navigator.to_dashboard()
            return

        pp = user.path_progress.get(path_id)
        if not pp:
            pp = PathProgress(path_id=path_id)
            user.path_progress[path_id] = pp

        steps = path_data["steps"]
        current = pp.current_step

        if current >= len(steps):
            pp.completed = True
            user.active_path = None
            self.navigator.user_repo.save(user)
            messagebox.showinfo(
                "Path Complete!",
                f"You completed {path_data['name']}!\n"
                f"All {len(steps)} exercises done."
            )
            self.navigator.to_dashboard()
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

        # Step list
        list_frame = tk.Frame(container, bg=COLORS["bg"])
        list_frame.pack(pady=10)

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

        # Skip button
        tk.Button(
            container,
            text="SKIP THIS STEP",
            font=FONTS["btn_sm"],
            bg=COLORS["card"],
            fg=COLORS["fg"],
            relief="flat",
            cursor="hand2",
            command=lambda: self._advance_step(path_id, current),
        ).pack()

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
        elif ex_type == "rsvp":
            app.rsvp_exercise.start()
        elif ex_type == "chunking":
            app.chunking_exercise.start()

    def _advance_step(self, path_id: str, step_idx: int) -> None:
        """Advance to the next step and refresh the path session screen."""
        user = self.navigator.get_user()
        if not user:
            return
        pp = user.path_progress.get(path_id)
        if pp and pp.current_step == step_idx:
            pp.current_step += 1
            path_data = TRAINING_PATHS.get(path_id, {})
            if pp.current_step >= len(path_data.get("steps", [])):
                pp.completed = True
                user.active_path = None
            self.navigator.user_repo.save(user)
        self.navigator.navigate_to("path_session")
