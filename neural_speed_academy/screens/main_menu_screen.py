"""
Main menu screen — the application entry point.
"""
from __future__ import annotations

import os

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QDialog,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

from neural_speed_academy.screens.base import BaseScreen
from neural_speed_academy.theme import COLORS, make_qfont, btn_css
from neural_speed_academy.i18n import tr


class MainMenuScreen(BaseScreen):

    def build(self, **kwargs) -> None:
        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")

        container = QWidget()
        container.setStyleSheet(f"background-color: {c['bg']};")
        cl = QVBoxLayout(container)
        cl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.setSpacing(0)

        # ── Branding block ──
        cl.addStretch(2)

        # App icon
        icon_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "assets", "icon.png",
        )
        if os.path.exists(icon_path):
            icon_lbl = QLabel()
            pixmap = QPixmap(icon_path).scaled(
                96, 96,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            icon_lbl.setPixmap(pixmap)
            icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_lbl.setStyleSheet("background: transparent;")
            cl.addWidget(icon_lbl)
            cl.addSpacing(10)

        title = QLabel(tr("main.menu.neural_speed_nacademy"))
        title.setFont(make_qfont("title_lg"))
        title.setStyleSheet(f"color: {c['accent']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(title)

        cl.addSpacing(6)

        # Accent line
        line = QWidget()
        line.setFixedSize(120, 2)
        line.setStyleSheet(f"background-color: {c['accent']};")
        cl.addWidget(line, alignment=Qt.AlignmentFlag.AlignCenter)

        cl.addSpacing(14)

        tagline = QLabel(tr("main.menu.let_your_brain_process_more_in"))
        tagline.setFont(make_qfont("tagline"))
        tagline.setStyleSheet(f"color: {c['muted']};")
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(tagline)

        cl.addStretch(1)

        # ── User greeting ──
        logged_in = self.navigator.current_user is not None
        user = self.navigator.current_user

        buttons: list[tuple[str, str, str, object]] = []

        if logged_in:
            welcome = QLabel(tr("main.menu.welcome_back", name=user.name))
            welcome.setFont(make_qfont("section_header"))
            welcome.setStyleSheet(f"color: {c['fg']};")
            welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cl.addWidget(welcome)
            cl.addSpacing(12)

            buttons.append(
                (tr("main.menu.continue_training"), c["accent"], c["btn_text"],
                 lambda: self.navigator.to_dashboard()),
            )
            buttons.append(
                (tr("main.menu.switch_profile"), c["card"], c["text_on_card"],
                 lambda: self.navigator.navigate_to("login")),
            )
        else:
            buttons.append(
                (tr("main.menu.login"), c["accent"], c["btn_text"],
                 lambda: self.navigator.navigate_to("login")),
            )

        buttons += [
            (tr("main.menu.training_paths"), c["accent"], c["btn_text"],
             lambda: self.navigator.navigate_to("paths")),
            (tr("main.menu.introduction"), c["accent"], c["btn_text"],
             lambda: self.navigator.navigate_to("introduction")),
            (tr("main.menu.language"), c["accent"], c["btn_text"],
             lambda: self.navigator.navigate_to("language")),
            (tr("main.menu.settings"), c["muted"], c["bg"],
             lambda: self.navigator.navigate_to("settings")),
            (tr("main.menu.information"), c["muted"], c["bg"], self._show_info),
            (tr("main.menu.quit"), c["alert"], c["btn_text"], self._quit),
        ]

        for text, bg, fg, callback in buttons:
            btn = QPushButton(text)
            btn.setStyleSheet(btn_css(bg, fg, min_width=300))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(callback)
            cl.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
            cl.addSpacing(2)

        cl.addStretch(2)

        self._layout.addWidget(container, 1)

        # Version label in bottom-right corner
        from neural_speed_academy import __version__
        ver = QLabel(f"v{__version__}")
        ver.setFont(make_qfont("btn_sm"))
        ver.setStyleSheet(
            f"color: {c['muted']}; background: transparent; padding: 4px 12px;"
        )
        ver.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._layout.addWidget(ver)

    def _show_info(self) -> None:
        c = COLORS
        dialog = QDialog(self)
        dialog.setWindowTitle(tr("main.menu.about"))
        dialog.setFixedSize(580, 380)
        dialog.setStyleSheet(f"background-color: {c['card']};")

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(40, 30, 40, 15)

        title = QLabel(tr("login.neural_speed_academy"))
        title.setFont(make_qfont("header"))
        title.setStyleSheet(f"color: {c['accent']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setWordWrap(True)
        layout.addWidget(title)

        body = QLabel(tr("main.menu.info_body"))
        body.setFont(make_qfont("body"))
        body.setStyleSheet(f"color: {c['text_on_card']};")
        body.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(body)

        from neural_speed_academy import __version__
        credit = QLabel(
            f"v{__version__}\n\n"
            "Created by Adam Jaeger\n"
            "adam.jaeger@roche.com  |  admjae@proton.me\n\n"
            "Repository setup and GitLab integration\n"
            "by Orlando Pereira\n"
            "\u00a9 2025"
        )
        credit.setFont(make_qfont("btn_sm"))
        credit.setStyleSheet(f"color: {c['muted']};")
        credit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(credit)

        close_btn = QPushButton(tr("nav.close"))
        close_btn.setStyleSheet(
            btn_css(c["accent"], c["btn_text"], padding="6px 20px")
        )
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        dialog.exec()

    def _quit(self) -> None:
        c = COLORS
        msg = QMessageBox(self)
        msg.setWindowTitle("Quit")
        msg.setText(tr("main.menu.are_you_sure_you_want_to_quit"))
        msg.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        msg.setStyleSheet(
            f"QMessageBox {{ background-color: {c['card']}; }}"
            f"QMessageBox QLabel {{ color: {c['text_on_card']}; }}"
            f"QPushButton {{ background-color: {c['accent']}; "
            f"color: {c['btn_text']}; border: 2px solid transparent; "
            f"padding: 6px 20px; border-radius: 3px; }}"
        )
        if msg.exec() == QMessageBox.StandardButton.Yes:
            from PyQt6.QtWidgets import QApplication
            QApplication.quit()
