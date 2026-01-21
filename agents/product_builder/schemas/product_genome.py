from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from datetime import datetime

class ProductDNA(BaseModel):
    problem_class: str = Field(..., description="The fundamental problem category (e.g. 'Wealth/Traffic')")
    mental_models: List[str] = Field(default_factory=list, description="Core mental models used (e.g. 'First Principles', 'Inversion')")
    skill_primitives: List[str] = Field(default_factory=list, description="Fundamental skills taught")
    emotional_driver: str = Field(..., description="Primary emotion driving the purchase/consumption")
    difficulty_level: str = Field(..., pattern="^(Beginner|Intermediate|Advanced|Master)$")

class ProductRelationships(BaseModel):
    prerequisites: List[str] = Field(default_factory=list, description="Slugs of products that should be consumed first")
    recommended_after: List[str] = Field(default_factory=list, description="Next logical steps in the curriculum")
    bundles: List[str] = Field(default_factory=list, description="Bundle IDs this product belongs to")

class TelemetryStats(BaseModel):
    total_sales: int = 0
    refund_rate: float = 0.0
    completion_rate: float = 0.0
    avg_rating: float = 0.0
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class ProductGenome(BaseModel):
    """
    Taxonomy and Intelligence layer for the Product Catalog.
    Allows for auto-curriculum generation and smart recommendations.
    """
    product_slug: str
    product_id: str
    
    dna: ProductDNA
    relationships: ProductRelationships
    stats: TelemetryStats = Field(default_factory=TelemetryStats)
    
    tags: List[str] = Field(default_factory=list)
    deprecated: bool = False
