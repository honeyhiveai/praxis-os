# Extracted Insights

## Requirements Insights (Phase 1)

### From Consolidated Workflow Tool Design:

**Business Goal:** Optimize AI agent performance by reducing tool count from 24 to 5 tools (79% reduction), achieving optimal LLM performance (~95% accuracy, minimal context pollution)

**User Need:** Comprehensive workflow management through a single, consistent interface that follows established patterns (aos_browser)

**Functional Requirements:**
1. **Discovery Actions** (3):
   - list_workflows: List available workflows with metadata
   - get_metadata: Get detailed workflow metadata
   - search: Semantic search over workflows

2. **Execution Actions** (5):
   - start: Initialize new workflow session
   - get_phase: Query current phase content
   - get_task: Query specific task content (horizontal scaling)
   - complete_phase: Submit evidence and advance phase
   - get_state: Query full workflow state

3. **Management Actions** (5):
   - list_sessions: List all sessions (active/completed/failed/stale)
   - get_session: Get detailed session information
   - delete_session: Remove session and clean up state files
   - pause: Pause workflow session
   - resume: Resume paused session

4. **Recovery Actions** (3):
   - retry_phase: Retry failed phase
   - rollback: Roll back to earlier phase
   - get_errors: Get session error details

5. **Debugging Actions** (2):
   - get_history: Get session activity timeline
   - get_metrics: Get session performance metrics

**Constraints:**
- Tool name must be `aos_workflow` (not `workflow`) to match `aos_browser` naming pattern
- Single tool with action dispatch parameter (not 17+ separate tools)
- Session-based architecture with session_id for most operations
- Must maintain compatibility during migration (deprecation wrappers acceptable for 1-2 releases)

**Out of Scope (Handled Through Workflows):**
- Workflow authoring (create_workflow) - handled by workflow_creation_v1 workflow
- Workflow validation (validate_workflow) - handled by workflow_validation_v1 workflow

---

## Design Insights (Phase 2)

### From Consolidated Workflow Tool Design:

**Architecture:** Single consolidated tool with action dispatch pattern (same as aos_browser)

**Component Structure:**
- Main tool function: `aos_workflow(action, session_id?, ...params)`
- Action dispatcher routing to 18 action handlers
- Action categories: Discovery, Execution, Management, Recovery, Debugging

**API Contract:**
```python
async def aos_workflow(
    action: str,  # Required: action to perform
    session_id: Optional[str] = None,  # Required for most operations
    
    # Start workflow params
    workflow_type: Optional[str] = None,
    target_file: Optional[str] = None,
    options: Optional[Dict[str, Any]] = None,
    
    # Task retrieval params
    phase: Optional[int] = None,
    task_number: Optional[int] = None,
    
    # Phase completion params
    evidence: Optional[Dict[str, Any]] = None,
    
    # Discovery params
    category: Optional[str] = None,
    search_query: Optional[str] = None,
    limit: Optional[int] = 5,
    
    # Session management params
    status: Optional[str] = None,
    reason: Optional[str] = None,
    checkpoint_note: Optional[str] = None,
    
    # Recovery params
    reset_evidence: Optional[bool] = False,
    to_phase: Optional[int] = None,
) -> Dict[str, Any]
```

**Data Model:**
- Action-specific parameter sets (optional parameters based on action)
- Consistent return structure: `Dict[str, Any]` with status, session_id, action-specific data
- Error responses include remediation guidance

**Session Management:**
- Persistent sessions across calls (same as aos_browser)
- Session ID isolation for multi-chat safety
- Session states: active, paused, completed, failed, stale

**Security Considerations:**
- Session isolation prevents cross-session interference
- State file access control
- Evidence validation before phase advancement

**Performance:**
- 5-tool surface optimizes LLM context
- Action dispatch faster than multiple tool lookups
- Batch operations possible within single tool call

**Design Patterns:**
- Follows aos_browser consolidation pattern exactly
- Complex domains → Single tool with action dispatch
- Simple utilities → Separate focused tools
- Complex operations → Through workflows

---

## Implementation Insights (Phase 4)

### From Consolidated Workflow Tool Design:

**Code Pattern - Action Dispatcher:**
```python
if action == "list_workflows":
    return await _list_workflows(category, search_query)
elif action == "start":
    if not workflow_type or not target_file:
        raise ValueError("start requires workflow_type and target_file")
    return await _start_workflow(workflow_type, target_file, options)
# ... 16 more actions
```

**Code Pattern - Parameter Validation:**
- Required parameters validated before handler call
- Descriptive error messages with remediation hints
- Type hints for all parameters

**Testing Strategy:**
```python
# Unit tests for each action handler
test_list_workflows()
test_start_workflow()
# ... 18 action tests

# Integration tests for workflows
test_discovery_workflow()
test_execute_workflow()
test_manage_sessions_workflow()
test_error_recovery_workflow()
```

**Deployment:**
- Phased rollout approach:
  - Week 1: Core actions (10 of 18) - Discovery + Execution + Basic Management
  - Week 2: Advanced actions (18 of 18) - Complete feature set
  - Week 3: Polish, documentation, integration tests

**Migration Strategy Options:**
1. **Hard Cutover** (Recommended): Remove old tools, introduce new consolidated tool. Clean break, no confusion.
2. **Deprecation Period**: Keep old tools as wrappers for 1-2 releases with @deprecated decorator

**Implementation Files:**
- `mcp_server/server/tools/workflow_tools.py` - Main tool registration
- Individual action handlers as internal functions
- Reuse existing workflow_engine infrastructure

**Error Handling:**
- Broad exception catching with structured error responses
- All errors include: status="error", error=str(e), action=action_name
- Remediation hints in error messages

**Documentation Requirements:**
- Comprehensive docstring with all 18 actions listed
- Examples for each action category
- Parameter documentation with types and defaults
- Related tools cross-reference

**Monitoring/Metrics:**
- Track action usage distribution
- Session lifecycle metrics (start → complete time)
- Error rates per action
- Tool count impact on LLM performance

---

## Cross-References

**Validated by Design Document:**
- Tool consolidation pattern (aos_browser proves viability)
- 5-tool target (optimal LLM performance)
- Action dispatch architecture (established pattern)
- Session-based operations (proven pattern)

**Conflicts:** None

**High-Priority Items:**
1. Tool name must be `aos_workflow` (not `workflow`)
2. Action dispatch with 18 actions across 5 categories
3. Consistency with aos_browser pattern
4. Phased implementation (Week 1 → Week 2 → Week 3)
5. Migration strategy decision (hard cutover vs deprecation)

---

## Insight Summary

**Total:** 47 insights  
**By Category:** Requirements [15], Design [20], Implementation [12]  
**Multi-source validated:** 4 (patterns proven by aos_browser)  
**Conflicts to resolve:** 0  
**High-priority items:** 5

**Phase 0 Complete:** ✅ 2025-10-22

