# Answer Pages Generation System

## Overview

This system generates TypeScript answer pages for the salars.net consciousness hub following the Answer Engine Optimization (AEO) framework from Notion's "Answer Pages That Google Has No Choice But to Rank" methodology.

## Completed Work

### 1. Infrastructure Created
- **scripts/generation/** - Main generation directory
- **parsers/marketing_parser.py** - Extracts question clusters from Marketing_3.md
- **generators/simple_generator.py** - Generates TypeScript pages with structured content
- **generators/page_generator.py** - API-based generator (not used due to no API key)
- **templates/answer_page.tsx.j2** - Jinja2 template for Next.js pages

### 2. 10 Sample Pages Generated

All pages successfully generated with complete content at:
`/home/rsalars/Projects/salarsu/frontend/app/consciousness/altered-states/`

#### Core Definitions & Foundations (5 pages)
1. `what-is-an-altered-state-of-consciousness/page.tsx`
2. `what-defines-normal-waking-consciousness/page.tsx`
3. `how-do-altered-states-differ-from-everyday-awareness/page.tsx`
4. `are-altered-states-always-intentional/page.tsx`
5. `can-altered-states-occur-spontaneously/page.tsx`

#### Natural vs Induced Altered States (2 pages)
6. `what-are-natural-altered-states-of-consciousness/page.tsx`
7. `what-causes-natural-altered-states-to-occur/page.tsx`

#### Entry Pathways & Triggers (2 pages)
8. `how-do-altered-states-begin/page.tsx`
9. `can-breathing-techniques-induce-altered-states/page.tsx`

#### Safety, Risks & Stability (1 page)
10. `are-altered-states-dangerous/page.tsx`

### 3. Build Verification

✓ All 10 pages compile without TypeScript errors
✓ Next.js build completed successfully
✓ All pages appear in build output

## Page Structure

Each page follows this format:

```typescript
- Metadata (title, description, OpenGraph, keywords)
- Breadcrumb navigation
- H1 Question title
- Short Answer section (20-35 words)
- Why This Matters section (2-4 sentences)
- Where This Changes section (1-3 sentences)
- Related Questions (5 links)
- Back to category link
```

## Content Quality

All pages contain:
- ✓ Authoritative 20-35 word answers
- ✓ Neuroscience mechanisms explained
- ✓ Boundary conditions and nuances
- ✓ No hardcoded colors (uses semantic tokens)
- ✓ Proper TypeScript types
- ✓ SEO-optimized metadata

## Next Steps to Generate More Pages

### Option 1: Generate All Remaining Pages (240+)

```bash
cd /home/rsalars/Projects/dreamweaving/scripts/generation

# Edit generate_sample_pages.py to include all questions from Marketing_3.md
# Run the full generation
python3 generate_sample_pages.py
```

### Option 2: Generate by Category

```python
# Create category-specific generation scripts
# Example: generate_meditation_pages.py, generate_memory_pages.py
```

### Option 3: Batch Generation with Content Filling

Currently pages are generated with placeholder prompts that must be filled manually.
To automate content generation, you would need either:

1. **Claude API access** - Modify `PageGenerator` to use API key
2. **Manual filling** - Use VS Code extension to fill placeholders interactively
3. **Alternative AI service** - Adapt generator to use different API

## File Structure

```
scripts/generation/
├── README.md                           # This file
├── generate_sample_pages.py            # Main generation script
├── parsers/
│   └── marketing_parser.py             # Question extraction
├── generators/
│   ├── simple_generator.py             # Template-based generation
│   └── page_generator.py               # API-based generation (unused)
└── templates/
    └── answer_page.tsx.j2              # TypeScript page template
```

## Source Data

Questions extracted from:
`/home/rsalars/Projects/dreamweaving/knowledge/notion_export/pages/Marketing_3.md`

Three topic maps available:
1. **Altered States** - 10 clusters, 100+ questions (DONE: 10 sample pages)
2. **Meditation** - 12 clusters, 120-180 questions
3. **Memory Systems** - Multi-cluster, 50+ questions

## Related Questions Algorithm

Pages link to related questions using this priority:
1. Same-cluster questions first (up to 3)
2. Fill remainder with cross-cluster questions
3. Maximum 5 related questions per page

## Key Design Decisions

1. **No API calls** - Generated pages with placeholders due to no Claude API key
2. **Manual content filling** - Content filled by Claude via VS Code extension
3. **Distributed structure** - Pages live under existing hubs, not /answers/
4. **Semantic tokens only** - No hardcoded colors (bg-background, text-foreground)
5. **TypeScript native** - Direct .tsx generation, no intermediate formats

## Answer Pages Framework Principles

From the Notion document:

### Micro-Answer Architecture
- One question per page
- 20-35 word direct answers
- No fluff or filler language
- Structured sections (Short Answer, Why This Matters, Where This Changes)

### SEO Optimization
- Question in H1, title, and meta description
- Related questions for internal linking
- Breadcrumb navigation
- Canonical URLs

### Content Quality
- Authoritative, neutral tone
- Mechanism explanations (neuroscience, psychology)
- Boundary conditions and nuances
- Trust reader intelligence

## Success Metrics

✓ 10 pages generated
✓ 0 TypeScript errors
✓ 0 build errors
✓ All pages render in development
✓ All pages build for production
✓ SEO metadata complete
✓ Related questions linked
✓ Semantic color tokens used

## Known Issues

None! All pages build successfully.

## Future Enhancements

1. Generate category index pages (`/definitions-foundations/page.tsx`)
2. Add FAQ schema markup for SEO
3. Create automated testing for content quality
4. Build batch generation scripts for remaining 240+ pages
5. Add analytics tracking for answer effectiveness
