#!/usr/bin/env python3
"""
Outcome Validation Utility v1.0
Validates that a script contains required patterns for its stated outcome.

Features:
- Loads outcome requirements from knowledge/outcome_registry.yaml
- Checks script for required patterns (vagal activation, fractionation loops, etc.)
- Validates archetype alignment
- Checks integration action presence
- Provides actionable suggestions for missing elements

Usage:
    python scripts/utilities/validate_outcome.py path/to/session/
    python scripts/utilities/validate_outcome.py path/to/session/ --verbose
"""

import sys
import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

# =============================================================================
# PATTERN DETECTION REGEXES
# =============================================================================
# These patterns detect the presence of hypnotic techniques in SSML scripts

PATTERN_DETECTORS = {
    'vagal_activation': {
        'description': 'Vagal activation patterns (parasympathetic nervous system)',
        'patterns': [
            # Breath-based vagal activation
            r'breath[e]?\s+(in|out|deeply|slowly)',
            r'inhale.*exhale',
            r'deep\s+breath',
            r'slow\s+breath',
            # Body-based vagal activation
            r'jaw\s+(soften|relax|release|loosen)',
            r'shoulders\s+(drop|release|soften|melt)',
            r'belly\s+(soften|relax|expand)',
            r'eyes\s+(soften|close|relax)',
            # Warmth/safety phrases
            r'(warm|warmth)\s+(spread|flow)',
            r'safe\s+(and|in)\s+(comfortable|secure)',
            r'(held|supported)\s+(safely|gently)',
        ],
        'min_matches': 2,  # Minimum unique pattern matches
    },

    'emotional_calibration': {
        'description': 'Emotional calibration and IFS-style permission',
        'patterns': [
            r'(notice|feel|sense)\s+what.*present',
            r'whatever\s+(emotion|feeling).*welcome',
            r'(part|parts)\s+of\s+(you|yourself)',
            r'allow\s+(yourself|whatever)',
            r'(meet|greet)\s+(this|that|whatever)',
            r'with\s+(compassion|kindness|gentleness)',
            r'(all\s+parts|every\s+part)\s+(of\s+you|welcome)',
        ],
        'min_matches': 1,
    },

    'fractionation_loops': {
        'description': 'Fractionation loops (A→B→B→A deepening)',
        'patterns': [
            r'deeper.*natural.*natural.*deeper',
            r'relaxed.*safe.*safe.*relaxed',
            r'go.*deeper.*wait.*already.*deeper',
            r'deeper\s+you\s+go.*more.*more.*deeper',
            r'comfortable.*safe.*safe.*comfortable',
            r'open.*trusting.*trusting.*open',
            r'deeper.*easier.*easier.*deeper',
        ],
        'min_matches': 2,
    },

    'temporal_dissociation': {
        'description': 'Temporal dissociation and future pacing',
        'patterns': [
            r'(minutes|hours|days|weeks)\s+(ahead|from\s+now)',
            r'in\s+the\s+(coming|next)\s+(days|weeks|moments)',
            r'as\s+time\s+(passes|unfolds|moves)',
            r'(future|tomorrow|later)\s+(you|self|when)',
            r'looking\s+back.*from',
            r'(over\s+time|gradually|increasingly)',
            r'(continue|continues|continuing)\s+to\s+(unfold|deepen|integrate)',
        ],
        'min_matches': 1,
    },

    'sensory_stacking': {
        'description': 'Multi-sensory immersion (VAK rotation)',
        'patterns': [
            # Visual
            r'(see|seeing|vision|light|glow|color|bright|shimmer)',
            # Auditory
            r'(hear|hearing|sound|tone|whisper|voice|echo)',
            # Kinesthetic
            r'(feel|feeling|sensation|touch|warm|cool|tingling)',
            # Rich descriptions
            r'(imagine|picture|visualize|notice)',
        ],
        'min_matches': 3,  # Need multiple senses engaged
    },

    'breath_pacing': {
        'description': 'Explicit breath pacing cues',
        'patterns': [
            r'breath[e]?\s+(in|out)\s*(slowly|deeply|gently)?',
            r'(inhale|exhale)\s*(deeply|slowly|fully)?',
            r'(long|slow|deep)\s+(inhale|exhale|breath)',
            r'with\s+(each|every)\s+breath',
            r'breathing\s+(deeply|slowly|naturally)',
            r'<break\s+time="[3-5]s"',  # Long breaks for breath
        ],
        'min_matches': 2,
    },

    'embedded_commands': {
        'description': 'Embedded commands via emphasis tags',
        'patterns': [
            r'<emphasis[^>]*>',  # Any emphasis tag counts
        ],
        'min_matches': 10,
        'count_all': True,  # Count all matches, not unique patterns
    },

    'double_binds': {
        'description': 'Illusory choice double-binds',
        'patterns': [
            r'(can|may)\s+\w+.*or\s+\w+.*whichever',
            r'choose\s+to.*or.*wait',
            r'(quickly|slowly)\s+or\s+(slowly|quickly)',
            r'whether\s+you.*or.*either\s+way',
            r'you\s+(might|may).*or\s+(perhaps|maybe)',
            r'(sooner|later).*doesn\'t\s+matter',
        ],
        'min_matches': 1,
    },

    # ==========================================================================
    # PHASE 1 PATTERNS (Critical NLP Techniques)
    # ==========================================================================

    'submodality_shifts': {
        'description': 'NLP submodality shifts (changing sensory qualities of mental representations)',
        'patterns': [
            # Shrink and distance
            r'(shrink|smaller|tiny|point|distance|far\s+away|fading)',
            r'growing\s+smaller',
            r'moving\s+(further|farther)\s+away',
            # Brighten and expand
            r'(brighten|brighter|expand|growing|larger|bigger|vivid)',
            r'fills?\s+(your\s+)?(entire\s+)?awareness',
            r'glowing\s+with\s+(warmth|light)',
            # Color transform
            r'(color|colour)\s+(shift|transform|change)',
            r'shifting.*color',
            r'color\s+that\s+feels',
            # Weight to lightness
            r'(weight|heavy|heaviness)\s+(lift|dissolve|transform)',
            r'becoming\s+(lighter|weightless|buoyant)',
            # Temperature shifts
            r'(warmth|cool)\s+(spread|flow|transform)',
            r'temperature\s+(shift|change)',
            # Sound/volume shifts
            r'(volume|sound|voice)\s+(fad|lower|soft|quiet)',
            r'(diminish|quieter|distant)\s+sound',
        ],
        'min_matches': 1,
    },

    'expectancy_priming': {
        'description': 'Placebo amplification through positive expectation',
        'patterns': [
            # Collective validation
            r'(most\s+people|many\s+(people|have)|others?\s+have)\s+(find|found|experience|report)',
            r'(deeply|profoundly)\s+(relax|transform|heal)',
            # Innate capacity
            r'(your\s+mind|you)\s+already\s+know',
            r'(natural|innate)\s+(ability|capacity|wisdom)',
            # Expectation statements
            r'something\s+(powerful|profound|meaningful)\s+(is\s+about|will)',
            r'(powerful|profound)\s+(shift|change|transformation)',
            # Preparatory priming
            r'(open|ready|prepared)\s+to\s+receive',
            r'(allow|let)\s+(yourself|this)\s+to\s+(work|happen|unfold)',
        ],
        'min_matches': 2,
    },

    'identity_reframing': {
        'description': 'Identity-level transformation (not just behavior change)',
        'patterns': [
            # Future self embodiment
            r'(version|self)\s+(of\s+you|who)\s+(has\s+already|that\s+has)',
            r'step\s+(into|forward\s+into)\s+(this|that|the)\s+(new|version)',
            r'becoming\s+who\s+you\s+(already\s+)?are',
            # Archetypal identification
            r'(feel|sense)\s+(their|this)\s+(strength|wisdom|power|courage)',
            r'(wearing|embodying)\s+this\s+(identity|energy|quality)',
            r'(always\s+been|has\s+always\s+been)\s+part\s+of\s+you',
            # Core identity statements
            r'this\s+is\s+who\s+you\s+(are|have\s+always\s+been)',
            r'(you\s+are|I\s+am)\s+(becoming|now|already)',
            # Walking as new self
            r'(walk|move|carry\s+yourself)\s+as\s+(the|this|someone)',
        ],
        'min_matches': 1,
    },

    # ==========================================================================
    # PHASE 2 PATTERNS (High-Impact Additions)
    # ==========================================================================

    'parts_integration': {
        'description': 'IFS-inspired parts work and internal dialogue',
        'patterns': [
            # Parts acknowledgment
            r'(part|parts)\s+of\s+(you|yourself)',
            r'(different|various|all)\s+parts',
            r'(a|that|this)\s+part\s+(that|which|of)',
            # Parts dialogue
            r'what\s+does\s+this\s+part\s+(want|need|feel)',
            r'(listen|listening)\s+to\s+(this|that)\s+part',
            r'(speak|speaking)\s+to\s+(this|that)\s+part',
            # Protector appreciation
            r'(thank|thanking|appreciate|gratitude)\s+(this|that)\s+part',
            r'(protect|protecting|protected)',
            r'(trying\s+to|wanted\s+to)\s+(help|protect|keep.*safe)',
            # Parts integration
            r'(parts|all\s+parts)\s+(coming|come)\s+together',
            r'(integrate|integration|integrating)',
            r'(harmony|peace)\s+(between|among)\s+parts',
            # Inner council
            r'(inner|internal)\s+(council|meeting|gathering)',
            r'(aspects|voices|parts)\s+of\s+(yourself|you)',
        ],
        'min_matches': 1,
    },

    'predictive_processing_disruption': {
        'description': 'Pattern interrupts and reality morphing for increased suggestibility',
        'patterns': [
            # Reality morphing
            r'(space|room|world)\s+(around\s+you)?\s*(begin|begins|beginning)\s+to\s+(shift|change|morph|dissolve)',
            r'(walls|floor|ground)\s+(dissolv|melt|shift|becom)',
            r'(ordinary|normal|usual)\s+rules\s+(soften|dissolve|don\'t\s+apply)',
            # Temporal dislocation
            r'time\s+(has\s+)?begun\s+to\s+flow\s+differently',
            r'(minute|minutes)\s+(lasting|become|feel\s+like)\s+(hours|eternity)',
            r'(hours|moments)\s+passing\s+in\s+(moments|seconds|instant)',
            # Ego softening
            r'(boundaries|edges|sense\s+of\s+self)\s+(soften|dissolve|blur)',
            r'(merge|merging|dissolving)\s+(into|with)\s+(the|this|everything)',
            r'(separate\s+self|individual|ego)\s+(fade|soften|release)',
            # Surreal imagery
            r'(impossible|surreal|dreamlike|magical)',
            r'(colors|shapes|forms)\s+(you\'ve\s+never|impossible)',
            # Observer separation
            r'(observe|watching|witness)\s+(yourself|your\s+thoughts)',
            r'(step\s+back|stepping\s+back)\s+(from|and\s+watch)',
        ],
        'min_matches': 1,
    },

    'schema_rewriting': {
        'description': 'Core belief transformation and schema modification',
        'patterns': [
            # Belief softening
            r'(old|ancient|deep)\s+(belief|pattern|story)',
            r'(learned|told|decided)\s+long\s+ago',
            r'(no\s+longer|doesn\'t)\s+(serve|apply|fit)',
            r'(loosen|soften|release)\s+(its\s+)?(grip|hold)',
            # New belief installation
            r'(new|deeper)\s+(truth|belief|knowing|understanding)',
            r'settling\s+into\s+(your\s+)?(cells|bones|body|being)',
            r'(always\s+been|was\s+always)\s+(there|true|waiting)',
            # Relational reparenting
            r'(loved|held|seen|accepted)\s+(exactly|just)\s+(as\s+you\s+are|unconditionally)',
            r'(deserving|worthy)\s+(of|exactly)',
            r'(you\s+are|I\s+am)\s+(enough|worthy|complete)',
            # Core unworthiness clearing
            r'(not\s+enough|unworthy|broken|defective)\s+(is\s+)?not\s+true',
            r'(release|let\s+go\s+of)\s+(the\s+)?(belief|idea|thought)',
        ],
        'min_matches': 1,
    },

    # ==========================================================================
    # PHASE 3 PATTERNS (Memory & State Work)
    # ==========================================================================

    'memory_reconsolidation': {
        'description': 'Safe memory work and emotional update (light protocol)',
        'patterns': [
            # Safe distance viewing
            r'(watch|view|see)\s+(it|this|that)\s+(from|at)\s+a\s+(safe\s+)?distance',
            r'(safe|protected)\s+(place|space|vantage)',
            r'(observe|watching)\s+(from\s+)?afar',
            # Wisdom reframe
            r'(new|fresh|different)\s+(understanding|perspective|wisdom)',
            r'(wisdom|understanding)\s+you\'ve\s+(gained|acquired|found)',
            r'(know|see|understand)\s+(now|things)\s+(differently|that)',
            # Emotional softening
            r'(edges|charge|intensity)\s+(soften|fade|dissolve)',
            r'(emotional\s+)?(charge|weight)\s+(lifting|releasing|fading)',
            # Resource connection
            r'(bring|connect|access)\s+(this|that|your)\s+(wisdom|strength|resource)',
            r'(adult|wiser|current)\s+self\s+(present|here|with)',
        ],
        'min_matches': 1,
    },

    'association_dissociation': {
        'description': 'Deliberate state switching between associated and dissociated perspectives',
        'patterns': [
            # Dissociation out
            r'step\s+(back|away)\s+from',
            r'(watch|observe|see)\s+(yourself|from\s+outside)',
            r'(as\s+if|like)\s+(watching|observing)\s+(from\s+)?a\s+distance',
            r'(floating|hovering)\s+(above|outside)',
            # Association in
            r'step\s+(fully\s+)?into\s+(this|that|the)',
            r'(fill|fills)\s+every\s+part\s+of\s+you',
            r'(feel|feeling)\s+(it|this)\s+in\s+your\s+(body|chest|heart)',
            r'(become|becoming)\s+(one\s+with|fully\s+present)',
            # State switching cues
            r'(now|and\s+now)\s+(step|move)\s+(back|into)',
            r'(shift|shifting)\s+(your\s+)?perspective',
        ],
        'min_matches': 1,
    },

    'compounded_anchoring': {
        'description': 'Multi-modal anchors that reinforce across modalities',
        'patterns': [
            # Physical anchors
            r'(each|every|whenever)\s+(time|moment)\s+you\s+(take|feel|notice)',
            r'(touch|press|place)\s+(your\s+)?(hand|finger|palm)',
            r'(three|3)\s+deep\s+breaths',
            # Symbolic anchors
            r'whenever\s+you\s+(recall|remember|think\s+of)\s+(the|this|that)',
            r'(symbol|image|object)\s+(remind|brings|returns)',
            r'(golden|glowing|sacred)\s+(object|symbol|light)',
            # Sensory anchors
            r'(notice|feel|sense)\s+(that|this)\s+(warmth|sensation|feeling)',
            r'(warmth|tingling|sensation)\s+(in\s+your|spread)',
            # Stacking language
            r'(each\s+time|every\s+time|whenever)',
            r'(this|that)\s+(feeling|state|experience)\s+(deepen|strengthen|return)',
        ],
        'min_matches': 1,
    },

    # ==========================================================================
    # PHASE 4 PATTERNS (Symbolic & Arc Work)
    # ==========================================================================

    'symbolic_catharsis': {
        'description': 'Emotional release through pure symbolism',
        'patterns': [
            # Fire release
            r'(cast|throw|release)\s+(into|to)\s+(the\s+)?(fire|flame)',
            r'(burn|burning|consume)\s+(away|what\s+no\s+longer)',
            r'(sacred|transforming)\s+(fire|flame)',
            # Water dissolution
            r'(wash|water|stream|river)\s+(away|dissolve|carry)',
            r'(dissolve|melt)\s+(into|in)\s+(the\s+)?(water|stream|ocean)',
            r'(purif|cleans)\w*\s+(by|in|through)\s+(the\s+)?water',
            # Wind scattering
            r'(wind|breeze)\s+(carry|carries|scatter)',
            r'(scatter|release)\s+(to|into)\s+(the\s+)?wind',
            r'(blow|blown)\s+away',
            # Earth burial
            r'(return|bury|place)\s+(to|in|into)\s+(the\s+)?earth',
            r'earth\s+(compost|transform|receive)',
            r'(ground|soil)\s+(absorb|receive|transform)',
            # Light transformation
            r'(light|radiance)\s+(transform|transmut|dissolv)',
            r'(dissolve|melt)\s+(into|in)\s+(pure\s+)?light',
        ],
        'min_matches': 1,
    },

    'multi_episode_arc': {
        'description': 'Series callbacks and cumulative journey references',
        'patterns': [
            # Series callbacks
            r'(remember|recall)\s+(from\s+)?(our\s+)?(last|previous)\s+(journey|session|time)',
            r'(as\s+you\s+)?(return|returned)\s+to\s+(the|this|a)\s+(familiar|sacred)',
            r'(recogni|remember)\s+(this|the)\s+(place|space|garden|temple)',
            # Evolving symbols
            r'(still|continues\s+to)\s+(glow|grow|evolve|develop)',
            r'(notice|see)\s+how\s+(it|this)\s+has\s+(grown|changed|evolved)',
            # Cumulative anchoring
            r'(adding|building|layering)\s+(to|upon)\s+(the|what)',
            r'(deepen|strengthen|grow)\s+(each|every)\s+(time|session)',
            # Character development
            r'(guide|guardian|ally)\s+(you\'ve|you\s+have)\s+(met|known)',
            r'(familiar|trusted)\s+(presence|guide|guardian)',
        ],
        'min_matches': 1,
    },

    'yes_sets': {
        'description': 'Truism sequences that build compliance momentum',
        'patterns': [
            r"you'?re\s+(here|listening|breathing|sitting)",
            r"you'?ve\s+(arrived|found|made\s+it)",
            r"(and\s+)?(already|beginning|starting)\s+to\s+(settle|relax)",
            r"(your\s+body|you)\s+(know|knows)\s+how\s+to",
        ],
        'min_matches': 3,
    },

    'pattern_interrupts': {
        'description': 'Sudden shifts that disrupt mental patterns',
        'patterns': [
            r'(suddenly|unexpectedly|in\s+an\s+instant)',
            r'(everything\s+)?(shifts?|changes?)\s+(completely|instantly|now)',
            r'(stop|freeze|pause)\s+(completely|entirely|now)',
            r'(wait|notice)\s*\.\.\.',  # Trailing ellipsis pattern
        ],
        'min_matches': 1,
    },
}

# Integration action detection patterns
INTEGRATION_ACTION_PATTERNS = {
    'hydration_anchor': [
        r'(drink|glass)\s+(of\s+)?(water|tea)',
        r'hydrat(e|ion)',
        r'sip\s+(of\s+)?water',
    ],
    'hand_heart_anchor': [
        r'(hand|palm)\s+(on|over|to)\s+(your\s+)?(heart|chest)',
        r'heart\s+(space|center)',
        r'touch\s+(your\s+)?chest',
    ],
    'beauty_noticing': [
        r'(notice|see|find)\s+(something\s+)?(beautiful|beauty)',
        r'(look\s+for|find)\s+(beauty|something\s+beautiful)',
        r'beautiful\s+(thing|moment|sight)',
    ],
    'breath_trigger': [
        r'(whenever|each\s+time)\s+you\s+breath',
        r'breath\s+(remind|bring|return)',
        r'deep\s+breath.*remember',
        r'breath\s+(as\s+)?anchor',
    ],
    'threshold_anchor': [
        r'(door|doorway|threshold)',
        r'(crossing|cross|step)\s+(through|into)',
        r'pass(ing)?\s+through',
    ],
    'morning_connection': [
        r'(each|every)\s+(morning|day)',
        r'(wake|waking|awaken)',
        r'(first\s+moments|first\s+thing)',
        r'(start|begin)\s+(your|the)\s+day',
    ],
}


def load_outcome_registry() -> Dict:
    """Load the outcome registry YAML file."""
    registry_path = Path(__file__).parent.parent.parent / 'knowledge' / 'outcome_registry.yaml'

    if not registry_path.exists():
        print(f"   Error: Outcome registry not found: {registry_path}")
        return {}

    with open(registry_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_manifest(session_path: Path) -> Optional[Dict]:
    """Load the session manifest.yaml."""
    manifest_path = session_path / 'manifest.yaml'

    if not manifest_path.exists():
        return None

    with open(manifest_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_script(session_path: Path) -> Optional[str]:
    """Load the SSML script content."""
    # Try production script first, then voice-clean, then any .ssml
    script_paths = [
        session_path / 'working_files' / 'script_production.ssml',
        session_path / 'working_files' / 'script_voice_clean.ssml',
        session_path / 'working_files' / 'script.ssml',
    ]

    for path in script_paths:
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()

    # Look for any SSML file
    for ssml_file in session_path.glob('**/*.ssml'):
        with open(ssml_file, 'r', encoding='utf-8') as f:
            return f.read()

    return None


def count_pattern_matches(content: str, pattern_config: Dict) -> Tuple[int, List[str]]:
    """
    Count pattern matches in content.
    Returns (count, list of matched patterns).
    """
    matched_patterns = []
    total_count = 0

    for pattern in pattern_config['patterns']:
        matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
        if matches:
            if pattern_config.get('count_all'):
                total_count += len(matches)
            else:
                matched_patterns.append(pattern)

    if pattern_config.get('count_all'):
        return total_count, [f"Total matches: {total_count}"]
    else:
        return len(matched_patterns), matched_patterns


def check_required_patterns(content: str, required_patterns: Dict, verbose: bool = False) -> Dict:
    """
    Check if script contains required patterns for the outcome.
    Returns validation results.
    """
    results = {
        'passed': [],
        'failed': [],
        'details': {}
    }

    for pattern_name, requirements in required_patterns.items():
        if pattern_name not in PATTERN_DETECTORS:
            continue

        detector = PATTERN_DETECTORS[pattern_name]
        min_required = requirements.get('minimum', detector.get('min_matches', 1))

        count, matched = count_pattern_matches(content, detector)

        detail = {
            'description': detector['description'],
            'found': count,
            'required': min_required,
            'placement': requirements.get('placement', 'throughout'),
            'rationale': requirements.get('rationale', ''),
        }

        if count >= min_required:
            results['passed'].append(pattern_name)
            detail['status'] = 'PASS'
        else:
            results['failed'].append(pattern_name)
            detail['status'] = 'FAIL'
            detail['deficit'] = min_required - count

        results['details'][pattern_name] = detail

    return results


def check_integration_actions(content: str) -> Dict:
    """
    Check for presence of integration actions.
    Returns validation results.
    """
    results = {
        'found': [],
        'missing': [],
        'details': {}
    }

    for action_name, patterns in INTEGRATION_ACTION_PATTERNS.items():
        found = False
        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                found = True
                break

        if found:
            results['found'].append(action_name)
        else:
            results['missing'].append(action_name)

    return results


def check_suggested_patterns(content: str, suggested_patterns: List[str]) -> Dict:
    """
    Check for presence of suggested (not required) patterns.
    Returns validation results as warnings, not failures.
    """
    results = {
        'present': [],
        'absent': [],
    }

    for pattern_name in suggested_patterns:
        if pattern_name not in PATTERN_DETECTORS:
            continue

        detector = PATTERN_DETECTORS[pattern_name]
        count, _ = count_pattern_matches(content, detector)

        if count > 0:
            results['present'].append(pattern_name)
        else:
            results['absent'].append(pattern_name)

    return results


def validate_outcome(session_path: str, verbose: bool = False) -> Dict:
    """
    Main validation function.

    Returns:
        {
            'valid': bool,
            'outcome': str,
            'required_patterns': {
                'passed': [...],
                'failed': [...],
                'details': {...}
            },
            'suggested_patterns': {
                'present': [...],
                'absent': [...]
            },
            'integration_actions': {
                'found': [...],
                'missing': [...]
            },
            'warnings': [...],
            'errors': [...]
        }
    """
    session_path = Path(session_path)

    result = {
        'valid': True,
        'outcome': None,
        'required_patterns': {},
        'suggested_patterns': {},
        'integration_actions': {},
        'warnings': [],
        'errors': [],
    }

    # Load outcome registry
    registry = load_outcome_registry()
    if not registry:
        result['errors'].append("Could not load outcome registry")
        result['valid'] = False
        return result

    # Load manifest
    manifest = load_manifest(session_path)
    if not manifest:
        result['errors'].append("Could not load manifest.yaml")
        result['valid'] = False
        return result

    # Get desired outcome from manifest
    session_data = manifest.get('session', {})
    desired_outcome = session_data.get('desired_outcome')

    if not desired_outcome:
        result['warnings'].append("No desired_outcome specified in manifest - skipping outcome validation")
        return result

    result['outcome'] = desired_outcome

    # Look up outcome requirements
    outcomes = registry.get('outcomes', {})
    if desired_outcome not in outcomes:
        result['errors'].append(f"Unknown outcome '{desired_outcome}' - not in registry")
        result['valid'] = False
        return result

    outcome_spec = outcomes[desired_outcome]

    # Load script
    script_content = load_script(session_path)
    if not script_content:
        result['errors'].append("Could not load SSML script")
        result['valid'] = False
        return result

    # Strip tags to get text content for pattern matching
    text_content = re.sub(r'<[^>]+>', ' ', script_content)
    text_content = re.sub(r'\s+', ' ', text_content)

    # Check required patterns
    required_patterns = outcome_spec.get('required_patterns', {})
    result['required_patterns'] = check_required_patterns(script_content, required_patterns, verbose)

    if result['required_patterns']['failed']:
        result['valid'] = False

    # Check suggested patterns
    suggested_patterns = outcome_spec.get('suggested_patterns', [])
    result['suggested_patterns'] = check_suggested_patterns(script_content, suggested_patterns)

    for absent in result['suggested_patterns']['absent']:
        result['warnings'].append(f"Suggested pattern '{absent}' not detected")

    # Check integration actions
    result['integration_actions'] = check_integration_actions(text_content)

    # At least one integration action is required
    if not result['integration_actions']['found']:
        result['valid'] = False
        result['errors'].append("No integration actions detected (at least 1 required)")

    # Check for outcome-specific integration actions
    primary_actions = outcome_spec.get('integration_actions', {}).get('primary', [])
    matching_actions = [a for a in primary_actions if a in result['integration_actions']['found']]

    if not matching_actions and primary_actions:
        result['warnings'].append(
            f"None of the primary integration actions for '{desired_outcome}' detected: {primary_actions}"
        )

    return result


def print_validation_report(result: Dict, verbose: bool = False):
    """Print a formatted validation report."""
    print()
    print("=" * 70)
    print("   Outcome Validation Report v1.0")
    print("=" * 70)
    print()

    if result['outcome']:
        print(f"   Desired Outcome: {result['outcome'].upper()}")
    else:
        print("   Desired Outcome: (not specified)")
    print()

    # Errors
    if result['errors']:
        print("   ERRORS:")
        for error in result['errors']:
            print(f"   └── {error}")
        print()

    # Required patterns
    if result['required_patterns']:
        rp = result['required_patterns']
        print("   Required Patterns:")

        for pattern_name in rp.get('passed', []):
            detail = rp['details'].get(pattern_name, {})
            print(f"   ├── ✅ {pattern_name}: {detail.get('found', 0)}/{detail.get('required', 1)}")
            if verbose and detail.get('rationale'):
                print(f"   │      Rationale: {detail['rationale']}")

        for pattern_name in rp.get('failed', []):
            detail = rp['details'].get(pattern_name, {})
            print(f"   ├── ❌ {pattern_name}: {detail.get('found', 0)}/{detail.get('required', 1)} (need {detail.get('deficit', 0)} more)")
            if detail.get('placement'):
                print(f"   │      Placement: {detail['placement']}")
            if verbose and detail.get('rationale'):
                print(f"   │      Rationale: {detail['rationale']}")

        print()

    # Suggested patterns
    if result['suggested_patterns']:
        sp = result['suggested_patterns']
        print("   Suggested Patterns:")

        for pattern in sp.get('present', []):
            print(f"   ├── ✅ {pattern}")

        for pattern in sp.get('absent', []):
            print(f"   ├── ⚠️  {pattern} (recommended)")

        print()

    # Integration actions
    if result['integration_actions']:
        ia = result['integration_actions']
        print("   Integration Actions:")

        for action in ia.get('found', []):
            print(f"   ├── ✅ {action}")

        if not ia.get('found'):
            print(f"   ├── ❌ No integration actions detected")

        print()

    # Warnings
    if result['warnings']:
        print("   Warnings:")
        for warning in result['warnings']:
            print(f"   └── ⚠️  {warning}")
        print()

    # Final verdict
    print("-" * 70)
    if result['valid']:
        print("   ✅ OUTCOME VALIDATION PASSED")
        print("      Script contains required patterns for stated outcome")
    else:
        print("   ❌ OUTCOME VALIDATION FAILED")
        print("      Script missing required patterns for stated outcome")
        print()
        print("   To fix:")
        for pattern_name in result['required_patterns'].get('failed', []):
            detail = result['required_patterns']['details'].get(pattern_name, {})
            desc = detail.get('description', pattern_name)
            print(f"   • Add {detail.get('deficit', 1)} more {desc}")
        for error in result['errors']:
            if 'integration' in error.lower():
                print("   • Add at least one integration action (hydration, breath, threshold, etc.)")

    print("-" * 70)
    print()


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Validate that a script contains required patterns for its stated outcome'
    )
    parser.add_argument('session_path', help='Path to session directory')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed output')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    if not os.path.isdir(args.session_path):
        print(f"Error: Not a directory: {args.session_path}")
        sys.exit(1)

    result = validate_outcome(args.session_path, verbose=args.verbose)

    if args.json:
        import json
        print(json.dumps(result, indent=2))
    else:
        print_validation_report(result, verbose=args.verbose)

    sys.exit(0 if result['valid'] else 1)


if __name__ == '__main__':
    main()
