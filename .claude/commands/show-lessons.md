---
name: show-lessons
description: Display accumulated learnings from the knowledge base
arguments:
  - name: category
    required: false
    description: Filter by category (content, audio, feedback, code)
agent: learning-agent
---

# /show-lessons Command

Display accumulated learnings and best practices from the knowledge base.

## Usage
```
/show-lessons
/show-lessons content
/show-lessons audio
/show-lessons feedback
```

## Categories

- **content** - Topics, themes, script patterns
- **audio** - Voice settings, binaural, mixing
- **feedback** - Viewer comments, preferences
- **code** - Code quality improvements

## Output

### All Lessons
```
/show-lessons
```

```markdown
# Accumulated Learnings

## Summary
- Total lessons: 15
- Last updated: 2025-12-01
- Sessions analyzed: 5

## By Category

### Content (5 lessons)
- L001: Healing topics achieve 20% higher retention
- L005: 30-minute duration optimal for transformation themes
- L008: Inner child themes resonate strongly with audience
- L012: Story-based journeys outperform abstract experiences
- L015: Seasonal themes (winter/holiday) get initial boost

### Audio (4 lessons)
- L002: 6Hz binaural in journey correlates with "deep relaxation" feedback
- L006: 0.85 speaking rate preferred over 0.90 for journey sections
- L009: en-US-Neural2-A voice consistently praised
- L013: Whisper overlay enhances "mystical" perception

### Feedback (4 lessons)
- L003: Voice quality most praised aspect (85% of positive comments)
- L007: Duration split - some want longer, some shorter
- L010: Binaural volume preference varies - consider options
- L014: Return listeners request follow-up sessions

### Code (2 lessons)
- L004: Retry logic essential for API reliability
- L011: Validation before generation prevents cascading failures

## Top Recommendations
1. Prioritize healing/transformation themes
2. Use en-US-Neural2-A with 0.85 rate
3. Consider offering duration variants
4. Always validate before building
```

### Filtered by Category
```
/show-lessons audio
```

```markdown
# Audio Lessons

## Voice Settings
- **L009**: en-US-Neural2-A consistently praised
  - Evidence: 85% positive mention rate
  - Sessions: garden-of-eden, atlas-starship
  - Action: Default for healing/general content

- **L006**: 0.85 speaking rate preferred
  - Evidence: "Perfect pace" feedback pattern
  - Sessions: All
  - Action: Use 0.85 for journey sections

## Binaural Settings
- **L002**: 6Hz in journey = "deep relaxation"
  - Evidence: Comment analysis correlation
  - Sessions: garden-of-eden
  - Action: Use 6Hz as default for journey

## Mixing
- **L013**: Whisper overlay enhances mystical perception
  - Evidence: "Ethereal", "mystical" keywords increased
  - Sessions: atlas-starship
  - Action: Enable whisper_overlay for spiritual themes
```

## Best Practices Document

Also updates `knowledge/best_practices.md`:
```markdown
# Best Practices - Dreamweaving Production

## Content Creation
- **Topics**: Prioritize healing, inner work, transformation
- **Duration**: 25-35 minutes optimal for YouTube
- **Structure**: Story-based journeys > abstract

## Audio Production
- **Voice**: en-US-Neural2-A for healing (warm, nurturing)
- **Rate**: 0.85 for journey sections
- **Binaural**: 6Hz base for deep trance

## Quality
- Always validate SSML before generation
- Run full validation before publishing
- Check loudness meets -14 LUFS

## Engagement
- Healing themes drive retention
- Voice quality most praised
- Offer response to viewer requests
```

## Applying Lessons

When generating new sessions, lessons are automatically consulted:
```
New session: "confidence building"

Relevant lessons applied:
- L005: Using 25-minute duration (transformation theme)
- L006: Using 0.85 speaking rate
- L009: Using en-US-Neural2-D (confidence = male voice)
```
