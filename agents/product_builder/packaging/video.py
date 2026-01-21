import logging
import re
from typing import List
from ..schemas.video import VideoPlan, VideoScene, VisualAsset

logger = logging.getLogger(__name__)

class VideoOrchestrator:
    """
    Converts a Chapter into a Video Production Plan.
    Breaks content into scenes and assigns visuals.
    """
    
    def generate_plan(self, chapter_title: str, content: str, audio_script: str) -> VideoPlan:
        """
        Synthesizes the Video Plan.
        """
        logger.info(f"Orchestrating Video Plan for: {chapter_title}")
        
        # 1. Parse Audio Script into segments (Simulation)
        # In a real app, this would use the XML structure of the SSML.
        # Here we split by newlines for a rough approximation.
        segments = [s.strip() for s in audio_script.split('\n') if len(s.strip()) > 20]
        
        scenes = []
        for i, segment in enumerate(segments):
            # Heuristic: Detect if this segment needs a diagram
            needs_diagram = "diagram" in segment.lower() or "structure" in segment.lower()
            
            visuals = []
            if needs_diagram:
                visuals.append(VisualAsset(
                    asset_type="diagram", 
                    description="Conceptual structure visualization",
                    spec="graph TD; A-->B;"
                ))
            else:
                 visuals.append(VisualAsset(
                    asset_type="text_overlay", 
                    description="Key phrase highlight",
                    content=segment[:30] + "..."
                ))
            
            scenes.append(VideoScene(
                scene_number=i+1,
                duration_est=len(segment) / 15.0, # Rough speaking rate est
                audio_segment=segment,
                visual_goal="teach" if needs_diagram else "anchor",
                visuals=visuals
            ))
            
        total_dur = sum(s.duration_est for s in scenes)
        
        return VideoPlan(
            chapter_title=chapter_title,
            total_duration=total_dur,
            target_style="diagram_walkthrough",
            scenes=scenes
        )
