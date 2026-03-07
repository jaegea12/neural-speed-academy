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
        "Follow the dot with your eyes only. Keep your head still. "
        "This is a warm-up exercise before intensive training.\n\n"
        "THE SCIENCE:\n"
        "The eyes are controlled by six extraocular muscles per eye. Like any "
        "muscles, they perform better when warmed up. Smooth pursuit and saccadic "
        "eye movements activate different neural circuits: the frontal eye fields "
        "for voluntary saccades and the medial superior temporal area for smooth "
        "pursuit (Krauzlis, 2004). Priming these circuits before training improves "
        "accuracy and reduces fatigue.\n\n"
        "BENEFITS:\n"
        "- Warms up extraocular muscles to reduce eye strain during exercises\n"
        "- Activates the oculomotor system for faster, more accurate saccades\n"
        "- Improves coordination between smooth pursuit and saccadic movements\n"
        "- Reduces the risk of eye fatigue during extended training sessions"
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

# User data configuration
USER_DATA_CONFIG = {
    "file_name": "neural_profile.json",
    "max_history_entries": 50,
    "xp_per_correct": 10,
}
