#!/usr/bin/env python3
"""
Generate Category Index Pages

Creates category overview pages that list all questions in each category
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from generators.simple_generator import SimplePageGenerator


# Category data
CATEGORIES = [
    {
        'name': 'Core Definitions & Foundations',
        'slug': 'definitions-foundations',
        'description': 'Fundamental concepts and definitions about altered states of consciousness.',
        'questions': [
            'What is an altered state of consciousness?',
            'What defines normal waking consciousness?',
            'How do altered states differ from everyday awareness?',
            'Are altered states always intentional?',
            'Can altered states occur spontaneously?'
        ]
    },
    {
        'name': 'Natural vs Induced Altered States',
        'slug': 'natural-vs-induced',
        'description': 'Understanding naturally occurring versus deliberately induced altered states.',
        'questions': [
            'What are natural altered states of consciousness?',
            'What causes natural altered states to occur?'
        ]
    },
    {
        'name': 'Entry Pathways & Triggers',
        'slug': 'entry-pathways',
        'description': 'How altered states begin and the various triggers that induce them.',
        'questions': [
            'How do altered states begin?',
            'Can breathing techniques induce altered states?'
        ]
    },
    {
        'name': 'Safety, Risks & Stability',
        'slug': 'safety-and-risks',
        'description': 'Understanding the safety considerations and potential risks of altered states.',
        'questions': [
            'Are altered states dangerous?'
        ]
    }
]


def generate_category_page(category, generator, output_base):
    """Generate a category index page"""
    
    # Build question links
    question_links = []
    for question in category['questions']:
        slug = generator._to_slug(question)
        question_links.append({
            'text': question,
            'url': f"/consciousness/altered-states/{category['slug']}/{slug}"
        })
    
    # Create category page content
    category_page_path = Path(output_base) / 'consciousness' / 'altered-states' / category['slug'] / 'page.tsx'
    category_page_path.parent.mkdir(parents=True, exist_ok=True)
    
    content = f'''import type {{ Metadata }} from "next";
import Link from "next/link";
import {{ ArrowLeft, HelpCircle }} from "lucide-react";
import {{ getSiteUrl }} from "@/lib/siteUrl";

const pageUrl = `${{getSiteUrl()}}/consciousness/altered-states/{category['slug']}`;

export const metadata: Metadata = {{
  title: "{category['name']} | Altered States",
  description: "{category['description']}",
  alternates: {{ canonical: pageUrl }},
  openGraph: {{
    title: "{category['name']}",
    description: "{category['description']}",
    url: pageUrl,
    type: "website",
  }},
}};

export default function {generator._to_component_name(category['slug'])}() {{
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-4xl space-y-8">

          {{/* Breadcrumb */}}
          <div className="space-y-2">
            <Link
              href="/consciousness/altered-states"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Altered States
            </Link>
          </div>

          {{/* Category Title */}}
          <div className="space-y-3">
            <h1 className="text-4xl font-semibold tracking-tight text-foreground">
              {category['name']}
            </h1>
            <p className="text-lg text-muted-foreground">
              {category['description']}
            </p>
          </div>

          {{/* Question List */}}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Questions in this category
            </h2>
            <div className="grid gap-3">
'''
    
    # Add question links
    for link in question_links:
        content += f'''              
              <Link
                href="{link['url']}"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">{link['text']}</span>
              </Link>
'''
    
    content += '''            </div>
          </section>

          {{/* Back to Hub */}}
          <section className="pt-6 border-t border-border">
            <Link
              href="/consciousness/altered-states"
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
}
'''
    
    category_page_path.write_text(content, encoding='utf-8')
    return category_page_path


def main():
    print("=== Generating Category Index Pages ===\n")
    
    generator = SimplePageGenerator(
        templates_dir='scripts/generation/templates',
        output_base='../salarsu/frontend/app'
    )
    
    output_base = Path('../salarsu/frontend/app')
    generated_paths = []
    
    for category in CATEGORIES:
        print(f"Generating: {category['name']}")
        try:
            path = generate_category_page(category, generator, output_base)
            generated_paths.append(path)
            print(f"  ✓ Created: {path.relative_to(output_base)}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print(f"\n=== Summary ===")
    print(f"Successfully generated: {len(generated_paths)}/{len(CATEGORIES)} category pages")
    
    print(f"\nGenerated pages:")
    for path in generated_paths:
        rel_path = path.relative_to(output_base)
        print(f"  - {rel_path}")


if __name__ == '__main__':
    main()
