# Step 1: Create Directory Structure

**Previous**: `00-START.md`  
**Current**: Creating all required directories  
**Next**: `02-copy-files.md`

---

## 🎯 What This Step Does

Create the complete `.praxis-os/` directory structure that the MCP server requires.

**Why this matters**: The MCP server validates that these directories exist at startup. If any are missing, the server will fail to start with a validation error.

**Time**: ~30 seconds

---

## 📁 Required Directories (8 total)

The MCP server requires exactly these directories:

```
.praxis-os/
├── standards/
│   └── universal/          # Universal CS fundamentals
├── usage/                   # prAxIs OS usage docs
├── workflows/               # Workflow definitions (CRITICAL!)
├── mcp_server/              # MCP server code
├── .cache/                  # Vector index and state files
└── specs/                   # User-created specs
    ├── review/              # Specs awaiting approval
    ├── approved/            # Specs ready to implement
    └── completed/           # Finished implementations

.cursor/                     # Cursor configuration
```

**Total**: 7 directories under `.praxis-os/` + 1 `.cursor/` directory

---

## ⚠️ Critical Directory: workflows/

**Most commonly forgotten directory**: `.praxis-os/workflows/`

The MCP server's `ConfigValidator` explicitly checks for:
- `.praxis-os/standards/`
- `.praxis-os/usage/`
- `.praxis-os/workflows/` ← **If this is missing, server won't start!**

From `mcp_server/config/validator.py`:
```python
for name in ["standards_path", "usage_path", "workflows_path"]:
    if not path.exists():
        errors.append(f"❌ {name} does not exist: {path}")
```

---

## 🔨 Commands to Create Directories

### Option A: Python (Recommended)

```python
import os

# Create all required directories
directories = [
    ".praxis-os/standards/universal",
    ".praxis-os/usage",
    ".praxis-os/workflows",          # ← Don't forget this!
    ".praxis-os/specs/review",       # Specs awaiting approval
    ".praxis-os/specs/approved",     # Specs ready to implement
    ".praxis-os/specs/completed",    # Finished implementations
    ".praxis-os/mcp_server",
    ".praxis-os/.cache",
    ".cursor",
]

for directory in directories:
    os.makedirs(directory, exist_ok=True)
    print(f"✅ Created: {directory}")

print("\n✅ All directories created")
```

### Option B: Shell Commands

**Linux / macOS / WSL2**:
```bash
mkdir -p .praxis-os/standards/universal
mkdir -p .praxis-os/usage
mkdir -p .praxis-os/workflows
mkdir -p .praxis-os/specs/review
mkdir -p .praxis-os/specs/approved
mkdir -p .praxis-os/specs/completed
mkdir -p .praxis-os/mcp_server
mkdir -p .praxis-os/.cache
mkdir -p .cursor
```

**Windows (PowerShell)**:
```powershell
New-Item -ItemType Directory -Force -Path ".praxis-os\standards\universal"
New-Item -ItemType Directory -Force -Path ".praxis-os\usage"
New-Item -ItemType Directory -Force -Path ".praxis-os\workflows"
New-Item -ItemType Directory -Force -Path ".praxis-os\specs\review"
New-Item -ItemType Directory -Force -Path ".praxis-os\specs\approved"
New-Item -ItemType Directory -Force -Path ".praxis-os\specs\completed"
New-Item -ItemType Directory -Force -Path ".praxis-os\mcp_server"
New-Item -ItemType Directory -Force -Path ".praxis-os\.cache"
New-Item -ItemType Directory -Force -Path ".cursor"
```

---

## ✅ Validation Checkpoint #1

After creating directories, verify they all exist:

```python
import os

required_dirs = [
    ".praxis-os/standards/universal",
    ".praxis-os/usage",
    ".praxis-os/workflows",       # ← Most important!
    ".praxis-os/specs/review",
    ".praxis-os/specs/approved",
    ".praxis-os/specs/completed",
    ".praxis-os/mcp_server",
    ".praxis-os/.cache",
    ".cursor",
]

missing = [d for d in required_dirs if not os.path.exists(d)]

if missing:
    print("❌ Missing directories:")
    for d in missing:
        print(f"   - {d}")
    print("\nFIX: Create the missing directories before continuing")
    exit(1)
else:
    print("✅ All required directories exist")
```

**Expected output**: `✅ All required directories exist`

**If validation fails**: Re-run the creation commands, then re-run validation.

---

## 🔍 Visual Verification

You can also manually check:

```bash
ls -la .praxis-os/
```

**Expected output**:
```
drwxr-xr-x  .cache/
drwxr-xr-x  mcp_server/
drwxr-xr-x  specs/
drwxr-xr-x  standards/
drwxr-xr-x  usage/
drwxr-xr-x  workflows/      ← Must be present!
```

```bash
ls -la .praxis-os/specs/
```

**Expected output**:
```
drwxr-xr-x  review/         ← Specs awaiting approval
drwxr-xr-x  approved/       ← Specs ready to implement
drwxr-xr-x  completed/      ← Finished implementations
```

```bash
ls -la .praxis-os/standards/
```

**Expected output**:
```
drwxr-xr-x  universal/
```

---

## 🚨 Troubleshooting

### Issue: "Permission denied"

**Cause**: No write permission in current directory  
**Fix**:
```bash
# Check permissions
ls -ld .
# Should show write permission (w) for your user

# If not, you may be in wrong directory
pwd    # Should show your project root
```

### Issue: Directories created but empty

**This is normal at this stage!** Directories are empty right now. The next step (02-copy-files.md) will populate them with content.

### Issue: ".praxis-os already exists"

**Cause**: prAxIs OS might already be installed  
**Options**:
1. **Update**: Remove old `.praxis-os/` and reinstall
2. **Keep**: If it's a valid installation, skip to validation
3. **Ask user**: What would they like to do?

```python
if os.path.exists(".praxis-os"):
    print("⚠️  .praxis-os/ already exists. Options:")
    print("1. Remove and reinstall (fresh install)")
    print("2. Keep and skip to validation")
    print("3. Cancel installation")
    # Get user input and proceed accordingly
```

---

## 📊 Progress Check

At this point you should have:
- ✅ 7 directories under `.praxis-os/`
- ✅ 1 `.cursor/` directory
- ✅ All directories are empty (normal)
- ✅ Validation checkpoint passed

**If anything above is ❌, stop and fix before continuing.**

---

## 🎯 What's Next

You've created the directory structure. Now you need to fill it with content.

**Next step**: Copy files from the source repository.

---

## ➡️ NEXT STEP

**Read file**: `installation/02-copy-files.md`

That file will:
1. Copy universal standards
2. Copy usage documentation
3. Copy workflows (fills the workflows/ directory you just created!)
4. Copy MCP server code
5. Validate all files copied correctly
6. Direct you to step 03

---

**Status**: Step 1 Complete ✅  
**Created**: 8 directories  
**Next File**: `02-copy-files.md`  
**Step**: 2 of 5

