#!/usr/bin/env python3
"""
PageGenerator - Generate TypeScript answer pages from questions

Uses Claude API to generate answer content, then renders Jinja2 templates
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from jinja2 import Environment, FileSystemLoader
import anthropic
import os


class PageGenerator:
    """Generate TypeScript page files from questions"""

    def __init__(self, templates_dir: str, output_base: str):
        self.env = Environment(loader=FileSystemLoader(templates_dir))
        self.output_base = Path(output_base)

        # Initialize Claude client
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        self.client = anthropic.Anthropic(api_key=api_key)

    def generate_answer_content(self, question: str, cluster_name: str, topic: str) -> Dict[str, any]:
        """
        Use Claude to generate answer content for a question

        Returns dict with:
        - short_answer: 20-35 word direct answer
        - context_paragraph: 2-4 sentences explaining why
        - boundary_paragraph: 1-3 sentences on limits/changes
        - related_keywords: List of related terms
        """

        prompt = f"""You are writing a concise, authoritative answer page about consciousness topics for salars.net.

Topic: {topic}
Category: {cluster_name}
Question: {question}

Generate content following this exact structure:

1. SHORT ANSWER (20-35 words):
Write a direct, declarative answer. No fluff. No "you should" language. Just explain what it is or how it works.

2. CONTEXT (2-4 sentences):
Explain WHY this happens, WHAT mechanisms are involved, or HOW it relates to the broader field. Be specific and concrete.

3. BOUNDARY (1-3 sentences):
When does this change? What are the limits? What exceptions exist? Add nuance without contradicting the short answer.

4. RELATED KEYWORDS (5-8 terms):
List related concepts, terms, or questions someone might also search for.

Rules:
- Use neutral, explanatory tone (not instructional)
- Avoid absolutes and hype
- Be concrete and specific
- Trust the reader's intelligence
- No product promotion or CTAs

Output as JSON:
{{
  "short_answer": "...",
  "context": "...",
  "boundary": "...",
  "keywords": ["term1", "term2", ...]
}}"""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )

            # Extract JSON from response
            response_text = message.content[0].text

            # Try to find JSON in the response
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return {
                    'short_answer': result.get('short_answer', ''),
                    'context_paragraph': result.get('context', ''),
                    'boundary_paragraph': result.get('boundary', ''),
                    'keywords': result.get('keywords', [])
                }
            else:
                print(f"Warning: Could not parse JSON from Claude response for: {question}")
                return self._fallback_content(question)

        except Exception as e:
            print(f"Error generating content for '{question}': {e}")
            return self._fallback_content(question)

    def _fallback_content(self, question: str) -> Dict[str, any]:
        """Fallback content if API fails"""
        return {
            'short_answer': f"This question explores {question.lower().replace('?', '')}.",
            'context_paragraph': "This is a complex topic that requires careful examination. Multiple factors influence this phenomenon, and understanding it requires considering various perspectives and contexts.",
            'boundary_paragraph': "The specific details vary depending on individual circumstances and environmental factors.",
            'keywords': ["consciousness", "awareness", "perception", "experience"]
        }

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
        Generate a single answer page

        Args:
            question: The question text (e.g., "What is an altered state?")
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

        # Generate answer content using Claude
        print(f"Generating content for: {question}")
        content = self.generate_answer_content(question, cluster_name, topic)

        # Prepare template context
        context = {
            'title': f"{question} | Salars Consciousness",
            'description': content['short_answer'][:155],  # Truncate to 155 chars for meta
            'question': question,
            'short_answer': content['short_answer'],
            'context_paragraph': content['context_paragraph'],
            'boundary_paragraph': content['boundary_paragraph'],
            'related_questions': related_questions[:5],  # Max 5 related
            'canonical_path': f"/{hub_path}/{category_slug}/{question_slug}",
            'component_name': self._to_component_name(question_slug),
            'back_url': f"/{hub_path}/{category_slug}",
            'category_name': cluster_name,
            'category_url': f"/{hub_path}/{category_slug}",
            'keywords_json': json.dumps(content['keywords']),
        }

        # Load and render template
        template = self.env.get_template('answer_page.tsx.j2')
        output = template.render(**context)

        # Write to file
        output_path = self.output_base / hub_path / category_slug / question_slug / 'page.tsx'
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output, encoding='utf-8')

        print(f"✓ Created: {output_path}")
        return output_path

    def _to_slug(self, text: str) -> str:
        """Convert text to URL-friendly slug"""
        # Remove punctuation
        slug = re.sub(r'[^\w\s-]', '', text.lower())
        # Replace whitespace with hyphens
        slug = re.sub(r'[\s_]+', '-', slug)
        # Remove leading/trailing hyphens
        slug = slug.strip('-')
        return slug

    def _to_component_name(self, slug: str) -> str:
        """Convert slug to PascalCase component name"""
        words = slug.split('-')
        return ''.join(word.capitalize() for word in words if word) + 'Page'


if __name__ == '__main__':
    # Test the generator
    generator = PageGenerator(
        templates_dir='scripts/generation/templates',
        output_base='../salarsu/frontend/app'
    )

    # Test with a sample question
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
            },
            {
                'text': 'Can altered states occur spontaneously?',
                'url': '/consciousness/altered-states/definitions-foundations/can-altered-states-occur-spontaneously'
            }
        ]
    )

    print(f"\nGenerated test page at: {output_path}")
