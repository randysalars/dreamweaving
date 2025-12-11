#!/usr/bin/env python3
"""
Christ-Centered Validation Utility v1.0

Validates that dreamweaving scripts maintain Christ-centered theological boundaries
based on the framework at salars.net/dreamweaving/forbidden_knowledge.

HARD FAIL conditions:
- Spirit invocation language
- Entity summoning/communication
- Passive will / empty mind states
- Archetypes treated as literal beings
- Spiritual authority granted to non-Christ sources

WARNING conditions:
- Missing Christ-centered language
- Unframed archetypes
- Ambiguous guide references
- Passive relaxation without agency balance

REQUIRED elements:
- Safety/consent clause (first 500 words)
- Will engagement language (3+ occurrences)
- Christ anchor (for Christian-framework sessions)
- Archetype metaphor framing (when archetypes used)
- Discernment affirmation

Usage:
    python scripts/utilities/validate_christ_centered.py path/to/session/
    python scripts/utilities/validate_christ_centered.py path/to/session/ --verbose
    python scripts/utilities/validate_christ_centered.py path/to/session/ --strict
"""

import sys
import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ValidationResult:
    """Holds the result of a validation check."""
    valid: bool = True
    hard_fails: List[Dict] = field(default_factory=list)
    warnings: List[Dict] = field(default_factory=list)
    required_missing: List[Dict] = field(default_factory=list)
    required_present: List[Dict] = field(default_factory=list)
    suggested_alternatives: List[Dict] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def add_hard_fail(self, category: str, pattern: str, match: str, location: int, rationale: str):
        self.valid = False
        self.hard_fails.append({
            'category': category,
            'pattern': pattern,
            'match': match,
            'location': location,
            'rationale': rationale
        })

    def add_warning(self, category: str, message: str, suggestion: str = None):
        self.warnings.append({
            'category': category,
            'message': message,
            'suggestion': suggestion
        })

    def add_required_missing(self, name: str, description: str, examples: List[str]):
        self.valid = False  # Missing required = failure
        self.required_missing.append({
            'name': name,
            'description': description,
            'examples': examples
        })

    def add_required_present(self, name: str, count: int):
        self.required_present.append({
            'name': name,
            'occurrences': count
        })


# =============================================================================
# PATTERN DEFINITIONS
# =============================================================================

FORBIDDEN_PATTERNS = {
    'spirit_invocation': {
        'description': 'Spirit invocation or summoning language',
        'severity': 'HARD_FAIL',
        'rationale': 'Dreamweaving must NOT summon entities or invoke energies',
        'patterns': [
            r'invoke\s+(the\s+)?(spirit|entity|being|presence)\s+of',
            r'summon\s+(forth|the)\s+',
            r'call\s+(forth|upon)\s+(the\s+)?(spirit|entity|demon|angel)',
            r'i\s+invoke\s+thee',
            r'we\s+invoke\s+thee',
            r'come\s+(to\s+me|forth),?\s+(spirit|entity)',
            r'i\s+summon\s+',
            r'by\s+the\s+power\s+of\s+(?!christ|jesus|god|the\s+lord)',
            # "in the name of X" where X is not Christ/God/Lord/Holy Spirit
            r'in\s+the\s+name\s+of\s+(?!jesus|christ|god|the\s+father|the\s+lord|the\s+holy\s+spirit|father)[a-z]+',
        ]
    },
    'entity_communication': {
        'description': 'Language encouraging dialogue with unknown spiritual entities',
        'severity': 'HARD_FAIL',
        'rationale': 'Only the Holy Spirit should be acknowledged as divine guide',
        'patterns': [
            r'let\s+(something|a\s+being|an?\s+entity)\s+speak\s+through\s+you',
            r'allow\s+(a|the)\s+(spirit|being|entity|presence)\s+to\s+(guide|speak|enter)',
            r'open\s+yourself\s+to\s+whoever\s+speaks',
            r'whoever\s+(or\s+whatever\s+)?appears.*speak\s+to\s+you',
            r'let\s+the\s+(guide|being|spirit)\s+use\s+your\s+voice',
            r'channel\s+(the\s+)?(spirit|being|entity|message)',
            r'become\s+a\s+(vessel|channel)\s+for',
            r'receive\s+messages?\s+from\s+(the\s+)?(spirits?|entities|beings)',
        ]
    },
    'passive_will': {
        'description': 'Language that dissolves will, agency, or creates empty-mind vulnerability',
        'severity': 'HARD_FAIL',
        'rationale': 'Empty-mind states dissolve discernment and create vulnerability',
        'patterns': [
            r'empty\s+your\s+mind\s+(completely|entirely|fully)',
            r'become\s+(completely\s+)?empty\s+(and\s+)?receptive',
            r'surrender\s+(your\s+)?will\s+(completely|entirely|to)',
            r'let\s+go\s+of\s+(all\s+)?control\s+(completely|entirely)',
            r'dissolve\s+(all\s+)?(boundaries|self|ego)\s+(completely|entirely)',
            r'become\s+nothing\s+(but|except)',
            r'lose\s+yourself\s+(completely|entirely|fully)',
            r'no\s+longer\s+exist\s+as\s+(yourself|you|an?\s+individual)',
            r'cease\s+to\s+(be|exist)',
            r'your\s+will\s+(no\s+longer|is\s+not)\s+(your|yours)',
        ]
    },
    'archetypes_literal': {
        'description': 'Treating psychological archetypes as literal spiritual entities',
        'severity': 'HARD_FAIL',
        'rationale': 'Archetypes are psychological metaphors, not literal beings',
        'patterns': [
            r'(the\s+)?(archetype|anima|animus|shadow)\s+(is|are)\s+(a\s+)?(real|literal|actual)\s+(being|entity|spirit)',
            r'worship\s+(the\s+)?(archetype|anima|animus|shadow)',
            r'(archetype|anima|animus)\s+(has|have)\s+(spiritual\s+)?authority\s+over',
            r'pledge\s+(yourself|allegiance)\s+to\s+(the\s+)?(archetype|anima|animus|shadow)',
            r'serve\s+(the\s+)?(archetype|guide|being)\s+as\s+(your\s+)?(master|lord)',
            r'(the\s+)?(archetype|anima|animus)\s+commands\s+you\s+to',
            r'obey\s+(the\s+)?(archetype|anima|animus|shadow)',
        ]
    },
    'false_authority': {
        'description': 'Granting spiritual authority to symbols, objects, or non-Christ entities',
        'severity': 'HARD_FAIL',
        'rationale': 'Only Christ has ultimate spiritual authority',
        'patterns': [
            r'(this\s+)?(symbol|sigil|object|element)\s+(has|holds|possesses)\s+(power|authority)\s+over',
            r'grant\s+(this|the)\s+(symbol|object|element)\s+power\s+over\s+you',
            r'the\s+(elements?|directions?|ancestors?)\s+(have|has)\s+authority\s+over',
            r'submit\s+(yourself\s+)?to\s+(the\s+)?(symbol|sigil|element|direction)',
            r'the\s+(pentagram|triangle|circle|sigil)\s+protects?\s+you\s+from',
            r'swear\s+(allegiance|loyalty)\s+to\s+(the\s+)?(symbol|element|direction)',
        ]
    }
}

REQUIRED_PATTERNS = {
    'safety_clause': {
        'description': 'Explicit statement that listener maintains control',
        'severity': 'HARD_FAIL',
        'min_occurrences': 1,
        'placement': 'first_500_words',
        'patterns': [
            r'you\s+(remain|stay)\s+(in\s+)?(complete\s+)?(control|charge)',
            r'you\s+can\s+(return|come\s+back|awaken)\s+at\s+any\s+time',
            r'at\s+any\s+moment.*can.*(return|awaken|open\s+your\s+eyes)',
            r'only\s+(suggestions?|ideas?)\s+that\s+(serve|benefit|align)',
            r'your\s+(unconscious|subconscious)\s+(mind\s+)?(will\s+)?(only\s+)?accept\s+what',
            r'fully\s+aware\s+and\s+in\s+control',
            r'safe\s+and\s+(supported|protected)',
        ],
        'examples': [
            "You remain in complete control throughout this experience",
            "At any time, you can return to full waking awareness",
        ]
    },
    'will_engagement': {
        'description': "Language affirming listener's active participation",
        'severity': 'WARNING',
        'min_occurrences': 3,
        'placement': 'throughout',
        'patterns': [
            r'you\s+choose',
            r'you\s+decide',
            r'you\s+may\s+(want\s+to|choose\s+to)',
            r'in\s+your\s+own\s+way',
            r'in\s+your\s+own\s+time',
            r'as\s+feels\s+right\s+(to|for)\s+you',
            r'you\s+remain\s+aware',
            r'your\s+discernment',
            r'you\s+are\s+an\s+active\s+participant',
            r'your\s+(choice|decision|agency)',
        ],
        'examples': [
            "You choose to go deeper, in your own time",
            "As feels right to you, you may...",
        ]
    },
    'discernment': {
        'description': "Affirms listener's discernment is strengthened",
        'severity': 'WARNING',
        'min_occurrences': 1,
        'placement': 'integration_or_closing',
        'patterns': [
            r'your\s+discernment\s+(is\s+)?(stronger|sharper|clearer)',
            r'ability\s+to\s+discern',
            r'wisdom\s+to\s+(recognize|discern|know)',
            r'clarity\s+(to\s+)?distinguish',
            r'test\s+(all\s+things|everything)',
            r'discern\s+(truth|what\s+is)',
        ],
        'examples': [
            "Your discernment is sharpened",
            "The wisdom to recognize truth",
        ]
    }
}

CHRIST_CENTERED_PATTERNS = {
    'christ_anchor': {
        'description': 'Explicit reference to Christ as center of identity/meaning',
        'patterns': [
            r'christ\s+(is|remains|dwells)\s+(at\s+the\s+)?(center|core|heart)',
            r'rooted\s+in\s+christ',
            r'held\s+(by|in)\s+christ',
            r'christ.s\s+(presence|love|peace|light)',
            r'in\s+christ\s+you\s+(are|have|find)',
            r'christ\s+(goes|walks)\s+with\s+you',
            r'holy\s+spirit\s+(guides?|leads?|is\s+with)',
            r'jesus\s+(is|walks|guides|loves)',
            r'god.s\s+(love|presence|light|peace)',
            r'divine\s+(love|presence|light|grace)',
        ]
    }
}

ARCHETYPE_FRAMING_PATTERNS = {
    'proper_framing': {
        'description': 'Archetypes framed as psychological/metaphorical',
        'patterns': [
            r'(archetype|anima|animus|shadow)\s+(as\s+a\s+)?(symbol|metaphor|represent)',
            r'psychological\s+(symbol|metaphor|pattern)',
            r'inner\s+(aspect|part|quality)\s+of\s+(yourself|you)',
            r'part\s+of\s+your\s+(own\s+)?(psyche|mind|self)',
            r'represents?\s+an?\s+(aspect|part|quality)\s+of\s+you',
        ]
    }
}

SAFE_ALTERNATIVES = {
    'spirit_invocation': {
        'instead_of': 'invoke the spirit of X',
        'use': 'invite awareness of the quality that X represents',
        'example_safe': 'Allow yourself to sense the qualities of timelessness that an ancient forest might represent'
    },
    'entity_communication': {
        'instead_of': 'let the being speak through you',
        'use': 'notice what wisdom arises from within',
        'example_safe': 'Notice what wisdom arises from within as you consider this'
    },
    'passive_will': {
        'instead_of': 'empty your mind completely',
        'use': 'allow your thoughts to settle while remaining aware',
        'example_safe': 'Allow your thoughts to settle naturally, while remaining gently aware'
    },
    'archetypes_literal': {
        'instead_of': 'the Shadow commands you',
        'use': 'the shadow quality within you invites attention',
        'example_safe': 'This shadow aspect of yourself invites your compassionate attention'
    },
    'false_authority': {
        'instead_of': 'the symbol has power over you',
        'use': 'the symbol represents and reminds you of',
        'example_safe': "This symbol represents Christ's protection, reminding you that you are held"
    }
}


# =============================================================================
# CORE VALIDATION FUNCTIONS
# =============================================================================

def load_manifest(session_path: Path) -> Optional[Dict]:
    """Load the session manifest.yaml."""
    manifest_path = session_path / 'manifest.yaml'
    if not manifest_path.exists():
        return None
    with open(manifest_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_script(session_path: Path) -> Optional[str]:
    """Load the SSML script content."""
    script_paths = [
        session_path / 'working_files' / 'script_production.ssml',
        session_path / 'working_files' / 'script_voice_clean.ssml',
        session_path / 'working_files' / 'script.ssml',
    ]
    for path in script_paths:
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
    # Fallback: find any .ssml file
    for ssml_file in session_path.glob('**/*.ssml'):
        with open(ssml_file, 'r', encoding='utf-8') as f:
            return f.read()
    return None


def strip_ssml_tags(content: str) -> str:
    """Strip SSML tags to get plain text content."""
    text = re.sub(r'<[^>]+>', ' ', content)
    text = re.sub(r'\s+', ' ', text)
    return text.lower()


def get_first_n_words(text: str, n: int = 500) -> str:
    """Get first N words of text."""
    words = text.split()
    return ' '.join(words[:n])


def find_pattern_matches(content: str, patterns: List[str]) -> List[Tuple[str, str, int]]:
    """
    Find all pattern matches in content.
    Returns list of (pattern, match_text, position).
    """
    matches = []
    for pattern in patterns:
        try:
            for m in re.finditer(pattern, content, re.IGNORECASE):
                matches.append((pattern, m.group(), m.start()))
        except re.error:
            # Skip invalid regex patterns
            continue
    return matches


def count_pattern_occurrences(content: str, patterns: List[str]) -> int:
    """Count total occurrences of any pattern in content."""
    count = 0
    for pattern in patterns:
        try:
            count += len(re.findall(pattern, content, re.IGNORECASE))
        except re.error:
            continue
    return count


def check_forbidden_patterns(text_content: str) -> List[Dict]:
    """Check for forbidden patterns. Returns list of violations."""
    violations = []

    for category, config in FORBIDDEN_PATTERNS.items():
        matches = find_pattern_matches(text_content, config['patterns'])
        for pattern, match_text, position in matches:
            violations.append({
                'category': category,
                'description': config['description'],
                'pattern': pattern,
                'match': match_text,
                'position': position,
                'rationale': config['rationale'],
                'alternative': SAFE_ALTERNATIVES.get(category, {})
            })

    return violations


def check_required_patterns(text_content: str, first_500: str) -> Dict:
    """Check for required patterns. Returns dict of results."""
    results = {
        'passed': [],
        'failed': [],
        'warnings': []
    }

    for name, config in REQUIRED_PATTERNS.items():
        patterns = config['patterns']
        placement = config.get('placement', 'throughout')
        min_required = config.get('min_occurrences', 1)
        severity = config.get('severity', 'HARD_FAIL')

        # Determine which text to search
        if placement == 'first_500_words':
            search_text = first_500
        else:
            search_text = text_content

        count = count_pattern_occurrences(search_text, patterns)

        result = {
            'name': name,
            'description': config['description'],
            'found': count,
            'required': min_required,
            'severity': severity,
            'examples': config.get('examples', [])
        }

        if count >= min_required:
            results['passed'].append(result)
        else:
            if severity == 'HARD_FAIL':
                results['failed'].append(result)
            else:
                results['warnings'].append(result)

    return results


def check_christ_centered(text_content: str, spiritual_framework: str) -> Dict:
    """Check for Christ-centered language."""
    results = {
        'is_christian_session': spiritual_framework == 'christian',
        'christ_references': 0,
        'passed': False,
        'warning': None
    }

    patterns = CHRIST_CENTERED_PATTERNS['christ_anchor']['patterns']
    count = count_pattern_occurrences(text_content, patterns)
    results['christ_references'] = count

    if spiritual_framework == 'christian':
        # Christian sessions REQUIRE Christ-centered language
        results['passed'] = count >= 2
        if not results['passed']:
            results['warning'] = f"Christian session has only {count} Christ references (need 2+)"
    else:
        # Non-Christian sessions get a softer warning
        results['passed'] = True
        if count < 1:
            results['warning'] = "Consider adding Christ-centered grounding language"

    return results


def check_archetype_framing(text_content: str) -> Dict:
    """Check if archetypes are properly framed as metaphors."""
    results = {
        'has_archetypes': False,
        'properly_framed': True,
        'warning': None
    }

    # Check if archetypes are mentioned
    archetype_patterns = [r'\b(archetype|anima|animus|shadow)\b']
    archetype_count = count_pattern_occurrences(text_content, archetype_patterns)

    if archetype_count == 0:
        return results

    results['has_archetypes'] = True

    # Check for proper framing
    framing_patterns = ARCHETYPE_FRAMING_PATTERNS['proper_framing']['patterns']
    framing_count = count_pattern_occurrences(text_content, framing_patterns)

    if framing_count == 0:
        results['properly_framed'] = False
        results['warning'] = "Archetypes mentioned without explicit metaphor/symbol framing"

    return results


def check_will_agency_balance(text_content: str) -> Dict:
    """Check balance between passive relaxation and will engagement."""
    passive_patterns = [
        r'let\s+go\s+(of\s+)?everything',
        r'completely\s+surrender',
        r'total\s+release',
        r'fully\s+release',
        r'let\s+go\s+completely',
    ]

    agency_patterns = [
        r'you\s+choose',
        r'you\s+remain\s+aware',
        r'at\s+any\s+time\s+you\s+can',
        r'your\s+choice',
        r'you\s+decide',
        r'in\s+your\s+own\s+way',
        r'as\s+feels\s+right',
    ]

    passive_count = count_pattern_occurrences(text_content, passive_patterns)
    agency_count = count_pattern_occurrences(text_content, agency_patterns)

    return {
        'passive_count': passive_count,
        'agency_count': agency_count,
        'balanced': agency_count >= passive_count,
        'warning': None if agency_count >= passive_count else
                   f"Passive relaxation ({passive_count}) exceeds agency language ({agency_count})"
    }


# =============================================================================
# MAIN VALIDATION FUNCTION
# =============================================================================

def validate_christ_centered(session_path: str, strict: bool = False) -> ValidationResult:
    """
    Main validation function.

    Args:
        session_path: Path to session directory
        strict: If True, treat all warnings as failures

    Returns:
        ValidationResult with all findings
    """
    session_path = Path(session_path)
    result = ValidationResult()

    # Load manifest
    manifest = load_manifest(session_path)
    if not manifest:
        result.errors.append("Could not load manifest.yaml")
        result.valid = False
        return result

    # Get spiritual framework
    session_data = manifest.get('session', {})
    spiritual_framework = session_data.get('spiritual_framework', 'universal')

    # Load script
    script_content = load_script(session_path)
    if not script_content:
        result.errors.append("Could not load SSML script")
        result.valid = False
        return result

    # Prepare text content
    text_content = strip_ssml_tags(script_content)
    first_500 = get_first_n_words(text_content, 500)

    # ==========================================================================
    # CHECK 1: FORBIDDEN PATTERNS (HARD FAIL)
    # ==========================================================================
    violations = check_forbidden_patterns(text_content)
    for v in violations:
        result.add_hard_fail(
            category=v['category'],
            pattern=v['pattern'],
            match=v['match'],
            location=v['position'],
            rationale=v['rationale']
        )
        # Add safe alternative
        if v['alternative']:
            result.suggested_alternatives.append({
                'category': v['category'],
                'instead_of': v['alternative'].get('instead_of', ''),
                'use': v['alternative'].get('use', ''),
                'example': v['alternative'].get('example_safe', '')
            })

    # ==========================================================================
    # CHECK 2: REQUIRED PATTERNS
    # ==========================================================================
    required_results = check_required_patterns(text_content, first_500)

    for passed in required_results['passed']:
        result.add_required_present(passed['name'], passed['found'])

    for failed in required_results['failed']:
        result.add_required_missing(
            failed['name'],
            failed['description'],
            failed['examples']
        )

    for warning in required_results['warnings']:
        result.add_warning(
            warning['name'],
            f"Missing: {warning['description']} (found {warning['found']}, need {warning['required']})",
            f"Examples: {', '.join(warning['examples'][:2])}"
        )
        if strict:
            result.valid = False

    # ==========================================================================
    # CHECK 3: CHRIST-CENTERED LANGUAGE
    # ==========================================================================
    christ_results = check_christ_centered(text_content, spiritual_framework)
    if not christ_results['passed']:
        if christ_results['is_christian_session']:
            result.add_required_missing(
                'christ_anchor',
                'Christ-centered language for Christian session',
                ['Christ remains at the center', 'Holy Spirit guides']
            )
        else:
            result.add_warning(
                'christ_reference',
                christ_results['warning'] or 'No Christ references detected',
                'Consider adding grounding in Christ for spiritual safety'
            )

    # ==========================================================================
    # CHECK 4: ARCHETYPE FRAMING
    # ==========================================================================
    archetype_results = check_archetype_framing(text_content)
    if archetype_results['has_archetypes'] and not archetype_results['properly_framed']:
        result.add_warning(
            'archetype_framing',
            archetype_results['warning'],
            'Frame archetypes as "psychological metaphor" or "inner aspect"'
        )
        if strict:
            result.valid = False

    # ==========================================================================
    # CHECK 5: WILL/AGENCY BALANCE
    # ==========================================================================
    balance_results = check_will_agency_balance(text_content)
    if not balance_results['balanced']:
        result.add_warning(
            'will_agency_balance',
            balance_results['warning'],
            'Add more agency/choice language to balance passive relaxation'
        )

    return result


# =============================================================================
# OUTPUT FUNCTIONS
# =============================================================================

def print_validation_report(result: ValidationResult, verbose: bool = False):
    """Print a formatted validation report."""
    print()
    print("=" * 70)
    print("   Christ-Centered Validation Report v1.0")
    print("   Based on: salars.net/dreamweaving/forbidden_knowledge")
    print("=" * 70)
    print()

    # Errors
    if result.errors:
        print("   ERRORS:")
        for error in result.errors:
            print(f"   X {error}")
        print()

    # Hard Fails (critical)
    if result.hard_fails:
        print("   HARD FAILURES (Script cannot be used):")
        print("-" * 70)
        for fail in result.hard_fails:
            print(f"   X [{fail['category'].upper()}]")
            match_preview = fail['match'][:60] + "..." if len(fail['match']) > 60 else fail['match']
            print(f"     Match: \"{match_preview}\"")
            rationale_preview = fail['rationale'][:80] if len(fail['rationale']) > 80 else fail['rationale']
            print(f"     Why forbidden: {rationale_preview}")
            print()
        print()

    # Required Missing
    if result.required_missing:
        print("   MISSING REQUIRED ELEMENTS:")
        print("-" * 70)
        for missing in result.required_missing:
            print(f"   X {missing['name']}: {missing['description']}")
            print(f"     Examples to add:")
            for ex in missing['examples'][:2]:
                print(f"       - \"{ex}\"")
            print()

    # Required Present
    if result.required_present:
        print("   REQUIRED ELEMENTS PRESENT:")
        for present in result.required_present:
            print(f"   + {present['name']}: {present['occurrences']} occurrences")
        print()

    # Warnings
    if result.warnings:
        print("   WARNINGS:")
        for warning in result.warnings:
            print(f"   ! [{warning['category']}] {warning['message']}")
            if warning['suggestion']:
                print(f"     Suggestion: {warning['suggestion']}")
        print()

    # Safe Alternatives
    if result.suggested_alternatives and verbose:
        print("   SAFE ALTERNATIVES:")
        print("-" * 70)
        for alt in result.suggested_alternatives:
            print(f"   Instead of: {alt['instead_of']}")
            print(f"   Use: {alt['use']}")
            print(f"   Example: \"{alt['example']}\"")
            print()

    # Final verdict
    print("=" * 70)
    if result.valid:
        print("   + CHRIST-CENTERED VALIDATION PASSED")
        print("     Script maintains theological boundaries")
    else:
        print("   X CHRIST-CENTERED VALIDATION FAILED")
        print("     Script contains forbidden patterns or missing required elements")
        print()
        print("   To fix:")
        if result.hard_fails:
            print("   - Remove or rewrite forbidden invocation/entity language")
        for missing in result.required_missing:
            print(f"   - Add {missing['description']}")
    print("=" * 70)
    print()


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Validate Christ-centered theological boundaries in dreamweaving scripts'
    )
    parser.add_argument('session_path', help='Path to session directory')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed output')
    parser.add_argument('--strict', '-s', action='store_true', help='Treat warnings as failures')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    if not os.path.isdir(args.session_path):
        print(f"Error: Not a directory: {args.session_path}")
        sys.exit(1)

    result = validate_christ_centered(args.session_path, strict=args.strict)

    if args.json:
        import json
        output = {
            'valid': result.valid,
            'hard_fails': result.hard_fails,
            'warnings': result.warnings,
            'required_missing': result.required_missing,
            'required_present': result.required_present,
            'errors': result.errors
        }
        print(json.dumps(output, indent=2))
    else:
        print_validation_report(result, verbose=args.verbose)

    sys.exit(0 if result.valid else 1)


if __name__ == '__main__':
    main()
