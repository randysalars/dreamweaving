# Code Review Rubric

> **Purpose:** Non-negotiable invariants that must be checked on every code change.

---

## Pre-Change Checklist

Before modifying any code:

- [ ] Read the file(s) being changed
- [ ] Search `.ai/memory/` for related incidents
- [ ] Check Serena memories if touching core systems
- [ ] Understand the current behavior before changing

---

## SSML Changes

| Check | Requirement | How to Verify |
|-------|-------------|---------------|
| Rate | `rate="1.0"` always | `grep 'rate="0\.'` returns nothing |
| Breaks | Duration < 10s | Validation script passes |
| Tags closed | All tags properly closed | XML parser accepts |
| SFX markers | On own lines, not inline | Visual inspection |
| Clean script | No markers in voice script | `grep '[SFX:' voice_clean.ssml` empty |

**Validation Command:**
```bash
python3 scripts/utilities/validate_ssml.py sessions/{session}/working_files/script.ssml
```

---

## Audio Changes

| Check | Requirement | How to Verify |
|-------|-------------|---------------|
| Voice file | Use `voice_enhanced.mp3` | Never reference raw `voice.mp3` |
| Voice level | -6 dB | Check mixer command |
| Binaural level | -6 dB | Check mixer command |
| SFX level | 0 dB | Check mixer command |
| Normalize | `normalize=0` in amix | Check filter_complex |
| Post-process | MANDATORY for all sessions | `*_MASTER.mp3` exists |

**Standard Mix Command:**
```bash
ffmpeg -y \
  -i voice_enhanced.wav -i binaural_dynamic.wav -i sfx_track.wav \
  -filter_complex "[0:a]volume=-6dB[v];[1:a]volume=-6dB[b];[2:a]volume=0dB[s];[v][b][s]amix=inputs=3:duration=longest:normalize=0" \
  -acodec pcm_s16le session_mixed.wav
```

---

## Manifest Changes

| Check | Requirement | How to Verify |
|-------|-------------|---------------|
| Schema valid | Passes JSON schema | Validation script |
| Duration | 5-60 minutes | Check `duration_minutes` |
| Required fields | name, title, duration | Validation script |
| Outcome | From `outcome_registry.yaml` | Cross-reference |

**Validation Command:**
```bash
python3 scripts/utilities/validate_manifest.py sessions/{session}/manifest.yaml
```

---

## Python Script Changes

| Check | Requirement | How to Verify |
|-------|-------------|---------------|
| Logging | Use `get_logger()`, not `print()` | Code review |
| Error handling | Specific exceptions with context | Code review |
| Type hints | Functions have type annotations | Code review |
| Docstrings | Public functions documented | Code review |
| Imports | Grouped: stdlib, third-party, local | Code review |

---

## Session Changes

| Check | Requirement | How to Verify |
|-------|-------------|---------------|
| Structure | All required directories exist | `ls` or validation |
| Manifest | Valid and present | Validation script |
| Output files | In `output/`, not root | `ls` |
| Working files | In `working_files/` | `ls` |

---

## Security Checks

| Check | Requirement | How to Verify |
|-------|-------------|---------------|
| No secrets | No API keys in code | `grep -r "API_KEY\|SECRET"` |
| .env excluded | .env files not committed | `.gitignore` check |
| Credentials | Only env var names logged, not values | Code review |

---

## Before Committing

1. [ ] All validation scripts pass
2. [ ] No secrets in staged files
3. [ ] Changes are minimal (smallest diff that works)
4. [ ] Tests pass (if applicable)
5. [ ] CLAUDE.md updated if adding new patterns

---

## After Significant Fixes

If you fixed a non-trivial issue:

1. [ ] Create memory card in `.ai/memory/`
2. [ ] Update relevant Serena memory if systemic
3. [ ] Add to `.ai/DEBUGGING.md` if common issue
4. [ ] Add validation if preventable

---

## Severity Guide for Issues Found

| Severity | Definition | Action |
|----------|------------|--------|
| **Critical** | Breaks production, security issue | Fix immediately, don't merge |
| **High** | Major functionality broken | Must fix before merge |
| **Medium** | Noticeable issues, workarounds exist | Should fix, can merge with TODO |
| **Low** | Cosmetic, minor improvements | Optional fix |

---

## Quick Decision: Should This Be Reviewed?

```
Change touches...
├── SSML scripts → Validate SSML
├── Audio mixing → Check levels, verify output
├── Python scripts → Code review, run tests
├── Manifests → Validate schema
├── Knowledge base → Check cross-references
├── CLAUDE.md → Extra scrutiny (affects all agents)
└── Anything else → Standard review
```
