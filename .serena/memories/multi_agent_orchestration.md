# Multi-Agent Orchestration System

## Overview

The Dreamweaving project uses a multi-agent orchestration system based on Cherny's Fleet Workflow pattern. This enables parallel agent execution, structured handoffs, and quality gates at each production stage.

## Agent Hierarchy

### Dreamweaver (Mastermind)
- **Role**: Master orchestrator with highest authority
- **Responsibilities**: Parse user intent, delegate to specialized agents, resolve conflicts
- **Decision Authority**: Final say on creative direction, can override individual agent decisions

### Specialized Agents
| Agent | Role | Primary Stage |
|-------|------|---------------|
| Manifest Architect | Generate manifest.yaml | Stage 1 |
| Script Writer | Generate SSML scripts | Stage 2 |
| Audio Engineer | Voice synthesis, mixing, mastering | Stages 3-5 |
| Visual Artist | Midjourney/SD prompts, scene images | Stage 5.5 |
| Video Producer | Video assembly, YouTube package | Stages 6-7 |
| Quality Control | Validation at each gate | All stages |
| Learning Agent | Analytics, feedback processing | Post-production |

## Handoff Contract Protocol

Location: `.claude/protocols/handoff-contract.md`

### Contract Format
```markdown
[Handoff]
From: <Agent Name>
To: <Agent Name>
Session: sessions/{name}/
Stage: <1-9>

## Context
- **Session**: [session path]
- **Prior Outputs**: [what's been done]
- **Knowledge Referenced**: [lessons, patterns, archetypes used]

## Task
[Specific task description]

## Creative Intent
[The transformation/experience to preserve]

## Constraints
- [Safety requirements]
- [Theological boundaries]
- [Technical limitations]

## Exit Criteria
- [ ] [Completion checklist]
```

### Agent-Specific Patterns

**Dreamweaver → Manifest Architect**
- Include: Duration, depth level, desired outcome, archetypes
- Constraints: Theological alignment, safety considerations

**Manifest Architect → Script Writer**
- Include: Complete manifest, section timings, archetype roles
- Constraints: Word count targets, safety clause requirements

**Script Writer → Quality Control**
- Include: SSML file path, validation requirements
- Exit Criteria: SSML validates, safety clauses present

**Quality Control → Audio Engineer**
- Include: Validated script path, binaural specs
- Constraints: Loudness targets, stem levels

## Quality Gates

| Transition | Validation | Command |
|------------|------------|---------|
| 1→2 | Manifest schema | `python3 scripts/utilities/validate_manifest.py` |
| 2→3 | SSML syntax + NLP | `python3 scripts/utilities/validate_ssml.py` |
| 3→4 | Voice quality | `ffprobe` level check |
| 4→5 | Mix levels | Verify -6dB voice/binaural |
| 5→5.5 | Loudness | `-14 LUFS` target |
| 5.5→6 | Image dimensions | 1920x1080 check |
| 6→7 | Video sync | Playback verification |

## Conflict Resolution Rules

Priority order (highest to lowest):
1. **Safety** - Never compromise listener wellbeing
2. **Theological boundaries** - Non-negotiable
3. **Creative intent** - Wins over technical convenience
4. **Technical constraints** - Must be respected
5. **Speed** - Only for iteration/testing

## Progress Tracking Format

```markdown
## Current Session: sessions/{name}/

### Completed
- [x] Stage 1: Manifest created
- [x] Stage 2: Script generated and validated

### In Progress
- [ ] Stage 3: Audio generation (Audio Engineer)

### Pending
- [ ] Stage 4-5: Mixing and mastering
- [ ] Stage 5.5: Scene images
- [ ] Stage 6-7: Video and YouTube package
```

## Rejection Protocol

When an agent cannot complete a task:

```markdown
[Handoff Rejection]
From: <Agent Name>
To: Dreamweaver
Session: sessions/{name}/
Reason: <brief reason>

## Blockers
- [What's preventing completion]

## Suggestions
- [Proposed resolution]

## Questions
- [Clarifications needed]
```

## Parallel Execution Patterns

### When to Parallelize
- Independent tasks (e.g., script generation + image prompt generation)
- Multiple validation checks
- Cross-session searches

### When to Serialize
- Dependent outputs (manifest → script → voice)
- Validation gates (must pass before next stage)
- Resource conflicts (same files being modified)

## Integration with Existing Systems

- **Skills System**: Tier 1-4 skills activate based on task type
- **Knowledge Base**: Agents reference lessons_learned.yaml
- **MCP Servers**: Serena, Notion RAG, SD for specialized operations

## Key Files

| File | Purpose |
|------|---------|
| `.claude/protocols/handoff-contract.md` | Handoff format specification |
| `.claude/agents/dreamweaver.md` | Mastermind orchestration patterns |
| `.claude/agents/quality-control.md` | Automated validation loops |
