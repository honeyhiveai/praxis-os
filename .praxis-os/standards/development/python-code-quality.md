# Python Code Quality Standards
# Generated for: praxis-os

## Code Quality Tools

### Your Project Status

| Tool | Purpose | Status | Recommendation |
|------|---------|--------|----------------|
| **Black** | Code formatting | ❌ Not configured | Add with `pyproject.toml` |
| **isort** | Import sorting | ❌ Not configured | Add with Black compatibility |
| **Pylint** | Static analysis | ❌ Not configured | Add for code quality checks |
| **MyPy** | Type checking | ❌ Not configured | Add for type safety |
| **Flake8** | Alternative linter | ❌ Not configured | Optional (Pylint preferred) |

---

## Black: Code Formatting

### Installation

```bash
pip install black
```

### Configuration (`pyproject.toml`)

```toml
[tool.black]
line-length = 100
target-version = ['py38', 'py39', 'py310', 'py311', 'py312']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''
```

### Usage

```bash
# Format all files
black mcp_server/

# Check without modifying
black --check mcp_server/

# Format specific file
black mcp_server/agent_os_rag.py

# See what would change
black --diff mcp_server/
```

### Pre-commit Hook

```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black

# Install hooks
pre-commit install
```

---

## isort: Import Sorting

### Installation

```bash
pip install isort
```

### Configuration (`pyproject.toml`)

```toml
[tool.isort]
profile = "black"  # Compatible with Black
line_length = 100
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
```

### Usage

```bash
# Sort imports
isort mcp_server/

# Check without modifying
isort --check mcp_server/

# See diff
isort --diff mcp_server/
```

### Correct Import Order

```python
# Standard library imports
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Third-party imports
import lancedb
from mcp.server.fastmcp import FastMCP
from sentence_transformers import SentenceTransformer
from watchdog.observers import Observer

# Local imports
from rag_engine import RAGEngine
from workflow_engine import WorkflowEngine
```

---

## Pylint: Static Analysis

### Installation

```bash
pip install pylint
```

### Configuration (`pyproject.toml`)

```toml
[tool.pylint.main]
py-version = "3.8"
ignore = [".git", "__pycache__", "build", "dist"]
jobs = 0  # Use all CPUs

[tool.pylint.messages_control]
disable = [
    "C0103",  # Invalid name (snake_case enforced elsewhere)
    "R0903",  # Too few public methods (fine for data classes)
    "W0212",  # Protected access (allowed in tests)
]

[tool.pylint.format]
max-line-length = 100
max-module-lines = 1000

[tool.pylint.design]
max-args = 7
max-attributes = 10
max-branches = 15
max-locals = 20
max-returns = 6
max-statements = 50
```

### Usage

```bash
# Analyze all files
pylint mcp_server/

# Analyze specific file
pylint mcp_server/agent_os_rag.py

# Generate config file
pylint --generate-rcfile > .pylintrc

# Score should be 10.0/10
# Target: No warnings or errors
```

### Common Pylint Issues and Fixes

#### Issue: Line too long

```python
# ❌ Bad: Line exceeds 100 characters
result = some_function(very_long_parameter_name, another_long_parameter, yet_another_parameter, and_more)

# ✅ Good: Break into multiple lines
result = some_function(
    very_long_parameter_name,
    another_long_parameter,
    yet_another_parameter,
    and_more
)
```

#### Issue: Too many arguments

```python
# ❌ Bad: Too many parameters
def create_engine(path1, path2, param1, param2, param3, param4, param5, param6):
    pass

# ✅ Good: Use config object
from dataclasses import dataclass

@dataclass
class EngineConfig:
    path1: Path
    path2: Path
    param1: str
    param2: int
    # ...

def create_engine(config: EngineConfig):
    pass
```

---

## MyPy: Type Checking

### Installation

```bash
pip install mypy
```

### Configuration (`pyproject.toml`)

```toml
[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
strict_equality = true

[[tool.mypy.overrides]]
module = [
    "lancedb.*",
    "sentence_transformers.*",
    "watchdog.*",
]
ignore_missing_imports = true
```

### Usage

```bash
# Type check all files
mypy mcp_server/

# Type check specific file
mypy mcp_server/agent_os_rag.py

# Show error codes
mypy --show-error-codes mcp_server/
```

### Type Annotation Examples

#### Function Signatures

```python
from typing import List, Dict, Optional, Union, Tuple
from pathlib import Path

def search_standards(
    query: str,
    n_results: int = 5,
    filters: Optional[Dict[str, str]] = None
) -> List[Dict[str, Union[str, float]]]:
    """
    Search standards with type hints.
    
    :param query: Search query string
    :param n_results: Number of results to return
    :param filters: Optional metadata filters
    :returns: List of result dictionaries
    """
    # Implementation
    return []
```

#### Class Attributes

```python
from typing import Optional
from pathlib import Path
import threading

class RAGEngine:
    """RAG engine with typed attributes."""
    
    index_path: Path
    standards_path: Path
    _lock: threading.Lock
    _index: Optional[object]  # LanceDB table
    
    def __init__(self, index_path: Path, standards_path: Path) -> None:
        self.index_path = index_path
        self.standards_path = standards_path
        self._lock = threading.Lock()
        self._index = None
```

#### Dataclasses with Types

```python
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class SearchResult:
    """Search result with type hints."""
    
    chunk_id: str
    content: str
    distance: float
    metadata: Dict[str, str]
    
    def is_relevant(self, threshold: float = 0.8) -> bool:
        """Check if result meets relevance threshold."""
        return self.distance >= threshold
```

---

## Docstrings (Sphinx Format - Mandatory)

### Function Docstrings

```python
def search(
    self,
    query: str,
    n_results: int = 5,
    filters: Optional[Dict[str, str]] = None
) -> SearchResults:
    """
    Search the vector index for relevant chunks.
    
    Performs semantic search using embeddings and returns the most
    relevant chunks from the standards documentation.
    
    :param query: Natural language search query
    :param n_results: Maximum number of results to return (default: 5)
    :param filters: Optional metadata filters (e.g., {"category": "concurrency"})
    :returns: SearchResults object containing chunks and metadata
    :raises ValueError: If query is empty or n_results is negative
    :raises RuntimeError: If index is not initialized
    
    Example:
        >>> engine = RAGEngine(index_path, standards_path)
        >>> results = engine.search("race conditions", n_results=3)
        >>> for chunk in results.chunks:
        ...     print(chunk.content)
    """
    if not query:
        raise ValueError("Query cannot be empty")
    if n_results < 0:
        raise ValueError("n_results must be non-negative")
    
    # Implementation
    ...
```

### Class Docstrings

```python
class RAGEngine:
    """
    RAG (Retrieval-Augmented Generation) engine for Agent OS standards.
    
    This class provides semantic search over Agent OS standards using
    LanceDB vector database and sentence transformers for embeddings.
    
    The engine supports:
    - Vector similarity search
    - Metadata filtering
    - Automatic index rebuilding
    - Thread-safe operations
    
    :ivar index_path: Path to LanceDB index directory
    :ivar standards_path: Path to standards markdown files
    
    Example:
        >>> engine = RAGEngine(
        ...     index_path=Path(".praxis-os/.cache/index"),
        ...     standards_path=Path(".praxis-os/standards")
        ... )
        >>> engine.build_index()
        >>> results = engine.search("concurrency patterns")
    """
    
    def __init__(self, index_path: Path, standards_path: Path) -> None:
        """
        Initialize RAG engine.
        
        :param index_path: Directory for vector index storage
        :param standards_path: Directory containing .md standard files
        :raises FileNotFoundError: If standards_path doesn't exist
        """
        ...
```

### Module Docstrings

```python
"""
Agent OS MCP/RAG Server - Main Integration Point.

This module provides the MCP (Model Context Protocol) server that exposes
Agent OS standards via semantic search and workflow management.

Tools:
    - search_standards: Semantic search over standards
    - start_workflow: Initialize phase-gated workflow
    - get_current_phase: Retrieve current phase content
    - complete_phase: Submit evidence and advance
    - get_workflow_state: Query workflow state

Features:
    - Automatic index rebuild when standards change
    - Local-first embeddings (free, offline)
    - Optional observability tracing

Example:
    Run the MCP server:
    
    $ python -m mcp_server.agent_os_rag
    
    Or from Python:
    
    >>> from mcp_server.agent_os_rag import create_server
    >>> server = create_server()
"""
```

---

## Code Review Checklist

Before committing code, verify:

### Formatting
- [ ] Black formatting applied: `black mcp_server/`
- [ ] Imports sorted: `isort mcp_server/`
- [ ] Line length ≤ 100 characters

### Static Analysis
- [ ] Pylint score 10.0/10: `pylint mcp_server/`
- [ ] MyPy passes with no errors: `mypy mcp_server/`
- [ ] No unused imports or variables

### Documentation
- [ ] All functions have Sphinx docstrings
- [ ] All classes have docstrings
- [ ] All modules have docstrings
- [ ] Complex logic has inline comments

### Type Hints
- [ ] All function parameters typed
- [ ] All return types typed
- [ ] No `Any` types (unless truly necessary)

### Testing
- [ ] Tests pass: `pytest tests/`
- [ ] Coverage ≥ 80%: `pytest --cov=mcp_server`
- [ ] No test warnings

---

## Your Project Context: praxis-os

### Recommendations

1. **Add `pyproject.toml`** with Black, isort, Pylint, MyPy config
2. **Run formatters** on existing code
3. **Add pre-commit hooks** to enforce standards
4. **Set up CI/CD** to run checks automatically
5. **Document code quality standards** in CONTRIBUTING.md

### Quick Setup Script

```bash
#!/bin/bash
# setup_code_quality.sh

# Install tools
pip install black isort pylint mypy pre-commit

# Create pyproject.toml (use examples above)

# Format existing code
black mcp_server/
isort mcp_server/

# Check code quality
pylint mcp_server/
mypy mcp_server/

# Setup pre-commit
pre-commit install
```

---

## References

- [Black documentation](https://black.readthedocs.io/)
- [isort documentation](https://pycqa.github.io/isort/)
- [Pylint documentation](https://pylint.pycqa.org/)
- [MyPy documentation](https://mypy.readthedocs.io/)
- [PEP 8 - Style Guide](https://peps.python.org/pep-0008/)
- [PEP 484 - Type Hints](https://peps.python.org/pep-0484/)

---

**Generated for praxis-os. Implement these code quality standards to maintain high code quality and consistency.**
