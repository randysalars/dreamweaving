#!/usr/bin/env python3
"""
YouTube Insights Extractor for Dreamweaving

Extracts patterns and insights from collected YouTube competitor data:
- Title patterns with CTR estimates
- Tag clustering by performance
- Retention benchmarks by duration/category
- Seasonal trend detection
- Thumbnail design patterns
- Success factor identification

Usage:
    # Update patterns from raw data
    python3 scripts/ai/youtube_insights_extractor.py --update-patterns

    # Full analysis with Notion sync
    python3 scripts/ai/youtube_insights_extractor.py --full-analysis --sync-notion

    # View insights for a category
    python3 scripts/ai/youtube_insights_extractor.py --view meditation

Author: Dreamweaving AI System
"""

import os
import re
import sys
import json
import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from collections import Counter, defaultdict
import math

import yaml

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "youtube_config.yaml"
DATA_PATH = PROJECT_ROOT / "knowledge" / "youtube_competitor_data"
RAW_PATH = DATA_PATH / "raw"

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class YouTubeInsightsExtractor:
    """
    Extracts patterns and insights from YouTube competitor data.
    """

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the extractor."""
        self.config_path = config_path or CONFIG_PATH
        self.config = self._load_config()
        self.raw_data = {}
        self.insights = {
            'title_patterns': [],
            'tag_clusters': {},
            'retention_benchmarks': {},
            'seasonal_trends': {},
            'competitor_channels': [],
            'top_videos': []
        }

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        return {}

    def load_raw_data(self) -> Dict[str, Any]:
        """Load all raw data from YAML files."""
        self.raw_data = {}

        if not RAW_PATH.exists():
            logger.warning(f"Raw data path does not exist: {RAW_PATH}")
            return {}

        for yaml_file in RAW_PATH.glob("*.yaml"):
            category = yaml_file.stem.replace('_raw', '')
            try:
                with open(yaml_file, 'r') as f:
                    self.raw_data[category] = yaml.safe_load(f)
                logger.info(f"Loaded raw data for: {category}")
            except Exception as e:
                logger.error(f"Error loading {yaml_file}: {e}")

        return self.raw_data

    def extract_title_patterns(self) -> List[Dict[str, Any]]:
        """
        Extract successful title patterns from video data.

        Identifies patterns like:
        - "[DURATION] [BENEFIT] | [FREQUENCY]"
        - "THE [ADJECTIVE] [OUTCOME] | [MODIFIER]"
        - etc.
        """
        logger.info("Extracting title patterns...")

        all_videos = []
        for category, data in self.raw_data.items():
            if isinstance(data, dict) and 'videos' in data:
                for video in data['videos']:
                    video['category'] = category
                    all_videos.append(video)

        if not all_videos:
            logger.warning("No videos found in raw data")
            return []

        # Define pattern templates to look for
        pattern_templates = [
            {
                'name': 'duration_benefit_frequency',
                'pattern': r'^\d+[\s-]*(minute|min|hour|hr).*?(meditation|sleep|healing|relaxation).*?(\d+\s*hz|theta|delta|alpha|gamma|binaural)',
                'template': '[DURATION] [BENEFIT] | [FREQUENCY]',
                'flags': re.IGNORECASE
            },
            {
                'name': 'superlative_outcome',
                'pattern': r'^(the\s+)?(most|deepest|powerful|ultimate|best|strongest)',
                'template': 'THE [SUPERLATIVE] [OUTCOME]',
                'flags': re.IGNORECASE
            },
            {
                'name': 'benefit_frequency',
                'pattern': r'(sleep|healing|meditation|relaxation|anxiety|stress).*?(\d+\s*hz|theta|delta|alpha|binaural)',
                'template': '[BENEFIT] [FREQUENCY]',
                'flags': re.IGNORECASE
            },
            {
                'name': 'duration_prefix',
                'pattern': r'^\[?\d+[\s-]*(minute|min|hour|hr)s?\]?',
                'template': '[DURATION] ...',
                'flags': re.IGNORECASE
            },
            {
                'name': 'frequency_prefix',
                'pattern': r'^(\d+\s*hz|theta|delta|alpha|gamma|binaural)',
                'template': '[FREQUENCY] ...',
                'flags': re.IGNORECASE
            },
            {
                'name': 'pipe_separator',
                'pattern': r'\|',
                'template': '[PART 1] | [PART 2]',
                'flags': 0
            },
            {
                'name': 'benefit_for_outcome',
                'pattern': r'(meditation|hypnosis|music|sleep)\s+(for|to)\s+',
                'template': '[TYPE] for [OUTCOME]',
                'flags': re.IGNORECASE
            }
        ]

        # Analyze each pattern
        pattern_results = []

        for template in pattern_templates:
            matching_videos = []
            regex = re.compile(template['pattern'], template['flags'])

            for video in all_videos:
                title = video.get('title', '')
                if regex.search(title):
                    matching_videos.append(video)

            if len(matching_videos) >= 5:  # Minimum occurrences
                # Calculate average performance
                total_views = sum(v.get('view_count', 0) for v in matching_videos)
                total_likes = sum(v.get('like_count', 0) for v in matching_videos)
                avg_views = total_views / len(matching_videos)
                avg_likes = total_likes / len(matching_videos)
                engagement_rate = total_likes / total_views if total_views else 0

                # Estimate CTR based on engagement rate
                # Higher engagement often correlates with better CTR
                estimated_ctr = min(engagement_rate * 100, 10)  # Cap at 10%

                # Get example titles
                examples = sorted(matching_videos, key=lambda x: x.get('view_count', 0), reverse=True)[:5]

                pattern_results.append({
                    'name': template['name'],
                    'template': template['template'],
                    'video_count': len(matching_videos),
                    'avg_views': int(avg_views),
                    'avg_likes': int(avg_likes),
                    'engagement_rate': round(engagement_rate, 4),
                    'estimated_ctr': round(estimated_ctr, 2),
                    'categories': list(set(v.get('category', 'unknown') for v in matching_videos)),
                    'examples': [
                        {
                            'title': v['title'],
                            'views': v.get('view_count', 0),
                            'channel': v.get('channel_title', '')
                        }
                        for v in examples
                    ]
                })

        # Sort by estimated CTR
        pattern_results.sort(key=lambda x: x['estimated_ctr'], reverse=True)

        self.insights['title_patterns'] = pattern_results
        logger.info(f"Extracted {len(pattern_results)} title patterns")

        return pattern_results

    def extract_tag_clusters(self) -> Dict[str, Any]:
        """
        Cluster tags by performance and category.
        """
        logger.info("Extracting tag clusters...")

        # Collect all tags with their performance metrics
        tag_stats = defaultdict(lambda: {
            'count': 0,
            'total_views': 0,
            'total_likes': 0,
            'categories': set(),
            'videos': []
        })

        for category, data in self.raw_data.items():
            if isinstance(data, dict) and 'videos' in data:
                for video in data['videos']:
                    tags = video.get('tags', [])
                    views = video.get('view_count', 0)
                    likes = video.get('like_count', 0)

                    for tag in tags:
                        tag_lower = tag.lower().strip()
                        if len(tag_lower) > 2:  # Skip very short tags
                            tag_stats[tag_lower]['count'] += 1
                            tag_stats[tag_lower]['total_views'] += views
                            tag_stats[tag_lower]['total_likes'] += likes
                            tag_stats[tag_lower]['categories'].add(category)
                            tag_stats[tag_lower]['videos'].append({
                                'title': video.get('title', ''),
                                'views': views
                            })

        # Process tag statistics
        tag_clusters = {
            'high_volume': [],
            'high_performance': [],
            'by_category': defaultdict(list)
        }

        for tag, stats in tag_stats.items():
            if stats['count'] >= 5:  # Minimum occurrences
                avg_views = stats['total_views'] / stats['count']
                avg_likes = stats['total_likes'] / stats['count']
                engagement = avg_likes / avg_views if avg_views else 0

                tag_data = {
                    'tag': tag,
                    'count': stats['count'],
                    'avg_views': int(avg_views),
                    'avg_likes': int(avg_likes),
                    'engagement_rate': round(engagement, 4),
                    'categories': list(stats['categories']),
                    'volume': 'high' if stats['count'] >= 20 else 'medium' if stats['count'] >= 10 else 'low',
                    'competition': 'high' if avg_views > 100000 else 'medium' if avg_views > 10000 else 'low'
                }

                # Categorize
                if stats['count'] >= 20:
                    tag_clusters['high_volume'].append(tag_data)

                if engagement > 0.04:  # >4% engagement
                    tag_clusters['high_performance'].append(tag_data)

                for cat in stats['categories']:
                    tag_clusters['by_category'][cat].append(tag_data)

        # Sort clusters
        tag_clusters['high_volume'].sort(key=lambda x: x['count'], reverse=True)
        tag_clusters['high_performance'].sort(key=lambda x: x['engagement_rate'], reverse=True)

        for cat in tag_clusters['by_category']:
            tag_clusters['by_category'][cat].sort(key=lambda x: x['avg_views'], reverse=True)
            tag_clusters['by_category'][cat] = tag_clusters['by_category'][cat][:20]  # Top 20 per category

        # Convert defaultdict to regular dict
        tag_clusters['by_category'] = dict(tag_clusters['by_category'])

        self.insights['tag_clusters'] = tag_clusters
        logger.info(f"Extracted {len(tag_clusters['high_volume'])} high-volume tags")

        return tag_clusters

    def extract_retention_benchmarks(self) -> Dict[str, Any]:
        """
        Extract retention benchmarks by duration and category.

        Note: We estimate retention from engagement metrics since
        actual retention data requires YouTube Analytics API access.
        """
        logger.info("Extracting retention benchmarks...")

        # Group videos by duration ranges
        duration_ranges = {
            '5-10min': (5, 10),
            '10-20min': (10, 20),
            '20-30min': (20, 30),
            '30-60min': (30, 60),
            '60min+': (60, 999)
        }

        benchmarks = {}

        for category, data in self.raw_data.items():
            if not isinstance(data, dict) or 'videos' not in data:
                continue

            category_benchmarks = {}

            for range_name, (min_dur, max_dur) in duration_ranges.items():
                matching_videos = []

                for video in data['videos']:
                    duration_str = video.get('duration', '')
                    minutes = self._parse_duration(duration_str)

                    if min_dur <= minutes < max_dur:
                        views = video.get('view_count', 0)
                        likes = video.get('like_count', 0)
                        comments = video.get('comment_count', 0)

                        # Estimate retention from engagement
                        # Higher engagement often indicates better retention
                        engagement = (likes + comments * 2) / views if views else 0

                        matching_videos.append({
                            'title': video.get('title', ''),
                            'duration_minutes': minutes,
                            'views': views,
                            'engagement': engagement
                        })

                if len(matching_videos) >= 3:
                    avg_engagement = sum(v['engagement'] for v in matching_videos) / len(matching_videos)

                    # Estimate average retention from engagement
                    # This is a rough estimate: engagement of 5% ≈ 50% retention
                    estimated_retention = min(avg_engagement * 10, 0.8)  # Cap at 80%

                    category_benchmarks[range_name] = {
                        'video_count': len(matching_videos),
                        'avg_engagement': round(avg_engagement, 4),
                        'estimated_retention': round(estimated_retention, 2),
                        'drop_points': self._estimate_drop_points(minutes, estimated_retention),
                        'top_performers': sorted(
                            matching_videos,
                            key=lambda x: x['engagement'],
                            reverse=True
                        )[:3]
                    }

            if category_benchmarks:
                benchmarks[category] = category_benchmarks

        self.insights['retention_benchmarks'] = benchmarks
        logger.info(f"Extracted retention benchmarks for {len(benchmarks)} categories")

        return benchmarks

    def _parse_duration(self, duration_str: str) -> int:
        """Parse ISO 8601 duration to minutes."""
        if not duration_str:
            return 0

        # Handle ISO 8601 format (PT1H30M45S)
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
        if match:
            hours = int(match.group(1) or 0)
            minutes = int(match.group(2) or 0)
            seconds = int(match.group(3) or 0)
            return hours * 60 + minutes + (1 if seconds > 30 else 0)

        return 0

    def _estimate_drop_points(self, duration_minutes: int, avg_retention: float) -> List[Dict]:
        """Estimate typical drop-off points based on duration and retention."""
        drop_points = []

        # Common drop-off patterns for meditation/hypnosis content
        if duration_minutes >= 5:
            drop_points.append({
                'time': '0:30-1:00',
                'description': 'Initial hook period',
                'estimated_drop': round((1 - avg_retention) * 0.3, 2),
                'recommendation': 'Strengthen opening hook, avoid slow starts'
            })

        if duration_minutes >= 10:
            drop_points.append({
                'time': f'{min(5, duration_minutes // 3)}:00',
                'description': 'Induction phase',
                'estimated_drop': round((1 - avg_retention) * 0.2, 2),
                'recommendation': 'Add engagement cue or binaural shift'
            })

        if duration_minutes >= 20:
            drop_points.append({
                'time': f'{duration_minutes // 2}:00',
                'description': 'Mid-journey',
                'estimated_drop': round((1 - avg_retention) * 0.15, 2),
                'recommendation': 'Pattern interrupt or scene change'
            })

        if duration_minutes >= 30:
            drop_points.append({
                'time': f'{int(duration_minutes * 0.75)}:00',
                'description': 'Pre-integration',
                'estimated_drop': round((1 - avg_retention) * 0.1, 2),
                'recommendation': 'Re-engagement cue before closing'
            })

        return drop_points

    def extract_seasonal_trends(self) -> Dict[str, Any]:
        """
        Extract seasonal trends from publish dates and view patterns.
        """
        logger.info("Extracting seasonal trends...")

        # Collect videos by month
        monthly_data = defaultdict(lambda: {
            'videos': [],
            'total_views': 0,
            'themes': Counter()
        })

        theme_keywords = {
            'new_year': ['new year', 'resolution', 'fresh start', 'beginning'],
            'confidence': ['confidence', 'self-esteem', 'courage', 'brave'],
            'anxiety': ['anxiety', 'stress', 'worry', 'calm'],
            'sleep': ['sleep', 'insomnia', 'rest', 'deep sleep'],
            'healing': ['healing', 'heal', 'recovery', 'restore'],
            'abundance': ['abundance', 'prosperity', 'wealth', 'manifest'],
            'relaxation': ['relax', 'peace', 'calm', 'tranquil'],
            'focus': ['focus', 'concentration', 'study', 'work'],
            'spiritual': ['spiritual', 'awakening', 'enlighten', 'soul'],
            'holiday': ['christmas', 'holiday', 'thanksgiving', 'easter']
        }

        for category, data in self.raw_data.items():
            if not isinstance(data, dict) or 'videos' not in data:
                continue

            for video in data['videos']:
                pub_date = video.get('published_at', '')
                if not pub_date:
                    continue

                try:
                    date = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                    month = date.month
                    month_name = date.strftime('%B').lower()

                    monthly_data[month]['videos'].append(video)
                    monthly_data[month]['total_views'] += video.get('view_count', 0)

                    # Detect themes in title
                    title_lower = video.get('title', '').lower()
                    for theme, keywords in theme_keywords.items():
                        if any(kw in title_lower for kw in keywords):
                            monthly_data[month]['themes'][theme] += 1

                except Exception as e:
                    logger.debug(f"Error parsing date: {e}")

        # Calculate trends
        seasonal_trends = {}
        total_avg_views = sum(
            d['total_views'] / len(d['videos'])
            for d in monthly_data.values()
            if d['videos']
        ) / len(monthly_data) if monthly_data else 0

        month_names = [
            'january', 'february', 'march', 'april', 'may', 'june',
            'july', 'august', 'september', 'october', 'november', 'december'
        ]

        for month_num in range(1, 13):
            month_name = month_names[month_num - 1]
            data = monthly_data[month_num]

            if not data['videos']:
                continue

            avg_views = data['total_views'] / len(data['videos'])
            view_lift = ((avg_views - total_avg_views) / total_avg_views) if total_avg_views else 0

            # Get top themes for this month
            top_themes = dict(data['themes'].most_common(5))

            seasonal_trends[month_name] = {
                'video_count': len(data['videos']),
                'avg_views': int(avg_views),
                'view_lift': round(view_lift, 2),
                'trending_themes': top_themes,
                'recommended_topics': self._get_month_recommendations(month_num, top_themes)
            }

        self.insights['seasonal_trends'] = seasonal_trends
        logger.info(f"Extracted seasonal trends for {len(seasonal_trends)} months")

        return seasonal_trends

    def _get_month_recommendations(self, month: int, themes: Dict) -> List[str]:
        """Get topic recommendations based on month and trending themes."""
        base_recommendations = {
            1: ['new year goals', 'fresh start meditation', 'motivation boost'],
            2: ['self-love', 'heart healing', 'relationship harmony'],
            3: ['spring renewal', 'energy cleanse', 'new beginnings'],
            4: ['stress relief', 'spring awakening', 'growth meditation'],
            5: ['abundance mindset', 'gratitude practice', 'nature connection'],
            6: ['summer energy', 'vitality boost', 'adventure spirit'],
            7: ['deep relaxation', 'vacation calm', 'heat relief'],
            8: ['back-to-routine', 'focus boost', 'productivity'],
            9: ['focus and clarity', 'study help', 'autumn grounding'],
            10: ['shadow work', 'inner transformation', 'harvest gratitude'],
            11: ['gratitude meditation', 'family harmony', 'abundance'],
            12: ['holiday stress relief', 'year-end reflection', 'peace and joy']
        }

        recommendations = base_recommendations.get(month, ['relaxation', 'healing', 'peace'])

        # Add theme-specific recommendations
        for theme in list(themes.keys())[:2]:
            if theme not in str(recommendations):
                recommendations.append(f'{theme} focus')

        return recommendations[:5]

    def extract_competitor_insights(self) -> List[Dict[str, Any]]:
        """
        Extract insights about top competitor channels.
        """
        logger.info("Extracting competitor insights...")

        all_channels = []

        for category, data in self.raw_data.items():
            if isinstance(data, dict) and 'channels' in data:
                for channel in data['channels']:
                    channel['primary_category'] = category
                    all_channels.append(channel)

        # Deduplicate by channel_id
        seen_ids = set()
        unique_channels = []
        for channel in all_channels:
            cid = channel.get('channel_id', '')
            if cid and cid not in seen_ids:
                seen_ids.add(cid)
                unique_channels.append(channel)

        # Sort by subscriber count
        unique_channels.sort(key=lambda x: x.get('subscriber_count', 0), reverse=True)

        # Calculate metrics
        for channel in unique_channels:
            subs = channel.get('subscriber_count', 0)
            views = channel.get('view_count', 0)
            videos = channel.get('video_count', 0)

            if videos > 0:
                channel['avg_views_per_video'] = views // videos

            if subs > 0:
                # Estimate monthly growth (very rough)
                channel['estimated_monthly_growth'] = 'Unknown'

        self.insights['competitor_channels'] = unique_channels[:50]  # Top 50
        logger.info(f"Extracted insights for {len(unique_channels)} competitor channels")

        return unique_channels

    def extract_top_videos(self) -> List[Dict[str, Any]]:
        """
        Extract top performing videos across all categories.
        """
        logger.info("Extracting top videos...")

        all_videos = []

        for category, data in self.raw_data.items():
            if isinstance(data, dict) and 'videos' in data:
                for video in data['videos']:
                    video['category'] = category
                    all_videos.append(video)

        # Sort by views
        all_videos.sort(key=lambda x: x.get('view_count', 0), reverse=True)

        # Add analysis for top videos
        for video in all_videos[:100]:
            views = video.get('view_count', 0)
            likes = video.get('like_count', 0)
            comments = video.get('comment_count', 0)

            video['engagement_rate'] = round((likes + comments) / views, 4) if views else 0
            video['like_rate'] = round(likes / views, 4) if views else 0
            video['comment_rate'] = round(comments / views, 6) if views else 0

            # Analyze why it might be successful
            video['success_factors'] = self._analyze_success_factors(video)

        self.insights['top_videos'] = all_videos[:100]
        logger.info(f"Extracted top {min(100, len(all_videos))} videos")

        return all_videos[:100]

    def _analyze_success_factors(self, video: Dict) -> List[str]:
        """Analyze potential success factors for a video."""
        factors = []
        title = video.get('title', '').lower()

        # Title analysis
        if any(word in title for word in ['deepest', 'most powerful', 'ultimate']):
            factors.append('Superlative title language')

        if re.search(r'\d+\s*(min|hour|hz)', title):
            factors.append('Specific duration/frequency in title')

        if '|' in title:
            factors.append('Pipe separator structure')

        # Duration analysis
        duration = self._parse_duration(video.get('duration', ''))
        if 20 <= duration <= 30:
            factors.append('Optimal duration (20-30 min)')
        elif duration >= 60:
            factors.append('Long-form content (60+ min)')

        # Engagement analysis
        engagement = video.get('engagement_rate', 0)
        if engagement > 0.05:
            factors.append('High engagement rate (>5%)')

        # Tags analysis
        tags = video.get('tags', [])
        if len(tags) >= 20:
            factors.append('Comprehensive tag usage')

        return factors if factors else ['Standard content']

    def save_insights(self):
        """Save all extracted insights to YAML files."""
        logger.info("Saving insights to YAML files...")

        # Title patterns
        if self.insights['title_patterns']:
            output = DATA_PATH / "title_patterns.yaml"
            with open(output, 'w') as f:
                yaml.dump({
                    'extracted_at': datetime.now().isoformat(),
                    'patterns': self.insights['title_patterns']
                }, f, default_flow_style=False, allow_unicode=True)
            logger.info(f"Saved title patterns to {output}")

        # Tag clusters
        if self.insights['tag_clusters']:
            output = DATA_PATH / "tag_clusters.yaml"
            with open(output, 'w') as f:
                yaml.dump({
                    'extracted_at': datetime.now().isoformat(),
                    'clusters': self.insights['tag_clusters']
                }, f, default_flow_style=False, allow_unicode=True)
            logger.info(f"Saved tag clusters to {output}")

        # Retention benchmarks
        if self.insights['retention_benchmarks']:
            output = DATA_PATH / "retention_benchmarks.yaml"
            with open(output, 'w') as f:
                yaml.dump({
                    'extracted_at': datetime.now().isoformat(),
                    'benchmarks': self.insights['retention_benchmarks']
                }, f, default_flow_style=False, allow_unicode=True)
            logger.info(f"Saved retention benchmarks to {output}")

        # Seasonal trends
        if self.insights['seasonal_trends']:
            output = DATA_PATH / "seasonal_trends.yaml"
            with open(output, 'w') as f:
                yaml.dump({
                    'extracted_at': datetime.now().isoformat(),
                    'trends': self.insights['seasonal_trends']
                }, f, default_flow_style=False, allow_unicode=True)
            logger.info(f"Saved seasonal trends to {output}")

        # Competitor channels
        if self.insights['competitor_channels']:
            output = DATA_PATH / "competitor_channels.yaml"
            with open(output, 'w') as f:
                yaml.dump({
                    'extracted_at': datetime.now().isoformat(),
                    'channels': self.insights['competitor_channels']
                }, f, default_flow_style=False, allow_unicode=True)
            logger.info(f"Saved competitor channels to {output}")

        # Top videos
        if self.insights['top_videos']:
            output = DATA_PATH / "top_videos.yaml"
            with open(output, 'w') as f:
                yaml.dump({
                    'extracted_at': datetime.now().isoformat(),
                    'videos': self.insights['top_videos']
                }, f, default_flow_style=False, allow_unicode=True)
            logger.info(f"Saved top videos to {output}")

        logger.info("All insights saved successfully")

    def full_analysis(self, sync_notion: bool = False):
        """Run full analysis pipeline."""
        logger.info("Running full analysis pipeline...")

        # Load raw data
        self.load_raw_data()

        if not self.raw_data:
            logger.error("No raw data available. Run youtube_competitor_analyzer.py first.")
            return

        # Extract all insights
        self.extract_title_patterns()
        self.extract_tag_clusters()
        self.extract_retention_benchmarks()
        self.extract_seasonal_trends()
        self.extract_competitor_insights()
        self.extract_top_videos()

        # Save to YAML
        self.save_insights()

        # Sync to Notion if requested
        if sync_notion:
            logger.info("Notion sync requested - will be implemented in notion_youtube_sync.py")
            # TODO: Implement Notion sync

        logger.info("Full analysis complete")

    def get_insights_summary(self) -> Dict[str, Any]:
        """Get a summary of all insights."""
        return {
            'title_patterns_count': len(self.insights.get('title_patterns', [])),
            'high_volume_tags': len(self.insights.get('tag_clusters', {}).get('high_volume', [])),
            'categories_with_benchmarks': len(self.insights.get('retention_benchmarks', {})),
            'months_with_trends': len(self.insights.get('seasonal_trends', {})),
            'competitor_channels': len(self.insights.get('competitor_channels', [])),
            'top_videos': len(self.insights.get('top_videos', []))
        }


def main():
    parser = argparse.ArgumentParser(
        description="YouTube Insights Extractor for Dreamweaving"
    )
    parser.add_argument(
        '--update-patterns',
        action='store_true',
        help="Update patterns from raw data"
    )
    parser.add_argument(
        '--full-analysis',
        action='store_true',
        help="Run full analysis pipeline"
    )
    parser.add_argument(
        '--sync-notion',
        action='store_true',
        help="Sync results to Notion databases"
    )
    parser.add_argument(
        '--view', '-v',
        help="View insights for a specific area (patterns/tags/retention/seasonal/channels/videos)"
    )
    parser.add_argument(
        '--config',
        type=Path,
        default=CONFIG_PATH,
        help="Path to config file"
    )

    args = parser.parse_args()

    # Initialize extractor
    extractor = YouTubeInsightsExtractor(config_path=args.config)

    if args.full_analysis:
        extractor.full_analysis(sync_notion=args.sync_notion)
        summary = extractor.get_insights_summary()
        print("\nAnalysis Summary:")
        for key, value in summary.items():
            print(f"  {key}: {value}")

    elif args.update_patterns:
        extractor.load_raw_data()
        extractor.extract_title_patterns()
        extractor.extract_tag_clusters()
        extractor.save_insights()
        print("Patterns updated successfully")

    elif args.view:
        extractor.load_raw_data()
        extractor.full_analysis()

        area = args.view.lower()
        if area == 'patterns':
            patterns = extractor.insights.get('title_patterns', [])
            print(f"\nTitle Patterns ({len(patterns)} found):\n")
            for p in patterns[:10]:
                print(f"  {p['template']}")
                print(f"    CTR: {p['estimated_ctr']}% | Videos: {p['video_count']} | Avg views: {p['avg_views']:,}")
                print()

        elif area == 'tags':
            tags = extractor.insights.get('tag_clusters', {}).get('high_volume', [])
            print(f"\nHigh-Volume Tags ({len(tags)} found):\n")
            for t in tags[:20]:
                print(f"  {t['tag']}: {t['count']} videos, {t['avg_views']:,} avg views")

        elif area == 'seasonal':
            trends = extractor.insights.get('seasonal_trends', {})
            print(f"\nSeasonal Trends:\n")
            for month, data in trends.items():
                lift = data.get('view_lift', 0)
                lift_str = f"+{lift:.0%}" if lift > 0 else f"{lift:.0%}"
                print(f"  {month.title()}: {lift_str} views | Topics: {', '.join(data.get('recommended_topics', [])[:3])}")

        else:
            print(f"Unknown view area: {area}")
            print("Available: patterns, tags, retention, seasonal, channels, videos")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
