# Archetype System Procedure

## Overview

The Dreamweaving Recurring Archetype System provides 100 archetypal figures across 12 families with cross-tradition equivalents, session tracking, and automatic SSML template injection.

## Key Files

### Knowledge Base
- `knowledge/archetypes/archetype_codex.yaml` - Master registry (20 archetypes defined, 100 planned)
- `knowledge/archetypes/archetype_history.yaml` - Session tracking and relationships
- `knowledge/indexes/archetype_family_index.yaml` - Family → archetypes mappings
- `knowledge/indexes/tradition_equivalence_index.yaml` - Cross-tradition name mappings
- `knowledge/indexes/color_frequency_map.yaml` - Visual/audio attributes

### Utility Scripts
- `scripts/utilities/archetype_selector.py` - Intelligent archetype selection
- `scripts/utilities/expand_archetypes.py` - Template tag expansion
- `scripts/utilities/validate_archetypes.py` - Validation utility

### Documentation
- `docs/ARCHETYPE_SYSTEM_SOP.md` - Complete usage documentation

## 12 Archetype Families

| Family | Description | Primary Outcomes |
|--------|-------------|------------------|
| `divine_light_healing` | Restoration, regeneration | healing |
| `transformation_alchemy` | Death/rebirth, shadow work | transformation |
| `oracle_seer` | Intuition, prophecy | self_knowledge |
| `warrior_power` | Courage, protection | empowerment |
| `divine_feminine` | Wisdom, compassion | creativity, healing |
| `divine_masculine` | Structure, purpose | empowerment, focus |
| `ascension_lightbody` | Transcendence | spiritual_growth |
| `shamanic_earth` | Nature, grounding | healing, relaxation |
| `mental_intelligence` | Cognition, memory | focus |
| `emotional_heart` | Love, joy | healing, relaxation |
| `abundance_destiny` | Prosperity, opportunity | abundance |
| `dreamweaver_meta` | Storytelling, world-shaping | all |

## Quick Commands

```bash
# Validate codex
python scripts/utilities/validate_archetypes.py --check-codex

# Select archetypes programmatically
python -c "
from scripts.utilities.archetype_selector import ArchetypeSelector
s = ArchetypeSelector()
for a in s.select_archetypes('healing'): print(f'{a.archetype_id}: {a.name}')
"

# Expand template tags in SSML
python scripts/utilities/expand_archetypes.py input.ssml output.ssml
```

## Template Tag Syntax

```xml
{{ARCHETYPE:family.name}}              <!-- Default first_encounter -->
{{ARCHETYPE:family.name:first_encounter}}
{{ARCHETYPE:family.name:return_encounter}}
{{ARCHETYPE:family.name:transformation}}
```

## Manifest Schema

```yaml
archetypes:
  - archetype_id: "divine_light_healing.inner_healer"
    role: "primary"  # primary|secondary|supporting|transitional
    encounter_type: "first_encounter"  # Optional
    relationship_level: 1  # Optional: 1-4
    appearance_section: "journey"  # Optional
    tradition: "christian"  # Optional: use tradition-specific naming
```

## Encounter Types

| Type | When to Use | Relationship Level |
|------|-------------|-------------------|
| `first_encounter` | First meeting | 1 (New) |
| `return_encounter` | Previously met | 2-3 (Familiar/Deep) |
| `transformation` | Deep work | 3-4 (Deep/Mastered) |
| `integration` | Final anchoring | 4 (Mastered) |

## Adding New Archetypes

1. Add entry to appropriate family in `archetype_codex.yaml`
2. Update `archetype_family_index.yaml` archetype list
3. Add tradition equivalents to `tradition_equivalence_index.yaml`
4. Run `python scripts/utilities/validate_archetypes.py --check-codex`

## Integration Points

- `scripts/ai/creative_workflow.py` - Uses ArchetypeSelector for session generation
- `config/manifest.schema.json` - Schema for archetype fields in manifests
- Template tags expanded before TTS generation
