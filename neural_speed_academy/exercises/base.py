"""
Base exercise class implementing the Template Method pattern for PyQt6.
"""
from __future__ import annotations

import logging
from abc import abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QMessageBox,
)
from PyQt6.QtCore import Qt, QTimer

from neural_speed_academy.theme import COLORS, make_qfont, font_css
from neural_speed_academy.config import USER_DATA_CONFIG

if TYPE_CHECKING:
    from neural_speed_academy.navigation.navigator import Navigator

logger = logging.getLogger(__name__)


class ExerciseError(Exception):
    pass


class ExerciseConfigError(ExerciseError):
    pass


@dataclass
class ExerciseResult:
    exercise_name: str
    score: int
    total: int
    xp_gained: int
    metadata: dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def score_string(self) -> str:
        return f"{self.score}/{self.total}"


class BaseExercise(QWidget):
    """Abstract base for all exercises. Renders into the navigator's stack."""

    def __init__(self, navigator: "Navigator", parent: QWidget | None = None):
        super().__init__(parent)
        self.navigator = navigator
        self._running: bool = False
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self._timers: list[QTimer] = []

    def _play(self, tone: str) -> None:
        """Play an audio cue, syncing engine state from theme settings."""
        from neural_speed_academy.audio import audio_engine
        from neural_speed_academy.theme import theme_manager
        audio_engine.enabled = theme_manager.sound_enabled
        audio_engine.volume = theme_manager.sound_volume
        audio_engine.play(tone)

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    def _clear(self) -> None:
        """Remove all child widgets, nested layouts, and stop timers."""
        self._running = False
        for timer in self._timers:
            timer.stop()
        self._timers.clear()
        self._clear_layout(self._layout)

    @staticmethod
    def _clear_layout(layout) -> None:
        """Recursively remove all items from a layout."""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                BaseExercise._clear_layout(item.layout())

    def _after(self, ms: int, callback) -> QTimer:
        """Schedule a callback after ms milliseconds. Returns the timer."""
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(callback)
        timer.start(ms)
        self._timers.append(timer)
        return timer

    def add_nav_bar(self, show_stop: bool = True) -> QFrame:
        """Add a navigation bar (same pattern as BaseScreen).

        Args:
            show_stop: Show the STOP button. Set False for config/menu
                       screens where Back is sufficient.
        """
        c = COLORS
        bar = QFrame()
        bar.setStyleSheet(f"background-color: {c['card']};")
        bar.setFixedHeight(50)
        bar_layout = QHBoxLayout(bar)
        bar_layout.setContentsMargins(10, 8, 10, 8)

        btn_style = (
            f"QPushButton {{ {font_css('btn_sm')} border: none; "
            f"padding: 2px 8px; border-radius: 3px; }}"
        )

        back_btn = QPushButton("\u2190 Back")
        back_btn.setStyleSheet(
            btn_style
            + f"QPushButton {{ background-color: {c['card']}; color: {c['fg']}; }}"
            + f"QPushButton:hover {{ background-color: {c['bg']}; }}"
        )
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(self.navigator.go_back)
        bar_layout.addWidget(back_btn)

        hub_btn = QPushButton("Training Hub")
        hub_btn.setStyleSheet(
            btn_style
            + f"QPushButton {{ background-color: {c['accent']}; color: {c['btn_text']}; }}"
        )
        hub_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        hub_btn.clicked.connect(self.navigator.to_dashboard)
        bar_layout.addWidget(hub_btn)

        bar_layout.addStretch()

        menu_btn = QPushButton("Main Menu")
        menu_btn.setStyleSheet(
            btn_style
            + f"QPushButton {{ background-color: {c['card']}; color: {c['fg']}; }}"
            + f"QPushButton:hover {{ background-color: {c['bg']}; }}"
        )
        menu_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        menu_btn.clicked.connect(lambda: self.navigator.navigate_to("main_menu"))
        bar_layout.addWidget(menu_btn)

        if show_stop:
            stop_btn = QPushButton("\u25a0 STOP")
            stop_btn.setStyleSheet(
                btn_style
                + f"QPushButton {{ background-color: {c['alert']}; color: {c['btn_text']}; }}"
            )
            stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            stop_btn.clicked.connect(self._stop_exercise)
            bar_layout.addWidget(stop_btn)

        user = self.navigator.get_user()
        if user:
            stats_label = QLabel(f"{user.name.upper()} | XP: {user.xp}")
            stats_label.setFont(make_qfont("nav_stats"))
            stats_label.setStyleSheet(
                f"color: {c['accent']}; background: transparent;"
            )
            bar_layout.addWidget(stats_label)

        self._layout.addWidget(bar)
        return bar

    def show_guide(self, topic: str) -> None:
        from neural_speed_academy.screens.base import _show_guide_dialog
        _show_guide_dialog(self, topic)

    def _stop_exercise(self) -> None:
        """Stop the current exercise and return to the dashboard."""
        self._running = False
        for t in self._timers:
            t.stop()
        self._timers.clear()
        self.navigator.finish_exercise()

    def complete(self, result: ExerciseResult) -> bool:
        """Save XP, log history, track personal bests. Returns True if new PB."""
        is_pb = False
        user = self.navigator.get_user()
        if user:
            try:
                user.add_xp(result.xp_gained)
                user.add_history(
                    exercise=result.exercise_name,
                    result=result.score_string(),
                    max_entries=USER_DATA_CONFIG["max_history_entries"],
                    metadata=result.metadata,
                )
                is_pb = user.update_personal_best(
                    result.exercise_name, result.score, result.total,
                    metadata=result.metadata,
                )
                self.navigator.save_user()
            except Exception as e:
                logger.error(f"Failed to save exercise result: {e}")
                QMessageBox.warning(
                    self, "Save Error",
                    "Could not save your progress. Please try again.",
                )
        return is_pb

    def show_result_screen(
        self,
        result: ExerciseResult,
        is_personal_best: bool = False,
        details: str = "",
    ) -> None:
        """Display a standardized result screen."""
        self._play("completion")
        self._clear()
        c = COLORS

        self.add_nav_bar()

        container = QWidget()
        container.setStyleSheet(f"background-color: {c['bg']};")
        cl = QVBoxLayout(container)
        cl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.setSpacing(8)

        title = QLabel("RESULTS")
        title.setFont(make_qfont("header"))
        title.setStyleSheet(f"color: {c['accent']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(title)

        score_lbl = QLabel(f"Score: {result.score_string()}")
        score_lbl.setFont(make_qfont("btn_lg"))
        score_lbl.setStyleSheet(f"color: {c['fg']};")
        score_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(score_lbl)

        if details:
            det = QLabel(details)
            det.setFont(make_qfont("body"))
            det.setStyleSheet(f"color: {c['fg']};")
            det.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cl.addWidget(det)

        xp_lbl = QLabel(f"XP earned: +{result.xp_gained}")
        xp_lbl.setFont(make_qfont("counter"))
        xp_lbl.setStyleSheet(f"color: {c['accent']};")
        xp_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(xp_lbl)

        if is_personal_best:
            pb = QLabel("NEW PERSONAL BEST!")
            pb.setFont(make_qfont("btn_bold"))
            pb.setStyleSheet(f"color: {c['success']};")
            pb.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cl.addWidget(pb)

        cl.addSpacing(15)

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

    def handle_error(self, error: Exception, message: str = "An error occurred") -> None:
        logger.error(f"{self.name} error: {error}")
        QMessageBox.critical(self, "Error", f"{message}\n\nDetails: {error}")
        self.navigator.finish_exercise()

    @abstractmethod
    def start(self, **config) -> None:
        pass
