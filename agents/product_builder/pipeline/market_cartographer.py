"""
Market Cartographer Agent
Generates the PositioningBrief - the foundational market positioning artifact.
"""

import logging
import json
from pathlib import Path
from typing import Optional

from ..core.llm import LLMClient
from ..core.intelligence import DemandSignal
from ..schemas.positioning_brief import PositioningBrief, AudienceProfile, Objection

logger = logging.getLogger(__name__)


class MarketCartographer:
    """
    Analyzes market demand and generates the PositioningBrief.
    This is the FIRST agent in the studio pipeline.
    """
    
    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir
        self.llm = LLMClient()
        
    def generate(self, signal: DemandSignal, title: str) -> PositioningBrief:
        """
        Generate PositioningBrief from market intelligence.
        
        Args:
            signal: The demand signal from market research
            title: Working product title
            
        Returns:
            PositioningBrief: The market positioning contract
        """
        logger.info(f"🗺️ MarketCartographer mapping position for: {title}")
        
        prompt = self._build_prompt(signal, title)
        response = self.llm.generate(prompt, max_tokens=2000)
        brief = self._parse_response(response, signal, title)
        
        logger.info(f"✅ PositioningBrief generated: {brief.core_promise[:60]}...")
        return brief
    
    def _build_prompt(self, signal: DemandSignal, title: str) -> str:
        return f"""
You are a market positioning expert. Analyze this product opportunity and generate a PositioningBrief.

## Product Opportunity
- Topic: {signal.topic}
- Key Themes: {', '.join(signal.key_themes)}
- Market Gaps: {', '.join(signal.missing_angles)}
- Evidence Score: {signal.evidence_score}
- Title: {title}

## Generate a PositioningBrief (JSON format):

1. **Audience**: Who is this for? (persona, pain points, current solutions, sophistication, buying triggers)
2. **Core Promise**: What transformation will they experience?
3. **Differentiator**: Why this vs. alternatives?
4. **Objections**: 3-5 common doubts and how we preempt them
5. **Competing Alternatives**: What else could they buy/do?
6. **Positioning Statement**: One paragraph elevator pitch

Return valid JSON matching this structure.
"""

    def _parse_response(self, response: str, signal: DemandSignal, title: str) -> PositioningBrief:
        """Parse LLM response into PositioningBrief."""
        try:
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                data = json.loads(response[json_start:json_end])
                return PositioningBrief(**data)
        except Exception as e:
            logger.warning(f"Failed to parse MarketCartographer response: {e}")
        
        # Fallback
        return PositioningBrief(
            audience=AudienceProfile(
                primary_persona=f"Someone struggling with {signal.topic}",
                pain_points=signal.missing_angles[:3] if signal.missing_angles else ["Lack of clarity"],
                current_solutions=["Books", "Courses", "YouTube"],
                sophistication_level="intermediate",
                buying_triggers=["Frustration with status quo", "Ready for change"]
            ),
            core_promise=f"Master {signal.topic} with a proven system",
            differentiator="Practical, actionable, and designed for real results",
            objections=[
                Objection(objection="Will this work for me?", preemption="Designed for your specific situation"),
                Objection(objection="I don't have time", preemption="Built for busy professionals")
            ],
            competing_alternatives=["Generic books", "Expensive courses", "Trial and error"],
            positioning_statement=f"{title} is the definitive guide to mastering {signal.topic}."
        )
