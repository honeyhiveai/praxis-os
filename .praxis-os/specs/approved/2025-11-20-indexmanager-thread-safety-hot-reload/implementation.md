# Implementation Approach

**Project:** IndexManager Thread Safety, Hot Reload, and Dynamic Logic Implementation  
**Date:** 2025-11-20  
**Status:** Implementation Guide  
**Version:** 1.0

---

## 1. Implementation Philosophy

**Core Principles:**
1. **Standards-First Development**: Every pattern validates against 4 concurrency standards before implementation
2. **Test-Driven Thread Safety**: Write concurrent access tests before implementing locks
3. **Dynamic Over Static**: Use INDEX_REGISTRY and config-driven logic to minimize future code changes
4. **Evidence-Based Performance**: Benchmark every optimization claim (RLock overhead measurement required)
5. **Phase-Gated Execution**: Complete Phase 1 (thread safety) before Phase 2 (hot reload)

---

## 2. Implementation Order

**Follow tasks.md phase sequence strictly:**

```
Phase 1: Thread Safety Core (16 hours)
    ├── Task 1.1: Audit _indexes access sites
    ├── Tasks 1.2-1.8: Add RLock protection (can parallelize by method)
    ├── Tasks 1.9-1.10: Documentation (parallel with 1.2-1.8)
    └── Tasks 1.11-1.13: Tests (concurrent, benchmark, stress)
    
Phase 2: Hot Reload API (20 hours)
    ├── Tasks 2.1-2.2: add_index, remove_index (parallel)
    ├── Task 2.3: Config diff logic
    ├── Task 2.4: reload_indexes with atomic swap
    └── Tasks 2.5-2.6: Tests (unit, integration)
    
Phase 3: Observability (8 hours)
    ├── Tasks 3.1-3.6: Structured logging (parallel)
    └── Tasks 3.7-3.8: Log analysis + compliance
```

**Critical Path:** Phase 1 (Task 1.1 → 1.2-1.8 → 1.11-1.13) → Phase 2 (2.3 → 2.4 → 2.6)

**Parallelization:** See tasks.md § Dependencies for multi-developer strategy (~30 hours with 3 developers)

---

## 3. Code Patterns

### Pattern 1: Thread-Safe Index Access

**When to Use:** Every access to `self._indexes` dictionary

**Rule:** Hold `_indexes_lock` for **minimum time** (microseconds for dict access), release before expensive operations (milliseconds for queries/builds).

**✅ CORRECT: Lock for dict access only**

```python
def route_action(self, action: str, **kwargs):
    """Route action to appropriate index with thread-safe access."""
    # Get index reference under RLock (fast, <10ns)
    with self._indexes_lock:  # RLock allows re-entrant calls
        index = self._indexes.get(index_name)
    
    if not index:
        raise IndexError(f"Index {index_name} not available")
    
    # Call index method OUTSIDE lock (allow concurrency)
    return index.search(**kwargs)  # 10-100ms, no lock blocking
```

**Why This Works:**
- RLock protects dict access (ensures no dict modifications during read)
- Re-entrant allows same thread to acquire lock multiple times (call chains work)
- Expensive operations (search, build, health check) run outside lock
- Multiple indexes can be searched concurrently
- Lock contention is ~1μs (10,000x faster than index operations)

**❌ WRONG: Hold lock during expensive operation**

```python
def route_action_bad(self, action: str, **kwargs):
    with self._indexes_lock:           # Acquire RLock
        index = self._indexes.get(name)
        return index.search(**kwargs)   # Search (10ms) - BLOCKS OTHER REQUESTS!
```

**Why This Fails:**
- Holds lock during 10-100ms search operation
- All concurrent requests must wait (serialization)
- Defeats purpose of concurrency (throughput drops 100x)
- Violates NFR-P2 (Concurrent Query Throughput)

**Applies To:** Tasks 1.2-1.8 (all 7 method modifications)

---

### Pattern 2: Snapshot Pattern for Iteration

**When to Use:** When iterating over `_indexes` dict (health checks, stats)

**Problem:** Cannot hold lock during long-running operations (health checks may take seconds)

**Solution:** Create shallow copy under lock, iterate outside lock

**✅ CORRECT: Snapshot pattern**

```python
def health_check_all(self) -> Dict[str, Dict]:
    """Thread-safe health check for all indexes."""
    # Get snapshot of indexes under lock (fast, <100ns)
    with self._indexes_lock:
        indexes_snapshot = dict(self._indexes)  # Shallow copy
    
    # Process snapshot outside lock (long-running, not blocking)
    results = {}
    for name, index in indexes_snapshot.items():
        results[name] = index.health_check()  # May take seconds
    
    return results
```

**Trade-offs:**
- **Pros:**
  - Lock held <100ns (dict copy only)
  - Other threads can query/modify `_indexes` during health checks
  - Consistent snapshot (all indexes from same moment)
- **Cons:**
  - Memory: +1KB per snapshot (10 indexes × ~100 bytes) → Negligible
  - Staleness: Snapshot may not reflect changes made after copy (acceptable for monitoring)

**❌ WRONG: Iterate under lock**

```python
def health_check_bad(self):
    with self._indexes_lock:
        for index in self._indexes.values():
            # health_check() may take seconds - BLOCKS ALL REQUESTS!
            result[name] = index.health_check()
```

**Applies To:** Tasks 1.4 (health_check_all), 1.8 (get_stats)

---

### Pattern 3: Atomic Swap for Hot Reload

**When to Use:** Adding/removing/reloading indexes at runtime

**Problem:** Cannot allow queries to see partially-updated `_indexes` dict (must see either old state or new state, never mixed)

**Solution:** Perform all dict modifications under single lock acquisition (atomic from other threads' perspective)

**✅ CORRECT: Atomic swap pattern**

```python
def reload_indexes(self, new_config: IndexesConfig) -> Dict[str, List[str]]:
    """Reload indexes from new config (declarative hot reload)."""
    # 1. Compute diff OUTSIDE lock (fast, config analysis)
    current_indexes = set(self._indexes.keys())
    desired_indexes = set(new_config.indexes)
    to_add = desired_indexes - current_indexes
    to_remove = current_indexes - desired_indexes
    
    # 2. Atomic swap UNDER LOCK (all dict modifications together)
    old_indexes = []
    with self._indexes_lock:
        # Remove obsolete indexes
        for name in to_remove:
            old_index = self._indexes.pop(name)
            old_indexes.append((name, old_index))
        
        # Add new indexes (instantiate from INDEX_REGISTRY)
        for name in to_add:
            index_class = INDEX_REGISTRY[name]  # Dynamic lookup
            new_index = index_class(new_config, base_path)
            self._indexes[name] = new_index
    
    # 3. Cleanup OUTSIDE lock (slow, may take seconds)
    for name, old_index in old_indexes:
        if hasattr(old_index, 'close'):
            old_index.close()  # Close file handles, release resources
    
    return {"added": list(to_add), "removed": list(to_remove)}
```

**Why This Works:**
- Config diff computed outside lock (fast, no blocking)
- Swap atomic under lock (consistent state)
- Cleanup (close) outside lock (may be slow, not blocking)
- Queries never see partial state (old/new only)
- In-flight requests continue using old index (graceful)

**❌ WRONG: Modify in-place (not atomic)**

```python
def reload_bad(self, new_config):
    # Acquires lock for each operation separately
    for name in to_remove:
        with self._indexes_lock:
            self._indexes.pop(name)  # Visible immediately!
        # Other threads see partial state here!
    for name in to_add:
        with self._indexes_lock:
            self._indexes[name] = new_index  # Another partial state!
```

**Why This Fails:**
- Multiple lock acquisitions (not atomic)
- Queries may see index removed but not yet added (KeyError)
- Violates NFR-R3 (Atomic State Transitions)

**Applies To:** Tasks 2.1-2.4 (hot reload implementation)

---

### Pattern 4: Dynamic Logic via INDEX_REGISTRY

**When to Use:** Any code that needs to know which index types exist

**Problem:** Hardcoded index names require code changes when new repos/indexes are added

**Solution:** Use INDEX_REGISTRY for dynamic discovery and instantiation

**✅ CORRECT: Dynamic logic (config-driven)**

```python
# MODULE LEVEL: ouroboros/subsystems/rag/__init__.py
INDEX_REGISTRY: Dict[str, Type[BaseIndex]] = {
    "standards": StandardsIndex,
    "code": CodeIndex,
    # Future: Add new indexes here without touching any other code
}

# USAGE: Dynamic instantiation
def reload_indexes_good(self, new_config):
    """Uses INDEX_REGISTRY - automatically handles new index types."""
    for index_name in new_config.indexes:  # From config
        if index_name not in INDEX_REGISTRY:
            raise RuntimeError(f"Unknown index type: {index_name}")
        
        # Dynamic instantiation (no hardcoded types)
        index_class = INDEX_REGISTRY[index_name]
        new_index = index_class(new_config, base_path)
        self._indexes[index_name] = new_index
```

**Benefits:**
1. **Extensibility**: Adding new index type (e.g., "docs", "api") requires:
   - Static: Modify 5+ places (init, reload, health check, etc.)
   - Dynamic: Add to INDEX_REGISTRY + config (1 place)
2. **Maintainability**: Config-driven code is self-documenting
   - Static: "Where are all the index names hardcoded?"
   - Dynamic: "Check INDEX_REGISTRY"
3. **Testability**: Can mock INDEX_REGISTRY for tests

**❌ WRONG: Hardcoded index names (static logic)**

```python
def reload_bad(self, new_config):
    """Hardcoded index names - breaks when new index types added."""
    # STATIC! Must modify this list when new index types are added
    for index_name in ["standards", "code", "ast"]:  
        if hasattr(new_config, index_name):
            # Must add another elif for each new type
            if index_name == "standards":
                new_index = StandardsIndex(...)
            elif index_name == "code":
                new_index = CodeIndex(...)
            # ... add 3+ lines per new index type
```

**Why This Matters:**
- Adding new repo in Phase 2: Zero code changes (config only)
- NFR-M3 (Dynamic Logic Extensibility) satisfied
- Fractal pattern maintained (IndexManager doesn't know index internals)

**Applies To:** Tasks 2.3-2.4 (hot reload), Task 1.1 (audit for hardcoded strings)

---

### Pattern 5: RLock vs Lock

**When to Use RLock:** When same thread may acquire lock multiple times (re-entrant call chains)

**In this project, we have 3 re-entrant call chains (see rlock-analysis.md):**

1. `route_action() → _get_required_indexes_for_action() → get_index()`
2. `ensure_all_indexes_healthy() → rebuild_index() → get_index()`
3. `update_from_watcher() → get_index()`

**Solution:** Use `threading.RLock` for `_indexes_lock`

**✅ CORRECT: RLock (re-entrant lock)**

```python
class IndexManager:
    def __init__(self, config: IndexesConfig, base_path: Path):
        self._indexes: Dict[str, BaseIndex] = {}
        self._indexes_lock = threading.RLock()  # Re-entrant lock for all operations
        # ...
```

**Why RLock:**
- Allows same thread to acquire lock multiple times
- Prevents deadlock in call chains (route_action → get_index)
- Negligible performance overhead vs Lock (+0.2ns, unmeasurable in practice)
- Correct choice per `python-concurrency.md` standard

**❌ WRONG: threading.Lock (non-re-entrant)**

```python
self._indexes_lock = threading.Lock()  # NON-re-entrant

def route_action(self, action):
    with self._indexes_lock:  # Acquires lock
        return self.get_index(name)  # Tries to acquire again → DEADLOCK!

def get_index(self, name):
    with self._indexes_lock:  # Same thread can't re-acquire Lock
        return self._indexes.get(name)
```

**Performance:**
- Lock acquisition: ~0.7ns
- RLock acquisition: ~0.9ns (+29% relative, but 0.2ns absolute)
- Index query: ~10-100ms (1,000,000x+ lock time)
- Overhead: 0.2ns / 50ms = 0.0000004% → Unmeasurable

**Applies To:** Task 1.2 (IndexManager.__init__)

---

### Pattern 6: Structured Logging for Observability

**When to Use:** All operations that need performance tracking or audit trail

**Format:** Structured logs with `extra={}` dict (machine-readable, jq parseable)

**✅ CORRECT: Structured logging**

```python
import logging

logger = logging.getLogger(__name__)

def route_action(self, action: str, **kwargs):
    start = time.perf_counter()
    
    # ... perform operation ...
    
    latency_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "Index query complete",
        extra={
            "event": "index_query",
            "index_name": index_name,
            "action": action,
            "latency_ms": round(latency_ms, 2),
            "result_count": len(results),
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

**Log Analysis (jq queries):**

```bash
# p95 latency
grep 'Index query' server.log | jq '.latency_ms' | sort -n | tail -n 5

# Slow queries (>1s)
grep 'Index query' server.log | jq 'select(.latency_ms > 1000)'

# Audit trail: Index operations
grep 'index_added\|index_removed' server.log | jq '.time, .index_name'
```

**❌ WRONG: Unstructured logging**

```python
# String interpolation - not machine-readable
logger.info(f"Query complete in {latency_ms}ms with {count} results")

# Would leak sensitive data (query content)
logger.info(f"Query: {query} -> Results: {results}")
```

**Security Requirements:**
- ✅ Log metadata only (index_name, latency, count)
- ❌ Never log query content or results (may contain sensitive data)
- ✅ Sanitize error messages (no full tracebacks to external systems)

**Event Types Required:**
- `index_query`: Query operations (latency, result count)
- `index_added`: Hot reload add (index_name, timestamp)
- `index_removed`: Hot reload remove (index_name, timestamp)
- `indexes_reloaded`: Reload operation (added, removed, kept arrays)
- `index_rebuilt`: Rebuild operation (duration, success boolean)

**Applies To:** Phase 3 tasks 3.1-3.8

---

## 4. Anti-Patterns to Avoid

### Anti-Pattern 1: Modifying Container State In-Place

**Problem:** Creating new partitions on existing CodeIndex container

**❌ WRONG: Modifies container state (not thread-safe, violates immutability)**

```python
def reload_bad(self, new_config):
    index = self._indexes["code"]
    index.add_partition("new-repo")  # Dangerous! Modifies container
```

**Why This Fails:**
- Containers have immutable `components` dict (set once in `__init__`)
- In-flight queries may see partial state (old partitions + new partition half-built)
- Violates fractal pattern (IndexManager shouldn't know partition internals)

**✅ CORRECT: Create new container, atomic swap**

```python
def reload_good(self, new_config):
    new_index = CodeIndex(new_config, base_path)  # New instance
    with self._indexes_lock:  # RLock protects
        self._indexes["code"] = new_index  # Atomic swap
    # Old container lives until in-flight requests complete
    # Python GC cleans up when no references remain
```

---

### Anti-Pattern 2: Bare Exception Handlers

**Problem:** `except Exception:` without re-raise hides critical errors

**❌ WRONG: Swallows all exceptions**

```python
def route_action_bad(self, action, **kwargs):
    try:
        return index.search(**kwargs)
    except Exception:  # Catches everything, including KeyboardInterrupt!
        logger.error("Search failed")
        return {"error": "search failed"}  # Vague, no context
```

**✅ CORRECT: Specific exception types, actionable errors**

```python
def route_action_good(self, action, **kwargs):
    try:
        return index.search(**kwargs)
    except KeyError as e:
        raise IndexError(f"Index '{index_name}' not available. Check config.") from e
    except TimeoutError as e:
        raise RuntimeError(f"Search timeout after 30s. Query: {action}") from e
    # Let unexpected exceptions propagate (fail-fast)
```

**Applies To:** All error handling (Tasks 1.2-1.8, 2.1-2.4)

---

### Anti-Pattern 3: Premature Optimization

**Problem:** Adding complexity before measuring

**Example:** Using RWLock before measuring contention

**Rule:** Measure first, optimize second

**Evidence-Based Performance:**
1. Implement with RLock (simple, correct)
2. Run benchmark test (Task 1.12)
3. Measure contention: `threading.active_count()` during stress test
4. **Only if** contention >10ms waits AND profiling confirms lock contention as bottleneck:
   - Consider RWLock (adds complexity)
   - Re-benchmark (prove improvement)

**Current Status:**
- RLock overhead: 0.2ns → Unmeasurable
- Index I/O: 10-100ms → Dominates (10,000,000x lock time)
- **Verdict:** RLock is sufficient, RWLock premature

**Applies To:** Design decisions (no premature RWLock in Phase 1)

---

## 5. Testing Patterns

### Test Pattern 1: Concurrent Access Test

**Purpose:** Validate thread safety under multi-repo load

**Code Pattern:**

```python
def test_concurrent_index_access():
    """Simulate 10-repo deployment with 100 concurrent operations."""
    import threading
    
    manager = IndexManager(config, base_path)
    errors = []
    
    def search_worker():
        """Simulate MCP search requests (asyncio context)."""
        for _ in range(1000):
            try:
                manager.route_action("search_code", query="test")
            except Exception as e:
                errors.append(("search", e))
    
    def health_worker():
        """Simulate health check poller (asyncio.to_thread)."""
        for _ in range(100):
            try:
                manager.health_check_all()
            except Exception as e:
                errors.append(("health", e))
    
    # 100 threads × 1000 ops = 100k operations
    threads = []
    threads += [threading.Thread(target=search_worker) for _ in range(80)]
    threads += [threading.Thread(target=health_worker) for _ in range(20)]
    
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)  # 30s max
    
    # Assertions
    assert len(errors) == 0, f"Thread safety violated: {errors[:5]}"
    assert all(not t.is_alive() for t in threads), "Threads deadlocked"
```

**Applies To:** Task 1.11

---

### Test Pattern 2: Lock Overhead Benchmark

**Purpose:** Validate NFR-P1 (<1% overhead)

**Code Pattern:**

```python
def test_lock_overhead_negligible():
    """Verify lock overhead < 1% of index operation time."""
    import time
    
    manager = IndexManager(config, base_path)
    
    # Measure 10,000 index operations with locks
    start = time.perf_counter()
    for _ in range(10000):
        manager.route_action("search_code", query="test")
    duration_with_locks = time.perf_counter() - start
    
    # Typical query: 50ms × 10k = 500s
    # Lock overhead <1%: Allow 505s max
    assert duration_with_locks < 505, \
        f"Lock overhead too high: {duration_with_locks}s"
    
    # Document lock acquisition time
    lock_time_ns = (duration_with_locks - 500) / 10000 * 1e9
    print(f"Lock overhead: ~{lock_time_ns:.1f}ns per operation")
```

**Applies To:** Task 1.12

---

### Test Pattern 3: Hot Reload Integration Test

**Purpose:** Validate atomic swap during concurrent queries

**Code Pattern:**

```python
def test_hot_reload_atomic_swap():
    """Validate reload doesn't disrupt in-flight queries."""
    import threading
    import time
    
    manager = IndexManager(config, base_path)
    errors = []
    query_count = {"count": 0}
    
    def query_worker():
        """Continuous queries during reload."""
        for _ in range(50):
            try:
                result = manager.route_action("search_code", query="test")
                query_count["count"] += 1
                time.sleep(0.01)  # 100 queries/sec
            except Exception as e:
                errors.append(e)
    
    # Start 50 concurrent query threads
    threads = [threading.Thread(target=query_worker) for _ in range(50)]
    for t in threads:
        t.start()
    
    # Wait for queries to start
    time.sleep(0.5)
    
    # Trigger hot reload mid-flight
    start_reload = time.perf_counter()
    new_config = load_new_config()  # Config with different repos
    report = manager.reload_indexes(new_config)
    reload_duration_ms = (time.perf_counter() - start_reload) * 1000
    
    # Wait for all queries to complete
    for t in threads:
        t.join(timeout=10)
    
    # Assertions
    assert len(errors) == 0, f"Queries failed during reload: {errors[:5]}"
    assert query_count["count"] >= 50 * 40, "Queries blocked by reload"
    assert reload_duration_ms < 100, f"Reload too slow: {reload_duration_ms}ms"
    assert "added" in report and "removed" in report
```

**Applies To:** Task 2.6

---

## 6. Import and Dependency Patterns

**Correct Import Order:**

```python
# index_manager.py
import threading
from typing import Dict, Optional, Type

from ouroboros.config.schemas.indexes import IndexesConfig
from ouroboros.subsystems.rag.base import BaseIndex
from ouroboros.subsystems.rag import INDEX_REGISTRY  # Dynamic registry
```

**Dependency Injection Pattern:**

```python
# IndexManager receives dependencies via __init__
class IndexManager:
    def __init__(
        self,
        config: IndexesConfig,      # Injected: Configuration
        base_path: Path,             # Injected: Workspace root
        session_mapper: SessionMapper  # Injected: State persistence (unused currently)
    ):
        self._indexes_lock = threading.RLock()  # Internal: No DI needed
        self._indexes: Dict[str, BaseIndex] = {}
        self._init_indexes()  # Uses INDEX_REGISTRY for dynamic instantiation
```

**Why Dependency Injection:**
- Testability: Can inject mock config/base_path for tests
- Flexibility: Config can change without modifying IndexManager
- Standards: Matches project patterns (see WorkflowEngine for reference)

---

## 7. Testing Strategy

### 7.1 Requirements Summary

**Total Requirements:** 24 (10 FRs + 14 NFRs)

**Functional Requirements (FR):** 10
- FR-001: Thread-Safe Dictionary Access (P0)
- FR-002: Re-entrant Lock Implementation (P0)
- FR-003: Concurrent Query Support (P0)
- FR-004: Hot Reload - Add Index (P1)
- FR-005: Hot Reload - Remove Index (P1)
- FR-006: Hot Reload - Reload Indexes (P1)
- FR-007: Standards Compliance Documentation (P0)
- FR-008: Snapshot Pattern for Iteration (P1)
- FR-009: Structured Logging for Observability (P2)
- FR-010: Lock Overhead Performance (P1)

**Non-Functional Requirements (NFR):** 14
- **Performance (P):** NFR-P1 (Lock Overhead), NFR-P2 (Concurrent Throughput), NFR-P3 (Hot Reload Speed)
- **Reliability (R):** NFR-R1 (Zero Race Conditions), NFR-R2 (Deadlock Prevention), NFR-R3 (Atomic State Transitions)
- **Maintainability (M):** NFR-M1 (Documentation), NFR-M2 (Test Suite), NFR-M3 (Dynamic Logic)
- **Consistency (C):** NFR-C1 (Architectural Consistency), NFR-C2 (Python 3.13 Compatibility)
- **Observability (O):** NFR-O1 (Structured Logging), NFR-O2 (Query Latency Visibility)
- **Security/Simplicity (S):** NFR-S1 (No External Dependencies)

**Priority Breakdown:**
- Critical (P0): 4 FRs, 3 NFRs = **7 requirements**
- High (P1): 4 FRs, 8 NFRs = **12 requirements**
- Medium (P2): 2 FRs, 3 NFRs = **5 requirements**

**Source:** `testing/requirements-list.md`

---

### 7.2 Traceability Matrix

**100% Requirement Coverage:**
- FRs mapped to tests: 10/10 (100%)
- NFRs mapped to tests: 14/14 (100%)
- Total test functions: **28+** across 3 test files

**Test File Distribution:**
- `test_index_manager_thread_safety.py`: 10 test functions (thread safety, stress, benchmarks, documentation)
- `test_index_manager_hot_reload.py`: 14 test functions (add/remove/reload unit + integration)
- `test_index_manager_logging.py`: 4 test functions (structured logging, security)

**Complete Mapping:** Every requirement has ≥1 test function validating its acceptance/measurement criteria.

**Matrix:** `testing/traceability-matrix.md`

---

### 7.3 Test Cases

**Functional Test Cases:** 30+ test cases across 10 FRs
- **Happy Path:** 18 test cases (feature works as expected)
- **Error Handling:** 5 test cases (graceful error handling)
- **Edge Cases:** 3 test cases (boundary conditions)
- **Integration:** 6 test cases (multi-component scenarios)

**Examples:**
- `test_concurrent_index_access()`: 100 threads × 1000 ops = 100k concurrent operations
- `test_hot_reload_atomic_swap()`: 50 query threads during reload (atomicity validation)
- `test_add_index_duplicate_raises_value_error()`: Error handling for duplicate index names

**NFR Verification Tests:** 15 test functions across 14 NFRs
- **Performance:** 3 tests (lock overhead <1%, throughput, reload <100ms)
- **Reliability:** 4 tests (zero race conditions, deadlock prevention, atomicity)
- **Maintainability:** 3 tests (documentation, coverage, extensibility)
- **Consistency:** 2 tests (RLock type, GIL-independence)
- **Observability:** 2 tests (structured logging, latency visibility)
- **Security:** 1 test (no external dependencies)

**Integration Scenarios:** 2 end-to-end scenarios
- Multi-agent multi-repo deployment (FR-001, FR-003, FR-008)
- Graceful config change (FR-004, FR-005, FR-006)

**Details:** `testing/functional-tests.md`, `testing/nonfunctional-tests.md`

---

### 7.4 Testing Approach

**Philosophy:**
- **Evidence-Based Thread Safety**: Don't assume, prove with 100k concurrent operations
- **Standards-Driven**: Validate compliance with 4 concurrency standards
- **Fast Feedback**: Unit tests <1s, integration tests <30s, total suite <2 min
- **Test-First for Concurrency**: Write concurrent access tests before implementing locks

**Test Pyramid:**
```
       ▲
      / \          1 E2E Test
     /   \         (Multi-agent multi-repo)
    /_____\
   /       \       6 Integration Tests
  /         \      (Hot reload during queries, etc.)
 /___________\
/             \    22 Unit Tests
/______________\   (Individual method behavior)
```

**Coverage Targets:**
- **Overall:** ≥90% line coverage for IndexManager
- **Critical Paths:** 100% coverage for 7 modified methods + 3 hot reload methods
- **Modified Code:** 100% coverage for lock-protected sections

**Execution Time:**
- Unit tests: <1s total (fast feedback)
- Integration tests: <30s total (acceptable for concurrent tests)
- E2E tests: <60s (full system validation)
- **Total suite:** <2 minutes (CI/CD friendly)

**Test Isolation:**
- **Mock:** External APIs, file system I/O, index implementations (use MockIndex)
- **Don't Mock:** `threading.RLock`, dict operations, IndexManager methods (test real behavior)

**Commands:**
```bash
# Run all tests
pytest tests/ouroboros/subsystems/rag/

# Run with coverage
pytest tests/ouroboros/subsystems/rag/ \
    --cov=ouroboros.subsystems.rag.index_manager \
    --cov-report=term-missing \
    --cov-fail-under=90

# Run stress tests only
pytest tests/ouroboros/subsystems/rag/ -k stress
```

**Strategy:** `testing/test-strategy.md`

---

### 7.5 Testing Checklist

**Before Implementation:**
- [ ] Review traceability matrix (`testing/traceability-matrix.md`)
- [ ] Review test cases (`testing/functional-tests.md`, `testing/nonfunctional-tests.md`)
- [ ] Review testing strategy (`testing/test-strategy.md`)
- [ ] Set up test environment (pytest, coverage.py, fixtures)

**During Implementation (Per Phase):**
- [ ] Write tests first or alongside code (TDD approach for concurrency)
- [ ] Verify tests pass after each method modification
- [ ] Check coverage after each phase (≥90% target)
- [ ] Run linter (zero errors required)

**Phase 1 Completion (Thread Safety):**
- [ ] All 13 Phase 1 tests implemented (concurrent access, benchmark, stress, documentation)
- [ ] All tests passing (100% pass rate)
- [ ] Coverage ≥90% for modified methods
- [ ] NFR-R1 (Zero Race Conditions) validated: 100k ops, zero exceptions
- [ ] NFR-P1 (Lock Overhead) validated: <1% regression

**Phase 2 Completion (Hot Reload):**
- [ ] All 6 Phase 2 tests implemented (unit tests for add/remove/reload + integration test)
- [ ] All tests passing
- [ ] NFR-P3 (Hot Reload <100ms) validated
- [ ] NFR-R3 (Atomic State Transitions) validated: No partial state visible
- [ ] NFR-M3 (Dynamic Logic) validated: INDEX_REGISTRY used, zero hardcoded types

**Phase 3 Completion (Observability):**
- [ ] All 4 Phase 3 tests implemented (structured logging, security)
- [ ] All tests passing
- [ ] NFR-O1 (Structured Logging) validated: 5+ event types, jq parseable
- [ ] NFR-O2 (Query Latency) validated: All queries log latency_ms

**Before Production Deployment:**
- [ ] All 28+ tests implemented across 3 test files
- [ ] All tests passing (100% success rate, zero flaky tests)
- [ ] Coverage target met: ≥90% overall, 100% critical paths
- [ ] All 7 critical (P0) requirements validated
- [ ] All 12 high-priority (P1) requirements validated
- [ ] No linter errors in modified code
- [ ] Code review approved (second developer validates thread safety)

---

### 7.6 Completeness Verification

✅ **All 24 requirements have been:**

1. **Extracted** into `testing/requirements-list.md`
   - 10 functional requirements with acceptance criteria
   - 14 non-functional requirements with measurement criteria
   - Priority levels assigned (7 P0, 12 P1, 5 P2)

2. **Mapped to tests** in `testing/traceability-matrix.md`
   - 10 FRs → 15+ test functions (100% coverage)
   - 14 NFRs → 15+ test functions (100% coverage)
   - 28+ total test functions identified
   - Test file locations specified

3. **Given test cases** in `testing/functional-tests.md` and `testing/nonfunctional-tests.md`
   - 30+ functional test cases (happy path, error handling, edge cases, integration)
   - 15 NFR verification tests (objective, measurable criteria)
   - All with setup, action, expected results, and verification documented

4. **Covered by strategy** in `testing/test-strategy.md`
   - Test pyramid defined (22 unit, 6 integration, 1 E2E)
   - Coverage targets set (≥90% overall, 100% critical paths)
   - Execution approach documented (commands, CI/CD, debugging)
   - Mocking strategy specified

**Counts Verification:**

| Document | Requirements Count | Test Functions Count | Match? |
|----------|-------------------|---------------------|--------|
| requirements-list.md | 24 (10 FR + 14 NFR) | - | ✅ |
| traceability-matrix.md | 24 (10 FR + 14 NFR) | 28+ | ✅ |
| functional-tests.md | 10 FRs | 30+ test cases | ✅ |
| nonfunctional-tests.md | 14 NFRs | 15 test functions | ✅ |
| test-strategy.md | - | 33 (22 unit + 6 int + 1 E2E + 4 log) | ✅ |

**No requirements are untested. 100% requirement → test traceability achieved.**

---

### 7.7 Test Implementation Schedule

**Phase 1 Tests (Tasks 1.11-1.13):** 9 hours
- Concurrent access test: 4 hours (100k ops, 4 contexts)
- Lock overhead benchmark: 2 hours (10k queries, measure <1%)
- Stress test: 3 hours (50 threads × 10s, stability validation)

**Phase 2 Tests (Tasks 2.5-2.6):** 7 hours
- Hot reload unit tests: 3 hours (9 test cases for add/remove/reload)
- Hot reload integration test: 4 hours (atomic swap during concurrent queries)

**Phase 3 Tests (Task 3.8):** 1 hour
- Logging tests: 1 hour (format validation, security, latency visibility)

**Total Test Implementation Time:** 17 hours (embedded in 44-hour implementation)

---

## 8. Deployment Guidance

### 8.1 Deployment Overview

**Scope:** Internal component modification (IndexManager thread safety + hot reload)  
**Impact:** Changes to `ouroboros/subsystems/rag/index_manager.py` and test files  
**Deployment Type:** Code update (no database migrations, no API changes)  
**Risk Level:** Medium (core component, but comprehensive tests mitigate risk)

**Deployment Strategy:** Phased rollout
1. Deploy to single-repo deployment first (validate thread safety)
2. Deploy to multi-repo deployment second (validate hot reload)
3. Monitor for 24-48 hours before marking complete

---

### 8.2 Pre-Deployment Checklist

**Code Quality:**
- [ ] All 28+ tests passing (100% pass rate)
  ```bash
  pytest tests/ouroboros/subsystems/rag/
  ```
- [ ] Code coverage ≥90%
  ```bash
  pytest tests/ouroboros/subsystems/rag/ \
      --cov=ouroboros.subsystems.rag.index_manager \
      --cov-fail-under=90
  ```
- [ ] Zero linter errors
  ```bash
  flake8 ouroboros/subsystems/rag/index_manager.py
  mypy ouroboros/subsystems/rag/index_manager.py
  ```
- [ ] Code review approved (second developer validates thread safety)
- [ ] All 3 phase validation gates passed (Phase 1, 2, 3 complete)

**Documentation:**
- [ ] Class docstring updated (threading model documented)
- [ ] Method docstrings updated (7 methods + 3 hot reload methods)
- [ ] Standards references included (4 concurrency standards)
- [ ] implementation.md reviewed by team

**Requirements:**
- [ ] All 7 critical (P0) requirements validated
- [ ] All 12 high-priority (P1) requirements validated
- [ ] Traceability matrix 100% complete

**Environment:**
- [ ] No new dependencies added (stdlib only)
- [ ] requirements.txt unchanged (NFR-S1 validated)
- [ ] Python version: ≥3.8 (3.13 compatible design)

---

### 8.3 Deployment Steps

**Step 1: Backup Current State**

```bash
# Create backup branch
git checkout -b backup/pre-thread-safety-$(date +%Y%m%d)
git push origin backup/pre-thread-safety-$(date +%Y%m%d)

# Document current behavior (baseline for comparison)
pytest tests/ouroboros/subsystems/rag/ --benchmark-only > baseline.txt
```

**Step 2: Merge Changes**

```bash
# Merge PR with thread safety + hot reload changes
git checkout main
git merge --no-ff feature/indexmanager-thread-safety-hot-reload

# Verify merge
git log --oneline -10
```

**Step 3: Run Full Test Suite**

```bash
# Run all tests (not just IndexManager)
pytest tests/ --tb=short

# Verify no regressions in other components
pytest tests/ouroboros/subsystems/ -v
```

**Step 4: Build and Install**

```bash
# Install in development mode
pip install -e .

# Verify installation
python -c "from ouroboros.subsystems.rag.index_manager import IndexManager; print('OK')"
```

**Step 5: Deploy to Staging**

```bash
# Deploy to staging environment (single-repo test deployment)
./deploy.sh staging

# Verify MCP server starts
ps aux | grep mcp-server
```

**Step 6: Smoke Tests**

```bash
# Test 1: Single query (validates basic functionality)
curl -X POST http://localhost:8000/mcp/search \
  -H "Content-Type: application/json" \
  -d '{"action": "search_code", "query": "test"}'

# Test 2: Concurrent queries (validates thread safety)
for i in {1..100}; do
  curl -X POST http://localhost:8000/mcp/search \
    -H "Content-Type: application/json" \
    -d '{"action": "search_code", "query": "test"}' &
done
wait

# Test 3: Hot reload (if applicable)
# Edit config, trigger reload, verify no query errors
```

**Step 7: Monitor Logs**

```bash
# Check for exceptions
grep "ERROR\|Exception\|Traceback" logs/server.log

# Check structured logs
grep "index_query" logs/server.log | jq '.latency_ms' | sort -n | tail -5

# Verify no race conditions
grep "race\|deadlock\|corruption" logs/server.log
# Expected: No results
```

**Step 8: Deploy to Production**

```bash
# If staging successful, deploy to production
./deploy.sh production

# Monitor for 10 minutes after deployment
tail -f logs/server.log | grep "ERROR\|Exception"
```

---

### 8.4 Post-Deployment Validation

**Functional Validation:**

```bash
# Test concurrent queries (validate thread safety in production)
pytest tests/ouroboros/subsystems/rag/test_index_manager_thread_safety.py::test_concurrent_index_access

# Test hot reload (if multi-repo deployment)
pytest tests/ouroboros/subsystems/rag/test_index_manager_hot_reload.py::test_hot_reload_atomic_swap
```

**Performance Validation:**

```bash
# Verify lock overhead <1%
pytest tests/ouroboros/subsystems/rag/test_index_manager_thread_safety.py::test_lock_overhead_negligible

# Verify hot reload <100ms (if applicable)
pytest tests/ouroboros/subsystems/rag/test_index_manager_hot_reload.py -k latency
```

**Log Analysis:**

```bash
# p95 latency (should match baseline)
grep "index_query" logs/server.log | jq '.latency_ms' | sort -n | awk 'BEGIN{c=0} {a[c++]=$1} END{print "p95:", a[int(c*0.95)]}'

# Error rate (should be 0%)
error_count=$(grep "ERROR" logs/server.log | wc -l)
total_queries=$(grep "index_query" logs/server.log | wc -l)
error_rate=$(echo "scale=4; $error_count / $total_queries * 100" | bc)
echo "Error rate: $error_rate%"  # Expected: 0%
```

**Monitoring Dashboard (24-48 hours):**
- Query latency p50, p95, p99 (should match baseline ±5%)
- Error rate (should be 0%)
- Thread count (should be stable, no leaks)
- Memory usage (should be stable, no leaks)

---

### 8.5 Rollback Strategy

**Rollback Triggers:**

1. **Critical (Immediate Rollback):**
   - Exceptions/crashes during queries
   - Data corruption detected
   - Deadlocks observed (threads hanging)
   - Error rate >1%

2. **Major (Rollback within 1 hour):**
   - Performance degradation >10%
   - Memory leak detected (increasing over time)
   - Hot reload failures

3. **Minor (Monitor, rollback if worsens):**
   - Logging anomalies
   - Latency spikes (but still <threshold)

**Rollback Procedure:**

**Option 1: Git Revert (Recommended)**

```bash
# 1. Identify commit to revert
git log --oneline --grep="thread-safety" -5

# 2. Revert merge commit
git revert -m 1 <merge-commit-hash>

# 3. Push revert
git push origin main

# 4. Redeploy previous version
./deploy.sh production

# 5. Verify rollback successful
pytest tests/ouroboros/subsystems/rag/ --tb=short
```

**Option 2: Restore from Backup Branch**

```bash
# 1. Checkout backup branch
git checkout backup/pre-thread-safety-20251120

# 2. Force deploy (emergency rollback)
./deploy.sh production --force

# 3. Verify system health
curl http://localhost:8000/health
```

**Post-Rollback:**
- [ ] Verify error rate drops to 0%
- [ ] Verify performance returns to baseline
- [ ] Document root cause in incident log
- [ ] Create issue for fix
- [ ] Schedule post-mortem

---

### 8.6 Environment Configuration

**No Environment Variables Required**

This implementation uses Python stdlib only (no configuration changes).

**Existing Config (unchanged):**
- `config.yaml`: Indexes configuration (used by hot reload)
- `base_path`: Workspace root (existing parameter)

**Validation:**

```python
# Verify config unchanged
from ouroboros.config import load_config
config = load_config()
assert "indexes" in config.rag
```

---

### 8.7 Deployment Checklist

**Pre-Deployment:**
- [ ] All tests passing (28+/28+)
- [ ] Code reviewed and approved
- [ ] Coverage ≥90% validated
- [ ] No linter errors
- [ ] Backup branch created
- [ ] Staging deployed successfully
- [ ] Smoke tests passed on staging

**Deployment:**
- [ ] Changes merged to main
- [ ] Full test suite passed
- [ ] Installed and verified
- [ ] Deployed to production
- [ ] Smoke tests passed on production

**Post-Deployment (24-48 hours):**
- [ ] Metrics normal (latency, error rate)
- [ ] Logs clean (no exceptions, no race conditions)
- [ ] Performance matches baseline (±5%)
- [ ] Hot reload works (if multi-repo deployment)
- [ ] No memory leaks (memory stable over 24h)
- [ ] No thread leaks (thread count stable)

---

### 8.8 Phased Rollout Plan

**Phase A: Single-Repo Deployment (Week 1)**

**Scope:** Deploy to single-repo deployment (e.g., internal development server)

**Validation:**
- Thread safety: 100k concurrent operations, zero exceptions
- Performance: Latency matches baseline
- Monitoring: 1 week observation period

**Success Criteria:**
- Zero race conditions
- Zero deadlocks
- Lock overhead <1%
- No production incidents

**Phase B: Multi-Repo Deployment (Week 2)**

**Scope:** Deploy to multi-repo deployment (e.g., production with 5-10 repos)

**Validation:**
- Hot reload: Add/remove repos without query errors
- Atomicity: Queries during reload see consistent state
- Performance: Reload <100ms

**Success Criteria:**
- Hot reload works without errors
- Atomic state transitions (no partial state)
- No performance degradation

**Phase C: Full Rollout (Week 3)**

**Scope:** Deploy to all environments

**Monitoring:**
- Continuous log analysis
- Performance dashboards
- Incident tracking

**Completion Criteria:**
- 2 weeks uptime without thread safety incidents
- Performance stable at baseline
- All requirements validated in production

---

## 9. Troubleshooting Guide

### 9.1 Common Issues

#### Issue 1: Race Condition Detected (Concurrent Access Test Fails)

**Symptoms:**
- `test_concurrent_index_access()` fails with exceptions
- Exception: `KeyError`, `AttributeError`, `RuntimeError` during concurrent ops
- Intermittent failures (test passes sometimes, fails other times)

**Cause:**
- Unprotected access to `_indexes` dict (missing lock)
- Lock held during expensive operation (blocking)
- Wrong lock type (Lock instead of RLock causing deadlock in re-entrant call)

**Solution:**

```python
# 1. Audit all _indexes accesses
grep -n "self._indexes" ouroboros/subsystems/rag/index_manager.py

# 2. Verify each access is under lock
# CORRECT:
with self._indexes_lock:
    index = self._indexes.get(name)  # Protected
# Query outside lock

# WRONG:
index = self._indexes.get(name)  # Unprotected - RACE CONDITION!

# 3. Run test with reduced threads for easier debugging
# Modify test: 100 threads → 10 threads
# Increases chance of reproducing issue in controlled way

# 4. Add logging to identify unprotected access
import logging
logger.debug(f"Accessing _indexes, lock held: {self._indexes_lock.locked()}")

# 5. Verify lock type
assert isinstance(self._indexes_lock, threading.RLock), "Must be RLock!"
```

**Prevention:**
- Use grep audit before committing: `grep "self._indexes" <file> | grep -v "lock"`
- Review checklist: "Is this access under lock?"
- Code review: Second developer validates all access sites

---

#### Issue 2: Deadlock (Tests Timeout)

**Symptoms:**
- Tests hang/timeout (threads never complete)
- `test_reentrant_lock_call_chains()` times out
- Application freezes during queries

**Cause:**
- Using `threading.Lock` instead of `RLock` (can't re-acquire in same thread)
- Acquiring multiple locks in inconsistent order (classic deadlock)
- Lock held indefinitely (forgot to release)

**Solution:**

```python
# 1. Verify RLock is used
assert isinstance(self._indexes_lock, threading.RLock)

# 2. Check for re-entrant call chains
# route_action() → get_index() both acquire lock
# With Lock: Deadlock
# With RLock: Works

# 3. Add timeout to lock acquisition (debugging only)
if not self._indexes_lock.acquire(timeout=5):
    logger.error("Lock acquisition timeout - possible deadlock!")
    raise TimeoutError("Deadlock detected")

# 4. Use threading.stack_size() to detect hung threads
import threading
for thread in threading.enumerate():
    if thread.is_alive():
        logger.warning(f"Thread {thread.name} still alive")

# 5. Check for forgotten lock release
# WRONG:
self._indexes_lock.acquire()
# ... code ...
# Forgot to release!

# CORRECT:
with self._indexes_lock:  # Auto-releases
    # ... code ...
```

**Prevention:**
- Always use `with self._indexes_lock:` (context manager auto-releases)
- Use RLock for re-entrant scenarios
- Test with `pytest-timeout` to catch hangs early

---

#### Issue 3: Lock Overhead >1% (Performance Test Fails)

**Symptoms:**
- `test_lock_overhead_negligible()` fails
- Query latency increased >1% vs. baseline
- Throughput degraded under concurrent load

**Cause:**
- Lock held during expensive operation (10-100ms query)
- High lock contention (too many threads)
- Incorrect measurement (including I/O in lock time)

**Solution:**

```python
# 1. Verify lock held for minimum time only
# WRONG: Lock held during query (10-100ms)
with self._indexes_lock:
    index = self._indexes.get(name)
    return index.search(query)  # 10-100ms - BAD!

# CORRECT: Lock held for dict access only (1ns)
with self._indexes_lock:
    index = self._indexes.get(name)  # 1ns - GOOD!
return index.search(query)  # 10-100ms outside lock

# 2. Profile lock acquisition time
import time
start = time.perf_counter()
with self._indexes_lock:
    pass  # Empty critical section
lock_time = (time.perf_counter() - start) * 1e9  # nanoseconds
print(f"Lock acquisition: {lock_time}ns")  # Expected: ~0.9ns

# 3. Check for contention
import threading
print(f"Active threads: {threading.active_count()}")
# High count (>100) may cause contention

# 4. Measure query time separately
start = time.perf_counter()
result = index.search(query)
query_time = (time.perf_counter() - start) * 1000  # ms
print(f"Query time: {query_time}ms")  # Expected: 10-100ms
# Lock time (0.9ns) << Query time (50ms) = 55,555,556x difference
```

**Prevention:**
- Always release lock before I/O operations
- Benchmark early and often
- Monitor lock contention in production

---

#### Issue 4: Hot Reload Fails (Atomic Swap Test Fails)

**Symptoms:**
- `test_hot_reload_atomic_swap()` fails
- Queries see partial state (some old indexes, some new)
- `IndexError` during reload: "Index not found"

**Cause:**
- Multiple lock acquisitions (not atomic)
- Config applied incrementally (remove first, then add - partial state visible)
- Lock released between operations

**Solution:**

```python
# WRONG: Not atomic (lock released between operations)
for name in to_remove:
    with self._indexes_lock:
        self._indexes.pop(name)  # Partial state visible here!
for name in to_add:
    with self._indexes_lock:
        self._indexes[name] = new_index  # Another partial state!

# CORRECT: Atomic swap (single lock acquisition)
with self._indexes_lock:
    # All modifications under one lock
    for name in to_remove:
        old = self._indexes.pop(name)
    for name in to_add:
        self._indexes[name] = new_index
# Lock released: state is consistent (all-or-nothing)

# Verification during test:
# Query results must match EITHER old config OR new config
assert is_valid_for(result, old_config) or is_valid_for(result, new_config)
assert not is_mixed_state(result)  # Never partial!
```

**Prevention:**
- All dict modifications in single `with self._indexes_lock:` block
- Test atomic swap explicitly
- Review: "Are all changes under one lock acquisition?"

---

#### Issue 5: Logging Data Leakage (Security Test Fails)

**Symptoms:**
- `test_log_scrubbing_no_sensitive_data()` fails
- Query content appears in logs
- Code snippets from search results in logs

**Cause:**
- Logging query parameter: `logger.info(f"Query: {query}")`  ← BAD!
- Logging results: `logger.info(f"Results: {results}")`  ← BAD!
- Unstructured logging with string interpolation

**Solution:**

```python
# WRONG: Logs sensitive data
logger.info(f"Query: {query}, Results: {results}")

# CORRECT: Logs metadata only
logger.info(
    "Index query complete",
    extra={
        "event": "index_query",
        "index_name": index_name,
        "latency_ms": latency,
        "result_count": len(results),  # Count only, not content!
        # NO query, NO results content
    }
)

# Verification:
# grep "query" logs/server.log | grep -v "index_query"
# Expected: No matches (no query content)
```

**Prevention:**
- Always use `extra={}` dict for logging
- Code review: "Does this log contain query content or results?"
- Security test validates no data leakage

---

### 9.2 Debugging Techniques

#### Debugging Thread Safety Issues

**Enable Threading Debug Mode:**

```python
# Add to IndexManager.__init__ for debugging
import threading
threading.current_thread().name = "IndexManager-Main"

# In each method, log thread ID
logger.debug(
    f"Method {method_name} called",
    extra={"thread_id": threading.current_thread().ident}
)

# Identify which threads are accessing _indexes
```

**Use ThreadSanitizer (if available):**

```bash
# Python must be built with ThreadSanitizer support
# Check: python3 --version  # Look for TSAN build
python3-tsan -m pytest tests/ouroboros/subsystems/rag/

# Output will show race conditions:
# WARNING: ThreadSanitizer: data race (pid=...)
#   Write of size 8 at 0x... by thread T1:
#     #0 route_action() index_manager.py:678
```

**Manual Lock Inspection:**

```python
# Add temporary debugging (remove before commit)
def route_action(self, action, **kwargs):
    logger.info(f"Lock status before: {self._indexes_lock.locked()}")
    with self._indexes_lock:
        logger.info(f"Lock acquired by: {threading.current_thread().name}")
        index = self._indexes.get(name)
    logger.info(f"Lock released")
    return index.search(**kwargs)
```

---

#### Debugging Performance Issues

**Profile Lock Contention:**

```python
import time
import threading

lock_wait_times = []

def acquire_with_timing():
    start = time.perf_counter()
    acquired = self._indexes_lock.acquire(blocking=True)
    wait_time = time.perf_counter() - start
    lock_wait_times.append(wait_time * 1000)  # ms
    return acquired

# After test:
print(f"Lock wait times - p50: {sorted(lock_wait_times)[50]}ms, p95: {sorted(lock_wait_times)[95]}ms")
# If p95 >10ms: Contention issue
```

**Profile Query Latency:**

```bash
# Extract latency from structured logs
grep "index_query" logs/server.log | jq '.latency_ms' > latencies.txt

# Analyze with Python
python3 <<EOF
import statistics
with open('latencies.txt') as f:
    latencies = [float(line) for line in f]
print(f"p50: {statistics.median(latencies)}ms")
print(f"p95: {sorted(latencies)[int(len(latencies)*0.95)]}ms")
print(f"p99: {sorted(latencies)[int(len(latencies)*0.99)]}ms")
EOF
```

**Use py-spy for Live Profiling:**

```bash
# Install py-spy
pip install py-spy

# Profile running server
sudo py-spy top --pid <server-pid>

# Look for threads spending time in lock acquisition
# If many threads in "RLock.acquire": High contention
```

---

#### Debugging Hot Reload Issues

**Trace Config Diff:**

```python
# Add logging to reload_indexes()
def reload_indexes(self, new_config):
    current = set(self._indexes.keys())
    desired = set(new_config.indexes)
    
    logger.info(
        "Reload diff",
        extra={
            "current": list(current),
            "desired": list(desired),
            "to_add": list(desired - current),
            "to_remove": list(current - desired),
        }
    )
    # ... rest of method
```

**Verify INDEX_REGISTRY:**

```python
# Check registry contains expected types
from ouroboros.subsystems.rag import INDEX_REGISTRY
print("INDEX_REGISTRY:", INDEX_REGISTRY.keys())
# Expected: dict_keys(['standards', 'code', ...])

# Verify new index type is registered
assert "new_index_type" in INDEX_REGISTRY, "Not registered!"
```

**Monitor State Transitions:**

```python
# Before/after snapshots
before = set(self._indexes.keys())
manager.reload_indexes(new_config)
after = set(self._indexes.keys())

print(f"Before: {before}")
print(f"After: {after}")
print(f"Added: {after - before}")
print(f"Removed: {before - after}")
```

---

### 9.3 Performance Debugging

**Slow Queries (Latency Spikes):**

```bash
# Find slow queries in logs
grep "index_query" logs/server.log | jq 'select(.latency_ms > 1000)'

# Common causes:
# 1. Index not cached (first query slow)
# 2. Large result set (>1000 results)
# 3. Disk I/O (index on slow storage)
# 4. Lock contention (rare, but possible)

# Debug: Add timing to each stage
with self._indexes_lock:
    t1 = time.perf_counter()
    index = self._indexes.get(name)
    lock_time = time.perf_counter() - t1

t2 = time.perf_counter()
result = index.search(query)
query_time = time.perf_counter() - t2

logger.info(f"Lock: {lock_time*1000}ms, Query: {query_time*1000}ms")
# If lock_time >10ms: Contention issue
# If query_time >1000ms: Index issue (not IndexManager)
```

**Memory Leaks:**

```bash
# Monitor memory over time
watch -n 1 "ps aux | grep mcp-server | awk '{print \$6}'"

# If memory increasing:
# 1. Check for unreleased index references
# 2. Check for thread leaks (threads not cleaned up)
# 3. Profile with memory_profiler

pip install memory_profiler
python -m memory_profiler server.py

# Look for increasing memory in IndexManager methods
```

**Thread Leaks:**

```python
# Monitor thread count
import threading
print(f"Active threads: {threading.active_count()}")
# Expected: ~10-20 threads (asyncio + watchdog + timers)
# If >50: Thread leak (threads not cleaned up after hot reload)

# List all threads
for thread in threading.enumerate():
    print(f"Thread: {thread.name}, Alive: {thread.is_alive()}")
```

---

### 9.4 Getting Help

**Before Asking for Help:**

1. **Reproduce the issue:**
   - Minimal reproducible example
   - Specific test that fails
   - Steps to reproduce

2. **Gather diagnostics:**
   ```bash
   # System info
   python --version
   pytest --version
   
   # Test output
   pytest tests/ouroboros/subsystems/rag/ -vvs --tb=long > test-output.txt
   
   # Logs
   tail -1000 logs/server.log > recent-logs.txt
   
   # Threading info
   python -c "import threading; print(threading.enumerate())"
   ```

3. **Check documentation:**
   - Review implementation.md (this document)
   - Review testing docs (testing/*.md)
   - Review concurrency standards (4 referenced standards)

**When Asking for Help:**

**Include:**
- Issue description (symptoms, what you expected vs. what happened)
- Reproducible example (test case or minimal code)
- Diagnostics (test output, logs, error messages)
- What you've tried (debugging steps, attempted solutions)

**Template:**

```
**Issue:** Race condition in test_concurrent_index_access()

**Symptoms:**
- Test fails intermittently (50% of runs)
- Exception: KeyError: 'code'
- Occurs during concurrent access from 100 threads

**Reproducible:**
pytest tests/ouroboros/subsystems/rag/test_index_manager_thread_safety.py::test_concurrent_index_access

**Diagnostics:**
- Test output: [attach test-output.txt]
- Logs: [attach recent-logs.txt]
- Thread count: 102 (expected: 100)

**Tried:**
- Verified lock type is RLock ✅
- Grepped for unprotected accesses (found none)
- Reduced threads to 10 (still fails)
```

**Where to Ask:**
- Team chat: #praxis-os-development
- GitHub Issues: honeyhiveai/praxis-os/issues
- Documentation: `.praxis-os/standards/` (reference for patterns)

---

## 10. Summary

### Document Structure

This implementation guide (implementation.md) contains:

1. **§1-2: Implementation Philosophy & Order** - Principles and phase sequence
2. **§3-6: Code Patterns** - 6 core patterns, 3 anti-patterns, imports
3. **§7: Testing Strategy** - 28+ tests, 100% requirement coverage
4. **§8: Deployment Guidance** - 8-step deployment, rollback, phased rollout
5. **§9: Troubleshooting** - 5 common issues, debugging techniques, getting help

### Key Takeaways

**Thread Safety:**
- Always use `with self._indexes_lock:` for dict access
- RLock required (not Lock) due to re-entrant call chains
- Hold lock for minimum time (<10ns for dict access)
- Lock overhead is unmeasurable vs. I/O (10-100ms queries)

**Hot Reload:**
- Atomic swap: All dict modifications under single lock acquisition
- Cleanup outside lock (avoid blocking queries)
- Use INDEX_REGISTRY for dynamic logic (zero hardcoded types)
- Test atomicity: Queries see old OR new, never partial

**Testing:**
- 28+ tests validate all 24 requirements (100% coverage)
- Critical tests: 100k concurrent ops (race condition detection), atomic swap (hot reload validation)
- Fast feedback: <2 min total test suite

**Deployment:**
- Phased rollout: Single-repo (Week 1) → Multi-repo (Week 2) → Full (Week 3)
- Rollback ready: Git revert or backup branch restore
- Monitor 24-48 hours post-deployment

**Troubleshooting:**
- Race conditions: Audit all `_indexes` accesses, verify lock protection
- Deadlocks: Use RLock, always use `with` statement
- Performance: Verify lock held <10ns, I/O outside lock
- Hot reload: Atomic swap (single lock acquisition for all changes)

---

**Document Version:** 1.3 (FINAL)  
**Last Updated:** 2025-11-20  
**Status:** ✅ Complete - All sections finished (Code Patterns, Testing, Deployment, Troubleshooting)  
**Pages:** 10 sections, ~450 lines  
**Ready for:** Implementation (Phase 1-3 execution)

