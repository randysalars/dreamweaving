---
name: validate
description: Validate SSML and manifest for a session
arguments:
  - name: session
    required: true
    description: Session name or path
agent: quality-control
---

# /validate Command

Run comprehensive validation on session SSML and manifest.

## Usage
```
/validate <session>
```

## Example
```
/validate inner-child-healing
```

## Process

1. **Validate SSML**
   ```bash
   python3 scripts/utilities/validate_ssml.py sessions/{session}/working_files/script.ssml
   ```
   - Check XML syntax
   - Verify structure
   - Validate tags

2. **Validate Manifest**
   ```bash
   python3 scripts/utilities/validate_manifest.py sessions/{session}/manifest.yaml
   ```
   - Schema compliance
   - Required fields
   - Timing consistency

3. **Cross-validation**
   - Duration consistency
   - Section alignment
   - Resource availability

4. **Generate report**
   - List all issues found
   - Provide fix suggestions
   - Severity levels (critical, warning, info)

## Validation Checks

### SSML
- [ ] XML syntax valid
- [ ] `<speak>` root element
- [ ] All tags closed
- [ ] Break durations reasonable (< 10s)
- [ ] Prosody values valid
- [ ] All 5 sections present

### Manifest
- [ ] Schema validation passes
- [ ] Required fields present
- [ ] Voice ID valid
- [ ] Section timings contiguous
- [ ] Duration reasonable (5-60 min)
- [ ] Binaural frequencies in range

### Cross-validation
- [ ] Script exists if manifest references it
- [ ] Duration estimates match
- [ ] Voice settings consistent

## Report Format

```
=== Validation Report: {session} ===

SSML Validation:
  ✓ XML syntax valid
  ✓ Structure correct
  ✗ Missing section: integration
    → Add <!-- SECTION: Integration --> comment

Manifest Validation:
  ✓ Schema valid
  ✓ Required fields present
  ⚠ Warning: Duration 45min above typical

Cross-validation:
  ✓ Files consistent
  ✓ Timings aligned

Summary: 1 error, 1 warning
```

## Auto-fix Options

Some issues can be auto-fixed:
- Unclosed XML tags
- Missing section comments
- Invalid break durations

Run with `--fix` to auto-repair:
```bash
python3 scripts/utilities/validate_ssml.py --fix script.ssml
```
