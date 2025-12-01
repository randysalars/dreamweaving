---
name: learn-comments
description: Analyze viewer comments for feedback patterns
arguments:
  - name: session
    required: true
    description: Session name
agent: learning-agent
---

# /learn-comments Command

Analyze YouTube comments to extract viewer feedback and improvement suggestions.

## Usage
```
/learn-comments <session>
```

## Example
```
/learn-comments garden-of-eden
```

## Process

1. **Collect comments**
   - User provides comments (copy/paste)
   - Or provides export file

2. **Analyze sentiment**
   - Classify positive/negative/neutral
   - Identify emotional tone

3. **Extract themes**
   - Voice quality feedback
   - Content feedback
   - Pacing/timing feedback
   - Technical issues
   - Suggestions

4. **Generate insights**
   - What viewers love
   - Areas of concern
   - Specific requests

5. **Store learnings**
   - Update `knowledge/lessons_learned.yaml`
   - Note common feedback patterns

## Input Format

Paste comments directly:
```
Comment 1: "This is the most relaxing hypnosis I've ever experienced. The voice is perfect!"

Comment 2: "I fell asleep before the journey section. Is that normal?"

Comment 3: "The binaural beats were too quiet for me, could barely hear them."

Comment 4: "Please make more sessions like this one! The inner child theme really helped."
```

## Analysis Output

```yaml
session: garden-of-eden
total_comments: 23
analysis_date: 2025-12-01

sentiment:
  positive: 18 (78%)
  neutral: 3 (13%)
  negative: 2 (9%)

themes:
  - theme: voice_quality
    sentiment: positive
    mentions: 8
    examples:
      - "voice is perfect"
      - "so soothing"
    insight: "Voice selection (en-US-Neural2-A) well received"

  - theme: pacing
    sentiment: positive
    mentions: 5
    examples:
      - "perfect pace"
      - "loved the slow tempo"
    insight: "0.85 speaking rate working well"

  - theme: binaural_volume
    sentiment: mixed
    mentions: 3
    concern: "Some find binaural too quiet"
    suggestion: "Consider offering different mix versions"

  - theme: content_request
    sentiment: positive
    mentions: 4
    request: "More inner child / healing content"

improvement_suggestions:
  - "Maintain current voice and pacing"
  - "Consider slightly louder binaural option"
  - "Create more healing-themed sessions"

praise_points:
  - Voice quality
  - Relaxation effectiveness
  - Inner child theme resonance
```

## Lesson Generation

From comment analysis, generate lessons:
```yaml
- id: L010
  date: 2025-12-01
  session: garden-of-eden
  category: feedback
  finding: "Voice quality consistently praised"
  evidence: "8 positive mentions, 0 negative"
  action: "Continue using en-US-Neural2-A for healing content"

- id: L011
  date: 2025-12-01
  session: garden-of-eden
  category: audio
  finding: "Some listeners want louder binaural"
  evidence: "3 mentions requesting louder"
  action: "Consider binaural boost option or alternative mix"
```

## Feedback Patterns

Track recurring feedback across sessions:
```yaml
recurring_feedback:
  - pattern: "voice_praise"
    frequency: 85%
    sessions: [garden-of-eden, atlas-starship, neural-navigator]

  - pattern: "duration_requests"
    frequency: 30%
    type: mixed
    note: "Some want longer, some shorter"
```
