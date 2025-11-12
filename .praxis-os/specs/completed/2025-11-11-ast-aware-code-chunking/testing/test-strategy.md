# Testing Strategy

**Project:** AST-Aware Code Chunking with Import Penalty  
**Date:** 2025-11-11  
**Purpose:** Comprehensive testing approach for all implementation phases

---

## 1. Testing Philosophy

**Core Principles:**
1. **Test-Driven Development**: Write tests before/during implementation
2. **Continuous Validation**: Run tests after every significant change
3. **Multi-Level Coverage**: Unit → Integration → End-to-End → Human Evaluation
4. **Real-World Validation**: Use actual python-sdk failure case as primary test
5. **Performance Baselines**: Compare AST vs line-based (side-by-side)

---

## 2. Test Levels

### 2.1 Unit Tests

**Scope:** Individual functions and methods

**Phase 2 Tasks (Task 2.8):**
- `UniversalASTChunker` methods:
  - `chunk_file()`: Parse and chunk at boundaries
  - `_chunk_imports()`: Group imports into single chunk
  - `_chunk_definition()`: Extract function/class as complete unit
  - `_calculate_import_ratio()`: Calculate import percentage
  - `_calculate_penalty()`: Determine penalty multiplier
- Edge cases:
  - Empty files
  - Files with only imports
  - Files with only code (no imports)
  - Large functions (>600 tokens)
  - Nested functions/classes

**Coverage Target:** >85% for `ast_chunker.py`

**Test File:** `tests/test_ast_chunker.py`

**Execution:** `pytest tests/test_ast_chunker.py -v --cov=ouroboros/subsystems/rag/code/ast_chunker`

---

### 2.2 Integration Tests

**Scope:** Component interactions

**Phase 3 Tasks (Task 3.5):**
- AST chunking end-to-end:
  - Build index with `chunking_strategy="ast"`
  - Verify chunks have `chunk_type` metadata
  - Query index, verify results include AST chunks
- Line-based fallback:
  - Set `chunking_strategy="line"`
  - Verify fallback works
  - Verify behavior equivalent to baseline
- Import penalty application:
  - Create test with import file and implementation file
  - Query for implementation
  - Verify implementation ranks #1-2, imports #5+
- Graceful degradation:
  - Index corrupted file (parse error)
  - Verify fallback to line-based
  - Verify index build completes

**Test Files:**
- `tests/test_semantic_index_ast_integration.py`
- `tests/test_code_index_partial_degradation.py` (existing, extend for AST)

**Execution:** `pytest tests/test_semantic_index_ast_integration.py -v`

---

### 2.3 End-to-End (E2E) Tests

**Scope:** Full workflow validation

**Phase 4 Tasks (Task 4.1-4.3):**
- **Task 4.1**: Index rebuild
  - Delete index, restart server
  - Verify rebuild with AST chunking
  - Measure rebuild time
- **Task 4.2**: Comparison test suite
  - Build 2 indexes (AST vs line-based)
  - Run 20 test queries
  - Compare rankings (imports vs implementations)
- **Task 4.3**: python-sdk query validation (PRIMARY)
  - Run exact query from problem statement
  - Verify `api/events.py` ranks #1-2
  - Verify `api/__init__.py` ranks #5+

**Test Script:** `scripts/validate_ast_chunking.py`

**Execution:** `python scripts/validate_ast_chunking.py --run-all`

---

### 2.4 Performance Tests

**Scope:** Latency, throughput, scalability

**Phase 4 Tasks (Task 4.4):**
- Index build time:
  - Measure AST vs line-based (100K LOC)
  - Target: <10 minutes
- Query latency:
  - Execute 100 queries
  - Measure p50, p95, p99
  - Target: p95 <200ms
- Import penalty overhead:
  - Profile search ranking stage
  - Target: <1ms overhead

**Tools:**
- Prometheus metrics (query latency)
- Python profiler (`cProfile`)
- Custom timing scripts

**Test Script:** `scripts/profile_ast_chunking.py`

**Execution:** `python scripts/profile_ast_chunking.py --queries=100`

---

### 2.5 Human Evaluation (Relevance Testing)

**Scope:** Search quality metrics

**Phase 4 Tasks (Task 4.5):**
- Select 100 diverse queries
- Execute queries, capture top-5 results
- Human judges rate results (relevant/irrelevant)
- Calculate metrics:
  - **Relevance@5**: % queries with ≥1 relevant in top-5 (target >90%)
  - **False Positive Rate**: % irrelevant in top-5 (target <15%)

**Process:**
1. Query selection (cover functions, classes, generic code)
2. Result capture (save JSON for reproducibility)
3. Blind evaluation (judges don't know AST vs line-based)
4. Metric calculation

**Test Script:** `scripts/evaluate_relevance.py`

**Execution:** `python scripts/evaluate_relevance.py --queries=relevance_test_set.json`

---

## 3. Test Data

### 3.1 Test Fixtures

**Phase 2 Task 2.8:**
- `tests/fixtures/python/`:
  - `simple_functions.py` (3 functions, 200 tokens each)
  - `with_imports.py` (10 imports, 3 functions)
  - `large_function.py` (1 function, 800 tokens)
  - `nested_classes.py` (class with nested methods)
- `tests/fixtures/typescript/`:
  - `arrow_functions.ts`
  - `class_definitions.ts`
  - `import_statements.ts`
- `tests/fixtures/go/`:
  - `func_declarations.go`
  - `struct_definitions.go`
  - `import_packages.go`

### 3.2 Real-World Test Cases

**python-sdk Failure Case:**
- File: `honeyhiveai/python-sdk/api/__init__.py` (imports only)
- File: `honeyhiveai/python-sdk/api/events.py` (implementation)
- Query: "EventsAPI list_events multiple filters array implementation"
- **Expected**: `events.py` #1-2, `__init__.py` #5+

---

## 4. Test Execution

### 4.1 Continuous Integration

**Pre-Commit:**
- Unit tests (fast, <30s)
- Linter (mypy, ruff)

**CI Pipeline:**
- Unit tests (all)
- Integration tests
- E2E tests (subset)
- Performance tests (if changed)

**Release Validation:**
- Full test suite
- Human evaluation (100 queries)
- Performance profiling

---

### 4.2 Test Phases Aligned with Implementation

| Implementation Phase | Test Phase | Tests Executed |
|---------------------|------------|----------------|
| Phase 0: Config Extraction | Unit | Config validation |
| Phase 1: Refactor AST | Unit, Regression | ast.py refactor, existing tests |
| Phase 2: Universal Chunker | Unit | ast_chunker.py (30+ tests) |
| Phase 3: Integration | Integration | End-to-end AST chunking |
| Phase 4: Validation | E2E, Performance, Relevance | Full suite |
| Phase 5: Documentation | Manual | Docs review |

---

## 5. Acceptance Criteria

### 5.1 Phase Gate Criteria

**Phase 2 Gate:**
- [ ] 30+ unit tests passing
- [ ] >85% code coverage for `ast_chunker.py`
- [ ] All test fixtures created

**Phase 3 Gate:**
- [ ] 5+ integration tests passing
- [ ] Import penalty applied in search
- [ ] Test fixture query ranks correctly

**Phase 4 Gate (CRITICAL):**
- [ ] python-sdk query validation **PASSED**
- [ ] p95 query latency <200ms
- [ ] Relevance@5 >90%
- [ ] False Positive Rate <15%

---

### 5.2 Release Criteria

**Minimum Requirements:**
- [ ] All functional tests pass (10/10)
- [ ] All non-functional tests pass (15/15)
- [ ] PRIMARY test passes (python-sdk query)
- [ ] Performance targets met (latency, build time)
- [ ] Relevance metrics meet targets (Relevance@5 >90%, FPR <15%)
- [ ] Zero critical bugs
- [ ] Documentation complete

---

## 6. Test Tooling

### 6.1 Test Framework

- **pytest**: Unit and integration tests
- **pytest-cov**: Code coverage reporting
- **pytest-benchmark**: Performance benchmarking

### 6.2 Fixtures and Mocking

- **pytest fixtures**: Test data (code files, configs)
- **unittest.mock**: Mock Tree-sitter parser (for error testing)
- **tempfile**: Temporary directories for index builds

### 6.3 Assertions

- **Standard assertions**: `assert`, `assert_equal`
- **Custom matchers**: `assert_chunks_at_boundaries()`, `assert_import_penalty_applied()`
- **Tolerance checks**: Token counts (±20%), latency (<200ms)

---

## 7. Test Maintenance

### 7.1 Test Updates

**When to Update Tests:**
- Config schema changes → Update config validation tests
- New language added → Add language-specific fixtures
- New chunking logic → Add unit tests for new methods
- Performance regression → Add performance test

### 7.2 Test Documentation

- **Docstrings**: Every test function documents purpose and expected behavior
- **Comments**: Complex assertions explained
- **README**: `tests/README.md` with execution instructions

---

## 8. Risk Mitigation

### 8.1 High-Risk Areas

**Tree-sitter Parsing:**
- **Risk**: Parse errors for edge cases
- **Mitigation**: Comprehensive fixtures, graceful fallback, extensive logging

**Import Penalty Calculation:**
- **Risk**: Penalty too aggressive or ineffective
- **Mitigation**: Human evaluation, comparison tests, tunable config

**Performance Regression:**
- **Risk**: AST overhead impacts query latency
- **Mitigation**: Performance tests, profiling, baseline comparison

---

## 9. Test Coverage Matrix

| Requirement | Unit Tests | Integration Tests | E2E Tests | Performance Tests | Relevance Tests |
|-------------|-----------|------------------|-----------|-------------------|----------------|
| FR-001 | ✅ | ✅ | ✅ | - | - |
| FR-002 | ✅ | ✅ | ✅ | - | ✅ |
| FR-003 | ✅ | ✅ | ✅ | ✅ | - |
| FR-004 | ✅ | ✅ | - | - | - |
| FR-005 | ✅ | ✅ | ✅ | - | - |
| FR-006 | - | - | ✅ | ✅ | - |
| FR-007 | - | - | ✅ | ✅ | - |
| FR-008 | - | ✅ | ✅ | - | - |
| FR-009 | ✅ | ✅ | - | - | - |
| FR-010 | ✅ | ✅ | ✅ | - | ✅ |
| NFR-P1 | - | - | - | ✅ | - |
| NFR-P2 | - | - | ✅ | ✅ | - |
| NFR-P3 | - | - | - | ✅ | - |
| NFR-U1 | - | ✅ | ✅ | - | ✅ |

---

## 10. Success Metrics

**Test Execution:**
- All tests passing: 100%
- Code coverage: >85%
- Test execution time: <10 minutes (CI)

**Quality Metrics:**
- Relevance@5: >90%
- False Positive Rate: <15%
- python-sdk query: PASS (implementation #1-2)

**Performance Metrics:**
- p95 query latency: <200ms
- Index rebuild: <10 minutes (100K LOC)
- Import penalty overhead: <1ms

---


