from typing import List, Optional, Dict, Any, Literal
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime

class ProductPromise(BaseModel):
    headline: str = Field(..., description="The main transformation promise")
    subhead: str = Field(..., description="Clarification of who it is for and the mechanism")
    target_audience: str = Field(..., description="Specific definition of the primary reader")
    transformation_timeline: str = Field(..., description="Time to value (e.g. '72 hours')")

class PricingModel(BaseModel):
    amount: float = Field(..., description="The price of the product in USD")
    currency: str = Field(default="USD")
    model_type: Literal["fixed", "subscription", "pay_what_you_want", "love_offering"] = "fixed"
    stripe_price_id: Optional[str] = None
    love_offering_min: Optional[float] = None
    love_offering_suggested: Optional[float] = None
    love_offering_anchor: Optional[str] = None

class BuildTarget(BaseModel):
    formats: List[Literal["mdx", "pdf", "epub", "audio", "video"]] = Field(default=["mdx", "pdf"])
    target_page_count: int = Field(default=100, ge=20)
    publish_path: str = Field(..., description="Target path in the salarsu store (e.g. /products/my-book)")

class MarketingHooks(BaseModel):
    core_angles: List[str] = Field(default_factory=list, description="3-7 core marketing angles")
    objections_to_crush: List[str] = Field(default_factory=list)
    
class AudiencePersona(BaseModel):
    current_state: str
    desired_state: str
    constraints: List[str]
    fears: List[str]
    language_patterns: List[str]

class ChapterSpec(BaseModel):
    title: str
    purpose: str
    key_takeaways: List[str]
    estimated_pages: int
    required_diagrams: List[str] = Field(default_factory=list)
    source_refs: List[str] = Field(default_factory=list, description="IDs of knowledge artifacts to reference")

class ProductBlueprint(BaseModel):
    """
    The Constitution for a Product Build.
    Once locked, this schema dictates every session of the Product Builder.
    """
    title: str
    slug: str
    version: str = "1.0.0"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    promise: ProductPromise
    audience: AudiencePersona
    voice_rules: List[str] = Field(..., description="Style and tone constraints")
    
    chapter_map: List[ChapterSpec]
    
    bonuses: List[Dict[str, str]] = Field(default_factory=list, description="List of bonus modules")
    marketing: MarketingHooks
    pricing: PricingModel
    build_targets: BuildTarget
    
    status: Literal["draft", "locked", "in_progress", "completed"] = "draft"
