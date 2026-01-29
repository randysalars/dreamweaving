"""
Code Visuals Generator (Simplified)
Generates charts, diagrams, and data visualizations using local Python libraries.
Template-based only - no LLM dependency.
"""

import logging
import re
import sys
import subprocess
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)


class CodeVisualsGenerator:
    """
    Generates PNGs from text descriptions using Matplotlib/Seaborn.
    Uses template-based generation only (no LLM/API calls).
    """
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir.resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_batch(self, visuals: List[Dict]) -> List[Dict]:
        """
        Process a batch of visual requests.
        visuals: List of {section_id, prompt, type}
        """
        results = []
        for v in visuals:
            try:
                path = self.generate(v['section_id'], v['prompt'], v.get('type', 'chart'))
                results.append({
                    "section_id": v['section_id'],
                    "path": str(path),
                    "success": True
                })
            except Exception as e:
                logger.error(f"Failed to generate code visual {v['section_id']}: {e}")
                results.append({
                    "section_id": v['section_id'],
                    "error": str(e),
                    "success": False
                })
        return results

    def generate(self, section_id: str, description: str, visual_type: str) -> Path:
        """Generate a single visual using templates."""
        filename = f"{section_id}.png"
        output_path = self.output_dir / filename
        
        logger.info(f"📊 Generating visual: {section_id} ({visual_type})")
        
        # Select template based on visual type
        if visual_type in ['flowchart', 'process', 'diagram']:
            code = self._flowchart_template(description, str(output_path))
        elif visual_type in ['timeline', 'journey_map', 'roadmap']:
            code = self._timeline_template(description, str(output_path))
        elif visual_type in ['comparison', 'table']:
            code = self._comparison_template(description, str(output_path))
        elif visual_type in ['concept', 'framework']:
            code = self._concept_template(description, str(output_path))
        else:
            # Skip generic charts - they add noise, not value
            logger.info(f"⏭️ Skipping generic visual: {section_id} (type: {visual_type})")
            return self._create_skip_marker(section_id, description)
        
        # Write and execute script
        script_path = self.output_dir / f"temp_{section_id}.py"
        script_path.write_text(code)
        
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.warning(f"⚠️ Visual generation failed: {result.stderr[:200]}")
                return self._create_skip_marker(section_id, description)
                
            if not output_path.exists():
                return self._create_skip_marker(section_id, description)
                
            logger.info(f"✅ Generated: {output_path.name}")
            return output_path
            
        finally:
            if script_path.exists():
                script_path.unlink()
    
    def _create_skip_marker(self, section_id: str, description: str) -> Path:
        """Create a marker file for skipped visuals (not included in PDF)."""
        marker_path = self.output_dir / f"{section_id}_skipped.txt"
        marker_path.write_text(f"SKIPPED: {section_id}\n\n{description[:200]}")
        return marker_path

    def _flowchart_template(self, description: str, output_path: str) -> str:
        """Generate a flowchart/process diagram."""
        # Extract steps from description
        steps = re.findall(r'(\w+[\s\w]*)->\\s*(\w+[\s\w]*)', description)
        
        nodes = []
        for s in steps:
            u, v = s[0].strip(), s[1].strip()
            if u not in nodes: nodes.append(u)
            if v not in nodes: nodes.append(v)
        
        if not nodes:
            # Default nodes based on description keywords
            nodes = ['Start', 'Process', 'Result']
            
        return f'''
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

nodes = {nodes}
n = len(nodes)

fig, ax = plt.subplots(figsize=(12, 4))
ax.set_xlim(0, n * 2.5)
ax.set_ylim(0, 2)
ax.axis('off')

# Dreamweaving color palette
colors = ['#6B46C1', '#805AD5', '#9F7AEA', '#B794F4', '#D6BCFA']

box_width = 1.8
box_height = 0.9
y_center = 1.0

for i, label in enumerate(nodes):
    x_center = i * 2.5 + 1.25
    color = colors[i % len(colors)]
    
    rect = patches.FancyBboxPatch(
        (x_center - box_width/2, y_center - box_height/2),
        box_width, box_height,
        boxstyle="round,pad=0.1",
        linewidth=2, edgecolor=color, facecolor='white'
    )
    ax.add_patch(rect)
    ax.text(x_center, y_center, label, ha='center', va='center', 
            fontsize=11, fontweight='bold', color='#2D3748', wrap=True)

    if i < n - 1:
        next_x = (i + 1) * 2.5 + 1.25
        ax.annotate("", xy=(next_x - box_width/2 - 0.1, y_center), 
                    xytext=(x_center + box_width/2 + 0.1, y_center),
                    arrowprops=dict(arrowstyle="->", lw=2, color='#718096'))

plt.savefig("{output_path}", dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
'''

    def _timeline_template(self, description: str, output_path: str) -> str:
        """Generate a timeline/journey visualization."""
        return f'''
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

steps = ['Foundation', 'Practice', 'Mastery', 'Expression']
colors = ['#E9D5FF', '#C4B5FD', '#A78BFA', '#8B5CF6']

fig, ax = plt.subplots(figsize=(12, 3))
ax.set_xlim(0, 10)
ax.set_ylim(0, 2)
ax.axis('off')

# Draw timeline
ax.plot([0.5, 9.5], [1, 1], 'k-', lw=2, alpha=0.3)

for i, (step, color) in enumerate(zip(steps, colors)):
    x = 0.5 + i * 2.5
    ax.scatter(x, 1, s=400, c=color, zorder=3, edgecolor='#4C1D95', linewidth=2)
    ax.text(x, 0.5, step, ha='center', fontsize=11, fontweight='bold', color='#2D3748')
    ax.text(x, 1.5, f"Phase {{i+1}}", ha='center', fontsize=9, color='#718096')

plt.savefig("{output_path}", dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
'''

    def _comparison_template(self, description: str, output_path: str) -> str:
        """Generate a comparison/table visualization."""
        return f'''
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 6))
ax.axis('off')

# Simple comparison layout
items = [
    ('Before', ['Basic understanding', 'Inconsistent practice', 'Limited vocabulary']),
    ('After', ['Deep mastery', 'Daily discipline', 'Rich expression'])
]

for col, (title, points) in enumerate(items):
    x = 0.25 + col * 0.5
    color = '#E9D5FF' if col == 0 else '#8B5CF6'
    
    ax.text(x, 0.95, title, ha='center', fontsize=16, fontweight='bold', 
            color='#2D3748', transform=ax.transAxes)
    
    for i, point in enumerate(points):
        y = 0.8 - i * 0.15
        ax.text(x, y, f"• {{point}}", ha='center', fontsize=11, 
                color='#4A5568', transform=ax.transAxes)

plt.savefig("{output_path}", dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
'''

    def _concept_template(self, description: str, output_path: str) -> str:
        """Generate a concept/framework diagram."""
        return f'''
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(10, 8))
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis('off')

# Central concept
center = patches.Circle((5, 5), 1.5, facecolor='#8B5CF6', edgecolor='#4C1D95', linewidth=3)
ax.add_patch(center)
ax.text(5, 5, 'Core\\nConcept', ha='center', va='center', fontsize=12, 
        fontweight='bold', color='white')

# Surrounding elements
concepts = ['Element 1', 'Element 2', 'Element 3', 'Element 4']
positions = [(2, 8), (8, 8), (2, 2), (8, 2)]
colors = ['#E9D5FF', '#C4B5FD', '#A78BFA', '#DDD6FE']

for (x, y), concept, color in zip(positions, concepts, colors):
    rect = patches.FancyBboxPatch((x-1, y-0.5), 2, 1, boxstyle="round,pad=0.1",
                                   facecolor=color, edgecolor='#6B46C1', linewidth=2)
    ax.add_patch(rect)
    ax.text(x, y, concept, ha='center', va='center', fontsize=10, color='#2D3748')
    
    # Connection line
    ax.plot([x, 5], [y, 5], '--', color='#A78BFA', alpha=0.5, lw=1.5)

plt.savefig("{output_path}", dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
'''


# Export visual prompts for Antigravity generation
def create_visual_prompts(title: str, chapters: list, output_path: Path) -> dict:
    """
    Create a visual_prompts.json file for Antigravity/manual image generation.
    
    This creates descriptions for contextual images that should be generated
    via Antigravity's generate_image tool or manually sourced.
    """
    prompts = {
        "cover": {
            "type": "illustration",
            "prompt": f"A beautiful, professional product cover image for '{title}'. "
                      f"Use warm, inviting colors. Style: premium digital product, modern and elegant.",
            "dimensions": "1024x1024",
            "priority": "required"
        }
    }
    
    # Add chapter illustrations only for key chapters (first 3, last 1)
    key_chapters = chapters[:3] + chapters[-1:] if len(chapters) > 3 else chapters
    
    for i, ch in enumerate(key_chapters):
        ch_title = ch.get('title', f'Chapter {i+1}')
        prompts[f"ch{i+1}_illustration"] = {
            "type": "illustration",
            "prompt": f"An artistic illustration representing the concept of '{ch_title}'. "
                      f"Abstract, inspirational, matching the theme of personal growth and mastery.",
            "dimensions": "1024x768",
            "priority": "optional"
        }
    
    # Save prompts file
    import json
    output_path.write_text(json.dumps(prompts, indent=2))
    logger.info(f"📝 Visual prompts saved: {output_path}")
    
    return prompts
