# Workflow Validation System

**VERSION:** 1.0
**LAST UPDATED:** 2025-11-28
**PURPOSE:** Automated validation and version control for workflow documentation

---

## Overview

The Workflow Validation System ensures that workflow documentation remains consistent, accurate, and up-to-date through automated checks and version control.

**Key Components:**
1. **Validation Script** - Automated checks for workflow consistency
2. **Version Control** - Track workflow versions across the project
3. **Git Hooks** - Prevent invalid workflow docs from being committed
4. **Update Tools** - Helper scripts to maintain workflows

---

## Quick Start

### Install Git Hooks (Recommended)

```bash
./scripts/utilities/setup_git_hooks.sh
```

This installs a pre-commit hook that automatically validates workflow documentation before commits.

### Run Validation Manually

```bash
python3 scripts/utilities/validate_workflows.py
```

### Update a Workflow Version

```bash
python3 scripts/utilities/update_workflow_version.py canonical_workflow 1.1 --reason "Added new feature"
```

---

## Validation Checks

The validation system performs these checks:

### 1. Canonical Workflow Exists ✅
- Ensures `docs/CANONICAL_WORKFLOW.md` exists
- Verifies it has VERSION and LAST UPDATED headers
- Confirms it's the authoritative source

### 2. Script References Valid ✅
- Checks that all scripts mentioned in docs actually exist
- Validates paths are correct
- Prevents broken references

**Example:**
```markdown
❌ References missing: scripts/core/nonexistent.py
✅ All referenced scripts exist
```

### 3. Version Headers Present ✅
- All session-specific docs must have:
  - `**VERSION:**`
  - `**LAST UPDATED:**`
  - `**STATUS:**`
- Helps track document currency

**Example:**
```markdown
sessions/neural-network-navigator/PRODUCTION_WORKFLOW.md: missing LAST UPDATED
```

### 4. Deprecated Warnings ✅
- Deprecated docs must have warnings
- Must reference CANONICAL_WORKFLOW.md
- Clear deprecation notices required

### 5. No Duplicate Workflows ✅
- Checks for duplicate scripts in root vs. sessions
- Ensures single source of truth
- Flags potential conflicts

### 6. File Naming Conventions ✅
- Validates naming follows TERMINOLOGY_GUIDE.md
- Checks for correct use of MASTERED (uppercase)
- Ensures consistency

### 7. Duration Consistency ✅
- Validates duration math (XX:XX = XXXX seconds)
- Checks for conflicting durations in same session
- Prevents specification errors

**Example:**
```markdown
❌ Duration mismatch - 28:30 is 1710s not 1700s
✅ Duration specifications consistent
```

### 8. Command Format Standards ✅
- Ensures commands use `python3` not `python`
- Checks for missing voice parameters
- Validates command examples

---

## Version Control System

### Version Registry

**File:** `.workflow-versions`

Tracks all workflow versions across the project:

```
# Format: workflow_name=version:last_updated:status

canonical_workflow=1.0:2025-11-28:CURRENT
neural_network_navigator_manual_v2=2.0:2025-11-28:CURRENT
audio_video_workflow=1.0:2025-11-28:DEPRECATED
```

**Status Codes:**
- `CURRENT` - Active and maintained
- `DEPRECATED` - Do not use, see canonical
- `FUTURE` - Planning/vision document

### Workflow IDs

Available workflow identifiers:

**Universal Workflows:**
- `canonical_workflow` → docs/CANONICAL_WORKFLOW.md
- `quick_start` → docs/QUICK_START.md
- `workflow_decision_tree` → docs/WORKFLOW_DECISION_TREE.md
- `terminology_guide` → docs/TERMINOLOGY_GUIDE.md
- `workflow_maintenance_guide` → docs/WORKFLOW_MAINTENANCE_GUIDE.md

**Session-Specific Workflows:**
- `neural_network_navigator_workflow` → sessions/neural-network-navigator/PRODUCTION_WORKFLOW.md
- `neural_network_navigator_manual_v1` → sessions/neural-network-navigator/PRODUCTION_MANUAL.md
- `neural_network_navigator_manual_v2` → sessions/neural-network-navigator/PRODUCTION_MANUAL_V2.md
- `garden_of_eden_manual` → sessions/garden-of-eden/PRODUCTION_MANUAL.md
- `garden_of_eden_audio_readme` → sessions/garden-of-eden/AUDIO_PRODUCTION_README.md

### Updating Workflow Versions

**Automatic Update (Recommended):**

```bash
python3 scripts/utilities/update_workflow_version.py \
    canonical_workflow 1.1 \
    --reason "Added support for new voice provider"
```

This automatically:
1. Updates VERSION in the workflow file
2. Updates LAST UPDATED timestamp
3. Adds entry to version history (if section exists)
4. Updates `.workflow-versions` registry

**Manual Update (Not Recommended):**

If you must update manually:
1. Update `**VERSION:**` line in workflow file
2. Update `**LAST UPDATED:**` line
3. Add version history entry if applicable
4. Update `.workflow-versions` file
5. Run validation: `python3 scripts/utilities/validate_workflows.py`

---

## Git Hooks Integration

### Pre-Commit Hook

Installed via `./scripts/utilities/setup_git_hooks.sh`

**What it does:**
1. Detects when workflow docs are modified
2. Runs validation checks automatically
3. Prevents commit if validation fails
4. Shows which checks failed

**Example Output:**

```
🔍 Running workflow validation checks...
📝 Modified workflow files:
  - docs/CANONICAL_WORKFLOW.md
  - sessions/neural-network-navigator/PRODUCTION_WORKFLOW.md

[1/8] Checking canonical workflow...
  ✓ Canonical workflow exists
[2/8] Checking script references...
  ✗ docs/CANONICAL_WORKFLOW.md references missing script: scripts/core/test.py

❌ Workflow validation failed!

Please fix the issues above before committing.
Or use 'git commit --no-verify' to bypass (not recommended).
```

### Bypassing Validation (Emergency Only)

```bash
git commit --no-verify -m "Emergency commit"
```

**⚠️ Warning:** Only use `--no-verify` in emergencies. Fix validation issues properly.

---

## Validation Output Examples

### All Checks Pass ✅

```
=== Workflow Documentation Validator ===

[1/8] Checking canonical workflow...
  ✓ Canonical workflow exists
[2/8] Checking script references...
  ✓ All referenced scripts exist
[3/8] Checking version headers...
  ✓ All session docs have version headers
[4/8] Checking deprecated doc warnings...
  ✓ All deprecated docs have warnings
[5/8] Checking for duplicate workflows...
  ✓ No duplicate scripts found
[6/8] Checking file naming conventions...
  ✓ File naming conventions followed
[7/8] Checking duration consistency...
  ✓ Duration specifications consistent
[8/8] Checking command formats...
  ✓ Command formats follow standards

=== Validation Results ===

✓ All validation checks passed!
```

### Issues Found ⚠️

```
=== Validation Results ===

Warnings (3):
  ⚠  sessions/new-session/README.md: missing VERSION, LAST UPDATED
  ⚠  CANONICAL_WORKFLOW.md: Uses 'python' instead of 'python3' in bash blocks
  ⚠  neural-network-navigator: Multiple different durations specified: [1421, 1680, 1722]

Errors (1):
  ✗ docs/CANONICAL_WORKFLOW.md references missing script: scripts/core/nonexistent.py

Total issues: 4 (1 errors, 3 warnings)

Please fix errors before committing workflow changes.
```

---

## Common Workflows

### Adding a New Session Workflow

1. **Create the workflow document:**
   ```bash
   # Create in sessions/my-session/PRODUCTION_WORKFLOW.md
   ```

2. **Add version header:**
   ```markdown
   # My Session: Production Workflow

   **VERSION:** 1.0 (Session-Specific)
   **LAST UPDATED:** 2025-11-28
   **SESSION DURATION:** XX minutes (XXXX seconds)
   **STATUS:** ✅ Current and Valid

   > **📖 For universal workflow:** See [../../docs/CANONICAL_WORKFLOW.md](...)
   ```

3. **Register in version control:**
   ```bash
   # Edit .workflow-versions
   my_session_workflow=1.0:2025-11-28:CURRENT
   ```

4. **Add to update script:**
   ```python
   # Edit scripts/utilities/update_workflow_version.py
   WORKFLOW_FILES = {
       ...
       "my_session_workflow": "sessions/my-session/PRODUCTION_WORKFLOW.md",
   }
   ```

5. **Validate:**
   ```bash
   python3 scripts/utilities/validate_workflows.py
   ```

### Updating Canonical Workflow

1. **Make your changes** to `docs/CANONICAL_WORKFLOW.md`

2. **Update version:**
   ```bash
   python3 scripts/utilities/update_workflow_version.py \
       canonical_workflow 1.1 \
       --reason "Added support for Edge TTS as alternative"
   ```

3. **Validate:**
   ```bash
   python3 scripts/utilities/validate_workflows.py
   ```

4. **Commit:**
   ```bash
   git add docs/CANONICAL_WORKFLOW.md .workflow-versions
   git commit -m "Update canonical workflow to v1.1"
   # Pre-commit hook runs automatically
   ```

### Deprecating a Workflow

1. **Add deprecation notice** to the document
2. **Update status in registry:**
   ```bash
   # Edit .workflow-versions
   old_workflow=1.0:2025-11-28:DEPRECATED
   ```

3. **Ensure it references canonical workflow**
4. **Validate:**
   ```bash
   python3 scripts/utilities/validate_workflows.py
   ```

---

## Troubleshooting

### Validation Fails in Pre-Commit Hook

**Problem:** Git commit is blocked by validation errors

**Solutions:**

1. **See what's wrong:**
   ```bash
   python3 scripts/utilities/validate_workflows.py
   ```

2. **Fix the issues** shown in output

3. **Try commit again:**
   ```bash
   git commit
   ```

4. **Emergency bypass (not recommended):**
   ```bash
   git commit --no-verify
   ```

### False Positive Validation Errors

**Problem:** Validator reports error but you believe it's incorrect

**Solutions:**

1. **Review validation logic:**
   - Check `scripts/utilities/validate_workflows.py`
   - Look for the specific check that's failing

2. **File an issue** if validator is wrong

3. **Temporary bypass:**
   ```bash
   git commit --no-verify
   ```

### Version Update Script Fails

**Problem:** `update_workflow_version.py` doesn't work

**Check:**

1. **Workflow ID is valid:**
   ```bash
   python3 scripts/utilities/update_workflow_version.py
   # Shows list of valid IDs
   ```

2. **File exists:**
   ```bash
   ls -la sessions/my-session/PRODUCTION_WORKFLOW.md
   ```

3. **Has version header:**
   ```bash
   grep "**VERSION:**" sessions/my-session/PRODUCTION_WORKFLOW.md
   ```

---

## Integration with CI/CD (Future)

### Planned Automation

**GitHub Actions Workflow:**
```yaml
name: Validate Workflows
on: [pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
      - name: Validate Workflows
        run: python3 scripts/utilities/validate_workflows.py
```

**Benefits:**
- Automatic validation on PRs
- Prevent merging invalid workflows
- Continuous integration

---

## Related Documentation

- [CANONICAL_WORKFLOW.md](CANONICAL_WORKFLOW.md) - Official workflow
- [WORKFLOW_MAINTENANCE_GUIDE.md](WORKFLOW_MAINTENANCE_GUIDE.md) - How to maintain workflows
- [TERMINOLOGY_GUIDE.md](TERMINOLOGY_GUIDE.md) - Standard terminology

---

## File Reference

**Validation System Files:**
- `.workflow-versions` - Version registry
- `.githooks/pre-commit` - Pre-commit validation hook
- `scripts/utilities/validate_workflows.py` - Main validator
- `scripts/utilities/update_workflow_version.py` - Version updater
- `scripts/utilities/setup_git_hooks.sh` - Hook installer
- `docs/WORKFLOW_VALIDATION.md` - This document

---

**Last Updated:** 2025-11-28
**Version:** 1.0
**Next Review:** 2026-11-28

---

*Automated validation ensures workflow consistency and prevents documentation drift.*
