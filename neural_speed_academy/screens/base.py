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

from neural_speed_academy.theme import COLORS, make_qfont, font_css, screen_metrics

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

    def add_nav_bar(self, intercept_back=None) -> QFrame:
        """Add a navigation bar with Back, Training Hub, and Main Menu buttons.

        Args:
            intercept_back: Optional callable returning bool. If provided, called
                before navigating away. Navigation proceeds only if it returns True.
        """
        c = COLORS
        bar = QFrame()
        bar.setStyleSheet(f"background-color: {c['card']};")
        bar.setFixedHeight(screen_metrics.nav_bar_h)
        bar_layout = QHBoxLayout(bar)
        bar_layout.setContentsMargins(12, 6, 12, 6)
        bar_layout.setSpacing(6)

        nav_style = (
            f"QPushButton {{ {font_css('btn_sm')} border: none; "
            f"padding: 6px 16px; border-radius: 4px; }}"
        )

        def _guarded_nav(action):
            """Wrap a navigation action with the intercept check."""
            if intercept_back and not intercept_back():
                return
            action()

        back_btn = QPushButton("\u2190 Back")
        back_btn.setStyleSheet(
            nav_style
            + f"QPushButton {{ background-color: {c['card']}; color: {c['fg']}; }}"
            + f"QPushButton:hover {{ background-color: {c['bg']}; }}"
        )
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(lambda: _guarded_nav(self.navigator.go_back))
        bar_layout.addWidget(back_btn)

        hub_btn = QPushButton("Training Hub")
        hub_btn.setStyleSheet(
            nav_style
            + f"QPushButton {{ background-color: {c['accent']}; color: {c['btn_text']}; }}"
        )
        hub_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        hub_btn.clicked.connect(lambda: _guarded_nav(self.navigator.to_dashboard))
        bar_layout.addWidget(hub_btn)

        menu_btn = QPushButton("Main Menu")
        menu_btn.setStyleSheet(
            nav_style
            + f"QPushButton {{ background-color: {c['card']}; color: {c['fg']}; }}"
            + f"QPushButton:hover {{ background-color: {c['bg']}; }}"
        )
        menu_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        menu_btn.clicked.connect(lambda: _guarded_nav(lambda: self.navigator.navigate_to("main_menu")))
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
        """Display a guide popup for the given topic, sized to fit content."""
        _show_guide_dialog(self, topic)


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


def _show_guide_dialog(parent: QWidget, topic: str) -> None:
    """Show a guide dialog sized to fit its content, up to 80% screen height."""
    from PyQt6.QtGui import QFont, QFontMetrics
    from PyQt6.QtWidgets import QApplication
    from neural_speed_academy.config import EXERCISE_GUIDES

    c = COLORS
    guide_title, text = EXERCISE_GUIDES.get(topic, ("INFO", "..."))

    dlg = QDialog(parent)
    dlg.setWindowTitle(guide_title)
    dlg.setStyleSheet(f"background-color: {c['card']};")

    layout = QVBoxLayout(dlg)
    layout.setContentsMargins(30, 25, 30, 20)
    layout.setSpacing(12)

    heading = QLabel(guide_title)
    heading.setFont(make_qfont("header"))
    heading.setStyleSheet(f"color: {c['accent']};")
    heading.setWordWrap(True)
    layout.addWidget(heading)

    body = QLabel(text)
    body_font = QFont("Segoe UI", 13)
    body.setFont(body_font)
    body.setStyleSheet(f"color: {c['text_on_card']}; line-height: 1.5;")
    body.setWordWrap(True)

    # Compute ideal dialog width and body height for the text
    dialog_w = 720
    body_margin = 30 + 30 + 5 + 5  # dialog margins + body padding
    avail_text_w = dialog_w - body_margin
    fm = QFontMetrics(body_font)
    body_rect = fm.boundingRect(
        0, 0, avail_text_w, 0,
        int(Qt.TextFlag.TextWordWrap), text,
    )
    heading_h = QFontMetrics(make_qfont("header")).height() + 20

    # Total content height: heading + spacing + body + close button area
    content_h = heading_h + 12 + body_rect.height() + 60 + 50
    # Cap at 80% of screen height
    screen = QApplication.primaryScreen()
    max_h = int(screen.availableGeometry().height() * 0.8) if screen else 800

    if content_h <= max_h:
        # Content fits — no scroll needed
        layout.addWidget(body)
        dlg.setFixedSize(dialog_w, content_h)
    else:
        # Content too tall — use scroll area
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
        body_layout.addWidget(body)
        body_layout.addStretch()
        scroll.setWidget(body_widget)
        layout.addWidget(scroll, 1)
        dlg.setFixedSize(dialog_w, max_h)

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
