# Functional Tests Plan

**Project:** IndexManager Thread Safety, Hot Reload, and Dynamic Logic Implementation  
**Date:** 2025-11-20  
**Purpose:** Detailed test cases for all functional requirements  
**Test File:** `tests/ouroboros/subsystems/rag/test_index_manager_thread_safety.py`, `test_index_manager_hot_reload.py`, `test_index_manager_logging.py`

---

## Test Case Format

Each functional requirement has multiple test cases covering:
- **Happy Path**: Feature works as expected under normal conditions
- **Error Handling**: Gracefully handles error conditions with actionable messages
- **Edge Cases**: Boundary conditions and corner cases
- **Integration**: Multi-component interaction scenarios

---

## FR-001: Thread-Safe Dictionary Access

**Requirement:** The system shall protect all access to the `_indexes` dictionary with the same `RLock` mechanism to prevent race conditions across 4 concurrent execution contexts.

**Acceptance Criteria:**
- All `_indexes` accesses protected by RLock
- Zero race conditions in 100k ops test
- Works across 4 contexts (asyncio, thread pool, watchdog, timer)

### Test Cases

#### Happy Path: Concurrent Access from Multiple Contexts

- **Test Function:** `test_concurrent_index_access()`
- **File:** `test_index_manager_thread_safety.py`
- **Setup:**
  - Initialize IndexManager with test config
  - Prepare 100 threads simulating 4 execution contexts:
    - 60 threads: asyncio event loop (sync tool handlers)
    - 20 threads: thread pool (asyncio.to_thread for health checks)
    - 10 threads: watchdog observer (file watcher callbacks)
    - 10 threads: timer threads (debounce updates)
- **Action:**
  - Each thread performs 1000 operations (100k total):
    - `route_action("search_code", query="test")` (80% of ops)
    - `health_check_all()` (10% of ops)
    - `update_from_watcher("code", [Path("test.py")])` (10% of ops)
- **Expected:**
  - All 100k operations complete successfully
  - Zero exceptions raised
  - Zero data corruption detected
  - All threads complete within 30s timeout
  - Results match sequential baseline
- **Verifies:**
  - Acceptance criterion 1: All accesses protected
  - Acceptance criterion 2: Zero race conditions
  - Acceptance criterion 3: Works across 4 contexts

#### Edge Case: Lock Under High Contention

- **Test Function:** `test_lock_contention_high_load()`
- **File:** `test_index_manager_thread_safety.py`
- **Setup:**
  - 200 threads (2x normal load)
  - All threads access same index simultaneously
- **Action:**
  - Simulate worst-case contention scenario
- **Expected:**
  - Lock acquisition may be slower but still works
  - No deadlocks
  - All operations eventually complete
- **Verifies:**
  - System remains functional under extreme contention

#### Edge Case: No Indexes Available

- **Test Function:** `test_concurrent_access_empty_indexes()`
- **File:** `test_index_manager_thread_safety.py`
- **Setup:**
  - IndexManager with empty `_indexes` dict
  - 50 threads attempting queries
- **Action:**
  - All threads call `route_action()` on non-existent index
- **Expected:**
  - All threads receive `IndexError` (graceful)
  - No crashes or deadlocks
- **Verifies:**
  - Thread safety works even with no indexes

---

## FR-002: Re-entrant Lock Implementation

**Requirement:** The system shall use `threading.RLock` (not `threading.Lock`) for `_indexes` protection to support 3 identified re-entrant call chains.

**Acceptance Criteria:**
- `_indexes_lock` is `threading.RLock` (not Lock)
- 3 re-entrant call chains execute without deadlock
- Lock type validated in tests

### Test Cases

#### Happy Path: Re-entrant Call Chains Execute

- **Test Function:** `test_reentrant_lock_call_chains()`
- **File:** `test_index_manager_thread_safety.py`
- **Setup:**
  - Initialize IndexManager with test config
  - Prepare call chain scenarios
- **Action:**
  - Test call chain 1: `route_action()` → `_get_required_indexes_for_action()` → `get_index()`
  - Test call chain 2: `ensure_all_indexes_healthy()` → `rebuild_index()` → `get_index()`
  - Test call chain 3: `update_from_watcher()` → `get_index()`
- **Expected:**
  - All 3 call chains complete successfully
  - No deadlocks (same thread acquires lock multiple times)
  - Operations return correct results
- **Verifies:**
  - Acceptance criterion 2: All 3 chains work
  - RLock's re-entrant property is essential

#### Happy Path: Lock Type Validation

- **Test Function:** `test_lock_type_is_rlock()`
- **File:** `test_index_manager_thread_safety.py`
- **Setup:**
  - Initialize IndexManager
- **Action:**
  - Inspect `manager._indexes_lock`
- **Expected:**
  - `assert isinstance(manager._indexes_lock, threading.RLock)`
  - Not `threading.Lock` or other type
- **Verifies:**
  - Acceptance criterion 1: RLock used (not Lock)

#### Error Simulation: What If Lock Was Used

- **Test Function:** `test_lock_vs_rlock_deadlock_demo()` (documentation test, may be skipped in CI)
- **File:** `test_index_manager_thread_safety.py`
- **Setup:**
  - Mock scenario where Lock is used instead of RLock
- **Action:**
  - Attempt re-entrant call chain
- **Expected:**
  - Deadlock occurs (test times out or detects deadlock)
  - Demonstrates why RLock is required
- **Verifies:**
  - Design decision justification

---

## FR-003: Concurrent Query Support

**Requirement:** The system shall support at least 100 concurrent AI agents executing index queries simultaneously without race conditions, data corruption, or performance degradation.

**Acceptance Criteria:**
- Support ≥100 concurrent query threads
- Zero race conditions
- Zero data corruption
- No measurable performance degradation

### Test Cases

#### Happy Path: 100 Concurrent Queries

- **Test Function:** `test_concurrent_queries_100_agents()`
- **File:** `test_index_manager_thread_safety.py`
- **Setup:**
  - Initialize IndexManager
  - Prepare 100 threads (simulating 100 AI agents)
- **Action:**
  - Each thread: 100 queries = 10k total operations
  - Mix of search operations on different indexes
- **Expected:**
  - All 10k queries complete successfully
  - Zero exceptions
  - Results are correct (match sequential baseline)
  - No measurable performance degradation (<5% slower than sequential)
- **Verifies:**
  - All acceptance criteria

#### Stress Test: Sustained Load

- **Test Function:** `test_thread_safety_stress()`
- **File:** `test_index_manager_thread_safety.py`
- **Setup:**
  - 50 threads (multi-agent system)
  - 10 seconds sustained load
- **Action:**
  - Continuous queries for 10s: ~100 ops/sec per thread = ~50k ops total
  - Mix of reads (queries) and writes (rebuilds)
- **Expected:**
  - Zero crashes
  - Zero exceptions
  - Zero data corruption
  - Performance remains stable over 10s (no degradation)
- **Verifies:**
  - System can handle sustained multi-agent load
  - No memory leaks or resource exhaustion

---

## FR-004: Hot Reload - Add Index

**Requirement:** The system shall provide an `add_index(index_name, index)` method that adds a new index to `_indexes` dictionary at runtime under lock protection.

**Acceptance Criteria:**
- Method signature correct
- Atomic insertion under RLock
- ValueError on duplicate
- TypeError on invalid type
- Immediately queryable
- Structured logging

### Test Cases

#### Happy Path: Add Index Successfully

- **Test Function:** `test_add_index_success()`
- **File:** `test_index_manager_hot_reload.py`
- **Setup:**
  - Initialize IndexManager
  - Create new StandardsIndex instance
- **Action:**
  - `manager.add_index("new_standards", new_index)`
- **Expected:**
  - Index added to `_indexes` dict
  - Immediately queryable via `route_action()`
  - Returns None (no error)
  - Log event emitted: `{"event": "index_added", "index_name": "new_standards"}`
- **Verifies:**
  - All acceptance criteria (happy path)

#### Error Handling: Duplicate Index Name

- **Test Function:** `test_add_index_duplicate_raises_value_error()`
- **File:** `test_index_manager_hot_reload.py`
- **Setup:**
  - IndexManager with existing "standards" index
- **Action:**
  - Try to add another index with name "standards"
- **Expected:**
  - Raises `ValueError` with message: `"Index 'standards' already exists"`
  - Original index unchanged
- **Verifies:**
  - Acceptance criterion: ValueError on duplicate

#### Error Handling: Invalid Index Type

- **Test Function:** `test_add_index_invalid_type_raises_type_error()`
- **File:** `test_index_manager_hot_reload.py`
- **Setup:**
  - IndexManager initialized
- **Action:**
  - Try to add non-BaseIndex object: `manager.add_index("bad", "not an index")`
- **Expected:**
  - Raises `TypeError` with message: `"Index must be instance of BaseIndex"`
- **Verifies:**
  - Acceptance criterion: TypeError on invalid type

#### Integration: Add Index During Queries

- **Test Function:** `test_add_index_during_concurrent_queries()`
- **File:** `test_index_manager_hot_reload.py`
- **Setup:**
  - IndexManager with existing indexes
  - 20 threads performing continuous queries
- **Action:**
  - Call `add_index()` while queries in-flight
- **Expected:**
  - Add operation completes <50ms
  - Concurrent queries unaffected (no errors)
  - New index immediately available to subsequent queries
- **Verifies:**
  - Lock protection works
  - Non-blocking add operation

---

## FR-005: Hot Reload - Remove Index

**Requirement:** The system shall provide a `remove_index(index_name)` method that removes an index from `_indexes` dictionary at runtime, with cleanup outside lock.

**Acceptance Criteria:**
- Method signature correct
- Atomic removal under RLock
- Cleanup (close) outside lock
- KeyError on not-found
- Structured logging

### Test Cases

#### Happy Path: Remove Index Successfully

- **Test Function:** `test_remove_index_success()`
- **File:** `test_index_manager_hot_reload.py`
- **Setup:**
  - IndexManager with "temp_index" to remove
- **Action:**
  - `manager.remove_index("temp_index")`
- **Expected:**
  - Index removed from `_indexes` dict
  - Old index cleanup called (`index.close()` if exists)
  - Returns None (no error)
  - Log event emitted: `{"event": "index_removed", "index_name": "temp_index"}`
- **Verifies:**
  - All acceptance criteria (happy path)

#### Error Handling: Index Not Found

- **Test Function:** `test_remove_index_not_found_raises_key_error()`
- **File:** `test_index_manager_hot_reload.py`
- **Setup:**
  - IndexManager without "nonexistent" index
- **Action:**
  - `manager.remove_index("nonexistent")`
- **Expected:**
  - Raises `KeyError` with message: `"Index 'nonexistent' not found"`
- **Verifies:**
  - Acceptance criterion: KeyError on not-found

#### Integration: Remove Index During Queries

- **Test Function:** `test_remove_index_during_concurrent_queries()`
- **File:** `test_index_manager_hot_reload.py`
- **Setup:**
  - IndexManager with index to remove
  - 20 threads querying that index
- **Action:**
  - Call `remove_index()` while queries in-flight
- **Expected:**
  - Remove operation completes <50ms
  - In-flight queries complete successfully (using old index)
  - New queries receive `IndexError` (index no longer available)
  - Old index cleaned up after in-flight queries finish
- **Verifies:**
  - Cleanup happens outside lock
  - Graceful handling of in-flight queries

---

## FR-006: Hot Reload - Reload Indexes

**Requirement:** The system shall provide a `reload_indexes(new_config)` method that atomically swaps indexes based on new configuration.

**Acceptance Criteria:**
- Method signature correct
- Config diff determines add/remove/keep
- Atomic swap under lock
- Cleanup outside lock
- Structured logging
- <100ms completion time

### Test Cases

#### Happy Path: Add Only

- **Test Function:** `test_reload_indexes_add_only()`
- **File:** `test_index_manager_hot_reload.py`
- **Setup:**
  - IndexManager with ["standards", "code"]
  - New config with ["standards", "code", "docs"]
- **Action:**
  - `report = manager.reload_indexes(new_config)`
- **Expected:**
  - Report: `{"added": ["docs"], "removed": [], "kept": ["standards", "code"]}`
  - "docs" index added and queryable
  - Existing indexes unchanged
  - Completes <100ms
- **Verifies:**
  - Config diff add scenario
  - Atomic swap

#### Happy Path: Remove Only

- **Test Function:** `test_reload_indexes_remove_only()`
- **File:** `test_index_manager_hot_reload.py`
- **Setup:**
  - IndexManager with ["standards", "code", "temp"]
  - New config with ["standards", "code"]
- **Action:**
  - `report = manager.reload_indexes(new_config)`
- **Expected:**
  - Report: `{"added": [], "removed": ["temp"], "kept": ["standards", "code"]}`
  - "temp" index removed
  - Cleanup called on old "temp" index
- **Verifies:**
  - Config diff remove scenario

#### Happy Path: Mixed Operations

- **Test Function:** `test_reload_indexes_mixed()`
- **File:** `test_index_manager_hot_reload.py`
- **Setup:**
  - IndexManager with ["standards", "code", "old"]
  - New config with ["standards", "code", "new"]
- **Action:**
  - `report = manager.reload_indexes(new_config)`
- **Expected:**
  - Report: `{"added": ["new"], "removed": ["old"], "kept": ["standards", "code"]}`
  - "old" removed, "new" added, others kept
- **Verifies:**
  - Config diff mixed scenario
  - Atomic swap (never partial state)

#### Error Handling: Invalid Config

- **Test Function:** `test_reload_indexes_invalid_config()`
- **File:** `test_index_manager_hot_reload.py`
- **Setup:**
  - IndexManager initialized
- **Action:**
  - Pass invalid config (e.g., empty indexes list)
- **Expected:**
  - Raises `ValidationError` (Pydantic)
  - No changes to `_indexes`
- **Verifies:**
  - Config validation works

#### Error Handling: Unknown Index Type

- **Test Function:** `test_reload_indexes_unknown_index_type()`
- **File:** `test_index_manager_hot_reload.py`
- **Setup:**
  - IndexManager initialized
  - Config with index type not in INDEX_REGISTRY
- **Action:**
  - `manager.reload_indexes(config_with_unknown_type)`
- **Expected:**
  - Raises `RuntimeError` with message: `"Unknown index type: unknown_type"`
  - Actionable error message
- **Verifies:**
  - INDEX_REGISTRY validation

#### Integration: Atomic Swap During Concurrent Queries

- **Test Function:** `test_hot_reload_atomic_swap()`
- **File:** `test_index_manager_hot_reload.py`
- **Setup:**
  - IndexManager with existing indexes
  - 50 concurrent query threads
  - New config with different repos
- **Action:**
  - Call `reload_indexes(new_config)` while queries in-flight
- **Expected:**
  - Reload completes <100ms
  - All queries complete successfully (zero exceptions)
  - No query sees partial state (validated via query results - either old or new config, never mixed)
  - Old indexes cleaned up after in-flight queries finish
- **Verifies:**
  - NFR-P3: <100ms
  - NFR-R3: Atomic state transitions
  - Queries unaffected by reload

---

## FR-007: Standards Compliance Documentation

**Requirement:** IndexManager shall have comprehensive threading model documentation enabling future maintainers to modify code safely.

**Acceptance Criteria:**
- Class docstring documents 4 concurrent contexts
- Lock usage patterns explained
- Code examples provided
- References 4 concurrency standards

### Test Cases

#### Documentation Completeness

- **Test Function:** `test_documentation_completeness()`
- **File:** `test_index_manager_thread_safety.py`
- **Setup:**
  - Import IndexManager class
- **Action:**
  - Inspect `IndexManager.__doc__`
  - Inspect 7 modified method docstrings
- **Expected:**
  - Class docstring contains:
    - Section on "Threading Model"
    - All 4 concurrent contexts documented (asyncio, thread pool, watchdog, timer)
    - Lock usage pattern example code
    - References to 4 standards (python-concurrency.md, race-conditions.md, shared-state-analysis.md, production-code-checklist.md)
  - Each of 7 modified methods has "Thread Safety:" section in docstring
  - Maintainer guidance: "Always use lock when accessing _indexes"
- **Verifies:**
  - All acceptance criteria

#### Code Example Validation

- **Test Function:** `test_docstring_code_examples_valid()`
- **File:** `test_index_manager_thread_safety.py`
- **Setup:**
  - Extract code examples from docstrings
- **Action:**
  - Parse and validate syntax
- **Expected:**
  - All code examples are syntactically valid Python
  - Examples demonstrate correct lock usage
- **Verifies:**
  - Code examples are usable (not pseudo-code)

---

## FR-008: Snapshot Pattern for Iteration

**Requirement:** The system shall use snapshot pattern when iterating over `_indexes` dictionary to minimize lock hold time.

**Acceptance Criteria:**
- `health_check_all()` uses snapshot
- `get_stats()` uses snapshot
- Lock held <100ns for snapshot creation
- Iteration happens outside lock

### Test Cases

#### Happy Path: Health Check Uses Snapshot

- **Test Function:** `test_health_check_uses_snapshot()`
- **File:** `test_index_manager_thread_safety.py`
- **Setup:**
  - IndexManager with 10 indexes
  - Mock health check to take 1s per index (10s total)
- **Action:**
  - Thread 1: Call `health_check_all()` (will take 10s)
  - Thread 2: Concurrent queries during health check
- **Expected:**
  - Health check completes successfully (10s)
  - Concurrent queries in Thread 2 complete immediately (not blocked)
  - Proves snapshot pattern: lock not held during 10s health check
- **Verifies:**
  - Acceptance criteria: snapshot used, iteration outside lock

#### Happy Path: Get Stats Uses Snapshot

- **Test Function:** `test_get_stats_uses_snapshot()`
- **File:** `test_index_manager_thread_safety.py`
- **Setup:**
  - IndexManager with 10 indexes
- **Action:**
  - Call `get_stats()` while concurrent modifications happen
- **Expected:**
  - Stats reflect consistent snapshot (all indexes from same moment)
  - No errors from concurrent modifications
- **Verifies:**
  - Snapshot pattern prevents iteration errors

#### Performance: Lock Hold Time

- **Test Function:** `test_snapshot_lock_hold_time()`
- **File:** `test_index_manager_thread_safety.py`
- **Setup:**
  - IndexManager with 10 indexes
- **Action:**
  - Measure lock hold time during `health_check_all()`
- **Expected:**
  - Lock hold time <100ns (for `dict(self._indexes)`)
  - Proves lock not held during iteration
- **Verifies:**
  - Acceptance criterion: Lock held <100ns

---

## FR-009: Structured Logging for Observability

**Requirement:** Log operations (query, add, remove, reload, rebuild) using structured logging with machine-readable metadata.

**Acceptance Criteria:**
- All operations logged with `extra={}` dict
- 5+ event types
- Machine-readable (jq parseable)
- No sensitive data in logs

### Test Cases

#### Happy Path: All Events Logged

- **Test Function:** `test_all_events_logged()`
- **File:** `test_index_manager_logging.py`
- **Setup:**
  - IndexManager with test config
  - Capture log output
- **Action:**
  - Perform operations:
    - Query: `route_action("search_code", query="test")`
    - Add: `add_index("new", new_index)`
    - Remove: `remove_index("temp")`
    - Reload: `reload_indexes(new_config)`
    - Rebuild: `rebuild_index("code")`
- **Expected:**
  - 5 log events emitted:
    - `{"event": "index_query", "index_name": "code", "latency_ms": ...}`
    - `{"event": "index_added", "index_name": "new"}`
    - `{"event": "index_removed", "index_name": "temp"}`
    - `{"event": "indexes_reloaded", "added": [...], "removed": [...]}`
    - `{"event": "index_rebuilt", "index_name": "code", "duration_ms": ...}`
- **Verifies:**
  - Acceptance criterion: 5+ event types

#### Format Validation: jq Parseable

- **Test Function:** `test_log_format_consistent()`
- **File:** `test_index_manager_logging.py`
- **Setup:**
  - Capture logs from operations
- **Action:**
  - Parse logs with jq (or Python equivalent)
- **Expected:**
  - All logs are valid JSON with `extra={}` dict
  - Consistent format across all events
  - Can query: `jq '.latency_ms'`, `jq '.event'`
- **Verifies:**
  - Acceptance criterion: Machine-readable

#### Security: No Sensitive Data in Logs

- **Test Function:** `test_log_scrubbing_no_sensitive_data()`
- **File:** `test_index_manager_logging.py`
- **Setup:**
  - Perform query with specific query content
- **Action:**
  - Inspect log output
- **Expected:**
  - Log contains metadata only (index_name, latency_ms, result_count)
  - Log does NOT contain:
    - Query content ("test" string not in log)
    - Query results (actual code snippets not in log)
  - Only safe metadata logged
- **Verifies:**
  - Acceptance criterion: No sensitive data

---

## FR-010: Lock Overhead Performance

**Requirement:** RLock overhead <1% vs. unprotected access, validated through benchmarking tests.

**Acceptance Criteria:**
- Benchmark 10k queries
- <1% regression
- Lock acquisition time documented

### Test Cases

#### Benchmark: Lock Overhead

- **Test Function:** `test_lock_overhead_negligible()`
- **File:** `test_index_manager_thread_safety.py`
- **Setup:**
  - IndexManager with test config
  - Prepare 10k queries
- **Action:**
  - Measure 10k queries with locks
  - Compare to baseline (or theoretical minimum)
- **Expected:**
  - Total time: ~500s (10k × 50ms per query)
  - Lock overhead: <1% → Max 505s allowed
  - Lock acquisition time: ~0.9ns per operation (documented in test output)
  - Proves lock overhead unmeasurable vs. I/O (10-100ms queries)
- **Verifies:**
  - All acceptance criteria

---

## Integration Tests

### Scenario: Multi-Agent Multi-Repo Deployment

**Requirements:** FR-001, FR-003, FR-008

**Test Function:** `test_multi_agent_multi_repo_e2e()`

**Setup:**
- IndexManager with 10 repos (simulating large deployment)
- 100 concurrent agents (threads)

**Flow:**
1. **Concurrent Queries (Phase 1):**
   - All 100 agents query different indexes simultaneously
   - Expect: All queries succeed, no race conditions
2. **Health Checks (Phase 2):**
   - Background health check runs during queries
   - Expect: Snapshot pattern prevents blocking
3. **Hot Reload (Phase 3):**
   - Add new repo mid-flight
   - Expect: Queries unaffected, new repo immediately available

**Verifies:** Complete multi-agent, multi-repo workflow

---

### Scenario: Graceful Config Change

**Requirements:** FR-004, FR-005, FR-006

**Test Function:** `test_graceful_config_change_e2e()`

**Setup:**
- Running system with active queries
- Config file updated (new repos added, old removed)

**Flow:**
1. Reload config: `reload_indexes(new_config)`
2. Expect: Atomic swap, zero query errors
3. Validate: Old indexes cleaned up, new indexes available

**Verifies:** Hot reload end-to-end

---

## Summary

| Functional Requirement | Test Cases | Happy Path | Error Handling | Edge Cases | Integration |
|------------------------|------------|------------|----------------|------------|-------------|
| FR-001 | 3 | ✅ | - | ✅ (high contention, empty indexes) | ✅ |
| FR-002 | 3 | ✅ (re-entrant chains, lock type) | - | ✅ (deadlock demo) | - |
| FR-003 | 2 | ✅ (100 agents) | - | - | ✅ (stress test) |
| FR-004 | 4 | ✅ | ✅ (duplicate, invalid type) | - | ✅ (during queries) |
| FR-005 | 3 | ✅ | ✅ (not found) | - | ✅ (during queries) |
| FR-006 | 6 | ✅ (add, remove, mixed) | ✅ (invalid config, unknown type) | - | ✅ (atomic swap) |
| FR-007 | 2 | ✅ (completeness, code examples) | - | - | - |
| FR-008 | 3 | ✅ (health check, stats, lock time) | - | - | - |
| FR-009 | 3 | ✅ (all events) | - | - | ✅ (jq, security) |
| FR-010 | 1 | ✅ (benchmark) | - | - | - |
| **TOTAL** | **30** | **18** | **5** | **3** | **6** |

**Total Test Functions:** 30+ across 3 test files

**Coverage:** 100% of functional requirements

---

**Document Version:** 1.0  
**Last Updated:** 2025-11-20  
**Status:** Functional tests complete - Ready for NFR tests (Task 6)


