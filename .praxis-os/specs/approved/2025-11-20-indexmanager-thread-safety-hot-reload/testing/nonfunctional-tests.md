# Non-Functional Tests Plan

**Project:** IndexManager Thread Safety, Hot Reload, and Dynamic Logic Implementation  
**Date:** 2025-11-20  
**Purpose:** Verification tests for performance, reliability, and quality requirements  
**Test Files:** `test_index_manager_thread_safety.py`, `test_index_manager_hot_reload.py`, `test_index_manager_logging.py`

---

## NFR Testing Overview

### Categories Tested

1. **Performance (NFR-P)**: Latency, throughput, resource usage
2. **Reliability (NFR-R)**: Race conditions, deadlocks, state consistency
3. **Maintainability (NFR-M)**: Documentation, test coverage, extensibility
4. **Consistency (NFR-C)**: Architectural patterns, compatibility
5. **Observability (NFR-O)**: Logging, metrics, visibility
6. **Security/Simplicity (NFR-S)**: Dependencies, supply chain

### Measurement Principles

- **Objective**: All metrics are measurable and binary (pass/fail)
- **Repeatable**: Tests produce consistent results across runs
- **Automated**: All tests run in CI/CD pipeline
- **Evidence-Based**: Claims validated through measurement

---

## Performance Tests (NFR-P)

### NFR-P1: Lock Overhead Negligibility

**Requirement:** RLock overhead <1% of query latency

**Metric Target:** <1% performance regression vs. baseline

**Test Specification:**

- **Test Function:** `test_lock_overhead_negligible()`
- **File:** `test_index_manager_thread_safety.py`
- **Measurement Method:**
  1. Benchmark 10,000 index queries with RLock protection
  2. Measure total execution time using `time.perf_counter()` (nanosecond precision)
  3. Compare to theoretical baseline (50ms per query × 10k = 500s)
- **Setup:**
  - IndexManager with test config
  - No other system load
  - 10k queries prepared
- **Execution:**
  ```python
  start = time.perf_counter()
  for _ in range(10000):
      manager.route_action("search_code", query="test")
  duration = time.perf_counter() - start
  ```
- **Pass Criteria:**
  - Total duration <505s (500s baseline + 1% = 505s)
  - Lock acquisition time documented: ~0.9ns per operation
  - Assert: `duration < 505`, failure message includes overhead %
- **Failure Diagnostics:**
  - If >1% overhead: Profile lock acquisition, check for contention
  - Expected: I/O dominates (10-100ms queries >> 1ns lock time)
- **Measurement Output:**
  ```
  Lock overhead: 2s over 500s = 0.4% ✅
  Lock acquisition time: ~0.9ns per operation
  I/O dominates: 50ms query >> 0.9ns lock (55,555,556x)
  ```

---

### NFR-P2: Concurrent Query Throughput

**Requirement:** Support ≥100 concurrent query threads without throughput degradation

**Metric Target:** 100 threads × 1000 queries = 100k operations, no degradation

**Test Specification:**

- **Test Function:** `test_concurrent_index_access()`
- **File:** `test_index_manager_thread_safety.py`
- **Measurement Method:**
  1. Spawn 100 threads, each performing 1000 queries
  2. Measure total throughput (ops/sec)
  3. Compare to sequential baseline
- **Setup:**
  - IndexManager initialized
  - 100 threads prepared
  - No external load
- **Execution:**
  ```python
  def worker():
      for _ in range(1000):
          manager.route_action("search_code", query="test")
  
  threads = [Thread(target=worker) for _ in range(100)]
  start = time.perf_counter()
  for t in threads: t.start()
  for t in threads: t.join()
  duration = time.perf_counter() - start
  throughput = 100_000 / duration  # ops/sec
  ```
- **Pass Criteria:**
  - All 100k operations complete successfully (zero exceptions)
  - Throughput ≥95% of theoretical max (allowing 5% overhead)
  - No measurable degradation over time
- **Failure Diagnostics:**
  - If throughput <95%: Check lock contention with `threading.active_count()`
  - If exceptions: Race condition detected (critical failure)
- **Measurement Output:**
  ```
  100k operations in 520s = 192 ops/sec ✅
  Theoretical max: 200 ops/sec (50ms per query)
  Efficiency: 96% ✅
  ```

---

### NFR-P3: Hot Reload Operation Speed

**Requirement:** Hot reload <100ms to minimize query disruption

**Metric Target:** 
- `add_index()`: <50ms
- `remove_index()`: <50ms
- `reload_indexes()`: <100ms for 10-repo config

**Test Specification:**

- **Test Function:** `test_hot_reload_latency()`
- **File:** `test_index_manager_hot_reload.py`
- **Measurement Method:**
  1. Measure each hot reload operation with `time.perf_counter()`
  2. Average over 100 runs for statistical validity
  3. Validate p95 < target (95% of operations meet target)
- **Setup:**
  - IndexManager with 10 existing indexes
  - Operations prepared in advance
- **Execution:**
  ```python
  latencies = []
  for _ in range(100):
      start = time.perf_counter()
      manager.add_index("temp", new_index)
      latency = (time.perf_counter() - start) * 1000  # ms
      latencies.append(latency)
      manager.remove_index("temp")
  
  p95 = sorted(latencies)[95]
  ```
- **Pass Criteria:**
  - add_index p95 <50ms
  - remove_index p95 <50ms
  - reload_indexes p95 <100ms
  - Assert with failure message including actual p95
- **Failure Diagnostics:**
  - If >target: Profile lock acquisition, check cleanup time
  - Expected: Dict operations <10ns, cleanup outside lock
- **Measurement Output:**
  ```
  add_index: p50=12ms, p95=35ms ✅ (<50ms target)
  remove_index: p50=15ms, p95=42ms ✅ (<50ms target)
  reload_indexes: p50=45ms, p95=87ms ✅ (<100ms target)
  ```

---

## Reliability Tests (NFR-R)

### NFR-R1: Zero Race Conditions

**Requirement:** Zero race conditions under concurrent access from 4 contexts over 100k operations

**Metric Target:** Zero exceptions, zero data corruption

**Test Specification:**

- **Test Function:** `test_concurrent_index_access()`
- **File:** `test_index_manager_thread_safety.py`
- **Measurement Method:**
  1. 100 threads × 1000 ops = 100k concurrent operations
  2. Mix of 4 execution contexts (asyncio, thread pool, watchdog, timer)
  3. Track all exceptions and data corruption
- **Setup:**
  - IndexManager with test config
  - Error collection: `errors = []`
  - 100 threads simulating 4 contexts
- **Execution:**
  ```python
  errors = []
  def worker():
      try:
          manager.route_action("search_code", query="test")
      except Exception as e:
          errors.append(e)
  
  # ... run 100k operations ...
  assert len(errors) == 0, f"Race conditions detected: {errors}"
  ```
- **Pass Criteria:**
  - Zero exceptions raised (strict requirement)
  - Zero data corruption (results match sequential baseline)
  - All operations complete within timeout
- **Failure Diagnostics:**
  - Any exception = critical failure (race condition detected)
  - ThreadSanitizer (if available) reports zero warnings
- **Measurement Output:**
  ```
  100k operations: 0 exceptions ✅
  Data integrity: 100% match vs baseline ✅
  ThreadSanitizer: 0 warnings ✅
  ```

---

### NFR-R2: Deadlock Prevention

**Requirement:** No deadlocks possible with RLock + re-entrant call chains

**Metric Target:** All 3 re-entrant call chains execute, 10s stress test completes

**Test Specification:**

- **Test Function:** `test_reentrant_lock_call_chains()`, `test_thread_safety_stress()`
- **File:** `test_index_manager_thread_safety.py`
- **Measurement Method:**
  1. Test each of 3 re-entrant call chains
  2. Run 10s stress test (50 threads sustained load)
  3. Monitor for deadlocks (timeout detection)
- **Setup:**
  - IndexManager with test config
  - Call chain scenarios prepared
  - Timeout: 30s max per test
- **Execution:**
  ```python
  # Test call chain 1
  result = manager.route_action("search_code", query="test")
  # Internally calls: route→get_index (re-entrant)
  assert result is not None  # Proves no deadlock
  
  # Stress test
  start = time.time()
  while time.time() - start < 10:
      manager.route_action(...)  # Continuous operations
  # If deadlock occurs, test times out
  ```
- **Pass Criteria:**
  - All 3 call chains complete successfully
  - Stress test completes in 10s (no timeout)
  - No threads hanging (check `threading.active_count()`)
- **Failure Diagnostics:**
  - Timeout = deadlock detected (critical failure)
  - Expected: RLock allows same-thread re-acquisition
- **Measurement Output:**
  ```
  Call chain 1 (route→get): ✅ No deadlock
  Call chain 2 (ensure→rebuild→get): ✅ No deadlock
  Call chain 3 (update→get): ✅ No deadlock
  Stress test 10s: ✅ Completed (no timeout)
  ```

---

### NFR-R3: Atomic State Transitions

**Requirement:** Hot reload atomic - queries see old OR new state, never partial

**Metric Target:** During reload, all queries complete successfully with correct results (old or new state only)

**Test Specification:**

- **Test Function:** `test_hot_reload_atomic_swap()`
- **File:** `test_index_manager_hot_reload.py`
- **Measurement Method:**
  1. Start 50 continuous query threads
  2. Trigger `reload_indexes()` mid-flight
  3. Validate query results match either old OR new config (never mixed)
- **Setup:**
  - IndexManager with config A
  - 50 query threads started
  - Config B prepared (different repos)
- **Execution:**
  ```python
  query_results = []
  def worker():
      result = manager.route_action(...)
      query_results.append(result)
  
  # Start queries
  # Trigger reload mid-flight
  manager.reload_indexes(config_B)
  
  # Validate results
  for result in query_results:
      assert is_valid_state(result, [config_A, config_B])
      assert not is_partial_state(result)
  ```
- **Pass Criteria:**
  - All queries complete successfully (zero exceptions)
  - All results valid for either old OR new config
  - No results show partial state (mixture of old+new)
- **Failure Diagnostics:**
  - Partial state detected = atomicity violated (critical failure)
  - Expected: All dict modifications under single lock acquisition
- **Measurement Output:**
  ```
  50 threads during reload: 0 exceptions ✅
  Results validation:
    - Old state: 23 queries ✅
    - New state: 27 queries ✅
    - Partial state: 0 queries ✅ (CRITICAL)
  Atomicity: 100% ✅
  ```

---

## Maintainability Tests (NFR-M)

### NFR-M1: Code Documentation Coverage

**Requirement:** Comprehensive threading model docs enabling safe modifications

**Metric Target:**
- Class docstring documents 4 contexts
- 7 method docstrings include "Thread Safety:" section
- References 4 concurrency standards

**Test Specification:**

- **Test Function:** `test_documentation_completeness()`
- **File:** `test_index_manager_thread_safety.py`
- **Measurement Method:**
  1. Inspect `IndexManager.__doc__` (class docstring)
  2. Inspect 7 modified method docstrings
  3. Search for required keywords and standards references
- **Setup:**
  - Import IndexManager class
  - Prepare regex patterns for validation
- **Execution:**
  ```python
  doc = IndexManager.__doc__
  assert "Threading Model" in doc
  assert "asyncio" in doc and "thread pool" in doc  # 4 contexts
  assert "python-concurrency.md" in doc  # Standards refs
  
  for method in modified_methods:
      assert "Thread Safety:" in method.__doc__
  ```
- **Pass Criteria:**
  - Class docstring contains all required sections
  - All 4 concurrent contexts documented
  - Lock usage pattern example included
  - 4 standards referenced
  - All 7 methods have threading documentation
- **Failure Diagnostics:**
  - Missing section = documentation incomplete
  - Use checklist from NFR-M1 requirements
- **Measurement Output:**
  ```
  Class docstring: ✅ Contains "Threading Model"
  4 contexts documented: ✅ (asyncio, thread pool, watchdog, timer)
  Lock example: ✅ Code snippet present
  Standards refs: ✅ (4/4 present)
  Method docstrings: ✅ (7/7 have "Thread Safety:")
  ```

---

### NFR-M2: Test Suite Completeness

**Requirement:** Comprehensive test coverage for all concurrency scenarios

**Metric Target:**
- Concurrent access test (100k ops)
- Lock overhead benchmark (<1%)
- Stress test (50 threads × 10s)
- Hot reload integration test

**Test Specification:**

- **Test Function:** `test_suite_completeness()` (meta-test)
- **File:** `test_index_manager_thread_safety.py`
- **Measurement Method:**
  1. Verify all required test functions exist
  2. Run test suite, collect metrics
  3. Validate code coverage ≥90%
- **Setup:**
  - pytest discovery
  - coverage.py installed
- **Execution:**
  ```bash
  pytest tests/ouroboros/subsystems/rag/ \
    --cov=ouroboros.subsystems.rag.index_manager \
    --cov-report=term-missing
  ```
- **Pass Criteria:**
  - All 28+ test functions present
  - All tests passing (100% success rate)
  - Code coverage ≥90% for IndexManager
  - Modified methods have 100% coverage
- **Failure Diagnostics:**
  - <90% coverage = identify untested code paths
  - Missing test = add to test suite
- **Measurement Output:**
  ```
  Test functions: 28/28 ✅
  Test pass rate: 100% (28/28 passed) ✅
  Code coverage:
    - IndexManager overall: 94% ✅ (≥90% target)
    - Modified methods: 100% ✅
    - Untested lines: 12 (non-critical paths)
  ```

---

### NFR-M3: Dynamic Logic Extensibility

**Requirement:** INDEX_REGISTRY enables new index types without code changes

**Metric Target:**
- `reload_indexes()` iterates INDEX_REGISTRY (not hardcoded)
- New index type requires zero IndexManager changes

**Test Specification:**

- **Test Function:** `test_reload_uses_index_registry()`
- **File:** `test_index_manager_hot_reload.py`
- **Measurement Method:**
  1. Grep index_manager.py for hardcoded index names
  2. Validate reload_indexes() uses INDEX_REGISTRY
  3. Test: Add new index type via registry, verify works without code mods
- **Setup:**
  - Mock new index type
  - Add to INDEX_REGISTRY dynamically
- **Execution:**
  ```python
  # Add new index type to registry (no code changes)
  INDEX_REGISTRY["mock_index"] = MockIndex
  
  # Reload with new config
  config = IndexesConfig(indexes=["standards", "mock_index"])
  manager.reload_indexes(config)
  
  # Verify new index works
  result = manager.route_action("search_mock", query="test")
  assert result is not None
  ```
- **Pass Criteria:**
  - Zero hardcoded index names in index_manager.py
  - reload_indexes() uses `INDEX_REGISTRY.keys()` or `.items()`
  - New index type works without IndexManager modifications
- **Failure Diagnostics:**
  - Hardcoded name found = violates dynamic logic
  - Expected: All index discovery via registry
- **Measurement Output:**
  ```
  Hardcoded index names: 0 ✅
  Registry usage: ✅ reload_indexes() iterates INDEX_REGISTRY
  Extensibility test:
    - Added "mock_index" to registry ✅
    - Reload succeeded ✅
    - New index queryable ✅
    - Zero IndexManager code changes ✅
  ```

---

## Consistency Tests (NFR-C)

### NFR-C1: Architectural Consistency

**Requirement:** Match WorkflowEngine pattern (RLock for dict orchestration)

**Metric Target:**
- `_indexes_lock` is `threading.RLock`
- Pattern matches `WorkflowEngine._dynamic_lock`

**Test Specification:**

- **Test Function:** `test_lock_type_is_rlock()`
- **File:** `test_index_manager_thread_safety.py`
- **Measurement Method:**
  1. Inspect IndexManager._indexes_lock type
  2. Compare to WorkflowEngine pattern (reference check)
- **Setup:**
  - Import IndexManager
  - Import WorkflowEngine (for comparison)
- **Execution:**
  ```python
  manager = IndexManager(config, base_path)
  assert isinstance(manager._indexes_lock, threading.RLock)
  
  # Pattern match validation
  workflow_engine = WorkflowEngine(...)
  assert type(manager._indexes_lock) == type(workflow_engine._dynamic_lock)
  ```
- **Pass Criteria:**
  - `_indexes_lock` is RLock (not Lock or other)
  - Pattern matches WorkflowEngine (consistency)
- **Failure Diagnostics:**
  - Wrong type = architecture inconsistency
- **Measurement Output:**
  ```
  Lock type: threading.RLock ✅
  Pattern match: ✅ (matches WorkflowEngine._dynamic_lock)
  ```

---

### NFR-C2: Python 3.13 Compatibility

**Requirement:** No GIL reliance, explicit locks protect all shared state

**Metric Target:** Design inspection confirms no GIL assumptions

**Test Specification:**

- **Test Function:** `test_no_gil_assumptions()`
- **File:** `test_index_manager_thread_safety.py`
- **Measurement Method:**
  1. Code inspection: Verify all `_indexes` accesses under lock
  2. Design review: Confirm explicit synchronization
  3. Future: Run on Python 3.13 with `PYTHON_GIL=0` when stable
- **Setup:**
  - Code review checklist
  - Audit all access sites
- **Execution:**
  ```python
  # Static analysis
  access_sites = grep_for("self._indexes", index_manager.py)
  for site in access_sites:
      assert is_under_lock(site), f"Unprotected access: {site}"
  
  # Design check
  assert "No GIL assumptions" in IndexManager.__doc__
  ```
- **Pass Criteria:**
  - All 12 `_indexes` access sites under lock
  - Documentation states "GIL-independent"
  - Future: Passes on Python 3.13 free-threaded mode
- **Failure Diagnostics:**
  - Unprotected access = GIL assumption (future bug)
- **Measurement Output:**
  ```
  Access sites audited: 12/12 ✅
  Protected by lock: 12/12 ✅
  GIL-independent: ✅ (explicit locks only)
  Python 3.13 ready: ✅ (design compliant, testing deferred)
  ```

---

## Observability Tests (NFR-O)

### NFR-O1: Structured Logging for Operations

**Requirement:** Machine-readable logs with `extra={}` dict, 5+ event types

**Metric Target:**
- All operations logged
- jq parseable
- 5+ event types

**Test Specification:**

- **Test Function:** `test_log_format_consistent()`
- **File:** `test_index_manager_logging.py`
- **Measurement Method:**
  1. Capture log output during operations
  2. Parse with jq (or Python json module)
  3. Validate format consistency
- **Setup:**
  - Capture log handler
  - Perform operations (query, add, remove, reload, rebuild)
- **Execution:**
  ```python
  with LogCapture() as logs:
      manager.route_action("search_code", query="test")
      manager.add_index("temp", new_index)
      # ... other operations ...
  
  for log in logs:
      data = json.loads(log)  # Must be JSON parseable
      assert "event" in data
      assert "timestamp" in data
  ```
- **Pass Criteria:**
  - All logs are valid JSON
  - `extra={}` dict contains metadata
  - 5+ event types present (index_query, index_added, index_removed, indexes_reloaded, index_rebuilt)
  - jq queries work (e.g., `jq '.latency_ms'`)
- **Failure Diagnostics:**
  - JSON parse error = format broken
  - Missing event = operation not logged
- **Measurement Output:**
  ```
  Log format: JSON ✅
  Event types: 5 (query, added, removed, reloaded, rebuilt) ✅
  jq parseable: ✅
  Structured metadata: ✅ (latency_ms, index_name, etc.)
  ```

---

### NFR-O2: Query Latency Visibility

**Requirement:** Log query latency to enable p50/p95/p99 analysis

**Metric Target:** Each query logs latency_ms

**Test Specification:**

- **Test Function:** `test_query_latency_logged()`
- **File:** `test_index_manager_logging.py`
- **Measurement Method:**
  1. Perform 100 queries
  2. Extract latency_ms from logs
  3. Compute p50/p95/p99
- **Setup:**
  - Capture log output
  - 100 queries prepared
- **Execution:**
  ```python
  with LogCapture() as logs:
      for _ in range(100):
          manager.route_action("search_code", query="test")
  
  latencies = [json.loads(log)["latency_ms"] for log in logs]
  p50 = sorted(latencies)[50]
  p95 = sorted(latencies)[95]
  p99 = sorted(latencies)[99]
  ```
- **Pass Criteria:**
  - All 100 queries logged
  - Each log has `latency_ms` field
  - Latencies are positive numbers
  - p95 analysis possible
- **Failure Diagnostics:**
  - Missing latency = incomplete logging
- **Measurement Output:**
  ```
  Queries logged: 100/100 ✅
  latency_ms present: 100% ✅
  p50: 45ms, p95: 87ms, p99: 152ms ✅
  Analysis enabled: ✅
  ```

---

## Security/Simplicity Tests (NFR-S)

### NFR-S1: No External Dependencies for Thread Safety

**Requirement:** Use only Python stdlib threading, no third-party locks

**Metric Target:** `import threading` only, requirements.txt unchanged

**Test Specification:**

- **Test Function:** `test_only_stdlib_threading_used()`
- **File:** `test_index_manager_thread_safety.py`
- **Measurement Method:**
  1. Grep import statements in index_manager.py
  2. Validate no third-party sync libraries
  3. Check requirements.txt for new dependencies
- **Setup:**
  - Access to codebase
  - requirements.txt baseline
- **Execution:**
  ```python
  imports = extract_imports("index_manager.py")
  threading_imports = [i for i in imports if "lock" in i.lower()]
  
  assert threading_imports == ["import threading"]
  assert "gevent" not in imports
  assert "eventlet" not in imports
  
  # Check requirements.txt
  requirements = read_requirements()
  assert "threading" not in requirements  # stdlib, not in requirements
  ```
- **Pass Criteria:**
  - Only `import threading` for synchronization
  - No gevent, eventlet, asyncio.Lock, or other third-party
  - requirements.txt unchanged (no new lock dependencies)
- **Failure Diagnostics:**
  - Third-party import = supply chain risk
- **Measurement Output:**
  ```
  Threading imports: 1 (import threading) ✅
  Third-party locks: 0 ✅
  requirements.txt: unchanged ✅
  Supply chain risk: minimal ✅
  ```

---

## Test Execution Guidance

### Performance Tests

**Environment:**
- Isolated system (no other load)
- Clean state (cold cache)
- Multiple runs for statistical validity (min 3 runs, report median)

**Tools:**
- `time.perf_counter()` for ns precision
- `pytest-benchmark` for automated benchmarking
- `perf` or `py-spy` for profiling

---

### Reliability Tests

**Environment:**
- Concurrent execution (ThreadPoolExecutor)
- Fault injection capability (mock failures)
- Timeout monitoring (detect deadlocks)

**Tools:**
- `pytest-xdist` for parallel test execution
- `ThreadSanitizer` (if available in Python build)
- `pytest-timeout` for deadlock detection

---

### Observability Tests

**Environment:**
- Log capture handlers
- JSON parsing tools (jq or Python json)

**Tools:**
- `pytest-loguru` or built-in `caplog`
- `jq` command-line for log analysis validation

---

## Summary

| Category | NFRs | Test Functions | Measurement Type | Target Metrics |
|----------|------|----------------|------------------|----------------|
| **Performance (P)** | 3 | 3 | Latency, throughput | <1% overhead, 100 threads, <100ms reload |
| **Reliability (R)** | 3 | 4 | Race conditions, deadlocks, atomicity | Zero exceptions, no timeouts, 100% atomic |
| **Maintainability (M)** | 3 | 3 | Documentation, coverage, extensibility | 4 contexts, ≥90% coverage, zero hardcoded |
| **Consistency (C)** | 2 | 2 | Pattern match, GIL-independence | RLock type, explicit locks |
| **Observability (O)** | 2 | 2 | Log format, latency visibility | 5+ events, jq parseable |
| **Security/Simplicity (S)** | 1 | 1 | Dependency check | stdlib only |
| **TOTAL** | **14** | **15** | **Objective measurements** | **100% measurable** |

**All NFRs have objective, measurable verification tests.**

---

**Document Version:** 1.0  
**Last Updated:** 2025-11-20  
**Status:** NFR tests complete - Ready for test strategy (Task 7)


