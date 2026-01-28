"""
Antigravity-Native Workflow Enhancements
Interactive wizard, prompt management, and response tracking.
"""

import json
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class PromptSpec:
    """Specification for a prompt to be generated."""
    id: str
    title: str
    description: str
    word_count: int = 2000
    category: str = "chapter"  # chapter, bonus, marketing, positioning
    order: int = 0
    dependencies: List[str] = field(default_factory=list)


@dataclass 
class ProductSpec:
    """Complete specification for a product."""
    title: str
    topic: str
    subtitle: str = ""
    target_audience: str = ""
    transformation: str = ""  # What transformation does reader achieve?
    pain_points: List[str] = field(default_factory=list)
    unique_angle: str = ""
    tone: str = "conversational, warm, expert"
    chapter_count: int = 10
    words_per_chapter: int = 2000
    include_audio: bool = False
    include_video: bool = False
    bonuses: List[str] = field(default_factory=list)
    price: float = 47.00
    
    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "topic": self.topic,
            "subtitle": self.subtitle,
            "target_audience": self.target_audience,
            "transformation": self.transformation,
            "pain_points": self.pain_points,
            "unique_angle": self.unique_angle,
            "tone": self.tone,
            "chapter_count": self.chapter_count,
            "words_per_chapter": self.words_per_chapter,
            "include_audio": self.include_audio,
            "include_video": self.include_video,
            "bonuses": self.bonuses,
            "price": self.price,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ProductSpec':
        return cls(**data)


def run_wizard() -> Optional[ProductSpec]:
    """
    Interactive wizard to build a product spec.
    Returns None if cancelled.
    """
    print("\n" + "═" * 60)
    print("   🧙 EPISTEMIC FACTORY — PRODUCT WIZARD")
    print("═" * 60)
    print("\nI'll ask you a few questions to create the perfect product.\n")
    print("(Press Ctrl+C to cancel at any time)\n")
    
    try:
        # Core info
        topic = input("📚 What's the main topic? (e.g., 'meditation for beginners')\n   → ").strip()
        if not topic:
            print("Topic is required!")
            return None
            
        title = input(f"\n📖 What's the product title? (default: based on topic)\n   → ").strip()
        if not title:
            # Generate a title from topic
            words = topic.split()
            title = " ".join(word.capitalize() for word in words[:4]) + " Guide"
        
        subtitle = input(f"\n✨ Subtitle/tagline? (optional)\n   → ").strip()
        
        # Target audience
        print(f"\n👥 Who is this for? Examples:")
        print("   • Busy professionals who want to reduce stress")
        print("   • Beginners with no prior experience")
        print("   • Parents looking for quick daily practices")
        target_audience = input("   → ").strip() or "Anyone interested in this topic"
        
        # Transformation
        print(f"\n🦋 What transformation does the reader achieve?")
        print("   Example: 'From stressed and overwhelmed to calm and focused'")
        transformation = input("   → ").strip() or f"Master {topic}"
        
        # Pain points
        print(f"\n😣 What pain points does this solve? (comma-separated)")
        print("   Example: 'can't focus, constant anxiety, poor sleep'")
        pain_input = input("   → ").strip()
        pain_points = [p.strip() for p in pain_input.split(",")] if pain_input else []
        
        # Unique angle
        print(f"\n💡 What's your unique angle or approach?")
        print("   Example: 'Science-backed techniques from neuroscience research'")
        unique_angle = input("   → ").strip() or "Practical, actionable approach"
        
        # Tone
        print(f"\n🎭 What tone should the content have?")
        print("   1. Conversational and warm")
        print("   2. Professional and authoritative")
        print("   3. Friendly and encouraging")
        print("   4. Academic and research-focused")
        print("   5. Custom (describe)")
        tone_choice = input("   → (1-5, default: 1): ").strip()
        tone_map = {
            "1": "conversational, warm, like a trusted friend",
            "2": "professional, authoritative, expert",
            "3": "friendly, encouraging, supportive coach",
            "4": "academic, research-based, evidence-driven",
        }
        if tone_choice == "5":
            tone = input("   Describe your custom tone: ").strip()
        else:
            tone = tone_map.get(tone_choice, tone_map["1"])
        
        # Structure
        print(f"\n📊 Product structure:")
        chapters_input = input("   How many chapters? (default: 10): ").strip()
        chapter_count = int(chapters_input) if chapters_input.isdigit() else 10
        
        words_input = input("   Words per chapter? (default: 2000): ").strip()
        words_per_chapter = int(words_input) if words_input.isdigit() else 2000
        
        # Media
        print(f"\n🎬 Include additional media?")
        include_audio = input("   Audio narration? (y/N): ").strip().lower() == 'y'
        include_video = input("   Video content? (y/N): ").strip().lower() == 'y'
        
        # Bonuses
        print(f"\n🎁 What bonus materials? (comma-separated, or press Enter for defaults)")
        print("   Examples: Quick Start Guide, Checklist, Workbook, Templates")
        bonus_input = input("   → ").strip()
        if bonus_input:
            bonuses = [b.strip() for b in bonus_input.split(",")]
        else:
            bonuses = ["Quick Start Guide", "Action Checklist", "Workbook"]
        
        # Price
        price_input = input(f"\n💰 Price? (default: $47): $").strip()
        price = float(price_input) if price_input else 47.00
        
        # Summary
        print("\n" + "═" * 60)
        print("   📋 PRODUCT SUMMARY")
        print("═" * 60)
        print(f"\n   Title: {title}")
        print(f"   Subtitle: {subtitle or '(none)'}")
        print(f"   Topic: {topic}")
        print(f"   Audience: {target_audience}")
        print(f"   Transformation: {transformation}")
        print(f"   Chapters: {chapter_count} × {words_per_chapter} words")
        print(f"   Audio: {'Yes' if include_audio else 'No'}")
        print(f"   Video: {'Yes' if include_video else 'No'}")
        print(f"   Bonuses: {', '.join(bonuses)}")
        print(f"   Price: ${price:.2f}")
        print("")
        
        confirm = input("   Create this product? (Y/n): ").strip().lower()
        if confirm == 'n':
            print("\n   Cancelled.")
            return None
        
        return ProductSpec(
            title=title,
            topic=topic,
            subtitle=subtitle,
            target_audience=target_audience,
            transformation=transformation,
            pain_points=pain_points,
            unique_angle=unique_angle,
            tone=tone,
            chapter_count=chapter_count,
            words_per_chapter=words_per_chapter,
            include_audio=include_audio,
            include_video=include_video,
            bonuses=bonuses,
            price=price,
        )
        
    except KeyboardInterrupt:
        print("\n\n   Cancelled.")
        return None
    except EOFError:
        print("\n\n   Cancelled (non-interactive mode).")
        return None


@dataclass
class ResponseStatus:
    """Status of a response to a prompt."""
    prompt_file: str
    response_file: Optional[str]
    word_count: int = 0
    status: str = "pending"  # pending, partial, complete


def check_responses(product_dir: Path) -> List[ResponseStatus]:
    """Check which prompts have responses and their status."""
    prompts_dir = product_dir / "output" / "prompts"
    responses_dir = product_dir / "output" / "responses"
    
    if not prompts_dir.exists():
        return []
    
    results = []
    
    for prompt_file in sorted(prompts_dir.glob("*.prompt.md")):
        # Find matching response
        slug = prompt_file.stem.replace(".prompt", "")
        response_file = responses_dir / f"{slug}.response.md"
        
        status = ResponseStatus(
            prompt_file=prompt_file.name,
            response_file=None,
            word_count=0,
            status="pending"
        )
        
        if response_file.exists():
            status.response_file = response_file.name
            content = response_file.read_text()
            status.word_count = len(content.split())
            
            if status.word_count >= 1500:
                status.status = "complete"
            elif status.word_count >= 500:
                status.status = "partial"
            else:
                status.status = "started"
        
        results.append(status)
    
    return results


def format_response_status(statuses: List[ResponseStatus]) -> str:
    """Format response status for display."""
    lines = [
        "",
        "╔" + "═" * 68 + "╗",
        "║" + " " * 20 + "RESPONSE STATUS" + " " * 33 + "║",
        "╠" + "═" * 68 + "╣",
        "║ {:40} │ {:10} │ {:10} ║".format("Prompt", "Status", "Words"),
        "╠" + "─" * 68 + "╣",
    ]
    
    status_icons = {
        "complete": "✅",
        "partial": "🔶",
        "started": "🔵",
        "pending": "⏳",
    }
    
    complete = 0
    partial = 0
    pending = 0
    total_words = 0
    
    for s in statuses:
        icon = status_icons.get(s.status, "❓")
        name = s.prompt_file.replace(".prompt.md", "")[:38]
        words = str(s.word_count) if s.word_count > 0 else "-"
        lines.append("║ {:40} │ {} {:8} │ {:10} ║".format(name, icon, s.status, words))
        
        if s.status == "complete":
            complete += 1
        elif s.status in ["partial", "started"]:
            partial += 1
        else:
            pending += 1
        total_words += s.word_count
    
    lines.append("╠" + "═" * 68 + "╣")
    lines.append("║ Complete: {:3} │ In Progress: {:3} │ Pending: {:3} │ Words: {:6} ║".format(
        complete, partial, pending, total_words
    ))
    lines.append("╚" + "═" * 68 + "╝")
    
    return "\n".join(lines)


def generate_antigravity_export(product_dir: Path) -> str:
    """
    Generate a formatted export of all prompts for easy copy-paste into Antigravity.
    """
    prompts_dir = product_dir / "output" / "prompts"
    
    if not prompts_dir.exists():
        return "No prompts found."
    
    prompt_files = sorted(prompts_dir.glob("*.prompt.md"))
    
    if not prompt_files:
        return "No prompts found."
    
    lines = [
        "# Antigravity Prompt Queue",
        f"# Product: {product_dir.name}",
        f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"# Prompts: {len(prompt_files)}",
        "",
        "---",
        "",
    ]
    
    for i, prompt_file in enumerate(prompt_files, 1):
        content = prompt_file.read_text()
        slug = prompt_file.stem.replace(".prompt", "")
        
        lines.append(f"## Prompt {i}/{len(prompt_files)}: {slug}")
        lines.append("")
        lines.append("```")
        lines.append(content.strip())
        lines.append("```")
        lines.append("")
        lines.append(f"**Save response to:** `output/responses/{slug}.response.md`")
        lines.append("")
        lines.append("---")
        lines.append("")
    
    return "\n".join(lines)


def preview_prompts(topic: str, title: str, template: str = None, 
                    chapter_count: int = 10) -> List[PromptSpec]:
    """
    Preview what prompts would be generated without creating files.
    """
    prompts = []
    
    # Positioning prompts
    prompts.append(PromptSpec(
        id="market_positioning",
        title="Market Positioning",
        description=f"Define the unique positioning for '{title}' in the {topic} market",
        word_count=500,
        category="positioning",
        order=0,
    ))
    
    prompts.append(PromptSpec(
        id="curriculum_design",
        title="Curriculum Design",
        description=f"Design the learning journey and chapter outline",
        word_count=800,
        category="positioning",
        order=1,
    ))
    
    prompts.append(PromptSpec(
        id="voice_style",
        title="Voice & Style Guide",
        description=f"Define the writing voice, tone, and style guidelines",
        word_count=400,
        category="positioning",
        order=2,
    ))
    
    # Chapter prompts
    for i in range(1, chapter_count + 1):
        prompts.append(PromptSpec(
            id=f"chapter_{i:02d}",
            title=f"Chapter {i}",
            description=f"Chapter {i} content (2000+ words)",
            word_count=2000,
            category="chapter",
            order=10 + i,
        ))
    
    # Bonus prompts
    bonus_topics = ["Quick Start Guide", "Action Checklist", "Workbook"]
    for i, bonus in enumerate(bonus_topics, 1):
        prompts.append(PromptSpec(
            id=f"bonus_{i:02d}",
            title=bonus,
            description=f"Bonus material: {bonus}",
            word_count=1500,
            category="bonus",
            order=100 + i,
        ))
    
    # Marketing prompts
    prompts.append(PromptSpec(
        id="landing_page",
        title="Landing Page Copy",
        description="High-converting landing page content",
        word_count=1500,
        category="marketing",
        order=200,
    ))
    
    return prompts


def format_prompt_preview(prompts: List[PromptSpec]) -> str:
    """Format prompt preview for display."""
    lines = [
        "",
        "╔" + "═" * 68 + "╗",
        "║" + " " * 20 + "PROMPT PREVIEW" + " " * 34 + "║",
        "╠" + "═" * 68 + "╣",
    ]
    
    category_icons = {
        "positioning": "🎯",
        "chapter": "📖",
        "bonus": "🎁",
        "marketing": "📣",
    }
    
    current_category = None
    total_words = 0
    
    for p in sorted(prompts, key=lambda x: x.order):
        if p.category != current_category:
            current_category = p.category
            icon = category_icons.get(p.category, "📄")
            lines.append(f"║ {icon} {p.category.upper():65} ║")
        
        lines.append("║   {:40} │ {:20} ║".format(
            p.title[:40], 
            f"~{p.word_count} words"
        ))
        total_words += p.word_count
    
    lines.append("╠" + "═" * 68 + "╣")
    lines.append("║ Total: {:3} prompts │ Estimated words: {:,}{}║".format(
        len(prompts), total_words, " " * 23
    ))
    lines.append("╚" + "═" * 68 + "╝")
    
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════
# STEP 3: CONTENT GENERATION HELPERS
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class NextPromptResult:
    """Result of finding the next prompt to work on."""
    prompt_file: Path
    prompt_content: str
    prompt_number: int
    total_prompts: int
    response_file: Path
    previous_completed: int
    estimated_words: int


def get_next_prompt(product_dir: Path) -> Optional[NextPromptResult]:
    """Find the next prompt that needs a response."""
    prompts_dir = product_dir / "output" / "prompts"
    responses_dir = product_dir / "output" / "responses"
    
    if not prompts_dir.exists():
        return None
    
    # Ensure responses directory exists
    responses_dir.mkdir(parents=True, exist_ok=True)
    
    prompt_files = sorted(prompts_dir.glob("*.prompt.md"))
    
    if not prompt_files:
        return None
    
    completed = 0
    for i, prompt_file in enumerate(prompt_files):
        slug = prompt_file.stem.replace(".prompt", "")
        response_file = responses_dir / f"{slug}.response.md"
        
        if response_file.exists():
            content = response_file.read_text()
            word_count = len(content.split())
            if word_count >= 1500:
                completed += 1
                continue
        
        # This is the next prompt to work on
        return NextPromptResult(
            prompt_file=prompt_file,
            prompt_content=prompt_file.read_text(),
            prompt_number=i + 1,
            total_prompts=len(prompt_files),
            response_file=response_file,
            previous_completed=completed,
            estimated_words=2000,
        )
    
    # All done!
    return None


def format_next_prompt(result: NextPromptResult) -> str:
    """Format next prompt for display."""
    lines = [
        "",
        "╔" + "═" * 68 + "╗",
        "║" + " " * 15 + f"PROMPT {result.prompt_number}/{result.total_prompts}" + " " * 36 + "║",
        "╠" + "═" * 68 + "╣",
        "",
    ]
    
    # Show progress bar
    progress = result.previous_completed / result.total_prompts
    bar_width = 50
    filled = int(bar_width * progress)
    bar = "█" * filled + "░" * (bar_width - filled)
    lines.append(f"  Progress: [{bar}] {result.previous_completed}/{result.total_prompts}")
    lines.append("")
    lines.append("─" * 68)
    lines.append("")
    
    # Show the prompt
    lines.append(result.prompt_content.strip())
    lines.append("")
    lines.append("─" * 68)
    lines.append("")
    lines.append(f"📝 Save your response to:")
    lines.append(f"   {result.response_file}")
    lines.append("")
    lines.append(f"💡 Target: ~{result.estimated_words} words")
    lines.append("")
    
    return "\n".join(lines)


@dataclass
class ValidationResult:
    """Result of validating a response."""
    is_valid: bool
    word_count: int
    issues: List[str]
    warnings: List[str]
    suggestions: List[str]


def validate_response(response_path: Path, min_words: int = 1500) -> ValidationResult:
    """Validate a response file for quality."""
    issues = []
    warnings = []
    suggestions = []
    
    if not response_path.exists():
        return ValidationResult(
            is_valid=False,
            word_count=0,
            issues=["File does not exist"],
            warnings=[],
            suggestions=["Create the response file first"],
        )
    
    content = response_path.read_text()
    word_count = len(content.split())
    
    # Check word count
    if word_count < min_words * 0.5:
        issues.append(f"Too short: {word_count} words (need at least {min_words})")
    elif word_count < min_words:
        warnings.append(f"Slightly short: {word_count}/{min_words} words")
    
    # Check for placeholder text
    placeholders = ["TODO", "FIXME", "TBD", "[placeholder]", "lorem ipsum", "xxx"]
    for ph in placeholders:
        if ph.lower() in content.lower():
            issues.append(f"Contains placeholder text: '{ph}'")
    
    # Check for markdown headers
    if not any(line.startswith("#") for line in content.split("\n")):
        warnings.append("No markdown headers found")
        suggestions.append("Add a # Title and ## Section headers")
    
    # Check for very short paragraphs
    paragraphs = [p for p in content.split("\n\n") if p.strip()]
    short_paras = [p for p in paragraphs if len(p.split()) < 20]
    if len(short_paras) > len(paragraphs) * 0.5:
        warnings.append("Many very short paragraphs")
        suggestions.append("Consider expanding paragraphs with more detail")
    
    # Check for repetitive starts
    sentences = [s.strip() for s in content.replace("\n", " ").split(".") if s.strip()]
    if len(sentences) >= 5:
        first_words = [s.split()[0].lower() if s.split() else "" for s in sentences[:10]]
        most_common = max(set(first_words), key=first_words.count)
        if first_words.count(most_common) >= 4:
            suggestions.append(f"Vary sentence openers ('{most_common}' used frequently)")
    
    is_valid = len(issues) == 0 and word_count >= min_words * 0.7
    
    return ValidationResult(
        is_valid=is_valid,
        word_count=word_count,
        issues=issues,
        warnings=warnings,
        suggestions=suggestions,
    )


def format_validation_result(result: ValidationResult, filename: str) -> str:
    """Format validation result for display."""
    lines = [
        "",
        "╔" + "═" * 68 + "╗",
        "║" + " " * 20 + "RESPONSE VALIDATION" + " " * 29 + "║",
        "╠" + "═" * 68 + "╣",
    ]
    
    status = "✅ VALID" if result.is_valid else "❌ NEEDS WORK"
    lines.append(f"║ File: {filename[:40]:40} │ {status:14} ║")
    lines.append(f"║ Word Count: {result.word_count:5,}" + " " * 46 + "║")
    lines.append("╠" + "─" * 68 + "╣")
    
    if result.issues:
        lines.append("║ ❌ ISSUES:" + " " * 57 + "║")
        for issue in result.issues:
            lines.append(f"║    • {issue[:60]:60} ║")
    
    if result.warnings:
        lines.append("║ ⚠️ WARNINGS:" + " " * 55 + "║")
        for warning in result.warnings:
            lines.append(f"║    • {warning[:60]:60} ║")
    
    if result.suggestions:
        lines.append("║ 💡 SUGGESTIONS:" + " " * 52 + "║")
        for suggestion in result.suggestions:
            lines.append(f"║    • {suggestion[:60]:60} ║")
    
    if not result.issues and not result.warnings and not result.suggestions:
        lines.append("║ ✨ Looking great! No issues found." + " " * 33 + "║")
    
    lines.append("╚" + "═" * 68 + "╝")
    
    return "\n".join(lines)


def import_response(product_dir: Path, prompt_slug: str, 
                    content: str = None, source_file: Path = None) -> Tuple[bool, str]:
    """
    Import a response from content or a file.
    Returns (success, message).
    """
    responses_dir = product_dir / "output" / "responses"
    responses_dir.mkdir(parents=True, exist_ok=True)
    
    response_file = responses_dir / f"{prompt_slug}.response.md"
    
    if source_file:
        if not source_file.exists():
            return False, f"Source file not found: {source_file}"
        content = source_file.read_text()
    
    if not content:
        return False, "No content provided"
    
    # Validate content has reasonable length
    word_count = len(content.split())
    if word_count < 100:
        return False, f"Content too short ({word_count} words, need at least 100)"
    
    # Write the response
    response_file.write_text(content)
    
    return True, f"Saved {word_count} words to {response_file}"


def generate_response_template(prompt_file: Path) -> str:
    """Generate a response template with structure from the prompt."""
    prompt_content = prompt_file.read_text()
    slug = prompt_file.stem.replace(".prompt", "")
    
    lines = [
        f"# Response: {slug.replace('_', ' ').title()}",
        "",
        f"*Generated: {datetime.now().strftime('%Y-%m-%d')}*",
        "",
        "---",
        "",
    ]
    
    # Try to extract sections from the prompt
    if "chapter" in slug.lower():
        lines.extend([
            "## Introduction",
            "",
            "[Opening hook that draws the reader in...]",
            "",
            "## Main Content",
            "",
            "[Core teaching and concepts...]",
            "",
            "## Practical Application",
            "",
            "[How to apply this in real life...]",
            "",
            "## Key Takeaways",
            "",
            "- [Key point 1]",
            "- [Key point 2]",
            "- [Key point 3]",
            "",
            "## Action Step",
            "",
            "[One specific thing the reader should do next...]",
            "",
        ])
    elif "bonus" in slug.lower():
        lines.extend([
            "## Overview",
            "",
            "[What this bonus covers...]",
            "",
            "## Content",
            "",
            "[Main bonus content...]",
            "",
            "## How to Use",
            "",
            "[Instructions for getting the most value...]",
            "",
        ])
    else:
        lines.extend([
            "## Section 1",
            "",
            "[Content here...]",
            "",
            "## Section 2",
            "",
            "[Content here...]",
            "",
            "## Section 3",
            "",
            "[Content here...]",
            "",
        ])
    
    lines.extend([
        "---",
        "",
        f"*Word count target: ~2000 words*",
        "",
    ])
    
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════
# STEP 3A: BONUS GENERATION HELPERS
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class BonusType:
    """A type of bonus that can be generated."""
    id: str
    name: str
    description: str
    word_count: int
    format: str  # pdf, checklist, worksheet, audio_script
    estimated_time: str


# Available bonus types
BONUS_TYPES = {
    "quick_start": BonusType(
        id="quick_start",
        name="Quick Start Guide",
        description="A condensed guide to get readers started immediately",
        word_count=1500,
        format="pdf",
        estimated_time="2-3 hours"
    ),
    "checklist": BonusType(
        id="checklist",
        name="Action Checklist",
        description="Step-by-step checklist to track progress",
        word_count=500,
        format="checklist",
        estimated_time="1 hour"
    ),
    "workbook": BonusType(
        id="workbook",
        name="Interactive Workbook",
        description="Exercises and reflection prompts for deeper learning",
        word_count=3000,
        format="worksheet",
        estimated_time="4-5 hours"
    ),
    "cheat_sheet": BonusType(
        id="cheat_sheet",
        name="Cheat Sheet",
        description="One-page reference with key concepts and formulas",
        word_count=800,
        format="pdf",
        estimated_time="1-2 hours"
    ),
    "templates": BonusType(
        id="templates",
        name="Templates Pack",
        description="Ready-to-use templates for common tasks",
        word_count=1000,
        format="pdf",
        estimated_time="2-3 hours"
    ),
    "resource_guide": BonusType(
        id="resource_guide",
        name="Resource Guide",
        description="Curated list of tools, books, and resources",
        word_count=2000,
        format="pdf",
        estimated_time="2-3 hours"
    ),
    "case_studies": BonusType(
        id="case_studies",
        name="Case Studies",
        description="Real-world examples and success stories",
        word_count=2500,
        format="pdf",
        estimated_time="3-4 hours"
    ),
    "faq": BonusType(
        id="faq",
        name="FAQ Guide",
        description="Common questions and detailed answers",
        word_count=1500,
        format="pdf",
        estimated_time="2 hours"
    ),
    "audio_companion": BonusType(
        id="audio_companion",
        name="Audio Companion Script",
        description="Script for audio narration of key concepts",
        word_count=3000,
        format="audio_script",
        estimated_time="4-5 hours"
    ),
    "journal": BonusType(
        id="journal",
        name="Practice Journal",
        description="90-day journal with prompts and tracking",
        word_count=2000,
        format="worksheet",
        estimated_time="3-4 hours"
    ),
}


def list_bonus_types() -> str:
    """List all available bonus types."""
    lines = [
        "",
        "╔" + "═" * 78 + "╗",
        "║" + " " * 25 + "AVAILABLE BONUS TYPES" + " " * 32 + "║",
        "╠" + "═" * 78 + "╣",
    ]
    
    for bonus in BONUS_TYPES.values():
        lines.append(f"║ {bonus.id:15} │ {bonus.name:25} │ ~{bonus.word_count:,} words │ {bonus.estimated_time:10} ║")
    
    lines.append("╠" + "═" * 78 + "╣")
    lines.append("║ Use: product-builder bonus-prompts --product-dir ./my-product --types quick_start,checklist   ║")
    lines.append("╚" + "═" * 78 + "╝")
    
    return "\n".join(lines)


def generate_bonus_prompts(product_dir: Path, bonus_types: List[str], 
                           product_title: str = None) -> List[Path]:
    """Generate prompts for bonus content (Antigravity-native workflow)."""
    prompts_dir = product_dir / "output" / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    
    # Try to get context from the product
    context = ""
    lp_path = product_dir / "landing_page_content.json"
    if lp_path.exists():
        try:
            import json
            data = json.loads(lp_path.read_text())
            product_title = product_title or data.get("title", "Product")
            target_audience = data.get("target_audience", "readers")
            context = f"""
Product: {product_title}
Target Audience: {target_audience}
"""
        except Exception:
            pass
    
    if not product_title:
        product_title = product_dir.name.replace("_", " ").title()
    
    created_prompts = []
    
    for bonus_id in bonus_types:
        bonus = BONUS_TYPES.get(bonus_id.strip())
        if not bonus:
            continue
        
        prompt_content = _generate_bonus_prompt_content(bonus, product_title, context)
        
        prompt_file = prompts_dir / f"bonus_{bonus.id}.prompt.md"
        prompt_file.write_text(prompt_content)
        created_prompts.append(prompt_file)
    
    return created_prompts


def _generate_bonus_prompt_content(bonus: BonusType, product_title: str, context: str) -> str:
    """Generate the content for a bonus prompt."""
    
    prompts = {
        "quick_start": f"""# Quick Start Guide for "{product_title}"

{context}

Create a Quick Start Guide (~1,500 words) that gives readers immediate value:

## Requirements:
1. **Introduction** (100 words) - What this guide covers and who it's for
2. **The 3 Essential Steps** (900 words) - The core actions to get started
3. **Common Mistakes to Avoid** (200 words) - What NOT to do
4. **Your First Week Plan** (200 words) - Day-by-day getting started plan
5. **Quick Reference** (100 words) - Key points summarized

## Tone:
- Action-oriented and encouraging
- Simple, clear language
- Immediate practical value

Save your response to: `output/responses/bonus_quick_start.response.md`
""",
        "checklist": f"""# Action Checklist for "{product_title}"

{context}

Create a comprehensive Action Checklist (~500 words) with:

## Requirements:
1. **Getting Started Checklist** (10-15 items)
2. **Daily Practice Checklist** (5-10 items)
3. **Weekly Review Checklist** (5-8 items)
4. **Progress Milestones** (5-10 milestone markers)

## Format:
- [ ] Checkbox style items
- Clear, actionable statements
- Grouped by phase or topic
- Include time estimates where relevant

Save your response to: `output/responses/bonus_checklist.response.md`
""",
        "workbook": f"""# Interactive Workbook for "{product_title}"

{context}

Create an Interactive Workbook (~3,000 words) with:

## Requirements:
1. **Introduction** (200 words) - How to use this workbook
2. **Self-Assessment** (400 words) - Where are you now? (questions + scoring)
3. **Goal Setting Section** (400 words) - Define your objectives
4. **Chapter Exercises** (1,200 words) - 6-8 exercises tied to main content
5. **Reflection Prompts** (400 words) - Deep thinking questions
6. **Action Planning** (400 words) - Convert insights into action

## Format:
- Leave space for writing (indicate with [Your answer here])
- Include scales and checkboxes
- Progressive difficulty

Save your response to: `output/responses/bonus_workbook.response.md`
""",
        "cheat_sheet": f"""# Cheat Sheet for "{product_title}"

{context}

Create a One-Page Cheat Sheet (~800 words) with:

## Requirements:
1. **Core Concepts** - The 5-7 most important ideas
2. **Key Formulas/Frameworks** - Visual frameworks if applicable
3. **Quick Reference Table** - Common scenarios and solutions
4. **Do's and Don'ts** - Quick tips
5. **Emergency Fixes** - What to do when things go wrong

## Format:
- Dense, scannable content
- Bullet points and tables
- Designed for quick reference
- Printable one-page format

Save your response to: `output/responses/bonus_cheat_sheet.response.md`
""",
        "templates": f"""# Templates Pack for "{product_title}"

{context}

Create a Templates Pack (~1,000 words) with 4-6 ready-to-use templates:

## Requirements:
1. **Planning Template** - Help readers plan their approach
2. **Tracking Template** - Monitor progress and results
3. **Daily/Weekly Template** - Routine structure
4. **Review Template** - Evaluate what's working

## Format:
- Each template should be copy-paste ready
- Include instructions for using each template
- Provide examples of completed templates

Save your response to: `output/responses/bonus_templates.response.md`
""",
        "resource_guide": f"""# Resource Guide for "{product_title}"

{context}

Create a Curated Resource Guide (~2,000 words) with:

## Requirements:
1. **Books** (5-10 recommendations) - With why each matters
2. **Tools & Apps** (5-10) - Free and paid options
3. **Websites & Communities** (5-10) - Online resources
4. **Courses & Learning** (3-5) - Further education
5. **Podcasts/Videos** (3-5) - Media recommendations

## Format:
- Brief description of each resource
- Why it's valuable
- Skill level (beginner/intermediate/advanced)
- Cost (free/paid)

Save your response to: `output/responses/bonus_resource_guide.response.md`
""",
        "case_studies": f"""# Case Studies for "{product_title}"

{context}

Create 3 Detailed Case Studies (~2,500 words total):

## Requirements for each case study:
1. **Background** - Who they were before
2. **Challenge** - What problem they faced
3. **Solution** - What they did (using concepts from the product)
4. **Results** - Specific outcomes and transformations
5. **Key Lessons** - What readers can learn from this

## Format:
- Make stories relatable but inspiring
- Include specific details and timeframes
- Vary the demographics/situations
- Extract actionable lessons

Save your response to: `output/responses/bonus_case_studies.response.md`
""",
        "faq": f"""# FAQ Guide for "{product_title}"

{context}

Create a comprehensive FAQ Guide (~1,500 words) with:

## Requirements:
1. **Getting Started FAQs** (5-7 questions)
2. **Common Challenges FAQs** (5-7 questions)
3. **Advanced Questions** (3-5 questions)
4. **Troubleshooting** (3-5 questions)

## Format:
- Real questions readers would ask
- Thorough but concise answers
- Link concepts to main product content
- Address objections and concerns

Save your response to: `output/responses/bonus_faq.response.md`
""",
        "audio_companion": f"""# Audio Companion Script for "{product_title}"

{context}

Create an Audio Script (~3,000 words) designed for narration:

## Requirements:
1. **Welcome & Overview** (300 words) - Set the stage
2. **Core Concept 1** (500 words) - Key teaching #1
3. **Core Concept 2** (500 words) - Key teaching #2
4. **Core Concept 3** (500 words) - Key teaching #3
5. **Guided Practice** (700 words) - Interactive exercise for listener
6. **Closing & Next Steps** (500 words) - Wrap up and motivation

## Format:
- Written for speaking (conversational)
- Include [PAUSE] markers for breathing
- Natural flow between sections
- Engaging and personal tone

Save your response to: `output/responses/bonus_audio_companion.response.md`
""",
        "journal": f"""# 90-Day Practice Journal for "{product_title}"

{context}

Create a Practice Journal template (~2,000 words) with:

## Requirements:
1. **Introduction** (200 words) - How to use this journal
2. **Week 1-4: Foundation Phase** (500 words) - Daily prompts template
3. **Week 5-8: Building Phase** (500 words) - Daily prompts template
4. **Week 9-12: Integration Phase** (500 words) - Daily prompts template
5. **Weekly Review Template** (200 words) - Reflection questions
6. **Monthly Milestone Check** (100 words) - Progress markers

## Format:
- Daily entry structure
- Mix of checkboxes and writing prompts
- Space for notes [Your notes here]
- Progressive challenge

Save your response to: `output/responses/bonus_journal.response.md`
""",
    }
    
    return prompts.get(bonus.id, f"# {bonus.name}\n\nGenerate content for this bonus.\n")


# ═══════════════════════════════════════════════════════════════════════
# STEP 3B: AUDIO GENERATION HELPERS
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class AudioSession:
    """An audio session to be recorded."""
    id: str
    title: str
    duration_minutes: int
    script_prompt: str
    output_filename: str


@dataclass
class AudioProject:
    """Configuration for an audio product."""
    product_title: str
    sessions: List[AudioSession]
    voice: str = "en_US-amy-medium"
    output_format: str = "mp3"


def generate_audio_script_prompt(session_num: int, total_sessions: int,
                                  session_title: str, session_topic: str,
                                  product_title: str, duration_minutes: int = 15) -> str:
    """Generate a prompt for an audio script/meditation."""
    
    return f"""# Audio Session {session_num}/{total_sessions}: {session_title}

## Product: {product_title}

Create a {duration_minutes}-minute audio script for "{session_title}".

## Requirements:

### Structure:
1. **Opening** (~2 min) - Welcoming, grounding, setting intention
2. **Core Content** (~{duration_minutes - 5} min) - Main teaching/practice for: {session_topic}
3. **Closing** (~3 min) - Integration, gentle return, next steps

### Formatting for TTS:
- Use [PAUSE] for 2-second pauses
- Use [LONG PAUSE] for 5-second pauses
- Use [BREATHE] for breathing space (3 seconds)
- Write phonetically for unusual words
- Use ellipses (...) for gentle transitions
- Write numbers as words (two, three, not 2, 3)

### Tone:
- Warm, calm, and present
- Conversational but focused
- Appropriate pacing for the content type
- Guide without commanding

### Word Count:
- ~150 words per minute of audio
- Target: {duration_minutes * 150} words

## Output Format:

```
# Session {session_num}: {session_title}

[Session script here with all TTS markers]
```

Save your response to: `output/responses/audio_{session_num:02d}_{session_title.lower().replace(' ', '_')}.response.md`
"""


def list_audio_sessions(product_dir: Path) -> List[dict]:
    """List all audio sessions for a product."""
    audio_dir = product_dir / "output" / "audio"
    prompts_dir = product_dir / "output" / "prompts"
    responses_dir = product_dir / "output" / "responses"
    
    sessions = []
    
    # Find audio-related prompts
    if prompts_dir.exists():
        for prompt_file in sorted(prompts_dir.glob("audio_*.prompt.md")):
            slug = prompt_file.stem.replace(".prompt", "")
            response_file = responses_dir / f"{slug}.response.md"
            audio_file = audio_dir / f"{slug}.mp3"
            
            session = {
                "slug": slug,
                "prompt_file": prompt_file,
                "has_script": response_file.exists(),
                "has_audio": audio_file.exists(),
                "response_file": response_file if response_file.exists() else None,
                "audio_file": audio_file if audio_file.exists() else None,
            }
            
            if response_file.exists():
                content = response_file.read_text()
                session["word_count"] = len(content.split())
                session["estimated_minutes"] = session["word_count"] // 150
            
            sessions.append(session)
    
    return sessions


def format_audio_sessions(sessions: List[dict]) -> str:
    """Format audio sessions for display."""
    if not sessions:
        return "\n📭 No audio sessions found. Generate prompts first with:\n   product-builder audio-prompts --product-dir ./product --sessions 8\n"
    
    lines = [
        "",
        "╔" + "═" * 78 + "╗",
        "║" + " " * 28 + "AUDIO SESSIONS" + " " * 36 + "║",
        "╠" + "═" * 78 + "╣",
        "║ {:20} │ {:8} │ {:8} │ {:8} │ {:20} ║".format(
            "Session", "Script", "Audio", "~Minutes", "Status"),
        "╠" + "─" * 78 + "╣",
    ]
    
    for s in sessions:
        script_icon = "✅" if s.get("has_script") else "⏳"
        audio_icon = "🎵" if s.get("has_audio") else "⏳"
        minutes = str(s.get("estimated_minutes", "-"))
        
        if s.get("has_audio"):
            status = "Complete"
        elif s.get("has_script"):
            status = "Ready for TTS"
        else:
            status = "Needs script"
        
        lines.append("║ {:20} │ {:8} │ {:8} │ {:8} │ {:20} ║".format(
            s["slug"][:20], script_icon, audio_icon, minutes, status
        ))
    
    total_with_audio = sum(1 for s in sessions if s.get("has_audio"))
    total_with_script = sum(1 for s in sessions if s.get("has_script"))
    
    lines.append("╠" + "═" * 78 + "╣")
    lines.append("║ Scripts: {}/{:3} │ Audio files: {}/{:3}{:40}║".format(
        total_with_script, len(sessions), total_with_audio, len(sessions), ""
    ))
    lines.append("╚" + "═" * 78 + "╝")
    
    return "\n".join(lines)


def generate_audio_prompts(product_dir: Path, session_count: int,
                           product_title: str = None, 
                           session_topics: List[str] = None) -> List[Path]:
    """Generate prompts for audio sessions."""
    prompts_dir = product_dir / "output" / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    
    if not product_title:
        product_title = product_dir.name.replace("_", " ").title()
    
    # Default session topics if not provided
    if not session_topics:
        session_topics = [
            "Foundation and Getting Started",
            "Core Technique Introduction",
            "Deepening the Practice",
            "Working with Challenges",
            "Building Consistency",
            "Advanced Applications",
            "Integration and Daily Life",
            "Mastery and Beyond",
            "Special Focus Session",
            "Complete Practice Session",
        ]
    
    created_prompts = []
    
    for i in range(1, session_count + 1):
        topic = session_topics[(i - 1) % len(session_topics)]
        title = f"Session {i}: {topic}"
        
        prompt_content = generate_audio_script_prompt(
            session_num=i,
            total_sessions=session_count,
            session_title=title,
            session_topic=topic,
            product_title=product_title,
            duration_minutes=15
        )
        
        slug = f"audio_{i:02d}_{topic.lower().replace(' ', '_')[:20]}"
        prompt_file = prompts_dir / f"{slug}.prompt.md"
        prompt_file.write_text(prompt_content)
        created_prompts.append(prompt_file)
    
    return created_prompts


def generate_audio_from_script(script_path: Path, output_path: Path,
                               voice: str = "en_US-amy-medium",
                               engine: str = "piper") -> Tuple[bool, str]:
    """
    Generate audio from a script file using TTS.
    
    Returns (success, message).
    """
    import subprocess
    import shutil
    
    if not script_path.exists():
        return False, f"Script not found: {script_path}"
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Read and clean the script
    raw_content = script_path.read_text()
    
    # Process TTS markers
    content = raw_content
    content = content.replace("[PAUSE]", "... ...")
    content = content.replace("[LONG PAUSE]", "... ... ... ... ...")
    content = content.replace("[BREATHE]", "... ... ...")
    
    # Remove markdown formatting
    import re
    content = re.sub(r'^#+\s+', '', content, flags=re.MULTILINE)  # Remove headers
    content = re.sub(r'\*\*([^*]+)\*\*', r'\1', content)  # Remove bold
    content = re.sub(r'\*([^*]+)\*', r'\1', content)  # Remove italic
    content = re.sub(r'^-\s+', '', content, flags=re.MULTILINE)  # Remove bullets
    content = re.sub(r'```[^`]*```', '', content, flags=re.DOTALL)  # Remove code blocks
    
    # Try different TTS engines
    if engine == "piper" and shutil.which("piper"):
        # Use Piper TTS
        temp_wav = output_path.with_suffix(".wav")
        try:
            process = subprocess.run(
                ["piper", "--model", voice, "--output_file", str(temp_wav)],
                input=content.encode(),
                capture_output=True,
                timeout=300
            )
            
            if process.returncode != 0:
                return False, f"Piper error: {process.stderr.decode()}"
            
            # Convert to MP3 if ffmpeg available
            if shutil.which("ffmpeg") and output_path.suffix == ".mp3":
                subprocess.run([
                    "ffmpeg", "-y", "-i", str(temp_wav),
                    "-codec:a", "libmp3lame", "-qscale:a", "2",
                    str(output_path)
                ], capture_output=True)
                temp_wav.unlink()  # Remove temp WAV
            else:
                # Just use WAV
                shutil.move(temp_wav, output_path.with_suffix(".wav"))
                return True, f"Created: {output_path.with_suffix('.wav')} (install ffmpeg for MP3)"
            
            return True, f"Created: {output_path}"
            
        except subprocess.TimeoutExpired:
            return False, "TTS generation timed out"
        except Exception as e:
            return False, f"TTS error: {str(e)}"
    
    elif engine == "espeak" and shutil.which("espeak-ng"):
        # Use espeak-ng as fallback
        try:
            temp_wav = output_path.with_suffix(".wav")
            process = subprocess.run(
                ["espeak-ng", "-w", str(temp_wav), "-s", "140"],
                input=content.encode(),
                capture_output=True,
                timeout=300
            )
            
            if process.returncode != 0:
                return False, f"espeak error: {process.stderr.decode()}"
            
            return True, f"Created: {temp_wav}"
            
        except Exception as e:
            return False, f"espeak error: {str(e)}"
    
    else:
        return False, "No TTS engine available. Install 'piper' or 'espeak-ng'"


def get_next_audio_session(product_dir: Path) -> Optional[dict]:
    """Get the next audio session that needs work."""
    sessions = list_audio_sessions(product_dir)
    
    for session in sessions:
        if not session.get("has_script"):
            return {"type": "needs_script", "session": session}
        elif not session.get("has_audio"):
            return {"type": "needs_audio", "session": session}
    
    return None  # All done!


# ═══════════════════════════════════════════════════════════════════════
# XTTS-v2 VOICE CLONING INTEGRATION
# ═══════════════════════════════════════════════════════════════════════


def convert_script_to_ssml(script_path: Path, output_path: Path) -> Tuple[bool, str, int]:
    """
    Convert a markdown script to SSML format for TTS processing.
    Returns (success, message, segment_count).
    """
    import re
    
    if not script_path.exists():
        return False, f"Script not found: {script_path}", 0
    
    content = script_path.read_text()
    
    # Process TTS markers into SSML breaks
    # [PAUSE] -> 2 seconds
    # [LONG PAUSE] -> 5 seconds
    # [BREATHE] -> 3 seconds
    content = content.replace("[PAUSE]", '<break time="2s"/>')
    content = content.replace("[LONG PAUSE]", '<break time="5s"/>')
    content = content.replace("[BREATHE]", '<break time="3s"/>')
    
    # Convert ellipses to short pauses
    content = re.sub(r'\.{3,}', '<break time="1s"/>', content)
    
    # Remove markdown headers but keep text
    content = re.sub(r'^#+\s+', '', content, flags=re.MULTILINE)
    
    # Remove bold/italic markers
    content = re.sub(r'\*\*([^*]+)\*\*', r'\1', content)
    content = re.sub(r'\*([^*]+)\*', r'\1', content)
    
    # Remove bullet points
    content = re.sub(r'^[-*]\s+', '', content, flags=re.MULTILINE)
    
    # Remove code blocks
    content = re.sub(r'```[^`]*```', '', content, flags=re.DOTALL)
    
    # Split into sentences for natural segment breaks
    sentences = re.split(r'(?<=[.!?])\s+', content)
    
    # Build SSML
    ssml_lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<speak>']
    segment_count = 0
    
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence and len(sentence) > 3:
            # Add sentence with small natural pause
            ssml_lines.append(f'  {sentence}')
            if '<break' not in sentence:
                ssml_lines.append('  <break time="500ms"/>')
            segment_count += 1
    
    ssml_lines.append('</speak>')
    
    ssml_content = '\n'.join(ssml_lines)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(ssml_content)
    
    return True, f"Created SSML with {segment_count} segments", segment_count


def find_voice_sample(product_dir: Path) -> Optional[Path]:
    """Find a voice sample file for cloning."""
    # Check common locations
    voice_locations = [
        product_dir / "voice_sample.wav",
        product_dir / "voice_sample.mp3",
        product_dir / "assets" / "voice_sample.wav",
        product_dir / "assets" / "voice_sample.mp3",
        Path.home() / "Projects/dreamweaving/assets/voices/ava_sample.wav",
        Path.home() / "Projects/dreamweaving/assets/voices/default.wav",
    ]
    
    for path in voice_locations:
        if path.exists():
            return path
    
    return None


def generate_audio_xtts(script_path: Path, output_path: Path,
                        voice_sample: Path = None,
                        speed: float = 0.88,
                        progress_callback = None) -> Tuple[bool, str]:
    """
    Generate audio using XTTS-v2 with voice cloning.
    
    Args:
        script_path: Path to the response script (.response.md)
        output_path: Path for output audio file (.mp3)
        voice_sample: Path to voice sample for cloning
        speed: Speed adjustment (0.88 = slightly slower for meditations)
        progress_callback: Optional callback(current, total, message)
    
    Returns (success, message).
    """
    import subprocess
    import tempfile
    
    # Find the XTTS script
    xtts_script = Path.home() / "Projects/dreamweaving/scripts/core/generate_voice_xtts_custom.py"
    
    if not xtts_script.exists():
        return False, f"XTTS script not found: {xtts_script}"
    
    # Find voice sample
    if voice_sample is None:
        voice_sample = find_voice_sample(script_path.parent.parent.parent)
    
    if voice_sample is None:
        return False, "No voice sample found. Create voice_sample.wav in product directory."
    
    # Create temp SSML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ssml', delete=False) as tmp:
        ssml_path = Path(tmp.name)
    
    try:
        # Convert script to SSML
        success, message, segment_count = convert_script_to_ssml(script_path, ssml_path)
        if not success:
            return False, message
        
        if progress_callback:
            progress_callback(0, segment_count, f"Converted script to {segment_count} segments")
        
        # Run XTTS generator
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        cmd = [
            str(Path.home() / "Projects/dreamweaving/venv_coqui/bin/python"),
            str(xtts_script),
            str(ssml_path),
            str(output_path.parent),
            "--voice", str(voice_sample),
            "--speed", str(speed)
        ]
        
        # Run with real-time progress output
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        current_segment = 0
        for line in process.stdout:
            line = line.strip()
            if line:
                # Parse progress from output like "[60/88]"
                import re
                match = re.search(r'\[(\d+)/(\d+)\]', line)
                if match:
                    current_segment = int(match.group(1))
                    total = int(match.group(2))
                    if progress_callback:
                        progress_callback(current_segment, total, line[:60])
                print(f"   {line}")
        
        process.wait()
        
        if process.returncode != 0:
            return False, "XTTS generation failed"
        
        # Rename output file
        generated_file = output_path.parent / "voice_xtts.mp3"
        if generated_file.exists():
            generated_file.rename(output_path)
        
        if output_path.exists():
            size_mb = output_path.stat().st_size / (1024 * 1024)
            return True, f"Created: {output_path} ({size_mb:.1f}MB)"
        else:
            return False, "Output file not created"
        
    finally:
        if ssml_path.exists():
            ssml_path.unlink()


def get_xtts_status() -> dict:
    """Check if XTTS-v2 is available and configured."""
    import shutil
    
    status = {
        "available": False,
        "script_exists": False,
        "venv_exists": False,
        "model_exists": False,
        "message": ""
    }
    
    xtts_script = Path.home() / "Projects/dreamweaving/scripts/core/generate_voice_xtts_custom.py"
    venv_python = Path.home() / "Projects/dreamweaving/venv_coqui/bin/python"
    model_dir = Path.home() / ".local/share/tts/tts_models--multilingual--multi-dataset--xtts_v2"
    
    status["script_exists"] = xtts_script.exists()
    status["venv_exists"] = venv_python.exists()
    status["model_exists"] = model_dir.exists()
    
    if all([status["script_exists"], status["venv_exists"], status["model_exists"]]):
        status["available"] = True
        status["message"] = "XTTS-v2 ready with voice cloning"
    else:
        missing = []
        if not status["script_exists"]:
            missing.append("script")
        if not status["venv_exists"]:
            missing.append("venv_coqui environment")
        if not status["model_exists"]:
            missing.append("XTTS model")
        status["message"] = f"Missing: {', '.join(missing)}"
    
    return status


# ═══════════════════════════════════════════════════════════════════════
# STEP 3C: VIDEO GENERATION HELPERS
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class VideoScene:
    """A scene in a video."""
    scene_id: str
    title: str
    narration: str
    duration_seconds: float
    visual_type: str  # "text", "image", "diagram", "quote", "statistics"
    visual_content: dict
    caption_text: str = ""


@dataclass
class VideoProject:
    """Configuration for a video project."""
    title: str
    scenes: List[VideoScene]
    style: dict = None
    audio_path: Optional[str] = None
    output_path: Optional[str] = None


# Video templates available
VIDEO_TEMPLATES = {
    "course_intro": {
        "name": "Course Introduction",
        "composition": "CourseIntro",
        "description": "Animated course title with key benefits",
        "duration": "30-60 seconds"
    },
    "chapter_video": {
        "name": "Chapter Video",
        "composition": "ChapterVideo", 
        "description": "Multi-scene chapter with narration and visuals",
        "duration": "5-15 minutes"
    },
    "key_insight": {
        "name": "Key Insight",
        "composition": "KeyInsight",
        "description": "Single powerful insight with visual emphasis",
        "duration": "30-60 seconds"
    },
    "before_after": {
        "name": "Before/After",
        "composition": "BeforeAfter",
        "description": "Transformation comparison",
        "duration": "20-40 seconds"
    },
    "checklist": {
        "name": "Checklist",
        "composition": "Checklist",
        "description": "Animated checklist with progress",
        "duration": "30-60 seconds"
    },
    "quote_card": {
        "name": "Quote Card",
        "composition": "QuoteCard",
        "description": "Inspirational quote with attribution",
        "duration": "15-30 seconds"
    },
    "framework_diagram": {
        "name": "Framework Diagram",
        "composition": "FrameworkDiagram",
        "description": "Animated diagram or framework visualization",
        "duration": "45-90 seconds"
    },
    "statistic": {
        "name": "Statistic",
        "composition": "Statistic",
        "description": "Animated number or statistic reveal",
        "duration": "15-30 seconds"
    },
    "progress_milestone": {
        "name": "Progress Milestone",
        "composition": "ProgressMilestone",
        "description": "Celebrates achievement with animation",
        "duration": "20-40 seconds"
    },
}


def list_video_templates() -> str:
    """List all available video templates."""
    lines = [
        "",
        "╔" + "═" * 78 + "╗",
        "║" + " " * 25 + "VIDEO TEMPLATES" + " " * 38 + "║",
        "╠" + "═" * 78 + "╣",
    ]
    
    for key, tmpl in VIDEO_TEMPLATES.items():
        lines.append(f"║ {key:20} │ {tmpl['name']:25} │ {tmpl['duration']:15} ║")
    
    lines.append("╠" + "═" * 78 + "╣")
    lines.append("║ Use: product-builder video-prompts --product-dir ./product --template chapter_video    ║")
    lines.append("╚" + "═" * 78 + "╝")
    
    return "\n".join(lines)


def generate_video_script_prompt(video_num: int, total_videos: int,
                                  video_title: str, video_topic: str,
                                  product_title: str, template: str = "chapter_video") -> str:
    """Generate a prompt for a video script."""
    
    template_info = VIDEO_TEMPLATES.get(template, VIDEO_TEMPLATES["chapter_video"])
    
    return f"""# Video {video_num}/{total_videos}: {video_title}

## Product: {product_title}
## Template: {template_info['name']} ({template_info['duration']})

Create a video script for "{video_title}" on the topic: {video_topic}

## Video Structure:

### 1. NARRATION SCRIPT
Write the spoken narration in segments, using TTS markers:
- [PAUSE] for 2-second pauses
- [LONG PAUSE] for 5-second pauses  
- [BREATHE] for 3-second breathing space

### 2. SCENE BREAKDOWN
For each segment of narration, describe the visual:

```
SCENE 1 (0:00-0:15)
Narration: "Welcome to [topic]..."
Visual: [TYPE: text/image/diagram/quote/statistic]
Description: [Describe what appears on screen]
Caption: [On-screen text/subtitle]
---
SCENE 2 (0:15-0:45)
...
```

### 3. VISUAL ASSETS NEEDED
List any images or graphics needed:
- Image 1: [description] - Search: [Unsplash/Pexels search term]
- Image 2: [description] - Generate: [AI image prompt]
- Diagram: [description of diagram to create]

## Requirements:
- Target duration: {template_info['duration']}
- Include captions for all spoken words
- Suggest Unsplash/Pexels search terms for stock images
- Include AI image generation prompts for custom graphics
- Word count: ~150 words per minute of narration

Save your response to: `output/responses/video_{video_num:02d}_{video_title.lower().replace(' ', '_')[:20]}.response.md`
"""


def list_video_sessions(product_dir: Path) -> List[dict]:
    """List all video sessions for a product."""
    video_dir = product_dir / "output" / "video"
    prompts_dir = product_dir / "output" / "prompts"
    responses_dir = product_dir / "output" / "responses"
    
    sessions = []
    
    if prompts_dir.exists():
        for prompt_file in sorted(prompts_dir.glob("video_*.prompt.md")):
            slug = prompt_file.stem.replace(".prompt", "")
            response_file = responses_dir / f"{slug}.response.md"
            video_file = video_dir / f"{slug}.mp4"
            audio_file = video_dir / f"{slug}_audio.mp3"
            
            session = {
                "slug": slug,
                "prompt_file": prompt_file,
                "has_script": response_file.exists(),
                "has_audio": audio_file.exists(),
                "has_video": video_file.exists(),
                "response_file": response_file if response_file.exists() else None,
                "audio_file": audio_file if audio_file.exists() else None,
                "video_file": video_file if video_file.exists() else None,
            }
            
            if response_file.exists():
                content = response_file.read_text()
                session["word_count"] = len(content.split())
            
            sessions.append(session)
    
    return sessions


def format_video_sessions(sessions: List[dict]) -> str:
    """Format video sessions for display."""
    if not sessions:
        return "\n📭 No video sessions found. Generate prompts first with:\n   product-builder video-prompts --product-dir ./product --videos 5\n"
    
    lines = [
        "",
        "╔" + "═" * 88 + "╗",
        "║" + " " * 35 + "VIDEO SESSIONS" + " " * 39 + "║",
        "╠" + "═" * 88 + "╣",
        "║ {:25} │ {:8} │ {:8} │ {:8} │ {:25} ║".format(
            "Session", "Script", "Audio", "Video", "Status"),
        "╠" + "─" * 88 + "╣",
    ]
    
    for s in sessions:
        script_icon = "✅" if s.get("has_script") else "⏳"
        audio_icon = "🎵" if s.get("has_audio") else "⏳"
        video_icon = "🎬" if s.get("has_video") else "⏳"
        
        if s.get("has_video"):
            status = "Complete"
        elif s.get("has_audio"):
            status = "Ready for render"
        elif s.get("has_script"):
            status = "Ready for audio"
        else:
            status = "Needs script"
        
        lines.append("║ {:25} │ {:8} │ {:8} │ {:8} │ {:25} ║".format(
            s["slug"][:25], script_icon, audio_icon, video_icon, status
        ))
    
    total_complete = sum(1 for s in sessions if s.get("has_video"))
    
    lines.append("╠" + "═" * 88 + "╣")
    lines.append("║ Complete: {}/{}{}║".format(
        total_complete, len(sessions), " " * 72
    ))
    lines.append("╚" + "═" * 88 + "╝")
    
    return "\n".join(lines)


def generate_video_prompts(product_dir: Path, video_count: int,
                           product_title: str = None,
                           video_topics: List[str] = None,
                           template: str = "chapter_video") -> List[Path]:
    """Generate prompts for video sessions."""
    prompts_dir = product_dir / "output" / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    
    if not product_title:
        product_title = product_dir.name.replace("_", " ").title()
    
    # Default video topics if not provided
    if not video_topics:
        video_topics = [
            "Introduction and Overview",
            "Core Concepts Explained",
            "Step-by-Step Process",
            "Common Mistakes to Avoid",
            "Advanced Techniques",
            "Real-World Examples",
            "Quick Reference Guide",
            "Summary and Next Steps",
        ]
    
    created_prompts = []
    
    for i in range(1, video_count + 1):
        topic = video_topics[(i - 1) % len(video_topics)]
        title = f"Video {i}: {topic}"
        
        prompt_content = generate_video_script_prompt(
            video_num=i,
            total_videos=video_count,
            video_title=title,
            video_topic=topic,
            product_title=product_title,
            template=template
        )
        
        slug = f"video_{i:02d}_{topic.lower().replace(' ', '_')[:20]}"
        prompt_file = prompts_dir / f"{slug}.prompt.md"
        prompt_file.write_text(prompt_content)
        created_prompts.append(prompt_file)
    
    return created_prompts


def fetch_stock_image(search_term: str, output_path: Path,
                      source: str = "unsplash") -> Tuple[bool, str]:
    """
    Fetch a stock image from Unsplash or Pexels.
    
    Returns (success, message_or_path).
    """
    import subprocess
    import urllib.request
    import json
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Use Unsplash Source API (no API key needed for random images)
    if source == "unsplash":
        # Unsplash Source API for random images by search
        url = f"https://source.unsplash.com/1920x1080/?{search_term.replace(' ', ',')}"
        
        try:
            urllib.request.urlretrieve(url, str(output_path))
            if output_path.exists() and output_path.stat().st_size > 1000:
                return True, str(output_path)
            else:
                return False, "Downloaded file too small or empty"
        except Exception as e:
            return False, f"Download failed: {str(e)}"
    
    return False, f"Unknown source: {source}"


def get_remotion_status() -> dict:
    """Check if Remotion is available and configured."""
    import shutil
    
    status = {
        "available": False,
        "npx_exists": shutil.which("npx") is not None,
        "project_exists": False,
        "message": ""
    }
    
    project_dir = Path(__file__).parent.parent / "remotion_project"
    status["project_exists"] = (project_dir / "package.json").exists()
    
    if status["npx_exists"] and status["project_exists"]:
        status["available"] = True
        status["message"] = "Remotion ready for video rendering"
    else:
        missing = []
        if not status["npx_exists"]:
            missing.append("Node.js/npx")
        if not status["project_exists"]:
            missing.append("remotion_project")
        status["message"] = f"Missing: {', '.join(missing)}"
    
    return status


def get_next_video_session(product_dir: Path) -> Optional[dict]:
    """Get the next video session that needs work."""
    sessions = list_video_sessions(product_dir)
    
    for session in sessions:
        if not session.get("has_script"):
            return {"type": "needs_script", "session": session}
        elif not session.get("has_audio"):
            return {"type": "needs_audio", "session": session}
        elif not session.get("has_video"):
            return {"type": "needs_render", "session": session}
    
    return None  # All done!


def render_video_with_remotion(
    script_path: Path,
    audio_path: Path,
    output_path: Path,
    composition: str = "ChapterVideo",
    images_dir: Path = None
) -> Tuple[bool, str]:
    """
    Render video using Remotion with audio and captions.
    
    Returns (success, message).
    """
    import subprocess
    import json
    
    project_dir = Path(__file__).parent.parent / "remotion_project"
    
    if not project_dir.exists():
        return False, f"Remotion project not found: {project_dir}"
    
    if not script_path.exists():
        return False, f"Script not found: {script_path}"
    
    if not audio_path.exists():
        return False, f"Audio not found: {audio_path}"
    
    # Parse script for scenes
    content = script_path.read_text()
    
    # Build props for Remotion
    props = {
        "audioUrl": str(audio_path.absolute()),
        "title": script_path.stem.replace("_", " ").title(),
        "scenes": [],  # Would parse from script
        "captionsEnabled": True,
    }
    
    if images_dir and images_dir.exists():
        props["imagesDir"] = str(images_dir.absolute())
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    cmd = [
        "npx", "remotion", "render",
        composition,
        str(output_path),
        "--props", json.dumps(props),
        "--width", "1920",
        "--height", "1080",
        "--codec", "h264",
    ]
    
    try:
        result = subprocess.run(
            cmd,
            cwd=str(project_dir),
            capture_output=True,
            timeout=1200  # 20 minute timeout
        )
        
        if result.returncode == 0:
            if output_path.exists():
                size_mb = output_path.stat().st_size / (1024 * 1024)
                return True, f"Created: {output_path} ({size_mb:.1f}MB)"
            else:
                return False, "Render completed but output not found"
        else:
            return False, f"Render failed: {result.stderr.decode()[:200]}"
            
    except subprocess.TimeoutExpired:
        return False, "Render timed out after 20 minutes"
    except Exception as e:
        return False, f"Render error: {str(e)}"


# ═══════════════════════════════════════════════════════════════════════
# STEP 3D: LANDING PAGE & STORE INTEGRATION HELPERS
# ═══════════════════════════════════════════════════════════════════════


# Digital product categories for SalarsNet store
DIGITAL_CATEGORIES = {
    "wealth": {"name": "Wealth Building", "icon": "💰"},
    "health": {"name": "Holistic Health", "icon": "🌿"},
    "dreamweavings": {"name": "Dreamweaving", "icon": "🌀"},
    "consciousness": {"name": "Consciousness", "icon": "🧠"},
    "ai": {"name": "AI Integration", "icon": "🤖"},
    "spirituality": {"name": "Spirituality", "icon": "🙏"},
    "survival": {"name": "Preparedness", "icon": "🏕️"},
    "poetry": {"name": "Poetry & Writing", "icon": "✍️"},
    "treasure": {"name": "Treasure Hunting", "icon": "🗺️"},
    "old-west": {"name": "Old West", "icon": "🤠"},
    "love": {"name": "Love & Relationships", "icon": "💝"},
    "happiness": {"name": "Happiness", "icon": "☀️"},
}


@dataclass
class ProductManifest:
    """Complete product information for store integration."""
    name: str
    slug: str
    description: str
    price: float
    sku: str
    category: str  # subcategory_slug
    image_path: str
    download_url: str
    download_type: str  # pdf, zip
    landing_page_content: dict
    sale_price: Optional[float] = None


def generate_product_slug(title: str) -> str:
    """Generate a URL-safe slug from title."""
    import re
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')


def generate_sku(category: str, sequence: int = 1) -> str:
    """Generate SKU in DIG-CATEGORY-XXX format."""
    cat_map = {
        "wealth": "WEALTH",
        "health": "HEALTH",
        "dreamweavings": "DREAMWEAVINGS",
        "consciousness": "CONSCIOUSNESS",
        "ai": "AI",
        "spirituality": "SPIRITUALITY",
        "survival": "SURVIVAL",
        "poetry": "POETRY",
        "treasure": "TREASURE",
        "old-west": "OLDWEST",
        "love": "LOVE",
        "happiness": "HAPPINESS",
    }
    cat_code = cat_map.get(category, category.upper()[:10])
    return f"DIG-{cat_code}-{sequence:03d}"


def generate_landing_page_prompt(product_title: str, product_description: str,
                                  category: str, target_price: float) -> str:
    """Generate a prompt for creating landing page content."""
    cat_info = DIGITAL_CATEGORIES.get(category, {"name": category, "icon": "📦"})
    
    return f"""# Landing Page Content: {product_title}

## Product: {product_title}
## Category: {cat_info['name']} {cat_info['icon']}
## Target Price: ${target_price:.2f}

Create compelling landing page content for this digital product.

**Product Description:**
{product_description}

---

## Required Output Structure (JSON format):

```json
{{
  "headline": "Short, powerful hook (5-8 words)",
  "subheadline": "2-3 sentence value proposition that expands the headline",
  "features": [
    {{
      "icon": "emoji icon",
      "title": "Feature Title (3-5 words)",
      "description": "1-2 sentence benefit-focused description"
    }}
    // Include 6 features
  ],
  "bonuses": [
    {{
      "title": "Bonus Name",
      "value": "$XX",
      "description": "What they get and why it's valuable"
    }}
    // Include 3 bonuses
  ],
  "testimonial": {{
    "quote": "Detailed, specific testimonial (2-3 sentences)",
    "author": "First Name L.",
    "role": "Relatable role/profession"
  }},
  "faq": [
    {{
      "question": "Common objection or question",
      "answer": "Clear, concise answer (2-3 sentences)"
    }}
    // Include 3-4 FAQs
  ]
}}
```

## Guidelines:
- **Headline**: Focus on the transformation, not the product
- **Features**: Lead with benefits, support with deliverables  
- **Bonuses**: Make them feel substantial ($10-$35 value each)
- **Testimonial**: Specific results, relatable author
- **FAQ**: Address objections (time, skill level, applicability)

Save your response to: `output/responses/landing_page.response.md`
"""


def generate_product_image_prompt(product_title: str, category: str,
                                   style: str = "premium_digital") -> str:
    """Generate a prompt for creating the product cover image."""
    styles = {
        "premium_digital": "premium app icon style, high-end digital product, dark background with subtle gradients, professional, modern, elegant, centered composition",
        "minimalist": "clean minimalist design, white space, elegant typography, single focal point, sophisticated",
        "mystical": "mystical ethereal glow, cosmic vibes, soft purple and blue gradients, dreamy, consciousness-expanding",
        "practical": "clean and professional, organized, trustworthy, practical feel, warm neutrals",
        "vibrant": "bold colors, energetic, dynamic, inspirational, motivating"
    }
    
    style_desc = styles.get(style, styles["premium_digital"])
    
    return f"""Create a digital product cover image for: "{product_title}"

Style: {style_desc}

Requirements:
- 1200x1200 pixels (square format)
- No text or typography (text will be overlaid)
- Abstract or symbolic representation of the topic
- High contrast for visibility
- Dark theme preferred to match SalarsNet aesthetic
- Should convey transformation and premium quality

Category context: {DIGITAL_CATEGORIES.get(category, {}).get('name', category)}
"""


def parse_landing_page_response(response_path: Path) -> Tuple[bool, dict]:
    """Parse landing page content from a response file."""
    import json
    import re
    
    if not response_path.exists():
        return False, {"error": f"Response file not found: {response_path}"}
    
    content = response_path.read_text()
    
    # Try to extract JSON from markdown code block
    json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
    if json_match:
        try:
            data = json.loads(json_match.group(1))
            return True, data
        except json.JSONDecodeError as e:
            return False, {"error": f"Invalid JSON: {e}"}
    
    # Try to parse entire content as JSON
    try:
        data = json.loads(content)
        return True, data
    except json.JSONDecodeError:
        return False, {"error": "Could not find valid JSON in response"}


def create_product_manifest(product_dir: Path) -> Tuple[bool, ProductManifest]:
    """Create product manifest from product directory contents."""
    import json
    
    # Check for required files
    config_file = product_dir / "product.json"
    landing_response = product_dir / "output" / "responses" / "landing_page.response.md"
    
    if not config_file.exists():
        return False, {"error": "product.json not found"}
    
    try:
        config = json.loads(config_file.read_text())
    except json.JSONDecodeError as e:
        return False, {"error": f"Invalid product.json: {e}"}
    
    # Parse landing page content if available
    landing_content = {}
    if landing_response.exists():
        success, result = parse_landing_page_response(landing_response)
        if success:
            landing_content = result
    
    # Find product image
    image_path = None
    for img_name in ["cover.png", "cover.jpg", "product.png", "product.jpg"]:
        if (product_dir / "output" / "images" / img_name).exists():
            image_path = f"/images/products/{config.get('slug', 'product')}.png"
            break
    
    if not image_path:
        image_path = f"/images/store/digital/{config.get('category', 'digital')}.png"
    
    # Build manifest
    manifest = ProductManifest(
        name=config.get("title", product_dir.name.replace("_", " ").title()),
        slug=config.get("slug") or generate_product_slug(config.get("title", product_dir.name)),
        description=config.get("description", ""),
        price=float(config.get("price", 14.99)),
        sku=config.get("sku") or generate_sku(config.get("category", "digital")),
        category=config.get("category", "wealth"),
        image_path=image_path,
        download_url=f"/downloads/products/{config.get('slug', 'product')}.zip",
        download_type=config.get("download_type", "zip"),
        landing_page_content=landing_content,
        sale_price=config.get("sale_price"),
    )
    
    return True, manifest


def generate_store_sql(manifest: ProductManifest) -> str:
    """Generate SQL for inserting/updating product in store."""
    import json
    
    landing_json = json.dumps(manifest.landing_page_content).replace("'", "''")
    
    return f"""-- Insert/Update product: {manifest.name}
-- Generated by Epistemic Factory Step 3d

INSERT INTO products (
    name, slug, description, price, sku,
    image, image_1, category_name, subcategory_name, status,
    stock_quantity, on_hand, is_digital, digital_file_url, digital_file_type,
    landing_page_content
) VALUES (
    '{manifest.name.replace("'", "''")}',
    '{manifest.slug}',
    '{manifest.description.replace("'", "''")}',
    {manifest.price},
    '{manifest.sku}',
    '{manifest.image_path}',
    '{manifest.image_path}',
    'digital',
    '{manifest.category}',
    'active',
    9999,
    true,
    true,
    '{manifest.download_url}',
    '{manifest.download_type}',
    '{landing_json}'::jsonb
)
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    price = EXCLUDED.price,
    image = EXCLUDED.image,
    landing_page_content = EXCLUDED.landing_page_content,
    digital_file_url = EXCLUDED.digital_file_url;

-- Also insert into dreamweavings table for dual-table pattern
INSERT INTO dreamweavings (
    title, slug, description, price, sku,
    image, category, status, is_digital, download_url
) VALUES (
    '{manifest.name.replace("'", "''")}',
    '{manifest.slug}',
    '{manifest.description.replace("'", "''")}',
    {manifest.price},
    '{manifest.sku}',
    '{manifest.image_path}',
    '{manifest.category}',
    'active',
    true,
    '{manifest.download_url}'
)
ON CONFLICT (slug) DO UPDATE SET
    title = EXCLUDED.title,
    description = EXCLUDED.description,
    price = EXCLUDED.price,
    image = EXCLUDED.image,
    download_url = EXCLUDED.download_url;
"""


def list_store_categories() -> str:
    """List all available digital product categories."""
    lines = [
        "",
        "╔" + "═" * 58 + "╗",
        "║" + " " * 15 + "DIGITAL PRODUCT CATEGORIES" + " " * 17 + "║",
        "╠" + "═" * 58 + "╣",
    ]
    
    for slug, info in DIGITAL_CATEGORIES.items():
        lines.append(f"║  {info['icon']} {slug:15} │ {info['name']:30} ║")
    
    lines.append("╚" + "═" * 58 + "╝")
    return "\n".join(lines)


def get_store_integration_status(product_dir: Path) -> dict:
    """Check store integration status for a product."""
    import json
    
    status = {
        "has_product_json": False,
        "has_landing_content": False,
        "has_cover_image": False,
        "has_download_zip": False,
        "has_sql_export": False,
        "ready_for_store": False,
        "missing": [],
    }
    
    # Check product.json
    config_file = product_dir / "product.json"
    if config_file.exists():
        status["has_product_json"] = True
    else:
        status["missing"].append("product.json")
    
    # Check landing page content
    landing_response = product_dir / "output" / "responses" / "landing_page.response.md"
    if landing_response.exists():
        success, _ = parse_landing_page_response(landing_response)
        status["has_landing_content"] = success
    if not status["has_landing_content"]:
        status["missing"].append("landing_page.response.md")
    
    # Check cover image
    for img in ["cover.png", "cover.jpg", "product.png", "product.jpg"]:
        if (product_dir / "output" / "images" / img).exists():
            status["has_cover_image"] = True
            break
    if not status["has_cover_image"]:
        status["missing"].append("cover image")
    
    # Check download ZIP
    output_dir = product_dir / "output"
    for zip_file in output_dir.glob("*.zip"):
        status["has_download_zip"] = True
        break
    if not status["has_download_zip"]:
        status["missing"].append("download ZIP")
    
    # Check SQL export
    if (product_dir / "output" / "store_insert.sql").exists():
        status["has_sql_export"] = True
    
    # Overall ready status
    status["ready_for_store"] = (
        status["has_product_json"] and
        status["has_landing_content"] and
        status["has_cover_image"] and
        status["has_download_zip"]
    )
    
    return status


def format_store_status(status: dict) -> str:
    """Format store integration status for display."""
    lines = [
        "",
        "╔" + "═" * 50 + "╗",
        "║" + " " * 12 + "STORE INTEGRATION STATUS" + " " * 14 + "║",
        "╠" + "═" * 50 + "╣",
    ]
    
    items = [
        ("product.json", status["has_product_json"]),
        ("Landing page content", status["has_landing_content"]),
        ("Cover image", status["has_cover_image"]),
        ("Download ZIP", status["has_download_zip"]),
        ("SQL export", status["has_sql_export"]),
    ]
    
    for label, ready in items:
        icon = "✅" if ready else "⏳"
        lines.append(f"║  {icon} {label:40} ║")
    
    lines.append("╠" + "═" * 50 + "╣")
    
    if status["ready_for_store"]:
        lines.append("║  🚀 READY FOR STORE INTEGRATION!               ║")
    else:
        lines.append("║  ⚠️  Missing: " + ", ".join(status["missing"])[:32] + " " * (32 - len(", ".join(status["missing"])[:32])) + " ║")
    
    lines.append("╚" + "═" * 50 + "╝")
    return "\n".join(lines)


def copy_assets_for_deployment(product_dir: Path, salarsu_path: Path) -> Tuple[bool, List[str]]:
    """Copy product assets to SalarsNet for deployment."""
    import shutil
    import json
    
    actions = []
    
    # Get product config
    config_file = product_dir / "product.json"
    if not config_file.exists():
        return False, ["product.json not found"]
    
    config = json.loads(config_file.read_text())
    slug = config.get("slug") or generate_product_slug(config.get("title", "product"))
    
    # Copy cover image
    for img_name in ["cover.png", "cover.jpg", "product.png"]:
        src_img = product_dir / "output" / "images" / img_name
        if src_img.exists():
            dest_img = salarsu_path / "public" / "images" / "products" / f"{slug}.png"
            dest_img.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_img, dest_img)
            actions.append(f"Copied: {dest_img}")
            break
    
    # Copy download ZIP
    for zip_file in (product_dir / "output").glob("*.zip"):
        dest_zip = salarsu_path / "public" / "downloads" / "products" / f"{slug}.zip"
        dest_zip.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(zip_file, dest_zip)
        actions.append(f"Copied: {dest_zip}")
        break
    
    # Copy SQL export
    sql_file = product_dir / "output" / "store_insert.sql"
    if sql_file.exists():
        dest_sql = salarsu_path / "db" / "seeds" / f"digital_{slug}.sql"
        dest_sql.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(sql_file, dest_sql)
        actions.append(f"Copied: {dest_sql}")
    
    return len(actions) > 0, actions
