"""
Transformation Map Schema
Defines the journey from starting state to ending state with milestones.
"""

from pydantic import BaseModel, Field
from typing import List


class Milestone(BaseModel):
    """A checkpoint in the transformation journey."""
    name: str = Field(description="Milestone name")
    description: str = Field(description="What the reader achieves here")
    marker: str = Field(description="How they know they've reached it")
    chapter_range: str = Field(description="Which chapters cover this milestone")


class TransformationMap(BaseModel):
    """
    The transformation contract.
    Every piece of content must advance the reader toward these outcomes.
    """
    starting_state: str = Field(
        description="Where the reader begins: emotions, beliefs, capabilities"
    )
    ending_state: str = Field(
        description="Where the reader ends: emotions, beliefs, capabilities"
    )
    milestones: List[Milestone] = Field(
        description="3-7 checkpoints in the journey",
        min_length=3,
        max_length=7
    )
    belief_shifts: List[str] = Field(
        description="What beliefs must change? (Before → After)"
    )
    skill_gains: List[str] = Field(
        description="What new capabilities will they have?"
    )
    habit_changes: List[str] = Field(
        description="What behaviors will they adopt?"
    )
    identity_evolution: str = Field(
        description="How will they see themselves differently?"
    )
