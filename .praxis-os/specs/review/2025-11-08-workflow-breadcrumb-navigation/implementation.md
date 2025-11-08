# Implementation Approach

**Project:** Workflow Breadcrumb Navigation System  
**Date:** 2025-11-08

---

## 1. Implementation Philosophy

**Core Principles:**
1. **Simplicity Over Abstraction**: Inline logic over strategy patterns - this is string formatting, not complex architecture
2. **Backward Compatibility**: Optional parameters, preserve existing behavior
3. **Behavioral Probability Engineering**: Make correct path easiest path through response structure
4. **Graceful Degradation**: Breadcrumb failures never block workflow execution
5. **Test-Driven Validation**: Unit tests verify breadcrumb generation for all scenarios

**Design Philosophy from specs.md Section 1.2:**
- Just-in-time information disclosure (prevent information leakage)
- Recency bias positioning (breadcrumbs at end of response)
- Action-specific guidance (not generic warnings)
- Literal call syntax (copy-paste executable)

---

## 2. Implementation Order

**Follow phased approach from tasks.md:**

1. **Phase 1: Foundation Changes** (1-2 hours)
   - Modify `guidance.py` to accept optional breadcrumb parameter
   - Enables all subsequent breadcrumb injection

2. **Phase 2: Task Count Infrastructure** (2-3 hours)
   - Add `WorkflowRenderer.get_task_count()` for static workflows
   - Add `WorkflowEngine._get_task_count_for_phase()` helper
   - Enables position-aware breadcrumb generation

3. **Phase 3: Breadcrumb Generation** (3-4 hours)
   - Modify 4 action handlers: `start_workflow`, `get_phase`, `get_task`, `complete_phase`
   - Each generates action-specific breadcrumb
   - **Critical path** - modify sequentially

4. **Phase 4: Testing & Validation** (3-4 hours)
   - Unit tests for all breadcrumb scenarios
   - Integration tests for full workflow execution
   - Behavioral validation (manual)

**Dependencies:** Must complete in order - each phase builds on previous.

---

## 3. Code Patterns

### Pattern 1: Optional Parameter for Backward Compatibility

**File:** `.praxis-os/ouroboros/subsystems/workflow/guidance.py`

**✅ CORRECT - Optional breadcrumb parameter:**

```python
def add_workflow_guidance(
    response: Dict[str, Any],
    breadcrumb: Optional[Dict[str, str]] = None  # ← Optional, default None
) -> Dict[str, Any]:
    """
    Decorate workflow response with static guidance and optional breadcrumb.
    
    Merging order (Python 3.7+ dict ordering):
        1. Static guidance fields (WORKFLOW_GUIDANCE_FIELDS) - prepended
        2. Response content - middle
        3. Breadcrumb fields (if provided) - appended (recency bias)
    
    Args:
        response: Base response from workflow engine
        breadcrumb: Optional action-specific navigation
    
    Returns:
        Decorated response with guidance + breadcrumb fields
    """
    # Start with static guidance
    guided = {**WORKFLOW_GUIDANCE_FIELDS, **response}
    
    # Add breadcrumb if provided (positioned last for recency bias)
    if breadcrumb:
        guided.update(breadcrumb)
    
    return guided
```

**Why this works:**
- `breadcrumb=None` default preserves existing behavior (no breaking change)
- Dict merging order ensures breadcrumb positioned last (recency bias)
- Simple conditional - no complex logic needed

**❌ ANTI-PATTERN - Required parameter:**

```python
def add_workflow_guidance(
    response: Dict[str, Any],
    breadcrumb: Dict[str, str]  # ← Required, breaks existing calls!
) -> Dict[str, Any]:
    # This breaks backward compatibility
```

---

### Pattern 2: Graceful Error Handling with Actionable Messages

**File:** `.praxis-os/ouroboros/subsystems/workflow/workflow_renderer.py`

**✅ CORRECT - Raise with actionable fix:**

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
    
    # Count task-*.md files
    task_files = list(phase_dir.glob("task-*-*.md"))
    return len(task_files)
```

**Why this works:**
- Specific error message with path
- Actionable fix (exact mkdir command)
- Uses project's RendererError pattern (what/why/how)

**❌ ANTI-PATTERN - Generic error:**

```python
if not phase_dir.exists():
    raise ValueError("Directory not found")  # ← Unhelpful!
```

---

### Pattern 3: Dynamic Routing Based on State

**File:** `.praxis-os/ouroboros/subsystems/workflow/engine.py`

**✅ CORRECT - Route based on workflow type:**

```python
def _get_task_count_for_phase(self, state: WorkflowState, phase: int) -> int:
    """
    Get task count for phase (dynamic routing for static vs dynamic workflows).
    
    Encapsulates the static vs dynamic logic in one place.
    
    Args:
        state: Current workflow state
        phase: Phase number
        
    Returns:
        Number of tasks in phase
    """
    is_dynamic = self._is_dynamic(state)
    
    if is_dynamic and phase > 0:
        # Dynamic: from registry (cached)
        registry = self._get_or_create_dynamic_registry(state.session_id, state)
        metadata = registry.get_phase_metadata(phase)
        return metadata["task_count"]
    else:
        # Static: from renderer (filesystem)
        return self._renderer.get_task_count(state.workflow_type, phase)
```

**Why this works:**
- Single point of logic for task count retrieval
- Uses existing `_is_dynamic()` method (don't duplicate logic)
- Clear comments explaining routing

**❌ ANTI-PATTERN - Duplicate routing logic:**

```python
# In multiple places:
if state.workflow_metadata.dynamic_phases:
    # ... duplicate logic ...
```

---

### Pattern 4: Just-In-Time Information Disclosure

**File:** `.praxis-os/ouroboros/subsystems/workflow/engine.py`

**✅ CORRECT - Remove early content, add breadcrumb:**

```python
def start_workflow(self, workflow_type: str, target: str, options: Optional[Dict] = None):
    # ... state creation logic ...
    
    # NO phase content here (just-in-time disclosure)
    response = {
        "session_id": state.session_id,
        "workflow_type": workflow_type,
        "target_file": target,
        "current_phase": state.current_phase,
        "workflow_overview": {...},
        # NO phase_content! ← Force get_phase call
    }
    
    # Add breadcrumb to first action
    breadcrumb = {
        "⚡_NEXT_ACTION": "get_phase(phase=0)",
    }
    
    return add_workflow_guidance(response, breadcrumb=breadcrumb)
```

**Why this works:**
- Removes information leakage (`phase_content` gone)
- Forces sequential execution (must call `get_phase`)
- Breadcrumb provides explicit next action

**❌ ANTI-PATTERN - Return full content:**

```python
# Before (enables bypass):
response = {
    "phase_content": "...FULL PHASE CONTENT...",  # ← AI reads this, skips get_phase
}
```

---

### Pattern 5: Position-Aware Conditional Breadcrumbs

**File:** `.praxis-os/ouroboros/subsystems/workflow/engine.py`

**✅ CORRECT - Dynamic breadcrumb based on position:**

```python
def get_task(self, session_id: str, phase: int, task_number: int):
    # ... existing code to get task_content ...
    
    # Get task count for breadcrumb
    task_count = self._get_task_count_for_phase(state, phase)
    
    # Build breadcrumb based on position
    if task_number < task_count:
        # Not the last task → point to next task
        breadcrumb = {
            "🎯_CURRENT_POSITION": f"Task {task_number}/{task_count}",
            "⚡_NEXT_ACTION": f"get_task(phase={phase}, task_number={task_number + 1})",
        }
    else:
        # Last task → point to complete_phase
        breadcrumb = {
            "🎯_CURRENT_POSITION": f"Task {task_number}/{task_count} (final)",
            "⚡_NEXT_ACTION": f"complete_phase(phase={phase}, evidence={{...}})",
        }
    
    # Build response
    response = {
        "session_id": session_id,
        "workflow_type": state.workflow_type,
        "phase": phase,
        "task_number": task_number,
        "current_phase": state.current_phase,
        "phase_status": phase_status,
        "task_content": task_content,
    }
    
    return add_workflow_guidance(response, breadcrumb=breadcrumb)
```

**Why this works:**
- Dynamic routing (different breadcrumb for middle vs final task)
- Literal call syntax (copy-paste executable)
- Position indicator gives context

**❌ ANTI-PATTERN - Static breadcrumb:**

```python
# Always points to next task (wrong for final task):
breadcrumb = {"⚡_NEXT_ACTION": f"get_task(phase={phase}, task_number={task_number + 1})"}
```

---

### Pattern 6: Emoji Field Names for Visual Emphasis

**Used across all action handlers**

**✅ CORRECT - Distinctive emoji prefixes:**

```python
# Different emojis for different purposes:
"⚡_NEXT_ACTION": "..."     # Lightning = action directive
"🎯_CURRENT_POSITION": "..." # Target = position marker
"📊_PHASE_INFO": "..."       # Chart = metadata
"✅_PHASE_COMPLETE": "..."   # Check = completion
"🎉_WORKFLOW_COMPLETE": "..." # Party = celebration
```

**Why this works:**
- Visual distinction draws attention
- Consistent meaning across actions
- Recency bias + visual emphasis = high attention weight

**❌ ANTI-PATTERN - Generic field names:**

```python
"next_action": "..."  # ← Easy to miss in wall of JSON
"position": "..."
```

---

### Pattern 7: Graceful Degradation

**File:** `.praxis-os/ouroboros/subsystems/workflow/engine.py`

**✅ CORRECT - Log and continue without breadcrumb:**

```python
def get_task(self, session_id: str, phase: int, task_number: int):
    # ... existing code ...
    
    try:
        task_count = self._get_task_count_for_phase(state, phase)
        breadcrumb = self._generate_breadcrumb(phase, task_number, task_count)
    except Exception as e:
        logger.error(f"Breadcrumb generation failed: {e}", extra={"phase": phase})
        breadcrumb = None  # Workflow continues without breadcrumb
    
    # ... build response ...
    return add_workflow_guidance(response, breadcrumb=breadcrumb)
```

**Why this works:**
- Breadcrumb failure doesn't break workflow execution
- Error logged for debugging
- `breadcrumb=None` falls back to existing behavior

**❌ ANTI-PATTERN - Let exception propagate:**

```python
task_count = self._get_task_count_for_phase(state, phase)  # ← Crashes workflow if fails!
breadcrumb = ...
```

---

## 4. Common Pitfalls

### Pitfall 1: Using Training Data Instead of Project Standards

**❌ WRONG:**
```python
# "I know how to do error handling from training data"
raise Exception("Error occurred")
```

**✅ CORRECT:**
```python
# Query project standards first, use RendererError pattern
raise RendererError(
    what_failed="...",
    why_failed="...",
    how_to_fix="..."
)
```

### Pitfall 2: Premature Optimization

**❌ WRONG:**
```python
# Cache task count (not needed, adds complexity)
self._task_count_cache[(workflow_type, phase)] = task_count
```

**✅ CORRECT:**
```python
# Simple is fast enough (<5ms for glob)
task_files = list(phase_dir.glob("task-*-*.md"))
return len(task_files)
```

### Pitfall 3: Breaking Backward Compatibility

**❌ WRONG:**
```python
def add_workflow_guidance(response, breadcrumb):  # ← Required parameter!
```

**✅ CORRECT:**
```python
def add_workflow_guidance(response, breadcrumb=None):  # ← Optional
```

---

## 5. File Modification Checklist

For each file modified, verify:

- [ ] **guidance.py**
  - [ ] `breadcrumb` parameter optional (default `None`)
  - [ ] Dict merging order correct (guidance → response → breadcrumb)
  - [ ] Backward compatible (existing calls work)

- [ ] **workflow_renderer.py**
  - [ ] `get_task_count()` method added
  - [ ] Uses `glob("task-*-*.md")` pattern
  - [ ] Raises `RendererError` with actionable fix

- [ ] **engine.py**
  - [ ] `_get_task_count_for_phase()` helper added
  - [ ] Routes correctly (static vs dynamic)
  - [ ] `start_workflow()`: NO `phase_content`, breadcrumb added
  - [ ] `get_phase()`: Task count aware breadcrumb
  - [ ] `get_task()`: Position-aware breadcrumb (middle vs final)
  - [ ] `complete_phase()`: Next phase breadcrumb (or celebration)

- [ ] **All modified files**
  - [ ] Zero pylint errors
  - [ ] Type hints present
  - [ ] Docstrings updated
  - [ ] Comments explain WHY (not just WHAT)

---

## 6. Implementation Notes

### Import Statements

**Required imports for modified files:**

```python
# guidance.py (no new imports needed)
from typing import Dict, Any, Optional

# workflow_renderer.py (no new imports needed)
from pathlib import Path

# engine.py (no new imports needed)
# Uses existing imports
```

### Performance Considerations

From specs.md Section 6.2:
- Task count retrieval target: <5ms (static), <1ms (dynamic)
- Breadcrumb generation target: <1ms
- No caching needed - primitives are fast enough

### Testing Strategy

See Section 7 below for comprehensive testing approach with requirements traceability.

---

## 7. Testing Strategy

### 7.1 Requirements Traceability

**Total Requirements from srd.md:**
- **Functional Requirements**: 10 (FR-001 through FR-010)
- **Non-Functional Requirements**: 6 categories (Performance, Maintainability, Backward Compatibility, Usability, Reliability, Observability)

**Testing Coverage Mandate:**
- Every FR must map to at least 1 test
- Critical FRs (FR-001 through FR-008) must have ≥2 tests each (happy path + edge case)
- High priority FRs (FR-009, FR-010) must have ≥1 test each

---

### 7.2 Unit Test Plan

**Test File:** `ouroboros/subsystems/workflow/tests/test_guidance_breadcrumbs.py`

#### Test Group 1: add_workflow_guidance() (FR-009, FR-010)

```python
def test_add_workflow_guidance_without_breadcrumb():
    """Test backward compatibility: breadcrumb=None preserves existing behavior (FR-009)."""
    response = {"session_id": "test_123", "data": "test"}
    result = add_workflow_guidance(response)
    
    # Verify static guidance fields present
    assert result["⚠️_WORKFLOW_EXECUTION_MODE"] == "ACTIVE"  # FR-010
    assert result["🛑_DO_NOT_USE_EXTERNAL_TASK_TOOLS"]  # FR-010
    assert result["execution_model"]  # FR-010
    
    # Verify response data preserved
    assert result["session_id"] == "test_123"
    assert result["data"] == "test"
    
    # Verify no breadcrumb fields (backward compatible)
    assert "⚡_NEXT_ACTION" not in result

def test_add_workflow_guidance_with_breadcrumb():
    """Test breadcrumb positioning: appears at end of response (FR-009)."""
    response = {"session_id": "test_123", "data": "test"}
    breadcrumb = {"⚡_NEXT_ACTION": "get_phase(phase=0)"}
    result = add_workflow_guidance(response, breadcrumb=breadcrumb)
    
    # Verify breadcrumb fields present
    assert result["⚡_NEXT_ACTION"] == "get_phase(phase=0)"
    
    # Verify field ordering (breadcrumb last)
    keys = list(result.keys())
    assert keys[-1] == "⚡_NEXT_ACTION"  # Recency bias positioning

def test_add_workflow_guidance_field_ordering():
    """Test dict merging order: guidance → response → breadcrumb (FR-009)."""
    response = {"middle_field": "test"}
    breadcrumb = {"⚡_NEXT_ACTION": "test"}
    result = add_workflow_guidance(response, breadcrumb=breadcrumb)
    
    keys = list(result.keys())
    # Static guidance first
    assert keys[0] == "⚠️_WORKFLOW_EXECUTION_MODE"
    # Response middle
    assert "middle_field" in keys
    # Breadcrumb last
    assert keys[-1] == "⚡_NEXT_ACTION"
```

---

#### Test Group 2: WorkflowRenderer.get_task_count() (FR-006)

**Test File:** `ouroboros/subsystems/workflow/tests/test_renderer_task_count.py`

```python
def test_get_task_count_valid_phase(tmp_path):
    """Test task count retrieval for valid phase directory (FR-006)."""
    # Setup: Create phase directory with 5 task files
    phase_dir = tmp_path / "spec_creation_v1" / "phases" / "0"
    phase_dir.mkdir(parents=True)
    for i in range(1, 6):
        (phase_dir / f"task-{i}-test.md").touch()
    
    renderer = WorkflowRenderer(workflows_dir=tmp_path)
    count = renderer.get_task_count("spec_creation_v1", 0)
    
    assert count == 5  # Correct count

def test_get_task_count_missing_phase_directory():
    """Test error handling when phase directory not found (FR-006)."""
    renderer = WorkflowRenderer(workflows_dir=Path("/nonexistent"))
    
    with pytest.raises(RendererError) as exc_info:
        renderer.get_task_count("spec_creation_v1", 0)
    
    # Verify actionable error message
    assert "Phase directory not found" in str(exc_info.value)
    assert "mkdir -p" in str(exc_info.value)  # Actionable fix

def test_get_task_count_performance(tmp_path):
    """Test task count performance <5ms for <50 files (NFR-P1)."""
    # Setup: Create phase with 50 task files
    phase_dir = tmp_path / "test_workflow" / "phases" / "0"
    phase_dir.mkdir(parents=True)
    for i in range(1, 51):
        (phase_dir / f"task-{i}-test.md").touch()
    
    renderer = WorkflowRenderer(workflows_dir=tmp_path)
    
    import time
    start = time.perf_counter()
    count = renderer.get_task_count("test_workflow", 0)
    duration_ms = (time.perf_counter() - start) * 1000
    
    assert count == 50
    assert duration_ms < 5.0  # <5ms (NFR-P1)
```

---

#### Test Group 3: WorkflowEngine._get_task_count_for_phase() (FR-007, FR-008)

**Test File:** `ouroboros/subsystems/workflow/tests/test_engine_task_count_helper.py`

```python
def test_get_task_count_static_workflow():
    """Test routing to WorkflowRenderer for static workflows (FR-008)."""
    # Mock state with static workflow
    state = Mock(workflow_type="spec_creation_v1", workflow_metadata=Mock(dynamic_phases=False))
    engine = WorkflowEngine(renderer=Mock(), dynamic_registry=Mock())
    engine._renderer.get_task_count.return_value = 5
    
    count = engine._get_task_count_for_phase(state, phase=0)
    
    assert count == 5
    engine._renderer.get_task_count.assert_called_once_with("spec_creation_v1", 0)

def test_get_task_count_dynamic_workflow():
    """Test routing to DynamicContentRegistry for dynamic workflows (FR-007, FR-008)."""
    # Mock state with dynamic workflow
    state = Mock(
        session_id="test_session",
        workflow_metadata=Mock(dynamic_phases=True)
    )
    engine = WorkflowEngine(renderer=Mock(), dynamic_registry=Mock())
    registry = Mock()
    registry.get_phase_metadata.return_value = {"task_count": 3}
    engine._get_or_create_dynamic_registry.return_value = registry
    
    count = engine._get_task_count_for_phase(state, phase=1)
    
    assert count == 3
    registry.get_phase_metadata.assert_called_once_with(1)

def test_get_task_count_graceful_degradation():
    """Test graceful degradation when task count retrieval fails (NFR-R1)."""
    state = Mock(workflow_type="test", workflow_metadata=Mock(dynamic_phases=False))
    engine = WorkflowEngine(renderer=Mock(), dynamic_registry=Mock())
    engine._renderer.get_task_count.side_effect = RendererError("Phase not found")
    
    # Should not raise, returns None for graceful degradation
    count = engine._get_task_count_for_phase(state, phase=0)
    assert count is None
```

---

#### Test Group 4: Breadcrumb Generation (FR-001 through FR-005)

**Test File:** `ouroboros/subsystems/workflow/tests/test_engine_breadcrumbs.py`

```python
def test_start_workflow_no_phase_content():
    """Test just-in-time disclosure: phase_content removed (FR-001)."""
    engine = WorkflowEngine(renderer=Mock(), dynamic_registry=Mock())
    result = engine.start_workflow("spec_creation_v1", "design.md")
    
    # Verify phase_content NOT in response
    assert "phase_content" not in result
    # Verify breadcrumb present
    assert result["⚡_NEXT_ACTION"] == "get_phase(phase=0)"  # FR-002

def test_get_phase_breadcrumb_with_tasks():
    """Test get_phase breadcrumb points to first task (FR-003)."""
    state = Mock(session_id="test", workflow_type="test")
    engine = WorkflowEngine(renderer=Mock())
    engine._get_task_count_for_phase = Mock(return_value=5)
    
    result = engine.get_phase("test", phase=0)
    
    assert result["📊_PHASE_INFO"] == "Phase 0 has 5 tasks"
    assert result["⚡_NEXT_ACTION"] == "get_task(phase=0, task_number=1)"

def test_get_phase_breadcrumb_no_tasks():
    """Test get_phase breadcrumb edge case: phase with no tasks (FR-003)."""
    state = Mock(session_id="test", workflow_type="test")
    engine = WorkflowEngine(renderer=Mock())
    engine._get_task_count_for_phase = Mock(return_value=0)
    
    result = engine.get_phase("test", phase=2)
    
    assert result["📊_PHASE_INFO"] == "Phase 2 has no tasks"
    assert result["⚡_NEXT_ACTION"] == "complete_phase(phase=2, evidence={...})"

def test_get_task_breadcrumb_middle_task():
    """Test get_task breadcrumb for middle task (FR-004)."""
    state = Mock(session_id="test", workflow_type="test")
    engine = WorkflowEngine(renderer=Mock())
    engine._get_task_count_for_phase = Mock(return_value=5)
    
    result = engine.get_task("test", phase=0, task_number=3)
    
    assert result["🎯_CURRENT_POSITION"] == "Task 3/5"
    assert result["⚡_NEXT_ACTION"] == "get_task(phase=0, task_number=4)"

def test_get_task_breadcrumb_final_task():
    """Test get_task breadcrumb for final task (FR-004)."""
    state = Mock(session_id="test", workflow_type="test")
    engine = WorkflowEngine(renderer=Mock())
    engine._get_task_count_for_phase = Mock(return_value=5)
    
    result = engine.get_task("test", phase=0, task_number=5)
    
    assert result["🎯_CURRENT_POSITION"] == "Task 5/5 (final)"
    assert result["⚡_NEXT_ACTION"] == "complete_phase(phase=0, evidence={...})"

def test_complete_phase_breadcrumb_more_phases():
    """Test complete_phase breadcrumb points to next phase (FR-005)."""
    engine = WorkflowEngine(renderer=Mock())
    # Mock successful phase completion with next phase
    result_state = Mock(current_phase=1)
    engine._complete_phase_internal = Mock(return_value=Mock(new_state=result_state))
    
    result = engine.complete_phase("test", phase=0, evidence={})
    
    assert result["✅_PHASE_COMPLETE"] == "Phase 0 completed successfully"
    assert result["⚡_NEXT_ACTION"] == "get_phase(phase=1)"

def test_complete_phase_breadcrumb_workflow_complete():
    """Test complete_phase celebration when workflow complete (FR-005)."""
    engine = WorkflowEngine(renderer=Mock())
    # Mock workflow completion (no next phase)
    engine._complete_phase_internal = Mock(return_value=Mock(new_state=None))
    
    result = engine.complete_phase("test", phase=5, evidence={})
    
    assert result["🎉_WORKFLOW_COMPLETE"] == "All phases completed successfully"
    assert "⚡_NEXT_ACTION" not in result  # No next action when complete
```

---

### 7.3 Integration Test Plan

**Test File:** `ouroboros/subsystems/workflow/tests/test_workflow_breadcrumb_integration.py`

#### Test 1: Full Static Workflow Execution (FR-001 through FR-010, NFR-C1)

```python
def test_full_static_workflow_with_breadcrumbs():
    """Test complete workflow execution with breadcrumbs (spec_creation_v1)."""
    engine = WorkflowEngine(renderer=WorkflowRenderer(), dynamic_registry=None)
    
    # Step 1: start_workflow
    result = engine.start_workflow("spec_creation_v1", "design.md")
    assert "phase_content" not in result  # FR-001
    assert result["⚡_NEXT_ACTION"] == "get_phase(phase=0)"  # FR-002
    session_id = result["session_id"]
    
    # Step 2: get_phase
    result = engine.get_phase(session_id, phase=0)
    assert "📊_PHASE_INFO" in result  # FR-003
    assert "⚡_NEXT_ACTION" in result  # FR-003
    assert "get_task(phase=0, task_number=1)" in result["⚡_NEXT_ACTION"]
    
    # Step 3: get_task (first)
    result = engine.get_task(session_id, phase=0, task_number=1)
    assert result["🎯_CURRENT_POSITION"] == "Task 1/5"  # FR-004
    assert "get_task(phase=0, task_number=2)" in result["⚡_NEXT_ACTION"]
    
    # Step 4: get_task (final)
    result = engine.get_task(session_id, phase=0, task_number=5)
    assert "(final)" in result["🎯_CURRENT_POSITION"]  # FR-004
    assert "complete_phase(phase=0" in result["⚡_NEXT_ACTION"]
    
    # Step 5: complete_phase
    result = engine.complete_phase(session_id, phase=0, evidence={"test": True})
    assert "✅_PHASE_COMPLETE" in result  # FR-005
    assert "get_phase(phase=1)" in result["⚡_NEXT_ACTION"]
```

#### Test 2: Backward Compatibility (NFR-C1)

```python
def test_existing_workflows_still_work():
    """Test backward compatibility: existing workflow sessions unaffected."""
    engine = WorkflowEngine(renderer=WorkflowRenderer())
    
    # Old-style call (without expecting breadcrumbs)
    result = engine.start_workflow("spec_creation_v1", "design.md")
    
    # Verify existing fields still present
    assert "session_id" in result
    assert "workflow_overview" in result
    
    # Can still complete workflow without using breadcrumbs
    session_id = result["session_id"]
    phase_result = engine.get_phase(session_id, 0)
    assert "phase_content" in phase_result  # Still accessible via get_phase
```

---

### 7.4 Performance Test Plan

**Test File:** `ouroboros/subsystems/workflow/tests/test_performance_benchmarks.py`

```python
def test_task_count_performance_static(benchmark):
    """Benchmark task count retrieval <5ms (NFR-P1)."""
    renderer = WorkflowRenderer(workflows_dir=Path(".praxis-os/workflows"))
    
    result = benchmark(renderer.get_task_count, "spec_creation_v1", 0)
    
    assert result > 0
    assert benchmark.stats["mean"] < 0.005  # <5ms average

def test_breadcrumb_generation_performance(benchmark):
    """Benchmark breadcrumb generation <1ms (NFR-P2)."""
    def generate_breadcrumb():
        task_number = 3
        task_count = 5
        return {
            "🎯_CURRENT_POSITION": f"Task {task_number}/{task_count}",
            "⚡_NEXT_ACTION": f"get_task(phase=0, task_number={task_number + 1})"
        }
    
    result = benchmark(generate_breadcrumb)
    
    assert "⚡_NEXT_ACTION" in result
    assert benchmark.stats["mean"] < 0.001  # <1ms average
```

---

### 7.5 Manual Behavioral Validation (NFR-O1)

**Objective:** Verify AI agents follow breadcrumbs (target: >95%)

**Test Protocol:**
1. Run workflow with AI agent (this session serves as validation)
2. Track action sequences:
   - `start_workflow` → `get_phase` → `get_task(1)` → `get_task(2)` → ... → `complete_phase`
3. Compare actual action sequence to breadcrumb suggestions
4. Calculate following rate: `(actions matching breadcrumb) / (total actions)`

**Expected Result:**
- Following rate >95%
- No task skipping
- Sequential execution maintained

---

### 7.6 Test Execution Checklist

**Before committing:**
- [ ] All unit tests passing (`pytest ouroboros/subsystems/workflow/tests/`)
- [ ] Integration tests passing
- [ ] Performance benchmarks met (NFR-P1, NFR-P2)
- [ ] Test coverage ≥90% for modified code
- [ ] Zero pylint errors (`tox -e lint`)
- [ ] Manual behavioral validation complete

**Coverage Targets:**
- `guidance.py`: ≥95% coverage
- `workflow_renderer.py`: ≥90% coverage
- `engine.py` (modified methods only): ≥90% coverage

---

### 7.7 Testing Summary

**Total Tests Planned:**
- Unit tests: 14 tests across 4 test files
- Integration tests: 2 comprehensive workflow tests
- Performance tests: 2 benchmark tests
- Behavioral validation: 1 manual test

**Requirements Coverage:**
- FR-001 through FR-010: 100% covered (every FR has ≥1 test)
- NFR-P1, NFR-P2: Performance benchmarks
- NFR-C1: Backward compatibility integration test
- NFR-R1: Graceful degradation unit test
- NFR-O1: Behavioral validation

---

## 8. Deployment Guidance

###8.1 Overview

This is an internal code enhancement to the workflow subsystem. No external deployment artifacts, database migrations, or infrastructure changes are required.

**Deployment Type:** Code-only change to existing MCP server

**Deployment Strategy:** Standard code deployment with backward compatibility

---

### 8.2 Pre-Deployment Checklist

**Before merging to main:**
- [ ] All unit tests passing (`pytest ouroboros/subsystems/workflow/tests/`)
- [ ] Integration tests passing
- [ ] Performance benchmarks met (<5ms task count, <1ms breadcrumb generation)
- [ ] Test coverage ≥90% for modified code
- [ ] Zero pylint errors (`tox -e lint`)
- [ ] Code reviewed and approved
- [ ] Manual behavioral validation complete (>95% breadcrumb following rate)

**Before deploying:**
- [ ] Merge to main branch
- [ ] CI/CD pipeline passes (all tests, linting)
- [ ] Staging deployment successful
- [ ] Smoke test on staging (run workflow, verify breadcrumbs appear)

---

### 8.3 Deployment Steps

**Step 1: Deploy to Staging**

```bash
# Standard MCP server deployment
# No special steps required - backward compatible change
git checkout main
git pull origin main

# Restart MCP server to pick up changes
# (Deployment method varies by environment)
```

**Step 2: Verify on Staging**

```bash
# Test workflow with breadcrumbs
pos_workflow(action="start_workflow", workflow_type="spec_creation_v1", target_file="test.md")
# Verify response includes ⚡_NEXT_ACTION field

pos_workflow(action="get_phase", session_id="...", phase=0)
# Verify response includes 📊_PHASE_INFO and ⚡_NEXT_ACTION

pos_workflow(action="get_task", session_id="...", phase=0, task_number=1)
# Verify response includes 🎯_CURRENT_POSITION and ⚡_NEXT_ACTION
```

**Step 3: Monitor Staging**

- [ ] Check MCP server logs for errors
- [ ] Verify workflow execution completes successfully
- [ ] Verify no performance degradation (check action duration metrics)
- [ ] Verify backward compatibility (existing workflows still work)

**Step 4: Deploy to Production**

```bash
# Standard production deployment
# No special configuration required
```

**Step 5: Post-Deployment Verification**

- [ ] Smoke test: Execute workflow end-to-end
- [ ] Monitor behavioral metrics (breadcrumb following rate)
- [ ] Check server logs for errors
- [ ] Verify performance metrics (p95 latency)

---

### 8.4 Configuration

**No Configuration Changes Required**

This feature requires no new configuration. It modifies existing workflow engine behavior with backward-compatible changes.

**Existing Configuration (unchanged):**
- Workflow definitions in `.praxis-os/workflows/`
- MCP server configuration in `.praxis-os/config/mcp.yaml`

---

### 8.5 Rollback Strategy

**If Issues Detected:**

**Severity: Critical (workflows broken, server crashes)**
1. Immediately rollback to previous version:
   ```bash
   git revert <commit-hash>
   # Or redeploy previous version
   ```
2. Restart MCP server
3. Verify workflows functional
4. Investigate root cause

**Severity: High (performance degradation, breadcrumb errors)**
1. Assess impact (are workflows completing successfully?)
2. If workflows still functional: Monitor and fix forward
3. If workflows broken: Rollback as above

**Severity: Medium (breadcrumbs not appearing, but workflows work)**
1. Fix forward (breadcrumb absence doesn't break workflows)
2. Deploy fix with next release

**Rollback Safety:**
- Backward compatible: Old clients work without breadcrumbs
- No database changes: No data migration needed
- No state changes: Workflow state format unchanged

---

### 8.6 Monitoring

**Key Metrics to Watch Post-Deployment:**

1. **Workflow Engagement Rate** (Goal: 99.9%)
   - Metric: `workflow.engagement_rate`
   - Baseline: 99%
   - Target: 99.9%
   - Alert: <99% (regression)

2. **Breadcrumb Following Rate** (Goal: >95%)
   - Metric: `workflow.breadcrumb.followed_rate`
   - Baseline: N/A (new metric)
   - Target: >95%
   - Alert: <80% (low following)

3. **Workflow Action Duration** (Goal: No increase)
   - Metric: `workflow.action.duration_ms` (p95)
   - Baseline: Varies by action
   - Target: <20% increase
   - Alert: >50% increase (performance regression)

4. **Task Count Retrieval Performance** (Goal: <5ms)
   - Metric: `workflow.task_count.duration_ms` (p95)
   - Baseline: N/A (new metric)
   - Target: <5ms (static), <1ms (dynamic)
   - Alert: >10ms (performance issue)

5. **Error Rate** (Goal: No increase)
   - Metric: `workflow.errors` (count)
   - Baseline: Varies
   - Target: No increase
   - Alert: >2x baseline (regression)

**Dashboard:** Add workflow breadcrumb metrics to existing observability dashboard

**Logs:** Monitor MCP server logs for:
- `Breadcrumb generation failed` (ERROR level)
- `Task count retrieval failed` (ERROR level)
- Increased error rates in workflow actions

---

### 8.7 Troubleshooting

**Common Issues:**

**Issue 1: Breadcrumbs not appearing**

**Symptoms:**
- Workflow actions return responses without `⚡_NEXT_ACTION` field

**Diagnosis:**
```bash
# Check MCP server logs
tail -f ~/Library/Application\ Support/Cursor/logs/.../MCP*.log | grep -i breadcrumb

# Look for "Breadcrumb generation failed" or "Task count retrieval failed"
```

**Resolution:**
- Check if task count retrieval failing (missing phase directory?)
- Verify `add_workflow_guidance()` called with breadcrumb parameter
- Check Python version (requires 3.7+ for dict ordering)

---

**Issue 2: Performance degradation**

**Symptoms:**
- Workflow actions taking longer than baseline

**Diagnosis:**
```bash
# Check action duration metrics
# Look for workflow.action.duration_ms p95 increase

# Profile task count retrieval
import time
start = time.perf_counter()
renderer.get_task_count("spec_creation_v1", 0)
duration = (time.perf_counter() - start) * 1000
print(f"Task count took {duration}ms")
```

**Resolution:**
- Verify phase directory has <50 files (NFR-P1 target)
- Check if filesystem slow (disk I/O issues)
- Consider caching if many workflow executions

---

**Issue 3: Workflow execution broken**

**Symptoms:**
- Workflows fail to complete
- Evidence validation errors increase

**Diagnosis:**
- Check if `phase_content` removal broke existing workflows
- Verify backward compatibility (can still call `get_phase` to get content)

**Resolution:**
- Rollback immediately if critical
- Fix forward if isolated issue

---

### 8.8 Deployment Summary

**Deployment Complexity:** Low
- Code-only change
- Backward compatible
- No migrations, config changes, or infrastructure updates

**Risk Level:** Low
- Backward compatible (existing workflows unaffected)
- Graceful degradation (breadcrumb failures don't break workflows)
- Easy rollback (no state changes)

**Timeline:**
- Staging deployment: 10 minutes
- Staging verification: 30 minutes
- Production deployment: 10 minutes
- Post-deployment monitoring: 24 hours

**Success Criteria:**
- All tests passing
- No error rate increase
- Breadcrumb following rate >95%
- No performance regression
- Workflow engagement rate improvement (99% → 99.9%)

