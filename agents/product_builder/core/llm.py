
import logging
import subprocess
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)

class LLMClient:
    """
    Wrapper that calls the Salarsu Node.js bridge for generation.
    """
    def __init__(self):
        # Locate the bridge script relative to this project
        # projects root is at parents[4]
        self.bridge_script = Path(__file__).resolve().parents[4] / "salarsu" / "scripts" / "simple_llm.js"
        
        if not self.bridge_script.exists():
             logger.error(f"Bridge script not found at {self.bridge_script}")
             self.valid = False
        else:
             self.valid = True

    def generate(self, prompt: str) -> str:
        """
        Generates text content using the Node bridge.
        """
        if not self.valid:
             return "# Error: LLM Bridge script not found."

        try:
            # We must run 'node' from the salarsu directory context if possible, 
            # OR just run it pointing to the file.
            # But the script loads env relative to itself, so it should be fine.
            # However, imports might be relative. 
            # The script uses 'import .. from ../src/...'. This resolves well if running 'node path/to/script'.
            
            cmd = ["node", str(self.bridge_script)]
            
            result = subprocess.run(
                cmd,
                input=prompt,
                capture_output=True,
                text=True,
                cwd=str(self.bridge_script.parent.parent), # Run in Salarsu root to ensure imports/env work
                check=True
            )
            
            
            output = result.stdout.strip()
            # Filter out dotenv logs
            clean_lines = [line for line in output.splitlines() if not line.startswith('[dotenv')]
            return "\n".join(clean_lines).strip()
            
        except subprocess.CalledProcessError as e:
            logger.error(f"LLM Generation failed: {e.stderr}")
            return f"# Error: LLM Generation failed: {e.stderr}"
        except Exception as e:
            logger.error(f"LLM Bridge Error: {e}")
            return f"# Error: LLM Bridge Error: {e}"
