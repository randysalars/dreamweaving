"""
Curriculum Architect Agent
Generates the CurriculumGraph - concepts, dependencies, practice loops.
"""

import logging
import json
from pathlib import Path
from typing import List

from ..core.llm import LLMClient
from ..schemas.transformation_map import TransformationMap
from ..schemas.curriculum_graph import CurriculumGraph, Concept, PracticeLoop, Assessment

logger = logging.getLogger(__name__)


class CurriculumArchitect:
    """
    Designs the learning structure based on the TransformationMap.
    """
    
    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir
        self.llm = LLMClient()
        
    def generate(self, transformation: TransformationMap, title: str) -> CurriculumGraph:
        """
        Generate CurriculumGraph from TransformationMap.
        """
        logger.info(f"📚 CurriculumArchitect designing learning structure for: {title}")
        
        prompt = self._build_prompt(transformation, title)
        response = self.llm.generate(prompt, max_tokens=3000)
        curriculum = self._parse_response(response, transformation)
        
        logger.info(f"✅ CurriculumGraph generated with {len(curriculum.concepts)} concepts")
        return curriculum
    
    def _build_prompt(self, transformation: TransformationMap, title: str) -> str:
        milestones_str = "\n".join([f"- {m.name}: {m.description}" for m in transformation.milestones])
        return f"""
You are an expert instructional designer creating a "Master Class" curriculum.

## TransformationMap Context
- Starting: {transformation.starting_state}
- Ending: {transformation.ending_state}
- Milestones:
{milestones_str}
- Skills to Gain: {', '.join(transformation.skill_gains)}

## Goal
Design a **comprehensive, deep-dive curriculum** that feels like a $2000 course. 
We need VOLUME and DEPTH. Do not create a thin outline. 
Aim for **12-15+ distinct concepts** (Chapters) that rigorously bridge the gap from Start to End.

## Generate a CurriculumGraph (JSON):

1. **Concepts**: List 12-15+ teachable concepts (id, name, description, difficulty, estimated_time_minutes).
   - The description should be detailed (2-3 sentences).
2. **Dependencies**: Map concept_id → list of prerequisite concept_ids
3. **Practice Loops**: Activities to practice concepts (name, concept_ids, type, instructions, success_criteria)
4. **Assessments**: Ways to verify understanding (name, concept_ids, type, questions_or_tasks)
5. **Minimum Viable Mastery**: Checklist of "must be able to do" items

Return valid JSON.
"""

    def _parse_response(self, response: str, transformation: TransformationMap) -> CurriculumGraph:
        try:
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                data = json.loads(response[json_start:json_end])
                return CurriculumGraph(**data)
        except Exception as e:
            logger.warning(f"Failed to parse CurriculumArchitect response: {e}")
        
        # Fallback based on milestones
        concepts = []
        for i, milestone in enumerate(transformation.milestones):
            concepts.append(Concept(
                id=f"concept_{i+1}",
                name=milestone.name,
                description=milestone.description,
                difficulty="intermediate",
                estimated_time_minutes=30
            ))
        
        return CurriculumGraph(
            concepts=concepts,
            dependencies={c.id: [concepts[i-1].id] if i > 0 else [] for i, c in enumerate(concepts)},
            practice_loops=[
                PracticeLoop(
                    name="Core Practice",
                    concept_ids=[c.id for c in concepts],
                    type="exercise",
                    instructions="Apply the concepts from this section",
                    success_criteria="Completed all exercises"
                )
            ],
            assessments=[
                Assessment(
                    name="Self-Check",
                    concept_ids=[c.id for c in concepts],
                    type="self-check",
                    questions_or_tasks=["Can you explain the key concepts?", "Have you applied the techniques?"]
                )
            ],
            minimum_viable_mastery=transformation.skill_gains
        )
