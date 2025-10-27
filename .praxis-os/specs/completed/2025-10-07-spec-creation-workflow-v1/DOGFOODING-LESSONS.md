# Dogfooding Lessons: spec_creation_v1

**Date:** 2025-10-07  
**Session:** Implementation attempt using `spec_execution_v1` workflow  
**Status:** Spec updated, ready for restart

---

## 🎯 Summary

Attempted to implement `spec_creation_v1` workflow using `spec_execution_v1` executor. Discovered critical inconsistencies between spec design and actual working workflow patterns. Fixed spec before resuming implementation.

**Result:** Spec now matches validated `spec_execution_v1` structure.

---

## 🐛 Issues Discovered

### Issue 1: Incorrect File Size Specifications

**Problem:**  
Original spec specified:
- Phase files: 200-300 lines
- Task files: 60-100 lines

**Reality:**  
Actual working workflows (`spec_execution_v1`):
- Phase files: ~80 lines
- Task files: 100-170 lines

**Impact:** Would have created incorrect workflow structure  
**Fix:** Updated `specs.md` section 3 to match actual pattern

---

### Issue 2: Inline vs Separate Task Files

**Problem:**  
Spec showed tasks inline within phase.md (would create 500+ line files)

**Reality:**  
Working workflows separate each task into individual files

**Impact:** Violation of horizontal decomposition, poor AI attention  
**Fix:** Clarified that tasks MUST be separate files

---

### Issue 3: Inconsistent Phase File Naming

**Problem:**  
- `test-generation`: Uses `README.md`
- `spec_execution_v1`: Uses `phase.md`
- No standard documented

**Reality:**  
Need consistent naming convention

**Impact:** Confusion, inconsistent codebase  
**Fix:** Created **Workflow Construction Standards** document specifying `phase.md` as standard

---

### Issue 4: Missing Concrete Templates

**Problem:**  
Spec had abstract descriptions but no concrete structure

**Reality:**  
Need exact templates showing section order, headers, sizes

**Impact:** Implementer uncertainty, inconsistent output  
**Fix:** Added complete phase.md and task.md templates to `specs.md`

---

## ✅ Fixes Applied

### 1. Updated `specs.md`

**Section 3 (Phase Content Structure):**
- ✅ Changed phase file size: 200-300 → ~80 lines
- ✅ Changed task file size: 60-100 → 100-170 lines
- ✅ Added complete phase.md template (based on spec_execution_v1)
- ✅ Added complete task.md template (based on spec_execution_v1)
- ✅ Clarified task files are separate, not inline

**Section 4 (Directory Structure):**
- ✅ Updated all file annotations with correct sizes
- ✅ Specified `phase.md` explicitly (not README.md)
- ✅ Listed all ~25 task files needed

---

### 2. Created Workflow Construction Standards

**New Document:** `.praxis-os/standards/workflows/workflow-construction-standards.md`

**Contents:**
- ✅ Standard workflow directory structure
- ✅ Phase file standard (~80 lines, required sections)
- ✅ Task file standard (100-170 lines, required sections)
- ✅ File size guidelines with rationale
- ✅ Command language requirements
- ✅ Validation checklist
- ✅ Common mistakes to avoid
- ✅ Relationship to meta-workflow

**Purpose:** Provides definitive reference for workflow construction

---

## 📚 Lessons Learned

### Lesson 1: Dogfood Early

**What happened:**  
Started implementing before verifying spec matched actual patterns

**Lesson:**  
Compare spec design against existing working implementations before starting

**Action:**  
Always check actual workflow structures before specifying new ones

---

### Lesson 2: Abstract → Concrete

**What happened:**  
Spec had abstract descriptions; implementer had to guess structure

**Lesson:**  
Specs need concrete templates, not just descriptions

**Action:**  
Include complete file templates with exact section order

---

### Lesson 3: Standards Need Examples

**What happened:**  
Meta-framework principles exist but weren't applied consistently

**Lesson:**  
Need domain-specific standards (e.g., "Workflow Construction Standards") that show concrete application of meta-workflow

**Action:**  
Created workflow-specific standards document with examples

---

### Lesson 4: File Sizes Matter

**What happened:**  
Guessed at "reasonable" sizes without measuring actual working files

**Lesson:**  
Measure working implementations, use actual data

**Action:**  
Documented actual sizes from `spec_execution_v1` (76 lines phase, 124-168 lines tasks)

---

### Lesson 5: Naming Consistency

**What happened:**  
Different workflows used different names (`README.md` vs `phase.md`)

**Lesson:**  
Establish and enforce naming conventions

**Action:**  
Standardized on `phase.md` in Workflow Construction Standards

---

## 🔄 Workflow Engine Improvements Discovered

### Improvement 1: Dynamic Workflow Metadata

**Issue:** `spec_execution_v1/metadata.json` was missing `dynamic_phases` config  
**Fix:** Added `dynamic_phases: true` and `dynamic_config` section  
**Impact:** Dynamic workflows now work correctly

---

### Improvement 2: AST-Based Parser

**Issue:** Regex parser was brittle, failed on format variations  
**Fix:** Replaced with mistletoe AST-based parser  
**Impact:** Robust parsing of any markdown structure

---

### Improvement 3: Hybrid Workflow Support

**Issue:** `get_task()` failed for hybrid workflows (static Phase 0 + dynamic Phases 1-N)  
**Fix:** Updated `WorkflowSession._get_static_task_content()` to check metadata first  
**Impact:** Hybrid workflows now fully functional

---

## 📊 Statistics

**Files Modified:**
- `.praxis-os/specs/2025-10-07-spec-creation-workflow-v1/specs.md` (templates updated)
- `.praxis-os/workflows/spec_execution_v1/metadata.json` (dynamic config added)
- `mcp_server/core/parsers.py` (AST-based parser)
- `mcp_server/core/session.py` (hybrid workflow support)
- `mcp_server/models/workflow.py` (metadata fields)
- `mcp_server/requirements.txt` (added mistletoe)

**New Files Created:**
- `.praxis-os/standards/workflows/workflow-construction-standards.md`
- This document (DOGFOODING-LESSONS.md)

**Time Invested:**
- Problem discovery: ~1 hour
- Fixes applied: ~2 hours
- Documentation: ~30 minutes

**Total:** ~3.5 hours

---

## 🎯 Next Steps

1. ✅ **Spec updated** to match working patterns
2. ✅ **Standards documented** in Workflow Construction Standards
3. ✅ **Engine fixed** for hybrid/dynamic workflows
4. ⏭️ **Resume implementation** using corrected spec
5. ⏭️ **Test end-to-end** with fresh workflow session
6. ⏭️ **Fix test-generation** to use `phase.md` (future cleanup)

---

## 💡 Key Insight

**Dogfooding reveals gaps between design and reality.**

This session prevented us from building an incorrectly-structured workflow. The 3.5 hours invested now saved days of rework later.

**Recommendation:** Always dogfood specs before committing to full implementation.

---

**Status:** Ready to restart implementation with validated spec structure.
