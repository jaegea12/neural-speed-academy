"""
Chunking exercise: flash multi-word phrases to train block reading.
"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QSlider, QMessageBox,
)
from PyQt6.QtCore import Qt

from neural_speed_academy.exercises.base import BaseExercise, ExerciseResult
from neural_speed_academy.theme import COLORS, make_qfont, theme_manager
from neural_speed_academy.config import CHUNKING_CONFIG, USER_DATA_CONFIG


class ChunkingExercise(BaseExercise):

    def __init__(self, navigator, parent: QWidget | None = None):
        super().__init__(navigator, parent)
        self.chunks: list = []
        self.chunk_idx: int = 0
        self.wpm: int = 250
        self.chunk_size: int = 3

    @property
    def name(self) -> str:
        return "Chunking"

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
        cl.setSpacing(8)

        guide_btn = QPushButton("GUIDE")
        guide_btn.setFont(make_qfont("btn_sm"))
        guide_btn.setStyleSheet(
            f"background-color: {c['accent']}; color: {c['btn_text']}; "
            f"border: none; padding: 4px 12px; border-radius: 3px;"
        )
        guide_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        guide_btn.clicked.connect(lambda: self.show_guide("chunking"))
        cl.addWidget(guide_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        title = QLabel("CHUNKING CONFIGURATION")
        title.setFont(make_qfont("header"))
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
        self._text_input.setFixedHeight(150)
        self._text_input.setPlainText(theme_manager.training_text)
        cl.addWidget(self._text_input)

        # Chunk size slider
        chunk_lbl = QLabel("Words Per Chunk:")
        chunk_lbl.setFont(make_qfont("slider_label"))
        chunk_lbl.setStyleSheet(f"color: {c['fg']};")
        cl.addWidget(chunk_lbl)

        init_chunk = kwargs.get("chunk_size", CHUNKING_CONFIG["default_chunk_size"])
        self._chunk_display = QLabel(str(init_chunk))
        self._chunk_display.setFont(make_qfont("counter"))
        self._chunk_display.setStyleSheet(f"color: {c['accent']};")
        self._chunk_display.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._chunk_slider = QSlider(Qt.Orientation.Horizontal)
        self._chunk_slider.setRange(
            CHUNKING_CONFIG["min_chunk_size"], CHUNKING_CONFIG["max_chunk_size"]
        )
        self._chunk_slider.setValue(init_chunk)
        self._chunk_slider.setFixedWidth(300)
        self._chunk_slider.setStyleSheet(
            f"QSlider::groove:horizontal {{ background: {c['card']}; height: 6px; border-radius: 3px; }}"
            f"QSlider::handle:horizontal {{ background: {c['accent']}; width: 16px; margin: -5px 0; border-radius: 8px; }}"
        )
        self._chunk_slider.valueChanged.connect(
            lambda v: self._chunk_display.setText(str(v))
        )
        cl.addWidget(self._chunk_slider, alignment=Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(self._chunk_display)

        # WPM slider
        wpm_lbl = QLabel("Display Speed (WPM equivalent):")
        wpm_lbl.setFont(make_qfont("slider_label"))
        wpm_lbl.setStyleSheet(f"color: {c['fg']};")
        cl.addWidget(wpm_lbl)

        init_wpm = kwargs.get("wpm", CHUNKING_CONFIG["default_wpm"])
        self._wpm_display = QLabel(str(init_wpm))
        self._wpm_display.setFont(make_qfont("counter"))
        self._wpm_display.setStyleSheet(f"color: {c['accent']};")
        self._wpm_display.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._wpm_slider = QSlider(Qt.Orientation.Horizontal)
        self._wpm_slider.setRange(CHUNKING_CONFIG["min_wpm"], CHUNKING_CONFIG["max_wpm"])
        self._wpm_slider.setValue(init_wpm)
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

        # Start button
        start_btn = QPushButton("START CHUNKING")
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
        self._delay = int(60000 * chunk_size / wpm)

        self._clear()
        self._running = True

        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")

        exit_btn = QPushButton("\u2716")
        exit_btn.setFont(make_qfont("exit_btn"))
        exit_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['alert']}; color: {c['text_on_card']}; "
            f"border: none; padding: 4px 8px; border-radius: 3px; }}"
        )
        exit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        exit_btn.clicked.connect(self._stop)
        self._layout.addWidget(exit_btn, alignment=Qt.AlignmentFlag.AlignRight)

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

    def _flash_chunk(self) -> None:
        if not self._running:
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
        total_words = sum(len(c.split()) for c in self.chunks)
        xp = total_words // 10
        result = ExerciseResult(
            exercise_name="CHUNKING",
            score=total_words,
            total=total_words,
            xp_gained=xp,
        )
        is_pb = self.complete(result)
        self.show_result_screen(
            result, is_personal_best=is_pb,
            details=f"Read {total_words} words in {len(self.chunks)} chunks at {self.wpm} WPM",
        )
