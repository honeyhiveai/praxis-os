# Step 6: Python venv, MCP Configuration, and RAG Index

**Previous**: `05-gitignore.md` (configured .gitignore)  
**Current**: Creating Python venv, configuring MCP, and building RAG index  
**Next**: `07-validate.md`

---

## 🎯 What This Step Does

1. Create isolated Python virtual environment
2. Install MCP server dependencies
3. Configure MCP server (agent-specific - see `03-agent-configuration.md`)
4. **Build RAG index** (enables semantic search - auto-built by Ouroboros on server start)
5. Validate Python setup

**Why isolated venv**: Prevents prAxIs OS dependencies from conflicting with your project's dependencies.

**Time**: ~3-5 minutes (includes RAG index build)

---

## 📦 Step 5.1: Create Python Virtual Environment

```python
import subprocess
import sys

# Create venv in .praxis-os/venv
print("📦 Creating Python virtual environment...")

result = subprocess.run([
    sys.executable, "-m", "venv", ".praxis-os/venv"
], capture_output=True, text=True)

if result.returncode != 0:
    print("❌ Failed to create venv:")
    print(result.stderr)
    exit(1)

print("✅ Virtual environment created at .praxis-os/venv/")
```

---

## 📥 Step 5.2: Install MCP Server Dependencies

```python
import subprocess
import os

# Determine pip path based on platform
if os.name == "nt":  # Windows
    pip_path = ".praxis-os/venv/Scripts/pip"
else:  # Unix-like (Linux, macOS, WSL2)
    pip_path = ".praxis-os/venv/bin/pip"

print(f"📥 Installing MCP server dependencies...")

result = subprocess.run([
    pip_path, "install", 
    "-r", ".praxis-os/ouroboros/requirements.txt"
], capture_output=True, text=True)

if result.returncode != 0:
    print("❌ Failed to install dependencies:")
    print(result.stderr)
    exit(1)

print("✅ Dependencies installed")
print(result.stdout)
```

---

## ✅ Validation Checkpoint #5A

Verify Python venv is working:

```python
import subprocess
import os

# Determine python path
if os.name == "nt":
    python_path = ".praxis-os/venv/Scripts/python.exe"
else:
    python_path = ".praxis-os/venv/bin/python"

# Test Python
result = subprocess.run([
    python_path, "--version"
], capture_output=True, text=True)

if result.returncode == 0:
    print(f"✅ Python venv working: {result.stdout.strip()}")
else:
    print("❌ Python venv not working")
    exit(1)

# Test module can be imported
result = subprocess.run([
    python_path, "-c", "import ouroboros"
], capture_output=True, text=True, 
   env={**os.environ, "PYTHONPATH": ".praxis-os"}
)

if result.returncode == 0:
    print("✅ MCP server module importable")
else:
    print("❌ Cannot import ouroboros:")
    print(result.stderr)
    exit(1)
```

---

## 🔧 Step 5.3: Configure MCP Server (Agent-Specific)

⚠️ **CRITICAL**: MCP configuration is agent-specific. Each agent uses different config files:

- **Cursor**: `.cursor/mcp.json`
- **Cline**: `.vscode/settings.json` (with `cline.mcpServers` key)
- **Claude Code (VS Code)**: `.vscode/settings.json` (with `claude-code.mcpServers` key)
- **Claude Code (CLI)**: `.mcp.json` or `~/.config/claude-code/mcp.json`
- **GitHub Copilot**: `.vscode/mcp.json`

**Next step**: Route to agent-specific configuration guide.

**Read file**: `installation/03-agent-configuration.md`

That file will:
1. Parse the agent/IDE from the user's installation command
2. Route to the correct agent-specific guide
3. Guide you through creating the appropriate MCP configuration file for your agent

**About Dual-Transport Mode:**

The `--transport dual` argument enables both:
- **stdio**: For IDE communication (traditional MCP)
- **HTTP**: For sub-agent access via `http://127.0.0.1:4242/mcp` (auto-allocated port)

**Benefits:**
- ✅ IDE integration works as before
- ✅ Sub-agents can connect via HTTP
- ✅ Zero port conflicts (automatic port allocation per project)
- ✅ Multi-project support (each gets its own port)

**State File:**

With dual-transport, a state file is created at `.praxis-os/.mcp_server_state.json` containing:
- Transport mode
- Allocated port
- HTTP URL
- Project info

This file is automatically managed (created on start, deleted on shutdown) and added to `.gitignore`.

---

## 📄 Verify MCP Configuration

After configuring your agent-specific MCP file, verify it was created correctly:

```python
import json
from pathlib import Path

# Determine which MCP config file to check based on agent
# (This should be done after routing via 03-agent-configuration.md)

# Example for Cursor:
mcp_file = Path(".cursor/mcp.json")
if mcp_file.exists():
    with open(mcp_file, "r") as f:
        config = json.load(f)
    
    # Critical checks
    checks = {
        "praxis-os server configured": "praxis-os" in config.get("mcpServers", {}),
        "Module name is 'ouroboros'": config["mcpServers"]["praxis-os"]["args"][1] == "ouroboros",
        "PYTHONPATH is set": "PYTHONPATH" in config["mcpServers"]["praxis-os"]["env"],
    }

all_passed = all(checks.values())

for check, passed in checks.items():
    print(f"{'✅' if passed else '❌'} {check}")

if not all_passed:
    print("\n❌ mcp.json configuration has issues!")
    exit(1)

print("\n✅ mcp.json configured correctly")
```

---

## 🔍 Manual Verification

You can manually check the mcp.json file:

```bash
# Check your agent-specific MCP config file
# (determined by routing via 03-agent-configuration.md)
```

**Note**: The exact MCP configuration format depends on your agent. See `installation/03-agent-configuration.md` to route to your agent-specific guide, which will show the correct configuration format for your agent.

**For Windows native**, the `command` should use `Scripts/python.exe` instead of `bin/python`.

---

## ✅ Validation Checkpoint #5B

Test that MCP server can start (don't worry if it complains about missing index, that's normal):

```python
import subprocess
import os
import time

# Determine python path
if os.name == "nt":
    python_path = ".praxis-os/venv/Scripts/python.exe"
else:
    python_path = ".praxis-os/venv/bin/python"

print("🧪 Testing MCP server startup...")

# Try to import and validate config
test_script = """
import sys
from pathlib import Path
sys.path.insert(0, '.praxis-os')

from ouroboros.config.loader import load_config

try:
    config = load_config(Path('.praxis-os/config/mcp.yaml'))
    # Config validation happens automatically on load
    print('VALIDATION_PASSED')
except Exception as e:
    print('VALIDATION_FAILED')
    print(f'  {e}')
    sys.exit(1)
"""

result = subprocess.run([
    python_path, "-c", test_script
], capture_output=True, text=True)

if "VALIDATION_PASSED" in result.stdout:
    print("✅ MCP server validation passed!")
else:
    print("❌ MCP server validation failed:")
    print(result.stdout)
    print(result.stderr)
    exit(1)
```

**Expected output**: `✅ MCP server validation passed!`

---

## 🚨 Troubleshooting

### Issue: "No module named 'venv'"

**Cause**: Python installation incomplete

**Fix**:
```bash
# Install python venv support (Ubuntu/Debian)
sudo apt-get install python3-venv

# Then retry venv creation
```

### Issue: "Permission denied" on venv creation

**Cause**: No write permission

**Fix**:
```bash
# Check permissions
ls -ld .praxis-os
# Should show write permission (w)
```

### Issue: Dependencies install fails

**Cause**: Network issue or missing dependencies

**Fix**:
```bash
# Retry with verbose output
.praxis-os/venv/bin/pip install -r .praxis-os/ouroboros/requirements.txt -v
```

### Issue: Config validation fails with "workflows_path does not exist"

**Cause**: You skipped step 01 or 02

**Fix**: Go back and ensure:
1. `.praxis-os/workflows/` directory exists (step 01)
2. Workflow files were copied (step 02)

---

## 🔍 Step 5.4: RAG Index Auto-Build

✅ **AUTOMATIC**: Ouroboros automatically builds RAG indexes on first server start!

The RAG (Retrieval Augmented Generation) index enables semantic search over prAxIs OS standards. Ouroboros will automatically build indexes when the MCP server starts if they don't exist.

**No manual build needed** - indexes are built automatically when you start the server.

**Index location**: `.praxis-os/.cache/indexes/`
- Standards index: `.praxis-os/.cache/indexes/standards/`
- Code index: `.praxis-os/.cache/indexes/code/`

**Expected behavior on first server start:**
```
INFO - IndexManager initialized with 2 indexes
INFO - 🔍 Checking health of all indexes...
INFO - 🔨 Building 2 missing/empty index(es)...
INFO -   Building standards index (full rebuild)...
INFO -   Building code index (full rebuild)...
INFO - ✅ StandardsIndex initialized
INFO - ✅ CodeIndex initialized
INFO - Including workflow metadata from: .praxis-os/workflows
INFO - Processing 98 markdown files
INFO - Generated 1247 chunks from 98 files
INFO - Generating embeddings for all chunks...
INFO - Creating new table with 1247 records...
✅ Table created with 1247 records
✅ Index full build complete in 87.3s
```

**What this does:**
- Auto-detects installed location (`.praxis-os/`)
- Scans all markdown files in `standards/`, `usage/`, and `workflows/` directories
- Chunks content using semantic-aware chunking (preserves section headers and metadata)
- Generates embeddings using local model (sentence-transformers, FREE & OFFLINE)
- Stores vectors in LanceDB at `.praxis-os/.cache/indexes/`

**Indexed content:**
- ✅ Standards (~46 files) - Universal CS fundamentals
- ✅ Usage docs (~5 files) - How to use prAxIs OS
- ✅ Workflows (~47 files) - Phase-gated workflow definitions

**Time**: 1-2 minutes for ~100 files (first run downloads embedding model ~90MB)  
**Disk**: ~20-50 MB for index

**Note**: The script auto-detects all three directories. The index auto-updates on file changes via file watcher in the MCP server, so you only need to build it once during installation.

---

## ✅ Validation Checkpoint #5C

Verify RAG index was created:

**Linux/macOS/WSL2:**
```bash
ls -la .praxis-os/.cache/indexes/
```

**Windows:**
```bash
dir .praxis-os\.cache\indexes\
```

**You should see:**
- `standards/` - Standards vector index directory (LanceDB)
- `code/` - Code vector + graph index directory (LanceDB + DuckDB)

**Quick test:**
```bash
# Linux/macOS/WSL2
test -d .praxis-os/.cache/indexes/standards && echo "✅ RAG index built" || echo "❌ RAG index missing"

# Windows
if exist .praxis-os\.cache\indexes\standards (echo ✅ RAG index built) else (echo ❌ RAG index missing)
```

---

## 🚨 Troubleshooting

### Issue: "No module named 'sentence_transformers'"

**Cause**: Dependencies not installed correctly

**Fix**:
```bash
.praxis-os/venv/bin/pip install -r .praxis-os/ouroboros/requirements.txt
```

### Issue: Build takes too long (>5 minutes)

**Cause**: First-time download of embedding model (~90 MB)

**Expected**: Downloads once, then cached forever. Subsequent builds take ~30 seconds.

### Issue: "Path does not exist: .praxis-os/standards"

**Cause**: You skipped step 02 (copying files)

**Fix**: Go back to `02-copy-files.md` and ensure all files were copied.

---

## 📊 Progress Check

At this point you should have:
- ✅ Python venv at `.praxis-os/venv/`
- ✅ MCP server dependencies installed
- ✅ Agent-specific MCP configuration file created (see `03-agent-configuration.md` for routing)
- ✅ Module name is `"ouroboros"` (not `"mcp_server"`)
- ✅ **RAG index built at `.praxis-os/.cache/indexes/`** (auto-built by Ouroboros on server start)
- ✅ Config validation passes
- ✅ All validation checkpoints passed

**If anything above is ❌, stop and fix before continuing.**

---

## 🎯 What's Next

You've set up the Python environment, MCP configuration, and RAG index. Now for the final step:
1. Run comprehensive validation
2. **Clean up temp directory** (critical!)
3. Inform user of successful installation

**Next step**: Final validation and cleanup.

---

## ➡️ NEXT STEP

**Read file**: `installation/07-validate.md`

That file will:
1. Run comprehensive validation of entire installation
2. **Delete the temp directory** (clean up after ourselves!)
3. Provide user instructions for enabling MCP server
4. Declare installation complete

---

**Status**: Step 5 Complete ✅  
**Created**: Python venv + mcp.json + RAG index  
**Next File**: `07-validate.md`  
**Step**: 6 of 7

