# Implementation Tasks: Resilient Index Building

**Project**: prAxIs OS - RAG Subsystem Enhancement  
**Feature**: Resilient Index Building with Fractal Build Status  
**Date**: 2025-11-14  
**Status**: Task Breakdown  
**Version**: 1.0

---

## Overview

This document breaks down the implementation of resilient index building into 8 phases with 38 tasks. Each task includes acceptance criteria, dependencies, time estimates, and validation gates.

**Total Estimated Time**: 18-28 hours

**Implementation Strategy**: Bottom-up (foundation → fractal → integration)

---

## Phase 0: Performance Foundation

**Purpose**: Implement caching infrastructure before adding build status checks  
**Duration**: 2-3 hours  
**Dependencies**: None  
**Rationale**: Cache must exist before components start checking build status

### Task 0.1: Implement Build State Cache

**File**: `ouroboros/subsystems/rag/index_manager.py`

**Description**: Add in-memory cache for build status with thread safety

**Changes**:
```python
class IndexManager:
    def __init__(self, ...):
        self._build_state_cache: Dict[str, BuildStatus] = {}
        self._build_state_cache_time: Dict[str, float] = {}
        self._build_state_cache_lock = threading.RLock()
        self._build_state_cache_ttl: float = 60.0  # BUILT state
        self._building_state_cache_ttl: float = 5.0  # BUILDING state (dynamic)
```

**Acceptance Criteria**:
- [ ] Cache dicts initialized in `__init__()`
- [ ] `RLock` created for thread safety
- [ ] TTL constants defined (60s, 5s)
- [ ] Type hints correct (MyPy passes)

**Time Estimate**: 30 minutes

**Dependencies**: None

---

### Task 0.2: Implement Dynamic TTL Calculation

**File**: `ouroboros/subsystems/rag/index_manager.py`

**Description**: Add method to calculate TTL based on build progress

**Changes**:
```python
def _calculate_building_ttl(self, progress_percent: float) -> float:
    """
    Dynamic TTL for BUILDING state based on progress.
    
    Early stage (0-10%): 2s TTL (fast changes)
    Mid stage (10-50%): 5s TTL (steady progress)
    Late stage (50-100%): 10s TTL (slow, near completion)
    """
    if progress_percent < 10:
        return 2.0
    elif progress_percent < 50:
        return 5.0
    else:
        return 10.0
```

**Acceptance Criteria**:
- [ ] Method implemented with correct logic
- [ ] Returns 2s for 0-10% progress
- [ ] Returns 5s for 10-50% progress
- [ ] Returns 10s for 50-100% progress
- [ ] Unit test covers all branches

**Time Estimate**: 30 minutes

**Dependencies**: Task 0.1

---

### Task 0.3: Implement Cache Invalidation

**File**: `ouroboros/subsystems/rag/index_manager.py`

**Description**: Add method to atomically invalidate cache entries

**Changes**:
```python
def _invalidate_build_cache(self, index_name: str) -> None:
    """Atomically invalidate build state cache for an index."""
    with self._build_state_cache_lock:
        self._build_state_cache.pop(index_name, None)
        self._build_state_cache_time.pop(index_name, None)
```

**Acceptance Criteria**:
- [ ] Method implemented with lock protection
- [ ] Both dicts cleared atomically
- [ ] No race conditions (verified by chaos test)
- [ ] Unit test verifies atomicity

**Time Estimate**: 30 minutes

**Dependencies**: Task 0.1

---

### Task 0.4: Add Thread Safety to _indexes Dict

**File**: `ouroboros/subsystems/rag/index_manager.py`

**Description**: Protect `_indexes` dict iteration with lock

**Changes**:
```python
class IndexManager:
    def __init__(self, ...):
        self._indexes_lock = threading.RLock()
        
    def _iter_indexes(self):
        """Safely iterate over indexes."""
        with self._indexes_lock:
            return list(self._indexes.items())
```

**Acceptance Criteria**:
- [ ] `_indexes_lock` created in `__init__()`
- [ ] All dict iterations protected by lock
- [ ] No concurrent modification errors (chaos test)
- [ ] Unit test verifies thread safety

**Time Estimate**: 30 minutes

**Dependencies**: Task 0.1

---

**Phase 0 Validation Gate**:
- [ ] All cache infrastructure implemented
- [ ] Thread safety verified (unit tests pass)
- [ ] MyPy type checking passes
- [ ] No linter errors

---

## Phase 1: Foundational Types

**Purpose**: Define data models and enums before implementing logic  
**Duration**: 1-2 hours  
**Dependencies**: Phase 0

### Task 1.1: Define IndexBuildState Enum

**File**: `ouroboros/subsystems/rag/base.py`

**Description**: Create enum for build states with priority

**Changes**:
```python
from enum import Enum

class IndexBuildState(str, Enum):
    """Build state enum with priority for aggregation."""
    NOT_BUILT = "not_built"
    QUEUED_TO_BUILD = "queued_to_build"
    BUILDING = "building"
    BUILT = "built"
    FAILED = "failed"
    
    @property
    def priority(self) -> int:
        """Priority for aggregation (higher = worse)."""
        return {
            IndexBuildState.BUILT: 0,
            IndexBuildState.NOT_BUILT: 1,
            IndexBuildState.QUEUED_TO_BUILD: 2,
            IndexBuildState.BUILDING: 3,
            IndexBuildState.FAILED: 4,
        }[self]
```

**Acceptance Criteria**:
- [ ] Enum defined with 5 states
- [ ] `priority` property implemented
- [ ] Priority order correct (FAILED > BUILDING > QUEUED > NOT_BUILT > BUILT)
- [ ] Unit test verifies priority calculation

**Time Estimate**: 20 minutes

**Dependencies**: None

---

### Task 1.2: Define BuildStatus Pydantic Model

**File**: `ouroboros/subsystems/rag/base.py`

**Description**: Create Pydantic model for build status

**Changes**:
```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class BuildStatus(BaseModel):
    """Build status model (mirrors HealthStatus)."""
    state: IndexBuildState
    message: str
    progress_percent: float = Field(ge=0.0, le=100.0)
    details: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    ttl_expires_at: Optional[datetime] = None
    
    class Config:
        frozen = True
        extra = "forbid"
```

**Acceptance Criteria**:
- [ ] Model defined with all fields
- [ ] `progress_percent` constrained (0-100)
- [ ] Model is frozen (immutable)
- [ ] Model forbids extra fields
- [ ] Unit test validates constraints

**Time Estimate**: 20 minutes

**Dependencies**: Task 1.1

---

### Task 1.3: Define IndexBuildConfig Schema

**File**: `ouroboros/config/schemas/indexes.py`

**Description**: Create config schema with validation

**Changes**: (See specs.md Section 4.2 for full schema)

**Acceptance Criteria**:
- [ ] All 9 config fields defined
- [ ] Default values set correctly
- [ ] Field constraints applied (ge, le)
- [ ] `model_post_init()` validation implemented
- [ ] Unit test verifies validation warnings

**Time Estimate**: 40 minutes

**Dependencies**: None

---

### Task 1.4: Update ComponentDescriptor

**File**: `ouroboros/shared/component_helpers.py`

**Description**: Add `build_status_check` field to descriptor

**Changes**:
```python
@dataclass
class ComponentDescriptor:
    name: str
    health_check: Callable[[], HealthStatus]
    build_status_check: Callable[[], BuildStatus]  # NEW
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
```

**Acceptance Criteria**:
- [ ] `build_status_check` field added
- [ ] Type hint correct
- [ ] Existing code still works (backward compatible)
- [ ] Unit test verifies field exists

**Time Estimate**: 15 minutes

**Dependencies**: Task 1.2

---

**Phase 1 Validation Gate**:
- [ ] All types defined and importable
- [ ] Pydantic validation works correctly
- [ ] Unit tests pass (>90% coverage)
- [ ] MyPy type checking passes

---

## Phase 2: Fractal Pattern Implementation

**Purpose**: Implement fractal build status aggregation  
**Duration**: 3-4 hours  
**Dependencies**: Phase 1

### Task 2.1: Implement dynamic_build_status() Helper

**File**: `ouroboros/shared/component_helpers.py`

**Description**: Create helper to aggregate component build statuses

**Changes**: (See specs.md Section 2.6 for full implementation)

**Acceptance Criteria**:
- [ ] Function signature matches spec
- [ ] Aggregates state (worst-first priority)
- [ ] Calculates average progress
- [ ] Aggregates messages
- [ ] Returns BuildStatus
- [ ] Unit test covers all state combinations

**Time Estimate**: 45 minutes

**Dependencies**: Task 1.2, Task 1.4

---

### Task 2.2: Add Abstract build_status() to BaseIndex

**File**: `ouroboros/subsystems/rag/base.py`

**Description**: Add abstract method to base class

**Changes**:
```python
@abstractmethod
def build_status(self) -> BuildStatus:
    """
    Get current build status of this index.
    
    Returns fractal aggregation of component build statuses.
    Must be implemented by all index subclasses.
    """
    pass
```

**Acceptance Criteria**:
- [ ] Abstract method added
- [ ] Docstring complete
- [ ] MyPy enforces implementation in subclasses
- [ ] No existing code breaks

**Time Estimate**: 15 minutes

**Dependencies**: Task 1.2

---

### Task 2.3: Implement Component Build Status Checks (StandardsIndex)

**File**: `ouroboros/subsystems/rag/standards/container.py`

**Description**: Implement lightweight build status checks for vector, FTS, metadata

**Changes**: (See specs.md Section 2.3 for full implementation)

**Acceptance Criteria**:
- [ ] `_check_vector_build_status()` implemented
- [ ] `_check_fts_build_status()` implemented
- [ ] `_check_metadata_build_status()` implemented
- [ ] Each check is lightweight (<100ms)
- [ ] Checks verify: table exists + has rows
- [ ] Progress files read if building
- [ ] Unit tests cover all states

**Time Estimate**: 60 minutes

**Dependencies**: Task 1.2, Task 2.1

---

### Task 2.4: Update StandardsIndex Components Registration

**File**: `ouroboros/subsystems/rag/standards/container.py`

**Description**: Register build status checks in component descriptors

**Changes**:
```python
self.components = {
    "vector": ComponentDescriptor(
        name="vector",
        health_check=self._check_vector_health,
        build_status_check=self._check_vector_build_status,  # NEW
        description="LanceDB vector index"
    ),
    # ... similar for metadata, fts
}
```

**Acceptance Criteria**:
- [ ] All components have `build_status_check` registered
- [ ] FTS component conditionally registered (if enabled)
- [ ] No breaking changes to existing health checks
- [ ] Unit test verifies registration

**Time Estimate**: 20 minutes

**Dependencies**: Task 2.3

---

### Task 2.5: Implement build_status() in StandardsIndex

**File**: `ouroboros/subsystems/rag/standards/container.py`

**Description**: Implement fractal aggregation method

**Changes**:
```python
def build_status(self) -> BuildStatus:
    """Aggregate build status from all components."""
    return dynamic_build_status(self.components)
```

**Acceptance Criteria**:
- [ ] Method implemented
- [ ] Calls `dynamic_build_status()`
- [ ] Returns aggregated BuildStatus
- [ ] Integration test verifies fractal aggregation

**Time Estimate**: 15 minutes

**Dependencies**: Task 2.1, Task 2.4

---

### Task 2.6: Implement Component Build Status Checks (CodeIndex)

**File**: `ouroboros/subsystems/rag/code/container.py`

**Description**: Implement build status checks for semantic and graph components

**Changes**: Similar to Task 2.3, but for CodeIndex

**Acceptance Criteria**:
- [ ] `_check_semantic_build_status()` implemented
- [ ] `_check_graph_build_status()` implemented
- [ ] Graph component conditionally registered (if enabled)
- [ ] Unit tests cover all states

**Time Estimate**: 45 minutes

**Dependencies**: Task 1.2, Task 2.1

---

### Task 2.7: Implement build_status() in CodeIndex

**File**: `ouroboros/subsystems/rag/code/container.py`

**Description**: Implement fractal aggregation for CodeIndex

**Changes**: Same as Task 2.5, but for CodeIndex

**Acceptance Criteria**:
- [ ] Method implemented
- [ ] Calls `dynamic_build_status()`
- [ ] Integration test verifies aggregation

**Time Estimate**: 15 minutes

**Dependencies**: Task 2.1, Task 2.6

---

**Phase 2 Validation Gate**:
- [ ] All indexes implement `build_status()`
- [ ] Fractal aggregation works correctly
- [ ] Component checks are lightweight (<100ms each)
- [ ] Integration tests pass
- [ ] MyPy type checking passes

---

## Phase 3: IndexManager Integration

**Purpose**: Integrate build status checking into query routing  
**Duration**: 2-3 hours  
**Dependencies**: Phase 2

### Task 3.1: Implement _get_required_indexes_for_action()

**File**: `ouroboros/subsystems/rag/index_manager.py`

**Description**: Map actions to required indexes

**Changes**:
```python
def _get_required_indexes_for_action(self, action: str) -> List[str]:
    """Map action to required indexes."""
    mapping = {
        "search_standards": ["standards"],
        "search_code": ["code"],
        "search_ast": ["code"],
        "find_callers": ["code"],
        "find_dependencies": ["code"],
        "find_call_paths": ["code"],
    }
    return mapping.get(action, [])
```

**Acceptance Criteria**:
- [ ] Method implemented
- [ ] All actions mapped
- [ ] Returns list of index names
- [ ] Unit test verifies mapping

**Time Estimate**: 20 minutes

**Dependencies**: None

---

### Task 3.2: Implement _check_build_readiness()

**File**: `ouroboros/subsystems/rag/index_manager.py`

**Description**: Check cache and call index.build_status() if needed

**Changes**: (See specs.md Section 2.1 for full implementation)

**Acceptance Criteria**:
- [ ] Method implemented
- [ ] Checks cache first (with lock)
- [ ] Calls `index.build_status()` on cache miss
- [ ] Updates cache with dynamic TTL
- [ ] Returns status if not BUILT
- [ ] Unit test verifies cache hit/miss logic

**Time Estimate**: 40 minutes

**Dependencies**: Task 0.1, Task 0.2, Task 2.2

---

### Task 3.3: Implement _format_building_response()

**File**: `ouroboros/subsystems/rag/index_manager.py`

**Description**: Format "building" response with progress

**Changes**: (See specs.md Section 2.1 for full implementation)

**Acceptance Criteria**:
- [ ] Method implemented
- [ ] Includes progress percentage
- [ ] Includes retry suggestion (30-60s)
- [ ] Includes estimated time remaining
- [ ] Unit test verifies format

**Time Estimate**: 20 minutes

**Dependencies**: Task 1.2

---

### Task 3.4: Implement _format_failed_response()

**File**: `ouroboros/subsystems/rag/index_manager.py`

**Description**: Format "failed" response with remediation

**Changes**: (See specs.md Section 2.1 for full implementation)

**Acceptance Criteria**:
- [ ] Method implemented
- [ ] Includes error details
- [ ] Includes remediation steps
- [ ] Includes TTL expiry time
- [ ] Unit test verifies format

**Time Estimate**: 20 minutes

**Dependencies**: Task 1.2

---

### Task 3.5: Implement _attach_build_metadata()

**File**: `ouroboros/subsystems/rag/index_manager.py`

**Description**: Attach build status metadata to successful queries

**Changes**: (See specs.md Section 2.1 for full implementation)

**Acceptance Criteria**:
- [ ] Method implemented
- [ ] Includes cache hit/miss info
- [ ] Includes build timestamp
- [ ] Unit test verifies metadata

**Time Estimate**: 15 minutes

**Dependencies**: None

---

### Task 3.6: Update route_action() with Build Status Checking

**File**: `ouroboros/subsystems/rag/index_manager.py`

**Description**: Integrate build status checks into query routing

**Changes**: (See specs.md Section 2.1 for full implementation)

**Acceptance Criteria**:
- [ ] Calls `_check_build_readiness()` before query
- [ ] Returns "building" response if BUILDING
- [ ] Returns "failed" response if FAILED
- [ ] Executes query if BUILT
- [ ] Attaches metadata to successful queries
- [ ] Integration test verifies all paths

**Time Estimate**: 40 minutes

**Dependencies**: Task 3.1, Task 3.2, Task 3.3, Task 3.4, Task 3.5

---

**Phase 3 Validation Gate**:
- [ ] `route_action()` checks build status before queries
- [ ] Cache hit rate >99% (performance test)
- [ ] Query overhead <2ms for BUILT indexes
- [ ] Integration tests pass
- [ ] No breaking changes to existing queries

---

## Phase 4: Corruption Handling

**Purpose**: Implement auto-repair on corruption detection  
**Duration**: 2-3 hours  
**Dependencies**: Phase 3

### Task 4.1: Implement set_corruption_handler() in BaseIndex

**File**: `ouroboros/subsystems/rag/base.py`

**Description**: Add method to inject corruption handler callback

**Changes**: (See specs.md Section 2.2 for full implementation)

**Acceptance Criteria**:
- [ ] Method implemented
- [ ] Stores callback in `_corruption_handler` attribute
- [ ] Callback signature documented
- [ ] Unit test verifies injection

**Time Estimate**: 15 minutes

**Dependencies**: None

---

### Task 4.2: Implement _handle_corruption() in IndexManager

**File**: `ouroboros/subsystems/rag/index_manager.py`

**Description**: Handle corruption detection and trigger auto-repair

**Changes**: (See specs.md Section 2.1 for full implementation)

**Acceptance Criteria**:
- [ ] Method implemented
- [ ] Logs corruption event
- [ ] Emits telemetry (if enabled)
- [ ] Invalidates cache atomically
- [ ] Sets state = BUILDING
- [ ] Starts background rebuild
- [ ] Raises ActionableError
- [ ] Unit test verifies all steps

**Time Estimate**: 45 minutes

**Dependencies**: Task 0.3, Task 4.1

---

### Task 4.3: Implement _rebuild_index_background()

**File**: `ouroboros/subsystems/rag/index_manager.py`

**Description**: Start background rebuild in daemon thread

**Changes**: (See specs.md Section 2.1 for full implementation)

**Acceptance Criteria**:
- [ ] Method implemented
- [ ] Checks if rebuild already in progress
- [ ] Starts daemon thread
- [ ] Thread calls `index.build()` with progress callback
- [ ] Unit test verifies thread creation
- [ ] Integration test verifies rebuild completes

**Time Estimate**: 30 minutes

**Dependencies**: Task 4.2

---

### Task 4.4: Inject Corruption Handlers in IndexManager.__init__()

**File**: `ouroboros/subsystems/rag/index_manager.py`

**Description**: Inject handlers into all indexes at initialization

**Changes**:
```python
def __init__(self, ...):
    # ... existing init ...
    
    # Inject corruption handlers
    for index_name, index in self._indexes.items():
        index.set_corruption_handler(
            lambda error, op: self._handle_corruption(index_name, error, op)
        )
```

**Acceptance Criteria**:
- [ ] Handlers injected for all indexes
- [ ] Lambda captures `index_name` correctly
- [ ] Unit test verifies injection

**Time Estimate**: 15 minutes

**Dependencies**: Task 4.1, Task 4.2

---

### Task 4.5: Add Corruption Detection to StandardsIndex.search()

**File**: `ouroboros/subsystems/rag/standards/container.py`

**Description**: Catch corruption errors and trigger handler

**Changes**: (See specs.md Section 2.3 for full implementation)

**Acceptance Criteria**:
- [ ] Try/except wraps search logic
- [ ] `is_corruption_error()` checks exception
- [ ] Calls `_corruption_handler` if corruption detected
- [ ] Raises ActionableError with remediation
- [ ] Integration test verifies auto-repair

**Time Estimate**: 20 minutes

**Dependencies**: Task 4.1, Task 4.2

---

### Task 4.6: Add Corruption Detection to StandardsIndex.build()

**File**: `ouroboros/subsystems/rag/standards/container.py`

**Description**: Catch corruption errors during build

**Changes**: Similar to Task 4.5, but for `build()` method

**Acceptance Criteria**:
- [ ] Try/except wraps build logic
- [ ] Calls corruption handler if detected
- [ ] Raises ActionableError
- [ ] Integration test verifies handling

**Time Estimate**: 15 minutes

**Dependencies**: Task 4.1, Task 4.2

---

### Task 4.7: Add Corruption Detection to StandardsIndex.update()

**File**: `ouroboros/subsystems/rag/standards/container.py`

**Description**: Catch corruption errors during update

**Changes**: Similar to Task 4.5, but for `update()` method

**Acceptance Criteria**:
- [ ] Try/except wraps update logic
- [ ] Calls corruption handler if detected
- [ ] Raises ActionableError
- [ ] Integration test verifies handling

**Time Estimate**: 15 minutes

**Dependencies**: Task 4.1, Task 4.2

---

### Task 4.8: Add Corruption Detection to CodeIndex

**File**: `ouroboros/subsystems/rag/code/container.py`

**Description**: Add corruption handling to CodeIndex (search, build, update)

**Changes**: Same as Tasks 4.5, 4.6, 4.7, but for CodeIndex

**Acceptance Criteria**:
- [ ] All three methods have corruption handling
- [ ] Integration tests verify auto-repair

**Time Estimate**: 30 minutes

**Dependencies**: Task 4.1, Task 4.2

---

### Task 4.9: Add Corruption Handling to route_action()

**File**: `ouroboros/subsystems/rag/index_manager.py`

**Description**: Catch corruption errors in query routing and return graceful response

**Changes**: (See specs.md Section 2.1 for full implementation)

**Acceptance Criteria**:
- [ ] Try/except wraps query execution
- [ ] Catches corruption errors
- [ ] Returns "building" response (not error)
- [ ] Subsequent queries see BUILDING state
- [ ] Integration test verifies graceful degradation

**Time Estimate**: 20 minutes

**Dependencies**: Task 3.6, Task 4.2

---

**Phase 4 Validation Gate**:
- [ ] Corruption detection works in all operations
- [ ] Auto-repair triggers successfully
- [ ] Background rebuild completes
- [ ] Subsequent queries return "building" status
- [ ] Eventual consistency achieved (integration test)
- [ ] Chaos test: mid-build corruption handled

---

## Phase 5: Progress Reporting

**Purpose**: Implement progress tracking and reporting  
**Duration**: 2-3 hours  
**Dependencies**: Phase 2

### Task 5.1: Implement Progress File Writing

**File**: `ouroboros/subsystems/rag/standards/vector.py` (and similar for other components)

**Description**: Write progress to file during build

**Changes**: (See specs.md Section 2.7 for full implementation)

**Acceptance Criteria**:
- [ ] `_write_progress_file()` method implemented
- [ ] Progress file format is JSON
- [ ] File written to `.praxis-os/.cache/rag/build-progress/`
- [ ] File name: `{index_name}.{component}.progress.json`
- [ ] Write is non-blocking (<5ms)
- [ ] Unit test verifies file format

**Time Estimate**: 30 minutes

**Dependencies**: None

---

### Task 5.2: Update build() Methods with Progress Callbacks

**File**: `ouroboros/subsystems/rag/standards/vector.py` (and similar)

**Description**: Call progress callback at key milestones

**Changes**: (See specs.md Section 2.7 for full implementation)

**Acceptance Criteria**:
- [ ] `build()` accepts `progress_callback` parameter
- [ ] Callback called at key milestones (every 10-20 chunks)
- [ ] Progress file written at each callback
- [ ] Callback signature: `(progress_percent: float, message: str) -> None`
- [ ] Integration test verifies callbacks

**Time Estimate**: 45 minutes

**Dependencies**: Task 5.1

---

### Task 5.3: Implement Progress File Reading in Build Status Checks

**File**: `ouroboros/subsystems/rag/standards/container.py`

**Description**: Read progress files in `_check_*_build_status()` methods

**Changes**:
```python
def _check_vector_build_status(self) -> BuildStatus:
    # ... existing checks ...
    
    # Check for progress file
    progress_file = self._get_progress_file_path("vector")
    if progress_file.exists():
        progress_data = json.loads(progress_file.read_text())
        # Ignore stale files (>1h old)
        if time.time() - progress_data["timestamp"] < 3600:
            return BuildStatus(
                state=IndexBuildState.BUILDING,
                progress_percent=progress_data["progress_percent"],
                message=progress_data["message"],
                details=progress_data
            )
```

**Acceptance Criteria**:
- [ ] Progress files read if they exist
- [ ] Stale files (>1h old) ignored
- [ ] Returns BUILDING state with progress
- [ ] Unit test verifies reading

**Time Estimate**: 30 minutes

**Dependencies**: Task 5.1, Task 2.3

---

### Task 5.4: Implement Progress File Cleanup

**File**: `ouroboros/subsystems/rag/standards/vector.py` (and similar)

**Description**: Delete progress files on build completion

**Changes**:
```python
def build(self, progress_callback=None):
    try:
        # ... build logic ...
        self._delete_progress_file()
    except Exception as e:
        self._delete_progress_file()
        raise
```

**Acceptance Criteria**:
- [ ] Progress files deleted on success
- [ ] Progress files deleted on failure
- [ ] Files deleted in finally block (guaranteed cleanup)
- [ ] Unit test verifies cleanup

**Time Estimate**: 20 minutes

**Dependencies**: Task 5.1, Task 5.2

---

### Task 5.5: Add Progress Reporting to All Components

**File**: Multiple files (vector.py, fts.py, metadata.py, graph.py)

**Description**: Add progress reporting to all component build methods

**Changes**: Similar to Task 5.2, but for all components

**Acceptance Criteria**:
- [ ] Vector component has progress reporting
- [ ] FTS component has progress reporting
- [ ] Metadata component has progress reporting
- [ ] Graph component has progress reporting
- [ ] Integration test verifies all components

**Time Estimate**: 60 minutes

**Dependencies**: Task 5.1, Task 5.2

---

**Phase 5 Validation Gate**:
- [ ] Progress files written during build
- [ ] Progress visible in build status checks
- [ ] Progress files cleaned up on completion
- [ ] No stale progress files remain
- [ ] Integration test verifies end-to-end progress reporting

---

## Phase 6: Config & Validation

**Purpose**: Implement configuration and validation logic  
**Duration**: 1-2 hours  
**Dependencies**: Phase 1

### Task 6.1: Integrate IndexBuildConfig into IndexesConfig

**File**: `ouroboros/config/schemas/indexes.py`

**Description**: Add `build` field to main config schema

**Changes**:
```python
class IndexesConfig(BaseModel):
    standards: StandardsIndexConfig
    code: CodeIndexConfig
    ast: ASTIndexConfig
    file_watcher: FileWatcherConfig
    build: IndexBuildConfig = Field(default_factory=IndexBuildConfig)  # NEW
```

**Acceptance Criteria**:
- [ ] `build` field added
- [ ] Default factory creates default config
- [ ] Config loads from YAML correctly
- [ ] Unit test verifies loading

**Time Estimate**: 15 minutes

**Dependencies**: Task 1.3

---

### Task 6.2: Implement Pre-flight Disk Space Check

**File**: `ouroboros/subsystems/rag/index_manager.py`

**Description**: Check disk space before building

**Changes**: (See specs.md Section 5.3 for full implementation)

**Acceptance Criteria**:
- [ ] `_check_disk_space()` method implemented
- [ ] Uses `shutil.disk_usage()`
- [ ] Compares to `config.build.disk_space_threshold_gb`
- [ ] Raises ActionableError if insufficient
- [ ] Unit test verifies check
- [ ] Chaos test: disk space exhaustion

**Time Estimate**: 30 minutes

**Dependencies**: Task 1.3, Task 6.1

---

### Task 6.3: Implement Failure Classification

**File**: `ouroboros/subsystems/rag/index_manager.py`

**Description**: Classify failures into categories (transient, config, resource, corruption)

**Changes**:
```python
def _classify_failure(self, error: Exception) -> str:
    """
    Classify failure type.
    
    Returns: "transient" | "config" | "resource" | "corruption"
    """
    error_str = str(error).lower()
    
    # Check transient keywords
    if any(kw in error_str for kw in self.config.build.transient_error_keywords):
        return "transient"
    
    # Check corruption
    if is_corruption_error(error):
        return "corruption"
    
    # Check resource errors
    if "disk" in error_str or "memory" in error_str or "space" in error_str:
        return "resource"
    
    # Default to config error
    return "config"
```

**Acceptance Criteria**:
- [ ] Method implemented
- [ ] All 4 categories handled
- [ ] Uses config-driven keywords
- [ ] Unit test covers all categories

**Time Estimate**: 30 minutes

**Dependencies**: Task 1.3, Task 6.1

---

### Task 6.4: Implement TTL-Based State Management

**File**: `ouroboros/subsystems/rag/index_manager.py`

**Description**: Set TTL on failure states based on classification

**Changes**:
```python
def _calculate_failure_ttl(self, failure_type: str) -> Optional[datetime]:
    """Calculate TTL expiry for failure state."""
    if failure_type == "config":
        # Config errors persist until restart
        return None
    elif failure_type == "transient":
        hours = self.config.build.transient_error_ttl_hours
        return datetime.now(timezone.utc) + timedelta(hours=hours)
    elif failure_type == "resource":
        hours = self.config.build.resource_error_ttl_hours
        return datetime.now(timezone.utc) + timedelta(hours=hours)
    else:
        # Corruption triggers auto-repair, no TTL needed
        return None
```

**Acceptance Criteria**:
- [ ] Method implemented
- [ ] Config errors: TTL=None
- [ ] Transient errors: TTL from config
- [ ] Resource errors: TTL from config
- [ ] Unit test verifies calculation

**Time Estimate**: 20 minutes

**Dependencies**: Task 6.3

---

### Task 6.5: Implement TTL Expiry Check in _check_build_readiness()

**File**: `ouroboros/subsystems/rag/index_manager.py`

**Description**: Auto-clear failure states when TTL expires

**Changes**:
```python
def _check_build_readiness(self, index_name: str) -> Optional[BuildStatus]:
    # ... existing cache check ...
    
    # Check if cached status is FAILED with expired TTL
    if cached_status.state == IndexBuildState.FAILED:
        if cached_status.ttl_expires_at:
            if datetime.now(timezone.utc) > cached_status.ttl_expires_at:
                # TTL expired, invalidate cache and retry
                self._invalidate_build_cache(index_name)
                # Fall through to rebuild
```

**Acceptance Criteria**:
- [ ] TTL expiry checked for FAILED states
- [ ] Cache invalidated on expiry
- [ ] Rebuild triggered automatically
- [ ] Integration test verifies expiry

**Time Estimate**: 20 minutes

**Dependencies**: Task 6.4

---

**Phase 6 Validation Gate**:
- [ ] Config validation warnings logged
- [ ] Pre-flight checks prevent known failures
- [ ] Failure classification works correctly
- [ ] TTL-based state management works
- [ ] Unit tests pass (>90% coverage)

---

## Phase 7: Telemetry (Optional)

**Purpose**: Implement optional telemetry for observability  
**Duration**: 1-2 hours  
**Dependencies**: Phase 4

### Task 7.1: Implement set_telemetry_callback()

**File**: `ouroboros/subsystems/rag/index_manager.py`

**Description**: Add method to register telemetry callback

**Changes**: (See specs.md Section 2.1 for full implementation)

**Acceptance Criteria**:
- [ ] Method implemented
- [ ] Stores callback in `_telemetry_callback` attribute
- [ ] Callback signature documented
- [ ] Unit test verifies registration

**Time Estimate**: 15 minutes

**Dependencies**: None

---

### Task 7.2: Implement _emit_telemetry()

**File**: `ouroboros/subsystems/rag/index_manager.py`

**Description**: Emit telemetry events safely

**Changes**: (See specs.md Section 5.2 for full implementation)

**Acceptance Criteria**:
- [ ] Method implemented
- [ ] Wraps callback in try/except
- [ ] Logs errors, doesn't propagate
- [ ] Only calls if telemetry enabled
- [ ] Unit test verifies error handling

**Time Estimate**: 15 minutes

**Dependencies**: Task 7.1

---

### Task 7.3: Add Telemetry Events to Key Operations

**File**: `ouroboros/subsystems/rag/index_manager.py`

**Description**: Emit events for build_started, corruption_detected, auto_repair_started, etc.

**Changes**: (See specs.md Section 2.1 for examples)

**Acceptance Criteria**:
- [ ] `build_started` event emitted
- [ ] `build_completed` event emitted
- [ ] `build_failed` event emitted
- [ ] `corruption_detected` event emitted
- [ ] `auto_repair_started` event emitted
- [ ] `auto_repair_completed` event emitted
- [ ] Integration test verifies events

**Time Estimate**: 45 minutes

**Dependencies**: Task 7.2

---

### Task 7.4: Update Server Initialization to Register Telemetry

**File**: `ouroboros/server.py`

**Description**: Register telemetry callback if enabled

**Changes**:
```python
if config.indexes.build.telemetry_enabled:
    def telemetry_callback(event_type: str, event_data: Dict[str, Any]):
        logger.info(f"📊 Telemetry: {event_type} - {event_data}")
    
    index_manager.set_telemetry_callback(telemetry_callback)
```

**Acceptance Criteria**:
- [ ] Callback registered if enabled
- [ ] Events logged to server logs
- [ ] Integration test verifies logging

**Time Estimate**: 15 minutes

**Dependencies**: Task 7.1, Task 7.3

---

**Phase 7 Validation Gate**:
- [ ] Telemetry callback registration works
- [ ] Events emitted correctly
- [ ] Telemetry errors don't crash system
- [ ] Telemetry disabled by default
- [ ] Integration test verifies end-to-end

---

## Phase 8: Testing + Validation

**Purpose**: Comprehensive testing and validation  
**Duration**: 4-6 hours  
**Dependencies**: All previous phases

### Task 8.1: Unit Tests - Data Models

**File**: `tests/ouroboros/subsystems/rag/test_build_status.py`

**Description**: Test BuildStatus model and IndexBuildState enum

**Test Cases**:
- [ ] `test_build_state_priority()`: Verify priority calculation
- [ ] `test_build_status_validation()`: Verify Pydantic constraints
- [ ] `test_build_status_immutable()`: Verify frozen model
- [ ] `test_build_status_no_extra_fields()`: Verify extra="forbid"

**Time Estimate**: 30 minutes

---

### Task 8.2: Unit Tests - Config Validation

**File**: `tests/ouroboros/config/test_index_build_config.py`

**Description**: Test IndexBuildConfig validation warnings

**Test Cases**:
- [ ] `test_low_disk_threshold_warning()`: Verify warning logged
- [ ] `test_high_retries_warning()`: Verify warning logged
- [ ] `test_disabled_retries_warning()`: Verify warning logged
- [ ] `test_short_ttl_warning()`: Verify warning logged
- [ ] `test_high_backoff_warning()`: Verify warning logged

**Time Estimate**: 45 minutes

---

### Task 8.3: Unit Tests - dynamic_build_status()

**File**: `tests/ouroboros/shared/test_component_helpers.py`

**Description**: Test fractal aggregation logic

**Test Cases**:
- [ ] `test_all_built()`: All components BUILT → BUILT
- [ ] `test_one_building()`: One BUILDING → BUILDING
- [ ] `test_one_failed()`: One FAILED → FAILED
- [ ] `test_progress_average()`: Verify average calculation
- [ ] `test_message_aggregation()`: Verify message concatenation

**Time Estimate**: 45 minutes

---

### Task 8.4: Unit Tests - Cache Logic

**File**: `tests/ouroboros/subsystems/rag/test_index_manager_cache.py`

**Description**: Test cache hit/miss, TTL, invalidation

**Test Cases**:
- [ ] `test_cache_hit()`: Verify cache hit returns cached status
- [ ] `test_cache_miss()`: Verify cache miss calls index.build_status()
- [ ] `test_cache_ttl_expiry()`: Verify TTL expiry invalidates cache
- [ ] `test_dynamic_ttl_calculation()`: Verify TTL based on progress
- [ ] `test_cache_invalidation()`: Verify atomic invalidation

**Time Estimate**: 60 minutes

---

### Task 8.5: Integration Tests - Fractal Pattern

**File**: `tests/ouroboros/subsystems/rag/test_fractal_build_status.py`

**Description**: Test end-to-end fractal aggregation

**Test Cases**:
- [ ] `test_standards_index_aggregation()`: Verify StandardsIndex aggregates components
- [ ] `test_code_index_aggregation()`: Verify CodeIndex aggregates components
- [ ] `test_index_manager_aggregation()`: Verify IndexManager aggregates indexes
- [ ] `test_partial_build()`: Verify progress during partial build

**Time Estimate**: 60 minutes

---

### Task 8.6: Integration Tests - Query Routing

**File**: `tests/ouroboros/subsystems/rag/test_route_action_build_status.py`

**Description**: Test route_action() with build status checking

**Test Cases**:
- [ ] `test_query_built_index()`: Query executes normally
- [ ] `test_query_building_index()`: Returns "building" response
- [ ] `test_query_failed_index()`: Returns "failed" response
- [ ] `test_query_not_built_index()`: Returns "not_built" response

**Time Estimate**: 60 minutes

---

### Task 8.7: Integration Tests - Auto-Repair

**File**: `tests/ouroboros/subsystems/rag/test_auto_repair.py`

**Description**: Test corruption detection and auto-repair

**Test Cases**:
- [ ] `test_corruption_detection()`: Verify corruption detected
- [ ] `test_auto_repair_triggered()`: Verify background rebuild starts
- [ ] `test_subsequent_queries_building()`: Verify queries return "building"
- [ ] `test_eventual_consistency()`: Verify rebuild completes and index becomes healthy

**Time Estimate**: 60 minutes

---

### Task 8.8: Chaos Test - Mid-Build Corruption

**File**: `tests/ouroboros/subsystems/rag/test_chaos_mid_build_corruption.py`

**Description**: Corrupt index during active build

**Test Scenario**:
1. Start index build
2. Corrupt index files mid-build (delete manifest, corrupt DB)
3. Verify build detects corruption
4. Verify auto-repair triggers
5. Verify eventual recovery

**Acceptance Criteria**:
- [ ] Build detects corruption
- [ ] Auto-repair triggered
- [ ] Rebuild completes successfully
- [ ] No data loss or crashes

**Time Estimate**: 45 minutes

---

### Task 8.9: Chaos Test - Concurrent Rebuild Requests

**File**: `tests/ouroboros/subsystems/rag/test_chaos_concurrent_rebuilds.py`

**Description**: Multiple corruption events simultaneously

**Test Scenario**:
1. Trigger 10 concurrent corruption events
2. Verify only one rebuild starts
3. Verify no race conditions
4. Verify eventual consistency

**Acceptance Criteria**:
- [ ] Only one rebuild thread created
- [ ] No deadlocks or race conditions
- [ ] All queries eventually succeed

**Time Estimate**: 45 minutes

---

### Task 8.10: Chaos Test - Corruption Under Query Load

**File**: `tests/ouroboros/subsystems/rag/test_chaos_corruption_under_load.py`

**Description**: Corruption during 100 concurrent queries

**Test Scenario**:
1. Start 100 concurrent queries
2. Corrupt index mid-query
3. Verify graceful degradation
4. Verify no crashes

**Acceptance Criteria**:
- [ ] Queries return "building" status (not crash)
- [ ] Auto-repair completes
- [ ] System recovers

**Time Estimate**: 45 minutes

---

### Task 8.11: Chaos Test - Disk Space Exhaustion

**File**: `tests/ouroboros/subsystems/rag/test_chaos_disk_space.py`

**Description**: Disk fills mid-build

**Test Scenario**:
1. Start index build
2. Fill disk mid-build (mock disk usage)
3. Verify pre-flight check catches it
4. Verify clear error message

**Acceptance Criteria**:
- [ ] Pre-flight check detects low space
- [ ] Build fails fast with ActionableError
- [ ] Error includes remediation steps

**Time Estimate**: 30 minutes

---

### Task 8.12: Chaos Test - Config Validation

**File**: `tests/ouroboros/config/test_chaos_config_validation.py`

**Description**: Unsafe config overrides trigger warnings

**Test Scenario**:
1. Load config with unsafe overrides
2. Verify warnings logged
3. Verify system still works (warnings only)

**Acceptance Criteria**:
- [ ] All 5 warning scenarios logged
- [ ] System doesn't crash
- [ ] Warnings include recommended values

**Time Estimate**: 30 minutes

---

### Task 8.13: Performance Benchmarks

**File**: `tests/ouroboros/subsystems/rag/test_performance_build_status.py`

**Description**: Measure performance impact

**Benchmarks**:
- [ ] Query latency (P50, P95, P99) before/after
- [ ] Cache hit rate measurement
- [ ] Build time overhead measurement
- [ ] Memory usage measurement

**Acceptance Criteria**:
- [ ] P99 query latency increase <5ms
- [ ] Cache hit rate >99%
- [ ] Build time overhead <5%
- [ ] Memory overhead <100KB

**Time Estimate**: 60 minutes

---

**Phase 8 Validation Gate**:
- [ ] Unit test coverage >90%
- [ ] Integration test coverage >80%
- [ ] All 5 chaos tests pass
- [ ] Performance benchmarks meet targets
- [ ] No regressions in existing tests
- [ ] MyPy type checking passes
- [ ] Ruff linting passes

---

## Summary

**Total Tasks**: 38  
**Total Phases**: 8  
**Estimated Time**: 18-28 hours

**Critical Path**:
1. Phase 0 (Performance Foundation) → Phase 1 (Foundational Types)
2. Phase 1 → Phase 2 (Fractal Pattern)
3. Phase 2 → Phase 3 (IndexManager Integration)
4. Phase 3 → Phase 4 (Corruption Handling)
5. Phase 2 → Phase 5 (Progress Reporting)
6. Phase 1 → Phase 6 (Config & Validation)
7. Phase 4 → Phase 7 (Telemetry, optional)
8. All phases → Phase 8 (Testing)

**Parallel Work Opportunities**:
- Phase 5 (Progress Reporting) can be done in parallel with Phase 3-4
- Phase 6 (Config & Validation) can be done in parallel with Phase 2-3
- Phase 7 (Telemetry) is optional and can be deferred

---

## Approval

**Task Breakdown Author**: Claude (AI Assistant)  
**Date**: 2025-11-14  
**Status**: Pending Review

**Reviewers**:
- [ ] Technical Lead
- [ ] Implementation Team

**Approval Criteria**:
- [ ] All tasks are specific and actionable
- [ ] Acceptance criteria are testable
- [ ] Dependencies are correct
- [ ] Time estimates are realistic
- [ ] Validation gates are comprehensive

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-14  
**Next Review**: After Phase 4 (Implementation Guidance)

