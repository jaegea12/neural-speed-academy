"""
Language selection screen.
"""
from __future__ import annotations

import os

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

from neural_speed_academy.screens.base import BaseScreen
from neural_speed_academy.theme import COLORS, make_qfont, theme_manager
from neural_speed_academy.i18n import tr, available_locales

_FLAGS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "assets", "flags",
)


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
            is_active = code == current

            btn_frame = QFrame()
            btn_frame.setFixedWidth(360)
            if is_active:
                btn_frame.setStyleSheet(
                    f"background-color: {c['card']}; "
                    f"border: 2px solid {c['accent']}; "
                    f"border-radius: 8px;"
                )
            else:
                btn_frame.setStyleSheet(
                    f"background-color: transparent; "
                    f"border: 2px solid {c['muted']}; "
                    f"border-radius: 8px;"
                )

            row = QHBoxLayout(btn_frame)
            row.setContentsMargins(16, 10, 16, 10)
            row.setSpacing(16)

            # Flag image or code badge fallback
            flag_path = os.path.join(_FLAGS_DIR, f"{code}.png")
            if os.path.exists(flag_path):
                flag_lbl = QLabel()
                pixmap = QPixmap(flag_path).scaled(
                    36, 24,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                flag_lbl.setPixmap(pixmap)
                flag_lbl.setFixedSize(44, 32)
                flag_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                flag_lbl.setStyleSheet("background: transparent; border: none;")
                row.addWidget(flag_lbl)
            else:
                badge = QLabel(code.upper())
                badge.setFont(make_qfont("btn_bold"))
                badge.setFixedSize(44, 32)
                badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
                if is_active:
                    badge.setStyleSheet(
                        f"background-color: {c['accent']}; "
                        f"color: {c['btn_text']}; "
                        f"border: none; border-radius: 4px;"
                    )
                else:
                    badge.setStyleSheet(
                        f"background-color: {c['muted']}; "
                        f"color: {c['bg']}; "
                        f"border: none; border-radius: 4px;"
                    )
                row.addWidget(badge)

            # Language name
            name_lbl = QLabel(name)
            name_lbl.setFont(make_qfont("section_header" if is_active else "btn"))
            name_lbl.setStyleSheet(
                f"color: {c['accent'] if is_active else c['fg']}; "
                f"background: transparent; border: none;"
            )
            row.addWidget(name_lbl)

            row.addStretch()

            if is_active:
                check = QLabel("\u2713")
                check.setFont(make_qfont("section_header"))
                check.setStyleSheet(
                    f"color: {c['accent']}; background: transparent; border: none;"
                )
                row.addWidget(check)

            btn_frame.setCursor(Qt.CursorShape.PointingHandCursor)
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
