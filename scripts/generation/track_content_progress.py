#!/usr/bin/env python3
"""
Track content filling progress for answer pages.

Scans all answer pages to identify which have placeholder content vs completed content.
Provides progress reports by topic and cluster.
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple
import yaml

def is_placeholder_content(file_path: Path) -> bool:
    """Check if a page still has placeholder content markers."""
    content = file_path.read_text()

    # Check for Claude placeholder markers (case-sensitive, as they appear in generated files)
    placeholder_patterns = [
        r'\[Claude: Write',
        r'\[Claude: Provide',
        r'\[Claude: Generate',
        r'TODO:',
        r'PLACEHOLDER',
    ]

    for pattern in placeholder_patterns:
        if re.search(pattern, content):
            return True

    return False

def get_completion_status(file_path: Path) -> str:
    """Determine completion status of a page."""
    if not file_path.exists():
        return "missing"

    if is_placeholder_content(file_path):
        return "placeholder"

    return "complete"

def scan_altered_states_progress(frontend_base: Path) -> Dict:
    """Scan Altered States pages and generate progress report."""
    yaml_path = Path(__file__).parent / "altered_states_questions.yaml"

    if not yaml_path.exists():
        return {"error": "YAML file not found"}

    with open(yaml_path) as f:
        data = yaml.safe_load(f)

    hub_path = "consciousness/altered-states"
    base_path = frontend_base / "app" / hub_path.replace("/", Path("/").as_posix())

    results = {
        "topic": "Altered States of Consciousness",
        "total_questions": 0,
        "complete": 0,
        "placeholder": 0,
        "missing": 0,
        "clusters": []
    }

    for cluster in data['clusters']:
        cluster_slug = cluster['category_slug']
        cluster_name = cluster['name']
        cluster_results = {
            "name": cluster_name,
            "slug": cluster_slug,
            "total": len(cluster['questions']),
            "complete": 0,
            "placeholder": 0,
            "missing": 0,
            "pages": []
        }

        for q_data in cluster['questions']:
            question = q_data['question']
            status = q_data.get('status', 'pending')

            # Convert question to slug
            slug = question.lower()
            slug = re.sub(r'[^\w\s-]', '', slug)
            slug = re.sub(r'[-\s]+', '-', slug)
            slug = slug.strip('-')

            page_path = base_path / cluster_slug / slug / "page.tsx"

            file_status = get_completion_status(page_path)

            cluster_results['pages'].append({
                "question": question,
                "slug": slug,
                "status": file_status,
                "yaml_status": status,
                "path": str(page_path.relative_to(frontend_base))
            })

            # Count by status
            if file_status == "complete":
                cluster_results['complete'] += 1
            elif file_status == "placeholder":
                cluster_results['placeholder'] += 1
            else:
                cluster_results['missing'] += 1

            results['total_questions'] += 1

        results['clusters'].append(cluster_results)
        results['complete'] += cluster_results['complete']
        results['placeholder'] += cluster_results['placeholder']
        results['missing'] += cluster_results['missing']

    return results

def print_progress_report(results: Dict, verbose: bool = False):
    """Print formatted progress report."""
    print(f"\n{'='*80}")
    print(f"  {results['topic']} - Content Progress Report")
    print(f"{'='*80}\n")

    total = results['total_questions']
    complete = results['complete']
    placeholder = results['placeholder']
    missing = results['missing']

    complete_pct = (complete / total * 100) if total > 0 else 0
    placeholder_pct = (placeholder / total * 100) if total > 0 else 0

    print(f"OVERALL PROGRESS:")
    print(f"  Total Questions:    {total}")
    print(f"  ✓ Complete:         {complete:3d} ({complete_pct:5.1f}%)")
    print(f"  ⚠ Placeholder:      {placeholder:3d} ({placeholder_pct:5.1f}%)")
    print(f"  ✗ Missing:          {missing:3d}")
    print()

    # Progress bar
    bar_width = 60
    complete_width = int(complete_pct / 100 * bar_width)
    placeholder_width = int(placeholder_pct / 100 * bar_width)

    bar = '█' * complete_width + '░' * placeholder_width + ' ' * (bar_width - complete_width - placeholder_width)
    print(f"  [{bar}] {complete_pct:.1f}%\n")

    print(f"{'─'*80}\n")
    print(f"PROGRESS BY CLUSTER:\n")

    for cluster in results['clusters']:
        name = cluster['name']
        total_c = cluster['total']
        complete_c = cluster['complete']
        placeholder_c = cluster['placeholder']
        missing_c = cluster['missing']

        complete_pct_c = (complete_c / total_c * 100) if total_c > 0 else 0

        status_icon = "✓" if complete_c == total_c else "⚠" if placeholder_c > 0 else "✗"

        print(f"  {status_icon} {name}")
        print(f"     {complete_c}/{total_c} complete ({complete_pct_c:.0f}%)")

        if verbose and (placeholder_c > 0 or missing_c > 0):
            print(f"     Pending pages:")
            for page in cluster['pages']:
                if page['status'] in ['placeholder', 'missing']:
                    status_marker = "⚠" if page['status'] == 'placeholder' else "✗"
                    print(f"       {status_marker} {page['question']}")

        print()

    print(f"{'─'*80}\n")

    # Next steps
    if placeholder > 0:
        pages_per_day = 15
        days_remaining = (placeholder + pages_per_day - 1) // pages_per_day
        print(f"NEXT STEPS:")
        print(f"  • {placeholder} pages need content")
        print(f"  • At 15 pages/day: {days_remaining} days remaining")
        print(f"  • At 20 pages/day: {(placeholder + 19) // 20} days remaining")
        print()

def find_next_to_fill(results: Dict, count: int = 5) -> List[Dict]:
    """Find next N pages to fill, prioritizing by cluster."""
    pending_pages = []

    for cluster in results['clusters']:
        for page in cluster['pages']:
            if page['status'] == 'placeholder':
                pending_pages.append({
                    'cluster': cluster['name'],
                    'question': page['question'],
                    'path': page['path']
                })

    return pending_pages[:count]

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Track content filling progress')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Show detailed page-by-page status')
    parser.add_argument('--next', type=int, default=0,
                       help='Show next N pages to fill')
    parser.add_argument('--frontend-path',
                       default='/home/rsalars/Projects/dreamweaving/salarsu/frontend',
                       help='Path to frontend directory')

    args = parser.parse_args()

    frontend_base = Path(args.frontend_path)

    if not frontend_base.exists():
        print(f"Error: Frontend path not found: {frontend_base}")
        return 1

    results = scan_altered_states_progress(frontend_base)

    if "error" in results:
        print(f"Error: {results['error']}")
        return 1

    print_progress_report(results, verbose=args.verbose)

    if args.next > 0:
        next_pages = find_next_to_fill(results, args.next)
        print(f"NEXT {args.next} PAGES TO FILL:\n")
        for i, page in enumerate(next_pages, 1):
            print(f"{i}. [{page['cluster']}]")
            print(f"   {page['question']}")
            print(f"   Path: {page['path']}")
            print()

    return 0

if __name__ == '__main__':
    exit(main())
