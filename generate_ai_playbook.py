#!/usr/bin/env python3
"""
Full Product Generator for AI Integration Playbook

A practical guide to collaborating with AI tools while keeping your creativity,
humanity, and critical thinking intact.

Features:
- 12 chapters targeting 100+ pages (1800+ words/chapter)
- 6 research-backed bonuses
- Quality checks embedded in prompts
- Page validation and expansion workflow

Usage:
    python3 generate_ai_playbook.py
"""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

# Import expansion utilities
from agents.product_builder.pipeline.content_expander import (
    validate_page_count, MIN_PAGES_MAIN_PRODUCT, 
    MIN_WORDS_PER_CHAPTER, TARGET_WORDS_PER_CHAPTER
)

OUTPUT_DIR = Path("products/ai_integration_playbook/output")
RESPONSES_DIR = OUTPUT_DIR / "responses"
BONUS_RESPONSES_DIR = OUTPUT_DIR / "bonuses" / "responses"

# ═══════════════════════════════════════════════════════════════
# PRODUCT CONFIGURATION
# ═══════════════════════════════════════════════════════════════

PRODUCT_CONFIG = {
    "title": "The AI Integration Playbook",
    "author": "Randy Salars",
    "topic": "AI Collaboration and Productivity",
    "promise": "Work WITH AI, not FOR it—master AI tools while keeping your creativity, humanity, and critical thinking intact",
    "audience": "Knowledge workers, creatives, and professionals who want to leverage AI without losing their unique voice or becoming dependent on it",
    "thesis": "AI is a powerful collaborator, not a replacement for human judgment. The key to AI mastery isn't learning to follow AI—it's learning to lead it while staying authentically human.",
    
    # 12 CHAPTERS
    "chapters": [
        {
            "number": 1,
            "title": "The AI Partnership Mindset",
            "purpose": "Shift from 'AI as tool' to 'AI as collaborator' while maintaining human agency",
            "takeaways": [
                "Why most people use AI wrong and get mediocre results",
                "The Human-AI collaboration spectrum: when to lead, when to delegate",
                "The 3 principles of effective AI partnership"
            ]
        },
        {
            "number": 2,
            "title": "Prompt Engineering Fundamentals",
            "purpose": "Master the art and science of communicating with AI",
            "takeaways": [
                "The anatomy of a perfect prompt",
                "The CRISP framework: Context, Role, Instructions, Style, Parameters",
                "Why vague prompts create vague outputs"
            ]
        },
        {
            "number": 3,
            "title": "Advanced Prompting Techniques",
            "purpose": "Go beyond basic prompts to unlock sophisticated AI capabilities",
            "takeaways": [
                "Chain-of-thought prompting for complex reasoning",
                "Few-shot learning: teaching by example",
                "Iterative refinement: the art of the follow-up"
            ]
        },
        {
            "number": 4,
            "title": "AI for Writing and Content",
            "purpose": "Use AI to enhance (not replace) your writing voice",
            "takeaways": [
                "Brainstorming and ideation workflows",
                "Editing and refinement techniques",
                "Maintaining your authentic voice with AI assistance"
            ]
        },
        {
            "number": 5,
            "title": "AI for Analysis and Research",
            "purpose": "Leverage AI for data analysis, research synthesis, and insight generation",
            "takeaways": [
                "Breaking down complex documents and data",
                "Synthesizing multiple sources into coherent insights",
                "Fact-checking and verification workflows"
            ]
        },
        {
            "number": 6,
            "title": "AI for Coding and Technical Work",
            "purpose": "Partner with AI for development, debugging, and technical problem-solving",
            "takeaways": [
                "Code generation best practices",
                "Debugging with AI: rubber duck debugging amplified",
                "Architecture review and code refactoring with AI"
            ]
        },
        {
            "number": 7,
            "title": "AI for Creative Work",
            "purpose": "Use AI as a creative collaborator without losing originality",
            "takeaways": [
                "Image generation: from concept to creation",
                "Creative brainstorming and ideation",
                "The line between inspiration and imitation"
            ]
        },
        {
            "number": 8,
            "title": "Tool Selection and Mastery",
            "purpose": "Navigate the AI tool landscape and choose the right tool for each job",
            "takeaways": [
                "ChatGPT vs Claude vs Gemini: strengths and weaknesses",
                "Image tools compared: Midjourney, DALL-E, Stable Diffusion",
                "Specialized tools for specific workflows"
            ]
        },
        {
            "number": 9,
            "title": "Building AI Workflows",
            "purpose": "Create repeatable AI-assisted workflows for common tasks",
            "takeaways": [
                "The Task-Prompt-Review-Refine loop",
                "Automating repetitive work without losing quality",
                "Building your personal AI toolkit"
            ]
        },
        {
            "number": 10,
            "title": "Ethics and Authenticity",
            "purpose": "Navigate the ethical considerations of AI use responsibly",
            "takeaways": [
                "When AI use crosses ethical lines",
                "Disclosure and transparency in AI-assisted work",
                "Bias awareness and mitigation"
            ]
        },
        {
            "number": 11,
            "title": "Critical Thinking with AI",
            "purpose": "Maintain and strengthen critical thinking in an AI-augmented world",
            "takeaways": [
                "Why AI can be confidently wrong",
                "Verification and fact-checking rituals",
                "Avoiding over-reliance and intellectual atrophy"
            ]
        },
        {
            "number": 12,
            "title": "The Future-Proof Human",
            "purpose": "Stay adaptable, human, and valuable as AI continues to evolve",
            "takeaways": [
                "Skills that AI amplifies vs skills AI replaces",
                "Building a sustainable AI-augmented practice",
                "Staying human in an increasingly AI-powered world"
            ]
        }
    ],
    
    # 6 STANDARD BONUSES
    "bonuses": [
        {"type": "cookbook", "title": "The Prompt Cookbook", "min_words": 2000,
         "description": "50+ ready-to-use prompts for writing, coding, analysis, and creative work"},
        {"type": "worksheet", "title": "AI Integration Worksheets", "min_words": 1500,
         "description": "Self-assessment tools and planning templates for AI adoption"},
        {"type": "reference_card", "title": "Quick Reference Cards", "min_words": 1200,
         "description": "Prompt frameworks, tool comparisons, and decision guides"},
        {"type": "meditation", "title": "AI Tool Deep Dives", "min_words": 2000,
         "description": "Complete guides for ChatGPT, Claude, Midjourney, and more"},
        {"type": "journal", "title": "AI Experiment Journal", "min_words": 1500,
         "description": "30-day journal for tracking and improving your AI collaboration"},
        {"type": "checklist", "title": "AI Workflow Checklists", "min_words": 1200,
         "description": "Step-by-step checklists for common AI-assisted tasks"},
    ],
    
    "voice_rules": """
- Write with the authority of someone who uses AI daily and has developed real insights
- Be practical and specific—avoid vague advice like "learn to use AI well"
- Include real examples of prompts and their outputs
- Acknowledge AI's limitations honestly
- Vary sentence length for natural rhythm
- Use fragments for punchiness. Like this.
- Be direct and confident in recommendations
- Maintain a sense of human agency—we're leading AI, not following it
""",

    "chapter_template": """
You are a team of 4 expert writers creating a chapter on AI collaboration:
- **Head Writer**: Structure, voice, practical framing
- **AI Expert**: Technical accuracy, current best practices
- **Teacher**: Clarity, examples, hands-on exercises
- **Editor**: Tight prose, remove fluff, make every word count

---

## Product Context

**Product:** {title}
**Promise:** {promise}
**Audience:** {audience}
**Core Thesis:** {thesis}

---

## This Chapter

**Chapter {chapter_number}: {chapter_title}**
**Purpose:** {chapter_purpose}
**Key Takeaways:** {chapter_takeaways}

---

## Writer Passes

### 1. STRUCTURE (Architect Pass)
- Open with a story or scenario that illustrates the challenge
- Build to an "aha moment" that reframes how they think about AI
- Deliver practical teaching with clear frameworks
- Close with specific action steps they can use TODAY
- Target: 1,800-2,200 words

### 2. AI EXPERTISE (Expert Pass)
- Include ACTUAL prompt examples (not just descriptions)
- Show real AI outputs where relevant
- Cover current best practices as of 2024-2025
- Address common mistakes and how to avoid them

### 3. TEACHING (Teacher Pass)
- Include 3+ worked examples with specific details
- Add practical exercises the reader can try immediately
- Address the most common misconception about this topic
- Make abstract concepts concrete with analogies

### 4. POLISH (Editor Pass)
- Cut any sentence that doesn't earn its place
- Ensure every paragraph has a clear purpose
- Check for repetition and redundancy
- Verify the voice is conversational yet authoritative

---

## Voice Rules
{voice_rules}

---

## Quality Checklist

□ Includes at least 2 actual prompt examples
□ Contains practical, immediately usable advice
□ Addresses a common mistake or misconception
□ Has specific action steps at the end
□ Maintains human agency and critical thinking emphasis
□ Is between 1,800-2,200 words

---

## Output Format

Output the complete chapter in Markdown:
- Use ## for section headers
- Use ### for subsections
- Use **bold** for key terms
- Use code blocks for prompts: ```prompt
- Include specific examples throughout

BEGIN WRITING THE CHAPTER NOW.
""",

    # EXPANSION PROMPT TEMPLATE
    "expansion_template": """## Chapter Expansion Needed

**Chapter:** {chapter_title}
**Current Words:** {current_words}
**Target Words:** {target_words}
**Words to Add:** ~{words_to_add}

## Current Content Summary
{content_summary}

## Expansion Instructions

Add {words_to_add} words of NEW content. Options:
1. Add more prompt examples with analysis
2. Include additional use cases
3. Address more edge cases or objections
4. Add hands-on exercises
5. Deepen the conceptual explanation

Every sentence must add value. Maintain the existing voice.
""",

    # BONUS GENERATION TEMPLATE
    "bonus_template": """## Generate Research-Backed Bonus Content

**Bonus Type:** {bonus_type}
**Title:** {bonus_title}
**Description:** {description}
**Minimum Words:** {min_words}

---

## Product Context

**Product Title:** {title}
**Core Topic:** {topic}
**Target Audience:** {audience}
**Core Thesis:** {thesis}

---

## Quality Standards

1. **Substantive Content**: Real value, not padding
2. **Practical**: Immediately usable
3. **Current**: Reflects 2024-2025 AI landscape
4. **Well-Organized**: # for chapters, ## for sections

---

Write the complete bonus content now. Every section must provide genuine value.
"""
}

# ═══════════════════════════════════════════════════════════════
# GENERATOR FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def generate_chapter_prompts(config: dict, output_dir: Path):
    """Generate all chapter prompts."""
    prompts_dir = output_dir / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📝 Generating {len(config['chapters'])} chapter prompts...")
    
    for chapter in config["chapters"]:
        prompt = config["chapter_template"].format(
            title=config["title"],
            promise=config["promise"],
            audience=config["audience"],
            thesis=config["thesis"],
            chapter_number=chapter["number"],
            chapter_title=chapter["title"],
            chapter_purpose=chapter["purpose"],
            chapter_takeaways=", ".join(chapter["takeaways"]),
            voice_rules=config["voice_rules"]
        )
        
        filename = f"chapter_{chapter['number']:02d}_{chapter['title'].lower().replace(' ', '_')}.prompt.md"
        prompt_path = prompts_dir / filename
        prompt_path.write_text(prompt)
        print(f"   ✅ {filename}")
    
    print(f"\n📂 Prompts saved to: {prompts_dir}")


def validate_responses(config: dict, responses_dir: Path) -> dict:
    """Validate chapter responses and identify expansion needs."""
    print("\n📊 VALIDATING CHAPTER RESPONSES")
    print("=" * 50)
    
    chapters = []
    for chapter in config["chapters"]:
        matching = list(responses_dir.glob(f"chapter_{chapter['number']:02d}*.md"))
        
        if matching:
            content = matching[0].read_text()
            chapters.append({
                "title": chapter["title"],
                "purpose": chapter["purpose"],
                "content": content,
                "key_takeaways": chapter["takeaways"]
            })
            word_count = len(content.split())
            status = "✅" if word_count >= MIN_WORDS_PER_CHAPTER else "⚠️"
            print(f"   {status} Chapter {chapter['number']}: {word_count} words")
        else:
            print(f"   ❌ Chapter {chapter['number']}: MISSING")
            chapters.append({
                "title": chapter["title"],
                "purpose": chapter["purpose"],
                "content": "",
                "key_takeaways": chapter["takeaways"]
            })
    
    stats = validate_page_count(chapters, MIN_PAGES_MAIN_PRODUCT)
    
    print(f"\n📊 SUMMARY:")
    print(f"   Total Words: {stats.total_words:,}")
    print(f"   Estimated Pages: {stats.estimated_pages}")
    print(f"   Minimum Required: {MIN_PAGES_MAIN_PRODUCT}")
    print(f"   Status: {'✅ PASSES' if stats.meets_minimum else '❌ NEEDS EXPANSION'}")
    
    return {
        "chapters": chapters,
        "stats": stats,
        "needs_expansion": not stats.meets_minimum
    }


def generate_bonus_prompts(config: dict, output_dir: Path):
    """Generate prompts for all 6 bonus documents."""
    bonus_dir = output_dir / "bonus_prompts"
    bonus_dir.mkdir(exist_ok=True)
    
    print(f"\n🎁 GENERATING {len(config['bonuses'])} BONUS PROMPTS")
    print("=" * 50)
    
    for bonus in config["bonuses"]:
        prompt = config["bonus_template"].format(
            bonus_type=bonus["type"],
            bonus_title=bonus["title"],
            description=bonus.get("description", ""),
            min_words=bonus["min_words"],
            title=config["title"],
            topic=config["topic"],
            audience=config["audience"],
            thesis=config["thesis"]
        )
        
        filename = f"generate_{bonus['type']}.prompt.md"
        prompt_path = bonus_dir / filename
        prompt_path.write_text(prompt)
        print(f"   📋 {filename} (min {bonus['min_words']} words)")
    
    print(f"\n📂 Bonus prompts saved to: {bonus_dir}")


def main():
    """Main entry point."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RESPONSES_DIR.mkdir(exist_ok=True)
    BONUS_RESPONSES_DIR.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("🤖 AI INTEGRATION PLAYBOOK - PRODUCT GENERATOR")
    print("=" * 60)
    print(f"\n📕 {PRODUCT_CONFIG['title']}")
    print(f"📝 {len(PRODUCT_CONFIG['chapters'])} chapters planned")
    print(f"🎁 {len(PRODUCT_CONFIG['bonuses'])} bonuses planned")
    print(f"🎯 Target: {MIN_PAGES_MAIN_PRODUCT}+ pages ({MIN_WORDS_PER_CHAPTER}+ words/chapter)")
    
    # Step 1: Generate chapter prompts
    generate_chapter_prompts(PRODUCT_CONFIG, OUTPUT_DIR)
    
    # Step 2: Check for existing responses and validate
    existing_responses = list(RESPONSES_DIR.glob("*.md"))
    if existing_responses:
        print(f"\n📄 Found {len(existing_responses)} existing chapter responses")
        validation = validate_responses(PRODUCT_CONFIG, RESPONSES_DIR)
    
    # Step 3: Generate bonus prompts
    generate_bonus_prompts(PRODUCT_CONFIG, OUTPUT_DIR)
    
    print("\n" + "=" * 60)
    print("📋 NEXT STEPS")
    print("=" * 60)
    print("1. Feed chapter prompts to LLM → save to responses/")
    print("2. Run validation to check page count")
    print("3. Feed bonus prompts to LLM → save to bonuses/responses/")
    print("4. Generate images")
    print("5. Compile PDFs and package")


if __name__ == "__main__":
    main()
