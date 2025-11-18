# Testing Strategy
## Code Search Auto-Truncation with Query-Aware Response Sizing

**Date:** 2025-11-16  
**Purpose:** Comprehensive testing approach for auto-truncation feature

---

## Testing Philosophy

**Core Principles:**
1. **Test-Driven Development (TDD):** Write tests before implementation where possible
2. **Fast, Isolated Unit Tests:** Test business logic in isolation with mocked dependencies
3. **Integration Tests for Interactions:** Verify component interactions and end-to-end flows
4. **Performance Validation:** Benchmark critical paths to ensure <10ms overhead
5. **Behavioral Verification:** Track metrics to validate assumptions (80/15/5 distribution)

**Coverage Targets:**
- **Overall:** ≥90% line coverage (NFR-3)
- **Unit Tests:** ≥95% coverage of truncation logic
- **Integration Tests:** 100% of critical paths
- **Edge Cases:** 100% of error conditions

**Quality Gates:**
- All tests must pass before merge
- Coverage must not decrease
- Performance benchmarks must meet targets (<10ms P95)
- No skipped tests without documented reason

---

## Test Pyramid

```
        /\
       /  \  E2E (Integration)
      /____\  - 21 tests (35%)
     /      \  - Component interactions
    /        \  - End-to-end flows
   /__________\ 
  /            \ Unit
 /              \ - 28 tests (47%)
/________________\ - Business logic
                   - Isolated components

     Performance
     - 5 tests (8%)
     - Benchmarks

     Coverage/Meta
     - 1 test (2%)
```

**Total Tests:** 55 (38 functional + 22 non-functional = 60 total)

**Distribution:**
- Unit: 28 tests (47%)
- Integration: 21 tests (35%)
- Performance: 5 tests (8%)
- Coverage: 1 test (2%)
- Observability: 5 tests (8%)

---

## Unit Testing

### Scope

**Components Under Test:**
1. **TruncationController** (`_determine_truncation` method)
   - Query angle detection
   - Angle-to-threshold mapping
   - Override handling
   - Graceful degradation

2. **TruncationProcessor** (`_truncate_code_chunks`, `_find_truncation_point` methods)
   - Smart boundary detection
   - Content truncation
   - Metadata enrichment
   - Inline hint generation

3. **Input Validation**
   - Parameter type checking
   - Value range validation
   - Error message generation

### Coverage Target

**≥95% line coverage** for truncation-related code:
- `.praxis-os/ouroboros/tools/pos_search_project.py` (new methods)
- All new helper functions

### Isolation Strategy

**Mock External Dependencies:**
- `QueryClassifier.classify()` - Mock to return specific angles
- `SemanticIndex.search()` - Mock to return test chunks
- `PrependGenerator` - Mock if needed for testing

**Don't Mock:**
- String operations (core logic)
- Data structures (dicts, lists)
- Helper methods under test

### Test Structure (AAA Pattern)

```python
def test_determine_truncation_conceptual_query():
    # Arrange: Setup test data and mocks
    query = "How does the authentication system work?"
    mock_classifier = Mock()
    mock_classifier.classify.return_value = Mock(primary="conceptual")
    
    # Act: Execute function under test
    result = _determine_truncation(query, truncate=True)
    
    # Assert: Verify expected outcome
    assert result == 100  # Conceptual queries → 100 lines
    mock_classifier.classify.assert_called_once_with(query)
```

### Test Organization

```
tests/unit/
└── test_truncation.py
    ├── TestDetermineTruncation (11 tests)
    │   ├── test_determine_truncation_conceptual_query
    │   ├── test_determine_truncation_location_query
    │   ├── test_determine_truncation_implementation_query
    │   ├── test_determine_truncation_critical_query
    │   ├── test_determine_truncation_troubleshooting_query
    │   ├── test_determine_truncation_unknown_angle
    │   ├── test_determine_truncation_explicit_false
    │   ├── test_determine_truncation_explicit_int
    │   ├── test_determine_truncation_explicit_auto
    │   ├── test_determine_truncation_invalid_type
    │   └── test_determine_truncation_invalid_value
    │
    ├── TestFindTruncationPoint (5 tests)
    │   ├── test_find_truncation_point_at_blank_line
    │   ├── test_find_truncation_point_at_def
    │   ├── test_find_truncation_point_at_class
    │   ├── test_find_truncation_point_no_boundary_fallback
    │   └── test_find_truncation_point_preserves_docstring
    │
    ├── TestTruncateCodeChunks (7 tests)
    │   ├── test_truncate_code_chunks_adds_metadata
    │   ├── test_truncate_code_chunks_inline_hint
    │   ├── test_truncate_code_chunks_no_truncation_metadata
    │   ├── test_truncate_preserves_class_docstring
    │   ├── test_truncate_preserves_init_method
    │   ├── test_truncate_preserves_main_method_signature
    │   └── test_truncate_shows_helper_signatures
    │
    └── TestReliability (5 tests)
        ├── test_classifier_failure_defaults_to_100
        ├── test_no_boundary_uses_target
        ├── test_empty_query_defaults_to_100
        ├── test_invalid_param_raises_error
        └── test_small_chunk_no_truncation
```

**Total Unit Tests:** 28

---

## Integration Testing

### Scope

**Component Interactions:**
1. **SearchCodeHandler ↔ TruncationController ↔ TruncationProcessor**
   - End-to-end search with truncation
   - Query classification → truncation → response

2. **SearchCodeHandler ↔ SemanticIndex**
   - Search execution
   - Result processing

3. **SearchCodeHandler ↔ PrependGenerator**
   - Prepend injection
   - Metadata enrichment

4. **Behavioral Metrics Tracking**
   - Query tracking
   - Token reduction metrics
   - Angle distribution

### Coverage Target

**100% of critical paths:**
- All query angles (conceptual, location, implementation, critical, troubleshooting)
- All override scenarios (True, False, int, "auto")
- Backwards compatibility (no truncate param)
- Other search actions (standards, AST, graph) unchanged

### Test Organization

```
tests/integration/
├── test_search_code.py (13 tests)
│   ├── TestQueryAngles (5 tests)
│   │   ├── test_search_code_conceptual_query_truncated
│   │   ├── test_search_code_location_query_truncated
│   │   ├── test_search_code_implementation_query_full
│   │   ├── test_search_code_critical_query_truncated
│   │   └── test_search_code_troubleshooting_query_full
│   │
│   ├── TestOverrides (4 tests)
│   │   ├── test_truncate_true_auto_detects
│   │   ├── test_truncate_false_full_chunks
│   │   ├── test_truncate_explicit_line_count
│   │   └── test_truncate_auto_string_explicit
│   │
│   ├── TestBackwardsCompatibility (5 tests)
│   │   ├── test_backwards_compatible_no_param
│   │   ├── test_backwards_compatible_response_structure
│   │   ├── test_standards_search_unchanged
│   │   ├── test_ast_search_unchanged
│   │   └── test_graph_search_unchanged
│   │
│   ├── TestMetadata (2 tests)
│   │   ├── test_truncated_result_metadata_complete
│   │   └── test_response_truncation_reason_metadata
│   │
│   └── TestEndToEnd (4 tests)
│       ├── test_e2e_conceptual_query_flow
│       ├── test_e2e_query_refinement_flow
│       ├── test_e2e_mixed_query_session
│       └── test_inline_hint_in_truncated_content
│
└── test_metrics.py (8 tests)
    ├── TestTokenReduction (4 tests)
    │   ├── test_token_reduction_conceptual_queries
    │   ├── test_token_reduction_location_queries
    │   ├── test_token_reduction_implementation_queries
    │   └── test_weighted_average_token_reduction
    │
    └── TestBehavioralMetrics (4 tests)
        ├── test_token_reduction_tracked
        ├── test_query_refinement_rate_tracked
        ├── test_angle_distribution_tracked
        └── test_misclassification_rate_tracked
```

**Total Integration Tests:** 21

### Test Execution Flow

**Integration Test Pattern:**
1. **Setup:** Initialize real components (no mocks for integration)
2. **Execute:** Call `pos_search_project` with real parameters
3. **Verify:** Check response structure, content, and metadata
4. **Cleanup:** Reset state if needed

**Example:**
```python
def test_e2e_conceptual_query_flow():
    # Setup: Real components, real code index
    query = "How does the workflow system work?"
    
    # Execute: Full search with truncation
    response = pos_search_project(
        action="search_code",
        query=query,
        n_results=3
    )
    
    # Verify: Response structure and content
    assert response["status"] == "success"
    assert response["count"] == 3
    
    for result in response["results"]:
        assert result["truncated"] == True
        assert len(result["content"].split("\n")) <= 110  # ~100 lines + buffer
        assert "Use truncate=False" in result["hint"]
    
    # Verify: Metadata
    assert response["metadata"]["truncation_reason"]["angle"] == "conceptual"
    assert response["metadata"]["truncation_reason"]["max_lines"] == 100
```

---

## Mocking Strategy

### What to Mock (Unit Tests)

**External Dependencies:**
1. **QueryClassifier**
   - Mock `classify()` to return specific angles
   - Test graceful degradation when classifier fails

2. **SemanticIndex**
   - Mock `search()` to return test chunks
   - Control chunk size and content for testing

3. **File System I/O** (if applicable)
   - Mock file reads/writes
   - Test error conditions

**Mocking Pattern:**
```python
from unittest.mock import Mock, patch

@patch('pos_search_project.QueryClassifier')
def test_with_mocked_classifier(mock_classifier_class):
    # Setup mock
    mock_classifier = Mock()
    mock_classifier.classify.return_value = Mock(primary="conceptual")
    mock_classifier_class.return_value = mock_classifier
    
    # Test with mocked dependency
    result = _determine_truncation("How does X work?", truncate=True)
    assert result == 100
```

### What NOT to Mock

**Core Logic:**
- String operations (splitting, slicing)
- Data structures (dicts, lists)
- Helper methods under test
- Simple transformations

**Integration Tests:**
- Real components (no mocks)
- Real code index (use test fixtures)
- Real QueryClassifier (test actual classification)

### Test Fixtures

**Reusable Test Data:**
```python
# tests/fixtures/code_chunks.py

SMALL_CHUNK = """
class Example:
    def __init__(self):
        pass
"""  # 50 lines

MEDIUM_CHUNK = """
class LargeClass:
    '''Comprehensive docstring...'''
    
    def __init__(self):
        '''Initialize...'''
        pass
    
    def main_method(self):
        '''Main logic...'''
        # Implementation
        pass
    
    # ... more methods ...
"""  # 500 lines

LARGE_CHUNK = """
# Very large implementation
# 2000+ lines
"""
```

---

## Performance Testing

### Scope

**Benchmarks:**
1. Truncation overhead for small/medium/large chunks
2. P95 latency across all chunk sizes
3. Concurrent truncation (no degradation)
4. Search latency impact (should be <5ms)

### Execution Environment

**Requirements:**
- Clean state (no cached data)
- Isolated environment (no other processes)
- Consistent hardware (same machine for all runs)
- Multiple runs for statistical validity (100+ iterations)

### Test Organization

```
tests/performance/
└── test_truncation_perf.py (5 tests)
    ├── test_truncation_overhead_small_chunks
    ├── test_truncation_overhead_medium_chunks
    ├── test_truncation_overhead_large_chunks
    ├── test_truncation_overhead_p95
    └── test_concurrent_truncation_no_degradation
```

### Performance Assertions

```python
import time
import numpy as np

def test_truncation_overhead_p95():
    chunks = generate_test_chunks(1000)  # Mixed sizes
    overheads = []
    
    for chunk in chunks:
        start = time.perf_counter()
        _truncate_code_chunks([chunk], max_lines=100)
        end = time.perf_counter()
        overheads.append((end - start) * 1000)  # ms
    
    p95 = np.percentile(overheads, 95)
    assert p95 < 10, f"P95 overhead {p95}ms exceeds 10ms target"
```

---

## Coverage Testing

### Measurement

**Tools:**
- `pytest-cov` for coverage tracking
- HTML reports for visualization

**Commands:**
```bash
# Run tests with coverage
pytest --cov=.praxis-os/ouroboros/tools/pos_search_project \
       --cov-report=term \
       --cov-report=html \
       --cov-fail-under=90

# View HTML report
open htmlcov/index.html
```

### Coverage Targets

| Component | Target | Priority |
|-----------|--------|----------|
| `_determine_truncation` | 100% | P0 |
| `_truncate_code_chunks` | 100% | P0 |
| `_find_truncation_point` | 100% | P0 |
| `_handle_search_code` (modified) | 95% | P0 |
| Overall truncation feature | 90% | P0 |

### Coverage Validation

```python
def test_coverage_exceeds_90_percent():
    """Meta-test: Verify coverage target is met"""
    coverage_report = run_coverage_analysis()
    assert coverage_report["line_coverage"] >= 90
    assert coverage_report["branch_coverage"] >= 85
```

---

## Test Execution

### Local Development

**Run All Tests:**
```bash
pytest tests/ -v
```

**Run Unit Tests Only:**
```bash
pytest tests/unit/ -v
```

**Run Integration Tests Only:**
```bash
pytest tests/integration/ -v
```

**Run Performance Tests:**
```bash
pytest tests/performance/ -v --benchmark-only
```

**Run with Coverage:**
```bash
pytest tests/ --cov=.praxis-os/ouroboros/tools/pos_search_project \
       --cov-report=html \
       --cov-fail-under=90
```

**Run Specific Test:**
```bash
pytest tests/unit/test_truncation.py::test_determine_truncation_conceptual_query -v
```

### CI/CD Pipeline

**Automated Test Execution:**
1. **On Every Commit:** Run full test suite
2. **On Pull Request:** Run tests + coverage check
3. **On Merge to Main:** Run tests + performance benchmarks

**Quality Gates:**
- All tests must pass ✅
- Coverage ≥90% ✅
- Performance benchmarks meet targets ✅
- No new linter errors ✅

**Pipeline Configuration:**
```yaml
# .github/workflows/test.yml (example)
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: pytest tests/ --cov --cov-fail-under=90
      - name: Run performance benchmarks
        run: pytest tests/performance/ --benchmark-only
```

---

## Test Data Management

### Test Fixtures

**Location:** `tests/fixtures/`

**Contents:**
- `code_chunks.py` - Sample code chunks (small, medium, large)
- `queries.py` - Test queries for each angle
- `expected_results.py` - Expected truncation outcomes

**Usage:**
```python
from tests.fixtures.code_chunks import MEDIUM_CHUNK

def test_truncate_medium_chunk():
    result = _truncate_code_chunks([MEDIUM_CHUNK], max_lines=100)
    assert result[0]["truncated"] == True
```

### Test Database (if applicable)

**For Integration Tests:**
- Use real code index with test data
- Seed with known code samples
- Reset state between tests

---

## Debugging Failed Tests

### Verbose Output

```bash
pytest tests/ -vv --tb=long
```

### Run Single Test with Debugging

```bash
pytest tests/unit/test_truncation.py::test_name -vv -s --pdb
```

### Coverage Report for Failed Tests

```bash
pytest tests/ --cov --cov-report=term-missing
```

---

## Test Maintenance

### When to Update Tests

1. **New Feature:** Add tests before implementation (TDD)
2. **Bug Fix:** Add regression test before fixing bug
3. **Refactor:** Update tests to match new structure
4. **Performance Change:** Update benchmark targets

### Test Review Checklist

- [ ] Test name clearly describes what is tested
- [ ] Test follows AAA pattern (Arrange, Act, Assert)
- [ ] Test is isolated (no dependencies on other tests)
- [ ] Test uses appropriate mocks (not over-mocked)
- [ ] Test has clear assertions (not just "no error")
- [ ] Test covers edge cases (not just happy path)
- [ ] Test is fast (<1s for unit tests)

---

## Summary

**Testing Strategy Overview:**

| Category | Tests | Coverage | Priority |
|----------|-------|----------|----------|
| Unit | 28 | 95% | P0 |
| Integration | 21 | 100% critical paths | P0 |
| Performance | 5 | <10ms P95 | P0 |
| Coverage | 1 | 90% overall | P0 |
| Observability | 5 | Metrics tracked | P1 |
| **Total** | **60** | **90%+** | - |

**Key Success Metrics:**
- ✅ All 60 tests pass
- ✅ Coverage ≥90%
- ✅ Performance <10ms P95
- ✅ No regressions in existing functionality
- ✅ Behavioral metrics validate assumptions (80/15/5)

**Estimated Test Execution Time:**
- Unit: 2-3 seconds
- Integration: 5-10 seconds
- Performance: 30-60 seconds
- **Total: ~1 minute**

---

