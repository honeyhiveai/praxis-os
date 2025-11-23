# Requirements Traceability Matrix

**Project:** Project Orientation System  
**Date:** 2025-11-19  
**Purpose:** Map every requirement to specific test files and functions

---

## Functional Requirements Traceability

| Requirement | Test File | Test Function(s) | Verification Method | Status |
|-------------|-----------|------------------|---------------------|--------|
| FR-001: Inline Metadata Discovery | `tests/ouroboros/subsystems/rag/standards/test_orientation.py` | - `test_extract_inline_metadata_valid()`<br>- `test_extract_inline_metadata_missing()`<br>- `test_regex_pattern_matches_metadata_line()` | Unit tests verify regex detection, field extraction, path defaults | Planned |
| FR-002: mcp.yaml Extension | `tests/ouroboros/subsystems/config/test_orientation_models.py` | - `test_orientation_query_model_validation()`<br>- `test_project_orientation_model()`<br>- `test_unified_config_project_extension()`<br>- `test_mcp_yaml_parsing_with_orientation()` | Unit tests verify Pydantic models, schema validation, multiple sources | Planned |
| FR-003: Automatic Execution | `tests/integration/test_orientation_workflow.py` | - `test_base_orientation_triggers_project_discovery()`<br>- `test_project_queries_executed_in_priority_order()`<br>- `test_orientation_completes_within_60s()` | Integration test verifies Query 10 triggers discovery, execution order, timing | Planned |
| FR-004: Error-Resistant Parsing | `tests/ouroboros/subsystems/rag/standards/test_orientation.py` | - `test_missing_metadata_returns_defaults()`<br>- `test_malformed_pairs_partial_parse()`<br>- `test_typo_in_marker_returns_defaults()`<br>- `test_bad_type_coercion_skip_field()`<br>- `test_no_indexing_failures_on_errors()` | Unit tests verify all error scenarios return gracefully, never crash | Planned |
| FR-005: Query Execution Order | `tests/ouroboros/subsystems/rag/standards/test_orientation.py` | - `test_priority_order_execution()`<br>- `test_same_priority_definition_order()`<br>- `test_depends_on_field_dependency_resolution()`<br>- `test_circular_dependency_detection()` | Unit tests verify sorting, dependency resolution, cycle detection | Planned |
| FR-006: Standards Pattern Compatibility | `tests/ouroboros/subsystems/rag/standards/test_orientation.py` | - `test_metadata_format_matches_standards()`<br>- `test_type_coercion_bool_int_string()`<br>- `test_error_handling_skip_log_continue()`<br>- `test_code_reuse_shared_method()` | Unit tests verify format consistency, type coercion, error handling, code reuse | Planned |
| FR-007: Base Orientation Integration | `tests/integration/test_orientation_workflow.py` | - `test_query_10_mentions_project_orientation()`<br>- `test_ai_queries_project_orientation()`<br>- `test_discovery_returns_metadata_and_queries()`<br>- `test_project_queries_after_base_complete()` | Integration test verifies Query 10 text, discovery, execution sequence | Planned |
| FR-008: Metadata Schema | `tests/ouroboros/subsystems/config/test_orientation_models.py` | - `test_required_fields_orientation_query()`<br>- `test_optional_fields_defaults()`<br>- `test_schema_validation_error_messages()`<br>- `test_documentation_examples_valid()` | Unit tests verify required/optional fields, validation errors, examples | Planned |
| FR-009: No Tooling Requirements | `tests/integration/test_orientation_workflow.py` | - `test_orientation_works_markdown_only()`<br>- `test_mcp_yaml_optional_not_required()`<br>- `test_no_precommit_hooks_needed()`<br>- `test_malformed_metadata_graceful_degradation()` | Integration test verifies no external tooling, pre-commit hooks, build steps | Planned |

**Functional Requirements Summary:**
- Total FRs: 9
- Test Files: 3
- Test Functions: 36+
- Coverage: 100% (all FRs mapped)

---

## Non-Functional Requirements Traceability

| Requirement | Test File | Test Function(s) | Metric/Target | Verification Method | Status |
|-------------|-----------|------------------|---------------|---------------------|--------|
| NFR-P1: Orientation Execution Time | `tests/performance/test_orientation_performance.py` | - `test_orientation_execution_under_60s()`<br>- `test_metadata_parsing_under_100ms_per_file()`<br>- `test_mcp_yaml_parsing_under_50ms()` | < 60s for 10 queries<br>< 100ms per file<br>< 50ms config | Performance test with timing assertions | Planned |
| NFR-P2: Indexing Performance | `tests/performance/test_orientation_performance.py` | - `test_metadata_extraction_overhead_under_5_percent()`<br>- `test_parsing_errors_no_retry_loops()` | < 5% degradation<br>No retry loops | Performance test comparing index build time with/without metadata | Planned |
| NFR-R1: Graceful Degradation | `tests/ouroboros/subsystems/rag/standards/test_orientation.py` | - `test_100_percent_graceful_degradation()`<br>- `test_zero_indexing_failures()`<br>- `test_zero_orientation_failures()` | 100% graceful<br>0 indexing failures<br>0 execution failures | Unit tests verify all error paths return successfully, never raise | Planned |
| NFR-R2: Error Resilience | `tests/ouroboros/subsystems/rag/standards/test_orientation.py` | - `test_missing_metadata_defaults()`<br>- `test_malformed_pairs_parse_valid()`<br>- `test_typo_log_warning_defaults()`<br>- `test_bad_coercion_skip_field()` | Defaults returned<br>Valid pairs parsed<br>Warnings logged<br>Fields skipped | Unit tests verify resilient behavior for each error type | Planned |
| NFR-U1: Zero Tooling Requirements | `tests/integration/test_orientation_workflow.py` | - `test_no_additional_tooling_required()`<br>- `test_no_precommit_hooks()`<br>- `test_no_build_step_required()`<br>- `test_markdown_and_yaml_only()` | No external deps<br>No hooks<br>No build<br>Files only | Integration test verifies system works with markdown + mcp.yaml only | Planned |
| NFR-U2: Error Messages | `tests/ouroboros/subsystems/rag/standards/test_orientation.py` | - `test_actionable_error_messages()`<br>- `test_log_includes_file_path_line_number()`<br>- `test_error_guides_user_to_fix()` | Actionable errors<br>Path + line<br>Fix guidance | Unit tests verify warning/error message content quality | Planned |
| NFR-U3: Documentation Clarity | Manual verification + integration test | - `test_example_configurations_valid()`<br>- Manual review: documentation completeness | Examples valid<br>Clear docs | Integration test validates examples, manual review for clarity | Planned |
| NFR-M1: Code Reuse | Code review + integration test | - `test_shared_metadata_parsing_method()`<br>- `test_pydantic_infrastructure_reuse()`<br>- Code review: verify reuse | Shared methods<br>Pydantic reuse | Code review verifies reuse, integration test validates functionality | Planned |
| NFR-M2: Test Coverage | `pytest --cov` | - All test files<br>- Coverage report analysis | ≥ 90% coverage<br>All scenarios | Coverage tool verifies percentage, test suite verifies scenarios | Planned |
| NFR-M3: Code Quality | `flake8`, `mypy`, code review | - `test_all_linting_passes()`<br>- Linting tools execution | 0 flake8 errors<br>0 mypy errors<br>Docstrings present | Linting tools verify code quality, code review validates docstrings | Planned |
| NFR-C1: Config Schema Compatibility | `tests/ouroboros/subsystems/config/test_orientation_models.py` | - `test_pydantic_v2_patterns()`<br>- `test_backward_compatible_no_orientation()`<br>- `test_forward_compatible_new_fields()` | Pydantic v2<br>Backward compat<br>Forward compat | Unit tests verify compatibility across versions | Planned |
| NFR-C2: Standards Index Compatibility | `tests/integration/test_orientation_workflow.py` | - `test_orientation_parsing_compatible_with_standards()`<br>- `test_no_breaking_changes_markdown_format()`<br>- `test_inline_pattern_matches_design()` | Compatible parsing<br>No breaking changes<br>Pattern match | Integration test verifies compatibility with existing standards index | Planned |
| NFR-S1: No Code Execution | `tests/security/test_orientation_security.py` | - `test_malicious_metadata_no_eval()`<br>- `test_metadata_values_as_data_not_code()`<br>- `test_no_command_injection_risk()` | No eval/exec<br>Data only<br>No injection | Security tests verify malicious inputs parsed as strings, never executed | Planned |
| NFR-S2: Input Validation | `tests/security/test_orientation_security.py` | - `test_metadata_fields_type_validation()`<br>- `test_query_strings_sanitized()`<br>- `test_dependency_graph_prevents_loops()` | Type validation<br>Sanitization<br>Loop prevention | Security tests verify validation for all input types | Planned |

**Non-Functional Requirements Summary:**
- Total NFRs: 14
- Test Files: 6
- Test Functions: 40+
- Coverage: 100% (all NFRs mapped)

---

## Test Organization

```
tests/
├── ouroboros/
│   ├── subsystems/
│   │   ├── rag/
│   │   │   └── standards/
│   │   │       └── test_orientation.py          # Core parsing and execution logic
│   │   └── config/
│   │       └── test_orientation_models.py        # Pydantic models and validation
│   └── tools/
│       └── test_pos_search_project.py            # Tool integration (if needed)
├── integration/
│   └── test_orientation_workflow.py              # End-to-end workflow tests
├── performance/
│   └── test_orientation_performance.py           # Performance and timing tests
└── security/
    └── test_orientation_security.py              # Security and input validation tests
```

### Test Counts by Type

- **Unit Tests:** ~60 test functions
  - Metadata parsing: ~25 functions
  - Pydantic models: ~15 functions
  - Error handling: ~15 functions
  - Code quality: ~5 functions

- **Integration Tests:** ~20 test functions
  - Base + project orientation workflow: ~8 functions
  - Configuration integration: ~6 functions
  - Compatibility tests: ~6 functions

- **Performance Tests:** ~5 test functions
  - Execution timing: ~3 functions
  - Indexing overhead: ~2 functions

- **Security Tests:** ~8 test functions
  - No code execution: ~4 functions
  - Input validation: ~4 functions

**Total Test Functions:** ~93

### Test Coverage by Requirement Type

- **Functional Requirements:** 36+ test functions (4 tests/FR average)
- **Non-Functional Requirements:** 40+ test functions (2.86 tests/NFR average)
- **Overlap:** Some tests verify multiple requirements simultaneously

### Coverage Verification

**100% Requirement Coverage:**
- All 9 FRs mapped to ≥1 test
- All 14 NFRs mapped to ≥1 test
- Total: 23/23 requirements (100%)

**Test Type Distribution:**
- Unit: ~65% (focused on component logic)
- Integration: ~22% (focused on workflows)
- Performance: ~5% (focused on timing)
- Security: ~8% (focused on malicious input)

---

## Traceability by Test File

### `test_orientation.py` (Unit Tests - Core)
**Requirements Covered:** FR-001, FR-004, FR-005, FR-006, NFR-R1, NFR-R2, NFR-U2  
**Focus:** Metadata parsing, error handling, type coercion, graceful degradation  
**Test Count:** ~25 functions

### `test_orientation_models.py` (Unit Tests - Config)
**Requirements Covered:** FR-002, FR-008, NFR-C1  
**Focus:** Pydantic models, schema validation, configuration extensions  
**Test Count:** ~15 functions

### `test_orientation_workflow.py` (Integration Tests)
**Requirements Covered:** FR-003, FR-007, FR-009, NFR-U1, NFR-C2  
**Focus:** End-to-end workflows, base + project integration, compatibility  
**Test Count:** ~20 functions

### `test_orientation_performance.py` (Performance Tests)
**Requirements Covered:** NFR-P1, NFR-P2  
**Focus:** Execution timing, parsing overhead, indexing performance  
**Test Count:** ~5 functions

### `test_orientation_security.py` (Security Tests)
**Requirements Covered:** NFR-S1, NFR-S2  
**Focus:** No code execution, input validation, malicious input handling  
**Test Count:** ~8 functions

### Code Quality & Coverage Verification
**Requirements Covered:** NFR-M1, NFR-M2, NFR-M3, NFR-U3  
**Verification:** Linting tools (flake8, mypy), coverage tools (pytest --cov), code review, documentation review  
**Test Count:** ~5 functions + manual verification

---

## Missing Test Coverage

**None** - All 23 requirements have corresponding test(s) mapped.

---

## Next Steps

1. ✅ Traceability matrix created with 100% requirement coverage
2. → Create detailed functional test plans (Task 5)
3. → Create detailed non-functional test plans (Task 6)
4. → Define unit and integration testing strategy (Task 7)

---


