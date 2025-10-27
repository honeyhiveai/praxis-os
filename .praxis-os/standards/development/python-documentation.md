# Python Documentation Standards
# Generated for: praxis-os

## Universal Documentation Principles

> **See universal standards:**
> - [Code Comments](../../universal/documentation/code-comments.md)
> - [API Documentation](../../universal/documentation/api-documentation.md)
> - [README Templates](../../universal/documentation/readme-templates.md)

This document applies universal documentation principles to Python-specific contexts.

---

## Documentation Tools for Python

### Your Project Status

| Tool | Purpose | Status | Recommendation |
|------|---------|--------|----------------|
| **Sphinx** | API documentation | ❌ Not configured | Add for auto-generated docs |
| **mkdocs** | Markdown documentation | ❌ Not configured | Alternative to Sphinx |
| **pydoc** | Built-in doc viewer | ✅ Always available | Use for quick reference |
| **README.md** | Project overview | ✅ Exists | Enhance with more details |

---

## Docstring Formats

### Sphinx Format (Recommended)

**Why:** Industry standard, excellent tooling, autodoc integration

```python
def search_standards(
    query: str,
    n_results: int = 5,
    filters: Optional[Dict[str, str]] = None
) -> List[SearchResult]:
    """
    Search the Agent OS standards using semantic search.
    
    Performs vector similarity search over the indexed standards
    and returns the most relevant chunks based on the query.
    
    :param query: Natural language search query
    :param n_results: Maximum number of results to return (default: 5)
    :param filters: Optional metadata filters for narrowing results
    :type query: str
    :type n_results: int
    :type filters: Optional[Dict[str, str]]
    :returns: List of search results with content and metadata
    :rtype: List[SearchResult]
    :raises ValueError: If query is empty or n_results is negative
    :raises RuntimeError: If the index is not initialized
    
    Example:
        >>> results = search_standards("race conditions", n_results=3)
        >>> for result in results:
        ...     print(result.content)
        
    .. note::
        The search uses local embeddings by default (sentence-transformers).
        For higher quality, configure OpenAI embeddings.
    
    .. warning::
        Large n_results values (>50) may impact performance.
    """
    pass
```

### Google Format (Alternative)

```python
def search_standards(query, n_results=5, filters=None):
    """Search the Agent OS standards using semantic search.
    
    Performs vector similarity search over the indexed standards
    and returns the most relevant chunks based on the query.
    
    Args:
        query (str): Natural language search query
        n_results (int, optional): Maximum number of results. Defaults to 5.
        filters (Dict[str, str], optional): Metadata filters. Defaults to None.
    
    Returns:
        List[SearchResult]: List of search results with content and metadata
    
    Raises:
        ValueError: If query is empty or n_results is negative
        RuntimeError: If the index is not initialized
    
    Example:
        >>> results = search_standards("race conditions", n_results=3)
        >>> for result in results:
        ...     print(result.content)
    """
    pass
```

### NumPy Format (Scientific)

```python
def search_standards(query, n_results=5, filters=None):
    """
    Search the Agent OS standards using semantic search.
    
    Parameters
    ----------
    query : str
        Natural language search query
    n_results : int, optional
        Maximum number of results to return (default is 5)
    filters : Dict[str, str], optional
        Metadata filters for narrowing results (default is None)
    
    Returns
    -------
    List[SearchResult]
        List of search results with content and metadata
    
    Raises
    ------
    ValueError
        If query is empty or n_results is negative
    RuntimeError
        If the index is not initialized
    
    Examples
    --------
    >>> results = search_standards("race conditions", n_results=3)
    >>> for result in results:
    ...     print(result.content)
    """
    pass
```

---

## Sphinx Documentation Setup

### Installation

```bash
pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints
```

### Project Structure

```
praxis-os/
├── docs/
│   ├── source/
│   │   ├── conf.py           # Sphinx configuration
│   │   ├── index.rst         # Documentation home
│   │   ├── api/
│   │   │   ├── rag_engine.rst
│   │   │   ├── workflow_engine.rst
│   │   │   └── mcp_tools.rst
│   │   ├── guides/
│   │   │   ├── installation.rst
│   │   │   └── usage.rst
│   │   └── _static/          # CSS, images
│   ├── Makefile
│   └── make.bat              # Windows
```

### Configuration (`docs/source/conf.py`)

```python
"""Sphinx configuration for Agent OS Enhanced."""

import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

# Project information
project = 'Agent OS Enhanced'
copyright = '2025, Agent OS Team'
author = 'Agent OS Team'
version = '1.0'
release = '1.0.0'

# Extensions
extensions = [
    'sphinx.ext.autodoc',           # Auto-generate docs from docstrings
    'sphinx.ext.napoleon',          # Support Google/NumPy formats
    'sphinx.ext.viewcode',          # Add source code links
    'sphinx.ext.intersphinx',       # Link to other docs
    'sphinx_autodoc_typehints',     # Better type hint rendering
]

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

# Theme
html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'navigation_depth': 4,
    'collapse_navigation': False,
}

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
}
```

### Building Documentation

```bash
# Initialize Sphinx (first time only)
cd docs
sphinx-quickstart

# Build HTML documentation
make html

# View documentation
open build/html/index.html

# Build PDF (requires LaTeX)
make latexpdf

# Clean build
make clean
```

---

## API Documentation with Autodoc

### Module Documentation

**`docs/source/api/rag_engine.rst`**:
```rst
RAG Engine
==========

.. automodule:: mcp_server.rag_engine
   :members:
   :undoc-members:
   :show-inheritance:

RAGEngine Class
---------------

.. autoclass:: mcp_server.rag_engine.RAGEngine
   :members:
   :special-members: __init__
   :inherited-members:
```

### Automatic Documentation Generation

```bash
# Generate .rst files for all modules
sphinx-apidoc -o docs/source/api mcp_server/

# Build documentation
cd docs
make html
```

---

## README.md Best Practices

### Current README Enhancement

Your current README is good! Here are some enhancements:

```markdown
# Agent OS Enhanced - Portable Multi-Agent Development Framework

**A portable Agent OS implementation with MCP RAG, sub-agents, and universal CS fundamentals.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## 🎯 Overview

Agent OS Enhanced is a portable development framework that combines:
- **Universal CS Fundamentals**: Timeless patterns applicable to any language
- **Language-Specific Generation**: LLM generates tailored guidance per project
- **MCP RAG Server**: Semantic search over standards with 90% context reduction
- **Specialized Sub-Agents**: Design validation, concurrency analysis, test generation
- **Conversational Installation**: Cursor agent installs and configures everything

## 📚 Documentation

- [Installation Guide](installation-guide.md)
- [Contributing Guidelines](CONTRIBUTING.md)
- [API Documentation](https://your-docs-site.com) <!-- Add when Sphinx docs are live -->
- [Sub-Agent Architecture](specs/sub-agent-architecture.md)

## 🚀 Quick Start

```bash
# In Cursor IDE, open your project and say:
"Install Agent OS from github.com/honeyhiveai/praxis-os"

# The Cursor agent will:
# 1. Analyze your project (detect language, frameworks)
# 2. Copy universal standards (static CS fundamentals)
# 3. Generate language-specific standards (tailored to your project)
# 4. Install MCP server locally (.praxis-os/mcp_server/)
# 5. Configure Cursor (.cursor/mcp.json)
# 6. Build RAG index
```

## 🔧 Development Setup

```bash
# Clone repository
git clone https://github.com/honeyhiveai/praxis-os.git
cd praxis-os

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r mcp_server/requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt  # TODO: Create this file

# Run tests
pytest tests/  # TODO: Add tests

# Build documentation
cd docs && make html  # TODO: Set up Sphinx
```

## 📖 Examples

### Using MCP Tools After Installation

```python
# Search standards
"What are the concurrency best practices?"
# → Queries RAG, returns language-specific guidance

# Validate designs
"Review this rate limiter design"
# → design_validator() sub-agent provides adversarial review

# Analyze concurrency
"Is this code thread-safe?"
# → concurrency_analyzer() sub-agent performs analysis
```

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - Use freely in any project. See [LICENSE](LICENSE) for details.

## 🙏 Credits

- **Foundation**: [Builder Methods Agent OS](https://buildermethods.com/agent-os) by Brian Casel
- **Evolution**: HoneyHive's LLM Workflow Engineering methodology
- **Implementation**: MCP/RAG architecture with specialized sub-agents

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/honeyhiveai/praxis-os/issues)
- **Discussions**: [GitHub Discussions](https://github.com/honeyhiveai/praxis-os/discussions)
```

---

## Code Comments Best Practices

### When to Comment

✅ **DO comment:**
- Complex algorithms
- Non-obvious business logic
- Workarounds for bugs/limitations
- Performance-critical sections
- Security-sensitive code

❌ **DON'T comment:**
- Obvious code (`x = x + 1  # Increment x`)
- Self-explanatory function names
- Redundant with docstrings

### Good Comments

```python
# Good: Explains WHY, not WHAT
def calculate_similarity(vec1, vec2):
    """Calculate cosine similarity between vectors."""
    # Use numpy for vectorized operations (10x faster than pure Python)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

# Good: Documents workaround
def process_file(path):
    """Process markdown file."""
    # Note: We use utf-8-sig to handle Windows BOM characters
    # See issue #123 for context
    with open(path, encoding='utf-8-sig') as f:
        return f.read()

# Good: Explains complex logic
def should_rebuild_index(last_rebuild_time):
    """Determine if index needs rebuilding."""
    # Rebuild if:
    # 1. More than 5 minutes since last rebuild (debounce)
    # 2. AND standards files have been modified
    # This prevents excessive rebuilds during rapid file edits
    if time.time() - last_rebuild_time < 300:
        return False
    return has_modified_files()
```

### Bad Comments

```python
# Bad: States the obvious
x = x + 1  # Increment x

# Bad: Redundant with function name
def get_user_by_id(user_id):
    """Get user by ID."""  # Docstring adds no value
    pass

# Bad: Outdated comment (code changed, comment didn't)
# Calculate average (WRONG: Now calculates median!)
def calculate_median(values):
    return statistics.median(values)
```

---

## Your Project Context: praxis-os

### Current State

✅ **README.md**: Exists with good structure  
❌ **No Sphinx documentation**  
❌ **No API docs**  
❌ **No usage examples**  
❌ **No changelog** (though CHANGELOG.md exists in mcp_server)

### Recommendations

1. **Set up Sphinx:**
   ```bash
   pip install sphinx sphinx-rtd-theme
   cd docs
   sphinx-quickstart
   ```

2. **Add API documentation:**
   - Document RAG engine
   - Document workflow engine
   - Document MCP tools
   - Document sub-agents

3. **Create usage guide:**
   - Installation walkthrough
   - Configuration options
   - MCP tool usage examples
   - Troubleshooting

4. **Add inline documentation:**
   - Complex logic in `rag_engine.py`
   - File watcher logic in `agent_os_rag.py`
   - Workflow state machine

5. **Create CHANGELOG.md at root:**
   - Track repository releases
   - Link to mcp_server/CHANGELOG.md for server changes

---

## Documentation Checklist

Before releasing a feature:

- [ ] All public functions have docstrings
- [ ] All classes have docstrings
- [ ] Complex logic has inline comments
- [ ] README updated if user-facing changes
- [ ] API docs regenerated with Sphinx
- [ ] Examples added/updated
- [ ] CHANGELOG.md updated

---

## References

- [Sphinx documentation](https://www.sphinx-doc.org/)
- [ReadTheDocs tutorial](https://docs.readthedocs.io/en/stable/tutorial/)
- [PEP 257 - Docstring Conventions](https://peps.python.org/pep-0257/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Universal Code Comments Standard](../../universal/documentation/code-comments.md)
- [Universal API Documentation Standard](../../universal/documentation/api-documentation.md)

---

**Generated for praxis-os. Set up Sphinx for professional API documentation.**
