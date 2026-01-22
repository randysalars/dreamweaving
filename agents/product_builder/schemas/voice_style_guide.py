"""
Voice Style Guide Schema
Defines the anti-AI writing rules and voice parameters.
"""

from pydantic import BaseModel, Field
from typing import List, Dict


class VoiceStyleGuide(BaseModel):
    """
    The voice contract.
    Writers must follow these rules to avoid AI-sounding content.
    """
    sentence_rhythm_rules: List[str] = Field(
        description="Rules for varying sentence length and structure",
        examples=[
            ["Vary sentence length: short, medium, long",
             "Use fragments for emphasis",
             "No more than 3 sentences in a row of similar length"]
        ]
    )
    banned_phrases: List[str] = Field(
        description="AI tells that must never appear",
        examples=[
            ["In today's fast-paced world",
             "It's important to note",
             "Let's dive in",
             "Without further ado",
             "In conclusion"]
        ]
    )
    metaphor_density: str = Field(
        default="1-2 per page",
        description="How often to use metaphors"
    )
    story_to_instruction_ratio: str = Field(
        default="30/70",
        description="Percentage of narrative vs direct instruction"
    )
    leveling_rules: Dict[str, str] = Field(
        description="How to adjust for different reader levels",
        examples=[{
            "beginner": "Use simple words, more examples, slower pacing",
            "intermediate": "Assume basics, focus on application",
            "advanced": "Dense content, nuanced tradeoffs, edge cases"
        }]
    )
    tone_descriptors: List[str] = Field(
        description="3-5 adjectives describing the voice",
        examples=[["confident", "warm", "practical", "slightly irreverent"]]
    )
    micro_story_quota: int = Field(
        default=2,
        description="Minimum vivid examples or micro-stories per chapter"
    )
