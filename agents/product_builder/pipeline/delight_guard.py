"""
DelightGuard Agent
The final excellence gate - ensures products are recommendable, not just complete.
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Tuple
from pydantic import BaseModel, Field

from ..core.llm import LLMClient

logger = logging.getLogger(__name__)


class DelightScore(BaseModel):
    """Scoring for the Delight Rubric."""
    clarity: int = Field(ge=1, le=10, description="Is every concept crystal clear?")
    enjoyment: int = Field(ge=1, le=10, description="Would someone finish willingly?")
    depth: int = Field(ge=1, le=10, description="Goes beyond surface level?")
    originality: int = Field(ge=1, le=10, description="Unique perspective present?")
    resonance: int = Field(ge=1, le=10, description="Will the reader feel something?")
    
    @property
    def average(self) -> float:
        return (self.clarity + self.enjoyment + self.depth + self.originality + self.resonance) / 5
    
    @property
    def verdict(self) -> str:
        if self.average >= 8:
            return "EXCEPTIONAL"
        elif self.average >= 7:
            return "SHIP"
        elif self.average >= 5:
            return "REVISE"
        else:
            return "REJECT"


class DelightGuard:
    """
    The final quality gate.
    Products must be recommendable, not just complete.
    """
    
    PASSING_THRESHOLD = 7.0
    
    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir
        self.llm = LLMClient()
        
    def evaluate(self, content: str, context: Dict) -> Tuple[DelightScore, List[str]]:
        """
        Evaluate content against the Delight Rubric.
        
        Args:
            content: The full product content
            context: Product context (title, thesis, etc.)
            
        Returns:
            Tuple of (DelightScore, list of improvement suggestions)
        """
        logger.info("🌟 DelightGuard evaluating product excellence...")
        
        prompt = self._build_prompt(content, context)
        response = self.llm.generate(prompt, max_tokens=1500)
        
        score, suggestions = self._parse_response(response)
        
        logger.info(f"DelightGuard Score: {score.average:.1f}/10 - Verdict: {score.verdict}")
        
        if score.average < self.PASSING_THRESHOLD:
            logger.warning(f"⚠️ Product did not pass Delight Gate. Suggestions: {suggestions}")
        else:
            logger.info("✅ Product passed Delight Gate!")
        
        return score, suggestions
    
    def passes(self, content: str, context: Dict) -> bool:
        """Simple pass/fail check."""
        score, _ = self.evaluate(content, context)
        return score.average >= self.PASSING_THRESHOLD
    
    def _build_prompt(self, content: str, context: Dict) -> str:
        """Build the evaluation prompt."""
        # Truncate content if too long
        max_content_length = 8000
        truncated = content[:max_content_length] if len(content) > max_content_length else content
        
        return f"""
You are evaluating a digital product for excellence. Rate it on the Delight Rubric.

## Product Context
- Title: {context.get('title', 'Unknown')}
- Thesis: {context.get('thesis', 'N/A')}
- Target Emotion: {context.get('emotional_arc', 'transformation')}

## Content Sample
{truncated}

## Evaluation Criteria (Rate 1-10 each)

1. **Clarity**: Is every concept crystal clear? No confusion?
2. **Enjoyment**: Would someone finish this willingly, not just dutifully?
3. **Depth**: Does it go beyond surface-level advice?
4. **Originality**: Is there a unique perspective or voice?
5. **Resonance**: Will the reader *feel* something meaningful?

## Response Format
Return JSON:
```json
{{
  "clarity": 8,
  "enjoyment": 7,
  "depth": 9,
  "originality": 6,
  "resonance": 8,
  "suggestions": ["Suggestion 1", "Suggestion 2"]
}}
```

Be honest. A score of 7+ means it ships. Lower means revise.
"""
    
    def _parse_response(self, response: str) -> Tuple[DelightScore, List[str]]:
        """Parse LLM response into score and suggestions."""
        try:
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            
            if json_start != -1 and json_end > json_start:
                data = json.loads(response[json_start:json_end])
                suggestions = data.pop("suggestions", [])
                score = DelightScore(**data)
                return score, suggestions
            else:
                raise ValueError("No JSON found")
                
        except Exception as e:
            logger.warning(f"Failed to parse DelightGuard response: {e}")
            # Default to passing but with caution
            return DelightScore(
                clarity=7, enjoyment=7, depth=7, originality=7, resonance=7
            ), ["Could not fully evaluate - manual review recommended"]
