# Python Virtual Environment Configuration

## Questions This Answers

- **Why does prAxIs OS require two separate virtual environments?**
- **Where should the prAxIs OS MCP server venv be located?**
- **How do I configure .cursor/mcp.json to use the correct venv?**
- **What's the difference between the prAxIs OS venv and project venv?**
- **How does the installation script detect my project's venv?**
- **What happens if I don't have a project venv when installing prAxIs OS?**
- **How do I activate the correct venv for development vs MCP server?**
- **What dependencies go in each venv?**
- **How do I troubleshoot venv-related issues?**
- **Why can't the MCP server and project share a single venv?**

## Quick Reference: Dual-Venv Architecture

**Why Two Venvs?** Isolation between prAxIs OS infrastructure and project dependencies

**prAxIs OS MCP Server Venv:**
- Location: `.praxis-os/venv/`
- Purpose: Run MCP server (RAG, workflow engine)
- Dependencies: lancedb, mcp, sentence-transformers, watchdog
- Usage: Configured in `.cursor/mcp.json`
- **DO NOT use for project code**

**Project Venv:**
- Location: User-specified (`.venv/`, `venv/`, `env/`)
- Purpose: Run project code, tests, linting
- Dependencies: Project-specific (from requirements.txt)
- Usage: Development, testing, deployment
- **DO NOT use for MCP server**

**Configuration:**
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

**Key Rule:** Never mix the two venvs - they serve different purposes!

---

## Two-Venv Architecture Overview

Python projects using prAxIs OS require **two separate virtual environments** to maintain isolation between prAxIs OS infrastructure and project dependencies.

---

## Virtual Environment Architecture

### 1. prAxIs OS MCP Server venv

**Location**: `.praxis-os/venv/`

**Purpose**: Isolated Python environment for prAxIs OS MCP server

**Dependencies**:
- `lancedb` - Vector database for RAG
- `mcp` - Model Context Protocol server
- `sentence-transformers` - Local embeddings
- `watchdog` - File system monitoring
- `honeyhive` (optional) - Observability integration

**Usage**: 
- Automatically created during prAxIs OS installation
- Used exclusively by `.cursor/mcp.json` to run the MCP server
- Should NOT be used for project code execution

**Installation**:
```bash
python -m venv .praxis-os/venv
.praxis-os/venv/bin/pip install -r mcp_server/requirements.txt
```

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

---

### 2. Project venv

**Location**: User-specified (commonly `venv/`, `.venv/`, or `env/`)

**Purpose**: Python environment for the actual project's code and dependencies

**Dependencies**: Project-specific (from `requirements.txt`, `pyproject.toml`, etc.)

**Usage**:
- Used for running project code
- Used for running tests (`pytest`)
- Used for linting and type checking
- Used for any project-specific tooling

**Detection Strategy** (in order of precedence):
1. User-provided path during installation
2. Active virtual environment (`$VIRTUAL_ENV`)
3. Common locations: `.venv/`, `venv/`, `env/`
4. Create new venv if none exists

---

## prAxIs OS Installation Process

### Step 1: Identify or Create Project venv

```python
# Pseudo-code for installation script
def setup_project_venv():
    # Check if venv is active
    if os.getenv('VIRTUAL_ENV'):
        project_venv = os.getenv('VIRTUAL_ENV')
        print(f"✅ Using active virtual environment: {project_venv}")
        return project_venv
    
    # Check common locations
    for venv_path in ['.venv', 'venv', 'env']:
        if Path(venv_path).exists():
            print(f"✅ Found existing virtual environment: {venv_path}")
            return str(Path.cwd() / venv_path)
    
    # Ask user or create new
    response = input("No virtual environment found. Create .venv? (y/n): ")
    if response.lower() == 'y':
        subprocess.run(['python', '-m', 'venv', '.venv'])
        print("✅ Created new virtual environment: .venv")
        return str(Path.cwd() / '.venv')
    else:
        venv_path = input("Enter path to your project's virtual environment: ")
        return venv_path
```

### Step 2: Document Project venv Location

Create `.praxis-os/config.json`:
```json
{
  "project": {
    "language": "python",
    "venv_path": "/absolute/path/to/project/venv",
    "venv_python": "/absolute/path/to/project/venv/bin/python"
  },
  "agent_os": {
    "venv_path": ".praxis-os/venv",
    "mcp_python": "${workspaceFolder}/.praxis-os/venv/bin/python"
  }
}
```

---

## Usage Guidelines for AI Assistants

### When to Use prAxIs OS venv (`.praxis-os/venv/`)

**NEVER** - The AI should never directly use this venv. It's managed automatically by Cursor for the MCP server.

### When to Use Project venv

**ALWAYS** for project operations:

#### Running Tests
```bash
# Correct ✅
/path/to/project/venv/bin/pytest tests/

# Wrong ❌
.praxis-os/venv/bin/pytest tests/  # Will fail - missing project dependencies
```

#### Running Linters
```bash
# Correct ✅
/path/to/project/venv/bin/pylint mcp_server/

# Correct ✅ (if installed in project venv)
/path/to/project/venv/bin/black --check .
```

#### Executing Project Code
```bash
# Correct ✅
/path/to/project/venv/bin/python my_script.py

# Wrong ❌
.praxis-os/venv/bin/python my_script.py  # May have missing dependencies
```

#### Installing Project Dependencies
```bash
# Correct ✅
/path/to/project/venv/bin/pip install pytest coverage

# Wrong ❌
.praxis-os/venv/bin/pip install pytest  # Pollutes prAxIs OS environment
```

---

## Configuration File Reference

The `.praxis-os/config.json` file stores virtual environment configuration:

```json
{
  "project": {
    "language": "python",
    "venv_path": "/Users/josh/src/project/.venv",
    "venv_python": "/Users/josh/src/project/.venv/bin/python",
    "venv_pip": "/Users/josh/src/project/.venv/bin/pip",
    "venv_pytest": "/Users/josh/src/project/.venv/bin/pytest"
  },
  "agent_os": {
    "venv_path": ".praxis-os/venv",
    "mcp_python": "${workspaceFolder}/.praxis-os/venv/bin/python"
  },
  "installation": {
    "installed_at": "2025-10-05T10:00:00Z",
    "version": "1.0.0"
  }
}
```

---

## AI Command Templates

When AI needs to run project commands, it should read `.praxis-os/config.json` and use the configured paths:

```python
# Read config
import json
config = json.load(open('.praxis-os/config.json'))
project_python = config['project']['venv_python']
project_pytest = config['project']['venv_pytest']

# Run tests
os.system(f"{project_pytest} tests/unit/")

# Run linter
os.system(f"{project_python} -m pylint mcp_server/")
```

---

## Virtual Environment Troubleshooting

### Issue: Tests fail with import errors

**Cause**: Tests are being run with prAxIs OS venv instead of project venv

**Solution**: 
1. Check `.praxis-os/config.json` for correct project venv path
2. Use the configured `venv_pytest` path explicitly
3. Verify project dependencies are installed: `{project_venv}/bin/pip list`

### Issue: MCP server fails to start

**Cause**: prAxIs OS venv is missing or corrupted

**Solution**:
1. Recreate prAxIs OS venv: `python -m venv .praxis-os/venv --clear`
2. Reinstall dependencies: `.praxis-os/venv/bin/pip install -r mcp_server/requirements.txt`
3. Restart Cursor to reload MCP server

### Issue: Project venv not found

**Cause**: Project venv was moved or deleted after installation

**Solution**:
1. Update `.praxis-os/config.json` with new venv path
2. Or recreate venv and reinstall project dependencies

---

## Best Practices

1. **Never mix environments**: Keep prAxIs OS and project dependencies completely separate
2. **Use absolute paths**: Store absolute paths in config for reliability
3. **Document in README**: Add section explaining the two-venv architecture
4. **Git ignore both**: Add both `.praxis-os/venv/` and project venv to `.gitignore`
5. **Test configuration**: Verify both venvs work independently after installation

---

## Example: Current Project Configuration

For the `praxis-os` project:

**prAxIs OS venv**: `.praxis-os/venv/`
- Purpose: Run MCP server
- Used by: Cursor's MCP integration

**Project venv**: `.praxis-os/venv/` (currently shared - should be separate!)
- Purpose: Run tests, execute project code
- Used by: pytest, linters, project scripts

**Recommendation**: Create separate project venv at `venv/` or `.venv/` and update configuration.

---

**Key Insight**: This two-venv architecture ensures prAxIs OS can be installed in any Python project without dependency conflicts, while maintaining clean isolation between infrastructure and application code.
