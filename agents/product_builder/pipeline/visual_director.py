"""
VisualDirector Agent
Plans all visuals for a product based on content and narrative structure.
"""

import logging
import json
from pathlib import Path
from typing import List, Dict, Optional

from ..core.llm import LLMClient
from ..schemas.visual_intent_map import VisualIntentMap, VisualIntent
from ..schemas.visual_style import VisualStyle, DREAMWEAVING_STYLE
from ..schemas.blueprint import ChapterSpec

logger = logging.getLogger(__name__)


class VisualDirector:
    """
    The visual planning intelligence.
    Reads content structure and decides what to visualize, how, and where.
    """
    
    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir
        self.llm = LLMClient()
        self.default_style = DREAMWEAVING_STYLE
        
    def plan_visuals(
        self, 
        title: str,
        chapters: List[ChapterSpec],
        style: Optional[VisualStyle] = None
    ) -> VisualIntentMap:
        """
        Generate a complete visual plan for the product.
        
        Args:
            title: Product title
            chapters: List of chapter specifications
            style: Visual style to use (defaults to Dreamweaving)
            
        Returns:
            VisualIntentMap with all visual intents
        """
        logger.info(f"🎨 VisualDirector planning visuals for: {title}")
        
        style = style or self.default_style
        intents = []
        
        # Add product-level visuals
        intents.append(self._create_cover_intent(title, style))
        intents.append(self._create_journey_map_intent(title, chapters))
        
        # Plan visuals for each chapter
        for i, chapter in enumerate(chapters):
            chapter_intents = self._plan_chapter_visuals(i + 1, chapter, style)
            intents.extend(chapter_intents)
        
        # Add closing visual
        intents.append(self._create_closing_intent(title, style))
        
        visual_map = VisualIntentMap(
            product_title=title,
            visual_style_name=style.name,
            total_visuals_planned=len([i for i in intents if i.recommended_type != "none"]),
            intents=intents
        )
        
        logger.info(f"✅ Visual plan complete: {visual_map.total_visuals_planned} visuals planned")
        logger.info(f"   Must-have: {visual_map.must_have_count}")
        
        return visual_map
    
    def _create_cover_intent(self, title: str, style: VisualStyle) -> VisualIntent:
        """Create intent for cover illustration."""
        return VisualIntent(
            section_id="cover",
            section_title="Cover",
            cognitive_load="low",
            visual_role="emotional_tone",
            recommended_type="metaphor_illustration",
            placement="full_page",
            description=f"Evocative cover illustration for '{title}'. {style.mood[0].title()} and {style.mood[1]}. Central visual metaphor representing transformation.",
            priority="must_have"
        )
    
    def _create_journey_map_intent(self, title: str, chapters: List[ChapterSpec]) -> VisualIntent:
        """Create intent for journey overview map."""
        chapter_names = [ch.title for ch in chapters]
        return VisualIntent(
            section_id="journey_map",
            section_title="Your Journey",
            cognitive_load="low",
            visual_role="orientation",
            recommended_type="map_overview",
            placement="section_start",
            description=f"Visual roadmap showing the journey through: {', '.join(chapter_names[:5])}. Shows progression from start to transformation.",
            priority="must_have"
        )
    
    def _create_closing_intent(self, title: str, style: VisualStyle) -> VisualIntent:
        """Create intent for closing visual."""
        return VisualIntent(
            section_id="closing",
            section_title="Closing",
            cognitive_load="low",
            visual_role="emotional_tone",
            recommended_type="metaphor_illustration",
            placement="chapter_end",
            description=f"Final inspiring illustration representing completion and new beginning. {style.mood[-1].title()} tone.",
            priority="nice_to_have"
        )
    
    def _plan_chapter_visuals(
        self, 
        chapter_num: int, 
        chapter: ChapterSpec,
        style: VisualStyle
    ) -> List[VisualIntent]:
        """Plan visuals for a single chapter."""
        intents = []
        
        # Determine cognitive load based on purpose
        load = self._assess_cognitive_load(chapter)
        
        # Chapter opener (always)
        intents.append(VisualIntent(
            section_id=f"ch{chapter_num}_opener",
            section_title=chapter.title,
            cognitive_load=load,
            visual_role="orientation",
            recommended_type="metaphor_illustration" if chapter_num <= 3 else "callout",
            placement="section_start",
            description=f"Chapter opener for '{chapter.title}'. Sets the tone for: {chapter.purpose}",
            priority="must_have" if chapter_num <= 2 else "nice_to_have"
        ))
        
        # If high cognitive load, add explanation diagram
        if load == "high":
            intents.append(VisualIntent(
                section_id=f"ch{chapter_num}_diagram",
                section_title=f"{chapter.title} - Concept",
                cognitive_load="high",
                visual_role="explanation",
                recommended_type="concept_diagram",
                placement="after_explanation",
                description=f"Diagram explaining the core concept of {chapter.title}. Shows relationships between: {', '.join(chapter.key_takeaways[:3])}",
                priority="must_have"
            ))
        
        # Chapter summary/key insight
        if len(chapter.key_takeaways) >= 2:
            intents.append(VisualIntent(
                section_id=f"ch{chapter_num}_summary",
                section_title=f"{chapter.title} - Key Points",
                cognitive_load="low",
                visual_role="memory_anchor",
                recommended_type="reference_graphic",
                placement="chapter_end",
                description=f"Visual summary of key takeaways: {', '.join(chapter.key_takeaways[:3])}",
                priority="nice_to_have"
            ))
        
        return intents
    
    def _assess_cognitive_load(self, chapter: ChapterSpec) -> str:
        """Assess the cognitive load of a chapter."""
        # High load indicators
        high_load_keywords = ["framework", "system", "process", "model", "architecture", "complex"]
        
        purpose_lower = chapter.purpose.lower()
        title_lower = chapter.title.lower()
        
        if any(kw in purpose_lower or kw in title_lower for kw in high_load_keywords):
            return "high"
        elif len(chapter.key_takeaways) > 3:
            return "medium"
        else:
            return "low"
    
    def generate_image_prompts(self, visual_map: VisualIntentMap, style: VisualStyle) -> List[Dict]:
        """
        Convert visual intents into generation prompts.
        
        Returns list of {section_id, prompt, type}
        """
        prompts = []
        
        for intent in visual_map.intents:
            if intent.recommended_type == "none":
                continue
            
            if intent.recommended_type == "metaphor_illustration":
                prompt = style.build_image_prompt(intent.description)
                prompts.append({
                    "section_id": intent.section_id,
                    "prompt": prompt,
                    "type": "ai_image",
                    "priority": intent.priority
                })
            
            elif intent.recommended_type == "concept_diagram":
                prompts.append({
                    "section_id": intent.section_id,
                    "prompt": intent.description,
                    "type": "mermaid_diagram",
                    "priority": intent.priority
                })
            
            elif intent.recommended_type in ["callout", "reference_graphic"]:
                prompts.append({
                    "section_id": intent.section_id,
                    "prompt": intent.description,
                    "type": "template_graphic",
                    "priority": intent.priority
                })
            
            elif intent.recommended_type == "map_overview":
                prompts.append({
                    "section_id": intent.section_id,
                    "prompt": intent.description,
                    "type": "journey_map",
                    "priority": intent.priority
                })
        
        return prompts
