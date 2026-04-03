"""
Training path selection screen.
"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QMessageBox, QScrollArea,
)
from PyQt6.QtCore import Qt

from neural_speed_academy.screens.base import BaseScreen, make_scroll_area
from neural_speed_academy.theme import COLORS, make_qfont
from neural_speed_academy.config import TRAINING_PATHS, TRAINING_PATH_CATEGORIES
from neural_speed_academy.state import PathProgress


class PathSelectionScreen(BaseScreen):

    def __init__(self, navigator, parent=None):
        super().__init__(navigator, parent)
        self._selected_cat: str = "daily"
        self._cat_buttons: dict[str, QPushButton] = {}
        self._cards_area: QVBoxLayout | None = None

    def build(self, **kwargs) -> None:
        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")
        self.add_nav_bar()

        container = QWidget()
        container.setStyleSheet(f"background-color: {c['bg']};")
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(30, 15, 30, 15)
        main_layout.setSpacing(10)

        title = QLabel("TRAINING PATHS")
        title.setFont(make_qfont("header"))
        title.setStyleSheet(f"color: {c['fg']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        sub = QLabel("Structured programs that combine exercises for specific goals")
        sub.setFont(make_qfont("sub"))
        sub.setStyleSheet(f"color: {c['muted']};")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(sub)

        main_layout.addSpacing(6)

        # Category tab bar
        tab_row = QHBoxLayout()
        tab_row.setSpacing(6)
        tab_row.addStretch()
        self._cat_buttons = {}
        for cat_key, cat_label in TRAINING_PATH_CATEGORIES:
            btn = QPushButton(cat_label)
            btn.setFont(make_qfont("btn_bold"))
            btn.setFixedHeight(38)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(
                lambda _, k=cat_key: self._select_category(k)
            )
            tab_row.addWidget(btn)
            self._cat_buttons[cat_key] = btn
        tab_row.addStretch()
        main_layout.addLayout(tab_row)

        main_layout.addSpacing(6)

        # Cards area (rebuilt on category change)
        self._cards_widget = QWidget()
        self._cards_widget.setStyleSheet(f"background-color: {c['bg']};")
        self._cards_area = QVBoxLayout(self._cards_widget)
        self._cards_area.setContentsMargins(0, 0, 0, 0)
        self._cards_area.setSpacing(10)

        scroll = QScrollArea()
        scroll.setWidget(self._cards_widget)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            f"QScrollArea {{ border: none; background-color: {c['bg']}; }}"
        )
        main_layout.addWidget(scroll, 1)

        # Bottom buttons
        btn_row = QHBoxLayout()
        btn_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_row.setSpacing(12)

        custom_btn = QPushButton("MY CUSTOM PATHS")
        custom_btn.setFont(make_qfont("btn_bold"))
        custom_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['action']}; color: {c['btn_text']}; "
            f"border: none; padding: 8px 20px; border-radius: 4px; }}"
        )
        custom_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        custom_btn.clicked.connect(
            lambda: self.navigator.navigate_to("custom_paths")
        )
        btn_row.addWidget(custom_btn)

        create_btn = QPushButton("+ CREATE NEW")
        create_btn.setFont(make_qfont("btn_bold"))
        create_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['card']}; color: {c['fg']}; "
            f"border: none; padding: 8px 20px; border-radius: 4px; }}"
        )
        create_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        create_btn.clicked.connect(self._create_custom_path)
        btn_row.addWidget(create_btn)

        main_layout.addLayout(btn_row)

        self._layout.addWidget(container, 1)

        # Show initial category
        self._select_category(self._selected_cat)

    def _tab_on(self) -> str:
        c = COLORS
        return (
            f"QPushButton {{ background-color: {c['accent']}; "
            f"color: {c['btn_text']}; border: none; "
            f"padding: 6px 18px; border-radius: 4px; }}"
        )

    def _tab_off(self) -> str:
        c = COLORS
        return (
            f"QPushButton {{ background-color: {c['card']}; "
            f"color: {c['fg']}; border: 1px solid {c['muted']}; "
            f"padding: 6px 18px; border-radius: 4px; }}"
            f"QPushButton:hover {{ background-color: {c['accent']}; "
            f"color: {c['btn_text']}; }}"
        )

    def _select_category(self, cat_key: str) -> None:
        self._selected_cat = cat_key

        # Update tab styles
        for k, btn in self._cat_buttons.items():
            btn.setStyleSheet(
                self._tab_on() if k == cat_key else self._tab_off()
            )

        # Clear cards area
        while self._cards_area.count():
            item = self._cards_area.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
            elif item.layout():
                # Clear nested layout
                sub = item.layout()
                while sub.count():
                    si = sub.takeAt(0)
                    sw = si.widget()
                    if sw:
                        sw.deleteLater()

        # Get paths for this category
        user = self.navigator.get_user()
        paths = [
            (pid, pdata) for pid, pdata in TRAINING_PATHS.items()
            if pdata.get("category") == cat_key
        ]

        c = COLORS

        if not paths:
            empty = QLabel("No paths in this category yet")
            empty.setFont(make_qfont("body"))
            empty.setStyleSheet(f"color: {c['muted']};")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._cards_area.addWidget(empty)
            self._cards_area.addStretch()
            return

        # Render path cards as full-width rows
        for path_id, path_data in paths:
            card = self._make_card(path_id, path_data, user)
            self._cards_area.addWidget(card)

        self._cards_area.addStretch()

    def _make_card(self, path_id, path_data, user) -> QFrame:
        c = COLORS
        card = QFrame()
        card.setStyleSheet(
            f"QFrame {{ background-color: {c['card']}; "
            f"border-radius: 6px; padding: 6px; }}"
        )
        row = QHBoxLayout(card)
        row.setContentsMargins(14, 10, 14, 10)
        row.setSpacing(16)

        # Left: name + description
        info_col = QVBoxLayout()
        info_col.setSpacing(4)

        name = QLabel(path_data["name"])
        name.setFont(make_qfont("btn_bold"))
        name.setStyleSheet(f"color: {c['accent']};")
        info_col.addWidget(name)

        desc = QLabel(path_data["description"])
        desc.setFont(make_qfont("body"))
        desc.setStyleSheet(f"color: {c['text_on_card']};")
        desc.setWordWrap(True)
        info_col.addWidget(desc)

        row.addLayout(info_col, 1)

        # Middle: stats
        steps = path_data["steps"]
        stats_col = QVBoxLayout()
        stats_col.setSpacing(2)
        stats_col.setAlignment(Qt.AlignmentFlag.AlignCenter)

        step_lbl = QLabel(f"{len(steps)} exercises")
        step_lbl.setFont(make_qfont("btn_sm"))
        step_lbl.setStyleSheet(f"color: {c['muted']};")
        step_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stats_col.addWidget(step_lbl)

        time_lbl = QLabel(f"~{len(steps) * 2} min")
        time_lbl.setFont(make_qfont("btn_sm"))
        time_lbl.setStyleSheet(f"color: {c['muted']};")
        time_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stats_col.addWidget(time_lbl)

        row.addLayout(stats_col)

        # Right: progress + button
        action_col = QVBoxLayout()
        action_col.setSpacing(4)
        action_col.setAlignment(Qt.AlignmentFlag.AlignCenter)

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
        prog.setAlignment(Qt.AlignmentFlag.AlignCenter)
        action_col.addWidget(prog)

        btn = QPushButton(btn_text)
        btn.setFont(make_qfont("btn_bold"))
        btn.setFixedWidth(120)
        btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['accent']}; color: {c['btn_text']}; "
            f"border: none; padding: 6px 16px; border-radius: 4px; }}"
        )
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(lambda checked, pid=path_id: self._start_path(pid))
        action_col.addWidget(btn)

        row.addLayout(action_col)
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


class CustomPathsScreen(BaseScreen):
    """Separate screen for viewing and managing custom paths."""

    def build(self, **kwargs) -> None:
        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")
        self.add_nav_bar()

        scroll, content, cl = make_scroll_area(self._layout)
        cl.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        cl.setContentsMargins(40, 15, 40, 15)

        title = QLabel("MY CUSTOM PATHS")
        title.setFont(make_qfont("header"))
        title.setStyleSheet(f"color: {c['accent']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(title)
        cl.addSpacing(10)

        user = self.navigator.get_user()
        if not user or not user.custom_paths:
            empty = QLabel("No custom paths yet.\nCreate one from the Training Paths screen.")
            empty.setFont(make_qfont("body"))
            empty.setStyleSheet(f"color: {c['muted']};")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cl.addWidget(empty)
        else:
            grid = QGridLayout()
            grid.setSpacing(8)
            for i, (cid, cdata) in enumerate(user.custom_paths.items()):
                row, col = i // 3, i % 3
                card = self._make_custom_card(cid, cdata, user)
                grid.addWidget(card, row, col)
            cl.addLayout(grid)

        cl.addSpacing(10)
        create_btn = QPushButton("+ CREATE NEW PATH")
        create_btn.setFont(make_qfont("btn_bold"))
        create_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['accent']}; color: {c['btn_text']}; "
            f"border: none; padding: 6px 20px; border-radius: 4px; }}"
        )
        create_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        create_btn.clicked.connect(
            lambda: self.navigator.navigate_to("path_builder")
        )
        cl.addWidget(create_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    def _make_custom_card(self, path_id, path_data, user) -> QFrame:
        c = COLORS
        card = QFrame()
        card.setFixedWidth(240)
        card.setStyleSheet(
            f"background-color: {c['card']}; border-radius: 6px; padding: 10px;"
        )
        cl = QVBoxLayout(card)
        cl.setSpacing(3)

        name = QLabel(path_data["name"])
        name.setFont(make_qfont("btn_bold"))
        name.setStyleSheet(f"color: {c['accent']};")
        cl.addWidget(name)

        steps = path_data["steps"]
        info = QLabel(f"{len(steps)} exercises")
        info.setFont(make_qfont("btn_sm"))
        info.setStyleSheet(f"color: {c['muted']};")
        cl.addWidget(info)

        btn = QPushButton("START")
        btn.setFont(make_qfont("btn_sm"))
        btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['accent']}; color: {c['btn_text']}; "
            f"border: none; padding: 4px; border-radius: 3px; }}"
        )
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(lambda checked, pid=path_id: self._start(pid))
        cl.addWidget(btn)
        return card

    def _start(self, path_id: str) -> None:
        user = self.navigator.get_user()
        if not user:
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
