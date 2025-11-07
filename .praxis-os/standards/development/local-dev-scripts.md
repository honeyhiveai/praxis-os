# Local Development Scripts Organization

**Purpose:** Separate consumer-facing scripts from framework developer scripts.

**Audience:** prAxIs OS framework developers only (local standard, not shipped).

**Status:** Active

---

## 🎯 TL;DR - Script Organization

**Keep source clean. Ship only what consumers need.**

```
Repository (source):
  scripts/              → Consumer-facing, shipped to consumers
    ├── build_rag_index.py
    ├── configure-claude-code-mcp.py
    ├── update-cline-mcp.py
    └── safe-upgrade.py

  .praxis-os/bin/       → Dev-only, committed but NOT shipped
    ├── analyze_session_chunks.py
    ├── chunk_large_file.py
    ├── validate_workflow_metadata.py
    ├── generate-manifest.py
    └── ... (other dev tools)
```

---

## ❌ The Problem

**Without this separation:**
- Consumer installation polluted with dev tools they never use
- Confusing: "Why do I have `validate_workflow_metadata.py`?"
- Bloat: Installing validation scripts, pre-commit hooks, analysis tools
- Maintenance: More scripts to version/document/support for consumers
- Source pollution: Dev scripts mixed with consumer scripts

**Root cause:** All scripts lived in `scripts/`, which `install-praxis-os.py` copies in full.

---

## ✅ The Solution

**Two distinct locations with clear purposes:**

### 1. Source `scripts/` Directory (Consumer-Facing)

**Location:** `/scripts/` in repository root

**Installed to:** `.praxis-os/scripts/` in consumer projects

**Purpose:** Tools that consumers of prAxIs OS need

**What goes here:**
- ✅ `build_rag_index.py` - RAG troubleshooting/rebuilds
- ✅ `configure-claude-code-mcp.py` - Secondary agent setup
- ✅ `update-cline-mcp.py` - Secondary agent setup
- ✅ `safe-upgrade.py` - Framework upgrade tool

**Criteria:**
- Would a consumer ever need to run this?
- Is this part of normal prAxIs OS usage?
- Does documentation reference this script?

### 2. `.praxis-os/bin/` Directory (Dev-Only)

**Location:** `.praxis-os/bin/` in repository (committed)

**Installed to:** Nowhere (not copied during consumer installation)

**Purpose:** Tools that prAxIs OS framework developers need

**What goes here:**
- ✅ `analyze_session_chunks.py` - Session analysis
- ✅ `chunk_large_file.py` - Dev utility
- ✅ `generate-gate-definitions.py` - Workflow authoring
- ✅ `generate-manifest.py` - Release automation
- ✅ `migrate_checkpoints_to_gates.py` - One-time migration
- ✅ `validate_workflow_metadata.py` - Pre-commit validation
- ✅ `validate-divio-compliance.py` - Doc validation
- ✅ `validate-links.py` - Doc validation
- ✅ Any pre-commit hooks or CI/CD helpers

**Criteria:**
- Is this for building/testing/validating prAxIs OS itself?
- Would a consumer ever need this?
- Is this meta-development tooling?

---

## 🔄 Development Workflow

### Creating a New Script

**Ask:** Will consumers need this?

**Yes (Consumer-facing):**
```bash
# Create in source
touch scripts/new-consumer-tool.py
chmod +x scripts/new-consumer-tool.py

# Test via reinstall (dogfooding)
python scripts/install-praxis-os.py

# Verify installed
ls -la .praxis-os/scripts/new-consumer-tool.py
```

**No (Dev-only):**
```bash
# Create in .praxis-os/bin/ (committed to source)
touch .praxis-os/bin/new-dev-tool.py
chmod +x .praxis-os/bin/new-dev-tool.py

# Commit so all framework devs have it
git add .praxis-os/bin/new-dev-tool.py
git commit -m "Add new-dev-tool for framework development"

# Run from bin
python .praxis-os/bin/new-dev-tool.py
```

### Using Dev Scripts

```bash
# Always reference .praxis-os/bin/ explicitly
python .praxis-os/bin/validate_workflow_metadata.py

# Or add to PATH for convenience (shell session only)
export PATH="$PWD/.praxis-os/bin:$PATH"
validate_workflow_metadata.py
```

### Moving Existing Scripts

**If script should be dev-only:**
```bash
# 1. Move to bin (or copy if needed elsewhere)
git mv scripts/some-dev-tool.py .praxis-os/bin/

# 2. Test it works
python .praxis-os/bin/some-dev-tool.py

# 3. Commit the change
git commit -m "Move some-dev-tool.py to dev-only (.praxis-os/bin/)"
```

**Always commit `.praxis-os/bin/`** - all framework devs need these tools.

---

## 📋 Current Script Inventory

### Consumer Scripts (`scripts/`)

| Script | Purpose | When Consumers Use |
|--------|---------|-------------------|
| `build_rag_index.py` | RAG index rebuild | Troubleshooting, force rebuild |
| `configure-claude-code-mcp.py` | Claude Code secondary agent | Multi-agent setup |
| `update-cline-mcp.py` | Cline secondary agent | Multi-agent setup |
| `safe-upgrade.py` | Framework upgrade | Upgrading prAxIs OS |

### Dev Scripts (`.praxis-os/bin/`)

| Script | Purpose | When Developers Use |
|--------|---------|---------------------|
| `analyze_session_chunks.py` | Session analysis | Debugging, learning |
| `chunk_large_file.py` | File chunking | Large file analysis |
| `generate-gate-definitions.py` | Workflow gates | Workflow authoring |
| `generate-manifest.py` | Universal manifest | Release process |
| `migrate_checkpoints_to_gates.py` | Legacy migration | One-time upgrade |
| `validate_workflow_metadata.py` | Workflow validation | Pre-commit, CI/CD |
| `validate-divio-compliance.py` | Doc validation | Pre-commit, CI/CD |
| `validate-links.py` | Link checking | Pre-commit, CI/CD |

---

## 🎯 Benefits

**For Consumers:**
- ✅ Clean installation (only 4 scripts instead of 12+)
- ✅ Clear purpose (every script is user-facing)
- ✅ Less confusion ("Why is this here?")
- ✅ Smaller footprint

**For Developers:**
- ✅ Clear separation (consumer vs dev)
- ✅ Freedom to create dev tools without polluting source
- ✅ Easy to find dev tools (`.praxis-os/bin/`)
- ✅ No need to document internal tools for consumers

**For the Framework:**
- ✅ Cleaner source repository
- ✅ Easier to audit what ships
- ✅ Aligned with meta-development patterns
- ✅ Better abstraction boundaries

---

## ⚠️ Anti-Patterns

**❌ Don't:** Put dev tools in source `scripts/`
```bash
# NO - pollutes consumer installs
scripts/validate_workflow_metadata.py
```

**✅ Do:** Put dev tools in local `.praxis-os/bin/`
```bash
# YES - dev-only, never shipped
.praxis-os/bin/validate_workflow_metadata.py
```

**❌ Don't:** Reference `.praxis-os/bin/` in consumer docs
```markdown
# NO - consumers don't have this
Run: python .praxis-os/bin/validate_workflow_metadata.py
```

**✅ Do:** Reference `.praxis-os/scripts/` in consumer docs
```markdown
# YES - consumers have this
Run: python .praxis-os/scripts/build_rag_index.py --force
```

**❌ Don't:** Put dev scripts in `.gitignore`
```bash
# NO - framework devs need these
# .gitignore: .praxis-os/bin/  # WRONG
```

**✅ Do:** Commit `.praxis-os/bin/` for all framework devs
```bash
# YES - shared dev tooling
git add .praxis-os/bin/
git commit -m "Add dev tooling"
```

---

## 🔍 Questions This Answers

**"Where should I put a new script?"**
→ Ask: Will consumers need it? Yes = `scripts/`, No = `.praxis-os/bin/`

**"Why can't I find `validate_workflow_metadata.py` in source `scripts/`?"**
→ It's dev-only, in `.praxis-os/bin/` (committed but not shipped to consumers)

**"How do consumers run secondary agent setup?"**
→ Scripts in `.praxis-os/scripts/` (installed from source `scripts/`)

**"Can I create dev tools without polluting consumer installs?"**
→ Yes! Put them in `.praxis-os/bin/` (committed but not shipped to consumers)

**"What's the difference between `scripts/` and `.praxis-os/bin/`?"**
→ `scripts/` = consumer-facing (shipped), `.praxis-os/bin/` = dev-only (not shipped)

---

## Related Standards

- `standards/development/meta-development-patterns.md` - Framework dev vs consumer experience
- `standards/development/dogfooding-model.md` - True dogfooding via installation
- `standards/development/multi-agent-architecture.md` - Secondary agent helper scripts

---

**Remember:** If consumers don't need it, it belongs in `.praxis-os/bin/`. Keep `scripts/` for consumer tools, keep `.praxis-os/bin/` for dev tools. Both are committed, only `scripts/` is shipped.

