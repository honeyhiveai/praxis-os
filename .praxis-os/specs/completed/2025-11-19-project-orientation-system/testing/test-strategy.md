# Testing Strategy

**Project:** Project Orientation System  
**Date:** 2025-11-19  
**Purpose:** Define testing approach, patterns, and coverage targets

---

## Testing Philosophy

**Core Principles:**
1. **Test-Driven Development** - Write tests before implementation for critical paths
2. **Fast, Isolated Unit Tests** - Tests run in milliseconds, no external dependencies
3. **Integration Tests for Workflows** - Verify component interactions end-to-end
4. **Error Path Testing** - Test failures as thoroughly as success paths
5. **Performance Testing** - Verify NFR targets with measurable benchmarks

**Coverage Target:** ≥ 90% line coverage for all components

**Test Pyramid:**
- **Unit Tests (65%):** Fast, isolated, component logic
- **Integration Tests (25%):** Component interactions, workflows
- **Performance/Security Tests (10%):** NFR verification

---

## Unit Testing Strategy

### Scope
**Test:** Business logic, data transformations, validation, parsing, utilities

**Components Under Test:**
- `OrientationMetadataParser` - Inline metadata extraction and type coercion
- `OrientationQuery` / `ProjectOrientation` / `ProjectConfig` - Pydantic model validation
- `OrientationDiscoveryHandler` - Query discovery and merging
- `ProjectOrientationExecutor` - Query execution and timeout logic
- Helper methods: `_resolve_dependencies()`, `_merge_sources()`, `_coerce_type()`

### Coverage Target
**Minimum:** 90% line coverage  
**Goal:** 95%+ line coverage with comprehensive edge case testing

### Test Structure (AAA Pattern)
```python
def test_feature_scenario():
    # Arrange: Setup test data
    parser = OrientationMetadataParser()
    content = "**Metadata**: orientation=true, priority=1"
    path = Path("test.md")
    
    # Act: Execute function under test
    result = parser.extract_inline_metadata(content, path)
    
    # Assert: Verify expected outcome
    assert result["orientation"] is True
    assert result["priority"] == 1
```

### Test Organization
```
tests/
├── ouroboros/
│   ├── subsystems/
│   │   ├── rag/
│   │   │   └── standards/
│   │   │       └── test_orientation.py      # Parsing, discovery, execution
│   │   └── config/
│   │       └── test_orientation_models.py   # Pydantic models
```

### Isolation Strategy
**Mock External Dependencies:**
- `pos_search_project` tool calls → Mock with `unittest.mock.patch`
- Standards index queries → Mock return values
- File system I/O → Use in-memory strings or temp files
- Time-dependent functions → Mock `time.time()` for timeout tests

**Don't Mock:**
- Units under test (OrientationMetadataParser, models, etc.)
- Simple data structures (Dict, List)
- Standard library functions (str.split, re.search)
- Pydantic validation (test actual validation logic)

### Test Patterns

#### Pattern 1: Parameterized Tests for Multiple Scenarios
```python
@pytest.mark.parametrize("input,expected", [
    ("true", True),
    ("TRUE", True),
    ("false", False),
    ("123", 123),
    ("text", "text"),
])
def test_type_coercion_all_types(input, expected):
    result = parser._coerce_type(input)
    assert result == expected
```

#### Pattern 2: Exception Testing
```python
def test_circular_dependency_raises_value_error():
    queries = [
        OrientationQuery(query="A", depends_on=["B"]),
        OrientationQuery(query="B", depends_on=["A"]),
    ]
    
    with pytest.raises(ValueError, match="Circular dependency"):
        handler._resolve_dependencies(queries)
```

#### Pattern 3: Log Verification
```python
def test_malformed_metadata_logs_warning(caplog):
    with caplog.at_level(logging.WARNING):
        parser.extract_inline_metadata("**Metadata**: bad=", path)
        
        assert "Failed to parse" in caplog.text
        assert str(path) in caplog.text
```

---

## Integration Testing Strategy

### Scope
**Test:** Component interactions, workflows, end-to-end scenarios

**Integration Scenarios:**
- Base orientation (Query 10) → Project discovery → Query execution
- Inline metadata + mcp.yaml → Merged query list
- OrientationDiscoveryHandler + OrientationMetadataParser + ProjectOrientationExecutor → Full workflow
- Error scenarios → Graceful degradation end-to-end

### Coverage Target
**All critical paths tested**  
**All user stories verified**

### Test Organization
```
tests/
├── integration/
│   └── test_orientation_workflow.py   # End-to-end orientation workflows
```

### Integration Test Structure
```python
def test_full_orientation_workflow_base_plus_project():
    """
    Integration test: Base orientation → project discovery → execution.
    Verifies FR-003, FR-007.
    """
    # Arrange: Setup project with orientation metadata
    project = create_test_project_with_orientation()
    
    # Act: Execute complete orientation
    base_results = execute_base_orientation(queries_1_to_9)
    query_10_result = execute_query_10()  # Triggers discovery
    project_queries = discover_project_orientation()
    project_results = execute_project_orientation(project_queries)
    
    # Assert: Verify complete workflow
    assert len(base_results) == 9
    assert len(project_queries) >= 1
    assert len(project_results) == len(project_queries)
    assert query_10_result.contains("project orientation")
```

### Integration Test Patterns

#### Pattern 1: Workflow Verification
```python
def test_priority_order_execution_end_to_end():
    """Verify queries execute in priority order through full stack."""
    queries = [
        OrientationQuery(query="Q3", priority=3),
        OrientationQuery(query="Q1", priority=1),
        OrientationQuery(query="Q2", priority=2),
    ]
    
    execution_order = []
    
    def track_execution(query):
        execution_order.append(query)
        return {"results": []}
    
    with mock.patch('executor._execute_query', side_effect=track_execution):
        executor.execute_orientation(queries)
    
    assert execution_order == ["Q1", "Q2", "Q3"]
```

#### Pattern 2: Error Resilience Verification
```python
def test_malformed_metadata_graceful_end_to_end():
    """Verify malformed metadata doesn't break indexing or execution."""
    # Create project with mix of valid and malformed files
    project = create_project([
        ("valid1.md", "**Metadata**: orientation=true, priority=1"),
        ("malformed.md", "**Metadata**: bad syntax here"),
        ("valid2.md", "**Metadata**: orientation=true, priority=2"),
    ])
    
    # Index all files
    index_result = index_manager.build_standards_index()
    assert index_result.indexing_failures == 0  # All files indexed
    
    # Execute orientation
    orientation_result = execute_full_orientation()
    assert orientation_result.success is True  # Execution succeeds
    assert len(orientation_result.queries) == 2  # Only valid queries
```

---

## Mocking Strategy

### When to Mock

**Mock These:**
1. **External API Calls**
   ```python
   with mock.patch('ouroboros.tools.pos_search_project.search_standards') as mock_search:
       mock_search.return_value = {"results": [...]}
       executor.execute_orientation(queries)
   ```

2. **Standards Index Queries**
   ```python
   with mock.patch.object(standards_index, 'search') as mock_search:
       mock_search.return_value = mock_results
       handler.discover_orientation_queries()
   ```

3. **File System I/O (in unit tests)**
   ```python
   # Use in-memory content instead of real files
   content = "**Metadata**: orientation=true"
   result = parser.extract_inline_metadata(content, Path("test.md"))
   ```

4. **Time-Dependent Functions**
   ```python
   with mock.patch('time.time') as mock_time:
       mock_time.side_effect = [0, 30, 61]  # Simulate timeout
       result = executor.execute_orientation(queries, timeout_ms=60000)
       assert result.timeout_occurred is True
   ```

### When NOT to Mock

**Don't Mock These:**
1. **Units Under Test** - Test actual implementation, not mocks
2. **Pydantic Models** - Test real validation logic
3. **Standard Library** - `str.split()`, `re.search()`, etc.
4. **Integration Test Components** - Test real interactions

### Mocking Tools

**Preferred:** `unittest.mock` (standard library)
```python
from unittest.mock import Mock, patch, MagicMock

# Patch function
with patch('module.function') as mock_func:
    mock_func.return_value = expected_value
    
# Patch method
with patch.object(obj, 'method') as mock_method:
    mock_method.side_effect = [result1, result2]
```

**Fixtures:** `pytest` fixtures for reusable test data
```python
@pytest.fixture
def sample_orientation_queries():
    return [
        OrientationQuery(query="architecture", priority=1),
        OrientationQuery(query="patterns", priority=2),
    ]

def test_something(sample_orientation_queries):
    result = executor.execute_orientation(sample_orientation_queries)
    assert result.success is True
```

---

## Performance and Security Testing Strategy

### Performance Tests
**Location:** `tests/performance/test_orientation_performance.py`

**Approach:**
- Clean environment (no cached data)
- Multiple runs (5-10) for statistical validity
- Report p50, p95, p99 percentiles
- Use `pytest-benchmark` for consistent measurement

**Example:**
```python
def test_orientation_execution_timing(benchmark):
    queries = create_test_queries(count=10)
    
    def execute():
        return executor.execute_orientation(queries)
    
    result = benchmark(execute)
    
    # pytest-benchmark reports timing stats automatically
    assert result.total_time_ms < 60000  # NFR-P1
```

### Security Tests
**Location:** `tests/security/test_orientation_security.py`

**Approach:**
- Malicious input generation
- Code inspection (no eval/exec)
- Input validation verification
- Attack simulation

**Example:**
```python
def test_no_code_execution_from_malicious_metadata():
    malicious_inputs = [
        "eval=__import__('os').system('ls')",
        "exec=print('pwned')",
    ]
    
    for malicious in malicious_inputs:
        content = f"**Metadata**: {malicious}"
        result = parser.extract_inline_metadata(content, path)
        
        # Verify parsed as string, not executed
        assert isinstance(result.get("eval"), str)
        # Verify no side effects
        assert not os.path.exists("/tmp/pwned")
```

---

## Test Execution

### Local Development

**Run all tests:**
```bash
pytest tests/
```

**Run unit tests only:**
```bash
pytest tests/ouroboros/
```

**Run integration tests:**
```bash
pytest tests/integration/
```

**Run with coverage:**
```bash
pytest --cov=ouroboros.subsystems.rag.standards.orientation \
       --cov=ouroboros.subsystems.config.models \
       --cov-report=term-missing \
       --cov-report=html \
       --cov-fail-under=90
```

**Run performance tests:**
```bash
pytest tests/performance/ --benchmark-only
```

**Run security tests:**
```bash
pytest tests/security/
```

### Linting and Type Checking

**Flake8 (style):**
```bash
flake8 ouroboros/subsystems/rag/standards/orientation.py
flake8 ouroboros/subsystems/config/models.py
```

**Mypy (type hints):**
```bash
mypy ouroboros/subsystems/rag/standards/orientation.py
mypy ouroboros/subsystems/config/models.py
```

**Bandit (security):**
```bash
bandit -r ouroboros/subsystems/rag/standards/orientation.py
```

**Black (formatting):**
```bash
black --check ouroboros/subsystems/rag/standards/orientation.py
```

### CI/CD Integration

**Tests run on:**
- Every commit to feature branch
- Every pull request
- Before merge to main

**CI Pipeline:**
1. Install dependencies
2. Run linting (flake8, mypy, bandit, black)
3. Run unit tests with coverage
4. Run integration tests
5. Run performance tests (benchmarks)
6. Run security tests
7. Verify coverage ≥ 90%
8. Report results

**Failure Conditions:**
- Any test fails
- Coverage < 90%
- Linting errors present
- Security issues detected

---

## Test Data Management

### Test Fixtures

**Reusable test data:**
```python
@pytest.fixture
def sample_markdown_with_metadata():
    return """
    # Test Standard
    
    **Metadata**: orientation=true, priority=1, domain=test
    
    ## Content
    """

@pytest.fixture
def sample_mcp_yaml():
    return {
        "project": {
            "orientation": {
                "enabled": True,
                "queries": [
                    {"query": "test query", "priority": 1}
                ]
            }
        }
    }
```

### Temporary Files

**Use pytest tmpdir for file system tests:**
```python
def test_file_parsing(tmpdir):
    # Create temp file
    test_file = tmpdir / "test.md"
    test_file.write_text("**Metadata**: orientation=true")
    
    # Test parsing
    result = parser.extract_inline_metadata(test_file.read_text(), Path(test_file))
    assert result["orientation"] is True
    
    # Cleanup automatic
```

---

## Test Documentation

### Docstrings

**Every test should have a docstring:**
```python
def test_circular_dependency_detection():
    """
    Verify circular dependencies are detected and raise ValueError.
    
    Tests FR-005 acceptance criteria: "Dependency validation prevents
    circular dependencies."
    
    Scenario: Query A depends on B, Query B depends on A.
    Expected: ValueError raised with cycle description.
    """
    # Test implementation...
```

### Test Names

**Descriptive names following pattern:**
- `test_{component}_{scenario}_{expected_outcome}()`
- Example: `test_metadata_parser_malformed_input_partial_parse()`

---

## Coverage Targets by Component

| Component | Unit Coverage | Integration Coverage |
|-----------|---------------|----------------------|
| OrientationMetadataParser | ≥ 95% | - |
| Pydantic Models | ≥ 90% | - |
| OrientationDiscoveryHandler | ≥ 90% | ✅ Full workflow |
| ProjectOrientationExecutor | ≥ 90% | ✅ Full workflow |
| Base Orientation Integration | - | ✅ Query 10 workflow |
| Error Handling | ≥ 95% | ✅ End-to-end |

**Overall Target:** ≥ 90% line coverage across all components

---

## Test Maintenance

### When to Update Tests

1. **New Feature:** Add tests for new functionality
2. **Bug Fix:** Add regression test before fixing
3. **Refactoring:** Update tests if API changes
4. **NFR Change:** Update performance/security tests

### Test Review Checklist

- [ ] Tests are deterministic (no flakiness)
- [ ] Tests are fast (unit tests < 100ms each)
- [ ] Tests are isolated (no shared state)
- [ ] Tests have clear assertions
- [ ] Tests have descriptive docstrings
- [ ] Mocking is appropriate (not over-mocked)
- [ ] Coverage meets targets

---

## Summary

**Test Strategy Highlights:**
- **90% coverage target** for all components
- **Test pyramid:** 65% unit, 25% integration, 10% performance/security
- **TDD approach** for critical paths
- **Mock external dependencies**, test real logic
- **Comprehensive error path testing**
- **Performance benchmarking** for NFR verification
- **Security testing** for malicious input handling
- **CI/CD integration** with automated test runs

**Total Test Count (Estimated):** ~93 test functions
- Unit: ~60 tests
- Integration: ~20 tests
- Performance: ~5 tests
- Security: ~8 tests

---


