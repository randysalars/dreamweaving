# Workflow Maintenance Guide

**Purpose:** Ensure workflow documentation stays consistent and authoritative

**Last Updated:** 2025-11-28

---

## Golden Rule

**THERE CAN BE ONLY ONE CANONICAL WORKFLOW.**

Any workflow changes must be made to [CANONICAL_WORKFLOW.md](CANONICAL_WORKFLOW.md) first, then propagated to other documentation.

---

## Workflow Update Protocol

### When Making Workflow Changes

1. **Update CANONICAL_WORKFLOW.md FIRST**
   - This is the single source of truth
   - All other docs reference this

2. **Update Core Documentation**
   - README.md (if quick start changes)
   - QUICK_START.md (if process changes)
   - INDEX.md (if major structure changes)

3. **Update Session-Specific Docs**
   - Only if they reference the changed workflow
   - Add notes about canonical workflow

4. **Test the Workflow**
   - Actually run the commands
   - Verify all steps work
   - Check all file paths exist

5. **Update Version History**
   - Add entry to CANONICAL_WORKFLOW.md version history
   - Update "Last Updated" date
   - Increment version number if major change

### When Creating New Session-Specific Workflows

1. **Start with Canonical Workflow**
   - Generate voice using canonical method
   - Apply any session-specific enhancements

2. **Document Session-Specific Parts ONLY**
   - Don't duplicate canonical workflow steps
   - Link to CANONICAL_WORKFLOW.md for base steps
   - Document only what's unique to this session

3. **Example Session Documentation Structure**

```markdown
# [Session Name] Production Workflow

## Quick Start

1. Follow [CANONICAL_WORKFLOW.md](../../docs/CANONICAL_WORKFLOW.md) to generate voice
2. Run session-specific ultimate mix: `./create_ultimate_audio.sh`
3. Create video: `./create_final_video.sh`

## Session-Specific Features

### Ultimate Audio Mix
[Describe unique audio layers, timings, effects]

### Video Production
[Describe unique scene counts, timings, transitions]

## Files
- Voice generation: Use canonical workflow
- Audio mixing: `create_ultimate_audio.sh` (this session)
- Video creation: `create_final_video.sh` (this session)
```

---

## Avoiding Workflow Conflicts

### ❌ DON'T

- Create duplicate workflow documentation
- Copy workflow steps from canonical to session docs
- Document two ways to do the same thing
- Create universal scripts for session-specific tasks
- Leave old documentation without deprecation notices

### ✅ DO

- Reference CANONICAL_WORKFLOW.md for standard steps
- Document only session-specific enhancements
- Keep scripts in session directories if session-specific
- Add clear deprecation notices to old docs
- Test workflows before documenting

---

## Documentation Hierarchy

```
CANONICAL_WORKFLOW.md (Level 0 - Universal Truth)
    ↓
README.md, INDEX.md, QUICK_START.md (Level 1 - Quick Reference)
    ↓
sessions/*/PRODUCTION_WORKFLOW.md (Level 2 - Session-Specific)
    ↓
sessions/*/README.md (Level 3 - Session Notes)
```

**Rule:** Lower levels reference higher levels, NEVER duplicate them.

---

## Workflow Version Control

### Semantic Versioning

**Format:** `MAJOR.MINOR.PATCH`

**MAJOR:** Breaking changes (e.g., switch TTS provider)
- Current: v1.0

**MINOR:** New features (e.g., add new voice options)
- Increment when adding capabilities

**PATCH:** Bug fixes, clarifications
- Increment for documentation improvements

### Version History Template

Add to CANONICAL_WORKFLOW.md:

```markdown
### Version X.Y (YYYY-MM-DD)
- ✅ Added: [feature description]
- 🔧 Changed: [change description]
- 🐛 Fixed: [fix description]
- ⚠️ Deprecated: [deprecated item]
```

---

## Deprecation Protocol

### When Deprecating Documentation

1. **Add Warning Banner**
```markdown
> **⚠️ THIS DOCUMENT IS DEPRECATED**
>
> **USE INSTEAD:** [docs/CANONICAL_WORKFLOW.md](CANONICAL_WORKFLOW.md)
>
> [Reason for deprecation]
>
> **Last Updated:** YYYY-MM-DD (Marked as deprecated)
```

2. **Update Title**
```markdown
# ⚠️ DEPRECATED: [Original Title]
```

3. **Keep Content**
- Don't delete the file
- Preserve for historical reference
- Eventually move to `.archive/deprecated_docs/`

4. **Update References**
- Find all links to deprecated doc
- Replace with canonical workflow link
- Add migration notes if needed

### When to Deprecate

- Multiple docs describe same workflow
- Workflow method changed fundamentally
- Documentation conflicts with canonical
- Better approach discovered

### When NOT to Deprecate

- Session-specific documentation (keep it)
- Historical notes and decisions (archive instead)
- Reference materials (move to resources)

---

## Testing Workflows

### Before Publishing Workflow Updates

1. **Clean Environment Test**
```bash
# Create test session
./scripts/utilities/create_new_session.sh "workflow-test"

# Follow documented steps exactly
# [Copy commands from documentation]

# Verify output
ls -lh sessions/workflow-test/output/
ffprobe sessions/workflow-test/output/audio.mp3
```

2. **Check All File Paths**
- Verify scripts exist at documented locations
- Check that all referenced files exist
- Ensure commands use correct paths

3. **Test Edge Cases**
- Long SSML scripts
- Different voice options
- Session-specific workflows
- Error conditions

4. **Verify Prerequisites**
- Are all dependencies documented?
- Do environment checks work?
- Are error messages helpful?

---

## Common Workflow Maintenance Tasks

### Adding New Voice Option

1. Update CANONICAL_WORKFLOW.md:
```markdown
**New Voice:**
- `en-US-Neural2-X` - [Description]
```

2. Test the voice:
```bash
python3 scripts/core/generate_audio_chunked.py \
    test.ssml test.mp3 en-US-Neural2-X
```

3. Update `config/voice_profiles.json` if needed

4. Increment MINOR version

### Changing Mastering Process

1. Test new mastering command thoroughly
2. Update CANONICAL_WORKFLOW.md
3. Add to version history
4. Increment MAJOR version (breaking change)
5. Add migration notes

### Adding New Core Script

1. Create script in appropriate directory
2. Document in CANONICAL_WORKFLOW.md
3. Add to README.md if major feature
4. Test thoroughly
5. Increment MINOR version

---

## Review Checklist

Before committing workflow documentation changes:

- [ ] CANONICAL_WORKFLOW.md updated first
- [ ] All commands tested and working
- [ ] File paths verified to exist
- [ ] Version number incremented
- [ ] Version history updated
- [ ] "Last Updated" date changed
- [ ] README.md updated if needed
- [ ] QUICK_START.md updated if needed
- [ ] No duplicate workflow instructions created
- [ ] All deprecated docs have warnings
- [ ] Session-specific docs reference canonical

---

## Conflict Resolution

### If You Find Conflicting Workflow Information

1. **Identify the Conflict**
   - Which documents conflict?
   - What specifically differs?
   - Which is more recent?

2. **Determine Canonical Version**
   - Check CANONICAL_WORKFLOW.md
   - This is the source of truth
   - Other docs should match this

3. **Fix Discrepancies**
   - Update non-canonical docs to match
   - Or deprecate non-canonical docs
   - Add notices about the conflict

4. **Document the Fix**
   - Add to WORKFLOW_CONSOLIDATION_SUMMARY.md
   - Note what changed and why
   - Update version history

---

## Emergency Workflow Rollback

### If Canonical Workflow Has Critical Error

1. **Identify the Problem**
   - What's broken?
   - Since when?
   - What changed?

2. **Check Git History**
```bash
git log docs/CANONICAL_WORKFLOW.md
git diff [previous-commit] docs/CANONICAL_WORKFLOW.md
```

3. **Revert if Needed**
```bash
git checkout [previous-commit] docs/CANONICAL_WORKFLOW.md
```

4. **Document the Rollback**
   - Add to version history
   - Note why rollback was needed
   - Plan fix for the issue

---

## Automation Opportunities

### Future Improvements

1. **Automated Workflow Testing**
   - CI/CD pipeline that tests documented workflows
   - Verify all file paths exist
   - Run actual commands in clean environment

2. **Link Validation**
   - Check all internal documentation links
   - Verify external links still work
   - Report broken references

3. **Version Consistency Check**
   - Ensure all docs reference same version
   - Warn if canonical workflow version older than session docs

4. **Duplicate Detection**
   - Scan for similar workflow instructions
   - Flag potential duplicates for review

---

## Contact & Questions

**Workflow Maintainer:** [To be assigned]

**When to Update This Guide:**
- When workflow maintenance process changes
- When new workflow patterns emerge
- When automation is added
- Annually (review and refresh)

**Related Documents:**
- [CANONICAL_WORKFLOW.md](CANONICAL_WORKFLOW.md) - The workflow itself
- [WORKFLOW_CONSOLIDATION_SUMMARY.md](../WORKFLOW_CONSOLIDATION_SUMMARY.md) - What was fixed
- [README.md](../README.md) - Project overview

---

**Last Updated:** 2025-11-28
**Guide Version:** 1.0
**Next Review:** 2026-11-28

---

*Keep workflows simple, consistent, and authoritative.*
