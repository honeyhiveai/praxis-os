# Non-Functional Tests Plan
## Code Search Auto-Truncation with Query-Aware Response Sizing

**Date:** 2025-11-16  
**Purpose:** Verification tests for performance, reliability, maintainability, observability, and usability

**NFR Categories:**
- **Performance:** Latency, throughput, resource usage
- **Reliability:** Fault tolerance, graceful degradation, error handling
- **Maintainability:** Code quality, test coverage, documentation
- **Observability:** Metrics tracking, behavioral analysis
- **Usability:** Self-documenting, self-teaching, clear guidance

---

## NFR-1: Performance

**Requirement:** Truncation overhead SHALL be <10ms per query

**Metric Target:** 95th percentile <10ms

**Measurement Criteria:**
- Post-processing only (no impact on search latency)
- Simple string operations (line splitting, slicing)
- O(n) complexity where n=lines in chunk
- No LLM inference required
- Benchmark: 95th percentile <10ms

### Test Specifications

#### Test 1.1: Small Chunk Truncation Overhead

**Test Function:** `test_truncation_overhead_small_chunks()`

**Setup:**
- 100 code chunks, each 100 lines
- Truncation target: 50 lines
- Measure truncation time only (exclude search time)

**Measurement:**
```python
import time

start = time.perf_counter()
result = _truncate_code_chunks(chunks, max_lines=50)
end = time.perf_counter()
overhead_ms = (end - start) * 1000
```

**Pass Criteria:**
- Mean overhead: <5ms
- P95 overhead: <10ms
- P99 overhead: <15ms

**Verifies:** Small chunks process efficiently

---

#### Test 1.2: Medium Chunk Truncation Overhead

**Test Function:** `test_truncation_overhead_medium_chunks()`

**Setup:**
- 100 code chunks, each 500 lines
- Truncation target: 100 lines
- Measure truncation time only

**Measurement:**
```python
overhead_ms = measure_truncation_time(chunks, max_lines=100)
```

**Pass Criteria:**
- Mean overhead: <8ms
- P95 overhead: <10ms
- P99 overhead: <15ms

**Verifies:** Medium chunks (typical case) meet performance target

---

#### Test 1.3: Large Chunk Truncation Overhead

**Test Function:** `test_truncation_overhead_large_chunks()`

**Setup:**
- 100 code chunks, each 2000 lines
- Truncation target: 150 lines
- Measure truncation time only

**Measurement:**
```python
overhead_ms = measure_truncation_time(chunks, max_lines=150)
```

**Pass Criteria:**
- Mean overhead: <10ms
- P95 overhead: <15ms
- P99 overhead: <20ms

**Verifies:** Large chunks still meet reasonable performance

---

#### Test 1.4: P95 Latency Across All Chunk Sizes

**Test Function:** `test_truncation_overhead_p95()`

**Setup:**
- 1000 code chunks with mixed sizes (100-2000 lines)
- Truncation targets: 50-150 lines (based on angle)
- Measure truncation time for each

**Measurement:**
```python
overheads = [measure_truncation_time([chunk], max_lines) 
             for chunk in chunks]
p95 = numpy.percentile(overheads, 95)
```

**Pass Criteria:**
- P95 overhead: <10ms ✅

**Verifies:** Meets primary performance target (NFR-1)

---

#### Test 1.5: Concurrent Truncation No Degradation

**Test Function:** `test_concurrent_truncation_no_degradation()`

**Setup:**
- 10 concurrent search requests
- Each returns 3 results (30 truncations total)
- Measure per-request latency

**Measurement:**
```python
import concurrent.futures

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(search_and_truncate, query) 
               for query in queries]
    latencies = [f.result()["latency_ms"] for f in futures]
p95 = numpy.percentile(latencies, 95)
```

**Pass Criteria:**
- P95 latency: <10ms (no degradation under concurrency)

**Verifies:** Stateless design supports concurrent requests

---

#### Test 1.6: No Search Latency Impact

**Test Function:** `test_no_search_latency_impact()`

**Setup:**
- Measure search latency with truncation enabled
- Measure search latency with truncation disabled
- Compare difference

**Measurement:**
```python
latency_with_truncation = measure_search_time(truncate=True)
latency_without_truncation = measure_search_time(truncate=False)
difference = latency_with_truncation - latency_without_truncation
```

**Pass Criteria:**
- Difference: <5ms (truncation is post-processing only)

**Verifies:** Truncation doesn't impact search performance

---

## NFR-2: Reliability

**Requirement:** System SHALL handle edge cases gracefully

**Measurement Criteria:**
- Classifier failure → Default to 100 lines
- No natural boundary → Use target line
- Empty query → Default to 100 lines
- Invalid truncate parameter → Error with guidance
- Chunk smaller than threshold → No truncation

### Test Specifications

#### Test 2.1: Classifier Unavailable Defaults to 100 Lines

**Test Function:** `test_classifier_failure_defaults_to_100()`

**Setup:**
- Mock QueryClassifier to raise exception
- Query: "How does X work?"

**Action:**
```python
with mock.patch.object(classifier, 'classify', side_effect=Exception("Classifier down")):
    response = pos_search_project(action="search_code", query="How does X work?")
```

**Expected:**
- Response status: "success" (no error)
- Result[0]["truncated"]: True
- Result[0]["content"]: ~100 lines (safe default)
- Warning logged: "QueryClassifier failed, defaulting to 100 lines"

**Pass Criteria:**
- System continues to function ✅
- Default truncation applied ✅
- No user-facing error ✅

**Verifies:** Graceful degradation when classifier fails

---

#### Test 2.2: No Boundary Found Uses Target Line

**Test Function:** `test_no_boundary_uses_target()`

**Setup:**
- Code chunk: Single 200-line method (no natural boundaries)
- Truncation target: 100 lines

**Action:**
```python
result = _truncate_code_chunks([chunk], max_lines=100)
```

**Expected:**
- Truncation point: 100 (target, fallback)
- Content: 100 lines
- Warning logged: "No natural boundary found within 20 lines, using target"

**Pass Criteria:**
- Truncation still applied ✅
- Fallback behavior correct ✅

**Verifies:** Handles edge case of no natural boundaries

---

#### Test 2.3: Empty Query Defaults to 100 Lines

**Test Function:** `test_empty_query_defaults_to_100()`

**Setup:**
- Query: "" (empty string)

**Action:**
```python
response = pos_search_project(action="search_code", query="")
```

**Expected:**
- Response status: "success" (or "error" if query validation fails)
- If success: Truncation defaults to 100 lines

**Pass Criteria:**
- No crash ✅
- Reasonable default behavior ✅

**Verifies:** Handles empty/malformed queries

---

#### Test 2.4: Invalid truncate Parameter Raises Error

**Test Function:** `test_invalid_param_raises_error()`

**Setup:**
- Query: "How does X work?"
- truncate: {"invalid": "dict"} (invalid type)

**Action:**
```python
response = pos_search_project(
    action="search_code", 
    query="How does X work?",
    truncate={"invalid": "dict"}
)
```

**Expected:**
- Response status: "error"
- Error code: "INVALID_PARAMETER"
- Error message: "truncate must be True, False, int, or 'auto'"
- Error includes remediation guidance

**Pass Criteria:**
- Clear error message ✅
- Actionable guidance ✅
- No crash ✅

**Verifies:** Input validation with helpful errors

---

#### Test 2.5: Chunk Smaller Than Threshold No Truncation

**Test Function:** `test_small_chunk_no_truncation()`

**Setup:**
- Code chunk: 50 lines
- Truncation target: 100 lines

**Action:**
```python
result = _truncate_code_chunks([chunk], max_lines=100)
```

**Expected:**
- Result[0]["truncated"]: False
- Result[0]["content"]: 50 lines (unchanged)
- No truncation applied

**Pass Criteria:**
- Small chunks unchanged ✅
- No unnecessary truncation ✅

**Verifies:** Handles chunks smaller than threshold

---

#### Test 2.6: Truncation Failure Returns Full Chunks

**Test Function:** `test_truncation_failure_returns_full_chunks()`

**Setup:**
- Mock _truncate_code_chunks to raise exception
- Query: "How does X work?"

**Action:**
```python
with mock.patch('_truncate_code_chunks', side_effect=Exception("Truncation error")):
    response = pos_search_project(action="search_code", query="How does X work?")
```

**Expected:**
- Response status: "success" (no error)
- Results: Full chunks (no truncation)
- Warning logged: "Truncation failed, returning full chunks"
- Response metadata: `truncation_warning = "Truncation failed"`

**Pass Criteria:**
- System continues to function ✅
- Full content returned as fallback ✅
- User informed via metadata ✅

**Verifies:** Graceful degradation on truncation failure

---

## NFR-3: Maintainability

**Requirement:** Code SHALL be well-tested and documented

**Measurement Criteria:**
- Test coverage >90%
- Unit tests for all truncation logic
- Integration tests for each query angle
- Edge case tests for error conditions
- Performance benchmarks
- Comprehensive docstrings with examples

### Test Specifications

#### Test 3.1: Test Coverage Exceeds 90%

**Test Function:** `test_coverage_exceeds_90_percent()`

**Setup:**
- Run full test suite with coverage tracking
- Measure coverage for truncation-related code

**Measurement:**
```bash
pytest --cov=.praxis-os/ouroboros/tools/pos_search_project \
       --cov-report=term \
       --cov-report=html \
       --cov-fail-under=90
```

**Pass Criteria:**
- Line coverage: >90% ✅
- Branch coverage: >85% ✅
- Coverage report generated ✅

**Verifies:** High test coverage for reliability

---

#### Test 3.2: All Public Methods Have Docstrings

**Test Function:** `test_all_public_methods_documented()`

**Setup:**
- Inspect pos_search_project.py
- Check all public methods for docstrings

**Measurement:**
```python
import inspect
import ast

# Parse file, find all public methods
# Verify each has docstring with examples
undocumented = find_undocumented_methods("pos_search_project.py")
```

**Pass Criteria:**
- All public methods have docstrings ✅
- Docstrings include examples ✅
- Docstrings explain parameters ✅

**Verifies:** Code is well-documented

---

#### Test 3.3: All Test Functions Pass

**Test Function:** `test_suite_execution()`

**Setup:**
- Run full test suite

**Measurement:**
```bash
pytest tests/ -v --tb=short
```

**Pass Criteria:**
- All tests pass ✅
- No skipped tests (except known issues) ✅
- No warnings ✅

**Verifies:** Test suite is comprehensive and passing

---

## NFR-4: Observability

**Requirement:** System SHALL track behavioral metrics for optimization

**Measurement Criteria:**
- Track token reduction per query
- Track temp file frequency
- Track query refinement rate (truncate=False after truncated)
- Track misclassification rate (immediate full chunk requests)
- Track angle distribution (validate 80/15/5 assumption)

### Test Specifications

#### Test 4.1: Token Reduction Tracked Per Query

**Test Function:** `test_token_reduction_tracked()`

**Setup:**
- Execute 10 queries with truncation
- Check metrics for token reduction data

**Measurement:**
```python
# Execute queries
for query in test_queries:
    response = pos_search_project(action="search_code", query=query)

# Check metrics
metrics = get_behavioral_metrics()
assert "token_reduction" in metrics
assert len(metrics["token_reduction"]) == 10
```

**Pass Criteria:**
- Token reduction recorded for each query ✅
- Metrics include: tokens_before, tokens_after, reduction_percent ✅

**Verifies:** Token reduction metrics collected

---

#### Test 4.2: Temp File Frequency Tracked

**Test Function:** `test_temp_file_frequency_tracked()`

**Setup:**
- Execute queries that would trigger temp files (large responses)
- Check metrics for temp file events

**Measurement:**
```python
# Execute large queries
response = pos_search_project(action="search_code", query="...", n_results=10)

# Check metrics
metrics = get_behavioral_metrics()
assert "temp_file_events" in metrics
```

**Pass Criteria:**
- Temp file events recorded ✅
- Metrics include: query, response_size, temp_file_written ✅

**Verifies:** Temp file frequency tracked for optimization

---

#### Test 4.3: Query Refinement Rate Tracked

**Test Function:** `test_query_refinement_rate_tracked()`

**Setup:**
- Execute query with truncation
- Execute same query with truncate=False
- Check metrics for refinement event

**Measurement:**
```python
# Initial query
response1 = pos_search_project(action="search_code", query="How does X work?")

# Refined query
response2 = pos_search_project(action="search_code", query="How does X work?", truncate=False)

# Check metrics
metrics = get_behavioral_metrics()
assert "query_refinements" in metrics
assert len(metrics["query_refinements"]) >= 1
```

**Pass Criteria:**
- Refinement events recorded ✅
- Metrics include: original_query, refined_query, time_between ✅

**Verifies:** Query refinement patterns tracked

---

#### Test 4.4: Angle Distribution Tracked

**Test Function:** `test_angle_distribution_tracked()`

**Setup:**
- Execute 100 queries with known angle distribution
- Check metrics for angle counts

**Measurement:**
```python
# Execute queries
execute_test_queries(100)  # 80 conceptual, 15 implementation, 5 critical

# Check metrics
metrics = get_behavioral_metrics()
angle_dist = metrics["angle_distribution"]
assert angle_dist["conceptual"] >= 75  # ~80%
assert angle_dist["implementation"] >= 10  # ~15%
```

**Pass Criteria:**
- Angle distribution recorded ✅
- Metrics validate 80/15/5 assumption ✅

**Verifies:** Query angle distribution tracked for validation

---

#### Test 4.5: Misclassification Rate Tracked

**Test Function:** `test_misclassification_rate_tracked()`

**Setup:**
- Execute query classified as "conceptual" (truncated)
- Immediately execute same query with truncate=False
- Check metrics for potential misclassification

**Measurement:**
```python
# Query gets truncated
response1 = pos_search_project(action="search_code", query="...")

# Immediate full chunk request (potential misclassification)
response2 = pos_search_project(action="search_code", query="...", truncate=False)

# Check metrics
metrics = get_behavioral_metrics()
assert "potential_misclassifications" in metrics
```

**Pass Criteria:**
- Misclassification events recorded ✅
- Metrics include: query, detected_angle, immediate_override ✅

**Verifies:** Misclassification rate tracked for classifier tuning

---

## NFR-5: Usability

**Requirement:** System SHALL be self-documenting and self-teaching

**Measurement Criteria:**
- Clear metadata in responses (truncation status, hints)
- Inline guidance in truncated content
- Examples in docstring for all parameter types
- Error messages with remediation guidance
- Standard document explaining behavior

### Test Specifications

#### Test 5.1: Truncated Response Includes Hint

**Test Function:** `test_truncated_response_includes_hint()`

**Setup:**
- Query: "How does X work?" (conceptual, truncated)

**Action:**
```python
response = pos_search_project(action="search_code", query="How does X work?")
```

**Expected:**
```python
assert "hint" in response["results"][0]
assert "truncate=False" in response["results"][0]["hint"]
assert "full chunk" in response["results"][0]["hint"].lower()
```

**Pass Criteria:**
- Hint present in response ✅
- Hint is actionable ✅
- Hint explains how to get full content ✅

**Verifies:** Responses include clear guidance

---

#### Test 5.2: Metadata is Self-Documenting

**Test Function:** `test_metadata_self_documenting()`

**Setup:**
- Query: "How does X work?" (conceptual, truncated)

**Action:**
```python
response = pos_search_project(action="search_code", query="How does X work?")
metadata = response["metadata"]["truncation_reason"]
```

**Expected:**
```python
assert "angle" in metadata  # Explains why truncated
assert "max_lines" in metadata  # Shows truncation threshold
assert "override" in metadata  # Indicates if user overrode
# Metadata is self-explanatory without documentation
```

**Pass Criteria:**
- Metadata fields have clear names ✅
- Metadata values are self-explanatory ✅
- No external documentation needed to understand ✅

**Verifies:** Metadata is self-documenting

---

#### Test 5.3: Error Messages Are Actionable

**Test Function:** `test_error_messages_actionable()`

**Setup:**
- Query with invalid truncate parameter

**Action:**
```python
response = pos_search_project(
    action="search_code",
    query="How does X work?",
    truncate="invalid_value"
)
```

**Expected:**
```python
assert response["status"] == "error"
assert "truncate must be" in response["error"]["message"]
assert "True, False, int, or 'auto'" in response["error"]["message"]
# Error tells user exactly what to do
```

**Pass Criteria:**
- Error message explains what's wrong ✅
- Error message explains how to fix ✅
- Error message includes valid examples ✅

**Verifies:** Error messages guide users to correct usage

---

#### Test 5.4: Docstring Includes All Parameter Examples

**Test Function:** `test_docstring_parameter_examples()`

**Setup:**
- Inspect pos_search_project docstring

**Measurement:**
```python
import inspect

docstring = inspect.getdoc(pos_search_project)
assert "truncate=True" in docstring
assert "truncate=False" in docstring
assert "truncate=200" in docstring
assert "truncate=\"auto\"" in docstring
```

**Pass Criteria:**
- All parameter types documented ✅
- Examples show correct usage ✅
- Examples cover common scenarios ✅

**Verifies:** Documentation is comprehensive

---

#### Test 5.5: Standard Document Exists

**Test Function:** `test_standard_document_exists()`

**Setup:**
- Check for standard document explaining truncation

**Measurement:**
```python
import os

standard_path = ".praxis-os/standards/universal/tools/pos-search-project-truncation.md"
assert os.path.exists(standard_path)

# Verify content
with open(standard_path) as f:
    content = f.read()
    assert "truncate parameter" in content.lower()
    assert "query angle" in content.lower()
    assert "examples" in content.lower()
```

**Pass Criteria:**
- Standard document exists ✅
- Document explains behavior ✅
- Document includes examples ✅

**Verifies:** Feature is documented in standards

---

## Test Execution Guidance

### Performance Tests

**Environment:**
- Clean state (no cached data)
- Isolated environment (no other processes)
- Consistent hardware (same machine for all runs)

**Execution:**
```bash
pytest tests/performance/ -v --benchmark-only
```

**Statistical Validity:**
- Run each test 100+ times
- Calculate mean, P95, P99
- Discard outliers (top/bottom 1%)

---

### Reliability Tests

**Environment:**
- Fault injection enabled
- Mock external dependencies (QueryClassifier)

**Execution:**
```bash
pytest tests/unit/test_truncation.py -v -k "reliability"
```

**Validation:**
- System continues to function under all fault conditions
- Graceful degradation (no crashes)
- Clear error messages

---

### Maintainability Tests

**Environment:**
- Full codebase
- Coverage tools installed

**Execution:**
```bash
pytest --cov=.praxis-os/ouroboros/tools/pos_search_project \
       --cov-report=html \
       --cov-fail-under=90
```

**Validation:**
- Coverage >90%
- All tests pass
- No skipped tests

---

### Observability Tests

**Environment:**
- Metrics collection enabled
- Behavioral tracking active

**Execution:**
```bash
pytest tests/integration/test_metrics.py -v
```

**Validation:**
- All metrics collected
- Metrics accurate
- Metrics queryable

---

### Usability Tests

**Environment:**
- Standard documents available
- Docstrings complete

**Execution:**
```bash
pytest tests/integration/test_search_code.py -v -k "usability"
```

**Validation:**
- Hints present in responses
- Metadata self-documenting
- Errors actionable

---

## Test Summary

**Total Non-Functional Test Cases:** 22

**By Category:**
- Performance: 6 tests
- Reliability: 6 tests
- Maintainability: 3 tests
- Observability: 5 tests
- Usability: 5 tests

**By NFR:**
- NFR-1 (Performance): 6 tests
- NFR-2 (Reliability): 6 tests
- NFR-3 (Maintainability): 3 tests
- NFR-4 (Observability): 5 tests
- NFR-5 (Usability): 5 tests

**Coverage:** 100% of non-functional requirements

**Objective Metrics:**
- All tests have measurable pass/fail criteria ✅
- No subjective assessments ✅
- Clear target values documented ✅

---

