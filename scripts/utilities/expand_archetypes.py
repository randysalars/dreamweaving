#!/usr/bin/env python3
"""
Archetype Tag Expansion Utility for Dreamweaving Scripts

Replaces {{ARCHETYPE:archetype_id:context}} tags in SSML scripts with the actual
archetype SSML templates from the archetype codex.

Usage:
    python expand_archetypes.py input.ssml output.ssml
    python expand_archetypes.py input.ssml output.ssml --encounter-type return
    python expand_archetypes.py input.ssml --in-place
    python expand_archetypes.py input.ssml output.ssml --tradition christian

Tag Format:
    {{ARCHETYPE:family.archetype_name}}
    {{ARCHETYPE:family.archetype_name:first_encounter}}
    {{ARCHETYPE:family.archetype_name:return_encounter}}
    {{ARCHETYPE:family.archetype_name:transformation}}

Examples:
    {{ARCHETYPE:divine_light_healing.inner_healer}}
    {{ARCHETYPE:warrior_power.archangel_michael:first_encounter}}
    {{ARCHETYPE:divine_feminine.rose_mother:return_encounter}}

The context (first_encounter, return_encounter, transformation) determines which
SSML template is used from the archetype codex. If omitted, defaults to first_encounter.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install with: pip install pyyaml")
    sys.exit(1)


# Paths to knowledge files
KNOWLEDGE_DIR = Path(__file__).parent.parent.parent / "knowledge"
ARCHETYPE_CODEX_PATH = KNOWLEDGE_DIR / "archetypes" / "archetype_codex.yaml"
ARCHETYPE_HISTORY_PATH = KNOWLEDGE_DIR / "archetypes" / "archetype_history.yaml"
TRADITION_INDEX_PATH = KNOWLEDGE_DIR / "indexes" / "tradition_equivalence_index.yaml"


def load_yaml_file(path: Path) -> dict:
    """Load a YAML file safely."""
    if not path.exists():
        print(f"Warning: File not found: {path}")
        return {}

    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def load_archetype_codex() -> dict:
    """
    Load the archetype codex from YAML file.

    The codex is organized by family, so we flatten it into a single dict
    keyed by archetype name.
    """
    if not ARCHETYPE_CODEX_PATH.exists():
        print(f"Error: Archetype codex not found at {ARCHETYPE_CODEX_PATH}")
        sys.exit(1)

    with open(ARCHETYPE_CODEX_PATH, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    # If there's a flat 'archetypes' key, use it
    if 'archetypes' in data:
        return data['archetypes']

    # Otherwise, extract archetypes from family sections
    archetypes = {}
    skip_keys = {'metadata', 'archetype_schema'}

    for family_name, family_data in data.items():
        if family_name in skip_keys:
            continue
        if not isinstance(family_data, dict):
            continue

        # Each family has a family_metadata key and archetype entries
        for key, value in family_data.items():
            if key == 'family_metadata':
                continue
            if isinstance(value, dict) and 'archetype_id' in value:
                archetypes[key] = value

    return archetypes


def load_archetype_history() -> dict:
    """Load archetype history for encounter type detection."""
    return load_yaml_file(ARCHETYPE_HISTORY_PATH)


def load_tradition_index() -> dict:
    """Load tradition equivalence index for name translation."""
    return load_yaml_file(TRADITION_INDEX_PATH)


def get_encounter_type_from_history(history: dict, archetype_id: str) -> str:
    """
    Determine encounter type based on listener history.

    Returns:
        'first_encounter' if archetype hasn't been used before
        'return_encounter' if archetype has been used
        'transformation' if relationship level >= 3
    """
    relationships = history.get('listener_relationships', {})

    if archetype_id not in relationships:
        return 'first_encounter'

    rel = relationships[archetype_id]
    level = rel.get('relationship_level', 1)

    if level >= 3:
        return 'transformation'
    elif level >= 2:
        return 'return_encounter'
    else:
        return 'first_encounter'


def get_tradition_name(
    tradition_index: dict,
    archetype_id: str,
    tradition: str
) -> Optional[str]:
    """Get tradition-specific name for an archetype."""
    if tradition == 'universal':
        return None

    traditions = tradition_index.get('traditions', {})
    tradition_data = traditions.get(tradition, {})
    archetypes = tradition_data.get('archetypes', {})

    # Parse archetype_id to get base name (without family prefix)
    if '.' in archetype_id:
        _, archetype_name = archetype_id.rsplit('.', 1)
    else:
        archetype_name = archetype_id

    return archetypes.get(archetype_name)


def get_archetype_ssml(
    codex: dict,
    archetype_id: str,
    context: str = "first_encounter",
    tradition: Optional[str] = None,
    tradition_index: Optional[dict] = None
) -> str:
    """
    Get the SSML template for a specific archetype.

    Args:
        codex: The loaded archetype codex
        archetype_id: Full archetype ID (e.g., 'divine_light_healing.inner_healer')
        context: 'first_encounter', 'return_encounter', or 'transformation'
        tradition: Optional tradition for name translation
        tradition_index: Loaded tradition index for name lookup

    Returns:
        The SSML template string, or error comment if not found
    """
    # Parse archetype_id (e.g., 'divine_light_healing.inner_healer')
    if '.' not in archetype_id:
        return f"<!-- ERROR: Invalid archetype_id format: {archetype_id} (expected family.name) -->"

    family, archetype_name = archetype_id.split('.', 1)

    # Find the archetype in the codex
    archetype = codex.get(archetype_name)
    if not archetype:
        return f"<!-- ERROR: Archetype not found in codex: {archetype_id} -->"

    # Verify family matches
    if archetype.get('family') != family:
        return f"<!-- WARNING: Family mismatch for {archetype_id} (expected {archetype.get('family')}) -->"

    # Get the appropriate template
    templates = archetype.get('templates', {})

    # Map context to template key
    template_keys = {
        'first_encounter': 'first_encounter_ssml',
        'return_encounter': 'return_encounter_ssml',
        'transformation': 'transformation_ssml',
        'integration': 'transformation_ssml'  # fallback
    }

    template_key = template_keys.get(context, 'first_encounter_ssml')
    ssml = templates.get(template_key, '')

    # If requested template not available, fall back to first_encounter
    if not ssml and template_key != 'first_encounter_ssml':
        ssml = templates.get('first_encounter_ssml', '')
        if ssml:
            ssml = f"<!-- Note: Using first_encounter template (no {context} template available) -->\n{ssml}"

    if not ssml:
        return f"<!-- ERROR: No SSML template found for archetype {archetype_id} -->"

    # Handle tradition-specific naming
    if tradition and tradition != 'universal' and tradition_index:
        tradition_name = get_tradition_name(tradition_index, archetype_id, tradition)
        if tradition_name:
            # Replace the universal name with tradition-specific name
            universal_name = archetype.get('name', '')
            if universal_name:
                ssml = ssml.replace(universal_name, tradition_name)

    # Clean up the SSML (remove leading/trailing whitespace per line, preserve structure)
    lines = ssml.strip().split('\n')
    cleaned_lines = []
    for line in lines:
        # Preserve intentional indentation for SSML structure
        stripped = line.rstrip()
        cleaned_lines.append(stripped)

    return '\n'.join(cleaned_lines)


def expand_archetype_tags(
    content: str,
    codex: dict,
    default_context: str = "first_encounter",
    tradition: Optional[str] = None,
    tradition_index: Optional[dict] = None,
    history: Optional[dict] = None,
    auto_detect_encounter: bool = False
) -> tuple:
    """
    Replace all {{ARCHETYPE:archetype_id:context}} tags with SSML content.

    Args:
        content: SSML script content
        codex: Loaded archetype codex
        default_context: Default encounter type if not specified in tag
        tradition: Tradition for name translation
        tradition_index: Loaded tradition index
        history: Archetype history for auto-detection
        auto_detect_encounter: If True, determine encounter type from history

    Returns:
        Tuple of (expanded_content, list of replacements made)
    """
    # Pattern matches both formats:
    # {{ARCHETYPE:family.name}} and {{ARCHETYPE:family.name:context}}
    pattern = r'\{\{ARCHETYPE:([a-z_]+\.[a-z_]+)(?::([a-z_]+))?\}\}'
    replacements = []

    def replace_tag(match):
        archetype_id = match.group(1)
        explicit_context = match.group(2)

        # Determine context
        if explicit_context:
            context = explicit_context
        elif auto_detect_encounter and history:
            context = get_encounter_type_from_history(history, archetype_id)
        else:
            context = default_context

        ssml = get_archetype_ssml(
            codex, archetype_id, context, tradition, tradition_index
        )

        replacements.append({
            'archetype_id': archetype_id,
            'context': context,
            'tradition': tradition or 'universal',
            'success': not ssml.startswith('<!-- ERROR')
        })

        return ssml

    expanded = re.sub(pattern, replace_tag, content)
    return expanded, replacements


def find_archetype_tags(content: str) -> list:
    """Find all archetype tags in content without replacing them."""
    pattern = r'\{\{ARCHETYPE:([a-z_]+\.[a-z_]+)(?::([a-z_]+))?\}\}'
    matches = re.findall(pattern, content)
    # Return list of (archetype_id, context) tuples
    return [(m[0], m[1] if m[1] else None) for m in matches]


def validate_archetype_tags(content: str, codex: dict) -> list:
    """
    Validate all archetype tags in content against the codex.

    Returns list of validation issues.
    """
    tags = find_archetype_tags(content)
    issues = []

    for archetype_id, context in tags:
        if '.' not in archetype_id:
            issues.append(f"Invalid format: {archetype_id}")
            continue

        family, archetype_name = archetype_id.split('.', 1)
        archetype = codex.get(archetype_name)

        if not archetype:
            issues.append(f"Not in codex: {archetype_id}")
        elif archetype.get('family') != family:
            issues.append(f"Family mismatch: {archetype_id} (actual: {archetype.get('family')})")
        else:
            # Check if requested template exists
            templates = archetype.get('templates', {})
            if context:
                template_key = f"{context}_ssml"
                if template_key not in templates:
                    issues.append(f"No {context} template: {archetype_id}")

    return issues


def main():
    parser = argparse.ArgumentParser(
        description="Expand {{ARCHETYPE:id:context}} tags in SSML scripts"
    )
    parser.add_argument('input', help="Input SSML file")
    parser.add_argument('output', nargs='?', help="Output SSML file (optional if --in-place)")
    parser.add_argument('--encounter-type', choices=['first_encounter', 'return_encounter', 'transformation'],
                       default='first_encounter',
                       help="Default encounter type for tags without explicit context")
    parser.add_argument('--tradition',
                       choices=['universal', 'christian', 'jewish', 'islamic', 'hindu',
                               'buddhist', 'egyptian', 'greek', 'norse', 'celtic',
                               'mayan', 'shamanic', 'taoist', 'gnostic'],
                       default='universal',
                       help="Use tradition-specific archetype names")
    parser.add_argument('--auto-detect', action='store_true',
                       help="Auto-detect encounter type from archetype history")
    parser.add_argument('--in-place', action='store_true',
                       help="Modify input file in place")
    parser.add_argument('--dry-run', action='store_true',
                       help="Show what would be replaced without making changes")
    parser.add_argument('--validate', action='store_true',
                       help="Only validate tags without expanding")
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
    elif not args.dry_run and not args.validate:
        print("Error: Specify output file or use --in-place")
        sys.exit(1)
    else:
        output_path = None

    # Load content
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Load codex
    codex = load_archetype_codex()

    # Find all tags first
    tags_found = find_archetype_tags(content)

    if not tags_found:
        print("No {{ARCHETYPE:...}} tags found in input file.")
        sys.exit(0)

    print(f"Found {len(tags_found)} archetype tag(s):")
    for arch_id, context in tags_found:
        ctx_str = f":{context}" if context else ""
        print(f"  - {arch_id}{ctx_str}")

    # Validate only mode
    if args.validate:
        issues = validate_archetype_tags(content, codex)
        if issues:
            print(f"\nValidation issues ({len(issues)}):")
            for issue in issues:
                print(f"  - {issue}")
            sys.exit(1)
        else:
            print("\nAll archetype tags are valid.")
            sys.exit(0)

    if args.dry_run:
        print("\n[Dry run - no changes made]")
        sys.exit(0)

    # Load optional resources
    tradition_index = None
    if args.tradition != 'universal':
        tradition_index = load_tradition_index()

    history = None
    if args.auto_detect:
        history = load_archetype_history()

    # Expand tags
    expanded, replacements = expand_archetype_tags(
        content, codex,
        default_context=args.encounter_type,
        tradition=args.tradition,
        tradition_index=tradition_index,
        history=history,
        auto_detect_encounter=args.auto_detect
    )

    # Report results
    successful = sum(1 for r in replacements if r['success'])
    failed = len(replacements) - successful

    print(f"\nExpanded {successful}/{len(replacements)} archetypes")
    print(f"  Default encounter type: {args.encounter_type}")
    print(f"  Tradition: {args.tradition}")
    if args.auto_detect:
        print("  Auto-detect from history: enabled")

    if failed > 0:
        print(f"\nWarnings ({failed} failed):")
        for r in replacements:
            if not r['success']:
                print(f"  - {r['archetype_id']}: Expansion failed")

    if args.verbose:
        print("\nReplacements:")
        for r in replacements:
            status = "OK" if r['success'] else "FAILED"
            print(f"  [{status}] {r['archetype_id']} ({r['context']}, {r['tradition']})")

    # Write output
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(expanded)
        print(f"\nOutput written to: {output_path}")


if __name__ == "__main__":
    main()
