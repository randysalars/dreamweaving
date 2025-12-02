#!/usr/bin/env python3
"""
NLP and Hypnotic Pattern Validation for Dreamweaving Scripts

This script validates that SSML scripts contain the required:
- Script structure (5 mandatory sections)
- NLP patterns (embedded commands, presuppositions, etc.)
- Sensory language (all 5 senses engaged)
- Post-hypnotic anchors
- Positive, empowering language

Usage:
    python validate_nlp.py script.ssml
    python validate_nlp.py script.ssml --verbose
    python validate_nlp.py script.ssml --report

Based on: prompts/hypnotic_dreamweaving_instructions.md
"""

import re
import sys
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional


# =============================================================================
# VALIDATION REQUIREMENTS
# =============================================================================

REQUIRED_SECTIONS = [
    ('PRE-TALK', 'PRETALK', 'PRE_TALK', 'SECTION 1'),
    ('INDUCTION', 'SECTION 2'),
    ('JOURNEY', 'MAIN JOURNEY', 'VISUALIZATION', 'SECTION 3'),
    ('INTEGRATION', 'RETURN', 'SECTION 4'),
    ('AWAKENING', 'CLOSING', 'SECTION 5'),
]

NLP_PATTERNS = {
    'embedded_commands': {
        'min_count': 5,
        'patterns': [
            r'<emphasis[^>]*>([^<]+)</emphasis>',  # Emphasized text
        ],
        'examples': [
            'you can <emphasis>relax deeply</emphasis> now',
            '<emphasis>let go completely</emphasis>',
        ],
        'description': 'Emphasized commands that slip past conscious awareness'
    },
    'presuppositions': {
        'min_count': 3,
        'patterns': [
            r'as you continue',
            r'while you\s+\w+',
            r'when you notice',
            r'the more you.*the more',
            r'as you\s+\w+',
            r'notice how',
            r'perhaps you\'ve already',
            r'you may already',
            r'beginning to',
        ],
        'description': 'Assumptions that desired state is already occurring'
    },
    'future_pacing': {
        'min_count': 2,
        'patterns': [
            r'in the days ahead',
            r'you\'ll find yourself',
            r'you\'ll notice',
            r'in the coming days',
            r'each time you',
            r'whenever you',
            r'from now on',
            r'in the future',
        ],
        'description': 'Connecting present experience to future behavior'
    },
    'truisms': {
        'min_count': 1,
        'patterns': [
            r'everyone knows',
            r'we all know',
            r'it\'s natural to',
            r'you already know',
            r'as you know',
            r'naturally',
        ],
        'description': 'Undeniable facts that build agreement'
    },
}

SENSORY_PATTERNS = {
    'visual': {
        'min_count': 3,
        'patterns': [
            r'\bsee\b', r'\bseeing\b', r'\bnotice\b', r'\blight\b',
            r'\bcolor', r'\bbright', r'\bshine', r'\bglow',
            r'\bimagine\b', r'\bvision\b', r'\bwatch\b', r'\blook\b',
            r'\bappear', r'\bview\b', r'\bpicture\b',
        ],
        'description': 'Visual/sight-related language'
    },
    'auditory': {
        'min_count': 3,
        'patterns': [
            r'\bhear\b', r'\bhearing\b', r'\bsound\b', r'\bvoice\b',
            r'\btone\b', r'\bsilence\b', r'\bwhisper', r'\blisten\b',
            r'\becho\b', r'\bchime\b', r'\bmusic\b', r'\brhythm\b',
        ],
        'description': 'Auditory/sound-related language'
    },
    'kinesthetic': {
        'min_count': 3,
        'patterns': [
            r'\bfeel\b', r'\bfeeling\b', r'\btouch\b', r'\bwarm',
            r'\bheavy\b', r'\blight\b', r'\brelax', r'\btingle',
            r'\bsensation\b', r'\bcomfort', r'\bsoft\b', r'\bsmooth',
            r'\bpressure\b', r'\bfloat',
        ],
        'description': 'Kinesthetic/feeling-related language'
    },
    'olfactory': {
        'min_count': 1,
        'patterns': [
            r'\bsmell\b', r'\bscent\b', r'\bfragrance\b', r'\baroma\b',
            r'\bperfume\b', r'\bincense\b', r'\bflowers?\b.*\bscent',
        ],
        'description': 'Olfactory/smell-related language'
    },
    'gustatory': {
        'min_count': 0,  # Optional
        'patterns': [
            r'\btaste\b', r'\bsweet\b', r'\bnectar\b', r'\bhoney\b',
            r'\bcrystalline water\b',
        ],
        'description': 'Gustatory/taste-related language (optional)'
    },
}

ANCHOR_PATTERNS = {
    'min_count': 3,
    'physical': [
        r'each time you take.*breath',
        r'whenever you.*breathe',
        r'when you.*touch',
        r'as you.*move',
    ],
    'symbolic': [
        r'whenever you recall',
        r'when you think of',
        r'when you remember',
        r'the image of',
        r'the symbol of',
    ],
    'sensory': [
        r'when you notice.*sensation',
        r'when you feel.*warmth',
        r'whenever you.*feel',
        r'that feeling of',
    ],
    'description': 'Triggers for reinstating hypnotic states'
}

NEGATIVE_PATTERNS = [
    r'\bdon\'t\b.*\bworry\b',  # "don't worry" - negative framing
    r'\bno\s+\w+\s+can\b',
    r'\bnever\s+\w+\s+again\b',
    r'\bfear\b',
    r'\banxious\b',
    r'\bpanic\b',
    r'\bterror\b',
    r'\bdread\b',
    r'\bhurt\b',
    r'\bpain\b(?!ting)',  # pain but not painting
    r'\bsuffering\b',
]


@dataclass
class ValidationResult:
    """Result of a single validation check."""
    name: str
    passed: bool
    found: int
    required: int
    details: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


@dataclass
class ValidationReport:
    """Complete validation report."""
    script_path: str
    passed: bool
    checks: Dict[str, ValidationResult] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    summary: str = ""


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def validate_structure(content: str) -> ValidationResult:
    """Validate that all 5 required sections are present."""
    found_sections = []
    missing_sections = []

    for section_names in REQUIRED_SECTIONS:
        found = False
        for name in section_names:
            pattern = rf'(?:<!--|SECTION|#)\s*{re.escape(name)}'
            if re.search(pattern, content, re.IGNORECASE):
                found = True
                found_sections.append(section_names[0])
                break

        if not found:
            missing_sections.append(section_names[0])

    passed = len(missing_sections) == 0

    result = ValidationResult(
        name="Script Structure",
        passed=passed,
        found=len(found_sections),
        required=len(REQUIRED_SECTIONS),
        details=[f"Found sections: {', '.join(found_sections)}"]
    )

    if missing_sections:
        result.suggestions = [f"Add missing sections: {', '.join(missing_sections)}"]

    return result


def validate_nlp_patterns(content: str) -> Dict[str, ValidationResult]:
    """Validate NLP pattern requirements."""
    results = {}
    content_lower = content.lower()

    for pattern_name, config in NLP_PATTERNS.items():
        matches = []
        for pattern in config['patterns']:
            for match in re.finditer(pattern, content_lower):
                matches.append(match.group(0)[:50])  # First 50 chars

        passed = len(matches) >= config['min_count']

        result = ValidationResult(
            name=pattern_name,
            passed=passed,
            found=len(matches),
            required=config['min_count'],
            details=matches[:5]  # Show first 5 matches
        )

        if not passed:
            result.suggestions = [
                f"Add more {pattern_name}: found {len(matches)}, need {config['min_count']}",
                f"Description: {config['description']}"
            ]
            if 'examples' in config:
                result.suggestions.append(f"Examples: {config['examples'][:2]}")

        results[pattern_name] = result

    return results


def validate_sensory_language(content: str) -> Dict[str, ValidationResult]:
    """Validate sensory language engagement."""
    results = {}
    content_lower = content.lower()

    for sense, config in SENSORY_PATTERNS.items():
        matches = []
        for pattern in config['patterns']:
            for match in re.finditer(pattern, content_lower):
                matches.append(match.group(0))

        # Remove duplicates
        matches = list(set(matches))

        passed = len(matches) >= config['min_count']

        result = ValidationResult(
            name=f"sensory_{sense}",
            passed=passed,
            found=len(matches),
            required=config['min_count'],
            details=matches[:5]
        )

        if not passed and config['min_count'] > 0:
            result.suggestions = [
                f"Add more {sense} language: found {len(matches)}, need {config['min_count']}",
                f"Description: {config['description']}"
            ]

        results[sense] = result

    return results


def validate_anchors(content: str) -> ValidationResult:
    """Validate post-hypnotic anchors."""
    content_lower = content.lower()
    anchor_types_found = []
    all_matches = []

    for anchor_type in ['physical', 'symbolic', 'sensory']:
        patterns = ANCHOR_PATTERNS[anchor_type]
        for pattern in patterns:
            if re.search(pattern, content_lower):
                anchor_types_found.append(anchor_type)
                for match in re.finditer(pattern, content_lower):
                    all_matches.append(f"[{anchor_type}] {match.group(0)[:40]}")
                break

    passed = len(set(anchor_types_found)) >= ANCHOR_PATTERNS['min_count']

    result = ValidationResult(
        name="Post-Hypnotic Anchors",
        passed=passed,
        found=len(set(anchor_types_found)),
        required=ANCHOR_PATTERNS['min_count'],
        details=all_matches[:5]
    )

    if not passed:
        missing = [t for t in ['physical', 'symbolic', 'sensory']
                   if t not in anchor_types_found]
        result.suggestions = [
            f"Need {ANCHOR_PATTERNS['min_count']} anchor types, found {len(set(anchor_types_found))}",
            f"Missing anchor types: {', '.join(missing)}"
        ]

    return result


def validate_positive_language(content: str) -> ValidationResult:
    """Check for negative/fear-based language."""
    content_lower = content.lower()
    negative_matches = []

    for pattern in NEGATIVE_PATTERNS:
        for match in re.finditer(pattern, content_lower):
            context_start = max(0, match.start() - 20)
            context_end = min(len(content_lower), match.end() + 20)
            context = content_lower[context_start:context_end]
            negative_matches.append(f"'{context.strip()}'")

    passed = len(negative_matches) == 0

    result = ValidationResult(
        name="Positive Language",
        passed=passed,
        found=len(negative_matches),
        required=0,  # Should be 0 negatives
        details=negative_matches[:5]
    )

    if not passed:
        result.suggestions = [
            "Replace negative language with positive alternatives",
            "Reframe using positive suggestions (what TO do, not what NOT to do)"
        ]

    return result


# =============================================================================
# MAIN VALIDATION
# =============================================================================

def validate_script(script_path: str, verbose: bool = False) -> ValidationReport:
    """
    Run complete validation on an SSML script.

    Args:
        script_path: Path to SSML file
        verbose: Show detailed output

    Returns:
        ValidationReport with all results
    """
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()

    report = ValidationReport(
        script_path=script_path,
        passed=True,
        checks={}
    )

    # Structure validation
    structure_result = validate_structure(content)
    report.checks['structure'] = structure_result
    if not structure_result.passed:
        report.passed = False

    # NLP patterns
    nlp_results = validate_nlp_patterns(content)
    for name, result in nlp_results.items():
        report.checks[f'nlp_{name}'] = result
        if not result.passed:
            report.passed = False

    # Sensory language
    sensory_results = validate_sensory_language(content)
    for name, result in sensory_results.items():
        report.checks[f'sensory_{name}'] = result
        if not result.passed and SENSORY_PATTERNS[name]['min_count'] > 0:
            report.passed = False

    # Anchors
    anchor_result = validate_anchors(content)
    report.checks['anchors'] = anchor_result
    if not anchor_result.passed:
        report.passed = False

    # Positive language
    positive_result = validate_positive_language(content)
    report.checks['positive_language'] = positive_result
    if not positive_result.passed:
        report.warnings.append("Contains potentially negative language")

    # Generate summary
    passed_count = sum(1 for r in report.checks.values() if r.passed)
    total_count = len(report.checks)
    report.summary = f"{passed_count}/{total_count} checks passed"

    return report


def print_report(report: ValidationReport, verbose: bool = False):
    """Print validation report to console."""
    print("=" * 70)
    print("NLP & HYPNOTIC PATTERN VALIDATION")
    print("=" * 70)
    print(f"\nScript: {report.script_path}")
    print(f"Result: {'✅ PASSED' if report.passed else '❌ FAILED'}")
    print(f"Summary: {report.summary}")
    print()

    # Group by category
    categories = {
        'Structure': ['structure'],
        'NLP Patterns': [k for k in report.checks if k.startswith('nlp_')],
        'Sensory Language': [k for k in report.checks if k.startswith('sensory_')],
        'Anchors': ['anchors'],
        'Language Quality': ['positive_language'],
    }

    for category, check_keys in categories.items():
        print(f"\n{category}:")
        print("-" * 40)

        for key in check_keys:
            if key in report.checks:
                result = report.checks[key]
                status = "✅" if result.passed else "❌"
                name = result.name.replace('_', ' ').title()
                print(f"  {status} {name}: {result.found}/{result.required}")

                if verbose and result.details:
                    for detail in result.details[:3]:
                        print(f"      - {detail}")

                if not result.passed and result.suggestions:
                    for suggestion in result.suggestions[:2]:
                        print(f"      💡 {suggestion}")

    if report.warnings:
        print("\n⚠️  WARNINGS:")
        for warning in report.warnings:
            print(f"  - {warning}")

    print()


# =============================================================================
# CLI
# =============================================================================

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate NLP and hypnotic patterns in SSML scripts"
    )
    parser.add_argument('script', help="Path to SSML script file")
    parser.add_argument('-v', '--verbose', action='store_true',
                       help="Show detailed matches")
    parser.add_argument('--report', action='store_true',
                       help="Output JSON report")

    args = parser.parse_args()

    if not Path(args.script).exists():
        print(f"Error: File not found: {args.script}")
        sys.exit(1)

    report = validate_script(args.script, args.verbose)

    if args.report:
        # JSON output
        output = {
            'script_path': report.script_path,
            'passed': report.passed,
            'summary': report.summary,
            'checks': {
                name: {
                    'passed': result.passed,
                    'found': result.found,
                    'required': result.required,
                    'suggestions': result.suggestions
                }
                for name, result in report.checks.items()
            },
            'warnings': report.warnings
        }
        print(json.dumps(output, indent=2))
    else:
        print_report(report, args.verbose)

    sys.exit(0 if report.passed else 1)
