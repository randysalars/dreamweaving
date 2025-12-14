#!/usr/bin/env bash
#
# Diff two DevTools audit reports (markdown).
#
# Usage:
#   ./scripts/utilities/diff_devtools_audits.sh path/to/reportA.md path/to/reportB.md
#
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: ./scripts/utilities/diff_devtools_audits.sh <reportA.md> <reportB.md>"
  exit 1
fi

A="$1"
B="$2"

if [[ ! -f "$A" ]]; then
  echo "Missing file: $A"
  exit 1
fi
if [[ ! -f "$B" ]]; then
  echo "Missing file: $B"
  exit 1
fi

if command -v git >/dev/null 2>&1; then
  exec git diff --no-index -- "$A" "$B"
fi

exec diff -u -- "$A" "$B"

