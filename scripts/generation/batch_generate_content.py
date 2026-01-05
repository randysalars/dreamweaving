#!/usr/bin/env python3
"""
Batch Answer Page Content Generator

Generates complete answer content for all pending questions using Claude API.
Falls back to placeholder templates if ANTHROPIC_API_KEY is not available.

Usage:
    # With API key (automatic content generation)
    export ANTHROPIC_API_KEY="your-key-here"
    python3 batch_generate_content.py --topic altered_states

    # Without API key (generates structured placeholders for manual filling)
    python3 batch_generate_content.py --topic altered_states --template-mode

    # Dry run to see what would be generated
    python3 batch_generate_content.py --topic altered_states --dry-run

    # Concurrent processing (default: 4 threads)
    python3 batch_generate_content.py --topic altered_states --concurrent 6
"""

import argparse
import concurrent.futures
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml
from jinja2 import Environment, FileSystemLoader

# Try to import anthropic, but continue if not available
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("Warning: anthropic package not installed. Will use template mode.")


class CostTracker:
    """Track API costs during batch generation"""

    def __init__(self):
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.page_count = 0
        self.start_time = time.time()

    def add_usage(self, input_tokens: int, output_tokens: int):
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.page_count += 1

    def get_cost_estimate(self) -> Dict[str, float]:
        """Calculate cost estimate using Claude Sonnet 4 pricing"""
        # Sonnet 4 pricing: $3/MTok input, $15/MTok output
        input_cost = (self.total_input_tokens / 1_000_000) * 3.00
        output_cost = (self.total_output_tokens / 1_000_000) * 15.00
        total_cost = input_cost + output_cost

        return {
            'input_tokens': self.total_input_tokens,
            'output_tokens': self.total_output_tokens,
            'input_cost': input_cost,
            'output_cost': output_cost,
            'total_cost': total_cost,
            'pages_generated': self.page_count
        }

    def print_summary(self):
        """Print cost summary"""
        elapsed = time.time() - self.start_time
        costs = self.get_cost_estimate()

        print("\n" + "="*60)
        print("BATCH GENERATION SUMMARY")
        print("="*60)
        print(f"Pages generated: {costs['pages_generated']}")
        print(f"Total tokens: {costs['input_tokens'] + costs['output_tokens']:,}")
        print(f"  - Input: {costs['input_tokens']:,}")
        print(f"  - Output: {costs['output_tokens']:,}")
        print(f"\nEstimated cost: ${costs['total_cost']:.2f}")
        print(f"  - Input: ${costs['input_cost']:.3f}")
        print(f"  - Output: ${costs['output_cost']:.3f}")
        print(f"\nTime elapsed: {elapsed:.1f} seconds")
        if costs['pages_generated'] > 0:
            print(f"Average: {elapsed/costs['pages_generated']:.1f} sec/page")
        print("="*60 + "\n")


class BatchContentGenerator:
    """Batch generate answer page content using Claude API or templates"""

    def __init__(self, templates_dir: str, output_base: str, api_key: Optional[str] = None):
        self.env = Environment(loader=FileSystemLoader(templates_dir))
        self.output_base = Path(output_base)
        self.cost_tracker = CostTracker()

        # Initialize Claude client if API key available
        self.client = None
        self.use_api = False

        if api_key and ANTHROPIC_AVAILABLE:
            try:
                self.client = anthropic.Anthropic(api_key=api_key)
                self.use_api = True
                print("✓ Claude API initialized - will generate real content")
            except Exception as e:
                print(f"Warning: Could not initialize Claude API: {e}")
                print("Falling back to template mode")
        else:
            print("Template mode: Will generate structured placeholders for manual filling")

    def load_pending_questions(self, yaml_path: Path) -> List[Dict]:
        """Load all pending questions from YAML"""
        with open(yaml_path) as f:
            data = yaml.safe_load(f)

        pending = []
        for cluster in data['clusters']:
            for q_data in cluster['questions']:
                # Skip completed questions
                if q_data.get('status') == 'complete':
                    continue

                pending.append({
                    'question': q_data['question'],
                    'cluster_id': cluster['id'],
                    'cluster_name': cluster['name'],
                    'category_slug': cluster['category_slug'],
                    'cluster': cluster  # Store full cluster for related questions
                })

        return pending

    def generate_answer_content_api(self, question: str, cluster_name: str, topic: str) -> Tuple[Dict[str, any], Dict]:
        """
        Use Claude API to generate answer content

        Returns: (content_dict, usage_dict)
        """

        prompt = f"""You are writing a concise, authoritative answer page about consciousness topics for salars.net.

Topic: {topic}
Category: {cluster_name}
Question: {question}

Generate content following this exact structure:

1. SHORT ANSWER (20-35 words):
Write a direct, declarative answer. No fluff. No "you should" language. Just explain what it is or how it works.

2. WHY THIS MATTERS (2-4 sentences):
Explain WHY this happens, WHAT mechanisms are involved, or HOW it relates to the broader field. Use causal language: "because," "results in," "leads to," "demonstrates." Be specific and concrete.

3. WHERE THIS CHANGES (1-3 sentences):
When does this change? What are the limits? What exceptions exist? Address boundaries and spectrum thinking without contradicting the short answer.

4. RELATED KEYWORDS (5-8 terms):
List related concepts, terms, or questions someone might also search for.

FORBIDDEN LANGUAGE:
Never use: "always," "never," "guaranteed," "proven," "the best," "revolutionary," "game-changing"

Rules:
- Use neutral, explanatory tone (not instructional)
- Avoid absolutes and hype
- Be concrete and specific
- Trust the reader's intelligence
- No product promotion or CTAs

Output as JSON:
{{
  "short_answer": "...",
  "why_this_matters": "...",
  "where_this_changes": "...",
  "keywords": ["term1", "term2", ...]
}}"""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )

            # Track usage
            usage = {
                'input_tokens': message.usage.input_tokens,
                'output_tokens': message.usage.output_tokens
            }

            # Extract JSON from response
            response_text = message.content[0].text

            # Try to find JSON in the response
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                content = {
                    'short_answer': result.get('short_answer', ''),
                    'why_this_matters': result.get('why_this_matters', ''),
                    'where_this_changes': result.get('where_this_changes', ''),
                    'keywords': result.get('keywords', [])
                }
                return content, usage
            else:
                print(f"  Warning: Could not parse JSON from Claude response")
                return self._template_content(question), usage

        except Exception as e:
            print(f"  Error generating content: {e}")
            return self._template_content(question), {'input_tokens': 0, 'output_tokens': 0}

    def _template_content(self, question: str) -> Dict[str, any]:
        """Generate template/placeholder content for manual filling"""
        return {
            'short_answer': f'[Claude: Write 20-35 word answer to "{question}"]',
            'why_this_matters': f'[Claude: Write 2-4 sentences explaining WHY this matters, using causal language (because, results in, leads to). Be specific about mechanisms and broader implications.]',
            'where_this_changes': f'[Claude: Write 1-3 sentences addressing when this CHANGES, what the limits are, or what exceptions exist. Add nuance without contradicting the short answer.]',
            'keywords': ["consciousness", "awareness", "perception"]
        }

    def _is_placeholder_content(self, file_path: Path) -> bool:
        """Check if a page file contains placeholder markers"""
        if not file_path.exists():
            return False  # Doesn't exist, not a placeholder

        try:
            content = file_path.read_text()
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

            return False  # No placeholder markers found = complete content

        except Exception:
            return False  # Error reading, assume not placeholder

    def build_related_questions(self, all_clusters: List[Dict], current_question: str,
                                current_cluster_id: str, hub_path: str) -> List[Dict]:
        """
        Build related questions list with same-cluster priority.
        Returns up to 5 related questions:
        - Up to 3 from same cluster
        - Fill remainder from other clusters
        """
        related = []
        same_cluster = []
        other_cluster = []

        for cluster in all_clusters:
            for q_data in cluster['questions']:
                q_text = q_data['question']
                if q_text == current_question:
                    continue

                slug = self._to_slug(q_text)
                q_info = {
                    'text': q_text,
                    'url': f"/{hub_path}/{cluster['category_slug']}/{slug}",
                    'cluster': cluster['id']
                }

                if cluster['id'] == current_cluster_id:
                    same_cluster.append(q_info)
                else:
                    other_cluster.append(q_info)

        # Add up to 3 from same cluster
        related.extend(same_cluster[:3])

        # Fill remainder with other clusters
        remaining = 5 - len(related)
        if remaining > 0:
            related.extend(other_cluster[:remaining])

        return related

    def generate_single_page(self, q_data: Dict, all_clusters: List[Dict],
                            hub_path: str, topic: str, skip_complete: bool = True) -> Dict:
        """
        Generate a single answer page

        Args:
            skip_complete: If True, skip files that already have complete content (default: True)

        Returns: result dict with status, question, path, usage
        """
        question = q_data['question']
        cluster_name = q_data['cluster_name']
        category_slug = q_data['category_slug']
        question_slug = self._to_slug(question)

        # Check if file exists and has complete content
        output_path = self.output_base / hub_path / category_slug / question_slug / 'page.tsx'

        if skip_complete and output_path.exists():
            if not self._is_placeholder_content(output_path):
                # File exists with complete content - skip it
                return {
                    'status': 'skipped',
                    'question': question,
                    'path': str(output_path),
                    'usage': {'input_tokens': 0, 'output_tokens': 0},
                    'reason': 'Already has complete content'
                }

        try:
            # Generate content (API or template)
            if self.use_api:
                content, usage = self.generate_answer_content_api(question, cluster_name, topic)
                self.cost_tracker.add_usage(usage['input_tokens'], usage['output_tokens'])
            else:
                content = self._template_content(question)
                usage = {'input_tokens': 0, 'output_tokens': 0}

            # Build related questions
            related_questions = self.build_related_questions(
                all_clusters, question, q_data['cluster_id'], hub_path
            )

            # Prepare template context
            context = {
                'title': f"{question} | Salars Consciousness",
                'description': content['short_answer'][:155] if not content['short_answer'].startswith('[Claude:') else question,
                'question': question,
                'short_answer': content['short_answer'],
                'why_this_matters': content['why_this_matters'],
                'where_this_changes': content['where_this_changes'],
                'related_questions': related_questions[:5],
                'canonical_path': f"/{hub_path}/{category_slug}/{question_slug}",
                'component_name': self._to_component_name(question_slug),
                'back_url': f"/{hub_path}/{category_slug}",
                'category_name': cluster_name,
                'category_url': f"/{hub_path}/{category_slug}",
                'keywords_json': json.dumps(content['keywords']),
            }

            # Load and render template
            template = self.env.get_template('answer_page_aeo.tsx.j2')
            output = template.render(**context)

            # Write to file
            output_path = self.output_base / hub_path / category_slug / question_slug / 'page.tsx'
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(output, encoding='utf-8')

            return {
                'status': 'success',
                'question': question,
                'path': str(output_path),
                'usage': usage,
                'mode': 'api' if self.use_api else 'template'
            }

        except Exception as e:
            return {
                'status': 'error',
                'question': question,
                'error': str(e),
                'usage': {'input_tokens': 0, 'output_tokens': 0}
            }

    def _to_slug(self, text: str) -> str:
        """Convert text to URL-friendly slug"""
        slug = re.sub(r'[^\w\s-]', '', text.lower())
        slug = re.sub(r'[\s_]+', '-', slug)
        return slug.strip('-')

    def _to_component_name(self, slug: str) -> str:
        """Convert slug to PascalCase component name"""
        words = slug.split('-')
        return ''.join(word.capitalize() for word in words if word) + 'Page'


def main():
    parser = argparse.ArgumentParser(
        description='Batch generate answer page content',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate with API (auto-detects ANTHROPIC_API_KEY env var)
  python3 batch_generate_content.py --topic altered_states

  # Generate templates without API
  python3 batch_generate_content.py --topic altered_states --template-mode

  # Dry run to preview
  python3 batch_generate_content.py --topic altered_states --dry-run

  # Process with 6 concurrent threads
  python3 batch_generate_content.py --topic altered_states --concurrent 6

  # Skip first 20 questions (resume from #21)
  python3 batch_generate_content.py --topic altered_states --skip 20
        """
    )

    parser.add_argument('--topic', default='altered_states',
                       choices=['altered_states', 'meditation', 'memory', 'integration', 'sleep_dreams'],
                       help='Topic to generate pages for')
    parser.add_argument('--concurrent', type=int, default=4,
                       help='Number of concurrent API calls (default: 4)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview what would be generated without creating files')
    parser.add_argument('--template-mode', action='store_true',
                       help='Force template mode even if API key is available')
    parser.add_argument('--skip', type=int, default=0,
                       help='Skip first N questions (useful for resuming)')
    parser.add_argument('--limit', type=int,
                       help='Limit to N questions (useful for testing)')

    args = parser.parse_args()

    # Setup paths
    script_dir = Path(__file__).parent
    yaml_path = script_dir / f"{args.topic}_questions.yaml"
    templates_dir = script_dir / 'templates'
    output_base = Path('/home/rsalars/Projects/dreamweaving/salarsu/frontend/app')

    if not yaml_path.exists():
        print(f"Error: Questions file not found: {yaml_path}")
        sys.exit(1)

    # Determine API key
    api_key = None if args.template_mode else os.getenv('ANTHROPIC_API_KEY')

    # Initialize generator
    generator = BatchContentGenerator(
        templates_dir=str(templates_dir),
        output_base=str(output_base),
        api_key=api_key
    )

    # Load questions
    pending = generator.load_pending_questions(yaml_path)

    # Load all clusters for related questions
    with open(yaml_path) as f:
        all_clusters = yaml.safe_load(f)['clusters']

    print(f"\nFound {len(pending)} pending questions")

    # Apply skip/limit
    if args.skip > 0:
        pending = pending[args.skip:]
        print(f"Skipping first {args.skip} questions")

    if args.limit:
        pending = pending[:args.limit]
        print(f"Limiting to {args.limit} questions")

    if args.dry_run:
        print("\nDRY RUN - Would generate these pages:\n")
        for i, q in enumerate(pending[:10], 1):
            print(f"  {i}. {q['question']}")
            print(f"     Category: {q['cluster_name']}")
        if len(pending) > 10:
            print(f"  ... and {len(pending) - 10} more")
        return

    # Hub path for URL construction
    hub_path = f"consciousness/{args.topic.replace('_', '-')}"

    # Batch generate
    print(f"\nGenerating {len(pending)} pages...\n")
    results = []

    if args.concurrent > 1 and generator.use_api:
        # Concurrent processing with API
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrent) as executor:
            futures = {
                executor.submit(
                    generator.generate_single_page,
                    q_data, all_clusters, hub_path, args.topic
                ): q_data
                for q_data in pending
            }

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                results.append(result)

                status_icon = "✓" if result['status'] == 'success' else ("⊙" if result['status'] == 'skipped' else "✗")
                mode = result.get('mode', result.get('reason', 'unknown'))
                print(f"{status_icon} [{mode[:30]:30}] {result['question']}")

                if result['status'] == 'error':
                    print(f"           Error: {result['error']}")

    else:
        # Sequential processing (template mode or concurrent=1)
        for q_data in pending:
            result = generator.generate_single_page(q_data, all_clusters, hub_path, args.topic)
            results.append(result)

            status_icon = "✓" if result['status'] == 'success' else ("⊙" if result['status'] == 'skipped' else "✗")
            mode = result.get('mode', result.get('reason', 'unknown'))
            print(f"{status_icon} [{mode[:30]:30}] {result['question']}")

            if result['status'] == 'error':
                print(f"           Error: {result['error']}")

    # Summary
    success = sum(1 for r in results if r['status'] == 'success')
    skipped = sum(1 for r in results if r['status'] == 'skipped')
    errors = sum(1 for r in results if r['status'] == 'error')

    print(f"\n{'='*60}")
    print(f"RESULTS: {success}/{len(pending)} pages generated successfully")
    if skipped > 0:
        print(f"Skipped: {skipped} (already complete)")
    if errors > 0:
        print(f"Errors: {errors}")

    # Cost summary if using API
    if generator.use_api:
        generator.cost_tracker.print_summary()

    # Save results log
    log_path = script_dir / f"batch_log_{args.topic}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(log_path, 'w') as f:
        json.dump({
            'topic': args.topic,
            'timestamp': datetime.now().isoformat(),
            'mode': 'api' if generator.use_api else 'template',
            'total_questions': len(pending),
            'success': success,
            'skipped': skipped,
            'errors': errors,
            'cost_estimate': generator.cost_tracker.get_cost_estimate() if generator.use_api else None,
            'results': results
        }, f, indent=2)

    print(f"\nLog saved to: {log_path}")


if __name__ == '__main__':
    main()
