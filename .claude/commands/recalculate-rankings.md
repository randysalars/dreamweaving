---
description: Force re-rank all lessons based on effectiveness
arguments: []
---

# Recalculate Lesson Rankings

Force recalculation of all lesson effectiveness scores and update confidence levels.

## Usage

```bash
/recalculate-rankings
```

## What This Does

1. **Loads all outcome records** from `knowledge/feedback/`
2. **Correlates lessons** with session outcomes
3. **Recalculates effectiveness scores** using weighted formula
4. **Updates confidence levels** based on thresholds:
   - Score >= 70 → Promote to `high`
   - Score 40-70 → Maintain `medium`
   - Score 30-40 → Demote to `low`
   - Score < 30 → Archive
5. **Applies time decay** (60-day half-life)
6. **Saves updated rankings** to effectiveness store

## When to Use

- After manually editing lessons
- After importing new outcome data
- When rankings seem stale or incorrect
- After changing scoring weights
- Weekly maintenance (automated)

## Execution

```python
from pathlib import Path
import sys
sys.path.insert(0, str(Path.cwd()))

try:
    from scripts.ai.learning.effectiveness_engine import EffectivenessEngine
    from scripts.ai.learning.feedback_store import FeedbackStore

    engine = EffectivenessEngine()
    store = FeedbackStore()

    print("## Recalculating Lesson Rankings\n")

    # Get before stats
    before_rankings = engine.get_ranked_lessons(limit=100)
    before_count = len(before_rankings)
    before_avg = sum(l.effectiveness_score for l in before_rankings) / before_count if before_rankings else 0

    print(f"Before: {before_count} ranked lessons, avg score {before_avg:.1f}")

    # Recalculate
    print("\nRecalculating...")
    engine.recalculate_all_rankings()

    # Get after stats
    after_rankings = engine.get_ranked_lessons(limit=100)
    after_count = len(after_rankings)
    after_avg = sum(l.effectiveness_score for l in after_rankings) / after_count if after_rankings else 0

    print(f"After: {after_count} ranked lessons, avg score {after_avg:.1f}")

    # Show changes
    promotions = []
    demotions = []

    for after in after_rankings:
        for before in before_rankings:
            if after.lesson_id == before.lesson_id:
                if after.confidence == 'high' and before.confidence != 'high':
                    promotions.append(after.lesson_id)
                elif after.confidence in ['low', 'archived'] and before.confidence not in ['low', 'archived']:
                    demotions.append(after.lesson_id)
                break

    if promotions:
        print(f"\n### Promotions ({len(promotions)})")
        for lid in promotions[:10]:
            print(f"- {lid} → high confidence")

    if demotions:
        print(f"\n### Demotions ({len(demotions)})")
        for lid in demotions[:10]:
            print(f"- {lid} → low/archived")

    if not promotions and not demotions:
        print("\nNo confidence level changes.")

    # Summary
    print("\n### Current Distribution")
    by_confidence = {}
    for l in after_rankings:
        conf = l.confidence or 'unknown'
        by_confidence[conf] = by_confidence.get(conf, 0) + 1

    for conf, count in sorted(by_confidence.items()):
        print(f"- {conf}: {count} lessons")

    print("\nRankings recalculated successfully.")

except ImportError as e:
    print(f"Import error: {e}")
    print("\nMake sure the effectiveness engine is properly installed.")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
```

## Output

Shows:
- Before/after statistics
- Lessons promoted to high confidence
- Lessons demoted to low confidence
- Current distribution by confidence level

## Automated Schedule

This runs automatically every Sunday at 4 AM MST via cron:

```yaml
# config/automation_config.yaml
recursive_improvement:
  cron:
    recalculate_rankings: "0 4 * * 0"
```

## See Also

- `/show-effectiveness` - View current rankings
- `/improve` - Run full improvement cycle
- `/show-lessons` - View all lessons
