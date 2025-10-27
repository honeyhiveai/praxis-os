# Implementation Tasks

**Project:** Thread Safety Fixes for MCP Server  
**Date:** 2025-10-13  
**Status:** Draft - Pending Approval  
**Based On:** srd.md (requirements), specs.md (technical design)

---

## Time Estimates

- **Phase 1:** 4-6 hours (Core thread safety implementation)
- **Phase 2:** 2-3 hours (Observability & metrics)
- **Phase 3:** 4-6 hours (Testing & validation)
- **Phase 4:** 2-3 hours (Documentation & deployment)
- **Total:** **12-18 hours** (~2-3 days)

---

## Phase 1: Core Thread Safety Implementation

**Objective:** Implement thread-safe locking for all cache components (WorkflowEngine, RAGEngine, CheckpointLoader) to eliminate race conditions and memory leaks.

**Estimated Duration:** 4-6 hours

**Dependencies:** None (can start immediately after spec approval)

**Deliverables:**
- WorkflowEngine with `_sessions_lock` (double-checked locking)
- RAGEngine with consistent locking in `_check_cache()`
- CheckpointLoader with `_cache_lock` (double-checked locking)
- Metadata cache removed from WorkflowEngine

**Validation Gate:**
- All modified files pass linting (ruff, mypy)
- Code review completed (2+ reviewers)
- Manual smoke tests pass (no crashes)

---

### Phase 1 Tasks

#### Task 1.1: Remove Metadata Cache from WorkflowEngine

**Priority:** CRITICAL (blocking - already completed prior to spec)  
**Estimated Time:** 0 hours (COMPLETED ✅)  
**Assignee:** Platform team

**Description:**
Remove `WorkflowEngine._metadata_cache` and update `load_workflow_metadata()` to load from disk on-demand.

**Acceptance Criteria:**
- [ ] `_metadata_cache: Dict[str, WorkflowMetadata]` removed from `__init__()`
- [ ] `load_workflow_metadata()` loads from disk every time (no cache check/store)
- [ ] Docstring updated to explain on-demand loading and performance (0.03ms)
- [ ] No references to `_metadata_cache` remain in codebase
- [ ] Manual test: Change metadata.json, verify change live without restart

**Files Modified:**
- `mcp_server/workflow_engine.py` (~10 lines deleted, ~5 lines modified)

**Status:** COMPLETED 2025-10-13

---

#### Task 1.2: Add Thread-Safe Session Cache to WorkflowEngine

**Priority:** CRITICAL  
**Estimated Time:** 2-3 hours  
**Assignee:** Platform team  
**Dependencies:** None

**Description:**
Implement double-checked locking pattern for `WorkflowEngine._sessions` cache to prevent duplicate session creation under concurrent access.

**Acceptance Criteria:**
- [ ] Add `_sessions_lock: threading.RLock = threading.RLock()` in `__init__()`
- [ ] Modify `get_session()` to use double-checked locking pattern:
  - Fast path: Check `if session_id in self._sessions` (no lock)
  - Slow path: Acquire lock, re-check, create if still missing
  - Cache store: `self._sessions[session_id] = session`
- [ ] Add `clear_session_cache()` method for test isolation
- [ ] Update docstring to document thread safety guarantees
- [ ] Add inline comments explaining fast path / slow path / re-check
- [ ] Linting: ruff and mypy pass with zero errors
- [ ] Type hints: 100% coverage on modified methods

**Code Pattern (from specs.md Section 2.1):**
```python
def get_session(self, session_id: str) -> WorkflowSession:
    # Fast path: optimistic read (no lock)
    if session_id in self._sessions:
        return self._sessions[session_id]
    
    # Slow path: acquire lock for cache miss
    with self._sessions_lock:
        # Re-check inside lock (critical!)
        if session_id in self._sessions:
            logger.debug("Session %s created by another thread", session_id)
            return self._sessions[session_id]
        
        # Create session (only once per ID)
        state = self.state_manager.load_state(session_id)
        metadata = self.load_workflow_metadata(state.workflow_type)
        session = WorkflowSession(...)
        self._sessions[session_id] = session
        logger.info("Created new session %s", session_id)
        return session
```

**Files Modified:**
- `mcp_server/workflow_engine.py` (~40 lines modified/added)

**Testing Validation:**
- Manual test: Start workflow, verify session cached
- Manual test: Restart MCP server, verify session reloaded from state

---

#### Task 1.3: Fix RAGEngine Locking Consistency

**Priority:** HIGH  
**Estimated Time:** 1-2 hours  
**Assignee:** Search team  
**Dependencies:** None

**Description:**
Move lock acquisition into `_check_cache()` and `_clean_cache()` methods to ensure all cache operations are protected.

**Acceptance Criteria:**
- [ ] Modify `_check_cache()`: Add `with self._lock:` at method start
- [ ] Modify `_clean_cache()`: Use `list(self._query_cache.items())` for iteration safety
- [ ] Update docstrings to clarify lock acquisition requirements
- [ ] Add inline comment: "Lock must be held for all cache operations"
- [ ] Verify `_cache_result()` is only called inside lock (existing, no change needed)
- [ ] Linting: ruff and mypy pass
- [ ] Type hints: Verify Optional[SearchResult] return type on `_check_cache()`

**Code Pattern (from specs.md Section 2.2):**
```python
def _check_cache(self, cache_key: str) -> Optional[SearchResult]:
    """Check cache with lock (FIXED)."""
    with self._lock:  # ← ADDED LOCK
        if cache_key not in self._query_cache:
            return None
        result, timestamp = self._query_cache[cache_key]
        if time.time() - timestamp > self.cache_ttl_seconds:
            del self._query_cache[cache_key]
            return None
        result.cache_hit = True
        return result

def _clean_cache(self) -> None:
    """Clean expired entries (FIXED)."""
    # Must be called while holding self._lock
    expired_keys = [
        key for key, (_, ts) in list(self._query_cache.items())  # ← list() copy
        if time.time() - ts > self.cache_ttl_seconds
    ]
    for key in expired_keys:
        del self._query_cache[key]
```

**Files Modified:**
- `mcp_server/rag_engine.py` (~15 lines modified)

**Testing Validation:**
- Manual test: Run search, verify no RuntimeError
- Manual test: Trigger cache cleanup (>100 entries), verify no crash

---

#### Task 1.4: Add Thread-Safe Checkpoint Cache

**Priority:** MEDIUM  
**Estimated Time:** 1-2 hours  
**Assignee:** Platform team  
**Dependencies:** None (can run in parallel with 1.2)

**Description:**
Implement double-checked locking for `CheckpointLoader._checkpoint_cache` using same pattern as WorkflowEngine.

**Acceptance Criteria:**
- [ ] Add `_cache_lock: threading.RLock = threading.RLock()` in `__init__()`
- [ ] Modify `load_checkpoint_requirements()` to use double-checked locking
  - Fast path: Check cache without lock
  - Slow path: Acquire lock, re-check, load if needed
- [ ] Update docstring to document thread safety guarantees
- [ ] Add inline comments explaining pattern
- [ ] Linting: ruff and mypy pass
- [ ] Type hints: 100% coverage

**Code Pattern (from specs.md Section 2.3):**
```python
def load_checkpoint_requirements(self, workflow_type: str, phase: int) -> Dict[str, Any]:
    cache_key = f"{workflow_type}_phase_{phase}"
    
    # Fast path
    if cache_key in self._checkpoint_cache:
        return self._checkpoint_cache[cache_key]
    
    # Slow path
    with self._cache_lock:
        if cache_key in self._checkpoint_cache:
            return self._checkpoint_cache[cache_key]
        requirements = self._load_from_rag(workflow_type, phase)
        self._checkpoint_cache[cache_key] = requirements
        return requirements
```

**Files Modified:**
- `mcp_server/workflow_engine.py` (CheckpointLoader class, ~25 lines modified/added)

**Testing Validation:**
- Manual test: Complete phase, verify checkpoint loaded
- Manual test: Complete same phase again, verify cached

---

## Phase 2: Observability & Monitoring

**Objective:** Implement cache metrics collection and logging to detect race conditions and monitor performance.

**Estimated Duration:** 2-3 hours

**Dependencies:** Phase 1 complete (need cache implementations to instrument)

**Deliverables:**
- CacheMetrics class with counters
- Logging integration for race detection
- Metrics integration in WorkflowEngine

**Validation Gate:**
- Metrics collected correctly (hits, misses, double_loads, lock_waits)
- Log messages appear when race detected
- Manual testing confirms metrics accuracy

---

### Phase 2 Tasks

#### Task 2.1: Implement CacheMetrics Class

**Priority:** MEDIUM  
**Estimated Time:** 1 hour  
**Assignee:** Observability team  
**Dependencies:** None (can run in parallel with Phase 1)

**Description:**
Create thread-safe CacheMetrics class to track cache performance and detect races.

**Acceptance Criteria:**
- [ ] Create `mcp_server/core/metrics.py` (new file)
- [ ] Implement CacheMetrics class with:
  - `_hits`, `_misses`, `_double_loads`, `_lock_waits` counters
  - `_lock: threading.Lock()` for thread safety
  - `record_hit()`, `record_miss()`, `record_double_load()`, `record_lock_wait()` methods
  - `get_metrics()` returns dict with counters + hit_rate
  - `reset()` for test isolation
- [ ] All methods acquire lock before updating counters
- [ ] Docstrings on all public methods
- [ ] Linting: ruff and mypy pass
- [ ] Type hints: 100% coverage

**Code Pattern (from specs.md Section 2.4):**
```python
class CacheMetrics:
    """Thread-safe cache performance metrics."""
    
    def __init__(self):
        self._hits: int = 0
        self._misses: int = 0
        self._double_loads: int = 0
        self._lock_waits: int = 0
        self._lock: threading.Lock = threading.Lock()
    
    def record_hit(self) -> None:
        with self._lock:
            self._hits += 1
    
    # ... (other methods)
```

**Files Created:**
- `mcp_server/core/metrics.py` (~80 lines new)

**Testing Validation:**
- Manual test: Record metrics, verify counters increment
- Manual test: Call reset(), verify counters zero

---

#### Task 2.2: Integrate Metrics into WorkflowEngine

**Priority:** MEDIUM  
**Estimated Time:** 1 hour  
**Assignee:** Platform team  
**Dependencies:** Task 1.2 (WorkflowEngine locking), Task 2.1 (CacheMetrics)

**Description:**
Add CacheMetrics to WorkflowEngine and instrument `get_session()` to record hits/misses/double-loads.

**Acceptance Criteria:**
- [ ] Add `self.metrics = CacheMetrics()` in `WorkflowEngine.__init__()`
- [ ] In `get_session()` fast path: Call `self.metrics.record_hit()` before return
- [ ] In `get_session()` slow path: Call `self.metrics.record_miss()` after lock acquisition
- [ ] In `get_session()` re-check inside lock: Call `self.metrics.record_double_load()` if found
- [ ] Add `get_metrics()` method to expose metrics externally
- [ ] Update docstrings
- [ ] Linting: ruff and mypy pass

**Files Modified:**
- `mcp_server/workflow_engine.py` (~10 lines added)

**Testing Validation:**
- Manual test: Get session, check metrics (hit or miss)
- Manual test: Concurrent gets, check for double_loads > 0

---

#### Task 2.3: Add Logging for Race Detection

**Priority:** MEDIUM  
**Estimated Time:** 30 minutes  
**Assignee:** Platform team  
**Dependencies:** Task 2.2 (metrics integration)

**Description:**
Add logging statements to warn when double-load detected (race occurred but prevented).

**Acceptance Criteria:**
- [ ] In `WorkflowEngine.get_session()` re-check path: Log WARNING with session_id and thread name
- [ ] Log message: "Race condition detected (double load) - prevented by lock. session_id=%s, thread=%s"
- [ ] Use structured logging with extra fields for session_id and thread
- [ ] Add similar logging to CheckpointLoader
- [ ] Docstrings explain when log messages appear

**Files Modified:**
- `mcp_server/workflow_engine.py` (~3 lines added)

**Testing Validation:**
- Manual test: Trigger concurrent session creation, verify WARNING in logs

---

## Phase 3: Testing & Validation

**Objective:** Implement comprehensive thread safety tests to validate correctness under concurrent load.

**Estimated Duration:** 4-6 hours

**Dependencies:** Phase 1 complete (need implementations to test)

**Deliverables:**
- Unit tests for concurrent session creation (no duplicates)
- Unit tests for concurrent RAG cache access (no iteration errors)
- Integration tests for dual-transport mode
- Benchmark tests for performance regression detection

**Validation Gate:**
- All tests pass 1000+ iterations
- Coverage ≥95% for modified files
- Benchmarks show <5% regression

---

### Phase 3 Tasks

#### Task 3.1: Unit Test - Concurrent Session Creation

**Priority:** HIGH  
**Estimated Time:** 2 hours  
**Assignee:** QA team + Platform team  
**Dependencies:** Task 1.2 (WorkflowEngine locking)

**Description:**
Test that concurrent `get_session()` calls return same object (no duplicate sessions).

**Acceptance Criteria:**
- [ ] Create `tests/unit/test_thread_safety_workflow_engine.py` (new file)
- [ ] Test: `test_concurrent_session_creation()` - 10 threads, same session_id
- [ ] Assert: All threads get same object ID (`id(session)`)
- [ ] Test: `test_no_memory_leak()` - 100 iterations, verify session count matches
- [ ] Test: `test_metrics_record_double_load()` - Verify metrics when race prevented
- [ ] Use threading.Barrier to synchronize thread start (maximize concurrency)
- [ ] Run 1000 iterations to catch rare races
- [ ] All tests pass consistently

**Test Pattern (from specs.md Section 3.5.2):**
```python
def test_concurrent_session_creation():
    engine = WorkflowEngine(...)
    session_id = "test-123"
    results = []
    
    def create():
        session = engine.get_session(session_id)
        results.append(id(session))
    
    threads = [threading.Thread(target=create) for _ in range(10)]
    for t in threads: t.start()
    for t in threads: t.join()
    
    assert len(set(results)) == 1, f"Created {len(set(results))} sessions!"
```

**Files Created:**
- `tests/unit/test_thread_safety_workflow_engine.py` (~150 lines new)

**Testing Validation:**
- Run `pytest tests/unit/test_thread_safety_workflow_engine.py -v`
- All tests pass
- Coverage: ≥95% for WorkflowEngine

---

#### Task 3.2: Unit Test - RAGEngine Cache Safety

**Priority:** HIGH  
**Estimated Time:** 1 hour  
**Assignee:** QA team + Search team  
**Dependencies:** Task 1.3 (RAGEngine locking)

**Description:**
Test that concurrent RAG searches don't crash with RuntimeError during cache cleanup.

**Acceptance Criteria:**
- [ ] Create `tests/unit/test_thread_safety_rag_engine.py` (new file)
- [ ] Test: `test_concurrent_cache_cleanup()` - Concurrent searches + cleanup loops
- [ ] Assert: No RuntimeError exceptions occur
- [ ] Test: `test_cache_ttl_expiration()` - Verify expired entries cleaned
- [ ] Run 1000 iterations
- [ ] All tests pass consistently

**Test Pattern (from specs.md Section 3.5.2):**
```python
def test_concurrent_cache_cleanup():
    rag = RAGEngine(...)
    
    def search_loop():
        for _ in range(100):
            rag.search("test query")
    
    def cleanup_loop():
        for _ in range(100):
            rag._clean_cache()
    
    threads = [
        threading.Thread(target=search_loop),
        threading.Thread(target=cleanup_loop)
    ]
    for t in threads: t.start()
    for t in threads: t.join()
    # Should not raise RuntimeError
```

**Files Created:**
- `tests/unit/test_thread_safety_rag_engine.py` (~100 lines new)

**Testing Validation:**
- Run `pytest tests/unit/test_thread_safety_rag_engine.py -v`
- All tests pass
- Coverage: ≥95% for RAGEngine modified methods

---

#### Task 3.3: Unit Test - CheckpointLoader Thread Safety

**Priority:** MEDIUM  
**Estimated Time:** 1 hour  
**Assignee:** QA team + Platform team  
**Dependencies:** Task 1.4 (CheckpointLoader locking)

**Description:**
Test that concurrent checkpoint loads don't duplicate RAG queries.

**Acceptance Criteria:**
- [ ] Create `tests/unit/test_thread_safety_checkpoint_loader.py` (new file)
- [ ] Test: `test_concurrent_checkpoint_load()` - 10 threads, same workflow+phase
- [ ] Assert: Only 1 RAG query made (verify with mock or counter)
- [ ] Test: `test_checkpoint_cache_hit()` - Verify subsequent loads cached
- [ ] Run 1000 iterations
- [ ] All tests pass

**Files Created:**
- `tests/unit/test_thread_safety_checkpoint_loader.py` (~80 lines new)

**Testing Validation:**
- Run `pytest tests/unit/test_thread_safety_checkpoint_loader.py -v`
- All tests pass
- Coverage: ≥95% for CheckpointLoader

---

#### Task 3.4: Integration Test - Dual Transport Concurrent Access

**Priority:** HIGH  
**Estimated Time:** 2 hours  
**Assignee:** QA team + Platform team  
**Dependencies:** Phase 1 complete

**Description:**
Test dual-transport mode (stdio + HTTP) with concurrent workflow starts to simulate sub-agent scenario.

**Acceptance Criteria:**
- [ ] Create `tests/integration/test_dual_transport_concurrent.py` (new file)
- [ ] Test: `test_stdio_and_http_concurrent_workflow_start()` - Simulate both transports
- [ ] Test: `test_concurrent_get_task()` - Both transports calling get_task()
- [ ] Test: `test_no_state_divergence()` - Verify consistent state across threads
- [ ] Use real MCP server in dual mode (not mocks)
- [ ] Assert: No exceptions, consistent results
- [ ] Run 100 iterations (slower due to full stack)

**Files Created:**
- `tests/integration/test_dual_transport_concurrent.py` (~150 lines new)

**Testing Validation:**
- Run `pytest tests/integration/test_dual_transport_concurrent.py -v`
- All tests pass
- Manual validation: Start dual-mode server, observe no crashes

---

#### Task 3.5: Benchmark Tests - Performance Regression Detection

**Priority:** MEDIUM  
**Estimated Time:** 1-2 hours  
**Assignee:** QA team  
**Dependencies:** Phase 1 complete

**Description:**
Benchmark cache operations to ensure <5% performance regression.

**Acceptance Criteria:**
- [ ] Create `tests/benchmarks/test_thread_safety_performance.py` (new file)
- [ ] Benchmark: `test_get_session_cache_hit_latency()` - Measure 1000 cache hits
- [ ] Benchmark: `test_concurrent_session_creation_throughput()` - Measure throughput
- [ ] Assert: Latency increase <5% compared to baseline
- [ ] Assert: Throughput decrease <5% compared to baseline
- [ ] Run with pytest-benchmark plugin
- [ ] Store results for CI/CD trending

**Files Created:**
- `tests/benchmarks/test_thread_safety_performance.py` (~100 lines new)

**Testing Validation:**
- Run `pytest tests/benchmarks/ --benchmark-only`
- All benchmarks within acceptable range (<5% regression)

---

## Phase 4: Documentation & Deployment

**Objective:** Update documentation, create deployment guide, and prepare for production rollout.

**Estimated Duration:** 2-3 hours

**Dependencies:** Phase 1, 2, 3 complete

**Deliverables:**
- Updated docstrings on all modified methods
- Deployment guide with rollback plan
- Monitoring setup instructions

**Validation Gate:**
- All docstrings complete and accurate
- Deployment guide reviewed and approved
- Code review complete (2+ reviewers)

---

### Phase 4 Tasks

#### Task 4.1: Update Docstrings

**Priority:** MEDIUM  
**Estimated Time:** 1 hour  
**Assignee:** Platform team  
**Dependencies:** Phase 1 complete

**Description:**
Ensure all modified methods have comprehensive docstrings documenting thread safety guarantees.

**Acceptance Criteria:**
- [ ] WorkflowEngine.get_session(): Document thread safety contract
- [ ] RAGEngine._check_cache(): Document lock requirement
- [ ] CheckpointLoader.load_checkpoint_requirements(): Document thread safety
- [ ] CacheMetrics: All public methods have docstrings
- [ ] Sphinx-style docstrings with Args, Returns, Raises sections
- [ ] Thread safety guarantees explicitly stated
- [ ] Performance characteristics documented (fast path / slow path)

**Files Modified:**
- `mcp_server/workflow_engine.py` (~20 lines docstrings added)
- `mcp_server/rag_engine.py` (~10 lines docstrings added)
- `mcp_server/core/metrics.py` (already done in Task 2.1)

**Testing Validation:**
- Run `sphinx-build` to generate docs (if configured)
- Manual review of all docstrings

---

#### Task 4.2: Create Deployment Guide

**Priority:** HIGH  
**Estimated Time:** 1 hour  
**Assignee:** Platform team  
**Dependencies:** Phase 1, 2, 3 complete

**Description:**
Write deployment guide with step-by-step instructions, validation steps, and rollback plan.

**Acceptance Criteria:**
- [ ] Create `.praxis-os/specs/2025-10-13-thread-safety-fixes/DEPLOYMENT.md`
- [ ] Section 1: Pre-deployment checklist (all tests pass, code review)
- [ ] Section 2: Deployment steps (merge PR, restart MCP server)
- [ ] Section 3: Validation (check logs, run manual tests, verify metrics)
- [ ] Section 4: Monitoring (what to watch for first 24 hours)
- [ ] Section 5: Rollback plan (revert commits, restart server)
- [ ] Section 6: Troubleshooting (common issues and fixes)
- [ ] Include specific commands and examples
- [ ] Reviewed by 2+ team members

**Files Created:**
- `.praxis-os/specs/2025-10-13-thread-safety-fixes/DEPLOYMENT.md` (~50 lines new)

**Testing Validation:**
- Follow deployment guide in staging environment
- Verify all steps work as documented

---

#### Task 4.3: Update Monitoring Setup

**Priority:** MEDIUM  
**Estimated Time:** 1 hour  
**Assignee:** Observability team  
**Dependencies:** Task 2.2 (metrics integration)

**Description:**
Document how to access cache metrics and set up alerts for race detection / lock contention.

**Acceptance Criteria:**
- [ ] Add section to DEPLOYMENT.md on accessing metrics
- [ ] Example: `engine.metrics.get_metrics()` returns dict
- [ ] Document alert thresholds:
  - `double_loads > 10/hour` → Investigate
  - `lock_waits / total > 5%` → Performance issue
  - `hit_rate < 90%` → Cache not effective
- [ ] Future: Prometheus export integration (P2, not in scope)

**Files Modified:**
- `.praxis-os/specs/2025-10-13-thread-safety-fixes/DEPLOYMENT.md` (~20 lines added)

**Testing Validation:**
- Manual: Access metrics via Python REPL
- Verify metrics dict structure matches documentation

---

## Implementation Summary

**Total Tasks:** 16 tasks across 4 phases  
**Total Estimated Time:** 12-18 hours (~2-3 days)

**Task Breakdown:**
- Phase 1 (Core): 4 tasks, 4-6 hours
- Phase 2 (Observability): 3 tasks, 2-3 hours
- Phase 3 (Testing): 5 tasks, 4-6 hours
- Phase 4 (Documentation): 3 tasks, 2-3 hours

**Critical Path:**
1. Task 1.2 (WorkflowEngine locking) → Task 2.2 (metrics) → Task 3.1 (tests)
2. Task 1.3 (RAGEngine locking) → Task 3.2 (tests)

**Parallel Work Opportunities:**
- Phase 1 tasks 1.2, 1.3, 1.4 can run in parallel
- Task 2.1 (CacheMetrics) can start before Phase 1 complete
- Phase 3 tests can be written concurrently by different team members

**Files Affected:**
- **Modified:** 2 files (workflow_engine.py, rag_engine.py)
- **Created:** 7 files (metrics.py, 5 test files, DEPLOYMENT.md)
- **Total LOC:** ~580 lines changed (per specs.md Section 2.8)

**Teams Involved:**
- Platform team: 4 tasks (primary owners)
- Search team: 1 task (RAGEngine)
- Observability team: 2 tasks (metrics)
- QA team: 5 tasks (testing)

**Risk Mitigation:**
- All changes backward compatible (no breaking changes)
- Comprehensive test coverage before production
- Staged rollout with monitoring
- Clear rollback plan in deployment guide

---

**END OF TASKS.MD**

**Next Step:** Map dependencies and validation gates (Task 2, 3, 4, 5 of Phase 3)

