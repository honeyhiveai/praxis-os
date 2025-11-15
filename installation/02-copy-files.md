# Step 2: Copy Files from Source

**Previous**: `01-directories.md` (created directories)  
**Current**: Copying all required files  
**Next**: `03-agent-configuration.md`

---

## 🎯 What This Step Does

Copy all required content from the source repository (`praxis-os/`) to your project.

**What gets copied**:
1. Universal standards (CS fundamentals)
2. Usage documentation (how to use prAxIs OS)
3. Workflows (spec_creation_v1, spec_execution_v1)
4. Ouroboros server code (MCP server - Python code that runs the server)

**Time**: ~1-2 minutes (depends on file system speed)

---

## 📦 Copy Operations (4 total)

### Copy #1: Universal Standards

**Source**: `{PRAXIS_OS_SOURCE}/dist/universal/standards/`  
**Destination**: `.praxis-os/standards/universal/`  
**Contents**: ~30 markdown files with CS fundamentals

```python
import shutil

# Use PRAXIS_OS_SOURCE from step 00
shutil.copytree(
    f"{PRAXIS_OS_SOURCE}/dist/universal/standards",
    ".praxis-os/standards/universal",
    dirs_exist_ok=True
)
print("✅ Copied universal standards")
```

**Note**: `PRAXIS_OS_SOURCE` is the temp directory you created in step 00.

**What's in there**: Architecture patterns, concurrency, testing, security, etc.

---

### Copy #2: Workflows (CRITICAL!)

**Source**: `{PRAXIS_OS_SOURCE}/dist/universal/workflows/`  
**Destination**: `.praxis-os/workflows/`  
**Contents**: Complete workflow definitions (spec_creation_v1 + spec_execution_v1)

⚠️ **This is the one people forget!**

```python
shutil.copytree(
    f"{PRAXIS_OS_SOURCE}/dist/universal/workflows",
    ".praxis-os/workflows",
    dirs_exist_ok=True
)
print("✅ Copied workflows")
```

**What's in there**:
- `spec_creation_v1/` - Phase-gated spec creation workflow
- `spec_execution_v1/` - Dynamic spec execution workflow

**Why it's critical**: Without this, the `start_workflow()` MCP tool won't work.

---

### Copy #3: Ouroboros Server Code

**Source**: `{PRAXIS_OS_SOURCE}/dist/ouroboros/`  
**Destination**: `.praxis-os/ouroboros/`  
**Contents**: ~20 Python files + requirements.txt

```python
shutil.copytree(
    f"{PRAXIS_OS_SOURCE}/dist/ouroboros",
    ".praxis-os/ouroboros",
    dirs_exist_ok=True
)
print("✅ Copied Ouroboros server")
```

**What's in there**: RAG engine, workflow engine, server factory, MCP tools, etc.

---

### Copy #4: Scripts (CRITICAL - RAG Index Builder!)

**Source**: `praxis-os/scripts/`  
**Destination**: `.praxis-os/scripts/`  
**Contents**: ~3 Python files including `build_rag_index.py`

⚠️ **DO NOT SKIP THIS!** Without `build_rag_index.py`, the MCP server cannot build the RAG index on first startup. AIs will try to create their own version, causing inconsistent implementations.

```python
shutil.copytree(
    "praxis-os/scripts",
    ".praxis-os/scripts",
    dirs_exist_ok=True
)
print("✅ Copied scripts")
```

**What's in there**:
- `build_rag_index.py` - Canonical IndexBuilder implementation (CRITICAL!)
- `generate-manifest.py` - Workflow manifest generator
- `safe-upgrade.py` - Safe upgrade utilities

**Why it's critical**: Ouroboros automatically builds RAG indexes on server start when `.praxis-os/.cache/indexes/` doesn't exist. The server code includes all necessary index building functionality.

---

## 🔨 Complete Copy Script

**Run this Python script** to copy all files:

```python
import shutil
import os

# PRAXIS_OS_SOURCE from step 00 (temp directory)
# Make sure this variable is still available!

def copy_with_status(src, dest, name):
    """Copy directory and print status"""
    try:
        shutil.copytree(src, dest, dirs_exist_ok=True)
        # Count files
        file_count = sum(len(files) for _, _, files in os.walk(dest))
        print(f"✅ {name}: {file_count} files copied")
        return True
    except Exception as e:
        print(f"❌ {name}: Failed - {e}")
        return False

print("Starting file copy operations...\n")
print(f"Source: {PRAXIS_OS_SOURCE}\n")

# Copy #1: Universal standards
success1 = copy_with_status(
    f"{PRAXIS_OS_SOURCE}/dist/universal/standards",
    ".praxis-os/standards/universal",
    "Universal standards"
)

# Copy #2: Workflows (CRITICAL!)
success2 = copy_with_status(
    f"{PRAXIS_OS_SOURCE}/dist/universal/workflows",
    ".praxis-os/workflows",
    "Workflows"
)

# Copy #3: Ouroboros server
success3 = copy_with_status(
    f"{PRAXIS_OS_SOURCE}/dist/ouroboros",
    ".praxis-os/ouroboros",
    "Ouroboros server"
)

# Copy #4: Scripts (CRITICAL!)
success4 = copy_with_status(
    f"{PRAXIS_OS_SOURCE}/scripts",
    ".praxis-os/scripts",
    "Scripts"
)

# Copy #5: .cursorrules (we'll handle merge in step 03, but copy for now)
# This will be overwritten in step 03 if needed

# Summary
print("\n" + "="*50)
if all([success1, success2, success3, success4]):
    print("✅ ALL FILES COPIED SUCCESSFULLY")
    print(f"\n📝 Temp source still at: {PRAXIS_OS_SOURCE}")
    print("   (Will be deleted in step 06)")
else:
    print("❌ SOME COPIES FAILED - Review errors above")
    exit(1)
```

**Expected output**:
```
Starting file copy operations...

✅ Universal standards: 31 files copied
✅ Usage documentation: 5 files copied
✅ Workflows: 47 files copied
✅ Ouroboros server: 23 files copied
✅ Scripts: 3 files copied

==================================================
✅ ALL FILES COPIED SUCCESSFULLY
```

---

## ✅ Validation Checkpoint #2

After copying, verify key files exist:

```python
import os

critical_files = [
    # Standards
    ".praxis-os/standards/universal/architecture/solid-principles.md",
    ".praxis-os/standards/universal/testing/test-pyramid.md",
    
    # Workflows (MOST IMPORTANT!)
    ".praxis-os/workflows/spec_creation_v1/metadata.json",
    ".praxis-os/workflows/spec_execution_v1/metadata.json",
    
    # Ouroboros Server
    ".praxis-os/ouroboros/__main__.py",
    ".praxis-os/ouroboros/requirements.txt",
    
    # Scripts (CRITICAL!)
    ".praxis-os/scripts/build_rag_index.py",  # Required for RAG index building!
    ".praxis-os/scripts/generate-manifest.py",
]

missing = [f for f in critical_files if not os.path.exists(f)]

if missing:
    print("❌ Missing critical files:")
    for f in missing:
        print(f"   - {f}")
    print("\nFIX: Re-run copy operations")
    exit(1)
else:
    print("✅ All critical files present")
```

---

## 🔍 Detailed Verification

Check that workflows directory is populated:

```python
import os

workflow_dirs = [
    ".praxis-os/workflows/spec_creation_v1",
    ".praxis-os/workflows/spec_execution_v1",
]

for workflow_dir in workflow_dirs:
    if not os.path.exists(workflow_dir):
        print(f"❌ Missing: {workflow_dir}")
        continue
    
    # Count files
    file_count = sum(len(files) for _, _, files in os.walk(workflow_dir))
    print(f"✅ {workflow_dir}: {file_count} files")

# Check for metadata.json specifically
for workflow_dir in workflow_dirs:
    metadata = os.path.join(workflow_dir, "metadata.json")
    if os.path.exists(metadata):
        print(f"✅ Found: {metadata}")
    else:
        print(f"❌ Missing: {metadata}")
```

**Expected output**:
```
✅ .praxis-os/workflows/spec_creation_v1: 38 files
✅ .praxis-os/workflows/spec_execution_v1: 9 files
✅ Found: .praxis-os/workflows/spec_creation_v1/metadata.json
✅ Found: .praxis-os/workflows/spec_execution_v1/metadata.json
```

---

## 🚨 Troubleshooting

### Issue: "Source path not found"

**Cause**: Running from wrong directory or source repo not available

**Fix**:
```python
import os

# Check if source repo is accessible
if not os.path.exists(f"{PRAXIS_OS_SOURCE}/dist/universal"):
    print("❌ Source repository not found")
    print("Current directory:", os.getcwd())
    print(f"Source path: {PRAXIS_OS_SOURCE}")
    print("\nFix: Ensure praxis-os is cloned/available")
    exit(1)
```

### Issue: "Permission denied" during copy

**Cause**: Target directory not writable

**Fix**:
```bash
# Check target directory permissions
ls -ld .praxis-os

# Should see something like: drwxr-xr-x
# The 'w' means writable
```

### Issue: Workflows directory empty after copy

**This means copy #3 failed!** Re-run the workflow copy:

```python
import shutil

shutil.copytree(
    f"{PRAXIS_OS_SOURCE}/dist/universal/workflows",
    ".praxis-os/workflows",
    dirs_exist_ok=True
)

# Verify
import os
count = sum(len(files) for _, _, files in os.walk(".praxis-os/workflows"))
print(f"Workflow files: {count}")  # Should be ~47
```

### Issue: Some files copied, others didn't

**Run selective re-copy**:

```python
# Identify what's missing, then copy just that
if not os.path.exists(".praxis-os/workflows/spec_creation_v1"):
    shutil.copytree(
        f"{PRAXIS_OS_SOURCE}/dist/universal/workflows/spec_creation_v1",
        ".praxis-os/workflows/spec_creation_v1"
    )
```

---

## 📊 Progress Check

At this point you should have:
- ✅ Standards files in `.praxis-os/standards/universal/`
- ✅ Workflow files in `.praxis-os/workflows/` (2 complete workflows)
- ✅ MCP server code in `.praxis-os/ouroboros/`
- ✅ Helper scripts in `.praxis-os/scripts/` (including `build_rag_index.py`!)
- ✅ All validation checkpoints passed

**Note**: The install script provides exact file counts during installation.

**If anything above is ❌, stop and fix before continuing.**

---

## 🎯 What's Next

You've copied all the content files. Now you need to handle agent-specific behavioral trigger files.

**Why these files are special**: Each agent uses different files that might already exist in the target project:
- **Cursor**: `.cursorrules` (project root)
- **Cline**: `.clinerules` (project root)
- **Claude Code**: `.claude/CLAUDE.md` (or `CLAUDE.md` for CLI)
- **GitHub Copilot**: `.github/copilot-instructions.md`

If these files exist, you CANNOT blindly overwrite them (that would destroy the user's existing configuration).

**Next step**: Route to agent-specific configuration guide.

---

## ➡️ NEXT STEP

**Read file**: `installation/03-agent-configuration.md`

That file will:
1. **Parse** the agent/IDE from the user's installation command (`"for <AGENT> (optional: in <IDE>)"`)
2. Route to the correct agent-specific configuration guide
3. Guide you through agent-specific file handling (`.cursorrules`, `.clinerules`, `.claude/CLAUDE.md`, `.github/copilot-instructions.md`, etc.)
4. Direct you to step 04 (config customization)

---

**Status**: Step 2 Complete ✅  
**Copied**: All required files (standards, workflows, server code, scripts)  
**Next File**: `03-agent-configuration.md`  
**Step**: 2 of 7

