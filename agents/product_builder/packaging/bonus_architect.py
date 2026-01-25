"""
BonusArchitect Agent
Designs bonuses as completion catalysts, not random extras.
"""

import logging
import json
from pathlib import Path
from typing import List

from ..core.llm import LLMClient
from ..schemas.product_intelligence import ProductIntelligence
from ..schemas.blueprint import ChapterSpec
from ..schemas.bonus_plan import BonusPlan, Bonus

logger = logging.getLogger(__name__)


class BonusArchitect:
    """
    Designs bonuses that map to friction points in the main product.
    Every bonus must earn its place.
    """
    
    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir
        self.llm = LLMClient()
        
    def design(self, intelligence: ProductIntelligence, chapters: List[ChapterSpec]) -> BonusPlan:
        """
        Design a bonus plan based on product intelligence and chapters.
        
        Args:
            intelligence: The ProductIntelligence from ProductMind
            chapters: The chapter list
            
        Returns:
            BonusPlan: Strategically designed bonuses
        """
        logger.info("🎁 BonusArchitect designing completion catalysts...")
        
        # Identify friction points
        friction_points = self._identify_friction_points(chapters)
        
        # Design bonuses for each category
        bonuses = []
        
        # 1. Clarity Bonus (helps understanding)
        clarity_bonus = self._design_clarity_bonus(intelligence, friction_points)
        if clarity_bonus:
            bonuses.append(clarity_bonus)
        
        # 2. Application Bonus (helps doing)
        application_bonus = self._design_application_bonus(intelligence, chapters)
        if application_bonus:
            bonuses.append(application_bonus)
        
        # 3. Reinforcement Bonus (helps remembering)
        reinforcement_bonus = self._design_reinforcement_bonus(intelligence)
        if reinforcement_bonus:
            bonuses.append(reinforcement_bonus)

        # 4. CUSTOM RESTORATION: Financial Freedom Specifics
        # (Restoring content requested by user that was "lost" in previous runs)
        # Check thesis or core_promise since core_topic isn't in ProductIntelligence schema
        topic_check = (intelligence.thesis + intelligence.core_promise).lower()
        if "financial freedom" in topic_check:
            logger.info("ℹ️ Restoring specific Financial Freedom bonuses...")
            bonuses.append(Bonus(
                type="deep_dive",
                title="The Recession-Proof Investing Guide",
                format="pdf",
                description="How to turn market crashes into wealth events.",
                target_friction="Fear of losing money",
                estimated_pages=10
            ))
            bonuses.append(Bonus(
                type="deep_dive",
                title="The Salary Negotiation Blackbook",
                format="pdf",
                description="Scripts to add $10k to your salary.",
                target_friction="Income ceiling",
                estimated_pages=8
            ))
        
        plan = BonusPlan(
            bonuses=bonuses,
            total_value_narrative=self._create_value_narrative(bonuses, intelligence)
        )
        
        logger.info(f"✅ BonusPlan designed with {len(bonuses)} bonuses.")
        return plan
    
    def _identify_friction_points(self, chapters: List[ChapterSpec]) -> List[str]:
        """Identify where readers might struggle."""
        friction = []
        for ch in chapters:
            # Chapters with complex topics or many takeaways = friction
            if len(ch.key_takeaways) > 3:
                friction.append(f"{ch.title}: Complex concepts")
            if any(word in ch.purpose.lower() for word in ["implement", "apply", "build", "create"]):
                friction.append(f"{ch.title}: Action required")
        return friction if friction else ["General application", "Concept integration"]
    
    def _design_clarity_bonus(self, intelligence: ProductIntelligence, friction_points: List[str]) -> Bonus:
        """Design a bonus that clarifies understanding."""
        return Bonus(
            type="clarity",
            title="Quick Reference Guide",
            format="pdf",
            description="One-page summary of key concepts and definitions for easy reference",
            target_friction=friction_points[0] if friction_points else "Core concepts",
            estimated_pages=3
        )
    
    def _design_application_bonus(self, intelligence: ProductIntelligence, chapters: List[ChapterSpec]) -> Bonus:
        """Design a bonus that helps application."""
        return Bonus(
            type="application",
            title="Action Workbook",
            format="worksheet",
            description="Step-by-step exercises to apply each chapter's insights",
            target_friction="Turning knowledge into action",
            estimated_pages=15
        )
    
    def _design_reinforcement_bonus(self, intelligence: ProductIntelligence) -> Bonus:
        """Design a bonus for emotional reinforcement."""
        return Bonus(
            type="reinforcement",
            title="Guided Reflection Audio",
            format="audio",
            description="10-minute guided reflection to internalize the transformation",
            target_friction="Making it stick",
            estimated_pages=10  # minutes for audio
        )
    
    def _create_value_narrative(self, bonuses: List[Bonus], intelligence: ProductIntelligence) -> str:
        """Create the value proposition for the bonus package."""
        total_items = len(bonuses)
        formats = set(b.format for b in bonuses)
        
        return (
            f"Plus {total_items} exclusive bonuses designed to accelerate your {intelligence.transformation.after_state.lower()} journey. "
            f"Includes {', '.join(formats)} resources worth over $97."
        )
