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

