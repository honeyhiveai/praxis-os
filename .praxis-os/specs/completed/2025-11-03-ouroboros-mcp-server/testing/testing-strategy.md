# Testing Strategy

**Purpose:** Defines unit and integration testing approach, patterns, and execution  
**Date:** 2025-11-06

---

## Testing Philosophy

**Core Principle:** Tests are specifications.

- **Unit tests** validate individual functions/classes in isolation
- **Integration tests** validate subsystems working together
- **Performance tests** validate NFR metrics (latency, memory, throughput)
- **End-to-end tests** validate complete user workflows

**Coverage Targets:**
- Unit test coverage: ≥50% (validate logic)
- Integration test coverage: ≥60% (validate composition)
- Critical path coverage: 100% (every FR/NFR has tests)

---

## Test Organization

### Directory Structure

```
tests/
├── unit/                          # Isolated unit tests (no I/O, no external deps)
│   ├── test_config_loader.py
│   ├── test_query_classifier.py
│   └── test_prepend_generator.py
│
├── integration/                   # Cross-subsystem integration tests
│   ├── test_search_flow.py       # End-to-end search
│   ├── test_workflow_flow.py     # End-to-end workflow
│   └── test_browser_flow.py      # End-to-end browser
│
├── ouroboros/                     # Mirrors source structure
│   ├── config/
│   │   └── test_config_validation.py
│   ├── foundation/
│   │   └── test_errors.py
│   ├── middleware/
│   │   ├── test_prepend_generator.py
│   │   ├── test_query_tracker.py
│   │   └── test_query_classifier.py
│   ├── subsystems/
│   │   ├── rag/
│   │   │   ├── test_index_manager.py
│   │   │   ├── test_file_watcher.py  # ← CRITICAL MISSING TEST
│   │   │   ├── test_standards_index.py
│   │   │   ├── test_code_index.py
│   │   │   ├── test_graph_index.py
│   │   │   └── test_ast_index.py
│   │   ├── workflow/
│   │   │   ├── test_engine.py
│   │   │   ├── test_checkpoint_validator.py
│   │   │   └── test_state_manager.py
│   │   └── browser/
│   │       └── test_session_mapper.py
│   ├── tools/
│   │   ├── test_pos_search.py
│   │   ├── test_pos_workflow.py
│   │   ├── test_pos_browser.py
│   │   └── test_pos_filesystem.py
│   ├── performance/
│   │   └── test_performance.py
│   ├── integration/
│   │   ├── test_search_flow.py
│   │   ├── test_file_watcher_latency.py
│   │   ├── test_index_health.py
│   │   ├── test_reliability_soak.py
│   │   └── test_thread_safety.py
│   └── validation/
│       ├── test_architecture.py
│       ├── test_behavioral_engineering.py
│       ├── test_error_messages.py
│       └── test_documentation.py
│
├── security/
│   ├── test_path_validation.py
│   ├── test_query_logging.py
│   └── test_secrets.py
│
└── conftest.py                    # Shared fixtures and config
```

---

## Unit Testing Strategy

### Principles

1. **No External Dependencies:** No file I/O, no database, no network
2. **Fast Execution:** Each test <10ms
3. **Isolated:** Tests don't affect each other
4. **Deterministic:** No flakiness, no timing dependencies

### Patterns

#### Pattern 1: Pure Function Testing

**Example:** Query classification

```python
def test_classify_conceptual_query():
    """Test that conceptual questions are classified correctly."""
    query = "How does the workflow system work?"
    result = classify_query_angle(query)
    assert result == "conceptual"
    assert "How" in result.keywords
```

#### Pattern 2: Mock External Dependencies

**Example:** Config loading

```python
@patch('ouroboros.config.loader.open')
def test_config_load(mock_open):
    """Test config loads from YAML."""
    mock_open.return_value = StringIO("indexes:\n  standards:\n    enabled: true")
    config = load_config()
    assert config.indexes.standards.enabled == True
```

#### Pattern 3: Fixture-Based Setup

**Example:** Prepend generator

```python
@pytest.fixture
def session_history():
    """Create fake session history."""
    return [
        {"query": "How does X work?", "angle": "conceptual"},
        {"query": "Where is Y?", "angle": "location"},
    ]

def test_prepend_generation(session_history):
    """Test prepend includes gamification."""
    prepend = generate_prepend(session_history)
    assert "🎯" in prepend  # Progress emoji
    assert "diversity" in prepend.lower()
```

### Mocking Strategy

**What to mock:**
- File system I/O (`open`, `Path.read_text`)
- Database connections (SQLite, DuckDB, LanceDB)
- Network calls (HTTP, external APIs)
- Time-dependent operations (`datetime.now()`)

**What NOT to mock:**
- Pure business logic
- Data transformations
- Pydantic models
- Simple utilities

**Mocking libraries:**
- `unittest.mock` (standard library, use for most cases)
- `pytest-mock` (cleaner syntax for pytest)
- `responses` (for HTTP mocking)
- `freezegun` (for time mocking)

---

## Integration Testing Strategy

### Principles

1. **Real Components:** Use actual subsystems, not mocks
2. **Temporary Resources:** Create/cleanup test data
3. **Realistic Scenarios:** Test real workflows
4. **Acceptable Latency:** Tests can take seconds, not milliseconds

### Patterns

#### Pattern 1: End-to-End Flow Testing

**Example:** Search flow (Standards → Index → Results)

```python
@pytest.fixture(scope="module")
def temp_standards_index(tmp_path_factory):
    """Create temporary StandardsIndex with test data."""
    index_dir = tmp_path_factory.mktemp("indexes")
    standards_dir = tmp_path_factory.mktemp("standards")
    
    # Create test standards files
    (standards_dir / "test-standard.md").write_text(
        "# Test Standard\n\nThis is a test standard about XYZTESTTERM."
    )
    
    # Build index
    index = StandardsIndex(index_dir, standards_dir)
    index.build()
    
    yield index
    
    # Cleanup
    shutil.rmtree(index_dir)
    shutil.rmtree(standards_dir)

def test_search_flow(temp_standards_index):
    """Test end-to-end search: query → index → results."""
    results = temp_standards_index.search("XYZTESTTERM", n_results=5)
    
    assert len(results) > 0
    assert "test-standard.md" in results[0].file_path
    assert "XYZTESTTERM" in results[0].content
```

#### Pattern 2: FileWatcher Integration Test

**Example:** File change → index update → searchable

```python
@pytest.fixture
def file_watcher_setup(tmp_path):
    """Setup FileWatcher with temp paths."""
    standards_dir = tmp_path / "standards"
    standards_dir.mkdir()
    
    index_dir = tmp_path / "indexes"
    index_dir.mkdir()
    
    # Create index
    index_manager = IndexManager(index_dir)
    index_manager.indexes["standards"] = StandardsIndex(index_dir, standards_dir)
    
    # Create watcher
    config = FileWatcherConfig(
        enabled=True,
        debounce_seconds=0.5,
        check_interval_seconds=0.1
    )
    
    path_mappings = {
        str(standards_dir): ["standards"]
    }
    
    watcher = FileWatcher(config, index_manager, path_mappings)
    watcher.start()
    
    yield standards_dir, index_manager, watcher
    
    # Cleanup
    watcher.stop()

def test_file_watcher_detects_and_indexes_new_file(file_watcher_setup):
    """Test FileWatcher detects new file and triggers index update."""
    standards_dir, index_manager, watcher = file_watcher_setup
    
    # Create new file with unique term
    unique_term = f"UNIQUETERM{time.time()}"
    (standards_dir / "new-file.md").write_text(f"# New File\n\n{unique_term}")
    
    # Wait for watcher to detect and index (max 5s)
    for _ in range(50):  # 50 * 0.1s = 5s max
        time.sleep(0.1)
        results = index_manager.indexes["standards"].search(unique_term, n_results=1)
        if len(results) > 0:
            break
    
    # Assert file was indexed
    assert len(results) > 0
    assert unique_term in results[0].content
    assert "new-file.md" in results[0].file_path
```

#### Pattern 3: Workflow Execution Test

**Example:** Start workflow → execute phase → validate evidence → complete

```python
def test_workflow_phase_gating():
    """Test that phase gates enforce evidence requirements."""
    # Start workflow
    session = start_workflow(
        workflow_type="spec_execution_v1",
        target_file="test-spec.md"
    )
    
    # Attempt to complete phase without evidence
    with pytest.raises(EvidenceValidationError) as exc_info:
        complete_phase(
            session_id=session.id,
            phase=1,
            evidence={}  # Missing required evidence
        )
    
    assert "Missing required evidence" in str(exc_info.value)
    
    # Complete phase with valid evidence
    result = complete_phase(
        session_id=session.id,
        phase=1,
        evidence={
            "spec_read": True,
            "phases_identified": True,
            "checkpoint_requirements_noted": True
        }
    )
    
    assert result.success == True
    assert session.current_phase == 2
```

### Fixture Strategy

**Scope levels:**
- `function`: Default, created/destroyed per test (use for most)
- `module`: Created once per test file (use for slow setup like indexes)
- `session`: Created once per test run (use for global resources)

**Common fixtures:**

```python
# conftest.py - shared fixtures

@pytest.fixture(scope="session")
def test_config():
    """Load test configuration."""
    return load_config("tests/fixtures/test_config.yaml")

@pytest.fixture
def temp_dir(tmp_path):
    """Create temporary directory that auto-cleans."""
    return tmp_path

@pytest.fixture(scope="module")
def standards_index(tmp_path_factory):
    """Create standards index with test data."""
    # ... setup ...
    yield index
    # ... cleanup ...

@pytest.fixture
def mock_index_manager():
    """Mock IndexManager for testing without real indexes."""
    manager = Mock(spec=IndexManager)
    manager.indexes = {}
    return manager
```

---

## Test Execution

### Running Tests

**All tests:**
```bash
pytest tests/
```

**Unit tests only (fast):**
```bash
pytest tests/unit/ tests/ouroboros/ -m "not integration"
```

**Integration tests only:**
```bash
pytest tests/integration/ tests/ouroboros/integration/
```

**Performance tests:**
```bash
pytest tests/ouroboros/performance/ --performance
```

**Specific test file:**
```bash
pytest tests/ouroboros/subsystems/rag/test_file_watcher.py
```

**Specific test function:**
```bash
pytest tests/ouroboros/subsystems/rag/test_file_watcher.py::test_watcher_detects_new_file
```

**With coverage:**
```bash
pytest tests/ --cov=ouroboros --cov-report=html
```

**Parallel execution (faster):**
```bash
pytest tests/ -n auto  # Use pytest-xdist
```

### Test Markers

**Define markers in pytest.ini:**
```ini
[pytest]
markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (slower, real resources)
    performance: Performance tests (measure NFRs)
    security: Security tests
    slow: Tests that take >5 seconds
```

**Use markers in tests:**
```python
@pytest.mark.integration
def test_file_watcher_flow():
    ...

@pytest.mark.performance
@pytest.mark.slow
def test_cold_start_latency():
    ...
```

**Run by marker:**
```bash
pytest -m unit          # Only unit tests
pytest -m integration   # Only integration tests
pytest -m "not slow"    # Skip slow tests
```

---

## Test Data Management

### Fixtures Directory

```
tests/fixtures/
├── config/
│   └── test_config.yaml
├── standards/
│   ├── test-standard-1.md
│   └── test-standard-2.md
├── workflows/
│   └── test_workflow_v1/
│       └── metadata.json
└── code/
    └── test_module.py
```

### Generating Test Data

**Pattern: Factory functions**

```python
def create_test_standard(content: str, filename: str = "test.md") -> Path:
    """Create a test standards file."""
    path = tmp_path / filename
    path.write_text(content)
    return path

def create_test_workflow(phases: int = 3) -> Path:
    """Create a test workflow with N phases."""
    metadata = {
        "workflow_type": "test_workflow",
        "phases": [
            {"phase_number": i, "phase_name": f"Phase {i}"}
            for i in range(1, phases + 1)
        ]
    }
    path = tmp_path / "metadata.json"
    path.write_text(json.dumps(metadata))
    return path
```

---

## Continuous Integration

### Pre-commit Hooks

Run fast tests before commit:
```bash
# .git/hooks/pre-commit
pytest tests/unit/ -x --tb=short
```

### CI Pipeline

**GitHub Actions workflow:**
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -e .[test]
      - run: pytest tests/ --cov --cov-report=xml
      - uses: codecov/codecov-action@v3
```

---

## Coverage Monitoring

### Coverage Targets

- **Overall:** ≥60% (integration focus)
- **Critical subsystems:** ≥80%
  - `ouroboros/subsystems/rag/` (≥80%)
  - `ouroboros/subsystems/workflow/` (≥80%)
  - `ouroboros/middleware/` (≥70%)
- **Tools:** ≥70%

### Coverage Reports

**HTML report (interactive):**
```bash
pytest tests/ --cov=ouroboros --cov-report=html
open htmlcov/index.html
```

**Terminal report:**
```bash
pytest tests/ --cov=ouroboros --cov-report=term-missing
```

**XML report (for CI):**
```bash
pytest tests/ --cov=ouroboros --cov-report=xml
```

---

## Critical Test Cases to Implement First

**Priority 1 (Essential):**
1. `tests/ouroboros/subsystems/rag/test_file_watcher.py` (8 tests) - **FR-015**
2. `tests/ouroboros/integration/test_file_watcher_latency.py` (2 tests) - **NFR-P5**
3. `tests/ouroboros/integration/test_search_flow.py` (extend for FR-011)
4. `tests/ouroboros/tools/test_pos_search.py` (6 tests) - **FR-005**

**Priority 2 (Important):**
5. `tests/ouroboros/config/test_config_validation.py` (FR-023, FR-025)
6. `tests/ouroboros/subsystems/rag/test_graph_index.py` (FR-013)
7. `tests/ouroboros/performance/test_performance.py` (NFR-P1-P7)
8. `tests/ouroboros/integration/test_index_health.py` (NFR-R2, NFR-R3)

**Priority 3 (Nice to Have):**
9. `tests/security/*` (NFR-S1-S4)
10. `tests/ouroboros/validation/test_architecture.py` (NFR-M1, NFR-M2)

---

## Testing Anti-Patterns to Avoid

### ❌ Don't: Test implementation details
```python
# Bad: Brittle, couples test to implementation
def test_prepend_uses_jinja_template():
    assert "jinja2" in str(type(prepend_generator.template))
```

### ✅ Do: Test observable behavior
```python
# Good: Tests output, not how it's generated
def test_prepend_includes_progress_emoji():
    prepend = generate_prepend(session_history)
    assert "🎯" in prepend
```

---

### ❌ Don't: Use real production resources
```python
# Bad: Modifies production database
def test_query_logging():
    log_query("test", db_path=".praxis-os/query_history.db")
```

### ✅ Do: Use temporary test resources
```python
# Good: Uses temp database
def test_query_logging(tmp_path):
    db_path = tmp_path / "test.db"
    log_query("test", db_path=db_path)
```

---

### ❌ Don't: Test multiple concerns in one test
```python
# Bad: Tests file watcher detection AND indexing AND search
def test_everything():
    watcher.start()
    create_file("test.md")
    assert watcher.detected_changes
    assert index.is_indexed("test.md")
    assert len(search("test")) > 0
```

### ✅ Do: One test per concern
```python
# Good: Separate tests for each concern
def test_watcher_detects_file_creation():
    watcher.start()
    create_file("test.md")
    assert watcher.detected_changes

def test_watcher_triggers_index_update():
    watcher.start()
    create_file("test.md")
    wait_for_indexing()
    assert index.is_indexed("test.md")

def test_indexed_file_searchable():
    index.add_file("test.md")
    results = search("test")
    assert len(results) > 0
```

---

## Summary

- **Unit tests:** Fast, isolated, no external deps, ≥50% coverage
- **Integration tests:** Real components, temp resources, ≥60% coverage
- **Critical gap:** FileWatcher tests (FR-015, NFR-P5) - **8 tests needed**
- **Test organization:** Mirror source structure in `tests/ouroboros/`
- **Mocking:** Mock I/O and external deps, don't mock business logic
- **Fixtures:** Use pytest fixtures for setup/teardown
- **Execution:** Use markers for test selection, parallel execution for speed
- **CI:** Run tests on every push, monitor coverage

**Next Step:** Implement Priority 1 tests, starting with FileWatcher.

