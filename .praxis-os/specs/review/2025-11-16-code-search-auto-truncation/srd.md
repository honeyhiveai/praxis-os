# Software Requirements Document (SRD)
## Code Search Auto-Truncation with Query-Aware Response Sizing

**Date:** 2025-11-16  
**Status:** Draft  
**Priority:** P0 (Critical Reliability & Performance)

---

## 1. Business Goals

### 1.1 Primary Objectives

**BG-1: Improve System Reliability**
- **Goal:** Eliminate client crashes and temp file workarounds caused by large code search responses
- **Current State:** 40-60 KB responses trigger temp file writes in Cursor and crash Cline sessions
- **Target State:** <8% of queries trigger temp files (only when explicitly needed for deep implementation queries)
- **Impact:** 80% reduction in temp file occurrences (from 40% to 8% of queries)
- **Rationale:** System reliability is foundational - crashes and workarounds undermine user trust and productivity

**BG-2: Optimize Token Economics**
- **Goal:** Reduce token waste in code search responses
- **Current State:** 6,000 tokens average per query, 80% of content unused for typical queries
- **Target State:** 1,800 tokens average per query (70% reduction)
- **Impact:** 3.4x more queries per 200K context window (33 → 111 queries)
- **Rationale:** Token efficiency directly impacts cost, performance, and context window longevity

**BG-3: Enhance User Experience**
- **Goal:** Provide right-sized responses based on query intent
- **Current State:** All queries get full implementations (500+ lines), AI scrolls through noise
- **Target State:** Automatic optimization - conceptual queries get overviews, implementation queries get full details
- **Impact:** Zero cognitive overhead for AI agents (automatic, self-correcting)
- **Rationale:** Better UX encourages query-first behavior and reduces friction

### 1.2 Success Metrics

| Metric | Current | Target | Measurement Method |
|--------|---------|--------|-------------------|
| **Avg tokens per query** | 6,000 | 1,800 | Token counter in response metadata |
| **Temp file frequency** | 40% | 8% | Track file writes per query |
| **Queries per context window** | 33 | 111 | 200K window ÷ avg tokens |
| **Query refinement rate** | N/A | 15% | Track `truncate=False` after truncated response |
| **Misclassification rate** | N/A | <5% | Track immediate full chunk requests |
| **Test coverage** | N/A | >90% | Unit + integration test coverage |
| **Performance overhead** | N/A | <10ms | Truncation latency measurement |

### 1.3 Business Value

**Quantified Impact:**
- **Cost Reduction:** 70% fewer tokens per query = 70% cost reduction for code search
- **Productivity Gain:** 3.4x more queries per context = longer sessions, fewer resets
- **Reliability Improvement:** 80% fewer temp files = smoother workflow, fewer interruptions
- **Behavioral Reinforcement:** Self-correcting system teaches better querying patterns

**Strategic Alignment:**
- Supports prAxIs OS mission: "External memory architecture" (filesystem over context)
- Reinforces "query liberally" pattern (more queries, less per query)
- Demonstrates behavioral engineering (system teaches optimal usage)

---

## 2. User Stories

### US-1: AI Agent Exploring Codebase (Conceptual Query)

**As an** AI agent exploring a new codebase  
**I want** high-level overviews of code components (entry point + algorithm)  
**So that** I can understand the system architecture without drowning in implementation details

**Acceptance Criteria:**
- Query like "How does X work?" returns ~100 lines per result
- Response includes: class docstring, `__init__`, main method signature + algorithm
- Response does NOT include: all helper methods, full implementations
- Metadata indicates truncation and how to get full content
- 80-90% of information need satisfied without follow-up

**Current Pain:** Gets 500+ lines per result, 80% unused, wastes tokens and attention

**Priority:** P0 (60% of queries)

---

### US-2: AI Agent Locating Functionality (Location Query)

**As an** AI agent searching for where functionality is implemented  
**I want** just the file path and signature  
**So that** I can quickly locate the code without reading full implementations

**Acceptance Criteria:**
- Query like "Where is X implemented?" returns ~50 lines per result
- Response includes: file path, class/function signature, docstring
- Response does NOT include: implementation body, helper methods
- Metadata indicates truncation and how to get full content
- File location and signature sufficient to answer query

**Current Pain:** Gets 500+ lines when only need location + signature

**Priority:** P0 (20% of queries)

---

### US-3: AI Agent Implementing Feature (Implementation Query)

**As an** AI agent implementing a new feature  
**I want** complete code implementations with all details  
**So that** I can understand the full algorithm, edge cases, and patterns

**Acceptance Criteria:**
- Query like "How to implement X?" returns full chunks (no truncation)
- Response includes: complete implementation, all helper methods, error handling
- No truncation applied (full 500+ lines)
- Metadata indicates no truncation applied
- All implementation details available for deep analysis

**Current Pain:** None - current behavior is correct for this use case

**Priority:** P0 (15% of queries, but critical when needed)

---

### US-4: AI Agent Debugging Issue (Troubleshooting Query)

**As an** AI agent debugging an issue  
**I want** full implementations including error paths  
**So that** I can understand edge cases and failure modes

**Acceptance Criteria:**
- Query like "Common X mistakes?" returns full chunks (no truncation)
- Response includes: complete implementation, error handling, edge cases
- No truncation applied
- All error paths and edge cases visible

**Current Pain:** None - current behavior is correct for this use case

**Priority:** P1 (2% of queries, critical for debugging)

---

### US-5: AI Agent Refining Query (Iterative Refinement)

**As an** AI agent who received truncated results  
**I want** clear guidance on how to get full implementations  
**So that** I can refine my query if I need more details

**Acceptance Criteria:**
- Truncated responses include inline hint: "Use truncate=False to get full implementation"
- Response metadata includes `truncation_reason` with detected angle
- AI can override with `truncate=False` or `truncate=200` (explicit line count)
- System teaches optimal query patterns through metadata

**Current Pain:** No guidance on how to get more details if needed

**Priority:** P1 (self-teaching system, behavioral reinforcement)

---

## 3. Functional Requirements

### FR-1: Query-Aware Auto-Truncation

**Requirement:** System SHALL automatically detect query intent and apply appropriate truncation

**Specification:**
- Use existing `QueryClassifier` to detect query angle (conceptual/location/implementation/critical/troubleshooting)
- Map angle to truncation threshold:
  - Conceptual (📖): 100 lines
  - Location (📍): 50 lines
  - Implementation (🔧): None (full chunk)
  - Critical (⭐): 150 lines
  - Troubleshooting (⚠️): None (full chunk)
- Default to 100 lines if angle cannot be determined
- Apply truncation only to `search_code` action (not standards or AST)

**Rationale:** 80% of queries only need high-level information; optimize for the common case

**Priority:** P0

**Test Cases:**
- TC-1.1: Conceptual query "How does X work?" → 100 lines per result
- TC-1.2: Location query "Where is X?" → 50 lines per result
- TC-1.3: Implementation query "How to implement X?" → Full chunks
- TC-1.4: Unknown angle → 100 lines (safe default)
- TC-1.5: Standards search → No truncation (ignored)

---

### FR-2: Explicit Override Mechanism

**Requirement:** System SHALL support explicit truncation control via `truncate` parameter

**Specification:**
- Add `truncate` parameter to `search_code` action
- Parameter types:
  - `True` (default): Auto-detect based on query angle
  - `False`: No truncation (full chunks)
  - `int` (e.g., 200): Explicit line count
  - `"auto"`: Same as `True` (explicit auto-detect)
- Override takes precedence over auto-detection
- Parameter ignored for non-code search actions

**Rationale:** Power users need control; explicit overrides for edge cases

**Priority:** P0

**Test Cases:**
- TC-2.1: `truncate=True` → Auto-detect (default)
- TC-2.2: `truncate=False` → Full chunks
- TC-2.3: `truncate=200` → Exactly 200 lines
- TC-2.4: `truncate="auto"` → Auto-detect (explicit)
- TC-2.5: Invalid value → Error with guidance

---

### FR-3: Smart Boundary Truncation

**Requirement:** System SHALL truncate at natural code boundaries (method/class boundaries)

**Specification:**
- Never truncate mid-method or mid-docstring
- Look backwards up to 20 lines from target to find natural boundary
- Natural boundaries: blank line, `def `, `class ` (language-specific)
- If no boundary found within 20 lines, use target line (fallback)
- Always preserve complete docstrings in truncated content

**Rationale:** Preserve semantic integrity; partial methods are confusing

**Priority:** P0

**Test Cases:**
- TC-3.1: Target at line 100, method ends at 95 → Truncate at 95
- TC-3.2: Target at line 100, no boundary in 80-100 → Truncate at 100
- TC-3.3: Docstring at lines 90-105, target 100 → Truncate at 110 (after docstring)
- TC-3.4: Multiple methods near target → Truncate at nearest boundary

---

### FR-4: Response Metadata

**Requirement:** System SHALL include comprehensive metadata in truncated responses

**Specification:**
- Per-result metadata:
  - `truncated`: Boolean (true if truncated)
  - `full_line_count`: Total lines in original chunk
  - `truncation_point`: Line where truncation occurred
  - `hint`: User guidance ("Use truncate=False to get full chunk")
- Response-level metadata:
  - `truncation_reason`: Object with `angle`, `max_lines`, `override`
- Inline hint in content: "\n\n... [truncated: X more lines]\nUse truncate=False..."

**Rationale:** Self-documenting system; teaches users how to get full content

**Priority:** P0

**Test Cases:**
- TC-4.1: Truncated result includes all metadata fields
- TC-4.2: Non-truncated result has `truncated=false`
- TC-4.3: Response includes `truncation_reason` with detected angle
- TC-4.4: Inline hint appears in truncated content

---

### FR-5: Backwards Compatibility

**Requirement:** System SHALL maintain backwards compatibility with existing queries

**Specification:**
- Existing queries without `truncate` parameter work unchanged (auto-detect applied)
- Default behavior: `truncate=True` (auto-detect)
- No changes to response structure (only additions)
- No changes to other search actions (standards, AST, graph)
- No changes to indexing (truncation is post-processing only)

**Rationale:** Don't break existing workflows; opt-in optimization

**Priority:** P0

**Test Cases:**
- TC-5.1: Query without `truncate` param → Auto-detect applied
- TC-5.2: Standards search → No truncation
- TC-5.3: AST search → No truncation
- TC-5.4: Graph search → No truncation
- TC-5.5: Existing response fields unchanged

---

### FR-6: Query Distribution Optimization

**Requirement:** System SHALL optimize for observed query distribution (80/15/5)

**Specification:**
- 80% of queries (conceptual/location) get truncated (50-100 lines)
- 15% of queries (implementation) get full chunks
- 5% of queries (critical/troubleshooting) get appropriate content
- Weighted average: 1,800 tokens per query (down from 6,000)
- Optimize for common case, preserve full content for edge cases

**Rationale:** Evidence-based design; optimize for actual usage patterns

**Priority:** P0

**Test Cases:**
- TC-6.1: Simulate 100 queries with 80/15/5 distribution → Avg 1,800 tokens
- TC-6.2: Conceptual queries → 80% token reduction
- TC-6.3: Implementation queries → 0% token reduction (full content)

---

### FR-7: Preserve Docstrings and Signatures

**Requirement:** System SHALL always include complete docstrings and signatures in truncated content

**Specification:**
- Class docstrings: Always included (typically first 40 lines)
- `__init__` method: Always included with signature + docstring
- Main method: Signature + docstring + high-level algorithm
- Helper methods: Signatures visible (names + params)
- Truncate at helper method boundaries (after main method)

**Rationale:** First 100 lines typically includes all critical context for understanding

**Priority:** P0

**Test Cases:**
- TC-7.1: Truncated at 100 lines includes complete class docstring
- TC-7.2: Truncated content includes `__init__` method
- TC-7.3: Main method signature + docstring included
- TC-7.4: Helper method signatures visible (not implementations)

---

## 4. Non-Functional Requirements

### NFR-1: Performance

**Requirement:** Truncation overhead SHALL be <10ms per query

**Specification:**
- Post-processing only (no impact on search latency)
- Simple string operations (line splitting, slicing)
- O(n) complexity where n = lines in chunk
- No LLM inference required
- Benchmark: 95th percentile <10ms

**Rationale:** Optimization should not add noticeable latency

**Priority:** P0

**Measurement:** Performance tests with 1000-line chunks

---

### NFR-2: Reliability

**Requirement:** System SHALL handle edge cases gracefully

**Specification:**
- Classifier failure → Default to 100 lines
- No natural boundary found → Use target line
- Empty query → Default to 100 lines
- Invalid `truncate` parameter → Error with guidance
- Chunk smaller than threshold → No truncation

**Rationale:** Graceful degradation; never fail hard

**Priority:** P0

**Test Cases:**
- TC-NFR-2.1: Classifier unavailable → Default to 100 lines
- TC-NFR-2.2: No boundary in 20 lines → Use target
- TC-NFR-2.3: Chunk 50 lines, threshold 100 → No truncation

---

### NFR-3: Maintainability

**Requirement:** Code SHALL be well-tested and documented

**Specification:**
- Test coverage >90%
- Unit tests for all truncation logic
- Integration tests for each query angle
- Edge case tests for error conditions
- Performance benchmarks
- Comprehensive docstrings with examples

**Rationale:** Critical reliability feature requires high quality

**Priority:** P0

**Measurement:** Coverage report, test suite execution

---

### NFR-4: Observability

**Requirement:** System SHALL track behavioral metrics for optimization

**Specification:**
- Track token reduction per query
- Track temp file frequency
- Track query refinement rate (`truncate=False` after truncated)
- Track misclassification rate (immediate full chunk requests)
- Track angle distribution (validate 80/15/5 assumption)

**Rationale:** Data-driven optimization; validate assumptions

**Priority:** P1

**Measurement:** Metrics dashboard, behavioral tracking

---

### NFR-5: Usability

**Requirement:** System SHALL be self-documenting and self-teaching

**Specification:**
- Clear metadata in responses (truncation status, hints)
- Inline guidance in truncated content
- Examples in docstring for all parameter types
- Error messages with remediation guidance
- Standard document explaining behavior

**Rationale:** AI agents learn from system responses; teach optimal patterns

**Priority:** P1

**Measurement:** User feedback, query refinement patterns

---

## 5. Out of Scope

### 5.1 Explicitly Excluded

**OOS-1: Modifying AST Chunking Strategy**
- **Description:** Implementing the TODO in `ast_chunker.py` to split large functions at control flow boundaries
- **Rationale:** Truncation is simpler, preserves semantic integrity, doesn't affect indexing
- **Future Consideration:** Can be revisited if truncation proves insufficient

**OOS-2: Pagination or Multi-Round-Trip Fetching**
- **Description:** Returning chunk IDs and requiring AI to request specific chunks
- **Rationale:** Adds latency for all queries; truncation satisfies 80% of queries immediately
- **Future Consideration:** Could be added for very large chunks (>2000 lines)

**OOS-3: LLM-Based Summarization**
- **Description:** Using LLM to generate summaries of code chunks
- **Rationale:** Adds cost, latency, and hallucination risk; truncation provides actual code
- **Future Consideration:** Could be added as optional enhancement

**OOS-4: Truncation for Standards or AST Search**
- **Description:** Applying truncation to standards or AST search results
- **Rationale:** Standards chunks already small (50-100 lines); AST returns structural patterns
- **Future Consideration:** Not needed; different content characteristics

**OOS-5: Learning/Adaptive Thresholds**
- **Description:** Adjusting truncation thresholds based on usage patterns
- **Rationale:** Static thresholds are simpler for MVP; learning adds complexity
- **Future Consideration:** Phase 2 enhancement after validating static thresholds

### 5.2 Assumptions

**A-1:** Query distribution remains approximately 80/15/5 (conceptual/implementation/other)  
**A-2:** First 100 lines of a class typically includes docstring + init + main method  
**A-3:** QueryClassifier accuracy is sufficient for truncation decisions  
**A-4:** Method boundaries can be detected with simple heuristics (blank line, def, class)  
**A-5:** 200K context window remains the target for optimization

### 5.3 Dependencies

**D-1:** Existing `QueryClassifier` in `middleware/query_classifier.py`  
**D-2:** Existing `AST Chunker` in `subsystems/rag/code/ast_chunker.py`  
**D-3:** Existing `pos_search_project` tool in `tools/pos_search_project.py`  
**D-4:** Python 3.11+ for type hints (`Union[bool, int, str]`)

---

## 6. Constraints

### 6.1 Technical Constraints

**C-1: Backwards Compatibility**
- All existing queries must work unchanged
- No breaking changes to response structure
- Default behavior must be safe and reasonable

**C-2: Semantic Integrity**
- Never truncate mid-method or mid-docstring
- Preserve complete semantic units
- Maintain code readability

**C-3: Performance**
- Truncation overhead <10ms per query
- No impact on search latency
- No impact on indexing performance

**C-4: Code Quality**
- Test coverage >90%
- Comprehensive documentation
- Error handling for all edge cases

### 6.2 Business Constraints

**C-5: Timeline**
- Implementation: 5-8 hours
- Spec creation: 1.5 hours
- Total: 6.5-9.5 hours (within 1 sprint)

**C-6: Risk**
- Low risk (post-processing only, doesn't affect indexing)
- Backwards compatible (safe default behavior)
- Reversible (can disable with `truncate=False`)

---

## 7. Acceptance Criteria

### 7.1 Must Have (P0)

- [ ] Auto-detect truncation based on query angle (FR-1)
- [ ] Explicit override via `truncate` parameter (FR-2)
- [ ] Smart boundary truncation (FR-3)
- [ ] Comprehensive metadata in responses (FR-4)
- [ ] Backwards compatibility maintained (FR-5)
- [ ] 70% average token reduction achieved (BG-2)
- [ ] 80% temp file reduction achieved (BG-1)
- [ ] Performance overhead <10ms (NFR-1)
- [ ] Test coverage >90% (NFR-3)

### 7.2 Should Have (P1)

- [ ] Query refinement tracking (NFR-4)
- [ ] Misclassification tracking (NFR-4)
- [ ] Behavioral metrics dashboard (NFR-4)
- [ ] Standard document explaining behavior (NFR-5)
- [ ] Examples for all parameter types (NFR-5)

### 7.3 Nice to Have (P2)

- [ ] Learning/adaptive thresholds (OOS-5, future)
- [ ] Pagination for very large chunks (OOS-2, future)
- [ ] LLM-based summaries (OOS-3, future)

---

## 8. References

### 8.1 Supporting Documents

- **Design Document:** `supporting-docs/2025-11-16-code-search-auto-truncation.md`
- **Document Index:** `supporting-docs/INDEX.md`

### 8.2 Related Standards

- **Behavioral Engineering Patterns:** `.praxis-os/standards/development/behavioral-engineering-patterns.md`
- **pos_search_project Usage Guide:** `.praxis-os/standards/universal/tools/pos-search-project-usage-guide.md`

### 8.3 Related Code

- **QueryClassifier:** `.praxis-os/ouroboros/middleware/query_classifier.py`
- **AST Chunker:** `.praxis-os/ouroboros/subsystems/rag/code/ast_chunker.py`
- **pos_search_project:** `.praxis-os/ouroboros/tools/pos_search_project.py`

---

## 9. Revision History

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2025-11-16 | 1.0 | AI Agent | Initial SRD creation from design document |

---

**Document Status:** ✅ Ready for Phase 2 (Design Specification)

