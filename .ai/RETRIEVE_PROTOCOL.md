# Retrieve-First Protocol

> **Purpose:** Standard workflow for AI assistants before starting any troubleshooting task.

---

## The Rule

**Before proposing ANY fix, ALWAYS search for existing solutions first.**

This prevents:
- Repeating past mistakes
- Reinventing solutions that exist
- Missing important context
- Wasting time on known issues

---

## Protocol Steps

### Step 1: Search Memory

Search the incident memory for related issues:

```bash
rg -n "keyword1|keyword2" .ai/memory/
```

Use keywords from `.ai/TRIGGER_MAPS.md` based on symptoms.

**Example:**
```bash
# For silent audio issue
rg -n "silent|volume|mix|stems" .ai/memory/
```

---

### Step 2: Check Error Catalog

Route the error to get structured guidance:

```bash
python3 scripts/ai/error_router.py "describe the symptom here"
```

**Example:**
```bash
python3 scripts/ai/error_router.py "audio output is silent"
```

This provides:
- Matched error ID
- Diagnostic checks to run
- Root causes to consider
- Fix pattern to follow
- Related Serena memories

---

### Step 3: Read Serena Memories (if applicable)

If the error router or trigger maps suggest a Serena memory, read it:

| Issue Type | Memory to Read |
|------------|----------------|
| Audio mixing/mastering | `audio_production_methodology` |
| SSML/script writing | `script_production_workflow` |
| Voice prosody/pacing | `voice_pacing_guidelines` |
| Production stages | `production_workflow_stages` |
| Website deployment | `website_upload_deployment` |
| Project overview | `dreamweaving_project_overview` |
| Learning system | `session_learnings_system` |
| DVE modules | `dve_module_system` |

---

### Step 4: Run Doctor (if system-wide)

For environment or system-wide issues:

```bash
python3 scripts/utilities/doctor.py
```

Or quick version:
```bash
python3 scripts/utilities/doctor.py --quick
```

---

### Step 5: Check DEBUGGING.md

If issue matches one of the top 10 common failures:

See `.ai/DEBUGGING.md` for decision-tree playbooks.

---

### Step 6: Proceed with Fix

Only now proceed with the fix using:
- Patterns found in memory
- Guidance from error catalog
- Information from Serena memories
- Playbook from DEBUGGING.md

---

## Quick Reference Commands

```bash
# Full retrieval workflow
rg -n "KEYWORD" .ai/memory/                    # 1. Search memory
python3 scripts/ai/error_router.py "SYMPTOM"   # 2. Route error
# 3. Read Serena memory (via Serena tools)
python3 scripts/utilities/doctor.py --quick    # 4. System check
# 5. Check .ai/DEBUGGING.md
```

---

## After Fixing

If the fix took significant effort:

1. **Create memory card:**
   ```bash
   cp .ai/memory/TEMPLATE.md .ai/memory/$(date +%Y-%m-%d)__short-title.md
   # Edit the new file with fix details
   ```

2. **Update INDEX.md:**
   Add entry to `.ai/memory/INDEX.md`

3. **Consider updates to:**
   - `.claude/error_catalog.yaml` (if new error type)
   - `.ai/DEBUGGING.md` (if common issue)
   - `.ai/TRIGGER_MAPS.md` (if new keywords helpful)

---

## For Claude & Codex Assistants

When user reports a problem:

1. **DO NOT** immediately propose a solution
2. **DO** follow this protocol first
3. **DO** mention what you searched and found (or didn't find)
4. **DO** cite sources: "According to memory card X..." or "Error catalog suggests..."

**Example response pattern:**
```
I searched memory for "silent audio" and found no previous incidents.
The error router matched `audio.silent_output` with 95% confidence.
Serena memory `audio_production_methodology` recommends checking stem levels.

Based on this, the most likely cause is...
```

---

## Protocol Exceptions

Skip retrieval only when:
- User explicitly says "don't search, just do X"
- Issue is trivially obvious (typo, missing file)
- You've already done retrieval in current conversation

Even then, note that you skipped retrieval.
