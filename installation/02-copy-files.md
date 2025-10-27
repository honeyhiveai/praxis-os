# Step 2: Copy Files from Source

**Previous**: `01-directories.md` (created directories)  
**Current**: Copying all required files  
**Next**: `03-cursorrules.md`

---

## 🎯 What This Step Does

Copy all required content from the source repository (`praxis-os/`) to your project.

**What gets copied**:
1. Universal standards (CS fundamentals)
2. Usage documentation (how to use prAxIs OS)
3. Workflows (spec_creation_v1, spec_execution_v1)
4. MCP server code (Python code that runs the server)

**Time**: ~1-2 minutes (depends on file system speed)

---

## 📦 Copy Operations (4 total)

### Copy #1: Universal Standards

**Source**: `{AGENT_OS_SOURCE}/universal/standards/`  
**Destination**: `.praxis-os/standards/universal/`  
**Contents**: ~30 markdown files with CS fundamentals

```python
import shutil

# Use AGENT_OS_SOURCE from step 00
shutil.copytree(
    f"{AGENT_OS_SOURCE}/universal/standards",
    ".praxis-os/standards/universal",
    dirs_exist_ok=True
)
print("✅ Copied universal standards")
```

**Note**: `AGENT_OS_SOURCE` is the temp directory you created in step 00.

**What's in there**: Architecture patterns, concurrency, testing, security, etc.

---

### Copy #2: Usage Documentation

**Source**: `praxis-os/universal/usage/`  
**Destination**: `.praxis-os/usage/`  
**Contents**: ~5 markdown files explaining how to use prAxIs OS

```python
shutil.copytree(
    "praxis-os/universal/usage",
    ".praxis-os/usage",
    dirs_exist_ok=True
)
print("✅ Copied usage documentation")
```

**What's in there**: Creating specs, operating model, MCP usage guide

---

### Copy #3: Workflows (CRITICAL!)

**Source**: `praxis-os/universal/workflows/`  
**Destination**: `.praxis-os/workflows/`  
**Contents**: ~50 files (spec_creation_v1 + spec_execution_v1)

⚠️ **This is the one people forget!**

```python
shutil.copytree(
    "praxis-os/universal/workflows",
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

### Copy #4: MCP Server Code

**Source**: `praxis-os/mcp_server/`  
**Destination**: `.praxis-os/mcp_server/`  
**Contents**: ~20 Python files + requirements.txt

```python
shutil.copytree(
    "praxis-os/mcp_server",
    ".praxis-os/mcp_server",
    dirs_exist_ok=True
)
print("✅ Copied MCP server")
```

**What's in there**: RAG engine, workflow engine, server factory, etc.

---

### Copy #5: Scripts (CRITICAL - RAG Index Builder!)

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

**Why it's critical**: The MCP server's `factory.py` imports `IndexBuilder` from this script to build the RAG index when `.praxis-os/.cache/vector_index/` doesn't exist. Without it, installation fails.

---

## 🔨 Complete Copy Script

**Run this Python script** to copy all files:

```python
import shutil
import os

# AGENT_OS_SOURCE from step 00 (temp directory)
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
print(f"Source: {AGENT_OS_SOURCE}\n")

# Copy #1: Universal standards
success1 = copy_with_status(
    f"{AGENT_OS_SOURCE}/universal/standards",
    ".praxis-os/standards/universal",
    "Universal standards"
)

# Copy #2: Usage docs
success2 = copy_with_status(
    f"{AGENT_OS_SOURCE}/universal/usage",
    ".praxis-os/usage",
    "Usage documentation"
)

# Copy #3: Workflows (CRITICAL!)
success3 = copy_with_status(
    f"{AGENT_OS_SOURCE}/universal/workflows",
    ".praxis-os/workflows",
    "Workflows"
)

# Copy #4: MCP server
success4 = copy_with_status(
    f"{AGENT_OS_SOURCE}/mcp_server",
    ".praxis-os/mcp_server",
    "MCP server"
)

# Copy #5: Scripts (CRITICAL!)
success5 = copy_with_status(
    f"{AGENT_OS_SOURCE}/scripts",
    ".praxis-os/scripts",
    "Scripts"
)

# Copy #6: .cursorrules (we'll handle merge in step 03, but copy for now)
# This will be overwritten in step 03 if needed

# Summary
print("\n" + "="*50)
if all([success1, success2, success3, success4, success5]):
    print("✅ ALL FILES COPIED SUCCESSFULLY")
    print(f"\n📝 Temp source still at: {AGENT_OS_SOURCE}")
    print("   (Will be deleted in step 05)")
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
✅ MCP server: 23 files copied
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
    
    # Usage
    ".praxis-os/usage/creating-specs.md",
    ".praxis-os/usage/mcp-usage-guide.md",
    
    # Workflows (MOST IMPORTANT!)
    ".praxis-os/workflows/spec_creation_v1/metadata.json",
    ".praxis-os/workflows/spec_execution_v1/metadata.json",
    
    # MCP Server
    ".praxis-os/mcp_server/__main__.py",
    ".praxis-os/mcp_server/requirements.txt",
    
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
if not os.path.exists("praxis-os/universal"):
    print("❌ Source repository not found")
    print("Current directory:", os.getcwd())
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
    "praxis-os/universal/workflows",
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
        "praxis-os/universal/workflows/spec_creation_v1",
        ".praxis-os/workflows/spec_creation_v1"
    )
```

---

## 📊 Progress Check

At this point you should have:
- ✅ ~31 files in `.praxis-os/standards/universal/`
- ✅ ~5 files in `.praxis-os/usage/`
- ✅ ~47 files in `.praxis-os/workflows/` (across 2 workflows)
- ✅ ~23 files in `.praxis-os/mcp_server/`
- ✅ ~3 files in `.praxis-os/scripts/` (including `build_rag_index.py`!)
- ✅ All validation checkpoints passed

**Total**: ~109 files copied

**If anything above is ❌, stop and fix before continuing.**

---

## 🎯 What's Next

You've copied all the content files. Now you need to handle `.cursorrules`.

**Why `.cursorrules` is special**: It might already exist in the target project. If it does, you CANNOT blindly overwrite it (that would destroy the user's existing Cursor configuration).

**Next step**: Safely handle `.cursorrules` file.

---

## ➡️ NEXT STEP

**Read file**: `installation/03-cursorrules.md`

That file will:
1. Check if `.cursorrules` already exists
2. If no: Copy directly (safe)
3. If yes: Ask user how to merge (preserve their rules!)
4. Validate merge was successful
5. Direct you to step 04

---

**Status**: Step 2 Complete ✅  
**Copied**: ~106 files  
**Next File**: `03-cursorrules.md`  
**Step**: 3 of 5

