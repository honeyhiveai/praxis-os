# Agent OS Installation - START HERE

**Read this file first. It will direct you to the next steps.**

---

## 🎯 What You're About To Do

Install prAxIs OS into the target project. This will:
1. Create `.praxis-os/` directory structure
2. Copy standards, workflows, and MCP server code
3. Create Python virtual environment
4. Configure Cursor to use MCP server
5. **Build RAG index** (enables semantic search over standards)

**Total Time**: ~5-10 minutes  
**Complexity**: Medium (vanilla LLM can follow)

---

## ⚠️ CRITICAL: Read These Mistakes FIRST

**These 4 mistakes will break the installation. Read them NOW:**

### Mistake #1: Forgetting `.praxis-os/workflows/` Directory
**What happens**: MCP server validation fails  
**Error message**: `❌ workflows_path does not exist`  
**Prevention**: Step 01 has a checklist - verify ALL 8 directories exist

### Mistake #2: Wrong Module Name in mcp.json
**What happens**: Python module not found error  
**Wrong**: `"mcp_server.agent_os_rag"`  
**Correct**: `"mcp_server"`  
**Prevention**: Step 05 has the exact JSON to copy

### Mistake #3: Blindly Overwriting .cursorrules
**What happens**: User's existing Cursor rules are destroyed  
**Prevention**: Step 03 checks if file exists first, asks user what to do

### Mistake #4: Forgetting to Copy Workflows
**What happens**: Workflows directory exists but is empty  
**Prevention**: Step 02 has explicit copy command for workflows

---

## 📋 Installation Steps Overview

You'll follow these files in order:

```
00-START.md           ← YOU ARE HERE (clone source, setup)
01-directories.md     Create all required directories
02-copy-files.md      Copy all content from source repo
03-cursorrules.md     Handle .cursorrules safely (don't overwrite!)
04-gitignore.md       Configure .gitignore (prevent committing 2.6GB!)
05-venv-mcp.md        Create venv, mcp.json, and BUILD RAG INDEX
06-validate.md        Final validation and cleanup temp files
```

Each file:
- ✅ ~200-250 lines (manageable attention span)
- ✅ Has validation checkpoints
- ✅ Tells you what file to read next
- ✅ Can be re-read if you get confused

---

## 🏗️ Architecture Context

**Source Repository** (praxis-os):
```
/tmp/agent-os-install-xyz/      ← Temp clone (will delete after!)
├── installation/               ← These guides
│   ├── 00-START.md            ← YOU ARE HERE
│   ├── 01-directories.md
│   ├── 02-copy-files.md
│   ├── 03-cursorrules.md
│   ├── 04-gitignore.md
│   ├── 05-venv-mcp.md
│   └── 06-validate.md
├── universal/                  ← Content to copy
│   ├── standards/
│   ├── usage/
│   └── workflows/
├── mcp_server/                 ← Code to copy
└── .cursorrules                ← File to copy (or merge)
```

**⚠️ CRITICAL**: This is a temp directory that will be deleted at the end!

**Target Project** (where you're installing):
```
target-project/                 ← Where you're installing TO
├── .praxis-os/                  ← Will be created
│   ├── standards/
│   ├── usage/
│   ├── workflows/
│   ├── mcp_server/
│   └── venv/
├── .cursorrules                ← Copy or merge
└── .cursor/
    └── mcp.json                ← Create fresh
```

---

## 🔍 Pre-Installation: Get Source Repository

**IMPORTANT**: You need the Agent OS source code, but you CANNOT clone it directly into the target project (that would litter a git repo inside their repo).

### Option A: Clone to Temp Directory (Recommended)

```python
import tempfile
import subprocess
import os

# Create temp directory
temp_dir = tempfile.mkdtemp(prefix="agent-os-install-")
print(f"📦 Cloning to temp location: {temp_dir}")

# Clone repo to temp
subprocess.run([
    "git", "clone", 
    "https://github.com/honeyhiveai/praxis-os.git",
    temp_dir
], check=True)

# Store this path - you'll use it throughout installation
AGENT_OS_SOURCE = temp_dir
print(f"✅ Source ready at: {AGENT_OS_SOURCE}")

# IMPORTANT: At the end of installation (step 05), you'll delete this temp directory
```

### Option B: User Provides Path

If the user already has Agent OS cloned somewhere:

```python
# Ask user where they've cloned praxis-os
AGENT_OS_SOURCE = input("Path to praxis-os clone: ")

# Validate it
assert os.path.exists(f"{AGENT_OS_SOURCE}/universal/"), "Invalid path"
assert os.path.exists(f"{AGENT_OS_SOURCE}/mcp_server/"), "Invalid path"

print(f"✅ Using source at: {AGENT_OS_SOURCE}")
```

### Pre-Installation Checks

```python
# 1. Check source repo is valid
assert os.path.exists(f"{AGENT_OS_SOURCE}/universal/"), "Source repo invalid"
assert os.path.exists(f"{AGENT_OS_SOURCE}/mcp_server/"), "MCP server not found"

# 2. Check target project is writable
assert os.access(".", os.W_OK), "Target directory not writable"

# 3. Check Python version
import sys
assert sys.version_info >= (3, 8), "Python 3.8+ required"

# 4. Check NOT inside praxis-os repo itself
current_dir = os.path.basename(os.getcwd())
assert current_dir != "praxis-os", "Don't install inside source repo!"
```

**If any checks fail, stop and fix before continuing.**

**⚠️ REMEMBER**: If you cloned to temp (Option A), you MUST delete it in step 05!

---

## 📚 Reference Materials

During installation, you can reference:

- **Common Failures**: `installation/TROUBLESHOOTING.md` (if you get stuck)
- **Detailed Guide**: `installation/DETAILED-GUIDE.md` (800+ lines, comprehensive)
- **Merge Protocol**: `installation/03-cursorrules.md` (step 3 has full details)

But for normal installation, just follow 01 → 02 → 03 → 04 → 05.

---

## 🎬 Ready to Start?

You've read the critical mistakes. You understand the architecture.

**Your first task**: Create directories.

---

## ➡️ NEXT STEP

**Read file**: `installation/01-directories.md`

That file will:
1. List all 8 required directories
2. Provide exact commands to create them
3. Provide validation commands
4. Direct you to step 02

---

**Status**: Pre-Installation Complete ✅  
**Next File**: `01-directories.md`  
**Step**: 1 of 6

