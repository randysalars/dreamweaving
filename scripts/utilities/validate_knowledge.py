#!/usr/bin/env python3
"""
Knowledge Base Validation Script
================================
Validates knowledge base entries against schema.yaml standards.
Checks for:
- Required fields
- Entry ID format
- Cross-reference validity
- SSML template compliance
- Index registration

Usage:
    python scripts/utilities/validate_knowledge.py                    # Validate all
    python scripts/utilities/validate_knowledge.py --file FILE        # Validate single file
    python scripts/utilities/validate_knowledge.py --check-refs       # Validate cross-references
    python scripts/utilities/validate_knowledge.py --check-index      # Check index registration
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Any

import yaml


class KnowledgeValidator:
    """Validates knowledge base entries against schema standards."""

    def __init__(self, knowledge_dir: str = "knowledge"):
        self.knowledge_dir = Path(knowledge_dir)
        self.errors: list[dict] = []
        self.warnings: list[dict] = []
        self.all_entry_ids: set[str] = set()
        self.index_entries: dict[str, list[str]] = {}

        # Valid enum values from schema
        self.valid_domains = [
            "traditions", "dream_work", "consciousness_maps", "psychology",
            "ritual", "mythology", "symbols", "audio", "embodiment", "science"
        ]
        self.valid_journey_phases = [
            "pre_talk", "induction", "deepening", "journey",
            "helm_deep_trance", "integration", "reorientation"
        ]
        self.valid_outcomes = [
            "healing", "transformation", "empowerment", "self_knowledge",
            "release", "spiritual_growth", "creativity", "relaxation",
            "focus", "confidence", "abundance", "manifestation",
            "faith", "intuition", "cognitive_enhancement"
        ]
        self.valid_elements = ["fire", "water", "air", "earth", "spirit", "void"]
        self.valid_brainwaves = ["gamma", "beta", "alpha", "theta", "delta"]

    def add_error(self, file: str, entry: str, message: str):
        """Add an error to the list."""
        self.errors.append({
            "file": file,
            "entry": entry,
            "message": message,
            "severity": "ERROR"
        })

    def add_warning(self, file: str, entry: str, message: str):
        """Add a warning to the list."""
        self.warnings.append({
            "file": file,
            "entry": entry,
            "message": message,
            "severity": "WARNING"
        })

    def load_yaml_file(self, path: Path) -> dict | None:
        """Load and parse a YAML file."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            self.add_error(str(path), "FILE", f"YAML parse error: {e}")
            return None
        except FileNotFoundError:
            self.add_error(str(path), "FILE", "File not found")
            return None

    def load_domain_index(self):
        """Load the domain index to check registration."""
        index_path = self.knowledge_dir / "indexes" / "domain_index.yaml"
        data = self.load_yaml_file(index_path)
        if data and "domains" in data:
            for domain_name, domain_data in data["domains"].items():
                if "files" in domain_data:
                    for file_key, file_data in domain_data["files"].items():
                        if "entries" in file_data:
                            path = file_data.get("path", "")
                            self.index_entries[path] = file_data["entries"]

    def validate_entry_id(self, entry_id: str, file: str) -> bool:
        """Validate entry_id format: domain.category.name"""
        pattern = r"^[a-z_]+\.[a-z_]+\.[a-z_0-9]+$"
        if not re.match(pattern, entry_id):
            self.add_error(file, entry_id,
                f"Invalid entry_id format. Expected 'domain.category.name', got '{entry_id}'")
            return False
        return True

    def validate_ssml_template(self, ssml: str, file: str, entry: str):
        """Validate SSML template follows guidelines."""
        if not ssml:
            return

        # Check for rate="1.0" (required)
        if 'rate="1.0"' not in ssml and "rate='1.0'" not in ssml:
            # Check for slow rates (which are prohibited)
            slow_rate_pattern = r'rate=["\']0\.\d+["\']'
            if re.search(slow_rate_pattern, ssml):
                self.add_error(file, entry,
                    "SSML uses slow rate (< 1.0). Must use rate='1.0' with breaks for pacing.")
            else:
                self.add_warning(file, entry,
                    "SSML template should explicitly include rate='1.0'")

        # Check for proper prosody tag
        if "<prosody" not in ssml:
            self.add_warning(file, entry,
                "SSML template missing <prosody> tag")

        # Check for break tags (good practice)
        if "<break" not in ssml:
            self.add_warning(file, entry,
                "SSML template has no <break> tags. Consider adding for pacing.")

    def validate_entry(self, entry: dict, file: str, entry_key: str):
        """Validate a single knowledge entry against the schema."""
        # Check for entry_id
        entry_id = entry.get("entry_id", entry_key)

        if entry_id:
            self.all_entry_ids.add(entry_id)
            self.validate_entry_id(entry_id, file)

        # Required fields
        required_fields = [
            ("name", "Entry missing 'name' field"),
            ("domain", "Entry missing 'domain' field"),
        ]

        for field, msg in required_fields:
            if field not in entry:
                self.add_error(file, entry_id or entry_key, msg)

        # Validate domain enum
        if "domain" in entry:
            domain = entry["domain"]
            if domain not in self.valid_domains:
                self.add_error(file, entry_id or entry_key,
                    f"Invalid domain '{domain}'. Must be one of: {self.valid_domains}")

        # Validate definition section
        definition = entry.get("definition", {})
        if isinstance(definition, dict):
            if "brief" not in definition:
                self.add_warning(file, entry_id or entry_key,
                    "Missing definition.brief")
        elif isinstance(definition, str):
            # Some entries have definition as a string
            pass
        else:
            self.add_warning(file, entry_id or entry_key,
                "Missing 'definition' section")

        # Validate applications section
        applications = entry.get("applications", {})
        if isinstance(applications, dict):
            # Check journey_phases
            phases = applications.get("journey_phases", [])
            if phases:
                for phase in phases:
                    if phase not in self.valid_journey_phases:
                        self.add_warning(file, entry_id or entry_key,
                            f"Unknown journey phase '{phase}'")

            # Check outcome_alignment
            outcomes = applications.get("outcome_alignment", [])
            if outcomes:
                for outcome in outcomes:
                    if outcome not in self.valid_outcomes:
                        self.add_warning(file, entry_id or entry_key,
                            f"Unknown outcome '{outcome}'")

        # Validate attributes section
        attributes = entry.get("attributes", {})
        if isinstance(attributes, dict):
            if "element" in attributes:
                element = attributes["element"]
                if isinstance(element, str) and element not in self.valid_elements:
                    self.add_warning(file, entry_id or entry_key,
                        f"Unknown element '{element}'")

            if "brainwave" in attributes:
                brainwave = attributes["brainwave"]
                if isinstance(brainwave, str) and brainwave not in self.valid_brainwaves:
                    self.add_warning(file, entry_id or entry_key,
                        f"Unknown brainwave '{brainwave}'")

        # Validate templates section
        templates = entry.get("templates", {})
        if isinstance(templates, dict):
            ssml = templates.get("ssml_snippet", "")
            if ssml:
                self.validate_ssml_template(ssml, file, entry_id or entry_key)

    def validate_cross_references(self, entry: dict, file: str, entry_key: str):
        """Validate that cross-references point to existing entries."""
        entry_id = entry.get("entry_id", entry_key)
        relationships = entry.get("relationships", {})

        if not isinstance(relationships, dict):
            return

        ref_fields = ["synergies", "opposites", "prerequisites", "progressions"]

        for field in ref_fields:
            refs = relationships.get(field, [])
            if not isinstance(refs, list):
                continue
            for ref in refs:
                if isinstance(ref, str) and ref not in self.all_entry_ids:
                    self.add_warning(file, entry_id or entry_key,
                        f"Cross-reference '{ref}' in {field} not found in knowledge base")

    def validate_file(self, file_path: Path) -> bool:
        """Validate all entries in a knowledge file."""
        data = self.load_yaml_file(file_path)
        if not data:
            return False

        rel_path = str(file_path.relative_to(self.knowledge_dir))

        # Find entry sections (skip metadata like version, purpose, etc.)
        metadata_keys = {"version", "created", "purpose", "last_updated", "description",
                        "metadata", "usage_guidelines", "cross_references", "notes"}

        for key, value in data.items():
            if key in metadata_keys:
                continue

            if isinstance(value, dict):
                # Check if this is a section containing multiple entries
                # or a single entry itself
                if "entry_id" in value or "name" in value or "definition" in value:
                    # Single entry
                    self.validate_entry(value, rel_path, key)
                else:
                    # Section with multiple entries
                    for entry_key, entry_value in value.items():
                        if isinstance(entry_value, dict):
                            self.validate_entry(entry_value, rel_path, entry_key)

        return len([e for e in self.errors if e["file"] == rel_path]) == 0

    def check_index_registration(self):
        """Check if knowledge files are registered in the domain index."""
        # Get all YAML files in knowledge subdirectories
        knowledge_files = []
        for domain_dir in self.knowledge_dir.iterdir():
            if domain_dir.is_dir() and domain_dir.name not in ["indexes"]:
                for yaml_file in domain_dir.glob("*.yaml"):
                    rel_path = f"{domain_dir.name}/{yaml_file.name}"
                    knowledge_files.append(rel_path)

        # Check against index
        registered_paths = set(self.index_entries.keys())

        for file_path in knowledge_files:
            if file_path not in registered_paths:
                self.add_warning("domain_index.yaml", file_path,
                    f"File '{file_path}' not registered in domain_index.yaml")

    def validate_all(self, check_refs: bool = True, check_index: bool = True):
        """Validate all knowledge files."""
        print("Loading domain index...")
        self.load_domain_index()

        print("Scanning knowledge files...")
        # First pass: collect all entry_ids
        for domain_dir in self.knowledge_dir.iterdir():
            if domain_dir.is_dir() and domain_dir.name not in ["indexes"]:
                for yaml_file in domain_dir.glob("*.yaml"):
                    data = self.load_yaml_file(yaml_file)
                    if data:
                        self._collect_entry_ids(data)

        # Second pass: validate entries
        print("Validating entries...")
        for domain_dir in self.knowledge_dir.iterdir():
            if domain_dir.is_dir() and domain_dir.name not in ["indexes"]:
                for yaml_file in domain_dir.glob("*.yaml"):
                    print(f"  Checking {yaml_file.relative_to(self.knowledge_dir)}...")
                    self.validate_file(yaml_file)

        # Third pass: validate cross-references
        if check_refs:
            print("Checking cross-references...")
            for domain_dir in self.knowledge_dir.iterdir():
                if domain_dir.is_dir() and domain_dir.name not in ["indexes"]:
                    for yaml_file in domain_dir.glob("*.yaml"):
                        data = self.load_yaml_file(yaml_file)
                        if data:
                            self._validate_cross_refs(data, yaml_file)

        # Check index registration
        if check_index:
            print("Checking index registration...")
            self.check_index_registration()

    def _collect_entry_ids(self, data: dict):
        """Collect all entry_ids from a data structure."""
        metadata_keys = {"version", "created", "purpose", "last_updated", "description",
                        "metadata", "usage_guidelines", "cross_references", "notes"}

        for key, value in data.items():
            if key in metadata_keys:
                continue
            if isinstance(value, dict):
                if "entry_id" in value:
                    self.all_entry_ids.add(value["entry_id"])
                else:
                    self._collect_entry_ids(value)

    def _validate_cross_refs(self, data: dict, file_path: Path):
        """Validate cross-references in a data structure."""
        rel_path = str(file_path.relative_to(self.knowledge_dir))
        metadata_keys = {"version", "created", "purpose", "last_updated", "description",
                        "metadata", "usage_guidelines", "cross_references", "notes"}

        for key, value in data.items():
            if key in metadata_keys:
                continue
            if isinstance(value, dict):
                if "entry_id" in value or "relationships" in value:
                    self.validate_cross_references(value, rel_path, key)
                else:
                    for entry_key, entry_value in value.items():
                        if isinstance(entry_value, dict):
                            self.validate_cross_references(entry_value, rel_path, entry_key)

    def print_report(self):
        """Print validation report."""
        print("\n" + "=" * 70)
        print("KNOWLEDGE BASE VALIDATION REPORT")
        print("=" * 70)

        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            print("-" * 50)
            for err in self.errors:
                print(f"  [{err['file']}] {err['entry']}")
                print(f"    → {err['message']}")
        else:
            print("\n✅ No errors found!")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            print("-" * 50)
            for warn in self.warnings:
                print(f"  [{warn['file']}] {warn['entry']}")
                print(f"    → {warn['message']}")
        else:
            print("\n✅ No warnings!")

        print("\n" + "=" * 70)
        print(f"SUMMARY: {len(self.errors)} errors, {len(self.warnings)} warnings")
        print(f"Entry IDs found: {len(self.all_entry_ids)}")
        print("=" * 70)

        return len(self.errors) == 0


def main():
    parser = argparse.ArgumentParser(description="Validate knowledge base entries")
    parser.add_argument("--file", "-f", help="Validate single file")
    parser.add_argument("--check-refs", action="store_true", default=True,
                       help="Check cross-references (default: on)")
    parser.add_argument("--no-check-refs", action="store_true",
                       help="Skip cross-reference checking")
    parser.add_argument("--check-index", action="store_true", default=True,
                       help="Check index registration (default: on)")
    parser.add_argument("--no-check-index", action="store_true",
                       help="Skip index registration checking")
    parser.add_argument("--knowledge-dir", "-d", default="knowledge",
                       help="Knowledge base directory")
    args = parser.parse_args()

    # Find project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    knowledge_dir = project_root / args.knowledge_dir

    if not knowledge_dir.exists():
        print(f"Error: Knowledge directory not found: {knowledge_dir}")
        sys.exit(1)

    validator = KnowledgeValidator(str(knowledge_dir))

    if args.file:
        file_path = knowledge_dir / args.file
        if not file_path.exists():
            print(f"Error: File not found: {file_path}")
            sys.exit(1)
        validator.validate_file(file_path)
    else:
        check_refs = not args.no_check_refs
        check_index = not args.no_check_index
        validator.validate_all(check_refs=check_refs, check_index=check_index)

    success = validator.print_report()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
