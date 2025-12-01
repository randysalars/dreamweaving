#!/usr/bin/env python3
"""
Update Workflow Version

Updates version information for workflow documentation.

Usage:
    python3 scripts/utilities/update_workflow_version.py <workflow_id> <new_version> [--reason "reason"]

Examples:
    python3 scripts/utilities/update_workflow_version.py canonical_workflow 1.1 --reason "Added new voice options"
    python3 scripts/utilities/update_workflow_version.py neural_network_navigator_manual_v2 2.1
"""

import sys
import re
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent

# Workflow ID to file mapping
WORKFLOW_FILES = {
    "canonical_workflow": "docs/CANONICAL_WORKFLOW.md",
    "quick_start": "docs/QUICK_START.md",
    "workflow_decision_tree": "docs/WORKFLOW_DECISION_TREE.md",
    "terminology_guide": "docs/TERMINOLOGY_GUIDE.md",
    "workflow_maintenance_guide": "docs/WORKFLOW_MAINTENANCE_GUIDE.md",
    "neural_network_navigator_workflow": "sessions/neural-network-navigator/PRODUCTION_WORKFLOW.md",
    "neural_network_navigator_manual_v1": "sessions/neural-network-navigator/PRODUCTION_MANUAL.md",
    "neural_network_navigator_manual_v2": "sessions/neural-network-navigator/PRODUCTION_MANUAL_V2.md",
    "garden_of_eden_manual": "sessions/garden-of-eden/PRODUCTION_MANUAL.md",
    "garden_of_eden_audio_readme": "sessions/garden-of-eden/AUDIO_PRODUCTION_README.md",
}

def update_version_in_file(file_path: Path, new_version: str) -> bool:
    """Update version number in a workflow file"""
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        return False

    content = file_path.read_text()
    today = datetime.now().strftime("%Y-%m-%d")

    # Update VERSION line
    content = re.sub(
        r'\*\*VERSION:\*\* [\d.]+',
        f'**VERSION:** {new_version}',
        content
    )

    # Update LAST UPDATED line
    content = re.sub(
        r'\*\*LAST UPDATED:\*\* \d{4}-\d{2}-\d{2}',
        f'**LAST UPDATED:** {today}',
        content
    )

    file_path.write_text(content)
    return True

def update_version_registry(workflow_id: str, new_version: str, status: str = "CURRENT") -> bool:
    """Update .workflow-versions registry"""
    registry_file = PROJECT_ROOT / ".workflow-versions"

    if not registry_file.exists():
        print(f"Error: Registry file not found: {registry_file}")
        return False

    content = registry_file.read_text()
    today = datetime.now().strftime("%Y-%m-%d")

    # Update or add the entry
    pattern = f"^{workflow_id}=.*$"
    replacement = f"{workflow_id}={new_version}:{today}:{status}"

    if re.search(pattern, content, re.MULTILINE):
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    else:
        # Add new entry
        content += f"\n{replacement}\n"

    registry_file.write_text(content)
    return True

def add_version_history_entry(file_path: Path, version: str, reason: str = None):
    """Add entry to version history section if it exists"""
    if not file_path.exists():
        return

    content = file_path.read_text()
    today = datetime.now().strftime("%Y-%m-%d")

    # Look for version history section
    if "## Version History" not in content:
        return

    # Create entry
    entry = f"\n### Version {version} ({today})\n"
    if reason:
        entry += f"- 🔧 Changed: {reason}\n"
    else:
        entry += "- 🔧 Changed: Version updated\n"

    # Find where to insert (after "## Version History")
    pattern = r'(## Version History\s*\n)'
    replacement = r'\1' + entry

    content = re.sub(pattern, replacement, content)
    file_path.write_text(content)

def main():
    if len(sys.argv) < 3:
        print("Usage: update_workflow_version.py <workflow_id> <new_version> [--reason \"reason\"]")
        print("\nAvailable workflow IDs:")
        for wf_id in WORKFLOW_FILES.keys():
            print(f"  - {wf_id}")
        sys.exit(1)

    workflow_id = sys.argv[1]
    new_version = sys.argv[2]

    # Extract reason if provided
    reason = None
    if "--reason" in sys.argv:
        reason_idx = sys.argv.index("--reason")
        if reason_idx + 1 < len(sys.argv):
            reason = sys.argv[reason_idx + 1]

    # Validate workflow ID
    if workflow_id not in WORKFLOW_FILES:
        print(f"Error: Unknown workflow ID: {workflow_id}")
        print("\nAvailable workflow IDs:")
        for wf_id in WORKFLOW_FILES.keys():
            print(f"  - {wf_id}")
        sys.exit(1)

    # Get file path
    file_path = PROJECT_ROOT / WORKFLOW_FILES[workflow_id]

    print(f"Updating {workflow_id} to version {new_version}...")

    # Update file
    if update_version_in_file(file_path, new_version):
        print(f"  ✓ Updated {file_path.relative_to(PROJECT_ROOT)}")

        # Add version history entry
        if reason:
            add_version_history_entry(file_path, new_version, reason)
            print(f"  ✓ Added version history entry")

        # Update registry
        if update_version_registry(workflow_id, new_version):
            print(f"  ✓ Updated version registry")

        print(f"\n✓ Version update complete!")
        print(f"\nNext steps:")
        print(f"  1. Review changes in {file_path.relative_to(PROJECT_ROOT)}")
        print(f"  2. Run: python3 scripts/utilities/validate_workflows.py")
        print(f"  3. Commit changes with message: 'Update {workflow_id} to v{new_version}'")
    else:
        print("✗ Version update failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
