---
name: on-ssml-change
trigger: file_save
pattern: "sessions/**/*.ssml"
description: Auto-validate SSML files on save
action: validate_ssml
---

# SSML Validation Hook

## Trigger
Activated when any `.ssml` file in `sessions/` is saved.

## Action
Run SSML validation and report issues inline.

## Implementation

When an SSML file is saved:

1. **Run validation**
   ```bash
   python3 scripts/utilities/validate_ssml.py {file_path}
   ```

2. **Parse output**
   - Extract errors and warnings
   - Get line numbers if available

3. **Report results**
   - Show validation status
   - List any issues found
   - Suggest fixes

## Validation Checks

- XML syntax valid
- `<speak>` root element present
- All tags properly closed
- Break durations reasonable (< 10s)
- Prosody values valid
- Section comments present

## Example Output

### Success
```
✓ SSML validation passed: script.ssml
  - XML syntax: valid
  - Structure: 5 sections found
  - Breaks: 42 break tags (all valid)
```

### Failure
```
✗ SSML validation failed: script.ssml

Errors:
  Line 45: Unclosed <prosody> tag
  Line 78: Break duration "15s" exceeds maximum (10s)

Suggestions:
  - Add </prosody> after line 45
  - Reduce break duration to 10s or less
```

## Auto-fix Option

For common issues, offer auto-fix:
```bash
python3 scripts/utilities/validate_ssml.py --fix {file_path}
```

Fixes:
- Unclosed tags
- Invalid break durations (caps at 10s)
- Missing XML declaration
