#!/usr/bin/env python3
"""
Manifest validation utility for Dreamweaving sessions.

Validates manifest.yaml files against the JSON schema and performs
additional semantic checks (e.g., section timing consistency).

Usage:
    python validate_manifest.py sessions/my-session/manifest.yaml
    python validate_manifest.py --all  # Validate all sessions
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Tuple, Optional

import yaml

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False
    print("Warning: jsonschema not installed. Install with: pip install jsonschema")

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from scripts.utilities.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


def load_schema() -> dict:
    """Load the manifest JSON schema."""
    # Try multiple locations for the schema
    schema_paths = [
        PROJECT_ROOT / "schemas" / "manifest.schema.json",
        PROJECT_ROOT / "config" / "manifest.schema.json",
    ]

    for schema_path in schema_paths:
        if schema_path.exists():
            with open(schema_path, 'r') as f:
                return json.load(f)

    raise FileNotFoundError(f"Schema not found in: {[str(p) for p in schema_paths]}")


def load_manifest(manifest_path: Path) -> dict:
    """Load a manifest.yaml file."""
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    with open(manifest_path, 'r') as f:
        return yaml.safe_load(f)


def validate_schema(manifest: dict, schema: dict) -> List[str]:
    """
    Validate manifest against JSON schema.

    Returns:
        List of validation error messages (empty if valid)
    """
    if not HAS_JSONSCHEMA:
        return ["jsonschema not installed - schema validation skipped"]

    errors = []
    validator = jsonschema.Draft7Validator(schema)

    for error in validator.iter_errors(manifest):
        path = " -> ".join(str(p) for p in error.absolute_path) if error.absolute_path else "root"
        errors.append(f"[{path}] {error.message}")

    return errors


def validate_sections_timing(manifest: dict) -> List[str]:
    """
    Validate that sections have consistent timing.

    Checks:
    - Sections are in chronological order
    - No gaps between sections
    - End times don't exceed session duration
    - No overlapping sections
    """
    errors = []
    sections = manifest.get("sections", [])
    session_duration = manifest.get("session", {}).get("duration", 0)

    if not sections:
        errors.append("No sections defined")
        return errors

    prev_end = 0
    for i, section in enumerate(sections):
        name = section.get("name", f"section_{i}")
        start = section.get("start", 0)
        end = section.get("end", 0)

        # Check chronological order
        if start < prev_end:
            errors.append(f"Section '{name}' starts at {start}s but previous section ends at {prev_end}s (overlap)")

        # Check for gaps
        if start > prev_end and i > 0:
            gap = start - prev_end
            errors.append(f"Gap of {gap}s between sections before '{name}'")

        # Check start < end
        if start >= end:
            errors.append(f"Section '{name}' has invalid timing: start ({start}) >= end ({end})")

        # Check against session duration
        if end > session_duration:
            errors.append(f"Section '{name}' ends at {end}s but session duration is {session_duration}s")

        prev_end = end

    # Check that sections cover full duration
    if sections and prev_end < session_duration:
        errors.append(f"Sections end at {prev_end}s but session duration is {session_duration}s")

    return errors


def validate_binaural_sections(manifest: dict) -> List[str]:
    """Validate binaural beat section timing."""
    errors = []
    sound_bed = manifest.get("sound_bed", {})
    binaural = sound_bed.get("binaural", {})

    if not binaural.get("enabled", False):
        return errors

    session_duration = manifest.get("session", {}).get("duration", 0)
    sections = binaural.get("sections", [])

    for i, section in enumerate(sections):
        start = section.get("start", 0)
        end = section.get("end", 0)
        offset_hz = section.get("offset_hz", 0)

        if start >= end:
            errors.append(f"Binaural section {i}: start ({start}) >= end ({end})")

        if end > session_duration:
            errors.append(f"Binaural section {i}: ends at {end}s, exceeds duration {session_duration}s")

        if offset_hz < 0.5 or offset_hz > 100:
            errors.append(f"Binaural section {i}: offset_hz ({offset_hz}) outside range [0.5, 100]")

    return errors


def validate_voice_provider(manifest: dict) -> List[str]:
    """Check for deprecated voice providers."""
    errors = []
    voice = manifest.get("voice", {})
    provider = voice.get("provider", "")

    if provider == "edge-tts":
        errors.append("Warning: edge-tts provider is deprecated. Use 'google' for production.")

    return errors


def validate_fx_timeline(manifest: dict) -> List[str]:
    """Validate effects timeline."""
    errors = []
    fx_timeline = manifest.get("fx_timeline", [])
    session_duration = manifest.get("session", {}).get("duration", 0)

    for i, fx in enumerate(fx_timeline):
        time = fx.get("time", 0)
        duration = fx.get("duration_s", 0)

        if time > session_duration:
            errors.append(f"Effect {i}: triggers at {time}s, exceeds session duration {session_duration}s")

        if time + duration > session_duration:
            errors.append(f"Effect {i}: ends at {time + duration}s, exceeds session duration")

    return errors


def validate_manifest(manifest_path: Path) -> Tuple[bool, List[str], List[str]]:
    """
    Validate a manifest file.

    Returns:
        Tuple of (is_valid, errors, warnings)
    """
    errors = []
    warnings = []

    try:
        manifest = load_manifest(manifest_path)
    except Exception as e:
        return False, [f"Failed to load manifest: {e}"], []

    try:
        schema = load_schema()
        schema_errors = validate_schema(manifest, schema)
        errors.extend(schema_errors)
    except FileNotFoundError:
        warnings.append("Schema file not found - schema validation skipped")
    except Exception as e:
        warnings.append(f"Schema validation error: {e}")

    # Semantic validations
    errors.extend(validate_sections_timing(manifest))
    errors.extend(validate_binaural_sections(manifest))
    errors.extend(validate_fx_timeline(manifest))

    # Warnings (not errors)
    provider_warnings = validate_voice_provider(manifest)
    warnings.extend(provider_warnings)

    is_valid = len(errors) == 0
    return is_valid, errors, warnings


def find_all_manifests() -> List[Path]:
    """Find all manifest.yaml files in sessions directory."""
    sessions_dir = PROJECT_ROOT / "sessions"
    manifests = []

    for session_dir in sessions_dir.iterdir():
        if session_dir.is_dir() and not session_dir.name.startswith('.'):
            manifest_path = session_dir / "manifest.yaml"
            if manifest_path.exists():
                manifests.append(manifest_path)

    return sorted(manifests)


def main():
    parser = argparse.ArgumentParser(
        description="Validate Dreamweaving session manifest files"
    )
    parser.add_argument(
        "manifest",
        nargs="?",
        help="Path to manifest.yaml file"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Validate all manifests in sessions/"
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Only show errors"
    )

    args = parser.parse_args()

    if args.all:
        manifests = find_all_manifests()
        if not manifests:
            print("No manifest files found in sessions/")
            return 1
    elif args.manifest:
        manifests = [Path(args.manifest)]
    else:
        parser.print_help()
        return 1

    all_valid = True
    total_errors = 0
    total_warnings = 0

    for manifest_path in manifests:
        if not args.quiet:
            print(f"\n{'=' * 60}")
            print(f"Validating: {manifest_path.relative_to(PROJECT_ROOT)}")
            print('=' * 60)

        is_valid, errors, warnings = validate_manifest(manifest_path)

        if not is_valid:
            all_valid = False

        total_errors += len(errors)
        total_warnings += len(warnings)

        if errors:
            print("\n❌ ERRORS:")
            for error in errors:
                print(f"  • {error}")

        if warnings and not args.quiet:
            print("\n⚠️  WARNINGS:")
            for warning in warnings:
                print(f"  • {warning}")

        if is_valid and not args.quiet:
            print("\n✅ Manifest is valid")

    # Summary
    if len(manifests) > 1:
        print(f"\n{'=' * 60}")
        print("SUMMARY")
        print('=' * 60)
        print(f"Manifests checked: {len(manifests)}")
        print(f"Total errors: {total_errors}")
        print(f"Total warnings: {total_warnings}")

        if all_valid:
            print("\n✅ All manifests are valid")
        else:
            print("\n❌ Some manifests have errors")

    return 0 if all_valid else 1


if __name__ == "__main__":
    sys.exit(main())
