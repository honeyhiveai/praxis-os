# Software Requirements Document

**Project:** Cascading Health Check Architecture  
**Date:** 2025-11-10  
**Priority:** High  
**Category:** Enhancement (Architectural Refactoring)

---

## 1. Introduction

### 1.1 Purpose
This document defines the requirements for implementing a fractal component registry pattern across the RAG subsystem to enable granular health checks, targeted rebuilds, and partial degradation.

### 1.2 Scope
This feature will replace static if/else health check logic with a dynamic component registry pattern that works identically at all levels of the RAG hierarchy (GraphIndex, CodeIndex, StandardsIndex, IndexManager).

---

## 2. Business Goals

### Goal 1: Zero-Maintenance Component Addition

**Objective:** Enable adding new RAG components without modifying orchestration logic in parent indexes

**Success Metrics:**
- Lines of code changed in IndexManager when adding component: **5+ changes** → **0 changes**
- Lines of code changed in CodeIndex when adding component: **3+ changes** → **0 changes**
- Developer time to add new component: **30-60 minutes** → **10-15 minutes**
- Risk of introducing bugs when adding components: **High (touching core logic)** → **Low (isolated to component)**

**Business Impact:**
- Reduces development time for RAG feature expansion by 50-75%
- Eliminates risk of breaking existing functionality when adding new capabilities
- Enables junior developers to contribute new components without understanding full system
- Accelerates innovation (faster iteration on RAG capabilities)

### Goal 2: Targeted Rebuild Performance

**Objective:** Rebuild only broken components instead of entire indexes, dramatically reducing rebuild times

**Success Metrics:**
- Rebuild time for single broken component: **30s (full rebuild)** → **2s (targeted)**
- Speedup factor: **1x** → **15x**
- Downtime during rebuild: **30s** → **2s**
- Data preservation: **0% (full rebuild destroys all)** → **90% (only broken component cleared)**

**Business Impact:**
- Reduces system recovery time by 93% (30s → 2s)
- Improves developer experience (faster iteration during debugging)
- Preserves expensive computations (embeddings, graph relationships)
- Enables hot-fix deployment (targeted rebuild for production issues)

### Goal 3: Partial Degradation Resilience

**Objective:** Allow operational components to continue serving requests when other components fail

**Success Metrics:**
- System availability when single component fails: **0% (all operations blocked)** → **50-90% (only dependent operations fail)**
- `find_callers()` success rate when AST broken: **0%** → **100%**
- `search_ast()` success rate when AST broken: **0%** → **0% (expected)**
- User-facing error rate: **100% (all queries fail)** → **10-50% (only queries using broken component)**

**Business Impact:**
- Improves system resilience (graceful degradation vs complete failure)
- Reduces user-facing errors by 50-90%
- Enables "best effort" service delivery (serve what we can, fail what we can't)
- Provides time window to fix issues without full outage

### Goal 4: Diagnostic Precision

**Objective:** Replace coarse boolean health status with granular component-level diagnostics

**Success Metrics:**
- Health check granularity: **1 status per index** → **5+ statuses per index**
- Time to identify root cause: **10-30 minutes (grep logs)** → **10 seconds (read health output)**
- False positive rebuild triggers: **High (any component broken → rebuild all)** → **Zero (only broken component triggers)**
- Diagnostic information density: **1 boolean** → **Component tree with counts/errors**

**Business Impact:**
- Reduces mean time to repair (MTTR) by 95% (30min → 30sec)
- Eliminates unnecessary rebuilds (saves compute resources + time)
- Enables proactive monitoring (detect component degradation before failure)
- Improves on-call experience (clear error messages vs investigation)

### Goal 5: Self-Maintaining Architecture

**Objective:** Establish architectural pattern that scales with complexity without increasing maintenance burden

**Success Metrics:**
- Maintenance burden growth: **O(N²) (each component affects all)** → **O(1) (components isolated)**
- Test coverage for new component: **Requires updating 5+ test suites** → **Single component test suite**
- Documentation updates per new component: **5+ locations** → **1 location (component registry)**
- Code comprehension barrier: **Must understand full RAG hierarchy** → **Must understand component abstraction only**

**Business Impact:**
- Enables sustainable growth (adding components doesn't slow development)
- Reduces onboarding time for new developers (simpler mental model)
- Lowers technical debt accumulation (pattern enforces clean architecture)
- Future-proofs RAG subsystem (prepared for 2x, 10x component growth)

## 2.1 Supporting Documentation

The business goals above are directly informed by:
- **2025-11-08-cascading-health-check-architecture.md**: Design document with success metrics, current problems, and architectural approach

See `supporting-docs/INDEX.md` for complete analysis and extracted insights.

---

## 3. User Stories

User stories describe the feature from the user's perspective.

### Story Format

**As a** {user type}  
**I want to** {capability}  
**So that** {benefit}

---

### Story 1: Add RAG Component Without Breaking System

**As a** RAG subsystem developer  
**I want to** add a new component (e.g., imports graph) to GraphIndex without modifying IndexManager or CodeIndex  
**So that** I can expand RAG capabilities without risking regressions in existing functionality

**Acceptance Criteria:**
- Given a new component implementation with health_check() and rebuild() methods
- When I register the component in the local index's component registry
- Then the component is automatically discovered by health checks
- And the component's capabilities are automatically exposed to users
- And no changes are required in parent indexes or IndexManager

**Priority:** Critical (Must-Have)

---

### Story 2: Rebuild Only Broken Component

**As a** developer debugging RAG issues  
**I want to** rebuild only the broken AST component without touching the operational graph component  
**So that** I can fix issues quickly without losing expensive computations (embeddings, relationships)

**Acceptance Criteria:**
- Given GraphIndex with AST component broken (0 nodes) and graph component operational (500 symbols)
- When I trigger a rebuild
- Then only AST component is rebuilt (2s)
- And graph component data is preserved (500 symbols remain)
- And total rebuild time is under 3s (vs 30s for full rebuild)

**Priority:** Critical (Must-Have)

---

### Story 3: Continue Operations During Partial Failure

**As a** user of RAG search capabilities  
**I want to** use `find_callers()` even when AST indexing is broken  
**So that** I can continue my work without waiting for full system recovery

**Acceptance Criteria:**
- Given GraphIndex with AST component unhealthy (0 nodes) and graph component healthy (500 symbols, 1200 edges)
- When I call `find_callers("my_function")`
- Then the query succeeds and returns valid results
- And I receive results in expected time (<1s)
- When I call `search_ast("pattern")`
- Then the query fails with clear error message indicating AST is unavailable

**Priority:** High

---

### Story 4: Identify Root Cause Quickly

**As an** on-call engineer responding to RAG alerts  
**I want to** see granular component-level health status with specific error messages  
**So that** I can identify and fix the root cause without extensive log analysis

**Acceptance Criteria:**
- Given a health check response from CodeIndex
- When I examine the health status
- Then I see status for each component (semantic, graph.ast, graph.traversal)
- And each component shows specific metrics (count, data_present, query_works, error message)
- And the output clearly indicates which capabilities are available vs unavailable
- And I can identify the root cause within 10 seconds

**Priority:** High

---

### Story 5: Query System Capabilities Dynamically

**As a** RAG API consumer  
**I want to** query which operations are currently available before attempting them  
**So that** I can provide better UX (disable unavailable features) and avoid unnecessary errors

**Acceptance Criteria:**
- Given CodeIndex health check response
- When I examine the "capabilities" field
- Then I see a map of all operations to their availability status
- And each capability shows true/false based on component health
- And I can use this to conditionally enable/disable UI features

**Priority:** Medium

---

## 3.1 Story Priority Summary

**Critical (Must-Have):**
- Story 1: Add RAG Component Without Breaking System
- Story 2: Rebuild Only Broken Component

**High Priority:**
- Story 3: Continue Operations During Partial Failure
- Story 4: Identify Root Cause Quickly

**Medium Priority:**
- Story 5: Query System Capabilities Dynamically

---

## 3.2 Supporting Documentation

User needs from supporting documents:
- **2025-11-08-cascading-health-check-architecture.md**: Problems with current system (false positive rebuilds, no partial degradation, poor diagnostics) directly inform user stories

See `supporting-docs/INDEX.md` for detailed requirements insights.

---

## 4. Functional Requirements

Functional requirements specify capabilities the system must provide.

---

### FR-001: Component Registration

**Description:** The system shall provide a ComponentDescriptor class for declarative component registration at any level of the RAG hierarchy.

**Priority:** Critical

**Related User Stories:** Story 1, Story 2

**Acceptance Criteria:**
- Component Descriptor accepts: name, provides, capabilities, health_check, rebuild, dependencies
- All parameters except dependencies are required
- Component registration uses dictionary with component names as keys
- Registration works identically at GraphIndex, CodeIndex, StandardsIndex, and IndexManager levels
- Invalid component descriptor (missing required params) raises ValidationError at registration time

---

### FR-002: Dynamic Health Check Discovery

**Description:** The system shall dynamically discover and call health_check() on all registered components without hardcoded logic.

**Priority:** Critical

**Related User Stories:** Story 1, Story 4

**Acceptance Criteria:**
- dynamic_health_check() helper function accepts Dict[str, ComponentDescriptor]
- Function iterates over all components and calls their health_check() method
- No if/else chains or component-specific logic in dynamic_health_check()
- Works with 1, 5, or 50+ components without code changes
- Returns aggregated HealthStatus with component details

---

### FR-003: Component-Level Health Reporting

**Description:** The system shall report health status for each component independently with specific metrics and error messages.

**Priority:** Critical

**Related User Stories:** Story 4

**Acceptance Criteria:**
- Health check returns status for EACH component (not single boolean)
- Each component status includes: healthy (bool), message (str), details (dict)
- Details include: data_present, query_works, count, error (if any)
- Output format allows drilling down from IndexManager → CodeIndex → GraphIndex → component
- Health check response includes "components" dict with all component statuses

---

### FR-004: Targeted Component Rebuild

**Description:** The system shall rebuild only broken components while preserving healthy component data.

**Priority:** Critical

**Related User Stories:** Story 2

**Acceptance Criteria:**
- IndexManager._find_rebuild_actions() identifies specific broken components (not entire indexes)
- Rebuild actions specify component path (e.g., "code.graph.ast")
- Each component descriptor includes rebuild() callable
- Rebuild only calls rebuild() on unhealthy components
- Healthy component data is preserved (not cleared/rebuilt)
- Rebuild time for single component is <3s (vs 30s for full rebuild)

---

### FR-005: Capability Discovery and Mapping

**Description:** The system shall dynamically map capabilities to components and report which operations are currently available.

**Priority:** High

**Related User Stories:** Story 5

**Acceptance Criteria:**
- Each component declares capabilities list (e.g., ["find_callers", "find_dependencies"])
- Health check response includes "capabilities" dict mapping operations to availability (bool)
- Capability is true if providing component is healthy, false if unhealthy
- Capabilities are aggregated from sub-components automatically
- No hardcoded capability mapping logic required

---

### FR-006: Partial Degradation Support

**Description:** The system shall allow operational components to handle requests even when other components are unhealthy.

**Priority:** High

**Related User Stories:** Story 3

**Acceptance Criteria:**
- Independent components do not block each other (AST broken ≠ graph blocked)
- Operations check capability availability before execution
- Healthy component operations succeed with expected performance
- Unhealthy component operations fail with clear error messages
- System reports partial degradation (e.g., "3/5 capabilities available")

---

### FR-007: Backward Compatibility

**Description:** The system shall support indexes without component pattern (legacy indexes) without requiring immediate migration.

**Priority:** High

**Related User Stories:** N/A (infrastructure)

**Acceptance Criteria:**
- hasattr() check detects if index has .components attribute
- Legacy indexes use fallback capability discovery
- Legacy indexes continue working with existing health_check() implementation
- Mixed environment supported (some indexes migrated, others not)
- No breaking changes to existing BaseIndex interface

---

### FR-008: Component Dependency Tracking

**Description:** The system shall track component dependencies declared in component descriptors.

**Priority:** Medium

**Related User Stories:** N/A (future enhancement)

**Acceptance Criteria:**
- ComponentDescriptor accepts dependencies list (component names)
- Dependencies are validated at registration (referenced components must exist)
- Health check considers dependencies (component depends on unhealthy dependency → unhealthy)
- Rebuild respects dependencies (rebuild dependencies first)
- Circular dependencies detected and rejected at registration time

---

### FR-009: Fractal Pattern Uniformity

**Description:** The system shall use identical component pattern at all hierarchy levels (GraphIndex, CodeIndex, StandardsIndex, IndexManager).

**Priority:** High

**Related User Stories:** Story 1

**Acceptance Criteria:**
- ComponentDescriptor class used at all 4 levels
- dynamic_health_check() helper used at all 4 levels
- Registration syntax identical across levels
- Health check response structure consistent (HealthStatus with components dict)
- Adding component requires only local changes (no propagation to parent levels)

---

### FR-010: Component Health Check Data Contract

**Description:** The system shall define standard data contract for component health check responses.

**Priority:** High

**Related User Stories:** Story 4

**Acceptance Criteria:**
- Component health_check() returns Dict[str, Any] (not boolean)
- Required keys: data_present (bool), query_works (bool), count (int), error (Optional[str])
- Additional component-specific keys allowed
- Empty component (count=0) does not automatically mean unhealthy
- Exception during health check returns error dict (not raised)

---

## 4.1 Requirements by Category

### Core Component Pattern
- FR-001: Component Registration
- FR-002: Dynamic Health Check Discovery
- FR-009: Fractal Pattern Uniformity

### Health Reporting
- FR-003: Component-Level Health Reporting
- FR-010: Component Health Check Data Contract

### Rebuild System
- FR-004: Targeted Component Rebuild
- FR-008: Component Dependency Tracking

### Operational Resilience
- FR-005: Capability Discovery and Mapping
- FR-006: Partial Degradation Support
- FR-007: Backward Compatibility

---

## 4.2 Traceability Matrix

| Requirement | User Stories | Business Goals | Priority |
|-------------|--------------|----------------|----------|
| FR-001 | Story 1, 2 | Goal 1, 5 | Critical |
| FR-002 | Story 1, 4 | Goal 1, 5 | Critical |
| FR-003 | Story 4 | Goal 4 | Critical |
| FR-004 | Story 2 | Goal 2 | Critical |
| FR-005 | Story 5 | Goal 3, 4 | High |
| FR-006 | Story 3 | Goal 3 | High |
| FR-007 | N/A | Goal 5 | High |
| FR-008 | N/A | Goal 5 | Medium |
| FR-009 | Story 1 | Goal 1, 5 | High |
| FR-010 | Story 4 | Goal 4 | High |

---

## 4.3 Supporting Documentation

Requirements informed by:
- **2025-11-08-cascading-health-check-architecture.md**: ComponentDescriptor pattern, dynamic health check architecture, four-level hierarchy design

See `supporting-docs/INSIGHTS.md` for detailed design insights extraction.

---

## 5. Non-Functional Requirements

NFRs define quality attributes and system constraints.

---

### 5.1 Performance

**NFR-P1: Health Check Execution Time**
- Individual component health check: < 50ms
- Full cascade health check (IndexManager → all components): < 500ms
- Health checks are infrequent (startup + manual trigger), so optimization is not critical

**NFR-P2: Targeted Rebuild Time**
- Single component rebuild: < 3s (AST rebuild target: 2s)
- Full index rebuild: < 30s (current baseline)
- Speedup factor for targeted rebuild: minimum 10x

**NFR-P3: Dynamic Discovery Overhead**
- Component registration (startup): < 10ms per index
- Dynamic health check vs static health check: < 2x overhead (acceptable for infrequent operations)
- Zero runtime performance impact on query operations (search_ast, find_callers)

---

### 5.2 Reliability

**NFR-R1: Partial Degradation**
- Independent component failures do not cascade to dependent components
- Healthy component success rate during partial failure: 100%
- System reports operational capability status (e.g., "3/5 capabilities available")

**NFR-R2: Health Check Resilience**
- Component health check exceptions do not crash health check system
- Failed component returns error dict (not raised exception)
- Health check system continues even if individual component check fails

**NFR-R3: Rebuild Safety**
- Targeted rebuild preserves data in healthy components: 100% preservation
- Rebuild failure in one component does not corrupt other components
- Rollback capability if rebuild fails (restore from backup if needed)

---

### 5.3 Maintainability

**NFR-M1: Code Change Isolation**
- Adding new component to GraphIndex: 0 changes in IndexManager
- Adding new component to GraphIndex: 0 changes in CodeIndex
- Adding new component: ~30 lines (component descriptor + health/rebuild methods)

**NFR-M2: Test Coverage**
- Component pattern foundation: minimum 90% coverage
- Each index with component pattern: minimum 80% coverage
- Integration tests for partial degradation: 100% coverage of critical scenarios

**NFR-M3: Code Complexity**
- Cyclomatic complexity of dynamic_health_check(): < 5
- No if/else chains for component-specific logic
- Pattern repeats identically at all levels (fractal uniformity)

**NFR-M4: Documentation**
- Each component must document: provides, capabilities, dependencies
- ComponentDescriptor usage examples for all 4 hierarchy levels
- Migration guide for converting static health checks to component pattern

---

### 5.4 Compatibility

**NFR-C1: Backward Compatibility**
- Indexes without .components attribute continue working: 100% compatibility
- No breaking changes to BaseIndex interface
- Mixed environment supported (some indexes migrated, others not)
- Gradual migration path (phase-by-phase rollout)

**NFR-C2: API Stability**
- HealthStatus response structure remains backward compatible
- New fields added (components, capabilities) but existing fields unchanged
- Existing code reading HealthStatus.healthy continues working

---

### 5.5 Scalability

**NFR-SC1: Component Count Scaling**
- Pattern works with 1 to 50+ components per index
- No performance degradation with component count (O(N) health check iteration)
- Memory overhead per component: < 1KB

**NFR-SC2: Hierarchy Depth Scaling**
- Pattern works at 4+ hierarchy levels without modification
- Recursive drill-down supported (IndexManager → CodeIndex → GraphIndex → components)
- No hardcoded depth limits

---

### 5.6 Usability

**NFR-U1: Diagnostic Clarity**
- Health check output human-readable (not just for machines)
- Error messages specific (include component name, error type, remediation hint)
- Component tree visualization in health output

**NFR-U2: Developer Experience**
- Component registration intuitive (declarative dictionary syntax)
- Error messages actionable (what went wrong, how to fix)
- Pattern learnable in < 30 minutes (single abstraction to understand)

---

### 5.7 Portability

**NFR-PO1: Platform Independence**
- No platform-specific code in component pattern
- Works on Linux, macOS, Windows
- Python 3.9+ compatibility

---

## 5.8 Supporting Documentation

NFRs informed by:
- **2025-11-08-cascading-health-check-architecture.md**: Performance targets (15x speedup, 2s rebuild), maintainability goals (0 changes in parent indexes), reliability requirements (partial degradation)

See `supporting-docs/INSIGHTS.md` for quantitative success metrics.

---

## 6. Out of Scope

Explicitly defines what is NOT included. Items may be considered for future phases.

### Explicitly Excluded

---

#### Features

**Not Included in This Release:**

1. **Automatic Remediation**
   - **Reason:** System identifies broken components but does not automatically fix them. Rebuilds are triggered manually or via external orchestration.
   - **Future Consideration:** Phase 2 could add auto-healing for specific failure modes (e.g., auto-rebuild if AST count = 0)

2. **Real-Time Health Monitoring**
   - **Reason:** Health checks are triggered at server startup or manually. No continuous/scheduled health monitoring.
   - **Future Consideration:** Phase 3 could add scheduled health checks with alerting integration

3. **Circular Dependency Resolution Algorithm**
   - **Reason:** Components declare dependencies, system validates at registration, but no complex dependency graph solver.
   - **Future Consideration:** If complex dependency chains emerge, may add topological sort for rebuild ordering

4. **Cross-Index Dependencies**
   - **Reason:** Components within an index can depend on each other, but no dependencies across indexes (e.g., StandardsIndex depending on CodeIndex components)
   - **Future Consideration:** Unlikely to be needed based on current architecture

5. **Component Versioning**
   - **Reason:** No version tracking for components or component descriptors
   - **Future Consideration:** Phase 4+ if component API evolves significantly

6. **UI/Dashboard for Health Visualization**
   - **Reason:** Health check output is JSON/structured data, no web UI for visualization
   - **Future Consideration:** Phase 3+ could add health dashboard with component tree visualization

---

#### User Types

**Not Supported:**

- **End Users (Non-Technical)**: This is an internal subsystem feature. No end-user-facing changes or documentation required.
- **External API Consumers**: No public API changes. Health check enhancements are internal only.

---

#### Platforms

**Not Supported:**

- **Python < 3.9**: Minimum Python 3.9 required (consistent with existing prAxis OS requirements)
- **Non-CPython Implementations**: PyPy, Jython not explicitly tested (may work but not guaranteed)

---

#### Integrations

**Not Included:**

- **External Monitoring Systems**: No direct integration with Prometheus, Grafana, DataDog, etc. Health check output can be consumed by these systems but no native exporters.
- **Alerting Systems**: No direct integration with PagerDuty, Slack, etc. External systems can parse health check responses.

---

#### Quality Levels

**Not Included:**

- **Zero Downtime Rebuilds**: Targeted rebuilds are faster (2s vs 30s) but component is unavailable during rebuild
- **Transactional Rebuilds**: No atomic rollback if rebuild partially succeeds then fails
- **Health Check Caching**: Health checks always query components fresh (no caching layer)

---

## 6.1 Future Enhancements

**Potential Phase 2 (Auto-Healing):**
- Automatic rebuild triggers for common failure modes
- Health check result persistence for trend analysis
- Alerting integration (webhook on component failure)

**Potential Phase 3 (Observability):**
- Scheduled health checks (e.g., every 5 minutes)
- Health metrics export to Prometheus
- Web UI for health visualization
- Historical health trends and analysis

**Potential Phase 4+ (Advanced Features):**
- Component versioning and migration support
- Blue-green component deployment
- A/B testing of component implementations
- Cross-index component dependencies

**Explicitly Not Planned:**
- Machine learning-based failure prediction
- Automatic component implementation generation
- Self-healing via code generation

---

## 6.2 Supporting Documentation

Out-of-scope items from:
- **2025-11-08-cascading-health-check-architecture.md**: Design doc explicitly excludes automatic remediation, real-time monitoring, and complex dependency resolution in initial implementation

See `supporting-docs/INSIGHTS.md` for scope boundaries.

---

## 7. Requirements Summary

**Phase 1 Complete - Requirements Gathered**

### Coverage

- **Business Goals**: 5 goals with quantitative success metrics
- **User Stories**: 5 stories (2 critical, 2 high, 1 medium) with acceptance criteria
- **Functional Requirements**: 10 FRs (4 critical, 5 high, 1 medium) organized by category
- **Non-Functional Requirements**: 18 NFRs across 7 categories
- **Out-of-Scope**: 13 items explicitly excluded with rationale

### Traceability

All requirements trace to:
- Business goals (Goal 1-5)
- User stories (Story 1-5)
- Supporting documentation (2025-11-08 design doc)

### Priority Distribution

**Critical**: 4 FRs (component registration, dynamic health check, component-level reporting, targeted rebuild)  
**High**: 5 FRs + majority of NFRs (capability discovery, partial degradation, backward compatibility, fractal pattern, health data contract)  
**Medium**: 1 FR (component dependency tracking)

### Next Phase

Phase 2 will translate these requirements into:
- Technical design decisions
- Component architecture
- API specifications
- Data models
- Integration patterns

---

