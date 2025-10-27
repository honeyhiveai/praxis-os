# Python Testing Standards
# Generated for: praxis-os

## 🚨 CRITICAL: AI Test Execution Protocol

### Rule: Use tox for Test Execution

**IF `tox.ini` exists in project root:**

❌ **NEVER run pytest directly:**
```bash
pytest tests/                    # WRONG
.venv/bin/pytest tests/          # WRONG
python -m pytest tests/          # WRONG
```

✅ **ALWAYS use tox:**
```bash
tox                             # Run all test environments
tox -e unit                     # Run unit tests
tox -e integration              # Run integration tests  
tox -e py313                    # Run specific Python version
```

### Why This Matters

1. **Dependency Isolation**: tox creates clean virtualenvs for each test run
2. **Reproducibility**: Ensures tests run in consistent environment
3. **CI/CD Alignment**: Local tests match continuous integration behavior
4. **Project Convention**: Respects project's testing infrastructure

### AI Assistant Bootstrap Process

```python
# Step 1: Check for tox.ini
from pathlib import Path

if Path("tox.ini").exists():
    # Project uses tox - MUST use it for tests
    print("✅ Found tox.ini - using tox for test execution")
    test_command = "tox"
else:
    # No tox - can use pytest directly
    print("⚠️  No tox.ini found - using pytest directly")
    test_command = "pytest tests/"
```

**See also:** [Python Virtual Environments](python-virtual-environments.md) for venv configuration

---

## Universal Testing Principles

> **See universal standards:**
> - [Test Pyramid](../../universal/testing/test-pyramid.md)
> - [Test Doubles](../../universal/testing/test-doubles.md)
> - [Property-Based Testing](../../universal/testing/property-based-testing.md)
> - [Integration Testing](../../universal/testing/integration-testing.md)

These universal standards contain timeless testing fundamentals. This document applies them to Python-specific contexts.

---

## Python Testing Frameworks

### Framework Comparison

| Framework | Use Case | Your Project Status |
|-----------|----------|-------------------|
| **pytest** | Modern, powerful, fixture-based (recommended) | ❌ Not detected - Recommended to add |
| **unittest** | Built-in, class-based, xUnit style | ❌ Not detected |
| **doctest** | Tests in docstrings | ❌ Not detected |
| **tox** | Multi-environment testing | ❌ Not detected - Recommended for Python packages |
| **coverage.py** | Code coverage measurement | ❌ Not detected - Recommended to add |

### Recommendation for This Project

Since this is a **Python MCP server package**, we recommend:

1. **pytest** - For unit and integration tests
2. **pytest-asyncio** - For async test support (if adding async features)
3. **coverage.py** - For code coverage tracking
4. **tox** - For testing across Python versions

---

## Pytest Patterns (Recommended)

### Installation

```bash
pip install pytest pytest-cov pytest-mock
```

### Project Structure

```
praxis-os/
├── mcp_server/
│   ├── praxis_os_rag.py
│   ├── rag_engine.py
│   └── workflow_engine.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Shared fixtures
│   ├── unit/
│   │   ├── test_rag_engine.py
│   │   ├── test_workflow_engine.py
│   │   └── test_chunker.py
│   └── integration/
│       ├── test_mcp_tools.py
│       └── test_end_to_end.py
└── pytest.ini
```

### Fixtures for Setup/Teardown

```python
# tests/conftest.py
import pytest
from pathlib import Path
import tempfile
import shutil

@pytest.fixture
def temp_standards_dir():
    """Create temporary standards directory for testing."""
    temp_dir = tempfile.mkdtemp()
    standards_path = Path(temp_dir) / "standards"
    standards_path.mkdir(parents=True)
    
    # Create sample standard files
    (standards_path / "test-standard.md").write_text(
        "# Test Standard\n\nThis is a test."
    )
    
    yield standards_path
    
    # Cleanup
    shutil.rmtree(temp_dir)

@pytest.fixture
def rag_engine(temp_standards_dir):
    """Create RAG engine with test data."""
    from mcp_server.rag_engine import RAGEngine
    
    engine = RAGEngine(
        index_path=temp_standards_dir / "index",
        standards_path=temp_standards_dir
    )
    engine.build_index()
    
    yield engine
    
    # Cleanup happens via temp_standards_dir fixture
```

### Unit Test Example

```python
# tests/unit/test_rag_engine.py
import pytest
from mcp_server.rag_engine import RAGEngine

def test_search_returns_relevant_chunks(rag_engine):
    """Test that search returns relevant results."""
    results = rag_engine.search(
        query="concurrency race conditions",
        n_results=5
    )
    
    assert len(results.chunks) > 0
    assert results.retrieval_method in ["vector", "grep_fallback"]
    assert all(chunk.content for chunk in results.chunks)

def test_search_with_filters(rag_engine):
    """Test search with metadata filters."""
    results = rag_engine.search(
        query="testing patterns",
        n_results=5,
        filters={"category": "testing"}
    )
    
    assert all(chunk.metadata.get("category") == "testing" 
               for chunk in results.chunks)

@pytest.mark.parametrize("query,expected_count", [
    ("race conditions", 1),
    ("testing pyramid", 1),
    ("nonexistent query", 0),
])
def test_search_various_queries(rag_engine, query, expected_count):
    """Test search with various queries."""
    results = rag_engine.search(query, n_results=10)
    assert len(results.chunks) >= expected_count
```

### Integration Test Example

```python
# tests/integration/test_mcp_tools.py
import pytest
from mcp_server.praxis_os_rag import create_server

@pytest.fixture
async def mcp_server():
    """Create MCP server for testing."""
    server = create_server()
    yield server
    # Cleanup if needed

@pytest.mark.asyncio
async def test_search_standards_tool(mcp_server):
    """Test search_standards MCP tool."""
    result = await mcp_server.call_tool(
        "search_standards",
        {
            "query": "concurrency patterns",
            "n_results": 3
        }
    )
    
    assert result is not None
    assert "chunks" in result
    assert len(result["chunks"]) <= 3

@pytest.mark.asyncio
async def test_workflow_lifecycle(mcp_server):
    """Test complete workflow lifecycle."""
    # Start workflow
    session = await mcp_server.call_tool(
        "start_workflow",
        {
            "workflow_type": "test_generation_v3",
            "target_file": "tests/test_example.py"
        }
    )
    
    session_id = session["session_id"]
    
    # Get current phase
    phase = await mcp_server.call_tool(
        "get_current_phase",
        {"session_id": session_id}
    )
    
    assert phase["phase_number"] == 1
    
    # Complete phase
    result = await mcp_server.call_tool(
        "complete_phase",
        {
            "session_id": session_id,
            "phase_number": 1,
            "evidence": "Phase 1 completed"
        }
    )
    
    assert result["success"] is True
```

---

## Mocking and Test Doubles

### Using `unittest.mock`

```python
from unittest.mock import Mock, patch, MagicMock, call
import pytest

# Mock external dependencies
@patch('mcp_server.rag_engine.lancedb.connect')
def test_rag_engine_with_mock_db(mock_connect):
    """Test RAG engine with mocked database."""
    # Setup mock
    mock_db = MagicMock()
    mock_table = MagicMock()
    mock_connect.return_value = mock_db
    mock_db.open_table.return_value = mock_table
    
    # Mock search results
    mock_table.search.return_value.limit.return_value.to_list.return_value = [
        {"chunk_id": "1", "content": "Test chunk", "distance": 0.1}
    ]
    
    # Test
    from mcp_server.rag_engine import RAGEngine
    engine = RAGEngine(index_path="test", standards_path="test")
    results = engine.search("test query")
    
    # Assertions
    mock_connect.assert_called_once()
    mock_db.open_table.assert_called_once()
    assert len(results.chunks) == 1

# Mock file system operations
@patch('pathlib.Path.exists')
@patch('pathlib.Path.read_text')
def test_load_standard_files(mock_read, mock_exists):
    """Test loading standard files with mocked filesystem."""
    mock_exists.return_value = True
    mock_read.return_value = "# Standard Content"
    
    # Your code that reads files
    # ...
    
    mock_exists.assert_called()
    mock_read.assert_called()
```

### Pytest-mock Plugin

```python
# More concise mocking with pytest-mock
def test_with_pytest_mock(mocker):
    """Test using pytest-mock plugin."""
    # Mock method
    mock_search = mocker.patch('mcp_server.rag_engine.RAGEngine.search')
    mock_search.return_value = MockSearchResult(chunks=[])
    
    # Test code
    # ...
    
    mock_search.assert_called_once_with("query", n_results=5)
```

---

## Testing Concurrency

### Thread Safety Tests

```python
import threading
import pytest

def test_concurrent_rag_searches(rag_engine):
    """Test that RAG engine handles concurrent searches safely."""
    results = []
    errors = []
    
    def search_worker(query):
        try:
            result = rag_engine.search(query, n_results=5)
            results.append(result)
        except Exception as e:
            errors.append(e)
    
    # Launch 10 concurrent searches
    threads = [
        threading.Thread(target=search_worker, args=(f"query {i}",))
        for i in range(10)
    ]
    
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    # Verify no errors and all results returned
    assert len(errors) == 0, f"Errors occurred: {errors}"
    assert len(results) == 10

def test_workflow_state_concurrent_writes(temp_dir):
    """Test that state manager handles concurrent writes safely."""
    from mcp_server.state_manager import StateManager
    
    state_manager = StateManager(temp_dir)
    
    def writer(session_id, value):
        for i in range(100):
            state_manager.save_state(session_id, {"value": value, "iteration": i})
    
    threads = [
        threading.Thread(target=writer, args=(f"session_{i}", i))
        for i in range(5)
    ]
    
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    # Verify all states saved correctly
    for i in range(5):
        state = state_manager.load_state(f"session_{i}")
        assert state is not None
        assert state["value"] == i
```

---

## Test Coverage

### Configuration (`pytest.ini`)

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --cov=mcp_server
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
    -v
```

### Running with Coverage

```bash
# Run tests with coverage
pytest --cov=mcp_server --cov-report=html

# View coverage report
open htmlcov/index.html

# Run specific test file
pytest tests/unit/test_rag_engine.py -v

# Run with markers
pytest -m "not slow" -v
```

### Coverage Goals

| Component | Target Coverage | Priority |
|-----------|----------------|----------|
| Core MCP tools | 90%+ | Critical |
| RAG engine | 85%+ | High |
| Workflow engine | 85%+ | High |
| Chunker | 80%+ | Medium |
| Utilities | 75%+ | Medium |

---

## Property-Based Testing with Hypothesis

For complex logic like chunking:

```python
from hypothesis import given, strategies as st
import pytest

@given(st.text(min_size=1, max_size=10000))
def test_chunker_preserves_content(text):
    """Property: Chunking and rejoining should preserve content."""
    from mcp_server.chunker import chunk_text
    
    chunks = chunk_text(text, max_chunk_size=500)
    rejoined = "".join(chunk.content for chunk in chunks)
    
    # Content should be preserved (modulo whitespace normalization)
    assert rejoined.strip() == text.strip()

@given(
    st.text(min_size=100, max_size=5000),
    st.integers(min_value=50, max_value=1000)
)
def test_chunks_respect_max_size(text, max_size):
    """Property: All chunks should respect max size limit."""
    from mcp_server.chunker import chunk_text
    
    chunks = chunk_text(text, max_chunk_size=max_size)
    
    for chunk in chunks:
        assert len(chunk.content) <= max_size * 1.2  # Allow 20% overflow for boundaries
```

---

## Tox for Multi-Environment Testing

### Configuration (`tox.ini`)

```ini
[tox]
envlist = py38,py39,py310,py311,py312
isolated_build = True

[testenv]
deps =
    pytest>=7.0
    pytest-cov>=4.0
    pytest-mock>=3.0
    -r{toxinidir}/mcp_server/requirements.txt

commands =
    pytest {posargs:tests/}

[testenv:coverage]
commands =
    pytest --cov=mcp_server --cov-report=html --cov-report=term

[testenv:lint]
deps =
    black
    pylint
    mypy
commands =
    black --check mcp_server/
    pylint mcp_server/
    mypy mcp_server/
```

### Running Tox

```bash
# Test all Python versions
tox

# Test specific version
tox -e py311

# Run coverage
tox -e coverage

# Run linting
tox -e lint
```

---

## Your Project Context: praxis-os

### Current State

❌ **No test infrastructure detected**
❌ **No pytest configuration**
❌ **No coverage tracking**
❌ **No CI/CD testing**

### Recommended Next Steps

1. **Add pytest infrastructure:**
   ```bash
   pip install pytest pytest-cov pytest-mock pytest-asyncio
   mkdir -p tests/unit tests/integration
   touch tests/__init__.py tests/conftest.py
   ```

2. **Create `pytest.ini`:**
   ```ini
   [pytest]
   testpaths = tests
   python_files = test_*.py
   addopts = --cov=mcp_server --cov-report=term-missing -v
   ```

3. **Write initial tests:**
   - `tests/unit/test_rag_engine.py` - RAG search functionality
   - `tests/unit/test_chunker.py` - Markdown chunking
   - `tests/unit/test_workflow_engine.py` - Workflow state machine
   - `tests/integration/test_mcp_tools.py` - End-to-end MCP tools

4. **Add CI/CD:**
   - GitHub Actions workflow for running tests
   - Pre-commit hooks for running tests locally

5. **Set coverage goals:**
   - Aim for 80%+ coverage on core functionality
   - Track coverage over time

---

## Testing Best Practices for MCP Servers

### 1. Test MCP Tool Interface

```python
@pytest.mark.asyncio
async def test_mcp_tool_input_validation():
    """Test that MCP tools validate input."""
    # Test missing required parameters
    with pytest.raises(ValueError):
        await search_standards(query=None)
    
    # Test invalid parameter types
    with pytest.raises(TypeError):
        await search_standards(query=123)
```

### 2. Test with Real Standards Files

```python
def test_rag_with_real_standards():
    """Test RAG engine with actual standards files."""
    standards_path = Path("universal/standards")
    
    engine = RAGEngine(
        index_path="test_index",
        standards_path=standards_path
    )
    engine.build_index()
    
    # Test with real queries
    results = engine.search("race conditions", n_results=5)
    
    assert len(results.chunks) > 0
    assert any("race condition" in chunk.content.lower() 
               for chunk in results.chunks)
```

### 3. Test Index Rebuilding

```python
def test_file_watcher_rebuilds_index(temp_dir):
    """Test that file watcher rebuilds index on changes."""
    standards_path = temp_dir / "standards"
    standards_path.mkdir()
    
    # Create initial file
    (standards_path / "test.md").write_text("# Original")
    
    # Build initial index
    engine = RAGEngine(index_path=temp_dir / "index", standards_path=standards_path)
    engine.build_index()
    
    # Modify file
    (standards_path / "test.md").write_text("# Updated Content")
    
    # Trigger rebuild (in real code, file watcher does this)
    engine.rebuild_index()
    
    # Verify updated content is indexed
    results = engine.search("Updated Content")
    assert len(results.chunks) > 0
```

---

## References

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [Hypothesis documentation](https://hypothesis.readthedocs.io/)
- [Universal Test Pyramid](../../universal/testing/test-pyramid.md)
- [Universal Test Doubles](../../universal/testing/test-doubles.md)

---

**Generated for praxis-os MCP server project. Add pytest infrastructure to improve code quality and confidence.**
