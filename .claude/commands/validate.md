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

3. **Outcome Validation**
   ```bash
   python3 scripts/utilities/validate_outcome.py sessions/{session}/
   ```
   - Pattern distribution for desired outcome
   - Archetype coherence
   - Target transformation alignment

4. **Christ-Centered Validation** (NEW)
   ```bash
   python3 scripts/utilities/validate_christ_centered.py sessions/{session}/
   ```
   - Forbidden pattern detection (HARD FAIL)
   - Required element verification
   - Will/agency balance check
   - Archetype framing validation

5. **Cross-validation**
   - Duration consistency
   - Section alignment
   - Resource availability

6. **Generate report**
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

### Christ-Centered (NEW)
- [ ] No spirit invocation language
- [ ] No entity communication patterns
- [ ] No passive will / empty mind language
- [ ] No archetypes as literal beings
- [ ] No false authority (non-Christ sources)
- [ ] Safety clause in first 500 words
- [ ] Will engagement (3+ occurrences)
- [ ] Christ anchor (2+ for Christian sessions)
- [ ] Archetypes framed as metaphors
- [ ] Discernment affirmation in closing

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

✝️ Christ-Centered Validation:
  ✓ No forbidden patterns detected
  ✓ Safety clause present
  ✓ Will engagement: 5 occurrences
  ⚠ Warning: Archetype used without metaphor framing
    → Add "as a psychological metaphor" or "representing an aspect of you"
  ⚠ Warning: Missing discernment affirmation
    → Add "your discernment is strengthened" in closing

Cross-validation:
  ✓ Files consistent
  ✓ Timings aligned

Summary: 1 error, 3 warnings
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
