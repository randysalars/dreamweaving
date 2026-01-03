#!/usr/bin/env python3
"""
Category Index Page Generator from YAML

Generates category index pages for all clusters in a topic's question YAML file.

Usage:
    python3 generate_category_pages_from_yaml.py --topic altered_states
    python3 generate_category_pages_from_yaml.py --topic altered_states --dry-run
"""

import sys
import yaml
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def load_questions(topic: str):
    """Load questions from YAML file."""
    yaml_file = Path(__file__).parent / f"{topic}_questions.yaml"

    if not yaml_file.exists():
        raise FileNotFoundError(f"Question file not found: {yaml_file}")

    with open(yaml_file, 'r') as f:
        return yaml.safe_load(f)


def generate_category_page(cluster, hub_path: str, output_base: Path, dry_run: bool = False):
    """Generate a single category index page."""
    category_slug = cluster['category_slug']
    category_name = cluster['name']
    category_desc = cluster.get('description', '')
    questions = cluster.get('questions', [])

    # Determine output path
    output_dir = output_base / hub_path / category_slug
    output_file = output_dir / 'page.tsx'

    if dry_run:
        print(f"  [DRY RUN] Would create: {output_file}")
        print(f"            Questions: {len(questions)}")
        return

    # Create directory if needed
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate component name
    component_name = ''.join(word.capitalize() for word in category_slug.split('-')) + 'Page'

    # Build page URL
    page_url = f"${{getSiteUrl()}}/{hub_path}/{category_slug}"

    # Generate TypeScript content
    content = f'''import type {{ Metadata }} from "next";
import Link from "next/link";
import {{ ArrowLeft, HelpCircle }} from "lucide-react";
import {{ getSiteUrl }} from "@/lib/siteUrl";

const pageUrl = `{page_url}`;

export const metadata: Metadata = {{
  title: "{category_name} | Altered States",
  description: "{category_desc}",
  alternates: {{ canonical: pageUrl }},
  openGraph: {{
    title: "{category_name}",
    description: "{category_desc}",
    url: pageUrl,
    type: "website",
  }},
}};

export default function {component_name}() {{
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-4xl space-y-8">
          <div className="space-y-2">
            <Link
              href="/{hub_path}"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Altered States
            </Link>
          </div>

          <div className="space-y-3">
            <h1 className="text-4xl font-semibold tracking-tight text-foreground">
              {category_name}
            </h1>
            <p className="text-lg text-muted-foreground">
              {category_desc}
            </p>
          </div>

          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Questions in this category
            </h2>
            <div className="grid gap-3">
'''

    # Add question links
    for q_data in questions:
        question = q_data['question']
        question_slug = question.lower()
        question_slug = question_slug.replace('?', '').replace("'", '').replace('"', '')
        question_slug = question_slug.replace(' ', '-')
        question_slug = ''.join(c for c in question_slug if c.isalnum() or c == '-')

        content += f'''              <Link
                href="/{hub_path}/{category_slug}/{question_slug}"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">{question}</span>
              </Link>
'''

    # Close the page
    content += f'''            </div>
          </section>

          <section className="pt-6 border-t border-border">
            <Link
              href="/{hub_path}"
              className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
            >
              View all Altered States categories
              <ArrowLeft className="h-4 w-4 rotate-180" />
            </Link>
          </section>
        </div>
      </main>
    </div>
  );
}}
'''

    # Write file
    with open(output_file, 'w') as f:
        f.write(content)

    print(f"  ✓ Created: {output_file}")
    print(f"    Questions: {len(questions)}")


def generate_all_category_pages(topic: str, dry_run: bool = False):
    """Generate all category index pages for a topic."""
    print(f"=== Generating Category Index Pages: {topic.replace('_', ' ').title()} ===\n")

    # Load questions
    data = load_questions(topic)
    clusters = data['clusters']

    # Determine paths
    hub_paths = {
        'altered_states': 'consciousness/altered-states',
        'meditation': 'consciousness/meditation',
        'memory': 'consciousness/memory'
    }
    hub_path = hub_paths.get(topic, topic)

    # Determine output base
    output_base = Path(__file__).parent.parent.parent / 'salarsu/frontend/app'

    if dry_run:
        print("[DRY RUN MODE - No files will be created]\n")

    print(f"Hub path: /{hub_path}/")
    print(f"Total categories: {len(clusters)}\n")

    # Generate each category page
    for idx, cluster in enumerate(clusters):
        print(f"[{idx+1}/{len(clusters)}] {cluster['name']}")
        generate_category_page(cluster, hub_path, output_base, dry_run)

    # Summary
    print(f"\n{'=' * 60}")
    print(f"\n✓ Category index pages {'would be' if dry_run else 'created'} successfully!")
    print(f"\nNext steps:")
    print(f"1. Update hub page with all category cards")
    print(f"2. Verify TypeScript compilation: cd ../salarsu/frontend && npm run build")
    print(f"3. Start content filling for answer pages")


def main():
    parser = argparse.ArgumentParser(
        description="Generate category index pages from YAML question files"
    )
    parser.add_argument(
        '--topic',
        required=True,
        choices=['altered_states', 'meditation', 'memory'],
        help='Topic to generate category pages for'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview what would be generated without creating files'
    )

    args = parser.parse_args()

    try:
        generate_all_category_pages(topic=args.topic, dry_run=args.dry_run)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
