"""
SEO Optimizer for Website Recursive Agent.

Auto-optimizes SEO based on:
- Search rankings tracking
- Keyword opportunity detection
- Meta tag optimization
- Content gap analysis

Uses patterns from high-ranking pages to improve underperformers.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import yaml
import json
import re
from collections import Counter

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


@dataclass
class SEOAnalysis:
    """SEO analysis for a page."""

    page_path: str
    page_title: str

    # Meta analysis
    title_length: int = 0
    title_has_keyword: bool = False
    meta_description_length: int = 0
    has_meta_description: bool = False

    # Keyword analysis
    primary_keyword: str = ""
    keyword_density: float = 0.0
    keyword_in_h1: bool = False
    keyword_in_first_paragraph: bool = False

    # Structure analysis
    h1_count: int = 0
    h2_count: int = 0
    word_count: int = 0
    internal_links: int = 0
    external_links: int = 0

    # Image analysis
    image_count: int = 0
    images_with_alt: int = 0

    # Overall SEO score (0-100)
    seo_score: float = 0.0

    # Issues found
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def compute_seo_score(self) -> float:
        """
        Compute overall SEO score based on multiple factors.

        Factors:
        - Title optimization: 20%
        - Meta description: 15%
        - Keyword usage: 25%
        - Content structure: 20%
        - Internal linking: 10%
        - Image optimization: 10%
        """
        score = 0.0

        # Title optimization (20%)
        title_score = 0.0
        if 50 <= self.title_length <= 60:
            title_score += 50
        elif 40 <= self.title_length <= 70:
            title_score += 30
        if self.title_has_keyword:
            title_score += 50
        score += title_score * 0.20

        # Meta description (15%)
        meta_score = 0.0
        if self.has_meta_description:
            meta_score += 50
            if 150 <= self.meta_description_length <= 160:
                meta_score += 50
            elif 120 <= self.meta_description_length <= 180:
                meta_score += 30
        score += meta_score * 0.15

        # Keyword usage (25%)
        keyword_score = 0.0
        if self.keyword_in_h1:
            keyword_score += 30
        if self.keyword_in_first_paragraph:
            keyword_score += 30
        if 0.01 <= self.keyword_density <= 0.03:
            keyword_score += 40
        elif self.keyword_density > 0:
            keyword_score += 20
        score += keyword_score * 0.25

        # Content structure (20%)
        structure_score = 0.0
        if self.h1_count == 1:
            structure_score += 30
        if self.h2_count >= 2:
            structure_score += 30
        if self.word_count >= 500:
            structure_score += 40
        elif self.word_count >= 300:
            structure_score += 20
        score += structure_score * 0.20

        # Internal linking (10%)
        link_score = min(100, self.internal_links * 20)
        score += link_score * 0.10

        # Image optimization (10%)
        if self.image_count > 0:
            image_score = (self.images_with_alt / self.image_count) * 100
        else:
            image_score = 50  # Neutral if no images
        score += image_score * 0.10

        self.seo_score = round(score, 1)
        return self.seo_score


@dataclass
class KeywordOpportunity:
    """A keyword opportunity for content optimization."""

    keyword: str
    search_volume_estimate: str  # low | medium | high
    competition_estimate: str  # low | medium | high
    relevance_score: float  # 0-100

    # Current state
    currently_ranking: bool = False
    current_position: Optional[int] = None

    # Recommendations
    target_pages: List[str] = field(default_factory=list)
    action: str = ""  # optimize_existing | create_new | add_to_existing


class SEOOptimizer:
    """
    SEO optimization for website content.

    Features:
    - Page SEO analysis
    - Keyword opportunity detection
    - Meta tag optimization suggestions
    - Content gap identification
    - Internal linking recommendations
    """

    # Target keyword clusters for dreamweaving content
    KEYWORD_CLUSTERS = {
        'hypnosis': [
            'self hypnosis', 'guided hypnosis', 'hypnotic meditation',
            'deep hypnosis', 'hypnosis sleep', 'healing hypnosis',
        ],
        'meditation': [
            'guided meditation', 'deep meditation', 'sleep meditation',
            'spiritual meditation', 'theta meditation', 'healing meditation',
        ],
        'binaural': [
            'binaural beats', 'theta waves', 'alpha waves',
            'brainwave entrainment', 'frequency meditation',
        ],
        'spiritual': [
            'spiritual journey', 'inner journey', 'sacred journey',
            'mystical experience', 'consciousness expansion',
        ],
        'healing': [
            'self healing', 'emotional healing', 'energy healing',
            'trauma healing', 'inner healing', 'soul healing',
        ],
    }

    def __init__(
        self,
        project_root: Optional[Path] = None,
    ):
        """
        Initialize SEO optimizer.

        Args:
            project_root: Path to project root
        """
        self.project_root = project_root or PROJECT_ROOT

        # Data storage
        self.data_dir = self.project_root / "knowledge" / "seo_data"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.analyses_file = self.data_dir / "seo_analyses.yaml"
        self.opportunities_file = self.data_dir / "keyword_opportunities.yaml"
        self.rankings_file = self.data_dir / "ranking_history.yaml"

        # Load existing data
        self._analyses: Dict[str, SEOAnalysis] = {}
        self._opportunities: List[KeywordOpportunity] = []
        self._load_data()

    def _load_data(self) -> None:
        """Load SEO data from disk."""
        # Load analyses
        if self.analyses_file.exists():
            try:
                with open(self.analyses_file) as f:
                    data = yaml.safe_load(f) or {}
                self._analyses = {
                    path: SEOAnalysis(**analysis)
                    for path, analysis in data.items()
                }
            except Exception:
                self._analyses = {}

        # Load opportunities
        if self.opportunities_file.exists():
            try:
                with open(self.opportunities_file) as f:
                    data = yaml.safe_load(f) or []
                self._opportunities = [
                    KeywordOpportunity(**opp) for opp in data
                ]
            except Exception:
                self._opportunities = []

    def _save_analyses(self) -> None:
        """Save analyses to disk."""
        data = {
            path: {
                'page_path': a.page_path,
                'page_title': a.page_title,
                'title_length': a.title_length,
                'title_has_keyword': a.title_has_keyword,
                'meta_description_length': a.meta_description_length,
                'has_meta_description': a.has_meta_description,
                'primary_keyword': a.primary_keyword,
                'keyword_density': a.keyword_density,
                'keyword_in_h1': a.keyword_in_h1,
                'keyword_in_first_paragraph': a.keyword_in_first_paragraph,
                'h1_count': a.h1_count,
                'h2_count': a.h2_count,
                'word_count': a.word_count,
                'internal_links': a.internal_links,
                'external_links': a.external_links,
                'image_count': a.image_count,
                'images_with_alt': a.images_with_alt,
                'seo_score': a.seo_score,
                'issues': a.issues,
                'recommendations': a.recommendations,
            }
            for path, a in self._analyses.items()
        }
        with open(self.analyses_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)

    def _save_opportunities(self) -> None:
        """Save opportunities to disk."""
        data = [
            {
                'keyword': o.keyword,
                'search_volume_estimate': o.search_volume_estimate,
                'competition_estimate': o.competition_estimate,
                'relevance_score': o.relevance_score,
                'currently_ranking': o.currently_ranking,
                'current_position': o.current_position,
                'target_pages': o.target_pages,
                'action': o.action,
            }
            for o in self._opportunities
        ]
        with open(self.opportunities_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)

    def analyze_page(
        self,
        page_path: str,
        content: str,
        title: str = "",
        meta_description: str = "",
        primary_keyword: str = "",
    ) -> SEOAnalysis:
        """
        Analyze a page's SEO.

        Args:
            page_path: Page path
            content: Page HTML/text content
            title: Page title
            meta_description: Meta description
            primary_keyword: Primary target keyword

        Returns:
            SEOAnalysis with score and recommendations
        """
        analysis = SEOAnalysis(
            page_path=page_path,
            page_title=title,
        )

        # Title analysis
        analysis.title_length = len(title)
        if primary_keyword:
            analysis.title_has_keyword = primary_keyword.lower() in title.lower()
            analysis.primary_keyword = primary_keyword

        # Meta description analysis
        analysis.has_meta_description = bool(meta_description)
        analysis.meta_description_length = len(meta_description)

        # Content analysis
        clean_content = self._strip_html(content)
        words = clean_content.split()
        analysis.word_count = len(words)

        # Keyword density
        if primary_keyword and analysis.word_count > 0:
            keyword_count = clean_content.lower().count(primary_keyword.lower())
            analysis.keyword_density = keyword_count / analysis.word_count

        # Structure analysis (simple HTML parsing)
        analysis.h1_count = content.lower().count('<h1')
        analysis.h2_count = content.lower().count('<h2')

        # Check keyword in h1
        h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.IGNORECASE | re.DOTALL)
        if h1_match and primary_keyword:
            analysis.keyword_in_h1 = primary_keyword.lower() in h1_match.group(1).lower()

        # Check keyword in first paragraph
        p_match = re.search(r'<p[^>]*>(.*?)</p>', content, re.IGNORECASE | re.DOTALL)
        if p_match and primary_keyword:
            analysis.keyword_in_first_paragraph = (
                primary_keyword.lower() in p_match.group(1).lower()
            )

        # Link analysis
        analysis.internal_links = len(re.findall(
            r'href=["\'][^"\']*salars\.net[^"\']*["\']',
            content,
            re.IGNORECASE,
        ))
        analysis.external_links = len(re.findall(
            r'href=["\']https?://(?!.*salars\.net)[^"\']+["\']',
            content,
            re.IGNORECASE,
        ))

        # Image analysis
        images = re.findall(r'<img[^>]*>', content, re.IGNORECASE)
        analysis.image_count = len(images)
        analysis.images_with_alt = len([
            img for img in images
            if 'alt=' in img.lower() and 'alt=""' not in img.lower()
        ])

        # Compute score
        analysis.compute_seo_score()

        # Generate issues and recommendations
        self._generate_recommendations(analysis)

        # Store analysis
        self._analyses[page_path] = analysis
        self._save_analyses()

        return analysis

    def _strip_html(self, content: str) -> str:
        """Strip HTML tags from content."""
        return re.sub(r'<[^>]+>', ' ', content)

    def _generate_recommendations(self, analysis: SEOAnalysis) -> None:
        """Generate issues and recommendations for analysis."""
        issues = []
        recommendations = []

        # Title issues
        if analysis.title_length < 40:
            issues.append("Title too short")
            recommendations.append("Expand title to 50-60 characters for better CTR")
        elif analysis.title_length > 70:
            issues.append("Title too long (may be truncated in search)")
            recommendations.append("Shorten title to under 60 characters")

        if not analysis.title_has_keyword and analysis.primary_keyword:
            issues.append("Primary keyword not in title")
            recommendations.append(
                f"Add '{analysis.primary_keyword}' to page title"
            )

        # Meta description issues
        if not analysis.has_meta_description:
            issues.append("Missing meta description")
            recommendations.append("Add meta description (150-160 characters)")
        elif analysis.meta_description_length < 120:
            issues.append("Meta description too short")
            recommendations.append("Expand meta description to 150-160 characters")

        # Content issues
        if analysis.word_count < 300:
            issues.append("Content too thin")
            recommendations.append("Add more content (aim for 500+ words)")

        if analysis.h1_count == 0:
            issues.append("Missing H1 heading")
            recommendations.append("Add a single H1 heading with primary keyword")
        elif analysis.h1_count > 1:
            issues.append("Multiple H1 headings")
            recommendations.append("Use only one H1 heading per page")

        if analysis.h2_count < 2:
            issues.append("Insufficient subheadings")
            recommendations.append("Add H2 subheadings to improve structure")

        # Keyword issues
        if analysis.keyword_density > 0.04:
            issues.append("Keyword density too high (keyword stuffing risk)")
            recommendations.append("Reduce keyword repetition for natural flow")
        elif analysis.keyword_density < 0.01 and analysis.primary_keyword:
            issues.append("Keyword density too low")
            recommendations.append(
                f"Include '{analysis.primary_keyword}' more naturally in content"
            )

        # Internal linking
        if analysis.internal_links == 0:
            issues.append("No internal links")
            recommendations.append("Add 2-3 internal links to related content")

        # Images
        if analysis.image_count > 0 and analysis.images_with_alt < analysis.image_count:
            missing_alt = analysis.image_count - analysis.images_with_alt
            issues.append(f"{missing_alt} images missing alt text")
            recommendations.append("Add descriptive alt text to all images")

        analysis.issues = issues
        analysis.recommendations = recommendations

    def identify_opportunities(self) -> List[KeywordOpportunity]:
        """
        Identify keyword opportunities for the website.

        Based on:
        - Keyword clusters relevant to dreamweaving
        - Current content coverage
        - Estimated competition

        Returns:
            List of keyword opportunities
        """
        opportunities = []

        # Analyze current content coverage
        covered_keywords = set()
        for analysis in self._analyses.values():
            if analysis.primary_keyword:
                covered_keywords.add(analysis.primary_keyword.lower())

        # Check each keyword cluster
        for cluster_name, keywords in self.KEYWORD_CLUSTERS.items():
            for keyword in keywords:
                is_covered = keyword.lower() in covered_keywords

                # Estimate relevance based on cluster
                relevance = 80.0 if cluster_name in ['hypnosis', 'meditation'] else 70.0

                opportunity = KeywordOpportunity(
                    keyword=keyword,
                    search_volume_estimate='medium',  # Would need actual data
                    competition_estimate='medium',
                    relevance_score=relevance,
                    currently_ranking=is_covered,
                    action='optimize_existing' if is_covered else 'create_new',
                )

                opportunities.append(opportunity)

        # Sort by relevance and coverage
        opportunities.sort(
            key=lambda o: (not o.currently_ranking, -o.relevance_score)
        )

        self._opportunities = opportunities
        self._save_opportunities()

        return opportunities

    def get_optimization_plan(
        self,
        page_path: str,
    ) -> Dict[str, Any]:
        """
        Get a complete optimization plan for a page.

        Args:
            page_path: Page to optimize

        Returns:
            Dict with optimization plan
        """
        analysis = self._analyses.get(page_path)
        if not analysis:
            return {'error': 'Page not analyzed yet'}

        plan = {
            'page_path': page_path,
            'current_score': analysis.seo_score,
            'target_score': min(100, analysis.seo_score + 20),
            'priority_actions': [],
            'quick_wins': [],
            'long_term_improvements': [],
        }

        # Categorize recommendations
        for i, rec in enumerate(analysis.recommendations):
            if 'title' in rec.lower() or 'meta' in rec.lower():
                plan['quick_wins'].append(rec)
            elif 'content' in rec.lower() or 'keyword' in rec.lower():
                plan['long_term_improvements'].append(rec)
            else:
                plan['priority_actions'].append(rec)

        # Add keyword suggestions if missing
        if not analysis.primary_keyword:
            relevant = self._suggest_keywords_for_page(page_path)
            if relevant:
                plan['keyword_suggestions'] = relevant[:5]

        return plan

    def _suggest_keywords_for_page(self, page_path: str) -> List[str]:
        """Suggest relevant keywords based on page path."""
        suggestions = []

        # Parse page path for hints
        path_parts = page_path.lower().split('/')

        if 'dreamweavings' in path_parts:
            suggestions.extend(self.KEYWORD_CLUSTERS['hypnosis'][:3])
            suggestions.extend(self.KEYWORD_CLUSTERS['spiritual'][:2])

        for part in path_parts:
            if 'heal' in part:
                suggestions.extend(self.KEYWORD_CLUSTERS['healing'][:3])
            if 'meditat' in part:
                suggestions.extend(self.KEYWORD_CLUSTERS['meditation'][:3])
            if 'binaural' in part or 'theta' in part:
                suggestions.extend(self.KEYWORD_CLUSTERS['binaural'][:3])

        return list(set(suggestions))

    def get_site_seo_summary(self) -> Dict[str, Any]:
        """Get overall SEO summary for the site."""
        if not self._analyses:
            return {'error': 'No pages analyzed yet'}

        scores = [a.seo_score for a in self._analyses.values()]
        avg_score = sum(scores) / len(scores)

        # Count issues by type
        all_issues = []
        for a in self._analyses.values():
            all_issues.extend(a.issues)

        issue_counts = Counter(all_issues)

        return {
            'total_pages_analyzed': len(self._analyses),
            'average_seo_score': round(avg_score, 1),
            'highest_score': max(scores),
            'lowest_score': min(scores),
            'pages_above_70': len([s for s in scores if s >= 70]),
            'pages_below_50': len([s for s in scores if s < 50]),
            'top_issues': issue_counts.most_common(5),
            'keyword_opportunities': len([
                o for o in self._opportunities if not o.currently_ranking
            ]),
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get optimizer statistics."""
        return {
            'pages_analyzed': len(self._analyses),
            'total_opportunities': len(self._opportunities),
            'uncovered_keywords': len([
                o for o in self._opportunities if not o.currently_ranking
            ]),
            'avg_seo_score': (
                sum(a.seo_score for a in self._analyses.values()) / len(self._analyses)
                if self._analyses else 0
            ),
        }
