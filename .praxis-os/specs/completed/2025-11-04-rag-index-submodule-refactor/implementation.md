# Implementation Guidance

**Project:** RAG Index Submodule Refactor  
**Date:** 2025-11-04

---

## 1. Implementation Philosophy

**Core Principles:**
1. **Quality-First Development**: Write tests alongside implementation, not after
2. **Incremental Integration**: Complete Phase 0 (foundation) before any index implementation
3. **Pattern Validation**: Use Phase 1 (simple index) to validate pattern before Phase 2 (complex index)
4. **Fail-Fast with Gates**: Stop at validation gates until all criteria pass
5. **Copy-Paste-Adapt**: Use supporting doc code examples as starting point (verified working code)

**Development Model:**
- Test-driven where beneficial (foundation components, critical logic)
- Integration testing for each phase before advancing
- No phase skipping (gates enforce this)
- Document WHY not just WHAT (comments explain rationale)

---

## 2. Implementation Order

**Follow tasks.md Phase Sequence:**
```
Phase 0 (Foundation) → Phase 1 (Standards) → Phase 2 (Code) → Phase 3 (IndexManager) → Phase 4 (Testing)
```

**Critical Path:**
- Foundation utilities MUST work before any index
- Standards index validates pattern before code index
- Code index MUST complete before IndexManager refactor
- IndexManager integration MUST work before final testing

---

## 3. Code Patterns

### Pattern 1: Abstract Base Class (BaseIndex Interface)

**Purpose:** Define uniform contract for all indexes

**Code Example (COPIED from supporting doc):**
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
    content_type: str
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
        """Build index from source paths."""
        pass
    
    @abstractmethod
    def search(
        self,
        query: str,
        n_results: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search the index."""
        pass
    
    @abstractmethod
    def update(self, changed_files: List[Path]) -> None:
        """Incrementally update index for changed files."""
        pass
    
    @abstractmethod
    def health_check(self) -> HealthStatus:
        """Check if index is operational."""
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        pass
```

**Used in:** All index implementations (Phase 1, 2, 3)

**Key Points:**
- Use Python ABC (Abstract Base Class) to enforce contract
- All methods are @abstractmethod (must be implemented)
- Pydantic models for data validation
- Type hints on all methods

**❌ Anti-Pattern:**
```python
# BAD: No abstract base class, duck typing only
class StandardsIndex:
    def search(self, query):  # No contract enforcement
        pass
```

---

### Pattern 2: Simple Submodule (Single Database)

**Purpose:** Organize simple indexes (LanceDB only)

**Code Example (COPIED from supporting doc):**
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

**Used in:** Phase 1 (standards index), future project_docs index

**Key Pattern Structure:**
1. **`__init__.py`**: Pure exports (no logic)
2. **`container.py`**: Implements BaseIndex, delegates to internal implementation
3. **`semantic.py`**: Internal implementation (hidden from IndexManager)

**✅ Correct Import:**
```python
# GOOD: Import from submodule root
from ouroboros.subsystems.rag.standards import StandardsIndex
```

**❌ Anti-Pattern:**
```python
# BAD: Import internal implementation directly
from ouroboros.subsystems.rag.standards.semantic import SemanticIndex
```

---

### Pattern 3: Complex Submodule (Multiple Databases)

**Purpose:** Organize complex indexes (LanceDB + DuckDB)

**Code Example (COPIED from supporting doc):**
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
```

**Used in:** Phase 2 (code index)

**Key Pattern Features:**
- **Orchestration**: Container manages 2 sub-indexes
- **Health Aggregation**: Combines health from both databases
- **Extended Methods**: `search_ast()`, `find_callers()`, `find_dependencies()` beyond BaseIndex
- **Parallel Updates**: Both databases updated together

**❌ Anti-Pattern:**
```python
# BAD: Exposing sub-indexes to IndexManager
code_index.semantic.search(...)  # IndexManager should never access this
code_index.graph.find_callers(...)  # Use code_index.find_callers() instead
```

---

### Pattern 4: Utility Helpers (DRY Principle)

**Purpose:** Eliminate duplication across indexes

**Code Example (COPIED from supporting doc):**
```python
# subsystems/rag/utils/lancedb_helpers.py

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from ouroboros.utils.errors import ActionableError

logger = logging.getLogger(__name__)


class LanceDBConnection:
    """Manages LanceDB connection with lazy initialization."""
    
    def __init__(self, db_path: Path):
        """Initialize connection manager."""
        self.db_path = db_path
        self._db: Optional[Any] = None
    
    def connect(self) -> Any:
        """Get or create LanceDB connection (lazy initialization)."""
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
                    how_to_fix=f"Check that {self.db_path.parent} is writable"
                ) from e
        
        return self._db
    
    def open_table(self, table_name: str) -> Any:
        """Open table with error handling."""
        try:
            db = self.connect()
            table = db.open_table(table_name)
            logger.info("✅ Opened table: %s", table_name)
            return table
            
        except FileNotFoundError as e:
            raise ActionableError(
                what_failed=f"Open LanceDB table '{table_name}'",
                why_failed="Table does not exist",
                how_to_fix=f"Run build first: index.build(source_paths)"
            ) from e
        except Exception as e:
            raise ActionableError(
                what_failed=f"Open LanceDB table '{table_name}'",
                why_failed=str(e),
                how_to_fix="Check database integrity or rebuild"
            ) from e


class EmbeddingModelLoader:
    """Singleton embedding model loader with class-level cache."""
    
    _model_cache: Dict[str, Any] = {}
    
    @classmethod
    def load(cls, model_name: str) -> Any:
        """Load or retrieve cached embedding model."""
        if model_name not in cls._model_cache:
            try:
                from sentence_transformers import SentenceTransformer
                
                logger.info("Loading embedding model: %s", model_name)
                model = SentenceTransformer(model_name)
                cls._model_cache[model_name] = model
                logger.info("✅ Model loaded: %s", model_name)
                
            except ImportError as e:
                raise ActionableError(
                    what_failed="SentenceTransformer import",
                    why_failed="sentence-transformers package not installed",
                    how_to_fix="Install via: pip install sentence-transformers"
                ) from e
            except Exception as e:
                raise ActionableError(
                    what_failed=f"Load embedding model '{model_name}'",
                    why_failed=str(e),
                    how_to_fix="Check internet connection or use local model"
                ) from e
        
        return cls._model_cache[model_name]
```

**Used in:** All indexes (standards, code)

**Key Benefits:**
- **Lazy Initialization**: Connect only when needed
- **Caching**: Model loaded once, reused across indexes
- **Error Handling**: ActionableError with fix guidance
- **Logging**: Consistent log messages

**Usage in Container:**
```python
# standards/container.py
from ouroboros.subsystems.rag.utils.lancedb_helpers import (
    LanceDBConnection,
    EmbeddingModelLoader
)

class StandardsIndex(BaseIndex):
    def __init__(self, config, base_path):
        self.lancedb = LanceDBConnection(base_path / ".cache" / "rag" / "standards")
        self._table = None
        self._embedding_model = None
    
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
```

---

### Pattern 5: Registry Pattern (Dynamic Discovery)

**Purpose:** Add indexes without modifying IndexManager

**Code Example (from specs.md):**
```python
# subsystems/rag/index_manager.py

INDEX_REGISTRY = {
    "standards": (
        "ouroboros.subsystems.rag.standards",
        "StandardsIndex",
        "Standards documentation search"
    ),
    "code": (
        "ouroboros.subsystems.rag.code",
        "CodeIndex",
        "Code semantic + structural + graph search"
    ),
    # Add new indexes here (no other code changes needed)
}

class IndexManager:
    def __init__(self, config, base_path):
        self._indexes: Dict[str, BaseIndex] = {}
        self._init_indexes()
    
    def _init_indexes(self):
        """Initialize all indexes from registry (dynamic import)."""
        for index_name, (module_path, class_name, description) in INDEX_REGISTRY.items():
            try:
                # Dynamic import
                module = __import__(module_path, fromlist=[class_name])
                index_class = getattr(module, class_name)
                
                # Get config for this index
                index_config = getattr(self.config, index_name, None)
                if not index_config:
                    logger.warning(f"No config for index '{index_name}', skipping")
                    continue
                
                # Instantiate
                self._indexes[index_name] = index_class(index_config, self.base_path)
                logger.info(f"✅ Initialized index: {index_name} - {description}")
                
            except Exception as e:
                logger.error(f"❌ Failed to initialize index '{index_name}': {e}", exc_info=True)
```

**Used in:** Phase 3 (IndexManager refactor)

**Key Benefits:**
- **Scalable**: Add new index = add registry entry only
- **No Special Cases**: All indexes treated uniformly
- **Config-Driven**: Enabled via config, not code changes

**❌ Anti-Pattern:**
```python
# BAD: Hardcoded initialization
self._indexes["standards"] = StandardsIndex(config.standards, base_path)
self._indexes["code"] = CodeIndex(config.code, base_path)
# Must modify this code for every new index
```

---

### Pattern 6: Health Check with Aggregation

**Purpose:** Detect corruption and aggregate health from sub-indexes

**Code Example (from supporting doc):**
```python
# For complex indexes with multiple databases
def health_check(self) -> HealthStatus:
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
        message="Code index operational",
        details={
            "semantic": semantic_health.model_dump(),
            "graph": graph_health.model_dump()
        }
    )
```

**3-Tier Validation (from specs.md):**
1. **Tier 1 - Metadata**: Table exists, row count > 0
2. **Tier 2 - Functional**: Test queries work (vector, FTS, scalar)
3. **Tier 3 - Data Integrity**: Row count >= expected minimum

**Used in:** All indexes, IndexManager

---

## 4. Anti-Patterns to Avoid

### ❌ Anti-Pattern 1: Bypassing Container

```python
# BAD: IndexManager importing implementation directly
from ouroboros.subsystems.rag.code.semantic import SemanticIndex
semantic = SemanticIndex(...)  # Bypasses container!

# BAD: Tools calling implementation directly
index_manager._indexes["code"].semantic.search(...)  # Bypasses CodeIndex interface!
```

**Why Bad:** Breaks encapsulation, couples to internal implementation

**✅ Correct:**
```python
# GOOD: Import from submodule root
from ouroboros.subsystems.rag.code import CodeIndex
code_index = CodeIndex(...)

# GOOD: Call through container methods
code_index.search(...)  # Uses container interface
code_index.search_ast(...)  # Extended method, still through container
```

---

### ❌ Anti-Pattern 2: Implementation in `__init__.py`

```python
# BAD: standards/__init__.py with 500 lines of implementation
class StandardsIndex(BaseIndex):
    def __init__(self, config, base_path):
        # 500 lines of implementation code here
        pass
```

**Why Bad:** `__init__.py` should be pure exports only

**✅ Correct:**
```python
# GOOD: standards/__init__.py (pure export)
from .container import StandardsIndex
__all__ = ["StandardsIndex"]
```

---

### ❌ Anti-Pattern 3: Cross-Submodule Dependencies

```python
# BAD: code/container.py
from ouroboros.subsystems.rag.standards import StandardsIndex
# Code index should never depend on standards index
```

**Why Bad:** Creates tight coupling, violates independence

**✅ Correct:** Each submodule is independent. If cross-index query needed, IndexManager orchestrates it.

---

### ❌ Anti-Pattern 4: Shared Global State

```python
# BAD: Global shared cache between indexes
_SHARED_CACHE = {}  # standards and code both use this
```

**Why Bad:** Hidden coupling, hard to test, thread-safety issues

**✅ Correct:** Use dependency injection (pass shared resources via constructor) or class-level caches within utilities

---

## 5. Configuration Patterns

**YAML Configuration (from supporting doc):**
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
  
  # Complex index (2 databases)
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
      duckdb_path: ".cache/rag/code.duckdb"
      ast:
        auto_install_parsers: true
```

**Key Points:**
- Config-driven (not hardcoded)
- Each index gets its own section
- Vector config separate from graph config
- Sensible defaults

---

## 6. Testing Patterns

(Continued in next section)


---

## 6. Testing Strategy

### Coverage Target

- **Minimum:** 80% code coverage for new code
- **Foundation (Phase 0):** 90% (critical infrastructure)
- **Integration Tests:** Every phase must pass integration test before advancing

### Testing Pyramid

```
     /\
    /  \    E2E (End-to-End): 10%
   /    \   - Full workflow tests
  /------\  Integration: 30%
 /        \ - Component interactions
/          \ Unit: 60%
------------  - Individual functions/classes
```

---

### Unit Tests

**Purpose:** Test individual components in isolation

**Coverage:**
- Phase 0: BaseIndex, Lock Manager, Utilities
- Phase 1: Standards container, semantic implementation
- Phase 2: Code container, semantic, graph implementations
- Phase 3: IndexManager initialization, routing
- Phase 4: Full test suite execution

**Pattern (Arrange-Act-Assert):**
```python
# tests/ouroboros/subsystems/rag/test_base.py

import pytest
from ouroboros.subsystems.rag.base import BaseIndex, SearchResult, HealthStatus

def test_base_index_is_abstract():
    """Verify BaseIndex cannot be instantiated (ABC enforcement)."""
    # Arrange: Abstract class
    
    # Act & Assert: Cannot instantiate
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        BaseIndex()


def test_search_result_validation():
    """Verify SearchResult validates relevance_score bounds."""
    # Arrange: Valid data
    valid_result = {
        "content": "SOLID principles...",
        "file_path": "standards/solid.md",
        "relevance_score": 0.92,
        "content_type": "standard",
        "metadata": {}
    }
    
    # Act: Create SearchResult
    result = SearchResult(**valid_result)
    
    # Assert: Validation passed
    assert result.relevance_score == 0.92
    
    # Act & Assert: Out-of-bounds rejected
    invalid_result = {**valid_result, "relevance_score": 1.5}
    with pytest.raises(ValueError):
        SearchResult(**invalid_result)
```

**Test Organization:**
```
tests/ouroboros/subsystems/rag/
├── test_base.py              # BaseIndex, SearchResult, HealthStatus
├── test_lock_manager.py      # IndexLockManager (shared/exclusive locks)
├── test_utils.py             # Utilities (connection, model loading)
├── standards/
│   ├── test_container.py     # StandardsIndex (delegation, locks)
│   └── test_semantic.py      # SemanticIndex (build, search, health)
├── code/
│   ├── test_container.py     # CodeIndex (orchestration, aggregation)
│   ├── test_semantic.py      # SemanticIndex (LanceDB)
│   └── test_graph.py         # GraphIndex (DuckDB, recursive CTEs)
└── test_index_manager.py     # IndexManager (registry, routing)
```

---

### Integration Tests

**Purpose:** Test component interactions and end-to-end flows

**Scope:**
- Database interactions (LanceDB, DuckDB)
- Index build → search → update workflows
- Health check → auto-repair workflows
- IndexManager → submodule routing

**Pattern:**
```python
# tests/ouroboros/subsystems/rag/standards/test_integration.py

import pytest
from pathlib import Path
from ouroboros.subsystems.rag.standards import StandardsIndex

@pytest.fixture
def standards_index(tmp_path):
    """Create standards index with test config."""
    from ouroboros.config.schemas.indexes import StandardsConfig
    
    config = StandardsConfig(
        source_paths=[Path("tests/fixtures/standards/")],
        vector={"model": "sentence-transformers/all-MiniLM-L6-v2", "dimension": 384}
    )
    return StandardsIndex(config, tmp_path)


def test_standards_index_end_to_end(standards_index, tmp_path):
    """Test full workflow: build → search → update → health_check."""
    # Arrange: Test standards files (small subset for speed)
    test_files = [
        tmp_path / "test_standard.md"
    ]
    test_files[0].write_text("# SOLID Principles\n\nSOLID is an acronym...")
    
    # Act 1: Build index
    standards_index.build(test_files, force=True)
    
    # Assert 1: Health check passes
    health = standards_index.health_check()
    assert health.healthy is True
    assert "operational" in health.message.lower()
    
    # Act 2: Search
    results = standards_index.search("SOLID principles", n_results=5)
    
    # Assert 2: Results returned
    assert len(results) > 0
    assert results[0].relevance_score > 0.5
    assert "SOLID" in results[0].content
    
    # Act 3: Update (modify file)
    test_files[0].write_text("# SOLID Principles (Updated)\n\nSOLID principles are...")
    standards_index.update(test_files)
    
    # Assert 3: Updated content searchable
    updated_results = standards_index.search("SOLID principles", n_results=5)
    assert len(updated_results) > 0


def test_concurrent_lock_acquisition(standards_index):
    """Test lock manager prevents concurrent access."""
    import multiprocessing
    
    def try_build(index_path):
        """Attempt to build (will block if locked)."""
        from ouroboros.subsystems.rag.lock_manager import IndexLockManager
        lock_mgr = IndexLockManager("standards", index_path / ".cache/rag")
        acquired = lock_mgr.acquire_exclusive(blocking=False)
        return acquired
    
    # Act 1: Acquire exclusive lock in main process
    lock = standards_index.lock_manager
    assert lock.acquire_exclusive(blocking=False) is True
    
    # Act 2: Try to acquire from another process
    with multiprocessing.Pool(1) as pool:
        result = pool.apply(try_build, (standards_index.base_path,))
    
    # Assert: Second process blocked
    assert result is False
    
    # Cleanup
    lock.release()
```

---

### Mocking Strategy

**When to Mock:**
1. **External APIs**: Network calls (always mock in unit tests)
2. **Databases**: Mock in unit tests, use real DB in integration tests
3. **File I/O**: Mock for unit tests, use tmp_path fixture for integration
4. **Time/Dates**: Mock for deterministic tests
5. **Embedding Models**: Mock for fast tests (load real model in integration)

**When NOT to Mock:**
- Business logic (test actual implementation)
- Internal utilities (test real behavior)
- Critical paths (use integration tests with real dependencies)

**Mocking Examples:**
```python
# Unit test with mocking
def test_search_calls_embedding_model(mocker):
    """Verify search generates embeddings (mock model)."""
    # Arrange: Mock embedding model
    mock_model = mocker.Mock()
    mock_model.encode.return_value = [[0.1] * 384]
    mocker.patch("ouroboros.subsystems.rag.utils.lancedb_helpers.EmbeddingModelLoader.load", return_value=mock_model)
    
    # Arrange: Index
    index = StandardsIndex(config, base_path)
    
    # Act: Search
    index.search("test query")
    
    # Assert: Model called
    mock_model.encode.assert_called_once_with("test query")


# Integration test without mocking
def test_search_returns_relevant_results(standards_index):
    """Verify search returns relevant results (real model, real DB)."""
    # Arrange: Real index with real data
    standards_index.build(test_files, force=True)
    
    # Act: Real search
    results = standards_index.search("SOLID principles", n_results=5)
    
    # Assert: Real relevance
    assert results[0].relevance_score > 0.7  # High relevance expected
```

---

### Performance Tests

**Purpose:** Ensure performance targets met

**Benchmarks (from specs.md):**
```python
# tests/ouroboros/performance/test_benchmarks.py

import pytest
import time

def test_standards_build_performance(standards_index, benchmark_files):
    """Ensure standards build < 60s."""
    start = time.perf_counter()
    
    standards_index.build(benchmark_files, force=True)
    
    elapsed = time.perf_counter() - start
    assert elapsed < 60, f"Build took {elapsed}s, target is <60s"


def test_search_latency_p95(standards_index):
    """Ensure search p95 < 300ms."""
    standards_index.build(benchmark_files, force=True)
    
    durations = []
    for _ in range(100):
        start = time.perf_counter()
        standards_index.search("test query", n_results=5)
        durations.append(time.perf_counter() - start)
    
    p95 = sorted(durations)[94]  # 95th percentile
    assert p95 < 0.3, f"p95 latency {p95*1000}ms, target is <300ms"
```

---

### Testing Checklist (Per Phase)

**Phase 0 (Foundation):**
- [ ] `pytest tests/ouroboros/subsystems/rag/test_base.py` - All passing
- [ ] `pytest tests/ouroboros/subsystems/rag/test_lock_manager.py` - All passing
- [ ] `pytest tests/ouroboros/subsystems/rag/test_utils.py` - All passing
- [ ] Code coverage >= 90%
- [ ] Concurrent lock test passing

**Phase 1 (Standards):**
- [ ] `pytest tests/ouroboros/subsystems/rag/standards/` - All passing
- [ ] Integration test: build → search → update → health
- [ ] Lock integration verified
- [ ] Auto-repair test passing

**Phase 2 (Code):**
- [ ] `pytest tests/ouroboros/subsystems/rag/code/` - All passing
- [ ] Integration test: semantic + graph both functional
- [ ] Recursive CTEs tested (find_callers, find_dependencies)
- [ ] Health aggregation tested
- [ ] SQLite → DuckDB migration verified (row counts match)

**Phase 3 (IndexManager):**
- [ ] `pytest tests/ouroboros/integration/test_index_manager.py` - All passing
- [ ] Registry initialization tested
- [ ] All routing actions tested
- [ ] FileWatcher integration tested

**Phase 4 (Full Suite):**
- [ ] `pytest tests/ouroboros/` - 529+ tests passing
- [ ] Zero test failures
- [ ] Performance benchmarks meet targets
- [ ] Zero linter/mypy errors

---

### Continuous Testing

**During Development:**
```bash
# Run tests for current module
pytest tests/ouroboros/subsystems/rag/test_base.py -v

# Run tests with coverage
pytest tests/ouroboros/subsystems/rag/ --cov=ouroboros.subsystems.rag --cov-report=term

# Run only failed tests
pytest --lf

# Run tests matching pattern
pytest -k "test_lock"
```

**Pre-Commit:**
```bash
# Run linting
pylint ouroboros/subsystems/rag/

# Run type checking
mypy ouroboros/subsystems/rag/

# Run all tests
pytest tests/ouroboros/ -v
```

**CI/CD Pipeline:**
1. Linting (pylint, black)
2. Type checking (mypy)
3. Unit tests (fast)
4. Integration tests (slower)
5. Performance benchmarks (baseline comparison)

---

## 7. Deployment Guidance


### Deployment Context

**This is a refactoring project, not a greenfield deployment.**

- **Deployment Type:** In-place refactor of existing MCP server
- **Impact:** Local development environment (Cursor IDE)
- **Risk:** Medium (no production users, but breaks AI workflow if failed)
- **Rollback:** Straightforward (git revert, old files available)

---

### Pre-Deployment Preparation

**1. Backup Current State:**
```bash
# Backup cache directory (indexes)
cp -r .cache/rag/ .cache/rag.backup-$(date +%Y%m%d)

# Backup old Python files (before deletion in Phase 4)
mkdir -p .backup/old-indexes/
cp ouroboros/subsystems/rag/*_index.py .backup/old-indexes/
```

**2. Environment Setup:**
```bash
# Ensure dependencies installed
pip install -r requirements.txt

# Verify Python version
python --version  # Should be 3.10+

# Check disk space (.cache/rag/ will grow during migration)
df -h .cache/
```

**3. Run Pre-Deployment Tests:**
```bash
# Baseline test suite
pytest tests/ouroboros/ -v > test-results-before.txt

# Verify current system works
python -c "from ouroboros.subsystems.rag import index_manager; print('OK')"
```

---

### Deployment Steps (Phase-by-Phase)

**Phase 0: Deploy Foundation**
```bash
# 1. Implement foundation components
# (BaseIndex, Lock Manager, Utilities)

# 2. Run foundation tests
pytest tests/ouroboros/subsystems/rag/test_base.py \
       tests/ouroboros/subsystems/rag/test_lock_manager.py \
       tests/ouroboros/subsystems/rag/test_utils.py -v

# 3. Verify imports work
python -c "from ouroboros.subsystems.rag.base import BaseIndex; print('✅ Foundation OK')"

# 4. Commit (safe point)
git add ouroboros/subsystems/rag/base.py lock_manager.py utils/
git commit -m "Phase 0: Foundation components"
```

**Phase 1: Deploy Standards Index**
```bash
# 1. Create standards submodule
mkdir -p ouroboros/subsystems/rag/standards/

# 2. Implement standards index (container + semantic)

# 3. Run standards tests
pytest tests/ouroboros/subsystems/rag/standards/ -v

# 4. Verify old index still works
python -c "from ouroboros.subsystems.rag.standards_index import StandardsIndex; print('✅ Old still works')"

# 5. Verify new index works
python -c "from ouroboros.subsystems.rag.standards import StandardsIndex; print('✅ New works')"

# 6. Commit (safe point)
git add ouroboros/subsystems/rag/standards/
git commit -m "Phase 1: Standards index submodule"
```

**Phase 2: Deploy Code Index**
```bash
# 1. Create code submodule
mkdir -p ouroboros/subsystems/rag/code/

# 2. Implement code index (container + semantic + graph)

# 3. Migrate SQLite → DuckDB
python scripts/migrate_sqlite_to_duckdb.py

# 4. Run code tests
pytest tests/ouroboros/subsystems/rag/code/ -v

# 5. Verify old index still works
python -c "from ouroboros.subsystems.rag.code_index import CodeIndex; print('✅ Old still works')"

# 6. Verify new index works
python -c "from ouroboros.subsystems.rag.code import CodeIndex; print('✅ New works')"

# 7. Commit (safe point)
git add ouroboros/subsystems/rag/code/
git commit -m "Phase 2: Code index submodule"
```

**Phase 3: Deploy IndexManager Refactor**
```bash
# 1. Update IndexManager (registry pattern)

# 2. Update tools layer (pos_search_project.py)

# 3. Run integration tests
pytest tests/ouroboros/integration/test_index_manager.py -v

# 4. Restart MCP server (Cursor must restart)
# Close Cursor → wait 5s → reopen

# 5. Test end-to-end via tools
# Use pos_search_project tool calls in Cursor

# 6. Commit (safe point)
git add ouroboros/subsystems/rag/index_manager.py
git add ouroboros/tools/pos_search_project.py
git commit -m "Phase 3: IndexManager refactor"
```

**Phase 4: Final Deployment (Cleanup)**
```bash
# 1. Run full test suite
pytest tests/ouroboros/ -v > test-results-after.txt

# 2. Verify no regressions
diff test-results-before.txt test-results-after.txt

# 3. Run performance benchmarks
pytest tests/ouroboros/performance/test_benchmarks.py

# 4. Delete old files (POINT OF NO RETURN)
rm ouroboros/subsystems/rag/standards_index.py
rm ouroboros/subsystems/rag/code_index.py
rm ouroboros/subsystems/rag/ast_index.py
rm ouroboros/subsystems/rag/graph_index.py

# 5. Delete old SQLite databases (if migration successful)
rm .cache/rag/*.db

# 6. Final commit
git add -A
git commit -m "Phase 4: Cleanup old files"

# 7. Tag release
git tag -a v2.0-rag-refactor -m "RAG Index Submodule Refactor Complete"
```

---

### Environment Configuration

**No New Environment Variables Required**

This refactor uses existing configuration (`config/mcp.yaml`). No environment changes needed.

**Existing Config (Verify Present):**
```yaml
# config/mcp.yaml
indexes:
  standards:
    source_paths: ["standards/"]
    # ... (existing config)
  
  code:
    source_paths: ["ouroboros/"]
    # ... (existing config)
```

---

### Data Migration

**SQLite → DuckDB Migration (Phase 2)**

**Migration Script:**
```python
# scripts/migrate_sqlite_to_duckdb.py

import sqlite3
import duckdb
import csv
from pathlib import Path

def migrate_sqlite_to_duckdb():
    """Migrate AST data from SQLite to DuckDB."""
    sqlite_path = Path(".cache/rag/ast.db")
    duckdb_path = Path(".cache/rag/code.duckdb")
    
    # 1. Export SQLite to CSV
    print("Exporting SQLite to CSV...")
    sqlite_conn = sqlite3.connect(sqlite_path)
    
    # Export symbols
    symbols = sqlite_conn.execute("SELECT * FROM symbols").fetchall()
    with open("symbols.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(["symbol_id", "symbol_name", "symbol_type", "file_path", "line_start", "line_end", ...])
        writer.writerows(symbols)
    
    # Export relationships
    relationships = sqlite_conn.execute("SELECT * FROM relationships").fetchall()
    with open("relationships.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "caller_id", "called_id", "relationship_type", ...])
        writer.writerows(relationships)
    
    sqlite_conn.close()
    
    # 2. Import CSV to DuckDB
    print("Importing CSV to DuckDB...")
    duckdb_conn = duckdb.connect(str(duckdb_path))
    
    # Create tables (schema from specs.md)
    duckdb_conn.execute("""
        CREATE TABLE IF NOT EXISTS symbols (
            symbol_id VARCHAR PRIMARY KEY,
            symbol_name VARCHAR NOT NULL,
            symbol_type VARCHAR NOT NULL,
            file_path VARCHAR NOT NULL,
            line_start INTEGER NOT NULL,
            line_end INTEGER NOT NULL,
            ...
        )
    """)
    
    duckdb_conn.execute("""
        CREATE TABLE IF NOT EXISTS relationships (
            id INTEGER PRIMARY KEY,
            caller_id VARCHAR NOT NULL,
            called_id VARCHAR NOT NULL,
            relationship_type VARCHAR NOT NULL,
            ...
        )
    """)
    
    # Import CSV
    duckdb_conn.execute("COPY symbols FROM 'symbols.csv' (HEADER)")
    duckdb_conn.execute("COPY relationships FROM 'relationships.csv' (HEADER)")
    
    # 3. Verify row counts
    sqlite_count = len(symbols)
    duckdb_count = duckdb_conn.execute("SELECT COUNT(*) FROM symbols").fetchone()[0]
    
    print(f"SQLite symbols: {sqlite_count}")
    print(f"DuckDB symbols: {duckdb_count}")
    
    assert sqlite_count == duckdb_count, "Row count mismatch!"
    
    print("✅ Migration successful!")
    duckdb_conn.close()

if __name__ == "__main__":
    migrate_sqlite_to_duckdb()
```

**Migration Verification:**
```bash
# Run migration
python scripts/migrate_sqlite_to_duckdb.py

# Verify DuckDB functional
python -c "
import duckdb
conn = duckdb.connect('.cache/rag/code.duckdb')
result = conn.execute('SELECT COUNT(*) FROM symbols').fetchone()
print(f'✅ DuckDB has {result[0]} symbols')
"

# Test recursive CTEs
python -c "
from ouroboros.subsystems.rag.code import CodeIndex
code_index = CodeIndex(config, base_path)
callers = code_index.find_callers('IndexManager.__init__', max_depth=5)
print(f'✅ Found {len(callers)} callers')
"
```

---

### Rollback Strategy

**Scenario 1: Phase 0-2 Failure (Foundation or Index Implementation)**

**Impact:** New code doesn't work, old code still available

**Rollback:**
```bash
# 1. Revert commits
git revert HEAD~N  # N = number of commits to revert

# 2. Delete new directories
rm -rf ouroboros/subsystems/rag/standards/
rm -rf ouroboros/subsystems/rag/code/

# 3. Verify old code works
pytest tests/ouroboros/ -v

# 4. Restart Cursor
# Old system functional
```

**Time to Rollback:** < 5 minutes  
**Data Loss:** None (old indexes still in `.cache/rag/`)

---

**Scenario 2: Phase 3 Failure (IndexManager Integration)**

**Impact:** Tools don't route correctly, server won't start

**Rollback:**
```bash
# 1. Revert IndexManager changes
git checkout HEAD~1 -- ouroboros/subsystems/rag/index_manager.py
git checkout HEAD~1 -- ouroboros/tools/pos_search_project.py

# 2. Restart Cursor
# System uses old routing

# 3. Fix integration issues

# 4. Redeploy Phase 3
```

**Time to Rollback:** < 2 minutes  
**Data Loss:** None

---

**Scenario 3: Phase 4 Failure (Old Files Deleted)**

**Impact:** Regressions discovered after cleanup

**Rollback:**
```bash
# 1. Restore old files from backup
cp .backup/old-indexes/*.py ouroboros/subsystems/rag/

# 2. Revert IndexManager to use old imports
git checkout HEAD~2 -- ouroboros/subsystems/rag/index_manager.py

# 3. Restart Cursor

# 4. System functional with old files
```

**Time to Rollback:** < 5 minutes  
**Data Loss:** None (backups available)

---

### Deployment Checklist

**Pre-Deployment (Before Phase 0):**
- [ ] Backup `.cache/rag/` directory
- [ ] Backup old `*_index.py` files
- [ ] Baseline test suite run (`test-results-before.txt`)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Disk space sufficient (>1GB free)
- [ ] Git working directory clean

**Per-Phase Deployment:**
- [ ] Phase tests passing
- [ ] Old code still works (backward compatibility until Phase 4)
- [ ] New code works (forward compatibility)
- [ ] Commit to git (safe rollback point)
- [ ] Validation gate criteria met

**Post-Deployment (After Phase 4):**
- [ ] Full test suite passing (529+ tests)
- [ ] Performance benchmarks meet targets
- [ ] MCP server restarts without errors
- [ ] All search actions functional via tools
- [ ] Health checks work for both indexes
- [ ] Old files safely deleted
- [ ] Migration successful (SQLite → DuckDB)
- [ ] Documentation updated
- [ ] Git tagged (`v2.0-rag-refactor`)

**Verification Commands:**
```bash
# Test suite
pytest tests/ouroboros/ -v

# Linting
pylint ouroboros/subsystems/rag/
mypy ouroboros/subsystems/rag/

# Import verification
python -c "
from ouroboros.subsystems.rag.standards import StandardsIndex
from ouroboros.subsystems.rag.code import CodeIndex
from ouroboros.subsystems.rag import IndexManager
print('✅ All imports successful')
"

# End-to-end verification
# (Use pos_search_project tool in Cursor)
```

---

## 8. Troubleshooting Guide


### Common Issues

---

#### Issue 1: ModuleNotFoundError on Import

**Symptoms:**
```python
ModuleNotFoundError: No module named 'ouroboros.subsystems.rag.standards'
```

**Cause:**
- Missing `__init__.py` files in directory structure
- Python path not configured correctly
- Module not installed in editable mode

**Solution:**
```bash
# 1. Verify directory structure
ls -la ouroboros/subsystems/rag/standards/
# Should see: __init__.py, container.py, semantic.py

# 2. Check __init__.py exports
cat ouroboros/subsystems/rag/standards/__init__.py
# Should contain: from .container import StandardsIndex

# 3. Reinstall package in editable mode
pip install -e .

# 4. Verify import works
python -c "from ouroboros.subsystems.rag.standards import StandardsIndex; print('✅ OK')"
```

---

#### Issue 2: Lock Acquisition Failure

**Symptoms:**
```
IOError: Cannot acquire exclusive lock (held by PID 1234)
```

**Cause:**
- MCP server is running and holds lock
- Previous process crashed, lock not released
- Multiple processes trying to rebuild simultaneously

**Solution:**
```bash
# 1. Check if MCP server is running
ps aux | grep ouroboros

# 2. Close Cursor (stops MCP server)
# Wait 5 seconds for graceful shutdown

# 3. If lock file still exists, check PID
cat .cache/rag/.standards.lock
# If PID doesn't exist, lock is stale

# 4. Remove stale lock file
rm .cache/rag/.standards.lock
rm .cache/rag/.code.lock

# 5. Retry operation
```

**Prevention:**
- Always close Cursor before manual rebuild scripts
- Use `with lock_manager.exclusive_lock():` context manager (auto-cleanup)

---

#### Issue 3: LanceDB Corruption Detected

**Symptoms:**
```
RuntimeError: lance error: Invalid manifest at version 123
```

**Cause:**
- Concurrent writes corrupted index
- Process killed during write
- Disk full during write

**Solution:**
```bash
# 1. Check disk space
df -h .cache/

# 2. Delete corrupted index
rm -rf .cache/rag/standards/

# 3. Rebuild from source
python -c "
from ouroboros.subsystems.rag.standards import StandardsIndex
index = StandardsIndex(config, base_path)
index.build(source_paths, force=True)
print('✅ Rebuilt')
"

# 4. Verify health
python -c "
index = StandardsIndex(config, base_path)
health = index.health_check()
assert health.healthy
print('✅ Healthy')
"
```

**Prevention:**
- Use lock manager (Phase 0 implementation)
- Ensure sufficient disk space (>1GB)
- Don't kill processes during index build

---

#### Issue 4: DuckDB Migration Row Count Mismatch

**Symptoms:**
```
AssertionError: Row count mismatch! SQLite: 1500, DuckDB: 1450
```

**Cause:**
- CSV export/import truncated data
- Schema mismatch between SQLite and DuckDB
- Special characters in data not escaped

**Solution:**
```bash
# 1. Check CSV files
wc -l symbols.csv relationships.csv
# Should match SQLite row counts

# 2. Check for data issues
grep -n "," symbols.csv | head -20
# Look for unescaped quotes, newlines in fields

# 3. Re-export with proper escaping
python -c "
import sqlite3
import csv
conn = sqlite3.connect('.cache/rag/ast.db')
with open('symbols.csv', 'w', newline='') as f:
    writer = csv.writer(f, quoting=csv.QUOTE_ALL)  # Quote all fields
    writer.writerows(conn.execute('SELECT * FROM symbols'))
"

# 4. Re-import to DuckDB
python scripts/migrate_sqlite_to_duckdb.py

# 5. Verify row counts
python -c "
import sqlite3, duckdb
sqlite_count = len(sqlite3.connect('.cache/rag/ast.db').execute('SELECT * FROM symbols').fetchall())
duckdb_count = duckdb.connect('.cache/rag/code.duckdb').execute('SELECT COUNT(*) FROM symbols').fetchone()[0]
assert sqlite_count == duckdb_count
print(f'✅ Counts match: {sqlite_count}')
"
```

**Alternative (If Migration Fails):**
- Skip migration, rebuild from source (reproducible)
```bash
rm .cache/rag/code.duckdb
python -c "
from ouroboros.subsystems.rag.code import CodeIndex
code_index = CodeIndex(config, base_path)
code_index.build(source_paths, force=True)
"
```

---

#### Issue 5: Import Circular Dependency

**Symptoms:**
```
ImportError: cannot import name 'BaseIndex' from partially initialized module
```

**Cause:**
- Circular imports between modules
- Container importing implementation, implementation importing container

**Solution:**
```bash
# 1. Check import order
# BAD (circular):
# base.py imports from container.py
# container.py imports from base.py

# 2. Fix import order
# GOOD:
# base.py: No imports from other rag modules
# container.py: Imports from base.py (one-way)
# semantic.py: No imports from container.py

# 3. Verify dependency graph
python -c "
import importlib
importlib.import_module('ouroboros.subsystems.rag.base')  # Should work
importlib.import_module('ouroboros.subsystems.rag.standards')  # Should work
"
```

**Prevention:**
- Base classes should have minimal dependencies
- Implementation files should not import containers
- Use type hints with `from __future__ import annotations` if needed

---

#### Issue 6: Pydantic Validation Error (Extra Fields)

**Symptoms:**
```
pydantic_core._pydantic_core.ValidationError: 1 validation error for SearchResult
extra_field
  Extra inputs are not permitted [type=extra_forbidden]
```

**Cause:**
- Pydantic model configured with `extra='forbid'`
- Data contains fields not in model schema
- SessionMapper adds `status` field internally

**Solution:**
```python
# Option 1: Remove extra fields before validation
data = {...}  # From database or JSON
data.pop("status", None)  # Remove internal fields
result = SearchResult(**data)

# Option 2: Change model config (less strict)
class SearchResult(BaseModel):
    model_config = ConfigDict(extra='ignore')  # Ignore extra fields
```

---

### Debugging Techniques

**1. Enable Debug Logging:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("ouroboros.subsystems.rag")
logger.setLevel(logging.DEBUG)

# Now all debug messages visible
```

**2. Interactive Debugging (pdb):**
```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use Python 3.7+ breakpoint()
breakpoint()

# Useful pdb commands:
# n - next line
# s - step into function
# c - continue
# p variable - print variable
# l - list code around current line
```

**3. Inspect LanceDB Table:**
```python
import lancedb

# Connect to database
db = lancedb.connect(".cache/rag/standards/")

# Open table
table = db.open_table("standards")

# Check schema
print(table.schema)

# Count rows
print(f"Rows: {table.count_rows()}")

# Sample data
sample = table.to_pandas().head(5)
print(sample)

# Check for corruption
try:
    table.search([0.1] * 384).limit(1).to_list()
    print("✅ Table functional")
except Exception as e:
    print(f"❌ Table corrupted: {e}")
```

**4. Inspect DuckDB Tables:**
```python
import duckdb

# Connect
conn = duckdb.connect(".cache/rag/code.duckdb")

# List tables
tables = conn.execute("SHOW TABLES").fetchall()
print(f"Tables: {tables}")

# Check schema
schema = conn.execute("DESCRIBE symbols").fetchall()
print(schema)

# Count rows
count = conn.execute("SELECT COUNT(*) FROM symbols").fetchone()[0]
print(f"Symbols: {count}")

# Sample data
sample = conn.execute("SELECT * FROM symbols LIMIT 5").fetchdf()
print(sample)

# Test recursive CTE
callers = conn.execute("""
WITH RECURSIVE callers AS (
    SELECT caller_id FROM relationships WHERE called_id = 'test_symbol'
)
SELECT * FROM callers
""").fetchall()
print(f"Callers: {len(callers)}")
```

**5. Profile Performance:**
```python
import cProfile
import pstats

# Profile function
profiler = cProfile.Profile()
profiler.enable()

index.search("test query", n_results=5)

profiler.disable()

# Print stats
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 slowest
```

**6. Memory Profiling:**
```python
import tracemalloc

# Start tracing
tracemalloc.start()

# Run operation
index.build(source_paths, force=True)

# Get memory usage
current, peak = tracemalloc.get_traced_memory()
print(f"Current: {current / 1024 / 1024:.2f} MB")
print(f"Peak: {peak / 1024 / 1024:.2f} MB")

tracemalloc.stop()
```

---

### Performance Troubleshooting

#### Slow Index Build

**Symptoms:** Build takes > 120s (code) or > 60s (standards)

**Diagnosis:**
```python
import time

start = time.perf_counter()
index.build(source_paths, force=True)
elapsed = time.perf_counter() - start
print(f"Build took {elapsed:.2f}s")
```

**Common Causes & Solutions:**

1. **Disk I/O bottleneck:**
```bash
# Check disk I/O
iotop  # Linux
# If high I/O wait, use SSD or reduce concurrent writes
```

2. **Slow embedding generation:**
```python
# Profile embedding step
with cProfile.Profile() as pr:
    embeddings = model.encode(chunks, batch_size=32)
# Look for slow sentence-transformers calls

# Solution: Increase batch size or use GPU
model.encode(chunks, batch_size=64, show_progress_bar=True)
```

3. **Network latency (downloading model):**
```bash
# Pre-download model
python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
print('✅ Model cached')
"
```

#### Slow Search Queries

**Symptoms:** Search p95 > 300ms

**Diagnosis:**
```python
durations = []
for _ in range(100):
    start = time.perf_counter()
    index.search("test query", n_results=5)
    durations.append(time.perf_counter() - start)

p95 = sorted(durations)[94]
print(f"p95: {p95*1000:.2f}ms")
```

**Common Causes & Solutions:**

1. **Missing vector index:**
```python
# Check if IVF_PQ index exists
table = db.open_table("standards")
indices = table.list_indices()
print(f"Indices: {indices}")

# If missing, create
table.create_index(metric="cosine", num_partitions=256)
```

2. **Missing scalar indexes:**
```python
# Create scalar indexes
table.create_scalar_index("domain")
table.create_scalar_index("phase")
```

3. **Large result set:**
```python
# Reduce n_results
results = index.search(query, n_results=3)  # Instead of 10
```

---

### Getting Help

**Before Asking for Help, Gather:**
1. **Error message** (full traceback)
2. **Steps to reproduce**
3. **Environment info:**
```bash
python --version
pip list | grep -E "(lancedb|duckdb|sentence-transformers)"
du -sh .cache/rag/
```
4. **Relevant code** (minimal reproducible example)
5. **What you've tried** (debugging steps)

**Resources:**
- **Standards Documentation:** `.praxis-os/standards/` (query with pos_search_project)
- **Spec Files:** This directory (`2025-11-04-rag-index-submodule-refactor/`)
- **Test Examples:** `tests/ouroboros/subsystems/rag/` (working code patterns)
- **Supporting Doc:** `supporting-docs/rag-index-submodule-pattern.md` (original design)

**Reporting Format:**
```
**Issue:** Brief description

**Environment:**
- Python version: 3.10.x
- OS: macOS/Linux/Windows
- Relevant packages: lancedb==0.13.0, duckdb==0.9.0

**Steps to Reproduce:**
1. Step 1
2. Step 2

**Expected:** What should happen

**Actual:** What actually happened

**Error Message:**
```
[full traceback]
```

**What I've Tried:**
- Tried X, resulted in Y
- Checked Z, found W
```

---

## 9. Appendices

### A. Quick Reference

**Common Commands:**
```bash
# Run tests
pytest tests/ouroboros/subsystems/rag/ -v

# Check imports
python -c "from ouroboros.subsystems.rag.standards import StandardsIndex; print('OK')"

# Rebuild index
python -c "
from ouroboros.subsystems.rag.standards import StandardsIndex
index = StandardsIndex(config, base_path)
index.build(source_paths, force=True)
"

# Health check
python -c "
index = StandardsIndex(config, base_path)
health = index.health_check()
print(f'Healthy: {health.healthy}, Message: {health.message}')
"
```

**File Locations:**
- Foundation: `ouroboros/subsystems/rag/base.py`, `lock_manager.py`, `utils/`
- Standards: `ouroboros/subsystems/rag/standards/`
- Code: `ouroboros/subsystems/rag/code/`
- IndexManager: `ouroboros/subsystems/rag/index_manager.py`
- Tests: `tests/ouroboros/subsystems/rag/`
- Config: `config/mcp.yaml`
- Cache: `.cache/rag/`

---

### B. Implementation Checklist

**Foundation (Phase 0):**
- [ ] BaseIndex, SearchResult, HealthStatus implemented
- [ ] IndexLockManager functional
- [ ] Utility modules (lancedb_helpers, duckdb_helpers) implemented
- [ ] Phase 0 tests passing

**Standards Index (Phase 1):**
- [ ] Directory structure created
- [ ] Container delegates to semantic
- [ ] Semantic implementation functional
- [ ] Phase 1 tests passing

**Code Index (Phase 2):**
- [ ] Directory structure created
- [ ] Container orchestrates semantic + graph
- [ ] SemanticIndex (LanceDB) functional
- [ ] GraphIndex (DuckDB) functional
- [ ] SQLite → DuckDB migration successful
- [ ] Phase 2 tests passing

**IndexManager (Phase 3):**
- [ ] Registry pattern implemented
- [ ] Dynamic initialization functional
- [ ] Query routing updated
- [ ] Tools layer integrated
- [ ] Phase 3 tests passing

**Final (Phase 4):**
- [ ] Full test suite passing (529+ tests)
- [ ] Performance targets met
- [ ] Old files deleted
- [ ] Documentation updated
- [ ] System operational

---

**END OF IMPLEMENTATION GUIDANCE DOCUMENT**

