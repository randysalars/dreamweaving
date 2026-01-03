#!/usr/bin/env python3
"""
Simple Page Generator - Creates page templates without API calls

Generates TypeScript pages with structured prompts for Claude to fill in later
"""

import json
import re
from pathlib import Path
from typing import Dict, List
from jinja2 import Environment, FileSystemLoader


class SimplePageGenerator:
    """Generate TypeScript page templates without API calls"""

    def __init__(self, templates_dir: str, output_base: str):
        self.env = Environment(loader=FileSystemLoader(templates_dir))
        self.output_base = Path(output_base)

    def generate_answer_page(
        self,
        question: str,
        cluster_name: str,
        category_slug: str,
        topic: str,
        hub_path: str,
        related_questions: List[Dict[str, str]] = None
    ) -> Path:
        """
        Generate a single answer page with template content

        Args:
            question: The question text
            cluster_name: Human-readable cluster name
            category_slug: URL-safe category slug
            topic: altered_states | meditation | memory
            hub_path: Hub path (e.g., "consciousness/altered-states")
            related_questions: List of dicts with 'text' and 'url' keys

        Returns:
            Path to generated file
        """

        if related_questions is None:
            related_questions = []

        # Generate slug from question
        question_slug = self._to_slug(question)

        # Create simple template content
        short_answer = f"[Claude: Write a 20-35 word direct answer to: {question}]"
        context = f"[Claude: Explain in 2-4 sentences why {question.lower().replace('?', '')} matters and what mechanisms are involved]"
        boundary = f"[Claude: Add 1-3 sentences about when this changes or what limits exist]"

        # Generate simple keywords from question
        keywords = self._extract_keywords(question, topic)

        # Prepare template context
        context_data = {
            'title': f"{question} | Salars Consciousness",
            'description': f"Exploring {question.lower().replace('?', '')} - understanding consciousness and awareness.",
            'question': question,
            'short_answer': short_answer,
            'context_paragraph': context,
            'boundary_paragraph': boundary,
            'related_questions': related_questions[:5],
            'canonical_path': f"/{hub_path}/{category_slug}/{question_slug}",
            'component_name': self._to_component_name(question_slug),
            'back_url': f"/{hub_path}/{category_slug}",
            'category_name': cluster_name,
            'category_url': f"/{hub_path}/{category_slug}",
            'keywords_json': json.dumps(keywords),
        }

        # Load and render template
        template = self.env.get_template('answer_page.tsx.j2')
        output = template.render(**context_data)

        # Write to file
        output_path = self.output_base / hub_path / category_slug / question_slug / 'page.tsx'
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output, encoding='utf-8')

        return output_path

    def _extract_keywords(self, question: str, topic: str) -> List[str]:
        """Extract simple keywords from question"""
        keywords = [topic.replace('_', ' '), 'consciousness', 'awareness']

        # Add words from question
        words = question.lower().replace('?', '').split()
        important_words = [w for w in words if len(w) > 4 and w not in ['what', 'when', 'where', 'which', 'how']]
        keywords.extend(important_words[:3])

        return keywords

    def _to_slug(self, text: str) -> str:
        """Convert text to URL-friendly slug"""
        slug = re.sub(r'[^\w\s-]', '', text.lower())
        slug = re.sub(r'[\s_]+', '-', slug)
        slug = slug.strip('-')
        return slug

    def _to_component_name(self, slug: str) -> str:
        """Convert slug to PascalCase component name"""
        words = slug.split('-')
        return ''.join(word.capitalize() for word in words if word) + 'Page'


if __name__ == '__main__':
    # Test
    generator = SimplePageGenerator(
        templates_dir='scripts/generation/templates',
        output_base='../salarsu/frontend/app'
    )

    test_question = "What is an altered state of consciousness?"
    output_path = generator.generate_answer_page(
        question=test_question,
        cluster_name="Core Definitions & Foundations",
        category_slug="definitions-foundations",
        topic="altered_states",
        hub_path="consciousness/altered-states",
        related_questions=[
            {
                'text': 'How do altered states differ from everyday awareness?',
                'url': '/consciousness/altered-states/definitions-foundations/how-do-altered-states-differ-from-everyday-awareness'
            }
        ]
    )

    print(f"Generated: {output_path}")
