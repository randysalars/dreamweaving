#!/usr/bin/env python3
"""
Convert SSML to plain text for Edge TTS
"""

import re
from pathlib import Path

def strip_ssml(ssml_content):
    """Remove SSML tags and keep only the text content"""

    # Remove comments
    text = re.sub(r'<!--.*?-->', '', ssml_content, flags=re.DOTALL)

    # Remove all XML/SSML tags but keep their content
    text = re.sub(r'<[^>]+>', '', text)

    # Clean up extra whitespace
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Multiple blank lines to double
    text = re.sub(r'  +', ' ', text)  # Multiple spaces to single
    text = text.strip()

    return text

def main():
    ssml_file = Path("script.ssml")
    output_file = Path("script.txt")

    print(f"Reading {ssml_file}...")
    with open(ssml_file, 'r', encoding='utf-8') as f:
        ssml_content = f.read()

    text = strip_ssml(ssml_content)

    print(f"Writing plain text to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(text)

    print(f"✅ Converted {len(ssml_content)} chars SSML to {len(text)} chars text")
    print(f"   Output: {output_file}")

if __name__ == "__main__":
    main()
