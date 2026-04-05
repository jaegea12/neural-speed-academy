"""
Introduction screen with science-backed training overview,
use cases, and exercise descriptions.
"""
from __future__ import annotations

from PyQt6.QtWidgets import QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt

from neural_speed_academy.screens.base import BaseScreen, make_scroll_area
from neural_speed_academy.theme import COLORS, make_qfont


# Entry types: "section" (header + body), "fact" (highlighted callout)
INTRO_CONTENT = [
    # ── Opening ──
    ("section", "WHAT IS NEURAL SPEED ACADEMY?",
     "Your brain processes far more information than you consciously use. "
     "Neural Speed Academy trains the visual, cognitive, and reading skills "
     "that unlock that capacity \u2014 through 15 targeted exercises, "
     "16 structured training paths, and detailed progress tracking.\n\n"
     "Every exercise produces measurable scores. Every session is logged. "
     "Whether you train alone, in a classroom, or in a clinical setting, "
     "your progress is visible and exportable."),

    # ── Who is this for? ──
    ("section", "WHO IS THIS FOR?",
     "\u2022 Students \u2014 Read textbooks faster, retain more for exams, "
     "and process lecture material efficiently. Spaced repetition and "
     "comprehension exercises directly support study workflows.\n\n"
     "\u2022 Professionals \u2014 Handle information overload. Scan reports, "
     "process emails, and extract key facts faster. Decision speed and "
     "divided attention exercises transfer to high-pressure work.\n\n"
     "\u2022 ADHD / Autism \u2014 Structured focus training with clear goals "
     "and immediate feedback. Visual exercises build sustained attention "
     "without relying on text-heavy tasks. 9 color profiles reduce "
     "sensory overload.\n\n"
     "\u2022 Seniors \u2014 Maintain cognitive sharpness. Reaction time, "
     "working memory, and attention exercises are among the most "
     "evidence-backed interventions for healthy cognitive aging.\n\n"
     "\u2022 Athletes \u2014 Peripheral vision, object tracking, and rapid "
     "decision-making directly improve field awareness and split-second "
     "reactions in competitive sports.\n\n"
     "\u2022 Clinicians & Researchers \u2014 Measurable baselines, per-user "
     "profiles, session history, and CSV/JSON export provide the data "
     "needed for clinical assessment and research protocols."),

    ("fact", None,
     "Reaction time is one of the strongest predictors of cognitive "
     "health in aging research. A 2014 meta-analysis found that "
     "computerized cognitive training improved processing speed by "
     "0.31 standard deviations in older adults (Lampit et al., PLOS Medicine)."),

    # ── Perception ──
    ("section", "PERCEPTION \u2014 5 EXERCISES",
     "Perception exercises train the raw speed and width of your visual "
     "intake \u2014 how much you see in a single glance.\n\n"
     "\u2022 Flash Numbers \u2014 Digits appear for a fraction of a second. "
     "You recall them. This trains iconic memory \u2014 the brief visual "
     "buffer that determines how much you capture per eye fixation. "
     "The same skill that lets a chess master see a board position "
     "in one glance.\n\n"
     "\u2022 Word Drills \u2014 Whole words flashed at increasing speed. "
     "Builds instant word recognition so reading becomes pattern "
     "matching rather than letter-by-letter decoding.\n\n"
     "\u2022 Eye-Span \u2014 Two items appear at the edges of your vision. "
     "You identify both. This widens your perceptual span \u2014 trained "
     "readers fixate 2\u20133 times per line instead of 5\u20137.\n\n"
     "\u2022 Schulte Grid \u2014 Find numbers 1\u201325 in sequence on a grid "
     "without moving your eyes from center. Expands peripheral awareness "
     "\u2014 the same skill that lets you scan a page, notice a car "
     "approaching from the side, or read a dashboard at a glance.\n\n"
     "\u2022 Peripheral Flash \u2014 Stimuli appear briefly in your side "
     "vision. Strengthens the visual field that most people underuse. "
     "Athletes, pilots, and drivers rely on this skill constantly."),

    ("fact", None,
     "Your peripheral vision covers over 180\u00b0 of your visual field "
     "but most people only actively use the central 2\u20135\u00b0 for reading. "
     "Training peripheral awareness can reduce the number of eye "
     "fixations per line by 40\u201360%."),

    # ── Cognition ──
    ("section", "COGNITION \u2014 5 EXERCISES",
     "Cognition exercises train the processing layer \u2014 how fast you "
     "think, decide, and hold information in mind.\n\n"
     "\u2022 Sequence Memory \u2014 Reproduce increasingly long sequences of "
     "numbers, letters, or colors. Working memory capacity predicts "
     "academic performance, problem-solving ability, and reading "
     "comprehension. This is one of the most researched cognitive "
     "training tasks.\n\n"
     "\u2022 Rapid Decision \u2014 Find targets on a grid under time pressure. "
     "Trains the speed-accuracy tradeoff that governs real-world "
     "decisions \u2014 from choosing the right lane in traffic to "
     "selecting the right answer under exam pressure.\n\n"
     "\u2022 Object Tracking (MOT) \u2014 Track 3\u20135 moving dots among "
     "distractors. This is the gold standard for divided attention "
     "research. Used by professional sports teams (NHL, Premier League) "
     "to train field awareness.\n\n"
     "\u2022 Split Attention \u2014 Process a word task and a shape task "
     "simultaneously. Real life rarely presents one thing at a time "
     "\u2014 this exercise trains the ability to handle parallel demands.\n\n"
     "\u2022 Reaction Time \u2014 Simple, choice, and go/no-go modes measure "
     "and improve response speed. Go/no-go specifically trains impulse "
     "control \u2014 the ability to withhold a response when needed."),

    ("fact", None,
     "Working memory training can transfer to fluid intelligence. "
     "Jaeggi et al. (2008, PNAS) showed that dual n-back training "
     "improved reasoning ability in proportion to training duration. "
     "Sequence Memory exercises target the same underlying capacity."),

    # ── Reading ──
    ("section", "READING \u2014 5 EXERCISES",
     "Reading exercises target the four bottlenecks that limit reading "
     "speed: too many fixations, regression (re-reading), subvocalization "
     "(inner voice), and narrow attention span.\n\n"
     "\u2022 Pacer & Quiz \u2014 Text scrolls at a set WPM, forcing forward "
     "momentum. Eliminates regression \u2014 the habit of re-reading that "
     "wastes 10\u201315% of reading time. Comprehension quiz afterward "
     "ensures speed doesn't sacrifice understanding.\n\n"
     "\u2022 RSVP Reader \u2014 One word at a time, faster than you can "
     "speak. This breaks the subvocalization barrier \u2014 the inner "
     "voice that limits most readers to ~150 WPM. Forces direct "
     "visual-to-meaning processing.\n\n"
     "\u2022 Chunking \u2014 Text is highlighted in 2\u20137 word groups. "
     "Trains your eyes to process phrases as single units instead of "
     "individual words. The same skill that lets experienced readers "
     "absorb a sentence in 2\u20133 fixations.\n\n"
     "\u2022 Spaced Repetition \u2014 The SM-2 algorithm schedules reviews "
     "at optimal intervals for long-term retention. Used by medical "
     "students, language learners, and anyone who needs to remember "
     "large amounts of information.\n\n"
     "\u2022 Slide Processing \u2014 Read a passage for a limited time, "
     "then answer questions from memory. Trains active reading \u2014 "
     "the habit of extracting key information on the first pass."),

    ("fact", None,
     "An average reader processes 200\u2013250 words per minute. "
     "Research shows that 4 weeks of consistent training typically "
     "produces 50\u2013100% speed gains while maintaining comprehension. "
     "The key is daily practice, not marathon sessions."),

    # ── Eye Warmup ──
    ("section", "EYE WARMUP",
     "The Eye Warmup (Priming) exercise guides your eyes through "
     "smooth pursuit, saccade, and convergence patterns. Use it before "
     "training sessions to prepare the extraocular muscles and reduce "
     "eye strain.\n\n"
     "Think of it as stretching before a workout. 60\u201390 seconds of "
     "eye priming improves tracking accuracy and reduces fatigue "
     "during longer training sessions."),

    # ── Training Paths ──
    ("section", "TRAINING PATHS",
     "16 structured paths organize exercises into progressive sessions "
     "so you don't have to plan your own training:\n\n"
     "\u2022 Speed Reading \u2014 Daily Warmup, Foundation, and paths "
     "targeting 300 / 400 / 600 / 800 WPM. Each path builds on the "
     "previous one with increasing difficulty.\n"
     "\u2022 Cognitive \u2014 Perception Master, Memory Foundations, "
     "Attention & Focus, Mental Agility.\n"
     "\u2022 Visual \u2014 Peripheral Vision, Visual Tracking.\n"
     "\u2022 Comprehension \u2014 Rapid Comprehension, Study Session.\n"
     "\u2022 Mixed \u2014 Full Brain Workout, Quick Cognitive Check.\n\n"
     "Paths track your progress step by step. Pick up where you "
     "left off, or restart anytime."),

    # ── Analytics ──
    ("section", "TRACKING & ANALYTICS",
     "Every session is recorded automatically:\n\n"
     "\u2022 XP and leveling system for motivation and progress.\n"
     "\u2022 Personal bests with exercise-appropriate metrics "
     "(accuracy, time, WPM, reaction time).\n"
     "\u2022 Training consistency calendar \u2014 see your active days "
     "at a glance.\n"
     "\u2022 Per-exercise progress charts with trend lines.\n"
     "\u2022 Tiered insights \u2014 immediate session feedback, 7-day "
     "trends, and long-term strength/weakness analysis.\n"
     "\u2022 Full session history with CSV and JSON export for "
     "research, clinical reports, or personal records."),

    # ── Accessibility ──
    ("section", "ACCESSIBILITY",
     "Neural Speed Academy is designed to be usable by everyone:\n\n"
     "\u2022 9 color profiles including high contrast, warm focus, "
     "and monochrome options for visual sensitivities.\n"
     "\u2022 Adjustable font scale (80\u2013150%) for comfortable reading.\n"
     "\u2022 Per-user preferences \u2014 each profile remembers its own "
     "theme and font size.\n"
     "\u2022 Keyboard navigation for all core functions.\n"
     "\u2022 Clean, distraction-free interface designed for focus."),

    # ── Expectations ──
    ("fact", None,
     "Divided attention improves with practice even in adults over 60. "
     "A 2013 study (Anguera et al., Nature) showed that multitasking "
     "training in older adults produced gains that transferred to "
     "sustained attention and working memory."),

    ("section", "REALISTIC EXPECTATIONS",
     "Research supports that consistent training (15\u201320 min/day, "
     "4\u20135 days/week) produces measurable gains within 2\u20134 weeks.\n\n"
     "\u2022 Reading speed: 50\u2013100% improvement is typical.\n"
     "\u2022 Working memory: gains appear after 2\u20133 weeks of daily "
     "practice.\n"
     "\u2022 Reaction time: measurable improvement within days.\n"
     "\u2022 Peripheral awareness: noticeable expansion within 1\u20132 "
     "weeks.\n\n"
     "The key is consistency, not intensity. Short daily sessions "
     "outperform occasional long ones.\n\n"
     "Claims of 1000+ WPM with full comprehension are not supported "
     "by peer-reviewed research. This program focuses on achievable, "
     "evidence-backed improvements."),

    # ── Limitations & Transfer ──
    ("section", "LIMITATIONS \u2014 WHAT THIS APP CANNOT DO",
     "Neural Speed Academy trains component skills in isolation. "
     "That training only becomes useful when you apply it to real "
     "tasks. Important things to understand:\n\n"
     "\u2022 Exercises are not a substitute for reading. Improving "
     "your RSVP speed or peripheral span means nothing if you don't "
     "practice reading actual books, articles, and documents.\n\n"
     "\u2022 Speed without comprehension is not reading. If you can't "
     "recall or explain what you read, you were scanning, not "
     "reading. Always test yourself.\n\n"
     "\u2022 Transfer is not automatic. Research shows that cognitive "
     "training gains are strongest on tasks similar to the training. "
     "Broader transfer (e.g., from Sequence Memory to exam "
     "performance) requires deliberate effort to apply the skills.\n\n"
     "\u2022 No app replaces professional help. If you have a diagnosed "
     "reading disability, ADHD, or visual processing disorder, this "
     "app can supplement \u2014 but not replace \u2014 guidance from a "
     "qualified specialist."),

    ("fact", None,
     "A 2016 review (Simons et al., Psychological Science in the "
     "Public Interest) found that cognitive training reliably improves "
     "performance on trained tasks, but evidence for broad transfer "
     "to everyday abilities remains limited. The most effective "
     "approach combines targeted training with real-world practice."),

    ("section", "HOW TO GET THE MOST OUT OF YOUR TRAINING",
     "Combine app exercises with deliberate real-world practice:\n\n"
     "\u2022 Train 15\u201320 minutes, then read for 20+ minutes. Apply "
     "what you practiced \u2014 wider fixations, fewer regressions, "
     "chunking phrases.\n\n"
     "\u2022 Use active reading strategies. Before reading, skim "
     "headings and structure. While reading, ask yourself questions. "
     "After reading, summarize from memory.\n\n"
     "\u2022 Take notes. Mind maps, margin annotations, or brief "
     "summaries force you to process what you read. Speed without "
     "retention is wasted effort.\n\n"
     "\u2022 Vary your material. Practice with textbooks, news "
     "articles, fiction, and technical documents. Each demands "
     "different reading strategies.\n\n"
     "\u2022 Track your real-world progress. Time yourself reading "
     "a chapter, then test recall. Your app scores should correlate "
     "with real improvements \u2014 if they don't, adjust your "
     "approach."),
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

        for entry in INTRO_CONTENT:
            entry_type = entry[0]

            if entry_type == "section":
                _, section_title, section_body = entry
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

            elif entry_type == "fact":
                _, _, fact_text = entry
                card = QFrame()
                card.setStyleSheet(
                    f"background-color: {c['card']}; "
                    f"border-left: 3px solid {c['accent']}; "
                    f"border-radius: 4px; padding: 12px 16px;"
                )
                card_layout = QVBoxLayout(card)
                card_layout.setContentsMargins(0, 0, 0, 0)

                did_you_know = QLabel("DID YOU KNOW?")
                did_you_know.setFont(make_qfont("btn_sm"))
                did_you_know.setStyleSheet(f"color: {c['accent']};")
                card_layout.addWidget(did_you_know)

                fact = QLabel(fact_text)
                fact.setFont(make_qfont("body"))
                fact.setStyleSheet(f"color: {c['text_on_card']};")
                fact.setWordWrap(True)
                card_layout.addWidget(fact)

                cl.addWidget(card)
                cl.addSpacing(15)
