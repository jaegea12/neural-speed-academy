"""
Slide Processing exercise.

Displays text-based slides with facts and numbers for a limited time.
After each slide disappears, 2-3 comprehension questions test recall
of specific details. Trains rapid information extraction.
"""
from __future__ import annotations

import random
import re

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSlider, QComboBox, QFrame,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QShortcut, QKeySequence

from neural_speed_academy.exercises.base import BaseExercise, ExerciseResult
from neural_speed_academy.theme import COLORS, make_qfont, btn_css
from neural_speed_academy.config import (
    SLIDE_PROCESSING_CONFIG, SLIDE_LIBRARY, USER_DATA_CONFIG,
)
from neural_speed_academy.i18n import tr


class SlideProcessingExercise(BaseExercise):

    def __init__(self, navigator, parent: QWidget | None = None):
        super().__init__(navigator, parent)
        self._display_s: int = 5
        self._total_slides: int = 5
        self._lines_per_slide: int = 6
        self._category: str = "mixed"
        self._slide_idx: int = 0
        self._question_idx: int = 0
        self._correct: int = 0
        self._total_questions: int = 0
        self._slides: list = []
        self._current_slide: tuple | None = None
        self._current_questions: list = []
        self._countdown_remaining: int = 0
        # UI refs
        self._countdown_lbl: QLabel | None = None
        self._progress_lbl: QLabel | None = None
        self._content_area: QWidget | None = None
        self._content_layout: QVBoxLayout | None = None
        self._countdown_timer: QTimer | None = None

    @property
    def name(self) -> str:
        return "Slide Processing"

    # ── Config screen ──

    def start(self, **kwargs) -> None:
        self._clear()
        self._running = True

        cfg = SLIDE_PROCESSING_CONFIG
        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")

        self._display_s = kwargs.get("display_s", cfg["default_display_s"])
        self._total_slides = kwargs.get("slides", cfg["default_slides"])
        self._lines_per_slide = kwargs.get("lines", 6)
        self._category = kwargs.get("category", "mixed")
        self._custom_slides: list = kwargs.get("custom_slides", [])

        # Skip config screen when launched from preset menu
        if kwargs:
            self._build_and_start()
            return

        self.add_nav_bar()

        container = QWidget()
        container.setStyleSheet(f"background-color: {c['bg']};")
        cl = QVBoxLayout(container)
        cl.setContentsMargins(40, 20, 40, 20)
        cl.setSpacing(10)

        # Guide button
        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        guide_btn = QPushButton(tr("chunking.guide"))
        guide_btn.setFont(make_qfont("btn_sm"))
        guide_btn.setStyleSheet(
            f"background-color: {c['accent']}; color: {c['btn_text']}; "
            f"border: 2px solid transparent; padding: 4px 12px; border-radius: 3px;"
        )
        guide_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        guide_btn.clicked.connect(
            lambda: self.show_guide("slide_processing")
        )
        top.addWidget(guide_btn)
        top.addStretch()
        cl.addLayout(top)

        title = QLabel(tr("slide.processing.slide_processing"))
        title.setFont(make_qfont("section_header"))
        title.setStyleSheet(f"color: {c['accent']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(title)

        cl.addSpacing(10)

        slider_groove = (
            f"QSlider::groove:horizontal {{ background: {c['card']}; "
            f"height: 6px; border-radius: 3px; }}"
            f"QSlider::handle:horizontal {{ background: {c['accent']}; "
            f"width: 16px; margin: -5px 0; border-radius: 8px; }}"
        )

        # Category selector
        cat_row = QHBoxLayout()
        cat_row.addStretch()
        cat_lbl = QLabel(tr("slide.processing.category"))
        cat_lbl.setFont(make_qfont("slider_label"))
        cat_lbl.setStyleSheet(f"color: {c['fg']};")
        cat_row.addWidget(cat_lbl)

        self._cat_combo = QComboBox()
        self._cat_combo.addItems([
            "Mixed", "Science", "Business", "Geography",
            "Motivation", "Neuroplasticity", "Humor",
            "History", "Nutrition",
        ])
        idx = {
            "mixed": 0, "science": 1, "business": 2, "geography": 3,
            "motivation": 4, "neuroplasticity": 5, "humor": 6,
            "history": 7, "nutrition": 8,
        }.get(self._category, 0)
        self._cat_combo.setCurrentIndex(idx)
        self._cat_combo.setStyleSheet(
            f"QComboBox {{ background-color: {c['card']}; color: {c['fg']}; "
            f"border: 1px solid {c['muted']}; padding: 4px 8px; "
            f"border-radius: 3px; }}"
            f"QComboBox::drop-down {{ border: none; }}"
            f"QComboBox QAbstractItemView {{ background-color: {c['card']}; "
            f"color: {c['fg']}; selection-background-color: {c['accent']}; }}"
        )
        self._cat_combo.setFixedWidth(180)
        cat_row.addWidget(self._cat_combo)
        cat_row.addStretch()
        cl.addLayout(cat_row)

        # Display time
        time_row = QHBoxLayout()
        time_row.addStretch()
        time_lbl = QLabel(tr("slide.processing.display_time_s"))
        time_lbl.setFont(make_qfont("slider_label"))
        time_lbl.setStyleSheet(f"color: {c['fg']};")
        time_row.addWidget(time_lbl)

        self._time_slider = QSlider(Qt.Orientation.Horizontal)
        self._time_slider.setRange(cfg["min_display_s"], cfg["max_display_s"])
        self._time_slider.setValue(self._display_s)
        self._time_slider.setFixedWidth(250)
        self._time_slider.setStyleSheet(slider_groove)

        self._time_display = QLabel(str(self._display_s))
        self._time_display.setFont(make_qfont("counter"))
        self._time_display.setStyleSheet(f"color: {c['accent']};")
        self._time_display.setFixedWidth(50)
        self._time_slider.valueChanged.connect(
            lambda v: self._time_display.setText(str(v))
        )
        time_row.addWidget(self._time_slider)
        time_row.addWidget(self._time_display)
        time_row.addStretch()
        cl.addLayout(time_row)

        # Number of slides
        slides_row = QHBoxLayout()
        slides_row.addStretch()
        slides_lbl = QLabel(tr("slide.processing.slides"))
        slides_lbl.setFont(make_qfont("slider_label"))
        slides_lbl.setStyleSheet(f"color: {c['fg']};")
        slides_row.addWidget(slides_lbl)

        self._slides_slider = QSlider(Qt.Orientation.Horizontal)
        self._slides_slider.setRange(cfg["min_slides"], cfg["max_slides"])
        self._slides_slider.setValue(self._total_slides)
        self._slides_slider.setFixedWidth(250)
        self._slides_slider.setStyleSheet(slider_groove)

        self._slides_display = QLabel(str(self._total_slides))
        self._slides_display.setFont(make_qfont("counter"))
        self._slides_display.setStyleSheet(f"color: {c['accent']};")
        self._slides_display.setFixedWidth(50)
        self._slides_slider.valueChanged.connect(
            lambda v: self._slides_display.setText(str(v))
        )
        slides_row.addWidget(self._slides_slider)
        slides_row.addWidget(self._slides_display)
        slides_row.addStretch()
        cl.addLayout(slides_row)

        cl.addSpacing(20)

        # Start button
        start_btn = QPushButton(tr("mot.start"))
        start_btn.setFont(make_qfont("btn_lg"))
        start_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['accent']}; "
            f"color: {c['btn_text']}; border: 2px solid transparent; "
            f"padding: 12px 50px; border-radius: 4px; }}"
        )
        start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        start_btn.clicked.connect(self._begin_exercise)
        cl.addWidget(start_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        shortcut.activated.connect(self._begin_exercise)

        cl.addStretch()
        self._layout.addWidget(container, 1)

    def _begin_exercise(self) -> None:
        self._display_s = self._time_slider.value()
        self._total_slides = self._slides_slider.value()
        cat_names = ["mixed", "science", "business", "geography",
                     "motivation", "neuroplasticity", "humor",
                     "history", "nutrition"]
        self._category = cat_names[self._cat_combo.currentIndex()]
        self._build_and_start()

    def _build_and_start(self) -> None:
        # Build slide pool from selected categories
        pool = []
        cats = self._category.split(",")
        if "custom_only" not in cats:
            if "mixed" in cats:
                for slides in SLIDE_LIBRARY.values():
                    pool.extend(slides)
            else:
                for cat in cats:
                    pool.extend(SLIDE_LIBRARY.get(cat.strip(), []))

        # Add custom slides
        if self._custom_slides:
            pool.extend(self._custom_slides)

        if not pool:
            for slides in SLIDE_LIBRARY.values():
                pool.extend(slides)

        random.shuffle(pool)
        self._slides = pool[:self._total_slides]
        # If not enough slides, allow repeats
        while len(self._slides) < self._total_slides:
            extra = list(pool)
            random.shuffle(extra)
            self._slides.extend(extra[:self._total_slides - len(self._slides)])

        self._slide_idx = 0
        self._correct = 0
        self._total_questions = 0
        self._show_slide()

    # ── Bullet/question mapping ──

    @staticmethod
    def _question_bullet_idx(
        question: tuple, bullets: list[str],
    ) -> int | None:
        """Return the bullet index a question's answer references, or None."""
        _, choices, correct_idx = question
        answer = choices[correct_idx].lower()

        # Extract numbers (digits, decimals, commas) from the answer
        answer_nums = set(re.findall(r"[\d,]+\.?\d*", answer))

        for i, b in enumerate(bullets):
            bl = b.lower()
            # Direct substring match
            if answer in bl:
                return i
            # Number-based match: all numbers in the answer appear in bullet
            if answer_nums:
                bullet_nums = set(re.findall(r"[\d,]+\.?\d*", bl))
                if answer_nums and answer_nums.issubset(bullet_nums):
                    return i
        return None

    @staticmethod
    def _shuffle_choices(question: tuple) -> tuple:
        """Return question with answer choices in random order."""
        q_text, choices, correct_idx = question
        correct_answer = choices[correct_idx]
        shuffled = list(choices)
        random.shuffle(shuffled)
        new_idx = shuffled.index(correct_answer)
        return (q_text, shuffled, new_idx)

    def _select_bullets_and_questions(
        self, bullets: list[str], questions: list,
    ) -> tuple[list[str], list]:
        """Pick a subset of bullets and return only answerable questions.

        Bullets are shuffled. Questions are shuffled and their answer
        choices are randomised so repeated plays feel different.
        """
        n = min(self._lines_per_slide, len(bullets))
        if n >= len(bullets):
            shuffled_bullets = list(bullets)
            random.shuffle(shuffled_bullets)
            shuffled_qs = [self._shuffle_choices(q) for q in questions]
            random.shuffle(shuffled_qs)
            return shuffled_bullets, shuffled_qs

        # Map each question to its source bullet
        q_map: list[tuple[int, tuple]] = []
        unmapped: list[tuple] = []
        for q in questions:
            idx = self._question_bullet_idx(q, bullets)
            if idx is not None:
                q_map.append((idx, q))
            else:
                unmapped.append(q)

        # Ensure we pick bullets that cover as many questions as possible
        needed_indices = {idx for idx, _ in q_map}
        # Start with bullet indices that have questions
        chosen = set()
        if len(needed_indices) <= n:
            chosen = set(needed_indices)
        else:
            # Pick n indices prioritising those with questions
            chosen = set(random.sample(sorted(needed_indices), n))

        # Fill remaining slots with random other bullets
        remaining = [i for i in range(len(bullets)) if i not in chosen]
        random.shuffle(remaining)
        while len(chosen) < n and remaining:
            chosen.add(remaining.pop())

        selected_bullets = [bullets[i] for i in chosen]
        random.shuffle(selected_bullets)

        # Filter questions to those whose source bullet is shown
        valid_qs = [q for idx, q in q_map if idx in chosen]
        # Include unmapped questions (can't determine source, keep them)
        valid_qs.extend(unmapped)

        # Ensure at least 2 questions if possible
        if len(valid_qs) < 2 and len(questions) >= 2:
            for idx, q in q_map:
                if q not in valid_qs:
                    valid_qs.append(q)
                    if len(valid_qs) >= 2:
                        break

        # Shuffle question order and answer choices
        valid_qs = [self._shuffle_choices(q) for q in valid_qs]
        random.shuffle(valid_qs)

        return selected_bullets, valid_qs

    # ── Slide display ──

    def _show_slide(self) -> None:
        if not self._running:
            return
        if self._slide_idx >= len(self._slides):
            self._show_results()
            return

        self._clear()
        self._running = True

        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")
        self._current_slide = self._slides[self._slide_idx]
        title, bullets, questions = self._current_slide

        # Subset bullets and filter questions based on lines setting
        show_bullets, self._current_questions = (
            self._select_bullets_and_questions(bullets, questions)
        )

        # Top bar
        top = QHBoxLayout()
        top.setContentsMargins(10, 6, 10, 2)

        self._progress_lbl = QLabel(
            f"Slide {self._slide_idx + 1}/{len(self._slides)}"
        )
        self._progress_lbl.setFont(make_qfont("counter"))
        self._progress_lbl.setStyleSheet(f"color: {c['accent']};")
        top.addWidget(self._progress_lbl)

        top.addStretch()

        self._countdown_lbl = QLabel(f"{self._display_s}s")
        self._countdown_lbl.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        self._countdown_lbl.setStyleSheet(f"color: {c['alert']};")
        top.addWidget(self._countdown_lbl)

        top.addStretch()

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

        # Slide card
        card = QFrame()
        card.setStyleSheet(
            f"background-color: {c['card']}; border-radius: 8px; "
            f"padding: 20px;"
        )
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(12)
        card_layout.setContentsMargins(30, 20, 30, 20)

        # Title
        title_lbl = QLabel(title.upper())
        title_lbl.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        title_lbl.setStyleSheet(f"color: {c['accent']};")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_lbl.setWordWrap(True)
        card_layout.addWidget(title_lbl)

        card_layout.addSpacing(10)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {c['muted']};")
        card_layout.addWidget(sep)

        card_layout.addSpacing(8)

        # Bullet points
        for bullet in show_bullets:
            bullet_lbl = QLabel(f"  •  {bullet}")
            bullet_lbl.setFont(QFont("Arial", 15))
            bullet_lbl.setStyleSheet(f"color: {c['fg']};")
            bullet_lbl.setWordWrap(True)
            card_layout.addWidget(bullet_lbl)

        card_layout.addStretch()
        self._layout.addWidget(card, 1)

        # Start countdown
        self._countdown_remaining = self._display_s
        self._countdown_timer = QTimer(self)
        self._countdown_timer.setInterval(1000)
        self._countdown_timer.timeout.connect(self._tick_countdown)
        self._countdown_timer.start()

    def _tick_countdown(self) -> None:
        self._countdown_remaining -= 1
        c = COLORS
        if self._countdown_remaining <= 0:
            if self._countdown_timer:
                self._countdown_timer.stop()
                self._countdown_timer = None
            self._question_idx = 0
            self._show_question()
        else:
            if self._countdown_lbl:
                self._countdown_lbl.setText(f"{self._countdown_remaining}s")
                # Color shift as time runs out
                if self._countdown_remaining <= 2:
                    self._countdown_lbl.setStyleSheet(
                        f"color: {c['alert']}; font-weight: bold;"
                    )

    # ── Questions ──

    def _show_question(self) -> None:
        if not self._running or not self._current_slide:
            return

        questions = self._current_questions
        if self._question_idx >= len(questions):
            self._slide_idx += 1
            self._show_slide()
            return

        self._clear()
        self._running = True

        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")

        q_text, choices, correct_idx = questions[self._question_idx]
        self._total_questions += 1

        # Top bar
        top = QHBoxLayout()
        top.setContentsMargins(10, 6, 10, 2)

        slide_info = QLabel(
            f"Slide {self._slide_idx + 1}/{len(self._slides)}  |  "
            f"Q{self._question_idx + 1}/{len(questions)}"
        )
        slide_info.setFont(make_qfont("counter"))
        slide_info.setStyleSheet(f"color: {c['accent']};")
        top.addWidget(slide_info)

        top.addStretch()

        score_lbl = QLabel(
            f"Score: {self._correct}/{self._total_questions - 1}"
        )
        score_lbl.setFont(make_qfont("counter"))
        score_lbl.setStyleSheet(f"color: {c['fg']};")
        top.addWidget(score_lbl)

        top.addStretch()

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

        # Question
        q_lbl = QLabel(q_text)
        q_lbl.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        q_lbl.setStyleSheet(f"color: {c['fg']};")
        q_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        q_lbl.setWordWrap(True)
        self._layout.addWidget(q_lbl)

        self._layout.addSpacing(20)

        # Answer buttons
        for i, choice in enumerate(choices):
            btn = QPushButton(f"  {i + 1}.  {choice}")
            btn.setFont(QFont("Arial", 14))
            btn.setFixedHeight(45)
            btn.setStyleSheet(
                f"QPushButton {{ background-color: {c['card']}; "
                f"color: {c['fg']}; border: 1px solid {c['muted']}; "
                f"padding: 8px 20px; border-radius: 4px; "
                f"text-align: left; }}"
                f"QPushButton:hover {{ background-color: {c['accent']}; "
                f"color: {c['btn_text']}; }}"
            )
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(
                lambda _, idx=i: self._check_answer(idx, correct_idx)
            )
            self._layout.addWidget(
                btn, 0, Qt.AlignmentFlag.AlignCenter
            )
            btn.setFixedWidth(500)

        self._layout.addStretch()

        # Keyboard shortcuts 1-4
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()

    def keyPressEvent(self, event) -> None:
        if event.isAutoRepeat():
            return
        key = event.key()
        if self._current_slide and self._question_idx < len(
            self._current_questions
        ):
            questions = self._current_questions
            _, _, correct_idx = questions[self._question_idx]
            num_choices = len(questions[self._question_idx][1])
            if key == Qt.Key.Key_1 and num_choices >= 1:
                self._check_answer(0, correct_idx)
                return
            if key == Qt.Key.Key_2 and num_choices >= 2:
                self._check_answer(1, correct_idx)
                return
            if key == Qt.Key.Key_3 and num_choices >= 3:
                self._check_answer(2, correct_idx)
                return
            if key == Qt.Key.Key_4 and num_choices >= 4:
                self._check_answer(3, correct_idx)
                return
        super().keyPressEvent(event)

    def _check_answer(self, chosen: int, correct: int) -> None:
        if not self._running:
            return

        c = COLORS
        is_correct = chosen == correct

        if is_correct:
            self._correct += 1

        # Show feedback briefly
        self._clear()
        self._running = True
        self.setStyleSheet(f"background-color: {c['bg']};")

        self._layout.addStretch()

        if is_correct:
            fb = QLabel(tr("slide.processing.u2714_correct"))
            fb.setStyleSheet(f"color: {c['success']};")
        else:
            questions = self._current_questions
            _, choices, correct_idx = questions[self._question_idx]
            fb = QLabel(f"\u2718  Answer: {choices[correct_idx]}")
            fb.setStyleSheet(f"color: {c['alert']};")

        fb.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        fb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(fb)

        self._layout.addStretch()

        self._question_idx += 1
        self._after(1200, self._show_question)

    # ── Results ──

    def _show_results(self) -> None:
        self._running = False
        c = COLORS

        total_q = self._total_questions
        accuracy_pct = (
            round(self._correct / total_q * 100) if total_q > 0 else 0
        )
        xp = self._correct * USER_DATA_CONFIG["xp_per_correct"]

        result = ExerciseResult(
            exercise_name="SLIDE PROCESSING",
            score=self._correct,
            total=total_q,
            xp_gained=xp,
            metadata={
                "category": self._category,
                "display_s": self._display_s,
                "slides": len(self._slides),
                "lines_per_slide": self._lines_per_slide,
                "accuracy_pct": accuracy_pct,
            },
        )
        is_pb = self.complete(result)

        self.show_result_screen(
            result,
            is_personal_best=is_pb,
            details=(
                f"{tr('result.category', cat=self._category)}  |  "
                f"{tr('result.display_time', s=self._display_s)}  |  "
                f"{tr('result.slides', count=len(self._slides))}  |  "
                f"{tr('result.lines', count=self._lines_per_slide)}\n"
                f"{tr('result.questions', correct=self._correct, total=total_q)}  |  "
                f"{tr('result.accuracy', pct=accuracy_pct)}"
            ),
        )

        # Rewire CONTINUE to go back to menu
        for btn in self.findChildren(QPushButton):
            if btn.text() == "CONTINUE":
                btn.disconnect()
                btn.clicked.connect(self.navigator.finish_exercise)

    def _stop(self) -> None:
        self._running = False
        if self._countdown_timer:
            self._countdown_timer.stop()
            self._countdown_timer = None
        for timer in self._timers:
            timer.stop()
        self._timers.clear()
        self.navigator.finish_exercise()
