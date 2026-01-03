#!/usr/bin/env python3
"""
Validate content quality for answer pages.

Checks that completed pages meet AEO quality standards:
- Short Answer: 20-35 words
- Presence of all required sections
- No forbidden marketing language
- Use of causal language
- Related question count = 5
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple
import yaml

# Forbidden words/phrases (marketing language)
FORBIDDEN_PATTERNS = [
    r'\balways\b',
    r'\bguaranteed?\b',
    r'\bthe best\b',
    r'\bproven\b',
    r'\bultimate\b',
    r'\bmust-have\b',
    r'\blife-changing\b',
    r'\bgroundbreaking\b',
    r'\brevolutionary\b',
]

# Causal language patterns (good)
CAUSAL_PATTERNS = [
    r'\bbecause\b',
    r'\bwhen\b',
    r'\bresults in\b',
    r'\bleads to\b',
    r'\bcauses?\b',
    r'\bdue to\b',
    r'\bthrough\b',
    r'\bvia\b',
]

def count_words(text: str) -> int:
    """Count words in text."""
    # Remove markdown, code, and special characters
    cleaned = re.sub(r'[^\w\s]', ' ', text)
    words = cleaned.split()
    return len(words)

def extract_short_answer(content: str) -> str:
    """Extract the Short Answer section content."""
    # Look for Short Answer section
    pattern = r'Short Answer.*?</p>\s*<p[^>]*>(.*?)</p>'
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)

    if match:
        answer = match.group(1)
        # Remove HTML tags
        answer = re.sub(r'<[^>]+>', '', answer)
        return answer.strip()

    return ""

def extract_section_content(content: str, section_heading: str) -> str:
    """Extract content from a specific section."""
    # Look for section heading and following paragraph
    pattern = rf'{section_heading}.*?</h2>\s*<p[^>]*>(.*?)</p>'
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)

    if match:
        text = match.group(1)
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        return text.strip()

    return ""

def count_related_questions(content: str) -> int:
    """Count related question links."""
    # Count Link components with HelpCircle
    pattern = r'<Link[^>]*href=["\']\/consciousness\/altered-states\/'
    matches = re.findall(pattern, content)
    return len(matches)

def check_for_forbidden_language(text: str) -> List[str]:
    """Check for forbidden marketing language."""
    violations = []

    for pattern in FORBIDDEN_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            violations.append(f"Forbidden word: {matches[0]}")

    return violations

def check_for_causal_language(text: str) -> bool:
    """Check if text uses causal language."""
    for pattern in CAUSAL_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True

    return False

def validate_page(file_path: Path) -> Dict:
    """Validate a single page against quality standards."""
    if not file_path.exists():
        return {"status": "missing", "errors": ["File not found"]}

    content = file_path.read_text()

    # Check for placeholder content
    if re.search(r'\[Claude:', content):
        return {"status": "placeholder", "errors": []}

    errors = []
    warnings = []

    # Extract sections
    short_answer = extract_short_answer(content)
    why_matters = extract_section_content(content, "Why This Matters")
    where_changes = extract_section_content(content, "Where This Changes")

    # Validate Short Answer
    if not short_answer:
        errors.append("Missing Short Answer section")
    else:
        word_count = count_words(short_answer)
        if word_count < 20:
            errors.append(f"Short Answer too short: {word_count} words (need 20-35)")
        elif word_count > 35:
            warnings.append(f"Short Answer too long: {word_count} words (target 20-35)")

    # Validate Why This Matters
    if not why_matters:
        errors.append("Missing 'Why This Matters' section")
    else:
        # Should use causal language
        if not check_for_causal_language(why_matters):
            warnings.append("'Why This Matters' lacks causal language (because, when, leads to, etc.)")

        # Check for forbidden language
        violations = check_for_forbidden_language(why_matters)
        if violations:
            errors.extend([f"Why This Matters: {v}" for v in violations])

    # Validate Where This Changes
    if not where_changes:
        errors.append("Missing 'Where This Changes' section")
    else:
        # Check for forbidden language
        violations = check_for_forbidden_language(where_changes)
        if violations:
            errors.extend([f"Where This Changes: {v}" for v in violations])

    # Validate Related Questions count
    related_count = count_related_questions(content)
    if related_count != 5:
        warnings.append(f"Related questions count: {related_count} (expected 5)")

    # Determine status
    if errors:
        status = "invalid"
    elif warnings:
        status = "warning"
    else:
        status = "valid"

    return {
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "metrics": {
            "short_answer_words": count_words(short_answer) if short_answer else 0,
            "related_questions": related_count,
            "has_causal_language": check_for_causal_language(why_matters) if why_matters else False
        }
    }

def validate_all_pages(frontend_base: Path) -> Dict:
    """Validate all answer pages."""
    yaml_path = Path(__file__).parent / "altered_states_questions.yaml"

    if not yaml_path.exists():
        return {"error": "YAML file not found"}

    with open(yaml_path) as f:
        data = yaml.safe_load(f)

    hub_path = "consciousness/altered-states"
    base_path = frontend_base / "app" / hub_path.replace("/", Path("/").as_posix())

    results = {
        "total": 0,
        "valid": 0,
        "warnings": 0,
        "invalid": 0,
        "placeholder": 0,
        "missing": 0,
        "pages": []
    }

    for cluster in data['clusters']:
        cluster_slug = cluster['category_slug']

        for q_data in cluster['questions']:
            question = q_data['question']

            # Convert question to slug
            slug = question.lower()
            slug = re.sub(r'[^\w\s-]', '', slug)
            slug = re.sub(r'[-\s]+', '-', slug)
            slug = slug.strip('-')

            page_path = base_path / cluster_slug / slug / "page.tsx"

            validation = validate_page(page_path)

            results['total'] += 1
            status = validation['status']

            if status == 'valid':
                results['valid'] += 1
            elif status == 'warning':
                results['warnings'] += 1
            elif status == 'invalid':
                results['invalid'] += 1
            elif status == 'placeholder':
                results['placeholder'] += 1
            elif status == 'missing':
                results['missing'] += 1

            if status in ['invalid', 'warning']:
                results['pages'].append({
                    'question': question,
                    'cluster': cluster['name'],
                    'path': str(page_path.relative_to(frontend_base)),
                    'status': status,
                    'errors': validation.get('errors', []),
                    'warnings': validation.get('warnings', []),
                    'metrics': validation.get('metrics', {})
                })

    return results

def print_validation_report(results: Dict, verbose: bool = False):
    """Print formatted validation report."""
    print(f"\n{'='*80}")
    print(f"  Content Quality Validation Report")
    print(f"{'='*80}\n")

    total = results['total']
    valid = results['valid']
    warnings = results['warnings']
    invalid = results['invalid']
    placeholder = results['placeholder']
    missing = results['missing']

    print(f"VALIDATION SUMMARY:")
    print(f"  Total Pages:        {total}")
    print(f"  ✓ Valid:            {valid:3d}")
    print(f"  ⚠ Warnings:         {warnings:3d}")
    print(f"  ✗ Invalid:          {invalid:3d}")
    print(f"  ○ Placeholder:      {placeholder:3d}")
    print(f"  - Missing:          {missing:3d}")
    print()

    if results['pages']:
        print(f"{'─'*80}\n")
        print(f"ISSUES FOUND:\n")

        for page in results['pages']:
            status_icon = "⚠" if page['status'] == 'warning' else "✗"
            print(f"{status_icon} {page['question']}")
            print(f"   Cluster: {page['cluster']}")
            print(f"   Path: {page['path']}")

            if page['errors']:
                print(f"   Errors:")
                for error in page['errors']:
                    print(f"     • {error}")

            if page['warnings']:
                print(f"   Warnings:")
                for warning in page['warnings']:
                    print(f"     • {warning}")

            if verbose and page['metrics']:
                print(f"   Metrics:")
                for key, value in page['metrics'].items():
                    print(f"     • {key}: {value}")

            print()

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Validate answer page content quality')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Show detailed metrics')
    parser.add_argument('--frontend-path',
                       default='/home/rsalars/Projects/dreamweaving/salarsu/frontend',
                       help='Path to frontend directory')

    args = parser.parse_args()

    frontend_base = Path(args.frontend_path)

    if not frontend_base.exists():
        print(f"Error: Frontend path not found: {frontend_base}")
        return 1

    results = validate_all_pages(frontend_base)

    if "error" in results:
        print(f"Error: {results['error']}")
        return 1

    print_validation_report(results, verbose=args.verbose)

    # Exit with error code if there are invalid pages
    if results['invalid'] > 0:
        return 1

    return 0

if __name__ == '__main__':
    exit(main())
