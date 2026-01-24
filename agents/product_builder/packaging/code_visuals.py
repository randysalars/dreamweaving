"""
Code Visuals Generator
Generates charts, diagrams, and data visualizations using local Python libraries.
Uses LLM to write the generation code, then executes it in a sandbox.
"""

import logging
import uuid
import sys
import subprocess
from pathlib import Path
from typing import Dict, Optional, List
from ..core.llm import LLMClient

logger = logging.getLogger(__name__)

class CodeVisualsGenerator:
    """
    Generates PNGs from text descriptions using Matplotlib/Seaborn/Graphviz.
    """
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir.resolve()
        self.llm = LLMClient()
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
        """
        Generate a single visual.
        """
        # Deterministic filename (Overwrite existing) to ensure Markdown links stay valid
        filename = f"{section_id}.png"
        output_path = self.output_dir / filename
        
        logger.info(f"📊 Generating Code Visual: {section_id} ({visual_type})")
        
        # 1. Generate Python Code
        code = self._generate_code(description, visual_type, str(output_path))
        
        # 2. Write Temp Script
        script_path = self.output_dir / f"temp_{section_id}.py"
        script_path.write_text(code)
        
        logger.info(f"🐛 EXEC SCRIPT: {script_path}")
        logger.info(f"🐛 CODE PREVIEW:\n{code[:300]}...\n(Saving to: {output_path})")

        # 3. Execute
        try:
            # Run in current venv
            python_exe = sys.executable
            result = subprocess.run(
                [python_exe, str(script_path)],
                capture_output=True,
                text=True,
                timeout=30 # 30s timeout
            )
            
            if result.stdout:
                logger.info(f"📜 STDOUT: {result.stdout}")
            if result.stderr:
                logger.warning(f"⚠️ STDERR: {result.stderr}")
            
            if result.returncode != 0:
                raise Exception(f"Script failed: {result.stderr}")
                
            if not output_path.exists():
                raise Exception(f"Script ran (RC=0) but did not generate image file at {output_path}")
                
            logger.info(f"✅ Generated: {output_path}")
            return output_path
            
        finally:
            # Cleanup temp script
            if script_path.exists():
                script_path.unlink()

    def _generate_code(self, description: str, visual_type: str, output_path: str) -> str:
        """
        Ask LLM to write the matplotlib/graphviz code.
        """
        prompt = f"""
        You are a Data Visualization Engineer.
        Write a COMPLETE, STANDALONE Python script to generate a high-quality PNG image based on the request below.
        
        **Request:** {description}
        **Type:** {visual_type}
        **Output Path:** {output_path}
        
        **Constraints:**
        1. Use 'matplotlib', 'seaborn', 'pandas', or 'graphviz'.
        2. Set style to 'seaborn-v0_8-whitegrid' or similar clean style.
        3. Use professional colors (Slate Blue, Dark Grey, Gold). NO basic Red/Green/Blue.
        4. DPI must be 300.
        5. Figure size: 10x6 inches.
        6. Font size: 12+. Title size: 16+.
        7. The script must save the file to `output_path`.
        8. Handle any data generation within the script (create dummy data that matches the concept).
        9. NO `plt.show()`. ONLY `plt.savefig(output_path, bbox_inches='tight')`.
        10. Do not wrap in markdown blocks. Return PURE LOCAL PYTHON CODE.
        
        **Example Code Structure:**
        import matplotlib.pyplot as plt
        import pandas as pd
        import seaborn as sns
        
        # Data
        data = {{ ... }}
        df = pd.DataFrame(data)
        
        # Plot
        plt.figure(figsize=(10,6))
        sns.barplot(...)
        plt.title("...")
        
        # Save
        plt.savefig("{output_path}", dpi=300, bbox_inches='tight')
        """
        
        response = self.llm.generate(prompt)
        
        # Strip markdown if present
        if "```python" in response:
            response = response.split("```python")[1].split("```")[0]
        elif "```" in response:
            response = response.split("```")[1].split("```")[0]
            
        # Try to generate via LLM first (if configured/valid)
        if not self.llm.mock_mode and self.llm.valid:
            try:
                response = self.llm.generate(prompt)
                # Strip markdown
                if "```python" in response:
                    response = response.split("```python")[1].split("```")[0]
                elif "```" in response:
                    response = response.split("```")[1].split("```")[0]
                
                # Check for explicit error or empty response
                if response.strip().startswith("# Error") or not response.strip():
                    raise ValueError("LLM returned error")

                # Support Mock Templates
                if "{output_path}" in response:
                    container_path = output_path
                    response = response.replace("{output_path}", container_path)

                # Force Headless Backend (Crucial for Server/CI)
                if "matplotlib" in response and "use('Agg')" not in response:
                    response = "import matplotlib\nmatplotlib.use('Agg')\n" + response

                return response.strip()
            except Exception:
                pass # Fallback to templates

        # --- ZERO COST TEMPLATE ENGINE (Fallback) ---
        logger.info("⚡ Using Zero-Cost Template Engine")
        return self._generate_from_template(description, output_path)

    def _generate_from_template(self, description: str, output_path: str) -> str:
        """
        Parses description to select a chart template and inject data.
        Heuristic-based (Free).
        """
        import re
        
        # 1. Parse Numbers and Labels
        # Look for patterns like "Apple: 100", "Start 25: $1M", "Year 1: 50%"
        # Regex: (Word/Phrase): (Currency/Number)
        matches = re.findall(r'([\w\s]+)[:]\s?[\$]?([\d,]+[\.]?[\d]?[%]?)', description)
        
        labels = []
        values = []
        
        for m in matches:
            label = m[0].strip()
            val_str = m[1].replace(',', '').replace('$', '').replace('%', '')
            try:
                # Handle suffixes
                mult = 1.0
                if 'k' in val_str.lower():
                    mult = 1000.0
                    val_str = val_str.lower().replace('k', '')
                elif 'm' in val_str.lower():
                    mult = 1000000.0
                    val_str = val_str.lower().replace('m', '')
                    
                val = float(val_str) * mult
                labels.append(label)
                values.append(val)
            except:
                continue
                
        # Defaults if no data found
        if not labels:
            labels = ['A', 'B', 'C']
            values = [10, 20, 30]

        # 2. Select Template based on Keywords
        desc_lower = description.lower()
        
        # --- GRAPHVIZ / FLOWCHART TEMPLATE ---
        if "flow" in desc_lower or "diagram" in desc_lower or "process" in desc_lower:
            # Extract steps: "Earn -> Save -> Invest"
            steps = re.findall(r'(\w+[\s\w]*)->\s*(\w+[\s\w]*)', description)
            if not steps:
                 # Try single word regex if phrase regex failed
                 steps = re.findall(r'(\w+)\s*->\s*(\w+)', description)
            
            # Build unique node list and edges preserving order
            nodes = []
            for s in steps:
                u, v = s[0].strip(), s[1].strip()
                if u not in nodes: nodes.append(u)
                if v not in nodes: nodes.append(v)
            
            if not nodes:
                nodes = ['Start', 'Action', 'Result']
            
            # Simple Matplotlib Flowchart Layout (Horizontal)
            code = f"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

nodes = {nodes}
n = len(nodes)

plt.figure(figsize=(10, 4))
ax = plt.gca()
ax.set_xlim(0, n * 2)
ax.set_ylim(0, 2)
ax.axis('off')

# Draw Nodes
box_width = 1.2
box_height = 0.8
y_center = 1.0

for i, label in enumerate(nodes):
    x_center = i * 2 + 1
    # Box
    rect = patches.FancyBboxPatch(
        (x_center - box_width/2, y_center - box_height/2),
        box_width, box_height,
        boxstyle="round,pad=0.1",
        linewidth=2, edgecolor='#4B0082', facecolor='#E6E6FA'
    )
    ax.add_patch(rect)
    # Text
    ax.text(x_center, y_center, label, ha='center', va='center', fontsize=11, fontweight='bold', color='#333', wrap=True)

    # Arrow to next (if not last)
    if i < n - 1:
        next_x = (i + 1) * 2 + 1
        # Start at right edge of current, End at left edge of next
        start = (x_center + box_width/2 + 0.1, y_center)
        end = (next_x - box_width/2 - 0.1, y_center)
        
        ax.annotate("", xy=end, xytext=start, 
                    arrowprops=dict(arrowstyle="->", lw=2, color='#666'))

plt.title("Process Flow", fontsize=14, pad=10)
plt.savefig("{output_path}", dpi=300, bbox_inches='tight')
"""
            return code

        # --- MATPLOTLIB BAR CHART TEMPLATE (Default) ---
        title = "Chart"
        if "title" in desc_lower:
            # Try to extract title (simple heuristic)
            pass 
        
        # Basic Bar Chart Template
        code = f"""
import matplotlib
matplotlib.use('Agg') # Force headless
import matplotlib.pyplot as plt
import seaborn as sns

labels = {labels}
values = {values}

plt.figure(figsize=(10,6))
plt.style.use('seaborn-v0_8-whitegrid')

# Color palette based on Dreamweaving (Gold/Purple/Slate)
colors = sns.color_palette("mako", n_colors=len(labels))

ax = sns.barplot(x=labels, y=values, palette=colors)

plt.title("{title}", fontsize=16, fontweight='bold', pad=20)
plt.ylabel("Value", fontsize=12)
plt.xticks(rotation=45 if len(labels) > 4 else 0)
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Add value labels
for i, v in enumerate(values):
    ax.text(i, v, str(v), color='black', ha="center", va="bottom")

plt.savefig("{output_path}", dpi=300, bbox_inches='tight')
"""
        return code
