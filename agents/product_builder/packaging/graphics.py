
import subprocess
import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

class GraphicDesigner:
    """
    Generates visual assets for the product using the DALL-E 3 bridge.
    """
    def __init__(self, salarsu_root: Path):
        self.salarsu_root = salarsu_root
        self.bridge_script = self.salarsu_root / "scripts" / "simple_image_gen.js"
        if not self.bridge_script.exists():
            raise FileNotFoundError(f"Image Gen Bridge script not found at {self.bridge_script}")

    def generate_cover(self, title: str, vibe_keywords: list, output_path: Path) -> Path:
        """
        Generates a product cover image.
        """
        prompt = (
            f"A premium, high-converting digital product cover titled '{title}'. "
            f"Design Style: {', '.join(vibe_keywords)}. "
            "Visuals: sophisticated, abstract representation of value. "
            "High resolution, professional design suitable for a store card."
        )
        
        return self._generate(prompt, output_path)

    def _generate(self, prompt: str, output_path: Path) -> Path:
        """
        Calls the Node.js bridge to generate the image.
        """
        payload = {
            "prompt": prompt,
            "output_path": str(output_path.resolve())
        }
        
        cmd = ["node", str(self.bridge_script)]
        
        try:
            logger.info(f"🎨 Generating Image: {prompt[:50]}...")
            result = subprocess.run(
                cmd,
                input=json.dumps(payload),
                capture_output=True,
                text=True,
                cwd=str(self.salarsu_root),
                check=True
            )
            created_path = result.stdout.strip()
            # Filter logs just in case
            lines = created_path.splitlines()
            clean_path = lines[-1] if lines else ""
            
            if Path(clean_path).exists():
                logger.info(f"✅ Image Generated: {clean_path}")
                return Path(clean_path)
            else:
                 raise FileNotFoundError(f"Image reported created but not found: {clean_path}")

        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Image Generation Failed: {e.stderr}")
            raise RuntimeError(f"Image Gen Failed: {e.stderr}")
