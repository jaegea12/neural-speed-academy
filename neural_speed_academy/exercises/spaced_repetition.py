"""
Spaced Repetition exercise.

SM-2 based flashcard system with pre-built and custom decks.
Cards are scheduled based on recall quality — forgotten cards
reappear sooner, mastered cards are spaced days or weeks apart.
"""
from __future__ import annotations

import random

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QLineEdit, QTextEdit, QFrame, QInputDialog,
    QMessageBox,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QKeySequence, QShortcut, QFont

from neural_speed_academy.exercises.base import BaseExercise, ExerciseResult
from neural_speed_academy.theme import COLORS, make_qfont, btn_css
from neural_speed_academy.config import SR_CONFIG, SR_BUILTIN_DECKS, USER_DATA_CONFIG
from neural_speed_academy.state import SRCard, SRDeck
from neural_speed_academy.i18n import tr


class SpacedRepetitionExercise(BaseExercise):

    def __init__(self, navigator, parent: QWidget | None = None):
        super().__init__(navigator, parent)
        self._deck: SRDeck | None = None
        self._queue: list[SRCard] = []
        self._current_card: SRCard | None = None
        self._card_idx: int = 0
        self._total_reviewed: int = 0
        self._ratings: list[int] = []
        self._in_review: bool = False
        self._in_reading: bool = False
        self._reading_idx: int = 0
        self._reading_cards: list[SRCard] = []
        # Options
        self._reverse_mode: bool = False
        self._timed_mode: int = 0  # 0 = off, else seconds per card
        self._session_size: int = 0  # 0 = default from config
        self._streak: int = 0
        self._best_streak: int = 0
        self._card_timer: QTimer | None = None

    @property
    def name(self) -> str:
        return "Spaced Repetition"

    # ── Deck selection screen ──

    def start(self, **kwargs) -> None:
        self._clear()
        self._running = True
        self.add_nav_bar(show_stop=False)

        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")

        # Ensure user has built-in decks initialized
        self._ensure_builtin_decks()

        container = QWidget()
        container.setStyleSheet(f"background-color: {c['bg']};")
        cl = QVBoxLayout(container)
        cl.setContentsMargins(30, 20, 30, 20)
        cl.setSpacing(10)

        # Title row (matches other menus)
        title_row = QHBoxLayout()
        title_row.addStretch()
        title_lbl = QLabel(tr("spaced.repetition.spaced_repetition"))
        title_lbl.setFont(make_qfont("header"))
        title_lbl.setStyleSheet(f"color: {c['fg']};")
        title_row.addWidget(title_lbl)

        guide_btn = QPushButton(tr("chunking.guide"))
        guide_btn.setFont(make_qfont("btn_sm"))
        guide_btn.setStyleSheet(
            f"background-color: {c['accent']}; color: {c['btn_text']}; "
            f"border: 2px solid transparent; padding: 6px 16px; border-radius: 4px;"
        )
        guide_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        guide_btn.clicked.connect(
            lambda: self.show_guide("spaced_repetition")
        )
        title_row.addWidget(guide_btn)
        title_row.addStretch()
        cl.addLayout(title_row)

        cl.addSpacing(6)

        # Two-column layout: decks (2/3) | options (1/3)
        columns = QHBoxLayout()
        columns.setSpacing(40)
        columns.setContentsMargins(20, 0, 20, 0)

        # ── Left: Deck list ──
        left = QVBoxLayout()
        left.setSpacing(8)

        deck_header = QLabel(tr("spaced.repetition.decks"))
        deck_header.setFont(make_qfont("menu_header"))
        deck_header.setStyleSheet(f"color: {c['accent']};")
        deck_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left.addWidget(deck_header)

        # Scrollable deck list
        deck_widget = QWidget()
        deck_widget.setStyleSheet(f"background-color: {c['bg']};")
        deck_layout = QVBoxLayout(deck_widget)
        deck_layout.setContentsMargins(0, 0, 0, 0)
        deck_layout.setSpacing(6)

        user = self.navigator.get_user()
        decks = user.sr_decks if user else []

        for deck in decks:
            stats = deck.stats()
            deck_frame = QFrame()
            deck_frame.setStyleSheet(
                f"QFrame {{ background-color: {c['card']}; "
                f"border-radius: 6px; padding: 4px; }}"
            )
            dl = QHBoxLayout(deck_frame)
            dl.setContentsMargins(10, 6, 10, 6)

            # Deck info
            info_col = QVBoxLayout()
            info_col.setSpacing(2)
            name_lbl = QLabel(deck.name)
            name_lbl.setFont(make_qfont("btn_bold"))
            name_lbl.setStyleSheet(f"color: {c['fg']};")
            info_col.addWidget(name_lbl)

            stats_text = (
                f"{stats['total']} cards  \u00b7  "
                f"{stats['due']} due  \u00b7  "
                f"{stats['new']} new"
            )
            stats_lbl = QLabel(stats_text)
            stats_lbl.setFont(make_qfont("btn_sm"))
            stats_lbl.setStyleSheet(f"color: {c['muted']};")
            info_col.addWidget(stats_lbl)
            dl.addLayout(info_col, 1)

            # Review button
            due_count = stats["due"] + stats["new"]
            if due_count > 0:
                review_btn = QPushButton(f"REVIEW ({due_count})")
                review_btn.setFont(make_qfont("btn_bold"))
                review_btn.setStyleSheet(
                    f"QPushButton {{ background-color: {c['success']}; "
                    f"color: {c['btn_text']}; border: 2px solid transparent; "
                    f"padding: 6px 14px; border-radius: 4px; }}"
                )
                review_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                review_btn.clicked.connect(
                    lambda _, d=deck: self._start_reading(d)
                )
                dl.addWidget(review_btn)
            else:
                done_lbl = QLabel(tr("spaced.repetition.u2714_all_caught_up"))
                done_lbl.setFont(make_qfont("btn_sm"))
                done_lbl.setStyleSheet(f"color: {c['success']};")
                dl.addWidget(done_lbl)

            # Manage button (add cards, only for non-builtin)
            if not deck.builtin:
                manage_btn = QPushButton(tr("spaced.repetition.u2795"))
                manage_btn.setFont(make_qfont("btn_sm"))
                manage_btn.setAccessibleName(tr("spaced.repetition.add_cards"))
                manage_btn.setToolTip(tr("spaced.repetition.add_cards"))
                manage_btn.setStyleSheet(
                    f"QPushButton {{ background-color: {c['accent']}; "
                    f"color: {c['btn_text']}; border: 2px solid transparent; "
                    f"padding: 6px 10px; border-radius: 4px; }}"
                )
                manage_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                manage_btn.clicked.connect(
                    lambda _, d=deck: self._add_card_dialog(d)
                )
                dl.addWidget(manage_btn)

            deck_layout.addWidget(deck_frame)

        deck_layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidget(deck_widget)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            f"QScrollArea {{ border: none; background-color: {c['bg']}; }}"
        )
        left.addWidget(scroll, 1)

        # New deck button
        new_btn = QPushButton(tr("spaced.repetition.new_deck"))
        new_btn.setFont(make_qfont("btn_bold"))
        new_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['card']}; "
            f"color: {c['accent']}; border: 1px solid {c['accent']}; "
            f"padding: 8px 20px; border-radius: 4px; }}"
            f"QPushButton:hover {{ background-color: {c['accent']}; "
            f"color: {c['btn_text']}; }}"
        )
        new_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        new_btn.clicked.connect(self._create_deck_dialog)
        left.addWidget(new_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        columns.addLayout(left, 2)

        # ── Right: Options ──
        right = QVBoxLayout()
        right.setSpacing(8)

        opt_header = QLabel(tr("spaced.repetition.options"))
        opt_header.setFont(make_qfont("menu_header"))
        opt_header.setStyleSheet(f"color: {c['accent']};")
        opt_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right.addWidget(opt_header)

        # Reverse mode toggle
        rev_header = QLabel(tr("spaced.repetition.mode"))
        rev_header.setFont(make_qfont("menu_header"))
        rev_header.setStyleSheet(f"color: {c['accent']};")
        rev_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right.addWidget(rev_header)

        self._normal_btn = QPushButton(tr("spaced.repetition.normal"))
        self._normal_btn.setFont(make_qfont("menu_btn"))
        self._normal_btn.setFixedHeight(40)
        self._normal_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._normal_btn.clicked.connect(lambda: self._set_reverse(False))
        right.addWidget(self._normal_btn)

        self._reverse_btn = QPushButton(tr("spaced.repetition.reverse"))
        self._reverse_btn.setFont(make_qfont("menu_btn"))
        self._reverse_btn.setFixedHeight(40)
        self._reverse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._reverse_btn.clicked.connect(lambda: self._set_reverse(True))
        right.addWidget(self._reverse_btn)

        right.addSpacing(10)

        # Timer options
        timer_header = QLabel(tr("spaced.repetition.time_limit"))
        timer_header.setFont(make_qfont("menu_header"))
        timer_header.setStyleSheet(f"color: {c['accent']};")
        timer_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right.addWidget(timer_header)

        self._timer_buttons: dict[int, QPushButton] = {}
        timer_options = [0, 15, 10, 7, 5, 3]
        timer_labels = {0: "Off", 15: "15s", 10: "10s", 7: "7s", 5: "5s", 3: "3s"}
        for t in timer_options:
            btn = QPushButton(timer_labels[t])
            btn.setFont(make_qfont("menu_btn"))
            btn.setFixedHeight(40)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, v=t: self._set_timed(v))
            right.addWidget(btn)
            self._timer_buttons[t] = btn

        right.addSpacing(10)

        # Session size
        size_header = QLabel(tr("spaced.repetition.session_size"))
        size_header.setFont(make_qfont("menu_header"))
        size_header.setStyleSheet(f"color: {c['accent']};")
        size_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right.addWidget(size_header)

        self._size_buttons: dict[int, QPushButton] = {}
        size_options = [0, 10, 20, 30, 50]
        size_labels = {0: "Default", 10: "10", 20: "20", 30: "30", 50: "50"}
        size_row = QHBoxLayout()
        size_row.setSpacing(8)
        for s in size_options:
            btn = QPushButton(size_labels[s])
            btn.setFont(make_qfont("menu_btn"))
            btn.setFixedHeight(40)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, v=s: self._set_session_size(v))
            size_row.addWidget(btn)
            self._size_buttons[s] = btn
        right.addLayout(size_row)

        right.addStretch()

        columns.addLayout(right, 1)
        cl.addLayout(columns, 1)

        self._layout.addWidget(container, 1)

        # Apply current option states to button styles
        self._set_reverse(self._reverse_mode)
        self._set_timed(self._timed_mode)
        self._set_session_size(self._session_size)

    def _opt_on(self) -> str:
        c = COLORS
        return (
            f"QPushButton {{ background-color: {c['accent']}; "
            f"color: {c['btn_text']}; border: 2px solid transparent; "
            f"padding: 6px 14px; border-radius: 4px; }}"
        )

    def _opt_off(self) -> str:
        c = COLORS
        return (
            f"QPushButton {{ background-color: {c['card']}; "
            f"color: {c['fg']}; border: 1px solid {c['muted']}; "
            f"padding: 6px 14px; border-radius: 4px; }}"
            f"QPushButton:hover {{ background-color: {c['accent']}; "
            f"color: {c['btn_text']}; }}"
        )

    def _set_reverse(self, on: bool) -> None:
        self._reverse_mode = on
        if hasattr(self, "_normal_btn"):
            self._normal_btn.setStyleSheet(
                self._opt_off() if on else self._opt_on()
            )
            self._reverse_btn.setStyleSheet(
                self._opt_on() if on else self._opt_off()
            )

    def _set_timed(self, seconds: int) -> None:
        self._timed_mode = seconds
        if hasattr(self, "_timer_buttons"):
            for v, btn in self._timer_buttons.items():
                btn.setStyleSheet(
                    self._opt_on() if v == seconds else self._opt_off()
                )

    def _set_session_size(self, size: int) -> None:
        self._session_size = size
        if hasattr(self, "_size_buttons"):
            for v, btn in self._size_buttons.items():
                btn.setStyleSheet(
                    self._opt_on() if v == size else self._opt_off()
                )

    def _ensure_builtin_decks(self) -> None:
        """Initialize built-in decks if user doesn't have them yet."""
        user = self.navigator.get_user()
        if not user:
            return
        existing_names = {d.name for d in user.sr_decks}
        for deck_name, card_data in SR_BUILTIN_DECKS.items():
            if deck_name not in existing_names:
                cards = [SRCard(front=f, back=b) for f, b in card_data]
                user.sr_decks.append(
                    SRDeck(name=deck_name, cards=cards, builtin=True)
                )

    def _create_deck_dialog(self) -> None:
        c = COLORS
        name, ok = QInputDialog.getText(
            self, "New Deck", "Deck name:",
        )
        if ok and name.strip():
            user = self.navigator.get_user()
            if user:
                user.sr_decks.append(SRDeck(name=name.strip()))
                self._save_user()
                self.start()  # refresh

    def _add_card_dialog(self, deck: SRDeck) -> None:
        c = COLORS
        front, ok1 = QInputDialog.getText(
            self, "Add Card", "Front (question/word):",
        )
        if not ok1 or not front.strip():
            return
        back, ok2 = QInputDialog.getText(
            self, "Add Card", "Back (answer/definition):",
        )
        if not ok2 or not back.strip():
            return
        deck.cards.append(SRCard(front=front.strip(), back=back.strip()))
        self._save_user()
        self.start()  # refresh

    # ── Review session ──

    def _stop_exercise(self) -> None:
        """Override base: return to deck selection during review/reading."""
        self._running = False
        for t in self._timers:
            t.stop()
        self._timers.clear()
        if self._card_timer:
            self._card_timer.stop()
            self._card_timer = None
        if self._in_review or self._in_reading:
            self._save_user()
            self._in_review = False
            self._in_reading = False
            self.start()
        else:
            self.navigator.finish_exercise()

    # ── Reading phase ──

    def _start_reading(self, deck: SRDeck) -> None:
        """Browse all cards in the deck before starting review."""
        self._deck = deck
        self._in_reading = True
        self._in_review = False
        self._reading_cards = list(deck.cards)
        self._reading_idx = 0
        self._show_reading_card()

    def _show_reading_card(self) -> None:
        if not self._reading_cards:
            self._start_review(self._deck)
            return

        self._clear()
        self._running = True

        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")
        card = self._reading_cards[self._reading_idx]
        total = len(self._reading_cards)

        # Top bar
        top = QHBoxLayout()
        top.setContentsMargins(10, 6, 10, 2)

        progress = QLabel(
            f"Reading {self._reading_idx + 1}/{total}  "
            f"\u00b7  {self._deck.name}"
        )
        progress.setFont(make_qfont("counter"))
        progress.setStyleSheet(f"color: {c['accent']};")
        top.addWidget(progress)

        top.addStretch()

        skip_btn = QPushButton(tr("spaced.repetition.skip_to_review_u25b6"))
        skip_btn.setFont(make_qfont("btn_sm"))
        skip_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['accent']}; "
            f"color: {c['btn_text']}; border: 2px solid transparent; "
            f"padding: 4px 12px; border-radius: 3px; }}"
        )
        skip_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        skip_btn.clicked.connect(
            lambda: self._start_review(self._deck)
        )
        top.addWidget(skip_btn)

        exit_btn = QPushButton(tr("chunking.u2716"))
        exit_btn.setAccessibleName(tr("chunking.close"))
        exit_btn.setToolTip(tr("chunking.close"))
        exit_btn.setFont(make_qfont("exit_btn"))
        exit_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        exit_btn.setStyleSheet(
            btn_css(c["alert"], c["text_on_card"], padding="4px 8px",
                    radius=3, font_key="exit_btn")
        )
        exit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        exit_btn.clicked.connect(self._stop)
        top.addWidget(exit_btn)
        self._layout.addLayout(top)

        self._layout.addStretch()

        # Card display — front and back visible
        front_label = QLabel(tr("spaced.repetition.front"))
        front_label.setFont(make_qfont("btn_sm"))
        front_label.setStyleSheet(f"color: {c['muted']};")
        front_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(front_label)

        front_text = QLabel(card.front)
        front_text.setFont(make_qfont("header"))
        front_text.setStyleSheet(f"color: {c['fg']};")
        front_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        front_text.setWordWrap(True)
        self._layout.addWidget(front_text)

        self._layout.addSpacing(16)

        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet(f"color: {c['muted']};")
        divider.setFixedWidth(300)
        self._layout.addWidget(
            divider, alignment=Qt.AlignmentFlag.AlignCenter
        )

        self._layout.addSpacing(16)

        back_label = QLabel(tr("spaced.repetition.back"))
        back_label.setFont(make_qfont("btn_sm"))
        back_label.setStyleSheet(f"color: {c['muted']};")
        back_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(back_label)

        back_text = QLabel(card.back)
        back_text.setFont(make_qfont("section_header"))
        back_text.setStyleSheet(f"color: {c['accent']};")
        back_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        back_text.setWordWrap(True)
        self._layout.addWidget(back_text)

        self._layout.addStretch()

        # Navigation buttons
        nav_row = QHBoxLayout()
        nav_row.setSpacing(20)
        nav_row.addStretch()

        if self._reading_idx > 0:
            prev_btn = QPushButton(tr("spaced.repetition.u2190_previous"))
            prev_btn.setFont(make_qfont("btn_bold"))
            prev_btn.setStyleSheet(
                f"QPushButton {{ background-color: {c['card']}; "
                f"color: {c['fg']}; border: 1px solid {c['muted']}; "
                f"padding: 8px 24px; border-radius: 4px; }}"
            )
            prev_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            prev_btn.clicked.connect(self._reading_prev)
            nav_row.addWidget(prev_btn)

        if self._reading_idx < total - 1:
            next_btn = QPushButton(tr("spaced.repetition.next_u2192"))
            next_btn.setFont(make_qfont("btn_bold"))
            next_btn.setStyleSheet(
                f"QPushButton {{ background-color: {c['accent']}; "
                f"color: {c['btn_text']}; border: 2px solid transparent; "
                f"padding: 8px 24px; border-radius: 4px; }}"
            )
            next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            next_btn.clicked.connect(self._reading_next)
            nav_row.addWidget(next_btn)
        else:
            start_btn = QPushButton(tr("spaced.repetition.start_review_u25b6"))
            start_btn.setFont(make_qfont("btn_bold"))
            start_btn.setStyleSheet(
                f"QPushButton {{ background-color: {c['success']}; "
                f"color: {c['btn_text']}; border: 2px solid transparent; "
                f"padding: 8px 24px; border-radius: 4px; }}"
            )
            start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            start_btn.clicked.connect(
                lambda: self._start_review(self._deck)
            )
            nav_row.addWidget(start_btn)

        nav_row.addStretch()
        self._layout.addLayout(nav_row)

        self._layout.addSpacing(10)

        # Keyboard: left/right arrows, Enter for next/start
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()

    def keyPressEvent(self, event) -> None:
        if event.isAutoRepeat():
            return
        key = event.key()
        if self._in_reading:
            if key == Qt.Key.Key_Right or key == Qt.Key.Key_D:
                if self._reading_idx < len(self._reading_cards) - 1:
                    self._reading_next()
                else:
                    self._start_review(self._deck)
                return
            if key == Qt.Key.Key_Left or key == Qt.Key.Key_A:
                if self._reading_idx > 0:
                    self._reading_prev()
                return
        super().keyPressEvent(event)

    def _reading_next(self) -> None:
        self._reading_idx += 1
        self._show_reading_card()

    def _reading_prev(self) -> None:
        self._reading_idx -= 1
        self._show_reading_card()

    # ── Review session ──

    def _start_review(self, deck: SRDeck) -> None:
        self._deck = deck
        self._in_review = True
        self._in_reading = False
        self._streak = 0
        self._best_streak = 0
        cfg = SR_CONFIG

        # Build review queue: due cards first, then new cards
        due = [c for c in deck.cards if c.due_date and c.is_due()]
        new = [c for c in deck.cards if not c.due_date]

        random.shuffle(due)
        random.shuffle(new)

        # Limit session size
        max_review = (
            self._session_size if self._session_size > 0
            else cfg["max_review_per_session"]
        )
        max_new = min(cfg["max_new_per_session"], max_review)
        review_cards = due[:max_review]
        review_cards.extend(new[:max_new])

        if not review_cards:
            return

        self._queue = review_cards
        self._card_idx = 0
        self._total_reviewed = 0
        self._ratings = []
        self._show_card()

    def _show_card(self) -> None:
        if self._card_idx >= len(self._queue):
            self._show_session_results()
            return

        self._current_card = self._queue[self._card_idx]
        if self._card_timer:
            self._card_timer.stop()
            self._card_timer = None
        self._clear()
        self._running = True

        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")

        # Determine what to show based on reverse mode
        show_text = (
            self._current_card.back if self._reverse_mode
            else self._current_card.front
        )

        # Top bar
        top = QHBoxLayout()
        top.setContentsMargins(10, 6, 10, 2)

        progress = QLabel(
            f"Card {self._card_idx + 1}/{len(self._queue)}  "
            f"\u00b7  {self._deck.name}"
        )
        progress.setFont(make_qfont("counter"))
        progress.setStyleSheet(f"color: {c['accent']};")
        top.addWidget(progress)

        # Streak display
        if self._streak > 0:
            streak_lbl = QLabel(f"\U0001f525 {self._streak}")
            streak_lbl.setFont(make_qfont("counter"))
            streak_lbl.setStyleSheet(f"color: {c['success']};")
            top.addWidget(streak_lbl)

        top.addStretch()

        # Timer countdown label
        if self._timed_mode > 0:
            self._timer_remaining = self._timed_mode
            self._timer_lbl = QLabel(f"{self._timed_mode}s")
            self._timer_lbl.setFont(QFont("Arial", 18, QFont.Weight.Bold))
            self._timer_lbl.setStyleSheet(f"color: {c['alert']};")
            top.addWidget(self._timer_lbl)
            top.addSpacing(10)

        # Mode indicators
        mode_parts = []
        if self._reverse_mode:
            mode_parts.append("REVERSE")
        if self._timed_mode > 0:
            mode_parts.append(f"{self._timed_mode}s")
        if mode_parts:
            mode_lbl = QLabel(" · ".join(mode_parts))
            mode_lbl.setFont(make_qfont("btn_sm"))
            mode_lbl.setStyleSheet(f"color: {c['muted']};")
            top.addWidget(mode_lbl)
            top.addSpacing(10)

        exit_btn = QPushButton(tr("chunking.u2716"))
        exit_btn.setAccessibleName(tr("chunking.close"))
        exit_btn.setToolTip(tr("chunking.close"))
        exit_btn.setFont(make_qfont("exit_btn"))
        exit_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        exit_btn.setStyleSheet(
            btn_css(c["alert"], c["text_on_card"], padding="4px 8px",
                    radius=3, font_key="exit_btn")
        )
        exit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        exit_btn.clicked.connect(self._stop)
        top.addWidget(exit_btn)
        self._layout.addLayout(top)

        # Card prompt
        self._layout.addStretch()

        hint_lbl = QLabel(tr("spaced.repetition.think_of_the_answer_then_revea"))
        hint_lbl.setFont(make_qfont("body"))
        hint_lbl.setStyleSheet(f"color: {c['muted']}; font-style: italic;")
        hint_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(hint_lbl)

        self._layout.addSpacing(12)

        front_lbl = QLabel(show_text)
        front_lbl.setFont(make_qfont("section_header"))
        front_lbl.setStyleSheet(f"color: {c['fg']};")
        front_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        front_lbl.setWordWrap(True)
        self._layout.addWidget(front_lbl)

        self._layout.addSpacing(20)

        # "Show Answer" button
        self._answer_area = QVBoxLayout()
        self._answer_area.setAlignment(Qt.AlignmentFlag.AlignCenter)

        show_btn = QPushButton(tr("spaced.repetition.show_answer"))
        show_btn.setFont(make_qfont("btn_lg"))
        show_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['accent']}; "
            f"color: {c['btn_text']}; border: 2px solid transparent; "
            f"padding: 12px 40px; border-radius: 4px; }}"
        )
        show_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        show_btn.clicked.connect(self._reveal_answer)
        self._answer_area.addWidget(
            show_btn, alignment=Qt.AlignmentFlag.AlignCenter
        )

        key_hint = QLabel(tr("spaced.repetition.x_to_reveal_1_4_to_rate"))
        key_hint.setFont(make_qfont("btn_sm"))
        key_hint.setStyleSheet(f"color: {c['muted']};")
        key_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._answer_area.addWidget(key_hint)

        # Keyboard shortcut (X — Space conflicts with QPushButton)
        shortcut = QShortcut(QKeySequence(Qt.Key.Key_X), self)
        shortcut.activated.connect(self._reveal_answer)

        self._layout.addLayout(self._answer_area)
        self._layout.addStretch()

        # Start timer if timed mode
        if self._timed_mode > 0:
            self._card_timer = QTimer(self)
            self._card_timer.setInterval(1000)
            self._card_timer.timeout.connect(self._tick_card_timer)
            self._card_timer.start()

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()

    def _tick_card_timer(self) -> None:
        self._timer_remaining -= 1
        c = COLORS
        if self._timer_remaining <= 0:
            if self._card_timer:
                self._card_timer.stop()
                self._card_timer = None
            self._reveal_answer()
        elif hasattr(self, "_timer_lbl") and self._timer_lbl:
            self._timer_lbl.setText(f"{self._timer_remaining}s")
            if self._timer_remaining <= 3:
                self._timer_lbl.setStyleSheet(
                    f"color: {c['alert']}; font-weight: bold;"
                )

    def _reveal_answer(self) -> None:
        if not self._current_card:
            return

        # Stop timer
        if self._card_timer:
            self._card_timer.stop()
            self._card_timer = None

        c = COLORS

        # Clear the answer area
        while self._answer_area.count():
            item = self._answer_area.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        # Show answer (opposite side from what was shown)
        answer_text = (
            self._current_card.front if self._reverse_mode
            else self._current_card.back
        )

        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet(f"color: {c['muted']};")
        self._answer_area.addWidget(divider)

        self._answer_area.addSpacing(10)

        answer_lbl = QLabel(answer_text)
        answer_lbl.setFont(make_qfont("header"))
        answer_lbl.setStyleSheet(f"color: {c['accent']};")
        answer_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        answer_lbl.setWordWrap(True)
        self._answer_area.addWidget(answer_lbl)

        self._answer_area.addSpacing(20)

        # Rating label
        rate_lbl = QLabel(tr("spaced.repetition.how_well_did_you_recall"))
        rate_lbl.setFont(make_qfont("body"))
        rate_lbl.setStyleSheet(f"color: {c['fg']};")
        rate_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._answer_area.addWidget(rate_lbl)

        self._answer_area.addSpacing(6)

        # Rating buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        ratings = [
            (0, "AGAIN", c["alert"]),
            (1, "HARD", "#e67e22"),
            (2, "GOOD", c["accent"]),
            (3, "EASY", c["success"]),
        ]

        for quality, label, color in ratings:
            btn = QPushButton(label)
            btn.setFont(make_qfont("btn_bold"))
            btn.setFixedWidth(90)
            btn.setStyleSheet(
                f"QPushButton {{ background-color: {color}; "
                f"color: {c['btn_text']}; border: 2px solid transparent; "
                f"padding: 8px; border-radius: 4px; }}"
            )
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(
                lambda _, q=quality: self._rate_card(q)
            )
            btn_row.addWidget(btn)

        btn_row.addStretch()
        self._answer_area.addLayout(btn_row)

        # Keyboard shortcuts: 1=Again, 2=Hard, 3=Good, 4=Easy
        for key, q in [(Qt.Key.Key_1, 0), (Qt.Key.Key_2, 1),
                       (Qt.Key.Key_3, 2), (Qt.Key.Key_4, 3)]:
            s = QShortcut(QKeySequence(key), self)
            s.activated.connect(lambda quality=q: self._rate_card(quality))

    def _rate_card(self, quality: int) -> None:
        if not self._current_card:
            return

        self._current_card.review(quality)
        self._ratings.append(quality)
        self._total_reviewed += 1
        self._card_idx += 1

        # Streak tracking: Good (2) or Easy (3) continues streak
        if quality >= 2:
            self._streak += 1
            self._best_streak = max(self._best_streak, self._streak)
        else:
            self._streak = 0

        # If "again", re-add to end of queue
        if quality == 0:
            self._queue.append(self._current_card)

        self._save_user()
        self._show_card()

    # ── Session results ──

    def _show_session_results(self) -> None:
        self._running = False
        self._in_review = False
        c = COLORS

        total = self._total_reviewed
        if not self._ratings:
            self.navigator.finish_exercise()
            return

        avg_quality = sum(self._ratings) / len(self._ratings)
        again_count = self._ratings.count(0)
        hard_count = self._ratings.count(1)
        good_count = self._ratings.count(2)
        easy_count = self._ratings.count(3)

        xp = total * USER_DATA_CONFIG["xp_per_correct"]
        result = ExerciseResult(
            exercise_name="SPACED REPETITION",
            score=total - again_count,
            total=total,
            xp_gained=xp,
            metadata={
                "deck": self._deck.name if self._deck else "",
                "cards_reviewed": total,
                "again": again_count,
                "hard": hard_count,
                "good": good_count,
                "easy": easy_count,
                "avg_quality": round(avg_quality, 2),
                "best_streak": self._best_streak,
                "reverse": self._reverse_mode,
                "timed": self._timed_mode,
            },
        )
        is_pb = self.complete(result)

        self._clear()
        self.add_nav_bar()
        self.setStyleSheet(f"background-color: {c['bg']};")

        container = QWidget()
        container.setStyleSheet(f"background-color: {c['bg']};")
        cl = QVBoxLayout(container)
        cl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.setSpacing(8)

        title = QLabel(tr("spaced.repetition.session_complete"))
        title.setFont(make_qfont("section_header"))
        title.setStyleSheet(f"color: {c['accent']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(title)

        cl.addSpacing(10)

        reviewed_lbl = QLabel(tr("spaced.cards_reviewed", count=total))
        reviewed_lbl.setFont(make_qfont("header"))
        reviewed_lbl.setStyleSheet(f"color: {c['fg']};")
        reviewed_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(reviewed_lbl)

        cl.addSpacing(10)

        # Rating breakdown
        breakdown = [
            (f"\u2718 Again: {again_count}", c["alert"]),
            (f"\u25cf Hard: {hard_count}", "#e67e22"),
            (f"\u25cf Good: {good_count}", c["accent"]),
            (f"\u2714 Easy: {easy_count}", c["success"]),
        ]
        for text, color in breakdown:
            lbl = QLabel(text)
            lbl.setFont(make_qfont("body"))
            lbl.setStyleSheet(f"color: {color};")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cl.addWidget(lbl)

        # Best streak
        if self._best_streak > 0:
            streak_lbl = QLabel(
                f"\U0001f525 Best streak: {self._best_streak}"
            )
            streak_lbl.setFont(make_qfont("body"))
            streak_lbl.setStyleSheet(f"color: {c['success']};")
            streak_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cl.addWidget(streak_lbl)

        cl.addSpacing(10)

        # Deck stats
        if self._deck:
            stats = self._deck.stats()
            deck_lbl = QLabel(
                f"{self._deck.name}: {stats['due']} still due  \u00b7  "
                f"{stats['learned']}/{stats['total']} learned"
            )
            deck_lbl.setFont(make_qfont("btn_sm"))
            deck_lbl.setStyleSheet(f"color: {c['muted']};")
            deck_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cl.addWidget(deck_lbl)

        cl.addSpacing(10)

        cont_btn = QPushButton(tr("base.continue"))
        cont_btn.setFont(make_qfont("btn_bold"))
        cont_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['accent']}; "
            f"color: {c['btn_text']}; border: 2px solid transparent; "
            f"padding: 8px 40px; border-radius: 4px; }}"
        )
        cont_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cont_btn.clicked.connect(self.start)
        cl.addWidget(cont_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self._layout.addWidget(container, 1)

    # ── Helpers ──

    def _save_user(self) -> None:
        """Persist user data after card updates."""
        self.navigator.save_user()

    def _stop(self) -> None:
        self._running = False
        self._in_review = False
        self._in_reading = False
        if self._card_timer:
            self._card_timer.stop()
            self._card_timer = None
        self._save_user()
        self.start()
