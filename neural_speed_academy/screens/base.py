"""
Base screen class for PyQt6.
All screens inherit from QWidget and are managed by a QStackedWidget navigator.
"""
from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QDialog, QScrollArea,
)
from PyQt6.QtCore import Qt

from neural_speed_academy.theme import COLORS, make_qfont, font_css

if TYPE_CHECKING:
    from neural_speed_academy.navigation.navigator import Navigator


class BaseScreen(QWidget):
    """Abstract base for all screens. Subclasses implement build()."""

    def __init__(self, navigator: "Navigator", parent: QWidget | None = None):
        super().__init__(parent)
        self.navigator = navigator
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

    def show_screen(self, **kwargs) -> None:
        """Called by the navigator when this screen becomes active."""
        # Clear existing widgets
        while self._layout.count():
            item = self._layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        self.build(**kwargs)

    @abstractmethod
    def build(self, **kwargs) -> None:
        """Build the screen UI. Must be implemented by subclasses."""
        pass

    def add_nav_bar(self) -> QFrame:
        """Add a navigation bar with Back, Training Hub, and Main Menu buttons."""
        c = COLORS
        bar = QFrame()
        bar.setStyleSheet(f"background-color: {c['card']};")
        bar.setFixedHeight(50)
        bar_layout = QHBoxLayout(bar)
        bar_layout.setContentsMargins(10, 8, 10, 8)

        btn_style = (
            f"QPushButton {{ {font_css('btn_sm')} border: none; padding: 2px 8px; "
            f"border-radius: 3px; }}"
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
        """Display a guide popup for the given topic."""
        from neural_speed_academy.config import EXERCISE_GUIDES

        c = COLORS
        title, text = EXERCISE_GUIDES.get(topic, ("INFO", "..."))

        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setFixedSize(700, 600)
        dialog.setStyleSheet(f"background-color: {c['card']};")

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(30, 20, 30, 20)

        title_lbl = QLabel(title)
        title_lbl.setFont(make_qfont("sub"))
        title_lbl.setStyleSheet(f"color: {c['accent']};")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_lbl)

        body_lbl = QLabel(text)
        body_lbl.setFont(make_qfont("body"))
        body_lbl.setStyleSheet(f"color: {c['text_on_card']};")
        body_lbl.setWordWrap(True)
        layout.addWidget(body_lbl, 1)

        close_btn = QPushButton("CLOSE")
        close_btn.setFont(make_qfont("btn_bold"))
        close_btn.setStyleSheet(
            f"background-color: {c['accent']}; color: {c['btn_text']}; "
            f"border: none; padding: 6px 20px; border-radius: 3px;"
        )
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        dialog.exec()


def make_scroll_area(parent_layout: QVBoxLayout) -> tuple[QScrollArea, QWidget, QVBoxLayout]:
    """Create a scrollable area. Returns (scroll_area, content_widget, content_layout)."""
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.Shape.NoFrame)
    scroll.setStyleSheet(f"background-color: {COLORS['bg']};")

    content = QWidget()
    content_layout = QVBoxLayout(content)
    content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
    scroll.setWidget(content)
    parent_layout.addWidget(scroll)
    return scroll, content, content_layout
