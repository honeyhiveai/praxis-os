# Supporting Documents Index

**Spec:** Code Search Auto-Truncation with Query-Aware Response Sizing  
**Created:** 2025-11-16  
**Total Documents:** 1

## Document Catalog

### 1. Code Search Auto-Truncation Design Document

**File:** `2025-11-16-code-search-auto-truncation.md`  
**Type:** Comprehensive Design Document  
**Purpose:** Complete design analysis of query-aware auto-truncation feature to solve large code search responses (40-60 KB) that trigger temp file workarounds and crash Cline sessions. Proposes using existing QueryClassifier to automatically determine optimal truncation based on query intent.

**Relevance:** Requirements [H], Design [H], Implementation [H]

**Key Topics:**
- Problem statement (40-60 KB responses, temp files, Cline crashes)
- Root cause analysis (AST chunking keeps entire functions/classes)
- Query distribution analysis (80% conceptual, 15% implementation, 5% troubleshooting)
- Auto-detect solution (QueryClassifier integration)
- Truncation thresholds by angle (50/100/150/None lines)
- Token reduction analysis (70% average savings)
- Temp file frequency reduction (80% reduction)
- Smart truncation at method boundaries
- User experience flows (conceptual/implementation/iterative)
- Success metrics (tokens, temp files, context window economics)
- Risk analysis and mitigations
- Implementation plan (5-8 hours, 4 phases)
- Alternatives considered (split at boundaries, pagination, summaries, no truncation)

---

## Cross-Document Analysis

**Common Themes:**
- Performance optimization through intelligent response sizing
- Behavioral engineering (self-correcting query refinement)
- Elegant integration with existing systems (QueryClassifier, AST chunking)
- Evidence-based design (real data from testing: 41.4 KB, 60.1 KB responses)
- User experience optimization (80/20 rule: optimize for common case)

**Potential Conflicts:**
- None (single comprehensive design document)

**Coverage Gaps:**
- None identified - design doc is comprehensive and covers:
  - Problem statement with evidence
  - Detailed solution design
  - API specification
  - Implementation algorithms
  - Success metrics
  - Risk analysis
  - Alternatives considered
  - Implementation plan with time estimates

---

## Document Summary

This design document emerged from a deep investigation into code search response sizes. Key discoveries:

1. **n_results=3 helps but doesn't solve root cause** - Reduced from 5→3 results (40% reduction), but still hit temp files for large classes
2. **AST chunking keeps entire functions/classes** - Design decision to preserve semantic integrity results in 500-2,000+ token chunks
3. **Query distribution is 80/15/5** - 80% conceptual/location queries only need high-level info, 15% need full implementation, 5% need error paths
4. **First 100 lines = perfect for conceptual** - Class docstring + __init__ + main method signature/algorithm
5. **QueryClassifier makes auto-detect elegant** - Already detecting query intent for prepends, reuse for truncation

The document provides complete specifications for:
- API design (`truncate` parameter with True/False/int/"auto" values)
- Truncation algorithm (classify query → map angle → truncate at boundaries)
- Response format (metadata + hints for users)
- Expected impact (70% token reduction, 80% temp file reduction, 3.4x more queries per context window)
- Implementation phases (core logic → auto-detect → documentation → validation)

---

## Extracted Insights

### Requirements Insights (Phase 1)

#### From Code Search Auto-Truncation Design Document:

**User Needs:**
- **Reliability:** Prevent Cline session crashes from large responses
- **Performance:** Reduce temp file workarounds in Cursor (40-60 KB responses)
- **Efficiency:** Reduce token waste (80% of returned content unused for typical queries)
- **UX:** Reduce cognitive load (AI scrolling through noise to find relevant information)

**Business Goals:**
- **70% average token reduction** across all code searches (6,000 → 1,800 tokens)
- **80% reduction in temp file occurrences** (40% → 8% of queries)
- **3.4x increase in queries per context window** (33 → 111 queries in 200K window)
- **Zero cognitive overhead** for AI agents (automatic optimization)

**Functional Requirements:**
- Auto-detect truncation based on query intent (using existing QueryClassifier)
- Support explicit override mechanism (`truncate=True/False/int/"auto"`)
- Apply truncation only to code search (not standards or AST search)
- Truncate at smart boundaries (method boundaries, not mid-function)
- Include metadata in responses (truncated status, full line count, hints)
- Preserve docstrings and signatures in truncated content
- Provide clear guidance on how to get full chunks

**Constraints:**
- Must maintain backwards compatibility (existing queries work unchanged)
- Must preserve semantic integrity (no mid-method cuts)
- Must not affect indexing (truncation is post-processing only)
- Performance overhead must be <10ms per query
- Test coverage must be >90%

**Query Distribution Requirements:**
- Conceptual queries (60%): 100 lines (entry point + overview)
- Location queries (20%): 50 lines (signature only)
- Implementation queries (15%): Full chunks (no truncation)
- Critical queries (3%): 150 lines (key methods + patterns)
- Troubleshooting queries (2%): Full chunks (error paths)

**Out of Scope:**
- Modifying AST chunking strategy (splitting at boundaries)
- Pagination or multi-round-trip fetching
- LLM-based summarization
- Truncation for standards or AST search

---

### Design Insights (Phase 2)

#### From Code Search Auto-Truncation Design Document:

**Architecture:**
- **Elegant integration:** Reuse existing QueryClassifier for truncation decisions
- **Post-processing:** Truncation happens after search, not during indexing
- **Three-system synergy:** QueryClassifier → Auto-Truncation → AST Chunking
- **Self-correcting:** Metadata teaches AI to request full chunks when needed

**Components:**
- `_determine_truncation(query, truncate_param)`: Maps query angle to line count
- `_truncate_code_chunks(results, max_lines)`: Performs smart truncation at boundaries
- `_find_truncation_point(lines, max_lines)`: Finds natural method boundaries
- Enhanced `_handle_search_code`: Accepts `truncate` parameter

**API Design:**
```python
pos_search_project(
    action="search_code",
    query: str,
    n_results: int = 3,
    truncate: Union[bool, int, str] = True,  # NEW
    filters: Optional[Dict] = None
)
```

**Parameter Behavior:**
- `True` (default): Auto-detect based on query angle
- `False`: No truncation (full chunks)
- `int` (e.g., 200): Explicit line count
- `"auto"`: Same as True (explicit)

**Truncation Strategy:**
- Angle mapping: conceptual→100, location→50, implementation→None, critical→150, troubleshooting→None
- Smart boundaries: Look backwards 20 lines for method end
- Fallback: Use max_lines if no boundary found
- Metadata: Include truncated status, full_line_count, truncation_point, hint

**Response Format:**
```json
{
  "results": [{
    "content": "[first N lines]\n\n... [truncated: X more lines]\nUse truncate=False...",
    "truncated": true,
    "full_line_count": 504,
    "truncation_point": 100,
    "hint": "Use truncate=False to get full chunk"
  }],
  "truncation_reason": {
    "angle": "conceptual",
    "max_lines": 100,
    "override": "Use truncate=False..."
  }
}
```

**Data Flow:**
1. AI queries naturally → QueryClassifier detects intent
2. Auto-truncate based on angle → Truncate at method boundaries
3. Add metadata + hints → Return optimized response

**Technology:**
- Reuse existing QueryClassifier (no new dependencies)
- Simple string operations (line splitting, slicing)
- O(n) complexity where n=lines (minimal overhead)

**Security/Validation:**
- Explicit check: Only apply to `search_code` action
- Parameter validation: Handle True/False/int/"auto"
- Graceful degradation: If classifier fails, default to 100 lines

---

### Implementation Insights (Phase 4)

#### From Code Search Auto-Truncation Design Document:

**Code Patterns:**

**Pattern 1: Angle-Based Truncation Mapping**
```python
truncation_map = {
    "conceptual": 100,      # Entry point + overview
    "location": 50,         # Signature only
    "implementation": None, # Full implementation
    "critical": 150,        # Key methods + patterns
    "troubleshooting": None # Error paths + edge cases
}
return truncation_map.get(angle, 100)  # Default: 100
```

**Pattern 2: Smart Boundary Detection**
```python
# Look backwards from max_lines for method boundary
for i in range(max_lines, max(0, max_lines - 20), -1):
    line = lines[i].strip()
    if not line or line.startswith("def ") or line.startswith("class "):
        return i  # Found natural boundary
return max_lines  # Fallback
```

**Pattern 3: Metadata Enrichment**
```python
result["content"] = truncated_content
result["truncated"] = True
result["full_line_count"] = len(lines)
result["truncation_point"] = truncation_point
result["hint"] = "Use truncate=False to get full chunk"
```

**Testing Strategy:**
- **Unit tests:** `_determine_truncation` (all parameter types: True/False/int/"auto")
- **Unit tests:** `_truncate_code_chunks` (small/medium/large chunks)
- **Unit tests:** `_find_truncation_point` (boundary detection)
- **Integration tests:** Each angle (📖📍🔧⭐⚠️)
- **Edge case tests:** Empty query, classifier failure, no boundary found
- **Validation tests:** Correct truncation for each angle
- **Performance tests:** Latency measurement (<10ms target)
- **Behavioral tests:** Query refinement tracking (truncate=False after truncated)
- **Coverage target:** >90%

**Deployment:**
- No index rebuild required (post-processing only)
- Backwards compatible (existing queries work)
- Feature flag not needed (safe default behavior)
- Monitoring: Track token reduction, temp file frequency, query refinement rate

**Performance Considerations:**
- Post-processing overhead: <10ms (simple string operations)
- No impact on search latency (happens after search)
- No impact on indexing (truncation is response-only)
- Cache truncation points if needed (optimization for Phase 2)

**Implementation Phases:**
1. **Phase 1:** Core truncation logic (2-3h) - parameter, methods, metadata
2. **Phase 2:** Auto-detect integration (1-2h) - classifier integration, angle mapping
3. **Phase 3:** Documentation (1h) - docstring, standards, examples
4. **Phase 4:** Validation & metrics (1-2h) - token counting, benchmarks, metrics

**Total Time:** 5-8 hours implementation

---

### Cross-References

**Validated by Multiple Sources:**
- N/A (single comprehensive design document)

**Conflicts:**
- None identified

**High-Priority Items:**
1. **P0 Reliability:** Prevent Cline crashes and temp file workarounds
2. **P0 Performance:** 70% token reduction, 80% temp file reduction
3. **P0 Backwards Compatibility:** Existing queries must work unchanged
4. **P1 Smart Boundaries:** Truncate at method boundaries, not mid-function
5. **P1 Metadata:** Include hints for users to get full chunks
6. **P2 Learning:** Track query refinement patterns for future optimization

---

## Insight Summary

**Total:** 47 insights  
**By Category:** Requirements [18], Design [16], Implementation [13]  
**Multi-source validated:** 0 (single source)  
**Conflicts to resolve:** 0  
**High-priority items:** 6

**Phase 0 Complete:** ✅ 2025-11-16

