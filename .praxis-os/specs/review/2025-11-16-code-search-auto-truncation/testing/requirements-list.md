# Requirements List for Testing
## Code Search Auto-Truncation with Query-Aware Response Sizing

**Date:** 2025-11-16  
**Source:** srd.md  
**Purpose:** Complete list of requirements for test planning and traceability

---

## Functional Requirements

| FR ID | Description | Acceptance Criteria | Priority |
|-------|-------------|---------------------|----------|
| **FR-1** | Query-Aware Auto-Truncation | System SHALL automatically detect query intent and apply appropriate truncation. Use QueryClassifier to detect angle (conceptual/location/implementation/critical/troubleshooting). Map angle to threshold: conceptual→100, location→50, implementation→None, critical→150, troubleshooting→None. Default to 100 if angle unknown. Apply only to search_code action. | P0 |
| **FR-2** | Explicit Override Mechanism | System SHALL support explicit truncation control via `truncate` parameter. Accept True (auto-detect), False (no truncation), int (explicit line count), "auto" (explicit auto-detect). Override takes precedence over auto-detection. Parameter ignored for non-code search. | P0 |
| **FR-3** | Smart Boundary Truncation | System SHALL truncate at natural code boundaries (method/class boundaries). Never truncate mid-method or mid-docstring. Look backwards up to 20 lines for boundary. Natural boundaries: blank line, `def `, `class `. Fallback to target line if no boundary found. Preserve complete docstrings. | P0 |
| **FR-4** | Response Metadata | System SHALL include comprehensive metadata in truncated responses. Per-result: truncated (bool), full_line_count (int), truncation_point (int), hint (str). Response-level: truncation_reason (angle, max_lines, override). Inline hint in content. | P0 |
| **FR-5** | Backwards Compatibility | System SHALL maintain backwards compatibility with existing queries. Existing queries without truncate parameter work unchanged (auto-detect applied). Default: truncate=True. No changes to response structure (only additions). No changes to other search actions or indexing. | P0 |
| **FR-6** | Query Distribution Optimization | System SHALL optimize for observed query distribution (80/15/5). 80% of queries (conceptual/location) get truncated (50-100 lines). 15% (implementation) get full chunks. 5% (critical/troubleshooting) get appropriate content. Weighted average: 1,800 tokens per query (down from 6,000). | P0 |
| **FR-7** | Preserve Docstrings and Signatures | System SHALL always include complete docstrings and signatures in truncated content. Class docstrings always included. __init__ method included with signature + docstring. Main method: signature + docstring + high-level algorithm. Helper methods: signatures visible. Truncate at helper method boundaries. | P0 |

---

## Non-Functional Requirements

| NFR ID | Description | Measurement Criteria | Priority |
|--------|-------------|----------------------|----------|
| **NFR-1** | Performance | Truncation overhead SHALL be <10ms per query. Post-processing only (no impact on search latency). Simple string operations (line splitting, slicing). O(n) complexity where n=lines in chunk. No LLM inference. Benchmark: 95th percentile <10ms. | P0 |
| **NFR-2** | Reliability | System SHALL handle edge cases gracefully. Classifier failure → default to 100 lines. No natural boundary → use target line. Empty query → default to 100 lines. Invalid truncate parameter → error with guidance. Chunk smaller than threshold → no truncation. | P0 |
| **NFR-3** | Maintainability | Code SHALL be well-tested and documented. Test coverage >90%. Unit tests for all truncation logic. Integration tests for each query angle. Edge case tests for error conditions. Performance benchmarks. Comprehensive docstrings with examples. | P0 |
| **NFR-4** | Observability | System SHALL track behavioral metrics for optimization. Track: token reduction per query, temp file frequency, query refinement rate (truncate=False after truncated), misclassification rate (immediate full chunk requests), angle distribution (validate 80/15/5 assumption). | P1 |
| **NFR-5** | Usability | System SHALL be self-documenting and self-teaching. Clear metadata in responses (truncation status, hints). Inline guidance in truncated content. Examples in docstring for all parameter types. Error messages with remediation guidance. Standard document explaining behavior. | P1 |

---

## Test Cases Summary

### FR-1: Query-Aware Auto-Truncation
- TC-1.1: Conceptual query "How does X work?" → 100 lines per result
- TC-1.2: Location query "Where is X?" → 50 lines per result
- TC-1.3: Implementation query "How to implement X?" → Full chunks
- TC-1.4: Unknown angle → 100 lines (safe default)
- TC-1.5: Standards search → No truncation (ignored)

### FR-2: Explicit Override Mechanism
- TC-2.1: `truncate=True` → Auto-detect (default)
- TC-2.2: `truncate=False` → Full chunks
- TC-2.3: `truncate=200` → Exactly 200 lines
- TC-2.4: `truncate="auto"` → Auto-detect (explicit)
- TC-2.5: Invalid value → Error with guidance

### FR-3: Smart Boundary Truncation
- TC-3.1: Target at line 100, method ends at 95 → Truncate at 95
- TC-3.2: Target at line 100, no boundary in 80-100 → Truncate at 100
- TC-3.3: Docstring at lines 90-105, target 100 → Truncate at 110 (after docstring)
- TC-3.4: Multiple methods near target → Truncate at nearest boundary

### FR-4: Response Metadata
- TC-4.1: Truncated result includes all metadata fields
- TC-4.2: Non-truncated result has `truncated=false`
- TC-4.3: Response includes `truncation_reason` with detected angle
- TC-4.4: Inline hint appears in truncated content

### FR-5: Backwards Compatibility
- TC-5.1: Query without `truncate` param → Auto-detect applied
- TC-5.2: Standards search → No truncation
- TC-5.3: AST search → No truncation
- TC-5.4: Graph search → No truncation
- TC-5.5: Existing response fields unchanged

### FR-6: Query Distribution Optimization
- TC-6.1: Simulate 100 queries with 80/15/5 distribution → Avg 1,800 tokens
- TC-6.2: Conceptual queries → 80% token reduction
- TC-6.3: Implementation queries → 0% token reduction (full content)

### FR-7: Preserve Docstrings and Signatures
- TC-7.1: Truncated at 100 lines includes complete class docstring
- TC-7.2: Truncated content includes `__init__` method
- TC-7.3: Main method signature + docstring included
- TC-7.4: Helper method signatures visible (not implementations)

### NFR-2: Reliability
- TC-NFR-2.1: Classifier unavailable → Default to 100 lines
- TC-NFR-2.2: No boundary in 20 lines → Use target
- TC-NFR-2.3: Chunk 50 lines, threshold 100 → No truncation

---

## Requirements Summary

**Functional Requirements:**
- Total: 7
- Priority P0: 7
- Priority P1: 0

**Non-Functional Requirements:**
- Total: 5
- Priority P0: 3
- Priority P1: 2

**Total Requirements to Test: 12**

**Test Cases:**
- Functional test cases: 27
- Non-functional test cases: 3
- Total test cases: 30

---

## Traceability Matrix

| Requirement | Test Cases | Test File |
|-------------|------------|-----------|
| FR-1 | TC-1.1, TC-1.2, TC-1.3, TC-1.4, TC-1.5 | functional-tests.md |
| FR-2 | TC-2.1, TC-2.2, TC-2.3, TC-2.4, TC-2.5 | functional-tests.md |
| FR-3 | TC-3.1, TC-3.2, TC-3.3, TC-3.4 | functional-tests.md |
| FR-4 | TC-4.1, TC-4.2, TC-4.3, TC-4.4 | functional-tests.md |
| FR-5 | TC-5.1, TC-5.2, TC-5.3, TC-5.4, TC-5.5 | functional-tests.md |
| FR-6 | TC-6.1, TC-6.2, TC-6.3 | functional-tests.md |
| FR-7 | TC-7.1, TC-7.2, TC-7.3, TC-7.4 | functional-tests.md |
| NFR-1 | Performance benchmarks | nonfunctional-tests.md |
| NFR-2 | TC-NFR-2.1, TC-NFR-2.2, TC-NFR-2.3 | nonfunctional-tests.md |
| NFR-3 | Coverage report | nonfunctional-tests.md |
| NFR-4 | Metrics tracking | nonfunctional-tests.md |
| NFR-5 | Usability validation | nonfunctional-tests.md |

---

## Coverage Analysis

**Requirements with Test Cases:** 12/12 (100%)  
**Requirements with Acceptance Criteria:** 12/12 (100%)  
**Requirements with Measurement Criteria:** 12/12 (100%)

**Status:** ✅ All requirements have defined test coverage

---

