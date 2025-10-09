# Technical Specifications
## Dynamic Workflow Engine & Session-Scoped Refactor

**Date:** 2025-10-06  
**Version:** 1.0

---

## 1. Architecture Overview

### 1.1 System Context

```
┌─────────────────────────────────────────────────────────────┐
│                        MCP Server                            │
│                                                               │
│  ┌──────────────┐                                            │
│  │ Workflow     │                                            │
│  │ Tools        │ ─────► WorkflowEngine (Session Factory)   │
│  └──────────────┘            │                               │
│                               ▼                               │
│                        WorkflowSession                        │
│                     ┌──────┴───────┐                         │
│                     ▼              ▼                          │
│              DynamicRegistry   RAGEngine                      │
│                     │              │                          │
│              ┌──────┴──────┐       │                          │
│              ▼             ▼       │                          │
│         SourceParser  Templates    │                          │
│              │                     │                          │
│              ▼                     ▼                          │
│          tasks.md         Workflow Content                    │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Key Design Principles

1. **Session-Scoped Ownership:** Each workflow session is an object with lifecycle management
2. **Lazy Rendering:** Templates rendered on-demand, cached for performance
3. **Backward Compatibility:** Static workflows use RAG, dynamic workflows use registry
4. **Clean Separation:** Registry, parsers, and session logic are separate concerns
5. **Extensibility:** Parser registry allows new source types

---

## 2. Component Architecture

### 2.1 Component Overview

| Component | Responsibility | Location |
|-----------|---------------|----------|
| `WorkflowEngine` | Session factory, coordination | `mcp_server/workflow_engine.py` |
| `WorkflowSession` | Session-scoped workflow logic | `mcp_server/core/session.py` |
| `DynamicContentRegistry` | Template rendering & caching | `mcp_server/core/dynamic_registry.py` |
| `SourceParser` | Parse external sources | `mcp_server/core/parsers.py` |
| `DynamicWorkflowContent` | Parsed/cached content | `mcp_server/core/dynamic_registry.py` |
| `WorkflowMetadata` | Workflow configuration | `mcp_server/models/workflow.py` |

### 2.2 Decision Flow

```
MCP Tool Call: get_current_phase(session_id)
         │
         ▼
  WorkflowEngine.get_session(session_id)
         │
         ▼
  WorkflowSession.get_current_phase()
         │
         ▼
   Is dynamic workflow?
    /            \
  YES             NO
   │               │
   ▼               ▼
Registry      RAGEngine
.render()     .search()
   │               │
   └───────┬───────┘
           ▼
   Return content (with or without template)
```

---

## 3. Data Models

### 3.1 WorkflowSession

```python
class WorkflowSession:
    """
    Session-scoped workflow with lifecycle management.
    
    Encapsulates all session-specific logic and state.
    """
    
    # Core attributes
    session_id: str
    workflow_type: str
    target_file: str
    state: WorkflowState
    
    # Dependencies
    rag_engine: RAGEngine
    state_manager: StateManager
    workflows_base_path: Path
    
    # Dynamic content (optional)
    dynamic_registry: Optional[DynamicContentRegistry]
    metadata: WorkflowMetadata
    
    def __init__(
        self,
        session_id: str,
        workflow_type: str,
        target_file: str,
        state: WorkflowState,
        rag_engine: RAGEngine,
        state_manager: StateManager,
        workflows_base_path: Path,
        metadata: WorkflowMetadata,
        options: Optional[Dict[str, Any]] = None
    ):
        """Initialize session with optional dynamic content."""
        
    def get_current_phase(self) -> Dict[str, Any]:
        """Get current phase content (no session_id param!)."""
        
    def get_task(self, phase: int, task_number: int) -> Dict[str, Any]:
        """Get task content (clean parameters)."""
        
    def complete_phase(self, phase: int, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Complete phase with validation."""
        
    def _is_dynamic(self) -> bool:
        """Check if this is a dynamic workflow."""
        
    def cleanup(self) -> None:
        """Clean up resources on completion."""
```

### 3.2 DynamicContentRegistry

```python
class DynamicContentRegistry:
    """
    Manages template rendering and caching for dynamic workflows.
    
    Lifecycle:
    1. Initialize with templates and source
    2. Render on-demand
    3. Cache results
    4. Return cached content on subsequent requests
    """
    
    def __init__(
        self,
        workflow_type: str,
        templates: Dict[str, Path],  # {'phase': path, 'task': path}
        source_path: Path,
        parser: SourceParser
    ):
        """Initialize registry with templates and source."""
        
    def get_phase_content(self, phase: int) -> str:
        """Get rendered phase content (cached)."""
        
    def get_task_content(self, phase: int, task_number: int) -> str:
        """Get rendered task content (cached)."""
        
    def get_phase_metadata(self, phase: int) -> Dict[str, Any]:
        """Get phase metadata for engine responses."""
```

### 3.3 DynamicWorkflowContent

```python
@dataclass
class DynamicWorkflowContent:
    """Parsed and cached content for a session."""
    
    # Source info
    source_path: Path
    workflow_type: str
    
    # Templates (loaded once)
    phase_template: str
    task_template: str
    
    # Parsed structure
    phases: List[DynamicPhase]
    
    # Render cache (lazy)
    _rendered_phases: Dict[int, str] = field(default_factory=dict)
    _rendered_tasks: Dict[Tuple[int, int], str] = field(default_factory=dict)
    
    def render_phase(self, phase: int) -> str:
        """Render phase template with data."""
        
    def render_task(self, phase: int, task_number: int) -> str:
        """Render task template with data."""

@dataclass
class DynamicPhase:
    """Phase structure from source."""
    phase_number: int
    phase_name: str
    description: str
    estimated_duration: str
    tasks: List[DynamicTask]
    validation_gate: List[str]

@dataclass
class DynamicTask:
    """Task structure from source."""
    task_id: str  # "1.1"
    task_name: str
    description: str
    estimated_time: str
    dependencies: List[str]
    acceptance_criteria: List[str]
```

### 3.4 WorkflowMetadata Extension

```python
@dataclass
class WorkflowMetadata:
    """Extended to support dynamic workflows."""
    
    # Existing fields...
    workflow_type: str
    version: str
    total_phases: Union[int, str]  # Can be "dynamic"
    phases: List[PhaseMetadata]
    
    # NEW: Dynamic workflow support
    dynamic_phases: bool = False
    dynamic_config: Optional[Dict[str, Any]] = None
    # dynamic_config structure:
    # {
    #     "source_type": "spec_tasks_md",
    #     "source_path_key": "spec_path",
    #     "templates": {
    #         "phase": "phases/dynamic/phase-template.md",
    #         "task": "phases/dynamic/task-template.md"
    #     },
    #     "parser": "spec_tasks_parser"
    # }
```

---

## 4. Component Specifications

### 4.1 WorkflowEngine (Refactored)

**Purpose:** Session factory and coordinator

**Changes:**
- Add session cache (session_id → WorkflowSession)
- Add `get_session()` method
- Refactor tool methods to use sessions

```python
class WorkflowEngine:
    def __init__(
        self,
        state_manager: StateManager,
        rag_engine: RAGEngine,
        checkpoint_loader: Optional[CheckpointLoader] = None,
        workflows_base_path: Optional[Path] = None,
    ):
        self.state_manager = state_manager
        self.rag_engine = rag_engine
        self.checkpoint_loader = checkpoint_loader
        self.workflows_base_path = workflows_base_path
        
        # Session cache
        self._sessions: Dict[str, WorkflowSession] = {}
        self._metadata_cache: Dict[str, WorkflowMetadata] = {}
    
    def get_session(self, session_id: str) -> WorkflowSession:
        """
        Get or create WorkflowSession instance.
        
        Caches sessions for performance.
        Initializes dynamic content if applicable.
        """
        if session_id in self._sessions:
            return self._sessions[session_id]
        
        # Load state
        state = self.state_manager.load_state(session_id)
        if not state:
            raise ValueError(f"Session {session_id} not found")
        
        # Load metadata
        metadata = self.load_workflow_metadata(state.workflow_type)
        
        # Create session
        session = WorkflowSession(
            session_id=session_id,
            workflow_type=state.workflow_type,
            target_file=state.target_file,
            state=state,
            rag_engine=self.rag_engine,
            state_manager=self.state_manager,
            workflows_base_path=self.workflows_base_path,
            metadata=metadata,
            options=state.metadata
        )
        
        # Cache
        self._sessions[session_id] = session
        
        return session
    
    def start_workflow(
        self, 
        workflow_type: str, 
        target_file: str, 
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Start workflow - creates session immediately.
        """
        # ... existing session creation ...
        
        # Get session (initializes dynamic content)
        session = self.get_session(state.session_id)
        
        # Return initial content
        return session.get_current_phase()
    
    # Tool methods delegate to sessions
    def get_current_phase(self, session_id: str) -> Dict[str, Any]:
        session = self.get_session(session_id)
        return session.get_current_phase()
    
    def get_task(self, session_id: str, phase: int, task_number: int) -> Dict[str, Any]:
        session = self.get_session(session_id)
        return session.get_task(phase, task_number)
    
    def complete_phase(self, session_id: str, phase: int, evidence: Dict[str, Any]) -> Dict[str, Any]:
        session = self.get_session(session_id)
        result = session.complete_phase(phase, evidence)
        
        # Cleanup if complete
        if result.get("workflow_complete"):
            session.cleanup()
            del self._sessions[session_id]
        
        return result
```

### 4.2 SourceParser

**Purpose:** Parse external sources into structured data

```python
class SourceParser(ABC):
    """Abstract parser for dynamic workflow sources."""
    
    @abstractmethod
    def parse(self, source_path: Path) -> List[DynamicPhase]:
        """Parse source into phases."""
        pass

class SpecTasksParser(SourceParser):
    """
    Parser for Agent OS spec tasks.md files.
    
    Expected Format:
    ### Phase N: Name
    **Goal:** Description
    **Tasks:**
    - [ ] **Task N.M**: Name
      - **Estimated Time**: X hours
      - **Dependencies**: Task N.K
      - **Acceptance Criteria**:
        - [ ] Criterion
    **Validation Gate:**
    - [ ] Gate criterion
    """
    
    def parse(self, source_path: Path) -> List[DynamicPhase]:
        """
        Parse tasks.md into structured phases.
        
        Returns:
            List of DynamicPhase objects
        
        Raises:
            ParseError: If format is invalid
        """
        content = source_path.read_text()
        phases = []
        
        # Split into phase sections
        phase_sections = self._split_phases(content)
        
        for section in phase_sections:
            phase = self._parse_phase_section(section)
            phases.append(phase)
        
        return phases
    
    def _split_phases(self, content: str) -> List[str]:
        """Split content by ### Phase headers."""
        
    def _parse_phase_section(self, section: str) -> DynamicPhase:
        """Parse single phase section."""
        
    def _extract_tasks(self, section: str) -> List[DynamicTask]:
        """Extract task list from phase section."""
        
    def _extract_validation_gate(self, section: str) -> List[str]:
        """Extract validation criteria."""
```

---

## 5. Integration Points

### 5.1 MCP Tools (No Changes)

MCP tool signatures remain identical:

```python
@mcp.tool()
async def start_workflow(
    workflow_type: str,
    target_file: str,
    options: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return workflow_engine.start_workflow(workflow_type, target_file, options)

@mcp.tool()
async def get_current_phase(session_id: str) -> Dict[str, Any]:
    return workflow_engine.get_current_phase(session_id)

@mcp.tool()
async def get_task(session_id: str, phase: int, task_number: int) -> Dict[str, Any]:
    return workflow_engine.get_task(session_id, phase, task_number)
```

### 5.2 StateManager (No Changes)

StateManager interface remains unchanged. Sessions use it for persistence.

### 5.3 RAGEngine (No Changes)

RAGEngine used for static workflow content (existing behavior).

---

## 6. Data Flow

### 6.1 Dynamic Workflow Initialization

```
1. start_workflow("spec_execution_v1", "path/to/spec")
   │
   ├─► WorkflowEngine.start_workflow()
   │   ├─► Load metadata.json
   │   │   └─► Detect dynamic_phases: true
   │   ├─► Create WorkflowState via StateManager
   │   └─► Get session_id
   │
   ├─► WorkflowEngine.get_session(session_id)
   │   ├─► Create WorkflowSession
   │   │   ├─► Check metadata.dynamic_phases
   │   │   └─► Initialize DynamicContentRegistry
   │   │       ├─► Load phase-template.md
   │   │       ├─► Load task-template.md
   │   │       ├─► Find spec's tasks.md (from options)
   │   │       ├─► SpecTasksParser.parse(tasks.md)
   │   │       └─► Cache parsed phases
   │   └─► Cache session
   │
   └─► WorkflowSession.get_current_phase()
       └─► Return Phase 0 content (static file)
```

### 6.2 Phase Transition (Enforcement Point)

```
1. complete_phase(session_id, phase=0, evidence={...})
   │
   ├─► WorkflowEngine.complete_phase(session_id, 0, evidence)
   │   └─► WorkflowSession.complete_phase(0, evidence)
   │       ├─► Validate evidence
   │       ├─► Advance state to Phase 1
   │       └─► Return next phase content
   │
   └─► WorkflowSession.get_current_phase()
       ├─► Check: self._is_dynamic() → YES
       │
       ├─► DynamicRegistry.get_phase_content(phase=1)
       │   ├─► Check cache → MISS
       │   ├─► Get DynamicPhase[1] data
       │   ├─► Render phase-template.md with data
       │   │   └─► Replace [PHASE_NUMBER], [PHASE_NAME], etc.
       │   ├─► Cache rendered content
       │   └─► Return content WITH COMMAND LANGUAGE
       │
       └─► Return to agent
           └─► Agent sees: "🛑 EXECUTE-NOW: Use get_task()..."
```

### 6.3 Task Retrieval

```
1. get_task(session_id, phase=1, task_number=1)
   │
   ├─► WorkflowEngine.get_task(session_id, 1, 1)
   │   └─► WorkflowSession.get_task(1, 1)
   │       ├─► Check: self._is_dynamic() → YES
   │       │
   │       └─► DynamicRegistry.get_task_content(1, 1)
   │           ├─► Check cache → MISS
   │           ├─► Get DynamicTask data
   │           ├─► Render task-template.md with data
   │           │   └─► Replace [TASK_ID], [TASK_NAME], etc.
   │           ├─► Cache rendered content
   │           └─► Return content WITH ENFORCEMENT
   │
   └─► Return to agent
       └─► Agent sees: "🛑 EXECUTE-NOW: Query production code checklist"
```

---

## 7. Template System

### 7.1 Template Placeholders

**Phase Template:**
- `[PHASE_NUMBER]` → phase_number
- `[PHASE_NAME]` → phase_name
- `[PHASE_DESCRIPTION]` → description
- `[ESTIMATED_DURATION]` → estimated_duration
- `[TASK_COUNT]` → len(tasks)
- `[VALIDATION_GATE]` → formatted validation criteria
- `[NEXT_PHASE_NUMBER]` → phase_number + 1

**Task Template:**
- `[TASK_ID]` → task_id ("1.1")
- `[TASK_NAME]` → task_name
- `[PHASE_NUMBER]` → parent phase number
- `[PHASE_NAME]` → parent phase name
- `[TASK_DESCRIPTION]` → description
- `[ESTIMATED_TIME]` → estimated_time
- `[DEPENDENCIES]` → formatted dependencies
- `[ACCEPTANCE_CRITERIA]` → formatted criteria list
- `[NEXT_TASK_NUMBER]` → task_number + 1

### 7.2 Rendering Algorithm

```python
def _render_template(template: str, data: Dict[str, Any]) -> str:
    """Simple placeholder replacement."""
    result = template
    
    for placeholder, value in data.items():
        # Format lists/complex values
        if isinstance(value, list):
            value = _format_list(value)
        
        # Replace [PLACEHOLDER] with value
        result = result.replace(f"[{placeholder}]", str(value))
    
    return result
```

---

## 8. Performance Considerations

### 8.1 Caching Strategy

| Level | Cache Location | Lifetime | Invalidation |
|-------|---------------|----------|--------------|
| Workflow Metadata | WorkflowEngine._metadata_cache | Server lifetime | Never (restart) |
| Session | WorkflowEngine._sessions | Until workflow complete | On completion |
| Parsed Source | DynamicWorkflowContent.phases | Session lifetime | On session cleanup |
| Rendered Phase | DynamicWorkflowContent._rendered_phases | Session lifetime | On session cleanup |
| Rendered Task | DynamicWorkflowContent._rendered_tasks | Session lifetime | On session cleanup |

### 8.2 Memory Profile

**Per Active Session:**
- WorkflowSession object: ~1 KB
- DynamicWorkflowContent: ~500 KB - 2 MB (depends on spec size)
  - Templates: ~20 KB
  - Parsed phases: ~100-500 KB
  - Rendered cache: ~500 KB - 1 MB
- Total: **< 5 MB per session**

**System-Wide:**
- Metadata cache: ~100 KB
- Session cache (10 sessions): ~50 MB
- Total overhead: **< 100 MB**

---

## 9. Error Handling

### 9.1 Error Types

```python
class DynamicWorkflowError(Exception):
    """Base exception for dynamic workflow errors."""

class ParseError(DynamicWorkflowError):
    """Source parsing failed."""

class TemplateError(DynamicWorkflowError):
    """Template loading or rendering failed."""

class SessionNotFoundError(DynamicWorkflowError):
    """Session ID not found."""

class PhaseOutOfRangeError(DynamicWorkflowError):
    """Phase number invalid."""
```

### 9.2 Error Responses

All errors return structured JSON:

```python
{
    "error": "parse_error",
    "message": "Could not parse tasks.md: Missing Phase 1 header",
    "hint": "Ensure tasks.md has ### Phase N: Name headers",
    "source_path": "/path/to/tasks.md",
    "line_number": 45  # if applicable
}
```

---

## 10. Testing Strategy

### 10.1 Unit Tests

- `test_dynamic_registry.py` - Template loading, rendering, caching
- `test_parsers.py` - tasks.md parsing, error handling
- `test_session.py` - WorkflowSession lifecycle, methods
- `test_workflow_engine.py` - Session factory, integration

### 10.2 Integration Tests

- `test_dynamic_workflow_e2e.py` - Full spec_execution_v1 flow
- `test_backward_compat.py` - Existing workflows unchanged
- `test_performance.py` - Rendering latency, memory usage

### 10.3 Test Coverage Target

- Overall: ≥ 80%
- Core components: ≥ 90%
  - DynamicContentRegistry
  - SourceParser
  - WorkflowSession

---

## 11. Deployment

### 11.1 Rollout Plan

1. **Phase 1:** Implement core components (no integration)
2. **Phase 2:** Integrate with WorkflowEngine (feature flag)
3. **Phase 3:** Enable for spec_execution_v1 only
4. **Phase 4:** Full rollout after validation

### 11.2 Rollback Plan

If issues arise:
- Feature flag disables dynamic workflows
- All sessions fall back to RAG path
- Zero impact on static workflows

---

**For detailed architecture, see:** `DYNAMIC_WORKFLOW_ARCHITECTURE.md`  
**For implementation guidance, see:** `implementation.md`
