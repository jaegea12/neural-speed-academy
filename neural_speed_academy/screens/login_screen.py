"""
Login screen for user authentication.
"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFrame, QMessageBox,
)
from PyQt6.QtCore import Qt

from neural_speed_academy.screens.base import BaseScreen
from neural_speed_academy.theme import COLORS, make_qfont, font_css


class LoginScreen(BaseScreen):

    def build(self, **kwargs) -> None:
        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")

        container = QWidget()
        container.setStyleSheet(f"background-color: {c['bg']};")
        cl = QVBoxLayout(container)
        cl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.setSpacing(8)

        title = QLabel("NEURAL SPEED ACADEMY")
        title.setFont(make_qfont("header"))
        title.setStyleSheet(f"color: {c['fg']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(title)
        cl.addSpacing(15)

        # Existing users
        users = self.navigator.user_repo.list_users()
        if users:
            sel_label = QLabel("SELECT PROFILE")
            sel_label.setFont(make_qfont("section_header"))
            sel_label.setStyleSheet(f"color: {c['accent']};")
            sel_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cl.addWidget(sel_label)

            for uname in users:
                profile = self.navigator.user_repo.get(uname)
                level = (profile.xp // 1000 + 1) if profile else 1

                row = QPushButton(f"  {uname}    Lv.{level}")
                row.setFont(make_qfont("btn_bold"))
                row.setStyleSheet(
                    f"QPushButton {{ background-color: {c['card']}; "
                    f"color: {c['text_on_card']}; border: none; "
                    f"padding: 8px 16px; text-align: left; "
                    f"border-radius: 4px; min-width: 250px; }}"
                    f"QPushButton:hover {{ background-color: {c['accent']}; }}"
                )
                row.setCursor(Qt.CursorShape.PointingHandCursor)
                row.clicked.connect(
                    lambda checked, n=uname: self._login_as(n)
                )
                cl.addWidget(row, alignment=Qt.AlignmentFlag.AlignCenter)

            # Separator
            sep = QFrame()
            sep.setFrameShape(QFrame.Shape.HLine)
            sep.setStyleSheet(f"color: {c['muted']};")
            sep.setFixedWidth(300)
            cl.addSpacing(10)
            cl.addWidget(sep, alignment=Qt.AlignmentFlag.AlignCenter)

            new_label = QLabel("OR CREATE NEW")
            new_label.setFont(make_qfont("section_header"))
            new_label.setStyleSheet(f"color: {c['accent']};")
            new_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cl.addWidget(new_label)

        # Name entry
        from neural_speed_academy.theme import input_css
        self._entry = QLineEdit()
        self._entry.setPlaceholderText("Type your name")
        self._entry.setFont(make_qfont("sub"))
        self._entry.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._entry.setFixedWidth(300)
        self._entry.setStyleSheet(input_css())
        self._entry.returnPressed.connect(self._do_login)
        cl.addWidget(self._entry, alignment=Qt.AlignmentFlag.AlignCenter)
        cl.addSpacing(10)

        start_btn = QPushButton("START TRAINING")
        start_btn.setFont(make_qfont("btn_bold"))
        start_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['accent']}; "
            f"color: {c['btn_text']}; border: none; "
            f"padding: 10px 30px; border-radius: 4px; }}"
        )
        start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        start_btn.clicked.connect(self._do_login)
        cl.addWidget(start_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self._layout.addWidget(container, 1)

    def _login_as(self, name: str) -> None:
        user = self.navigator.user_repo.get_or_create(name)
        self.navigator.set_user(user)
        self.navigator.complete_login()

    def _do_login(self) -> None:
        name = self._entry.text().strip()
        if not name:
            QMessageBox.information(
                self, "Name Required", "Please enter your name to continue."
            )
            return
        user = self.navigator.user_repo.get_or_create(name)
        self.navigator.set_user(user)
        self.navigator.complete_login()
