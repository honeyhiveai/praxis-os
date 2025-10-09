# Agent OS .gitignore Requirements

**Purpose**: Canonical list of required .gitignore entries for Agent OS installations

---

## Required Entries

All Agent OS installations MUST include these entries in the project's `.gitignore`:

```gitignore
# Agent OS - Ephemeral content (do not commit)
.agent-os/.cache/
.agent-os/venv/
.agent-os/mcp_server/__pycache__/
.agent-os/scripts/__pycache__/
.agent-os.backup.*
.agent-os/.upgrade_lock
```

---

## Why Each Entry is Required

| Pattern | Size | Reason | Impact if Committed |
|---------|------|--------|---------------------|
| `.agent-os/.cache/` | ~1.3GB | Vector index, regenerated on each machine | Massive repo bloat, conflicts across machines |
| `.agent-os/venv/` | ~100MB | Python virtual environment | Platform-specific, breaks across OS/Python versions |
| `.agent-os/mcp_server/__pycache__/` | ~5MB | Python bytecode | Platform/Python version specific |
| `.agent-os/scripts/__pycache__/` | ~1MB | Python bytecode | Platform/Python version specific |
| `.agent-os.backup.*` | ~1.3GB | Upgrade backups (temporary) | Massive repo bloat, only needed locally for rollback |
| `.agent-os/.upgrade_lock` | <1KB | Upgrade lock file (temporary) | Meaningless outside upgrade process |

**Total potential bloat**: ~2.7GB of ephemeral files

---

## What SHOULD Be Committed

Agent OS content that should be tracked in version control:

| Directory | Purpose | Commit? |
|-----------|---------|---------|
| `.agent-os/standards/` | Universal CS fundamentals + project standards | ✅ YES |
| `.agent-os/usage/` | Documentation + custom docs | ✅ YES |
| `.agent-os/workflows/` | Workflow definitions | ✅ YES |
| `.agent-os/specs/` | Project specifications | ✅ YES (critical!) |
| `.agent-os/mcp_server/` | MCP server code | ✅ YES (if customized) |
| `.cursor/mcp.json` | Cursor MCP configuration | ✅ YES |
| `.cursorrules` | AI assistant behavioral triggers | ✅ YES |

---

## Format for .gitignore

The entries should be added as a single section:

```gitignore
# Agent OS - Ephemeral content (do not commit)
.agent-os/.cache/
.agent-os/venv/
.agent-os/mcp_server/__pycache__/
.agent-os/scripts/__pycache__/
.agent-os.backup.*
.agent-os/.upgrade_lock
```

**Rules**:
- Section header: `# Agent OS - Ephemeral content (do not commit)`
- One pattern per line
- Blank line before and after section (for readability)
- Append to existing `.gitignore` if present
- Create new `.gitignore` if missing

---

## Verification

To verify entries are working:

```bash
# Check if patterns are ignored
git check-ignore .agent-os/.cache/test         # Should exit 0
git check-ignore .agent-os.backup.20251008     # Should exit 0
git check-ignore .agent-os/.upgrade_lock       # Should exit 0

# Check if any ephemeral files are already committed
git ls-files .agent-os/.cache/ .agent-os/venv/ .agent-os.backup.*
# Should return nothing
```

---

## Historical Context

**Added**: October 8, 2025  
**Rationale**: Users were committing 1.3GB+ vector indexes and upgrade backups, causing:
- GitHub rejecting pushes (file size limits)
- Repo clones taking 10+ minutes
- Merge conflicts on binary cache files
- Wasted CI/CD bandwidth

**Previous Issue**: `.agent-os.backup.*` was not in original .gitignore, discovered during upgrade workflow testing when 665 backup files (117K insertions) were staged for commit.

---

## For Workflow Authors

### Installation Workflows

When writing installation guides, reference this file:

```python
# Read canonical requirements
with open(f"{AGENT_OS_SOURCE}/universal/standards/installation/gitignore-requirements.md") as f:
    content = f.read()
    # Extract code block with required entries
```

### Upgrade Workflows

When updating existing installations:

```python
# Read from standards, not hardcoded list
standards_path = ".agent-os/standards/universal/installation/gitignore-requirements.md"
with open(standards_path) as f:
    content = f.read()
    # Extract and compare with target .gitignore
```

---

## Maintenance

To add a new required entry:

1. Add pattern to this file's "Required Entries" section
2. Update the table explaining why it's required
3. Installation and upgrade workflows will automatically pick it up

**Do NOT**:
- Hardcode lists in workflow task files
- Duplicate this list elsewhere
- Add entries without documenting the reason

---

**Last Updated**: October 8, 2025  
**Canonical Source**: `universal/standards/installation/gitignore-requirements.md`

