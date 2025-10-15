# Workflow Directory Naming Convention Fix

**Date:** 2025-10-13  
**Workflow:** `spec_creation_v1`  
**Issue:** Workflow did not enforce spec directory naming convention  
**Status:** ✅ FIXED

---

## Problem

The `spec_creation_v1` workflow used a `{SPEC_DIR}` placeholder throughout all tasks but **never defined how to set it** or what naming convention to follow.

This led to inconsistent spec directory naming:
- ❌ Created: `thread-safety-fixes-2025-10-13` (date as suffix)
- ✅ Expected: `2025-10-13-thread-safety-fixes` (date as prefix)

**Root Cause:** Workflow relied on implicit assumptions instead of explicit instructions.

---

## Solution

Added **Task 0: Create Spec Directory** to Phase 0 with:

1. **Explicit Naming Convention:**
   - Format: `YYYY-MM-DD-descriptive-name`
   - Date as PREFIX (ISO 8601)
   - Kebab-case descriptive name
   - 2-5 words max

2. **Validation:**
   - Regex format check
   - Current date verification (via `current_date` tool)
   - Case and character validation

3. **Common Issue Documentation:**
   - Examples of wrong vs correct formats
   - Troubleshooting for common mistakes

4. **Export for Reuse:**
   - Stores `SPEC_DIR` in `.agent-os/specs/.current-spec`
   - All subsequent tasks source this value

---

## Changes Made

### 1. Created New Task File
**File:** `universal/workflows/spec_creation_v1/phases/0/task-0-create-directory.md`
- **Lines:** 159 (within 100-170 optimal range ✅)
- **Purpose:** Enforce directory naming convention
- **Time:** 1 minute

### 2. Updated Phase 0 Overview
**File:** `universal/workflows/spec_creation_v1/phases/0/phase.md`
- Total tasks: 3 → 4
- Task sequence: 0 → 1 → 2 → 3
- Added directory creation to deliverables
- Added format validation to checkpoint

### 3. Updated Metadata
**File:** `universal/workflows/spec_creation_v1/metadata.json`
- Added Task 0 to Phase 0 tasks array
- Added `spec_directory_created` to checkpoint evidence
- Added format validation to validation criteria
- Updated key deliverables

**Validation:** ✅ Passes `validate_workflow_metadata.py`

### 4. Updated Task 1
**File:** `universal/workflows/spec_creation_v1/phases/0/task-1-copy-documents.md`
- Changed Step 1 from "create directory" to "verify directory exists"
- Updated all bash commands to `source .current-spec` and use `${SPEC_DIR}`
- Fixed step numbering (was duplicate Step 4s)

---

## Validation

```bash
$ python scripts/validate_workflow_metadata.py universal/workflows/spec_creation_v1

✅ VALID - All required fields present and properly structured
✅ Metadata follows workflow-metadata-standards.md
✅ Ready for workflow engine consumption
```

**Task 0 File:**
```bash
$ ls -la .agent-os/workflows/spec_creation_v1/phases/0/task-0-create-directory.md
-rw-r--r--  4058 Oct 13 10:34 task-0-create-directory.md  ✅
```

---

## Impact

### Before (Broken)
- AI inferred naming from context (unreliable)
- Created `feature-name-2025-10-13` (wrong format)
- No validation or guidance

### After (Fixed)
- Explicit `YYYY-MM-DD-descriptive-name` format
- Mandatory validation gate
- Common issues documented
- Current date tool enforced

### Future Specs
All future specs created via `spec_creation_v1` will:
- ✅ Follow `YYYY-MM-DD-descriptive-name` convention
- ✅ Sort chronologically in directory listings
- ✅ Match existing spec naming patterns
- ✅ Use correct current date (not inferred)

---

## Example Usage

When AI runs `spec_creation_v1` now:

```bash
# Task 0 (NEW)
# AI calls: mcp_agent-os-rag_current_date()
# Returns: {"date": "2025-10-13"}
# AI constructs: 2025-10-13-{descriptive-name}
SPEC_DIR="2025-10-13-thread-safety-fixes"

# Validate format
[[ $SPEC_DIR =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z0-9-]+$ ]] || exit 1

# Create
mkdir -p .agent-os/specs/${SPEC_DIR}
echo "SPEC_DIR=${SPEC_DIR}" > .agent-os/specs/.current-spec

# Task 1 (UPDATED)
source .agent-os/specs/.current-spec
mkdir -p .agent-os/specs/${SPEC_DIR}/supporting-docs/
# ... uses ${SPEC_DIR} throughout
```

---

## Lessons Learned

1. **Explicit > Implicit:** Workflows must explicitly define conventions, not assume AI will infer them.

2. **Validation Gates:** Adding format validation prevents silent failures.

3. **Horizontal Decomposition:** Task 0 is 159 lines (optimal range), focused on single concern.

4. **Dogfooding Catches Issues:** This bug was discovered while dogfooding `spec_creation_v1` to create the thread safety spec.

5. **Meta-Framework Works:** The workflow that creates workflows (`workflow_creation_v1`) needs its own quality gates to ensure generated workflows are correct.

---

## Related Fixes

This fix is related to but separate from:
- **Metadata Schema Fix** (2025-10-13): Standardized metadata.json format
- **Thread Safety Analysis** (2025-10-13): Discovered during spec creation for this issue

---

## Status

✅ **COMPLETE**
- [x] Task 0 created (159 lines)
- [x] Phase 0 updated
- [x] metadata.json updated
- [x] Task 1 updated to reference Task 0
- [x] Validation passes
- [x] Copied to `.agent-os/workflows/`
- [x] Summary documented

**Next:** Future specs will automatically follow the correct naming convention.

