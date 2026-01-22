"""
Curriculum Graph Schema
Defines concepts, dependencies, practice loops, and minimum viable mastery.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class Concept(BaseModel):
    """A teachable concept within the curriculum."""
    id: str = Field(description="Unique identifier for dependency mapping")
    name: str = Field(description="Concept name")
    description: str = Field(description="What this concept covers")
    difficulty: str = Field(description="beginner/intermediate/advanced")
    estimated_time_minutes: int = Field(default=15)


class PracticeLoop(BaseModel):
    """A practice activity tied to concepts."""
    name: str
    concept_ids: List[str] = Field(description="Which concepts this practices")
    type: str = Field(description="exercise/drill/project/reflection")
    instructions: str
    success_criteria: str


class Assessment(BaseModel):
    """A way to verify understanding."""
    name: str
    concept_ids: List[str]
    type: str = Field(description="quiz/self-check/project/application")
    questions_or_tasks: List[str]


class CurriculumGraph(BaseModel):
    """
    The curriculum contract.
    Ensures proper sequencing and practice coverage.
    """
    concepts: List[Concept] = Field(description="All teachable concepts")
    dependencies: Dict[str, List[str]] = Field(
        description="concept_id → list of prerequisite concept_ids"
    )
    practice_loops: List[PracticeLoop] = Field(
        description="Practice activities for each concept cluster"
    )
    assessments: List[Assessment] = Field(
        description="Ways to verify understanding"
    )
    minimum_viable_mastery: List[str] = Field(
        description="Checklist: What must the reader be able to do?"
    )
