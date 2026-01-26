"""
Bonus Plan Schema
Defines the structure for intelligently designed product bonuses.
"""

from pydantic import BaseModel, Field
from typing import Literal, List


class Bonus(BaseModel):
    """A single bonus item designed to enhance the main product."""
    type: Literal["clarity", "application", "reinforcement", "deep_dive"] = Field(
        description="The purpose category of this bonus"
    )
    title: str = Field(description="Name of the bonus")
    format: Literal["pdf", "audio", "video", "interactive", "checklist", "worksheet"] = Field(
        description="The delivery format"
    )
    description: str = Field(description="What this bonus provides")
    target_friction: str = Field(
        description="Which chapter or concept this bonus helps with"
    )
    estimated_pages: int = Field(default=5, description="Estimated length in pages/minutes")


class BonusPlan(BaseModel):
    """Complete bonus strategy for a product."""
    bonuses: List[Bonus] = Field(
        description="List of strategically designed bonuses",
        min_length=1,
        max_length=6
    )
    total_value_narrative: str = Field(
        description="How to present the combined value of bonuses"
    )
