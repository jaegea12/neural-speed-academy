"""
Exercise configurations and data for Neural Speed Academy.
"""
from __future__ import annotations

# Word pairs for ambiguous word recognition exercises
WORD_PAIRS = [
    ("TRAIL", "TRIAL"), ("QUIET", "QUITE"), ("FROM", "FORM"), ("BOARD", "BROAD"),
    ("ANGEL", "ANGLE"), ("DAIRY", "DIARY"), ("ADAPT", "ADOPT"), ("AFFECT", "EFFECT"),
    ("LOOSE", "LOSE"), ("PEACE", "PIECE"), ("PRINCIPAL", "PRINCIPLE"), ("STATIONARY", "STATIONERY"),
    ("COMPLEMENT", "COMPLIMENT"), ("ADVICE", "ADVISE"), ("DEVICE", "DEVISE"), ("MORAL", "MORALE"),
    ("PERSONAL", "PERSONNEL"), ("PROCEED", "PRECEDE"), ("THAN", "THEN"), ("WEATHER", "WHETHER"),
    ("ACCEPT", "EXCEPT"), ("ACCESS", "EXCESS"), ("ADDITION", "EDITION"), ("BARE", "BEAR"),
    ("BRAKE", "BREAK"), ("CEILING", "SEALING"), ("CELLAR", "SELLER"), ("CENT", "SCENT"),
    ("CEREAL", "SERIAL"), ("CITE", "SIGHT"), ("COARSE", "COURSE"), ("DESERT", "DESSERT"),
    ("ELICIT", "ILLICIT"), ("EMINENT", "IMMINENT"), ("FAIR", "FARE"), ("FORMALLY", "FORMERLY"),
    ("FORTH", "FOURTH"), ("GORILLA", "GUERRILLA"), ("HEAR", "HERE"), ("HOLE", "WHOLE"),
    ("INCIDENCE", "INCIDENTS"), ("INSTANCE", "INSTANTS"), ("ISLE", "AISLE"), ("LATER", "LATTER"),
    ("LEAD", "LED"), ("LESSEN", "LESSON"), ("LIGHTNING", "LIGHTENING"), ("MEAT", "MEET"),
    ("MINER", "MINOR"), ("PASSED", "PAST"), ("PATIENCE", "PATIENTS"), ("PLAIN", "PLANE"),
    ("PRESENCE", "PRESENTS"), ("RAIN", "REIGN"), ("RIGHT", "WRITE"), ("SCENE", "SEEN"),
    ("SIGHT", "SITE"), ("SOLE", "SOUL"), ("STAIR", "STARE"), ("STAKE", "STEAK"),
    ("SWEET", "SUITE"), ("TAIL", "TALE"), ("THEIR", "THERE"), ("TO", "TOO"),
    ("TRACK", "TRACT"), ("VAIN", "VEIN"), ("WAIST", "WASTE"), ("WAIT", "WEIGHT"),
]

# Exercise guide texts
EXERCISE_GUIDES = {
    "flash": (
        "FLASH PERCEPTION",
        "HOW TO USE:\n"
        "Begin with fixed digits (e.g., just '1 digit') to reduce anxiety. "
        "Once comfortable, move to 'Overlapping' sets (e.g., 2-4 digits) to stop "
        "your brain from predicting the length.\n\n"
        "THE SCIENCE:\n"
        "Tachistoscopic training (brief visual exposure) has been used since the "
        "1800s to study perception. Research shows that the visual system can "
        "process information in as little as 13 milliseconds (Potter et al., MIT, "
        "2014). With practice, the brain learns to encode more information per "
        "fixation by strengthening the ventral visual stream.\n\n"
        "BENEFITS:\n"
        "- Increases the number of characters recognized per eye fixation\n"
        "- Trains iconic memory (ultra-short-term visual buffer)\n"
        "- Reduces subvocalization by forcing faster-than-speech processing\n"
        "- Improves digit span, a core measure of working memory capacity"
    ),
    "eyespan": (
        "EYE-SPAN EXPANSION",
        "HOW TO USE:\n"
        "Horizontal: Trains width for reading lines.\n"
        "Vertical: Trains 'Block Reading' (seeing multiple lines at once).\n"
        "Mixed: Trains agility.\n"
        "Focus only on the fixation cross (+) in the center.\n\n"
        "THE SCIENCE:\n"
        "The fovea (central 2 degrees of vision) provides sharp detail, but the "
        "parafovea (extending to ~5 degrees) can identify words during reading. "
        "Skilled readers extract useful information from a wider perceptual span: "
        "about 14-15 characters to the right of fixation in English (Rayner, 1998). "
        "Training peripheral recognition expands this effective span.\n\n"
        "BENEFITS:\n"
        "- Widens the perceptual span, reducing the number of fixations per line\n"
        "- Trains parafoveal preview, allowing the brain to pre-process upcoming words\n"
        "- Vertical mode develops block reading, useful for scanning documents\n"
        "- Directly increases reading speed by covering more text per fixation"
    ),
    "schulte": (
        "SCHULTE GRID",
        "HOW TO USE:\n"
        "Find numbers 1 through 25 in order. Keep your gaze fixed on the center "
        "square and use peripheral vision to locate each number.\n"
        "Score: +5 for correct click, -2 for wrong click.\n\n"
        "THE SCIENCE:\n"
        "Schulte tables were developed by German psychiatrist Walter Schulte to "
        "measure and train visual attention. Studies in sports psychology show that "
        "athletes who train with Schulte grids develop faster visual search times "
        "and broader attentional fields (Appelbaum & Erickson, 2018). The exercise "
        "engages both the dorsal attention network (spatial awareness) and the "
        "ventral attention network (target detection).\n\n"
        "BENEFITS:\n"
        "- Expands peripheral awareness without moving the eyes\n"
        "- Improves visual search speed and selective attention\n"
        "- Strengthens the ability to suppress distractors\n"
        "- Used by pilots and athletes to sharpen situational awareness"
    ),
    "pacer": (
        "PACER FLOW",
        "HOW TO USE:\n"
        "Paste your reading material, set a target WPM, and follow the highlight. "
        "Do not regress (look back). Let the pacer pull your eyes forward.\n\n"
        "THE SCIENCE:\n"
        "Regression (re-reading) accounts for 10-15% of all eye movements during "
        "reading and is a major speed limiter (Rayner et al., 2012). A visual pacer "
        "acts as an external metronome that suppresses regression and gradually "
        "pushes reading rate above the comfort zone. This leverages the spacing "
        "effect: slightly exceeding your current speed forces deeper encoding.\n\n"
        "BENEFITS:\n"
        "- Eliminates regression, the single largest source of wasted reading time\n"
        "- Trains a steady, rhythmic eye movement pattern\n"
        "- Gradually increases comfortable reading speed through progressive overload\n"
        "- Improves focus and reduces mind-wandering during reading"
    ),
    "priming": (
        "EYE PRIMING",
        "HOW TO USE:\n"
        "Follow the dot with your eyes only. Keep your head still.\n"
        "SACCADE modes: the dot jumps between positions in structured patterns "
        "(horizontal, vertical, diagonal, expanding). These train fast, accurate "
        "eye jumps — the primary movement used in reading.\n"
        "PURSUIT modes: the dot moves continuously along a path (line, circle, "
        "figure-8). Track it smoothly without jumping ahead.\n\n"
        "THE SCIENCE:\n"
        "The eyes are controlled by six extraocular muscles per eye. Saccades "
        "and smooth pursuit engage different neural circuits: the frontal eye "
        "fields for voluntary saccades and the medial superior temporal area "
        "for smooth pursuit (Krauzlis, 2004). Training both systems improves "
        "oculomotor flexibility. Sports vision research shows that structured "
        "saccadic training improves reaction time and visual search speed "
        "(Appelbaum & Erickson, 2018).\n\n"
        "BENEFITS:\n"
        "- Warms up extraocular muscles to reduce eye strain during exercises\n"
        "- Saccade patterns train the exact eye movements used in reading\n"
        "- Smooth pursuit develops tracking accuracy and eye-hand coordination\n"
        "- Expanding saccades progressively increase oculomotor range\n"
        "- Reduces the risk of eye fatigue during extended training sessions"
    ),
    "rsvp": (
        "RSVP (RAPID SERIAL VISUAL PRESENTATION)",
        "HOW TO USE:\n"
        "Paste your reading material or use the sample text. Set your target "
        "WPM and press Start. Words appear one at a time at the center of the "
        "screen. Keep your eyes fixed on the center — no eye movement needed.\n\n"
        "THE SCIENCE:\n"
        "RSVP eliminates the two biggest speed limiters in reading: saccadic "
        "eye movements and regression. By presenting words at a fixed point, "
        "the eyes stay still while the brain processes each word. Research by "
        "Forster (1970) established RSVP as a standard paradigm in psycholinguistics. "
        "At speeds above ~300 WPM, the brain is forced to abandon subvocalization "
        "(internal speech) and process text visually, building a direct pathway "
        "from visual input to comprehension.\n\n"
        "BENEFITS:\n"
        "- Eliminates eye movement overhead, isolating pure word processing speed\n"
        "- Breaks the subvocalization habit by exceeding inner speech rate\n"
        "- Trains rapid lexical access — recognizing words faster\n"
        "- Builds comfort with higher reading speeds before applying them to "
        "normal text\n"
        "- Measurable: track your comfortable WPM over time"
    ),
    "chunking": (
        "CHUNKING (PHRASE READING)",
        "HOW TO USE:\n"
        "Paste your text, choose how many words per chunk (2-6), set the display "
        "speed, and press Start. Word groups flash at the center of the screen. "
        "Read each group as a single unit of meaning.\n\n"
        "THE SCIENCE:\n"
        "Miller's Law (1956) established that working memory holds ~7 chunks of "
        "information. By grouping words into meaningful phrases, you effectively "
        "multiply the text processed per cognitive 'slot.' Skilled readers "
        "naturally fixate on word groups rather than individual words — their "
        "perceptual span covers 2-4 words per fixation (Rayner, 1998). Chunking "
        "training accelerates this transition from word-by-word to phrase-level "
        "reading.\n\n"
        "BENEFITS:\n"
        "- Trains the brain to process word groups as single units\n"
        "- Directly reduces the number of fixations needed per line\n"
        "- Builds the core skill that separates fast readers from slow ones\n"
        "- Complements RSVP: RSVP trains speed, chunking trains breadth\n"
        "- Improves reading comprehension by preserving phrase-level meaning"
    ),
}

# Pacer configuration
PACER_CONFIG = {
    "min_wpm": 200,
    "max_wpm": 1000,
    "default_wpm": 300,
}

# Schulte grid configuration
SCHULTE_CONFIG = {
    "grid_size": 5,
    "correct_points": 5,
    "wrong_penalty": 2,
}

# Eye priming configuration
PRIMING_CONFIG = {
    "total_positions": 20,
    "delay_ms": 600,
    "positions": [
        (0.2, 0.3), (0.8, 0.3),
        (0.2, 0.5), (0.8, 0.5),
        (0.2, 0.7), (0.8, 0.7),
    ],
}

# Flash timing configuration (in milliseconds)
FLASH_TIMING = {
    "cross_duration": 800,
    "dots_duration": 400,
    "flash_duration": 50,
    "post_flash_delay": 500,
    "correction_display": 1500,
}

# RSVP configuration
RSVP_CONFIG = {
    "min_wpm": 200,
    "max_wpm": 1200,
    "default_wpm": 350,
}

# Chunking configuration
CHUNKING_CONFIG = {
    "min_chunk_size": 2,
    "max_chunk_size": 6,
    "default_chunk_size": 3,
    "min_wpm": 150,
    "max_wpm": 800,
    "default_wpm": 250,
}

# User data configuration
USER_DATA_CONFIG = {
    "file_name": "neural_profile.json",
    "max_history_entries": 50,
    "xp_per_correct": 10,
}
