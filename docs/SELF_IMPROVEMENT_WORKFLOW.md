# Self-Improvement Workflow (Pillar 3 Implementation)

A self-evolutive system for continuous improvement of the dreamweaving production workflow.

## Core Principle

> "Intelligence that compounds over time by analyzing past operations, adjusting processes based on feedback, and identifying efficiencies without ongoing human intervention."

---

## Feedback Loop Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SESSION PRODUCTION CYCLE                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐     │
│  │  CREATE  │───▶│ GENERATE │───▶│ PUBLISH  │───▶│ ANALYZE  │     │
│  │  Session │    │   Audio  │    │  Video   │    │ Feedback │     │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘     │
│       │                                               │            │
│       │         ┌─────────────────────────────────────┘            │
│       │         │                                                  │
│       │         ▼                                                  │
│       │   ┌─────────────┐                                         │
│       │   │   LEARN     │                                         │
│       │   │ • Extract   │                                         │
│       │   │ • Pattern   │                                         │
│       │   │ • Record    │                                         │
│       │   └─────────────┘                                         │
│       │         │                                                  │
│       │         ▼                                                  │
│       │   ┌─────────────┐                                         │
│       └◀──│   APPLY     │                                         │
│           │ • Recommend │                                         │
│           │ • Auto-tune │                                         │
│           │ • Generate  │                                         │
│           └─────────────┘                                         │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 1. Feedback Collection Points

### A. Production Metrics (Automatic)

Collected after each session generation:

| Metric | Source | Purpose |
|--------|--------|---------|
| Duration accuracy | Compare target vs actual | Improve estimation |
| Audio quality score | quality_scorer.py | Track improvements |
| Generation time | Pipeline logs | Efficiency tracking |
| Error count | Validation logs | Code quality |
| Resource usage | System metrics | Optimization |

### B. Analytics Data (Manual Import)

From YouTube Studio:

```bash
python3 scripts/ai/learning/feedback_analyzer.py \
    --analytics path/to/analytics.json \
    --update-knowledge
```

Key metrics:
- Average view duration
- Retention curve
- Engagement rate (likes/comments/shares)
- Subscriber conversion

### C. Viewer Comments (Manual Import)

```bash
python3 scripts/ai/learning/feedback_analyzer.py \
    --comments path/to/comments.txt \
    --update-knowledge
```

Analysis includes:
- Sentiment distribution
- Theme extraction
- Specific suggestions
- Common complaints

### D. Session Review (After Each Production)

Triggered automatically or manually:

```bash
python3 scripts/ai/learning/lessons_manager.py add \
    --category audio \
    --lesson "Static binaural lacks hypnotic arc" \
    --importance high \
    --tags "binaural,effectiveness"
```

---

## 2. Learning System Components

### A. Knowledge Base Structure

```
knowledge/
├── lessons_learned.yaml      # Accumulated learnings
├── best_practices.md         # Auto-updated guide
├── analytics_history/        # Historical data
├── code_improvements/        # Code fix history
└── session_learnings/        # Per-session analysis
    └── {session}_{date}.yaml
```

### B. Lessons Manager

```bash
# View all lessons
python3 scripts/ai/learning/lessons_manager.py show

# View high-priority lessons
python3 scripts/ai/learning/lessons_manager.py show --importance high

# Get recommendations for new session
python3 scripts/ai/learning/lessons_manager.py recommend --theme cosmic --duration 30

# View statistics
python3 scripts/ai/learning/lessons_manager.py stats
```

### C. Feedback Analyzer

```bash
# Analyze YouTube analytics
python3 scripts/ai/learning/feedback_analyzer.py --analytics data.json

# Analyze viewer comments
python3 scripts/ai/learning/feedback_analyzer.py --comments comments.txt

# Full session analysis with knowledge update
python3 scripts/ai/learning/feedback_analyzer.py \
    --session sessions/my-session \
    --update-knowledge
```

---

## 3. Automatic Improvement Triggers

### A. Pre-Generation Phase

Before generating a new session, the system should:

1. **Query relevant lessons:**
   ```python
   from scripts.ai.learning.lessons_manager import LessonsManager

   manager = LessonsManager()
   recommendations = manager.get_recommendations(
       theme="neuroplasticity",
       duration=30*60
   )
   ```

2. **Apply high-confidence lessons automatically:**
   - Voice selection based on theme
   - Binaural progression based on session type
   - Duration estimation adjustments

3. **Suggest medium-confidence lessons for review:**
   - Display recommendations to user
   - Allow override or acceptance

### B. Post-Generation Phase

After generating a session:

1. **Compare metrics to targets:**
   ```python
   # Automatic metrics collection
   metrics = {
       'duration_target': manifest['duration'] * 60,
       'duration_actual': get_audio_duration(output_path),
       'deviation_percent': calculate_deviation(...)
   }
   ```

2. **Record deviations as lessons:**
   - If deviation > 10%, create lesson
   - If quality score < threshold, flag for review

3. **Update success patterns:**
   - Track which settings produced good results
   - Reinforce effective patterns

### C. Analytics Integration Phase

When analytics become available:

1. **Import and analyze:**
   ```bash
   python3 scripts/ai/learning/feedback_analyzer.py \
       --analytics youtube_analytics.json \
       --session sessions/my-session \
       --update-knowledge
   ```

2. **Correlate with production settings:**
   - Match retention drops to script timestamps
   - Identify audio settings that correlate with engagement

3. **Generate actionable improvements:**
   - "Retention drops at 12:30 - review transition pacing"
   - "High engagement correlated with 6 Hz theta sections"

---

## 4. Pattern Recognition

### A. Cross-Session Analysis

Periodically analyze patterns across sessions:

```bash
python3 scripts/ai/learning/lessons_manager.py patterns --sessions 10
```

Patterns to track:
- Which themes get best retention
- Optimal duration by topic
- Voice preferences by content type
- Binaural settings by effectiveness

### B. A/B Testing Framework

When uncertain about approaches:

1. Create variant sessions
2. Track performance metrics
3. Record winner as lesson
4. Apply to future sessions

Example lesson:
```yaml
- id: L010
  finding: "Dynamic binaural (8 Hz → 4 Hz) outperforms static 6 Hz by 15% retention"
  evidence: "A/B test: session-A (dynamic) vs session-B (static)"
  confidence: high
  action: "Default to dynamic binaural for all theta sessions"
```

---

## 5. Autonomous Adjustments

### A. Auto-Tunable Parameters

Parameters that can be adjusted automatically based on feedback:

| Parameter | Source of Truth | Adjustment Logic |
|-----------|-----------------|------------------|
| Speaking rate | Retention curves | Slow down at drop points |
| Binaural volume | Viewer comments | Adjust if complaints |
| Session length | Watch time data | Match sweet spot |
| Pause duration | Retention vs script | Optimize breaks |

### B. Manual Override Points

Parameters requiring human judgment:

| Parameter | Why Manual |
|-----------|-----------|
| Theme selection | Creative decision |
| Script content | Artistic control |
| Visual style | Brand consistency |
| Voice personality | Character choice |

---

## 6. Integration with Production Scripts

### A. Pipeline Hook Points

```python
# In pipeline.py or build_session.py

# PRE-GENERATION HOOK
def pre_generation_hook(manifest, session_path):
    # Query lessons
    manager = LessonsManager()
    recommendations = manager.get_recommendations(
        theme=manifest.get('theme'),
        duration=manifest.get('duration')
    )

    # Apply automatic adjustments
    for rec in recommendations['audio']:
        if rec['confidence'] == 'high':
            apply_audio_recommendation(manifest, rec)

    return manifest

# POST-GENERATION HOOK
def post_generation_hook(session_path, metrics):
    # Record session learnings
    learning_path = Path('knowledge/session_learnings')
    session_name = session_path.name

    record_session_metrics(learning_path, session_name, metrics)

    # Check for issues
    issues = detect_issues(metrics)
    for issue in issues:
        manager.add_lesson(
            category=issue['category'],
            lesson=issue['description'],
            importance=issue['severity']
        )
```

### B. Interactive Recommendations

When starting a new session:

```
$ python3 scripts/utilities/create_new_session.sh "my-new-session"

Creating session: my-new-session

📚 RECOMMENDATIONS FROM LEARNING SYSTEM:

AUDIO:
  [HIGH] Use dynamic binaural progression (12→6→10 Hz)
  [HIGH] Add 40 Hz gamma burst at insight moment
  [MED]  Consider micro-modulation during theta

CONTENT:
  [HIGH] Pre-estimate duration (target: 30 min = ~3000 words + 8 min pauses)
  [MED]  Story-based journeys show 20% higher retention

Apply recommendations? [Y/n/select]:
```

---

## 7. Workflow Commands

### Daily Operations

```bash
# Start new session with recommendations
./scripts/utilities/create_new_session.sh "session-name" --apply-lessons

# Generate with automatic metrics collection
python3 scripts/core/build_session.py sessions/session-name --track-metrics

# Review what was learned
python3 scripts/ai/learning/lessons_manager.py show --days 7
```

### Weekly Review

```bash
# Analyze all sessions from past week
python3 scripts/ai/learning/feedback_analyzer.py --weekly-review

# Update best practices document
python3 scripts/ai/learning/lessons_manager.py update-best-practices

# View improvement trends
python3 scripts/ai/learning/lessons_manager.py stats --trend
```

### When Analytics Available

```bash
# Full feedback integration
python3 scripts/ai/learning/feedback_analyzer.py \
    --analytics youtube_data.json \
    --comments viewer_comments.txt \
    --session sessions/my-session \
    --update-knowledge \
    --generate-report
```

---

## 8. Success Metrics

Track these to measure system effectiveness:

| Metric | Target | How Measured |
|--------|--------|--------------|
| Duration accuracy | Within 10% | Actual vs target |
| Quality score trend | Increasing | Weekly average |
| Lesson application rate | >80% | Applied/recommended |
| Viewer retention | >45% | YouTube analytics |
| Issue recurrence | Decreasing | Same issue count |

---

## Implementation Status

### Implemented ✓
- [x] LessonsManager (lessons_manager.py)
- [x] FeedbackAnalyzer (feedback_analyzer.py)
- [x] CodeReviewer (code_reviewer.py)
- [x] Quality Scorer (quality_scorer.py)
- [x] Knowledge base structure
- [x] **Dynamic Binaural Generator** (`scripts/core/generate_dynamic_binaural.py`)
  - Reads frequency maps from manifest or JSON files
  - Built-in presets: neuroplasticity, standard_hypnotic, deep_sleep, confidence, healing
  - Supports gamma bursts, micro-modulation, smooth transitions
  - Template generation for new sessions
- [x] **Duration Estimator** (`scripts/utilities/estimate_duration.py`)
  - Estimates SSML duration before voice generation
  - Accounts for word count, pauses, and speaking rate
  - Compares with target and suggests adjustments
- [x] **Pre-Generation Check** (`scripts/ai/pre_generation_check.py`)
  - Validates session before generation
  - Queries lessons learned for recommendations
  - Checks duration, binaural config, voice settings
  - Outputs prioritized recommendations (critical, high, medium)
- [x] **Post-Generation Metrics** (`scripts/ai/post_generation_metrics.py`)
  - Collects actual duration and quality metrics
  - Compares with targets and estimates
  - Analyzes binaural implementation
  - Auto-records lessons learned (with --record-lesson flag)
  - Generates learning reports (with --save-report flag)

### Needs Implementation
- [ ] Interactive recommendations in session creation script
- [ ] Automatic lesson extraction from production runs
- [ ] A/B testing framework
- [ ] Pipeline hook integration (pre/post generation)

### Future Enhancements
- [ ] ML-based pattern recognition
- [ ] Automated YouTube analytics import
- [ ] Viewer engagement prediction
- [ ] Content recommendation engine

---

## Quick Reference - New Tools

### Pre-Generation (BEFORE voice synthesis)

```bash
# 1. Estimate duration from SSML
python3 scripts/utilities/estimate_duration.py \
    sessions/my-session/working_files/script.ssml \
    --manifest sessions/my-session/manifest.yaml

# 2. Run pre-generation check (queries lessons + validates config)
python3 scripts/ai/pre_generation_check.py sessions/my-session

# 3. Generate dynamic binaural with preset
python3 scripts/core/generate_dynamic_binaural.py \
    sessions/my-session/output/binaural.wav \
    --duration 1800 \
    --preset neuroplasticity

# Or generate a frequency map template first
python3 scripts/core/generate_dynamic_binaural.py \
    output.wav --generate-template --template-preset neuroplasticity --duration 1800 \
    > sessions/my-session/working_files/binaural_frequency_map.json
```

### Post-Generation (AFTER session complete)

```bash
# Collect metrics and analyze
python3 scripts/ai/post_generation_metrics.py sessions/my-session

# Save learning report to knowledge base
python3 scripts/ai/post_generation_metrics.py sessions/my-session --save-report

# Auto-record lessons from issues
python3 scripts/ai/post_generation_metrics.py sessions/my-session --record-lesson
```

### Available Binaural Presets

| Preset | Description | Key Features |
|--------|-------------|--------------|
| `neuroplasticity` | Neural Network Navigator style | 12→8→7→6 Hz + 40 Hz gamma burst |
| `standard_hypnotic` | Standard hypnotic arc | 12→8→6→8→10 Hz |
| `deep_sleep` | Sleep induction | 10→6→3→1.5 Hz |
| `confidence` | Activation/confidence | 14→10→7→10→14 Hz |
| `healing` | Healing/recovery | 10→6→4→6→10 Hz |
| `static_theta` | Simple static theta | 6 Hz throughout |

---

*This document describes the Pillar 3 (Self-Evolutive Systems) implementation for the Dreamweaving project. The system learns and improves automatically through feedback loops, pattern recognition, and data analysis.*

*Last updated: 2025-12-01*
