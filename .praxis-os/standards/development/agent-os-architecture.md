# prAxIs OS Architecture

**Last Updated:** 2025-10-06  
**Status:** TRUE DOGFOODING (no symlinks)

---

## 🎯 Core Principles

1. **Dogfooding** - We use prAxIs OS exactly like consumers do
2. **No Shortcuts** - No symlinks, no special cases, feel all the pain
3. **Two-Venv Architecture** - MCP server and project code run in separate virtualenvs
4. **MCP-First** - All prAxIs OS knowledge accessed via MCP tools, not direct file reading

---

## 📂 Directory Structure

```
praxis-os/
├── universal/                        # FRAMEWORK SOURCE (edit this)
│   ├── standards/                   # Universal standards (all languages)
│   │   ├── ai-safety/
│   │   ├── architecture/
│   │   ├── concurrency/
│   │   ├── database/
│   │   ├── documentation/
│   │   ├── failure-modes/
│   │   ├── meta-workflow/
│   │   ├── performance/
│   │   ├── security/
│   │   └── testing/
│   ├── usage/                       # Usage guides for AI agents
│   │   ├── mcp-usage-guide.md
│   │   ├── operating-model.md
│   │   └── creating-specs.md
│   └── workflows/                   # Workflow definitions
│       ├── test_generation_v3/
│       └── production_code_v2/
│
├── mcp_server/                       # MCP SERVER SOURCE (edit this)
│   ├── praxis_os_rag.py              # Main MCP server
│   ├── rag_engine.py                # RAG search engine
│   ├── workflow_engine.py           # Workflow phase gating
│   ├── state_manager.py             # Workflow state persistence
│   ├── chunker.py                   # Document chunking
│   ├── framework_generator.py       # Workflow generation
│   └── requirements.txt
│
├── .praxis-os/                        # LOCAL INSTALL (like consumers)
│   ├── mcp_server/                  # ✅ COPIED from ../mcp_server/
│   ├── standards/                   
│   │   ├── universal/               # ✅ COPIED from ../../universal/standards/
│   │   ├── ai-assistant/            # Project-specific (AI guidance)
│   │   └── development/             # Project-specific (Python guidance)
│   ├── usage/                       # ✅ COPIED from ../../universal/usage/
│   ├── workflows/                   # ✅ COPIED from ../../universal/workflows/
│   ├── venv/                        # MCP server virtualenv
│   ├── .cache/                      # RAG vector index (LanceDB)
│   ├── scripts/                     # Index build scripts
│   └── config.json                  # Path configuration
│
├── tests/                            # Test suite
│   ├── unit/
│   └── integration/
│
├── .cursorrules                      # AI behavior rules
├── CONTRIBUTING.md                   # How to contribute
└── README.md                         # Project overview
```

---

## 🔄 Dogfooding Model

### The Problem Symlinks Caused

**OLD (WRONG):**
```
.praxis-os/standards/universal/ → ../../universal/standards/  # ❌ SYMLINK
```

**Problems:**
- We got instant updates (consumers must re-install)
- File watcher worked via symlink (special case)
- Never tested installation process
- Couldn't catch copy/path bugs

### The Solution (TRUE DOGFOODING)

**NEW (CORRECT):**
```
.praxis-os/standards/universal/  # ✅ REAL COPIED FILES
```

**Benefits:**
- We experience same workflow as consumers
- Must re-install after editing source (validates installation)
- File watcher only watches installed files (correct behavior)
- Catch all path/copy bugs before shipping

---

## 🔧 Development Workflows

### Workflow 1: Edit Framework Source

**When:** Changing universal standards, usage docs, workflows

```bash
# 1. Edit framework source
vim universal/standards/ai-safety/production-code-checklist.md

# 2. Copy to .praxis-os/ (like consumers do)
cp -r universal/standards .praxis-os/standards/universal

# 3. File watcher auto-rebuilds RAG index
# (triggered by file change in .praxis-os/)

# 4. Restart MCP server (if needed)
# Cursor → Settings → MCP → Restart agent-os-rag

# 5. Test changes in Cursor
# Query MCP to verify updated content

# 6. Commit changes
git add universal/standards/ .praxis-os/standards/universal/
git commit -m "docs: update production code checklist"
```

**Pain Points This Reveals:**
- "Ugh, copying is annoying" → Create better update command
- "Ugh, forgot to copy" → Add validation/reminders
- "Ugh, wrong directory structure" → Fix installation script

**Every pain point = consumers feel it = MUST FIX**

---

### Workflow 2: Edit Project-Specific Standards

**When:** Adding Python-specific guidance for this project only

```bash
# 1. Edit project-specific file directly
vim .praxis-os/standards/development/python-concurrency.md

# 2. File watcher auto-rebuilds index
# (no copy needed - not framework source)

# 3. Test in Cursor
```

These files are NOT distributed - safe to edit in place.

---

### Workflow 3: Edit MCP Server Code

**When:** Changing MCP server functionality

```bash
# 1. Edit source
vim mcp_server/praxis_os_rag.py

# 2. Copy to .praxis-os/
cp -r mcp_server .praxis-os/

# 3. Restart MCP server (REQUIRED for code changes)
# Cursor → Settings → MCP → Restart agent-os-rag

# 4. Test changes
```

**Note:** Content changes (markdown) auto-rebuild via file watcher.  
Server code changes require manual restart.

---

## 🧩 Component Architecture

### 1. MCP Server (`mcp_server/praxis_os_rag.py`)

**Responsibilities:**
- Expose MCP tools to AI agents
- Orchestrate RAG search, workflow engine, state management
- Watch installed files for changes (`.praxis-os/`)

**MCP Tools:**
- `pos_search` - Semantic search over prAxIs OS documentation
- `start_workflow` - Begin phase-gated workflow with overview
- `get_current_phase` - Get current phase content and task metadata
- `get_task` - Get full content for one task (horizontal scaling)
- `complete_phase` - Submit evidence and advance phase
- `get_workflow_state` - Get complete workflow state
- `create_workflow` - Generate new workflow framework
- `current_date` - Get current date/time (prevent AI date errors)

---

### 2. RAG Engine (`mcp_server/rag_engine.py`)

**Responsibilities:**
- Vector search over prAxIs OS documentation
- Local embeddings (sentence-transformers, no API costs)
- LanceDB for vector storage

**Features:**
- Semantic search with filters (phase, tags)
- Chunk-level retrieval with source attribution
- Configurable source paths via `config.json`

---

### 3. Workflow Engine (`mcp_server/workflow_engine.py`)

**Responsibilities:**
- Phase-gated workflow execution
- Checkpoint validation (evidence requirements)
- Workflow metadata loading
- Task content retrieval

**Key Methods:**
- `start_workflow()` - Initialize workflow, return Phase 0/1 content + overview
- `get_current_phase()` - Return task metadata list + general guidance
- `get_task()` - Return full content for one task at a time
- `complete_phase()` - Validate evidence, advance phase

---

### 4. State Manager (`mcp_server/state_manager.py`)

**Responsibilities:**
- Workflow state persistence
- Session management
- Dynamic starting phase detection (Phase 0 vs Phase 1)

**Key Methods:**
- `create_session()` - Detect starting phase, create state
- `_detect_starting_phase()` - Check if Phase 0 exists in workflow

---

### 5. File Watcher

**Responsibilities:**
- Monitor `.praxis-os/standards/`, `.praxis-os/usage/`, `.praxis-os/workflows/`
- Auto-rebuild RAG index on file changes
- Trigger incremental updates

**Behavior:**
- Watches: `.praxis-os/` (installed files)
- Does NOT watch: `universal/` (framework source)
- Triggers on: `.md` and `.json` file changes
- Action: Rebuild RAG index with updated content

---

## 🚨 Critical Distinctions

### Framework Source vs. Installed Files

| Location | Purpose | Who Edits | Distribution | Tracked in Git |
|----------|---------|-----------|--------------|----------------|
| `universal/` | Framework source | Framework devs | YES (copied) | YES (source) |
| `.praxis-os/standards/universal/` | Installed framework | NO ONE | NO (local) | YES (example) |
| `.praxis-os/standards/development/` | Project-specific | Project devs | NO (local) | YES (tracked) |
| `.praxis-os/.cache/` | RAG index | System | NO | NO (ephemeral) |
| `.praxis-os/venv/` | Python venv | System | NO | NO (ephemeral) |

**Rules:**
1. **NEVER edit `.praxis-os/standards/universal/`** (managed by copy)
2. **ALWAYS edit `universal/`** (source of truth)
3. **ALWAYS copy** after editing framework source
4. **Project-specific files** can be edited directly

---

## 🔍 File Watcher Behavior

### Correct Behavior (No Symlinks)

```python
# File watcher watches .praxis-os/standards/
observer.schedule(watcher, ".praxis-os/standards", recursive=True)

# With real copied files:
# Edit universal/standards/foo.md
# → NOT visible in .praxis-os/ (different file)
# → File watcher does NOT trigger
# → Must copy to update .praxis-os/
# → This is CORRECT (same as consumers)

# Edit .praxis-os/standards/development/bar.md
# → File change in watched directory
# → File watcher triggers rebuild
# → This is CORRECT (local edits)
```

**Key Insight:** File watcher ONLY watches installed files, not source.

---

## 📦 Configuration (`config.json`)

Consuming projects can customize paths:

```json
{
  "rag_sources": {
    "standards_path": ".praxis-os/standards",
    "usage_path": ".praxis-os/usage",
    "workflows_path": ".praxis-os/workflows"
  }
}
```

**Defaults** (if `config.json` missing):
- `standards_path`: `.praxis-os/standards`
- `usage_path`: `universal/usage`
- `workflows_path`: `universal/workflows`

---

## 🎯 Quality Principles

### Why We Had Bugs

1. **Not following our own standards** - `production-code-checklist.md` existed but wasn't consulted
2. **Stale RAG index** - File watcher used wrong paths
3. **Insufficient testing** - No integration tests for real workflows
4. **Symlink shortcuts** - Fake dogfooding hid real problems

### How We're Fixing It

1. **TRUE dogfooding** - No symlinks, feel all consumer pain
2. **Query MCP before coding** - Enforce via `.cursorrules`
3. **Fix file watcher** - Use correct configured paths
4. **Comprehensive tests** - Integration tests for all critical paths
5. **"Belt and suspenders"** - Multiple validation layers

---

## 📊 Success Metrics

**We're truly dogfooding when:**
- ✅ No symlinks (except venv internals)
- ✅ All content is real copies
- ✅ We follow same update workflow as consumers
- ✅ We feel friction and fix it
- ✅ `.praxis-os/` serves as reference example for consumers

**We're shipping quality when:**
- ✅ MCP queries work before we code
- ✅ RAG index is never stale
- ✅ All integration tests pass
- ✅ `get_task` returns correct phase content
- ✅ File watcher uses correct paths

---

## 📚 Related Documentation

- `DOGFOODING_ARCHITECTURE.md` - Detailed dogfooding design
- `CONTRIBUTING.md` - How to contribute (edit→copy→test workflow)
- `README.md` - Project overview and quick start
- `.cursorrules` - AI behavior rules (MCP-first, standards-first)
- `universal/usage/operating-model.md` - Human vs AI roles
- `universal/usage/mcp-usage-guide.md` - How to use MCP tools