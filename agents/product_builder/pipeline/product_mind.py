"""
ProductMind Agent
The deep thinking layer that generates ProductIntelligence before any writing begins.
"""

import logging
import json
from pathlib import Path
from typing import Optional

from ..core.llm import LLMClient
from ..core.intelligence import DemandSignal
from ..schemas.product_intelligence import ProductIntelligence, ReaderAvatar, TransformationMap

logger = logging.getLogger(__name__)


class ProductMind:
    """
    Generates the strategic intelligence layer for a product.
    This MUST run before any content creation.
    """
    
    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir
        self.llm = LLMClient()
        self.template_path = templates_dir / "product_mind.md"
        
    def generate(self, signal: DemandSignal, title: str) -> ProductIntelligence:
        """
        Generate ProductIntelligence from a DemandSignal.
        
        Args:
            signal: The market intelligence signal
            title: Working title for the product
            
        Returns:
            ProductIntelligence: The deep thinking artifact
        """
        logger.info(f"🧠 ProductMind activating for: {title}")
        
        # Load template
        template = self._load_template()
        
        # Build context
        context = {
            "topic": signal.topic,
            "key_themes": ", ".join(signal.key_themes),
            "missing_angles": ", ".join(signal.missing_angles),
            "title": title,
        }
        
        # Render prompt
        prompt = template.format(**context)
        
        # Call LLM
        response = self.llm.generate(prompt, max_tokens=2000)
        
        # Parse response
        intelligence = self._parse_response(response, signal, title)
        
        logger.info(f"✅ ProductIntelligence generated. Thesis: {intelligence.thesis[:80]}...")
        
        return intelligence
    
    def _load_template(self) -> str:
        """Load the ProductMind prompt template."""
        if self.template_path.exists():
            return self.template_path.read_text()
        else:
            logger.warning(f"Template not found at {self.template_path}, using fallback.")
            return self._fallback_template()
    
    def _parse_response(self, response: str, signal: DemandSignal, title: str) -> ProductIntelligence:
        """Parse LLM response into ProductIntelligence schema."""
        try:
            # Try to extract JSON from response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
                return ProductIntelligence(**data)
            else:
                raise ValueError("No JSON found in response")
                
        except Exception as e:
            logger.warning(f"Failed to parse ProductMind response: {e}. Using defaults.")
            return self._default_intelligence(signal, title)
    
    def _default_intelligence(self, signal: DemandSignal, title: str) -> ProductIntelligence:
        """Generate sensible defaults if LLM parsing fails."""
        return ProductIntelligence(
            avatar=ReaderAvatar(
                beliefs=["I need better systems", "Success requires hard work"],
                fears=["Falling behind", "Making wrong decisions"],
                desires=["Financial freedom", "Clarity and confidence"],
                energy_level="neutral",
                sophistication="intermediate"
            ),
            transformation=TransformationMap(
                before_state=f"Confused about {signal.topic}",
                after_state=f"Confident and equipped to master {signal.topic}",
                key_shifts=signal.key_themes[:3] if signal.key_themes else ["Mindset shift", "New skills", "Clear action plan"]
            ),
            emotional_arc=["curiosity", "hope", "challenge", "breakthrough", "empowerment"],
            thesis=f"This product exists because too many people struggle with {signal.topic} without a clear path forward.",
            core_promise=f"By the end, you will have a clear, actionable framework for {signal.topic}.",
            anti_goals=["Not a quick fix", "Not academic theory", "Not one-size-fits-all"]
        )
    
    def _fallback_template(self) -> str:
        """Minimal fallback template."""
        return """
You are analyzing a product idea. Generate a ProductIntelligence JSON object.

Topic: {topic}
Themes: {key_themes}
Title: {title}

Respond with JSON only.
"""
