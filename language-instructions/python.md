# Python Language-Specific Standards Generation Instructions

**For the Cursor Agent: When installing Agent OS in a Python project, use these instructions to generate language-specific standards by applying universal CS fundamentals to Python-specific contexts.**

---

## Instructions Overview

You will generate 6 Python-specific standard files by:
1. Reading universal standards from `universal/standards/`
2. Analyzing the target Python project
3. Applying Python-specific context (GIL, threading, pytest, tox, venvs, etc.)
4. Integrating project-specific patterns (detected frameworks, tools)
5. Creating `.praxis-os/config.json` with venv paths and test commands

## File 1: `python-concurrency.md`

### Source Materials
Read these universal standards:
- `universal/standards/concurrency/race-conditions.md`
- `universal/standards/concurrency/deadlocks.md` (if exists)
- `universal/standards/concurrency/locking-strategies.md` (if exists)

### Python-Specific Context to Add

#### The GIL (Global Interpreter Lock)
Explain:
- What the GIL is and why it exists
- GIL prevents true parallelism in threading
- When GIL matters (CPU-bound) vs when it doesn't (I/O-bound)

#### Python Concurrency Models
Map universal concepts to Python:

| Universal Concept | Python Implementation | When to Use |
|-------------------|----------------------|-------------|
| Multi-threading | `threading` module | I/O-bound tasks (GIL allows context switching) |
| Multi-processing | `multiprocessing` module | CPU-bound tasks (bypasses GIL) |
| Async/cooperative | `asyncio` module | High-concurrency I/O (single-threaded) |
| Mutex | `threading.Lock` | Simple mutual exclusion |
| Reentrant Lock | `threading.RLock` | Nested function calls with same lock |
| Semaphore | `threading.Semaphore` | Resource pooling |
| Event | `threading.Event` | Signaling between threads |
| Condition Variable | `threading.Condition` | Complex synchronization |

#### Code Examples
Generate Python examples showing:

```python
# Example: Proper locking with context manager
import threading

class ThreadSafeCounter:
    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()
    
    def increment(self):
        with self._lock:  # Context manager ensures release
            self._value += 1
    
    def get_value(self):
        with self._lock:
            return self._value

# Example: GIL-aware decision making
# For I/O-bound: Use threading
import threading
import requests

def fetch_url(url):
    return requests.get(url).text

urls = [...]
threads = [threading.Thread(target=fetch_url, args=(url,)) for url in urls]
# Works well: GIL released during I/O

# For CPU-bound: Use multiprocessing
from multiprocessing import Pool

def compute_intensive(data):
    return sum(x**2 for x in data)

with Pool(processes=4) as pool:
    results = pool.map(compute_intensive, data_chunks)
# True parallelism: Bypasses GIL
```

### Project Context Integration

Analyze the target project and add:
- **If `asyncio` detected**: Add async/await patterns, event loop guidance
- **If Celery detected**: Add distributed task queue patterns, worker concurrency
- **If Django detected**: Add request-scoped concurrency, database connection pooling
- **If Flask detected**: Add WSGI worker model, thread-local storage
- **If FastAPI detected**: Add async route handlers, background tasks

### Structure

```markdown
# Python Concurrency Standards
# Generated for: {project_name}

## Universal Concurrency Principles
> See universal standards:
> - [Race Conditions](../../universal/concurrency/race-conditions.md)
> - [Locking Strategies](../../universal/concurrency/locking-strategies.md)

## Python-Specific Concurrency

### The GIL (Global Interpreter Lock)
[Explanation as above]

### Threading vs Multiprocessing vs Asyncio
[Comparison table and decision tree]

### Python Locking Primitives
[Table mapping universal to Python]

### Code Examples
[Python-specific examples]

## Your Project Context
[Detected frameworks and patterns]
```

---

## File 2: `python-testing.md`

### Source Materials
Read:
- `universal/standards/testing/test-pyramid.md`
- `universal/standards/testing/test-doubles.md` (if exists)

### 🚨 CRITICAL: Add tox Test Execution Protocol at Top

**IF `tox.ini` detected in project:**

Add this section FIRST (before all other content):

```markdown
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
```

### Python-Specific Context to Add

#### Testing Frameworks
| Framework | Use Case | Your Project |
|-----------|----------|--------------|
| pytest | Modern, powerful, recommended | ✅ Detected / ❌ Not used |
| unittest | Built-in, class-based | ✅ Detected / ❌ Not used |
| tox | Multi-environment testing | ✅ Detected / ❌ Not used |
| coverage.py | Code coverage measurement | ✅ Detected / ❌ Not used |

#### Pytest Patterns (if detected)
```python
# Fixtures for setup/teardown
import pytest

@pytest.fixture
def database():
    db = create_test_database()
    yield db
    db.cleanup()

def test_user_creation(database):
    user = database.create_user("test@example.com")
    assert user.email == "test@example.com"

# Parametrize for multiple inputs
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_double(input, expected):
    assert double(input) == expected
```

#### Mocking Patterns
```python
from unittest.mock import Mock, patch, MagicMock

# Mock external API
@patch('requests.get')
def test_fetch_data(mock_get):
    mock_get.return_value.json.return_value = {"key": "value"}
    result = fetch_data("https://api.example.com")
    assert result["key"] == "value"

# Mock database
@patch('myapp.database.session')
def test_create_user(mock_session):
    mock_session.add = Mock()
    create_user("test@example.com")
    mock_session.add.assert_called_once()
```

### Project Context Integration
- **If pytest.ini exists**: Reference pytest configuration
- **If tox.ini exists**: Reference tox environments
- **If Django**: Add Django TestCase patterns, fixtures
- **If Flask**: Add Flask test client patterns
- **If FastAPI**: Add TestClient patterns, async test patterns

---

## File 3: `python-dependencies.md`

### Source Materials
Read:
- `universal/standards/architecture/dependency-injection.md` (if exists)

### Python-Specific Context

#### Version Pinning Strategies

| Specifier | Meaning | When to Use | Example |
|-----------|---------|-------------|---------|
| `~=X.Y.Z` | Compatible release (patches OK) | **Recommended default** | `requests~=2.28.0` |
| `==X.Y.Z` | Exact version | Critical stability needs | `fastapi==0.104.1` |
| `>=X.Y.Z,<A.B` | Version range | Broad compatibility | `pydantic>=1.0,<2.0` |
| `>=X.Y.Z` | Minimum version | **Avoid** (non-deterministic) | ❌ Don't use |

#### Package Managers

Detect and document:
- **pip + requirements.txt**: Traditional, simple
- **Poetry + pyproject.toml**: Modern, lock files
- **Pipenv + Pipfile**: Alternative, lock files
- **Conda**: Scientific computing

#### Virtual Environments
```bash
# venv (built-in)
python -m venv venv
source venv/bin/activate

# virtualenv
virtualenv venv

# conda
conda create -n myproject python=3.11
```

### Project Context Integration
- **If pyproject.toml**: Use Poetry/PEP 518 patterns
- **If requirements.txt**: Use pip patterns with inline comments
- **If setup.py**: Use setuptools `install_requires`
- **If Conda detected**: Add conda-specific patterns

---

## File 4: `python-code-quality.md`

### Python-Specific Tools

#### Formatting
- **Black**: Opinionated, zero-config (recommended)
  - Config: `pyproject.toml` → `[tool.black]`
  - Target line length: 88 (Black default) or 100 (common)

- **isort**: Import sorting
  - Config: `.isort.cfg` or `pyproject.toml` → `[tool.isort]`
  - Compatible with Black

#### Linting
- **Pylint**: Comprehensive static analysis (recommended)
  - Config: `pyproject.toml` → `[tool.pylint]`
  - Target score: 10.0/10 (non-negotiable)

- **Flake8**: Alternative linter
  - Config: `.flake8` or `setup.cfg`

#### Type Checking
- **MyPy**: Static type checker (mandatory for typed code)
  - Config: `mypy.ini` or `pyproject.toml` → `[tool.mypy]`
  - Target: 0 errors

#### Type Annotations (Mandatory)
```python
from typing import List, Dict, Optional, Union

def process_data(
    items: List[str],
    config: Dict[str, int],
    timeout: Optional[float] = None
) -> Union[str, None]:
    """Process data with configuration.
    
    :param items: List of items to process
    :param config: Configuration dictionary
    :param timeout: Optional timeout in seconds
    :returns: Processed result or None on failure
    :raises ValueError: If items list is empty
    """
    if not items:
        raise ValueError("Items list cannot be empty")
    # ...
```

#### Docstrings (Mandatory - Sphinx Format)
```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief one-line description.

    Detailed explanation if needed (optional).

    :param param1: Description of param1
    :param param2: Description of param2
    :returns: Description of return value
    :raises ValueError: When param1 is empty
    :raises TypeError: When param2 is negative
    """
```

### Project Context Integration
- **If pyproject.toml has [tool.black]**: Reference existing Black config
- **If .pylintrc exists**: Reference Pylint config
- **If mypy.ini exists**: Reference type checking setup
- **If Sphinx detected**: Emphasize Sphinx docstring format

---

## File 5: `python-documentation.md`

### Python-Specific Documentation

#### Sphinx (Recommended)
- **Config**: `docs/conf.py`
- **Format**: reStructuredText (.rst)
- **Extensions**: autodoc (API docs from docstrings)

#### Docstring Formats
- **Sphinx** (recommended): `:param:`, `:returns:`, `:raises:`
- **Google**: `Args:`, `Returns:`, `Raises:`
- **NumPy**: Scientific computing projects

Example:
```python
def calculate(x: float, y: float, operation: str = "add") -> float:
    """
    Perform arithmetic operation on two numbers.

    This function supports basic arithmetic operations including
    addition, subtraction, multiplication, and division.

    :param x: First number
    :param y: Second number
    :param operation: Operation to perform ("add", "subtract", "multiply", "divide")
    :returns: Result of the operation
    :raises ValueError: If operation is not supported
    :raises ZeroDivisionError: If dividing by zero

    Example usage:
        >>> calculate(10, 5, "add")
        15.0
        >>> calculate(10, 5, "divide")
        2.0
    """
```

### Project Context Integration
- **If docs/conf.py**: Reference Sphinx configuration
- **If using autodoc**: Add guidance on docstring completeness
- **If README.md**: Note markdown vs RST distinction
- **If mkdocs detected**: Add mkdocs-specific patterns

---

## File 6: `python-virtual-environments.md`

### Purpose
Document the **two-venv architecture** required for Python projects using Agent OS.

### Critical Concepts

#### Two Separate Virtual Environments

**1. Agent OS MCP Server venv** (`.praxis-os/venv/`)
- Purpose: Run Agent OS MCP server in isolation
- Dependencies: lancedb, mcp, sentence-transformers, watchdog, honeyhive
- Used by: Cursor's MCP integration (configured in `.cursor/mcp.json`)
- **Never used for project code execution**

**2. Project venv** (`.venv/`, `venv/`, or user-specified)
- Purpose: Run project code, tests, linters
- Dependencies: Project-specific from requirements.txt/pyproject.toml
- Used by: pytest, tox, linters, project scripts
- **This is where AI runs all project commands**

### File Template

```markdown
# Python Virtual Environment Configuration

## Overview

Python projects using Agent OS require **two separate virtual environments**.

## Virtual Environment Architecture

### 1. Agent OS MCP Server venv

**Location**: `.praxis-os/venv/`

**Purpose**: Isolated Python environment for Agent OS MCP server

**Dependencies**:
- lancedb, mcp, sentence-transformers, watchdog, honeyhive (optional)

**Usage**: 
- Automatically created during Agent OS installation
- Used exclusively by `.cursor/mcp.json`
- **Should NOT be used for project code execution**

**Configuration in `.cursor/mcp.json`**:
```json
{
  "mcpServers": {
    "agent-os-rag": {
      "command": "${workspaceFolder}/.praxis-os/venv/bin/python",
      "args": ["-m", "mcp_server"]
    }
  }
}
```

### 2. Project venv

**Location**: {DETECTED_LOCATION or "User-specified"}

**Purpose**: Python environment for project code and dependencies

**Dependencies**: {List detected from requirements.txt/pyproject.toml}

**Usage**:
- Running tests (pytest, tox)
- Running linters (pylint, black, mypy)
- Executing project code

**Detection Strategy**:
1. Check for active venv: `$VIRTUAL_ENV`
2. Check common locations: `.venv/`, `venv/`, `env/`
3. Create new if none exists (with user confirmation)

## Configuration File

Create `.praxis-os/config.json`:
```json
{
  "project": {
    "language": "python",
    "venv_path": "{ABSOLUTE_PATH_TO_PROJECT_VENV}",
    "venv_python": "{ABSOLUTE_PATH_TO_PROJECT_VENV}/bin/python",
    "venv_pytest": "{ABSOLUTE_PATH_TO_PROJECT_VENV}/bin/pytest",
    "test_command": "tox" or "pytest tests/"
  },
  "agent_os": {
    "venv_path": ".praxis-os/venv",
    "mcp_python": "${workspaceFolder}/.praxis-os/venv/bin/python"
  }
}
```

## AI Command Execution Rules

### When to Use Project venv (ALWAYS for project operations)

✅ **Running Tests:**
```bash
# If tox.ini exists
tox

# Otherwise
{PROJECT_VENV}/bin/pytest tests/
```

✅ **Running Linters:**
```bash
{PROJECT_VENV}/bin/pylint src/
{PROJECT_VENV}/bin/black --check .
{PROJECT_VENV}/bin/mypy src/
```

✅ **Executing Project Code:**
```bash
{PROJECT_VENV}/bin/python script.py
```

✅ **Installing Project Dependencies:**
```bash
{PROJECT_VENV}/bin/pip install -r requirements.txt
```

### When to Use Agent OS venv (NEVER directly)

❌ **The AI should NEVER directly use `.praxis-os/venv/`**
- It's managed automatically by Cursor
- Only used for MCP server process

## Troubleshooting

### Issue: Tests fail with import errors
**Cause**: Tests running with Agent OS venv instead of project venv
**Solution**: Verify `.praxis-os/config.json` has correct project venv path

### Issue: MCP server fails to start
**Cause**: Agent OS venv missing/corrupted
**Solution**: Recreate with `python -m venv .praxis-os/venv --clear`

## Best Practices

1. **Never mix environments**: Keep Agent OS and project dependencies separate
2. **Use absolute paths**: Store absolute paths in config for reliability
3. **Document in README**: Explain two-venv architecture to team
4. **Git ignore both**: Add both `.praxis-os/venv/` and project venv to `.gitignore`
```

### Installation Detection Steps

When generating this file:

1. **Check for active venv:**
   ```python
   import os
   active_venv = os.getenv('VIRTUAL_ENV')
   ```

2. **Check common locations:**
   ```python
   from pathlib import Path
   for venv_name in ['.venv', 'venv', 'env']:
       if (Path.cwd() / venv_name).exists():
           project_venv = Path.cwd() / venv_name
   ```

3. **Prompt for creation if none found:**
   - Ask user if they want to create .venv
   - Or ask for path to existing venv

4. **Create `.praxis-os/config.json`:**
   - Store both venv paths (absolute)
   - Store Python/pytest/pip executable paths
   - Determine test_command ("tox" if tox.ini exists, otherwise "pytest tests/")

---

## Installation Steps You Should Follow

1. **Analyze target Python project**
   - Detect pytest, unittest, tox
   - Detect Black, Pylint, MyPy
   - Detect Sphinx, mkdocs
   - Detect frameworks (Django, Flask, FastAPI)
   - Detect async usage
   - Detect Celery, message queues

2. **Read universal standards**
   - Read all relevant files from `universal/standards/`

3. **Generate Python-specific standards**
   - Use templates above
   - Apply Python context
   - Integrate project-specific patterns
   - Include code examples

4. **Create files**
   - `.praxis-os/standards/development/python-concurrency.md`
   - `.praxis-os/standards/development/python-testing.md` (with tox protocol at top if tox.ini detected)
   - `.praxis-os/standards/development/python-dependencies.md`
   - `.praxis-os/standards/development/python-code-quality.md`
   - `.praxis-os/standards/development/python-documentation.md`
   - `.praxis-os/standards/development/python-virtual-environments.md` (two-venv architecture)

5. **Cross-reference universal standards**
   - Link back to `../../universal/standards/` files
   - Show relationship between universal and Python-specific

6. **Include project context sections**
   - "Your Project Context" sections showing detected patterns
   - Examples from actual codebase (if available)

---

**Result:** Python-specific standards that reference universal CS fundamentals while providing Python-specific implementations tailored to the target project.
