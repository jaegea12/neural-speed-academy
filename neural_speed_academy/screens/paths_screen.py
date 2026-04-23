"""
Training path selection screen.
"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QScrollArea, QMessageBox,
)
from PyQt6.QtCore import Qt

from neural_speed_academy.screens.base import BaseScreen, make_scroll_area
from neural_speed_academy.theme import COLORS, make_qfont, btn_css
from neural_speed_academy.config import TRAINING_PATHS, TRAINING_PATH_CATEGORIES
from neural_speed_academy.state import PathProgress
from neural_speed_academy.i18n import tr


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

        title = QLabel(tr("paths.training_paths"))
        title.setFont(make_qfont("header"))
        title.setStyleSheet(f"color: {c['fg']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        sub = QLabel(tr("paths.structured_programs_that_combi"))
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
        _cat_tr = {
            "daily": "paths.cat.daily",
            "reading": "paths.cat.reading",
            "cognitive": "paths.cat.cognitive",
            "visual": "paths.cat.visual",
            "info": "paths.cat.info",
        }
        for cat_key, cat_label in TRAINING_PATH_CATEGORIES:
            display = tr(_cat_tr[cat_key]) if cat_key in _cat_tr else cat_label
            btn = QPushButton(display)
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

        custom_btn = QPushButton(tr("paths.my_custom_paths"))
        custom_btn.setStyleSheet(
            btn_css(c["action"], c["btn_text"], padding="8px 20px")
        )
        custom_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        custom_btn.clicked.connect(
            lambda: self.navigator.navigate_to("custom_paths")
        )
        btn_row.addWidget(custom_btn)

        create_btn = QPushButton(tr("paths.create_new"))
        create_btn.setStyleSheet(
            btn_css(c["card"], c["fg"], padding="8px 20px")
        )
        create_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        create_btn.clicked.connect(self._create_custom_path)
        btn_row.addWidget(create_btn)

        main_layout.addLayout(btn_row)

        self._layout.addWidget(container, 1)

        # Show initial category
        self._select_category(self._selected_cat)

    def _tab_on(self) -> str:
        return btn_css(COLORS["accent"], COLORS["btn_text"], padding="6px 18px")

    def _tab_off(self) -> str:
        return btn_css(COLORS["card"], COLORS["fg"], padding="6px 18px")

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
            empty = QLabel(tr("paths.no_paths_in_this_category_yet"))
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
        btn.setFixedWidth(120)
        btn.setStyleSheet(
            btn_css(c["accent"], c["btn_text"], padding="6px 16px")
        )
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(lambda checked, pid=path_id: self._start_path(pid))
        action_col.addWidget(btn)

        copy_btn = QPushButton(tr("paths.copy"))
        copy_btn.setFixedWidth(120)
        copy_btn.setStyleSheet(
            btn_css(c["card"], c["fg"], padding="4px 12px",
                    radius=3, font_key="btn_sm")
        )
        copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        copy_btn.clicked.connect(
            lambda checked, pid=path_id: self._copy_path(pid)
        )
        action_col.addWidget(copy_btn)

        row.addLayout(action_col)
        return card

    def _copy_path(self, path_id: str) -> None:
        user = self.navigator.get_user()
        if not user:
            self.navigator.require_login("paths")
            return
        self.navigator.navigate_to("path_builder", copy_from=path_id)

    def _create_custom_path(self) -> None:
        user = self.navigator.get_user()
        if not user:
            self.navigator.require_login("paths")
            return
        self.navigator.navigate_to("path_builder")

    def _start_path(self, path_id: str) -> None:
        user = self.navigator.get_user()
        if not user:
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

        title = QLabel(tr("paths.my_custom_paths"))
        title.setFont(make_qfont("header"))
        title.setStyleSheet(f"color: {c['accent']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(title)
        cl.addSpacing(10)

        user = self.navigator.get_user()
        if not user or not user.custom_paths:
            empty = QLabel(tr("paths.no_custom_paths_yet_ncreate_on"))
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
        create_btn = QPushButton(tr("paths.create_new_path"))
        create_btn.setStyleSheet(
            btn_css(c["accent"], c["btn_text"], padding="6px 20px")
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

        start_btn = QPushButton(tr("mot.start"))
        start_btn.setStyleSheet(
            btn_css(c["accent"], c["btn_text"], padding="4px", radius=3,
                    font_key="btn_sm")
        )
        start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        start_btn.clicked.connect(
            lambda checked, pid=path_id: self._start(pid)
        )
        cl.addWidget(start_btn)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(4)

        edit_btn = QPushButton(tr("paths.edit"))
        edit_btn.setStyleSheet(
            btn_css(c["card"], c["fg"], padding="3px", radius=3,
                    font_key="btn_sm")
        )
        edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_btn.clicked.connect(
            lambda checked, pid=path_id: self._edit_path(pid)
        )
        btn_row.addWidget(edit_btn)

        del_btn = QPushButton(tr("paths.delete"))
        del_btn.setStyleSheet(
            btn_css(c["card"], c["alert"], padding="3px", radius=3,
                    font_key="btn_sm")
        )
        del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        del_btn.clicked.connect(
            lambda checked, pid=path_id: self._delete_path(pid)
        )
        btn_row.addWidget(del_btn)

        cl.addLayout(btn_row)
        return card

    def _edit_path(self, path_id: str) -> None:
        self.navigator.navigate_to("path_builder", edit_path_id=path_id)

    def _delete_path(self, path_id: str) -> None:
        user = self.navigator.get_user()
        if not user:
            return
        reply = QMessageBox.question(
            self, tr("paths.delete_confirm_title"),
            tr("paths.delete_confirm_body"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        user.custom_paths.pop(path_id, None)
        user.path_progress.pop(path_id, None)
        if user.active_path == path_id:
            user.active_path = None
        self.navigator.user_repo.save(user)
        self.navigator.navigate_to("custom_paths")

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
