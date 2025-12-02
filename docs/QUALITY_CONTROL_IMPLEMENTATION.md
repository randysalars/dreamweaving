# Quality Control Implementation Guide

## Overview

This document describes the complete Quality Control (QC) framework for ensuring all hypnotic sessions are produced with consistent standards. The system uses multiple complementary verification layers to make it virtually impossible to omit any mandatory element.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    QUALITY CONTROL FRAMEWORK                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   LAYER 1    │    │   LAYER 2    │    │   LAYER 3    │       │
│  │   Standards  │───▶│  Validation  │───▶│  Cross-Check │       │
│  │   Document   │    │    Tools     │    │   Reports    │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│         │                   │                   │                │
│         ▼                   ▼                   ▼                │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │  Production  │    │   Automated  │    │  Consistency │       │
│  │  Checklist   │    │  Pre-Build   │    │   Analysis   │       │
│  │   (Manual)   │    │   Checks     │    │   (Library)  │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Layer 1: Standards Documentation

### Purpose
Defines the authoritative specification for all mandatory elements.

### Files
- **[HYPNOTIC_SESSION_STANDARDS.md](HYPNOTIC_SESSION_STANDARDS.md)** - Complete standards reference
- **[templates/SESSION_PRODUCTION_CHECKLIST.md](../templates/SESSION_PRODUCTION_CHECKLIST.md)** - Per-session checklist

### Usage
1. Read standards document before starting any session
2. Print checklist for each new session
3. Complete every checkbox before delivery

### Enforcement
- Standards document is the single source of truth
- Any deviation requires documented justification
- Version controlled for audit trail

---

## Layer 2: Automated Validation Tools

### Purpose
Programmatically verify all mandatory elements are present.

### Tools

#### 1. `validate_hypnotic_standards.py`
Primary validation script that checks:
- All 5 section markers present
- Pre-talk elements (introduction, safety, consent)
- Induction elements (relaxation, breathing, countdown)
- Journey elements (all 5 senses, archetypes)
- Integration elements (ascending count, grounding)
- Closing elements (anchors, thank you, blessing)
- Manifest configuration
- Voice enhancement settings
- Audio output files

**Usage:**
```bash
# Single session
python3 scripts/utilities/validate_hypnotic_standards.py sessions/my-session

# All sessions
python3 scripts/utilities/validate_hypnotic_standards.py --all

# With cross-session comparison
python3 scripts/utilities/validate_hypnotic_standards.py --all --compare
```

#### 2. `validate_ssml.py`
SSML syntax validation:
- XML well-formedness
- Valid SSML tags
- Break duration limits

```bash
python3 scripts/utilities/validate_ssml.py sessions/my-session/working_files/script.ssml
```

#### 3. `validate_manifest.py`
Manifest schema validation:
- Required fields present
- Values within valid ranges
- Schema compliance

```bash
python3 scripts/utilities/validate_manifest.py sessions/my-session/manifest.yaml
```

#### 4. `validate_session_structure.py`
Directory structure validation:
- Required folders exist
- Required files present
- No misplaced files

```bash
python3 scripts/utilities/validate_session_structure.py sessions/my-session
```

### Integration Points

#### Pre-Build Hook
Add to `.claude/hooks/pre-build.sh`:
```bash
#!/bin/bash
# Validate before building

SESSION=$1

echo "Running pre-build validation..."

python3 scripts/utilities/validate_hypnotic_standards.py "sessions/$SESSION"
RESULT=$?

if [ $RESULT -ne 0 ]; then
    echo "❌ Validation failed! Fix issues before building."
    exit 1
fi

echo "✓ Validation passed"
```

#### Git Pre-Commit Hook
Add to `.githooks/pre-commit`:
```bash
#!/bin/bash
# Validate all changed sessions before commit

CHANGED_SESSIONS=$(git diff --cached --name-only | grep "^sessions/" | cut -d'/' -f2 | sort -u)

for session in $CHANGED_SESSIONS; do
    if [ -d "sessions/$session" ]; then
        python3 scripts/utilities/validate_hypnotic_standards.py "sessions/$session"
        if [ $? -ne 0 ]; then
            echo "❌ Session $session failed validation"
            exit 1
        fi
    fi
done
```

---

## Layer 3: Cross-Session Verification

### Purpose
Ensure consistency across the entire session library, not just individual sessions.

### Tools

#### `session_consistency_report.py`
Generates comprehensive comparison report:
- Metrics analysis (word count, anchors, sense coverage)
- Common issues across sessions
- Outlier detection
- Enhancement coverage tracking
- Recommendations for fixes

**Usage:**
```bash
# Generate Markdown report
python3 scripts/utilities/session_consistency_report.py

# Generate HTML report
python3 scripts/utilities/session_consistency_report.py --format html --output report.html

# Generate JSON for automation
python3 scripts/utilities/session_consistency_report.py --format json --output report.json
```

### Metrics Tracked

| Metric | Target | Acceptable Range |
|--------|--------|------------------|
| Word Count | 3,750 | 3,200 - 4,200 |
| Anchor Count | 5 | 3 - 7 |
| Sense Coverage | 5/5 | 4/5 minimum |
| Section Count | 5 | 5 exactly |
| Enhancement Coverage | 100% | 100% required |

### Consistency Checks

1. **Word Count Variance** - Flag sessions >30% from mean
2. **Enhancement Gaps** - Identify missing enhancements
3. **Voice Consistency** - Ensure same voice across sessions
4. **Audio Levels** - Verify mastering targets match

---

## Implementation Workflow

### For New Sessions

```
1. CREATE SESSION
   ├── Run create_new_session.sh
   └── Verify directory structure created

2. CONFIGURE MANIFEST
   ├── Fill all required fields
   ├── Set voice_enhancement.enabled = true
   ├── Configure all 8 enhancement layers
   └── Run validate_manifest.py

3. WRITE SCRIPT
   ├── Include all 5 section markers
   ├── Complete all mandatory elements
   ├── Follow SSML standards (rate="1.0")
   └── Run validate_ssml.py

4. VALIDATE STANDARDS
   ├── Run validate_hypnotic_standards.py
   ├── Fix any errors
   └── Repeat until VALID

5. GENERATE AUDIO
   ├── Run generate_voice.py
   ├── Verify voice_enhanced.mp3 created
   └── Apply all enhancement layers

6. FINAL CHECK
   ├── Complete production checklist
   ├── Run validate_hypnotic_standards.py
   ├── Run session_consistency_report.py
   └── Compare against existing sessions

7. SIGN-OFF
   ├── All checkboxes completed
   ├── All validations passed
   └── Ready for publication
```

### For Existing Sessions (Remediation)

```bash
# 1. Identify non-compliant sessions
python3 scripts/utilities/session_consistency_report.py --format json > audit.json

# 2. Fix each session
for session in $(jq -r '.sessions[] | select(.compliant==false) | .name' audit.json); do
    echo "Fixing: $session"
    # Update manifest
    # Regenerate audio with enhancements
    # Validate
    python3 scripts/utilities/validate_hypnotic_standards.py "sessions/$session"
done

# 3. Verify consistency
python3 scripts/utilities/session_consistency_report.py
```

---

## Quality Gates

### Gate 1: Manifest Validation
**When:** Before script writing
**Tool:** `validate_manifest.py`
**Blocks:** Script generation if manifest incomplete

### Gate 2: Script Validation
**When:** After script completion
**Tool:** `validate_ssml.py` + `validate_hypnotic_standards.py`
**Blocks:** Voice generation if script invalid

### Gate 3: Audio Validation
**When:** After audio generation
**Tool:** `validate_hypnotic_standards.py`
**Blocks:** Publication if audio missing enhancements

### Gate 4: Consistency Validation
**When:** Before publication
**Tool:** `session_consistency_report.py`
**Blocks:** Publication if inconsistent with library

---

## Deviation Protocol

If a session MUST deviate from standards:

1. **Document the deviation** in `notes.md`:
   ```markdown
   ## Standard Deviation Notice

   **Date:** YYYY-MM-DD
   **Element:** [Which standard is being deviated from]
   **Reason:** [Why deviation is necessary]
   **Approval:** [Who approved the deviation]
   **Impact:** [How this affects the session]
   ```

2. **Add to manifest:**
   ```yaml
   metadata:
     standard_deviations:
       - element: "voice_enhancement.echo"
         reason: "Session uses natural reverb from outdoor recording"
         approved_by: "Producer Name"
   ```

3. **Update validation whitelist** if recurring:
   - Add to `ALLOWED_DEVIATIONS` in validation script

---

## Monitoring & Reporting

### Weekly Consistency Check
```bash
# Add to crontab or run weekly
python3 scripts/utilities/session_consistency_report.py \
    --format html \
    --output reports/consistency_$(date +%Y%m%d).html
```

### Metrics Dashboard
The HTML report provides visual dashboard of:
- Compliance rate trend
- Enhancement coverage
- Common issues
- Outlier detection

### Alerts
Set up notifications for:
- Compliance rate drops below 90%
- New session fails validation
- Enhancement coverage incomplete

---

## Training Materials

### For New Producers

1. Read `docs/HYPNOTIC_SESSION_STANDARDS.md` completely
2. Study 2-3 compliant sessions as examples
3. Create test session using `SESSION_PRODUCTION_CHECKLIST.md`
4. Run all validation tools
5. Submit for review

### Validation Cheat Sheet

```bash
# Quick validation commands

# Validate single session (full)
python3 scripts/utilities/validate_hypnotic_standards.py sessions/NAME

# Validate SSML syntax only
python3 scripts/utilities/validate_ssml.py sessions/NAME/working_files/script.ssml

# Validate manifest only
python3 scripts/utilities/validate_manifest.py sessions/NAME/manifest.yaml

# Check all sessions
python3 scripts/utilities/validate_hypnotic_standards.py --all

# Generate consistency report
python3 scripts/utilities/session_consistency_report.py

# Full pre-publication check
python3 scripts/utilities/validate_hypnotic_standards.py sessions/NAME && \
python3 scripts/utilities/session_consistency_report.py | grep NAME
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-02 | Initial implementation |

---

## Contact

For questions about quality standards:
- Review `docs/HYPNOTIC_SESSION_STANDARDS.md`
- Check `knowledge/lessons_learned.yaml`
- Consult production team
