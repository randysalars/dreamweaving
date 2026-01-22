"""
Visual Style Schema
Defines the visual language for consistent product aesthetics.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class ColorPalette(BaseModel):
    """Color scheme for visuals."""
    primary: str = Field(description="Primary color (hex)")
    secondary: str = Field(description="Secondary color (hex)")
    accent: str = Field(description="Accent color (hex)")
    background: str = Field(description="Background color (hex)")
    text: str = Field(description="Text color (hex)")
    muted: str = Field(description="Muted/subtle color (hex)")
    
    @property
    def all_colors(self) -> List[str]:
        return [self.primary, self.secondary, self.accent, 
                self.background, self.text, self.muted]


class VisualStyle(BaseModel):
    """
    Complete visual style system for a product line.
    Ensures all visuals look cohesive.
    """
    name: str = Field(description="Style name (e.g., 'Dreamweaving Ethereal')")
    description: str = Field(description="Brief description of the aesthetic")
    
    # Colors
    colors: ColorPalette
    
    # Art Direction
    art_style: str = Field(
        description="Overall visual style",
        examples=["minimalist line art", "ethereal watercolor", 
                  "modern geometric", "hand-drawn sketch"]
    )
    
    mood: List[str] = Field(
        description="3-5 mood descriptors",
        examples=[["calm", "contemplative", "hopeful", "grounded"]]
    )
    
    lighting: str = Field(
        default="soft ambient",
        description="Lighting style for illustrations"
    )
    
    # Constraints
    banned_elements: List[str] = Field(
        description="Elements to avoid",
        examples=[["photorealistic faces", "busy patterns", 
                   "harsh shadows", "neon colors"]]
    )
    
    # Components
    icon_set: str = Field(
        default="phosphor",
        description="Icon library to use"
    )
    
    diagram_style: str = Field(
        default="clean-modern",
        description="Style for diagrams and charts"
    )
    
    typography: str = Field(
        default="modern-serif",
        description="Typography family"
    )
    
    # AI Generation
    base_prompt_prefix: str = Field(
        description="Prefix added to all AI image generation prompts"
    )
    
    base_prompt_suffix: str = Field(
        description="Suffix/negative prompt for AI generation"
    )
    
    def build_image_prompt(self, description: str) -> str:
        """Build a complete image generation prompt."""
        return f"{self.base_prompt_prefix} {description} {self.base_prompt_suffix}"


# Default styles
DREAMWEAVING_STYLE = VisualStyle(
    name="Dreamweaving Ethereal",
    description="Soft, contemplative visuals that evoke inner journeys and transformation",
    colors=ColorPalette(
        primary="#4A5568",      # Warm gray
        secondary="#718096",    # Medium gray
        accent="#9F7AEA",       # Soft purple
        background="#FAF5FF",   # Light lavender
        text="#2D3748",         # Dark gray
        muted="#A0AEC0"         # Muted gray
    ),
    art_style="ethereal watercolor with soft edges",
    mood=["contemplative", "hopeful", "grounded", "peaceful", "transformative"],
    lighting="soft golden hour",
    banned_elements=[
        "photorealistic faces",
        "harsh shadows",
        "neon colors",
        "busy patterns",
        "corporate imagery",
        "clipart style",
        "3D renders"
    ],
    icon_set="phosphor-light",
    diagram_style="minimal-organic",
    typography="elegant-serif",
    base_prompt_prefix="Ethereal, contemplative illustration in soft watercolor style. Peaceful, transformative mood. Subtle light rays. Muted purple and gold accents.",
    base_prompt_suffix="--no text, words, letters, photorealistic, harsh shadows, neon, busy, cluttered, corporate"
)

MODERN_EDITORIAL_STYLE = VisualStyle(
    name="Modern Editorial",
    description="Clean, professional visuals for business and practical content",
    colors=ColorPalette(
        primary="#1A365D",      # Navy
        secondary="#2B6CB0",    # Blue
        accent="#ED8936",       # Orange
        background="#FFFFFF",   # White
        text="#1A202C",         # Near black
        muted="#718096"         # Gray
    ),
    art_style="clean geometric with bold lines",
    mood=["confident", "professional", "clear", "actionable"],
    lighting="bright even",
    banned_elements=[
        "photorealistic faces",
        "gradients",
        "drop shadows",
        "decorative swirls",
        "stock photo style"
    ],
    icon_set="feather",
    diagram_style="clean-modern",
    typography="geometric-sans",
    base_prompt_prefix="Modern minimalist illustration. Clean geometric shapes. Professional, confident mood. Limited color palette.",
    base_prompt_suffix="--no text, words, gradients, photorealistic, busy, decorative"
)
