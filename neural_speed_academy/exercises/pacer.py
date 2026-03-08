"""
Pacer exercise with 5 highlight modes, peripheral dimming, live WPM bar,
display-line-aware stepping, and keyword comprehension quiz.
"""
from __future__ import annotations

import re
import time

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QSlider, QRadioButton, QButtonGroup, QFrame, QMessageBox,
    QProgressBar,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import (
    QTextCursor, QColor, QFont, QKeySequence, QShortcut,
)

from neural_speed_academy.exercises.base import BaseExercise, ExerciseResult
from neural_speed_academy.theme import COLORS, make_qfont, theme_manager
from neural_speed_academy.config import PACER_CONFIG, USER_DATA_CONFIG

# ── Keyword extraction ──

_STOP_WORDS = frozenset(
    "the a an and or but in on at to for of is it that this with from by as "
    "are was were be been has have had do does did not no nor so if then than "
    "can will would could should may might shall its you your we our they them "
    "he she his her my me us who what when where how all each every some any "
    "also just about more most very much many such only other into over after "
    "before between through during without again further once here there which "
    "these those being both same own too up out off down".split()
)


def _extract_keywords(text: str, max_keywords: int = 8) -> list[str]:
    words = re.findall(r"[a-zA-Z]+", text.lower())
    freq: dict[str, int] = {}
    for w in words:
        if len(w) >= 4 and w not in _STOP_WORDS:
            freq[w] = freq.get(w, 0) + 1
    ranked = sorted(freq, key=lambda w: freq[w], reverse=True)
    return ranked[:max_keywords]


# ── Helpers ──

def _radio_style(c: dict) -> str:
    return (
        f"QRadioButton {{ color: {c['fg']}; background: transparent; spacing: 8px; }}"
        f"QRadioButton::indicator {{ width: 14px; height: 14px; "
        f"border: 2px solid {c['muted']}; border-radius: 7px; "
        f"background: transparent; }}"
        f"QRadioButton::indicator:checked {{ "
        f"border: 2px solid {c['accent']}; "
        f"background: {c['accent']}; }}"
    )


class PacerExercise(BaseExercise):

    MODES = {
        "word": "Word",
        "chunk": "Chunk",
        "line": "Line",
        "multi": "Multi-Line",
        "zpattern": "Z-Pattern",
    }

    def __init__(self, navigator, parent: QWidget | None = None):
        super().__init__(navigator, parent)
        self._source_text: str = ""
        self._words: list[str] = []
        # Each step: (char_start, char_end, group_start, group_end)
        # group_start/group_end define the vertical extent for the overlay
        self._steps: list[tuple[int, int, int, int]] = []
        self._step_idx: int = 0
        self._delay: int = 200
        self._n_lines: int = 3
        self._start_time: float = 0.0

    @property
    def name(self) -> str:
        return "Pacer"

    # ── Config screen ──

    def start(self, **kwargs) -> None:
        self._clear()
        self._running = True
        self.add_nav_bar()

        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")

        container = QWidget()
        container.setStyleSheet(f"background-color: {c['bg']};")
        cl = QVBoxLayout(container)
        cl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.setContentsMargins(80, 5, 80, 5)
        cl.setSpacing(4)

        # Guide button
        top = QHBoxLayout()
        guide_btn = QPushButton("GUIDE")
        guide_btn.setFont(make_qfont("btn_sm"))
        guide_btn.setStyleSheet(
            f"background-color: {c['accent']}; color: {c['btn_text']}; "
            f"border: none; padding: 4px 12px; border-radius: 3px;"
        )
        guide_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        guide_btn.clicked.connect(lambda: self.show_guide("pacer"))
        top.addWidget(guide_btn)
        top.addStretch()
        cl.addLayout(top)

        title = QLabel("PACER CONFIGURATION")
        title.setFont(make_qfont("section_header"))
        title.setStyleSheet(f"color: {c['accent']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(title)

        # Text input
        self._text_input = QTextEdit()
        self._text_input.setFont(make_qfont("pacer_text"))
        self._text_input.setStyleSheet(
            f"QTextEdit {{ background-color: {c['card']}; color: {c['text_on_card']}; "
            f"border: none; padding: 8px; border-radius: 4px; }}"
        )
        self._text_input.setFixedHeight(120)
        self._text_input.setPlainText(theme_manager.training_text)
        cl.addWidget(self._text_input)

        # WPM slider
        wpm_lbl = QLabel("Target Speed (WPM):")
        wpm_lbl.setFont(make_qfont("slider_label"))
        wpm_lbl.setStyleSheet(f"color: {c['fg']};")
        wpm_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(wpm_lbl)

        self._wpm_display = QLabel(str(PACER_CONFIG["default_wpm"]))
        self._wpm_display.setFont(make_qfont("counter"))
        self._wpm_display.setStyleSheet(f"color: {c['accent']};")
        self._wpm_display.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._wpm_slider = QSlider(Qt.Orientation.Horizontal)
        self._wpm_slider.setRange(PACER_CONFIG["min_wpm"], PACER_CONFIG["max_wpm"])
        self._wpm_slider.setValue(PACER_CONFIG["default_wpm"])
        self._wpm_slider.setFixedWidth(400)
        self._wpm_slider.setStyleSheet(
            f"QSlider::groove:horizontal {{ background: {c['card']}; height: 6px; border-radius: 3px; }}"
            f"QSlider::handle:horizontal {{ background: {c['accent']}; width: 16px; margin: -5px 0; border-radius: 8px; }}"
        )
        self._wpm_slider.valueChanged.connect(
            lambda v: self._wpm_display.setText(str(v))
        )
        cl.addWidget(self._wpm_slider, alignment=Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(self._wpm_display)

        # Mode selector
        mode_lbl = QLabel("Highlight Mode:")
        mode_lbl.setFont(make_qfont("slider_label"))
        mode_lbl.setStyleSheet(f"color: {c['fg']};")
        mode_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(mode_lbl)

        rb_style = _radio_style(c)
        self._mode_group = QButtonGroup(self)
        mode_row = QHBoxLayout()
        mode_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        for key, label in self.MODES.items():
            rb = QRadioButton(label)
            rb.setFont(make_qfont("btn"))
            rb.setStyleSheet(rb_style)
            rb.setProperty("mode_key", key)
            if key == "word":
                rb.setChecked(True)
            self._mode_group.addButton(rb)
            mode_row.addWidget(rb)
        self._mode_group.buttonClicked.connect(self._on_mode_changed)
        cl.addLayout(mode_row)

        # N-lines slider (visible only for multi / z-pattern)
        self._nlines_frame = QFrame()
        self._nlines_frame.setStyleSheet("background: transparent;")
        nf_layout = QVBoxLayout(self._nlines_frame)
        nf_layout.setContentsMargins(0, 0, 0, 0)
        nf_layout.setSpacing(2)

        nlines_lbl = QLabel("Lines per step:")
        nlines_lbl.setFont(make_qfont("slider_label"))
        nlines_lbl.setStyleSheet(f"color: {c['fg']};")
        nf_layout.addWidget(nlines_lbl)

        self._nlines_display = QLabel("3")
        self._nlines_display.setFont(make_qfont("counter"))
        self._nlines_display.setStyleSheet(f"color: {c['accent']};")
        self._nlines_display.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._nlines_slider = QSlider(Qt.Orientation.Horizontal)
        self._nlines_slider.setRange(2, 5)
        self._nlines_slider.setValue(3)
        self._nlines_slider.setFixedWidth(200)
        self._nlines_slider.setStyleSheet(
            f"QSlider::groove:horizontal {{ background: {c['card']}; height: 6px; border-radius: 3px; }}"
            f"QSlider::handle:horizontal {{ background: {c['accent']}; width: 16px; margin: -5px 0; border-radius: 8px; }}"
        )
        self._nlines_slider.valueChanged.connect(
            lambda v: self._nlines_display.setText(str(v))
        )
        nf_layout.addWidget(self._nlines_slider, alignment=Qt.AlignmentFlag.AlignCenter)
        nf_layout.addWidget(self._nlines_display)

        self._nlines_frame.setVisible(False)
        cl.addWidget(self._nlines_frame, alignment=Qt.AlignmentFlag.AlignCenter)

        # Start button
        start_btn = QPushButton("START READING")
        start_btn.setFont(make_qfont("btn_lg"))
        start_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['success']}; color: {c['btn_text']}; "
            f"border: none; padding: 10px 40px; border-radius: 4px; }}"
        )
        start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        start_btn.clicked.connect(self._start_from_ui)
        cl.addWidget(start_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        hint = QLabel("Ctrl+Enter to start")
        hint.setFont(make_qfont("btn_sm"))
        hint.setStyleSheet(f"color: {c['muted']};")
        cl.addWidget(hint, alignment=Qt.AlignmentFlag.AlignCenter)

        self._layout.addWidget(container, 1)

        # Ctrl+Enter shortcut
        shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        shortcut.activated.connect(self._start_from_ui)

    def _on_mode_changed(self, btn: QRadioButton) -> None:
        mode = btn.property("mode_key")
        self._nlines_frame.setVisible(mode in ("multi", "zpattern"))

    # ── Launch reading ──

    def _start_from_ui(self) -> None:
        text = self._text_input.toPlainText()
        wpm = self._wpm_slider.value()
        mode = "word"
        for btn in self._mode_group.buttons():
            if btn.isChecked():
                mode = btn.property("mode_key")
                break
        self._n_lines = self._nlines_slider.value()
        self._run_pacer(text, wpm, mode)

    def _run_pacer(self, text: str, wpm: int, mode: str) -> None:
        words = text.split()
        if not words:
            QMessageBox.information(
                self, "No Text", "Please enter some text before starting."
            )
            return

        self._source_text = text
        self._words = words
        self._wpm_target = wpm
        self._mode = mode

        self._clear()
        self._running = True

        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")

        # Top bar: exit + WPM indicator
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(10, 6, 10, 2)

        exit_btn = QPushButton("\u2716")
        exit_btn.setFont(make_qfont("exit_btn"))
        exit_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['alert']}; "
            f"color: {c['text_on_card']}; "
            f"border: none; padding: 4px 8px; border-radius: 3px; }}"
        )
        exit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        exit_btn.clicked.connect(self.navigator.finish_exercise)
        top_bar.addWidget(exit_btn)
        top_bar.addStretch()

        self._wpm_label = QLabel(f"WPM: {wpm}")
        self._wpm_label.setFont(make_qfont("counter"))
        self._wpm_label.setStyleSheet(f"color: {c['accent']};")
        top_bar.addWidget(self._wpm_label)
        self._layout.addLayout(top_bar)

        # Progress bar
        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        self._progress_bar.setFixedHeight(6)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setStyleSheet(
            f"QProgressBar {{ background: {c['card']}; "
            f"border: none; border-radius: 3px; }}"
            f"QProgressBar::chunk {{ background: {c['accent']}; "
            f"border-radius: 3px; }}"
        )
        self._layout.addWidget(self._progress_bar)

        # Reader page — A4-ish proportions, capped for screen safety
        fov = theme_manager.fov_config
        page_w = fov["page_width"]
        page_h = min(int(page_w * 1.35), 900)
        font_size = fov["font_size"]

        self._reader = QTextEdit()
        reader_font = QFont("Georgia", font_size)
        self._reader.setFont(reader_font)
        px, py = fov["pad_x"], fov["pad_y"]
        self._reader.setStyleSheet(
            f"QTextEdit {{ background-color: {c['reader_bg']}; "
            f"color: {c['reader_fg']}; "
            f"border: 1px solid {c['muted']}; "
            f"padding: {py}px {px}px; }}"
        )
        self._reader.setFixedSize(page_w, page_h)
        self._reader.setReadOnly(True)
        self._reader.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._reader.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        joined = " ".join(words)
        self._reader.setPlainText(joined)

        # Highlight overlay — child of viewport so cursorRect coords
        # map directly without offset translation
        vp = self._reader.viewport()
        self._overlay = QWidget(vp)
        hl_color = QColor(c["highlight"])
        hl_color.setAlpha(80)
        self._overlay.setStyleSheet(
            f"background-color: rgba({hl_color.red()},{hl_color.green()},"
            f"{hl_color.blue()},{hl_color.alpha()}); border-radius: 3px;"
        )
        self._overlay.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents
        )
        self._overlay.setGeometry(0, 0, 0, 0)
        self._overlay.show()

        self._layout.addWidget(
            self._reader, 1, Qt.AlignmentFlag.AlignCenter
        )

        # Defer step building until layout is done
        QTimer.singleShot(250, self._build_and_start)

    def _build_and_start(self) -> None:
        joined = " ".join(self._words)
        self._steps = self._build_steps(
            joined, self._words, self._mode
        )
        self._step_idx = 0

        avg_words = len(self._words) / max(len(self._steps), 1)
        self._delay = int(60000 / self._wpm_target * avg_words)

        self._start_time = time.monotonic()
        self._words_shown = 0
        self._after(300, self._pacer_step)

    # ── Display-line detection ──

    def _get_display_lines(self, text: str) -> list[tuple[int, int]]:
        """Use QTextEdit layout to find actual wrapped line boundaries.
        Falls back to font-metrics estimation if layout isn't ready."""
        doc = self._reader.document()
        lines: list[tuple[int, int]] = []
        block = doc.begin()
        while block.isValid():
            layout = block.layout()
            if layout and layout.lineCount() > 0:
                block_start = block.position()
                for i in range(layout.lineCount()):
                    line = layout.lineAt(i)
                    start = block_start + line.textStart()
                    length = line.textLength()
                    end = start + length
                    while end > start and text[end - 1 : end] in (" ", "\n"):
                        end -= 1
                    if end > start:
                        lines.append((start, end))
            block = block.next()

        if lines:
            return lines

        # Fallback: estimate using font metrics and widget width
        fm = self._reader.fontMetrics()
        avg_char_w = fm.averageCharWidth()
        fov = theme_manager.fov_config
        usable_w = fov["page_width"] - 2 * fov["pad_x"] - 20
        chars_per_line = max(20, usable_w // max(avg_char_w, 1))
        pos = 0
        while pos < len(text):
            end = min(pos + chars_per_line, len(text))
            if end < len(text):
                space = text.rfind(" ", pos, end)
                if space > pos:
                    end = space
            lines.append((pos, end))
            pos = end + 1 if end < len(text) else end
        return lines or [(0, len(text))]

    def _chunk_line(
        self,
        text: str,
        line_start: int,
        line_end: int,
        chunk_words: int,
        group_start: int | None = None,
        group_end: int | None = None,
    ) -> list[tuple[int, int, int, int]]:
        """Split a text range into chunk-sized word groups.
        group_start/group_end define the vertical extent for the overlay."""
        gs = group_start if group_start is not None else line_start
        ge = group_end if group_end is not None else line_end
        segment = text[line_start:line_end]
        words_in_line = segment.split()
        if not words_in_line:
            return [(line_start, line_end, gs, ge)]
        chunks: list[tuple[int, int, int, int]] = []
        pos = line_start
        for i in range(0, len(words_in_line), chunk_words):
            group = " ".join(words_in_line[i : i + chunk_words])
            idx = text.find(group, pos)
            if idx == -1:
                idx = pos
            chunks.append((idx, idx + len(group), gs, ge))
            pos = idx + len(group)
        return chunks

    # ── Step building ──

    def _build_steps(
        self, text: str, words: list[str], mode: str,
    ) -> list[tuple[int, int, int, int]]:
        if mode == "word":
            return self._steps_word(text, words)
        elif mode == "chunk":
            return self._steps_chunk(text, words)
        elif mode == "line":
            return self._steps_line(text)
        elif mode == "multi":
            return self._steps_multi(text)
        elif mode == "zpattern":
            return self._steps_zpattern(text)
        return [(0, len(text), 0, len(text))]

    def _steps_word(
        self, text: str, words: list[str],
    ) -> list[tuple[int, int, int, int]]:
        steps: list[tuple[int, int, int, int]] = []
        pos = 0
        for w in words:
            idx = text.find(w, pos)
            if idx == -1:
                idx = pos
            steps.append((idx, idx + len(w), idx, idx + len(w)))
            pos = idx + len(w)
        return steps or [(0, len(text), 0, len(text))]

    def _steps_chunk(
        self, text: str, words: list[str],
    ) -> list[tuple[int, int, int, int]]:
        chunk_size = 3
        steps: list[tuple[int, int, int, int]] = []
        pos = 0
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i : i + chunk_size])
            idx = text.find(chunk, pos)
            if idx == -1:
                idx = pos
            end = idx + len(chunk)
            steps.append((idx, end, idx, end))
            pos = end
        return steps or [(0, len(text), 0, len(text))]

    def _steps_line(
        self, text: str,
    ) -> list[tuple[int, int, int, int]]:
        """Chunk-width highlight sweeping across each display line."""
        lines = self._get_display_lines(text)
        steps: list[tuple[int, int, int, int]] = []
        for ls, le in lines:
            steps.extend(self._chunk_line(text, ls, le, 3))
        return steps or [(0, len(text), 0, len(text))]

    def _steps_multi(
        self, text: str,
    ) -> list[tuple[int, int, int, int]]:
        """Chunk-width highlight spanning n_lines in height, sweeping
        left-to-right across the first line of each group, then jumping
        down to the next group."""
        lines = self._get_display_lines(text)
        n = self._n_lines
        if not lines:
            return [(0, len(text), 0, len(text))]
        steps: list[tuple[int, int, int, int]] = []
        for i in range(0, len(lines), n):
            group = lines[i : i + n]
            gs = group[0][0]
            ge = group[-1][1]
            # Sweep across the first line; overlay height spans all n_lines
            first_ls, first_le = group[0]
            steps.extend(
                self._chunk_line(text, first_ls, first_le, 3, gs, ge)
            )
        return steps or [(0, len(text), 0, len(text))]

    def _steps_zpattern(
        self, text: str,
    ) -> list[tuple[int, int, int, int]]:
        """Z-pattern: 3 sweeps per n_lines group (left→right, right→left,
        left→right). Overlay height spans the full group."""
        lines = self._get_display_lines(text)
        n = self._n_lines
        if not lines:
            return [(0, len(text), 0, len(text))]
        steps: list[tuple[int, int, int, int]] = []
        for i in range(0, len(lines), n):
            group = lines[i : i + n]
            gs = group[0][0]
            ge = group[-1][1]
            block_len = ge - gs
            if block_len <= 0:
                steps.append((gs, ge, gs, ge))
                continue
            seg = block_len // 3
            steps.append((gs, gs + seg, gs, ge))
            steps.append((gs + seg, gs + 2 * seg, gs, ge))
            steps.append((gs + 2 * seg, ge, gs, ge))
        return steps or [(0, len(text), 0, len(text))]

    # ── Overlay positioning ──

    def _overlay_rect(
        self, start: int, end: int, group_start: int, group_end: int,
    ) -> tuple[int, int, int, int]:
        """Compute pixel rect for the highlight overlay.
        Width from (start, end), height from (group_start, group_end).
        Coordinates are in viewport space (overlay is a viewport child)."""
        cursor = self._reader.textCursor()

        # Horizontal extent from the chunk characters
        cursor.setPosition(start)
        r1 = self._reader.cursorRect(cursor)
        cursor.setPosition(end)
        r2 = self._reader.cursorRect(cursor)

        x = r1.left()
        if r2.top() > r1.top():
            w = self._reader.viewport().width() - x
        else:
            w = max(r2.right() - r1.left(), 10)

        # Vertical extent from the group boundaries
        cursor.setPosition(group_start)
        rg1 = self._reader.cursorRect(cursor)
        cursor.setPosition(group_end)
        rg2 = self._reader.cursorRect(cursor)

        y = rg1.top()
        h = max(rg2.bottom() - rg1.top(), r1.height())

        return x, y, w, h

    # ── Pacer step ──

    def _pacer_step(self) -> None:
        if not self._running:
            return
        if self._step_idx >= len(self._steps):
            self._overlay.hide()
            self._quiz_phase()
            return

        start, end, gs, ge = self._steps[self._step_idx]

        # Position the overlay highlight
        ox, oy, ow, oh = self._overlay_rect(start, end, gs, ge)
        self._overlay.setGeometry(ox, oy, ow, oh)
        self._overlay.show()

        # Scroll so the highlighted area is visible
        cursor = self._reader.textCursor()
        cursor.setPosition(start)
        self._reader.setTextCursor(cursor)
        self._reader.ensureCursorVisible()

        # Update progress bar
        pct = int(100 * (self._step_idx + 1) / len(self._steps))
        self._progress_bar.setValue(pct)

        # Update live WPM
        joined = " ".join(self._words)
        self._words_shown += len(joined[start:end].split())
        elapsed = time.monotonic() - self._start_time
        if elapsed > 0.5:
            live_wpm = int(self._words_shown / (elapsed / 60))
            self._wpm_label.setText(f"WPM: {live_wpm}")

        self._step_idx += 1
        self._after(self._delay, self._pacer_step)

    # ── Quiz phase ──

    def _quiz_phase(self) -> None:
        self._clear()
        self._running = True
        self.add_nav_bar()

        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")
        self._keywords = _extract_keywords(self._source_text)

        container = QWidget()
        container.setStyleSheet(f"background-color: {c['bg']};")
        cl = QVBoxLayout(container)
        cl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.setSpacing(8)

        title = QLabel("COMPREHENSION CHECK")
        title.setFont(make_qfont("header"))
        title.setStyleSheet(f"color: {c['accent']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(title)

        desc = QLabel("Summarize what you just read in your own words.")
        desc.setFont(make_qfont("body"))
        desc.setStyleSheet(f"color: {c['fg']};")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(desc)

        self._quiz_input = QTextEdit()
        self._quiz_input.setFont(make_qfont("pacer_text"))
        self._quiz_input.setStyleSheet(
            f"QTextEdit {{ background-color: {c['card']}; color: {c['text_on_card']}; "
            f"border: none; padding: 8px; border-radius: 4px; }}"
        )
        self._quiz_input.setFixedHeight(150)
        cl.addWidget(self._quiz_input)

        check_btn = QPushButton("CHECK")
        check_btn.setFont(make_qfont("btn_bold"))
        check_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['accent']}; color: {c['btn_text']}; "
            f"border: none; padding: 8px 30px; border-radius: 4px; }}"
        )
        check_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        check_btn.clicked.connect(self._score_quiz)
        cl.addWidget(check_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self._layout.addWidget(container, 1)
        self._quiz_input.setFocus()

    def _score_quiz(self) -> None:
        summary = self._quiz_input.toPlainText().lower()
        summary_words = set(re.findall(r"[a-zA-Z]+", summary))

        matched = [kw for kw in self._keywords if kw in summary_words]
        score = len(matched)
        total = len(self._keywords)

        xp = score * USER_DATA_CONFIG["xp_per_correct"]
        result = ExerciseResult(
            exercise_name="PACER", score=score, total=total, xp_gained=xp,
        )
        is_pb = self.complete(result)

        # Results screen with keyword breakdown
        self._clear()
        self.add_nav_bar()

        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")

        container = QWidget()
        container.setStyleSheet(f"background-color: {c['bg']};")
        cl = QVBoxLayout(container)
        cl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.setSpacing(6)

        title = QLabel("RESULTS")
        title.setFont(make_qfont("header"))
        title.setStyleSheet(f"color: {c['accent']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(title)

        score_lbl = QLabel(f"Key concepts recalled: {score}/{total}")
        score_lbl.setFont(make_qfont("btn_lg"))
        score_lbl.setStyleSheet(f"color: {c['fg']};")
        score_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(score_lbl)

        xp_lbl = QLabel(f"XP earned: +{xp}")
        xp_lbl.setFont(make_qfont("counter"))
        xp_lbl.setStyleSheet(f"color: {c['accent']};")
        xp_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(xp_lbl)

        if is_pb:
            pb = QLabel("NEW PERSONAL BEST!")
            pb.setFont(make_qfont("btn_bold"))
            pb.setStyleSheet(f"color: {c['success']};")
            pb.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cl.addWidget(pb)

        for kw in self._keywords:
            found = kw in summary_words
            color = c["success"] if found else c["alert"]
            marker = "\u2713" if found else "\u2717"
            lbl = QLabel(f"  {marker}  {kw}")
            lbl.setFont(make_qfont("body"))
            lbl.setStyleSheet(f"color: {color};")
            cl.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignCenter)

        cont_btn = QPushButton("CONTINUE")
        cont_btn.setFont(make_qfont("btn_bold"))
        cont_btn.setStyleSheet(
            f"background-color: {c['accent']}; color: {c['btn_text']}; "
            f"border: none; padding: 8px 40px; border-radius: 4px;"
        )
        cont_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cont_btn.clicked.connect(self.navigator.finish_exercise)
        cl.addWidget(cont_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self._layout.addWidget(container, 1)
