#!/usr/bin/env python3
"""
anchor_selector.py - Anchor Selection and Query Utility

Provides intelligent anchor selection for Dreamweaving sessions:
- Query anchors by outcome, phase, category, and state tags
- Avoid repetition across recent sessions
- Optimize for synergy between selected anchors
- Track usage history

Usage:
    from scripts.utilities.anchor_selector import AnchorSelector

    selector = AnchorSelector()
    anchors = selector.select_anchors(
        outcome="healing",
        journey_phases=["integration", "reorientation"],
        count=5
    )
"""

import os
import re
import random
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any, Set
import yaml

# Project root detection
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent


class AnchorEntry:
    """Represents a single anchor from the registry."""

    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.anchor_id = data.get("anchor_id", "")
        self.name = data.get("name", "")
        self.category = data.get("category", "")
        self.trigger_type = data.get("trigger_type", "")

        # Definition
        definition = data.get("definition", {})
        self.brief = definition.get("brief", "")
        self.extended = definition.get("extended", "")

        # Attributes
        attributes = data.get("attributes", {})
        self.state_tags = attributes.get("state_tags", [])
        self.intensity = attributes.get("intensity", "moderate")
        self.modality = attributes.get("modality", "mental")
        self.duration_effect = attributes.get("duration_effect", "short")
        self.cumulative = attributes.get("cumulative", True)

        # Applications
        applications = data.get("applications", {})
        self.journey_phases = applications.get("journey_phases", [])
        self.outcome_alignment = applications.get("outcome_alignment", [])
        self.installation_context = applications.get("installation_context", "in_closing")
        self.contraindications = applications.get("contraindications", [])

        # Templates
        templates = data.get("templates", {})
        self.installation_ssml = templates.get("installation_ssml", "")
        self.reinforcement_ssml = templates.get("reinforcement_ssml", "")
        self.recall_phrase = templates.get("recall_phrase", "")
        self.sfx_cue = templates.get("sfx_cue", "")
        self.visual_imagery = templates.get("visual_imagery", "")

        # Relationships
        relationships = data.get("relationships", {})
        self.synergies = relationships.get("synergies", [])
        self.conflicts = relationships.get("conflicts", [])
        self.progressions = relationships.get("progressions", [])
        self.outcome_patterns = relationships.get("outcome_patterns", [])

        # Scoring (set during selection)
        self._score = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Return anchor data for manifest inclusion."""
        return {
            "anchor_id": self.anchor_id,
            "name": self.name,
            "category": self.category,
            "recall_phrase": self.recall_phrase,
            "state_tags": self.state_tags,
            "installation_context": self.installation_context
        }

    def __repr__(self):
        return f"AnchorEntry({self.anchor_id})"


class AnchorSelector:
    """
    Intelligent anchor selection for Dreamweaving sessions.

    Features:
    - Query by outcome, phase, category, and state tags
    - Variety enforcement (avoid recent usage)
    - Synergy optimization between anchors
    - Category diversity requirements
    """

    # Selection criteria from schema
    MIN_ANCHORS = 3
    MAX_ANCHORS = 7
    MIN_CATEGORIES = 2
    LOOKBACK_SESSIONS = 3
    MAX_REPETITION = 5
    SYNERGY_BONUS = 0.2
    CONFLICT_PENALTY = 0.5
    RECENCY_PENALTY = 0.3

    # Category groupings for required presence
    PHYSICAL_CATEGORIES = {"breath", "kinesthetic", "nature"}
    MENTAL_CATEGORIES = {"verbal", "symbolic", "visual", "portal"}

    def __init__(self, registry_path: Optional[str] = None, history_path: Optional[str] = None):
        """
        Initialize the anchor selector.

        Args:
            registry_path: Path to anchor_registry.yaml (auto-detected if None)
            history_path: Path to anchor_history.yaml (auto-detected if None)
        """
        if registry_path is None:
            registry_path = PROJECT_ROOT / "knowledge" / "anchors" / "anchor_registry.yaml"
        if history_path is None:
            history_path = PROJECT_ROOT / "knowledge" / "anchors" / "anchor_history.yaml"

        self.registry_path = Path(registry_path)
        self.history_path = Path(history_path)

        self.anchors: Dict[str, AnchorEntry] = {}
        self.history: Dict[str, Any] = {}

        self._load_registry()
        self._load_history()

    def _load_registry(self):
        """Load anchors from registry file."""
        if not self.registry_path.exists():
            raise FileNotFoundError(f"Anchor registry not found: {self.registry_path}")

        with open(self.registry_path, "r") as f:
            data = yaml.safe_load(f)

        # Parse each category's anchors
        for category in ["breath", "auditory", "visual", "kinesthetic", "symbolic",
                         "portal", "verbal", "musical", "nature", "daily_life"]:
            category_data = data.get(category, {})
            for anchor_key, anchor_data in category_data.items():
                if isinstance(anchor_data, dict) and "anchor_id" in anchor_data:
                    anchor = AnchorEntry(anchor_data)
                    self.anchors[anchor.anchor_id] = anchor

        print(f"[anchor_selector] Loaded {len(self.anchors)} anchors from registry")

    def _load_history(self):
        """Load usage history from file."""
        if self.history_path.exists():
            with open(self.history_path, "r") as f:
                self.history = yaml.safe_load(f) or {}
        else:
            self.history = {
                "sessions": [],
                "usage_counts": {}
            }

    def _save_history(self):
        """Save usage history to file."""
        # Ensure directory exists
        self.history_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.history_path, "w") as f:
            yaml.dump(self.history, f, default_flow_style=False)

    def get_recent_anchors(self, lookback: int = None) -> Set[str]:
        """Get anchor IDs used in recent sessions."""
        if lookback is None:
            lookback = self.LOOKBACK_SESSIONS

        recent_ids = set()
        sessions = self.history.get("sessions", [])

        for session in sessions[-lookback:]:
            for anchor_id in session.get("anchors", []):
                recent_ids.add(anchor_id)

        return recent_ids

    def get_usage_counts(self) -> Dict[str, int]:
        """Get usage count for each anchor."""
        return self.history.get("usage_counts", {})

    def get_anchor(self, anchor_id: str) -> Optional[AnchorEntry]:
        """Get a specific anchor by ID."""
        return self.anchors.get(anchor_id)

    def get_anchor_ssml(self, anchor_id: str, mode: str = "installation") -> str:
        """
        Get SSML template for an anchor.

        Args:
            anchor_id: The anchor ID
            mode: "installation" or "reinforcement"

        Returns:
            SSML string, or empty string if not found
        """
        anchor = self.get_anchor(anchor_id)
        if not anchor:
            return ""

        if mode == "installation":
            return anchor.installation_ssml
        elif mode == "reinforcement":
            return anchor.reinforcement_ssml or anchor.installation_ssml
        else:
            return anchor.installation_ssml

    def query_anchors(
        self,
        outcome: Optional[str] = None,
        journey_phases: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        state_tags: Optional[List[str]] = None,
        intensity: Optional[str] = None,
        exclude_ids: Optional[List[str]] = None
    ) -> List[AnchorEntry]:
        """
        Query anchors matching criteria.

        Args:
            outcome: Desired outcome to match
            journey_phases: Journey phases to match (any match)
            categories: Categories to include
            state_tags: State tags to match (any match)
            intensity: Intensity level to match
            exclude_ids: Anchor IDs to exclude

        Returns:
            List of matching AnchorEntry objects
        """
        exclude_ids = exclude_ids or []
        results = []

        for anchor_id, anchor in self.anchors.items():
            # Skip excluded
            if anchor_id in exclude_ids:
                continue

            # Outcome filter
            if outcome and outcome not in anchor.outcome_alignment:
                continue

            # Phase filter (any match)
            if journey_phases:
                if not any(phase in anchor.journey_phases for phase in journey_phases):
                    continue

            # Category filter
            if categories and anchor.category not in categories:
                continue

            # State tag filter (any match)
            if state_tags:
                if not any(tag in anchor.state_tags for tag in state_tags):
                    continue

            # Intensity filter
            if intensity and anchor.intensity != intensity:
                continue

            results.append(anchor)

        return results

    def select_anchors(
        self,
        outcome: str,
        journey_phases: List[str],
        count: int = 5,
        categories_required: Optional[List[str]] = None,
        exclude_recent: bool = True,
        ensure_variety: bool = True
    ) -> List[AnchorEntry]:
        """
        Select optimal anchors for a session.

        Args:
            outcome: The session's desired outcome
            journey_phases: Journey phases to use
            count: Number of anchors to select (3-7)
            categories_required: Specific categories to include
            exclude_recent: Apply recency penalty
            ensure_variety: Ensure category diversity

        Returns:
            List of selected AnchorEntry objects
        """
        # Clamp count
        count = max(self.MIN_ANCHORS, min(self.MAX_ANCHORS, count))

        # Get candidates matching outcome and phases
        candidates = self.query_anchors(
            outcome=outcome,
            journey_phases=journey_phases
        )

        if not candidates:
            # Fallback: just match phases
            candidates = self.query_anchors(journey_phases=journey_phases)

        if not candidates:
            # Fallback: all anchors
            candidates = list(self.anchors.values())

        # Score each candidate
        recent_ids = self.get_recent_anchors() if exclude_recent else set()
        usage_counts = self.get_usage_counts()

        for anchor in candidates:
            anchor._score = 1.0

            # Outcome bonus
            if outcome in anchor.outcome_alignment:
                anchor._score += 0.3

            # Phase match bonus
            phase_matches = sum(1 for p in journey_phases if p in anchor.journey_phases)
            anchor._score += phase_matches * 0.1

            # Recency penalty
            if anchor.anchor_id in recent_ids:
                anchor._score -= self.RECENCY_PENALTY

            # Usage count penalty (prefer less-used anchors)
            uses = usage_counts.get(anchor.anchor_id, 0)
            if uses > self.MAX_REPETITION:
                anchor._score -= 0.2
            elif uses == 0:
                anchor._score += 0.1  # Bonus for unused anchors

        # Sort by score
        candidates.sort(key=lambda a: a._score, reverse=True)

        selected: List[AnchorEntry] = []
        selected_ids: Set[str] = set()
        categories_used: Set[str] = set()

        # Phase 1: If specific categories required, pick one from each
        if categories_required:
            for cat in categories_required:
                cat_anchors = [a for a in candidates
                               if a.category == cat and a.anchor_id not in selected_ids]
                if cat_anchors:
                    best = max(cat_anchors, key=lambda a: a._score)
                    selected.append(best)
                    selected_ids.add(best.anchor_id)
                    categories_used.add(best.category)

        # Phase 2: Ensure variety (at least one physical, one mental)
        if ensure_variety and len(selected) < count:
            # Check physical
            if not categories_used.intersection(self.PHYSICAL_CATEGORIES):
                physical_anchors = [a for a in candidates
                                    if a.category in self.PHYSICAL_CATEGORIES
                                    and a.anchor_id not in selected_ids]
                if physical_anchors:
                    best = max(physical_anchors, key=lambda a: a._score)
                    selected.append(best)
                    selected_ids.add(best.anchor_id)
                    categories_used.add(best.category)

            # Check mental
            if not categories_used.intersection(self.MENTAL_CATEGORIES):
                mental_anchors = [a for a in candidates
                                  if a.category in self.MENTAL_CATEGORIES
                                  and a.anchor_id not in selected_ids]
                if mental_anchors:
                    best = max(mental_anchors, key=lambda a: a._score)
                    selected.append(best)
                    selected_ids.add(best.anchor_id)
                    categories_used.add(best.category)

        # Phase 3: Apply synergy bonuses and select remaining
        remaining_count = count - len(selected)
        if remaining_count > 0:
            # Apply synergy scoring
            for anchor in candidates:
                if anchor.anchor_id in selected_ids:
                    continue

                synergy_bonus = 0
                for selected_anchor in selected:
                    if selected_anchor.anchor_id in anchor.synergies:
                        synergy_bonus += self.SYNERGY_BONUS
                    if selected_anchor.anchor_id in anchor.conflicts:
                        synergy_bonus -= self.CONFLICT_PENALTY

                anchor._score += synergy_bonus

            # Re-sort remaining candidates
            remaining = [a for a in candidates if a.anchor_id not in selected_ids]
            remaining.sort(key=lambda a: a._score, reverse=True)

            # Prefer category diversity in remaining selection
            if len(categories_used) < self.MIN_CATEGORIES:
                for anchor in remaining:
                    if anchor.category not in categories_used:
                        selected.append(anchor)
                        selected_ids.add(anchor.anchor_id)
                        categories_used.add(anchor.category)
                        remaining_count -= 1
                        if remaining_count <= 0:
                            break

            # Fill remaining slots with top scorers
            for anchor in remaining:
                if anchor.anchor_id not in selected_ids:
                    selected.append(anchor)
                    selected_ids.add(anchor.anchor_id)
                    remaining_count -= 1
                    if remaining_count <= 0:
                        break

        return selected

    def suggest_for_section(
        self,
        section_name: str,
        outcome: str,
        already_used: Optional[List[str]] = None
    ) -> List[AnchorEntry]:
        """
        Suggest 1-2 anchors appropriate for a specific script section.

        Args:
            section_name: e.g., "induction", "journey", "closing"
            outcome: Session outcome
            already_used: Anchor IDs already selected

        Returns:
            List of 1-2 suggested anchors
        """
        already_used = already_used or []

        # Map section names to journey phases
        section_phase_map = {
            "pre_talk": ["pre_talk"],
            "pretalk": ["pre_talk"],
            "induction": ["induction", "deepening"],
            "deepening": ["deepening"],
            "journey": ["journey", "helm_deep_trance"],
            "helm": ["helm_deep_trance"],
            "integration": ["integration"],
            "closing": ["integration", "reorientation"],
            "reorientation": ["reorientation"]
        }

        phases = section_phase_map.get(section_name.lower(), ["integration"])

        candidates = self.query_anchors(
            outcome=outcome,
            journey_phases=phases,
            exclude_ids=already_used
        )

        if not candidates:
            candidates = self.query_anchors(
                journey_phases=phases,
                exclude_ids=already_used
            )

        # Score and return top 2
        for anchor in candidates:
            anchor._score = 1.0
            if outcome in anchor.outcome_alignment:
                anchor._score += 0.3

            # Prefer anchors with matching installation context
            context_map = {
                "induction": "during_induction",
                "deepening": "during_deepening",
                "journey": "during_journey",
                "helm": "at_peak",
                "integration": "during_integration",
                "closing": "in_closing"
            }
            expected_context = context_map.get(section_name.lower(), "in_closing")
            if anchor.installation_context == expected_context:
                anchor._score += 0.2

        candidates.sort(key=lambda a: a._score, reverse=True)
        return candidates[:2]

    def record_usage(self, session_name: str, anchor_ids: List[str]):
        """
        Record anchor usage for a session.

        Args:
            session_name: Name of the session
            anchor_ids: List of anchor IDs used
        """
        # Add to session history
        sessions = self.history.get("sessions", [])
        sessions.append({
            "session": session_name,
            "date": datetime.now().isoformat(),
            "anchors": anchor_ids
        })

        # Keep only recent sessions
        max_history = 20
        self.history["sessions"] = sessions[-max_history:]

        # Update usage counts
        usage_counts = self.history.get("usage_counts", {})
        for anchor_id in anchor_ids:
            usage_counts[anchor_id] = usage_counts.get(anchor_id, 0) + 1
        self.history["usage_counts"] = usage_counts

        # Save
        self._save_history()

    def get_all_categories(self) -> List[str]:
        """Get list of all anchor categories."""
        return list(set(a.category for a in self.anchors.values()))

    def get_anchors_by_category(self, category: str) -> List[AnchorEntry]:
        """Get all anchors in a category."""
        return [a for a in self.anchors.values() if a.category == category]

    def get_anchors_by_outcome(self, outcome: str) -> List[AnchorEntry]:
        """Get all anchors supporting an outcome."""
        return [a for a in self.anchors.values() if outcome in a.outcome_alignment]

    def format_for_manifest(self, anchors: List[AnchorEntry]) -> List[Dict]:
        """Format anchors for inclusion in manifest.yaml."""
        return [a.to_dict() for a in anchors]

    def format_for_youtube(self, anchors: List[AnchorEntry]) -> str:
        """
        Format anchors for YouTube description.

        Returns markdown-formatted anchor section.
        """
        if not anchors:
            return ""

        lines = [
            "## 🎯 Post-Hypnotic Anchors",
            "",
            "This session installs these powerful anchors for future use:",
            ""
        ]

        for anchor in anchors:
            category_display = anchor.category.replace("_", " ").title()
            lines.append(f"**{anchor.name}** ({category_display})")
            if anchor.recall_phrase:
                lines.append(f"  *Trigger: {anchor.recall_phrase}*")
            lines.append("")

        lines.append("_These anchors strengthen with repeated listening._")
        lines.append("")

        return "\n".join(lines)


def expand_anchor_tags(content: str, selector: AnchorSelector, mode: str = "installation") -> str:
    """
    Expand {{ANCHOR:anchor_id}} tags in content.

    Args:
        content: Script content with anchor tags
        selector: AnchorSelector instance
        mode: "installation" or "reinforcement"

    Returns:
        Content with anchor tags replaced by SSML
    """
    pattern = r'\{\{ANCHOR:([a-z_\.]+)\}\}'

    def replacer(match):
        anchor_id = match.group(1)
        ssml = selector.get_anchor_ssml(anchor_id, mode)
        if not ssml:
            return f"<!-- ANCHOR NOT FOUND: {anchor_id} -->"
        return ssml.strip()

    return re.sub(pattern, replacer, content)


# CLI interface for testing
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Anchor Selector Utility")
    parser.add_argument("--outcome", "-o", help="Desired outcome (e.g., healing, transformation)")
    parser.add_argument("--phases", "-p", nargs="+", help="Journey phases to match")
    parser.add_argument("--count", "-n", type=int, default=5, help="Number of anchors to select")
    parser.add_argument("--category", "-c", help="Filter by category")
    parser.add_argument("--list-categories", action="store_true", help="List all categories")
    parser.add_argument("--list-anchors", action="store_true", help="List all anchors")
    parser.add_argument("--get", "-g", help="Get specific anchor by ID")
    parser.add_argument("--youtube", action="store_true", help="Format output for YouTube")

    args = parser.parse_args()

    selector = AnchorSelector()

    if args.list_categories:
        print("\nAnchor Categories:")
        for cat in sorted(selector.get_all_categories()):
            count = len(selector.get_anchors_by_category(cat))
            print(f"  - {cat}: {count} anchors")

    elif args.list_anchors:
        print(f"\nAll Anchors ({len(selector.anchors)}):")
        for anchor_id in sorted(selector.anchors.keys()):
            anchor = selector.anchors[anchor_id]
            print(f"  - {anchor_id}: {anchor.name}")

    elif args.get:
        anchor = selector.get_anchor(args.get)
        if anchor:
            print(f"\nAnchor: {anchor.anchor_id}")
            print(f"Name: {anchor.name}")
            print(f"Category: {anchor.category}")
            print(f"Brief: {anchor.brief}")
            print(f"State Tags: {', '.join(anchor.state_tags)}")
            print(f"Recall Phrase: {anchor.recall_phrase}")
            print(f"\nInstallation SSML:")
            print(anchor.installation_ssml[:500] + "..." if len(anchor.installation_ssml) > 500 else anchor.installation_ssml)
        else:
            print(f"Anchor not found: {args.get}")

    elif args.outcome:
        phases = args.phases or ["integration", "reorientation"]
        anchors = selector.select_anchors(
            outcome=args.outcome,
            journey_phases=phases,
            count=args.count
        )

        if args.youtube:
            print(selector.format_for_youtube(anchors))
        else:
            print(f"\nSelected {len(anchors)} anchors for outcome '{args.outcome}':")
            for anchor in anchors:
                print(f"  - [{anchor.category}] {anchor.anchor_id}: {anchor.name}")
                print(f"    Recall: {anchor.recall_phrase}")

    else:
        parser.print_help()
