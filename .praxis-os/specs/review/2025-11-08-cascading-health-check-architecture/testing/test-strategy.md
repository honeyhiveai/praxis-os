# Testing Strategy

**Project:** Cascading Health Check Architecture  
**Date:** 2025-11-10  
**Purpose:** Overall testing approach for component pattern implementation

---

## Testing Philosophy

1. **Test-Driven Development**: Write tests before/alongside implementation where possible
2. **Fast Isolation**: Unit tests run in < 1s total
3. **Integration Reality**: Integration tests use real database (DuckDB)
4. **Coverage Discipline**: Foundation ≥ 90%, Indexes ≥ 80%
5. **Quality Gates**: All tests must pass before commit (pre-commit hooks)

---

## Test Pyramid

```
        /\
       /E2E\          ← Few (5-10): Full cascade, multi-level scenarios
      /------\
     /Integr-\       ← Some (20-30): Component interactions, partial degradation
    /----------\
   /Unit Tests \     ← Many (40-50): ComponentDescriptor, dynamic_health_check, helpers
  /--------------\
```

**Distribution Target:**
- Unit: 60% of tests
- Integration: 35% of tests
- E2E: 5% of tests

---

## Unit Testing

### Scope

Test individual functions/methods in isolation:
- `ComponentDescriptor` validation
- `dynamic_health_check()` logic
- Individual component health check methods (`_check_ast_health`, `_check_graph_health`)
- Individual rebuild methods (`_rebuild_ast`, `_rebuild_graph`)
- Helper utilities

### Coverage Target

- **Foundation** (`component_helpers.py`): ≥ 90%
- **Index implementations**: ≥ 80%
- **Edge cases**: 100% (empty dicts, exceptions, invalid inputs)

### Test Structure (AAA Pattern)

```python
def test_component_descriptor_valid():
    # Arrange: Setup test data
    name = "ast"
    provides = ["ast_nodes"]
    capabilities = ["search_ast"]
    health_check = lambda: HealthStatus(healthy=True)
    rebuild = lambda: None
    
    # Act: Execute function under test
    descriptor = ComponentDescriptor(
        name=name,
        provides=provides,
        capabilities=capabilities,
        health_check=health_check,
        rebuild=rebuild,
    )
    
    # Assert: Verify result
    assert descriptor.name == "ast"
    assert descriptor.provides == ["ast_nodes"]
    assert descriptor.dependencies == []  # Default
```

### Isolation Strategy

**Mock external dependencies:**
- Database connections (use `unittest.mock.Mock()`)
- File system I/O
- Network calls (none in this feature)

**Don't mock:**
- Units under test (ComponentDescriptor, dynamic_health_check)
- Simple data structures (dicts, lists)
- HealthStatus responses

**Example: Mocking DB Connection**

```python
from unittest.mock import Mock, MagicMock

def test_check_ast_health_healthy():
    # Arrange
    mock_conn = Mock()
    mock_conn.execute.return_value.fetchone.return_value = [500]  # COUNT=500
    
    index = GraphIndex(config, base_path, languages)
    index.db_connection = Mock()
    index.db_connection.get_connection.return_value = mock_conn
    
    # Act
    health = index._check_ast_health()
    
    # Assert
    assert health.healthy == True
    assert health.details["count"] == 500
```

### Organization

```
ouroboros/tests/unit/
├── subsystems/
│   └── rag/
│       ├── utils/
│       │   └── test_component_helpers.py          # Foundation tests
│       └── indexes/
│           ├── test_graph_index_components.py     # GraphIndex unit tests
│           ├── test_code_index_components.py      # CodeIndex unit tests
│           ├── test_standards_index_components.py # StandardsIndex unit tests
│           └── test_index_manager_components.py   # IndexManager unit tests
```

---

## Integration Testing

### Scope

Test component interactions with real database:
- GraphIndex components (AST + graph) health checks
- CodeIndex aggregating sub-indexes
- IndexManager cascading health checks
- Targeted rebuild flows (AST broken → rebuild → verify)
- Partial degradation scenarios

### Coverage Target

- **Critical paths**: 100% (partial degradation, targeted rebuild)
- **Component interactions**: All combinations tested
- **Error scenarios**: Major error paths covered

### Test Structure

```python
def test_partial_degradation_ast_broken_graph_healthy():
    # Arrange: Real DuckDB database
    index = GraphIndex(config, test_db_path, languages)
    index.build()  # Initial build
    
    # Clear AST (inject fault)
    conn = index.db_connection.get_connection()
    conn.execute("DELETE FROM ast_nodes")
    
    # Act: Health check
    health = index.health_check()
    
    # Assert: Partial degradation
    assert health.healthy == False, "Overall unhealthy"
    assert health.details["components"]["ast"]["healthy"] == False
    assert health.details["components"]["graph"]["healthy"] == True
    
    # Verify operations
    results = index.find_callers("my_function")
    assert len(results) > 0, "Graph operations succeed"
```

### Database Strategy

**Use real DuckDB (not mocked):**
- Fast enough for integration tests (in-memory or tmpfile)
- Catch SQL syntax errors
- Test real query performance

**Setup/Teardown:**

```python
import pytest
import tempfile

@pytest.fixture
def test_db():
    """Create temporary DuckDB database for testing"""
    with tempfile.NamedTemporaryFile(suffix=".db") as f:
        yield f.name
    # Auto-cleanup

def test_graphindex_health(test_db):
    index = GraphIndex(config, test_db, languages)
    # Test with real DB
```

### Organization

```
ouroboros/tests/integration/
├── subsystems/
│   └── rag/
│       ├── test_graphindex_partial_degradation.py
│       ├── test_codeindex_aggregation.py
│       ├── test_indexmanager_cascade.py
│       └── test_targeted_rebuild.py
```

---

## End-to-End Testing

### Scope

Full system scenarios spanning multiple levels:
- IndexManager → CodeIndex → GraphIndex → components (4 levels)
- Server startup health check cascade
- Full rebuild vs targeted rebuild comparison
- Backward compatibility (mixed migrated/legacy indexes)

### Test Structure

```python
def test_e2e_server_startup_cascade():
    # Arrange: Full system with IndexManager
    manager = IndexManager(config, base_path)
    manager.build_all()
    
    # Act: Full cascade health check (like server startup)
    start = time.perf_counter()
    health = manager.health_check_all()
    duration = time.perf_counter() - start
    
    # Assert: Performance + correctness
    assert duration < 0.500, "Cascade < 500ms"
    assert all(status.healthy for status in health.values())
    
    # Verify drill-down
    code_health = health["code"]
    assert "components" in code_health.details
    assert "graph" in code_health.details["components"]
```

---

## Mocking Strategy

### When to Mock

**Mock external dependencies:**
1. **Database (unit tests only)**
   - Use `unittest.mock.Mock()` for db connections
   - Mock `execute()` and `fetchone()` return values
   
2. **File System I/O**
   - Mock file parsing if slow
   - Use `tempfile` for real files when needed

3. **Time-Dependent Functions**
   - Mock `time.perf_counter()` for deterministic timing tests

**Example: Mocking for Exception Testing**

```python
from unittest.mock import Mock, side_effect

def test_dynamic_health_check_component_exception():
    # Arrange: Component that raises exception
    mock_component = Mock()
    mock_component.health_check.side_effect = RuntimeError("DB failed")
    
    descriptor = ComponentDescriptor(
        name="broken",
        provides=["data"],
        capabilities=["op"],
        health_check=mock_component.health_check,
        rebuild=lambda: None,
    )
    
    components = {"broken": descriptor}
    
    # Act: Should not raise
    status = dynamic_health_check(components)
    
    # Assert
    assert status.components["broken"]["healthy"] == False
    assert "error" in status.components["broken"]["details"]
```

### When NOT to Mock

**Use real implementations:**
1. **Units Under Test**
   - ComponentDescriptor (real instantiation)
   - dynamic_health_check (real function)
   
2. **Simple Data Structures**
   - Dicts, lists (just create them)
   - HealthStatus (real dataclass)

3. **Integration Tests**
   - Real DuckDB database
   - Real file system (with cleanup)
   - Real sub-components

---

## Test Execution

### Commands

**Run All Tests:**
```bash
pytest ouroboros/tests/ -v
```

**Run Unit Tests Only:**
```bash
pytest ouroboros/tests/unit/ -v
```

**Run Integration Tests Only:**
```bash
pytest ouroboros/tests/integration/ -v
```

**Run with Coverage:**
```bash
pytest ouroboros/tests/ --cov=ouroboros/subsystems/rag --cov-report=term-missing
```

**Run Specific Test:**
```bash
pytest ouroboros/tests/unit/subsystems/rag/utils/test_component_helpers.py::test_component_descriptor_valid -v
```

**Run Failed Tests Only:**
```bash
pytest --lf  # Last failed
```

### Coverage Reporting

```bash
# Generate HTML coverage report
pytest ouroboros/tests/ --cov=ouroboros/subsystems/rag --cov-report=html

# Open report
open htmlcov/index.html
```

### CI/CD Integration

**Pre-Commit Hooks:**
- Runs: `pytest ouroboros/tests/ --cov-fail-under=80`
- Blocks commit if tests fail or coverage < 80%

**GitHub Actions (if applicable):**
```yaml
- name: Run tests
  run: |
    pytest ouroboros/tests/ -v --cov=ouroboros --cov-report=xml
    
- name: Upload coverage
  uses: codecov/codecov-action@v3
```

---

## Testing Patterns

### Pattern 1: Test Component Registration

```python
def test_graphindex_component_registration():
    """Verify components registered correctly"""
    index = GraphIndex(config, base_path, languages)
    
    # Verify registry structure
    assert hasattr(index, "components")
    assert isinstance(index.components, dict)
    assert "ast" in index.components
    assert "graph" in index.components
    
    # Verify component properties
    ast_comp = index.components["ast"]
    assert ast_comp.name == "ast"
    assert "ast_nodes" in ast_comp.provides
    assert "search_ast" in ast_comp.capabilities
```

### Pattern 2: Test Dynamic Health Check Aggregation

```python
def test_dynamic_health_check_aggregation():
    """Verify health aggregation logic"""
    # Create components with known health
    healthy = ComponentDescriptor(..., health_check=lambda: HealthStatus(healthy=True))
    unhealthy = ComponentDescriptor(..., health_check=lambda: HealthStatus(healthy=False))
    
    components = {
        "comp1": healthy,
        "comp2": unhealthy,
        "comp3": healthy,
    }
    
    # Test aggregation
    status = dynamic_health_check(components)
    
    # Assertions
    assert status.healthy == False, "Overall unhealthy if any component unhealthy"
    assert status.details["components"]["comp1"]["healthy"] == True
    assert status.details["components"]["comp2"]["healthy"] == False
    assert status.details["capabilities"]["comp1_op"] == True
    assert status.details["capabilities"]["comp2_op"] == False
```

### Pattern 3: Test Targeted Rebuild

```python
def test_targeted_rebuild_preserves_healthy():
    """Verify targeted rebuild preserves healthy component data"""
    index = GraphIndex(config, test_db_path, languages)
    index.build()
    
    # Capture baseline
    conn = index.db_connection.get_connection()
    symbols_before = list(conn.execute("SELECT * FROM symbols"))
    
    # Clear AST only
    conn.execute("DELETE FROM ast_nodes")
    
    # Rebuild AST
    index._rebuild_ast()
    
    # Verify preservation
    symbols_after = list(conn.execute("SELECT * FROM symbols"))
    assert symbols_before == symbols_after, "Graph data preserved"
    
    # Verify AST rebuilt
    ast_count = conn.execute("SELECT COUNT(*) FROM ast_nodes").fetchone()[0]
    assert ast_count > 0, "AST repopulated"
```

---

## Coverage Targets

### Per-Phase Targets

| Phase | Component | Target | Priority |
|-------|-----------|--------|----------|
| 0 | component_helpers.py | ≥ 90% | Critical |
| 1 | GraphIndex | ≥ 80% | Critical |
| 2 | CodeIndex | ≥ 80% | High |
| 3 | StandardsIndex | ≥ 80% | High |
| 4 | IndexManager | ≥ 80% | Critical |

### Minimum Coverage Gates

**Pre-Commit Hook:**
```bash
pytest --cov-fail-under=80
# Blocks commit if < 80%
```

**Phase Validation Gate:**
- Foundation (Phase 0): ≥ 90%
- Each index phase: ≥ 80%

---

## Test Data Management

### Test Fixtures

**Shared Fixtures** (`conftest.py`):

```python
import pytest

@pytest.fixture
def mock_component_descriptor():
    """Factory for creating test ComponentDescriptors"""
    def _create(name="test", healthy=True):
        return ComponentDescriptor(
            name=name,
            provides=["data"],
            capabilities=["op"],
            health_check=lambda: HealthStatus(healthy=healthy),
            rebuild=lambda: None,
        )
    return _create

@pytest.fixture
def test_codebase(tmp_path):
    """Create test Python files for indexing"""
    (tmp_path / "module.py").write_text("""
def my_function():
    pass

def caller():
    my_function()
""")
    return tmp_path
```

---

## Summary

**Testing Philosophy:** Test pyramid with emphasis on unit tests, integration for critical paths, E2E for full scenarios

**Coverage:** Foundation ≥ 90%, Indexes ≥ 80%, enforced by pre-commit hooks

**Isolation:** Mock external dependencies in unit tests, real DB in integration

**Organization:** 
- `tests/unit/` - Fast, isolated
- `tests/integration/` - Component interactions
- `tests/e2e/` - Full cascade scenarios

**Execution:** `pytest` with `--cov` for coverage, pre-commit hooks enforce quality gates

**Test Count Estimate:** 
- Unit: 40-50 tests
- Integration: 20-30 tests
- E2E: 5-10 tests
- **Total: 65-90 tests**

---


