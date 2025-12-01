#!/usr/bin/env python3
"""
Feedback Analyzer for Dreamweaving Self-Learning System

Analyzes feedback from multiple sources:
- YouTube analytics (views, retention, engagement)
- Viewer comments (sentiment, themes, suggestions)
- Session performance metrics

Extracts actionable insights for improvement.

Usage:
    python3 scripts/ai/learning/feedback_analyzer.py --analytics analytics.json
    python3 scripts/ai/learning/feedback_analyzer.py --comments comments.txt
    python3 scripts/ai/learning/feedback_analyzer.py --session sessions/{session}
"""

import os
import sys
import yaml
import json
import argparse
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from collections import Counter


# Sentiment indicators for comment analysis
POSITIVE_INDICATORS = [
    'love', 'amazing', 'wonderful', 'beautiful', 'peaceful', 'relaxing',
    'helped', 'best', 'perfect', 'great', 'awesome', 'thank', 'works',
    'calming', 'soothing', 'effective', 'powerful', 'transformative',
    'subscribed', 'favorite', 'recommend', 'masterpiece', 'healing',
]

NEGATIVE_INDICATORS = [
    'boring', 'annoying', 'hate', 'bad', 'worst', 'terrible', 'couldn\'t',
    'too long', 'too short', 'too fast', 'too slow', 'distracting',
    'unsubscribed', 'skip', 'clickbait', 'disappointing', 'waste',
]

SUGGESTION_PATTERNS = [
    r'could you (?:please )?(.+)\?',
    r'would be (?:nice|great|better) (?:if|to) (.+)',
    r'you should (.+)',
    r'please (?:make|do|add|try) (.+)',
    r'i wish (.+)',
    r'suggestion:?\s*(.+)',
    r'request:?\s*(.+)',
]

# Retention thresholds
RETENTION_EXCELLENT = 0.60  # 60%+ average retention
RETENTION_GOOD = 0.45      # 45-60%
RETENTION_AVERAGE = 0.30   # 30-45%
# Below 30% needs improvement


class FeedbackAnalysis:
    """Container for analysis results."""

    def __init__(self, source: str):
        self.source = source
        self.timestamp = datetime.now().isoformat()
        self.metrics: Dict = {}
        self.insights: List[Dict] = []
        self.suggestions: List[str] = []
        self.action_items: List[Dict] = []

    def add_insight(self, category: str, description: str, importance: str = "medium"):
        """Add an insight from analysis."""
        self.insights.append({
            "category": category,
            "description": description,
            "importance": importance,
        })

    def add_action(self, action: str, priority: str = "medium", category: str = "general"):
        """Add an actionable improvement."""
        self.action_items.append({
            "action": action,
            "priority": priority,
            "category": category,
        })

    def to_dict(self) -> Dict:
        return {
            "source": self.source,
            "timestamp": self.timestamp,
            "metrics": self.metrics,
            "insights": self.insights,
            "suggestions": self.suggestions,
            "action_items": self.action_items,
        }


def analyze_youtube_analytics(analytics_data: Dict) -> FeedbackAnalysis:
    """Analyze YouTube analytics data."""
    analysis = FeedbackAnalysis("youtube_analytics")

    # Extract key metrics
    views = analytics_data.get('views', 0)
    watch_time = analytics_data.get('watch_time_minutes', 0)
    avg_view_duration = analytics_data.get('average_view_duration_seconds', 0)
    video_duration = analytics_data.get('video_duration_seconds', 0)
    likes = analytics_data.get('likes', 0)
    dislikes = analytics_data.get('dislikes', 0)
    comments = analytics_data.get('comments', 0)
    subscribers_gained = analytics_data.get('subscribers_gained', 0)
    retention_data = analytics_data.get('retention', {})

    analysis.metrics = {
        "views": views,
        "watch_time_minutes": watch_time,
        "avg_view_duration_seconds": avg_view_duration,
        "engagement_rate": calculate_engagement_rate(views, likes, comments),
    }

    # Retention analysis
    if video_duration > 0 and avg_view_duration > 0:
        avg_retention = avg_view_duration / video_duration
        analysis.metrics["average_retention"] = round(avg_retention, 3)

        if avg_retention >= RETENTION_EXCELLENT:
            analysis.add_insight(
                "retention",
                f"Excellent retention ({avg_retention:.0%}). Content is highly engaging.",
                "high"
            )
        elif avg_retention >= RETENTION_GOOD:
            analysis.add_insight(
                "retention",
                f"Good retention ({avg_retention:.0%}). Minor improvements possible.",
                "medium"
            )
        elif avg_retention >= RETENTION_AVERAGE:
            analysis.add_insight(
                "retention",
                f"Average retention ({avg_retention:.0%}). Consider pacing adjustments.",
                "high"
            )
            analysis.add_action(
                "Review script pacing - consider more engaging opening",
                priority="high",
                category="script"
            )
        else:
            analysis.add_insight(
                "retention",
                f"Low retention ({avg_retention:.0%}). Significant improvements needed.",
                "critical"
            )
            analysis.add_action(
                "Analyze drop-off points and revise content structure",
                priority="critical",
                category="script"
            )

    # Analyze retention curve if available
    if retention_data:
        drop_points = find_retention_drops(retention_data)
        for point in drop_points:
            analysis.add_insight(
                "retention_drop",
                f"Significant drop at {point['time']}s ({point['drop']:.0%} loss)",
                "high"
            )
            analysis.add_action(
                f"Review content around {point['time']}s timestamp",
                priority="high",
                category="script"
            )

    # Engagement analysis
    if views > 0:
        like_ratio = likes / views if views > 0 else 0
        comment_ratio = comments / views if views > 0 else 0

        if like_ratio > 0.05:
            analysis.add_insight("engagement", "High like ratio - content resonates well", "medium")
        elif like_ratio < 0.02:
            analysis.add_insight("engagement", "Low like ratio - consider stronger CTAs", "medium")
            analysis.add_action(
                "Add or improve call-to-action for engagement",
                priority="medium",
                category="video"
            )

        if comment_ratio > 0.01:
            analysis.add_insight("engagement", "Good comment rate - community building", "medium")

    # Subscriber conversion
    if views > 100 and subscribers_gained > 0:
        sub_rate = subscribers_gained / views
        analysis.metrics["subscriber_conversion"] = round(sub_rate, 4)
        if sub_rate > 0.02:
            analysis.add_insight("growth", "Strong subscriber conversion", "medium")
        elif sub_rate < 0.005:
            analysis.add_action(
                "Improve subscriber call-to-action",
                priority="medium",
                category="video"
            )

    return analysis


def find_retention_drops(retention_data: Dict) -> List[Dict]:
    """Find significant drops in retention curve."""
    drops = []

    if isinstance(retention_data, dict):
        times = sorted(retention_data.keys(), key=lambda x: int(x))
        prev_retention = 1.0

        for time in times:
            current = retention_data[time]
            drop = prev_retention - current

            if drop > 0.10:  # More than 10% drop
                drops.append({
                    "time": int(time),
                    "drop": drop,
                    "retention_after": current,
                })
            prev_retention = current

    return drops


def calculate_engagement_rate(views: int, likes: int, comments: int) -> float:
    """Calculate engagement rate."""
    if views == 0:
        return 0
    return round((likes + comments * 3) / views, 4)  # Comments weighted higher


def analyze_comments(comments_text: str) -> FeedbackAnalysis:
    """Analyze viewer comments for sentiment and suggestions."""
    analysis = FeedbackAnalysis("viewer_comments")

    # Split into individual comments
    comments = [c.strip() for c in comments_text.split('\n') if c.strip()]
    analysis.metrics["total_comments"] = len(comments)

    if not comments:
        return analysis

    # Sentiment analysis
    positive_count = 0
    negative_count = 0
    neutral_count = 0

    positive_comments = []
    negative_comments = []
    suggestions = []

    for comment in comments:
        comment_lower = comment.lower()

        # Check sentiment
        pos_score = sum(1 for word in POSITIVE_INDICATORS if word in comment_lower)
        neg_score = sum(1 for word in NEGATIVE_INDICATORS if word in comment_lower)

        if pos_score > neg_score:
            positive_count += 1
            positive_comments.append(comment)
        elif neg_score > pos_score:
            negative_count += 1
            negative_comments.append(comment)
        else:
            neutral_count += 1

        # Extract suggestions
        for pattern in SUGGESTION_PATTERNS:
            matches = re.findall(pattern, comment_lower, re.IGNORECASE)
            suggestions.extend(matches)

    # Calculate sentiment
    total = len(comments)
    analysis.metrics.update({
        "positive_ratio": round(positive_count / total, 2),
        "negative_ratio": round(negative_count / total, 2),
        "neutral_ratio": round(neutral_count / total, 2),
    })

    # Sentiment insights
    pos_ratio = positive_count / total
    if pos_ratio > 0.8:
        analysis.add_insight("sentiment", "Overwhelmingly positive reception", "high")
    elif pos_ratio > 0.6:
        analysis.add_insight("sentiment", "Generally positive reception", "medium")
    elif pos_ratio < 0.4:
        analysis.add_insight("sentiment", "Mixed or negative reception - review needed", "critical")
        analysis.add_action(
            "Analyze negative comments for specific issues",
            priority="high",
            category="content"
        )

    # Extract themes from negative comments
    if negative_comments:
        themes = extract_themes(negative_comments)
        for theme, count in themes.most_common(3):
            analysis.add_insight(
                "negative_theme",
                f"Recurring issue: '{theme}' mentioned {count} times",
                "high"
            )

    # Process suggestions
    analysis.suggestions = list(set(suggestions))[:10]  # Top 10 unique
    if suggestions:
        analysis.add_insight(
            "viewer_suggestions",
            f"{len(set(suggestions))} unique suggestions from viewers",
            "medium"
        )

    # Specific feedback patterns
    specific_feedback = extract_specific_feedback(comments)
    for fb in specific_feedback:
        analysis.add_action(
            f"Consider: {fb}",
            priority="medium",
            category="improvement"
        )

    return analysis


def extract_themes(comments: List[str]) -> Counter:
    """Extract common themes from comments."""
    themes = Counter()

    # Look for common complaint patterns
    complaint_patterns = {
        'pacing': ['too fast', 'too slow', 'rushed', 'dragged'],
        'audio': ['audio', 'sound', 'volume', 'quiet', 'loud', 'music'],
        'voice': ['voice', 'narrator', 'speaking', 'accent'],
        'length': ['long', 'short', 'duration'],
        'content': ['boring', 'repetitive', 'confusing', 'distracting'],
    }

    for comment in comments:
        comment_lower = comment.lower()
        for theme, keywords in complaint_patterns.items():
            if any(kw in comment_lower for kw in keywords):
                themes[theme] += 1

    return themes


def extract_specific_feedback(comments: List[str]) -> List[str]:
    """Extract specific actionable feedback."""
    feedback = []

    for comment in comments:
        comment_lower = comment.lower()

        # Duration feedback
        if 'too long' in comment_lower:
            feedback.append("Some viewers find duration too long")
        elif 'too short' in comment_lower:
            feedback.append("Some viewers want longer content")

        # Pacing feedback
        if 'too fast' in comment_lower:
            feedback.append("Consider slower pacing")
        elif 'too slow' in comment_lower:
            feedback.append("Consider faster pacing")

        # Audio feedback
        if any(x in comment_lower for x in ['binaural', 'beats', 'frequencies']):
            if any(x in comment_lower for x in ['love', 'great', 'perfect']):
                feedback.append("Binaural beats well-received")
            elif any(x in comment_lower for x in ['annoying', 'loud', 'distracting']):
                feedback.append("Adjust binaural beat intensity")

    return list(set(feedback))


def analyze_session_performance(session_path: Path) -> FeedbackAnalysis:
    """Analyze session files for improvement opportunities."""
    analysis = FeedbackAnalysis("session_review")

    # Check if quality report exists
    quality_report_path = session_path / 'working_files' / 'quality_report.json'
    if quality_report_path.exists():
        with open(quality_report_path, 'r') as f:
            quality_data = json.load(f)
            analysis.metrics["quality_score"] = quality_data.get('overall_score', 0)

            # Extract issues from quality report
            for component, data in quality_data.get('components', {}).items():
                for issue in data.get('issues', []):
                    analysis.add_action(
                        issue['description'],
                        priority="medium",
                        category=component
                    )

    # Analyze session manifest for patterns
    manifest_path = session_path / 'manifest.yaml'
    if manifest_path.exists():
        with open(manifest_path, 'r') as f:
            manifest = yaml.safe_load(f)

        # Check configuration patterns
        voice_config = manifest.get('voice', {})
        speaking_rate = voice_config.get('speaking_rate', 1.0)
        if speaking_rate < 0.8:
            analysis.add_insight("config", "Using slow speaking rate - good for relaxation", "low")
        elif speaking_rate > 1.1:
            analysis.add_insight("config", "Speaking rate may be too fast for hypnotic content", "medium")

    return analysis


def save_analysis(analysis: FeedbackAnalysis, output_path: Path):
    """Save analysis results."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = analysis.to_dict()

    with open(output_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    return output_path


def update_lessons_learned(analysis: FeedbackAnalysis, knowledge_path: Path):
    """Update the lessons learned knowledge base."""
    lessons_path = knowledge_path / 'lessons_learned.yaml'

    if lessons_path.exists():
        with open(lessons_path, 'r') as f:
            lessons = yaml.safe_load(f) or {}
    else:
        lessons = {"analytics_insights": [], "viewer_feedback": [], "code_improvements": []}

    # Add new insights
    for insight in analysis.insights:
        if insight['importance'] in ['high', 'critical']:
            lesson = {
                "date": analysis.timestamp[:10],
                "source": analysis.source,
                "insight": insight['description'],
                "category": insight['category'],
            }

            if analysis.source == 'youtube_analytics':
                lessons.setdefault('analytics_insights', []).append(lesson)
            elif analysis.source == 'viewer_comments':
                lessons.setdefault('viewer_feedback', []).append(lesson)

    # Keep only recent entries (last 50 per category)
    for key in lessons:
        if isinstance(lessons[key], list):
            lessons[key] = lessons[key][-50:]

    lessons_path.parent.mkdir(parents=True, exist_ok=True)
    with open(lessons_path, 'w') as f:
        yaml.dump(lessons, f, default_flow_style=False, sort_keys=False, allow_unicode=True)


def main():
    parser = argparse.ArgumentParser(description='Analyze feedback for learning')
    parser.add_argument('--analytics', help='Path to YouTube analytics JSON')
    parser.add_argument('--comments', help='Path to comments text file')
    parser.add_argument('--session', help='Path to session directory')
    parser.add_argument('--output', help='Output path for analysis')
    parser.add_argument('--update-knowledge', action='store_true',
                       help='Update knowledge base with insights')
    args = parser.parse_args()

    analyses = []

    # Process analytics
    if args.analytics:
        with open(args.analytics, 'r') as f:
            analytics_data = json.load(f)
        analysis = analyze_youtube_analytics(analytics_data)
        analyses.append(analysis)
        print(f"Analyzed YouTube analytics: {len(analysis.insights)} insights, {len(analysis.action_items)} actions")

    # Process comments
    if args.comments:
        with open(args.comments, 'r') as f:
            comments_text = f.read()
        analysis = analyze_comments(comments_text)
        analyses.append(analysis)
        print(f"Analyzed {analysis.metrics.get('total_comments', 0)} comments")
        print(f"  Sentiment: {analysis.metrics.get('positive_ratio', 0):.0%} positive")
        if analysis.suggestions:
            print(f"  Found {len(analysis.suggestions)} viewer suggestions")

    # Process session
    if args.session:
        session_path = Path(args.session)
        analysis = analyze_session_performance(session_path)
        analyses.append(analysis)
        print(f"Analyzed session: {len(analysis.action_items)} improvement opportunities")

    # Save results
    if analyses:
        # Combine analyses
        combined = {
            "timestamp": datetime.now().isoformat(),
            "analyses": [a.to_dict() for a in analyses],
            "summary": {
                "total_insights": sum(len(a.insights) for a in analyses),
                "total_actions": sum(len(a.action_items) for a in analyses),
                "total_suggestions": sum(len(a.suggestions) for a in analyses),
            }
        }

        # Determine output path
        if args.output:
            output_path = Path(args.output)
        elif args.session:
            output_path = Path(args.session) / 'working_files' / 'feedback_analysis.yaml'
        else:
            output_path = Path('knowledge') / 'feedback_analysis.yaml'

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            yaml.dump(combined, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        print(f"\nSaved analysis to: {output_path}")

        # Update knowledge base
        if args.update_knowledge:
            knowledge_path = Path('knowledge')
            for analysis in analyses:
                update_lessons_learned(analysis, knowledge_path)
            print(f"Updated knowledge base at: {knowledge_path}/lessons_learned.yaml")

        # Print action items
        print("\n--- ACTION ITEMS ---")
        for analysis in analyses:
            if analysis.action_items:
                print(f"\nFrom {analysis.source}:")
                for action in analysis.action_items:
                    priority_marker = "!!!" if action['priority'] == 'critical' else ("!!" if action['priority'] == 'high' else "!")
                    print(f"  {priority_marker} [{action['category']}] {action['action']}")


if __name__ == "__main__":
    main()
