# Non-Functional Tests Plan

**Project:** Project Orientation System  
**Date:** 2025-11-19  
**Purpose:** Verification tests for performance, reliability, security, and quality requirements

**NFR Categories:**
- **Performance:** Latency, throughput, resource usage
- **Reliability:** Fault tolerance, graceful degradation, error recovery
- **Security:** Input validation, no code execution, attack prevention
- **Maintainability:** Code quality, test coverage, documentation
- **Usability:** Error messages, tooling requirements, documentation clarity
- **Compatibility:** Backward/forward compatibility, schema consistency

---

## Performance Tests (NFR-P1, NFR-P2)

### NFR-P1: Orientation Execution Time

**Requirement:** Project orientation discovery and execution < 1 minute for 5-10 queries

**Metric Targets:**
- Total execution time: < 60,000ms for 10 queries
- Inline metadata parsing: < 100ms per markdown file
- mcp.yaml parsing: < 50ms per configuration load

#### Test 1: Orientation Execution Under 60 Seconds
- **Test:** `test_orientation_execution_under_60_seconds()`
- **File:** `tests/performance/test_orientation_performance.py`
- **Setup:** 10 project orientation queries configured
- **Measurement:** 
  ```python
  start = time.time()
  result = executor.execute_orientation(queries)
  elapsed_ms = (time.time() - start) * 1000
  ```
- **Pass Criteria:** `elapsed_ms < 60000`
- **Expected:** ~30-40s for 10 queries (p50), <60s worst case (p95)

#### Test 2: Metadata Parsing Performance
- **Test:** `test_metadata_parsing_under_100ms_per_file()`
- **File:** `tests/performance/test_orientation_performance.py`
- **Setup:** 100 markdown files with inline metadata
- **Measurement:**
  ```python
  times = []
  for file in markdown_files:
      start = time.time()
      parser.extract_inline_metadata(file.read_text(), file)
      times.append((time.time() - start) * 1000)
  p95 = np.percentile(times, 95)
  ```
- **Pass Criteria:** `p95 < 100` (95th percentile under 100ms)
- **Expected:** ~10-20ms per file (median), <100ms worst case

#### Test 3: mcp.yaml Parsing Performance
- **Test:** `test_mcp_yaml_parsing_under_50ms()`
- **File:** `tests/performance/test_orientation_performance.py`
- **Setup:** mcp.yaml with project.orientation section (10 queries)
- **Measurement:**
  ```python
  start = time.time()
  config = UnifiedConfig.from_yaml(yaml_path)
  elapsed_ms = (time.time() - start) * 1000
  ```
- **Pass Criteria:** `elapsed_ms < 50`
- **Expected:** ~10-20ms typical, <50ms worst case

---

### NFR-P2: Indexing Performance

**Requirement:** Metadata extraction shall not degrade standards index build time by more than 5%

**Metric Targets:**
- Index build time degradation: < 5%
- No retry loops on parsing errors

#### Test 4: Indexing Performance Degradation
- **Test:** `test_metadata_extraction_overhead_under_5_percent()`
- **File:** `tests/performance/test_orientation_performance.py`
- **Setup:** 1000 standards files (baseline vs with metadata extraction)
- **Measurement:**
  ```python
  # Baseline: index without metadata extraction
  baseline_time = measure_index_build(extract_metadata=False)
  
  # With metadata: index with extraction
  with_metadata_time = measure_index_build(extract_metadata=True)
  
  degradation_pct = ((with_metadata_time - baseline_time) / baseline_time) * 100
  ```
- **Pass Criteria:** `degradation_pct < 5.0`
- **Expected:** 1-3% degradation typical, <5% worst case

#### Test 5: No Retry Loops on Parsing Errors
- **Test:** `test_parsing_errors_no_retry_loops()`
- **File:** `tests/performance/test_orientation_performance.py`
- **Setup:** 10 files with malformed metadata, measure parse attempts
- **Measurement:**
  ```python
  with mock.patch('parser._extract_inline_metadata') as mock_extract:
      index_files(malformed_files)
      # Verify single attempt per file (no retries)
      assert mock_extract.call_count == len(malformed_files)
  ```
- **Pass Criteria:** Each file parsed exactly once (no retry loops)
- **Expected:** Single pass, graceful skip on errors

---

## Reliability Tests (NFR-R1, NFR-R2)

### NFR-R1: Graceful Degradation

**Requirement:** 100% graceful degradation on malformed metadata

**Metric Targets:**
- Graceful degradation: 100% (no exceptions raised)
- Indexing failures: 0
- Orientation execution failures: 0

#### Test 6: 100% Graceful Degradation
- **Test:** `test_100_percent_graceful_degradation_all_error_types()`
- **File:** `tests/ouroboros/subsystems/rag/standards/test_orientation.py`
- **Setup:** 20 markdown files with various error scenarios:
  - Missing metadata (5 files)
  - Malformed pairs (5 files)
  - Typo in marker (5 files)
  - Bad type coercion (5 files)
- **Measurement:**
  ```python
  exceptions_raised = 0
  for file in error_files:
      try:
          parser.extract_inline_metadata(file.read_text(), file)
      except Exception:
          exceptions_raised += 1
  graceful_pct = ((20 - exceptions_raised) / 20) * 100
  ```
- **Pass Criteria:** `graceful_pct == 100.0` (zero exceptions)
- **Expected:** All files parse successfully, warnings logged

#### Test 7: Zero Indexing Failures
- **Test:** `test_zero_indexing_failures_on_metadata_errors()`
- **File:** `tests/ouroboros/subsystems/rag/standards/test_orientation.py`
- **Setup:** Index 100 files (80 valid, 20 malformed metadata)
- **Measurement:**
  ```python
  result = index_manager.build_standards_index()
  assert result.files_indexed == 100
  assert result.indexing_failures == 0
  ```
- **Pass Criteria:** `indexing_failures == 0`
- **Expected:** All files indexed, malformed metadata skipped gracefully

#### Test 8: Zero Orientation Execution Failures
- **Test:** `test_zero_orientation_execution_failures()`
- **File:** `tests/integration/test_orientation_workflow.py`
- **Setup:** Project with mix of valid and malformed orientation metadata
- **Measurement:**
  ```python
  result = execute_full_orientation()
  assert result.execution_failures == 0
  assert result.queries_executed >= 0  # Partial ok, but no failures
  ```
- **Pass Criteria:** `execution_failures == 0`
- **Expected:** Execution completes, invalid queries skipped

---

### NFR-R2: Error Resilience

**Requirement:** Resilient behavior for missing, malformed, and incorrect metadata

**Metric Targets:**
- Missing metadata → defaults returned
- Malformed pairs → valid pairs parsed
- Typos → warnings logged, defaults returned
- Bad coercion → field skipped, remaining parsed

#### Test 9: Error Resilience Matrix
- **Test:** `test_error_resilience_all_scenarios()`
- **File:** `tests/ouroboros/subsystems/rag/standards/test_orientation.py`
- **Setup:** Test matrix with all error scenarios
- **Measurement:**
  ```python
  scenarios = [
      ("missing", "", {"domain": "default"}),  # Expected: defaults
      ("malformed", "a=1, bad, c=3", {"a": "1", "c": "3"}),  # Expected: skip bad
      ("typo", "**Metdata**: a=1", {"domain": "default"}),  # Expected: defaults
      ("bad_coercion", "a=notabool, b=1", {"b": 1}),  # Expected: skip a
  ]
  
  for name, input, expected in scenarios:
      result = parser.extract_inline_metadata(input, path)
      assert result == expected, f"Scenario {name} failed"
  ```
- **Pass Criteria:** All 4 scenarios pass with expected behavior
- **Expected:** 100% resilient behavior across all error types

---

## Security Tests (NFR-S1, NFR-S2)

### NFR-S1: No Code Execution

**Requirement:** No eval(), exec(), or dynamic code execution from metadata

**Metric Targets:**
- Code execution attempts: 0
- All metadata values treated as data

#### Test 10: Malicious Metadata No Code Execution
- **Test:** `test_malicious_metadata_no_eval_no_exec()`
- **File:** `tests/security/test_orientation_security.py`
- **Setup:** Malicious metadata strings:
  ```python
  malicious_inputs = [
      "eval=__import__('os').system('ls')",
      "exec=print('pwned')",
      "cmd=$(whoami)",
      "injection='; DROP TABLE users; --",
  ]
  ```
- **Measurement:**
  ```python
  for malicious in malicious_inputs:
      content = f"**Metadata**: {malicious}"
      result = parser.extract_inline_metadata(content, path)
      # Verify parsed as string, not executed
      assert isinstance(result.get("eval"), str)
      assert isinstance(result.get("exec"), str)
  ```
- **Pass Criteria:** All malicious inputs parsed as strings, never executed
- **Expected:** No side effects (no files created, no commands run)

#### Test 11: Metadata Values as Data Not Code
- **Test:** `test_metadata_values_treated_as_data_not_code()`
- **File:** `tests/security/test_orientation_security.py`
- **Setup:** Potentially dangerous strings in metadata
- **Measurement:**
  ```python
  # Verify no eval() or exec() in parser code
  parser_source = inspect.getsource(OrientationMetadataParser)
  assert "eval(" not in parser_source
  assert "exec(" not in parser_source
  ```
- **Pass Criteria:** Parser source contains no eval/exec calls
- **Expected:** Only regex-based parsing, no code execution paths

---

### NFR-S2: Input Validation

**Requirement:** All metadata fields validated, query strings sanitized, dependency graphs validated

**Metric Targets:**
- Type validation: 100% (all fields validated)
- Circular dependencies: detected and rejected
- Injection attempts: sanitized/rejected

#### Test 12: Metadata Fields Type Validation
- **Test:** `test_metadata_fields_type_validation_comprehensive()`
- **File:** `tests/security/test_orientation_security.py`
- **Setup:** Test invalid types for each field
- **Measurement:**
  ```python
  invalid_inputs = [
      {"priority": "high"},  # Should be int
      {"orientation": "yes"},  # Should be bool
      {"depends_on": "query1"},  # Should be list
  ]
  
  for invalid in invalid_inputs:
      with pytest.raises(ValidationError):
          OrientationQuery(**invalid)
  ```
- **Pass Criteria:** All invalid types raise ValidationError
- **Expected:** 100% type validation via Pydantic

#### Test 13: Query Strings Sanitized
- **Test:** `test_query_strings_sanitized_no_injection()`
- **File:** `tests/security/test_orientation_security.py`
- **Setup:** Query strings with shell metacharacters
- **Measurement:**
  ```python
  dangerous_queries = [
      "test; rm -rf /",
      "test && echo pwned",
      "test | cat /etc/passwd",
  ]
  
  for query_str in dangerous_queries:
      # Verify query validation rejects dangerous strings
      with pytest.raises(ValidationError):
          OrientationQuery(query=query_str)
  ```
- **Pass Criteria:** Shell metacharacters rejected by validation
- **Expected:** Only alphanumeric + safe chars allowed in queries

#### Test 14: Dependency Graph Prevents Loops
- **Test:** `test_dependency_graph_circular_dependency_detection()`
- **File:** `tests/security/test_orientation_security.py`
- **Setup:** Circular dependency scenarios
- **Measurement:**
  ```python
  # Scenario 1: A → B → A
  queries = [
      OrientationQuery(query="A", depends_on=["B"]),
      OrientationQuery(query="B", depends_on=["A"]),
  ]
  
  with pytest.raises(ValueError, match="Circular dependency"):
      handler._resolve_dependencies(queries)
  ```
- **Pass Criteria:** Circular dependencies detected and raise ValueError
- **Expected:** All circular dependency patterns detected

---

## Maintainability Tests (NFR-M1, NFR-M2, NFR-M3)

### NFR-M1: Code Reuse

**Requirement:** Reuse existing parsing logic and Pydantic infrastructure

**Metric Targets:**
- Shared methods: ≥1 (e.g., _extract_inline_metadata)
- Pydantic models: reuse existing patterns

#### Test 15: Shared Metadata Parsing Method
- **Test:** `test_shared_metadata_parsing_method_reuse()`
- **File:** Code review + integration test
- **Measurement:**
  ```python
  # Verify OrientationMetadataParser uses same method as StandardsIndex
  from ouroboros.subsystems.rag.standards.semantic import StandardsIndex
  from ouroboros.subsystems.rag.standards.orientation import OrientationMetadataParser
  
  # Check if method signatures match or method is shared
  standards_method = StandardsIndex._extract_inline_metadata
  orientation_method = OrientationMetadataParser._extract_inline_metadata
  
  # Verify same implementation or shared import
  assert standards_method.__code__.co_code == orientation_method.__code__.co_code
  ```
- **Pass Criteria:** Shared implementation verified
- **Expected:** Code reuse confirmed

---

### NFR-M2: Test Coverage

**Requirement:** Minimum 90% code coverage for metadata parsing and orientation execution

**Metric Target:** ≥ 90% coverage

#### Test 16: Code Coverage Target
- **Test:** `pytest --cov=ouroboros.subsystems.rag.standards.orientation --cov-report=term-missing`
- **File:** All test files
- **Measurement:**
  ```bash
  pytest --cov=ouroboros.subsystems.rag.standards.orientation \
         --cov=ouroboros.subsystems.config.models \
         --cov-report=term-missing \
         --cov-fail-under=90
  ```
- **Pass Criteria:** Coverage ≥ 90%
- **Expected:** 92-95% coverage with comprehensive test suite

#### Test 17: Comprehensive Test Scenarios
- **Test:** Review test suite completeness
- **Measurement:**
  - Valid metadata: ✅
  - Missing metadata: ✅
  - Malformed metadata: ✅
  - Typos: ✅
  - Bad types: ✅
  - Edge cases: ✅
- **Pass Criteria:** All scenarios covered
- **Expected:** Complete scenario coverage

---

### NFR-M3: Code Quality

**Requirement:** Docstrings, type hints, zero linting errors

**Metric Targets:**
- Flake8 errors: 0
- Mypy errors: 0
- Docstring coverage: 100% for public methods

#### Test 18: Linting Passes
- **Test:** `test_all_linting_passes_flake8_mypy()`
- **File:** `tests/ouroboros/subsystems/rag/standards/test_orientation.py`
- **Measurement:**
  ```bash
  # Flake8
  flake8 ouroboros/subsystems/rag/standards/orientation.py
  exit_code_flake8=$?
  
  # Mypy
  mypy ouroboros/subsystems/rag/standards/orientation.py
  exit_code_mypy=$?
  
  assert exit_code_flake8 == 0
  assert exit_code_mypy == 0
  ```
- **Pass Criteria:** Both tools exit with code 0
- **Expected:** Zero linting errors

#### Test 19: Docstring and Type Hint Coverage
- **Test:** Manual code review + automated check
- **Measurement:**
  ```python
  import inspect
  
  for name, obj in inspect.getmembers(OrientationMetadataParser):
      if callable(obj) and not name.startswith('_'):
          # Check docstring
          assert obj.__doc__ is not None, f"{name} missing docstring"
          
          # Check type hints
          sig = inspect.signature(obj)
          for param in sig.parameters.values():
              assert param.annotation != inspect.Parameter.empty
  ```
- **Pass Criteria:** 100% public methods have docstrings and type hints
- **Expected:** Complete documentation

---

## Usability Tests (NFR-U1, NFR-U2, NFR-U3)

### NFR-U1: Zero Tooling Requirements

**Requirement:** No additional tooling in consumer projects

**Metric Target:** 0 external dependencies

#### Test 20: No Additional Tooling Required
- **Test:** `test_no_additional_tooling_required_in_consumer_projects()`
- **File:** `tests/integration/test_orientation_workflow.py`
- **Measurement:**
  - Create fresh consumer project
  - Add orientation metadata
  - Execute orientation
  - Verify works without: pre-commit hooks, build steps, external validators
- **Pass Criteria:** Orientation works with markdown + mcp.yaml only
- **Expected:** Zero external tooling needed

---

### NFR-U2: Error Messages

**Requirement:** Actionable error/warning messages

**Metric Target:** 100% messages include file path and fix guidance

#### Test 21: Actionable Error Messages
- **Test:** `test_error_messages_actionable_with_file_path()`
- **File:** `tests/ouroboros/subsystems/rag/standards/test_orientation.py`
- **Measurement:**
  ```python
  with caplog.at_level(logging.WARNING):
      parser.extract_inline_metadata(malformed_content, Path("test/file.md"))
      
      # Verify warning includes:
      assert "test/file.md" in caplog.text  # File path
      assert "Failed to parse" in caplog.text  # What failed
      assert "metadata value" in caplog.text  # What to fix
  ```
- **Pass Criteria:** All warnings include path + description + fix guidance
- **Expected:** Actionable messages for all error scenarios

---

### NFR-U3: Documentation Clarity

**Requirement:** Documentation clear enough for project maintainers without framework expertise

**Metric Target:** Examples validate successfully, clear instructions

#### Test 22: Documentation Examples Valid
- **Test:** `test_documentation_examples_all_valid()`
- **File:** `tests/integration/test_orientation_workflow.py`
- **Measurement:**
  ```python
  # Extract code examples from documentation
  doc_path = Path("standards/universal/workflows/project-orientation-guide.md")
  examples = extract_code_blocks(doc_path)
  
  # Validate each example
  for example in examples:
      if example.language == "yaml":
          config = UnifiedConfig.from_yaml_string(example.code)
          assert config is not None
      elif example.language == "markdown":
          metadata = parser.extract_inline_metadata(example.code, path)
          assert metadata is not None
  ```
- **Pass Criteria:** All documentation examples parse/validate successfully
- **Expected:** 100% valid examples

---

## Compatibility Tests (NFR-C1, NFR-C2)

### NFR-C1: Configuration Schema Compatibility

**Requirement:** Backward and forward compatible mcp.yaml extensions

**Metric Targets:**
- Backward compatible: projects without orientation work unchanged
- Forward compatible: new fields don't break existing configs

#### Test 23: Backward Compatibility
- **Test:** `test_backward_compatible_no_orientation_metadata()`
- **File:** `tests/ouroboros/subsystems/config/test_orientation_models.py`
- **Measurement:**
  ```python
  # mcp.yaml without project.orientation section
  config_without = UnifiedConfig.from_yaml("mcp_no_orientation.yaml")
  assert config_without.project is None  # Optional field
  
  # Verify system works without orientation
  result = execute_base_orientation()
  assert result.success is True
  ```
- **Pass Criteria:** System works without project.orientation
- **Expected:** Graceful handling of missing section

#### Test 24: Forward Compatibility
- **Test:** `test_forward_compatible_new_metadata_fields()`
- **File:** `tests/ouroboros/subsystems/config/test_orientation_models.py`
- **Measurement:**
  ```python
  # Add new optional field to OrientationQuery
  query_with_new_field = {
      "query": "test",
      "priority": 1,
      "new_field": "value"  # Future field
  }
  
  # Verify Pydantic allows extra fields (configured)
  query = OrientationQuery(**query_with_new_field)
  assert query.query == "test"
  # new_field ignored gracefully
  ```
- **Pass Criteria:** New fields don't break parsing
- **Expected:** Extra fields allowed, forward compatible

---

### NFR-C2: Standards Index Compatibility

**Requirement:** Orientation parsing compatible with existing standards index

**Metric Target:** No breaking changes to markdown format

#### Test 25: Standards Index Compatibility
- **Test:** `test_orientation_parsing_compatible_with_standards_index()`
- **File:** `tests/integration/test_orientation_workflow.py`
- **Measurement:**
  ```python
  # Same markdown file parsed by both systems
  test_markdown = Path("test_standard.md")
  
  # Parse with standards index
  standards_result = standards_index.parse_file(test_markdown)
  
  # Parse with orientation parser
  orientation_result = orientation_parser.extract_inline_metadata(
      test_markdown.read_text(), test_markdown
  )
  
  # Verify compatible results
  assert standards_result.metadata == orientation_result
  ```
- **Pass Criteria:** Both parsers return same metadata
- **Expected:** 100% compatibility

---

## Test Execution Guidelines

### Performance Tests
**Environment:**
- Clean state (no cached data)
- Isolated environment (no other processes)
- Multiple runs (5-10) for statistical validity
- Report p50, p95, p99 percentiles

**Tools:**
- Python `time` module for timing
- `pytest-benchmark` for statistical analysis
- `memory_profiler` for memory usage

### Reliability Tests
**Environment:**
- Fault injection capable
- Recovery time measurement
- Error scenario simulation

**Tools:**
- `pytest` with exception handling
- Mocking for fault injection
- Logging verification

### Security Tests
**Environment:**
- Isolated test environment (VM/container)
- No production data
- Attack simulation tools

**Tools:**
- `bandit` for static security analysis
- Custom malicious input generation
- Code inspection for eval/exec

### Code Quality Tests
**Environment:**
- Clean codebase
- All dependencies installed

**Tools:**
- `flake8` for style
- `mypy` for type checking
- `pytest-cov` for coverage
- `interrogate` for docstring coverage

---

## Test Summary

**Total Non-Functional Test Cases:** 25

### By Category:
- **Performance:** 5 tests (NFR-P1, NFR-P2)
- **Reliability:** 4 tests (NFR-R1, NFR-R2)
- **Security:** 5 tests (NFR-S1, NFR-S2)
- **Maintainability:** 5 tests (NFR-M1, NFR-M2, NFR-M3)
- **Usability:** 3 tests (NFR-U1, NFR-U2, NFR-U3)
- **Compatibility:** 3 tests (NFR-C1, NFR-C2)

### Measurement Methods:
- **Automated:** 22 tests (88%)
- **Manual/Code Review:** 3 tests (12%)

**Coverage:** All 14 NFRs have corresponding verification tests with objective, measurable criteria.

---


