#!/bin/bash
# Setup Git Hooks for Workflow Validation
#
# This script installs git hooks that automatically validate workflow
# documentation before commits.
#
# Usage:
#   ./scripts/utilities/setup_git_hooks.sh

set -e

cd "$(git rev-parse --show-toplevel)"

echo "🔧 Setting up git hooks for workflow validation..."
echo ""

# Check if .git directory exists
if [ ! -d ".git" ]; then
    echo "❌ Error: .git directory not found"
    echo "   Are you in a git repository?"
    exit 1
fi

# Create hooks directory if it doesn't exist
mkdir -p .git/hooks

# Install pre-commit hook
if [ -f ".git/hooks/pre-commit" ]; then
    echo "⚠️  Warning: pre-commit hook already exists"
    echo ""
    echo "Options:"
    echo "  1. Backup and replace"
    echo "  2. Skip installation"
    echo "  3. View existing hook"
    echo ""
    read -p "Choose (1/2/3): " choice

    case $choice in
        1)
            echo "Backing up existing hook..."
            mv .git/hooks/pre-commit .git/hooks/pre-commit.backup.$(date +%Y%m%d%H%M%S)
            ;;
        2)
            echo "Skipping pre-commit hook installation"
            exit 0
            ;;
        3)
            echo ""
            echo "=== Existing pre-commit hook ==="
            cat .git/hooks/pre-commit
            echo "================================"
            exit 0
            ;;
        *)
            echo "Invalid choice, exiting"
            exit 1
            ;;
    esac
fi

# Create symlink to our hook
ln -s ../../.githooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

echo "✅ Pre-commit hook installed!"
echo ""
echo "What this does:"
echo "  • Validates workflow documentation before commits"
echo "  • Checks for missing version headers"
echo "  • Validates script references"
echo "  • Checks command formats"
echo "  • Ensures duration consistency"
echo ""
echo "To bypass validation (emergency only):"
echo "  git commit --no-verify"
echo ""
echo "To test the hook:"
echo "  python3 scripts/utilities/validate_workflows.py"
echo ""
echo "✓ Setup complete!"
