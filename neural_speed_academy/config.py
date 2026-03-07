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
        "Begin with fixed digits (e.g., just '1 digit') to reduce anxiety.\n\n"
        "Once comfortable, move to 'Overlapping' sets (e.g., 2-4 digits) to stop "
        "your brain from predicting the length."
    ),
    "eyespan": (
        "EYE-SPAN EXPANSION",
        "Horizontal: Trains width for reading lines.\n\n"
        "Vertical: Trains 'Block Reading' (seeing multiple lines at once).\n\n"
        "Mixed: Trains agility.\n\n"
        "Focus only on the Red '+'."
    ),
    "schulte": (
        "SCHULTE GRID",
        "Find 1-25. Do not move your eyes from the center square.\n\n"
        "Score: +5 for correct click, -2 for wrong click."
    ),
    "pacer": (
        "PACER FLOW",
        "Follow the highlight. Do not regress (look back)."
    ),
    "priming": (
        "EYE PRIMING",
        "Follow the dot with your eyes only. Keep your head still. "
        "This warms up the extraocular muscles."
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
