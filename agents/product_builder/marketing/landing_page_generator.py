"""
Landing Page Generator
Creates high-converting sales pages for products.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field

from ..core.llm import LLMClient
from ..schemas.positioning_brief import PositioningBrief
from ..schemas.transformation_map import TransformationMap

logger = logging.getLogger(__name__)


@dataclass
class Testimonial:
    """Customer testimonial."""
    name: str
    role: str
    quote: str
    result: str = ""
    avatar_url: str = ""


@dataclass
class PricingTier:
    """Pricing option."""
    name: str
    price: str
    description: str
    features: List[str]
    is_featured: bool = False
    cta_text: str = "Get Started"


@dataclass
class FAQ:
    """Frequently asked question."""
    question: str
    answer: str


@dataclass
class LandingPageContent:
    """Complete landing page content."""
    # Hero
    headline: str
    subheadline: str
    hero_cta: str = "Get Instant Access"
    
    # Problem/Agitation
    problem_headline: str = ""
    pain_points: List[str] = field(default_factory=list)
    
    # Solution
    solution_headline: str = ""
    solution_description: str = ""
    
    # Transformation
    before_state: List[str] = field(default_factory=list)
    after_state: List[str] = field(default_factory=list)
    
    # Features/Benefits
    features: List[Dict[str, str]] = field(default_factory=list)
    
    # Social Proof
    testimonials: List[Testimonial] = field(default_factory=list)
    stats: List[Dict[str, str]] = field(default_factory=list)
    
    # Curriculum/Contents
    modules: List[Dict[str, str]] = field(default_factory=list)
    
    # Bonuses
    bonuses: List[Dict[str, str]] = field(default_factory=list)
    
    # Pricing
    pricing_tiers: List[PricingTier] = field(default_factory=list)
    
    # Guarantee
    guarantee_headline: str = "100% Satisfaction Guarantee"
    guarantee_text: str = ""
    
    # FAQ
    faqs: List[FAQ] = field(default_factory=list)
    
    # Urgency
    urgency_text: str = ""
    
    # Final CTA
    final_headline: str = ""
    final_cta: str = "Get Started Now"
    
    # Meta
    meta_title: str = ""
    meta_description: str = ""


class LandingPageGenerator:
    """
    Generates high-converting landing pages for products.
    
    Based on proven copywriting frameworks:
    - PAS (Problem-Agitation-Solution)
    - AIDA (Attention-Interest-Desire-Action)
    - StoryBrand framework
    """
    
    def __init__(self, templates_dir: Path = None):
        self.templates_dir = templates_dir or Path(__file__).parent.parent / "templates"
        self.llm = LLMClient()
    
    def generate(
        self,
        title: str,
        positioning: PositioningBrief,
        transformation: TransformationMap,
        chapters: List[Dict] = None,
        bonuses: List[Dict] = None
    ) -> LandingPageContent:
        """
        Generate complete landing page content.
        
        Args:
            title: Product title
            positioning: Positioning brief
            transformation: Transformation map
            chapters: List of chapter details
            bonuses: List of bonus details
            
        Returns:
            LandingPageContent with all sections
        """
        logger.info(f"📄 Generating landing page for: {title}")
        
        content = LandingPageContent(
            headline=self._generate_headline(title, positioning),
            subheadline=positioning.core_promise,
            meta_title=f"{title} | {positioning.core_promise[:50]}",
            meta_description=positioning.positioning_statement
        )
        
        # Problem section
        content.problem_headline = self._generate_problem_headline(positioning)
        content.pain_points = positioning.audience.pain_points[:5]
        
        # Solution
        content.solution_headline = f"Introducing {title}"
        content.solution_description = positioning.positioning_statement
        
        # Transformation
        content.before_state = [transformation.starting_state] if isinstance(transformation.starting_state, str) else transformation.starting_state[:4]
        content.after_state = [transformation.ending_state] if isinstance(transformation.ending_state, str) else transformation.ending_state[:4]
        
        # Features from belief shifts and skills
        content.features = [
            {"title": shift.split("→")[1].strip() if "→" in shift else shift, 
             "description": f"Transform from {shift.split('→')[0].strip()}" if "→" in shift else shift}
            for shift in transformation.belief_shifts[:6]
        ]
        
        # Modules from chapters
        if chapters:
            content.modules = [
                {"title": ch.get("title", f"Module {i+1}"), 
                 "description": ch.get("purpose", "")}
                for i, ch in enumerate(chapters)
            ]
        
        # Bonuses
        if bonuses:
            content.bonuses = bonuses[:4]
        
        # Generate FAQs from objections
        content.faqs = [
            FAQ(question=obj.objection, answer=obj.preemption)
            for obj in positioning.objections[:6]
        ]
        
        # Guarantee
        content.guarantee_text = "Try the entire program risk-free. If you don't see results within 30 days, we'll refund every penny. No questions asked."
        
        # Final CTA
        content.final_headline = f"Ready to {positioning.core_promise.lower()}?"
        
        logger.info("✅ Landing page content generated")
        return content
    
    def _generate_headline(self, title: str, positioning: PositioningBrief) -> str:
        """Generate a compelling headline."""
        prompt = f"""
Create a compelling headline for a product called "{title}".

Core promise: {positioning.core_promise}
Target audience: {positioning.audience.primary_persona}
Differentiator: {positioning.differentiator}

Rules:
- Maximum 10 words
- Speak to the transformation
- Be specific, not generic
- Avoid hype words like "revolutionary" or "game-changing"

Return ONLY the headline, no quotes.
"""
        return self.llm.generate(prompt, max_tokens=50).strip()
    
    def _generate_problem_headline(self, positioning: PositioningBrief) -> str:
        """Generate problem section headline."""
        pain = positioning.audience.pain_points[0] if positioning.audience.pain_points else "stuck"
        return f"Tired of feeling {pain.lower().replace('feeling ', '')}?"
    
    def render_html(self, content: LandingPageContent, style: str = "modern") -> str:
        """
        Render landing page content to HTML.
        
        Args:
            content: LandingPageContent
            style: "modern", "minimal", "bold"
            
        Returns:
            Complete HTML string
        """
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{content.meta_title}</title>
    <meta name="description" content="{content.meta_description}">
    <style>
{self._get_css(style)}
    </style>
</head>
<body>
    <!-- Hero Section -->
    <header class="hero">
        <div class="container">
            <h1>{content.headline}</h1>
            <p class="subheadline">{content.subheadline}</p>
            <a href="#pricing" class="cta-button">{content.hero_cta}</a>
        </div>
    </header>

    <!-- Problem Section -->
    <section class="problem">
        <div class="container">
            <h2>{content.problem_headline}</h2>
            <ul class="pain-points">
                {"".join(f'<li>❌ {pain}</li>' for pain in content.pain_points)}
            </ul>
        </div>
    </section>

    <!-- Solution Section -->
    <section class="solution">
        <div class="container">
            <h2>{content.solution_headline}</h2>
            <p>{content.solution_description}</p>
        </div>
    </section>

    <!-- Transformation Section -->
    <section class="transformation">
        <div class="container">
            <h2>The Transformation</h2>
            <div class="before-after">
                <div class="before">
                    <h3>Before</h3>
                    <ul>{"".join(f'<li>{item}</li>' for item in content.before_state)}</ul>
                </div>
                <div class="arrow">→</div>
                <div class="after">
                    <h3>After</h3>
                    <ul>{"".join(f'<li>{item}</li>' for item in content.after_state)}</ul>
                </div>
            </div>
        </div>
    </section>

    <!-- Features Section -->
    <section class="features">
        <div class="container">
            <h2>What You'll Learn</h2>
            <div class="features-grid">
                {"".join(f'''
                <div class="feature">
                    <h3>{f["title"]}</h3>
                    <p>{f.get("description", "")}</p>
                </div>
                ''' for f in content.features)}
            </div>
        </div>
    </section>

    <!-- Modules Section -->
    {self._render_modules(content.modules) if content.modules else ""}

    <!-- Bonuses Section -->
    {self._render_bonuses(content.bonuses) if content.bonuses else ""}

    <!-- FAQ Section -->
    <section class="faq">
        <div class="container">
            <h2>Frequently Asked Questions</h2>
            <div class="faq-list">
                {"".join(f'''
                <div class="faq-item">
                    <h3>{faq.question}</h3>
                    <p>{faq.answer}</p>
                </div>
                ''' for faq in content.faqs)}
            </div>
        </div>
    </section>

    <!-- Guarantee Section -->
    <section class="guarantee">
        <div class="container">
            <h2>{content.guarantee_headline}</h2>
            <p>{content.guarantee_text}</p>
        </div>
    </section>

    <!-- Final CTA Section -->
    <section class="final-cta" id="pricing">
        <div class="container">
            <h2>{content.final_headline}</h2>
            <a href="#" class="cta-button cta-large">{content.final_cta}</a>
        </div>
    </section>

    <footer>
        <div class="container">
            <p>&copy; {__import__('datetime').datetime.now().year} SalarsNet. All rights reserved.</p>
        </div>
    </footer>
</body>
</html>
"""
    
    def _render_modules(self, modules: List[Dict]) -> str:
        """Render modules/curriculum section."""
        items = "".join(f'''
        <div class="module">
            <h3>{m["title"]}</h3>
            <p>{m.get("description", "")}</p>
        </div>
        ''' for m in modules)
        
        return f'''
    <section class="modules">
        <div class="container">
            <h2>What's Inside</h2>
            <div class="modules-list">{items}</div>
        </div>
    </section>
'''
    
    def _render_bonuses(self, bonuses: List[Dict]) -> str:
        """Render bonuses section."""
        items = "".join(f'''
        <div class="bonus">
            <h3>🎁 {b.get("title", b.get("name", "Bonus"))}</h3>
            <p>{b.get("description", "")}</p>
        </div>
        ''' for b in bonuses)
        
        return f'''
    <section class="bonuses">
        <div class="container">
            <h2>Plus These Bonuses</h2>
            <div class="bonuses-grid">{items}</div>
        </div>
    </section>
'''
    
    def _get_css(self, style: str) -> str:
        """Get CSS for the landing page."""
        return """
:root {
    --primary: #9F7AEA;
    --primary-dark: #7C3AED;
    --text: #1a202c;
    --text-light: #4a5568;
    --bg: #ffffff;
    --bg-alt: #f7fafc;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: 'Inter', system-ui, sans-serif;
    color: var(--text);
    line-height: 1.6;
}

.container {
    max-width: 1100px;
    margin: 0 auto;
    padding: 0 24px;
}

section {
    padding: 80px 0;
}

h1, h2, h3 { font-weight: 700; }
h1 { font-size: 3rem; line-height: 1.2; }
h2 { font-size: 2rem; margin-bottom: 24px; text-align: center; }
h3 { font-size: 1.25rem; margin-bottom: 12px; }

.hero {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    text-align: center;
    padding: 120px 24px;
}

.subheadline {
    font-size: 1.5rem;
    opacity: 0.9;
    margin: 24px 0 40px;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
}

.cta-button {
    display: inline-block;
    background: white;
    color: var(--primary-dark);
    padding: 16px 40px;
    border-radius: 8px;
    font-weight: 600;
    text-decoration: none;
    font-size: 1.125rem;
    transition: transform 0.2s, box-shadow 0.2s;
}

.cta-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

.cta-large {
    background: var(--primary);
    color: white;
    padding: 20px 60px;
    font-size: 1.25rem;
}

.problem { background: var(--bg-alt); }

.pain-points {
    list-style: none;
    max-width: 600px;
    margin: 0 auto;
}

.pain-points li {
    padding: 12px 0;
    font-size: 1.125rem;
    color: var(--text-light);
}

.transformation { background: var(--bg); }

.before-after {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 40px;
    flex-wrap: wrap;
}

.before, .after {
    flex: 1;
    min-width: 280px;
    padding: 32px;
    border-radius: 12px;
}

.before { background: #fed7d7; }
.after { background: #c6f6d5; }

.arrow {
    font-size: 3rem;
    color: var(--primary);
}

.features { background: var(--bg-alt); }

.features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 32px;
}

.feature {
    background: white;
    padding: 32px;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.05);
}

.modules, .bonuses { background: var(--bg); }

.faq { background: var(--bg-alt); }

.faq-item {
    max-width: 700px;
    margin: 0 auto 24px;
    padding: 24px;
    background: white;
    border-radius: 8px;
}

.guarantee {
    background: var(--primary);
    color: white;
    text-align: center;
}

.final-cta {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    color: white;
    text-align: center;
}

footer {
    background: var(--text);
    color: white;
    padding: 24px;
    text-align: center;
}
"""
