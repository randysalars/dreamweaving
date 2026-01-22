"""
Positioning Brief Schema
The foundational market positioning artifact that all downstream agents must obey.
"""

from pydantic import BaseModel, Field
from typing import List


class AudienceProfile(BaseModel):
    """Detailed profile of the target audience."""
    primary_persona: str = Field(description="One-sentence description of ideal reader")
    pain_points: List[str] = Field(description="Top 3-5 frustrations they experience")
    current_solutions: List[str] = Field(description="What they've already tried")
    sophistication_level: str = Field(description="novice/intermediate/expert")
    buying_triggers: List[str] = Field(description="What makes them ready to act now")


class Objection(BaseModel):
    """A common doubt and its preemption."""
    objection: str = Field(description="The doubt or pushback")
    preemption: str = Field(description="How to address it")


class PositioningBrief(BaseModel):
    """
    The market positioning contract.
    Downstream agents cannot improvise outside this artifact.
    """
    audience: AudienceProfile = Field(description="Who this is for")
    core_promise: str = Field(
        description="The transformation statement: 'After this, you will...'"
    )
    differentiator: str = Field(
        description="Why yours vs alternatives: What makes this unique?"
    )
    objections: List[Objection] = Field(
        description="Common doubts and how we preempt them"
    )
    competing_alternatives: List[str] = Field(
        description="What else they could buy/do instead"
    )
    positioning_statement: str = Field(
        description="One paragraph elevator pitch"
    )
