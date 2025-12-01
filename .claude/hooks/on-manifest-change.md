---
name: on-manifest-change
trigger: file_save
pattern: "sessions/**/manifest.yaml"
description: Auto-validate manifest files on save
action: validate_manifest
---

# Manifest Validation Hook

## Trigger
Activated when any `manifest.yaml` in `sessions/` is saved.

## Action
Run schema validation and consistency checks.

## Implementation

When a manifest file is saved:

1. **Run validation**
   ```bash
   python3 scripts/utilities/validate_manifest.py {file_path}
   ```

2. **Check schema**
   - Validate against `config/manifest.schema.json`
   - Check required fields
   - Verify data types

3. **Check consistency**
   - Section timings are contiguous
   - Duration is reasonable
   - Voice ID is valid

4. **Report results**
   - Show validation status
   - List any issues
   - Suggest fixes

## Validation Checks

### Schema Validation
- Required fields present
- Data types correct
- Enum values valid

### Consistency Checks
- Sections don't overlap
- Sections cover full duration
- Voice exists in voice_config.yaml
- Binaural frequencies in valid range

### Best Practice Checks
- Duration between 5-60 minutes
- Speaking rate between 0.75-1.25
- Target LUFS is -14 (YouTube standard)

## Example Output

### Success
```
✓ Manifest validation passed: manifest.yaml
  - Schema: valid
  - Sections: 5 sections, contiguous timing
  - Voice: en-US-Neural2-A (valid)
  - Duration: 30 minutes
```

### Failure
```
✗ Manifest validation failed: manifest.yaml

Errors:
  - Missing required field: session.topic
  - Section timing gap: 08:00 to 09:00 undefined

Warnings:
  - Duration 75 minutes exceeds typical (recommend 25-45)
  - Speaking rate 0.65 below typical (recommend 0.75-1.0)

Suggestions:
  - Add topic field to session section
  - Add section covering 08:00-09:00
```

## Schema Reference

Key required fields:
- `session.name`
- `session.topic`
- `session.duration_minutes`
- `voice.provider`
- `voice.voice`
- `sections[]` with start/end times
