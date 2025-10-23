# Implementation Tasks: aos_workflow Tool

**Spec:** `.agent-os/specs/review/2025-10-22-aos-workflow-tool/`  
**Target Completion:** 2 weeks  
**Implementation Strategy:** Clean cutover (remove existing tools, deploy new consolidated tool)

---

## Overview

This document breaks down the implementation of the `aos_workflow` consolidated tool into manageable phases with clear dependencies, acceptance criteria, and validation gates.

**Implementation Phases:**
1. **Foundation** - Core infrastructure and action dispatcher
2. **Discovery & Execution** - Workflow discovery and session execution actions
3. **Management & Recovery** - Session management and error recovery actions
4. **Testing & Documentation** - Comprehensive testing, documentation, and cutover
5. **Deployment & Validation** - Clean cutover, validation, and monitoring

---

## Phase 1: Foundation (Days 1-2)

**Objective:** Establish core infrastructure for consolidated tool.

**Dependencies:** None (starting from scratch)

### Task 1.1: Create Module Structure
**Priority:** Critical  
**Estimated Time:** 2 hours  
**Assignee:** Backend Developer

**Steps:**
1. Create `mcp_server/server/tools/workflow_tools.py`
2. Add module imports and dependencies
3. Create test file `tests/server/tools/test_workflow_tools.py`
4. Set up basic test fixtures

**Acceptance Criteria:**
- [ ] Module file exists with proper structure
- [ ] Can import WorkflowEngine and StateManager
- [ ] Test file runs (even with no tests yet)
- [ ] No circular import errors

**Validation:**
```bash
python -c "from mcp_server.server.tools.workflow_tools import *"
pytest tests/server/tools/test_workflow_tools.py -v
```

**Traceability:** NFR-M1 (Maintainability)

---

### Task 1.2: Implement Tool Registration Function
**Priority:** Critical  
**Estimated Time:** 3 hours  
**Assignee:** Backend Developer  
**Dependencies:** Task 1.1

**Steps:**
1. Create `register_workflow_tools()` function
2. Add MCP server integration (@mcp.tool() decorator)
3. Implement tool count return
4. Add integration with existing tool registry

**Acceptance Criteria:**
- [ ] Function registers exactly 1 tool
- [ ] Tool appears in MCP tools/list
- [ ] Tool metadata includes all 14 actions
- [ ] Registration integrates with existing server startup

**Validation:**
```bash
# Start MCP server and check tool count
python -m mcp_server
# Verify tools/list includes aos_workflow
```

**Traceability:** FR-001 (Single consolidated tool)

---

### Task 1.3: Implement Action Dispatcher
**Priority:** Critical  
**Estimated Time:** 4 hours  
**Assignee:** Backend Developer  
**Dependencies:** Task 1.2

**Steps:**
1. Create `aos_workflow()` async function with complete signature
2. Implement action validation (check against VALID_ACTIONS set)
3. Create ACTION_HANDLERS dict mapping actions to handlers
4. Implement parameter validation for each action
5. Add error handling with sanitized messages

**Acceptance Criteria:**
- [ ] Function signature matches specs.md Section 3.1
- [ ] Unknown action returns proper error with valid_actions list
- [ ] Parameter validation raises ValueError for missing required params
- [ ] Error responses include remediation guidance
- [ ] All 14 actions defined in ACTION_HANDLERS dict

**Validation:**
```python
# Test unknown action
result = aos_workflow(action="invalid_action")
assert result["status"] == "error"
assert "valid_actions" in result

# Test missing parameters
result = aos_workflow(action="start")  # Missing workflow_type, target_file
assert result["status"] == "error"
assert "workflow_type" in result["error"]
```

**Traceability:** FR-001, FR-007 (Validation), NFR-U1 (Error messages)

---

### Task 1.4: Implement Input Validation Helpers
**Priority:** High  
**Estimated Time:** 3 hours  
**Assignee:** Backend Developer  
**Dependencies:** Task 1.3

**Steps:**
1. Create `validate_session_id()` function
2. Create `validate_target_file()` function (path traversal protection)
3. Create `validate_evidence_size()` function
4. Add unit tests for all validation functions

**Acceptance Criteria:**
- [ ] Session ID validation rejects malformed IDs
- [ ] Path validation prevents directory traversal (../, absolute paths)
- [ ] Evidence size validation enforces 10MB limit
- [ ] All validation functions have comprehensive unit tests

**Validation:**
```python
# Test path traversal protection
with pytest.raises(ValueError, match="directory traversal"):
    validate_target_file("../../../etc/passwd")

# Test evidence size limit
large_evidence = {"data": "x" * (11 * 1024 * 1024)}
with pytest.raises(ValueError, match="too large"):
    validate_evidence_size(large_evidence)
```

**Traceability:** FR-007, NFR-S1 (Security)

---

**Phase 1 Validation Gate:**

Before advancing to Phase 2:
- [ ] All Phase 1 tasks completed
- [ ] Tool registration working (1 tool registered)
- [ ] Action dispatcher validates and routes correctly
- [ ] Input validation prevents security issues
- [ ] All unit tests passing (>= 15 tests)
- [ ] No linter errors

**Evidence Required:**
```bash
pytest tests/server/tools/test_workflow_tools.py -v --cov
# Expected: >= 15 tests, 100% coverage on validators
pylint mcp_server/server/tools/workflow_tools.py
# Expected: Score >= 9.0/10
```

---

## Phase 2: Discovery & Execution Actions (Days 3-5)

**Objective:** Implement workflow discovery and core execution actions.

**Dependencies:** Phase 1 complete

### Task 2.1: Implement list_workflows Action
**Priority:** Critical  
**Estimated Time:** 4 hours  
**Assignee:** Backend Developer  
**Dependencies:** Phase 1

**Steps:**
1. Create `_handle_list_workflows()` function
2. Implement workflow metadata loading from metadata.json files
3. Add category filtering logic
4. Implement metadata caching (lru_cache)
5. Add tests for discovery with/without filters

**Acceptance Criteria:**
- [ ] Returns all available workflows with metadata
- [ ] Category filter works correctly
- [ ] Response includes: workflow_type, description, category, phases, estimated_duration
- [ ] Metadata cached for performance (< 100ms response)
- [ ] Works with both `.agent-os/workflows/` and `universal/workflows/`

**Validation:**
```python
result = aos_workflow(action="list_workflows")
assert result["status"] == "success"
assert len(result["workflows"]) >= 2  # test_generation_v3, spec_creation_v1
assert all("workflow_type" in w for w in result["workflows"])

# Test filtering
result = aos_workflow(action="list_workflows", category="code_generation")
assert all(w["category"] == "code_generation" for w in result["workflows"])
```

**Traceability:** FR-010, Story 1

---

### Task 2.2: Implement start Action
**Priority:** Critical  
**Estimated Time:** 5 hours  
**Assignee:** Backend Developer  
**Dependencies:** Task 2.1

**Steps:**
1. Create `_handle_start()` function
2. Call `WorkflowEngine.start_workflow()`
3. Generate unique session_id
4. Return session_id + phase 1 content
5. Handle workflow not found errors
6. Add comprehensive tests

**Acceptance Criteria:**
- [ ] Creates new workflow session
- [ ] Returns unique session_id
- [ ] Returns Phase 1 content immediately
- [ ] Session state file created in `.agent-os/state/workflows/`
- [ ] Validates workflow_type exists
- [ ] Response time < 500ms

**Validation:**
```python
result = aos_workflow(
    action="start",
    workflow_type="test_generation_v3",
    target_file="src/test.py"
)
assert result["status"] == "success"
assert "session_id" in result
assert result["current_phase"] == 1
assert "phase_content" in result

# Verify state file created
import os
state_file = f".agent-os/state/workflows/{result['session_id']}.json"
assert os.path.exists(state_file)
```

**Traceability:** FR-002, FR-008, Story 2

---

### Task 2.3: Implement get_phase Action
**Priority:** Critical  
**Estimated Time:** 3 hours  
**Assignee:** Backend Developer  
**Dependencies:** Task 2.2

**Steps:**
1. Create `_handle_get_phase()` function
2. Load session state
3. Call `WorkflowEngine.get_current_phase()`
4. Return phase content with artifacts from previous phases
5. Add tests for various phase states

**Acceptance Criteria:**
- [ ] Returns current phase content
- [ ] Includes artifacts from previous completed phases
- [ ] Session not found returns proper error
- [ ] Response includes current_phase, total_phases, phase_content

**Validation:**
```python
# Start session first
session = aos_workflow(action="start", workflow_type="test_gen_v3", target_file="test.py")

result = aos_workflow(action="get_phase", session_id=session["session_id"])
assert result["status"] == "success"
assert result["current_phase"] == 1
assert "phase_content" in result
```

**Traceability:** FR-002, Story 5

---

### Task 2.4: Implement get_task Action
**Priority:** High  
**Estimated Time:** 4 hours  
**Assignee:** Backend Developer  
**Dependencies:** Task 2.3

**Steps:**
1. Create `_handle_get_task()` function
2. Call `WorkflowEngine.get_task()`
3. Return task content with execution steps
4. Validate phase and task_number are valid
5. Add tests for task retrieval

**Acceptance Criteria:**
- [ ] Returns detailed task content
- [ ] Includes execution steps with commands
- [ ] Validates phase and task_number are in range
- [ ] Returns artifacts_to_produce list

**Validation:**
```python
session = aos_workflow(action="start", workflow_type="test_gen_v3", target_file="test.py")

result = aos_workflow(
    action="get_task",
    session_id=session["session_id"],
    phase=1,
    task_number=1
)
assert result["status"] == "success"
assert "task_content" in result
assert "execution_steps" in result["task_content"]
```

**Traceability:** FR-006, Story 5

---

### Task 2.5: Implement complete_phase Action
**Priority:** Critical  
**Estimated Time:** 6 hours  
**Assignee:** Backend Developer  
**Dependencies:** Task 2.4

**Steps:**
1. Create `_handle_complete_phase()` function
2. Validate evidence against checkpoint criteria
3. Call `WorkflowEngine.complete_phase()`
4. Handle checkpoint passed: advance to next phase
5. Handle checkpoint failed: return missing evidence
6. Update session state with artifacts
7. Add comprehensive tests for success/failure cases

**Acceptance Criteria:**
- [ ] Validates evidence against checkpoint
- [ ] Advances phase on checkpoint pass
- [ ] Returns missing evidence on checkpoint fail
- [ ] Updates session state with artifacts
- [ ] Returns next phase content on success
- [ ] Returns remediation guidance on failure

**Validation:**
```python
session = aos_workflow(action="start", workflow_type="test_gen_v3", target_file="test.py")

# Test success case
result = aos_workflow(
    action="complete_phase",
    session_id=session["session_id"],
    phase=1,
    evidence={"code_structure": {...}, "test_candidates": [...]}
)
assert result["status"] == "success"
assert result["checkpoint_passed"] == True
assert result["phase_completed"] == 1
assert "next_phase" in result

# Test failure case
result = aos_workflow(
    action="complete_phase",
    session_id=session["session_id"],
    phase=1,
    evidence={"code_structure": {...}}  # Missing test_candidates
)
assert result["status"] == "error"
assert result["checkpoint_passed"] == False
assert "missing_evidence" in result
```

**Traceability:** FR-002, FR-007, Story 2

---

### Task 2.6: Implement get_state Action
**Priority:** High  
**Estimated Time:** 2 hours  
**Assignee:** Backend Developer  
**Dependencies:** Task 2.5

**Steps:**
1. Create `_handle_get_state()` function
2. Call `WorkflowEngine.get_workflow_state()`
3. Return complete session state
4. Add tests

**Acceptance Criteria:**
- [ ] Returns complete workflow state
- [ ] Includes all artifacts from completed phases
- [ ] Includes session metadata (created_at, last_updated, status)
- [ ] Indicates if session is resume_capable

**Validation:**
```python
session = aos_workflow(action="start", workflow_type="test_gen_v3", target_file="test.py")

result = aos_workflow(action="get_state", session_id=session["session_id"])
assert result["status"] == "success"
assert "workflow_type" in result
assert "current_phase" in result
assert "artifacts" in result
assert "resume_capable" in result
```

**Traceability:** FR-002, FR-003, Story 6

---

**Phase 2 Validation Gate:**

Before advancing to Phase 3:
- [ ] All Phase 2 tasks completed
- [ ] Discovery action (list_workflows) working
- [ ] All 5 execution actions working
- [ ] Checkpoint validation enforced
- [ ] State persistence working
- [ ] All tests passing (>= 35 tests total)
- [ ] No linter errors

**Evidence Required:**
```bash
pytest tests/server/tools/test_workflow_tools.py::test_list_workflows -v
pytest tests/server/tools/test_workflow_tools.py::test_execution_actions -v
# Expected: All tests green
```

---

## Phase 3: Management & Recovery Actions (Days 6-8)

**Objective:** Implement session management and error recovery actions.

**Dependencies:** Phase 2 complete

### Task 3.1: Implement list_sessions Action
**Priority:** High  
**Estimated Time:** 3 hours  
**Assignee:** Backend Developer  
**Dependencies:** Phase 2

**Steps:**
1. Create `_handle_list_sessions()` function
2. Call `StateManager.list_sessions()`
3. Implement status filtering
4. Optimize for performance (only load summary fields)
5. Add tests

**Acceptance Criteria:**
- [ ] Lists all sessions with summary info
- [ ] Status filter works (active, completed, failed, paused)
- [ ] Returns session_id, workflow_type, current_phase, status, timestamps
- [ ] Performance: < 200ms for 100 sessions

**Validation:**
```python
# Create multiple sessions
for i in range(3):
    aos_workflow(action="start", workflow_type="test_gen_v3", target_file=f"test_{i}.py")

result = aos_workflow(action="list_sessions")
assert result["status"] == "success"
assert result["count"] >= 3

# Test filtering
result = aos_workflow(action="list_sessions", status="active")
assert all(s["status"] == "active" for s in result["sessions"])
```

**Traceability:** FR-003, Story 3

---

### Task 3.2: Implement get_session Action
**Priority:** High  
**Estimated Time:** 2 hours  
**Assignee:** Backend Developer  
**Dependencies:** Task 3.1

**Steps:**
1. Create `_handle_get_session()` function
2. Call `StateManager.get_session()`
3. Return detailed session info with history
4. Add tests

**Acceptance Criteria:**
- [ ] Returns complete session details
- [ ] Includes phase_history with durations
- [ ] Includes options passed at start
- [ ] Session not found returns proper error

**Validation:**
```python
session = aos_workflow(action="start", workflow_type="test_gen_v3", target_file="test.py")

result = aos_workflow(action="get_session", session_id=session["session_id"])
assert result["status"] == "success"
assert "session" in result
assert "phase_history" in result["session"]
```

**Traceability:** FR-003, Story 3

---

### Task 3.3: Implement delete_session Action
**Priority:** High  
**Estimated Time:** 2 hours  
**Assignee:** Backend Developer  
**Dependencies:** Task 3.2

**Steps:**
1. Create `_handle_delete_session()` function
2. Call `StateManager.delete_session()`
3. Remove state file from filesystem
4. Add optional reason parameter
5. Add tests

**Acceptance Criteria:**
- [ ] Deletes session state file
- [ ] Returns confirmation with cleanup details
- [ ] Optional reason parameter recorded
- [ ] Idempotent (deleting non-existent session doesn't error)

**Validation:**
```python
session = aos_workflow(action="start", workflow_type="test_gen_v3", target_file="test.py")
session_id = session["session_id"]

result = aos_workflow(action="delete_session", session_id=session_id, reason="Test cleanup")
assert result["status"] == "success"
assert result["deleted"] == True

# Verify state file removed
import os
state_file = f".agent-os/state/workflows/{session_id}.json"
assert not os.path.exists(state_file)
```

**Traceability:** FR-003, Story 3

---

### Task 3.4: Implement pause Action
**Priority:** Medium  
**Estimated Time:** 3 hours  
**Assignee:** Backend Developer  
**Dependencies:** Task 3.3

**Steps:**
1. Create `_handle_pause()` function
2. Update session status to "paused"
3. Save checkpoint with timestamp and note
4. Add tests for pause/resume flow

**Acceptance Criteria:**
- [ ] Updates session status to "paused"
- [ ] Saves checkpoint_note if provided
- [ ] Records paused_at timestamp
- [ ] Can only pause "active" sessions

**Validation:**
```python
session = aos_workflow(action="start", workflow_type="test_gen_v3", target_file="test.py")

result = aos_workflow(
    action="pause",
    session_id=session["session_id"],
    checkpoint_note="Waiting for review"
)
assert result["status"] == "success"
assert result["paused"] == True
assert result["resume_capable"] == True
```

**Traceability:** FR-003, Story 3

---

### Task 3.5: Implement resume Action
**Priority:** Medium  
**Estimated Time:** 3 hours  
**Assignee:** Backend Developer  
**Dependencies:** Task 3.4

**Steps:**
1. Create `_handle_resume()` function
2. Update session status back to "active"
3. Calculate paused duration
4. Return current phase content
5. Add tests

**Acceptance Criteria:**
- [ ] Updates session status to "active"
- [ ] Returns current phase content
- [ ] Calculates paused_duration_seconds
- [ ] Can only resume "paused" sessions

**Validation:**
```python
session = aos_workflow(action="start", workflow_type="test_gen_v3", target_file="test.py")
aos_workflow(action="pause", session_id=session["session_id"])

result = aos_workflow(action="resume", session_id=session["session_id"])
assert result["status"] == "success"
assert result["resumed"] == True
assert result["current_phase"] == 1
assert "paused_duration_seconds" in result
```

**Traceability:** FR-003, Story 3

---

### Task 3.6: Implement retry_phase Action
**Priority:** High  
**Estimated Time:** 4 hours  
**Assignee:** Backend Developer  
**Dependencies:** Task 3.5

**Steps:**
1. Create `_handle_retry_phase()` function
2. Call `WorkflowEngine.retry_phase()`
3. Implement evidence reset logic
4. Return phase content with previous errors
5. Add tests

**Acceptance Criteria:**
- [ ] Retries specified phase
- [ ] Optionally resets evidence if reset_evidence=True
- [ ] Returns phase content
- [ ] Includes previous_errors in response

**Validation:**
```python
session = aos_workflow(action="start", workflow_type="test_gen_v3", target_file="test.py")
# Simulate failure
aos_workflow(action="complete_phase", session_id=session["session_id"], phase=1, evidence={})

result = aos_workflow(action="retry_phase", session_id=session["session_id"], phase=1)
assert result["status"] == "success"
assert result["retrying"] == True
assert "phase_content" in result
```

**Traceability:** FR-004, Story 4

---

### Task 3.7: Implement rollback Action
**Priority:** High  
**Estimated Time:** 4 hours  
**Assignee:** Backend Developer  
**Dependencies:** Task 3.6

**Steps:**
1. Create `_handle_rollback()` function
2. Call `WorkflowEngine.rollback()`
3. Clear artifacts from rolled-back phases
4. Return phase content at rollback target
5. Add tests

**Acceptance Criteria:**
- [ ] Rolls back to specified phase
- [ ] Clears artifacts from phases > to_phase
- [ ] Updates completed_phases list
- [ ] Returns phase content at target phase

**Validation:**
```python
session = aos_workflow(action="start", workflow_type="test_gen_v3", target_file="test.py")
# Complete phase 1, advance to phase 2
aos_workflow(action="complete_phase", session_id=session["session_id"], phase=1, evidence={...})

result = aos_workflow(action="rollback", session_id=session["session_id"], to_phase=1)
assert result["status"] == "success"
assert result["rolled_back"] == True
assert result["to_phase"] == 1
assert result["from_phase"] == 2
```

**Traceability:** FR-004, Story 4

---

### Task 3.8: Implement get_errors Action
**Priority:** Medium  
**Estimated Time:** 2 hours  
**Assignee:** Backend Developer  
**Dependencies:** Task 3.7

**Steps:**
1. Create `_handle_get_errors()` function
2. Return error log from session state
3. Add tests

**Acceptance Criteria:**
- [ ] Returns all errors for session
- [ ] Each error includes phase, timestamp, error_type, message, details
- [ ] Returns empty list if no errors
- [ ] Includes error_count and last_error timestamp

**Validation:**
```python
session = aos_workflow(action="start", workflow_type="test_gen_v3", target_file="test.py")
# Cause an error
aos_workflow(action="complete_phase", session_id=session["session_id"], phase=1, evidence={})

result = aos_workflow(action="get_errors", session_id=session["session_id"])
assert result["status"] == "success"
assert result["error_count"] >= 1
assert len(result["errors"]) >= 1
```

**Traceability:** FR-004, Story 4, Story 6

---

**Phase 3 Validation Gate:**

Before advancing to Phase 4:
- [ ] All Phase 3 tasks completed
- [ ] All 5 management actions working
- [ ] All 3 recovery actions working
- [ ] Pause/resume flow working
- [ ] Error tracking functional
- [ ] All tests passing (>= 55 tests total)
- [ ] No linter errors

**Evidence Required:**
```bash
pytest tests/server/tools/test_workflow_tools.py::test_management_actions -v
pytest tests/server/tools/test_workflow_tools.py::test_recovery_actions -v
# Expected: All tests green
```

---

## Phase 4: Testing & Documentation (Days 9-11)

**Objective:** Comprehensive testing, security validation, performance testing, and documentation.

**Dependencies:** Phase 3 complete

### Task 4.1: Security Testing
**Priority:** Critical  
**Estimated Time:** 6 hours  
**Assignee:** Backend Developer  
**Dependencies:** Phase 3

**Steps:**
1. Implement path traversal attack tests
2. Implement evidence size limit tests
3. Implement session ID validation tests
4. Implement concurrency safety tests
5. Add input fuzzing tests

**Acceptance Criteria:**
- [ ] Path traversal attempts rejected
- [ ] Oversized evidence rejected (> 10MB)
- [ ] Malformed session IDs rejected
- [ ] Concurrent modifications handled safely
- [ ] All security tests passing

**Validation:**
```bash
pytest tests/server/tools/test_workflow_tools_security.py -v
# Expected: >= 20 security tests, all passing
```

**Traceability:** NFR-S1, NFR-S2

---

### Task 4.2: Performance Testing
**Priority:** High  
**Estimated Time:** 4 hours  
**Assignee:** Backend Developer  
**Dependencies:** Phase 3

**Steps:**
1. Implement response time tests (< 100ms discovery, < 500ms execution)
2. Implement memory usage tests (< 50MB for active sessions)
3. Implement scalability tests (100+ concurrent sessions)
4. Implement cache efficiency tests
5. Add performance benchmarks to CI

**Acceptance Criteria:**
- [ ] list_workflows < 100ms
- [ ] start action < 500ms
- [ ] Memory usage < 50MB for 50 sessions
- [ ] 100+ concurrent sessions supported
- [ ] Cache hit rate > 90% for repeated queries

**Validation:**
```bash
pytest tests/server/tools/test_workflow_tools_performance.py -v
# Expected: All performance targets met
```

**Traceability:** NFR-P1, NFR-P2, NFR-P3, NFR-Sc1

---

### Task 4.3: Integration Testing
**Priority:** High  
**Estimated Time:** 5 hours  
**Assignee:** Backend Developer  
**Dependencies:** Phase 3

**Steps:**
1. Implement end-to-end workflow tests
2. Test complete workflow from start to completion
3. Test error recovery flows
4. Test pause/resume flows
5. Test rollback scenarios

**Acceptance Criteria:**
- [ ] Complete workflow (start → multiple phases → complete) works
- [ ] Error recovery flow works (fail → retry → succeed)
- [ ] Pause/resume preserves state correctly
- [ ] Rollback correctly resets state

**Validation:**
```bash
pytest tests/integration/test_aos_workflow_e2e.py -v
# Expected: >= 10 integration tests, all passing
```

**Traceability:** All FRs, All NFRs

---

### Task 4.4: Tool Documentation
**Priority:** High  
**Estimated Time:** 4 hours  
**Assignee:** Technical Writer / Backend Developer  
**Dependencies:** Phase 3

**Steps:**
1. Create comprehensive tool docstring
2. Add usage examples for all 14 actions
3. Document error scenarios with remediation
4. Create migration guide from old tools
5. Update MCP server documentation

**Acceptance Criteria:**
- [ ] Tool docstring complete with all actions
- [ ] Usage examples for each action
- [ ] Error scenarios documented
- [ ] Migration guide created
- [ ] Documentation reviewed and approved

**Deliverables:**
- Updated docstring in `workflow_tools.py`
- Migration guide: `.agent-os/specs/review/2025-10-22-aos-workflow-tool/MIGRATION.md`

**Traceability:** NFR-U1, NFR-M1

---

### Task 4.5: Remove Old Tools (Clean Cutover Prep)
**Priority:** Critical  
**Estimated Time:** 3 hours  
**Assignee:** Backend Developer  
**Dependencies:** Phase 3

**Steps:**
1. Identify all existing workflow tools to remove
2. Create removal checklist
3. Prepare cleanup script
4. Document breaking changes
5. Create pre-cutover validation script

**Acceptance Criteria:**
- [ ] List of tools to remove identified
- [ ] Cleanup script created and tested in dev
- [ ] Breaking changes documented
- [ ] Pre-cutover validation script ready

**Tools to Remove:**
- `start_workflow`
- `get_current_phase`
- `get_task`
- `complete_phase`
- `get_workflow_state`
- Any other fragmented workflow tools

**Traceability:** FR-009 (Clean cutover)

---

**Phase 4 Validation Gate:**

Before advancing to Phase 5:
- [ ] All Phase 4 tasks completed
- [ ] Security tests passing (>= 20 tests)
- [ ] Performance tests passing (all targets met)
- [ ] Integration tests passing (>= 10 tests)
- [ ] Documentation complete
- [ ] Old tool removal prepared
- [ ] Total test count >= 85 tests
- [ ] Test coverage >= 90%

**Evidence Required:**
```bash
pytest tests/ -v --cov=mcp_server.server.tools.workflow_tools --cov-report=term-missing
# Expected: >= 85 tests, >= 90% coverage
```

---

## Phase 5: Deployment & Validation (Days 12-14)

**Objective:** Deploy consolidated tool, remove old tools, validate in production, monitor performance.

**Dependencies:** Phase 4 complete

### Task 5.1: Staging Deployment
**Priority:** Critical  
**Estimated Time:** 3 hours  
**Assignee:** DevOps / Backend Developer  
**Dependencies:** Phase 4

**Steps:**
1. Deploy to staging environment
2. Run full test suite in staging
3. Validate tool registration
4. Test discovery via tools/list
5. Run smoke tests

**Acceptance Criteria:**
- [ ] Deployed to staging successfully
- [ ] All tests passing in staging
- [ ] Tool appears in tools/list
- [ ] Smoke tests passing

**Validation:**
```bash
# In staging environment
pytest tests/ -v --cov
# Expected: All tests green
```

**Traceability:** NFR-Co1 (Compatibility)

---

### Task 5.2: Clean Cutover Execution
**Priority:** Critical  
**Estimated Time:** 2 hours  
**Assignee:** Backend Developer  
**Dependencies:** Task 5.1

**Steps:**
1. Back up current tool registry
2. Execute cleanup script to remove old tools
3. Restart MCP server
4. Verify tool count reduced
5. Verify aos_workflow registered

**Acceptance Criteria:**
- [ ] Old tools removed successfully
- [ ] aos_workflow is only workflow tool
- [ ] Tool count reduced by ~17-18 tools
- [ ] No tool registration errors
- [ ] Server restarts cleanly

**Validation:**
```bash
# Before cutover: count tools
curl localhost:8000/tools/list | jq '.tools | length'  # ~24 tools

# After cutover:
curl localhost:8000/tools/list | jq '.tools | length'  # ~6 tools (down from 24)
curl localhost:8000/tools/list | jq '.tools[] | select(.name == "aos_workflow")'
# Expected: aos_workflow present
```

**Traceability:** FR-009 (Clean cutover)

---

### Task 5.3: Production Deployment
**Priority:** Critical  
**Estimated Time:** 2 hours  
**Assignee:** DevOps / Backend Developer  
**Dependencies:** Task 5.2

**Steps:**
1. Deploy to production environment
2. Execute clean cutover
3. Monitor error logs
4. Validate first production workflow execution
5. Monitor performance metrics

**Acceptance Criteria:**
- [ ] Deployed to production successfully
- [ ] Clean cutover executed
- [ ] No critical errors in logs
- [ ] First workflow execution successful
- [ ] Performance metrics within targets

**Validation:**
```bash
# Test production deployment
curl https://api.production.com/tools/list | jq '.tools[] | select(.name == "aos_workflow")'
# Expected: aos_workflow present

# Test workflow execution
# (Manual test with real workflow)
```

**Traceability:** NFR-Co1, NFR-R2 (Reliability)

---

### Task 5.4: Performance Monitoring Setup
**Priority:** High  
**Estimated Time:** 3 hours  
**Assignee:** DevOps / Backend Developer  
**Dependencies:** Task 5.3

**Steps:**
1. Set up performance metrics collection
2. Create monitoring dashboard
3. Set up alerts for performance degradation
4. Monitor action latencies
5. Monitor error rates

**Acceptance Criteria:**
- [ ] Metrics collection active
- [ ] Dashboard shows action latencies, error rates, session counts
- [ ] Alerts configured for:
  - Response time > 1s
  - Error rate > 5%
  - Memory usage > 100MB
- [ ] Metrics retained for 30 days

**Validation:**
- Dashboard accessible and showing metrics
- Test alert by simulating high latency

**Traceability:** NFR-P1, NFR-P2, NFR-Sc2

---

### Task 5.5: Post-Deployment Validation
**Priority:** Critical  
**Estimated Time:** 4 hours  
**Assignee:** QA / Backend Developer  
**Dependencies:** Task 5.4

**Steps:**
1. Run comprehensive production smoke tests
2. Execute at least 3 complete workflows
3. Test all 14 actions in production
4. Validate performance targets met
5. Validate error handling
6. Generate validation report

**Acceptance Criteria:**
- [ ] All 14 actions tested in production
- [ ] 3+ complete workflows executed successfully
- [ ] Performance targets met (< 100ms discovery, < 500ms execution)
- [ ] Error handling working as expected
- [ ] Validation report generated

**Validation Report Template:**
```markdown
# aos_workflow Production Validation Report

## Test Execution
- Date: YYYY-MM-DD
- Environment: Production
- Tester: Name

## Test Results
- [ ] All 14 actions tested ✅/❌
- [ ] Discovery actions (1): ✅/❌
- [ ] Execution actions (5): ✅/❌
- [ ] Management actions (5): ✅/❌
- [ ] Recovery actions (3): ✅/❌

## Performance Metrics
- list_workflows: XXms (target: < 100ms)
- start: XXms (target: < 500ms)
- complete_phase: XXms (target: < 500ms)

## Issues Found
(List any issues discovered)

## Recommendation
✅ Approve for production use
❌ Rollback required (explain)
```

**Traceability:** All FRs, All NFRs

---

### Task 5.6: Update Documentation & Communication
**Priority:** High  
**Estimated Time:** 3 hours  
**Assignee:** Technical Writer / Backend Developer  
**Dependencies:** Task 5.5

**Steps:**
1. Update main README with aos_workflow usage
2. Update Agent OS documentation site
3. Create announcement/changelog
4. Update any dependent workflows
5. Send deployment notification

**Acceptance Criteria:**
- [ ] README updated
- [ ] Documentation site updated
- [ ] Changelog created
- [ ] Team notified
- [ ] Migration guide published

**Deliverables:**
- Updated `README.md`
- Updated docs site
- `CHANGELOG.md` entry
- Migration guide published

**Traceability:** NFR-M1, NFR-U1

---

**Phase 5 Validation Gate (Final):**

Project complete when:
- [ ] All Phase 5 tasks completed
- [ ] Deployed to production
- [ ] Clean cutover executed (old tools removed)
- [ ] Post-deployment validation passed
- [ ] Performance monitoring active
- [ ] Documentation updated
- [ ] Team notified
- [ ] No critical issues in production

**Final Evidence:**
```bash
# Verify production deployment
curl https://api.production.com/tools/list | jq '.tools | length'
# Expected: ~6 tools (down from ~24)

# Verify aos_workflow working
# (Manual workflow execution test)

# Check monitoring dashboard
# Expected: Green metrics, no alerts
```

**Sign-off Required:**
- [ ] Tech Lead
- [ ] Product Manager
- [ ] QA Lead

---

## Dependencies Graph

```
Phase 1: Foundation
├─ Task 1.1: Module Structure
├─ Task 1.2: Registration ← Task 1.1
├─ Task 1.3: Dispatcher ← Task 1.2
└─ Task 1.4: Validation ← Task 1.3

Phase 2: Discovery & Execution ← Phase 1
├─ Task 2.1: list_workflows
├─ Task 2.2: start ← Task 2.1
├─ Task 2.3: get_phase ← Task 2.2
├─ Task 2.4: get_task ← Task 2.3
├─ Task 2.5: complete_phase ← Task 2.4
└─ Task 2.6: get_state ← Task 2.5

Phase 3: Management & Recovery ← Phase 2
├─ Task 3.1: list_sessions
├─ Task 3.2: get_session ← Task 3.1
├─ Task 3.3: delete_session ← Task 3.2
├─ Task 3.4: pause ← Task 3.3
├─ Task 3.5: resume ← Task 3.4
├─ Task 3.6: retry_phase ← Task 3.5
├─ Task 3.7: rollback ← Task 3.6
└─ Task 3.8: get_errors ← Task 3.7

Phase 4: Testing & Documentation ← Phase 3
├─ Task 4.1: Security Testing
├─ Task 4.2: Performance Testing
├─ Task 4.3: Integration Testing
├─ Task 4.4: Documentation
└─ Task 4.5: Clean Cutover Prep

Phase 5: Deployment & Validation ← Phase 4
├─ Task 5.1: Staging Deployment
├─ Task 5.2: Clean Cutover ← Task 5.1
├─ Task 5.3: Production Deployment ← Task 5.2
├─ Task 5.4: Monitoring Setup ← Task 5.3
├─ Task 5.5: Post-Deployment Validation ← Task 5.4
└─ Task 5.6: Documentation & Communication ← Task 5.5
```

---

## Risk Management

### High Risks

**Risk 1: WorkflowEngine API Changes Required**
- **Probability:** Medium
- **Impact:** High
- **Mitigation:** Review WorkflowEngine API early (Phase 1); if changes needed, create separate PR
- **Contingency:** Implement adapter layer if API can't be modified

**Risk 2: Performance Targets Not Met**
- **Probability:** Low
- **Impact:** Medium
- **Mitigation:** Implement caching early (Phase 2); performance test continuously
- **Contingency:** Optimize hot paths, add more aggressive caching

**Risk 3: Clean Cutover Breaking Existing Users**
- **Probability:** Low
- **Impact:** High
- **Mitigation:** Comprehensive testing (Phase 4); clear migration guide
- **Contingency:** Emergency rollback script prepared; old tools archived not deleted

### Medium Risks

**Risk 4: Concurrency Issues in Production**
- **Probability:** Medium
- **Impact:** Medium
- **Mitigation:** File locking implementation (Phase 1); concurrency tests (Phase 4)
- **Contingency:** Add optimistic locking as backup mechanism

**Risk 5: Large Evidence Payloads Causing Memory Issues**
- **Probability:** Low
- **Impact:** Medium
- **Mitigation:** Evidence size validation (10MB limit); streaming for large states
- **Contingency:** Implement evidence compression

---

## Success Criteria

**Technical Success:**
- [ ] All 14 actions implemented and tested
- [ ] Test coverage >= 90%
- [ ] Performance targets met (< 100ms discovery, < 500ms execution)
- [ ] Security tests passing
- [ ] Zero critical bugs in production

**Business Success:**
- [ ] Tool count reduced from ~24 to ~6
- [ ] Workflow tool surface consolidated into 1 tool
- [ ] AI agent performance improved (fewer tools = better LLM performance)
- [ ] Maintainability improved (single codebase vs 17 tools)

**User Success:**
- [ ] All existing workflows continue to work
- [ ] Workflow discovery improved (list_workflows action)
- [ ] Error messages improved (with remediation)
- [ ] Documentation clear and comprehensive

---

## Timeline Summary

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| Phase 1: Foundation | 2 days | Module structure, registration, dispatcher, validation |
| Phase 2: Discovery & Execution | 3 days | 1 discovery action, 5 execution actions |
| Phase 3: Management & Recovery | 3 days | 5 management actions, 3 recovery actions |
| Phase 4: Testing & Documentation | 3 days | Security tests, performance tests, integration tests, docs |
| Phase 5: Deployment & Validation | 3 days | Staging, production deployment, clean cutover, validation |
| **Total** | **14 days (2 weeks)** | **Consolidated aos_workflow tool in production** |

---

**Document Version:** 1.0  
**Last Updated:** 2025-10-23  
**Status:** Ready for Implementation

