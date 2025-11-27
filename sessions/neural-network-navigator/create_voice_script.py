#!/usr/bin/env python3
"""
Create SSML Voice Script for Neural Network Navigator

This script reads the MEDITATION_SCRIPT.md file and:
1. Strips all NLP pattern tags ([PRESUP-TEMP], [EMBED-CMD], etc.)
2. Keeps SSML markup (<break>, <emphasis>)
3. Wraps in proper SSML structure
4. Adds section-specific prosody (rate/pitch adjustments)
5. Saves as working_files/voice_script.ssml
"""

import re

def strip_pattern_tags(text):
    """Remove all NLP pattern tags from the script"""
    # Pattern tags to remove: [PRESUP-TEMP], [EMBED-CMD], [VAK-V], etc.
    pattern = r'\[(?:PRESUP-TEMP|PRESUP-AWARE|PRESUP-CHANGE|PRESUP-ABILITY|' \
              r'EMBED-CMD|PACE|LEAD|TAG-Q|BIND-DOUBLE|BIND-CONSCIOUS-UNCONSCIOUS|' \
              r'BIND-TIME|BIND-CONSCIOUS|LOOP-OPEN [ABC]|LOOP-CLOSE [ABC]|' \
              r'ARCHETYPE|METAPHOR|METAPHOR-EXPAND|VAK-V|VAK-A|VAK-K)\]\s*'
    return re.sub(pattern, '', text)

def extract_script_sections(markdown_path):
    """Extract script content from markdown file"""
    with open(markdown_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by section markers
    sections = []
    current_section = None
    script_lines = []

    for line in content.split('\n'):
        # Detect section headers
        if line.startswith('## SECTION'):
            if current_section and script_lines:
                sections.append({
                    'name': current_section,
                    'script': '\n'.join(script_lines)
                })
                script_lines = []
            current_section = line.strip('#').strip()

        # Skip markdown headers, metadata lines
        elif line.startswith('#') or line.startswith('**') or line.startswith('---'):
            continue

        # Collect script content
        elif current_section and line.strip() and not line.startswith('###'):
            script_lines.append(line)

    # Add last section
    if current_section and script_lines:
        sections.append({
            'name': current_section,
            'script': '\n'.join(script_lines)
        })

    return sections

def create_ssml(sections):
    """Create complete SSML document with prosody"""

    ssml = '''<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
'''

    for i, section in enumerate(sections):
        name = section['name']
        script = strip_pattern_tags(section['script'])

        # Determine prosody based on section
        if 'PRE-TALK' in name:
            rate = "1.0"
            pitch = "0st"
        elif 'INDUCTION' in name:
            rate = "0.85"
            pitch = "-2st"
        elif 'EXPLORATION' in name or 'ACTIVATION' in name or 'INTEGRATION' in name:
            rate = "0.90"
            pitch = "-1st"
        elif 'CONSOLIDATION' in name:
            rate = "0.90"
            pitch = "0st"
        elif 'RETURN' in name:
            # Gradual speed increase - we'll use 0.95 as average
            rate = "0.95"
            pitch = "0st"
        else:
            rate = "0.90"
            pitch = "0st"

        # Wrap in prosody
        ssml += f'  <prosody rate="{rate}" pitch="{pitch}">\n'
        ssml += f'    {script}\n'
        ssml += '  </prosody>\n\n'

    ssml += '</speak>'

    return ssml

def main():
    print("Creating SSML voice script for Neural Network Navigator...")

    # Read meditation script
    script_path = 'MEDITATION_SCRIPT.md'
    output_path = 'working_files/voice_script.ssml'

    print(f"Reading {script_path}...")
    sections = extract_script_sections(script_path)
    print(f"Found {len(sections)} sections")

    print("Stripping pattern tags and creating SSML...")
    ssml = create_ssml(sections)

    print(f"Writing to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(ssml)

    print(f"✓ SSML voice script created successfully!")
    print(f"  File size: {len(ssml)} characters")
    print(f"  Sections: {len(sections)}")
    print(f"\nNext step: Generate voice audio with Edge TTS")

if __name__ == '__main__':
    main()
