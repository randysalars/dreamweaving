#!/usr/bin/env python3
"""
Generate Sample Answer Pages

Creates 10 sample answer pages for testing the generation system
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from generators.simple_generator import SimplePageGenerator


# Sample questions from the Altered States section
SAMPLE_QUESTIONS = [
    {
        'question': 'What is an altered state of consciousness?',
        'cluster': 'Core Definitions & Foundations',
        'category_slug': 'definitions-foundations',
    },
    {
        'question': 'What defines normal waking consciousness?',
        'cluster': 'Core Definitions & Foundations',
        'category_slug': 'definitions-foundations',
    },
    {
        'question': 'How do altered states differ from everyday awareness?',
        'cluster': 'Core Definitions & Foundations',
        'category_slug': 'definitions-foundations',
    },
    {
        'question': 'Are altered states always intentional?',
        'cluster': 'Core Definitions & Foundations',
        'category_slug': 'definitions-foundations',
    },
    {
        'question': 'Can altered states occur spontaneously?',
        'cluster': 'Core Definitions & Foundations',
        'category_slug': 'definitions-foundations',
    },
    {
        'question': 'What are natural altered states of consciousness?',
        'cluster': 'Natural vs Induced Altered States',
        'category_slug': 'natural-vs-induced',
    },
    {
        'question': 'What causes natural altered states to occur?',
        'cluster': 'Natural vs Induced Altered States',
        'category_slug': 'natural-vs-induced',
    },
    {
        'question': 'How do altered states begin?',
        'cluster': 'Entry Pathways & Triggers',
        'category_slug': 'entry-pathways',
    },
    {
        'question': 'Can breathing techniques induce altered states?',
        'cluster': 'Entry Pathways & Triggers',
        'category_slug': 'entry-pathways',
    },
    {
        'question': 'Are altered states dangerous?',
        'cluster': 'Safety, Risks & Stability',
        'category_slug': 'safety-and-risks',
    },
]


def build_related_questions(questions, current_idx, generator):
    """Build related questions list for a given question"""
    related = []

    # Add same-cluster questions first
    current_cluster = questions[current_idx]['cluster']
    same_cluster = [
        q for i, q in enumerate(questions)
        if q['cluster'] == current_cluster and i != current_idx
    ]

    # Add up to 3 from same cluster
    for q in same_cluster[:3]:
        slug = generator._to_slug(q['question'])
        related.append({
            'text': q['question'],
            'url': f"/consciousness/altered-states/{q['category_slug']}/{slug}"
        })

    # Fill with other questions if needed
    if len(related) < 5:
        other = [
            q for i, q in enumerate(questions)
            if q['cluster'] != current_cluster and i != current_idx
        ]
        for q in other[:5 - len(related)]:
            slug = generator._to_slug(q['question'])
            related.append({
                'text': q['question'],
                'url': f"/consciousness/altered-states/{q['category_slug']}/{slug}"
            })

    return related


def main():
    print("=== Generating Sample Answer Pages ===\n")

    # Initialize generator
    generator = SimplePageGenerator(
        templates_dir='scripts/generation/templates',
        output_base='../salarsu/frontend/app'
    )

    generated_paths = []

    # Generate each sample page
    for idx, q_data in enumerate(SAMPLE_QUESTIONS):
        print(f"\n[{idx + 1}/{len(SAMPLE_QUESTIONS)}] {q_data['question']}")

        related = build_related_questions(SAMPLE_QUESTIONS, idx, generator)

        try:
            output_path = generator.generate_answer_page(
                question=q_data['question'],
                cluster_name=q_data['cluster'],
                category_slug=q_data['category_slug'],
                topic='altered_states',
                hub_path='consciousness/altered-states',
                related_questions=related
            )
            generated_paths.append(output_path)
        except Exception as e:
            print(f"  ✗ Error: {e}")

    # Summary
    print(f"\n\n=== Summary ===")
    print(f"Successfully generated: {len(generated_paths)}/{len(SAMPLE_QUESTIONS)} pages")
    print(f"\nGenerated pages:")
    for path in generated_paths:
        rel_path = path.relative_to(Path('../salarsu/frontend/app'))
        print(f"  - {rel_path}")

    print(f"\n✓ Sample pages generated successfully!")
    print(f"\nNext steps:")
    print(f"1. cd ../salarsu/frontend")
    print(f"2. npm run build")
    print(f"3. Check for TypeScript errors")


if __name__ == '__main__':
    main()
