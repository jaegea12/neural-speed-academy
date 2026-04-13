"""
Training hub dashboard.
"""
from __future__ import annotations

from typing import Callable

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QGridLayout, QProgressBar, QScrollArea,
)
from PyQt6.QtCore import Qt

from neural_speed_academy.screens.base import BaseScreen
from neural_speed_academy.theme import COLORS, make_qfont, btn_css
from neural_speed_academy.i18n import tr


class DashboardScreen(BaseScreen):


    def __init__(self, navigator, exercise_callbacks: dict[str, Callable],
                 parent: QWidget | None = None):
        super().__init__(navigator, parent)
        self.exercise_callbacks = exercise_callbacks

    def build(self, **kwargs) -> None:
        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")

        # Header bar
        header = QFrame()
        header.setStyleSheet(f"background-color: {c['card']};")
        header.setFixedHeight(60)
        hl = QHBoxLayout(header)
        title = QLabel(tr("dashboard.training_hub"))
        title.setFont(make_qfont("header"))
        title.setStyleSheet(f"color: {c['text_on_card']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hl.addWidget(title)
        self._layout.addWidget(header)

        # Scrollable main content (vertical only)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        scroll.setStyleSheet(
            f"QScrollArea {{ background-color: {c['bg']}; border: 2px solid transparent; }}"
            f"QScrollBar:vertical {{ background: {c['card']}; width: 8px; }}"
            f"QScrollBar::handle:vertical {{ background: {c['muted']}; "
            f"border-radius: 4px; min-height: 30px; }}"
            f"QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical "
            f"{{ height: 0; }}"
        )

        content = QWidget()
        content.setStyleSheet(f"background-color: {c['bg']};")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(60, 12, 60, 12)
        cl.setSpacing(8)

        self._build_user_card(cl)
        self._build_onboarding(cl)
        self._build_action_bar(cl)
        self._build_continue_button(cl)
        self._build_personal_bests(cl)

        # Eye Priming — standalone warmup button above exercise grid
        c_priming = COLORS
        warmup_btn = QPushButton(tr("dashboard.eye_warmup"))
        warmup_btn.setMaximumWidth(250)
        warmup_btn.setStyleSheet(
            btn_css(c_priming["priming"], c_priming["btn_text"],
                    padding="12px", font_key="btn_bold")
        )
        warmup_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        warmup_btn.clicked.connect(self._cb("menu_priming"))
        cl.addWidget(warmup_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        cl.addSpacing(4)

        # Exercise grid — three columns
        grid = QGridLayout()
        grid.setSpacing(8)

        self._create_section(grid, tr("dashboard.cat.perception"), 0, [
            (tr("dashboard.ex.flash_numbers"), self._cb("menu_flash")),
            (tr("dashboard.ex.word_drills"), self._cb("menu_words")),
            (tr("dashboard.ex.eyespan"), self._cb("menu_eyespan")),
            (tr("dashboard.ex.schulte"), self._cb("menu_schulte")),
            (tr("dashboard.ex.peripheral_flash"), self._cb("menu_peripheral_flash")),
        ])
        self._create_section(grid, tr("dashboard.cat.cognition"), 1, [
            (tr("dashboard.ex.sequence_memory"), self._cb("menu_sequence_memory")),
            (tr("dashboard.ex.rapid_decision"), self._cb("menu_rapid_decision")),
            (tr("dashboard.ex.mot"), self._cb("menu_mot")),
            (tr("dashboard.ex.split_attention"), self._cb("menu_split_attention")),
            (tr("dashboard.ex.reaction_time"), self._cb("menu_reaction_time")),
        ])
        self._create_section(grid, tr("dashboard.cat.reading"), 2, [
            (tr("dashboard.ex.pacer"), self._cb("setup_pacer")),
            (tr("dashboard.ex.rsvp"), self._cb("setup_rsvp")),
            (tr("dashboard.ex.chunking"), self._cb("setup_chunking")),
            (tr("dashboard.ex.spaced_repetition"), self._cb("start_sr")),
            (tr("dashboard.ex.slide_processing"), self._cb("menu_slide_processing")),
        ])
        cl.addLayout(grid)
        cl.addStretch()

        scroll.setWidget(content)
        self._layout.addWidget(scroll, 1)

    # ── User card ──

    def _build_user_card(self, layout: QVBoxLayout) -> None:
        user = self.navigator.get_user()
        if not user:
            return
        c = COLORS

        card = QFrame()
        card.setStyleSheet(
            f"background-color: {c['card']}; border-radius: 6px; "
            f"padding: 8px 20px;"
        )
        cl = QHBoxLayout(card)

        level = user.xp // 1000 + 1
        info = QLabel(tr("dashboard.user_info",
            name=user.name.upper(), level=level,
            streak=user.streak))
        info.setFont(make_qfont("btn_sm"))
        info.setStyleSheet(f"color: {c['text_on_card']};")
        cl.addWidget(info)
        cl.addStretch()

        last_text = tr("dashboard.no_sessions_yet")
        if user.history:
            last = user.history[0]
            last_text = tr("dashboard.last_session_info",
                exercise=last.exercise, result=last.result,
                timestamp=last.timestamp)
        last_lbl = QLabel(last_text)
        last_lbl.setFont(make_qfont("btn_sm"))
        last_lbl.setStyleSheet(f"color: {c['muted']};")
        cl.addWidget(last_lbl)
        layout.addWidget(card)

        # XP bar
        xp_in_level = user.xp % 1000
        bar_row = QHBoxLayout()
        progress = QProgressBar()
        progress.setRange(0, 1000)
        progress.setValue(xp_in_level)
        progress.setFixedHeight(8)
        progress.setTextVisible(False)
        progress.setStyleSheet(
            f"QProgressBar {{ background-color: {c['card']}; "
            f"border: 2px solid transparent; border-radius: 4px; }}"
            f"QProgressBar::chunk {{ background-color: {c['accent']}; "
            f"border-radius: 4px; }}"
        )
        bar_row.addWidget(progress)

        xp_label = QLabel(tr("stats.xp_to_next", current=xp_in_level, level=level + 1))
        xp_label.setFont(make_qfont("btn_sm"))
        xp_label.setStyleSheet(f"color: {c['muted']};")
        bar_row.addWidget(xp_label)
        layout.addLayout(bar_row)

    # ── Onboarding ──

    def _build_onboarding(self, layout: QVBoxLayout) -> None:
        user = self.navigator.get_user()
        if not user or user.history:
            return
        c = COLORS

        banner = QFrame()
        banner.setStyleSheet(
            f"background-color: {c['accent']}; border-radius: 6px; "
            f"padding: 12px 20px;"
        )
        bl = QHBoxLayout(banner)

        welcome = QLabel(tr("dashboard.welcome_new_to_speed_reading"))
        welcome.setFont(make_qfont("btn_bold"))
        welcome.setStyleSheet(f"color: {c['btn_text']};")
        bl.addWidget(welcome)
        bl.addStretch()

        start_btn = QPushButton(tr("dashboard.start_foundation_path"))
        start_btn.setStyleSheet(
            btn_css(c["btn_text"], c["accent"], padding="4px 12px", radius=3)
        )
        start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        start_btn.clicked.connect(self._start_foundation)
        bl.addWidget(start_btn)
        layout.addWidget(banner)

    def _start_foundation(self) -> None:
        from neural_speed_academy.config import TRAINING_PATHS
        from neural_speed_academy.state import PathProgress

        user = self.navigator.get_user()
        if user and "foundation" in TRAINING_PATHS:
            if "foundation" not in user.path_progress:
                user.path_progress["foundation"] = PathProgress(
                    path_id="foundation", current_step=0, completed=False,
                    start_xp=user.xp,
                )
            user.active_path = "foundation"
            self.navigator.save_user()
            self.navigator.navigate_to("path_session")

    # ── Action bar ──

    def _build_action_bar(self, layout: QVBoxLayout) -> None:
        c = COLORS
        bar = QHBoxLayout()
        bar.setSpacing(8)

        action_style = btn_css(c["action"], c["btn_text"], padding="8px 24px")
        exit_style = btn_css(c["card"], c["fg"], padding="8px 24px")

        # Left: forward navigation
        for label, cb_name in [
            (tr("dashboard.nav.training_paths"), "show_paths"),
            (tr("dashboard.nav.stats_history"), "show_stats"),
        ]:
            btn = QPushButton(label)
            btn.setStyleSheet(action_style)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(self._cb(cb_name))
            bar.addWidget(btn)

        bar.addStretch()

        # Right: exit actions
        menu_btn = QPushButton(tr("nav.main_menu"))
        menu_btn.setStyleSheet(exit_style)
        menu_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        menu_btn.clicked.connect(
            lambda: self.navigator.navigate_to("main_menu")
        )
        bar.addWidget(menu_btn)

        logout_btn = QPushButton(tr("dashboard.logout"))
        logout_btn.setStyleSheet(exit_style)
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.clicked.connect(self.navigator.logout)
        bar.addWidget(logout_btn)

        layout.addLayout(bar)

    # ── Continue path ──

    def _build_continue_button(self, layout: QVBoxLayout) -> None:
        from neural_speed_academy.config import TRAINING_PATHS

        user = self.navigator.get_user()
        if not user or not user.active_path:
            return
        path_data = TRAINING_PATHS.get(user.active_path)
        if not path_data:
            return
        pp = user.path_progress.get(user.active_path)
        if not pp or pp.completed:
            return
        steps = path_data["steps"]
        if pp.current_step >= len(steps):
            return

        c = COLORS
        _, step_label, _ = steps[pp.current_step]
        btn = QPushButton(
            tr("dashboard.continue_path", path=path_data['name'], step=step_label)
        )
        btn.setStyleSheet(
            btn_css(c["success"], c["btn_text"], padding="10px")
        )
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(
            lambda: self.navigator.navigate_to("path_session")
        )
        layout.addWidget(btn)

    # ── Personal bests ──

    def _build_personal_bests(self, layout: QVBoxLayout) -> None:
        user = self.navigator.get_user()
        if not user or not user.personal_bests:
            return
        c = COLORS

        header = QLabel(tr("dashboard.personal_bests"))
        header.setFont(make_qfont("section_header"))
        header.setStyleSheet(f"color: {c['muted']};")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        grid = QGridLayout()
        grid.setSpacing(6)

        items = list(user.personal_bests.items())
        cols = 3
        for i, (exercise, data) in enumerate(items):
            row_idx, col_idx = divmod(i, cols)
            cell = QFrame()
            cell.setStyleSheet(
                f"background-color: {c['card']}; border-radius: 4px;"
            )
            cl = QHBoxLayout(cell)
            cl.setContentsMargins(10, 6, 10, 6)
            cl.setSpacing(8)

            name_lbl = QLabel(exercise)
            name_lbl.setFont(make_qfont("btn_sm"))
            name_lbl.setStyleSheet(f"color: {c['muted']};")
            cl.addWidget(name_lbl)

            cl.addStretch()

            from neural_speed_academy.screens.stats_screen import StatsScreen
            primary, _ = StatsScreen._pb_display(exercise, data)
            score_lbl = QLabel(primary)
            score_lbl.setFont(make_qfont("btn_bold"))
            score_lbl.setStyleSheet(f"color: {c['text_on_card']};")
            cl.addWidget(score_lbl)

            grid.addWidget(cell, row_idx, col_idx)

        layout.addLayout(grid)

    # ── Exercise grid ──

    def _create_section(self, grid: QGridLayout, title: str, column: int,
                        items: list[tuple[str, Callable]]) -> None:
        c = COLORS
        header = QLabel(title)
        header.setFont(make_qfont("section_header"))
        header.setStyleSheet(f"color: {c['muted']};")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        grid.addWidget(header, 0, column)

        for i, (text, command) in enumerate(items):
            btn = QPushButton(text)
            btn.setFixedHeight(38)
            btn.setStyleSheet(btn_css(c["accent"], c["btn_text"],
                                      padding="4px 12px"))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(command)
            grid.addWidget(btn, i + 1, column)

    def _cb(self, name: str) -> Callable:
        return self.exercise_callbacks.get(name, lambda: None)
