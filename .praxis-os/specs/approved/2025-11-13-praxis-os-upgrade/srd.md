# Software Requirements Document: praxis-os Upgrade System

**Spec ID:** 2025-11-13-praxis-os-upgrade  
**Status:** 🚧 In Review  
**Version:** 1.0.0  
**Last Updated:** 2025-11-13  
**Author:** AI Agent (Claude)  
**Reviewer:** TBD

---

## 🎯 Executive Summary

This specification defines an upgrade system for praxis-os consumer installations. The system must preserve user content (specs, customizations) while updating framework code (standards, workflows, server) in 3-5 minutes with mandatory backup and automatic rollback on failure.

**Key Requirement:** Enable safe, fast, reliable upgrades for the growing base of praxis-os consumer installations.

---

## 📋 Business Goals

### Goal 1: Enable Reliable Framework Evolution
**Why It Matters:** praxis-os is under active development. Consumer installations need to stay current as standards, workflows, and server code evolve.

**Current Problem:** Upgrade path is broken:
- Documentation references deleted directories (`mcp_server/`, `usage/`)
- Installation deletes source repo after copying (no git relationship)
- Manual rsync commands assume local source (unavailable)
- Existing workflow has wrong paths

**Business Impact:**
- ❌ Consumer installations become stale (missed bug fixes, new features)
- ❌ Support burden increases (debugging old versions)
- ❌ User frustration (no clear upgrade path)
- ❌ Framework evolution slows (fear of breaking installs)

**Success Metric:** 100% of consumers can upgrade to latest version in < 5 minutes.

---

### Goal 2: Preserve User Investment
**Why It Matters:** Users invest time creating specs, customizing configs, and defining project-specific standards. Upgrades must never lose this work.

**Current Problem:** No clear ownership model. Users don't know:
- Which files will be overwritten?
- Which customizations will be lost?
- How to preserve their work?

**Business Impact:**
- ❌ Users fear upgrades (data loss risk)
- ❌ Upgrades deferred indefinitely (technical debt)
- ❌ User trust eroded (framework seems unreliable)

**Success Metric:** Zero user content lost across 100 upgrades.

---

### Goal 3: Reduce Support Burden
**Why It Matters:** Every broken upgrade is a support ticket. Manual interventions don't scale.

**Current Problem:**
- Users need to manually detect breaking changes
- No automatic recovery if upgrade fails
- Config merge requires manual diff/merge
- No validation that upgrade worked

**Business Impact:**
- ❌ Support time per user increases
- ❌ Engineering time diverted to support
- ❌ User productivity lost (debugging failed upgrades)

**Success Metric:** < 5% of upgrades require support intervention.

---

## 👥 User Stories

### Story 1: Framework Developer Ships Update
**As a** praxis-os framework developer  
**I want to** ship standards/workflow/server updates to all consumers  
**So that** everyone benefits from improvements and bug fixes

**Acceptance Criteria:**
- Updates ship via GitHub push
- Consumers pull updates via simple command
- Changes propagate in < 5 minutes
- No manual file copying required

---

### Story 2: Consumer Updates Safely
**As a** praxis-os consumer (developer using framework)  
**I want to** update to latest version without risking my work  
**So that** I get new features while keeping my specs/configs

**Acceptance Criteria:**
- One command to upgrade
- My specs/ directory never touched
- My config customizations preserved
- Automatic backup created
- Clear success/failure message

---

### Story 3: Recovery from Failed Upgrade
**As a** praxis-os consumer  
**I want to** automatic recovery if upgrade fails  
**So that** I'm not stuck with broken installation

**Acceptance Criteria:**
- Upgrade detects failure mid-process
- Automatically restores from backup
- Installation works as before
- Clear error message with remediation

---

### Story 4: Understanding What Changed
**As a** praxis-os consumer  
**I want to** see what changed in an upgrade  
**So that** I understand new features and breaking changes

**Acceptance Criteria:**
- Upgrade report shows files added/modified/deleted
- Config changes highlighted
- Breaking changes detected and explained
- Links to changelog/docs provided

---

## ⚙️ Functional Requirements

### FR-1: Pre-Flight Validation
**Priority:** P0 (Must Have)  
**Description:** Validate environment before attempting upgrade.

**Requirements:**
- FR-1.1: Verify `.praxis-os/` directory exists at target
- FR-1.2: Verify `.praxis-os/ouroboros/` exists (not broken install)
- FR-1.3: Check Python ≥ 3.9 available
- FR-1.4: Check git installed
- FR-1.5: Verify disk space ≥ 500MB available (for backup without indexes)
- FR-1.6: Detect breaking changes (e.g., old `mcp_server/` dir)
- FR-1.7: Exit with clear error message if any check fails

**Validation:** Script runs all checks, exits code 1 if any fail.

---

### FR-2: Mandatory Backup Creation
**Priority:** P0 (Must Have)  
**Description:** Always create timestamped backup before upgrade.

**Requirements:**
- FR-2.1: Create `.praxis-os.backup.YYYYMMDD_HHMMSS/` directory
- FR-2.2: Backup essential files:
  - `ouroboros/` (server code)
  - `standards/` (all standards)
  - `workflows/` (all workflows)
  - `config/` (configs)
  - `specs/` (user specs)
  - `scripts/` (helper scripts)
- FR-2.3: Exclude ephemeral data:
  - `.cache/` (RAG indexes - 2GB+)
  - `workspace/` (temp files)
  - `venv/` (Python env)
  - `**/__pycache__/`, `**/*.pyc` (bytecode)
- FR-2.4: Generate SHA256 checksum manifest
- FR-2.5: Validate backup integrity (checksums match)
- FR-2.6: Complete in < 10 seconds
- FR-2.7: Backup size < 100MB (excluding indexes)
- FR-2.8: Support `--skip-backup` flag (dangerous, warns user)

**Validation:** Backup created, checksums valid, size < 100MB, time < 10s.

---

### FR-3: Source Acquisition
**Priority:** P0 (Must Have)  
**Description:** Clone or use local praxis-os source.

**Requirements:**
- FR-3.1: Clone `github.com/honeyhiveai/praxis-os` to temp directory
- FR-3.2: Support `--source /path` flag for local source
- FR-3.3: Validate source has `dist/` directory structure
- FR-3.4: Extract version from source
- FR-3.5: Compare with installed version
- FR-3.6: Display version change (e.g., "0.9.0 → 1.0.0")
- FR-3.7: Complete in < 60 seconds (GitHub clone)

**Validation:** Source cloned/loaded, version extracted, comparison shown.

---

### FR-4: Framework File Upgrade
**Priority:** P0 (Must Have)  
**Description:** Overwrite framework-owned files with latest.

**Requirements:**
- FR-4.1: Rsync `dist/universal/standards/` → `.praxis-os/standards/universal/`
- FR-4.2: Rsync `dist/universal/workflows/` → `.praxis-os/workflows/`
- FR-4.3: Rsync `dist/ouroboros/` → `.praxis-os/ouroboros/`
- FR-4.4: Rsync `scripts/` → `.praxis-os/scripts/`
- FR-4.5: Use `--delete` flag (remove obsolete files)
- FR-4.6: Preserve `.praxis-os/specs/` (never touch)
- FR-4.7: Preserve `.praxis-os/standards/development/` (user-owned)
- FR-4.8: Generate file change report:
  - Count added files
  - Count modified files
  - Count deleted files
  - List all changes
- FR-4.9: Verify checksums after copy
- FR-4.10: Complete in < 90 seconds

**Validation:** All framework files updated, checksums match, user files untouched.

---

### FR-5: Config Update Preparation
**Priority:** P0 (Must Have)  
**Description:** Provide new config template for optional user update (non-blocking).

**Requirements:**
- FR-5.1: Copy `dist/config/mcp.yaml` → `.praxis-os/config/mcp.yaml.new` (reference)
- FR-5.2: Compare new vs current config (diff)
- FR-5.3: If no changes: Delete `.new` file, skip notification
- FR-5.4: If changes exist: Display update instructions (non-blocking)
- FR-5.5: Instructions include:
  - "Your current config will continue to work" (backward compatible)
  - "New features will use defaults" (version-aware loading)
  - "Review .new template to see new options" (optional)
  - "Update when ready" (no deadline)
  - "Delete .new after updating" (cleanup)
- FR-5.6: Display instructions to user (informational only)
- FR-5.7: Complete in < 15 seconds

**Design Note:** MCP server uses version-aware config loading (framework-level) to ensure old configs work with sensible defaults for new features. This prevents deadlock where LLM needs MCP tools to merge config but MCP server won't start without merged config.

**Validation:** Config template copied, instructions displayed, upgrade succeeds regardless of user action.

---

### FR-6: Gitignore Merge
**Priority:** P1 (Should Have)  
**Description:** Additive merge of .gitignore patterns.

**Requirements:**
- FR-6.1: Read new patterns from `standards/` docs
- FR-6.2: Read existing `.gitignore`
- FR-6.3: Add new patterns (don't remove existing)
- FR-6.4: Deduplicate patterns
- FR-6.5: Preserve user comments
- FR-6.6: Complete in < 5 seconds

**Validation:** New patterns added, existing patterns preserved.

---

### FR-7: Dependency Update
**Priority:** P0 (Must Have)  
**Description:** Update Python dependencies in venv.

**Requirements:**
- FR-7.1: Activate `.praxis-os/venv`
- FR-7.2: Run `pip install --upgrade -r ouroboros/requirements.txt`
- FR-7.3: Run post-install hooks (e.g., `playwright install` if needed)
- FR-7.4: Verify import works (`import ouroboros`)
- FR-7.5: Support `--skip-deps` flag (faster, for standards-only changes)
- FR-7.6: Complete in < 60 seconds

**Validation:** Dependencies updated, imports work.

---

### FR-8: Index Rebuild Trigger
**Priority:** P0 (Must Have)  
**Description:** Signal MCP server to rebuild RAG indexes.

**Requirements:**
- FR-8.1: Create `.praxis-os/.rebuild_indexes` flag file
- FR-8.2: MCP server detects flag on startup
- FR-8.3: Server rebuilds indexes in background
- FR-8.4: Server deletes flag after rebuild

**Validation:** Flag file created, server rebuilds on next start.

---

### FR-9: Upgrade Validation
**Priority:** P0 (Must Have)  
**Description:** Validate upgrade succeeded (file-based only).

**Requirements:**
- FR-9.1: Verify file counts match expected:
  - Standards: > 0 files
  - Workflows: > 0 files
  - Server code: > 0 files
- FR-9.2: Test Python import (`import ouroboros`)
- FR-9.3: Validate config YAML schema
- FR-9.4: Verify all checksums match
- FR-9.5: Generate validation report
- FR-9.6: Display user instructions for MCP testing:
  - Restart Cursor/IDE
  - Test MCP tools
  - Check server logs
  - Test config reconciliation
- FR-9.7: Complete in < 30 seconds

**Validation:** All file checks pass, user instructions displayed.

---

### FR-10: Cleanup & Reporting
**Priority:** P0 (Must Have)  
**Description:** Clean up temp files and generate upgrade report.

**Requirements:**
- FR-10.1: Delete temp source clone
- FR-10.2: Keep backup (user deletes after 7 days)
- FR-10.3: Optionally archive old backups (`--keep-backups N`)
- FR-10.4: Generate upgrade summary:
  - Version change
  - Files added/modified/deleted
  - Backup location
  - Next steps for user
  - Exit code 0 (success)
- FR-10.5: Complete in < 15 seconds

**Validation:** Temp files deleted, report generated, exit code 0.

---

### FR-11: Automatic Rollback on Failure
**Priority:** P0 (Must Have)  
**Description:** Automatically restore from backup if upgrade fails.

**Requirements:**
- FR-11.1: Catch any exception during upgrade phases
- FR-11.2: Display error message with context
- FR-11.3: Restore from backup directory:
  - Delete current `.praxis-os/`
  - Copy backup back to `.praxis-os/`
  - Verify restore checksums
- FR-11.4: Display rollback success message
- FR-11.5: Keep backup for debugging
- FR-11.6: Exit code 1 (failure)
- FR-11.7: Complete rollback in < 30 seconds

**Validation:** Backup restored, installation works, clear error message.

---

### FR-12: Dry-Run Preview
**Priority:** P1 (Should Have)  
**Description:** Show what would change without modifying files.

**Requirements:**
- FR-12.1: Accept `--dry-run` flag
- FR-12.2: Run all phases except file modifications
- FR-12.3: Display:
  - Files that would be added
  - Files that would be modified
  - Files that would be deleted
  - Disk space needed
  - Estimated time
- FR-12.4: Exit code 0 (nothing changed)

**Validation:** No files modified, complete report shown.

---

### FR-13: Breaking Change Detection
**Priority:** P0 (Must Have)  
**Description:** Detect and explain breaking changes.

**Requirements:**
- FR-13.1: Detect `mcp_server/` → `ouroboros/` rename
- FR-13.2: Detect other breaking changes (case-by-case)
- FR-13.3: Display clear error message:
  - What changed
  - Why it's breaking
  - Migration options (fresh install vs manual)
  - Link to documentation
- FR-13.4: Exit code 1 (cannot auto-migrate)

**Validation:** Breaking change detected, clear message shown, exit 1.

---

### FR-14: Concurrent Upgrade Prevention
**Priority:** P1 (Should Have)  
**Description:** Prevent multiple simultaneous upgrades.

**Requirements:**
- FR-14.1: Create `.praxis-os/.upgrade_lock` file with PID
- FR-14.2: Check lock exists before starting
- FR-14.3: If lock found: Check if PID is still running
- FR-14.4: If stale (PID dead): Remove lock, proceed
- FR-14.5: If active (PID alive): Display error, exit 1
- FR-14.6: Release lock on completion (success or failure)

**Validation:** Only one upgrade runs at a time.

---

## 🚀 Non-Functional Requirements

### NFR-1: Performance
**Priority:** P0 (Must Have)

- NFR-1.1: Total upgrade time < 5 minutes (typical)
- NFR-1.2: Backup creation < 10 seconds
- NFR-1.3: File copy < 90 seconds
- NFR-1.4: Dependency update < 60 seconds
- NFR-1.5: Validation < 30 seconds

**Validation:** Measure with `time` command, 95th percentile < 5min.

---

### NFR-2: Reliability
**Priority:** P0 (Must Have)

- NFR-2.1: 99.9% success rate (< 0.1% failures)
- NFR-2.2: 100% automatic rollback on failure
- NFR-2.3: 100% user content preservation
- NFR-2.4: 0% data loss (backup + restore)

**Validation:** Run 1000 upgrades, measure success rate, verify no data loss.

---

### NFR-3: Maintainability
**Priority:** P0 (Must Have)

- NFR-3.1: Single script (< 1000 lines)
- NFR-3.2: Reuse 80%+ of `install-praxis-os.py` logic
- NFR-3.3: Clear function documentation
- NFR-3.4: Type hints on all functions
- NFR-3.5: Unit test coverage > 80%

**Validation:** Code review, test coverage report.

---

### NFR-4: Usability
**Priority:** P0 (Must Have)

- NFR-4.1: Single command to upgrade
- NFR-4.2: Progress indicators during long operations
- NFR-4.3: Clear success/failure messages
- NFR-4.4: Actionable error messages with remediation
- NFR-4.5: `--help` flag with examples

**Validation:** User testing, documentation review.

---

### NFR-5: Safety
**Priority:** P0 (Must Have)

- NFR-5.1: Mandatory backup (unless `--skip-backup`)
- NFR-5.2: Atomic file operations
- NFR-5.3: Checksum validation
- NFR-5.4: Automatic rollback on failure
- NFR-5.5: Dry-run mode for preview

**Validation:** Failure injection testing, verify rollback works.

---

### NFR-6: Compatibility
**Priority:** P0 (Must Have)

- NFR-6.1: Python ≥ 3.9
- NFR-6.2: Works on macOS, Linux, Windows (Git Bash)
- NFR-6.3: No external dependencies beyond Python stdlib + existing
- NFR-6.4: Compatible with existing `.praxis-os/` structure

**Validation:** Test on all platforms, verify no new deps.

---

## 🚫 Out of Scope

### Explicitly NOT Included:

1. **Generic Breaking Change Migration**
   - Rationale: Too complex, error-prone
   - Alternative: Case-by-case detection with clear error messages

2. **GUI Upgrade Interface**
   - Rationale: CLI-first for automation, GUI is future work
   - Alternative: Well-designed CLI with rich output

3. **MCP Server Restart Control**
   - Rationale: Script cannot control Cursor/IDE restart
   - Alternative: User instructions for manual restart

4. **Smoke Testing MCP Tools**
   - Rationale: Requires running MCP server (can't control)
   - Alternative: File-based validation + user testing instructions

5. **Config Schema Auto-Migration**
   - Rationale: Complex, context-dependent
   - Alternative: LLM-driven semantic merge (human oversight)

6. **Remote Upgrade Orchestration**
   - Rationale: Consumer-side only, no server coordination
   - Alternative: User runs script locally

7. **Incremental Upgrades (Skip Versions)**
   - Rationale: Always upgrade to latest, no intermediate versions
   - Alternative: Fresh install if too far behind

8. **Rollback to Arbitrary Version**
   - Rationale: Only rollback to pre-upgrade state
   - Alternative: Re-run upgrade to different version

9. **Plugin/Extension Upgrade**
   - Rationale: No plugin system yet
   - Alternative: Future work when plugins exist

10. **Video Walkthrough Documentation**
    - Rationale: Low priority, way in the future
    - Alternative: Comprehensive written docs

---

## 📊 Success Metrics

### Quantitative Metrics:

1. **Upgrade Success Rate:** ≥ 99.9%
2. **Upgrade Time:** < 5 minutes (95th percentile)
3. **Backup Size:** < 100MB (excluding indexes)
4. **Backup Time:** < 10 seconds
5. **User Content Loss:** 0% (100% preservation)
6. **Support Tickets:** < 5% of upgrades require intervention
7. **Rollback Success Rate:** 100% (all failures recover)

### Qualitative Metrics:

1. **User Confidence:** Users trust upgrades won't break their work
2. **Documentation Clarity:** Users understand upgrade process
3. **Error Message Quality:** Users can self-remediate issues
4. **Framework Velocity:** Developers ship updates fearlessly

---

## 📚 Supporting Documentation

See `supporting-docs/` for:
- `design-doc.md` - Detailed design decisions and architecture

---

## 🔄 Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-11-13 | AI Agent (Claude) | Initial SRD based on design doc |

---

**Next Phase:** Design Specification (specs.md)

