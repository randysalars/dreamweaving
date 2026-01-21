from typing import List, Literal, Optional
from pydantic import BaseModel, Field

class VisualAsset(BaseModel):
    asset_type: Literal["text_overlay", "diagram", "image", "screen_capture"]
    description: str
    content: Optional[str] = None # For text overlays
    spec: Optional[str] = None # For diagrams (Mermaid code)

class VideoScene(BaseModel):
    scene_number: int
    duration_est: float = Field(..., description="Estimated duration in seconds")
    audio_segment: str = Field(..., description="The script/audio portion for this scene")
    visual_goal: Literal["teach", "anchor", "transition", "metaphor"]
    visuals: List[VisualAsset] = Field(default_factory=list)
    transition: Optional[str] = "cut"

class VideoPlan(BaseModel):
    """
    Detailed production plan for a video lesson.
    """
    chapter_title: str
    total_duration: float
    target_style: Literal["slide_based", "diagram_walkthrough", "kinetic_text"]
    scenes: List[VideoScene] = Field(default_factory=list)
