# Complete Workflow Tool Surface for AI Agents
**Date**: 2025-10-15  
**Core Insight**: Workflows are THE primary feature - tools must comprehensively support AI agent usage  
**Goal**: Design complete tool surface for workflow discovery, execution, and management

---

## The User's Critical Insight

**Key points**:
1. "Tools are designed to be used by AI" - optimize for AI agent needs
2. "Listing available workflows" - discovery is essential
3. "Listing current sessions" - session visibility/management
4. "Managing deletion of bad state files" - cleanup/recovery
5. "Workflows are a core component" - this is THE feature
6. "Complex tasks to achieve near deterministic output" - reliability is the goal

**Implication**: Current 5 execution tools are INCOMPLETE. We need a comprehensive workflow management surface.

---

## Current Tool Surface (Incomplete)

### What We Have (5 tools)

**Execution**:
1. `start_workflow` - Initialize session
2. `get_current_phase` - Query current phase
3. `get_task` - Query specific task
4. `complete_phase` - Advance phase
5. `get_workflow_state` - Query full state

**Authoring** (separate domain):
6. `create_workflow` - Generate workflow
7. `validate_workflow` - Validate structure

**Utility**:
8. `current_date` - Date/time

### What's Missing (Critical Gaps)

**Discovery** (can't find workflows):
- ❌ List available workflows
- ❌ Query workflow metadata (before starting)
- ❌ Search workflows by capability
- ❌ Get workflow requirements

**Session Management** (can't manage sessions):
- ❌ List active sessions
- ❌ List all sessions (active + completed + failed)
- ❌ Get session details (without starting workflow)
- ❌ Delete session (cleanup bad state)
- ❌ Pause session
- ❌ Resume session

**Error Recovery** (can't recover from failures):
- ❌ Detect stale sessions
- ❌ Clean up orphaned sessions
- ❌ Retry failed phase
- ❌ Roll back phase

**Debugging/Inspection** (can't diagnose issues):
- ❌ Get session history (what happened?)
- ❌ Get validation errors (why did checkpoint fail?)
- ❌ Get session metrics (how long, which phase)

---

## Complete Tool Surface Design

### Category 1: Workflow Discovery (3 tools)

#### 1.1 list_workflows

```python
@mcp.tool()
async def list_workflows(
    category: Optional[str] = None,  # "code_generation", "documentation", "system", "meta"
    search_query: Optional[str] = None,  # keyword search in description
) -> Dict[str, Any]:
    """
    List available workflows with metadata.
    
    Essential for AI agents to discover which workflows exist and when to use them.
    Returns complete metadata for informed workflow selection.
    
    Args:
        category: Filter by workflow category
        search_query: Keyword search (e.g., "test", "documentation")
    
    Returns:
        {
            "workflows": [
                {
                    "workflow_type": "test_generation_v3",
                    "category": "code_generation",
                    "description": "Generate comprehensive test suites...",
                    "version": "1.0.0",
                    "total_phases": 8,
                    "estimated_duration": "2-4 hours",
                    "best_for": ["Python", "pytest", "unit tests"],
                    "primary_outputs": ["test file", "coverage report"],
                    "requirements": {
                        "target_file": "Python source file",
                        "min_version": "3.8"
                    }
                }
            ],
            "total": 7,
            "categories": ["code_generation", "documentation", "system", "meta"]
        }
    
    Example:
        # Find workflows for testing
        result = list_workflows(category="code_generation", search_query="test")
        workflow_type = result["workflows"][0]["workflow_type"]
        
        # Start workflow
        session = start_workflow(workflow_type, "myfile.py")
    """
```

#### 1.2 get_workflow_metadata

```python
@mcp.tool()
async def get_workflow_metadata(workflow_type: str) -> Dict[str, Any]:
    """
    Get detailed metadata for a specific workflow.
    
    Allows AI agents to inspect workflow requirements, phases, and outputs
    BEFORE starting the workflow. Critical for informed decision-making.
    
    Args:
        workflow_type: Workflow identifier (e.g., "test_generation_v3")
    
    Returns:
        {
            "workflow_type": "test_generation_v3",
            "version": "1.0.0",
            "description": "Generate comprehensive test suites...",
            "category": "code_generation",
            "total_phases": 8,
            "estimated_duration": "2-4 hours",
            "primary_outputs": ["test file", "coverage report"],
            "phases": [
                {
                    "phase_number": 0,
                    "phase_name": "Setup & Analysis",
                    "purpose": "Analyze code structure...",
                    "estimated_effort": "15-30 minutes",
                    "key_deliverables": ["Function list", "Class hierarchy"],
                    "validation_criteria": ["All functions identified", "Dependencies mapped"]
                }
                // ... more phases
            ],
            "requirements": {
                "target_file": {
                    "type": "file",
                    "description": "Python source file to generate tests for",
                    "extensions": [".py"]
                }
            },
            "options": {
                "coverage_threshold": {
                    "type": "integer",
                    "default": 80,
                    "description": "Minimum coverage percentage"
                }
            }
        }
    
    Example:
        # Check workflow details before starting
        metadata = get_workflow_metadata("test_generation_v3")
        print(f"This workflow has {metadata['total_phases']} phases")
        print(f"Estimated time: {metadata['estimated_duration']}")
        
        # Proceed with workflow
        session = start_workflow("test_generation_v3", "myfile.py")
    """
```

#### 1.3 search_workflows

```python
@mcp.tool()
async def search_workflows(
    query: str,
    limit: int = 5
) -> Dict[str, Any]:
    """
    Semantic search over workflow descriptions.
    
    Uses RAG to find workflows based on natural language queries.
    Alternative to list_workflows when you don't know the exact category.
    
    Args:
        query: Natural language query (e.g., "generate tests for Python")
        limit: Maximum results to return
    
    Returns:
        {
            "results": [
                {
                    "workflow_type": "test_generation_v3",
                    "relevance_score": 0.95,
                    "description": "Generate comprehensive test suites...",
                    "reason": "Matches: generate tests, Python"
                }
            ],
            "query": "generate tests for Python",
            "total_results": 2
        }
    
    Example:
        # Semantic search
        results = search_workflows("I need to document my API endpoints")
        workflow_type = results["results"][0]["workflow_type"]
        
        # Start top result
        session = start_workflow(workflow_type, "api.py")
    """
```

### Category 2: Session Execution (5 tools - Current)

**Keep as is** (or consolidate to 1 tool with action parameter):

2.1 `start_workflow` - Initialize session  
2.2 `get_current_phase` - Query current phase  
2.3 `get_task` - Query specific task  
2.4 `complete_phase` - Advance phase  
2.5 `get_workflow_state` - Query full state

### Category 3: Session Management (5 tools)

#### 3.1 list_sessions

```python
@mcp.tool()
async def list_sessions(
    status: Optional[str] = None,  # "active", "completed", "failed", "stale"
    workflow_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    List all workflow sessions with status and metadata.
    
    Critical for AI agents to see active sessions, resume work, or clean up stale sessions.
    
    Args:
        status: Filter by session status
        workflow_type: Filter by workflow type
    
    Returns:
        {
            "sessions": [
                {
                    "session_id": "363da7f6-f3c4-4342-a354-f9efff4e7d69",
                    "workflow_type": "test_generation_v3",
                    "target_file": "myfile.py",
                    "status": "active",  // "active", "completed", "failed", "stale"
                    "current_phase": 2,
                    "total_phases": 8,
                    "progress": 0.25,  // 25% complete
                    "created_at": "2025-10-15T14:30:00Z",
                    "updated_at": "2025-10-15T15:45:00Z",
                    "duration_minutes": 75,
                    "is_stale": false,  // true if > 24 hours inactive
                    "last_activity": "Completed Phase 1"
                }
            ],
            "total": 3,
            "active": 1,
            "completed": 1,
            "failed": 0,
            "stale": 1
        }
    
    Example:
        # Find active sessions
        sessions = list_sessions(status="active")
        if sessions["total"] > 0:
            # Resume existing session
            session_id = sessions["sessions"][0]["session_id"]
            state = get_workflow_state(session_id)
        
        # Find stale sessions to clean up
        stale = list_sessions(status="stale")
        for session in stale["sessions"]:
            delete_session(session["session_id"])
    """
```

#### 3.2 get_session_details

```python
@mcp.tool()
async def get_session_details(session_id: str) -> Dict[str, Any]:
    """
    Get comprehensive session information without modifying state.
    
    More detailed than get_workflow_state - includes history, errors, metrics.
    
    Args:
        session_id: Session identifier
    
    Returns:
        {
            "session_id": "363da7f6-...",
            "workflow_type": "test_generation_v3",
            "target_file": "myfile.py",
            "status": "active",
            "current_phase": 2,
            "completed_phases": [0, 1],
            "failed_phases": [],
            "created_at": "2025-10-15T14:30:00Z",
            "updated_at": "2025-10-15T15:45:00Z",
            "duration_minutes": 75,
            "is_stale": false,
            
            "phase_history": [
                {
                    "phase": 0,
                    "completed_at": "2025-10-15T14:45:00Z",
                    "duration_minutes": 15,
                    "evidence": {"functions_identified": 5},
                    "checkpoint_passed": true
                },
                {
                    "phase": 1,
                    "completed_at": "2025-10-15T15:30:00Z",
                    "duration_minutes": 45,
                    "evidence": {"tests_written": 10},
                    "checkpoint_passed": true
                }
            ],
            
            "errors": [],  // Any errors encountered
            
            "metrics": {
                "total_time_minutes": 75,
                "average_phase_minutes": 30,
                "phases_completed": 2,
                "phases_remaining": 6,
                "estimated_completion": "2025-10-15T18:30:00Z"
            }
        }
    """
```

#### 3.3 delete_session

```python
@mcp.tool()
async def delete_session(
    session_id: str,
    reason: Optional[str] = None
) -> Dict[str, Any]:
    """
    Delete a workflow session and clean up state files.
    
    Critical for recovering from errors, cleaning up stale sessions,
    or resetting after experimentation.
    
    Args:
        session_id: Session to delete
        reason: Optional reason for deletion (for logging)
    
    Returns:
        {
            "session_id": "363da7f6-...",
            "deleted": true,
            "files_removed": [
                ".praxis-os/.cache/state/363da7f6-f3c4-4342-a354-f9efff4e7d69.json"
            ],
            "reason": "Stale session - no activity in 48 hours"
        }
    
    Example:
        # Clean up stale sessions
        stale = list_sessions(status="stale")
        for session in stale["sessions"]:
            delete_session(
                session["session_id"],
                reason=f"Stale: {session['duration_minutes']} minutes old"
            )
        
        # Delete failed session to retry
        delete_session(failed_session_id, reason="Retry after fixing code")
    """
```

#### 3.4 pause_session

```python
@mcp.tool()
async def pause_session(
    session_id: str,
    checkpoint: Optional[str] = None
) -> Dict[str, Any]:
    """
    Pause a workflow session for later resumption.
    
    Allows AI agents to save progress and resume work later.
    Useful for long-running workflows or when switching contexts.
    
    Args:
        session_id: Session to pause
        checkpoint: Optional checkpoint note
    
    Returns:
        {
            "session_id": "363da7f6-...",
            "paused": true,
            "paused_at": "2025-10-15T16:00:00Z",
            "current_phase": 2,
            "checkpoint": "Completed analysis, ready for implementation",
            "resume_instructions": "Call resume_session() to continue"
        }
    """
```

#### 3.5 resume_session

```python
@mcp.tool()
async def resume_session(session_id: str) -> Dict[str, Any]:
    """
    Resume a paused workflow session.
    
    Returns current phase content to continue work.
    
    Args:
        session_id: Session to resume
    
    Returns:
        {
            "session_id": "363da7f6-...",
            "resumed": true,
            "resumed_at": "2025-10-15T17:00:00Z",
            "paused_duration_minutes": 60,
            "current_phase": 2,
            "phase_content": {...},  // Same as get_current_phase
            "checkpoint_note": "Completed analysis, ready for implementation"
        }
    """
```

### Category 4: Error Recovery (3 tools)

#### 4.1 retry_phase

```python
@mcp.tool()
async def retry_phase(
    session_id: str,
    phase: int,
    reset_evidence: bool = False
) -> Dict[str, Any]:
    """
    Retry a failed phase after fixing issues.
    
    Allows AI agents to recover from validation failures without restarting entire workflow.
    
    Args:
        session_id: Session identifier
        phase: Phase to retry
        reset_evidence: Clear previous evidence submission
    
    Returns:
        {
            "session_id": "363da7f6-...",
            "phase": 1,
            "retry_count": 2,
            "phase_content": {...},
            "previous_error": "Checkpoint validation failed: missing field 'tests_count'",
            "instructions": "Fix the validation errors and call complete_phase again"
        }
    """
```

#### 4.2 rollback_phase

```python
@mcp.tool()
async def rollback_phase(
    session_id: str,
    to_phase: int
) -> Dict[str, Any]:
    """
    Roll back workflow to an earlier phase.
    
    Useful when later phase reveals errors in earlier work.
    
    Args:
        session_id: Session identifier
        to_phase: Phase to roll back to
    
    Returns:
        {
            "session_id": "363da7f6-...",
            "rolled_back_from": 4,
            "rolled_back_to": 2,
            "phases_reset": [3, 4],
            "current_phase": 2,
            "phase_content": {...}
        }
    """
```

#### 4.3 get_session_errors

```python
@mcp.tool()
async def get_session_errors(session_id: str) -> Dict[str, Any]:
    """
    Get all errors encountered during workflow execution.
    
    Critical for diagnosing issues and providing remediation guidance.
    
    Args:
        session_id: Session identifier
    
    Returns:
        {
            "session_id": "363da7f6-...",
            "total_errors": 2,
            "errors": [
                {
                    "phase": 1,
                    "error_type": "ValidationError",
                    "message": "Checkpoint validation failed",
                    "details": {
                        "missing_fields": ["tests_count", "coverage_percent"],
                        "submitted_evidence": {"tests_written": true}
                    },
                    "occurred_at": "2025-10-15T15:30:00Z",
                    "remediation": "Ensure evidence includes all required fields: tests_count, coverage_percent"
                },
                {
                    "phase": 2,
                    "error_type": "FileNotFoundError",
                    "message": "Target file not found: myfile.py",
                    "occurred_at": "2025-10-15T16:00:00Z",
                    "remediation": "Check file path and ensure file exists"
                }
            ]
        }
    """
```

### Category 5: Debugging/Inspection (2 tools)

#### 5.1 get_session_history

```python
@mcp.tool()
async def get_session_history(session_id: str) -> Dict[str, Any]:
    """
    Get complete history of session activities.
    
    Shows what happened, when, and what evidence was submitted.
    Essential for understanding workflow execution and debugging.
    
    Args:
        session_id: Session identifier
    
    Returns:
        {
            "session_id": "363da7f6-...",
            "workflow_type": "test_generation_v3",
            "created_at": "2025-10-15T14:30:00Z",
            "total_duration_minutes": 120,
            
            "timeline": [
                {
                    "timestamp": "2025-10-15T14:30:00Z",
                    "action": "session_created",
                    "details": {
                        "workflow_type": "test_generation_v3",
                        "target_file": "myfile.py"
                    }
                },
                {
                    "timestamp": "2025-10-15T14:45:00Z",
                    "action": "phase_completed",
                    "phase": 0,
                    "evidence": {"functions_identified": 5},
                    "checkpoint_passed": true,
                    "duration_minutes": 15
                },
                {
                    "timestamp": "2025-10-15T15:30:00Z",
                    "action": "phase_failed",
                    "phase": 1,
                    "evidence": {"tests_written": true},
                    "checkpoint_passed": false,
                    "errors": ["Missing required field: tests_count"]
                },
                {
                    "timestamp": "2025-10-15T15:45:00Z",
                    "action": "phase_retried",
                    "phase": 1
                },
                {
                    "timestamp": "2025-10-15T16:30:00Z",
                    "action": "phase_completed",
                    "phase": 1,
                    "evidence": {"tests_written": true, "tests_count": 10},
                    "checkpoint_passed": true,
                    "duration_minutes": 45
                }
            ]
        }
    """
```

#### 5.2 get_session_metrics

```python
@mcp.tool()
async def get_session_metrics(session_id: str) -> Dict[str, Any]:
    """
    Get performance metrics for session.
    
    Useful for understanding workflow efficiency and identifying bottlenecks.
    
    Args:
        session_id: Session identifier
    
    Returns:
        {
            "session_id": "363da7f6-...",
            "workflow_type": "test_generation_v3",
            
            "time_metrics": {
                "total_duration_minutes": 120,
                "active_time_minutes": 90,
                "idle_time_minutes": 30,
                "average_phase_minutes": 15,
                "slowest_phase": {
                    "phase": 3,
                    "duration_minutes": 45
                },
                "fastest_phase": {
                    "phase": 0,
                    "duration_minutes": 10
                }
            },
            
            "progress_metrics": {
                "phases_completed": 6,
                "phases_remaining": 2,
                "progress_percent": 75,
                "estimated_completion": "2025-10-15T18:00:00Z",
                "estimated_remaining_minutes": 30
            },
            
            "quality_metrics": {
                "checkpoint_pass_rate": 0.83,  // 5/6 phases passed first try
                "retries": 1,
                "errors": 2
            }
        }
    """
```

---

## Complete Tool Count

### Consolidated Design (Recommended)

**Session Execution** (1 tool):
- `workflow_session` - Consolidated: start, get_phase, get_task, complete_phase, get_state

**Discovery** (3 tools):
- `list_workflows` - List all workflows
- `get_workflow_metadata` - Get workflow details
- `search_workflows` - Semantic search

**Session Management** (5 tools):
- `list_sessions` - List all sessions
- `get_session_details` - Get session info
- `delete_session` - Clean up sessions
- `pause_session` - Pause work
- `resume_session` - Resume work

**Error Recovery** (3 tools):
- `retry_phase` - Retry failed phase
- `rollback_phase` - Roll back to earlier phase
- `get_session_errors` - Get error details

**Debugging** (2 tools):
- `get_session_history` - Get activity timeline
- `get_session_metrics` - Get performance metrics

**Authoring** (2 tools):
- `create_workflow` - Generate workflow
- `validate_workflow` - Validate structure

**Utility** (1 tool):
- `current_date` - Date/time

**Other domains** (3 tools):
- `search_standards` - RAG search
- `get_server_info` - Server info
- `pos_browser` - Browser automation

**Total: 20 tools** (at the threshold, but comprehensive)

---

## Extensibility Consideration

**20 tools is at the performance threshold!** Need to be strategic.

### Option A: Selective Loading (Recommended)

```python
# Default tools (core functionality)
DEFAULT_TOOLS = [
    "workflow_session",      # 1
    "list_workflows",        # 2
    "list_sessions",         # 3
    "delete_session",        # 4
    "search_standards",      # 5
    "get_server_info",       # 6
    "current_date"           # 7
]  # 7 tools (optimal)

# Advanced workflow tools (opt-in)
WORKFLOW_ADVANCED = [
    "get_workflow_metadata",
    "search_workflows",
    "get_session_details",
    "pause_session",
    "resume_session",
    "retry_phase",
    "rollback_phase",
    "get_session_errors",
    "get_session_history",
    "get_session_metrics"
]  # +10 tools = 17 total (good)

# Authoring tools (opt-in)
WORKFLOW_AUTHORING = [
    "create_workflow",
    "validate_workflow"
]  # +2 tools = 19 total (threshold)

# Browser tools (opt-in)
BROWSER_TOOLS = [
    "pos_browser"
]  # +1 tool = 20 total (at limit)
```

### Option B: Tool Groups

```python
# Configure in .praxis-os/config.json
{
    "mcp": {
        "enabled_tool_groups": [
            "workflow_core",      // 7 tools: execution + discovery + session mgmt
            "workflow_advanced",  // 8 tools: error recovery + debugging
            "workflow_authoring", // 2 tools: create + validate
            "browser"             // 1 tool: pos_browser
        ]
    }
}
```

---

## Implementation Priority

### Phase 1: Discovery & Basic Management (Week 1)

**Add 3 tools** (11 → 14 tools):
1. `list_workflows` - Essential for discovery
2. `list_sessions` - Essential for session visibility
3. `delete_session` - Essential for cleanup

**Impact**: AI agents can discover workflows, see sessions, clean up bad state

### Phase 2: Advanced Management (Week 2)

**Add 3 tools** (14 → 17 tools):
4. `get_workflow_metadata` - Inspect before starting
5. `get_session_details` - Deep inspection
6. `get_session_errors` - Debugging

**Impact**: AI agents can make informed decisions, debug failures

### Phase 3: Error Recovery (Week 3)

**Add 2 tools** (17 → 19 tools):
7. `retry_phase` - Recover from failures
8. `rollback_phase` - Fix earlier mistakes

**Impact**: AI agents can recover without restarting workflow

### Phase 4: Advanced Features (Week 4+)

**Add 3 tools** (19 → 22 tools - OVER THRESHOLD):
9. `pause_session` - Pause work
10. `resume_session` - Resume work
11. `get_session_history` - Full timeline

**Tradeoff**: Need selective loading or accept performance degradation

---

## Conclusion

### The Real Insight

**Workflows are the core feature of Agent OS Enhanced**. The tool surface must comprehensively support:
1. **Discovery**: Find and understand workflows
2. **Execution**: Run workflows reliably
3. **Management**: See, pause, resume, delete sessions
4. **Recovery**: Handle errors gracefully
5. **Debugging**: Understand what happened

**Current 5 execution tools are insufficient** for AI agents to use workflows effectively.

### Recommendation

**Phase 1 implementation** (3 new tools):
- `list_workflows` - Discovery
- `list_sessions` - Visibility
- `delete_session` - Cleanup

**Result**: 14 tools (good range), covers critical gaps

**Future phases**: Add advanced tools with selective loading to stay under 20-tool threshold

**Should I implement Phase 1 (list_workflows, list_sessions, delete_session)?**

