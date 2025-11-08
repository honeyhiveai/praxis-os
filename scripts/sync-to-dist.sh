#!/bin/bash
#
# sync-to-dist.sh: Sync local dev install to dist/ build artifacts
#
# Workflow:
#   1. Dev in .praxis-os/ (local install)
#   2. Verify everything works
#   3. Run this script to sync to dist/
#   4. Manually reconcile config/mcp.yaml (environment-specific)
#
# Usage:
#   ./scripts/sync-to-dist.sh          # Dry-run (show what will be synced)
#   ./scripts/sync-to-dist.sh --sync   # Actually sync files
#
# What gets synced:
#   ✅ .praxis-os/ouroboros/ → dist/ouroboros/
#   ✅ .praxis-os/standards/universal/ → dist/universal/standards/
#   ✅ .praxis-os/workflows/ → dist/universal/workflows/
#   ❌ config/mcp.yaml (manual reconciliation required)
#   ❌ __pycache__, *.pyc (excluded)
#   ❌ state/, .cache/ (runtime files, excluded)
#
# Traceability:
#   - Built to prevent dist/ drift issues
#   - Ensures deployable artifacts match verified local install

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Detect project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Paths
LOCAL_INSTALL="$PROJECT_ROOT/.praxis-os"
DIST_DIR="$PROJECT_ROOT/dist"

# Check if running in dry-run or sync mode
DRY_RUN=true
if [[ "${1:-}" == "--sync" ]]; then
    DRY_RUN=false
fi

# Header
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Sync Local Install → dist/ Build Artifacts${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""

# Validate paths exist
if [[ ! -d "$LOCAL_INSTALL" ]]; then
    echo -e "${RED}❌ Local install not found: $LOCAL_INSTALL${NC}"
    exit 1
fi

if [[ ! -d "$DIST_DIR" ]]; then
    echo -e "${RED}❌ Dist directory not found: $DIST_DIR${NC}"
    exit 1
fi

# Function to show diff summary
show_diff() {
    local src=$1
    local dest=$2
    local name=$3
    
    echo -e "${YELLOW}📊 Comparing: $name${NC}"
    
    # Use rsync dry-run to show what would change
    # Exclude patterns: __pycache__, *.pyc, state/, .cache/
    rsync_output=$(rsync -avn --delete \
        --exclude='__pycache__/' \
        --exclude='*.pyc' \
        --exclude='state/' \
        --exclude='.cache/' \
        --itemize-changes \
        "$src/" "$dest/" 2>&1 || true)
    
    # Count changes (rsync itemize format: >f+++++++++ = new file, *deleting = deleted)
    files_to_update=$(echo "$rsync_output" | grep -cE '^>f|^\.f|^<f')
    files_to_delete=$(echo "$rsync_output" | grep -cE '^\*deleting.*\.(py|md|yaml|yml|txt|sh|json)$')
    dirs_to_create=$(echo "$rsync_output" | grep -cE '^cd\+')
    
    if [[ $files_to_update -eq 0 && $files_to_delete -eq 0 && $dirs_to_create -eq 0 ]]; then
        echo -e "  ${GREEN}✅ Already in sync (no changes)${NC}"
    else
        echo -e "  ${YELLOW}📝 Changes detected:${NC}"
        [[ $files_to_update -gt 0 ]] && echo -e "     - Files to update/create: $files_to_update"
        [[ $files_to_delete -gt 0 ]] && echo -e "     - Files to delete: $files_to_delete"
        [[ $dirs_to_create -gt 0 ]] && echo -e "     - Directories to create: $dirs_to_create"
        
        # Show first 10 changes
        echo ""
        echo -e "  ${BLUE}Preview (first 10 file changes):${NC}"
        echo "$rsync_output" | grep -E '^(>f|\.f|<f|\*deleting.*\.(py|md|yaml|yml|txt|sh|json)$)' | head -10 | sed 's/^/     /'
        
        total_changes=$((files_to_update + files_to_delete))
        if [[ $total_changes -gt 10 ]]; then
            echo -e "     ${YELLOW}... and $((total_changes - 10)) more file changes${NC}"
        fi
    fi
    echo ""
}

# Function to perform sync
do_sync() {
    local src=$1
    local dest=$2
    local name=$3
    
    echo -e "${GREEN}🔄 Syncing: $name${NC}"
    
    rsync -av --delete \
        --exclude='__pycache__/' \
        --exclude='*.pyc' \
        --exclude='state/' \
        --exclude='.cache/' \
        "$src/" "$dest/"
    
    echo -e "  ${GREEN}✅ Sync complete${NC}"
    echo ""
}

# ============================================================================
# 1. Sync Ouroboros Code
# ============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}1. Ouroboros Code${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

show_diff "$LOCAL_INSTALL/ouroboros" "$DIST_DIR/ouroboros" "Ouroboros"

if [[ $DRY_RUN == false ]]; then
    do_sync "$LOCAL_INSTALL/ouroboros" "$DIST_DIR/ouroboros" "Ouroboros"
fi

# ============================================================================
# 2. Sync Universal Standards
# ============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}2. Universal Standards${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

show_diff "$LOCAL_INSTALL/standards/universal" "$DIST_DIR/universal/standards" "Universal Standards"

if [[ $DRY_RUN == false ]]; then
    do_sync "$LOCAL_INSTALL/standards/universal" "$DIST_DIR/universal/standards" "Universal Standards"
fi

# ============================================================================
# 3. Sync Workflows
# ============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}3. Workflows${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

show_diff "$LOCAL_INSTALL/workflows" "$DIST_DIR/universal/workflows" "Workflows"

if [[ $DRY_RUN == false ]]; then
    do_sync "$LOCAL_INSTALL/workflows" "$DIST_DIR/universal/workflows" "Workflows"
fi

# ============================================================================
# 4. Config Files (Manual Reconciliation Required)
# ============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}4. Config Files (Manual Reconciliation)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${YELLOW}⚠️  Config files require manual reconciliation:${NC}"
echo -e "   📄 .praxis-os/config/mcp.yaml (local dev config)"
echo -e "   📄 dist/config/mcp.yaml (default shipped config)"
echo ""
echo -e "${YELLOW}   These configs are environment-specific and must be reconciled manually.${NC}"
echo -e "${YELLOW}   Local config points to dev install, dist config points to installed paths.${NC}"
echo ""

# ============================================================================
# Summary
# ============================================================================
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
if [[ $DRY_RUN == true ]]; then
    echo -e "${YELLOW}📋 DRY-RUN COMPLETE${NC}"
    echo ""
    echo -e "  This was a preview. No files were modified."
    echo -e "  To actually sync files, run:"
    echo ""
    echo -e "    ${GREEN}./scripts/sync-to-dist.sh --sync${NC}"
    echo ""
else
    echo -e "${GREEN}✅ SYNC COMPLETE${NC}"
    echo ""
    echo -e "  Local install → dist/ sync finished successfully!"
    echo ""
    echo -e "  ${YELLOW}⚠️  Don't forget to manually reconcile config/mcp.yaml${NC}"
    echo ""
fi
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"

