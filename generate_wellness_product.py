#!/usr/bin/env python3
"""
Full Product Generator for Holistic Wellness Protocol

This script follows the EXACT same process that created Financial Freedom Blueprint:
- 12 chapters
- 1,500+ words per chapter (18,000+ total)
- 100+ pages in final PDF
- Quality checks embedded in prompts

ENHANCED with:
- Page count validation and expansion prompts
- Research-backed bonus content generation
- Complete packaging workflow

Usage:
    python3 generate_wellness_product.py

This generates prompts, which can be fed to the LLM to create full chapter content.
"""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

# Import expansion utilities
from agents.product_builder.pipeline.content_expander import (
    validate_page_count, MIN_PAGES_MAIN_PRODUCT, 
    MIN_WORDS_PER_CHAPTER, TARGET_WORDS_PER_CHAPTER
)

OUTPUT_DIR = Path("products/holistic_wellness_protocol/output")
RESPONSES_DIR = OUTPUT_DIR / "responses"
PROMPTS_DIR = OUTPUT_DIR / "prompts"
EXPANSION_DIR = OUTPUT_DIR / "expansion_prompts"
BONUS_PROMPTS_DIR = OUTPUT_DIR / "bonus_prompts"

# ═══════════════════════════════════════════════════════════════
# PRODUCT CONFIGURATION
# ═══════════════════════════════════════════════════════════════

PRODUCT_CONFIG = {
    "title": "The Holistic Wellness Protocol",
    "author": "Randy Salars",
    "topic": "Holistic Health and Wellness",
    "promise": "Restore your natural vitality through integrated practices for nutrition, movement, sleep, and mindfulness",
    "audience": "Health-conscious adults feeling exhausted despite trying various wellness approaches",
    "thesis": "True wellness isn't found in extreme diets or punishing workouts—it's found in sustainable daily systems that work with your body's natural wisdom",
    
    # 12 CHAPTERS
    "chapters": [
        {
            "number": 1,
            "title": "The Wellness Reset",
            "purpose": "Shatter wellness industry myths and reveal why most health advice fails",
            "takeaways": [
                "Why willpower-based wellness fails 100% of the time",
                "The 4 pillars: Nutrition, Movement, Sleep, Mindfulness",
                "Small shifts compound into transformation"
            ]
        },
        {
            "number": 2,
            "title": "Nutrition Foundation",
            "purpose": "Simplify nutrition to what actually works long-term",
            "takeaways": [
                "The 80/20 rule of sustainable eating",
                "Foods to embrace vs minimize (with specific examples)",
                "Meal timing and its effects on energy"
            ]
        },
        {
            "number": 3,
            "title": "The Movement Protocol",
            "purpose": "Build a sustainable movement practice at any fitness level",
            "takeaways": [
                "The 3-level movement hierarchy",
                "The 15-minute minimum workout",
                "Non-exercise activity thermogenesis (NEAT)"
            ]
        },
        {
            "number": 4,
            "title": "Sleep Optimization",
            "purpose": "Transform sleep from afterthought to superpower",
            "takeaways": [
                "The science of sleep cycles and deep rest",
                "Environment optimization (temperature, light, sound)",
                "The 3-hour wind-down protocol"
            ]
        },
        {
            "number": 5,
            "title": "Mindfulness Practices",
            "purpose": "Develop mental clarity and stress resilience",
            "takeaways": [
                "The 5-minute daily practice that transforms stress response",
                "Beyond sitting meditation: walking, breath, gratitude",
                "How mindfulness interrupts chronic stress"
            ]
        },
        {
            "number": 6,
            "title": "The Morning Protocol",
            "purpose": "Design the first hour for optimal daily performance",
            "takeaways": [
                "The 15-minute minimum morning routine",
                "Light, hydration, and movement sequencing",
                "Protecting the first hour from reactive work"
            ]
        },
        {
            "number": 7,
            "title": "The Evening Protocol",
            "purpose": "Optimize the transition from activity to rest",
            "takeaways": [
                "The 3-hour wind-down structure",
                "The two-minute evening journal",
                "Sleep preparation rituals"
            ]
        },
        {
            "number": 8,
            "title": "Stress Management",
            "purpose": "Work with stress instead of against it",
            "takeaways": [
                "Acute vs chronic stress: understanding the difference",
                "The stress audit: identifying high-stress areas",
                "Immediate relief tools: 4-7-8 breath, 5-4-3-2-1 grounding"
            ]
        },
        {
            "number": 9,
            "title": "Energy Management",
            "purpose": "Treat energy as your most valuable resource",
            "takeaways": [
                "Understanding ultradian and circadian rhythms",
                "Energy deposits vs withdrawals",
                "Building an energy budget"
            ]
        },
        {
            "number": 10,
            "title": "Building Habits",
            "purpose": "Make wellness practices automatic",
            "takeaways": [
                "The habit loop: Cue → Routine → Reward",
                "Habit stacking for seamless integration",
                "The two-minute rule for starting new habits"
            ]
        },
        {
            "number": 11,
            "title": "The 90-Day Transformation",
            "purpose": "Structure the complete wellness journey",
            "takeaways": [
                "Days 1-30: Foundation phase",
                "Days 31-60: Expansion phase",
                "Days 61-90: Integration phase"
            ]
        },
        {
            "number": 12,
            "title": "Sustaining Wellness for Life",
            "purpose": "Maintain gains and continue evolving",
            "takeaways": [
                "Weekly, monthly, and quarterly review rhythms",
                "The one-rep rule for recovering from setbacks",
                "Building your wellness community"
            ]
        }
    ],
    
    # 6 STANDARD BONUSES
    "bonuses": [
        {"type": "cookbook", "title": "The Wellness Cookbook", "min_words": 2000},
        {"type": "worksheet", "title": "Practice Worksheets", "min_words": 1500},
        {"type": "reference_card", "title": "Quick Reference Cards", "min_words": 1200},
        {"type": "meditation", "title": "Guided Meditation Scripts", "min_words": 2000},
        {"type": "journal", "title": "90-Day Transformation Journal", "min_words": 1500},
        {"type": "checklist", "title": "Action Checklists", "min_words": 1200},
    ],
    
    "voice_rules": """
- Vary sentence length: mix short punchy sentences with longer flowing ones
- Use fragments for emphasis. Like this.
- No more than 3 sentences of similar length in a row
- Start some sentences with 'And' or 'But' for conversational feel
- Include rhetorical questions to engage the reader
- Use specific numbers and examples, not vague generalities
- Write like you're having coffee with a friend who asked for help
- Be direct. Don't hedge. Stand behind your recommendations.
""",

    "chapter_template": """
You are a team of 4 expert writers working together to create one exceptional chapter:
- **Head Writer (The Architect)**: Structure, voice, core promise
- **Story Producer (The Storyteller)**: Narrative hooks, emotional arcs, memorable moments
- **Teacher (The Pedagogue)**: Clarity, examples, exercises, misconception handling
- **Line Editor (The Polisher)**: Tight prose, remove fluff, make every word count

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
- Open with a **story or scene** that illustrates the problem
- Build to a **"Here's what I discovered"** moment
- Deliver the main teaching in a clear framework
- Close with **specific action steps**
- Target: 1,800-2,200 words

### 2. NARRATIVE (Storyteller Pass)
- The opening hook must make someone WANT to keep reading
- Use the "And then... But then... Therefore..." structure for tension
- Create at least TWO "aha moments" that the reader will remember
- Include a client/reader story or case study (can be composite)

### 3. TEACHING (Teacher Pass)
- Explain the "How" and "Why", not just "What"
- Include at least 3 **worked examples** with specific details
- Add 2-3 practical **action steps** the reader can do TODAY
- Address the most common misconception about this topic

### 4. POLISH (Editor Pass)
- Cut any sentence that doesn't earn its place
- Replace passive voice with active
- Check that every paragraph has a clear purpose
- Ensure smooth transitions between sections

---

## Voice Rules
{voice_rules}

---

## Quality Checklist

### Content Rubric
□ Purpose Achieved: Does this chapter deliver on its stated purpose?
□ Story Hook: Does the opening grab attention immediately?
□ Worked Examples: Are there at least 3 concrete, specific examples?
□ Actionable: Can the reader immediately apply this?
□ Misconception Coverage: Are common errors addressed?
□ Transfer: Can the reader use this in their life?

### Delight Rubric
□ Enjoyment: Would someone finish this willingly?
□ Depth: Does it go beyond surface-level advice?
□ Originality: Is there a unique perspective or fresh insight?
□ Resonance: Will the reader feel something meaningful?

---

## Output Format

Output the complete chapter in Markdown format:
- Use ## for section headers
- Use ### for subsections
- Use **bold** for key terms
- Use lists for action steps
- Include specific numbers, examples, and stories

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

Add {words_to_add} words of NEW content to this chapter. You may:

1. **Add More Examples**: Include 2-3 additional worked examples with specific details
2. **Expand Existing Sections**: Go deeper into concepts that were briefly covered
3. **Add Case Studies**: Include real-world scenarios showing the concept in action
4. **Address More Objections**: Cover additional "but what about..." concerns
5. **Add Action Steps**: More specific implementation guidance

**Quality Requirements:**
- Every sentence must add value (no fluff or padding)
- Maintain the existing voice and tone
- Use specific numbers, examples, and stories
- Make content immediately actionable

**Output Format:**
Return ONLY the new content to be added (not the entire chapter).
Format as markdown that can be inserted after the existing content.
Begin each new section with ## or ### headers.
""",

    # BONUS GENERATION TEMPLATE
    "bonus_template": """## Generate Research-Backed Bonus Content

**Bonus Type:** {bonus_type}
**Title:** {bonus_title}
**Minimum Words:** {min_words}

---

## Product Context

**Product Title:** {title}
**Core Topic:** {topic}
**Target Audience:** {audience}
**Core Thesis:** {thesis}

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

Write the complete bonus content now. Use # for main chapters (each starts new page in PDF).
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
        response_file = responses_dir / f"chapter_{chapter['number']:02d}*.response.md"
        matching = list(responses_dir.glob(f"chapter_{chapter['number']:02d}*.response.md"))
        
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
    
    # Validate page count
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


def generate_expansion_prompts(config: dict, validation: dict, output_dir: Path):
    """Generate expansion prompts for thin chapters."""
    expansion_dir = output_dir / "expansion_prompts"
    expansion_dir.mkdir(exist_ok=True)
    
    stats = validation["stats"]
    
    if stats.meets_minimum:
        print("\n✅ No expansion needed - content meets page minimum.")
        return
    
    print(f"\n📋 GENERATING EXPANSION PROMPTS")
    print("=" * 50)
    
    thin_chapters = [
        (i, ch_stats) 
        for i, ch_stats in enumerate(stats.chapter_stats) 
        if ch_stats['words'] < MIN_WORDS_PER_CHAPTER
    ]
    
    for idx, ch_stats in thin_chapters:
        chapter = validation["chapters"][idx]
        words_to_add = TARGET_WORDS_PER_CHAPTER - ch_stats['words']
        
        prompt = config["expansion_template"].format(
            chapter_title=chapter["title"],
            current_words=ch_stats['words'],
            target_words=TARGET_WORDS_PER_CHAPTER,
            words_to_add=words_to_add,
            content_summary=chapter["content"][:500] + "..." if len(chapter["content"]) > 500 else chapter["content"]
        )
        
        filename = f"expand_ch{idx+1:02d}_{chapter['title'].lower().replace(' ', '_')}.prompt.md"
        prompt_path = expansion_dir / filename
        prompt_path.write_text(prompt)
        print(f"   📋 {filename} (need +{words_to_add} words)")
    
    print(f"\n📂 Expansion prompts saved to: {expansion_dir}")
    print("💡 Generate responses and add them to the chapter files, then re-run validation.")


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


def show_workflow_status(config: dict, output_dir: Path):
    """Show the current workflow status and next steps."""
    responses_dir = output_dir / "responses"
    bonuses_dir = output_dir / "bonuses" / "responses"
    
    print("\n" + "=" * 60)
    print("📊 WORKFLOW STATUS")
    print("=" * 60)
    
    # Check chapters
    chapter_responses = list(responses_dir.glob("*.response.md")) if responses_dir.exists() else []
    print(f"\n📕 MAIN CHAPTERS: {len(chapter_responses)}/{len(config['chapters'])}")
    
    if len(chapter_responses) == len(config["chapters"]):
        print("   ✅ All chapters generated")
        # Validate
        validation = validate_responses(config, responses_dir)
        if validation["needs_expansion"]:
            print("   ⚠️ Some chapters need expansion")
    else:
        print(f"   ⏳ Generate remaining {len(config['chapters']) - len(chapter_responses)} chapters")
    
    # Check bonuses
    bonus_responses = list(bonuses_dir.glob("*.md")) if bonuses_dir.exists() else []
    print(f"\n🎁 BONUSES: {len(bonus_responses)}/{len(config['bonuses'])}")
    
    if len(bonus_responses) == len(config["bonuses"]):
        print("   ✅ All bonuses generated")
    else:
        print(f"   ⏳ Generate remaining {len(config['bonuses']) - len(bonus_responses)} bonuses")
    
    # Show next steps
    print("\n📋 NEXT STEPS:")
    if len(chapter_responses) < len(config["chapters"]):
        print("   1. Feed chapter prompts to LLM → save to responses/")
    elif validation.get("needs_expansion"):
        print("   1. Feed expansion prompts to LLM → add to chapters")
    elif len(bonus_responses) < len(config["bonuses"]):
        print("   1. Feed bonus prompts to LLM → save to bonuses/responses/")
    else:
        print("   1. Run compilation to build PDFs")
        print("   2. Generate images if not done")
        print("   3. Package final zip")


def main():
    """Main entry point."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RESPONSES_DIR.mkdir(exist_ok=True)
    
    print("=" * 60)
    print("🌿 HOLISTIC WELLNESS PROTOCOL - PRODUCT GENERATOR")
    print("=" * 60)
    print(f"\n📕 {PRODUCT_CONFIG['title']}")
    print(f"📝 {len(PRODUCT_CONFIG['chapters'])} chapters planned")
    print(f"🎁 {len(PRODUCT_CONFIG['bonuses'])} bonuses planned")
    print(f"🎯 Target: {MIN_PAGES_MAIN_PRODUCT}+ pages ({MIN_WORDS_PER_CHAPTER}+ words/chapter)")
    
    # Step 1: Generate chapter prompts
    generate_chapter_prompts(PRODUCT_CONFIG, OUTPUT_DIR)
    
    # Step 2: Check for existing responses and validate
    existing_responses = list(RESPONSES_DIR.glob("*.response.md"))
    if existing_responses:
        print(f"\n📄 Found {len(existing_responses)} existing chapter responses")
        validation = validate_responses(PRODUCT_CONFIG, RESPONSES_DIR)
        
        # Step 3: Generate expansion prompts if needed
        if validation["needs_expansion"]:
            generate_expansion_prompts(PRODUCT_CONFIG, validation, OUTPUT_DIR)
    
    # Step 4: Generate bonus prompts
    generate_bonus_prompts(PRODUCT_CONFIG, OUTPUT_DIR)
    
    # Step 5: Show overall status
    show_workflow_status(PRODUCT_CONFIG, OUTPUT_DIR)


if __name__ == "__main__":
    main()

