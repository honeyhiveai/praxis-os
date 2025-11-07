# RAG Index Submodule Pattern

**Status:** Proposed  
**Date:** 2025-11-05  
**Author:** System Architecture  
**Parent Spec:** 2025-11-03-ouroboros-mcp-server

---

## Executive Summary

Refactor RAG indexes to use a **submodule-per-index** pattern where each index (standards, code, project_docs, dependency_docs) is a self-contained Python submodule. This provides:

1. **Uniform Interface**: IndexManager treats all indexes identically
2. **Internal Freedom**: Each submodule optimized for its use case (simple vs complex)
3. **Loose Coupling**: Submodule internals hidden behind interface boundary
4. **Independent Evolution**: Add/modify indexes without touching IndexManager

---

## Motivation

### Current Problem

```
subsystems/rag/
├── standards_index.py    # All-in-one (simple)
├── code_index.py         # Split 1/3 (semantic only)
├── ast_index.py          # Split 2/3 (structural)
└── graph_index.py        # Split 3/3 (call graph)
```

**Issues:**
- **Inconsistent abstraction**: Standards is all-in-one, Code is split across 3 files
- **IndexManager knows too much**: Manages 4 "indexes" when conceptually it's 2 (standards + code)
- **No room to grow**: Where would `project_docs/` or `dependency_docs/` go?
- **Coupling**: IndexManager directly imports `ast_index.py`, `graph_index.py`
- **Wrong database**: Current code uses SQLite for AST, but spec calls for DuckDB only (LanceDB + DuckDB, NOT 3 databases)

### Proposed Solution

```
subsystems/rag/
├── base.py                        # Interface contract
├── index_manager.py               # Orchestrator
├── watcher.py                     # File watching
├── standards/                     # Submodule (simple today)
│   ├── __init__.py                # from .container import StandardsIndex
│   ├── container.py               # StandardsIndex (interface with IndexManager)
│   └── semantic.py                # SemanticIndex (implementation)
├── code/                          # Submodule (complex)
│   ├── __init__.py                # from .container import CodeIndex
│   ├── container.py               # CodeIndex (interface with IndexManager)
│   ├── semantic.py                # SemanticIndex (LanceDB: vector+FTS+scalar)
│   └── graph.py                   # GraphIndex (DuckDB: AST + call graph)
├── project_docs/                  # Future: Local docs
│   ├── __init__.py                # from .container import ProjectDocsIndex
│   ├── container.py               # ProjectDocsIndex (interface)
│   └── semantic.py                # Implementation
└── dependency_docs/               # Future: External docs
    ├── __init__.py                # from .container import DependencyDocsIndex
    ├── container.py               # DependencyDocsIndex (interface)
    ├── semantic.py                # Implementation
    └── versioning.py              # Version management
```

**Key Pattern: Every submodule has `container.py`**
- **`__init__.py`**: Pure exports (no implementation)
- **`container.py`**: Interface with IndexManager (uniform entry point)
- **Implementation files**: Internal details (semantic.py, graph.py, etc.)

**Database Architecture (2 databases total):**
- **LanceDB**: Vector + FTS + Scalar indexes (standards & code semantic)
  - Standards: Scalar indexes on domain, phase, section
  - Code: Scalar indexes on language, file_path, symbol_type
- **DuckDB**: AST symbols + Call graph + Recursive CTEs (code structural & traversal)

---

## Architecture

### Principle: Submodule = Architectural Boundary

```
┌─────────────────────────────────────────────────────────┐
│ IndexManager (Orchestrator)                             │
│ - Owns lifecycle of ALL indexes                         │
│ - Delegates to submodules via BaseIndex interface       │
└─────────────────────────────────────────────────────────┘
                          │
                          ↓ depends on (abstraction)
┌─────────────────────────────────────────────────────────┐
│ BaseIndex (Interface)                                    │
│ - build(source_paths, force)                            │
│ - search(query, n_results, filters)                     │
│ - update(changed_files)                                 │
│ - health_check() → HealthStatus                         │
│ - get_stats() → Dict[str, Any]                          │
└─────────────────────────────────────────────────────────┘
                          ↑ implemented by (details)
        ┌─────────────────┼─────────────────┬─────────────┐
        │                 │                 │             │
┌───────────────┐ ┌───────────────┐ ┌──────────────┐ ┌──────────────┐
│ standards/    │ │ code/         │ │ project_docs/│ │ dependency_  │
│               │ │               │ │              │ │ docs/        │
│ Standards     │ │ CodeIndex     │ │ ProjectDocs  │ │ Dependency   │
│ Index         │ │ (container)   │ │ Index        │ │ DocsIndex    │
└───────────────┘ └───────────────┘ └──────────────┘ └──────────────┘
                       │
                       ├─ semantic.py   (LanceDB: vector+FTS+scalar)
                       └─ graph.py      (DuckDB: AST+call graph)
```

### Key Principles

1. **Uniform Entry Point: Every submodule has `container.py`**
   - ✅ Always look in `container.py` for the main class
   - ✅ Predictable pattern for AI/human discovery
   - ✅ No special cases or guessing

2. **IndexManager couples to submodule interface, never internals**
   - ✅ `from ouroboros.subsystems.rag.code import CodeIndex` (imports from `__init__.py`)
   - ✅ `code/container.py` defines `CodeIndex` (interface layer)
   - ❌ `from ouroboros.subsystems.rag.code.semantic import SemanticIndex` (bypasses interface)

3. **Each submodule free to organize internally**
   - Simple: `container.py` delegates to single `semantic.py` (LanceDB)
   - Complex: `container.py` orchestrates 2 files (semantic.py → LanceDB, graph.py → DuckDB)
   - Pattern is consistent regardless of complexity

4. **BaseIndex = contract, submodule = implementation**
   - High-level IndexManager depends on low-level submodules via abstraction (Dependency Inversion)
   - `container.py` implements BaseIndex interface, delegates to internal implementations

---

## Interface Design

### BaseIndex Contract (Abstract Interface)

```python
# subsystems/rag/base.py

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class SearchResult(BaseModel):
    """Unified search result across all index types."""
    content: str
    file_path: str
    relevance_score: float  # 0.0-1.0
    content_type: str       # "standard", "code", "project_doc", etc.
    metadata: Dict[str, Any]
    chunk_id: Optional[str] = None
    line_range: Optional[tuple[int, int]] = None
    section: Optional[str] = None

class HealthStatus(BaseModel):
    """Health status for an index."""
    healthy: bool
    message: str
    details: Dict[str, Any] = {}
    last_updated: Optional[str] = None

class BaseIndex(ABC):
    """Abstract interface all index submodules must implement."""
    
    @abstractmethod
    def build(self, source_paths: List[Path], force: bool = False) -> None:
        """Build index from source paths.
        
        Args:
            source_paths: Paths to index (directories or files)
            force: If True, rebuild even if exists
            
        Raises:
            ActionableError: If build fails
        """
        pass
    
    @abstractmethod
    def search(
        self,
        query: str,
        n_results: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search the index.
        
        Args:
            query: Natural language query
            n_results: Max results
            filters: Optional metadata filters
            
        Returns:
            List of SearchResult sorted by relevance
        """
        pass
    
    @abstractmethod
    def update(self, changed_files: List[Path]) -> None:
        """Incrementally update index for changed files.
        
        Args:
            changed_files: Files added/modified/deleted
        """
        pass
    
    @abstractmethod
    def health_check(self) -> HealthStatus:
        """Check if index is operational."""
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics (doc count, size, etc.)."""
        pass
```

### IndexManager Interface (Orchestrator)

```python
# subsystems/rag/index_manager.py

class IndexManager:
    """Central orchestrator for all RAG indexes.
    
    Responsibilities:
    - Initialize all configured indexes (registry pattern)
    - Route queries to correct index
    - Manage index lifecycle (build, health, repair)
    - Coordinate incremental updates from FileWatcher
    """
    
    def __init__(self, config: IndexesConfig, base_path: Path):
        """Initialize all indexes from config."""
        self._indexes: Dict[str, BaseIndex] = {}
        self._init_indexes()  # Registry-based discovery
    
    # === Lifecycle Management ===
    
    def ensure_all_indexes_healthy(self, auto_build: bool = True) -> Dict[str, Any]:
        """Orchestrate startup health checks and auto-repair.
        
        Returns:
            {
                "all_healthy": bool,
                "indexes_rebuilt": List[str],
                "indexes_failed": List[str],
                "health_status": Dict[str, HealthStatus]
            }
        """
        pass
    
    def rebuild_index(self, index_name: str, force: bool = False) -> None:
        """Rebuild specific index from source."""
        pass
    
    def health_check_all(self) -> Dict[str, HealthStatus]:
        """Get health status for all indexes."""
        pass
    
    # === Query Routing ===
    
    def route_action(self, action: str, **kwargs) -> Dict[str, Any]:
        """Route action to correct index.
        
        Actions:
            - search_standards
            - search_code
            - search_project_docs
            - search_dependency_docs
            - find_callers (code graph)
            - find_dependencies (code graph)
        """
        pass
    
    # === Incremental Updates ===
    
    def update_from_watcher(self, index_name: str, changed_files: List[Path]) -> None:
        """Update index with changed files from FileWatcher.
        
        Delegates to index.update(changed_files).
        """
        pass
```

---

## Lifecycle Management

### Full Ownership by MCP Process

```
MCP Server Startup (server.py)
    ↓
IndexManager.ensure_all_indexes_healthy(auto_build=True)
    ↓
┌─────────────────────────────────────────────────────┐
│ 1. Health Check All Indexes                         │
│    ├─> standards.health_check()                     │
│    ├─> code.health_check()                          │
│    ├─> project_docs.health_check()                  │
│    └─> dependency_docs.health_check()               │
│                                                      │
│ 2. Categorize Unhealthy                             │
│    ├─> Secondary rebuild only (FTS/scalar missing)  │
│    └─> Full rebuild (empty or missing)              │
│                                                      │
│ 3. Rebuild Secondary Indexes (fast)                 │
│    └─> index.rebuild_secondary_indexes()            │
│                                                      │
│ 4. Rebuild Full Indexes (slow)                      │
│    └─> IndexManager.rebuild_index(name)             │
│        └─> index.build(source_paths, force=False)   │
│                                                      │
│ 5. Re-check Health                                  │
│    └─> Verify all now healthy                       │
│                                                      │
│ 6. Report Summary                                   │
│    └─> Log: rebuilt, failed, all_healthy            │
└─────────────────────────────────────────────────────┘
    ↓
Server Ready (all indexes operational)
```

### Health Check Flow (Per Index)

Each submodule implements `health_check()` to report operational status:

```python
# Example: code/__init__.py

class CodeIndex(BaseIndex):
    def health_check(self) -> HealthStatus:
        """Aggregate health from all sub-indexes."""
        
        # Check all 3 internal indexes
        semantic_healthy = self.semantic.health_check()
        ast_healthy = self.ast.health_check()
        graph_healthy = self.graph.health_check()
        
        # All must be healthy
        if not all([semantic_healthy, ast_healthy, graph_healthy]):
            return HealthStatus(
                healthy=False,
                message="One or more code sub-indexes unhealthy",
                details={
                    "semantic": semantic_healthy,
                    "ast": ast_healthy,
                    "graph": graph_healthy
                }
            )
        
        # Aggregate stats
        total_chunks = self.semantic.count_chunks()
        total_nodes = self.ast.count_nodes()
        total_symbols = self.graph.count_symbols()
        
        return HealthStatus(
            healthy=True,
            message=f"Code index operational ({total_chunks} chunks, {total_nodes} AST nodes, {total_symbols} symbols)",
            details={
                "chunks": total_chunks,
                "ast_nodes": total_nodes,
                "symbols": total_symbols
            }
        )
```

### Build Flow (Per Index)

```python
# Example: code/__init__.py

class CodeIndex(BaseIndex):
    def build(self, source_paths: List[Path], force: bool = False) -> None:
        """Build both sub-indexes from source."""
        
        logger.info("Building code index from %d paths", len(source_paths))
        
        # Build semantic index (LanceDB: vector + FTS + metadata)
        logger.info("  Building semantic index...")
        self.semantic.build(source_paths, force)
        logger.info("  ✅ Semantic index built (LanceDB)")
        
        # Build graph index (DuckDB: AST symbols + call graph)
        logger.info("  Building graph index (AST + call graph)...")
        self.graph.build(source_paths, force)
        logger.info("  ✅ Graph index built (DuckDB)")
        
        logger.info("✅ Code index fully built (LanceDB + DuckDB)")
```

---

## Corruption Detection & Auto-Repair

### Problem Statement

Index corruption can occur from:
- **Concurrent writes**: Manual rebuild while MCP server running (file handle conflicts)
- **Incomplete transactions**: Server crash mid-write
- **Disk errors**: Storage failures, permission issues
- **LanceDB bugs**: Upstream issues in lance-rs

**Symptoms:**
```python
# Search fails with LanceDB errors
RuntimeError: lance error: LanceError(IO): External error: Not found: ...
RuntimeError: lance error: Invalid manifest: ...

# FTS returns no results despite data existing
# Scalar indexes fail silently
```

### Detection Strategy

**Two-Layer Detection:**

#### 1. Proactive Detection (Startup Health Checks)

```python
# container.py
def health_check(self) -> HealthStatus:
    """Check index health with functional validation.
    
    Three-tier validation:
    1. Metadata check: Table/indexes exist?
    2. Functional check: Test query works?
    3. Data integrity: Row counts reasonable?
    """
    try:
        # Tier 1: Metadata
        if not self._table_exists():
            return HealthStatus(
                healthy=False,
                message="Table missing",
                details={"needs_full_rebuild": True}
            )
        
        row_count = self._table.count_rows()
        if row_count == 0:
            return HealthStatus(
                healthy=False,
                message="Index empty",
                details={"needs_full_rebuild": True}
            )
        
        # Tier 2: Functional validation (CRITICAL FOR CORRUPTION DETECTION)
        try:
            # Test vector search
            test_vector = [0.1] * self.config.vector.dimension
            test_results = self._table.search(test_vector).limit(1).to_list()
            
            # Test FTS (if enabled)
            if self.config.fts.enabled:
                fts_results = self._table.search("test").limit(1).to_list()
            
            # Test scalar query (if enabled)
            if self.config.scalar_indexes:
                scalar_results = self._table.search(test_vector).where("file_path IS NOT NULL").limit(1).to_list()
        
        except Exception as e:
            # Corruption detected!
            logger.warning("⚠️  Index corruption detected: %s", e)
            return HealthStatus(
                healthy=False,
                message=f"Index corrupted: {str(e)[:100]}",
                details={
                    "corruption_detected": True,
                    "needs_full_rebuild": True,
                    "error": str(e)
                }
            )
        
        # Tier 3: Data integrity
        if row_count < expected_minimum:
            return HealthStatus(
                healthy=False,
                message=f"Index incomplete: {row_count} rows (expected >{expected_minimum})",
                details={"needs_full_rebuild": True}
            )
        
        return HealthStatus(
            healthy=True,
            message=f"Healthy: {row_count} chunks indexed",
            details={"row_count": row_count}
        )
    
    except Exception as e:
        return HealthStatus(
            healthy=False,
            message=f"Health check failed: {e}",
            details={"needs_full_rebuild": True}
        )
```

#### 2. Reactive Detection (Runtime Search Errors)

```python
# container.py
def search(self, query: str, ...) -> List[SearchResult]:
    """Search with automatic corruption recovery."""
    try:
        # Normal search path
        return self._execute_search(query, ...)
    
    except RuntimeError as e:
        error_str = str(e).lower()
        
        # Detect LanceDB corruption errors
        if any(pattern in error_str for pattern in [
            "lance error",
            "invalid manifest",
            "not found",
            "corrupted",
            "external error"
        ]):
            logger.error("🚨 LanceDB corruption detected during search: %s", e)
            
            # Attempt auto-repair (if not already rebuilding)
            if not self._is_rebuilding:
                logger.info("🔧 Attempting automatic index rebuild...")
                try:
                    self.rebuild(force=True)
                    logger.info("✅ Index rebuilt successfully, retrying search...")
                    return self._execute_search(query, ...)  # Retry
                
                except Exception as rebuild_error:
                    logger.error("❌ Auto-repair failed: %s", rebuild_error)
                    raise IndexError(
                        what_failed="Search (index corrupted, auto-repair failed)",
                        why_failed=str(rebuild_error),
                        how_to_fix="Restart MCP server. If persists, delete index cache and rebuild."
                    ) from rebuild_error
            else:
                raise IndexError(
                    what_failed="Search (index rebuilding in progress)",
                    why_failed="Index is currently being rebuilt",
                    how_to_fix="Wait 30-60 seconds and try again"
                ) from e
        else:
            # Non-corruption error, re-raise
            raise
```

### Auto-Repair Workflow

**Startup Flow (Orchestrated by IndexManager):**

```
┌─────────────────────────────────────────────────────────┐
│ IndexManager.ensure_all_indexes_healthy()               │
└─────────────────────────────────────────────────────────┘
                        ↓
        ┌───────────────────────────────┐
        │ Health check all indexes      │
        └───────────────────────────────┘
                        ↓
        ┌───────────────────────────────┐
        │ Categorize unhealthy:         │
        │ - Corruption detected?        │
        │ - Missing table?              │
        │ - Secondary indexes only?     │
        └───────────────────────────────┘
                        ↓
        ┌───────────────────────────────┐
        │ Rebuild secondary (fast) →    │
        │   FTS + scalar only           │
        └───────────────────────────────┘
                        ↓
        ┌───────────────────────────────┐
        │ Rebuild full (slow) →         │
        │   Re-chunk + re-embed         │
        └───────────────────────────────┘
                        ↓
        ┌───────────────────────────────┐
        │ Re-check health               │
        │ - All healthy? ✅             │
        │ - Still failing? ❌ Log error │
        └───────────────────────────────┘
```

**Runtime Flow (Triggered by Search Error):**

```
┌─────────────────────────────────────────────────────────┐
│ User searches → LanceDB error                            │
└─────────────────────────────────────────────────────────┘
                        ↓
        ┌───────────────────────────────┐
        │ Detect corruption pattern     │
        │ "lance error", "corrupted"    │
        └───────────────────────────────┘
                        ↓
        ┌───────────────────────────────┐
        │ Check rebuild lock            │
        │ (prevent concurrent rebuilds) │
        └───────────────────────────────┘
                        ↓
        ┌───────────────────────────────┐
        │ Acquire lock → rebuild        │
        └───────────────────────────────┘
                        ↓
        ┌───────────────────────────────┐
        │ Retry search (once)           │
        │ - Success? ✅                 │
        │ - Fail? ❌ Raise error        │
        └───────────────────────────────┘
```

### Implementation Details

#### Rebuild Lock (Prevent Concurrent Rebuilds)

```python
# container.py
class StandardsIndex:
    def __init__(self, ...):
        self._rebuild_lock = threading.Lock()
        self._is_rebuilding = False
    
    def rebuild(self, force: bool = False):
        """Thread-safe rebuild with lock."""
        with self._rebuild_lock:
            if self._is_rebuilding:
                raise IndexError(
                    what_failed="Index rebuild",
                    why_failed="Rebuild already in progress",
                    how_to_fix="Wait for current rebuild to complete"
                )
            
            try:
                self._is_rebuilding = True
                self._do_rebuild(force=force)
            finally:
                self._is_rebuilding = False
```

#### Corruption Detection Patterns

```python
# Patterns that indicate LanceDB corruption (from real logs)
CORRUPTION_PATTERNS = [
    "lance error",           # Generic LanceDB error
    "invalid manifest",      # Manifest file corrupted
    "not found",            # Missing index files
    "corrupted",            # Explicit corruption
    "external error",       # I/O errors from lance-rs
    "failed to read",       # Read failures
    "unexpected eof",       # Truncated files
]

def is_corruption_error(error: Exception) -> bool:
    """Detect if error indicates index corruption."""
    error_str = str(error).lower()
    return any(pattern in error_str for pattern in CORRUPTION_PATTERNS)
```

#### Health Check Details for Each Index Type

**Standards (LanceDB: Vector + FTS + Scalar):**
```python
# Test vector search
test_vector = [0.1] * dimension
vector_results = table.search(test_vector).limit(1).to_list()

# Test FTS
fts_results = table.search("test").limit(1).to_list()

# Test scalar filtering
scalar_results = table.search(test_vector).where("domain IS NOT NULL").limit(1).to_list()
```

**Code Semantic (LanceDB: Vector + FTS + Scalar):**
```python
# Test vector search
test_vector = [0.1] * dimension
vector_results = table.search(test_vector).limit(1).to_list()

# Test FTS
fts_results = table.search("function").limit(1).to_list()

# Test scalar filtering (language, file_path)
scalar_results = table.search(test_vector).where("language = 'python'").limit(1).to_list()
```

**Code Graph (DuckDB: AST + Call Graph):**
```python
# Test symbol query
cursor.execute("SELECT * FROM symbols LIMIT 1")

# Test relationship query
cursor.execute("SELECT * FROM relationships LIMIT 1")

# Test recursive CTE (call graph traversal)
cursor.execute("""
    WITH RECURSIVE callers AS (
        SELECT * FROM relationships WHERE called_symbol = 'test' LIMIT 1
    )
    SELECT * FROM callers
""")
```

### Logging & Observability

**Corruption Detection Logs:**
```
2025-11-05 10:23:45 WARNING [standards_index] ⚠️  Index corruption detected: lance error: Invalid manifest
2025-11-05 10:23:45 INFO    [standards_index] 🔧 Attempting automatic index rebuild...
2025-11-05 10:24:12 INFO    [standards_index] ✅ Index rebuilt successfully (450 chunks)
2025-11-05 10:24:12 INFO    [standards_index] ♻️  Retrying search after auto-repair...
2025-11-05 10:24:13 INFO    [standards_index] ✅ Search succeeded after auto-repair
```

**Health Check Logs:**
```
2025-11-05 10:20:00 INFO    [index_manager] 🔍 Checking health of all indexes...
2025-11-05 10:20:00 INFO    [index_manager]   ✅ standards: Healthy (450 chunks)
2025-11-05 10:20:00 WARNING [index_manager]   ⚠️  code: Corrupted (lance error: Invalid manifest)
2025-11-05 10:20:00 INFO    [index_manager] 🔧 Rebuilding 1 corrupted index(es)...
2025-11-05 10:20:45 INFO    [index_manager]   ✅ Built code index (1234 chunks)
2025-11-05 10:20:45 INFO    [index_manager] ✅ All indexes healthy and operational
```

### Edge Cases

#### 1. Concurrent Rebuild (MCP Server + Manual Script)

**Problem:** User runs manual rebuild script while MCP server running
**Solution:** File lock on index directory

```python
# Acquire EXCLUSIVE lock on .index.lock
lock_path = cache_path / ".index.lock"
with open(lock_path, "w") as lock_file:
    try:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        # Rebuild...
    except BlockingIOError:
        raise IndexError(
            what_failed="Index rebuild",
            why_failed="Another process is rebuilding the index",
            how_to_fix="Wait for other rebuild to complete, or stop MCP server"
        )
```

#### 2. Repeated Corruption (Auto-Repair Limit)

**Problem:** Index keeps getting corrupted (disk issue, bug)
**Solution:** Limit auto-repair attempts, fail fast

```python
# Track repair attempts
self._repair_attempts = 0
MAX_REPAIR_ATTEMPTS = 3

if self._repair_attempts >= MAX_REPAIR_ATTEMPTS:
    raise IndexError(
        what_failed="Search (index repeatedly corrupted)",
        why_failed=f"Auto-repair failed {MAX_REPAIR_ATTEMPTS} times",
        how_to_fix="Check disk health. Delete index cache: rm -rf .cache/rag/. Restart server."
    )
```

#### 3. Partial Corruption (FTS Broken, Vector OK)

**Problem:** FTS index corrupted but vector search works
**Solution:** Rebuild secondary indexes only (fast path)

```python
def health_check(self) -> HealthStatus:
    # ...
    
    # Vector works?
    try:
        vector_results = self._test_vector_search()
    except:
        return HealthStatus(healthy=False, details={"needs_full_rebuild": True})
    
    # FTS works?
    try:
        fts_results = self._test_fts_search()
    except:
        return HealthStatus(
            healthy=False,
            message="FTS corrupted (vector OK)",
            details={"needs_secondary_rebuild": True}  # Fast path!
        )
```

### Testing Strategy

**Unit Tests:**
```python
def test_detects_corruption_from_lance_error():
    """Test corruption detection from LanceDB error."""
    index = StandardsIndex(...)
    
    # Mock corrupted table
    index._table.search = Mock(side_effect=RuntimeError("lance error: Invalid manifest"))
    
    # Health check should detect corruption
    health = index.health_check()
    assert not health.healthy
    assert health.details["corruption_detected"] is True

def test_auto_repair_on_search_error():
    """Test automatic repair when search fails."""
    index = StandardsIndex(...)
    
    # First search fails (corruption)
    index._execute_search = Mock(side_effect=RuntimeError("lance error: ..."))
    
    # Rebuild succeeds
    index.rebuild = Mock()
    
    # Second search succeeds
    index._execute_search.side_effect = [
        RuntimeError("lance error: ..."),  # First call
        [SearchResult(...)]                # Second call (after repair)
    ]
    
    # Should auto-repair and succeed
    results = index.search("test query")
    assert len(results) > 0
    index.rebuild.assert_called_once()
```

**Integration Tests:**
```python
def test_startup_corruption_recovery():
    """Test server starts successfully even with corrupted index."""
    # Corrupt the index
    shutil.rmtree(cache_path / "standards.lance")
    
    # Start server (should auto-rebuild)
    index_manager = IndexManager(config, base_path)
    result = index_manager.ensure_all_indexes_healthy(auto_build=True)
    
    assert result["all_healthy"] is True
    assert "standards" in result["indexes_rebuilt"]
```

### References

- **Old MCP Server Implementation**: `.praxis-os/mcp_server/server/indexes/standards_index.py` (lines 735-757)
- **LanceDB Corruption Patterns**: Observed from production logs in `cursor-data-discovery.md`
- **Auto-Repair Philosophy**: "Just works" reliability - detect and fix automatically, user never sees errors

---

## File Locking for Index Integrity

### Problem Statement

**Primary Corruption Source:** Manual rebuild scripts running while MCP server is operating.

```bash
# Terminal 1: MCP server running (Cursor open)
# LanceDB has open file handles to index files

# Terminal 2: User runs manual rebuild
python .praxis-os/scripts/rebuild_index.py --force

# Result: Index corruption (concurrent writes to LanceDB)
# Symptoms: "lance error: Invalid manifest", "External error: Not found"
```

**Why This Happens:**
- LanceDB uses memory-mapped files and maintains internal state
- Concurrent writes from different processes corrupt the manifest
- No database-level locking in LanceDB (relies on application-level coordination)

### Solution: File-Based Locking (fcntl)

**Two-Lock Pattern (from proven old mcp_server):**

#### 1. **Shared Lock** (Held While MCP Server Running)

```python
# Acquired on index connection, released on shutdown
# Prevents manual rebuild scripts from running
# Multiple readers OK (stdio + http), no writers allowed

lock_file = cache_path / ".index.lock"
fcntl.flock(lock_fd, fcntl.LOCK_SH)  # Shared lock
```

#### 2. **Exclusive Lock** (Held During Rebuild)

```python
# Acquired before rebuild, released after
# Blocks other rebuilds AND queries
# Only one writer at a time

lock_file = cache_path / ".index.lock"
fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)  # Exclusive, non-blocking
```

### Lock State Diagram

```
┌─────────────────────────────────────────────────────────┐
│ Lock States                                              │
└─────────────────────────────────────────────────────────┘

UNLOCKED (No MCP server, no rebuild)
    ↓
    ├─→ MCP Server Starts
    │   ├─ Acquire SHARED lock on connection
    │   └─ Hold for entire server lifetime
    │       ↓
    │   SHARED LOCKED (Server running, queries OK)
    │       ↓
    │       ├─ Manual rebuild tries EXCLUSIVE lock
    │       │  └─→ FAILS (BlockingIOError)
    │       │      "Another process holds the lock"
    │       │
    │       └─ Server shutdown releases SHARED lock
    │           └─→ Back to UNLOCKED
    │
    └─→ Manual Rebuild (Server NOT running)
        ├─ Acquire EXCLUSIVE lock
        └─ Release after rebuild
            └─→ Back to UNLOCKED
```

### Utility Module: `IndexLockManager`

**Centralized lock management to avoid reimplementation in every container.**

```python
# subsystems/rag/lock_manager.py
"""File-based locking for RAG indexes.

Prevents concurrent access to LanceDB/DuckDB indexes from multiple processes.
Uses fcntl (POSIX) for advisory locks.

Design:
- Shared lock: MCP server holds while running (allows queries)
- Exclusive lock: Rebuilds hold temporarily (blocks everything)
- Non-blocking: Fail fast if lock unavailable
"""

import fcntl
import logging
from pathlib import Path
from typing import Optional, Literal
from contextlib import contextmanager

logger = logging.getLogger(__name__)

LockType = Literal["shared", "exclusive"]


class IndexLockManager:
    """Manages file locks for index integrity.
    
    Prevents corruption from concurrent access by different processes.
    Typical usage:
    - Shared lock: Acquired on index connection (held while server running)
    - Exclusive lock: Acquired during rebuild (blocks all access)
    
    Thread Safety:
        Uses OS-level locks (fcntl), automatically thread-safe within process.
        Protects against different processes, not different threads.
    """
    
    def __init__(self, index_name: str, cache_path: Path):
        """Initialize lock manager for an index.
        
        Args:
            index_name: Index identifier (e.g., "standards", "code")
            cache_path: Cache directory where lock file will be stored
        """
        self.index_name = index_name
        self.cache_path = cache_path
        self.lock_file_path = cache_path / f".{index_name}.lock"
        self._lock_fd: Optional[int] = None
        self._lock_type: Optional[LockType] = None
    
    def acquire_shared(self, blocking: bool = True) -> bool:
        """Acquire shared lock (multiple readers allowed).
        
        Used by MCP server to hold lock while running. Prevents manual
        rebuild scripts from acquiring exclusive lock.
        
        Args:
            blocking: If True, waits for lock. If False, fails immediately.
        
        Returns:
            True if lock acquired, False if non-blocking and unavailable
        
        Raises:
            IOError: If lock acquisition fails (permissions, etc.)
        """
        if self._lock_fd is not None:
            logger.warning("Lock already held (%s), releasing first", self._lock_type)
            self.release()
        
        try:
            # Create lock file if doesn't exist
            self.cache_path.mkdir(parents=True, exist_ok=True)
            self._lock_fd = open(self.lock_file_path, 'w', encoding='utf-8')
            
            # Acquire shared lock
            lock_flag = fcntl.LOCK_SH
            if not blocking:
                lock_flag |= fcntl.LOCK_NB
            
            logger.debug("Acquiring SHARED lock on %s index...", self.index_name)
            fcntl.flock(self._lock_fd.fileno(), lock_flag)
            self._lock_type = "shared"
            logger.info("✅ SHARED lock acquired on %s index", self.index_name)
            return True
        
        except BlockingIOError:
            logger.warning("⚠️  SHARED lock unavailable (exclusive lock held)")
            if self._lock_fd:
                self._lock_fd.close()
                self._lock_fd = None
            return False
        
        except Exception as e:
            logger.error("Failed to acquire SHARED lock: %s", e)
            if self._lock_fd:
                self._lock_fd.close()
                self._lock_fd = None
            raise
    
    def acquire_exclusive(self, blocking: bool = False) -> bool:
        """Acquire exclusive lock (no readers/writers allowed).
        
        Used during index rebuild. Blocks all other access (queries, rebuilds).
        
        Args:
            blocking: If True, waits for lock. If False, fails immediately.
                     Default False for rebuilds (fail fast if server running).
        
        Returns:
            True if lock acquired, False if non-blocking and unavailable
        
        Raises:
            IOError: If lock acquisition fails
        """
        if self._lock_fd is not None:
            logger.warning("Lock already held (%s), releasing first", self._lock_type)
            self.release()
        
        try:
            # Create lock file if doesn't exist
            self.cache_path.mkdir(parents=True, exist_ok=True)
            self._lock_fd = open(self.lock_file_path, 'w', encoding='utf-8')
            
            # Acquire exclusive lock
            lock_flag = fcntl.LOCK_EX
            if not blocking:
                lock_flag |= fcntl.LOCK_NB
            
            logger.debug("Acquiring EXCLUSIVE lock on %s index...", self.index_name)
            fcntl.flock(self._lock_fd.fileno(), lock_flag)
            self._lock_type = "exclusive"
            logger.info("✅ EXCLUSIVE lock acquired on %s index", self.index_name)
            return True
        
        except BlockingIOError:
            logger.warning("⚠️  EXCLUSIVE lock unavailable (server running or other rebuild in progress)")
            if self._lock_fd:
                self._lock_fd.close()
                self._lock_fd = None
            return False
        
        except Exception as e:
            logger.error("Failed to acquire EXCLUSIVE lock: %s", e)
            if self._lock_fd:
                self._lock_fd.close()
                self._lock_fd = None
            raise
    
    def release(self) -> None:
        """Release currently held lock."""
        if self._lock_fd is None:
            logger.debug("No lock to release")
            return
        
        try:
            fcntl.flock(self._lock_fd.fileno(), fcntl.LOCK_UN)
            self._lock_fd.close()
            logger.info("✅ %s lock released on %s index", 
                       self._lock_type.upper() if self._lock_type else "UNKNOWN",
                       self.index_name)
        except Exception as e:
            logger.warning("Failed to release lock: %s", e)
        finally:
            self._lock_fd = None
            self._lock_type = None
    
    @contextmanager
    def exclusive_lock(self, blocking: bool = False):
        """Context manager for exclusive lock (rebuild operations).
        
        Usage:
            with lock_manager.exclusive_lock():
                # Rebuild index
                ...
        """
        acquired = self.acquire_exclusive(blocking=blocking)
        if not acquired:
            raise IOError(
                f"Cannot acquire exclusive lock on {self.index_name} index. "
                "Another process (MCP server or rebuild script) is using it. "
                "Stop the MCP server or wait for other operation to complete."
            )
        
        try:
            yield
        finally:
            self.release()
    
    def __del__(self):
        """Ensure lock is released on garbage collection."""
        if self._lock_fd is not None:
            try:
                self.release()
            except Exception:
                pass  # Best effort cleanup
```

### Usage in Index Containers

#### Connection (Acquire Shared Lock)

```python
# standards/container.py
from ouroboros.subsystems.rag.lock_manager import IndexLockManager

class StandardsIndex(BaseIndex):
    def __init__(self, config, base_path):
        self.config = config
        self.base_path = base_path
        self.cache_path = base_path / ".cache" / "rag" / "standards"
        
        # Initialize lock manager
        self.lock_manager = IndexLockManager(
            index_name="standards",
            cache_path=self.cache_path
        )
        
        # Connect to LanceDB
        self._connect()
    
    def _connect(self):
        """Connect to LanceDB and acquire shared lock."""
        import lancedb
        
        # Acquire shared lock (hold for server lifetime)
        if not self.lock_manager.acquire_shared(blocking=False):
            logger.warning("⚠️  Could not acquire shared lock, proceeding without lock")
            # Continue anyway (degraded mode), but log warning
        
        # Connect to LanceDB
        self.db = lancedb.connect(str(self.cache_path))
        self.table = self.db.open_table("standards")
        logger.info("Connected to standards index")
    
    def close(self):
        """Close connection and release lock."""
        if hasattr(self, 'table'):
            del self.table
        if hasattr(self, 'db'):
            del self.db
        
        # Release shared lock
        self.lock_manager.release()
        logger.info("Standards index connection closed")
```

#### Rebuild (Acquire Exclusive Lock)

```python
# standards/container.py (continued)
def rebuild(self, force: bool = False):
    """Rebuild index with exclusive lock."""
    
    # Acquire exclusive lock (fail fast if server running)
    with self.lock_manager.exclusive_lock(blocking=False):
        logger.info("🔨 Rebuilding standards index...")
        
        # Do rebuild
        self._chunk_files()
        self._generate_embeddings()
        self._build_lancedb_table()
        self._create_indexes()
        
        logger.info("✅ Standards index rebuilt successfully")
```

### Error Messages

**Manual Rebuild While Server Running:**

```bash
$ python rebuild_index.py --force

❌ Error: Cannot acquire exclusive lock on standards index.
   Reason: Another process (MCP server or rebuild script) is using it.
   
   How to fix:
   1. Close Cursor (stops MCP server)
   2. Wait a few seconds for lock to release
   3. Run rebuild again
   
   OR
   
   Trust automatic rebuild: The MCP server will auto-rebuild on next file change.
```

**Server Startup (Lock Already Held):**

```
2025-11-05 10:30:00 WARNING [standards_index] ⚠️  Could not acquire shared lock (exclusive lock held)
2025-11-05 10:30:00 WARNING [standards_index]    Another process may be rebuilding the index
2025-11-05 10:30:00 INFO    [standards_index]    Proceeding in degraded mode (queries OK, but no rebuild protection)
```

### Platform Compatibility

**POSIX Systems (Linux, macOS):**
- `fcntl` module available (standard library)
- Advisory locks (processes can ignore, but well-behaved apps respect)

**Windows:**
- `fcntl` not available
- Fallback options:
  1. `msvcrt.locking()` (Windows equivalent)
  2. Named mutexes (`win32event`)
  3. No-op (log warning, no lock protection)

**Proposed Implementation:**

```python
# lock_manager.py
import sys
import logging

logger = logging.getLogger(__name__)

if sys.platform == "win32":
    logger.warning("⚠️  File locking not yet implemented for Windows")
    logger.warning("    Index corruption possible if manual rebuild run while server running")
    
    # Stub implementation (no-op)
    class IndexLockManager:
        def __init__(self, index_name, cache_path):
            pass
        
        def acquire_shared(self, blocking=True):
            return True  # No-op
        
        def acquire_exclusive(self, blocking=False):
            return True  # No-op
        
        def release(self):
            pass  # No-op
else:
    # Real fcntl-based implementation (POSIX)
    # ... (code above) ...
```

### Integration with Existing Code

**Changes Required:**

1. **Create `lock_manager.py` utility module**
   - `IndexLockManager` class
   - Platform detection (fcntl vs Windows stub)

2. **Update all index containers:**
   - `standards/container.py`
   - `code/container.py` (semantic + graph both need locks)
   - Future: `project_docs/container.py`, `dependency_docs/container.py`

3. **Acquire shared lock on connection:**
   - Called in `__init__()` or `_connect()`
   - Held for entire server lifetime
   - Released in `close()` or `__del__()`

4. **Acquire exclusive lock on rebuild:**
   - Use context manager: `with self.lock_manager.exclusive_lock():`
   - Fail fast if unavailable (non-blocking)
   - Actionable error message

5. **Update rebuild scripts:**
   - Use same `IndexLockManager`
   - Fail fast with clear message if server running

### Testing Strategy

**Unit Tests:**

```python
def test_shared_lock_allows_multiple_readers():
    """Test multiple processes can hold shared locks."""
    lock1 = IndexLockManager("standards", cache_path)
    lock2 = IndexLockManager("standards", cache_path)
    
    assert lock1.acquire_shared(blocking=False)
    assert lock2.acquire_shared(blocking=False)  # Should succeed
    
    lock1.release()
    lock2.release()

def test_exclusive_lock_blocks_shared():
    """Test exclusive lock prevents shared lock acquisition."""
    lock1 = IndexLockManager("standards", cache_path)
    lock2 = IndexLockManager("standards", cache_path)
    
    assert lock1.acquire_exclusive(blocking=False)
    assert not lock2.acquire_shared(blocking=False)  # Should fail
    
    lock1.release()

def test_exclusive_lock_blocks_exclusive():
    """Test only one exclusive lock at a time."""
    lock1 = IndexLockManager("standards", cache_path)
    lock2 = IndexLockManager("standards", cache_path)
    
    assert lock1.acquire_exclusive(blocking=False)
    assert not lock2.acquire_exclusive(blocking=False)  # Should fail
    
    lock1.release()

def test_context_manager_releases_on_exception():
    """Test lock released even if rebuild fails."""
    lock = IndexLockManager("standards", cache_path)
    
    try:
        with lock.exclusive_lock():
            raise RuntimeError("Simulated rebuild failure")
    except RuntimeError:
        pass
    
    # Lock should be released
    assert lock._lock_fd is None
```

**Integration Tests:**

```python
def test_server_startup_with_manual_rebuild():
    """Test server startup while manual rebuild running (edge case)."""
    # Start manual rebuild (holds exclusive lock)
    rebuild_process = subprocess.Popen(["python", "rebuild_index.py", "--force"])
    time.sleep(1)  # Let rebuild acquire lock
    
    # Try to start server (should fail to acquire shared lock)
    index = StandardsIndex(config, base_path)
    # Should log warning but continue in degraded mode
    
    rebuild_process.terminate()
    rebuild_process.wait()
```

### Benefits

1. **Prevents Primary Corruption Source**: Manual rebuild while server running
2. **Fail Fast**: Clear error messages when lock unavailable
3. **Reusable**: Single `IndexLockManager` used by all indexes
4. **Cross-Process**: Protects against different processes (stdio + http + manual scripts)
5. **Proven Design**: Same pattern as old mcp_server (battle-tested)

### References

- **Old MCP Server Implementation**: `.praxis-os/mcp_server/server/indexes/standards_index.py` (lines 277, 419, 791)
- **fcntl Documentation**: https://docs.python.org/3/library/fcntl.html
- **Advisory Locking**: Well-behaved processes cooperate, malicious processes can ignore

---

## Shared Utilities (DRY Principles)

### Problem: Code Duplication Across Indexes

**Current state (Ouroboros):**

```python
# standards_index.py - Lines 71-127
def _ensure_db(self):
    if self._db is None:
        import lancedb
        self._db = lancedb.connect(str(self.index_path))
        # ... error handling ...

def _ensure_table(self):
    if self._table is None:
        self._ensure_db()
        self._table = self._db.open_table("standards")
        # ... error handling ...

def _ensure_embedding_model(self):
    if self._embedding_model is None:
        from sentence_transformers import SentenceTransformer
        self._embedding_model = SentenceTransformer(self.config.vector.model)
        # ... error handling ...

# code_index.py - Lines 74-120
# EXACT SAME CODE (except table name)
def _ensure_db(self): ...
def _ensure_table(self): ...
def _ensure_embedding_model(self): ...
```

**Duplication across:**
- `standards_index.py` ✅ Has it
- `code_index.py` ✅ Has it
- Future: `project_docs/semantic.py` ❓ Will need it
- Future: `dependency_docs/semantic.py` ❓ Will need it

### Solution: Utility Modules

#### 1. **LanceDB Connection Manager** (`rag/utils/lancedb_helpers.py`)

```python
# subsystems/rag/utils/lancedb_helpers.py
"""LanceDB connection and table management utilities.

Provides lazy-loading patterns for LanceDB connections, tables, and models
to avoid duplication across all LanceDB-based indexes.
"""

import logging
from pathlib import Path
from typing import Any, Optional

from ouroboros.utils.errors import ActionableError, IndexError

logger = logging.getLogger(__name__)


class LanceDBConnection:
    """Manages LanceDB connection with lazy initialization.
    
    Thread-safe, lazy-loading wrapper for LanceDB database connections.
    Reusable across all indexes that use LanceDB.
    """
    
    def __init__(self, db_path: Path):
        """Initialize connection manager.
        
        Args:
            db_path: Path to LanceDB database directory
        """
        self.db_path = db_path
        self._db: Optional[Any] = None
    
    def connect(self) -> Any:
        """Get or create LanceDB connection (lazy initialization).
        
        Returns:
            LanceDB database connection
            
        Raises:
            ActionableError: If connection fails
        """
        if self._db is None:
            try:
                import lancedb
                self.db_path.mkdir(parents=True, exist_ok=True)
                self._db = lancedb.connect(str(self.db_path))
                logger.info("✅ Connected to LanceDB at %s", self.db_path)
            except ImportError as e:
                raise ActionableError(
                    what_failed="LanceDB import",
                    why_failed="lancedb package not installed",
                    how_to_fix="Install via: pip install 'lancedb>=0.13.0'"
                ) from e
            except Exception as e:
                raise ActionableError(
                    what_failed="LanceDB connection",
                    why_failed=str(e),
                    how_to_fix=f"Check that {self.db_path} is writable"
                ) from e
        
        return self._db
    
    def open_table(self, table_name: str) -> Any:
        """Open a table (lazy initialization).
        
        Args:
            table_name: Name of the table to open
            
        Returns:
            LanceDB table object
            
        Raises:
            IndexError: If table doesn't exist
        """
        db = self.connect()
        try:
            table = db.open_table(table_name)
            logger.info("✅ Opened table: %s", table_name)
            return table
        except Exception as e:
            raise IndexError(
                what_failed=f"Open table '{table_name}'",
                why_failed="Table does not exist. Index not built yet.",
                how_to_fix=f"Build index first using IndexManager.rebuild_index('{table_name}')"
            ) from e
    
    def close(self):
        """Close connection and release resources."""
        if self._db is not None:
            # LanceDB doesn't have explicit close, just release reference
            del self._db
            self._db = None
            logger.info("LanceDB connection closed")


class EmbeddingModelLoader:
    """Manages sentence-transformer embedding models with lazy loading.
    
    Caches loaded models to avoid reloading across different operations.
    Reusable across all indexes that use embeddings.
    """
    
    # Class-level cache: {model_name: model_instance}
    _model_cache: dict[str, Any] = {}
    
    @classmethod
    def load(cls, model_name: str) -> Any:
        """Load or retrieve cached embedding model.
        
        Args:
            model_name: HuggingFace model identifier
            
        Returns:
            SentenceTransformer model instance
            
        Raises:
            ActionableError: If model loading fails
        """
        if model_name not in cls._model_cache:
            try:
                from sentence_transformers import SentenceTransformer
                
                logger.info("Loading embedding model: %s", model_name)
                model = SentenceTransformer(model_name)
                cls._model_cache[model_name] = model
                logger.info("✅ Embedding model loaded: %s", model_name)
                
            except ImportError as e:
                raise ActionableError(
                    what_failed="SentenceTransformer import",
                    why_failed="sentence-transformers package not installed",
                    how_to_fix="Install via: pip install 'sentence-transformers>=2.0.0'"
                ) from e
            except Exception as e:
                raise ActionableError(
                    what_failed=f"Load embedding model ({model_name})",
                    why_failed=str(e),
                    how_to_fix="Check model name in config. Examples: BAAI/bge-small-en-v1.5, sentence-transformers/all-MiniLM-L6-v2"
                ) from e
        
        return cls._model_cache[model_name]
    
    @classmethod
    def clear_cache(cls):
        """Clear model cache (for testing or memory management)."""
        cls._model_cache.clear()
        logger.info("Embedding model cache cleared")


class RerankerLoader:
    """Manages cross-encoder reranking models with lazy loading.
    
    Optional component for improving search precision.
    Reusable across all indexes that support reranking.
    """
    
    # Class-level cache: {model_name: model_instance}
    _reranker_cache: dict[str, Any] = {}
    
    @classmethod
    def load(cls, model_name: str) -> Optional[Any]:
        """Load or retrieve cached reranker model.
        
        Args:
            model_name: HuggingFace cross-encoder model identifier
            
        Returns:
            CrossEncoder model instance, or None if unavailable
        """
        if model_name not in cls._reranker_cache:
            try:
                from sentence_transformers import CrossEncoder
                
                logger.info("Loading reranker model: %s", model_name)
                model = CrossEncoder(model_name)
                cls._reranker_cache[model_name] = model
                logger.info("✅ Reranker loaded: %s", model_name)
                
            except ImportError:
                logger.warning("⚠️  Cross-encoder not available, reranking disabled")
                return None
            except Exception as e:
                logger.warning("⚠️  Failed to load reranker, reranking disabled: %s", e)
                return None
        
        return cls._reranker_cache.get(model_name)
```

**Usage in containers:**

```python
# standards/container.py
from ouroboros.subsystems.rag.utils.lancedb_helpers import (
    LanceDBConnection, 
    EmbeddingModelLoader,
    RerankerLoader
)

class StandardsIndex(BaseIndex):
    def __init__(self, config, base_path):
        self.config = config
        self.base_path = base_path
        self.cache_path = base_path / ".cache" / "rag" / "standards"
        
        # Use utility classes (no duplication!)
        self.lancedb = LanceDBConnection(self.cache_path)
        self._table = None
        self._embedding_model = None
        self._reranker = None
    
    def _ensure_table(self):
        """Open table (uses utility)."""
        if self._table is None:
            self._table = self.lancedb.open_table("standards")
    
    def _ensure_embedding_model(self):
        """Load embedding model (uses utility)."""
        if self._embedding_model is None:
            self._embedding_model = EmbeddingModelLoader.load(
                self.config.vector.model
            )
    
    def _ensure_reranker(self):
        """Load reranker (uses utility)."""
        if self._reranker is None and self.config.reranking:
            self._reranker = RerankerLoader.load(
                self.config.reranking.model
            )
```

#### 2. **DuckDB Connection Manager** (`rag/utils/duckdb_helpers.py`)

```python
# subsystems/rag/utils/duckdb_helpers.py
"""DuckDB connection management utilities.

Provides lazy-loading patterns for DuckDB connections and schema management
for AST and graph indexes.
"""

import logging
from pathlib import Path
from typing import Any, Optional

from ouroboros.utils.errors import ActionableError

logger = logging.getLogger(__name__)


class DuckDBConnection:
    """Manages DuckDB connection with lazy initialization.
    
    Thread-safe, lazy-loading wrapper for DuckDB database connections.
    Reusable for AST and graph indexes.
    """
    
    def __init__(self, db_path: Path):
        """Initialize connection manager.
        
        Args:
            db_path: Path to DuckDB database file
        """
        self.db_path = db_path
        self._conn: Optional[Any] = None
    
    def connect(self) -> Any:
        """Get or create DuckDB connection (lazy initialization).
        
        Returns:
            DuckDB connection object
            
        Raises:
            ActionableError: If connection fails
        """
        if self._conn is None:
            try:
                import duckdb
                
                self.db_path.parent.mkdir(parents=True, exist_ok=True)
                self._conn = duckdb.connect(str(self.db_path))
                logger.info("✅ Connected to DuckDB at %s", self.db_path)
                
            except ImportError as e:
                raise ActionableError(
                    what_failed="DuckDB import",
                    why_failed="duckdb package not installed",
                    how_to_fix="Install via: pip install 'duckdb>=0.9.0'"
                ) from e
            except Exception as e:
                raise ActionableError(
                    what_failed="DuckDB connection",
                    why_failed=str(e),
                    how_to_fix=f"Check that {self.db_path.parent} is writable"
                ) from e
        
        return self._conn
    
    def execute(self, query: str, params: Optional[tuple] = None) -> Any:
        """Execute query with connection.
        
        Args:
            query: SQL query string
            params: Optional query parameters
            
        Returns:
            Query result
        """
        conn = self.connect()
        if params:
            return conn.execute(query, params)
        return conn.execute(query)
    
    def close(self):
        """Close connection and release resources."""
        if self._conn is not None:
            self._conn.close()
            self._conn = None
            logger.info("DuckDB connection closed")
```

#### 3. **File Change Detection** (`rag/utils/file_tracker.py`)

```python
# subsystems/rag/utils/file_tracker.py
"""File change detection for incremental index updates.

Tracks file modification times and hashes to detect changes since last build.
Reusable across all indexes.
"""

import hashlib
import json
import logging
from pathlib import Path
from typing import Dict, List, Set

logger = logging.getLogger(__name__)


class FileChangeTracker:
    """Tracks file changes for incremental index updates.
    
    Persists metadata (file hashes, mod times) to detect:
    - New files
    - Modified files
    - Deleted files
    
    Reusable across all indexes that need incremental updates.
    """
    
    def __init__(self, metadata_path: Path):
        """Initialize change tracker.
        
        Args:
            metadata_path: Path to metadata JSON file
        """
        self.metadata_path = metadata_path
        self.metadata: Dict[str, Dict] = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, Dict]:
        """Load file metadata from disk."""
        if self.metadata_path.exists():
            try:
                with open(self.metadata_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning("Failed to load metadata, starting fresh: %s", e)
        return {}
    
    def _save_metadata(self):
        """Save file metadata to disk."""
        try:
            self.metadata_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.metadata_path, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            logger.warning("Failed to save metadata: %s", e)
    
    def get_changed_files(
        self,
        current_files: List[Path],
        use_hash: bool = False
    ) -> Dict[str, List[Path]]:
        """Detect changed files since last build.
        
        Args:
            current_files: List of files to check
            use_hash: If True, use content hash. If False, use mtime only.
        
        Returns:
            Dictionary with keys:
            - "new": Newly added files
            - "modified": Files that changed
            - "deleted": Files that were removed
        """
        new_files = []
        modified_files = []
        
        current_paths = {str(f.resolve()) for f in current_files}
        old_paths = set(self.metadata.keys())
        
        # Detect new and modified
        for file_path in current_files:
            path_str = str(file_path.resolve())
            
            if path_str not in self.metadata:
                # New file
                new_files.append(file_path)
            else:
                # Check if modified
                if use_hash:
                    current_hash = self._compute_hash(file_path)
                    if current_hash != self.metadata[path_str].get("hash"):
                        modified_files.append(file_path)
                else:
                    current_mtime = file_path.stat().st_mtime
                    if current_mtime > self.metadata[path_str].get("mtime", 0):
                        modified_files.append(file_path)
        
        # Detect deleted
        deleted_paths = old_paths - current_paths
        deleted_files = [Path(p) for p in deleted_paths]
        
        logger.info("File changes: %d new, %d modified, %d deleted",
                   len(new_files), len(modified_files), len(deleted_files))
        
        return {
            "new": new_files,
            "modified": modified_files,
            "deleted": deleted_files
        }
    
    def update_metadata(self, files: List[Path], use_hash: bool = False):
        """Update metadata for files.
        
        Args:
            files: Files to update metadata for
            use_hash: If True, compute content hash
        """
        for file_path in files:
            path_str = str(file_path.resolve())
            
            metadata = {
                "mtime": file_path.stat().st_mtime,
            }
            
            if use_hash:
                metadata["hash"] = self._compute_hash(file_path)
            
            self.metadata[path_str] = metadata
        
        self._save_metadata()
    
    def remove_metadata(self, files: List[Path]):
        """Remove metadata for deleted files.
        
        Args:
            files: Files to remove metadata for
        """
        for file_path in files:
            path_str = str(file_path.resolve())
            self.metadata.pop(path_str, None)
        
        self._save_metadata()
    
    @staticmethod
    def _compute_hash(file_path: Path) -> str:
        """Compute MD5 hash of file content.
        
        Args:
            file_path: File to hash
            
        Returns:
            Hex digest of MD5 hash
        """
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
```

#### 4. **File Discovery** (`rag/utils/file_discovery.py`)

```python
# subsystems/rag/utils/file_discovery.py
"""File discovery utilities for index building.

Provides glob-based file discovery with language detection and filtering.
Reusable across all indexes.
"""

import logging
from pathlib import Path
from typing import List, Optional, Set

logger = logging.getLogger(__name__)


class FileDiscovery:
    """Discovers files for index building.
    
    Supports:
    - Glob patterns (**.md, **.py, etc.)
    - Language filtering
    - Exclude patterns (.gitignore-style)
    - Size limits
    """
    
    def __init__(
        self,
        source_paths: List[Path],
        include_patterns: List[str],
        exclude_patterns: Optional[List[str]] = None,
        max_file_size_mb: int = 10
    ):
        """Initialize file discovery.
        
        Args:
            source_paths: Base directories to search
            include_patterns: Glob patterns to include (e.g., "**.py")
            exclude_patterns: Patterns to exclude (e.g., "**/test_*.py")
            max_file_size_mb: Skip files larger than this
        """
        self.source_paths = source_paths
        self.include_patterns = include_patterns
        self.exclude_patterns = exclude_patterns or []
        self.max_file_size = max_file_size_mb * 1024 * 1024
    
    def discover(self) -> List[Path]:
        """Discover all matching files.
        
        Returns:
            List of file paths
        """
        discovered: Set[Path] = set()
        
        for source_path in self.source_paths:
            if not source_path.exists():
                logger.warning("Source path does not exist: %s", source_path)
                continue
            
            for pattern in self.include_patterns:
                for file_path in source_path.glob(pattern):
                    if not file_path.is_file():
                        continue
                    
                    # Check size
                    if file_path.stat().st_size > self.max_file_size:
                        logger.debug("Skipping large file: %s", file_path)
                        continue
                    
                    # Check exclude patterns
                    if self._should_exclude(file_path):
                        continue
                    
                    discovered.add(file_path)
        
        logger.info("Discovered %d files", len(discovered))
        return sorted(discovered)
    
    def _should_exclude(self, file_path: Path) -> bool:
        """Check if file matches exclude patterns.
        
        Args:
            file_path: File to check
            
        Returns:
            True if should be excluded
        """
        path_str = str(file_path)
        
        for pattern in self.exclude_patterns:
            # Simple wildcard matching (can be enhanced with fnmatch)
            if pattern in path_str:
                return True
        
        return False
```

### Utility Module Organization

```
subsystems/rag/
├── utils/                         # Shared utilities (NEW)
│   ├── __init__.py                # Export all utilities
│   ├── lancedb_helpers.py         # LanceDB connection/models
│   ├── duckdb_helpers.py          # DuckDB connection
│   ├── file_tracker.py            # Change detection
│   ├── file_discovery.py          # File discovery
│   └── corruption_detector.py     # Corruption patterns (from earlier section)
├── lock_manager.py                # File locking (from earlier section)
├── base.py                        # BaseIndex interface
├── index_manager.py               # Orchestrator
├── watcher.py                     # File watching
├── standards/                     # Uses ALL utilities
│   ├── __init__.py
│   ├── container.py               # Uses lancedb_helpers, file_tracker, lock_manager
│   └── semantic.py
├── code/                          # Uses ALL utilities
│   ├── __init__.py
│   ├── container.py               # Uses lancedb_helpers, duckdb_helpers, file_tracker, lock_manager
│   ├── semantic.py                # Uses lancedb_helpers
│   └── graph.py                   # Uses duckdb_helpers
└── ...
```

### Benefits

1. **DRY**: Write once, use everywhere
2. **Consistency**: Same error handling, logging patterns
3. **Testability**: Test utilities once, all indexes benefit
4. **Maintainability**: Fix bugs in one place
5. **Discoverability**: Clear `utils/` directory for common code

### Before/After Comparison

**Before (current Ouroboros):**

```python
# standards_index.py: 127 lines of boilerplate
def _ensure_db(self): ...        # 18 lines
def _ensure_table(self): ...     # 12 lines
def _ensure_embedding(self): ... # 22 lines

# code_index.py: 127 lines of DUPLICATE boilerplate
def _ensure_db(self): ...        # 18 lines (DUPLICATE)
def _ensure_table(self): ...     # 12 lines (DUPLICATE)
def _ensure_embedding(self): ... # 22 lines (DUPLICATE)

# Total: 254 lines across 2 files
```

**After (with utilities):**

```python
# utils/lancedb_helpers.py: 150 lines (ONCE)
class LanceDBConnection: ...
class EmbeddingModelLoader: ...
class RerankerLoader: ...

# standards_index.py: 20 lines (uses utilities)
def _ensure_table(self):
    self._table = self.lancedb.open_table("standards")

def _ensure_embedding(self):
    self._embedding = EmbeddingModelLoader.load(self.config.vector.model)

# code_index.py: 20 lines (uses utilities)
# Same pattern, NO DUPLICATION

# Total: 190 lines (vs 254), scales to 4+ indexes with NO additional duplication
```

### Implementation Priority

1. **High Priority** (blocks refactor):
   - `IndexLockManager` (prevents corruption)
   - `LanceDBConnection` (used by standards + code + 2 future indexes)
   - `EmbeddingModelLoader` (used by standards + code + 2 future indexes)

2. **Medium Priority** (nice to have):
   - `DuckDBConnection` (used by graph + ast)
   - `FileChangeTracker` (incremental updates)
   - `FileDiscovery` (file discovery)

3. **Low Priority** (optional):
   - `RerankerLoader` (optional feature)
   - Corruption detection helpers (already in design, not urgent)

---

## Incremental Update Flow

### File Watcher → IndexManager → Index

```
File Change Detected (watcher.py)
    ↓
FileWatcher.on_file_event(event)
    ├─> Debounce (500ms window)
    ├─> Map path → affected indexes
    │   Example: "ouroboros/server.py" → ["code"]
    │            "standards/dev/x.md" → ["standards"]
    └─> For each affected index:
        └─> IndexManager.update_from_watcher(index_name, [file_path])
            └─> index.update([file_path])
                └─> Submodule handles incremental update
```

### Path Mapping (FileWatcher Configuration)

```python
# watcher.py

PATH_MAPPINGS = {
    "standards/": ["standards"],
    "ouroboros/": ["code"],
    "docs/": ["project_docs"],
    ".praxis-os/dependency_docs/": ["dependency_docs"],
}

# When ouroboros/server.py changes:
# 1. FileWatcher detects change
# 2. Maps "ouroboros/" → ["code"]
# 3. Calls IndexManager.update_from_watcher("code", [Path("ouroboros/server.py")])
# 4. IndexManager delegates to code.update([Path("ouroboros/server.py")])
# 5. CodeIndex updates both sub-indexes:
#    - semantic: Re-chunk file, update vectors (LanceDB)
#    - graph: Re-parse AST + update call graph (DuckDB)
```

### Index Update Implementation (Per Submodule)

```python
# Example: code/__init__.py

class CodeIndex(BaseIndex):
    def update(self, changed_files: List[Path]) -> None:
        """Incrementally update all sub-indexes."""
        
        logger.info("Updating code index for %d files", len(changed_files))
        
        # Update all 3 in parallel (order doesn't matter)
        try:
            # Semantic: Re-chunk and re-index vectors
            self.semantic.update(changed_files)
            
            # AST: Re-parse and update nodes
            self.ast.update(changed_files)
            
            # Graph: Re-analyze calls and update relationships
            self.graph.update(changed_files)
            
            logger.info("✅ Code index updated for %d files", len(changed_files))
            
        except Exception as e:
            logger.error("Failed to update code index: %s", e, exc_info=True)
            raise
```

---

## Submodule Internal Patterns

**Every submodule follows the same 3-file pattern:**

### Pattern 1: Simple Index (Single Implementation)

For indexes with straightforward requirements (e.g., standards, project_docs):

```python
# standards/__init__.py (Pure exports)
from .container import StandardsIndex

__all__ = ["StandardsIndex"]

# standards/container.py (Interface with IndexManager)
from ouroboros.subsystems.rag.base import BaseIndex, HealthStatus, SearchResult
from .semantic import SemanticIndex

class StandardsIndex(BaseIndex):
    """Main interface for standards documentation search.
    
    Today: Simple delegation to semantic search.
    Tomorrow: Could add custom chunking, metadata extraction, etc.
    """
    
    def __init__(self, config, base_path):
        self.config = config
        self.base_path = base_path
        # Delegate to semantic implementation
        self.semantic = SemanticIndex(config, base_path)
    
    def build(self, source_paths, force=False):
        """Delegate to semantic index."""
        return self.semantic.build(source_paths, force)
    
    def search(self, query, n_results=5, filters=None):
        """Delegate to semantic index."""
        return self.semantic.search(query, n_results, filters)
    
    def update(self, changed_files):
        """Delegate to semantic index."""
        return self.semantic.update(changed_files)
    
    def health_check(self):
        """Delegate to semantic index."""
        return self.semantic.health_check()
    
    def get_stats(self):
        """Delegate to semantic index."""
        return self.semantic.get_stats()

# standards/semantic.py (Implementation)
class SemanticIndex:
    """LanceDB-based semantic search (vector + FTS).
    
    Internal implementation, not exposed to IndexManager.
    """
    
    def __init__(self, config, base_path):
        self.config = config
        self.base_path = base_path
        self._db = None
        self._table = None
        self._embedding_model = None
    
    def build(self, source_paths, force=False):
        # All build logic here
        pass
    
    def search(self, query, n_results=5, filters=None):
        # Hybrid search: vector + FTS + RRF
        pass
    
    # ... other methods
```

### Pattern 2: Complex Index (Multiple Implementations)

For indexes with multiple sub-components (e.g., code, dependency_docs):

```python
# code/__init__.py (Pure exports)
from .container import CodeIndex

__all__ = ["CodeIndex"]

# code/container.py (Interface with IndexManager)
from ouroboros.subsystems.rag.base import BaseIndex, HealthStatus, SearchResult
from .semantic import SemanticIndex
from .graph import GraphIndex

class CodeIndex(BaseIndex):
    """Main interface for code search.
    
    Orchestrates 2 sub-indexes (2 databases):
    - semantic: LanceDB (vector + FTS + scalar for semantic code search with metadata filtering)
    - graph: DuckDB (AST symbols + call graph traversal via recursive CTEs)
    """
    
    def __init__(self, config, base_path):
        self.config = config
        self.base_path = base_path
        
        # Initialize 2 sub-indexes (LanceDB + DuckDB)
        self.semantic = SemanticIndex(config.vector, config.fts, base_path)
        self.graph = GraphIndex(config.graph, base_path)
    
    def build(self, source_paths, force=False):
        """Build both sub-indexes."""
        self.semantic.build(source_paths, force)
        self.graph.build(source_paths, force)
    
    def search(self, query, n_results=5, filters=None):
        """Default action: semantic search (LanceDB)."""
        return self.semantic.search(query, n_results, filters)
    
    def search_ast(self, query, n_results=5, filters=None):
        """Structural search: query AST symbols (DuckDB)."""
        return self.graph.search_ast(query, n_results, filters)
    
    def find_callers(self, symbol_name, max_depth=10):
        """Graph traversal: who calls this symbol? (DuckDB recursive CTE)."""
        return self.graph.find_callers(symbol_name, max_depth)
    
    def find_dependencies(self, symbol_name, max_depth=10):
        """Graph traversal: what does this symbol call? (DuckDB recursive CTE)."""
        return self.graph.find_dependencies(symbol_name, max_depth)
    
    def update(self, changed_files):
        """Update both sub-indexes."""
        self.semantic.update(changed_files)
        self.graph.update(changed_files)
    
    def health_check(self):
        """Aggregate health from both sub-indexes."""
        semantic_health = self.semantic.health_check()
        graph_health = self.graph.health_check()
        
        all_healthy = semantic_health.healthy and graph_health.healthy
        
        if not all_healthy:
            return HealthStatus(
                healthy=False,
                message="One or more code sub-indexes unhealthy",
                details={
                    "semantic": semantic_health.model_dump(),
                    "graph": graph_health.model_dump()
                }
            )
        
        return HealthStatus(
            healthy=True,
            message=f"Code index operational",
            details={
                "semantic": semantic_health.model_dump(),
                "graph": graph_health.model_dump()
            }
        )
    
    def get_stats(self):
        """Aggregate stats from both sub-indexes."""
        return {
            "semantic": self.semantic.get_stats(),
            "graph": self.graph.get_stats(),
        }

# code/semantic.py (Implementation - Internal)
class SemanticIndex:
    """LanceDB-based semantic code search (vector + FTS + scalar).
    
    Internal implementation, not exposed to IndexManager.
    Stores code chunks with:
    - Embeddings for semantic similarity search (vector)
    - Full-text index for keyword matching (FTS)
    - Scalar indexes for metadata filtering (language, file_path, symbol_type)
    """
    # Implementation details...
    pass

# code/graph.py (Implementation - Internal)
class GraphIndex:
    """DuckDB-based AST + call graph (symbols + relationships + recursive CTEs).
    
    Internal implementation, not exposed to IndexManager.
    Handles:
    - AST symbol extraction (Tree-sitter)
    - Symbol storage (DuckDB tables: symbols, relationships)
    - Structural queries (search_ast)
    - Graph traversal (find_callers, find_dependencies, find_call_paths)
    """
    # Implementation details...
    pass
```

### Key Observations

**Uniform Discovery Pattern:**
1. **Want to understand an index?** → Open `<submodule>/container.py`
2. **See what it does?** → Check method signatures in container
3. **Need implementation details?** → Look at specific files (semantic.py, ast.py, etc.)

**Simple vs Complex = Same Structure:**
- Simple: `container.py` delegates to 1 file (`semantic.py` → LanceDB)
- Complex: `container.py` orchestrates 2 files (`semantic.py` → LanceDB, `graph.py` → DuckDB)
- Pattern is identical, only delegation complexity differs

**Database Usage (Consistent Pattern):**
- **LanceDB only**: Standards, Project Docs
  - Vector + FTS + Scalar (metadata filtering)
- **LanceDB + DuckDB**: Code
  - LanceDB: Semantic search (vector + FTS + scalar for code chunks)
  - DuckDB: Structural search (AST symbols + call graph relationships)
- **No SQLite**: All storage uses LanceDB and/or DuckDB

---

## Configuration Schema

```yaml
# config/mcp.yaml

indexes:
  # Simple index
  standards:
    source_paths:
      - "standards/"
    vector:
      model: "sentence-transformers/all-MiniLM-L6-v2"
      dimension: 384
      chunk_size: 800
      chunk_overlap: 100
    fts: {}
  
  # Complex index (container with 2 databases)
  code:
    source_paths:
      - "ouroboros/"
    languages:
      - "python"
    # Semantic search (LanceDB)
    vector:
      model: "sentence-transformers/all-MiniLM-L6-v2"
      dimension: 384
      chunk_size: 200
      chunk_overlap: 20
    fts: {}
    # AST + Graph traversal (DuckDB)
    graph:
      max_depth: 10
      duckdb_path: ".cache/code.duckdb"
      ast:
        auto_install_parsers: true
        venv_path: "venv/"
  
  # Future: Simple index
  project_docs:
    source_paths:
      - "docs/"
      - "README.md"
    vector: { ... }
    fts: {}
  
  # Future: Complex index
  dependency_docs:
    libraries:
      - name: "lancedb"
        version: "0.13.0"
        docs_url: "https://lancedb.github.io/lancedb/"
      - name: "duckdb"
        version: "0.9.2"
        docs_url: "https://duckdb.org/docs/"
    vector: { ... }
    versioning:
      track_changes: true
      auto_update: false
  
  # File watcher
  file_watcher:
    enabled: true
    debounce_ms: 500
```

---

## Registry-Based Initialization

IndexManager uses a registry to discover and initialize submodules:

```python
# index_manager.py

INDEX_REGISTRY = {
    "standards": (
        "ouroboros.subsystems.rag.standards",
        "StandardsIndex",
        "Standards documentation index"
    ),
    "code": (
        "ouroboros.subsystems.rag.code",
        "CodeIndex",
        "Code semantic + structural + graph index"
    ),
    "project_docs": (
        "ouroboros.subsystems.rag.project_docs",
        "ProjectDocsIndex",
        "Local project documentation index"
    ),
    "dependency_docs": (
        "ouroboros.subsystems.rag.dependency_docs",
        "DependencyDocsIndex",
        "External dependency documentation index"
    ),
}

def _init_indexes(self):
    """Initialize all configured indexes dynamically."""
    for index_name, (module_path, class_name, description) in INDEX_REGISTRY.items():
        # Check if configured
        if not hasattr(self.config, index_name):
            continue
        
        index_config = getattr(self.config, index_name)
        if not index_config:
            continue
        
        # Dynamic import
        try:
            module = __import__(module_path, fromlist=[class_name])
            index_class = getattr(module, class_name)
            
            # Instantiate with standard args
            self._indexes[index_name] = index_class(
                config=index_config,
                base_path=self.base_path
            )
            logger.info("✅ %s initialized: %s", class_name, description)
            
        except ImportError as e:
            logger.warning("%s not available: %s", class_name, e)
        except Exception as e:
            logger.error("Failed to initialize %s: %s", class_name, e)
```

---

## Migration Path

### Phase 1: Refactor Existing (standards, code)

**Step 1: Create submodule directories**
```bash
mkdir -p ouroboros/subsystems/rag/standards
mkdir -p ouroboros/subsystems/rag/code
```

**Step 2: Migrate standards index**
```bash
# Create structure
touch ouroboros/subsystems/rag/standards/__init__.py
touch ouroboros/subsystems/rag/standards/container.py

# Move implementation
mv ouroboros/subsystems/rag/standards_index.py \
   ouroboros/subsystems/rag/standards/semantic.py

# Update standards/__init__.py
echo 'from .container import StandardsIndex\n__all__ = ["StandardsIndex"]' > \
   ouroboros/subsystems/rag/standards/__init__.py

# Create container (copy StandardsIndex class from semantic.py, make it delegate)
```

**Step 3: Migrate code index (complex - 2 databases)**
```bash
# Create structure
touch ouroboros/subsystems/rag/code/__init__.py
touch ouroboros/subsystems/rag/code/container.py

# Move implementations (2 files only, NO SQLite)
mv ouroboros/subsystems/rag/code_index.py \
   ouroboros/subsystems/rag/code/semantic.py

# Merge ast_index.py + graph_index.py into single graph.py (DuckDB handles both)
# graph.py will contain:
# - AST symbol extraction (Tree-sitter → DuckDB symbols table)
# - Call graph relationships (DuckDB relationships table)
# - Recursive CTEs (find_callers, find_dependencies, find_call_paths)
cat ouroboros/subsystems/rag/ast_index.py \
    ouroboros/subsystems/rag/graph_index.py > \
    ouroboros/subsystems/rag/code/graph.py
# (Then manually merge/refactor to single DuckDB-based class)

# Update code/__init__.py
echo 'from .container import CodeIndex\n__all__ = ["CodeIndex"]' > \
   ouroboros/subsystems/rag/code/__init__.py

# Create container (new file that orchestrates semantic + graph)
```

**Step 4: Update IndexManager**
```python
# Old imports
from ouroboros.subsystems.rag.standards_index import StandardsIndex
from ouroboros.subsystems.rag.code_index import CodeIndex
from ouroboros.subsystems.rag.ast_index import ASTIndex
from ouroboros.subsystems.rag.graph_index import GraphIndex

# New imports (cleaner!)
from ouroboros.subsystems.rag.standards import StandardsIndex
from ouroboros.subsystems.rag.code import CodeIndex

# INDEX_REGISTRY simplifies to:
INDEX_REGISTRY = {
    "standards": ("ouroboros.subsystems.rag.standards", "StandardsIndex"),
    "code": ("ouroboros.subsystems.rag.code", "CodeIndex"),
}
```

**Step 5: Update tools layer**
```python
# Old: Tools directly called ast/graph indexes (4 separate indexes)
index_manager._indexes["ast"].search(...)
index_manager._indexes["graph"].find_callers(...)

# New: Tools call through CodeIndex container (2 indexes only)
code_index = index_manager._indexes["code"]
code_index.search_ast(...)      # Container delegates to graph.search_ast() (DuckDB)
code_index.find_callers(...)    # Container delegates to graph.find_callers() (DuckDB)
```

**Step 6: Remove IndexManager special cases**
```python
# Old: IndexManager had special logic for ast/graph "nested" indexes
if index_name in ("graph", "ast") and hasattr(self.config, "code"):
    # Special handling to get source_paths from parent...
# Old: IndexManager tracked 4 indexes (standards, code, ast, graph)

# New: No special cases! Only 2 indexes (standards, code)
# Code index internally handles its 2 sub-components (semantic + graph)
# IndexManager just calls: code_index.build(source_paths)
```

### Phase 2: Add New Indexes (project_docs, dependency_docs)

**Following the established pattern:**

1. **Create submodule:**
   ```bash
   mkdir -p ouroboros/subsystems/rag/project_docs
   touch ouroboros/subsystems/rag/project_docs/__init__.py
   touch ouroboros/subsystems/rag/project_docs/container.py
   touch ouroboros/subsystems/rag/project_docs/semantic.py
   ```

2. **Add to registry:**
   ```python
   INDEX_REGISTRY = {
       "standards": ("ouroboros.subsystems.rag.standards", "StandardsIndex"),
       "code": ("ouroboros.subsystems.rag.code", "CodeIndex"),
       "project_docs": ("ouroboros.subsystems.rag.project_docs", "ProjectDocsIndex"),  # ← New
   }
   ```

3. **Add config schema** (already config-driven!)

4. **IndexManager automatically discovers and initializes** (no code changes needed!)

---

## Benefits

### 1. **Uniform Discovery Pattern**
- **Every submodule has `container.py`** = predictable entry point
- AI/human always knows where to look first
- No guessing "is the main class in `__init__.py` or elsewhere?"
- Consistent pattern across simple and complex indexes

### 2. **Uniform Interface**
- IndexManager treats all indexes identically
- No special cases for "nested" indexes (now hidden in container)
- Simple vs complex = same interface, different internal implementation

### 3. **Loose Coupling**
- IndexManager couples to submodule interface (`container.py`), never internals
- Submodules can refactor internally without breaking IndexManager
- Implementation files (semantic.py, ast.py) completely hidden

### 4. **Internal Freedom**
- Simple indexes: `container.py` delegates to 1 file (`semantic.py`)
- Complex indexes: `container.py` orchestrates N files (semantic + ast + graph)
- Each optimized for its use case, but same structure

### 5. **Independent Evolution**
- Add new indexes without modifying IndexManager
- Modify existing indexes without affecting others
- Standards can grow complex internally without changing interface
- Clear ownership boundaries

### 6. **Scalability**
- Easy to add: `project_docs/`, `dependency_docs/`, etc.
- Registry pattern handles discovery
- Config-driven initialization
- Pattern scales to any number of indexes

---

## Anti-Patterns to Avoid

### ❌ Bypassing the container
```python
# BAD: IndexManager importing implementation directly
from ouroboros.subsystems.rag.code.semantic import SemanticIndex
semantic = SemanticIndex(...)  # Bypasses container.py interface!

# BAD: Tools calling implementation directly
index_manager._indexes["code"].semantic.search(...)  # Bypasses CodeIndex interface!
```

### ❌ Implementation code in `__init__.py`
```python
# BAD: standards/__init__.py
class StandardsIndex(BaseIndex):
    def __init__(self, config, base_path):
        # 500 lines of implementation code here
        pass

# GOOD: standards/__init__.py (pure export)
from .container import StandardsIndex
__all__ = ["StandardsIndex"]
```

### ❌ Cross-submodule dependencies
```python
# BAD: code/container.py
from ouroboros.subsystems.rag.standards import StandardsIndex
# Code index should never depend on standards index

# GOOD: Each submodule is independent
# If cross-index query needed, IndexManager orchestrates it
```

### ❌ Shared state between submodules
```python
# BAD: Global shared cache between indexes
_SHARED_CACHE = {}  # standards and code both use this

# GOOD: Each submodule owns its state
# If sharing needed, pass via dependency injection
```

### ❌ Inconsistent file structure
```python
# BAD: One index has container.py, another doesn't
standards/
├── __init__.py
└── container.py  # Has container

project_docs/
└── __init__.py   # No container, code directly here

# GOOD: All indexes follow same pattern
standards/
├── __init__.py
├── container.py
└── semantic.py

project_docs/
├── __init__.py
├── container.py  # Always has container
└── semantic.py
```

### ✅ Correct patterns
```python
# GOOD: IndexManager imports from submodule root
from ouroboros.subsystems.rag.code import CodeIndex
# (Resolves to code/__init__.py → code/container.py)

# GOOD: Submodule internals completely hidden
code_index = CodeIndex(config, base_path)
# IndexManager doesn't know about semantic/ast/graph

# GOOD: Tools call through container methods
code_index.search_ast(...)      # Container delegates to ast.py
code_index.find_callers(...)    # Container delegates to graph.py

# GOOD: Submodules are independent
# Each has its own state, no shared globals
# Each follows same structure (container + implementations)
```

---

## Open Questions

1. **Should IndexManager expose stats for sub-indexes?**
   - Option A: `get_stats("code")` returns aggregate
   - Option B: `get_stats("code.semantic")` allows drilling down
   - **Recommendation**: Option A (keep internals hidden)

2. **How to handle cross-index queries?**
   - Example: "Search standards AND code"
   - **Recommendation**: New action `search_all` that queries multiple indexes and merges results

3. **Should submodules share embedding models?**
   - Saves memory if same model
   - **Recommendation**: Yes, but via dependency injection from IndexManager, not shared global

---

## Success Criteria

- ✅ All indexes are submodules with uniform interface
- ✅ IndexManager has <10 lines of index-specific logic
- ✅ Adding new index = create submodule + add to registry + config
- ✅ Submodule internals can change without affecting IndexManager
- ✅ File watcher updates work through IndexManager delegation
- ✅ All existing tests pass after refactoring

---

## References

- **Clean Architecture**: Uncle Bob's layered architecture (high-level depends on abstraction)
- **Dependency Inversion**: SOLID principle (depend on abstractions, not concretions)
- **Plugin Architecture**: Registry pattern for dynamic discovery
- **Container Pattern**: Composite object managing sub-components

