"""
Training path selection and execution screens.
"""
from __future__ import annotations

import random

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QProgressBar, QScrollArea, QMessageBox,
)
from PyQt6.QtCore import Qt

from neural_speed_academy.screens.base import BaseScreen, make_scroll_area
from neural_speed_academy.theme import COLORS, make_qfont, font_css
from neural_speed_academy.config import TRAINING_PATHS
from neural_speed_academy.state import PathProgress


class PathSelectionScreen(BaseScreen):

    def build(self, **kwargs) -> None:
        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")
        self.add_nav_bar()

        scroll, content, cl = make_scroll_area(self._layout)
        cl.setContentsMargins(40, 20, 40, 20)

        title = QLabel("TRAINING PATHS")
        title.setFont(make_qfont("header"))
        title.setStyleSheet(f"color: {c['accent']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(title)

        sub = QLabel("Structured programs that combine exercises for specific goals")
        sub.setFont(make_qfont("sub"))
        sub.setStyleSheet(f"color: {c['muted']};")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(sub)
        cl.addSpacing(15)

        user = self.navigator.get_user()
        all_paths = list(TRAINING_PATHS.items())
        if user and user.custom_paths:
            for cid, cdata in user.custom_paths.items():
                all_paths.append((cid, cdata))

        grid = QGridLayout()
        grid.setSpacing(10)
        for i, (path_id, path_data) in enumerate(all_paths):
            row, col = i // 3, i % 3
            card = self._make_card(path_id, path_data, user)
            grid.addWidget(card, row, col)
        cl.addLayout(grid)

        cl.addSpacing(15)
        create_btn = QPushButton("+ CREATE CUSTOM PATH")
        create_btn.setFont(make_qfont("btn_bold"))
        create_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['action']}; color: {c['btn_text']}; "
            f"border: none; padding: 8px 24px; border-radius: 4px; }}"
        )
        create_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        create_btn.clicked.connect(self._create_custom_path)
        cl.addWidget(create_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    def _make_card(self, path_id, path_data, user) -> QFrame:
        c = COLORS
        card = QFrame()
        card.setFixedWidth(280)
        card.setStyleSheet(f"background-color: {c['card']}; border-radius: 6px; padding: 15px;")
        cl = QVBoxLayout(card)
        cl.setSpacing(4)

        name = QLabel(path_data["name"])
        name.setFont(make_qfont("section_header"))
        name.setStyleSheet(f"color: {c['accent']};")
        cl.addWidget(name)

        desc = QLabel(path_data["description"])
        desc.setFont(make_qfont("body"))
        desc.setStyleSheet(f"color: {c['text_on_card']};")
        desc.setWordWrap(True)
        cl.addWidget(desc)

        steps = path_data["steps"]
        est = len(steps) * 2
        info = QLabel(f"{len(steps)} exercises  ~{est} min")
        info.setFont(make_qfont("btn_sm"))
        info.setStyleSheet(f"color: {c['muted']};")
        cl.addWidget(info)

        prog_text, btn_text = "Not started", "START"
        if user:
            pp = user.path_progress.get(path_id)
            if pp and not pp.completed:
                prog_text = f"Step {pp.current_step + 1}/{len(steps)}"
                btn_text = "CONTINUE"
            elif pp and pp.completed:
                prog_text = "Completed \u2713"
                btn_text = "RESTART"

        prog = QLabel(prog_text)
        prog.setFont(make_qfont("btn_sm"))
        prog.setStyleSheet(f"color: {c['accent']};")
        cl.addWidget(prog)

        btn = QPushButton(btn_text)
        btn.setFont(make_qfont("btn_bold"))
        btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['accent']}; color: {c['btn_text']}; "
            f"border: none; padding: 6px; border-radius: 3px; }}"
        )
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(lambda checked, pid=path_id: self._start_path(pid))
        cl.addWidget(btn)
        return card

    def _create_custom_path(self) -> None:
        user = self.navigator.get_user()
        if not user:
            QMessageBox.information(self, "Login Required", "Please log in first.")
            self.navigator.require_login("paths")
            return
        self.navigator.navigate_to("path_builder")

    def _start_path(self, path_id: str) -> None:
        user = self.navigator.get_user()
        if not user:
            QMessageBox.information(self, "Login Required", "Please log in first.")
            self.navigator.require_login("paths")
            return
        pp = user.path_progress.get(path_id)
        if pp and pp.completed:
            pp.current_step = 0
            pp.completed = False
            pp.start_xp = user.xp
        elif not pp:
            pp = PathProgress(path_id=path_id, start_xp=user.xp)
            user.path_progress[path_id] = pp
        user.active_path = path_id
        self.navigator.user_repo.save(user)
        self.navigator.navigate_to("path_session")
