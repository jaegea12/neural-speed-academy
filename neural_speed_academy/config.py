"""
Exercise configurations and data for Neural Speed Academy.
"""
from __future__ import annotations

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
}

# Training paths
# Each step: (exercise_type, label, params_dict)
# exercise_type maps to a launcher in the path execution screen.
TRAINING_PATHS = {
    # Daily Warmup first — most frequently used
    "daily_warmup": {
        "name": "Daily Warmup",
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
}
