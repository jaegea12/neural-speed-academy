"""
Training hub dashboard.
"""
from __future__ import annotations

from typing import Callable

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QGridLayout, QProgressBar,
)
from PyQt6.QtCore import Qt

from neural_speed_academy.screens.base import BaseScreen
from neural_speed_academy.theme import COLORS, make_qfont, font_css, btn_css, screen_metrics


class DashboardScreen(BaseScreen):
    @property
    def BTN_WIDTH(self) -> int:
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        if screen:
            avail_w = screen.availableGeometry().width()
            win = self.window()
            if win and not win.isFullScreen():
                avail_w = min(avail_w, win.width() or 1024)
        else:
            avail_w = 1024
        # Two columns, leave margins and spacing
        w = min(int((avail_w - 120) / 2.5), 360)
        return max(w, 180)

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
        title = QLabel("TRAINING HUB")
        title.setFont(make_qfont("header"))
        title.setStyleSheet(f"color: {c['text_on_card']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hl.addWidget(title)
        self._layout.addWidget(header)

        # Main content
        content = QWidget()
        content.setStyleSheet(f"background-color: {c['bg']};")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(30, 12, 30, 12)
        cl.setSpacing(10)

        self._build_user_card(cl)
        self._build_onboarding(cl)
        self._build_action_bar(cl)
        self._build_continue_button(cl)
        self._build_personal_bests(cl)

        # Eye Priming — standalone warmup button above exercise grid
        c_priming = COLORS
        warmup_btn = QPushButton("EYE WARMUP")
        warmup_btn.setFixedWidth(self.BTN_WIDTH)
        warmup_btn.setStyleSheet(
            btn_css(c_priming["priming"], c_priming["btn_text"],
                    padding="12px", font_key="btn_bold")
        )
        warmup_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        warmup_btn.clicked.connect(self._cb("menu_priming"))
        cl.addWidget(warmup_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        cl.addSpacing(4)

        # Exercise grid
        grid = QGridLayout()
        grid.setSpacing(12)

        self._create_section(grid, "PERCEPTION", 0, [
            ("Flash Numbers", self._cb("menu_flash")),
            ("Word Drills", self._cb("menu_words")),
            ("Eye-Span", self._cb("menu_eyespan")),
            ("Schulte Grid", self._cb("start_schulte")),
            ("Sequence Memory", self._cb("menu_sequence_memory")),
            ("Peripheral Flash", self._cb("menu_peripheral_flash")),
            ("Rapid Decision", self._cb("menu_rapid_decision")),
            ("Object Tracking", self._cb("menu_mot")),
            ("Split Attention", self._cb("menu_split_attention")),
        ])
        self._create_section(grid, "READING", 1, [
            ("Pacer & Quiz", self._cb("setup_pacer")),
            ("RSVP Reader", self._cb("setup_rsvp")),
            ("Chunking", self._cb("setup_chunking")),
        ])
        cl.addLayout(grid)
        cl.addStretch()

        self._layout.addWidget(content, 1)

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
        info = QLabel(
            f"{user.name.upper()}   |   Level {level}   |   "
            f"Streak: {user.streak} day{'s' if user.streak != 1 else ''}"
        )
        info.setFont(make_qfont("btn_sm"))
        info.setStyleSheet(f"color: {c['text_on_card']};")
        cl.addWidget(info)
        cl.addStretch()

        last_text = "No sessions yet"
        if user.history:
            last = user.history[0]
            last_text = (
                f"Last: {last.exercise} \u2014 {last.result} ({last.timestamp})"
            )
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
            f"border: none; border-radius: 4px; }}"
            f"QProgressBar::chunk {{ background-color: {c['accent']}; "
            f"border-radius: 4px; }}"
        )
        bar_row.addWidget(progress)

        xp_label = QLabel(f"{xp_in_level}/1000 XP to Level {level + 1}")
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

        welcome = QLabel("Welcome! New to speed reading?")
        welcome.setFont(make_qfont("btn_bold"))
        welcome.setStyleSheet(f"color: {c['btn_text']};")
        bl.addWidget(welcome)
        bl.addStretch()

        start_btn = QPushButton("START FOUNDATION PATH")
        start_btn.setFont(make_qfont("btn_bold"))
        start_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['btn_text']}; "
            f"color: {c['accent']}; border: none; "
            f"padding: 4px 12px; border-radius: 3px; }}"
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
            ("Training Paths", "show_paths"),
            ("Stats & History", "show_stats"),
        ]:
            btn = QPushButton(label)
            btn.setStyleSheet(action_style)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(self._cb(cb_name))
            bar.addWidget(btn)

        bar.addStretch()

        # Right: exit actions
        menu_btn = QPushButton("Main Menu")
        menu_btn.setStyleSheet(exit_style)
        menu_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        menu_btn.clicked.connect(
            lambda: self.navigator.navigate_to("main_menu")
        )
        bar.addWidget(menu_btn)

        logout_btn = QPushButton("Logout")
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
            f"CONTINUE: {path_data['name']} \u2014 {step_label}"
        )
        btn.setFont(make_qfont("btn_bold"))
        btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['success']}; "
            f"color: {c['btn_text']}; border: none; "
            f"padding: 10px; border-radius: 4px; }}"
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
        row = QHBoxLayout()
        for exercise, data in user.personal_bests.items():
            cell = QFrame()
            cell.setStyleSheet(
                f"background-color: {c['card']}; border-radius: 4px; "
                f"padding: 6px 12px;"
            )
            cl = QVBoxLayout(cell)
            cl.setSpacing(2)
            name_lbl = QLabel(exercise)
            name_lbl.setFont(make_qfont("btn_sm"))
            name_lbl.setStyleSheet(f"color: {c['muted']};")
            cl.addWidget(name_lbl)
            score_lbl = QLabel(
                f"{data['score']}/{data['total']}  ({data['pct']}%)"
            )
            score_lbl.setFont(make_qfont("btn_bold"))
            score_lbl.setStyleSheet(f"color: {c['text_on_card']};")
            cl.addWidget(score_lbl)
            row.addWidget(cell)
        row.addStretch()
        layout.addLayout(row)

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
            btn.setFixedWidth(self.BTN_WIDTH)
            btn.setStyleSheet(btn_css(c["accent"], c["btn_text"]))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(command)
            grid.addWidget(
                btn, i + 1, column,
                alignment=Qt.AlignmentFlag.AlignCenter,
            )

    def _cb(self, name: str) -> Callable:
        return self.exercise_callbacks.get(name, lambda: None)
