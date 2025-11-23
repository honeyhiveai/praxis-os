# Software Requirements Document

**Project:** IndexManager Thread Safety, Hot Reload, and Dynamic Logic Implementation  
**Date:** 2025-11-20  
**Priority:** Critical (P0 for thread safety, P1 for hot reload)  
**Category:** Enhancement + Technical Debt

---

## 1. Introduction

### 1.1 Purpose
This document defines the requirements for making IndexManager thread-safe through consistent lock usage, implementing a hot reload API for dynamic index management, and ensuring architectural consistency with project patterns.

### 1.2 Scope
This feature will:
- Add thread safety protections to all 12 access sites of `_indexes` dictionary
- Implement hot reload capability (add/remove/reload indexes at runtime)
- Maintain architectural consistency with WorkflowEngine threading patterns
- Leverage existing fractal patterns and INDEX_REGISTRY for dynamic logic
- Comply with 4 project concurrency standards

**Out of Scope:**
- Rewriting entire threading model from scratch
- Performance optimization (no performance problems exist)
- External synchronization libraries
- Async-only refactoring

---

## 2. Business Goals

### Goal 1: Eliminate Concurrency Standards Violations

**Objective:** Achieve 100% compliance with project concurrency standards in IndexManager to prevent silent data corruption and ensure code quality.

**Success Metrics:**
- **Standards Compliance:** 0/4 standards → 4/4 standards compliant
  - `python-concurrency.md`: Consistent lock usage
  - `race-conditions.md`: Protected shared state
  - `shared-state-analysis.md`: Documented threading model
  - `production-code-checklist.md`: Validated with tests
- **Lock Coverage:** 1/12 access sites protected → 12/12 access sites protected
- **Test Coverage:** 0 concurrent access tests → 3 comprehensive test suites
- **Documentation:** 0 threading docs → Complete threading model documented

**Business Impact:**
- **Risk Reduction:** Prevents potential silent data corruption in production
- **Code Quality:** Aligns with project quality standards and best practices
- **Technical Debt:** Eliminates architectural debt before multi-repo scaling
- **Maintainability:** Future developers understand threading model explicitly

**Rationale:**
Current implementation violates 4 concurrency standards despite working correctly in single-repo deployments. This "accidental safety" via Python GIL is not documented and creates risk for future changes. Multi-repo scaling (10+ repos, 50+ indexes) introduces uncertainty that must be eliminated.

---

### Goal 2: Enable Confident Multi-Repo Scaling

**Objective:** Provide evidence-based assurance that IndexManager can reliably handle multi-repo code intelligence deployments with 10+ repositories and 50+ indexes.

**Success Metrics:**
- **Deployment Confidence:** "Accidentally safe" → Evidence-based validation
- **Concurrent Operations:** Tested with 100 threads × 1000 operations = 100k operations
- **Index Count Support:** Validated with 10+ concurrent indexes
- **Query Throughput:** No measurable degradation (<1% overhead) under concurrent load
- **Documentation:** 0 capacity planning docs → Multi-repo deployment guidelines

**Business Impact:**
- **Product Capability:** Unlocks multi-repo deployments for enterprise customers
- **Customer Trust:** Evidence-based assurance vs. "it should work"
- **Support Costs:** Reduces debugging time for scaling issues
- **Sales Enablement:** Clear capacity limits for deployment planning

**Rationale:**
Current single-repo deployments work, but multi-repo scaling introduces 10x increase in concurrent index access. Without explicit thread safety validation, deployments operate on assumptions rather than proven capability.

---

### Goal 3: Future-Proof for Dynamic Repo Management

**Objective:** Enable hot reload capability to add/remove/reload indexes at runtime without server restart, supporting dynamic configuration management use cases.

**Success Metrics:**
- **Reload Capability:** Manual restart required → Runtime add/remove/reload
- **Atomic Operations:** Queries see consistent state during reload
- **Zero Downtime:** No query failures during index swap
- **Config Driven:** Adding new repo requires 0 code changes (INDEX_REGISTRY)
- **API Completion:** 3 new methods (add_index, remove_index, reload_indexes)

**Business Impact:**
- **Developer Experience:** Add new repo → Reload config → Index created (no restart)
- **Operational Efficiency:** Eliminates server restart downtime
- **Extensibility:** New index types added via config, not code changes
- **Maintenance Cost:** Reduced deployment friction for config changes

**Use Case:**
User adds new repository to config, issues reload command, index is created and available for queries immediately. No manual restart, no downtime, no code changes.

**Rationale:**
Current design requires server restart to add new indexes. Hot reload aligns with project's config-driven architecture patterns and enables more flexible deployment workflows.

---

### Goal 4: Maintain Architectural Consistency

**Objective:** Ensure IndexManager threading patterns match WorkflowEngine (proven in production) and leverage project's fractal architecture patterns.

**Success Metrics:**
- **Pattern Consistency:** IndexManager threading diverges → Matches WorkflowEngine RLock pattern
- **Fractal Alignment:** Hot reload uses same fractal patterns as existing subsystems
- **Registry Usage:** Static patterns → Dynamic INDEX_REGISTRY-driven logic
- **Code Review:** Human validation confirms architectural consistency

**Business Impact:**
- **Codebase Coherence:** Consistent patterns across subsystems
- **Onboarding Speed:** New developers recognize familiar patterns
- **Maintainability:** Changes follow established architectural principles
- **Quality Assurance:** Proven patterns reduce risk of architectural mistakes

**Validation:**
WorkflowEngine uses `RLock` for `_dynamic_sessions` dict (identical pattern to IndexManager's `_indexes` dict). This proves the pattern works in production under similar concurrent access scenarios.

**Rationale:**
Architectural consistency reduces cognitive load for maintainers and ensures new features follow proven patterns. Divergent approaches create fragmentation and increase maintenance burden.

---

## 2.1 Supporting Documentation

The business goals above are informed by:
- **Design Document** (`2025-11-20-indexmanager-thread-safety.md`): Problem statement with 4 standards violations, current state analysis with 12 access sites, and 3 options considered
- **Threading Analysis** (`2025-11-20-threading-model-deep-dive.md`): Identified 4 concurrent execution contexts and "accidental safety" via GIL
- **RLock Analysis** (`2025-11-20-rlock-analysis.md`): Proved RLock necessity with 3 re-entrant call chains
- **Open Questions Analysis** (`2025-11-20-open-questions-analysis.md`): Resolved hot reload approach and observability strategy
- **Fractal Pattern Analysis** (`2025-11-20-fractal-pattern-analysis.md`): Documented architectural patterns for consistent implementation

See `supporting-docs/INDEX.md` for complete cross-reference mapping and `supporting-docs/INSIGHTS.md` for 47 categorized findings.

---

## 2.2 Business Goals Summary

| Goal | Priority | Impact | Validation |
|------|----------|--------|------------|
| **Standards Compliance** | P0 (Critical) | Risk reduction, code quality | 4/4 standards met, 12/12 sites protected |
| **Multi-Repo Scaling** | P0 (Critical) | Product capability, customer trust | 100k concurrent operations validated |
| **Hot Reload** | P1 (High) | Developer experience, operational efficiency | 3 API methods, atomic swap tested |
| **Architectural Consistency** | P1 (High) | Maintainability, onboarding | Pattern matches WorkflowEngine |

---

## 3. User Stories

User stories describe the feature from the user's perspective, focusing on needs and outcomes rather than technical solutions.

### Story Format

**As a** {user type}  
**I want to** {capability}  
**So that** {benefit}

---

### Story 1: Confident Multi-Repo Deployment

**As a** DevOps Engineer deploying Agent OS for enterprise customers  
**I want to** have evidence-based validation that IndexManager handles 10+ repositories concurrently  
**So that** I can confidently deploy multi-repo configurations without risking silent data corruption or query failures

**Acceptance Criteria:**
- Given IndexManager is configured with 10+ repositories (50+ indexes)
- When 100 concurrent AI agents execute queries simultaneously
- Then all queries return correct results with no race conditions detected
- And system logs show thread-safe access patterns
- And performance degradation is <1% compared to single-threaded baseline

**Priority:** Critical (P0)

**Business Value:** Enables enterprise deployments, reduces support escalations, increases customer trust

---

### Story 2: Dynamic Repository Management

**As a** System Administrator managing Agent OS configuration  
**I want to** add or remove repository indexes without restarting the server  
**So that** I can respond quickly to changing project needs without downtime

**Acceptance Criteria:**
- Given Agent OS is running with active query traffic
- When I add a new repository to config and issue reload command
- Then new index is built and immediately available for queries
- And in-flight queries to existing indexes complete successfully
- And no queries see partial or inconsistent index state

**Priority:** High (P1)

**Business Value:** Reduces operational friction, eliminates restart downtime, improves developer experience

---

### Story 3: Maintainable Threading Model

**As a** Future Developer modifying IndexManager code  
**I want to** understand the threading model and lock usage patterns clearly  
**So that** I don't accidentally introduce race conditions or break thread safety

**Acceptance Criteria:**
- Given I'm reviewing IndexManager code for the first time
- When I read the class docstring and method documentation
- Then I understand which methods access shared state
- And I know when to acquire locks for new methods
- And I have examples of correct lock acquisition patterns
- And I can find tests that validate thread safety

**Priority:** High (P1)

**Business Value:** Reduces maintenance costs, prevents regression bugs, enables safe code evolution

---

### Story 4: Standards-Compliant Codebase

**As a** Code Reviewer validating pull requests  
**I want to** verify that IndexManager complies with all project concurrency standards  
**So that** I can approve changes confidently knowing they meet quality requirements

**Acceptance Criteria:**
- Given I'm reviewing a PR that modifies IndexManager
- When I check against concurrency standards checklist
- Then all shared state access is protected by locks
- And threading model is documented
- And concurrent access tests pass
- And standards references are clear in code comments

**Priority:** Critical (P0)

**Business Value:** Enforces code quality, reduces technical debt, aligns with project standards

---

### Story 5: Multi-Agent Query Support

**As an** AI Agent executing code intelligence queries  
**I want to** query indexes concurrently with other agents without errors  
**So that** multiple agents can work on the same codebase simultaneously

**Acceptance Criteria:**
- Given multiple AI agents are connected via streamablehttp transport
- When agents execute queries to different indexes simultaneously
- Then each agent receives correct results for their queries
- And no agent experiences query failures due to race conditions
- And query latency remains consistent under concurrent load

**Priority:** High (P1)

**Business Value:** Enables multi-agent workflows, supports advanced use cases, improves scalability

---

### Story 6: Graceful Configuration Changes

**As a** System Administrator  
**I want to** reload index configuration atomically  
**So that** queries never see partially-updated or corrupted index state

**Acceptance Criteria:**
- Given ongoing query traffic during config reload
- When I trigger index reload operation
- Then each query sees either old index OR new index (never partial state)
- And old index remains available until new index is ready
- And cleanup of old index happens after queries complete

**Priority:** High (P1)

**Business Value:** Ensures data consistency, prevents query failures, enables safe operations

---

## 3.1 Story Priority Summary

**Critical (Must-Have - P0):**
- Story 1: Confident Multi-Repo Deployment
- Story 4: Standards-Compliant Codebase

**High Priority (P1):**
- Story 2: Dynamic Repository Management
- Story 3: Maintainable Threading Model
- Story 5: Multi-Agent Query Support
- Story 6: Graceful Configuration Changes

**Rationale:** P0 stories address immediate standards violations and deployment risks. P1 stories enable future capabilities and operational improvements.

---

## 3.2 User Personas

**Primary Personas:**
1. **DevOps Engineer** - Deploys and manages Agent OS installations for customers
2. **System Administrator** - Configures and operates running Agent OS instances
3. **AI Agent** - Executes code intelligence queries programmatically
4. **Future Developer** - Maintains and extends IndexManager codebase

**Secondary Personas:**
5. **Code Reviewer** - Validates PR quality against standards
6. **QA Engineer** - Tests concurrent access scenarios

---

## 3.3 Supporting Documentation

User needs from supporting documents:
- **Design Document**: "Future maintainers unaware of threading assumptions" → Story 3 (maintainability)
- **Open Questions Analysis**: "Hot config reload: add repo → reload → index created" → Story 2, 6 (dynamic management)
- **Threading Analysis**: "Multi-repo scaling (10+ repos, 50+ indexes) introduces uncertainty" → Story 1 (confident deployment)
- **RLock Analysis**: "Prevent deadlocks in re-entrant call chains" → Story 4 (standards compliance)

See `supporting-docs/INDEX.md` for complete analysis and `supporting-docs/INSIGHTS.md` for requirement traceability.

---

## 4. Functional Requirements

Functional requirements specify concrete capabilities the system must provide to satisfy user stories and business goals.

---

### FR-001: Thread-Safe Dictionary Access

**Description:** The system shall protect all access to the `_indexes` dictionary with the same `RLock` mechanism to prevent race conditions across 4 concurrent execution contexts (asyncio event loop, thread pool, watchdog observer, timer threads).

**Priority:** Critical (P0)

**Related User Stories:** Story 1 (Multi-Repo Deployment), Story 4 (Standards Compliance)

**Acceptance Criteria:**
- All 12 identified access sites to `_indexes` dict use `_indexes_lock`
- Lock acquisition uses `with self._indexes_lock:` pattern consistently
- No access to `_indexes` occurs outside lock protection
- Code review checklist confirms 100% lock coverage
- Grep audit shows zero unprotected access patterns

**Verification Method:** Code inspection + concurrent access tests

---

### FR-002: Re-entrant Lock Implementation

**Description:** The system shall use `threading.RLock` (not `threading.Lock`) for `_indexes` protection to support 3 identified re-entrant call chains where methods call each other while needing lock protection.

**Priority:** Critical (P0)

**Related User Stories:** Story 4 (Standards Compliance), Story 3 (Maintainable Threading)

**Acceptance Criteria:**
- `_indexes_lock` declared as `threading.RLock()` 
- Re-entrant call chain 1 (`route_action` → `_get_required_indexes_for_action`) executes without deadlock
- Re-entrant call chain 2 (`route_action` → `_calculate_index_status` → `_get_required_indexes_for_action`) executes without deadlock
- Re-entrant call chain 3 (`route_action` → `_get_required_indexes_for_action` → `_calculate_index_status`) executes without deadlock
- Deadlock detection test with 100 concurrent threads passes

**Verification Method:** Re-entrancy unit tests + deadlock stress test

---

### FR-003: Concurrent Query Support

**Description:** The system shall support at least 100 concurrent AI agents executing index queries simultaneously without race conditions, data corruption, or measurable performance degradation.

**Priority:** Critical (P0)

**Related User Stories:** Story 1 (Multi-Repo Deployment), Story 5 (Multi-Agent Support)

**Acceptance Criteria:**
- Concurrent access test with 100 threads × 1000 operations (100k total) completes successfully
- All queries return correct results (verified against sequential baseline)
- No race condition errors logged
- No exceptions raised during concurrent access
- Performance overhead <1% compared to single-threaded baseline
- Test validates 10+ index configurations (multi-repo scenario)

**Verification Method:** Concurrent stress test (`test_concurrent_index_access()`)

---

### FR-004: Hot Reload - Add Index

**Description:** The system shall provide an `add_index(index_name, index)` method that adds a new index to `_indexes` dictionary at runtime under lock protection, making it immediately available for queries.

**Priority:** High (P1)

**Related User Stories:** Story 2 (Dynamic Repository Management), Story 6 (Graceful Config Changes)

**Acceptance Criteria:**
- Method signature: `add_index(self, index_name: str, index: BaseIndex) -> None`
- Acquires `_indexes_lock` before modifying `_indexes` dict
- New index immediately available to `route_action()` queries
- Concurrent queries to existing indexes continue successfully during add operation
- Raises `ValueError` if index_name already exists
- Logs structured event: `index_added` with `index_name` metadata

**Verification Method:** Unit test + concurrent query test during add

---

### FR-005: Hot Reload - Remove Index

**Description:** The system shall provide a `remove_index(index_name)` method that removes an index from `_indexes` dictionary at runtime, with cleanup operations performed outside the lock to avoid blocking queries.

**Priority:** High (P1)

**Related User Stories:** Story 2 (Dynamic Repository Management), Story 6 (Graceful Config Changes)

**Acceptance Criteria:**
- Method signature: `remove_index(self, index_name: str) -> None`
- Acquires `_indexes_lock` only for dict removal (not cleanup)
- Calls `index.close()` outside lock to prevent blocking
- In-flight queries to other indexes continue successfully
- Raises `KeyError` if index_name not found
- Logs structured event: `index_removed` with `index_name` metadata

**Verification Method:** Unit test + concurrent query test during remove

---

### FR-006: Hot Reload - Reload Indexes

**Description:** The system shall provide a `reload_indexes(new_config)` method that atomically swaps indexes based on new configuration, determining which indexes to add/remove/keep using config diff logic.

**Priority:** High (P1)

**Related User Stories:** Story 2 (Dynamic Repository Management), Story 6 (Graceful Config Changes)

**Acceptance Criteria:**
- Method signature: `reload_indexes(self, new_config: IndexesConfig) -> Dict[str, str]`
- Returns dict with keys: `{"added": [names], "removed": [names], "kept": [names]}`
- Determines diff: `to_add = new_config - current`, `to_remove = current - new_config`
- Calls `add_index()` for each new index
- Calls `remove_index()` for each removed index
- Operations are atomic: queries see either old OR new state, never partial
- Logs structured event: `indexes_reloaded` with diff metadata

**Verification Method:** Integration test with config changes + concurrent queries

---

### FR-007: Standards Compliance Documentation

**Description:** The system shall include comprehensive threading model documentation in IndexManager class docstring explaining 4 concurrent contexts, lock usage patterns, and code examples for maintainers.

**Priority:** Critical (P0)

**Related User Stories:** Story 3 (Maintainable Threading), Story 4 (Standards Compliance)

**Acceptance Criteria:**
- Class docstring documents 4 concurrent execution contexts explicitly
- Lock acquisition pattern shown with code example
- `_indexes` dict identified as shared mutable state
- Reference to 4 concurrency standards included
- Method docstrings indicate which methods acquire locks
- Maintainer guidance included: "When adding methods that access `_indexes`, always use lock"

**Verification Method:** Documentation review against standards checklist

---

### FR-008: Snapshot Pattern for Iteration

**Description:** The system shall use snapshot pattern when iterating over `_indexes` dictionary to minimize lock hold time and prevent blocking concurrent queries.

**Priority:** High (P1)

**Related User Stories:** Story 1 (Multi-Repo Deployment), Story 5 (Multi-Agent Support)

**Acceptance Criteria:**
- `get_all_indexes()` creates shallow copy under lock: `dict(self._indexes)`
- Iteration/processing occurs on snapshot outside lock
- Lock hold time <100ns (dict copy only)
- Concurrent queries not blocked during iteration
- Snapshot pattern documented in method docstring

**Verification Method:** Lock hold time profiling + concurrent query test

---

### FR-009: Structured Logging for Observability

**Description:** The system shall log all index operations (query, add, remove, reload, rebuild) using structured logging with machine-readable metadata for observability without external metrics systems.

**Priority:** Medium (P2)

**Related User Stories:** Story 2 (Dynamic Repository Management)

**Acceptance Criteria:**
- All index operations log events with `extra={}` dict
- Event types: `index_query`, `index_added`, `index_removed`, `indexes_reloaded`, `index_rebuilt`
- Metadata includes: `index_name`, `action`, `latency_ms`, `result_count` (for queries)
- Log level: INFO for operations, DEBUG for timing details
- Follows `structured-logging-observability.md` standard
- No external metrics dependencies (Prometheus, Datadog, etc.)

**Verification Method:** Log output inspection + grep for structured logging patterns

---

### FR-010: Lock Overhead Performance

**Description:** The system shall ensure RLock overhead is negligible (<1% performance regression) compared to unprotected access, validated through benchmarking tests.

**Priority:** High (P1)

**Related User Stories:** Story 1 (Multi-Repo Deployment)

**Acceptance Criteria:**
- Benchmark test: 10,000 index queries with/without locks
- Performance regression <1% (measured latency difference)
- RLock acquisition time <1ns (per RLock analysis)
- Lock hold time <10ns (dict lookup only)
- Test documents that I/O operations (file access, DB queries) dominate latency (1000x+ lock overhead)

**Verification Method:** Performance benchmark test (`test_lock_overhead_negligible()`)

---

## 4.1 Requirements by Category

### Thread Safety (Critical Path)
- FR-001: Thread-Safe Dictionary Access (P0)
- FR-002: Re-entrant Lock Implementation (P0)
- FR-003: Concurrent Query Support (P0)
- FR-007: Standards Compliance Documentation (P0)

### Hot Reload API (Future Capability)
- FR-004: Hot Reload - Add Index (P1)
- FR-005: Hot Reload - Remove Index (P1)
- FR-006: Hot Reload - Reload Indexes (P1)

### Performance & Observability
- FR-008: Snapshot Pattern for Iteration (P1)
- FR-009: Structured Logging for Observability (P2)
- FR-010: Lock Overhead Performance (P1)

---

## 4.2 Traceability Matrix

| Requirement | User Stories | Business Goals | Priority | LOC Estimate |
|-------------|--------------|----------------|----------|--------------|
| FR-001 | 1, 4 | 1, 2 | P0 | ~50 (lock acquisitions) |
| FR-002 | 3, 4 | 1, 4 | P0 | ~5 (RLock declaration) |
| FR-003 | 1, 5 | 2 | P0 | ~100 (test suite) |
| FR-004 | 2, 6 | 3 | P1 | ~30 (method + test) |
| FR-005 | 2, 6 | 3 | P1 | ~30 (method + test) |
| FR-006 | 2, 6 | 3 | P1 | ~40 (method + test) |
| FR-007 | 3, 4 | 1, 4 | P0 | ~50 (documentation) |
| FR-008 | 1, 5 | 2 | P1 | ~15 (snapshot pattern) |
| FR-009 | 2 | 3 | P2 | ~30 (logging statements) |
| FR-010 | 1 | 2 | P1 | ~50 (benchmark test) |

**Total Estimated LOC:** ~400 lines (implementation + tests + docs)

**Critical Path:** FR-001, FR-002, FR-003, FR-007 must be completed before hot reload features.

---

## 4.3 Supporting Documentation

Requirements informed by:
- **Design Document** (§1): 4 standards violations → FR-001, FR-002, FR-007
- **Threading Analysis** (§2): 4 concurrent contexts, 12 access sites → FR-001, FR-003
- **RLock Analysis** (§3): 3 re-entrant call chains → FR-002
- **Open Questions** (§5): Hot reload use case → FR-004, FR-005, FR-006
- **Fractal Patterns** (§4): INDEX_REGISTRY for dynamic logic → FR-006
- **Open Questions** (§2): Observability via structured logging → FR-009

See `supporting-docs/INDEX.md` for complete cross-reference mapping.

---

## 5. Non-Functional Requirements

Non-functional requirements define quality attributes and system constraints that determine HOW WELL the system performs its functions.

---

### 5.1 Performance

**NFR-P1: Lock Overhead Negligibility**

**Requirement:** RLock acquisition and release overhead shall be <1% of total query latency to ensure thread safety does not degrade performance.

**Measurement Criteria:**
- Benchmark 10,000 queries with locks vs. without locks
- Latency difference ≤1% (measured in μs)
- Lock acquisition time: <1ns per RLock analysis
- Lock hold time: <10ns (dict lookup only)
- I/O operations dominate (1000x+ lock overhead)

**Acceptance:** Benchmark test passes with <1% regression

**Rationale:** Thread safety must not compromise query performance for users

---

**NFR-P2: Concurrent Query Throughput**

**Requirement:** System shall support minimum 100 concurrent query threads without throughput degradation or contention issues.

**Measurement Criteria:**
- Throughput test: 100 threads × 1000 queries each = 100k operations
- Completion time: Within 110% of sequential baseline (10% tolerance)
- No lock contention warnings logged
- All queries return correct results
- CPU utilization remains <80%

**Acceptance:** Stress test completes with ≤10% overhead

**Rationale:** Multi-agent deployments require high concurrent query capacity

---

**NFR-P3: Hot Reload Operation Speed**

**Requirement:** Index hot reload operations (add/remove/reload) shall complete in <100ms to minimize disruption to query traffic.

**Measurement Criteria:**
- `add_index()`: <50ms to acquire lock + insert
- `remove_index()`: <30ms for lock + dict removal (cleanup async)
- `reload_indexes()`: <100ms for config diff + swap operations
- In-flight queries experience <5ms additional latency during reload
- No query failures during reload

**Acceptance:** Hot reload integration test validates timing and query success

**Rationale:** Configuration changes should be fast and non-disruptive

---

### 5.2 Reliability

**NFR-R1: Zero Race Conditions**

**Requirement:** System shall exhibit zero race conditions under concurrent access from 4 execution contexts over 100k operations.

**Measurement Criteria:**
- ThreadSanitizer (if available) reports zero race warnings
- 100 threads × 1000 operations = 100k concurrent accesses
- Zero exceptions raised
- Zero incorrect query results (verified against sequential baseline)
- Zero corrupted index state

**Acceptance:** Concurrent stress test passes with zero failures over 10 runs

**Rationale:** Data integrity is critical for code intelligence accuracy

---

**NFR-R2: Deadlock Prevention**

**Requirement:** System shall guarantee no deadlocks possible through use of re-entrant RLock and single lock acquisition order.

**Measurement Criteria:**
- All 3 re-entrant call chains execute without deadlock
- Deadlock detection test (100 threads with 10s timeout) passes
- No thread hangs observed in stress tests
- Lock acquisition order documented and enforced
- No nested lock acquisitions across different locks

**Acceptance:** Deadlock test suite passes, code review confirms single RLock

**Rationale:** Deadlocks cause system hangs requiring manual restart

---

**NFR-R3: Atomic State Transitions**

**Requirement:** Hot reload operations shall be atomic: queries see either old state OR new state, never partial/inconsistent state.

**Measurement Criteria:**
- During `reload_indexes()`, concurrent queries complete successfully
- Each query uses one consistent index snapshot (old or new)
- Zero queries see index-not-found during swap
- Zero queries see partially-updated index state
- State transition occurs within single lock acquisition

**Acceptance:** Concurrent reload test validates atomicity

**Rationale:** Partial state causes query errors and incorrect results

---

### 5.3 Maintainability

**NFR-M1: Code Documentation Coverage**

**Requirement:** IndexManager shall have comprehensive threading model documentation enabling future maintainers to modify code safely without introducing race conditions.

**Measurement Criteria:**
- Class docstring: Documents 4 concurrent contexts, lock usage, shared state
- Method docstrings: Indicate which methods acquire locks
- Code examples: Lock acquisition pattern shown
- Standards references: Links to 4 concurrency standards
- Maintainer guidance: "Always use lock when accessing `_indexes`"
- Documentation review: Human validation confirms clarity

**Acceptance:** Documentation review checklist 100% complete

**Rationale:** Undocumented threading assumptions cause future bugs

---

**NFR-M2: Test Suite Completeness**

**Requirement:** Thread safety implementation shall have comprehensive test coverage (unit, integration, stress) validating all concurrency scenarios.

**Measurement Criteria:**
- Test suite includes:
  - `test_concurrent_index_access()`: 100k operations
  - `test_lock_overhead_negligible()`: Performance benchmark
  - `test_thread_safety_stress()`: Concurrent reads + writes
  - `test_hot_reload_atomic_swap()`: Hot reload atomicity
  - `test_re_entrant_call_chains()`: Deadlock prevention
- All tests pass in CI/CD pipeline
- Test coverage for IndexManager: ≥85%
- Tests run on every PR

**Acceptance:** Test suite exists and passes

**Rationale:** Tests prevent regression and validate correctness

---

**NFR-M3: Dynamic Logic Extensibility**

**Requirement:** Hot reload implementation shall use INDEX_REGISTRY for dynamic index creation, ensuring new index types require zero IndexManager code changes.

**Measurement Criteria:**
- `reload_indexes()` iterates over INDEX_REGISTRY (not hardcoded types)
- Adding new index type: Update registry only, no route_action changes
- Config-driven: Index types specified in config, not code
- Maintainability: New repo = config change, not code deployment
- Follows project fractal pattern architecture

**Acceptance:** Code review confirms INDEX_REGISTRY usage, zero hardcoded types

**Rationale:** Static patterns create maintenance burden, dynamic logic scales

---

### 5.4 Compatibility

**NFR-C1: Architectural Consistency**

**Requirement:** IndexManager threading patterns shall match WorkflowEngine (proven in production) using identical RLock-for-dict-orchestration pattern.

**Measurement Criteria:**
- `IndexManager._indexes_lock` is `threading.RLock` (matches `WorkflowEngine._dynamic_lock`)
- Both protect dict-of-orchestrated-objects pattern
- Lock acquisition patterns match (with statement, snapshot for iteration)
- Both follow project's fractal orchestration architecture
- Code review validates pattern consistency

**Acceptance:** Human review confirms architectural alignment

**Rationale:** Consistent patterns reduce cognitive load and leverage proven designs

---

**NFR-C2: Python 3.13 Compatibility**

**Requirement:** Thread safety implementation shall not rely on Python GIL, ensuring compatibility with Python 3.13+ free-threaded mode.

**Measurement Criteria:**
- Explicit locks protect all shared state (no GIL assumptions)
- Threading model documents zero GIL dependencies
- Code comments identify previously-accidental safety via GIL
- Tests should pass with `PYTHON_GIL=0` (when Python 3.13 available)
- Future-proof: No code changes needed for GIL removal

**Acceptance:** Documentation confirms GIL independence, no "TODO: add locks when GIL removed" comments

**Rationale:** Python 3.13 optional free-threading requires explicit synchronization

---

### 5.5 Observability

**NFR-O1: Structured Logging for Operations**

**Requirement:** System shall log all index operations using structured logging (machine-readable, queryable) without requiring external metrics systems.

**Measurement Criteria:**
- All operations logged with `extra={}` dict containing metadata
- Event types covered: `index_query`, `index_added`, `index_removed`, `indexes_reloaded`, `index_rebuilt`
- Metadata includes: `index_name`, `action`, `latency_ms`, `result_count` (queries)
- Log aggregation possible via grep/jq for performance analysis
- No Prometheus/Datadog/external system dependencies
- Follows `structured-logging-observability.md` standard

**Acceptance:** Log output inspection confirms structured format, grep queries work

**Rationale:** Per-project MCP server has no external metrics; logs enable observability

---

**NFR-O2: Query Latency Visibility**

**Requirement:** System shall log query latency (p50, p95, p99) via structured logs to enable performance analysis and bottleneck identification.

**Measurement Criteria:**
- Each query logs latency in milliseconds
- Log format: `{"event": "index_query", "latency_ms": 42.3, "index_name": "code", ...}`
- Latency buckets analyzable via log aggregation
- No performance impact from logging (<0.1ms overhead)
- Operators can identify slow queries via log analysis

**Acceptance:** Log analysis demonstrates latency percentile calculation

**Rationale:** Visibility enables performance debugging and optimization

---

### 5.6 Security

**NFR-S1: No External Dependencies for Thread Safety**

**Requirement:** Thread safety implementation shall use only Python standard library (`threading` module), avoiding external synchronization libraries to minimize supply chain risk.

**Measurement Criteria:**
- `import threading` only (no third-party locks)
- No new dependencies added to `requirements.txt` for concurrency
- Standard library RLock proven reliable and maintained
- Reduced supply chain attack surface

**Acceptance:** Dependency audit confirms zero new packages

**Rationale:** Minimizing dependencies reduces security risk and maintenance burden

---

## 5.7 NFR Summary by Category

| Category | NFR Count | Priority | Validation Method |
|----------|-----------|----------|-------------------|
| Performance | 3 | P0, P1 | Benchmarks, stress tests |
| Reliability | 3 | P0 | Concurrent tests, deadlock detection |
| Maintainability | 3 | P0, P1 | Documentation review, code review, test coverage |
| Compatibility | 2 | P1 | Code review, architectural validation |
| Observability | 2 | P2 | Log inspection, analysis scripts |
| Security | 1 | P0 | Dependency audit |

**Total NFRs:** 14

**Critical Path:** NFR-R1 (Zero Race Conditions), NFR-R2 (Deadlock Prevention), NFR-M1 (Documentation), NFR-M2 (Test Suite)

---

## 5.8 Supporting Documentation

NFRs informed by:
- **RLock Analysis** (§4): RLock 0.9ns vs Lock 0.7ns (negligible) → NFR-P1
- **Design Document** (§7): 3 test suites required → NFR-M2
- **Open Questions** (§2): Structured logging for observability → NFR-O1, NFR-O2
- **Design Document** (§8): No deadlocks with RLock → NFR-R2
- **Open Questions** (§5): INDEX_REGISTRY for dynamic logic → NFR-M3
- **Design Document** (§10): WorkflowEngine pattern consistency → NFR-C1
- **Open Questions** (§4): Python 3.13 GIL removal → NFR-C2
- **Design Document** (§6.4): Atomic swap under lock → NFR-R3

See `supporting-docs/INDEX.md` for complete NFR traceability.

---

## 6. Out of Scope

Explicitly defines what is NOT included in this implementation. Clear boundaries prevent scope creep, manage expectations, and focus effort on critical requirements.

### Explicitly Excluded

---

#### 6.1 Features Not Included

**1. Read-Write Lock (RWLock) Optimization**
- **Reason:** Current read-heavy workload shows zero lock contention. RLock sufficient.
- **Evidence:** Lock hold time <10ns, I/O dominates latency (1000x+)
- **Future Consideration:** Only if profiling shows lock contention under multi-repo load
- **Decision Point:** Implement thread safety with RLock first, measure, then optimize if needed

**2. Index Lifecycle State Machine**
- **Reason:** Current implicit states (building/ready/stale) work correctly
- **Scope:** Formal state machine (with transitions, guards, events) is overkill for current needs
- **Future Consideration:** If hot reload complexity increases, consider formal states
- **Alternative:** Document implicit states in implementation.md

**3. External Metrics Integration**
- **Reason:** Per-project MCP server has no Prometheus/Datadog/external metrics in typical deployments
- **Approach:** Use structured logging for observability instead (NFR-O1, NFR-O2)
- **Out of Scope:** Prometheus exporters, StatsD clients, APM integration
- **Rationale:** Adds dependencies, complexity for minimal benefit in local deployments

**4. FileWatcher Refactoring**
- **Reason:** Separate concern from IndexManager thread safety
- **Scope:** This spec focuses on IndexManager, not FileWatcher internals
- **Note:** FileWatcher uses threading (Observer, Timer), but its thread safety is separate issue
- **Future Work:** FileWatcher may need its own thread safety analysis

**5. Graceful Shutdown Coordination**
- **Reason:** Server shutdown logic is broader than IndexManager scope
- **Current:** Background tasks lack graceful shutdown (separate technical debt)
- **Out of Scope:** Task cancellation, cleanup coordination, shutdown hooks
- **Future Work:** Server-wide shutdown protocol (not IndexManager-specific)

**6. Async-Only Refactoring**
- **Reason:** Current hybrid threading + asyncio model works; full async rewrite is unnecessary
- **Risk:** High complexity, low benefit, potential bugs
- **Decision:** Keep hybrid model, add explicit synchronization
- **Not a Goal:** Eliminating threading entirely

**7. Performance Optimization Beyond Thread Safety**
- **Reason:** No performance problems identified; optimization is premature
- **Current:** Query latency acceptable, no customer complaints
- **Out of Scope:** Query caching, index warming, lazy loading optimizations
- **Approach:** Thread safety must not degrade performance (NFR-P1), but optimizations beyond that are excluded

**8. Multi-Master Index Synchronization**
- **Reason:** Single-server deployment model, no distributed index use case
- **Out of Scope:** Index replication, cross-server synchronization, consensus protocols
- **Architecture:** Per-project MCP server = single IndexManager instance
- **Not Needed:** Distributed locking, conflict resolution

---

#### 6.2 User Types Not Supported

**1. Remote Index Query APIs**
- **Reason:** MCP protocol is the only supported interface
- **Out of Scope:** REST API, GraphQL, gRPC for index queries
- **Current:** AI agents use MCP tools only

**2. Direct Index Manipulation by Users**
- **Reason:** Indexes managed internally, not exposed to users
- **Out of Scope:** User-facing index add/remove/rebuild commands
- **Access:** Hot reload via config file only, not user-initiated API calls

---

#### 6.3 Platforms Not Supported

**1. Windows Threading Model Differences**
- **Reason:** Python threading abstraction handles OS differences
- **Testing:** Tests run on Linux/macOS; Windows compatibility assumed via Python stdlib
- **Out of Scope:** Windows-specific threading tests, platform-specific locks

**2. Python 3.13 Free-Threaded Mode Testing**
- **Reason:** Python 3.13 not released/stable yet
- **Future:** Design is GIL-independent (NFR-C2), should work with free-threading
- **Out of Scope:** Actual testing on Python 3.13 with `PYTHON_GIL=0`
- **Action:** Document as future validation when 3.13 stable

---

#### 6.4 Integrations Not Included

**1. External Lock Managers**
- **Reason:** Python stdlib `threading.RLock` is sufficient and proven
- **Out of Scope:** Redis locks, ZooKeeper, etcd, distributed locks
- **Rationale:** Adds dependencies, network calls, failure modes

**2. APM / Observability Platforms**
- **Reason:** Local MCP server, no external observability services
- **Out of Scope:** Datadog APM, New Relic, Honeycomb, Sentry performance tracing
- **Alternative:** Structured logging (NFR-O1, NFR-O2)

**3. Index Storage Backend Changes**
- **Reason:** LanceDB, DuckDB internals not changing
- **Out of Scope:** Switching to different vector DBs, SQL backends
- **Focus:** Thread-safe orchestration layer only

---

#### 6.5 Quality Levels Beyond Defined NFRs

**1. Formal Verification**
- **Reason:** Testing + code review sufficient for project risk level
- **Out of Scope:** TLA+, model checking, formal proofs of correctness
- **Approach:** Empirical validation via stress tests

**2. Zero-Downtime Deployments**
- **Reason:** MCP server restarts are acceptable for deployments
- **Out of Scope:** Blue-green deployments, rolling updates, hot code swapping
- **Note:** Hot reload enables zero-downtime config changes (different from code deployment)

**3. Sub-Millisecond Latency Guarantees**
- **Reason:** Code intelligence queries are I/O-bound (file access, DB queries)
- **Out of Scope:** Real-time latency guarantees, latency SLAs
- **Acceptable:** p95 latency <200ms (NFR-P1)

---

## 6.6 Future Enhancements (Potential Post-MVP)

**Potential Phase 2 (If Evidence Supports):**
- **RWLock Optimization** - Only if lock contention measured in multi-repo deployments
- **Index Lifecycle State Machine** - If hot reload becomes more complex
- **FileWatcher Thread Safety** - If FileWatcher issues identified separately
- **Python 3.13 Validation** - When Python 3.13 is stable and widely adopted

**Potential Phase 3 (Lower Priority):**
- **Graceful Shutdown Protocol** - Server-wide concern, not IndexManager-specific
- **Query Result Caching** - Performance optimization (only if needed)
- **Index Warming Strategies** - Reduce cold-start latency (only if problem identified)

**Explicitly Not Planned (No Current Use Case):**
- **Multi-Master Index Replication** - Single-server architecture
- **External Lock Managers** - Python stdlib sufficient
- **Formal Verification** - Testing adequate for risk level
- **Async-Only Refactoring** - Current model works

---

## 6.7 Boundary Clarifications

**Q: Why not use RWLock from the start?**  
A: Evidence shows zero lock contention. RLock overhead negligible (<1ns). Optimize only if measurement proves necessary (YAGNI principle).

**Q: Why not formal state machine for indexes?**  
A: Current implicit states work. Formal state machine adds complexity without clear benefit. Document states in implementation.md instead.

**Q: Why not external metrics?**  
A: Per-project MCP server = no external observability in typical deployments. Structured logging provides queryable data without dependencies.

**Q: Why not graceful shutdown?**  
A: Separate concern. Server-wide shutdown coordination needed, not IndexManager-specific. Defer to server lifecycle design.

**Q: Why not test on Python 3.13 now?**  
A: Python 3.13 not stable yet. Design is GIL-independent (NFR-C2), testing deferred to 3.13 stable release.

---

## 6.8 Supporting Documentation

Out-of-scope items clarified by:
- **Design Document** (§2): Non-goals explicitly listed (async-only refactoring, performance optimization, external libraries)
- **Open Questions** (§3): RWLock evaluation only if contention observed
- **Open Questions** (§2): Structured logging, not external metrics
- **Design Document** (§8): FileWatcher is separate concern
- **Open Questions** (§5): Hot reload focus on config changes, not full deployment automation

See `supporting-docs/INDEX.md` for complete context.

---

## 6.9 Out-of-Scope Summary

| Category | Count | Rationale |
|----------|-------|-----------|
| Features | 8 | YAGNI, separate concerns, premature optimization |
| User Types | 2 | MCP-only interface, internal index management |
| Platforms | 2 | Python stdlib abstracts OS, Python 3.13 not stable |
| Integrations | 3 | Local deployment, avoid external dependencies |
| Quality Levels | 3 | Testing adequate, acceptable latency, restart tolerable |

**Total Out-of-Scope Items:** 18 explicitly documented

**Key Principle:** Focus on critical P0/P1 requirements, defer optimizations until evidence supports need.

---

## Phase 1 Complete: Requirements Document Summary

**Sections Completed:**
- ✅ Business Goals: 4 goals with metrics
- ✅ User Stories: 6 stories covering 4 personas
- ✅ Functional Requirements: 10 FRs (FR-001 to FR-010)
- ✅ Non-Functional Requirements: 14 NFRs across 6 categories
- ✅ Out of Scope: 18 items with rationale

**Total Requirements:** 24 FRs + 14 NFRs = **38 requirements**

**Traceability:** All requirements mapped to user stories, business goals, and supporting documents

**Estimated Implementation:** ~400 LOC (implementation + tests + docs)

**Critical Path:** FR-001, FR-002, FR-003, FR-007 (thread safety core) → FR-004, FR-005, FR-006 (hot reload)

---

## Next: Technical Design (Phase 2)

Continue to Phase 2 to create specs.md with detailed architecture, component design, APIs, and implementation approach.

