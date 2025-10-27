# Technical Specifications

**Project:** AOS Workflow Tool  
**Date:** 2025-10-22  
**Based on:** srd.md (requirements)

---

## 1. Architecture Overview

### 1.1 Architectural Pattern: Consolidated Tool with Action Dispatch

**Primary Pattern:** Action Dispatch Pattern (proven by `pos_browser`)

The `pos_workflow` tool follows a consolidated architecture where a single MCP tool provides multiple operations through an action parameter. This pattern has been successfully implemented in `pos_browser` (20+ actions) and provides optimal performance for AI agent tool selection.

```
┌─────────────────────────────────────────────────────────┐
│                    pos_workflow Tool                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  MCP Tool Interface                                      │
│  ├─ Tool Name: pos_workflow                             │
│  ├─ Required Param: action (str)                        │
│  └─ Optional Params: session_id, phase, task_number...  │
│                                                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Action Dispatcher                                       │
│  ├─ Validates action parameter                          │
│  ├─ Routes to appropriate handler                       │
│  └─ Returns structured response                         │
│                                                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Action Handlers (14 actions)                           │
│                                                          │
│  Discovery (1):                                          │
│  └─ list_workflows → WorkflowEngine.list_workflows()    │
│                                                          │
│  Execution (5):                                          │
│  ├─ start          → WorkflowEngine.start_workflow()    │
│  ├─ get_phase      → WorkflowEngine.get_current_phase() │
│  ├─ get_task       → WorkflowEngine.get_task()          │
│  ├─ complete_phase → WorkflowEngine.complete_phase()    │
│  └─ get_state      → WorkflowEngine.get_workflow_state()│
│                                                          │
│  Management (5):                                         │
│  ├─ list_sessions  → StateManager.list_sessions()       │
│  ├─ get_session    → StateManager.get_session()         │
│  ├─ delete_session → StateManager.delete_session()      │
│  ├─ pause          → StateManager.pause_session()       │
│  └─ resume         → StateManager.resume_session()      │
│                                                          │
│  Recovery (3):                                           │
│  ├─ retry_phase    → WorkflowEngine.retry_phase()       │
│  ├─ rollback       → WorkflowEngine.rollback()          │
│  └─ get_errors     → StateManager.get_errors()          │
│                                                          │
└─────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────┐
│              Existing Infrastructure                     │
│              (No Modifications Required)                 │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  WorkflowEngine                                          │
│  ├─ Phase gating logic                                   │
│  ├─ Checkpoint validation                                │
│  ├─ State management                                     │
│  └─ Task content loading                                 │
│                                                          │
│  StateManager                                            │
│  ├─ Session persistence                                  │
│  ├─ State file I/O                                       │
│  └─ Cleanup operations                                   │
│                                                          │
│  Workflow Definitions                                    │
│  ├─ YAML metadata                                        │
│  ├─ Phase markdown files                                 │
│  └─ Task markdown files                                  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Key Characteristics:**
- **Single Entry Point:** All workflow operations through one tool
- **Action-Based Routing:** Operation determined by `action` parameter
- **Thin Wrapper:** Delegates to existing WorkflowEngine/StateManager
- **Consistent Interface:** Same pattern as `pos_browser` for familiarity
- **Zero Engine Changes:** No modifications to workflow engine logic

---

### 1.2 Architectural Decisions

#### Decision 1: Action Dispatch Pattern

**Decision:** Implement all workflow operations as actions within a single `pos_workflow` tool rather than maintaining separate tools for each operation.

**Rationale:**
- **Addresses FR-001:** Single consolidated tool interface requirement
- **Addresses NFR-P3:** Tool count reduction (8 tools → 1 tool) improves LLM performance
- **Proven Pattern:** Successfully used in `pos_browser` (20+ actions)
- **Better Discoverability:** All operations visible in one tool's documentation
- **Consistent Namespace:** Clear that all operations are workflow-related

**Alternatives Considered:**
- **Keep Separate Tools:** Original design with start_workflow, get_current_phase, etc. as separate tools
  - **Why Rejected:** High tool count degrades LLM performance; inconsistent with pos_browser pattern; harder to discover related operations
- **Categorized Sub-Tools:** Group into workflow_execution, workflow_management, workflow_recovery tools
  - **Why Rejected:** Still fragments the surface; arbitrary category boundaries; harder to discover all capabilities

**Trade-offs:**
- **Pros:** Optimal LLM performance, consistent pattern, single documentation source, clear namespace
- **Cons:** Single larger docstring vs multiple smaller ones; parameter complexity in one function
- **Mitigation:** Comprehensive parameter documentation with clear examples per action

---

#### Decision 2: Clean Cutover (No Migration Period)

**Decision:** Replace existing workflow tools completely with `pos_workflow` - no deprecation wrappers or dual support period.

**Rationale:**
- **Addresses FR-009:** Clean cutover requirement
- **Addresses NFR-U3:** Migration simplicity - one clear path
- **Eliminates Confusion:** No ambiguity about which tool to use
- **Simpler Maintenance:** No wrapper code to maintain and eventually remove
- **Cleaner Codebase:** No deprecated code paths cluttering the implementation

**Alternatives Considered:**
- **Deprecation Period:** Keep old tools as wrappers for 1-2 releases
  - **Why Rejected:** Adds complexity; maintains higher tool count temporarily; confuses users about which tool is "right"
- **Gradual Migration:** Migrate one operation at a time
  - **Why Rejected:** Prolonged mixed state; unclear completion criteria; technical debt lingers

**Trade-offs:**
- **Pros:** Clean implementation, clear expectations, immediate tool count benefit, no technical debt
- **Cons:** Requires updating all existing code/docs at once
- **Mitigation:** Single PR implementation; comprehensive before/after documentation

---

#### Decision 3: Workflow Discovery Action (list_workflows)

**Decision:** Implement list_workflows action to discover available workflow definitions.

**Rationale:**
- **Addresses FR-010:** Workflow discovery action requirement
- **Discovers Workflows:** Returns list of available workflow types (test_generation_v3, spec_creation_v1, etc.)
- **Essential Functionality:** Agents need to discover what workflows are runnable without hardcoding
- **Complements Tools/List:** MCP tools/list discovers tool capabilities; list_workflows discovers workflow definitions
- **Metadata Rich:** Provides workflow descriptions, phases, estimated duration, categories

**Alternatives Considered:**
- **Hardcoded Workflow Names:** Agents memorize workflow types
  - **Why Rejected:** Fragile; doesn't scale; breaks when workflows are added/removed
- **Advanced Discovery (search/filter/metadata):** Additional semantic search and detailed metadata actions
  - **Why Deferred:** Basic list_workflows sufficient for v1; advanced features for future if needed
- **Separate Discovery Tool:** Dedicated workflow_discovery tool
  - **Why Rejected:** Fragments surface again; contradicts consolidation goal

**Trade-offs:**
- **Pros:** Enables dynamic workflow discovery; supports extensibility; reduces hardcoding
- **Cons:** Adds one more action (14 total)
- **Mitigation:** Still significantly fewer than 18 fragmented tools; action is essential

---

#### Decision 4: Delegate to Existing WorkflowEngine (Zero Modifications)

**Decision:** Implement `pos_workflow` as a thin wrapper that delegates all operations to existing WorkflowEngine and StateManager classes without modifying their internal logic.

**Rationale:**
- **Addresses FR-008:** Workflow engine integration requirement
- **Addresses NFR-C2:** Compatible workflow engine integration
- **Minimizes Risk:** No changes to battle-tested workflow logic
- **Reduces Scope:** Tool surface consolidation only, not engine refactoring
- **Maintains Stability:** Existing workflows continue working unchanged

**Alternatives Considered:**
- **Refactor Engine Simultaneously:** Redesign WorkflowEngine internals while consolidating tools
  - **Why Rejected:** Couples two major changes; increases risk; extends timeline; unclear if engine changes are needed
- **Create New Engine:** Build new workflow engine alongside tool consolidation
  - **Why Rejected:** Massive scope increase; no clear benefit; existing engine works well

**Trade-offs:**
- **Pros:** Low risk, clear scope, maintains stability, faster implementation
- **Cons:** Can't optimize engine simultaneously (but not needed)
- **Mitigation:** None needed - this is the correct scoping decision

---

### 1.3 Requirements Traceability

| Requirement | Architectural Element | How Addressed |
|-------------|----------------------|---------------|
| FR-001: Single Consolidated Tool | pos_workflow tool with action parameter | Single MCP tool registration, action-based dispatch |
| FR-002: Session-Based Execution | Action handlers delegate to WorkflowEngine | start, get_phase, get_task, complete_phase, get_state actions |
| FR-003: Session Management | Action handlers delegate to StateManager | list_sessions, get_session, delete_session, pause, resume actions |
| FR-004: Error Recovery | Recovery action handlers | retry_phase, rollback, get_errors actions |
| FR-005: Debugging/Metrics | Metrics action handlers | get_history, get_metrics actions (future enhancement) |
| FR-006: Horizontal Task Scaling | get_task action handler | Delegates to WorkflowEngine.get_task() |
| FR-007: Parameter Validation | Action dispatcher validates params | ValueError with remediation before handler invocation |
| FR-008: Engine Integration | Thin wrapper architecture | All handlers delegate to existing engine methods |
| FR-009: Clean Cutover | Registration replaces old tools | No deprecation wrappers, single tool registration |
| FR-010: Discovery via tools/list | MCP standard mechanism | Comprehensive tool docstring, no custom discovery |
| NFR-P1: Response Time | Direct delegation (no extra layers) | Minimal dispatch overhead, existing engine performance |
| NFR-P2: Context Efficiency | Single tool docstring | One comprehensive docstring vs 8 separate ones |
| NFR-P3: LLM Performance | 5-tool surface | 8 workflow tools → 1 pos_workflow tool |
| NFR-R1: Error Handling | Broad exception catching in handlers | Structured error responses with remediation |
| NFR-R2: State Persistence | Uses existing StateManager | No changes to state file format or I/O |
| NFR-C3: Pattern Consistency | Action dispatch structure | Follows pos_browser pattern exactly |

---

### 1.4 Technology Stack

**Language:** Python 3.11+

**MCP Framework:** FastMCP
- Tool registration via @mcp.tool() decorator
- Automatic parameter schema generation
- Built-in error handling

**Existing Infrastructure (Reused):**
- **WorkflowEngine:** Phase gating, checkpoint validation, task loading
- **StateManager:** Session persistence, state file I/O
- **RAGEngine:** Standards search (unchanged)
- **BrowserManager:** Browser automation (unchanged)

**Dependencies:**
- No new dependencies required
- Reuses existing FastMCP, WorkflowEngine, StateManager

**Optional Integrations:**
- **HoneyHive:** Tracing/observability (via @tool_trace decorator)
- **Logging:** Python logging module (existing infrastructure)

**File Locations:**
- **Implementation:** `mcp_server/server/tools/workflow_tools.py`
- **Tests:** `tests/server/tools/test_workflow_tools.py`
- **Engine (unchanged):** `mcp_server/core/workflow_engine.py`
- **State (unchanged):** `mcp_server/core/state_manager.py`

---

### 1.5 Deployment Architecture

**Deployment Model:** Single Process MCP Server

```
┌───────────────────────────────────────────┐
│           Cursor IDE / Client              │
│                                            │
│  MCP Client                                │
│  ├─ Tool Discovery                         │
│  ├─ Tool Invocation                        │
│  └─ Response Handling                      │
│                                            │
└─────────────────┬──────────────────────────┘
                  │ MCP Protocol (stdio)
                  ↓
┌───────────────────────────────────────────┐
│        MCP Server (FastMCP)                │
│                                            │
│  Tool Registry                             │
│  ├─ search_standards                       │
│  ├─ pos_workflow  ← NEW                    │
│  ├─ pos_browser                            │
│  ├─ get_server_info                        │
│  └─ current_date                           │
│                                            │
│  [Old tools removed]                       │
│  ├─ start_workflow ← REMOVED               │
│  ├─ get_current_phase ← REMOVED            │
│  ├─ get_task ← REMOVED                     │
│  ├─ complete_phase ← REMOVED               │
│  ├─ get_workflow_state ← REMOVED           │
│  ├─ create_workflow ← REMOVED              │
│  ├─ validate_workflow ← REMOVED            │
│  └─ current_date (kept)                    │
│                                            │
└─────────────────┬──────────────────────────┘
                  │
                  ↓
┌───────────────────────────────────────────┐
│       Existing Infrastructure              │
│                                            │
│  WorkflowEngine                            │
│  ├─ .praxis-os/workflows/ (definitions)     │
│  └─ .praxis-os/state/ (sessions)            │
│                                            │
│  RAGEngine                                 │
│  └─ .praxis-os/.cache/vector_index/         │
│                                            │
└───────────────────────────────────────────┘
```

**Configuration:**
- No configuration changes required
- Tool groups remain: `["rag", "workflow", "browser"]`
- Tool count automatically reduces from 8 → 1 in workflow group

**Rollout Strategy:**
- Single PR: Remove old tools, add pos_workflow
- No feature flags needed (clean cutover)
- Update docs in same PR
- No data migration required (state format unchanged)

---

## 2. Component Design

### 2.1 Component: Tool Registration Function

**Purpose:** Register the consolidated `pos_workflow` tool with the FastMCP server.

**Responsibilities:**
- Register single MCP tool with comprehensive docstring
- Wire dependencies (WorkflowEngine, StateManager)
- Return tool count for verification

**Requirements Satisfied:**
- FR-001: Single consolidated tool interface
- NFR-C1: MCP protocol compliance

**Public Interface:**
```python
def register_workflow_tools(
    mcp: FastMCP,
    workflow_engine: WorkflowEngine,
    state_manager: StateManager,
) -> int:
    """Register workflow tool with MCP server.
    
    Args:
        mcp: FastMCP server instance
        workflow_engine: WorkflowEngine instance for workflow operations
        state_manager: StateManager instance for session management
        
    Returns:
        int: Number of tools registered (always 1 for pos_workflow)
    """
    @mcp.tool()
    async def pos_workflow(...) -> Dict[str, Any]:
        # Implementation
        pass
    
    return 1  # One tool registered
```

**Dependencies:**
- Requires: FastMCP instance, WorkflowEngine, StateManager
- Provides: Single pos_workflow tool to MCP ecosystem

**Error Handling:**
- Registration errors logged and propagated to server startup

---

### 2.2 Component: Main Tool Function (pos_workflow)

**Purpose:** Single entry point for all workflow operations, dispatches to appropriate handlers.

**Responsibilities:**
- Accept action parameter and route to handler
- Validate required parameters for each action
- Catch and structure all exceptions
- Return consistent response format

**Requirements Satisfied:**
- FR-001: Single tool interface with action dispatch
- FR-007: Parameter validation and error messages
- NFR-R1: Error handling with remediation

**Public Interface:**
```python
async def pos_workflow(
    action: str,  # Required: operation to perform
    session_id: Optional[str] = None,  # For most operations
    
    # Discovery params
    category: Optional[str] = None,
    
    # Execution params
    workflow_type: Optional[str] = None,
    target_file: Optional[str] = None,
    options: Optional[Dict[str, Any]] = None,
    
    # Task params
    phase: Optional[int] = None,
    task_number: Optional[int] = None,
    
    # Completion params
    evidence: Optional[Dict[str, Any]] = None,
    
    # Management params
    status: Optional[str] = None,
    reason: Optional[str] = None,
    checkpoint_note: Optional[str] = None,
    
    # Recovery params
    reset_evidence: Optional[bool] = False,
    to_phase: Optional[int] = None,
) -> Dict[str, Any]:
    """Comprehensive workflow management tool.
    
    Actions:
        Discovery (1): list_workflows
        Execution (5): start, get_phase, get_task, complete_phase, get_state
        Management (5): list_sessions, get_session, delete_session, pause, resume
        Recovery (3): retry_phase, rollback, get_errors
        
    Returns:
        Dict with status, session_id, and action-specific data
    """
```

**Dependencies:**
- Requires: WorkflowEngine, StateManager (via closure)
- Provides: MCP-compatible workflow operations

**Error Handling:**
- Missing parameters → ValueError with remediation
- Invalid action → Error with valid action list
- Handler exceptions → Structured error response

---

### 2.3 Component: Action Dispatcher

**Purpose:** Route action parameter to appropriate handler with validation.

**Responsibilities:**
- Validate action is known
- Check required parameters for action
- Invoke correct handler
- Handle unknown actions gracefully

**Requirements Satisfied:**
- FR-007: Parameter validation
- NFR-U1: Clear error messages

**Implementation Pattern:**
```python
# Inside pos_workflow function
try:
    if action == "list_workflows":
        return await _handle_list_workflows(category)
    
    elif action == "start":
        if not workflow_type or not target_file:
            raise ValueError("start requires workflow_type and target_file")
        return await _handle_start(workflow_type, target_file, options)
    
    elif action == "get_phase":
        if not session_id:
            raise ValueError("get_phase requires session_id")
        return await _handle_get_phase(session_id)
    
    # ... 11 more actions ...
    
    else:
        return {
            "status": "error",
            "error": f"Unknown action: {action}",
            "valid_actions": ["list_workflows", "start", "get_phase", ...]
        }
except Exception as e:
    return {"status": "error", "error": str(e), "action": action}
```

**Dependencies:**
- Requires: Action handler functions
- Provides: Validated dispatch to handlers

**Error Handling:**
- Unknown actions return list of valid actions
- Parameter validation failures include remediation examples

---

### 2.4 Component: Discovery Action Handler

**Purpose:** Implement workflow discovery operation (list_workflows).

**Responsibilities:**
- List all available workflow definitions
- Filter by category if requested
- Return workflow metadata (type, description, phases, duration)

**Requirements Satisfied:**
- FR-010: Workflow discovery action

**Handler Interface:**
```python
async def _handle_list_workflows(
    category: Optional[str] = None
) -> Dict[str, Any]:
    """List available workflow definitions."""
    workflows = workflow_engine.list_workflows(category=category)
    return {
        "status": "success",
        "workflows": workflows,
        "total": len(workflows)
    }
```

**Dependencies:**
- Requires: WorkflowEngine instance
- Provides: Workflow discovery to main tool

**Error Handling:**
- Invalid category → return all workflows with warning
- No workflows found → empty list with success status

---

### 2.5 Component: Execution Action Handlers

**Purpose:** Implement workflow execution operations (start, get_phase, get_task, complete_phase, get_state).

**Responsibilities:**
- Delegate to WorkflowEngine methods
- Transform responses to consistent format
- Handle engine-specific errors

**Requirements Satisfied:**
- FR-002: Session-based workflow execution
- FR-006: Horizontal task scaling
- FR-008: Workflow engine integration

**Handler Interfaces:**
```python
async def _handle_start(
    workflow_type: str,
    target_file: str,
    options: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """Start new workflow session."""
    result = workflow_engine.start_workflow(
        workflow_type=workflow_type,
        target_file=target_file,
        metadata=options
    )
    return result

async def _handle_get_phase(session_id: str) -> Dict[str, Any]:
    """Get current phase content."""
    return workflow_engine.get_current_phase(session_id)

async def _handle_get_task(
    session_id: str,
    phase: int,
    task_number: int
) -> Dict[str, Any]:
    """Get specific task content."""
    return workflow_engine.get_task(session_id, phase, task_number)

async def _handle_complete_phase(
    session_id: str,
    phase: int,
    evidence: Dict[str, Any]
) -> Dict[str, Any]:
    """Submit evidence and advance phase."""
    return workflow_engine.complete_phase(
        session_id=session_id,
        phase=phase,
        evidence=evidence
    )

async def _handle_get_state(session_id: str) -> Dict[str, Any]:
    """Get complete workflow state."""
    return workflow_engine.get_workflow_state(session_id)
```

**Dependencies:**
- Requires: WorkflowEngine instance
- Provides: Execution operations to main tool

**Error Handling:**
- Engine errors caught and returned as structured responses
- Session not found, phase not accessible, etc. → specific error messages

---

### 2.6 Component: Management Action Handlers

**Purpose:** Implement session management operations (list_sessions, get_session, delete_session, pause, resume).

**Responsibilities:**
- Delegate to StateManager methods
- Provide session filtering and cleanup
- Handle session lifecycle operations

**Requirements Satisfied:**
- FR-003: Session management operations
- NFR-SC2: Session management scalability

**Handler Interfaces:**
```python
async def _handle_list_sessions(
    status: Optional[str] = None
) -> Dict[str, Any]:
    """List all sessions with optional status filter."""
    return state_manager.list_sessions(status=status)

async def _handle_get_session(session_id: str) -> Dict[str, Any]:
    """Get detailed session information."""
    return state_manager.get_session(session_id)

async def _handle_delete_session(
    session_id: str,
    reason: Optional[str] = None
) -> Dict[str, Any]:
    """Delete session and clean up state files."""
    state_manager.delete_session(session_id, reason=reason)
    return {"status": "success", "session_id": session_id}

async def _handle_pause(
    session_id: str,
    checkpoint_note: Optional[str] = None
) -> Dict[str, Any]:
    """Pause workflow session."""
    return state_manager.pause_session(session_id, note=checkpoint_note)

async def _handle_resume(session_id: str) -> Dict[str, Any]:
    """Resume paused session."""
    return state_manager.resume_session(session_id)
```

**Dependencies:**
- Requires: StateManager instance
- Provides: Session management to main tool

**Error Handling:**
- Session not found → clear error with list of available sessions
- Invalid state transitions → error with current state and valid transitions

---

### 2.7 Component: Recovery Action Handlers

**Purpose:** Implement error recovery operations (retry_phase, rollback, get_errors).

**Responsibilities:**
- Provide workflow recovery mechanisms
- Enable error inspection and correction
- Support phase rollback scenarios

**Requirements Satisfied:**
- FR-004: Error recovery operations
- NFR-U1: Developer experience with recovery

**Handler Interfaces:**
```python
async def _handle_retry_phase(
    session_id: str,
    phase: int,
    reset_evidence: bool = False
) -> Dict[str, Any]:
    """Retry failed phase with optional evidence reset."""
    return workflow_engine.retry_phase(
        session_id=session_id,
        phase=phase,
        reset_evidence=reset_evidence
    )

async def _handle_rollback(
    session_id: str,
    to_phase: int
) -> Dict[str, Any]:
    """Roll back to earlier phase."""
    return workflow_engine.rollback(session_id=session_id, to_phase=to_phase)

async def _handle_get_errors(session_id: str) -> Dict[str, Any]:
    """Get session error details with remediation guidance."""
    return state_manager.get_errors(session_id)
```

**Dependencies:**
- Requires: WorkflowEngine, StateManager
- Provides: Recovery operations to main tool

**Error Handling:**
- Cannot rollback forward → error explaining direction constraint
- Invalid phase number → error with valid phase range

---

### 2.8 Component Interactions

**Interaction Flow:**

```
MCP Client
    ↓
    │ pos_workflow(action="start", ...)
    ↓
pos_workflow (Main Tool)
    ↓
    │ Validate action & params
    ↓
Action Dispatcher
    ↓
    │ Route to handler
    ↓
_handle_start (Execution Handler)
    ↓
    │ Delegate to engine
    ↓
WorkflowEngine.start_workflow()
    ↓
    │ Create session, load workflow
    ↓
StateManager (save session state)
    ↓
    │ Return session_id + Phase 0 content
    ↓
Response to Client
```

| From | To | Method | Purpose |
|------|----|--------|---------|
| MCP Client | pos_workflow | Tool invocation | Execute workflow operation |
| pos_workflow | Action Dispatcher | Internal routing | Select handler based on action |
| Action Dispatcher | Execution Handlers | Handler invocation | Execute operation |
| Execution Handlers | WorkflowEngine | Delegation | Leverage existing workflow logic |
| Management Handlers | StateManager | Delegation | Manage session lifecycle |
| All Handlers | pos_workflow | Return response | Structured result to client |

---

### 2.9 Module Organization

**File Structure:**
```
mcp_server/
├── server/
│   └── tools/
│       ├── workflow_tools.py          ← NEW (pos_workflow implementation)
│       ├── rag_tools.py               ← Existing (unchanged)
│       └── browser_tools.py           ← Existing (unchanged)
├── core/
│   ├── workflow_engine.py             ← Existing (unchanged)
│   └── state_manager.py               ← Existing (unchanged)
└── __init__.py
```

**Implementation File: workflow_tools.py**
```python
# Structure
def register_workflow_tools(...) -> int:
    \"\"\"Main registration function.\"\"\"
    
    @mcp.tool()
    async def pos_workflow(...) -> Dict[str, Any]:
        \"\"\"Tool implementation with action dispatch.\"\"\"
        # Dispatcher logic
        if action == "start":
            return await _handle_start(...)
        # ... more actions
    
    return 1  # Tool count

# Handler functions (module-level)
async def _handle_list_workflows(...) -> Dict[str, Any]: ...
async def _handle_start(...) -> Dict[str, Any]: ...
async def _handle_get_phase(...) -> Dict[str, Any]: ...
async def _handle_get_task(...) -> Dict[str, Any]: ...
# ... 10 more handlers
```

**Dependency Rules:**
- No circular imports
- WorkflowEngine and StateManager accessed via parameters (dependency injection)
- Handler functions are module-private (prefixed with _)
- Tool registration is the only public function

**Testing Structure:**
```
tests/
└── server/
    └── tools/
        ├── test_workflow_tools.py        ← NEW
        │   ├── test_register_workflow_tools()
        │   ├── test_pos_workflow_start()
        │   ├── test_pos_workflow_get_phase()
        │   └── ... (one test per action)
        ├── test_rag_tools.py             ← Existing
        └── test_browser_tools.py         ← Existing
```

---

## 3. API Specification

### 3.1 Tool Signature

```python
@mcp.tool()
async def pos_workflow(
    action: str,
    
    # Session context
    session_id: Optional[str] = None,
    
    # Start workflow parameters
    workflow_type: Optional[str] = None,
    target_file: Optional[str] = None,
    options: Optional[Dict[str, Any]] = None,
    
    # Task retrieval parameters
    phase: Optional[int] = None,
    task_number: Optional[int] = None,
    
    # Phase completion parameters
    evidence: Optional[Dict[str, Any]] = None,
    
    # Discovery parameters
    category: Optional[str] = None,
    
    # Session management parameters
    status: Optional[str] = None,
    reason: Optional[str] = None,
    checkpoint_note: Optional[str] = None,
    
    # Recovery parameters
    reset_evidence: Optional[bool] = False,
    to_phase: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Consolidated workflow management tool following pos_browser pattern.
    
    Handles all workflow operations through action-based dispatch:
    - Discovery (1 action): list_workflows
    - Execution (5 actions): start, get_phase, get_task, complete_phase, get_state
    - Management (5 actions): list_sessions, get_session, delete_session, pause, resume
    - Recovery (3 actions): retry_phase, rollback, get_errors
    
    Args:
        action: Operation to perform (required)
        session_id: Session identifier (required for execution/management/recovery)
        workflow_type: Workflow type identifier (required for start)
        target_file: Target file path (required for start)
        options: Optional workflow configuration (for start)
        phase: Phase number (for complete_phase, retry_phase)
        task_number: Task number (for get_task)
        evidence: Evidence dictionary (for complete_phase)
        category: Workflow category filter (for list_workflows)
        status: Session status filter (for list_sessions)
        reason: Reason for operation (for delete_session)
        checkpoint_note: Note for pause checkpoint (for pause)
        reset_evidence: Reset evidence flag (for retry_phase)
        to_phase: Target phase (for rollback)
    
    Returns:
        Dictionary with operation-specific results, always including:
        - status: "success" or "error"
        - action: Echo of requested action
        - Additional fields per action (see action details below)
    
    Raises:
        ValueError: If required parameters missing for action
        RuntimeError: If workflow operation fails
    """
```

**Requirements Satisfied:**
- FR-001: Single consolidated tool interface
- FR-007: Parameter validation
- NFR-U1: Clear error messages with remediation
- NFR-M1: Self-documenting interface

---

### 3.2 Action Catalog

#### 3.2.1 Discovery Actions

##### list_workflows

**Purpose:** Discover available workflow definitions with metadata.

**Parameters:**
- `action`: "list_workflows" (required)
- `category`: Optional category filter (e.g., "code_generation", "documentation")

**Returns:**
```python
{
    "status": "success",
    "action": "list_workflows",
    "workflows": [
        {
            "workflow_type": "test_generation_v3",
            "description": "Generate comprehensive test suites with TDD workflow",
            "category": "code_generation",
            "phases": 8,
            "estimated_duration": "15-30 minutes",
            "target_languages": ["python", "javascript", "typescript"]
        },
        {
            "workflow_type": "spec_creation_v1",
            "description": "Create comprehensive technical specifications",
            "category": "documentation",
            "phases": 3,
            "estimated_duration": "20-40 minutes",
            "artifacts": ["srd.md", "specs.md", "tasks.md"]
        }
        # ... more workflows
    ],
    "count": 2
}
```

**Example:**
```python
# List all workflows
result = pos_workflow(action="list_workflows")

# Filter by category
result = pos_workflow(action="list_workflows", category="code_generation")
```

**Requirements Satisfied:** FR-010, Story 1

---

#### 3.2.2 Execution Actions

##### start

**Purpose:** Initialize new workflow session with phase gating.

**Parameters:**
- `action`: "start" (required)
- `workflow_type`: Workflow identifier (required, e.g., "test_generation_v3")
- `target_file`: Target file path (required)
- `options`: Optional workflow configuration

**Returns:**
```python
{
    "status": "success",
    "action": "start",
    "session_id": "test_generation_v3_myfile_py_20251023_143022",
    "workflow_type": "test_generation_v3",
    "target_file": "src/myfile.py",
    "current_phase": 1,
    "phase_content": {
        "phase_number": 1,
        "title": "Analysis",
        "description": "Analyze target file structure",
        "tasks": ["task-1-examine-code.md", "task-2-identify-patterns.md"],
        "checkpoint": {
            "required_evidence": ["code_structure", "test_candidates"],
            "validation": "Must identify at least 3 testable functions"
        }
    },
    "acknowledgment_required": true
}
```

**Example:**
```python
session = pos_workflow(
    action="start",
    workflow_type="test_generation_v3",
    target_file="src/calculator.py",
    options={"coverage_target": 90}
)
session_id = session["session_id"]
```

**Requirements Satisfied:** FR-002, FR-008, Story 2

---

##### get_phase

**Purpose:** Get current phase content with requirements and artifacts.

**Parameters:**
- `action`: "get_phase" (required)
- `session_id`: Session identifier (required)

**Returns:**
```python
{
    "status": "success",
    "action": "get_phase",
    "session_id": "test_generation_v3_myfile_py_20251023_143022",
    "current_phase": 2,
    "phase_content": {
        "phase_number": 2,
        "title": "Test Design",
        "description": "Design test cases based on analysis",
        "tasks": ["task-1-design-unit-tests.md", "task-2-design-integration-tests.md"],
        "checkpoint": {
            "required_evidence": ["test_plan", "test_cases"],
            "validation": "Must have test plan covering all identified functions"
        },
        "artifacts_from_previous_phases": {
            "phase_1": ["code_structure", "test_candidates"]
        }
    },
    "total_phases": 8
}
```

**Example:**
```python
phase = pos_workflow(action="get_phase", session_id=session_id)
print(f"Current phase: {phase['current_phase']}/{phase['total_phases']}")
```

**Requirements Satisfied:** FR-002, FR-008, Story 5

---

##### get_task

**Purpose:** Get detailed task content for horizontal scaling.

**Parameters:**
- `action`: "get_task" (required)
- `session_id`: Session identifier (required)
- `phase`: Phase number (required)
- `task_number`: Task number (required)

**Returns:**
```python
{
    "status": "success",
    "action": "get_task",
    "session_id": "test_generation_v3_myfile_py_20251023_143022",
    "phase": 1,
    "task_number": 1,
    "task_content": {
        "title": "Examine Code Structure",
        "description": "Analyze target file to understand structure",
        "execution_steps": [
            {
                "step": 1,
                "command": "read_file",
                "description": "Read target file",
                "expected_output": "File contents"
            },
            {
                "step": 2,
                "command": "grep",
                "description": "Find function definitions",
                "expected_output": "List of functions"
            }
        ],
        "artifacts_to_produce": ["code_structure"],
        "estimated_duration": "2-5 minutes"
    }
}
```

**Example:**
```python
task = pos_workflow(
    action="get_task",
    session_id=session_id,
    phase=1,
    task_number=1
)
# Execute task steps
for step in task["task_content"]["execution_steps"]:
    print(f"Step {step['step']}: {step['description']}")
```

**Requirements Satisfied:** FR-006, Story 5

---

##### complete_phase

**Purpose:** Submit evidence and attempt phase completion with validation.

**Parameters:**
- `action`: "complete_phase" (required)
- `session_id`: Session identifier (required)
- `phase`: Phase number (required)
- `evidence`: Evidence dictionary matching checkpoint criteria (required)

**Returns (Success):**
```python
{
    "status": "success",
    "action": "complete_phase",
    "session_id": "test_generation_v3_myfile_py_20251023_143022",
    "phase_completed": 1,
    "checkpoint_passed": true,
    "evidence_accepted": ["code_structure", "test_candidates"],
    "next_phase": {
        "phase_number": 2,
        "title": "Test Design",
        "description": "Design test cases based on analysis"
    }
}
```

**Returns (Failure):**
```python
{
    "status": "error",
    "action": "complete_phase",
    "session_id": "test_generation_v3_myfile_py_20251023_143022",
    "phase": 1,
    "checkpoint_passed": false,
    "missing_evidence": ["test_candidates"],
    "validation_errors": [
        "Required evidence 'test_candidates' not provided"
    ],
    "remediation": "Submit evidence containing all required fields: ['code_structure', 'test_candidates']"
}
```

**Example:**
```python
# Submit evidence
result = pos_workflow(
    action="complete_phase",
    session_id=session_id,
    phase=1,
    evidence={
        "code_structure": {...},
        "test_candidates": [...]
    }
)

if result["checkpoint_passed"]:
    print(f"Phase {result['phase_completed']} complete!")
    print(f"Next: {result['next_phase']['title']}")
else:
    print(f"Missing: {result['missing_evidence']}")
```

**Requirements Satisfied:** FR-002, FR-007, FR-008, Story 2

---

##### get_state

**Purpose:** Get complete workflow state for debugging and resume.

**Parameters:**
- `action`: "get_state" (required)
- `session_id`: Session identifier (required)

**Returns:**
```python
{
    "status": "success",
    "action": "get_state",
    "session_id": "test_generation_v3_myfile_py_20251023_143022",
    "workflow_type": "test_generation_v3",
    "target_file": "src/calculator.py",
    "current_phase": 2,
    "total_phases": 8,
    "completed_phases": [1],
    "artifacts": {
        "phase_1": {
            "code_structure": {...},
            "test_candidates": [...]
        }
    },
    "session_status": "active",
    "created_at": "2025-10-23T14:30:22Z",
    "last_updated": "2025-10-23T14:45:10Z",
    "resume_capable": true
}
```

**Example:**
```python
state = pos_workflow(action="get_state", session_id=session_id)
print(f"Progress: {len(state['completed_phases'])}/{state['total_phases']} phases")
print(f"Status: {state['session_status']}")
```

**Requirements Satisfied:** FR-002, FR-003, Story 6

---

#### 3.2.3 Management Actions

##### list_sessions

**Purpose:** List all workflow sessions with optional status filter.

**Parameters:**
- `action`: "list_sessions" (required)
- `status`: Optional status filter ("active", "completed", "failed", "paused")

**Returns:**
```python
{
    "status": "success",
    "action": "list_sessions",
    "sessions": [
        {
            "session_id": "test_generation_v3_myfile_py_20251023_143022",
            "workflow_type": "test_generation_v3",
            "target_file": "src/calculator.py",
            "current_phase": 2,
            "total_phases": 8,
            "status": "active",
            "created_at": "2025-10-23T14:30:22Z",
            "last_updated": "2025-10-23T14:45:10Z"
        },
        {
            "session_id": "spec_creation_v1_feature_20251022_091500",
            "workflow_type": "spec_creation_v1",
            "target_file": "docs/feature.md",
            "current_phase": 3,
            "total_phases": 3,
            "status": "completed",
            "created_at": "2025-10-22T09:15:00Z",
            "completed_at": "2025-10-22T10:30:00Z"
        }
    ],
    "count": 2
}
```

**Example:**
```python
# List all sessions
all_sessions = pos_workflow(action="list_sessions")

# List only active sessions
active = pos_workflow(action="list_sessions", status="active")
```

**Requirements Satisfied:** FR-003, Story 3

---

##### get_session

**Purpose:** Get detailed session information including history and metadata.

**Parameters:**
- `action`: "get_session" (required)
- `session_id`: Session identifier (required)

**Returns:**
```python
{
    "status": "success",
    "action": "get_session",
    "session": {
        "session_id": "test_generation_v3_myfile_py_20251023_143022",
        "workflow_type": "test_generation_v3",
        "target_file": "src/calculator.py",
        "current_phase": 2,
        "total_phases": 8,
        "completed_phases": [1],
        "status": "active",
        "created_at": "2025-10-23T14:30:22Z",
        "last_updated": "2025-10-23T14:45:10Z",
        "phase_history": [
            {
                "phase": 1,
                "started_at": "2025-10-23T14:30:22Z",
                "completed_at": "2025-10-23T14:45:10Z",
                "duration_seconds": 888
            }
        ],
        "options": {"coverage_target": 90}
    }
}
```

**Example:**
```python
session_info = pos_workflow(action="get_session", session_id=session_id)
duration = session_info["session"]["phase_history"][0]["duration_seconds"]
print(f"Phase 1 took {duration} seconds")
```

**Requirements Satisfied:** FR-003, Story 3

---

##### delete_session

**Purpose:** Remove session and clean up state files.

**Parameters:**
- `action`: "delete_session" (required)
- `session_id`: Session identifier (required)
- `reason`: Optional reason for deletion

**Returns:**
```python
{
    "status": "success",
    "action": "delete_session",
    "session_id": "test_generation_v3_myfile_py_20251023_143022",
    "deleted": true,
    "cleanup": {
        "state_file_removed": true,
        "artifacts_preserved": false
    }
}
```

**Example:**
```python
result = pos_workflow(
    action="delete_session",
    session_id=session_id,
    reason="Test completed, no longer needed"
)
print(f"Session deleted: {result['deleted']}")
```

**Requirements Satisfied:** FR-003, Story 3

---

##### pause

**Purpose:** Pause active workflow session for later resume.

**Parameters:**
- `action`: "pause" (required)
- `session_id`: Session identifier (required)
- `checkpoint_note`: Optional note describing pause point

**Returns:**
```python
{
    "status": "success",
    "action": "pause",
    "session_id": "test_generation_v3_myfile_py_20251023_143022",
    "paused": true,
    "checkpoint": {
        "phase": 2,
        "timestamp": "2025-10-23T15:00:00Z",
        "note": "Waiting for code review before continuing"
    },
    "resume_capable": true
}
```

**Example:**
```python
result = pos_workflow(
    action="pause",
    session_id=session_id,
    checkpoint_note="Waiting for code review before continuing"
)
```

**Requirements Satisfied:** FR-003, Story 3

---

##### resume

**Purpose:** Resume paused workflow session.

**Parameters:**
- `action`: "resume" (required)
- `session_id`: Session identifier (required)

**Returns:**
```python
{
    "status": "success",
    "action": "resume",
    "session_id": "test_generation_v3_myfile_py_20251023_143022",
    "resumed": true,
    "current_phase": 2,
    "paused_duration_seconds": 3600,
    "phase_content": {
        "phase_number": 2,
        "title": "Test Design",
        # ... phase content
    }
}
```

**Example:**
```python
result = pos_workflow(action="resume", session_id=session_id)
print(f"Resumed at phase {result['current_phase']}")
```

**Requirements Satisfied:** FR-003, Story 3

---

#### 3.2.4 Recovery Actions

##### retry_phase

**Purpose:** Retry failed phase with optional evidence reset.

**Parameters:**
- `action`: "retry_phase" (required)
- `session_id`: Session identifier (required)
- `phase`: Phase number (required)
- `reset_evidence`: Reset evidence flag (default: False)

**Returns:**
```python
{
    "status": "success",
    "action": "retry_phase",
    "session_id": "test_generation_v3_myfile_py_20251023_143022",
    "phase": 2,
    "retrying": true,
    "evidence_reset": false,
    "phase_content": {
        "phase_number": 2,
        "title": "Test Design",
        # ... phase content
    },
    "previous_errors": ["Validation failed: incomplete test plan"]
}
```

**Example:**
```python
# Retry with existing evidence
result = pos_workflow(action="retry_phase", session_id=session_id, phase=2)

# Retry with fresh start
result = pos_workflow(
    action="retry_phase",
    session_id=session_id,
    phase=2,
    reset_evidence=True
)
```

**Requirements Satisfied:** FR-004, Story 4

---

##### rollback

**Purpose:** Roll back to earlier phase.

**Parameters:**
- `action`: "rollback" (required)
- `session_id`: Session identifier (required)
- `to_phase`: Target phase number (required)

**Returns:**
```python
{
    "status": "success",
    "action": "rollback",
    "session_id": "test_generation_v3_myfile_py_20251023_143022",
    "from_phase": 4,
    "to_phase": 2,
    "rolled_back": true,
    "artifacts_cleared": [3, 4],
    "phase_content": {
        "phase_number": 2,
        "title": "Test Design",
        # ... phase content
    }
}
```

**Example:**
```python
# Roll back to phase 2
result = pos_workflow(
    action="rollback",
    session_id=session_id,
    to_phase=2
)
print(f"Rolled back from phase {result['from_phase']} to {result['to_phase']}")
```

**Requirements Satisfied:** FR-004, Story 4

---

##### get_errors

**Purpose:** Get session error details for debugging.

**Parameters:**
- `action`: "get_errors" (required)
- `session_id`: Session identifier (required)

**Returns:**
```python
{
    "status": "success",
    "action": "get_errors",
    "session_id": "test_generation_v3_myfile_py_20251023_143022",
    "errors": [
        {
            "phase": 2,
            "timestamp": "2025-10-23T14:55:00Z",
            "error_type": "ValidationError",
            "message": "Incomplete test plan",
            "details": {
                "missing_fields": ["integration_tests"],
                "validation_rule": "Must include unit and integration tests"
            }
        }
    ],
    "error_count": 1,
    "last_error": "2025-10-23T14:55:00Z"
}
```

**Example:**
```python
errors = pos_workflow(action="get_errors", session_id=session_id)
for error in errors["errors"]:
    print(f"Phase {error['phase']}: {error['message']}")
```

**Requirements Satisfied:** FR-004, Story 4, Story 6

---

### 3.3 Error Responses

All actions return consistent error format when operations fail:

```python
{
    "status": "error",
    "action": "start",  # Echo of requested action
    "error": "Workflow type 'invalid_workflow_v1' not found",
    "error_type": "NotFoundError",
    "remediation": "Use pos_workflow(action='list_workflows') to see available workflows",
    "valid_actions": ["list_workflows", "start", "get_phase", ...]  # Included for unknown action errors
}
```

**Common Error Types:**
- `ValueError`: Missing or invalid parameters
- `NotFoundError`: Session or workflow not found
- `ValidationError`: Checkpoint validation failed
- `StateError`: Invalid state transition
- `RuntimeError`: Workflow engine error

**Requirements Satisfied:** FR-007, NFR-U1, NFR-U2

---

## 4. Data Models

### 4.1 Session State Model

**Purpose:** Persistent state storage for workflow sessions.

**Storage Location:** `.praxis-os/state/workflows/<session_id>.json`

**Schema:**
```python
{
    "session_id": str,              # Unique session identifier
    "workflow_type": str,            # Workflow type (e.g., "test_generation_v3")
    "target_file": str,              # Target file path
    "current_phase": int,            # Current phase number (1-indexed)
    "total_phases": int,             # Total number of phases
    "completed_phases": List[int],   # List of completed phase numbers
    "session_status": str,           # "active", "completed", "failed", "paused"
    
    # Timestamps
    "created_at": str,               # ISO 8601 timestamp
    "last_updated": str,             # ISO 8601 timestamp
    "completed_at": Optional[str],   # ISO 8601 timestamp (if completed)
    "paused_at": Optional[str],      # ISO 8601 timestamp (if paused)
    
    # Workflow state
    "artifacts": Dict[str, Any],     # Artifacts by phase: {"phase_1": {...}, "phase_2": {...}}
    "evidence": Dict[int, Dict],     # Evidence by phase: {1: {...}, 2: {...}}
    "options": Dict[str, Any],       # Workflow configuration options
    
    # History tracking
    "phase_history": List[Dict],     # Phase execution history
    "errors": List[Dict],            # Error log
    
    # Metadata
    "checkpoint_note": Optional[str] # Note for paused sessions
}
```

**Phase History Entry Schema:**
```python
{
    "phase": int,                    # Phase number
    "started_at": str,               # ISO 8601 timestamp
    "completed_at": Optional[str],   # ISO 8601 timestamp
    "duration_seconds": Optional[int],
    "attempt": int,                  # Retry attempt number (1-indexed)
    "status": str                    # "completed", "failed", "rolled_back"
}
```

**Error Entry Schema:**
```python
{
    "phase": int,                    # Phase where error occurred
    "timestamp": str,                # ISO 8601 timestamp
    "error_type": str,               # Error class name
    "message": str,                  # Error message
    "details": Dict[str, Any],       # Additional error details
    "remediation": Optional[str]     # Suggested fix
}
```

**Requirements Satisfied:** FR-002, FR-003, NFR-R1, NFR-R2

---

### 4.2 Workflow Metadata Model

**Purpose:** Workflow definition metadata for discovery.

**Storage Location:** Embedded in workflow metadata.json files

**Schema:**
```python
{
    "workflow_type": str,            # Unique workflow identifier
    "version": str,                  # Version (e.g., "v3", "v1")
    "name": str,                     # Display name
    "description": str,              # Human-readable description
    "category": str,                 # Category (e.g., "code_generation", "documentation")
    "phases": int,                   # Total number of phases
    "estimated_duration": str,       # Human-readable duration (e.g., "15-30 minutes")
    
    # Optional metadata
    "target_languages": Optional[List[str]],  # For code generation workflows
    "artifacts": Optional[List[str]],         # Output artifacts
    "prerequisites": Optional[List[str]],     # Required conditions
    "tags": Optional[List[str]]              # Search tags
}
```

**Requirements Satisfied:** FR-010, Story 1

---

### 4.3 Action Request Model

**Purpose:** Standardized input format for pos_workflow calls.

**Model:**
```python
class WorkflowActionRequest:
    action: str                      # Required action name
    
    # Session context
    session_id: Optional[str]
    
    # Start workflow
    workflow_type: Optional[str]
    target_file: Optional[str]
    options: Optional[Dict[str, Any]]
    
    # Task retrieval
    phase: Optional[int]
    task_number: Optional[int]
    
    # Phase completion
    evidence: Optional[Dict[str, Any]]
    
    # Discovery
    category: Optional[str]
    
    # Management
    status: Optional[str]
    reason: Optional[str]
    checkpoint_note: Optional[str]
    
    # Recovery
    reset_evidence: Optional[bool]
    to_phase: Optional[int]
```

**Validation Rules:**
- `action` must be one of 14 valid actions
- `session_id` required for all actions except `list_workflows` and `start`
- `workflow_type` and `target_file` required for `start`
- `phase` required for `complete_phase`, `retry_phase`
- `task_number` required for `get_task`
- `evidence` required for `complete_phase`
- `to_phase` required for `rollback`

**Requirements Satisfied:** FR-007, NFR-U1

---

### 4.4 Action Response Model

**Purpose:** Standardized output format for all pos_workflow actions.

**Base Response Schema:**
```python
{
    "status": str,                   # "success" or "error"
    "action": str,                   # Echo of requested action
    # ... action-specific fields
}
```

**Success Response:** Includes action-specific data fields (see Section 3.2)

**Error Response Schema:**
```python
{
    "status": "error",
    "action": str,
    "error": str,                    # Error message
    "error_type": str,               # Error class name
    "remediation": Optional[str],    # Suggested fix
    "valid_actions": Optional[List[str]]  # For unknown action errors
}
```

**Requirements Satisfied:** FR-007, NFR-U1, NFR-U2

---

### 4.5 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│                     AI Agent                            │
└───────────────┬─────────────────────────────────────────┘
                │
                │ WorkflowActionRequest
                │ {action, session_id, ...}
                ↓
┌─────────────────────────────────────────────────────────┐
│                  pos_workflow Tool                      │
│  ┌───────────────────────────────────────────────────┐  │
│  │         Action Dispatcher                         │  │
│  │  - Validates action                               │  │
│  │  - Validates required parameters                  │  │
│  │  - Routes to handler                              │  │
│  └─────────────────┬─────────────────────────────────┘  │
│                    │                                     │
│         ┌──────────┼──────────┐                         │
│         ↓          ↓          ↓                         │
│  ┌──────────┬──────────┬──────────┐                    │
│  │Discovery │Execution │Management│Recovery│            │
│  │Handlers  │Handlers  │Handlers  │Handlers│            │
│  └────┬─────┴────┬─────┴────┬─────┴────┬───┘            │
│       │          │          │          │                │
└───────┼──────────┼──────────┼──────────┼────────────────┘
        │          │          │          │
        │          ↓          │          │
        │    ┌─────────────┐ │          │
        │    │WorkflowEngine│ │          │
        │    │ - start     │ │          │
        │    │ - get_phase │ │          │
        │    │ - get_task  │ │          │
        │    │ - complete  │ │          │
        │    │ - retry     │ │          │
        │    │ - rollback  │ │          │
        │    └──────┬──────┘ │          │
        │           │        │          │
        │           ↓        ↓          ↓
        │    ┌──────────────────────────────┐
        └────→     StateManager             │
             │ - Session State (JSON)       │
             │ - Persistence                │
             │ - list/get/delete/pause      │
             └──────────────┬───────────────┘
                            │
                            ↓
                    ┌──────────────┐
                    │ File System  │
                    │ .praxis-os/   │
                    │   state/     │
                    │   workflows/ │
                    └──────────────┘
```

**Data Flow:**
1. AI agent calls `pos_workflow(action=..., ...)`
2. Action dispatcher validates and routes request
3. Handler calls WorkflowEngine or StateManager
4. State persisted to JSON files
5. Response returned to AI agent

**Requirements Satisfied:** FR-001, FR-002, FR-003, FR-008, NFR-R1

---

### 4.6 State Lifecycle

```
┌────────┐
│  NULL  │
└────┬───┘
     │ pos_workflow(action="start")
     ↓
┌────────────┐
│   ACTIVE   │ ←──────────────────┐
└─┬────┬───┬─┘                    │
  │    │   │ pos_workflow(action="pause")
  │    │   ↓                      │
  │    │ ┌────────┐               │
  │    │ │ PAUSED │───────────────┘
  │    │ └────────┘ pos_workflow(action="resume")
  │    │
  │    │ pos_workflow(action="complete_phase", phase=N, evidence={...})
  │    │ [checkpoint passed for final phase]
  │    ↓
  │ ┌───────────┐
  │ │ COMPLETED │
  │ └───────────┘
  │
  │ pos_workflow(action="complete_phase")
  │ [checkpoint failed]
  ↓
┌────────┐
│ FAILED │ ───┐
└────────┘    │ pos_workflow(action="retry_phase")
      ↑       │ or pos_workflow(action="rollback")
      │       ↓
      └───  ACTIVE

Delete: pos_workflow(action="delete_session") from any state
```

**State Transitions:**
- **NULL → ACTIVE:** `start` action creates new session
- **ACTIVE → PAUSED:** `pause` action saves checkpoint
- **PAUSED → ACTIVE:** `resume` action restores session
- **ACTIVE → COMPLETED:** Final phase completed successfully
- **ACTIVE → FAILED:** Phase checkpoint validation fails
- **FAILED → ACTIVE:** `retry_phase` or `rollback` action
- **ANY → NULL:** `delete_session` removes session

**Requirements Satisfied:** FR-002, FR-003, FR-004, NFR-R2

---

## 5. Security Considerations

### 5.1 Input Validation

**Threat:** Malicious or malformed input causing system compromise or instability.

**Mitigation Strategies:**

**Action Validation:**
```python
VALID_ACTIONS = {
    "list_workflows", "start", "get_phase", "get_task", "complete_phase",
    "get_state", "list_sessions", "get_session", "delete_session",
    "pause", "resume", "retry_phase", "rollback", "get_errors"
}

if action not in VALID_ACTIONS:
    raise ValueError(f"Invalid action: {action}")
```

**Session ID Validation:**
```python
# Pattern: workflow_type_target_language_timestamp
# Example: test_generation_v3_myfile_py_20251023_143022
SESSION_ID_PATTERN = r"^[a-z0-9_]+$"

if session_id and not re.match(SESSION_ID_PATTERN, session_id):
    raise ValueError("Invalid session_id format")
```

**Path Validation:**
```python
# Prevent directory traversal attacks
def validate_target_file(target_file: str) -> bool:
    # Normalize path
    norm_path = os.path.normpath(target_file)
    
    # Check for directory traversal
    if ".." in norm_path or norm_path.startswith("/"):
        raise ValueError("Invalid target_file: directory traversal detected")
    
    # Ensure path is within workspace
    workspace = os.getcwd()
    full_path = os.path.join(workspace, norm_path)
    if not full_path.startswith(workspace):
        raise ValueError("Invalid target_file: outside workspace")
    
    return True
```

**Evidence Validation:**
```python
# Limit evidence size to prevent memory exhaustion
MAX_EVIDENCE_SIZE = 10 * 1024 * 1024  # 10 MB

def validate_evidence(evidence: Dict) -> bool:
    evidence_json = json.dumps(evidence)
    if len(evidence_json) > MAX_EVIDENCE_SIZE:
        raise ValueError(f"Evidence too large: {len(evidence_json)} bytes (max: {MAX_EVIDENCE_SIZE})")
    return True
```

**Requirements Satisfied:** FR-007, NFR-S1

---

### 5.2 State File Security

**Threat:** Unauthorized access or modification of workflow state files.

**Mitigation Strategies:**

**File Permissions:**
```python
# Set restrictive permissions on state files
# Owner: read/write, Group: none, Other: none
os.chmod(state_file_path, 0o600)
```

**Path Isolation:**
```python
# All state files confined to .praxis-os/state/workflows/
STATE_DIR = ".praxis-os/state/workflows/"

def get_state_file_path(session_id: str) -> str:
    # Validate session_id to prevent directory traversal
    if not re.match(r"^[a-z0-9_]+$", session_id):
        raise ValueError("Invalid session_id")
    
    # Construct safe path
    state_file = os.path.join(STATE_DIR, f"{session_id}.json")
    
    # Verify path is within STATE_DIR
    if not os.path.abspath(state_file).startswith(os.path.abspath(STATE_DIR)):
        raise ValueError("Path traversal attempt detected")
    
    return state_file
```

**Atomic Writes:**
```python
# Prevent corruption from partial writes
def save_state_atomic(session_id: str, state: Dict) -> None:
    state_file = get_state_file_path(session_id)
    temp_file = f"{state_file}.tmp"
    
    # Write to temporary file
    with open(temp_file, 'w') as f:
        json.dump(state, f, indent=2)
    
    # Atomic rename
    os.rename(temp_file, state_file)
    
    # Set permissions
    os.chmod(state_file, 0o600)
```

**Requirements Satisfied:** NFR-S1, NFR-R1

---

### 5.3 Resource Limits

**Threat:** Resource exhaustion through excessive session creation or large evidence payloads.

**Mitigation Strategies:**

**Session Limits:**
```python
MAX_ACTIVE_SESSIONS = 100

def enforce_session_limit() -> None:
    active_sessions = state_manager.list_sessions(status="active")
    if len(active_sessions) >= MAX_ACTIVE_SESSIONS:
        raise RuntimeError(f"Maximum active sessions ({MAX_ACTIVE_SESSIONS}) reached")
```

**Evidence Size Limits:**
```python
MAX_EVIDENCE_SIZE = 10 * 1024 * 1024  # 10 MB

def validate_evidence_size(evidence: Dict) -> None:
    size = len(json.dumps(evidence))
    if size > MAX_EVIDENCE_SIZE:
        raise ValueError(f"Evidence too large: {size} bytes")
```

**Session Cleanup:**
```python
# Auto-cleanup stale sessions
STALE_SESSION_THRESHOLD = 7 * 24 * 3600  # 7 days

def cleanup_stale_sessions() -> None:
    now = datetime.now()
    for session in state_manager.list_sessions():
        last_updated = datetime.fromisoformat(session["last_updated"])
        age = (now - last_updated).total_seconds()
        
        if age > STALE_SESSION_THRESHOLD:
            state_manager.delete_session(session["session_id"])
```

**Requirements Satisfied:** NFR-S2, NFR-Sc1

---

### 5.4 Error Information Disclosure

**Threat:** Error messages revealing sensitive system information.

**Mitigation Strategies:**

**Sanitized Error Messages:**
```python
def sanitize_error(error: Exception) -> Dict[str, Any]:
    # Generic error types safe to expose
    safe_types = {
        ValueError: "ValidationError",
        KeyError: "NotFoundError",
        FileNotFoundError: "NotFoundError"
    }
    
    error_type = type(error)
    safe_type = safe_types.get(error_type, "RuntimeError")
    
    # Don't expose internal paths or stack traces
    safe_message = str(error).split("\n")[0]  # First line only
    safe_message = re.sub(r"/[^\s]+/", "***", safe_message)  # Redact paths
    
    return {
        "status": "error",
        "error_type": safe_type,
        "error": safe_message
    }
```

**Logging vs User-Facing Errors:**
```python
try:
    result = workflow_engine.start_workflow(...)
except Exception as e:
    # Log full error internally
    logger.error(f"Workflow start failed: {e}", exc_info=True)
    
    # Return sanitized error to user
    return sanitize_error(e)
```

**Requirements Satisfied:** NFR-S1, NFR-U1

---

### 5.5 Workflow Definition Integrity

**Threat:** Malicious or corrupted workflow definitions causing unexpected behavior.

**Mitigation Strategies:**

**Workflow Path Validation:**
```python
# Only load workflows from trusted directories
TRUSTED_WORKFLOW_DIRS = [
    ".praxis-os/workflows/",
    "universal/workflows/"  # For Agent OS repo only
]

def get_workflow_path(workflow_type: str) -> str:
    for base_dir in TRUSTED_WORKFLOW_DIRS:
        workflow_dir = os.path.join(base_dir, workflow_type)
        if os.path.exists(workflow_dir):
            # Verify path is within trusted directory
            abs_workflow = os.path.abspath(workflow_dir)
            abs_base = os.path.abspath(base_dir)
            if abs_workflow.startswith(abs_base):
                return workflow_dir
    
    raise ValueError(f"Workflow '{workflow_type}' not found in trusted directories")
```

**Metadata Validation:**
```python
def validate_workflow_metadata(metadata: Dict) -> bool:
    required_fields = ["workflow_type", "name", "description", "category", "phases"]
    
    for field in required_fields:
        if field not in metadata:
            raise ValueError(f"Invalid workflow metadata: missing '{field}'")
    
    if not isinstance(metadata["phases"], int) or metadata["phases"] < 1:
        raise ValueError("Invalid workflow metadata: 'phases' must be positive integer")
    
    return True
```

**Requirements Satisfied:** NFR-S1, NFR-R2

---

### 5.6 Concurrency Safety

**Threat:** Race conditions causing state corruption when multiple operations access the same session.

**Mitigation Strategies:**

**File-Based Locking:**
```python
import fcntl

def with_session_lock(session_id: str):
    """Context manager for exclusive session access."""
    lock_file = f".praxis-os/state/workflows/{session_id}.lock"
    
    class SessionLock:
        def __enter__(self):
            self.lock_fd = open(lock_file, 'w')
            fcntl.flock(self.lock_fd, fcntl.LOCK_EX)
            return self
        
        def __exit__(self, *args):
            fcntl.flock(self.lock_fd, fcntl.LOCK_UN)
            self.lock_fd.close()
    
    return SessionLock()

# Usage
with with_session_lock(session_id):
    state = state_manager.load_session(session_id)
    # ... modify state ...
    state_manager.save_session(session_id, state)
```

**Optimistic Locking:**
```python
# Include version number in state
state = {
    "_version": 1,
    "session_id": "...",
    # ... other fields
}

def save_session_with_version_check(session_id: str, state: Dict) -> None:
    current_state = load_session(session_id)
    
    if current_state["_version"] != state["_version"]:
        raise StateError("Session modified by another operation")
    
    state["_version"] += 1
    save_session(session_id, state)
```

**Requirements Satisfied:** NFR-R1, NFR-R2

---

### 5.7 Security Testing Requirements

**Test Categories:**

**Input Validation Tests:**
- Test invalid action names
- Test malformed session IDs
- Test directory traversal attempts in `target_file`
- Test oversized evidence payloads
- Test null/undefined required parameters

**Path Traversal Tests:**
```python
def test_path_traversal_protection():
    # Should reject directory traversal
    with pytest.raises(ValueError):
        pos_workflow(action="start", workflow_type="test_gen_v3", target_file="../../../etc/passwd")
    
    # Should reject absolute paths
    with pytest.raises(ValueError):
        pos_workflow(action="start", workflow_type="test_gen_v3", target_file="/etc/passwd")
```

**Resource Limit Tests:**
```python
def test_evidence_size_limit():
    large_evidence = {"data": "x" * (11 * 1024 * 1024)}  # 11 MB
    
    with pytest.raises(ValueError, match="Evidence too large"):
        pos_workflow(action="complete_phase", session_id="test", phase=1, evidence=large_evidence)
```

**Concurrency Tests:**
```python
def test_concurrent_session_modification():
    session_id = "test_session"
    
    # Simulate concurrent modifications
    def modify_session():
        state = state_manager.load_session(session_id)
        time.sleep(0.1)  # Simulate work
        state_manager.save_session(session_id, state)
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(modify_session) for _ in range(10)]
        results = [f.result() for f in futures]
    
    # Verify state consistency
    final_state = state_manager.load_session(session_id)
    assert final_state is not None
```

**Requirements Satisfied:** NFR-S1, NFR-S2

---

## 6. Performance Strategies

### 6.1 Response Time Optimization

**Goal:** < 100ms for discovery, < 500ms for execution actions (NFR-P1, NFR-P2)

**Strategies:**

**Lazy Loading of Workflow Metadata:**
```python
# Cache workflow metadata on first access
_workflow_metadata_cache = None

def list_workflows(category: Optional[str] = None) -> List[Dict]:
    global _workflow_metadata_cache
    
    if _workflow_metadata_cache is None:
        _workflow_metadata_cache = _load_all_workflow_metadata()
    
    if category:
        return [w for w in _workflow_metadata_cache if w["category"] == category]
    
    return _workflow_metadata_cache
```

**Efficient State Loading:**
```python
# Only load required fields for list operations
def list_sessions_fast(status: Optional[str] = None) -> List[Dict]:
    sessions = []
    for state_file in glob.glob(".praxis-os/state/workflows/*.json"):
        # Read only first few lines to get summary info
        with open(state_file, 'r') as f:
            # Load minimal data for listing
            state = json.load(f)
            summary = {
                "session_id": state["session_id"],
                "workflow_type": state["workflow_type"],
                "current_phase": state["current_phase"],
                "status": state["session_status"],
                "last_updated": state["last_updated"]
            }
            
            if status is None or summary["status"] == status:
                sessions.append(summary)
    
    return sessions
```

**Action Dispatch Optimization:**
```python
# Use dict dispatch instead of if/elif chain
ACTION_HANDLERS = {
    "list_workflows": _handle_list_workflows,
    "start": _handle_start,
    "get_phase": _handle_get_phase,
    # ... 11 more
}

async def pos_workflow(action: str, **kwargs) -> Dict[str, Any]:
    handler = ACTION_HANDLERS.get(action)
    if not handler:
        return {"status": "error", "error": f"Unknown action: {action}"}
    
    return await handler(**kwargs)
```

**Requirements Satisfied:** NFR-P1, NFR-P2

---

### 6.2 Memory Efficiency

**Goal:** < 50 MB for active sessions, efficient state file handling

**Strategies:**

**Streaming State File Parsing:**
```python
# For large state files, use streaming JSON parser
import ijson

def get_session_artifacts_streaming(session_id: str, phase: int) -> Dict:
    state_file = get_state_file_path(session_id)
    
    with open(state_file, 'rb') as f:
        # Stream parse to find specific phase artifacts
        artifacts = ijson.items(f, f'artifacts.phase_{phase}')
        for artifact in artifacts:
            return artifact
    
    return {}
```

**Artifact Pruning:**
```python
# Remove old phase artifacts when rolling back
def rollback_to_phase(session_id: str, to_phase: int) -> None:
    state = load_session(session_id)
    
    # Remove artifacts from phases > to_phase
    phases_to_remove = [p for p in state["completed_phases"] if p > to_phase]
    for phase in phases_to_remove:
        state["artifacts"].pop(f"phase_{phase}", None)
        state["evidence"].pop(phase, None)
    
    save_session(session_id, state)
```

**Evidence Compression:**
```python
import gzip
import base64

def compress_evidence(evidence: Dict) -> str:
    """Compress large evidence payloads."""
    json_str = json.dumps(evidence)
    compressed = gzip.compress(json_str.encode('utf-8'))
    return base64.b64encode(compressed).decode('utf-8')

def decompress_evidence(compressed: str) -> Dict:
    """Decompress evidence."""
    decoded = base64.b64decode(compressed.encode('utf-8'))
    decompressed = gzip.decompress(decoded)
    return json.loads(decompressed.decode('utf-8'))
```

**Requirements Satisfied:** NFR-P3, NFR-Sc1

---

### 6.3 Caching Strategy

**Goal:** Minimize redundant file system operations

**Strategies:**

**Workflow Metadata Cache:**
```python
from functools import lru_cache
from typing import Optional

@lru_cache(maxsize=128)
def get_workflow_metadata_cached(workflow_type: str) -> Dict:
    """Cache workflow metadata (invalidate on workflow updates)."""
    metadata_file = f".praxis-os/workflows/{workflow_type}/metadata.json"
    with open(metadata_file, 'r') as f:
        return json.load(f)

# Clear cache when workflows are updated
def invalidate_workflow_cache():
    get_workflow_metadata_cached.cache_clear()
```

**Session State Cache (Short-Lived):**
```python
from datetime import datetime, timedelta

class SessionCache:
    def __init__(self, ttl_seconds: int = 60):
        self.cache = {}
        self.ttl = timedelta(seconds=ttl_seconds)
    
    def get(self, session_id: str) -> Optional[Dict]:
        if session_id in self.cache:
            state, timestamp = self.cache[session_id]
            if datetime.now() - timestamp < self.ttl:
                return state
            else:
                del self.cache[session_id]
        return None
    
    def set(self, session_id: str, state: Dict) -> None:
        self.cache[session_id] = (state, datetime.now())
    
    def invalidate(self, session_id: str) -> None:
        self.cache.pop(session_id, None)

# Usage
session_cache = SessionCache(ttl_seconds=60)

def load_session_cached(session_id: str) -> Dict:
    cached = session_cache.get(session_id)
    if cached:
        return cached
    
    state = load_session_from_disk(session_id)
    session_cache.set(session_id, state)
    return state
```

**Cache Invalidation Rules:**
- Invalidate session cache after any write operation (`save_session`)
- Invalidate workflow metadata cache when workflows are added/modified
- Cache size limits to prevent memory growth

**Requirements Satisfied:** NFR-P1, NFR-P2, NFR-Sc1

---

### 6.4 Batch Operations

**Goal:** Efficient handling of multiple related operations

**Strategies:**

**Batch Session Listing:**
```python
def list_sessions_with_details(session_ids: List[str]) -> List[Dict]:
    """Load multiple sessions efficiently."""
    results = []
    
    # Read all files in single pass
    for session_id in session_ids:
        try:
            state = load_session(session_id)
            results.append(state)
        except FileNotFoundError:
            continue
    
    return results
```

**Parallel Phase Loading:**
```python
from concurrent.futures import ThreadPoolExecutor

def get_all_phase_content(session_id: str) -> List[Dict]:
    """Load all phase content in parallel."""
    state = load_session(session_id)
    total_phases = state["total_phases"]
    
    def load_phase(phase_num: int) -> Dict:
        return workflow_engine.get_phase_content(state["workflow_type"], phase_num)
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        phases = list(executor.map(load_phase, range(1, total_phases + 1)))
    
    return phases
```

**Requirements Satisfied:** NFR-P2, NFR-Sc1

---

### 6.5 I/O Optimization

**Goal:** Minimize disk operations, efficient file handling

**Strategies:**

**Buffered Writes:**
```python
class BufferedStateWriter:
    def __init__(self, flush_interval: int = 5):
        self.buffer = {}
        self.flush_interval = flush_interval
        self.last_flush = datetime.now()
    
    def write(self, session_id: str, state: Dict) -> None:
        self.buffer[session_id] = state
        
        # Flush if buffer is large or interval exceeded
        if len(self.buffer) >= 10 or \
           (datetime.now() - self.last_flush).total_seconds() > self.flush_interval:
            self.flush()
    
    def flush(self) -> None:
        for session_id, state in self.buffer.items():
            save_session_to_disk(session_id, state)
        
        self.buffer.clear()
        self.last_flush = datetime.now()
```

**Async File Operations:**
```python
import aiofiles

async def save_session_async(session_id: str, state: Dict) -> None:
    """Async state save for non-blocking I/O."""
    state_file = get_state_file_path(session_id)
    temp_file = f"{state_file}.tmp"
    
    async with aiofiles.open(temp_file, 'w') as f:
        await f.write(json.dumps(state, indent=2))
    
    os.rename(temp_file, state_file)
```

**Memoized File Stats:**
```python
@lru_cache(maxsize=256)
def get_session_exists(session_id: str) -> bool:
    """Cache session existence checks."""
    state_file = get_state_file_path(session_id)
    return os.path.exists(state_file)
```

**Requirements Satisfied:** NFR-P1, NFR-P2, NFR-R1

---

### 6.6 Scalability Considerations

**Goal:** Handle 100+ concurrent sessions without degradation (NFR-Sc1)

**Strategies:**

**Session Sharding:**
```python
def get_shard_path(session_id: str) -> str:
    """Distribute sessions across subdirectories."""
    # Use first 2 chars of session_id as shard key
    shard = session_id[:2]
    shard_dir = f".praxis-os/state/workflows/{shard}/"
    os.makedirs(shard_dir, exist_ok=True)
    return os.path.join(shard_dir, f"{session_id}.json")
```

**Resource Pool Management:**
```python
from queue import Queue

class WorkflowEnginePool:
    def __init__(self, pool_size: int = 10):
        self.pool = Queue(maxsize=pool_size)
        for _ in range(pool_size):
            self.pool.put(WorkflowEngine())
    
    def acquire(self) -> WorkflowEngine:
        return self.pool.get()
    
    def release(self, engine: WorkflowEngine) -> None:
        self.pool.put(engine)

# Usage
engine_pool = WorkflowEnginePool(pool_size=10)

async def pos_workflow_pooled(action: str, **kwargs) -> Dict:
    engine = engine_pool.acquire()
    try:
        return await _execute_action(engine, action, **kwargs)
    finally:
        engine_pool.release(engine)
```

**Load Monitoring:**
```python
class LoadMonitor:
    def __init__(self):
        self.active_operations = 0
        self.max_operations = 100
    
    def check_capacity(self) -> bool:
        return self.active_operations < self.max_operations
    
    def acquire(self) -> None:
        if not self.check_capacity():
            raise RuntimeError("System at capacity, try again later")
        self.active_operations += 1
    
    def release(self) -> None:
        self.active_operations = max(0, self.active_operations - 1)

load_monitor = LoadMonitor()
```

**Requirements Satisfied:** NFR-Sc1, NFR-Sc2

---

### 6.7 Performance Testing Requirements

**Test Categories:**

**Response Time Tests:**
```python
import pytest
import time

def test_list_workflows_performance():
    start = time.time()
    result = pos_workflow(action="list_workflows")
    elapsed = time.time() - start
    
    assert elapsed < 0.1, f"list_workflows took {elapsed}s (target: < 100ms)"
    assert result["status"] == "success"

def test_start_workflow_performance():
    start = time.time()
    result = pos_workflow(action="start", workflow_type="test_gen_v3", target_file="test.py")
    elapsed = time.time() - start
    
    assert elapsed < 0.5, f"start took {elapsed}s (target: < 500ms)"
```

**Scalability Tests:**
```python
def test_concurrent_sessions():
    session_ids = []
    
    # Create 100 concurrent sessions
    for i in range(100):
        result = pos_workflow(
            action="start",
            workflow_type="test_gen_v3",
            target_file=f"test_{i}.py"
        )
        session_ids.append(result["session_id"])
    
    # Verify all sessions are active
    sessions = pos_workflow(action="list_sessions", status="active")
    assert sessions["count"] >= 100

def test_large_evidence_performance():
    # Create session
    session = pos_workflow(action="start", workflow_type="test_gen_v3", target_file="test.py")
    
    # Large but valid evidence (8 MB)
    large_evidence = {"data": ["x" * 1000] * 8000}
    
    start = time.time()
    result = pos_workflow(
        action="complete_phase",
        session_id=session["session_id"],
        phase=1,
        evidence=large_evidence
    )
    elapsed = time.time() - start
    
    assert elapsed < 2.0, f"Large evidence processing took {elapsed}s"
```

**Memory Tests:**
```python
import psutil
import os

def test_memory_usage():
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Create 50 sessions with artifacts
    for i in range(50):
        session = pos_workflow(action="start", workflow_type="test_gen_v3", target_file=f"test_{i}.py")
        pos_workflow(
            action="complete_phase",
            session_id=session["session_id"],
            phase=1,
            evidence={"test": "data"}
        )
    
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_increase = final_memory - initial_memory
    
    assert memory_increase < 50, f"Memory increased by {memory_increase} MB (target: < 50 MB)"
```

**Cache Efficiency Tests:**
```python
def test_cache_hit_rate():
    # Warm up cache
    pos_workflow(action="list_workflows")
    
    # Measure cache hits
    start = time.time()
    for _ in range(100):
        pos_workflow(action="list_workflows")
    elapsed = time.time() - start
    
    avg_time = elapsed / 100
    assert avg_time < 0.01, f"Cached list_workflows averaged {avg_time}s (target: < 10ms)"
```

**Requirements Satisfied:** NFR-P1, NFR-P2, NFR-P3, NFR-Sc1

---

### 6.8 Performance Monitoring

**Metrics to Track:**

```python
class PerformanceMetrics:
    def __init__(self):
        self.action_latencies = defaultdict(list)
        self.action_counts = defaultdict(int)
        self.error_counts = defaultdict(int)
    
    def record_action(self, action: str, latency_ms: float, success: bool) -> None:
        self.action_latencies[action].append(latency_ms)
        self.action_counts[action] += 1
        if not success:
            self.error_counts[action] += 1
    
    def get_stats(self) -> Dict:
        stats = {}
        for action, latencies in self.action_latencies.items():
            stats[action] = {
                "count": self.action_counts[action],
                "avg_latency_ms": sum(latencies) / len(latencies),
                "p95_latency_ms": sorted(latencies)[int(len(latencies) * 0.95)],
                "error_rate": self.error_counts[action] / self.action_counts[action]
            }
        return stats

metrics = PerformanceMetrics()
```

**Instrumentation:**
```python
async def pos_workflow_instrumented(action: str, **kwargs) -> Dict:
    start = time.time()
    try:
        result = await pos_workflow(action, **kwargs)
        success = result["status"] == "success"
        return result
    finally:
        latency_ms = (time.time() - start) * 1000
        metrics.record_action(action, latency_ms, success)
```

**Requirements Satisfied:** NFR-P1, NFR-P2, NFR-Sc2

---

