# Technical Specifications: Resilient Index Building

**Project**: prAxIs OS - RAG Subsystem Enhancement  
**Feature**: Resilient Index Building with Fractal Build Status  
**Date**: 2025-11-14  
**Status**: Technical Design  
**Version**: 1.0

---

## 1. Architecture Overview

### 1.1 System Context

```
┌─────────────────────────────────────────────────────────────┐
│                     MCP Server (Ouroboros)                   │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              IndexManager (Orchestrator)                │ │
│  │  • Route queries to indexes                             │ │
│  │  • Check build status before execution                  │ │
│  │  • Inject corruption handlers                           │ │
│  │  • Manage build state cache                             │ │
│  │  • Coordinate background rebuilds                       │ │
│  └─────────────┬──────────────────────────────────────────┘ │
│                │                                              │
│       ┌────────┴────────┬──────────────┬──────────────┐     │
│       │                 │              │              │     │
│  ┌────▼─────┐     ┌────▼─────┐  ┌────▼─────┐  ┌────▼─────┐│
│  │Standards │     │   Code   │  │   AST    │  │  Future  ││
│  │  Index   │     │  Index   │  │  Index   │  │  Indexes ││
│  └────┬─────┘     └────┬─────┘  └────┬─────┘  └──────────┘│
│       │                │              │                      │
│  ┌────▼────────────────▼──────────────▼─────┐              │
│  │        Component Layer (Fractal)          │              │
│  │  • Vector (LanceDB)                       │              │
│  │  • FTS (DuckDB)                           │              │
│  │  • Metadata (DuckDB)                      │              │
│  │  • Graph (DuckDB)                         │              │
│  └───────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────┘
```

**Key Architectural Principles**:
1. **Fractal Pattern**: Build status mirrors health check architecture (3-level hierarchy)
2. **Callback Injection**: Corruption handlers injected to avoid circular dependencies
3. **Cache-First**: Build status cached with dynamic TTL (2-60s)
4. **Auto-Repair**: Corruption triggers background rebuild automatically
5. **Graceful Degradation**: Queries return "building" status instead of failing

**Requirements Traceability**: FR-001 to FR-006 (Fractal Build Status Pattern)

---

### 1.2 Fractal Build Status Hierarchy

```
Level 1: IndexManager (Orchestrator)
├─ route_action() checks build status before query execution
├─ Aggregates status from all indexes
└─ Returns: "building" | "failed" | executes query

Level 2: Index (StandardsIndex, CodeIndex, ASTIndex)
├─ build_status() aggregates component status
├─ Uses dynamic_build_status(self.components)
└─ Returns: BuildStatus (state, progress, message)

Level 3: Component (Vector, FTS, Metadata, Graph)
├─ _check_vector_build_status()
├─ _check_fts_build_status()
├─ _check_metadata_build_status()
├─ _check_graph_build_status()
└─ Returns: BuildStatus (lightweight checks)
```

**Delegation Model**:
- IndexManager → Indexes → Components
- Each level aggregates status from below
- Progress is averaged (e.g., 3 components at 50%, 75%, 100% → 75% overall)
- State priority: FAILED > BUILDING > QUEUED > NOT_BUILT > BUILT

**Requirements Traceability**: FR-004, FR-005, FR-006

---

### 1.3 Data Flow: Query Execution with Build Status

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Query arrives at IndexManager.route_action()             │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Check build state cache (with lock)                      │
│    • Cache hit (99%+): Return cached status                 │
│    • Cache miss: Call index.build_status()                  │
└───────────────────────────┬─────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
┌───────────────────────┐   ┌───────────────────────┐
│ 3a. Status = BUILT    │   │ 3b. Status = BUILDING │
│     Execute query     │   │     Return "building" │
│     Return results    │   │     with progress     │
└───────────────────────┘   └───────────────────────┘
                │                       │
                ▼                       ▼
┌───────────────────────┐   ┌───────────────────────┐
│ 3c. Status = FAILED   │   │ 3d. Corruption Error  │
│     Return "failed"   │   │     Invalidate cache  │
│     with remediation  │   │     Start rebuild     │
│                       │   │     Return error      │
└───────────────────────┘   └───────────────────────┘
```

**Requirements Traceability**: FR-006, FR-009, FR-016 to FR-020

---

### 1.4 Auto-Repair Flow: Corruption Detection → Recovery

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Corruption detected in search() / build() / update()     │
│    • DuckDB: "database disk image is malformed"             │
│    • LanceDB: "invalid manifest"                            │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Index calls corruption_handler callback                  │
│    • Callback injected by IndexManager                      │
│    • No circular dependency (callback pattern)              │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. IndexManager._handle_corruption()                        │
│    • Acquire lock (atomic operation)                        │
│    • Invalidate cache for this index                        │
│    • Set state = BUILDING (progress = 0%)                   │
│    • Emit telemetry (if enabled)                            │
│    • Release lock                                            │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Start background rebuild (daemon thread)                 │
│    • _rebuild_index_background(index_name)                  │
│    • Non-blocking (main thread continues)                   │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Raise ActionableError to original caller                 │
│    • "Auto-repair in progress (background rebuild started)" │
│    • "Retry query in 30-60s"                                │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. Subsequent queries return "building" status              │
│    • route_action() checks cache → BUILDING                 │
│    • Returns progress updates (not error)                   │
│    • Eventual consistency achieved                          │
└─────────────────────────────────────────────────────────────┘
```

**Requirements Traceability**: FR-007 to FR-011

---

## 2. Component Specifications

### 2.1 IndexManager (Orchestrator)

**File**: `ouroboros/subsystems/rag/index_manager.py`

**Responsibilities**:
1. Route queries to appropriate indexes
2. Check build status before query execution
3. Inject corruption handlers into indexes
4. Manage build state cache (thread-safe)
5. Coordinate background rebuilds
6. Emit telemetry events (optional)

**New Attributes**:
```python
class IndexManager:
    _build_state_cache: Dict[str, BuildStatus]
    _build_state_cache_time: Dict[str, float]
    _build_state_cache_lock: threading.RLock
    _build_state_cache_ttl: float = 60.0  # BUILT state
    _building_state_cache_ttl: float = 5.0  # BUILDING state (dynamic)
    _indexes_lock: threading.RLock  # Protect _indexes dict iteration
    _telemetry_callback: Optional[Callable[[str, Dict[str, Any]], None]]
```

**New Methods**:

**`route_action(action: str, query: str, ...) -> Dict[str, Any]`**
- Check build readiness via `_check_build_readiness()`
- If BUILDING: return "building" response via `_format_building_response()`
- If FAILED: return "failed" response via `_format_failed_response()`
- If BUILT: execute query normally
- Catch corruption errors, trigger auto-repair
- Attach build metadata via `_attach_build_metadata()`

**`_check_build_readiness(index_name: str) -> Optional[BuildStatus]`**
- Check cache first (with lock)
- If cache miss or expired: call `index.build_status()`
- Update cache with dynamic TTL
- Return status if not BUILT

**`_format_building_response(status: BuildStatus, action: str) -> Dict`**
- Format "building" response with progress
- Include retry suggestion (30-60s)
- Include estimated time remaining

**`_format_failed_response(status: BuildStatus, action: str) -> Dict`**
- Format "failed" response with error details
- Include remediation steps
- Include TTL expiry time

**`_attach_build_metadata(response: Dict, index_name: str) -> Dict`**
- Attach build status metadata to successful queries
- Include cache hit/miss info
- Include build timestamp

**`_get_required_indexes_for_action(action: str) -> List[str]`**
- Map action to required indexes
- e.g., "search_standards" → ["standards"]
- e.g., "find_callers" → ["code"]

**`set_corruption_handler(index: BaseIndex)`**
- Inject corruption handler callback into index
- Handler: `lambda error, op: self._handle_corruption(index.name, error, op)`

**`_handle_corruption(index_name: str, error: Exception, operation: str)`**
- Log corruption event
- Emit telemetry (if enabled)
- Invalidate cache atomically (with lock)
- Set state = BUILDING
- Start background rebuild via `_rebuild_index_background()`
- Raise ActionableError

**`_rebuild_index_background(index_name: str)`**
- Check if rebuild already in progress
- Start daemon thread: `threading.Thread(target=self._rebuild_index, daemon=True)`
- Thread calls `index.build()` with progress callback

**`set_telemetry_callback(callback: Callable)`**
- Set telemetry callback for event emission
- Callback signature: `(event_type: str, event_data: Dict[str, Any]) -> None`

**`_emit_telemetry(event_type: str, event_data: Dict[str, Any])`**
- Call telemetry callback if set
- Catch and log errors (don't propagate)

**Requirements Traceability**: FR-006, FR-008, FR-009, FR-010, FR-012 to FR-015, FR-029 to FR-031

---

### 2.2 BaseIndex (Abstract Base Class)

**File**: `ouroboros/subsystems/rag/base.py`

**New Abstract Method**:
```python
@abstractmethod
def build_status(self) -> BuildStatus:
    """
    Get current build status of this index.
    
    Returns fractal aggregation of component build statuses.
    Must be implemented by all index subclasses.
    
    Returns:
        BuildStatus with state, progress, message, details
    """
    pass
```

**New Method**:
```python
def set_corruption_handler(
    self, 
    handler: Callable[[Exception, str], None]
) -> None:
    """
    Inject corruption handler callback from IndexManager.
    
    Args:
        handler: Callback to invoke on corruption detection
                 Signature: (error: Exception, operation: str) -> None
    """
    self._corruption_handler = handler
```

**Corruption Handling Pattern**:
```python
# In search(), build(), update() methods:
try:
    # ... existing logic ...
except Exception as e:
    if is_corruption_error(e):
        if self._corruption_handler:
            self._corruption_handler(e, "search")  # or "build", "update"
        raise ActionableError(...) from e
    raise
```

**Requirements Traceability**: FR-001, FR-007, FR-008

---

### 2.3 StandardsIndex (Concrete Implementation)

**File**: `ouroboros/subsystems/rag/standards/container.py`

**Updated Components Registration**:
```python
self.components: Dict[str, ComponentDescriptor] = {
    "vector": ComponentDescriptor(
        name="vector",
        health_check=self._check_vector_health,
        build_status_check=self._check_vector_build_status,  # NEW
        description="LanceDB vector index"
    ),
    "metadata": ComponentDescriptor(
        name="metadata",
        health_check=self._check_metadata_health,
        build_status_check=self._check_metadata_build_status,  # NEW
        description="DuckDB metadata index"
    ),
}

# Conditionally add FTS if enabled
if self.config.fts.enabled:
    self.components["fts"] = ComponentDescriptor(
        name="fts",
        health_check=self._check_fts_health,
        build_status_check=self._check_fts_build_status,  # NEW
        description="DuckDB full-text search"
    )
```

**New Method: `build_status()`**
```python
def build_status(self) -> BuildStatus:
    """
    Aggregate build status from all components (fractal pattern).
    
    Returns:
        BuildStatus with aggregated state and progress
    """
    return dynamic_build_status(self.components)
```

**New Component Build Status Checks**:

**`_check_vector_build_status() -> BuildStatus`**
- Check if LanceDB table exists
- Check if table has rows (>0)
- Check for progress file (if building)
- Return: BUILT | BUILDING | NOT_BUILT | FAILED

**`_check_fts_build_status() -> BuildStatus`**
- Check if DuckDB FTS table exists
- Check if table has rows (>0)
- Check for progress file (if building)
- Return: BUILT | BUILDING | NOT_BUILT | FAILED

**`_check_metadata_build_status() -> BuildStatus`**
- Check if DuckDB metadata table exists
- Check if table has rows (>0)
- Check for progress file (if building)
- Return: BUILT | BUILDING | NOT_BUILT | FAILED

**Corruption Handling in `search()`**:
```python
def search(self, query: str, n_results: int = 5) -> List[Dict]:
    try:
        # ... existing search logic ...
    except Exception as e:
        if is_corruption_error(e):
            if self._corruption_handler:
                self._corruption_handler(e, "search")
            raise ActionableError(
                what_failed="standards index search",
                why_failed=f"Index corrupted: {e}",
                how_to_fix=(
                    "Auto-repair in progress (background rebuild started).\n"
                    "Options:\n"
                    "1. Retry query in 30-60s (rebuild will complete)\n"
                    "2. Check disk space and file permissions\n"
                    "3. Restart server if issue persists"
                )
            ) from e
        raise
```

**Requirements Traceability**: FR-004, FR-005, FR-007, FR-009

---

### 2.4 CodeIndex (Concrete Implementation)

**File**: `ouroboros/subsystems/rag/code/container.py`

**Similar to StandardsIndex, with additional graph component**:

```python
self.components: Dict[str, ComponentDescriptor] = {
    "semantic": ComponentDescriptor(
        name="semantic",
        health_check=self._check_semantic_health,
        build_status_check=self._check_semantic_build_status,  # NEW
        description="CodeBERT semantic index"
    ),
}

# Conditionally add graph if enabled
if self.config.graph.enabled:
    self.components["graph"] = ComponentDescriptor(
        name="graph",
        health_check=self._check_graph_health,
        build_status_check=self._check_graph_build_status,  # NEW
        description="DuckDB call graph"
    )
```

**New Component Build Status Checks**:
- `_check_semantic_build_status()`: Check LanceDB semantic index
- `_check_graph_build_status()`: Check DuckDB graph tables (ast_nodes, call_graph)

**Requirements Traceability**: FR-004, FR-005, FR-007, FR-009

---

### 2.5 ComponentDescriptor (Enhanced)

**File**: `ouroboros/shared/component_helpers.py`

**Updated Schema**:
```python
@dataclass
class ComponentDescriptor:
    name: str
    health_check: Callable[[], HealthStatus]
    build_status_check: Callable[[], BuildStatus]  # NEW
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
```

**Requirements Traceability**: FR-004

---

### 2.6 dynamic_build_status() Helper

**File**: `ouroboros/shared/component_helpers.py`

**Function Signature**:
```python
def dynamic_build_status(
    components: Dict[str, ComponentDescriptor]
) -> BuildStatus:
    """
    Aggregate build status from multiple components (fractal pattern).
    
    Mirrors dynamic_health_check() architecture.
    
    Args:
        components: Dict of component descriptors with build_status_check
        
    Returns:
        BuildStatus with aggregated state and progress
        
    State Priority (worst-first):
        FAILED > BUILDING > QUEUED_TO_BUILD > NOT_BUILT > BUILT
        
    Progress Calculation:
        Average of all component progress percentages
    """
    pass
```

**Implementation Logic**:
1. Call `build_status_check()` for each component
2. Determine worst state (priority: FAILED > BUILDING > QUEUED > NOT_BUILT > BUILT)
3. Calculate average progress
4. Aggregate messages
5. Return BuildStatus

**Requirements Traceability**: FR-005

---

### 2.7 Progress Callback System

**File**: `ouroboros/subsystems/rag/standards/vector.py` (and similar for other components)

**Progress File Format**:
```json
{
  "state": "BUILDING",
  "progress_percent": 45.0,
  "message": "Embedding chunk 450/1000",
  "timestamp": "2025-11-14T12:34:56Z",
  "component": "vector"
}
```

**Progress File Location**:
- `.praxis-os/.cache/rag/build-progress/{index_name}.{component}.progress.json`

**Progress Callback in `build()` Method**:
```python
def build(
    self, 
    progress_callback: Optional[Callable[[float, str], None]] = None
) -> None:
    """
    Build vector index with progress reporting.
    
    Args:
        progress_callback: Optional callback for progress updates
                          Signature: (progress_percent: float, message: str) -> None
    """
    total_chunks = len(chunks)
    for i, chunk in enumerate(chunks):
        # ... embed and index chunk ...
        
        if progress_callback:
            progress = (i + 1) / total_chunks * 100
            message = f"Embedding chunk {i+1}/{total_chunks}"
            progress_callback(progress, message)
            
            # Also write to progress file
            self._write_progress_file(progress, message)
```

**Progress File Cleanup**:
- Delete on successful build completion
- Delete on build failure
- Ignore stale files (>1h old)

**Requirements Traceability**: FR-026 to FR-028

---

## 3. API Specifications

### 3.1 IndexManager.route_action()

**Signature**:
```python
def route_action(
    self,
    action: str,
    query: str,
    method: str = "hybrid",
    n_results: int = 5,
    max_depth: int = 10,
    to_symbol: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Route search query to appropriate index with build status checking.
    
    Args:
        action: Search action (search_standards, search_code, find_callers, etc.)
        query: Search query or symbol name
        method: Search method (hybrid, vector, fts)
        n_results: Number of results to return
        max_depth: Max traversal depth for graph queries
        to_symbol: Target symbol for find_call_paths
        filters: Optional metadata filters
        
    Returns:
        Dict with status, results, and metadata
        
    Response Formats:
        Success: {"status": "success", "results": [...], "metadata": {...}}
        Building: {"status": "building", "progress": 45.0, "message": "...", "retry_in": 30}
        Failed: {"status": "failed", "error": "...", "remediation": "...", "ttl_expires_at": "..."}
        
    Raises:
        ActionableError: If corruption detected (triggers auto-repair)
        ValueError: If invalid action or missing parameters
    """
```

**Build Status Check Flow**:
1. Determine required indexes via `_get_required_indexes_for_action(action)`
2. For each required index:
   - Call `_check_build_readiness(index_name)`
   - If status is not BUILT, return early with status response
3. If all indexes BUILT, execute query normally

**Requirements Traceability**: FR-006, FR-011

---

### 3.2 BaseIndex.build_status()

**Signature**:
```python
@abstractmethod
def build_status(self) -> BuildStatus:
    """
    Get current build status of this index (fractal aggregation).
    
    Returns:
        BuildStatus with state, progress, message, details
        
    Implementation Pattern:
        return dynamic_build_status(self.components)
    """
```

**Requirements Traceability**: FR-001, FR-005

---

### 3.3 Component Build Status Check

**Signature**:
```python
def _check_vector_build_status(self) -> BuildStatus:
    """
    Check build status of vector component (lightweight).
    
    Checks:
        1. Table exists (LanceDB)
        2. Table has rows (>0)
        3. Progress file exists (if building)
        
    Returns:
        BuildStatus with state, progress, message
        
    States:
        BUILT: Table exists and has rows
        BUILDING: Progress file exists
        NOT_BUILT: Table doesn't exist or empty
        FAILED: Error reading table or progress file
    """
```

**Requirements Traceability**: FR-004, FR-018

---

### 3.4 Corruption Handler Callback

**Signature**:
```python
def _handle_corruption(
    self,
    index_name: str,
    error: Exception,
    operation: str
) -> None:
    """
    Handle index corruption detection (auto-repair).
    
    Args:
        index_name: Name of corrupted index
        error: Exception that triggered corruption detection
        operation: Operation that detected corruption (search, build, update)
        
    Side Effects:
        1. Logs corruption event
        2. Emits telemetry (if enabled)
        3. Invalidates cache atomically
        4. Sets state = BUILDING
        5. Starts background rebuild thread
        6. Raises ActionableError to caller
    """
```

**Requirements Traceability**: FR-008, FR-009, FR-010

---

### 3.5 Telemetry Callback

**Signature**:
```python
def set_telemetry_callback(
    self,
    callback: Callable[[str, Dict[str, Any]], None]
) -> None:
    """
    Set telemetry callback for event emission.
    
    Args:
        callback: Function to call on telemetry events
                  Signature: (event_type: str, event_data: Dict[str, Any]) -> None
                  
    Event Types:
        - build_started
        - build_progress
        - build_completed
        - build_failed
        - corruption_detected
        - auto_repair_started
        - auto_repair_completed
    """
```

**Requirements Traceability**: FR-029, FR-030

---

## 4. Data Models

### 4.1 BuildStatus (Pydantic Model)

**File**: `ouroboros/subsystems/rag/base.py`

**Schema**:
```python
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime

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

class BuildStatus(BaseModel):
    """
    Build status model (mirrors HealthStatus).
    
    Used for fractal aggregation of component build statuses.
    """
    state: IndexBuildState = Field(
        description="Current build state"
    )
    message: str = Field(
        description="Human-readable status message"
    )
    progress_percent: float = Field(
        ge=0.0,
        le=100.0,
        description="Build progress (0-100)"
    )
    details: Dict[str, Any] = Field(
        default_factory=dict,
        description="Diagnostic details (component statuses, errors, etc.)"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if state=FAILED"
    )
    ttl_expires_at: Optional[datetime] = Field(
        default=None,
        description="TTL expiry for FAILED state"
    )
    
    class Config:
        frozen = True  # Immutable
        extra = "forbid"  # No extra fields
```

**Requirements Traceability**: FR-002, FR-003

---

### 4.2 IndexBuildConfig (Pydantic Model)

**File**: `ouroboros/config/schemas/indexes.py`

**Schema**:
```python
from pydantic import BaseModel, Field, model_validator
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class IndexBuildConfig(BaseModel):
    """
    Configuration for resilient index building.
    
    All thresholds and TTLs are configurable for flexibility.
    """
    disk_space_threshold_gb: float = Field(
        default=2.0,
        ge=0.1,
        description="Minimum free disk space required to build (GB)"
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Max retries for transient failures"
    )
    retry_backoff_base: float = Field(
        default=2.0,
        ge=1.0,
        le=10.0,
        description="Exponential backoff base (seconds)"
    )
    transient_error_keywords: List[str] = Field(
        default_factory=lambda: [
            "timeout",
            "connection",
            "network",
            "temporary",
            "unavailable",
            "model download",
        ],
        description="Keywords to identify transient errors"
    )
    config_error_ttl_hours: Optional[float] = Field(
        default=None,
        description="TTL for config errors (None = until restart)"
    )
    transient_error_ttl_hours: float = Field(
        default=24.0,
        ge=0.1,
        description="TTL for transient errors (hours)"
    )
    resource_error_ttl_hours: float = Field(
        default=1.0,
        ge=0.1,
        description="TTL for resource errors (hours)"
    )
    report_progress_per_component: bool = Field(
        default=True,
        description="Report progress at component level"
    )
    telemetry_enabled: bool = Field(
        default=False,
        description="Enable telemetry event emission"
    )
    
    @model_validator(mode="after")
    def validate_config(self) -> "IndexBuildConfig":
        """
        Validate config and log warnings for unsafe overrides.
        
        Warnings logged for:
            - Disk space threshold <1GB
            - Max retries >5 or =0
            - TTLs too short (<1h for transient)
            - Backoff base too high (>5.0)
        """
        # Warn if disk space threshold is too low
        if self.disk_space_threshold_gb < 1.0:
            logger.warning(
                "⚠️  Low disk_space_threshold_gb (%.1fGB). "
                "Recommended: 2GB+ to prevent mid-build failures. "
                "Current setting may cause frequent build failures.",
                self.disk_space_threshold_gb
            )
        
        # Warn if max_retries is too high
        if self.max_retries > 5:
            logger.warning(
                "⚠️  High max_retries (%d). "
                "May delay failure detection and mask persistent issues. "
                "Recommended: 3 retries for transient failures.",
                self.max_retries
            )
        
        # Warn if max_retries is disabled
        if self.max_retries == 0:
            logger.warning(
                "⚠️  Retries disabled (max_retries=0). "
                "Transient failures (network timeouts, model downloads) will fail immediately. "
                "Recommended: 3 retries."
            )
        
        # Warn if TTLs are too short
        if self.transient_error_ttl_hours < 1.0:
            logger.warning(
                "⚠️  Short transient_error_ttl_hours (%.1fh). "
                "May cause frequent rebuild attempts for persistent issues. "
                "Recommended: 24h to allow time for external issues to resolve.",
                self.transient_error_ttl_hours
            )
        
        # Warn if resource error TTL is too long
        if self.resource_error_ttl_hours > 24.0:
            logger.warning(
                "⚠️  Long resource_error_ttl_hours (%.1fh). "
                "Resource issues (disk space, memory) should be resolved quickly. "
                "Recommended: 1h for fast recovery.",
                self.resource_error_ttl_hours
            )
        
        # Warn if backoff base is too high
        if self.retry_backoff_base > 5.0:
            logger.warning(
                "⚠️  High retry_backoff_base (%.1f). "
                "Exponential backoff will be very aggressive (e.g., 5^3 = 125s wait). "
                "Recommended: 2.0 for reasonable retry intervals.",
                self.retry_backoff_base
            )
        
        return self
```

**Requirements Traceability**: FR-021, FR-022

---

### 4.3 ComponentDescriptor (Enhanced)

**File**: `ouroboros/shared/component_helpers.py`

**Schema**:
```python
from dataclasses import dataclass, field
from typing import Callable, Dict, Any

@dataclass
class ComponentDescriptor:
    """
    Descriptor for a system component with health and build status checks.
    
    Used for fractal aggregation of component statuses.
    """
    name: str
    health_check: Callable[[], HealthStatus]
    build_status_check: Callable[[], BuildStatus]  # NEW
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
```

**Requirements Traceability**: FR-004

---

## 5. Security Considerations

### 5.1 Thread Safety (SEC-001)

**Threat**: Race conditions in cache access and index dict iteration

**Mitigation**:
- Use `threading.RLock` for all cache operations
- Use `threading.RLock` for `_indexes` dict iteration
- Atomic cache invalidation + state update
- Reentrant locks allow nested calls

**Implementation**:
```python
with self._build_state_cache_lock:
    # Atomic operation
    self._build_state_cache.pop(index_name, None)
    self._build_state_cache_time.pop(index_name, None)
    self._build_state_cache[index_name] = BuildStatus(...)
```

**Requirements Traceability**: FR-012 to FR-014, NFR-006

---

### 5.2 Telemetry Safety (SEC-002)

**Threat**: Malicious telemetry callback crashes system

**Mitigation**:
- Wrap all telemetry calls in try/except
- Log errors, don't propagate
- Telemetry disabled by default
- No sensitive data in telemetry events

**Implementation**:
```python
def _emit_telemetry(self, event_type: str, event_data: Dict[str, Any]):
    if self._telemetry_callback:
        try:
            self._telemetry_callback(event_type, event_data)
        except Exception as e:
            logger.error("Telemetry callback failed: %s", e)
            # Don't propagate - telemetry is optional
```

**Requirements Traceability**: FR-015, FR-031

---

### 5.3 Disk Space Validation (SEC-003)

**Threat**: Index build fills disk, crashes system

**Mitigation**:
- Pre-flight disk space check (configurable threshold)
- Fail fast with clear error message
- Suggest remediation (free space, increase threshold)

**Implementation**:
```python
def _check_disk_space(self) -> None:
    free_gb = shutil.disk_usage(self.base_path).free / (1024**3)
    if free_gb < self.config.build.disk_space_threshold_gb:
        raise ActionableError(
            what_failed="Index build pre-flight check",
            why_failed=f"Insufficient disk space ({free_gb:.1f}GB free, {self.config.build.disk_space_threshold_gb:.1f}GB required)",
            how_to_fix=(
                "Options:\n"
                "1. Free up disk space\n"
                "2. Increase disk_space_threshold_gb in config (if safe)\n"
                "3. Move index to larger volume"
            )
        )
```

**Requirements Traceability**: FR-024

---

### 5.4 Progress File Isolation (SEC-004)

**Threat**: Progress file writes block main thread

**Mitigation**:
- Progress file writes are non-blocking
- Writes are <5ms (small JSON files)
- Stale files ignored (>1h old)
- Files cleaned up on completion

**Requirements Traceability**: FR-019, FR-027, FR-028, NFR-002

---

### 5.5 Corruption Handler Injection (SEC-005)

**Threat**: Circular dependencies between IndexManager and indexes

**Mitigation**:
- Use callback pattern (no back-references)
- Indexes don't import IndexManager
- Handler injected at initialization
- Handler is optional (graceful degradation)

**Implementation**:
```python
# In IndexManager.__init__():
for index in self._indexes.values():
    index.set_corruption_handler(
        lambda error, op: self._handle_corruption(index.name, error, op)
    )
```

**Requirements Traceability**: FR-008

---

## 6. Performance Strategies

### 6.1 Three-Tier Caching (PERF-001)

**Strategy**: Cache build status with dynamic TTL to minimize overhead

**Tier 1: In-Memory State Cache**
- Cache `BuildStatus` objects in memory
- TTL: 60s for BUILT, 2-10s for BUILDING (dynamic), 60s for FAILED
- Cache hit rate target: >99% for BUILT indexes
- Cache invalidated on: build completion, corruption detection, TTL expiry

**Tier 2: Lightweight Component Checks**
- Component checks don't load models or perform test searches
- Only verify: table exists + has rows
- Estimated cost: 15-70ms (vs 145-720ms for health checks)

**Tier 3: Progress Files**
- Progress files only exist during active builds
- Read on cache miss for BUILDING state
- Deleted on build completion
- <1KB JSON files, <5ms read time

**Performance Impact**:
- Cached BUILT: <2ms overhead (99.9% of queries)
- Cached BUILDING: <10ms overhead (dynamic TTL)
- Cache miss: <100ms overhead (rare)

**Requirements Traceability**: FR-016 to FR-020, NFR-001, NFR-003

---

### 6.2 Dynamic TTL Strategy (PERF-002)

**Strategy**: Adjust cache TTL based on build progress to balance freshness and performance

**TTL Calculation**:
```python
def _calculate_building_ttl(progress_percent: float) -> float:
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

**Rationale**:
- Early stage: Build just started, state may change quickly
- Mid stage: Steady progress, moderate freshness needed
- Late stage: Near completion, longer TTL acceptable

**Requirements Traceability**: FR-016, NFR-001

---

### 6.3 Lazy Progress Reporting (PERF-003)

**Strategy**: Only write progress files when config enables per-component reporting

**Configuration**:
```python
report_progress_per_component: bool = True  # Default
```

**Behavior**:
- If `True`: Write progress files for each component (detailed visibility)
- If `False`: Only report index-level progress (lower overhead)

**Trade-off**:
- Detailed progress: +1% build time, better observability
- Index-level only: Minimal overhead, less granular visibility

**Requirements Traceability**: FR-021, FR-027, NFR-002

---

### 6.4 Background Rebuild (PERF-004)

**Strategy**: Rebuild corrupted indexes in background thread to avoid blocking queries

**Implementation**:
- Daemon thread: Auto-terminates when main process exits
- Non-blocking: Original query raises error immediately
- Eventual consistency: Subsequent queries return "building" status
- Progress visible: Cache updated by background thread

**Benefits**:
- No query blocking (main thread continues)
- Graceful degradation (queries return status, not crash)
- Auto-recovery (system converges to healthy state)

**Requirements Traceability**: FR-009, FR-011, NFR-008

---

### 6.5 Atomic Cache Operations (PERF-005)

**Strategy**: Minimize lock contention by keeping critical sections small

**Pattern**:
```python
# BAD: Lock held for entire rebuild
with self._build_state_cache_lock:
    self._build_state_cache.pop(index_name, None)
    self._rebuild_index(index_name)  # SLOW!
    self._build_state_cache[index_name] = BuildStatus(...)

# GOOD: Lock only for cache updates
with self._build_state_cache_lock:
    self._build_state_cache.pop(index_name, None)
    self._build_state_cache[index_name] = BuildStatus(state=BUILDING, ...)

# Rebuild happens outside lock (background thread)
self._rebuild_index_background(index_name)
```

**Requirements Traceability**: FR-010, FR-014, NFR-004

---

## 7. Implementation Notes

### 7.1 Phased Implementation

**Phase 0: Performance Foundation (2-3 hours)**
- Implement build state cache with dynamic TTL
- Implement cache invalidation logic
- Add thread safety (RLock)
- **Rationale**: Cache must exist before adding build status checks

**Phase 1: Foundational Types (1-2 hours)**
- Define `IndexBuildState` enum
- Define `BuildStatus` Pydantic model
- Define `IndexBuildConfig` schema with validation
- Add `build_status_check` to `ComponentDescriptor`

**Phase 2: Fractal Pattern (3-4 hours)**
- Implement `dynamic_build_status()` helper
- Add abstract `build_status()` to `BaseIndex`
- Implement `build_status()` in `StandardsIndex`, `CodeIndex`
- Implement component build status checks

**Phase 3: IndexManager Integration (2-3 hours)**
- Implement `route_action()` build status checking
- Implement helper methods (`_check_build_readiness`, etc.)
- Implement `_get_required_indexes_for_action()`

**Phase 4: Corruption Handling (2-3 hours)**
- Implement callback injection pattern
- Implement `_handle_corruption()` in `IndexManager`
- Add corruption detection to `search()`, `build()`, `update()` in indexes
- Implement `_rebuild_index_background()`

**Phase 5: Progress Reporting (2-3 hours)**
- Implement progress callback in `build()` methods
- Implement progress file writing
- Implement progress file reading in build status checks
- Implement progress file cleanup

**Phase 6: Config & Validation (1-2 hours)**
- Implement `IndexBuildConfig.model_post_init()` validation
- Implement pre-flight disk space check
- Implement failure classification logic
- Implement TTL-based state management

**Phase 7: Telemetry (Optional, 1-2 hours)**
- Implement `set_telemetry_callback()`
- Implement `_emit_telemetry()`
- Add telemetry events to key operations

**Phase 8: Testing + Validation (4-6 hours)**
- Unit tests for all new components
- Integration tests for fractal pattern
- Chaos tests (5 scenarios)
- Performance benchmarks

**Total Estimated Time**: 18-28 hours

---

### 7.2 Testing Strategy

**Unit Tests** (90%+ coverage):
- `BuildStatus` model validation
- `IndexBuildState` priority calculation
- `dynamic_build_status()` aggregation logic
- Cache TTL calculation
- Config validation warnings
- Component build status checks

**Integration Tests** (80%+ coverage):
- End-to-end query flow with build status checking
- Corruption detection → auto-repair → recovery
- Background rebuild coordination
- Progress reporting and cleanup
- Cache invalidation and TTL expiry

**Chaos Tests** (5 scenarios from ChatGPT-5 feedback):
1. **Mid-Build Corruption**: Corrupt index during active build
2. **Concurrent Rebuild Requests**: Multiple corruption events simultaneously
3. **Corruption Under Query Load**: Corruption during 100 concurrent queries
4. **Disk Space Exhaustion**: Disk fills mid-build
5. **Config Validation**: Unsafe config overrides trigger warnings

**Performance Benchmarks**:
- Query latency (P50, P95, P99) before/after implementation
- Cache hit rate measurement
- Build time overhead measurement
- Memory usage measurement

**Requirements Traceability**: NFR-013

---

### 7.3 Backward Compatibility

**Guaranteed**:
- Existing indexes continue to work
- Existing health checks continue to work
- Existing search APIs unchanged
- No breaking changes to public APIs

**Migration Path**:
- New `build_status()` method added to `BaseIndex` (abstract)
- All existing index implementations must implement `build_status()`
- Default implementation: return `BuildStatus(state=BUILT, progress=100.0, message="Index healthy")`

**Requirements Traceability**: NFR-015

---

## 8. Traceability Matrix

| Requirement | Component | Method/Attribute | Test Coverage |
|-------------|-----------|------------------|---------------|
| FR-001 | BaseIndex | `build_status()` | Unit + Integration |
| FR-002 | base.py | `BuildStatus` model | Unit |
| FR-003 | base.py | `IndexBuildState` enum | Unit |
| FR-004 | ComponentDescriptor | `build_status_check` | Unit + Integration |
| FR-005 | component_helpers.py | `dynamic_build_status()` | Unit + Integration |
| FR-006 | IndexManager | `route_action()` | Integration |
| FR-007 | StandardsIndex, CodeIndex | `search()` corruption detection | Integration + Chaos |
| FR-008 | BaseIndex | `set_corruption_handler()` | Unit + Integration |
| FR-009 | IndexManager | `_handle_corruption()` | Integration + Chaos |
| FR-010 | IndexManager | Cache invalidation + rebuild | Integration + Chaos |
| FR-011 | IndexManager | `route_action()` graceful responses | Integration |
| FR-012 to FR-015 | IndexManager | Thread safety (RLock) | Integration + Chaos |
| FR-016 to FR-020 | IndexManager | Caching strategy | Unit + Performance |
| FR-021 | indexes.py | `IndexBuildConfig` | Unit |
| FR-022 | IndexBuildConfig | `model_post_init()` | Unit |
| FR-023 | IndexManager | Failure classification | Unit + Integration |
| FR-024 | IndexManager | Pre-flight checks | Unit + Chaos |
| FR-025 | IndexManager | TTL-based state management | Integration |
| FR-026 to FR-028 | Vector, FTS, etc. | Progress reporting | Integration |
| FR-029 to FR-031 | IndexManager | Telemetry | Unit + Integration |

---

## 9. Approval

**Technical Design Author**: Claude (AI Assistant)  
**Date**: 2025-11-14  
**Status**: Pending Review

**Reviewers**:
- [ ] Technical Lead
- [ ] Architecture Review Board
- [ ] Security Review

**Approval Criteria**:
- [ ] Architecture aligns with requirements
- [ ] All components clearly defined
- [ ] APIs are well-specified
- [ ] Data models are complete
- [ ] Security considerations addressed
- [ ] Performance strategies defined
- [ ] Implementation plan is realistic
- [ ] Traceability matrix complete

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-14  
**Next Review**: After Phase 3 (Task Breakdown)

