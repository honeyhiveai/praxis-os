# Dogfooding Model - Development in Consumer Environment

**Purpose:** How to develop prAxIs OS by using it exactly like consumers do

**Audience:** prAxIs OS framework developers

**Status:** Active - Canonical development workflow

**Keywords:** local-first development, installation testing, edit-test loop, copy up to skeleton, deployed directory structure, praxis-os installation paths, skeleton source versus installed target, hot reload cycle, reinstall validation purpose, server implementation file location, task definition file placement, helper script storage, end-user pathing, rapid iteration mechanics, where files live during development

**NOT covered here (see `meta-development-patterns.md`):** documentation decisions, error diagnosis mindset, API design choices, information architecture (what goes where in docs)

---

## 🎯 TL;DR - Local-First Development Rule

**"Develop EVERYTHING in `.praxis-os/` first, copy up to skeleton when shipping"**

This standard covers ITERATION MECHANICS: where files live during development, how to test changes, when to promote to source.

- ✅ Edit in `.praxis-os/` (installed environment, real paths)
- ✅ Validate locally (hot reload, semantic queries, task execution)
- ✅ Promote to skeleton (`universal/`, `scripts/`, `mcp_server/`) when shipping to users
- ✅ Full reinstall = QA checkpoint (not iteration step)

**No exceptions.** This validates installation process, real paths, and end-user experience.

**Note:** For documentation philosophy (what to write where, error diagnosis, API exposure), see `meta-development-patterns.md`.

---

## ❌ The Problem - Source-Directory Editing

**Anti-pattern:** Modifying source directories (`universal/`, `scripts/`, `mcp_server/`)

**Why this fails:**

1. **Not Runtime Environment**
   - Users execute from `.praxis-os/` installed paths
   - You're modifying distribution source
   - Path conflicts, task execution issues hidden

2. **Can't Validate Install Process**
   - Never test installation procedure during iteration
   - Copy issues only found when users install

3. **Different Testing Cycle**
   - You: Modify source → changes work instantly (edit-in-place)
   - Users: Must reinstall to see changes
   - Different experience = missed defects

4. **Task Execution Paths Wrong**
   - Tasks execute from `.praxis-os/workflows/` in runtime environment
   - Editing in `universal/workflows/` doesn't test actual execution paths

**Result:** Framework authors have fundamentally different experience than downstream users.

---

## ✅ The Solution - Installed-Location Editing

**Canonical architecture:**

```
praxis-os/
├── scripts/                      # SOURCE (distribution origin)
├── universal/                    # SOURCE (distribution origin)
├── mcp_server/                   # SOURCE (distribution origin)
│
├── .praxis-os/                   # INSTALLED (runtime environment)
│   ├── scripts/                  # ← EDIT HERE for published scripts
│   ├── standards/
│   │   ├── universal/            # ← EDIT HERE for shipped docs
│   │   └── development/          # ← EDIT HERE for internal docs
│   ├── workflows/                # ← EDIT HERE for task definitions
│   ├── mcp_server/               # ← EDIT HERE for server modules
│   ├── venv/
│   └── .cache/
│
└── .praxis-os/bin/               # INTERNAL TOOLS (never distributed)
```

**The rule:** Edit in `.praxis-os/` (runtime paths), promote to source when distributing.

### Benefits

1. ✅ **Actual Runtime Environment** - Exact paths, execution context as users experience
2. ✅ **Rapid Testing** - No reinstall for validation (hot reload, service restart)
3. ✅ **Validates Paths** - Task execution, imports, file resolution tested
4. ✅ **Promotion Validates Install** - Reinstall = QA checkpoint
5. ✅ **Same Mental Model** - Your testing cycle = user experience

---

## 🔄 Development Workflows - All Start Local

### Workflow 1: MCP Server Development

**Use Case:** Adding features, fixing bugs in MCP server

**Steps:**
```bash
# 1. Dev in local install (consumer environment)
vim .praxis-os/mcp_server/rag_engine.py

# 2. Restart MCP to test
# Cursor → Cmd+Shift+P → "MCP: Restart Server"

# 3. Test with queries/tools
# Changes visible immediately in consumer environment

# 4. When ready to ship, copy up
cp .praxis-os/mcp_server/rag_engine.py mcp_server/

# 5. Reinstall = QA validation
python scripts/install-praxis-os.py --force
# Verify copied file works correctly via installation
```

**Why installed-location editing:**
- ✅ Test in exact runtime paths
- ✅ Rapid iteration (restart, not reinstall)
- ✅ Validate import paths, file resolution

---

### Workflow 2: Consumer Script Development

**Use Case:** Helper scripts for multi-agent setup, utilities

**Steps:**
```bash
# 1. Dev in local install
vim .praxis-os/scripts/new-helper-tool.py
chmod +x .praxis-os/scripts/new-helper-tool.py

# 2. Test immediately
python .praxis-os/scripts/new-helper-tool.py

# 3. Iterate until working
# No reinstall needed - direct execution

# 4. When ready to ship, copy up
cp .praxis-os/scripts/new-helper-tool.py scripts/

# 5. Reinstall = QA validation
python scripts/install-praxis-os.py --force
ls -la .praxis-os/scripts/new-helper-tool.py
```

**Why local-first:**
- ✅ Test from installed location
- ✅ Fast iteration cycle
- ✅ Validate consumer experience

---

### Workflow 3: Workflow Development

**Use Case:** Creating new workflows for consumers

**Steps:**
```bash
# 1. Dev in local install (where workflows execute)
mkdir -p .praxis-os/workflows/my-new-workflow
vim .praxis-os/workflows/my-new-workflow/metadata.json
vim .praxis-os/workflows/my-new-workflow/phase-1.md

# 2. Test workflow execution
# Use pos_workflow tool to run from .praxis-os/workflows/

# 3. Iterate on phases, gates, evidence
# Workflows execute from .praxis-os/ - you're testing real paths

# 4. When ready to ship, copy up
cp -r .praxis-os/workflows/my-new-workflow \
      universal/workflows/

# 5. Reinstall = QA validation
python scripts/install-praxis-os.py --force
# Verify workflow still works after installation
```

**Why local-first:**
- ✅ Workflows execute from `.praxis-os/workflows/` in consumer env
- ✅ Test actual execution paths, not source paths
- ✅ Catch path/reference bugs early

---

### Workflow 4: Universal Standards Development

**Use Case:** Creating standards that will ship to consumers

**Steps:**
```bash
# 1. Dev in local install (where standards are queried from)
vim .praxis-os/standards/universal/testing/new-pattern.md

# 2. File watcher auto-rebuilds index
# Or manually: python .praxis-os/scripts/build_rag_index.py

# 3. Query to validate
# Search: "new testing pattern"
# Verify content is discoverable and useful

# 4. When ready to ship, copy up
cp .praxis-os/standards/universal/testing/new-pattern.md \
   universal/standards/testing/

# 5. Reinstall = QA validation
python scripts/install-praxis-os.py --force
# Verify standard is still queryable after installation
```

**Why local-first:**
- ✅ Test RAG indexing from installed location
- ✅ Validate search discoverability
- ✅ Fast query iteration

---

### Workflow 5: Local-Only Standards Development

**Use Case:** Project-specific guidance (never ships)

**Steps:**
```bash
# 1. Dev in local install
vim .praxis-os/standards/development/local-dev-scripts.md

# 2. File watcher auto-rebuilds index

# 3. Query to validate
# Search: "dev scripts organization"

# 4. NEVER copy up (local-only)
# Commit directly to repo
git add .praxis-os/standards/development/local-dev-scripts.md
git commit -m "Add local dev scripts standard"
```

**Why local-only:**
- ✅ Framework dev knowledge
- ✅ Not relevant to consumers
- ✅ Committed but never shipped

---

## 📋 Copy-Up Decision Tree

**When you're ready to ship from `.praxis-os/` to skeleton:**

```
Is this ready to ship to consumers?
├─ YES
│  └─ Copy up to skeleton:
│     ├─ .praxis-os/mcp_server/*.py      → mcp_server/
│     ├─ .praxis-os/scripts/*.py         → scripts/
│     ├─ .praxis-os/workflows/my-wf/     → universal/workflows/
│     └─ .praxis-os/standards/universal/ → universal/standards/
│
└─ NO (dev-only or not ready)
   └─ Keep in .praxis-os/:
      ├─ .praxis-os/standards/development/ (never ship)
      ├─ .praxis-os/bin/ (dev tools, never ship)
      └─ .praxis-os/* (work in progress)

---

## 🔍 File Watching Behavior

**The file watcher:**
- ✅ Watches `.praxis-os/standards/` (installed/development location)
- ❌ Does NOT watch skeleton directories (`universal/`, `scripts/`, `mcp_server/`)

**This is correct:**

```python
# File watcher configuration
observer.schedule(watcher, ".praxis-os/standards", recursive=True)

# Scenario 1: Edit in .praxis-os/ (dogfooding workflow)
vim .praxis-os/standards/universal/testing/new-pattern.md
# → File watcher detects change
# → Auto-rebuilds index
# → Immediately queryable
# ✅ Fast iteration!

# Scenario 2: Edit skeleton (anti-pattern)
vim universal/standards/testing/new-pattern.md
# → File watcher does NOT detect (different directory)
# → Index not rebuilt
# → NOT queryable until reinstall
# ❌ Slow iteration, breaks dogfooding

# Scenario 3: Copy-up for shipping
cp .praxis-os/standards/universal/testing/new-pattern.md \
   universal/standards/testing/
# → Skeleton updated for distribution
# → Reinstall validates installation process
```

**Key Insight:** Develop in `.praxis-os/` for fast iteration with file watcher.

---

## 🚨 Critical Distinctions - Skeleton vs Local Install

### Directory Purpose Matrix

| Location | Purpose | Dev Location | Shipping Destination |
|----------|---------|--------------|---------------------|
| `.praxis-os/mcp_server/` | **DEV HERE** | Fast iteration | → `mcp_server/` |
| `.praxis-os/scripts/` | **DEV HERE** | Fast iteration | → `scripts/` |
| `.praxis-os/workflows/` | **DEV HERE** | Real execution paths | → `universal/workflows/` |
| `.praxis-os/standards/universal/` | **DEV HERE** | RAG testing | → `universal/standards/` |
| `.praxis-os/standards/development/` | **DEV HERE** | Local-only (never ship) | (committed, not shipped) |
| `.praxis-os/bin/` | **DEV HERE** | Dev tools only | (committed, not shipped) |
| `mcp_server/` | Skeleton | Copy-up target | Shipped to consumers |
| `scripts/` | Skeleton | Copy-up target | Shipped to consumers |
| `universal/` | Skeleton | Copy-up target | Shipped to consumers |

**The Rule:**
1. **ALWAYS dev in `.praxis-os/`** (consumer environment)
2. **NEVER dev in skeleton** (`universal/`, `scripts/`, `mcp_server/`)
3. **Copy up when ready to ship** (QA via reinstall)
4. **Reinstall = validation** (not iteration)

---

## 🎓 Reinstall Purpose - QA Validation

**Reinstall is NOT for iteration:**
- ❌ Don't reinstall to test every change
- ❌ Don't use reinstall as part of dev loop

**Reinstall IS for validation:**
- ✅ After copy-up, verify installation works
- ✅ Periodic QA check (weekly dogfooding validation)
- ✅ Before releasing new version
- ✅ Testing installation script changes

**Fast iteration cycle:**
```bash
# ✅ CORRECT: Dev in .praxis-os/, test immediately
vim .praxis-os/mcp_server/rag_engine.py
# Restart MCP → test → iterate

# ❌ WRONG: Dev in skeleton, reinstall each time
vim mcp_server/rag_engine.py
python scripts/install-praxis-os.py --force  # Slow!
# Restart MCP → test → reinstall again → slow!
```

**When to reinstall:**
1. After copy-up (QA the installation)
2. Weekly validation (ensure dogfooding still works)
3. Before git commit (final check)
4. When installation script changes

---

## 📊 Workflow Comparison

| Scenario | Skeleton-First (Anti-pattern) | Local-First (Dogfooding) |
|----------|-------------------------------|--------------------------|
| Edit location | `universal/standards/foo.md` | `.praxis-os/standards/universal/foo.md` |
| File watcher | NO (wrong directory) | YES (instant rebuild) |
| Testing cycle | Edit → reinstall → test | Edit → test (instant) |
| Validates paths | NO (source paths) | YES (consumer paths) |
| Iteration speed | Slow (reinstall each time) | Fast (direct testing) |
| Consumer environment | ❌ Different | ✅ Identical |
| Dogfooding validity | ❌ Fake | ✅ Real |

---

## 🔍 Questions This Answers

**"Where should I develop MCP server code?"**
→ `.praxis-os/mcp_server/` (consumer environment, fast iteration)

**"Where should I create a new workflow?"**
→ `.praxis-os/workflows/` (real execution paths, test where it runs)

**"Where should I write a new universal standard?"**
→ `.praxis-os/standards/universal/` (RAG testing, query validation)

**"When do I copy up to skeleton?"**
→ When ready to ship to consumers (validated locally first)

**"Why not develop in `universal/` or `scripts/`?"**
→ Wrong paths, slow iteration, doesn't test consumer environment

**"What's the purpose of reinstall?"**
→ QA validation of installation, not iteration loop

**"How do I know if it's ready to ship?"**
→ Tested in `.praxis-os/`, works correctly, validated with dogfooding

**"What's the iteration cycle?"**
→ Edit `.praxis-os/` → test → iterate (no reinstall until copy-up)

**"Where do local-only standards go?"**
→ `.praxis-os/standards/development/` (never copy up, committed but not shipped)

**"What about dev tools like validators?"**
→ `.praxis-os/bin/` (dev-only, never shipped)

---

## Related Standards

**Development workflow (this document's domain):**
- `local-dev-scripts.md` - Where dev-only scripts live (bin/ vs scripts/)
- `multi-agent-architecture.md` - Secondary agent setup

**Standards creation mindset (different domain):**
- `meta-development-patterns.md` - Where to document knowledge, bug attribution, abstraction boundaries

**Clear separation:**
- **This doc answers:** "Where do I edit this file?" "How do I iterate?" "When do I copy up?"
- **Meta-dev answers:** "Should I document this in universal/?" "Is this a bug?" "Should consumers see this?"

---

**Remember:** Develop where consumers use it (`.praxis-os/`), copy up when shipping (skeleton). Reinstall = QA validation, not iteration.
