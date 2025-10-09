# Step 4: Python venv and MCP Configuration

**Previous**: `03-cursorrules.md` (handled .cursorrules)  
**Current**: Creating Python venv and configuring Cursor MCP  
**Next**: `05-validate.md`

---

## 🎯 What This Step Does

1. Create isolated Python virtual environment
2. Install MCP server dependencies
3. Create `.cursor/mcp.json` configuration file
4. Validate Python setup

**Why isolated venv**: Prevents Agent OS dependencies from conflicting with your project's dependencies.

**Time**: ~2-3 minutes

---

## 📦 Step 4.1: Create Python Virtual Environment

```python
import subprocess
import sys

# Create venv in .agent-os/venv
print("📦 Creating Python virtual environment...")

result = subprocess.run([
    sys.executable, "-m", "venv", ".agent-os/venv"
], capture_output=True, text=True)

if result.returncode != 0:
    print("❌ Failed to create venv:")
    print(result.stderr)
    exit(1)

print("✅ Virtual environment created at .agent-os/venv/")
```

---

## 📥 Step 4.2: Install MCP Server Dependencies

```python
import subprocess
import os

# Determine pip path based on platform
if os.name == "nt":  # Windows
    pip_path = ".agent-os/venv/Scripts/pip"
else:  # Unix-like (Linux, macOS, WSL2)
    pip_path = ".agent-os/venv/bin/pip"

print(f"📥 Installing MCP server dependencies...")

result = subprocess.run([
    pip_path, "install", 
    "-r", ".agent-os/mcp_server/requirements.txt"
], capture_output=True, text=True)

if result.returncode != 0:
    print("❌ Failed to install dependencies:")
    print(result.stderr)
    exit(1)

print("✅ Dependencies installed")
print(result.stdout)
```

---

## ✅ Validation Checkpoint #4A

Verify Python venv is working:

```python
import subprocess
import os

# Determine python path
if os.name == "nt":
    python_path = ".agent-os/venv/Scripts/python.exe"
else:
    python_path = ".agent-os/venv/bin/python"

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
   env={**os.environ, "PYTHONPATH": ".agent-os"}
)

if result.returncode == 0:
    print("✅ MCP server module importable")
else:
    print("❌ Cannot import mcp_server:")
    print(result.stderr)
    exit(1)
```

---

## 🔧 Step 4.3: Create .cursor/mcp.json

⚠️ **CRITICAL**: Use `"mcp_server"` NOT `"mcp_server.agent_os_rag"`!

```python
import json
import os

# Determine correct Python path for mcp.json
if os.name == "nt":
    # Windows native
    python_cmd = "${workspaceFolder}/.agent-os/venv/Scripts/python.exe"
else:
    # Linux, macOS, WSL2
    python_cmd = "${workspaceFolder}/.agent-os/venv/bin/python"

mcp_config = {
    "mcpServers": {
        "agent-os-rag": {
            "command": python_cmd,
            "args": ["-m", "mcp_server"],  # ← CORRECT module name!
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

# Write mcp.json
with open(".cursor/mcp.json", "w") as f:
    json.dump(mcp_config, f, indent=2)

print("✅ .cursor/mcp.json created")
print(f"   Platform: {'Windows' if os.name == 'nt' else 'Unix-like'}")
print(f"   Python: {python_cmd}")
print("   Module: mcp_server")
```

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
    "agent-os-rag server configured": "agent-os-rag" in config.get("mcpServers", {}),
    "Module name is 'mcp_server'": config["mcpServers"]["agent-os-rag"]["args"][1] == "mcp_server",
    "PYTHONPATH is set": "PYTHONPATH" in config["mcpServers"]["agent-os-rag"]["env"],
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
    "agent-os-rag": {
      "command": "${workspaceFolder}/.agent-os/venv/bin/python",
      "args": ["-m", "mcp_server"],
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

**For Windows native**, the `command` should use `Scripts/python.exe` instead of `bin/python`.

---

## ✅ Validation Checkpoint #4B

Test that MCP server can start (don't worry if it complains about missing index, that's normal):

```python
import subprocess
import os
import time

# Determine python path
if os.name == "nt":
    python_path = ".agent-os/venv/Scripts/python.exe"
else:
    python_path = ".agent-os/venv/bin/python"

print("🧪 Testing MCP server startup...")

# Try to import and validate config
test_script = """
import sys
from pathlib import Path
sys.path.insert(0, '.agent-os')

from mcp_server.config import ConfigLoader, ConfigValidator

config = ConfigLoader.load(Path('.agent-os'))
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
ls -ld .agent-os
# Should show write permission (w)
```

### Issue: Dependencies install fails

**Cause**: Network issue or missing dependencies

**Fix**:
```bash
# Retry with verbose output
.agent-os/venv/bin/pip install -r .agent-os/mcp_server/requirements.txt -v
```

### Issue: Config validation fails with "workflows_path does not exist"

**Cause**: You skipped step 01 or 02

**Fix**: Go back and ensure:
1. `.agent-os/workflows/` directory exists (step 01)
2. Workflow files were copied (step 02)

---

## 📊 Progress Check

At this point you should have:
- ✅ Python venv at `.agent-os/venv/`
- ✅ MCP server dependencies installed
- ✅ `.cursor/mcp.json` created with correct config
- ✅ Module name is `"mcp_server"` (not `"mcp_server.agent_os_rag"`)
- ✅ Config validation passes
- ✅ All validation checkpoints passed

**If anything above is ❌, stop and fix before continuing.**

---

## 🎯 What's Next

You've set up the Python environment and Cursor configuration. Now for the final step:
1. Run comprehensive validation
2. **Clean up temp directory** (critical!)
3. Inform user of successful installation

**Next step**: Final validation and cleanup.

---

## ➡️ NEXT STEP

**Read file**: `installation/06-validate.md`

That file will:
1. Run comprehensive validation of entire installation
2. **Delete the temp directory** (clean up after ourselves!)
3. Provide user instructions for enabling MCP server
4. Declare installation complete

---

**Status**: Step 4 Complete ✅  
**Created**: Python venv + mcp.json  
**Next File**: `05-validate.md`  
**Step**: 5 of 5 (final step!)

