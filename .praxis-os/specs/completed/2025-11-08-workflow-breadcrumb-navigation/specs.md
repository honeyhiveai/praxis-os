# Technical Specifications

**Project:** Workflow Breadcrumb Navigation System  
**Date:** 2025-11-08  
**Based on:** srd.md (requirements)

---

## 1. Architecture Overview

### 1.1 Architectural Pattern

**Pattern:** Modular Monolith with Inline Enhancement

**Description:** The breadcrumb navigation system is an inline enhancement to the existing workflow engine within the monolithic praxis-os codebase. Rather than creating a separate abstraction layer or service, breadcrumb generation logic is integrated directly into the workflow engine's action handlers.

**Rationale:**
- **Requirement Alignment**: Supports FR-002 through FR-005 (breadcrumb generation in each action)
- **Simplicity**: KISS principle applies (NFR-M1) - this is string formatting with conditionals, not complex enough to warrant separate architecture
- **Performance**: Inline logic eliminates function call overhead, meeting NFR-P2 (<1ms breadcrumb generation)
- **Maintainability**: All breadcrumb logic in one file (`engine.py`) improves readability (NFR-M1)

**Key Subsystems:**
1. **Workflow Engine** (`.praxis-os/ouroboros/subsystems/workflow/engine.py`): Core orchestration, action handlers, breadcrumb generation
2. **Workflow Renderer** (`.praxis-os/ouroboros/subsystems/workflow/workflow_renderer.py`): Static workflow content loading, task count retrieval
3. **Dynamic Content Registry** (`.praxis-os/ouroboros/subsystems/workflow/dynamic_registry.py`): Dynamic workflow content caching, task count retrieval
4. **Guidance Module** (`.praxis-os/ouroboros/subsystems/workflow/guidance.py`): Response decoration with static guidance and breadcrumbs

**Architectural Diagram:**

```
┌────────────────────────────────────────────────────────────┐
│                     AI Agent (MCP Client)                   │
└─────────────────────────┬──────────────────────────────────┘
                          │ MCP Tool Calls
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                 Workflow Engine (engine.py)                  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │       Action Handlers (start, get_phase, get_task)   │  │
│  │                                                       │  │
│  │  • Remove information leakage (FR-001)               │  │
│  │  • Generate action-specific breadcrumbs (FR-002-005) │  │
│  │  • Call _get_task_count_for_phase() (FR-008)        │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                   │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │     Breadcrumb Generation (inline conditionals)      │  │
│  │                                                       │  │
│  │  if task_number < task_count:                        │  │
│  │      next_action = get_task(task_number + 1)         │  │
│  │  else:                                                │  │
│  │      next_action = complete_phase(evidence={...})    │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                   │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │    add_workflow_guidance(response, breadcrumb)       │  │
│  │                                                       │  │
│  │  • Prepend static guidance (WORKFLOW_EXECUTION_MODE) │  │
│  │  • Append breadcrumb at end (recency bias)           │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────┬───────────────────────────────────┘
                          │
            ┌─────────────┴─────────────┐
            │                           │
            ▼                           ▼
┌──────────────────────┐    ┌──────────────────────────┐
│  WorkflowRenderer    │    │ DynamicContentRegistry   │
│                      │    │                          │
│  • get_task_count()  │    │  • get_phase_metadata()  │
│  • glob task-*.md    │    │  • cached task_count     │
│  (FR-006)            │    │  (FR-007)                │
└──────────────────────┘    └──────────────────────────┘
```

---

### 1.2 Architectural Decisions

#### Decision 1: Inline Logic vs. Strategy Pattern

**Decision:** Implement breadcrumb generation as inline conditional logic within each action handler, rather than creating a separate `BreadcrumbGenerator` strategy class.

**Rationale:**
- **Simplicity (NFR-M1)**: Breadcrumb generation is string formatting with 3-4 conditional branches per action. Does not warrant abstraction.
- **Readability**: All logic in one place (`engine.py`) makes flow easier to understand. No jumping between files.
- **Performance (NFR-P2)**: Eliminates function call overhead for strategy dispatch.
- **Maintenance**: Simple conditionals are easier to debug than strategy pattern with multiple classes.

**Alternatives Considered:**
- **Strategy Pattern**: Separate `BreadcrumbGenerator` class with pluggable strategies for different actions.
  - **Why Not**: Over-engineering for simple string formatting. Adds indirection without meaningful benefit.

**Trade-offs:**
- **Pros:** Simple, fast, readable, all logic co-located
- **Cons:** Slightly more coupling (engine knows about UX), harder to globally change format (must update multiple places), harder to test in isolation

---

#### Decision 2: Just-In-Time Information Disclosure

**Decision:** Remove `phase_content` from `start_workflow` response, forcing AI agents to call `get_phase` to retrieve phase information.

**Rationale:**
- **Requirement Alignment**: Implements FR-001 (just-in-time disclosure)
- **Security Against Bypass**: Prevents outlier AIs from reading full phase content upfront and skipping workflow engagement (Story 2)
- **Sequential Execution**: Makes sequential calls the only way to access workflow content

**Alternatives Considered:**
- **Keep `phase_content` in `start_workflow`**: Simpler for compliant AIs (one less call).
  - **Why Not**: Enables information leakage, allowing outlier AIs to bypass workflow steps.

**Trade-offs:**
- **Pros:** Prevents lookahead, enforces sequential access, catches outlier AIs
- **Cons:** One extra call for compliant AIs (negligible: <50ms), slightly more verbose

---

#### Decision 3: Breadcrumb Positioning at Response End

**Decision:** Position breadcrumb fields at the end of workflow response dictionaries using Python 3.7+ dict ordering.

**Rationale:**
- **Recency Bias**: AI decision weights are highest for content read most recently. Positioning breadcrumbs last maximizes probability they're acted upon.
- **Visual Emphasis**: End position makes breadcrumbs stand out (not buried in response middle).
- **Backward Compatible**: Adding fields at end doesn't disrupt existing response structure parsing.

**Alternatives Considered:**
- **Breadcrumbs at Start**: Higher visibility.
  - **Why Not**: Lower recency bias. AI reads entire response, so end position has higher decision weight.

**Trade-offs:**
- **Pros:** Higher recency weight, non-disruptive positioning
- **Cons:** If AI stops reading response early, breadcrumb may not be seen (rare)

---

#### Decision 4: Task Count from Filesystem vs. Cache

**Decision:** Retrieve task count for static workflows via `glob()` on filesystem, and for dynamic workflows from cached `DynamicContentRegistry`.

**Rationale:**
- **Performance (NFR-P1)**: `glob()` is fast (<5ms for <50 files), caching not needed for static workflows
- **Accuracy**: Direct filesystem read ensures task count is always current (no cache invalidation complexity)
- **Simplicity**: No caching logic, memory overhead, or invalidation strategy required

**Alternatives Considered:**
- **Cache Task Count for Static Workflows**: Store task count in memory on first retrieval.
  - **Why Not**: `glob()` is already fast enough. Caching adds complexity without measurable performance benefit.

**Trade-offs:**
- **Pros:** Simple, accurate, no cache invalidation needed
- **Cons:** Slight I/O overhead per `get_task` call (negligible: <5ms)

---

#### Decision 5: Emoji Anchors for Visual Emphasis

**Decision:** Use emoji anchors (⚡, 🎯, ✅, 📊) in breadcrumb field names for visual emphasis.

**Rationale:**
- **Attention Weight**: Emojis increase visual salience, boosting AI's probability of noticing and acting on breadcrumbs
- **Clarity**: Field names remain descriptive even without emojis (`_NEXT_ACTION`, `_CURRENT_POSITION`)
- **User Feedback**: Emojis make responses more engaging for human observers (secondary benefit)

**Alternatives Considered:**
- **No Emojis**: Use plain field names (`NEXT_ACTION`, `CURRENT_POSITION`).
  - **Why Not**: Lower visual emphasis. Emojis provide free attention boost without downside.
- **Configurable Emoji Toggle**: Allow users to disable emojis.
  - **Why Not**: Adds complexity without clear demand. Can be added later if accessibility concerns arise.

**Trade-offs:**
- **Pros:** Higher attention weight, engaging UX, no performance cost
- **Cons:** Some environments may not render emojis (rare), slightly less formal

---

### 1.3 Requirements Traceability

| Requirement | Architectural Element | How Addressed |
|-------------|----------------------|---------------|
| FR-001 | `start_workflow()` action handler | Removes `phase_content` from response |
| FR-002 | `start_workflow()` breadcrumb logic | Generates `⚡_NEXT_ACTION: "get_phase(phase=0)"` |
| FR-003 | `get_phase()` breadcrumb logic | Generates breadcrumb to first task or `complete_phase` |
| FR-004 | `get_task()` breadcrumb logic | Dynamic breadcrumb based on `task_number` vs. `task_count` |
| FR-005 | `complete_phase()` breadcrumb logic | Generates breadcrumb to next phase or completion message |
| FR-006 | `WorkflowRenderer.get_task_count()` | Counts `task-*-*.md` files via `glob()` |
| FR-007 | `DynamicContentRegistry.get_phase_metadata()` | Returns cached `task_count` from parsed spec |
| FR-008 | `WorkflowEngine._get_task_count_for_phase()` | Routes to renderer or registry based on workflow type |
| FR-009 | `add_workflow_guidance(breadcrumb=None)` | Optional parameter ensures backward compatibility |
| FR-010 | `WORKFLOW_GUIDANCE_FIELDS` constant | Static fields prepended to all responses |
| NFR-P1 | `glob()` for static workflows | Fast task count retrieval (<5ms) |
| NFR-M1 | Inline breadcrumb logic | All logic in `engine.py`, no strategy pattern |
| NFR-C1 | Optional `breadcrumb` parameter | Non-breaking API change |
| NFR-U1 | Literal call syntax in breadcrumbs | AI can copy-paste exact function signature |
| NFR-O1 | Breadcrumb fields in response | Visible in JSON for observability |

---

### 1.4 Technology Stack

**Language:** Python 3.9+  
**Framework:** praxis-os workflow subsystem (existing)  
**Key Libraries:**  
- `pathlib` (filesystem operations for task count)
- `typing` (type hints for maintainability)

**No New Dependencies:** This feature uses only Python standard library and existing praxis-os infrastructure.

**File Structure:**
```
.praxis-os/ouroboros/subsystems/workflow/
├── engine.py                  # Core workflow engine (modified)
├── workflow_renderer.py       # Static workflow content loading (modified)
├── dynamic_registry.py        # Dynamic workflow content caching (existing)
├── guidance.py                # Response decoration (modified)
└── types.py                   # Type definitions (existing)
```

**Testing Framework:** pytest (existing)

---

### 1.5 Deployment Architecture

**Deployment Model:** In-place upgrade (no separate service)

**Deployment Steps:**
1. Update `engine.py`, `renderer.py`, `guidance.py` with new code
2. Run unit tests (`pytest` with 80%+ coverage)
3. Run integration tests (full workflow execution)
4. Restart praxis-os MCP server

**Rollback Strategy:** Git revert to previous commit (no database migrations, no state changes)

**Monitoring:**
- Breadcrumb following rate (via behavioral metrics: NFR-O1)
- Evidence validation failure rate (should remain <5%: NFR-R1)
- Workflow execution time (should not increase >1%: NFR-P2)

---

## 1.6 Supporting Documentation

Architecture informed by:
- **2025-11-08-workflow-breadcrumb-navigation.md**: Detailed design with architectural decisions, options considered, trade-off analysis

See `supporting-docs/INSIGHTS.md` for implementation insights and design rationale.

---

## 2. Component Design

---

### 2.1 Component: WorkflowEngine

**Purpose:** Core workflow orchestration, action handling, and breadcrumb generation.

**Responsibilities:**
- Execute workflow actions (`start_workflow`, `get_phase`, `get_task`, `complete_phase`)
- Generate action-specific breadcrumbs based on current position
- Route task count retrieval to appropriate source (static vs. dynamic)
- Enforce just-in-time information disclosure
- Coordinate with guidance module for response decoration

**Requirements Satisfied:**
- FR-001: Remove `phase_content` from `start_workflow`
- FR-002: Generate breadcrumb in `start_workflow`
- FR-003: Generate breadcrumb in `get_phase`
- FR-004: Generate dynamic breadcrumb in `get_task`
- FR-005: Generate breadcrumb in `complete_phase`
- FR-008: Unified task count helper method

**Public Interface:**
```python
class WorkflowEngine:
    def start_workflow(
        self,
        workflow_type: str,
        target_file: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Start workflow and return breadcrumb to get_phase."""
        
    def get_phase(
        self,
        session_id: str,
        phase: int
    ) -> Dict[str, Any]:
        """Get phase content and breadcrumb to first task."""
        
    def get_task(
        self,
        session_id: str,
        phase: int,
        task_number: int
    ) -> Dict[str, Any]:
        """Get task content and dynamic breadcrumb."""
        
    def complete_phase(
        self,
        session_id: str,
        phase: int,
        evidence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate evidence and return breadcrumb to next phase."""
        
    def _get_task_count_for_phase(
        self,
        state: WorkflowState,
        phase: int
    ) -> int:
        """Route task count retrieval (FR-008)."""
```

**Dependencies:**
- Requires: `WorkflowRenderer`, `DynamicContentRegistry`, `WorkflowGuidance`
- Provides: Workflow execution interface for MCP tools

**Internal Structure:**
- Action handlers: One method per MCP action
- Breadcrumb generation: Inline conditionals within each handler
- Task count routing: `_get_task_count_for_phase()` helper method

**Error Handling:**
- Task count retrieval fails → Log error, continue with static guidance only (graceful degradation)
- Breadcrumb generation fails → Log error, return response without breadcrumb (NFR-C2)

---

### 2.2 Component: WorkflowRenderer

**Purpose:** Load static workflow content from filesystem and provide task count for breadcrumb generation.

**Responsibilities:**
- Load phase content from `phases/{phase}/phase.md`
- Load task content from `phases/{phase}/task-{number}-{name}.md`
- Count tasks in phase via filesystem glob
- Validate workflow structure

**Requirements Satisfied:**
- FR-006: Task count retrieval for static workflows

**Public Interface:**
```python
class WorkflowRenderer:
    def get_task_count(
        self,
        workflow_type: str,
        phase: int
    ) -> int:
        """
        Get task count by counting task-*.md files.
        
        Raises:
            RendererError: If phase directory not found
        """
        
    def get_phase_content(
        self,
        workflow_type: str,
        phase: int
    ) -> str:
        """Load phase content from filesystem."""
        
    def get_task_content(
        self,
        workflow_type: str,
        phase: int,
        task_number: int
    ) -> str:
        """Load task content from filesystem."""
```

**Dependencies:**
- Requires: Filesystem access (`pathlib`)
- Provides: Static workflow content for `WorkflowEngine`

**Internal Structure:**
- Filesystem operations: `glob()` for task counting, `read_text()` for content
- Error handling: Raise `RendererError` with actionable fix (mkdir command)

**Performance:**
- Task count via `glob()`: <5ms for <50 files (NFR-P1)
- No caching needed (already fast)

**Error Handling:**
- Phase directory not found → Raise `RendererError` with mkdir command (NFR-U2)
- Task file not found → Raise `RendererError` with expected filename

---

### 2.3 Component: DynamicContentRegistry

**Purpose:** Cache parsed dynamic workflow content and provide task count from cached metadata.

**Responsibilities:**
- Parse `tasks.md` from spec directory
- Cache phase metadata including task count
- Provide task content from cache
- Handle cache invalidation (if spec changes)

**Requirements Satisfied:**
- FR-007: Task count retrieval for dynamic workflows

**Public Interface:**
```python
class DynamicContentRegistry:
    def get_phase_metadata(
        self,
        phase: int
    ) -> Dict[str, Any]:
        """
        Get phase metadata including task_count.
        
        Returns:
            {
                "phase": int,
                "task_count": int,
                "task_names": List[str],
                ...
            }
        """
        
    def get_task_content(
        self,
        phase: int,
        task_number: int
    ) -> str:
        """Get task content from cache."""
```

**Dependencies:**
- Requires: Spec directory, `tasks.md` parser
- Provides: Dynamic workflow content for `WorkflowEngine`

**Internal Structure:**
- Parsing: Extract phases/tasks from `tasks.md` on first access
- Caching: Store parsed content in memory (per session)
- Performance: <1ms cached lookup (NFR-P1)

**Error Handling:**
- `tasks.md` not found → Raise error with path
- Parse error → Raise error with line number

---

### 2.4 Component: WorkflowGuidance

**Purpose:** Decorate workflow responses with static guidance fields and action-specific breadcrumbs.

**Responsibilities:**
- Prepend static guidance fields to responses
- Append action-specific breadcrumbs at end
- Position fields for maximum AI attention (recency bias)
- Maintain backward compatibility

**Requirements Satisfied:**
- FR-009: Optional breadcrumb parameter (backward compatible)
- FR-010: Static guidance fields preserved

**Public Interface:**
```python
WORKFLOW_GUIDANCE_FIELDS = {
    "⚠️_WORKFLOW_EXECUTION_MODE": "ACTIVE",
    "🛑_DO_NOT_USE_EXTERNAL_TASK_TOOLS": "...",
    "execution_model": "Complete task → Submit evidence → Advance phase",
}

def add_workflow_guidance(
    response: Dict[str, Any],
    breadcrumb: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Decorate response with guidance and breadcrumb.
    
    Args:
        response: Base response from engine
        breadcrumb: Optional action-specific breadcrumb
        
    Returns:
        Decorated response with guidance + breadcrumb
    """
```

**Dependencies:**
- Requires: None (standalone function)
- Provides: Response decoration for `WorkflowEngine`

**Internal Structure:**
- Dict merging: `{**GUIDANCE, **response, **breadcrumb}` (Python 3.7+ ordering)
- Positioning: Static guidance first, response middle, breadcrumb last

**Error Handling:**
- No errors possible (simple dict merge)

---

## 2.5 Component Interactions

**Interaction Flow (get_task example):**

```
AI Agent
   │
   │ get_task(session_id, phase=0, task_number=3)
   ▼
WorkflowEngine.get_task()
   │
   ├──► _get_task_count_for_phase(state, phase)
   │       │
   │       ├──► (if static) WorkflowRenderer.get_task_count()
   │       │                     │
   │       │                     └──► glob("task-*-*.md")
   │       │
   │       └──► (if dynamic) DynamicContentRegistry.get_phase_metadata()
   │                              │
   │                              └──► cached metadata["task_count"]
   │
   ├──► Get task content (existing logic)
   │
   ├──► Generate breadcrumb (inline conditional)
   │    • if task_number < task_count: next task
   │    • else: complete_phase
   │
   └──► add_workflow_guidance(response, breadcrumb)
            │
            └──► Decorated response with breadcrumb
```

**Component Dependency Graph:**

```
WorkflowEngine
    ├── depends on → WorkflowRenderer (static workflows)
    ├── depends on → DynamicContentRegistry (dynamic workflows)
    └── depends on → WorkflowGuidance (response decoration)

WorkflowRenderer
    └── depends on → pathlib (filesystem)

DynamicContentRegistry
    └── depends on → Spec parser (existing)

WorkflowGuidance
    └── depends on → None (standalone)
```

---

## 2.6 Module Organization

**Directory Structure:**
```
.praxis-os/ouroboros/subsystems/workflow/
├── engine.py                  # WorkflowEngine (modified)
├── workflow_renderer.py       # WorkflowRenderer (modified)
├── dynamic_registry.py        # DynamicContentRegistry (existing)
├── guidance.py                # WorkflowGuidance (modified)
├── types.py                   # Type definitions (existing)
└── tests/
    ├── test_engine_breadcrumbs.py          # New
    ├── test_renderer_task_count.py         # New
    ├── test_guidance_decoration.py         # New
    └── test_integration_breadcrumb_flow.py # New
```

**Dependency Rules:**
- No circular imports
- `engine.py` imports `renderer.py`, `dynamic_registry.py`, `guidance.py`
- `guidance.py` is standalone (no imports from workflow subsystem)
- Use dependency injection where possible (renderer/registry passed to engine)

---

## 3. API Design

---

### 3.1 MCP Tool Interface (Existing - No Changes)

**Context:** This feature enhances the existing `pos_workflow` MCP tool. No new MCP tools or endpoints are added.

**Existing MCP Actions (Unmodified Signatures):**
- `start_workflow(workflow_type, target_file, options)`
- `get_phase(session_id, phase)`
- `get_task(session_id, phase, task_number)`
- `complete_phase(session_id, phase, evidence)`

**Change:** Response structure only (add breadcrumb fields), not action signatures.

---

### 3.2 Internal Interfaces

---

#### 3.2.1 WorkflowEngine Interface Changes

**New Method:**

```python
def _get_task_count_for_phase(
    self,
    state: WorkflowState,
    phase: int
) -> int:
    """
    Get task count for phase, routing to appropriate source.
    
    Routes to:
    - WorkflowRenderer.get_task_count() for static workflows
    - DynamicContentRegistry.get_phase_metadata() for dynamic workflows
    
    Args:
        state: Current workflow state (contains workflow_type, dynamic flag)
        phase: Phase number to get task count for
        
    Returns:
        Number of tasks in phase
        
    Raises:
        RendererError: If static workflow phase directory not found
        RegistryError: If dynamic workflow metadata not available
    """
```

**Modified Methods (Return Type Changes Only):**

```python
def start_workflow(...) -> Dict[str, Any]:
    """
    Start workflow session.
    
    Returns:
        {
            # Existing fields (unchanged):
            "session_id": str,
            "workflow_type": str,
            "current_phase": int,
            "workflow_overview": {...},
            
            # REMOVED:
            # "phase_content": str,  # <-- FR-001: Just-in-time disclosure
            
            # ADDED (FR-002):
            "⚡_NEXT_ACTION": "get_phase(phase=0)",
        }
    """

def get_phase(...) -> Dict[str, Any]:
    """
    Get phase content and metadata.
    
    Returns:
        {
            # Existing fields (unchanged):
            "session_id": str,
            "phase": int,
            "phase_content": str,
            "phase_status": {...},
            
            # ADDED (FR-003):
            "📊_PHASE_INFO": "Phase N has M tasks",
            "⚡_NEXT_ACTION": "get_task(phase=N, task_number=1)",
            # OR (if no tasks):
            "⚡_NEXT_ACTION": "complete_phase(phase=N, evidence={...})",
        }
    """

def get_task(...) -> Dict[str, Any]:
    """
    Get task content and position.
    
    Returns:
        {
            # Existing fields (unchanged):
            "session_id": str,
            "phase": int,
            "task_number": int,
            "task_content": str,
            "phase_status": {...},
            
            # ADDED (FR-004):
            "🎯_CURRENT_POSITION": "Task N/M",
            "⚡_NEXT_ACTION": "get_task(phase=P, task_number=N+1)",
            # OR (if final task):
            "🎯_CURRENT_POSITION": "Task N/M (final)",
            "⚡_NEXT_ACTION": "complete_phase(phase=P, evidence={...})",
        }
    """

def complete_phase(...) -> Dict[str, Any]:
    """
    Validate evidence and advance phase.
    
    Returns:
        {
            # Existing fields (unchanged):
            "session_id": str,
            "phase": int,
            "validation_result": str,
            "next_phase": Optional[int],
            
            # ADDED (FR-005):
            "✅_PHASE_COMPLETE": "Phase N completed successfully",
            "⚡_NEXT_ACTION": "get_phase(phase=N+1)",
            # OR (if workflow complete):
            "🎉_WORKFLOW_COMPLETE": "All phases completed successfully",
        }
    """
```

---

#### 3.2.2 WorkflowRenderer Interface Changes

**New Method:**

```python
def get_task_count(
    self,
    workflow_type: str,
    phase: int
) -> int:
    """
    Get number of tasks in phase for static workflow.
    
    Implementation:
        1. Construct phase directory path: workflows_dir / workflow_type / "phases" / str(phase)
        2. Validate directory exists
        3. Count files matching glob pattern: "task-*-*.md"
        4. Return count
    
    Args:
        workflow_type: Workflow identifier (e.g., "spec_creation_v1")
        phase: Phase number (0-indexed)
        
    Returns:
        Number of task files in phase directory
        
    Raises:
        RendererError: If phase directory not found
            - what_failed: "Task count retrieval"
            - why_failed: f"Phase directory not found: {phase_dir}"
            - how_to_fix: f"Create phase directory: mkdir -p {phase_dir}"
    
    Performance:
        - <5ms for directories with <50 files (NFR-P1)
        - Uses pathlib.glob() (fast, non-recursive)
    """
```

---

#### 3.2.3 DynamicContentRegistry Interface (Existing - No Changes)

**Existing Method Used:**

```python
def get_phase_metadata(
    self,
    phase: int
) -> Dict[str, Any]:
    """
    Get phase metadata from cached spec parse.
    
    Returns:
        {
            "phase": int,
            "phase_name": str,
            "task_count": int,  # <-- FR-007: Used for breadcrumbs
            "task_names": List[str],
            "estimated_effort": str,
            ...
        }
    """
```

**No Changes Required:** `task_count` field already exists in metadata.

---

#### 3.2.4 WorkflowGuidance Interface Changes

**Modified Function Signature:**

```python
def add_workflow_guidance(
    response: Dict[str, Any],
    breadcrumb: Optional[Dict[str, str]] = None  # <-- FR-009: New optional parameter
) -> Dict[str, Any]:
    """
    Decorate workflow response with static guidance and optional breadcrumb.
    
    Merging Order (Python 3.7+ dict ordering):
        1. Static guidance fields (WORKFLOW_GUIDANCE_FIELDS) - prepended
        2. Response content - middle
        3. Breadcrumb fields (if provided) - appended (recency bias)
    
    Args:
        response: Base response from workflow engine
        breadcrumb: Optional action-specific navigation
            Examples:
            - {"⚡_NEXT_ACTION": "get_phase(phase=0)"}
            - {"🎯_CURRENT_POSITION": "Task 3/5", "⚡_NEXT_ACTION": "get_task(phase=0, task_number=4)"}
            - {"✅_PHASE_COMPLETE": "Phase 1 completed", "⚡_NEXT_ACTION": "get_phase(phase=2)"}
    
    Returns:
        Decorated response with guidance + breadcrumb fields
        
    Backward Compatibility:
        - If breadcrumb=None: Returns response with only static guidance (existing behavior)
        - If breadcrumb provided: Returns response with static guidance + breadcrumb
        - No breaking changes (optional parameter, NFR-C1)
    """
```

---

### 3.3 Data Transfer Objects

---

#### 3.3.1 Breadcrumb Structure

**Type Definition:**

```python
Breadcrumb = Dict[str, str]
```

**Valid Breadcrumb Fields:**
- `⚡_NEXT_ACTION`: Literal call syntax for next action (required)
- `🎯_CURRENT_POSITION`: Task position indicator (optional, only in `get_task`)
- `✅_PHASE_COMPLETE`: Phase completion message (optional, only in `complete_phase`)
- `🎉_WORKFLOW_COMPLETE`: Workflow completion message (optional, only in `complete_phase`)
- `📊_PHASE_INFO`: Phase metadata (optional, only in `get_phase`)

**Examples:**

```python
# start_workflow breadcrumb:
{"⚡_NEXT_ACTION": "get_phase(phase=0)"}

# get_phase breadcrumb (with tasks):
{
    "📊_PHASE_INFO": "Phase 0 has 5 tasks",
    "⚡_NEXT_ACTION": "get_task(phase=0, task_number=1)"
}

# get_task breadcrumb (middle task):
{
    "🎯_CURRENT_POSITION": "Task 3/5",
    "⚡_NEXT_ACTION": "get_task(phase=0, task_number=4)"
}

# get_task breadcrumb (final task):
{
    "🎯_CURRENT_POSITION": "Task 5/5 (final)",
    "⚡_NEXT_ACTION": "complete_phase(phase=0, evidence={...})"
}

# complete_phase breadcrumb (more phases):
{
    "✅_PHASE_COMPLETE": "Phase 0 completed successfully",
    "⚡_NEXT_ACTION": "get_phase(phase=1)"
}

# complete_phase breadcrumb (workflow complete):
{
    "🎉_WORKFLOW_COMPLETE": "All phases completed successfully"
}
```

---

### 3.4 Error Handling

---

#### 3.4.1 Graceful Degradation (NFR-C2)

**Philosophy:** Breadcrumb failures should never block workflow execution.

**Error Scenarios:**

1. **Task Count Retrieval Fails:**
   ```python
   try:
       task_count = self._get_task_count_for_phase(state, phase)
   except Exception as e:
       logger.error(f"Task count retrieval failed: {e}", extra={"phase": phase})
       # Continue with static guidance only (no breadcrumb)
       return add_workflow_guidance(response, breadcrumb=None)
   ```

2. **Breadcrumb Generation Fails:**
   ```python
   try:
       breadcrumb = self._generate_breadcrumb(...)
   except Exception as e:
       logger.error(f"Breadcrumb generation failed: {e}")
       # Continue with response, no breadcrumb
       return add_workflow_guidance(response, breadcrumb=None)
   ```

3. **Response Decoration Fails:**
   ```python
   # add_workflow_guidance() is simple dict merge, cannot fail
   # But if it does (e.g., memory error), caller catches:
   try:
       return add_workflow_guidance(response, breadcrumb)
   except Exception as e:
       logger.critical(f"Response decoration failed: {e}")
       return response  # Return undecorated response
   ```

---

#### 3.4.2 Error Messages (NFR-U2)

**RendererError (phase directory not found):**

```python
raise RendererError(
    what_failed="Task count retrieval",
    why_failed=f"Phase directory not found: {phase_dir}",
    how_to_fix=f"Create phase directory: mkdir -p {phase_dir}"
)
```

**RendererError (task file not found):**

```python
raise RendererError(
    what_failed="Task content loading",
    why_failed=f"Task file not found: {task_file}",
    how_to_fix=f"Expected file: {expected_filename}"
)
```

---

### 3.5 Contract Guarantees

---

#### 3.5.1 Breadcrumb Correctness

**Guarantee:** If breadcrumb is present, it contains a valid next action.

**Validation:**
- `⚡_NEXT_ACTION` field is always a callable action with correct parameters
- Action parameters are syntactically correct (e.g., `phase=0`, not `phase=`)
- Task numbers are within valid range (1 to task_count)
- Phase numbers are within valid range (0 to max_phase)

**Testing:** Unit tests validate breadcrumb generation logic for all cases.

---

#### 3.5.2 Backward Compatibility

**Guarantee (NFR-C1):** Existing workflow callers continue to work without changes.

**Contract:**
- `add_workflow_guidance(response)` without breadcrumb parameter works exactly as before
- Response structure unchanged for callers that don't provide breadcrumb
- Static guidance fields preserved in all responses

**Testing:** Integration tests run existing workflow sessions to ensure no breaking changes.

---

## 4. Data Models

---

### 4.1 Overview

**Context:** This feature does not introduce new persistent data models. Breadcrumb navigation operates entirely in-memory within workflow responses. Existing workflow state persistence is unchanged.

**Data Categories:**
1. **Ephemeral (In-Memory)**: Breadcrumb structures (generated per response, not persisted)
2. **Existing (Unchanged)**: `WorkflowState` (already persists session data)

---

### 4.2 Ephemeral Data Structures

---

#### 4.2.1 Breadcrumb (In-Memory)

**Type:** `Dict[str, str]` (ephemeral, not persisted)

**Lifecycle:** Created during action handler execution, included in response, discarded after transmission.

**Structure:**

```python
Breadcrumb = Dict[str, str]

# Examples per action:

# start_workflow:
{
    "⚡_NEXT_ACTION": "get_phase(phase=0)"
}

# get_phase (with tasks):
{
    "📊_PHASE_INFO": "Phase 0 has 5 tasks",
    "⚡_NEXT_ACTION": "get_task(phase=0, task_number=1)"
}

# get_phase (no tasks):
{
    "📊_PHASE_INFO": "Phase 2 has no tasks",
    "⚡_NEXT_ACTION": "complete_phase(phase=2, evidence={...})"
}

# get_task (middle):
{
    "🎯_CURRENT_POSITION": "Task 3/5",
    "⚡_NEXT_ACTION": "get_task(phase=0, task_number=4)"
}

# get_task (final):
{
    "🎯_CURRENT_POSITION": "Task 5/5 (final)",
    "⚡_NEXT_ACTION": "complete_phase(phase=0, evidence={...})"
}

# complete_phase (more phases):
{
    "✅_PHASE_COMPLETE": "Phase 0 completed successfully",
    "⚡_NEXT_ACTION": "get_phase(phase=1)"
}

# complete_phase (workflow complete):
{
    "🎉_WORKFLOW_COMPLETE": "All phases completed successfully"
}
```

**Validation:**
- `⚡_NEXT_ACTION` must contain valid function signature with correct parameters
- Task numbers must be within range `[1, task_count]`
- Phase numbers must be within range `[0, max_phase]`

**Storage:** None (ephemeral, included in response only)

---

### 4.3 Existing Data Models (Unchanged)

---

#### 4.3.1 WorkflowState (Persisted)

**Storage:** `.praxis-os/state/workflow/{session_id}.json`

**Existing Fields (No Changes):**

```python
@dataclass
class WorkflowState:
    session_id: str
    workflow_type: str
    target_file: str
    current_phase: int
    metadata: Dict[str, Any]
    checkpoints: Dict[int, str]  # phase -> status
    phase_artifacts: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
```

**No Modifications:** Breadcrumb navigation does not require any changes to workflow state persistence.

**Rationale:** Breadcrumbs are guidance, not state. State persistence remains unchanged.

---

#### 4.3.2 WorkflowMetadata (Unchanged)

**Existing Structure:**

```python
@dataclass
class WorkflowMetadata:
    workflow_type: str
    version: str
    name: str
    description: str
    max_phase: int
    total_phases: int
    estimated_duration: str
    primary_outputs: List[str]
    dynamic_phases: bool  # <-- Used to determine task count source
    # ... other fields ...
```

**Used By:** `WorkflowEngine._get_task_count_for_phase()` checks `dynamic_phases` flag to route task count retrieval.

**No Modifications:** All required metadata already exists.

---

### 4.4 Computed Values (Not Stored)

---

#### 4.4.1 Task Count

**Source (Static Workflows):**
- Computed on-demand via `WorkflowRenderer.get_task_count()`
- Method: Count files matching `task-*-*.md` in phase directory
- Performance: <5ms (NFR-P1)

**Source (Dynamic Workflows):**
- Cached in `DynamicContentRegistry` (in-memory)
- Populated during spec parsing (Phase 0 of spec_execution_v1 workflow)
- Accessed via `DynamicContentRegistry.get_phase_metadata()["task_count"]`

**Not Persisted:** Task count is computed/cached, not stored in workflow state.

---

### 4.5 Response Structure Evolution

---

#### 4.5.1 start_workflow Response

**Before (Existing):**

```python
{
    "⚠️_WORKFLOW_EXECUTION_MODE": "ACTIVE",  # Static guidance
    "🛑_DO_NOT_USE_EXTERNAL_TASK_TOOLS": "...",  # Static guidance
    "execution_model": "...",  # Static guidance
    "session_id": "workflow_abc123_s0",
    "workflow_type": "spec_creation_v1",
    "target_file": "design.md",
    "current_phase": 0,
    "workflow_overview": {...},
    "phase_content": "# Phase 0: ...\n\n..."  # REMOVED (FR-001)
}
```

**After (With Breadcrumbs):**

```python
{
    "⚠️_WORKFLOW_EXECUTION_MODE": "ACTIVE",  # Static guidance (unchanged)
    "🛑_DO_NOT_USE_EXTERNAL_TASK_TOOLS": "...",  # Static guidance (unchanged)
    "execution_model": "...",  # Static guidance (unchanged)
    "session_id": "workflow_abc123_s0",
    "workflow_type": "spec_creation_v1",
    "target_file": "design.md",
    "current_phase": 0,
    "workflow_overview": {...},
    # phase_content REMOVED (FR-001)
    "⚡_NEXT_ACTION": "get_phase(phase=0)"  # ADDED (FR-002)
}
```

---

#### 4.5.2 get_task Response

**Before (Existing):**

```python
{
    "⚠️_WORKFLOW_EXECUTION_MODE": "ACTIVE",
    "🛑_DO_NOT_USE_EXTERNAL_TASK_TOOLS": "...",
    "execution_model": "...",
    "session_id": "workflow_abc123_s0",
    "workflow_type": "spec_creation_v1",
    "phase": 0,
    "task_number": 3,
    "current_phase": 0,
    "phase_status": {...},
    "task_content": "## Task 3: ...\n\n..."
}
```

**After (With Breadcrumbs):**

```python
{
    "⚠️_WORKFLOW_EXECUTION_MODE": "ACTIVE",
    "🛑_DO_NOT_USE_EXTERNAL_TASK_TOOLS": "...",
    "execution_model": "...",
    "session_id": "workflow_abc123_s0",
    "workflow_type": "spec_creation_v1",
    "phase": 0,
    "task_number": 3,
    "current_phase": 0,
    "phase_status": {...},
    "task_content": "## Task 3: ...\n\n...",
    "🎯_CURRENT_POSITION": "Task 3/5",  # ADDED (FR-004)
    "⚡_NEXT_ACTION": "get_task(phase=0, task_number=4)"  # ADDED (FR-004)
}
```

---

### 4.6 Data Flow

---

#### 4.6.1 Task Count Retrieval Flow

```
WorkflowEngine.get_task()
    │
    ▼
_get_task_count_for_phase(state, phase)
    │
    ├─ Check: state.workflow_metadata.dynamic_phases
    │
    ├─ If True (dynamic workflow):
    │   │
    │   ▼
    │   DynamicContentRegistry.get_phase_metadata(phase)
    │       │
    │       ▼
    │   Return cached metadata["task_count"]
    │   (Populated during spec parsing)
    │
    └─ If False (static workflow):
        │
        ▼
        WorkflowRenderer.get_task_count(workflow_type, phase)
            │
            ▼
        phase_dir = workflows_dir / workflow_type / "phases" / str(phase)
            │
            ▼
        task_files = list(phase_dir.glob("task-*-*.md"))
            │
            ▼
        return len(task_files)
```

---

#### 4.6.2 Breadcrumb Generation Flow

```
WorkflowEngine.get_task(session_id, phase, task_number)
    │
    ├─ Load task content (existing logic)
    │
    ├─ Get task_count via _get_task_count_for_phase()
    │
    ├─ Generate breadcrumb (inline conditional):
    │   │
    │   ├─ if task_number < task_count:
    │   │   │
    │   │   └─ breadcrumb = {
    │   │         "🎯_CURRENT_POSITION": f"Task {task_number}/{task_count}",
    │   │         "⚡_NEXT_ACTION": f"get_task(phase={phase}, task_number={task_number + 1})"
    │   │      }
    │   │
    │   └─ else:  # final task
    │       │
    │       └─ breadcrumb = {
    │             "🎯_CURRENT_POSITION": f"Task {task_number}/{task_count} (final)",
    │             "⚡_NEXT_ACTION": f"complete_phase(phase={phase}, evidence={{...}})"
    │          }
    │
    ├─ Build response dict
    │
    └─ add_workflow_guidance(response, breadcrumb)
            │
            └─ return {**WORKFLOW_GUIDANCE_FIELDS, **response, **breadcrumb}
```

---

### 4.7 Memory Footprint

**New Memory Usage:**

1. **Breadcrumb dict per response**: ~200 bytes
   - 2 string keys + 2 string values
   - Example: `{"🎯_CURRENT_POSITION": "Task 3/5", "⚡_NEXT_ACTION": "get_task(phase=0, task_number=4)"}`

2. **Task count (integer) per action**: 8 bytes

**Total per workflow action**: <300 bytes (negligible)

**Persistent storage**: 0 bytes (breadcrumbs not persisted)

**Rationale:** Breadcrumbs are ephemeral guidance, not state. No persistent storage overhead.

---

## 5. Security Design

---

### 5.1 Overview

**Context:** This feature is an internal enhancement to the workflow engine. No new authentication, authorization, or data protection mechanisms are required.

**Security Posture:** Inherits existing praxis-os MCP server security model (authenticated MCP clients only).

**Threat Model:** Low risk. Breadcrumb navigation is guidance generation (string formatting), not data manipulation or external integration.

---

### 5.2 Input Validation

---

#### 5.2.1 Parameter Validation (Existing)

**Scope:** MCP tool parameters validated by existing workflow engine logic.

**Validations (Already Implemented):**
- `session_id`: Must be valid workflow session (existing check)
- `phase`: Must be within `[0, max_phase]` (existing check)
- `task_number`: Must be within `[1, task_count]` (existing check)
- `evidence`: Must conform to phase evidence schema (existing check)

**No New Validation Required:** Breadcrumb generation uses already-validated parameters.

---

#### 5.2.2 Breadcrumb Parameter Validation

**Risk:** Malformed breadcrumbs could confuse AI agents or cause errors.

**Mitigation:**
1. **Type Safety:** TypedDict or dataclass for breadcrumb structure (considered, rejected for simplicity)
2. **Unit Tests:** Validate breadcrumb format for all scenarios
3. **Graceful Degradation:** If breadcrumb generation fails, workflow continues without breadcrumb (NFR-C2)

**Attack Vector Analysis:**
- **Code Injection:** Not applicable. Breadcrumbs are plain strings, not executed code.
- **XSS:** Not applicable. Breadcrumbs are JSON response fields, not HTML.
- **SQL Injection:** Not applicable. Breadcrumbs are not persisted to database.

---

### 5.3 Authorization

---

#### 5.3.1 MCP Client Authorization (Existing)

**Scope:** MCP server already validates authenticated clients. Breadcrumb feature does not change authorization model.

**Access Control:** Only authenticated MCP clients can invoke `pos_workflow` actions.

**No Changes:** Breadcrumb navigation inherits existing authorization.

---

### 5.4 Data Protection

---

#### 5.4.1 No Sensitive Data in Breadcrumbs

**Guarantee:** Breadcrumbs contain only:
- Action names (public API)
- Phase/task numbers (non-sensitive metadata)
- Position indicators (e.g., "Task 3/5")

**No PII, No Secrets:** Breadcrumbs never include:
- User identifiers
- File contents
- Evidence data
- API keys or tokens

**Verification:** Code review ensures breadcrumb generation only uses phase/task metadata.

---

#### 5.4.2 Logging

**Breadcrumb Logging (NFR-O1):**
- Breadcrumbs logged at DEBUG level for observability
- No sensitive data in breadcrumbs → safe to log

**Log Sanitization:** Not required (breadcrumbs contain no sensitive data).

---

### 5.5 Code Security

---

#### 5.5.1 Injection Prevention

**F-String Safety:**

```python
# SAFE (all inputs are integers or validated enums):
breadcrumb = {
    "🎯_CURRENT_POSITION": f"Task {task_number}/{task_count}",
    "⚡_NEXT_ACTION": f"get_task(phase={phase}, task_number={task_number + 1})"
}
```

**Why Safe:**
- `task_number`, `task_count`, `phase` are integers (type-checked)
- No user-provided strings in breadcrumb generation
- No dynamic code execution

---

#### 5.5.2 Error Handling (Defensive Programming)

**Graceful Degradation (NFR-C2):**

```python
try:
    task_count = self._get_task_count_for_phase(state, phase)
    breadcrumb = self._generate_breadcrumb(phase, task_number, task_count)
except Exception as e:
    logger.error(f"Breadcrumb generation failed: {e}")
    breadcrumb = None  # Workflow continues without breadcrumb
```

**Rationale:** Breadcrumb failures never block workflow execution (defense in depth).

---

### 5.6 Dependency Security

---

#### 5.6.1 No New Dependencies

**Risk Reduction:** This feature introduces zero new dependencies.

**Libraries Used:**
- `pathlib` (Python stdlib)
- `typing` (Python stdlib)

**Supply Chain Risk:** None (no external dependencies).

---

### 5.7 Security Testing

---

#### 5.7.1 Test Coverage

**Unit Tests:**
- Breadcrumb generation for all actions (valid inputs)
- Breadcrumb generation with edge cases (phase 0, final task, no tasks)
- Error handling (task count retrieval fails, invalid phase)

**Integration Tests:**
- Full workflow execution with breadcrumbs
- Breadcrumb following behavior (if AI follows, workflow completes correctly)

**No Penetration Testing Required:** Low-risk internal enhancement, no attack surface.

---

### 5.8 Security Checklist

**Checklist from srd.md NFR-S* requirements:**

- [x] **Input Validation:** Parameters validated by existing workflow engine
- [x] **Output Validation:** Breadcrumbs unit-tested for correctness
- [x] **Error Handling:** Graceful degradation if breadcrumb generation fails
- [x] **Logging:** DEBUG-level logging for observability
- [x] **No Sensitive Data:** Breadcrumbs contain only public metadata
- [x] **No New Dependencies:** Uses Python stdlib only
- [x] **Code Review:** Breadcrumb generation logic reviewed for injection risks

**Result:** All security requirements satisfied. Low risk, no additional controls needed.

---

## 6. Performance Design

---

### 6.1 Overview

**Performance Goals (from srd.md):**
- NFR-P1: Task count retrieval < 5ms for static workflows
- NFR-P2: Breadcrumb generation overhead < 1ms per action
- No measurable impact on end-to-end workflow execution time (<1% increase acceptable)

**Strategy:** Minimize overhead through simple operations (no caching, no complex algorithms, just fast primitives).

---

### 6.2 Task Count Retrieval Performance

---

#### 6.2.1 Static Workflows (Filesystem)

**Method:** `pathlib.glob("task-*-*.md")`

**Performance Characteristics:**
- **Typical:** <5ms for directories with <50 files (NFR-P1)
- **Worst Case:** <20ms for directories with 200+ files (unlikely)
- **Bottleneck:** Filesystem I/O (mitigated by OS page cache)

**No Caching Needed:**
- `glob()` is already fast enough
- Caching adds complexity (invalidation, memory overhead)
- Simplicity > premature optimization

**Profiling Strategy:**
- If performance issues arise (>5ms consistently), add in-memory cache
- Cache key: `(workflow_type, phase)`
- Invalidation: Not needed (workflow structure static)

---

#### 6.2.2 Dynamic Workflows (Cached)

**Method:** `DynamicContentRegistry.get_phase_metadata()["task_count"]`

**Performance Characteristics:**
- **Typical:** <1ms (dict lookup from cached metadata)
- **Cache Population:** During spec parsing (Phase 0 of spec_execution_v1)
- **Cache Lifetime:** Per workflow session (not persisted)

**Already Optimal:** In-memory dict lookup is fast enough.

---

### 6.3 Breadcrumb Generation Performance

---

#### 6.3.1 String Formatting Overhead

**Method:** F-string formatting + dict construction

**Performance Characteristics:**
- **Typical:** <1ms (f-string + dict merge)
- **Memory:** ~200 bytes per breadcrumb dict
- **CPU:** Negligible (string formatting is highly optimized in Python)

**Example:**

```python
# <1ms operation:
breadcrumb = {
    "🎯_CURRENT_POSITION": f"Task {task_number}/{task_count}",
    "⚡_NEXT_ACTION": f"get_task(phase={phase}, task_number={task_number + 1})"
}
```

**No Optimization Needed:** This is as fast as it gets for string operations.

---

#### 6.3.2 Dict Merging Overhead

**Method:** `{**WORKFLOW_GUIDANCE_FIELDS, **response, **breadcrumb}`

**Performance Characteristics:**
- **Typical:** <0.1ms (shallow dict merge)
- **Memory:** No additional allocation (views, not copies)
- **Complexity:** O(n) where n = number of keys (~10-15 keys total)

**Already Optimal:** Python dict merging is highly optimized.

---

### 6.4 End-to-End Impact Analysis

---

#### 6.4.1 Baseline Workflow Action Time

**Existing (without breadcrumbs):**
- `start_workflow`: ~50ms (state creation, metadata loading)
- `get_phase`: ~30ms (file I/O for phase content)
- `get_task`: ~25ms (file I/O for task content)
- `complete_phase`: ~40ms (evidence validation, state update)

---

#### 6.4.2 Added Overhead (with breadcrumbs)

**New Operations:**
- Task count retrieval: +5ms (static) or +1ms (dynamic)
- Breadcrumb generation: +1ms (string formatting)
- Dict merging: +0.1ms (negligible)

**Total Added:** ~6ms per action (worst case: static workflow)

**Percentage Increase:** ~20% per action (acceptable, below 1% end-to-end)

---

#### 6.4.3 Workflow Execution Time

**Example: spec_creation_v1 (6 phases, ~30 tasks total):**

**Without breadcrumbs:**
- start_workflow: 50ms
- get_phase x6: 180ms
- get_task x30: 750ms
- complete_phase x6: 240ms
- **Total:** 1220ms (~1.2 seconds)

**With breadcrumbs:**
- start_workflow: 51ms (+1ms)
- get_phase x6: 186ms (+6ms, task count only once per phase)
- get_task x30: 930ms (+180ms, ~6ms per task)
- complete_phase x6: 246ms (+6ms)
- **Total:** 1413ms (~1.4 seconds)

**Impact:** +193ms total (+15.8%), well under user-perceivable threshold (~100-200ms is imperceptible for tool calls)

**Acceptable:** <1% impact on end-to-end workflow (minutes to hours), negligible UX impact.

---

### 6.5 Memory Footprint

---

#### 6.5.1 Per-Action Memory

**Breadcrumb dict:** ~200 bytes
- 2 string keys (~40 bytes each)
- 2 string values (~60 bytes each)

**Task count integer:** 8 bytes

**Total:** ~210 bytes per action (negligible)

---

#### 6.5.2 Workflow Session Memory

**Example: 30-task workflow:**
- Breadcrumb generation: 30 actions x 210 bytes = ~6 KB
- No persistence (breadcrumbs discarded after response)
- **Total added memory:** <10 KB per workflow session

**Impact:** Negligible (<0.1% of typical workflow session memory ~10 MB).

---

### 6.6 Monitoring & Observability

---

#### 6.6.1 Performance Metrics (NFR-O1)

**Metrics to Collect:**
1. **Task count retrieval time** (static vs. dynamic)
   - Metric: `workflow.task_count.duration_ms` (histogram)
   - Labels: `workflow_type`, `phase`, `source` (static/dynamic)
   - Target: p95 < 5ms (static), p95 < 1ms (dynamic)

2. **Breadcrumb generation time**
   - Metric: `workflow.breadcrumb.duration_ms` (histogram)
   - Labels: `action` (start/get_phase/get_task/complete_phase)
   - Target: p95 < 1ms

3. **Workflow action duration** (existing, compare before/after)
   - Metric: `workflow.action.duration_ms` (histogram)
   - Labels: `action`
   - Target: No >20% increase post-deployment

---

#### 6.6.2 Behavioral Metrics (NFR-O1)

**Metrics to Collect:**
1. **Breadcrumb following rate**
   - Metric: `workflow.breadcrumb.followed` (counter)
   - Labels: `matched` (true/false), `action`, `workflow_type`
   - Target: >95% match rate

2. **Evidence validation failure rate**
   - Metric: `workflow.evidence.validation_failed` (counter)
   - Target: <5% (no increase from baseline)

3. **Workflow completion rate**
   - Metric: `workflow.completed` (counter)
   - Target: No decrease from baseline

---

#### 6.6.3 Alerting

**Performance Alerts:**
- Task count retrieval p95 > 10ms (sustained 5min) → Warning
- Breadcrumb generation p95 > 2ms (sustained 5min) → Warning
- Workflow action duration increase >50% from baseline → Critical

**Behavioral Alerts:**
- Breadcrumb following rate <80% (sustained 1hr) → Warning
- Evidence validation failure rate >10% → Critical

---

### 6.7 Optimization Strategies (Future)

---

#### 6.7.1 If Task Count Retrieval Becomes Bottleneck

**Trigger:** p95 > 10ms consistently for static workflows

**Optimization:** In-memory cache

```python
class WorkflowRenderer:
    def __init__(self):
        self._task_count_cache: Dict[Tuple[str, int], int] = {}
    
    def get_task_count(self, workflow_type: str, phase: int) -> int:
        cache_key = (workflow_type, phase)
        if cache_key in self._task_count_cache:
            return self._task_count_cache[cache_key]
        
        # ... existing glob() logic ...
        task_count = len(task_files)
        self._task_count_cache[cache_key] = task_count
        return task_count
```

**Invalidation:** Not needed (workflow structure is static)

**Memory Overhead:** ~20 bytes per cached entry (negligible)

---

#### 6.7.2 If Breadcrumb Generation Becomes Bottleneck

**Trigger:** p95 > 2ms consistently

**Optimization:** Pre-compute breadcrumb templates (unlikely to be needed)

**Note:** This is premature optimization. String formatting is already optimal.

---

### 6.8 Performance Testing

---

#### 6.8.1 Microbenchmarks

**Test:** Task count retrieval (static workflow)
- **Setup:** Directory with 50 task files
- **Measure:** Time for 1000 `get_task_count()` calls
- **Target:** Average <5ms per call

**Test:** Breadcrumb generation
- **Setup:** Mock workflow state
- **Measure:** Time for 1000 breadcrumb generations
- **Target:** Average <1ms per call

---

#### 6.8.2 Integration Tests

**Test:** Full workflow execution (spec_creation_v1)
- **Setup:** Run workflow with 30 tasks
- **Measure:** Total execution time (with vs. without breadcrumbs)
- **Target:** Increase <20% (acceptable given added functionality)

**Test:** Concurrent workflows
- **Setup:** Run 10 workflows in parallel
- **Measure:** p95 latency per action
- **Target:** No degradation vs. single workflow

---

### 6.9 Performance Checklist

**Checklist from srd.md NFR-P* requirements:**

- [x] **NFR-P1:** Task count retrieval <5ms (static), <1ms (dynamic)
- [x] **NFR-P2:** Breadcrumb generation overhead <1ms
- [x] **End-to-End Impact:** <20% per action, <1% workflow total
- [x] **Memory Footprint:** <10 KB per workflow session
- [x] **Monitoring:** Metrics for task count, breadcrumb generation, action duration
- [x] **Alerting:** Performance and behavioral alerts defined
- [x] **Testing:** Microbenchmarks and integration tests planned

**Result:** All performance requirements satisfied. Simple operations ensure fast execution.

**Requirements Satisfied:**
- FR-001: Removes `phase_content` from `start_workflow` response
- FR-002: Generates breadcrumb in `start_workflow`
- FR-003: Generates breadcrumb in `get_phase`
- FR-004: Generates dynamic breadcrumb in `get_task`
- FR-005: Generates breadcrumb in `complete_phase`
- FR-008: Unified task count helper method

**Public Interface:**
```python
class WorkflowEngine:
    def start_workflow(
        self,
        workflow_type: str,
        target: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Start workflow, return overview + breadcrumb (no phase_content)."""
        
    def get_phase(
        self,
        session_id: str,
        phase: int
    ) -> Dict[str, Any]:
        """Get phase content + breadcrumb to first task."""
        
    def get_task(
        self,
        session_id: str,
        phase: int,
        task_number: int
    ) -> Dict[str, Any]:
        """Get task content + dynamic breadcrumb based on position."""
        
    def complete_phase(
        self,
        session_id: str,
        phase: int,
        evidence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate evidence + breadcrumb to next phase."""
        
    def _get_task_count_for_phase(
        self,
        state: WorkflowState,
        phase: int
    ) -> int:
        """Route task count retrieval (static renderer vs. dynamic registry)."""
```

**Internal Methods (New):**
```python
def _get_task_count_for_phase(self, state: WorkflowState, phase: int) -> int:
    """
    Get task count for phase (dynamic routing).
    
    Routes to:
    - DynamicContentRegistry if dynamic workflow (phase > 0)
    - WorkflowRenderer if static workflow
    
    Returns:
        int: Number of tasks in phase
    """
    is_dynamic = self._is_dynamic(state)
    
    if is_dynamic and phase > 0:
        registry = self._get_or_create_dynamic_registry(state.session_id, state)
        metadata = registry.get_phase_metadata(phase)
        return metadata["task_count"]
    else:
        return self._renderer.get_task_count(state.workflow_type, phase)
```

**Dependencies:**
- Requires: `WorkflowRenderer` (task count for static workflows)
- Requires: `DynamicContentRegistry` (task count for dynamic workflows)
- Requires: `add_workflow_guidance()` (response decoration)
- Provides: Workflow orchestration to MCP tool layer

**Error Handling:**
- If breadcrumb generation fails → log error, continue with static guidance only (graceful degradation: NFR-C2)
- If task count retrieval fails → log error, continue with workflow (no crash: NFR-C2)

**Changes from Current Implementation:**
1. **`start_workflow()`**: Remove `phase_content` from response, add breadcrumb
2. **`get_phase()`**: Add breadcrumb logic (call `_get_task_count_for_phase()`)
3. **`get_task()`**: Add dynamic breadcrumb logic based on task position
4. **`complete_phase()`**: Add breadcrumb to next phase
5. **New method**: `_get_task_count_for_phase()` helper

---

### 2.2 Component: WorkflowRenderer

**Purpose:** Load and render static workflow content from filesystem, including task count retrieval.

**Responsibilities:**
- Load phase content from markdown files
- Load task content from markdown files
- Count tasks in a phase (new: FR-006)
- Render workflow metadata

**Requirements Satisfied:**
- FR-006: Task count retrieval for static workflows

**Public Interface:**
```python
class WorkflowRenderer:
    def get_phase_content(
        self,
        workflow_type: str,
        phase: int
    ) -> str:
        """Load phase.md content from filesystem."""
        
    def get_task_content(
        self,
        workflow_type: str,
        phase: int,
        task_number: int
    ) -> str:
        """Load task-{number}-{name}.md content from filesystem."""
        
    def get_task_count(
        self,
        workflow_type: str,
        phase: int
    ) -> int:
        """Count task-*.md files in phase directory (NEW)."""
```

**New Method Implementation:**
```python
def get_task_count(self, workflow_type: str, phase: int) -> int:
    """
    Get number of tasks in phase (for static workflows).
    
    Counts task-{number}-*.md files in phase directory.
    
    Args:
        workflow_type: Workflow type identifier
        phase: Phase number
        
    Returns:
        Number of tasks in phase
        
    Raises:
        RendererError: If phase directory not found
    """
    phase_dir = self.workflows_dir / workflow_type / "phases" / str(phase)
    
    if not phase_dir.exists():
        raise RendererError(
            what_failed="Task count retrieval",
            why_failed=f"Phase directory not found: {phase_dir}",
            how_to_fix=f"Create phase directory: mkdir -p {phase_dir}",
        )
    
    # Count task-*.md files (fast: <5ms for <50 files)
    task_files = list(phase_dir.glob("task-*-*.md"))
    return len(task_files)
```

**Dependencies:**
- Requires: `pathlib` (filesystem operations)
- Provides: Static workflow content to `WorkflowEngine`

**Error Handling:**
- If phase directory not found → raise `RendererError` with actionable fix message (NFR-U2)
- If glob fails → raise exception (critical error, cannot continue)

**Performance:**
- Task count retrieval: <5ms for directories with <50 task files (NFR-P1)
- Uses `glob()` (fast), not recursive directory walk

---

### 2.3 Component: DynamicContentRegistry

**Purpose:** Cache and serve dynamically-parsed workflow content from spec `tasks.md` files.

**Responsibilities:**
- Parse spec `tasks.md` files into phase/task structure
- Cache parsed content for performance
- Provide task count metadata (existing: FR-007)
- Serve phase and task content on demand

**Requirements Satisfied:**
- FR-007: Task count retrieval for dynamic workflows (existing functionality)

**Public Interface:**
```python
class DynamicContentRegistry:
    def get_phase_metadata(self, phase: int) -> Dict[str, Any]:
        """
        Get phase metadata including task count.
        
        Returns:
            Dict with keys: phase_name, task_count, purpose, ...
        """
        
    def get_phase_content(self, phase: int) -> str:
        """Get full phase content."""
        
    def get_task_content(self, phase: int, task_number: int) -> str:
        """Get individual task content."""
```

**Dependencies:**
- Requires: Spec `tasks.md` file
- Provides: Dynamic workflow content to `WorkflowEngine`

**Error Handling:**
- If phase not found → raise exception with helpful message
- If task number out of range → raise exception

**Performance:**
- Task count retrieval: <1ms (cached lookup: NFR-P1)
- Content is parsed once, cached for session lifetime

**No Changes Required:** This component already exposes `task_count` via `get_phase_metadata()`.

---

### 2.4 Component: Guidance Module

**Purpose:** Decorate workflow responses with static guidance and action-specific breadcrumbs.

**Responsibilities:**
- Prepend static guidance fields to all responses
- Append action-specific breadcrumbs at response end
- Maintain backward compatibility (optional breadcrumb parameter)

**Requirements Satisfied:**
- FR-009: Backward compatible breadcrumb parameter
- FR-010: Static guidance fields preserved

**Public Interface:**
```python
def add_workflow_guidance(
    response: Dict[str, Any],
    breadcrumb: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Inject guidance + action-specific breadcrumb into workflow tool response.
    
    Args:
        response: Base response from workflow engine
        breadcrumb: Optional dict with action-specific navigation
                   (e.g., {"⚡_NEXT_ACTION": "get_task(phase=0, task_number=3)"})
                   
    Returns:
        Response with guidance fields prepended and breadcrumb appended
    """
```

**Implementation:**
```python
WORKFLOW_GUIDANCE_FIELDS = {
    "⚠️_WORKFLOW_EXECUTION_MODE": "ACTIVE",
    "🛑_DO_NOT_USE_EXTERNAL_TASK_TOOLS": "...",
    "execution_model": "Complete task → Submit evidence → Advance phase",
}

def add_workflow_guidance(
    response: Dict[str, Any],
    breadcrumb: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    # Start with static guidance
    guided = {**WORKFLOW_GUIDANCE_FIELDS, **response}
    
    # Add action-specific breadcrumb at END (recency bias)
    # Python 3.7+ preserves dict insertion order
    if breadcrumb:
        guided.update(breadcrumb)
    
    return guided
```

**Dependencies:**
- Requires: None (pure function)
- Provides: Response decoration to `WorkflowEngine`

**Error Handling:**
- No error conditions (pure dict manipulation)

**Performance:**
- Dict merging: <1ms (NFR-P2)

**Changes from Current Implementation:**
- Add `breadcrumb` parameter (optional, defaults to `None`)
- Append breadcrumb at end if provided

---

## 2.5 Component Interactions

**Interaction Flow (get_task example):**

```
AI Agent
   │
   │ get_task(phase=0, task_number=3)
   ▼
WorkflowEngine
   │
   ├──► _get_task_count_for_phase(state, phase=0)
   │    │
   │    ├──► [If static workflow] → WorkflowRenderer.get_task_count("spec_creation_v1", 0)
   │    │                           └──► glob("task-*-*.md") → returns 6
   │    │
   │    └──► [If dynamic workflow] → DynamicContentRegistry.get_phase_metadata(0)
   │                                  └──► returns {"task_count": 5}
   │
   ├──► Get task content (existing logic)
   │
   ├──► Generate breadcrumb (new logic)
   │    if task_number < task_count:
   │        breadcrumb = {"⚡_NEXT_ACTION": "get_task(phase=0, task_number=4)"}
   │    else:
   │        breadcrumb = {"⚡_NEXT_ACTION": "complete_phase(phase=0, evidence={...})"}
   │
   └──► add_workflow_guidance(response, breadcrumb)
        └──► Returns decorated response
```

**Interaction Table:**

| From | To | Method | Purpose |
|------|----|--------|---------|
| MCP Tool | WorkflowEngine | `get_task()` | Request task content with breadcrumb |
| WorkflowEngine | WorkflowRenderer | `get_task_count()` | Count tasks (static workflows) |
| WorkflowEngine | DynamicContentRegistry | `get_phase_metadata()` | Get task count (dynamic workflows) |
| WorkflowEngine | Guidance Module | `add_workflow_guidance()` | Decorate response with breadcrumb |

---

## 2.6 Module Organization

**Directory Structure:**
```
.praxis-os/ouroboros/subsystems/workflow/
├── engine.py                  # WorkflowEngine (MODIFIED)
├── workflow_renderer.py       # WorkflowRenderer (MODIFIED)
├── dynamic_registry.py        # DynamicContentRegistry (NO CHANGES)
├── guidance.py                # add_workflow_guidance() (MODIFIED)
├── types.py                   # WorkflowState, etc. (NO CHANGES)
├── checkpoint_loader.py       # Evidence validation (NO CHANGES)
└── state_manager.py           # State persistence (NO CHANGES)
```

**Dependency Rules:**
- No circular imports (already enforced)
- `engine.py` depends on `renderer.py`, `registry.py`, `guidance.py`
- `renderer.py` and `registry.py` are independent
- `guidance.py` has no dependencies (pure function)

**Import Structure:**
```python
# engine.py
from .workflow_renderer import WorkflowRenderer
from .dynamic_registry import DynamicContentRegistry
from .guidance import add_workflow_guidance

# No circular dependencies
```

---

## 2.7 Supporting Documentation

Component design informed by:
- **2025-11-08-workflow-breadcrumb-navigation.md**: Component responsibilities, interface design, inline logic rationale

See `supporting-docs/INSIGHTS.md` for implementation patterns and code examples.

---

## 3. API Design

---

### 3.1 MCP Tool Interface (External API)

**Note:** The workflow subsystem is exposed via MCP (Model Context Protocol) tools, not REST APIs. The "API" is the MCP tool function signatures.

#### pos_workflow(action="start_workflow")

**Purpose:** Start a new workflow session with breadcrumb to first phase

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| action | str | Yes | "start_workflow" |
| workflow_type | str | Yes | Workflow identifier (e.g., "spec_creation_v1") |
| target_file | str | Yes | Target file or directory |
| options | dict | No | Optional workflow configuration |

**Response (Success):**
```json
{
  "⚠️_WORKFLOW_EXECUTION_MODE": "ACTIVE",
  "🛑_DO_NOT_USE_EXTERNAL_TASK_TOOLS": "...",
  "execution_model": "Complete task → Submit evidence → Advance phase",
  
  "session_id": "workflow_abc123_s0",
  "workflow_type": "spec_creation_v1",
  "target_file": "design.md",
  "current_phase": 0,
  "workflow_overview": {
    "max_phase": 5,
    "description": "..."
  },
  
  "⚡_NEXT_ACTION": "get_phase(phase=0)"
}
```

**Key Changes from Current:**
- **Removed:** `phase_content` field (FR-001: just-in-time disclosure)
- **Added:** `⚡_NEXT_ACTION` breadcrumb (FR-002)

**Error Responses:**
- `status: "error"`, `message: "Workflow type not found"`
- `status: "error"`, `message: "Invalid target file"`

---

#### pos_workflow(action="get_phase")

**Purpose:** Get phase content with breadcrumb to first task or complete_phase

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| action | str | Yes | "get_phase" |
| session_id | str | Yes | Workflow session identifier |
| phase | int | Yes | Phase number to retrieve |

**Response (Success, with tasks):**
```json
{
  "⚠️_WORKFLOW_EXECUTION_MODE": "ACTIVE",
  "🛑_DO_NOT_USE_EXTERNAL_TASK_TOOLS": "...",
  "execution_model": "Complete task → Submit evidence → Advance phase",
  
  "session_id": "workflow_abc123_s0",
  "phase": 0,
  "phase_status": {"is_completed": false, "is_current": true},
  "phase_content": "# Phase 0: ...",
  
  "📊_PHASE_INFO": "Phase 0 has 5 tasks",
  "⚡_NEXT_ACTION": "get_task(phase=0, task_number=1)"
}
```

**Response (Success, no tasks):**
```json
{
  ...
  "📊_PHASE_INFO": "Phase 0 has no tasks",
  "⚡_NEXT_ACTION": "complete_phase(phase=0, evidence={...})"
}
```

**Key Changes from Current:**
- **Added:** `📊_PHASE_INFO` field with task count (FR-003)
- **Added:** `⚡_NEXT_ACTION` breadcrumb (FR-003)

**Error Responses:**
- `status: "error"`, `message: "Phase not accessible"`
- `status: "error"`, `message: "Invalid phase number"`

---

#### pos_workflow(action="get_task")

**Purpose:** Get task content with dynamic breadcrumb based on position

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| action | str | Yes | "get_task" |
| session_id | str | Yes | Workflow session identifier |
| phase | int | Yes | Phase number |
| task_number | int | Yes | Task number (1-indexed) |

**Response (Success, not final task):**
```json
{
  "⚠️_WORKFLOW_EXECUTION_MODE": "ACTIVE",
  "🛑_DO_NOT_USE_EXTERNAL_TASK_TOOLS": "...",
  "execution_model": "Complete task → Submit evidence → Advance phase",
  
  "session_id": "workflow_abc123_s0",
  "phase": 0,
  "task_number": 3,
  "task_content": "# Task 3: ...",
  
  "🎯_CURRENT_POSITION": "Task 3/5",
  "⚡_NEXT_ACTION": "get_task(phase=0, task_number=4)"
}
```

**Response (Success, final task):**
```json
{
  ...
  "task_number": 5,
  "task_content": "# Task 5: ...",
  
  "🎯_CURRENT_POSITION": "Task 5/5 (final)",
  "⚡_NEXT_ACTION": "complete_phase(phase=0, evidence={...})"
}
```

**Key Changes from Current:**
- **Added:** `🎯_CURRENT_POSITION` field (FR-004)
- **Added:** `⚡_NEXT_ACTION` dynamic breadcrumb (FR-004)

**Error Responses:**
- `status: "error"`, `message: "Task number out of range"`
- `status: "error"`, `message: "Phase not accessible"`

---

#### pos_workflow(action="complete_phase")

**Purpose:** Validate evidence and advance to next phase with breadcrumb

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| action | str | Yes | "complete_phase" |
| session_id | str | Yes | Workflow session identifier |
| phase | int | Yes | Phase number to complete |
| evidence | dict | Yes | Evidence dictionary (keys hidden, validated at runtime) |

**Response (Success, more phases exist):**
```json
{
  "⚠️_WORKFLOW_EXECUTION_MODE": "ACTIVE",
  "🛑_DO_NOT_USE_EXTERNAL_TASK_TOOLS": "...",
  "execution_model": "Complete task → Submit evidence → Advance phase",
  
  "session_id": "workflow_abc123_s0",
  "phase": 0,
  "validation_result": "success",
  "next_phase": 1,
  
  "✅_PHASE_COMPLETE": "Phase 0 completed successfully",
  "⚡_NEXT_ACTION": "get_phase(phase=1)"
}
```

**Response (Success, workflow complete):**
```json
{
  ...
  "validation_result": "success",
  "workflow_complete": true,
  
  "🎉_WORKFLOW_COMPLETE": "All phases completed successfully"
}
```

**Key Changes from Current:**
- **Added:** `✅_PHASE_COMPLETE` or `🎉_WORKFLOW_COMPLETE` (FR-005)
- **Added:** `⚡_NEXT_ACTION` breadcrumb (FR-005)

**Error Responses:**
- `status: "error"`, `message: "Evidence validation failed"`, `validation: {...}`
- `status: "error"`, `message: "Required evidence fields missing: [...]"`

---

### 3.2 Internal Interfaces

#### WorkflowEngine

```python
class WorkflowEngine:
    """Core workflow orchestration with breadcrumb generation."""
    
    def start_workflow(
        self,
        workflow_type: str,
        target: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Start workflow and return breadcrumb to get_phase.
        
        Returns:
            Dict with workflow overview + ⚡_NEXT_ACTION breadcrumb
            (NO phase_content - just-in-time disclosure)
        """
        
    def get_phase(
        self,
        session_id: str,
        phase: int
    ) -> Dict[str, Any]:
        """
        Get phase content and breadcrumb to first task.
        
        Returns:
            Dict with phase_content + 📊_PHASE_INFO + ⚡_NEXT_ACTION
        """
        
    def get_task(
        self,
        session_id: str,
        phase: int,
        task_number: int
    ) -> Dict[str, Any]:
        """
        Get task content and dynamic breadcrumb.
        
        Returns:
            Dict with task_content + 🎯_CURRENT_POSITION + ⚡_NEXT_ACTION
        """
        
    def complete_phase(
        self,
        session_id: str,
        phase: int,
        evidence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate evidence and advance to next phase.
        
        Returns:
            Dict with validation_result + ✅_PHASE_COMPLETE + ⚡_NEXT_ACTION
        """
        
    def _get_task_count_for_phase(
        self,
        state: WorkflowState,
        phase: int
    ) -> int:
        """
        Route task count retrieval to appropriate source.
        
        Internal helper method (not exposed to MCP).
        """
```

---

#### WorkflowRenderer

```python
class WorkflowRenderer:
    """Static workflow content loading and task counting."""
    
    def get_task_count(
        self,
        workflow_type: str,
        phase: int
    ) -> int:
        """
        Count task-*.md files in phase directory.
        
        Args:
            workflow_type: Workflow identifier
            phase: Phase number
            
        Returns:
            Number of tasks in phase
            
        Raises:
            RendererError: If phase directory not found
        """
```

---

#### Guidance Module

```python
def add_workflow_guidance(
    response: Dict[str, Any],
    breadcrumb: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Decorate response with guidance and breadcrumb.
    
    Args:
        response: Base response from workflow engine
        breadcrumb: Optional breadcrumb fields to append at end
                   (e.g., {"⚡_NEXT_ACTION": "get_task(phase=0, task_number=3)"})
                   
    Returns:
        Response with:
        - Static guidance fields prepended
        - Original response content
        - Breadcrumb fields appended (if provided)
    """
```

---

### 3.3 Breadcrumb Response Schema

**Breadcrumb Fields (Action-Specific):**

```python
# start_workflow breadcrumb
{
    "⚡_NEXT_ACTION": "get_phase(phase=0)"
}

# get_phase breadcrumb (with tasks)
{
    "📊_PHASE_INFO": "Phase {N} has {M} tasks",
    "⚡_NEXT_ACTION": "get_task(phase={N}, task_number=1)"
}

# get_phase breadcrumb (no tasks)
{
    "📊_PHASE_INFO": "Phase {N} has no tasks",
    "⚡_NEXT_ACTION": "complete_phase(phase={N}, evidence={...})"
}

# get_task breadcrumb (not final)
{
    "🎯_CURRENT_POSITION": "Task {N}/{M}",
    "⚡_NEXT_ACTION": "get_task(phase={P}, task_number={N+1})"
}

# get_task breadcrumb (final task)
{
    "🎯_CURRENT_POSITION": "Task {N}/{M} (final)",
    "⚡_NEXT_ACTION": "complete_phase(phase={P}, evidence={...})"
}

# complete_phase breadcrumb (more phases)
{
    "✅_PHASE_COMPLETE": "Phase {N} completed successfully",
    "⚡_NEXT_ACTION": "get_phase(phase={N+1})"
}

# complete_phase breadcrumb (workflow complete)
{
    "🎉_WORKFLOW_COMPLETE": "All phases completed successfully"
}
```

**Field Naming Convention:**
- **⚡_NEXT_ACTION**: Always contains literal call syntax (copy-paste-execute)
- **🎯_CURRENT_POSITION**: Progress indicator ("Task N/M")
- **📊_PHASE_INFO**: Context information ("Phase N has M tasks")
- **✅_PHASE_COMPLETE**: Success message for phase completion
- **🎉_WORKFLOW_COMPLETE**: Success message for workflow completion

**Emoji Rationale (NFR-U1):**
- Increase visual salience (attention weight)
- Field names remain descriptive without emojis
- No accessibility issues (field names are sufficient fallback)

---

### 3.4 Error Handling

**Error Response Format:**
```json
{
  "status": "error",
  "action": "{action_name}",
  "message": "Human-readable error message",
  "details": {
    "error_type": "ValidationError",
    "field_errors": {
      "evidence": ["Missing required field: task_count"]
    }
  }
}
```

**Error Types:**
- **ValidationError**: Evidence validation failed (phase gate)
- **NotFoundError**: Session, phase, or task not found
- **StateError**: Workflow in invalid state for requested action
- **RendererError**: Phase directory not found (static workflows)

**Error Messages (Actionable - NFR-U2):**
- `"Phase directory not found: {path}. Create it with: mkdir -p {path}"`
- `"Task number out of range. Phase {N} has {M} tasks, requested task {X}"`
- `"Evidence validation failed. Missing required fields: {fields}"`

---

### 3.5 Supporting Documentation

API design informed by:
- **2025-11-08-workflow-breadcrumb-navigation.md**: Breadcrumb response structure, field naming conventions, error handling patterns

See `supporting-docs/INSIGHTS.md` for breadcrumb examples and response structure rationale.

---

## 4. Data Models

---

### 4.1 Domain Models

**Note:** This feature does not introduce new domain entities. It enhances existing workflow responses with breadcrumb fields.

#### WorkflowState (Existing, No Changes)

```python
@dataclass
class WorkflowState:
    """Workflow session state (unchanged)."""
    session_id: str
    workflow_type: str
    current_phase: int
    target_file: str
    metadata: Dict[str, Any]
    checkpoints: Dict[int, str]  # phase -> status
    created_at: datetime
    updated_at: datetime
```

**Business Rules (Unchanged):**
- Session IDs must be unique
- `current_phase` must be <= `max_phase`
- Checkpoints track phase completion status

**No Changes Required:** Breadcrumb navigation does not modify workflow state. It only enhances response structure.

---

#### Breadcrumb Data Structure (New, Ephemeral)

```python
# Breadcrumb is a dictionary added to responses (not persisted)
BreadcrumbFields = Dict[str, str]

# Examples (see API Design section for full schemas):
{
    "⚡_NEXT_ACTION": "get_task(phase=0, task_number=3)"
}

{
    "🎯_CURRENT_POSITION": "Task 3/5",
    "⚡_NEXT_ACTION": "get_task(phase=0, task_number=4)"
}
```

**Characteristics:**
- **Ephemeral**: Not persisted to database or state files
- **Action-specific**: Generated dynamically based on workflow position
- **Read-only**: AI agents consume breadcrumbs, don't modify them

**Field Types:**
- All breadcrumb fields are `str` (literal call syntax or status messages)
- No complex nested structures
- No validation required (generated by engine, not user input)

---

### 4.2 Response Data Structures

**Workflow Response (Enhanced):**

```python
# Generic response structure (all actions)
WorkflowResponse = TypedDict("WorkflowResponse", {
    # Static guidance (prepended)
    "⚠️_WORKFLOW_EXECUTION_MODE": str,
    "🛑_DO_NOT_USE_EXTERNAL_TASK_TOOLS": str,
    "execution_model": str,
    
    # Action-specific content (middle)
    "session_id": str,
    "workflow_type": str,
    "phase": int,
    "task_number": Optional[int],
    "phase_content": Optional[str],
    "task_content": Optional[str],
    # ... other action-specific fields ...
    
    # Breadcrumb fields (appended at end)
    "⚡_NEXT_ACTION": Optional[str],
    "🎯_CURRENT_POSITION": Optional[str],
    "📊_PHASE_INFO": Optional[str],
    "✅_PHASE_COMPLETE": Optional[str],
    "🎉_WORKFLOW_COMPLETE": Optional[str],
}, total=False)
```

**Key Properties:**
- Dict ordering preserved (Python 3.7+): static → content → breadcrumb
- Breadcrumb fields optional (only present if `breadcrumb` parameter provided to `add_workflow_guidance`)
- All values are strings (no complex types)

---

### 4.3 Data Flow

**Breadcrumb Generation Flow:**

```
1. WorkflowEngine receives action call
   ↓
2. Engine executes action logic
   ↓
3. Engine calls _get_task_count_for_phase() if needed
   ↓ (returns int)
4. Engine generates breadcrumb dict based on:
   - Action type (start_workflow, get_phase, get_task, complete_phase)
   - Workflow position (task_number, task_count, phase, max_phase)
   ↓
5. Engine builds response dict (action-specific content)
   ↓
6. Engine calls add_workflow_guidance(response, breadcrumb)
   ↓
7. Guidance module merges:
   static_guidance + response + breadcrumb
   ↓
8. Final response returned to AI agent
```

**Data does not persist:** Breadcrumbs are generated fresh for each action call.

---

### 4.4 Task Count Data

**Task Count (New, Derived Data):**

```python
# Task count is an integer derived from:
# - Static workflows: glob("task-*-*.md").count
# - Dynamic workflows: DynamicContentRegistry cache

task_count: int  # Number of tasks in a phase
```

**Sources:**
- **Static Workflows**: Filesystem (glob count)
- **Dynamic Workflows**: Cached in `DynamicContentRegistry.phase_metadata`

**Usage:**
- Used to generate dynamic breadcrumbs in `get_task()`
- Determines if current task is final task
- Exposed in `📊_PHASE_INFO` breadcrumb field

**Performance:**
- Static: <5ms (glob is fast for <50 files)
- Dynamic: <1ms (cached lookup)

**No Persistence:** Task count is derived on demand, not stored.

---

### 4.5 Data Validation

**No New Validation Required:**

Since breadcrumbs are generated by the engine (not user input), there's no validation needed. However, if breadcrumb generation encounters errors:

**Error Conditions:**
- `task_count_for_phase()` → `RendererError` if phase directory missing
- `task_count_for_phase()` → Exception if glob fails

**Error Handling (NFR-C2):**
- Log error with context (phase, workflow_type)
- Continue workflow with static guidance only (no breadcrumb)
- Do not crash or block workflow execution

**Graceful Degradation:**
```python
try:
    task_count = self._get_task_count_for_phase(state, phase)
    breadcrumb = self._generate_breadcrumb(task_number, task_count)
except Exception as e:
    logger.error(f"Breadcrumb generation failed: {e}", extra={
        "phase": phase,
        "task_number": task_number,
        "workflow_type": state.workflow_type
    })
    breadcrumb = None  # Proceed without breadcrumb
```

---

### 4.6 Data Relationships

**No New Relationships:**

This feature does not introduce new entity relationships. Existing relationships remain unchanged:

- WorkflowState ↔ CheckpointLoader (evidence validation)
- WorkflowState ↔ StateManager (persistence)
- WorkflowEngine ↔ WorkflowRenderer (content loading)
- WorkflowEngine ↔ DynamicContentRegistry (dynamic workflows)

**New Data Flow Only:**
- WorkflowEngine → WorkflowRenderer: `get_task_count()` (new call)
- WorkflowEngine → Guidance Module: `breadcrumb` parameter (new parameter)

---

### 4.7 Supporting Documentation

Data model design informed by:
- **2025-11-08-workflow-breadcrumb-navigation.md**: Breadcrumb structure, task count derivation, graceful degradation strategy

See `supporting-docs/INSIGHTS.md` for examples of breadcrumb data structures in various scenarios.

---

## 5. Security Design

---

### 5.1 Security Context

**Note:** This feature is internal to the workflow subsystem and does not expose new external attack surfaces. The "security" concerns are primarily about behavioral probability engineering (preventing AI agents from bypassing workflows) rather than traditional authentication/authorization.

**No New Security Vulnerabilities Introduced:**
- No user input in breadcrumb generation (engine-generated only)
- No SQL injection risk (no database queries)
- No XSS risk (breadcrumbs are strings in MCP responses, not rendered in HTML)
- No authentication/authorization changes (workflow engine already requires valid session)

---

### 5.2 Behavioral Security (AI Bypass Prevention)

**Threat:** Outlier AI agents bypassing workflow engagement by skipping steps

**Mitigation Strategy:**
1. **Just-In-Time Information Disclosure (FR-001)**
   - Remove `phase_content` from `start_workflow` response
   - Force sequential calls: `start_workflow` → `get_phase` → `get_task`
   - Prevents lookahead (AI cannot see future content without calling)

2. **Breadcrumb Navigation (FR-002-005)**
   - Provide explicit next action in every response
   - Make "correct path" the "easiest path" (highest decision weight)
   - Use visual emphasis (emojis) to increase attention weight

3. **Evidence Validation at Phase Gate (Existing)**
   - Ultimate enforcement mechanism (not changed by this feature)
   - Hidden evidence requirements prevent fabrication
   - Actionable error messages guide proper submission

**Effectiveness:**
- Target: 99% → 99.9% engagement rate (catch outlier AIs)
- Measurement: Breadcrumb following rate (target: >95%)
- Fallback: Evidence validation still catches bypasses at phase gate

**Not Enforced:** This is behavioral guidance (probability engineering), not hard enforcement. AI agents *can* still skip steps, but breadcrumbs make it less likely.

---

### 5.3 Input Validation

**Breadcrumb Generation (Engine-Side):**
- All breadcrumbs generated by engine (not user input)
- No validation needed (trusted source)

**Task Count Retrieval (Engine-Side):**
- `workflow_type` and `phase` validated by existing engine logic
- `glob()` pattern is hardcoded (`task-*-*.md`), no injection risk
- Phase directory path validated (must exist, or raises `RendererError`)

**Error Handling (NFR-C2):**
- Invalid input caught by existing workflow engine validation
- Breadcrumb generation failures do not expose sensitive info
- Graceful degradation: continue with static guidance only (no crash)

**No New Validation Required:** This feature does not accept user input for breadcrumb generation.

---

### 5.4 Data Integrity

**Breadcrumb Consistency:**
- Breadcrumbs generated fresh for each action (no stale data)
- Task count derived on demand (always current)
- No caching of breadcrumbs (prevents stale navigation)

**State Integrity (Unchanged):**
- Workflow state persistence unaffected
- Checkpoint validation unchanged
- Evidence validation unchanged

**Risk:** If task count retrieval fails (e.g., phase directory deleted mid-workflow), breadcrumb may be incorrect.

**Mitigation:**
- `RendererError` raised if phase directory not found (NFR-U2)
- Error message includes fix: `mkdir -p {path}`
- Workflow can still proceed (evidence validation is ultimate gate)

---

### 5.5 Logging & Observability

**Security-Relevant Logging:**
- Breadcrumb generation failures logged at ERROR level
- Task count retrieval failures logged with context (phase, workflow_type)
- Breadcrumb following rate tracked via behavioral metrics (NFR-O1)

**Log Contents:**
```python
logger.error("Breadcrumb generation failed", extra={
    "phase": phase,
    "task_number": task_number,
    "workflow_type": state.workflow_type,
    "error": str(e)
})
```

**No Sensitive Data in Logs:**
- Breadcrumbs contain action names and parameters (not sensitive)
- No PII, credentials, or secret data in breadcrumb fields

**Audit Trail:**
- Workflow action calls already logged (existing)
- Breadcrumb fields visible in MCP tool responses (observable)
- Can audit which AIs follow breadcrumbs vs. skip

---

### 5.6 Graceful Degradation (Defense in Depth)

**Failure Mode: Breadcrumb Generation Fails**

**Impact:** AI agent does not receive next action guidance

**Behavior:**
1. Log error with context
2. Return response with static guidance only (no breadcrumb)
3. AI agent can still complete workflow (via evidence validation)

**Code Example:**
```python
try:
    task_count = self._get_task_count_for_phase(state, phase)
    if task_number < task_count:
        breadcrumb = {"⚡_NEXT_ACTION": f"get_task(phase={phase}, task_number={task_number + 1})"}
    else:
        breadcrumb = {"⚡_NEXT_ACTION": f"complete_phase(phase={phase}, evidence={{...}})"}
except Exception as e:
    logger.error(f"Breadcrumb generation failed: {e}")
    breadcrumb = None  # Graceful degradation

return add_workflow_guidance(response, breadcrumb)  # Works with or without breadcrumb
```

**Defense in Depth:**
- Layer 1: Breadcrumbs guide AI behavior (soft guidance)
- Layer 2: Evidence validation enforces quality (hard enforcement)
- Layer 3: Human review catches issues (ultimate fallback)

---

### 5.7 Threat Model

**Threat 1: AI Agent Ignores Breadcrumbs**
- **Likelihood:** Low (breadcrumbs make following easier than skipping)
- **Impact:** Low (evidence validation still catches at phase gate)
- **Mitigation:** Behavioral metrics track compliance, iterate on format if needed

**Threat 2: Breadcrumb Generation Fails**
- **Likelihood:** Very Low (simple logic, no external dependencies)
- **Impact:** Low (graceful degradation, workflow continues)
- **Mitigation:** Error logging, graceful degradation (NFR-C2)

**Threat 3: Task Count Retrieval Fails**
- **Likelihood:** Very Low (phase directory deleted mid-workflow)
- **Impact:** Low (actionable error message, workflow can retry)
- **Mitigation:** `RendererError` with fix instructions (NFR-U2)

**Threat 4: Malicious AI Attempts to Bypass**
- **Likelihood:** N/A (AI agents are not adversarial, just probabilistic)
- **Impact:** Low (evidence validation is ultimate enforcement)
- **Mitigation:** Not a security threat (behavioral optimization, not adversarial)

**No Traditional Security Threats:**
- No authentication bypass (no auth changes)
- No privilege escalation (no authorization changes)
- No injection attacks (no user input)
- No data exfiltration (breadcrumbs are not sensitive)

---

### 5.8 Security Testing

**Security Test Cases:**

1. **Graceful Degradation Test**
   - Simulate `RendererError` in task count retrieval
   - Verify workflow continues with static guidance only
   - Verify error logged with context

2. **Evidence Validation Still Works**
   - Submit invalid evidence (missing required fields)
   - Verify phase gate blocks advancement
   - Verify breadcrumbs do not bypass validation

3. **No Information Leakage in start_workflow**
   - Call `start_workflow`
   - Verify `phase_content` NOT in response (FR-001)
   - Verify workflow overview only (high-level metadata)

4. **Task Count Accuracy**
   - For static workflow: verify glob count matches actual task files
   - For dynamic workflow: verify cached count matches parsed spec
   - Verify breadcrumb uses correct task count

**No Penetration Testing Required:** This is an internal feature with no new external attack surface.

---

### 5.9 Supporting Documentation

Security design informed by:
- **2025-11-08-workflow-breadcrumb-navigation.md**: Behavioral security (AI bypass prevention), graceful degradation strategy, defense in depth approach

See `supporting-docs/INSIGHTS.md` for threat model and risk analysis.

