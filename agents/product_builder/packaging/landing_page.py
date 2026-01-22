import logging
from pathlib import Path
from ..schemas.blueprint import ProductBlueprint
from ..core.llm import LLMClient

logger = logging.getLogger(__name__)

class LandingPageAgent:
    """
    Generates a conversion-focused Landing Page from the Product Blueprint.
    """
    def __init__(self, templates_dir: Path):
        self.template_path = templates_dir / "landing_page_gen.md"
        self.llm = LLMClient()
        
    def generate(self, blueprint: ProductBlueprint) -> str:
        """
        Populate the landing page template using LLM.
        """
        logger.info(f"Generating Landing Page for {blueprint.title}...")
        
        if self.template_path.exists():
            with open(self.template_path, 'r') as f:
                template = f.read()
        else:
            return "# Error: Template not found"
            
        # Synthesize marketing copy from Blueprint
        context = {
            "title": blueprint.title,
            "subhead": blueprint.promise.subhead,
            "headline": blueprint.promise.headline,
            "audience_state": blueprint.audience.current_state,
            "bullet_points": "\n".join([f"- {c.title}: {c.purpose}" for c in blueprint.chapter_map]),
        }
        
        # Determine prompt
        try:
             prompt = template.format(**context)
        except Exception as e:
             prompt = f"{template}\n\nCONTEXT:\n{context}"
             
        return self.llm.generate(prompt)
