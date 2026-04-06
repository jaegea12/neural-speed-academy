"""
Language selection screen with flag indicators.
"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
)
from PyQt6.QtCore import Qt

from neural_speed_academy.screens.base import BaseScreen
from neural_speed_academy.theme import COLORS, make_qfont, btn_css, theme_manager
from neural_speed_academy.i18n import tr, available_locales, load_locale


# Flag emoji + native name for each supported locale
_LOCALE_FLAGS: dict[str, str] = {
    "en": "\U0001f1ec\U0001f1e7",  # 🇬🇧
    "de": "\U0001f1e9\U0001f1ea",  # 🇩🇪
    "fr": "\U0001f1eb\U0001f1f7",  # 🇫🇷
    "es": "\U0001f1ea\U0001f1f8",  # 🇪🇸
    "it": "\U0001f1ee\U0001f1f9",  # 🇮🇹
    "pt": "\U0001f1e7\U0001f1f7",  # 🇧🇷
    "nl": "\U0001f1f3\U0001f1f1",  # 🇳🇱
    "ja": "\U0001f1ef\U0001f1f5",  # 🇯🇵
    "zh": "\U0001f1e8\U0001f1f3",  # 🇨🇳
    "ko": "\U0001f1f0\U0001f1f7",  # 🇰🇷
}


class LanguageScreen(BaseScreen):

    def build(self, **kwargs) -> None:
        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")
        self.add_nav_bar()

        container = QWidget()
        container.setStyleSheet(f"background-color: {c['bg']};")
        cl = QVBoxLayout(container)
        cl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.setSpacing(0)

        cl.addStretch(2)

        title = QLabel(tr("language.select_language"))
        title.setFont(make_qfont("header"))
        title.setStyleSheet(f"color: {c['accent']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(title)

        cl.addSpacing(8)

        subtitle = QLabel(tr("language.subtitle"))
        subtitle.setFont(make_qfont("body"))
        subtitle.setStyleSheet(f"color: {c['muted']};")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(subtitle)

        cl.addSpacing(30)

        # Language buttons
        current = theme_manager.locale
        locales = available_locales()

        for code, name in locales.items():
            flag = _LOCALE_FLAGS.get(code, "")
            is_active = code == current

            btn_frame = QFrame()
            btn_frame.setFixedWidth(360)
            btn_frame.setStyleSheet(
                f"background-color: {c['card'] if is_active else 'transparent'}; "
                f"border: 2px solid {c['accent'] if is_active else 'transparent'}; "
                f"border-radius: 8px; padding: 4px;"
            )
            row = QHBoxLayout(btn_frame)
            row.setContentsMargins(16, 10, 16, 10)
            row.setSpacing(16)

            flag_lbl = QLabel(flag)
            flag_lbl.setFont(make_qfont("title_lg"))
            flag_lbl.setStyleSheet("background: transparent;")
            flag_lbl.setFixedWidth(48)
            flag_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            row.addWidget(flag_lbl)

            name_lbl = QLabel(name)
            name_lbl.setFont(make_qfont("section_header" if is_active else "btn"))
            name_lbl.setStyleSheet(
                f"color: {c['accent'] if is_active else c['fg']}; "
                f"background: transparent;"
            )
            row.addWidget(name_lbl)

            row.addStretch()

            if is_active:
                check = QLabel("\u2713")
                check.setFont(make_qfont("section_header"))
                check.setStyleSheet(
                    f"color: {c['accent']}; background: transparent;"
                )
                row.addWidget(check)

            btn_frame.setCursor(Qt.CursorShape.PointingHandCursor)
            # Use mousePressEvent via an event filter
            btn_frame.mousePressEvent = self._make_select_handler(code)

            cl.addWidget(btn_frame, alignment=Qt.AlignmentFlag.AlignCenter)
            cl.addSpacing(6)

        cl.addStretch(3)

        self._layout.addWidget(container, 1)

    def _make_select_handler(self, code: str):
        def handler(event):
            if code != theme_manager.locale:
                theme_manager.locale = code
                theme_manager.save()
                self.show_screen()
        return handler
