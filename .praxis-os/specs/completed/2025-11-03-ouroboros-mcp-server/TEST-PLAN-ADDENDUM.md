# Test Plan Addendum

**Project:** Ouroboros MCP Server  
**Date:** 2025-11-06  
**Purpose:** Comprehensive test plan with 100% requirements traceability  
**Status:** Addendum to completed spec (retrofitting testing)

---

## Executive Summary

This addendum provides a complete test plan for the Ouroboros MCP Server specification, ensuring 100% traceability from requirements to test cases.

**Key Findings:**
- **Total Requirements:** 69 (25 FRs + 44 NFRs)
- **Total Test Cases Defined:** 140+ (75 functional + 65 non-functional)
- **Critical Gap Identified:** FR-015 (File Watcher) had **ZERO tests**, which allowed the initialization bug to reach production
- **Test Implementation Status:** ~52 tests exist, ~118 tests needed

**Test Plan Structure:**
1. Requirements List (all 69 requirements extracted)
2. Traceability Matrix (requirements → test files → test functions)
3. Functional Test Cases (75 test cases for 25 FRs)
4. Non-Functional Test Cases (65 test cases for 44 NFRs)
5. Testing Strategy (unit, integration, mocking, execution)

---

## 1. Requirements List

**Source:** `testing/requirements-list.md`

### Functional Requirements (25 FRs)

| FR ID | Description | Priority |
|-------|-------------|----------|
| FR-001 | Query Prepend Generation | High |
| FR-002 | Query Tracking and Persistence | High |
| FR-003 | Query Diversity Classification | High |
| FR-004 | Behavioral Drift Detection | Medium |
| FR-005 | pos_search_project - Unified Search Tool | High |
| FR-006 | pos_workflow - Workflow Execution Tool | High |
| FR-007 | pos_browser - Browser Automation Tool | High |
| FR-008 | pos_filesystem - File Operations Tool | High |
| FR-009 | get_server_info - Server Status Tool | Medium |
| FR-010 | Tool Auto-Discovery and Registration | High |
| FR-011 | Standards Search (Hybrid: Vector + FTS + RRF + Rerank) | High |
| FR-012 | Code Semantic Search (LanceDB) | Medium |
| FR-013 | Code Graph Traversal (DuckDB) | Medium |
| FR-014 | AST Structural Search (Tree-sitter) | Medium |
| **FR-015** | **File Watcher (Incremental Index Updates)** | **High** |
| FR-016 | Index Health Checks and Auto-Repair | High |
| FR-017 | Phase-Gated Execution | High |
| FR-018 | Evidence Validation (Multi-Layer) | High |
| FR-019 | Hidden Evidence Schemas | High |
| FR-020 | Workflow State Persistence | High |
| FR-021 | Isolated Playwright Sessions | Medium |
| FR-022 | Browser Actions | Medium |
| FR-023 | Pydantic v2 Schema Validation | High |
| FR-024 | Config-Driven Language Support | Medium |
| FR-025 | Fail-Fast Validation | High |

### Non-Functional Requirements (44 NFRs)

**Categories:**
- **Performance (7):** Cold start, config load, search latency, incremental updates, prepend overhead, memory
- **Reliability (5):** Uptime, health checks, auto-repair, degradation, data integrity
- **Security (4):** Adversarial design, query sanitization, path traversal, secrets
- **Scalability (3):** Document scaling, symbol scaling, concurrent queries
- **Maintainability (5):** No circular deps, clean architecture, test coverage, error quality, documentation
- **Usability (4):** Error discoverability, fail-fast, behavioral feedback, tool discoverability
- **Extensibility (3):** Config-driven languages, pluggable tools, custom workflows
- **Portability (3):** MacOS, Linux, WSL2
- **Compatibility (3):** MCP protocol, index format, Python versions
- **Observability (4):** Structured logging, query metrics, performance metrics, behavioral metrics
- **Testability (3):** Unit test isolation, integration coverage, performance repeatability

**Full requirements list:** See `testing/requirements-list.md`

---

## 2. Traceability Matrix

**Source:** `testing/traceability-matrix.md`

### Critical Finding: FR-015 (File Watcher) Gap

```
FR-015: File Watcher
├── Test File: tests/ouroboros/subsystems/rag/test_file_watcher.py
├── Status: ❌ MISSING (ZERO TESTS)
├── Impact: Production bug (watcher not initialized in ouroboros/server.py)
└── Tests Needed:
    ├── test_watcher_detects_file_changes() 
    ├── test_watcher_triggers_index_update()
    ├── test_watcher_debouncing()
    ├── test_watcher_path_mapping()
    ├── test_watcher_initialization_on_server_start() ← Would have caught bug
    └── test_watcher_graceful_failure()
```

**This is the test that would have prevented the production bug:** Test Case 15.7 validates that FileWatcher is initialized on server start, which was missing from `ouroboros/server.py`.

### Traceability Summary

- **FRs mapped to tests:** 25/25 (100%)
- **NFRs mapped to tests:** 44/44 (100%)
- **Tests existing:** ~52 (~37 unit, ~13 integration, ~2 performance/security)
- **Tests planned:** ~118
- **Total test coverage planned:** ~170 test functions

**Test Organization:**
```
tests/
├── ouroboros/
│   ├── subsystems/
│   │   └── rag/
│   │       ├── test_index_manager.py (✅ exists)
│   │       ├── test_file_watcher.py (❌ CRITICAL MISSING)
│   │       ├── test_code_index.py (❌ planned)
│   │       ├── test_graph_index.py (❌ planned)
│   │       └── test_ast_index.py (❌ planned)
│   ├── integration/
│   │   ├── test_search_flow.py (✅ exists)
│   │   ├── test_file_watcher_latency.py (❌ MISSING - NFR-P5)
│   │   └── test_index_health.py (❌ planned)
│   └── performance/
│       └── test_performance.py (partial - needs NFR tests)
└── security/
    ├── test_path_validation.py (❌ planned)
    ├── test_query_logging.py (❌ planned)
    └── test_secrets.py (❌ planned)
```

**Full traceability matrix:** See `testing/traceability-matrix.md`

---

## 3. Functional Test Cases

**Source:** `testing/functional-test-cases.md`

### 3.1 Middleware Tests (FR-001 to FR-004)

**FR-001: Query Prepend Generation**
- Test 1.1: Prepend includes gamification content (✅ exists)
- Test 1.2: Prepend adapts to query diversity
- Test 1.3: First query gets bootstrap prepend

**FR-002: Query Tracking**
- Test 2.1: All queries logged to SQLite (✅ exists)
- Test 2.2: Session context captured
- Test 2.3: Query metadata persisted

**FR-003: Query Diversity Classification**
- Test 3.1-3.5: All 5 angles classified (✅ exists)

**FR-004: Behavioral Drift Detection**
- Test 4.1: Diversity drop detected (❌ planned)
- Test 4.2: Prepends strengthened on drift (❌ planned)

---

### 3.2 Tool Tests (FR-005 to FR-009)

**FR-005: pos_search_project Tool** (❌ No comprehensive tests)
- Test 5.1: search_standards routes to StandardsIndex
- Test 5.2: search_code routes to CodeIndex
- Test 5.3: find_callers routes to GraphIndex
- Test 5.4: find_dependencies routes correctly
- Test 5.5: find_call_paths routes correctly
- Test 5.6: search_ast routes to ASTIndex

**FR-006: pos_workflow Tool** (✅ Partial coverage)
- Test 6.1: start action creates session (✅ exists)
- Test 6.2: get_phase returns current phase (✅ exists)
- Test 6.3: complete_phase validates evidence (✅ exists)

**FR-007-009:** Browser, Filesystem, ServerInfo tools (mixed coverage)

---

### 3.3 RAG Subsystem Tests (FR-011 to FR-015)

**FR-011: Standards Hybrid Search**
- Test 11.1: Hybrid combines vector + FTS (✅ exists)
- Test 11.2: RRF fusion applied
- Test 11.3: Reranking optional (❌ planned)

**FR-012: Code Semantic Search** (❌ No tests)
- Test 12.1: CodeBERT embeddings used

**FR-013: Code Graph Traversal** (❌ No tests)
- Test 13.1: find_callers uses recursive CTE
- Test 13.2: find_dependencies uses recursive CTE
- Test 13.3: find_call_paths finds full paths

**FR-014: AST Structural Search** (❌ No tests)
- Test 14.1: Tree-sitter parser used

---

### 3.4 FR-015: File Watcher Tests (CRITICAL - ALL MISSING)

**❌ ZERO TESTS EXIST - This is why the bug reached production**

**Test Case 15.1: Watcher detects new file creation**
- Setup: FileWatcher monitoring `.praxis-os/standards/`
- Action: Create new file in standards/
- Assert: File change event detected
- Evidence: FR-015.1 validated

**Test Case 15.2: Watcher detects file modifications**
- Setup: FileWatcher running
- Action: Modify existing file
- Assert: Modification event detected
- Evidence: FR-015.2 validated

**Test Case 15.3: Watcher detects file deletions**
- Setup: FileWatcher running
- Action: Delete file
- Assert: Deletion event detected
- Evidence: FR-015.3 validated

**Test Case 15.4: Watcher triggers incremental index update**
- Setup: FileWatcher running, index initialized
- Action: Create new standards file with unique term "XYZTESTTERM"
- Assert: Within 5s, search for "XYZTESTTERM" returns the new file
- Evidence: FR-015.4 validated (hot reload works)

**Test Case 15.5: Watcher uses path_mappings correctly**
- Setup: FileWatcher with path_mappings
- Action: Modify file in /standards
- Assert: Only standards index updated, not code indexes
- Evidence: FR-015.5 validated

**Test Case 15.6: Watcher debounces rapid changes**
- Setup: FileWatcher running
- Action: Make 10 rapid edits to same file
- Assert: Only 1 index update triggered (debounced)
- Evidence: FR-015.6 validated

**Test Case 15.7: Watcher initialization on server start** ← **WOULD HAVE CAUGHT THE BUG**
- Setup: Start Ouroboros server with `config.indexes.file_watcher.enabled=True`
- Action: Check logs for "FileWatcher started"
- Assert: FileWatcher initialized and started
- Evidence: FR-015.7 validated
- **Impact:** This test would have caught the missing FileWatcher initialization in `ouroboros/server.py`

**Test Case 15.8: Watcher graceful failure if IndexManager unavailable**
- Setup: Start server with IndexManager disabled
- Action: Check FileWatcher behavior
- Assert: FileWatcher skips initialization gracefully, warning logged
- Evidence: FR-015.8 validated

---

### 3.5 Workflow & Browser Tests (FR-017 to FR-022)

**FR-017: Phase-Gated Execution**
- Test 17.1: Cannot skip phases (✅ exists)

**FR-018: Evidence Validation (Multi-Layer)** (✅ Comprehensive tests exist)
- Test 18.1-18.5: All 5 validation layers tested

**FR-019-022:** Workflow state, browser sessions, browser actions (mixed coverage)

---

### 3.6 Config System Tests (FR-023 to FR-025)

**FR-023: Pydantic v2 Validation** (❌ No dedicated tests)
- Test 23.1: Config validates on load
- Test 23.2: Invalid config fails fast

**FR-024: Config-Driven Languages** (❌ No tests)
- Test 24.1: Add language via YAML only

**FR-025: Fail-Fast Validation** (❌ No tests)
- Test 25.1: All validation at startup

**Full functional test cases:** See `testing/functional-test-cases.md`

---

## 4. Non-Functional Test Cases

**Source:** `testing/nonfunctional-test-cases.md`

### 4.1 Performance Tests (NFR-P1 to NFR-P7)

**NFR-P1: Server Cold Start Time (<30s p95)**
- Test P1.1: Measure cold start latency (✅ exists)
- Test P1.2: Identify startup bottlenecks

**NFR-P2: Config Load Time (<100ms p95)**
- Test P2.1: Measure config validation latency (❌ planned)

**NFR-P3: Search Latency - Hybrid (<200ms p95)**
- Test P3.1: Measure hybrid search latency (❌ planned)
- Test P3.2: Search latency under load

**NFR-P4: Code Graph Traversal (<100ms p95)**
- Test P4.1: Measure graph query latency (❌ planned)

**NFR-P5: Incremental Index Update (<5s p95)** ← **Critical for FileWatcher validation**
- **Test P5.1: File-save-to-searchable latency** (❌ MISSING)
  - Setup: FileWatcher running, StandardsIndex initialized
  - Action: 100 iterations: (1) Save file with unique term, (2) Search for term, (3) Measure time delta
  - Metric: Calculate p95 of (search_success_time - file_save_time)
  - Pass Criteria: p95 < 5 seconds
  - Evidence: NFR-P5 validated (hot reload performance)
- Test P5.2: Large file incremental update

**NFR-P6: Prepend Generation (<5ms p95)**
- Test P6.1: Measure prepend latency (❌ planned)

**NFR-P7: Memory Usage (<2GB RSS)**
- Test P7.1: Normal operation memory (❌ planned)
- Test P7.2: Memory leak detection

---

### 4.2 Reliability Tests (NFR-R1 to NFR-R5)

**NFR-R1: Uptime (24+ hours)**
- Test R1.1: 24-hour soak test (❌ planned)
- Test R1.2: Soak test under load

**NFR-R2: Health Check Coverage (95%+ detection)**
- Test R2.1: Inject corruption scenarios (❌ planned)

**NFR-R3: Auto-Repair Success (90%+)**
- Test R3.1: Measure auto-repair success (❌ planned)

**NFR-R4: Graceful Degradation**
- Test R4.1: FTS failure fallback (❌ planned)

**NFR-R5: Data Integrity**
- Test R5.1: Incremental vs full rebuild (❌ planned)

---

### 4.3 Security Tests (NFR-S1 to NFR-S4)

**NFR-S1: Adversarial Design (99%+ rejection)**
- Test S1.1: Gaming attempts rejected (✅ exists)

**NFR-S2: Query Sanitization (No PII)**
- Test S2.1: PII not logged (❌ planned)

**NFR-S3: Path Traversal Prevention**
- Test S3.1: All traversal attempts blocked (❌ planned)

**NFR-S4: Secrets Management**
- Test S4.1: No secrets in git (❌ planned)
- Test S4.2: No secrets in logs (❌ planned)

---

### 4.4 Other NFR Categories

**Scalability (NFR-SC1 to SC3):**
- SC1: 50K documents (❌ planned)
- SC2: 100K symbols (❌ planned)
- SC3: 10 concurrent queries (✅ exists)

**Maintainability (NFR-M1 to M5):**
- M1: No circular dependencies (❌ planned)
- M2: Clean architecture (❌ planned)
- M3: Integration test coverage ≥60% (❌ planned)
- M4: Error message quality (❌ planned)
- M5: Documentation coverage (❌ planned)

**Usability, Extensibility, Portability, Compatibility, Observability, Testability:**
- Mixed status, mostly planned

**Full non-functional test cases:** See `testing/nonfunctional-test-cases.md`

---

## 5. Testing Strategy

**Source:** `testing/testing-strategy.md`

### 5.1 Testing Philosophy

**Core Principle:** Tests are specifications.

- **Unit tests:** Validate individual functions/classes in isolation
- **Integration tests:** Validate subsystems working together
- **Performance tests:** Validate NFR metrics
- **End-to-end tests:** Validate complete workflows

**Coverage Targets:**
- Unit test coverage: ≥50%
- Integration test coverage: ≥60%
- Critical path coverage: 100% (every FR/NFR has tests)

---

### 5.2 Unit Testing Strategy

**Principles:**
1. No external dependencies (no file I/O, DB, network)
2. Fast execution (<10ms per test)
3. Isolated (tests don't affect each other)
4. Deterministic (no flakiness)

**Mocking Strategy:**

**Mock these:**
- File system I/O (`open`, `Path.read_text`)
- Database connections (SQLite, DuckDB, LanceDB)
- Network calls (HTTP, external APIs)
- Time-dependent operations (`datetime.now()`)

**Don't mock these:**
- Pure business logic
- Data transformations
- Pydantic models
- Simple utilities

**Example:** Pure function testing

```python
def test_classify_conceptual_query():
    """Test that conceptual questions are classified correctly."""
    query = "How does the workflow system work?"
    result = classify_query_angle(query)
    assert result == "conceptual"
```

---

### 5.3 Integration Testing Strategy

**Principles:**
1. Use real components (not mocks)
2. Create/cleanup temporary resources
3. Test realistic scenarios
4. Acceptable latency (seconds, not milliseconds)

**Critical Pattern: FileWatcher Integration Test**

```python
@pytest.fixture
def file_watcher_setup(tmp_path):
    """Setup FileWatcher with temp paths."""
    standards_dir = tmp_path / "standards"
    standards_dir.mkdir()
    
    index_dir = tmp_path / "indexes"
    index_dir.mkdir()
    
    # Create index
    index_manager = IndexManager(index_dir)
    index_manager.indexes["standards"] = StandardsIndex(index_dir, standards_dir)
    
    # Create watcher
    config = FileWatcherConfig(
        enabled=True,
        debounce_seconds=0.5,
        check_interval_seconds=0.1
    )
    
    path_mappings = {
        str(standards_dir): ["standards"]
    }
    
    watcher = FileWatcher(config, index_manager, path_mappings)
    watcher.start()
    
    yield standards_dir, index_manager, watcher
    
    # Cleanup
    watcher.stop()

def test_file_watcher_detects_and_indexes_new_file(file_watcher_setup):
    """Test FileWatcher detects new file and triggers index update."""
    standards_dir, index_manager, watcher = file_watcher_setup
    
    # Create new file with unique term
    unique_term = f"UNIQUETERM{time.time()}"
    (standards_dir / "new-file.md").write_text(f"# New File\n\n{unique_term}")
    
    # Wait for watcher to detect and index (max 5s)
    for _ in range(50):  # 50 * 0.1s = 5s max
        time.sleep(0.1)
        results = index_manager.indexes["standards"].search(unique_term, n_results=1)
        if len(results) > 0:
            break
    
    # Assert file was indexed
    assert len(results) > 0
    assert unique_term in results[0].content
    assert "new-file.md" in results[0].file_path
```

---

### 5.4 Test Execution

**Running tests:**

```bash
# All tests
pytest tests/

# Unit tests only (fast)
pytest tests/unit/ tests/ouroboros/ -m "not integration"

# Integration tests only
pytest tests/integration/ tests/ouroboros/integration/

# Performance tests
pytest tests/ouroboros/performance/ --performance

# Specific test file
pytest tests/ouroboros/subsystems/rag/test_file_watcher.py

# With coverage
pytest tests/ --cov=ouroboros --cov-report=html

# Parallel execution
pytest tests/ -n auto
```

**Test markers:**

```python
@pytest.mark.integration
def test_file_watcher_flow():
    ...

@pytest.mark.performance
@pytest.mark.slow
def test_cold_start_latency():
    ...
```

---

### 5.5 Test Organization

```
tests/
├── unit/                          # Isolated unit tests
│   ├── test_config_loader.py
│   └── test_prepend_generator.py
│
├── integration/                   # Cross-subsystem tests
│   ├── test_search_flow.py
│   └── test_workflow_flow.py
│
├── ouroboros/                     # Mirrors source structure
│   ├── subsystems/
│   │   ├── rag/
│   │   │   ├── test_index_manager.py (✅)
│   │   │   ├── test_file_watcher.py (❌ CRITICAL)
│   │   │   ├── test_code_index.py (❌)
│   │   │   ├── test_graph_index.py (❌)
│   │   │   └── test_ast_index.py (❌)
│   │   ├── workflow/
│   │   └── browser/
│   ├── integration/
│   │   ├── test_file_watcher_latency.py (❌ CRITICAL)
│   │   ├── test_index_health.py (❌)
│   │   └── test_reliability_soak.py (❌)
│   └── performance/
│       └── test_performance.py (partial)
│
└── security/
    ├── test_path_validation.py (❌)
    ├── test_query_logging.py (❌)
    └── test_secrets.py (❌)
```

**Full testing strategy:** See `testing/testing-strategy.md`

---

## 6. Priority Test Implementation Roadmap

### Priority 1 (Essential - Implement First)

**These tests would have caught the FileWatcher bug:**

1. **`tests/ouroboros/subsystems/rag/test_file_watcher.py`** (8 tests)
   - FR-015: All FileWatcher functionality
   - **Test 15.7 is the smoking gun:** Validates watcher starts on server init
   - Estimated effort: 4-6 hours

2. **`tests/ouroboros/integration/test_file_watcher_latency.py`** (2 tests)
   - NFR-P5: File-save-to-searchable latency (<5s p95)
   - Validates end-to-end hot reload performance
   - Estimated effort: 2-3 hours

3. **`tests/ouroboros/integration/test_search_flow.py`** (extend)
   - FR-011: Hybrid search with RRF + reranking
   - Currently partial, needs comprehensive coverage
   - Estimated effort: 2-3 hours

4. **`tests/ouroboros/tools/test_pos_search.py`** (6 tests)
   - FR-005: All 6 search action routes validated
   - Estimated effort: 3-4 hours

**Total Priority 1 Effort:** 11-16 hours

---

### Priority 2 (Important - Implement Second)

5. **Config System Tests:**
   - `tests/ouroboros/config/test_config_validation.py` (FR-023, FR-025)
   - Estimated effort: 2-3 hours

6. **Graph Index Tests:**
   - `tests/ouroboros/subsystems/rag/test_graph_index.py` (FR-013)
   - Estimated effort: 3-4 hours

7. **Performance Tests:**
   - `tests/ouroboros/performance/test_performance.py` (NFR-P1-P7)
   - Estimated effort: 6-8 hours

8. **Index Health Tests:**
   - `tests/ouroboros/integration/test_index_health.py` (NFR-R2, NFR-R3)
   - Estimated effort: 4-5 hours

**Total Priority 2 Effort:** 15-20 hours

---

### Priority 3 (Nice to Have)

9. **Security Tests:**
   - `tests/security/*` (NFR-S1-S4)
   - Estimated effort: 4-6 hours

10. **Architecture Validation:**
    - `tests/ouroboros/validation/test_architecture.py` (NFR-M1, NFR-M2)
    - Estimated effort: 2-3 hours

**Total Priority 3 Effort:** 6-9 hours

---

### Implementation Timeline

**Immediate (Week 1):**
- Priority 1: FileWatcher tests (11-16 hours)
- **Prevents future FileWatcher bugs**

**Short-term (Week 2-3):**
- Priority 2: Config, graph, performance, health (15-20 hours)
- **Achieves 70%+ critical path coverage**

**Medium-term (Month 1):**
- Priority 3: Security, architecture (6-9 hours)
- **Achieves 90%+ coverage**

**Total Test Implementation Effort:** 32-45 hours

---

## 7. Lessons Learned

### 7.1 Root Cause Analysis: FileWatcher Bug

**What happened:**
- FR-015 (File Watcher) was fully specified in the SRD
- Implementation was complete in `ouroboros/subsystems/rag/watcher.py`
- **But:** FileWatcher was never initialized in `ouroboros/server.py`
- Bug reached production, preventing hot reload of standards

**Why it happened:**
- **Zero tests for FR-015** (no test enforcing initialization)
- No traceability matrix mapping FR-015 → test cases
- Testing section in `implementation.md` was generic, not requirements-driven
- No evidence gate requiring "all FRs have test plans"

**How this test plan prevents recurrence:**
- 100% requirements traceability (every FR/NFR → tests)
- Test Case 15.7 explicitly validates server initialization
- Traceability matrix makes gaps visible
- Requirements-driven test planning, not ad-hoc

---

### 7.2 Value of Requirements Traceability

**Before this test plan:**
- Testing was implementation-driven ("test what we built")
- Gaps invisible until production failure
- No systematic way to verify completeness

**After this test plan:**
- Testing is requirements-driven ("test what we specified")
- Gaps visible in traceability matrix
- Systematic verification: every FR/NFR must have ≥1 test

**Traceability Matrix as Quality Gate:**
```
Requirement → Test File → Test Function → Status

If ANY requirement shows "❌ MISSING", the spec is incomplete.
```

This is **adversarial design for specifications**: the structure prevents incomplete testing.

---

### 7.3 Workflow Improvement: spec_creation_v1

**Gap identified:** The `spec_creation_v1` workflow that created this spec had a vague "Testing Strategy" task that didn't enforce:
- Requirements extraction for test planning
- Traceability matrix creation
- Test case definition for every FR/NFR
- Evidence gates for testing completeness

**Fix:** Updated `spec_creation_v1` Phase 4 with 6 new testing tasks:
- Task 3: Discover requirements for testing
- Task 4: Requirements traceability matrix
- Task 5: Functional test cases
- Task 6: Non-functional test cases
- Task 7: Unit/integration testing strategy
- Task 8: Consolidate test plan

**Impact:** Every future spec will have 100% requirements traceability by default.

---

## 8. Test Plan Validation Checklist

Before marking this addendum complete, verify:

- [x] All 69 requirements extracted into `requirements-list.md`
- [x] Traceability matrix created mapping all requirements to tests
- [x] 75 functional test cases defined for 25 FRs
- [x] 65 non-functional test cases defined for 44 NFRs
- [x] Testing strategy documented (unit, integration, mocking, execution)
- [x] FileWatcher tests defined (8 tests including initialization check)
- [x] Priority 1-3 implementation roadmap created
- [ ] Priority 1 tests implemented (in progress)
- [ ] 100% critical path coverage achieved (pending Priority 1-2 implementation)

---

## 9. Related Documents

**This Addendum:**
- `testing/requirements-list.md` - All 69 requirements extracted from srd.md
- `testing/traceability-matrix.md` - Requirements → tests mapping
- `testing/functional-test-cases.md` - 75 test cases for FRs
- `testing/nonfunctional-test-cases.md` - 65 test cases for NFRs
- `testing/testing-strategy.md` - Unit, integration, mocking, execution strategy

**Original Spec:**
- `srd.md` - Software Requirements Document (25 FRs, 44 NFRs)
- `specs.md` - Technical Specification
- `implementation.md` - Implementation Approach (original testing section generic)
- `tasks.md` - Implementation Tasks

---

## 10. Conclusion

This test plan addendum provides **100% requirements traceability** for the Ouroboros MCP Server, ensuring every functional and non-functional requirement is mapped to concrete, actionable test cases.

**Key Deliverables:**
1. ✅ 69 requirements extracted and categorized
2. ✅ Traceability matrix with 100% coverage
3. ✅ 140+ test cases defined
4. ✅ Testing strategy documented
5. ✅ Priority implementation roadmap

**Critical Finding:**
The FileWatcher production bug (FR-015) occurred because **zero tests existed** for a high-priority functional requirement. Test Case 15.7 (server initialization validation) would have caught this bug immediately.

**Next Steps:**
1. Implement Priority 1 tests (11-16 hours) to prevent future FileWatcher issues
2. Implement Priority 2 tests (15-20 hours) for 70%+ critical path coverage
3. Integrate this test plan into CI/CD pipeline
4. Use this addendum as a template for future specs

**Mission Accomplished:** This spec now has the test plan it should have had from day one.

---

**Addendum Status:** ✅ Complete  
**Test Implementation Status:** 🚧 In Progress (Priority 1)  
**Total Effort Required:** 32-45 hours to full coverage  
**Date:** 2025-11-06

