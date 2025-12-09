#!/usr/bin/env python3
"""
Anchor Tag Expansion Utility for Dreamweaving Scripts

Replaces {{ANCHOR:anchor_id}} tags in SSML scripts with the actual
anchor SSML templates from the anchor registry.

Usage:
    python expand_anchors.py input.ssml output.ssml
    python expand_anchors.py input.ssml output.ssml --mode reinforcement
    python expand_anchors.py input.ssml --in-place

Modes:
    installation (default): Full anchor installation SSML
    reinforcement: Shorter reinforcement SSML for previously installed anchors

Example tag in script:
    {{ANCHOR:kinesthetic.heart_touch_calm}}

This will be replaced with the installation_ssml or reinforcement_ssml
from the anchor registry.
"""

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install with: pip install pyyaml")
    sys.exit(1)


# Path to anchor registry
ANCHOR_REGISTRY_PATH = Path(__file__).parent.parent.parent / "knowledge" / "anchors" / "anchor_registry.yaml"


def load_anchor_registry():
    """Load the anchor registry from YAML file."""
    if not ANCHOR_REGISTRY_PATH.exists():
        print(f"Error: Anchor registry not found at {ANCHOR_REGISTRY_PATH}")
        sys.exit(1)

    with open(ANCHOR_REGISTRY_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_anchor_ssml(registry: dict, anchor_id: str, mode: str = "installation") -> str:
    """
    Get the SSML template for a specific anchor.

    Args:
        registry: The loaded anchor registry
        anchor_id: Full anchor ID (e.g., 'kinesthetic.heart_touch_calm')
        mode: 'installation' for full SSML, 'reinforcement' for shorter version

    Returns:
        The SSML template string, or error comment if not found
    """
    # Parse anchor_id into category and name (e.g., 'breath.calm_breath_slow_exhale')
    if '.' not in anchor_id:
        return f"<!-- ERROR: Invalid anchor_id format: {anchor_id} -->"

    category, anchor_name = anchor_id.split('.', 1)

    # Navigate to the category in the registry
    category_data = registry.get(category, {})
    if not category_data:
        return f"<!-- ERROR: Category not found: {category} -->"

    # Find the anchor within the category
    anchor = category_data.get(anchor_name)
    if not anchor:
        return f"<!-- ERROR: Anchor not found: {anchor_id} -->"

    templates = anchor.get('templates', {})

    if mode == "reinforcement":
        ssml = templates.get('reinforcement_ssml', '')
        if not ssml:
            # Fall back to installation if no reinforcement available
            ssml = templates.get('installation_ssml', '')
    else:
        ssml = templates.get('installation_ssml', '')

    if ssml:
        # Clean up the SSML (remove leading/trailing whitespace per line)
        lines = [line.strip() for line in ssml.strip().split('\n')]
        return '\n'.join(lines)
    else:
        return f"<!-- ERROR: No {mode} SSML found for anchor {anchor_id} -->"


def expand_anchor_tags(content: str, registry: dict, mode: str = "installation") -> tuple:
    """
    Replace all {{ANCHOR:anchor_id}} tags with SSML content.

    Args:
        content: SSML script content
        registry: Loaded anchor registry
        mode: 'installation' or 'reinforcement'

    Returns:
        Tuple of (expanded_content, list of replacements made)
    """
    pattern = r'\{\{ANCHOR:([a-z_]+\.[a-z0-9_]+)\}\}'
    replacements = []

    def replace_tag(match):
        anchor_id = match.group(1)
        ssml = get_anchor_ssml(registry, anchor_id, mode)
        replacements.append({
            'anchor_id': anchor_id,
            'mode': mode,
            'success': not ssml.startswith('<!-- ERROR')
        })
        return ssml

    expanded = re.sub(pattern, replace_tag, content)
    return expanded, replacements


def find_anchor_tags(content: str) -> list:
    """Find all anchor tags in content without replacing them."""
    pattern = r'\{\{ANCHOR:([a-z_]+\.[a-z0-9_]+)\}\}'
    return re.findall(pattern, content)


def main():
    parser = argparse.ArgumentParser(
        description="Expand {{ANCHOR:id}} tags in SSML scripts"
    )
    parser.add_argument('input', help="Input SSML file")
    parser.add_argument('output', nargs='?', help="Output SSML file (optional if --in-place)")
    parser.add_argument('--mode', choices=['installation', 'reinforcement'],
                       default='installation',
                       help="Anchor mode: installation (full) or reinforcement (short)")
    parser.add_argument('--in-place', action='store_true',
                       help="Modify input file in place")
    parser.add_argument('--dry-run', action='store_true',
                       help="Show what would be replaced without making changes")
    parser.add_argument('-v', '--verbose', action='store_true',
                       help="Verbose output")

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)

    # Determine output path
    if args.in_place:
        output_path = input_path
    elif args.output:
        output_path = Path(args.output)
    else:
        print("Error: Specify output file or use --in-place")
        sys.exit(1)

    # Load content and registry
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    registry = load_anchor_registry()

    # Find all tags first
    tags_found = find_anchor_tags(content)

    if not tags_found:
        print("No {{ANCHOR:...}} tags found in input file.")
        sys.exit(0)

    print(f"Found {len(tags_found)} anchor tag(s):")
    for tag in tags_found:
        print(f"  - {tag}")

    if args.dry_run:
        print("\n[Dry run - no changes made]")
        sys.exit(0)

    # Expand tags
    expanded, replacements = expand_anchor_tags(content, registry, args.mode)

    # Report results
    successful = sum(1 for r in replacements if r['success'])
    failed = len(replacements) - successful

    print(f"\nExpanded {successful}/{len(replacements)} anchors (mode: {args.mode})")

    if failed > 0:
        print(f"\nWarnings ({failed} failed):")
        for r in replacements:
            if not r['success']:
                print(f"  - {r['anchor_id']}: Not found in registry")

    if args.verbose:
        print("\nReplacements:")
        for r in replacements:
            status = "OK" if r['success'] else "FAILED"
            print(f"  [{status}] {r['anchor_id']}")

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(expanded)

    print(f"\nOutput written to: {output_path}")


if __name__ == "__main__":
    main()
