---
name: Analyze Analytics
level: intermediate
description: Process YouTube Studio analytics to extract insights
---

# Analyze Analytics Skill

## Overview
Process YouTube analytics data to learn what works and improve future sessions.

## Input Data

User provides from YouTube Studio:
- Views
- Watch time (hours)
- Average view duration
- Retention percentage
- Likes / Dislikes
- Comments count
- Shares
- Subscribers gained

## Analysis Process

### 1. Compare to Benchmarks
- How does this session compare to others?
- Is retention above/below average?
- Is engagement (likes/views) good?

### 2. Identify Patterns
- Topic correlation with metrics
- Duration vs retention
- Voice settings vs feedback

### 3. Extract Insights
- What worked well?
- What could improve?
- Specific recommendations

### 4. Store Learnings
Update `knowledge/lessons_learned.yaml` with:
- Finding
- Evidence
- Recommended action
- Confidence level

## Key Metrics to Track

| Metric | Good | Average | Needs Work |
|--------|------|---------|------------|
| Retention (30 min) | >50% | 30-50% | <30% |
| Like Ratio | >8% | 4-8% | <4% |
| Comment Rate | >1% | 0.5-1% | <0.5% |

## Example Insight

```yaml
- finding: "Healing topics achieve higher retention"
  evidence: "62% vs 45% average across 5 sessions"
  action: "Prioritize healing themes"
  confidence: high
```
