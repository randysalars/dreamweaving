# Knowledge Base Standard Operating Procedure

## Overview

This document defines the standard procedure for adding new knowledge entries to the Dreamweaving knowledge base. Following this procedure ensures proper indexing, cross-referencing, and integration with the agent retrieval system.

---

## Quick Reference Checklist

When adding new knowledge content, complete ALL applicable steps:

```
[ ] 1. Create/update the knowledge YAML file in appropriate domain folder
[ ] 2. Register file in knowledge/indexes/domain_index.yaml
[ ] 3. If outcome-related: Update knowledge/indexes/outcome_index.yaml
[ ] 4. If outcome-related: Update knowledge/outcome_registry.yaml
[ ] 5. Run validation: python scripts/utilities/validate_knowledge.py
[ ] 6. Test retrieval: python scripts/utilities/query_knowledge.py
```

---

## Step 1: Create the Knowledge File

### Location
Place files in the appropriate domain folder under `knowledge/`:

| Domain | Folder | Content Type |
|--------|--------|--------------|
| `symbols` | `knowledge/symbols/` | Elements, colors, geometry, correspondences |
| `audio` | `knowledge/audio/` | Binaural presets, soundscapes, frequencies |
| `traditions` | `knowledge/traditions/` | Mystical traditions, esoteric systems |
| `dream_work` | `knowledge/dream_work/` | Dream techniques, liminal states |
| `consciousness_maps` | `knowledge/consciousness_maps/` | Enlightenment frameworks, stage models |
| `psychology` | `knowledge/psychology/` | Therapeutic modalities, hypnosis, NLP |
| `ritual` | `knowledge/ritual/` | Invocation, prayer, ceremonial sequences |
| `mythology` | `knowledge/mythology/` | Pantheons, archetypes, narrative structures |
| `embodiment` | `knowledge/embodiment/` | Breath work, somatic practices |
| `science` | `knowledge/science/` | Scientific frameworks, research models |
| `session_learnings` | `knowledge/session_learnings/` | Production session learnings (meta) |
| `code_improvements` | `knowledge/code_improvements/` | Technical improvements (meta) |

### File Naming
- Use `lowercase_with_underscores.yaml`
- Be descriptive: `abundance_mindset.yaml`, `manifestation_technology.yaml`

### Entry Schema
Follow the schema defined in `knowledge/schema.yaml`. Required fields:

```yaml
entry_id: "domain.category.name"  # e.g., "psychology.abundance.scarcity_deprogramming"
name: "Human Readable Name"
domain: "psychology"  # Must match parent folder
category: "abundance"

definition:
  brief: "One-sentence definition (max 150 chars)"
  extended: |
    Detailed explanation (2-5 paragraphs)

applications:
  journey_phases: [induction, journey, integration]  # Where this applies
  outcome_alignment: [abundance, manifestation]       # Which outcomes it supports

templates:
  ssml_snippet: |
    <prosody rate="1.0" pitch="-1st">
    Template text with <break time="2s"/> tags...
    </prosody>

relationships:
  synergies: [other.entry.ids]
  related_patterns: [pattern_names]
```

---

## Step 2: Register in Domain Index

Update `knowledge/indexes/domain_index.yaml`:

### 2a. Add File Entry
Find the appropriate domain section and add the file:

```yaml
domains:
  psychology:
    description: "Psychology, hypnosis, and therapeutic modalities"
    status: "active"  # Set to "active" if domain has active files
    files:
      # ... existing files ...
      your_new_file:
        path: "psychology/your_new_file.yaml"
        entries: [entry1, entry2, entry3]  # List main entry keys
        status: "active"
```

### 2b. Update Domain Status
If adding the first active file to a domain, change domain status:
```yaml
status: "active"  # Was "pending"
```

### 2c. Update Statistics
At the bottom of the file, update:
```yaml
statistics:
  total_domains: 12      # Increment if adding new domain
  total_files: 75        # Increment for new file
  files_active: 9        # Increment if file is active
  files_pending: 66      # Adjust accordingly
  last_entry_added: "2025-12-05"  # Today's date
```

---

## Step 3: Update Outcome Index (If Applicable)

If your knowledge supports specific outcomes, update `knowledge/indexes/outcome_index.yaml`:

### 3a. Add/Update Outcome Entry
```yaml
outcomes:
  your_outcome:
    description: "Brief description of outcome"
    primary_domains:
      - psychology      # Most relevant domains
      - symbols
    secondary_domains:
      - ritual          # Supporting domains
    tertiary_domains:
      - science         # Optional enrichment
    key_entries:
      - psychology.your_category.entry1
      - psychology.your_category.entry2
    element_emphasis: earth      # fire, water, air, earth, spirit
    chakra_emphasis: root        # root, sacral, solar, heart, throat, third_eye, crown
    brainwave_target: alpha      # gamma, beta, alpha, theta, delta
```

### 3b. Update Reverse Indexes
Add outcome to the appropriate reverse indexes:

```yaml
element_outcomes:
  earth:
    primary: [abundance, your_outcome]  # Add here if primary
    secondary: [healing]                 # Or here if secondary

chakra_outcomes:
  root:
    outcomes: [abundance, your_outcome]

brainwave_outcomes:
  alpha:
    outcomes: [empowerment, confidence, your_outcome]
```

---

## Step 4: Update Outcome Registry (If Applicable)

If your knowledge defines a new outcome or significantly extends an existing one, update `knowledge/outcome_registry.yaml`:

### 4a. Add Outcome Definition
```yaml
outcomes:
  your_outcome:
    description: "Full description of outcome"
    subcategories:
      - subcategory1
      - subcategory2

    required_patterns:
      embedded_commands:
        minimum: 10
        emphasis_words: ["word1", "word2"]
        rationale: "Why this pattern is required"
      sensory_stacking:
        minimum: 3
        placement: "journey, helm"

    suggested_patterns:
      - fractionation_loops
      - temporal_dissociation

    advanced_patterns:
      schema_rewriting:
        required: true
        minimum: 1
        usage: "How to use this pattern"

    suggested_archetypes:
      primary: [archetype1, archetype2]
      secondary: [archetype3]

    suggested_journey_families:
      primary: [eden_garden, celestial_journey]
      secondary: [temple_initiation]

    suggested_objects:
      primary: [golden_key, seed_of_becoming]
      secondary: [glowing_stone]

    integration_actions:
      primary: [breath_trigger, hand_heart_anchor]
      secondary: [beauty_noticing]

    success_metrics:
      physiological:
        - "Physical indicator 1"
      emotional:
        - "Emotional indicator 1"
      behavioral:
        - "Behavioral indicator 1"

    brainwave_arc:
      start: alpha
      journey_peak: theta
      return: alpha
```

### 4b. Update Reference Indexes
Add entries to the reference indexes at the bottom:

```yaml
pattern_outcome_index:
  your_pattern:
    primary: [your_outcome]
    secondary: [related_outcome]

archetype_outcome_index:
  your_archetype:
    primary: [your_outcome]
    secondary: [related_outcome]

object_outcome_index:
  your_object:
    primary: [your_outcome]

family_outcome_index:
  your_journey_family:
    primary: [your_outcome]
```

---

## Step 5: Validate

Run the validation script to check for errors:

```bash
# Activate environment
source venv/bin/activate

# Full validation
python scripts/utilities/validate_knowledge.py

# Validate single file
python scripts/utilities/validate_knowledge.py --file psychology/your_file.yaml

# Skip cross-reference checks (faster)
python scripts/utilities/validate_knowledge.py --no-check-refs

# Skip index registration check
python scripts/utilities/validate_knowledge.py --no-check-index
```

### Common Validation Errors

| Error | Fix |
|-------|-----|
| "Entry missing 'domain' field" | Add `domain: "domain_name"` to entry |
| "Invalid entry_id format" | Use format `domain.category.name` |
| "File not registered in domain_index" | Add to domain_index.yaml |
| "SSML uses slow rate" | Change to `rate="1.0"`, use breaks for pacing |
| "Cross-reference not found" | Verify referenced entry_id exists |

---

## Step 6: Test Retrieval

Verify entries are queryable:

```bash
# List all outcomes
python scripts/utilities/query_knowledge.py --list-outcomes

# List all domains
python scripts/utilities/query_knowledge.py --list-domains

# Query specific outcome
python scripts/utilities/query_knowledge.py --outcome your_outcome --json

# Query specific domain
python scripts/utilities/query_knowledge.py --domain psychology

# Get specific entry
python scripts/utilities/query_knowledge.py --entry psychology.category.entry_name

# Get entries for a session
python scripts/utilities/query_knowledge.py --for-session sessions/your-session/manifest.yaml
```

---

## Example: Adding Abundance Knowledge

Here's a complete example of adding the `abundance_mindset.yaml` file:

### 1. Create File
`knowledge/psychology/abundance_mindset.yaml`:
```yaml
version: "1.0"
created: "2025-12-05"
domain: psychology
category: abundance_mindset

scarcity_deprogramming:
  entry_id: "psychology.abundance_mindset.scarcity_deprogramming"
  name: "Scarcity Deprogramming"
  domain: "psychology"
  category: "abundance_mindset"

  definition:
    brief: "Techniques for releasing scarcity beliefs and survival-mode patterns"
    extended: |
      Scarcity programming originates from evolutionary survival mechanisms...

  applications:
    journey_phases: [induction, journey, helm_deep_trance]
    outcome_alignment: [abundance, transformation, confidence]

  templates:
    ssml_snippet: |
      <prosody rate="1.0" pitch="-1st">
      And as you breathe... <break time="2s"/>
      notice how those old fears of not-enough... <break time="1.5s"/>
      begin to soften... <break time="2s"/>
      </prosody>
```

### 2. Register in Domain Index
```yaml
# In knowledge/indexes/domain_index.yaml
psychology:
  status: "active"
  files:
    abundance_mindset:
      path: "psychology/abundance_mindset.yaml"
      entries: [scarcity_deprogramming, abundance_archetypes, worthiness_work]
      status: "active"
```

### 3. Add to Outcome Index
```yaml
# In knowledge/indexes/outcome_index.yaml
outcomes:
  abundance:
    description: "Prosperity consciousness, wealth attraction"
    primary_domains: [psychology, symbols, embodiment]
    key_entries:
      - psychology.abundance_mindset.scarcity_deprogramming
    element_emphasis: earth
    chakra_emphasis: root
    brainwave_target: alpha
```

### 4. Add to Outcome Registry
```yaml
# In knowledge/outcome_registry.yaml
outcomes:
  abundance:
    description: "Cultivating prosperity consciousness..."
    required_patterns:
      embedded_commands:
        minimum: 10
        emphasis_words: ["abundant", "wealthy", "prosperous"]
    # ... full definition
```

### 5. Validate
```bash
python scripts/utilities/validate_knowledge.py
# Should show no errors for the new file
```

### 6. Test
```bash
python scripts/utilities/query_knowledge.py --outcome abundance --json
# Should return the new entries
```

---

## Maintenance Tasks

### Periodic Validation
Run full validation weekly or before major session builds:
```bash
python scripts/utilities/validate_knowledge.py 2>&1 | tee validation_report.txt
```

### Cross-Reference Audit
Check that all relationships are bidirectional:
- If A synergizes with B, B should synergize with A
- Update both entries when adding relationships

### Statistics Audit
Periodically verify statistics match actual file counts:
```bash
find knowledge -name "*.yaml" -type f | wc -l
```

---

## Tools Reference

| Tool | Purpose | Usage |
|------|---------|-------|
| `validate_knowledge.py` | Validate entries against schema | `python scripts/utilities/validate_knowledge.py` |
| `query_knowledge.py` | Query and retrieve entries | `python scripts/utilities/query_knowledge.py --help` |
| `schema.yaml` | Reference schema definition | `knowledge/schema.yaml` |

---

## Files Modified When Adding Knowledge

| File | Always | If Outcome-Related |
|------|--------|-------------------|
| `knowledge/{domain}/{file}.yaml` | Yes | Yes |
| `knowledge/indexes/domain_index.yaml` | Yes | Yes |
| `knowledge/indexes/outcome_index.yaml` | No | Yes |
| `knowledge/outcome_registry.yaml` | No | Yes (if new/major outcome) |

---

## Troubleshooting

### "File not found" errors
- Check file path matches exactly in domain_index.yaml
- Paths are relative to `knowledge/` directory

### Entries not appearing in queries
- Verify file is registered in domain_index.yaml with `status: "active"`
- Check entry_id format matches query pattern
- Run validation to find syntax errors

### YAML parse errors
- Quote strings containing special characters: `brainwave: "delta (note)"`
- Avoid tabs, use spaces only
- Check for unescaped colons in values

### Cross-reference warnings
- Referenced entry_id must exist in knowledge base
- Check spelling and format: `domain.category.name`
