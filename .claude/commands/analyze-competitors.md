# Analyze YouTube Competitors

Analyze YouTube competitors in a specific category to gather insights for video creation.

## Arguments
- `$ARGUMENTS` - Category to analyze (meditation, hypnosis, sleep, affirmations, binaural_beats, spiritual) or "all" for all categories

## Instructions

Run YouTube competitor analysis for the specified category:

```bash
cd /home/rsalars/Projects/dreamweaving && source venv/bin/activate

# Parse the argument
CATEGORY="$ARGUMENTS"

if [ -z "$CATEGORY" ]; then
    echo "Usage: /analyze-competitors <category>"
    echo "Categories: meditation, hypnosis, sleep, affirmations, binaural_beats, spiritual, all"
    exit 1
fi

if [ "$CATEGORY" = "all" ]; then
    # Analyze all categories
    python3 scripts/ai/youtube_competitor_analyzer.py --categories all

    # Extract insights
    python3 scripts/ai/youtube_insights_extractor.py --full-analysis

    # Sync to Notion (optional)
    # python3 scripts/ai/notion_youtube_sync.py --sync-all
else
    # Analyze specific category
    python3 scripts/ai/youtube_competitor_analyzer.py --category "$CATEGORY"

    # Extract insights
    python3 scripts/ai/youtube_insights_extractor.py --update-patterns
fi

echo ""
echo "=== Analysis Complete ==="
echo "Data saved to: knowledge/youtube_competitor_data/"
echo ""
echo "To view insights:"
echo "  python3 scripts/ai/youtube_insights_extractor.py --view title_patterns"
echo "  python3 scripts/ai/youtube_insights_extractor.py --view tag_clusters"
echo ""
echo "To sync to Notion:"
echo "  python3 scripts/ai/notion_youtube_sync.py --sync-all"
```

## What This Does

1. **Searches YouTube** for top-performing videos in the specified category
2. **Fetches video details** including views, likes, tags, descriptions
3. **Extracts patterns** from successful titles, tags, and engagement metrics
4. **Saves insights** to `knowledge/youtube_competitor_data/` YAML files
5. **Makes data available** for the auto-generate pipeline via RAG

## Output Files

After running, these files will be updated:
- `knowledge/youtube_competitor_data/competitor_channels.yaml` - Top channels
- `knowledge/youtube_competitor_data/top_videos.yaml` - Best performing videos
- `knowledge/youtube_competitor_data/title_patterns.yaml` - High-CTR title structures
- `knowledge/youtube_competitor_data/tag_clusters.yaml` - Tag performance data
- `knowledge/youtube_competitor_data/retention_benchmarks.yaml` - Engagement benchmarks
- `knowledge/youtube_competitor_data/seasonal_trends.yaml` - Monthly interest patterns

## Integration

The auto-generate pipeline (`/auto-generate`) automatically uses this competitor data to:
- Suggest optimized titles based on proven patterns
- Recommend high-performing tags
- Apply seasonal theme adjustments
- Set engagement benchmarks

## First-Time Setup

Before first use, authenticate with YouTube API:
```bash
python3 scripts/ai/youtube_competitor_analyzer.py --category meditation
# Follow OAuth flow in browser
```

## Cron Automation

Weekly analysis runs automatically via cron (Sundays 3 AM).
To manually trigger weekly sync:
```bash
python3 scripts/ai/youtube_competitor_analyzer.py --weekly-sync
```
