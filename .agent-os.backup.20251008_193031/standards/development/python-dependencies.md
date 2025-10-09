# Python Dependencies Standards
# Generated for: agent-os-enhanced

## Universal Dependency Principles

> **See universal standards:**
> - [Dependency Injection](../../universal/architecture/dependency-injection.md)

This document applies universal dependency management principles to Python-specific contexts.

---

## Version Pinning Strategies

| Specifier | Meaning | When to Use | Example |
|-----------|---------|-------------|---------|
| `~=X.Y.Z` | **Compatible release** (patches OK) | ✅ **Recommended default** | `lancedb~=0.25.0` |
| `==X.Y.Z` | **Exact version** | Critical stability, security | `cryptography==41.0.7` |
| `>=X.Y.Z,<A.B` | **Version range** | Broad compatibility | `pydantic>=1.0,<2.0` |
| `>=X.Y.Z` | **Minimum version** | ❌ **Avoid** (non-deterministic) | ❌ `requests>=2.0` |

### Explanation

- **`~=X.Y.Z`** (Compatible Release): Allows patch versions (e.g., `~=0.25.0` → `0.25.1` OK, `0.26.0` NOT OK)
- **`==X.Y.Z`** (Exact): Pins to exact version, no flexibility
- **`>=X,<Y`** (Range): Useful for major version boundaries (Python 2→3, Pydantic 1→2)
- **`>=X`** (Minimum): Dangerous - leads to non-reproducible builds

---

## Package Managers

### Your Project: pip + requirements.txt

✅ **Detected**: `mcp_server/requirements.txt`

#### Current Dependencies

```txt
# Vector database for RAG
lancedb~=0.25.0          # ✅ Good: Compatible release specifier

# Model Context Protocol
mcp>=1.0.0               # ⚠️ Consider: ~=1.0.0 for stability

# Local embeddings
sentence-transformers>=2.0.0  # ⚠️ Consider: ~=2.0.0

# File watching
watchdog>=3.0.0          # ⚠️ Consider: ~=3.0.0

# Observability (optional)
honeyhive>=0.1.0         # ⚠️ Consider: ~=0.1.0
```

#### Recommendations

```txt
# Agent OS MCP/RAG Server Dependencies

# Vector database for RAG (locked to 0.25.x for stability)
lancedb~=0.25.0

# Model Context Protocol (locked to 1.x series)
mcp~=1.0.0

# Local embeddings (locked to 2.x series)
sentence-transformers~=2.0.0

# File watching for automatic index rebuild
watchdog~=3.0.0

# Optional: Observability
honeyhive~=0.1.0

# Optional: OpenAI embeddings for higher quality
# openai~=1.0.0
```

---

## Virtual Environments

### Creating Virtual Environments

```bash
# venv (built-in, recommended)
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Verify activation
which python  # Should point to venv/bin/python

# Install dependencies
pip install -r mcp_server/requirements.txt
```

### Deactivation

```bash
deactivate
```

---

## Dependency Installation Patterns

### For Development

```bash
# Install in editable mode for local development
pip install -e .

# Install with dev dependencies
pip install -r requirements-dev.txt
```

### For Production

```bash
# Install exact versions from lock file
pip install -r requirements.txt --no-deps

# Verify installed versions
pip freeze > installed.txt
diff requirements.txt installed.txt
```

---

## Dependency Security

### Vulnerability Scanning

```bash
# Install safety
pip install safety

# Check for known vulnerabilities
safety check --file=mcp_server/requirements.txt

# Update vulnerable packages
pip install --upgrade package-name
```

### Regular Updates

```bash
# Show outdated packages
pip list --outdated

# Update specific package
pip install --upgrade lancedb

# Update all packages (careful!)
pip list --outdated | cut -d ' ' -f1 | xargs -n1 pip install -U
```

---

## Dependency Injection in Python

### Pattern 1: Constructor Injection (Recommended)

```python
from pathlib import Path
from typing import Optional

class RAGEngine:
    """RAG engine with injected dependencies."""
    
    def __init__(
        self,
        index_path: Path,
        standards_path: Path,
        embedder: Optional['Embedder'] = None
    ):
        """
        Initialize RAG engine with dependencies.
        
        :param index_path: Path to vector index
        :param standards_path: Path to standards directory
        :param embedder: Optional custom embedder (defaults to SentenceTransformer)
        """
        self.index_path = index_path
        self.standards_path = standards_path
        self.embedder = embedder or self._create_default_embedder()
    
    def _create_default_embedder(self):
        """Create default embedder."""
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer('all-MiniLM-L6-v2')

# Usage
engine = RAGEngine(
    index_path=Path(".agent-os/.cache/index"),
    standards_path=Path(".agent-os/standards")
)

# Testing with mock embedder
mock_embedder = MockEmbedder()
test_engine = RAGEngine(
    index_path=test_path,
    standards_path=test_standards,
    embedder=mock_embedder  # Injected for testing
)
```

### Pattern 2: Factory Functions

```python
def create_rag_engine(
    project_root: Path,
    use_openai_embeddings: bool = False
) -> RAGEngine:
    """Factory function for creating RAG engine with appropriate config."""
    index_path = project_root / ".agent-os" / ".cache" / "index"
    standards_path = project_root / ".agent-os" / "standards"
    
    if use_openai_embeddings:
        from openai import OpenAI
        embedder = OpenAIEmbedder(client=OpenAI())
    else:
        embedder = SentenceTransformerEmbedder()
    
    return RAGEngine(
        index_path=index_path,
        standards_path=standards_path,
        embedder=embedder
    )
```

### Pattern 3: Protocol-Based Injection (Python 3.8+)

```python
from typing import Protocol, List

class Embedder(Protocol):
    """Protocol for embedding providers."""
    
    def embed(self, text: str) -> List[float]:
        """Embed text into vector."""
        ...

class SentenceTransformerEmbedder:
    """Concrete implementation using sentence-transformers."""
    
    def embed(self, text: str) -> List[float]:
        # Implementation
        return [0.1, 0.2, ...]

class OpenAIEmbedder:
    """Concrete implementation using OpenAI."""
    
    def embed(self, text: str) -> List[float]:
        # Implementation
        return [0.3, 0.4, ...]

def process_with_embedder(embedder: Embedder, text: str):
    """Function accepts any Embedder protocol implementation."""
    return embedder.embed(text)
```

---

## Your Project Context: agent-os-enhanced

### Current State

✅ **Package Manager**: pip + requirements.txt  
✅ **Dependencies**: Minimal, well-chosen  
❌ **No requirements-dev.txt**: Should separate dev dependencies  
❌ **No lock file**: Consider adding for reproducibility  
❌ **Version specifiers**: Could be more restrictive (`~=` instead of `>=`)

### Recommendations

#### 1. Split Dependencies

**`mcp_server/requirements.txt`** (production):
```txt
lancedb~=0.25.0
mcp~=1.0.0
sentence-transformers~=2.0.0
watchdog~=3.0.0
```

**`requirements-dev.txt`** (development):
```txt
-r mcp_server/requirements.txt

# Testing
pytest~=7.0
pytest-cov~=4.0
pytest-mock~=3.0
pytest-asyncio~=0.21.0

# Code Quality
black~=23.0
pylint~=2.17
mypy~=1.0
isort~=5.12

# Documentation
sphinx~=7.0
sphinx-rtd-theme~=1.3

# Utilities
hypothesis~=6.0  # Property-based testing
```

#### 2. Add Installation Instructions to README

```markdown
## Installation

### Production
```bash
pip install -r mcp_server/requirements.txt
```

### Development
```bash
pip install -r requirements-dev.txt
pip install -e .  # Editable install
```

#### 3. Add Dependency Validation Script

**`scripts/check_deps.py`**:
```python
#!/usr/bin/env python3
"""Validate dependency versions and security."""

import subprocess
import sys

def check_security():
    """Check for known vulnerabilities."""
    result = subprocess.run(
        ["safety", "check", "--file=mcp_server/requirements.txt"],
        capture_output=True
    )
    if result.returncode != 0:
        print("⚠️  Security vulnerabilities found!")
        print(result.stdout.decode())
        return False
    print("✅ No known vulnerabilities")
    return True

def check_outdated():
    """Check for outdated packages."""
    result = subprocess.run(
        ["pip", "list", "--outdated"],
        capture_output=True
    )
    outdated = result.stdout.decode()
    if outdated.strip():
        print("⚠️  Outdated packages:")
        print(outdated)
    else:
        print("✅ All packages up to date")

if __name__ == "__main__":
    check_security()
    check_outdated()
```

---

## Common Dependency Issues

### Issue 1: Dependency Conflicts

```bash
# Problem: Conflicting version requirements
ERROR: package-a 1.0 requires foo>=2.0
ERROR: package-b 1.0 requires foo<2.0

# Solution: Use pip's dependency resolver
pip install --upgrade pip  # Ensure pip 20.3+
pip install package-a package-b  # Resolver finds compatible versions
```

### Issue 2: Missing System Dependencies

```bash
# Problem: Package requires system libraries
ERROR: Could not build wheels for lancedb

# Solution (macOS):
brew install rust cmake

# Solution (Ubuntu):
sudo apt-get install build-essential cmake
```

### Issue 3: Circular Dependencies

```python
# Problem: Module A imports B, B imports A
# file_a.py
from file_b import ClassB

# file_b.py
from file_a import ClassA  # Circular!

# Solution: Use TYPE_CHECKING
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from file_a import ClassA  # Import only for type hints
```

---

## References

- [Python Packaging User Guide](https://packaging.python.org/)
- [pip documentation](https://pip.pypa.io/)
- [PEP 440 - Version Identification](https://peps.python.org/pep-0440/)
- [Universal Dependency Injection](../../universal/architecture/dependency-injection.md)

---

**Generated for agent-os-enhanced. Consider adding requirements-dev.txt and tightening version specifiers.**
