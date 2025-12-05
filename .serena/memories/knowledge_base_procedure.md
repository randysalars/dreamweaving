# Knowledge Base Addition Procedure

## Quick Checklist
When adding new knowledge content:

1. **Create/Update YAML file** in `knowledge/{domain}/`
2. **Register in domain_index.yaml** at `knowledge/indexes/domain_index.yaml`
3. **If outcome-related**: Update `knowledge/indexes/outcome_index.yaml`
4. **If outcome-related**: Update `knowledge/outcome_registry.yaml`
5. **Validate**: `python scripts/utilities/validate_knowledge.py`
6. **Test**: `python scripts/utilities/query_knowledge.py`

## Key Files to Update

### Always Update
- `knowledge/{domain}/{filename}.yaml` - The actual content
- `knowledge/indexes/domain_index.yaml` - Register file, update statistics

### If Outcome-Related
- `knowledge/indexes/outcome_index.yaml` - Add to outcomes section + reverse indexes
- `knowledge/outcome_registry.yaml` - Full outcome definition + all reference indexes

## Domain Index Updates
```yaml
# In domain_index.yaml
your_domain:
  status: "active"
  files:
    your_file:
      path: "domain/filename.yaml"
      entries: [entry1, entry2, entry3]
      status: "active"

# Update statistics at bottom
statistics:
  total_files: X      # Increment
  files_active: Y     # Increment if active
```

## Outcome Index Updates
```yaml
# Add outcome definition
outcomes:
  your_outcome:
    description: "..."
    primary_domains: [...]
    secondary_domains: [...]
    key_entries: [...]
    element_emphasis: earth
    chakra_emphasis: root
    brainwave_target: alpha

# Update reverse indexes
element_outcomes:
  earth:
    primary: [..., your_outcome]

chakra_outcomes:
  root:
    outcomes: [..., your_outcome]

brainwave_outcomes:
  alpha:
    outcomes: [..., your_outcome]
```

## Outcome Registry Updates
For new/major outcomes, add full definition including:
- required_patterns
- suggested_patterns
- advanced_patterns
- suggested_archetypes (primary/secondary)
- suggested_journey_families
- suggested_objects
- integration_actions
- success_metrics
- brainwave_arc

Then update ALL reference indexes at bottom:
- pattern_outcome_index
- archetype_outcome_index
- object_outcome_index
- family_outcome_index

## Validation Commands
```bash
# Full validation
python scripts/utilities/validate_knowledge.py

# Single file
python scripts/utilities/validate_knowledge.py --file domain/file.yaml

# Query test
python scripts/utilities/query_knowledge.py --outcome your_outcome --json
python scripts/utilities/query_knowledge.py --domain your_domain
```

## Entry Schema (Required Fields)
```yaml
entry_id: "domain.category.name"
name: "Human Readable Name"
domain: "domain_name"

definition:
  brief: "One sentence (max 150 chars)"

applications:
  journey_phases: [induction, journey, integration]
  outcome_alignment: [healing, transformation]
```

## Full Documentation
See: docs/KNOWLEDGE_BASE_SOP.md
