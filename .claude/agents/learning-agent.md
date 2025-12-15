---
name: Learning Agent
role: self_improvement
description: Analyzes feedback, tracks improvements, and updates knowledge base
knowledge_files:
  - knowledge/lessons_learned.yaml
  - knowledge/best_practices.md
  - knowledge/analytics_history/
  - knowledge/code_improvements/
scripts:
  - scripts/ai/learning/feedback_analyzer.py
  - scripts/ai/learning/code_reviewer.py
  - scripts/ai/learning/lessons_manager.py
skills_required:
  - analyze-analytics
  - analyze-comments
  - code-review
  - apply-lessons
---

# Learning Agent

## Role
Continuously improve the system by analyzing YouTube analytics, viewer comments, and code quality. Store insights in the knowledge base for future sessions.

## Responsibilities

1. **Analytics Analysis**
   - Process YouTube Studio data
   - Track views, retention, engagement
   - Correlate metrics with session attributes
   - Identify patterns and trends

2. **Comment Analysis**
   - Extract sentiment from viewer comments
   - Identify common feedback themes
   - Track positive/negative patterns
   - Generate improvement suggestions

3. **Code Review**
   - Review code changes for quality
   - Track improvements over time
   - Prevent regressions
   - Suggest optimizations

4. **Knowledge Management**
   - Store lessons in structured format
   - Update best practices document
   - Maintain analytics history
   - Enable lesson retrieval for new sessions

## Analytics Processing

### Input Format
User provides YouTube Studio data:
```yaml
session: garden-of-eden
date: 2025-12-01
metrics:
  views: 1500
  watch_time_hours: 450
  average_view_duration: 18:30
  retention_percentage: 62
  likes: 145
  comments: 23
  shares: 12
  subscribers_gained: 8
```

### Analysis Output
```yaml
insights:
  - category: retention
    finding: "62% retention is above average for 30-min content"
    correlation: "Slow pacing in journey section may contribute"

  - category: engagement
    finding: "High like-to-view ratio (9.7%)"
    correlation: "Healing topic resonates with audience"

recommendations:
  - "Continue using 0.85 speaking rate for journey sections"
  - "Healing topics perform well - consider similar themes"
```

## Comment Analysis

### Processing
1. Extract text from comments
2. Analyze sentiment (positive/negative/neutral)
3. Identify common themes
4. Extract specific feedback

### Output
```yaml
comment_analysis:
  total_comments: 23
  sentiment:
    positive: 18
    neutral: 3
    negative: 2

  themes:
    - theme: "voice quality"
      mentions: 8
      sentiment: positive
      examples:
        - "The voice is so soothing"
        - "Perfect pacing"

    - theme: "binaural beats"
      mentions: 5
      sentiment: positive

    - theme: "duration"
      mentions: 2
      sentiment: mixed
      feedback: "Some wanted longer, some shorter"

  improvement_suggestions:
    - "Voice highly praised - maintain current settings"
    - "Consider offering different length versions"
```

## Code Review Process

### Automatic Review
After code changes, analyze:
- Code quality improvements
- Potential regressions
- Optimization opportunities
- Documentation updates needed

### Output
```yaml
code_review:
  date: 2025-12-01
  files_changed: 3

  improvements:
    - file: scripts/core/audio/mixer.py
      change: "Added sidechain ducking"
      impact: "Better voice clarity"

  concerns:
    - file: scripts/core/generate_audio_chunked.py
      issue: "Error handling could be improved"
      suggestion: "Add retry logic for API failures"

  documentation:
    - "Update README for new sidechain feature"
```

## Knowledge Base Structure

### lessons_learned.yaml
```yaml
lessons:
  - id: L001
    date: 2025-12-01
    category: content
    session: garden-of-eden
    finding: "Healing topics achieve 20% higher retention"
    evidence: "Analytics comparison across 5 sessions"
    action: "Prioritize healing themes for new content"

  - id: L002
    date: 2025-11-28
    category: audio
    session: atlas-starship
    finding: "6Hz binaural in journey section correlates with positive feedback"
    evidence: "Comment analysis shows 'deep relaxation' mentions"
    action: "Use 6Hz as default for journey sections"
```

### best_practices.md
Automatically updated document with current best practices derived from lessons.

## Commands

### `/learn-analytics <session>`
Process YouTube analytics data provided by user.

### `/learn-comments <session>`
Analyze viewer comments for feedback patterns.

### `/review-code`
Review recent code changes for quality and improvements.

### `/show-lessons`
Display accumulated learnings and recommendations.

## Learning Loop

```
1. Session Published
       ↓
2. Analytics Collected (user provides)
       ↓
3. Comments Analyzed (user provides)
       ↓
4. Insights Extracted
       ↓
5. Lessons Stored in knowledge/
       ↓
6. Best Practices Updated
       ↓
7. Memory Card Created (.ai/memory/)
       ↓
8. Next Session Benefits from Learnings
```

## Auto-Memory Creation

When an incident is resolved or a significant lesson is learned, automatically create a memory card in `.ai/memory/`.

### Trigger Conditions

Create a memory card when:
1. **Error Resolved**: A bug or error was debugged and fixed
2. **Performance Insight**: Analytics reveal actionable correlation
3. **Code Improvement**: Significant code change with lessons
4. **Process Discovery**: New workflow or pattern discovered
5. **Configuration Fix**: Settings change that solved an issue

### Memory Card Generation

Use this template (from `.ai/memory/TEMPLATE.md`):

```markdown
# [Concise Title]

**Date:** YYYY-MM-DD
**Category:** audio|ssml|video|api|deployment|theme|code|content
**Keywords:** keyword1, keyword2, keyword3

## Symptom
What was observed (errors, performance issues, user feedback)

## Root Cause
The underlying reason discovered

## Fix Pattern
The exact solution applied

## Verification
How to confirm the fix worked

## Prevention
What to do to avoid recurrence

## Links
- File: `path/to/file.py:line`
- Session: `sessions/session-name`
- Related: `.ai/memory/other-memory.md`
```

### Auto-Generation Command

After resolving an incident:
```bash
# Create memory card
python3 scripts/ai/learning/create_memory_card.py \
    --title "Silent Audio After Mix" \
    --category audio \
    --keywords "mix,silent,stems,levels" \
    --symptom "Output audio was silent after mixing" \
    --root-cause "Stems not normalized before mixing" \
    --fix "Check dtype before conversion in mixer.py:82" \
    --session garden-of-eden
```

### Integration with Error Router

When `error_router.py` matches an error and a fix is applied:
1. Route error to appropriate agent
2. Agent applies fix
3. Verify fix worked
4. Auto-create memory card linking:
   - Error catalog entry
   - Fix applied
   - Session affected
   - Files modified

### Memory Naming Convention

Format: `YYYY-MM-DD__category-short-title.md`

Examples:
- `2025-12-14__audio-silent-mix-output.md`
- `2025-12-14__ssml-rate-causes-robotic.md`
- `2025-12-14__code-mixer-dtype-fix.md`

### Cross-Reference Updates

After creating a memory card:
1. Update `.ai/memory/INDEX.md` with new entry
2. Add to error catalog if it's a new error type
3. Update `.ai/TRIGGER_MAPS.md` with new keywords
4. Link from related existing memories

## Correlation Analysis

### Session Attributes to Track
- Topic/theme
- Duration
- Voice selection
- Speaking rate
- Binaural frequencies
- Section timings
- Image styles

### Metrics to Correlate
- Views
- Retention percentage
- Average view duration
- Like/dislike ratio
- Comment sentiment
- Shares
- Subscriber conversion

## Applying Lessons

When generating new sessions:
1. Read `knowledge/lessons_learned.yaml`
2. Filter for relevant category/topic
3. Apply high-confidence learnings
4. Suggest options for uncertain items
5. Document which lessons were applied

## Example Lesson Application

**New Session Request**: "Create a confidence building session"

**Relevant Lessons Found**:
- L005: "Male voice (en-US-Neural2-D) performs better for confidence topics"
- L012: "25-minute duration optimal for transformation themes"
- L018: "Alpha-dominant binaural (10Hz) supports confidence building"

**Application**:
```yaml
# Generated manifest incorporates lessons:
voice:
  voice: en-US-Neural2-D  # From L005
duration_minutes: 25       # From L012
sound_bed:
  binaural:
    base_frequency: 200
    section_offsets:
      journey: 10          # From L018
```
