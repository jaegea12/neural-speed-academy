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
    QMessageBox, QDialog, QScrollArea,
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

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    def _clear(self) -> None:
        """Remove all child widgets and stop timers."""
        self._running = False
        for timer in self._timers:
            timer.stop()
        self._timers.clear()
        while self._layout.count():
            item = self._layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def _after(self, ms: int, callback) -> QTimer:
        """Schedule a callback after ms milliseconds. Returns the timer."""
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(callback)
        timer.start(ms)
        self._timers.append(timer)
        return timer

    def add_nav_bar(self) -> QFrame:
        """Add a navigation bar (same pattern as BaseScreen)."""
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

        menu_btn = QPushButton("Main Menu")
        menu_btn.setStyleSheet(
            btn_style
            + f"QPushButton {{ background-color: {c['card']}; color: {c['fg']}; }}"
            + f"QPushButton:hover {{ background-color: {c['bg']}; }}"
        )
        menu_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        menu_btn.clicked.connect(lambda: self.navigator.navigate_to("main_menu"))
        bar_layout.addWidget(menu_btn)

        bar_layout.addStretch()

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
        from PyQt6.QtGui import QFont
        from neural_speed_academy.config import EXERCISE_GUIDES
        c = COLORS
        guide_title, text = EXERCISE_GUIDES.get(topic, ("INFO", "..."))

        dlg = QDialog(self)
        dlg.setWindowTitle(guide_title)
        dlg.setMinimumSize(720, 500)
        dlg.setStyleSheet(f"background-color: {c['card']};")

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(30, 25, 30, 20)
        layout.setSpacing(12)

        heading = QLabel(guide_title)
        heading.setFont(make_qfont("header"))
        heading.setStyleSheet(f"color: {c['accent']};")
        heading.setWordWrap(True)
        layout.addWidget(heading)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            f"QScrollArea {{ border: none; background: transparent; }}"
            f"QScrollBar:vertical {{ background: {c['card']}; width: 8px; }}"
            f"QScrollBar::handle:vertical {{ background: {c['muted']}; "
            f"border-radius: 4px; min-height: 30px; }}"
            f"QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical "
            f"{{ height: 0; }}"
        )
        body_widget = QWidget()
        body_layout = QVBoxLayout(body_widget)
        body_layout.setContentsMargins(5, 5, 5, 5)

        body = QLabel(text)
        body_font = QFont("Segoe UI", 13)
        body.setFont(body_font)
        body.setStyleSheet(
            f"color: {c['text_on_card']}; line-height: 1.5;"
        )
        body.setWordWrap(True)
        body_layout.addWidget(body)
        body_layout.addStretch()

        scroll.setWidget(body_widget)
        layout.addWidget(scroll, 1)

        close_btn = QPushButton("CLOSE")
        close_btn.setFont(make_qfont("btn_bold"))
        close_btn.setStyleSheet(
            f"background-color: {c['accent']}; color: {c['btn_text']}; "
            f"border: none; padding: 8px 30px; border-radius: 4px;"
        )
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(dlg.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        dlg.exec()

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
                )
                is_pb = user.update_personal_best(
                    result.exercise_name, result.score, result.total,
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
