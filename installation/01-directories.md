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

## 📁 Required Directories

The installation creates this directory structure:

```
.praxis-os/
├── standards/
│   ├── universal/          # Universal CS fundamentals (from framework)
│   └── development/        # Project-specific standards (LLM-generated)
├── workflows/              # Workflow definitions (CRITICAL!)
├── ouroboros/              # MCP server code
├── scripts/                # Helper scripts (RAG index builder, etc.)
├── workspace/              # Temporary working files
│   ├── design/             # Design documents
│   ├── analysis/           # Analysis artifacts
│   └── scratch/            # Scratch space
├── specs/                  # User-created specs
│   ├── review/             # Specs awaiting approval
│   ├── approved/           # Specs ready to implement
│   └── completed/          # Finished implementations
├── .cache/                 # RAG index and state files (ephemeral)
└── venv/                   # Python virtual environment (ephemeral)
```

**Note**: The install script creates these automatically. No manual creation needed.

---

## ⚠️ Critical Directory: workflows/

**Most commonly forgotten directory**: `.praxis-os/workflows/`

The MCP server requires this directory to exist. If missing, workflow tools will fail.

**Good news**: The `install-praxis-os.py` script creates all directories automatically, so you don't need to worry about this when using the script.

---

## 🔨 Manual Directory Creation (If Script Fails)

**⚠️ IMPORTANT**: Use the `install-praxis-os.py` script instead. This manual path is only for troubleshooting.

### Option A: Python

```python
import os

# Create all required directories (matches install script)
directories = [
    ".praxis-os/standards/universal",
    ".praxis-os/standards/development",
    ".praxis-os/workflows",
    ".praxis-os/ouroboros",
    ".praxis-os/scripts",
    ".praxis-os/workspace/design",
    ".praxis-os/workspace/analysis",
    ".praxis-os/workspace/scratch",
    ".praxis-os/specs/review",
    ".praxis-os/specs/approved",
    ".praxis-os/specs/completed",
    ".praxis-os/.cache/vector_index",
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
mkdir -p .praxis-os/standards/development
mkdir -p .praxis-os/workflows
mkdir -p .praxis-os/ouroboros
mkdir -p .praxis-os/scripts
mkdir -p .praxis-os/workspace/{design,analysis,scratch}
mkdir -p .praxis-os/specs/{review,approved,completed}
mkdir -p .praxis-os/.cache/vector_index
```

**Windows (PowerShell)**:
```powershell
New-Item -ItemType Directory -Force -Path ".praxis-os\standards\universal"
New-Item -ItemType Directory -Force -Path ".praxis-os\standards\development"
New-Item -ItemType Directory -Force -Path ".praxis-os\workflows"
New-Item -ItemType Directory -Force -Path ".praxis-os\ouroboros"
New-Item -ItemType Directory -Force -Path ".praxis-os\scripts"
New-Item -ItemType Directory -Force -Path ".praxis-os\workspace\design"
New-Item -ItemType Directory -Force -Path ".praxis-os\workspace\analysis"
New-Item -ItemType Directory -Force -Path ".praxis-os\workspace\scratch"
New-Item -ItemType Directory -Force -Path ".praxis-os\specs\review"
New-Item -ItemType Directory -Force -Path ".praxis-os\specs\approved"
New-Item -ItemType Directory -Force -Path ".praxis-os\specs\completed"
New-Item -ItemType Directory -Force -Path ".praxis-os\.cache\vector_index"
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
    ".praxis-os/ouroboros",
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
drwxr-xr-x  ouroboros/
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

