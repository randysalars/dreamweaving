"""
Image Generator
Handles AI image generation and diagram rendering.
"""

import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, List, Dict
from dataclasses import dataclass

from ..schemas.visual_style import VisualStyle

logger = logging.getLogger(__name__)


@dataclass
class GeneratedImage:
    """Result of image generation."""
    section_id: str
    path: str
    type: str
    success: bool
    error: Optional[str] = None


class ImageGenerator:
    """
    Generates images for product visuals.
    Supports: AI images, Mermaid diagrams, template graphics.
    """
    
    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path("./generated_visuals")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_batch(
        self, 
        prompts: List[Dict], 
        style: VisualStyle
    ) -> List[GeneratedImage]:
        """
        Generate all visuals from a list of prompts.
        
        Args:
            prompts: List of {section_id, prompt, type, priority}
            style: Visual style to use
            
        Returns:
            List of GeneratedImage results
        """
        logger.info(f"🖼️ Generating {len(prompts)} visuals...")
        
        results = []
        
        for prompt_spec in prompts:
            section_id = prompt_spec["section_id"]
            prompt = prompt_spec["prompt"]
            gen_type = prompt_spec["type"]
            
            try:
                if gen_type == "ai_image":
                    path = self.generate_ai_image(section_id, prompt, style)
                elif gen_type == "mermaid_diagram":
                    path = self.generate_mermaid_diagram(section_id, prompt)
                elif gen_type == "journey_map":
                    path = self.generate_journey_map(section_id, prompt)
                else:
                    path = self.generate_placeholder(section_id, prompt)
                
                results.append(GeneratedImage(
                    section_id=section_id,
                    path=str(path),
                    type=gen_type,
                    success=True
                ))
                
            except Exception as e:
                logger.error(f"Failed to generate {section_id}: {e}")
                results.append(GeneratedImage(
                    section_id=section_id,
                    path="",
                    type=gen_type,
                    success=False,
                    error=str(e)
                ))
        
        successful = sum(1 for r in results if r.success)
        logger.info(f"✅ Generated {successful}/{len(prompts)} visuals")
        
        return results
    
    def generate_ai_image(
        self, 
        section_id: str, 
        prompt: str, 
        style: VisualStyle
    ) -> Path:
        """
        Generate an image prompt for Antigravity processing.
        
        This creates a .image_prompt.md file that can be processed by 
        Antigravity's generate_image tool via the text interface.
        
        Args:
            section_id: Identifier for this image
            prompt: Base prompt describing the image
            style: Visual style to apply
            
        Returns:
            Path to the generated prompt file or placeholder
        """
        prompt_path = self.output_dir / f"{section_id}.image_prompt.md"
        placeholder_path = self.output_dir / f"{section_id}_placeholder.txt"
        
        # Build enhanced prompt with style information
        style_additions = []
        if style and hasattr(style, 'color_scheme'):
            style_additions.append(f"Color scheme: {style.color_scheme}")
        if style and hasattr(style, 'mood'):
            style_additions.append(f"Mood: {style.mood}")
        
        enhanced_prompt = f"""# Image Generation Prompt: {section_id}

## Instructions for Antigravity

Use the `generate_image` tool to create this image.

**Image Name:** {section_id}
**Save To:** {self.output_dir}/{section_id}.png

---

## Prompt

{prompt}

{chr(10).join(style_additions) if style_additions else ''}

## Style Guidelines

- Professional, clean design
- Suitable for digital product materials
- Abstract or conceptual preferred over photorealistic
- Modern, minimalist aesthetic

---

## After Generation

Once the image is generated, it will be saved to:
`{self.output_dir}/{section_id}.png`

The compilation pipeline will automatically detect and include this image.
"""
        
        # Save the prompt file
        prompt_path.write_text(enhanced_prompt)
        logger.info(f"📝 Image prompt created: {section_id}")
        logger.info(f"   → Run Antigravity with: generate_image for {section_id}")
        
        # Also create a placeholder to show the prompt is ready
        placeholder_path.write_text(f"PENDING: {section_id}\n\nPrompt file: {prompt_path}\n\nDescription:\n{prompt}")
        
        return prompt_path

    
    def generate_mermaid_diagram(self, section_id: str, description: str) -> Path:
        """
        Generate a Mermaid diagram from description.
        """
        output_path = self.output_dir / f"{section_id}.png"
        
        # Generate Mermaid code from description
        mermaid_code = self._description_to_mermaid(description)
        
        # Try to render with mmdc (mermaid-cli)
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as f:
                f.write(mermaid_code)
                mmd_path = f.name
            
            result = subprocess.run(
                ["mmdc", "-i", mmd_path, "-o", str(output_path), "-b", "transparent"],
                capture_output=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Mermaid diagram generated: {section_id}")
                return output_path
            else:
                raise Exception(f"mmdc failed: {result.stderr.decode()}")
                
        except FileNotFoundError:
            logger.warning("mermaid-cli not installed, saving as text")
            # Save mermaid code as text for manual rendering
            text_path = self.output_dir / f"{section_id}.mmd"
            text_path.write_text(mermaid_code)
            return text_path
        except Exception as e:
            logger.warning(f"Diagram generation failed: {e}")
            return self.generate_placeholder(section_id, description)
    
    def generate_journey_map(self, section_id: str, description: str) -> Path:
        """Generate a journey/roadmap visualization."""
        # Extract chapter names from description
        mermaid_code = """
graph LR
    A[Start] --> B[Foundation]
    B --> C[Application]
    C --> D[Mastery]
    D --> E[Transformation]
    
    style A fill:#9F7AEA,stroke:#553C9A
    style E fill:#48BB78,stroke:#276749
"""
        return self._save_mermaid(section_id, mermaid_code)
    
    def generate_placeholder(self, section_id: str, description: str) -> Path:
        """Generate a placeholder for missing visuals."""
        output_path = self.output_dir / f"{section_id}_placeholder.txt"
        output_path.write_text(f"PLACEHOLDER: {section_id}\n\nDescription:\n{description}")
        logger.info(f"📝 Placeholder created: {section_id}")
        return output_path
    
    def _description_to_mermaid(self, description: str) -> str:
        """Convert a description to basic Mermaid code."""
        # Simple fallback - create a basic flowchart
        return """
graph TD
    A[Concept] --> B[Understanding]
    B --> C[Application]
    C --> D[Mastery]
    
    style A fill:#4A5568,stroke:#2D3748
    style D fill:#9F7AEA,stroke:#553C9A
"""
    
    def _save_mermaid(self, section_id: str, code: str) -> Path:
        """Save mermaid code and attempt to render."""
        mmd_path = self.output_dir / f"{section_id}.mmd"
        mmd_path.write_text(code)
        return mmd_path


class DiagramRenderer:
    """
    Specialized renderer for diagrams and charts.
    """
    
    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path("./generated_visuals/diagrams")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def render_concept_diagram(self, spec: Dict) -> Path:
        """Render a concept/framework diagram."""
        # Implementation would use Mermaid or custom SVG generation
        pass
    
    def render_checklist(self, items: List[str], title: str) -> Path:
        """Render a styled checklist graphic."""
        # Implementation would generate styled HTML -> PNG
        pass
    
    def render_comparison_table(self, data: Dict) -> Path:
        """Render a comparison/feature table."""
        pass
