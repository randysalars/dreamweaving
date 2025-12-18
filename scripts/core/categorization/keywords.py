"""
Category keyword mappings for dreamweaving auto-categorization.

Each category has:
- primary: High-confidence keywords (weight: 1.0)
- secondary: Supporting keywords (weight: 0.5)
"""

CATEGORY_KEYWORDS = {
    # Core Categories (from /types page)
    "guided-visualization": {
        "primary": [
            "visualization", "guided", "imagery", "imagine", "picture",
            "visualize", "envision", "guided journey", "inner vision"
        ],
        "secondary": [
            "scene", "landscape", "vision", "see", "observe",
            "inner eye", "mental image", "picture", "visual"
        ],
        "priority": 10,
    },
    "shamanic-journeying": {
        "primary": [
            "shamanic", "shaman", "drum", "drumming", "spirit guide",
            "animal ally", "totem", "power animal", "shamanism"
        ],
        "secondary": [
            "journey", "spirit", "realm", "lower world", "upper world",
            "middle world", "soul retrieval", "tribal", "indigenous"
        ],
        "priority": 20,
    },
    "active-imagination": {
        "primary": [
            "active imagination", "jungian", "jung", "dialogue",
            "inner figure", "dream symbol", "psyche", "analytical psychology"
        ],
        "secondary": [
            "unconscious", "personification", "anima", "animus",
            "persona", "complex", "individuation", "depth psychology"
        ],
        "priority": 30,
    },
    "mindfulness-pathworkings": {
        "primary": [
            "mindfulness", "mindful", "meditation", "meditative",
            "breath", "breathing", "present moment", "awareness practice"
        ],
        "secondary": [
            "awareness", "body scan", "sensation", "grounding",
            "centered", "stillness", "calm", "zen", "vipassana"
        ],
        "priority": 40,
    },
    "archetypal-encounters": {
        "primary": [
            "archetype", "archetypal", "hero", "sage", "shadow",
            "warrior", "lover", "magician", "king", "queen"
        ],
        "secondary": [
            "fool", "trickster", "mother", "father", "wise old man",
            "great mother", "inner child", "anima", "animus"
        ],
        "priority": 50,
    },
    "healing-journeys": {
        "primary": [
            "healing", "heal", "restore", "repair", "recover",
            "wellness", "therapy", "therapeutic", "cure"
        ],
        "secondary": [
            "emotional release", "energy balance", "self-compassion",
            "trauma", "integration", "wholeness", "renewal", "restoration"
        ],
        "priority": 60,
    },
    "creative-inspiration": {
        "primary": [
            "creative", "creativity", "inspiration", "inspire",
            "imagination", "artistic", "innovation", "creative flow"
        ],
        "secondary": [
            "muse", "ideas", "problem solving", "brainstorm",
            "vision", "expression", "art", "invention"
        ],
        "priority": 70,
    },
    "lucid-dream-induction": {
        "primary": [
            "lucid dream", "lucid dreaming", "dream awareness",
            "conscious dreaming", "dream control", "lucidity"
        ],
        "secondary": [
            "reality check", "dream state", "sleep", "REM",
            "hypnagogia", "dream recall", "oneironautics", "wake-initiated"
        ],
        "priority": 80,
    },

    # Extended Categories (from /more page)
    "elemental-journeys": {
        "primary": [
            "element", "elemental", "earth", "water", "fire",
            "air", "ether", "elements", "earth element"
        ],
        "secondary": [
            "grounding", "flow", "transformation", "breath",
            "spirit", "nature force", "primal", "element work"
        ],
        "priority": 100,
    },
    "mythic-storywork": {
        "primary": [
            "myth", "mythic", "mythology", "legend", "epic",
            "saga", "tale", "hero's journey", "mythological"
        ],
        "secondary": [
            "quest", "odyssey", "fairy tale", "folklore",
            "story", "narrative", "ancient story", "mythical"
        ],
        "priority": 110,
    },
    "soundscapes": {
        "primary": [
            "soundscape", "binaural", "sound healing", "frequency",
            "tone", "vibration", "sonic", "sound journey"
        ],
        "secondary": [
            "music", "ambient", "nature sounds", "isochronic",
            "solfeggio", "432hz", "theta", "audio meditation"
        ],
        "priority": 120,
    },
    "collective-dreamweavings": {
        "primary": [
            "collective", "group", "shared", "community",
            "together", "unified", "group journey"
        ],
        "secondary": [
            "mass consciousness", "hive mind", "group soul",
            "collective unconscious", "morphic field", "communal"
        ],
        "priority": 130,
    },
    "future-self-encounters": {
        "primary": [
            "future self", "future version", "older self",
            "wiser self", "destiny", "potential", "higher self"
        ],
        "secondary": [
            "timeline", "possibilities", "direction", "guidance",
            "vision", "purpose", "becoming", "evolution"
        ],
        "priority": 140,
    },
    "integration-pathworkings": {
        "primary": [
            "integration", "integrate", "embody", "ground",
            "anchor", "consolidate", "integrative"
        ],
        "secondary": [
            "apply", "daily life", "practical", "real world",
            "sustainable", "lasting", "embodiment"
        ],
        "priority": 150,
    },

    # Theme Categories
    "cultural-traditions": {
        "primary": [
            "cultural", "tradition", "native american", "indigenous",
            "japanese", "celtic", "egyptian", "apache", "ancestral"
        ],
        "secondary": [
            "heritage", "customs", "ritual", "ceremony",
            "lineage", "tribal", "ancient culture"
        ],
        "priority": 200,
    },
    "eastern-philosophy": {
        "primary": [
            "taoist", "taoism", "dao", "daoism",
            "buddhist", "buddhism", "zen", "zen meditation",
            "hindu", "vedic", "vedas", "yoga philosophy",
            "yin", "yang", "yin-yang", "yin and yang",
            "eastern", "oriental philosophy"
        ],
        "secondary": [
            "confucian", "confucius",
            "sufi", "sufism",
            "dharma", "karma", "chakra",
            "mantra", "om", "meditation",
            "wu wei", "middle way", "enlightenment",
            "balance", "polarity", "philosophy"
        ],
        "priority": 205,
    },
    "spiritual-religious": {
        "primary": [
            "christian", "biblical", "gnostic", "spiritual",
            "sacred", "divine", "holy", "religious", "christ"
        ],
        "secondary": [
            "saints", "virtues", "temple", "altar",
            "prayer", "devotion", "grace", "masonic", "wiccan"
        ],
        "priority": 210,
    },
    "nature-elements": {
        "primary": [
            "nature", "forest", "garden", "tree", "plant",
            "animal", "mineral", "crystal", "eden"
        ],
        "secondary": [
            "meadow", "river", "mountain", "herb",
            "seed", "wildlife", "ecosystem", "natural"
        ],
        "priority": 220,
    },
    "mythology-archetypes": {
        "primary": [
            "god", "goddess", "deity", "mythical creature",
            "dragon", "unicorn", "tarot", "tree of life"
        ],
        "secondary": [
            "pantheon", "olympus", "asgard", "kabbalah",
            "symbol", "oracle", "divine being"
        ],
        "priority": 230,
    },
    "healing-wellness": {
        "primary": [
            "trauma", "addiction", "recovery", "energy healing",
            "chakra", "negativity", "release", "wellness"
        ],
        "secondary": [
            "forgiveness", "letting go", "peace", "balance",
            "harmony", "restoration", "therapy"
        ],
        "priority": 240,
    },
    "personal-development": {
        "primary": [
            "confidence", "power", "strength", "courage",
            "wealth", "abundance", "success", "empowerment"
        ],
        "secondary": [
            "motivation", "achievement", "relationship",
            "connection", "purpose", "growth"
        ],
        "priority": 250,
    },
    "creative-arts": {
        "primary": [
            "poetry", "artistic", "musical", "writing",
            "creative arts", "expression", "art"
        ],
        "secondary": [
            "muse", "composition", "performance",
            "dance", "theater", "creative expression"
        ],
        "priority": 260,
    },
    "science-exploration": {
        "primary": [
            "physics", "math", "chemistry", "science",
            "cognitive", "quantum", "electric", "scientific"
        ],
        "secondary": [
            "elements", "periodic table", "formula",
            "experiment", "discovery", "neural"
        ],
        "priority": 270,
    },
    "paranormal-esoteric": {
        "primary": [
            "ufo", "alien", "parallel reality", "third eye",
            "astral", "paranormal", "psychic", "extraterrestrial"
        ],
        "secondary": [
            "telepathy", "clairvoyance", "dimension",
            "portal", "otherworldly", "supernatural"
        ],
        "priority": 280,
    },
    "historical-journeys": {
        "primary": [
            "history", "historical", "president", "civil war",
            "independence", "ancient", "medieval", "era"
        ],
        "secondary": [
            "period", "famous", "leader", "founding fathers",
            "historic", "past", "antiquity"
        ],
        "priority": 290,
    },
    "entertainment-inspired": {
        "primary": [
            "lord of the rings", "matrix", "book character",
            "movie", "film", "story", "adventure"
        ],
        "secondary": [
            "tolkien", "middle earth", "neo", "fictional",
            "fantasy world", "sci-fi", "fiction"
        ],
        "priority": 300,
    },
    "sensory-body": {
        "primary": [
            "senses", "sensory", "sensuality", "beauty",
            "body", "touch", "pleasure", "somatic"
        ],
        "secondary": [
            "taste", "smell", "sight", "hearing",
            "kinesthetic", "embodied"
        ],
        "priority": 310,
    },
    "shadow-depths": {
        "primary": [
            "shadow", "dark", "underworld", "descent",
            "unconscious", "depth", "darkness"
        ],
        "secondary": [
            "hell", "abyss", "void", "monster",
            "fear", "integration", "shadow work"
        ],
        "priority": 320,
    },
    "higher-realms": {
        "primary": [
            "ascent", "heaven", "heavenly", "light",
            "angel", "higher", "divine", "celestial"
        ],
        "secondary": [
            "guide", "helper", "luminous", "radiant",
            "enlightenment", "transcendent"
        ],
        "priority": 330,
    },

    # Growth Experience Categories
    "consciousness-exploration": {
        "primary": [
            "consciousness", "awareness", "perception", "mind",
            "being", "existence", "perspective", "conscious"
        ],
        "secondary": [
            "infant", "newborn", "animal mind", "plant consciousness",
            "hive mind", "collective", "sentience"
        ],
        "priority": 400,
    },
    "scientific-dimensional": {
        "primary": [
            "quantum", "physics", "ai", "artificial intelligence",
            "time travel", "evolution", "dimension", "dimensional"
        ],
        "secondary": [
            "particle", "wave", "observer", "relativity",
            "multiverse", "paradox", "scientific"
        ],
        "priority": 410,
    },
    "microscopic-cosmic": {
        "primary": [
            "microscopic", "cosmic", "nanoparticle", "black hole",
            "universe", "galaxy", "star", "cosmos"
        ],
        "secondary": [
            "cell", "molecule", "atom", "space",
            "nebula", "big bang", "radiation"
        ],
        "priority": 420,
    },
}

# Archetype to category mapping
ARCHETYPE_CATEGORIES = {
    # Core archetypes
    "hero": ["archetypal-encounters", "personal-development"],
    "sage": ["archetypal-encounters", "spiritual-religious"],
    "healer": ["healing-journeys", "healing-wellness"],
    "shaman": ["shamanic-journeying"],
    "guide": ["guided-visualization", "future-self-encounters"],
    "shadow": ["shadow-depths", "active-imagination"],
    "warrior": ["archetypal-encounters", "personal-development"],
    "lover": ["archetypal-encounters", "sensory-body"],
    "magician": ["archetypal-encounters", "creative-inspiration"],
    "king": ["archetypal-encounters", "personal-development"],
    "queen": ["archetypal-encounters", "personal-development"],
    "fool": ["archetypal-encounters", "creative-inspiration"],
    "trickster": ["archetypal-encounters", "shadow-depths"],
    "mother": ["archetypal-encounters", "healing-journeys"],
    "father": ["archetypal-encounters", "personal-development"],
    "wise old man": ["archetypal-encounters", "spiritual-religious"],
    "great mother": ["archetypal-encounters", "nature-elements"],
    "inner child": ["archetypal-encounters", "healing-journeys"],

    # Nature archetypes
    "animal": ["shamanic-journeying", "nature-elements"],
    "plant": ["nature-elements", "healing-wellness"],
    "tree": ["nature-elements"],
    "forest": ["nature-elements"],

    # Divine archetypes
    "angel": ["higher-realms", "spiritual-religious"],
    "god": ["mythology-archetypes", "spiritual-religious"],
    "goddess": ["mythology-archetypes", "spiritual-religious"],
    "deity": ["mythology-archetypes"],

    # Mythic archetypes
    "dragon": ["mythology-archetypes", "shadow-depths"],
    "phoenix": ["mythology-archetypes", "healing-journeys"],
    "unicorn": ["mythology-archetypes", "higher-realms"],
}

# Binaural frequency to category hints
FREQUENCY_CATEGORIES = {
    # Delta (0.5-4 Hz) - Deep sleep, unconscious
    "delta": ["shadow-depths", "consciousness-exploration"],
    # Theta (4-8 Hz) - Meditation, dreams
    "theta": ["guided-visualization", "lucid-dream-induction", "shamanic-journeying"],
    # Alpha (8-12 Hz) - Relaxation, creativity
    "alpha": ["mindfulness-pathworkings", "creative-inspiration", "healing-journeys"],
    # Beta (12-30 Hz) - Alert, focused
    "beta": ["personal-development", "science-exploration"],
    # Gamma (30-100 Hz) - Peak awareness
    "gamma": ["consciousness-exploration", "higher-realms"],
}

# Map keywords.py category slugs to actual database category slugs
# The database has fewer categories than keywords.py, so we need to map them
SLUG_TO_DB_CATEGORY = {
    # Direct matches (same slug in both)
    "eastern-philosophy": "eastern-philosophy",
    "archetypal": "archetypal",
    "relaxation": "relaxation",
    "confidence": "confidence",
    "healing": "healing",
    "shadow-work": "shadow-work",
    "nature-forest": "nature-forest",
    "cosmic-space": "cosmic-space",
    "sacred-spiritual": "sacred-spiritual",
    "layer-1": "layer-1",

    # Map keywords.py slugs -> database slugs
    "healing-journeys": "healing",
    "healing-wellness": "healing",
    "spiritual-religious": "sacred-spiritual",
    "higher-realms": "sacred-spiritual",
    "shadow-depths": "shadow-work",
    "nature-elements": "nature-forest",
    "microscopic-cosmic": "cosmic-space",
    "personal-development": "confidence",
    "mindfulness-pathworkings": "relaxation",
    "soundscapes": "relaxation",
    "guided-visualization": "archetypal",
    "archetypal-encounters": "archetypal",
    "shamanic-journeying": "archetypal",
    "active-imagination": "archetypal",
    "lucid-dream-induction": "relaxation",
    "creative-inspiration": "archetypal",
    "elemental-journeys": "nature-forest",
    "mythic-storywork": "archetypal",
    "collective-dreamweavings": "archetypal",
    "future-self-encounters": "archetypal",
    "integration-pathworkings": "healing",
    "cultural-traditions": "sacred-spiritual",
    "mythology-archetypes": "archetypal",
    "creative-arts": "archetypal",
    "science-exploration": "cosmic-space",
    "paranormal-esoteric": "cosmic-space",
    "historical-journeys": "archetypal",
    "entertainment-inspired": "archetypal",
    "sensory-body": "relaxation",
    "consciousness-exploration": "cosmic-space",
    "scientific-dimensional": "cosmic-space",
}


def get_db_category(keywords_slug: str) -> str:
    """
    Convert a keywords.py category slug to the corresponding database category slug.

    The keywords.py file has many more granular categories than the database.
    This function maps them to the 10 database categories.

    Args:
        keywords_slug: The category slug from the auto-categorization system

    Returns:
        The corresponding database category slug, or 'archetypal' as fallback
    """
    return SLUG_TO_DB_CATEGORY.get(keywords_slug, "archetypal")
