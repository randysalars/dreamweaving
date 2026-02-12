#!/bin/bash
# scripts/dw-quality-check.sh
# Quality gate for the Dreamweaving project.
# Mirrors Salarsu's quality-score.sh but for Python/media pipeline.
# Outputs a score 0-100.

set -euo pipefail

DW_DIR="$(cd "$(dirname "$0")/.." && pwd)"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}  🎬 Dreamweaving Quality Gate${NC}"
echo -e "${BLUE}  $(date)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

SCORE=0
MAX_SCORE=100

section_score() {
    local name="$1"
    local points="$2"
    local max="$3"
    
    printf "  %-35s %d/%d pts\n" "$name" "$points" "$max"
    SCORE=$((SCORE + points))
}

# ─── 1. PYTHON CODE QUALITY (25 pts) ─────────────────
echo -e "${BLUE}§1 Python Code Quality${NC}"
PY_PTS=0

# Check if ruff or pylint is available
if command -v ruff >/dev/null 2>&1; then
    LINT_ERRORS=$(ruff check "$DW_DIR/scripts/" --select E,W --statistics 2>/dev/null | wc -l || echo 999)
    if [ "$LINT_ERRORS" -lt 5 ]; then PY_PTS=15
    elif [ "$LINT_ERRORS" -lt 20 ]; then PY_PTS=10
    elif [ "$LINT_ERRORS" -lt 50 ]; then PY_PTS=5
    fi
elif command -v python3 -m py_compile >/dev/null 2>&1; then
    # At minimum check for syntax errors
    SYNTAX_ERRORS=0
    while IFS= read -r pyfile; do
        python3 -c "import py_compile; py_compile.compile('$pyfile', doraise=True)" 2>/dev/null || SYNTAX_ERRORS=$((SYNTAX_ERRORS + 1))
    done < <(find "$DW_DIR/scripts" -name "*.py" -not -path "*/venv/*" -not -path "*/__pycache__/*" 2>/dev/null | head -50)
    
    if [ "$SYNTAX_ERRORS" -eq 0 ]; then PY_PTS=15
    elif [ "$SYNTAX_ERRORS" -lt 3 ]; then PY_PTS=10
    else PY_PTS=5
    fi
fi

# Type hints usage
TYPE_HINT_FILES=$(grep -rl '-> \|: str\|: int\|: bool\|: list\|: dict\|Optional\[' "$DW_DIR/scripts/" 2>/dev/null | grep '\.py$' | wc -l || echo 0)
TOTAL_PY=$(find "$DW_DIR/scripts" -name "*.py" -not -path "*/venv/*" 2>/dev/null | wc -l || echo 1)
TYPE_RATIO=$((TYPE_HINT_FILES * 100 / (TOTAL_PY + 1)))
if [ "$TYPE_RATIO" -gt 50 ]; then PY_PTS=$((PY_PTS + 10))
elif [ "$TYPE_RATIO" -gt 25 ]; then PY_PTS=$((PY_PTS + 5))
fi

section_score "Python Code Quality" "$PY_PTS" 25

# ─── 2. TEST COVERAGE (20 pts) ───────────────────────
echo -e "${BLUE}§2 Test Coverage${NC}"
TEST_PTS=0

TEST_COUNT=$(find "$DW_DIR/tests" -name "test_*.py" -o -name "*_test.py" 2>/dev/null | wc -l || echo 0)
if [ "$TEST_COUNT" -gt 10 ]; then TEST_PTS=10
elif [ "$TEST_COUNT" -gt 5 ]; then TEST_PTS=7
elif [ "$TEST_COUNT" -gt 0 ]; then TEST_PTS=3
fi

# Try running tests
if [ -f "$DW_DIR/pytest.ini" ] || [ -f "$DW_DIR/setup.cfg" ]; then
    if (cd "$DW_DIR" && python3 -m pytest tests/ -x --tb=short -q 2>/dev/null); then
        TEST_PTS=$((TEST_PTS + 10))
    else
        TEST_PTS=$((TEST_PTS + 2))
    fi
fi

section_score "Test Coverage" "$TEST_PTS" 20

# ─── 3. KNOWLEDGE BASE INTEGRITY (20 pts) ────────────
echo -e "${BLUE}§3 Knowledge Base Integrity${NC}"
KB_PTS=0

if [ -d "$DW_DIR/knowledge" ]; then
    KB_FILES=$(find "$DW_DIR/knowledge" -name "*.yaml" -o -name "*.yml" -o -name "*.md" 2>/dev/null | wc -l || echo 0)
    if [ "$KB_FILES" -gt 20 ]; then KB_PTS=10
    elif [ "$KB_FILES" -gt 10 ]; then KB_PTS=7
    elif [ "$KB_FILES" -gt 0 ]; then KB_PTS=3
    fi
    
    # Check for key files
    [ -f "$DW_DIR/knowledge/lessons_learned.yaml" ] && KB_PTS=$((KB_PTS + 3))
    [ -f "$DW_DIR/knowledge/best_practices.md" ] && KB_PTS=$((KB_PTS + 3))
    [ -d "$DW_DIR/knowledge/indexes" ] && KB_PTS=$((KB_PTS + 4))
fi

section_score "Knowledge Base Integrity" "$KB_PTS" 20

# ─── 4. SESSION HYGIENE (15 pts) ─────────────────────
echo -e "${BLUE}§4 Session Hygiene${NC}"
SH_PTS=0

if [ -d "$DW_DIR/sessions" ]; then
    TOTAL_SESSIONS=$(find "$DW_DIR/sessions" -maxdepth 1 -type d | wc -l || echo 0)
    
    # Check for orphaned sessions (no manifest)
    ORPHANS=0
    for session in "$DW_DIR"/sessions/*/; do
        [ ! -d "$session" ] && continue
        if [ ! -f "${session}manifest.yaml" ] && [ ! -f "${session}manifest.yml" ]; then
            ORPHANS=$((ORPHANS + 1))
        fi
    done
    
    if [ "$ORPHANS" -eq 0 ]; then SH_PTS=10
    elif [ "$ORPHANS" -lt 3 ]; then SH_PTS=7
    else SH_PTS=3
    fi
    
    # Check for stuck working_files (over 7 days old)
    STALE=$(find "$DW_DIR/sessions" -name "working_files" -type d -mtime +7 2>/dev/null | wc -l || echo 0)
    if [ "$STALE" -eq 0 ]; then SH_PTS=$((SH_PTS + 5))
    elif [ "$STALE" -lt 3 ]; then SH_PTS=$((SH_PTS + 3))
    fi
fi

section_score "Session Hygiene" "$SH_PTS" 15

# ─── 5. INFRASTRUCTURE (20 pts) ──────────────────────
echo -e "${BLUE}§5 Infrastructure${NC}"
INF_PTS=0

[ -f "$DW_DIR/requirements.txt" ] && INF_PTS=$((INF_PTS + 3))
[ -d "$DW_DIR/venv" ] && INF_PTS=$((INF_PTS + 2))
[ -f "$DW_DIR/.gitignore" ] && INF_PTS=$((INF_PTS + 2))
[ -f "$DW_DIR/CLAUDE.md" ] && INF_PTS=$((INF_PTS + 3))
[ -f "$DW_DIR/pytest.ini" ] && INF_PTS=$((INF_PTS + 2))
[ -d "$DW_DIR/.claude/skills" ] && INF_PTS=$((INF_PTS + 3))
[ -d "$DW_DIR/agents" ] && INF_PTS=$((INF_PTS + 3))

# Git health
if (cd "$DW_DIR" && git status --porcelain 2>/dev/null | wc -l) | grep -q '^0$'; then
    INF_PTS=$((INF_PTS + 2))
fi

section_score "Infrastructure" "$INF_PTS" 20

# ─── SUMMARY ─────────────────────────────────────────
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
printf "  ${BLUE}Quality Score: "
if [ "$SCORE" -ge 80 ]; then
    echo -e "${GREEN}${SCORE}/100${NC} 🟢"
elif [ "$SCORE" -ge 60 ]; then
    echo -e "${YELLOW}${SCORE}/100${NC} 🟡"
else
    echo -e "${RED}${SCORE}/100${NC} 🔴"
fi
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"

# Output JSON for consumption by other tools
echo "{\"score\": $SCORE, \"max\": 100, \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" > "/tmp/dw-quality-score.json"

exit 0
