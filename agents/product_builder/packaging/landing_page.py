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
        
    def generate(self, blueprint: ProductBlueprint, bonus_plan: dict = None) -> dict:
        """
        Populate the landing page template using LLM, returning a JSON object.
        """
        logger.info(f"Generating Landing Page for {blueprint.title}...")
        
        # Switch to JSON template
        json_template_path = self.template_path.parent / "landing_page_json.md"
        
        if json_template_path.exists():
            with open(json_template_path, 'r') as f:
                template = f.read()
        else:
            logger.error(f"Template not found: {json_template_path}")
            return {"error": "Template not found"}
            
        # Synthesize marketing copy from Blueprint
        context = {
            "title": blueprint.title,
            "subhead": blueprint.promise.subhead,
            "headline": blueprint.promise.headline,
            "audience_state": blueprint.audience.current_state,
            "bullet_points": "\n".join([f"- {c.title}: {c.purpose}" for c in blueprint.chapter_map]),
        }
        
        # Inject Bonus Plan if available
        if bonus_plan and hasattr(bonus_plan, 'bonuses'):
            logger.info("   🎁 Injecting Bonus Plan into copy generation Context...")
            bonus_descriptions = "\n".join([
                f"BONUS {i+1}: {b.title} ({b.format})\nDescription: {b.description}\nValue: Help overcome '{b.target_friction}'"
                for i, b in enumerate(bonus_plan.bonuses)
            ])
            context['bonus_instruction'] = f"CRITICAL: USE THESE SPECIFIC BONUSES. DO NOT INVENT NEW ONES:\n{bonus_descriptions}"
        else:
            context['bonus_instruction'] = "Invent 3 high-value bonuses relevant to the topic."

        # Determine prompt
        try:
             prompt = template.format(**context)
        except Exception as e:
             # Fallback if template doesn't have {bonus_instruction} placeholder yet
             # We assume we might need to append it or just let the context dump handle it
             if "bonus_instruction" not in template:
                 prompt = f"{template}\n\nCONTEXT:\n{context}\n\n{context['bonus_instruction']}"
             else:
                 prompt = f"{template}\n\nCONTEXT:\n{context}"
             
        response = self.llm.generate(prompt)
        
        # Parse JSON
        import json
        import re
        
        try:
            # Strip markdown code blocks if present
            clean_response = response.strip()
            if clean_response.startswith("```"):
                clean_response = re.sub(r"^```(json)?\n", "", clean_response)
                clean_response = re.sub(r"\n```$", "", clean_response)
            
            return json.loads(clean_response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Landing Page JSON: {e}")
            logger.debug(f"Raw response: {response}")
            # Fallback structure
            return {
                "headline": blueprint.promise.headline,
                "subheadline": blueprint.promise.subhead,
                "features": [],
                "bonuses": [],
                "faq": [],
                "testimonial": {},
                "raw_generated_content": response
            }
