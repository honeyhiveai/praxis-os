# Dynamic Workflow Architecture Design

**Date:** 2025-10-06  
**Purpose:** Extend workflow engine to support dynamically-generated phase/task content with template scaffolding  
**Status:** Design Proposal

---

## Problem Statement

Current workflow engine uses RAG to retrieve static workflow content from files. This works for fixed workflows (test_generation_v3, production_code_v2) but fails for dynamic workflows like spec_execution_v1 where:

- Phase count is unknown (depends on spec's tasks.md)
- Task content comes from external source (spec files)
- Templates provide structure/enforcement (command language)
- No physical phase/task files exist in workflow directory

**Current Failure Mode:**
1. Agent completes Phase 0
2. Engine calls `_get_phase_content_from_rag("spec_execution_v1", phase=1)`
3. RAG search finds spec's raw tasks.md (no command language)
4. Agent receives unstructured content → breaks out of workflow

---

## Architectural Approach

### Core Concept: Dynamic Content Registry

Add a **session-scoped dynamic content registry** that:
1. Detects workflows with `dynamic_phases: true` in metadata.json
2. Loads and caches templates on first use
3. Parses external source (e.g., spec's tasks.md) on-demand
4. Renders templates with source data in-memory
5. Serves rendered content via existing get_phase/get_task APIs
6. Cleans up when session completes

**No changes to MCP API surface** - transparent to AI agents

---

## Component Design

### 1. Workflow Metadata Extension

**File:** `workflows/{workflow_type}/metadata.json`

**New Fields:**

```json
{
  "workflow_type": "spec_execution_v1",
  "dynamic_phases": true,
  "dynamic_config": {
    "source_type": "spec_tasks_md",
    "source_path_key": "spec_path",
    "templates": {
      "phase": "phases/dynamic/phase-template.md",
      "task": "phases/dynamic/task-template.md"
    },
    "parser": "spec_tasks_parser"
  }
}
```

**Field Definitions:**

| Field | Type | Description |
|-------|------|-------------|
| `dynamic_phases` | bool | Enable dynamic content generation |
| `source_type` | string | Type of external source ("spec_tasks_md", "jira_api", etc.) |
| `source_path_key` | string | Key in workflow options to find source path |
| `templates.phase` | string | Relative path to phase template |
| `templates.task` | string | Relative path to task template |
| `parser` | string | Parser identifier for source format |

---

### 2. Dynamic Content Registry

**New Component:** `mcp_server/core/dynamic_registry.py`

```python
class DynamicContentRegistry:
    """
    Session-scoped registry for dynamically-generated workflow content.
    
    Manages lifecycle:
    - Parse source on first access
    - Cache rendered templates per session
    - Serve content via get_phase/get_task
    - Cleanup on session completion
    """
    
    def __init__(self):
        # session_id -> DynamicWorkflowContent
        self._sessions: Dict[str, DynamicWorkflowContent] = {}
        
        # Registered parsers
        self._parsers: Dict[str, Callable] = {
            "spec_tasks_parser": SpecTasksParser(),
        }
    
    def initialize_session(
        self, 
        session_id: str,
        workflow_type: str,
        dynamic_config: Dict[str, Any],
        options: Dict[str, Any],
        workflows_base_path: Path
    ) -> None:
        """
        Initialize dynamic content for a session.
        
        Steps:
        1. Load templates from workflow directory
        2. Get source path from options
        3. Parse source using configured parser
        4. Create DynamicWorkflowContent cache
        
        :param session_id: Workflow session ID
        :param workflow_type: Workflow type
        :param dynamic_config: Config from metadata.json
        :param options: Options passed to start_workflow
        :param workflows_base_path: Base path for workflows
        """
    
    def has_session(self, session_id: str) -> bool:
        """Check if session has dynamic content."""
        return session_id in self._sessions
    
    def get_phase_content(self, session_id: str, phase: int) -> str:
        """
        Get rendered phase content.
        
        Returns template-wrapped content with command language.
        Renders on-demand and caches result.
        """
    
    def get_task_content(
        self, 
        session_id: str, 
        phase: int, 
        task_number: int
    ) -> str:
        """
        Get rendered task content.
        
        Returns template-wrapped task with enforcement.
        Renders on-demand and caches result.
        """
    
    def get_phase_metadata(self, session_id: str, phase: int) -> Dict[str, Any]:
        """
        Get phase metadata (name, task count, etc.).
        
        Used by workflow engine to build responses.
        """
    
    def cleanup_session(self, session_id: str) -> None:
        """Remove session from registry (when workflow completes)."""
        if session_id in self._sessions:
            del self._sessions[session_id]
```

---

### 3. Dynamic Workflow Content (Cache Structure)

**Internal Data Structure:**

```python
@dataclass
class DynamicWorkflowContent:
    """Parsed and cached dynamic workflow content for a session."""
    
    session_id: str
    workflow_type: str
    source_path: Path
    
    # Templates (loaded once)
    phase_template: str
    task_template: str
    
    # Parsed structure from source
    phases: List[DynamicPhase]
    
    # Rendered content cache (lazy)
    _rendered_phases: Dict[int, str] = field(default_factory=dict)
    _rendered_tasks: Dict[Tuple[int, int], str] = field(default_factory=dict)
    
    def render_phase(self, phase: int) -> str:
        """Render phase template with phase data."""
        if phase not in self._rendered_phases:
            phase_data = self.phases[phase]
            self._rendered_phases[phase] = self._render_template(
                self.phase_template, phase_data
            )
        return self._rendered_phases[phase]
    
    def render_task(self, phase: int, task_number: int) -> str:
        """Render task template with task data."""
        cache_key = (phase, task_number)
        if cache_key not in self._rendered_tasks:
            task_data = self.phases[phase].tasks[task_number - 1]
            self._rendered_tasks[cache_key] = self._render_template(
                self.task_template, task_data
            )
        return self._rendered_tasks[cache_key]

@dataclass
class DynamicPhase:
    """Phase structure parsed from source."""
    phase_number: int
    phase_name: str
    description: str
    estimated_duration: str
    tasks: List[DynamicTask]
    validation_gate: List[str]

@dataclass
class DynamicTask:
    """Task structure parsed from source."""
    task_id: str  # e.g., "1.1"
    task_name: str
    description: str
    estimated_time: str
    dependencies: List[str]
    acceptance_criteria: List[str]
```

---

### 4. Source Parser Interface

**New Component:** `mcp_server/core/parsers.py`

```python
class SourceParser(ABC):
    """Abstract parser for dynamic workflow sources."""
    
    @abstractmethod
    def parse(self, source_path: Path) -> List[DynamicPhase]:
        """
        Parse source into structured phase/task data.
        
        :param source_path: Path to source file/directory
        :return: List of DynamicPhase objects
        :raises ParseError: If source is invalid
        """
        pass

class SpecTasksParser(SourceParser):
    """
    Parser for prAxIs OS spec tasks.md files.
    
    Extracts:
    - Phase headers (### Phase N: Name)
    - Task lists with acceptance criteria
    - Validation gates
    - Dependencies
    """
    
    def parse(self, source_path: Path) -> List[DynamicPhase]:
        """
        Parse spec's tasks.md file.
        
        Expected structure:
        ```markdown
        ### Phase 1: Phase Name
        **Goal:** Description
        **Tasks:**
        - [ ] **Task 1.1**: Name
          - **Estimated Time**: 4 hours
          - **Dependencies**: None
          - **Acceptance Criteria**:
            - [ ] Criterion 1
        
        **Validation Gate:**
        - [ ] Gate criterion 1
        ```
        """
        # Implementation parses markdown structure
        # Returns List[DynamicPhase]
```

---

### 5. Workflow Engine Integration

**Changes to `WorkflowEngine` class:**

```python
class WorkflowEngine:
    def __init__(
        self,
        state_manager: StateManager,
        rag_engine: RAGEngine,
        checkpoint_loader: Optional[CheckpointLoader] = None,
        workflows_base_path: Optional[Path] = None,
    ):
        # ... existing init ...
        
        # NEW: Dynamic content registry
        self.dynamic_registry = DynamicContentRegistry()
    
    def start_workflow(
        self, 
        workflow_type: str, 
        target_file: str, 
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Start workflow with dynamic content support."""
        
        # Load metadata
        workflow_metadata = self.load_workflow_metadata(workflow_type)
        
        # Check for dynamic phases
        if workflow_metadata.dynamic_phases:
            # Initialize dynamic content for this session
            session_id = state.session_id  # from state_manager
            self.dynamic_registry.initialize_session(
                session_id=session_id,
                workflow_type=workflow_type,
                dynamic_config=workflow_metadata.dynamic_config,
                options=metadata or {},
                workflows_base_path=self.workflows_base_path
            )
        
        # ... rest of existing code ...
    
    def _get_phase_content_from_rag(
        self, 
        workflow_type: str, 
        phase: int
    ) -> Dict[str, Any]:
        """
        Get phase content - static or dynamic.
        
        DECISION POINT: Use dynamic registry or RAG?
        """
        
        # Check if current session uses dynamic content
        session_id = self._get_current_session_id()  # from context
        
        if self.dynamic_registry.has_session(session_id):
            # DYNAMIC PATH: Render from templates
            return self._get_dynamic_phase_content(session_id, phase)
        else:
            # STATIC PATH: Use RAG (existing behavior)
            return self._get_static_phase_content(workflow_type, phase)
    
    def _get_dynamic_phase_content(
        self, 
        session_id: str, 
        phase: int
    ) -> Dict[str, Any]:
        """
        Get dynamically-rendered phase content.
        
        Returns template-wrapped content with command language.
        """
        # Get rendered phase content from registry
        phase_content = self.dynamic_registry.get_phase_content(session_id, phase)
        
        # Get phase metadata for response structure
        phase_meta = self.dynamic_registry.get_phase_metadata(session_id, phase)
        
        return {
            "phase_overview": phase_content,  # Full template-wrapped content
            "tasks": phase_meta["tasks"],      # Task metadata list
            "phase_name": phase_meta["name"],
            "task_count": len(phase_meta["tasks"]),
        }
    
    def _get_static_phase_content(
        self, 
        workflow_type: str, 
        phase: int
    ) -> Dict[str, Any]:
        """Existing RAG-based content retrieval (unchanged)."""
        # ... existing implementation ...
    
    def get_task(
        self, 
        session_id: str, 
        phase: int, 
        task_number: int
    ) -> Dict[str, Any]:
        """
        Get task content - static or dynamic.
        
        DECISION POINT: Use dynamic registry or RAG?
        """
        
        if self.dynamic_registry.has_session(session_id):
            # DYNAMIC PATH: Render from task template
            task_content = self.dynamic_registry.get_task_content(
                session_id, phase, task_number
            )
            
            return {
                "session_id": session_id,
                "phase": phase,
                "task_number": task_number,
                "task_content": task_content,  # Template-wrapped
                "source": "dynamic"
            }
        else:
            # STATIC PATH: Use RAG (existing behavior)
            # ... existing implementation ...
    
    def complete_phase(
        self, 
        session_id: str, 
        phase: int, 
        evidence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Complete phase with cleanup on workflow end."""
        
        # ... existing validation and advancement ...
        
        # Check if workflow complete
        if state.is_complete():
            # Cleanup dynamic content
            self.dynamic_registry.cleanup_session(session_id)
        
        return response
```

---

## Data Flow

### Initialization (start_workflow)

```
1. User calls: start_workflow("spec_execution_v1", spec_path)
                     ↓
2. WorkflowEngine.start_workflow()
                     ↓
3. Load metadata.json → detect dynamic_phases: true
                     ↓
4. Create session_id via state_manager
                     ↓
5. DynamicRegistry.initialize_session()
   - Load phase-template.md
   - Load task-template.md
   - Find spec's tasks.md (from options)
   - Parse tasks.md → List[DynamicPhase]
   - Cache in registry[session_id]
                     ↓
6. Return Phase 0 content (static file)
```

### Phase Transition (complete_phase → get_current_phase)

```
1. Agent calls: complete_phase(session_id, phase=0, evidence={...})
                     ↓
2. Validation passes → advance to Phase 1
                     ↓
3. WorkflowEngine._get_phase_content_from_rag("spec_execution_v1", 1)
                     ↓
4. Check: dynamic_registry.has_session(session_id)? → YES
                     ↓
5. DynamicRegistry.get_phase_content(session_id, phase=1)
   - Check cache → miss
   - Get DynamicPhase[1] data
   - Render phase-template.md with data
   - Cache result
   - Return rendered content WITH COMMAND LANGUAGE
                     ↓
6. Return to agent with enforcement
```

### Task Retrieval (get_task)

```
1. Agent calls: get_task(session_id, phase=1, task_number=1)
                     ↓
2. WorkflowEngine.get_task()
                     ↓
3. Check: dynamic_registry.has_session(session_id)? → YES
                     ↓
4. DynamicRegistry.get_task_content(session_id, 1, 1)
   - Check cache → miss
   - Get DynamicTask data
   - Render task-template.md with data
   - Cache result
   - Return rendered content WITH COMMAND LANGUAGE
                     ↓
5. Return to agent with enforcement
```

### Cleanup (workflow completion)

```
1. Agent completes final phase
                     ↓
2. WorkflowEngine.complete_phase() → state.is_complete() == True
                     ↓
3. DynamicRegistry.cleanup_session(session_id)
   - Delete cached templates
   - Delete cached renders
   - Remove session from registry
```

---

## Template Rendering

### Phase Template Variables

Template placeholders populated from `DynamicPhase`:

| Placeholder | Source |
|------------|--------|
| `[PHASE_NUMBER]` | phase_number |
| `[PHASE_NAME]` | phase_name |
| `[PHASE_DESCRIPTION]` | description |
| `[ESTIMATED_DURATION]` | estimated_duration |
| `[TASK_COUNT]` | len(tasks) |
| `[VALIDATION_GATE]` | validation_gate (formatted list) |
| `[NEXT_PHASE_NUMBER]` | phase_number + 1 |

### Task Template Variables

Template placeholders populated from `DynamicTask`:

| Placeholder | Source |
|------------|--------|
| `[TASK_ID]` | task_id (e.g., "1.1") |
| `[TASK_NAME]` | task_name |
| `[PHASE_NUMBER]` | Parent phase number |
| `[PHASE_NAME]` | Parent phase name |
| `[TASK_DESCRIPTION]` | description |
| `[ESTIMATED_TIME]` | estimated_time |
| `[DEPENDENCIES]` | dependencies (formatted) |
| `[ACCEPTANCE_CRITERIA]` | acceptance_criteria (formatted list) |
| `[NEXT_TASK_NUMBER]` | task_number + 1 |

---

## Backward Compatibility

**No Breaking Changes:**
- Existing workflows (test_generation_v3, production_code_v2) work unchanged
- Static workflows use RAG path (existing behavior)
- Only workflows with `dynamic_phases: true` use registry
- MCP API surface unchanged

---

## Performance Considerations

### Memory Usage
- **One cache per active session** (typical: 1-3 sessions)
- **Template size:** ~5-10 KB per template
- **Rendered content:** ~20-50 KB per phase/task
- **Total per session:** ~500 KB - 2 MB (acceptable)

### Rendering Performance
- **First access:** Parse + render (~50-100ms)
- **Cached access:** Dictionary lookup (~1ms)
- **Lazy rendering:** Only render accessed phases/tasks

### Cleanup
- **On workflow completion:** Automatic cleanup
- **On server restart:** In-memory cache cleared (sessions persist in state_manager)

---

## Error Handling

### Source Parse Failures

```python
try:
    phases = parser.parse(source_path)
except ParseError as e:
    return {
        "error": "source_parse_failed",
        "message": f"Could not parse {source_path}: {e}",
        "hint": "Verify tasks.md follows spec format"
    }
```

### Missing Templates

```python
if not template_path.exists():
    return {
        "error": "template_not_found",
        "message": f"Template {template_path} not found",
        "hint": "Check metadata.json template paths"
    }
```

### Invalid Phase/Task Access

```python
if phase >= len(self.phases):
    return {
        "error": "phase_out_of_range",
        "message": f"Phase {phase} not found (spec has {len(self.phases)} phases)"
    }
```

---

## Testing Strategy

### Unit Tests

1. **DynamicContentRegistry**
   - Initialize session with valid source
   - Parse spec tasks.md correctly
   - Render phase templates with placeholders
   - Render task templates with placeholders
   - Cache rendered content
   - Cleanup sessions

2. **SpecTasksParser**
   - Parse valid tasks.md
   - Extract phases correctly
   - Extract tasks correctly
   - Handle malformed input gracefully

### Integration Tests

1. **End-to-End Dynamic Workflow**
   - Start spec_execution_v1 workflow
   - Complete Phase 0
   - Verify Phase 1 has command language
   - Call get_task() → verify enforcement
   - Complete all phases
   - Verify cleanup

2. **Backward Compatibility**
   - Start test_generation_v3 → verify RAG path
   - Start production_code_v2 → verify RAG path
   - Both should work unchanged

---

## Implementation Plan

### Phase 1: Core Infrastructure (4-6 hours)
- [ ] Create `core/dynamic_registry.py` with DynamicContentRegistry
- [ ] Create `core/parsers.py` with SpecTasksParser
- [ ] Add models for DynamicPhase, DynamicTask
- [ ] Unit tests for registry and parser

### Phase 2: Workflow Engine Integration (3-4 hours)
- [ ] Add dynamic_registry to WorkflowEngine.__init__
- [ ] Modify start_workflow to initialize dynamic sessions
- [ ] Modify _get_phase_content_from_rag to check registry
- [ ] Modify get_task to check registry
- [ ] Add cleanup to complete_phase

### Phase 3: Testing & Validation (2-3 hours)
- [ ] Integration test for spec_execution_v1
- [ ] Verify command language enforcement
- [ ] Test backward compatibility
- [ ] Performance profiling

### Phase 4: Documentation (1-2 hours)
- [ ] Update workflow engine docs
- [ ] Document dynamic workflow creation
- [ ] Add examples

**Total Estimated Effort:** 10-15 hours

---

## Open Questions

1. **Session Context:** How does `_get_phase_content_from_rag` know the session_id?
   - Option A: Add session_id parameter to method signature
   - Option B: Store session_id in thread-local context
   - **Recommendation:** Add parameter (explicit is better)

2. **Template Syntax:** Use simple string replacement or templating engine?
   - Option A: `str.replace("[PLACEHOLDER]", value)`
   - Option B: Jinja2 templates
   - **Recommendation:** Start with simple replacement, migrate if complex

3. **Multiple Sessions:** Can same workflow_type have multiple sessions?
   - Answer: Yes (different specs), registry must be session-scoped ✅

4. **Source Changes:** What if spec's tasks.md changes during workflow?
   - Answer: Parsed once on initialization, changes ignored (session snapshot)

---

## Success Criteria

- [ ] Phase 0 → Phase 1 transition includes command language
- [ ] Agent CANNOT break out of workflow after Phase 0
- [ ] get_task() returns template-wrapped content with enforcement
- [ ] All checkpoints enforced through phase completion
- [ ] Backward compatibility maintained (existing workflows work)
- [ ] Memory usage < 5 MB per session
- [ ] Rendering latency < 100ms first access, < 5ms cached

---

**This design enables dynamic workflows while maintaining clean architecture and backward compatibility.**
