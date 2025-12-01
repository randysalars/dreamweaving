---
name: learn-analytics
description: Process YouTube analytics data for a session
arguments:
  - name: session
    required: true
    description: Session name
agent: learning-agent
---

# /learn-analytics Command

Process YouTube Studio analytics data to extract insights and improve future sessions.

## Usage
```
/learn-analytics <session>
```

## Example
```
/learn-analytics garden-of-eden
```

## Process

1. **Request analytics data**
   - User provides YouTube Studio metrics
   - Or pastes analytics screenshot text

2. **Parse metrics**
   - Views, watch time
   - Average view duration
   - Retention percentage
   - Likes, comments, shares
   - Subscriber conversion

3. **Analyze performance**
   - Compare to previous sessions
   - Identify patterns
   - Correlate with session attributes

4. **Extract insights**
   - What worked well
   - Areas for improvement
   - Specific recommendations

5. **Store learnings**
   - Update `knowledge/lessons_learned.yaml`
   - Update `knowledge/best_practices.md`
   - Save raw data to `knowledge/analytics_history/`

## Input Format

Provide metrics in any format:
```
Session: garden-of-eden
Date: 2025-12-01
Views: 1,500
Watch time: 450 hours
Average view duration: 18:30
Retention: 62%
Likes: 145
Comments: 23
Shares: 12
New subscribers: 8
```

## Output

### Insights Generated
```yaml
session: garden-of-eden
date: 2025-12-01
metrics:
  views: 1500
  retention: 62%
  avg_duration: "18:30"

insights:
  - category: retention
    finding: "62% retention is excellent for 30-min content"
    confidence: high

  - category: engagement
    finding: "High like ratio (9.7%) indicates content resonates"
    confidence: high

correlations:
  - attribute: topic
    value: healing
    metric: retention
    observation: "Healing topics average 15% higher retention"

recommendations:
  - "Continue healing theme focus"
  - "Maintain current pacing (0.85 rate)"
  - "Consider series on related healing topics"
```

## Lesson Storage

Insights are stored in `knowledge/lessons_learned.yaml`:
```yaml
lessons:
  - id: L001
    date: 2025-12-01
    session: garden-of-eden
    category: content
    finding: "Healing topics achieve higher retention"
    evidence: "62% vs 45% average"
    action: "Prioritize healing themes"
    confidence: high
```

## Tracking Over Time

Analytics history stored in:
```
knowledge/analytics_history/
└── garden-of-eden/
    ├── analytics_2025-12-01.yaml
    ├── analytics_2025-12-15.yaml
    └── analytics_2025-12-30.yaml
```

This enables trend analysis across time.

## Best Practice Updates

When patterns emerge, `knowledge/best_practices.md` is updated:
```markdown
## Content Topics
- **Healing themes**: Consistently achieve 15-20% higher retention
- Recommendation: Prioritize healing, inner work, transformation topics
```
