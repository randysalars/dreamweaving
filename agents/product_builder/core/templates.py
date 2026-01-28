"""
Product Templates
Pre-configured product types for quick creation.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class ProductTemplate:
    """A pre-configured product template."""
    name: str
    description: str
    
    # Content settings
    chapters: int = 10
    words_per_chapter: int = 2000
    
    # Media
    audio: bool = False
    video: bool = False
    
    # Bonuses
    bonuses: List[str] = field(default_factory=list)
    
    # Pricing
    default_price: float = 47.00
    suggested_sale_price: Optional[float] = None
    
    # Marketing
    email_sequences: bool = True
    social_posts: bool = True
    
    # Style
    style: str = "dreamweaving"
    
    def to_args(self) -> Dict[str, Any]:
        """Convert template to CLI argument dict."""
        return {
            "pdf": True,
            "audio": self.audio,
            "video": self.video,
            "landing_page": True,
            "emails": self.email_sequences,
            "social": self.social_posts,
            "style": self.style,
        }


# Available templates
TEMPLATES: Dict[str, ProductTemplate] = {
    "ebook": ProductTemplate(
        name="Standard eBook",
        description="12-chapter PDF eBook with 3 bonus PDFs",
        chapters=12,
        words_per_chapter=2000,
        audio=False,
        video=False,
        bonuses=["Quick Start Guide", "Action Checklist", "Workbook"],
        default_price=29.00,
        suggested_sale_price=19.99,
    ),
    
    "premium-ebook": ProductTemplate(
        name="Premium eBook",
        description="20-chapter PDF with audio narration and 5 bonuses",
        chapters=20,
        words_per_chapter=2500,
        audio=True,
        video=False,
        bonuses=[
            "Quick Start Guide",
            "Action Checklist", 
            "Workbook",
            "Resource Library",
            "Bonus Chapter: Advanced Techniques"
        ],
        default_price=47.00,
        suggested_sale_price=29.99,
    ),
    
    "audio-pack": ProductTemplate(
        name="Audio Pack",
        description="8-session audio program with companion guide",
        chapters=8,
        words_per_chapter=1500,  # Shorter for audio pacing
        audio=True,
        video=False,
        bonuses=["Companion Guide PDF", "Session Transcripts"],
        default_price=37.00,
        suggested_sale_price=24.99,
        style="meditative",
    ),
    
    "video-course": ProductTemplate(
        name="Video Course",
        description="10-module video course with workbooks",
        chapters=10,
        words_per_chapter=1200,  # Script length
        audio=True,
        video=True,
        bonuses=[
            "Course Workbook",
            "Quick Reference Cards",
            "Resource Library",
            "Certificate of Completion",
            "Bonus Module: Implementation Guide"
        ],
        default_price=97.00,
        suggested_sale_price=67.00,
    ),
    
    "mini-course": ProductTemplate(
        name="Mini Course",
        description="5-lesson quick-start course",
        chapters=5,
        words_per_chapter=1500,
        audio=False,
        video=False,
        bonuses=["Action Checklist"],
        default_price=19.00,
        suggested_sale_price=12.99,
    ),
    
    "lead-magnet": ProductTemplate(
        name="Lead Magnet",
        description="Free PDF lead magnet (10-15 pages)",
        chapters=1,
        words_per_chapter=3000,
        audio=False,
        video=False,
        bonuses=[],
        default_price=0.00,
        suggested_sale_price=None,
        email_sequences=True,  # Welcome sequence only
        social_posts=False,
    ),
    
    "masterclass": ProductTemplate(
        name="Masterclass",
        description="Comprehensive 15-module deep dive with all media",
        chapters=15,
        words_per_chapter=3000,
        audio=True,
        video=True,
        bonuses=[
            "Complete Workbook",
            "Quick Reference Cards",
            "Implementation Templates",
            "Resource Library",
            "Bonus Module: Case Studies",
            "Private Community Access Guide",
            "Certificate of Completion"
        ],
        default_price=197.00,
        suggested_sale_price=127.00,
    ),
}


def get_template(name: str) -> Optional[ProductTemplate]:
    """Get a template by name."""
    return TEMPLATES.get(name.lower())


def list_templates() -> List[ProductTemplate]:
    """List all available templates."""
    return list(TEMPLATES.values())


def get_template_names() -> List[str]:
    """Get list of template names."""
    return list(TEMPLATES.keys())


def format_template_list() -> str:
    """Format templates for display."""
    lines = ["Available Templates:", ""]
    
    for key, template in TEMPLATES.items():
        audio_icon = "🔊" if template.audio else "  "
        video_icon = "📹" if template.video else "  "
        price = f"${template.default_price:.0f}" if template.default_price > 0 else "FREE"
        
        lines.append(f"  {key:15} {audio_icon} {video_icon}  ${template.default_price:>6.0f}  {template.description}")
    
    lines.append("")
    lines.append("Usage: product-builder create --template <name> --topic \"your topic\"")
    
    return "\n".join(lines)
