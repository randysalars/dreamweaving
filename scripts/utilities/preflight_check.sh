#!/bin/bash
# Pre-flight Check Script
# Runs all necessary checks before starting any workflow
# Usage: ./scripts/utilities/preflight_check.sh [--fix]

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

echo -e "${BOLD}=== Dreamweaving Pre-Flight Check ===${NC}\n"

# Track results
CHECKS_PASSED=0
CHECKS_FAILED=0
CHECKS_WARNING=0

# Parse arguments
AUTO_FIX=false
if [[ "$1" == "--fix" ]]; then
    AUTO_FIX=true
    echo -e "${BLUE}Auto-fix enabled${NC}\n"
fi

# Check 1: Environment
echo -e "${BOLD}[1/5] Checking Environment...${NC}"
if python3 scripts/core/check_env.py; then
    echo -e "${GREEN}✓ Environment OK${NC}\n"
    ((CHECKS_PASSED++))
else
    echo -e "${RED}✗ Environment issues found${NC}"
    if [ "$AUTO_FIX" = true ]; then
        echo -e "${BLUE}Attempting auto-fix...${NC}"
        if python3 scripts/core/check_env.py --fix; then
            echo -e "${GREEN}✓ Environment fixed${NC}\n"
            ((CHECKS_PASSED++))
        else
            echo -e "${RED}✗ Auto-fix failed${NC}\n"
            ((CHECKS_FAILED++))
        fi
    else
        echo -e "${YELLOW}Run with --fix to attempt automatic fixes${NC}\n"
        ((CHECKS_FAILED++))
    fi
fi

# Check 2: Disk Space
echo -e "${BOLD}[2/5] Checking Disk Space...${NC}"
FREE_SPACE=$(df "$PROJECT_ROOT" | awk 'NR==2 {print $4}')
FREE_GB=$((FREE_SPACE / 1024 / 1024))

if [ $FREE_GB -ge 5 ]; then
    echo -e "${GREEN}✓ Sufficient disk space: ${FREE_GB}GB available${NC}\n"
    ((CHECKS_PASSED++))
elif [ $FREE_GB -ge 1 ]; then
    echo -e "${YELLOW}⚠ Low disk space: ${FREE_GB}GB available (recommend 5GB+)${NC}\n"
    ((CHECKS_WARNING++))
else
    echo -e "${RED}✗ Critical disk space: ${FREE_GB}GB available${NC}\n"
    ((CHECKS_FAILED++))
fi

# Check 3: Required Directories
echo -e "${BOLD}[3/5] Checking Directory Structure...${NC}"
REQUIRED_DIRS=("sessions" "scripts/core" "scripts/utilities" "docs" "config")
MISSING_DIRS=()

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        MISSING_DIRS+=("$dir")
    fi
done

if [ ${#MISSING_DIRS[@]} -eq 0 ]; then
    echo -e "${GREEN}✓ All required directories present${NC}\n"
    ((CHECKS_PASSED++))
else
    echo -e "${RED}✗ Missing directories: ${MISSING_DIRS[*]}${NC}"
    if [ "$AUTO_FIX" = true ]; then
        echo -e "${BLUE}Creating missing directories...${NC}"
        for dir in "${MISSING_DIRS[@]}"; do
            mkdir -p "$dir"
            echo -e "  Created: $dir"
        done
        echo -e "${GREEN}✓ Directories created${NC}\n"
        ((CHECKS_PASSED++))
    else
        echo -e "${YELLOW}Run with --fix to create missing directories${NC}\n"
        ((CHECKS_FAILED++))
    fi
fi

# Check 4: Workflow Documentation
echo -e "${BOLD}[4/5] Validating Workflow Documentation...${NC}"
if python3 scripts/utilities/validate_workflows.py > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Workflow documentation valid${NC}\n"
    ((CHECKS_PASSED++))
else
    echo -e "${YELLOW}⚠ Workflow validation warnings (non-critical)${NC}\n"
    ((CHECKS_WARNING++))
fi

# Check 5: Git Status
echo -e "${BOLD}[5/5] Checking Git Status...${NC}"
if git diff --quiet && git diff --cached --quiet 2>/dev/null; then
    echo -e "${GREEN}✓ Working directory clean${NC}\n"
    ((CHECKS_PASSED++))
else
    UNCOMMITTED=$(git status --short 2>/dev/null | wc -l)
    echo -e "${YELLOW}⚠ ${UNCOMMITTED} uncommitted changes${NC}\n"
    ((CHECKS_WARNING++))
fi

# Summary
echo -e "${BOLD}=== Summary ===${NC}\n"
echo -e "${GREEN}Passed:${NC}   $CHECKS_PASSED"
echo -e "${YELLOW}Warnings:${NC} $CHECKS_WARNING"
echo -e "${RED}Failed:${NC}   $CHECKS_FAILED"
echo ""

# Final status
if [ $CHECKS_FAILED -eq 0 ]; then
    if [ $CHECKS_WARNING -eq 0 ]; then
        echo -e "${GREEN}${BOLD}✓ All checks passed! Ready to proceed.${NC}\n"
        exit 0
    else
        echo -e "${YELLOW}${BOLD}⚠ System ready with warnings${NC}\n"
        exit 0
    fi
else
    echo -e "${RED}${BOLD}✗ Please fix critical issues before proceeding${NC}"
    if [ "$AUTO_FIX" = false ]; then
        echo -e "${BLUE}Tip: Run with --fix to attempt automatic fixes${NC}"
    fi
    echo ""
    exit 1
fi
