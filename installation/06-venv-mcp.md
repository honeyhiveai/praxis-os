# Step 6: Python venv, MCP Configuration, and RAG Index

**Previous**: `05-gitignore.md` (configured .gitignore)  
**Current**: Creating Python venv, configuring Cursor MCP, and building RAG index  
**Next**: `07-validate.md`

---

## 🎯 What This Step Does

1. Create isolated Python virtual environment
2. Install MCP server dependencies
3. Create `.cursor/mcp.json` configuration file
4. **Build RAG index** (enables semantic search)
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
    "-r", ".praxis-os/mcp_server/requirements.txt"
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
    python_path, "-c", "import mcp_server"
], capture_output=True, text=True, 
   env={**os.environ, "PYTHONPATH": ".praxis-os"}
)

if result.returncode == 0:
    print("✅ MCP server module importable")
else:
    print("❌ Cannot import mcp_server:")
    print(result.stderr)
    exit(1)
```

---

## 🔧 Step 5.3: Create .cursor/mcp.json

⚠️ **CRITICAL**: Use `"mcp_server"` NOT `"mcp_server.praxis_os_rag"`!

```python
import json
import os

# Determine correct Python path for mcp.json
if os.name == "nt":
    # Windows native
    python_cmd = "${workspaceFolder}/.praxis-os/venv/Scripts/python.exe"
else:
    # Linux, macOS, WSL2
    python_cmd = "${workspaceFolder}/.praxis-os/venv/bin/python"

mcp_config = {
    "mcpServers": {
        "praxis-os-rag": {
            "command": python_cmd,
            "args": [
                "-m",
                "mcp_server",
                "--transport",
                "dual",  # ← Enable dual-transport (stdio + HTTP)
                "--log-level",
                "INFO"
            ],
            "env": {
                "PROJECT_ROOT": "${workspaceFolder}",
                "PYTHONPATH": "${workspaceFolder}/.praxis-os",
                "PYTHONUNBUFFERED": "1"
            },
            "autoApprove": [
                "search_standards",
                "get_current_phase",
                "get_workflow_state",
                "get_server_info"
            ]
        }
    }
}

# Write mcp.json
with open(".cursor/mcp.json", "w") as f:
    json.dump(mcp_config, f, indent=2)

print("✅ .cursor/mcp.json created")
print(f"   Platform: {'Windows' if os.name == 'nt' else 'Unix-like'}")
print(f"   Python: {python_cmd}")
print("   Module: mcp_server")
print("   Transport: dual (stdio + HTTP)")
print("   HTTP endpoint: http://127.0.0.1:4242/mcp (auto-allocated port)")
```

**About Dual-Transport Mode:**

The `--transport dual` argument enables both:
- **stdio**: For Cursor IDE communication (traditional MCP)
- **HTTP**: For sub-agent access via `http://127.0.0.1:4242/mcp`

**Benefits:**
- ✅ IDE integration works as before
- ✅ Sub-agents can connect via HTTP
- ✅ Zero port conflicts (automatic port allocation per project)
- ✅ Multi-project support (each gets its own port)

**Alternative Modes** (if needed):
- `stdio`: IDE only (no HTTP) - use if you don't need sub-agents
- `http`: HTTP only (no stdio) - use for services/testing

**State File:**

With dual-transport, a state file is created at `.praxis-os/.mcp_server_state.json` containing:
- Transport mode
- Allocated port
- HTTP URL
- Project info

This file is automatically managed (created on start, deleted on shutdown) and added to `.gitignore`.

---

## 📄 Verify mcp.json Content

Check that the file was created correctly:

```python
import json

# Read and verify
with open(".cursor/mcp.json", "r") as f:
    config = json.load(f)

# Critical checks
checks = {
    "praxis-os-rag server configured": "praxis-os-rag" in config.get("mcpServers", {}),
    "Module name is 'mcp_server'": config["mcpServers"]["praxis-os-rag"]["args"][1] == "mcp_server",
    "PYTHONPATH is set": "PYTHONPATH" in config["mcpServers"]["praxis-os-rag"]["env"],
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
cat .cursor/mcp.json
```

**Should look like this** (Linux/macOS/WSL2):
```json
{
  "mcpServers": {
    "praxis-os-rag": {
      "command": "${workspaceFolder}/.praxis-os/venv/bin/python",
      "args": ["-m", "mcp_server"],
      "env": {
        "PROJECT_ROOT": "${workspaceFolder}",
        "PYTHONPATH": "${workspaceFolder}/.praxis-os",
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

from mcp_server.config import ConfigLoader, ConfigValidator

config = ConfigLoader.load(Path('.praxis-os'))
errors = ConfigValidator.validate(config)

if errors:
    print('VALIDATION_FAILED')
    for error in errors:
        print(f'  {error}')
    sys.exit(1)
else:
    print('VALIDATION_PASSED')
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
.praxis-os/venv/bin/pip install -r .praxis-os/mcp_server/requirements.txt -v
```

### Issue: Config validation fails with "workflows_path does not exist"

**Cause**: You skipped step 01 or 02

**Fix**: Go back and ensure:
1. `.praxis-os/workflows/` directory exists (step 01)
2. Workflow files were copied (step 02)

---

## 🔍 Step 5.4: Build RAG Index

⚠️ **CRITICAL STEP**: Without the RAG index, `search_standards` won't work!

The RAG (Retrieval Augmented Generation) index enables semantic search over prAxIs OS standards.

**Linux/macOS/WSL2:**
```bash
.praxis-os/venv/bin/python .praxis-os/scripts/build_rag_index.py \
  --index-path .praxis-os/.cache/vector_index \
  --standards-path .praxis-os/standards \
  --usage-path .praxis-os/usage \
  --workflows-path .praxis-os/workflows
```

**Windows:**
```bash
.praxis-os\venv\Scripts\python.exe .praxis-os\scripts\build_rag_index.py --index-path .praxis-os\.cache\vector_index --standards-path .praxis-os\standards --usage-path .praxis-os\usage --workflows-path .praxis-os\workflows
```

**Expected output:**
```
INFO - Initializing LanceDB at .praxis-os/.cache/vector_index
INFO - Including usage docs from: .praxis-os/usage
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
- Stores vectors in LanceDB at `.praxis-os/.cache/vector_index/`

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
ls -la .praxis-os/.cache/vector_index/
```

**Windows:**
```bash
dir .praxis-os\.cache\vector_index\
```

**You should see:**
- `praxis_os_standards.lance/` - LanceDB table directory
- `metadata.json` - Build metadata (timestamps, file counts, etc.)

**Quick test:**
```bash
# Linux/macOS/WSL2
test -f .praxis-os/.cache/vector_index/metadata.json && echo "✅ RAG index built" || echo "❌ RAG index missing"

# Windows
if exist .praxis-os\.cache\vector_index\metadata.json (echo ✅ RAG index built) else (echo ❌ RAG index missing)
```

---

## 🚨 Troubleshooting

### Issue: "No module named 'sentence_transformers'"

**Cause**: Dependencies not installed correctly

**Fix**:
```bash
.praxis-os/venv/bin/pip install -r .praxis-os/mcp_server/requirements.txt
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
- ✅ `.cursor/mcp.json` created with correct config
- ✅ Module name is `"mcp_server"` (not `"mcp_server.praxis_os_rag"`)
- ✅ **RAG index built at `.praxis-os/.cache/vector_index/`** (NEW!)
- ✅ Config validation passes
- ✅ All validation checkpoints passed

**If anything above is ❌, stop and fix before continuing.**

---

## 🎯 What's Next

You've set up the Python environment, Cursor configuration, and RAG index. Now for the final step:
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

