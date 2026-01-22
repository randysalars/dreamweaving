"""
Voice Stylist Agent
Generates the VoiceStyleGuide - anti-AI writing rules.
"""

import logging
import json
from pathlib import Path

from ..core.llm import LLMClient
from ..schemas.positioning_brief import PositioningBrief
from ..schemas.voice_style_guide import VoiceStyleGuide

logger = logging.getLogger(__name__)


class VoiceStylist:
    """
    Defines the voice and anti-AI writing rules.
    """
    
    # Default banned phrases (AI tells)
    DEFAULT_BANNED_PHRASES = [
        "In today's fast-paced world",
        "It's important to note",
        "Let's dive in",
        "Without further ado",
        "In conclusion",
        "First and foremost",
        "At the end of the day",
        "It goes without saying",
        "Needless to say",
        "The fact of the matter is",
        "When it comes to",
        "In order to",
        "Due to the fact that",
        "As a matter of fact",
        "For all intents and purposes"
    ]
    
    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir
        self.llm = LLMClient()
        
    def generate(self, brief: PositioningBrief, title: str) -> VoiceStyleGuide:
        """
        Generate VoiceStyleGuide based on audience and positioning.
        """
        logger.info(f"🎨 VoiceStylist crafting voice guide for: {title}")
        
        # Determine tone based on audience sophistication
        tone = self._determine_tone(brief)
        
        guide = VoiceStyleGuide(
            sentence_rhythm_rules=[
                "Vary sentence length: mix short punchy sentences with longer flowing ones",
                "Use fragments for emphasis. Like this.",
                "No more than 3 sentences of similar length in a row",
                "Start some sentences with 'And' or 'But' for conversational feel",
                "End sections with short, memorable statements"
            ],
            banned_phrases=self.DEFAULT_BANNED_PHRASES,
            metaphor_density="1-2 fresh metaphors per page, 0 clichés",
            story_to_instruction_ratio="30/70 for practical content, 50/50 for transformational",
            leveling_rules={
                "beginner": "Define all terms, use simple examples, slower pacing",
                "intermediate": "Assume basics, focus on application and nuance",
                "advanced": "Dense content, tradeoffs, edge cases, expert shortcuts"
            },
            tone_descriptors=tone,
            micro_story_quota=2
        )
        
        logger.info(f"✅ VoiceStyleGuide generated with {len(guide.banned_phrases)} banned phrases")
        return guide
    
    def _determine_tone(self, brief: PositioningBrief) -> list[str]:
        """Determine tone based on audience and topic."""
        base_tone = ["confident", "practical", "warm"]
        
        if brief.audience.sophistication_level == "expert":
            base_tone = ["authoritative", "precise", "collegial"]
        elif brief.audience.sophistication_level == "beginner":
            base_tone = ["encouraging", "patient", "accessible"]
        
        return base_tone
