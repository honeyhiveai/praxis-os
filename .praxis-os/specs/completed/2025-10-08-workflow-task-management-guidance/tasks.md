# Implementation Tasks

**Project:** Workflow Task Management Guidance  
**Date:** 2025-10-08  
**Based on:** srd.md (requirements), specs.md (design)

---

## Task Breakdown Overview

**Total Phases:** 2  
**Total Tasks:** 6  
**Estimated Time:** 1 hour 30 minutes

---

## Phase 1: Implementation

**Purpose:** Implement guidance wrapper and integrate with workflow engine  
**Estimated Time:** 45 minutes

---

### Task 1.1: Create Guidance Wrapper Function

**Description:** Implement the `add_workflow_guidance()` function that injects task management guidance fields into workflow responses.

**File:** `mcp_server/workflow_engine.py` (add new function)

**Requirements Satisfied:** FR-1, FR-2, FR-3, NFR-P1, NFR-M1, NFR-R1

**Acceptance Criteria:**
- [ ] Function `add_workflow_guidance(response: Dict) -> Dict` created
- [ ] Constant `WORKFLOW_GUIDANCE_FIELDS` defined with 3 required fields:
  - `⚠️_WORKFLOW_EXECUTION_MODE`: "ACTIVE"
  - `🛑_DO_NOT_USE_EXTERNAL_TASK_TOOLS`: (prohibition message)
  - `execution_model`: "Complete task → Submit evidence → Advance phase"
- [ ] Function handles non-dict inputs gracefully (returns input unchanged)
- [ ] Function has try-except with logging for error handling
- [ ] Guidance fields prepended to response (appear first in dict)
- [ ] Function is pure (no side effects, stateless)
- [ ] Type hints included (Dict[str, Any])
- [ ] Docstring with example included

**Time Estimate:** 15 minutes

**Dependencies:** None

---

### Task 1.2: Integrate Wrapper with Workflow Engine

**Description:** Modify WorkflowEngine methods to apply guidance wrapper to all responses.

**File:** `mcp_server/workflow_engine.py` (modify WorkflowEngine class)

**Requirements Satisfied:** FR-4, FR-5, FR-7

**Acceptance Criteria:**
- [ ] `start_workflow()` method calls `add_workflow_guidance()` before return
- [ ] `get_current_phase()` method calls `add_workflow_guidance()` before return
- [ ] `get_task()` method calls `add_workflow_guidance()` before return
- [ ] `complete_phase()` method calls `add_workflow_guidance()` before return
- [ ] `get_workflow_state()` method calls `add_workflow_guidance()` before return
- [ ] No changes to method signatures (backward compatible)
- [ ] No changes to core workflow logic
- [ ] Integration is transparent (callers don't need changes)

**Time Estimate:** 10 minutes

**Dependencies:** Task 1.1 (wrapper function must exist)

---

### Task 1.3: Add Logging and Error Handling

**Description:** Ensure proper logging for guidance injection failures.

**File:** `mcp_server/workflow_engine.py`

**Requirements Satisfied:** NFR-R1, NFR-M3

**Acceptance Criteria:**
- [ ] Import logger at module level
- [ ] Wrapper function logs warning if injection fails
- [ ] Log message includes exception details
- [ ] No exceptions propagated from wrapper
- [ ] Graceful degradation documented in comments

**Time Estimate:** 5 minutes

**Dependencies:** Task 1.1

---

### Task 1.4: Code Review and Refactoring

**Description:** Review implementation for code quality, style, and adherence to prAxIs OS conventions.

**Requirements Satisfied:** NFR-M2

**Acceptance Criteria:**
- [ ] Code follows PEP 8 style guidelines
- [ ] Follows existing prAxIs OS Python conventions
- [ ] No code duplication
- [ ] Clear variable and function names
- [ ] Comments explain non-obvious decisions
- [ ] No TODOs or FIXMEs left in code
- [ ] Implementation is < 50 lines total (per NFR-M1)

**Time Estimate:** 10 minutes

**Dependencies:** Tasks 1.1, 1.2, 1.3

---

### Phase 1 Validation Gate

🛑 **GATE:** Implementation Complete

**Checkpoint Evidence Required:**
- [ ] All code changes implemented ✅/❌
- [ ] Guidance wrapper function complete ✅/❌
- [ ] All 5 workflow engine methods wrapped ✅/❌
- [ ] Error handling implemented ✅/❌
- [ ] Code follows style guidelines ✅/❌
- [ ] No linter errors ✅/❌
- [ ] Implementation <= 50 lines of code ✅/❌

**Validation Method:**
- Manual code review
- Run linter: `ruff check mcp_server/workflow_engine.py`
- Count lines added/modified

**Proceed to Phase 2 only when all criteria met.**

---

## Phase 2: Testing & Validation

**Purpose:** Test implementation and validate requirements satisfied  
**Estimated Time:** 45 minutes

---

### Task 2.1: Write Unit Tests

**Description:** Create unit tests for the guidance wrapper function.

**File:** `tests/unit/test_workflow_guidance.py` (new file)

**Requirements Satisfied:** NFR-M2 (100% test coverage)

**Acceptance Criteria:**
- [ ] Test file created: `tests/unit/test_workflow_guidance.py`
- [ ] Test: `test_add_guidance_to_valid_dict()` - normal case
- [ ] Test: `test_add_guidance_preserves_original_fields()` - non-invasive
- [ ] Test: `test_add_guidance_with_non_dict_input()` - graceful degradation
- [ ] Test: `test_guidance_fields_appear_first()` - field ordering
- [ ] Test: `test_guidance_field_values()` - correct content
- [ ] Test: `test_all_required_fields_present()` - completeness
- [ ] All tests pass
- [ ] 100% coverage of `add_workflow_guidance()` function

**Time Estimate:** 20 minutes

**Dependencies:** Phase 1 complete

---

### Task 2.2: Write Integration Test

**Description:** Create integration test validating AI doesn't create TODOs during workflow execution.

**File:** `tests/integration/test_workflow_guidance_integration.py` (new file)

**Requirements Satisfied:** Acceptance Testing (srd.md Section 7.2, Test Scenario 1)

**Acceptance Criteria:**
- [ ] Test file created: `tests/integration/test_workflow_guidance_integration.py`
- [ ] Test: `test_workflow_responses_include_guidance()` - checks all tools
  - Calls `start_workflow()`
  - Calls `get_current_phase()`
  - Calls `get_task()`
  - Calls `complete_phase()`
  - Asserts all responses have guidance fields
- [ ] Test: `test_guidance_fields_in_all_workflow_types()` - universal coverage
  - Tests `spec_creation_v1`
  - Tests `spec_execution_v1`
  - Verifies guidance present in both
- [ ] Test: `test_backward_compatibility()` - existing workflows work
  - Workflow completes successfully
  - Response structure valid
  - No breaking changes
- [ ] All integration tests pass

**Time Estimate:** 20 minutes

**Dependencies:** Phase 1 complete

---

### Task 2.3: Manual Validation & Dogfooding

**Description:** Manually execute a workflow and verify no TODO creation, guidance visible.

**Requirements Satisfied:** Acceptance Testing (srd.md Section 7.1, Definition of Done)

**Acceptance Criteria:**
- [ ] Start `spec_creation_v1` workflow manually
- [ ] Execute through at least Phase 1
- [ ] Verify: No `todo_write` calls made by AI
- [ ] Verify: Guidance fields visible in tool responses
- [ ] Verify: Guidance messages clear and actionable
- [ ] Document results in validation report
- [ ] Take screenshots of guidance fields in responses (optional)

**Time Estimate:** 15 minutes (including documentation)

**Dependencies:** Phase 1 complete, Task 2.1 and 2.2 passed

---

### Phase 2 Validation Gate

🛑 **GATE:** Testing & Validation Complete

**Checkpoint Evidence Required:**
- [ ] Unit tests written and passing ✅/❌
- [ ] Integration tests written and passing ✅/❌
- [ ] Manual validation completed ✅/❌
- [ ] No TODOs created during test workflow execution ✅/❌
- [ ] Guidance fields present in all tool responses ✅/❌
- [ ] All acceptance criteria from srd.md Section 7.1 met ✅/❌
- [ ] Validation report documented ✅/❌

**Validation Method:**
- Run: `pytest tests/unit/test_workflow_guidance.py -v`
- Run: `pytest tests/integration/test_workflow_guidance_integration.py -v`
- Review manual validation documentation
- Check test coverage: `pytest --cov=mcp_server.workflow_engine --cov-report=term`

**All tests must pass before considering feature complete.**

---

## Task Dependencies Diagram

```
Phase 1: Implementation
┌─────────────────────────────────────────────────┐
│                                                 │
│  Task 1.1: Create Wrapper Function             │
│              (15 min)                           │
│                                                 │
└────────────┬────────────────────────────────────┘
             │
             ├──────┐
             │      │
             ▼      ▼
┌────────────────────┐  ┌──────────────────────┐
│                    │  │                      │
│  Task 1.2:         │  │  Task 1.3:           │
│  Integrate         │  │  Add Logging         │
│  (10 min)          │  │  (5 min)             │
│                    │  │                      │
└──────────┬─────────┘  └──────┬───────────────┘
           │                   │
           └────────┬──────────┘
                    │
                    ▼
           ┌──────────────────┐
           │                  │
           │  Task 1.4:       │
           │  Code Review     │
           │  (10 min)        │
           │                  │
           └────────┬─────────┘
                    │
           ═════════▼═════════════════════
                PHASE 1 GATE
           ═════════════════════════════════
                    │
                    ▼
Phase 2: Testing & Validation
┌────────────────────────────────────────────────┐
│                                                │
│  Task 2.1: Write Unit Tests (20 min)          │
│  Task 2.2: Write Integration Tests (20 min)   │
│  Task 2.3: Manual Validation (15 min)         │
│                                                │
│  (Can be done in parallel)                    │
└────────────────────┬───────────────────────────┘
                     │
            ═════════▼═════════════════════
                 PHASE 2 GATE
            ═════════════════════════════════
                     │
                     ▼
              FEATURE COMPLETE
```

---

## Time Estimates Summary

| Phase | Total Time | Tasks |
|-------|------------|-------|
| Phase 1: Implementation | 45 min | 4 tasks |
| Phase 2: Testing & Validation | 45 min | 3 tasks |
| **TOTAL** | **1h 30min** | **7 tasks** |

**Note:** Estimate assumes developer familiar with codebase. Includes time for validation gates and documentation.

---

## Requirements Traceability Matrix

| Requirement | Implemented By | Tested By |
|-------------|---------------|-----------|
| FR-1: Mode indication | Task 1.1 | Task 2.1, 2.2 |
| FR-2: External tool prohibition | Task 1.1 | Task 2.1, 2.2 |
| FR-3: Execution model | Task 1.1 | Task 2.1, 2.2 |
| FR-4: Universal coverage | Task 1.2 | Task 2.2 |
| FR-5: Backward compatibility | Task 1.2 | Task 2.2 |
| FR-6: Response size efficiency | Task 1.1 | Task 2.1 |
| FR-7: Persistent guidance | Task 1.2 | Task 2.2 |
| NFR-P1: Performance | Task 1.1 | Task 2.1 (timing) |
| NFR-M1: Simplicity | Task 1.4 | Manual review |
| NFR-M2: Code quality | Task 1.4, 2.1 | Manual review, tests |
| NFR-C1: Backward compat | Task 1.2 | Task 2.2 |
| NFR-R1: Fault tolerance | Task 1.3 | Task 2.1 |
| NFR-R2: Consistency | Task 1.1 | Task 2.2 |
| NFR-U1: Clarity | Task 1.1 | Task 2.3 (manual) |
| NFR-U2: Visibility | Task 1.1 | Task 2.3 (manual) |

**Coverage:** 100% of requirements traced to implementation and tests

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation | Task |
|------|------------|--------|------------|------|
| Wrapper breaks existing workflows | Low | High | Extensive testing, graceful degradation | Task 2.2 |
| Performance overhead too high | Very Low | Medium | Keep implementation minimal, benchmark | Task 2.1 |
| AI still creates TODOs | Medium | High | Manual validation, iterate on messaging | Task 2.3 |
| Test coverage insufficient | Low | Medium | 100% coverage requirement, integration tests | Task 2.1, 2.2 |

**Overall Risk:** LOW (simple implementation, extensive testing, graceful degradation)

---

## Rollout Plan

**Deployment Strategy:** Single-step deployment (no feature flag needed)

**Rollout Steps:**
1. Merge implementation to main branch
2. Deploy to praxis-os dogfooding environment
3. Validate via manual workflow execution
4. Monitor for issues (none expected - fail-safe design)
5. Document in CHANGELOG.md

**Rollback Plan:**
- If issues detected: Revert commit (< 5 minutes)
- No data migration required
- No breaking changes (backward compatible)

---

## Success Metrics

Post-deployment, validate success by:

1. **Execute spec_creation_v1 workflow**
   - Verify no todo_write calls made
   - Verify guidance fields present in all responses
   
2. **Execute spec_execution_v1 workflow**
   - Verify no todo_write calls made
   - Verify workflow completes successfully

3. **Measure response times**
   - Baseline: Before deployment
   - After: Confirm < 1ms overhead

4. **Monitor for errors**
   - Check MCP server logs for guidance injection warnings
   - Expect zero warnings (graceful degradation working)

**Success Criteria (srd.md Section 7.1) Met:** ✅

---

**End of Implementation Tasks**

