"""
Main menu screen — the application entry point.
"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QDialog,
)
from PyQt6.QtCore import Qt

from neural_speed_academy.screens.base import BaseScreen
from neural_speed_academy.theme import COLORS, make_qfont, font_css, btn_css


class MainMenuScreen(BaseScreen):

    def build(self, **kwargs) -> None:
        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")

        container = QWidget()
        container.setStyleSheet(f"background-color: {c['bg']};")
        cl = QVBoxLayout(container)
        cl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.setSpacing(6)

        title = QLabel("NEURAL SPEED ACADEMY")
        title.setFont(make_qfont("title"))
        title.setStyleSheet(f"color: {c['accent']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(title)

        slogan = QLabel("Let your brain process more information in less time")
        slogan.setFont(make_qfont("sub"))
        slogan.setStyleSheet(f"color: {c['muted']};")
        slogan.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addSpacing(30)
        cl.addWidget(slogan)
        cl.addSpacing(20)

        logged_in = self.navigator.current_user is not None
        user = self.navigator.current_user

        buttons: list[tuple[str, str, str, object]] = []

        if logged_in:
            welcome = QLabel(f"Welcome back, {user.name}")
            welcome.setFont(make_qfont("section_header"))
            welcome.setStyleSheet(f"color: {c['fg']};")
            welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cl.addWidget(welcome)
            cl.addSpacing(8)

            buttons.append(
                ("CONTINUE TRAINING", c["accent"], c["btn_text"],
                 lambda: self.navigator.to_dashboard()),
            )
            buttons.append(
                ("SWITCH PROFILE", c["action"], c["btn_text"],
                 lambda: self.navigator.navigate_to("login")),
            )
        else:
            buttons.append(
                ("LOGIN", c["accent"], c["btn_text"],
                 lambda: self.navigator.navigate_to("login")),
            )

        buttons += [
            ("INTRODUCTION", c["action"], c["btn_text"],
             lambda: self.navigator.navigate_to("introduction")),
            ("TRAINING PATHS", c["action"], c["btn_text"],
             lambda: self.navigator.navigate_to("paths")),
            ("SETTINGS", c["card"], c["fg"],
             lambda: self.navigator.navigate_to("settings")),
            ("INFORMATION", c["card"], c["fg"], self._show_info),
            ("QUIT", c["alert"], c["btn_text"], self._quit),
        ]

        for text, bg, fg, callback in buttons:
            btn = QPushButton(text)
            btn.setStyleSheet(btn_css(bg, fg, min_width=300))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(callback)
            cl.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self._layout.addWidget(container, 1)

        # Version label in bottom-right corner
        from neural_speed_academy import __version__
        ver = QLabel(f"v{__version__}")
        ver.setFont(make_qfont("btn_sm"))
        ver.setStyleSheet(f"color: {c['muted']}; background: transparent; padding: 6px 12px;")
        ver.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._layout.addWidget(ver)

    def _show_info(self) -> None:
        c = COLORS
        dialog = QDialog(self)
        dialog.setWindowTitle("About")
        dialog.setFixedSize(580, 380)
        dialog.setStyleSheet(f"background-color: {c['card']};")

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(40, 30, 40, 15)

        title = QLabel("NEURAL SPEED ACADEMY")
        title.setFont(make_qfont("header"))
        title.setStyleSheet(f"color: {c['accent']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setWordWrap(True)
        layout.addWidget(title)

        body = QLabel(
            "A desktop application for speed reading\n"
            "and cognitive training.\n\n"
            "15 exercises across reading, cognition,\n"
            "visual processing, and information retention.\n"
            "16 structured training paths in 5 categories."
        )
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

        close_btn = QPushButton("CLOSE")
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
        msg.setText("Are you sure you want to quit?")
        msg.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        msg.setStyleSheet(
            f"QMessageBox {{ background-color: {c['card']}; }}"
            f"QMessageBox QLabel {{ color: {c['text_on_card']}; }}"
            f"QPushButton {{ background-color: {c['accent']}; "
            f"color: {c['btn_text']}; border: none; "
            f"padding: 6px 20px; border-radius: 3px; }}"
        )
        if msg.exec() == QMessageBox.StandardButton.Yes:
            from PyQt6.QtWidgets import QApplication
            QApplication.quit()
