"""
Content Expander
Validates page counts and iteratively expands content until targets are met.

This module ensures main products meet the 100+ page minimum through:
1. Page count validation
2. Identification of thin chapters
3. Iterative expansion with research-backed content
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# CONFIGURATION CONSTANTS
# ═══════════════════════════════════════════════════════════════

# Page calculation (approximate)
WORDS_PER_PAGE = 250  # Standard for printed material

# Main product thresholds
MIN_PAGES_MAIN_PRODUCT = 100
MIN_WORDS_PER_CHAPTER = 1800
TARGET_WORDS_PER_CHAPTER = 2200
MAX_EXPANSION_ITERATIONS = 5

# Bonus content thresholds
MIN_WORDS_PER_BONUS = 1000
MIN_PAGES_PER_BONUS = 8
NUM_REQUIRED_BONUSES = 6


# ═══════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════

@dataclass
class PageStats:
    """Statistics about content page count."""
    total_words: int
    estimated_pages: int
    meets_minimum: bool
    chapter_stats: List[Dict[str, Any]]
    thin_chapters: List[int]  # Indices of chapters below MIN_WORDS


@dataclass
class ExpansionResult:
    """Result of an expansion operation."""
    original_pages: int
    final_pages: int
    iterations_used: int
    chapters_expanded: List[str]
    success: bool


# ═══════════════════════════════════════════════════════════════
# VALIDATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def count_words(text: str) -> int:
    """Count words in text."""
    if not text:
        return 0
    return len(text.split())


def estimate_pages(chapters: List[Dict[str, Any]]) -> int:
    """Estimate page count from chapters."""
    total_words = sum(count_words(ch.get('content', '')) for ch in chapters)
    # Add overhead for headers, spacing, images (~15%)
    adjusted_words = total_words * 0.85
    return max(1, int(adjusted_words / WORDS_PER_PAGE))


def validate_page_count(chapters: List[Dict[str, Any]], min_pages: int = MIN_PAGES_MAIN_PRODUCT) -> PageStats:
    """
    Validate that chapters meet the minimum page count.
    
    Args:
        chapters: List of chapter dicts with 'title' and 'content'
        min_pages: Minimum required pages
        
    Returns:
        PageStats with validation results
    """
    chapter_stats = []
    thin_chapters = []
    total_words = 0
    
    for i, chapter in enumerate(chapters):
        content = chapter.get('content', '')
        word_count = count_words(content)
        total_words += word_count
        
        stats = {
            'index': i,
            'title': chapter.get('title', f'Chapter {i+1}'),
            'words': word_count,
            'pages': max(1, word_count // WORDS_PER_PAGE),
            'meets_minimum': word_count >= MIN_WORDS_PER_CHAPTER
        }
        chapter_stats.append(stats)
        
        if word_count < MIN_WORDS_PER_CHAPTER:
            thin_chapters.append(i)
    
    estimated_pages = max(1, int(total_words * 0.85 / WORDS_PER_PAGE))
    
    return PageStats(
        total_words=total_words,
        estimated_pages=estimated_pages,
        meets_minimum=estimated_pages >= min_pages,
        chapter_stats=chapter_stats,
        thin_chapters=thin_chapters
    )


def identify_expansion_opportunities(stats: PageStats, target_pages: int = MIN_PAGES_MAIN_PRODUCT) -> List[Tuple[int, int]]:
    """
    Identify which chapters should be expanded and by how much.
    
    Returns:
        List of (chapter_index, target_words) tuples
    """
    if stats.meets_minimum:
        return []
    
    # Calculate how many more words we need
    pages_needed = target_pages - stats.estimated_pages
    words_needed = pages_needed * WORDS_PER_PAGE
    
    opportunities = []
    
    # First: expand thin chapters to minimum
    for idx in stats.thin_chapters:
        current_words = stats.chapter_stats[idx]['words']
        target = TARGET_WORDS_PER_CHAPTER
        if current_words < target:
            opportunities.append((idx, target))
            words_needed -= (target - current_words)
    
    # If still need more, expand all chapters proportionally
    if words_needed > 0:
        chapters_to_expand = len(stats.chapter_stats) - len(opportunities)
        if chapters_to_expand > 0:
            words_per_chapter = words_needed // chapters_to_expand
            for i, ch_stats in enumerate(stats.chapter_stats):
                if i not in [o[0] for o in opportunities]:
                    current = ch_stats['words']
                    opportunities.append((i, current + words_per_chapter))
    
    return opportunities


# ═══════════════════════════════════════════════════════════════
# EXPANSION FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def generate_expansion_prompt(chapter: Dict[str, Any], target_words: int, product_context: Dict[str, Any]) -> str:
    """
    Generate a prompt to expand a chapter.
    
    Args:
        chapter: Chapter dict with title, content, purpose
        target_words: Target word count
        product_context: Product title, thesis, audience
        
    Returns:
        Expansion prompt string
    """
    current_words = count_words(chapter.get('content', ''))
    words_to_add = max(200, target_words - current_words)
    
    return f"""## Chapter Expansion Task

You are expanding an existing chapter to add more depth and value.

**Product:** {product_context.get('title', 'Digital Product')}
**Audience:** {product_context.get('audience', 'General readers')}

**Chapter:** {chapter.get('title', 'Chapter')}
**Purpose:** {chapter.get('purpose', 'See content below')}

**Current Word Count:** {current_words} words
**Target Word Count:** {target_words} words
**Words to Add:** ~{words_to_add} words

---

## Current Chapter Content

{chapter.get('content', '')[:3000]}...

---

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
"""


def generate_bonus_expansion_prompt(bonus_type: str, topic: str, current_content: str = "") -> str:
    """
    Generate a prompt to create or expand bonus content.
    
    Args:
        bonus_type: Type of bonus (cookbook, worksheet, reference_card, etc.)
        topic: Main product topic
        current_content: Existing content if expanding
        
    Returns:
        Bonus generation prompt
    """
    bonus_templates = {
        'cookbook': """Create a practical recipe/meal guide with:
- Introduction explaining the approach
- Weekly shopping lists with costs
- Complete recipes with ingredients, steps, timing
- Protein and nutrition information
- Meal prep guide
Target: 2000+ words of genuinely useful content""",
        
        'worksheet': """Create structured worksheets/assessments with:
- Clear instructions for each exercise
- Fill-in-the-blank sections with context
- Self-assessment rubrics with specific criteria  
- Planning templates with examples
- Progress tracking sections
Target: 1500+ words covering 5-6 worksheets""",
        
        'reference_card': """Create quick reference cards covering:
- Protocol summaries (morning, evening, etc.)
- Key metrics and targets
- Quick-reference tables
- Emergency tools and techniques
- Phase transition guides
Target: 1200+ words across 6-8 topic cards""",
        
        'meditation': """Create complete guided meditation scripts with:
- Clear timing and pacing notes
- Word-for-word scripts (not summaries)
- Pause indicators (...)
- 5 distinct meditations for different purposes
Target: 2000+ words of actual scripts""",
        
        'journal': """Create a structured journaling system with:
- Daily prompts based on research (reflection, gratitude, intention)
- Weekly review templates
- Monthly assessment frameworks
- Prompts for challenging situations
- 30+ days of unique prompts
Target: 1500+ words""",
        
        'checklist': """Create phase-based checklists with:
- Action items organized by timeframe
- Success criteria for each item
- Common obstacles and solutions
- Progress tracking mechanisms
Target: 1200+ words"""
    }
    
    template = bonus_templates.get(bonus_type, bonus_templates['worksheet'])
    
    prompt = f"""## Research-Backed Bonus Content Generation

**Topic:** {topic}
**Bonus Type:** {bonus_type.replace('_', ' ').title()}

---

## Requirements

{template}

---

## Quality Standards

1. **Substantive Content**: Every section must provide genuine value, not padding
2. **Research-Backed**: Include specific techniques, numbers, and evidence where applicable
3. **Actionable**: Reader can use this content immediately
4. **Well-Organized**: Clear chapter structure with proper markdown headings
5. **Professional**: Publication-ready quality

---

## Structure

Use this heading structure:
- `#` for major chapters/sections (each starts new page)
- `##` for sections within chapters
- `###` for subsections
- Bold for key terms

---

## Output

Write the complete bonus content now. Remember: This must be genuinely valuable content that someone would want to reference repeatedly, not filler material.
"""
    
    return prompt


# ═══════════════════════════════════════════════════════════════
# EXPANSION LOOP
# ═══════════════════════════════════════════════════════════════

def run_expansion_loop(
    chapters: List[Dict[str, Any]], 
    product_context: Dict[str, Any],
    min_pages: int = MIN_PAGES_MAIN_PRODUCT,
    max_iterations: int = MAX_EXPANSION_ITERATIONS,
    expansion_callback=None
) -> ExpansionResult:
    """
    Run the iterative expansion loop until page target is met.
    
    Args:
        chapters: List of chapter dicts
        product_context: Product metadata (title, thesis, audience)
        min_pages: Minimum pages required
        max_iterations: Maximum expansion attempts
        expansion_callback: Optional function(chapter, prompt) that returns expanded content
        
    Returns:
        ExpansionResult with details
    """
    original_stats = validate_page_count(chapters, min_pages)
    logger.info(f"📊 Initial: {original_stats.estimated_pages} pages, {original_stats.total_words} words")
    
    if original_stats.meets_minimum:
        logger.info("✅ Content already meets minimum page requirement")
        return ExpansionResult(
            original_pages=original_stats.estimated_pages,
            final_pages=original_stats.estimated_pages,
            iterations_used=0,
            chapters_expanded=[],
            success=True
        )
    
    chapters_expanded = []
    
    for iteration in range(max_iterations):
        logger.info(f"🔄 Expansion iteration {iteration + 1}/{max_iterations}")
        
        stats = validate_page_count(chapters, min_pages)
        if stats.meets_minimum:
            logger.info(f"✅ Target reached: {stats.estimated_pages} pages")
            break
            
        opportunities = identify_expansion_opportunities(stats, min_pages)
        
        if not opportunities:
            logger.warning("⚠️ No expansion opportunities found")
            break
            
        for idx, target_words in opportunities[:3]:  # Expand up to 3 chapters per iteration
            chapter = chapters[idx]
            title = chapter.get('title', f'Chapter {idx+1}')
            
            if expansion_callback:
                prompt = generate_expansion_prompt(chapter, target_words, product_context)
                expansion = expansion_callback(chapter, prompt)
                if expansion:
                    chapters[idx]['content'] = chapter.get('content', '') + '\n\n' + expansion
                    chapters_expanded.append(title)
                    logger.info(f"   📝 Expanded: {title}")
            else:
                # In prompts-only mode, just log what would happen
                logger.info(f"   📋 Would expand: {title} (target: {target_words} words)")
                chapters_expanded.append(f"{title} (prompt generated)")
    
    final_stats = validate_page_count(chapters, min_pages)
    
    return ExpansionResult(
        original_pages=original_stats.estimated_pages,
        final_pages=final_stats.estimated_pages,
        iterations_used=iteration + 1,
        chapters_expanded=chapters_expanded,
        success=final_stats.meets_minimum
    )


# ═══════════════════════════════════════════════════════════════
# BONUS VALIDATION
# ═══════════════════════════════════════════════════════════════

@dataclass
class BonusValidation:
    """Validation result for bonus content."""
    bonus_name: str
    word_count: int
    estimated_pages: int
    meets_minimum: bool
    issues: List[str]


def validate_bonus_content(bonus_name: str, content: str) -> BonusValidation:
    """
    Validate that bonus content meets minimum requirements.
    
    Args:
        bonus_name: Name of the bonus
        content: Full text content
        
    Returns:
        BonusValidation result
    """
    words = count_words(content)
    pages = max(1, int(words * 0.85 / WORDS_PER_PAGE))
    issues = []
    
    if words < MIN_WORDS_PER_BONUS:
        issues.append(f"Below minimum words ({words} < {MIN_WORDS_PER_BONUS})")
    
    if pages < MIN_PAGES_PER_BONUS:
        issues.append(f"Below minimum pages ({pages} < {MIN_PAGES_PER_BONUS})")
    
    # Check for padding indicators
    lines = content.split('\n')
    empty_ratio = sum(1 for l in lines if not l.strip()) / max(1, len(lines))
    if empty_ratio > 0.3:
        issues.append(f"High empty line ratio ({empty_ratio:.0%}) - possible padding")
    
    return BonusValidation(
        bonus_name=bonus_name,
        word_count=words,
        estimated_pages=pages,
        meets_minimum=len(issues) == 0,
        issues=issues
    )


def validate_all_bonuses(bonuses: Dict[str, str]) -> Tuple[bool, List[BonusValidation]]:
    """
    Validate all bonus content.
    
    Args:
        bonuses: Dict of bonus_name -> content
        
    Returns:
        (all_valid, list of BonusValidation results)
    """
    results = []
    all_valid = True
    
    for name, content in bonuses.items():
        validation = validate_bonus_content(name, content)
        results.append(validation)
        if not validation.meets_minimum:
            all_valid = False
            logger.warning(f"⚠️ Bonus '{name}' has issues: {validation.issues}")
    
    if len(bonuses) < NUM_REQUIRED_BONUSES:
        all_valid = False
        logger.warning(f"⚠️ Only {len(bonuses)} bonuses provided, need {NUM_REQUIRED_BONUSES}")
    
    return all_valid, results
