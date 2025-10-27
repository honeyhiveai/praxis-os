#!/usr/bin/env bash
# Validates documentation quality before commit
# Runs Divio compliance and internal link checks on changed markdown files

set -euo pipefail

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Validating documentation quality...${NC}"
echo ""

# Check if docs directory exists
if [[ ! -d "docs/content" ]]; then
    echo -e "${YELLOW}⚠️  No docs/content directory found, skipping doc validation${NC}"
    exit 0
fi

# Get list of changed markdown files in docs/
CHANGED_MD_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '^docs/.*\.md$' || true)

if [[ -z "$CHANGED_MD_FILES" ]]; then
    echo -e "${GREEN}✅ No documentation files changed, skipping validation${NC}"
    exit 0
fi

echo -e "${BLUE}📄 Changed documentation files:${NC}"
echo "$CHANGED_MD_FILES" | sed 's/^/  - /'
echo ""

VALIDATION_FAILED=0

# ============================================================================
# 1. Divio Compliance Check (Warning threshold: 80%)
# ============================================================================

echo -e "${BLUE}📋 Running Divio compliance check...${NC}"

if [[ ! -f "scripts/validate-divio-compliance.py" ]]; then
    echo -e "${YELLOW}⚠️  Divio validation script not found, skipping${NC}"
else
    # Run compliance check on docs/content
    if python scripts/validate-divio-compliance.py 2>&1 | grep -q "FAIL"; then
        echo -e "${RED}❌ Divio compliance check failed${NC}"
        echo -e "${YELLOW}💡 Fix: Review compliance violations above${NC}"
        echo -e "${YELLOW}   - Ensure 'doc_type' frontmatter is present${NC}"
        echo -e "${YELLOW}   - Check content matches declared type${NC}"
        echo -e "${YELLOW}   - Run: python scripts/validate-divio-compliance.py${NC}"
        VALIDATION_FAILED=1
    else
        echo -e "${GREEN}✅ Divio compliance check passed${NC}"
    fi
fi

echo ""

# ============================================================================
# 2. Internal Link Validation
# ============================================================================

echo -e "${BLUE}🔗 Running internal link validation...${NC}"

if [[ ! -f "scripts/validate-links.py" ]]; then
    echo -e "${YELLOW}⚠️  Link validation script not found, skipping${NC}"
else
    # Run link validation (skip external for speed)
    if python scripts/validate-links.py --skip-external 2>&1 | grep -q "FAIL"; then
        echo -e "${RED}❌ Link validation failed (broken internal links found)${NC}"
        echo -e "${YELLOW}💡 Fix: Review broken links above${NC}"
        echo -e "${YELLOW}   - Update broken paths to match new structure${NC}"
        echo -e "${YELLOW}   - Verify target files exist${NC}"
        echo -e "${YELLOW}   - Run: python scripts/validate-links.py --skip-external${NC}"
        VALIDATION_FAILED=1
    else
        echo -e "${GREEN}✅ Link validation passed${NC}"
    fi
fi

echo ""

# ============================================================================
# 3. Optional: Full Docusaurus Build Check
# ============================================================================

if [[ "${DOCS_FULL_BUILD:-0}" == "1" ]]; then
    echo -e "${BLUE}🏗️  Running full Docusaurus build check...${NC}"
    
    if [[ ! -d "docs" ]] || [[ ! -f "docs/package.json" ]]; then
        echo -e "${YELLOW}⚠️  Docusaurus project not found, skipping build check${NC}"
    else
        cd docs
        if npm run build > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Docusaurus build passed${NC}"
            cd ..
        else
            echo -e "${RED}❌ Docusaurus build failed${NC}"
            echo -e "${YELLOW}💡 Fix: Run 'cd docs && npm run build' for details${NC}"
            cd ..
            VALIDATION_FAILED=1
        fi
    fi
    echo ""
fi

# ============================================================================
# Final Result
# ============================================================================

if [[ $VALIDATION_FAILED -eq 1 ]]; then
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}❌ Documentation validation failed${NC}"
    echo -e "${YELLOW}💡 Fix issues above or bypass with: git commit --no-verify${NC}"
    echo -e "${YELLOW}   (Not recommended - prefer fixing issues)${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 1
else
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✅ All documentation validation passed${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 0
fi

