# Functional Tests Plan
## Code Search Auto-Truncation with Query-Aware Response Sizing

**Date:** 2025-11-16  
**Purpose:** Detailed test cases for all functional requirements

**Test Case Format:**
- **Happy Path:** Feature works as expected with valid inputs
- **Error Path:** Handles errors gracefully with clear messaging
- **Edge Cases:** Boundary conditions and corner cases

---

## FR-1: Query-Aware Auto-Truncation

**Requirement:** System SHALL automatically detect query intent and apply appropriate truncation

**Acceptance Criteria:**
- Use QueryClassifier to detect angle (conceptual/location/implementation/critical/troubleshooting)
- Map angle to threshold: conceptual→100, location→50, implementation→None, critical→150, troubleshooting→None
- Default to 100 if angle unknown
- Apply only to search_code action

### Test Cases

#### TC-1.1: Conceptual Query Returns 100 Lines

**Test Function:** `test_search_code_conceptual_query_truncated()`

**Setup:**
- Code chunk with 500 lines
- Query: "How does the authentication system work?"
- Expected angle: "conceptual"

**Action:**
```python
response = pos_search_project(
    action="search_code",
    query="How does the authentication system work?",
    n_results=1
)
```

**Expected:**
- Response status: "success"
- Result count: 1
- Result[0]["truncated"]: True
- Result[0]["content"]: ~100 lines
- Result[0]["full_line_count"]: 500
- Result[0]["truncation_point"]: ~100
- Response metadata includes: `truncation_reason.angle = "conceptual"`

**Verifies:** Conceptual queries get 100-line truncation

---

#### TC-1.2: Location Query Returns 50 Lines

**Test Function:** `test_search_code_location_query_truncated()`

**Setup:**
- Code chunk with 500 lines
- Query: "Where is the user validation implemented?"
- Expected angle: "location"

**Action:**
```python
response = pos_search_project(
    action="search_code",
    query="Where is the user validation implemented?",
    n_results=1
)
```

**Expected:**
- Result[0]["truncated"]: True
- Result[0]["content"]: ~50 lines
- Result[0]["full_line_count"]: 500
- Response metadata: `truncation_reason.angle = "location"`

**Verifies:** Location queries get 50-line truncation

---

#### TC-1.3: Implementation Query Returns Full Chunks

**Test Function:** `test_search_code_implementation_query_full()`

**Setup:**
- Code chunk with 500 lines
- Query: "How to implement OAuth2 flow?"
- Expected angle: "implementation"

**Action:**
```python
response = pos_search_project(
    action="search_code",
    query="How to implement OAuth2 flow?",
    n_results=1
)
```

**Expected:**
- Result[0]["truncated"]: False
- Result[0]["content"]: 500 lines (full chunk)
- Response metadata: `truncation_reason.angle = "implementation"`

**Verifies:** Implementation queries get full chunks (no truncation)

---

#### TC-1.4: Critical Query Returns 150 Lines

**Test Function:** `test_search_code_critical_query_truncated()`

**Setup:**
- Code chunk with 500 lines
- Query: "Key patterns in workflow execution"
- Expected angle: "critical"

**Action:**
```python
response = pos_search_project(
    action="search_code",
    query="Key patterns in workflow execution",
    n_results=1
)
```

**Expected:**
- Result[0]["truncated"]: True
- Result[0]["content"]: ~150 lines
- Response metadata: `truncation_reason.angle = "critical"`

**Verifies:** Critical queries get 150-line truncation

---

#### TC-1.5: Troubleshooting Query Returns Full Chunks

**Test Function:** `test_search_code_troubleshooting_query_full()`

**Setup:**
- Code chunk with 500 lines
- Query: "Common authentication errors and fixes"
- Expected angle: "troubleshooting"

**Action:**
```python
response = pos_search_project(
    action="search_code",
    query="Common authentication errors and fixes",
    n_results=1
)
```

**Expected:**
- Result[0]["truncated"]: False
- Result[0]["content"]: 500 lines (full chunk)
- Response metadata: `truncation_reason.angle = "troubleshooting"`

**Verifies:** Troubleshooting queries get full chunks

---

#### TC-1.6: Unknown Angle Defaults to 100 Lines

**Test Function:** `test_search_code_unknown_angle_defaults()`

**Setup:**
- Code chunk with 500 lines
- Query: "xyzabc" (nonsense query)
- Expected angle: Unknown/unclassified

**Action:**
```python
response = pos_search_project(
    action="search_code",
    query="xyzabc",
    n_results=1
)
```

**Expected:**
- Result[0]["truncated"]: True
- Result[0]["content"]: ~100 lines (default)
- Response metadata: `truncation_reason.angle = "conceptual"` (fallback)

**Verifies:** Unknown angles default to safe 100-line truncation

---

#### TC-1.7: Standards Search Not Truncated

**Test Function:** `test_search_standards_not_truncated()`

**Setup:**
- Standards document with 500 lines
- Query: "How does workflow system work?"

**Action:**
```python
response = pos_search_project(
    action="search_standards",
    query="How does workflow system work?",
    n_results=1
)
```

**Expected:**
- Result[0]["truncated"]: False (or field not present)
- Result[0]["content"]: Full content (no truncation)
- No truncation metadata in response

**Verifies:** Truncation only applies to search_code action

---

## FR-2: Explicit Override Mechanism

**Requirement:** System SHALL support explicit truncation control via `truncate` parameter

**Acceptance Criteria:**
- Accept True (auto-detect), False (no truncation), int (explicit line count), "auto" (explicit auto-detect)
- Override takes precedence over auto-detection
- Parameter ignored for non-code search

### Test Cases

#### TC-2.1: truncate=True Auto-Detects (Default)

**Test Function:** `test_truncate_true_auto_detects()`

**Setup:**
- Code chunk with 500 lines
- Query: "How does X work?" (conceptual)

**Action:**
```python
response = pos_search_project(
    action="search_code",
    query="How does X work?",
    truncate=True,
    n_results=1
)
```

**Expected:**
- Result[0]["truncated"]: True
- Result[0]["content"]: ~100 lines
- Response metadata: `truncation_reason.override = False`

**Verifies:** truncate=True enables auto-detection

---

#### TC-2.2: truncate=False Returns Full Chunks

**Test Function:** `test_truncate_false_full_chunks()`

**Setup:**
- Code chunk with 500 lines
- Query: "How does X work?" (conceptual, would normally truncate)

**Action:**
```python
response = pos_search_project(
    action="search_code",
    query="How does X work?",
    truncate=False,
    n_results=1
)
```

**Expected:**
- Result[0]["truncated"]: False
- Result[0]["content"]: 500 lines (full chunk)
- Response metadata: `truncation_reason.override = True, max_lines = None`

**Verifies:** truncate=False disables truncation (override)

---

#### TC-2.3: truncate=200 Returns Exactly 200 Lines

**Test Function:** `test_truncate_explicit_line_count()`

**Setup:**
- Code chunk with 500 lines
- Query: "How does X work?" (conceptual, would normally be 100)

**Action:**
```python
response = pos_search_project(
    action="search_code",
    query="How does X work?",
    truncate=200,
    n_results=1
)
```

**Expected:**
- Result[0]["truncated"]: True
- Result[0]["content"]: ~200 lines
- Result[0]["truncation_point"]: ~200
- Response metadata: `truncation_reason.override = True, max_lines = 200`

**Verifies:** Explicit integer overrides auto-detection

---

#### TC-2.4: truncate="auto" Explicitly Auto-Detects

**Test Function:** `test_truncate_auto_string_explicit()`

**Setup:**
- Code chunk with 500 lines
- Query: "How does X work?" (conceptual)

**Action:**
```python
response = pos_search_project(
    action="search_code",
    query="How does X work?",
    truncate="auto",
    n_results=1
)
```

**Expected:**
- Result[0]["truncated"]: True
- Result[0]["content"]: ~100 lines
- Response metadata: `truncation_reason.override = False`

**Verifies:** truncate="auto" same as truncate=True

---

#### TC-2.5: Invalid truncate Value Raises Error

**Test Function:** `test_truncate_invalid_value_error()`

**Setup:**
- Query: "How does X work?"

**Action:**
```python
response = pos_search_project(
    action="search_code",
    query="How does X work?",
    truncate="invalid",  # Invalid string
    n_results=1
)
```

**Expected:**
- Response status: "error"
- Error code: "INVALID_PARAMETER"
- Error message: Contains "truncate must be True, False, int, or 'auto'"
- Error includes remediation guidance

**Verifies:** Invalid parameter values produce clear error messages

---

#### TC-2.6: Negative Line Count Raises Error

**Test Function:** `test_truncate_negative_int_error()`

**Setup:**
- Query: "How does X work?"

**Action:**
```python
response = pos_search_project(
    action="search_code",
    query="How does X work?",
    truncate=-50,  # Negative int
    n_results=1
)
```

**Expected:**
- Response status: "error"
- Error code: "INVALID_PARAMETER"
- Error message: "truncate line count must be positive"

**Verifies:** Input validation prevents invalid line counts

---

## FR-3: Smart Boundary Truncation

**Requirement:** System SHALL truncate at natural code boundaries

**Acceptance Criteria:**
- Never truncate mid-method or mid-docstring
- Look backwards up to 20 lines for boundary
- Natural boundaries: blank line, `def `, `class `
- Fallback to target line if no boundary found
- Preserve complete docstrings

### Test Cases

#### TC-3.1: Truncate at Method Boundary

**Test Function:** `test_truncate_at_method_boundary()`

**Setup:**
- Code chunk:
  - Lines 1-50: Class definition
  - Lines 51-95: Method A (ends at line 95)
  - Lines 96-100: Blank lines
  - Lines 101-200: Method B
- Target truncation: 100 lines

**Action:**
```python
result = _truncate_code_chunks([chunk], max_lines=100)
```

**Expected:**
- Truncation point: 95 (end of Method A, natural boundary)
- Content includes: Complete Method A
- Content excludes: Method B
- Metadata: `truncation_point = 95`

**Verifies:** Truncates at nearest method boundary before target

---

#### TC-3.2: Truncate at Class Boundary

**Test Function:** `test_truncate_at_class_boundary()`

**Setup:**
- Code chunk:
  - Lines 1-90: Class A
  - Lines 91-95: Blank lines
  - Lines 96-200: Class B (starts at line 96)
- Target truncation: 100 lines

**Action:**
```python
result = _truncate_code_chunks([chunk], max_lines=100)
```

**Expected:**
- Truncation point: 95 (before Class B starts)
- Content includes: Complete Class A
- Content excludes: Class B

**Verifies:** Truncates before new class definition

---

#### TC-3.3: No Boundary Found Uses Target

**Test Function:** `test_truncate_no_boundary_uses_target()`

**Setup:**
- Code chunk: Single 200-line method (no natural boundaries)
- Target truncation: 100 lines

**Action:**
```python
result = _truncate_code_chunks([chunk], max_lines=100)
```

**Expected:**
- Truncation point: 100 (target, fallback)
- Warning logged: "No natural boundary found, using target line"

**Verifies:** Fallback to target when no boundary within 20 lines

---

#### TC-3.4: Preserve Complete Docstring

**Test Function:** `test_truncate_preserves_docstring()`

**Setup:**
- Code chunk:
  - Lines 1-10: Class definition
  - Lines 11-50: Class docstring (multi-line)
  - Lines 51-100: Methods
- Target truncation: 40 lines (would cut docstring)

**Action:**
```python
result = _truncate_code_chunks([chunk], max_lines=40)
```

**Expected:**
- Truncation point: ≥50 (after docstring ends)
- Content includes: Complete docstring
- No partial docstring in output

**Verifies:** Never truncates mid-docstring

---

#### TC-3.5: Blank Line as Natural Boundary

**Test Function:** `test_truncate_at_blank_line()`

**Setup:**
- Code chunk:
  - Lines 1-98: Code
  - Line 99: Blank line
  - Lines 100-200: More code
- Target truncation: 100 lines

**Action:**
```python
result = _truncate_code_chunks([chunk], max_lines=100)
```

**Expected:**
- Truncation point: 99 (blank line is natural boundary)
- Content ends with blank line (clean separation)

**Verifies:** Blank lines are recognized as natural boundaries

---

## FR-4: Response Metadata

**Requirement:** System SHALL include comprehensive metadata in truncated responses

**Acceptance Criteria:**
- Per-result: truncated (bool), full_line_count (int), truncation_point (int), hint (str)
- Response-level: truncation_reason (angle, max_lines, override)
- Inline hint in content

### Test Cases

#### TC-4.1: Truncated Result Includes All Metadata

**Test Function:** `test_truncated_result_metadata_complete()`

**Setup:**
- Code chunk with 500 lines
- Query: "How does X work?" (conceptual, 100 lines)

**Action:**
```python
response = pos_search_project(
    action="search_code",
    query="How does X work?",
    n_results=1
)
```

**Expected:**
```python
assert response["results"][0]["truncated"] == True
assert response["results"][0]["full_line_count"] == 500
assert response["results"][0]["truncation_point"] == 100
assert "Use truncate=False" in response["results"][0]["hint"]
assert response["metadata"]["truncation_reason"]["angle"] == "conceptual"
assert response["metadata"]["truncation_reason"]["max_lines"] == 100
assert response["metadata"]["truncation_reason"]["override"] == False
```

**Verifies:** All required metadata fields present and accurate

---

#### TC-4.2: Non-Truncated Result Metadata

**Test Function:** `test_non_truncated_result_metadata()`

**Setup:**
- Code chunk with 500 lines
- Query: "How to implement X?" (implementation, no truncation)

**Action:**
```python
response = pos_search_project(
    action="search_code",
    query="How to implement X?",
    n_results=1
)
```

**Expected:**
```python
assert response["results"][0]["truncated"] == False
assert "full_line_count" not in response["results"][0]  # Optional
assert "truncation_point" not in response["results"][0]
assert "hint" not in response["results"][0]
```

**Verifies:** Non-truncated results have minimal metadata

---

#### TC-4.3: Inline Hint in Content

**Test Function:** `test_inline_hint_in_truncated_content()`

**Setup:**
- Code chunk with 500 lines
- Query: "How does X work?" (conceptual, 100 lines)

**Action:**
```python
response = pos_search_project(
    action="search_code",
    query="How does X work?",
    n_results=1
)
content = response["results"][0]["content"]
```

**Expected:**
```python
assert "... [truncated:" in content
assert "400 more lines]" in content  # 500 - 100 = 400
assert "Use truncate=False to get full chunk" in content
```

**Verifies:** Inline hint appears in truncated content

---

#### TC-4.4: Response-Level Truncation Reason

**Test Function:** `test_response_truncation_reason_metadata()`

**Setup:**
- Query: "Where is X?" (location, 50 lines)

**Action:**
```python
response = pos_search_project(
    action="search_code",
    query="Where is X?",
    n_results=1
)
```

**Expected:**
```python
assert "truncation_reason" in response["metadata"]
assert response["metadata"]["truncation_reason"]["angle"] == "location"
assert response["metadata"]["truncation_reason"]["max_lines"] == 50
assert response["metadata"]["truncation_reason"]["override"] == False
```

**Verifies:** Response-level metadata explains truncation decision

---

## FR-5: Backwards Compatibility

**Requirement:** System SHALL maintain backwards compatibility with existing queries

**Acceptance Criteria:**
- Existing queries without truncate parameter work unchanged (auto-detect applied)
- Default: truncate=True
- No changes to response structure (only additions)
- No changes to other search actions or indexing

### Test Cases

#### TC-5.1: Query Without truncate Param Works

**Test Function:** `test_backwards_compatible_no_param()`

**Setup:**
- Code chunk with 500 lines
- Query: "How does X work?" (conceptual)

**Action:**
```python
# Old-style call (no truncate parameter)
response = pos_search_project(
    action="search_code",
    query="How does X work?",
    n_results=1
)
```

**Expected:**
- Response status: "success"
- Result[0]["truncated"]: True (auto-detect applied)
- Result[0]["content"]: ~100 lines
- No errors or warnings

**Verifies:** Existing queries work unchanged with auto-detect

---

#### TC-5.2: Existing Response Fields Unchanged

**Test Function:** `test_backwards_compatible_response_structure()`

**Setup:**
- Query: "How does X work?"

**Action:**
```python
response = pos_search_project(
    action="search_code",
    query="How does X work?",
    n_results=1
)
```

**Expected:**
```python
# All existing fields still present
assert "status" in response
assert "action" in response
assert "results" in response
assert "count" in response
assert "metadata" in response
assert "file" in response["results"][0]
assert "content" in response["results"][0]
assert "score" in response["results"][0]
# New fields are additions only
assert "truncated" in response["results"][0]  # New field
```

**Verifies:** Response structure is additive (no breaking changes)

---

#### TC-5.3: Standards Search Unchanged

**Test Function:** `test_standards_search_unchanged()`

**Setup:**
- Standards document
- Query: "How does X work?"

**Action:**
```python
response = pos_search_project(
    action="search_standards",
    query="How does X work?",
    n_results=1
)
```

**Expected:**
- No truncation applied
- No truncation metadata in response
- Behavior identical to pre-truncation implementation

**Verifies:** Other search actions unaffected

---

#### TC-5.4: AST Search Unchanged

**Test Function:** `test_ast_search_unchanged()`

**Setup:**
- Code files
- Query: "function definitions"

**Action:**
```python
response = pos_search_project(
    action="search_ast",
    query="function definitions",
    n_results=1
)
```

**Expected:**
- No truncation applied
- Behavior unchanged

**Verifies:** AST search unaffected

---

#### TC-5.5: Graph Search Unchanged

**Test Function:** `test_graph_search_unchanged()`

**Setup:**
- Code graph
- Query: "process_workflow"

**Action:**
```python
response = pos_search_project(
    action="find_callers",
    query="process_workflow",
    max_depth=5
)
```

**Expected:**
- No truncation applied
- Behavior unchanged

**Verifies:** Graph search unaffected

---

## FR-6: Query Distribution Optimization

**Requirement:** System SHALL optimize for observed query distribution (80/15/5)

**Acceptance Criteria:**
- 80% of queries (conceptual/location) get truncated (50-100 lines)
- 15% (implementation) get full chunks
- 5% (critical/troubleshooting) get appropriate content
- Weighted average: 1,800 tokens per query (down from 6,000)

### Test Cases

#### TC-6.1: Weighted Average Token Reduction

**Test Function:** `test_weighted_average_token_reduction()`

**Setup:**
- Simulate 100 queries with 80/15/5 distribution
- Each chunk: 500 lines (~6,000 tokens)

**Action:**
```python
# 80 conceptual/location queries (avg 75 lines)
# 15 implementation queries (500 lines)
# 5 critical/troubleshooting queries (150/500 lines)
total_tokens = simulate_query_distribution(100)
avg_tokens = total_tokens / 100
```

**Expected:**
- Average tokens per query: ~1,800 (±10%)
- Token reduction: ~70% (from 6,000 to 1,800)

**Verifies:** Achieves 70% token reduction target

---

#### TC-6.2: Conceptual Queries Token Reduction

**Test Function:** `test_conceptual_queries_token_reduction()`

**Setup:**
- 10 conceptual queries
- Each chunk: 500 lines (~6,000 tokens)

**Action:**
```python
total_tokens_before = 10 * 6000
total_tokens_after = sum([
    count_tokens(response["results"][0]["content"])
    for response in conceptual_query_responses
])
reduction = (total_tokens_before - total_tokens_after) / total_tokens_before
```

**Expected:**
- Token reduction: ~83% (100 lines vs 500 lines)

**Verifies:** Conceptual queries achieve high token reduction

---

#### TC-6.3: Implementation Queries No Reduction

**Test Function:** `test_implementation_queries_no_reduction()`

**Setup:**
- 10 implementation queries
- Each chunk: 500 lines (~6,000 tokens)

**Action:**
```python
total_tokens_before = 10 * 6000
total_tokens_after = sum([
    count_tokens(response["results"][0]["content"])
    for response in implementation_query_responses
])
reduction = (total_tokens_before - total_tokens_after) / total_tokens_before
```

**Expected:**
- Token reduction: 0% (full chunks returned)

**Verifies:** Implementation queries get full content (no reduction)

---

## FR-7: Preserve Docstrings and Signatures

**Requirement:** System SHALL always include complete docstrings and signatures in truncated content

**Acceptance Criteria:**
- Class docstrings always included
- __init__ method included with signature + docstring
- Main method: signature + docstring + high-level algorithm
- Helper methods: signatures visible
- Truncate at helper method boundaries

### Test Cases

#### TC-7.1: Class Docstring Preserved

**Test Function:** `test_truncate_preserves_class_docstring()`

**Setup:**
- Code chunk:
  - Lines 1-5: Class definition
  - Lines 6-40: Class docstring
  - Lines 41-500: Methods
- Target truncation: 100 lines

**Action:**
```python
result = _truncate_code_chunks([chunk], max_lines=100)
content = result[0]["content"]
```

**Expected:**
- Content includes: Lines 1-40 (complete class docstring)
- Docstring not truncated mid-sentence
- Class purpose clearly documented

**Verifies:** Class docstrings always preserved

---

#### TC-7.2: __init__ Method Included

**Test Function:** `test_truncate_includes_init_method()`

**Setup:**
- Code chunk:
  - Lines 1-40: Class definition + docstring
  - Lines 41-80: __init__ method with docstring
  - Lines 81-500: Other methods
- Target truncation: 100 lines

**Action:**
```python
result = _truncate_code_chunks([chunk], max_lines=100)
content = result[0]["content"]
```

**Expected:**
- Content includes: Lines 1-80 (class + __init__)
- __init__ signature visible
- __init__ docstring complete
- Parameters documented

**Verifies:** __init__ method always included in truncated content

---

#### TC-7.3: Main Method Signature Preserved

**Test Function:** `test_truncate_preserves_main_method_signature()`

**Setup:**
- Code chunk:
  - Lines 1-80: Class + __init__
  - Lines 81-120: Main method (signature + docstring + logic)
  - Lines 121-500: Helper methods
- Target truncation: 100 lines

**Action:**
```python
result = _truncate_code_chunks([chunk], max_lines=100)
content = result[0]["content"]
```

**Expected:**
- Content includes: Main method signature
- Content includes: Main method docstring
- Content may include: High-level algorithm (if fits)
- Truncation at method boundary after main method

**Verifies:** Main method signature + docstring preserved

---

#### TC-7.4: Helper Method Signatures Visible

**Test Function:** `test_truncate_shows_helper_signatures()`

**Setup:**
- Code chunk:
  - Lines 1-80: Class + __init__
  - Lines 81-120: Main method
  - Lines 121-140: Helper method 1 signature + docstring
  - Lines 141-160: Helper method 2 signature + docstring
  - Lines 161-500: Helper implementations
- Target truncation: 150 lines

**Action:**
```python
result = _truncate_code_chunks([chunk], max_lines=150)
content = result[0]["content"]
```

**Expected:**
- Content includes: Helper method signatures
- Content includes: Helper method docstrings
- Content excludes: Helper method implementations
- Truncation at helper method boundary

**Verifies:** Helper method signatures visible (not full implementations)

---

## Integration Tests

### Scenario 1: End-to-End Conceptual Query

**Requirements:** FR-1, FR-3, FR-4, FR-5

**Test Function:** `test_e2e_conceptual_query_flow()`

**Flow:**
1. AI agent queries: "How does the workflow system work?"
2. QueryClassifier detects: "conceptual"
3. System determines: 100-line truncation
4. System searches code index
5. System finds 3 results (500 lines each)
6. System truncates each at natural boundaries (~100 lines)
7. System adds metadata (truncated=True, hint, truncation_reason)
8. System returns response

**Expected:**
- Response contains 3 truncated results
- Each ~100 lines with complete docstrings
- Metadata guides AI to use truncate=False if needed
- Total response: ~300 lines (vs 1,500 lines without truncation)

**Verifies:** Complete flow for most common query type

---

### Scenario 2: Query Refinement Flow

**Requirements:** FR-2, FR-4, FR-5

**Test Function:** `test_e2e_query_refinement_flow()`

**Flow:**
1. AI agent queries: "How does X work?" (conceptual)
2. System returns truncated results with hint
3. AI agent reads hint: "Use truncate=False to get full chunk"
4. AI agent refines query with truncate=False
5. System returns full chunks

**Expected:**
- First response: Truncated with hint
- Second response: Full chunks
- AI learns optimal query pattern
- System tracks refinement rate (NFR-4)

**Verifies:** Self-teaching system guides AI to optimal queries

---

### Scenario 3: Mixed Query Types in Session

**Requirements:** FR-1, FR-2, FR-5

**Test Function:** `test_e2e_mixed_query_session()`

**Flow:**
1. Query 1: "How does X work?" → Truncated (conceptual)
2. Query 2: "Where is Y?" → Truncated (location, 50 lines)
3. Query 3: "How to implement Z?" → Full chunks (implementation)
4. Query 4: Standards search → No truncation

**Expected:**
- Each query gets appropriate treatment
- No interference between queries
- Behavioral metrics track angle distribution

**Verifies:** System handles diverse query types in single session

---

## Test Summary

**Total Functional Test Cases:** 38

**By Requirement:**
- FR-1: 7 tests
- FR-2: 6 tests
- FR-3: 5 tests
- FR-4: 4 tests
- FR-5: 5 tests
- FR-6: 3 tests
- FR-7: 4 tests
- Integration: 4 tests

**Coverage:** 100% of functional requirements

---

