"""
Flash perception exercises: numbers, words, and eye-span.
"""
from __future__ import annotations

import random
import tkinter as tk
from tkinter import messagebox
from typing import Callable, Optional

from neural_speed_academy.exercises.base import BaseExercise, ExerciseResult
from neural_speed_academy.theme import COLORS, FONTS
from neural_speed_academy.config import WORD_PAIRS, USER_DATA_CONFIG, FLASH_TIMING


class FlashExercise(BaseExercise):
    """
    Flash perception exercise for numbers, words, and eye-span training.
    Shows content briefly and asks user to recall it.
    """

    def __init__(self, root: tk.Tk, navigator):
        super().__init__(root, navigator)
        
        # Flash widgets - created fresh each exercise to avoid destruction issues
        self.lbl_flash_center: Optional[tk.Label] = None
        self.lbl_flash_left: Optional[tk.Label] = None
        self.lbl_flash_right: Optional[tk.Label] = None
        self.lbl_cross: Optional[tk.Label] = None
        
        # Exercise state
        self.mode: str = ""
        self.rounds_total: int = 0
        self.current_round: int = 0
        self.correct_count: int = 0
        self.target_val: str = ""
        self.level_logic: Optional[Callable] = None
        self.span_config: dict = {}
        self.flash_coords: dict = {}
        self.input_frame: Optional[tk.Frame] = None
        self.word_pairs = WORD_PAIRS

    def _create_flash_widgets(self) -> None:
        """Create flash display widgets."""
        self.lbl_flash_center = tk.Label(
            self.root, text="", font=FONTS["flash"],
            fg=COLORS["fg"], bg=COLORS["bg"]
        )
        self.lbl_flash_left = tk.Label(
            self.root, text="", font=FONTS["flash"],
            fg=COLORS["fg"], bg=COLORS["bg"]
        )
        self.lbl_flash_right = tk.Label(
            self.root, text="", font=FONTS["flash"],
            fg=COLORS["fg"], bg=COLORS["bg"]
        )
        self.lbl_cross = tk.Label(
            self.root, text="+", font=("Arial", 50),
            fg=COLORS["cross"], bg=COLORS["bg"]
        )

    @property
    def name(self) -> str:
        return "Flash Perception"

    def start(self, mode: str, rounds: int, level_func: Callable, span_config: dict = None, **kwargs) -> None:
        """
        Start the flash exercise.
        
        Args:
            mode: "flash_num", "flash_word", or "eyespan"
            rounds: Number of rounds
            level_func: Function that returns digit count for current round
            span_config: For eyespan mode, dict with "mode" and "width"
        """
        self.mode = mode
        self.rounds_total = rounds
        self.current_round = 0
        self.correct_count = 0
        self.level_logic = level_func
        self.span_config = span_config or {}
        
        # Create fresh flash widgets
        self._create_flash_widgets()
        
        self._next_round()

    def _clear_flash_widgets(self) -> None:
        """Hide all flash-related widgets."""
        if self.lbl_flash_center:
            self.lbl_flash_center.place_forget()
        if self.lbl_flash_left:
            self.lbl_flash_left.place_forget()
        if self.lbl_flash_right:
            self.lbl_flash_right.place_forget()
        if self.lbl_cross:
            self.lbl_cross.place_forget()
        if self.input_frame:
            self.input_frame.destroy()
            self.input_frame = None

    def _next_round(self) -> None:
        """Advance to next round or complete exercise."""
        if self.current_round >= self.rounds_total:
            self._complete_exercise()
            return

        self._clear_flash_widgets()
        self.clear()
        
        # Recreate flash widgets after clear destroys them
        self._create_flash_widgets()
        
        self.add_nav_bar()
        self.current_round += 1

        # Counter widget
        cnt_str = f"ROUND: {self.current_round}/{self.rounds_total}   |   CORRECT: {self.correct_count}"
        label = tk.Label(
            self.root, text=cnt_str,
            font=("Segoe UI", 12, "bold"),
            fg=COLORS["accent"], bg=COLORS["bg"]
        )
        label.pack(pady=5)
        self.add_widget(label)

        # Show cross
        self.lbl_cross.config(fg=COLORS["cross"], text="+")
        self.lbl_cross.place(relx=0.5, rely=0.5, anchor="center")

        # Prepare content
        self._prepare_content()

        # Sequence: Cross -> Dots -> Flash
        self.root.after(FLASH_TIMING["cross_duration"], self._show_pre_flash_dots)

    def _prepare_content(self) -> None:
        """Prepare the content to flash based on mode."""
        if self.mode == "flash_num":
            d = self.level_logic(self.current_round)
            self.target_val = str(random.randint(10**(d-1), (10**d)-1))
            self.lbl_flash_center.config(text=self.target_val, fg=COLORS["fg"])
            
        elif self.mode == "flash_word":
            self.target_val = random.choice(random.choice(self.word_pairs))
            self.lbl_flash_center.config(text=self.target_val, fg=COLORS["fg"])
            
        elif self.mode == "eyespan":
            d = self.level_logic(self.current_round)
            low, high = 10**(d-1), (10**d)-1
            n1 = str(random.randint(low, high))
            n2 = str(random.randint(low, high))
            self.target_val = f"{n1} {n2}"
            self.lbl_flash_left.config(text=n1, fg=COLORS["fg"])
            self.lbl_flash_right.config(text=n2, fg=COLORS["fg"])

            w = self.span_config.get("width", 50) / 200.0
            m = self.span_config.get("mode", "h")
            if m == "m":
                m = random.choice(["h", "v"])

            # Clamp positions so labels don't extend past screen edges.
            # Reserve a margin proportional to digit count to account for
            # the label width (anchor="center" means half the label extends
            # in each direction).
            margin = 0.03 * d + 0.02

            if m == "h":
                l_relx = max(margin, 0.5 - w)
                r_relx = min(1.0 - margin, 0.5 + w)
                self.flash_coords = {
                    "l_relx": l_relx, "l_rely": 0.5,
                    "r_relx": r_relx, "r_rely": 0.5
                }
            else:
                l_rely = max(margin, 0.5 - w)
                r_rely = min(1.0 - margin, 0.5 + w)
                self.flash_coords = {
                    "l_relx": 0.5, "l_rely": l_rely,
                    "r_relx": 0.5, "r_rely": r_rely
                }
            self.lbl_flash_left.place_forget()
            self.lbl_flash_right.place_forget()

    def _show_pre_flash_dots(self) -> None:
        """Change cross to dots before flash."""
        self.lbl_cross.config(text="••", fg=COLORS["accent"])
        self.root.after(FLASH_TIMING["dots_duration"], self._do_flash)

    def _do_flash(self) -> None:
        """Flash the content briefly."""
        self.lbl_cross.place_forget()

        # Show content
        if self.mode == "eyespan":
            self.lbl_flash_left.place(
                relx=self.flash_coords["l_relx"],
                rely=self.flash_coords["l_rely"],
                anchor="center"
            )
            self.lbl_flash_right.place(
                relx=self.flash_coords["r_relx"],
                rely=self.flash_coords["r_rely"],
                anchor="center"
            )
        else:
            self.lbl_flash_center.place(relx=0.5, rely=0.5, anchor="center")

        # Force Tkinter to render the widget before starting the hide timer,
        # otherwise the 50ms window can elapse before the label is painted.
        self.root.update_idletasks()
        self.root.after(FLASH_TIMING["flash_duration"], self._hide_flash)

    def _hide_flash(self) -> None:
        """Hide flash content after brief display."""
        if self.mode == "eyespan":
            self.lbl_flash_left.place_forget()
            self.lbl_flash_right.place_forget()
        else:
            self.lbl_flash_center.place_forget()

        self.root.after(FLASH_TIMING["post_flash_delay"], self._show_input)

    def _show_input(self) -> None:
        """Show input field for user response."""
        self.input_frame = tk.Frame(self.root, bg=COLORS["bg"])
        self.input_frame.place(relx=0.5, rely=0.7, anchor="center")

        entry = tk.Entry(
            self.input_frame,
            font=("Segoe UI", 24),
            bg=COLORS["card"],
            fg="white",
            justify="center",
            insertbackground="white"
        )
        entry.pack(pady=10)
        entry.focus_set()
        entry.bind("<Return>", lambda e: self._verify(entry.get()))

        tk.Button(
            self.input_frame,
            text="CHECK",
            command=lambda: self._verify(entry.get()),
            bg=COLORS["accent"],
            fg="#0f172a",
            font=("Segoe UI", 12, "bold")
        ).pack()

    def _verify(self, user_input: str) -> None:
        """Verify user input against target."""
        if user_input.upper().strip() == self.target_val:
            self.correct_count += 1
            self._next_round()
        else:
            self._show_correction()

    def _show_correction(self) -> None:
        """Show the correct answer."""
        if self.input_frame:
            self.input_frame.destroy()
            self.input_frame = None

        # Redisplay content in alert color
        if self.mode == "eyespan":
            self.lbl_flash_left.config(fg=COLORS["alert"])
            self.lbl_flash_right.config(fg=COLORS["alert"])
            self.lbl_flash_left.place(
                relx=self.flash_coords["l_relx"],
                rely=self.flash_coords["l_rely"],
                anchor="center"
            )
            self.lbl_flash_right.place(
                relx=self.flash_coords["r_relx"],
                rely=self.flash_coords["r_rely"],
                anchor="center"
            )
        else:
            self.lbl_flash_center.config(fg=COLORS["alert"])
            self.lbl_flash_center.place(relx=0.5, rely=0.5, anchor="center")

        self.root.update()
        self.root.after(FLASH_TIMING["correction_display"], self._next_round)

    def _complete_exercise(self) -> None:
        """Handle exercise completion."""
        xp_gained = self.correct_count * USER_DATA_CONFIG["xp_per_correct"]
        result = ExerciseResult(
            exercise_name=self.mode.upper(),
            score=self.correct_count,
            total=self.rounds_total,
            xp_gained=xp_gained
        )
        self.complete(result)
        messagebox.showinfo("Done", f"Score: {self.correct_count}/{self.rounds_total}")
        self._clear_flash_widgets()
        self.navigator.to_dashboard()
