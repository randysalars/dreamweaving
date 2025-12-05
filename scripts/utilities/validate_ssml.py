#!/usr/bin/env python3
"""
SSML Validation Utility v2.0
Validates SSML syntax, hypnotic patterns, distribution, rhythm, and safety

Features:
- Basic SSML syntax validation
- Hypnotic pattern presence checks
- Distribution analysis (embedded commands, fractionation loops)
- Rhythm/cadence analysis (sentence length variation)
- Safety clause enforcement (HARD FAIL if missing)
- Breath pacing by section

Usage:
    python scripts/utilities/validate_ssml.py path/to/script.ssml
"""

import sys
import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path

# Version 2.0 - Enhanced with distribution, rhythm, and safety checks

def strip_ns(tag):
    """Return tag name without namespace."""
    return tag.split('}', 1)[-1] if '}' in tag else tag


def check_safety_clause(text_content):
    """
    HARD FAIL if no safety/autonomy clause in first 500 words.
    Returns (passed: bool, message: str)
    """
    words = text_content.split()
    first_500 = ' '.join(words[:500])

    safety_patterns = [
        r'remain.*in control',
        r'return to.*awareness',
        r'at any time.*choose',
        r'completely safe',
        r'fully aware.*in control',
        r'safe.*throughout',
        r'your choice.*return',
    ]

    for pattern in safety_patterns:
        if re.search(pattern, first_500, re.IGNORECASE):
            return True, "Safety/autonomy clause present in opening"

    return False, "No safety/autonomy clause in first 500 words"


def analyze_emphasis_distribution(content, word_count):
    """
    Analyze distribution of embedded commands (emphasis tags).
    Returns dict with metrics and status.
    """
    # Find all emphasis tag positions in content
    emphasis_positions = [m.start() for m in re.finditer(r'<emphasis', content)]
    emphasis_count = len(emphasis_positions)

    # Calculate per 100 words
    per_100 = (emphasis_count / word_count * 100) if word_count > 0 else 0

    result = {
        'total': emphasis_count,
        'per_100_words': round(per_100, 1),
        'min_required': 10,
        'max_per_100': 8,
        'min_per_100': 2,
        'status': 'ok',
        'issues': []
    }

    if emphasis_count < 10:
        result['status'] = 'warning'
        result['issues'].append(f"Only {emphasis_count} embedded commands (minimum 10)")

    if per_100 > 8:
        result['status'] = 'warning'
        result['issues'].append(f"Too dense: {per_100:.1f} per 100 words (max 8)")

    if per_100 < 2 and word_count > 500:
        result['status'] = 'warning'
        result['issues'].append(f"Too sparse: {per_100:.1f} per 100 words (min 2)")

    return result


def analyze_fractionation_distribution(text_content):
    """
    Analyze fractionation loop positions to ensure proper distribution.
    Returns dict with metrics and status.
    """
    # Patterns that indicate fractionation loops
    loop_patterns = [
        r'deeper.*natural.*natural.*deeper',
        r'relaxed.*safe.*safe.*relaxed',
        r'go.*deeper.*wait.*already.*deeper',
        r'deeper you go.*more.*more.*deeper',
        r'comfortable.*safe.*safe.*comfortable',
        r'open.*trusting.*trusting.*open',
    ]

    positions = []
    for pattern in loop_patterns:
        matches = list(re.finditer(pattern, text_content, re.IGNORECASE | re.DOTALL))
        for m in matches:
            # Calculate position as percentage of text
            pos_pct = (m.start() / len(text_content) * 100) if text_content else 0
            positions.append(pos_pct)

    positions.sort()

    result = {
        'count': len(positions),
        'positions': [round(p, 1) for p in positions],
        'min_required': 2,
        'expected_ranges': [(15, 25), (50, 75)],
        'status': 'ok',
        'issues': []
    }

    if len(positions) < 2:
        result['status'] = 'warning'
        result['issues'].append(f"Only {len(positions)} fractionation loops (minimum 2)")

    # Check if loops are in expected positions
    has_early_loop = any(15 <= p <= 35 for p in positions)
    has_peak_loop = any(45 <= p <= 80 for p in positions)

    if positions and not has_early_loop:
        result['issues'].append("No fractionation loop in induction area (15-35%)")
    if positions and not has_peak_loop:
        result['issues'].append("No fractionation loop at journey peak (45-80%)")

    return result


def analyze_rhythm(text_content):
    """
    Analyze sentence length variation for hypnotic rhythm.
    Returns dict with metrics and status.
    """
    # Split into sentences (accounting for ellipsis as continuation, not sentence end)
    # Use . ! ? followed by space or tag as sentence boundaries
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text_content)
    sentences = [s.strip() for s in sentences if s.strip() and len(s.split()) > 2]

    if not sentences:
        return {
            'status': 'warning',
            'issues': ['Could not parse sentences for rhythm analysis']
        }

    lengths = [len(s.split()) for s in sentences]

    if not lengths:
        return {
            'status': 'warning',
            'issues': ['No measurable sentences found']
        }

    avg_length = sum(lengths) / len(lengths)
    short_count = sum(1 for l in lengths if l <= 10)
    long_count = sum(1 for l in lengths if l > 35)
    run_on_count = sum(1 for l in lengths if l > 45)

    short_pct = (short_count / len(lengths) * 100) if lengths else 0

    result = {
        'sentence_count': len(sentences),
        'avg_length': round(avg_length, 1),
        'short_pct': round(short_pct, 1),
        'long_count': long_count,
        'run_on_count': run_on_count,
        'target_avg': (12, 28),
        'target_short_pct': 20,
        'status': 'ok',
        'issues': []
    }

    if avg_length < 10:
        result['issues'].append(f"Sentences too short (avg {avg_length:.1f} words)")
    elif avg_length > 32:
        result['issues'].append(f"Sentences too long (avg {avg_length:.1f} words)")

    if short_pct < 15:
        result['issues'].append(f"Need more short sentences for emphasis ({short_pct:.0f}% < 15%)")

    if run_on_count > 0:
        result['status'] = 'warning'
        result['issues'].append(f"{run_on_count} run-on sentences (>45 words)")

    return result


def analyze_breath_pacing(content, word_count):
    """
    Analyze break frequency relative to word count.
    Returns dict with metrics.
    """
    break_count = len(re.findall(r'<break', content))

    # Find words between breaks
    # Split content by break tags
    segments = re.split(r'<break[^>]*/?>', content)

    max_words_between = 0
    for segment in segments:
        # Strip tags to get just text
        text_only = re.sub(r'<[^>]+>', '', segment)
        words = len(text_only.split())
        if words > max_words_between:
            max_words_between = words

    result = {
        'total_breaks': break_count,
        'breaks_per_100_words': round(break_count / word_count * 100, 1) if word_count else 0,
        'max_words_between': max_words_between,
        'recommended_max': 60,  # General guideline
        'status': 'ok',
        'issues': []
    }

    if max_words_between > 80:
        result['status'] = 'warning'
        result['issues'].append(f"Long stretch without break: {max_words_between} words (max ~60-80)")

    if break_count < word_count / 100:
        result['issues'].append("Low break density - add more <break> tags for pacing")

    return result

def validate_ssml(file_path):
    """Validate SSML file and provide detailed feedback"""

    print("=" * 70)
    print("   SSML Validation Utility v2.0")
    print("=" * 70)
    print()

    # Check file exists
    if not os.path.exists(file_path):
        print(f"❌ Error: File not found: {file_path}")
        return False

    print(f"📄 Validating: {file_path}")
    print()

    # Read file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

    # Check file size
    file_size = len(content.encode('utf-8'))
    print(f"📊 File size: {file_size:,} bytes")

    if file_size > 5000:
        print(f"⚠️  Warning: File is large ({file_size} bytes)")
        print(f"   Recommend using generate_audio_chunked.py")
    print()

    # Validate XML syntax
    try:
        root = ET.fromstring(content)
        print("✅ XML syntax is valid")
    except ET.ParseError as e:
        print(f"❌ XML Parse Error: {e}")
        print(f"   Line {e.position[0]}, Column {e.position[1]}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    # Check for <speak> root element (allow namespace)
    tag_name = strip_ns(root.tag)
    if tag_name != 'speak':
        print(f"❌ Error: Root element should be <speak>, found <{root.tag}>")
        return False
    print("✅ Root <speak> element present")

    # Check for required attributes
    if 'version' not in root.attrib:
        print("⚠️  Warning: <speak> missing 'version' attribute")
    else:
        print(f"✅ Version: {root.attrib['version']}")

    lang_value = root.attrib.get('xml:lang') or root.attrib.get('{http://www.w3.org/XML/1998/namespace}lang')
    if not lang_value:
        print("⚠️  Warning: <speak> missing 'xml:lang' attribute")
    else:
        print(f"✅ Language: {lang_value}")

    print()

    # Analyze content
    print("📋 Content Analysis:")
    print()

    # Count elements
    prosody_count = sum(1 for elem in root.iter() if strip_ns(elem.tag) == 'prosody')
    break_count = sum(1 for elem in root.iter() if strip_ns(elem.tag) == 'break')
    phoneme_count = sum(1 for elem in root.iter() if strip_ns(elem.tag) == 'phoneme')
    emphasis_count = sum(1 for elem in root.iter() if strip_ns(elem.tag) == 'emphasis')

    print(f"   <prosody> tags: {prosody_count}")
    print(f"   <break> tags: {break_count}")
    print(f"   <phoneme> tags: {phoneme_count}")
    print(f"   <emphasis> tags: {emphasis_count} (embedded commands)")

    # Check emphasis count against minimum (10 required)
    if emphasis_count < 10:
        print(f"   ⚠️  Low emphasis count: {emphasis_count}/10 minimum")
    else:
        print(f"   ✅ Embedded commands: {emphasis_count} (≥10 required)")
    print()

    # Estimate duration
    text_content = ''.join(root.itertext())
    word_count = len(text_content.split())

    # Rough estimate: 150 words per minute for normal speech
    # Hypnosis is slower (rate=0.85), so ~130 wpm
    estimated_minutes = word_count / 130

    print(f"   Word count: {word_count:,}")
    print(f"   Estimated duration: {estimated_minutes:.1f} minutes")
    print()

    # =========================================================================
    # SAFETY CHECK (HARD FAIL)
    # =========================================================================
    print("🛡️ Safety Check:")
    print()

    safety_passed, safety_msg = check_safety_clause(text_content)
    if safety_passed:
        print(f"   ✅ {safety_msg}")
    else:
        print(f"   ❌ CRITICAL: {safety_msg}")
        print("      Must include language about listener control within first 500 words")
        print("      Example: 'You remain fully in control throughout this experience...'")
        print()
        print("=" * 70)
        print("❌ VALIDATION FAILED - Safety clause required")
        print("=" * 70)
        return False  # HARD FAIL

    print()

    # Check for hypnotic patterns
    print("🎭 Hypnotic Pattern Check:")
    print()

    # Check for fractionation loops (circular deepening patterns)
    fractionation_patterns = [
        r'deeper.*natural.*natural.*deeper',
        r'relaxed.*safe.*safe.*relaxed',
        r'go.*deeper.*wait.*already.*deeper',
    ]
    fractionation_found = 0
    for pattern in fractionation_patterns:
        if re.search(pattern, text_content, re.IGNORECASE | re.DOTALL):
            fractionation_found += 1

    if fractionation_found >= 2:
        print(f"   ✅ Fractionation loops: {fractionation_found} found (≥2 required)")
    elif fractionation_found == 1:
        print(f"   ⚠️  Fractionation loops: {fractionation_found}/2 minimum")
    else:
        print("   ⚠️  No fractionation loops detected (2 required)")

    # Check for yes-sets (3+ truisms in sequence)
    yes_set_pattern = r"you'?re\s+\w+.*you'?re\s+\w+.*you'?re\s+\w+"
    if re.search(yes_set_pattern, text_content, re.IGNORECASE | re.DOTALL):
        print("   ✅ Yes-set pattern detected")
    else:
        print("   ⚠️  No yes-set detected (3+ truisms recommended in opening)")

    # Check for temporal dissociation
    temporal_pattern = r'(minutes|hours|days)\s+ahead'
    if re.search(temporal_pattern, text_content, re.IGNORECASE):
        print("   ✅ Temporal dissociation/future pacing detected")
    else:
        print("   ⚠️  No temporal dissociation detected (required in integration)")

    # Check for double-binds
    double_bind_patterns = [
        r'(can|may)\s+\w+.*or\s+\w+.*whichever',
        r'choose\s+to.*or.*wait',
        r'quickly\s+or\s+slowly',
    ]
    double_bind_found = any(re.search(p, text_content, re.IGNORECASE) for p in double_bind_patterns)
    if double_bind_found:
        print("   ✅ Double-bind pattern detected")
    else:
        print("   ⚠️  No double-bind detected (recommended in journey)")

    # Check for rate violations (should always be 1.0)
    rate_violations = re.findall(r'rate=["\']0\.\d+["\']', content)
    if rate_violations:
        print(f"   ❌ Rate violations found: {rate_violations[:3]}")
        print("      Use rate=\"1.0\" for all sections (L015)")
    else:
        print("   ✅ All prosody rates are 1.0 (correct)")

    print()

    # =========================================================================
    # ADVANCED PSYCHOLOGICAL PATTERNS (Phase 1-4 Implementation)
    # =========================================================================
    print("🧠 Advanced Psychological Patterns:")
    print()

    # Phase 1: NLP Submodality Shifts
    submodality_patterns = [
        r'(shrink|smaller|tiny|distance|far\s+away|fading)',
        r'growing\s+smaller',
        r'(brighten|brighter|expand|larger|vivid)',
        r'fills?\s+(your\s+)?(entire\s+)?awareness',
        r'(color|colour)\s+(shift|transform|change)',
        r'(weight|heavy)\s+(lift|dissolve|transform)',
        r'becoming\s+(lighter|weightless)',
    ]
    submodality_found = sum(1 for p in submodality_patterns if re.search(p, text_content, re.IGNORECASE))
    if submodality_found >= 1:
        print(f"   ✅ Submodality shifts: {submodality_found} types detected")
    else:
        print("   ⚠️  No submodality shifts detected (recommended for transformation)")

    # Phase 1: Expectancy Priming
    expectancy_patterns = [
        r'(most\s+people|many\s+(people|have))\s+(find|found|experience)',
        r'(your\s+mind|you)\s+already\s+know',
        r'(natural|innate)\s+(ability|capacity|wisdom)',
        r'something\s+(powerful|profound)\s+(is\s+about|will)',
        r'(open|ready|prepared)\s+to\s+receive',
    ]
    expectancy_found = sum(1 for p in expectancy_patterns if re.search(p, text_content, re.IGNORECASE))
    if expectancy_found >= 2:
        print(f"   ✅ Expectancy priming: {expectancy_found} patterns (≥2 required)")
    elif expectancy_found == 1:
        print(f"   ⚠️  Expectancy priming: only {expectancy_found}/2 minimum")
    else:
        print("   ⚠️  No expectancy priming detected (add to pre-talk)")

    # Phase 1: Identity Reframing
    identity_patterns = [
        r'(version|self)\s+(of\s+you|who)\s+(has\s+already|that\s+has)',
        r'step\s+(into|forward\s+into)\s+(this|that|the)\s+(new|version)',
        r'becoming\s+who\s+you\s+(already\s+)?are',
        r'(always\s+been|has\s+always\s+been)\s+part\s+of\s+you',
        r'this\s+is\s+who\s+you\s+(are|have\s+always\s+been)',
    ]
    identity_found = any(re.search(p, text_content, re.IGNORECASE) for p in identity_patterns)
    if identity_found:
        print("   ✅ Identity reframing detected")
    else:
        print("   ⚠️  No identity reframing detected (recommended for transformation)")

    # Phase 2: Parts Integration
    parts_patterns = [
        r'(part|parts)\s+of\s+(you|yourself)',
        r'(different|various|all)\s+parts',
        r'(thank|appreciate)\s+(this|that)\s+part',
        r'(parts|all\s+parts)\s+(coming|come)\s+together',
    ]
    parts_found = any(re.search(p, text_content, re.IGNORECASE) for p in parts_patterns)
    if parts_found:
        print("   ✅ Parts integration language detected")
    else:
        print("   ℹ️  No parts integration (optional for healing outcomes)")

    # Phase 2: Schema Rewriting
    schema_patterns = [
        r'(old|ancient|deep)\s+(belief|pattern|story)',
        r'(no\s+longer|doesn\'t)\s+(serve|apply|fit)',
        r'(new|deeper)\s+(truth|belief|knowing)',
        r'settling\s+into\s+(your\s+)?(cells|bones|body)',
        r'(you\s+are|I\s+am)\s+(enough|worthy|complete)',
    ]
    schema_found = any(re.search(p, text_content, re.IGNORECASE) for p in schema_patterns)
    if schema_found:
        print("   ✅ Schema rewriting detected")
    else:
        print("   ℹ️  No schema rewriting (optional for transformation)")

    # Phase 3: Association/Dissociation
    assoc_dissoc_patterns = [
        r'step\s+(back|away)\s+from',
        r'(watch|observe|see)\s+(yourself|from\s+outside)',
        r'step\s+(fully\s+)?into\s+(this|that|the)',
        r'(fill|fills)\s+every\s+part\s+of\s+you',
    ]
    assoc_dissoc_found = any(re.search(p, text_content, re.IGNORECASE) for p in assoc_dissoc_patterns)
    if assoc_dissoc_found:
        print("   ✅ Association/dissociation cues detected")
    else:
        print("   ℹ️  No association/dissociation (optional for healing)")

    # Phase 4: Symbolic Catharsis
    catharsis_patterns = [
        r'(cast|throw|release)\s+(into|to)\s+(the\s+)?(fire|flame)',
        r'(wash|water|stream|river)\s+(away|dissolve|carry)',
        r'(wind|breeze)\s+(carry|scatter)',
        r'(return|bury|place)\s+(to|in|into)\s+(the\s+)?earth',
        r'(dissolve|melt)\s+(into|in)\s+(pure\s+)?light',
    ]
    catharsis_found = any(re.search(p, text_content, re.IGNORECASE) for p in catharsis_patterns)
    if catharsis_found:
        print("   ✅ Symbolic catharsis detected")
    else:
        print("   ℹ️  No symbolic catharsis (optional for release outcomes)")

    print()

    # =========================================================================
    # DISTRIBUTION ANALYSIS (Phase 2C Enhancement)
    # =========================================================================
    print("📊 Distribution Analysis:")
    print()

    # Analyze embedded command distribution
    emphasis_dist = analyze_emphasis_distribution(content, word_count)
    print("   Embedded Commands:")
    print(f"   ├── Total: {emphasis_dist['total']} ", end="")
    if emphasis_dist['total'] >= 10:
        print("(✅ ≥10)")
    else:
        print(f"(⚠️ need {10 - emphasis_dist['total']} more)")
    print(f"   ├── Per 100 words: {emphasis_dist['per_100_words']} ", end="")
    if 2 <= emphasis_dist['per_100_words'] <= 8:
        print("(✅ 2-8 range)")
    else:
        print("(⚠️ outside 2-8 range)")
    for issue in emphasis_dist['issues']:
        print(f"   └── ⚠️ {issue}")
    print()

    # Analyze fractionation loop distribution
    frac_dist = analyze_fractionation_distribution(text_content)
    print("   Fractionation Loops:")
    print(f"   ├── Count: {frac_dist['count']} ", end="")
    if frac_dist['count'] >= 2:
        print("(✅ ≥2)")
    else:
        print("(⚠️ need more)")
    if frac_dist['positions']:
        pos_str = ", ".join([f"{p}%" for p in frac_dist['positions']])
        print(f"   ├── Positions: {pos_str}")
    for issue in frac_dist['issues']:
        print(f"   └── ⚠️ {issue}")
    print()

    # Analyze sentence rhythm
    rhythm = analyze_rhythm(text_content)
    print("   Sentence Rhythm:")
    if 'sentence_count' in rhythm:
        print(f"   ├── Average length: {rhythm['avg_length']} words ", end="")
        if 12 <= rhythm['avg_length'] <= 28:
            print("(✅ 12-28 range)")
        else:
            print("(⚠️ outside target)")
        print(f"   ├── Short sentences (<10 words): {rhythm['short_pct']}%")
        if rhythm['run_on_count'] > 0:
            print(f"   └── ⚠️ {rhythm['run_on_count']} run-on sentences (>45 words)")
    for issue in rhythm.get('issues', []):
        print(f"   └── ⚠️ {issue}")
    print()

    # Analyze breath pacing
    pacing = analyze_breath_pacing(content, word_count)
    print("   Breath Pacing:")
    print(f"   ├── Total breaks: {pacing['total_breaks']}")
    print(f"   ├── Max words between breaks: {pacing['max_words_between']} ", end="")
    if pacing['max_words_between'] <= 80:
        print("(✅ <80)")
    else:
        print("(⚠️ too long)")
    for issue in pacing['issues']:
        print(f"   └── ⚠️ {issue}")

    print()

    # Check for common issues
    issues_found = False

    print("🔍 Checking for common issues:")
    print()

    # Check for unclosed tags
    open_tags = content.count('<prosody')
    close_tags = content.count('</prosody>')
    if open_tags != close_tags:
        print(f"⚠️  Warning: Unmatched <prosody> tags (open: {open_tags}, close: {close_tags})")
        issues_found = True

    # Check for very long sections without breaks
    if break_count < (word_count / 100):
        print(f"⚠️  Warning: Low break density (recommend more <break> tags)")
        print(f"   Current: {break_count} breaks for {word_count} words")
        print(f"   Recommend: ~{word_count // 50} breaks")
        issues_found = True

    # Check for breaks without preceding punctuation (L016)
    breaks_without_punct = re.findall(r'[a-zA-Z]\s*<break', content)
    if breaks_without_punct:
        print(f"⚠️  Warning: {len(breaks_without_punct)} breaks without preceding punctuation (L016)")
        print("   Add comma, ellipsis, or period before <break> tags to prevent word cutoff")
        issues_found = True

    # Check for sections marked with [PLACEHOLDER] or text markers (CRITICAL - will be read aloud!)
    if '[' in text_content and ']' in text_content:
        placeholders = re.findall(r'\[([^\]]+)\]', text_content)
        if placeholders:
            print(f"❌ CRITICAL: Found {len(placeholders)} square bracket markers (WILL BE READ ALOUD!):")
            for ph in placeholders[:5]:  # Show first 5
                print(f"   - [{ph}]")
            if len(placeholders) > 5:
                print(f"   ... and {len(placeholders) - 5} more")
            print()
            print("   🔧 FIX: Replace with proper SSML tags:")
            print("      [pause] → <break time=\"2s\"/>")
            print("      [breathe] → <break time=\"3s\"/>")
            print("      [PAUSE 2s] → <break time=\"2s\"/>")
            issues_found = True

    # Check for common text markers that will be vocalized
    text_markers = [
        ('pause', r'\bpause\b(?![^<]*>)'),  # 'pause' not inside tag
        ('breathe', r'\bbreathe\b(?![^<]*>)'),
        ('silence', r'\bsilence\b(?![^<]*>)'),
    ]
    for name, pattern in text_markers:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            print(f"⚠️  Warning: Found '{name}' as plain text (verify it's intentional)")
            issues_found = True

    # Check for special characters that might need escaping
    content_no_comments = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
    ampersands = [c for c in content_no_comments if c == '&']
    if ampersands:
        if content_no_comments.count('&') != content_no_comments.count('&amp;'):
            print("⚠️  Warning: Found unescaped '&' characters")
            print("   Use &amp; instead of & in text content")
            issues_found = True

    if not issues_found:
        print("✅ No common issues detected")

    print()

    # =========================================================================
    # OUTCOME VALIDATION (if session path can be derived)
    # =========================================================================
    outcome_valid = True
    session_path = None

    # Try to derive session path from file path
    file_path_obj = Path(file_path)
    if 'sessions' in file_path_obj.parts:
        # Find the session directory
        parts = file_path_obj.parts
        sessions_idx = parts.index('sessions')
        if len(parts) > sessions_idx + 1:
            session_path = Path(*parts[:sessions_idx + 2])

    if session_path and session_path.exists():
        manifest_path = session_path / 'manifest.yaml'
        if manifest_path.exists():
            print("🎯 Outcome Validation:")
            print()

            try:
                from validate_outcome import validate_outcome, print_validation_report

                result = validate_outcome(str(session_path))

                if result['outcome']:
                    # Only print brief summary here, not full report
                    print(f"   Desired outcome: {result['outcome']}")

                    rp = result.get('required_patterns', {})
                    passed = len(rp.get('passed', []))
                    failed = len(rp.get('failed', []))
                    total = passed + failed

                    if total > 0:
                        if failed == 0:
                            print(f"   ✅ Required patterns: {passed}/{total} present")
                        else:
                            print(f"   ⚠️  Required patterns: {passed}/{total} present")
                            for pattern_name in rp.get('failed', []):
                                detail = rp['details'].get(pattern_name, {})
                                print(f"      └── Missing: {pattern_name} ({detail.get('found', 0)}/{detail.get('required', 1)})")

                    ia = result.get('integration_actions', {})
                    if ia.get('found'):
                        print(f"   ✅ Integration actions: {len(ia['found'])} found")
                    else:
                        print("   ⚠️  No integration actions detected")

                    if not result['valid']:
                        outcome_valid = False
                        print()
                        print("   Run: python scripts/utilities/validate_outcome.py " + str(session_path) + " -v")
                        print("   for detailed outcome validation report")
                else:
                    print("   ℹ️  No desired_outcome in manifest - skipping outcome check")
                    print("      Add 'desired_outcome' field to enable outcome validation")

            except ImportError:
                print("   ℹ️  Outcome validator not available")
            except Exception as e:
                print(f"   ⚠️  Outcome validation error: {e}")

            print()

    print("=" * 70)
    if outcome_valid:
        print("✅ Validation Complete")
    else:
        print("⚠️  Validation Complete (outcome warnings)")
    print("=" * 70)
    print()

    return True


def main():
    if len(sys.argv) != 2:
        print("Usage: python validate_ssml.py <path-to-ssml-file>")
        print()
        print("Example:")
        print("  python scripts/utilities/validate_ssml.py sessions/my-session/script.ssml")
        sys.exit(1)

    file_path = sys.argv[1]

    if validate_ssml(file_path):
        print("✨ Your SSML is ready for audio generation!")
        sys.exit(0)
    else:
        print("❌ Please fix the issues above before generating audio")
        sys.exit(1)


if __name__ == '__main__':
    main()
