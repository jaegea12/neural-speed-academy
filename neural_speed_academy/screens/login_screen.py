"""
Login screen for user authentication.
"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFrame, QMessageBox,
)
from PyQt6.QtCore import Qt

from neural_speed_academy.screens.base import BaseScreen
from neural_speed_academy.theme import COLORS, make_qfont, font_css, btn_css, input_css

from PyQt6.QtWidgets import QHBoxLayout

import hashlib


def _hash_pw(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


class LoginScreen(BaseScreen):

    def build(self, **kwargs) -> None:
        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")

        # Back button at top-left
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(12, 8, 12, 0)
        back_btn = QPushButton("\u2190 BACK")
        back_btn.setStyleSheet(
            btn_css(c["card"], c["fg"], padding="6px 16px", font_key="btn_sm")
        )
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(self.navigator.go_back)
        top_bar.addWidget(back_btn)
        top_bar.addStretch()
        self._layout.addLayout(top_bar)

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
                has_pw = bool(profile and profile.password_hash)
                label = f"  {uname}    Lv.{level}"
                if has_pw:
                    label += "  \U0001f512"

                row_widget = QFrame()
                row_widget.setStyleSheet("background: transparent;")
                row_layout = QHBoxLayout(row_widget)
                row_layout.setContentsMargins(0, 0, 0, 0)
                row_layout.setSpacing(4)

                login_btn = QPushButton(label)
                login_btn.setFont(make_qfont("btn_bold"))
                login_btn.setStyleSheet(
                    btn_css(c["card"], c["text_on_card"],
                            padding="8px 16px", min_width=250)
                )
                login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                login_btn.clicked.connect(
                    lambda checked, n=uname: self._login_as(n)
                )
                row_layout.addWidget(login_btn)

                del_btn = QPushButton("\u2716")
                del_btn.setFixedSize(32, 32)
                del_btn.setStyleSheet(
                    f"QPushButton {{ background-color: transparent; "
                    f"color: {c['muted']}; border: none; font-size: 14px; }}"
                    f"QPushButton:hover {{ color: {c['alert']}; }}"
                )
                del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                del_btn.setToolTip(f"Delete profile: {uname}")
                del_btn.setAccessibleName(f"Delete profile {uname}")
                del_btn.clicked.connect(
                    lambda checked, n=uname: self._confirm_delete(n)
                )
                row_layout.addWidget(del_btn)

                cl.addWidget(row_widget, alignment=Qt.AlignmentFlag.AlignCenter)

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
        self._entry = QLineEdit()
        self._entry.setPlaceholderText("Type your name")
        self._entry.setFont(make_qfont("sub"))
        self._entry.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._entry.setFixedWidth(300)
        self._entry.setStyleSheet(input_css())
        self._entry.returnPressed.connect(self._do_login)
        cl.addWidget(self._entry, alignment=Qt.AlignmentFlag.AlignCenter)

        # Password entry (optional for new profiles)
        self._pw_entry = QLineEdit()
        self._pw_entry.setPlaceholderText("Password (optional)")
        self._pw_entry.setFont(make_qfont("sub"))
        self._pw_entry.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._pw_entry.setFixedWidth(300)
        self._pw_entry.setEchoMode(QLineEdit.EchoMode.Password)
        self._pw_entry.setStyleSheet(input_css())
        self._pw_entry.returnPressed.connect(self._do_login)
        cl.addWidget(self._pw_entry, alignment=Qt.AlignmentFlag.AlignCenter)

        cl.addSpacing(10)

        start_btn = QPushButton("CREATE & START")
        start_btn.setStyleSheet(
            btn_css(c["accent"], c["btn_text"], padding="10px 30px")
        )
        start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        start_btn.clicked.connect(self._do_login)
        cl.addWidget(start_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self._layout.addWidget(container, 1)

    def _confirm_delete(self, name: str) -> None:
        """Ask for confirmation before deleting a profile."""
        c = COLORS
        msg = QMessageBox(self)
        msg.setWindowTitle("Delete Profile")
        msg.setText(f"Delete profile \"{name}\"?\n\nAll progress, history, and XP will be lost.")
        msg.setStyleSheet(
            f"QMessageBox {{ background-color: {c['card']}; color: {c['fg']}; }}"
            f"QLabel {{ color: {c['fg']}; }}"
            f"QPushButton {{ background-color: {c['accent']}; color: {c['btn_text']}; "
            f"border: none; padding: 6px 20px; border-radius: 4px; min-width: 80px; }}"
        )
        msg.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        msg.setDefaultButton(QMessageBox.StandardButton.No)
        if msg.exec() == QMessageBox.StandardButton.Yes:
            # If deleting the currently logged-in user, log out
            current = self.navigator.get_user()
            if current and current.name == name:
                self.navigator.current_user = None
            self.navigator.user_repo.delete(name)
            # Rebuild the login screen to reflect the change
            self.show_screen()

    def _login_as(self, name: str) -> None:
        profile = self.navigator.user_repo.get(name)
        if not profile:
            return
        if profile.password_hash:
            self._prompt_password(profile)
        else:
            self.navigator.set_user(profile)
            self.navigator.complete_login()

    def _prompt_password(self, profile) -> None:
        """Show a password dialog for a protected profile."""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout as DVBox
        c = COLORS

        dlg = QDialog(self)
        dlg.setWindowTitle(f"Login — {profile.name}")
        dlg.setFixedSize(350, 180)
        dlg.setStyleSheet(f"background-color: {c['card']};")

        dl = DVBox(dlg)
        dl.setContentsMargins(25, 20, 25, 15)
        dl.setSpacing(10)

        lbl = QLabel(f"Enter password for {profile.name}")
        lbl.setFont(make_qfont("body"))
        lbl.setStyleSheet(f"color: {c['text_on_card']};")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dl.addWidget(lbl)

        pw_field = QLineEdit()
        pw_field.setEchoMode(QLineEdit.EchoMode.Password)
        pw_field.setFont(make_qfont("sub"))
        pw_field.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pw_field.setStyleSheet(input_css())
        dl.addWidget(pw_field)

        def try_login():
            if _hash_pw(pw_field.text()) == profile.password_hash:
                dlg.accept()
                self.navigator.set_user(profile)
                self.navigator.complete_login()
            else:
                lbl.setText("Wrong password. Try again.")
                lbl.setStyleSheet(f"color: {c['alert']};")
                pw_field.clear()

        pw_field.returnPressed.connect(try_login)

        ok_btn = QPushButton("LOGIN")
        ok_btn.setStyleSheet(
            btn_css(c["accent"], c["btn_text"], padding="6px 20px")
        )
        ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_btn.clicked.connect(try_login)
        dl.addWidget(ok_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        dlg.exec()

    def _do_login(self) -> None:
        name = self._entry.text().strip()
        if not name:
            QMessageBox.information(
                self, "Name Required", "Please enter your name to continue."
            )
            return
        password = self._pw_entry.text()
        user = self.navigator.user_repo.get_or_create(name)
        # Set password if creating new profile and password provided
        if not user.password_hash and password:
            user.password_hash = _hash_pw(password)
            self.navigator.user_repo.save(user)
        elif user.password_hash:
            # Existing user with password — verify
            if _hash_pw(password) != user.password_hash:
                QMessageBox.warning(
                    self, "Wrong Password",
                    "The password does not match this profile."
                )
                return
        self.navigator.set_user(user)
        self.navigator.complete_login()
