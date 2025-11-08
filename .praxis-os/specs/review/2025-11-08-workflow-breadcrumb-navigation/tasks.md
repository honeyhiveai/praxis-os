# Implementation Tasks

**Project:** Workflow Breadcrumb Navigation System  
**Date:** 2025-11-08  
**Status:** Draft - Pending Approval

---

## Time Estimates

- **Phase 1:** 1-2 hours (Foundation changes)
- **Phase 2:** 2-3 hours (Task count infrastructure)
- **Phase 3:** 3-4 hours (Breadcrumb generation)
- **Phase 4:** 3-4 hours (Testing & validation)
- **Total:** 9-13 hours (~1.5-2 days)

---

## Phase 1: Foundation Changes

**Objective:** Modify guidance module to support action-specific breadcrumbs while maintaining backward compatibility.

**Estimated Duration:** 1-2 hours

### Phase 1 Tasks

- [ ] **Task 1.1**: Modify add_workflow_guidance() function signature (S: 30 min)
  - Add optional `breadcrumb` parameter to function signature
  - Update docstring to document breadcrumb structure and usage
  - Verify function signature compatible with existing calls (breadcrumb=None default)
  
  **Acceptance Criteria:**
  - [ ] Function signature includes `breadcrumb: Optional[Dict[str, str]] = None` parameter
  - [ ] Docstring documents breadcrumb structure with example
  - [ ] Docstring explains recency bias positioning strategy
  - [ ] Zero pylint errors on modified file
  
- [ ] **Task 1.2**: Implement breadcrumb merging logic (M: 1 hour)
  - Update dict merging order: `{**WORKFLOW_GUIDANCE_FIELDS, **response, **breadcrumb}`
  - Ensure breadcrumb fields positioned last (recency bias)
  - Preserve static guidance fields at start
  - Verify Python 3.7+ dict ordering behavior maintained
  
  **Acceptance Criteria:**
  - [ ] Dict merging order: static guidance → response → breadcrumb (if provided)
  - [ ] Breadcrumb fields appear last in merged dict (verified via unit test)
  - [ ] Backward compatibility: breadcrumb=None returns response identical to current behavior
  - [ ] Zero pylint errors on modified file
  
- [ ] **Task 1.3**: Add guidance module unit tests (S: 30 min)
  - Test `add_workflow_guidance()` with breadcrumb=None (backward compatibility)
  - Test `add_workflow_guidance()` with breadcrumb dict (positioning)
  - Test field ordering (guidance first, response middle, breadcrumb last)
  - Verify no breaking changes to existing behavior
  
  **Acceptance Criteria:**
  - [ ] 3 unit tests added for guidance module
  - [ ] Test coverage for guidance.py ≥ 95%
  - [ ] All unit tests passing (pytest exit code 0)
  - [ ] Tests verify dict key ordering (Python 3.7+ insertion order)

---

## Phase 2: Task Count Infrastructure

**Objective:** Implement task count retrieval for both static and dynamic workflows to enable position-aware breadcrumb generation.

**Estimated Duration:** 2-3 hours

### Phase 2 Tasks

- [ ] **Task 2.1**: Implement WorkflowRenderer.get_task_count() for static workflows (M: 1.5 hours)
  - Add `get_task_count(workflow_type, phase)` method to WorkflowRenderer class
  - Use `pathlib.glob("task-*-*.md")` to count task files in phase directory
  - Return count of matching files
  - Add error handling for missing phase directory (raise RendererError with mkdir command)
  - Verify method returns correct count for existing workflows (spec_creation_v1)
  
  **Acceptance Criteria:**
  - [ ] `get_task_count()` method added to WorkflowRenderer class
  - [ ] Method returns correct count for spec_creation_v1 Phase 0 (5 tasks)
  - [ ] Raises `RendererError` with actionable `mkdir` command when phase directory not found
  - [ ] Method performance < 5ms for directories with < 50 files (from specs.md NFR-P1)
  - [ ] Zero pylint errors on modified file
  
- [ ] **Task 2.2**: Implement WorkflowEngine._get_task_count_for_phase() helper (M: 1 hour)
  - Add private `_get_task_count_for_phase(state, phase)` method to WorkflowEngine
  - Check `state.workflow_metadata.dynamic_phases` flag to route request
  - If static: Call `self.renderer.get_task_count(workflow_type, phase)`
  - If dynamic: Call `self.dynamic_registry.get_phase_metadata(phase)["task_count"]`
  - Add error handling with graceful degradation (log error, return None on failure)
  - Verify routing works for both static (spec_creation_v1) and dynamic (spec_execution_v1) workflows
  
  **Acceptance Criteria:**
  - [ ] `_get_task_count_for_phase()` helper method added to WorkflowEngine
  - [ ] Method correctly routes to `WorkflowRenderer.get_task_count()` for static workflows
  - [ ] Method correctly routes to `DynamicContentRegistry.get_phase_metadata()` for dynamic workflows
  - [ ] Graceful degradation: returns None on exception (workflow continues without breadcrumb)
  - [ ] Error logged at ERROR level when task count retrieval fails
  - [ ] Zero pylint errors on modified file
  
- [ ] **Task 2.3**: Add task count retrieval unit tests (S: 30 min)
  - Test `WorkflowRenderer.get_task_count()` with valid phase directory
  - Test `WorkflowRenderer.get_task_count()` with missing phase directory (error case)
  - Test `WorkflowEngine._get_task_count_for_phase()` for static workflow
  - Test `WorkflowEngine._get_task_count_for_phase()` for dynamic workflow
  - Verify graceful degradation on task count retrieval failure
  
  **Acceptance Criteria:**
  - [ ] 5 unit tests added for task count retrieval
  - [ ] Test coverage for new methods ≥ 90%
  - [ ] All unit tests passing (pytest exit code 0)
  - [ ] Error handling tested: RendererError raised correctly, graceful degradation verified

---

## Phase 3: Breadcrumb Generation

**Objective:** Modify workflow engine action handlers to generate and inject action-specific breadcrumbs using just-in-time disclosure pattern.

**Estimated Duration:** 3-4 hours

### Phase 3 Tasks

- [ ] **Task 3.1**: Modify start_workflow() for just-in-time disclosure (M: 45 min)
  - Remove `phase_content` from response dict (prevents early information leakage)
  - Generate breadcrumb: `{"⚡_NEXT_ACTION": "get_phase(phase=0)"}`
  - Pass breadcrumb to `add_workflow_guidance(response, breadcrumb=breadcrumb)`
  - Verify response no longer contains `phase_content` field
  - Verify `⚡_NEXT_ACTION` field appears at end of response
  
  **Acceptance Criteria:**
  - [ ] `phase_content` field removed from `start_workflow()` response
  - [ ] Breadcrumb `{"⚡_NEXT_ACTION": "get_phase(phase=0)"}` generated
  - [ ] Breadcrumb positioned last in response (verified via test)
  - [ ] Zero pylint errors on modified file
  
- [ ] **Task 3.2**: Modify get_phase() with task count aware breadcrumb (M: 1 hour)
  - Call `_get_task_count_for_phase(state, phase)` to get task count
  - If task_count > 0: Generate breadcrumb to first task
  - If task_count == 0: Generate breadcrumb to complete_phase (edge case)
  - Add `📊_PHASE_INFO` field: `"Phase {phase} has {task_count} tasks"`
  - Add `⚡_NEXT_ACTION` field with appropriate call
  - Pass breadcrumb to `add_workflow_guidance(response, breadcrumb=breadcrumb)`
  - Verify breadcrumb points to correct next action for both cases
  
- [ ] **Task 3.3**: Modify get_task() with dynamic position-aware breadcrumb (M: 1.5 hours)
  - Call `_get_task_count_for_phase(state, phase)` to get task count
  - If `task_number < task_count`: Generate breadcrumb to next task
  - If `task_number == task_count`: Generate breadcrumb to complete_phase (final task)
  - Add `🎯_CURRENT_POSITION` field: `"Task {task_number}/{task_count}"` (or `"Task {task_number}/{task_count} (final)"`)
  - Add `⚡_NEXT_ACTION` field with appropriate call
  - Pass breadcrumb to `add_workflow_guidance(response, breadcrumb=breadcrumb)`
  - Add graceful degradation if task count retrieval fails (continue without breadcrumb)
  - Verify breadcrumb dynamically adjusts based on position in phase
  
- [ ] **Task 3.4**: Modify complete_phase() with next phase breadcrumb (M: 45 min)
  - Check if workflow has more phases: `result.new_state.current_phase <= max_phase`
  - If more phases: Generate breadcrumb to next phase
  - If workflow complete: Generate celebration breadcrumb (no next action)
  - Add `✅_PHASE_COMPLETE` or `🎉_WORKFLOW_COMPLETE` field
  - Add `⚡_NEXT_ACTION` field (if more phases)
  - Pass breadcrumb to `add_workflow_guidance(response, breadcrumb=breadcrumb)`
  - Verify breadcrumb appears for multi-phase workflows and completion cases

---

## Phase 4: Testing & Validation

**Objective:** Validate breadcrumb behavior across all workflow types, ensure backward compatibility, and verify behavioral improvements.

**Estimated Duration:** 3-4 hours

### Phase 4 Tasks

- [ ] **Task 4.1**: Add breadcrumb generation unit tests (M: 1.5 hours)
  - Test `start_workflow()` breadcrumb (no phase_content, correct next action)
  - Test `get_phase()` breadcrumb with tasks (points to first task)
  - Test `get_phase()` breadcrumb with no tasks (points to complete_phase)
  - Test `get_task()` breadcrumb for middle task (points to next task)
  - Test `get_task()` breadcrumb for final task (points to complete_phase)
  - Test `complete_phase()` breadcrumb with more phases (points to next phase)
  - Test `complete_phase()` breadcrumb for workflow completion (celebration message)
  - Verify all breadcrumbs positioned last in response (recency bias)
  
- [ ] **Task 4.2**: Add integration tests for full workflow execution (M: 1.5 hours)
  - Test static workflow (spec_creation_v1) end-to-end with breadcrumbs
  - Test dynamic workflow (spec_execution_v1) end-to-end with breadcrumbs
  - Verify breadcrumbs appear in all responses throughout workflow
  - Verify `phase_content` removed from `start_workflow` response
  - Verify task count accuracy for both workflow types
  - Test graceful degradation when task count retrieval fails
  
- [ ] **Task 4.3**: Add backward compatibility tests (S: 45 min)
  - Test existing workflow sessions continue to work without modification
  - Test `add_workflow_guidance(response)` without breadcrumb parameter (no breaking change)
  - Test static guidance fields preserved in all responses
  - Verify compliant AI workflows not disrupted
  
- [ ] **Task 4.4**: Manual behavioral validation (S: 45 min)
  - Run workflow with AI agent (this session) and observe if breadcrumbs are followed
  - Track action sequences to verify sequential execution
  - Verify AI calls actions in breadcrumb-suggested order
  - Document breadcrumb following rate (target: >95%)

---

## Dependencies

### Phase Dependencies

**Phase 1 → Phase 2**  
Phase 2 (Task Count Infrastructure) depends on Phase 1 (Foundation Changes) being complete.  
Cannot implement task count helper method in engine without updated `add_workflow_guidance()` function that accepts breadcrumb parameter.

**Phase 2 → Phase 3**  
Phase 3 (Breadcrumb Generation) depends on Phase 2 (Task Count Infrastructure) being complete.  
Cannot generate position-aware breadcrumbs in action handlers without `_get_task_count_for_phase()` helper method and `WorkflowRenderer.get_task_count()`.

**Phase 3 → Phase 4**  
Phase 4 (Testing & Validation) depends on Phase 3 (Breadcrumb Generation) being complete.  
Cannot test breadcrumb behavior without breadcrumb generation implemented in all action handlers.

### Task Dependencies

**Linear Dependencies (Sequential):**
- Task 1.1 → Task 1.2 → Task 1.3 (Phase 1: Foundation changes must be sequential)
- Task 2.1 || Task 2.2 → Task 2.3 (Phase 2: Both renderer and engine methods needed before tests)
- Task 3.1 → Task 3.2 → Task 3.3 → Task 3.4 (Phase 3: Action handlers modified in dependency order)
- Task 4.1 || Task 4.2 || Task 4.3 → Task 4.4 (Phase 4: All tests must pass before behavioral validation)

**Parallel Tasks (Can Execute Simultaneously):**
- **Task 2.1 || Task 2.2**: WorkflowRenderer.get_task_count() and WorkflowEngine helper are independent
- **Task 4.1 || Task 4.2 || Task 4.3**: Unit tests, integration tests, and backward compatibility tests can run in parallel

**Cross-Phase Dependencies:**
- Task 2.2 depends on Task 1.2 (engine helper needs updated guidance function)
- Task 3.1 depends on Task 1.2 (start_workflow needs updated guidance function)
- Task 3.2 depends on Task 2.2 (get_phase needs task count helper)
- Task 3.3 depends on Task 2.2 (get_task needs task count helper)
- Task 4.1 depends on Tasks 3.1-3.4 (unit tests need breadcrumb generation implemented)

### Critical Path

```
Task 1.1 → Task 1.2 → Task 2.2 → Task 3.3 → Task 4.2
```

**Explanation:** This is the longest dependency chain. Any delay in these tasks delays the entire project.

- Task 1.1 (30 min): Modify guidance function signature
- Task 1.2 (1 hour): Implement breadcrumb merging logic
- Task 2.2 (1 hour): Implement engine task count helper
- Task 3.3 (1.5 hours): Modify get_task() with dynamic breadcrumb (most complex)
- Task 4.2 (1.5 hours): Integration tests for full workflow

**Critical Path Duration:** ~5.5 hours

**Total Project Duration:** ~9-13 hours (includes parallel work)

---

## Phase Validation Gates

### Phase 1 Validation Gate

**Before advancing to Phase 2:**
- [ ] All Phase 1 tasks completed (Tasks 1.1, 1.2, 1.3)
- [ ] All Phase 1 acceptance criteria met
- [ ] `add_workflow_guidance()` accepts optional `breadcrumb` parameter
- [ ] Breadcrumb merging logic implemented and tested
- [ ] 3 unit tests added with ≥95% coverage for guidance module
- [ ] All tests passing (pytest exit code 0)
- [ ] Zero pylint errors on modified files
- [ ] Backward compatibility verified (breadcrumb=None works)

### Phase 2 Validation Gate

**Before advancing to Phase 3:**
- [ ] All Phase 2 tasks completed (Tasks 2.1, 2.2, 2.3)
- [ ] All Phase 2 acceptance criteria met
- [ ] `WorkflowRenderer.get_task_count()` implemented for static workflows
- [ ] `WorkflowEngine._get_task_count_for_phase()` helper implemented
- [ ] Task count routing works for both static and dynamic workflows
- [ ] 5 unit tests added with ≥90% coverage for new methods
- [ ] All tests passing (pytest exit code 0)
- [ ] Zero pylint errors on modified files
- [ ] Graceful degradation verified (task count failure doesn't break workflow)
- [ ] Performance target met (<5ms for static workflows)

### Phase 3 Validation Gate

**Before advancing to Phase 4:**
- [ ] All Phase 3 tasks completed (Tasks 3.1, 3.2, 3.3, 3.4)
- [ ] All Phase 3 acceptance criteria met
- [ ] `start_workflow()` no longer returns `phase_content` (just-in-time disclosure)
- [ ] `get_phase()` generates task count aware breadcrumb
- [ ] `get_task()` generates dynamic position-aware breadcrumb
- [ ] `complete_phase()` generates next phase breadcrumb
- [ ] All breadcrumbs positioned last in response (recency bias)
- [ ] All action handlers call `add_workflow_guidance()` with breadcrumb
- [ ] Zero pylint errors on modified files
- [ ] Edge cases handled (no tasks in phase, final task, workflow complete)

### Phase 4 Validation Gate

**Before marking project complete:**
- [ ] All Phase 4 tasks completed (Tasks 4.1, 4.2, 4.3, 4.4)
- [ ] All Phase 4 acceptance criteria met
- [ ] Unit tests cover all breadcrumb generation scenarios (7+ test cases)
- [ ] Integration tests verify full workflow execution (static + dynamic)
- [ ] Backward compatibility tests pass (no breaking changes)
- [ ] Manual behavioral validation complete (breadcrumb following rate >95%)
- [ ] All test suites passing (pytest exit code 0)
- [ ] Test coverage ≥90% for modified code
- [ ] Zero pylint errors across all modified files
- [ ] Performance requirements met (NFR-P1, NFR-P2 from specs.md)

---

## Project Completion Criteria

**All criteria must be met before deployment:**

- [ ] **Functionality**: All 4 phases completed with validation gates passed
- [ ] **Quality**: All tests passing, ≥90% coverage, zero pylint errors
- [ ] **Performance**: Task count <5ms (static), breadcrumb generation <1ms
- [ ] **Backward Compatibility**: Existing workflows unaffected, no breaking changes
- [ ] **Behavioral Validation**: AI agents follow breadcrumbs sequentially (>95% rate)
- [ ] **Documentation**: Code comments added, docstrings updated
- [ ] **Code Review**: All changes reviewed and approved
- [ ] **Integration**: Changes work with both static (spec_creation_v1) and dynamic (spec_execution_v1) workflows
