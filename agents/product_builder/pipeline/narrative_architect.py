"""
NarrativeArchitect Agent
Transforms ProductIntelligence into a guided journey structure.
"""

import logging
import json
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field

from ..core.llm import LLMClient
from ..schemas.product_intelligence import ProductIntelligence
from ..schemas.blueprint import ChapterSpec

logger = logging.getLogger(__name__)


class InsightChapter(BaseModel):
    """A chapter designed for narrative flow."""
    chapter_number: int
    title: str
    purpose: str = Field(description="Why this chapter exists")
    core_insight: str = Field(description="The one thing they'll understand")
    target_emotion: str = Field(description="What they should feel after reading")
    transition_hook: str = Field(description="How this leads to the next chapter")


class NarrativeSpine(BaseModel):
    """The story structure of the product."""
    opening_tension: str = Field(description="What's at stake if reader does nothing")
    orientation: str = Field(description="The promise of the journey")
    insight_chapters: List[InsightChapter]
    integration: str = Field(description="How all pieces connect")
    closure_activation: str = Field(description="Specific first step, not 'good luck'")


class NarrativeArchitect:
    """
    Transforms a flat chapter list into a narrative journey.
    """
    
    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir
        self.llm = LLMClient()
        self.template_path = templates_dir / "narrative_architect.md"
        
    def design(self, intelligence: ProductIntelligence, chapters: List[ChapterSpec]) -> NarrativeSpine:
        """
        Design the narrative spine for the product.
        
        Args:
            intelligence: The ProductIntelligence from ProductMind
            chapters: The initial chapter map
            
        Returns:
            NarrativeSpine: The story structure
        """
        logger.info(f"🏗️ NarrativeArchitect designing spine for {len(chapters)} chapters...")
        
        # Load template
        template = self._load_template()
        
        # Format chapter map
        chapter_map = "\n".join([
            f"- Chapter {i+1}: {ch.title} — {ch.purpose}"
            for i, ch in enumerate(chapters)
        ])
        
        # Build context
        context = {
            "thesis": intelligence.thesis,
            "emotional_arc": ", ".join(intelligence.emotional_arc),
            "core_promise": intelligence.core_promise,
            "reader_energy": intelligence.avatar.energy_level,
            "chapter_map": chapter_map,
        }
        
        # Render prompt
        prompt = template.format(**context)
        
        # Call LLM
        response = self.llm.generate(prompt, max_tokens=2500)
        
        # Parse response
        spine = self._parse_response(response, chapters)
        
        logger.info(f"✅ NarrativeSpine designed. Opening: {spine.opening_tension[:60]}...")
        
        return spine
    
    def _load_template(self) -> str:
        """Load the NarrativeArchitect prompt template."""
        if self.template_path.exists():
            return self.template_path.read_text()
        else:
            logger.warning(f"Template not found at {self.template_path}")
            return "Design a narrative spine for: {thesis}\nChapters: {chapter_map}"
    
    def _parse_response(self, response: str, chapters: List[ChapterSpec]) -> NarrativeSpine:
        """Parse LLM response into NarrativeSpine schema."""
        try:
            # Extract JSON
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
                return NarrativeSpine(**data)
            else:
                raise ValueError("No JSON found in response")
                
        except Exception as e:
            logger.warning(f"Failed to parse NarrativeArchitect response: {e}. Using defaults.")
            return self._default_spine(chapters)
    
    def _default_spine(self, chapters: List[ChapterSpec]) -> NarrativeSpine:
        """Generate sensible defaults if LLM parsing fails."""
        insight_chapters = [
            InsightChapter(
                chapter_number=i + 1,
                title=ch.title,
                purpose=ch.purpose,
                core_insight=ch.key_takeaways[0] if ch.key_takeaways else "Core understanding",
                target_emotion="clarity",
                transition_hook="Building on this foundation..."
            )
            for i, ch in enumerate(chapters)
        ]
        
        return NarrativeSpine(
            opening_tension="Without this knowledge, you risk staying stuck in the same patterns.",
            orientation="This journey will take you from confusion to confident action.",
            insight_chapters=insight_chapters,
            integration="Together, these principles form a complete system for transformation.",
            closure_activation="Your first step: Apply the core insight from Chapter 1 today."
        )
