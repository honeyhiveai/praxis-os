# Agent OS Installation Guide

**How to install prAxIs OS into a target project**

---

## 🎯 Quick Start

When a user says: **"Install Agent OS from github.com/honeyhiveai/agent-os-enhanced"**

**Start here** → Read `00-START.md` and follow the chain.

---

## 📖 Installation Files (Horizontally Scaled)

These files use **horizontal scaling** - each file is ~200-250 lines and chains to the next. This works around vanilla LLM attention span constraints.

### Sequential Installation Chain

```
00-START.md           ← START HERE (clone to temp, setup)
    ↓
01-directories.md     Create all 8 required directories
    ↓
02-copy-files.md      Copy ~106 files from source
    ↓
03-cursorrules.md     Handle .cursorrules safely (don't overwrite!)
    ↓
04-gitignore.md       Configure .gitignore (prevent committing 2.6GB!)
    ↓
05-venv-mcp.md        Create Python venv + mcp.json + BUILD RAG INDEX
    ↓
06-validate.md        Validate + CLEANUP temp directory
    ↓
COMPLETE! ✅
```

**Each file**:
- ~200-250 lines (manageable for vanilla LLMs)
- Explicit validation checkpoints
- Clear "Next Step" at the end
- Can be re-read if confused

---

## 🎯 Design Principle: Bootstrapping Problem

**The Problem**: Agent OS helps LLMs follow complex instructions, but we need an LLM to install Agent OS (before it has our enhancements).

**The Solution**: These guides work for **vanilla LLMs**:
- ✅ Short files (~250 lines each)
- ✅ One task per file
- ✅ Validation after each step
- ✅ Critical mistakes listed upfront
- ✅ Visual separators (emojis, headers, code blocks)
- ✅ Chain navigation (explicit "Next Step")

---

## ⚠️ Critical Success Factors

### 1. Don't Litter Git Repos!

The source repo (`agent-os-enhanced`) is **cloned to a temp directory** and **deleted at the end**. We do NOT leave a git repo inside the consumer's project.

### 2. Don't Overwrite .cursorrules!

Many projects have existing `.cursorrules` files. Step 03 checks for this and offers merge options instead of blindly overwriting.

### 3. Create ALL Directories

The most common mistake: forgetting `.agent-os/workflows/` directory. The MCP server's `ConfigValidator` requires it.

### 4. Use Correct Module Name

In `mcp.json`, use `"mcp_server"` NOT `"mcp_server.agent_os_rag"`. The entry point is `mcp_server/__main__.py`.

---

## 📚 Reference Documents

### For LLMs During Installation

- **00-START.md** → Entry point, critical mistakes, setup
- **01-directories.md** → Directory creation with validation
- **02-copy-files.md** → File copying with validation  
- **03-cursorrules.md** → Safe .cursorrules handling
- **04-gitignore.md** → Configure .gitignore to prevent commits of ephemeral files
- **05-venv-mcp.md** → Python venv + mcp.json creation + **RAG index build**
- **06-validate.md** → Final validation + cleanup

### For Deep Dives (if needed)

- **installation-guide.md** (800+ lines) - Comprehensive detailed guide
- **CURSORRULES_MERGE_GUIDE.md** - Complete merge protocol
- **INSTALLATION_CHECKLIST.md** - Validation checklist
- **INSTALLATION_GUIDE_UPDATE_SUMMARY.md** - Change history

---

## 🏗️ Architecture Context

**Source Repository** (this repo):
```
agent-os-enhanced/
├── installation/          ← Installation guides
│   ├── 00-START.md       ← Entry point
│   ├── 01-directories.md
│   ├── 02-copy-files.md
│   ├── 03-cursorrules.md
│   ├── 04-gitignore.md
│   ├── 05-venv-mcp.md
│   └── 06-validate.md
├── universal/             ← Content to copy
│   ├── standards/
│   ├── usage/
│   └── workflows/
├── mcp_server/            ← Server code to copy
└── .cursorrules           ← Rules to copy/merge
```

**During Installation** (temp directory):
```
/tmp/agent-os-install-xyz/
└── [same structure as above]
    ← Cloned here temporarily
    ← Deleted at end of step 05
```

**Target Project** (consumer):
```
target-project/
├── .agent-os/             ← Created during installation
│   ├── standards/
│   ├── usage/
│   ├── workflows/
│   ├── mcp_server/
│   ├── venv/
│   └── .cache/
├── .cursorrules           ← Copied or merged
└── .cursor/
    └── mcp.json           ← Created fresh
```

---

## ✅ Validation

After installation, these should all be true:

```python
checks = {
    ".agent-os/workflows/": exists and has ~47 files,
    ".agent-os/venv/": exists with working Python,
    ".agent-os/.cache/vector_index/": exists with RAG index,
    ".cursorrules": exists with Agent OS rules,
    ".cursor/mcp.json": exists with "mcp_server" module,
    "Temp directory": deleted (cleaned up),
}
```

---

## 🚨 Common Failure Modes

| Issue | Cause | Fix |
|-------|-------|-----|
| Missing workflows/ | Forgot step 01 | Create `.agent-os/workflows/` |
| Wrong module name | Used `mcp_server.agent_os_rag` | Change to `mcp_server` in mcp.json |
| Empty workflows/ | Forgot step 02 | Copy files from `universal/workflows/` |
| Git repo left behind | Forgot step 05 | Delete temp directory manually |
| .cursorrules overwritten | Didn't follow step 03 | Restore from `.cursorrules.backup` |

---

## 📖 For Maintainers

### When Updating Installation Process

1. Update the sequential files (00-06)
2. Keep each file ~200-250 lines
3. Maintain chain navigation
4. Update this README
5. Test on fresh project

### Critical Safety Rules

1. ⚠️ Never leave temp directory behind
2. ⚠️ Never blindly overwrite .cursorrules
3. ⚠️ Always validate at each step
4. ⚠️ Always backup user files before modifying

---

## 🎯 Success Criteria

Installation is successful when:
- ✅ All 8 directories created
- ✅ ~106 files copied
- ✅ .cursorrules handled safely
- ✅ Python venv working
- ✅ **RAG index built** (enables semantic search)
- ✅ mcp.json configured correctly
- ✅ **Temp directory deleted**
- ✅ MCP server validation passes

**Installation time**: ~5-10 minutes  
**Success rate**: Expected 100% (with proper guides)

---

**Last Updated**: October 8, 2025  
**Version**: 2.0 (Horizontally-scaled, bootstrapping-friendly)
