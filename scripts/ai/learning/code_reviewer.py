#!/usr/bin/env python3
"""
Code Reviewer for Dreamweaving Self-Learning System

Reviews project code for:
- Common issues and anti-patterns
- Improvement opportunities
- Best practices adherence
- Technical debt

Stores improvements in knowledge base for future reference.

Usage:
    python3 scripts/ai/learning/code_reviewer.py
    python3 scripts/ai/learning/code_reviewer.py --path scripts/core/
    python3 scripts/ai/learning/code_reviewer.py --fix-common
"""

import os
import sys
import ast
import yaml
import argparse
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Set
from collections import defaultdict


class CodeIssue:
    """Represents a code issue found during review."""

    def __init__(
        self,
        file_path: str,
        line_number: int,
        issue_type: str,
        description: str,
        severity: str = "info",
        suggestion: str = "",
    ):
        self.file_path = file_path
        self.line_number = line_number
        self.issue_type = issue_type
        self.description = description
        self.severity = severity  # info, warning, error
        self.suggestion = suggestion

    def to_dict(self) -> Dict:
        return {
            "file": self.file_path,
            "line": self.line_number,
            "type": self.issue_type,
            "description": self.description,
            "severity": self.severity,
            "suggestion": self.suggestion,
        }


class CodeReviewer:
    """Reviews Python code for common issues."""

    def __init__(self):
        self.issues: List[CodeIssue] = []
        self.stats = defaultdict(int)

    def review_file(self, file_path: Path) -> List[CodeIssue]:
        """Review a single Python file."""
        issues = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception as e:
            return [CodeIssue(
                str(file_path), 0, "read_error",
                f"Could not read file: {e}", "error"
            )]

        # Line-by-line checks
        for i, line in enumerate(lines, 1):
            issues.extend(self._check_line(str(file_path), i, line))

        # AST-based checks
        try:
            tree = ast.parse(content)
            issues.extend(self._check_ast(str(file_path), tree))
        except SyntaxError as e:
            issues.append(CodeIssue(
                str(file_path), e.lineno or 0, "syntax_error",
                f"Syntax error: {e.msg}", "error"
            ))

        # Content-level checks
        issues.extend(self._check_content(str(file_path), content))

        return issues

    def _check_line(self, file_path: str, line_num: int, line: str) -> List[CodeIssue]:
        """Check a single line for issues."""
        issues = []

        # Check line length
        if len(line) > 120:
            issues.append(CodeIssue(
                file_path, line_num, "line_length",
                f"Line too long ({len(line)} chars)", "info",
                "Consider breaking into multiple lines"
            ))

        # Check for print statements (should use logging in production)
        if re.match(r'^\s*print\s*\(', line) and 'debug' not in file_path.lower():
            issues.append(CodeIssue(
                file_path, line_num, "print_statement",
                "Using print() instead of logging", "info",
                "Consider using logging module for production code"
            ))

        # Check for TODO/FIXME comments
        if re.search(r'#\s*(TODO|FIXME|XXX|HACK)', line, re.IGNORECASE):
            match = re.search(r'#\s*(TODO|FIXME|XXX|HACK):?\s*(.+)?', line, re.IGNORECASE)
            if match:
                issues.append(CodeIssue(
                    file_path, line_num, "todo_comment",
                    f"{match.group(1)}: {match.group(2) or 'No description'}",
                    "info"
                ))

        # Check for hardcoded paths
        if re.search(r'["\']\/home\/|["\']\/Users\/', line):
            issues.append(CodeIssue(
                file_path, line_num, "hardcoded_path",
                "Hardcoded absolute path detected", "warning",
                "Use Path.home() or configuration for paths"
            ))

        # Check for bare except
        if re.match(r'\s*except\s*:', line):
            issues.append(CodeIssue(
                file_path, line_num, "bare_except",
                "Bare except clause catches all exceptions", "warning",
                "Specify exception type: except Exception:"
            ))

        # Check for subprocess shell=True
        if 'shell=True' in line and 'subprocess' in line:
            issues.append(CodeIssue(
                file_path, line_num, "shell_injection",
                "subprocess with shell=True is a security risk", "warning",
                "Use shell=False and pass args as list"
            ))

        return issues

    def _check_ast(self, file_path: str, tree: ast.AST) -> List[CodeIssue]:
        """Check AST for structural issues."""
        issues = []

        for node in ast.walk(tree):
            # Check function complexity (too many arguments)
            if isinstance(node, ast.FunctionDef):
                if len(node.args.args) > 7:
                    issues.append(CodeIssue(
                        file_path, node.lineno, "too_many_args",
                        f"Function '{node.name}' has {len(node.args.args)} parameters",
                        "info",
                        "Consider using a config object or dataclass"
                    ))

                # Check for missing docstring
                if not ast.get_docstring(node):
                    if not node.name.startswith('_'):
                        issues.append(CodeIssue(
                            file_path, node.lineno, "missing_docstring",
                            f"Function '{node.name}' missing docstring",
                            "info"
                        ))

            # Check class docstrings
            if isinstance(node, ast.ClassDef):
                if not ast.get_docstring(node):
                    issues.append(CodeIssue(
                        file_path, node.lineno, "missing_docstring",
                        f"Class '{node.name}' missing docstring",
                        "info"
                    ))

            # Check for nested functions depth
            if isinstance(node, ast.FunctionDef):
                nested_depth = self._count_nesting(node)
                if nested_depth > 4:
                    issues.append(CodeIssue(
                        file_path, node.lineno, "deep_nesting",
                        f"Function '{node.name}' has deep nesting ({nested_depth} levels)",
                        "warning",
                        "Consider refactoring to reduce complexity"
                    ))

        return issues

    def _count_nesting(self, node: ast.AST, depth: int = 0) -> int:
        """Count maximum nesting depth in a node."""
        max_depth = depth

        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                child_depth = self._count_nesting(child, depth + 1)
                max_depth = max(max_depth, child_depth)
            else:
                child_depth = self._count_nesting(child, depth)
                max_depth = max(max_depth, child_depth)

        return max_depth

    def _check_content(self, file_path: str, content: str) -> List[CodeIssue]:
        """Check content-level patterns."""
        issues = []

        # Check for duplicate imports
        import_pattern = r'^(?:from\s+\S+\s+)?import\s+(.+)$'
        imports = re.findall(import_pattern, content, re.MULTILINE)
        seen = set()
        for imp in imports:
            if imp in seen:
                issues.append(CodeIssue(
                    file_path, 0, "duplicate_import",
                    f"Duplicate import: {imp}", "info"
                ))
            seen.add(imp)

        # Check for magic numbers
        magic_pattern = r'(?<!["\'\w])(\d{3,})(?!["\'\w\.])'
        for match in re.finditer(magic_pattern, content):
            # Skip common acceptable numbers
            num = int(match.group(1))
            if num not in [100, 1000, 1024, 2048, 4096, 8000, 16000, 44100, 48000]:
                line_num = content[:match.start()].count('\n') + 1
                issues.append(CodeIssue(
                    file_path, line_num, "magic_number",
                    f"Magic number {num} should be a named constant",
                    "info"
                ))

        return issues

    def review_directory(self, dir_path: Path, exclude_patterns: List[str] = None) -> List[CodeIssue]:
        """Review all Python files in a directory."""
        exclude_patterns = exclude_patterns or ['venv', '__pycache__', '.git', 'node_modules']

        all_issues = []

        for py_file in dir_path.rglob('*.py'):
            # Check exclusions
            if any(excl in str(py_file) for excl in exclude_patterns):
                continue

            issues = self.review_file(py_file)
            all_issues.extend(issues)

            # Update stats
            for issue in issues:
                self.stats[issue.severity] += 1
                self.stats[f"type:{issue.issue_type}"] += 1

        return all_issues

    def generate_report(self, issues: List[CodeIssue]) -> Dict:
        """Generate a structured report from issues."""
        # Group by file
        by_file = defaultdict(list)
        for issue in issues:
            by_file[issue.file_path].append(issue)

        # Group by type
        by_type = defaultdict(list)
        for issue in issues:
            by_type[issue.issue_type].append(issue)

        return {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_issues": len(issues),
                "errors": self.stats.get("error", 0),
                "warnings": self.stats.get("warning", 0),
                "info": self.stats.get("info", 0),
                "files_reviewed": len(by_file),
            },
            "by_severity": {
                "errors": [i.to_dict() for i in issues if i.severity == "error"],
                "warnings": [i.to_dict() for i in issues if i.severity == "warning"],
            },
            "by_type": {
                issue_type: {
                    "count": len(items),
                    "examples": [i.to_dict() for i in items[:3]]
                }
                for issue_type, items in by_type.items()
            },
            "by_file": {
                file_path: [i.to_dict() for i in file_issues]
                for file_path, file_issues in by_file.items()
            }
        }


def update_improvements_knowledge(report: Dict, knowledge_path: Path):
    """Update the code improvements knowledge base."""
    improvements_path = knowledge_path / 'code_improvements' / 'improvements.yaml'

    if improvements_path.exists():
        with open(improvements_path, 'r') as f:
            data = yaml.safe_load(f) or {}
    else:
        data = {"reviews": [], "patterns": {}, "resolved": []}

    # Add this review
    review_entry = {
        "date": datetime.now().isoformat()[:10],
        "total_issues": report["summary"]["total_issues"],
        "errors": report["summary"]["errors"],
        "warnings": report["summary"]["warnings"],
    }
    data.setdefault("reviews", []).append(review_entry)

    # Track issue patterns over time
    for issue_type, info in report.get("by_type", {}).items():
        data.setdefault("patterns", {})[issue_type] = {
            "last_count": info["count"],
            "last_seen": datetime.now().isoformat()[:10],
        }

    # Keep history manageable
    data["reviews"] = data["reviews"][-30:]  # Last 30 reviews

    improvements_path.parent.mkdir(parents=True, exist_ok=True)
    with open(improvements_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    return improvements_path


def main():
    parser = argparse.ArgumentParser(description='Review project code')
    parser.add_argument('--path', default='scripts/',
                       help='Path to review (default: scripts/)')
    parser.add_argument('--output', help='Output path for report')
    parser.add_argument('--update-knowledge', action='store_true',
                       help='Update knowledge base with findings')
    parser.add_argument('--severity', choices=['all', 'warning', 'error'],
                       default='all', help='Minimum severity to report')
    args = parser.parse_args()

    reviewer = CodeReviewer()

    review_path = Path(args.path)
    print(f"Reviewing code in: {review_path}")

    if review_path.is_file():
        issues = reviewer.review_file(review_path)
    else:
        issues = reviewer.review_directory(review_path)

    # Filter by severity
    if args.severity == 'warning':
        issues = [i for i in issues if i.severity in ['warning', 'error']]
    elif args.severity == 'error':
        issues = [i for i in issues if i.severity == 'error']

    # Generate report
    report = reviewer.generate_report(issues)

    print(f"\n{'='*60}")
    print("CODE REVIEW SUMMARY")
    print(f"{'='*60}")
    print(f"Files reviewed: {report['summary']['files_reviewed']}")
    print(f"Total issues: {report['summary']['total_issues']}")
    print(f"  Errors: {report['summary']['errors']}")
    print(f"  Warnings: {report['summary']['warnings']}")
    print(f"  Info: {report['summary']['info']}")

    # Show top issue types
    print(f"\n--- TOP ISSUE TYPES ---")
    sorted_types = sorted(
        report['by_type'].items(),
        key=lambda x: x[1]['count'],
        reverse=True
    )[:5]
    for issue_type, info in sorted_types:
        print(f"  {issue_type}: {info['count']}")

    # Show critical issues
    if report['by_severity']['errors']:
        print(f"\n--- ERRORS (require attention) ---")
        for error in report['by_severity']['errors'][:5]:
            print(f"  {error['file']}:{error['line']} - {error['description']}")

    if report['by_severity']['warnings'][:5]:
        print(f"\n--- WARNINGS (should review) ---")
        for warning in report['by_severity']['warnings'][:5]:
            print(f"  {warning['file']}:{warning['line']} - {warning['description']}")

    # Save report
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = Path('knowledge') / 'code_review_report.yaml'

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        yaml.dump(report, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    print(f"\nSaved report to: {output_path}")

    # Update knowledge base
    if args.update_knowledge:
        improvements_path = update_improvements_knowledge(report, Path('knowledge'))
        print(f"Updated knowledge: {improvements_path}")


if __name__ == "__main__":
    main()
