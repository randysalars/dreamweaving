#!/usr/bin/env python3
"""
Archetype Validation Utility for Dreamweaving Sessions

Validates archetype usage in session manifests and SSML scripts against
the archetype codex, checking for:
- Valid archetype IDs
- Family consistency
- Outcome alignment
- Minimum archetype count
- No conflicting archetypes
- Appropriate encounter types
- Unexpanded archetype tags in scripts

Usage:
    python validate_archetypes.py sessions/{session}/
    python validate_archetypes.py sessions/{session}/ --verbose
    python validate_archetypes.py sessions/{session}/ --fix-encounter-types
    python validate_archetypes.py --check-codex  # Validate codex itself
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install with: pip install pyyaml")
    sys.exit(1)


# Paths to knowledge files
KNOWLEDGE_DIR = Path(__file__).parent.parent.parent / "knowledge"
ARCHETYPE_CODEX_PATH = KNOWLEDGE_DIR / "archetypes" / "archetype_codex.yaml"
ARCHETYPE_HISTORY_PATH = KNOWLEDGE_DIR / "archetypes" / "archetype_history.yaml"
FAMILY_INDEX_PATH = KNOWLEDGE_DIR / "indexes" / "archetype_family_index.yaml"
OUTCOME_INDEX_PATH = KNOWLEDGE_DIR / "indexes" / "outcome_index.yaml"


class ValidationResult:
    """Holds validation results with errors, warnings, and info."""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []

    def add_error(self, msg: str):
        self.errors.append(msg)

    def add_warning(self, msg: str):
        self.warnings.append(msg)

    def add_info(self, msg: str):
        self.info.append(msg)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def print_report(self, verbose: bool = False):
        """Print validation report."""
        if self.errors:
            print(f"\n ERRORS ({len(self.errors)}):")
            for err in self.errors:
                print(f"  - {err}")

        if self.warnings:
            print(f"\n WARNINGS ({len(self.warnings)}):")
            for warn in self.warnings:
                print(f"  - {warn}")

        if verbose and self.info:
            print(f"\n INFO ({len(self.info)}):")
            for info in self.info:
                print(f"  - {info}")

        if self.is_valid:
            print("\n Validation PASSED")
        else:
            print("\n Validation FAILED")


def load_yaml_file(path: Path) -> dict:
    """Load a YAML file safely."""
    if not path.exists():
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def load_archetype_codex() -> dict:
    """
    Load the archetype codex.

    The codex is organized by family, so we flatten it into a single dict
    keyed by archetype name.
    """
    data = load_yaml_file(ARCHETYPE_CODEX_PATH)

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


def load_family_index() -> dict:
    """Load the family index."""
    data = load_yaml_file(FAMILY_INDEX_PATH)
    return data.get('families', {})


def load_outcome_index() -> dict:
    """Load the outcome index."""
    return load_yaml_file(OUTCOME_INDEX_PATH)


def validate_codex_itself() -> ValidationResult:
    """
    Validate the archetype codex structure and completeness.
    """
    result = ValidationResult()

    if not ARCHETYPE_CODEX_PATH.exists():
        result.add_error(f"Archetype codex not found: {ARCHETYPE_CODEX_PATH}")
        return result

    archetypes = load_archetype_codex()

    if not archetypes:
        result.add_error("No archetypes defined in codex")
        return result

    result.add_info(f"Found {len(archetypes)} archetypes in codex")

    # Load family index for cross-reference
    family_index = load_family_index()

    # Required fields for each archetype
    required_fields = ['archetype_id', 'name', 'family', 'definition', 'attributes', 'templates']
    required_attributes = ['primary_color', 'frequency_hz', 'brainwave_target', 'element', 'chakra']
    required_templates = ['first_encounter_ssml']

    # Track families found
    families_found = set()

    for arch_name, arch_data in archetypes.items():
        prefix = f"Archetype '{arch_name}'"

        # Check required fields
        for field in required_fields:
            if field not in arch_data:
                result.add_error(f"{prefix}: Missing required field '{field}'")

        # Check archetype_id format
        arch_id = arch_data.get('archetype_id', '')
        if arch_id:
            if '.' not in arch_id:
                result.add_error(f"{prefix}: Invalid archetype_id format '{arch_id}' (expected family.name)")
            else:
                family, name = arch_id.split('.', 1)
                if name != arch_name:
                    result.add_warning(f"{prefix}: archetype_id name '{name}' doesn't match key '{arch_name}'")
                if arch_data.get('family') and arch_data['family'] != family:
                    result.add_error(f"{prefix}: Family mismatch - archetype_id says '{family}' but family field says '{arch_data['family']}'")
                families_found.add(family)

        # Check attributes
        attributes = arch_data.get('attributes', {})
        for attr in required_attributes:
            if attr not in attributes:
                result.add_warning(f"{prefix}: Missing attribute '{attr}'")

        # Check templates
        templates = arch_data.get('templates', {})
        for tmpl in required_templates:
            if tmpl not in templates:
                result.add_warning(f"{prefix}: Missing template '{tmpl}'")
            elif not templates[tmpl].strip():
                result.add_warning(f"{prefix}: Empty template '{tmpl}'")

        # Validate SSML in templates
        for tmpl_name, tmpl_content in templates.items():
            if tmpl_content and '<prosody' in tmpl_content:
                if '</prosody>' not in tmpl_content:
                    result.add_error(f"{prefix}: Unclosed <prosody> tag in template '{tmpl_name}'")
                if 'rate="' in tmpl_content:
                    # Check for slow rates
                    if 'rate="0.8' in tmpl_content or 'rate="0.9' in tmpl_content:
                        result.add_warning(f"{prefix}: Template '{tmpl_name}' uses slow rate (should be 1.0)")

        # Check tradition_equivalents if present
        trad_equiv = arch_data.get('tradition_equivalents', {})
        if trad_equiv:
            result.add_info(f"{prefix}: Has {len(trad_equiv)} tradition equivalents")

    # Check family coverage
    if family_index:
        expected_families = set(family_index.keys())
        missing_families = expected_families - families_found
        if missing_families:
            result.add_info(f"Families with no archetypes yet: {', '.join(sorted(missing_families))}")

    return result


def validate_manifest_archetypes(session_path: Path) -> ValidationResult:
    """
    Validate archetypes in a session manifest.yaml.
    """
    result = ValidationResult()
    manifest_path = session_path / "manifest.yaml"

    if not manifest_path.exists():
        result.add_error(f"Manifest not found: {manifest_path}")
        return result

    manifest = load_yaml_file(manifest_path)
    archetypes = manifest.get('archetypes', [])

    if not archetypes:
        result.add_warning("No archetypes defined in manifest")
        return result

    result.add_info(f"Found {len(archetypes)} archetypes in manifest")

    # Load codex for validation
    codex = load_archetype_codex()

    # Get session outcome for alignment check
    session_data = manifest.get('session', {})
    desired_outcome = session_data.get('desired_outcome', '')

    # Track families used for diversity check
    families_used = []
    roles_used = []

    for i, arch in enumerate(archetypes):
        prefix = f"Archetype [{i}]"
        arch_id = arch.get('archetype_id')
        name = arch.get('name', 'unnamed')

        # If using new codex format
        if arch_id:
            prefix = f"Archetype '{arch_id}'"

            # Validate ID format
            if '.' not in arch_id:
                result.add_error(f"{prefix}: Invalid archetype_id format (expected family.name)")
                continue

            family, arch_name = arch_id.split('.', 1)
            families_used.append(family)

            # Check if archetype exists in codex
            if arch_name not in codex:
                result.add_error(f"{prefix}: Not found in archetype codex")
                continue

            codex_entry = codex[arch_name]

            # Verify family matches
            if codex_entry.get('family') != family:
                result.add_error(f"{prefix}: Family mismatch (manifest: {family}, codex: {codex_entry.get('family')})")

            # Check encounter_type
            encounter_type = arch.get('encounter_type')
            if encounter_type:
                valid_types = ['first_encounter', 'return_encounter', 'transformation', 'integration']
                if encounter_type not in valid_types:
                    result.add_error(f"{prefix}: Invalid encounter_type '{encounter_type}'")

            # Check relationship_level
            rel_level = arch.get('relationship_level')
            if rel_level is not None:
                if not isinstance(rel_level, int) or rel_level < 1 or rel_level > 4:
                    result.add_error(f"{prefix}: relationship_level must be 1-4")

            # Check outcome alignment
            if desired_outcome:
                applications = codex_entry.get('applications', {})
                outcome_alignment = applications.get('outcome_alignment', [])
                if outcome_alignment and desired_outcome not in outcome_alignment:
                    result.add_warning(f"{prefix}: May not align with desired outcome '{desired_outcome}' (aligned: {outcome_alignment})")

        # Check role
        role = arch.get('role')
        if role:
            roles_used.append(role)
            valid_roles = ['primary', 'secondary', 'supporting', 'transitional',
                          'guidance', 'transformation', 'wisdom_keeper', 'healing', 'higher_self', 'vessel']
            if role not in valid_roles:
                result.add_warning(f"{prefix}: Unknown role '{role}'")

    # Check minimum archetype count
    if len(archetypes) < 2:
        result.add_warning("Recommended: At least 2 archetypes per session")

    # Check for family diversity
    if len(families_used) > 0 and len(set(families_used)) == 1 and len(families_used) > 2:
        result.add_warning(f"Low family diversity: All {len(families_used)} archetypes from '{families_used[0]}' family")

    # Check for primary role
    if roles_used and 'primary' not in roles_used:
        result.add_info("No archetype marked as 'primary' role")

    return result


def validate_script_archetypes(session_path: Path) -> ValidationResult:
    """
    Validate archetype tags in SSML scripts.
    """
    result = ValidationResult()

    # Check both production and voice-clean scripts
    script_paths = [
        session_path / "working_files" / "script_production.ssml",
        session_path / "working_files" / "script_voice_clean.ssml",
        session_path / "working_files" / "script.ssml",
    ]

    scripts_found = []
    for script_path in script_paths:
        if script_path.exists():
            scripts_found.append(script_path)

    if not scripts_found:
        result.add_info("No SSML scripts found to validate")
        return result

    codex = load_archetype_codex()

    # Pattern for archetype tags
    pattern = r'\{\{ARCHETYPE:([a-z_]+\.[a-z_]+)(?::([a-z_]+))?\}\}'

    for script_path in scripts_found:
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()

        matches = re.findall(pattern, content)

        if matches:
            result.add_warning(f"{script_path.name}: Found {len(matches)} unexpanded ARCHETYPE tags")

            for arch_id, context in matches:
                if '.' in arch_id:
                    _, arch_name = arch_id.split('.', 1)
                    if arch_name not in codex:
                        result.add_error(f"{script_path.name}: Unknown archetype '{arch_id}'")
                    else:
                        result.add_info(f"  - {arch_id}" + (f":{context}" if context else ""))

    return result


def validate_session(session_path: Path, verbose: bool = False) -> ValidationResult:
    """
    Complete validation of a session's archetype usage.
    """
    result = ValidationResult()

    if not session_path.exists():
        result.add_error(f"Session path not found: {session_path}")
        return result

    result.add_info(f"Validating session: {session_path.name}")

    # Validate manifest archetypes
    manifest_result = validate_manifest_archetypes(session_path)
    result.errors.extend(manifest_result.errors)
    result.warnings.extend(manifest_result.warnings)
    result.info.extend(manifest_result.info)

    # Validate script archetypes
    script_result = validate_script_archetypes(session_path)
    result.errors.extend(script_result.errors)
    result.warnings.extend(script_result.warnings)
    result.info.extend(script_result.info)

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Validate archetype usage in Dreamweaving sessions"
    )
    parser.add_argument('session_path', nargs='?', help="Path to session directory")
    parser.add_argument('--check-codex', action='store_true',
                       help="Validate the archetype codex itself")
    parser.add_argument('--fix-encounter-types', action='store_true',
                       help="Auto-fix encounter types based on history (not yet implemented)")
    parser.add_argument('-v', '--verbose', action='store_true',
                       help="Verbose output with info messages")

    args = parser.parse_args()

    # Validate codex mode
    if args.check_codex:
        print("Validating Archetype Codex...")
        result = validate_codex_itself()
        result.print_report(args.verbose)
        sys.exit(0 if result.is_valid else 1)

    # Session validation mode
    if not args.session_path:
        parser.print_help()
        sys.exit(1)

    session_path = Path(args.session_path)
    print(f"Validating archetypes in: {session_path}")

    result = validate_session(session_path, args.verbose)
    result.print_report(args.verbose)

    sys.exit(0 if result.is_valid else 1)


if __name__ == "__main__":
    main()
