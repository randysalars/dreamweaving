#!/usr/bin/env python3
"""
Full Product Generator for Holistic Wellness Protocol

This script follows the EXACT same process that created Financial Freedom Blueprint:
- 12 chapters
- 1,500+ words per chapter (18,000+ total)
- 100+ pages in final PDF
- Quality checks embedded in prompts

Usage:
    python3 generate_wellness_product.py

This generates prompts, which can be fed to the LLM to create full chapter content.
"""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

OUTPUT_DIR = Path("products/holistic_wellness_protocol/output")
RESPONSES_DIR = OUTPUT_DIR / "responses"

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
"""
}

# ═══════════════════════════════════════════════════════════════
# GENERATOR FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def generate_prompts(config: dict, output_dir: Path):
    """Generate all chapter prompts."""
    prompts_dir = output_dir / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📝 Generating {len(config['chapters'])} chapter prompts...")
    
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
    print("\n💡 NEXT STEP: Feed these prompts to your LLM to generate chapter content.")
    print("   Save responses to: products/holistic_wellness_protocol/output/responses/")


def main():
    """Main entry point."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RESPONSES_DIR.mkdir(exist_ok=True)
    
    print("=" * 60)
    print("🌿 HOLISTIC WELLNESS PROTOCOL - PRODUCT GENERATOR")
    print("=" * 60)
    print(f"\n📕 {PRODUCT_CONFIG['title']}")
    print(f"📝 {len(PRODUCT_CONFIG['chapters'])} chapters planned")
    print(f"🎯 Target: 18,000+ words (100+ pages)")
    
    # Generate prompts
    generate_prompts(PRODUCT_CONFIG, OUTPUT_DIR)
    
    # Check if responses already exist
    existing_responses = list(RESPONSES_DIR.glob("*.response.md"))
    if existing_responses:
        print(f"\n📄 Found {len(existing_responses)} existing responses!")
        print("   Run compile step to build PDF.")


if __name__ == "__main__":
    main()
