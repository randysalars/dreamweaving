# YouTube Packaging Standard Operating Procedure

**Sacred Digital Dreamweaver - YouTube Publishing Workflow**

This document serves as the master reference for creating consistent, high-quality YouTube packages across all Dreamweaver sessions. It defines fixed brand elements, flexible content variables, quality standards, and procedural steps.

---

## Table of Contents

1. [Purpose & Scope](#purpose--scope)
2. [Package Components](#package-components)
3. [Brand Identity (Fixed Elements)](#brand-identity-fixed-elements)
4. [Content Variables (Flexible Elements)](#content-variables-flexible-elements)
5. [Thumbnail Production Workflow](#thumbnail-production-workflow)
6. [Title Optimization Workflow](#title-optimization-workflow)
7. [Description Generation Workflow](#description-generation-workflow)
8. [VTT Subtitle Generation](#vtt-subtitle-generation)
9. [Quality Checklists](#quality-checklists)
10. [Tool Reference](#tool-reference)
11. [Troubleshooting](#troubleshooting)

---

## Purpose & Scope

### Purpose

Enable seamless, consistent YouTube package creation across all Dreamweaver sessions regardless of:
- Content variety (Eden, cosmic, neural, warrior themes)
- Time gaps between sessions
- Changes in subject matter

### Scope

This SOP covers generation of:
- YouTube thumbnails (1280x720 PNG)
- Optimized video titles
- Full video descriptions with chapters
- VTT subtitle files
- Upload metadata (tags, category, privacy)

### Guiding Principles

| Principle | Application |
|-----------|-------------|
| **Consistency** | Same visual language, brand colors, and quality standards |
| **Recognition** | Thumbnails identifiable as Sacred Digital Dreamweaver at a glance |
| **CTR Optimization** | Every element designed for maximum click-through rate |
| **Mobile-First** | All designs readable at 200x112 pixel preview size |

---

## Package Components

### Complete YouTube Package Contents

```
sessions/{session}/output/
├── youtube_thumbnail.png       # 1280x720 branded thumbnail
├── subtitles.vtt               # WebVTT chapter markers
├── YOUTUBE_DESCRIPTION.md      # Full description with chapters
├── YOUTUBE_PACKAGE_README.md   # Upload instructions
└── youtube_package/            # Optional consolidated folder
    ├── thumbnail.png
    └── metadata.json
```

### Generation Command

```bash
python3 scripts/core/package_youtube.py --session sessions/{session}
```

---

## Brand Identity (Fixed Elements)

These elements MUST remain consistent across ALL thumbnails and packages.

### Color Palettes

| Palette | Primary | Secondary | Background | Use Case |
|---------|---------|-----------|------------|----------|
| **sacred_light** | `#FFD700` (Gold) | `#F4E4BC` (Cream) | `#0A0A1A` (Cosmic) | Default, spiritual themes |
| **cosmic_journey** | `#9B6DFF` (Purple) | `#64B5F6` (Blue) | `#0D0221` (Space) | Cosmic, starship themes |
| **garden_eden** | `#50C878` (Emerald) | `#FFD700` (Gold) | `#0F2818` (Forest) | Eden, garden themes |
| **ancient_temple** | `#D4AF37` (Antique) | `#8B4513` (Bronze) | `#1A0F0A` (Temple) | Historical, temple themes |
| **neural_network** | `#00D4FF` (Cyan) | `#9B6DFF` (Purple) | `#0A0A1A` (Digital) | Neural, tech themes |

### Typography Standards

| Element | Font | Size | Style |
|---------|------|------|-------|
| Title | DejaVuSans-Bold | 100px | ALL CAPS, white with glow |
| Subtitle | DejaVuSans | 42px | Title case, secondary color |
| Badges | DejaVuSans-Bold | 32px | White on dark/accent background |

### Visual Effects

| Effect | Specification | Purpose |
|--------|---------------|---------|
| **Vignette** | 30-60% strength, radial | Frame focus, dark edges |
| **Center Glow** | 25% intensity, palette glow color | Draw eye to center |
| **Text Glow** | 8-10px radius, palette glow color | Readability, mystical feel |
| **Text Shadow** | 4px offset, black 60% opacity | Edge separation |

### Zone Layout (1280x720)

```
┌───────────────────────────────────────────────────────────────┐
│  SAFE MARGIN (10% = 64px sides, 36px top/bottom)              │
│  ┌───────────────────────────────────────────────────────┐    │
│  │  TITLE ZONE (top 30% = 216px)                         │    │
│  │  - Bold title text                                    │    │
│  │  - Subtitle if applicable                             │    │
│  ├───────────────────────────────────────────────────────┤    │
│  │  FOCAL ZONE (center 40% = 288px)                      │    │
│  │  - Main visual element                                │    │
│  │  - Highest contrast area                              │    │
│  │  - Center glow effect                                 │    │
│  ├───────────────────────────────────────────────────────┤    │
│  │  BADGE ZONE (bottom 15% = 108px)                      │    │
│  │  - Feature badge (left): Hz, brainwave state          │    │
│  │  - Duration badge (right): MM:SS                      │    │
│  └───────────────────────────────────────────────────────┘    │
│  YouTube timestamp overlay zone (bottom right 8% margin)      │
└───────────────────────────────────────────────────────────────┘
```

### Channel Promo (Description Header)

**FIXED TEXT** - Always appears first in every description:

```
🌟 Visit https://www.salars.net/dreamweavings for more guided hypnosis journeys by Salars

---
```

---

## Content Variables (Flexible Elements)

These elements change per session while maintaining brand consistency.

### Thumbnail Variables

| Variable | Source | Fallback |
|----------|--------|----------|
| **Base Image** | `images/uploaded/*.png` | Gradient background |
| **Title Text** | `manifest.yaml → title` | Session slug, title case |
| **Subtitle** | `manifest.yaml → theme` | None |
| **Duration** | `manifest.yaml → duration` | Calculated from audio |
| **Features** | `manifest.yaml → audio.binaural` | None |
| **Palette** | Manual selection based on theme | `sacred_light` |
| **Template** | Manual selection based on content | `portal_gateway` |

### Template Selection Guide

| Session Theme | Recommended Template | Recommended Palette |
|---------------|---------------------|---------------------|
| Eden/Garden pathworking | `journey_scene` | `garden_eden` |
| Cosmic/Starship | `portal_gateway` | `cosmic_journey` |
| Temple/Ancient | `sacred_symbol` | `ancient_temple` |
| Neural/Brainwave | `abstract_energy` | `neural_network` |
| Warrior/Forge | `portal_gateway` | `ancient_temple` |
| General spiritual | `portal_gateway` | `sacred_light` |

### Title Variables

| Variable | Source | Optimization Rules |
|----------|--------|-------------------|
| **Power Verb** | Session theme | Forge, Unlock, Enter, Awaken, Journey |
| **Transformation** | Session purpose | Courage, Peace, Connection, Power |
| **Feature** | Technical element | Deep Hypnosis, Theta Journey, Gamma Activation |

### Description Variables

| Section | Source | Required |
|---------|--------|----------|
| **Title** | `youtube.optimized_title` or generated | Yes |
| **Duration** | Calculated from audio | Yes |
| **Archetypes** | `manifest.yaml → archetypes[]` | If present |
| **Audio Specs** | `manifest.yaml → audio.*` | Yes |
| **Timeline/Chapters** | `manifest.yaml → sections[]` | Yes |
| **Tags** | `manifest.yaml → youtube.tags[]` | Yes |

---

## Thumbnail Production Workflow

### Prerequisites

- [ ] Session manifest.yaml exists with title and theme
- [ ] Base images uploaded to `images/uploaded/` (optional but recommended)
- [ ] venv activated

### Step 1: Select Template and Palette

Based on session theme, choose appropriate template and palette from the selection guide above.

### Step 2: Verify Base Image

```bash
ls sessions/{session}/images/uploaded/
```

If no images exist, the generator will use a gradient background.

### Step 3: Generate Thumbnail

**Basic generation (auto-detects settings from manifest):**
```bash
python3 scripts/core/generate_thumbnail.py sessions/{session}/
```

**With explicit settings:**
```bash
python3 scripts/core/generate_thumbnail.py sessions/{session}/ \
    --template portal_gateway \
    --palette ancient_temple \
    --title "FORGE UNBREAKABLE COURAGE" \
    --subtitle "Deep Hypnosis Journey" \
    --duration "30:00" \
    --features "150Hz" "Theta"
```

### Step 4: Verify Output

```bash
# Check file exists and size
ls -la sessions/{session}/output/youtube_thumbnail.png

# View thumbnail (if GUI available)
xdg-open sessions/{session}/output/youtube_thumbnail.png
```

### Step 5: Quality Check

Use the thumbnail quality checklist (see Quality Checklists section).

---

## Title Optimization Workflow

### The 10 Commandments of High-CTR Titles

1. **ONE Big Promise** - Single clear value, not multiple
2. **Curiosity Gap** - Raise a question, don't answer it
3. **Keyword Anchor** - Main keyword in first 3 words
4. **Emotional Trigger** - Use power words that evoke feeling
5. **Specificity** - Specific = believable, vague = ignorable
6. **Optimal Length** - 4-7 words for browse, 7-11 for search
7. **Power Verbs** - Use movement verbs: Forge, Unlock, Enter, Awaken
8. **Pattern Interrupt** - Stand out from typical meditation titles
9. **Story Beginning** - Sound like a story, not a label
10. **A/B Testable** - Design variations for testing

### Title Templates

| Template | Format | Example |
|----------|--------|---------|
| Power Verb + Transform | `[VERB] [TRANSFORMATION] \| [FEATURE]` | Forge Unbreakable Courage \| Deep Hypnosis |
| Enter + Place | `Enter [MYSTICAL_LOCATION]` | Enter the Iron Soul Forge |
| The + Name | `The [EVOCATIVE_NAME] \| [BENEFIT]` | The Garden of Eden \| Deep Peace |
| Transform Promise | `[BECOME] [STATE] in [TIME]` | Become Fearless in 30 Minutes |

### Setting Optimized Title in Manifest

```yaml
youtube:
  optimized_title: "Forge Unbreakable Courage | Deep Hypnosis Journey"
```

### Title Generation Priority

1. `youtube.optimized_title` (manual, preferred)
2. `youtube.title` (legacy field)
3. Auto-generated from `title` field

---

## Description Generation Workflow

### Description Structure

```markdown
🌟 Visit https://www.salars.net/dreamweavings for more guided hypnosis journeys by Salars

---

# [OPTIMIZED_TITLE]

[youtube.description if set]

**Duration**: [X] minutes

## 🎭 Journey Archetypes

[If archetypes exist in manifest]
**[Name]** - [Role]
  [Description]
  *Qualities: [qualities]*

## 🎧 Audio Specifications

- **Binaural Beats**: [carrier] Hz carrier
- **Gamma Flash**: [freq] Hz at [timestamp] (if applicable)

## 🌌 Timeline

**0:00** - Pre Talk
**3:00** - Induction
...

⚠️ Use headphones for binaural effectiveness
Do not use while driving or operating machinery

## 🏷️ Tags

tag1, tag2, tag3, ...
```

### Tag Guidelines

- 20-25 tags maximum
- Include: theme keywords, technique keywords, benefit keywords
- Format: comma-separated for easy YouTube copy/paste
- Example categories:
  - Technique: guided hypnosis, binaural beats, theta waves
  - Theme: courage meditation, warrior mindset, inner strength
  - Benefits: confidence, discipline, resilience

---

## VTT Subtitle Generation

### VTT Format

```
WEBVTT

1
00:00:00.000 --> 00:03:00.000
Pre Talk
Welcome & Preparation
(alpha)

2
00:03:00.000 --> 00:08:30.000
Induction
Descent into Trance
(alpha_to_theta)
```

### Section Definition in Manifest

```yaml
sections:
  - name: "pre_talk"
    description: "Welcome & Preparation"
    start: 0        # seconds
    end: 180        # seconds
    brainwave_target: "alpha"

  - name: "induction"
    description: "Descent into Trance"
    start: 180
    end: 510
    brainwave_target: "alpha_to_theta"
```

### VTT Generation

VTT files are automatically generated by `package_youtube.py` from the `sections` array in the manifest.

```bash
python3 scripts/core/package_youtube.py --session sessions/{session}
```

---

## Quality Checklists

### Thumbnail Quality Checklist

```
THUMBNAIL QUALITY CHECKLIST
─────────────────────────────────────────────
□ Readable at 200x112 pixels (mobile preview)
□ Title visible and legible
□ Single clear focal point
□ High contrast between elements
□ Consistent with channel branding
□ No critical content in outer 10% margins
□ Duration badge doesn't overlap YouTube timestamp
□ Colors pop in YouTube dark/light modes
□ File under 2MB
□ Evokes curiosity without misleading
□ Palette appropriate for session theme
□ Template appropriate for content type
─────────────────────────────────────────────
```

### Title Quality Checklist

```
TITLE QUALITY CHECKLIST
─────────────────────────────────────────────
□ Single clear promise (not multiple)
□ Keyword anchor in first 3 words
□ Emotional trigger present
□ Specific, not vague
□ 4-11 words (ideal: 5-7)
□ Power verb included
□ Creates curiosity without confusion
□ Sounds like story beginning, not label
□ Different from typical meditation titles
□ Would YOU click on this?
─────────────────────────────────────────────
```

### Description Quality Checklist

```
DESCRIPTION QUALITY CHECKLIST
─────────────────────────────────────────────
□ Website promo at top (Salars spelling correct)
□ Title matches optimized_title
□ Duration accurate
□ All archetypes listed (if applicable)
□ Audio specs complete
□ Timeline matches actual sections
□ Safety disclaimers present
□ Tags comma-separated (20-25 tags)
□ All timestamps formatted correctly
□ Markdown renders properly
─────────────────────────────────────────────
```

### VTT Quality Checklist

```
VTT QUALITY CHECKLIST
─────────────────────────────────────────────
□ WEBVTT header present
□ All sections from manifest included
□ Timestamps in HH:MM:SS.mmm format
□ No overlapping cue times
□ Section names human-readable (spaces, title case)
□ Brainwave targets in parentheses
□ End time of last cue matches session duration
□ Descriptions match manifest descriptions
─────────────────────────────────────────────
```

### Complete Package Checklist

```
YOUTUBE PACKAGE COMPLETE CHECKLIST
─────────────────────────────────────────────
□ youtube_thumbnail.png exists (1280x720)
□ subtitles.vtt exists and validates
□ YOUTUBE_DESCRIPTION.md exists
□ YOUTUBE_PACKAGE_README.md exists
□ All files in output/ directory
□ Manifest has youtube.optimized_title
□ Manifest has youtube.tags (20-25 items)
□ Manifest has complete sections array
□ Thumbnail passes quality checklist
□ Title passes quality checklist
□ Description passes quality checklist
□ VTT passes quality checklist
─────────────────────────────────────────────
```

---

## Tool Reference

### Primary Scripts

| Script | Purpose | Command |
|--------|---------|---------|
| `generate_thumbnail.py` | Create branded thumbnail | `python3 scripts/core/generate_thumbnail.py sessions/{session}/` |
| `package_youtube.py` | Generate full package | `python3 scripts/core/package_youtube.py --session sessions/{session}` |

### Thumbnail Generator Options

```bash
python3 scripts/core/generate_thumbnail.py sessions/{session}/ \
    --template [portal_gateway|sacred_symbol|journey_scene|abstract_energy] \
    --palette [sacred_light|cosmic_journey|garden_eden|ancient_temple|neural_network] \
    --title "CUSTOM TITLE" \
    --subtitle "Custom subtitle" \
    --duration "30:00" \
    --features "150Hz" "Theta" \
    --base-image path/to/image.png \
    --output path/to/output.png
```

### Package Generator Options

```bash
python3 scripts/core/package_youtube.py \
    --session sessions/{session} \
    --audio path/to/audio.mp3 \
    --output-dir path/to/output
```

### Manifest YouTube Configuration

```yaml
youtube:
  # Optimized title (manual, preferred)
  optimized_title: "Forge Unbreakable Courage | Deep Hypnosis Journey"

  # Legacy title field (fallback)
  title: "The Iron Soul Forge"

  # Description override
  description: "Custom description paragraph..."

  # Thumbnail source override
  thumbnail_source: "images/uploaded/specific_image.png"

  # SEO tags (comma-separated in output)
  tags:
    - guided hypnosis
    - courage meditation
    - binaural beats
    # ... 20-25 total

  # YouTube settings
  category: "People & Blogs"
  privacy: unlisted
```

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| No thumbnail generated | Missing Pillow | `pip install Pillow` |
| Title not appearing | Font not found | Check DejaVuSans-Bold installation |
| VTT empty | No sections in manifest | Add `sections:` array to manifest |
| Tags as hashtags | Old code version | Update package_youtube.py |
| Wrong website URL | Typo in template | Check promo text in create_description() |
| Duration badge missing | No duration in manifest | Add `duration:` to manifest |
| Base image not used | Wrong path | Check `images/uploaded/` exists |

### Validation Commands

```bash
# Check thumbnail file
file sessions/{session}/output/youtube_thumbnail.png
identify sessions/{session}/output/youtube_thumbnail.png  # ImageMagick

# Validate VTT syntax
head -20 sessions/{session}/output/subtitles.vtt

# Check manifest sections
grep -A 5 "sections:" sessions/{session}/manifest.yaml

# Verify package completeness
ls -la sessions/{session}/output/
```

### Debug Mode

For verbose output during generation:

```bash
# Thumbnail generator prints debug info by default
python3 scripts/core/generate_thumbnail.py sessions/{session}/ 2>&1 | tee thumbnail_debug.log

# Package generator
python3 scripts/core/package_youtube.py --session sessions/{session} 2>&1 | tee package_debug.log
```

---

## Quick Reference Card

### Minimum Viable Package

```bash
# 1. Ensure manifest has required fields
# Required: title, duration, sections[]
# Recommended: youtube.optimized_title, youtube.tags[]

# 2. Generate thumbnail
python3 scripts/core/generate_thumbnail.py sessions/{session}/

# 3. Generate package
python3 scripts/core/package_youtube.py --session sessions/{session}

# 4. Verify
ls sessions/{session}/output/
```

### Palette Quick Reference

| Theme | Palette |
|-------|---------|
| Spiritual/Divine | `sacred_light` |
| Cosmic/Space | `cosmic_journey` |
| Nature/Garden | `garden_eden` |
| Ancient/Temple | `ancient_temple` |
| Tech/Neural | `neural_network` |

### Template Quick Reference

| Content Type | Template |
|--------------|----------|
| Portal/Journey | `portal_gateway` |
| Symbol Focus | `sacred_symbol` |
| Scene/Landscape | `journey_scene` |
| Abstract/Energy | `abstract_energy` |

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-02 | Initial SOP creation |

---

*This document is the authoritative reference for YouTube packaging in the Sacred Digital Dreamweaver project. All sessions should follow these standards for brand consistency.*
