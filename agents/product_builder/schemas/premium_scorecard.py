"""
Premium Scorecard Schema
Multi-axis scoring for premium product quality.
"""

from pydantic import BaseModel, Field
from typing import List


class PremiumScorecard(BaseModel):
    """
    Multi-axis quality score. Products must pass ALL thresholds to ship.
    """
    thinking_depth: int = Field(ge=0, le=10, description="How deeply thought-out is the content?")
    structure_curriculum: int = Field(ge=0, le=10, description="Is the learning structure sound?")
    clarity_coherence: int = Field(ge=0, le=10, description="Is everything clear and consistent?")
    delight_voice: int = Field(ge=0, le=10, description="Is it enjoyable to read?")
    practicality_actionability: int = Field(ge=0, le=10, description="Can readers take action?")
    bonus_power: int = Field(ge=0, le=10, description="Do bonuses accelerate completion?")
    packaging_quality: int = Field(ge=0, le=10, description="Is the final package polished?")
    
    # Detailed feedback per dimension
    feedback: dict[str, List[str]] = Field(
        default_factory=dict,
        description="Improvement suggestions per dimension"
    )
    
    @property
    def all_scores(self) -> List[int]:
        return [
            self.thinking_depth,
            self.structure_curriculum,
            self.clarity_coherence,
            self.delight_voice,
            self.practicality_actionability,
            self.bonus_power,
            self.packaging_quality
        ]
    
    @property
    def average(self) -> float:
        return sum(self.all_scores) / len(self.all_scores)
    
    @property
    def minimum(self) -> int:
        return min(self.all_scores)
    
    @property
    def publishable(self) -> bool:
        """Products must have no score under 8 and average ≥ 8.5"""
        return self.minimum >= 8 and self.average >= 8.5
    
    @property
    def verdict(self) -> str:
        if self.publishable:
            return "PREMIUM_SHIP"
        elif self.minimum >= 7 and self.average >= 7.5:
            return "STANDARD_SHIP"
        elif self.minimum >= 5:
            return "REVISE"
        else:
            return "REJECT"
    
    def weakest_dimensions(self, n: int = 2) -> List[str]:
        """Return the n lowest-scoring dimensions."""
        dimensions = [
            ("thinking_depth", self.thinking_depth),
            ("structure_curriculum", self.structure_curriculum),
            ("clarity_coherence", self.clarity_coherence),
            ("delight_voice", self.delight_voice),
            ("practicality_actionability", self.practicality_actionability),
            ("bonus_power", self.bonus_power),
            ("packaging_quality", self.packaging_quality)
        ]
        sorted_dims = sorted(dimensions, key=lambda x: x[1])
        return [d[0] for d in sorted_dims[:n]]
