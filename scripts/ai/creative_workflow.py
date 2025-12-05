#!/usr/bin/env python3
"""
Creative Workflow Engine for Dreamweaving

This module provides the complete creative pipeline from topic to script:
1. Brainstorm multiple journey concepts for a topic
2. Generate archetypes, binaural frequencies, and sound effects for each
3. Score and select the best journey for the target audience
4. Generate the complete SSML script

Usage:
    from scripts.ai.creative_workflow import CreativeWorkflow

    workflow = CreativeWorkflow()
    result = workflow.brainstorm_and_create("healing from grief")

    # Or step by step:
    concepts = workflow.brainstorm_journeys("healing from grief")
    selected = workflow.select_best_journey(concepts)
    script = workflow.generate_script(selected)
"""

import os
import sys
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
import random


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class BinauralProgression:
    """Defines binaural beat frequency progression for a journey."""
    name: str
    description: str
    sections: Dict[str, Dict[str, float]]  # section_name -> {offset_hz, duration_ratio}
    base_hz: int = 432
    gamma_burst_enabled: bool = False
    gamma_burst_time_ratio: float = 0.7  # When in journey to trigger gamma (0-1)

    def to_manifest_format(self, total_duration: int) -> List[Dict]:
        """Convert to manifest.yaml sound_bed.binaural.sections format."""
        result = []
        current_time = 0
        for section_name, config in self.sections.items():
            duration = int(total_duration * config.get('duration_ratio', 0.2))
            result.append({
                'start': current_time,
                'end': current_time + duration,
                'offset_hz': config['offset_hz']
            })
            current_time += duration
        return result


@dataclass
class Archetype:
    """Represents an archetypal figure or element in the journey."""
    name: str
    role: str  # guidance, transformation, wisdom_keeper, shadow, higher_self, vessel
    description: str
    symbol: str
    qualities: List[str]
    appearance_section: str  # Which section they appear in
    suggested_voice_tone: str = "warm"  # warm, deep, ethereal, commanding


@dataclass
class SoundEffect:
    """Represents a sound effect or audio layer."""
    name: str
    type: str  # texture, tone, nature, special
    description: str
    character: str
    sections: List[str]  # Which sections it's active in
    intensity: float = 0.5  # 0.0 to 1.0


@dataclass
class JourneyConcept:
    """Complete concept for a dreamweaving journey."""
    title: str
    theme: str
    metaphor: str  # Core metaphor/setting (e.g., "cosmic vessel", "garden", "ocean")
    therapeutic_goal: str
    setting: str
    key_transformation: str
    archetypes: List[Archetype]
    binaural_progression: BinauralProgression
    sound_effects: List[SoundEffect]
    target_duration_minutes: int = 30
    voice_recommendation: str = "default"  # Profile from voice_config.yaml
    imagery_style: str = "cosmic"  # cosmic, nature, abstract, mystical, technological
    score: float = 0.0  # Calculated fitness score
    score_breakdown: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'title': self.title,
            'theme': self.theme,
            'metaphor': self.metaphor,
            'therapeutic_goal': self.therapeutic_goal,
            'setting': self.setting,
            'key_transformation': self.key_transformation,
            'archetypes': [asdict(a) for a in self.archetypes],
            'binaural_progression': asdict(self.binaural_progression),
            'sound_effects': [asdict(s) for s in self.sound_effects],
            'target_duration_minutes': self.target_duration_minutes,
            'voice_recommendation': self.voice_recommendation,
            'imagery_style': self.imagery_style,
            'score': self.score,
            'score_breakdown': self.score_breakdown,
        }


# =============================================================================
# KNOWLEDGE BASES
# =============================================================================

# Therapeutic goal to brainwave state mapping
THERAPEUTIC_BRAINWAVES = {
    'healing': {'primary': 'theta', 'secondary': 'delta', 'peak': 'gamma'},
    'grief': {'primary': 'theta', 'secondary': 'delta', 'peak': 'theta'},
    'anxiety': {'primary': 'alpha', 'secondary': 'theta', 'peak': 'alpha'},
    'confidence': {'primary': 'alpha', 'secondary': 'beta', 'peak': 'gamma'},
    'sleep': {'primary': 'delta', 'secondary': 'theta', 'peak': None},
    'creativity': {'primary': 'theta', 'secondary': 'alpha', 'peak': 'gamma'},
    'focus': {'primary': 'beta', 'secondary': 'alpha', 'peak': 'gamma'},
    'spiritual': {'primary': 'theta', 'secondary': 'delta', 'peak': 'gamma'},
    'abundance': {'primary': 'alpha', 'secondary': 'theta', 'peak': 'gamma'},
    'trauma': {'primary': 'theta', 'secondary': 'delta', 'peak': None},
    'forgiveness': {'primary': 'theta', 'secondary': 'alpha', 'peak': 'gamma'},
    'self_love': {'primary': 'alpha', 'secondary': 'theta', 'peak': 'gamma'},
    'transformation': {'primary': 'theta', 'secondary': 'delta', 'peak': 'gamma'},
    'relaxation': {'primary': 'alpha', 'secondary': 'theta', 'peak': None},
}

# Brainwave frequencies
BRAINWAVE_FREQUENCIES = {
    'delta': 2.0,      # Deep sleep, healing
    'theta': 6.0,      # Meditation, creativity, memory
    'alpha': 10.0,     # Relaxation, calm focus
    'beta': 18.0,      # Active thinking
    'gamma': 40.0,     # Peak awareness, insight
}

# Predefined binaural progressions for different journey types
BINAURAL_TEMPLATES = {
    'deep_journey': BinauralProgression(
        name="Deep Journey Arc",
        description="Classic descent into theta/delta and return",
        sections={
            'pretalk': {'offset_hz': 10.0, 'duration_ratio': 0.08},
            'induction': {'offset_hz': 8.0, 'duration_ratio': 0.15},
            'deepening': {'offset_hz': 6.0, 'duration_ratio': 0.12},
            'journey_1': {'offset_hz': 4.0, 'duration_ratio': 0.20},
            'journey_2': {'offset_hz': 2.5, 'duration_ratio': 0.20},
            'integration': {'offset_hz': 6.0, 'duration_ratio': 0.12},
            'awakening': {'offset_hz': 10.0, 'duration_ratio': 0.13},
        },
        gamma_burst_enabled=True,
        gamma_burst_time_ratio=0.65,
    ),
    'healing': BinauralProgression(
        name="Healing Waters",
        description="Gentle theta with delta dips for cellular healing",
        sections={
            'pretalk': {'offset_hz': 10.0, 'duration_ratio': 0.10},
            'induction': {'offset_hz': 7.0, 'duration_ratio': 0.15},
            'healing_1': {'offset_hz': 4.0, 'duration_ratio': 0.25},
            'healing_2': {'offset_hz': 2.0, 'duration_ratio': 0.20},
            'integration': {'offset_hz': 5.0, 'duration_ratio': 0.15},
            'awakening': {'offset_hz': 9.0, 'duration_ratio': 0.15},
        },
        gamma_burst_enabled=False,
    ),
    'confidence': BinauralProgression(
        name="Empowerment Arc",
        description="Alpha-dominant with theta depths and gamma peaks",
        sections={
            'pretalk': {'offset_hz': 10.0, 'duration_ratio': 0.08},
            'induction': {'offset_hz': 8.0, 'duration_ratio': 0.12},
            'foundation': {'offset_hz': 6.0, 'duration_ratio': 0.15},
            'empowerment': {'offset_hz': 10.0, 'duration_ratio': 0.25},
            'integration': {'offset_hz': 12.0, 'duration_ratio': 0.20},
            'awakening': {'offset_hz': 10.0, 'duration_ratio': 0.20},
        },
        gamma_burst_enabled=True,
        gamma_burst_time_ratio=0.60,
    ),
    'sleep': BinauralProgression(
        name="Sleep Descent",
        description="Gradual descent into deep delta, no return",
        sections={
            'pretalk': {'offset_hz': 8.0, 'duration_ratio': 0.05},
            'relaxation': {'offset_hz': 6.0, 'duration_ratio': 0.15},
            'descent_1': {'offset_hz': 4.0, 'duration_ratio': 0.20},
            'descent_2': {'offset_hz': 2.5, 'duration_ratio': 0.25},
            'deep_sleep': {'offset_hz': 1.5, 'duration_ratio': 0.35},
        },
        gamma_burst_enabled=False,
    ),
    'spiritual': BinauralProgression(
        name="Transcendence Path",
        description="Deep theta journey with gamma enlightenment moments",
        sections={
            'pretalk': {'offset_hz': 10.0, 'duration_ratio': 0.08},
            'induction': {'offset_hz': 7.83, 'duration_ratio': 0.12},  # Schumann resonance
            'opening': {'offset_hz': 6.0, 'duration_ratio': 0.15},
            'transcendence': {'offset_hz': 4.0, 'duration_ratio': 0.25},
            'communion': {'offset_hz': 3.0, 'duration_ratio': 0.15},
            'integration': {'offset_hz': 6.0, 'duration_ratio': 0.12},
            'return': {'offset_hz': 10.0, 'duration_ratio': 0.13},
        },
        gamma_burst_enabled=True,
        gamma_burst_time_ratio=0.55,
    ),
}

# Archetype templates by role
ARCHETYPE_TEMPLATES = {
    'guidance': [
        Archetype("The Navigator", "guidance", "Wise guide through unknown territories",
                  "compass of light", ["wisdom", "direction", "trust"], "induction"),
        Archetype("The Wise Elder", "guidance", "Ancient keeper of timeless knowledge",
                  "glowing staff", ["patience", "understanding", "acceptance"], "journey"),
        Archetype("The Star Guide", "guidance", "Celestial being of cosmic navigation",
                  "constellation map", ["cosmic awareness", "pathfinding", "clarity"], "journey"),
    ],
    'transformation': [
        Archetype("The Alchemist", "transformation", "Master of inner transmutation",
                  "philosopher's stone", ["transformation", "gold from lead", "potential"], "journey"),
        Archetype("The Phoenix", "transformation", "Symbol of rebirth through fire",
                  "flames of renewal", ["rebirth", "release", "new beginnings"], "journey"),
        Archetype("The Butterfly", "transformation", "Embodiment of metamorphosis",
                  "chrysalis", ["patience", "emergence", "beauty"], "integration"),
    ],
    'wisdom_keeper': [
        Archetype("The Scribe", "wisdom_keeper", "Keeper of ancient records and memories",
                  "living scroll", ["memory", "recording", "truth"], "journey"),
        Archetype("The Oracle", "wisdom_keeper", "Seer of past, present, and future",
                  "crystal pool", ["prophecy", "insight", "connection"], "journey"),
        Archetype("The Librarian", "wisdom_keeper", "Guardian of the cosmic archives",
                  "infinite library", ["knowledge", "access", "understanding"], "journey"),
    ],
    'healing': [
        Archetype("The Healer", "healing", "Compassionate presence of restoration",
                  "healing hands of light", ["restoration", "compassion", "wholeness"], "journey"),
        Archetype("The Water Bearer", "healing", "Bringer of emotional cleansing",
                  "sacred vessel", ["purification", "flow", "release"], "journey"),
        Archetype("The Garden Tender", "healing", "Nurturer of growth and renewal",
                  "seeds of light", ["nurturing", "patience", "cultivation"], "journey"),
    ],
    'higher_self': [
        Archetype("The Future Self", "higher_self", "Your evolved presence from beyond time",
                  "mirror of light", ["potential", "guidance", "love"], "journey"),
        Archetype("The Inner Light", "higher_self", "The divine spark within",
                  "radiant core", ["divinity", "truth", "essence"], "journey"),
        Archetype("The Soul Star", "higher_self", "Your eternal presence above the crown",
                  "star above", ["eternity", "purpose", "connection"], "integration"),
    ],
    'vessel': [
        Archetype("The Sacred Ship", "vessel", "Vehicle for consciousness travel",
                  "vessel of light", ["journey", "safety", "exploration"], "induction"),
        Archetype("The Temple", "vessel", "Sacred space for transformation",
                  "pillars of light", ["sanctuary", "ritual", "power"], "journey"),
        Archetype("The Cocoon", "vessel", "Protective space of becoming",
                  "silk of light", ["protection", "gestation", "emergence"], "journey"),
    ],
}

# Sound effect templates
SOUND_EFFECT_TEMPLATES = {
    'cosmic': [
        SoundEffect("Cosmic Hum", "tone", "Deep resonance of space", "ethereal drone", ["journey"], 0.4),
        SoundEffect("Star Whispers", "texture", "Distant stellar communication", "shimmering pulses", ["journey"], 0.3),
        SoundEffect("Nebula Drift", "texture", "Swirling cosmic gases", "slow movement", ["induction", "journey"], 0.5),
    ],
    'nature': [
        SoundEffect("Forest Rain", "nature", "Gentle rainfall through leaves", "soft patter", ["induction", "journey"], 0.4),
        SoundEffect("Ocean Waves", "nature", "Rhythmic surf on shore", "rolling waves", ["induction", "journey"], 0.5),
        SoundEffect("Wind Through Trees", "nature", "Gentle breeze in canopy", "rustling leaves", ["journey"], 0.3),
    ],
    'mystical': [
        SoundEffect("Temple Bells", "special", "Distant sacred resonance", "crystalline tones", ["journey", "integration"], 0.3),
        SoundEffect("Singing Bowls", "tone", "Tibetan bowl harmonics", "rich overtones", ["induction", "journey"], 0.4),
        SoundEffect("Angelic Choir", "texture", "Ethereal voices", "wordless harmony", ["journey"], 0.3),
    ],
    'technological': [
        SoundEffect("Ship Systems", "texture", "Ambient vessel sounds", "soft hums and beeps", ["journey"], 0.3),
        SoundEffect("Warp Field", "texture", "Dimensional transition", "swooshing energy", ["journey"], 0.4),
        SoundEffect("Neural Interface", "special", "Digital consciousness connection", "crystalline data", ["journey"], 0.3),
    ],
    'elemental': [
        SoundEffect("Sacred Fire", "nature", "Crackling ceremonial flames", "warm crackle", ["journey"], 0.4),
        SoundEffect("Underground Stream", "nature", "Water flowing through caverns", "echoing flow", ["journey"], 0.4),
        SoundEffect("Mountain Wind", "nature", "High altitude air currents", "powerful gusts", ["journey"], 0.3),
    ],
}

# Journey setting templates
SETTING_TEMPLATES = {
    'cosmic': [
        "aboard a sentient starship traveling between dimensions",
        "floating through a luminous nebula of creation",
        "walking through a crystalline space station at the edge of the galaxy",
        "sitting in the observation deck of an ancient alien vessel",
    ],
    'nature': [
        "in an ancient forest where the trees hold memories",
        "by a sacred pool deep within a hidden valley",
        "atop a mountain where the veil between worlds is thin",
        "in a garden that exists between sleeping and waking",
    ],
    'mystical': [
        "within an infinite library containing all knowledge",
        "in a temple made of living light",
        "inside a sacred geometric pattern come alive",
        "at the threshold of a doorway between realms",
    ],
    'underwater': [
        "in a crystal palace beneath peaceful waters",
        "floating through an ocean of luminescent light",
        "in an underwater temple of ancient wisdom",
        "within a sacred cenote of healing waters",
    ],
    'inner': [
        "deep within the landscape of your own heart",
        "in the garden of your subconscious mind",
        "within the temple of your inner wisdom",
        "at the center of your own radiant being",
    ],
}

# Topic keyword mappings for intelligent concept generation
TOPIC_KEYWORDS = {
    'grief': ['healing', 'loss', 'release', 'memories', 'letting go', 'peace', 'acceptance'],
    'anxiety': ['calm', 'peace', 'safety', 'grounding', 'breath', 'present', 'stillness'],
    'confidence': ['power', 'strength', 'voice', 'presence', 'worth', 'capability', 'shine'],
    'sleep': ['rest', 'peace', 'surrender', 'drift', 'comfort', 'warmth', 'release'],
    'abundance': ['flow', 'receiving', 'wealth', 'prosperity', 'deserving', 'open', 'attract'],
    'healing': ['restoration', 'wholeness', 'light', 'repair', 'renewal', 'cellular', 'energy'],
    'spiritual': ['connection', 'divine', 'source', 'higher', 'consciousness', 'awakening', 'unity'],
    'creativity': ['flow', 'inspiration', 'muse', 'expression', 'ideas', 'birth', 'channel'],
    'forgiveness': ['release', 'peace', 'freedom', 'compassion', 'understanding', 'letting go'],
    'transformation': ['change', 'becoming', 'evolution', 'shedding', 'emergence', 'new'],
    'self_love': ['acceptance', 'compassion', 'worth', 'nurturing', 'embrace', 'kindness'],
    'focus': ['clarity', 'attention', 'concentration', 'laser', 'precision', 'single-pointed'],
}


# =============================================================================
# CREATIVE WORKFLOW ENGINE
# =============================================================================

class CreativeWorkflow:
    """
    Complete creative workflow from topic to script.

    Handles:
    - Brainstorming multiple journey concepts
    - Generating appropriate archetypes, binaural progressions, sound effects
    - Scoring and selecting the best journey
    - Generating the complete SSML script
    """

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the creative workflow engine."""
        self.project_root = Path(__file__).parent.parent.parent
        self.config_path = config_path or self.project_root / "config" / "voice_config.yaml"
        self.voice_config = self._load_voice_config()
        self.lessons_learned = self._load_lessons()

    def _load_voice_config(self) -> Dict:
        """Load voice configuration."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        return {}

    def _load_lessons(self) -> Dict:
        """Load lessons learned for informed decisions."""
        lessons_path = self.project_root / "knowledge" / "lessons_learned.yaml"
        if lessons_path.exists():
            with open(lessons_path, 'r') as f:
                return yaml.safe_load(f)
        return {}

    def identify_therapeutic_focus(self, topic: str) -> Tuple[str, List[str]]:
        """
        Analyze the topic to identify the primary therapeutic focus.

        Returns:
            Tuple of (primary_focus, relevant_keywords)
        """
        topic_lower = topic.lower()

        # Score each therapeutic category
        scores = {}
        for category, keywords in TOPIC_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in topic_lower)
            # Also check if category name is in topic
            if category.replace('_', ' ') in topic_lower:
                score += 3
            scores[category] = score

        # Get best match
        if max(scores.values()) > 0:
            primary = max(scores, key=scores.get)
        else:
            # Default to transformation for unknown topics
            primary = 'transformation'

        # Collect relevant keywords found
        relevant = []
        for kw_list in TOPIC_KEYWORDS.values():
            for kw in kw_list:
                if kw in topic_lower:
                    relevant.append(kw)

        return primary, relevant

    def brainstorm_journeys(
        self,
        topic: str,
        num_concepts: int = 5,
        duration_minutes: int = 30
    ) -> List[JourneyConcept]:
        """
        Brainstorm multiple journey concepts for a given topic.

        Args:
            topic: The session topic/theme
            num_concepts: Number of concepts to generate
            duration_minutes: Target duration for the session

        Returns:
            List of JourneyConcept objects
        """
        therapeutic_focus, keywords = self.identify_therapeutic_focus(topic)
        concepts = []

        # Determine which setting styles to use based on therapeutic focus
        setting_styles = self._get_setting_styles_for_focus(therapeutic_focus)

        for i in range(num_concepts):
            # Rotate through setting styles
            style = setting_styles[i % len(setting_styles)]

            # Create concept
            concept = self._generate_concept(
                topic=topic,
                therapeutic_focus=therapeutic_focus,
                keywords=keywords,
                setting_style=style,
                duration_minutes=duration_minutes,
                concept_num=i + 1,
            )
            concepts.append(concept)

        return concepts

    def _get_setting_styles_for_focus(self, therapeutic_focus: str) -> List[str]:
        """Get appropriate setting styles for a therapeutic focus."""
        style_mappings = {
            'healing': ['nature', 'underwater', 'inner', 'mystical'],
            'grief': ['nature', 'inner', 'mystical', 'cosmic'],
            'anxiety': ['nature', 'underwater', 'inner'],
            'confidence': ['cosmic', 'mystical', 'inner'],
            'sleep': ['nature', 'underwater', 'cosmic'],
            'spiritual': ['cosmic', 'mystical', 'inner'],
            'abundance': ['nature', 'cosmic', 'mystical'],
            'creativity': ['cosmic', 'mystical', 'nature'],
            'transformation': ['cosmic', 'mystical', 'inner', 'nature'],
            'self_love': ['inner', 'nature', 'mystical'],
            'forgiveness': ['nature', 'inner', 'underwater'],
            'focus': ['cosmic', 'mystical', 'inner'],
        }
        return style_mappings.get(therapeutic_focus, ['cosmic', 'nature', 'mystical', 'inner'])

    def _generate_concept(
        self,
        topic: str,
        therapeutic_focus: str,
        keywords: List[str],
        setting_style: str,
        duration_minutes: int,
        concept_num: int,
    ) -> JourneyConcept:
        """Generate a single journey concept."""

        # Select setting - derive from topic if descriptive enough
        setting = self._generate_setting(topic, setting_style)

        # Create title based on setting and focus
        title = self._generate_title(topic, therapeutic_focus, setting_style, concept_num)

        # Generate metaphor
        metaphor = self._generate_metaphor(therapeutic_focus, setting_style)

        # Select binaural progression
        binaural = self._select_binaural_progression(therapeutic_focus)

        # Select archetypes (2-4 per journey)
        archetypes = self._select_archetypes(therapeutic_focus, setting_style)

        # Select sound effects
        sound_effects = self._select_sound_effects(setting_style)

        # Select voice
        voice = self._select_voice(therapeutic_focus)

        # Create the concept
        concept = JourneyConcept(
            title=title,
            theme=topic,
            metaphor=metaphor,
            therapeutic_goal=therapeutic_focus.replace('_', ' '),
            setting=setting,
            key_transformation=self._generate_transformation(therapeutic_focus, keywords),
            archetypes=archetypes,
            binaural_progression=binaural,
            sound_effects=sound_effects,
            target_duration_minutes=duration_minutes,
            voice_recommendation=voice,
            imagery_style=setting_style,
        )

        return concept

    def _generate_title(self, topic: str, focus: str, style: str, num: int) -> str:
        """Generate a compelling title for the journey.

        If the user provided a descriptive topic (3+ words), use it directly
        with proper title case. Otherwise, fall back to template-based generation.
        """
        # Check if topic is descriptive enough to use directly
        topic_words = topic.strip().split()
        if len(topic_words) >= 3:
            # Topic is descriptive - use it directly with enhancement
            return self._enhance_topic_title(topic)

        # Fall back to template-based generation for generic topics
        title_templates = {
            'cosmic': [
                "Voyage to the {focus} Star",
                "The Cosmic {focus} Gateway",
                "Starlight Journey of {focus}",
                "Celestial {focus} Activation",
            ],
            'nature': [
                "The Sacred Grove of {focus}",
                "Waters of {focus}",
                "The Ancient Forest of {focus}",
                "Mountain Path to {focus}",
            ],
            'mystical': [
                "The Temple of {focus}",
                "Gateway to {focus}",
                "The Sacred {focus} Chamber",
                "Initiation into {focus}",
            ],
            'underwater': [
                "Deep Waters of {focus}",
                "The {focus} Sanctuary Below",
                "Ocean of {focus}",
                "The Crystal {focus} Cavern",
            ],
            'inner': [
                "Journey to Your Inner {focus}",
                "The Heart's {focus} Path",
                "Within: A {focus} Voyage",
                "The {focus} Within",
            ],
        }

        templates = title_templates.get(style, title_templates['cosmic'])
        template = templates[num % len(templates)]

        focus_word = focus.replace('_', ' ').title()
        return template.format(focus=focus_word)

    def _enhance_topic_title(self, topic: str) -> str:
        """Enhance a user-provided topic into a polished title.

        Applies proper title case while preserving special words like
        articles, prepositions, and proper nouns.
        """
        # Words that should remain lowercase (unless first word)
        lowercase_words = {'to', 'the', 'a', 'an', 'of', 'in', 'for', 'and', 'or', 'but', 'with', 'from'}

        title = topic.strip()
        words = title.split()
        result = []

        for i, word in enumerate(words):
            # First word is always capitalized
            if i == 0:
                result.append(word.capitalize())
            # Check if word is already all caps (might be acronym or proper noun like "MASTER")
            elif word.isupper() and len(word) > 1:
                result.append(word)
            # Lowercase words stay lowercase
            elif word.lower() in lowercase_words:
                result.append(word.lower())
            # Everything else gets title case
            else:
                result.append(word.capitalize())

        return ' '.join(result)

    def _generate_setting(self, topic: str, style: str) -> str:
        """Generate setting based on topic or fall back to templates.

        If the topic is descriptive (3+ words), derive the setting from it.
        Otherwise, randomly select from style-based templates.
        """
        topic_words = topic.strip().split()

        if len(topic_words) >= 3:
            # Derive setting from the topic
            return self._derive_setting_from_topic(topic)

        # Fall back to template-based setting
        settings = SETTING_TEMPLATES.get(style, SETTING_TEMPLATES['cosmic'])
        return random.choice(settings)

    def _derive_setting_from_topic(self, topic: str) -> str:
        """Derive a setting description from a descriptive topic.

        Transforms topic into an immersive setting description.
        """
        topic_lower = topic.lower()

        # Check for specific mythological/geographical references
        if any(term in topic_lower for term in ['tír na nóg', 'tir na nog', 'land of eternal', 'otherworld']):
            return "on the mystical shores of Tír na nÓg, the Celtic Otherworld where time stands still and eternal youth flows through every breath"

        if any(term in topic_lower for term in ['eden', 'garden of']):
            return "within the luminous Garden of Eden, where the Tree of Life glows with sacred light and rivers of living water flow"

        if any(term in topic_lower for term in ['atlantis', 'atlantean']):
            return "in the crystal halls of ancient Atlantis, where advanced wisdom merges with sacred technology"

        if any(term in topic_lower for term in ['egypt', 'pyramid', 'pharaoh', 'nile']):
            return "within an ancient Egyptian temple, where hieroglyphs glow with golden light and the wisdom of ages awaits"

        if any(term in topic_lower for term in ['celtic', 'druid', 'stonehenge']):
            return "in a sacred Celtic grove, where ancient oaks whisper secrets and the veil between worlds grows thin"

        if any(term in topic_lower for term in ['forest', 'woods', 'tree']):
            return "deep within an enchanted forest, where ancient trees hold timeless wisdom and paths of light guide your way"

        if any(term in topic_lower for term in ['ocean', 'sea', 'water', 'underwater']):
            return "in the luminous depths of a sacred ocean, where crystalline waters hold healing energy and ancient mysteries"

        if any(term in topic_lower for term in ['mountain', 'peak', 'summit']):
            return "atop a sacred mountain where the veil between earth and sky dissolves into infinite possibility"

        if any(term in topic_lower for term in ['temple', 'shrine', 'sanctuary']):
            return "within an ancient temple of light, where sacred geometry resonates with cosmic harmony"

        if any(term in topic_lower for term in ['star', 'cosmic', 'galaxy', 'universe', 'space']):
            return "aboard a vessel of light traveling through the cosmic tapestry, where stars sing and nebulae pulse with creative energy"

        if any(term in topic_lower for term in ['dream', 'sleep', 'night']):
            return "in the realm between waking and dreaming, where consciousness drifts through landscapes of infinite possibility"

        if any(term in topic_lower for term in ['heart', 'love', 'soul']):
            return "deep within the sacred chamber of your heart, where your truest essence radiates with eternal light"

        if any(term in topic_lower for term in ['journey', 'path', 'quest']):
            return "on a sacred path that winds through realms of transformation, where each step brings you closer to your truest self"

        # Default: create a setting based on the topic itself
        return f"in a sacred realm where the essence of {topic.lower()} surrounds you with transformative energy"

    def _generate_metaphor(self, focus: str, style: str) -> str:
        """Generate the core metaphor for the journey."""
        metaphors = {
            ('healing', 'nature'): "healing waters flowing through an ancient forest",
            ('healing', 'cosmic'): "a sentient nebula that absorbs pain and radiates renewal",
            ('healing', 'underwater'): "a deep ocean sanctuary where wounds dissolve into light",
            ('grief', 'nature'): "a garden where memories become seeds of peace",
            ('grief', 'inner'): "a sacred chamber where tears become stars",
            ('confidence', 'cosmic'): "a starship powered by your inner fire",
            ('confidence', 'mystical'): "a temple where your true voice echoes eternal",
            ('sleep', 'nature'): "a nest of clouds cradled by ancient trees",
            ('sleep', 'cosmic'): "drifting through gentle nebulae toward peaceful void",
            ('spiritual', 'cosmic'): "a vessel traveling to the source of all consciousness",
            ('spiritual', 'mystical'): "a temple at the intersection of all dimensions",
            ('transformation', 'cosmic'): "a chrysalis ship carrying you to your next evolution",
            ('transformation', 'nature'): "a cocoon woven from moonlight and possibility",
        }

        key = (focus, style)
        if key in metaphors:
            return metaphors[key]

        # Default metaphor
        return f"a sacred journey through {style} realms toward {focus.replace('_', ' ')}"

    def _select_binaural_progression(self, focus: str) -> BinauralProgression:
        """Select the best binaural progression for the therapeutic focus."""
        # Map therapeutic focus to binaural template
        focus_to_template = {
            'healing': 'healing',
            'grief': 'healing',
            'anxiety': 'healing',
            'confidence': 'confidence',
            'sleep': 'sleep',
            'spiritual': 'spiritual',
            'abundance': 'confidence',
            'creativity': 'spiritual',
            'transformation': 'deep_journey',
            'self_love': 'healing',
            'forgiveness': 'healing',
            'focus': 'confidence',
        }

        template_name = focus_to_template.get(focus, 'deep_journey')
        template = BINAURAL_TEMPLATES[template_name]

        # Create a copy with slight randomization for variety
        import copy
        progression = copy.deepcopy(template)

        return progression

    def _select_archetypes(self, focus: str, style: str) -> List[Archetype]:
        """Select 2-4 archetypes appropriate for the journey."""
        # Determine which archetype roles are most relevant
        role_priorities = {
            'healing': ['healing', 'guidance', 'higher_self'],
            'grief': ['healing', 'wisdom_keeper', 'higher_self'],
            'anxiety': ['guidance', 'healing', 'vessel'],
            'confidence': ['higher_self', 'transformation', 'guidance'],
            'sleep': ['vessel', 'guidance', 'healing'],
            'spiritual': ['wisdom_keeper', 'higher_self', 'guidance'],
            'abundance': ['higher_self', 'transformation', 'guidance'],
            'creativity': ['transformation', 'wisdom_keeper', 'guidance'],
            'transformation': ['transformation', 'higher_self', 'guidance'],
            'self_love': ['higher_self', 'healing', 'guidance'],
            'forgiveness': ['healing', 'higher_self', 'wisdom_keeper'],
        }

        roles = role_priorities.get(focus, ['guidance', 'transformation', 'higher_self'])

        selected = []
        for role in roles[:3]:  # Select up to 3 archetypes
            templates = ARCHETYPE_TEMPLATES.get(role, [])
            if templates:
                archetype = random.choice(templates)
                selected.append(archetype)

        return selected

    def _select_sound_effects(self, style: str) -> List[SoundEffect]:
        """Select sound effects appropriate for the setting style."""
        effects = SOUND_EFFECT_TEMPLATES.get(style, SOUND_EFFECT_TEMPLATES['cosmic'])

        # Select 2-3 effects
        num_effects = min(3, len(effects))
        return random.sample(effects, num_effects)

    def _select_voice(self, focus: str) -> str:
        """Select the recommended voice profile for the focus."""
        # Map therapeutic focus to voice recommendations
        voice_mappings = {
            'healing': 'default',      # Neural2-E, deep resonant female
            'grief': 'soft_female',    # Neural2-C, soft nurturing
            'anxiety': 'default',
            'confidence': 'clear_female',  # Neural2-F
            'sleep': 'default',
            'spiritual': 'default',
            'abundance': 'clear_female',
            'creativity': 'warm_female',
            'transformation': 'default',
            'self_love': 'soft_female',
            'forgiveness': 'warm_female',
            'focus': 'calm_male',
        }

        return voice_mappings.get(focus, 'default')

    def _generate_transformation(self, focus: str, keywords: List[str]) -> str:
        """Generate the key transformation statement."""
        transformations = {
            'healing': "emerging whole, renewed, and radiating vitality",
            'grief': "releasing with love and finding peace within the memories",
            'anxiety': "resting in unshakeable calm and present-moment peace",
            'confidence': "standing in your full power, voice clear and presence magnetic",
            'sleep': "surrendering into the deepest, most restorative rest",
            'spiritual': "awakening to your cosmic nature and divine connection",
            'abundance': "opening fully to receive the universe's infinite gifts",
            'creativity': "becoming a clear channel for inspiration to flow through",
            'transformation': "emerging as the next evolution of yourself",
            'self_love': "embracing yourself completely with compassion and acceptance",
            'forgiveness': "releasing all burdens and walking free in peace",
            'focus': "achieving laser-like clarity and unwavering attention",
        }

        return transformations.get(focus, "experiencing profound positive transformation")

    def score_journey(self, concept: JourneyConcept) -> float:
        """
        Score a journey concept based on multiple factors.

        Scoring criteria:
        - Coherence: How well elements work together
        - Depth: Psychological/spiritual depth of the journey
        - Balance: Balance between elements
        - Novelty: Freshness of the combination
        - Effectiveness: Predicted therapeutic effectiveness

        Returns:
            Score from 0.0 to 1.0
        """
        scores = {}

        # Coherence score (setting matches focus)
        coherence = self._score_coherence(concept)
        scores['coherence'] = coherence

        # Archetype depth score
        archetype_score = self._score_archetypes(concept)
        scores['archetype_depth'] = archetype_score

        # Binaural appropriateness
        binaural_score = self._score_binaural(concept)
        scores['binaural_match'] = binaural_score

        # Sound design score
        sound_score = self._score_sound_design(concept)
        scores['sound_design'] = sound_score

        # Duration feasibility
        duration_score = 1.0 if 20 <= concept.target_duration_minutes <= 45 else 0.7
        scores['duration'] = duration_score

        # Calculate weighted average
        weights = {
            'coherence': 0.30,
            'archetype_depth': 0.25,
            'binaural_match': 0.20,
            'sound_design': 0.15,
            'duration': 0.10,
        }

        total_score = sum(scores[k] * weights[k] for k in scores)

        # Store breakdown
        concept.score_breakdown = scores
        concept.score = total_score

        return total_score

    def _score_coherence(self, concept: JourneyConcept) -> float:
        """Score how coherently the elements work together."""
        score = 0.7  # Base score

        # Check if imagery style matches therapeutic goal
        good_matches = {
            'healing': ['nature', 'underwater', 'inner'],
            'grief': ['nature', 'inner', 'mystical'],
            'confidence': ['cosmic', 'mystical'],
            'spiritual': ['cosmic', 'mystical'],
            'sleep': ['nature', 'underwater', 'cosmic'],
        }

        goal = concept.therapeutic_goal.replace(' ', '_')
        if goal in good_matches:
            if concept.imagery_style in good_matches[goal]:
                score += 0.2

        # Check archetype coherence
        if len(concept.archetypes) >= 2:
            score += 0.1

        return min(1.0, score)

    def _score_archetypes(self, concept: JourneyConcept) -> float:
        """Score the archetype selection."""
        if not concept.archetypes:
            return 0.3

        score = 0.5

        # Having 2-3 archetypes is ideal
        num_archetypes = len(concept.archetypes)
        if 2 <= num_archetypes <= 3:
            score += 0.3
        elif num_archetypes == 4:
            score += 0.2

        # Check for role diversity
        roles = set(a.role for a in concept.archetypes)
        if len(roles) >= 2:
            score += 0.2

        return min(1.0, score)

    def _score_binaural(self, concept: JourneyConcept) -> float:
        """Score binaural progression appropriateness."""
        score = 0.7  # Base score for having any progression

        prog = concept.binaural_progression

        # Check if gamma burst is appropriate
        therapeutic_brainwaves = THERAPEUTIC_BRAINWAVES.get(
            concept.therapeutic_goal.replace(' ', '_'), {}
        )

        if therapeutic_brainwaves.get('peak') == 'gamma' and prog.gamma_burst_enabled:
            score += 0.2
        elif therapeutic_brainwaves.get('peak') is None and not prog.gamma_burst_enabled:
            score += 0.1

        # Check section count (5-7 is ideal)
        num_sections = len(prog.sections)
        if 5 <= num_sections <= 7:
            score += 0.1

        return min(1.0, score)

    def _score_sound_design(self, concept: JourneyConcept) -> float:
        """Score sound effect selection."""
        if not concept.sound_effects:
            return 0.5

        score = 0.6

        # Having 2-3 effects is ideal
        num_effects = len(concept.sound_effects)
        if 2 <= num_effects <= 3:
            score += 0.2

        # Check for type diversity
        types = set(e.type for e in concept.sound_effects)
        if len(types) >= 2:
            score += 0.2

        return min(1.0, score)

    def select_best_journey(
        self,
        concepts: List[JourneyConcept],
        audience_preferences: Optional[Dict] = None
    ) -> JourneyConcept:
        """
        Select the best journey concept from the brainstormed options.

        Args:
            concepts: List of brainstormed concepts
            audience_preferences: Optional dict with audience preferences

        Returns:
            The highest-scoring JourneyConcept
        """
        # Score all concepts
        for concept in concepts:
            self.score_journey(concept)

        # Apply audience preference adjustments if provided
        if audience_preferences:
            self._apply_audience_preferences(concepts, audience_preferences)

        # Sort by score and return best
        concepts.sort(key=lambda c: c.score, reverse=True)

        return concepts[0]

    def _apply_audience_preferences(
        self,
        concepts: List[JourneyConcept],
        preferences: Dict
    ):
        """Adjust scores based on audience preferences."""
        preferred_style = preferences.get('imagery_style')
        preferred_duration = preferences.get('duration_minutes')

        for concept in concepts:
            adjustment = 0.0

            if preferred_style and concept.imagery_style == preferred_style:
                adjustment += 0.1

            if preferred_duration:
                duration_diff = abs(concept.target_duration_minutes - preferred_duration)
                if duration_diff <= 5:
                    adjustment += 0.05

            concept.score = min(1.0, concept.score + adjustment)

    def generate_manifest(self, concept: JourneyConcept, session_name: str) -> Dict:
        """
        Generate a complete manifest.yaml structure from a concept.

        Args:
            concept: The selected journey concept
            session_name: Name for the session directory

        Returns:
            Dict representing the manifest.yaml content
        """
        duration_seconds = concept.target_duration_minutes * 60

        # Get voice config
        voice_profile = self.voice_config.get('profiles', {}).get(
            concept.voice_recommendation,
            self.voice_config.get('profiles', {}).get('default', {})
        )

        manifest = {
            'session': {
                'name': session_name,
                'topic': concept.theme,
                'duration': duration_seconds,
                'style': concept.therapeutic_goal.replace(' ', '_'),
                'created': datetime.now().strftime('%Y-%m-%d'),
            },
            'voice': {
                'provider': 'google',
                'voice_name': voice_profile.get('name', 'en-US-Neural2-E'),
                'description': concept.title,
                'rate': 0.85,
                'pitch': '-2st',
            },
            'sections': self._generate_sections(concept, duration_seconds),
            'archetypes': [
                {
                    'name': a.name,
                    'role': a.role,
                    'description': a.description,
                    'symbol': a.symbol,
                    'qualities': a.qualities,
                    'appearance_section': a.appearance_section,
                }
                for a in concept.archetypes
            ],
            'sound_bed': {
                'binaural': {
                    'enabled': True,
                    'base_hz': concept.binaural_progression.base_hz,
                    'sections': concept.binaural_progression.to_manifest_format(duration_seconds),
                },
                'pink_noise': {'enabled': False},
                'nature': {'enabled': any(e.type == 'nature' for e in concept.sound_effects)},
            },
            'mixing': {
                'voice_lufs': -16,
                'binaural_lufs': -26,
                'sidechain': {'enabled': True},
            },
            'mastering': {
                'target_lufs': -14,
                'true_peak_dbtp': -1.5,
                'sample_rate_hz': 48000,
                'bit_depth': 24,
            },
            'outputs': {
                'formats': ['wav', 'mp3'],
            },
            'youtube': {
                'title': f"{concept.title} | Binaural Beats Meditation",
                'subtitle': f"432Hz • {concept.therapeutic_goal.title()}",
                'description': f"A transformational journey: {concept.key_transformation}",
                'tags': [
                    'binaural beats',
                    'meditation',
                    '432hz',
                    'guided meditation',
                    concept.therapeutic_goal,
                    concept.imagery_style,
                ],
            },
        }

        # Add FX timeline if gamma burst enabled
        if concept.binaural_progression.gamma_burst_enabled:
            gamma_time = int(duration_seconds * concept.binaural_progression.gamma_burst_time_ratio)
            manifest['fx_timeline'] = [{
                'type': 'gamma_flash',
                'time': gamma_time,
                'duration_s': 3.0,
                'freq_hz': 40,
                'description': 'Peak insight moment',
            }]

        return manifest

    def _generate_sections(self, concept: JourneyConcept, duration: int) -> List[Dict]:
        """Generate section timing from concept."""
        sections = []

        # Standard section ratios
        ratios = {
            'pretalk': 0.08,
            'induction': 0.15,
            'journey': 0.50,
            'integration': 0.15,
            'awakening': 0.12,
        }

        brainwave_targets = {
            'pretalk': 'alpha',
            'induction': 'alpha_to_theta',
            'journey': 'theta_delta',
            'integration': 'theta_to_alpha',
            'awakening': 'alpha',
        }

        current_time = 0
        for section_name, ratio in ratios.items():
            section_duration = int(duration * ratio)
            sections.append({
                'name': section_name,
                'start': current_time,
                'end': current_time + section_duration,
                'brainwave_target': brainwave_targets[section_name],
                'description': self._get_section_description(section_name, concept),
            })
            current_time += section_duration

        return sections

    def _get_section_description(self, section: str, concept: JourneyConcept) -> str:
        """Generate section description based on concept."""
        descriptions = {
            'pretalk': f"Welcome and introduction to {concept.theme}",
            'induction': f"Relaxation and descent into {concept.setting}",
            'journey': f"Main journey: {concept.metaphor}",
            'integration': f"Integration: {concept.key_transformation}",
            'awakening': "Gentle return to full waking awareness",
        }
        return descriptions.get(section, section.title())

    def brainstorm_and_create(
        self,
        topic: str,
        session_name: Optional[str] = None,
        num_concepts: int = 5,
        duration_minutes: int = 30,
        audience_preferences: Optional[Dict] = None,
        save_concepts: bool = True,
    ) -> Dict:
        """
        Complete workflow: brainstorm, select best, generate manifest.

        Args:
            topic: The session topic/theme
            session_name: Name for the session (auto-generated if None)
            num_concepts: Number of concepts to brainstorm
            duration_minutes: Target session duration
            audience_preferences: Optional audience preference adjustments
            save_concepts: Whether to save all concepts to file

        Returns:
            Dict with 'selected_concept', 'manifest', 'all_concepts'
        """
        # Generate session name if not provided
        if not session_name:
            session_name = topic.lower().replace(' ', '-').replace("'", "")[:30]

        # Brainstorm concepts
        concepts = self.brainstorm_journeys(
            topic=topic,
            num_concepts=num_concepts,
            duration_minutes=duration_minutes,
        )

        # Select best
        selected = self.select_best_journey(concepts, audience_preferences)

        # Generate manifest
        manifest = self.generate_manifest(selected, session_name)

        result = {
            'selected_concept': selected.to_dict(),
            'manifest': manifest,
            'all_concepts': [c.to_dict() for c in concepts],
            'session_name': session_name,
        }

        # Optionally save concepts
        if save_concepts:
            session_path = self.project_root / "sessions" / session_name
            session_path.mkdir(parents=True, exist_ok=True)

            concepts_file = session_path / "working_files" / "brainstormed_concepts.yaml"
            concepts_file.parent.mkdir(parents=True, exist_ok=True)

            with open(concepts_file, 'w') as f:
                yaml.dump(result['all_concepts'], f, default_flow_style=False, sort_keys=False)

        return result

    def display_concepts(self, concepts: List[JourneyConcept]) -> str:
        """Generate a human-readable display of brainstormed concepts."""
        lines = ["=" * 60]
        lines.append("BRAINSTORMED JOURNEY CONCEPTS")
        lines.append("=" * 60)

        for i, concept in enumerate(concepts, 1):
            lines.append(f"\n--- Concept {i}: {concept.title} ---")
            lines.append(f"Theme: {concept.theme}")
            lines.append(f"Setting: {concept.setting}")
            lines.append(f"Metaphor: {concept.metaphor}")
            lines.append(f"Key Transformation: {concept.key_transformation}")
            lines.append(f"Duration: {concept.target_duration_minutes} minutes")
            lines.append(f"Imagery Style: {concept.imagery_style}")
            lines.append(f"Voice: {concept.voice_recommendation}")

            lines.append("\nArchetypes:")
            for arch in concept.archetypes:
                lines.append(f"  - {arch.name} ({arch.role}): {arch.description}")

            lines.append(f"\nBinaural: {concept.binaural_progression.name}")
            lines.append(f"  {concept.binaural_progression.description}")

            lines.append("\nSound Effects:")
            for fx in concept.sound_effects:
                lines.append(f"  - {fx.name}: {fx.description}")

            if concept.score > 0:
                lines.append(f"\nScore: {concept.score:.2f}")
                for key, val in concept.score_breakdown.items():
                    lines.append(f"  {key}: {val:.2f}")

        lines.append("\n" + "=" * 60)
        return "\n".join(lines)


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """CLI interface for the creative workflow."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Brainstorm and create dreamweaving journeys'
    )
    parser.add_argument('topic', help='The topic/theme for the journey')
    parser.add_argument('--name', '-n', help='Session name (auto-generated if not provided)')
    parser.add_argument('--concepts', '-c', type=int, default=5,
                       help='Number of concepts to brainstorm (default: 5)')
    parser.add_argument('--duration', '-d', type=int, default=30,
                       help='Target duration in minutes (default: 30)')
    parser.add_argument('--style', '-s',
                       choices=['cosmic', 'nature', 'mystical', 'underwater', 'inner'],
                       help='Preferred imagery style')
    parser.add_argument('--show-all', action='store_true',
                       help='Show all brainstormed concepts')
    parser.add_argument('--save-manifest', action='store_true',
                       help='Save manifest to session directory')
    parser.add_argument('--json', action='store_true',
                       help='Output as JSON')

    args = parser.parse_args()

    # Build preferences
    preferences = {}
    if args.style:
        preferences['imagery_style'] = args.style
    if args.duration != 30:
        preferences['duration_minutes'] = args.duration

    # Run workflow
    workflow = CreativeWorkflow()

    result = workflow.brainstorm_and_create(
        topic=args.topic,
        session_name=args.name,
        num_concepts=args.concepts,
        duration_minutes=args.duration,
        audience_preferences=preferences if preferences else None,
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        # Display results
        if args.show_all:
            concepts = [JourneyConcept(**c) if isinstance(c, dict) else c
                       for c in result['all_concepts']]
            # Need to reconstruct objects for display
            print("\nAll brainstormed concepts saved to working_files/brainstormed_concepts.yaml")

        print("\n" + "=" * 60)
        print("SELECTED JOURNEY")
        print("=" * 60)
        selected = result['selected_concept']
        print(f"\nTitle: {selected['title']}")
        print(f"Theme: {selected['theme']}")
        print(f"Setting: {selected['setting']}")
        print(f"Metaphor: {selected['metaphor']}")
        print(f"Transformation: {selected['key_transformation']}")
        print(f"Score: {selected['score']:.2f}")

        print("\nArchetypes:")
        for arch in selected['archetypes']:
            print(f"  - {arch['name']}: {arch['description']}")

        print(f"\nBinaural: {selected['binaural_progression']['name']}")

        if args.save_manifest:
            session_path = workflow.project_root / "sessions" / result['session_name']
            session_path.mkdir(parents=True, exist_ok=True)
            manifest_path = session_path / "manifest.yaml"

            with open(manifest_path, 'w') as f:
                yaml.dump(result['manifest'], f, default_flow_style=False, sort_keys=False)

            print(f"\nManifest saved to: {manifest_path}")
        else:
            print(f"\nUse --save-manifest to save to sessions/{result['session_name']}/manifest.yaml")


if __name__ == "__main__":
    main()
