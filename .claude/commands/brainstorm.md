---
name: brainstorm
description: Brainstorm journey concepts for a topic and create the best one
arguments:
  - name: topic
    required: true
    description: The topic or theme for the dreamweaving journey
agent: dreamweaver
---

# /brainstorm Command

Brainstorm multiple journey concepts for a topic, select the best one, and optionally generate the complete session.

## Usage
```
/brainstorm <topic>
```

## Examples
```
/brainstorm healing from grief
/brainstorm building confidence
/brainstorm connecting with higher self
/brainstorm releasing anxiety
/brainstorm abundance and prosperity
```

## Process

### Phase 1: Analysis
1. **Identify therapeutic focus**
   - Parse topic for keywords
   - Determine primary therapeutic goal
   - Map to appropriate brainwave states

### Phase 2: Brainstorming (5 concepts)
2. **Generate journey concepts**
   - Create 5 unique journey concepts
   - Each with different:
     - Setting/imagery style (cosmic, nature, mystical, underwater, inner)
     - Metaphor and transformation arc
     - Archetype selection (2-4 per journey)
     - Binaural progression
     - Sound effects

### Phase 3: Scoring & Selection
3. **Score each concept**
   - Coherence (setting matches focus)
   - Archetype depth
   - Binaural appropriateness
   - Sound design quality
   - Duration feasibility

4. **Select best journey**
   - Highest scoring concept
   - Consider audience preferences if specified

### Phase 4: Output
5. **Generate outputs**
   - Display all concepts with scores
   - Present selected concept in detail
   - Optionally generate manifest.yaml
   - Optionally proceed to script generation

## What Gets Generated

For each concept:
- **Title**: Compelling name for the journey
- **Setting**: Where the journey takes place
- **Metaphor**: Core symbolic framework
- **Transformation**: Key change/outcome
- **Archetypes**: Guide figures and symbols
- **Binaural Progression**: Frequency map for the journey
- **Sound Effects**: Atmospheric audio layers
- **Voice Recommendation**: Best voice for the content

## Therapeutic Focus Mappings

| Topic Keywords | Therapeutic Focus | Primary Brainwave |
|---------------|-------------------|-------------------|
| grief, loss, letting go | healing/grief | theta |
| anxiety, calm, peace | anxiety relief | alpha |
| confidence, power, voice | confidence | alpha/beta |
| sleep, rest, surrender | sleep | delta |
| spiritual, divine, source | spiritual | theta |
| abundance, wealth, prosperity | abundance | alpha |
| creativity, inspiration | creativity | theta |
| transformation, change | transformation | theta |

## Binaural Templates

- **Deep Journey Arc**: Classic descent into theta/delta with gamma burst
- **Healing Waters**: Gentle theta with delta dips
- **Empowerment Arc**: Alpha-dominant with gamma peaks
- **Sleep Descent**: Gradual delta descent, no return
- **Transcendence Path**: Deep theta with gamma enlightenment

## Archetype Roles

- **Guidance**: Navigator, Wise Elder, Star Guide
- **Transformation**: Alchemist, Phoenix, Butterfly
- **Wisdom Keeper**: Scribe, Oracle, Librarian
- **Healing**: Healer, Water Bearer, Garden Tender
- **Higher Self**: Future Self, Inner Light, Soul Star
- **Vessel**: Sacred Ship, Temple, Cocoon

## Follow-up Commands

After brainstorming, you can:
```
/generate-manifest <session>  # Create full manifest from concept
/generate-script <session>    # Generate the SSML script
/full-build <session>         # Complete production pipeline
```

## Integration with Creative Workflow

This command uses `scripts/ai/creative_workflow.py` which provides:
- `brainstorm_journeys()`: Generate multiple concepts
- `score_journey()`: Evaluate concept quality
- `select_best_journey()`: Choose optimal concept
- `generate_manifest()`: Create manifest.yaml
- `brainstorm_and_create()`: Complete workflow

## Example Output

```
BRAINSTORMED JOURNEY CONCEPTS
=============================

--- Concept 1: Voyage to the Healing Star (Score: 0.87) ---
Setting: aboard a sentient starship traveling between dimensions
Metaphor: a sentient nebula that absorbs pain and radiates renewal
Transformation: emerging whole, renewed, and radiating vitality

Archetypes:
  - The Healer (healing): Compassionate presence of restoration
  - The Navigator (guidance): Wise guide through unknown territories
  - The Future Self (higher_self): Your evolved presence from beyond time

Binaural: Healing Waters
  Gentle theta with delta dips for cellular healing

Sound Effects:
  - Cosmic Hum: Deep resonance of space
  - Star Whispers: Distant stellar communication

--- SELECTED: Concept 1 ---
```
