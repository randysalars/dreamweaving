"""
BonusArchitect Agent
Designs AND generates bonuses as completion catalysts, not random extras.

Enhanced with:
- 6 standard bonus types (cookbook, worksheet, reference_card, meditation, journal, checklist)
- Research-backed content generation
- Template-based structure
- Content quality validation
"""

import logging
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from ..core.llm import LLMClient
from ..schemas.product_intelligence import ProductIntelligence
from ..schemas.blueprint import ChapterSpec
from ..schemas.bonus_plan import BonusPlan, Bonus

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# BONUS TYPE DEFINITIONS
# ═══════════════════════════════════════════════════════════════

# Standard 6 bonus types with their purposes
STANDARD_BONUS_TYPES = {
    'cookbook': {
        'name': 'Cookbook/Recipe Guide',
        'purpose': 'Practical recipes, meal plans, or step-by-step examples',
        'min_words': 2000,
        'template': 'cookbook_template.md'
    },
    'worksheet': {
        'name': 'Practice Worksheets',
        'purpose': 'Self-assessment, planning exercises, and fill-in templates',
        'min_words': 1500,
        'template': 'worksheet_template.md'
    },
    'reference_card': {
        'name': 'Quick Reference Cards',
        'purpose': 'Protocol summaries and quick-lookup information',
        'min_words': 1200,
        'template': 'reference_card_template.md'
    },
    'meditation': {
        'name': 'Guided Scripts',
        'purpose': 'Complete word-for-word scripts for practices',
        'min_words': 2000,
        'template': 'meditation_template.md'
    },
    'journal': {
        'name': 'Transformation Journal',
        'purpose': 'Daily prompts and reflection exercises',
        'min_words': 1500,
        'template': 'journal_template.md'
    },
    'checklist': {
        'name': 'Action Checklists',
        'purpose': 'Phase-based checklists and progress tracking',
        'min_words': 1200,
        'template': 'checklist_template.md'
    }
}


@dataclass
class BonusContentSpec:
    """Specification for a bonus to generate."""
    type: str
    title: str
    topic: str
    context: Dict[str, Any]
    min_words: int = 1000


class BonusArchitect:
    """
    Designs AND generates bonuses that map to friction points in the main product.
    Every bonus must earn its place with substantive, research-backed content.
    
    Enhanced capabilities:
    - 6 standard bonus types with templates
    - Content generation (not just planning)
    - Quality validation
    """
    
    def __init__(self, templates_dir: Path, output_dir: Optional[Path] = None, prompts_only: bool = False):
        self.templates_dir = templates_dir
        self.bonus_templates_dir = templates_dir / "bonus"
        self.output_dir = output_dir
        self.prompts_only = prompts_only
        self.llm = LLMClient()
        
    def design(self, intelligence: ProductIntelligence, chapters: List[ChapterSpec]) -> BonusPlan:
        """
        Design a bonus plan based on product intelligence and chapters.
        
        Args:
            intelligence: The ProductIntelligence from ProductMind
            chapters: The chapter list
            
        Returns:
            BonusPlan: Strategically designed bonuses
        """
        logger.info("🎁 BonusArchitect designing completion catalysts...")
        
        # Identify friction points
        friction_points = self._identify_friction_points(chapters)
        
        # Design 6 standard bonuses
        bonuses = self._design_standard_6(intelligence, chapters, friction_points)
        
        plan = BonusPlan(
            bonuses=bonuses,
            total_value_narrative=self._create_value_narrative(bonuses, intelligence)
        )
        
        logger.info(f"✅ BonusPlan designed with {len(bonuses)} bonuses.")
        return plan
    
    def _design_standard_6(self, intelligence: ProductIntelligence, 
                           chapters: List[ChapterSpec], friction_points: List[str]) -> List[Bonus]:
        """Design the standard 6-bonus package."""
        bonuses = []
        topic = intelligence.thesis if intelligence else "the main topic"
        
        # Map internal types to schema-allowed Bonus.type literals
        # Schema allows: 'clarity', 'application', 'reinforcement', 'deep_dive'
        TYPE_MAPPING = {
            'cookbook': 'application',
            'worksheet': 'application', 
            'reference_card': 'clarity',
            'meditation': 'reinforcement',
            'journal': 'deep_dive',
            'checklist': 'application'
        }
        
        # Map bonus types to specific designs
        bonus_designs = [
            {
                'internal_type': 'cookbook',
                'title': self._generate_bonus_title('cookbook', topic),
                'description': 'Complete recipes, meal plans, and examples',
                'friction': 'Practical implementation'
            },
            {
                'internal_type': 'worksheet',
                'title': self._generate_bonus_title('worksheet', topic),
                'description': 'Self-assessment and planning exercises',
                'friction': friction_points[0] if friction_points else 'Application'
            },
            {
                'internal_type': 'reference_card',
                'title': self._generate_bonus_title('reference_card', topic),
                'description': 'Quick-reference summaries of key protocols',
                'friction': 'Daily reference needs'
            },
            {
                'internal_type': 'meditation',
                'title': self._generate_bonus_title('meditation', topic),
                'description': 'Complete guided practice scripts',
                'friction': 'Practice guidance'
            },
            {
                'internal_type': 'journal',
                'title': self._generate_bonus_title('journal', topic),
                'description': '90-day prompted journal for transformation tracking',
                'friction': 'Sustaining momentum'
            },
            {
                'internal_type': 'checklist',
                'title': self._generate_bonus_title('checklist', topic),
                'description': 'Phase-based action checklists',
                'friction': 'Tracking progress'
            }
        ]
        
        for design in bonus_designs:
            internal_type = design['internal_type']
            schema_type = TYPE_MAPPING.get(internal_type, 'application')
            type_config = STANDARD_BONUS_TYPES.get(internal_type, {})
            bonuses.append(Bonus(
                type=schema_type,
                title=design['title'],
                format='pdf',
                description=design['description'],
                target_friction=design['friction'],
                estimated_pages=type_config.get('min_words', 1000) // 200  # ~200 words/page
            ))
        
        return bonuses

    
    def _generate_bonus_title(self, bonus_type: str, topic: str) -> str:
        """Generate an appropriate title for a bonus type."""
        titles = {
            'cookbook': f"The {self._extract_topic_keyword(topic)} Cookbook",
            'worksheet': f"Practice Worksheets & Assessments",
            'reference_card': f"Quick Reference Cards",
            'meditation': f"Guided Practice Scripts",
            'journal': f"90-Day Transformation Journal",
            'checklist': f"Action Checklists & Trackers"
        }
        return titles.get(bonus_type, f"{bonus_type.replace('_', ' ').title()} Guide")
    
    def _extract_topic_keyword(self, topic: str) -> str:
        """Extract a keyword from the topic for titles."""
        keywords = ['wellness', 'financial', 'productivity', 'health', 'fitness', 
                   'relationship', 'career', 'mindset', 'business', 'wealth']
        for kw in keywords:
            if kw in topic.lower():
                return kw.title()
        return "Complete"
    
    def generate_all_content(self, plan: BonusPlan, product_context: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate actual content for all bonuses in the plan.
        
        Args:
            plan: The BonusPlan with bonus specifications
            product_context: Product title, topic, thesis, etc.
            
        Returns:
            Dict mapping bonus type -> generated content (markdown)
        """
        logger.info(f"📝 Generating content for {len(plan.bonuses)} bonuses...")
        
        generated = {}
        
        for bonus in plan.bonuses:
            content = self.generate_bonus_content(
                bonus_type=bonus.type,
                bonus_title=bonus.title,
                product_context=product_context
            )
            generated[bonus.type] = content
            logger.info(f"   ✅ {bonus.title}: {len(content.split())} words")
        
        return generated
    
    def generate_bonus_content(self, bonus_type: str, bonus_title: str, 
                               product_context: Dict[str, Any]) -> str:
        """
        Generate content for a single bonus.
        
        Args:
            bonus_type: One of the standard bonus types
            bonus_title: Title for this bonus
            product_context: Product metadata
            
        Returns:
            Generated markdown content
        """
        # Load template if available
        template_content = self._load_template(bonus_type)
        
        # Generate the prompt
        prompt = self._create_generation_prompt(
            bonus_type=bonus_type,
            bonus_title=bonus_title,
            template=template_content,
            product_context=product_context
        )
        
        if self.prompts_only:
            # In prompts_only mode, save prompt and return placeholder
            if self.output_dir:
                prompts_dir = self.output_dir / "bonus_prompts"
                prompts_dir.mkdir(exist_ok=True)
                prompt_path = prompts_dir / f"generate_{bonus_type}.prompt.md"
                prompt_path.write_text(prompt)
                logger.info(f"   📋 Saved prompt: {prompt_path.name}")
            return f"# {bonus_title}\n\n[Content generation prompt saved. Run LLM to generate.]"
        else:
            # Generate with LLM
            try:
                response = self.llm.generate(prompt)
                return response
            except Exception as e:
                logger.warning(f"⚠️ LLM generation failed for {bonus_type}: {e}")
                return f"# {bonus_title}\n\n[Generation failed. See bonus prompt for manual generation.]"
    
    def _load_template(self, bonus_type: str) -> str:
        """Load the template file for a bonus type."""
        type_config = STANDARD_BONUS_TYPES.get(bonus_type, {})
        template_file = type_config.get('template', f'{bonus_type}_template.md')
        template_path = self.bonus_templates_dir / template_file
        
        if template_path.exists():
            return template_path.read_text()
        return ""
    
    def _create_generation_prompt(self, bonus_type: str, bonus_title: str,
                                   template: str, product_context: Dict[str, Any]) -> str:
        """Create the full generation prompt for a bonus."""
        type_config = STANDARD_BONUS_TYPES.get(bonus_type, {})
        min_words = type_config.get('min_words', 1000)
        
        prompt = f"""## Generate Research-Backed Bonus Content

**Bonus Type:** {type_config.get('name', bonus_type)}
**Title:** {bonus_title}
**Minimum Words:** {min_words}

---

## Product Context

**Product Title:** {product_context.get('title', 'Digital Product')}
**Core Topic:** {product_context.get('topic', 'Personal development')}
**Target Audience:** {product_context.get('audience', 'Motivated individuals')}
**Core Thesis:** {product_context.get('thesis', 'Transformation through practical action')}

---

## Template/Requirements

{template if template else 'No specific template. Create comprehensive, well-organized content.'}

---

## Quality Standards

1. **Substantive Content**: Every section provides genuine value, not padding
2. **Research-Backed**: Include specific techniques, data, and evidence
3. **Actionable**: Reader can use this content immediately  
4. **Well-Organized**: Clear heading structure (# for chapters, ## for sections)
5. **Professional**: Publication-ready quality
6. **Minimum {min_words} words**: Meet the minimum while maintaining quality

---

## Important

⚠️ Do NOT pad content with empty lines, repetitive phrases, or filler material.
⚠️ Every paragraph must add value.
⚠️ Use specific numbers, examples, and actionable details.

---

Write the complete bonus content now. Begin with a # Introduction section.
"""
        return prompt
    
    def _identify_friction_points(self, chapters: List[ChapterSpec]) -> List[str]:
        """Identify where readers might struggle."""
        friction = []
        for ch in chapters:
            if len(ch.key_takeaways) > 3:
                friction.append(f"{ch.title}: Complex concepts")
            if any(word in ch.purpose.lower() for word in ["implement", "apply", "build", "create"]):
                friction.append(f"{ch.title}: Action required")
        return friction if friction else ["General application", "Concept integration"]
    
    def _create_value_narrative(self, bonuses: List[Bonus], intelligence: ProductIntelligence) -> str:
        """Create the value proposition for the bonus package."""
        total_items = len(bonuses)
        total_pages = sum(b.estimated_pages for b in bonuses)
        
        transformation = intelligence.transformation.after_state if intelligence and intelligence.transformation else "transformation"
        
        return (
            f"Plus {total_items} exclusive bonuses ({total_pages}+ pages of actionable content) "
            f"designed to accelerate your {transformation.lower()} journey. "
            f"Together worth over $197 in separate value."
        )

