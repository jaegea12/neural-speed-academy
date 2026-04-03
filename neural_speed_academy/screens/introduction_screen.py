"""
Introduction screen with speed reading science and training overview.
"""
from __future__ import annotations

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt

from neural_speed_academy.screens.base import BaseScreen, make_scroll_area
from neural_speed_academy.theme import COLORS, make_qfont


INTRO_SECTIONS = [
    ("WHAT IS NEURAL SPEED ACADEMY?",
     "Neural Speed Academy trains the visual, cognitive, and reading skills "
     "that determine how fast and accurately you process information. "
     "The program combines 15 exercises across three categories with "
     "16 structured training paths, progress tracking, and adaptive difficulty.\n\n"
     "It is designed for individual learners, schools, clinics, and "
     "research settings. All exercises produce measurable scores that "
     "can be tracked over time."),

    ("PERCEPTION \u2014 5 EXERCISES",
     "\u2022 Flash Numbers \u2014 Briefly displayed digits train iconic memory "
     "and rapid number recognition.\n"
     "\u2022 Word Drills \u2014 Flash words at increasing speed to build "
     "instant word recognition.\n"
     "\u2022 Eye-Span \u2014 Widens the perceptual span so each eye fixation "
     "captures more text.\n"
     "\u2022 Schulte Grid \u2014 Find numbers in sequence on a grid to expand "
     "peripheral awareness without moving the eyes.\n"
     "\u2022 Peripheral Flash \u2014 Identify stimuli shown briefly in your "
     "peripheral vision to strengthen side awareness."),

    ("COGNITION \u2014 5 EXERCISES",
     "\u2022 Sequence Memory \u2014 Reproduce increasingly long sequences of "
     "numbers, letters, or colors to train working memory.\n"
     "\u2022 Rapid Decision \u2014 Find targets on a grid under time pressure "
     "to build decision speed and accuracy.\n"
     "\u2022 Object Tracking (MOT) \u2014 Track multiple moving objects "
     "simultaneously to train divided attention.\n"
     "\u2022 Split Attention \u2014 Process a central word task and a "
     "peripheral shape task at the same time.\n"
     "\u2022 Reaction Time \u2014 Measure and improve response speed across "
     "simple, choice, and go/no-go modes."),

    ("READING \u2014 5 EXERCISES",
     "\u2022 Pacer & Quiz \u2014 Guided reading at a set WPM with "
     "comprehension questions afterward.\n"
     "\u2022 RSVP Reader \u2014 Rapid Serial Visual Presentation flashes "
     "one word at a time, breaking the subvocalization barrier.\n"
     "\u2022 Chunking \u2014 Read text in highlighted phrase groups to "
     "train block processing.\n"
     "\u2022 Spaced Repetition \u2014 SM-2 algorithm for long-term "
     "vocabulary and concept retention.\n"
     "\u2022 Slide Processing \u2014 Read a passage, then answer "
     "comprehension questions from memory."),

    ("EYE WARMUP",
     "The Eye Warmup (Priming) exercise guides your eyes through "
     "smooth pursuit, saccade, and convergence patterns. Use it before "
     "training sessions to prepare the extraocular muscles and reduce "
     "eye strain."),

    ("TRAINING PATHS",
     "16 structured paths organize exercises into progressive sessions:\n\n"
     "\u2022 Speed Reading \u2014 Daily Warmup, Foundation, and paths "
     "targeting 300/400/600/800 WPM.\n"
     "\u2022 Cognitive \u2014 Perception Master, Memory Foundations, "
     "Attention & Focus, Mental Agility.\n"
     "\u2022 Visual \u2014 Peripheral Vision, Visual Tracking.\n"
     "\u2022 Comprehension \u2014 Rapid Comprehension, Study Session.\n"
     "\u2022 Mixed \u2014 Full Brain Workout, Quick Cognitive Check.\n\n"
     "Paths track your progress and guide you through exercises in "
     "an effective order."),

    ("TRACKING & ANALYTICS",
     "Your performance is tracked automatically:\n\n"
     "\u2022 XP and leveling system for motivation.\n"
     "\u2022 Personal bests per exercise with exercise-appropriate metrics.\n"
     "\u2022 Training consistency calendar showing active days.\n"
     "\u2022 Per-exercise progress charts with trend lines.\n"
     "\u2022 Tiered insights: immediate feedback, 7-day trends, and "
     "long-term strength/weakness analysis.\n"
     "\u2022 Session history with CSV/JSON export for research use."),

    ("REALISTIC EXPECTATIONS",
     "Research supports that consistent training (15\u201320 min/day, "
     "4\u20135 days/week) produces measurable gains within 2\u20134 weeks. "
     "Most people can improve their reading speed significantly while "
     "maintaining comprehension. Cognitive exercises like working memory "
     "and attention training show transfer effects when practiced "
     "regularly over several weeks.\n\n"
     "Claims of 1000+ WPM with full comprehension are not supported "
     "by peer-reviewed research."),
]


class IntroductionScreen(BaseScreen):

    def build(self, **kwargs) -> None:
        c = COLORS
        self.setStyleSheet(f"background-color: {c['bg']};")
        self.add_nav_bar()

        scroll, content, cl = make_scroll_area(self._layout)
        cl.setContentsMargins(60, 20, 60, 30)

        title = QLabel("INTRODUCTION")
        title.setFont(make_qfont("header"))
        title.setStyleSheet(f"color: {c['accent']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(title)
        cl.addSpacing(10)

        for section_title, section_body in INTRO_SECTIONS:
            sec = QLabel(section_title)
            sec.setFont(make_qfont("section_header"))
            sec.setStyleSheet(f"color: {c['fg']};")
            cl.addWidget(sec)
            cl.addSpacing(4)

            body = QLabel(section_body)
            body.setFont(make_qfont("body"))
            body.setStyleSheet(f"color: {c['fg']};")
            body.setWordWrap(True)
            cl.addWidget(body)
            cl.addSpacing(15)
