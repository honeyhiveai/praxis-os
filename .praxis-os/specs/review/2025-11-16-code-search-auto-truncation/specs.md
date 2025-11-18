# Technical Specifications
## Code Search Auto-Truncation with Query-Aware Response Sizing

**Project:** Code Search Auto-Truncation  
**Date:** 2025-11-16  
**Based on:** srd.md (requirements)  
**Status:** Draft

---

## 1. Architecture Overview

### 1.1 Architectural Pattern

**Primary Pattern:** **Post-Processing Enhancement Pattern**

This feature implements a post-processing enhancement to the existing search pipeline, adding intelligent truncation after search results are retrieved but before they are returned to the client.

**Pattern Characteristics:**
- **Non-invasive:** Does not modify core search or indexing logic
- **Composable:** Integrates with existing QueryClassifier middleware
- **Reversible:** Can be disabled via parameter without code changes
- **Transparent:** Backwards compatible with existing queries

**Architecture Diagram:**

```
┌─────────────────────────────────────────────────────────────────┐
│                     pos_search_project Tool                      │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  1. Receive Query                                          │ │
│  │     - action: "search_code"                                │ │
│  │     - query: "How does X work?"                            │ │
│  │     - truncate: True (default)                             │ │
│  └────────────────┬───────────────────────────────────────────┘ │
│                   │                                               │
│  ┌────────────────▼───────────────────────────────────────────┐ │
│  │  2. Execute Search (Existing)                              │ │
│  │     - SemanticIndex.search()                               │ │
│  │     - Returns n_results=3 chunks                           │ │
│  │     - Each chunk: 500-2,000+ lines                         │ │
│  └────────────────┬───────────────────────────────────────────┘ │
│                   │                                               │
│  ┌────────────────▼───────────────────────────────────────────┐ │
│  │  3. Classify Query Intent (NEW - uses existing)           │ │
│  │     ┌──────────────────────────────────────────┐          │ │
│  │     │  QueryClassifier.classify(query)         │          │ │
│  │     │  → Returns: "conceptual" angle           │          │ │
│  │     └──────────────────────────────────────────┘          │ │
│  └────────────────┬───────────────────────────────────────────┘ │
│                   │                                               │
│  ┌────────────────▼───────────────────────────────────────────┐ │
│  │  4. Determine Truncation (NEW)                             │ │
│  │     - _determine_truncation(query, truncate_param)         │ │
│  │     - Maps angle → line count                              │ │
│  │     - conceptual → 100 lines                               │ │
│  └────────────────┬───────────────────────────────────────────┘ │
│                   │                                               │
│  ┌────────────────▼───────────────────────────────────────────┐ │
│  │  5. Truncate at Smart Boundaries (NEW)                     │ │
│  │     - _truncate_code_chunks(results, max_lines=100)        │ │
│  │     - For each chunk:                                      │ │
│  │       • Find natural boundary (method end)                 │ │
│  │       • Truncate at boundary                               │ │
│  │       • Add metadata + hint                                │ │
│  └────────────────┬───────────────────────────────────────────┘ │
│                   │                                               │
│  ┌────────────────▼───────────────────────────────────────────┐ │
│  │  6. Return Optimized Response                              │ │
│  │     - 3 results × 100 lines = 300 lines (~8 KB)           │ │
│  │     - Metadata: truncated=true, hint, full_line_count     │ │
│  │     - 70% token reduction achieved                         │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘

Legend:
  [Existing] - No changes to existing components
  [NEW]      - New components/logic added
  [Enhanced] - Existing component with new parameter
```

**Three-System Synergy:**

```
┌──────────────────────┐
│  QueryClassifier     │  (Existing - Reused)
│  - Detects angle     │  
│  - Used for prepends │  ────┐
└──────────────────────┘      │
                              │ Provides
                              │ query angle
┌──────────────────────┐      │
│  Auto-Truncation     │  (New)
│  - Maps angle → lines│  ◄───┘
│  - Truncates smartly │  
│  - Adds metadata     │  ────┐
└──────────────────────┘      │
                              │ Respects
                              │ boundaries
┌──────────────────────┐      │
│  AST Chunking        │  (Existing - Unchanged)
│  - Semantic units    │  ◄───┘
│  - Method boundaries │
│  - Clean structure   │
└──────────────────────┘
```

### 1.2 Architectural Decisions

#### Decision 1: Post-Processing vs. Index-Time Truncation

**Decision:** Implement truncation as post-processing after search, not during indexing

**Rationale:**
- **FR-5 (Backwards Compatibility):** No index rebuild required
- **FR-2 (Explicit Override):** Users can request full chunks with `truncate=False`
- **NFR-1 (Performance):** No impact on search latency or indexing performance
- **Maintainability:** Simpler to implement, test, and debug

**Alternatives Considered:**
- **Index-Time Truncation:** Store multiple versions of each chunk (50/100/150/full lines)
  - **Why Not:** 4x storage cost, complex index management, no flexibility for overrides
- **Modify AST Chunking:** Implement TODO to split at control flow boundaries
  - **Why Not:** Breaks semantic integrity, affects all code search, requires index rebuild

**Trade-offs:**
- **Pros:** 
  - Zero impact on existing system
  - Reversible (can disable with parameter)
  - No index rebuild needed
  - Flexible (per-query control)
- **Cons:**
  - Slight latency increase (<10ms) for truncation processing
  - Full chunks still stored in index (no storage savings)

---

#### Decision 2: Reuse QueryClassifier vs. New Classification

**Decision:** Reuse existing `QueryClassifier` for truncation decisions

**Rationale:**
- **FR-1 (Auto-Truncation):** Already detects query angles (conceptual/location/implementation/critical/troubleshooting)
- **Consistency:** Same classification used for prepends and truncation
- **Simplicity:** No new dependencies, no new training, proven accuracy
- **Integration:** Already integrated in middleware pipeline

**Alternatives Considered:**
- **New ML Classifier:** Train specific model for truncation decisions
  - **Why Not:** Over-engineering, adds complexity, requires training data
- **Rule-Based Heuristics:** Simple keyword matching
  - **Why Not:** Less accurate, harder to maintain, already have better solution

**Trade-offs:**
- **Pros:**
  - Zero new dependencies
  - Proven accuracy (used for prepends)
  - Consistent behavior across features
  - Simple integration
- **Cons:**
  - Tied to classifier accuracy (but <5% misclassification acceptable)
  - Can't optimize specifically for truncation (but current angles work well)

---

#### Decision 3: Smart Boundaries vs. Hard Line Limits

**Decision:** Truncate at natural code boundaries (method/class ends) rather than hard line counts

**Rationale:**
- **FR-3 (Smart Boundaries):** Preserve semantic integrity
- **UX:** Partial methods are confusing and unusable
- **Quality:** Better to return 95 complete lines than 100 lines with half a method

**Alternatives Considered:**
- **Hard Line Limits:** Always truncate at exactly N lines
  - **Why Not:** Breaks semantic integrity, cuts mid-method
- **AST-Based Truncation:** Use Tree-sitter to find exact method boundaries
  - **Why Not:** Over-engineering, simple heuristics work for 95% of cases

**Trade-offs:**
- **Pros:**
  - Preserves semantic integrity
  - Returned code is always valid/complete
  - Better UX (no partial methods)
- **Cons:**
  - Actual truncation point varies (90-110 lines for 100-line target)
  - Slightly more complex logic (backwards search)

---

### 1.3 Requirements Traceability

| Requirement | Architectural Element | How Addressed |
|-------------|----------------------|---------------|
| **FR-1: Auto-Truncation** | QueryClassifier integration | Reuse existing classifier to detect query angle, map to truncation threshold |
| **FR-2: Explicit Override** | `truncate` parameter in API | Accept True/False/int/"auto", override auto-detection |
| **FR-3: Smart Boundaries** | `_find_truncation_point()` | Look backwards 20 lines for method/class boundary |
| **FR-4: Response Metadata** | Metadata enrichment | Add truncated, full_line_count, hint fields to each result |
| **FR-5: Backwards Compat** | Post-processing pattern | No changes to search/indexing, default behavior safe |
| **FR-6: Query Distribution** | Angle-based mapping | Optimize for 80% (conceptual/location), preserve 15% (implementation) |
| **FR-7: Preserve Docstrings** | First-N-lines strategy | First 100 lines typically includes docstrings + signatures |
| **NFR-1: Performance** | Post-processing only | Simple string operations, O(n) complexity, <10ms overhead |
| **NFR-2: Reliability** | Graceful degradation | Classifier failure → default 100 lines, no boundary → use target |
| **NFR-3: Maintainability** | High test coverage | Unit tests for all methods, integration tests for all angles |
| **NFR-4: Observability** | Metrics tracking | Track token reduction, temp file frequency, refinement rate |
| **NFR-5: Usability** | Self-documenting | Metadata includes hints, inline guidance in truncated content |
| **BG-1: Reliability** | 80% temp file reduction | Truncate 80% of queries (conceptual/location) to <30 KB |
| **BG-2: Token Economics** | 70% token reduction | Weighted average: 6,000 → 1,800 tokens per query |
| **BG-3: User Experience** | Zero cognitive overhead | Automatic optimization, self-correcting via metadata |

---

### 1.4 Technology Stack

**Language:** Python 3.11+  
**Type Hints:** `Union[bool, int, str]` for `truncate` parameter  
**Dependencies:** 
- Existing: `QueryClassifier` (middleware/query_classifier.py)
- Existing: `SemanticIndex` (subsystems/rag/code/semantic.py)
- No new external dependencies

**Integration Points:**
- `pos_search_project` tool (tools/pos_search_project.py)
- `QueryClassifier` middleware (middleware/query_classifier.py)
- `PrependGenerator` middleware (middleware/prepend_generator.py)

**Data Structures:**
- Input: Query string, truncate parameter
- Processing: List of search results (dicts)
- Output: Enhanced results with metadata

**Performance:**
- String operations: `split()`, `join()`, slicing
- Complexity: O(n) where n = lines in chunk
- Target: <10ms per query

---

### 1.5 Deployment Architecture

**Deployment Model:** In-process enhancement (no new services)

**Components:**
```
┌─────────────────────────────────────────┐
│  MCP Server (praxis-os)                 │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  pos_search_project Tool           │ │
│  │  - Enhanced with truncation logic  │ │
│  │  - No API changes (new parameter)  │ │
│  └────────────────────────────────────┘ │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  QueryClassifier (Existing)        │ │
│  │  - No changes required             │ │
│  └────────────────────────────────────┘ │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  SemanticIndex (Existing)          │ │
│  │  - No changes required             │ │
│  └────────────────────────────────────┘ │
│                                          │
└─────────────────────────────────────────┘
```

**Deployment Steps:**
1. Add new methods to `pos_search_project.py`
2. Update tool docstring with new parameter
3. No server restart required (hot reload)
4. No index rebuild required
5. No configuration changes required

**Rollback Plan:**
- Set `truncate=False` as default (one-line change)
- Or remove truncation logic (isolated methods)
- No data migration needed

---

## 2. Component Design

### 2.1 Component: TruncationController

**Purpose:** Orchestrates query-aware truncation by determining appropriate truncation thresholds and coordinating with the QueryClassifier

**Responsibilities:**
- Determine truncation threshold based on query angle
- Handle explicit override parameters (True/False/int/"auto")
- Provide graceful degradation if classifier unavailable
- Map query angles to line counts per truncation strategy

**Requirements Satisfied:**
- FR-1: Auto-detect truncation based on query intent
- FR-2: Support explicit override mechanism
- NFR-2: Handle edge cases gracefully (classifier failure, invalid params)

**Public Interface:**
```python
def _determine_truncation(
    self,
    query: str,
    truncate_param: Optional[Union[bool, int, str]]
) -> Optional[int]:
    """Determine truncation line count based on query intent.
    
    Args:
        query: Search query string
        truncate_param: Truncation control (True/False/int/"auto")
        
    Returns:
        Line count to truncate to, or None for no truncation
        
    Examples:
        >>> _determine_truncation("How does X work?", True)
        100  # Conceptual query
        
        >>> _determine_truncation("Where is X?", True)
        50  # Location query
        
        >>> _determine_truncation("How to implement X?", True)
        None  # Implementation query - no truncation
        
        >>> _determine_truncation("Any query", False)
        None  # Explicit override - no truncation
        
        >>> _determine_truncation("Any query", 200)
        200  # Explicit line count
    """
```

**Dependencies:**
- Requires: `QueryClassifier` (existing, via `self.prepend_generator.classifier`)
- Provides: Truncation threshold for `TruncationProcessor`

**Error Handling:**
- Classifier unavailable → Default to 100 lines
- Invalid `truncate_param` type → Raise ValueError with guidance
- Unknown query angle → Default to 100 lines

**Angle Mapping Strategy:**
```python
truncation_map = {
    "conceptual": 100,      # Entry point + overview
    "location": 50,         # Signature only
    "implementation": None, # Full implementation
    "critical": 150,        # Key methods + patterns
    "troubleshooting": None # Error paths + edge cases
}
```

---

### 2.2 Component: TruncationProcessor

**Purpose:** Performs smart truncation at natural code boundaries while preserving semantic integrity

**Responsibilities:**
- Truncate code chunks at method/class boundaries
- Preserve complete docstrings and signatures
- Add metadata to truncated results (status, hints, line counts)
- Generate inline guidance for users

**Requirements Satisfied:**
- FR-3: Smart boundary truncation
- FR-4: Response metadata
- FR-7: Preserve docstrings and signatures
- NFR-1: Performance (<10ms overhead)

**Public Interface:**
```python
def _truncate_code_chunks(
    self,
    results: List[Dict[str, Any]],
    max_lines: int
) -> List[Dict[str, Any]]:
    """Truncate code chunks at smart boundaries.
    
    Args:
        results: List of search results with 'content' field
        max_lines: Maximum lines to include per result
        
    Returns:
        Results with truncated content and metadata
        
    Metadata Added:
        - truncated: bool (True if truncated)
        - full_line_count: int (original line count)
        - truncation_point: int (line where truncated)
        - hint: str (guidance for getting full chunk)
    """

def _find_truncation_point(
    self,
    lines: List[str],
    max_lines: int
) -> int:
    """Find natural truncation point at method boundary.
    
    Strategy:
        - Look backwards up to 20 lines from max_lines
        - Find blank line, 'def ', or 'class ' (method/class boundary)
        - If no boundary found, use max_lines (fallback)
        
    Args:
        lines: List of code lines
        max_lines: Target truncation line
        
    Returns:
        Actual truncation line (natural boundary)
    """
```

**Dependencies:**
- Requires: Search results from `SemanticIndex`
- Provides: Truncated results with metadata

**Error Handling:**
- Chunk smaller than threshold → No truncation, set `truncated=false`
- No natural boundary found → Use max_lines (fallback)
- Empty content → Return unchanged

**Performance Characteristics:**
- Complexity: O(n) where n = lines in chunk
- Operations: String split, slice, join
- Target: <10ms per query (simple string operations)

---

### 2.3 Component: Enhanced SearchCodeHandler

**Purpose:** Integrates truncation into existing code search flow with backwards compatibility

**Responsibilities:**
- Accept new `truncate` parameter in `_handle_search_code`
- Coordinate between search, classification, and truncation
- Apply truncation only to code search (not standards/AST)
- Maintain backwards compatibility (default behavior safe)

**Requirements Satisfied:**
- FR-5: Backwards compatibility
- FR-6: Query distribution optimization
- NFR-5: Usability (self-documenting)

**Public Interface:**
```python
async def _handle_search_code(
    self,
    query: str,
    n_results: int = 3,
    truncate: Union[bool, int, str] = True,  # NEW PARAMETER
    filters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Handle code search with optional truncation.
    
    Args:
        query: Search query
        n_results: Number of results (default: 3)
        truncate: Truncation control (default: True for auto-detect)
            - True: Auto-detect based on query angle
            - False: No truncation (full chunks)
            - int: Explicit line count
            - "auto": Same as True (explicit)
        filters: Optional metadata filters
        
    Returns:
        Search results with optional truncation applied
    """
```

**Dependencies:**
- Requires: `SemanticIndex`, `TruncationController`, `TruncationProcessor`
- Provides: Enhanced search results to MCP client

**Integration Flow:**
1. Execute search (existing logic)
2. If `truncate` enabled and action is "search_code":
   - Determine truncation threshold
   - Apply truncation at smart boundaries
   - Add metadata
3. Return results (with or without truncation)

**Error Handling:**
- Invalid `truncate` parameter → ValueError with examples
- Search failure → Pass through (no truncation applied)
- Truncation failure → Return full chunks with warning

---

### 2.4 Component Interactions

**Interaction Flow:**

```
┌─────────────────────────────────────────────────────────────────┐
│                     MCP Client Request                           │
│  pos_search_project(action="search_code", query="How does X?")  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  Enhanced SearchCodeHandler                                      │
│  1. Parse parameters (truncate=True by default)                  │
│  2. Execute search → SemanticIndex                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  TruncationController                                            │
│  1. Get query angle from QueryClassifier                         │
│  2. Map angle → line count (conceptual → 100)                    │
│  3. Return threshold                                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  TruncationProcessor                                             │
│  1. For each result, find natural boundary                       │
│  2. Truncate at boundary                                         │
│  3. Add metadata (truncated, hint, line counts)                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  Return to MCP Client                                            │
│  - Optimized results (70% token reduction)                       │
│  - Metadata for self-teaching                                    │
└─────────────────────────────────────────────────────────────────┘
```

**Component Communication:**

| From | To | Method | Purpose |
|------|-----|--------|---------|
| SearchCodeHandler | SemanticIndex | `search()` | Execute code search |
| SearchCodeHandler | TruncationController | `_determine_truncation()` | Get truncation threshold |
| TruncationController | QueryClassifier | `classify()` | Get query angle |
| SearchCodeHandler | TruncationProcessor | `_truncate_code_chunks()` | Apply truncation |
| TruncationProcessor | (internal) | `_find_truncation_point()` | Find natural boundary |

---

### 2.5 Module Organization

**File Structure:**
```
.praxis-os/ouroboros/tools/
└── pos_search_project.py
    ├── class POSSearchProject
    │   ├── _handle_search_code()          [Enhanced - new parameter]
    │   ├── _determine_truncation()        [New method]
    │   ├── _truncate_code_chunks()        [New method]
    │   └── _find_truncation_point()       [New method]
    └── [All other methods unchanged]
```

**Design Principles:**
- **Single Responsibility:** Each method has one clear purpose
- **Composition:** TruncationController + TruncationProcessor as logical components (methods, not classes)
- **Backwards Compatibility:** New parameter with safe default
- **Testability:** Pure functions (deterministic, no side effects)

**Dependency Rules:**
- No new external dependencies
- Reuse existing `QueryClassifier` (via `self.prepend_generator.classifier`)
- No circular dependencies
- No changes to `SemanticIndex` or `QueryClassifier`

---

## 3. API Design

### 3.1 MCP Tool API

**Tool Name:** `pos_search_project`

**Action:** `search_code` (enhanced)

**Purpose:** Execute semantic code search with optional query-aware truncation

**Authentication:** MCP session-based (inherited from existing tool)

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `action` | str | Yes | - | Must be "search_code" |
| `query` | str | Yes | - | Search query string |
| `n_results` | int | No | 3 | Number of results to return |
| `truncate` | Union[bool, int, str] | No | `True` | Truncation control (NEW) |
| `filters` | Dict[str, Any] | No | `None` | Optional metadata filters |

**Truncate Parameter Behavior:**

| Value | Type | Behavior | Use Case |
|-------|------|----------|----------|
| `True` | bool | Auto-detect based on query angle (default) | 80% of queries |
| `False` | bool | No truncation, return full chunks | Deep implementation analysis |
| `200` | int | Explicit line count (e.g., 200 lines) | Custom truncation |
| `"auto"` | str | Same as `True` (explicit auto-detect) | Documentation clarity |

**Request Example:**

```python
# Auto-detect truncation (default)
pos_search_project(
    action="search_code",
    query="How does the prepend generator work?"
)

# Explicit override - no truncation
pos_search_project(
    action="search_code",
    query="How to implement suggestion rotation?",
    truncate=False
)

# Explicit line count
pos_search_project(
    action="search_code",
    query="Where is workflow validation?",
    truncate=150
)
```

**Response 200 (Success):**

```json
{
  "status": "success",
  "action": "search_code",
  "results": [
    {
      "content": "[first 100 lines]\n\n... [truncated: 404 more lines]\nUse truncate=False to get full implementation",
      "file_path": "ouroboros/middleware/prepend_generator.py",
      "relevance_score": 0.95,
      "line_range": [46, 550],
      "truncated": true,
      "full_line_count": 504,
      "truncation_point": 100,
      "hint": "Use truncate=False to get full chunk",
      "metadata": {
        "language": "python",
        "_partition": "praxis-os"
      }
    }
  ],
  "count": 3,
  "truncation_reason": {
    "angle": "conceptual",
    "max_lines": 100,
    "override": "Use truncate=False to get full chunks"
  },
  "metadata": {
    "query_tokens": 8,
    "search_time_ms": 45,
    "truncation_time_ms": 3
  }
}
```

**Response 200 (No Truncation):**

```json
{
  "status": "success",
  "action": "search_code",
  "results": [
    {
      "content": "[full 504 lines]",
      "file_path": "ouroboros/middleware/prepend_generator.py",
      "relevance_score": 0.95,
      "line_range": [46, 550],
      "truncated": false,
      "full_line_count": 504,
      "metadata": {
        "language": "python",
        "_partition": "praxis-os"
      }
    }
  ],
  "count": 3,
  "metadata": {
    "query_tokens": 8,
    "search_time_ms": 45
  }
}
```

**Error Response (Invalid Parameter):**

```json
{
  "status": "error",
  "action": "search_code",
  "error": {
    "code": "INVALID_PARAMETER",
    "message": "Invalid truncate parameter: 'invalid'. Must be True, False, int, or 'auto'.",
    "examples": [
      "truncate=True (auto-detect)",
      "truncate=False (no truncation)",
      "truncate=200 (explicit line count)",
      "truncate='auto' (explicit auto-detect)"
    ]
  }
}
```

**Error Response (Search Failure):**

```json
{
  "status": "error",
  "action": "search_code",
  "error": {
    "code": "SEARCH_FAILED",
    "message": "Code search failed: [reason]"
  }
}
```

---

### 3.2 Internal Interfaces

#### Interface: TruncationController

**Method:** `_determine_truncation`

```python
def _determine_truncation(
    self,
    query: str,
    truncate_param: Optional[Union[bool, int, str]]
) -> Optional[int]:
    """Determine truncation line count based on query intent.
    
    Args:
        query: Search query string
        truncate_param: Truncation control (True/False/int/"auto")
        
    Returns:
        Line count to truncate to, or None for no truncation
        
    Raises:
        ValueError: If truncate_param is invalid type
        
    Examples:
        >>> _determine_truncation("How does X work?", True)
        100  # Conceptual query
        
        >>> _determine_truncation("Where is X?", True)
        50  # Location query
        
        >>> _determine_truncation("How to implement X?", True)
        None  # Implementation query - no truncation
        
        >>> _determine_truncation("Any query", False)
        None  # Explicit override
        
        >>> _determine_truncation("Any query", 200)
        200  # Explicit line count
        
        >>> _determine_truncation("Any query", "invalid")
        ValueError: Invalid truncate parameter
    """
```

**Contract:**
- MUST handle all parameter types (bool, int, str, None)
- MUST return int or None (never other types)
- MUST default to 100 if classifier fails
- MUST raise ValueError for invalid types

---

#### Interface: TruncationProcessor

**Method:** `_truncate_code_chunks`

```python
def _truncate_code_chunks(
    self,
    results: List[Dict[str, Any]],
    max_lines: int
) -> List[Dict[str, Any]]:
    """Truncate code chunks at smart boundaries.
    
    Args:
        results: List of search results with 'content' field
        max_lines: Maximum lines to include per result
        
    Returns:
        Results with truncated content and metadata
        
    Metadata Added:
        - truncated: bool (True if truncated)
        - full_line_count: int (original line count)
        - truncation_point: int (line where truncated)
        - hint: str (guidance for getting full chunk)
        
    Examples:
        >>> results = [{"content": "500 lines of code..."}]
        >>> _truncate_code_chunks(results, max_lines=100)
        [{"content": "100 lines...", "truncated": True, ...}]
    """
```

**Contract:**
- MUST preserve all existing fields in results
- MUST add metadata fields (truncated, full_line_count, truncation_point, hint)
- MUST truncate at natural boundaries (method/class ends)
- MUST handle chunks smaller than max_lines (no truncation)
- MUST handle empty content gracefully

---

**Method:** `_find_truncation_point`

```python
def _find_truncation_point(
    self,
    lines: List[str],
    max_lines: int
) -> int:
    """Find natural truncation point at method boundary.
    
    Args:
        lines: List of code lines
        max_lines: Target truncation line
        
    Returns:
        Actual truncation line (natural boundary)
        
    Algorithm:
        1. Start at max_lines
        2. Look backwards up to 20 lines
        3. Find blank line, 'def ', or 'class '
        4. Return boundary line
        5. If no boundary, return max_lines (fallback)
        
    Examples:
        >>> lines = ["def foo():", "    pass", "", "def bar():"]
        >>> _find_truncation_point(lines, max_lines=3)
        2  # Blank line after foo()
    """
```

**Contract:**
- MUST return int in range [max(0, max_lines-20), max_lines]
- MUST look backwards from max_lines
- MUST recognize language-specific boundaries (def, class for Python)
- MUST fallback to max_lines if no boundary found

---

### 3.3 Data Transfer Objects

#### Result Metadata (Enhanced)

```python
@dataclass
class SearchResult:
    """Enhanced search result with truncation metadata."""
    
    # Existing fields (unchanged)
    content: str
    file_path: str
    relevance_score: float
    line_range: Tuple[int, int]
    metadata: Dict[str, Any]
    
    # New fields (added)
    truncated: bool = False
    full_line_count: Optional[int] = None
    truncation_point: Optional[int] = None
    hint: Optional[str] = None
```

#### Truncation Reason

```python
@dataclass
class TruncationReason:
    """Metadata about why/how truncation was applied."""
    
    angle: str  # Query angle (conceptual/location/implementation/critical/troubleshooting)
    max_lines: int  # Truncation threshold applied
    override: str  # Guidance for getting full chunks
```

#### Response Metadata (Enhanced)

```python
@dataclass
class ResponseMetadata:
    """Enhanced response metadata with truncation timing."""
    
    # Existing fields
    query_tokens: int
    search_time_ms: int
    
    # New fields (optional)
    truncation_time_ms: Optional[int] = None  # Only if truncation applied
```

---

### 3.4 Error Handling

**Error Codes:**

| Code | HTTP Status | Trigger | Message Format |
|------|-------------|---------|----------------|
| `INVALID_PARAMETER` | 400 | Invalid `truncate` parameter type | "Invalid truncate parameter: {value}. Must be True, False, int, or 'auto'." |
| `SEARCH_FAILED` | 500 | Search execution failure | "Code search failed: {reason}" |
| `TRUNCATION_FAILED` | 500 | Truncation processing failure | "Truncation failed: {reason}. Returning full chunks." |
| `CLASSIFIER_UNAVAILABLE` | 200 (Warning) | QueryClassifier unavailable | "Classifier unavailable, defaulting to 100 lines" |

**Error Response Format:**

```json
{
  "status": "error",
  "action": "search_code",
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {},
    "remediation": "Suggested fix or workaround"
  }
}
```

**Graceful Degradation:**

- **Classifier Failure:** Default to 100 lines, log warning, continue
- **Truncation Failure:** Return full chunks, log error, include warning in response
- **Invalid Parameter:** Return error with examples, do not execute search

---

### 3.5 Backwards Compatibility

**Existing API (Unchanged):**

```python
# All existing calls work without modification
pos_search_project(
    action="search_code",
    query="How does X work?",
    n_results=3
)
# Now applies auto-truncation by default (truncate=True)
```

**Response Structure (Backwards Compatible):**

- All existing fields preserved
- New fields added (truncated, full_line_count, etc.)
- Clients ignoring new fields continue to work
- No breaking changes to response structure

**Migration Path:**

- **Phase 1:** Deploy with `truncate=True` as default (auto-detect)
- **Phase 2:** Monitor metrics (token reduction, temp file frequency)
- **Phase 3:** Adjust thresholds based on data
- **Rollback:** Change default to `truncate=False` (one-line change)

---

## 4. Data Models

### 4.1 Domain Models

This feature enhances existing search results with truncation metadata. No new persistent data models are introduced.

#### Enhanced Search Result

```python
# Existing structure (unchanged)
SearchResult = Dict[str, Any]  # From SemanticIndex

# Enhanced with truncation metadata (new fields added)
{
    # Existing fields (preserved)
    "content": str,              # Code chunk content
    "file_path": str,            # Source file path
    "relevance_score": float,    # Search relevance (0.0-1.0)
    "line_range": Tuple[int, int],  # [start_line, end_line]
    "metadata": {
        "language": str,         # Programming language
        "_partition": str        # Partition identifier
    },
    
    # New fields (added by truncation)
    "truncated": bool,           # True if content was truncated
    "full_line_count": int,      # Original line count before truncation
    "truncation_point": int,     # Line where truncation occurred
    "hint": str                  # User guidance for getting full chunk
}
```

**Business Rules:**
- `truncated=False` → `full_line_count`, `truncation_point`, `hint` are `None`
- `truncated=True` → All metadata fields must be present
- `truncation_point` ≤ `full_line_count`
- `truncation_point` in range `[max(0, max_lines-20), max_lines]` (smart boundary)
- `hint` always includes "Use truncate=False to get full chunk"

---

#### Truncation Configuration

```python
# Angle-to-threshold mapping (static configuration)
TRUNCATION_MAP = {
    "conceptual": 100,      # Entry point + overview
    "location": 50,         # Signature only
    "implementation": None, # Full implementation (no truncation)
    "critical": 150,        # Key methods + patterns
    "troubleshooting": None # Error paths (no truncation)
}

# Default fallback
DEFAULT_TRUNCATION = 100  # Used when angle unknown or classifier fails
```

**Business Rules:**
- `None` value means no truncation (return full chunk)
- All thresholds are line counts (not token counts)
- Thresholds are targets, actual truncation may vary ±20 lines (smart boundaries)
- Configuration is static (no runtime modification in MVP)

---

#### Response Metadata

```python
# Enhanced response metadata
{
    "status": "success",
    "action": "search_code",
    "results": List[SearchResult],  # Enhanced with truncation metadata
    "count": int,                    # Number of results
    
    # New: Truncation reason (only if truncation applied)
    "truncation_reason": {
        "angle": str,                # Detected query angle
        "max_lines": int,            # Threshold applied
        "override": str              # Guidance for users
    },
    
    # Enhanced: Response metadata
    "metadata": {
        "query_tokens": int,
        "search_time_ms": int,
        "truncation_time_ms": int    # New: truncation overhead
    }
}
```

**Business Rules:**
- `truncation_reason` only present if at least one result was truncated
- `truncation_time_ms` only present if truncation was applied
- `angle` must be one of: conceptual, location, implementation, critical, troubleshooting
- `max_lines` matches value from `TRUNCATION_MAP[angle]`

---

### 4.2 Data Flow

**Input Data:**
```python
{
    "action": "search_code",
    "query": "How does X work?",
    "n_results": 3,
    "truncate": True  # or False, int, "auto"
}
```

**Intermediate Data (from SemanticIndex):**
```python
[
    {
        "content": "500 lines of code...",
        "file_path": "path/to/file.py",
        "relevance_score": 0.95,
        "line_range": [46, 550],
        "metadata": {"language": "python", "_partition": "praxis-os"}
    },
    # ... 2 more results
]
```

**Processing Data (truncation decision):**
```python
{
    "query_angle": "conceptual",     # From QueryClassifier
    "truncation_threshold": 100,     # From TRUNCATION_MAP
    "truncate_enabled": True         # From parameter
}
```

**Output Data (enhanced results):**
```python
[
    {
        "content": "100 lines...\n\n... [truncated: 400 more lines]\n...",
        "file_path": "path/to/file.py",
        "relevance_score": 0.95,
        "line_range": [46, 550],
        "metadata": {"language": "python", "_partition": "praxis-os"},
        "truncated": True,
        "full_line_count": 500,
        "truncation_point": 98,  # Smart boundary (not exactly 100)
        "hint": "Use truncate=False to get full chunk"
    },
    # ... 2 more results
]
```

---

### 4.3 State Management

**No Persistent State:**
- Truncation is stateless (no database, no cache)
- Each request is independent
- No session state required
- No state synchronization needed

**Transient State (per-request):**
```python
# Request lifecycle state
{
    "query": str,                    # User query
    "truncate_param": Union[...],    # User parameter
    "query_angle": str,              # Detected angle
    "truncation_threshold": int,     # Computed threshold
    "search_results": List[Dict],    # From SemanticIndex
    "truncated_results": List[Dict], # After processing
    "start_time": float,             # For timing
    "truncation_time": float         # Truncation overhead
}
```

**Lifecycle:**
1. **Request Start:** Parse parameters, validate `truncate` param
2. **Search:** Execute semantic search (existing logic)
3. **Classify:** Detect query angle (if `truncate=True`)
4. **Determine:** Map angle → threshold
5. **Truncate:** Process each result at smart boundaries
6. **Enhance:** Add metadata to results
7. **Return:** Send enhanced response
8. **Cleanup:** All state discarded (no persistence)

---

### 4.4 Validation Rules

#### Input Validation

**`truncate` Parameter:**
```python
# Valid values
truncate in [True, False, "auto"]  # Boolean or string
isinstance(truncate, int) and truncate > 0  # Positive integer

# Invalid values
truncate in [None, "", "invalid", -1, 0, 1.5]
→ Raise ValueError with examples
```

**`query` Parameter:**
```python
# Valid
len(query) > 0 and isinstance(query, str)

# Invalid
query in [None, "", "   "]
→ Raise ValueError: "Query cannot be empty"
```

#### Output Validation

**Truncated Result:**
```python
if result["truncated"] == True:
    assert result["full_line_count"] > 0
    assert result["truncation_point"] > 0
    assert result["truncation_point"] <= result["full_line_count"]
    assert result["hint"] is not None
    assert "truncate=False" in result["hint"]
```

**Non-Truncated Result:**
```python
if result["truncated"] == False:
    assert result["full_line_count"] == len(result["content"].split("\n"))
    assert result["truncation_point"] is None
    assert result["hint"] is None
```

#### Boundary Validation

**Smart Truncation Point:**
```python
# Truncation point must be within tolerance
assert max_lines - 20 <= truncation_point <= max_lines

# Content must match truncation point
assert len(result["content"].split("\n")) == truncation_point
```

---

### 4.5 Data Constraints

**Performance Constraints:**
- Truncation processing: <10ms per query
- Memory overhead: Minimal (string slicing, no copies)
- No database queries (all in-memory)

**Size Constraints:**
- Input query: No explicit limit (reasonable queries <1KB)
- Chunk size: Handled by existing AST chunking (500-2,000+ lines)
- Response size: Reduced by 70% average (goal: <30 KB per query)

**Concurrency Constraints:**
- Stateless design: No locking required
- Thread-safe: Pure functions, no shared mutable state
- Concurrent requests: Independent processing

---

## 5. Security Design

### 5.1 Security Context

This feature is a **post-processing enhancement** to existing search functionality. It inherits all security controls from the existing `pos_search_project` tool and MCP server infrastructure.

**Security Posture:**
- **No new attack surface:** No new endpoints, no new authentication
- **No sensitive data:** Processes code chunks (already accessible via search)
- **No privilege escalation:** Same permissions as existing search
- **No data persistence:** Stateless processing, no storage

---

### 5.2 Authentication & Authorization

**Inherited from Existing System:**

**Authentication:**
- MCP session-based authentication (existing)
- No changes to authentication mechanism
- No new credentials or tokens

**Authorization:**
- Same permissions as `pos_search_project` tool
- If user can search code, they can use truncation
- No additional authorization checks required

**Access Control:**
- Truncation parameter is user-controlled (no privilege implications)
- `truncate=False` does not grant additional access (returns same data as before)
- `truncate=True` reduces data returned (more restrictive, not less)

---

### 5.3 Input Validation

**Parameter Validation:**

**`truncate` Parameter:**
```python
# Strict type checking
if not isinstance(truncate, (bool, int, str, type(None))):
    raise ValueError(
        f"Invalid truncate parameter type: {type(truncate)}. "
        "Must be bool, int, or str."
    )

# Value validation
if isinstance(truncate, str) and truncate not in ["auto"]:
    raise ValueError(
        f"Invalid truncate string value: {truncate}. "
        "Must be 'auto'."
    )

if isinstance(truncate, int) and truncate <= 0:
    raise ValueError(
        f"Invalid truncate line count: {truncate}. "
        "Must be positive integer."
    )
```

**`query` Parameter:**
```python
# Inherited from existing search validation
# No additional validation needed for truncation
```

**Protection Against:**
- **Type confusion:** Strict type checking prevents unexpected types
- **Integer overflow:** Python handles large integers safely
- **Injection attacks:** No SQL/command execution, pure string processing
- **Path traversal:** No file system access in truncation logic

---

### 5.4 Data Protection

**Data Handling:**

**In Transit:**
- Inherited from MCP protocol (existing encryption)
- No additional data transmission
- Response size reduced (less data exposure)

**In Memory:**
- Transient processing only (no persistence)
- String slicing (no data copying)
- Automatic garbage collection after response

**In Logs:**
- Log truncation decisions (angle, threshold)
- Do NOT log full code content
- Do NOT log sensitive query details

**Example Safe Logging:**
```python
logger.info(
    "Truncation applied",
    extra={
        "angle": "conceptual",
        "threshold": 100,
        "results_truncated": 3,
        "token_reduction": 0.72
    }
)
# Do NOT log: query text, code content, file paths
```

---

### 5.5 Denial of Service (DoS) Protection

**Resource Limits:**

**CPU:**
- Truncation is O(n) where n = lines in chunk
- Bounded by existing chunk sizes (500-2,000 lines)
- Worst case: ~10ms per query (acceptable)

**Memory:**
- No additional memory allocation (string slicing)
- No unbounded data structures
- No recursion (iterative algorithms)

**Mitigation:**
- Inherit rate limiting from existing MCP server
- No additional DoS vectors introduced
- Truncation actually reduces resource usage (smaller responses)

**Attack Scenarios:**
```python
# Scenario 1: Large truncate value
truncate=1000000  # User requests huge truncation
→ Bounded by actual chunk size (max 2,000 lines)
→ No additional resource consumption

# Scenario 2: Rapid requests
# Multiple truncation requests in quick succession
→ Inherit existing rate limiting
→ Stateless design prevents resource exhaustion

# Scenario 3: Malicious query
query="<script>alert('xss')</script>"
→ Query passed to existing search (already validated)
→ No additional XSS risk in truncation logic
```

---

### 5.6 Information Disclosure

**Risk Assessment:**

**Reduced Information Disclosure:**
- Truncation **reduces** data returned (80% less for conceptual queries)
- Users get **less** information by default, not more
- `truncate=False` returns same data as before (no new disclosure)

**Metadata Disclosure:**
```python
# Metadata added by truncation
{
    "truncated": true,
    "full_line_count": 504,
    "truncation_point": 100,
    "hint": "Use truncate=False..."
}
```

**Risk:** Reveals full chunk size before truncation  
**Mitigation:** User already has access to full chunk (can request with `truncate=False`)  
**Severity:** Low (no additional information disclosed)

**Query Angle Disclosure:**
```python
{
    "truncation_reason": {
        "angle": "conceptual",  # Reveals how query was classified
        "max_lines": 100
    }
}
```

**Risk:** Reveals query classification  
**Mitigation:** Classification is deterministic (user can infer from query)  
**Severity:** Very Low (no sensitive information)

---

### 5.7 Code Injection Prevention

**No Code Execution:**
- Truncation is pure string processing (no `eval`, no `exec`)
- No dynamic code generation
- No template rendering with user input
- No shell command execution

**Safe String Operations:**
```python
# Safe operations only
lines = content.split("\n")          # String split
truncated = "\n".join(lines[:100])   # String join
hint = f"Use truncate=False..."      # F-string (safe, no eval)
```

**No Risk Of:**
- SQL injection (no database queries)
- Command injection (no shell execution)
- Code injection (no eval/exec)
- Template injection (no template rendering)

---

### 5.8 Security Testing

**Test Cases:**

**Input Validation Tests:**
- TC-SEC-1: Invalid `truncate` type → ValueError
- TC-SEC-2: Negative `truncate` value → ValueError
- TC-SEC-3: Invalid string value → ValueError
- TC-SEC-4: Large `truncate` value → Bounded by chunk size

**DoS Protection Tests:**
- TC-SEC-5: 1000 rapid requests → Rate limiting applied
- TC-SEC-6: Extremely large query → Handled by existing validation
- TC-SEC-7: Concurrent requests → No resource exhaustion

**Information Disclosure Tests:**
- TC-SEC-8: Truncated response → No sensitive data in metadata
- TC-SEC-9: Error messages → No stack traces or internal paths
- TC-SEC-10: Logs → No code content or sensitive query details

**Injection Prevention Tests:**
- TC-SEC-11: Query with special characters → Safe processing
- TC-SEC-12: Query with SQL syntax → No SQL execution
- TC-SEC-13: Query with shell commands → No shell execution

---

### 5.9 Security Monitoring

**Metrics to Track:**

**Usage Patterns:**
- Truncation parameter distribution (True/False/int)
- Query angle distribution (conceptual/location/implementation)
- Average truncation threshold applied

**Anomaly Detection:**
- Unusual `truncate` values (e.g., always `False`)
- High rate of explicit overrides (may indicate UX issue)
- Classifier failures (may indicate attack or bug)

**Audit Logging:**
```python
# Log truncation decisions (not content)
{
    "event": "search_truncation_applied",
    "timestamp": "2025-11-16T14:30:00Z",
    "session_id": "abc123",
    "angle": "conceptual",
    "threshold": 100,
    "results_truncated": 3,
    "token_reduction": 0.72
}
```

**Do NOT Log:**
- Full query text (may contain sensitive search terms)
- Code content (may contain secrets or PII)
- File paths (may reveal internal structure)

---

### 5.10 Compliance Considerations

**Data Privacy:**
- No PII processed by truncation logic
- No data retention (stateless processing)
- No cross-user data leakage (isolated requests)

**GDPR/Privacy:**
- Right to access: Truncation does not affect (user can request full chunks)
- Right to deletion: Not applicable (no data stored)
- Data minimization: Truncation **improves** compliance (less data transmitted)

**Security Standards:**
- OWASP Top 10: No new vulnerabilities introduced
- CWE Top 25: No relevant weaknesses
- SANS Top 25: No relevant vulnerabilities

---

### 5.11 Security Review Checklist

- [x] **Authentication:** Inherited from existing system, no changes
- [x] **Authorization:** Same permissions as existing search
- [x] **Input Validation:** Strict type and value checking
- [x] **Output Encoding:** Not applicable (JSON response, no rendering)
- [x] **Injection Prevention:** No code execution, safe string operations
- [x] **DoS Protection:** Bounded resource usage, inherit rate limiting
- [x] **Information Disclosure:** Reduced data exposure, safe metadata
- [x] **Logging:** Safe logging (no sensitive data)
- [x] **Error Handling:** No stack traces or internal details in errors
- [x] **Cryptography:** Not applicable (no encryption needed)
- [x] **Session Management:** Inherited from MCP server
- [x] **File Upload:** Not applicable
- [x] **API Security:** Inherited from existing tool

**Security Posture:** ✅ **LOW RISK**

- No new attack surface
- No sensitive data processing
- No privilege escalation
- Reduces data exposure (70% less data transmitted)

---

## 6. Performance Design

### 6.1 Performance Targets

**From Requirements (NFR-1):**
- **Truncation Overhead:** <10ms per query (95th percentile)
- **Search Latency:** No impact on existing search performance
- **Memory Overhead:** Minimal (no additional allocations)
- **Throughput:** No degradation from current baseline

**Success Criteria:**
```python
# Performance benchmarks
assert truncation_time_p95 < 10  # milliseconds
assert memory_overhead < 1  # MB per request
assert throughput_degradation < 0.05  # 5% max
```

---

### 6.2 Optimization Strategies

#### 6.2.1 Algorithm Optimization

**String Operations:**
```python
# Efficient string processing
lines = content.split("\n")  # O(n) - single pass
truncated = lines[:truncation_point]  # O(1) - slice (view, not copy)
result = "\n".join(truncated)  # O(n) - single pass

# Total: O(n) where n = lines in chunk
# Bounded: n ≤ 2,000 lines (existing chunk limit)
# Expected: ~3ms for 500-line chunk
```

**Boundary Detection:**
```python
# Backwards search (limited range)
for i in range(max_lines, max(0, max_lines - 20), -1):
    # O(20) worst case - constant time
    if is_boundary(lines[i]):
        return i

# Total: O(20) = O(1) constant time
# Expected: <1ms
```

**Total Truncation Time:**
- String split: ~2ms
- Boundary detection: ~1ms
- String join: ~2ms
- Metadata creation: ~1ms
- **Total: ~6ms (well under 10ms target)**

---

#### 6.2.2 Memory Optimization

**No Additional Allocations:**
```python
# Efficient memory usage
lines = content.split("\n")  # Creates list of string views (minimal)
truncated = lines[:100]  # Slice creates view, not copy
result = "\n".join(truncated)  # Single allocation for result

# Memory overhead: ~1 KB for metadata dict
# No deep copies, no caching, no persistence
```

**Garbage Collection:**
- Transient objects only (request-scoped)
- Automatic cleanup after response
- No memory leaks (no circular references)

---

#### 6.2.3 Concurrency Optimization

**Stateless Design:**
- No shared mutable state
- No locking required
- Thread-safe by design
- Independent request processing

**Parallel Execution:**
```python
# Each result can be truncated independently
for result in results:  # Can be parallelized if needed
    truncate_result(result)

# Current: Sequential (sufficient for n=3 results)
# Future: Parallel processing if n_results increases
```

---

### 6.3 Performance Monitoring

**Metrics to Track:**

**Latency Metrics:**
```python
{
    "truncation_time_ms": float,  # Per-query truncation overhead
    "truncation_time_p50": float,  # Median
    "truncation_time_p95": float,  # 95th percentile
    "truncation_time_p99": float,  # 99th percentile
    "search_time_ms": float,       # Existing search latency
    "total_time_ms": float         # End-to-end latency
}
```

**Throughput Metrics:**
```python
{
    "queries_per_second": float,      # Overall throughput
    "truncated_queries_pct": float,   # % of queries truncated
    "avg_token_reduction": float,     # Average token savings
    "temp_file_frequency": float      # % of queries triggering temp files
}
```

**Resource Metrics:**
```python
{
    "memory_overhead_mb": float,      # Memory per request
    "cpu_overhead_pct": float,        # CPU increase from truncation
    "response_size_kb": float         # Average response size
}
```

---

### 6.4 Performance Testing

**Test Scenarios:**

**Scenario 1: Small Chunks (< threshold)**
```python
# Input: 50-line chunk, threshold=100
# Expected: No truncation, <1ms overhead
# Validation: truncated=False, time <1ms
```

**Scenario 2: Medium Chunks (~ threshold)**
```python
# Input: 500-line chunk, threshold=100
# Expected: Truncation at boundary, ~6ms
# Validation: truncated=True, time <10ms
```

**Scenario 3: Large Chunks (>> threshold)**
```python
# Input: 2000-line chunk, threshold=100
# Expected: Truncation at boundary, ~8ms
# Validation: truncated=True, time <10ms
```

**Scenario 4: Multiple Results**
```python
# Input: 3 results × 500 lines each
# Expected: All truncated, ~18ms total
# Validation: 3 truncated, time <30ms
```

**Scenario 5: Concurrent Requests**
```python
# Input: 100 concurrent queries
# Expected: No throughput degradation
# Validation: p95 latency <10ms, no errors
```

---

### 6.5 Scalability Considerations

**Current Scale:**
- Queries per day: ~1,000 (estimated)
- Concurrent users: ~10 (estimated)
- Response size: 40-60 KB → 8-18 KB (70% reduction)

**Future Scale (10x growth):**
- Queries per day: ~10,000
- Concurrent users: ~100
- Truncation overhead: Still <10ms (O(n) with bounded n)

**Bottlenecks:**
- **Not truncation:** Truncation is O(n) with small n (bounded by chunk size)
- **Search itself:** Existing semantic search is the bottleneck
- **Network:** Response transmission (reduced by 70% with truncation)

**Scaling Strategy:**
- **Horizontal:** Stateless design enables easy horizontal scaling
- **Vertical:** Not needed (truncation overhead is minimal)
- **Caching:** Not applicable (stateless, no repeated queries)

---

### 6.6 Performance Regression Prevention

**Baseline Metrics (Before Truncation):**
```python
{
    "search_time_p95": 45,  # ms
    "response_size_avg": 40,  # KB
    "queries_per_second": 50,
    "memory_per_request": 5  # MB
}
```

**Target Metrics (After Truncation):**
```python
{
    "search_time_p95": 45,  # ms (no change)
    "truncation_time_p95": 10,  # ms (new overhead)
    "total_time_p95": 55,  # ms (search + truncation)
    "response_size_avg": 12,  # KB (70% reduction)
    "queries_per_second": 48,  # (5% acceptable degradation)
    "memory_per_request": 5  # MB (no change)
}
```

**Regression Tests:**
```python
# Run before deployment
assert total_time_p95 < baseline_search_time_p95 * 1.25  # Max 25% increase
assert response_size_avg < baseline_response_size * 0.35  # Min 65% reduction
assert queries_per_second > baseline_qps * 0.95  # Max 5% degradation
```

---

### 6.7 Performance Optimization Roadmap

**Phase 1 (MVP - Current):**
- ✅ O(n) truncation algorithm
- ✅ Smart boundary detection
- ✅ Minimal memory overhead
- ✅ Stateless design

**Phase 2 (Future Optimizations):**
- Parallel result truncation (if n_results increases)
- Cached truncation points (if same chunks queried repeatedly)
- Adaptive thresholds (learn from usage patterns)
- Streaming truncation (for very large chunks)

**Phase 3 (Advanced):**
- GPU-accelerated boundary detection (if needed)
- Predictive truncation (pre-truncate during indexing)
- Compression (gzip truncated responses)

**Current Assessment:** Phase 1 is sufficient for expected load

---

### 6.8 Performance SLIs (Service Level Indicators)

**Latency SLIs:**
- **P50 (Median):** <5ms truncation overhead
- **P95:** <10ms truncation overhead
- **P99:** <15ms truncation overhead

**Throughput SLIs:**
- **Queries/sec:** >45 (5% degradation acceptable)
- **Token reduction:** >65% average
- **Temp file frequency:** <10% of queries

**Resource SLIs:**
- **Memory overhead:** <1 MB per request
- **CPU overhead:** <5% increase
- **Response size:** <15 KB average (down from 40 KB)

**Monitoring & Alerts:**
```python
# Warning alerts
if truncation_time_p95 > 10:
    alert("Truncation latency exceeds target")

if token_reduction_avg < 0.65:
    alert("Token reduction below target")

if temp_file_frequency > 0.10:
    alert("Temp file frequency above target")

# Critical alerts
if truncation_time_p95 > 20:
    alert("CRITICAL: Truncation latency 2x target")

if queries_per_second < 40:
    alert("CRITICAL: Throughput degradation >20%")
```

---

### 6.9 Performance Validation

**Pre-Deployment Checklist:**
- [ ] Benchmark truncation overhead: <10ms p95
- [ ] Load test: 100 concurrent queries, no degradation
- [ ] Memory profiling: No leaks, <1 MB overhead
- [ ] Regression test: Total latency <25% increase
- [ ] Token reduction: >65% average achieved
- [ ] Temp file frequency: <10% of queries

**Post-Deployment Monitoring:**
- Monitor truncation_time_p95 for 7 days
- Track token_reduction_avg daily
- Alert on temp_file_frequency spikes
- Review query_angle distribution weekly

**Success Criteria:**
- ✅ 70% token reduction achieved
- ✅ <10ms truncation overhead
- ✅ <5% throughput degradation
- ✅ 80% temp file reduction

---


