# Archetype System SOP

## Overview

The Dreamweaving Archetype System provides 100 recurring archetypal figures across 12 families, with cross-tradition equivalents, session tracking, and automatic SSML template injection.

## Key Concepts

### Archetype Families (12 Total)

| Family | Description | Primary Outcomes | Element |
|--------|-------------|------------------|---------|
| `divine_light_healing` | Restoration, regeneration | healing, transformation | water |
| `transformation_alchemy` | Death/rebirth, shadow work | transformation, release | fire |
| `oracle_seer` | Intuition, prophecy | self_knowledge, spiritual_growth | air |
| `warrior_power` | Courage, protection, strength | empowerment, confidence | fire |
| `divine_feminine` | Wisdom, compassion, creativity | creativity, healing | water |
| `divine_masculine` | Structure, purpose, direction | empowerment, focus | fire |
| `ascension_lightbody` | Transcendence, enlightenment | spiritual_growth, transformation | spirit |
| `shamanic_earth` | Nature, grounding, animal allies | healing, relaxation | earth |
| `mental_intelligence` | Cognition, memory, learning | focus, creativity | air |
| `emotional_heart` | Love, joy, compassion | healing, relaxation | water |
| `abundance_destiny` | Prosperity, opportunity, calling | abundance, empowerment | earth |
| `dreamweaver_meta` | Storytelling, world-shaping | all outcomes | spirit |

### Archetype IDs

Format: `{family}.{archetype_name}`

Examples:
- `divine_light_healing.inner_healer`
- `warrior_power.archangel_michael`
- `transformation_alchemy.phoenix_renewal`

### Encounter Types

| Type | When to Use | Relationship Level |
|------|-------------|-------------------|
| `first_encounter` | Listener's first meeting | 1 (New) |
| `return_encounter` | Listener has met before | 2-3 (Familiar/Deep) |
| `transformation` | Deep integration work | 3-4 (Deep/Mastered) |
| `integration` | Final anchoring | 4 (Mastered) |

### Relationship Levels

| Level | Name | Sessions Required | Notes |
|-------|------|------------------|-------|
| 1 | New | 1 | First encounter |
| 2 | Familiar | 2+ | Can use abbreviated intros |
| 3 | Deep | 4+ | Strong relationship |
| 4 | Mastered | 7+ | Fully integrated |

---

## File Locations

### Knowledge Files

| File | Purpose |
|------|---------|
| `knowledge/archetypes/archetype_codex.yaml` | Master archetype registry (100 archetypes) |
| `knowledge/archetypes/archetype_history.yaml` | Session tracking and relationships |
| `knowledge/indexes/archetype_family_index.yaml` | Family-to-archetype mappings |
| `knowledge/indexes/tradition_equivalence_index.yaml` | Cross-tradition name mappings |
| `knowledge/indexes/color_frequency_map.yaml` | Visual/audio attributes |

### Utility Scripts

| Script | Purpose |
|--------|---------|
| `scripts/utilities/archetype_selector.py` | Intelligent archetype selection |
| `scripts/utilities/expand_archetypes.py` | Template tag expansion |
| `scripts/utilities/validate_archetypes.py` | Validation utility |

---

## Usage Workflows

### 1. Selecting Archetypes for a Session

The `ArchetypeSelector` class handles intelligent selection:

```python
from scripts.utilities.archetype_selector import ArchetypeSelector

selector = ArchetypeSelector()

# Select archetypes for a healing journey
archetypes = selector.select_archetypes(
    outcome='healing',
    journey_phases=['journey', 'integration'],
    count=3,
    prefer_recurring=True,
    tradition='christian'  # Optional: use Christian names
)

for arch in archetypes:
    print(f"{arch.name} ({arch.encounter_type})")
```

**Selection Algorithm:**
1. Filter by outcome alignment
2. Score by journey phase match
3. Apply relationship bonus for recurring archetypes
4. Apply recency penalty (avoid overuse)
5. Ensure family diversity

### 2. Using Archetype Template Tags

In SSML scripts, use template tags:

```xml
<!-- Basic tag (uses first_encounter by default) -->
{{ARCHETYPE:divine_light_healing.inner_healer}}

<!-- With explicit encounter type -->
{{ARCHETYPE:warrior_power.archangel_michael:first_encounter}}

<!-- Return encounter for recurring archetype -->
{{ARCHETYPE:divine_feminine.rose_mother:return_encounter}}
```

### 3. Expanding Template Tags

```bash
# Expand tags in script
python scripts/utilities/expand_archetypes.py \
    sessions/my-session/working_files/script.ssml \
    sessions/my-session/working_files/script_expanded.ssml

# With tradition-specific names
python scripts/utilities/expand_archetypes.py \
    input.ssml output.ssml \
    --tradition hindu

# Auto-detect encounter types from history
python scripts/utilities/expand_archetypes.py \
    input.ssml output.ssml \
    --auto-detect
```

### 4. Validating Archetypes

```bash
# Validate a session
python scripts/utilities/validate_archetypes.py sessions/my-session/ -v

# Validate the codex itself
python scripts/utilities/validate_archetypes.py --check-codex
```

### 5. Updating History After Session

```python
from scripts.utilities.archetype_selector import ArchetypeSelector

selector = ArchetypeSelector()

# After session completion
selector.update_history(
    session_id='my-session-001',
    archetypes_used=selected_archetypes,
    session_date='2025-12-09',
    outcome='healing'
)
```

---

## Manifest Schema

In `manifest.yaml`, archetypes use this structure:

```yaml
archetypes:
  - archetype_id: "divine_light_healing.inner_healer"
    name: "The Inner Healer"
    role: "primary"
    encounter_type: "first_encounter"
    relationship_level: 1
    appearance_section: "journey"

  - archetype_id: "transformation_alchemy.phoenix_renewal"
    name: "The Phoenix of Renewal"
    role: "secondary"
    encounter_type: "first_encounter"
    relationship_level: 1
    appearance_section: "helm_deep_trance"
```

### Required Fields
- `archetype_id` - Reference to codex
- `role` - primary, secondary, supporting, transitional

### Optional Fields
- `encounter_type` - first_encounter, return_encounter, transformation
- `relationship_level` - 1-4
- `appearance_section` - pre_talk, induction, journey, etc.
- `tradition` - Use tradition-specific naming
- `ssml_template_override` - Custom SSML

---

## Tradition Equivalents

Each archetype can have names in multiple traditions:

| Archetype | Christian | Hindu | Buddhist | Egyptian |
|-----------|-----------|-------|----------|----------|
| inner_healer | Holy Spirit Healer | Dhanvantri | Medicine Buddha | Isis |
| archangel_michael | Archangel Michael | Kartikeya | Manjushri | Horus |
| rose_mother | Virgin Mary | Divine Mother | Kuan Yin | Isis |
| phoenix_renewal | Resurrection | Shiva/Shakti | Ego Death | Bennu Bird |

Use the `--tradition` flag or `tradition` manifest field to apply.

---

## Adding New Archetypes

### 1. Define in Codex

Add to `knowledge/archetypes/archetype_codex.yaml`:

```yaml
archetypes:
  new_archetype_name:
    archetype_id: "family_name.new_archetype_name"
    name: "Display Name"
    family: family_name

    definition:
      brief: "One-line description"
      extended: |
        Detailed description of the archetype's role,
        origin, and psychological function.

    attributes:
      primary_color: gold
      secondary_color: white
      frequency_hz: 528
      brainwave_target: theta
      element: fire
      chakra: solar

    tradition_equivalents:
      christian: "Christian Name"
      hindu: "Hindu Name"
      buddhist: "Buddhist Name"

    applications:
      journey_phases: [journey, helm_deep_trance]
      outcome_alignment: [healing, transformation]

    templates:
      first_encounter_ssml: |
        <prosody rate="1.0" pitch="-1st">
        And now... <break time="2s"/>
        [Archetype introduction SSML]
        </prosody>

      return_encounter_ssml: |
        <prosody rate="1.0" pitch="-1st">
        [Shorter return greeting SSML]
        </prosody>

    relationships:
      synergies: [related_archetype_1, related_archetype_2]
      conflicts: []
```

### 2. Update Family Index

Add to `knowledge/indexes/archetype_family_index.yaml`:

```yaml
families:
  family_name:
    archetypes:
      - existing_archetype
      - new_archetype_name  # Add here
```

### 3. Add Tradition Equivalents

Update `knowledge/indexes/tradition_equivalence_index.yaml`:

```yaml
traditions:
  christian:
    archetypes:
      new_archetype_name: "Christian Name"
  hindu:
    archetypes:
      new_archetype_name: "Hindu Name"
```

### 4. Validate

```bash
python scripts/utilities/validate_archetypes.py --check-codex
```

---

## Best Practices

### Session Design

1. **Minimum 2 archetypes** per session
2. **Family diversity** - avoid all archetypes from same family
3. **One primary** archetype, 1-2 supporting
4. **Outcome alignment** - match archetypes to desired outcome

### SSML Templates

1. Always use `rate="1.0"` (normal speed)
2. Use `<break>` tags for pacing (2-4 seconds for archetype appearances)
3. Include sensory descriptions (visual, kinesthetic)
4. First encounters need more introduction than returns

### Recurring Archetypes

1. Track history for continuity
2. Use `return_encounter` for familiar archetypes
3. Reference previous sessions subtly
4. Deepen relationship over time

---

## Troubleshooting

### "Archetype not found in codex"

- Check spelling of archetype_id
- Verify family prefix matches codex entry
- Run `validate_archetypes.py --check-codex`

### "No template found"

- Ensure archetype has `templates.first_encounter_ssml`
- Check for `return_encounter_ssml` if using that type

### "Family mismatch"

- The family in `archetype_id` must match the `family` field
- Example: `divine_light_healing.inner_healer` requires `family: divine_light_healing`

### "Low family diversity warning"

- Add archetypes from different families
- Consider the outcome → family mappings in family index

---

## Quick Reference

### Commands

```bash
# Select archetypes programmatically
python -c "
from scripts.utilities.archetype_selector import ArchetypeSelector
s = ArchetypeSelector()
for a in s.select_archetypes('healing'): print(f'{a.archetype_id}: {a.name}')
"

# Expand template tags
python scripts/utilities/expand_archetypes.py input.ssml output.ssml

# Validate session
python scripts/utilities/validate_archetypes.py sessions/my-session/ -v

# Validate codex
python scripts/utilities/validate_archetypes.py --check-codex
```

### Template Tag Syntax

```
{{ARCHETYPE:family.name}}              # Default first_encounter
{{ARCHETYPE:family.name:first_encounter}}
{{ARCHETYPE:family.name:return_encounter}}
{{ARCHETYPE:family.name:transformation}}
```

### Manifest Fields

```yaml
archetypes:
  - archetype_id: "family.name"      # Required
    role: "primary"                   # Required: primary|secondary|supporting
    encounter_type: "first_encounter" # Optional
    relationship_level: 1             # Optional: 1-4
    appearance_section: "journey"     # Optional
    tradition: "christian"            # Optional
```
