# Implementation Tasks

**Project:** IndexManager Thread Safety, Hot Reload, and Dynamic Logic Implementation  
**Date:** 2025-11-20  
**Status:** Draft - Pending Approval  
**Based on:** specs.md (technical design), srd.md (requirements)

---

## Time Estimates

- **Phase 1:** 16 hours (Thread Safety Core - Critical Path)
- **Phase 2:** 20 hours (Hot Reload API - Dynamic Management)
- **Phase 3:** 8 hours (Observability - Monitoring & Logging)
- **Total:** 44 hours (~5.5 days at 8 hrs/day)

**Note:** Estimates assume single developer, include testing and documentation time.

---

## Phase 1: Thread Safety Core

**Objective:** Implement consistent RLock protection across all 12 access sites to `_indexes` dictionary, add comprehensive documentation, and validate with concurrent access tests. This phase satisfies critical standards compliance requirements (FR-001, FR-002, NFR-R1, NFR-R2).

**Priority:** P0 (Critical Path - Must Complete First)

**Estimated Duration:** 16 hours

**Key Deliverables:**
- RLock protection on 7 modified methods
- Threading model documentation (class docstring, method docstrings)
- 3 test suites (concurrent access, lock overhead, stress test)
- Standards compliance validation

**Dependencies:** None (starting point)

**Risks:**
- Incomplete lock migration (miss an access site) → Mitigation: Comprehensive grep audit
- Deadlock introduction → Mitigation: RLock prevents same-thread deadlock
- Performance regression → Mitigation: Benchmark test validates <1% overhead

---

### Phase 1 Tasks

- [ ] **Task 1.1**: Audit all `_indexes` access sites (M - 2 hours)
  - Grep for `self._indexes` in index_manager.py
  - Identify all 12 access sites (reads, writes, iterations)
  - Document line numbers and access patterns
  - Cross-reference with design doc list (7 methods + init)
  - Verify no missed access sites
  
  **Acceptance Criteria:**
  - [ ] Grep results documented showing all `self._indexes` occurrences
  - [ ] Exactly 12 access sites identified (matches design doc)
  - [ ] Line numbers documented for each access site
  - [ ] Access pattern categorized for each site (read/write/iterate)
  - [ ] Cross-reference validates 7 methods + init match design doc
  - [ ] Code review confirms no missed access sites

- [ ] **Task 1.2**: Add RLock to route_action() method (S - 1 hour)
  - Wrap `self._indexes.get(index_name)` with `with self._indexes_lock:`
  - Move query execution outside lock (keep lock hold time <10ns)
  - Update method docstring to document thread safety
  - Verify lock pattern matches design doc § 6.2
  - Manual test: Single query works
  
  **Acceptance Criteria:**
  - [ ] `self._indexes.get()` wrapped with `with self._indexes_lock:`
  - [ ] Query execution code remains outside lock (index.search() not in lock context)
  - [ ] Method docstring includes "Thread Safety:" section
  - [ ] Lock pattern matches specs.md § 3.4 Pattern 1
  - [ ] Manual test passes: query returns correct results
  - [ ] No linter errors introduced

- [ ] **Task 1.3**: Add RLock to get_index() method (S - 0.5 hours)
  - Wrap `self._indexes.get(index_name)` with lock
  - Update docstring
  - Verify no functional changes (same return value)
  
  **Acceptance Criteria:**
  - [ ] `self._indexes.get()` wrapped with lock
  - [ ] Docstring updated with thread safety note
  - [ ] Return value unchanged (returns Optional[BaseIndex])
  - [ ] Existing callers unaffected (backward compatible)

- [ ] **Task 1.4**: Add RLock with snapshot to health_check_all() (S - 1 hour)
  - Implement snapshot pattern: `with self._indexes_lock: snapshot = dict(self._indexes)`
  - Process snapshot outside lock
  - Update docstring to document snapshot pattern
  - Verify lock hold time <100ns
  
  **Acceptance Criteria:**
  - [ ] Snapshot created with `dict(self._indexes)` under lock
  - [ ] Health check logic operates on snapshot outside lock
  - [ ] Docstring documents snapshot pattern reasoning
  - [ ] Lock pattern matches specs.md § 3.4 Pattern 2
  - [ ] Manual profiling confirms lock hold time <100ns

- [ ] **Task 1.5**: Add RLock to ensure_all_indexes_healthy() (S - 1 hour)
  - Wrap `_indexes` iteration with lock or use snapshot
  - Update docstring
  - Verify background task compatibility
  
  **Acceptance Criteria:**
  - [ ] `_indexes` access protected by lock or snapshot pattern used
  - [ ] Docstring updated with thread safety note
  - [ ] Background task (asyncio.to_thread) still functions correctly
  - [ ] No deadlocks when called from thread pool

- [ ] **Task 1.6**: Add RLock to rebuild_index() (S - 0.5 hours)
  - Wrap `self._indexes.get()` with lock
  - Keep rebuild logic outside lock
  - Update docstring
  
  **Acceptance Criteria:**
  - [ ] `self._indexes.get()` wrapped with lock
  - [ ] Index.build() called outside lock (not blocking queries)
  - [ ] Docstring updated
  - [ ] Rebuild still functions correctly

- [ ] **Task 1.7**: Add RLock to update_from_watcher() (S - 0.5 hours)
  - Wrap `self._indexes.get()` with lock
  - Keep update logic outside lock
  - Update docstring
  
  **Acceptance Criteria:**
  - [ ] `self._indexes.get()` wrapped with lock
  - [ ] Index update logic outside lock
  - [ ] Docstring updated
  - [ ] FileWatcher callbacks still work (timer threads compatible)

- [ ] **Task 1.8**: Add RLock to get_stats() (S - 1 hour)
  - Implement snapshot pattern for iteration
  - Update docstring
  - Verify stats remain accurate
  
  **Acceptance Criteria:**
  - [ ] Snapshot pattern implemented (dict copy under lock)
  - [ ] Stats calculation uses snapshot outside lock
  - [ ] Docstring updated
  - [ ] Stats output format unchanged
  - [ ] Stats accuracy validated (matches pre-lock behavior)

- [ ] **Task 1.9**: Document threading model in class docstring (M - 2 hours)
  - Add comprehensive class docstring to IndexManager
  - Document 4 concurrent execution contexts
  - Provide lock acquisition pattern example code
  - Reference 4 concurrency standards
  - Add maintainer guidance: "Always use lock when accessing _indexes"
  - Review against NFR-M1 requirements
  
  **Acceptance Criteria:**
  - [ ] Class docstring added/updated with threading section
  - [ ] All 4 concurrent contexts documented (asyncio, thread pool, watchdog, timer)
  - [ ] Lock acquisition example code included in docstring
  - [ ] References to 4 standards included (python-concurrency, race-conditions, shared-state-analysis, production-code-checklist)
  - [ ] Maintainer guidance explicitly stated
  - [ ] NFR-M1 requirements checklist 100% satisfied
  - [ ] Code review confirms documentation clarity

- [ ] **Task 1.10**: Document threading in method docstrings (M - 2 hours)
  - Update docstrings for all 7 modified methods
  - Indicate which methods acquire _indexes_lock
  - Document lock hold time expectations
  - Add "Thread Safety:" section to each
  
  **Acceptance Criteria:**
  - [ ] All 7 modified methods have updated docstrings
  - [ ] Each docstring includes "Thread Safety:" section
  - [ ] Lock acquisition explicitly documented per method
  - [ ] Lock hold time expectations documented (<10ns for dict access, <100ns for snapshot)
  - [ ] Docstring format consistent across all methods
  - [ ] Code review approves documentation quality

- [ ] **Task 1.11**: Create concurrent access test (L - 4 hours)
  - Implement test_concurrent_index_access() per design doc § 7
  - 100 threads × 1000 operations = 100k concurrent accesses
  - Mix of route_action, health_check_all, update_from_watcher calls
  - Assert: Zero exceptions, zero data corruption
  - Assert: All operations complete within timeout
  - Verify: Results match sequential baseline
  
  **Acceptance Criteria:**
  - [ ] Test file created: test_index_manager_thread_safety.py
  - [ ] Test spawns exactly 100 threads
  - [ ] Each thread performs exactly 1000 operations (100k total)
  - [ ] Mix includes route_action, health_check_all, update_from_watcher
  - [ ] Test passes: zero exceptions raised
  - [ ] Test passes: zero data corruption detected
  - [ ] Test passes: all threads complete within 30s timeout
  - [ ] Results validated against sequential baseline
  - [ ] NFR-R1 (Zero Race Conditions) satisfied

- [ ] **Task 1.12**: Create lock overhead benchmark test (M - 2 hours)
  - Implement test_lock_overhead_negligible() per design doc § 7
  - Benchmark 10,000 queries with locks
  - Measure latency difference
  - Assert: <1% regression (NFR-P1)
  - Document: Lock acquisition ~0.9ns, I/O dominates
  
  **Acceptance Criteria:**
  - [ ] Benchmark test created: test_lock_overhead_negligible()
  - [ ] Benchmark runs exactly 10,000 queries
  - [ ] Latency measured with time.perf_counter() (ns precision)
  - [ ] Test passes: overhead <1% (NFR-P1)
  - [ ] Test documents lock acquisition time ~0.9ns
  - [ ] Test documents I/O dominates (1000x+ lock overhead)
  - [ ] Test output includes performance metrics

- [ ] **Task 1.13**: Create stress test (M - 3 hours)
  - Implement test_thread_safety_stress() per design doc § 7
  - 50 threads × 10 seconds sustained load
  - Mix of reads (queries) + writes (rebuilds)
  - Assert: No crashes, no exceptions, no corruption
  - Assert: Performance remains stable under load
  
  **Acceptance Criteria:**
  - [ ] Stress test created: test_thread_safety_stress()
  - [ ] Test spawns exactly 50 threads
  - [ ] Test runs for exactly 10 seconds sustained
  - [ ] Mix of read operations (queries) and write operations (rebuilds)
  - [ ] Test passes: zero crashes
  - [ ] Test passes: zero exceptions
  - [ ] Test passes: zero data corruption
  - [ ] Performance remains stable (no degradation over 10s)
  - [ ] NFR-P2 (Concurrent Query Throughput) validated

---

### Phase 1 Validation Gate

**🛑 Before advancing to Phase 2, verify:**

**Code Quality:**
- [ ] All 7 methods modified with RLock protection
- [ ] All 13 Phase 1 tasks completed and checked off
- [ ] All Phase 1 acceptance criteria met (100% checklist complete)
- [ ] Zero linter errors in modified files
- [ ] Code reviewed against `python-concurrency.md` standard
- [ ] No bare exception handlers introduced

**Testing:**
- [ ] test_concurrent_index_access() passes (100k operations, zero exceptions)
- [ ] test_lock_overhead_negligible() passes (<1% overhead confirmed)
- [ ] test_thread_safety_stress() passes (50 threads × 10s, stable)
- [ ] All existing tests still pass (no regressions)
- [ ] Test coverage for modified methods ≥90%

**Documentation:**
- [ ] Class docstring updated with threading model (4 contexts documented)
- [ ] All 7 method docstrings updated with "Thread Safety:" sections
- [ ] Lock acquisition patterns documented with examples
- [ ] All 4 concurrency standards referenced in comments

**Standards Compliance:**
- [ ] `python-concurrency.md`: Lock usage validated ✅
- [ ] `race-conditions.md`: Prevention strategies satisfied ✅
- [ ] `shared-state-analysis.md`: All 3 questions answered ✅
- [ ] `production-code-checklist.md`: Concurrency checklist 100% ✅

**Requirements Satisfied:**
- [ ] FR-001 (Thread-Safe Index Access) ✅
- [ ] FR-002 (Thread-Safe Index Operations) ✅
- [ ] FR-003 (Threading Model Documentation) ✅
- [ ] NFR-R1 (Zero Race Conditions) ✅
- [ ] NFR-R2 (Deadlock Prevention) ✅
- [ ] NFR-P1 (Negligible Overhead) ✅
- [ ] NFR-P2 (Concurrent Throughput) ✅
- [ ] NFR-M1 (Documentation Quality) ✅

**Exit Criteria:**
- [ ] Thread safety foundation is solid (all tests green)
- [ ] No blocking issues for Phase 2 hot reload implementation
- [ ] Code review approved by second developer
- [ ] Standards compliance validated by checklist

🚨 **DO NOT PROCEED TO PHASE 2** if any validation criteria fail. Phase 2 builds on Phase 1's thread-safe foundation.

---

## Phase 2: Hot Reload API

**Objective:** Implement dynamic index management with add/remove/reload capabilities, enabling runtime configuration changes without server restart. This phase leverages INDEX_REGISTRY for dynamic logic and implements atomic swap pattern for consistency (FR-004, FR-005, FR-006, NFR-M3, NFR-R3).

**Priority:** P1 (High - Enables Dynamic Operations)

**Estimated Duration:** 20 hours

**Key Deliverables:**
- 3 new methods (add_index, remove_index, reload_indexes)
- Config diff logic
- Atomic swap implementation
- Hot reload integration tests
- Structured logging for reload events

**Dependencies:** Phase 1 must complete (thread-safe foundation required)

**Risks:**
- Config parsing errors → Mitigation: Pydantic validation
- Partial reload state → Mitigation: Atomic swap under lock
- Old index cleanup failure → Mitigation: Cleanup outside lock, log errors

---

### Phase 2 Tasks

- [ ] **Task 2.1**: Implement add_index() method (M - 3 hours)
  - Signature: `add_index(self, index_name: str, index: BaseIndex) -> None`
  - Atomic insertion under `_indexes_lock`
  - Raise ValueError if index_name already exists
  - Raise TypeError if not isinstance(index, BaseIndex)
  - Add structured logging: `{"event": "index_added", "index_name": ...}`
  - Write docstring per specs.md § 3.2
  - Verify: Method signature matches API spec exactly
  
  **Acceptance Criteria:**
  - [ ] Method signature exactly matches specs.md § 3.2
  - [ ] Insertion wrapped with `with self._indexes_lock:`
  - [ ] ValueError raised if `index_name in self._indexes`
  - [ ] TypeError raised if not `isinstance(index, BaseIndex)`
  - [ ] Structured log emitted with event="index_added", index_name metadata
  - [ ] Docstring complete per specs.md (includes Args, Raises, Thread Safety, Logging sections)
  - [ ] FR-004 requirements satisfied
  - [ ] Unit test passes for success case
  - [ ] Unit test passes for ValueError case
  - [ ] Unit test passes for TypeError case

- [ ] **Task 2.2**: Implement remove_index() method (M - 3 hours)
  - Signature: `remove_index(self, index_name: str) -> None`
  - Atomic removal under lock
  - Call `index.close()` outside lock (avoid blocking)
  - Raise KeyError if index_name not found
  - Add structured logging: `{"event": "index_removed", "index_name": ...}`
  - Write docstring per specs.md § 3.2
  - Verify: Cleanup happens outside lock
  
  **Acceptance Criteria:**
  - [ ] Method signature exactly matches specs.md § 3.2
  - [ ] Dict removal wrapped with lock: `old_index = self._indexes.pop(index_name)`
  - [ ] `index.close()` called outside lock context
  - [ ] KeyError raised if `index_name not in self._indexes`
  - [ ] Structured log emitted with event="index_removed"
  - [ ] Docstring complete per specs.md (includes Notes about cleanup)
  - [ ] FR-005 requirements satisfied
  - [ ] Lock pattern matches specs.md § 3.4 Pattern 4
  - [ ] Unit test passes for success case
  - [ ] Unit test passes for KeyError case
  - [ ] Cleanup failure logged but doesn't raise

- [ ] **Task 2.3**: Implement config diff logic for reload_indexes() (M - 3 hours)
  - Compute `to_add = new_config.indexes - current_indexes`
  - Compute `to_remove = current_indexes - new_config.indexes`
  - Compute `to_keep = intersection`
  - Validate: All index names in INDEX_REGISTRY
  - Raise RuntimeError if unknown index type
  - Return diff dict: `{"added": [...], "removed": [...], "kept": [...]}`
  - Verify: Diff computation outside lock (fast)
  
  **Acceptance Criteria:**
  - [ ] Diff logic computes to_add correctly (set difference)
  - [ ] Diff logic computes to_remove correctly (set difference)
  - [ ] Diff logic computes to_keep correctly (set intersection)
  - [ ] Validation checks all names against INDEX_REGISTRY
  - [ ] RuntimeError raised with actionable message if unknown type
  - [ ] Return dict has exactly 3 keys: "added", "removed", "kept"
  - [ ] Diff computation happens outside any lock context
  - [ ] Unit test validates all diff scenarios (add only, remove only, mixed, keep all)

- [ ] **Task 2.4**: Implement reload_indexes() atomic swap (L - 4 hours)
  - Signature: `reload_indexes(self, new_config: IndexesConfig) -> Dict[str, List[str]]`
  - Call config diff logic (Task 2.3)
  - Acquire lock
  - For each in to_remove: pop from `_indexes`
  - For each in to_add: instantiate from INDEX_REGISTRY, insert into `_indexes`
  - Release lock
  - Close old indexes outside lock
  - Add structured logging: `{"event": "indexes_reloaded", "added": ..., "removed": ..., "kept": ...}`
  - Write docstring per specs.md § 3.2
  - Verify: Swap is atomic, queries see consistent state
  
  **Acceptance Criteria:**
  - [ ] Method signature exactly matches specs.md § 3.2
  - [ ] Config diff logic called first (outside lock)
  - [ ] All dict modifications (pop, insert) happen under single lock acquisition
  - [ ] Lock pattern matches specs.md § 3.4 Pattern 4
  - [ ] INDEX_REGISTRY used for dynamic instantiation (no hardcoded types)
  - [ ] Old index cleanup happens outside lock
  - [ ] Structured log emitted with all 3 arrays (added, removed, kept)
  - [ ] Docstring complete with Algorithm section
  - [ ] FR-006 requirements satisfied
  - [ ] NFR-R3 (Atomic State Transitions) satisfied
  - [ ] NFR-M3 (Dynamic Logic) satisfied
  - [ ] Return value matches expected format

- [ ] **Task 2.5**: Create hot reload unit tests (M - 3 hours)
  - Test add_index(): Success case, ValueError on duplicate
  - Test remove_index(): Success case, KeyError on not-found
  - Test reload_indexes(): Add, remove, keep scenarios
  - Test config validation (Pydantic errors)
  - Test INDEX_REGISTRY lookup failures
  - Assert: All methods have correct signatures
  
  **Acceptance Criteria:**
  - [ ] Test file created: test_index_manager_hot_reload.py
  - [ ] test_add_index_success() passes
  - [ ] test_add_index_duplicate_raises_value_error() passes
  - [ ] test_remove_index_success() passes
  - [ ] test_remove_index_not_found_raises_key_error() passes
  - [ ] test_reload_indexes_add_only() passes
  - [ ] test_reload_indexes_remove_only() passes
  - [ ] test_reload_indexes_mixed() passes
  - [ ] test_reload_indexes_invalid_config() passes (Pydantic ValidationError)
  - [ ] test_reload_indexes_unknown_index_type() passes (RuntimeError)
  - [ ] All 3 method signatures validated
  - [ ] Test coverage for hot reload methods ≥90%

- [ ] **Task 2.6**: Create hot reload integration test (L - 4 hours)
  - Test: test_hot_reload_atomic_swap()
  - Start 50 concurrent query threads
  - Call reload_indexes() mid-flight
  - Assert: All queries complete successfully
  - Assert: No query sees partial state (old/new only)
  - Assert: Reload completes <100ms (NFR-P3)
  - Verify: Old index cleaned up after queries finish
  
  **Acceptance Criteria:**
  - [ ] Integration test created: test_hot_reload_atomic_swap()
  - [ ] Test spawns exactly 50 query threads
  - [ ] reload_indexes() called while queries in-flight
  - [ ] Test passes: all queries complete successfully (zero exceptions)
  - [ ] Test passes: no query sees partial state (validated via query results)
  - [ ] Test passes: reload completes <100ms (NFR-P3 satisfied)
  - [ ] Test verifies old index cleanup occurred
  - [ ] Test validates INDEX_REGISTRY used (no hardcoded types)
  - [ ] FR-006, NFR-R3, NFR-P3 requirements validated

---

### Phase 2 Validation Gate

**🛑 Before advancing to Phase 3, verify:**

**Code Quality:**
- [ ] All 3 new methods implemented (add_index, remove_index, reload_indexes)
- [ ] All 6 Phase 2 tasks completed and checked off
- [ ] All Phase 2 acceptance criteria met (100% checklist complete)
- [ ] Config diff logic extracted and reusable
- [ ] Atomic swap pattern correctly implemented (lock covers all dict mods)
- [ ] Old index cleanup happens outside lock (non-blocking)
- [ ] Zero linter errors in new code
- [ ] Code reviewed for race conditions

**Testing:**
- [ ] All hot reload unit tests pass (9+ test cases)
- [ ] test_hot_reload_atomic_swap() passes (concurrent queries during reload)
- [ ] Config validation tests pass (Pydantic errors caught)
- [ ] INDEX_REGISTRY validation tests pass (unknown types rejected)
- [ ] Reload completes <100ms (NFR-P3 timing validated)
- [ ] All Phase 1 tests still pass (no regressions)
- [ ] Test coverage for new methods ≥90%

**Documentation:**
- [ ] All 3 method docstrings complete (Args, Returns, Raises, Algorithm, Thread Safety, Logging)
- [ ] Docstrings match specs.md § 3.2 exactly
- [ ] INDEX_REGISTRY usage documented in code comments
- [ ] Atomic swap pattern explained in reload_indexes() docstring

**Dynamic Logic Validation:**
- [ ] INDEX_REGISTRY used for all index instantiation (zero hardcoded types)
- [ ] Config-driven: New index types can be added without code changes
- [ ] Fractal pattern maintained (IndexManager orchestrates, doesn't know index internals)
- [ ] NFR-M3 (Dynamic Logic Extensibility) satisfied

**Requirements Satisfied:**
- [ ] FR-004 (Dynamic Index Management) ✅
- [ ] FR-005 (Safe Index Removal) ✅
- [ ] FR-006 (Atomic Hot Reload) ✅
- [ ] NFR-R3 (Atomic State Transitions) ✅
- [ ] NFR-P3 (Hot Reload <100ms) ✅
- [ ] NFR-M3 (Dynamic Logic) ✅

**Exit Criteria:**
- [ ] Hot reload functionality complete and tested
- [ ] Logging foundation in place (events logged)
- [ ] Ready for Phase 3 observability enhancements (log analysis, compliance)
- [ ] Code review approved
- [ ] Integration tests demonstrate production-readiness

**Optional: Phase 3 Parallel Start:**
If Phase 3 starts in parallel (not recommended but possible), ensure Phase 2 logging events (index_added, index_removed, indexes_reloaded) are already implemented before Task 3.2-3.4 validation.

---

## Phase 3: Observability

**Objective:** Implement structured logging for all index operations, enabling performance analysis and operational debugging without external metrics systems. This phase provides queryable logs for latency tracking and anomaly detection (FR-009, NFR-O1, NFR-O2).

**Priority:** P2 (Medium - Operational Visibility)

**Estimated Duration:** 8 hours

**Key Deliverables:**
- Structured logging with `extra={}` metadata
- Event types: index_query, index_added, index_removed, indexes_reloaded, index_rebuilt
- Log analysis examples (jq queries for p95, slow queries)
- Logging standard compliance

**Dependencies:** Phase 2 recommended (hot reload events to log)

**Risks:**
- Performance impact from logging → Mitigation: Logging overhead <0.1ms
- Sensitive data leakage → Mitigation: Metadata only, no query content

---

### Phase 3 Tasks

- [ ] **Task 3.1**: Add structured logging to route_action() (S - 1 hour)
  - Log event: `index_query`
  - Metadata: `index_name`, `action`, `latency_ms`, `result_count`
  - Use INFO level
  - Follow `structured-logging-observability.md` standard
  - Verify: Logs are machine-readable (jq parseable)
  
  **Acceptance Criteria:**
  - [ ] Structured log added: `logger.info("Index query", extra={...})`
  - [ ] Log event includes "index_query" identifier
  - [ ] Metadata includes: index_name, action, latency_ms, result_count
  - [ ] Log level is INFO
  - [ ] Follows `structured-logging-observability.md` standard format
  - [ ] Log output is jq parseable (JSON-compatible extra dict)
  - [ ] FR-009 requirements satisfied
  - [ ] No query content logged (metadata only, security validated)

- [ ] **Task 3.2**: Add structured logging to add_index() (S - 0.5 hours)
  - Log event: `index_added`
  - Metadata: `index_name`, `timestamp`
  - Verify: Already added in Task 2.1, validate format
  
  **Acceptance Criteria:**
  - [ ] Logging already present from Task 2.1 (validated)
  - [ ] Log format matches structured logging standard
  - [ ] Event name is "index_added"
  - [ ] Metadata includes index_name and timestamp
  - [ ] Log level is INFO

- [ ] **Task 3.3**: Add structured logging to remove_index() (S - 0.5 hours)
  - Log event: `index_removed`
  - Metadata: `index_name`, `timestamp`
  - Verify: Already added in Task 2.2, validate format
  
  **Acceptance Criteria:**
  - [ ] Logging already present from Task 2.2 (validated)
  - [ ] Log format matches structured logging standard
  - [ ] Event name is "index_removed"
  - [ ] Metadata includes index_name and timestamp
  - [ ] Log level is INFO

- [ ] **Task 3.4**: Add structured logging to reload_indexes() (S - 0.5 hours)
  - Log event: `indexes_reloaded`
  - Metadata: `added[]`, `removed[]`, `kept[]`, `timestamp`
  - Verify: Already added in Task 2.4, validate format
  
  **Acceptance Criteria:**
  - [ ] Logging already present from Task 2.4 (validated)
  - [ ] Log format matches structured logging standard
  - [ ] Event name is "indexes_reloaded"
  - [ ] Metadata includes added, removed, kept arrays
  - [ ] Log level is INFO

- [ ] **Task 3.5**: Add structured logging to rebuild_index() (S - 1 hour)
  - Log event: `index_rebuilt`
  - Metadata: `index_name`, `duration_ms`, `success`
  - Use INFO level for success, ERROR for failure
  - Verify: Rebuild events queryable
  
  **Acceptance Criteria:**
  - [ ] Structured log added to rebuild_index()
  - [ ] Event name is "index_rebuilt"
  - [ ] Metadata includes: index_name, duration_ms, success (boolean)
  - [ ] INFO level used for success=true
  - [ ] ERROR level used for success=false
  - [ ] Log format matches structured logging standard
  - [ ] Rebuild events are jq queryable

- [ ] **Task 3.6**: Add error logging for failures (M - 2 hours)
  - Log event: `index_add_failed`, `index_remove_failed`, etc.
  - Metadata: `index_name`, `error`, `timestamp`
  - Use ERROR level
  - Ensure no sensitive data in error messages
  - Verify: Actionable error messages (NFR-M1)
  
  **Acceptance Criteria:**
  - [ ] Error events logged for: index_add_failed, index_remove_failed, index_reload_failed
  - [ ] All error logs use ERROR level
  - [ ] Metadata includes: index_name, error (sanitized message), timestamp
  - [ ] Error messages are actionable per NFR-M1
  - [ ] No sensitive data in error messages (validated)
  - [ ] Error log format consistent with success logs
  - [ ] Security test passes (no data leakage)

- [ ] **Task 3.7**: Create log analysis examples (S - 1 hour)
  - Document jq queries for p95 latency
  - Document jq queries for slow queries (>1s)
  - Document jq queries for failed operations
  - Add examples to implementation.md
  - Verify: Examples work on actual log output
  
  **Acceptance Criteria:**
  - [ ] jq query documented for p95 latency calculation
  - [ ] jq query documented for slow queries (>1000ms filter)
  - [ ] jq query documented for failed operations (ERROR level)
  - [ ] jq query documented for audit trail (add/remove events)
  - [ ] All examples added to implementation.md
  - [ ] All examples tested on actual log output and work correctly
  - [ ] NFR-O2 (Query Latency Visibility) satisfied

- [ ] **Task 3.8**: Validate logging compliance (S - 1 hour)
  - Review all logging against `structured-logging-observability.md`
  - Verify: No query content logged (metadata only)
  - Verify: All events have timestamps
  - Verify: Log format consistent across all methods
  - Assert: Security test passes (no sensitive data leakage)
  
  **Acceptance Criteria:**
  - [ ] All logging reviewed against `structured-logging-observability.md` standard
  - [ ] Compliance checklist 100% complete
  - [ ] Verified: Zero query content in logs (only metadata)
  - [ ] Verified: All log events include timestamps
  - [ ] Verified: Log format consistent (same extra dict structure)
  - [ ] Security test passes: test_log_scrubbing_no_sensitive_data()
  - [ ] NFR-O1 (Structured Logging) fully satisfied
  - [ ] Code review approves logging implementation

---

### Phase 3 Validation Gate

**🛑 Before marking implementation complete, verify:**

**Code Quality:**
- [ ] All 8 Phase 3 tasks completed and checked off
- [ ] All Phase 3 acceptance criteria met (100% checklist complete)
- [ ] Structured logging added to all required methods (5 events minimum)
- [ ] Log format consistent across all logging statements
- [ ] Zero linter errors in logging code
- [ ] Code reviewed for security (no data leakage)

**Logging Implementation:**
- [ ] 5+ event types logged: index_query, index_added, index_removed, indexes_reloaded, index_rebuilt
- [ ] All events use `extra={}` dict for structured metadata
- [ ] Metadata includes: index_name, action, latency_ms, result_count, timestamp (as appropriate)
- [ ] INFO level for success events
- [ ] ERROR level for failure events
- [ ] No query content in logs (metadata only - security requirement)

**Log Analysis:**
- [ ] jq query examples documented for p95 latency
- [ ] jq query examples documented for slow queries (>1s)
- [ ] jq query examples documented for failed operations
- [ ] jq query examples documented for audit trail (add/remove)
- [ ] All examples tested on actual log output
- [ ] Examples added to implementation.md or operations runbook

**Standards Compliance:**
- [ ] `structured-logging-observability.md`: Format validated ✅
- [ ] Security requirements: No sensitive data in logs ✅
- [ ] Log format consistency: All events use same structure ✅
- [ ] Test: test_log_scrubbing_no_sensitive_data() passes ✅

**Requirements Satisfied:**
- [ ] FR-009 (Structured Event Logging) ✅
- [ ] NFR-O1 (Structured Logging) ✅
- [ ] NFR-O2 (Query Latency Visibility) ✅

**Exit Criteria:**
- [ ] Observability complete: Can analyze performance via logs
- [ ] Security validated: No data leakage in logs
- [ ] Operations-ready: Log analysis queries documented
- [ ] Code review approved

---

## Project Completion Validation

**🎯 All phases complete when:**

**Implementation:**
- [ ] All 27 tasks across 3 phases completed ✅
- [ ] All acceptance criteria met (100% of 150+ criteria) ✅
- [ ] All 3 phase validation gates passed ✅

**Testing:**
- [ ] Thread safety tests pass (100k concurrent ops) ✅
- [ ] Hot reload tests pass (atomic swap validated) ✅
- [ ] Log scrubbing test passes (security validated) ✅
- [ ] All existing tests still pass (zero regressions) ✅
- [ ] Test coverage ≥90% for modified/new code ✅

**Standards Compliance:**
- [ ] All 4 concurrency standards satisfied ✅
- [ ] Structured logging standard satisfied ✅
- [ ] Code review checklist 100% complete ✅

**Documentation:**
- [ ] Threading model fully documented ✅
- [ ] Hot reload API documented ✅
- [ ] Log analysis examples provided ✅
- [ ] Implementation notes updated ✅

**Requirements Traceability:**
- [ ] All 10 functional requirements (FR-001 to FR-010) satisfied ✅
- [ ] All 14 non-functional requirements satisfied ✅
- [ ] Traceability matrix validated ✅

**Deployment Readiness:**
- [ ] No blocking issues
- [ ] Performance validated (<1% overhead, <100ms reload)
- [ ] Security validated (no data leakage)
- [ ] Operations runbook complete (log analysis)
- [ ] Ready for production deployment

**Estimated Total Time:**
- Sequential: 44 hours (5.5 days)
- Optimized (3 developers): 30 hours (3.75 days)
- Critical path: 26 hours (minimum possible)

---

## Acceptance Criteria Summary

**Phase 1 (Thread Safety Core):**
- RLock protection on all 12 access sites to `_indexes`
- 100k concurrent operations with zero race conditions
- Lock overhead <1% (negligible performance impact)
- Threading model fully documented
- 4 concurrency standards compliance validated

**Phase 2 (Hot Reload API):**
- 3 new methods: add_index, remove_index, reload_indexes
- Atomic swap under lock (consistent state)
- Reload completes <100ms
- Dynamic logic via INDEX_REGISTRY (config-driven)
- Fractal pattern maintained

**Phase 3 (Observability):**
- Structured logging for 5+ event types
- Machine-readable logs (jq parseable)
- Log analysis queries documented
- No sensitive data leakage (security validated)
- Query latency visibility

---

## Dependencies

### Phase-Level Dependencies

```
Phase 1 (Thread Safety Core)
    ↓ REQUIRED (hard dependency)
Phase 2 (Hot Reload API)
    ↓ RECOMMENDED (soft dependency)
Phase 3 (Observability)
```

**Phase 1 → Phase 2:**
Phase 2 (Hot Reload) depends on Phase 1 (Thread Safety) being complete. Cannot implement atomic index swap (add/remove/reload) without thread-safe _indexes dict access. Hot reload methods acquire the same _indexes_lock that Phase 1 implements.

**Phase 2 → Phase 3:**
Phase 3 (Observability) is RECOMMENDED but not REQUIRED after Phase 2. Logging for hot reload events (index_added, index_removed, indexes_reloaded) benefits from Phase 2 completion, but query logging (Task 3.1) can be implemented independently.

**Critical Path:** Phase 1 → Phase 2 (44 hours sequential)  
**Optimization:** Phase 3 can start after Phase 1 if needed (parallel with Phase 2), reducing total time to ~36 hours.

---

### Task-Level Dependencies

**Phase 1 (No Internal Dependencies):**
- All tasks 1.2-1.8 depend on Task 1.1 (audit) to identify access sites
- Tasks 1.11-1.13 (tests) depend on tasks 1.2-1.8 (lock implementation) being complete
- Tasks 1.9-1.10 (documentation) can be done in parallel with 1.2-1.8
- **Critical Path within Phase 1:** 1.1 → 1.2-1.8 (parallel) → 1.11-1.13 (parallel)

**Phase 2 Internal Dependencies:**
- Task 2.4 (reload_indexes) depends on Task 2.3 (config diff logic)
- Task 2.5 (unit tests) depends on Tasks 2.1, 2.2, 2.4 (methods implemented)
- Task 2.6 (integration test) depends on Task 2.4 (reload_indexes implemented)
- Tasks 2.1, 2.2 can be done in parallel
- **Critical Path within Phase 2:** 2.3 → 2.4 → 2.6

**Phase 3 (Minimal Internal Dependencies):**
- Tasks 3.2-3.4 validate logging added in Phase 2 (soft dependency)
- Task 3.7 (log examples) depends on Tasks 3.1-3.6 (logging implemented)
- Task 3.8 (compliance validation) depends on all other Phase 3 tasks
- Tasks 3.1, 3.5, 3.6 can be done in parallel
- **Critical Path within Phase 3:** 3.1-3.6 (parallel) → 3.7 → 3.8

---

### Task Dependency Matrix

| Task | Depends On | Type | Blocks |
|------|------------|------|--------|
| 1.1 | None | - | 1.2-1.13 |
| 1.2-1.8 | 1.1 | Hard | 1.11-1.13 |
| 1.9-1.10 | 1.1 | Hard | 1.13 (doc validation) |
| 1.11 | 1.2-1.8 | Hard | Phase 1 completion |
| 1.12-1.13 | 1.2-1.8 | Hard | Phase 1 completion |
| 2.1 | Phase 1 complete | Hard | 2.5 |
| 2.2 | Phase 1 complete | Hard | 2.5 |
| 2.3 | Phase 1 complete | Hard | 2.4 |
| 2.4 | 2.3 | Hard | 2.5, 2.6, Phase 2 completion |
| 2.5 | 2.1, 2.2, 2.4 | Hard | Phase 2 completion |
| 2.6 | 2.4 | Hard | Phase 2 completion |
| 3.1 | Phase 1 complete | Soft (Phase 2 not needed) | 3.7, 3.8 |
| 3.2-3.4 | Phase 2 complete | Hard (validate Phase 2 logs) | 3.7, 3.8 |
| 3.5-3.6 | Phase 1 complete | Soft | 3.7, 3.8 |
| 3.7 | 3.1-3.6 | Hard (needs logs to analyze) | 3.8 |
| 3.8 | 3.1-3.7 | Hard (validates all logging) | Phase 3 completion |

---

### Parallel Execution Opportunities

**Phase 1 Parallelization:**
- After Task 1.1 (audit), can split work:
  - Developer A: Tasks 1.2-1.4 (route_action, get_index, health_check_all)
  - Developer B: Tasks 1.5-1.8 (ensure_all, rebuild, update_from_watcher, get_stats)
  - Developer C: Tasks 1.9-1.10 (documentation)
- After code changes complete, can parallelize tests:
  - Developer A: Task 1.11 (concurrent access test)
  - Developer B: Task 1.12 (benchmark test)
  - Developer C: Task 1.13 (stress test)
- **Potential time savings:** ~40% (16 hours → 10 hours with 3 developers)

**Phase 2 Parallelization:**
- Tasks 2.1 (add_index) and 2.2 (remove_index) are independent, can be done in parallel
- After 2.4 (reload_indexes) complete, can parallelize:
  - Developer A: Task 2.5 (unit tests)
  - Developer B: Task 2.6 (integration test)
- **Potential time savings:** ~30% (20 hours → 14 hours with 2 developers)

**Phase 3 Parallelization:**
- Tasks 3.1, 3.5, 3.6 are independent (different methods)
- Tasks 3.2-3.4 are quick validations (can be sequential, minimal impact)
- **Potential time savings:** ~25% (8 hours → 6 hours with 2 developers)

---

### Dependency Validation

✅ **No Circular Dependencies:** All dependencies flow forward (earlier tasks/phases → later tasks/phases)  
✅ **Necessary Dependencies:** All dependencies are required for correctness (not just convenient)  
✅ **Parallel Tasks Identified:** Tasks with no dependencies can run simultaneously  
✅ **Critical Path Identified:** Phase 1 (Task 1.1 → 1.2-1.8 → 1.11-1.13) → Phase 2 (2.3 → 2.4 → 2.6)

**Total Sequential Time:** 44 hours (5.5 days)  
**Optimized Parallel Time:** ~30 hours (3.75 days) with 3 developers  
**Critical Path Time:** ~26 hours (minimum possible with unlimited parallelization)

---

## Out of Scope (Not in MVP)

**Phase 4: Future Enhancements** - Deferred to post-MVP:
- RWLock optimization (only if contention measured)
- Index lifecycle state machine (only if complexity increases)
- FileWatcher thread safety (separate concern)
- Python 3.13 validation (when stable)
- Graceful shutdown protocol (server-wide concern)

**Rationale:** Focus on P0/P1 requirements, optimize later based on evidence

---

## Next: Task Breakdown

Continue to next workflow task to add specific tasks for each phase.

