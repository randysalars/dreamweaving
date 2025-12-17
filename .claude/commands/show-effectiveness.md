---
description: Display lesson effectiveness rankings
arguments:
  - name: category
    description: Filter by category (content, audio, feedback, all)
    required: false
    default: "all"
---

# Lesson Effectiveness Rankings

Display lesson effectiveness rankings based on measured outcomes.

## Usage

```bash
/show-effectiveness          # Show all ranked lessons
/show-effectiveness content  # Show content lessons only
/show-effectiveness audio    # Show audio lessons only
/show-effectiveness feedback # Show feedback lessons only
```

## What This Shows

For each lesson with sufficient applications (3+):

| Field | Description |
|-------|-------------|
| **ID** | Lesson identifier |
| **Category** | content, audio, or feedback |
| **Score** | Effectiveness score (0-100) |
| **Confidence** | high, medium, low, or archived |
| **Applications** | Times applied |
| **Success Rate** | % of successful generations |
| **Quality Impact** | Quality score delta vs baseline |
| **Retention Impact** | YouTube retention delta |

## Effectiveness Score Formula

```
Score = (success_rate × 0.25) +
        (quality_impact × 0.20) +
        (retention_impact × 0.25) +
        (engagement_impact × 0.15) +
        (recency × 0.10) +
        (consistency × 0.05)
```

## Confidence Thresholds

| Score Range | Confidence Level |
|-------------|------------------|
| >= 70 | high |
| 40-70 | medium |
| 30-40 | low |
| < 30 | archived |

## Execution

Display effectiveness for category: $ARGUMENTS

```python
from pathlib import Path
import sys
sys.path.insert(0, str(Path.cwd()))

category = "$ARGUMENTS" or "all"

try:
    from scripts.ai.learning.effectiveness_engine import EffectivenessEngine
    engine = EffectivenessEngine()

    # Get ranked lessons
    rankings = engine.get_ranked_lessons(
        category=category if category != "all" else None,
        limit=30
    )

    print("## Lesson Effectiveness Rankings\n")
    print(f"Category: {category}\n")

    if not rankings:
        print("No lessons with sufficient applications (min 3) found.")
        print("\nLessons need to be applied to 3+ sessions before effectiveness scoring kicks in.")
    else:
        print("| Rank | ID | Category | Score | Confidence | Apps | Success | Quality Δ |")
        print("|------|----|----------|-------|------------|------|---------|-----------|")

        for i, lesson in enumerate(rankings, 1):
            print(f"| {i} | {lesson.lesson_id} | {lesson.category or 'N/A'} | "
                  f"{lesson.effectiveness_score:.1f} | {lesson.confidence or 'N/A'} | "
                  f"{lesson.times_applied} | {lesson.success_rate*100:.0f}% | "
                  f"{lesson.avg_quality_impact:+.1f} |")

        print(f"\nTotal: {len(rankings)} lessons ranked")

        # Summary statistics
        if rankings:
            avg_score = sum(l.effectiveness_score for l in rankings) / len(rankings)
            high_conf = len([l for l in rankings if l.confidence == 'high'])
            low_conf = len([l for l in rankings if l.confidence == 'low'])

            print(f"\n### Summary")
            print(f"- Average effectiveness score: {avg_score:.1f}")
            print(f"- High confidence lessons: {high_conf}")
            print(f"- Low confidence lessons: {low_conf}")

except ImportError as e:
    print(f"Import error: {e}")
    print("\nMake sure the effectiveness engine is properly installed.")
except Exception as e:
    print(f"Error: {e}")
```

## Interpreting Results

### High Performers (Score >= 70)
These lessons consistently improve session outcomes. They are automatically applied with high priority during generation.

### Medium Performers (Score 40-70)
These lessons show mixed results. They may be context-dependent. Review for potential refinement.

### Low Performers (Score < 40)
These lessons don't improve outcomes or may even harm them. Consider:
1. Revising the lesson content
2. Adding context restrictions
3. Archiving if consistently poor

## See Also

- `/improve` - Run improvement cycle to update scores
- `/recalculate-rankings` - Force recalculation
- `/show-lessons` - View all lessons (not just ranked)
