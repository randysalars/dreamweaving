# Archetype Feature Documentation

**VERSION:** 1.0
**STATUS:** ✅ PRODUCTION READY
**LAST UPDATED:** 2025-11-30

## Overview

The archetype feature allows you to document symbolic characters and elements in your meditation journeys. These archetypes automatically enhance YouTube descriptions with rich narrative context.

---

## How to Use

### 1. Define Archetypes in manifest.yaml

Add an `archetypes` section to your session manifest:

```yaml
archetypes:
  - name: "The Navigator"
    role: "cosmic_guidance"
    description: "Ancient wisdom keeper who charts patterns through consciousness"
    appearance_time: 540  # When introduced (seconds)
    qualities: ["pattern recognition", "cosmic mapping", "sacred geometry"]

  - name: "The Starship ATLAS"
    role: "vessel_of_transformation"
    description: "Living ship that bridges ancient wisdom and future technology"
    appearance_time: 720
    qualities: ["sacred technology", "time-space navigation", "consciousness interface"]

  - name: "The Pathfinder"
    role: "pattern_weaver"
    description: "Guide who reveals hidden connections in the cosmic tapestry"
    appearance_time: 1000
    qualities: ["synchronicity", "connection", "revelation"]
```

### 2. Auto-Generated Descriptions

When you run `package_youtube.py`, the archetypes section automatically generates:

```markdown
## 🎭 Journey Archetypes

This meditation journey features symbolic encounters with:

**The Navigator** - Cosmic Guidance
  Ancient wisdom keeper who charts patterns through consciousness
  *Qualities: pattern recognition, cosmic mapping, sacred geometry*

**The Starship ATLAS** - Vessel Of Transformation
  Living ship that bridges ancient wisdom and future technology
  *Qualities: sacred technology, time-space navigation, consciousness interface*

**The Pathfinder** - Pattern Weaver
  Guide who reveals hidden connections in the cosmic tapestry
  *Qualities: synchronicity, connection, revelation*
```

---

## Archetype Fields

| Field | Required | Description | Example |
|-------|----------|-------------|---------|
| `name` | Yes | Name of the archetype | "The Navigator" |
| `role` | Yes | Function in the journey | "cosmic_guidance" |
| `description` | Yes | Brief description | "Ancient wisdom keeper..." |
| `appearance_time` | Yes | When introduced (seconds) | 540 |
| `qualities` | Optional | List of qualities/attributes | ["wisdom", "direction"] |

---

## Common Archetype Roles

Here are suggested role types for consistency:

- `guidance` - Wise guides and mentors
- `vessel_of_transformation` - Ships, vehicles, containers
- `cultivation` - Gardeners, nurturers, builders
- `revelation` - Revealers, pathfinders, illuminators
- `protection` - Guardians, shields, protectors
- `healing` - Healers, restorers, balancers
- `cosmic_guidance` - Stellar navigators, cosmic mappers
- `pattern_weaver` - Connection makers, synchronicity guides
- `time_keeper` - Temporal guides, past/future bridges

---

## Benefits

### 1. Enhanced YouTube Descriptions
- Richer narrative context for viewers
- Better SEO with descriptive keywords
- Professional presentation of symbolic elements

### 2. Documentation
- Track symbolic elements across sessions
- Reference for future script writing
- Build a consistent archetype library

### 3. Future AI Integration
- Enable AI-assisted script generation from archetypes
- Template-based journey creation
- Pattern analysis across sessions

### 4. Session Categorization
- Group sessions by archetype themes
- Discover archetypal patterns in your work
- Build thematic series

---

## Example: Garden of Eden Session

```yaml
archetypes:
  - name: "The Gardener"
    role: "cultivation"
    description: "Divine cultivator of consciousness and possibility"
    appearance_time: 300
    qualities: ["nurturing", "growth", "sacred tending"]

  - name: "The Tree of Knowledge"
    role: "vessel_of_wisdom"
    description: "Living library of infinite understanding"
    appearance_time: 600
    qualities: ["wisdom", "connection", "rootedness"]

  - name: "The Serpent Guide"
    role: "revelation"
    description: "Revealer of hidden truths and transformations"
    appearance_time: 900
    qualities: ["transformation", "shedding", "rebirth"]
```

---

## Example: Neural Network Navigator Session

```yaml
archetypes:
  - name: "The Neural Navigator"
    role: "guidance"
    description: "Guide through the landscape of consciousness"
    appearance_time: 400
    qualities: ["mapping", "connection", "exploration"]

  - name: "The Network Weaver"
    role: "pattern_weaver"
    description: "Weaver of neural pathways and connections"
    appearance_time: 800
    qualities: ["integration", "linking", "strengthening"]

  - name: "The Gamma Burst"
    role: "revelation"
    description: "Moment of cosmic insight and clarity"
    appearance_time: 1240
    qualities: ["illumination", "breakthrough", "activation"]
```

---

## Workflow Integration

The archetype feature is **fully integrated** into the automated workflow:

### Single Command Production

```bash
python3 scripts/core/build_session.py \
  --session sessions/my-session \
  --ssml sessions/my-session/script.ssml \
  --auto-package
```

This automatically:
1. ✅ Reads archetypes from manifest.yaml
2. ✅ Generates archetype-enriched YouTube description
3. ✅ Creates complete YouTube package

### Manual YouTube Package

```bash
python3 scripts/core/package_youtube.py \
  --session sessions/my-session
```

Archetypes are automatically included in the description.

---

## Best Practices

### 1. Consistent Naming
- Use "The [Name]" format for clarity
- Examples: "The Navigator", "The Gardener", "The Starship"

### 2. Meaningful Roles
- Use descriptive role names
- Match role to archetype function
- Use underscores for multi-word roles: `cosmic_guidance`

### 3. Rich Descriptions
- 1-2 sentences describing essence
- Focus on symbolic meaning
- Avoid technical jargon

### 4. Timing
- Set `appearance_time` to when archetype is introduced
- Use seconds from start of session
- Align with section timing if possible

### 5. Quality Lists
- Choose 2-4 key qualities
- Use single words or short phrases
- Focus on essential attributes

---

## Optional vs Required

**Archetypes are OPTIONAL** - the workflow works perfectly without them:

- If no archetypes defined → No archetype section in description
- If archetypes defined → Automatic archetype section added
- Backward compatible with existing sessions

---

## Template Reference

The enhanced template is at: [sessions/_template/manifest.yaml](../sessions/_template/manifest.yaml)

Example archetype definitions are included as commented-out examples.

---

## Future Enhancements

Planned features for archetypes:

1. **VTT Integration** - Show archetype names in subtitles at appearance time
2. **AI Script Generation** - Generate journey scripts from archetype templates
3. **Archetype Library** - Reusable archetype definitions across sessions
4. **Image Association** - Link specific images to archetype appearances
5. **Thematic Analysis** - Pattern detection across sessions

---

**Created**: 2025-11-30
**Maintainer**: Randy Sailer
**Status**: Production Ready ✅
