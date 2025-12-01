#!/usr/bin/env python3
"""
Hypnotic Language Patterns Module
Ericksonian nested loops, Milton Model ambiguities, sensory-synesthetic blending,
somatic anchors, limbic language, and time distortion patterns.

Based on clinical hypnotherapy research and NLP linguistic modeling.
"""

import random
from typing import List, Dict, Optional

# =============================================================================
# NESTED HYPNOTIC LOOPS (Ericksonian Patterning)
# =============================================================================

NESTED_LOOPS = [
    # Loop pattern 1: Noticing awareness
    [
        "and as you notice yourself listening",
        "you may also notice yourself noticing",
        "how listening becomes a feeling",
        "and that feeling becomes something drifting inward",
    ],
    # Loop pattern 2: Drifting deeper
    [
        "and as you drift",
        "you might notice the drifting",
        "becoming a kind of floating",
        "that floats you deeper still",
    ],
    # Loop pattern 3: Relaxation cascade
    [
        "and as relaxation spreads",
        "you can feel yourself feeling",
        "the feeling of letting go",
        "letting go into a deeper letting go",
    ],
    # Loop pattern 4: Awareness expanding
    [
        "and as awareness expands",
        "expanding into the expansion itself",
        "you find yourself finding",
        "something that was always here",
    ],
    # Loop pattern 5: Breath awareness
    [
        "and as you breathe",
        "breathing into the breathing",
        "each breath becomes a wave",
        "carrying you on waves of breath",
    ],
]

def get_nested_loop(index: Optional[int] = None) -> List[str]:
    """Get a nested loop pattern for hypnotic deepening."""
    if index is not None and 0 <= index < len(NESTED_LOOPS):
        return NESTED_LOOPS[index]
    return random.choice(NESTED_LOOPS)


# =============================================================================
# SENSORY-SYNESTHETIC BLENDING
# =============================================================================

SYNESTHETIC_PHRASES = [
    # Visual-kinesthetic
    "feel the color of the light",
    "sense the texture of the silence",
    "touch the warmth of the glow",

    # Auditory-kinesthetic
    "hear the warmth spreading",
    "listen to the softness",
    "feel the sound of stillness",

    # Visual-auditory
    "see the sound of your breath softening",
    "watch the silence deepen",
    "observe the quiet colors",

    # Kinesthetic-visual
    "the weight becomes a color",
    "heaviness dissolving into light",
    "warmth glowing from within",

    # Multi-sensory
    "taste the sweetness of peace",
    "smell the freshness of clarity",
    "the texture of timelessness",
]

def get_synesthetic_phrase() -> str:
    """Get a random sensory-synesthetic phrase."""
    return random.choice(SYNESTHETIC_PHRASES)


# =============================================================================
# SOMATIC ANCHORS
# =============================================================================

SOMATIC_ANCHORS = {
    "head": [
        "that subtle heaviness behind the eyes",
        "the softness gathering around the eyes",
        "a gentle pressure at the crown",
        "the temples releasing their grip",
        "the jaw unclenching naturally",
    ],
    "shoulders": [
        "the heaviness settling into the shoulders",
        "shoulders dropping away from the ears",
        "that releasing in the upper back",
        "arms growing pleasantly heavy",
    ],
    "chest": [
        "the chest opening softly",
        "heart space expanding",
        "breath flowing freely through the ribs",
        "a warm glow behind the sternum",
    ],
    "abdomen": [
        "the belly softening",
        "that gentle unwinding in the core",
        "abdomen floating freely",
        "the center growing still and quiet",
    ],
    "spine": [
        "the spine lengthening naturally",
        "each vertebra releasing",
        "that warm hum at the base of the spine",
        "the back body melting into support",
    ],
    "hands": [
        "warmth spreading through the palms",
        "fingers softening and releasing",
        "hands growing pleasantly heavy",
        "that tingling in the fingertips",
    ],
    "feet": [
        "feet grounding into the earth",
        "toes releasing their grip",
        "the soles of the feet warming",
        "energy flowing down through the legs",
    ],
    "breath": [
        "your breath as a soft wave rising and falling",
        "the way your breath naturally slows",
        "each exhale a gentle release",
        "breath becoming effortless",
    ],
}

def get_somatic_anchor(body_part: Optional[str] = None) -> str:
    """Get a somatic anchor phrase for a specific body part or random."""
    if body_part and body_part in SOMATIC_ANCHORS:
        return random.choice(SOMATIC_ANCHORS[body_part])
    all_anchors = [a for anchors in SOMATIC_ANCHORS.values() for a in anchors]
    return random.choice(all_anchors)


# =============================================================================
# MILTON MODEL AMBIGUITIES
# =============================================================================

MILTON_MODEL_PATTERNS = {
    "mind_reading": [
        "you may already be noticing",
        "something inside knows exactly how",
        "part of you understands",
        "your unconscious mind recognizes",
        "you're probably aware that",
    ],
    "lost_performative": [
        "it's good to relax deeply",
        "it's important to let go",
        "it's natural to drift",
        "it's comfortable to sink deeper",
        "it's perfectly okay to release",
    ],
    "cause_effect": [
        "as you breathe, you relax",
        "the more you listen, the deeper you go",
        "each word takes you further",
        "hearing my voice helps you drift",
        "with each moment, peace grows",
    ],
    "presupposition": [
        "when you notice the relaxation",
        "as you continue to deepen",
        "after you've drifted even deeper",
        "once you're completely relaxed",
        "before you go even deeper",
    ],
    "tag_questions": [
        "isn't it",
        "aren't you",
        "can't you",
        "don't you",
        "won't you",
    ],
    "double_binds": [
        "you can relax quickly or slowly, whichever feels right",
        "you may notice the change now or in a moment",
        "either way, you're drifting deeper",
        "whether you realize it consciously or not",
        "you can let go completely or partially at first",
    ],
    "embedded_commands": [
        "you can allow yourself to sink deeper",
        "it's okay to let go more fully now",
        "your body knows how to relax perfectly",
        "you might find yourself drifting down",
        "perhaps you'll notice yourself releasing",
    ],
    "ambiguity": [
        "a certain kind of drifting",
        "something shifting inside",
        "that interesting feeling",
        "a particular sense of",
        "in a way that's just right",
    ],
}

def get_milton_pattern(pattern_type: Optional[str] = None) -> str:
    """Get a Milton Model language pattern."""
    if pattern_type and pattern_type in MILTON_MODEL_PATTERNS:
        return random.choice(MILTON_MODEL_PATTERNS[pattern_type])
    all_patterns = [p for patterns in MILTON_MODEL_PATTERNS.values() for p in patterns]
    return random.choice(all_patterns)


# =============================================================================
# LIMBIC LANGUAGE (Emotional Activation)
# =============================================================================

LIMBIC_PHRASES = {
    "safety": [
        "safe warmth",
        "held securely",
        "protected and peaceful",
        "cocooned in comfort",
        "wrapped in safety",
    ],
    "softness": [
        "soft openness",
        "gentle surrender",
        "tender release",
        "delicate unwinding",
        "silky stillness",
    ],
    "warmth": [
        "warm golden glow",
        "spreading warmth",
        "cozy depths",
        "sun-touched peace",
        "gentle heat",
    ],
    "floating": [
        "a drifting sense of being held",
        "floating weightlessly",
        "suspended in stillness",
        "buoyant and free",
        "carried gently",
    ],
    "depth": [
        "deeper stillness",
        "profound quiet",
        "ancient peace",
        "bottomless calm",
        "infinite rest",
    ],
}

def get_limbic_phrase(emotion: Optional[str] = None) -> str:
    """Get a limbic language phrase for emotional activation."""
    if emotion and emotion in LIMBIC_PHRASES:
        return random.choice(LIMBIC_PHRASES[emotion])
    all_phrases = [p for phrases in LIMBIC_PHRASES.values() for p in phrases]
    return random.choice(all_phrases)


# =============================================================================
# TIME DISTORTION LANGUAGE
# =============================================================================

TIME_DISTORTION_PHRASES = [
    "moments stretching softly",
    "a feeling outside ordinary time",
    "between one breath and the next, entire worlds open",
    "time becoming elastic",
    "hours passing like seconds, or seconds like hours",
    "in this timeless space",
    "where past and future dissolve",
    "suspended between moments",
    "time unwinding like a ribbon",
    "in the eternal now",
    "minutes melting into moments",
    "beyond the reach of clocks",
    "where time has no meaning",
    "drifting through timelessness",
    "a single moment containing everything",
]

def get_time_distortion() -> str:
    """Get a time distortion phrase."""
    return random.choice(TIME_DISTORTION_PHRASES)


# =============================================================================
# TRANCE RATIFICATIONS
# =============================================================================

TRANCE_RATIFICATIONS = [
    # Physical observations
    "that subtle heaviness in your jaw",
    "the way your breath naturally slows",
    "the softness gathering around the eyes",
    "that pleasant weight in your limbs",
    "the stillness spreading through your body",

    # Mental observations
    "thoughts drifting by like clouds",
    "that dreamy quality to your awareness",
    "the way sounds seem more distant",
    "how words float past your conscious mind",
    "that comfortable mental fog",

    # Emotional observations
    "that sense of deep peace settling in",
    "the quiet contentment spreading",
    "a feeling of profound safety",
    "that inner smile forming",
    "the warmth of complete acceptance",
]

def get_trance_ratification() -> str:
    """Get a trance ratification phrase."""
    return random.choice(TRANCE_RATIFICATIONS)


# =============================================================================
# SOOTHING REFRAINS (Rhythmic Anchors)
# =============================================================================

SOOTHING_REFRAINS = [
    "and deeper still",
    "softly drifting",
    "a slow dissolving",
    "beautifully relaxing",
    "gently releasing",
    "floating down",
    "peacefully surrendering",
    "melting deeper",
    "quietly descending",
    "tenderly letting go",
]

def get_soothing_refrain() -> str:
    """Get a soothing refrain for rhythmic entrainment."""
    return random.choice(SOOTHING_REFRAINS)


# =============================================================================
# EMOTIONAL COLOR GRADING
# =============================================================================

EMOTIONAL_COLORS = {
    "induction_early": {
        "primary": ["warmth", "safety", "comfort"],
        "phrases": [
            "wrapped in gentle warmth",
            "safe and supported",
            "comfortable and at ease",
            "held in peaceful safety",
        ]
    },
    "induction_deep": {
        "primary": ["quiet depth", "inner descent", "stillness"],
        "phrases": [
            "sinking into quiet depths",
            "descending inward",
            "profound stillness gathering",
            "the deep quiet within",
        ]
    },
    "journey": {
        "primary": ["wonder", "calm curiosity", "exploration"],
        "phrases": [
            "curious and open",
            "gently exploring",
            "wonder unfolding",
            "peaceful discovery",
        ]
    },
    "core_experience": {
        "primary": ["profound stillness", "gravity", "timelessness"],
        "phrases": [
            "absolute stillness",
            "weightless gravity",
            "timeless presence",
            "infinite depth",
        ]
    },
    "return": {
        "primary": ["clarity", "brightness", "gentle awakening"],
        "phrases": [
            "clarity returning",
            "gentle brightening",
            "softly awakening",
            "peaceful emergence",
        ]
    },
}

def get_emotional_color(phase: str) -> Dict:
    """Get emotional color grading for a journey phase."""
    return EMOTIONAL_COLORS.get(phase, EMOTIONAL_COLORS["journey"])


# =============================================================================
# SOMATIC RETURN SEQUENCE
# =============================================================================

SOMATIC_RETURN_SEQUENCE = [
    {
        "area": "hands",
        "phrases": [
            "beginning with your hands, feeling warmth returning to your palms",
            "noticing your fingers now, perhaps a gentle tingling",
            "hands becoming more present, more alive",
        ]
    },
    {
        "area": "feet",
        "phrases": [
            "awareness flowing down to your feet",
            "feeling your toes, the soles of your feet",
            "grounding energy returning through your legs",
        ]
    },
    {
        "area": "breath",
        "phrases": [
            "breath deepening naturally",
            "fuller breaths now, refreshing and clearing",
            "each breath bringing more alertness",
        ]
    },
    {
        "area": "spine",
        "phrases": [
            "spine lengthening, posture naturally correcting",
            "energy rising up through your back",
            "feeling supported and upright",
        ]
    },
    {
        "area": "eyes",
        "phrases": [
            "eyes clearing behind closed lids",
            "light beginning to filter through",
            "ready to see clearly when you choose",
        ]
    },
]

def get_somatic_return_sequence() -> List[Dict]:
    """Get the full somatic return sequence."""
    return SOMATIC_RETURN_SEQUENCE


# =============================================================================
# SSML GENERATION HELPERS
# =============================================================================

def generate_temporal_jitter(base_ms: int = 300, variance: int = 80) -> int:
    """Generate randomized pause duration for natural rhythm."""
    return base_ms + random.randint(-variance, variance)


def generate_pitch_drift(base_pct: float = 0.0, variance: float = 3.0) -> str:
    """Generate subtle pitch variation for natural speech."""
    drift = base_pct + random.uniform(-variance, variance)
    sign = "+" if drift >= 0 else ""
    return f"{sign}{drift:.1f}%"


def wrap_with_falling_cadence(text: str, drop_semitones: float = -0.5) -> str:
    """Wrap text with SSML for falling cadence (sentence ending)."""
    return f'<prosody pitch="{drop_semitones}st">{text}</prosody>'


def wrap_with_pitch_drift(text: str) -> str:
    """Wrap text with random pitch drift for naturalness."""
    drift = generate_pitch_drift()
    return f'<prosody pitch="{drift}">{text}</prosody>'


def generate_break(base_ms: int = 300) -> str:
    """Generate SSML break with temporal jitter."""
    ms = generate_temporal_jitter(base_ms)
    return f'<break time="{ms}ms"/>'


# =============================================================================
# PATTERN INTEGRATION
# =============================================================================

def generate_deepening_sequence() -> str:
    """Generate a complete hypnotic deepening sequence."""
    sequence = []

    # Start with Milton Model presupposition
    sequence.append(get_milton_pattern("presupposition"))
    sequence.append(generate_break(400))

    # Add nested loop
    loop = get_nested_loop()
    for phrase in loop:
        sequence.append(phrase)
        sequence.append(generate_break(350))

    # Add somatic anchor
    sequence.append(get_somatic_anchor())
    sequence.append(generate_break(500))

    # Add trance ratification
    sequence.append(get_trance_ratification())
    sequence.append(generate_break(400))

    # End with soothing refrain
    sequence.append(wrap_with_falling_cadence(get_soothing_refrain()))

    return " ".join(sequence)


# =============================================================================
# CLI for testing
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("HYPNOTIC LANGUAGE PATTERNS - Test Output")
    print("=" * 70)

    print("\n--- Nested Loop ---")
    for phrase in get_nested_loop():
        print(f"  {phrase}")

    print("\n--- Synesthetic Phrase ---")
    print(f"  {get_synesthetic_phrase()}")

    print("\n--- Somatic Anchors ---")
    for part in ["head", "breath", "spine"]:
        print(f"  [{part}] {get_somatic_anchor(part)}")

    print("\n--- Milton Model ---")
    for ptype in ["embedded_commands", "presupposition", "double_binds"]:
        print(f"  [{ptype}] {get_milton_pattern(ptype)}")

    print("\n--- Limbic Language ---")
    for emotion in ["safety", "warmth", "depth"]:
        print(f"  [{emotion}] {get_limbic_phrase(emotion)}")

    print("\n--- Time Distortion ---")
    print(f"  {get_time_distortion()}")

    print("\n--- Trance Ratification ---")
    print(f"  {get_trance_ratification()}")

    print("\n--- Complete Deepening Sequence ---")
    print(generate_deepening_sequence())

    print("\n--- Temporal Jitter Examples ---")
    for _ in range(5):
        print(f"  {generate_temporal_jitter()}ms", end=" ")
    print()
