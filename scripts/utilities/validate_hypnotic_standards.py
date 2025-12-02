#!/usr/bin/env python3
"""
Hypnotic Session Standards Validator

Comprehensive validation tool ensuring all hypnotic processing elements
are included and consistent across all sessions.

This is the PRIMARY quality control tool for Dreamweaving sessions.

Usage:
    python3 validate_hypnotic_standards.py sessions/my-session
    python3 validate_hypnotic_standards.py --all
    python3 validate_hypnotic_standards.py --all --compare
    python3 validate_hypnotic_standards.py --report

Features:
    - Validates all mandatory elements per session
    - Cross-session consistency checking
    - Generates compliance reports
    - Identifies missing/inconsistent elements
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import yaml


# =============================================================================
# STANDARDS DEFINITIONS
# =============================================================================

# Mandatory sections (must appear in this order)
MANDATORY_SECTIONS = [
    ("pretalk", "PRE-TALK", 2, 3),       # (id, marker, min_min, max_min)
    ("induction", "INDUCTION", 3, 5),
    ("journey", "MAIN JOURNEY", 10, 20),
    ("integration", "INTEGRATION", 2, 3),
    ("closing", "POST-HYPNOTIC", 2, 3),
]

# Pre-talk required elements
PRETALK_ELEMENTS = {
    "introduction": [
        r"(sacred digital dreamweaver|randy sailer|autonomous ai)",
        "Introduction as Sacred Digital Dreamweaver"
    ],
    "purpose": [
        r"(today|session|journey).*(purpose|goal|intention|cultivate|explore|discover)",
        "Clear statement of session purpose"
    ],
    "safety": [
        r"(fully aware|in control|safe|supported|return.*any.*moment|open your eyes)",
        "Safety reassurance statement"
    ],
    "preparation": [
        r"(comfortable|headphones|position|won't be disturbed|relax)",
        "Preparation instructions"
    ],
    "consent": [
        r"(when you're ready|ready.*begin|let's begin|we begin)",
        "Consent cue to begin"
    ],
}

# Induction required elements
INDUCTION_ELEMENTS = {
    "relaxation": [
        r"(relax|relaxation|tension|release|heavy|soft|calm|let go)",
        "Progressive relaxation sequence"
    ],
    "breathing": [
        r"(breath|breathe|inhale|exhale|breathing)",
        "Breathing cues"
    ],
    "countdown": [
        r"(ten|nine|eight|seven|six|five|four|three|two|one|\b10\b|\b9\b|\b8\b|\b7\b|\b6\b|\b5\b|\b4\b|\b3\b|\b2\b|\b1\b)",
        "Countdown deepening"
    ],
    "deepening": [
        r"(deeper|deep|descend|drift|float|sinking|falling)",
        "Deepening suggestions"
    ],
}

# Journey required senses
JOURNEY_SENSES = {
    "sight": [
        r"(see|seeing|vision|visual|light|color|glow|bright|dark|shadow|notice|observe|watch|look)",
        "Visual descriptions"
    ],
    "sound": [
        r"(hear|hearing|sound|listen|voice|whisper|echo|hum|ring|silence|tone|music)",
        "Auditory descriptions"
    ],
    "touch": [
        r"(feel|feeling|touch|warm|cool|cold|hot|soft|smooth|rough|pressure|sensation|texture)",
        "Tactile descriptions"
    ],
    "smell": [
        r"(smell|scent|fragrance|aroma|incense|flower|earth|air|fresh)",
        "Olfactory descriptions"
    ],
    "taste": [
        r"(taste|flavor|sweet|bitter|nectar|honey|water|drink)",
        "Gustatory descriptions (optional)"
    ],
}

# Integration required elements
INTEGRATION_ELEMENTS = {
    "ascending_count": [
        r"(one|two|three|four|five|six|seven|eight|nine|ten|\b1\b|\b2\b|\b3\b|\b4\b|\b5\b)",
        "Ascending countdown"
    ],
    "grounding": [
        r"(body|feet|hands|physical|present|awareness|surface|chair|floor|ground)",
        "Physical grounding cues"
    ],
    "anchoring": [
        r"(bring.*back|bringing.*with|carry.*forward|remember|take.*with|integrate)",
        "Insight anchoring"
    ],
}

# Closing required elements
CLOSING_ELEMENTS = {
    "anchors": [
        r"(whenever|each time|every time|moment|remember|recall|trigger|cue|anchor)",
        "Post-hypnotic anchors"
    ],
    "future_pacing": [
        r"(days ahead|coming days|week|future|tomorrow|forward|from now on|ongoing)",
        "Future pacing suggestions"
    ],
    "thank_you": [
        r"(thank you|grateful|gratitude|honor|blessed|appreciate)",
        "Gratitude expression"
    ],
    "call_to_action": [
        r"(like|subscribe|follow|share|channel|link)",
        "Call to action"
    ],
    "blessing": [
        r"(bless|blessing|peace|light|love|journey|go forth|namaste|be well)",
        "Closing blessing"
    ],
}

# Voice enhancement required settings
VOICE_ENHANCEMENT_REQUIRED = [
    "warmth_drive",
    "deessing",
    "whisper_overlay",
    "subharmonic",
    "double_voice",
    "room_tone",
    "cuddle_waves",
]

# Audio standards
AUDIO_STANDARDS = {
    "voice_db": -6,
    "binaural_db": -6,
    "sfx_db": 0,
    "target_lufs": -14,
    "true_peak": -1.5,
    "sample_rate": 48000,
}

# Binaural arc checkpoints (section: target Hz range)
BINAURAL_ARC = {
    "pretalk": (8, 12),
    "induction": (6, 10),
    "journey": (1, 7),
    "integration": (4, 10),
    "closing": (8, 12),
}


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ValidationResult:
    """Result of validating a single element."""
    element: str
    required: bool
    present: bool
    description: str
    details: str = ""
    count: int = 0


@dataclass
class SectionValidation:
    """Validation results for a single section."""
    section_id: str
    section_name: str
    present: bool
    duration_valid: bool
    duration_actual: Optional[float] = None
    elements: List[ValidationResult] = field(default_factory=list)


@dataclass
class SessionValidation:
    """Complete validation results for a session."""
    session_name: str
    session_path: Path
    valid: bool
    sections: List[SectionValidation] = field(default_factory=list)
    manifest_errors: List[str] = field(default_factory=list)
    script_errors: List[str] = field(default_factory=list)
    audio_errors: List[str] = field(default_factory=list)
    file_errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    info: List[str] = field(default_factory=list)

    # Metrics for cross-session comparison
    word_count: int = 0
    anchor_count: int = 0
    sense_coverage: int = 0  # Out of 5
    deepening_count: int = 0
    break_count: int = 0


# =============================================================================
# VALIDATORS
# =============================================================================

class HypnoticStandardsValidator:
    """
    Validates a hypnotic session against all mandatory standards.
    """

    def __init__(self, session_path: Path):
        self.session_path = Path(session_path)
        self.session_name = self.session_path.name
        self.result = SessionValidation(
            session_name=self.session_name,
            session_path=self.session_path,
            valid=True
        )

        # Loaded data
        self.manifest: Dict = {}
        self.script_content: str = ""
        self.script_sections: Dict[str, str] = {}

    def validate(self) -> SessionValidation:
        """Run complete validation."""
        print(f"\n{'='*60}")
        print(f"Validating: {self.session_name}")
        print(f"{'='*60}")

        # Check basic structure
        if not self._validate_structure():
            return self.result

        # Load files
        self._load_manifest()
        self._load_script()

        # Validate components
        self._validate_manifest()
        self._validate_script_sections()
        self._validate_script_elements()
        self._validate_audio_settings()
        self._validate_output_files()

        # Calculate metrics
        self._calculate_metrics()

        # Determine overall validity
        self.result.valid = (
            len(self.result.manifest_errors) == 0 and
            len(self.result.script_errors) == 0 and
            len(self.result.audio_errors) == 0 and
            len(self.result.file_errors) == 0
        )

        return self.result

    def _validate_structure(self) -> bool:
        """Validate basic directory structure."""
        if not self.session_path.exists():
            self.result.file_errors.append(f"Session directory does not exist")
            self.result.valid = False
            return False

        required_dirs = ["output", "working_files"]
        for d in required_dirs:
            if not (self.session_path / d).exists():
                self.result.file_errors.append(f"Missing required directory: {d}/")

        if not (self.session_path / "manifest.yaml").exists():
            self.result.file_errors.append("Missing manifest.yaml")
            self.result.valid = False
            return False

        return True

    def _load_manifest(self):
        """Load and parse manifest.yaml."""
        manifest_path = self.session_path / "manifest.yaml"
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                self.manifest = yaml.safe_load(f) or {}
        except Exception as e:
            self.result.manifest_errors.append(f"Failed to parse manifest: {e}")

    def _load_script(self):
        """Load script content."""
        # Try multiple possible locations
        script_paths = [
            self.session_path / "working_files" / "script_production.ssml",
            self.session_path / "working_files" / "script_voice_clean.ssml",
            self.session_path / "script.ssml",
        ]

        for path in script_paths:
            if path.exists():
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        self.script_content = f.read().lower()
                    self.result.info.append(f"Loaded script: {path.name}")
                    break
                except Exception as e:
                    self.result.warnings.append(f"Failed to read {path.name}: {e}")

        if not self.script_content:
            self.result.script_errors.append("No SSML script found")
            return

        # Extract sections
        self._extract_script_sections()

    def _extract_script_sections(self):
        """Extract content for each section from script."""
        # Find section markers
        section_patterns = [
            (r'<!-- section 1.*?-->(.*?)(?=<!-- section 2|$)', 'pretalk'),
            (r'<!-- section 2.*?-->(.*?)(?=<!-- section 3|$)', 'induction'),
            (r'<!-- section 3.*?-->(.*?)(?=<!-- section 4|$)', 'journey'),
            (r'<!-- section 4.*?-->(.*?)(?=<!-- section 5|$)', 'integration'),
            (r'<!-- section 5.*?-->(.*?)(?=</speak>|$)', 'closing'),
        ]

        for pattern, section_id in section_patterns:
            match = re.search(pattern, self.script_content, re.DOTALL | re.IGNORECASE)
            if match:
                self.script_sections[section_id] = match.group(1)

    def _validate_manifest(self):
        """Validate manifest has all required fields."""
        print("\n[Manifest Validation]")

        # Required top-level sections
        required_sections = ["session", "voice", "sections"]
        for section in required_sections:
            if section not in self.manifest:
                self.result.manifest_errors.append(f"Missing required section: {section}")
                print(f"  ✗ Missing section: {section}")
            else:
                print(f"  ✓ Has section: {section}")

        # Session fields
        if "session" in self.manifest:
            session = self.manifest["session"]
            required_fields = ["name", "duration"]
            for field in required_fields:
                if field not in session:
                    self.result.manifest_errors.append(f"Missing session.{field}")

        # Voice settings
        if "voice" in self.manifest:
            voice = self.manifest["voice"]
            if voice.get("voice_name") != "en-US-Neural2-H":
                self.result.warnings.append(
                    f"Non-standard voice: {voice.get('voice_name')} "
                    f"(standard is en-US-Neural2-H)"
                )

        # Sections defined
        if "sections" in self.manifest:
            manifest_sections = self.manifest["sections"]
            if len(manifest_sections) < 5:
                self.result.manifest_errors.append(
                    f"Only {len(manifest_sections)} sections defined (need 5)"
                )

        # Voice enhancement
        if "voice_enhancement" in self.manifest:
            ve = self.manifest["voice_enhancement"]
            if not ve.get("enabled", False):
                self.result.audio_errors.append("voice_enhancement not enabled")
            else:
                for setting in VOICE_ENHANCEMENT_REQUIRED:
                    if setting not in ve:
                        self.result.audio_errors.append(
                            f"Missing voice_enhancement.{setting}"
                        )
        else:
            self.result.warnings.append("No voice_enhancement section in manifest")

    def _validate_script_sections(self):
        """Validate all 5 sections are present with correct markers."""
        print("\n[Section Markers]")

        for section_id, marker, min_dur, max_dur in MANDATORY_SECTIONS:
            # Check for section marker
            pattern = rf'<!-- section.*{marker}'
            match = re.search(pattern, self.script_content, re.IGNORECASE)

            section_val = SectionValidation(
                section_id=section_id,
                section_name=marker,
                present=match is not None,
                duration_valid=True
            )

            if match:
                print(f"  ✓ {marker}")

                # Check duration from manifest
                if "sections" in self.manifest:
                    for ms in self.manifest["sections"]:
                        if ms.get("name", "").lower() == section_id:
                            start = ms.get("start", 0)
                            end = ms.get("end", 0)
                            duration_min = (end - start) / 60
                            section_val.duration_actual = duration_min

                            if duration_min < min_dur or duration_min > max_dur:
                                section_val.duration_valid = False
                                self.result.warnings.append(
                                    f"{marker} duration {duration_min:.1f}min "
                                    f"(standard: {min_dur}-{max_dur}min)"
                                )
            else:
                print(f"  ✗ {marker} - MISSING")
                self.result.script_errors.append(f"Missing section marker: {marker}")

            self.result.sections.append(section_val)

    def _validate_script_elements(self):
        """Validate required elements within each section."""
        print("\n[Section Content Validation]")

        # Validate Pre-Talk elements
        if "pretalk" in self.script_sections or self.script_content:
            content = self.script_sections.get("pretalk", self.script_content[:3000])
            print("\n  Pre-Talk Elements:")
            self._validate_elements(content, PRETALK_ELEMENTS, "pretalk", required=True)

        # Validate Induction elements
        if "induction" in self.script_sections:
            content = self.script_sections["induction"]
            print("\n  Induction Elements:")
            self._validate_elements(content, INDUCTION_ELEMENTS, "induction", required=True)

        # Validate Journey senses
        if "journey" in self.script_sections:
            content = self.script_sections["journey"]
            print("\n  Journey Sensory Coverage:")
            self._validate_elements(content, JOURNEY_SENSES, "journey", required=False)

        # Validate Integration elements
        if "integration" in self.script_sections:
            content = self.script_sections["integration"]
            print("\n  Integration Elements:")
            self._validate_elements(content, INTEGRATION_ELEMENTS, "integration", required=True)

        # Validate Closing elements
        if "closing" in self.script_sections or self.script_content:
            content = self.script_sections.get("closing", self.script_content[-4000:])
            print("\n  Closing Elements:")
            self._validate_elements(content, CLOSING_ELEMENTS, "closing", required=True)

    def _validate_elements(self, content: str, elements: Dict, section: str, required: bool):
        """Validate specific elements are present in content."""
        for element_id, (pattern, description) in elements.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            count = len(matches)
            present = count > 0

            result = ValidationResult(
                element=element_id,
                required=required,
                present=present,
                description=description,
                count=count
            )

            # Find corresponding section validation
            for sv in self.result.sections:
                if sv.section_id == section:
                    sv.elements.append(result)
                    break

            if present:
                print(f"    ✓ {description} ({count} instances)")
            else:
                marker = "✗" if required else "○"
                print(f"    {marker} {description} - MISSING")
                if required:
                    self.result.script_errors.append(
                        f"[{section}] Missing: {description}"
                    )
                else:
                    self.result.warnings.append(
                        f"[{section}] Consider adding: {description}"
                    )

    def _validate_audio_settings(self):
        """Validate audio configuration in manifest."""
        print("\n[Audio Settings]")

        # Check binaural configuration
        if "sound_bed" in self.manifest:
            sb = self.manifest["sound_bed"]
            if "binaural" in sb:
                binaural = sb["binaural"]
                if not binaural.get("enabled", False):
                    self.result.audio_errors.append("Binaural beats not enabled")
                    print("  ✗ Binaural: DISABLED")
                else:
                    print("  ✓ Binaural: enabled")
                    base_hz = binaural.get("base_hz", 200)
                    print(f"    Carrier: {base_hz} Hz")
            else:
                self.result.audio_errors.append("No binaural configuration")
        else:
            self.result.warnings.append("No sound_bed configuration in manifest")

        # Check mastering settings
        if "mastering" in self.manifest:
            mastering = self.manifest["mastering"]
            target_lufs = mastering.get("target_lufs", -14)
            true_peak = mastering.get("true_peak_dbtp", -1.5)
            print(f"  ✓ Mastering: {target_lufs} LUFS, {true_peak} dBTP")

            if target_lufs != -14:
                self.result.warnings.append(
                    f"Non-standard LUFS target: {target_lufs} (standard: -14)"
                )

    def _validate_output_files(self):
        """Validate expected output files exist."""
        print("\n[Output Files]")

        output_dir = self.session_path / "output"
        if not output_dir.exists():
            self.result.file_errors.append("No output/ directory")
            return

        expected_files = [
            ("voice_enhanced.mp3", True, "Enhanced voice (production)"),
            ("voice.mp3", False, "Raw TTS voice"),
            ("session_mixed.wav", False, "Mixed session"),
        ]

        for filename, required, description in expected_files:
            path = output_dir / filename
            if path.exists():
                print(f"  ✓ {filename}")
            else:
                if required:
                    self.result.file_errors.append(f"Missing: {filename}")
                    print(f"  ✗ {filename} - MISSING (required)")
                else:
                    print(f"  ○ {filename} - not present")

    def _calculate_metrics(self):
        """Calculate metrics for cross-session comparison."""
        # Word count (strip SSML tags)
        if self.script_content:
            text_only = re.sub(r'<[^>]+>', '', self.script_content)
            text_only = re.sub(r'\[sfx:[^\]]+\]', '', text_only, flags=re.IGNORECASE)
            words = text_only.split()
            self.result.word_count = len(words)

        # Count anchors
        anchor_patterns = [
            r'whenever you',
            r'each time you',
            r'every time you',
            r'when you notice',
            r'when you feel',
        ]
        for pattern in anchor_patterns:
            self.result.anchor_count += len(re.findall(pattern, self.script_content))

        # Count senses covered
        sense_count = 0
        for sense, (pattern, _) in JOURNEY_SENSES.items():
            if re.search(pattern, self.script_content):
                sense_count += 1
        self.result.sense_coverage = sense_count

        # Count deepening phrases
        deepening_pattern = r'(deeper|deep|descend|drift|float|sink)'
        self.result.deepening_count = len(re.findall(deepening_pattern, self.script_content))

        # Count breaks
        break_pattern = r'<break[^>]*>'
        self.result.break_count = len(re.findall(break_pattern, self.script_content))

    def get_report(self) -> str:
        """Generate formatted validation report."""
        lines = [
            f"\n{'='*70}",
            f"VALIDATION REPORT: {self.session_name}",
            f"Path: {self.session_path}",
            f"{'='*70}",
        ]

        # Errors
        if self.result.manifest_errors:
            lines.append("\n[MANIFEST ERRORS]")
            for err in self.result.manifest_errors:
                lines.append(f"  ✗ {err}")

        if self.result.script_errors:
            lines.append("\n[SCRIPT ERRORS]")
            for err in self.result.script_errors:
                lines.append(f"  ✗ {err}")

        if self.result.audio_errors:
            lines.append("\n[AUDIO ERRORS]")
            for err in self.result.audio_errors:
                lines.append(f"  ✗ {err}")

        if self.result.file_errors:
            lines.append("\n[FILE ERRORS]")
            for err in self.result.file_errors:
                lines.append(f"  ✗ {err}")

        # Warnings
        if self.result.warnings:
            lines.append("\n[WARNINGS]")
            for warn in self.result.warnings:
                lines.append(f"  ⚠ {warn}")

        # Metrics
        lines.append("\n[METRICS]")
        lines.append(f"  Word count: {self.result.word_count}")
        lines.append(f"  Anchors: {self.result.anchor_count}")
        lines.append(f"  Senses covered: {self.result.sense_coverage}/5")
        lines.append(f"  Deepening phrases: {self.result.deepening_count}")
        lines.append(f"  Break tags: {self.result.break_count}")

        # Status
        status = "✓ VALID" if self.result.valid else "✗ INVALID"
        lines.append(f"\n{'='*70}")
        lines.append(f"STATUS: {status}")
        lines.append(f"{'='*70}")

        return "\n".join(lines)


# =============================================================================
# CROSS-SESSION COMPARISON
# =============================================================================

class CrossSessionComparator:
    """Compares multiple sessions for consistency."""

    def __init__(self, results: List[SessionValidation]):
        self.results = results

    def analyze(self) -> Dict[str, Any]:
        """Analyze consistency across sessions."""
        analysis = {
            "total_sessions": len(self.results),
            "valid_sessions": sum(1 for r in self.results if r.valid),
            "metrics": self._analyze_metrics(),
            "common_issues": self._find_common_issues(),
            "outliers": self._find_outliers(),
        }
        return analysis

    def _analyze_metrics(self) -> Dict[str, Dict[str, float]]:
        """Calculate metric statistics."""
        metrics = {}

        # Word count
        word_counts = [r.word_count for r in self.results if r.word_count > 0]
        if word_counts:
            metrics["word_count"] = {
                "mean": sum(word_counts) / len(word_counts),
                "min": min(word_counts),
                "max": max(word_counts),
                "target": 3750,
            }

        # Anchor count
        anchor_counts = [r.anchor_count for r in self.results]
        if anchor_counts:
            metrics["anchor_count"] = {
                "mean": sum(anchor_counts) / len(anchor_counts),
                "min": min(anchor_counts),
                "max": max(anchor_counts),
                "target_min": 3,
                "target_max": 5,
            }

        # Sense coverage
        sense_counts = [r.sense_coverage for r in self.results]
        if sense_counts:
            metrics["sense_coverage"] = {
                "mean": sum(sense_counts) / len(sense_counts),
                "min": min(sense_counts),
                "max": max(sense_counts),
                "target": 5,
            }

        return metrics

    def _find_common_issues(self) -> List[Tuple[str, int]]:
        """Find issues that appear across multiple sessions."""
        issue_counts: Dict[str, int] = {}

        for result in self.results:
            all_issues = (
                result.manifest_errors +
                result.script_errors +
                result.audio_errors +
                result.file_errors
            )
            for issue in all_issues:
                # Normalize issue text
                normalized = re.sub(r'\d+', 'N', issue)
                issue_counts[normalized] = issue_counts.get(normalized, 0) + 1

        # Sort by frequency
        sorted_issues = sorted(issue_counts.items(), key=lambda x: -x[1])
        return sorted_issues[:10]  # Top 10

    def _find_outliers(self) -> Dict[str, List[str]]:
        """Find sessions that deviate significantly from norms."""
        outliers = {
            "low_word_count": [],
            "high_word_count": [],
            "low_anchors": [],
            "missing_senses": [],
        }

        # Calculate thresholds
        word_counts = [r.word_count for r in self.results if r.word_count > 0]
        if word_counts:
            avg_words = sum(word_counts) / len(word_counts)

            for result in self.results:
                if result.word_count < avg_words * 0.7:
                    outliers["low_word_count"].append(result.session_name)
                elif result.word_count > avg_words * 1.3:
                    outliers["high_word_count"].append(result.session_name)

                if result.anchor_count < 3:
                    outliers["low_anchors"].append(result.session_name)

                if result.sense_coverage < 4:
                    outliers["missing_senses"].append(result.session_name)

        return outliers

    def get_report(self) -> str:
        """Generate cross-session comparison report."""
        analysis = self.analyze()

        lines = [
            f"\n{'='*70}",
            "CROSS-SESSION CONSISTENCY REPORT",
            f"{'='*70}",
            f"\nTotal Sessions: {analysis['total_sessions']}",
            f"Valid Sessions: {analysis['valid_sessions']}",
            f"Compliance Rate: {analysis['valid_sessions']/analysis['total_sessions']*100:.1f}%",
        ]

        # Metrics
        lines.append("\n[METRIC ANALYSIS]")
        for metric_name, stats in analysis["metrics"].items():
            lines.append(f"\n  {metric_name}:")
            for stat_name, value in stats.items():
                lines.append(f"    {stat_name}: {value:.1f}" if isinstance(value, float) else f"    {stat_name}: {value}")

        # Common issues
        if analysis["common_issues"]:
            lines.append("\n[COMMON ISSUES]")
            for issue, count in analysis["common_issues"]:
                lines.append(f"  ({count}x) {issue}")

        # Outliers
        lines.append("\n[OUTLIER SESSIONS]")
        outliers = analysis["outliers"]
        for category, sessions in outliers.items():
            if sessions:
                lines.append(f"\n  {category}:")
                for s in sessions:
                    lines.append(f"    - {s}")

        lines.append(f"\n{'='*70}")

        return "\n".join(lines)


# =============================================================================
# MAIN
# =============================================================================

def find_all_sessions(project_root: Path) -> List[Path]:
    """Find all session directories."""
    sessions_dir = project_root / "sessions"
    if not sessions_dir.exists():
        return []
    return [
        d for d in sessions_dir.iterdir()
        if d.is_dir() and d.name != "_template" and not d.name.startswith(".")
    ]


def get_project_root() -> Path:
    """Find project root."""
    script_path = Path(__file__).resolve()
    # Go up from scripts/utilities/ to project root
    return script_path.parent.parent.parent


def main():
    parser = argparse.ArgumentParser(
        description="Validate hypnotic session against production standards"
    )
    parser.add_argument(
        "session",
        nargs="?",
        help="Path to session directory"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Validate all sessions"
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Include cross-session consistency analysis"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate detailed compliance report"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    args = parser.parse_args()

    if not args.session and not args.all:
        parser.print_help()
        sys.exit(1)

    project_root = get_project_root()

    if args.all:
        sessions = find_all_sessions(project_root)
    else:
        sessions = [Path(args.session)]

    if not sessions:
        print("No sessions found")
        sys.exit(0)

    # Validate all sessions
    results = []
    for session_path in sessions:
        validator = HypnoticStandardsValidator(session_path)
        result = validator.validate()
        results.append(result)
        print(validator.get_report())

    # Cross-session comparison
    if args.compare and len(results) > 1:
        comparator = CrossSessionComparator(results)
        print(comparator.get_report())

    # Summary
    valid_count = sum(1 for r in results if r.valid)
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"Sessions validated: {len(results)}")
    print(f"Valid sessions: {valid_count}/{len(results)}")
    print(f"Compliance rate: {valid_count/len(results)*100:.1f}%")

    # JSON output
    if args.json:
        output = {
            "timestamp": datetime.now().isoformat(),
            "sessions": [
                {
                    "name": r.session_name,
                    "valid": r.valid,
                    "errors": r.manifest_errors + r.script_errors + r.audio_errors + r.file_errors,
                    "warnings": r.warnings,
                    "metrics": {
                        "word_count": r.word_count,
                        "anchor_count": r.anchor_count,
                        "sense_coverage": r.sense_coverage,
                    }
                }
                for r in results
            ]
        }
        print("\n" + json.dumps(output, indent=2))

    # Exit code
    sys.exit(0 if valid_count == len(results) else 1)


if __name__ == "__main__":
    main()
