# Requirements Traceability Matrix

**Purpose:** Maps requirements → test files → test functions  
**Date:** 2025-11-06

---

## Functional Requirements Traceability

| Requirement | Test File | Test Function(s) | Status |
|-------------|-----------|------------------|--------|
| FR-001: Query Prepend Generation | tests/ouroboros/middleware/test_prepend_generator.py | test_prepend_includes_gamification() | ✅ Exists |
|  |  | test_prepend_generation_with_history() | ✅ Exists |
| FR-002: Query Tracking | tests/ouroboros/middleware/test_query_tracker.py | test_query_logged_to_db() | ✅ Exists |
|  |  | test_query_metadata_captured() | ✅ Exists |
| FR-003: Query Diversity Classification | tests/ouroboros/middleware/test_query_classifier.py | test_classify_by_angle() | ✅ Exists |
|  |  | test_all_angles_classified() | ✅ Exists |
| FR-004: Behavioral Drift Detection | tests/ouroboros/middleware/test_query_tracker.py | test_drift_detection() | ❌ Planned |
| FR-005: pos_search_project Tool | tests/ouroboros/tools/test_pos_search.py | test_search_standards() | ❌ Planned |
|  |  | test_search_code() | ❌ Planned |
|  |  | test_find_callers() | ❌ Planned |
| FR-006: pos_workflow Tool | tests/server/tools/test_workflow_tools.py | test_workflow_start() | ✅ Exists |
|  |  | test_workflow_get_phase() | ✅ Exists |
|  |  | test_workflow_complete_phase() | ✅ Exists |
| FR-007: pos_browser Tool | tests/ouroboros/integration/test_browser_flow.py | test_browser_navigate() | ✅ Exists |
|  |  | test_browser_session_isolation() | ✅ Exists |
| FR-008: pos_filesystem Tool | tests/ouroboros/tools/test_pos_filesystem.py | test_filesystem_path_validation() | ❌ Planned |
|  |  | test_filesystem_gitignore_respect() | ❌ Planned |
| FR-009: get_server_info Tool | tests/unit/test_server_info_tools.py | test_server_status() | ✅ Exists |
|  |  | test_server_health() | ✅ Exists |
| FR-010: Tool Auto-Discovery | tests/ouroboros/tools/test_tool_registry.py | test_tool_discovery() | ❌ Planned |
|  |  | test_tool_registration() | ❌ Planned |
| FR-011: Standards Hybrid Search | tests/ouroboros/integration/test_search_flow.py | test_hybrid_search() | ✅ Exists |
|  |  | test_search_with_reranking() | ❌ Planned |
| FR-012: Code Semantic Search | tests/ouroboros/subsystems/rag/test_code_index.py | test_code_search_semantic() | ❌ Planned |
| FR-013: Code Graph Traversal | tests/ouroboros/subsystems/rag/test_graph_index.py | test_find_callers() | ❌ Planned |
|  |  | test_find_dependencies() | ❌ Planned |
|  |  | test_find_call_paths() | ❌ Planned |
| FR-014: AST Structural Search | tests/ouroboros/subsystems/rag/test_ast_index.py | test_ast_query() | ❌ Planned |
| **FR-015: File Watcher** | **tests/ouroboros/subsystems/rag/test_file_watcher.py** | **test_watcher_detects_file_changes()** | **❌ MISSING** |
|  |  | **test_watcher_triggers_index_update()** | **❌ MISSING** |
|  |  | **test_watcher_debouncing()** | **❌ MISSING** |
|  |  | **test_watcher_path_mapping()** | **❌ MISSING** |
| FR-016: Index Health Checks | tests/ouroboros/subsystems/rag/test_index_manager.py | test_health_check_all() | ✅ Exists |
|  |  | test_auto_repair() | ❌ Planned |
| FR-017: Phase-Gated Execution | tests/ouroboros/integration/test_workflow_flow.py | test_phase_gating() | ✅ Exists |
|  |  | test_cannot_skip_phases() | ❌ Planned |
| FR-018: Evidence Validation | tests/integration/test_evidence_validation_integration.py | test_multi_layer_validation() | ✅ Exists |
| FR-019: Hidden Evidence Schemas | tests/ouroboros/subsystems/workflow/test_checkpoint_loader.py | test_schemas_not_exposed() | ❌ Planned |
| FR-020: Workflow State Persistence | tests/unit/test_workflow_session.py | test_state_persistence() | ✅ Exists |
|  |  | test_workflow_resumable() | ❌ Planned |
| FR-021: Isolated Playwright Sessions | tests/ouroboros/integration/test_browser_flow.py | test_session_isolation() | ✅ Exists |
| FR-022: Browser Actions | tests/integration/test_browser_tools.py | test_browser_navigate() | ✅ Exists |
|  |  | test_browser_click() | ✅ Exists |
|  |  | test_browser_type() | ✅ Exists |
| FR-023: Pydantic v2 Validation | tests/ouroboros/config/test_config_validation.py | test_config_validation() | ❌ Planned |
|  |  | test_fail_fast_errors() | ❌ Planned |
| FR-024: Config-Driven Languages | tests/ouroboros/config/test_language_config.py | test_add_language_via_yaml() | ❌ Planned |
| FR-025: Fail-Fast Validation | tests/ouroboros/config/test_config_validation.py | test_startup_validation() | ❌ Planned |

---

## Non-Functional Requirements Traceability

### Performance Tests

| Requirement | Test File | Test Function(s) | Metric Target | Status |
|-------------|-----------|------------------|---------------|--------|
| NFR-P1: Cold Start | tests/ouroboros/performance/test_performance.py | test_cold_start_latency() | <30s p95 | ✅ Exists |
| NFR-P2: Config Load | tests/ouroboros/performance/test_performance.py | test_config_load_time() | <100ms p95 | ❌ Planned |
| NFR-P3: Search Latency | tests/ouroboros/performance/test_performance.py | test_hybrid_search_latency() | <200ms p95 | ❌ Planned |
| NFR-P4: Graph Query Latency | tests/ouroboros/performance/test_performance.py | test_graph_query_latency() | <100ms p95 | ❌ Planned |
| **NFR-P5: Incremental Update** | **tests/ouroboros/integration/test_file_watcher_latency.py** | **test_file_save_to_searchable_latency()** | **<5s p95** | **❌ MISSING** |
| NFR-P6: Prepend Overhead | tests/ouroboros/performance/test_performance.py | test_prepend_generation_latency() | <5ms p95 | ❌ Planned |
| NFR-P7: Memory Usage | tests/ouroboros/performance/test_performance.py | test_memory_usage_normal_operation() | <2GB RSS | ❌ Planned |

### Reliability Tests

| Requirement | Test File | Test Function(s) | Metric Target | Status |
|-------------|-----------|------------------|---------------|--------|
| NFR-R1: Uptime | tests/ouroboros/integration/test_reliability_soak.py | test_24_hour_uptime() | 24+ hours | ❌ Planned |
| NFR-R2: Health Check Coverage | tests/ouroboros/integration/test_index_health.py | test_corruption_detection_rate() | 95%+ | ❌ Planned |
| NFR-R3: Auto-Repair Success | tests/ouroboros/integration/test_index_health.py | test_auto_repair_success_rate() | 90%+ | ❌ Planned |
| NFR-R4: Graceful Degradation | tests/ouroboros/integration/test_search_flow.py | test_fallback_to_vector_only() | Search continues | ❌ Planned |
| NFR-R5: Data Integrity | tests/ouroboros/integration/test_index_integrity.py | test_incremental_vs_full_rebuild() | Identical | ❌ Planned |

### Security Tests

| Requirement | Test File | Test Function(s) | Metric Target | Status |
|-------------|-----------|------------------|---------------|--------|
| NFR-S1: Adversarial Design | tests/ouroboros/validation/test_behavioral_engineering.py | test_gaming_attempts_rejected() | 99%+ | ✅ Exists |
| NFR-S2: Query Sanitization | tests/security/test_query_logging.py | test_no_pii_in_logs() | No PII | ❌ Planned |
| NFR-S3: Path Traversal | tests/security/test_path_validation.py | test_path_traversal_blocked() | All blocked | ❌ Planned |
| NFR-S4: Secrets Management | tests/security/test_secrets.py | test_no_secrets_in_git() | No secrets | ❌ Planned |

### Other NFR Categories

| Requirement | Test File | Test Function(s) | Status |
|-------------|-----------|------------------|--------|
| NFR-SC1: Document Scaling | tests/ouroboros/performance/test_performance.py | test_50k_documents() | ❌ Planned |
| NFR-SC2: Symbol Scaling | tests/ouroboros/performance/test_performance.py | test_100k_symbols() | ❌ Planned |
| NFR-SC3: Concurrent Queries | tests/ouroboros/integration/test_thread_safety.py | test_concurrent_queries() | ✅ Exists |
| NFR-M1: No Circular Dependencies | tests/ouroboros/validation/test_architecture.py | test_no_circular_imports() | ❌ Planned |
| NFR-M2: Clean Architecture | tests/ouroboros/validation/test_architecture.py | test_no_cross_subsystem_imports() | ❌ Planned |
| NFR-M3: Integration Test Coverage | tests/conftest.py | test_coverage_report() | ❌ Planned |
| NFR-M4: Error Message Quality | tests/ouroboros/validation/test_error_messages.py | test_all_errors_actionable() | ❌ Planned |
| NFR-M5: Documentation Coverage | tests/ouroboros/validation/test_documentation.py | test_public_api_documented() | ❌ Planned |
| NFR-U1-U4: Usability | tests/ouroboros/integration/test_usability.py | (Multiple tests) | ❌ Planned |
| NFR-E1-E3: Extensibility | tests/ouroboros/integration/test_extensibility.py | (Multiple tests) | ❌ Planned |
| NFR-PO1-PO3: Portability | tests/ouroboros/integration/test_platform_compat.py | (Multiple tests) | ❌ Planned |
| NFR-C1-C3: Compatibility | tests/ouroboros/integration/test_compatibility.py | (Multiple tests) | ❌ Planned |
| NFR-O1-O4: Observability | tests/ouroboros/integration/test_observability.py | (Multiple tests) | ❌ Planned |
| NFR-T1-T3: Testability | tests/ouroboros/validation/test_testability.py | (Multiple tests) | ❌ Planned |

---

## Test Organization

**Directory structure:**
```
tests/
├── ouroboros/
│   ├── config/
│   ├── foundation/
│   ├── middleware/
│   ├── subsystems/
│   │   ├── rag/
│   │   │   ├── test_index_manager.py
│   │   │   ├── test_file_watcher.py (❌ MISSING - FR-015)
│   │   │   ├── test_code_index.py (❌ MISSING)
│   │   │   ├── test_graph_index.py (❌ MISSING)
│   │   │   └── test_ast_index.py (❌ MISSING)
│   │   ├── workflow/
│   │   └── browser/
│   ├── tools/
│   ├── integration/
│   ├── performance/
│   └── validation/
├── integration/
├── security/
└── unit/
```

**Test counts by type:**
- Unit tests (existing): ~37
- Integration tests (existing): ~13
- Performance tests (existing): ~1
- Security tests (existing): ~1
- **Tests needed for 100% traceability: ~52**

**Critical Gaps:**
1. **FR-015 (File Watcher): ZERO tests** ← This caused the production bug
2. FR-005 (pos_search_project tool): No comprehensive tests
3. FR-010 (Tool Auto-Discovery): No tests
4. FR-023-025 (Config system): No validation tests
5. Most NFRs lack verification tests

---

## Traceability Summary

- **FRs mapped to tests:** 25/25 (100% planned, ~40% implemented)
- **NFRs mapped to tests:** 44/44 (100% planned, ~10% implemented)
- **Total test functions planned:** ~170
- **Total test functions existing:** ~52
- **Test functions needed:** ~118

**Critical Finding:** FR-015 (File Watcher) had NO tests mapped, which allowed the initialization bug to reach production.

