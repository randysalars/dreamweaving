#!/usr/bin/env python3
"""
Knowledge Base Query Tool
=========================
Query the knowledge base by outcome, domain, or entry ID.
Designed for use by AI agents and in scripts.

Usage:
    # Query by outcome
    python scripts/utilities/query_knowledge.py --outcome abundance

    # Query by domain
    python scripts/utilities/query_knowledge.py --domain psychology

    # Get specific entry
    python scripts/utilities/query_knowledge.py --entry psychology.abundance_mindset.scarcity_deprogramming

    # Get entries for a session
    python scripts/utilities/query_knowledge.py --for-session sessions/my-session/manifest.yaml

    # Output as JSON
    python scripts/utilities/query_knowledge.py --outcome healing --json
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import yaml


class KnowledgeQuery:
    """Query and retrieve knowledge base entries."""

    def __init__(self, knowledge_dir: str = "knowledge"):
        self.knowledge_dir = Path(knowledge_dir)
        self.outcome_index: dict = {}
        self.domain_index: dict = {}
        self.outcome_registry: dict = {}
        self._load_indexes()

    def _load_yaml(self, path: Path) -> dict | None:
        """Load a YAML file."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Warning: Could not load {path}: {e}", file=sys.stderr)
            return None

    def _load_indexes(self):
        """Load all index files."""
        # Load outcome index
        outcome_path = self.knowledge_dir / "indexes" / "outcome_index.yaml"
        data = self._load_yaml(outcome_path)
        if data:
            self.outcome_index = data.get("outcomes", {})

        # Load domain index
        domain_path = self.knowledge_dir / "indexes" / "domain_index.yaml"
        data = self._load_yaml(domain_path)
        if data:
            self.domain_index = data.get("domains", {})

        # Load outcome registry
        registry_path = self.knowledge_dir / "outcome_registry.yaml"
        data = self._load_yaml(registry_path)
        if data:
            self.outcome_registry = data.get("outcomes", {})

    def get_outcome_info(self, outcome: str) -> dict:
        """Get complete information for an outcome."""
        result = {
            "outcome": outcome,
            "found": False,
            "index_info": None,
            "registry_info": None,
            "domains": [],
            "key_entries": [],
            "patterns": {},
            "archetypes": [],
            "journey_families": [],
            "objects": []
        }

        # Get from outcome index
        if outcome in self.outcome_index:
            result["found"] = True
            idx = self.outcome_index[outcome]
            result["index_info"] = {
                "description": idx.get("description"),
                "primary_domains": idx.get("primary_domains", []),
                "secondary_domains": idx.get("secondary_domains", []),
                "tertiary_domains": idx.get("tertiary_domains", []),
                "key_entries": idx.get("key_entries", []),
                "element_emphasis": idx.get("element_emphasis"),
                "chakra_emphasis": idx.get("chakra_emphasis"),
                "brainwave_target": idx.get("brainwave_target")
            }
            result["domains"] = (
                idx.get("primary_domains", []) +
                idx.get("secondary_domains", [])
            )
            result["key_entries"] = idx.get("key_entries", [])

        # Get from outcome registry
        if outcome in self.outcome_registry:
            result["found"] = True
            reg = self.outcome_registry[outcome]
            result["registry_info"] = {
                "description": reg.get("description"),
                "subcategories": reg.get("subcategories", []),
                "required_patterns": reg.get("required_patterns", {}),
                "suggested_patterns": reg.get("suggested_patterns", []),
                "advanced_patterns": reg.get("advanced_patterns", {}),
                "success_metrics": reg.get("success_metrics", {}),
                "brainwave_arc": reg.get("brainwave_arc", {})
            }
            result["patterns"] = {
                "required": reg.get("required_patterns", {}),
                "suggested": reg.get("suggested_patterns", []),
                "advanced": reg.get("advanced_patterns", {})
            }
            result["archetypes"] = (
                reg.get("suggested_archetypes", {}).get("primary", []) +
                reg.get("suggested_archetypes", {}).get("secondary", [])
            )
            result["journey_families"] = (
                reg.get("suggested_journey_families", {}).get("primary", []) +
                reg.get("suggested_journey_families", {}).get("secondary", [])
            )
            result["objects"] = (
                reg.get("suggested_objects", {}).get("primary", []) +
                reg.get("suggested_objects", {}).get("secondary", [])
            )

        return result

    def get_domain_info(self, domain: str) -> dict:
        """Get information about a domain and its files."""
        result = {
            "domain": domain,
            "found": False,
            "description": None,
            "status": None,
            "files": [],
            "active_files": [],
            "entries": []
        }

        if domain in self.domain_index:
            result["found"] = True
            dom = self.domain_index[domain]
            result["description"] = dom.get("description")
            result["status"] = dom.get("status")

            files = dom.get("files", {})
            for file_key, file_info in files.items():
                file_data = {
                    "key": file_key,
                    "path": file_info.get("path"),
                    "status": file_info.get("status"),
                    "entries": file_info.get("entries", [])
                }
                result["files"].append(file_data)
                if file_info.get("status") == "active":
                    result["active_files"].append(file_data)
                result["entries"].extend(file_info.get("entries", []))

        return result

    def get_entry(self, entry_id: str) -> dict:
        """Attempt to retrieve a specific entry by ID."""
        result = {
            "entry_id": entry_id,
            "found": False,
            "file_path": None,
            "entry_data": None
        }

        # Parse entry_id to find domain
        parts = entry_id.split(".")
        if len(parts) < 2:
            return result

        domain = parts[0]
        if domain not in self.domain_index:
            return result

        # Search through domain files
        dom = self.domain_index[domain]
        for file_key, file_info in dom.get("files", {}).items():
            file_path = self.knowledge_dir / file_info.get("path", "")
            if not file_path.exists():
                continue

            data = self._load_yaml(file_path)
            if not data:
                continue

            # Search for the entry
            entry = self._find_entry_in_data(data, entry_id)
            if entry:
                result["found"] = True
                result["file_path"] = str(file_path)
                result["entry_data"] = entry
                return result

        return result

    def _find_entry_in_data(self, data: dict, entry_id: str) -> dict | None:
        """Recursively search for an entry by ID."""
        metadata_keys = {"version", "created", "purpose", "last_updated", "description",
                        "metadata", "usage_guidelines", "cross_references", "notes"}

        for key, value in data.items():
            if key in metadata_keys:
                continue
            if isinstance(value, dict):
                if value.get("entry_id") == entry_id:
                    return value
                # Check if key matches the last part of entry_id
                if entry_id.endswith(f".{key}") or entry_id == key:
                    return value
                # Recurse
                found = self._find_entry_in_data(value, entry_id)
                if found:
                    return found
        return None

    def get_entries_for_session(self, manifest_path: str) -> dict:
        """Get relevant knowledge entries based on a session manifest."""
        result = {
            "manifest_path": manifest_path,
            "outcome": None,
            "outcome_info": None,
            "recommended_entries": [],
            "patterns": {},
            "archetypes": [],
            "objects": []
        }

        manifest = self._load_yaml(Path(manifest_path))
        if not manifest:
            return result

        # Get outcome from manifest
        session = manifest.get("session", {})
        outcome = session.get("desired_outcome")

        if not outcome:
            return result

        result["outcome"] = outcome
        result["outcome_info"] = self.get_outcome_info(outcome)

        if result["outcome_info"]["found"]:
            result["patterns"] = result["outcome_info"]["patterns"]
            result["archetypes"] = result["outcome_info"]["archetypes"]
            result["objects"] = result["outcome_info"]["objects"]

            # Get key entries
            for entry_id in result["outcome_info"]["key_entries"]:
                entry = self.get_entry(entry_id)
                if entry["found"]:
                    result["recommended_entries"].append({
                        "entry_id": entry_id,
                        "data": entry["entry_data"]
                    })

        return result

    def list_outcomes(self) -> list:
        """List all available outcomes."""
        outcomes = set(self.outcome_index.keys()) | set(self.outcome_registry.keys())
        return sorted(list(outcomes))

    def list_domains(self) -> list:
        """List all available domains."""
        return sorted(list(self.domain_index.keys()))


def main():
    parser = argparse.ArgumentParser(description="Query the knowledge base")
    parser.add_argument("--outcome", "-o", help="Query by outcome name")
    parser.add_argument("--domain", "-d", help="Query by domain name")
    parser.add_argument("--entry", "-e", help="Get specific entry by ID")
    parser.add_argument("--for-session", "-s", help="Get entries for a session manifest")
    parser.add_argument("--list-outcomes", action="store_true", help="List all outcomes")
    parser.add_argument("--list-domains", action="store_true", help="List all domains")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--knowledge-dir", default="knowledge", help="Knowledge directory")
    args = parser.parse_args()

    # Find project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    knowledge_dir = project_root / args.knowledge_dir

    if not knowledge_dir.exists():
        print(f"Error: Knowledge directory not found: {knowledge_dir}")
        sys.exit(1)

    query = KnowledgeQuery(str(knowledge_dir))

    result = None

    if args.list_outcomes:
        result = {"outcomes": query.list_outcomes()}
    elif args.list_domains:
        result = {"domains": query.list_domains()}
    elif args.outcome:
        result = query.get_outcome_info(args.outcome)
    elif args.domain:
        result = query.get_domain_info(args.domain)
    elif args.entry:
        result = query.get_entry(args.entry)
    elif args.for_session:
        manifest_path = project_root / args.for_session
        result = query.get_entries_for_session(str(manifest_path))
    else:
        parser.print_help()
        sys.exit(1)

    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        _pretty_print(result)


def _pretty_print(data: dict, indent: int = 0):
    """Pretty print a dictionary."""
    prefix = "  " * indent
    for key, value in data.items():
        if isinstance(value, dict):
            print(f"{prefix}{key}:")
            _pretty_print(value, indent + 1)
        elif isinstance(value, list):
            if value and isinstance(value[0], dict):
                print(f"{prefix}{key}:")
                for item in value:
                    _pretty_print(item, indent + 1)
                    print()
            else:
                print(f"{prefix}{key}: {value}")
        else:
            print(f"{prefix}{key}: {value}")


if __name__ == "__main__":
    main()
