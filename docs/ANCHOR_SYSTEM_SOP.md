# Anchor System SOP - Post-Hypnotic Anchors for Dreamweaving

## Overview

The anchor system provides a comprehensive library of 100+ post-hypnotic anchors across 10 categories. These anchors link specific triggers (breath patterns, gestures, visualizations, sounds) to desired states (calm, focus, healing, confidence).

## Key Files

| File | Purpose |
|------|---------|
| `knowledge/anchors/anchor_registry.yaml` | Master registry of all anchors (100 entries) |
| `knowledge/anchors/anchor_schema.yaml` | Entry format specification |
| `scripts/utilities/anchor_selector.py` | Selection and query utility |
| `scripts/utilities/expand_anchors.py` | Template tag expansion |
| `scripts/utilities/validate_nlp.py` | Anchor variety validation |

## Anchor Categories (10)

| Category | ID Prefix | Trigger Type | Examples |
|----------|-----------|--------------|----------|
| **Breath** | `breath.` | Physical | calm_breath_slow_exhale, power_breath_chest_lift |
| **Auditory** | `auditory.` | Auditory | soft_chime_depth, rain_on_roof |
| **Visual** | `visual.` | Visual | blue_flame_focus, golden_sphere_abundance |
| **Kinesthetic** | `kinesthetic.` | Physical | heart_touch_calm, fist_squeeze_power |
| **Symbolic** | `symbolic.` | Mental | phoenix_feather_rise, shield_of_protection |
| **Portal** | `portal.` | Mental | staircase_10_down, garden_gate_peace |
| **Verbal** | `verbal.` | Verbal | phrase_i_am_safe, mantra_peace_within |
| **Musical** | `musical.` | Auditory | gong_wash_reset, theta_wave_journey |
| **Nature** | `nature.` | Sensory | sunbeam_on_skin, forest_sanctuary |
| **Daily Life** | `daily_life.` | Environmental | doorway_reset, shower_ritual_cleanse |

## Using Anchors in Scripts

### Template Tag Syntax

Place anchor tags in your SSML scripts:

```xml
<!-- Integration section -->
<prosody rate="1.0" pitch="-1st">
And now I want to give you some powerful anchors...<break time="2s"/>

{{ANCHOR:kinesthetic.heart_touch_calm}}

{{ANCHOR:breath.calm_breath_slow_exhale}}

{{ANCHOR:verbal.phrase_i_am_safe}}
</prosody>
```

### Expanding Tags

Before voice generation, expand anchor tags to actual SSML:

```bash
# Full installation mode (default)
python3 scripts/utilities/expand_anchors.py \
    working_files/script.ssml \
    working_files/script_expanded.ssml

# Reinforcement mode (shorter SSML)
python3 scripts/utilities/expand_anchors.py \
    working_files/script.ssml \
    working_files/script_expanded.ssml \
    --mode reinforcement

# Dry run to see what would be replaced
python3 scripts/utilities/expand_anchors.py \
    working_files/script.ssml \
    --dry-run
```

## Programmatic Selection

Use the anchor selector for intelligent anchor selection:

```python
from scripts.utilities.anchor_selector import AnchorSelector

selector = AnchorSelector()

# Select anchors for a healing session
anchors = selector.select_anchors(
    outcome="healing",
    journey_phases=["integration", "reorientation"],
    count=5
)

# Get SSML for a specific anchor
ssml = selector.get_anchor_ssml(
    "kinesthetic.heart_touch_calm",
    mode="installation"  # or "reinforcement"
)

# Query by criteria
results = selector.query_anchors(
    outcome="confidence",
    categories=["breath", "kinesthetic"],
    state_tags=["power", "strength"]
)
```

## Selection Algorithm

The selector uses a scoring algorithm that considers:

1. **Outcome Alignment** - Anchors matching the session's desired_outcome score higher
2. **Phase Compatibility** - Anchors appropriate for the current journey phase
3. **Recency Penalty** - Recently used anchors (last 3 sessions) score lower
4. **Category Diversity** - Ensures variety across anchor types
5. **Synergy Bonus** - Anchors that work well together score higher

## Manifest Integration

Add anchors to session manifests:

```yaml
# In manifest.yaml
anchors:
  - anchor_id: "kinesthetic.heart_touch_calm"
    name: "Heart Touch - Instant Calm"
    category: kinesthetic
    recall_phrase: "Hand on heart, peace arrives"
    state_tags: [calm, healing, connection]
    installation_context: in_closing

  - anchor_id: "breath.calm_breath_slow_exhale"
    name: "Calm Breath - Slow Exhale"
    category: breath
    recall_phrase: "Slow exhale, calm arrives"
    state_tags: [calm, grounding, release]
    installation_context: during_induction
```

## YouTube Description Integration

Anchors are automatically included in YouTube descriptions when present in the manifest:

```markdown
## Post-Hypnotic Anchors

This session installs these powerful anchors for future use:

**Heart Touch - Instant Calm** (Kinesthetic)
  *Trigger: Hand on heart, peace arrives*

**Calm Breath - Slow Exhale** (Breath)
  *Trigger: Slow exhale, calm arrives*

_These anchors strengthen with repeated listening._
```

## Validation Requirements

The NLP validator checks for anchor variety:

| Requirement | Minimum |
|-------------|---------|
| Total anchors | 3 |
| Different categories | 2 |
| Body-based anchor | 1 (breath, kinesthetic, or nature) |
| Mental anchor | 1 (symbolic, verbal, or visual) |

Run validation:

```bash
python3 scripts/utilities/validate_nlp.py script.ssml --verbose
```

## Anchor Entry Schema

Each anchor in the registry follows this structure:

```yaml
anchor_id: "category.anchor_name"  # e.g., "kinesthetic.heart_touch_calm"
name: "Human Readable Name"
category: kinesthetic  # One of 10 categories
trigger_type: physical  # physical|sensory|symbolic|auditory|visual|verbal|environmental

definition:
  brief: "One-line description"
  extended: |
    Full explanation of the anchor mechanism,
    psychology, and how it works.

attributes:
  state_tags: [calm, healing, connection]  # Max 5 from allowed list
  intensity: moderate  # subtle|moderate|strong|profound
  modality: physical   # physical|mental|emotional|spiritual|combined
  duration_effect: short  # instant|short|medium|long|permanent
  cumulative: true  # Strengthens with repeated use

applications:
  journey_phases: [integration, reorientation]
  outcome_alignment: [healing, relaxation, confidence]
  installation_context: in_closing
  contraindications: []

templates:
  installation_ssml: |
    <prosody rate="1.0" pitch="-1st">
    Full SSML for anchor installation...
    Uses breaks for pacing, NEVER slow rate.
    </prosody>

  reinforcement_ssml: |
    <prosody rate="1.0" pitch="-1st">
    Shorter SSML for reinforcing existing anchor...
    </prosody>

  recall_phrase: "Short trigger phrase for daily use"
  sfx_cue: "Suggested sound effect"
  visual_imagery: "Imagery description"

relationships:
  synergies: ["other.anchor_id"]  # Works well with
  conflicts: []  # Should not be used together
  progressions: []  # More advanced anchors to progress to
```

## SSML Template Rules

All anchor SSML templates MUST follow these rules:

1. **Rate = 1.0** - Always use `rate="1.0"`. Never slow the rate.
2. **Use Breaks** - Achieve pacing through `<break>` tags
3. **Break Durations**:
   - Between phrases: 1.5s-2s
   - After key suggestions: 2s-3s
   - Major pauses: 3s-5s
4. **Prosody** - Use pitch adjustment for depth (`pitch="-1st"`)

## Best Practices

### Anchor Selection for Sessions

1. **Match outcome** - Select anchors aligned with session's desired_outcome
2. **Vary categories** - Use at least 2-3 different anchor types
3. **Include body-based** - Always have at least one physical/kinesthetic anchor
4. **Consider context** - Use installation_context to place anchors appropriately
5. **Check synergies** - Prefer anchors that synergize with each other

### Installation Timing

| Installation Context | When to Use |
|---------------------|-------------|
| `during_induction` | Early relaxation anchors (breath, grounding) |
| `during_deepening` | Deepening aids (portal, musical) |
| `during_journey` | Journey-specific anchors |
| `at_peak` | Most powerful/transcendent anchors |
| `during_integration` | Processing anchors |
| `in_closing` | Take-home anchors for daily use |
| `daily_practice` | Anchors designed for everyday triggers |

### Repetition and Reinforcement

- Use `reinforcement_ssml` for anchors installed in previous sessions
- Track anchor usage in `anchor_history.yaml` to avoid over-repetition
- Allow 3+ sessions before reusing the same anchor

## Extending the Registry

To add new anchors:

1. Follow the schema in `anchor_schema.yaml`
2. Add to appropriate category section in `anchor_registry.yaml`
3. Ensure SSML uses `rate="1.0"` with proper breaks
4. Define relationships (synergies, conflicts)
5. Run validation to verify format

Example minimal entry:

```yaml
new_anchor_name:
  anchor_id: "category.new_anchor_name"
  name: "Display Name"
  category: category
  trigger_type: physical
  definition:
    brief: "Brief description"
  attributes:
    state_tags: [calm, focus]
    intensity: moderate
    modality: physical
  applications:
    journey_phases: [integration]
    outcome_alignment: [relaxation]
    installation_context: in_closing
  templates:
    installation_ssml: |
      <prosody rate="1.0" pitch="-1st">
      Anchor installation text...<break time="2s"/>
      </prosody>
    recall_phrase: "Recall trigger phrase"
  relationships:
    synergies: []
    conflicts: []
    progressions: []
```

## Quick Reference

### Common Anchor Combinations

**Healing Sessions:**
- `kinesthetic.heart_touch_calm`
- `breath.calm_breath_slow_exhale`
- `visual.emerald_healing_sphere`
- `symbolic.chalice_of_healing`

**Confidence Sessions:**
- `breath.power_breath_chest_lift`
- `kinesthetic.spine_alignment_power`
- `verbal.phrase_i_am_protected`
- `visual.mountain_peak_clarity`

**Relaxation Sessions:**
- `breath.ocean_wave_breath`
- `nature.ocean_shore_peace`
- `auditory.rain_on_roof`
- `daily_life.bedtime_gratitude_close`

**Spiritual Growth Sessions:**
- `portal.rainbow_bridge_connection`
- `visual.starlight_connection`
- `musical.celestial_choir_transcend`
- `nature.moonlight_wisdom`

### Troubleshooting

| Issue | Solution |
|-------|----------|
| Anchor tag not expanding | Check anchor_id spelling matches registry |
| Validation failing | Ensure min 3 anchors, 2 categories, body+mental |
| SSML sounds robotic | Verify rate="1.0", add more breaks |
| Same anchors every session | Check anchor_history.yaml for usage tracking |
