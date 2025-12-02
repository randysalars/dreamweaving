#!/usr/bin/env python3
"""
Convert visualizations.txt affirmations to SSML format for voice synthesis.

This script reads the affirmations text and creates a properly formatted
SSML file with hypnotic pacing using breaks between affirmations.
"""

import re
from pathlib import Path

def convert_to_ssml(input_file: Path, output_file: Path):
    """Convert plain text affirmations to SSML format."""

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Start SSML document
    ssml_parts = ['<speak>']

    # Add opening prosody for hypnotic delivery
    ssml_parts.append('<prosody rate="0.95" pitch="-1st">')

    # Split content into lines
    lines = content.split('\n')

    current_section = None

    for line in lines:
        line = line.strip()

        # Skip empty lines
        if not line:
            continue

        # Check if this is a section header (single word or short phrase without punctuation at end)
        # Section headers are standalone words like "Gratitude", "Goals", etc.
        if re.match(r'^[A-Z][a-zA-Z\s]{0,20}$', line) and not line.endswith('.'):
            if current_section:
                # Add longer pause between sections
                ssml_parts.append('<break time="3s"/>')

            current_section = line
            # Add section as emphasized header
            ssml_parts.append(f'\n<!-- SECTION: {line} -->')
            ssml_parts.append(f'<emphasis level="moderate">{line}</emphasis>')
            ssml_parts.append('<break time="2s"/>')
            continue

        # Skip lines that are just bullet points or dashes
        if line.startswith('- "'):
            line = line[3:]  # Remove "- " prefix
            if line.endswith('"'):
                line = line[:-1]  # Remove trailing quote
        elif line.startswith('-'):
            line = line[1:].strip()

        # Clean up the line - remove leading/trailing quotes
        line = line.strip('"')

        # Skip very short lines that are probably formatting artifacts
        if len(line) < 10:
            continue

        # Escape special XML characters
        line = line.replace('&', '&amp;')
        line = line.replace('<', '&lt;')
        line = line.replace('>', '&gt;')

        # Add the affirmation text with appropriate pause after
        ssml_parts.append(line)
        ssml_parts.append('<break time="1200ms"/>')

    # Close prosody and speak tags
    ssml_parts.append('</prosody>')
    ssml_parts.append('</speak>')

    # Join and write output
    ssml_content = '\n'.join(ssml_parts)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(ssml_content)

    print(f"Created SSML file: {output_file}")
    print(f"Total size: {len(ssml_content):,} bytes")

    return output_file

if __name__ == '__main__':
    script_dir = Path(__file__).parent
    input_file = script_dir / 'visualizations.txt'
    output_file = script_dir / 'working_files' / 'affirmations.ssml'

    # Create working_files directory if needed
    output_file.parent.mkdir(parents=True, exist_ok=True)

    convert_to_ssml(input_file, output_file)
