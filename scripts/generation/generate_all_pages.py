#!/usr/bin/env python3
"""
Batch Answer Page Generator

Generates all answer pages for a topic from YAML question files.
Supports dry-run mode, incremental generation (skips existing), and progress tracking.

Usage:
    python3 generate_all_pages.py --topic altered_states
    python3 generate_all_pages.py --topic altered_states --dry-run
    python3 generate_all_pages.py --topic altered_states --force  # Regenerate existing
"""

import sys
import yaml
import argparse
from pathlib import Path
from typing import Dict, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from generators.simple_generator import SimplePageGenerator


def load_questions(topic: str) -> Dict:
    """Load questions from YAML file for given topic."""
    yaml_file = Path(__file__).parent / f"{topic}_questions.yaml"

    if not yaml_file.exists():
        raise FileNotFoundError(f"Question file not found: {yaml_file}")

    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)

    return data


def build_related_questions(all_questions: List[Dict], current_question: str,
                            current_cluster_id: str, generator, hub_path: str) -> List[Dict]:
    """
    Build related questions list with same-cluster priority.

    Returns up to 5 related questions:
    - Up to 3 from same cluster
    - Fill remainder from other clusters
    """
    related = []

    # Get all questions from same cluster
    same_cluster = []
    other_cluster = []

    for cluster in all_questions:
        for q_data in cluster['questions']:
            q_text = q_data['question']
            if q_text == current_question:
                continue  # Skip current question

            if cluster['id'] == current_cluster_id:
                same_cluster.append({
                    'question': q_text,
                    'category_slug': cluster['category_slug']
                })
            else:
                other_cluster.append({
                    'question': q_text,
                    'category_slug': cluster['category_slug']
                })

    # Add up to 3 from same cluster
    for q in same_cluster[:3]:
        slug = generator._to_slug(q['question'])
        related.append({
            'text': q['question'],
            'url': f"/{hub_path}/{q['category_slug']}/{slug}"
        })

    # Fill remainder with other clusters
    remaining = 5 - len(related)
    if remaining > 0:
        for q in other_cluster[:remaining]:
            slug = generator._to_slug(q['question'])
            related.append({
                'text': q['question'],
                'url': f"/{hub_path}/{q['category_slug']}/{slug}"
            })

    return related


def generate_topic_pages(topic: str, dry_run: bool = False, force: bool = False,
                        pending_only: bool = True):
    """
    Generate all pages for a topic.

    Args:
        topic: Topic name (e.g., 'altered_states')
        dry_run: If True, only print what would be generated
        force: If True, regenerate existing pages
        pending_only: If True, only generate pages marked as 'pending'
    """
    print(f"=== Batch Answer Page Generation: {topic.replace('_', ' ').title()} ===\n")

    # Load questions
    data = load_questions(topic)
    clusters = data['clusters']

    # Determine hub path based on topic
    hub_paths = {
        'altered_states': 'consciousness/altered-states',
        'meditation': 'consciousness/meditation',
        'memory': 'consciousness/memory'
    }
    hub_path = hub_paths.get(topic, f'{topic}')

    # Initialize generator
    generator = SimplePageGenerator(
        templates_dir=str(Path(__file__).parent / 'templates'),
        output_base=str(Path(__file__).parent.parent.parent / 'salarsu/frontend/app')
    )

    # Count statistics
    total_questions = 0
    questions_to_generate = 0
    completed_questions = 0
    skipped_questions = 0

    # First pass: count
    for cluster in clusters:
        for q_data in cluster.get('questions', []):
            total_questions += 1
            status = q_data.get('status', 'pending')

            if status == 'complete':
                completed_questions += 1
                if not force:
                    continue

            questions_to_generate += 1

    print(f"Total questions in {topic}: {total_questions}")
    print(f"Already completed: {completed_questions}")
    print(f"To generate: {questions_to_generate}")

    if dry_run:
        print("\n[DRY RUN MODE - No files will be created]\n")

    print(f"\n{'=' * 60}\n")

    # Second pass: generate
    generated_count = 0

    for cluster in clusters:
        cluster_id = cluster['id']
        cluster_name = cluster['name']
        category_slug = cluster['category_slug']
        cluster_desc = cluster.get('description', '')

        questions = cluster.get('questions', [])
        if not questions:
            continue

        print(f"\n## {cluster_name} ({len(questions)} questions)")
        print(f"Category: /{hub_path}/{category_slug}/\n")

        for idx, q_data in enumerate(questions):
            question = q_data['question']
            status = q_data.get('status', 'pending')

            # Skip if completed and not forcing
            if status == 'complete' and not force:
                print(f"  [{idx+1}/{len(questions)}] ✓ SKIP (already complete): {question}")
                skipped_questions += 1
                continue

            # Skip if only generating pending
            if pending_only and status != 'pending':
                print(f"  [{idx+1}/{len(questions)}] - SKIP (status: {status}): {question}")
                skipped_questions += 1
                continue

            print(f"  [{idx+1}/{len(questions)}] {'[DRY RUN]' if dry_run else 'GENERATING'}: {question}")

            if dry_run:
                generated_count += 1
                continue

            # Build related questions
            related = build_related_questions(clusters, question, cluster_id, generator, hub_path)

            # Generate page
            try:
                output_path = generator.generate_answer_page(
                    question=question,
                    cluster_name=cluster_name,
                    category_slug=category_slug,
                    topic=topic,
                    hub_path=hub_path,
                    related_questions=related
                )
                print(f"      → Created: {output_path}")
                generated_count += 1

            except Exception as e:
                print(f"      ✗ ERROR: {e}")

    # Summary
    print(f"\n{'=' * 60}")
    print("\n=== Generation Summary ===\n")
    print(f"Total questions: {total_questions}")
    print(f"Already completed: {completed_questions}")
    print(f"Skipped: {skipped_questions}")
    print(f"{'Would generate' if dry_run else 'Generated'}: {generated_count}")

    if not dry_run:
        print(f"\n✓ Answer pages created successfully!")
        print(f"\nNext steps:")
        print(f"1. Generate category index pages: python3 generate_category_pages.py {topic}")
        print(f"2. Verify TypeScript compilation: cd ../salarsu/frontend && npm run build")
        print(f"3. Start content filling (15-20 pages/day target)")


def main():
    parser = argparse.ArgumentParser(
        description="Generate answer pages from YAML question files"
    )
    parser.add_argument(
        '--topic',
        required=True,
        choices=['altered_states', 'meditation', 'memory'],
        help='Topic to generate pages for'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview what would be generated without creating files'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Regenerate existing pages (ignores "complete" status)'
    )
    parser.add_argument(
        '--all-status',
        action='store_true',
        help='Generate pages regardless of status (not just pending)'
    )

    args = parser.parse_args()

    try:
        generate_topic_pages(
            topic=args.topic,
            dry_run=args.dry_run,
            force=args.force,
            pending_only=not args.all_status
        )
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
