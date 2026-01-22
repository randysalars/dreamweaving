"""
Transformation Designer Agent
Generates the TransformationMap - the journey from starting state to ending state.
"""

import logging
import json
from pathlib import Path
from typing import List

from ..core.llm import LLMClient
from ..schemas.positioning_brief import PositioningBrief
from ..schemas.transformation_map import TransformationMap, Milestone

logger = logging.getLogger(__name__)


class TransformationDesigner:
    """
    Designs the transformation journey based on the PositioningBrief.
    """
    
    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir
        self.llm = LLMClient()
        
    def generate(self, brief: PositioningBrief, title: str) -> TransformationMap:
        """
        Generate TransformationMap from PositioningBrief.
        """
        logger.info(f"🦋 TransformationDesigner mapping journey for: {title}")
        
        prompt = self._build_prompt(brief, title)
        response = self.llm.generate(prompt, max_tokens=2000)
        transformation = self._parse_response(response, brief)
        
        logger.info(f"✅ TransformationMap generated with {len(transformation.milestones)} milestones")
        return transformation
    
    def _build_prompt(self, brief: PositioningBrief, title: str) -> str:
        return f"""
You are a transformation architect. Design the reader's journey.

## Context
- Core Promise: {brief.core_promise}
- Audience: {brief.audience.primary_persona}
- Pain Points: {', '.join(brief.audience.pain_points)}

## Generate a TransformationMap (JSON):

1. **Starting State**: Where does the reader begin? (emotions, beliefs, capabilities)
2. **Ending State**: Where do they end up?
3. **Milestones**: 3-7 checkpoints (name, description, marker, chapter_range)
4. **Belief Shifts**: What beliefs must change? (list of "Before → After")
5. **Skill Gains**: What new capabilities?
6. **Habit Changes**: What behaviors will they adopt?
7. **Identity Evolution**: How will they see themselves differently?

Return valid JSON.
"""

    def _parse_response(self, response: str, brief: PositioningBrief) -> TransformationMap:
        try:
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                data = json.loads(response[json_start:json_end])
                return TransformationMap(**data)
        except Exception as e:
            logger.warning(f"Failed to parse TransformationDesigner response: {e}")
        
        # Fallback
        return TransformationMap(
            starting_state=f"Confused and frustrated with {brief.audience.pain_points[0] if brief.audience.pain_points else 'the topic'}",
            ending_state=brief.core_promise,
            milestones=[
                Milestone(name="Foundation", description="Core concepts understood", marker="Can explain the basics", chapter_range="1-2"),
                Milestone(name="Application", description="First practical success", marker="Completed first exercise", chapter_range="3-5"),
                Milestone(name="Mastery", description="Full implementation", marker="Consistent results", chapter_range="6-8")
            ],
            belief_shifts=["I can't do this → I have a clear path", "This is too complex → This is manageable"],
            skill_gains=["Systematic approach", "Practical implementation"],
            habit_changes=["Daily practice", "Consistent review"],
            identity_evolution="From confused learner to confident practitioner"
        )
