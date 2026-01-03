#!/usr/bin/env python3
"""
Marketing3Parser - Extract question maps from Notion Marketing_3.md export

Extracts three topic maps:
1. Altered States of Consciousness (10-12 clusters, ~124 questions)
2. Meditation States (12 clusters, ~120-180 questions)
3. Memory Systems (12 clusters, ~50-60 questions)
"""

import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class Marketing3Parser:
    """Extract question maps from Marketing_3.md"""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"Marketing_3.md not found at: {file_path}")
        self.content = self._load_file()

    def _load_file(self) -> str:
        """Load file content"""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def extract_all_topic_maps(self) -> Dict[str, Dict[str, List[str]]]:
        """Extract all three topic maps"""
        return {
            'altered_states': self.extract_topic_map('altered_states'),
            'meditation': self.extract_topic_map('meditation'),
            'memory': self.extract_topic_map('memory')
        }

    def extract_topic_map(self, topic_name: str) -> Dict[str, List[str]]:
        """
        Extract complete question map for a topic

        Args:
            topic_name: "altered_states" | "meditation" | "memory"

        Returns:
            Dict mapping cluster names to lists of questions
        """
        # Find section header patterns
        patterns = {
            'altered_states': r"##\s+The Complete Map of Altered States of Consciousness\s*\n\s*---",
            'meditation': r"##\s+🧠\s+The Question Cloud:\s+Meditation States?",
            'memory': r"##\s+🧠\s+The Question Cloud:\s+Memory"
        }

        pattern = patterns.get(topic_name)
        if not pattern:
            raise ValueError(f"Unknown topic: {topic_name}")

        # Extract section content
        section_match = re.search(pattern, self.content, re.IGNORECASE)
        if not section_match:
            raise ValueError(f"Topic map not found: {topic_name}")

        start_pos = section_match.end()

        # Find next major section (as endpoint)
        # Look for next ## header that's not a sub-cluster
        next_section = re.search(r"\n##\s+[^#🔹]", self.content[start_pos:])
        end_pos = start_pos + next_section.start() if next_section else len(self.content)

        section_content = self.content[start_pos:end_pos]

        return self._parse_clusters(section_content, topic_name)

    def _parse_clusters(self, content: str, topic_name: str) -> Dict[str, List[str]]:
        """Parse cluster sections into question lists"""
        clusters = {}

        # Different patterns for different sections
        # Altered States uses Roman numerals: ## I. Name or ### I. Name
        # Meditation/Memory use numbers: ## 🔹 1. Name or ### 1. Name
        cluster_patterns = [
            r"###?\s+(?:🔹\s+)?([IVX]+)\.\s+([^\n(]+?)(?:\s+\((\d+)\))?\s*$",  # Roman numerals
            r"###?\s+(?:🔹\s+)?(\d+)\.\s+([^\n(]+?)(?:\s+\((\d+)\))?\s*$",  # Numbers
            r"###?\s+(?:🔹\s+)?(\d+)️⃣\s+([^\n(]+?)(?:\s+\((\d+)\))?\s*$",  # Emoji numbers
        ]

        all_matches = []
        for pattern in cluster_patterns:
            matches = list(re.finditer(pattern, content, re.MULTILINE))
            all_matches.extend(matches)

        # Sort by position in text
        all_matches.sort(key=lambda m: m.start())

        if not all_matches:
            print(f"Warning: No clusters found for {topic_name}")
            return {}

        for i, match in enumerate(all_matches):
            cluster_id = match.group(1)
            cluster_name = match.group(2).strip()

            # Clean up cluster name
            cluster_name = re.sub(r'\s+', ' ', cluster_name)
            cluster_name = cluster_name.strip(' —–-')

            # Extract content between this cluster and next
            start = match.end()
            end = all_matches[i+1].start() if i+1 < len(all_matches) else len(content)

            cluster_content = content[start:end]

            # Extract questions
            questions = self._extract_questions(cluster_content)

            if questions:
                clusters[cluster_name] = questions
                print(f"  {cluster_id}. {cluster_name}: {len(questions)} questions")

        return clusters

    def _extract_questions(self, cluster_content: str) -> List[str]:
        """Extract questions from cluster content"""
        questions = []

        # Questions can be:
        # - Numbered lists (1. Question)
        # - Bullet points (- Question)
        # - Just lines ending with ?

        # First, try structured lists
        question_patterns = [
            r"^\s*\d+\.\s+(.+?)(?:\?)?$",  # 1. Question
            r"^\s*[-•]\s+(.+?)(?:\?)?$",    # - Question or • Question
        ]

        for line in cluster_content.split('\n'):
            line = line.strip()

            # Skip empty lines, headers, purpose statements
            if not line or line.startswith('#') or line.startswith('**Purpose'):
                continue
            if line.startswith('Purpose:') or line.startswith('User state:'):
                continue

            # Try patterns
            matched = False
            for pattern in question_patterns:
                match = re.match(pattern, line)
                if match:
                    question_text = match.group(1).strip()
                    # Clean up and add question mark if missing
                    question_text = self._clean_question(question_text)
                    if question_text:
                        questions.append(question_text)
                        matched = True
                        break

            # If no pattern matched but line ends with ?, treat as question
            if not matched and line.endswith('?'):
                question_text = self._clean_question(line)
                if question_text and len(question_text) > 10:  # Reasonable length
                    questions.append(question_text)

        return questions

    def _clean_question(self, text: str) -> str:
        """Clean and normalize question text"""
        # Remove markdown formatting
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*([^*]+)\*', r'\1', text)      # Italic
        text = re.sub(r'`([^`]+)`', r'\1', text)        # Code

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        # Ensure ends with question mark
        if text and not text.endswith('?'):
            text += '?'

        return text

    def get_statistics(self) -> Dict[str, any]:
        """Get statistics about all topic maps"""
        stats = {}

        for topic in ['altered_states', 'meditation', 'memory']:
            try:
                topic_map = self.extract_topic_map(topic)
                total_questions = sum(len(qs) for qs in topic_map.values())
                stats[topic] = {
                    'clusters': len(topic_map),
                    'total_questions': total_questions,
                    'cluster_names': list(topic_map.keys())
                }
            except Exception as e:
                stats[topic] = {'error': str(e)}

        return stats


if __name__ == '__main__':
    # Test the parser
    parser = Marketing3Parser('knowledge/notion_export/pages/Marketing_3.md')

    print("=== Marketing3Parser Test ===\n")

    # Test each topic
    for topic in ['altered_states', 'meditation', 'memory']:
        print(f"\n{topic.upper().replace('_', ' ')}:")
        try:
            topic_map = parser.extract_topic_map(topic)
            total = sum(len(qs) for qs in topic_map.values())
            print(f"Found {len(topic_map)} clusters, {total} total questions\n")

            # Show first few questions from first cluster
            if topic_map:
                first_cluster = list(topic_map.keys())[0]
                questions = topic_map[first_cluster]
                print(f"Sample from '{first_cluster}':")
                for q in questions[:3]:
                    print(f"  - {q}")
                if len(questions) > 3:
                    print(f"  ... and {len(questions) - 3} more")
        except Exception as e:
            print(f"Error: {e}")

    # Show statistics
    print("\n\n=== STATISTICS ===")
    stats = parser.get_statistics()
    for topic, data in stats.items():
        print(f"\n{topic}:")
        if 'error' in data:
            print(f"  Error: {data['error']}")
        else:
            print(f"  Clusters: {data['clusters']}")
            print(f"  Total Questions: {data['total_questions']}")
