"""
Shared comprehension recall system for text-based exercises.

Extracts keywords from source text using lightweight stemming,
scores the user's summary with stem-aware matching and partial credit,
and displays results with keyword breakdown.
"""
from __future__ import annotations

import re
from typing import Callable

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QFrame,
)
from PyQt6.QtCore import Qt

from neural_speed_academy.theme import COLORS, make_qfont, input_css, screen_metrics
# Regex pattern for word tokenisation — includes accented Latin characters
# so that German (ä ö ü ß), French (é è ê ë ç), Spanish (ñ á í ó ú),
# Italian, and Portuguese words are captured correctly.
_WORD_RE = re.compile(r"[a-zA-ZÀ-ÖØ-öø-ÿ]+")

from neural_speed_academy.i18n import tr

_STOP_WORDS = frozenset(
    # English
    "the a an and or but in on at to for of is it that this with from by as "
    "are was were be been has have had do does did not no nor so if then than "
    "can will would could should may might shall its you your we our they them "
    "he she his her my me us who what when where how all each every some any "
    "also just about more most very much many such only other into over after "
    "before between through during without again further once here there which "
    "these those being both same own too up out off down "
    # German
    "der die das ein eine einer eines einem einen und oder aber in auf an zu "
    "für von ist es dass dies mit aus als sind war waren sein hat haben hatte "
    "nicht kein noch wenn dann als kann wird würde soll darf mag ihr euer "
    "wir sie er ich mich mir uns ihm ihn ihr was wer wie wo alle jede jeder "
    "auch nur über nach vor zwischen durch ohne wieder mehr sehr viel viele "
    "andere andere anderen anderer anderes hier dort diese dieser dieses "
    "dem den des sich man "
    # French
    "le la les un une des et ou mais dans sur pour de est ce que qui avec par "
    "sont était été être ont avoir avait pas non plus si alors comme peut sera "
    "nous vous ils elles lui elle mon ton son notre votre leur mes tes ses nos "
    "vos leurs tout tous toute toutes autre autres même ici cette cet ces "
    "aux du au "
    # Spanish
    "el la los las un una unos unas del al por para con sin sobre entre desde "
    "hasta como más pero sino también muy cada todo toda todos todas otro otra "
    "otros otras este esta estos estas ese esa esos esas aquel aquella "
    "que quien cual donde cuando como hay ser estar tener hacer poder decir "
    "fue era sido está son han nos les "
    # Italian
    "il lo la gli le un una dei del della delle degli alla alle nel nella "
    "nelle nei con per tra fra che chi come dove quando più anche molto ogni "
    "tutto tutti tutta tutte altro altra altri altre questo questa questi queste "
    "quello quella quelli quelle suo sua suoi sue nostro nostra loro "
    "essere avere fare potere dire stato sono era hanno "
    # Portuguese
    "que de em um uma para com não mais por mas como dos das nos nas pelo pela "
    "seu sua seus suas este esta estes estas esse essa esses essas aquele "
    "aquela todo toda todos todas outro outra outros outras muito muita muitos "
    "ser estar ter fazer poder dizer foi era são tem".split()
)

# Suffix rules for lightweight multilingual stemming (no external deps).
# Ordered longest-first so the most specific rule matches first.
_SUFFIX_RULES: list[tuple[str, str]] = [
    # ── English ──
    ("ational", "ate"),
    ("tional", "tion"),
    ("encies", "ence"),
    ("ancies", "ance"),
    ("izers", "ize"),
    ("ising", "ise"),
    ("izing", "ize"),
    ("ating", "ate"),
    ("ities", "ity"),
    ("ously", "ous"),
    ("ively", "ive"),
    ("fully", "ful"),
    ("ments", "ment"),
    ("ness", ""),
    ("ment", ""),
    ("able", ""),
    ("ible", ""),
    ("tion", ""),
    ("sion", ""),
    ("ally", ""),
    ("ence", ""),
    ("ance", ""),
    ("ious", ""),
    ("eous", ""),
    ("ling", ""),
    ("ings", ""),
    ("ful", ""),
    ("ous", ""),
    ("ive", ""),
    ("ing", ""),
    ("ies", "y"),
    ("ied", "y"),
    ("ier", "y"),
    ("ers", ""),
    ("est", ""),
    ("ism", ""),
    ("ist", ""),
    ("ity", ""),
    ("ize", ""),
    ("ise", ""),
    ("ate", ""),
    ("ent", ""),
    ("ant", ""),
    ("ed", ""),
    ("er", ""),
    ("ly", ""),
    ("al", ""),
    ("en", ""),
    # ── German ──
    ("ungen", ""),    # Bewegungen → Beweg
    ("keit", ""),     # Geschwindigkeit → Geschwindig
    ("heit", ""),     # Freiheit → Frei
    ("lich", ""),     # natürlich → natür
    ("isch", ""),     # technisch → techn
    ("ung", ""),      # Übung → Üb
    ("ern", ""),      # verbessern → verbess
    ("eln", ""),      # handeln → hand
    ("ens", ""),      # Lesens → Les
    # ── French ──
    ("ement", ""),    # rapidement → rapid
    ("ation", ""),    # information → inform
    ("ments", ""),    # mouvements → mouv  (also English)
    ("eurs", ""),     # lecteurs → lect
    ("euse", ""),     # heureuse → heur
    ("eux", ""),      # heureux → heur
    ("eur", ""),      # lecteur → lect
    # ── Spanish ──
    ("ción", ""),     # información → inform
    ("iones", ""),    # informaciones → informac
    ("mente", ""),    # rápidamente → rápida
    ("ando", ""),     # leyendo → ley  (gerund)
    ("endo", ""),     # corriendo → corri
    ("ados", ""),     # entrenados → entren
    ("adas", ""),     # entrenadas → entren
    ("ado", ""),      # entrenado → entren
    ("ada", ""),      # entrenada → entren
    # ── Italian ──
    ("zione", ""),    # informazione → inform
    ("zioni", ""),    # informazioni → inform
    ("mente", ""),    # rapidamente → rapida  (also Spanish)
    ("ando", ""),     # leggendo → legg  (also Spanish)
    ("endo", ""),     # correndo → corr
    ("ato", ""),      # allenato → allen
    ("ata", ""),      # allenata → allen
    ("ati", ""),      # allenati → allen
    ("ate", ""),      # allenate → allen  (also English)
    # ── Portuguese ──
    ("ação", ""),     # informação → inform
    ("ções", ""),     # informações → informa
    ("mente", ""),    # rapidamente → rapida
    ("ando", ""),     # lendo → l  (gerund, also Spanish)
    ("endo", ""),     # correndo → corr
    ("ados", ""),     # treinados → trein
    ("adas", ""),     # treinadas → trein
    ("ado", ""),      # treinado → trein
    ("ada", ""),      # treinada → trein
    # ── Shared short suffixes (applied last) ──
    ("es", ""),
    ("s", ""),
]


def _stem(word: str) -> str:
    """Lightweight multilingual stemmer — reduce a word to an approximate root.

    Handles common inflections in EN/DE/FR/ES/IT/PT without external
    libraries.  Good enough for recall scoring and keyword grouping.
    """
    if len(word) <= 4:
        return word
    for suffix, replacement in _SUFFIX_RULES:
        if word.endswith(suffix):
            base = word[: -len(suffix)]
            candidate = base + replacement
            # The base (before suffix) must be at least 4 chars to avoid
            # false stems like "speed" -> "spe" (where "ed" isn't a suffix)
            if len(base) >= 4 and len(candidate) >= 3:
                return candidate
    return word


def extract_keywords(text: str, max_keywords: int = 8) -> list[str]:
    """Extract key content words from text by frequency.

    Uses stemming to group inflected forms, then picks the most common
    surface form for each stem group.

    Weighting:
    - Words in the first/last sentence of each paragraph get 2× weight
      (topic sentences carry the main ideas).
    - Words in the first 25% of the overall text get 1.5× weight
      (introductions establish the subject).
    - Minimum word length is 5 characters to filter trivial words.
    """
    words = _WORD_RE.findall(text.lower())
    if not words:
        return []

    quarter = max(len(words) // 4, 1)

    # Build a set of word positions that fall in paragraph boundary sentences
    _boundary_positions: set[int] = set()
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    global_pos = 0
    for para in paragraphs:
        para_lower = para.lower()
        # Split paragraph into sentences (rough heuristic)
        sentences = re.split(r'(?<=[.!?])\s+', para_lower)
        if not sentences:
            continue
        first_sent = sentences[0]
        last_sent = sentences[-1] if len(sentences) > 1 else ""
        # Find word positions in this paragraph
        para_words = _WORD_RE.findall(para_lower)
        first_sent_words = set(_WORD_RE.findall(first_sent))
        last_sent_words = set(_WORD_RE.findall(last_sent))
        seen_first: dict[str, int] = {}
        for j, pw in enumerate(para_words):
            pos = global_pos + j
            if pw in first_sent_words:
                if seen_first.get(pw, 0) < first_sent.count(pw):
                    _boundary_positions.add(pos)
                    seen_first[pw] = seen_first.get(pw, 0) + 1
            if pw in last_sent_words:
                _boundary_positions.add(pos)
        global_pos += len(para_words)

    # stem -> {surface_form -> weighted_count}
    stem_groups: dict[str, dict[str, float]] = {}

    for i, w in enumerate(words):
        if len(w) < 5 or w in _STOP_WORDS:
            continue
        weight = 1.0
        if i < quarter:
            weight = 1.5
        if i in _boundary_positions:
            weight *= 2.0
        s = _stem(w)
        if s not in stem_groups:
            stem_groups[s] = {}
        stem_groups[s][w] = stem_groups[s].get(w, 0) + weight

    # For each stem group, total weight and pick the most common surface form
    ranked: list[tuple[float, str]] = []
    for s, forms in stem_groups.items():
        total_weight = sum(forms.values())
        best_form = max(forms, key=lambda f: forms[f])
        ranked.append((total_weight, best_form))

    ranked.sort(key=lambda x: x[0], reverse=True)
    return [form for _, form in ranked[:max_keywords]]


def _get_stems(words: set[str]) -> dict[str, set[str]]:
    """Build a stem -> surface-forms mapping for a set of words."""
    stems: dict[str, set[str]] = {}
    for w in words:
        s = _stem(w)
        if s not in stems:
            stems[s] = set()
        stems[s].add(w)
    return stems


def score_recall(
    keywords: list[str],
    summary_text: str,
) -> tuple[float, int, list[tuple[str, str]]]:
    """Score a recall summary against extracted keywords.

    Uses stem-aware matching: if the user writes "running" and the keyword
    is "run", it counts as a match. Also detects substring containment
    for compound words (e.g., "speedreading" matches "speed").

    Returns:
        (score, total, matches) where matches is a list of
        (keyword, match_type) pairs. match_type is "exact", "stem",
        "partial", or "miss".
    """
    summary_words = set(_WORD_RE.findall(summary_text.lower()))
    summary_stems = _get_stems(summary_words)

    matches: list[tuple[str, str]] = []
    score = 0.0

    for kw in keywords:
        kw_stem = _stem(kw)

        # 1. Exact match
        if kw in summary_words:
            matches.append((kw, "exact"))
            score += 1.0
            continue

        # 2. Stem match (e.g., "running" matches keyword "run")
        if kw_stem in summary_stems:
            matches.append((kw, "stem"))
            score += 1.0
            continue

        # 3. Partial/substring match for compound words or longer keywords
        partial = False
        if len(kw) >= 5:
            for sw in summary_words:
                if len(sw) >= 5 and (kw in sw or sw in kw):
                    matches.append((kw, "partial"))
                    score += 0.5
                    partial = True
                    break
        if not partial:
            matches.append((kw, "miss"))

    return score, len(keywords), matches


def build_recall_screen(
    parent: QWidget,
    layout: QVBoxLayout,
    source_text: str,
    on_scored: Callable[[float, int, list[tuple[str, str]], list[str]], None],
    exercise_label: str = "COMPREHENSION CHECK",
) -> None:
    """Build the recall quiz UI into the given layout.

    Args:
        parent: Parent widget (the exercise screen).
        layout: Layout to add widgets to.
        source_text: The text the user just read.
        on_scored: Callback(score, total, matches, all_keywords) after scoring.
            matches is a list of (keyword, match_type) tuples.
        exercise_label: Title shown above the prompt.
    """
    c = COLORS
    keywords = extract_keywords(source_text)

    container = QWidget()
    container.setStyleSheet(f"background-color: {c['bg']};")
    cl = QVBoxLayout(container)
    cl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    cl.setSpacing(8)

    title = QLabel(exercise_label)
    title.setFont(make_qfont("header"))
    title.setStyleSheet(f"color: {c['accent']};")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    cl.addWidget(title)

    desc = QLabel(tr("recall.summarize_what_you_just_read_i"))
    desc.setFont(make_qfont("body"))
    desc.setStyleSheet(f"color: {c['fg']};")
    desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
    cl.addWidget(desc)

    quiz_input = QTextEdit()
    quiz_input.setFont(make_qfont("pacer_text"))
    quiz_input.setStyleSheet(input_css(widget="QTextEdit"))
    quiz_input.setFixedHeight(200)
    quiz_input.setFixedWidth(min(screen_metrics.reader_w, screen_metrics.text_input_w))
    cl.addWidget(quiz_input, alignment=Qt.AlignmentFlag.AlignCenter)

    def _score():
        summary = quiz_input.toPlainText()
        score, total, matches = score_recall(keywords, summary)
        on_scored(score, total, matches, keywords)

    check_btn = QPushButton(tr("flash.check"))
    check_btn.setFont(make_qfont("btn_bold"))
    check_btn.setStyleSheet(
        f"QPushButton {{ background-color: {c['accent']}; color: {c['btn_text']}; "
        f"border: 2px solid transparent; padding: 8px 30px; border-radius: 4px; }}"
    )
    check_btn.setCursor(Qt.CursorShape.PointingHandCursor)
    check_btn.clicked.connect(_score)
    cl.addWidget(check_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    skip_btn = QPushButton(tr("recall.skip"))
    skip_btn.setFont(make_qfont("btn_sm"))
    skip_btn.setStyleSheet(
        f"QPushButton {{ background-color: {c['card']}; color: {c['fg']}; "
        f"border: 2px solid transparent; padding: 6px 20px; border-radius: 4px; }}"
        f"QPushButton:hover {{ background-color: {c['bg']}; }}"
    )
    skip_btn.setCursor(Qt.CursorShape.PointingHandCursor)
    skip_btn.clicked.connect(
        lambda: on_scored(0, len(keywords), [(kw, "miss") for kw in keywords], keywords)
    )
    cl.addWidget(skip_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    layout.addWidget(container, 1)
    quiz_input.setFocus()


def build_recall_results(
    layout: QVBoxLayout,
    score: float,
    total: int,
    matches: list[tuple[str, str]],
    keywords: list[str],
) -> QVBoxLayout:
    """Build the keyword breakdown results into the given layout.

    Returns the layout for further additions (e.g., Continue button).
    """
    c = COLORS

    container = QWidget()
    container.setStyleSheet(f"background-color: {c['bg']};")
    cl = QVBoxLayout(container)
    cl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    cl.setSpacing(6)

    int_score = int(score) if score == int(score) else round(score, 1)
    score_lbl = QLabel(tr("recall.keywords_recalled", score=int_score, total=total))
    score_lbl.setFont(make_qfont("header"))
    color = c["success"] if score >= total * 0.6 else c["alert"]
    score_lbl.setStyleSheet(f"color: {color};")
    score_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    cl.addWidget(score_lbl)

    pct = round(score / total * 100) if total > 0 else 0
    pct_lbl = QLabel(tr("recall.comprehension_pct", pct=pct))
    pct_lbl.setFont(make_qfont("counter"))
    pct_lbl.setStyleSheet(f"color: {c['accent']};")
    pct_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    cl.addWidget(pct_lbl)

    cl.addSpacing(10)

    # Keyword breakdown with match type indicators
    _match_icons = {
        "exact": ("\u2714", "success"),
        "stem": ("\u2714", "success"),
        "partial": ("\u25d0", "accent"),
        "miss": ("\u2718", "muted"),
    }
    _match_labels = {
        "exact": "",
        "stem": " (stem match)",
        "partial": " (partial)",
        "miss": "",
    }

    for kw, match_type in matches:
        icon, color_key = _match_icons.get(match_type, ("\u2718", "muted"))
        suffix = _match_labels.get(match_type, "")
        color_kw = c[color_key]
        lbl = QLabel(f"  {icon}  {kw}{suffix}")
        lbl.setFont(make_qfont("body"))
        lbl.setStyleSheet(f"color: {color_kw};")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(lbl)

    layout.addWidget(container, 1)
    return cl
