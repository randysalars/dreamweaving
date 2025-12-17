---
name: Recursive Improver
role: self_evolving_orchestrator
description: Self-evolving agent that continuously improves the entire Dreamweaving system through feedback loops
knowledge_files:
  - knowledge/lessons_learned.yaml
  - knowledge/best_practices.md
  - knowledge/feedback/outcome_records.yaml
  - knowledge/feedback/lesson_effectiveness.yaml
  - knowledge/feedback/pending_outcome_checks.yaml
scripts:
  - scripts/ai/recursive_improver.py
  - scripts/ai/learning/feedback_store.py
  - scripts/ai/learning/effectiveness_engine.py
  - scripts/ai/agents/dreamweaver_recursive.py
skills_required:
  tier4:  # Growth and learning
    - analytics-learning
    - feedback-integration
---

# Recursive Improver Agent

## Role

Self-evolving orchestrator that continuously improves the entire Dreamweaving system by:
1. Tracking lesson effectiveness across sessions
2. Promoting successful patterns and demoting unsuccessful ones
3. Connecting session outcomes to YouTube analytics
4. Automating the learning feedback loop

## The Recursive Improvement Loop

```
┌─────────────────────────────────────────────────────────────────────┐
│                 RECURSIVE IMPROVEMENT LOOP                          │
│                                                                      │
│   ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐   │
│   │ RETRIEVE │ ──► │  APPLY   │ ──► │ GENERATE │ ──► │ MEASURE  │   │
│   │ LESSONS  │     │ LESSONS  │     │ SESSION  │     │ OUTCOME  │   │
│   └──────────┘     └──────────┘     └──────────┘     └──────────┘   │
│        ▲                                                  │          │
│        │                                                  ▼          │
│   ┌──────────┐                                      ┌──────────┐    │
│   │  UPDATE  │ ◄────────────────────────────────── │  SCORE   │    │
│   │ RANKINGS │                                      │ LESSONS  │    │
│   └──────────┘                                      └──────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

## Core Capabilities

### 1. Lesson Retrieval & Ranking

Before session generation:
- Retrieve lessons relevant to topic, duration, and desired outcome
- Rank lessons by effectiveness score (0-100)
- Filter lessons that have been applied 3+ times (statistical validity)
- Apply context-aware boosting for similar topics

```python
# Example usage
from scripts.ai.recursive_improver import RecursiveImprover

improver = RecursiveImprover()
lessons = improver.get_ranked_lessons(
    topic="Finding Inner Peace",
    duration=25,
    desired_outcome="relaxation",
    category="content",
    limit=10
)
```

### 2. Outcome Recording

After session generation:
- Record immediate metrics (success, quality score, stages completed)
- Track which lessons were applied
- Schedule YouTube analytics check for later (7-day delay)

```python
outcome_id = improver.record_session_outcome(
    session_name="finding-inner-peace-20251217",
    applied_lessons=["L001", "L005", "L012"],
    metrics={
        'generation_success': True,
        'quality_score': 78.5,
        'stages_completed': ['voice', 'mixing', 'mastering'],
    }
)
```

### 3. Effectiveness Scoring

The effectiveness score is a weighted composite:

| Metric | Weight | Description |
|--------|--------|-------------|
| Success Rate | 25% | Did generation succeed? |
| Quality Impact | 20% | Quality score delta vs baseline |
| Retention Impact | 25% | YouTube retention delta |
| Engagement Impact | 15% | YouTube engagement delta |
| Recency | 10% | Recent lessons weighted higher |
| Consistency | 5% | Lower variance = higher score |

### 4. Confidence Promotion/Demotion

Based on effectiveness scores:
- **Score >= 70**: Promote to high confidence
- **Score 40-70**: Maintain current confidence
- **Score < 40**: Demote to low confidence
- **Score < 30**: Archive (rarely applied)

## Data Storage

### Feedback Directory Structure

```
knowledge/feedback/
├── outcome_records.yaml        # Session outcomes with metrics
├── lesson_effectiveness.yaml   # Lesson effectiveness tracking
└── pending_outcome_checks.yaml # Scheduled YouTube checks
```

### Outcome Record Schema

```yaml
record_id: "outcome-20251217-143022-finding-inner-peace"
session_name: "finding-inner-peace-20251217"
created_at: "2025-12-17T14:30:22"
lesson_ids:
  - L001
  - L005
  - L012
generation_success: true
quality_score: 78.5
stages_completed: ["voice", "mixing", "mastering"]
stages_failed: []
execution_time_seconds: 1847.3
estimated_cost_usd: 1.06
youtube_video_id: null  # Set after upload
avg_retention_pct: null  # Set after YouTube tracking
engagement_rate: null
views_30d: null
likes: null
comments: null
```

### Lesson Effectiveness Schema

```yaml
lesson_id: "L001"
times_applied: 12
times_succeeded: 10
success_rate: 0.833
avg_quality_impact: 73.2
quality_variance: 45.6
avg_retention_impact: 4.2  # Delta vs baseline
avg_engagement_impact: 0.012
last_applied: "2025-12-17T14:30:22"
first_applied: "2025-10-01T09:15:00"
best_contexts:
  - "relaxation-healing"
  - "nature-garden"
worst_contexts:
  - "confidence-power"
context_effectiveness:
  relaxation-healing: 82.5
  nature-garden: 78.3
  confidence-power: 41.2
```

## Commands

### `/improve [agent_type]`

Run manual improvement cycle for specified agent type.

```bash
# Dreamweaver improvement cycle
/improve dreamweaver

# RAG improvement cycle (future)
/improve rag

# Website improvement cycle (future)
/improve website
```

### `/show-effectiveness [category]`

Display lesson effectiveness rankings.

```bash
# Show all ranked lessons
/show-effectiveness

# Show content lessons only
/show-effectiveness content

# Show audio lessons only
/show-effectiveness audio
```

### `/recalculate-rankings`

Force recalculation of all lesson effectiveness scores.

```bash
/recalculate-rankings
```

## Integration Points

### auto_generate.py

The recursive improver is automatically integrated:

1. **_stage_create_plan**: Retrieves ranked lessons before generation
2. **_stage_self_improvement**: Records outcome after generation

### Manifest Tracking

Applied lessons are tracked in session manifests:

```yaml
# sessions/{name}/manifest.yaml
recursive_improvement:
  applied_lessons:
    - L001
    - L005
    - L012
  lesson_count: 3
  categories:
    content: 2
    audio: 1
  applied_at: "2025-12-17T14:30:22"
```

## Automation Schedule

| Task | Schedule | Purpose |
|------|----------|---------|
| `process_pending_outcomes` | 3 AM daily | Check sessions awaiting YouTube metrics |
| `recalculate_rankings` | 4 AM Sunday | Weekly lesson re-ranking |
| `sync_youtube_analytics` | 5 AM daily | Fetch YouTube data |
| `optimize_knowledge` | 6 AM Monday | Knowledge gap detection |

## Configuration

### Environment Variables

```bash
# YouTube API (for delayed metrics)
YOUTUBE_API_KEY=your-api-key
YOUTUBE_CLIENT_ID=your-client-id
YOUTUBE_CLIENT_SECRET=your-client-secret

# Google Analytics (for website tracking)
GA_MEASUREMENT_ID=G-XXXXXXXXXX
GA_STREAM_ID=your-stream-id
```

### automation_config.yaml

```yaml
recursive_improvement:
  enabled: true
  min_applications: 3  # Min uses before scoring
  promotion_threshold: 70.0
  demotion_threshold: 40.0
  archive_threshold: 30.0
  decay_half_life_days: 60
  youtube_check_delay_days: 7

  weights:
    success_rate: 0.25
    quality_impact: 0.20
    retention_impact: 0.25
    engagement_impact: 0.15
    recency: 0.10
    consistency: 0.05
```

## Baseline Metrics

The system maintains rolling baseline metrics for comparison:

| Metric | Default | Description |
|--------|---------|-------------|
| avg_quality_score | 65.0 | Average quality score across sessions |
| avg_retention_pct | 35.0 | Average YouTube retention percentage |
| avg_engagement_rate | 0.03 | Average engagement rate (likes+comments/views) |

Baselines are recalculated weekly based on actual outcomes.

## Success Metrics

| Metric | Current | Target (3 months) |
|--------|---------|-------------------|
| Lessons with applications tracked | ~10% | 80% |
| Sessions using ranked lessons | 0% | 100% |
| YouTube analytics connected | No | Yes |
| Avg quality score improvement | N/A | +15% |

## Sub-Agents (All Implemented)

### RAG Recursive Agent

Self-improving knowledge retrieval:
- Location: `scripts/ai/agents/rag_recursive.py`
- Track which queries produce good sessions
- Boost successful query patterns
- Deep relationship traversal (archetype → realm → frequency)
- Semantic query caching

```python
from scripts.ai.agents import create_rag_recursive_agent

agent = create_rag_recursive_agent()
context = agent.prepare_context(
    topic="Finding Inner Peace",
    desired_outcome="relaxation",
    depth=2
)
print(context.to_prompt_context())
```

### Website Recursive Agent

Self-improving content marketing:
- Location: `scripts/ai/website/website_recursive.py`
- Track page performance via Google Analytics
- Extract success patterns from top performers
- Generate improvement suggestions
- SEO auto-optimization based on keywords

```python
from scripts.ai.website import create_website_recursive_agent

agent = create_website_recursive_agent()
results = agent.run_improvement_cycle()
print(results['priority_actions'])
```

## Troubleshooting

### No Lessons Retrieved

1. Check if `lessons_learned.yaml` exists and has lessons
2. Verify lessons have `id` field
3. Check if LessonsManager can load the file

### Outcome Not Recorded

1. Check if `knowledge/feedback/` directory exists
2. Verify write permissions
3. Check for YAML serialization errors in logs

### Effectiveness Not Updating

1. Ensure 3+ applications for lesson (MIN_APPLICATIONS)
2. Run `/recalculate-rankings` manually
3. Check `lesson_effectiveness.yaml` for data integrity
