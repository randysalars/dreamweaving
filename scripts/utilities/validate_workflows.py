#!/usr/bin/env python3
"""
Workflow Validation Script

Validates that workflow documentation is consistent, up-to-date, and follows standards.

Usage:
    python3 scripts/utilities/validate_workflows.py
    python3 scripts/utilities/validate_workflows.py --fix  # Auto-fix some issues
"""

import os
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class WorkflowValidator:
    def __init__(self, auto_fix=False):
        self.auto_fix = auto_fix
        self.errors = []
        self.warnings = []
        self.fixes_applied = []

    def validate_all(self):
        """Run all validation checks"""
        print(f"\n{Colors.BOLD}=== Workflow Documentation Validator ==={Colors.RESET}\n")

        # Check 1: Validate canonical workflow exists
        self.check_canonical_workflow_exists()

        # Check 2: Validate all scripts referenced in docs exist
        self.check_script_references()

        # Check 3: Validate version headers on session docs
        self.check_version_headers()

        # Check 4: Validate deprecated docs have warnings
        self.check_deprecated_warnings()

        # Check 5: Check for duplicate workflow instructions
        self.check_duplicate_workflows()

        # Check 6: Validate file naming conventions
        self.check_file_naming()

        # Check 7: Validate duration consistency
        self.check_duration_consistency()

        # Check 8: Validate command formats
        self.check_command_formats()

        # Print results
        self.print_results()

        # Return exit code
        return 1 if self.errors else 0

    def check_canonical_workflow_exists(self):
        """Ensure CANONICAL_WORKFLOW.md exists and is valid"""
        print(f"{Colors.BLUE}[1/8]{Colors.RESET} Checking canonical workflow...")

        canonical = PROJECT_ROOT / "docs" / "CANONICAL_WORKFLOW.md"
        if not canonical.exists():
            self.errors.append("CRITICAL: docs/CANONICAL_WORKFLOW.md does not exist!")
            return

        content = canonical.read_text()

        # Check for version header
        if "**VERSION:**" not in content:
            self.warnings.append("CANONICAL_WORKFLOW.md missing VERSION header")

        # Check for last updated
        if "**LAST UPDATED:**" not in content:
            self.warnings.append("CANONICAL_WORKFLOW.md missing LAST UPDATED timestamp")

        print(f"  {Colors.GREEN}✓{Colors.RESET} Canonical workflow exists")

    def check_script_references(self):
        """Check that all scripts referenced in docs actually exist"""
        print(f"{Colors.BLUE}[2/8]{Colors.RESET} Checking script references...")

        # Find all markdown files
        docs_to_check = [
            PROJECT_ROOT / "docs" / "CANONICAL_WORKFLOW.md",
            PROJECT_ROOT / "README.md",
            PROJECT_ROOT / "docs" / "QUICK_START.md",
        ]

        # Pattern to find script references
        script_pattern = re.compile(r'`?scripts/[a-zA-Z_/]+\.py`?')

        missing_scripts = []
        for doc in docs_to_check:
            if not doc.exists():
                continue

            content = doc.read_text()
            matches = script_pattern.findall(content)

            for match in matches:
                # Clean up the path
                script_path = match.strip('`')
                full_path = PROJECT_ROOT / script_path

                if not full_path.exists():
                    missing_scripts.append(f"{doc.name} references missing script: {script_path}")

        if missing_scripts:
            for msg in missing_scripts:
                self.errors.append(msg)
        else:
            print(f"  {Colors.GREEN}✓{Colors.RESET} All referenced scripts exist")

    def check_version_headers(self):
        """Validate session-specific docs have version headers"""
        print(f"{Colors.BLUE}[3/8]{Colors.RESET} Checking version headers...")

        # Find all session production docs
        session_docs = []
        for session_dir in (PROJECT_ROOT / "sessions").glob("*/"):
            if session_dir.name.startswith("_"):
                continue

            for doc in session_dir.glob("PRODUCTION*.md"):
                session_docs.append(doc)
            for doc in session_dir.glob("*README*.md"):
                session_docs.append(doc)

        missing_headers = []
        for doc in session_docs:
            content = doc.read_text()

            required_fields = ["**VERSION:**", "**LAST UPDATED:**", "**STATUS:**"]
            missing = [field for field in required_fields if field not in content]

            if missing:
                missing_headers.append(f"{doc.relative_to(PROJECT_ROOT)}: missing {', '.join(missing)}")

        if missing_headers:
            for msg in missing_headers:
                self.warnings.append(msg)
        else:
            print(f"  {Colors.GREEN}✓{Colors.RESET} All session docs have version headers")

    def check_deprecated_warnings(self):
        """Check that deprecated docs have proper warnings"""
        print(f"{Colors.BLUE}[4/8]{Colors.RESET} Checking deprecated doc warnings...")

        deprecated_docs = [
            PROJECT_ROOT / "docs" / "AUDIO_VIDEO_WORKFLOW.md",
            PROJECT_ROOT / "docs" / "VOICE_WORKFLOW.md",
            PROJECT_ROOT / "docs" / "SESSION_AUTOMATION_PLAN.md",
        ]

        missing_warnings = []
        for doc in deprecated_docs:
            if not doc.exists():
                continue

            content = doc.read_text()

            if "⚠️" not in content[:500]:  # Check first 500 chars
                missing_warnings.append(f"{doc.name} missing deprecation warning")

            if "CANONICAL_WORKFLOW.md" not in content[:1000]:  # Check first 1000 chars
                missing_warnings.append(f"{doc.name} missing reference to canonical workflow")

        if missing_warnings:
            for msg in missing_warnings:
                self.warnings.append(msg)
        else:
            print(f"  {Colors.GREEN}✓{Colors.RESET} All deprecated docs have warnings")

    def check_duplicate_workflows(self):
        """Check for duplicate workflow instructions"""
        print(f"{Colors.BLUE}[5/8]{Colors.RESET} Checking for duplicate workflows...")

        # Check for duplicate shell scripts in root vs sessions
        root_scripts = list((PROJECT_ROOT / "").glob("create_*.sh"))

        duplicates = []
        for root_script in root_scripts:
            # Check if it's a deprecation notice or actual script
            content = root_script.read_text()
            if "DEPRECATED" in content[:200]:
                continue  # This is fine - it's a deprecation notice

            # Check if identical script exists in sessions
            for session_dir in (PROJECT_ROOT / "sessions").glob("*/"):
                session_script = session_dir / root_script.name
                if session_script.exists():
                    duplicates.append(f"Duplicate script: {root_script.name} in root and {session_dir.name}/")

        if duplicates:
            for msg in duplicates:
                self.warnings.append(msg)
        else:
            print(f"  {Colors.GREEN}✓{Colors.RESET} No duplicate scripts found")

    def check_file_naming(self):
        """Validate file naming conventions"""
        print(f"{Colors.BLUE}[6/8]{Colors.RESET} Checking file naming conventions...")

        issues = []

        # Check for lowercase MASTERED (should be uppercase)
        for audio_file in PROJECT_ROOT.rglob("*mastered*.wav"):
            if "MASTERED" not in audio_file.name:
                issues.append(f"File should use MASTERED (uppercase): {audio_file.relative_to(PROJECT_ROOT)}")

        # Check for wrong voice file naming
        for voice_file in PROJECT_ROOT.rglob("*voice*.mp3"):
            # Should follow pattern: session_name_voice.mp3
            if voice_file.parent.name == "working_files" and "NATURAL" in voice_file.name.upper():
                # This is actually fine - it's a different naming pattern
                pass

        if issues:
            for msg in issues[:5]:  # Limit to first 5
                self.warnings.append(msg)
            if len(issues) > 5:
                self.warnings.append(f"... and {len(issues) - 5} more naming issues")
        else:
            print(f"  {Colors.GREEN}✓{Colors.RESET} File naming conventions followed")

    def check_duration_consistency(self):
        """Check that duration specifications are consistent"""
        print(f"{Colors.BLUE}[7/8]{Colors.RESET} Checking duration consistency...")

        # Extract durations from session docs
        duration_specs = {}

        for session_dir in (PROJECT_ROOT / "sessions").glob("*/"):
            if session_dir.name.startswith("_"):
                continue

            session_name = session_dir.name
            durations = set()

            # Check all markdown files in session
            for md_file in session_dir.glob("*.md"):
                content = md_file.read_text()

                # Look for duration patterns
                # Pattern 1: XX:XX (XXXX seconds)
                matches = re.findall(r'(\d+):(\d+)\s*\((\d+)\s*seconds?\)', content)
                for match in matches:
                    minutes = int(match[0])
                    seconds = int(match[1])
                    stated_total = int(match[2])
                    calculated_total = minutes * 60 + seconds

                    if calculated_total != stated_total:
                        self.errors.append(
                            f"{session_name}/{md_file.name}: Duration mismatch - "
                            f"{match[0]}:{match[1]} is {calculated_total}s not {stated_total}s"
                        )

                    durations.add(calculated_total)

            # Check if multiple different durations specified
            if len(durations) > 1:
                self.warnings.append(
                    f"{session_name}: Multiple different durations specified: {sorted(durations)}"
                )

            duration_specs[session_name] = durations

        if not any(duration_specs.values()):
            print(f"  {Colors.YELLOW}!{Colors.RESET} No duration specifications found to validate")
        elif not self.errors and len([d for d in duration_specs.values() if len(d) > 1]) == 0:
            print(f"  {Colors.GREEN}✓{Colors.RESET} Duration specifications consistent")

    def check_command_formats(self):
        """Validate command format standards"""
        print(f"{Colors.BLUE}[8/8]{Colors.RESET} Checking command formats...")

        issues = []

        # Check key documentation files
        docs_to_check = [
            PROJECT_ROOT / "README.md",
            PROJECT_ROOT / "docs" / "CANONICAL_WORKFLOW.md",
            PROJECT_ROOT / "docs" / "QUICK_START.md",
        ]

        for doc in docs_to_check:
            if not doc.exists():
                continue

            content = doc.read_text()

            # Check for python instead of python3
            if re.search(r'```bash.*?\bpython\s+(?!3)', content, re.DOTALL):
                issues.append(f"{doc.name}: Uses 'python' instead of 'python3' in bash blocks")

            # Check for generate_audio_chunked.py without voice parameter in examples
            pattern = r'generate_audio_chunked\.py\s+[^\s]+\s+[^\s]+\s*$'
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                if 'en-US-' not in content[match.start():match.end()+100]:
                    issues.append(f"{doc.name}: generate_audio_chunked.py missing voice parameter")
                    break

        if issues:
            for msg in issues:
                self.warnings.append(msg)
        else:
            print(f"  {Colors.GREEN}✓{Colors.RESET} Command formats follow standards")

    def print_results(self):
        """Print validation results"""
        print(f"\n{Colors.BOLD}=== Validation Results ==={Colors.RESET}\n")

        if self.fixes_applied:
            print(f"{Colors.GREEN}Fixes Applied:{Colors.RESET}")
            for fix in self.fixes_applied:
                print(f"  {Colors.GREEN}✓{Colors.RESET} {fix}")
            print()

        if self.warnings:
            print(f"{Colors.YELLOW}Warnings ({len(self.warnings)}):{Colors.RESET}")
            for warning in self.warnings:
                print(f"  {Colors.YELLOW}⚠{Colors.RESET}  {warning}")
            print()

        if self.errors:
            print(f"{Colors.RED}Errors ({len(self.errors)}):{Colors.RESET}")
            for error in self.errors:
                print(f"  {Colors.RED}✗{Colors.RESET} {error}")
            print()

        # Summary
        total_issues = len(self.errors) + len(self.warnings)
        if total_issues == 0:
            print(f"{Colors.GREEN}{Colors.BOLD}✓ All validation checks passed!{Colors.RESET}\n")
        else:
            print(f"{Colors.YELLOW}Total issues: {total_issues} ({len(self.errors)} errors, {len(self.warnings)} warnings){Colors.RESET}\n")

            if self.errors:
                print(f"{Colors.RED}Please fix errors before committing workflow changes.{Colors.RESET}\n")

def main():
    """Main entry point"""
    auto_fix = "--fix" in sys.argv

    validator = WorkflowValidator(auto_fix=auto_fix)
    exit_code = validator.validate_all()

    sys.exit(exit_code)

if __name__ == "__main__":
    main()
