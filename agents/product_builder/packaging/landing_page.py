"""
Enhanced Landing Page Agent.

Generates conversion-optimized landing page content with CRO psychology,
and optionally outputs a styled HTML page.
"""

import logging
import json
import re
from pathlib import Path
from typing import Dict, Any, Optional

from ..schemas.blueprint import ProductBlueprint
from ..core.llm import LLMClient
from .landing_page_html import LandingPageHTMLGenerator

logger = logging.getLogger(__name__)


class LandingPageAgent:
    """
    Generates a premium, conversion-focused Landing Page.
    
    Features:
    - CRO psychology elements (pain agitation, social proof, urgency)
    - Expanded content sections
    - Optional HTML output generation
    """
    
    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir
        self.premium_template_path = templates_dir / "landing_page_premium.md"
        self.legacy_template_path = templates_dir / "landing_page_json.md"
        self.llm = LLMClient()
        self.html_generator = LandingPageHTMLGenerator()
    
    def generate(
        self, 
        blueprint: ProductBlueprint, 
        bonus_plan: Optional[Any] = None,
        generate_html: bool = True,
        output_dir: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Generate landing page content and optionally HTML output.
        
        Args:
            blueprint: Product blueprint with title, promise, audience, chapters
            bonus_plan: Optional bonus plan from BonusArchitect
            generate_html: Whether to also generate HTML file
            output_dir: Where to save HTML (if generate_html=True)
            
        Returns:
            Dict with landing page content (and html_path if generated)
        """
        logger.info(f"🚀 Generating Premium Landing Page for: {blueprint.title}")
        
        # Select template
        template_path = self.premium_template_path if self.premium_template_path.exists() else self.legacy_template_path
        
        if not template_path.exists():
            logger.error(f"Template not found: {template_path}")
            return {"error": "Template not found"}
        
        template = template_path.read_text()
        
        # Build context
        context = self._build_context(blueprint, bonus_plan)
        
        # Format prompt
        try:
            prompt = template.format(**context)
        except KeyError as e:
            logger.warning(f"Missing template key: {e}. Using fallback.")
            prompt = f"{template}\n\nCONTEXT:\n{json.dumps(context, indent=2)}"
        
        # Generate content via LLM
        logger.info("   📝 Generating copy with CRO psychology...")
        response = self.llm.generate(prompt)
        
        # Parse JSON response
        content = self._parse_response(response, blueprint)
        
        # Generate HTML if requested
        if generate_html and output_dir:
            html_path = output_dir / "landing_page.html"
            self.html_generator.generate(content, html_path)
            content['html_path'] = str(html_path)
            logger.info(f"   🌐 HTML generated: {html_path}")
        
        # Save JSON content
        if output_dir:
            json_path = output_dir / "landing_page_content.json"
            json_path.write_text(json.dumps(content, indent=2))
            content['json_path'] = str(json_path)
            logger.info(f"   📄 JSON saved: {json_path}")
        
        logger.info("✅ Premium Landing Page generation complete!")
        return content
    
    def _build_context(self, blueprint: ProductBlueprint, bonus_plan: Optional[Any]) -> Dict[str, str]:
        """Build template context from blueprint and bonus plan."""
        context = {
            "title": blueprint.title,
            "subhead": getattr(blueprint.promise, 'subhead', ''),
            "headline": getattr(blueprint.promise, 'headline', ''),
            "audience_state": getattr(blueprint.audience, 'current_state', ''),
            "bullet_points": "\n".join([
                f"- {c.title}: {c.purpose}" 
                for c in getattr(blueprint, 'chapter_map', [])
            ]),
        }
        
        # Inject bonus plan
        if bonus_plan and hasattr(bonus_plan, 'bonuses'):
            logger.info("   🎁 Injecting Bonus Plan...")
            bonus_descriptions = "\n".join([
                f"BONUS {i+1}: {b.title} ({b.format})\n"
                f"Description: {b.description}\n"
                f"Value: ${b.target_friction}"
                for i, b in enumerate(bonus_plan.bonuses)
            ])
            context['bonus_instruction'] = (
                f"CRITICAL: USE THESE SPECIFIC BONUSES. DO NOT INVENT NEW ONES:\n"
                f"{bonus_descriptions}"
            )
        else:
            context['bonus_instruction'] = (
                "Create 3 high-value bonuses relevant to the topic. "
                "Each should solve a specific friction point."
            )
        
        return context
    
    def _parse_response(self, response: str, blueprint: ProductBlueprint) -> Dict[str, Any]:
        """Parse LLM response into structured content."""
        try:
            clean_response = response.strip()
            
            # Strip markdown code blocks
            if clean_response.startswith("```"):
                clean_response = re.sub(r"^```(json)?\n", "", clean_response)
                clean_response = re.sub(r"\n```$", "", clean_response)
            
            # Find JSON boundaries
            json_start = clean_response.find("{")
            json_end = clean_response.rfind("}") + 1
            
            if json_start != -1 and json_end > json_start:
                return json.loads(clean_response[json_start:json_end])
            else:
                raise ValueError("No JSON object found in response")
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Landing Page JSON: {e}")
            logger.debug(f"Raw response: {response[:500]}...")
            
            # Return fallback structure
            return self._fallback_content(blueprint, response)
    
    def _fallback_content(self, blueprint: ProductBlueprint, raw_response: str) -> Dict[str, Any]:
        """Generate fallback content structure when parsing fails."""
        return {
            "hero": {
                "hook": "Ready to transform your results?",
                "headline": getattr(blueprint.promise, 'headline', blueprint.title),
                "subheadline": getattr(blueprint.promise, 'subhead', ''),
                "cta_primary": "Get Instant Access",
                "cta_secondary": "Learn More"
            },
            "pain_agitation": {
                "opener": "You've been struggling...",
                "pain_points": ["Frustration with current methods", "Lack of clear guidance", "Wasted time and money"],
                "agitation": "It's time for a change.",
                "bridge": "There is a better way."
            },
            "solution": {
                "intro": "Introducing...",
                "product_name": blueprint.title,
                "features": [
                    {"icon": "✨", "title": "Comprehensive Guide", "description": "Everything you need in one place."},
                    {"icon": "🎯", "title": "Actionable Steps", "description": "Clear instructions you can follow."},
                    {"icon": "⚡", "title": "Fast Results", "description": "See progress quickly."}
                ],
                "differentiator": "Unlike other solutions, this gives you a complete system."
            },
            "social_proof": {
                "stats": [{"number": "1,000+", "label": "Happy Customers"}],
                "testimonials": [
                    {"quote": "This changed everything for me.", "author": "Happy Customer", "role": "User", "rating": 5}
                ],
                "logos": []
            },
            "bonuses": [],
            "risk_reversal": {
                "guarantee_type": "30-Day Money-Back Guarantee",
                "guarantee_copy": "If you're not satisfied, get a full refund. No questions asked.",
                "badge_text": "100% Risk-Free"
            },
            "urgency": {
                "urgency_type": "limited_time",
                "message": "Special pricing available for a limited time."
            },
            "faq": [
                {"question": "Who is this for?", "answer": "Anyone looking to improve their results."},
                {"question": "What's included?", "answer": "Everything described above, plus bonuses."}
            ],
            "about": {
                "name": "Your Guide",
                "bio": "Expert in this field with years of experience.",
                "credentials": []
            },
            "footer_cta": {
                "headline": "Ready to get started?",
                "subheadline": "Join thousands who have already transformed.",
                "cta_text": "Get Instant Access"
            },
            "page_title": blueprint.title,
            "meta_description": f"Learn {blueprint.title} with this comprehensive guide.",
            "raw_generated_content": raw_response
        }
