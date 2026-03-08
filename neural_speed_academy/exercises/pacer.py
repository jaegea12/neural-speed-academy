"""
Pacer exercise for guided reading with configurable highlight modes.
Supports word, chunk, line, and multi-line pacing with a keyword quiz.
"""
from __future__ import annotations

import re
import tkinter as tk

from neural_speed_academy.exercises.base import BaseExercise, ExerciseResult
from neural_speed_academy.theme import COLORS, FONTS, theme_manager
from neural_speed_academy.config import PACER_CONFIG, USER_DATA_CONFIG

# Common words excluded from keyword extraction
_STOP_WORDS = frozenset(
    "the a an and or but in on at to for of is it that this with from by as "
    "are was were be been has have had do does did not no nor so if then than "
    "can will would could should may might shall its you your we our they them "
    "he she his her my me us who what when where how all each every some any "
    "also just about more most very much many such only other into over after "
    "before between through during without again further once here there which "
    "these those being both same own too up out off down".split()
)

# Page dimensions — DIN A4 proportions (1:1.414)
PAGE_WIDTH = 620
PAGE_PAD_X = 60
PAGE_PAD_Y = 50


def _extract_keywords(text: str, max_keywords: int = 8) -> list[str]:
    """Extract significant words from text for quiz scoring."""
    words = re.findall(r"[a-zA-Z]+", text.lower())
    freq: dict[str, int] = {}
    for w in words:
        if len(w) >= 4 and w not in _STOP_WORDS:
            freq[w] = freq.get(w, 0) + 1
    ranked = sorted(freq, key=lambda w: freq[w], reverse=True)
    return ranked[:max_keywords]


class PacerExercise(BaseExercise):
    """
    Pacer reading exercise with multiple highlight modes.
    Highlights text at a configurable WPM rate, then quizzes comprehension.
    """

    MODES = {
        "word": "Single Word",
        "chunk": "Chunk (2-3 words)",
        "line": "Full Line",
        "multi_line": "Multi-Line (2-3)",
        "z_pattern": "Z-Pattern",
    }

    def __init__(self, root: tk.Tk, navigator):
        super().__init__(root, navigator)
        self.pacer_state: dict = {}
        self.lbl_progress: tk.Label | None = None
        self._source_text: str = ""

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

        tk.Button(
            container, text="GUIDE",
            bg=COLORS["accent"], fg=COLORS["btn_text"],
            cursor="hand2",
            command=lambda: self.show_guide("pacer"),
        ).place(x=50, y=20)

        content = tk.Frame(container, bg=COLORS["bg"])
        content.pack(expand=True)

        tk.Label(
            content, text="PACER CONFIGURATION",
            font=FONTS["header"], fg=COLORS["accent"], bg=COLORS["bg"],
        ).pack(pady=(0, 10))

        # Text input
        text_frame = tk.Frame(content, bg=COLORS["card"], padx=2, pady=2)
        text_frame.pack(pady=5)

        text_input = tk.Text(
            text_frame, height=6, width=60,
            font=FONTS["pacer_text"],
            bg=COLORS["card"], fg=COLORS["text_on_card"],
            insertbackground=COLORS["text_on_card"],
            wrap="word", bd=0,
        )
        text_input.pack()
        text_input.insert("1.0", theme_manager.training_text)

        # WPM slider
        tk.Label(
            content, text="Target Speed (WPM):",
            font=FONTS["slider_label"], fg=COLORS["fg"], bg=COLORS["bg"],
        ).pack(pady=(10, 0))

        wpm_var = tk.IntVar(value=PACER_CONFIG["default_wpm"])
        tk.Scale(
            content, variable=wpm_var,
            from_=PACER_CONFIG["min_wpm"], to=PACER_CONFIG["max_wpm"],
            orient="horizontal", bg=COLORS["bg"], fg=COLORS["text_on_card"],
            length=400, highlightthickness=0,
        ).pack(pady=5)

        # Highlight mode selector
        tk.Label(
            content, text="Highlight Mode:",
            font=FONTS["slider_label"], fg=COLORS["fg"], bg=COLORS["bg"],
        ).pack(pady=(10, 0))

        mode_var = tk.StringVar(value="word")
        mode_frame = tk.Frame(content, bg=COLORS["bg"])
        mode_frame.pack(pady=5)

        # Multi-line count selector (shown/hidden based on mode)
        ml_frame = tk.Frame(content, bg=COLORS["bg"])
        ml_label = tk.Label(
            ml_frame, text="Lines per step:",
            font=FONTS["slider_label"], fg=COLORS["fg"], bg=COLORS["bg"],
        )
        ml_label.pack(side="left", padx=(0, 10))
        ml_var = tk.IntVar(value=2)
        ml_scale = tk.Scale(
            ml_frame, variable=ml_var, from_=2, to=5,
            orient="horizontal", bg=COLORS["bg"], fg=COLORS["text_on_card"],
            length=200, highlightthickness=0,
        )
        ml_scale.pack(side="left")

        def _on_mode_change(*_args):
            if mode_var.get() in ("multi_line", "z_pattern"):
                ml_frame.pack(pady=5)
            else:
                ml_frame.pack_forget()

        mode_var.trace_add("write", _on_mode_change)

        for key, label in self.MODES.items():
            tk.Radiobutton(
                mode_frame, text=label, variable=mode_var, value=key,
                font=FONTS["btn"], fg=COLORS["fg"], bg=COLORS["bg"],
                selectcolor=COLORS["card"],
                activebackground=COLORS["bg"], activeforeground=COLORS["fg"],
                indicatoron=True, anchor="w",
            ).pack(side="left", padx=8)

        # Start button
        btn_frame = tk.Frame(container, bg=COLORS["bg"], pady=20)
        btn_frame.pack(side="bottom", fill="x")

        tk.Button(
            btn_frame, text="START READING",
            command=lambda: self._run_pacer(
                text_input.get("1.0", tk.END), wpm_var.get(),
                mode_var.get(), ml_var.get(),
            ),
            bg=COLORS["success"], fg=COLORS["btn_text"],
            font=FONTS["btn_lg"], width=30, pady=10,
            relief="flat", cursor="hand2",
        ).pack()

    # ── Pacer execution ────────────────────────────────────────

    def _run_pacer(self, text: str, wpm: int, mode: str,
                   n_lines: int = 2) -> None:
        """Start the pacing animation."""
        words = text.split()
        if not words:
            return

        self._source_text = text
        self.clear()

        # Exit button
        exit_btn = tk.Button(
            self.root, text="✖",
            font=FONTS["exit_btn"],
            bg=COLORS["alert"], fg=COLORS["text_on_card"],
            command=self.navigator.finish_exercise, bd=0,
        )
        exit_btn.place(relx=0.95, rely=0.05, anchor="center")
        self.add_widget(exit_btn)

        # Progress label
        self.lbl_progress = tk.Label(
            self.root, text="0%",
            font=FONTS["section_header"],
            fg=COLORS["fg"], bg=COLORS["bg"],
        )
        self.lbl_progress.place(relx=0.5, rely=0.03, anchor="center")
        self.add_widget(self.lbl_progress)

        # Mode label
        mode_text = self.MODES.get(mode, mode)
        if mode == "multi_line":
            mode_text = f"Multi-Line ({n_lines} lines)"
        mode_label = tk.Label(
            self.root, text=mode_text,
            font=FONTS["btn_sm"], fg=COLORS["muted"], bg=COLORS["bg"],
        )
        mode_label.place(relx=0.5, rely=0.065, anchor="center")
        self.add_widget(mode_label)

        # Book-page container — centered, constrained width
        page_frame = tk.Frame(
            self.root, bg=COLORS["reader_bg"],
            width=PAGE_WIDTH, highlightthickness=1,
            highlightbackground=COLORS["muted"],
        )
        page_frame.place(
            relx=0.5, rely=0.54, anchor="center",
            width=PAGE_WIDTH, relheight=0.88,
        )
        page_frame.pack_propagate(False)
        self.add_widget(page_frame)

        text_widget = tk.Text(
            page_frame,
            font=FONTS["pacer"],
            bg=COLORS["reader_bg"], fg=COLORS["reader_fg"],
            wrap="word",
            padx=PAGE_PAD_X, pady=PAGE_PAD_Y,
            relief="flat", cursor="arrow",
            spacing1=4, spacing3=4,
        )
        text_widget.pack(fill="both", expand=True)
        text_widget.insert("1.0", " ".join(words))
        text_widget.config(state="disabled")

        # Highlight tag
        text_widget.tag_config("hl", background=COLORS["highlight"])

        # Bring controls to front
        exit_btn.lift()
        self.lbl_progress.lift()
        mode_label.lift()

        # Build step units based on mode
        steps = self._build_steps(text_widget, words, mode, n_lines)

        # WPM applies to words; scale delay by words-per-step
        avg_words_per_step = len(words) / max(len(steps), 1)
        delay = int(60000 / wpm * avg_words_per_step)

        self.pacer_state = {
            "step_idx": 0,
            "steps": steps,
            "delay": delay,
            "widget": text_widget,
            "total_words": len(words),
            "mode": mode,
            "n_lines": n_lines,
        }

        self._pacer_step()

    def _build_steps(
        self, widget: tk.Text, words: list[str], mode: str,
        n_lines: int = 2,
    ) -> list[tuple[str, str]]:
        """Build (start_index, end_index) pairs for each highlight step."""
        if mode == "word":
            return self._steps_by_word(words)
        elif mode == "chunk":
            return self._steps_by_chunk(words, chunk_size=3)
        elif mode == "line":
            display_lines = self._get_display_lines(widget)
            return display_lines if display_lines else [("1.0", "end")]
        elif mode == "multi_line":
            return self._steps_by_multi_line(widget, n_lines=n_lines)
        elif mode == "z_pattern":
            return self._steps_z_pattern(widget, words, n_lines)
        return self._steps_by_word(words)

    @staticmethod
    def _steps_by_word(words: list[str]) -> list[tuple[str, str]]:
        """One step per word."""
        steps = []
        pos = 0
        for w in words:
            start = f"1.0 + {pos}c"
            end = f"1.0 + {pos + len(w)}c"
            steps.append((start, end))
            pos += len(w) + 1
        return steps

    @staticmethod
    def _steps_by_chunk(
        words: list[str], chunk_size: int = 3,
    ) -> list[tuple[str, str]]:
        """One step per N-word chunk."""
        steps = []
        pos = 0
        for i in range(0, len(words), chunk_size):
            chunk = words[i:i + chunk_size]
            chunk_text = " ".join(chunk)
            start = f"1.0 + {pos}c"
            end = f"1.0 + {pos + len(chunk_text)}c"
            steps.append((start, end))
            pos += len(chunk_text) + 1
        return steps

    @staticmethod
    def _get_display_lines(widget: tk.Text) -> list[tuple[str, str]]:
        """Get display line boundaries using Tk display line indices.

        Uses 'display linestart' and 'display lineend' to handle
        word-wrapped text correctly.
        """
        widget.update_idletasks()
        lines = []
        idx = "1.0"
        end_idx = widget.index("end - 1c")
        while widget.compare(idx, "<=", end_idx):
            dl_start = widget.index(f"{idx} display linestart")
            dl_end = widget.index(f"{idx} display lineend")
            if not lines or widget.compare(dl_start, ">", lines[-1][0]):
                lines.append((dl_start, dl_end))
            # Move to next display line
            next_idx = widget.index(f"{dl_end} + 1 display char")
            if widget.compare(next_idx, "<=", idx):
                break
            idx = next_idx
        return lines

    @staticmethod
    def _steps_by_multi_line(
        widget: tk.Text, n_lines: int = 2,
    ) -> list[list[tuple[str, str]]]:
        """Chunk-sweep across groups of N display lines.

        Each step is a list of (start, end) ranges — one per line in
        the group at the same horizontal column position. This creates
        a vertical highlight band that sweeps left-to-right.
        """
        lines = PacerExercise._get_display_lines(widget)
        if not lines:
            return [[("1.0", "end")]]

        steps: list[list[tuple[str, str]]] = []
        chunk_size = 3

        for i in range(0, len(lines), n_lines):
            group = lines[i:i + n_lines]

            # Get words per line in this group
            line_contents = []
            for dl_start, dl_end in group:
                text = widget.get(dl_start, dl_end)
                line_contents.append((dl_start, dl_end, text, text.split()))

            # Use the first line to determine chunk positions
            first_start, first_end, first_text, first_words = line_contents[0]
            if not first_words:
                steps.append([(group[0][0], group[-1][1])])
                continue

            char_offset = 0
            for ci in range(0, len(first_words), chunk_size):
                chunk = first_words[ci:ci + chunk_size]
                chunk_text = " ".join(chunk)
                pos = first_text.find(chunk_text, char_offset)
                if pos < 0:
                    continue

                # Build ranges: highlight same column band on each line
                ranges = []
                for dl_start, dl_end, lt, lw in line_contents:
                    line_len = len(lt)
                    # Clamp to line length
                    s = min(pos, line_len)
                    e = min(pos + len(chunk_text), line_len)
                    if s < e:
                        ranges.append((
                            f"{dl_start} + {s}c",
                            f"{dl_start} + {e}c",
                        ))
                    else:
                        # Line is shorter, highlight what's there
                        ranges.append((dl_start, dl_end))

                if ranges:
                    steps.append(ranges)
                char_offset = pos + len(chunk_text)

        return steps if steps else [[("1.0", "end")]]

    @staticmethod
    def _steps_z_pattern(
        widget: tk.Text, words: list[str], n_lines: int = 2,
    ) -> list:
        """Z-pattern across groups of N display lines.

        For each N-line group, produces 3 steps that sweep
        left → center → right. Each step highlights the same
        horizontal third across all lines in the group, creating
        a vertical band that traces a Z path down the page.
        """
        lines = PacerExercise._get_display_lines(widget)
        if not lines:
            return [("1.0", "end")]

        steps: list = []
        for i in range(0, len(lines), n_lines):
            group = lines[i:i + n_lines]

            # Get column extents from the first line in the group
            dl_start, dl_end = group[0]
            start_int = int(widget.index(dl_start).split(".")[1])
            end_int = int(widget.index(dl_end).split(".")[1])
            span = end_int - start_int
            if span <= 0:
                steps.append([(dl_start, dl_end)])
                continue

            seg = max(span // 3, 1)

            # 3 sweeps: left, center, right
            for s in range(3):
                s_start_col = start_int + s * seg
                s_end_col = start_int + (s + 1) * seg if s < 2 else end_int

                ranges = []
                for g_start, g_end in group:
                    row = widget.index(g_start).split(".")[0]
                    line_end_col = int(widget.index(g_end).split(".")[1])
                    # Clamp to actual line length
                    cs = min(s_start_col, line_end_col)
                    ce = min(s_end_col, line_end_col)
                    if cs < ce:
                        ranges.append((f"{row}.{cs}", f"{row}.{ce}"))
                if ranges:
                    steps.append(ranges)

        return steps

    def _pacer_step(self) -> None:
        """Advance to next highlight step."""
        state = self.pacer_state
        widget = state["widget"]

        try:
            if not widget.winfo_exists():
                return
        except tk.TclError:
            return

        steps = state["steps"]
        idx = state["step_idx"]

        if idx < len(steps):
            step = steps[idx]

            widget.config(state="normal")
            widget.tag_remove("hl", "1.0", "end")

            # Step is either a (start, end) tuple or a list of ranges
            if isinstance(step, list):
                for start, end in step:
                    widget.tag_add("hl", start, end)
                see_target = step[0][0]
            else:
                start, end = step
                widget.tag_add("hl", start, end)
                see_target = start

            widget.see(see_target)
            widget.config(state="disabled")

            pct = int(100 * idx / len(steps))
            self.lbl_progress.config(text=f"PROGRESS: {pct}%")

            state["step_idx"] += 1
            self.root.after(state["delay"], self._pacer_step)
        else:
            self._quiz_phase()

    # ── Quiz phase ─────────────────────────────────────────────

    def _quiz_phase(self) -> None:
        """Keyword-based comprehension quiz after reading."""
        self.clear()
        self.add_nav_bar()

        self._keywords = _extract_keywords(self._source_text)

        container = tk.Frame(self.root, bg=COLORS["bg"])
        container.pack(expand=True)
        self.add_widget(container)

        tk.Label(
            container, text="COMPREHENSION CHECK",
            font=FONTS["header"], fg=COLORS["accent"], bg=COLORS["bg"],
        ).pack(pady=(0, 10))

        tk.Label(
            container,
            text="Summarize what you just read in your own words.",
            font=FONTS["body"], fg=COLORS["fg"], bg=COLORS["bg"],
        ).pack(pady=(0, 15))

        text_frame = tk.Frame(container, bg=COLORS["card"], padx=2, pady=2)
        text_frame.pack(pady=5)

        self._quiz_input = tk.Text(
            text_frame, height=6, width=60,
            font=FONTS["pacer_text"],
            bg=COLORS["card"], fg=COLORS["text_on_card"],
            insertbackground=COLORS["text_on_card"],
            wrap="word", bd=0,
        )
        self._quiz_input.pack()
        self._quiz_input.focus_set()

        tk.Button(
            container, text="CHECK",
            command=self._score_quiz,
            bg=COLORS["accent"], fg=COLORS["btn_text"],
            font=FONTS["btn_bold"], width=20, pady=8,
            relief="flat", cursor="hand2",
        ).pack(pady=15)

    def _score_quiz(self) -> None:
        """Score the summary against extracted keywords."""
        summary = self._quiz_input.get("1.0", "end").lower()
        summary_words = set(re.findall(r"[a-zA-Z]+", summary))

        matched = [kw for kw in self._keywords if kw in summary_words]
        score = len(matched)
        total = len(self._keywords)

        xp = score * USER_DATA_CONFIG["xp_per_correct"]
        result = ExerciseResult(
            exercise_name="PACER",
            score=score,
            total=total,
            xp_gained=xp,
        )
        self.complete(result)

        # Show results
        self.clear()
        self.add_nav_bar()

        container = tk.Frame(self.root, bg=COLORS["bg"])
        container.pack(expand=True)
        self.add_widget(container)

        tk.Label(
            container, text="RESULTS",
            font=FONTS["header"], fg=COLORS["accent"], bg=COLORS["bg"],
        ).pack(pady=(0, 15))

        tk.Label(
            container,
            text=f"Key concepts recalled: {score}/{total}",
            font=FONTS["btn_lg"], fg=COLORS["fg"], bg=COLORS["bg"],
        ).pack(pady=5)

        tk.Label(
            container,
            text=f"XP earned: {xp}",
            font=FONTS["counter"], fg=COLORS["accent"], bg=COLORS["bg"],
        ).pack(pady=5)

        # Show which keywords were found/missed
        kw_frame = tk.Frame(container, bg=COLORS["bg"])
        kw_frame.pack(pady=15)

        for kw in self._keywords:
            found = kw in summary_words
            color = COLORS["success"] if found else COLORS["alert"]
            marker = "✓" if found else "✗"
            tk.Label(
                kw_frame,
                text=f"  {marker}  {kw}",
                font=FONTS["body"], fg=color, bg=COLORS["bg"],
                anchor="w", width=30,
            ).pack(anchor="w")

        tk.Button(
            container, text="CONTINUE",
            command=self.navigator.finish_exercise,
            bg=COLORS["accent"], fg=COLORS["btn_text"],
            font=FONTS["btn_bold"], width=20, pady=8,
            relief="flat", cursor="hand2",
        ).pack(pady=15)
