"""
Pacer exercise for guided reading with word highlighting.
"""

import tkinter as tk

from neural_speed_academy.exercises.base import BaseExercise
from neural_speed_academy.theme import COLORS, FONTS
from neural_speed_academy.config import PACER_CONFIG


class PacerExercise(BaseExercise):
    """
    Pacer reading exercise.
    Highlights words at a configurable WPM rate to train reading speed.
    """

    def __init__(self, root: tk.Tk, navigator):
        super().__init__(root, navigator)
        self.pacer_state: dict = {}
        self.lbl_progress: tk.Label = None

    @property
    def name(self) -> str:
        return "Pacer"

    def start(self, **kwargs) -> None:
        """Show the pacer configuration screen."""
        self.clear()
        self.add_nav_bar()

        container = tk.Frame(self.root, bg=COLORS["bg"])
        container.pack(expand=True, fill="both")
        self.add_widget(container)

        # Guide button
        guide_btn = tk.Button(
            container,
            text="📘 GUIDE",
            bg=COLORS["accent"],
            fg="#0f172a",
            command=lambda: self.show_guide("pacer")
        )
        guide_btn.place(x=50, y=20)

        # Content frame
        content = tk.Frame(container, bg=COLORS["bg"])
        content.pack(expand=True)

        tk.Label(
            content,
            text="PACER CONFIGURATION",
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
            font=("Georgia", 12),
            bg=COLORS["card"],
            fg="white",
            insertbackground="white",
            bd=0
        )
        text_input.pack()
        text_input.insert("1.0", "Paste your reading material here...")

        # WPM slider
        tk.Label(
            content,
            text="Target Speed (WPM):",
            font=("Segoe UI", 12),
            fg=COLORS["fg"],
            bg=COLORS["bg"]
        ).pack(pady=(10, 0))

        wpm_var = tk.IntVar(value=PACER_CONFIG["default_wpm"])
        tk.Scale(
            content,
            variable=wpm_var,
            from_=PACER_CONFIG["min_wpm"],
            to=PACER_CONFIG["max_wpm"],
            orient="horizontal",
            bg=COLORS["bg"],
            fg="white",
            length=400,
            highlightthickness=0
        ).pack(pady=5)

        # Start button
        btn_frame = tk.Frame(container, bg=COLORS["bg"], pady=20)
        btn_frame.pack(side="bottom", fill="x")

        tk.Button(
            btn_frame,
            text="START READING",
            command=lambda: self._run_pacer(text_input.get("1.0", tk.END), wpm_var.get()),
            bg=COLORS["success"],
            fg="#0f172a",
            font=("Segoe UI", 16, "bold"),
            width=30,
            pady=10,
            relief="flat",
            cursor="hand2"
        ).pack()

    def _run_pacer(self, text: str, wpm: int) -> None:
        """Start the pacing animation."""
        words = text.split()
        self.clear()

        if not words:
            return

        # Exit button
        exit_btn = tk.Button(
            self.root,
            text="✖",
            font=("Arial", 14),
            bg=COLORS["alert"],
            fg="white",
            command=self.navigator.to_dashboard,
            bd=0
        )
        exit_btn.place(relx=0.95, rely=0.05, anchor="center")
        self.add_widget(exit_btn)

        # Progress label
        self.lbl_progress = tk.Label(
            self.root,
            text="0%",
            font=("Segoe UI", 14, "bold"),
            fg=COLORS["fg"],
            bg=COLORS["bg"]
        )
        self.lbl_progress.place(relx=0.5, rely=0.05, anchor="center")
        self.add_widget(self.lbl_progress)

        # Calculate delay from WPM
        delay = int(60000 / wpm)

        # Text widget
        text_widget = tk.Text(
            self.root,
            font=FONTS["pacer"],
            bg="#e2e8f0",
            fg="#0f172a",
            wrap="word",
            padx=100,
            pady=100
        )
        text_widget.place(relx=0, rely=0.1, relwidth=1, relheight=0.9)
        text_widget.insert("1.0", " ".join(words))
        text_widget.config(state="disabled")
        text_widget.tag_config("h", background=COLORS["highlight"])
        self.add_widget(text_widget)

        # Bring controls to front
        exit_btn.lift()
        self.lbl_progress.lift()

        # Initialize state
        self.pacer_state = {
            "idx": 0,
            "words": words,
            "delay": delay,
            "widget": text_widget
        }

        self._pacer_step()

    def _pacer_step(self) -> None:
        """Advance to next word in pacer."""
        idx = self.pacer_state["idx"]
        words = self.pacer_state["words"]
        text_widget = self.pacer_state["widget"]

        try:
            if not text_widget.winfo_exists():
                return
        except tk.TclError:
            return

        if idx < len(words):
            text_widget.config(state="normal")
            text_widget.tag_remove("h", "1.0", "end")

            # Find word position
            start = "1.0"
            for _ in range(idx):
                start = text_widget.search(" ", start, stopindex="end") + "+1c"
            end = text_widget.search(" ", start, stopindex="end") or "end"

            text_widget.tag_add("h", start, end)
            text_widget.see(start)
            text_widget.config(state="disabled")

            # Update progress
            progress = int((idx / len(words)) * 100)
            self.lbl_progress.config(text=f"PROGRESS: {progress}%")

            self.pacer_state["idx"] += 1
            self.root.after(self.pacer_state["delay"], self._pacer_step)
        else:
            self._quiz_phase()

    def _quiz_phase(self) -> None:
        """Show quiz/summary phase after reading."""
        self.clear()
        self.add_nav_bar()

        tk.Label(
            self.root,
            text="Summarize what you read:",
            font=FONTS["header"],
            bg=COLORS["bg"],
            fg="white"
        ).pack(pady=20)

        summary_text = tk.Text(self.root, height=5)
        summary_text.pack()
        self.add_widget(summary_text)

        tk.Button(
            self.root,
            text="Done",
            command=self.navigator.to_dashboard,
            bg=COLORS["accent"],
            fg="#0f172a",
            font=("Segoe UI", 12, "bold"),
            width=15
        ).pack()
