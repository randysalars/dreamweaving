# Dreamweaving Claude Skills System Architecture

## Overview

The Dreamweaving project implements a **4-tier Claude Skills system** designed for safe, effective guided altered-state experiences. Skills are composable, reloadable competencies that agents invoke as needed.

## Tier Structure

| Tier | Name | Purpose | Load Policy |
|------|------|---------|-------------|
| **Tier 1** | Neural Core | Always-on foundation | Always loaded |
| **Tier 2** | Immune System | Safety & boundaries | Triggered/Always |
| **Tier 3** | Operations | Production pipeline | Task-specific |
| **Tier 4** | Growth | Business automation | Conditional |

## Directory Structure

```
.claude/skills/
├── tier1-neural-core/
│   ├── hypnotic-language/         # Attention guidance & trance navigation
│   │   ├── SKILL.md               # Master metadata
│   │   ├── induction/             # Entry patterns
│   │   ├── deepening/             # Fractionation, time distortion
│   │   ├── suggestion/            # Indirect, values-aligned
│   │   ├── emergence/             # Reorientation, grounding
│   │   └── validation/            # Depth checks, forbidden patterns
│   │
│   ├── symbolic-mapping/          # Meaning engine for symbols/archetypes
│   │   ├── SKILL.md
│   │   ├── symbols/               # Elemental, light-dark, path-threshold
│   │   ├── archetypes/            # Guide, pilgrim, healer, witness
│   │   ├── mappings/              # Intention→symbol, symbol→emotion
│   │   ├── theological-filters/   # Christian-safe, forbidden-frames
│   │   ├── narrative-constraints/ # Agency, authority, closure rules
│   │   └── validation/
│   │
│   └── audio-somatic/             # Nervous system engineering
│       ├── SKILL.md
│       ├── breath-regulation/
│       ├── somatic-anchoring/
│       ├── arousal-control/
│       ├── audio-layering/
│       ├── exit-reintegration/
│       └── validation/
│
├── tier2-safety/
│   ├── psychological-stability/   # Integration monitoring
│   │   └── SKILL.md               # Triggers, response protocols
│   │
│   ├── christian-discernment/     # Theological governance
│   │   └── SKILL.md               # Entity detection, boundary tests
│   │
│   └── ethical-framing/           # Consent & agency preservation
│       └── SKILL.md               # Pre-talk requirements, checkpoints
│
├── tier3-production/              # (To be migrated from old structure)
│   ├── ssml-generation/
│   ├── voice-synthesis/
│   ├── audio-mixing/
│   ├── video-assembly/
│   └── youtube-packaging/
│
└── tier4-growth/                  # (Deferred for future)
    ├── analytics-learning/
    └── feedback-integration/
```

## SKILL.md Structure

Every skill has a master SKILL.md with:

```yaml
---
name: Skill Name
tier: 1|2|3|4
load_policy: always|triggered|task-specific|conditional
description: One-line purpose
version: 1.0.0
---

# Skill Name

## Purpose
What this skill manages

## Must Always
- Required behaviors

## Never
- Prohibited behaviors

## Sub-Skills
Links to sub-skill files

## Integration
Dependencies on other skills/knowledge

## Quality Rubric
Validation checklist
```

## Tier 1: Neural Core Skills

### 1. Hypnotic Language & Induction

**Purpose**: Control system for attention guidance and safe trance navigation.

**Sub-Skills**:
- `induction/`: soft-entry, attention-pacing, permissive-language
- `deepening/`: fractionation, time-distortion, imagery-coupling
- `suggestion/`: indirect-suggestion, values-alignment, metaphor-framing
- `emergence/`: reorientation, grounding, memory-integration
- `validation/`: depth-checks, dissociation-guards, forbidden-patterns

**Key Rules**:
- Always use `rate="1.0"` in SSML (pacing via `<break>` tags)
- Permission markers every 3-4 sentences
- Never command, always invite
- Complete emergence sequence required

### 2. Symbolic & Archetypal Mapping

**Purpose**: Meaning engine that translates intention into safe symbolic experience.

**Key Rules**:
- Symbols are representations, not beings
- Archetypes are functional roles, not authorities
- Meaning-making belongs to listener
- All imagery Christian-compatible

**Archetype Roles**:
- Guide: Points, never commands
- Pilgrim: Always the listener
- Healer: Facilitates, not power source
- Witness: Observes, never judges

### 3. Audio Layering & Somatic Cue

**Purpose**: Nervous system engineering for embodied trance.

**Key Rules**:
- Voice always dominant (-6 dB reference)
- Somatic anchors every 1-3 minutes
- Never float/dissolve without grounding
- Breath-paced speech (exhale > inhale)

## Tier 2: Safety Skills

### 1. Psychological Stability Monitoring

**Triggers**:
- Deep trance language (Layer 3+)
- Identity/transformation work
- Trauma-adjacent content
- Prolonged visualization (>10 min)

**Response Levels**:
1. **Yellow**: Insert grounding, continue
2. **Orange**: Reduce depth, shift to grounding
3. **Red**: Emergency emergence

### 2. Christian Discernment

**Three Boundary Tests**:
1. Does this honor God as source?
2. Is free will preserved?
3. Are only permitted presences invoked?

**Entity Rules**:
- God/Christ/Spirit: Invited, not commanded
- Angels: Messengers only, not authorities
- Inner wisdom: Must trace to God
- Spirit guides: FORBIDDEN

### 3. Ethical Framing

**Pre-Talk Requirements**:
- Safety statement
- Depth consent
- Exit availability

**Forbidden Patterns**:
- Coercion ("you must")
- Manipulation ("without realizing")
- Dependency ("only this can help")
- Fear-based motivation

## Skill Loading

### Always Load Together

Tier 1 skills must load as a bundle:
- hypnotic-language + symbolic-mapping + audio-somatic

*"Remove one, and the other two become dangerous."*

### Load Order

1. Tier 2 ethical-framing (always)
2. Tier 1 bundle (always)
3. Tier 2 psychological-stability (triggered)
4. Tier 2 christian-discernment (triggered)
5. Tier 3 production skills (per task)

## Integration Points

| Skill | Reads From |
|-------|------------|
| hypnotic-language | knowledge/hypnotic_patterns.yaml |
| symbolic-mapping | knowledge/archetypes.yaml, outcome_registry.yaml |
| audio-somatic | knowledge/binaural_presets.yaml, polyvagal_theory.yaml |
| christian-discernment | theological-filters/ |

## Agent Integration

Agents declare tiered skills:

```yaml
# script-writer.md
skills_required:
  tier1: [hypnotic-language, symbolic-mapping]
  tier2: [psychological-stability, christian-discernment]
  tier3: [ssml-generation, voice-synthesis]
```

## Validation Flow

1. **Generation**: Skills guide content creation
2. **Post-Generation**: validation/ sub-skills check output
3. **Tier 2 Triggers**: Override if safety concerns
4. **Final Check**: validate_ssml.py, validate_skill_compliance.py

## Key Safety Principles

1. **Agency Always**: Listener chooses everything
2. **Body Connected**: Somatic anchors prevent dissociation
3. **God as Source**: All good traced to divine
4. **Complete Emergence**: Never leave someone in trance
5. **Tiered Response**: Yellow → Orange → Red protocols

## Quick Reference

### For Script Generation

1. Check outcome in manifest
2. Load Tier 1 bundle
3. Apply theological filters
4. Insert agency checkpoints (every 3-5 min)
5. Include complete emergence
6. Run validation

### For Audio Production

1. Voice: -6 dB
2. Binaural: -6 dB  
3. SFX: 0 dB
4. Target: -14 LUFS
5. Run hypnotic post-processing

### For Safety Triggers

- Dissociation signs → Emergency grounding
- Theological drift → Content replacement
- Agency concerns → Agency checkpoint insertion
- Depth exceeded → Ceiling enforcement
