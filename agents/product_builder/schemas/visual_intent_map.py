"""
Visual Intent Map Schema
Maps each section to its visual needs before any images are created.
"""

from pydantic import BaseModel, Field
from typing import List, Literal, Optional


class VisualIntent(BaseModel):
    """Visual intent for a single section."""
    section_id: str = Field(description="Unique identifier for the section")
    section_title: str = Field(description="Title of the section")
    cognitive_load: Literal["low", "medium", "high"] = Field(
        description="How mentally demanding is this section?"
    )
    visual_role: Literal[
        "orientation",      # "Where am I?" - maps, overviews
        "explanation",      # Clarify complex ideas - diagrams
        "memory_anchor",    # Make it stick - metaphors
        "emotional_tone",   # Set the mood - illustrations
        "fatigue_break",    # Reduce reading exhaustion - callouts
        "none"              # No visual needed
    ] = Field(description="Primary purpose of the visual")
    
    recommended_type: Literal[
        "concept_diagram",       # Frameworks, models, systems
        "map_overview",          # Journey maps, roadmaps
        "callout",               # Pull-quotes, key ideas
        "metaphor_illustration", # Abstract concepts, mood
        "reference_graphic",     # Checklists, summaries
        "icon_decoration",       # Minimal visual break
        "none"                   # No visual
    ] = Field(description="Type of visual to create")
    
    placement: Literal[
        "section_start",     # Opening anchor
        "after_explanation", # Following dense text
        "chapter_end",       # Summary/reinforcement
        "inline",            # Within the flow
        "full_page"          # Dedicated visual page
    ] = Field(description="Where to place the visual")
    
    description: str = Field(
        description="What the visual should convey - used for generation prompts"
    )
    
    priority: Literal["must_have", "nice_to_have", "optional"] = Field(
        default="nice_to_have",
        description="How important is this visual?"
    )
    
    reuse_asset: Optional[str] = Field(
        default=None,
        description="Path to existing library asset if reusing"
    )


class VisualIntentMap(BaseModel):
    """
    Complete visual plan for a product.
    Generated AFTER NarrativeSpine, BEFORE image creation.
    """
    product_title: str
    visual_style_name: str = Field(
        description="Reference to the visual style system to use"
    )
    total_visuals_planned: int = Field(default=0)
    intents: List[VisualIntent] = Field(default_factory=list)
    
    @property
    def must_have_count(self) -> int:
        return sum(1 for i in self.intents if i.priority == "must_have")
    
    @property
    def by_type(self) -> dict:
        """Group intents by visual type."""
        result = {}
        for intent in self.intents:
            t = intent.recommended_type
            if t not in result:
                result[t] = []
            result[t].append(intent)
        return result
