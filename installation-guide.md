# Installation Guide for Cursor Agent

**Instructions for the Cursor AI Agent on how to install Agent OS Enhanced in a target project.**

---

## Overview

When a user says:
> "Install Agent OS from github.com/honeyhiveai/agent-os-enhanced"

You (the Cursor agent) will:
1. Clone/read this repository
2. Detect project language and characteristics
3. Generate language-specific standards
4. Install MCP server with isolated Python venv
5. Configure Cursor
6. Build RAG index
7. Analyze project tooling and provide recommendations

---

## Step 1: Clone or Read Repository

```python
# If the user provides a git URL
git_url = "github.com/honeyhiveai/agent-os-enhanced"

# Options:
# A) Clone to temp directory
# B) Read via GitHub API
# C) User provides local path

# Read key files:
- .cursorrules (universal, 46 lines)
- universal/standards/** (all markdown files)
- language-instructions/{detected_language}.md
- mcp_server/** (all Python files)
```

---

## Step 2: Analyze Target Project

### Detect Language

Check for language indicators:

```python
def detect_language(project_root):
    # Python
    if exists("pyproject.toml") or exists("setup.py") or exists("requirements.txt"):
        return "python"
    
    # Go
    if exists("go.mod"):
        return "go"
    
    # JavaScript/TypeScript
    if exists("package.json"):
        if exists("tsconfig.json"):
            return "typescript"
        return "javascript"
    
    # Rust
    if exists("Cargo.toml"):
        return "rust"
    
    # Java
    if exists("pom.xml") or exists("build.gradle"):
        return "java"
    
    # C#
    if exists("*.csproj"):
        return "csharp"
    
    # Unknown - prompt user
    return prompt_user_for_language()
```

### Detect Project Characteristics (Python Example)

**Note:** This is lightweight detection for standard generation context only.
Detailed tooling analysis happens in Step 7 (after MCP server is running).

```python
def detect_python_characteristics(project_root):
    """
    Detect basic project characteristics for standard generation.
    NOT full tooling analysis (that happens in Step 7).
    """
    detected = {
        "language": "python",
        "frameworks": [],
        "async": False,
    }
    
    # Detect frameworks (affects standard examples)
    requirements_files = ["requirements.txt", "pyproject.toml", "Pipfile"]
    for req_file in requirements_files:
        if exists(req_file):
            content = read(req_file)
            if "django" in content:
                detected["frameworks"].append("django")
            if "flask" in content:
                detected["frameworks"].append("flask")
            if "fastapi" in content:
                detected["frameworks"].append("fastapi")
    
    # Detect async usage (affects concurrency standard)
    if scan_codebase_for("async def"):
        detected["async"] = True
    
    return detected
```

---

## Step 3: Generate Language-Specific Standards

### Read Language Instructions

```python
language = detected["language"]
instructions_file = f"language-instructions/{language}.md"
instructions = read(instructions_file)
```

### Generate Standards Using Instructions

**IMPORTANT:** Generate standards for **universal principles applied to the language**.
Do NOT create tooling configuration files (tox.ini, package.json, etc.).

For each standard file specified in instructions:

```python
# Example: Generating python-concurrency.md

# 1. Read universal standards
race_conditions = read("universal/standards/concurrency/race-conditions.md")
locking_strategies = read("universal/standards/concurrency/locking-strategies.md")

# 2. Apply language-specific context from instructions
python_context = {
    "gil_explanation": "...",  # From instructions
    "threading_vs_multiprocessing": "...",  # From instructions
    "locking_primitives": {...},  # From instructions
    "code_examples": [...],  # From instructions
}

# 3. Integrate project-specific patterns (if detected)
project_patterns = {
    "async_detected": detected["async"],
    "frameworks": detected["frameworks"],
}

# 4. Generate the standard file
generated_content = f"""
# Python Concurrency Standards
# Generated for: {project_name}

## Universal Concurrency Principles
> See universal standards:
> - [Race Conditions](../../universal/concurrency/race-conditions.md)
> - [Locking Strategies](../../universal/concurrency/locking-strategies.md)

## Python-Specific Concurrency

### The GIL (Global Interpreter Lock)
{python_context["gil_explanation"]}

### Threading vs Multiprocessing vs Asyncio
{python_context["threading_vs_multiprocessing"]}

### Python Locking Primitives
{python_context["locking_primitives"]}

### Code Examples
{python_context["code_examples"]}

## Your Project Context
{format_project_patterns(project_patterns)}
"""

# 5. Write to target project
write(".agent-os/standards/development/python-concurrency.md", generated_content)
```

Repeat for all standard files specified in language instructions.

**Standards to generate (Python example):**
- python-testing.md (universal principles → pytest, unittest, tox)
- python-concurrency.md (universal principles → GIL, threading, asyncio)
- python-dependencies.md (universal principles → pip, poetry, venv)
- python-code-quality.md (universal principles → PEP8, type hints, linting)
- python-documentation.md (universal principles → docstrings, Sphinx)

---

## Step 4: Install Files in Target Project

### Create Directory Structure

```python
create_directory(".agent-os/standards/universal/")
create_directory(".agent-os/standards/development/")
create_directory(".agent-os/standards/ai-assistant/")
create_directory(".agent-os/usage/")              # NEW: Agent OS usage documentation
create_directory(".agent-os/product/")
create_directory(".agent-os/specs/")
create_directory(".agent-os/mcp_server/")
create_directory(".agent-os/.cache/")
create_directory(".cursor/")
```

### Copy Universal Standards

```python
# Option A: Symlink (more efficient, stays in sync)
symlink("agent-os-enhanced/universal/standards", ".agent-os/standards/universal")

# Option B: Copy (more portable, project owns the content)
copy_recursively("agent-os-enhanced/universal/standards", ".agent-os/standards/universal")
```

### Copy Agent OS Usage Documentation

```python
# Copy Agent OS usage documentation
# These docs explain how to use Agent OS (creating specs, operating model, MCP usage)
# Separate from project-specific documentation standards

copy("agent-os-enhanced/universal/usage/creating-specs.md", ".agent-os/usage/")
copy("agent-os-enhanced/universal/usage/operating-model.md", ".agent-os/usage/")
copy("agent-os-enhanced/universal/usage/mcp-usage-guide.md", ".agent-os/usage/")

# File watcher will auto-index these, making them searchable via MCP
# Example query: "How do I create a spec?"
```

### Copy MCP Server

```python
copy_recursively("agent-os-enhanced/mcp_server", ".agent-os/mcp_server")
```

### Copy Build Scripts

```python
# Copy RAG index builder script
create_directory(".agent-os/scripts/")
copy("agent-os-enhanced/.agent-os/scripts/build_rag_index.py", ".agent-os/scripts/")
```

### Create Python Virtual Environment for MCP Server

**CRITICAL:** MCP server needs isolated Python environment.

```python
# Create venv for Agent OS MCP server
run_command("python3 -m venv .agent-os/venv")

# Install MCP server dependencies
run_command(".agent-os/venv/bin/pip install -r .agent-os/mcp_server/requirements.txt")
```

**Why separate venv?**
- Isolates Agent OS dependencies from project dependencies
- Prevents version conflicts
- Project can use different Python version/tools

### Copy .cursorrules

```python
copy("agent-os-enhanced/.cursorrules", ".cursorrules")
```

### Create .cursor/mcp.json

```json
{
  "mcpServers": {
    "agent-os-rag": {
      "command": "${workspaceFolder}/.agent-os/venv/bin/python",
      "args": [
        "-m",
        "mcp_server.agent_os_rag"
      ],
      "env": {
        "PROJECT_ROOT": "${workspaceFolder}",
        "PYTHONPATH": "${workspaceFolder}/.agent-os",
        "PYTHONUNBUFFERED": "1"
      },
      "autoApprove": [
        "search_standards",
        "get_current_phase",
        "get_workflow_state"
      ]
    }
  }
}
```

**Key changes:**
- Uses `.agent-os/venv/bin/python` (isolated environment)
- Uses `-m mcp_server.agent_os_rag` (module syntax)
- Adds `PYTHONUNBUFFERED=1` (for logs)

### Update .gitignore

```python
append_to_gitignore("""
# Agent OS
.agent-os/.cache/
.agent-os/venv/
.agent-os/mcp_server/__pycache__/
""")
```

---

## Step 5: Build RAG Index

```python
# Run index builder using Agent OS venv Python
run_command(".agent-os/venv/bin/python .agent-os/scripts/build_rag_index.py")

# This will:
# 1. Find all .md files in .agent-os/standards/ and .agent-os/usage/
# 2. Chunk them appropriately
# 3. Generate embeddings (using local sentence-transformers)
# 4. Store in LanceDB at .agent-os/.cache/vector_index/
```

---

## Step 6: Enable MCP Server in Cursor

**Activate the MCP server without restarting.**

```
✅ Agent OS files installed!
✅ RAG index built!

🔄 Next step: Enable MCP Server

To activate the server:
1. Open Cursor Settings (Cmd/Ctrl + ,)
2. Navigate to: Features → Model Context Protocol
3. Find "agent-os-rag" server
4. Click "Enable" or ensure it's toggled on

The MCP server will start automatically. You'll see:
- MCP tools available in your chat
- File watcher monitoring .agent-os/ for changes
- RAG engine ready for queries

Once enabled, I'll continue with project analysis.
```

**Alternative (if user prefers):** User can restart Cursor instead, which also activates MCP servers.

---

## Step 7: Project Tooling Analysis & Recommendations

**After Cursor restarts and MCP server is running**, perform interactive project analysis.

### Objective

Analyze existing tooling and provide recommendations (documentation-only, no file creation).

### Process

Have a conversational analysis with the user:

```
Agent: "Now that Agent OS is installed, let me analyze your project's tooling setup..."

[Agent performs detection - see detection logic below]

Agent: "Analysis complete! Here's what I found:

📊 Python Tooling Analysis

Detected:
✅ Test runner: pytest (pytest.ini)
✅ Dependency manager: pip (requirements.txt)

Missing:
❌ Code formatter (critical)
❌ Linter (important)
❌ Type checker (recommended)

Would you like recommendations on tooling setup?"

User: "Yes, what do you suggest?"

Agent: "Based on community best practices:

**Formatter:** black + isort
- Most popular Python formatters
- Zero-config, opinionated
- Template: .agent-os/templates/python/pyproject.toml

**Linter:** pylint OR ruff
- pylint: comprehensive analysis
- ruff: faster, all-in-one tool
- Template: .agent-os/templates/python/.pylintrc

**Type checker:** mypy
- Most mature Python type checker
- Template: .agent-os/templates/python/mypy.ini

Shall I document these findings and recommendations?"

User: "Yes, and we'll add ruff later"

Agent: "Creating tooling analysis document..."
[Creates .agent-os/standards/development/python-tooling-analysis.md]

Agent: "✅ Documented at .agent-os/standards/development/python-tooling-analysis.md

📁 Reference templates available at .agent-os/templates/python/
📖 Best practices guide: .agent-os/usage/python-best-practices.md

The file watcher detected the new file and is updating the RAG index (~30 seconds).
Your tooling analysis is now searchable via MCP!"
```

### Detection Logic (Python Example)

```python
def analyze_python_tooling(project_root):
    """
    Detect existing Python tooling configuration.
    Returns findings and recommendations.
    """
    findings = {
        "test_runner": detect_test_runner(project_root),
        "formatter": detect_formatter(project_root),
        "linter": detect_linter(project_root),
        "type_checker": detect_type_checker(project_root),
        "dependency_manager": detect_dependency_manager(project_root),
    }
    
    # Identify gaps
    gaps = []
    if not findings["test_runner"]:
        gaps.append({
            "category": "test_runner",
            "severity": "critical",
            "recommendation": "pytest with tox wrapper"
        })
    if not findings["formatter"]:
        gaps.append({
            "category": "formatter",
            "severity": "critical",
            "recommendation": "black + isort"
        })
    if not findings["linter"]:
        gaps.append({
            "category": "linter",
            "severity": "important",
            "recommendation": "pylint OR ruff"
        })
    if not findings["type_checker"]:
        gaps.append({
            "category": "type_checker",
            "severity": "recommended",
            "recommendation": "mypy"
        })
    
    return {
        "findings": findings,
        "gaps": gaps,
        "completeness_score": calculate_score(findings)
    }

def detect_test_runner(project_root):
    """Detect test runner configuration."""
    if Path("tox.ini").exists():
        return {"tool": "tox", "config": "tox.ini"}
    if Path("pytest.ini").exists():
        return {"tool": "pytest", "config": "pytest.ini"}
    if Path("Makefile").exists() and "test:" in Path("Makefile").read_text():
        return {"tool": "make", "config": "Makefile"}
    return None

def detect_formatter(project_root):
    """Detect code formatter."""
    pyproject = Path("pyproject.toml")
    if pyproject.exists():
        content = pyproject.read_text()
        if "tool.black" in content:
            return {"tool": "black", "config": "pyproject.toml"}
        if "tool.ruff" in content and "format" in content:
            return {"tool": "ruff", "config": "pyproject.toml"}
    return None

def detect_linter(project_root):
    """Detect linter configuration."""
    if Path(".pylintrc").exists():
        return {"tool": "pylint", "config": ".pylintrc"}
    pyproject = Path("pyproject.toml")
    if pyproject.exists():
        content = pyproject.read_text()
        if "tool.pylint" in content:
            return {"tool": "pylint", "config": "pyproject.toml"}
        if "tool.ruff" in content and "lint" in content:
            return {"tool": "ruff", "config": "pyproject.toml"}
    return None

def detect_type_checker(project_root):
    """Detect type checker."""
    if Path("mypy.ini").exists():
        return {"tool": "mypy", "config": "mypy.ini"}
    pyproject = Path("pyproject.toml")
    if pyproject.exists() and "tool.mypy" in pyproject.read_text():
        return {"tool": "mypy", "config": "pyproject.toml"}
    return None
```

### Generate Tooling Analysis Document

Create: `.agent-os/standards/development/{language}-tooling-analysis.md`

**Example content (with gaps):**

```markdown
# Python Tooling Analysis

**Analysis Date:** 2025-10-06  
**Completeness Score:** 40% ⚠️

---

## Detected Tooling

| Category | Tool | Status |
|----------|------|--------|
| **Test Runner** | pytest | ✅ Detected |
| **Formatter** | None | ❌ Missing |
| **Linter** | None | ❌ Missing |
| **Type Checker** | None | ⚠️ Not detected |
| **Dependency Manager** | pip | ✅ Detected |

---

## Configuration Details

### Test Runner: pytest
- **Config file:** `pytest.ini`
- **AI command:** `pytest tests/`

---

## Gaps & Recommendations

### 🚨 CRITICAL: No Code Formatter

**Impact:** Code style inconsistency across team.

**Recommendation: black + isort**
- black: Most popular Python formatter (opinionated, zero-config)
- isort: Import sorting
- Template: `.agent-os/templates/python/pyproject.toml`
- Best practices: `.agent-os/usage/python-formatting-best-practices.md`

### ⚠️ IMPORTANT: No Linter

**Impact:** No automated code quality checks.

**Recommendation: pylint OR ruff**
- pylint: Comprehensive code analysis
- ruff: Faster, all-in-one tool
- Template: `.agent-os/templates/python/.pylintrc`
- Best practices: `.agent-os/usage/python-linting-best-practices.md`

### 💡 RECOMMENDED: Add Type Checker

**Impact:** No type safety enforcement.

**Recommendation: mypy**
- Most mature Python type checker
- Template: `.agent-os/templates/python/mypy.ini`
- Best practices: `.agent-os/usage/python-type-checking-best-practices.md`

---

## AI Execution Protocol

🛑 CRITICAL: Use detected tooling commands

- **Run tests:** `pytest tests/`

⚠️ **Formatting not configured:** AI cannot auto-format until formatter added.

⚠️ **Linting not configured:** AI cannot check code quality automatically.
```

**Example content (complete setup):**

```markdown
# Python Tooling Analysis

**Analysis Date:** 2025-10-06  
**Completeness Score:** 100% ✅

---

## Detected Tooling

| Category | Tool | Status |
|----------|------|--------|
| **Test Runner** | tox | ✅ Detected |
| **Formatter** | black + isort | ✅ Detected |
| **Linter** | pylint | ✅ Detected |
| **Type Checker** | mypy | ✅ Detected |
| **Dependency Manager** | pip | ✅ Detected |

---

## Configuration Details

### Test Runner: tox
- **Config file:** `tox.ini`
- **Environments:** py313, lint, format, unit, integration
- **AI commands:** 
  - Run all tests: `tox`
  - Run unit tests: `tox -e unit`
  - Run integration tests: `tox -e integration`

### Formatter: black + isort
- **Config file:** `pyproject.toml`
- **AI commands:**
  - Check formatting: `black --check src/ tests/`
  - Auto-fix: `black src/ tests/ && isort src/ tests/`

### Linter: pylint
- **Config file:** `pyproject.toml`
- **AI command:** `pylint src/`

### Type Checker: mypy
- **Config file:** `pyproject.toml`
- **AI command:** `mypy src/`

---

## Assessment

✅ **Excellent tooling setup!**

This project has comprehensive tooling configured. All essential categories covered.

---

## AI Execution Protocol

🛑 CRITICAL: Use detected tooling commands

- **Run all tests:** `tox`
- **Run unit tests:** `tox -e unit`
- **Check code quality:** `tox -e lint`
- **Check formatting:** `black --check src/ tests/`
- **Auto-fix formatting:** `black src/ tests/ && isort src/ tests/`
```

### Key Points

**What this step DOES:**
- ✅ Detects existing tooling
- ✅ Identifies gaps
- ✅ Recommends community best practices
- ✅ Documents findings for AI consumption
- ✅ Provides templates for reference

**What this step DOES NOT do:**
- ❌ Create tooling files (tox.ini, pyproject.toml, etc.)
- ❌ Modify existing files
- ❌ Install packages
- ❌ Make decisions for the team

**File Watcher Auto-Indexing:**
- When tooling-analysis.md is created, file watcher detects it
- RAG index automatically updated within ~30 seconds
- No manual rebuild step needed
- Standards immediately searchable via `search_standards()`

---

## Step 8: Communicate to User

### Installation Summary

```
✅ Agent OS Enhanced installed successfully!

Created:
✅ .cursorrules (46 lines, universal behavioral triggers)
✅ .agent-os/standards/universal/ (15 files, static CS fundamentals)
✅ .agent-os/standards/development/ (5 Python-specific files, generated)
   - python-concurrency.md (threading, asyncio, GIL)
   - python-testing.md (pytest, coverage, tox)
   - python-dependencies.md (pip, requirements.txt, version pinning)
   - python-code-quality.md (Black, Pylint, MyPy)
   - python-documentation.md (Sphinx, docstrings)
✅ .agent-os/mcp_server/ (RAG + sub-agents)
✅ .cursor/mcp.json (MCP configuration)
✅ RAG index built (1,247 chunks from 20 standards)

Detected in your project:
✅ Python project with pytest
✅ Black + Pylint for code quality
✅ Sphinx for documentation
✅ No async code detected yet

MCP Tools Available:
- mcp_agent-os-rag_search_standards - Search standards
- design_validator - Adversarial design review
- concurrency_analyzer - Thread safety analysis
- test_generator - Systematic test creation

Try: "Design a rate limiter with proper concurrency handling"
```

---

## Error Handling

### Language Detection Failed

```
⚠️  Could not auto-detect project language.

I found:
- Some Python files (10 .py files)
- Some JavaScript files (5 .js files)

Which language should I initialize for?
1. Python
2. JavaScript
3. Both (multi-language project)

User selects option, then proceed.
```

### Missing Dependencies

```
⚠️  Agent OS MCP server requires:
- Python 3.8+
- lancedb
- sentence-transformers

Should I create a requirements.txt for the MCP server?
```

### Existing Installation

```
⚠️  Agent OS is already installed in this project.

Options:
1. Update to latest version (preserves customizations)
2. Reinstall (overwrites customizations)
3. Cancel

User selects option.
```

---

## Update Workflow

When user says:
> "Update Agent OS to latest version"

```python
# 1. Pull latest from agent-os-enhanced repo
# 2. Backup user customizations
backup(".agent-os/standards/development/custom-*.md")

# 3. Update MCP server (always update)
copy_recursively("agent-os-enhanced/mcp_server", ".agent-os/mcp_server")

# 4. Update universal standards (if changed)
if universal_standards_changed():
    copy_recursively("agent-os-enhanced/universal", ".agent-os/standards/universal")

# 5. Optionally regenerate language-specific standards
prompt_user("Regenerate Python standards? (preserves custom files)")

# 6. Rebuild index
run_command("python .agent-os/scripts/build_rag_index.py")

# 7. Report
report_update_summary()
```

---

## Validation

After installation, validate:

```python
checks = {
    ".cursorrules exists": os.path.exists(".cursorrules"),
    ".agent-os/standards/universal/ exists": os.path.exists(".agent-os/standards/universal"),
    ".agent-os/standards/development/ has files": len(os.listdir(".agent-os/standards/development")) > 0,
    ".agent-os/mcp_server/ exists": os.path.exists(".agent-os/mcp_server"),
    ".cursor/mcp.json exists": os.path.exists(".cursor/mcp.json"),
    "RAG index built": os.path.exists(".agent-os/.cache/vector_index"),
}

if all(checks.values()):
    print("✅ Installation validated successfully")
else:
    print("⚠️  Issues detected:", [k for k, v in checks.items() if not v])
```

---

**End of Installation Guide**

This guide provides the systematic process for installing Agent OS Enhanced in any target project. Follow these steps conversationally, adapting to project context and user feedback.
