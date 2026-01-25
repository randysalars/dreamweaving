"""
Enhanced Landing Page Content Schema.

Comprehensive dataclasses for conversion-optimized landing page content
including CRO psychology elements and structured sections.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class HeroSection:
    """The opening section that captures attention."""
    hook: str  # Pattern interrupt question/statement
    headline: str  # Main benefit-driven headline
    subheadline: str  # Supporting statement
    cta_primary: str  # Main call-to-action text
    cta_secondary: Optional[str] = None  # Secondary CTA (e.g., "See What's Inside")
    hero_image: Optional[str] = None  # Path to hero image


@dataclass
class PainAgitation:
    """Amplify the problem before presenting the solution."""
    opener: str  # "You've tried everything..."
    pain_points: List[str]  # List of frustrations
    agitation: str  # "And it's not your fault..."
    bridge: str  # Transition to solution


@dataclass
class Feature:
    """A single feature/benefit item."""
    icon: str  # Emoji or icon class
    title: str  # Feature name
    description: str  # Benefit-driven description


@dataclass
class SolutionSection:
    """The product presentation section."""
    intro: str  # "Introducing..."
    product_name: str
    features: List[Feature]
    differentiator: str  # "Unlike other programs..."
    product_image: Optional[str] = None


@dataclass
class Stat:
    """A social proof statistic."""
    number: str  # "10,000+"
    label: str  # "Students Enrolled"


@dataclass
class Testimonial:
    """A customer testimonial."""
    quote: str
    author: str
    role: str
    image: Optional[str] = None
    rating: Optional[int] = 5  # 1-5 stars


@dataclass
class SocialProofSection:
    """Credibility and trust markers."""
    stats: List[Stat]
    testimonials: List[Testimonial]
    logos: List[str] = field(default_factory=list)  # "As seen on..."


@dataclass
class Bonus:
    """A product bonus."""
    title: str
    value: str  # e.g., "97.00"
    description: str
    format: str = "pdf"  # pdf, video, audio, template


@dataclass
class RiskReversal:
    """Guarantee and refund information."""
    guarantee_type: str  # "30-day money-back"
    guarantee_copy: str  # Full guarantee statement
    badge_text: Optional[str] = "100% Risk-Free"


@dataclass
class UrgencyElement:
    """Scarcity and urgency drivers."""
    urgency_type: str  # "limited_time", "limited_quantity", "price_increase"
    message: str
    deadline: Optional[str] = None  # ISO date or countdown text


@dataclass
class FAQItem:
    """A single FAQ entry."""
    question: str
    answer: str


@dataclass
class AboutSection:
    """Creator/author information."""
    name: str
    bio: str
    credentials: List[str] = field(default_factory=list)
    image: Optional[str] = None


@dataclass
class PricingTier:
    """A pricing option."""
    name: str  # "Basic", "Pro", "VIP"
    price: str  # "$47"
    original_price: Optional[str] = None  # For strikethrough
    features: List[str] = field(default_factory=list)
    is_featured: bool = False
    cta_text: str = "Get Access"


@dataclass
class FooterCTA:
    """Final call-to-action section."""
    headline: str
    subheadline: Optional[str] = None
    cta_text: str = "Get Started Now"


@dataclass
class LandingPageContent:
    """Complete landing page content structure."""
    # Required sections
    hero: HeroSection
    solution: SolutionSection
    bonuses: List[Bonus]
    faq: List[FAQItem]
    footer_cta: FooterCTA
    
    # Optional but recommended
    pain_agitation: Optional[PainAgitation] = None
    social_proof: Optional[SocialProofSection] = None
    risk_reversal: Optional[RiskReversal] = None
    urgency: Optional[UrgencyElement] = None
    about: Optional[AboutSection] = None
    pricing: Optional[List[PricingTier]] = None
    
    # Meta
    page_title: str = ""
    meta_description: str = ""
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        import dataclasses
        return dataclasses.asdict(self)
