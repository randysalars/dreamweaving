import logging
from pathlib import Path
from ..schemas.blueprint import ProductBlueprint

logger = logging.getLogger(__name__)

class LandingPageAgent:
    """
    Generates a conversion-focused Landing Page from the Product Blueprint.
    """
    def __init__(self, templates_dir: Path):
        self.template_path = templates_dir / "landing_page.mdx"
        
    def generate(self, blueprint: ProductBlueprint) -> str:
        """
        Populate the landing page template.
        """
        logger.info(f"Generating Landing Page for {blueprint.title}...")
        
        if self.template_path.exists():
            with open(self.template_path, 'r') as f:
                template = f.read()
        else:
            return "# Error: Template not found"
            
        # Synthesize marketing copy from Blueprint (Simple rule-based mapping for now)
        context = {
            "title": blueprint.title,
            "subhead": blueprint.promise.subhead,
            "headline": blueprint.promise.headline,
            "problem_agitation": f"If you are feeling {blueprint.audience.current_state}, you are not alone.",
            "solution_description": f"This is not just a book. It is a {blueprint.promise.transformation_timeline} system.",
            "bullet_points": "\n".join([f"- {c.title}: {c.purpose}" for c in blueprint.chapter_map[:5]]),
            "toc_preview": f"Contains {len(blueprint.chapter_map)} deep-dive modules."
        }
        
        return template.format(**context)
