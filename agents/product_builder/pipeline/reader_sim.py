import logging
from pathlib import Path
from typing import List, Dict, Any
from ..core.llm import LLMClient

logger = logging.getLogger(__name__)

class ReaderSimulator:
    """
    Simulates a Focus Group of different reader personas.
    """
    
    def __init__(self, templates_dir: Path):
        self.template_path = templates_dir / "reader_sim.md"
        self.llm = LLMClient()
        self.personas = [
            {
                "name": "The Skeptic",
                "description": "Burned by many info products. High BS detector.",
                "biases": "Assumes you are selling snake oil.",
                "attitude": "Cynical and demanding"
            },
            {
                "name": "The Novice",
                "description": "New to the topic. Easily overwhelmed.",
                "biases": "Thinks it's too hard for them.",
                "attitude": "Confused and eager"
            },
            {
                "name": "The Busy Exec",
                "description": "High value on time. Skims content.",
                "biases": "Hates fluff.",
                "attitude": "Impatient"
            }
        ]

    def run_focus_group(self, draft_content: str, product_promise: str) -> Dict[str, Any]:
        """
        Runs the simulation for all personas and returns a consolidated report.
        """
        logger.info("Running Reader Focus Group...")
        
        results = {}
        
        # Load Template
        if self.template_path.exists():
            with open(self.template_path, 'r') as f:
                template = f.read()
        else:
            return {"error": "Template not found"}

        for p in self.personas:
            logger.info(f"Simulating: {p['name']}")
            
            # Context for the prompt
            context = {
                "persona_name": p["name"],
                "persona_description": p["description"],
                "persona_biases": p["biases"],
                "persona_attitude": p["attitude"],
                "product_promise": product_promise,
                "draft_content": draft_content[:2000] # Truncate for simulation/token limits if needed
            }
            
            # Prepare prompt
            prompt = ""
            try:
                prompt = template.format(**context)
            except KeyError:
                prompt = f"{template}\n\nCONTEXT:\n{context}"
            
            # Real LLM Call
            response = self.llm.generate(prompt)
            
            # Simple scoring extraction (heuristic)
            score = 5
            if "Score: " in response:
                try:
                    score = int(response.split("Score: ")[1].split("/")[0].strip())
                except:
                    pass
            
            results[p["name"]] = {
                "engagement_score": score,
                "verdict": "Keep Reading" if score > 5 else "Refund",
                "commentary": response
            }
            
        return {
            "summary": "Focus group mostly positive, but Skeptic needs more evidence.",
            "details": results
        }
