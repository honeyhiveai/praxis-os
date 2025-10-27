# Dogfooding Architecture - Design Document

**Date:** 2025-10-06  
**Status:** Design Approved, Implementation Pending  
**Critical:** This document defines how Agent OS development validates installation/updates

---

## 🎯 Core Principle

**"Use Agent OS exactly like consumers do"**

If we use special symlinks or shortcuts, we can't validate:
- Installation process
- Update process  
- Real-world consumer experience
- Path resolution bugs
- File copy/distribution issues

---

## ❌ Current Architecture (WRONG)

### What We Have Now

```
praxis-os/
├── universal/                    # Framework source
│   └── standards/
│       └── ai-safety/
│           └── production-code-checklist.md
│
└── .praxis-os/                    # Local install (SPECIAL CASE)
    └── standards/
        └── universal/  → ../../universal/standards/  # ❌ SYMLINK
```

### Problems

1. **Not Real Dogfooding**
   - Consumers get COPIED files
   - We have symlinks (instant updates)
   - We can't catch copy/path bugs

2. **Can't Validate Installation**
   - Never test real installation flow
   - Installation bugs only found by consumers

3. **Can't Validate Updates**
   - Our "updates" are instant (symlink)
   - Consumers must re-install or pull
   - We don't test update process

4. **Confusing Mental Model**
   - Edit `universal/` → instant change via symlink
   - Consumers: Edit source → must re-install → change
   - Different workflow = missed bugs

---

## ✅ Correct Architecture (TRUE DOGFOODING)

### What We Should Have

```
praxis-os/
├── universal/                    # Framework SOURCE (for distribution)
│   ├── standards/                # Edit these to change framework
│   ├── usage/
│   └── workflows/
│
├── .praxis-os/                    # LOCAL INSTALL (like any consumer)
│   ├── standards/                # REAL COPIED FILES (no symlinks)
│   │   ├── universal/            # ✅ Copied from ../universal/standards/
│   │   ├── ai-safety/            # ✅ Copied framework content
│   │   └── development/          # Project-specific additions
│   ├── usage/                    # ✅ Copied from ../universal/usage/
│   ├── workflows/                # ✅ Copied from ../universal/workflows/
│   ├── venv/
│   ├── .cache/
│   └── config.json
│
└── mcp_server/                   # MCP server SOURCE (for distribution)
    └── agent_os_rag.py
```

### Benefits

1. ✅ **True Dogfooding** - Exact same setup as consumers
2. ✅ **Validates Installation** - We run real installation process
3. ✅ **Validates Updates** - We test update workflow
4. ✅ **Catches Path Bugs** - File copy/path resolution tested
5. ✅ **Clear Mental Model** - Edit source → re-install → change (same as consumers)

---

## 🔄 Development Workflows

### Workflow 1: Edit Framework Source

**Use Case:** Changing universal standards, usage docs, workflows

**Steps:**
```bash
# 1. Edit framework source
vim universal/standards/ai-safety/production-code-checklist.md

# 2. Re-install locally (like a consumer updating)
python scripts/install_agent_os.py --force
# OR
python .praxis-os/scripts/build_rag_index.py --force

# 3. Verify in Cursor
# Query MCP: "What is the production code checklist?"
# Should return updated content

# 4. Commit source changes
git add universal/standards/ai-safety/production-code-checklist.md
git commit -m "docs(standards): update production code checklist"
```

**Why this is GOOD:**
- ✅ Tests installation script
- ✅ Tests index rebuild
- ✅ Tests path resolution
- ✅ Same as consumers do

---

### Workflow 2: Edit Project-Specific Standards

**Use Case:** Python-specific guidance for this project only

**Steps:**
```bash
# 1. Edit project-specific file directly
vim .praxis-os/standards/development/python-concurrency.md

# 2. File watcher auto-rebuilds index
# (or manually: python .praxis-os/scripts/build_rag_index.py)

# 3. No re-install needed (not framework source)
```

**Why this is GOOD:**
- These files are NOT distributed
- Safe to edit in place
- Same as consumers adding their own standards

---

### Workflow 3: Edit MCP Server Code

**Use Case:** Changing MCP server functionality

**Steps:**
```bash
# 1. Edit source
vim mcp_server/agent_os_rag.py

# 2. Restart MCP server
# Cursor → Settings → MCP → Restart agent-os-rag

# 3. Test changes
# Use Cursor AI with updated MCP tools
```

**Note:** MCP server code is in source tree, not copied to `.praxis-os/`

---

## 📦 Installation Process

### Initial Installation

**What consumers do (and we should do):**

```bash
# Clone framework (consumers: install from package)
git clone https://github.com/honeyhiveai/praxis-os.git
cd praxis-os

# Run installation script
python scripts/install_agent_os.py

# Installation creates:
# - .praxis-os/ directory
# - Copies universal/ → .praxis-os/standards/universal/
# - Copies universal/usage/ → .praxis-os/usage/
# - Copies universal/workflows/ → .praxis-os/workflows/
# - Creates .praxis-os/venv/
# - Builds RAG index
# - Creates .praxis-os/config.json
```

**We test this EVERY time we re-install after editing source.**

---

### Update Process

**What consumers do (and we should test):**

```bash
# Option 1: Pull new version and re-install
git pull origin main
python scripts/install_agent_os.py --force

# Option 2: Package update (for distributed version)
pip install --upgrade praxis-os
agent-os update
```

**We validate this by:**
1. Editing `universal/` source
2. Running re-install
3. Verifying `.praxis-os/` updated correctly
4. Checking MCP finds new content

---

## 🔍 File Watching Behavior

### Current Behavior (WRONG with symlinks)

```python
# File watcher watches .praxis-os/standards/
observer.schedule(watcher, ".praxis-os/standards", recursive=True)

# Because of symlink:
# Edit universal/standards/foo.md
# → Visible as .praxis-os/standards/universal/foo.md (symlink)
# → File watcher triggers rebuild
# → Appears to work (but special case!)
```

### Correct Behavior (NO symlinks)

```python
# File watcher watches .praxis-os/standards/
observer.schedule(watcher, ".praxis-os/standards", recursive=True)

# With real files:
# Edit universal/standards/foo.md
# → NOT visible in .praxis-os/ (different file)
# → File watcher does NOT trigger
# → Must re-install to update .praxis-os/
# → This is CORRECT (same as consumers)
```

**Key Insight:**
- File watcher ONLY watches `.praxis-os/` (installed files)
- Does NOT watch `universal/` (framework source)
- Editing source requires re-install (correct behavior)

---

## 🚨 Critical Distinctions

### Framework Source vs. Installed Files

| Location | Purpose | Who Edits | Distribution |
|----------|---------|-----------|--------------|
| `universal/` | Framework source | Framework developers | YES (copied to consumers) |
| `.praxis-os/standards/universal/` | Installed framework | NO ONE (managed by install) | NO (consumer-local) |
| `.praxis-os/standards/development/` | Project-specific | Project developers | NO (project-local) |
| `mcp_server/` | MCP server source | Framework developers | YES (imported by install) |

**Rules:**
1. **NEVER edit `.praxis-os/standards/universal/`** (it's managed by install script)
2. **ALWAYS edit `universal/`** (source of truth)
3. **ALWAYS re-install** after editing framework source
4. **Project-specific files** can be edited directly in `.praxis-os/standards/development/`

---

## 🔧 Implementation Tasks

### Phase 1: Remove Symlinks

1. **Backup current `.praxis-os/`**
   ```bash
   mv .praxis-os .praxis-os.backup
   ```

2. **Remove from `.gitignore`** temporarily
   ```bash
   # We need to track that .praxis-os/ structure exists
   # But not the content (venv, cache)
   ```

3. **Update `.gitignore`**
   ```
   # .praxis-os/ content that should be ignored
   .praxis-os/venv/
   .praxis-os/.cache/
   .praxis-os/standards/universal/  # Installed, not source
   .praxis-os/standards/ai-safety/  # Installed, not source
   .praxis-os/usage/                # Installed, not source
   .praxis-os/workflows/            # Installed, not source
   
   # Track these (project-specific)
   !.praxis-os/standards/development/
   !.praxis-os/config.json
   ```

---

### Phase 2: Update Installation Script

**File:** `scripts/install_agent_os.py`

**Add:**
```python
def install_framework_content(target_dir: Path, source_dir: Path):
    """
    Copy framework content to target directory.
    
    This is how consumers install framework files.
    We use the EXACT same process for dogfooding.
    """
    import shutil
    
    # Remove existing (for updates)
    if target_dir.exists():
        shutil.rmtree(target_dir)
    
    # Copy source to target (deep copy, NOT symlink)
    shutil.copytree(source_dir, target_dir, symlinks=False)
    
    logger.info(f"✅ Copied {source_dir} → {target_dir}")

# During installation:
install_framework_content(
    target_dir=Path(".praxis-os/standards/universal"),
    source_dir=Path("universal/standards")
)

install_framework_content(
    target_dir=Path(".praxis-os/usage"),
    source_dir=Path("universal/usage")
)

install_framework_content(
    target_dir=Path(".praxis-os/workflows"),
    source_dir=Path("universal/workflows")
)
```

---

### Phase 3: Update Documentation

1. **Update `ARCHITECTURE.md`** with correct dogfooding model
2. **Update `CONTRIBUTING.md`** with edit/re-install workflow
3. **Add to `README.md`** about dogfooding approach
4. **Update `.cursorrules`** to query MCP about architecture before changes

---

### Phase 4: Validate

1. **Clean install:**
   ```bash
   rm -rf .praxis-os
   python scripts/install_agent_os.py
   ```

2. **Test framework edit:**
   ```bash
   echo "# TEST" >> universal/standards/test.md
   python scripts/install_agent_os.py --force
   # Verify: .praxis-os/standards/universal/test.md exists
   ```

3. **Test MCP search:**
   ```
   Query: "test standard"
   # Should find the new test.md
   ```

4. **Test file watcher:**
   ```bash
   # Edit .praxis-os/standards/development/python-testing.md
   # File watcher should trigger rebuild
   # Query MCP to verify
   ```

---

## 📊 Comparison Matrix

| Scenario | Current (Symlinks) | Correct (Copies) |
|----------|-------------------|------------------|
| Edit `universal/standards/foo.md` | Instant change (symlink) | Must re-install |
| File watcher triggers | YES (via symlink) | NO (different file) |
| Tests installation | NO (special case) | YES (real process) |
| Tests updates | NO (instant) | YES (re-install) |
| Same as consumers | NO (symlinks) | YES (copies) |
| Dogfooding validity | ❌ Fake | ✅ Real |

---

## 🎯 Success Criteria

After implementation:

- [ ] No symlinks in `.praxis-os/`
- [ ] All files in `.praxis-os/` are real copies
- [ ] Editing `universal/` requires re-install to see changes
- [ ] File watcher only triggers on `.praxis-os/` edits (not `universal/`)
- [ ] Installation script tested on EVERY framework edit
- [ ] Same workflow as consumers
- [ ] Documentation explains edit → re-install → verify cycle
- [ ] `.gitignore` properly separates source (tracked) vs installed (ignored)

---

## 🚀 Next Steps

1. **Review this design** with team
2. **Approve architecture change**
3. **Implement Phase 1-4** (remove symlinks, update install, docs, validate)
4. **Update `.cursorrules`** to enforce this model
5. **Create "Contributing to Framework" guide** explaining the workflow

---

**Related Documents:**
- `ARCHITECTURE.md` - Current architecture (needs update)
- `CONTRIBUTING.md` - How to contribute (needs update)
- `scripts/install_agent_os.py` - Installation script (needs update)
- `.cursorrules` - AI behavior rules (needs update)
