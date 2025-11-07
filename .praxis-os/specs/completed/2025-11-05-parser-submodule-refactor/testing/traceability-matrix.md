# Requirements Traceability Matrix

**Purpose:** Maps requirements → test files → test functions  
**Date:** 2025-11-05

---

## Functional Requirements Traceability

| Requirement | Test File | Test Function(s) | Status |
|-------------|-----------|------------------|--------|
| FR-001: Extensible Parser Architecture | tests/unit/test_parsers.py | test_parser_base_class_exists() | ✅ Exists |
|  |  | test_markdown_parser_exists() | ✅ Exists |
|  |  | test_yaml_parser_exists() | ✅ Exists |
|  |  | test_shared_utilities_exist() | ❌ Planned |
| FR-002: Module Size Constraints | tests/validation/test_module_sizes.py | test_no_module_exceeds_500_lines() | ❌ Planned |
|  |  | test_all_modules_within_target_range() | ❌ Planned |
| FR-003: Backward Compatibility | tests/integration/test_backward_compat.py | test_old_imports_work() | ✅ Exists |
|  |  | test_deprecation_warnings_emitted() | ❌ Planned |
| FR-004: Plugin-Like Parser Pattern | tests/unit/test_parsers.py | test_new_parser_registration() | ❌ Planned |
|  |  | test_parser_isolation() | ❌ Planned |
| FR-005: Incremental Migration | tests/integration/test_migration.py | test_8_phase_migration() | ❌ Planned |
|  |  | test_rollback_capability() | ❌ Planned |
| **FR-006: Defensive Format Parsing** | **tests/unit/test_semantic_parser.py** | **test_semantic_scoring()** | **✅ Exists** |
|  |  | **test_phase_detection()** | **✅ Exists** |
|  |  | **test_task_detection()** | **✅ Exists** |
| **FR-007: Phase Shift Detection** | **tests/unit/test_semantic_parser.py** | **test_phase_shift_phase_0_to_1()** | **❌ CRITICAL MISSING** |
|  |  | **test_phase_shift_phase_3_to_1()** | **❌ CRITICAL MISSING** |
|  |  | **test_phase_regression_detected()** | **❌ CRITICAL MISSING** |
| **FR-008: Sequential Phase Validation** | **tests/unit/test_semantic_parser.py** | **test_reject_phase_skip()** | **❌ CRITICAL MISSING** |
|  |  | **test_1_to_3_rejected()** | **❌ CRITICAL MISSING** |
|  |  | **test_sequential_phases_accepted()** | **❌ CRITICAL MISSING** |
| FR-009: Cross-Phase Dependencies | tests/unit/test_parsers.py | test_future_phase_dependency_rejected() | ❌ Planned |
|  |  | test_valid_dependencies_accepted() | ❌ Planned |
| FR-010: Task ID Normalization | tests/unit/test_semantic_parser.py | test_task_id_normalization() | ✅ Exists |
|  |  | test_various_formats_normalized() | ❌ Planned |
| FR-011: Dependency Format Preservation | tests/unit/test_parsers.py | test_dependency_string_preserved() | ❌ Planned |

---

## Non-Functional Requirements Traceability

### Performance Tests

| Requirement | Test File | Test Function(s) | Metric Target | Status |
|-------------|-----------|------------------|---------------|--------|
| NFR-P1: Parsing Speed | tests/performance/test_parser_performance.py | test_tasks_parsing_speed() | ≤100ms for 50KB | ❌ Planned |
|  |  | test_no_performance_regression() | ±5% variance | ❌ Planned |
| NFR-P2: Memory Efficiency | tests/performance/test_parser_performance.py | test_memory_usage() | ≤50MB peak | ❌ Planned |
|  |  | test_no_memory_leaks() | No leaks | ❌ Planned |

### Reliability Tests

| Requirement | Test File | Test Function(s) | Metric Target | Status |
|-------------|-----------|------------------|---------------|--------|
| **NFR-R1: Zero Regressions** | **tests/integration/test_regression.py** | **test_all_completed_specs_parse_identically()** | **100%** | **❌ CRITICAL MISSING** |
|  |  | **test_529_tests_pass()** | **100%** | **✅ Exists (implicit)** |
| NFR-R2: Error Handling | tests/unit/test_parsers.py | test_parse_error_actionable() | All errors actionable | ✅ Exists |
|  |  | test_error_messages_include_location() | All have location | ❌ Planned |

### Maintainability Tests

| Requirement | Test File | Test Function(s) | Metric Target | Status |
|-------------|-----------|------------------|---------------|--------|
| NFR-M1: Module Size Limits | tests/validation/test_module_sizes.py | test_max_500_lines_per_module() | Max 500 lines | ❌ Planned |
| NFR-M2: Code Organization | tests/validation/test_architecture.py | test_no_circular_imports() | 0 circular | ❌ Planned |
|  |  | test_single_responsibility() | SRP enforced | ❌ Planned |
| NFR-M3: Documentation | tests/validation/test_documentation.py | test_all_public_functions_documented() | 100% | ❌ Planned |

### Testability Tests

| Requirement | Test File | Test Function(s) | Metric Target | Status |
|-------------|-----------|------------------|---------------|--------|
| NFR-T1: Test Coverage | tests/conftest.py | test_coverage_report() | ≥85% | ❌ Planned |
|  |  | test_critical_paths_100_percent() | 100% | ❌ Planned |
| NFR-T2: Test Isolation | tests/validation/test_test_isolation.py | test_all_tests_run_independently() | No deps | ❌ Planned |
| NFR-T3: Test Speed | tests/validation/test_test_speed.py | test_full_suite_under_30s() | <30s | ❌ Planned |
|  |  | test_individual_modules_under_2s() | <2s | ❌ Planned |

### Compatibility Tests

| Requirement | Test File | Test Function(s) | Metric Target | Status |
|-------------|-----------|------------------|---------------|--------|
| NFR-C1: Backward Compatibility | tests/integration/test_backward_compat.py | test_old_imports_work() | All work | ✅ Exists |
|  |  | test_deprecation_warnings() | Warnings emitted | ❌ Planned |
| NFR-C2: Python Version | tests/integration/test_python_compat.py | test_python_39_plus() | Works on 3.9+ | ❌ Planned |
| NFR-C3: Dependency Stability | tests/integration/test_dependencies.py | test_no_new_dependencies() | 0 new | ❌ Planned |

### Extensibility Tests

| Requirement | Test File | Test Function(s) | Metric Target | Status |
|-------------|-----------|------------------|---------------|--------|
| NFR-E1: Parser Addition Effort | tests/integration/test_extensibility.py | test_add_new_parser_effort() | ≤4 hours | ❌ Planned |
|  |  | test_zero_existing_file_modifications() | 0 modifications | ❌ Planned |
| NFR-E2: Shared Utility Reuse | tests/integration/test_extensibility.py | test_code_reuse_rate() | ≥60% | ❌ Planned |

### Deployment Tests

| Requirement | Test File | Test Function(s) | Metric Target | Status |
|-------------|-----------|------------------|---------------|--------|
| NFR-D1: Migration Safety | tests/integration/test_migration.py | test_8_phase_incremental_migration() | 8 phases | ❌ Planned |
|  |  | test_each_phase_independently_verifiable() | All verifiable | ❌ Planned |
| NFR-D2: Zero Downtime | tests/integration/test_migration.py | test_no_service_interruption() | No downtime | ❌ Planned |

### Quality Assurance Tests

| Requirement | Test File | Test Function(s) | Metric Target | Status |
|-------------|-----------|------------------|---------------|--------|
| NFR-Q1: Linting Compliance | tests/validation/test_linting.py | test_zero_linting_errors() | 0 errors | ❌ Planned |
|  |  | test_type_hints_on_all_public_functions() | 100% | ❌ Planned |
| NFR-Q2: Code Review | N/A (manual process) | N/A | Review required | N/A |

### Configuration Tests

| Requirement | Test File | Test Function(s) | Metric Target | Status |
|-------------|-----------|------------------|---------------|--------|
| NFR-SC1: Scoring Thresholds | tests/unit/test_semantic_parser.py | test_thresholds_configurable() | Configurable | ❌ Planned |
|  |  | test_default_thresholds_30() | Defaults = 30.0 | ❌ Planned |
| NFR-SC2: Scoring Signals | tests/unit/test_semantic_parser.py | test_multi_signal_evaluation() | Multi-signal | ✅ Exists |
|  |  | test_signals_tunable() | Tunable | ❌ Planned |

---

## Test Organization

**Directory structure:**
```
tests/
├── unit/
│   ├── test_parsers.py (✅ exists - 300+ lines)
│   ├── test_semantic_parser.py (✅ exists - 400+ lines)
│   └── test_shared_utilities.py (❌ planned)
│
├── integration/
│   ├── test_backward_compat.py (✅ partial)
│   ├── test_regression.py (❌ CRITICAL MISSING - NFR-R1)
│   ├── test_migration.py (❌ planned)
│   └── test_extensibility.py (❌ planned)
│
├── performance/
│   └── test_parser_performance.py (❌ planned)
│
└── validation/
    ├── test_module_sizes.py (❌ planned)
    ├── test_architecture.py (❌ planned)
    ├── test_documentation.py (❌ planned)
    ├── test_test_isolation.py (❌ planned)
    ├── test_test_speed.py (❌ planned)
    └── test_linting.py (❌ planned)
```

---

## Traceability Summary

- **FRs mapped to tests:** 11/11 (100% planned)
- **NFRs mapped to tests:** 16/16 (100% planned)
- **Tests existing:** ~15 test functions (~700 lines in 2 files)
- **Tests planned:** ~50 test functions
- **Total test coverage planned:** ~65 test functions

**Critical Gaps:**
1. **FR-007 (Phase Shift Detection):** ZERO tests - this is the current production bug
2. **FR-008 (Sequential Phase Validation):** ZERO tests - prevents task misassignment
3. **NFR-R1 (Zero Regressions):** No comprehensive regression suite for all completed specs

**Existing Coverage:**
- FR-006 (Defensive Parsing): ✅ Good coverage (~10 tests)
- FR-010 (Task ID Normalization): ✅ Basic coverage (1 test)
- NFR-R2 (Error Handling): ✅ Basic coverage (1 test)
- FR-001 (Architecture): ✅ Basic structure tests (3 tests)
- FR-003 (Backward Compat): ✅ Partial (old imports work)

**Priority 1 Tests Needed:**
1. FR-007: Phase shift detection (3 tests) - Would have caught current bug
2. FR-008: Sequential validation (3 tests) - Prevents task misassignment
3. NFR-R1: Regression suite (1 comprehensive test) - 100% specs must parse identically

