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
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut

from neural_speed_academy.exercises.base import BaseExercise, ExerciseResult
from neural_speed_academy.theme import COLORS, make_qfont, input_css, screen_metrics
from neural_speed_academy.config import SR_CONFIG, SR_BUILTIN_DECKS, USER_DATA_CONFIG
from neural_speed_academy.state import SRCard, SRDeck


class SpacedRepetitionExercise(BaseExercise):

    def __init__(self, navigator, parent: QWidget | None = None):
        super().__init__(navigator, parent)
        self._deck: SRDeck | None = None
        self._queue: list[SRCard] = []
        self._current_card: SRCard | None = None
        self._card_idx: int = 0
        self._total_reviewed: int = 0
        self._ratings: list[int] = []

    @property
    def name(self) -> str:
        return "Spaced Repetition"

    # ── Deck selection screen ──

    def start(self, **kwargs) -> None:
        self._clear()
        self._running = True
        self.add_nav_bar()

        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")

        # Ensure user has built-in decks initialized
        self._ensure_builtin_decks()

        container = QWidget()
        container.setStyleSheet(f"background-color: {c['bg']};")
        cl = QVBoxLayout(container)
        cl.setContentsMargins(40, 10, 40, 10)
        cl.setSpacing(8)

        # Guide button
        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        guide_btn = QPushButton("GUIDE")
        guide_btn.setFont(make_qfont("btn_sm"))
        guide_btn.setStyleSheet(
            f"background-color: {c['accent']}; color: {c['btn_text']}; "
            f"border: none; padding: 4px 12px; border-radius: 3px;"
        )
        guide_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        guide_btn.clicked.connect(
            lambda: self.show_guide("spaced_repetition")
        )
        top.addWidget(guide_btn)
        top.addStretch()
        cl.addLayout(top)

        title = QLabel("SPACED REPETITION")
        title.setFont(make_qfont("section_header"))
        title.setStyleSheet(f"color: {c['accent']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(title)

        subtitle = QLabel("Select a deck to review")
        subtitle.setFont(make_qfont("body"))
        subtitle.setStyleSheet(f"color: {c['fg']};")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(subtitle)

        cl.addSpacing(10)

        # Deck list
        user = self.navigator.get_user()
        decks = user.sr_decks if user else []

        for deck in decks:
            stats = deck.stats()
            deck_frame = QFrame()
            deck_frame.setStyleSheet(
                f"QFrame {{ background-color: {c['card']}; "
                f"border-radius: 6px; padding: 8px; }}"
            )
            dl = QHBoxLayout(deck_frame)
            dl.setContentsMargins(12, 8, 12, 8)

            # Deck info
            info_col = QVBoxLayout()
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
                    f"color: {c['btn_text']}; border: none; "
                    f"padding: 6px 16px; border-radius: 4px; }}"
                )
                review_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                review_btn.clicked.connect(
                    lambda _, d=deck: self._start_review(d)
                )
                dl.addWidget(review_btn)
            else:
                done_lbl = QLabel("\u2714 All caught up")
                done_lbl.setFont(make_qfont("btn_sm"))
                done_lbl.setStyleSheet(f"color: {c['success']};")
                dl.addWidget(done_lbl)

            # Manage button (add cards, only for non-builtin)
            if not deck.builtin:
                manage_btn = QPushButton("\u2795")
                manage_btn.setFont(make_qfont("btn_sm"))
                manage_btn.setToolTip("Add cards")
                manage_btn.setStyleSheet(
                    f"QPushButton {{ background-color: {c['accent']}; "
                    f"color: {c['btn_text']}; border: none; "
                    f"padding: 6px 10px; border-radius: 4px; }}"
                )
                manage_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                manage_btn.clicked.connect(
                    lambda _, d=deck: self._add_card_dialog(d)
                )
                dl.addWidget(manage_btn)

            cl.addWidget(deck_frame)

        cl.addSpacing(10)

        # Create new deck button
        new_btn = QPushButton("+ NEW DECK")
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
        cl.addWidget(new_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        cl.addStretch()

        scroll = QScrollArea()
        scroll.setWidget(container)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            f"QScrollArea {{ border: none; background-color: {c['bg']}; }}"
        )
        self._layout.addWidget(scroll, 1)

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

    def _start_review(self, deck: SRDeck) -> None:
        self._deck = deck
        cfg = SR_CONFIG

        # Build review queue: due cards first, then new cards
        due = [c for c in deck.cards if c.due_date and c.is_due()]
        new = [c for c in deck.cards if not c.due_date]

        random.shuffle(due)
        random.shuffle(new)

        # Limit session size
        review_cards = due[:cfg["max_review_per_session"]]
        new_slots = cfg["max_new_per_session"]
        review_cards.extend(new[:new_slots])

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
        self._clear()
        self._running = True

        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")

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

        top.addStretch()

        exit_btn = QPushButton("\u2716")
        exit_btn.setFont(make_qfont("exit_btn"))
        exit_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['alert']}; "
            f"color: {c['text_on_card']}; "
            f"border: none; padding: 4px 8px; border-radius: 3px; }}"
        )
        exit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        exit_btn.clicked.connect(self._stop)
        top.addWidget(exit_btn)
        self._layout.addLayout(top)

        # Card front
        self._layout.addStretch()

        hint_lbl = QLabel("Think of the answer, then reveal it")
        hint_lbl.setFont(make_qfont("body"))
        hint_lbl.setStyleSheet(f"color: {c['muted']}; font-style: italic;")
        hint_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(hint_lbl)

        self._layout.addSpacing(12)

        front_lbl = QLabel(self._current_card.front)
        front_lbl.setFont(make_qfont("section_header"))
        front_lbl.setStyleSheet(f"color: {c['fg']};")
        front_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        front_lbl.setWordWrap(True)
        self._layout.addWidget(front_lbl)

        self._layout.addSpacing(20)

        # "Show Answer" button
        self._answer_area = QVBoxLayout()
        self._answer_area.setAlignment(Qt.AlignmentFlag.AlignCenter)

        show_btn = QPushButton("SHOW ANSWER")
        show_btn.setFont(make_qfont("btn_lg"))
        show_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['accent']}; "
            f"color: {c['btn_text']}; border: none; "
            f"padding: 12px 40px; border-radius: 4px; }}"
        )
        show_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        show_btn.clicked.connect(self._reveal_answer)
        self._answer_area.addWidget(
            show_btn, alignment=Qt.AlignmentFlag.AlignCenter
        )

        key_hint = QLabel("X to reveal  ·  1-4 to rate")
        key_hint.setFont(make_qfont("btn_sm"))
        key_hint.setStyleSheet(f"color: {c['muted']};")
        key_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._answer_area.addWidget(key_hint)

        # Keyboard shortcut (X — Space conflicts with QPushButton)
        shortcut = QShortcut(QKeySequence(Qt.Key.Key_X), self)
        shortcut.activated.connect(self._reveal_answer)

        self._layout.addLayout(self._answer_area)
        self._layout.addStretch()

    def _reveal_answer(self) -> None:
        if not self._current_card:
            return

        c = COLORS

        # Clear the answer area
        while self._answer_area.count():
            item = self._answer_area.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        # Show answer
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet(f"color: {c['muted']};")
        self._answer_area.addWidget(divider)

        self._answer_area.addSpacing(10)

        answer_lbl = QLabel(self._current_card.back)
        answer_lbl.setFont(make_qfont("header"))
        answer_lbl.setStyleSheet(f"color: {c['accent']};")
        answer_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        answer_lbl.setWordWrap(True)
        self._answer_area.addWidget(answer_lbl)

        self._answer_area.addSpacing(20)

        # Rating label
        rate_lbl = QLabel("How well did you recall?")
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
                f"color: {c['btn_text']}; border: none; "
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

        # If "again", re-add to end of queue
        if quality == 0:
            self._queue.append(self._current_card)

        self._save_user()
        self._show_card()

    # ── Session results ──

    def _show_session_results(self) -> None:
        self._running = False
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

        title = QLabel("SESSION COMPLETE")
        title.setFont(make_qfont("section_header"))
        title.setStyleSheet(f"color: {c['accent']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(title)

        cl.addSpacing(10)

        reviewed_lbl = QLabel(f"Cards reviewed: {total}")
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

        cont_btn = QPushButton("CONTINUE")
        cont_btn.setFont(make_qfont("btn_bold"))
        cont_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['accent']}; "
            f"color: {c['btn_text']}; border: none; "
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
        self._save_user()
        self.start()
