#!/usr/bin/env python3
"""
SSML Validation Utility
Validates SSML syntax and provides helpful error messages

Usage:
    python scripts/utilities/validate_ssml.py path/to/script.ssml
"""

import sys
import os
import xml.etree.ElementTree as ET
from pathlib import Path

def validate_ssml(file_path):
    """Validate SSML file and provide detailed feedback"""

    print("=" * 70)
    print("   SSML Validation Utility")
    print("=" * 70)
    print()

    # Check file exists
    if not os.path.exists(file_path):
        print(f"❌ Error: File not found: {file_path}")
        return False

    print(f"📄 Validating: {file_path}")
    print()

    # Read file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

    # Check file size
    file_size = len(content.encode('utf-8'))
    print(f"📊 File size: {file_size:,} bytes")

    if file_size > 5000:
        print(f"⚠️  Warning: File is large ({file_size} bytes)")
        print(f"   Recommend using generate_audio_chunked.py")
    print()

    # Validate XML syntax
    try:
        root = ET.fromstring(content)
        print("✅ XML syntax is valid")
    except ET.ParseError as e:
        print(f"❌ XML Parse Error: {e}")
        print(f"   Line {e.position[0]}, Column {e.position[1]}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    # Check for <speak> root element
    if root.tag != 'speak':
        print(f"❌ Error: Root element should be <speak>, found <{root.tag}>")
        return False
    else:
        print("✅ Root <speak> element present")

    # Check for required attributes
    if 'version' not in root.attrib:
        print("⚠️  Warning: <speak> missing 'version' attribute")
    else:
        print(f"✅ Version: {root.attrib['version']}")

    if 'xml:lang' not in root.attrib:
        print("⚠️  Warning: <speak> missing 'xml:lang' attribute")
    else:
        print(f"✅ Language: {root.attrib['xml:lang']}")

    print()

    # Analyze content
    print("📋 Content Analysis:")
    print()

    # Count elements
    prosody_count = len(root.findall('.//prosody'))
    break_count = len(root.findall('.//break'))
    phoneme_count = len(root.findall('.//phoneme'))
    emphasis_count = len(root.findall('.//emphasis'))

    print(f"   <prosody> tags: {prosody_count}")
    print(f"   <break> tags: {break_count}")
    print(f"   <phoneme> tags: {phoneme_count}")
    print(f"   <emphasis> tags: {emphasis_count}")
    print()

    # Estimate duration
    text_content = ''.join(root.itertext())
    word_count = len(text_content.split())

    # Rough estimate: 150 words per minute for normal speech
    # Hypnosis is slower (rate=0.85), so ~130 wpm
    estimated_minutes = word_count / 130

    print(f"   Word count: {word_count:,}")
    print(f"   Estimated duration: {estimated_minutes:.1f} minutes")
    print()

    # Check for common issues
    issues_found = False

    print("🔍 Checking for common issues:")
    print()

    # Check for unclosed tags
    open_tags = content.count('<prosody')
    close_tags = content.count('</prosody>')
    if open_tags != close_tags:
        print(f"⚠️  Warning: Unmatched <prosody> tags (open: {open_tags}, close: {close_tags})")
        issues_found = True

    # Check for very long sections without breaks
    if break_count < (word_count / 100):
        print(f"⚠️  Warning: Low break density (recommend more <break> tags)")
        print(f"   Current: {break_count} breaks for {word_count} words")
        print(f"   Recommend: ~{word_count // 50} breaks")
        issues_found = True

    # Check for sections marked with [PLACEHOLDER]
    if '[' in text_content and ']' in text_content:
        import re
        placeholders = re.findall(r'\[([^\]]+)\]', text_content)
        if placeholders:
            print(f"⚠️  Warning: Found {len(placeholders)} placeholder(s):")
            for ph in placeholders[:5]:  # Show first 5
                print(f"   - [{ph}]")
            if len(placeholders) > 5:
                print(f"   ... and {len(placeholders) - 5} more")
            issues_found = True

    # Check for special characters that might need escaping
    if '&' in content and '&lt;' not in content and '&gt;' not in content:
        if content.count('&') != content.count('&amp;'):
            print("⚠️  Warning: Found unescaped '&' characters")
            print("   Use &amp; instead of & in text content")
            issues_found = True

    if not issues_found:
        print("✅ No common issues detected")

    print()
    print("=" * 70)
    print("✅ Validation Complete")
    print("=" * 70)
    print()

    return True


def main():
    if len(sys.argv) != 2:
        print("Usage: python validate_ssml.py <path-to-ssml-file>")
        print()
        print("Example:")
        print("  python scripts/utilities/validate_ssml.py sessions/my-session/script.ssml")
        sys.exit(1)

    file_path = sys.argv[1]

    if validate_ssml(file_path):
        print("✨ Your SSML is ready for audio generation!")
        sys.exit(0)
    else:
        print("❌ Please fix the issues above before generating audio")
        sys.exit(1)


if __name__ == '__main__':
    main()
