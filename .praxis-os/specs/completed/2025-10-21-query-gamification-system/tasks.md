# Implementation Tasks

**Project:** Query Gamification System  
**Date:** 2025-10-21  
**Status:** Draft - Pending Approval

---

## Time Estimates

- **Phase 1: Foundation** - 4-6 hours (Core modules implementation)
- **Phase 2: Integration** - 2-3 hours (MCP tool enhancement)
- **Phase 3: Testing** - 3-4 hours (Comprehensive test suite)
- **Phase 4: Finalization** - 1-2 hours (Documentation and validation)
- **Total:** 10-15 hours (1.5-2 days of focused development)

---

## Phase 1: Foundation

**Objective:** Implement the four core modules that provide gamification functionality. These modules are the building blocks for the query tracking and feedback system.

**Estimated Duration:** 4-6 hours

### Phase 1 Tasks

- [x] **Task 1.1**: Implement Query Classifier Module (M - 1.5-2 hours)
  - Create `mcp_server/core/query_classifier.py`
  - Define `QueryAngle` type alias (5 angle literals)
  - Implement `classify_query_angle(query: str) -> QueryAngle` function
  - Define keyword patterns for each angle (definition, location, practical, best_practice, error_prevention)
  - Implement `get_angle_emoji(angle: QueryAngle) -> str` function
  - Implement `get_angle_suggestion(angle: QueryAngle, topic: str) -> str` function
  - Verify classification accuracy with sample queries
  - Verify performance ≤5ms for classification
  - **Traces to:** specs.md Section 2.1 (QueryClassifier Component)
  
  **Acceptance Criteria:**
  - [ ] `QueryAngle` type alias defined with exactly 5 literals ('definition', 'location', 'practical', 'best_practice', 'error_prevention')
  - [ ] `classify_query_angle()` function exists with correct type signature (str → QueryAngle)
  - [ ] All 5 angles have keyword patterns defined (≥5 keywords per angle)
  - [ ] Classification accuracy ≥90% on sample set of 50 queries (10 per angle)
  - [ ] Classification latency ≤5ms average (100 sample runs)
  - [ ] `get_angle_emoji()` returns correct emoji for all 5 angles
  - [ ] `get_angle_suggestion()` generates valid suggestion strings
  - [ ] All functions have complete docstrings (Args, Returns, Examples)
  - [ ] Module passes `mypy --strict` with zero errors
  - [ ] Module passes linter with zero errors

- [x] **Task 1.2**: Implement Query Tracker Module (M - 2-2.5 hours)
  - Create `mcp_server/core/query_tracker.py`
  - Define `QueryStats` dataclass with all fields (total_queries, unique_queries, angles_covered, query_history, last_query_time)
  - Implement singleton `QueryTracker` class with `_sessions` dictionary
  - Implement `record_query(session_id, query)` method with validation
  - Implement uniqueness detection (normalized query comparison)
  - Implement query history management (FIFO, max 10)
  - Implement `get_stats(session_id)` method
  - Implement `get_uncovered_angles(session_id)` method
  - Implement `reset_session(session_id)` method (for testing)
  - Implement module-level `get_tracker()` singleton accessor
  - Verify memory per session ~1KB
  - Verify latency ≤2ms for record_query
  - **Traces to:** specs.md Section 2.2 (QueryTracker Component)
  
  **Acceptance Criteria:**
  - [ ] `QueryStats` dataclass defined with all 5 fields (total_queries, unique_queries, angles_covered, query_history, last_query_time)
  - [ ] `QueryTracker` class implements singleton pattern (single instance per process)
  - [ ] `record_query()` correctly increments total_queries on every call
  - [ ] Uniqueness detection works: "What is X?" and "what is x?" counted as same query
  - [ ] Query history limited to 10 entries (FIFO eviction when >10)
  - [ ] `get_stats()` returns accurate QueryStats for given session
  - [ ] `get_uncovered_angles()` returns set of angles not yet covered
  - [ ] Memory per session ≤1.5KB (measured with `sys.getsizeof()`)
  - [ ] `record_query()` latency ≤2ms average (100 sample runs)
  - [ ] All methods have complete docstrings (Args, Returns, Examples)
  - [ ] Module passes `mypy --strict` with zero errors
  - [ ] Module passes linter with zero errors

- [x] **Task 1.3**: Implement Prepend Generator Module (S - 1-1.5 hours)
  - Create `mcp_server/core/prepend_generator.py`
  - Implement `generate_query_prepend(tracker, session_id, current_query)` function
  - Implement topic extraction from query (remove common words)
  - Implement suggestion selection logic (deterministic angle ordering)
  - Implement progress line formatting (emojis, query count, angles covered)
  - Implement completion detection (5+ queries, 4+ angles)
  - Enforce token budget (≤120 tokens max, ~85 avg)
  - Verify prepend format matches design (header, progress, suggestion/completion, separator)
  - Verify token counts within budget across scenarios
  - **Traces to:** specs.md Section 2.3 (PrependGenerator Component)
  
  **Acceptance Criteria:**
  - [ ] `generate_query_prepend()` function exists with correct signature (tracker, session_id, current_query → str)
  - [ ] Prepend includes header line with 🔍 emojis and tagline
  - [ ] Prepend includes progress line (Queries: X/5 | Unique: Y | Angles: ...)
  - [ ] Prepend includes suggestion when <5 queries (e.g., "💡 Try: 'X best practices'")
  - [ ] Prepend includes completion message when ≥5 queries and ≥4 angles
  - [ ] Token count ≤120 tokens maximum across all scenarios (1, 3, 5+ queries)
  - [ ] Average token count ~85 tokens across 100 sample prepends
  - [ ] Prepend format exactly matches specs.md Section 2.3 example output
  - [ ] Topic extraction works on 10 sample queries (removes common words like "what", "how")
  - [ ] Function latency ≤10ms average (100 sample runs)
  - [ ] Function has complete docstring (Args, Returns, Examples)
  - [ ] Module passes `mypy --strict` with zero errors
  - [ ] Module passes linter with zero errors

- [x] **Task 1.4**: Implement Session ID Extractor Module (S - 0.5-1 hour)
  - Create `mcp_server/core/session_id_extractor.py`
  - Implement `extract_session_id_from_context()` with fallback chain (MCP context → PID → "default")
  - Implement `hash_session_id(raw_id)` using SHA-256 truncated to 16 chars
  - Verify deterministic hashing (same input → same hash)
  - Verify hash collision resistance (different inputs → different hashes)
  - Verify latency ≤1ms
  - **Traces to:** specs.md Section 2.4 (SessionExtractor Component)
  
  **Acceptance Criteria:**
  - [ ] `extract_session_id_from_context()` function exists with correct signature (→ str)
  - [ ] Fallback chain implemented: tries MCP context, then PID, then "default"
  - [ ] Function never returns None or empty string (always valid session ID)
  - [ ] `hash_session_id()` function exists with correct signature (str → str)
  - [ ] Hashed session IDs are exactly 16 characters (hex)
  - [ ] Hashing is deterministic: same input produces same hash (tested with 10 samples)
  - [ ] Hash collision test: 1,000 different inputs produce 1,000 unique hashes
  - [ ] Latency ≤1ms for both functions (100 sample runs)
  - [ ] Both functions have complete docstrings (Args, Returns, Examples)
  - [ ] Module passes `mypy --strict` with zero errors
  - [ ] Module passes linter with zero errors

---

## Phase 2: Integration

**Objective:** Integrate the gamification system into the existing MCP `search_standards()` tool, ensuring backward compatibility and graceful error handling.

**Estimated Duration:** 2-3 hours

### Phase 2 Tasks

- [x] **Task 2.1**: Integrate Gamification into search_standards() (M - 1.5-2 hours)
  - Open `mcp_server/server/tools/rag_tools.py`
  - Import gamification modules at top of file (`get_tracker`, `generate_query_prepend`, `extract_session_id_from_context`)
  - Locate `search_standards()` function
  - Add session ID extraction after search execution
  - Add query recording to tracker
  - Add prepend generation
  - Add prepend to first result content
  - Preserve original return type and structure
  - Verify backward compatibility (function signature unchanged)
  - Verify prepend appears in first result only
  - **Traces to:** specs.md Section 2.5 (Integration Layer)
  
  **Acceptance Criteria:**
  - [ ] Imports added at top of `rag_tools.py` (no import errors)
  - [ ] `search_standards()` function signature unchanged (same parameters, same return type)
  - [ ] Gamification code added after search execution (not before)
  - [ ] Prepend appears in `formatted_results[0]["content"]` (first result only)
  - [ ] Second and subsequent results unchanged (no prepend)
  - [ ] Manual test: call `search_standards("What is validation?")` returns result with prepend
  - [ ] Manual test: second call shows updated stats (Queries: 2/5)
  - [ ] Return type matches MCP spec (`list[types.TextContent | types.ImageContent | types.EmbeddedResource]`)
  - [ ] No breaking changes to existing `search_standards()` behavior
  - [ ] Integration passes `mypy --strict` with zero errors

- [x] **Task 2.2**: Implement Error Handling and Graceful Degradation (S - 0.5-1 hour)
  - Wrap gamification logic in try-except block
  - On exception: log error with hashed session ID
  - On exception: return unmodified search results (graceful degradation)
  - Add logging for successful gamification (debug level)
  - Verify errors don't break search functionality
  - Verify errors are logged with full traceback
  - Verify session IDs are hashed in error logs
  - **Traces to:** specs.md Section 3.4 (Error Handling), Section 5.5.2 (Error Handling Security)
  
  **Acceptance Criteria:**
  - [ ] Try-except block wraps all gamification code (4 lines: session_id, record_query, prepend, concatenation)
  - [ ] Exception handler logs error with `logger.error()` including `exc_info=True`
  - [ ] Session ID in error logs is hashed (not plain text)
  - [ ] On gamification error, search results returned unmodified
  - [ ] Manual test: simulate error (mock tracker to raise exception) → search still works
  - [ ] Error log includes exception type and traceback
  - [ ] Successful gamification logged at DEBUG level (optional, for monitoring)
  - [ ] No user-visible error messages (errors transparent to AI agent)
  - [ ] Test: force 10 different exception types → all handled gracefully

- [x] **Task 2.3**: Validate Backward Compatibility (S - 0.5 hour)
  - Run existing tests for `search_standards()` (if any)
  - Verify function signature unchanged
  - Verify return type unchanged
  - Verify existing callers work without modification
  - Test with and without gamification enabled
  - Document any integration points or configuration
  - **Traces to:** specs.md Section 3.1 (MCP Tool Interface - Backward Compatibility)
  
  **Acceptance Criteria:**
  - [ ] All existing tests for `search_standards()` still pass (if any exist)
  - [ ] Function signature inspection shows no changes (use `inspect.signature()`)
  - [ ] Return type annotation unchanged in code
  - [ ] Manual test: existing code calling `search_standards()` works without modification
  - [ ] Test: disable gamification (comment out) → search still works identically
  - [ ] No new required parameters added to `search_standards()`
  - [ ] No new exceptions raised (beyond what existed before)
  - [ ] Integration documented in code comments (where gamification code starts/ends)

---

## Phase 3: Testing

**Objective:** Validate all functional requirements, non-functional requirements (performance, memory, token cost), and security controls through comprehensive testing.

**Estimated Duration:** 3-4 hours

### Phase 3 Tasks

- [x] **Task 3.1**: Write Unit Tests for Core Modules (M - 1.5-2 hours)
  - Create `tests/core/test_query_classifier.py`
  - Test `classify_query_angle()` with all 5 angle types (definition, location, practical, best_practice, error_prevention)
  - Test `get_angle_emoji()` for all angles
  - Test `get_angle_suggestion()` with various topics
  - Create `tests/core/test_query_tracker.py`
  - Test `record_query()` (total/unique counting, angle tracking, history management)
  - Test `get_stats()` and `get_uncovered_angles()`
  - Test uniqueness detection (normalized queries)
  - Test query history FIFO (max 10 queries)
  - Create `tests/core/test_prepend_generator.py`
  - Test prepend generation for various scenarios (1, 3, 5+ queries)
  - Test topic extraction
  - Test suggestion selection
  - Test completion message (5+ queries, 4+ angles)
  - Create `tests/core/test_session_id_extractor.py`
  - Test session ID extraction fallback chain
  - Test session ID hashing (determinism, collision resistance)
  - Verify all tests pass with 100% coverage for core modules
  - **Traces to:** specs.md Sections 2.1-2.4 (All Component Interfaces)
  
  **Acceptance Criteria:**
  - [ ] `test_query_classifier.py` exists with ≥8 test functions
  - [ ] All 5 angle types classified correctly (10 sample queries per angle, 50 total)
  - [ ] `get_angle_emoji()` tested for all 5 angles (returns correct emoji)
  - [ ] `get_angle_suggestion()` tested with 5 different topics
  - [ ] `test_query_tracker.py` exists with ≥10 test functions
  - [ ] Test: total_queries increments on every call (including duplicates)
  - [ ] Test: unique_queries only increments for new normalized queries
  - [ ] Test: query history limited to 10 (11th query evicts oldest)
  - [ ] Test: `get_stats()` returns accurate QueryStats
  - [ ] Test: `get_uncovered_angles()` returns correct set
  - [ ] `test_prepend_generator.py` exists with ≥6 test functions
  - [ ] Test: prepend for 1 query (includes suggestion)
  - [ ] Test: prepend for 5+ queries with 4+ angles (includes completion message)
  - [ ] Test: topic extraction removes common words (tested with 10 queries)
  - [ ] `test_session_id_extractor.py` exists with ≥4 test functions
  - [ ] Test: session ID extraction returns non-empty string
  - [ ] Test: hashing is deterministic (same input → same hash, 10 samples)
  - [ ] All tests pass: `pytest tests/core/ -v` (exit code 0)
  - [ ] Code coverage ≥95% for all 4 core modules (`pytest --cov=mcp_server/core --cov-report=term`)

- [x] **Task 3.2**: Write Integration Tests (M - 1-1.5 hours)
  - Create `tests/integration/test_search_standards_gamification.py`
  - Test `search_standards()` with gamification enabled
  - Verify prepend appears in first result
  - Verify prepend format matches specification
  - Test multi-query session (progressive stats)
  - Test graceful degradation (simulate gamification error)
  - Test backward compatibility (existing behavior preserved)
  - Test session isolation (multiple sessions don't interfere)
  - Verify all integration tests pass
  - **Traces to:** specs.md Section 2.5 (Integration Layer), Section 3.4 (Error Handling)
  
  **Acceptance Criteria:**
  - [ ] `test_search_standards_gamification.py` exists with ≥6 test functions
  - [ ] Test: call `search_standards("What is X?")` returns list with ≥1 result
  - [ ] Test: first result contains prepend (starts with "🔍🔍🔍🔍🔍")
  - [ ] Test: prepend format matches specs (header, progress, separator)
  - [ ] Test: progressive stats (1st call: "Queries: 1/5", 2nd call: "Queries: 2/5")
  - [ ] Test: graceful degradation (mock tracker to raise exception → search returns results)
  - [ ] Test: error doesn't propagate to user (no exception raised to caller)
  - [ ] Test: session isolation (2 different session IDs have independent stats)
  - [ ] Test: backward compatibility (function signature unchanged)
  - [ ] All integration tests pass: `pytest tests/integration/ -v` (exit code 0)

- [x] **Task 3.3**: Write Performance Tests (M - 1-1.5 hours)
  - Create `tests/performance/test_gamification_performance.py`
  - Test end-to-end latency (full gamification flow ≤20ms)
  - Test individual component latency (classifier ≤5ms, tracker ≤2ms, prepend ≤10ms)
  - Test memory usage (100 sessions ≤100KB)
  - Test memory under load (1,000 sessions ≤1MB, 10,000 sessions ≤10MB)
  - Test token budget compliance (prepend ≤120 tokens max, ~85 avg)
  - Test search latency impact (baseline vs. gamified, <5% increase)
  - Test sustained load (100 sessions × 10 queries, no degradation)
  - Test burst load (1,000 queries single session, latency stable)
  - Verify all performance SLAs met (NFR-P1 through NFR-P4)
  - **Traces to:** specs.md Section 6 (Performance Design), srd.md NFR-P1 through NFR-P4
  
  **Acceptance Criteria:**
  - [ ] `test_gamification_performance.py` exists with ≥8 test functions
  - [ ] Test: end-to-end latency ≤20ms p95 (100 sample runs with `time.perf_counter()`)
  - [ ] Test: classifier latency ≤5ms p95 (100 sample runs)
  - [ ] Test: tracker `record_query()` latency ≤2ms p95 (100 sample runs)
  - [ ] Test: prepend generator latency ≤10ms p95 (100 sample runs)
  - [ ] Test: memory for 100 sessions ≤100KB (measured with `tracemalloc`)
  - [ ] Test: memory for 1,000 sessions ≤1MB
  - [ ] Test: token count ≤120 max across all scenarios (1, 3, 5, 10 queries)
  - [ ] Test: average token count ~85 tokens (100 sample prepends)
  - [ ] Test: search latency impact <5% (baseline search vs. gamified search)
  - [ ] Test: sustained load (100 sessions × 10 queries, p95 latency stable)
  - [ ] Test: burst load (1,000 queries single session, no latency degradation)
  - [ ] All performance tests pass: `pytest tests/performance/ -v` (exit code 0)
  - [ ] Performance report generated showing all SLAs met

- [x] **Task 3.4**: Write Security Tests (S - 0.5-1 hour)
  - Create `tests/security/test_gamification_security.py`
  - Test session ID hashing (SHA-256, 16 char truncation)
  - Test log privacy (no plain session IDs in logs)
  - Test input validation (empty/None/long queries handled safely)
  - Test query length truncation (>10,000 chars truncated)
  - Test error handling (no implementation details leaked)
  - Verify no SQL injection risk (in-memory dict, no database)
  - Verify no XSS risk (text-only output, no HTML)
  - Verify all security tests pass
  - **Traces to:** specs.md Section 5 (Security Design), srd.md NFR-S1
  
  **Acceptance Criteria:**
  - [ ] `test_gamification_security.py` exists with ≥6 test functions
  - [ ] Test: `hash_session_id()` produces 16-character hex strings
  - [ ] Test: hashing is deterministic (10 samples with same input → same hash)
  - [ ] Test: log inspection shows hashed session IDs only (no plain text)
  - [ ] Test: empty query raises ValueError (not silently ignored)
  - [ ] Test: None query raises ValueError
  - [ ] Test: query >10,000 chars truncated to 10,000 (not rejected)
  - [ ] Test: gamification error logged without leaking implementation details
  - [ ] Test: prepend output is plain text only (no HTML tags)
  - [ ] Manual inspection: no SQL queries in code (in-memory dict only)
  - [ ] All security tests pass: `pytest tests/security/ -v` (exit code 0)

---

## Phase 4: Finalization

**Objective:** Complete documentation, conduct code review, validate against all requirements, and prepare for deployment.

**Estimated Duration:** 1-2 hours

### Phase 4 Tasks

- [x] **Task 4.1**: Code Review and Cleanup (S - 0.5-1 hour)
  - Run type checker (`mypy --strict mcp_server/core/`)
  - Run linter (`ruff check mcp_server/core/`)
  - Fix any type errors or linting issues
  - Review all docstrings (Args, Returns, Examples complete)
  - Ensure 100% type hints coverage
  - Remove any debug print statements or commented code
  - Verify code follows project style guide
  - Run all tests one final time (unit, integration, performance, security)
  - **Traces to:** specs.md Section 3.6 (API Summary - type safety)
  
  **Acceptance Criteria:**
  - [ ] `mypy --strict mcp_server/core/` reports 0 errors
  - [ ] `ruff check mcp_server/core/` reports 0 errors
  - [ ] All 4 core modules have 100% type hints coverage (all functions, all parameters, all return types)
  - [ ] All public functions have complete docstrings (Args, Returns, Examples sections)
  - [ ] No debug print statements remaining in code
  - [ ] No commented-out code blocks remaining
  - [ ] Code formatting consistent across all files
  - [ ] Full test suite passes: `pytest tests/ -v` (exit code 0, all 4 test categories)
  - [ ] Test coverage report generated: `pytest --cov=mcp_server --cov-report=html`
  - [ ] Manual code review checklist completed (naming, logic, error handling)

- [x] **Task 4.2**: Update Documentation (S - 0.5 hour)
  - Update module-level docstrings in all 4 core modules
  - Add usage examples to README or docs (if applicable)
  - Document any configuration options (if any)
  - Update changelog with new feature
  - Document known limitations (if any)
  - Add inline code examples for key functions
  - **Traces to:** General best practices
  
  **Acceptance Criteria:**
  - [ ] All 4 core modules have comprehensive module-level docstrings (purpose, usage, examples)
  - [ ] Usage example added showing how to use query gamification (if user-facing)
  - [ ] Configuration options documented (if any exist, e.g., disable flag)
  - [ ] Changelog updated with new feature entry (date, description, author)
  - [ ] Known limitations documented (e.g., "Session state lost on process restart")
  - [ ] At least 3 inline code examples added to module docstrings
  - [ ] Documentation is accurate (no outdated information)
  - [ ] Documentation follows project style guide

- [x] **Task 4.3**: Final Validation Against Requirements (S - 0.5 hour)
  - Review srd.md and verify all functional requirements (FR-001 through FR-013) are met
  - Verify all non-functional requirements (NFR-P1 through NFR-P4, NFR-R1, NFR-R2, NFR-S1, NFR-M1, NFR-M2, NFR-C1, NFR-C2, NFR-U1, NFR-U2) are met
  - Run full test suite (all phases) and verify 100% pass rate
  - Check coverage report (aim for >90% coverage on new code)
  - Create traceability matrix (requirements → tests)
  - Document any deviations or future improvements
  - Mark specification as "Ready for Deployment"
  - **Traces to:** srd.md (All Requirements), specs.md (All Sections)
  
  **Acceptance Criteria:**
  - [ ] All 13 functional requirements (FR-001 through FR-013) verified and documented as "Met"
  - [ ] All 14 non-functional requirements verified and documented as "Met"
  - [ ] Full test suite passes: `pytest tests/ -v --cov` (100% pass rate)
  - [ ] Code coverage ≥90% on new code (4 core modules + integration in rag_tools.py)
  - [ ] Traceability matrix created mapping each requirement to specific tests
  - [ ] Requirements traceability matrix shows 100% coverage (all requirements tested)
  - [ ] Any deviations from specs documented with rationale
  - [ ] Future improvements documented (if any identified during implementation)
  - [ ] srd.md status updated to "Ready for Deployment" or "Implementation Complete"
  - [ ] Final sign-off checklist completed (all Phase 1-4 tasks checked off)

---

**Total Phases:** 4  
**Total Tasks:** 14 (4 Foundation + 3 Integration + 4 Testing + 3 Finalization)
**Total Estimated Time:** 10-15 hours (1.5-2 days)
**Average Task Size:** Small to Medium (0.5-2.5 hours per task)

---

## Dependencies

### Phase-Level Dependencies

#### Phase 1 → Phase 2
Phase 2 (Integration) depends on Phase 1 (Foundation) being complete.  
**Cannot integrate gamification into `search_standards()` without the 4 core modules** (QueryClassifier, QueryTracker, PrependGenerator, SessionExtractor) being implemented first.

**Blocking deliverables from Phase 1:**
- `query_classifier.py` module (provides `classify_query_angle`, `QueryAngle` type)
- `query_tracker.py` module (provides `get_tracker`, `QueryTracker` class)
- `prepend_generator.py` module (provides `generate_query_prepend`)
- `session_id_extractor.py` module (provides `extract_session_id_from_context`, `hash_session_id`)

**Impact if Phase 1 delayed:** Phase 2 cannot start (hard blocker). Integration code would have nothing to import.

---

#### Phase 2 → Phase 3
Phase 3 (Testing) depends on Phases 1 & 2 being complete.  
**Cannot test functionality that doesn't exist or isn't integrated.**

**Blocking deliverables from Phase 2:**
- Gamification integrated into `search_standards()` in `rag_tools.py`
- Error handling implemented (graceful degradation)
- Backward compatibility verified

**Impact if Phase 2 delayed:** Phase 3 cannot start (hard blocker). Tests would have no integrated system to test.

---

#### Phase 3 → Phase 4
Phase 4 (Finalization) depends on Phase 3 being complete.  
**Cannot finalize and validate without comprehensive testing demonstrating all requirements are met.**

**Blocking deliverables from Phase 3:**
- All unit tests passing (core modules validated)
- All integration tests passing (end-to-end flow validated)
- All performance tests passing (NFRs validated)
- All security tests passing (security controls validated)

**Impact if Phase 3 delayed:** Phase 4 cannot start (hard blocker). Cannot sign off on implementation without test evidence.

---

### Task-Level Dependencies

#### Phase 1: Foundation (Parallel Execution Possible)

**Tasks 1.1, 1.2, 1.3, 1.4 are independent:**
- ✅ **Can be done in parallel** (each implements a separate module)
- No internal dependencies (modules don't import each other)
- Optimal execution: Implement all 4 simultaneously

**Dependency structure:**
```
Phase 1 Start
├── Task 1.1: QueryClassifier     (parallel)
├── Task 1.2: QueryTracker         (parallel)
├── Task 1.3: PrependGenerator     (parallel)
└── Task 1.4: SessionExtractor     (parallel)
     ↓
Phase 1 Complete (all 4 modules exist)
```

---

#### Phase 2: Integration (Sequential with 1 Parallel)

**Task 2.1 → Tasks 2.2 & 2.3:**
- **Task 2.1** (Integrate gamification) must complete first
- **Task 2.2** (Error handling) depends on Task 2.1 (adds error handling around integration code)
- **Task 2.3** (Backward compatibility validation) can run in parallel with Task 2.2

**Dependencies:**
- Task 2.1: Depends on Phase 1 (all 4 modules must exist)
- Task 2.2: Depends on Task 2.1 (wraps integration code in try-except)
- Task 2.3: Depends on Task 2.1 (validates integration doesn't break existing behavior)

**Dependency structure:**
```
Phase 1 Complete
     ↓
Task 2.1: Integrate into search_standards()
     ↓
     ├── Task 2.2: Add error handling         (sequential)
     └── Task 2.3: Validate backward compat   (parallel with 2.2)
          ↓
Phase 2 Complete
```

---

#### Phase 3: Testing (Parallel Execution Possible)

**Tasks 3.1, 3.2, 3.3, 3.4 are independent:**
- ✅ **Can be done in parallel** (each tests a different aspect)
- No internal dependencies (unit, integration, performance, security tests are separate)
- Optimal execution: Write all 4 test suites simultaneously

**Dependencies:**
- All Phase 3 tasks depend on Phase 2 being complete
- No dependencies between Phase 3 tasks

**Dependency structure:**
```
Phase 2 Complete
     ↓
     ├── Task 3.1: Unit Tests            (parallel)
     ├── Task 3.2: Integration Tests     (parallel)
     ├── Task 3.3: Performance Tests     (parallel)
     └── Task 3.4: Security Tests        (parallel)
          ↓
Phase 3 Complete (all tests passing)
```

---

#### Phase 4: Finalization (Sequential Execution)

**Tasks 4.1 → 4.2 → 4.3 (sequential):**
- **Task 4.1** (Code review) should complete first (clean up before documenting)
- **Task 4.2** (Documentation) depends on Task 4.1 (document clean, final code)
- **Task 4.3** (Final validation) depends on Tasks 4.1 & 4.2 (validate complete, documented system)

**Dependencies:**
- Task 4.1: Depends on Phase 3 (all tests must pass before review)
- Task 4.2: Depends on Task 4.1 (document final, reviewed code)
- Task 4.3: Depends on Tasks 4.1 & 4.2 (validate everything is complete)

**Dependency structure:**
```
Phase 3 Complete
     ↓
Task 4.1: Code Review & Cleanup
     ↓
Task 4.2: Update Documentation
     ↓
Task 4.3: Final Validation
     ↓
Project Complete
```

---

### Critical Path Analysis

**Critical path (longest dependency chain):**
```
Phase 1 (any task) → Task 2.1 → Task 2.2 → Phase 3 (any task) → Task 4.1 → Task 4.2 → Task 4.3
```

**Estimated critical path duration:**
- Phase 1: 2.5 hours (longest task: 1.2 @ 2-2.5 hours)
- Task 2.1: 2 hours
- Task 2.2: 1 hour
- Phase 3: 2 hours (longest task: 3.1 or 3.3 @ 1.5-2 hours)
- Task 4.1: 1 hour
- Task 4.2: 0.5 hours
- Task 4.3: 0.5 hours
- **Total: ~9.5-10 hours (minimum time with ideal execution)**

**Parallelization opportunities:**
- Phase 1: 4 tasks in parallel → save 6 hours
- Phase 3: 4 tasks in parallel → save 4 hours
- Phase 2 (Task 2.3 parallel with 2.2): save 0.5 hours

**Best case with full parallelization: ~6-7 hours (with 4 developers)**  
**Realistic single-developer: ~10-15 hours (as estimated)**

---

### Dependency Summary

**Phase Dependencies:** 3 (linear: 1→2→3→4)  
**Task Dependencies:** 6 (2.1→2.2, 2.1→2.3, 4.1→4.2, 4.2→4.3, Phase 1→2.1, Phase 3→4.1)  
**Tasks with no dependencies (within phase):** 8 (all Phase 1 tasks, all Phase 3 tasks)  
**Parallel tasks:** 8 (Phase 1: 4 tasks, Phase 3: 4 tasks)  
**Sequential tasks:** 6 (Phase 2: 3 tasks, Phase 4: 3 tasks)

**No circular dependencies detected.** ✅  
**Execution order validated.** ✅

---

## Phase Validation Gates

### Phase 1 Validation Gate: Foundation Complete

**Before advancing to Phase 2 (Integration), verify:**

- [ ] **All Phase 1 tasks completed**
  - [ ] Task 1.1: QueryClassifier module implemented ✅/❌
  - [ ] Task 1.2: QueryTracker module implemented ✅/❌
  - [ ] Task 1.3: PrependGenerator module implemented ✅/❌
  - [ ] Task 1.4: SessionExtractor module implemented ✅/❌

- [ ] **All Phase 1 acceptance criteria met**
  - [ ] All 4 modules pass `mypy --strict` with 0 errors ✅/❌
  - [ ] All 4 modules pass linter with 0 errors ✅/❌
  - [ ] All functions have complete docstrings ✅/❌
  - [ ] All 4 modules have 100% type hints coverage ✅/❌

- [ ] **Module functionality verified**
  - [ ] Query classification works for all 5 angles (tested manually with 10 sample queries) ✅/❌
  - [ ] Query tracking correctly counts total/unique queries (tested with 5 queries) ✅/❌
  - [ ] Prepend generation produces correctly formatted output (tested with 1, 3, 5 query scenarios) ✅/❌
  - [ ] Session ID extraction and hashing works (tested with 3 different session IDs) ✅/❌

- [ ] **Performance baselines met**
  - [ ] Query classification latency ≤5ms (measured) ✅/❌
  - [ ] Query recording latency ≤2ms (measured) ✅/❌
  - [ ] Prepend generation latency ≤10ms (measured) ✅/❌
  - [ ] Session ID extraction latency ≤1ms (measured) ✅/❌

- [ ] **Module files exist**
  - [ ] `mcp_server/core/query_classifier.py` exists ✅/❌
  - [ ] `mcp_server/core/query_tracker.py` exists ✅/❌
  - [ ] `mcp_server/core/prepend_generator.py` exists ✅/❌
  - [ ] `mcp_server/core/session_id_extractor.py` exists ✅/❌

**Exit Criteria:** All checkboxes checked. All 4 core modules implemented, typed, documented, and manually verified to work correctly.

---

### Phase 2 Validation Gate: Integration Complete

**Before advancing to Phase 3 (Testing), verify:**

- [ ] **All Phase 2 tasks completed**
  - [ ] Task 2.1: Gamification integrated into `search_standards()` ✅/❌
  - [ ] Task 2.2: Error handling and graceful degradation implemented ✅/❌
  - [ ] Task 2.3: Backward compatibility validated ✅/❌

- [ ] **All Phase 2 acceptance criteria met**
  - [ ] `search_standards()` function signature unchanged ✅/❌
  - [ ] Prepend appears in first result only (not in subsequent results) ✅/❌
  - [ ] Try-except block wraps all gamification code ✅/❌
  - [ ] Session IDs in error logs are hashed (not plain text) ✅/❌
  - [ ] Integration passes `mypy --strict` with 0 errors ✅/❌

- [ ] **Integration functionality verified**
  - [ ] Manual test: Call `search_standards("What is X?")` returns result with prepend ✅/❌
  - [ ] Manual test: Second call shows updated stats (Queries: 2/5) ✅/❌
  - [ ] Manual test: Simulate gamification error → search still works ✅/❌
  - [ ] Manual test: Disable gamification → search works identically ✅/❌

- [ ] **Error handling verified**
  - [ ] Gamification errors logged with full traceback ✅/❌
  - [ ] Gamification errors don't break search (returns unmodified results) ✅/❌
  - [ ] No user-visible error messages (errors transparent to AI agent) ✅/❌

- [ ] **Integration file modified**
  - [ ] `mcp_server/server/tools/rag_tools.py` modified with gamification code ✅/❌
  - [ ] Imports added at top of file (no import errors) ✅/❌

**Exit Criteria:** All checkboxes checked. Gamification fully integrated into `search_standards()`, error handling robust, backward compatibility maintained.

---

### Phase 3 Validation Gate: Testing Complete

**Before advancing to Phase 4 (Finalization), verify:**

- [ ] **All Phase 3 tasks completed**
  - [ ] Task 3.1: Unit tests for all core modules written ✅/❌
  - [ ] Task 3.2: Integration tests written ✅/❌
  - [ ] Task 3.3: Performance tests written ✅/❌
  - [ ] Task 3.4: Security tests written ✅/❌

- [ ] **All Phase 3 acceptance criteria met**
  - [ ] All unit tests pass: `pytest tests/core/ -v` (exit code 0) ✅/❌
  - [ ] All integration tests pass: `pytest tests/integration/ -v` (exit code 0) ✅/❌
  - [ ] All performance tests pass: `pytest tests/performance/ -v` (exit code 0) ✅/❌
  - [ ] All security tests pass: `pytest tests/security/ -v` (exit code 0) ✅/❌
  - [ ] Code coverage ≥95% for all 4 core modules ✅/❌

- [ ] **Test coverage verified**
  - [ ] ≥8 unit test functions in `test_query_classifier.py` ✅/❌
  - [ ] ≥10 unit test functions in `test_query_tracker.py` ✅/❌
  - [ ] ≥6 unit test functions in `test_prepend_generator.py` ✅/❌
  - [ ] ≥4 unit test functions in `test_session_id_extractor.py` ✅/❌
  - [ ] ≥6 integration test functions in `test_search_standards_gamification.py` ✅/❌
  - [ ] ≥8 performance test functions in `test_gamification_performance.py` ✅/❌
  - [ ] ≥6 security test functions in `test_gamification_security.py` ✅/❌

- [ ] **Performance SLAs met**
  - [ ] End-to-end latency ≤20ms p95 (measured) ✅/❌
  - [ ] Classifier latency ≤5ms p95 (measured) ✅/❌
  - [ ] Tracker latency ≤2ms p95 (measured) ✅/❌
  - [ ] Prepend generator latency ≤10ms p95 (measured) ✅/❌
  - [ ] Memory: 100 sessions ≤100KB (measured) ✅/❌
  - [ ] Token count ≤120 max, ~85 avg (measured) ✅/❌
  - [ ] Search latency impact <5% (measured) ✅/❌

- [ ] **Security controls validated**
  - [ ] Session ID hashing produces 16-char hex strings (tested) ✅/❌
  - [ ] Log inspection shows no plain session IDs (tested) ✅/❌
  - [ ] Empty/None queries raise ValueError (tested) ✅/❌
  - [ ] Query >10,000 chars truncated (tested) ✅/❌
  - [ ] Prepend output is plain text only (no HTML tags) ✅/❌

- [ ] **Test files exist**
  - [ ] `tests/core/test_query_classifier.py` exists ✅/❌
  - [ ] `tests/core/test_query_tracker.py` exists ✅/❌
  - [ ] `tests/core/test_prepend_generator.py` exists ✅/❌
  - [ ] `tests/core/test_session_id_extractor.py` exists ✅/❌
  - [ ] `tests/integration/test_search_standards_gamification.py` exists ✅/❌
  - [ ] `tests/performance/test_gamification_performance.py` exists ✅/❌
  - [ ] `tests/security/test_gamification_security.py` exists ✅/❌

**Exit Criteria:** All checkboxes checked. Comprehensive test suite covering unit, integration, performance, and security. All tests passing. All SLAs met.

---

### Phase 4 Validation Gate: Project Complete

**Before marking project as "Ready for Deployment", verify:**

- [ ] **All Phase 4 tasks completed**
  - [ ] Task 4.1: Code review and cleanup completed ✅/❌
  - [ ] Task 4.2: Documentation updated ✅/❌
  - [ ] Task 4.3: Final validation against requirements completed ✅/❌

- [ ] **All Phase 4 acceptance criteria met**
  - [ ] `mypy --strict mcp_server/core/` reports 0 errors ✅/❌
  - [ ] `ruff check mcp_server/core/` reports 0 errors ✅/❌
  - [ ] No debug print statements remaining ✅/❌
  - [ ] No commented-out code blocks remaining ✅/❌
  - [ ] All module-level docstrings complete ✅/❌
  - [ ] Changelog updated with new feature ✅/❌

- [ ] **Requirements validation**
  - [ ] All 13 functional requirements (FR-001 through FR-013) verified as "Met" ✅/❌
  - [ ] All 14 non-functional requirements verified as "Met" ✅/❌
  - [ ] Traceability matrix created (requirements → tests) ✅/❌
  - [ ] Requirements coverage 100% (all requirements tested) ✅/❌

- [ ] **Full system validation**
  - [ ] Full test suite passes: `pytest tests/ -v --cov` (100% pass rate) ✅/❌
  - [ ] Code coverage ≥90% on new code ✅/❌
  - [ ] No known bugs or issues ✅/❌
  - [ ] All deviations from specs documented ✅/❌

- [ ] **Documentation complete**
  - [ ] All 4 core modules have comprehensive module-level docstrings ✅/❌
  - [ ] All functions have complete docstrings (Args, Returns, Examples) ✅/❌
  - [ ] Known limitations documented ✅/❌
  - [ ] Future improvements documented (if any) ✅/❌

- [ ] **Final sign-off**
  - [ ] srd.md status updated to "Ready for Deployment" ✅/❌
  - [ ] All Phase 1 tasks checked off ✅/❌
  - [ ] All Phase 2 tasks checked off ✅/❌
  - [ ] All Phase 3 tasks checked off ✅/❌
  - [ ] All Phase 4 tasks checked off ✅/❌

**Exit Criteria:** All checkboxes checked. Implementation complete, tested, documented, and validated. Ready for deployment.

---

## Acceptance Criteria Summary

### Phase 1: Foundation
**Success Criteria:** All 4 core modules implemented, typed, documented, and manually verified to work.  
**Quality Gate:** mypy + linter pass, manual functionality tests pass, latency targets met.

### Phase 2: Integration
**Success Criteria:** Gamification integrated into `search_standards()`, error handling robust, backward compatibility maintained.  
**Quality Gate:** Manual integration tests pass, error handling tested, no breaking changes.

### Phase 3: Testing
**Success Criteria:** Comprehensive test suite (unit, integration, performance, security) with 100% pass rate and ≥90% coverage.  
**Quality Gate:** All tests pass, all SLAs met, all security controls validated.

### Phase 4: Finalization
**Success Criteria:** Code reviewed, documented, and validated against all requirements. Ready for deployment.  
**Quality Gate:** No linting errors, requirements traceability complete, all documentation updated.

---

## Project Completion

**Before marking project as complete:**

- [ ] All 4 phases completed ✅/❌
- [ ] All 14 tasks completed ✅/❌
- [ ] All phase validation gates passed ✅/❌
- [ ] All 13 functional requirements (FR-001 through FR-013) met ✅/❌
- [ ] All 14 non-functional requirements met ✅/❌
- [ ] Full test suite passing (unit, integration, performance, security) ✅/❌
- [ ] Code coverage ≥90% on new code ✅/❌
- [ ] Zero linting errors ✅/❌
- [ ] Zero type errors ✅/❌
- [ ] All documentation complete ✅/❌
- [ ] Traceability matrix shows 100% requirements coverage ✅/❌
- [ ] Ready for deployment sign-off obtained ✅/❌

**Total Validation Checkpoints:** 100+ (distributed across 4 phase gates)  
**All gates binary:** Each checkbox is a clear yes/no check  
**Gate enforcement:** Cannot proceed to next phase without completing previous gate

---

## Implementation Readiness

**The query gamification system will be considered ready for deployment when:**

1. All 14 tasks have been completed
2. All 4 phase validation gates have passed
3. All 27 functional and non-functional requirements have been validated
4. The full test suite (50+ tests) passes with ≥90% coverage
5. Code quality tools report zero errors
6. Documentation is complete and accurate
7. Final sign-off has been obtained

**Estimated total effort:** 10-15 hours (1.5-2 days) for a single developer  
**Estimated with parallelization:** 6-7 hours (1 day) with 4 developers

