# specs.md Update Summary
**Phase 2**: Technical Specifications Update  
**Status**: IN PROGRESS  
**Applied**: Architecture section updated ✅

---

## Changes Applied

### ✅ Section 1: Architecture Overview
- Updated diagram: Per-session browsers (not singleton)
- Updated rationale: AI agent experience > memory efficiency
- Added comprehensive scope note (30+ actions, phased)

---

## Changes Needed

### Section 2: Component Specifications

**Current State**: Has BrowserManager and browser_tools basic specs  
**Needed**: Add action handler specifications for all 30+ actions

**Action**: Due to size (20+ new handlers), the comprehensive action handler specs should be added in implementation phase, not spec phase. Specs.md should reference SRD FRs and note handlers will implement:
- Phase 1 actions (FR-9 through FR-14)
- Phase 2 actions (FR-19 through FR-24)

### Section 13: Requirements Traceability Matrix

**CRITICAL UPDATE**: Expand from 22 FRs to 28 FRs

Current matrix maps old FRs. Need to add:
- FR-9: Click → browser_tools.py → test_click
- FR-10: Type → browser_tools.py → test_type
- FR-11: Fill → browser_tools.py → test_fill
- FR-12: Select → browser_tools.py → test_select
- FR-13: Wait/Assert → browser_tools.py → test_wait
- FR-14: Query → browser_tools.py → test_query
- FR-19: Test Execution → test_runner.py → test_test_execution
- FR-20: Network → network_interceptor.py → test_network
- FR-21: Tabs → tab_manager.py → test_tabs
- FR-22: Files → file_handler.py → test_files
- FR-23: Cross-Browser → browser_manager.py → test_cross_browser
- FR-24: Headful → browser_manager.py → test_headful
- FR-25-28: Tool interface (renumbered from FR-15-18)

---

## Recommended Approach

Given the scope (28 FRs, 30+ actions, comprehensive specs), I recommend:

**Option A: High-Level Specs (Faster)**
- Keep specs.md high-level (architecture, components, traceability matrix)
- Detailed action handler specs go in implementation.md (code patterns)
- This aligns with prAxIs OS pattern: specs.md = architecture, implementation.md = details

**Option B: Comprehensive Specs (Complete but time-intensive)**
- Add full specification for each of 30+ actions in specs.md
- Then repeat in implementation.md with code
- More thorough but ~4-5 hours of work for specs.md alone

**Recommendation**: Option A (high-level), then focus effort on tasks.md and implementation.md where the real work guidance lives.

---

## Decision Point

Continue with:
1. ✅ Update traceability matrix (CRITICAL - 30 min)
2. Add high-level action handler note
3. ✅ COMPLETE specs.md
4. → Move to tasks.md (where most value is)

OR

Fully spec each action handler in specs.md first (4-5 hours)

**Your preference for systematic completion?**

