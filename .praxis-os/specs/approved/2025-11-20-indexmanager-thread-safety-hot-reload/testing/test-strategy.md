# Testing Strategy

**Project:** IndexManager Thread Safety, Hot Reload, and Dynamic Logic Implementation  
**Date:** 2025-11-20  
**Purpose:** Define comprehensive testing approach for thread safety, hot reload, and observability  
**Version:** 1.0

---

## Testing Philosophy

**Core Principles:**

1. **Evidence-Based Thread Safety**: Don't assume thread safety, prove it through 100k concurrent operations
2. **Standards-Driven**: Every test validates compliance with 4 concurrency standards
3. **Fast Feedback**: Unit tests run in <1s, integration tests in <30s
4. **Test-First for Concurrency**: Write concurrent access tests before implementing locks
5. **Measurement Over Intuition**: All performance claims validated through benchmarks

**Risk-Based Priority:**

- **Critical (P0)**: Thread safety, deadlock prevention → Must pass before Phase 2
- **High (P1)**: Hot reload atomicity, lock overhead → Must pass before production
- **Medium (P2)**: Observability, logging → Can iterate post-MVP

---

## Test Pyramid

```
                  ▲
                 / \
                /   \               1 E2E Test
               /     \              (Multi-agent multi-repo)
              /_______\
             /         \
            /           \           6 Integration Tests
           /             \          (Hot reload during queries, etc.)
          /_______________\
         /                 \
        /                   \       22 Unit Tests
       /                     \      (Individual method behavior)
      /_______________________\
```

**Distribution:**
- **Unit Tests**: 22 tests (76%) - Fast, isolated
- **Integration Tests**: 6 tests (21%) - Component interactions
- **E2E Tests**: 1 test (3%) - Full system validation

**Total**: 29 test functions across 3 test files

---

## Unit Testing

### Scope

**What to Unit Test:**
- Individual IndexManager methods (add_index, remove_index, reload_indexes)
- Lock type validation (RLock vs Lock)
- Config validation (Pydantic errors)
- Documentation completeness (docstring inspection)
- Error handling (ValueError, KeyError, RuntimeError)
- INDEX_REGISTRY usage (dynamic logic validation)

**What NOT to Unit Test:**
- Concurrent access (integration test)
- Lock performance (benchmark test)
- Index implementations (tested separately in index-specific test files)

### Coverage Target

**Overall**: ≥90% line coverage for modified code  
**Modified Methods**: 100% coverage for 7 methods (route_action, get_index, health_check_all, ensure_all_indexes_healthy, rebuild_index, update_from_watcher, get_stats)  
**New Methods**: 100% coverage for 3 hot reload methods (add_index, remove_index, reload_indexes)

**Coverage Exclusions:**
- `__init__` (initialization, not critical logic)
- Error handling for impossible conditions (defensive programming)
- Logging statements (tested via log analysis)

### Test Structure

**AAA Pattern** (Arrange-Act-Assert):

```python
def test_add_index_success():
    # Arrange
    manager = IndexManager(config, base_path)
    new_index = StandardsIndex(config.standards, base_path)
    
    # Act
    manager.add_index("new_standards", new_index)
    
    # Assert
    assert "new_standards" in manager._indexes
    assert manager.get_index("new_standards") == new_index
```

**Given-When-Then** (BDD style for complex scenarios):

```python
def test_reload_indexes_mixed():
    # Given: IndexManager with old config
    manager = IndexManager(old_config, base_path)
    
    # When: Reload with new config (add + remove)
    report = manager.reload_indexes(new_config)
    
    # Then: Report shows correct diff
    assert report["added"] == ["new_repo"]
    assert report["removed"] == ["old_repo"]
    assert report["kept"] == ["standards", "code"]
```

### Isolation Strategy

**Mock:**
- BaseIndex instances (use test doubles with predictable behavior)
- File system operations (not testing disk I/O, testing logic)
- Config loading (use in-memory test configs)

**Don't Mock:**
- `threading.RLock` (testing actual lock behavior)
- Dict operations (testing actual `_indexes` dict)
- IndexManager methods (testing real implementation)

**Test Doubles:**

```python
class MockIndex(BaseIndex):
    """Test double for index instances."""
    def search(self, **kwargs):
        return {"results": ["mock_result"]}
    
    def health_check(self):
        return {"status": "healthy"}
    
    def close(self):
        pass  # No-op for tests
```

### Organization

```
tests/ouroboros/subsystems/rag/
├── test_index_manager_hot_reload.py
│   ├── test_add_index_success()
│   ├── test_add_index_duplicate_raises_value_error()
│   ├── test_remove_index_success()
│   ├── test_remove_index_not_found_raises_key_error()
│   ├── test_reload_indexes_add_only()
│   ├── test_reload_indexes_remove_only()
│   ├── test_reload_indexes_mixed()
│   ├── test_reload_indexes_invalid_config()
│   ├── test_reload_indexes_unknown_index_type()
│   └── test_reload_uses_index_registry()
│
└── test_index_manager_thread_safety.py
    ├── test_lock_type_is_rlock()
    ├── test_no_gil_assumptions()
    ├── test_only_stdlib_threading_used()
    ├── test_documentation_completeness()
    └── test_docstring_code_examples_valid()
```

**Naming Convention:**
- `test_{method_name}_{scenario}()` - e.g., `test_add_index_duplicate_raises_value_error()`
- Descriptive names explain what's being tested
- Scenario describes expected behavior or error condition

---

## Integration Testing

### Scope

**What to Integration Test:**
- Concurrent access from multiple threads (race condition detection)
- Hot reload during concurrent queries (atomicity validation)
- Lock overhead under concurrent load (performance validation)
- Snapshot pattern during concurrent modifications (isolation validation)
- Re-entrant lock call chains (deadlock prevention)

**Critical Integration Scenarios:**
1. **Multi-Agent Queries**: 100 threads × 1000 queries = 100k concurrent operations
2. **Hot Reload Atomicity**: 50 query threads during `reload_indexes()` call
3. **Health Check Concurrency**: Health check during queries (snapshot validation)
4. **Stress Test**: 50 threads × 10s sustained load

### Test Harness

**Threading Test Harness:**

```python
def run_concurrent_test(workers: List[Callable], timeout: int = 30):
    """Execute worker functions concurrently, collect errors."""
    import threading
    
    errors = []
    threads = []
    
    for worker in workers:
        def wrapped_worker():
            try:
                worker()
            except Exception as e:
                errors.append((worker.__name__, e))
        
        thread = threading.Thread(target=wrapped_worker)
        threads.append(thread)
    
    # Start all threads
    for t in threads:
        t.start()
    
    # Wait for completion (with timeout)
    for t in threads:
        t.join(timeout=timeout)
    
    # Validate
    assert len(errors) == 0, f"Concurrent test failures: {errors}"
    assert all(not t.is_alive() for t in threads), "Threads deadlocked"
    
    return len(threads)
```

**Usage:**

```python
def test_concurrent_index_access():
    manager = IndexManager(config, base_path)
    
    def search_worker():
        for _ in range(1000):
            manager.route_action("search_code", query="test")
    
    workers = [search_worker for _ in range(100)]
    ops_count = run_concurrent_test(workers, timeout=30)
    
    assert ops_count == 100  # All threads completed
```

### Organization

```
tests/ouroboros/subsystems/rag/
├── test_index_manager_thread_safety.py
│   ├── test_concurrent_index_access()        # 100k ops integration
│   ├── test_reentrant_lock_call_chains()     # Call chain integration
│   ├── test_lock_overhead_negligible()       # Performance integration
│   ├── test_thread_safety_stress()           # Sustained load integration
│   ├── test_health_check_uses_snapshot()     # Snapshot concurrency
│   └── test_get_stats_uses_snapshot()        # Snapshot concurrency
│
└── test_index_manager_hot_reload.py
    ├── test_add_index_during_concurrent_queries()     # Hot reload integration
    ├── test_remove_index_during_concurrent_queries()  # Hot reload integration
    └── test_hot_reload_atomic_swap()                  # Atomic swap integration
```

### Execution Time Targets

| Test Type | Time Target | Rationale |
|-----------|-------------|-----------|
| Unit tests (22) | <1s total | Fast feedback loop |
| Integration tests (6) | <30s total | Acceptable for concurrent tests |
| E2E test (1) | <60s | Full system validation |
| **Total suite** | **<2 minutes** | CI/CD friendly |

---

## Performance Testing

### Benchmark Tests

**Purpose**: Validate quantitative NFRs (lock overhead <1%, hot reload <100ms)

**Framework**: pytest-benchmark or manual timing with `time.perf_counter()`

**Example:**

```python
def test_lock_overhead_negligible(benchmark):
    """Benchmark lock acquisition overhead."""
    manager = IndexManager(config, base_path)
    
    def query_with_locks():
        manager.route_action("search_code", query="test")
    
    result = benchmark(query_with_locks)
    
    # Validate
    assert result.stats["median"] < 0.051  # 50ms query + 1% = 50.5ms
```

**Measurement Precision**:
- Use `time.perf_counter()` for nanosecond precision
- Run ≥10 iterations for statistical validity
- Report median (robust to outliers)

---

## Stress Testing

### Purpose

Validate system stability under sustained load (NFR-R2: Deadlock Prevention, NFR-P2: Concurrent Throughput)

### Approach

```python
def test_thread_safety_stress():
    """50 threads × 10s sustained load."""
    manager = IndexManager(config, base_path)
    stop_event = threading.Event()
    errors = []
    
    def worker():
        while not stop_event.is_set():
            try:
                manager.route_action("search_code", query="test")
                time.sleep(0.01)  # ~100 ops/sec per thread
            except Exception as e:
                errors.append(e)
    
    threads = [threading.Thread(target=worker) for _ in range(50)]
    for t in threads:
        t.start()
    
    time.sleep(10)  # Sustained load
    stop_event.set()
    
    for t in threads:
        t.join(timeout=5)
    
    # Validate
    assert len(errors) == 0, f"Stress test failures: {errors}"
    assert all(not t.is_alive() for t in threads), "Threads hung"
```

**Metrics Collected:**
- Operations per second (throughput)
- Error rate (should be 0%)
- Memory usage (detect leaks)
- Thread count (detect thread leaks)

---

## Mocking Strategy

### When to Mock

**Mock External Dependencies:**
- ✅ File system I/O (use in-memory test data)
- ✅ Config file loading (use test config objects)
- ✅ Index implementations (use MockIndex for isolation)

**Don't Mock Core Logic:**
- ❌ `threading.RLock` (test real lock behavior)
- ❌ `dict` operations (test real `_indexes` dict)
- ❌ IndexManager methods (test actual implementation)

### Mock Patterns

**Fixture-Based Mocking (pytest):**

```python
@pytest.fixture
def mock_index_manager():
    """Fixture providing IndexManager with mock indexes."""
    config = TestConfig(indexes=["standards", "code"])
    manager = IndexManager(config, Path("/tmp/test"))
    
    # Replace real indexes with mocks
    manager._indexes["standards"] = MockStandardsIndex()
    manager._indexes["code"] = MockCodeIndex()
    
    return manager

def test_with_mocks(mock_index_manager):
    """Use fixture for fast, isolated test."""
    result = mock_index_manager.route_action("search_code", query="test")
    assert result == {"results": ["mock_result"]}
```

**Monkey Patching (for INDEX_REGISTRY):**

```python
def test_reload_with_mock_registry(monkeypatch):
    """Test dynamic logic with mocked registry."""
    mock_registry = {
        "standards": MockStandardsIndex,
        "code": MockCodeIndex,
        "test": MockTestIndex  # New type for test
    }
    
    monkeypatch.setattr("ouroboros.subsystems.rag.INDEX_REGISTRY", mock_registry)
    
    config = IndexesConfig(indexes=["test"])
    manager = IndexManager(config, base_path)
    
    # Validate: Used mocked registry
    assert isinstance(manager._indexes["test"], MockTestIndex)
```

---

## Test Execution

### Local Development

**Run all tests:**
```bash
pytest tests/ouroboros/subsystems/rag/
```

**Run specific test file:**
```bash
pytest tests/ouroboros/subsystems/rag/test_index_manager_thread_safety.py
```

**Run specific test:**
```bash
pytest tests/ouroboros/subsystems/rag/test_index_manager_thread_safety.py::test_concurrent_index_access
```

**Run with coverage:**
```bash
pytest tests/ouroboros/subsystems/rag/ \
    --cov=ouroboros.subsystems.rag.index_manager \
    --cov-report=term-missing \
    --cov-report=html
```

**Run stress tests only:**
```bash
pytest tests/ouroboros/subsystems/rag/ -k stress
```

### CI/CD

**GitHub Actions / CI Pipeline:**

```yaml
# .github/workflows/test.yml
- name: Run thread safety tests
  run: |
    pytest tests/ouroboros/subsystems/rag/test_index_manager_thread_safety.py \
      --cov=ouroboros.subsystems.rag.index_manager \
      --cov-fail-under=90

- name: Run hot reload tests
  run: pytest tests/ouroboros/subsystems/rag/test_index_manager_hot_reload.py

- name: Run logging tests
  run: pytest tests/ouroboros/subsystems/rag/test_index_manager_logging.py
```

**Pre-commit Hook:**
```bash
# .git/hooks/pre-commit
pytest tests/ouroboros/subsystems/rag/ --maxfail=1 --tb=short
```

---

## Coverage Targets

### Overall Coverage

**Target**: ≥90% line coverage for IndexManager

**Measurement**:
```bash
pytest --cov=ouroboros.subsystems.rag.index_manager \
       --cov-report=term-missing
```

**Expected Output:**
```
Name                                   Stmts   Miss  Cover   Missing
---------------------------------------------------------------------
ouroboros/subsystems/rag/index_manager.py   250     25    90%   123-145, 678
---------------------------------------------------------------------
TOTAL                                   250     25    90%
```

### Critical Path Coverage

**Must be 100%:**
- All 7 modified methods (route_action, get_index, health_check_all, ensure_all_indexes_healthy, rebuild_index, update_from_watcher, get_stats)
- All 3 hot reload methods (add_index, remove_index, reload_indexes)
- All lock acquisition paths

**Allowed <100%:**
- Error handling for impossible conditions
- Defensive programming (e.g., logging failures)

---

## Test Data Management

### Test Configs

**Inline Test Configs:**

```python
def test_config():
    """Minimal config for testing."""
    return IndexesConfig(
        indexes=["standards", "code"],
        base_path=Path("/tmp/test"),
        # ... minimal required fields
    )
```

**Fixture-Based Configs:**

```python
@pytest.fixture
def multi_repo_config():
    """Config simulating 10-repo deployment."""
    return IndexesConfig(
        indexes=["repo1", "repo2", ..., "repo10"],
        # ...
    )
```

### Test Isolation

**Between Tests:**
- Each test gets fresh IndexManager instance
- No shared state between tests
- Teardown: Clean up any test artifacts (if created)

**Within Tests:**
- Use separate config objects
- Don't modify shared fixtures
- Mock external dependencies for speed

---

## Debugging Failed Tests

### Thread Safety Failures

**Symptom**: Exceptions during `test_concurrent_index_access()`

**Debug Steps:**
1. Run test with increased logging: `pytest -s -v`
2. Reduce thread count to isolate: Change 100 threads → 10 threads
3. Add print statements in lock-protected sections
4. Check for unprotected `_indexes` accesses: `grep "self._indexes" index_manager.py`
5. Validate lock type: `assert isinstance(_indexes_lock, RLock)`

**Common Causes:**
- Missing lock on `_indexes` access
- Lock held during expensive operation (blocking)
- Wrong lock type (Lock instead of RLock)

### Hot Reload Failures

**Symptom**: Exceptions during `test_hot_reload_atomic_swap()`

**Debug Steps:**
1. Check query results for partial state: Validate results match old OR new config
2. Increase reload logging: Log every add/remove operation
3. Reduce query thread count for easier debugging
4. Verify atomic swap: All dict mods under single lock acquisition

**Common Causes:**
- Multiple lock acquisitions (not atomic)
- Cleanup inside lock (blocking queries)
- Config validation missing

### Performance Test Failures

**Symptom**: `test_lock_overhead_negligible()` fails (>1% overhead)

**Debug Steps:**
1. Profile lock acquisition: Use `py-spy` or `cProfile`
2. Check for lock contention: Increase timeout, see if it passes
3. Validate test environment: Isolated system, no other load
4. Measure baseline: Run without locks to establish baseline

**Common Causes:**
- System load affecting measurement
- Contention from other threads
- Incorrect measurement (including I/O in lock time)

---

## Test Maintenance

### When to Update Tests

**Triggers:**
1. New method added → Add unit test
2. New concurrency scenario → Add integration test
3. New NFR added → Add verification test
4. Bug found → Add regression test

### Test Review Checklist

- [ ] Test name is descriptive
- [ ] Test has clear AAA/Given-When-Then structure
- [ ] Test asserts specific behavior (not generic "works")
- [ ] Test runs in <1s (unit) or <30s (integration)
- [ ] Test is isolated (no external dependencies)
- [ ] Test failure message is actionable

---

## Summary

| Test Type | Count | Target | File Location |
|-----------|-------|--------|---------------|
| **Unit Tests** | 22 | <1s total | `test_index_manager_hot_reload.py`, `test_index_manager_thread_safety.py` |
| **Integration Tests** | 6 | <30s total | `test_index_manager_thread_safety.py`, `test_index_manager_hot_reload.py` |
| **E2E Tests** | 1 | <60s | `test_index_manager_thread_safety.py` |
| **Logging Tests** | 4 | <5s | `test_index_manager_logging.py` |
| **TOTAL** | **33** | **<2 min** | **3 test files** |

**Coverage**: ≥90% for IndexManager, 100% for critical paths

**Execution**: Local (pytest), CI/CD (GitHub Actions), Pre-commit hook

**Philosophy**: Evidence-based thread safety, standards-driven, fast feedback

---

**Document Version:** 1.0  
**Last Updated:** 2025-11-20  
**Status:** Testing strategy complete - Ready for consolidation (Task 8)


