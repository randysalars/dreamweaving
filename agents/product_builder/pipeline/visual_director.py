"""
VisualDirector Agent (Simplified)
Plans essential visuals for a product - fewer is better.
Focus on high-impact, contextual visuals only.
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional

from ..schemas.visual_intent_map import VisualIntentMap, VisualIntent
from ..schemas.visual_style import VisualStyle, DREAMWEAVING_STYLE
from ..schemas.blueprint import ChapterSpec

logger = logging.getLogger(__name__)


class VisualDirector:
    """
    Visual planning intelligence - simplified for quality over quantity.
    Plans only essential visuals that add real value.
    """
    
    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir
        self.default_style = DREAMWEAVING_STYLE
        
    def plan_visuals(
        self, 
        title: str,
        chapters: List[ChapterSpec],
        style: Optional[VisualStyle] = None
    ) -> VisualIntentMap:
        """
        Generate a minimal, high-impact visual plan.
        
        Focuses on:
        - 1 cover image (required)
        - 1 journey map for orientation
        - Key chapter illustrations (only for first 2 chapters)
        """
        logger.info(f"🎨 VisualDirector planning visuals for: {title}")
        
        style = style or self.default_style
        intents = []
        
        # REQUIRED: Cover image
        intents.append(self._create_cover_intent(title, style))
        
        # OPTIONAL: Journey map (only if 5+ chapters)
        if len(chapters) >= 5:
            intents.append(self._create_journey_map_intent(title, chapters))
        
        # KEY CHAPTERS: Only first 2 chapters get illustrations
        for i, chapter in enumerate(chapters[:2]):
            intents.append(self._create_chapter_opener(i + 1, chapter, style))
        
        visual_map = VisualIntentMap(
            product_title=title,
            visual_style_name=style.name,
            total_visuals_planned=len(intents),
            intents=intents
        )
        
        logger.info(f"✅ Visual plan complete: {len(intents)} visuals planned")
        
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
            description=f"Professional product cover for '{title}'. Evocative, premium aesthetic.",
            priority="must_have"
        )
    
    def _create_journey_map_intent(self, title: str, chapters: List[ChapterSpec]) -> VisualIntent:
        """Create intent for journey overview."""
        return VisualIntent(
            section_id="journey_map",
            section_title="Your Journey",
            cognitive_load="low",
            visual_role="orientation",
            recommended_type="map_overview",
            placement="section_start",
            description=f"Visual timeline showing progression through the content.",
            priority="nice_to_have"
        )
    
    def _create_chapter_opener(
        self, 
        chapter_num: int, 
        chapter: ChapterSpec,
        style: VisualStyle
    ) -> VisualIntent:
        """Create opener for key chapters."""
        return VisualIntent(
            section_id=f"ch{chapter_num}_opener",
            section_title=chapter.title,
            cognitive_load="low",
            visual_role="orientation",
            recommended_type="metaphor_illustration",
            placement="section_start",
            description=f"Illustration for '{chapter.title}' - {chapter.purpose[:100]}",
            priority="nice_to_have"
        )
    
    def generate_image_prompts(self, visual_map: VisualIntentMap, style: VisualStyle) -> List[Dict]:
        """
        Convert visual intents into generation prompts.
        Returns list of {section_id, prompt, type}
        """
        prompts = []
        
        for intent in visual_map.intents:
            gen_type = self._map_intent_to_generator(intent.recommended_type)
            
            prompts.append({
                "section_id": intent.section_id,
                "prompt": intent.description,
                "type": gen_type,
                "priority": intent.priority
            })
        
        return prompts
    
    def _map_intent_to_generator(self, recommended_type: str) -> str:
        """Map visual intent types to generator types."""
        mapping = {
            "ai_image": "ai_image",        # Use Antigravity/OpenAI
            "timeline": "timeline",         # Template-based
            "flowchart": "flowchart",       # Template-based
            "concept": "concept",           # Template-based
            "comparison": "comparison",     # Template-based
        }
        return mapping.get(recommended_type, "ai_image")
