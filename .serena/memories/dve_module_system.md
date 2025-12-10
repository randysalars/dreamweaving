# DVE (Deep Visualization Enhancement) Module System

## Overview

The DVE system provides modular enhancement techniques for creating deeper, more immersive visualization experiences in Dreamweaving sessions. It consists of 7 insertable micro-modules (15-30 seconds each) organized into 3 tiers, mapped to 5 visualization levels.

## 5-Level Visualization Taxonomy

| Level | Name | Modules | Typical Sessions |
|-------|------|---------|------------------|
| 1 | Foundational | None | Beginner, Layer 1 |
| 2 | Immersive | DVE-01 | Standard Layer 2 |
| 3 | Embodied | DVE-01 through DVE-04 | Deep Layer 2, Layer 3 entry |
| 4 | Interactive | DVE-01 through DVE-05 | Layer 3, Ipsissimus entry |
| 5 | Hyperimaginal | All modules (DVE-01 to DVE-07) | Ipsissimus, Advanced |

## DVE Module Quick Reference

### Tier 1 - Foundation (Level 2+)

| Module | Name | Duration | Placement | Purpose |
|--------|------|----------|-----------|---------|
| DVE-01 | Imaginal Priming | 20s | End of pre_talk | Activates subconscious image-generation |
| DVE-02 | Hypnagogic Entry | 25s | Middle of induction | Theta-dominant waking-sleeping threshold |
| DVE-03 | Theater/Temple Construction | 25s | End of deepening | Establishes stable imaginal container |

### Tier 2 - Intermediate (Level 3+)

| Module | Name | Duration | Placement | Purpose |
|--------|------|----------|-----------|---------|
| DVE-04 | Embodiment & Proprioception | 25s | Start of journey | Deep body awareness in imaginal space |
| DVE-05 | Autonomous Agents & Mirrors | 28s | During archetypal encounters | Entities that move independently |

### Tier 3 - Hyperimaginal (Level 5 only)

| Module | Name | Duration | Placement | Purpose |
|--------|------|----------|-----------|---------|
| DVE-06 | Stabilization Protocols | 18s | Extended visualization | Anti-fade techniques from lucid dreaming |
| DVE-07 | Predictive Processing Override | 25s | helm_deep_trance peak only | Impossible imagery for breakthrough states |

## Key Files

| File | Purpose |
|------|---------|
| `knowledge/visualization/dve_modules.yaml` | Core module definitions with SSML templates |
| `knowledge/visualization/scene_architecture.yaml` | Depth layers, scene types, transitions |
| `knowledge/embodiment/proprioceptive_templates.yaml` | Body awareness templates for DVE-04 |
| `knowledge/indexes/dve_index.yaml` | Quick reference index |
| `knowledge/outcome_registry.yaml` | DVE recommendations per outcome (in `dve_recommendations` section) |
| `config/manifest.schema.json` | DVE fields in manifest schema |
| `prompts/hypnotic_dreamweaving_instructions.md` | DVE section with usage guidelines |

## DVE-03 Container Variants

| Variant | Best For | Key Elements |
|---------|----------|--------------|
| theater | Neutral, screen-based | Curved walls, viewing seat, domed ceiling |
| temple | Initiation, sacred work | Columns, altar, sacred geometry |
| spaceship | Cosmic journeys | Viewscreens, navigation console, stars |
| garden | Healing, abundance | Trees, flowers, water features, paths |
| cave | Shadow work, descent | Rough stone, phosphorescence, passages |
| observatory | Celestial, cognitive | Dome, telescope, star charts |

## DVE-05 Variants

| Variant | Best For |
|---------|----------|
| autonomous_agent | Self-knowledge, spiritual guidance |
| dialogue_framework | Intuition, inner council |
| mirror_encounter | Confidence, transformation, identity work |
| parts_dialogue | Shadow integration, healing |

## Outcome Alignment

| Outcome | Minimum Level | Optimal Level | Emphasis Modules |
|---------|---------------|---------------|------------------|
| healing | 2 | 3 | DVE-01, DVE-04 |
| transformation | 3 | 4 | DVE-05 (mirror) |
| empowerment | 2 | 3 | DVE-01, DVE-04 |
| self_knowledge | 3 | 4 | DVE-05 (autonomous) |
| spiritual_growth | 4 | 5 | DVE-05, DVE-07 |
| creativity | 2 | 3 | DVE-02 |
| relaxation | 1 | 2 | Light DVE only |
| confidence | 2 | 3 | DVE-05 (mirror) |

## Contraindications

| Module | Caution For | Modification |
|--------|-------------|--------------|
| DVE-02 | High anxiety, sleep disorders | Use gentler variant |
| DVE-03 | Claustrophobia | Use open variants (garden) |
| DVE-04 | Body dysmorphia, somatic trauma | Focus on sensation, not appearance |
| DVE-05 | Dissociative disorders | Use dialogue_framework only |
| DVE-07 | Psychotic, dissociative, first-time | **CONTRAINDICATED** |

## Manifest Schema Usage

Sessions can specify DVE configuration in manifest.yaml:

```yaml
session:
  visualization_level: 3  # 1-5
  dve_config:
    modules_enabled: [DVE-01, DVE-02, DVE-03, DVE-04]
    auto_select_from_level: true
    theater_variant: temple
```

Sections can specify insertions:

```yaml
sections:
  - name: deepening
    dve_insertions:
      - module_id: DVE-03
        position: end
        variant: temple
```

## DVE Insertion Markers

Use these markers in scripts to indicate DVE placement:

```
[DVE:PRIMING_START] ... [DVE:PRIMING_END]
[DVE:HYPNAGOGIC_START] ... [DVE:HYPNAGOGIC_END]
[DVE:CONTAINER_START] ... [DVE:CONTAINER_END]
[DVE:EMBODIMENT_START] ... [DVE:EMBODIMENT_END]
[DVE:AUTONOMOUS_START] ... [DVE:AUTONOMOUS_END]
[DVE:MIRROR_START] ... [DVE:MIRROR_END]
[DVE:STABILIZE_START] ... [DVE:STABILIZE_END]
[DVE:OVERRIDE_START] ... [DVE:OVERRIDE_END]
```

## Design Principles

1. **Backward Compatible** - Level 1 sessions work unchanged
2. **Incremental Adoption** - Use 0, some, or all modules
3. **Rate = 1.0 Always** - Pacing through breaks, never slow rate
4. **15-30 Second Modules** - Brief, insertable micro-sections
5. **Safety-First** - Contraindication matrix for vulnerable populations
6. **Outcome-Aligned** - DVE recommendations integrated with outcome engineering

## Psychological Foundations

- **Imaginal Priming (DVE-01)**: Based on research showing pre-activation of imagery faculty improves visualization
- **Hypnagogic Entry (DVE-02)**: Theta-gamma coupling at waking-sleeping threshold
- **Container Construction (DVE-03)**: Jung's active imagination "temenos" concept
- **Embodiment (DVE-04)**: Proprioceptive integration from Desoille's Guided Affective Imagery
- **Autonomous Agents (DVE-05)**: Jungian autonomous figures from active imagination
- **Stabilization (DVE-06)**: Lucid dreaming research on scene maintenance
- **Predictive Override (DVE-07)**: Disrupts brain's prediction for awe/breakthrough states
