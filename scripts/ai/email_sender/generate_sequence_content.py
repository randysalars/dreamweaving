#!/usr/bin/env python3
"""
Dreamweaver Email Sequence Content Generator
Automates the generation of full email content for all nurture sequences.

Features:
- Sequential processing (one email at a time)
- Rate-limiting (configurable delay)
- Modular generation classes
- "Dreamweaver" voice alignment
- Organized folder structure
- Dry-run mode for verification
"""

import os
import sys
import json
import yaml
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Voice Guidelines based on ArticleGenerator
VOICE_GUIDELINES = """
DREAMWEAVER VOICE CHARACTERISTICS:

Tone:
- Gentle but not soft
- Honest but not harsh
- Spacious - leave room for the reader
- Permission-giving, never prescriptive
- Professional but deeply personal (Randy's voice)

Recognition Signals:
- "You're not strange for feeling this."
- "Many people carry this quietly."
- "This doesn't mean something is wrong."
- "You don't have to fix this immediately."

Philosophy: "Slow Business"
- Value intent, connection, and the human "why" over speed and automation.
- The content must help the reader whether or not they ever buy anything.
- No high-pressure sales, no hype, no urgency language.
"""

@dataclass
class EmailIdea:
    sequence_slug: str
    topic: str
    index: int
    subject_idea: str
    theme: str
    tone: str

class EmailContentGenerator:
    def __init__(self, project_root: Path, api_key: str, delay: float = 2.0):
        self.project_root = project_root
        self.output_dir = project_root / "config" / "sequences" / "content"
        self.delay = delay
        self.api_key = api_key
        
        # Initialize Grok/OpenAI client
        if OPENAI_AVAILABLE:
            self.client = openai.OpenAI(
                api_key=api_key,
                base_url="https://api.x.ai/v1",
            )
        else:
            self.client = None

    def log(self, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")

    def load_sequences(self) -> List[EmailIdea]:
        sequences_dir = self.project_root / "config" / "sequences"
        ideas = []
        
        for yaml_file in sorted(sequences_dir.glob("*.yaml")):
            slug = yaml_file.stem
            with open(yaml_file, "r") as f:
                data = yaml.safe_load(f)
                topic = data.get("topic", slug.replace("_", " ").title())
                emails = data.get("emails", [])
                
                for email_data in emails:
                    ideas.append(EmailIdea(
                        sequence_slug=slug,
                        topic=topic,
                        index=email_data["index"],
                        subject_idea=email_data["subject"],
                        theme=email_data["theme"],
                        tone=email_data["tone"]
                    ))
        return ideas

    def generate_email(self, idea: EmailIdea, dry_run: bool = False) -> Optional[str]:
        target_path = self.output_dir / idea.sequence_slug / f"{idea.index:03d}.txt"
        
        if target_path.exists():
            self.log(f"Skipping {idea.sequence_slug}_{idea.index:03d} (Already exists)")
            return None

        if dry_run:
            self.log(f"[DRY RUN] Would generate: {idea.sequence_slug} - Email {idea.index}: {idea.subject_idea}")
            return "dry_run_content"

        self.log(f"Generating: {idea.sequence_slug} - Email {idea.index}: {idea.subject_idea}")
        
        prompt = self._build_prompt(idea)
        
        try:
            response = self.client.chat.completions.create(
                model="grok-3", # Use current stable model
                messages=[
                    {"role": "system", "content": "You are Randy, the creator of Dreamweaving. You write gentle, profound, and trust-building emails using the 'Slow Business' philosophy."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            self._save_content(idea, content)
            return content
            
        except Exception as e:
            self.log(f"Error generating {idea.sequence_slug}_{idea.index}: {e}")
            return None

    def _build_prompt(self, idea: EmailIdea) -> str:
        return f"""
Draft a full email for the '{idea.topic}' sequence. 

{VOICE_GUIDELINES}

EMAIL SPECIFICATIONS:
- Sequence: {idea.topic}
- Email Number: {idea.index} / 10
- Subject Idea: {idea.subject_idea}
- Theme: {idea.theme}
- Specified Tone: {idea.tone}

REQUIREMENTS:
1. Include a clear Subject Line (can refine the idea).
2. Use a personal greeting (e.g., "Hello,").
3. The body should be 3-5 paragraphs, focusing on the theme with profound insight.
4. Use Randy's voice: quiet, observant, and permission-giving.
5. End with a gentle closing (e.g., "Be well, Randy" or "With peace, Randy").
6. Output raw text content only (no markdown formatting like 'Subject: ...' is fine, but don't add conversational filler around the draft).

Draft the email now:
"""

    def _save_content(self, idea: EmailIdea, content: str):
        topic_dir = self.output_dir / idea.sequence_slug
        topic_dir.mkdir(parents=True, exist_ok=True)
        
        target_path = topic_dir / f"{idea.index:03d}.txt"
        with open(target_path, "w") as f:
            f.write(content.strip())
        
        self.log(f"Saved to {target_path}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate Dreamweaving Sequence Content")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be generated")
    parser.add_argument("--delay", type=float, default=2.0, help="Delay between emails in seconds")
    parser.add_argument("--limit", type=int, help="Limit number of emails to generate")
    parser.add_argument("--topic", type=str, help="Only process a specific topic slug")
    
    args = parser.parse_args()
    
    api_key = os.getenv("GROK_API_KEY")
    if not api_key:
        print("Error: GROK_API_KEY environment variable not set.")
        sys.exit(1)
        
    project_root = Path(__file__).parent.parent.parent.parent
    generator = EmailContentGenerator(project_root, api_key, delay=args.delay)
    
    all_ideas = generator.load_sequences()
    
    if args.topic:
        all_ideas = [i for i in all_ideas if i.sequence_slug == args.topic]
    
    processed_count = 0
    for idea in all_ideas:
        if args.limit and processed_count >= args.limit:
            break
            
        result = generator.generate_email(idea, dry_run=args.dry_run)
        
        if result:
            processed_count += 1
            if not args.dry_run:
                time.sleep(args.delay)
                
    generator.log(f"Done. Processed {processed_count} emails.")

if __name__ == "__main__":
    main()
