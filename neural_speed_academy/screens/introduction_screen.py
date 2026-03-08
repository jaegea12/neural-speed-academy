"""
Introduction screen with speed reading science and training overview.
"""
from __future__ import annotations

import tkinter as tk

from neural_speed_academy.screens.base import BaseScreen
from neural_speed_academy.theme import COLORS, FONTS


INTRO_TEXT = (
    "WHAT IS SPEED READING?\n\n"
    "Speed reading is not skimming. It is the systematic training of visual "
    "and cognitive skills that remove inefficiencies from the reading process. "
    "An average reader processes 200-250 words per minute (WPM). Trained "
    "readers consistently reach 400-600 WPM with equal or better comprehension.\n\n"

    "THE FOUR BOTTLENECKS\n\n"
    "1. TOO MANY FIXATIONS — Your eyes don't glide across text. They jump "
    "(saccade) and pause (fixate) 3-4 times per line. Each fixation processes "
    "only 1-2 words. Training: Eye-Span and Chunking exercises widen your "
    "perceptual span so each fixation covers more words.\n\n"
    "2. REGRESSION — 10-15% of eye movements go backward to re-read text "
    "you already passed. This is the single largest waste of reading time. "
    "Training: Pacer exercises suppress regression by forcing forward momentum.\n\n"
    "3. SUBVOCALIZATION — The inner voice that 'reads aloud' in your head "
    "limits you to speaking speed (~150 WPM). Training: Flash and RSVP "
    "exercises present text faster than speech, forcing direct visual-to-meaning "
    "processing.\n\n"
    "4. NARROW ATTENTION — Untrained readers focus on one word at a time. "
    "Training: Schulte grids and Eye-Span exercises expand peripheral awareness "
    "so you process more of the visual field simultaneously.\n\n"

    "THE EXERCISES\n\n"
    "• Flash Perception — Trains iconic memory and rapid digit/word recognition\n"
    "• Eye-Span — Widens the perceptual span for fewer fixations per line\n"
    "• Schulte Grid — Expands peripheral awareness without moving the eyes\n"
    "• Eye Priming — Warms up extraocular muscles before training\n"
    "• Pacer — Guided reading that eliminates regression\n"
    "• RSVP — Single-word flash that breaks the subvocalization barrier\n"
    "• Chunking — Phrase-level reading for block processing\n\n"

    "REALISTIC EXPECTATIONS\n\n"
    "Research supports that consistent training (15-20 min/day, 4-5 days/week) "
    "produces measurable gains within 2-4 weeks. Most people can double their "
    "reading speed while maintaining comprehension. Claims of 1000+ WPM with "
    "full comprehension are not supported by peer-reviewed research."
)


class IntroductionScreen(BaseScreen):
    """Introduction screen with speed reading science overview."""

    def build(self, **kwargs) -> None:
        """Build the introduction UI."""
        self.root.configure(bg=COLORS["bg"])
        self.add_nav_bar()

        # Scrollable content
        container = tk.Frame(self.root, bg=COLORS["bg"])
        container.pack(fill="both", expand=True)
        self.add_widget(container)

        canvas = tk.Canvas(container, bg=COLORS["bg"], highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=COLORS["bg"])

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Mouse wheel scrolling — unbind on canvas destroy to avoid leaks
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.root.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind("<Destroy>", lambda e: self.root.unbind_all("<MouseWheel>"))

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Title
        tk.Label(
            scroll_frame,
            text="INTRODUCTION TO SPEED READING",
            font=FONTS["header"],
            fg=COLORS["accent"],
            bg=COLORS["bg"],
        ).pack(pady=(20, 10), padx=40, anchor="w")

        # Content
        tk.Label(
            scroll_frame,
            text=INTRO_TEXT,
            font=FONTS["body"],
            fg=COLORS["fg"],
            bg=COLORS["bg"],
            wraplength=800,
            justify="left",
        ).pack(padx=40, pady=(0, 30), anchor="w")

        # Back button
        tk.Button(
            scroll_frame,
            text="← BACK TO MENU",
            font=FONTS["btn_bold"],
            bg=COLORS["accent"],
            fg=COLORS["btn_text"],
            relief="flat",
            width=20,
            pady=8,
            cursor="hand2",
            command=lambda: self.navigator.navigate_to("main_menu"),
        ).pack(pady=(0, 40))
