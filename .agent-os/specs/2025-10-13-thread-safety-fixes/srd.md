# Software Requirements Document

**Project:** Thread Safety Fixes for MCP Server  
**Date:** 2025-10-13  
**Priority:** CRITICAL  
**Category:** Fix / Infrastructure Enhancement

---

## 1. Introduction

### 1.1 Purpose
This document defines the requirements for implementing thread-safe caching mechanisms in the Agent OS MCP server to enable reliable sub-agent concurrent callbacks and dual-transport mode operation without race conditions, memory leaks, or data corruption.

### 1.2 Scope
This feature will:
- Add thread-safe locking to critical cache implementations
- Remove premature cache optimization (metadata cache)
- Implement comprehensive thread safety testing
- Enable production-ready sub-agent architecture
- Improve developer dogfooding experience

This effort affects:
- `mcp_server/workflow_engine.py` (WorkflowEngine class)
- `mcp_server/rag_engine.py` (RAGEngine class)
- `mcp_server/workflow_engine.py` (CheckpointLoader class)
- `tests/` directory (new thread safety tests)

---

## 2. Business Goals

### Goal 1: Enable Sub-Agent Production Deployment

**Objective:** Support multi-agent architecture where sub-agents can make concurrent MCP callbacks without causing system failures, enabling production deployment of complex agent workflows.

**Success Metrics:**
- **Race Condition Failures:** Current state: CERTAIN under concurrent load → Target: ZERO failures in stress tests (100+ concurrent threads)
- **Memory Leaks:** Current: Unbounded session object creation possible → Target: Single session object per ID guaranteed
- **Sub-Agent Reliability:** Current: BLOCKED (cannot deploy) → Target: 100% reliable concurrent callbacks

**Business Impact:**
- Unlocks multi-agent use cases (sub-agent tool invocations)
- Enables horizontal scaling of agent capabilities
- Increases market competitiveness (advanced agent architecture)
- Removes deployment blocker for key customers

**Supporting Documentation:**
- **thread-safety-analysis-2025-10-13.md**: Executive Summary, Section 10 (Conclusion)
  - "...critical thread safety vulnerabilities that **will cause production failures** when sub-agents make concurrent callbacks"
  - "Overall Risk: **HIGH** - Must fix before sub-agent deployment"

### Goal 2: Improve Developer Agility & Dogfooding Experience

**Objective:** Eliminate infrastructure impediments to workflow development by removing premature cache optimizations that require MCP server restarts, enabling rapid iteration and real-time testing of workflow changes.

**Success Metrics:**
- **Metadata Change Latency:** Current: Requires MCP restart (30-60 seconds) → Target: Live immediately (0.06ms load time)
- **Development Velocity:** Current: Restart interrupts flow → Target: Seamless workflow editing
- **Cache Performance Cost:** Added cost: 0.06ms per session (2 loads) → Context: RAG search is 833x slower (50ms)

**Business Impact:**
- Faster workflow development iteration cycles
- Better dogfooding = better product quality
- Reduced developer friction and frustration
- Infrastructure serves developers instead of blocking them

**Supporting Documentation:**
- **thread-safety-analysis-2025-10-13.md**: Section "IMMEDIATE ACTION REQUIRED"
  - "Blocks dogfooding - requires MCP restart to see metadata.json changes"
  - "Analysis: Session-level caching already exists (`WorkflowSession.metadata`), making engine-level cache redundant"
  - Performance data: "0.03ms to load metadata.json"

### Goal 3: Achieve Production-Ready Reliability Standards

**Objective:** Eliminate all critical and high-severity thread safety vulnerabilities to meet production reliability standards, preventing data corruption, intermittent failures, and degraded user experience under concurrent load.

**Success Metrics:**
- **Critical Issues:** Current: 1 (WorkflowEngine._sessions) → Target: 0
- **High Issues:** Current: 1 (RAGEngine._query_cache) → Target: 0
- **Test Coverage:** Current: 0% for thread safety → Target: 100% coverage of concurrent scenarios
- **Stress Test Pass Rate:** Current: N/A (would fail) → Target: 100% (1000+ iterations, 100+ concurrent threads)

**Business Impact:**
- Production deployment confidence
- Eliminates intermittent failures under load
- Protects user data integrity
- Reduces support burden from race-condition bugs
- Meets enterprise reliability expectations

**Supporting Documentation:**
- **thread-safety-analysis-2025-10-13.md**: Section 9 (Risk Assessment)
  - Session double-init: HIGH probability, HIGH impact = **CRITICAL** severity
  - Cache iteration error: MEDIUM probability, HIGH impact = **HIGH** severity
  - "Risk: Sub-agent concurrent calls will cause: race conditions, double-initialization, lost cache updates, data corruption, intermittent failures"

## 2.1 Supporting Documentation

The business goals above are informed by:
- **thread-safety-analysis-2025-10-13.md**: Comprehensive thread safety analysis with independent code review
  - Executive Summary: Risk assessment and impact
  - Section 2: Cache-by-cache vulnerability analysis
  - Section 9: Risk assessment matrix
  - Section 10: Conclusion with recommendations
  - Appendix A: Independent code verification (100% accuracy confirmed)

See `supporting-docs/INDEX.md` for complete document catalog and `supporting-docs/INSIGHTS.md` for extracted requirements insights.

---

## 3. Stakeholders

### 3.1 Primary Stakeholders
- **Sub-Agent Users:** Developers building multi-agent workflows
- **Production Users:** Customers using dual-transport mode (IDE + HTTP)
- **Workflow Developers:** Internal team dogfooding Agent OS workflows

### 3.2 Secondary Stakeholders
- **Platform Team:** Responsible for MCP server reliability
- **Support Team:** Handle escalations from race condition bugs
- **Enterprise Customers:** Require production-grade reliability

---

## 4. User Stories

User stories describe the feature from the user's perspective, focusing on user needs and desired outcomes rather than technical solutions.

### Story Format

**As a** {user type}  
**I want to** {capability}  
**So that** {benefit}

---

### Story 1: Sub-Agent Concurrent MCP Callbacks

**As a** sub-agent invoked by a workflow tool  
**I want to** make HTTP MCP callbacks to the server (start_workflow, get_task, complete_phase, search_standards)  
**So that** I can access workflow orchestration, RAG knowledge retrieval, and state management capabilities  
**Without** causing race conditions, memory leaks, or data corruption in the parent MCP server

**Acceptance Criteria:**
- **Given** I am a sub-agent running as a separate process
- **When** I make concurrent MCP HTTP calls while the main IDE is also making stdio calls
- **Then** all my requests are handled correctly without:
  - Creating duplicate WorkflowSession objects (memory leaks)
  - Cache corruption or inconsistency
  - RuntimeError exceptions from cache iteration
  - State divergence between threads

**Priority:** CRITICAL (blocks sub-agent deployment)

**Supporting Documentation:**
- **thread-safety-analysis-2025-10-13.md**: Section 1.2 (Sub-Agent Invocation Pattern), Scenario 2

---

### Story 2: Dual Transport Concurrent Usage

**As a** user running the MCP server in dual mode (stdio + HTTP)  
**I want** concurrent requests from my IDE (stdio) and sub-agents (HTTP) to be handled safely  
**So that** I can use advanced multi-agent workflows without system instability or failures

**Acceptance Criteria:**
- **Given** MCP server is running in dual-transport mode
- **When** my IDE and a sub-agent make concurrent calls to the same workflow
- **Then** the system:
  - Maintains consistent state across both transports
  - Prevents duplicate expensive operations (session creation, metadata loading)
  - Returns the same cached objects to both threads
  - Does not leak memory or accumulate orphaned objects

**Priority:** CRITICAL (blocks production deployment)

**Supporting Documentation:**
- **thread-safety-analysis-2025-10-13.md**: Section 1.1 (Transport Modes), Section 3 (Attack Scenarios)

---

### Story 3: Rapid Workflow Development Iteration

**As a** workflow developer dogfooding Agent OS  
**I want** changes to workflow metadata.json to take effect immediately  
**So that** I can iterate quickly on workflow design without restarting the MCP server

**Acceptance Criteria:**
- **Given** I am developing a workflow with metadata.json
- **When** I update metadata.json fields (add phases, change tasks, update descriptions)
- **Then** the next workflow start reflects my changes immediately
- **Without** requiring MCP server restart (30-60 second interruption)
- **And** the performance cost is negligible (<1ms)

**Priority:** HIGH (improves developer experience)

**Supporting Documentation:**
- **thread-safety-analysis-2025-10-13.md**: Section "IMMEDIATE ACTION REQUIRED" (Metadata Cache Removal)

---

### Story 4: Reliable Stress Testing

**As a** platform engineer validating production readiness  
**I want** thread safety test coverage for concurrent scenarios  
**So that** I can verify the system behaves correctly under heavy concurrent load before deployment

**Acceptance Criteria:**
- **Given** I am running the test suite
- **When** I execute thread safety tests with 100+ concurrent threads
- **Then** all tests pass consistently (1000+ iterations)
- **And** tests cover:
  - Concurrent session creation (no duplicates)
  - Concurrent RAG cache access (no iteration errors)
  - Dual transport integration (no race conditions)
  - Cache metrics validation (detect double-loads)

**Priority:** HIGH (production readiness requirement)

**Supporting Documentation:**
- **thread-safety-analysis-2025-10-13.md**: Section 6 (Testing Strategy), Appendix A.4 (Test Coverage Gaps)

---

## 4.1 Story Priority Summary

**Critical (Must-Have):**
- Story 1: Sub-Agent Concurrent MCP Callbacks - Enables multi-agent architecture
- Story 2: Dual Transport Concurrent Usage - Production deployment requirement

**High Priority:**
- Story 3: Rapid Workflow Development Iteration - Developer experience improvement
- Story 4: Reliable Stress Testing - Production validation requirement

**User Personas:**
1. **Sub-Agent Process** (primary) - Autonomous agent making MCP callbacks
2. **Workflow Developer** (primary) - Internal team building workflows
3. **Platform Engineer** (secondary) - Validating production readiness
4. **End Users** (indirect) - Benefit from reliable multi-agent workflows

## 4.2 Supporting Documentation

User needs from supporting documents:
- **thread-safety-analysis-2025-10-13.md**: 
  - Sub-agent architecture requirements (Executive Summary, Section 1.2)
  - Developer dogfooding pain points (Immediate Action section)
  - Test coverage gaps identified (Section 6, Appendix A.4)
  - Production reliability requirements (Section 9, Risk Assessment)

See `supporting-docs/INSIGHTS.md` for complete extraction of user stories (3 stories with full traceability).

---

## 5. Functional Requirements

Functional requirements specify concrete capabilities the system must provide to satisfy user stories and business goals.

---

### FR-001: Thread-Safe Session Cache

**Description:** The system shall prevent duplicate WorkflowSession object creation when multiple threads concurrently request the same session ID through WorkflowEngine.get_session().

**Priority:** CRITICAL

**Related User Stories:** Story 1 (Sub-Agent Concurrent Callbacks), Story 2 (Dual Transport Usage)

**Related Business Goals:** Goal 1 (Sub-Agent Production Deployment), Goal 3 (Production Reliability)

**Acceptance Criteria:**
- When 10+ threads concurrently call `get_session(session_id)` for the same ID, exactly ONE WorkflowSession object is created
- All threads receive a reference to the SAME WorkflowSession instance (verified by `id(session)`)
- No orphaned session objects are created (memory leak prevention)
- Cache check-then-create pattern is protected by threading.RLock
- Double-checked locking pattern implemented (fast path without lock, re-check inside lock)
- Test passes 1000+ iterations with 100+ concurrent threads

**Supporting Documentation:**
- **thread-safety-analysis-2025-10-13.md**: Section 2.2 (WorkflowEngine._sessions Analysis), Scenario 2 (Session Double-Initialization)

---

### FR-002: Consistent RAG Cache Locking

**Description:** The system shall protect all RAGEngine._query_cache operations (read, write, cleanup) with consistent lock acquisition to prevent iteration errors and cache inconsistency.

**Priority:** HIGH

**Related User Stories:** Story 1 (Sub-Agent Concurrent Callbacks), Story 2 (Dual Transport Usage)

**Related Business Goals:** Goal 3 (Production Reliability)

**Acceptance Criteria:**
- `_check_cache()` method acquires lock before reading cache
- `_clean_cache()` method is only called while lock is held
- Cache cleanup uses `list(cache.items())` copy to prevent iteration-during-modification errors
- No RuntimeError: "dictionary changed size during iteration" occurs under concurrent load
- Concurrent searches and cache cleanup execute without crashes (100+ iterations)
- Lock is reentrant (RLock) to prevent deadlock if same thread re-enters

**Supporting Documentation:**
- **thread-safety-analysis-2025-10-13.md**: Section 2.4 (RAGEngine._query_cache Analysis), Scenario 3 (Cache Cleanup During Iteration)

---

### FR-003: Metadata Cache Removal

**Description:** The system shall load workflow metadata.json on-demand without engine-level caching, enabling immediate reflection of metadata changes during development.

**Priority:** CRITICAL (COMPLETED ✅)

**Related User Stories:** Story 3 (Rapid Workflow Development Iteration)

**Related Business Goals:** Goal 2 (Developer Agility & Dogfooding)

**Acceptance Criteria:**
- WorkflowEngine._metadata_cache removed entirely from codebase
- `load_workflow_metadata()` loads from disk on each call
- Session-level caching (WorkflowSession.metadata) remains intact
- Performance overhead ≤ 0.1ms per metadata load (measured: 0.03ms)
- Metadata.json changes take effect on next workflow start without MCP restart
- No stale metadata issues during development

**Status:** COMPLETED 2025-10-13 (prior to spec creation)

**Supporting Documentation:**
- **thread-safety-analysis-2025-10-13.md**: Section "IMMEDIATE ACTION REQUIRED", Performance analysis showing 0.03ms load time

---

### FR-004: Thread Safety Test Coverage

**Description:** The system shall include comprehensive automated tests that validate thread-safe behavior of cache implementations under concurrent load.

**Priority:** HIGH

**Related User Stories:** Story 4 (Reliable Stress Testing)

**Related Business Goals:** Goal 3 (Production Reliability)

**Acceptance Criteria:**
- Unit test `test_concurrent_session_creation()` verifies single session per ID under 10+ concurrent threads
- Unit test `test_concurrent_rag_cache_access()` verifies no iteration errors during concurrent searches + cleanup
- Unit test `test_checkpoint_cache_thread_safety()` verifies CheckpointLoader locking
- Integration test `test_dual_transport_concurrent_workflow_start()` simulates stdio + HTTP concurrent calls
- All tests run in CI/CD pipeline on every commit
- Tests pass consistently (1000+ iterations without failures)
- Test execution time < 30 seconds for full thread safety suite

**Supporting Documentation:**
- **thread-safety-analysis-2025-10-13.md**: Section 6 (Testing Strategy), Appendix A.4 (Test Coverage Gaps)

---

### FR-005: CheckpointLoader Thread Safety

**Description:** The system shall protect CheckpointLoader._checkpoint_cache with thread-safe locking to prevent duplicate checkpoint loads under concurrent access.

**Priority:** MEDIUM

**Related User Stories:** Story 2 (Dual Transport Usage)

**Related Business Goals:** Goal 3 (Production Reliability)

**Acceptance Criteria:**
- CheckpointLoader adds `_cache_lock: threading.RLock`
- `load_checkpoint_requirements()` implements double-checked locking pattern
- Concurrent checkpoint loads for same workflow+phase return same cached object
- No duplicate RAG queries for same checkpoint under concurrent access
- Performance: Cache hits require <1ns (no lock acquisition on fast path)

**Supporting Documentation:**
- **thread-safety-analysis-2025-10-13.md**: Section 2.3 (CheckpointLoader Analysis), Section 5.1 (Solution)

---

### FR-006: Cache Performance Monitoring

**Description:** The system shall provide metrics and logging to detect race conditions, measure cache effectiveness, and monitor lock contention in production.

**Priority:** MEDIUM

**Related User Stories:** Story 4 (Reliable Stress Testing)

**Related Business Goals:** Goal 3 (Production Reliability)

**Acceptance Criteria:**
- CacheMetrics class tracks: hits, misses, double_loads, lock_waits
- Logger warns when double-load detected: "Race detected - double load occurred"
- Metrics accessible via server info tool or log aggregation
- Performance profiling shows lock_waits < 5% of total requests
- Metrics help validate that fixes prevent races (double_loads = 0)

**Supporting Documentation:**
- **thread-safety-analysis-2025-10-13.md**: Section 7 (Monitoring & Observability)

---

## 5.1 Requirements by Category

### Thread Safety (Critical)
- FR-001: Thread-Safe Session Cache
- FR-002: Consistent RAG Cache Locking
- FR-003: Metadata Cache Removal (COMPLETED ✅)
- FR-005: CheckpointLoader Thread Safety

### Testing & Validation (High)
- FR-004: Thread Safety Test Coverage

### Observability (Medium)
- FR-006: Cache Performance Monitoring

---

## 5.2 Traceability Matrix

| Requirement | User Stories | Business Goals | Priority | Status |
|-------------|--------------|----------------|----------|--------|
| FR-001 | Story 1, 2 | Goal 1, 3 | CRITICAL | Planned |
| FR-002 | Story 1, 2 | Goal 3 | HIGH | Planned |
| FR-003 | Story 3 | Goal 2 | CRITICAL | COMPLETED ✅ |
| FR-004 | Story 4 | Goal 3 | HIGH | Planned |
| FR-005 | Story 2 | Goal 3 | MEDIUM | Planned |
| FR-006 | Story 4 | Goal 3 | MEDIUM | Planned |

**Summary:** 6 functional requirements (1 completed, 5 planned)
- Critical: 2 (1 completed, 1 planned)
- High: 2 (planned)
- Medium: 2 (planned)

---

## 5.3 Supporting Documentation

Functional requirements derived from:
- **thread-safety-analysis-2025-10-13.md**: 
  - Section 2: Cache-by-cache vulnerability analysis (source for FR-001, FR-002, FR-005)
  - Section "IMMEDIATE ACTION": Metadata cache removal rationale (FR-003)
  - Section 6: Testing strategy recommendations (FR-004)
  - Section 7: Monitoring and observability needs (FR-006)

See `supporting-docs/INSIGHTS.md` for complete FR extraction (4 original FRs + 2 derived = 6 total).

---

## 6. Non-Functional Requirements

Non-functional requirements define quality attributes and system constraints that specify HOW WELL the system must perform.

---

### 6.1 Performance

**NFR-P1: Lock Overhead Minimization**
- **Requirement:** Thread-safe locking mechanisms must have minimal performance impact on cache operations
- **Measurement Criteria:**
  - Cache hit (fast path): < 1 nanosecond overhead (no lock acquisition)
  - Cache miss (slow path): Lock acquisition overhead < 10 microseconds
  - 95th percentile latency increase: < 5% compared to pre-fix baseline
  - Throughput degradation: < 5% compared to pre-fix baseline
- **Target:** Zero-cost abstraction for cache hits through double-checked locking
- **Test Method:** Benchmark before/after with 1000+ iterations, measure p50/p95/p99 latencies

**NFR-P2: Metadata Load Performance**
- **Requirement:** On-demand metadata loading must have negligible performance impact
- **Measurement Criteria:**
  - Single metadata.json load time: ≤ 0.1ms (measured: 0.03ms)
  - Per-session overhead: ≤ 0.2ms (2 loads max per session)
  - Comparison context: RAG search ~50ms (250x slower), acceptable
- **Target:** Performance cost justified by developer agility gain
- **Test Method:** Measure load time across 1000+ iterations

**Supporting Documentation:**
- **thread-safety-analysis-2025-10-13.md**: Section 5.1 (Double-Checked Locking Performance), Performance analysis showing 0.03ms metadata load

---

### 6.2 Reliability

**NFR-R1: Zero Race Conditions**
- **Requirement:** System must eliminate all race conditions under concurrent load
- **Measurement Criteria:**
  - Concurrent session creation test: 0 duplicate sessions (1000+ iterations, 100+ threads)
  - Cache iteration test: 0 RuntimeError exceptions (1000+ iterations)
  - Metrics validation: `metrics.double_loads = 0` after fixes
  - Stress test pass rate: 100% (no intermittent failures)
- **Target:** Guaranteed correctness under all concurrent scenarios
- **Test Method:** Automated stress tests in CI/CD, run on every commit

**NFR-R2: Zero Memory Leaks**
- **Requirement:** System must not create orphaned objects or accumulate memory under concurrent access
- **Measurement Criteria:**
  - Memory profiling: No unbounded growth over 1000+ workflow sessions
  - Session count: Exactly one WorkflowSession per session_id (verified by object ID)
  - Cache size: Bounded by TTL and max size limits
  - Long-running test (1 hour): Memory usage stable (no leak)
- **Target:** Constant memory footprint (no accumulation)
- **Test Method:** Memory profiler (tracemalloc), long-running stress test

**NFR-R3: Production Uptime**
- **Requirement:** Thread safety fixes must not introduce new failure modes
- **Measurement Criteria:**
  - Server stability: No crashes related to locking or cache operations
  - Deadlock prevention: RLock reentrant, no circular wait conditions
  - Graceful degradation: Lock timeout with error logging (not hang)
  - Mean time between failures: > 720 hours (30 days continuous operation)
- **Target:** Production-grade reliability
- **Test Method:** Canary deployment, staged rollout with monitoring

**Supporting Documentation:**
- **thread-safety-analysis-2025-10-13.md**: Section 9 (Risk Assessment), Section 10 (Conclusion on reliability requirements)

---

### 6.3 Maintainability

**NFR-M1: Consistent Locking Patterns**
- **Requirement:** All cache implementations must use consistent, well-documented locking patterns
- **Measurement Criteria:**
  - Single locking pattern: RLock with double-checked locking
  - Code consistency: All caches use same pattern (no mix of strategies)
  - Documentation: Inline comments explain fast path / slow path / re-check
  - Code review: Locking patterns approved by 2+ reviewers
- **Target:** Maintainable, understandable, reviewable code
- **Test Method:** Code review checklist, linting rules for lock patterns

**NFR-M2: Test Coverage**
- **Requirement:** Thread safety code must have comprehensive test coverage
- **Measurement Criteria:**
  - Line coverage for modified files: ≥ 95%
  - Branch coverage: ≥ 90%
  - Thread safety specific tests: 100% coverage of critical paths
  - Test documentation: Each test explains race condition it prevents
- **Target:** No untested concurrent code paths
- **Test Method:** pytest-cov, coverage.py reports

**NFR-M3: Code Quality**
- **Requirement:** Thread safety fixes must meet production code standards
- **Measurement Criteria:**
  - Linting: 0 errors, 0 warnings (ruff, mypy)
  - Type hints: 100% on all modified functions
  - Docstrings: Sphinx-style for all public methods
  - Complexity: Cyclomatic complexity ≤ 10 per function
- **Target:** Production-grade code quality
- **Test Method:** Automated linting in CI/CD

**Supporting Documentation:**
- **thread-safety-analysis-2025-10-13.md**: Section 5.1 (Solution Quality), Section 8 (Recommendations for consistency)

---

### 6.4 Observability

**NFR-O1: Cache Metrics**
- **Requirement:** System must provide visibility into cache behavior and race detection
- **Measurement Criteria:**
  - Metrics tracked: hits, misses, double_loads, lock_waits
  - Logging: Warning when race detected (double_load > 0)
  - Accessibility: Metrics via server_info tool or Prometheus export
  - Granularity: Per-cache metrics (sessions, rag_cache, checkpoints)
- **Target:** Real-time race detection and performance monitoring
- **Test Method:** Validate metrics collection, verify logging output

**NFR-O2: Lock Contention Monitoring**
- **Requirement:** System must detect and report lock contention issues
- **Measurement Criteria:**
  - Lock wait percentage: Tracked and logged
  - Threshold alert: Warning if lock_waits > 5% of requests
  - Performance profiling: Ability to measure hold time, wait time
  - Dashboard: Grafana/similar visualization of lock metrics
- **Target:** Proactive detection of lock contention problems
- **Test Method:** Synthetic load test, measure lock_waits under various loads

**Supporting Documentation:**
- **thread-safety-analysis-2025-10-13.md**: Section 7 (Monitoring & Observability)

---

### 6.5 Security

**NFR-S1: Thread Safety as Security Concern**
- **Requirement:** Race conditions must be treated as security vulnerabilities (potential DoS via memory exhaustion)
- **Measurement Criteria:**
  - Vulnerability classification: Memory leak race = HIGH severity
  - Security review: Thread safety fixes reviewed by security team
  - Threat model: Document race → memory exhaustion → DoS attack vector
  - Mitigation validation: Stress test confirms no unbounded resource consumption
- **Target:** Eliminate security-relevant race conditions
- **Test Method:** Security threat modeling, penetration testing (concurrent load)

**Supporting Documentation:**
- **thread-safety-analysis-2025-10-13.md**: Security implications in Section 2.2 (memory leak → DoS)

---

## 6.6 Non-Functional Requirements Summary

**By Category:**
- Performance: 2 NFRs (lock overhead, metadata load performance)
- Reliability: 3 NFRs (zero races, zero leaks, production uptime)
- Maintainability: 3 NFRs (consistent patterns, test coverage, code quality)
- Observability: 2 NFRs (cache metrics, lock contention monitoring)
- Security: 1 NFR (thread safety as security concern)

**Total:** 11 non-functional requirements

**Priority Matrix:**
- CRITICAL: NFR-R1 (Zero Race Conditions), NFR-R2 (Zero Memory Leaks)
- HIGH: NFR-P1 (Lock Overhead), NFR-M2 (Test Coverage), NFR-O1 (Cache Metrics)
- MEDIUM: NFR-M1 (Consistent Patterns), NFR-M3 (Code Quality), NFR-R3 (Uptime), NFR-O2 (Lock Contention), NFR-S1 (Security), NFR-P2 (Metadata Performance)

---

## 6.7 Supporting Documentation

Non-functional requirements derived from:
- **thread-safety-analysis-2025-10-13.md**:
  - Performance requirements: Section 5.1 (Fast Path Optimization)
  - Reliability requirements: Section 9 (Risk Assessment), Section 10 (Conclusion)
  - Maintainability requirements: Section 5.1 (Consistent Patterns)
  - Observability requirements: Section 7 (Monitoring & Observability)
  - Security implications: Section 2.2 (Memory leak as DoS vector)

See `supporting-docs/INSIGHTS.md` for complete NFR extraction (4 original NFRs + 7 derived = 11 total).

---

## 7. Out of Scope

Explicitly defines what is NOT included in this implementation. Items may be considered for future phases. Defining boundaries prevents scope creep and manages expectations.

### Explicitly Excluded

---

#### Features

**Not Included in This Release:**

1. **Lock-Free Data Structures**
   - **Reason:** Complexity too high for immediate need; lock-based solution adequate for current scale
   - **Analysis:** Lock-free programming requires deep expertise, difficult to verify correctness
   - **Performance:** Double-checked locking provides <1ns overhead on cache hits (sufficient)
   - **Future Consideration:** P3 (Long term) - Only if lock contention becomes measurable problem (>5% of requests)
   - **Source:** thread-safety-analysis Section 8 (Recommendations)

2. **Distributed / Multi-Process Caching**
   - **Reason:** Single-process scope; no immediate requirement for cross-process coordination
   - **Analysis:** Current architecture uses single MCP server process with multiple threads
   - **Performance:** In-process caching sufficient for current workload
   - **Future Consideration:** P3 (Long term) - Required only for horizontal server scaling across processes
   - **Source:** thread-safety-analysis Section 8 (Recommendations)

3. **Comprehensive Performance Profiling**
   - **Reason:** P2 (Medium term) - Should be done AFTER thread safety fixes are validated
   - **Analysis:** Need baseline correctness before optimizing performance
   - **Approach:** Profile lock contention, measure latency before/after, identify bottlenecks
   - **Future Consideration:** P2 (Next sprint) - After thread safety tests pass and fixes deploy to staging
   - **Source:** thread-safety-analysis Section 8 (Recommendations)

4. **Alternative Locking Strategies**
   - **Reason:** Single standardized approach (RLock + double-checked locking) sufficient
   - **Alternatives Considered:** ThreadSafeDict wrapper, threading.local() per-thread caches
   - **Decision:** Standardization > variety; reduces cognitive load for reviewers
   - **Future Consideration:** Only if evidence shows current approach insufficient
   - **Source:** thread-safety-analysis Section 5 (Alternative solutions)

5. **Automatic Deadlock Detection**
   - **Reason:** P2/P3 - Nice-to-have; prevention (RLock reentrant, consistent order) is primary strategy
   - **Analysis:** RLock prevents same-thread deadlock; lock order consistency prevents cross-thread deadlock
   - **Monitoring:** Timeout logging can detect hangs
   - **Future Consideration:** P3 - Only if production deadlocks occur despite prevention measures
   - **Source:** thread-safety-analysis Section 8 (Recommendations)

---

#### Platforms & Environments

**Not Affected / Out of Scope:**

1. **Windows-Specific Threading**
   - **Reason:** Python threading abstraction handles platform differences
   - **Analysis:** threading.RLock works identically on macOS, Linux, Windows
   - **Validation:** Current test suite runs on macOS; CI/CD should test on Linux
   - **Future:** Cross-platform testing already covered by Python stdlib

2. **Asyncio Event Loop Modifications**
   - **Reason:** Event loop behavior does not need changes; shared state protection is sufficient
   - **Analysis:** Each thread has separate event loop; locks protect shared state across loops
   - **Out of Scope:** Changing FastMCP's event loop architecture
   - **Source:** thread-safety-analysis Section 4.2 (Asyncio clarification)

---

#### Components

**Not Modified:**

1. **StateManager File Locking**
   - **Reason:** Already thread-safe; uses OS-level fcntl locks
   - **Analysis:** File-based locking is correct and performant
   - **Decision:** No changes needed (verified safe in analysis)
   - **Source:** thread-safety-analysis Section 2.6 (StateManager verified safe)

2. **DynamicContentRegistry**
   - **Reason:** Session-scoped; no sharing between threads
   - **Analysis:** Each WorkflowSession has its own registry; isolated
   - **Decision:** No thread safety needed (no shared state)
   - **Source:** thread-safety-analysis Section 2.7 (Registry verified safe)

3. **Transport Layer (stdio / HTTP)**
   - **Reason:** Transport threading architecture is correct; only cache layer needs fixes
   - **Analysis:** Dual transport mode itself is not the issue; shared cache access is
   - **Decision:** No changes to TransportManager or FastMCP integration
   - **Source:** thread-safety-analysis Section 1.1 (Architecture analysis)

---

#### Testing & Validation

**Not Included:**

1. **Load Testing / Stress Testing Beyond Functional Validation**
   - **Reason:** Functional correctness focus; performance benchmarking is P2
   - **This Release:** Tests validate correctness (no races, no leaks) under concurrent load
   - **Out of Scope:** Production-scale load testing (1000+ RPS sustained), capacity planning
   - **Future Consideration:** P2 - After fixes deployed to staging

2. **Sub-Agent Implementation Testing**
   - **Reason:** Testing sub-agent framework itself is separate effort
   - **This Release:** Simulate sub-agent pattern (HTTP MCP callbacks) but don't build full sub-agent
   - **Out of Scope:** End-to-end sub-agent workflow validation
   - **Future Consideration:** Separate effort by sub-agent team

---

## 7.1 Future Enhancements

**Potential Phase 2 (Short Term, 1-2 sprints):**
- Comprehensive performance profiling under production-like load
- Lock contention analysis and optimization (if needed)
- Extended stress testing (1000+ RPS, 24+ hour runs)
- Grafana dashboards for cache metrics visualization

**Potential Phase 3 (Long Term, 3-6 months):**
- Lock-free data structures (only if lock contention > 5% measured)
- Distributed caching for multi-process scaling
- Deadlock detection and automated recovery tooling
- Advanced thread safety patterns (read-write locks, fine-grained locking)

**Explicitly Not Planned:**
- Custom threading primitives (Python stdlib sufficient)
- Green threads / coroutine-based concurrency (asyncio already used correctly)
- Thread pool tuning (not identified as bottleneck)

---

## 7.2 Supporting Documentation

Out-of-scope items from:
- **thread-safety-analysis-2025-10-13.md**:
  - Section 5: Alternative solutions evaluated but not selected
  - Section 8: Recommendations showing priority (P0/P1/P2/P3)
  - Section 2.6, 2.7: Components verified safe (no changes needed)

See `supporting-docs/INSIGHTS.md` for complete out-of-scope extraction (3 original items + 12 derived = 15 total).

---

## 7.3 Out-of-Scope Summary

**By Category:**
- Features: 5 items (lock-free, distributed cache, profiling, alternative strategies, deadlock detection)
- Platforms: 2 items (Windows-specific, asyncio modifications)
- Components: 3 items (StateManager, DynamicContentRegistry, TransportLayer)
- Testing: 2 items (load testing, sub-agent testing)

**Total:** 15 out-of-scope items with clear rationale

**Priority for Future:**
- P1 (Next Sprint): None - this spec is complete and sufficient
- P2 (Short Term): Performance profiling, extended stress testing, metrics visualization
- P3 (Long Term): Lock-free structures, distributed caching, deadlock detection

---

## 8. Summary

### Requirements Overview

**Business Goals:** 3 goals with metrics
- Sub-agent production deployment (CRITICAL)
- Developer agility & dogfooding (HIGH)
- Production reliability standards (CRITICAL)

**User Stories:** 4 stories with acceptance criteria
- 2 CRITICAL (sub-agent callbacks, dual transport)
- 2 HIGH (rapid iteration, stress testing)

**Functional Requirements:** 6 requirements
- 2 CRITICAL (1 completed: metadata cache removal; 1 planned: session cache)
- 2 HIGH (RAG locking, test coverage)
- 2 MEDIUM (checkpoint cache, metrics)

**Non-Functional Requirements:** 11 requirements across 5 categories
- Performance: 2 NFRs
- Reliability: 3 NFRs (2 CRITICAL)
- Maintainability: 3 NFRs
- Observability: 2 NFRs
- Security: 1 NFR

**Out of Scope:** 15 items with rationale and future consideration

---

### Phase 1 Complete

✅ **srd.md** is complete with:
- Introduction and scope definition
- Stakeholder identification
- Comprehensive business goals with metrics
- User stories with acceptance criteria
- Functional requirements (6 FRs with traceability)
- Non-functional requirements (11 NFRs across 5 categories)
- Out-of-scope boundaries (15 items)
- Full traceability to supporting documentation

**Total Artifacts:**
- Supporting documents: 1 (thread-safety-analysis, 51KB)
- Insights extracted: 58 (16 req, 18 design, 24 implementation)
- Requirements defined: 17 (6 FR + 11 NFR)
- User stories: 4 (2 critical, 2 high)
- Business goals: 3 (2 critical, 1 high)

**Ready for Phase 2:** Technical Design (specs.md)

---

**END OF SOFTWARE REQUIREMENTS DOCUMENT**

