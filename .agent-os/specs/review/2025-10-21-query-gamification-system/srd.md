# Software Requirements Document

**Project:** Query Gamification System  
**Date:** 2025-10-21  
**Priority:** High  
**Category:** Enhancement

---

## 1. Introduction

### 1.1 Purpose
This document defines the requirements for implementing a gamification system that maintains AI agent query-first behavior throughout conversations by exploiting LLM completion-seeking patterns.

### 1.2 Scope
This feature will inject dynamic, personalized feedback into `search_standards()` results to create continuous behavioral reinforcement without requiring control of agent system prompts or UI. The system tracks query patterns per session and provides progress indicators, angle coverage visualization, and concrete suggestions to maintain 5-10 queries per task throughout the conversation lifecycle.

---

## 2. Business Goals

### Goal 1: Sustain Query-First Behavior Throughout Conversations

**Objective:** Maintain AI agent query frequency at 5-10 queries per task throughout entire conversation lifecycle (50+ messages), preventing degradation to improvisation.

**Success Metrics:**
- **Queries per task**: 1-2 (current, after message 10) → 5-10 (target, sustained)
- **Query consistency**: Degrades after message 10 (current) → Sustained through message 50+ (target)
- **Conversation depth**: Limited exploration (current) → Comprehensive discovery (target)

**Business Impact:**
- **Quality improvement**: More thorough AI understanding leads to fewer implementation errors
- **Cost reduction**: Prevent 1-3 debugging cycles per task (saving 300-1000 tokens per prevented error)
- **User satisfaction**: Higher quality output with fewer "obvious mistakes" requiring correction

**ROI Calculation:**
- **Cost**: ~400 tokens per task in dynamic prepend messages
- **Benefit**: 500-1000 tokens saved per prevented debugging cycle
- **Break-even**: Prevents 1 error every 2-3 tasks (highly achievable)

---

### Goal 2: Increase Multi-Angle Query Exploration

**Objective:** Drive AI agents to explore topics from multiple perspectives (definition, location, practical, best practice, error prevention) rather than single-angle surface understanding.

**Success Metrics:**
- **Angle diversity**: 1.2 angles per task (current estimate) → 4+ angles per task (target)
- **Coverage completeness**: 20% of tasks cover 4+ angles (current) → 80% of tasks (target)
- **Exploration depth**: Surface-level queries (current) → Comprehensive multi-perspective discovery (target)

**Business Impact:**
- **Reduced blind spots**: AI discovers edge cases, anti-patterns, and best practices before implementing
- **Better architectural decisions**: Understanding location + best practices leads to better design choices
- **Fewer rework cycles**: Comprehensive understanding upfront prevents "oh, I didn't know about that" moments

**Behavioral Rationale:**
- Semantic search is probabilistic; single query = narrow view
- Multi-angle exploration discovers different content chunks
- AI agents can execute 5 queries in 60 seconds (humans need hours of reading)

---

### Goal 3: Reduce Implementation Errors from Incomplete Understanding

**Objective:** Measurably decrease the frequency of implementation errors caused by AI agents proceeding with insufficient context.

**Success Metrics:**
- **Debugging messages per task**: Baseline TBD (track over 2 weeks) → 30% reduction (target)
- **Implementation accuracy on first pass**: Baseline TBD → 20% improvement (target)
- **User corrections per task**: Baseline TBD → 25% reduction (target)

**Business Impact:**
- **Faster iteration velocity**: Less time spent in back-and-forth corrections
- **Higher user confidence**: Users trust AI more when quality is consistently high
- **Reduced frustration**: Fewer "you missed something obvious" moments

**Measurement Approach:**
- Track debugging cycles in development logs (count of messages fixing previous implementation)
- Survey user satisfaction with output quality (before/after deployment)
- Monitor conversation message counts (fewer messages = fewer corrections)

---

### Goal 4: Achieve Agent-Agnostic Consistency

**Objective:** Ensure query gamification works uniformly across all MCP-compatible agents (Cursor, Cline, Continue) without requiring agent-specific adaptations.

**Success Metrics:**
- **Agent compatibility**: Works with 100% of MCP-compatible agents (Cursor, Cline, Continue tested)
- **Behavior consistency**: Similar query patterns across different agents (±10% variance acceptable)
- **Zero agent-specific code**: No conditional logic based on agent type

**Business Impact:**
- **Broader ecosystem compatibility**: Works with current and future MCP-compatible agents
- **Reduced maintenance burden**: Single implementation serves all agents
- **User flexibility**: Users can switch agents without losing quality improvements

**Technical Rationale:**
- MCP provides standardized tool interface
- Behavioral reinforcement happens server-side (agent-agnostic)
- No dependence on agent-specific system prompts or UI

---

## 3. User Stories

User stories describe the feature from the user's perspective.

### Story Format

**As a** {user type}  
**I want to** {capability}  
**So that** {benefit}

---

### Story 1: Query Progress Visibility

**As an** AI agent executing tasks  
**I want to** see my query progress (e.g., "3/5 queries") in real-time  
**So that** I'm aware of how thoroughly I've explored the topic and feel motivated to reach completion

**Acceptance Criteria:**
- Given I've executed N queries in the current session
- When I receive search_standards() results
- Then I see "Queries: N/5" in the prepend message
- And the progress counter increments with each unique query
- And the counter resets per session (not cumulative across conversations)

**Priority:** Critical (Must-Have)

**Rationale:** Progress visibility is the core completion-seeking mechanism. Without it, the gamification system has no behavioral impact.

---

### Story 2: Angle Coverage Feedback

**As an** AI agent exploring a topic  
**I want to** see which query angles I've covered (📖 definition, 📍 location, 🔧 practical, ⭐ best practice, ⚠️ error prevention)  
**So that** I can identify unexplored perspectives and achieve comprehensive understanding

**Acceptance Criteria:**
- Given I've executed queries covering some angles
- When I receive search_standards() results
- Then I see angle indicators (e.g., "📖✓ 📍✓ 🔧⬜ ⭐⬜ ⚠️⬜")
- And covered angles show ✓ checkmark
- And uncovered angles show ⬜ empty box
- And angle classification is reasonably accurate (≥80%)

**Priority:** Critical (Must-Have)

**Rationale:** Angle diversity prevents gaming the system through repeated similar queries. Forces true multi-perspective exploration.

---

### Story 3: Concrete Query Suggestions

**As an** AI agent with incomplete angle coverage  
**I want to** receive specific suggestions for uncovered angles (e.g., "Try: 'validation common mistakes'")  
**So that** I have a concrete next step and reduced friction for continuing to query

**Acceptance Criteria:**
- Given I've covered fewer than 5 angles
- When I receive search_standards() results
- Then I see a concrete suggestion like "💡 Try: '{topic} best practices'"
- And the suggestion targets an uncovered angle
- And the suggestion incorporates context from my current query (topic extraction)
- And suggestions stop appearing once 5/5 queries are complete

**Priority:** High

**Rationale:** Reduces decision fatigue. Makes querying the path of least resistance rather than requiring the agent to think "what should I query next?"

---

### Story 4: Completion Acknowledgment

**As an** AI agent who has explored comprehensively  
**I want to** receive explicit acknowledgment when I've completed thorough exploration (5/5 queries, 4+ angles)  
**So that** I feel confident proceeding to implementation with sufficient context

**Acceptance Criteria:**
- Given I've executed 5+ queries covering 4+ angles
- When I receive search_standards() results
- Then I see "✅ Comprehensive discovery complete! Ready to implement."
- And no further suggestions are shown
- And the message provides positive reinforcement

**Priority:** High

**Rationale:** Positive reinforcement strengthens the query-first behavior pattern. Provides clear signal that exploration phase is complete.

---

### Story 5: Consistent Quality Throughout Conversation

**As a** human developer using AI assistance  
**I want** the AI to maintain query-first behavior throughout long conversations (50+ messages)  
**So that** implementation quality doesn't degrade as the conversation progresses

**Acceptance Criteria:**
- Given I'm in a conversation with 50+ messages
- When I ask the AI to implement a feature
- Then the AI queries 4+ times before implementing
- And query frequency doesn't degrade compared to early messages
- And implementation quality remains high

**Priority:** Critical (Must-Have)

**Rationale:** This is the primary user-facing value proposition. Without sustained behavior, the system fails its core purpose.

---

### Story 6: Reduced Debugging Cycles

**As a** human developer using AI assistance  
**I want** the AI to discover edge cases, anti-patterns, and best practices before implementing  
**So that** I spend less time correcting "obvious" mistakes the AI could have discovered

**Acceptance Criteria:**
- Given the AI has queried comprehensively (4+ angles)
- When the AI implements a feature
- Then the implementation includes edge case handling
- And follows best practices discovered through queries
- And avoids common mistakes documented in standards
- And I need fewer correction messages compared to baseline

**Priority:** High

**Rationale:** User-facing quality improvement. Directly impacts user satisfaction and trust in AI assistance.

---

### Story 7: Agent-Agnostic Experience

**As a** human developer who might use different AI agents (Cursor, Cline, Continue)  
**I want** query gamification to work consistently across all MCP-compatible agents  
**So that** I get the same quality improvements regardless of my tool choice

**Acceptance Criteria:**
- Given I use Cursor, Cline, or Continue with MCP
- When the AI queries via search_standards()
- Then gamification feedback appears identically
- And behavioral improvements are consistent (±10% variance)
- And no agent-specific configuration is required

**Priority:** High

**Rationale:** MCP ecosystem compatibility. Ensures solution isn't tool-locked.

---

### Story 8: No User Distraction

**As a** human developer reviewing AI query results  
**I want** gamification feedback to be unobtrusive  
**So that** I can focus on actual search results without being distracted by progress indicators

**Acceptance Criteria:**
- Given the AI is querying with gamification active
- When I see the search results
- Then the prepend message is ≤3 lines
- And visually separated from results (clear boundary)
- And doesn't distract from actual content
- And I don't receive negative feedback about noise/clutter

**Priority:** Medium

**Rationale:** User experience consideration. Gamification should improve outcomes without degrading UX.

---

## 3.1 Story Priority Summary

**Critical (Must-Have):**
- Story 1: Query Progress Visibility
- Story 2: Angle Coverage Feedback
- Story 5: Consistent Quality Throughout Conversation

**High Priority:**
- Story 3: Concrete Query Suggestions
- Story 4: Completion Acknowledgment
- Story 6: Reduced Debugging Cycles
- Story 7: Agent-Agnostic Experience

**Medium Priority:**
- Story 8: No User Distraction

**Implementation Order:**
1. Stories 1 & 2 (core gamification mechanics)
2. Story 3 (suggestions for usability)
3. Story 4 (completion feedback)
4. Stories 5-8 (quality validation and UX refinement)

---

## 3.2 Supporting Documentation

User needs from supporting documents:
- **query-gamification-system-2025-10-21.md**: Documents the behavioral problem (query patterns degrade after 10+ messages), completion-seeking psychology, and multi-angle discovery pattern that inform these user stories

See `supporting-docs/INDEX.md` for complete user need analysis.

---

## 4. Functional Requirements

Functional requirements specify capabilities the system must provide.

---

### FR-001: Session-Based Query Tracking

**Description:** The system shall track query statistics per conversation session, including total queries, unique queries, and query history.

**Priority:** Critical

**Related User Stories:** Story 1 (Query Progress Visibility), Story 5 (Consistent Quality)

**Acceptance Criteria:**
- System maintains separate statistics for each session_id
- Total query count increments for every search_standards() call
- Unique query count increments only for non-duplicate queries (case-insensitive comparison)
- Query history stores last 10 queries per session
- Statistics reset when session ends (process termination)
- No persistence required (in-memory only)

---

### FR-002: Query Angle Classification

**Description:** The system shall classify each query into one of five standard angles: definition, location, practical, best practice, or error prevention.

**Priority:** Critical

**Related User Stories:** Story 2 (Angle Coverage Feedback)

**Acceptance Criteria:**
- Classification accuracy ≥80% on representative query samples
- Classification executes in ≤5ms per query
- Uses keyword-based pattern matching (no ML required)
- Returns QueryAngle enum type
- Falls back to 'definition' for ambiguous queries
- Classification is deterministic (same query → same angle every time)

---

### FR-003: Dynamic Prepend Message Generation

**Description:** The system shall generate personalized feedback messages based on current query statistics and inject them into search_standards() results.

**Priority:** Critical

**Related User Stories:** Story 1 (Query Progress), Story 2 (Angle Coverage), Story 3 (Suggestions), Story 4 (Completion)

**Acceptance Criteria:**
- Prepend message includes "Queries: N/5 | Unique: M" format
- Prepend shows angle coverage with emoji indicators (📖✓ 📍⬜ etc.)
- Message is ≤3 lines (no line breaks within progress section)
- Prepend is injected into first result's content field
- Message generation executes in ≤10ms
- Visual separator (---) clearly delineates prepend from results

---

### FR-004: Progress Counter Display

**Description:** The system shall display a progress counter showing N/5 queries completed in the current session.

**Priority:** Critical

**Related User Stories:** Story 1 (Query Progress Visibility)

**Acceptance Criteria:**
- Counter format: "Queries: N/5" where N is total queries
- Counter updates in real-time with each query
- Target of 5 queries is fixed (not configurable in v1)
- Counter visible in every search_standards() response
- Counter resets per session (not cumulative)

---

### FR-005: Angle Coverage Visualization

**Description:** The system shall display visual indicators showing which of the 5 query angles have been covered in the current session.

**Priority:** Critical

**Related User Stories:** Story 2 (Angle Coverage Feedback)

**Acceptance Criteria:**
- Format: "📖✓ 📍⬜ 🔧✓ ⭐⬜ ⚠️⬜"
- Covered angles show emoji + ✓ checkmark
- Uncovered angles show emoji + ⬜ empty box
- All 5 angles always displayed (in consistent order)
- Order: definition, location, practical, best_practice, error_prevention
- Updates with each query based on classification

---

### FR-006: Concrete Query Suggestions

**Description:** The system shall suggest specific next queries for uncovered angles when fewer than 5 queries have been executed.

**Priority:** High

**Related User Stories:** Story 3 (Concrete Query Suggestions)

**Acceptance Criteria:**
- Suggestion format: "💡 Try: '{topic} {angle_pattern}'"
- Targets first uncovered angle (deterministic order)
- Extracts topic from current query when possible
- Falls back to generic "[concept]" if topic extraction fails
- Suggestions stop appearing at 5/5 queries
- Suggestion is actionable (can copy-paste the suggested query)

---

### FR-007: Completion Message Display

**Description:** The system shall display a completion acknowledgment message when the user has executed 5+ queries covering 4+ angles.

**Priority:** High

**Related User Stories:** Story 4 (Completion Acknowledgment)

**Acceptance Criteria:**
- Message: "✅ Comprehensive discovery complete! Ready to implement."
- Displayed when total_queries ≥ 5 AND angles_covered ≥ 4
- Replaces suggestion message (mutually exclusive)
- Provides positive reinforcement tone
- Continues to display on subsequent queries (sticky completion state)

---

### FR-008: Session ID Extraction

**Description:** The system shall extract or generate a session identifier for tracking purposes, with fallback strategies for robustness.

**Priority:** High

**Related User Stories:** Story 1 (Query Progress), Story 5 (Consistent Quality)

**Acceptance Criteria:**
- Primary: Extract session_id from MCP request context (if available)
- Fallback 1: Use process ID (PID) as session identifier
- Fallback 2: Use "default" session if all else fails
- Session extraction executes in ≤1ms
- Session ID is stable within a single conversation
- No cross-session data leakage

---

### FR-009: MCP Tool Integration

**Description:** The system shall integrate with the existing search_standards() MCP tool without breaking changes to the tool interface.

**Priority:** Critical

**Related User Stories:** Story 7 (Agent-Agnostic Experience)

**Acceptance Criteria:**
- No changes to search_standards() function signature
- No changes to return type structure
- Backward compatible with existing callers
- Integration requires ≤10 lines of code change in rag_tools.py
- No impact on search functionality (RAG search still works identically)
- Gamification is additive only (prepend injection)

---

### FR-010: Unique Query Detection

**Description:** The system shall identify duplicate queries to accurately track unique query count and prevent gaming the system.

**Priority:** Medium

**Related User Stories:** Story 2 (Angle Coverage Feedback)

**Acceptance Criteria:**
- Case-insensitive comparison (treat "VALIDATION" and "validation" as same)
- Whitespace normalization (treat "   validation  " and "validation" as same)
- Stores normalized query string in history for comparison
- Duplicate queries still increment total count but not unique count
- Duplicate detection executes in O(n) where n = queries in session

---

### FR-011: Agent-Agnostic Operation

**Description:** The system shall operate identically across all MCP-compatible AI agents (Cursor, Cline, Continue) without agent-specific code.

**Priority:** High

**Related User Stories:** Story 7 (Agent-Agnostic Experience)

**Acceptance Criteria:**
- No conditional logic based on agent type
- No agent-specific configuration required
- Gamification behavior identical across Cursor, Cline, Continue
- Testing performed on all three agents
- No reliance on agent-specific system prompts or UI

---

### FR-012: Token Budget Compliance

**Description:** The system shall keep prepend message token cost ≤500 tokens per task to ensure cost-effectiveness.

**Priority:** High

**Related User Stories:** Story 8 (No User Distraction)

**Acceptance Criteria:**
- Average prepend message ≤95 tokens (target: ~85 tokens)
- Maximum prepend message ≤120 tokens
- Token cost measured across 10 representative queries
- Cost per task (5-10 queries) ≤500 tokens total
- Cost documented in implementation phase

---

### FR-013: Performance Requirements

**Description:** The system shall process gamification logic with negligible latency impact on search operations.

**Priority:** High

**Related User Stories:** Story 8 (No User Distraction)

**Acceptance Criteria:**
- Query classification: ≤5ms per query
- Tracking update: ≤2ms per query
- Prepend generation: ≤10ms per query
- Total gamification overhead: ≤20ms per search_standards() call
- No user-perceivable delay (20ms << 50ms search time)

---

## 4.1 Requirements by Category

### Core Gamification Mechanics
- FR-001: Session-Based Query Tracking (Critical)
- FR-002: Query Angle Classification (Critical)
- FR-003: Dynamic Prepend Message Generation (Critical)

### User-Facing Feedback
- FR-004: Progress Counter Display (Critical)
- FR-005: Angle Coverage Visualization (Critical)
- FR-006: Concrete Query Suggestions (High)
- FR-007: Completion Message Display (High)

### System Integration
- FR-008: Session ID Extraction (High)
- FR-009: MCP Tool Integration (Critical)
- FR-011: Agent-Agnostic Operation (High)

### Quality & Performance
- FR-010: Unique Query Detection (Medium)
- FR-012: Token Budget Compliance (High)
- FR-013: Performance Requirements (High)

---

## 4.2 Traceability Matrix

| Requirement | User Stories | Business Goals | Priority |
|-------------|--------------|----------------|----------|
| FR-001 | Story 1, 5 | Goal 1, 3 | Critical |
| FR-002 | Story 2 | Goal 2 | Critical |
| FR-003 | Story 1, 2, 3, 4 | Goal 1, 2 | Critical |
| FR-004 | Story 1 | Goal 1 | Critical |
| FR-005 | Story 2 | Goal 2 | Critical |
| FR-006 | Story 3 | Goal 1 | High |
| FR-007 | Story 4 | Goal 1 | High |
| FR-008 | Story 1, 5 | Goal 1 | High |
| FR-009 | Story 7 | Goal 4 | Critical |
| FR-010 | Story 2 | Goal 2 | Medium |
| FR-011 | Story 7 | Goal 4 | High |
| FR-012 | Story 8 | Goal 1 | High |
| FR-013 | Story 8 | Goal 1, 3 | High |

---

## 4.3 Supporting Documentation

Requirements informed by:
- **query-gamification-system-2025-10-21.md**: Sections on "Implementation Details" provide concrete functional requirements including QueryTracker architecture, angle classification patterns, and prepend generation logic

See `supporting-docs/INDEX.md` section "Requirements Insights (Phase 1)" for detailed requirement derivation from source document.

---

## 5. Non-Functional Requirements

NFRs define quality attributes and system constraints.

---

### 5.1 Performance

**NFR-P1: Token Cost Efficiency**
- Average prepend message token cost: ≤95 tokens (target: ~85 tokens)
- Maximum prepend message: ≤120 tokens
- Total token cost per task (5-10 queries): ≤500 tokens
- **Measurement:** Token counting across 20 representative queries
- **Rationale:** Cost-effectiveness is critical for adoption. Each query adds ~43 tokens vs current static prepend; must demonstrate positive ROI.

**NFR-P2: Processing Latency**
- Query angle classification: ≤5ms per query
- Tracking statistics update: ≤2ms per query
- Prepend message generation: ≤10ms per query
- Total gamification overhead: ≤20ms per search_standards() call
- **Measurement:** Performance profiling with Python time.perf_counter()
- **Rationale:** Must be imperceptible to users. Search operations take ~50-200ms; 20ms overhead is acceptable (<10% impact).

**NFR-P3: Memory Footprint**
- Memory per active session: ≤1MB
- Total system memory overhead: ≤100MB (assuming <100 concurrent sessions)
- No memory leaks (constant memory usage over 1000+ queries)
- **Measurement:** Python memory_profiler tracking over extended operation
- **Rationale:** In-memory state only; must scale to reasonable concurrent session counts without excessive memory consumption.

---

### 5.2 Reliability

**NFR-R1: Graceful Degradation**
- System remains functional if session ID extraction fails (fallback to PID or "default")
- System remains functional if angle classification fails (fallback to "definition" angle)
- System remains functional if topic extraction fails (fallback to generic "[concept]" in suggestions)
- Search functionality never impacted by gamification failures
- **Measurement:** Fault injection testing (simulate each failure mode)
- **Rationale:** Gamification is enhancement, not core functionality. Must never break search operations.

**NFR-R2: Session Isolation**
- Statistics for session A do not affect session B
- No cross-session data leakage
- Session termination cleanly releases memory (no orphaned state)
- Concurrent sessions operate independently
- **Measurement:** Multi-session integration tests, memory leak detection
- **Rationale:** Ensures accurate per-conversation tracking and prevents confusion between concurrent users.

**NFR-R3: Deterministic Behavior**
- Same query in same context produces same classification (deterministic)
- Angle order consistent across all queries (definition → location → practical → best practice → error prevention)
- Progress counter accurately reflects query count (no drift)
- **Measurement:** Repeated test runs with identical inputs verify identical outputs
- **Rationale:** Predictable behavior builds trust and enables effective debugging.

---

### 5.3 Maintainability

**NFR-M1: Code Quality**
- Test coverage: ≥90% for all new modules (query_classifier, query_tracker, prepend_generator)
- Linter clean: Zero pylint/flake8 errors
- Type hints: 100% coverage with mypy validation
- **Measurement:** pytest-cov, pylint, mypy CI checks
- **Rationale:** High quality code reduces future maintenance burden. 90% coverage ensures robustness.

**NFR-M2: Rollback Safety**
- Rollback time: ≤5 minutes (revert single file change)
- Zero data migration required for rollback
- Rollback doesn't break existing functionality
- All new code isolated in new modules (no scattered changes)
- **Measurement:** Timed rollback exercise, integration testing post-rollback
- **Rationale:** Early-stage aggressive deployment requires fast rollback capability for risk mitigation.

**NFR-M3: Documentation**
- Every public function has docstring with Args, Returns, Examples
- README updated with gamification feature description
- Architecture decision recorded in supporting-docs
- **Measurement:** Documentation coverage tool, manual review
- **Rationale:** Enables future developers to understand and extend the system.

---

### 5.4 Compatibility

**NFR-C1: Agent-Agnostic Operation**
- Works identically on Cursor, Cline, Continue (all MCP-compatible agents)
- Zero agent-specific code or configuration
- No dependence on agent-specific system prompts or UI
- Behavioral variance across agents: ≤10%
- **Measurement:** Manual testing on all three agents, behavioral metrics comparison
- **Rationale:** MCP ecosystem compatibility. Single implementation serves entire ecosystem.

**NFR-C2: Backward Compatibility**
- No breaking changes to search_standards() function signature
- Existing callers work without modification
- Return type structure unchanged (prepend is additive)
- No changes to RAG search functionality
- **Measurement:** Regression testing with existing codebase, API contract validation
- **Rationale:** Must not disrupt existing workflows. Gamification is enhancement only.

**NFR-C3: Python Version Compatibility**
- Supports Python 3.10+ (current project requirement)
- No deprecated language features
- Dependencies compatible with existing requirements.txt
- **Measurement:** CI testing across Python 3.10, 3.11, 3.12
- **Rationale:** Aligns with project's Python version policy.

---

### 5.5 Scalability

**NFR-SC1: Horizontal Scaling**
- No shared state between MCP server processes
- Each process maintains independent session tracking
- Session state lives in process memory (no external state store required)
- **Measurement:** Multi-process deployment testing
- **Rationale:** Simplifies deployment. Each conversation typically handled by single process.

**NFR-SC2: Session Count Scaling**
- System supports ≥100 concurrent sessions without degradation
- Memory usage scales linearly with session count (O(n))
- Processing time per query remains constant regardless of session count (O(1))
- **Measurement:** Load testing with 100 concurrent simulated sessions
- **Rationale:** Must handle realistic concurrent usage without performance impact.

---

### 5.6 Security

**NFR-S1: Session Privacy**
- Session IDs hashed if logged (not stored in plaintext)
- No personally identifiable information in logs
- Query history limited to last 10 queries per session (bounded memory)
- **Measurement:** Log inspection, privacy audit
- **Rationale:** Respects user privacy even for internal debugging logs.

**NFR-S2: Injection Safety**
- No user input directly embedded in prepend messages
- All prepend content is server-generated
- No XSS vulnerabilities (prepend is plain text, not HTML/JavaScript)
- **Measurement:** Security code review, input sanitization verification
- **Rationale:** Prevents malicious exploitation of prepend injection mechanism.

---

### 5.7 Usability

**NFR-U1: Non-Intrusive Feedback**
- Prepend message ≤3 lines (compact)
- Clear visual separator (---) between prepend and results
- Emoji indicators universally understood (📖📍🔧⭐⚠️ standard symbols)
- No negative user feedback on distraction/clutter (measured post-deployment)
- **Measurement:** User feedback collection, UI review
- **Rationale:** Gamification should enhance UX, not degrade it. Feedback must be unobtrusive.

**NFR-U2: Actionable Feedback**
- Suggestions are copy-pasteable (exact query strings)
- Progress is immediately visible (no need to compute)
- Completion state is clear (✅ message unambiguous)
- **Measurement:** Usability testing with representative users
- **Rationale:** Feedback must reduce friction, not add cognitive load.

---

### 5.8 Supporting Documentation

NFRs informed by:
- **query-gamification-system-2025-10-21.md**: Section "Non-Functional Requirements" defines token cost targets (≤500 tokens/task), latency constraints (≤10ms), memory limits (≤1MB/session), and agent-agnostic operation requirements

See `supporting-docs/INDEX.md` section "Requirements Insights (Phase 1)" for complete NFR derivation.

---

### 5.9 NFR Summary by Priority

**Critical (Must-Have):**
- NFR-P2: Processing Latency (≤20ms total)
- NFR-R1: Graceful Degradation
- NFR-C1: Agent-Agnostic Operation
- NFR-C2: Backward Compatibility

**High Priority:**
- NFR-P1: Token Cost Efficiency (≤500 tokens/task)
- NFR-P3: Memory Footprint (≤1MB/session)
- NFR-R2: Session Isolation
- NFR-M1: Code Quality (≥90% coverage)
- NFR-M2: Rollback Safety (≤5 min)
- NFR-U1: Non-Intrusive Feedback

**Medium Priority:**
- NFR-R3: Deterministic Behavior
- NFR-M3: Documentation
- NFR-C3: Python Version Compatibility
- NFR-SC1: Horizontal Scaling
- NFR-SC2: Session Count Scaling
- NFR-S1: Session Privacy
- NFR-S2: Injection Safety
- NFR-U2: Actionable Feedback

---

## 6. Out of Scope

Explicitly defines what is NOT included. Items may be considered for future phases.

### Explicitly Excluded

---

#### Features Not Included

**1. User-Facing Dashboard**
- **Description:** Web UI showing query statistics, patterns, and behavioral trends
- **Reason:** Requires agent UI modifications we don't control (Cursor, Cline, Continue). MCP server is backend only.
- **Future Consideration:** Possible in V3 if MCP spec adds UI extension points. Low priority - AI-facing reinforcement is sufficient.
- **Alternative:** AI agent sees feedback directly in search results (current design).

**2. Mandatory Query Gates**
- **Description:** Block AI agent from proceeding to implementation until N queries completed
- **Reason:** Too restrictive. Would break conversational flow for simple tasks. We don't control agent execution loop.
- **Future Consideration:** Not planned. Violates non-intrusive design principle.
- **Alternative:** Behavioral nudges via completion mechanics (current design).

**3. Reward Points System**
- **Description:** Accumulate points for queries, unlock badges/achievements
- **Reason:** Overly complex for the problem. Completion mechanics are simpler and equally effective.
- **Future Consideration:** Not planned. Current gamification mechanics are sufficient.
- **Alternative:** Progress counter + angle coverage + completion message (current design).

**4. Cross-Session Learning & Analytics**
- **Description:** Track query patterns across multiple conversations, identify successful query sequences, recommend patterns
- **Reason:** Adds complexity (requires persistence, data aggregation, pattern analysis). V1 focuses on per-session reinforcement.
- **Future Consideration:** Deferred to V5. Requires database for cross-session state.
- **Alternative:** Per-session tracking only (current design).

**5. Customizable Angle Definitions**
- **Description:** Allow users to define custom query angles beyond the standard 5 (definition, location, practical, best practice, error prevention)
- **Reason:** Adds configuration complexity. Standard 5 angles are well-validated and sufficient for comprehensive discovery.
- **Future Consideration:** Possible in V4 if user demand emerges. Low priority.
- **Alternative:** Fixed 5-angle system (current design).

**6. Historical Query Analytics**
- **Description:** Reports showing query trends over time, angle distribution histograms, session comparisons
- **Reason:** Out of scope for V1. Focus is behavioral reinforcement, not analytics.
- **Future Consideration:** Deferred to V5 with cross-session learning.
- **Alternative:** Real-time per-session feedback only (current design).

**7. Persistent State Across Server Restarts**
- **Description:** Save session state to disk/database, resume after server restart
- **Reason:** Adds complexity (serialization, storage, recovery logic). Conversations typically complete within single server lifetime.
- **Future Consideration:** Only if server stability issues emerge. Low priority.
- **Alternative:** In-memory state only (current design). Session resets are acceptable.

**8. Multi-Language Support**
- **Description:** Angle classification and suggestions in languages other than English
- **Reason:** Keyword-based classification is English-specific. Multi-language requires significant pattern expansion or ML.
- **Future Consideration:** Possible in V6 if international demand. Low priority (AI agents typically use English queries).
- **Alternative:** English only (current design).

**9. Configuration UI**
- **Description:** Admin interface to adjust target query count (5), angle definitions, suggestion templates
- **Reason:** Fixed values are empirically validated. Configuration adds complexity without clear benefit.
- **Future Consideration:** Possible in V3 if A/B testing shows benefit of different targets.
- **Alternative:** Hard-coded defaults (current design). Changes require code modification.

**10. Agent System Prompt Modification**
- **Description:** Inject instructions into agent system prompts (e.g., "You must query 5 times")
- **Reason:** We don't control agent infrastructure (Cursor, Cline, Continue). MCP server is separate process.
- **Future Consideration:** Not possible unless we build our own agent. Out of our control.
- **Alternative:** Behavioral reinforcement via tool responses only (current design).

---

#### User Types Not Supported

**Non-MCP Agents:**
- **Description:** AI agents not using Model Context Protocol (e.g., bare OpenAI API calls, custom agents)
- **Reason:** Gamification is MCP-tool specific. Requires search_standards() tool integration.
- **Future Consideration:** Would require different integration point (e.g., API middleware).
- **Workaround:** None. MCP compatibility required.

---

#### Platforms Not Supported

**Non-Python Environments:**
- **Description:** Gamification in non-Python MCP servers (JavaScript, Go, Rust servers)
- **Reason:** Current implementation is Python-specific. Porting requires rewrite.
- **Future Consideration:** Possible if other language MCP servers gain adoption.
- **Workaround:** Python MCP server only.

---

#### Integrations Not Included

**Workflow System Integration (V1):**
- **Description:** Tie query tracking to workflow phase gates (e.g., Phase 1 requires 5 queries minimum)
- **Reason:** Deferred to V6. Requires workflow engine modification.
- **Future Consideration:** High value but complex. Planned for future enhancement.
- **Workaround:** Query gamification and workflows operate independently in V1.

**External Analytics Platforms:**
- **Description:** Export query statistics to Mixpanel, Amplitude, etc.
- **Reason:** Out of scope for V1. Focus is behavioral reinforcement, not analytics.
- **Future Consideration:** Possible in V5 with analytics feature.
- **Workaround:** None. Manual log inspection only.

---

## 6.1 Future Enhancements

**Potential V2 (2-4 weeks after V1):**
- Adaptive query targets based on task complexity (simple tasks: 3 queries, complex: 7 queries)
- Query quality scoring beyond angle diversity

**Potential V3 (1-2 months):**
- Configuration options (adjust target count, customize suggestion templates)
- Token cost optimization (shorter messages, more efficient formatting)

**Potential V4 (2-3 months):**
- Custom angle definitions for specific domains
- A/B testing framework for gamification variations

**Potential V5 (3-6 months):**
- Cross-session learning (identify successful query patterns)
- Historical analytics and reporting
- Pattern recommendations based on past success

**Potential V6 (6+ months):**
- Workflow system integration (query requirements tied to phase gates)
- Multi-language support for international users
- ML-based angle classification (replace keyword matching)

**Explicitly Not Planned:**
- Mandatory query gates (violates non-intrusive principle)
- Reward points system (unnecessary complexity)
- Agent system prompt modification (not possible with MCP architecture)
- User-facing dashboard (requires agent UI control we don't have)

---

## 6.2 Supporting Documentation

Out-of-scope items from:
- **query-gamification-system-2025-10-21.md**: Section "Non-Goals" explicitly lists user-facing dashboards, mandatory query gates, reward points systems, and cross-session analytics as out of scope. Section "Future Enhancements" outlines V2-V6 roadmap.

See `supporting-docs/INDEX.md` for rationale behind scope decisions.

---

## 6.3 Scope Summary

**In Scope (V1):**
- Per-session query tracking (total, unique, angles, history)
- Real-time feedback via prepend messages
- 5 fixed query angles with keyword-based classification
- Dynamic suggestions for uncovered angles
- Completion acknowledgment at 5/5 queries
- Agent-agnostic operation (Cursor, Cline, Continue)
- In-memory state only (no persistence)

**Out of Scope (V1):**
- User-facing dashboards and analytics UI
- Mandatory query enforcement gates
- Cross-session state and learning
- Customizable angles or configuration UI
- Persistent state across server restarts
- Multi-language support
- Workflow system integration
- Non-MCP agent support

**Boundary Clarity:**
- V1 focuses on **behavioral reinforcement only** (AI-facing feedback)
- V1 avoids **infrastructure complexity** (no persistence, no configuration)
- V1 maintains **simplicity** (fixed angles, hard-coded targets)
- Future versions can add **sophistication** (learning, analytics, customization)

---

## 2.1 Supporting Documentation

The business goals above are informed by:
- **query-gamification-system-2025-10-21.md**: Comprehensive design document with problem analysis, behavioral psychology rationale, token cost analysis, and ROI justification

See `supporting-docs/INDEX.md` for complete analysis and extracted insights.

---

## 2.2 Success Criteria Summary

**Minimum Viable Success:**
- Query count sustained at ≥4 per task throughout conversation
- At least 3 different angles explored per task
- No negative user feedback on distraction/noise
- System deployed and stable within 1 week

**Stretch Goals:**
- 50% increase in queries per task (from 1-2 to 5-10)
- 4+ angles covered in 80% of tasks
- Measurable 20%+ reduction in implementation errors
- Positive user feedback: "AI seems more thorough"

---

## 2.3 Business Context

**Current State:**
- AI agents follow query-first patterns for first 3-5 messages
- After message 10+, query behavior degrades as agents drift to improvisation
- This leads to implementations based on incomplete understanding
- Users spend time correcting "obvious" mistakes the AI could have discovered via querying

**Desired State:**
- AI agents maintain consistent query behavior throughout 50+ message conversations
- Multi-angle exploration becomes standard practice (not exception)
- Implementation quality increases due to comprehensive understanding
- Users receive higher quality output requiring fewer corrections

**Why Now:**
- Project is ~2 weeks old (small user base, low blast radius for experimentation)
- Fast iteration velocity possible (deploy → test → refine in 2-3 day cycles)
- Foundation for future enhancements (workflow integration, cross-session learning)

---

## 2.4 Non-Goals

These are explicitly out of scope for this feature:

- **User-facing dashboards**: Requires agent UI changes we don't control
- **Mandatory query gates**: Would break conversational flow (too restrictive)
- **Reward points systems**: Too complex for the problem; completion mechanics sufficient
- **Cross-session analytics**: Deferred to future enhancement (V5)
- **Agent system prompt modification**: We don't control agent infrastructure

