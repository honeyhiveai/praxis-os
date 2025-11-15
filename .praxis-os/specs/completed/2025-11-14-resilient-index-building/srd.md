# Software Requirements Document: Resilient Index Building

**Project**: prAxIs OS - RAG Subsystem Enhancement  
**Feature**: Resilient Index Building with Fractal Build Status  
**Date**: 2025-11-14  
**Status**: Requirements Gathering  
**Version**: 1.0

---

## 1. Business Goals

### 1.1 Primary Goal: Eliminate Index Build Blind Spots

**Problem**: Current index building is opaque and brittle - users don't know if indexes are building, failed, or corrupted until queries fail.

**Goal**: Transform index building from a brittle, opaque sequence into a **resilient, observable, and self-healing system**.

**Success Metrics**:
- **Resilience**: 3× improvement over baseline (from 3/10 to 9/10)
- **Observability**: 100% of build failures provide actionable remediation
- **Recovery**: 95%+ of corruption events auto-repair without user intervention
- **Performance**: <2ms query overhead for healthy indexes (99.9% cache hit rate)

### 1.2 Secondary Goal: Establish Architectural Pattern

**Goal**: Create a reusable fractal pattern that can be applied to other subsystems.

**Success Metrics**:
- Pattern documented in standards
- Pattern mirrors existing health check architecture
- Pattern enables composable, introspectable systems

### 1.3 Tertiary Goal: Production-Ready Quality

**Goal**: Achieve production-ready quality validated by multiple reviewers.

**Success Metrics**:
- ✅ Pessimistic principal engineer review: 10/10
- ✅ ChatGPT-5/Cline review: 10/10 (design maturity)
- ✅ All critical/high/medium issues addressed (10/10 fixes applied)
- ✅ Chaos testing validates resilience under stress

---

## 2. User Stories

### 2.1 As an AI Agent

**Story 1: Transparent Build Status**
> As an AI agent querying the RAG index,  
> I want to know if the index is still building,  
> So that I can retry later instead of failing with a cryptic error.

**Acceptance Criteria**:
- Query returns "building" status with progress percentage
- Response includes estimated time remaining
- Response suggests retry interval (e.g., "Retry in 30-60s")

**Story 2: Auto-Repair on Corruption**
> As an AI agent encountering index corruption,  
> I want the system to automatically repair itself,  
> So that I don't need human intervention to continue working.

**Acceptance Criteria**:
- Corruption detected automatically (search, build, update operations)
- Background rebuild triggered without blocking
- Subsequent queries return "building" status
- Eventual consistency achieved (rebuild completes successfully)

**Story 3: Performance Without Overhead**
> As an AI agent querying healthy indexes,  
> I want near-zero performance overhead for build status checks,  
> So that my queries remain fast.

**Acceptance Criteria**:
- <2ms overhead for BUILT indexes (cached)
- 99.9% cache hit rate for stable indexes
- No performance degradation during normal operation

### 2.2 As a Human Developer

**Story 4: Actionable Error Messages**
> As a developer debugging index build failures,  
> I want clear error messages with remediation steps,  
> So that I can fix issues quickly without deep system knowledge.

**Acceptance Criteria**:
- All errors classified (transient, config, resource, corruption)
- Each error includes specific remediation steps
- Config errors provide exact field and suggested value
- Errors visible via `get_server_info(action="health")`

**Story 5: Observable Build Progress**
> As a developer monitoring index builds,  
> I want real-time progress reporting,  
> So that I know the system is working and not stuck.

**Acceptance Criteria**:
- Per-component progress (e.g., "standards.vector: 45%")
- Per-index aggregated progress (e.g., "standards: 66.7%")
- Progress visible via build status API
- Progress updates every 2-10s (dynamic TTL)

**Story 6: Safe Configuration**
> As a developer configuring index building,  
> I want warnings about unsafe settings,  
> So that I don't accidentally misconfigure the system.

**Acceptance Criteria**:
- Config validation on server startup
- Warnings logged for unsafe overrides (low disk threshold, high retries, etc.)
- Warnings include recommended values
- System still allows overrides (flexibility maintained)

---

## 3. Functional Requirements

### 3.1 Fractal Build Status Pattern (FR-001 to FR-006)

**FR-001: Build Status Abstract Method**
- `BaseIndex` MUST define abstract `build_status()` method
- All index implementations MUST implement `build_status()`
- Method MUST return `BuildStatus` model

**FR-002: Build Status Model**
- `BuildStatus` model MUST include:
  - `state: IndexBuildState` (enum)
  - `message: str` (human-readable status)
  - `progress_percent: float` (0-100)
  - `details: Dict[str, Any]` (diagnostic info)
  - `error: Optional[str]` (if state=FAILED)
  - `ttl_expires_at: Optional[datetime]` (for error states)
- Model MUST be frozen (immutable)
- Model MUST forbid extra fields

**FR-003: Build State Enum**
- `IndexBuildState` enum MUST define states:
  - `NOT_BUILT`: Index not yet created
  - `QUEUED_TO_BUILD`: Build queued but not started
  - `BUILDING`: Build in progress
  - `BUILT`: Build complete and healthy
  - `FAILED`: Build failed (with TTL)
- State priority for aggregation: FAILED > BUILDING > QUEUED > NOT_BUILT > BUILT

**FR-004: Component-Level Build Status**
- Each component (vector, fts, metadata, graph) MUST have `build_status_check` function
- `ComponentDescriptor` MUST include `build_status_check: Callable[[], BuildStatus]`
- Component checks MUST be lightweight (<100ms each)

**FR-005: Index-Level Aggregation**
- Index classes MUST aggregate component build status via `dynamic_build_status()`
- Aggregation MUST follow fractal pattern (mirrors `dynamic_health_check()`)
- Aggregated progress MUST be average of component progress

**FR-006: Manager-Level Routing**
- `IndexManager.route_action()` MUST check build status before executing queries
- If index is BUILDING, MUST return "building" response (not error)
- If index is FAILED, MUST return "failed" response with remediation
- If index is BUILT, MUST execute query normally

### 3.2 Corruption Handling (FR-007 to FR-011)

**FR-007: Corruption Detection**
- System MUST detect corruption in all operations: `search()`, `build()`, `update()`
- Detection MUST use `is_corruption_error()` function
- Known corruption patterns MUST be checked

**FR-008: Callback Pattern Injection**
- `IndexManager` MUST inject corruption handler into indexes via callback
- Indexes MUST accept handler via `set_corruption_handler(callback)` method
- No back-references to `IndexManager` allowed (avoid circular dependencies)

**FR-009: Auto-Repair Mechanism**
- Corruption detection MUST trigger background rebuild automatically
- Background rebuild MUST run in daemon thread
- Original query MUST raise `ActionableError` with "auto-repair in progress" message

**FR-010: Atomic State Transition**
- Cache invalidation + state update MUST be atomic (protected by lock)
- State MUST transition: BUILT → BUILDING (on corruption detection)
- Cache MUST be invalidated before rebuild starts

**FR-011: Graceful Query Responses**
- `route_action()` MUST catch corruption errors
- Subsequent queries MUST receive "building" response (not error)
- Response MUST include progress and retry suggestion

### 3.3 Thread Safety (FR-012 to FR-015)

**FR-012: Cache Protection**
- Build state cache MUST be protected by `RLock`
- All cache reads/writes MUST acquire lock
- Lock MUST be reentrant (allow nested calls)

**FR-013: Dict Iteration Protection**
- `_indexes` dict iteration MUST be protected by `RLock`
- All iterations MUST acquire lock before accessing dict
- Lock prevents concurrent modification during iteration

**FR-014: Atomic Operations**
- Cache invalidation + rebuild start MUST be atomic
- No race conditions between cache read and state update
- Lock held for entire critical section

**FR-015: Thread-Safe Telemetry**
- Telemetry callbacks MUST NOT block main thread
- Telemetry errors MUST NOT crash system
- Telemetry MUST be optional (disabled by default)

### 3.4 Performance & Caching (FR-016 to FR-020)

**FR-016: Dynamic TTL Strategy**
- BUILT state: 60s TTL (stable, rarely changes)
- BUILDING state: Dynamic TTL based on progress:
  - 0-10% progress: 2s TTL (early stage, fast changes)
  - 10-50% progress: 5s TTL (mid stage, steady)
  - 50-100% progress: 10s TTL (late stage, slow)
- FAILED state: 60s TTL (stable until intervention)
- NOT_BUILT/QUEUED: 0s TTL (no cache)

**FR-017: Cache Hit Rate**
- Cache hit rate MUST be >99% for BUILT indexes
- Cache miss overhead MUST be <100ms
- Cache MUST be invalidated after build/rebuild

**FR-018: Lightweight Checks**
- Component build status checks MUST NOT load embedding models
- Component build status checks MUST NOT perform test searches
- Component build status checks MUST only verify: table exists + has rows
- Estimated cost: ~15-70ms (vs 145-720ms for health checks)

**FR-019: Progress File Tracking**
- Progress files MUST only exist during active builds
- Progress files MUST be deleted when build completes
- Progress files MUST be <1KB (JSON format)
- Progress file writes MUST be non-blocking

**FR-020: Query Overhead**
- Query overhead MUST be <2ms for cached BUILT indexes
- Query overhead MUST be <10ms for cached BUILDING indexes
- Query overhead MUST be <100ms for cache misses

### 3.5 Configuration & Validation (FR-021 to FR-025)

**FR-021: IndexBuildConfig Schema**
- Config MUST define:
  - `disk_space_threshold_gb: float` (default: 2.0)
  - `max_retries: int` (default: 3)
  - `retry_backoff_base: float` (default: 2.0)
  - `transient_error_keywords: list[str]`
  - `config_error_ttl_hours: Optional[float]` (default: None = until restart)
  - `transient_error_ttl_hours: float` (default: 24.0)
  - `resource_error_ttl_hours: float` (default: 1.0)
  - `report_progress_per_component: bool` (default: True)
  - `telemetry_enabled: bool` (default: False)

**FR-022: Config Validation**
- Config MUST validate on initialization via `model_post_init()`
- Validation MUST log warnings for unsafe overrides:
  - Disk space threshold <1GB
  - Max retries >5 or =0
  - TTLs too short (<1h for transient)
  - Backoff base too high (>5.0)
- Warnings MUST include recommended values
- Validation MUST NOT block (warnings only)

**FR-023: Failure Classification**
- System MUST classify failures into categories:
  - **Transient**: Network timeouts, model downloads (retry with backoff)
  - **Config**: Invalid model names, missing paths (no retry, persist until restart)
  - **Resource**: Disk full, OOM (conditional retry, short TTL)
  - **Corruption**: Broken index files (auto-repair, no retry)
- Classification MUST be dynamic (config-driven keywords)

**FR-024: Pre-flight Checks**
- System MUST check disk space before building (config-driven threshold)
- Check MUST fail fast with clear error if insufficient space
- Error MUST include required space and remediation steps

**FR-025: TTL-Based State Management**
- Failure states MUST have TTL (time-to-live)
- Config errors: TTL=None (persist until server restart)
- Transient errors: TTL=24h (configurable)
- Resource errors: TTL=1h (configurable)
- TTL expiry MUST auto-clear failure state

### 3.6 Progress Reporting (FR-026 to FR-028)

**FR-026: Progress Callback**
- `build()` methods MUST accept optional `progress_callback` parameter
- Callback signature: `Callable[[float, str], None]` (progress_percent, message)
- Callback MUST be called at key milestones (file processing, embedding, indexing)

**FR-027: Component Progress Tracking**
- Each component MUST write progress to file during build
- Progress file format: JSON with state, message, progress_percent, timestamp
- Progress files MUST be read by `_check_*_build_status()` methods

**FR-028: Progress Cleanup**
- Progress files MUST be deleted when build completes (success or failure)
- Stale progress files (>1h old) MUST be ignored
- Progress file writes MUST NOT block build process

### 3.7 Telemetry & Observability (FR-029 to FR-031)

**FR-029: Optional Telemetry**
- Telemetry MUST be disabled by default
- Telemetry MUST be opt-in via config
- Telemetry callback MUST be injectable via `set_telemetry_callback()`

**FR-030: Event Types**
- System MUST emit events for:
  - `build_started`: Index build initiated
  - `build_progress`: Build progress update
  - `build_completed`: Index build finished
  - `build_failed`: Index build failed
  - `corruption_detected`: Index corruption detected
  - `auto_repair_started`: Auto-repair initiated
  - `auto_repair_completed`: Auto-repair finished

**FR-031: Telemetry Safety**
- Telemetry callbacks MUST NOT block main thread
- Telemetry errors MUST be caught and logged (not propagated)
- Telemetry MUST NOT impact performance when disabled

---

## 4. Non-Functional Requirements

### 4.1 Performance (NFR-001 to NFR-004)

**NFR-001: Query Latency**
- P99 query latency MUST NOT increase by >5ms
- Cached build status checks MUST complete in <2ms
- Cache hit rate MUST be >99% for BUILT indexes

**NFR-002: Build Time**
- Index build time MUST NOT increase by >5%
- Progress reporting overhead MUST be <1% of build time
- Progress file writes MUST be <5ms each

**NFR-003: Memory Overhead**
- Build state cache MUST use <1KB per index
- Progress files MUST be <1KB each
- Total memory overhead MUST be <100KB

**NFR-004: Throughput**
- System MUST support 500-1000 queries/second (healthy indexes)
- System MUST support 10-50 queries/second (building indexes)
- Cache must not become bottleneck under load

### 4.2 Reliability (NFR-005 to NFR-008)

**NFR-005: Auto-Repair Success Rate**
- Auto-repair MUST succeed for 95%+ of corruption events
- Auto-repair MUST complete within 60s for small indexes (<1000 chunks)
- Auto-repair MUST complete within 5min for large indexes (>10,000 chunks)

**NFR-006: Thread Safety**
- System MUST be thread-safe under concurrent access
- No race conditions under 100 concurrent queries
- No deadlocks under any scenario

**NFR-007: Failure Recovery**
- System MUST recover from mid-build corruption
- System MUST recover from concurrent rebuild requests
- System MUST recover from disk space exhaustion

**NFR-008: Eventual Consistency**
- Corrupted indexes MUST eventually become healthy (via auto-repair)
- Build failures MUST eventually clear (via TTL expiry)
- System MUST converge to healthy state

### 4.3 Observability (NFR-009 to NFR-011)

**NFR-009: Error Clarity**
- 100% of errors MUST include actionable remediation
- Error messages MUST be specific (not generic)
- Config errors MUST include exact field and suggested value

**NFR-010: Progress Visibility**
- Build progress MUST be visible at component level
- Build progress MUST be visible at index level
- Build progress MUST be visible at manager level

**NFR-011: Health Reporting**
- `get_server_info(action="health")` MUST include build status
- Health report MUST include failure details (if any)
- Health report MUST include remediation steps

### 4.4 Maintainability (NFR-012 to NFR-014)

**NFR-012: Code Quality**
- All code MUST pass type checking (MyPy)
- All code MUST pass linting (Ruff)
- All code MUST have docstrings (Google style)

**NFR-013: Test Coverage**
- Unit test coverage MUST be >90%
- Integration test coverage MUST be >80%
- Chaos tests MUST validate resilience under stress

**NFR-014: Documentation**
- All public APIs MUST be documented
- All config options MUST be documented
- All error codes MUST be documented

### 4.5 Compatibility (NFR-015 to NFR-016)

**NFR-015: Backward Compatibility**
- Existing indexes MUST continue to work
- Existing health checks MUST continue to work
- Existing APIs MUST NOT break

**NFR-016: Forward Compatibility**
- Design MUST support future index types
- Design MUST support future component types
- Design MUST support future telemetry backends

---

## 5. Out of Scope

### 5.1 Explicitly NOT Included

**OS-001: Async I/O for Progress Files**
- Rationale: Premature optimization (progress files are <1KB, writes are ~1-5ms)
- Future consideration: If profiling shows bottleneck
- Deferred to: Post-V1 optimization

**OS-002: Full Event System**
- Rationale: Overkill for current needs (1 trigger → 1 action)
- Future consideration: If 3+ handlers needed per event
- Deferred to: Future observability enhancement

**OS-003: Distributed Index Building**
- Rationale: Out of scope for single-server architecture
- Future consideration: If multi-server deployment needed
- Deferred to: Future scalability work

**OS-004: Index Migration System**
- Rationale: Breaking changes handled case-by-case
- Future consideration: If frequent schema changes occur
- Deferred to: Future maintenance work

**OS-005: Real-Time Progress Streaming**
- Rationale: Polling-based progress (2-10s updates) is sufficient
- Future consideration: If sub-second updates needed
- Deferred to: Future UX enhancement

### 5.2 Assumptions & Dependencies

**Assumption 1**: Single-server deployment (no distributed coordination needed)

**Assumption 2**: Indexes fit in memory (no out-of-core index building)

**Assumption 3**: LanceDB and DuckDB are stable (no database engine changes)

**Assumption 4**: Python 3.10+ (for type hints and Pydantic v2)

**Dependency 1**: Pydantic v2 for config validation

**Dependency 2**: Threading module for background rebuilds

**Dependency 3**: Existing health check infrastructure

---

## 6. Success Metrics

### 6.1 Quantitative Metrics

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| **Resilience Score** | 3/10 | 9/10 | Manual assessment (retry logic, failure classification, progress reporting) |
| **Auto-Repair Success Rate** | 0% | 95%+ | `(successful_auto_repairs / total_corruption_events) * 100` |
| **Cache Hit Rate** | N/A | 99%+ | `(cache_hits / total_build_status_checks) * 100` |
| **Query Overhead (cached)** | N/A | <2ms | P99 latency increase for BUILT indexes |
| **Query Overhead (cache miss)** | N/A | <100ms | P99 latency for cache miss scenarios |
| **Error Actionability** | ~30% | 100% | `(errors_with_remediation / total_errors) * 100` |
| **Test Coverage** | N/A | >90% | Unit + integration test coverage |

### 6.2 Qualitative Metrics

**Design Quality**:
- ✅ Pessimistic principal engineer review: 10/10
- ✅ ChatGPT-5/Cline review: 10/10 (design maturity)

**Architectural Alignment**:
- ✅ Fractal pattern mirrors health checks
- ✅ Consistent with prAxIs OS philosophy

**Production Readiness**:
- ✅ All 10 critical/high/medium issues addressed
- ✅ Chaos testing validates resilience
- ✅ Config validation prevents misconfigurations

---

## 7. References

### 7.1 Supporting Documents

All supporting documents are located in `supporting-docs/`:

1. **2025-11-14-resilient-index-building-COMPREHENSIVE-V2.md** (55KB)
   - Primary design document with all 10 fixes and ChatGPT-5 enhancements
   - Sections: Fractal architecture, corruption handling, thread safety, performance, config, progress reporting

2. **2025-11-14-REVIEW-SUMMARY.md** (10KB)
   - Pessimistic principal engineer review
   - 10 critical/high/medium issues identified and fixed
   - V1 vs V2 comparison

3. **2025-11-14-resilient-index-building-feedback.md** (2.3KB)
   - ChatGPT-5/Cline formal review
   - 10/10 rating (design maturity)
   - 4 recommendations (3 integrated, 1 deferred)

4. **2025-11-14-build-status-performance-analysis.md** (17KB)
   - Detailed performance analysis
   - Three-tier caching strategy
   - Performance tables and optimization strategies

5. **2025-11-14-event-system-analysis.md** (20KB)
   - Event system analysis
   - Corruption handling design
   - Auto-repair mechanism

### 7.2 Related Standards

- `cascading-health-check-architecture/` - Fractal pattern reference
- `stateless-instance-architecture.md` - AI statelessness principles
- `ai-capabilities-trust.md` - AI operational guidelines
- `retry-strategies.md` - Exponential backoff patterns
- `graceful-degradation.md` - Handling partial failures

---

## 8. Approval

**Requirements Author**: Claude (AI Assistant)  
**Date**: 2025-11-14  
**Status**: Pending Review

**Reviewers**:
- [ ] Technical Lead
- [ ] Product Owner
- [ ] Architecture Review Board

**Approval Criteria**:
- [ ] All functional requirements are clear and testable
- [ ] Non-functional requirements are measurable
- [ ] Out-of-scope items are explicitly documented
- [ ] Success metrics are defined
- [ ] Supporting documents are referenced

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-14  
**Next Review**: After Phase 2 (Technical Design)

