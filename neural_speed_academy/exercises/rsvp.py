"""
RSVP (Rapid Serial Visual Presentation) exercise.
Flashes words from a passage one at a time at configurable WPM.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from neural_speed_academy.exercises.base import BaseExercise, ExerciseResult
from neural_speed_academy.theme import COLORS, FONTS, theme_manager
from neural_speed_academy.config import RSVP_CONFIG, USER_DATA_CONFIG


class RsvpExercise(BaseExercise):
    """
    RSVP exercise: displays words one at a time at a target WPM.
    Trains rapid word processing and reduces subvocalization.
    """

    def __init__(self, root: tk.Tk, navigator):
        super().__init__(root, navigator)
        self.words: list = []
        self.word_idx: int = 0
        self.wpm: int = 300
        self.lbl_word: tk.Label = None
        self.lbl_progress: tk.Label = None
        self._running: bool = False

    @property
    def name(self) -> str:
        return "RSVP"

    def start(self, **kwargs) -> None:
        """Show the RSVP configuration screen."""
        self.clear()
        self.add_nav_bar()

        container = tk.Frame(self.root, bg=COLORS["bg"])
        container.pack(expand=True, fill="both")
        self.add_widget(container)

        # Guide button
        tk.Button(
            container,
            text="GUIDE",
            bg=COLORS["accent"],
            fg=COLORS["btn_text"],
            cursor="hand2",
            command=lambda: self.show_guide("rsvp"),
        ).place(x=50, y=20)

        content = tk.Frame(container, bg=COLORS["bg"])
        content.pack(expand=True)

        tk.Label(
            content,
            text="RSVP CONFIGURATION",
            font=FONTS["header"],
            fg=COLORS["accent"],
            bg=COLORS["bg"]
        ).pack(pady=(0, 10))

        # Text input
        text_frame = tk.Frame(content, bg=COLORS["card"], padx=2, pady=2)
        text_frame.pack(pady=5)

        text_input = tk.Text(
            text_frame,
            height=6,
            width=60,
            font=FONTS["pacer_text"],
            bg=COLORS["card"],
            fg=COLORS["text_on_card"],
            insertbackground=COLORS["text_on_card"],
            bd=0
        )
        text_input.pack()
        text_input.insert("1.0", theme_manager.training_text)

        # WPM slider
        tk.Label(
            content,
            text="Words Per Minute:",
            font=FONTS["slider_label"],
            fg=COLORS["fg"],
            bg=COLORS["bg"]
        ).pack(pady=(10, 0))

        wpm_var = tk.IntVar(value=RSVP_CONFIG["default_wpm"])
        tk.Scale(
            content,
            variable=wpm_var,
            from_=RSVP_CONFIG["min_wpm"],
            to=RSVP_CONFIG["max_wpm"],
            orient="horizontal",
            bg=COLORS["bg"],
            fg=COLORS["text_on_card"],
            length=400,
            highlightthickness=0
        ).pack(pady=5)

        # Start button
        btn_frame = tk.Frame(container, bg=COLORS["bg"], pady=20)
        btn_frame.pack(side="bottom", fill="x")

        def _start():
            self._run_rsvp(text_input.get("1.0", tk.END), wpm_var.get())

        tk.Button(
            btn_frame,
            text="START RSVP",
            command=_start,
            bg=COLORS["success"],
            fg=COLORS["btn_text"],
            font=FONTS["btn_lg"],
            width=30,
            pady=10,
            relief="flat",
            cursor="hand2",
        ).pack()

        # Ctrl+Enter to start from text area
        text_input.bind("<Control-Return>", lambda e: _start())

    def _run_rsvp(self, text: str, wpm: int) -> None:
        """Start the RSVP display."""
        self.words = text.split()
        if not self.words:
            messagebox.showinfo("No Text", "Please enter some text before starting.")
            return

        self.wpm = wpm
        self.word_idx = 0
        delay = int(60000 / wpm)

        self.clear()
        self._running = True
        self.root.configure(bg=COLORS["bg"])

        # Exit button
        exit_btn = tk.Button(
            self.root,
            text="✖",
            font=FONTS["exit_btn"],
            bg=COLORS["alert"],
            fg=COLORS["text_on_card"],
            command=self._stop,
            bd=0
        )
        exit_btn.place(relx=0.95, rely=0.05, anchor="center")
        self.add_widget(exit_btn)

        # Progress
        self.lbl_progress = tk.Label(
            self.root,
            text=f"0% | {wpm} WPM",
            font=FONTS["counter"],
            fg=COLORS["accent"],
            bg=COLORS["bg"]
        )
        self.lbl_progress.place(relx=0.5, rely=0.1, anchor="center")
        self.add_widget(self.lbl_progress)

        # Word display
        self.lbl_word = tk.Label(
            self.root,
            text="",
            font=FONTS["rsvp"],
            fg=COLORS["fg"],
            bg=COLORS["bg"]
        )
        self.lbl_word.place(relx=0.5, rely=0.5, anchor="center")
        self.add_widget(self.lbl_word)

        self._delay = delay
        self.root.after(500, self._flash_word)

    def _flash_word(self) -> None:
        """Display the next word."""
        if not self._running:
            return
        if self.word_idx >= len(self.words):
            self._complete_exercise()
            return

        self.lbl_word.config(text=self.words[self.word_idx])
        self.word_idx += 1
        pct = int(self.word_idx / len(self.words) * 100)
        self.lbl_progress.config(text=f"{pct}% | {self.wpm} WPM")
        self.root.after(self._delay, self._flash_word)

    def _stop(self) -> None:
        """Stop the exercise and return to dashboard."""
        self._running = False
        self.navigator.finish_exercise()

    def _complete_exercise(self) -> None:
        """Handle exercise completion."""
        self._running = False
        word_count = len(self.words)
        xp = word_count // 10
        result = ExerciseResult(
            exercise_name="RSVP",
            score=word_count,
            total=word_count,
            xp_gained=xp
        )
        is_pb = self.complete(result)
        self.show_result_screen(result, is_personal_best=is_pb,
                                details=f"Read {word_count} words at {self.wpm} WPM")
