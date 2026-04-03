"""
Chunking exercise: flash multi-word phrases to train block reading.
"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit,
    QSlider, QMessageBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut

from neural_speed_academy.exercises.base import BaseExercise, ExerciseResult
from neural_speed_academy.theme import COLORS, make_qfont, input_css, theme_manager, screen_metrics
from neural_speed_academy.config import CHUNKING_CONFIG, USER_DATA_CONFIG


class ChunkingExercise(BaseExercise):

    def __init__(self, navigator, parent: QWidget | None = None):
        super().__init__(navigator, parent)
        self.chunks: list = []
        self.chunk_idx: int = 0
        self.wpm: int = 250
        self.chunk_size: int = 3
        self._paused: bool = False

    @property
    def name(self) -> str:
        return "Chunking"

    def start(self, **kwargs) -> None:
        self._clear()
        self._running = True
        self.add_nav_bar(show_stop=False)

        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")

        slider_groove = (
            f"QSlider::groove:horizontal {{ background: {c['card']}; "
            f"height: 6px; border-radius: 3px; }}"
            f"QSlider::handle:horizontal {{ background: {c['accent']}; "
            f"width: 16px; margin: -5px 0; border-radius: 8px; }}"
        )

        container = QWidget()
        container.setStyleSheet(f"background-color: {c['bg']};")
        cl = QVBoxLayout(container)
        cl.setContentsMargins(40, 10, 40, 10)
        cl.setSpacing(6)

        # Guide button
        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        guide_btn = QPushButton("GUIDE")
        guide_btn.setFont(make_qfont("btn_sm"))
        guide_btn.setStyleSheet(
            f"background-color: {c['accent']}; color: {c['btn_text']}; "
            f"border: none; padding: 4px 12px; border-radius: 3px;"
        )
        guide_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        guide_btn.clicked.connect(lambda: self.show_guide("chunking"))
        top.addWidget(guide_btn)
        top.addStretch()
        cl.addLayout(top)

        title = QLabel("CHUNKING CONFIGURATION")
        title.setFont(make_qfont("section_header"))
        title.setStyleSheet(f"color: {c['accent']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(title)

        # Text input — 60% screen width, 15 lines visible
        self._text_input = QTextEdit()
        self._text_input.setFont(make_qfont("pacer_text"))
        self._text_input.setStyleSheet(input_css(widget="QTextEdit"))
        fm = self._text_input.fontMetrics()
        line_h = fm.lineSpacing()
        self._text_input.setFixedHeight(line_h * 15 + 20)
        self._text_input.setFixedWidth(screen_metrics.text_input_w)
        self._text_input.setPlainText(theme_manager.training_text)
        cl.addWidget(self._text_input, 0, Qt.AlignmentFlag.AlignCenter)

        # Chunk size: label + slider + value in one row
        init_chunk = kwargs.get(
            "chunk_size", CHUNKING_CONFIG["default_chunk_size"]
        )
        chunk_row = QHBoxLayout()
        chunk_row.setContentsMargins(0, 0, 0, 0)
        chunk_row.setSpacing(8)
        chunk_row.addStretch()
        chunk_lbl = QLabel("Words/chunk:")
        chunk_lbl.setFont(make_qfont("slider_label"))
        chunk_lbl.setStyleSheet(f"color: {c['fg']};")
        chunk_row.addWidget(chunk_lbl)

        self._chunk_slider = QSlider(Qt.Orientation.Horizontal)
        self._chunk_slider.setRange(
            CHUNKING_CONFIG["min_chunk_size"],
            CHUNKING_CONFIG["max_chunk_size"],
        )
        self._chunk_slider.setValue(init_chunk)
        self._chunk_slider.setFixedWidth(200)
        self._chunk_slider.setStyleSheet(slider_groove)

        self._chunk_display = QLabel(str(init_chunk))
        self._chunk_display.setFont(make_qfont("counter"))
        self._chunk_display.setStyleSheet(f"color: {c['accent']};")
        self._chunk_display.setFixedWidth(30)
        self._chunk_slider.valueChanged.connect(
            lambda v: self._chunk_display.setText(str(v))
        )
        chunk_row.addWidget(self._chunk_slider)
        chunk_row.addWidget(self._chunk_display)
        chunk_row.addStretch()
        cl.addLayout(chunk_row)

        # WPM: label + slider + value in one row
        init_wpm = kwargs.get("wpm", CHUNKING_CONFIG["default_wpm"])
        wpm_row = QHBoxLayout()
        wpm_row.setContentsMargins(0, 0, 0, 0)
        wpm_row.setSpacing(8)
        wpm_row.addStretch()
        wpm_lbl = QLabel("Target WPM:")
        wpm_lbl.setFont(make_qfont("slider_label"))
        wpm_lbl.setStyleSheet(f"color: {c['fg']};")
        wpm_row.addWidget(wpm_lbl)

        self._wpm_slider = QSlider(Qt.Orientation.Horizontal)
        self._wpm_slider.setRange(
            CHUNKING_CONFIG["min_wpm"], CHUNKING_CONFIG["max_wpm"]
        )
        self._wpm_slider.setValue(init_wpm)
        self._wpm_slider.setFixedWidth(300)
        self._wpm_slider.setStyleSheet(slider_groove)

        self._wpm_display = QLabel(str(init_wpm))
        self._wpm_display.setFont(make_qfont("counter"))
        self._wpm_display.setStyleSheet(f"color: {c['accent']};")
        self._wpm_display.setFixedWidth(50)
        self._wpm_slider.valueChanged.connect(
            lambda v: self._wpm_display.setText(str(v))
        )
        wpm_row.addWidget(self._wpm_slider)
        wpm_row.addWidget(self._wpm_display)
        wpm_row.addStretch()
        cl.addLayout(wpm_row)

        # Start button
        cl.addSpacing(4)
        start_btn = QPushButton("START CHUNKING")
        start_btn.setFont(make_qfont("btn_lg"))
        start_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['success']}; "
            f"color: {c['btn_text']}; "
            f"border: none; padding: 10px 40px; border-radius: 4px; }}"
        )
        start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        start_btn.clicked.connect(self._start_from_ui)
        cl.addWidget(start_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        hint = QLabel("Ctrl+Enter to start  |  Space to pause")
        hint.setFont(make_qfont("btn_sm"))
        hint.setStyleSheet(f"color: {c['muted']};")
        cl.addWidget(hint, alignment=Qt.AlignmentFlag.AlignCenter)

        shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        shortcut.activated.connect(self._start_from_ui)

        self._layout.addWidget(container, 1)

    def _start_from_ui(self) -> None:
        text = self._text_input.toPlainText()
        self._run_chunking(text, self._chunk_slider.value(), self._wpm_slider.value())

    def _build_chunks(self, text: str, size: int) -> list:
        words = text.split()
        return [" ".join(words[i:i + size]) for i in range(0, len(words), size)]

    def _run_chunking(self, text: str, chunk_size: int, wpm: int) -> None:
        self.chunks = self._build_chunks(text, chunk_size)
        if not self.chunks:
            QMessageBox.information(self, "No Text", "Please enter some text before starting.")
            return

        self.chunk_size = chunk_size
        self.wpm = wpm
        self.chunk_idx = 0
        self._paused = False
        self._delay = int(60000 * chunk_size / wpm)

        self._clear()
        self._running = True

        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")

        top_row = QHBoxLayout()
        top_row.setContentsMargins(8, 4, 8, 0)

        self._pause_btn = QPushButton("PAUSE")
        self._pause_btn.setFont(make_qfont("btn_sm"))
        self._pause_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['action']}; color: {c['btn_text']}; "
            f"border: none; padding: 4px 14px; border-radius: 3px; }}"
        )
        self._pause_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._pause_btn.clicked.connect(self._toggle_pause)
        top_row.addWidget(self._pause_btn)

        top_row.addStretch()

        exit_btn = QPushButton("\u2716")
        exit_btn.setAccessibleName("Close")
        exit_btn.setToolTip("Close")
        exit_btn.setFont(make_qfont("exit_btn"))
        exit_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['alert']}; color: {c['text_on_card']}; "
            f"border: none; padding: 4px 8px; border-radius: 3px; }}"
        )
        exit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        exit_btn.clicked.connect(self._stop)
        top_row.addWidget(exit_btn)

        self._layout.addLayout(top_row)

        self._lbl_progress = QLabel(f"0% | {chunk_size}-word chunks | {wpm} WPM")
        self._lbl_progress.setFont(make_qfont("counter"))
        self._lbl_progress.setStyleSheet(f"color: {c['accent']};")
        self._lbl_progress.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(self._lbl_progress)

        self._lbl_chunk = QLabel("")
        self._lbl_chunk.setFont(make_qfont("rsvp"))
        self._lbl_chunk.setStyleSheet(f"color: {c['fg']};")
        self._lbl_chunk.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(self._lbl_chunk, 1)

        self._after(500, self._flash_chunk)

    def _toggle_pause(self) -> None:
        c = COLORS
        if self._paused:
            self._paused = False
            self._pause_btn.setText("PAUSE")
            self._pause_btn.setStyleSheet(
                f"QPushButton {{ background-color: {c['action']}; color: {c['btn_text']}; "
                f"border: none; padding: 4px 14px; border-radius: 3px; }}"
            )
            self._flash_chunk()
        else:
            self._paused = True
            self._pause_btn.setText("CONTINUE")
            self._pause_btn.setStyleSheet(
                f"QPushButton {{ background-color: {c['success']}; color: {c['btn_text']}; "
                f"border: none; padding: 4px 14px; border-radius: 3px; }}"
            )
            status = self._lbl_progress.text()
            self._lbl_progress.setText(f"PAUSED | {status.split('|', 1)[-1].strip()}")

    def _flash_chunk(self) -> None:
        if not self._running or self._paused:
            return
        if self.chunk_idx >= len(self.chunks):
            self._complete_exercise()
            return

        self._lbl_chunk.setText(self.chunks[self.chunk_idx])
        self.chunk_idx += 1
        pct = int(self.chunk_idx / len(self.chunks) * 100)
        self._lbl_progress.setText(
            f"{pct}% | {self.chunk_size}-word chunks | {self.wpm} WPM"
        )
        self._after(self._delay, self._flash_chunk)

    def _stop(self) -> None:
        self._running = False
        self.navigator.finish_exercise()

    def _complete_exercise(self) -> None:
        self._running = False
        self._total_words = sum(len(c.split()) for c in self.chunks)
        self._source_text = " ".join(self.chunks)
        self._quiz_phase()

    def _quiz_phase(self) -> None:
        from neural_speed_academy.exercises.recall import build_recall_screen
        self._clear()
        self.add_nav_bar()
        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")
        build_recall_screen(
            self, self._layout, self._source_text,
            on_scored=self._on_recall_scored,
            exercise_label="CHUNKING — COMPREHENSION CHECK",
        )

    def _on_recall_scored(self, score, total, matches, keywords) -> None:
        from neural_speed_academy.exercises.recall import build_recall_results
        self._clear()
        self.add_nav_bar(show_stop=False)
        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")

        int_score = int(score) if score == int(score) else round(score, 1)
        comprehension_pct = round(score / total * 100) if total > 0 else 0
        xp = self._total_words // 10 + int(score) * USER_DATA_CONFIG["xp_per_correct"]
        result = ExerciseResult(
            exercise_name="CHUNKING",
            score=int_score,
            total=total,
            xp_gained=xp,
            metadata={
                "wpm": self.wpm,
                "chunk_size": self.chunk_size,
                "word_count": self._total_words,
                "chunk_count": len(self.chunks),
                "comprehension_score": int_score,
                "comprehension_total": total,
                "comprehension_pct": comprehension_pct,
            },
        )
        is_pb = self.complete(result)

        cl = build_recall_results(
            self._layout, score, total, matches, keywords,
        )

        cl.addSpacing(10)
        details = QLabel(
            f"Read {self._total_words} words in {len(self.chunks)} chunks at {self.wpm} WPM"
        )
        details.setFont(make_qfont("body"))
        details.setStyleSheet(f"color: {c['fg']};")
        details.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(details)

        if is_pb:
            pb = QLabel("NEW PERSONAL BEST!")
            pb.setFont(make_qfont("btn_bold"))
            pb.setStyleSheet(f"color: {c['highlight']};")
            pb.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cl.addWidget(pb)

        cl.addSpacing(10)
        cont_btn = QPushButton("CONTINUE")
        cont_btn.setFont(make_qfont("btn_bold"))
        cont_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['accent']}; color: {c['btn_text']}; "
            f"border: none; padding: 8px 40px; border-radius: 4px; }}"
        )
        cont_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cont_btn.clicked.connect(self.navigator.finish_exercise)
        cl.addWidget(cont_btn, alignment=Qt.AlignmentFlag.AlignCenter)
