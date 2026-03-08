"""
Chunking exercise: flash multi-word phrases to train block reading.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from neural_speed_academy.exercises.base import BaseExercise, ExerciseResult
from neural_speed_academy.theme import COLORS, FONTS
from neural_speed_academy.config import CHUNKING_CONFIG, USER_DATA_CONFIG

SAMPLE_TEXT = (
    "Speed reading is not about skipping words or skimming the surface. "
    "It is about training the brain to process groups of words as single "
    "units of meaning. Just as a skilled musician reads chords rather than "
    "individual notes, a skilled reader perceives phrases rather than "
    "isolated words. This ability, called chunking, leverages the brain's "
    "natural pattern recognition. Research shows that working memory can "
    "hold approximately seven chunks of information at once. By grouping "
    "words into meaningful phrases, you effectively multiply the amount "
    "of text your brain can process in each fixation. The key is practice: "
    "repeated exposure to phrase-level reading gradually rewires the visual "
    "processing pipeline to default to larger units."
)


class ChunkingExercise(BaseExercise):
    """
    Chunking exercise: displays multi-word phrases at configurable speed.
    Trains the brain to read in word groups instead of single words.
    """

    def __init__(self, root: tk.Tk, navigator):
        super().__init__(root, navigator)
        self.chunks: list = []
        self.chunk_idx: int = 0
        self.wpm: int = 250
        self.chunk_size: int = 3
        self.lbl_chunk: tk.Label = None
        self.lbl_progress: tk.Label = None
        self._running: bool = False

    @property
    def name(self) -> str:
        return "Chunking"

    def start(self, **kwargs) -> None:
        """Show the chunking configuration screen."""
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
            command=lambda: self.show_guide("chunking")
        ).place(x=50, y=20)

        content = tk.Frame(container, bg=COLORS["bg"])
        content.pack(expand=True)

        tk.Label(
            content,
            text="CHUNKING CONFIGURATION",
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
        text_input.insert("1.0", SAMPLE_TEXT)

        # Chunk size selector
        tk.Label(
            content,
            text="Words Per Chunk:",
            font=FONTS["slider_label"],
            fg=COLORS["fg"],
            bg=COLORS["bg"]
        ).pack(pady=(10, 0))

        chunk_var = tk.IntVar(value=CHUNKING_CONFIG["default_chunk_size"])
        tk.Scale(
            content,
            variable=chunk_var,
            from_=CHUNKING_CONFIG["min_chunk_size"],
            to=CHUNKING_CONFIG["max_chunk_size"],
            orient="horizontal",
            bg=COLORS["bg"],
            fg=COLORS["text_on_card"],
            length=300,
            highlightthickness=0
        ).pack(pady=5)

        # WPM slider
        tk.Label(
            content,
            text="Display Speed (WPM equivalent):",
            font=FONTS["slider_label"],
            fg=COLORS["fg"],
            bg=COLORS["bg"]
        ).pack(pady=(10, 0))

        wpm_var = tk.IntVar(value=CHUNKING_CONFIG["default_wpm"])
        tk.Scale(
            content,
            variable=wpm_var,
            from_=CHUNKING_CONFIG["min_wpm"],
            to=CHUNKING_CONFIG["max_wpm"],
            orient="horizontal",
            bg=COLORS["bg"],
            fg=COLORS["text_on_card"],
            length=400,
            highlightthickness=0
        ).pack(pady=5)

        # Start button
        btn_frame = tk.Frame(container, bg=COLORS["bg"], pady=20)
        btn_frame.pack(side="bottom", fill="x")

        tk.Button(
            btn_frame,
            text="START CHUNKING",
            command=lambda: self._run_chunking(
                text_input.get("1.0", tk.END),
                chunk_var.get(),
                wpm_var.get()
            ),
            bg=COLORS["success"],
            fg=COLORS["btn_text"],
            font=FONTS["btn_lg"],
            width=30,
            pady=10,
            relief="flat",
        ).pack()

    def _build_chunks(self, text: str, size: int) -> list:
        """Split text into chunks of the given word count."""
        words = text.split()
        return [
            " ".join(words[i:i + size])
            for i in range(0, len(words), size)
        ]

    def _run_chunking(self, text: str, chunk_size: int, wpm: int) -> None:
        """Start the chunking display."""
        self.chunks = self._build_chunks(text, chunk_size)
        if not self.chunks:
            return

        self.chunk_size = chunk_size
        self.wpm = wpm
        self.chunk_idx = 0
        self._running = True
        # Delay per chunk: account for multiple words per chunk
        self._delay = int(60000 * chunk_size / wpm)

        self.clear()
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
            text=f"0% | {chunk_size}-word chunks | {wpm} WPM",
            font=FONTS["counter"],
            fg=COLORS["accent"],
            bg=COLORS["bg"]
        )
        self.lbl_progress.place(relx=0.5, rely=0.1, anchor="center")
        self.add_widget(self.lbl_progress)

        # Chunk display
        self.lbl_chunk = tk.Label(
            self.root,
            text="",
            font=FONTS["pacer"],
            fg=COLORS["fg"],
            bg=COLORS["bg"]
        )
        self.lbl_chunk.place(relx=0.5, rely=0.5, anchor="center")
        self.add_widget(self.lbl_chunk)

        self.root.after(500, self._flash_chunk)

    def _flash_chunk(self) -> None:
        """Display the next chunk."""
        if not self._running:
            return
        if self.chunk_idx >= len(self.chunks):
            self._complete_exercise()
            return

        self.lbl_chunk.config(text=self.chunks[self.chunk_idx])
        self.chunk_idx += 1
        pct = int(self.chunk_idx / len(self.chunks) * 100)
        self.lbl_progress.config(
            text=f"{pct}% | {self.chunk_size}-word chunks | {self.wpm} WPM"
        )
        self.root.after(self._delay, self._flash_chunk)

    def _stop(self) -> None:
        """Stop and return to dashboard."""
        self._running = False
        self.navigator.finish_exercise()

    def _complete_exercise(self) -> None:
        """Handle exercise completion."""
        self._running = False
        total_words = sum(len(c.split()) for c in self.chunks)
        xp = total_words // 10
        result = ExerciseResult(
            exercise_name="CHUNKING",
            score=total_words,
            total=total_words,
            xp_gained=xp
        )
        self.complete(result)
        messagebox.showinfo(
            "Done",
            f"Read {total_words} words in {len(self.chunks)} chunks "
            f"at {self.wpm} WPM\nXP: +{xp}"
        )
        self.navigator.finish_exercise()
