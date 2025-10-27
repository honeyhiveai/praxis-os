---
sidebar_position: 6
doc_type: how-to
---

# Upgrading prAxIs OS

Keep your prAxIs OS installation up-to-date with new features, standards, and improvements.

## Quick Upgrade

The simplest way to upgrade:

```bash
# In Cursor, say:
"Run the prAxIs OS upgrade workflow"
```

The AI will use the `praxis_os_upgrade_v1` workflow to safely upgrade your installation with automatic backup and validation.

**Total Time:** ~3-4 minutes

---

## Upgrade Workflow (Recommended)

The `praxis_os_upgrade_v1` workflow provides a safe, automated upgrade process:

### Start the Workflow

```python
# Via MCP tools
start_workflow(
    workflow_type="praxis_os_upgrade_v1",
    target_file="mcp_server",
    options={
        "source_path": "/path/to/praxis-os",  # Or GitHub URL
        "dry_run": false,
        "auto_restart": true
    }
)
```

### What Gets Upgraded

The workflow updates:

1. **Universal Standards** (`.praxis-os/standards/universal/`)
   - Concurrency patterns
   - Architecture patterns
   - Testing strategies
   - Failure modes
   - Security patterns

2. **Usage Documentation** (`.praxis-os/usage/`)
   - MCP tool guides
   - Operating model
   - Update procedures

3. **Workflows** (`.praxis-os/workflows/`)
   - `spec_creation_v1`
   - `spec_execution_v1`
   - `praxis_os_upgrade_v1`
   - Any new workflows

4. **MCP Server** (`.praxis-os/mcp_server/`)
   - Server code
   - Dependencies
   - Bug fixes
   - New features

5. **Configuration**
   - `.gitignore` entries (auto-updates from standards)
   - Version tracking

### What's Preserved

Your customizations are **never** overwritten:

- ✅ **User Specs** (`.praxis-os/specs/`) - Completely untouched
- ✅ **Development Standards** (`.praxis-os/standards/development/`) - Your language-specific standards
- ✅ **Custom Documentation** (`.praxis-os/usage/`) - New docs added, yours preserved
- ✅ **Project Configuration** - `.cursorrules`, `mcp.json`

---

## Upgrade Process

### Phase 0: Pre-Flight Checks (30s)

Validates everything before starting:

- Source repository exists and is valid
- Target installation is healthy
- Sufficient disk space (~500MB)
- No concurrent upgrades running
- Git status is clean (if in git repo)

### Phase 1: Backup & Preparation (20s)

Creates safety net:

- Timestamped backup: `.praxis-os.backup.YYYYMMDD_HHMMSS/`
- Checksum manifest for validation
- Upgrade lock to prevent concurrent upgrades

### Phase 2: Content Upgrade (60s)

Updates standards, usage, workflows:

- Dry-run first (preview changes)
- Actual upgrade with `rsync`
- Updates `.gitignore` from standards
- Verifies checksums

**Safety**: User-writable directories use `rsync -av` (NO `--delete` flag) to preserve your files.

### Phase 3: MCP Server Upgrade (60s)

Updates server code and dependencies:

- Copies new MCP server code
- Updates Python dependencies
- Runs post-install steps (Playwright, etc.)
- **Restarts MCP server** (Cursor must be restarted)

:::tip Server Restart
After Phase 3, you must restart Cursor to reload the MCP server. The workflow automatically saves its state and resumes after restart.
:::

### Phase 4: Post-Upgrade Validation (30s)

Verifies everything works:

- MCP tools registered correctly
- RAG search operational
- Browser tools functional
- Workflow execution working

### Phase 5: Cleanup (15s)

Finishes up:

- Releases upgrade lock
- Archives old backups (if any)
- Generates upgrade report
- Updates version tracking

---

## Rollback

If anything goes wrong, automatic rollback restores from backup:

### Automatic Rollback

If any phase fails (2, 3, or 4), the workflow automatically:

1. Stops immediately
2. Restores from `.praxis-os.backup.*/`
3. Releases upgrade lock
4. Reports what failed

**Target rollback time:** < 30 seconds

### Manual Rollback

If you need to manually rollback:

```bash
# Stop MCP server (restart Cursor)

# Restore from backup
rm -rf .praxis-os
mv .praxis-os.backup.YYYYMMDD_HHMMSS .praxis-os

# Restart Cursor to reload MCP server
```

---

## Version Tracking

prAxIs OS tracks what's installed:

```bash
# Check current version
cat .praxis-os/VERSION.txt

# Shows:
# version_installed=2025-10-08T12:00:00Z
# version_updated=2025-10-08T14:30:00Z
# commit=a1b2c3d
# source=/path/to/praxis-os
```

---

## Upgrade Frequency

### When to Upgrade

Upgrade when:

- 🆕 **New features** are released (check GitHub releases)
- 🐛 **Bug fixes** for issues you're experiencing
- 📚 **New standards** for technologies you use
- 🔄 **New workflows** that match your needs

### When NOT to Upgrade

Skip upgrading when:

- ⏰ In the middle of critical work
- 🔬 Running important tests/experiments
- 📝 Working on complex specs (finish first)

---

## Manual Upgrade (Advanced)

If you need manual control:

### 1. Backup Current Installation

```bash
cp -r .praxis-os .praxis-os.backup.$(date +%Y%m%d_%H%M%S)
```

### 2. Pull Latest Source

```bash
# If you have local clone
cd /path/to/praxis-os
git pull origin main

# Or fresh clone
git clone https://github.com/honeyhiveai/praxis-os.git /tmp/praxis-os-latest
```

### 3. Update Content

```bash
# Update standards (prAxIs OS owned)
rsync -av --delete praxis-os/universal/standards/ .praxis-os/standards/universal/

# Update usage (preserve user docs)
rsync -av praxis-os/universal/usage/ .praxis-os/usage/

# Update workflows
rsync -av --delete praxis-os/universal/workflows/ .praxis-os/workflows/
```

### 4. Update MCP Server

```bash
# Copy server code
rsync -av --delete praxis-os/mcp_server/ .praxis-os/mcp_server/

# Update dependencies
cd .praxis-os
./venv/bin/pip install -r mcp_server/requirements.txt

# Restart Cursor
```

### 5. Update .gitignore

```bash
# Check for new required entries
# See: .praxis-os/standards/universal/installation/gitignore-requirements.md
```

---

## Troubleshooting

### "Upgrade failed in Phase 2"

**Cause:** File conflicts or permission issues

**Fix:**
1. Check error message in upgrade report
2. Manually resolve conflicts
3. Re-run workflow

### "MCP server won't start after upgrade"

**Cause:** Dependency mismatch or Python version

**Fix:**
```bash
# Rebuild virtualenv
rm -rf .praxis-os/venv
cd .praxis-os
python -m venv venv
./venv/bin/pip install -r mcp_server/requirements.txt

# Restart Cursor
```

### "Workflow says concurrent upgrade running"

**Cause:** Previous upgrade didn't complete

**Fix:**
```bash
# Remove stale lock
rm -f .praxis-os/.upgrade_lock

# Re-run workflow
```

### "Backup directory is huge"

**Cause:** Backups include vector index cache

**Fix:**
```bash
# Check backup size
du -sh .praxis-os.backup.*

# Safe to delete after 7 days of stable operation
rm -rf .praxis-os.backup.20251001_*
```

**Note:** Backups are NOT committed to git (in `.gitignore`)

---

## What's New in Each Version

### v1.5.0 (October 8, 2025)

**Added:**
- `.gitignore` management (prevents 2.7GB of ephemeral files)
- `validate_workflow` MCP tool
- `current_date` MCP tool for preventing date errors
- Installation step 04: gitignore configuration
- Single source of truth for gitignore requirements

**Fixed:**
- CRITICAL: Removed dangerous `--delete` from user-writable directories
- Phase 2 now safely preserves user documentation

**Changed:**
- Installation steps: 5 → 6 (added gitignore)
- Upgrade Phase 2: 3 → 4 tasks
- Total upgrade time: 3min 20s → 3min 35s

### v1.4.0 (October 7, 2025)

**Added:**
- Modular MCP server architecture
- Selective tool loading (performance optimization)
- Tool count monitoring (warns at >20 tools)

**Changed:**
- Configuration management with validation
- Dependency injection throughout
- Entry point simplified

### Earlier Versions

See [CHANGELOG.md](https://github.com/honeyhiveai/praxis-os/blob/main/mcp_server/CHANGELOG.md) for complete history.

---

## Best Practices

### Before Upgrading

1. ✅ **Commit your work** - Clean git status
2. ✅ **Finish active specs** - Complete what you're working on
3. ✅ **Note your version** - Check `VERSION.txt` before upgrade
4. ✅ **Read release notes** - Know what's changing

### After Upgrading

1. ✅ **Restart Cursor** - Reload MCP server
2. ✅ **Test MCP tools** - Quick `search_standards` query
3. ✅ **Verify workflows** - Check workflow list
4. ✅ **Review changes** - See upgrade report
5. ✅ **Delete backup after 7 days** - If no issues

### Regular Maintenance

- 📅 Check for updates monthly
- 🧹 Clean old backups quarterly
- 📊 Review upgrade reports
- 🔍 Monitor MCP server logs

---

## Related Documentation

- **[Installation](../tutorials/installation)** - Initial setup
- **[MCP Tools](../reference/mcp-tools)** - Available tools after upgrade
- **[Workflows](../reference/workflows)** - Workflow system overview


