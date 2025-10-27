# Supporting Documents Index

**Spec:** Query Gamification System  
**Created:** 2025-10-21  
**Total Documents:** 1

## Document Catalog

### 1. Query Gamification System Design

**File:** `query-gamification-system-2025-10-21.md`  
**Type:** Comprehensive technical design document  
**Size:** 45KB  
**Purpose:** Complete design for implementing a gamification system that uses behavioral psychology (completion-seeking patterns) to maintain AI agent query-first behavior throughout conversations, preventing drift to improvisation.

**Relevance:** Requirements [H], Design [H], Implementation [H]

**Key Topics:**
- Multi-angle discovery pattern (5 query angles: definition, location, practical, best practice, error prevention)
- Behavioral problem: AI query patterns degrade after 10+ messages
- Completion mechanics: Progress counters (3/5), visual gaps (⬜), angle tracking (📖📍🔧⭐⚠️)
- QueryTracker architecture: session-based state management
- Dynamic prepend generation: personalized feedback in search results
- Angle classification: keyword-based query intent detection
- Token cost analysis: ~400 tokens per task, positive ROI
- Testing strategy: unit tests, integration tests, full cycle validation
- Rollout plan: aggressive early-stage deployment with fast iteration

**Architecture Components:**
- `query_classifier.py` - Classify queries into 5 standard angles
- `query_tracker.py` - Track per-session query statistics
- `prepend_generator.py` - Generate dynamic feedback messages
- `session_id_extractor.py` - Extract session context
- Integration into `rag_tools.py` - Modify search_standards() tool

**Success Criteria:**
- Query count sustained at 4+ per task throughout conversation
- At least 3 different angles explored per task
- No negative user feedback on distraction/noise
- Measurable reduction in implementation errors

---

## Cross-Document Analysis

**Common Themes:**
- Single document provides end-to-end coverage (executive summary → implementation → testing → deployment)

**Potential Conflicts:**
- None (single authoritative source)

**Coverage Gaps:**
- Integration with existing workflow system (noted as "Future Enhancement V6")
- MCP session ID extraction implementation details (document acknowledges this as TODO)
- User acceptance testing results (deployment plan assumes rapid iteration)
- Metrics baseline (document notes "TBD" for current error rates)

---

## Document Quality Assessment

**Strengths:**
- Comprehensive coverage: problem definition → solution → architecture → implementation → testing
- Behavioral psychology foundation: grounded in LLM completion-seeking behavior
- Concrete implementation: full code examples with ~400 lines total
- Cost-benefit analysis: explicit token cost calculation and ROI justification
- Testing strategy: detailed unit and integration test specifications
- Rollout strategy: appropriate for early-stage product

**Gaps Requiring Clarification:**
1. **Baseline metrics:** Need to establish current query behavior (queries per task, angle diversity)
2. **Session ID reliability:** Document acknowledges MCP spec doesn't provide session metadata yet
3. **Workflow integration:** How this relates to existing phase gates and evidence validation
4. **User visibility:** Whether users should see query statistics (document rejects dashboard)

---

## Insights for Spec Creation

**Requirements Insights:**
- **Primary goal:** Maintain 5-10 queries per task throughout conversation (currently drops to 1-2 after message 10)
- **Target metrics:** 4+ angles covered in 80% of tasks, 50% increase in queries per task
- **Non-goal:** Mandatory query gates (rejected as too restrictive)

**Design Insights:**
- **Core mechanism:** Dynamic prepend messages in search_standards() results
- **State management:** In-memory per-session tracking (no persistence needed)
- **Angle classification:** Keyword-based pattern matching (5 categories)
- **Integration point:** Minimal changes to existing code (10-line modification + 4 new files)

**Implementation Insights:**
- **File structure:** 4 new core modules (~400 lines total), modify 1 existing tool
- **Testing approach:** Unit tests for each module + integration test for full cycle
- **Deployment:** Single-stage rollout (no gradual rollout needed at early stage)
- **Rollback:** Trivial (revert 10-line change, all new code isolated)

---

## Extracted Insights (Detailed)

### Requirements Insights (Phase 1)

#### From query-gamification-system-2025-10-21.md:

**User Needs:**
- **Problem:** AI agents query frequently for first 3-5 messages, then drift to improvisation after message 10+
- **Need:** Sustained query-first behavior throughout entire conversation (50+ messages)
- **Impact:** Reduced implementation errors from incomplete understanding

**Business Goals:**
- Maintain 5-10 queries per task throughout conversation (baseline: 1-2 after message 10)
- Increase multi-angle exploration (5 perspectives vs current 1-2)
- Reduce debugging cycles (save 300-1000 tokens per prevented error)
- Consistent behavior across all MCP-compatible agents (Cursor, Cline, Continue)

**Functional Requirements:**
- **FR-1:** Track query count per session (total and unique)
- **FR-2:** Classify queries into 5 angles (definition, location, practical, best practice, error prevention)
- **FR-3:** Generate dynamic prepend messages based on query history
- **FR-4:** Display progress indicator (N/5 queries)
- **FR-5:** Display angle coverage visual (📖✓ 📍✓ 🔧⬜ ⭐⬜ ⚠️⬜)
- **FR-6:** Suggest next uncovered angle
- **FR-7:** Show completion message when 5/5 achieved
- **FR-8:** Extract session ID from MCP context

**Non-Functional Requirements:**
- **NFR-1:** Token cost ≤ 500 tokens per task (~400 tokens target)
- **NFR-2:** Processing latency ≤ 10ms per query (no user-perceivable delay)
- **NFR-3:** Memory footprint ≤ 1MB per session (in-memory state only)
- **NFR-4:** Agent-agnostic (works with Cursor, Cline, Continue, any MCP-compatible)
- **NFR-5:** No breaking changes to existing MCP tool interface
- **NFR-6:** Rollback time ≤ 5 minutes (single file revert)

**Success Criteria:**
- **Minimum viable:** Query count ≥4 per task sustained throughout conversation
- **Minimum viable:** ≥3 different angles explored per task
- **Minimum viable:** No negative user feedback on distraction/noise
- **Stretch:** 50% increase in queries per task
- **Stretch:** 4+ angles in 80% of tasks
- **Stretch:** Measurable reduction in implementation errors

**Constraints:**
- Cannot modify agent system prompts (we don't control Cursor/Cline)
- Cannot modify agent UI (MCP server side only)
- Cannot require user interaction (must be automatic)
- Cannot persist state across server restarts (in-memory only acceptable)

**Out of Scope:**
- User-facing dashboard (rejected - requires UI changes we don't control)
- Mandatory query gates (rejected - too restrictive)
- Reward points system (rejected - too complex for the problem)
- Cross-session learning/analytics (deferred to V5)

---

### Design Insights (Phase 2)

#### From query-gamification-system-2025-10-21.md:

**Architecture Pattern:**
- **Pattern:** Interceptor pattern on MCP tool responses
- **Approach:** Inject dynamic prepend into search_standards() results
- **Rationale:** Minimal disruption, leverages existing tool interface

**System Components:**

1. **QueryClassifier** (`query_classifier.py`)
   - **Responsibility:** Classify query string into one of 5 angles
   - **Method:** Keyword-based pattern matching
   - **Input:** Query string
   - **Output:** QueryAngle enum (definition/location/practical/best_practice/error_prevention)
   - **Size:** ~100 lines

2. **QueryTracker** (`query_tracker.py`)
   - **Responsibility:** Maintain per-session query statistics
   - **State:** Dictionary of session_id → QueryStats (total queries, unique queries, angles covered, history)
   - **Lifetime:** Process lifetime (no persistence)
   - **Thread Safety:** Not required (single-threaded MCP server)
   - **Size:** ~150 lines

3. **PrependGenerator** (`prepend_generator.py`)
   - **Responsibility:** Generate dynamic feedback messages
   - **Input:** QueryTracker stats, current query
   - **Output:** Formatted prepend string with progress/suggestions
   - **Logic:** Progress bar, angle indicators, next suggestion, completion message
   - **Size:** ~100 lines

4. **SessionExtractor** (`session_id_extractor.py`)
   - **Responsibility:** Extract session ID from MCP request context
   - **Fallback Strategy:** PID-based if MCP metadata unavailable
   - **Default:** "default" session for backward compatibility
   - **Size:** ~50 lines

**Data Models:**

```python
QueryAngle = Literal['definition', 'location', 'practical', 'best_practice', 'error_prevention']

@dataclass
class QueryStats:
    total_queries: int = 0
    unique_queries: int = 0
    angles_covered: Set[QueryAngle] = field(default_factory=set)
    query_history: List[str] = field(default_factory=list)
    last_query_time: datetime | None = None
```

**Data Flow:**
1. AI agent calls search_standards(query)
2. Extract session_id from context (or use PID fallback)
3. Execute RAG search → get results
4. Track query: classifier → tracker → update stats
5. Generate prepend: tracker stats → prepend generator → formatted message
6. Inject prepend into first result
7. Return results to agent

**API/Integration:**
- **Modified Function:** `search_standards()` in `rag_tools.py` (10-line change)
- **New Imports:** QueryTracker, PrependGenerator modules
- **Backward Compatibility:** Yes (prepend is additive, not breaking)

**Security:**
- **Session Isolation:** Stats maintained per-session, no cross-contamination
- **Privacy:** Session IDs hashed if logged (not stored)
- **Injection Risk:** None (prepend is server-generated, not user input)

**Performance:**
- **Time Complexity:** O(1) for classification, tracking, prepend generation
- **Space Complexity:** O(n) where n = unique queries per session (bounded by conversation length)
- **Memory Management:** In-memory only, garbage collected with session end

**Behavioral Psychology Design:**
- **Completion-seeking:** Progress indicator (3/5) creates tension
- **Visual gaps:** Empty boxes (⬜⬜⬜) activate fill-pattern
- **Concrete suggestions:** Reduce decision fatigue, lower friction
- **Angle diversity:** Prevents gaming (can't just repeat same query)

---

### Implementation Insights (Phase 4)

#### From query-gamification-system-2025-10-21.md:

**File Structure:**
```
mcp_server/
  core/
    query_classifier.py      (~100 lines) [NEW]
    query_tracker.py         (~150 lines) [NEW]
    prepend_generator.py     (~100 lines) [NEW]
    session_id_extractor.py  (~50 lines) [NEW]
  server/
    tools/
      rag_tools.py           (10-line modification) [MODIFIED]
```

**Code Patterns:**

1. **Angle Classification** (Keyword matching)
```python
def classify_query_angle(query: str) -> QueryAngle:
    query_lower = query.lower()
    if any(pattern in query_lower for pattern in ['what is', 'define']):
        return 'definition'
    # ... etc
```

2. **Session State Management** (Global singleton)
```python
_tracker = QueryTracker()

def get_tracker() -> QueryTracker:
    return _tracker
```

3. **Dynamic Prepend Generation** (Template-based)
```python
prepend = f"""Queries: {stats.total_queries}/5 | Angles: {angles_display}
💡 {suggestion}"""
```

**Testing Strategy:**

**Unit Tests** (~350 lines total):
- `test_query_classifier.py`: Test all 5 angle classifications (definition, location, practical, best practice, error prevention)
- `test_query_tracker.py`: Test count tracking, unique detection, angle coverage, session isolation
- `test_prepend_generator.py`: Test progress display, angle indicators, suggestions, completion messages

**Integration Tests** (~200 lines):
- `test_query_gamification.py`: Full cycle test (5 queries → completion message)
- Mock search_standards calls, verify prepend evolution

**Manual Testing:**
1. Start fresh conversation
2. Execute 5 queries covering different angles
3. Verify prepend messages evolve correctly
4. Verify completion message appears
5. Test repeated queries (should not double-count unique)

**Test Coverage Target:** ≥90%

**Deployment Process:**

**Phase 1: Implementation** (2-3 hours)
- Create 4 new core modules
- Modify rag_tools.py
- Run unit tests

**Phase 2: Testing** (1-2 hours)
- Write and run integration tests
- Manual testing

**Phase 3: Deploy** (immediate)
- Deploy to production (early-stage aggressive approach)
- No gradual rollout needed (small user base, low blast radius)

**Phase 4: Monitor** (ongoing)
- Manual observation for first week
- Track: query behavior, user feedback, bugs
- Iterate based on usage (2-3 day cycles)

**Rollback Plan:**
- **Trigger:** Critical bugs or negative user feedback
- **Action:** Revert 10-line change in rag_tools.py
- **Time:** < 5 minutes
- **Risk:** Low (all new code isolated in new files)

**Monitoring (Manual, Week 1):**
- Does AI query more frequently?
- Are suggestions helpful or annoying?
- Token cost acceptable?
- Any crashes/errors?

**Iteration Velocity:**
- Deploy v1: Day 1
- Tweak based on usage: Day 2-3
- Stable version: Day 5
- Enhancements: Ongoing

**Troubleshooting:**

**Issue 1:** Session ID extraction fails
- **Symptom:** All queries grouped under "default" session
- **Fix:** Falls back gracefully, gamification still works

**Issue 2:** Angle classification incorrect
- **Symptom:** Wrong emoji shown for query type
- **Fix:** Refine keyword patterns in classifier

**Issue 3:** Token cost higher than expected
- **Symptom:** Prepend messages too long
- **Fix:** Shorten suggestion text, optimize formatting

**Issue 4:** Distraction/noise complaints
- **Symptom:** Users find prepend distracting
- **Fix:** Add opt-out flag, reduce prepend verbosity

---

### Cross-References

**Validated by Multiple Sources:**
- N/A (single authoritative document)

**Conflicts:**
- None identified

**High-Priority Items:**
1. **QueryTracker implementation** (core component, all others depend on it)
2. **Prepend injection point** (integration with existing rag_tools.py)
3. **Angle classification accuracy** (determines quality of diversity tracking)
4. **Token cost validation** (must stay under 500 tokens per task)
5. **User acceptance** (no negative feedback on distraction)

---

## Insight Summary

**Total:** 45 insights  
**By Category:** Requirements [18], Design [15], Implementation [12]  
**Multi-source validated:** 0 (single source document)  
**Conflicts to resolve:** 0  
**High-priority items:** 5

**Phase 0 Complete:** ✅ 2025-10-21

