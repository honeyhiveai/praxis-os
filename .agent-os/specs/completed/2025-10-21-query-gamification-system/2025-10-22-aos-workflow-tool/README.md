# Specification: aos_workflow Consolidated Tool

**Status:** 🟡 In Review  
**Created:** 2025-10-22  
**Target Release:** v1.0  
**Estimated Effort:** 2 weeks (14 days)

---

## Executive Summary

This specification defines the consolidation of 17+ fragmented workflow management tools into a single, powerful `aos_workflow` tool, following the proven `aos_browser` pattern. This consolidation will dramatically improve AI agent performance, reduce cognitive load, and enhance maintainability.

**Problem:** Agent OS currently has ~24 MCP tools, with 17+ dedicated to workflow operations. This high tool count degrades LLM performance by 85% and creates a fragmented, inconsistent interface.

**Solution:** Consolidate all workflow operations into a single `aos_workflow` tool with 14 actions, reducing total tool count from ~24 to ~6 (optimal range for LLM performance).

**Impact:** 
- **Performance:** Reduce tool count by ~75% (24 → 6 tools)
- **Consistency:** Single interface following aos_browser pattern
- **Maintainability:** One codebase vs 17+ scattered tools
- **Discoverability:** Built-in workflow discovery (`list_workflows` action)

---

## Key Features

### 1. Consolidated Action-Based Interface
Single tool with 14 actions organized by category:
- **Discovery (1 action):** list_workflows
- **Execution (5 actions):** start, get_phase, get_task, complete_phase, get_state
- **Management (5 actions):** list_sessions, get_session, delete_session, pause, resume
- **Recovery (3 actions):** retry_phase, rollback, get_errors

### 2. Workflow Discovery
AI agents can dynamically discover available workflows without hardcoding:
```python
# Discover workflows
workflows = aos_workflow(action="list_workflows")
# Returns: test_generation_v3, spec_creation_v1, etc.

# Filter by category
code_gen_workflows = aos_workflow(action="list_workflows", category="code_generation")
```

### 3. Clean Cutover Strategy
No deprecation period or compatibility wrappers:
- Remove old tools immediately
- Deploy new consolidated tool
- Clear, simple interface

### 4. Zero Workflow Engine Modifications
Delegates to existing `WorkflowEngine` and `StateManager` - no changes to core workflow logic required.

---

## Business Value

### Improved AI Agent Performance
- **Current:** 24 tools = 85% performance degradation
- **Target:** 6 tools = 95% performance (optimal range)
- **Result:** Faster, more accurate AI responses

### Simplified Maintenance
- **Before:** 17+ separate tool files to maintain
- **After:** 1 consolidated file with clear organization
- **Result:** Easier to debug, test, and extend

### Enhanced User Experience
- **Discovery:** Agents can find workflows dynamically
- **Consistency:** Same pattern as aos_browser (familiar)
- **Error Messages:** Clear remediation guidance
- **Result:** Better usability for AI agents

### Cost Reduction
- **Fewer Tools:** Reduced context size for LLM
- **Better Performance:** Faster execution = lower costs
- **Easier Maintenance:** Less developer time spent on workflow tools

---

## Technical Highlights

### Architecture
- **Pattern:** Action-based dispatch (like aos_browser)
- **Implementation:** Single `aos_workflow()` function with `action` parameter
- **Dependencies:** Delegates to existing WorkflowEngine and StateManager
- **State Management:** File-based JSON persistence in `.agent-os/state/workflows/`

### Security
- **Input Validation:** Path traversal protection, session ID validation
- **Resource Limits:** 10MB evidence size limit, 100 concurrent sessions max
- **Error Sanitization:** No sensitive information exposed
- **File Locking:** Concurrency-safe state updates

### Performance
- **Discovery:** < 100ms (cached metadata)
- **Execution:** < 500ms (start, complete_phase)
- **Memory:** < 50MB for active sessions
- **Scalability:** 100+ concurrent sessions supported

### Testing
- **Unit Tests:** >= 85 tests, >= 90% coverage
- **Security Tests:** Path traversal, resource limits, concurrency
- **Performance Tests:** Response times, memory usage, scalability
- **Integration Tests:** End-to-end workflow execution

---

## Document Structure

This specification consists of 5 documents:

1. **README.md** (this file) - Executive summary and quick reference
2. **srd.md** - Software Requirements Document
   - Business goals, user stories, functional requirements, non-functional requirements
3. **specs.md** - Technical Specifications (2753 lines)
   - Architecture, component design, API specification, data models, security, performance
4. **tasks.md** - Implementation Task Breakdown (987 lines)
   - 5 phases, 30+ tasks, dependencies, validation gates, risk management
5. **implementation.md** - Detailed Implementation Guide (1045 lines)
   - Step-by-step code examples, tests, troubleshooting, rollback plan

---

## Implementation Timeline

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| **Phase 1: Foundation** | 2 days | Module structure, registration, dispatcher, validation |
| **Phase 2: Discovery & Execution** | 3 days | 1 discovery + 5 execution actions |
| **Phase 3: Management & Recovery** | 3 days | 5 management + 3 recovery actions |
| **Phase 4: Testing & Documentation** | 3 days | Security, performance, integration tests, docs |
| **Phase 5: Deployment & Validation** | 3 days | Staging, production deployment, clean cutover, validation |
| **Total** | **14 days** | **aos_workflow in production** |

---

## Quick Start Guide

### For Developers

1. **Read the spec:**
   ```bash
   cd .agent-os/specs/review/2025-10-22-aos-workflow-tool/
   
   # Start with requirements
   cat srd.md
   
   # Then technical design
   cat specs.md
   
   # Then implementation plan
   cat tasks.md
   cat implementation.md
   ```

2. **Set up development environment:**
   ```bash
   # Create feature branch
   git checkout -b feat/aos-workflow-tool
   
   # Install dependencies
   pip install -r mcp_server/requirements.txt
   pip install -r requirements-dev.txt
   
   # Create module files
   touch mcp_server/server/tools/workflow_tools.py
   touch tests/server/tools/test_workflow_tools.py
   ```

3. **Implement Phase 1:**
   - Follow `implementation.md` Phase 1 steps
   - Run tests after each task
   - Validate at phase gate before proceeding

### For Reviewers

1. **Verify completeness:**
   - [ ] Business requirements clear? (srd.md)
   - [ ] Technical design sound? (specs.md)
   - [ ] Tasks well-defined? (tasks.md)
   - [ ] Implementation guidance clear? (implementation.md)

2. **Check requirements traceability:**
   - [ ] Each FR maps to user story
   - [ ] Each component maps to FR
   - [ ] Each task maps to FR
   - [ ] All NFRs have validation criteria

3. **Review risks:**
   - [ ] Security risks addressed?
   - [ ] Performance risks mitigated?
   - [ ] Deployment risks managed?

4. **Approve or request changes:**
   - Add comments to spec files
   - Request clarification if needed
   - Approve when satisfied

### For Product Managers

**Business Impact:**
- ✅ Improves AI agent performance (85% → 95%)
- ✅ Reduces maintenance burden (17 tools → 1 tool)
- ✅ Enhances user experience (discovery, consistency)
- ✅ Clean cutover (no migration complexity)

**Success Metrics:**
- Tool count: 24 → 6 (target: < 10)
- AI agent accuracy: Baseline → +10%
- Response time: Baseline → -20%
- Error rate: < 1%

**Timeline:** 2 weeks (14 days)

**Resources:** 1 backend developer, 1 QA engineer

---

## API Quick Reference

### Discovery
```python
# List all workflows
aos_workflow(action="list_workflows")

# Filter by category
aos_workflow(action="list_workflows", category="code_generation")
```

### Execution
```python
# Start workflow
session = aos_workflow(
    action="start",
    workflow_type="test_generation_v3",
    target_file="src/myfile.py"
)

# Get current phase
phase = aos_workflow(action="get_phase", session_id=session_id)

# Get specific task
task = aos_workflow(action="get_task", session_id=session_id, phase=1, task_number=1)

# Complete phase
result = aos_workflow(
    action="complete_phase",
    session_id=session_id,
    phase=1,
    evidence={"code_structure": {...}}
)

# Get workflow state
state = aos_workflow(action="get_state", session_id=session_id)
```

### Management
```python
# List sessions
sessions = aos_workflow(action="list_sessions", status="active")

# Get session details
session_info = aos_workflow(action="get_session", session_id=session_id)

# Delete session
aos_workflow(action="delete_session", session_id=session_id, reason="Cleanup")

# Pause/resume
aos_workflow(action="pause", session_id=session_id, checkpoint_note="Break")
aos_workflow(action="resume", session_id=session_id)
```

### Recovery
```python
# Retry failed phase
aos_workflow(action="retry_phase", session_id=session_id, phase=2)

# Rollback to earlier phase
aos_workflow(action="rollback", session_id=session_id, to_phase=1)

# Get errors
errors = aos_workflow(action="get_errors", session_id=session_id)
```

---

## Requirements Summary

### Functional Requirements (10)
- FR-001: Single consolidated tool interface
- FR-002: Session-based workflow execution
- FR-003: Session management operations
- FR-004: Error recovery operations
- FR-005: Debugging and metrics (deferred to future)
- FR-006: Horizontal task scaling
- FR-007: Parameter validation and error messages
- FR-008: Workflow engine integration
- FR-009: Clean cutover from existing tools
- FR-010: Workflow discovery action

### Non-Functional Requirements (18)
- **Performance (3):** Discovery < 100ms, execution < 500ms, memory < 50MB
- **Reliability (2):** Graceful degradation, state persistence
- **Maintainability (3):** Clean code, self-documenting, comprehensive tests
- **Compatibility (1):** MCP protocol compliance
- **Usability (2):** Clear error messages, remediation guidance
- **Scalability (2):** 100+ concurrent sessions, horizontal scaling

---

## Risks & Mitigation

### High Risks
1. **WorkflowEngine API Changes Required**
   - Mitigation: Review API early, implement adapter layer if needed
2. **Clean Cutover Breaking Existing Users**
   - Mitigation: Comprehensive testing, clear migration guide, rollback plan

### Medium Risks
3. **Performance Targets Not Met**
   - Mitigation: Implement caching early, profile continuously
4. **Concurrency Issues in Production**
   - Mitigation: File locking, concurrency tests

---

## Success Criteria

**Technical:**
- [ ] All 14 actions implemented and tested
- [ ] Test coverage >= 90%
- [ ] Performance targets met
- [ ] Security tests passing
- [ ] Zero critical bugs in production

**Business:**
- [ ] Tool count reduced from ~24 to ~6
- [ ] AI agent performance improved
- [ ] Maintainability improved
- [ ] User feedback positive

---

## Approval Workflow

```
┌─────────────────┐
│  Spec Created   │ ← You are here
│   (In Review)   │
└────────┬────────┘
         │
         │ Review & Approve
         ↓
┌─────────────────┐
│   Approved      │
│ (Ready for Dev) │
└────────┬────────┘
         │
         │ Implement & Test
         ↓
┌─────────────────┐
│   Completed     │
│ (In Production) │
└─────────────────┘
```

**Current Status:** 🟡 In Review

**To Approve:**
1. Review all 5 spec documents
2. Verify requirements are clear and complete
3. Confirm technical design is sound
4. Approve and move to `.agent-os/specs/approved/`

**To Implement:**
- Wait for approval
- Then: `aos_workflow(action="start", workflow_type="spec_execution_v1", target_file="aos-workflow-tool", options={"spec_path": ".agent-os/specs/approved/2025-10-22-aos-workflow-tool"})`

---

## Contact & Support

**Spec Author:** AI Assistant  
**Created:** 2025-10-23  
**Last Updated:** 2025-10-23  

**Questions?**
- Technical questions → Review `specs.md` and `implementation.md`
- Business questions → Review `srd.md`
- Implementation questions → Review `tasks.md` and `implementation.md`

---

## Document History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-10-23 | Initial specification created | AI Assistant |

---

**Status:** 🟡 In Review  
**Next Step:** Review and approve for implementation

