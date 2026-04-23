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

TEXT_LIBRARY_DE = {
    "Grundlagen des Schnelllesens": (
        "Leicht",
        "Schnelllesen ist die Fähigkeit, Texte deutlich schneller als der Durchschnitt "
        "zu erfassen, ohne dabei das Verständnis zu verlieren. Die meisten Menschen lesen "
        "mit einer Geschwindigkeit von etwa 200 bis 250 Wörtern pro Minute. Mit gezieltem "
        "Training lässt sich diese Rate verdoppeln oder sogar verdreifachen. Der Schlüssel "
        "liegt darin, wie unsere Augen und unser Gehirn zusammenarbeiten. Beim normalen "
        "Lesen fixieren die Augen jedes einzelne Wort, oft sogar mehrfach. Geübte Leser "
        "hingegen erfassen ganze Wortgruppen in einer einzigen Fixation. Sie nutzen den "
        "Kontext und ihr Vorwissen, um Bedeutung schneller zu erschließen. Ein weiterer "
        "Faktor ist die Subvokalisierung — das innere Mitsprechen beim Lesen. Diese "
        "Gewohnheit begrenzt die Lesegeschwindigkeit auf das Tempo der gesprochenen "
        "Sprache. Durch Training kann man lernen, Wörter direkt visuell zu verarbeiten, "
        "ohne sie innerlich auszusprechen. Ebenso wichtig ist es, Regressionen zu "
        "vermeiden — das unbewusste Zurückspringen zu bereits gelesenen Textstellen. "
        "Ein Pacer hilft dabei, den Blick konsequent vorwärts zu führen. Das Ziel ist "
        "nicht nur Geschwindigkeit, sondern ein effizienterer Leseprozess insgesamt."
    ),
    "Die Wissenschaft des Gedächtnisses": (
        "Leicht",
        "Unser Gedächtnis ist keine einzelne Funktion, sondern ein komplexes System "
        "aus mehreren Komponenten. Das sensorische Gedächtnis hält Sinneseindrücke für "
        "Bruchteile von Sekunden fest. Das Arbeitsgedächtnis — oft auch Kurzzeitgedächtnis "
        "genannt — kann etwa sieben Informationseinheiten gleichzeitig verarbeiten und "
        "behält sie für 20 bis 30 Sekunden. Das Langzeitgedächtnis speichert Informationen "
        "potenziell unbegrenzt. Der Übergang vom Arbeits- ins Langzeitgedächtnis gelingt "
        "am besten durch Wiederholung, emotionale Verknüpfung und aktive Verarbeitung. "
        "Hermann Ebbinghaus entdeckte bereits 1885 die Vergessenskurve: Ohne Wiederholung "
        "vergessen wir innerhalb einer Stunde etwa 50 Prozent des Gelernten. Die verteilte "
        "Wiederholung — das Lernen in zunehmenden Abständen — ist die effektivste bekannte "
        "Methode gegen dieses Vergessen. Auch Schlaf spielt eine entscheidende Rolle. "
        "Während wir schlafen, konsolidiert das Gehirn Erinnerungen und überträgt sie "
        "vom Hippocampus in den Neokortex. Wer nach dem Lernen ausreichend schläft, "
        "behält deutlich mehr als jemand, der die Nacht durcharbeitet."
    ),
    "Konzentration und Fokus": (
        "Leicht",
        "Konzentration ist die Fähigkeit, die Aufmerksamkeit bewusst auf eine Aufgabe "
        "zu richten und Ablenkungen auszublenden. In einer Welt voller Benachrichtigungen "
        "und ständiger Erreichbarkeit wird diese Fähigkeit immer wertvoller — und immer "
        "seltener. Studien zeigen, dass der durchschnittliche Büroangestellte alle drei "
        "Minuten unterbrochen wird und bis zu 23 Minuten braucht, um wieder in den "
        "Zustand tiefer Konzentration zurückzufinden. Dieser Zustand, den der Psychologe "
        "Mihaly Csikszentmihalyi als Flow bezeichnet, ist der Schlüssel zu Höchstleistung. "
        "Im Flow verschmelzen Handlung und Bewusstsein, die Zeit scheint stillzustehen, "
        "und die Arbeit fühlt sich mühelos an. Flow entsteht, wenn die Anforderung einer "
        "Aufgabe genau dem eigenen Können entspricht — weder zu leicht noch zu schwer. "
        "Konzentration lässt sich trainieren wie ein Muskel. Kurze, regelmäßige Übungen "
        "sind dabei wirksamer als seltene Marathonsitzungen. Schon 15 bis 20 Minuten "
        "tägliches Training können die Aufmerksamkeitsspanne messbar verbessern."
    ),
    "Neuroplastizität und Lernen": (
        "Mittel",
        "Neuroplastizität bezeichnet die Fähigkeit des Gehirns, sich durch Erfahrung "
        "und Training strukturell und funktionell zu verändern. Lange glaubte die "
        "Wissenschaft, dass das Gehirn nach der Kindheit weitgehend unveränderlich sei. "
        "Heute wissen wir, dass neuronale Netzwerke sich ein Leben lang anpassen können. "
        "Wenn wir eine neue Fähigkeit erlernen, bilden sich neue synaptische Verbindungen. "
        "Bei regelmäßiger Wiederholung werden diese Verbindungen stärker — ein Prozess, "
        "den der Neurowissenschaftler Donald Hebb mit dem Prinzip zusammenfasste: Neuronen, "
        "die gemeinsam feuern, vernetzen sich. Umgekehrt schwächen sich Verbindungen ab, "
        "die nicht genutzt werden. Das Gehirn ist also kein statisches Organ, sondern ein "
        "dynamisches System, das sich ständig an seine Anforderungen anpasst. Für das "
        "Schnelllesen bedeutet das: Die visuellen und kognitiven Fähigkeiten, die schnelles "
        "Lesen ermöglichen, lassen sich durch gezieltes Training aufbauen. Die Erweiterung "
        "der Blickspanne, die Reduktion von Regressionen und die Beschleunigung der "
        "Wortverarbeitung sind keine angeborenen Talente, sondern trainierbare Fertigkeiten. "
        "Entscheidend ist die Regelmäßigkeit: Tägliche kurze Einheiten sind wirksamer als "
        "gelegentliche intensive Sitzungen, weil sie dem Gehirn Zeit geben, die neuen "
        "Verbindungen zu festigen."
    ),
    "Visuelle Wahrnehmung beim Lesen": (
        "Mittel",
        "Beim Lesen bewegen sich unsere Augen nicht gleichmäßig über den Text, sondern "
        "in schnellen Sprüngen, sogenannten Sakkaden. Zwischen diesen Sprüngen verharren "
        "die Augen für etwa 200 bis 250 Millisekunden auf einer Stelle — das sind die "
        "Fixationen, in denen die eigentliche Informationsaufnahme stattfindet. Die "
        "Wahrnehmungsspanne erstreckt sich dabei etwa 3 bis 4 Zeichen nach links und "
        "14 bis 15 Zeichen nach rechts von der Fixation. Im Zentrum des Blickfelds, "
        "der Fovea, werden Buchstaben und Wörter scharf erkannt. In der Parafovea — "
        "dem Bereich direkt daneben — werden bereits vorbereitende Informationen über "
        "das nächste Wort gewonnen: Wortlänge, Anfangsbuchstaben und teilweise sogar "
        "Bedeutung. Geübte Leser nutzen diese parafoveale Vorschau besonders effektiv. "
        "Sie benötigen weniger Fixationen pro Zeile und machen kürzere Fixationen. "
        "Regressionen — Rücksprünge zu bereits gelesenen Wörtern — machen bei "
        "ungeübten Lesern bis zu 15 Prozent aller Augenbewegungen aus. Training mit "
        "einem visuellen Pacer kann diese Regressionen deutlich reduzieren und die "
        "Lesegeschwindigkeit nachhaltig steigern."
    ),
    "Arbeitsgedächtnis und Leseverständnis": (
        "Mittel",
        "Das Arbeitsgedächtnis ist die kognitive Werkbank, auf der wir Informationen "
        "kurzfristig halten und verarbeiten. Seine Kapazität ist begrenzt — George Miller "
        "beschrieb 1956 die magische Zahl 7 plus minus 2 als typische Spanne. Beim Lesen "
        "spielt das Arbeitsgedächtnis eine zentrale Rolle: Es hält den Anfang eines Satzes "
        "im Bewusstsein, während die Augen das Ende erreichen. Es verknüpft Pronomen mit "
        "ihren Bezugswörtern und integriert neue Informationen in das bestehende "
        "Textverständnis. Forschung zeigt einen starken Zusammenhang zwischen "
        "Arbeitsgedächtniskapazität und Leseverständnis. Menschen mit größerem "
        "Arbeitsgedächtnis verstehen komplexe Texte besser, weil sie mehr Kontext "
        "gleichzeitig verfügbar halten können. Die gute Nachricht: Das Arbeitsgedächtnis "
        "lässt sich trainieren. Sequenz-Gedächtnis-Übungen, bei denen zunehmend lange "
        "Folgen von Zahlen oder Wörtern reproduziert werden müssen, erweitern die "
        "Kapazität messbar. Chunking — das Zusammenfassen einzelner Elemente zu "
        "bedeutungsvollen Gruppen — ist eine weitere wirksame Strategie. Statt sich "
        "sieben einzelne Ziffern zu merken, fasst man sie zu zwei oder drei Zahlengruppen "
        "zusammen und erhöht so die effektive Speicherkapazität."
    ),
    "Die Kunst des aktiven Lesens": (
        "Schwer",
        "Aktives Lesen unterscheidet sich grundlegend vom passiven Aufnehmen von Text. "
        "Während passive Leser ihre Augen über die Seite gleiten lassen und hoffen, dass "
        "Informationen hängen bleiben, gehen aktive Leser strategisch vor. Sie stellen "
        "vor dem Lesen Fragen an den Text, überfliegen zunächst die Struktur und aktivieren "
        "ihr Vorwissen zum Thema. Während des Lesens markieren sie Schlüsselstellen, "
        "formulieren Zusammenfassungen in eigenen Worten und stellen Verbindungen zu "
        "bereits Bekanntem her. Nach dem Lesen überprüfen sie ihr Verständnis durch "
        "Selbstbefragung. Diese Methode, bekannt als SQ3R (Survey, Question, Read, "
        "Recite, Review), wurde bereits 1946 von Francis Robinson entwickelt und ist "
        "bis heute eine der am besten erforschten Lesestrategien. Metaanalysen zeigen, "
        "dass aktive Leser nicht nur mehr behalten, sondern den Stoff auch tiefer "
        "verstehen und besser auf neue Situationen übertragen können. Der entscheidende "
        "Unterschied liegt in der kognitiven Verarbeitungstiefe. Oberflächliches Lesen "
        "aktiviert nur die phonologische Schleife — wir hören die Wörter innerlich. "
        "Tiefes Lesen aktiviert zusätzlich semantische Netzwerke, episodisches Gedächtnis "
        "und exekutive Funktionen. Je mehr Verarbeitungswege beteiligt sind, desto "
        "dauerhafter und abrufbarer wird die gespeicherte Information."
    ),
    "Entscheidungsfindung unter Unsicherheit": (
        "Schwer",
        "Menschen treffen täglich Tausende von Entscheidungen, die meisten davon unbewusst. "
        "Die Forschung von Daniel Kahneman und Amos Tversky hat gezeigt, dass unser "
        "Entscheidungsverhalten systematisch von rationalen Modellen abweicht. Ihr "
        "Zwei-Systeme-Modell unterscheidet zwischen System 1 — schnell, automatisch und "
        "intuitiv — und System 2 — langsam, bewusst und analytisch. System 1 nutzt "
        "Heuristiken, also mentale Abkürzungen, die in den meisten Situationen zu guten "
        "Ergebnissen führen, aber auch systematische Verzerrungen erzeugen können. Der "
        "Ankereffekt beispielsweise beschreibt unsere Tendenz, uns bei Schätzungen an "
        "einem zuerst genannten Wert zu orientieren, selbst wenn dieser willkürlich ist. "
        "Die Verfügbarkeitsheuristik lässt uns die Wahrscheinlichkeit von Ereignissen "
        "überschätzen, die uns leicht in den Sinn kommen — etwa Flugzeugabstürze "
        "gegenüber Autounfällen. Der Bestätigungsfehler führt dazu, dass wir bevorzugt "
        "Informationen suchen und wahrnehmen, die unsere bestehenden Überzeugungen "
        "bestätigen. Das Verständnis dieser kognitiven Verzerrungen ist der erste "
        "Schritt, um bessere Entscheidungen zu treffen. Wer seine eigenen Denkmuster "
        "kennt, kann bewusst System 2 aktivieren, wenn die Situation es erfordert."
    ),
    "Warum Lesen alles verändert": (
        "Leicht",
        "Lesen ist eine der wirkungsvollsten Gewohnheiten, die ein Mensch entwickeln kann. "
        "Anders als passiver Medienkonsum verlangt Lesen aktive Beteiligung des Gehirns. "
        "Sie konstruieren mentale Bilder, folgen Argumenten und bauen Verbindungen zwischen "
        "Ideen auf. Dieser Prozess stärkt neuronale Pfade und verbessert kognitive "
        "Funktionen auf eine Weise, die keine andere Aktivität replizieren kann. Studien "
        "zeigen durchgehend, dass regelmäßige Leser einen größeren Wortschatz, stärkere "
        "analytische Denkfähigkeiten und mehr Empathie besitzen. Das Lesen von Belletristik "
        "ermöglicht es, die Welt aus verschiedenen Perspektiven zu erleben und emotionale "
        "Intelligenz aufzubauen. Sachbücher akkumulieren Wissen über die Zeit. Jedes Buch "
        "fügt einem mentalen Rahmenwerk hinzu, das das Lernen des Nächsten erleichtert. "
        "Warren Buffett führt einen großen Teil seines Erfolgs darauf zurück, früh in "
        "seiner Karriere 500 Seiten am Tag gelesen zu haben. Sie verstehen etwas "
        "Grundlegendes: Lesen ist keine Freizeitbeschäftigung, sondern eine Investition. "
        "Die Rendite dieser Investition ist ein schärferer Verstand, bessere Entscheidungen "
        "und ein tieferes Verständnis der Welt."
    ),
}

TEXT_LIBRARY_FR = {
    "Les bases de la lecture rapide": (
        "Facile",
        "La lecture rapide est la capacité de lire des textes nettement plus vite que "
        "la moyenne sans perdre en compréhension. La plupart des gens lisent à une "
        "vitesse d'environ 200 à 250 mots par minute. Avec un entraînement ciblé, "
        "ce rythme peut être doublé, voire triplé. La clé réside dans la façon dont "
        "nos yeux et notre cerveau collaborent. Lors d'une lecture normale, les yeux "
        "se fixent sur chaque mot individuellement, parfois même plusieurs fois. Les "
        "lecteurs entraînés, en revanche, saisissent des groupes entiers de mots en "
        "une seule fixation. Ils utilisent le contexte et leurs connaissances préalables "
        "pour accéder au sens plus rapidement. Un autre facteur est la subvocalisation "
        "— cette habitude de prononcer intérieurement les mots pendant la lecture. "
        "Cette habitude limite la vitesse de lecture au rythme de la parole. Par "
        "l'entraînement, on peut apprendre à traiter les mots directement de manière "
        "visuelle, sans les prononcer intérieurement. Il est tout aussi important "
        "d'éviter les régressions — ces retours inconscients vers des passages déjà "
        "lus. Un pacer aide à maintenir le regard résolument vers l'avant. L'objectif "
        "n'est pas seulement la vitesse, mais un processus de lecture globalement "
        "plus efficace."
    ),
    "La science de la mémoire": (
        "Facile",
        "Notre mémoire n'est pas une fonction unique, mais un système complexe composé "
        "de plusieurs composantes. La mémoire sensorielle retient les impressions des "
        "sens pendant des fractions de seconde. La mémoire de travail — souvent appelée "
        "mémoire à court terme — peut traiter environ sept unités d'information "
        "simultanément et les conserver pendant 20 à 30 secondes. La mémoire à long "
        "terme stocke les informations de manière potentiellement illimitée. Le passage "
        "de la mémoire de travail à la mémoire à long terme réussit le mieux par la "
        "répétition, l'association émotionnelle et le traitement actif. Hermann "
        "Ebbinghaus a découvert dès 1885 la courbe de l'oubli : sans répétition, nous "
        "oublions environ 50 pour cent de ce que nous avons appris en une heure. La "
        "répétition espacée — apprendre à intervalles croissants — est la méthode la "
        "plus efficace connue contre cet oubli. Le sommeil joue également un rôle "
        "décisif. Pendant que nous dormons, le cerveau consolide les souvenirs et les "
        "transfère de l'hippocampe vers le néocortex. Celui qui dort suffisamment après "
        "avoir appris retient nettement plus que celui qui travaille toute la nuit."
    ),
    "Concentration et attention": (
        "Facile",
        "La concentration est la capacité de diriger consciemment son attention sur une "
        "tâche et de filtrer les distractions. Dans un monde de notifications constantes "
        "et de disponibilité permanente, cette capacité devient de plus en plus précieuse "
        "— et de plus en plus rare. Des études montrent que l'employé de bureau moyen "
        "est interrompu toutes les trois minutes et a besoin de jusqu'à 23 minutes pour "
        "retrouver un état de concentration profonde. Cet état, que le psychologue "
        "Mihaly Csikszentmihalyi appelle le flow, est la clé de la performance optimale. "
        "Dans le flow, action et conscience fusionnent, le temps semble s'arrêter et "
        "le travail paraît sans effort. Le flow survient lorsque l'exigence d'une tâche "
        "correspond exactement à nos compétences — ni trop facile, ni trop difficile. "
        "La concentration se travaille comme un muscle. Des exercices courts et réguliers "
        "sont plus efficaces que de rares sessions marathon. Seulement 15 à 20 minutes "
        "d'entraînement quotidien peuvent améliorer de manière mesurable la capacité "
        "d'attention."
    ),
    "Neuroplasticité et apprentissage": (
        "Moyen",
        "La neuroplasticité désigne la capacité du cerveau à se modifier structurellement "
        "et fonctionnellement par l'expérience et l'entraînement. Pendant longtemps, la "
        "science a cru que le cerveau était largement immuable après l'enfance. "
        "Aujourd'hui, nous savons que les réseaux neuronaux peuvent s'adapter tout au "
        "long de la vie. Lorsque nous apprenons une nouvelle compétence, de nouvelles "
        "connexions synaptiques se forment. Avec une répétition régulière, ces connexions "
        "se renforcent — un processus que le neuroscientifique Donald Hebb a résumé par "
        "le principe : les neurones qui s'activent ensemble se connectent ensemble. "
        "Inversement, les connexions non utilisées s'affaiblissent. Le cerveau n'est "
        "donc pas un organe statique, mais un système dynamique qui s'adapte constamment "
        "à ses exigences. Pour la lecture rapide, cela signifie que les compétences "
        "visuelles et cognitives qui permettent une lecture rapide peuvent être "
        "développées par un entraînement ciblé. L'élargissement du champ visuel, la "
        "réduction des régressions et l'accélération du traitement des mots ne sont "
        "pas des talents innés, mais des compétences entraînables. La régularité est "
        "déterminante : de courtes sessions quotidiennes sont plus efficaces que des "
        "sessions intensives occasionnelles."
    ),
    "La perception visuelle en lecture": (
        "Moyen",
        "Pendant la lecture, nos yeux ne se déplacent pas de manière uniforme sur le "
        "texte, mais par sauts rapides appelés saccades. Entre ces sauts, les yeux "
        "se fixent pendant environ 200 à 250 millisecondes sur un point — ce sont les "
        "fixations, pendant lesquelles l'absorption réelle d'information a lieu. "
        "L'empan perceptif s'étend sur environ 3 à 4 caractères à gauche et 14 à 15 "
        "caractères à droite de la fixation. Au centre du champ visuel, la fovéa, les "
        "lettres et les mots sont reconnus nettement. Dans la parafovéa — la zone "
        "directement adjacente — des informations préparatoires sur le mot suivant "
        "sont déjà recueillies : longueur du mot, premières lettres et parfois même "
        "le sens. Les lecteurs entraînés utilisent cette prévisualisation parafovéale "
        "de manière particulièrement efficace. Ils nécessitent moins de fixations par "
        "ligne et font des fixations plus courtes. Les régressions — retours vers des "
        "mots déjà lus — représentent jusqu'à 15 pour cent de tous les mouvements "
        "oculaires chez les lecteurs non entraînés. L'entraînement avec un pacer "
        "visuel peut réduire significativement ces régressions et augmenter durablement "
        "la vitesse de lecture."
    ),
    "Mémoire de travail et compréhension": (
        "Moyen",
        "La mémoire de travail est l'établi cognitif sur lequel nous maintenons et "
        "traitons temporairement les informations. Sa capacité est limitée — George "
        "Miller a décrit en 1956 le nombre magique 7 plus ou moins 2 comme empan "
        "typique. En lecture, la mémoire de travail joue un rôle central : elle "
        "maintient le début d'une phrase en conscience pendant que les yeux atteignent "
        "la fin. Elle relie les pronoms à leurs référents et intègre les nouvelles "
        "informations dans la compréhension existante du texte. La recherche montre "
        "une forte corrélation entre la capacité de mémoire de travail et la "
        "compréhension en lecture. Les personnes ayant une mémoire de travail plus "
        "grande comprennent mieux les textes complexes car elles peuvent maintenir "
        "plus de contexte simultanément. La bonne nouvelle : la mémoire de travail "
        "peut être entraînée. Les exercices de mémoire séquentielle, où des séquences "
        "de plus en plus longues de nombres ou de mots doivent être reproduites, "
        "élargissent la capacité de manière mesurable. Le chunking — le regroupement "
        "d'éléments individuels en groupes significatifs — est une autre stratégie "
        "efficace."
    ),
    "L'art de la lecture active": (
        "Difficile",
        "La lecture active se distingue fondamentalement de l'absorption passive de "
        "texte. Alors que les lecteurs passifs laissent leurs yeux glisser sur la page "
        "en espérant que les informations restent, les lecteurs actifs procèdent de "
        "manière stratégique. Ils posent des questions au texte avant de lire, "
        "survolent d'abord la structure et activent leurs connaissances préalables "
        "sur le sujet. Pendant la lecture, ils marquent les passages clés, formulent "
        "des résumés dans leurs propres mots et établissent des liens avec ce qu'ils "
        "connaissent déjà. Après la lecture, ils vérifient leur compréhension par "
        "l'auto-questionnement. Cette méthode, connue sous le nom de SQ3R (Survey, "
        "Question, Read, Recite, Review), a été développée en 1946 par Francis Robinson "
        "et reste l'une des stratégies de lecture les mieux étudiées. Les méta-analyses "
        "montrent que les lecteurs actifs retiennent non seulement plus, mais comprennent "
        "aussi le contenu plus profondément et le transfèrent mieux à de nouvelles "
        "situations. La différence décisive réside dans la profondeur du traitement "
        "cognitif. La lecture superficielle n'active que la boucle phonologique — nous "
        "entendons les mots intérieurement. La lecture profonde active en plus les "
        "réseaux sémantiques, la mémoire épisodique et les fonctions exécutives."
    ),
    "La prise de décision sous incertitude": (
        "Difficile",
        "Les êtres humains prennent des milliers de décisions chaque jour, la plupart "
        "inconsciemment. Les recherches de Daniel Kahneman et Amos Tversky ont montré "
        "que notre comportement décisionnel s'écarte systématiquement des modèles "
        "rationnels. Leur modèle à deux systèmes distingue le Système 1 — rapide, "
        "automatique et intuitif — du Système 2 — lent, conscient et analytique. "
        "Le Système 1 utilise des heuristiques, des raccourcis mentaux qui mènent à "
        "de bons résultats dans la plupart des situations, mais peuvent aussi produire "
        "des biais systématiques. L'effet d'ancrage, par exemple, décrit notre tendance "
        "à nous orienter vers une première valeur mentionnée lors d'estimations, même "
        "si cette valeur est arbitraire. L'heuristique de disponibilité nous fait "
        "surestimer la probabilité d'événements qui nous viennent facilement à l'esprit "
        "— comme les accidents d'avion par rapport aux accidents de voiture. Le biais "
        "de confirmation nous pousse à chercher et percevoir préférentiellement les "
        "informations qui confirment nos croyances existantes. Comprendre ces biais "
        "cognitifs est le premier pas vers de meilleures décisions."
    ),
    "Pourquoi la lecture change tout": (
        "Facile",
        "La lecture est l'une des habitudes les plus puissantes qu'une personne puisse "
        "développer. Contrairement à la consommation passive de médias, la lecture exige "
        "une participation active du cerveau. Vous construisez des images mentales, "
        "suivez des arguments et établissez des connexions entre les idées. Ce processus "
        "renforce les voies neuronales et améliore les fonctions cognitives d'une manière "
        "qu'aucune autre activité ne peut reproduire. Les études montrent de manière "
        "constante que les lecteurs réguliers possèdent un vocabulaire plus riche, des "
        "capacités de réflexion analytique plus fortes et davantage d'empathie. La "
        "lecture de fiction permet de vivre le monde depuis différentes perspectives et "
        "de développer l'intelligence émotionnelle. Les ouvrages documentaires accumulent "
        "le savoir au fil du temps. Chaque livre ajoute à un cadre mental qui facilite "
        "l'apprentissage du suivant. Warren Buffett attribue une grande partie de son "
        "succès au fait d'avoir lu 500 pages par jour au début de sa carrière. Ils "
        "comprennent quelque chose de fondamental : la lecture n'est pas un loisir, "
        "mais un investissement. Le rendement de cet investissement est un esprit plus "
        "affûté, de meilleures décisions et une compréhension plus profonde du monde."
    ),
}

TEXT_LIBRARY_ES = {
    "Fundamentos de la lectura rápida": (
        "Fácil",
        "La lectura rápida consiste en procesar textos a una velocidad considerablemente "
        "superior a la media sin sacrificar la comprensión. La mayoría de las personas "
        "leen entre 200 y 250 palabras por minuto. Con un entrenamiento adecuado, esa "
        "cifra puede duplicarse o incluso triplicarse. La clave está en la coordinación "
        "entre los ojos y el cerebro. Durante la lectura convencional, los ojos se "
        "detienen en cada palabra de forma individual, a veces más de una vez. Los "
        "lectores entrenados, en cambio, captan grupos enteros de palabras en una sola "
        "fijación. Utilizan el contexto y sus conocimientos previos para acceder al "
        "significado con mayor rapidez. Otro factor determinante es la subvocalización, "
        "esa costumbre de pronunciar mentalmente cada palabra mientras se lee. Este "
        "hábito limita la velocidad de lectura al ritmo del habla. Mediante la práctica, "
        "es posible aprender a procesar las palabras de forma puramente visual, sin "
        "necesidad de articularlas internamente. Igualmente importante es evitar las "
        "regresiones, esos retornos involuntarios a pasajes ya leídos. Un marcador de "
        "ritmo ayuda a mantener la mirada avanzando de forma constante. El objetivo no "
        "es solo la velocidad, sino un proceso de lectura globalmente más eficiente."
    ),
    "La ciencia de la memoria": (
        "Fácil",
        "La memoria no es una función única, sino un sistema complejo formado por varios "
        "componentes. La memoria sensorial retiene las impresiones de los sentidos durante "
        "fracciones de segundo. La memoria de trabajo, a menudo llamada memoria a corto "
        "plazo, puede manejar aproximadamente siete unidades de información de forma "
        "simultánea y conservarlas entre 20 y 30 segundos. La memoria a largo plazo, por "
        "su parte, almacena información de manera prácticamente ilimitada. La transferencia "
        "de datos de la memoria de trabajo a la memoria a largo plazo se produce mediante "
        "la repetición, la asociación emocional y la elaboración activa. Las técnicas "
        "mnemotécnicas aprovechan estos mecanismos creando vínculos artificiales entre la "
        "información nueva y los conocimientos ya almacenados. El palacio de la memoria, "
        "por ejemplo, asocia datos con ubicaciones espaciales conocidas. La repetición "
        "espaciada distribuye las sesiones de repaso a intervalos crecientes, lo que "
        "fortalece las conexiones neuronales de forma más eficaz que el estudio intensivo "
        "concentrado en una sola sesión."
    ),
    "Concentración y enfoque": (
        "Fácil",
        "La capacidad de concentración es un recurso limitado que se agota con el uso "
        "continuado. Investigaciones en neurociencia han demostrado que la atención "
        "sostenida depende de la corteza prefrontal, una región del cerebro que consume "
        "grandes cantidades de glucosa y oxígeno. Cuando esta zona se fatiga, la "
        "concentración disminuye y aumenta la susceptibilidad a las distracciones. La "
        "técnica Pomodoro, que alterna bloques de trabajo de 25 minutos con pausas breves, "
        "se basa en este principio. Las pausas permiten que la corteza prefrontal se "
        "recupere. El entorno también desempeña un papel fundamental. Cada notificación, "
        "cada interrupción, obliga al cerebro a realizar un costoso cambio de contexto. "
        "Estudios muestran que tras una interrupción se necesitan hasta 23 minutos para "
        "recuperar el nivel de concentración anterior. Por eso, crear un entorno libre de "
        "distracciones es tan importante como entrenar la propia capacidad de enfoque. "
        "La meditación y los ejercicios de atención plena fortalecen las redes neuronales "
        "responsables del control atencional."
    ),
    "Neuroplasticidad y aprendizaje": (
        "Medio",
        "El cerebro humano no es una estructura fija, sino un órgano extraordinariamente "
        "adaptable que se reorganiza constantemente en respuesta a la experiencia. Este "
        "fenómeno, conocido como neuroplasticidad, constituye la base biológica del "
        "aprendizaje. Cada vez que adquirimos una nueva habilidad o un nuevo conocimiento, "
        "se forman nuevas conexiones sinápticas o se refuerzan las existentes. La "
        "repetición consolida estas conexiones, haciendo que los circuitos neuronales "
        "implicados se activen con mayor facilidad y rapidez. Este proceso explica por "
        "qué la práctica deliberada es tan eficaz. No se trata simplemente de repetir "
        "una tarea, sino de hacerlo con atención consciente, retroalimentación inmediata "
        "y un nivel de dificultad progresivamente creciente. La neuroplasticidad también "
        "explica por qué los hábitos son tan poderosos. Las conductas repetidas crean "
        "caminos neuronales que se automatizan con el tiempo, liberando recursos "
        "cognitivos para tareas más complejas. El entrenamiento de lectura rápida "
        "aprovecha directamente estos mecanismos, transformando procesos que inicialmente "
        "requieren esfuerzo consciente en habilidades automáticas."
    ),
    "Percepción visual en la lectura": (
        "Medio",
        "El proceso de lectura implica una interacción compleja entre la percepción "
        "visual, la atención y los procesos cognitivos superiores. Cuando un lector fija "
        "la mirada en una palabra, el sistema visual extrae información de una región "
        "denominada campo perceptivo, que se extiende aproximadamente 3 o 4 caracteres "
        "a la izquierda y 14 o 15 caracteres a la derecha del punto de fijación. Dentro "
        "de este campo, la identificación detallada de letras y palabras ocurre en la "
        "región foveal, que abarca unos 2 grados de ángulo visual. El procesamiento "
        "parafoveal proporciona información preliminar sobre las palabras siguientes, "
        "incluyendo su longitud, las letras iniciales y, en ocasiones, información "
        "fonológica o semántica parcial. Los movimientos sacádicos, que abarcan "
        "típicamente entre 7 y 9 caracteres, sirven para llevar nuevo texto a la visión "
        "foveal. La duración de las fijaciones, que promedia entre 200 y 250 milisegundos, "
        "refleja el tiempo necesario para el acceso léxico y la integración de la palabra "
        "fijada en la representación continua de la oración."
    ),
    "Memoria de trabajo y comprensión lectora": (
        "Medio",
        "La memoria de trabajo es el sistema cognitivo que mantiene y manipula información "
        "de forma temporal mientras realizamos tareas complejas como la lectura. Su "
        "capacidad es limitada, generalmente a entre cuatro y siete elementos simultáneos, "
        "lo que tiene implicaciones directas para la comprensión de textos. Cuando leemos "
        "una oración larga, la memoria de trabajo debe retener las primeras palabras "
        "mientras procesa las siguientes, construyendo progresivamente el significado "
        "global. Si la carga excede su capacidad, la comprensión se deteriora. Los "
        "lectores expertos desarrollan estrategias para gestionar esta limitación. La "
        "agrupación semántica, por ejemplo, permite condensar múltiples elementos en "
        "unidades significativas más amplias. La automatización del reconocimiento de "
        "palabras libera recursos de la memoria de trabajo para dedicarlos a la "
        "comprensión. Por eso, el vocabulario amplio y la fluidez lectora son predictores "
        "tan fiables de la comprensión. Cuanto menos esfuerzo se dedica a decodificar "
        "palabras individuales, más recursos quedan disponibles para integrar ideas, "
        "hacer inferencias y construir una representación coherente del texto."
    ),
    "El arte de la lectura activa": (
        "Difícil",
        "La lectura activa se distingue de la lectura pasiva por el grado de implicación "
        "cognitiva del lector. Mientras que el lector pasivo recorre el texto de forma "
        "lineal, absorbiendo información sin cuestionarla, el lector activo mantiene un "
        "diálogo constante con el material. Formula preguntas antes de comenzar cada "
        "sección, genera predicciones sobre el contenido, evalúa la solidez de los "
        "argumentos y conecta las ideas nuevas con sus conocimientos previos. Esta "
        "aproximación transforma la lectura de un acto receptivo en un proceso "
        "constructivo. Las investigaciones en psicología educativa demuestran que la "
        "lectura activa mejora significativamente tanto la comprensión como la retención "
        "a largo plazo. Técnicas como el subrayado selectivo, la anotación marginal y "
        "la elaboración de resúmenes obligan al cerebro a procesar la información a un "
        "nivel más profundo. El método SQ3R — explorar, preguntar, leer, recitar y "
        "revisar — sistematiza este enfoque. Cada paso añade una capa adicional de "
        "procesamiento que fortalece la huella mnémica. La paradoja es que la lectura "
        "activa, aunque inicialmente más lenta, produce un aprendizaje más eficiente "
        "porque reduce la necesidad de releer."
    ),
    "Toma de decisiones bajo incertidumbre": (
        "Difícil",
        "La teoría del proceso dual postula que la cognición humana opera a través de "
        "dos sistemas fundamentalmente distintos. El Sistema 1 se caracteriza por un "
        "procesamiento automático, rápido y sin esfuerzo que opera por debajo del umbral "
        "de la conciencia. Se basa en heurísticas, memoria asociativa y reconocimiento "
        "de patrones para generar juicios y decisiones rápidas. El Sistema 2, por el "
        "contrario, es deliberado, lento y exigente, requiere atención consciente y "
        "recursos de la memoria de trabajo. Se activa cuando nos enfrentamos a situaciones "
        "novedosas, realizamos cálculos complejos o necesitamos anular las respuestas "
        "automáticas del Sistema 1. La investigación de Kahneman y Tversky demostró que "
        "el procesamiento del Sistema 1, aunque generalmente adaptativo, puede conducir "
        "a sesgos sistemáticos y errores de juicio. Entre estos sesgos cognitivos se "
        "encuentran el anclaje, la heurística de disponibilidad, la representatividad y "
        "los efectos de encuadre. Comprender cuándo y cómo se activa cada sistema "
        "permite diseñar intervenciones que mejoren la toma de decisiones."
    ),
    "Por qué la lectura lo cambia todo": (
        "Fácil",
        "La lectura es uno de los hábitos más transformadores que una persona puede "
        "desarrollar. A diferencia del consumo pasivo de medios, leer exige una "
        "participación activa del cerebro. Se construyen imágenes mentales, se siguen "
        "argumentos y se establecen conexiones entre ideas. Este proceso fortalece las "
        "vías neuronales y mejora la función cognitiva de maneras que ninguna otra "
        "actividad puede replicar. Los estudios demuestran consistentemente que los "
        "lectores habituales poseen vocabularios más amplios, habilidades analíticas más "
        "sólidas y mayor empatía. La lectura de ficción, en particular, permite "
        "experimentar el mundo desde perspectivas diferentes, construyendo una "
        "inteligencia emocional que se transfiere directamente a las relaciones de la "
        "vida real. La lectura de no ficción acumula conocimiento con el tiempo. Cada "
        "libro leído añade un marco mental que facilita el aprendizaje del siguiente. "
        "Warren Buffett atribuye gran parte de su éxito a leer 500 páginas al día al "
        "inicio de su carrera. Bill Gates lee unos 50 libros al año. Ambos comprenden "
        "algo fundamental: la lectura no es un lujo, es una inversión cuyo rendimiento "
        "es una mente más aguda y una comprensión más profunda del mundo."
    ),
}

TEXT_LIBRARY_IT = {
    "Fondamenti della lettura veloce": (
        "Facile",
        "La lettura veloce consiste nell'elaborare testi a una velocità considerevolmente "
        "superiore alla media senza sacrificare la comprensione. La maggior parte delle persone "
        "legge tra le 200 e le 250 parole al minuto. Con un allenamento mirato, questa cifra "
        "può essere raddoppiata o addirittura triplicata. La chiave sta nella coordinazione "
        "tra occhi e cervello. Durante la lettura convenzionale, gli occhi si fermano su ogni "
        "parola singolarmente, a volte più di una volta. I lettori allenati, invece, colgono "
        "interi gruppi di parole in una singola fissazione. Utilizzano il contesto e le "
        "conoscenze pregresse per accedere al significato con maggiore rapidità. Un altro "
        "fattore determinante è la subvocalizzazione, quell'abitudine di pronunciare "
        "mentalmente ogni parola durante la lettura. Questa abitudine limita la velocità di "
        "lettura al ritmo del parlato. Attraverso la pratica, è possibile imparare a elaborare "
        "le parole in modo puramente visivo, senza bisogno di articolarle internamente. "
        "Altrettanto importante è evitare le regressioni, quei ritorni involontari a passaggi "
        "già letti. Un marcatore di ritmo aiuta a mantenere lo sguardo in costante avanzamento."
    ),
    "La scienza della memoria": (
        "Facile",
        "La memoria non è una funzione unica, ma un sistema complesso formato da diverse "
        "componenti. La memoria sensoriale trattiene le impressioni dei sensi per frazioni di "
        "secondo. La memoria di lavoro, spesso chiamata memoria a breve termine, può gestire "
        "circa sette unità di informazione simultaneamente e conservarle per 20-30 secondi. "
        "La memoria a lungo termine, invece, immagazzina informazioni in modo praticamente "
        "illimitato. Il trasferimento dei dati dalla memoria di lavoro a quella a lungo termine "
        "avviene attraverso la ripetizione, l'associazione emotiva e l'elaborazione attiva. Le "
        "tecniche mnemoniche sfruttano questi meccanismi creando collegamenti artificiali tra "
        "le nuove informazioni e le conoscenze già archiviate. Il palazzo della memoria, ad "
        "esempio, associa i dati a luoghi spaziali conosciuti. La ripetizione spaziata "
        "distribuisce le sessioni di ripasso a intervalli crescenti, rafforzando le connessioni "
        "neurali in modo più efficace rispetto allo studio intensivo concentrato in un'unica "
        "sessione."
    ),
    "Concentrazione e attenzione": (
        "Facile",
        "La capacità di concentrazione è una risorsa limitata che si esaurisce con l'uso "
        "prolungato. Le ricerche in neuroscienze hanno dimostrato che l'attenzione sostenuta "
        "dipende dalla corteccia prefrontale, una regione del cervello che consuma grandi "
        "quantità di glucosio e ossigeno. Quando questa zona si affatica, la concentrazione "
        "diminuisce e aumenta la suscettibilità alle distrazioni. La tecnica del Pomodoro, "
        "che alterna blocchi di lavoro di 25 minuti con pause brevi, si basa su questo "
        "principio. Le pause permettono alla corteccia prefrontale di recuperare. Anche "
        "l'ambiente gioca un ruolo fondamentale. Ogni notifica, ogni interruzione, costringe "
        "il cervello a effettuare un costoso cambio di contesto. Gli studi mostrano che dopo "
        "un'interruzione servono fino a 23 minuti per recuperare il livello di concentrazione "
        "precedente. Per questo, creare un ambiente privo di distrazioni è tanto importante "
        "quanto allenare la propria capacità di focalizzazione."
    ),
    "Neuroplasticità e apprendimento": (
        "Medio",
        "Il cervello umano non è una struttura fissa, ma un organo straordinariamente "
        "adattabile che si riorganizza costantemente in risposta all'esperienza. Questo "
        "fenomeno, noto come neuroplasticità, costituisce la base biologica dell'apprendimento. "
        "Ogni volta che acquisiamo una nuova abilità o una nuova conoscenza, si formano nuove "
        "connessioni sinaptiche o si rafforzano quelle esistenti. La ripetizione consolida "
        "queste connessioni, facendo sì che i circuiti neurali coinvolti si attivino con "
        "maggiore facilità e rapidità. Questo processo spiega perché la pratica deliberata è "
        "così efficace. Non si tratta semplicemente di ripetere un compito, ma di farlo con "
        "attenzione consapevole, feedback immediato e un livello di difficoltà progressivamente "
        "crescente. La neuroplasticità spiega anche perché le abitudini sono così potenti. I "
        "comportamenti ripetuti creano percorsi neurali che si automatizzano nel tempo, "
        "liberando risorse cognitive per compiti più complessi."
    ),
    "Percezione visiva nella lettura": (
        "Medio",
        "Il processo di lettura implica un'interazione complessa tra percezione visiva, "
        "attenzione e processi cognitivi superiori. Quando un lettore fissa lo sguardo su una "
        "parola, il sistema visivo estrae informazioni da una regione denominata campo "
        "percettivo, che si estende per circa 3-4 caratteri a sinistra e 14-15 caratteri a "
        "destra del punto di fissazione. All'interno di questo campo, l'identificazione "
        "dettagliata di lettere e parole avviene nella regione foveale, che sottende circa 2 "
        "gradi di angolo visivo. L'elaborazione parafoveale fornisce informazioni preliminari "
        "sulle parole successive, inclusa la loro lunghezza, le lettere iniziali e talvolta "
        "informazioni fonologiche o semantiche parziali. I movimenti saccadici, che coprono "
        "tipicamente 7-9 caratteri, servono a portare nuovo testo nella visione foveale. La "
        "durata delle fissazioni, che in media è di 200-250 millisecondi, riflette il tempo "
        "necessario per l'accesso lessicale."
    ),
    "Memoria di lavoro e comprensione": (
        "Medio",
        "La memoria di lavoro è il sistema cognitivo che mantiene e manipola informazioni in "
        "modo temporaneo mentre svolgiamo compiti complessi come la lettura. La sua capacità è "
        "limitata, generalmente a quattro-sette elementi simultanei, il che ha implicazioni "
        "dirette per la comprensione dei testi. Quando leggiamo una frase lunga, la memoria di "
        "lavoro deve trattenere le prime parole mentre elabora le successive, costruendo "
        "progressivamente il significato globale. Se il carico supera la sua capacità, la "
        "comprensione si deteriora. I lettori esperti sviluppano strategie per gestire questa "
        "limitazione. Il raggruppamento semantico, ad esempio, permette di condensare più "
        "elementi in unità significative più ampie. L'automatizzazione del riconoscimento delle "
        "parole libera risorse della memoria di lavoro da dedicare alla comprensione. Per "
        "questo, un vocabolario ampio e la fluidità nella lettura sono predittori così "
        "affidabili della comprensione."
    ),
    "L'arte della lettura attiva": (
        "Difficile",
        "La lettura attiva si distingue dalla lettura passiva per il grado di coinvolgimento "
        "cognitivo del lettore. Mentre il lettore passivo percorre il testo in modo lineare, "
        "assorbendo informazioni senza metterle in discussione, il lettore attivo mantiene un "
        "dialogo costante con il materiale. Formula domande prima di iniziare ogni sezione, "
        "genera previsioni sul contenuto, valuta la solidità degli argomenti e collega le nuove "
        "idee alle conoscenze pregresse. Questo approccio trasforma la lettura da un atto "
        "ricettivo in un processo costruttivo. Le ricerche in psicologia dell'educazione "
        "dimostrano che la lettura attiva migliora significativamente sia la comprensione che "
        "la ritenzione a lungo termine. Tecniche come la sottolineatura selettiva, le "
        "annotazioni a margine e l'elaborazione di riassunti costringono il cervello a "
        "elaborare le informazioni a un livello più profondo. Il paradosso è che la lettura "
        "attiva, sebbene inizialmente più lenta, produce un apprendimento più efficiente."
    ),
    "Processo decisionale sotto incertezza": (
        "Difficile",
        "La teoria del processo duale postula che la cognizione umana opera attraverso due "
        "sistemi fondamentalmente distinti. Il Sistema 1 si caratterizza per un'elaborazione "
        "automatica, rapida e senza sforzo che opera al di sotto della soglia della coscienza. "
        "Si basa su euristiche, memoria associativa e riconoscimento di pattern per generare "
        "giudizi e decisioni rapide. Il Sistema 2, al contrario, è deliberato, lento e "
        "impegnativo, richiede attenzione consapevole e risorse della memoria di lavoro. Si "
        "attiva quando ci troviamo di fronte a situazioni nuove, eseguiamo calcoli complessi o "
        "dobbiamo annullare le risposte automatiche del Sistema 1. La ricerca di Kahneman e "
        "Tversky ha dimostrato che l'elaborazione del Sistema 1, sebbene generalmente "
        "adattativa, può portare a bias sistematici ed errori di giudizio. Tra questi bias "
        "cognitivi troviamo l'ancoraggio, l'euristica della disponibilità, la "
        "rappresentatività e gli effetti di framing."
    ),
    "Perché la lettura cambia tutto": (
        "Facile",
        "La lettura è una delle abitudini più trasformative che una persona possa sviluppare. "
        "A differenza del consumo passivo di media, leggere richiede una partecipazione attiva "
        "del cervello. Si costruiscono immagini mentali, si seguono argomentazioni e si "
        "stabiliscono connessioni tra idee. Questo processo rafforza le vie neurali e migliora "
        "la funzione cognitiva in modi che nessun'altra attività può replicare. Gli studi "
        "dimostrano costantemente che i lettori abituali possiedono vocabolari più ampi, "
        "capacità analitiche più solide e maggiore empatia. La lettura di narrativa, in "
        "particolare, permette di sperimentare il mondo da prospettive diverse, costruendo "
        "un'intelligenza emotiva che si trasferisce direttamente alle relazioni della vita "
        "reale. La lettura di saggistica accumula conoscenza nel tempo. Ogni libro letto "
        "aggiunge un quadro mentale che facilita l'apprendimento successivo. Warren Buffett "
        "attribuisce gran parte del suo successo alla lettura di 500 pagine al giorno "
        "all'inizio della sua carriera. Entrambi comprendono qualcosa di fondamentale: la "
        "lettura non è un lusso, è un investimento."
    ),
}

TEXT_LIBRARY_PT = {
    "Fundamentos da leitura rápida": (
        "Fácil",
        "A leitura rápida consiste em processar textos a uma velocidade consideravelmente "
        "superior à média sem sacrificar a compreensão. A maioria das pessoas lê entre 200 "
        "e 250 palavras por minuto. Com treino adequado, esse número pode ser duplicado ou "
        "até triplicado. A chave está na coordenação entre os olhos e o cérebro. Durante a "
        "leitura convencional, os olhos fixam-se em cada palavra individualmente, por vezes "
        "mais do que uma vez. Os leitores treinados, pelo contrário, captam grupos inteiros "
        "de palavras numa única fixação. Utilizam o contexto e os conhecimentos prévios para "
        "aceder ao significado com maior rapidez. Outro fator determinante é a subvocalização, "
        "o hábito de pronunciar mentalmente cada palavra durante a leitura. Este hábito limita "
        "a velocidade de leitura ao ritmo da fala. Através da prática, é possível aprender a "
        "processar as palavras de forma puramente visual, sem necessidade de as articular "
        "internamente. Igualmente importante é evitar as regressões, esses retornos "
        "involuntários a passagens já lidas. Um marcador de ritmo ajuda a manter o olhar "
        "em avanço constante."
    ),
    "A ciência da memória": (
        "Fácil",
        "A memória não é uma função única, mas um sistema complexo formado por várias "
        "componentes. A memória sensorial retém as impressões dos sentidos durante frações "
        "de segundo. A memória de trabalho, frequentemente chamada memória de curto prazo, "
        "pode gerir aproximadamente sete unidades de informação em simultâneo e conservá-las "
        "durante 20 a 30 segundos. A memória de longo prazo, por sua vez, armazena informação "
        "de forma praticamente ilimitada. A transferência de dados da memória de trabalho para "
        "a memória de longo prazo ocorre através da repetição, da associação emocional e da "
        "elaboração ativa. As técnicas mnemónicas aproveitam estes mecanismos criando ligações "
        "artificiais entre a informação nova e os conhecimentos já armazenados. O palácio da "
        "memória, por exemplo, associa dados a localizações espaciais conhecidas. A repetição "
        "espaçada distribui as sessões de revisão a intervalos crescentes, fortalecendo as "
        "conexões neurais de forma mais eficaz do que o estudo intensivo concentrado numa "
        "única sessão."
    ),
    "Concentração e foco": (
        "Fácil",
        "A capacidade de concentração é um recurso limitado que se esgota com o uso continuado. "
        "Investigações em neurociência demonstraram que a atenção sustentada depende do córtex "
        "pré-frontal, uma região do cérebro que consome grandes quantidades de glucose e "
        "oxigénio. Quando esta zona se fatiga, a concentração diminui e aumenta a "
        "suscetibilidade às distrações. A técnica Pomodoro, que alterna blocos de trabalho de "
        "25 minutos com pausas breves, baseia-se neste princípio. As pausas permitem que o "
        "córtex pré-frontal recupere. O ambiente também desempenha um papel fundamental. Cada "
        "notificação, cada interrupção, obriga o cérebro a realizar uma custosa mudança de "
        "contexto. Estudos mostram que após uma interrupção são necessários até 23 minutos "
        "para recuperar o nível de concentração anterior. Por isso, criar um ambiente livre "
        "de distrações é tão importante como treinar a própria capacidade de foco. A meditação "
        "e os exercícios de atenção plena fortalecem as redes neurais responsáveis pelo "
        "controlo atencional."
    ),
    "Neuroplasticidade e aprendizagem": (
        "Médio",
        "O cérebro humano não é uma estrutura fixa, mas um órgão extraordinariamente adaptável "
        "que se reorganiza constantemente em resposta à experiência. Este fenómeno, conhecido "
        "como neuroplasticidade, constitui a base biológica da aprendizagem. Cada vez que "
        "adquirimos uma nova competência ou um novo conhecimento, formam-se novas conexões "
        "sinápticas ou reforçam-se as existentes. A repetição consolida estas conexões, "
        "fazendo com que os circuitos neurais envolvidos se ativem com maior facilidade e "
        "rapidez. Este processo explica por que a prática deliberada é tão eficaz. Não se "
        "trata simplesmente de repetir uma tarefa, mas de o fazer com atenção consciente, "
        "feedback imediato e um nível de dificuldade progressivamente crescente. A "
        "neuroplasticidade também explica por que os hábitos são tão poderosos. Os "
        "comportamentos repetidos criam caminhos neurais que se automatizam com o tempo, "
        "libertando recursos cognitivos para tarefas mais complexas."
    ),
    "Perceção visual na leitura": (
        "Médio",
        "O processo de leitura implica uma interação complexa entre a perceção visual, a "
        "atenção e os processos cognitivos superiores. Quando um leitor fixa o olhar numa "
        "palavra, o sistema visual extrai informação de uma região denominada campo percetivo, "
        "que se estende por aproximadamente 3 a 4 caracteres à esquerda e 14 a 15 caracteres "
        "à direita do ponto de fixação. Dentro deste campo, a identificação detalhada de "
        "letras e palavras ocorre na região foveal, que subentende cerca de 2 graus de ângulo "
        "visual. O processamento parafoveal fornece informação preliminar sobre as palavras "
        "seguintes, incluindo o seu comprimento, as letras iniciais e, por vezes, informação "
        "fonológica ou semântica parcial. Os movimentos sacádicos, que abrangem tipicamente "
        "7 a 9 caracteres, servem para trazer novo texto para a visão foveal. A duração das "
        "fixações, que em média é de 200 a 250 milissegundos, reflete o tempo necessário para "
        "o acesso lexical e a integração da palavra na representação contínua da frase."
    ),
    "Memória de trabalho e compreensão leitora": (
        "Médio",
        "A memória de trabalho é o sistema cognitivo que mantém e manipula informação de forma "
        "temporária enquanto realizamos tarefas complexas como a leitura. A sua capacidade é "
        "limitada, geralmente a quatro a sete elementos simultâneos, o que tem implicações "
        "diretas para a compreensão de textos. Quando lemos uma frase longa, a memória de "
        "trabalho deve reter as primeiras palavras enquanto processa as seguintes, construindo "
        "progressivamente o significado global. Se a carga exceder a sua capacidade, a "
        "compreensão deteriora-se. Os leitores experientes desenvolvem estratégias para gerir "
        "esta limitação. O agrupamento semântico, por exemplo, permite condensar múltiplos "
        "elementos em unidades significativas mais amplas. A automatização do reconhecimento "
        "de palavras liberta recursos da memória de trabalho para dedicar à compreensão. Por "
        "isso, o vocabulário amplo e a fluência leitora são preditores tão fiáveis da "
        "compreensão."
    ),
    "A arte da leitura ativa": (
        "Difícil",
        "A leitura ativa distingue-se da leitura passiva pelo grau de envolvimento cognitivo "
        "do leitor. Enquanto o leitor passivo percorre o texto de forma linear, absorvendo "
        "informação sem a questionar, o leitor ativo mantém um diálogo constante com o "
        "material. Formula perguntas antes de começar cada secção, gera previsões sobre o "
        "conteúdo, avalia a solidez dos argumentos e liga as novas ideias aos conhecimentos "
        "prévios. Esta abordagem transforma a leitura de um ato recetivo num processo "
        "construtivo. As investigações em psicologia educacional demonstram que a leitura "
        "ativa melhora significativamente tanto a compreensão como a retenção a longo prazo. "
        "Técnicas como o sublinhado seletivo, a anotação marginal e a elaboração de resumos "
        "obrigam o cérebro a processar a informação a um nível mais profundo. O método SQ3R "
        "— explorar, perguntar, ler, recitar e rever — sistematiza esta abordagem. O paradoxo "
        "é que a leitura ativa, embora inicialmente mais lenta, produz uma aprendizagem mais "
        "eficiente porque reduz a necessidade de reler."
    ),
    "Tomada de decisão sob incerteza": (
        "Difícil",
        "A teoria do processo dual postula que a cognição humana opera através de dois sistemas "
        "fundamentalmente distintos. O Sistema 1 caracteriza-se por um processamento automático, "
        "rápido e sem esforço que opera abaixo do limiar da consciência. Baseia-se em "
        "heurísticas, memória associativa e reconhecimento de padrões para gerar juízos e "
        "decisões rápidas. O Sistema 2, pelo contrário, é deliberado, lento e exigente, "
        "requerendo atenção consciente e recursos da memória de trabalho. Ativa-se quando nos "
        "deparamos com situações novas, realizamos cálculos complexos ou precisamos de anular "
        "as respostas automáticas do Sistema 1. A investigação de Kahneman e Tversky demonstrou "
        "que o processamento do Sistema 1, embora geralmente adaptativo, pode conduzir a vieses "
        "sistemáticos e erros de julgamento. Entre estes vieses cognitivos encontram-se a "
        "ancoragem, a heurística da disponibilidade, a representatividade e os efeitos de "
        "enquadramento."
    ),
    "Porque é que a leitura muda tudo": (
        "Fácil",
        "A leitura é um dos hábitos mais transformadores que uma pessoa pode desenvolver. Ao "
        "contrário do consumo passivo de media, ler exige uma participação ativa do cérebro. "
        "Constroem-se imagens mentais, seguem-se argumentos e estabelecem-se conexões entre "
        "ideias. Este processo fortalece as vias neurais e melhora a função cognitiva de "
        "formas que nenhuma outra atividade pode replicar. Os estudos demonstram "
        "consistentemente que os leitores habituais possuem vocabulários mais amplos, "
        "capacidades analíticas mais sólidas e maior empatia. A leitura de ficção, em "
        "particular, permite experimentar o mundo a partir de perspetivas diferentes, "
        "construindo uma inteligência emocional que se transfere diretamente para as relações "
        "da vida real. A leitura de não-ficção acumula conhecimento ao longo do tempo. Cada "
        "livro lido acrescenta um quadro mental que facilita a aprendizagem seguinte. Warren "
        "Buffett atribui grande parte do seu sucesso à leitura de 500 páginas por dia no "
        "início da sua carreira. Ambos compreendem algo fundamental: a leitura não é um luxo, "
        "é um investimento cujo retorno é uma mente mais afiada e uma compreensão mais "
        "profunda do mundo."
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
            ("eyespan", "Eye-Span: Vertical 40%", {"mode": "v", "width": 40, "low": 2, "high": 2, "rounds": 10}),
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
            ("eyespan", "Eye-Span: Vertical 40%", {"mode": "v", "width": 40, "low": 2, "high": 2, "rounds": 10}),
            ("peripheral_flash", "Peripheral Flash: Challenge", {}),
            ("eyespan", "Eye-Span: Horizontal 50%", {"mode": "h", "width": 50, "low": 2, "high": 3, "rounds": 12}),
            ("eyespan", "Eye-Span: Vertical 50%", {"mode": "v", "width": 50, "low": 2, "high": 3, "rounds": 10}),
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

    # ── Cognitive Performance (additional) ──
    "processing_speed": {
        "name": "Processing Speed",
        "category": "cognitive",
        "description": "Push raw mental speed — fast reactions, rapid decisions, quick digit recall",
        "steps": [
            ("reaction_time", "Reaction Time: Simple Warmup", {"mode": "simple"}),
            ("flash", "Flash: 4 Digits", {"digits": 4, "rounds": 12}),
            ("rapid_decision", "Rapid Decision Grid", {}),
            ("reaction_time", "Reaction Time: Choice", {"mode": "choice"}),
            ("flash", "Flash: 5-6 Digits", {"low": 5, "high": 6, "rounds": 12}),
            ("rapid_decision", "Rapid Decision Grid: Challenge", {}),
            ("reaction_time", "Reaction Time: Go/No-Go", {"mode": "go_nogo"}),
            ("flash", "Flash: 6-7 Digits", {"low": 6, "high": 7, "rounds": 15}),
        ],
    },
    "executive_function": {
        "name": "Executive Function",
        "category": "cognitive",
        "description": "Train inhibition, task switching, and cognitive control",
        "steps": [
            ("reaction_time", "Reaction Time: Go/No-Go Warmup", {"mode": "go_nogo"}),
            ("split_attention", "Split Attention: Sequential", {"mode": "sequential"}),
            ("sequence_memory", "Sequence Memory", {}),
            ("split_attention", "Split Attention: Simultaneous", {"mode": "simultaneous"}),
            ("reaction_time", "Reaction Time: Choice", {"mode": "choice"}),
            ("rapid_decision", "Rapid Decision Grid", {}),
            ("split_attention", "Split Attention: Rapid", {"mode": "rapid"}),
            ("sequence_memory", "Sequence Memory: Extended", {}),
            ("reaction_time", "Reaction Time: Go/No-Go Final", {"mode": "go_nogo"}),
        ],
    },
    "deep_focus": {
        "name": "Deep Focus",
        "category": "cognitive",
        "description": "Build sustained concentration through extended exercises",
        "steps": [
            ("priming", "Eye Priming: Slow Horizontal", {"mode": "saccade_h", "delay": 700, "duration_s": 60}),
            ("schulte", "Schulte Grid: 5×5", {"grid_size": 5}),
            ("mot", "MOT: 4 Targets · 10s", {"targets": 4, "duration": 10}),
            ("split_attention", "Split Attention: 25 Rounds", {"mode": "simultaneous", "rounds": 25}),
            ("schulte", "Schulte Grid: 6×6", {"grid_size": 6}),
            ("mot", "MOT: 5 Targets · 10s", {"targets": 5, "duration": 10}),
            ("recall", "Recall: Mixed (10 items)", {"mode": "mixed", "count": 10}),
            ("schulte", "Schulte Grid: 7×7", {"grid_size": 7}),
        ],
    },

    # ── Visual Processing (additional) ──
    "speed_perception": {
        "name": "Speed Perception",
        "category": "visual",
        "description": "Maximize visual intake speed — fast flashes, tight spans, rapid slides",
        "steps": [
            ("priming", "Eye Priming: Fast Horizontal", {"mode": "saccade_h", "delay": 400}),
            ("flash", "Flash: 5 Digits", {"digits": 5, "rounds": 12}),
            ("eyespan", "Eye-Span: Horizontal 30%", {"mode": "h", "width": 30, "low": 2, "high": 2, "rounds": 10}),
            ("flash", "Flash: 6-7 Digits", {"low": 6, "high": 7, "rounds": 15}),
            ("eyespan", "Eye-Span: Vertical 40%", {"mode": "v", "width": 40, "low": 2, "high": 3, "rounds": 10}),
            ("slide_processing", "Slides: 6s · Mixed", {"display_s": 6, "slides": 5}),
            ("flash", "Flash: 7-8 Digits", {"low": 7, "high": 8, "rounds": 15}),
            ("eyespan", "Eye-Span: Mixed 50%", {"mode": "m", "width": 50, "low": 3, "high": 3, "rounds": 12}),
            ("slide_processing", "Slides: 4s · Mixed", {"display_s": 4, "slides": 5}),
        ],
    },
    "wide_field": {
        "name": "Wide-Field Training",
        "category": "visual",
        "description": "Expand peripheral awareness and useful field of view",
        "steps": [
            ("priming", "Eye Priming: Expanding Saccades", {"mode": "saccade_expand", "delay": 500}),
            ("eyespan", "Eye-Span: Horizontal 40%", {"mode": "h", "width": 40, "low": 2, "high": 2, "rounds": 10}),
            ("peripheral_flash", "Peripheral Flash: Warmup", {}),
            ("eyespan", "Eye-Span: Vertical 50%", {"mode": "v", "width": 50, "low": 2, "high": 3, "rounds": 10}),
            ("mot", "MOT: 4 Targets · 8s", {"targets": 4, "duration": 8}),
            ("eyespan", "Eye-Span: Horizontal 60%", {"mode": "h", "width": 60, "low": 3, "high": 3, "rounds": 12}),
            ("peripheral_flash", "Peripheral Flash: Challenge", {}),
            ("priming", "Eye Priming: Fast Diagonal", {"mode": "saccade_diag", "delay": 400}),
            ("eyespan", "Eye-Span: Vertical 60%", {"mode": "v", "width": 60, "low": 3, "high": 4, "rounds": 12}),
            ("eyespan", "Eye-Span: Mixed 70%", {"mode": "m", "width": 70, "low": 3, "high": 4, "rounds": 15}),
        ],
    },
}
