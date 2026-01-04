# Batch Answer Page Automation System

## Overview

This system automates the generation of answer pages for the Answer Engine Optimization (AEO) content strategy. It can generate **250+ pages** across 3 topics (Altered States, Meditation, Memory Systems) using either:

1. **Claude API** - Automatic content generation (~$1.10 for 110 pages, 15 minutes)
2. **Template Mode** - Structured placeholders for manual filling (current default)

## Quick Start

### Current Status
- ✅ **Altered States**: 3/124 complete (2.4%)
  - 111 pages with structured placeholders ready for filling
  - 10 pages not yet generated (missing from YAML)
  - 3 pages manually completed (dreams, hypnosis, flow state)

### Option 1: Continue Manual Filling (Current Approach)

Use the tracking script to see which pages to fill next:

```bash
python3 scripts/generation/track_content_progress.py --next 10
```

Then manually edit the placeholder pages with real content following the AEO template.

### Option 2: Use Claude API for Automatic Content

**Cost**: ~$1.10 for all 111 remaining pages
**Time**: ~15 minutes with 4 concurrent threads

#### Setup (One-Time)

1. Get Claude API key from https://console.anthropic.com/
2. Set environment variable:
   ```bash
   export ANTHROPIC_API_KEY="your-key-here"
   ```
3. Install anthropic package (if not already installed):
   ```bash
   pip install anthropic
   ```

#### Generate All Pages

```bash
# Generate all pending pages with Claude API
python3 scripts/generation/batch_generate_content.py --topic altered_states

# With 6 concurrent threads (faster, higher API rate)
python3 scripts/generation/batch_generate_content.py --topic altered_states --concurrent 6
```

The script automatically:
- ✅ Skips pages with complete content (won't overwrite your work)
- ✅ Generates AEO-optimized content (20-35 word answers, causal language, boundaries)
- ✅ Validates against forbidden language ("always," "guaranteed," etc.)
- ✅ Tracks costs and token usage
- ✅ Saves detailed log for review

## File Structure

```
scripts/generation/
├── batch_generate_content.py        # Main batch generator
├── altered_states_questions.yaml    # 124 questions with status tracking
├── templates/
│   └── answer_page_aeo.tsx.j2      # AEO-optimized page template
├── track_content_progress.py        # Progress tracker
├── validate_content_quality.py      # AEO quality validator
└── batch_log_*.json                 # Execution logs

salarsu/frontend/app/consciousness/altered-states/
├── {category}/
│   └── {question-slug}/
│       └── page.tsx                 # Generated answer pages
```

## Command Reference

### Batch Generation

```bash
# Template mode (placeholders only, no API needed)
python3 batch_generate_content.py --topic altered_states --template-mode

# API mode (requires ANTHROPIC_API_KEY)
python3 batch_generate_content.py --topic altered_states

# Dry run (preview what would be generated)
python3 batch_generate_content.py --topic altered_states --dry-run

# Resume from question #50 (skip first 50)
python3 batch_generate_content.py --topic altered_states --skip 50

# Generate only next 20 pages (testing)
python3 batch_generate_content.py --topic altered_states --limit 20

# 6 concurrent API calls (faster generation)
python3 batch_generate_content.py --topic altered_states --concurrent 6
```

### Progress Tracking

```bash
# Full progress report
python3 track_content_progress.py

# Show next 10 pages to fill
python3 track_content_progress.py --next 10

# Show next 20 from specific cluster
python3 track_content_progress.py --cluster "definitions-foundations" --next 20
```

### Quality Validation

```bash
# Validate all completed pages
python3 validate_content_quality.py

# Validate specific page
python3 validate_content_quality.py --page "are-dreams-considered-altered-states"
```

## Content Quality Standards (AEO)

All generated/manual content must follow these standards:

### ✅ Required Elements

1. **Short Answer** (20-35 words)
   - Direct, declarative response
   - No fluff or "you should" language
   - Explain WHAT it is or HOW it works

2. **Why This Matters** (2-4 sentences)
   - Use causal language: "because," "results in," "leads to," "demonstrates"
   - Explain mechanisms and broader implications
   - Be specific and concrete

3. **Where This Changes** (1-3 sentences)
   - Address boundaries, limits, exceptions
   - Spectrum thinking without contradicting short answer

4. **Related Questions** (exactly 5)
   - Auto-generated with same-cluster priority (up to 3)
   - Remaining filled from other clusters

### ❌ Forbidden Language

Never use: "always," "never," "guaranteed," "proven," "the best," "revolutionary," "game-changing"

### Tone Guidelines

- Neutral, explanatory (not instructional)
- No absolutes or hype
- Trust reader's intelligence
- No product promotion or CTAs

## Cost & Performance Estimates

### Claude API (Sonnet 4)

| Task | Cost | Time | Tokens |
|------|------|------|--------|
| 1 page | ~$0.01 | ~8 sec | ~800 total |
| 111 pages | ~$1.10 | ~15 min | ~88K total |
| 250 pages (all 3 topics) | ~$2.50 | ~35 min | ~200K total |

**Pricing**: $3/MTok input, $15/MTok output (Claude Sonnet 4)

### Performance (4 concurrent threads)

- Sequential: ~8 sec/page × 111 = 15 minutes
- Concurrent (4): ~15 minutes total
- Concurrent (6): ~10 minutes total

## Safety Features

### Won't Overwrite Complete Content

The script checks for placeholder markers before generating:
- `[Claude: Write`
- `[Claude: Provide`
- `TODO:`
- `PLACEHOLDER`

If a page exists WITHOUT these markers, it's considered complete and **skipped**.

### Execution Logs

Every run creates a timestamped log in `batch_log_{topic}_{timestamp}.json` with:
- All generated pages and their status
- Token usage and cost estimates
- Errors and warnings
- Mode (API vs template)

### Dry Run Mode

Always test with `--dry-run` first to preview what will be generated without creating files.

## Workflow Patterns

### Pattern 1: Full API Automation

```bash
# 1. Setup API key
export ANTHROPIC_API_KEY="your-key-here"

# 2. Generate all pages
python3 batch_generate_content.py --topic altered_states --concurrent 6

# 3. Validate quality
python3 validate_content_quality.py

# 4. Review flagged pages manually
python3 track_content_progress.py --next 20

# 5. Deploy
cd /home/rsalars/Projects/dreamweaving/salarsu
npm run build
git add .
git commit -m "Generated all Altered States answer pages"
git push
```

**Timeline**: ~30 minutes for 111 pages
**Cost**: ~$1.10

### Pattern 2: Hybrid (API + Manual Refinement)

```bash
# 1. Generate with API
python3 batch_generate_content.py --topic altered_states

# 2. Identify weak pages
python3 validate_content_quality.py | grep WARNING

# 3. Manually refine flagged pages
# (Edit in VS Code)

# 4. Re-run validation
python3 validate_content_quality.py

# 5. Deploy
```

**Timeline**: 15 min API + 2-3 hours manual refinement
**Quality**: Highest (AI + human review)

### Pattern 3: Template + Manual Filling (Current)

```bash
# 1. Already generated 111 templates
# (Already done)

# 2. Fill next 10 pages manually
python3 track_content_progress.py --next 10

# 3. Edit each page in VS Code
# (Follow AEO template from completed examples)

# 4. Validate as you go
python3 validate_content_quality.py

# 5. Deploy after each batch
```

**Timeline**: 6-8 days at 15-20 pages/day
**Quality**: High (full manual control)

## Next Steps

### For Altered States Topic

**Option A: API Generation (Recommended for Speed)**
1. Get Claude API key from https://console.anthropic.com/
2. Run: `export ANTHROPIC_API_KEY="your-key"`
3. Run: `python3 batch_generate_content.py --topic altered_states --concurrent 4`
4. Review output and validate
5. Deploy to production

**Option B: Continue Manual Filling**
1. Run: `python3 track_content_progress.py --next 10`
2. Fill 10 pages following AEO template (see completed examples)
3. Validate: `python3 validate_content_quality.py`
4. Repeat until complete

### For Future Topics (Meditation, Memory Systems)

1. Extract questions from Marketing_3.md into YAML files:
   - `meditation_questions.yaml` (~130-150 questions)
   - `memory_questions.yaml` (~50-60 questions)

2. Run batch generation (same commands, different topic):
   ```bash
   python3 batch_generate_content.py --topic meditation
   python3 batch_generate_content.py --topic memory
   ```

3. Total for all 3 topics: ~250 pages, ~$2.50, ~35 minutes

## Troubleshooting

### "anthropic package not installed"

Install it:
```bash
pip install anthropic
```

### "ANTHROPIC_API_KEY environment variable not set"

Set it:
```bash
export ANTHROPIC_API_KEY="your-key-here"
# Or add to ~/.bashrc for permanent:
echo 'export ANTHROPIC_API_KEY="your-key"' >> ~/.bashrc
```

### Pages generated with placeholders instead of real content

You're in template mode. Either:
- Set API key and rerun without `--template-mode`
- Or manually fill the placeholders (current approach)

### Script overwrote my completed pages

The updated script now checks for completion and skips pages with real content. Restore from git if needed:
```bash
git checkout HEAD -- path/to/overwritten/page.tsx
```

### Want to regenerate a specific page

Delete it first, then run batch script with `--limit 1 --skip N` to regenerate just that page.

## Implementation Details

### Related Questions Algorithm

For each answer page, generates 5 related questions:
1. Up to 3 from **same cluster** (maintains topical cohesion)
2. Remainder from **other clusters** (encourages cross-topic exploration)
3. All questions link to valid answer pages

### Placeholder Detection

Checks for these markers to determine if content is complete:
- `[Claude: Write` - Template marker for AI generation
- `[Claude: Provide` - Alternative template marker
- `TODO:` - Standard development marker
- `PLACEHOLDER` - Explicit placeholder text

If ANY found → considered placeholder → will be regenerated
If NONE found → considered complete → will be skipped

### Cost Tracking

Tracks both:
- **Input tokens**: Your prompts and context
- **Output tokens**: Claude's generated content

Formula: `(input_tokens / 1M × $3) + (output_tokens / 1M × $15)`

### Template Rendering

Uses Jinja2 templates with these variables:
- `{{ question }}` - The question text
- `{{ short_answer }}` - 20-35 word direct answer
- `{{ why_this_matters }}` - Context paragraph
- `{{ where_this_changes }}` - Boundary paragraph
- `{{ related_questions }}` - List of 5 related Q&A links
- `{{ category_name }}` - Human-readable category
- `{{ category_url }}` - Back link to category index

## Future Enhancements

### Planned Features

- [ ] **Multi-topic batch run** - Generate all 3 topics in one command
- [ ] **Quality scoring** - Auto-score each page against AEO rubric
- [ ] **Content variation** - A/B test different answer styles
- [ ] **SEO optimization** - Auto-optimize titles/descriptions for search
- [ ] **Image generation** - Auto-create featured images per page

### API Cost Optimization

Current: Claude Sonnet 4 ($3/$15 per MTok)

Potential optimizations:
- Use Claude Haiku for simple Q&A (~70% cost savings)
- Batch prompts with JSON array output (reduce overhead)
- Pre-compute embeddings for related questions (faster)

## Contact & Support

For questions or issues with this system:
1. Check existing batch logs in `scripts/generation/batch_log_*.json`
2. Review CLAUDE.md for project-wide context
3. Run scripts with `--dry-run` first to debug

## Credits

Built as part of the Answer Engine Optimization (AEO) strategy for salars.net.
Integrates with existing Dreamweaving project infrastructure.

**Status**: Production-ready ✅
**Last Updated**: 2026-01-04
**Version**: 1.0.0
