# Requirements Traceability: Resilient Index Building

**Project**: prAxIs OS - RAG Subsystem Enhancement  
**Feature**: Resilient Index Building with Fractal Build Status  
**Date**: 2025-11-14  
**Version**: 1.0

---

## Purpose

This document provides complete traceability from requirements (srd.md) to test cases (functional-tests.md, nonfunctional-tests.md). Every requirement must have at least one corresponding test case.

---

## Functional Requirements (31 total)

### FR-001: Build Status Abstract Method
**Requirement**: `BaseIndex` MUST define abstract `build_status()` method  
**Test Coverage**: `test_build_status.py::test_base_index_abstract_method`  
**Status**: ✅ Testable

### FR-002: Build Status Model
**Requirement**: `BuildStatus` model MUST include all specified fields  
**Test Coverage**: `test_build_status.py::test_build_status_model_validation`  
**Status**: ✅ Testable

### FR-003: Build State Enum
**Requirement**: `IndexBuildState` enum MUST define 5 states with priority  
**Test Coverage**: `test_build_status.py::test_build_state_priority`  
**Status**: ✅ Testable

### FR-004: Component-Level Build Status
**Requirement**: Each component MUST have `build_status_check` function  
**Test Coverage**: `test_component_helpers.py::test_component_descriptor_build_status_check`  
**Status**: ✅ Testable

### FR-005: Index-Level Aggregation
**Requirement**: Index classes MUST aggregate component build status  
**Test Coverage**: `test_fractal_build_status.py::test_index_aggregation`  
**Status**: ✅ Testable

### FR-006: Manager-Level Routing
**Requirement**: `IndexManager.route_action()` MUST check build status before queries  
**Test Coverage**: `test_route_action_build_status.py::test_query_routing_with_build_status`  
**Status**: ✅ Testable

### FR-007: Corruption Detection
**Requirement**: System MUST detect corruption in all operations  
**Test Coverage**: `test_auto_repair.py::test_corruption_detection`  
**Status**: ✅ Testable

### FR-008: Callback Pattern Injection
**Requirement**: `IndexManager` MUST inject corruption handler via callback  
**Test Coverage**: `test_auto_repair.py::test_corruption_handler_injection`  
**Status**: ✅ Testable

### FR-009: Auto-Repair Mechanism
**Requirement**: Corruption detection MUST trigger background rebuild  
**Test Coverage**: `test_auto_repair.py::test_auto_repair_triggered`  
**Status**: ✅ Testable

### FR-010: Atomic State Transition
**Requirement**: Cache invalidation + state update MUST be atomic  
**Test Coverage**: `test_index_manager_cache.py::test_atomic_cache_invalidation`  
**Status**: ✅ Testable

### FR-011: Graceful Query Responses
**Requirement**: `route_action()` MUST return "building" response on corruption  
**Test Coverage**: `test_route_action_build_status.py::test_graceful_degradation_on_corruption`  
**Status**: ✅ Testable

### FR-012: Cache Protection
**Requirement**: Build state cache MUST be protected by `RLock`  
**Test Coverage**: `test_index_manager_cache.py::test_cache_thread_safety`  
**Status**: ✅ Testable

### FR-013: Dict Iteration Protection
**Requirement**: `_indexes` dict iteration MUST be protected by `RLock`  
**Test Coverage**: `test_index_manager_cache.py::test_dict_iteration_thread_safety`  
**Status**: ✅ Testable

### FR-014: Atomic Operations
**Requirement**: Cache invalidation + rebuild start MUST be atomic  
**Test Coverage**: `test_auto_repair.py::test_atomic_corruption_handling`  
**Status**: ✅ Testable

### FR-015: Thread-Safe Telemetry
**Requirement**: Telemetry callbacks MUST NOT block main thread  
**Test Coverage**: `test_telemetry.py::test_telemetry_thread_safety`  
**Status**: ✅ Testable

### FR-016: Dynamic TTL Strategy
**Requirement**: TTL MUST vary by state (BUILT: 60s, BUILDING: dynamic, FAILED: 60s)  
**Test Coverage**: `test_index_manager_cache.py::test_dynamic_ttl_calculation`  
**Status**: ✅ Testable

### FR-017: Cache Hit Rate
**Requirement**: Cache hit rate MUST be >99% for BUILT indexes  
**Test Coverage**: `test_performance_build_status.py::test_cache_hit_rate`  
**Status**: ✅ Testable

### FR-018: Lightweight Checks
**Requirement**: Component checks MUST NOT load models or perform test searches  
**Test Coverage**: `test_component_build_status.py::test_lightweight_checks`  
**Status**: ✅ Testable

### FR-019: Progress File Tracking
**Requirement**: Progress files MUST only exist during active builds  
**Test Coverage**: `test_progress_reporting.py::test_progress_file_lifecycle`  
**Status**: ✅ Testable

### FR-020: Query Overhead
**Requirement**: Query overhead MUST be <2ms for cached BUILT indexes  
**Test Coverage**: `test_performance_build_status.py::test_query_overhead`  
**Status**: ✅ Testable

### FR-021: IndexBuildConfig Schema
**Requirement**: Config MUST define 9 fields with defaults  
**Test Coverage**: `test_index_build_config.py::test_config_schema`  
**Status**: ✅ Testable

### FR-022: Config Validation
**Requirement**: Config MUST validate on initialization and log warnings  
**Test Coverage**: `test_index_build_config.py::test_config_validation_warnings`  
**Status**: ✅ Testable

### FR-023: Failure Classification
**Requirement**: System MUST classify failures into 4 categories  
**Test Coverage**: `test_failure_classification.py::test_classify_failure`  
**Status**: ✅ Testable

### FR-024: Pre-flight Checks
**Requirement**: System MUST check disk space before building  
**Test Coverage**: `test_preflight_checks.py::test_disk_space_check`  
**Status**: ✅ Testable

### FR-025: TTL-Based State Management
**Requirement**: Failure states MUST have TTL (config-driven)  
**Test Coverage**: `test_ttl_management.py::test_ttl_expiry`  
**Status**: ✅ Testable

### FR-026: Progress Callback
**Requirement**: `build()` methods MUST accept optional `progress_callback`  
**Test Coverage**: `test_progress_reporting.py::test_progress_callback`  
**Status**: ✅ Testable

### FR-027: Component Progress Tracking
**Requirement**: Each component MUST write progress to file during build  
**Test Coverage**: `test_progress_reporting.py::test_progress_file_writing`  
**Status**: ✅ Testable

### FR-028: Progress Cleanup
**Requirement**: Progress files MUST be deleted when build completes  
**Test Coverage**: `test_progress_reporting.py::test_progress_file_cleanup`  
**Status**: ✅ Testable

### FR-029: Optional Telemetry
**Requirement**: Telemetry MUST be disabled by default and opt-in  
**Test Coverage**: `test_telemetry.py::test_telemetry_disabled_by_default`  
**Status**: ✅ Testable

### FR-030: Event Types
**Requirement**: System MUST emit 7 event types  
**Test Coverage**: `test_telemetry.py::test_telemetry_event_types`  
**Status**: ✅ Testable

### FR-031: Telemetry Safety
**Requirement**: Telemetry callbacks MUST NOT block or crash system  
**Test Coverage**: `test_telemetry.py::test_telemetry_error_handling`  
**Status**: ✅ Testable

---

## Non-Functional Requirements (16 total)

### NFR-001: Query Latency
**Requirement**: P99 query latency MUST NOT increase by >5ms  
**Test Coverage**: `test_performance_build_status.py::test_query_latency_impact`  
**Status**: ✅ Testable

### NFR-002: Build Time
**Requirement**: Index build time MUST NOT increase by >5%  
**Test Coverage**: `test_performance_build_status.py::test_build_time_overhead`  
**Status**: ✅ Testable

### NFR-003: Memory Overhead
**Requirement**: Build state cache MUST use <1KB per index  
**Test Coverage**: `test_performance_build_status.py::test_memory_overhead`  
**Status**: ✅ Testable

### NFR-004: Throughput
**Requirement**: System MUST support 500-1000 queries/second (healthy indexes)  
**Test Coverage**: `test_performance_build_status.py::test_throughput`  
**Status**: ✅ Testable

### NFR-005: Auto-Repair Success Rate
**Requirement**: Auto-repair MUST succeed for 95%+ of corruption events  
**Test Coverage**: `test_auto_repair.py::test_auto_repair_success_rate`  
**Status**: ✅ Testable

### NFR-006: Thread Safety
**Requirement**: System MUST be thread-safe under concurrent access  
**Test Coverage**: `test_chaos_concurrent_rebuilds.py::test_concurrent_corruption_events`  
**Status**: ✅ Testable

### NFR-007: Failure Recovery
**Requirement**: System MUST recover from mid-build corruption, concurrent rebuilds, disk exhaustion  
**Test Coverage**: `test_chaos_*.py` (5 scenarios)  
**Status**: ✅ Testable

### NFR-008: Eventual Consistency
**Requirement**: Corrupted indexes MUST eventually become healthy  
**Test Coverage**: `test_auto_repair.py::test_eventual_consistency`  
**Status**: ✅ Testable

### NFR-009: Error Clarity
**Requirement**: 100% of errors MUST include actionable remediation  
**Test Coverage**: `test_error_messages.py::test_actionable_errors`  
**Status**: ✅ Testable

### NFR-010: Progress Visibility
**Requirement**: Build progress MUST be visible at component, index, and manager levels  
**Test Coverage**: `test_progress_reporting.py::test_progress_visibility_levels`  
**Status**: ✅ Testable

### NFR-011: Health Reporting
**Requirement**: `get_server_info(action="health")` MUST include build status  
**Test Coverage**: `test_health_reporting.py::test_build_status_in_health_report`  
**Status**: ✅ Testable

### NFR-012: Code Quality
**Requirement**: All code MUST pass type checking and linting  
**Test Coverage**: CI/CD pipeline (MyPy, Ruff)  
**Status**: ✅ Testable

### NFR-013: Test Coverage
**Requirement**: Unit test coverage >90%, integration test coverage >80%  
**Test Coverage**: `pytest-cov` report  
**Status**: ✅ Testable

### NFR-014: Documentation
**Requirement**: All public APIs MUST be documented  
**Test Coverage**: Manual review (docstring completeness)  
**Status**: ⚠️ Manual verification required

### NFR-015: Backward Compatibility
**Requirement**: Existing indexes, health checks, and APIs MUST continue to work  
**Test Coverage**: `test_backward_compatibility.py::test_existing_functionality`  
**Status**: ✅ Testable

### NFR-016: Forward Compatibility
**Requirement**: Design MUST support future index types and component types  
**Test Coverage**: Manual review (architecture extensibility)  
**Status**: ⚠️ Manual verification required

---

## Out of Scope Items (5 total)

### OS-001: Async I/O for Progress Files
**Status**: Deferred (premature optimization)  
**Future Consideration**: If profiling shows bottleneck

### OS-002: Full Event System
**Status**: Deferred (overkill for current needs)  
**Future Consideration**: If 3+ handlers needed per event

### OS-003: Distributed Index Building
**Status**: Deferred (single-server architecture)  
**Future Consideration**: If multi-server deployment needed

### OS-004: Index Migration System
**Status**: Deferred (case-by-case breaking changes)  
**Future Consideration**: If frequent schema changes

### OS-005: Real-Time Progress Streaming
**Status**: Deferred (polling-based progress sufficient)  
**Future Consideration**: If sub-second updates needed

---

## Test Coverage Summary

| Category | Total Requirements | Testable | Manual Verification | Coverage % |
|----------|-------------------|----------|---------------------|------------|
| **Functional Requirements** | 31 | 31 | 0 | 100% |
| **Non-Functional Requirements** | 16 | 14 | 2 | 87.5% |
| **Total** | 47 | 45 | 2 | 95.7% |

**Manual Verification Items**:
- NFR-014: Documentation completeness (docstrings)
- NFR-016: Forward compatibility (architecture review)

---

## Traceability Matrix

| Requirement ID | Test File | Test Function | Priority |
|----------------|-----------|---------------|----------|
| FR-001 | test_build_status.py | test_base_index_abstract_method | Critical |
| FR-002 | test_build_status.py | test_build_status_model_validation | Critical |
| FR-003 | test_build_status.py | test_build_state_priority | Critical |
| FR-004 | test_component_helpers.py | test_component_descriptor_build_status_check | Critical |
| FR-005 | test_fractal_build_status.py | test_index_aggregation | Critical |
| FR-006 | test_route_action_build_status.py | test_query_routing_with_build_status | Critical |
| FR-007 | test_auto_repair.py | test_corruption_detection | Critical |
| FR-008 | test_auto_repair.py | test_corruption_handler_injection | Critical |
| FR-009 | test_auto_repair.py | test_auto_repair_triggered | Critical |
| FR-010 | test_index_manager_cache.py | test_atomic_cache_invalidation | Critical |
| FR-011 | test_route_action_build_status.py | test_graceful_degradation_on_corruption | High |
| FR-012 | test_index_manager_cache.py | test_cache_thread_safety | Critical |
| FR-013 | test_index_manager_cache.py | test_dict_iteration_thread_safety | Critical |
| FR-014 | test_auto_repair.py | test_atomic_corruption_handling | Critical |
| FR-015 | test_telemetry.py | test_telemetry_thread_safety | Medium |
| FR-016 | test_index_manager_cache.py | test_dynamic_ttl_calculation | High |
| FR-017 | test_performance_build_status.py | test_cache_hit_rate | High |
| FR-018 | test_component_build_status.py | test_lightweight_checks | High |
| FR-019 | test_progress_reporting.py | test_progress_file_lifecycle | Medium |
| FR-020 | test_performance_build_status.py | test_query_overhead | High |
| FR-021 | test_index_build_config.py | test_config_schema | Medium |
| FR-022 | test_index_build_config.py | test_config_validation_warnings | High |
| FR-023 | test_failure_classification.py | test_classify_failure | Medium |
| FR-024 | test_preflight_checks.py | test_disk_space_check | High |
| FR-025 | test_ttl_management.py | test_ttl_expiry | Medium |
| FR-026 | test_progress_reporting.py | test_progress_callback | Medium |
| FR-027 | test_progress_reporting.py | test_progress_file_writing | Medium |
| FR-028 | test_progress_reporting.py | test_progress_file_cleanup | Medium |
| FR-029 | test_telemetry.py | test_telemetry_disabled_by_default | Low |
| FR-030 | test_telemetry.py | test_telemetry_event_types | Low |
| FR-031 | test_telemetry.py | test_telemetry_error_handling | Medium |
| NFR-001 | test_performance_build_status.py | test_query_latency_impact | Critical |
| NFR-002 | test_performance_build_status.py | test_build_time_overhead | High |
| NFR-003 | test_performance_build_status.py | test_memory_overhead | Medium |
| NFR-004 | test_performance_build_status.py | test_throughput | High |
| NFR-005 | test_auto_repair.py | test_auto_repair_success_rate | Critical |
| NFR-006 | test_chaos_concurrent_rebuilds.py | test_concurrent_corruption_events | Critical |
| NFR-007 | test_chaos_*.py | (5 scenarios) | Critical |
| NFR-008 | test_auto_repair.py | test_eventual_consistency | Critical |
| NFR-009 | test_error_messages.py | test_actionable_errors | High |
| NFR-010 | test_progress_reporting.py | test_progress_visibility_levels | Medium |
| NFR-011 | test_health_reporting.py | test_build_status_in_health_report | High |
| NFR-012 | CI/CD | MyPy, Ruff | Critical |
| NFR-013 | CI/CD | pytest-cov | Critical |
| NFR-014 | Manual | Docstring review | Medium |
| NFR-015 | test_backward_compatibility.py | test_existing_functionality | Critical |
| NFR-016 | Manual | Architecture review | Low |

---

## Approval

**Requirements Traceability Author**: Claude (AI Assistant)  
**Date**: 2025-11-14  
**Status**: Pending Review

**Approval Criteria**:
- [ ] All functional requirements have test coverage
- [ ] All non-functional requirements have test coverage or manual verification plan
- [ ] Traceability matrix is complete
- [ ] Test priorities are assigned

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-14

