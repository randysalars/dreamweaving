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
# STEP 3B ENHANCEMENTS: AUDIO TEMPLATES, VOICE LIBRARY, QUALITY ANALYZER
# ═══════════════════════════════════════════════════════════════════════


# Audio generation presets for different content types
AUDIO_TEMPLATES = {
    "meditation": {
        "name": "Meditation",
        "description": "Slow, calming pace for guided meditations",
        "speed": 0.85,
        "pause_multiplier": 1.5,  # 50% longer pauses
        "word_rate": 120,  # words per minute
        "background_music": "ambient",
        "fade_in": 5,
        "fade_out": 10,
    },
    "narration": {
        "name": "Narration",
        "description": "Clear storytelling pace for audiobooks",
        "speed": 0.95,
        "pause_multiplier": 1.0,
        "word_rate": 150,
        "background_music": None,
        "fade_in": 2,
        "fade_out": 3,
    },
    "teaching": {
        "name": "Teaching",
        "description": "Natural pace for educational content",
        "speed": 1.0,
        "pause_multiplier": 0.8,  # Shorter pauses
        "word_rate": 160,
        "background_music": None,
        "fade_in": 1,
        "fade_out": 2,
    },
    "hypnosis": {
        "name": "Hypnosis",
        "description": "Very slow, rhythmic pace for inductions",
        "speed": 0.80,
        "pause_multiplier": 2.0,  # Double pauses
        "word_rate": 100,
        "background_music": "theta_binaural",
        "fade_in": 10,
        "fade_out": 15,
    },
    "podcast": {
        "name": "Podcast",
        "description": "Conversational pace for dynamic content",
        "speed": 1.05,
        "pause_multiplier": 0.7,  # Minimal pauses
        "word_rate": 170,
        "background_music": None,
        "fade_in": 0,
        "fade_out": 1,
    },
    "affirmation": {
        "name": "Affirmation",
        "description": "Clear, empowering pace for affirmations",
        "speed": 0.90,
        "pause_multiplier": 1.3,
        "word_rate": 130,
        "background_music": "432hz",
        "fade_in": 3,
        "fade_out": 5,
    },
}


def list_audio_templates() -> str:
    """List all available audio templates/presets."""
    lines = [
        "",
        "╔" + "═" * 72 + "╗",
        "║" + " " * 22 + "AUDIO TEMPLATES / PRESETS" + " " * 25 + "║",
        "╠" + "═" * 72 + "╣",
        "║ {:12} │ {:10} │ {:8} │ {:35} ║".format(
            "Template", "Speed", "WPM", "Description"),
        "╠" + "─" * 72 + "╣",
    ]
    
    for key, template in AUDIO_TEMPLATES.items():
        lines.append("║ {:12} │ {:10} │ {:8} │ {:35} ║".format(
            key,
            f"{template['speed']:.2f}x",
            str(template['word_rate']),
            template['description'][:35]
        ))
    
    lines.append("╠" + "═" * 72 + "╣")
    lines.append("║ Usage: product-builder generate-audio --preset meditation --all" + " " * 7 + "║")
    lines.append("╚" + "═" * 72 + "╝")
    
    return "\n".join(lines)


def get_audio_template(template_name: str) -> Optional[dict]:
    """Get an audio template by name."""
    return AUDIO_TEMPLATES.get(template_name)


# ═══════════════════════════════════════════════════════════════════════
# VOICE LIBRARY MANAGER
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class VoiceInfo:
    """Information about an available voice."""
    name: str
    engine: str  # xtts, piper, espeak
    path: Optional[Path]
    language: str
    gender: str
    description: str


def discover_voices() -> List[VoiceInfo]:
    """Discover all available voices across engines."""
    import shutil
    
    voices = []
    
    # 1. Discover XTTS voice samples
    voice_dirs = [
        Path.home() / "Projects/dreamweaving/assets/voices",
        Path.home() / "Projects/dreamweaving/voice_samples",
    ]
    
    for voice_dir in voice_dirs:
        if voice_dir.exists():
            for voice_file in voice_dir.glob("*.wav"):
                voices.append(VoiceInfo(
                    name=voice_file.stem,
                    engine="xtts",
                    path=voice_file,
                    language="en",
                    gender="unknown",
                    description=f"Custom XTTS voice: {voice_file.name}"
                ))
            for voice_file in voice_dir.glob("*.mp3"):
                voices.append(VoiceInfo(
                    name=voice_file.stem,
                    engine="xtts",
                    path=voice_file,
                    language="en",
                    gender="unknown",
                    description=f"Custom XTTS voice: {voice_file.name}"
                ))
    
    # 2. Discover Piper voices
    piper_models_dir = Path.home() / ".local/share/piper/voices"
    if piper_models_dir.exists():
        for model_file in piper_models_dir.glob("*.onnx"):
            name = model_file.stem
            parts = name.split("-")
            lang = parts[0] if parts else "en"
            voices.append(VoiceInfo(
                name=name,
                engine="piper",
                path=model_file,
                language=lang,
                gender="unknown",
                description=f"Piper model: {name}"
            ))
    
    # 3. Check for espeak-ng
    if shutil.which("espeak-ng"):
        # Add common espeak voices
        for voice_id, desc in [
            ("en-us", "American English"),
            ("en-gb", "British English"),
            ("en-au", "Australian English"),
        ]:
            voices.append(VoiceInfo(
                name=voice_id,
                engine="espeak",
                path=None,
                language="en",
                gender="neutral",
                description=f"espeak-ng: {desc}"
            ))
    
    return voices


def list_voices() -> str:
    """List all available voices in a formatted table."""
    voices = discover_voices()
    
    if not voices:
        return "\n📭 No voices found. Install Piper, espeak-ng, or add XTTS voice samples.\n"
    
    lines = [
        "",
        "╔" + "═" * 78 + "╗",
        "║" + " " * 28 + "VOICE LIBRARY" + " " * 37 + "║",
        "╠" + "═" * 78 + "╣",
        "║ {:20} │ {:8} │ {:6} │ {:35} ║".format(
            "Voice Name", "Engine", "Lang", "Description"),
        "╠" + "─" * 78 + "╣",
    ]
    
    # Group by engine
    by_engine = {}
    for v in voices:
        by_engine.setdefault(v.engine, []).append(v)
    
    for engine in ["xtts", "piper", "espeak"]:
        if engine in by_engine:
            lines.append(f"║ {'─' * 76} ║")
            lines.append(f"║ {engine.upper()} VOICES:{'':68} ║")
            for v in by_engine[engine]:
                lines.append("║ {:20} │ {:8} │ {:6} │ {:35} ║".format(
                    v.name[:20],
                    v.engine,
                    v.language,
                    v.description[:35]
                ))
    
    lines.append("╠" + "═" * 78 + "╣")
    lines.append(f"║ Total: {len(voices)} voices available" + " " * 55 + "║")
    lines.append("╚" + "═" * 78 + "╝")
    
    return "\n".join(lines)


def get_voice_by_name(name: str) -> Optional[VoiceInfo]:
    """Find a voice by name."""
    voices = discover_voices()
    for v in voices:
        if v.name.lower() == name.lower():
            return v
    return None


# ═══════════════════════════════════════════════════════════════════════
# AUDIO QUALITY ANALYZER
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class AudioQualityReport:
    """Quality analysis results for an audio file."""
    file_path: Path
    duration_seconds: float
    expected_duration: float  # Based on word count
    sample_rate: int
    channels: int
    bit_depth: int
    peak_level: float  # 0.0 to 1.0
    rms_level: float  # Average loudness
    silence_ratio: float  # Proportion of silence
    issues: List[str]
    quality_score: int  # 0-100


def analyze_audio_file(audio_path: Path, expected_words: int = 0) -> Optional[AudioQualityReport]:
    """Analyze an audio file for quality issues."""
    import subprocess
    import json
    
    if not audio_path.exists():
        return None
    
    try:
        # Use ffprobe to get audio info
        result = subprocess.run([
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", "-show_streams", str(audio_path)
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            return None
        
        info = json.loads(result.stdout)
        audio_stream = None
        for stream in info.get("streams", []):
            if stream.get("codec_type") == "audio":
                audio_stream = stream
                break
        
        if not audio_stream:
            return None
        
        duration = float(info.get("format", {}).get("duration", 0))
        sample_rate = int(audio_stream.get("sample_rate", 44100))
        channels = int(audio_stream.get("channels", 2))
        
        # Expected duration based on word count (150 wpm default)
        expected_duration = (expected_words / 150) * 60 if expected_words > 0 else duration
        
        # Analyze audio levels with ffmpeg
        level_result = subprocess.run([
            "ffmpeg", "-i", str(audio_path), "-af", 
            "volumedetect", "-f", "null", "-"
        ], capture_output=True, text=True, timeout=60)
        
        # Parse volume levels from stderr
        peak_level = 0.5
        rms_level = 0.3
        for line in level_result.stderr.split("\n"):
            if "max_volume" in line:
                try:
                    val = float(line.split(":")[1].strip().replace(" dB", ""))
                    peak_level = min(1.0, 10 ** (val / 20))
                except:
                    pass
            elif "mean_volume" in line:
                try:
                    val = float(line.split(":")[1].strip().replace(" dB", ""))
                    rms_level = min(1.0, 10 ** (val / 20))
                except:
                    pass
        
        # Detect quality issues
        issues = []
        quality_score = 100
        
        # Duration check
        duration_diff = abs(duration - expected_duration) / max(expected_duration, 1)
        if duration_diff > 0.3:  # More than 30% off
            issues.append(f"Duration differs from expected by {duration_diff*100:.0f}%")
            quality_score -= 15
        
        # Clipping check
        if peak_level > 0.98:
            issues.append("Audio may be clipping (peak > 98%)")
            quality_score -= 20
        
        # Too quiet
        if rms_level < 0.1:
            issues.append("Audio may be too quiet (RMS < 10%)")
            quality_score -= 10
        
        # Sample rate check
        if sample_rate < 22050:
            issues.append(f"Low sample rate: {sample_rate}Hz")
            quality_score -= 10
        
        # Estimate silence ratio (rough approximation)
        silence_ratio = max(0, 1 - (rms_level * 5))  # Very rough estimate
        
        return AudioQualityReport(
            file_path=audio_path,
            duration_seconds=duration,
            expected_duration=expected_duration,
            sample_rate=sample_rate,
            channels=channels,
            bit_depth=16,  # Assume 16-bit
            peak_level=peak_level,
            rms_level=rms_level,
            silence_ratio=silence_ratio,
            issues=issues,
            quality_score=max(0, quality_score)
        )
        
    except Exception as e:
        return None


def analyze_product_audio(product_dir: Path) -> Tuple[List[AudioQualityReport], str]:
    """Analyze all audio files in a product directory."""
    audio_dir = product_dir / "output" / "audio"
    responses_dir = product_dir / "output" / "responses"
    
    if not audio_dir.exists():
        return [], "No audio directory found"
    
    reports = []
    
    for audio_file in sorted(audio_dir.glob("*.mp3")):
        # Try to find matching response for word count
        slug = audio_file.stem
        response_file = responses_dir / f"{slug}.response.md"
        word_count = 0
        
        if response_file.exists():
            word_count = len(response_file.read_text().split())
        
        report = analyze_audio_file(audio_file, word_count)
        if report:
            reports.append(report)
    
    # Also check WAV files
    for audio_file in sorted(audio_dir.glob("*.wav")):
        report = analyze_audio_file(audio_file, 0)
        if report:
            reports.append(report)
    
    return reports, f"Analyzed {len(reports)} audio files"


def format_audio_quality_report(reports: List[AudioQualityReport]) -> str:
    """Format audio quality reports for display."""
    if not reports:
        return "\n📭 No audio files found to analyze.\n"
    
    lines = [
        "",
        "╔" + "═" * 78 + "╗",
        "║" + " " * 24 + "AUDIO QUALITY REPORT" + " " * 34 + "║",
        "╠" + "═" * 78 + "╣",
        "║ {:25} │ {:8} │ {:6} │ {:6} │ {:20} ║".format(
            "File", "Duration", "Peak", "Score", "Status"),
        "╠" + "─" * 78 + "╣",
    ]
    
    total_duration = 0
    total_score = 0
    
    for r in reports:
        duration_str = f"{int(r.duration_seconds // 60)}:{int(r.duration_seconds % 60):02d}"
        peak_str = f"{r.peak_level * 100:.0f}%"
        score_str = f"{r.quality_score}%"
        
        if r.quality_score >= 90:
            status = "✅ Excellent"
        elif r.quality_score >= 70:
            status = "✅ Good"
        elif r.quality_score >= 50:
            status = "⚠️  Fair"
        else:
            status = "❌ Issues"
        
        total_duration += r.duration_seconds
        total_score += r.quality_score
        
        lines.append("║ {:25} │ {:8} │ {:6} │ {:6} │ {:20} ║".format(
            r.file_path.name[:25],
            duration_str,
            peak_str,
            score_str,
            status
        ))
        
        # Show issues if any
        for issue in r.issues[:2]:  # Max 2 issues per file
            lines.append(f"║   ⚠️  {issue[:70]:<70} ║")
    
    # Summary
    avg_score = total_score / len(reports) if reports else 0
    total_mins = int(total_duration // 60)
    total_secs = int(total_duration % 60)
    
    lines.append("╠" + "═" * 78 + "╣")
    lines.append(f"║ Total Duration: {total_mins}:{total_secs:02d} │ Average Quality: {avg_score:.0f}%" + " " * 32 + "║")
    
    if avg_score >= 80:
        lines.append("║ 🎵 Audio quality is good! Ready for publishing." + " " * 28 + "║")
    else:
        lines.append("║ ⚠️  Some quality issues detected. Review before publishing." + " " * 16 + "║")
    
    lines.append("╚" + "═" * 78 + "╝")
    
    return "\n".join(lines)


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
# STEP 3C ENHANCEMENTS: STYLES, QUALITY ANALYZER, THUMBNAIL GENERATOR
# ═══════════════════════════════════════════════════════════════════════


# Video style presets for consistent branding
VIDEO_STYLES = {
    "dreamweaving": {
        "name": "Dreamweaving",
        "description": "Mystical purple/teal with starfield background",
        "primary_color": "#9b59b6",
        "secondary_color": "#1abc9c",
        "background": "starfield",
        "font_family": "Playfair Display",
        "animation_style": "smooth_fades",
        "overlay_opacity": 0.3,
    },
    "professional": {
        "name": "Professional",
        "description": "Clean navy/white with minimal design",
        "primary_color": "#2c3e50",
        "secondary_color": "#ecf0f1",
        "background": "gradient",
        "font_family": "Inter",
        "animation_style": "minimal",
        "overlay_opacity": 0.1,
    },
    "energetic": {
        "name": "Energetic",
        "description": "Vibrant colors with dynamic motion",
        "primary_color": "#e74c3c",
        "secondary_color": "#f1c40f",
        "background": "particles",
        "font_family": "Poppins",
        "animation_style": "dynamic",
        "overlay_opacity": 0.2,
    },
    "calming": {
        "name": "Calming",
        "description": "Soft pastels with nature imagery",
        "primary_color": "#74b9ff",
        "secondary_color": "#a29bfe",
        "background": "nature",
        "font_family": "Lora",
        "animation_style": "slow_dissolves",
        "overlay_opacity": 0.4,
    },
    "dark_mode": {
        "name": "Dark Mode",
        "description": "Dark background with accent glow",
        "primary_color": "#00d2d3",
        "secondary_color": "#ff6b6b",
        "background": "dark_minimal",
        "font_family": "Space Grotesk",
        "animation_style": "subtle_glow",
        "overlay_opacity": 0.15,
    },
    "educational": {
        "name": "Educational",
        "description": "Clean whiteboard style for teaching",
        "primary_color": "#3498db",
        "secondary_color": "#2ecc71",
        "background": "whiteboard",
        "font_family": "Open Sans",
        "animation_style": "draw_in",
        "overlay_opacity": 0.05,
    },
}


def list_video_styles() -> str:
    """List all available video style presets."""
    lines = [
        "",
        "╔" + "═" * 78 + "╗",
        "║" + " " * 26 + "VIDEO STYLE PRESETS" + " " * 33 + "║",
        "╠" + "═" * 78 + "╣",
        "║ {:15} │ {:12} │ {:45} ║".format(
            "Style", "Font", "Description"),
        "╠" + "─" * 78 + "╣",
    ]
    
    for key, style in VIDEO_STYLES.items():
        lines.append("║ {:15} │ {:12} │ {:45} ║".format(
            key,
            style['font_family'][:12],
            style['description'][:45]
        ))
    
    lines.append("╠" + "═" * 78 + "╣")
    lines.append("║ Usage: product-builder render-video --style dreamweaving --all" + " " * 14 + "║")
    lines.append("╚" + "═" * 78 + "╝")
    
    return "\n".join(lines)


def get_video_style(style_name: str) -> Optional[dict]:
    """Get a video style by name."""
    return VIDEO_STYLES.get(style_name)


# ═══════════════════════════════════════════════════════════════════════
# VIDEO QUALITY ANALYZER
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class VideoQualityReport:
    """Quality analysis results for a video file."""
    file_path: Path
    duration_seconds: float
    width: int
    height: int
    fps: float
    bitrate_kbps: int
    file_size_mb: float
    has_audio: bool
    audio_bitrate: int
    codec: str
    issues: List[str]
    quality_score: int  # 0-100


def analyze_video_file(video_path: Path, expected_duration: float = 0) -> Optional[VideoQualityReport]:
    """Analyze a video file for quality issues."""
    import subprocess
    import json
    
    if not video_path.exists():
        return None
    
    try:
        # Use ffprobe to get video info
        result = subprocess.run([
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", "-show_streams", str(video_path)
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            return None
        
        info = json.loads(result.stdout)
        
        # Find video and audio streams
        video_stream = None
        audio_stream = None
        for stream in info.get("streams", []):
            if stream.get("codec_type") == "video" and not video_stream:
                video_stream = stream
            elif stream.get("codec_type") == "audio" and not audio_stream:
                audio_stream = stream
        
        if not video_stream:
            return None
        
        # Extract info
        duration = float(info.get("format", {}).get("duration", 0))
        width = int(video_stream.get("width", 0))
        height = int(video_stream.get("height", 0))
        
        # Calculate FPS
        fps_str = video_stream.get("r_frame_rate", "30/1")
        if "/" in fps_str:
            num, denom = fps_str.split("/")
            fps = float(num) / float(denom) if float(denom) > 0 else 30
        else:
            fps = float(fps_str)
        
        # Bitrate
        bitrate = int(info.get("format", {}).get("bit_rate", 0)) // 1000
        
        # File size
        file_size_mb = video_path.stat().st_size / (1024 * 1024)
        
        # Audio info
        has_audio = audio_stream is not None
        audio_bitrate = int(audio_stream.get("bit_rate", 0)) // 1000 if audio_stream else 0
        
        # Codec
        codec = video_stream.get("codec_name", "unknown")
        
        # Detect quality issues
        issues = []
        quality_score = 100
        
        # Resolution check
        if width < 1280 or height < 720:
            issues.append(f"Low resolution: {width}x{height} (recommend 1920x1080)")
            quality_score -= 15
        
        # Aspect ratio check
        aspect = width / height if height > 0 else 0
        if abs(aspect - 16/9) > 0.1 and abs(aspect - 9/16) > 0.1:
            issues.append(f"Non-standard aspect ratio: {aspect:.2f}")
            quality_score -= 5
        
        # FPS check
        if fps < 24:
            issues.append(f"Low frame rate: {fps:.1f} fps (recommend 30+)")
            quality_score -= 10
        
        # Bitrate check
        if bitrate > 0 and bitrate < 2000:
            issues.append(f"Low bitrate: {bitrate} kbps (may look blocky)")
            quality_score -= 10
        
        # Audio check
        if not has_audio:
            issues.append("No audio track detected")
            quality_score -= 20
        elif audio_bitrate < 96:
            issues.append(f"Low audio bitrate: {audio_bitrate} kbps")
            quality_score -= 5
        
        # Duration check
        if expected_duration > 0:
            duration_diff = abs(duration - expected_duration) / expected_duration
            if duration_diff > 0.2:
                issues.append(f"Duration differs from expected by {duration_diff*100:.0f}%")
                quality_score -= 10
        
        # File size check (suspicious if too small or too large)
        minutes = duration / 60
        if minutes > 0:
            mb_per_minute = file_size_mb / minutes
            if mb_per_minute < 5:
                issues.append(f"Very low file size: {mb_per_minute:.1f} MB/min")
                quality_score -= 10
        
        return VideoQualityReport(
            file_path=video_path,
            duration_seconds=duration,
            width=width,
            height=height,
            fps=fps,
            bitrate_kbps=bitrate,
            file_size_mb=file_size_mb,
            has_audio=has_audio,
            audio_bitrate=audio_bitrate,
            codec=codec,
            issues=issues,
            quality_score=max(0, quality_score)
        )
        
    except Exception as e:
        return None


def analyze_product_videos(product_dir: Path) -> Tuple[List[VideoQualityReport], str]:
    """Analyze all video files in a product directory."""
    video_dir = product_dir / "output" / "video"
    
    if not video_dir.exists():
        return [], "No video directory found"
    
    reports = []
    
    for video_file in sorted(video_dir.glob("*.mp4")):
        report = analyze_video_file(video_file)
        if report:
            reports.append(report)
    
    # Also check for webm files
    for video_file in sorted(video_dir.glob("*.webm")):
        report = analyze_video_file(video_file)
        if report:
            reports.append(report)
    
    return reports, f"Analyzed {len(reports)} video files"


def format_video_quality_report(reports: List[VideoQualityReport]) -> str:
    """Format video quality reports for display."""
    if not reports:
        return "\n📭 No video files found to analyze.\n"
    
    lines = [
        "",
        "╔" + "═" * 88 + "╗",
        "║" + " " * 30 + "VIDEO QUALITY REPORT" + " " * 38 + "║",
        "╠" + "═" * 88 + "╣",
        "║ {:25} │ {:10} │ {:10} │ {:8} │ {:6} │ {:15} ║".format(
            "File", "Resolution", "Duration", "FPS", "Score", "Status"),
        "╠" + "─" * 88 + "╣",
    ]
    
    total_duration = 0
    total_score = 0
    total_size = 0
    
    for r in reports:
        duration_str = f"{int(r.duration_seconds // 60)}:{int(r.duration_seconds % 60):02d}"
        resolution = f"{r.width}x{r.height}"
        fps_str = f"{r.fps:.0f}"
        score_str = f"{r.quality_score}%"
        
        if r.quality_score >= 90:
            status = "✅ Excellent"
        elif r.quality_score >= 70:
            status = "✅ Good"
        elif r.quality_score >= 50:
            status = "⚠️  Fair"
        else:
            status = "❌ Issues"
        
        total_duration += r.duration_seconds
        total_score += r.quality_score
        total_size += r.file_size_mb
        
        lines.append("║ {:25} │ {:10} │ {:10} │ {:8} │ {:6} │ {:15} ║".format(
            r.file_path.name[:25],
            resolution,
            duration_str,
            fps_str,
            score_str,
            status
        ))
        
        # Show issues if any
        for issue in r.issues[:2]:
            lines.append(f"║   ⚠️  {issue[:80]:<80} ║")
    
    # Summary
    avg_score = total_score / len(reports) if reports else 0
    total_mins = int(total_duration // 60)
    total_secs = int(total_duration % 60)
    
    lines.append("╠" + "═" * 88 + "╣")
    lines.append(f"║ Total: {total_mins}:{total_secs:02d} │ {total_size:.1f} MB │ Avg Quality: {avg_score:.0f}%" + " " * 43 + "║")
    
    if avg_score >= 80:
        lines.append("║ 🎬 Video quality is good! Ready for publishing." + " " * 38 + "║")
    else:
        lines.append("║ ⚠️  Some quality issues detected. Review before publishing." + " " * 26 + "║")
    
    lines.append("╚" + "═" * 88 + "╝")
    
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════
# THUMBNAIL GENERATOR
# ═══════════════════════════════════════════════════════════════════════


# Thumbnail size presets
THUMBNAIL_SIZES = {
    "youtube": {"width": 1280, "height": 720, "name": "YouTube"},
    "social": {"width": 1200, "height": 630, "name": "Social Media"},
    "square": {"width": 1080, "height": 1080, "name": "Square (IG)"},
    "story": {"width": 1080, "height": 1920, "name": "Vertical Story"},
    "twitter": {"width": 1600, "height": 900, "name": "Twitter"},
}


def list_thumbnail_sizes() -> str:
    """List thumbnail size presets."""
    lines = [
        "",
        "╔" + "═" * 60 + "╗",
        "║" + " " * 18 + "THUMBNAIL SIZES" + " " * 27 + "║",
        "╠" + "═" * 60 + "╣",
        "║ {:12} │ {:15} │ {:25} ║".format("Preset", "Dimensions", "Use Case"),
        "╠" + "─" * 60 + "╣",
    ]
    
    for key, size in THUMBNAIL_SIZES.items():
        dims = f"{size['width']}x{size['height']}"
        lines.append("║ {:12} │ {:15} │ {:25} ║".format(
            key, dims, size['name']
        ))
    
    lines.append("╚" + "═" * 60 + "╝")
    return "\n".join(lines)


def extract_frame_from_video(
    video_path: Path,
    output_path: Path,
    timestamp: float = 5.0,
    size_preset: str = "youtube"
) -> Tuple[bool, str]:
    """Extract a frame from video as thumbnail."""
    import subprocess
    
    if not video_path.exists():
        return False, f"Video not found: {video_path}"
    
    size = THUMBNAIL_SIZES.get(size_preset, THUMBNAIL_SIZES["youtube"])
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(timestamp),
        "-i", str(video_path),
        "-vframes", "1",
        "-vf", f"scale={size['width']}:{size['height']}:force_original_aspect_ratio=decrease,pad={size['width']}:{size['height']}:(ow-iw)/2:(oh-ih)/2",
        str(output_path)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=30)
        
        if result.returncode == 0 and output_path.exists():
            return True, f"Created thumbnail: {output_path}"
        else:
            return False, f"Failed: {result.stderr.decode()[:100]}"
    except Exception as e:
        return False, f"Error: {str(e)}"


def generate_video_thumbnail(
    video_path: Path,
    output_path: Path = None,
    text_overlay: str = None,
    size_preset: str = "youtube",
    timestamp: float = None
) -> Tuple[bool, str]:
    """
    Generate a thumbnail from video with optional text overlay.
    
    If timestamp is None, tries multiple points to find a good frame.
    """
    import subprocess
    
    if not video_path.exists():
        return False, f"Video not found: {video_path}"
    
    if output_path is None:
        output_path = video_path.parent / f"{video_path.stem}_thumb.jpg"
    
    size = THUMBNAIL_SIZES.get(size_preset, THUMBNAIL_SIZES["youtube"])
    
    # If no timestamp specified, try to find a good frame
    if timestamp is None:
        # Get video duration first
        probe_cmd = [
            "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)
        ]
        try:
            result = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=10)
            duration = float(result.stdout.strip()) if result.stdout.strip() else 30
            # Pick a point about 20% into the video
            timestamp = min(duration * 0.2, 10)
        except:
            timestamp = 5.0
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Build filter chain
    filters = [
        f"scale={size['width']}:{size['height']}:force_original_aspect_ratio=decrease",
        f"pad={size['width']}:{size['height']}:(ow-iw)/2:(oh-ih)/2"
    ]
    
    # Add text overlay if provided
    if text_overlay:
        # Escape special characters for ffmpeg
        safe_text = text_overlay.replace("'", "'\\''").replace(":", "\\:")
        filters.append(
            f"drawtext=text='{safe_text}':fontsize=64:fontcolor=white:"
            f"x=(w-text_w)/2:y=h-100:shadowcolor=black:shadowx=2:shadowy=2"
        )
    
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(timestamp),
        "-i", str(video_path),
        "-vframes", "1",
        "-vf", ",".join(filters),
        "-q:v", "2",  # High quality JPEG
        str(output_path)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=30)
        
        if result.returncode == 0 and output_path.exists():
            size_kb = output_path.stat().st_size // 1024
            return True, f"Created: {output_path} ({size_kb}KB)"
        else:
            return False, f"Failed: {result.stderr.decode()[:100]}"
    except Exception as e:
        return False, f"Error: {str(e)}"


def generate_all_thumbnails(
    product_dir: Path,
    size_preset: str = "youtube"
) -> Tuple[int, List[str]]:
    """Generate thumbnails for all videos in a product."""
    video_dir = product_dir / "output" / "video"
    thumb_dir = product_dir / "output" / "thumbnails"
    
    if not video_dir.exists():
        return 0, ["No video directory found"]
    
    thumb_dir.mkdir(parents=True, exist_ok=True)
    
    results = []
    success_count = 0
    
    for video_file in sorted(video_dir.glob("*.mp4")):
        output_path = thumb_dir / f"{video_file.stem}.jpg"
        success, message = generate_video_thumbnail(
            video_file, output_path, size_preset=size_preset
        )
        results.append(f"{video_file.name}: {message}")
        if success:
            success_count += 1
    
    return success_count, results


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


# ═══════════════════════════════════════════════════════════════════════
# STEP 3D ENHANCEMENTS: SEO, OG IMAGES, PREFLIGHT CHECKLIST
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class SEOMetadata:
    """SEO metadata for a product page."""
    title: str  # 55-60 chars
    description: str  # 150-160 chars
    keywords: List[str]
    canonical_url: str
    og_title: str
    og_description: str
    og_image: str
    schema_json: dict


def generate_seo_metadata(
    product_title: str,
    product_description: str,
    category: str,
    slug: str,
    price: float,
    image_url: str = None,
    base_url: str = "https://salars.net"
) -> SEOMetadata:
    """Generate optimized SEO metadata for a product."""
    
    # Truncate title to 55-60 chars
    seo_title = product_title[:55] + "..." if len(product_title) > 58 else product_title
    if len(seo_title) < 50:
        seo_title = f"{seo_title} | SalarsNet"
    
    # Truncate description to 150-160 chars
    if len(product_description) > 155:
        seo_description = product_description[:150].rsplit(' ', 1)[0] + "..."
    else:
        seo_description = product_description
    
    # Generate keywords from title and category
    words = product_title.lower().split()
    cat_info = DIGITAL_CATEGORIES.get(category, {"name": category})
    keywords = list(set([
        category,
        cat_info.get("name", category).lower(),
        "digital product",
        "download",
        "ebook",
        *[w for w in words if len(w) > 3]
    ]))[:10]
    
    canonical_url = f"{base_url}/digital/{slug}"
    og_image = image_url or f"{base_url}/images/products/{slug}.png"
    
    # Schema.org Product JSON-LD
    schema_json = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": product_title,
        "description": product_description[:500],
        "image": og_image,
        "url": canonical_url,
        "sku": f"DIG-{slug.upper()[:10]}",
        "category": cat_info.get("name", category),
        "offers": {
            "@type": "Offer",
            "priceCurrency": "USD",
            "price": price,
            "availability": "https://schema.org/InStock",
            "seller": {
                "@type": "Organization",
                "name": "SalarsNet"
            }
        },
        "brand": {
            "@type": "Brand",
            "name": "SalarsNet"
        }
    }
    
    return SEOMetadata(
        title=seo_title,
        description=seo_description,
        keywords=keywords,
        canonical_url=canonical_url,
        og_title=product_title[:60],
        og_description=seo_description,
        og_image=og_image,
        schema_json=schema_json
    )


def format_seo_metadata(seo: SEOMetadata) -> str:
    """Format SEO metadata for display."""
    import json
    
    lines = [
        "",
        "╔" + "═" * 78 + "╗",
        "║" + " " * 28 + "SEO METADATA" + " " * 38 + "║",
        "╠" + "═" * 78 + "╣",
        f"║ Title ({len(seo.title)} chars):".ljust(79) + "║",
        f"║   {seo.title[:72]}".ljust(79) + "║",
        "║".ljust(79) + "║",
        f"║ Description ({len(seo.description)} chars):".ljust(79) + "║",
        f"║   {seo.description[:72]}".ljust(79) + "║",
        "║".ljust(79) + "║",
        f"║ Keywords: {', '.join(seo.keywords[:5])}".ljust(79) + "║",
        f"║ Canonical: {seo.canonical_url[:65]}".ljust(79) + "║",
        f"║ OG Image: {seo.og_image[:65]}".ljust(79) + "║",
        "╠" + "═" * 78 + "╣",
        "║ Schema.org JSON-LD:".ljust(79) + "║",
    ]
    
    schema_str = json.dumps(seo.schema_json, indent=2)
    for line in schema_str.split('\n')[:8]:
        lines.append(f"║   {line[:73]}".ljust(79) + "║")
    lines.append("║   ...".ljust(79) + "║")
    
    lines.append("╚" + "═" * 78 + "╝")
    return "\n".join(lines)


def export_seo_metadata(seo: SEOMetadata, output_dir: Path) -> Tuple[bool, str]:
    """Export SEO metadata to files."""
    import json
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # HTML meta tags
    meta_html = f'''<!-- SEO Meta Tags - Generated by Epistemic Factory -->
<title>{seo.title}</title>
<meta name="description" content="{seo.description}">
<meta name="keywords" content="{', '.join(seo.keywords)}">
<link rel="canonical" href="{seo.canonical_url}">

<!-- Open Graph -->
<meta property="og:title" content="{seo.og_title}">
<meta property="og:description" content="{seo.og_description}">
<meta property="og:image" content="{seo.og_image}">
<meta property="og:url" content="{seo.canonical_url}">
<meta property="og:type" content="product">

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{seo.og_title}">
<meta name="twitter:description" content="{seo.og_description}">
<meta name="twitter:image" content="{seo.og_image}">

<!-- Schema.org JSON-LD -->
<script type="application/ld+json">
{json.dumps(seo.schema_json, indent=2)}
</script>
'''
    
    meta_file = output_dir / "seo_meta.html"
    meta_file.write_text(meta_html)
    
    # Also save as JSON for programmatic use
    json_file = output_dir / "seo_metadata.json"
    json_file.write_text(json.dumps({
        "title": seo.title,
        "description": seo.description,
        "keywords": seo.keywords,
        "canonical_url": seo.canonical_url,
        "og_title": seo.og_title,
        "og_description": seo.og_description,
        "og_image": seo.og_image,
        "schema": seo.schema_json
    }, indent=2))
    
    return True, f"Exported SEO metadata to: {meta_file}"


# ═══════════════════════════════════════════════════════════════════════
# OG/SOCIAL CARD GENERATOR
# ═══════════════════════════════════════════════════════════════════════


# OG image style presets
OG_IMAGE_STYLES = {
    "default": {
        "name": "Default",
        "description": "Product title with price badge",
        "bg_color": "#1a1a2e",
        "accent_color": "#9b59b6",
        "text_color": "#ffffff",
    },
    "minimal": {
        "name": "Minimal",
        "description": "Clean title only",
        "bg_color": "#ffffff",
        "accent_color": "#333333",
        "text_color": "#333333",
    },
    "promo": {
        "name": "Promo/Sale",
        "description": "Title with sale badge",
        "bg_color": "#e74c3c",
        "accent_color": "#f1c40f",
        "text_color": "#ffffff",
    },
    "dreamweaving": {
        "name": "Dreamweaving",
        "description": "Purple mystical theme",
        "bg_color": "#1a0a2e",
        "accent_color": "#00d2d3",
        "text_color": "#e8e8e8",
    },
}


def list_og_styles() -> str:
    """List OG image style presets."""
    lines = [
        "",
        "╔" + "═" * 60 + "╗",
        "║" + " " * 17 + "OG IMAGE STYLES" + " " * 28 + "║",
        "╠" + "═" * 60 + "╣",
        "║ {:15} │ {:40} ║".format("Style", "Description"),
        "╠" + "─" * 60 + "╣",
    ]
    
    for key, style in OG_IMAGE_STYLES.items():
        lines.append("║ {:15} │ {:40} ║".format(
            key, style['description']
        ))
    
    lines.append("╚" + "═" * 60 + "╝")
    return "\n".join(lines)


def generate_og_image(
    title: str,
    output_path: Path,
    subtitle: str = None,
    price: float = None,
    style: str = "default",
    sale_badge: bool = False
) -> Tuple[bool, str]:
    """
    Generate an OG image for social sharing using ImageMagick.
    
    Creates a 1200x630 image with title, optional subtitle/price.
    """
    import subprocess
    
    style_config = OG_IMAGE_STYLES.get(style, OG_IMAGE_STYLES["default"])
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Build ImageMagick command
    cmd = [
        "convert",
        "-size", "1200x630",
        f"xc:{style_config['bg_color']}",
        # Add gradient overlay
        "-fill", f"rgba(0,0,0,0.3)",
        "-draw", "rectangle 0,0 1200,630",
    ]
    
    # Main title
    title_size = 72 if len(title) < 30 else 56 if len(title) < 50 else 44
    cmd.extend([
        "-gravity", "Center",
        "-fill", style_config['text_color'],
        "-font", "Helvetica-Bold",
        "-pointsize", str(title_size),
        "-annotate", "+0-50", title[:60],
    ])
    
    # Subtitle if provided
    if subtitle:
        cmd.extend([
            "-pointsize", "28",
            "-annotate", "+0+40", subtitle[:80],
        ])
    
    # Price badge if provided
    if price:
        price_str = f"${price:.0f}" if price == int(price) else f"${price:.2f}"
        cmd.extend([
            "-gravity", "SouthEast",
            "-fill", style_config['accent_color'],
            "-pointsize", "36",
            "-annotate", "+50+50", price_str,
        ])
    
    # Sale badge if enabled
    if sale_badge:
        cmd.extend([
            "-gravity", "NorthEast",
            "-fill", "#e74c3c",
            "-draw", "circle 1140,60 1140,100",
            "-fill", "white",
            "-pointsize", "18",
            "-annotate", "+40+65", "SALE",
        ])
    
    # Add SalarsNet branding
    cmd.extend([
        "-gravity", "SouthWest",
        "-fill", "rgba(255,255,255,0.6)",
        "-pointsize", "20",
        "-annotate", "+30+30", "SalarsNet",
    ])
    
    cmd.append(str(output_path))
    
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=30)
        
        if result.returncode == 0 and output_path.exists():
            size_kb = output_path.stat().st_size // 1024
            return True, f"Created: {output_path} ({size_kb}KB)"
        else:
            # Fallback: try simpler approach
            simple_cmd = [
                "convert",
                "-size", "1200x630",
                f"xc:{style_config['bg_color']}",
                "-gravity", "Center",
                "-fill", style_config['text_color'],
                "-pointsize", "60",
                "-annotate", "0", title[:40],
                str(output_path)
            ]
            result2 = subprocess.run(simple_cmd, capture_output=True, timeout=30)
            if result2.returncode == 0 and output_path.exists():
                return True, f"Created (simple): {output_path}"
            return False, f"Failed: {result.stderr.decode()[:100]}"
    except FileNotFoundError:
        return False, "ImageMagick not installed. Install with: sudo apt install imagemagick"
    except Exception as e:
        return False, f"Error: {str(e)}"


def generate_product_og_images(
    product_dir: Path,
    title: str = None,
    price: float = None
) -> Tuple[int, List[str]]:
    """Generate all OG images for a product."""
    import json
    
    output_dir = product_dir / "output" / "og_images"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load product info if not provided
    if not title:
        config_file = product_dir / "product.json"
        if config_file.exists():
            config = json.loads(config_file.read_text())
            title = config.get("title", "Digital Product")
            price = config.get("price", 0)
        else:
            title = "Digital Product"
    
    results = []
    success_count = 0
    
    # Generate each style
    for style_name in ["default", "minimal", "dreamweaving"]:
        output_path = output_dir / f"og_{style_name}.png"
        success, message = generate_og_image(
            title, output_path,
            price=price,
            style=style_name
        )
        results.append(f"{style_name}: {message}")
        if success:
            success_count += 1
    
    return success_count, results


# ═══════════════════════════════════════════════════════════════════════
# PREFLIGHT CHECKLIST
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class PreflightCheck:
    """A single preflight check result."""
    name: str
    passed: bool
    message: str
    severity: str  # "error", "warning", "info"


def run_preflight_checks(product_dir: Path) -> List[PreflightCheck]:
    """Run comprehensive preflight checks before deployment."""
    import json
    
    checks = []
    
    # 1. product.json exists and is valid
    config_file = product_dir / "product.json"
    if config_file.exists():
        try:
            config = json.loads(config_file.read_text())
            if config.get("title") and config.get("price"):
                checks.append(PreflightCheck(
                    "Product Config", True,
                    f"Valid: {config.get('title')[:30]}",
                    "info"
                ))
            else:
                checks.append(PreflightCheck(
                    "Product Config", False,
                    "Missing title or price in product.json",
                    "error"
                ))
        except json.JSONDecodeError:
            checks.append(PreflightCheck(
                "Product Config", False,
                "Invalid JSON in product.json",
                "error"
            ))
    else:
        checks.append(PreflightCheck(
            "Product Config", False,
            "product.json not found",
            "error"
        ))
    
    # 2. Cover image exists and is correct size
    image_found = False
    for img in ["cover.png", "cover.jpg", "product.png", "product.jpg"]:
        img_path = product_dir / "output" / "images" / img
        if img_path.exists():
            image_found = True
            size_kb = img_path.stat().st_size // 1024
            if size_kb > 2000:
                checks.append(PreflightCheck(
                    "Cover Image", False,
                    f"Image too large: {size_kb}KB (max 2MB)",
                    "warning"
                ))
            else:
                checks.append(PreflightCheck(
                    "Cover Image", True,
                    f"Found: {img} ({size_kb}KB)",
                    "info"
                ))
            break
    if not image_found:
        checks.append(PreflightCheck(
            "Cover Image", False,
            "No cover image found (cover.png/jpg needed)",
            "error"
        ))
    
    # 3. Download file exists
    zip_found = False
    for zip_file in (product_dir / "output").glob("*.zip"):
        zip_found = True
        size_mb = zip_file.stat().st_size / (1024 * 1024)
        checks.append(PreflightCheck(
            "Download File", True,
            f"Found: {zip_file.name} ({size_mb:.1f}MB)",
            "info"
        ))
        break
    if not zip_found:
        checks.append(PreflightCheck(
            "Download File", False,
            "No ZIP file found in output/",
            "error"
        ))
    
    # 4. Landing page content
    landing_file = product_dir / "output" / "responses" / "landing_page.response.md"
    if landing_file.exists():
        success, content = parse_landing_page_response(landing_file)
        if success:
            checks.append(PreflightCheck(
                "Landing Page", True,
                "Valid landing page content",
                "info"
            ))
        else:
            checks.append(PreflightCheck(
                "Landing Page", False,
                "Could not parse landing page content",
                "warning"
            ))
    else:
        checks.append(PreflightCheck(
            "Landing Page", False,
            "Landing page content not found",
            "warning"
        ))
    
    # 5. Price check
    if config_file.exists():
        try:
            config = json.loads(config_file.read_text())
            price = config.get("price", 0)
            if price <= 0:
                checks.append(PreflightCheck(
                    "Pricing", False,
                    "Price must be greater than 0",
                    "error"
                ))
            elif price < 5:
                checks.append(PreflightCheck(
                    "Pricing", True,
                    f"Low price: ${price} (consider increasing)",
                    "warning"
                ))
            else:
                checks.append(PreflightCheck(
                    "Pricing", True,
                    f"Price set: ${price}",
                    "info"
                ))
        except:
            pass
    
    # 6. SEO metadata
    seo_file = product_dir / "output" / "seo_metadata.json"
    if seo_file.exists():
        checks.append(PreflightCheck(
            "SEO Metadata", True,
            "SEO metadata generated",
            "info"
        ))
    else:
        checks.append(PreflightCheck(
            "SEO Metadata", False,
            "Run: product-builder generate-seo -d [dir]",
            "warning"
        ))
    
    # 7. SQL export
    sql_file = product_dir / "output" / "store_insert.sql"
    if sql_file.exists():
        checks.append(PreflightCheck(
            "SQL Export", True,
            "Store SQL ready",
            "info"
        ))
    else:
        checks.append(PreflightCheck(
            "SQL Export", False,
            "Run: product-builder generate-sql -d [dir]",
            "warning"
        ))
    
    return checks


def format_preflight_results(checks: List[PreflightCheck]) -> str:
    """Format preflight check results for display."""
    lines = [
        "",
        "╔" + "═" * 70 + "╗",
        "║" + " " * 22 + "PREFLIGHT CHECKLIST" + " " * 29 + "║",
        "╠" + "═" * 70 + "╣",
    ]
    
    passed = 0
    failed = 0
    warnings = 0
    
    for check in checks:
        if check.passed:
            icon = "✅"
            passed += 1
        elif check.severity == "warning":
            icon = "⚠️"
            warnings += 1
        else:
            icon = "❌"
            failed += 1
        
        lines.append(f"║ {icon} {check.name:18} │ {check.message[:45]:<45} ║")
    
    lines.append("╠" + "═" * 70 + "╣")
    
    status_line = f"║ Passed: {passed} │ Warnings: {warnings} │ Failed: {failed}"
    lines.append(status_line.ljust(71) + "║")
    
    if failed == 0 and warnings == 0:
        lines.append("║ 🚀 All checks passed! Ready for deployment.".ljust(71) + "║")
    elif failed == 0:
        lines.append("║ ⚠️  Minor issues detected. Review warnings before deploying.".ljust(71) + "║")
    else:
        lines.append("║ ❌ Critical issues found. Fix errors before deploying.".ljust(71) + "║")
    
    lines.append("╚" + "═" * 70 + "╝")
    
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════
# STEP 4 ENHANCEMENTS: COMPILE VERIFICATION, STATS, TOC
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class CompilationStats:
    """Statistics for a compiled product."""
    total_chapters: int
    total_words: int
    total_pages: int  # Estimated
    total_images: int
    reading_time_mins: int
    pdf_size_mb: float
    zip_size_mb: float
    complexity_score: int  # 1-10
    has_pdf: bool
    has_audio: bool
    has_video: bool
    has_bonuses: bool


@dataclass
class CompileVerification:
    """Verification result for compilation."""
    name: str
    passed: bool
    message: str
    severity: str  # "error", "warning", "info"


def analyze_compiled_content(product_dir: Path) -> Optional[CompilationStats]:
    """Analyze a compiled product and gather statistics."""
    import json
    import re
    
    output_dir = product_dir / "output"
    responses_dir = output_dir / "responses"
    
    if not output_dir.exists():
        return None
    
    # Count chapters
    chapter_files = list(responses_dir.glob("*.response.md")) if responses_dir.exists() else []
    total_chapters = len(chapter_files)
    
    # Count words
    total_words = 0
    for chapter in chapter_files:
        content = chapter.read_text()
        words = len(content.split())
        total_words += words
    
    # Estimate pages (250 words per page)
    total_pages = max(1, total_words // 250)
    
    # Count images
    images_dir = output_dir / "images"
    total_images = len(list(images_dir.glob("*.png"))) + len(list(images_dir.glob("*.jpg"))) if images_dir.exists() else 0
    
    # Reading time (200 WPM average)
    reading_time_mins = max(1, total_words // 200)
    
    # PDF size
    pdf_files = list(output_dir.glob("*.pdf"))
    pdf_size_mb = pdf_files[0].stat().st_size / (1024 * 1024) if pdf_files else 0
    
    # ZIP size
    zip_files = list(output_dir.glob("*.zip"))
    zip_size_mb = zip_files[0].stat().st_size / (1024 * 1024) if zip_files else 0
    
    # Check for audio/video/bonuses
    audio_dir = output_dir / "audio"
    video_dir = output_dir / "video"
    bonus_dir = output_dir / "bonuses"
    
    has_audio = audio_dir.exists() and any(audio_dir.glob("*.mp3"))
    has_video = video_dir.exists() and any(video_dir.glob("*.mp4"))
    has_bonuses = bonus_dir.exists() and any(bonus_dir.iterdir())
    has_pdf = len(pdf_files) > 0
    
    # Complexity score based on content
    complexity = 5  # Base
    if total_words > 20000:
        complexity += 2
    if total_images > 10:
        complexity += 1
    if has_audio:
        complexity += 1
    if has_video:
        complexity += 1
    complexity = min(10, complexity)
    
    return CompilationStats(
        total_chapters=total_chapters,
        total_words=total_words,
        total_pages=total_pages,
        total_images=total_images,
        reading_time_mins=reading_time_mins,
        pdf_size_mb=pdf_size_mb,
        zip_size_mb=zip_size_mb,
        complexity_score=complexity,
        has_pdf=has_pdf,
        has_audio=has_audio,
        has_video=has_video,
        has_bonuses=has_bonuses
    )


def format_compilation_stats(stats: CompilationStats) -> str:
    """Format compilation stats for display."""
    lines = [
        "",
        "╔" + "═" * 60 + "╗",
        "║" + " " * 18 + "COMPILATION STATS" + " " * 25 + "║",
        "╠" + "═" * 60 + "╣",
        f"║ 📚 Chapters: {stats.total_chapters}".ljust(61) + "║",
        f"║ 📝 Words: {stats.total_words:,}".ljust(61) + "║",
        f"║ 📄 Pages (est): {stats.total_pages}".ljust(61) + "║",
        f"║ 🖼️  Images: {stats.total_images}".ljust(61) + "║",
        f"║ ⏱️  Reading Time: ~{stats.reading_time_mins} minutes".ljust(61) + "║",
        "╠" + "─" * 60 + "╣",
    ]
    
    # File sizes
    if stats.pdf_size_mb > 0:
        lines.append(f"║ 📄 PDF Size: {stats.pdf_size_mb:.1f} MB".ljust(61) + "║")
    if stats.zip_size_mb > 0:
        lines.append(f"║ 📦 ZIP Size: {stats.zip_size_mb:.1f} MB".ljust(61) + "║")
    
    # Content flags
    content_flags = []
    if stats.has_pdf:
        content_flags.append("PDF")
    if stats.has_audio:
        content_flags.append("Audio")
    if stats.has_video:
        content_flags.append("Video")
    if stats.has_bonuses:
        content_flags.append("Bonuses")
    
    lines.append(f"║ 📋 Contains: {', '.join(content_flags)}".ljust(61) + "║")
    lines.append(f"║ 🎯 Complexity: {'⭐' * stats.complexity_score}{'☆' * (10 - stats.complexity_score)}".ljust(61) + "║")
    
    lines.append("╚" + "═" * 60 + "╝")
    return "\n".join(lines)


def verify_compilation(product_dir: Path) -> List[CompileVerification]:
    """Verify compilation integrity."""
    import json
    
    checks = []
    output_dir = product_dir / "output"
    responses_dir = output_dir / "responses"
    
    # 1. Check responses directory exists
    if responses_dir.exists():
        response_files = list(responses_dir.glob("*.response.md"))
        if len(response_files) > 0:
            checks.append(CompileVerification(
                "Response Files", True,
                f"Found {len(response_files)} chapters",
                "info"
            ))
        else:
            checks.append(CompileVerification(
                "Response Files", False,
                "No response files found",
                "error"
            ))
    else:
        checks.append(CompileVerification(
            "Response Files", False,
            "responses/ directory not found",
            "error"
        ))
    
    # 2. Check for empty chapters
    empty_chapters = []
    if responses_dir.exists():
        for resp in responses_dir.glob("*.response.md"):
            content = resp.read_text().strip()
            if len(content) < 100:
                empty_chapters.append(resp.name)
    
    if empty_chapters:
        checks.append(CompileVerification(
            "Chapter Content", False,
            f"Empty chapters: {', '.join(empty_chapters[:3])}",
            "warning"
        ))
    else:
        checks.append(CompileVerification(
            "Chapter Content", True,
            "All chapters have content",
            "info"
        ))
    
    # 3. Check PDF exists
    pdf_files = list(output_dir.glob("*.pdf")) if output_dir.exists() else []
    if pdf_files:
        size_mb = pdf_files[0].stat().st_size / (1024 * 1024)
        if size_mb < 0.1:
            checks.append(CompileVerification(
                "PDF Output", False,
                f"PDF too small: {size_mb:.2f}MB",
                "warning"
            ))
        elif size_mb > 50:
            checks.append(CompileVerification(
                "PDF Output", True,
                f"PDF large: {size_mb:.1f}MB (consider optimizing)",
                "warning"
            ))
        else:
            checks.append(CompileVerification(
                "PDF Output", True,
                f"PDF created: {size_mb:.1f}MB",
                "info"
            ))
    else:
        checks.append(CompileVerification(
            "PDF Output", False,
            "No PDF file found",
            "error"
        ))
    
    # 4. Check ZIP exists
    zip_files = list(output_dir.glob("*.zip")) if output_dir.exists() else []
    if zip_files:
        size_mb = zip_files[0].stat().st_size / (1024 * 1024)
        checks.append(CompileVerification(
            "ZIP Package", True,
            f"ZIP created: {size_mb:.1f}MB",
            "info"
        ))
    else:
        checks.append(CompileVerification(
            "ZIP Package", False,
            "No ZIP file found (run compile first)",
            "warning"
        ))
    
    # 5. Check images
    images_dir = output_dir / "images"
    if images_dir.exists():
        img_count = len(list(images_dir.glob("*.png"))) + len(list(images_dir.glob("*.jpg")))
        if img_count > 0:
            checks.append(CompileVerification(
                "Images", True,
                f"Found {img_count} images",
                "info"
            ))
        else:
            checks.append(CompileVerification(
                "Images", False,
                "No images in output/images/",
                "warning"
            ))
    
    # 6. Word count check
    total_words = 0
    if responses_dir.exists():
        for resp in responses_dir.glob("*.response.md"):
            total_words += len(resp.read_text().split())
    
    if total_words < 5000:
        checks.append(CompileVerification(
            "Word Count", False,
            f"Low word count: {total_words:,} (consider adding content)",
            "warning"
        ))
    else:
        checks.append(CompileVerification(
            "Word Count", True,
            f"Total: {total_words:,} words",
            "info"
        ))
    
    return checks


def format_compile_verification(checks: List[CompileVerification]) -> str:
    """Format verification results for display."""
    lines = [
        "",
        "╔" + "═" * 65 + "╗",
        "║" + " " * 20 + "COMPILE VERIFICATION" + " " * 25 + "║",
        "╠" + "═" * 65 + "╣",
    ]
    
    passed = 0
    failed = 0
    warnings = 0
    
    for check in checks:
        if check.passed:
            icon = "✅"
            passed += 1
        elif check.severity == "warning":
            icon = "⚠️"
            warnings += 1
        else:
            icon = "❌"
            failed += 1
        
        lines.append(f"║ {icon} {check.name:18} │ {check.message[:40]:<40} ║")
    
    lines.append("╠" + "═" * 65 + "╣")
    
    status_line = f"║ Passed: {passed} │ Warnings: {warnings} │ Failed: {failed}"
    lines.append(status_line.ljust(66) + "║")
    
    if failed == 0:
        lines.append("║ ✅ Compilation verified! Ready to package.".ljust(66) + "║")
    else:
        lines.append("║ ❌ Compilation issues found. Review errors above.".ljust(66) + "║")
    
    lines.append("╚" + "═" * 65 + "╝")
    
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════
# TABLE OF CONTENTS GENERATOR
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class TOCEntry:
    """A table of contents entry."""
    title: str
    page: int
    level: int  # 1 = chapter, 2 = section
    slug: str


def extract_toc_from_responses(product_dir: Path) -> List[TOCEntry]:
    """Extract table of contents from response files."""
    import re
    
    responses_dir = product_dir / "output" / "responses"
    
    if not responses_dir.exists():
        return []
    
    entries = []
    page = 1
    
    for idx, resp_file in enumerate(sorted(responses_dir.glob("*.response.md")), 1):
        content = resp_file.read_text()
        slug = resp_file.stem.replace(".response", "")
        
        # Extract chapter title from first heading
        lines = content.split('\n')
        title = slug.replace("_", " ").title()
        
        for line in lines[:10]:
            if line.startswith("# "):
                title = line[2:].strip()
                break
            elif line.startswith("## "):
                title = line[3:].strip()
                break
        
        entries.append(TOCEntry(
            title=title,
            page=page,
            level=1,
            slug=slug
        ))
        
        # Estimate pages for this chapter (250 words/page)
        words = len(content.split())
        pages = max(1, words // 250)
        page += pages
        
        # Extract sections (## headings)
        for line in lines:
            if line.startswith("## "):
                section_title = line[3:].strip()
                if section_title and len(section_title) < 80:
                    entries.append(TOCEntry(
                        title=section_title,
                        page=page - pages + 1,
                        level=2,
                        slug=f"{slug}_{section_title.lower().replace(' ', '-')[:20]}"
                    ))
    
    return entries


def format_toc(entries: List[TOCEntry], include_sections: bool = True) -> str:
    """Format table of contents for display/output."""
    lines = [
        "",
        "═" * 60,
        "TABLE OF CONTENTS".center(60),
        "═" * 60,
        "",
    ]
    
    for entry in entries:
        if entry.level == 1:
            # Chapter
            title_part = entry.title[:45]
            page_part = str(entry.page)
            dots = "." * (55 - len(title_part) - len(page_part))
            lines.append(f"{title_part}{dots}{page_part}")
        elif entry.level == 2 and include_sections:
            # Section (indented)
            title_part = f"  {entry.title[:40]}"
            page_part = str(entry.page)
            dots = "." * (55 - len(title_part) - len(page_part))
            lines.append(f"{title_part}{dots}{page_part}")
    
    lines.append("")
    lines.append("═" * 60)
    
    return "\n".join(lines)


def generate_toc_markdown(entries: List[TOCEntry], product_title: str) -> str:
    """Generate markdown TOC for inclusion in PDF."""
    lines = [
        f"# {product_title}",
        "",
        "## Table of Contents",
        "",
    ]
    
    for entry in entries:
        if entry.level == 1:
            lines.append(f"- **[{entry.title}](#{entry.slug})** — Page {entry.page}")
        elif entry.level == 2:
            lines.append(f"  - [{entry.title}](#{entry.slug})")
    
    lines.append("")
    lines.append("---")
    lines.append("")
    
    return "\n".join(lines)


def save_toc_to_file(product_dir: Path, entries: List[TOCEntry], product_title: str) -> Tuple[bool, str]:
    """Save TOC to output directory."""
    output_dir = product_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save as markdown
    md_content = generate_toc_markdown(entries, product_title)
    md_file = output_dir / "table_of_contents.md"
    md_file.write_text(md_content)
    
    # Save as plain text
    txt_content = format_toc(entries)
    txt_file = output_dir / "table_of_contents.txt"
    txt_file.write_text(txt_content)
    
    return True, f"Saved TOC to {md_file} and {txt_file}"


# ═══════════════════════════════════════════════════════════════════════
# STEP 5 ENHANCEMENTS: DRY-RUN, VERIFICATION, HISTORY
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class DeploymentRecord:
    """Record of a deployment."""
    slug: str
    timestamp: str
    version: int
    zip_path: str
    image_path: str
    sql_path: str
    success: bool
    error: Optional[str] = None


@dataclass
class DeployDryRun:
    """Dry-run deployment preview."""
    slug: str
    zip_source: str
    zip_dest: str
    image_source: str
    image_dest: str
    sql_statements: str
    product_url: str
    download_url: str


def dry_run_deploy(product_dir: Path, salarsu_path: Path = None) -> Tuple[bool, DeployDryRun]:
    """Preview deployment without making changes."""
    import json
    
    if salarsu_path is None:
        salarsu_path = Path.home() / "Projects" / "salarsu"
    
    config_file = product_dir / "product.json"
    if not config_file.exists():
        return False, None
    
    config = json.loads(config_file.read_text())
    slug = config.get("slug") or generate_product_slug(config.get("title", "product"))
    
    output_dir = product_dir / "output"
    
    # Find source files
    zip_source = None
    for zip_file in output_dir.glob("*.zip"):
        zip_source = str(zip_file)
        break
    
    image_source = None
    for img in ["cover.png", "cover.jpg", "product.png"]:
        img_path = output_dir / "images" / img
        if img_path.exists():
            image_source = str(img_path)
            break
    
    # Destination paths
    zip_dest = str(salarsu_path / "public" / "downloads" / "products" / f"{slug}.zip")
    image_dest = str(salarsu_path / "public" / "images" / "products" / f"{slug}.png")
    
    # SQL preview
    sql_file = output_dir / "store_insert.sql"
    sql_statements = sql_file.read_text() if sql_file.exists() else "No SQL file found"
    
    dry_run = DeployDryRun(
        slug=slug,
        zip_source=zip_source or "No ZIP found",
        zip_dest=zip_dest,
        image_source=image_source or "No image found",
        image_dest=image_dest,
        sql_statements=sql_statements[:500] + "..." if len(sql_statements) > 500 else sql_statements,
        product_url=f"https://salars.net/digital/{slug}",
        download_url=f"https://salars.net/downloads/products/{slug}.zip"
    )
    
    return True, dry_run


def format_dry_run(dry_run: DeployDryRun) -> str:
    """Format dry-run preview for display."""
    lines = [
        "",
        "╔" + "═" * 70 + "╗",
        "║" + " " * 22 + "DEPLOYMENT DRY RUN" + " " * 30 + "║",
        "╠" + "═" * 70 + "╣",
        f"║ 🏷️  Slug: {dry_run.slug[:55]}".ljust(71) + "║",
        "╠" + "─" * 70 + "╣",
        "║ 📦 ZIP Transfer:".ljust(71) + "║",
        f"║   From: {dry_run.zip_source[:58]}".ljust(71) + "║",
        f"║   To:   {dry_run.zip_dest[:58]}".ljust(71) + "║",
        "╠" + "─" * 70 + "╣",
        "║ 🖼️  Image Transfer:".ljust(71) + "║",
        f"║   From: {dry_run.image_source[:58]}".ljust(71) + "║",
        f"║   To:   {dry_run.image_dest[:58]}".ljust(71) + "║",
        "╠" + "─" * 70 + "╣",
        "║ 🔗 URLs:".ljust(71) + "║",
        f"║   Product: {dry_run.product_url[:55]}".ljust(71) + "║",
        f"║   Download: {dry_run.download_url[:54]}".ljust(71) + "║",
        "╠" + "─" * 70 + "╣",
        "║ 📝 SQL Preview:".ljust(71) + "║",
    ]
    
    for sql_line in dry_run.sql_statements.split('\n')[:5]:
        lines.append(f"║   {sql_line[:65]}".ljust(71) + "║")
    
    lines.append("╠" + "═" * 70 + "╣")
    lines.append("║ ⚠️  DRY RUN - No changes made. Use without --dry-run to deploy.".ljust(71) + "║")
    lines.append("╚" + "═" * 70 + "╝")
    
    return "\n".join(lines)


@dataclass
class DeployVerification:
    """Verification of a deployment."""
    name: str
    passed: bool
    message: str
    severity: str


def verify_deployment(slug: str, salarsu_path: Path = None) -> List[DeployVerification]:
    """Verify a deployment was successful."""
    import subprocess
    
    if salarsu_path is None:
        salarsu_path = Path.home() / "Projects" / "salarsu"
    
    checks = []
    
    # 1. Check ZIP file exists locally
    zip_path = salarsu_path / "public" / "downloads" / "products" / f"{slug}.zip"
    if zip_path.exists():
        size_mb = zip_path.stat().st_size / (1024 * 1024)
        checks.append(DeployVerification(
            "ZIP File", True,
            f"Found: {size_mb:.1f}MB",
            "info"
        ))
    else:
        checks.append(DeployVerification(
            "ZIP File", False,
            f"Not found: {zip_path.name}",
            "error"
        ))
    
    # 2. Check image exists locally
    image_path = salarsu_path / "public" / "images" / "products" / f"{slug}.png"
    if not image_path.exists():
        image_path = salarsu_path / "public" / "images" / "products" / f"{slug}.jpg"
    
    if image_path.exists():
        checks.append(DeployVerification(
            "Cover Image", True,
            f"Found: {image_path.name}",
            "info"
        ))
    else:
        checks.append(DeployVerification(
            "Cover Image", False,
            f"Not found: {slug}.png/jpg",
            "warning"
        ))
    
    # 3. Check SQL seed file exists
    sql_path = salarsu_path / "db" / "seeds" / f"digital_{slug}.sql"
    if sql_path.exists():
        checks.append(DeployVerification(
            "SQL Seed", True,
            f"Found: digital_{slug}.sql",
            "info"
        ))
    else:
        checks.append(DeployVerification(
            "SQL Seed", False,
            "SQL seed file not found",
            "warning"
        ))
    
    # 4. Try to reach product URL (if curl available)
    product_url = f"https://salars.net/digital/{slug}"
    try:
        result = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", product_url],
            capture_output=True,
            timeout=10
        )
        status_code = result.stdout.decode().strip()
        if status_code == "200":
            checks.append(DeployVerification(
                "Product Page", True,
                f"Accessible (HTTP {status_code})",
                "info"
            ))
        elif status_code == "404":
            checks.append(DeployVerification(
                "Product Page", False,
                f"Not found (HTTP {status_code})",
                "warning"
            ))
        else:
            checks.append(DeployVerification(
                "Product Page", True,
                f"HTTP {status_code}",
                "info"
            ))
    except:
        checks.append(DeployVerification(
            "Product Page", True,
            "Could not verify (curl unavailable)",
            "info"
        ))
    
    # 5. Check deployment history
    history_file = salarsu_path / ".deployment_history" / f"{slug}.json"
    if history_file.exists():
        checks.append(DeployVerification(
            "Deployment Record", True,
            "History recorded",
            "info"
        ))
    else:
        checks.append(DeployVerification(
            "Deployment Record", False,
            "No deployment history",
            "warning"
        ))
    
    return checks


def format_deploy_verification(checks: List[DeployVerification]) -> str:
    """Format verification results."""
    lines = [
        "",
        "╔" + "═" * 60 + "╗",
        "║" + " " * 17 + "DEPLOY VERIFICATION" + " " * 24 + "║",
        "╠" + "═" * 60 + "╣",
    ]
    
    passed = 0
    failed = 0
    
    for check in checks:
        if check.passed:
            icon = "✅"
            passed += 1
        else:
            icon = "❌" if check.severity == "error" else "⚠️"
            failed += 1
        
        lines.append(f"║ {icon} {check.name:18} │ {check.message[:35]:<35} ║")
    
    lines.append("╠" + "═" * 60 + "╣")
    
    if failed == 0:
        lines.append("║ ✅ Deployment verified successfully!".ljust(61) + "║")
    else:
        lines.append("║ ⚠️  Some checks failed. Review issues above.".ljust(61) + "║")
    
    lines.append("╚" + "═" * 60 + "╝")
    
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════
# DEPLOYMENT HISTORY
# ═══════════════════════════════════════════════════════════════════════


def record_deployment(
    slug: str,
    zip_path: str,
    image_path: str,
    sql_path: str,
    success: bool,
    error: str = None,
    salarsu_path: Path = None
) -> DeploymentRecord:
    """Record a deployment in history."""
    import json
    from datetime import datetime
    
    if salarsu_path is None:
        salarsu_path = Path.home() / "Projects" / "salarsu"
    
    history_dir = salarsu_path / ".deployment_history"
    history_dir.mkdir(parents=True, exist_ok=True)
    
    history_file = history_dir / f"{slug}.json"
    
    # Load existing history
    if history_file.exists():
        history = json.loads(history_file.read_text())
    else:
        history = {"slug": slug, "deployments": []}
    
    # Create new record
    version = len(history["deployments"]) + 1
    timestamp = datetime.now().isoformat()
    
    record = DeploymentRecord(
        slug=slug,
        timestamp=timestamp,
        version=version,
        zip_path=zip_path,
        image_path=image_path,
        sql_path=sql_path,
        success=success,
        error=error
    )
    
    # Add to history
    history["deployments"].append({
        "timestamp": timestamp,
        "version": version,
        "zip_path": zip_path,
        "image_path": image_path,
        "sql_path": sql_path,
        "success": success,
        "error": error
    })
    
    # Save
    history_file.write_text(json.dumps(history, indent=2))
    
    return record


def load_deployment_history(slug: str, salarsu_path: Path = None) -> List[DeploymentRecord]:
    """Load deployment history for a product."""
    import json
    
    if salarsu_path is None:
        salarsu_path = Path.home() / "Projects" / "salarsu"
    
    history_file = salarsu_path / ".deployment_history" / f"{slug}.json"
    
    if not history_file.exists():
        return []
    
    history = json.loads(history_file.read_text())
    
    return [
        DeploymentRecord(
            slug=slug,
            timestamp=d["timestamp"],
            version=d["version"],
            zip_path=d["zip_path"],
            image_path=d["image_path"],
            sql_path=d["sql_path"],
            success=d["success"],
            error=d.get("error")
        )
        for d in history.get("deployments", [])
    ]


def format_deployment_history(records: List[DeploymentRecord]) -> str:
    """Format deployment history for display."""
    if not records:
        return "\n  No deployment history found.\n"
    
    lines = [
        "",
        "╔" + "═" * 70 + "╗",
        "║" + " " * 22 + "DEPLOYMENT HISTORY" + " " * 30 + "║",
        f"║ Product: {records[0].slug}".ljust(71) + "║",
        "╠" + "═" * 70 + "╣",
        "║ {:5} │ {:20} │ {:8} │ {:25} ║".format("Ver", "Timestamp", "Status", "Notes"),
        "╠" + "─" * 70 + "╣",
    ]
    
    for record in reversed(records[-10:]):  # Last 10 deployments
        status = "✅ OK" if record.success else "❌ FAIL"
        ts_short = record.timestamp[:19].replace("T", " ")
        notes = record.error[:20] if record.error else "Deployed"
        lines.append("║ {:5} │ {:20} │ {:8} │ {:25} ║".format(
            f"v{record.version}", ts_short, status, notes
        ))
    
    lines.append("╠" + "═" * 70 + "╣")
    lines.append(f"║ Total deployments: {len(records)}".ljust(71) + "║")
    lines.append("╚" + "═" * 70 + "╝")
    
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════
# STEP 6 ENHANCEMENTS: MARKETING TEMPLATES, UTM, PREVIEW
# ═══════════════════════════════════════════════════════════════════════


MARKETING_TEMPLATES = {
    "launch-week": {
        "name": "Launch Week",
        "description": "7-day intensive launch campaign",
        "emails": ["teaser", "launch", "reminder", "last-chance", "closed"],
        "social_posts_per_day": 3,
        "platforms": ["twitter", "linkedin", "instagram"],
        "duration_days": 7,
    },
    "evergreen": {
        "name": "Evergreen",
        "description": "Ongoing promotional content",
        "emails": ["welcome", "value-1", "value-2", "offer"],
        "social_posts_per_day": 1,
        "platforms": ["twitter", "linkedin"],
        "duration_days": 30,
    },
    "flash-sale": {
        "name": "Flash Sale",
        "description": "24-48 hour urgency campaign",
        "emails": ["announcement", "reminder", "final-hours"],
        "social_posts_per_day": 5,
        "platforms": ["twitter", "instagram"],
        "duration_days": 2,
    },
    "testimonial": {
        "name": "Testimonial",
        "description": "Social proof focused campaign",
        "emails": ["story-1", "story-2", "results"],
        "social_posts_per_day": 2,
        "platforms": ["linkedin", "instagram"],
        "duration_days": 14,
    },
    "educational": {
        "name": "Educational",
        "description": "Value-first content marketing",
        "emails": ["lesson-1", "lesson-2", "lesson-3", "offer"],
        "social_posts_per_day": 2,
        "platforms": ["twitter", "linkedin"],
        "duration_days": 7,
    },
}


@dataclass
class MarketingTemplate:
    """A marketing template with campaign details."""
    name: str
    description: str
    emails: List[str]
    social_posts_per_day: int
    platforms: List[str]
    duration_days: int


def list_marketing_templates() -> Dict[str, MarketingTemplate]:
    """List available marketing templates."""
    return {
        key: MarketingTemplate(
            name=val["name"],
            description=val["description"],
            emails=val["emails"],
            social_posts_per_day=val["social_posts_per_day"],
            platforms=val["platforms"],
            duration_days=val["duration_days"],
        )
        for key, val in MARKETING_TEMPLATES.items()
    }


def format_marketing_templates() -> str:
    """Format marketing templates for display."""
    lines = [
        "",
        "╔" + "═" * 75 + "╗",
        "║" + " " * 25 + "MARKETING TEMPLATES" + " " * 31 + "║",
        "╠" + "═" * 75 + "╣",
        "║ {:15} │ {:30} │ {:8} │ {:12} ║".format("Template", "Description", "Duration", "Posts/Day"),
        "╠" + "─" * 75 + "╣",
    ]
    
    for key, template in MARKETING_TEMPLATES.items():
        lines.append("║ {:15} │ {:30} │ {:8} │ {:12} ║".format(
            key,
            template["description"][:30],
            f"{template['duration_days']} days",
            str(template["social_posts_per_day"])
        ))
    
    lines.append("╠" + "═" * 75 + "╣")
    lines.append("║ Usage: product-builder marketing --template <name>".ljust(76) + "║")
    lines.append("╚" + "═" * 75 + "╝")
    
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════
# UTM LINK GENERATOR
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class UTMLinks:
    """Generated UTM links for a product."""
    product_slug: str
    campaign: str
    base_url: str
    product_link: str
    twitter_link: str
    linkedin_link: str
    instagram_link: str
    email_link: str
    newsletter_link: str


def generate_utm_links(
    slug: str,
    campaign: str = None,
    base_url: str = "https://salars.net"
) -> UTMLinks:
    """Generate UTM-tagged links for all channels."""
    from urllib.parse import urlencode
    
    if campaign is None:
        from datetime import datetime
        campaign = f"launch-{datetime.now().strftime('%b%Y').lower()}"
    
    product_path = f"/digital/{slug}"
    
    def make_utm(source: str, medium: str) -> str:
        params = urlencode({
            "utm_source": source,
            "utm_medium": medium,
            "utm_campaign": campaign,
            "utm_content": slug,
        })
        return f"{base_url}{product_path}?{params}"
    
    return UTMLinks(
        product_slug=slug,
        campaign=campaign,
        base_url=base_url,
        product_link=f"{base_url}{product_path}",
        twitter_link=make_utm("twitter", "social"),
        linkedin_link=make_utm("linkedin", "social"),
        instagram_link=make_utm("instagram", "social"),
        email_link=make_utm("email", "email"),
        newsletter_link=make_utm("newsletter", "email"),
    )


def format_utm_links(links: UTMLinks) -> str:
    """Format UTM links for display."""
    lines = [
        "",
        "╔" + "═" * 80 + "╗",
        "║" + " " * 30 + "UTM LINKS" + " " * 41 + "║",
        "╠" + "═" * 80 + "╣",
        f"║ 🏷️  Product: {links.product_slug}".ljust(81) + "║",
        f"║ 📊 Campaign: {links.campaign}".ljust(81) + "║",
        "╠" + "─" * 80 + "╣",
        "║ 🔗 Direct Link:".ljust(81) + "║",
        f"║    {links.product_link[:75]}".ljust(81) + "║",
        "╠" + "─" * 80 + "╣",
        "║ 📱 Social Media:".ljust(81) + "║",
        f"║    Twitter:   {links.twitter_link[:60]}".ljust(81) + "║",
        f"║    LinkedIn:  {links.linkedin_link[:60]}".ljust(81) + "║",
        f"║    Instagram: {links.instagram_link[:60]}".ljust(81) + "║",
        "╠" + "─" * 80 + "╣",
        "║ 📧 Email:".ljust(81) + "║",
        f"║    Email:      {links.email_link[:60]}".ljust(81) + "║",
        f"║    Newsletter: {links.newsletter_link[:60]}".ljust(81) + "║",
        "╚" + "═" * 80 + "╝",
    ]
    
    return "\n".join(lines)


def export_utm_links(links: UTMLinks, output_dir: Path) -> Tuple[bool, str]:
    """Export UTM links to file."""
    import json
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Export as JSON
    json_file = output_dir / "utm_links.json"
    json_file.write_text(json.dumps({
        "product_slug": links.product_slug,
        "campaign": links.campaign,
        "links": {
            "direct": links.product_link,
            "twitter": links.twitter_link,
            "linkedin": links.linkedin_link,
            "instagram": links.instagram_link,
            "email": links.email_link,
            "newsletter": links.newsletter_link,
        }
    }, indent=2))
    
    # Export as markdown
    md_file = output_dir / "utm_links.md"
    md_content = f"""# UTM Links: {links.product_slug}

**Campaign:** {links.campaign}

## Social Media

- **Twitter:** {links.twitter_link}
- **LinkedIn:** {links.linkedin_link}  
- **Instagram:** {links.instagram_link}

## Email

- **Email Campaign:** {links.email_link}
- **Newsletter:** {links.newsletter_link}

## Direct

- **Product Page:** {links.product_link}
"""
    md_file.write_text(md_content)
    
    return True, f"Exported UTM links to {json_file} and {md_file}"


# ═══════════════════════════════════════════════════════════════════════
# CONTENT PREVIEW
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class ContentCheck:
    """A content validation check."""
    name: str
    passed: bool
    message: str
    value: str


@dataclass
class ContentPreview:
    """Preview of marketing content with validation."""
    emails_count: int
    social_posts_count: int
    twitter_chars_avg: int
    linkedin_chars_avg: int
    subject_lines: List[str]
    checks: List[ContentCheck]


def preview_marketing_content(product_dir: Path) -> Optional[ContentPreview]:
    """Preview and validate marketing content."""
    output_dir = product_dir / "output"
    
    if not output_dir.exists():
        return None
    
    checks = []
    emails_count = 0
    social_posts_count = 0
    subject_lines = []
    twitter_chars = []
    linkedin_chars = []
    
    # Check email files
    for email_file in output_dir.glob("emails_*.md"):
        content = email_file.read_text()
        
        # Count emails (separated by ---)
        emails = content.split("---")
        emails_count += len([e for e in emails if e.strip()])
        
        # Extract subject lines
        for line in content.split('\n'):
            if line.startswith("Subject:") or line.startswith("**Subject:**"):
                subject = line.split(":", 1)[-1].strip()
                subject_lines.append(subject)
    
    # Check social content
    social_file = output_dir / "social_promo.md"
    if social_file.exists():
        content = social_file.read_text()
        
        # Parse posts
        posts = content.split("---")
        for post in posts:
            if "Twitter" in post or "X:" in post:
                text = post.split('\n')[-1].strip()
                if text:
                    twitter_chars.append(len(text))
                    social_posts_count += 1
            elif "LinkedIn" in post:
                text = post.split('\n')[-1].strip()
                if text:
                    linkedin_chars.append(len(text))
                    social_posts_count += 1
            elif post.strip():
                social_posts_count += 1
    
    # Validation checks
    
    # 1. Email subject line length
    long_subjects = [s for s in subject_lines if len(s) > 50]
    if long_subjects:
        checks.append(ContentCheck(
            "Email Subjects", False,
            f"{len(long_subjects)} subjects over 50 chars",
            str(len(long_subjects))
        ))
    elif subject_lines:
        checks.append(ContentCheck(
            "Email Subjects", True,
            f"All {len(subject_lines)} subjects under 50 chars",
            str(len(subject_lines))
        ))
    
    # 2. Twitter post length
    long_tweets = [c for c in twitter_chars if c > 280]
    if long_tweets:
        checks.append(ContentCheck(
            "Twitter Length", False,
            f"{len(long_tweets)} posts over 280 chars",
            str(len(long_tweets))
        ))
    elif twitter_chars:
        avg = sum(twitter_chars) // len(twitter_chars)
        checks.append(ContentCheck(
            "Twitter Length", True,
            f"Avg: {avg} chars (max 280)",
            str(avg)
        ))
    
    # 3. LinkedIn post length
    if linkedin_chars:
        avg = sum(linkedin_chars) // len(linkedin_chars)
        if avg < 100:
            checks.append(ContentCheck(
                "LinkedIn Length", False,
                f"Posts too short: avg {avg} chars",
                str(avg)
            ))
        else:
            checks.append(ContentCheck(
                "LinkedIn Length", True,
                f"Good length: avg {avg} chars",
                str(avg)
            ))
    
    # 4. Content quantity
    if emails_count < 3:
        checks.append(ContentCheck(
            "Email Quantity", False,
            f"Only {emails_count} emails (recommend 5+)",
            str(emails_count)
        ))
    else:
        checks.append(ContentCheck(
            "Email Quantity", True,
            f"{emails_count} emails ready",
            str(emails_count)
        ))
    
    if social_posts_count < 5:
        checks.append(ContentCheck(
            "Social Quantity", False,
            f"Only {social_posts_count} posts (recommend 10+)",
            str(social_posts_count)
        ))
    else:
        checks.append(ContentCheck(
            "Social Quantity", True,
            f"{social_posts_count} social posts ready",
            str(social_posts_count)
        ))
    
    return ContentPreview(
        emails_count=emails_count,
        social_posts_count=social_posts_count,
        twitter_chars_avg=sum(twitter_chars) // len(twitter_chars) if twitter_chars else 0,
        linkedin_chars_avg=sum(linkedin_chars) // len(linkedin_chars) if linkedin_chars else 0,
        subject_lines=subject_lines,
        checks=checks
    )


def format_content_preview(preview: ContentPreview) -> str:
    """Format content preview for display."""
    lines = [
        "",
        "╔" + "═" * 65 + "╗",
        "║" + " " * 20 + "MARKETING CONTENT PREVIEW" + " " * 20 + "║",
        "╠" + "═" * 65 + "╣",
        f"║ 📧 Emails: {preview.emails_count}".ljust(66) + "║",
        f"║ 📱 Social Posts: {preview.social_posts_count}".ljust(66) + "║",
    ]
    
    if preview.twitter_chars_avg > 0:
        lines.append(f"║ 🐦 Twitter Avg: {preview.twitter_chars_avg} chars".ljust(66) + "║")
    if preview.linkedin_chars_avg > 0:
        lines.append(f"║ 💼 LinkedIn Avg: {preview.linkedin_chars_avg} chars".ljust(66) + "║")
    
    lines.append("╠" + "─" * 65 + "╣")
    lines.append("║ 📝 Subject Lines:".ljust(66) + "║")
    
    for subject in preview.subject_lines[:5]:
        lines.append(f"║   • {subject[:55]}".ljust(66) + "║")
    
    if len(preview.subject_lines) > 5:
        lines.append(f"║   ... and {len(preview.subject_lines) - 5} more".ljust(66) + "║")
    
    lines.append("╠" + "═" * 65 + "╣")
    lines.append("║ VALIDATION CHECKS:".ljust(66) + "║")
    lines.append("╠" + "─" * 65 + "╣")
    
    passed = 0
    failed = 0
    
    for check in preview.checks:
        if check.passed:
            icon = "✅"
            passed += 1
        else:
            icon = "⚠️"
            failed += 1
        
        lines.append(f"║ {icon} {check.name:18} │ {check.message[:40]:<40} ║")
    
    lines.append("╠" + "═" * 65 + "╣")
    
    if failed == 0:
        lines.append("║ ✅ All content validated! Ready to publish.".ljust(66) + "║")
    else:
        lines.append(f"║ ⚠️  {failed} issues to review before publishing.".ljust(66) + "║")
    
    lines.append("╚" + "═" * 65 + "╝")
    
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════
# STEP 7 ENHANCEMENTS: SCHEDULE PREVIEW, REGISTRATION STATUS, COUNTDOWN
# ═══════════════════════════════════════════════════════════════════════


# Optimal posting times by platform (UTC)
OPTIMAL_POSTING_TIMES = {
    "twitter": ["09:00", "12:00", "17:00"],
    "linkedin": ["08:00", "12:00"],
    "instagram": ["11:00", "19:00"],
}


@dataclass
class ScheduledPost:
    """A scheduled social media post."""
    date: str
    time: str
    platform: str
    content_preview: str


@dataclass
class SchedulePreview:
    """Preview of scheduled posts."""
    launch_date: str
    total_posts: int
    posts_by_day: Dict[str, List[ScheduledPost]]
    platforms: List[str]


def generate_schedule_preview(
    product_dir: Path,
    launch_date: str,
    posts_per_day: int = 3,
    duration_days: int = 7
) -> Optional[SchedulePreview]:
    """Generate a preview of scheduled posts."""
    from datetime import datetime, timedelta
    
    output_dir = product_dir / "output"
    social_file = output_dir / "social_promo.md"
    
    if not social_file.exists():
        return None
    
    # Parse social content
    content = social_file.read_text()
    posts = [p.strip() for p in content.split("---") if p.strip()]
    
    # Generate schedule
    posts_by_day = {}
    platforms_used = set()
    
    try:
        launch = datetime.strptime(launch_date, "%Y-%m-%d")
    except:
        return None
    
    post_index = 0
    for day in range(duration_days):
        date = launch + timedelta(days=day)
        date_str = date.strftime("%Y-%m-%d")
        posts_by_day[date_str] = []
        
        for post_num in range(min(posts_per_day, len(posts) - post_index)):
            if post_index >= len(posts):
                break
            
            post_content = posts[post_index]
            
            # Detect platform
            if "Twitter" in post_content or "X:" in post_content:
                platform = "twitter"
            elif "LinkedIn" in post_content:
                platform = "linkedin"
            elif "Instagram" in post_content:
                platform = "instagram"
            else:
                platform = "twitter"
            
            platforms_used.add(platform)
            times = OPTIMAL_POSTING_TIMES.get(platform, ["12:00"])
            time = times[post_num % len(times)]
            
            # Get content preview
            lines = [l for l in post_content.split('\n') if l.strip() and not l.startswith('#')]
            preview = lines[-1][:50] + "..." if lines else "Post content"
            
            posts_by_day[date_str].append(ScheduledPost(
                date=date_str,
                time=time,
                platform=platform,
                content_preview=preview
            ))
            
            post_index += 1
    
    return SchedulePreview(
        launch_date=launch_date,
        total_posts=post_index,
        posts_by_day=posts_by_day,
        platforms=list(platforms_used)
    )


def format_schedule_preview(preview: SchedulePreview) -> str:
    """Format schedule preview for display."""
    lines = [
        "",
        "╔" + "═" * 75 + "╗",
        "║" + " " * 25 + "SCHEDULE PREVIEW" + " " * 34 + "║",
        "╠" + "═" * 75 + "╣",
        f"║ 🚀 Launch Date: {preview.launch_date}".ljust(76) + "║",
        f"║ 📱 Platforms: {', '.join(preview.platforms)}".ljust(76) + "║",
        f"║ 📊 Total Posts: {preview.total_posts}".ljust(76) + "║",
        "╠" + "═" * 75 + "╣",
    ]
    
    for date_str, day_posts in list(preview.posts_by_day.items())[:7]:
        if day_posts:
            lines.append(f"║ 📅 {date_str}:".ljust(76) + "║")
            for post in day_posts:
                icon = "🐦" if post.platform == "twitter" else "💼" if post.platform == "linkedin" else "📷"
                lines.append(f"║   {icon} {post.time} - {post.content_preview[:50]}".ljust(76) + "║")
            lines.append("╠" + "─" * 75 + "╣")
    
    lines.append("║ 💡 Use --launch-date YYYY-MM-DD to schedule for real".ljust(76) + "║")
    lines.append("╚" + "═" * 75 + "╝")
    
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════
# REGISTRATION STATUS
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class RegistrationItem:
    """A registered item (email or post)."""
    item_type: str
    name: str
    status: str
    scheduled_time: Optional[str] = None


@dataclass
class RegistrationStatus:
    """Status of registered emails and posts."""
    slug: str
    emails_registered: int
    posts_scheduled: int
    items: List[RegistrationItem]
    next_scheduled: Optional[str]


def check_registration_status(slug: str, salarsu_path: Path = None) -> RegistrationStatus:
    """Check registration status for a product."""
    if salarsu_path is None:
        salarsu_path = Path.home() / "Projects" / "salarsu"
    
    items = []
    emails_registered = 0
    posts_scheduled = 0
    next_scheduled = None
    
    # Check for email registration markers
    email_marker = salarsu_path / ".email_registry" / f"{slug}.json"
    if email_marker.exists():
        import json
        try:
            data = json.loads(email_marker.read_text())
            emails_registered = data.get("count", 0)
            for email in data.get("emails", []):
                items.append(RegistrationItem(
                    item_type="email",
                    name=email.get("name", "Email"),
                    status="registered"
                ))
        except:
            pass
    
    # Check for Buffer schedule markers
    buffer_marker = salarsu_path / ".buffer_schedule" / f"{slug}.json"
    if buffer_marker.exists():
        import json
        try:
            data = json.loads(buffer_marker.read_text())
            posts_scheduled = data.get("count", 0)
            for post in data.get("posts", [])[:5]:
                items.append(RegistrationItem(
                    item_type="social",
                    name=post.get("platform", "Social"),
                    status="scheduled",
                    scheduled_time=post.get("time")
                ))
            next_scheduled = data.get("next_scheduled")
        except:
            pass
    
    # If no markers, check output files
    if not items:
        output_dir = salarsu_path.parent / "dreamweaving" / "products" / slug / "output"
        
        if (output_dir / "emails_welcome.md").exists():
            items.append(RegistrationItem("email", "Welcome Sequence", "generated"))
        if (output_dir / "emails_launch.md").exists():
            items.append(RegistrationItem("email", "Launch Sequence", "generated"))
        if (output_dir / "social_promo.md").exists():
            items.append(RegistrationItem("social", "Social Package", "generated"))
    
    return RegistrationStatus(
        slug=slug,
        emails_registered=emails_registered,
        posts_scheduled=posts_scheduled,
        items=items,
        next_scheduled=next_scheduled
    )


def format_registration_status(status: RegistrationStatus) -> str:
    """Format registration status for display."""
    lines = [
        "",
        "╔" + "═" * 60 + "╗",
        "║" + " " * 17 + "REGISTRATION STATUS" + " " * 24 + "║",
        "╠" + "═" * 60 + "╣",
        f"║ 🏷️  Product: {status.slug}".ljust(61) + "║",
        f"║ 📧 Emails Registered: {status.emails_registered}".ljust(61) + "║",
        f"║ 📱 Posts Scheduled: {status.posts_scheduled}".ljust(61) + "║",
    ]
    
    if status.next_scheduled:
        lines.append(f"║ ⏰ Next Post: {status.next_scheduled}".ljust(61) + "║")
    
    lines.append("╠" + "─" * 60 + "╣")
    
    if status.items:
        for item in status.items[:8]:
            icon = "📧" if item.item_type == "email" else "📱"
            status_icon = "✅" if item.status in ["registered", "scheduled"] else "⏳"
            time_str = f" @ {item.scheduled_time}" if item.scheduled_time else ""
            lines.append(f"║ {icon} {status_icon} {item.name:25} │ {item.status}{time_str}".ljust(61) + "║")
    else:
        lines.append("║ ⚠️  No registrations found.".ljust(61) + "║")
        lines.append("║    Run with --register-emails or --schedule-buffer".ljust(61) + "║")
    
    lines.append("╚" + "═" * 60 + "╝")
    
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════
# LAUNCH COUNTDOWN
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class LaunchCheckItem:
    """A launch checklist item."""
    name: str
    completed: bool
    category: str


@dataclass
class LaunchCountdown:
    """Launch countdown with checklist."""
    launch_date: str
    days_until: int
    hours_until: int
    checklist: List[LaunchCheckItem]
    ready_percentage: int


def generate_launch_countdown(product_dir: Path, launch_date: str) -> Optional[LaunchCountdown]:
    """Generate launch countdown with checklist."""
    from datetime import datetime
    
    output_dir = product_dir / "output"
    
    if not output_dir.exists():
        return None
    
    # Calculate time until launch
    try:
        launch = datetime.strptime(launch_date, "%Y-%m-%d")
        now = datetime.now()
        diff = launch - now
        days_until = diff.days
        hours_until = diff.seconds // 3600
    except:
        days_until = 0
        hours_until = 0
    
    checklist = []
    
    # Product checklist
    checklist.append(LaunchCheckItem(
        "Product PDF", 
        (output_dir / "product.pdf").exists() or any(output_dir.glob("*.pdf")),
        "Product"
    ))
    checklist.append(LaunchCheckItem(
        "Product ZIP",
        any(output_dir.glob("*.zip")),
        "Product"
    ))
    checklist.append(LaunchCheckItem(
        "Cover Image",
        (output_dir / "images").exists() and any((output_dir / "images").glob("*")),
        "Product"
    ))
    
    # Marketing checklist
    checklist.append(LaunchCheckItem(
        "Landing Page",
        (output_dir / "landing_page_content.json").exists(),
        "Marketing"
    ))
    checklist.append(LaunchCheckItem(
        "Email Sequences",
        any(output_dir.glob("emails_*.md")),
        "Marketing"
    ))
    checklist.append(LaunchCheckItem(
        "Social Posts",
        (output_dir / "social_promo.md").exists(),
        "Marketing"
    ))
    
    # Deployment checklist
    checklist.append(LaunchCheckItem(
        "SQL Export",
        (output_dir / "store_insert.sql").exists(),
        "Deployment"
    ))
    checklist.append(LaunchCheckItem(
        "SEO Metadata",
        (output_dir / "seo_metadata.json").exists(),
        "Deployment"
    ))
    checklist.append(LaunchCheckItem(
        "UTM Links",
        (output_dir / "utm_links.json").exists(),
        "Deployment"
    ))
    
    completed = sum(1 for item in checklist if item.completed)
    ready_percentage = int((completed / len(checklist)) * 100)
    
    return LaunchCountdown(
        launch_date=launch_date,
        days_until=days_until,
        hours_until=hours_until,
        checklist=checklist,
        ready_percentage=ready_percentage
    )


def format_launch_countdown(countdown: LaunchCountdown) -> str:
    """Format launch countdown for display."""
    lines = [
        "",
        "╔" + "═" * 60 + "╗",
        "║" + " " * 18 + "LAUNCH COUNTDOWN" + " " * 26 + "║",
        "╠" + "═" * 60 + "╣",
    ]
    
    # Big countdown display
    if countdown.days_until > 0:
        lines.append(f"║ 🚀 {countdown.days_until} DAYS, {countdown.hours_until} HOURS until launch!".ljust(61) + "║")
    elif countdown.days_until == 0:
        lines.append(f"║ 🚀 LAUNCH DAY! {countdown.hours_until} hours remaining".ljust(61) + "║")
    else:
        lines.append(f"║ ⚠️  Launch date has passed ({countdown.launch_date})".ljust(61) + "║")
    
    lines.append(f"║ 📅 Launch: {countdown.launch_date}".ljust(61) + "║")
    lines.append("╠" + "═" * 60 + "╣")
    
    # Progress bar
    filled = countdown.ready_percentage // 5
    empty = 20 - filled
    progress = "█" * filled + "░" * empty
    lines.append(f"║ READINESS: [{progress}] {countdown.ready_percentage}%".ljust(61) + "║")
    lines.append("╠" + "─" * 60 + "╣")
    
    # Checklist by category
    current_category = None
    for item in countdown.checklist:
        if item.category != current_category:
            current_category = item.category
            lines.append(f"║ 📋 {current_category}:".ljust(61) + "║")
        
        icon = "✅" if item.completed else "⏳"
        lines.append(f"║   {icon} {item.name}".ljust(61) + "║")
    
    lines.append("╠" + "═" * 60 + "╣")
    
    if countdown.ready_percentage == 100:
        lines.append("║ 🎉 ALL SYSTEMS GO! Ready for launch!".ljust(61) + "║")
    elif countdown.ready_percentage >= 70:
        lines.append("║ 👍 Almost ready! Complete remaining items.".ljust(61) + "║")
    else:
        lines.append("║ ⚠️  Not ready yet. Complete checklist items.".ljust(61) + "║")
    
    lines.append("╚" + "═" * 60 + "╝")
    
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════
# PIPELINE AUTOMATION: PRESETS, PROGRESS, VERIFICATION
# ═══════════════════════════════════════════════════════════════════════


PIPELINE_PRESETS = {
    "quick": {
        "name": "Quick",
        "description": "Fast product, no media",
        "audio": False,
        "video": False,
        "deploy": False,
        "schedule": False,
        "price": 27.00,
        "sale_price": None,
    },
    "standard": {
        "name": "Standard",
        "description": "Full product with audio and deploy",
        "audio": True,
        "video": False,
        "deploy": True,
        "schedule": False,
        "price": 47.00,
        "sale_price": None,
    },
    "premium": {
        "name": "Premium",
        "description": "Complete product with all media and scheduling",
        "audio": True,
        "video": True,
        "deploy": True,
        "schedule": True,
        "price": 97.00,
        "sale_price": 67.00,
    },
    "enterprise": {
        "name": "Enterprise",
        "description": "Maximum value with extended content",
        "audio": True,
        "video": True,
        "deploy": True,
        "schedule": True,
        "price": 197.00,
        "sale_price": 147.00,
    },
}


@dataclass
class PipelinePreset:
    """A pipeline configuration preset."""
    name: str
    description: str
    audio: bool
    video: bool
    deploy: bool
    schedule: bool
    price: float
    sale_price: Optional[float]


def get_pipeline_preset(name: str) -> Optional[PipelinePreset]:
    """Get a pipeline preset by name."""
    if name not in PIPELINE_PRESETS:
        return None
    
    preset = PIPELINE_PRESETS[name]
    return PipelinePreset(
        name=preset["name"],
        description=preset["description"],
        audio=preset["audio"],
        video=preset["video"],
        deploy=preset["deploy"],
        schedule=preset["schedule"],
        price=preset["price"],
        sale_price=preset["sale_price"],
    )


def format_pipeline_presets() -> str:
    """Format pipeline presets for display."""
    lines = [
        "",
        "╔" + "═" * 80 + "╗",
        "║" + " " * 28 + "PIPELINE PRESETS" + " " * 36 + "║",
        "╠" + "═" * 80 + "╣",
        "║ {:12} │ {:30} │ {:6} │ {:6} │ {:8} ║".format(
            "Preset", "Description", "Audio", "Video", "Price"
        ),
        "╠" + "─" * 80 + "╣",
    ]
    
    for key, preset in PIPELINE_PRESETS.items():
        audio = "✅" if preset["audio"] else "❌"
        video = "✅" if preset["video"] else "❌"
        price = f"${preset['price']:.0f}"
        lines.append("║ {:12} │ {:30} │ {:6} │ {:6} │ {:8} ║".format(
            key, preset["description"][:30], audio, video, price
        ))
    
    lines.append("╠" + "═" * 80 + "╣")
    lines.append("║ Usage: product-builder auto-launch --preset <name>".ljust(81) + "║")
    lines.append("╚" + "═" * 80 + "╝")
    
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════
# PIPELINE PROGRESS TRACKING
# ═══════════════════════════════════════════════════════════════════════


PIPELINE_PHASES = [
    ("create", "Creating product content"),
    ("audio", "Generating audio"),
    ("video", "Generating video"),
    ("seo", "Creating SEO metadata"),
    ("deploy", "Deploying to store"),
    ("marketing", "Generating marketing"),
    ("schedule", "Scheduling content"),
]


@dataclass
class PipelineProgress:
    """Track pipeline execution progress."""
    current_phase: str
    current_index: int
    total_phases: int
    phase_results: Dict[str, bool]
    start_time: str
    errors: List[str]


def create_pipeline_progress(enabled_phases: List[str]) -> PipelineProgress:
    """Create a new pipeline progress tracker."""
    from datetime import datetime
    
    return PipelineProgress(
        current_phase="",
        current_index=0,
        total_phases=len(enabled_phases),
        phase_results={},
        start_time=datetime.now().isoformat(),
        errors=[]
    )


def format_progress_bar(progress: PipelineProgress, status: str) -> str:
    """Format a progress bar for display."""
    if progress.total_phases == 0:
        return ""
    
    percentage = int((progress.current_index / progress.total_phases) * 100)
    filled = percentage // 5
    empty = 20 - filled
    bar = "█" * filled + "░" * empty
    
    return f"[{bar}] {percentage:3d}%  {status}"


# ═══════════════════════════════════════════════════════════════════════
# PHASE VERIFICATION
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class PhaseVerification:
    """Result of verifying a pipeline phase."""
    phase: str
    passed: bool
    checks: List[Tuple[str, bool, str]]


def verify_create_phase(output_dir: Path) -> PhaseVerification:
    """Verify the create phase completed successfully."""
    checks = []
    
    # Check for PDF
    pdfs = list(output_dir.glob("*.pdf"))
    checks.append(("PDF exists", len(pdfs) > 0, f"Found {len(pdfs)} PDF(s)"))
    
    # Check for cover image
    images_dir = output_dir / "images"
    has_cover = images_dir.exists() and any(images_dir.glob("*"))
    checks.append(("Cover image", has_cover, "Image found" if has_cover else "No image"))
    
    # Check for landing page
    lp_file = output_dir / "landing_page_content.json"
    checks.append(("Landing page", lp_file.exists(), "Content ready" if lp_file.exists() else "Missing"))
    
    # Check for product.json
    config_file = output_dir.parent / "product.json"
    if not config_file.exists():
        config_file = output_dir / "product.json"
    checks.append(("Product config", config_file.exists(), "Config found" if config_file.exists() else "Missing"))
    
    passed = all(check[1] for check in checks)
    return PhaseVerification("create", passed, checks)


def verify_deploy_phase(slug: str, salarsu_path: Path = None) -> PhaseVerification:
    """Verify the deploy phase completed successfully."""
    if salarsu_path is None:
        salarsu_path = Path.home() / "Projects" / "salarsu"
    
    checks = []
    
    # Check ZIP file
    zip_path = salarsu_path / "public" / "downloads" / "products" / f"{slug}.zip"
    checks.append(("ZIP deployed", zip_path.exists(), "Found" if zip_path.exists() else "Missing"))
    
    # Check image
    image_path = salarsu_path / "public" / "images" / "products" / f"{slug}.png"
    checks.append(("Image deployed", image_path.exists(), "Found" if image_path.exists() else "Missing"))
    
    passed = all(check[1] for check in checks)
    return PhaseVerification("deploy", passed, checks)


def format_phase_verification(verification: PhaseVerification) -> str:
    """Format phase verification for display."""
    icon = "✅" if verification.passed else "❌"
    status = "PASSED" if verification.passed else "FAILED"
    
    lines = [f"   {icon} {verification.phase.upper()}: {status}"]
    for check_name, passed, message in verification.checks:
        check_icon = "✓" if passed else "✗"
        lines.append(f"      {check_icon} {check_name}: {message}")
    
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════
# PIPELINE SUMMARY
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class PipelineSummary:
    """Summary of a completed pipeline run."""
    title: str
    slug: str
    output_dir: str
    phases_completed: List[str]
    phases_failed: List[str]
    pdf_pages: int
    pdf_size_mb: float
    audio_count: int
    audio_duration_min: int
    video_count: int
    store_url: Optional[str]
    download_url: Optional[str]
    posts_scheduled: int
    emails_registered: int
    launch_date: Optional[str]
    days_until_launch: int
    total_duration_sec: int


def generate_pipeline_summary(
    title: str,
    slug: str,
    output_dir: Path,
    progress: PipelineProgress,
    launch_date: str = None
) -> PipelineSummary:
    """Generate a summary of the pipeline run."""
    from datetime import datetime
    import os
    
    # Calculate duration
    try:
        start = datetime.fromisoformat(progress.start_time)
        duration = int((datetime.now() - start).total_seconds())
    except:
        duration = 0
    
    # Collect stats
    phases_completed = [p for p, success in progress.phase_results.items() if success]
    phases_failed = [p for p, success in progress.phase_results.items() if not success]
    
    # PDF stats
    pdf_pages = 0
    pdf_size = 0
    for pdf in output_dir.glob("*.pdf"):
        pdf_size += pdf.stat().st_size / (1024 * 1024)
        # Rough page estimate
        pdf_pages = max(pdf_pages, int(pdf.stat().st_size / 50000))
    
    # Audio stats
    audio_dir = output_dir / "audio"
    audio_count = len(list(audio_dir.glob("*.mp3"))) if audio_dir.exists() else 0
    audio_duration = audio_count * 15  # Estimate 15 min per track
    
    # Video stats
    video_dir = output_dir / "video"
    video_count = len(list(video_dir.glob("*.mp4"))) if video_dir.exists() else 0
    
    # Launch date
    days_until = 0
    if launch_date:
        try:
            launch = datetime.strptime(launch_date, "%Y-%m-%d")
            days_until = (launch - datetime.now()).days
        except:
            pass
    
    return PipelineSummary(
        title=title,
        slug=slug,
        output_dir=str(output_dir),
        phases_completed=phases_completed,
        phases_failed=phases_failed,
        pdf_pages=pdf_pages,
        pdf_size_mb=pdf_size,
        audio_count=audio_count,
        audio_duration_min=audio_duration,
        video_count=video_count,
        store_url=f"https://salars.net/digital/{slug}" if "deploy" in phases_completed else None,
        download_url=f"https://salars.net/downloads/products/{slug}.zip" if "deploy" in phases_completed else None,
        posts_scheduled=0,  # Would need to check markers
        emails_registered=0,  # Would need to check markers
        launch_date=launch_date,
        days_until_launch=days_until,
        total_duration_sec=duration
    )


def format_pipeline_summary(summary: PipelineSummary) -> str:
    """Format pipeline summary for display."""
    lines = [
        "",
        "═" * 70,
        "🎉 PRODUCT LAUNCH COMPLETE!",
        "═" * 70,
        f"   📁 Product: {summary.output_dir}",
        f"   🏷️  Title: {summary.title}",
        "",
    ]
    
    # Assets
    lines.append("   📦 Assets Created:")
    if summary.pdf_pages > 0:
        lines.append(f"      • PDF: ~{summary.pdf_pages} pages, {summary.pdf_size_mb:.1f}MB")
    if summary.audio_count > 0:
        lines.append(f"      • Audio: {summary.audio_count} tracks, ~{summary.audio_duration_min}m")
    if summary.video_count > 0:
        lines.append(f"      • Video: {summary.video_count} videos")
    
    lines.append("")
    
    # URLs
    if summary.store_url:
        lines.append("   🌐 Live URLs:")
        lines.append(f"      • Store: {summary.store_url}")
        lines.append(f"      • Download: {summary.download_url}")
        lines.append("")
    
    # Launch date
    if summary.launch_date:
        lines.append(f"   📅 Launch: {summary.launch_date} ({summary.days_until_launch} days away)")
        lines.append("")
    
    # Duration
    mins = summary.total_duration_sec // 60
    secs = summary.total_duration_sec % 60
    lines.append(f"   ⏱️  Duration: {mins}m {secs}s")
    
    # Phase summary
    completed = len(summary.phases_completed)
    total = completed + len(summary.phases_failed)
    lines.append(f"   ✅ Phases: {completed}/{total} completed")
    
    if summary.phases_failed:
        lines.append(f"   ⚠️  Failed: {', '.join(summary.phases_failed)}")
    
    lines.append("═" * 70)
    
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════
# QUALITY INTELLIGENCE SYSTEM
# ═══════════════════════════════════════════════════════════════════════


# Quality thresholds
QUALITY_THRESHOLDS = {
    "readability_min": 40,       # Flesch Reading Ease minimum
    "readability_max": 80,       # Flesch Reading Ease maximum (not too simple)
    "word_count_min": 5000,      # Minimum words for a product
    "page_count_min": 20,        # Minimum pages
    "actionable_ratio_min": 0.15, # 15% actionable content
    "overall_score_min": 70,     # Minimum overall quality score
}


@dataclass
class ReadabilityScore:
    """Text readability analysis."""
    flesch_reading_ease: float
    flesch_kincaid_grade: float
    avg_sentence_length: float
    avg_word_length: float
    complex_word_ratio: float
    reading_level: str
    target_audience: str


def calculate_readability(text: str) -> ReadabilityScore:
    """Calculate readability metrics for text."""
    import re
    
    # Clean text
    text = re.sub(r'[#*_\[\]()]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Count elements
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    sentence_count = max(len(sentences), 1)
    
    words = text.split()
    word_count = max(len(words), 1)
    
    # Count syllables (approximation)
    def count_syllables(word):
        word = word.lower()
        vowels = 'aeiouy'
        count = 0
        prev_vowel = False
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_vowel:
                count += 1
            prev_vowel = is_vowel
        if word.endswith('e'):
            count -= 1
        return max(count, 1)
    
    syllable_count = sum(count_syllables(w) for w in words)
    
    # Complex words (3+ syllables)
    complex_words = sum(1 for w in words if count_syllables(w) >= 3)
    complex_ratio = complex_words / word_count
    
    # Averages
    avg_sentence_length = word_count / sentence_count
    avg_word_length = sum(len(w) for w in words) / word_count
    
    # Flesch Reading Ease: 206.835 - 1.015 * ASL - 84.6 * ASW
    asl = avg_sentence_length
    asw = syllable_count / word_count
    flesch_ease = 206.835 - (1.015 * asl) - (84.6 * asw)
    flesch_ease = max(0, min(100, flesch_ease))
    
    # Flesch-Kincaid Grade Level
    fk_grade = (0.39 * asl) + (11.8 * asw) - 15.59
    fk_grade = max(0, min(20, fk_grade))
    
    # Determine reading level
    if flesch_ease >= 80:
        reading_level = "Easy"
        target_audience = "General public, casual readers"
    elif flesch_ease >= 60:
        reading_level = "Standard"
        target_audience = "High school to college level"
    elif flesch_ease >= 40:
        reading_level = "Moderate"
        target_audience = "College educated professionals"
    elif flesch_ease >= 20:
        reading_level = "Difficult"
        target_audience = "Advanced readers, experts"
    else:
        reading_level = "Very Difficult"
        target_audience = "Specialists, academics"
    
    return ReadabilityScore(
        flesch_reading_ease=round(flesch_ease, 1),
        flesch_kincaid_grade=round(fk_grade, 1),
        avg_sentence_length=round(avg_sentence_length, 1),
        avg_word_length=round(avg_word_length, 2),
        complex_word_ratio=round(complex_ratio, 3),
        reading_level=reading_level,
        target_audience=target_audience
    )


def format_readability_score(score: ReadabilityScore) -> str:
    """Format readability score for display."""
    lines = [
        "",
        "╔" + "═" * 60 + "╗",
        "║" + " " * 18 + "READABILITY SCORE" + " " * 25 + "║",
        "╠" + "═" * 60 + "╣",
        f"║ 📊 Flesch Reading Ease: {score.flesch_reading_ease}/100".ljust(61) + "║",
        f"║ 📚 Flesch-Kincaid Grade: {score.flesch_kincaid_grade}".ljust(61) + "║",
        f"║ 📝 Reading Level: {score.reading_level}".ljust(61) + "║",
        f"║ 🎯 Target Audience: {score.target_audience}".ljust(61) + "║",
        "╠" + "─" * 60 + "╣",
        f"║ Avg Sentence Length: {score.avg_sentence_length} words".ljust(61) + "║",
        f"║ Avg Word Length: {score.avg_word_length} chars".ljust(61) + "║",
        f"║ Complex Word Ratio: {score.complex_word_ratio * 100:.1f}%".ljust(61) + "║",
        "╚" + "═" * 60 + "╝",
    ]
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════
# CONTENT DENSITY ANALYSIS
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class ContentDensity:
    """Content value density analysis."""
    total_words: int
    total_pages: int
    words_per_page: int
    actionable_items: int
    actionable_ratio: float
    examples_count: int
    lists_count: int
    headers_count: int
    value_score: float


def analyze_content_density(text: str) -> ContentDensity:
    """Analyze content density and value metrics."""
    import re
    
    # Word and page counts
    words = text.split()
    total_words = len(words)
    total_pages = max(1, total_words // 250)  # ~250 words per page
    words_per_page = total_words // total_pages
    
    # Actionable items (imperatives, numbered steps)
    actionable_patterns = [
        r'\d+\.\s+\w+',           # Numbered steps
        r'(?:Step|Action|Do|Try|Start|Create|Build|Make|Write|Set|Add|Remove)\s',
        r'(?:First|Next|Then|Finally|Now)\,?\s',
        r'\[\s*\]\s+\w+',          # Checkboxes
    ]
    actionable_items = 0
    for pattern in actionable_patterns:
        actionable_items += len(re.findall(pattern, text, re.IGNORECASE))
    
    actionable_ratio = actionable_items / max(total_words, 1)
    
    # Examples and lists
    examples_count = len(re.findall(r'(?:Example|Case Study|For instance|e\.g\.)', text, re.IGNORECASE))
    lists_count = len(re.findall(r'^[-*•]\s+', text, re.MULTILINE))
    headers_count = len(re.findall(r'^#{1,6}\s+', text, re.MULTILINE))
    
    # Value score (0-100)
    value_score = min(100, (
        (min(actionable_ratio * 100, 30)) +                    # Up to 30 for actionability
        (min(examples_count * 5, 20)) +                         # Up to 20 for examples
        (min(lists_count * 2, 20)) +                            # Up to 20 for structure
        (min(headers_count * 2, 20)) +                          # Up to 20 for organization
        (10 if words_per_page >= 200 else 5)                    # Density bonus
    ))
    
    return ContentDensity(
        total_words=total_words,
        total_pages=total_pages,
        words_per_page=words_per_page,
        actionable_items=actionable_items,
        actionable_ratio=round(actionable_ratio, 4),
        examples_count=examples_count,
        lists_count=lists_count,
        headers_count=headers_count,
        value_score=round(value_score, 1)
    )


def format_content_density(density: ContentDensity) -> str:
    """Format content density for display."""
    lines = [
        "",
        "╔" + "═" * 60 + "╗",
        "║" + " " * 18 + "CONTENT DENSITY" + " " * 27 + "║",
        "╠" + "═" * 60 + "╣",
        f"║ 📊 Value Score: {density.value_score}/100".ljust(61) + "║",
        "╠" + "─" * 60 + "╣",
        f"║ 📝 Total Words: {density.total_words:,}".ljust(61) + "║",
        f"║ 📄 Estimated Pages: {density.total_pages}".ljust(61) + "║",
        f"║ 📐 Words/Page: {density.words_per_page}".ljust(61) + "║",
        "╠" + "─" * 60 + "╣",
        f"║ ✅ Actionable Items: {density.actionable_items}".ljust(61) + "║",
        f"║ 📚 Examples: {density.examples_count}".ljust(61) + "║",
        f"║ 📋 Lists: {density.lists_count}".ljust(61) + "║",
        f"║ 🏷️  Headers: {density.headers_count}".ljust(61) + "║",
        "╚" + "═" * 60 + "╝",
    ]
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════
# COMPLETENESS CHECK
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class CompletenessCheck:
    """Product completeness analysis."""
    has_pdf: bool
    has_cover: bool
    has_landing_page: bool
    has_emails: bool
    has_social: bool
    has_seo: bool
    has_utm: bool
    has_audio: bool
    has_video: bool
    completeness_score: int
    missing_items: List[str]


def check_product_completeness(product_dir: Path) -> CompletenessCheck:
    """Check completeness of a product."""
    output_dir = product_dir / "output"
    
    # Check each component
    has_pdf = any(output_dir.glob("*.pdf"))
    
    images_dir = output_dir / "images"
    has_cover = images_dir.exists() and any(images_dir.glob("*"))
    
    has_landing_page = (output_dir / "landing_page_content.json").exists()
    has_emails = any(output_dir.glob("emails_*.md"))
    has_social = (output_dir / "social_promo.md").exists()
    has_seo = (output_dir / "seo_metadata.json").exists()
    has_utm = (output_dir / "utm_links.json").exists()
    
    audio_dir = output_dir / "audio"
    has_audio = audio_dir.exists() and any(audio_dir.glob("*.mp3"))
    
    video_dir = output_dir / "video"
    has_video = video_dir.exists() and any(video_dir.glob("*.mp4"))
    
    # Calculate score
    items = [
        (has_pdf, "PDF", 20),
        (has_cover, "Cover Image", 10),
        (has_landing_page, "Landing Page", 15),
        (has_emails, "Email Sequences", 15),
        (has_social, "Social Posts", 10),
        (has_seo, "SEO Metadata", 10),
        (has_utm, "UTM Links", 5),
        (has_audio, "Audio", 10),
        (has_video, "Video", 5),
    ]
    
    completeness_score = sum(weight for has, _, weight in items if has)
    missing_items = [name for has, name, _ in items if not has]
    
    return CompletenessCheck(
        has_pdf=has_pdf,
        has_cover=has_cover,
        has_landing_page=has_landing_page,
        has_emails=has_emails,
        has_social=has_social,
        has_seo=has_seo,
        has_utm=has_utm,
        has_audio=has_audio,
        has_video=has_video,
        completeness_score=completeness_score,
        missing_items=missing_items
    )


def format_completeness_check(check: CompletenessCheck) -> str:
    """Format completeness check for display."""
    lines = [
        "",
        "╔" + "═" * 60 + "╗",
        "║" + " " * 17 + "COMPLETENESS CHECK" + " " * 25 + "║",
        "╠" + "═" * 60 + "╣",
        f"║ 📊 Completeness Score: {check.completeness_score}/100".ljust(61) + "║",
        "╠" + "─" * 60 + "╣",
    ]
    
    items = [
        ("PDF", check.has_pdf),
        ("Cover Image", check.has_cover),
        ("Landing Page", check.has_landing_page),
        ("Email Sequences", check.has_emails),
        ("Social Posts", check.has_social),
        ("SEO Metadata", check.has_seo),
        ("UTM Links", check.has_utm),
        ("Audio", check.has_audio),
        ("Video", check.has_video),
    ]
    
    for name, has in items:
        icon = "✅" if has else "⏳"
        lines.append(f"║ {icon} {name}".ljust(61) + "║")
    
    if check.missing_items:
        lines.append("╠" + "═" * 60 + "╣")
        lines.append(f"║ ⚠️  Missing: {', '.join(check.missing_items[:3])}".ljust(61) + "║")
    
    lines.append("╚" + "═" * 60 + "╝")
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════
# OVERALL QUALITY SCORE
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class QualityReport:
    """Comprehensive quality analysis report."""
    product_name: str
    readability: ReadabilityScore
    density: ContentDensity
    completeness: CompletenessCheck
    overall_score: float
    grade: str
    passed: bool
    recommendations: List[str]


def generate_quality_report(product_dir: Path) -> Optional[QualityReport]:
    """Generate comprehensive quality report for a product."""
    output_dir = product_dir / "output"
    
    if not output_dir.exists():
        return None
    
    # Load product name
    config_file = product_dir / "product.json"
    if config_file.exists():
        import json
        config = json.loads(config_file.read_text())
        product_name = config.get("title", product_dir.name)
    else:
        product_name = product_dir.name
    
    # Collect all text content
    text_content = ""
    for md_file in output_dir.glob("*.md"):
        text_content += md_file.read_text() + "\n\n"
    
    # If no markdown, try to get from prompts/responses
    if len(text_content.strip()) < 100:
        prompts_dir = output_dir / "prompts"
        if prompts_dir.exists():
            for prompt_file in prompts_dir.glob("*.md"):
                text_content += prompt_file.read_text() + "\n\n"
    
    # Analyze readability
    readability = calculate_readability(text_content) if text_content else ReadabilityScore(
        flesch_reading_ease=0, flesch_kincaid_grade=0, avg_sentence_length=0,
        avg_word_length=0, complex_word_ratio=0, reading_level="N/A", target_audience="N/A"
    )
    
    # Analyze density
    density = analyze_content_density(text_content) if text_content else ContentDensity(
        total_words=0, total_pages=0, words_per_page=0, actionable_items=0,
        actionable_ratio=0, examples_count=0, lists_count=0, headers_count=0, value_score=0
    )
    
    # Check completeness
    completeness = check_product_completeness(product_dir)
    
    # Calculate overall score (weighted average)
    readability_score = min(100, max(0, readability.flesch_reading_ease))
    overall_score = (
        readability_score * 0.25 +
        density.value_score * 0.35 +
        completeness.completeness_score * 0.40
    )
    
    # Determine grade
    if overall_score >= 90:
        grade = "A+"
    elif overall_score >= 80:
        grade = "A"
    elif overall_score >= 70:
        grade = "B"
    elif overall_score >= 60:
        grade = "C"
    elif overall_score >= 50:
        grade = "D"
    else:
        grade = "F"
    
    passed = overall_score >= QUALITY_THRESHOLDS["overall_score_min"]
    
    # Generate recommendations
    recommendations = []
    if readability.flesch_reading_ease < 40:
        recommendations.append("Simplify language - current text is too difficult")
    elif readability.flesch_reading_ease > 80:
        recommendations.append("Add more depth - content may be too simple")
    
    if density.actionable_items < 10:
        recommendations.append("Add more actionable steps and exercises")
    
    if density.examples_count < 5:
        recommendations.append("Include more examples and case studies")
    
    if not completeness.has_pdf:
        recommendations.append("Generate PDF - essential for product delivery")
    
    if not completeness.has_cover:
        recommendations.append("Add cover image - increases perceived value")
    
    if not completeness.has_audio:
        recommendations.append("Consider audio version - increases accessibility")
    
    return QualityReport(
        product_name=product_name,
        readability=readability,
        density=density,
        completeness=completeness,
        overall_score=round(overall_score, 1),
        grade=grade,
        passed=passed,
        recommendations=recommendations[:5]  # Top 5
    )


def format_quality_report(report: QualityReport) -> str:
    """Format comprehensive quality report for display."""
    passed_icon = "✅ PASSED" if report.passed else "❌ FAILED"
    
    lines = [
        "",
        "╔" + "═" * 70 + "╗",
        "║" + " " * 23 + "QUALITY INTELLIGENCE REPORT" + " " * 20 + "║",
        "╠" + "═" * 70 + "╣",
        f"║ 📦 Product: {report.product_name[:50]}".ljust(71) + "║",
        "╠" + "═" * 70 + "╣",
    ]
    
    # Overall score with visual
    filled = int(report.overall_score // 5)
    empty = 20 - filled
    bar = "█" * filled + "░" * empty
    lines.append(f"║ OVERALL SCORE: [{bar}] {report.overall_score:.0f}%".ljust(71) + "║")
    lines.append(f"║ GRADE: {report.grade}  |  STATUS: {passed_icon}".ljust(71) + "║")
    lines.append("╠" + "═" * 70 + "╣")
    
    # Component scores
    lines.append("║ COMPONENT SCORES:".ljust(71) + "║")
    lines.append(f"║   📖 Readability: {report.readability.flesch_reading_ease}/100 ({report.readability.reading_level})".ljust(71) + "║")
    lines.append(f"║   💎 Content Value: {report.density.value_score}/100".ljust(71) + "║")
    lines.append(f"║   ✅ Completeness: {report.completeness.completeness_score}/100".ljust(71) + "║")
    lines.append("╠" + "─" * 70 + "╣")
    
    # Stats
    lines.append("║ CONTENT STATS:".ljust(71) + "║")
    lines.append(f"║   📝 Words: {report.density.total_words:,}  |  📄 Pages: ~{report.density.total_pages}".ljust(71) + "║")
    lines.append(f"║   ✅ Actionable Items: {report.density.actionable_items}  |  📚 Examples: {report.density.examples_count}".ljust(71) + "║")
    
    # Recommendations
    if report.recommendations:
        lines.append("╠" + "═" * 70 + "╣")
        lines.append("║ 💡 RECOMMENDATIONS:".ljust(71) + "║")
        for rec in report.recommendations[:4]:
            lines.append(f"║   • {rec[:60]}".ljust(71) + "║")
    
    lines.append("╚" + "═" * 70 + "╝")
    
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════
# QUALITY GATE (DEPLOY BLOCKER)
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class QualityGate:
    """Quality gate result for deploy blocking."""
    passed: bool
    score: float
    threshold: float
    blocking_issues: List[str]
    warnings: List[str]


def check_quality_gate(product_dir: Path, threshold: float = None) -> QualityGate:
    """Check if product passes quality gate for deployment."""
    if threshold is None:
        threshold = QUALITY_THRESHOLDS["overall_score_min"]
    
    report = generate_quality_report(product_dir)
    
    if not report:
        return QualityGate(
            passed=False,
            score=0,
            threshold=threshold,
            blocking_issues=["No product found"],
            warnings=[]
        )
    
    blocking_issues = []
    warnings = []
    
    # Check overall score
    if report.overall_score < threshold:
        blocking_issues.append(f"Overall score {report.overall_score:.0f}% below threshold {threshold:.0f}%")
    
    # Check critical components
    if not report.completeness.has_pdf:
        blocking_issues.append("No PDF generated - cannot deploy")
    
    # Warnings (non-blocking)
    if report.readability.flesch_reading_ease < 30:
        warnings.append("Very difficult to read - may limit audience")
    
    if report.density.total_words < QUALITY_THRESHOLDS["word_count_min"]:
        warnings.append(f"Content under {QUALITY_THRESHOLDS['word_count_min']:,} words")
    
    if not report.completeness.has_cover:
        warnings.append("No cover image - consider adding one")
    
    if report.density.actionable_items < 5:
        warnings.append("Low actionable content - add exercises")
    
    return QualityGate(
        passed=len(blocking_issues) == 0,
        score=report.overall_score,
        threshold=threshold,
        blocking_issues=blocking_issues,
        warnings=warnings
    )


def format_quality_gate(gate: QualityGate) -> str:
    """Format quality gate result for display."""
    icon = "✅ GATE PASSED" if gate.passed else "❌ GATE FAILED"
    
    lines = [
        "",
        "╔" + "═" * 60 + "╗",
        "║" + " " * 20 + "QUALITY GATE" + " " * 28 + "║",
        "╠" + "═" * 60 + "╣",
        f"║ {icon}".ljust(61) + "║",
        f"║ Score: {gate.score:.0f}%  |  Threshold: {gate.threshold:.0f}%".ljust(61) + "║",
        "╠" + "─" * 60 + "╣",
    ]
    
    if gate.blocking_issues:
        lines.append("║ 🚫 BLOCKING ISSUES:".ljust(61) + "║")
        for issue in gate.blocking_issues:
            lines.append(f"║   ❌ {issue[:50]}".ljust(61) + "║")
    
    if gate.warnings:
        lines.append("║ ⚠️  WARNINGS:".ljust(61) + "║")
        for warning in gate.warnings[:3]:
            lines.append(f"║   ⚠️ {warning[:50]}".ljust(61) + "║")
    
    if gate.passed and not gate.warnings:
        lines.append("║ 🎉 All checks passed! Ready for deployment.".ljust(61) + "║")
    
    lines.append("╚" + "═" * 60 + "╝")
    
    return "\n".join(lines)
