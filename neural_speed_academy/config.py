"""
Exercise configurations and data for Neural Speed Academy.
"""
from __future__ import annotations

from neural_speed_academy.i18n import tr

# Word pairs for ambiguous word recognition exercises
WORD_PAIRS = [
    # Letter-swap / anagram confusables
    ("TRAIL", "TRIAL"), ("QUIET", "QUITE"), ("FROM", "FORM"), ("BOARD", "BROAD"),
    ("ANGEL", "ANGLE"), ("DAIRY", "DIARY"), ("ADAPT", "ADOPT"), ("SACRED", "SCARED"),
    ("UNITED", "UNTIED"), ("CAUSAL", "CASUAL"), ("MARITAL", "MARTIAL"), ("CLAM", "CALM"),
    ("NUCLEAR", "UNCLEAR"), ("CONSERVATION", "CONVERSATION"),
    # Homophones and near-homophones
    ("AFFECT", "EFFECT"), ("LOOSE", "LOSE"), ("PEACE", "PIECE"), ("ADVICE", "ADVISE"),
    ("DEVICE", "DEVISE"), ("MORAL", "MORALE"), ("THAN", "THEN"), ("WEATHER", "WHETHER"),
    ("ACCEPT", "EXCEPT"), ("ACCESS", "EXCESS"), ("BARE", "BEAR"), ("BRAKE", "BREAK"),
    ("CEILING", "SEALING"), ("CELLAR", "SELLER"), ("CENT", "SCENT"), ("CEREAL", "SERIAL"),
    ("CITE", "SIGHT"), ("COARSE", "COURSE"), ("DESERT", "DESSERT"), ("FAIR", "FARE"),
    ("FORTH", "FOURTH"), ("HEAR", "HERE"), ("HOLE", "WHOLE"), ("ISLE", "AISLE"),
    ("LEAD", "LED"), ("LESSEN", "LESSON"), ("MEAT", "MEET"), ("MINER", "MINOR"),
    ("PASSED", "PAST"), ("PATIENCE", "PATIENTS"), ("PLAIN", "PLANE"), ("RAIN", "REIGN"),
    ("RIGHT", "WRITE"), ("SCENE", "SEEN"), ("SIGHT", "SITE"), ("SOLE", "SOUL"),
    ("STAIR", "STARE"), ("STAKE", "STEAK"), ("SWEET", "SUITE"), ("TAIL", "TALE"),
    ("THEIR", "THERE"), ("TO", "TOO"), ("VAIN", "VEIN"), ("WAIST", "WASTE"),
    ("WAIT", "WEIGHT"), ("ALTAR", "ALTER"), ("CANVAS", "CANVASS"), ("DUAL", "DUEL"),
    ("FLAIR", "FLARE"), ("FLOUR", "FLOWER"), ("MEDAL", "MEDDLE"), ("PEDAL", "PEDDLE"),
    ("POUR", "PORE"), ("PRAY", "PREY"), ("PROFIT", "PROPHET"), ("ROLE", "ROLL"),
    ("SEAM", "SEEM"), ("SOAR", "SORE"), ("WARY", "WEARY"), ("ALOUD", "ALLOWED"),
    ("BORN", "BORNE"), ("COUNCIL", "COUNSEL"), ("CURRANT", "CURRENT"), ("DRAFT", "DRAUGHT"),
    # Visually similar (same length, differ by 1-2 letters)
    ("PRINCIPAL", "PRINCIPLE"), ("STATIONARY", "STATIONERY"), ("COMPLEMENT", "COMPLIMENT"),
    ("PERSONAL", "PERSONNEL"), ("PROCEED", "PRECEDE"), ("ADDITION", "EDITION"),
    ("ELICIT", "ILLICIT"), ("EMINENT", "IMMINENT"), ("FORMALLY", "FORMERLY"),
    ("GORILLA", "GUERRILLA"), ("INCIDENCE", "INCIDENTS"), ("INSTANCE", "INSTANTS"),
    ("LATER", "LATTER"), ("LIGHTNING", "LIGHTENING"), ("PRESENCE", "PRESENTS"),
    ("TRACK", "TRACT"), ("PRESCRIBE", "PROSCRIBE"), ("EMIGRATE", "IMMIGRATE"),
    ("ALLUSION", "ILLUSION"), ("ASSENT", "ASCENT"), ("DESCENT", "DISSENT"),
    ("DISCRETE", "DISCREET"), ("ENSURE", "INSURE"),
]

# Exercise guide texts — content lives in locales/*.json
_GUIDE_KEYS = [
    "flash",
    "eyespan",
    "schulte",
    "pacer",
    "priming",
    "rsvp",
    "chunking",
    "sequence_memory",
    "rapid_decision",
    "peripheral_flash",
    "mot",
    "split_attention",
    "reaction_time",
    "slide_processing",
    "spaced_repetition",
]


def get_exercise_guide(topic: str) -> tuple[str, str]:
    """Return (title, body) for the given guide topic, translated."""
    return (
        tr(f"guide.{topic}.title"),
        tr(f"guide.{topic}.body"),
    )


# Backward-compatible dict-like access
class _GuideProxy(dict):
    """Lazy dict that returns tr()-based guide content on access."""
    def get(self, key, default=None):
        if key in _GUIDE_KEYS:
            return get_exercise_guide(key)
        return default
    def __getitem__(self, key):
        if key in _GUIDE_KEYS:
            return get_exercise_guide(key)
        raise KeyError(key)
    def __contains__(self, key):
        return key in _GUIDE_KEYS


EXERCISE_GUIDES = _GuideProxy()

# Spaced Repetition configuration
SR_CONFIG = {
    "max_new_per_session": 10,
    "max_review_per_session": 30,
    "default_ease": 2.5,
    "min_ease": 1.3,
}

# Pre-built decks: list of (front, back) tuples
SR_BUILTIN_DECKS = {
    "SAT Vocabulary": [
        ("Aberration", "A departure from what is normal or expected"),
        ("Benevolent", "Well-meaning and kindly"),
        ("Cacophony", "A harsh, discordant mixture of sounds"),
        ("Debilitate", "To make weak or feeble"),
        ("Ephemeral", "Lasting for a very short time"),
        ("Fastidious", "Very attentive to detail; meticulous"),
        ("Gregarious", "Fond of company; sociable"),
        ("Hackneyed", "Lacking originality; overused"),
        ("Iconoclast", "A person who attacks cherished beliefs"),
        ("Juxtapose", "To place side by side for comparison"),
        ("Laconic", "Using very few words; concise"),
        ("Magnanimous", "Generous or forgiving, especially toward a rival"),
        ("Nefarious", "Wicked or criminal"),
        ("Obfuscate", "To make unclear or confusing"),
        ("Pernicious", "Having a harmful effect, especially gradually"),
        ("Quintessential", "Representing the most perfect example"),
        ("Recalcitrant", "Stubbornly uncooperative"),
        ("Sycophant", "A person who flatters to gain advantage"),
        ("Tenacious", "Holding firmly; persistent"),
        ("Ubiquitous", "Present, appearing, or found everywhere"),
    ],
    "World Capitals": [
        ("Japan", "Tokyo"),
        ("France", "Paris"),
        ("Brazil", "Bras\u00edlia"),
        ("Australia", "Canberra"),
        ("Egypt", "Cairo"),
        ("Canada", "Ottawa"),
        ("South Korea", "Seoul"),
        ("Argentina", "Buenos Aires"),
        ("Thailand", "Bangkok"),
        ("Turkey", "Ankara"),
        ("Norway", "Oslo"),
        ("Peru", "Lima"),
        ("New Zealand", "Wellington"),
        ("Kenya", "Nairobi"),
        ("Switzerland", "Bern"),
        ("Poland", "Warsaw"),
        ("Vietnam", "Hanoi"),
        ("Colombia", "Bogot\u00e1"),
        ("Morocco", "Rabat"),
        ("Czech Republic", "Prague"),
    ],
    "Speed Reading Terms": [
        ("Subvocalization", "The habit of silently pronouncing words while reading"),
        ("Saccade", "A rapid eye movement between fixation points"),
        ("Fixation", "A pause where the eye rests to process text"),
        ("Regression", "Moving the eyes backward to re-read text"),
        ("Peripheral vision", "Vision outside the center of gaze"),
        ("Chunking", "Grouping words into meaningful units"),
        ("WPM", "Words per minute — standard reading speed measure"),
        ("RSVP", "Rapid Serial Visual Presentation — one word at a time"),
        ("Metaguiding", "Using a finger or pointer to guide eye movement"),
        ("Foveal vision", "Sharp central vision used for reading"),
        ("Magnocellular pathway", "Fast visual pathway for motion and periphery"),
        ("Useful field of view", "Area from which info can be extracted in one fixation"),
        ("Pacer", "A visual guide that sets reading tempo"),
        ("Comprehension", "Understanding and retaining what is read"),
        ("Skimming", "Reading quickly to get the main ideas"),
    ],
    "Neuroscience Basics": [
        ("Neuron", "A nerve cell that transmits electrical and chemical signals"),
        ("Synapse", "The junction between two neurons where signals are transmitted"),
        ("Axon", "Long projection of a neuron that conducts electrical impulses away from the cell body"),
        ("Dendrite", "Branched extension of a neuron that receives signals from other neurons"),
        ("Myelin sheath", "Insulating layer around axons that speeds up signal transmission"),
        ("Neurotransmitter", "Chemical messenger released at synapses (e.g. dopamine, serotonin)"),
        ("Hippocampus", "Brain region essential for forming new long-term memories"),
        ("Amygdala", "Brain structure involved in processing emotions, especially fear"),
        ("Prefrontal cortex", "Front brain region responsible for planning, decision-making, and impulse control"),
        ("Cerebellum", "Brain region that coordinates movement, balance, and motor learning"),
        ("Neuroplasticity", "The brain's ability to reorganize and form new neural connections"),
        ("Long-term potentiation", "Strengthening of synapses based on repeated stimulation — basis of learning"),
        ("Dopamine", "Neurotransmitter involved in reward, motivation, and motor control"),
        ("Serotonin", "Neurotransmitter that regulates mood, sleep, and appetite"),
        ("GABA", "Main inhibitory neurotransmitter — reduces neuronal excitability"),
        ("Broca's area", "Brain region in the left frontal lobe responsible for speech production"),
        ("Wernicke's area", "Brain region in the left temporal lobe responsible for language comprehension"),
        ("Corpus callosum", "Bundle of nerve fibers connecting the left and right brain hemispheres"),
        ("Thalamus", "Brain relay station that routes sensory information to the cortex"),
        ("Basal ganglia", "Group of nuclei involved in motor control, learning, and habit formation"),
    ],
    "Historical Dates": [
        ("Fall of the Roman Empire", "476 AD"),
        ("Signing of the Magna Carta", "1215"),
        ("Columbus reaches the Americas", "1492"),
        ("Start of the French Revolution", "1789"),
        ("Declaration of US Independence", "1776"),
        ("Battle of Waterloo", "1815"),
        ("Start of World War I", "1914"),
        ("End of World War II", "1945"),
        ("Moon landing (Apollo 11)", "July 20, 1969"),
        ("Fall of the Berlin Wall", "November 9, 1989"),
        ("Invention of the printing press", "c. 1440 (Gutenberg)"),
        ("Start of the Industrial Revolution", "c. 1760"),
        ("Russian Revolution", "1917"),
        ("Discovery of penicillin", "1928 (Alexander Fleming)"),
        ("Founding of the United Nations", "1945"),
        ("First human in space", "April 12, 1961 (Yuri Gagarin)"),
        ("Invention of the World Wide Web", "1989 (Tim Berners-Lee)"),
        ("End of apartheid in South Africa", "1994"),
        ("Treaty of Versailles", "1919"),
        ("Assassination of Julius Caesar", "44 BC"),
    ],
    "Science & Nature": [
        ("Speed of light", "299,792,458 m/s (approx. 300,000 km/s)"),
        ("Absolute zero", "−273.15 °C (0 Kelvin)"),
        ("Chemical symbol for gold", "Au (from Latin 'aurum')"),
        ("Largest planet in the solar system", "Jupiter"),
        ("Smallest bone in the human body", "Stapes (in the middle ear)"),
        ("pH of pure water", "7 (neutral)"),
        ("Number of chromosomes in a human cell", "46 (23 pairs)"),
        ("Hardest natural substance", "Diamond (10 on Mohs scale)"),
        ("Distance from Earth to the Sun", "~149.6 million km (1 AU)"),
        ("Boiling point of water at sea level", "100 °C (212 °F)"),
        ("Most abundant gas in Earth's atmosphere", "Nitrogen (78%)"),
        ("Speed of sound in air", "~343 m/s at 20 °C"),
        ("Largest organ of the human body", "Skin"),
        ("Chemical formula for table salt", "NaCl (sodium chloride)"),
        ("Number of bones in the adult human body", "206"),
        ("Closest star to Earth (after the Sun)", "Proxima Centauri (4.24 light-years)"),
        ("Avogadro's number", "6.022 × 10²³"),
        ("Planck's constant", "6.626 × 10⁻³⁴ J·s"),
        ("Half-life of Carbon-14", "5,730 years"),
        ("Density of water at 4 °C", "1,000 kg/m³"),
    ],
    "Programming Concepts": [
        ("Big O notation", "Describes the upper bound of an algorithm's time or space complexity"),
        ("Recursion", "A function that calls itself to solve smaller instances of the same problem"),
        ("Stack vs. Queue", "Stack: LIFO (last in, first out) — Queue: FIFO (first in, first out)"),
        ("Hash table", "Data structure that maps keys to values using a hash function — O(1) average lookup"),
        ("Binary search", "Search algorithm that halves the search space each step — O(log n)"),
        ("Polymorphism", "Objects of different types responding to the same interface/method"),
        ("Deadlock", "Two or more processes waiting for each other to release resources — none can proceed"),
        ("REST", "Representational State Transfer — architectural style for stateless web APIs"),
        ("SQL JOIN", "Combines rows from two or more tables based on a related column"),
        ("Git rebase vs. merge", "Rebase: replays commits on new base — Merge: creates a merge commit"),
        ("TCP vs. UDP", "TCP: reliable, ordered delivery — UDP: fast, no guarantee of delivery"),
        ("Mutex", "Mutual exclusion lock — ensures only one thread accesses a resource at a time"),
        ("Garbage collection", "Automatic memory management that reclaims unused objects"),
        ("Design pattern: Singleton", "Ensures a class has only one instance with a global access point"),
        ("Design pattern: Observer", "Object notifies dependents automatically when its state changes"),
        ("ACID properties", "Atomicity, Consistency, Isolation, Durability — guarantees for database transactions"),
        ("CAP theorem", "A distributed system can guarantee at most 2 of: Consistency, Availability, Partition tolerance"),
        ("Idempotent operation", "An operation that produces the same result regardless of how many times it's applied"),
        ("Memoization", "Caching the results of expensive function calls to avoid redundant computation"),
        ("Dependency injection", "Providing dependencies to a class from outside rather than creating them internally"),
    ],
    "Cognitive Biases": [
        ("Confirmation bias", "Tendency to search for information that confirms existing beliefs"),
        ("Anchoring bias", "Over-relying on the first piece of information encountered"),
        ("Dunning-Kruger effect", "Low-ability individuals overestimate their competence; experts underestimate theirs"),
        ("Availability heuristic", "Judging probability by how easily examples come to mind"),
        ("Sunk cost fallacy", "Continuing an endeavor because of previously invested resources"),
        ("Bandwagon effect", "Adopting beliefs or behaviors because many others do"),
        ("Halo effect", "Letting one positive trait influence overall judgment of a person"),
        ("Survivorship bias", "Focusing on successes while overlooking failures that are less visible"),
        ("Framing effect", "Drawing different conclusions from the same data depending on how it's presented"),
        ("Status quo bias", "Preference for the current state of affairs over change"),
        ("Recency bias", "Giving more weight to recent events than earlier ones"),
        ("Negativity bias", "Negative experiences have a greater impact than positive ones of equal intensity"),
        ("Hindsight bias", "Believing, after an event, that one would have predicted it ('I knew it all along')"),
        ("Fundamental attribution error", "Attributing others' behavior to character while attributing own behavior to circumstances"),
        ("Peak-end rule", "Judging an experience based on its most intense point and its end, not the average"),
    ],
    "Latin Phrases": [
        ("Carpe diem", "Seize the day"),
        ("Veni, vidi, vici", "I came, I saw, I conquered"),
        ("Cogito, ergo sum", "I think, therefore I am"),
        ("E pluribus unum", "Out of many, one"),
        ("Ad hominem", "Attacking the person rather than the argument"),
        ("Habeas corpus", "You shall have the body — right to appear before a court"),
        ("Tabula rasa", "Blank slate — the mind before experience"),
        ("Memento mori", "Remember that you will die"),
        ("Quid pro quo", "Something for something — an exchange"),
        ("Status quo", "The existing state of affairs"),
        ("Bona fide", "In good faith; genuine"),
        ("Per se", "By itself; intrinsically"),
        ("De facto", "In fact; in practice (whether by right or not)"),
        ("Alma mater", "Nourishing mother — one's former school or university"),
        ("Vice versa", "The other way around"),
    ],
    "Mental Models": [
        ("First principles thinking", "Breaking problems down to fundamental truths and reasoning up from there"),
        ("Inversion", "Approaching a problem backward — think about what you want to avoid"),
        ("Circle of competence", "Knowing the boundaries of what you truly understand"),
        ("Second-order thinking", "Considering the consequences of consequences, not just immediate effects"),
        ("Occam's razor", "The simplest explanation is usually the correct one"),
        ("Hanlon's razor", "Never attribute to malice what can be explained by incompetence"),
        ("Map is not the territory", "Models and abstractions are simplifications, not reality itself"),
        ("Pareto principle (80/20)", "Roughly 80% of effects come from 20% of causes"),
        ("Margin of safety", "Building in a buffer for error or uncertainty"),
        ("Opportunity cost", "The value of the next best alternative you give up when making a choice"),
        ("Compounding", "Small consistent gains accumulate exponentially over time"),
        ("Feedback loops", "Outputs of a system that circle back as inputs, amplifying or dampening effects"),
        ("Regression to the mean", "Extreme outcomes tend to be followed by more average ones"),
        ("Antifragility", "Systems that gain from disorder and stress (Nassim Taleb)"),
        ("Leverage", "Using a small input to achieve a disproportionately large output"),
    ],
}

# MOT configuration
MOT_CONFIG = {
    "default_targets": 3,
    "min_targets": 2,
    "max_targets": 6,
    "default_distractors": 5,
    "min_distractors": 2,
    "max_distractors": 10,
    "default_speed": 3,
    "min_speed": 1,
    "max_speed": 7,
    "default_duration": 6,
    "min_duration": 3,
    "max_duration": 12,
    "default_rounds": 5,
    "highlight_ms": 2000,
    "dot_radius": 20,
    "arena_padding": 30,
}

# Peripheral flash configuration
PERIPHERAL_FLASH_CONFIG = {
    "default_flash_ms": 100,
    "min_flash_ms": 50,
    "max_flash_ms": 100,
    "default_eccentricity": 50,
    "min_eccentricity": 20,
    "max_eccentricity": 90,
    "default_rounds": 15,
    "stimulus_types": ["letters", "numbers", "shapes"],
    "shapes": ["\u25b2", "\u25cf", "\u25a0", "\u25c6", "\u2605"],
    "shape_names": ["triangle", "circle", "square", "diamond", "star"],
}

# Rapid Decision Grid configuration
RAPID_DECISION_CONFIG = {
    "correct_points": 5,
    "wrong_penalty": 2,
    "default_grid_size": 5,
    "time_limits": [0, 60, 45, 30],
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

# Split Attention configuration
SPLIT_ATTENTION_CONFIG = {
    "default_center_ms": 120,
    "min_center_ms": 40,
    "max_center_ms": 300,
    "default_peripheral_ms": 100,
    "min_peripheral_ms": 40,
    "max_peripheral_ms": 250,
    "default_rounds": 15,
    "min_rounds": 5,
    "max_rounds": 30,
    "modes": ["sequential", "simultaneous", "rapid"],
    "shapes": ["\u25b2", "\u25cf", "\u25a0", "\u25c6", "\u2605"],
    "shape_names": ["triangle", "circle", "square", "diamond", "star"],
    "shape_colors": ["#e74c3c", "#3498db", "#2ecc71", "#f39c12"],
    "peripheral_directions": [
        (0.0, -1.0),   # top
        (0.0, 1.0),    # bottom
        (-1.0, 0.0),   # left
        (1.0, 0.0),    # right
        (-0.7, -0.7),  # top-left
        (0.7, -0.7),   # top-right
        (-0.7, 0.7),   # bottom-left
        (0.7, 0.7),    # bottom-right
    ],
    "eccentricity": 65,
}

# Reaction Time configuration
REACTION_TIME_CONFIG = {
    "default_rounds": 15,
    "min_rounds": 5,
    "max_rounds": 30,
    "min_delay_ms": 1000,
    "max_delay_ms": 4000,
    "timeout_ms": 1000,         # max wait for response in go/no-go
    "modes": ["simple", "choice", "go_no_go"],
    "go_ratio": 0.7,            # default fraction of go trials
    "choice_colors": [
        ("#2ecc71", "Green"),
        ("#e74c3c", "Red"),
        ("#3498db", "Blue"),
        ("#f1c40f", "Yellow"),
    ],
    "choice_shapes": ["\u25cf", "\u25a0", "\u25b2", "\u25c6"],
    "choice_shape_names": ["circle", "square", "triangle", "diamond"],
}

# Slide Processing configuration
SLIDE_PROCESSING_CONFIG = {
    "default_display_s": 10,
    "min_display_s": 3,
    "max_display_s": 20,
    "default_slides": 5,
    "min_slides": 3,
    "max_slides": 10,
    "questions_per_slide": 3,
    "categories": [
        "science", "business", "geography",
        "motivation", "neuroplasticity", "humor", "history", "nutrition",
    ],
}

# Built-in slide library: (title, [bullet_points], [(question, [choices], correct_idx)])
SLIDE_LIBRARY = {
    "science": [
        (
            "The Human Brain",
            [
                "Weight: 1.4 kg (about 2% of body weight)",
                "Contains approximately 86 billion neurons",
                "Uses 20% of the body's total energy",
                "Generates about 23 watts of electrical power",
                "Processing speed: up to 120 m/s in myelinated axons",
                "Storage capacity estimated at 2.5 petabytes",
            ],
            [
                ("How many neurons does the brain contain?",
                 ["12 billion", "86 billion", "100 billion", "45 billion"], 1),
                ("What percentage of body energy does the brain use?",
                 ["10%", "15%", "20%", "30%"], 2),
                ("What is the brain's estimated storage capacity?",
                 ["1.5 petabytes", "2.5 petabytes", "5 petabytes", "500 terabytes"], 1),
            ],
        ),
        (
            "Mars Exploration",
            [
                "Distance from Earth: 54.6 to 401 million km",
                "Surface temperature: -87°C to -5°C average",
                "Olympus Mons: tallest volcano at 21.9 km",
                "Day length (sol): 24 hours 37 minutes",
                "Atmosphere: 95.3% carbon dioxide",
                "Gravity: 3.72 m/s² (38% of Earth's)",
            ],
            [
                ("What is the height of Olympus Mons?",
                 ["15.2 km", "18.6 km", "21.9 km", "25.1 km"], 2),
                ("What percentage of Mars' atmosphere is CO₂?",
                 ["78.1%", "89.7%", "95.3%", "99.2%"], 2),
                ("What is Mars' gravity compared to Earth?",
                 ["28%", "38%", "48%", "58%"], 1),
            ],
        ),
        (
            "Ocean Facts",
            [
                "Oceans cover 71% of Earth's surface",
                "Average depth: 3,688 meters",
                "Deepest point: Mariana Trench at 10,994 meters",
                "Contains 97% of Earth's water",
                "Pacific Ocean: largest at 165.25 million km²",
                "Ocean temperature range: -2°C to 36°C",
            ],
            [
                ("What is the average ocean depth?",
                 ["2,450 m", "3,688 m", "4,200 m", "5,100 m"], 1),
                ("What percentage of Earth's water is in the oceans?",
                 ["87%", "92%", "97%", "99%"], 2),
                ("How deep is the Mariana Trench?",
                 ["8,848 m", "9,500 m", "10,994 m", "12,100 m"], 2),
            ],
        ),
        (
            "Speed of Light",
            [
                "Speed in vacuum: 299,792,458 m/s",
                "Light travels 9.461 trillion km per year",
                "Sunlight reaches Earth in 8 minutes 20 seconds",
                "Light from the Moon: 1.3 seconds to Earth",
                "Nearest star (Proxima Centauri): 4.24 light-years",
                "Light slows to 225,000 km/s in water",
            ],
            [
                ("How long does sunlight take to reach Earth?",
                 ["4 min 10 sec", "6 min 45 sec", "8 min 20 sec", "12 min 5 sec"], 2),
                ("How far is Proxima Centauri in light-years?",
                 ["2.18", "4.24", "6.71", "8.60"], 1),
                ("What is the speed of light in water?",
                 ["150,000 km/s", "225,000 km/s", "275,000 km/s", "299,792 km/s"], 1),
            ],
        ),
        (
            "DNA & Genetics",
            [
                "Human genome: 3.2 billion base pairs",
                "Humans share 98.7% DNA with chimpanzees",
                "Each cell contains about 2 meters of DNA",
                "Only 1.5% of DNA codes for proteins",
                "23 pairs of chromosomes in human cells",
                "DNA replication speed: 1,000 nucleotides/second",
            ],
            [
                ("How many base pairs in the human genome?",
                 ["1.8 billion", "3.2 billion", "4.6 billion", "6.4 billion"], 1),
                ("What percentage of DNA codes for proteins?",
                 ["1.5%", "5%", "10%", "25%"], 0),
                ("How much DNA does each cell contain?",
                 ["0.5 meters", "2 meters", "5 meters", "10 meters"], 1),
            ],
        ),
    ],
    "business": [
        (
            "Global Coffee Market 2024",
            [
                "Market value: $495.2 billion",
                "Annual consumption: 10.5 billion kg worldwide",
                "Top producer: Brazil (37.4% of global output)",
                "Average price per kg: $14.80 (arabica)",
                "Specialty coffee segment growing at 12.3% CAGR",
                "Finland leads per-capita consumption: 12 kg/year",
            ],
            [
                ("What is the global coffee market value?",
                 ["$312.8 billion", "$495.2 billion", "$620.5 billion", "$780.1 billion"], 1),
                ("What percentage of global coffee does Brazil produce?",
                 ["22.1%", "29.8%", "37.4%", "45.6%"], 2),
                ("Which country leads per-capita coffee consumption?",
                 ["Italy", "Colombia", "Finland", "USA"], 2),
            ],
        ),
        (
            "Electric Vehicle Sales",
            [
                "Global EV sales 2024: 17.1 million units",
                "Market share: 22% of all new car sales",
                "China leads with 59% of global EV sales",
                "Average EV battery cost: $139/kWh",
                "Tesla market share: 18.4% of global EVs",
                "Average EV range: 348 km per charge",
            ],
            [
                ("How many EVs were sold globally in 2024?",
                 ["9.8 million", "13.5 million", "17.1 million", "21.4 million"], 2),
                ("What is China's share of global EV sales?",
                 ["35%", "47%", "59%", "72%"], 2),
                ("What is the average EV battery cost per kWh?",
                 ["$89", "$139", "$189", "$239"], 1),
            ],
        ),
        (
            "Remote Work Statistics",
            [
                "32.6 million Americans will work remotely by 2025",
                "Productivity increase: 13% for remote workers",
                "Average commute time saved: 72 minutes/day",
                "Companies save $11,000 per remote worker annually",
                "67% of remote workers report better work-life balance",
                "Video conferencing market: $13.8 billion",
            ],
            [
                ("How much commute time do remote workers save daily?",
                 ["45 minutes", "72 minutes", "90 minutes", "120 minutes"], 1),
                ("How much do companies save per remote worker?",
                 ["$5,000", "$8,500", "$11,000", "$15,000"], 2),
                ("What is the productivity increase for remote workers?",
                 ["8%", "13%", "18%", "25%"], 1),
            ],
        ),
        (
            "Smartphone Market Q4 2024",
            [
                "Global shipments: 328.2 million units",
                "Samsung: 19.4% market share (#1)",
                "Apple: 18.2% market share (#2)",
                "Average selling price: $322",
                "5G phones: 78% of all shipments",
                "Foldable phones grew 49% year-over-year",
            ],
            [
                ("How many smartphones shipped in Q4 2024?",
                 ["245.6 million", "328.2 million", "412.7 million", "501.3 million"], 1),
                ("What was Samsung's market share?",
                 ["15.8%", "19.4%", "23.1%", "27.6%"], 1),
                ("What percentage of shipments were 5G phones?",
                 ["58%", "68%", "78%", "88%"], 2),
            ],
        ),
        (
            "Global Tourism 2024",
            [
                "International arrivals: 1.4 billion",
                "Tourism revenue: $1.9 trillion",
                "Most visited country: France (100 million visitors)",
                "Average spending per tourist: $1,350",
                "Tourism employs 330 million people worldwide",
                "Asia-Pacific growth rate: 18% year-over-year",
            ],
            [
                ("How many international tourist arrivals in 2024?",
                 ["0.8 billion", "1.1 billion", "1.4 billion", "1.8 billion"], 2),
                ("Which country had the most visitors?",
                 ["Spain", "USA", "France", "Italy"], 2),
                ("How many people does tourism employ globally?",
                 ["180 million", "250 million", "330 million", "420 million"], 2),
            ],
        ),
    ],
    "geography": [
        (
            "Japan",
            [
                "Population: 123.3 million (2024)",
                "Capital: Tokyo (population 13.96 million)",
                "Area: 377,975 km²",
                "Highest point: Mount Fuji at 3,776 meters",
                "GDP per capita: $33,950",
                "Life expectancy: 84.8 years (highest globally)",
            ],
            [
                ("What is Japan's population?",
                 ["98.5 million", "123.3 million", "145.7 million", "168.2 million"], 1),
                ("How tall is Mount Fuji?",
                 ["2,954 m", "3,776 m", "4,421 m", "5,108 m"], 1),
                ("What is Japan's life expectancy?",
                 ["78.2 years", "81.5 years", "84.8 years", "87.3 years"], 2),
            ],
        ),
        (
            "Brazil",
            [
                "Population: 216.4 million (2024)",
                "Capital: Brasília (not São Paulo or Rio)",
                "Area: 8,515,767 km² (5th largest country)",
                "Amazon Rainforest covers 5.5 million km²",
                "Official language: Portuguese",
                "Coastline: 7,491 km long",
            ],
            [
                ("What is Brazil's capital?",
                 ["São Paulo", "Rio de Janeiro", "Brasília", "Salvador"], 2),
                ("How large is the Amazon Rainforest?",
                 ["3.2 million km²", "5.5 million km²", "7.8 million km²", "9.1 million km²"], 1),
                ("How long is Brazil's coastline?",
                 ["4,230 km", "5,860 km", "7,491 km", "9,120 km"], 2),
            ],
        ),
        (
            "Australia",
            [
                "Population: 26.6 million (2024)",
                "Capital: Canberra (not Sydney)",
                "Area: 7,692,024 km² (6th largest country)",
                "Great Barrier Reef: 2,300 km long",
                "Highest point: Mount Kosciuszko at 2,228 m",
                "87% of population lives in urban areas",
            ],
            [
                ("What is Australia's population?",
                 ["18.4 million", "26.6 million", "34.2 million", "42.8 million"], 1),
                ("How long is the Great Barrier Reef?",
                 ["1,200 km", "1,800 km", "2,300 km", "2,900 km"], 2),
                ("What percentage of Australians live in urban areas?",
                 ["72%", "79%", "87%", "94%"], 2),
            ],
        ),
        (
            "Switzerland",
            [
                "Population: 8.9 million (2024)",
                "Capital: Bern (not Zurich or Geneva)",
                "4 official languages: German, French, Italian, Romansh",
                "Area: 41,285 km²",
                "Highest point: Dufourspitze at 4,634 m",
                "GDP per capita: $99,994 (2nd highest globally)",
            ],
            [
                ("What is Switzerland's capital?",
                 ["Zurich", "Geneva", "Bern", "Basel"], 2),
                ("How many official languages does Switzerland have?",
                 ["2", "3", "4", "5"], 2),
                ("What is Switzerland's GDP per capita?",
                 ["$67,450", "$82,310", "$99,994", "$115,200"], 2),
            ],
        ),
        (
            "Egypt",
            [
                "Population: 109.3 million (2024)",
                "Capital: Cairo (population 21.9 million)",
                "Nile River length: 6,650 km (longest in Africa)",
                "Great Pyramid height: 146.6 meters (originally)",
                "Area: 1,002,450 km² (97% desert)",
                "Suez Canal: 193.3 km long, opened 1869",
            ],
            [
                ("What is Cairo's population?",
                 ["14.2 million", "17.5 million", "21.9 million", "25.3 million"], 2),
                ("How long is the Nile River?",
                 ["4,130 km", "5,390 km", "6,650 km", "7,920 km"], 2),
                ("How long is the Suez Canal?",
                 ["120.5 km", "156.8 km", "193.3 km", "231.7 km"], 2),
            ],
        ),
    ],
    "motivation": [
        (
            "The 10,000 Hour Rule",
            [
                "Popularized by Malcolm Gladwell in Outliers (2008)",
                "Based on research by K. Anders Ericsson",
                "Elite violinists averaged 10,000 hours of practice by age 20",
                "Deliberate practice matters more than total hours",
                "Top performers practice 4 hours/day with full focus",
                "Feedback loops accelerate skill acquisition by 26%",
            ],
            [
                ("Who popularized the 10,000 hour rule?",
                 ["Daniel Kahneman", "Malcolm Gladwell", "Cal Newport", "James Clear"], 1),
                ("How many hours/day do top performers practice?",
                 ["2 hours", "4 hours", "6 hours", "8 hours"], 1),
                ("By how much do feedback loops accelerate learning?",
                 ["12%", "18%", "26%", "35%"], 2),
            ],
        ),
        (
            "Growth Mindset Research",
            [
                "Coined by Carol Dweck at Stanford University",
                "Students praised for effort improved 30% more",
                "Fixed mindset: intelligence is static",
                "Growth mindset: abilities develop through dedication",
                "73% of top CEOs identify as growth-mindset thinkers",
                "Mindset interventions raised GPAs by 0.3 points average",
            ],
            [
                ("Who coined the term 'growth mindset'?",
                 ["Angela Duckworth", "Carol Dweck", "Martin Seligman", "Amy Cuddy"], 1),
                ("How much more did effort-praised students improve?",
                 ["10%", "20%", "30%", "40%"], 2),
                ("What percentage of top CEOs identify as growth-mindset?",
                 ["53%", "63%", "73%", "83%"], 2),
            ],
        ),
        (
            "The Power of Habits",
            [
                "40% of daily actions are habits, not decisions",
                "Habit loop: cue → routine → reward (Charles Duhigg)",
                "New habit formation takes 66 days on average",
                "Implementation intentions increase success rate by 91%",
                "Keystone habits trigger cascading positive changes",
                "Habit stacking: attach new habits to existing ones",
            ],
            [
                ("What percentage of daily actions are habits?",
                 ["20%", "30%", "40%", "50%"], 2),
                ("How many days does new habit formation take on average?",
                 ["21 days", "45 days", "66 days", "90 days"], 2),
                ("By how much do implementation intentions increase success?",
                 ["51%", "71%", "81%", "91%"], 3),
            ],
        ),
        (
            "Flow State Performance",
            [
                "Concept developed by Mihaly Csikszentmihalyi in 1975",
                "Flow increases productivity by up to 500%",
                "Requires challenge-skill balance (4% above current ability)",
                "Average time to enter flow: 15-20 minutes",
                "Interruptions reset the flow timer completely",
                "Flow triggers 5 neurochemicals: dopamine, norepinephrine, endorphins, anandamide, serotonin",
            ],
            [
                ("Who developed the concept of flow?",
                 ["Daniel Pink", "Mihaly Csikszentmihalyi", "Cal Newport", "Adam Grant"], 1),
                ("By how much can flow increase productivity?",
                 ["100%", "200%", "350%", "500%"], 3),
                ("How long does it take to enter flow?",
                 ["5-10 minutes", "15-20 minutes", "25-30 minutes", "35-40 minutes"], 1),
            ],
        ),
        (
            "Grit and Perseverance",
            [
                "Researched by Angela Duckworth at UPenn",
                "Grit predicts success better than IQ in 78% of studies",
                "West Point cadets: grit score predicted completion rate",
                "Grit = passion + sustained persistence over years",
                "Gritty individuals practice 32% more hours weekly",
                "Grit can be developed — it's not purely innate",
            ],
            [
                ("Who researched grit?",
                 ["Carol Dweck", "Angela Duckworth", "Martin Seligman", "Dan Pink"], 1),
                ("In what percentage of studies does grit outpredict IQ?",
                 ["58%", "68%", "78%", "88%"], 2),
                ("How much more do gritty individuals practice weekly?",
                 ["12%", "22%", "32%", "42%"], 2),
            ],
        ),
    ],
    "neuroplasticity": [
        (
            "Brain Plasticity Basics",
            [
                "The brain forms 1 million new neural connections per second in infancy",
                "Adults generate ~700 new neurons daily in the hippocampus",
                "London taxi drivers have 16% larger posterior hippocampi",
                "Neuroplasticity peaks before age 25 but continues lifelong",
                "Learning a new skill increases gray matter in 2 weeks",
                "Sleep consolidates neural pathways — 7-9 hours optimal",
            ],
            [
                ("How many new neurons do adults generate daily?",
                 ["200", "500", "700", "1,000"], 2),
                ("How much larger are taxi drivers' posterior hippocampi?",
                 ["8%", "12%", "16%", "22%"], 2),
                ("How quickly can learning increase gray matter?",
                 ["2 days", "2 weeks", "2 months", "6 months"], 1),
            ],
        ),
        (
            "Memory Formation",
            [
                "Short-term memory holds 7±2 items (Miller's Law, 1956)",
                "Long-term potentiation (LTP) strengthens synapses",
                "Spaced repetition improves retention by 200%",
                "The forgetting curve: 70% lost within 24 hours without review",
                "Emotional memories are 3x stronger due to amygdala activation",
                "Sleep replays memories at 20x speed during REM",
            ],
            [
                ("How many items can short-term memory hold?",
                 ["3±1", "5±2", "7±2", "9±3"], 2),
                ("How much is forgotten within 24 hours without review?",
                 ["40%", "55%", "70%", "85%"], 2),
                ("How much faster does sleep replay memories?",
                 ["5x", "10x", "20x", "50x"], 2),
            ],
        ),
        (
            "Exercise and the Brain",
            [
                "Aerobic exercise increases hippocampal volume by 2%",
                "BDNF (brain-derived neurotrophic factor) rises 32% after exercise",
                "20 minutes of walking improves attention for 2 hours",
                "Regular exercisers have 15% better executive function",
                "Exercise reduces dementia risk by 30-40%",
                "Peak cognitive benefit: 150 minutes moderate exercise/week",
            ],
            [
                ("By how much does aerobic exercise increase hippocampal volume?",
                 ["1%", "2%", "4%", "6%"], 1),
                ("How much does BDNF rise after exercise?",
                 ["12%", "22%", "32%", "42%"], 2),
                ("How many minutes of moderate exercise per week is optimal?",
                 ["90 minutes", "120 minutes", "150 minutes", "200 minutes"], 2),
            ],
        ),
        (
            "Meditation and Neural Changes",
            [
                "8 weeks of meditation increases cortical thickness by 1.5mm",
                "Meditators show 25% more gray matter in the prefrontal cortex",
                "Default mode network activity decreases by 50% during meditation",
                "Mindfulness reduces amygdala reactivity by 22%",
                "Long-term meditators (10,000+ hours) show gamma wave increases of 700%",
                "Just 10 minutes daily improves working memory by 14%",
            ],
            [
                ("How much does cortical thickness increase after 8 weeks?",
                 ["0.5mm", "1.0mm", "1.5mm", "2.0mm"], 2),
                ("By how much does mindfulness reduce amygdala reactivity?",
                 ["12%", "17%", "22%", "28%"], 2),
                ("How much does 10 min daily meditation improve working memory?",
                 ["8%", "14%", "20%", "26%"], 1),
            ],
        ),
        (
            "Bilingualism and Cognition",
            [
                "Bilinguals switch tasks 28% faster than monolinguals",
                "Speaking 2+ languages delays dementia onset by 4.5 years",
                "Bilingual brains have denser gray matter in the ACC",
                "Language switching strengthens the dorsolateral prefrontal cortex",
                "Children exposed to 2 languages by age 3 show 20% better attention",
                "The bilingual advantage peaks between ages 60-80",
            ],
            [
                ("How much faster do bilinguals switch tasks?",
                 ["14%", "21%", "28%", "35%"], 2),
                ("By how many years does bilingualism delay dementia?",
                 ["2.5 years", "3.5 years", "4.5 years", "5.5 years"], 2),
                ("At what age range does the bilingual advantage peak?",
                 ["30-50", "40-60", "50-70", "60-80"], 3),
            ],
        ),
    ],
    "humor": [
        (
            "Laughter Science",
            [
                "Average adult laughs 17 times per day",
                "Children laugh about 300 times per day",
                "A good laugh burns 10-40 calories",
                "Laughter releases endorphins — pain tolerance rises 10%",
                "Gelotology: the scientific study of laughter",
                "Laughter is 30x more likely in social settings",
            ],
            [
                ("How many times does an average adult laugh per day?",
                 ["7", "17", "27", "47"], 1),
                ("What is the scientific study of laughter called?",
                 ["Risology", "Gelotology", "Humorology", "Comicology"], 1),
                ("How much more likely is laughter in social settings?",
                 ["10x", "20x", "30x", "50x"], 2),
            ],
        ),
        (
            "Weird Animal Facts",
            [
                "A group of flamingos is called a 'flamboyance'",
                "Octopuses have 3 hearts and blue blood",
                "Cows have best friends and get stressed when separated",
                "A snail can sleep for 3 years continuously",
                "Dolphins sleep with one eye open (unihemispheric sleep)",
                "Honey never spoils — 3,000-year-old honey is still edible",
            ],
            [
                ("How many hearts does an octopus have?",
                 ["1", "2", "3", "4"], 2),
                ("How long can a snail sleep?",
                 ["3 months", "1 year", "3 years", "5 years"], 2),
                ("What is a group of flamingos called?",
                 ["A flock", "A flamboyance", "A flutter", "A parade"], 1),
            ],
        ),
        (
            "Absurd World Records",
            [
                "Longest hiccupping spree: 68 years (Charles Osborne)",
                "Most T-shirts worn at once: 260 shirts",
                "Fastest 100m on all fours: 15.71 seconds (Kenichi Ito)",
                "Longest fingernails ever: 8.65 meters total (Lee Redmond)",
                "Most people in a Mini Cooper: 28 people",
                "Loudest purr by a cat: 67.8 decibels (Merlin)",
            ],
            [
                ("How long did the longest hiccupping spree last?",
                 ["12 years", "34 years", "68 years", "91 years"], 2),
                ("How many T-shirts were worn at once?",
                 ["155", "210", "260", "305"], 2),
                ("How loud was the loudest cat purr?",
                 ["45.2 dB", "56.4 dB", "67.8 dB", "78.3 dB"], 2),
            ],
        ),
        (
            "Food Oddities",
            [
                "Bananas are berries, but strawberries are not",
                "Honey is essentially bee vomit (regurgitated nectar)",
                "Peanuts are not nuts — they're legumes",
                "Ketchup was sold as medicine in the 1830s",
                "Apples float because they are 25% air",
                "A single spaghetti noodle is called a 'spaghetto'",
            ],
            [
                ("What percentage of an apple is air?",
                 ["10%", "15%", "25%", "35%"], 2),
                ("When was ketchup sold as medicine?",
                 ["1790s", "1830s", "1870s", "1910s"], 1),
                ("What is a single spaghetti noodle called?",
                 ["Spaghettino", "Spaghetto", "Spaghettini", "Spago"], 1),
            ],
        ),
        (
            "Useless But True",
            [
                "The inventor of the Pringles can is buried in one",
                "A jiffy is an actual unit of time: 1/100th of a second",
                "The dot over the letter 'i' is called a 'tittle'",
                "Scotland's national animal is the unicorn",
                "There are more possible chess games than atoms in the universe",
                "The average person walks 150,000 km in a lifetime (3.75x around Earth)",
            ],
            [
                ("What is a jiffy in seconds?",
                 ["1/10th", "1/50th", "1/100th", "1/1000th"], 2),
                ("What is the dot over 'i' called?",
                 ["A pip", "A tittle", "A dot", "A jot"], 1),
                ("What is Scotland's national animal?",
                 ["Highland cow", "Loch Ness monster", "Unicorn", "Red deer"], 2),
            ],
        ),
    ],
    "history": [
        (
            "Ancient Rome",
            [
                "Founded: 753 BC (traditional date)",
                "Peak population: 1 million people (2nd century AD)",
                "Roman roads network: 400,000 km total",
                "Colosseum capacity: 50,000-80,000 spectators",
                "Roman Empire lasted 503 years (27 BC – 476 AD)",
                "Concrete invented by Romans — Pantheon dome still stands",
            ],
            [
                ("How extensive was the Roman road network?",
                 ["100,000 km", "250,000 km", "400,000 km", "600,000 km"], 2),
                ("What was the Colosseum's capacity?",
                 ["20,000-40,000", "50,000-80,000", "90,000-120,000", "130,000-150,000"], 1),
                ("How long did the Roman Empire last?",
                 ["303 years", "403 years", "503 years", "603 years"], 2),
            ],
        ),
        (
            "The Moon Landing",
            [
                "Date: July 20, 1969 (Apollo 11)",
                "Neil Armstrong: first human on the Moon",
                "Mission duration: 8 days, 3 hours, 18 minutes",
                "Distance to Moon: 384,400 km",
                "Moon walk duration: 2 hours 31 minutes",
                "Total Apollo Moon walkers: 12 astronauts",
            ],
            [
                ("How long was the Apollo 11 mission?",
                 ["5 days 12 hours", "8 days 3 hours", "10 days 7 hours", "12 days 1 hour"], 1),
                ("How far is the Moon from Earth?",
                 ["284,400 km", "384,400 km", "484,400 km", "584,400 km"], 1),
                ("How many astronauts walked on the Moon total?",
                 ["6", "8", "10", "12"], 3),
            ],
        ),
        (
            "World War II Key Numbers",
            [
                "Duration: 1939-1945 (6 years)",
                "Countries involved: 61 nations",
                "D-Day: June 6, 1944 — 156,000 Allied troops landed",
                "Total military deaths: approximately 25 million",
                "The war cost an estimated $1.3 trillion (1945 dollars)",
                "V-E Day: May 8, 1945 — Victory in Europe",
            ],
            [
                ("How many nations were involved in WWII?",
                 ["31", "41", "51", "61"], 3),
                ("How many Allied troops landed on D-Day?",
                 ["78,000", "116,000", "156,000", "196,000"], 2),
                ("What was V-E Day?",
                 ["April 2, 1945", "May 8, 1945", "June 14, 1945", "July 20, 1945"], 1),
            ],
        ),
        (
            "The Renaissance",
            [
                "Period: roughly 1400-1600 AD",
                "Birthplace: Florence, Italy",
                "Gutenberg's printing press: invented around 1440",
                "Leonardo da Vinci painted the Mona Lisa: 1503-1519",
                "Michelangelo's Sistine Chapel ceiling: 4 years to complete",
                "The word 'Renaissance' means 'rebirth' in French",
            ],
            [
                ("When was the printing press invented?",
                 ["Around 1380", "Around 1440", "Around 1500", "Around 1560"], 1),
                ("How long did the Sistine Chapel ceiling take?",
                 ["2 years", "4 years", "6 years", "8 years"], 1),
                ("Where did the Renaissance originate?",
                 ["Rome", "Venice", "Florence", "Milan"], 2),
            ],
        ),
        (
            "The Industrial Revolution",
            [
                "Started in Britain around 1760",
                "Steam engine improved by James Watt in 1769",
                "World population doubled from 1 to 2 billion (1800-1927)",
                "First railway: Stockton to Darlington, 1825 (40 km)",
                "Child labor: children as young as 5 worked 16-hour days",
                "By 1850, Britain produced 50% of the world's iron",
            ],
            [
                ("When did James Watt improve the steam engine?",
                 ["1749", "1759", "1769", "1779"], 2),
                ("How long was the first railway?",
                 ["20 km", "30 km", "40 km", "50 km"], 2),
                ("What percentage of world iron did Britain produce by 1850?",
                 ["30%", "40%", "50%", "60%"], 2),
            ],
        ),
    ],
    "nutrition": [
        (
            "Macronutrients",
            [
                "Protein: 4 calories per gram",
                "Carbohydrates: 4 calories per gram",
                "Fat: 9 calories per gram",
                "Alcohol: 7 calories per gram (no nutritional value)",
                "Recommended daily protein: 0.8g per kg body weight",
                "Brain uses 120g of glucose per day",
            ],
            [
                ("How many calories per gram does fat contain?",
                 ["4", "7", "9", "12"], 2),
                ("How many calories per gram does alcohol have?",
                 ["4", "5", "7", "9"], 2),
                ("How much glucose does the brain use daily?",
                 ["60g", "90g", "120g", "150g"], 2),
            ],
        ),
        (
            "Hydration Facts",
            [
                "Human body is 60% water",
                "Brain is 73% water",
                "2% dehydration reduces cognitive performance by 20%",
                "Recommended intake: 2.7L (women) / 3.7L (men) daily",
                "Kidneys filter 180 liters of blood per day",
                "Thirst signal activates at 1-2% body water loss",
            ],
            [
                ("What percentage of the brain is water?",
                 ["53%", "63%", "73%", "83%"], 2),
                ("How much blood do kidneys filter daily?",
                 ["80 liters", "120 liters", "180 liters", "240 liters"], 2),
                ("At what dehydration level does cognition drop 20%?",
                 ["1%", "2%", "4%", "6%"], 1),
            ],
        ),
        (
            "Vitamins and Minerals",
            [
                "Vitamin D: 600 IU recommended daily (ages 1-70)",
                "Iron: men need 8mg/day, women need 18mg/day",
                "Vitamin C: 90mg/day for men, 75mg for women",
                "Calcium: 1,000mg/day for adults under 50",
                "B12 deficiency affects 15% of people over 60",
                "Magnesium is involved in 300+ enzymatic reactions",
            ],
            [
                ("How much iron do women need daily?",
                 ["8mg", "12mg", "18mg", "24mg"], 2),
                ("How many enzymatic reactions involve magnesium?",
                 ["100+", "200+", "300+", "400+"], 2),
                ("What percentage of people over 60 are B12 deficient?",
                 ["5%", "10%", "15%", "25%"], 2),
            ],
        ),
        (
            "Gut-Brain Connection",
            [
                "The gut contains 500 million neurons (enteric nervous system)",
                "95% of serotonin is produced in the gut",
                "Gut microbiome: 39 trillion bacteria (more than human cells)",
                "Vagus nerve: primary communication highway (80% gut→brain)",
                "Fiber intake of 30g/day reduces depression risk by 26%",
                "Probiotics improve mood scores by 18% in clinical trials",
            ],
            [
                ("What percentage of serotonin is produced in the gut?",
                 ["65%", "80%", "95%", "99%"], 2),
                ("How many bacteria are in the gut microbiome?",
                 ["9 trillion", "19 trillion", "39 trillion", "59 trillion"], 2),
                ("By how much does 30g fiber/day reduce depression risk?",
                 ["12%", "18%", "26%", "34%"], 2),
            ],
        ),
        (
            "Caffeine and Performance",
            [
                "Caffeine half-life: 5-6 hours",
                "Peak blood concentration: 30-60 minutes after intake",
                "Improves reaction time by 11% on average",
                "Optimal dose: 3-6 mg per kg body weight",
                "400mg/day considered safe for adults (≈4 cups coffee)",
                "Caffeine blocks adenosine receptors, reducing sleepiness",
            ],
            [
                ("What is caffeine's half-life?",
                 ["1-2 hours", "3-4 hours", "5-6 hours", "7-8 hours"], 2),
                ("By how much does caffeine improve reaction time?",
                 ["5%", "8%", "11%", "15%"], 2),
                ("How much caffeine per day is considered safe?",
                 ["200mg", "300mg", "400mg", "500mg"], 2),
            ],
        ),
    ],
}

# User data configuration
USER_DATA_CONFIG = {
    "file_name": "neural_profile.json",
    "max_history_entries": 500,
    "xp_per_correct": 10,
}

# Reading text library — built-in passages of varying difficulty.
# Keys are display names, values are (difficulty_label, word_count, text).
TEXT_LIBRARY = {
    "Speed Reading Basics": (
        "Easy",
        "Speed reading is the process of rapidly recognizing and absorbing phrases "
        "or sentences on a page all at once rather than identifying individual words. "
        "The amount of information that we process seems to be growing by the day, "
        "whether it is emails, reports, websites, or books. We are likely to feel "
        "pressured to get through this information more quickly so that we can stay "
        "informed and make better decisions. Most people read at an average rate of "
        "250 words per minute, though some are naturally quicker than others. But the "
        "ability to speed read could mean that you double this rate. We do not "
        "necessarily read each letter in a word or each word in a sentence. Instead, "
        "we use context and prior knowledge to fill in the gaps. The key to speed "
        "reading is to train your eyes and brain to process information more "
        "efficiently. This involves reducing subvocalization, expanding your visual "
        "span, and minimizing regression. With practice, you can learn to take in "
        "more words per fixation and move through text more fluidly. The goal is not "
        "just to read faster but to maintain or improve comprehension while doing so."
    ),
    "The Science of Memory": (
        "Easy",
        "Memory is the faculty of the brain by which data or information is encoded, "
        "stored, and retrieved when needed. It is the retention of information over "
        "time for the purpose of influencing future action. Memory is often understood "
        "as an informational processing system with explicit and implicit functioning "
        "that is made up of a sensory processor, short-term memory, and long-term "
        "memory. The sensory processor allows information from the outside world to "
        "be sensed in the form of chemical and physical stimuli and attended to with "
        "various levels of focus and intent. Working memory serves as an encoding and "
        "retrieval processor. Information in the form of stimuli is encoded in "
        "accordance with explicit or implicit functions by the working memory "
        "processor. The working memory also retrieves information from previously "
        "stored material. Finally, the randomly accessed long-term memory store "
        "allows information to be retained indefinitely."
    ),
    "Cognitive Load Theory": (
        "Medium",
        "Cognitive load theory suggests that learning happens best under conditions "
        "that are aligned with human cognitive architecture. The structure of human "
        "cognitive architecture, while not known precisely, is discernible through "
        "the results of experimental research. Researchers have identified three "
        "types of cognitive load: intrinsic, extraneous, and germane. Intrinsic "
        "cognitive load is inherent to the material being learned and is determined "
        "by the levels of element interactivity. Extraneous cognitive load is "
        "generated by the manner in which information is presented to learners and "
        "is under the control of instructional designers. Germane cognitive load "
        "refers to the work put into creating a permanent store of knowledge, or a "
        "schema. Unlike intrinsic and extraneous loads, germane load is considered "
        "desirable because it contributes directly to learning. The theory has been "
        "used to explain a wide range of experimental findings and has generated "
        "several instructional design principles. These include the worked example "
        "effect, the split attention effect, the redundancy effect, and the modality "
        "effect. Each of these principles provides guidance on how to structure "
        "instructional materials to optimize learning by managing cognitive load."
    ),
    "Neuroplasticity and Learning": (
        "Medium",
        "Neuroplasticity, also known as neural plasticity or brain plasticity, is "
        "the ability of neural networks in the brain to change through growth and "
        "reorganization. It is when the brain is rewired to function in some way "
        "that differs from how it previously functioned. These changes range from "
        "individual neuron pathways making new connections to systematic adjustments "
        "like cortical remapping. Examples of neuroplasticity include circuit and "
        "network changes that result from learning a new ability, environmental "
        "influences, practice, and psychological stress. Neuroplasticity was once "
        "thought by neuroscientists to manifest only during childhood, but research "
        "in the latter half of the twentieth century showed that many aspects of the "
        "brain can be altered even through adulthood. The developing brain exhibits "
        "a higher degree of plasticity than the adult brain. Activity-dependent "
        "plasticity can have significant implications for healthy development, "
        "learning, memory, and recovery from brain damage. During most of the "
        "twentieth century, the general consensus among neuroscientists was that "
        "brain structure is relatively immutable after a critical period during "
        "early childhood. This belief has been challenged by new findings, revealing "
        "that many aspects of the brain remain plastic even into adulthood."
    ),
    "Visual Processing in Reading": (
        "Hard",
        "The process of reading involves a complex interplay between visual "
        "perception, attention, and higher-order cognitive processes. When a reader "
        "fixates on a word, the visual system extracts information from a region "
        "known as the perceptual span, which extends approximately 3 to 4 characters "
        "to the left and 14 to 15 characters to the right of fixation for readers "
        "of left-to-right orthographies. Within this span, detailed letter and word "
        "identification occurs in the foveal region, which subtends approximately "
        "2 degrees of visual angle. Parafoveal processing provides preliminary "
        "information about upcoming words, including word length, initial letters, "
        "and sometimes partial phonological or semantic information. This parafoveal "
        "preview benefit facilitates subsequent foveal processing when the eyes move "
        "to fixate the previewed word. Saccadic eye movements, which typically span "
        "7 to 9 characters, serve to bring new text into foveal vision. The duration "
        "of fixations, averaging approximately 200 to 250 milliseconds, reflects the "
        "time required for lexical access and integration of the fixated word into "
        "the ongoing sentence representation. Skilled readers demonstrate remarkable "
        "efficiency in coordinating these perceptual and cognitive processes, "
        "achieving reading rates that far exceed what would be predicted by simple "
        "serial letter-by-letter processing models."
    ),
    "Dual Process Theory of Cognition": (
        "Hard",
        "Dual process theory posits that human cognition operates through two "
        "fundamentally distinct systems. System 1 is characterized by automatic, "
        "fast, and effortless processing that operates below the threshold of "
        "conscious awareness. It relies on heuristics, associative memory, and "
        "pattern recognition to generate rapid judgments and decisions. System 2, "
        "in contrast, is deliberate, slow, and effortful, requiring conscious "
        "attention and working memory resources. It is engaged when we encounter "
        "novel situations, perform complex computations, or override the automatic "
        "responses generated by System 1. The interaction between these two systems "
        "is central to understanding human reasoning, decision-making, and judgment "
        "under uncertainty. Research by Kahneman and Tversky demonstrated that "
        "System 1 processing, while generally adaptive, can lead to systematic "
        "biases and errors in judgment. These cognitive biases include anchoring, "
        "availability heuristic, representativeness, and framing effects. The "
        "recognition of these dual processes has profound implications for fields "
        "ranging from behavioral economics to clinical psychology. Understanding "
        "when and how each system is engaged allows for the design of interventions "
        "that can improve decision-making by either leveraging System 1 efficiency "
        "or engaging System 2 deliberation when accuracy is paramount."
    ),
    "Why Reading Changes Everything": (
        "Easy",
        "Reading is one of the most powerful habits a person can develop. Unlike "
        "passive media consumption, reading demands active engagement from your brain. "
        "You construct mental images, follow arguments, and build connections between "
        "ideas. This process strengthens neural pathways and improves cognitive "
        "function in ways that no other activity can replicate. Studies consistently "
        "show that regular readers have larger vocabularies, stronger analytical "
        "thinking skills, and greater empathy. Reading fiction, in particular, allows "
        "you to experience the world through different perspectives, building emotional "
        "intelligence that transfers directly to real-life relationships. Non-fiction "
        "reading compounds knowledge over time. Each book you read adds to a mental "
        "framework that makes learning the next thing easier. Warren Buffett attributes "
        "much of his success to reading 500 pages a day early in his career. Bill Gates "
        "reads about 50 books a year. They understand something fundamental: reading is "
        "not a luxury, it is an investment. The return on that investment is a sharper "
        "mind, better decisions, and a deeper understanding of the world. Every book "
        "you finish is proof that you can commit to something and see it through. That "
        "discipline carries over into every other area of your life."
    ),
    "The Power of Your Subconscious Mind": (
        "Easy",
        "Your subconscious mind processes roughly 11 million bits of information per "
        "second, while your conscious mind handles only about 50. This means the vast "
        "majority of your thinking, decision-making, and behavior is driven by processes "
        "you are not even aware of. The subconscious does not distinguish between what "
        "is real and what is vividly imagined. This is why visualization works. Athletes "
        "who mentally rehearse their performance activate the same neural pathways as "
        "those who physically practice. The thoughts you repeat become beliefs, and "
        "beliefs shape actions. If you consistently tell yourself you are a slow reader, "
        "your subconscious accepts that as truth and acts accordingly. But the reverse "
        "is equally true. When you train consistently and see measurable progress, your "
        "subconscious updates its model of what you are capable of. This is not wishful "
        "thinking. It is how the brain works. Every training session you complete sends "
        "a signal to your subconscious: I am someone who improves. Over time, that "
        "identity becomes self-reinforcing. The effort you put into training your "
        "reading speed is simultaneously training your mind to believe in growth."
    ),
    "Thoughts Shape Reality": (
        "Medium",
        "The quality of your thoughts determines the quality of your life. This is not "
        "a motivational cliche but a neurological fact. Every thought you think triggers "
        "a cascade of neurochemical events. Positive, focused thoughts release dopamine "
        "and serotonin, which improve mood, motivation, and cognitive performance. "
        "Negative, scattered thoughts trigger cortisol, which impairs memory, reduces "
        "focus, and weakens the immune system. The brain is constantly rewiring itself "
        "based on what you pay attention to. Neuroscientists call this Hebbian learning: "
        "neurons that fire together wire together. If you spend your time consuming "
        "shallow content and reacting to distractions, you are literally building a "
        "brain optimized for distraction. If you spend time reading deeply, training "
        "your focus, and challenging your perception, you build a brain optimized for "
        "depth and clarity. The exercises in this application are designed to do exactly "
        "that. Flash perception trains rapid pattern recognition. Guided pacing builds "
        "sustained attention. Schulte grids expand peripheral awareness. Each exercise "
        "is a deliberate act of shaping your neural architecture. You are not just "
        "reading faster. You are becoming someone who thinks more clearly, focuses "
        "more deeply, and processes the world with greater precision."
    ),
}

# Training paths
# Each step: (exercise_type, label, params_dict)
# exercise_type maps to a launcher in the path execution screen.
TRAINING_PATH_CATEGORIES = [
    ("daily", "Daily Routines"),
    ("reading", "Speed Reading"),
    ("cognitive", "Cognitive Performance"),
    ("visual", "Visual Processing"),
    ("info", "Information Processing"),
]

TRAINING_PATHS = {
    # ── Daily Routines ──
    "daily_warmup": {
        "name": "Daily Warmup",
        "category": "daily",
        "description": "Quick 5-minute session to keep skills sharp",
        "adaptive": True,
        "steps": [
            ("priming", "Eye Priming: Mixed Saccades", {"mode": "saccade_diag", "delay": 500}),
            ("flash", "Flash: Adaptive Digits", {"low": 2, "high": 4, "rounds": 10}),
            ("eyespan", "Eye-Span: Adaptive", {"mode": "h", "width": 30, "low": 2, "high": 2, "rounds": 8}),
            ("schulte", "Schulte Grid", {}),
            ("pacer", "Pacer & Quiz: Comprehension Check", {}),
        ],
    },
    # Paths ordered by difficulty
    "foundation": {
        "name": "Foundation",
        "category": "reading",
        "description": "Build baseline perception and focus skills (2 weeks)",
        "steps": [
            ("priming", "Eye Priming: Horizontal Saccades", {"mode": "saccade_h", "delay": 600}),
            ("flash", "Flash: 2-3 Digits", {"low": 2, "high": 3, "rounds": 10}),
            ("flash", "Flash: 3 Digits Fixed", {"digits": 3, "rounds": 10}),
            ("eyespan", "Eye-Span: Narrow 30%", {"mode": "h", "width": 30, "low": 2, "high": 2, "rounds": 8}),
            ("schulte", "Schulte Grid", {}),
            ("flash", "Flash: 3-4 Digits", {"low": 3, "high": 4, "rounds": 10}),
            ("eyespan", "Eye-Span: Narrow 30%", {"mode": "h", "width": 30, "low": 2, "high": 2, "rounds": 10}),
            ("priming", "Eye Priming: Smooth Pursuit Circle", {"mode": "pursuit_circle", "cycles": 10}),
            ("flash", "Flash: 4 Digits Fixed", {"digits": 4, "rounds": 10}),
            ("eyespan", "Eye-Span: Horizontal 40%", {"mode": "h", "width": 40, "low": 2, "high": 2, "rounds": 10}),
            ("pacer", "Pacer & Quiz: Comprehension Check", {}),
        ],
    },
    "path_300": {
        "name": "Path to 300 WPM",
        "category": "reading",
        "description": "Gentle introduction to speed reading for complete beginners",
        "steps": [
            ("priming", "Eye Priming: Horizontal Saccades", {"mode": "saccade_h", "delay": 600}),
            ("flash", "Flash: 3 Digits Fixed", {"digits": 3, "rounds": 10}),
            ("eyespan", "Eye-Span: Narrow 30%", {"mode": "h", "width": 30, "low": 2, "high": 2, "rounds": 8}),
            ("rsvp", "RSVP: 200 WPM", {"wpm": 200}),
            ("chunking", "Chunking: 2-Word Phrases", {"chunk_size": 2, "wpm": 180}),
            ("flash", "Flash: 3-4 Digits", {"low": 3, "high": 4, "rounds": 10}),
            ("eyespan", "Eye-Span: Narrow 30%", {"mode": "h", "width": 30, "low": 2, "high": 2, "rounds": 10}),
            ("rsvp", "RSVP: 250 WPM", {"wpm": 250}),
            ("chunking", "Chunking: 2-Word Phrases", {"chunk_size": 2, "wpm": 220}),
            ("flash", "Flash: 4 Digits Fixed", {"digits": 4, "rounds": 10}),
            ("eyespan", "Eye-Span: Horizontal 40%", {"mode": "h", "width": 40, "low": 2, "high": 2, "rounds": 10}),
            ("rsvp", "RSVP: 300 WPM", {"wpm": 300}),
            ("chunking", "Chunking: 3-Word Phrases", {"chunk_size": 3, "wpm": 250}),
            ("schulte", "Schulte Grid", {}),
            ("pacer", "Pacer & Quiz: Comprehension Check", {}),
        ],
    },
    "path_400": {
        "name": "Path to 400 WPM",
        "category": "reading",
        "description": "Develop speed reading fundamentals for comfortable fast reading",
        "steps": [
            # Warmup
            ("priming", "Eye Priming: Expanding Saccades", {"mode": "saccade_expand", "delay": 500}),
            # Phase 1: Build perception at 300-350 WPM
            ("flash", "Flash: 4 Digits Fixed", {"digits": 4, "rounds": 12}),
            ("eyespan", "Eye-Span: Narrow 30%", {"mode": "h", "width": 30, "low": 2, "high": 2, "rounds": 10}),
            ("rsvp", "RSVP: 300 WPM", {"wpm": 300}),
            ("chunking", "Chunking: 3-Word Phrases", {"chunk_size": 3, "wpm": 280}),
            # Phase 2: Push to 350 WPM
            ("flash", "Flash: 4-5 Digits", {"low": 4, "high": 5, "rounds": 12}),
            ("eyespan", "Eye-Span: Horizontal 40%", {"mode": "h", "width": 40, "low": 2, "high": 2, "rounds": 10}),
            ("rsvp", "RSVP: 350 WPM", {"wpm": 350}),
            ("chunking", "Chunking: 3-Word Phrases", {"chunk_size": 3, "wpm": 320}),
            ("schulte", "Schulte Grid", {}),
            # Phase 3: Consolidate at 400 WPM
            ("priming", "Eye Priming: Vertical Saccades", {"mode": "saccade_v", "delay": 500}),
            ("flash", "Flash: 5-6 Digits", {"low": 5, "high": 6, "rounds": 12}),
            ("eyespan", "Eye-Span: Horizontal 50%", {"mode": "h", "width": 50, "low": 2, "high": 3, "rounds": 10}),
            ("rsvp", "RSVP: 400 WPM", {"wpm": 400}),
            ("chunking", "Chunking: 4-Word Phrases", {"chunk_size": 4, "wpm": 350}),
            ("pacer", "Pacer & Quiz: Comprehension Check", {}),
        ],
    },
    "path_600": {
        "name": "Path to 600 WPM",
        "category": "reading",
        "description": "Advanced training for high-speed reading with comprehension",
        "steps": [
            # Warmup
            ("priming", "Eye Priming: Figure-8 Pursuit", {"mode": "pursuit_figure8", "cycles": 12}),
            # Phase 1: Sharpen perception, read at 400-450 WPM
            ("flash", "Flash: 5 Digits Fixed", {"digits": 5, "rounds": 12}),
            ("eyespan", "Eye-Span: Horizontal 40%", {"mode": "h", "width": 40, "low": 2, "high": 3, "rounds": 10}),
            ("rsvp", "RSVP: 400 WPM", {"wpm": 400}),
            ("chunking", "Chunking: 4-Word Phrases", {"chunk_size": 4, "wpm": 380}),
            # Phase 2: Widen span, push to 500 WPM
            ("flash", "Flash: 5-7 Digits", {"low": 5, "high": 7, "rounds": 15}),
            ("eyespan", "Eye-Span: Horizontal 50%", {"mode": "h", "width": 50, "low": 2, "high": 3, "rounds": 12}),
            ("rsvp", "RSVP: 500 WPM", {"wpm": 500}),
            ("chunking", "Chunking: 4-Word Phrases", {"chunk_size": 4, "wpm": 450}),
            ("schulte", "Schulte Grid", {}),
            # Phase 3: Add vertical/mixed span, push to 550 WPM
            ("priming", "Eye Priming: Fast Expanding Saccades", {"mode": "saccade_expand", "delay": 400}),
            ("flash", "Flash: 6-7 Digits", {"low": 6, "high": 7, "rounds": 15}),
            ("eyespan", "Eye-Span: Vertical 50%", {"mode": "v", "width": 50, "low": 2, "high": 3, "rounds": 12}),
            ("rsvp", "RSVP: 550 WPM", {"wpm": 550}),
            ("chunking", "Chunking: 5-Word Phrases", {"chunk_size": 5, "wpm": 480}),
            # Phase 4: Consolidate at 600 WPM
            ("flash", "Flash: 6-8 Digits", {"low": 6, "high": 8, "rounds": 15}),
            ("eyespan", "Eye-Span: Mixed 50%", {"mode": "m", "width": 50, "low": 3, "high": 3, "rounds": 12}),
            ("rsvp", "RSVP: 600 WPM", {"wpm": 600}),
            ("chunking", "Chunking: 5-Word Phrases", {"chunk_size": 5, "wpm": 520}),
            ("pacer", "Pacer & Quiz: Comprehension Check", {}),
        ],
    },
    "path_800": {
        "name": "Path to 800 WPM",
        "category": "reading",
        "description": "Elite training pushing the limits of visual processing",
        "steps": [
            # Warmup
            ("priming", "Eye Priming: Fast Diagonal Saccades", {"mode": "saccade_diag", "delay": 350}),
            # Phase 1: Baseline at 550-600 WPM
            ("flash", "Flash: 6 Digits Fixed", {"digits": 6, "rounds": 15}),
            ("eyespan", "Eye-Span: Horizontal 50%", {"mode": "h", "width": 50, "low": 2, "high": 3, "rounds": 12}),
            ("rsvp", "RSVP: 550 WPM", {"wpm": 550}),
            ("chunking", "Chunking: 5-Word Phrases", {"chunk_size": 5, "wpm": 500}),
            # Phase 2: Push perception, read at 650 WPM
            ("flash", "Flash: 6-7 Digits", {"low": 6, "high": 7, "rounds": 15}),
            ("eyespan", "Eye-Span: Horizontal 60%", {"mode": "h", "width": 60, "low": 3, "high": 3, "rounds": 12}),
            ("rsvp", "RSVP: 650 WPM", {"wpm": 650}),
            ("chunking", "Chunking: 5-Word Phrases", {"chunk_size": 5, "wpm": 580}),
            ("schulte", "Schulte Grid", {}),
            # Phase 3: Mixed directions, push to 700 WPM
            ("priming", "Eye Priming: Fast Figure-8 Pursuit", {"mode": "pursuit_figure8", "cycles": 15}),
            ("flash", "Flash: 7-8 Digits", {"low": 7, "high": 8, "rounds": 15}),
            ("eyespan", "Eye-Span: Vertical 60%", {"mode": "v", "width": 60, "low": 3, "high": 4, "rounds": 12}),
            ("rsvp", "RSVP: 700 WPM", {"wpm": 700}),
            ("chunking", "Chunking: 6-Word Phrases", {"chunk_size": 6, "wpm": 620}),
            # Phase 4: Wide span, push to 750 WPM
            ("flash", "Flash: 7-9 Digits", {"low": 7, "high": 9, "rounds": 15}),
            ("eyespan", "Eye-Span: Mixed 70%", {"mode": "m", "width": 70, "low": 3, "high": 4, "rounds": 15}),
            ("rsvp", "RSVP: 750 WPM", {"wpm": 750}),
            ("chunking", "Chunking: 6-Word Phrases", {"chunk_size": 6, "wpm": 680}),
            # Phase 5: Consolidate at 800 WPM
            ("flash", "Flash: 8-10 Digits", {"low": 8, "high": 10, "rounds": 15}),
            ("eyespan", "Eye-Span: Mixed 80%", {"mode": "m", "width": 80, "low": 3, "high": 5, "rounds": 15}),
            ("rsvp", "RSVP: 800 WPM", {"wpm": 800}),
            ("chunking", "Chunking: 7-Word Phrases", {"chunk_size": 7, "wpm": 720}),
            ("pacer", "Pacer & Quiz: Comprehension Check", {}),
        ],
    },
    "perception_master": {
        "name": "Perception Master",
        "category": "visual",
        "description": "Intensive flash and eye-span training for maximum visual processing",
        "steps": [
            ("priming", "Eye Priming: Fast Horizontal Saccades", {"mode": "saccade_h", "delay": 400}),
            # Phase 1: Build digit span
            ("flash", "Flash: 4 Digits Fixed", {"digits": 4, "rounds": 12}),
            ("eyespan", "Eye-Span: Narrow 30%", {"mode": "h", "width": 30, "low": 2, "high": 2, "rounds": 10}),
            ("flash", "Flash: 5 Digits Fixed", {"digits": 5, "rounds": 12}),
            ("eyespan", "Eye-Span: Horizontal 40%", {"mode": "h", "width": 40, "low": 2, "high": 3, "rounds": 10}),
            # Phase 2: Increase span width and digit count
            ("flash", "Flash: 5-6 Digits", {"low": 5, "high": 6, "rounds": 12}),
            ("eyespan", "Eye-Span: Vertical 40%", {"mode": "v", "width": 40, "low": 2, "high": 3, "rounds": 10}),
            ("flash", "Flash: 6-7 Digits", {"low": 6, "high": 7, "rounds": 15}),
            ("eyespan", "Eye-Span: Mixed 50%", {"mode": "m", "width": 50, "low": 2, "high": 3, "rounds": 12}),
            ("schulte", "Schulte Grid", {}),
            # Phase 3: Elite perception
            ("priming", "Eye Priming: Fast Expanding Saccades", {"mode": "saccade_expand", "delay": 350}),
            ("flash", "Flash: 7-8 Digits", {"low": 7, "high": 8, "rounds": 15}),
            ("eyespan", "Eye-Span: Horizontal 60%", {"mode": "h", "width": 60, "low": 3, "high": 4, "rounds": 12}),
            ("eyespan", "Eye-Span: Mixed 70%", {"mode": "m", "width": 70, "low": 3, "high": 4, "rounds": 15}),
        ],
    },

    # ── Cognitive Performance ──
    "memory_foundations": {
        "name": "Memory Foundations",
        "category": "cognitive",
        "description": "Build working memory capacity through progressive challenges",
        "steps": [
            ("sequence_memory", "Sequence Memory: Warmup", {}),
            ("recall", "Recall: Words (5 items)", {"mode": "words", "count": 5}),
            ("recall", "Recall: Numbers (5 items)", {"mode": "numbers", "count": 5}),
            ("sequence_memory", "Sequence Memory: Extended", {}),
            ("recall", "Recall: Mixed (7 items)", {"mode": "mixed", "count": 7}),
            ("spaced_repetition", "Spaced Repetition: Review", {}),
            ("recall", "Recall: Words (10 items)", {"mode": "words", "count": 10}),
            ("sequence_memory", "Sequence Memory: Challenge", {}),
        ],
    },
    "attention_focus": {
        "name": "Attention & Focus",
        "category": "cognitive",
        "description": "Train sustained and divided attention across multiple tasks",
        "steps": [
            ("priming", "Eye Priming: Warmup", {"mode": "saccade_h", "delay": 500}),
            ("schulte", "Schulte Grid: Focus", {}),
            ("split_attention", "Split Attention: Sequential", {"mode": "sequential"}),
            ("mot", "MOT: 3 Targets", {"targets": 3, "duration": 6}),
            ("split_attention", "Split Attention: Simultaneous", {"mode": "simultaneous"}),
            ("mot", "MOT: 4 Targets", {"targets": 4, "duration": 8}),
            ("split_attention", "Split Attention: Rapid", {"mode": "rapid"}),
            ("mot", "MOT: 5 Targets", {"targets": 5, "duration": 8}),
        ],
    },
    "mental_agility": {
        "name": "Mental Agility",
        "category": "cognitive",
        "description": "Speed up decision-making and reaction time under pressure",
        "steps": [
            ("reaction_time", "Reaction Time: Simple", {"mode": "simple"}),
            ("rapid_decision", "Rapid Decision Grid: Warmup", {}),
            ("reaction_time", "Reaction Time: Choice", {"mode": "choice"}),
            ("split_attention", "Split Attention: Sequential", {"mode": "sequential"}),
            ("rapid_decision", "Rapid Decision Grid: Challenge", {}),
            ("reaction_time", "Reaction Time: Go/No-Go", {"mode": "go_nogo"}),
            ("split_attention", "Split Attention: Rapid", {"mode": "rapid"}),
            ("rapid_decision", "Rapid Decision Grid: Final", {}),
        ],
    },

    # ── Visual Processing ──
    "peripheral_vision": {
        "name": "Peripheral Vision",
        "category": "visual",
        "description": "Expand your useful field of view for faster reading and awareness",
        "steps": [
            ("priming", "Eye Priming: Expanding Saccades", {"mode": "saccade_expand", "delay": 500}),
            ("peripheral_flash", "Peripheral Flash: Warmup", {}),
            ("schulte", "Schulte Grid", {}),
            ("eyespan", "Eye-Span: Horizontal 30%", {"mode": "h", "width": 30, "low": 2, "high": 2, "rounds": 10}),
            ("peripheral_flash", "Peripheral Flash: Challenge", {}),
            ("eyespan", "Eye-Span: Horizontal 50%", {"mode": "h", "width": 50, "low": 2, "high": 3, "rounds": 12}),
            ("priming", "Eye Priming: Diagonal Saccades", {"mode": "saccade_diag", "delay": 400}),
            ("eyespan", "Eye-Span: Mixed 60%", {"mode": "m", "width": 60, "low": 3, "high": 4, "rounds": 12}),
        ],
    },
    "visual_tracking": {
        "name": "Visual Tracking",
        "category": "visual",
        "description": "Track moving objects and process fast visual stimuli",
        "steps": [
            ("priming", "Eye Priming: Smooth Pursuit Circle", {"mode": "pursuit_circle", "cycles": 10}),
            ("mot", "MOT: 3 Targets · 6s", {"targets": 3, "duration": 6}),
            ("peripheral_flash", "Peripheral Flash", {}),
            ("priming", "Eye Priming: Figure-8 Pursuit", {"mode": "pursuit_figure8", "cycles": 12}),
            ("mot", "MOT: 4 Targets · 8s", {"targets": 4, "duration": 8}),
            ("reaction_time", "Reaction Time: Choice", {"mode": "choice"}),
            ("mot", "MOT: 5 Targets · 8s", {"targets": 5, "duration": 8}),
            ("priming", "Eye Priming: Fast Expanding", {"mode": "saccade_expand", "delay": 350}),
        ],
    },

    # ── Information Processing ──
    "rapid_comprehension": {
        "name": "Rapid Comprehension",
        "category": "info",
        "description": "Extract and retain key facts from briefly presented information",
        "steps": [
            ("flash", "Flash: 4 Digits Warmup", {"digits": 4, "rounds": 10}),
            ("slide_processing", "Slides: 10s · Science", {"display_s": 10, "slides": 3, "category": "science"}),
            ("recall", "Recall: Words", {"mode": "words", "count": 7}),
            ("slide_processing", "Slides: 8s · Mixed", {"display_s": 8, "slides": 3, "category": "science,business,history"}),
            ("recall", "Recall: Mixed", {"mode": "mixed", "count": 8}),
            ("slide_processing", "Slides: 6s · Mixed", {"display_s": 6, "slides": 5, "category": "science,geography,nutrition"}),
            ("pacer", "Pacer & Quiz: Comprehension Check", {}),
        ],
    },
    "study_session": {
        "name": "Study Session",
        "category": "info",
        "description": "Structured learning and retention — review, absorb, recall",
        "steps": [
            ("spaced_repetition", "Spaced Repetition: Review Due Cards", {}),
            ("slide_processing", "Slides: 12s · Neuroplasticity", {"display_s": 12, "slides": 5, "category": "neuroplasticity"}),
            ("recall", "Recall: Words", {"mode": "words", "count": 8}),
            ("slide_processing", "Slides: 10s · Science", {"display_s": 10, "slides": 5, "category": "science"}),
            ("recall", "Recall: Numbers", {"mode": "numbers", "count": 6}),
            ("spaced_repetition", "Spaced Repetition: Final Review", {}),
        ],
    },

    # ── Daily Routines (additional) ──
    "full_brain_workout": {
        "name": "Full Brain Workout",
        "category": "daily",
        "description": "Comprehensive 15-20 minute session hitting all cognitive areas",
        "steps": [
            ("priming", "Eye Priming: Mixed Saccades", {"mode": "saccade_diag", "delay": 450}),
            ("flash", "Flash: 4-5 Digits", {"low": 4, "high": 5, "rounds": 10}),
            ("reaction_time", "Reaction Time: Simple", {"mode": "simple"}),
            ("mot", "MOT: 4 Targets", {"targets": 4, "duration": 8}),
            ("split_attention", "Split Attention: Simultaneous", {"mode": "simultaneous"}),
            ("slide_processing", "Slides: 8s · Mixed", {"display_s": 8, "slides": 5, "category": "science,history,business"}),
            ("recall", "Recall: Mixed", {"mode": "mixed", "count": 8}),
            ("schulte", "Schulte Grid", {}),
            ("pacer", "Pacer & Quiz: Comprehension Check", {}),
        ],
    },
    "quick_cognitive_check": {
        "name": "Quick Cognitive Check",
        "category": "daily",
        "description": "5-minute cognitive sharpness test — reaction, decisions, memory",
        "steps": [
            ("reaction_time", "Reaction Time: Simple", {"mode": "simple"}),
            ("rapid_decision", "Rapid Decision Grid", {}),
            ("sequence_memory", "Sequence Memory", {}),
            ("reaction_time", "Reaction Time: Go/No-Go", {"mode": "go_nogo"}),
        ],
    },
}
