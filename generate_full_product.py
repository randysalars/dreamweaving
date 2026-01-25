#!/usr/bin/env python3
"""
Full Product Generator for Antigravity-Native Mode

This script generates a complete product with:
- 10-12 chapters
- 1,500+ words per chapter (15,000+ total)
- 100+ pages in final PDF
- Quality checks embedded in prompts
- Visual requirements

Usage:
1. Run this script to generate prompts
2. Read prompts and generate content (as Antigravity)
3. Run compile step to create final PDF
"""

import json
from pathlib import Path
from datetime import datetime

# ═══════════════════════════════════════════════════════════════
# PRODUCT CONFIGURATION
# ═══════════════════════════════════════════════════════════════

PRODUCT_CONFIG = {
    "title": "Financial Freedom Blueprint",
    "author": "Randy Salars",
    "topic": "Personal Finance and Wealth Building",
    "promise": "Transform your relationship with money and build lasting wealth through proven systems",
    "audience": "Working professionals who feel stuck financially and want a clear path to financial independence",
    "thesis": "Financial freedom isn't about earning more money—it's about building systems that make wealth automatic",
    
    # 10+ CHAPTERS - This is the key change!
    "chapters": [
        {
            "number": 1,
            "title": "The Money Lie",
            "purpose": "Shatter the myths about budgeting and reveal why most financial advice fails",
            "takeaways": [
                "Why willpower-based budgeting always fails",
                "The architecture mindset vs. restriction mindset",
                "How the wealthy actually think about money"
            ]
        },
        {
            "number": 2,
            "title": "Know Your Numbers",
            "purpose": "Complete financial assessment and net worth calculation",
            "takeaways": [
                "Calculate your true monthly cost of living",
                "Determine your net worth (the only metric that matters)",
                "Identify your money leaks and unconscious spending"
            ]
        },
        {
            "number": 3,
            "title": "The Zero-Based System",
            "purpose": "Master zero-based budgeting where every dollar has a job",
            "takeaways": [
                "The Income - Allocations = Zero formula",
                "Setting up budget categories that work",
                "Permission spending vs. restriction spending"
            ]
        },
        {
            "number": 4,
            "title": "Account Architecture",
            "purpose": "Set up the multi-account system for automatic money flow",
            "takeaways": [
                "The four-account system explained",
                "Why separation creates clarity",
                "Choosing the right banks and accounts"
            ]
        },
        {
            "number": 5,
            "title": "Automation Mastery",
            "purpose": "Wire your finances to run without daily decisions",
            "takeaways": [
                "The paycheck cascade automation",
                "Setting up automatic bill pay",
                "Auto-invest configuration"
            ]
        },
        {
            "number": 6,
            "title": "Emergency Fund Architecture",
            "purpose": "Build your financial shock absorber the right way",
            "takeaways": [
                "How much you actually need (based on your situation)",
                "Where to keep your emergency fund",
                "The psychology of financial security"
            ]
        },
        {
            "number": 7,
            "title": "Sinking Funds Strategy",
            "purpose": "Eliminate surprise expenses forever",
            "takeaways": [
                "Identifying predictable irregular expenses",
                "Setting up and funding sinking funds",
                "Managing multiple savings goals"
            ]
        },
        {
            "number": 8,
            "title": "Debt Destruction Protocol",
            "purpose": "Systematic approach to eliminating debt",
            "takeaways": [
                "Avalanche vs. Snowball method (which is right for you)",
                "Debt payoff automation",
                "Staying motivated during the debt journey"
            ]
        },
        {
            "number": 9,
            "title": "Investment Essentials",
            "purpose": "The simple investment strategy that beats 80% of professionals",
            "takeaways": [
                "Index funds and why they work",
                "Tax-advantaged accounts explained",
                "The power of consistent investing"
            ]
        },
        {
            "number": 10,
            "title": "The Freedom Number",
            "purpose": "Calculate exactly when you can stop working",
            "takeaways": [
                "The 4% rule and your magic number",
                "Accelerating toward financial independence",
                "The milestone markers on your journey"
            ]
        },
        {
            "number": 11,
            "title": "Income Expansion",
            "purpose": "Grow your earning power strategically",
            "takeaways": [
                "Salary negotiation tactics",
                "High-value skill development",
                "Side income streams that scale"
            ]
        },
        {
            "number": 12,
            "title": "The Wealth Mindset",
            "purpose": "The psychology that separates the wealthy from the struggling",
            "takeaways": [
                "Escaping the hedonic treadmill",
                "Identity-based financial habits",
                "Building generational wealth thinking"
            ]
        }
    ],
    
    "voice_rules": """
- Vary sentence length: mix short punchy sentences with longer flowing ones
- Use fragments for emphasis. Like this.
- No more than 3 sentences of similar length in a row
- Start some sentences with 'And' or 'But' for conversational feel
- End sections with short, memorable statements
- Include specific numbers and examples (not vague generalities)
- Use stories to illustrate concepts
- Include at least one memorable quote per chapter
""",
    
    "banned_phrases": [
        "In today's fast-paced world",
        "It's important to note",
        "Let's dive in",
        "Without further ado",
        "In conclusion",
        "First and foremost",
        "At the end of the day"
    ]
}

# ═══════════════════════════════════════════════════════════════
# PROMPT TEMPLATE
# ═══════════════════════════════════════════════════════════════

CHAPTER_PROMPT_TEMPLATE = """# Complete Chapter Generation Prompt

You are a team of 4 expert writers working together to create one exceptional chapter:
- **Head Writer (The Architect)**: Structure, voice, core promise
- **Story Producer (The Storyteller)**: Narrative hooks, emotional arcs, memorable moments
- **Teacher (The Pedagogue)**: Clarity, examples, exercises, misconception handling
- **Line Editor (The Polisher)**: Tight prose, remove fluff, make every word count

---

## Product Context

**Product:** {title}
**Promise:** {promise}
**Target Audience:** {audience}
**Core Thesis:** {thesis}

---

## Chapter Assignment

**Chapter Number:** {chapter_number}
**Chapter Title:** {chapter_title}
**Purpose:** {chapter_purpose}

**Key Takeaways the Reader Must Walk Away With:**
{takeaways}

---

## Voice & Style Rules

{voice_rules}

**Banned Phrases (Never Use):**
{banned_phrases}

---

## Writing Instructions

### 1. STRUCTURE (Head Writer Pass)
- Start with a **pattern interrupt** - a bold statement, surprising statistic, or question that stops the scroll
- Create a clear **spine** - logical flow from opening hook to satisfying close
- Break into 5-7 distinct sections with clear H2 headers
- Include at least ONE table or formatted list for scanability
- End the chapter with a memorable, quotable line

### 2. STORY (Story Producer Pass)
- Open the chapter with a **micro-story** - a named person with a specific problem
- Build **emotional momentum** - the reader should feel something (frustration, hope, realization)
- Use the "And then... But then... Therefore..." structure for tension
- Create at least TWO "aha moments" that the reader will remember
- Include a customer/reader story or case study

### 3. TEACHING (Teacher Pass)
- Explain the "How" and "Why", not just "What"
- Include at least 3 **worked examples** with specific numbers and details
- Add 2-3 practical **action steps** the reader can do TODAY
- Address the most common misconception about this topic
- Include a checklist or worksheet element

### 4. POLISH (Editor Pass)
- Vary sentence length (short punches mixed with flowing explanations)
- Remove weasel words: "very", "really", "just", "actually", "basically"
- No fluff paragraphs - if a paragraph doesn't add value, cut it
- Check that every section delivers on its promise
- Ensure smooth transitions between sections

---

## Quality Requirements

**CRITICAL: Minimum Word Count: 2,000 words**
**Maximum Word Count: 3,500 words**

Before submitting, you MUST self-evaluate against these criteria (all must score 7+/10):

### Story Rubric
□ Hook Strength: Does the opening grab attention immediately?
□ Emotional Movement: Does the reader feel something?
□ Coherence: Does the narrative flow logically?
□ Memorability: Is there a concept that will stick?
□ Momentum: Does it drive the reader forward?

### Teaching Rubric
□ Clarity: Is every concept explained simply?
□ Worked Examples: Are there at least 3 concrete, specific examples?
□ Actionable: Can the reader immediately apply this?
□ Misconception Coverage: Are common errors addressed?
□ Transfer: Can the reader use this in their life?

### Delight Rubric
□ Enjoyment: Would someone finish this willingly?
□ Depth: Does it go beyond surface-level advice?
□ Originality: Is there a unique perspective or voice?
□ Resonance: Will the reader feel something meaningful?

**If any axis scores below 7, revise before outputting.**

---

## Output Format

Return the complete chapter in clean Markdown:
- Use ## for main section headers
- Use ### for sub-sections
- Use **bold** for key terms on first introduction
- Use > blockquotes for memorable quotes or key principles
- Use - bullets for lists (not *)
- Include at least one table
- NO code blocks wrapping the content

---

## Begin Writing

Write the complete Chapter {chapter_number}: {chapter_title} now.
Remember: 2,000-3,500 words, 5-7 sections, all quality checks passing.
"""

# ═══════════════════════════════════════════════════════════════
# GENERATOR FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def generate_prompts(config: dict, output_dir: Path):
    """Generate all chapter prompts."""
    prompts_dir = output_dir / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    
    responses_dir = output_dir / "responses"
    responses_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📝 Generating {len(config['chapters'])} chapter prompts...")
    
    for chapter in config["chapters"]:
        # Format takeaways
        takeaways = "\n".join([f"- {t}" for t in chapter["takeaways"]])
        banned = ", ".join([f'"{p}"' for p in config["banned_phrases"]])
        
        prompt = CHAPTER_PROMPT_TEMPLATE.format(
            title=config["title"],
            promise=config["promise"],
            audience=config["audience"],
            thesis=config["thesis"],
            chapter_number=chapter["number"],
            chapter_title=chapter["title"],
            chapter_purpose=chapter["purpose"],
            takeaways=takeaways,
            voice_rules=config["voice_rules"],
            banned_phrases=banned
        )
        
        # Add metadata header
        slug = f"chapter_{chapter['number']:02d}_{chapter['title'].lower().replace(' ', '_')}"
        full_prompt = f"""# Prompt: {slug}
Generated: {datetime.now().isoformat()}

## Instructions for Antigravity

Read this prompt carefully and generate the requested content.
Write your response to: `{responses_dir}/{slug}.response.md`

---

{prompt}

---

## Response Instructions

After generating your response:
1. Create the file: `{responses_dir}/{slug}.response.md`
2. Write ONLY the generated content (no markdown wrappers).
3. After all chapters are complete, run the compile step.
"""
        
        prompt_path = prompts_dir / f"{slug}.prompt.md"
        prompt_path.write_text(full_prompt)
        print(f"   ✅ {prompt_path.name}")
    
    # Save config for compile step
    config_path = output_dir / "product_config.json"
    config_path.write_text(json.dumps(config, indent=2))
    
    print(f"\n📊 Summary:")
    print(f"   Chapters: {len(config['chapters'])}")
    print(f"   Target Words: {len(config['chapters']) * 2500} (~2,500/chapter)")
    print(f"   Target Pages: {len(config['chapters']) * 2500 // 250} (~250 words/page)")
    print(f"   Prompts Dir: {prompts_dir}")
    
    print(f"\n🚀 Next Steps:")
    print(f"   1. Read each prompt in {prompts_dir}")
    print(f"   2. Generate chapter content")
    print(f"   3. Save responses to {responses_dir}")
    print(f"   4. Run: python generate_full_product.py --compile")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Full Product Generator")
    parser.add_argument("--output", default="products/financial_freedom_blueprint/output", help="Output directory")
    parser.add_argument("--compile", action="store_true", help="Compile responses into final PDF")
    args = parser.parse_args()
    
    output_dir = Path(args.output)
    
    if args.compile:
        print("🔧 Compile mode - generating PDF from responses...")
        compile_product(output_dir)
    else:
        print("📝 Generate mode - creating chapter prompts...")
        generate_prompts(PRODUCT_CONFIG, output_dir)


def compile_product(output_dir: Path):
    """Compile responses into final PDF."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    
    from agents.product_builder.packaging.pdf_generator import PDFGenerator, PDFConfig
    
    config_path = output_dir / "product_config.json"
    responses_dir = output_dir / "responses"
    
    if not config_path.exists():
        print(f"❌ Config not found: {config_path}")
        return
    
    config = json.loads(config_path.read_text())
    
    # Load all responses
    chapters = []
    total_words = 0
    
    for ch in config["chapters"]:
        slug = f"chapter_{ch['number']:02d}_{ch['title'].lower().replace(' ', '_')}"
        resp_path = responses_dir / f"{slug}.response.md"
        
        if resp_path.exists():
            content = resp_path.read_text().strip()
            word_count = len(content.split())
            total_words += word_count
            
            chapters.append({
                "title": f"Chapter {ch['number']}: {ch['title']}",
                "purpose": ch["purpose"],
                "content": content,
                "key_takeaways": ch["takeaways"]
            })
            print(f"   ✅ {slug}: {word_count} words")
        else:
            print(f"   ⚠️ Missing: {resp_path.name}")
    
    print(f"\n📊 Total: {len(chapters)} chapters, {total_words} words")
    
    if len(chapters) < 10:
        print(f"⚠️ Warning: Less than 10 chapters. Product may be too short.")
    
    if total_words < 15000:
        print(f"⚠️ Warning: Less than 15,000 words. Product may not reach 100 pages.")
    
    # Generate PDF
    pdf_config = PDFConfig(
        title=config["title"],
        author=config["author"],
        output_path=str(output_dir / f"{config['title'].replace(' ', '_')}.pdf")
    )
    
    pdf_gen = PDFGenerator()
    pdf_path = pdf_gen.generate(chapters, pdf_config, visuals={})
    print(f"\n✅ PDF Generated: {pdf_path}")


if __name__ == "__main__":
    main()
