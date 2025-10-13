# System Requirements Document (SRD)

## Agent OS Upgrade Workflow

**Version:** 1.0  
**Date:** 2025-10-08  
**Status:** Requirements Phase  
**Workflow ID:** `agent_os_upgrade_v1`

---

## 1. Business Goals

### BG-1: Automate Agent OS Upgrades

**Objective:** Eliminate manual upgrade steps and reduce upgrade time from 10+ minutes (manual) to under 2 minutes (automated).

**Success Metrics:**
- **Adoption:** 80%+ of users use automated workflow within 30 days
- **Time Savings:** Average upgrade time < 2 minutes (vs 10+ manual)
- **Success Rate:** > 95% of upgrades succeed without manual intervention
- **User Satisfaction:** NPS score > 50 for upgrade experience

**Business Impact:**
- Reduces support burden (fewer upgrade-related issues)
- Increases adoption velocity (easier to stay current)
- Enables faster feature deployment
- Reduces downtime during upgrades

---

### BG-2: Increase Upgrade Safety & Reliability

**Objective:** Provide automatic rollback capability to eliminate fear of failed upgrades.

**Success Metrics:**
- **Rollback Success:** 100% of rollback attempts succeed
- **Rollback Time:** < 30 seconds to restore previous version
- **Data Preservation:** 0 instances of user data/config loss
- **Detection Rate:** 100% of failed upgrades detected automatically

**Business Impact:**
- Increases user confidence in upgrading
- Reduces downtime from failed upgrades
- Preserves user customizations
- Enables "upgrade without fear" mentality

---

### BG-3: Demonstrate Meta-Framework for Operational Tasks

**Objective:** Showcase Agent OS meta-workflow handling complex operational workflows with state persistence across server restarts.

**Success Metrics:**
- **Resumability:** 100% success rate resuming after server restart
- **Documentation:** Complete workflow serves as reference implementation
- **Reusability:** Pattern adopted for 2+ other operational workflows
- **Complexity Handling:** Successfully handles 6-phase workflow with server restart

**Business Impact:**
- Validates Agent OS architecture for production use
- Creates reusable patterns for complex workflows
- Demonstrates value to potential enterprise users
- Increases confidence in Agent OS capabilities

---

## 2. User Stories

### US-1: Safe Upgrade with Automatic Rollback

**As a** developer using Agent OS in my project  
**I want** to upgrade Agent OS with a single command and automatic rollback if something fails  
**So that** I can stay current without fear of breaking my development environment

**Acceptance Criteria:**
1. ✅ Single command initiates upgrade process
2. ✅ Pre-flight checks validate source and target before any changes
3. ✅ Automatic backup created before any modifications
4. ✅ If any phase fails, automatic rollback to backup
5. ✅ Rollback completes in < 30 seconds
6. ✅ All user customizations preserved (config, custom files)
7. ✅ Clear messaging at each step showing progress
8. ✅ Final report shows what was upgraded

**Priority:** P0 (Must Have)

---

### US-2: Resume Upgrade After Server Restart

**As a** developer upgrading Agent OS  
**I want** the upgrade workflow to survive the MCP server restart  
**So that** the workflow can upgrade the server itself without manual intervention

**Acceptance Criteria:**
1. ✅ Workflow state persists to disk (`.agent-os/.cache/state/`)
2. ✅ State includes current phase, completed phases, and artifacts
3. ✅ After server restart, workflow can be resumed with session ID
4. ✅ Resume picks up at Phase 4 (post-restart validation)
5. ✅ All previous phase artifacts available to subsequent phases
6. ✅ No data loss during restart

**Priority:** P0 (Must Have)

---

### US-3: Preview Changes Before Applying

**As a** developer cautious about upgrades  
**I want** to see what will change before committing to the upgrade  
**So that** I can review impacts and decide whether to proceed

**Acceptance Criteria:**
1. ✅ Dry-run mode available via configuration option
2. ✅ Preview shows: new files, updated files, conflicts
3. ✅ File-level diff available for key changes
4. ✅ Clear indication of any potential conflicts
5. ✅ Can proceed with actual upgrade after reviewing preview
6. ✅ Preview completes in < 30 seconds

**Priority:** P1 (Should Have)

---

### US-4: Resolve Conflicts Interactively

**As a** developer with custom modifications  
**I want** to be prompted when conflicts are detected  
**So that** I can choose how to resolve them without losing my changes

**Acceptance Criteria:**
1. ✅ Conflict detection during content upgrade (Phase 2)
2. ✅ AI prompts for each conflict with context
3. ✅ Options: keep local, use remote, merge, skip
4. ✅ Can review file content before deciding
5. ✅ All decisions logged in upgrade report
6. ✅ Can abort upgrade if conflicts are too complex

**Priority:** P1 (Should Have)

---

## 3. Functional Requirements

### Core Upgrade Requirements

| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| FR-1 | Validate source repo is clean (no uncommitted changes) before upgrade | MUST | US-1 |
| FR-2 | Create timestamped backup (format: `YYYY-MM-DD-HHMMSS`) before any modifications | MUST | US-1 |
| FR-3 | Use `safe-upgrade.py` script for content upgrade with conflict detection | MUST | US-4 |
| FR-4 | Sync MCP server code from source to `.agent-os/mcp_server/` | MUST | US-2 |
| FR-5 | Install Python dependencies from `requirements.txt` | MUST | FR-4 |
| FR-6 | Detect and execute post-install steps (e.g., `playwright install chromium`) | MUST | FR-5 |
| FR-7 | Restart MCP server gracefully (pkill + restart) | MUST | US-2 |
| FR-8 | Persist workflow state to disk (`.agent-os/.cache/state/{session-id}.json`) | MUST | US-2 |
| FR-9 | Validate upgrade succeeded via smoke tests and tool registration checks | MUST | US-1 |
| FR-10 | Automatic rollback on failure (Phase 2, 3, or 4) | SHOULD | US-1 |
| FR-11 | Generate upgrade report documenting all changes | SHOULD | US-1 |
| FR-12 | Support dry-run mode to preview changes | SHOULD | US-3 |

---

### Validation & Safety Requirements

| ID | Requirement | Priority | Rationale |
|----|-------------|----------|-----------|
| FR-13 | Check source path exists and is `agent-os-enhanced` repo | MUST | Prevent invalid source |
| FR-14 | Check git status is clean (no uncommitted changes) in source | MUST | Prevent partial upgrades |
| FR-15 | Validate target `.agent-os/` directory structure | MUST | Prevent corruption |
| FR-16 | Check available disk space (need 2x current `.agent-os` size) | MUST | Prevent out-of-space failures |
| FR-17 | Check for concurrent upgrade workflows (`.agent-os/.upgrade-lock`) | MUST | Prevent race conditions |
| FR-18 | Verify backup integrity via checksums | MUST | Ensure rollback works |
| FR-19 | Validate copied files match source via checksums | MUST | Detect corruption |
| FR-20 | Check server health after restart (tools respond) | MUST | Catch restart failures |

---

### State & Resumability Requirements

| ID | Requirement | Priority | Implementation |
|----|-------------|----------|----------------|
| FR-21 | Save workflow state after each phase completion | MUST | Write to `.cache/state/` |
| FR-22 | State includes: session ID, current phase, completed phases, artifacts | MUST | JSON format |
| FR-23 | State persists across MCP server restart | MUST | Disk-based storage |
| FR-24 | Provide `get_workflow_state(session_id)` to resume | MUST | Load from disk |
| FR-25 | Phase artifacts accessible to subsequent phases | MUST | Pass via state |

---

### Reporting & Documentation Requirements

| ID | Requirement | Priority | Output |
|----|-------------|----------|--------|
| FR-26 | Generate upgrade summary report | SHOULD | `.cache/upgrade-summary-{date}.md` |
| FR-27 | Update `INSTALLATION_SUMMARY.md` with upgrade details | SHOULD | Append to existing |
| FR-28 | Append to `UPDATE_LOG.txt` | SHOULD | Timestamped entry |
| FR-29 | Create validation report | SHOULD | `.cache/upgrade-validation-{date}.json` |
| FR-30 | Archive old backups (keep last 3) | MAY | Delete older backups |

---

## 4. Non-Functional Requirements

### Performance (NFR-P)

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-P1 | Total upgrade time (no conflicts) | < 2 minutes | End-to-end timer |
| NFR-P2 | Upgrade time with conflicts | < 5 minutes | End-to-end timer |
| NFR-P3 | Rollback time | < 30 seconds | Rollback timer |
| NFR-P4 | Dry-run preview time | < 30 seconds | Preview generation |
| NFR-P5 | Server restart time | < 10 seconds | Health check latency |

---

### Reliability (NFR-R)

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-R1 | Upgrade success rate (no conflicts) | > 95% | Telemetry |
| NFR-R2 | Rollback success rate | 100% | Telemetry |
| NFR-R3 | State persistence success rate | 100% | Resume attempts |
| NFR-R4 | Backup integrity verification | 100% | Checksum validation |
| NFR-R5 | Zero data loss events | 100% | User reports |

---

### Usability (NFR-U)

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-U1 | Single command to start upgrade | 1 command | API design |
| NFR-U2 | Clear progress messaging at each phase | 100% phases | User feedback |
| NFR-U3 | Actionable error messages | 100% errors | User feedback |
| NFR-U4 | User prompts only when necessary | < 3 prompts | Typical case |
| NFR-U5 | Upgrade report human-readable | Yes | Review |

---

### Maintainability (NFR-M)

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-M1 | Documentation coverage | 100% phases | Review |
| NFR-M2 | Phase files < 200 lines | Yes | Line count |
| NFR-M3 | Task files 100-170 lines | Yes | Line count |
| NFR-M4 | Reusable rollback procedure | Yes | Code review |
| NFR-M5 | Follows meta-workflow standards | 100% | Compliance check |

---

### Security (NFR-S)

| ID | Requirement | Target | Rationale |
|----|-------------|--------|-----------|
| NFR-S1 | Never delete user content | Enforce | Preserve work |
| NFR-S2 | Never overwrite config without prompt | Enforce | Preserve settings |
| NFR-S3 | Validate source git clean | Enforce | Prevent malicious code |
| NFR-S4 | Checksum validation on all copies | Enforce | Detect tampering |
| NFR-S5 | Lock prevents concurrent upgrades | Enforce | Race condition prevention |

---

## 5. Workflow Structure

### Phase Overview

The upgrade workflow consists of 6 phases:

| Phase | Name | Duration | Critical Actions |
|-------|------|----------|-----------------|
| 0 | Pre-Flight Checks | ~30s | Validate source, target, disk space |
| 1 | Backup & Preparation | ~20s | Create backup, acquire lock |
| 2 | Content Upgrade | ~45s | Run safe-upgrade.py, handle conflicts |
| 3 | MCP Server Upgrade | ~60s | Copy code, install deps, **restart server** |
| 4 | Post-Upgrade Validation | ~30s | Smoke tests, tool checks |
| 5 | Cleanup & Documentation | ~15s | Release lock, archive backups, reports |

**Total Duration:** ~3 minutes 20 seconds

**Critical Path:** Phase 3 (server restart) → requires state persistence

---

### State Persistence Schema

```json
{
  "session_id": "uuid",
  "workflow_type": "agent_os_upgrade_v1",
  "target_file": "mcp_server",
  "current_phase": 3,
  "completed_phases": [0, 1, 2],
  "phase_artifacts": {
    "0": {
      "source_path": "/path/to/agent-os-enhanced",
      "source_version": "1.2.0",
      "source_commit": "abc123",
      "validation_passed": true
    },
    "1": {
      "backup_path": ".agent-os/.backups/2025-10-08-103045/",
      "backup_size": "45.2 MB",
      "files_backed_up": 487
    },
    "2": {
      "content_upgrade_report": {
        "new_files": 3,
        "updated_files": 12,
        "conflicts": 0
      }
    }
  },
  "metadata": {
    "dry_run": false,
    "auto_restart": true
  }
}
```

---

## 6. Dependencies & Integration

### External Systems

| System | Purpose | Integration Point |
|--------|---------|------------------|
| `safe-upgrade.py` | Content upgrade with conflict detection | Phase 2 (subprocess) |
| `workflow_engine.py` | Workflow orchestration | All phases |
| `state_manager.py` | State persistence | Phase 0-5 |
| `pip` | Dependency installation | Phase 3 |
| `playwright` | Browser automation dependencies | Phase 3 (post-install) |
| `git` | Source validation | Phase 0 |

---

### File System Structure

```
.agent-os/
├── .cache/
│   └── state/
│       └── {session-id}.json       # Workflow state
├── .backups/
│   └── YYYY-MM-DD-HHMMSS/          # Timestamped backup
│       ├── MANIFEST.json           # Checksum manifest
│       ├── mcp_server/             # Server code backup
│       ├── config.json             # Config backup
│       └── requirements-snapshot.txt
├── .upgrade-lock                   # Concurrent upgrade prevention
├── mcp_server/                     # MCP server code (upgraded)
├── standards/                      # Content (upgraded)
├── usage/                          # Content (upgraded)
├── workflows/                      # Content (upgraded)
└── config.json                     # User config (preserved)
```

---

## 7. Acceptance Criteria

### Overall Success Criteria

An upgrade is considered successful if:

1. ✅ All 6 phases complete without errors
2. ✅ MCP server responds to requests after restart
3. ✅ All expected MCP tools registered
4. ✅ Smoke tests pass (RAG search, workflow list, browser session)
5. ✅ No errors in server log
6. ✅ Version updated correctly in all locations
7. ✅ User config and customizations preserved
8. ✅ Upgrade report generated

---

### Rollback Success Criteria

A rollback is considered successful if:

1. ✅ Restore completes in < 30 seconds
2. ✅ Server starts successfully after restore
3. ✅ All tools functional with previous version
4. ✅ User config and data intact
5. ✅ No residual files from failed upgrade

---

## 8. Out of Scope

### Explicitly Out of Scope (v1.0)

| Item | Rationale | Future Consideration |
|------|-----------|---------------------|
| Partial upgrades (content-only or MCP-only) | Increases complexity, risk of version mismatch | Consider for v1.1 |
| Multi-project batch upgrades | Single project is MVP | Consider for v2.0 |
| Auto-update on schedule (cron) | Requires additional testing infrastructure | Consider for v2.0 |
| Cloud backup integration | Adds external dependency | Consider for v2.0 |
| Custom MCP server modification detection | Complex three-way merge required | Consider for v1.1 |
| Canary deployments | Requires multiple environments | Consider for v2.0 |
| Delta upgrades (only changed files) | Complexity vs. benefit not justified yet | Consider for v1.1 if performance issue |
| Automatic git commit of upgrades | User repo modification requires permission | Make optional in v1.1 |
| Migration for breaking changes | Handle manually in v1.0 | Build framework in v1.1 |
| Full unit test suite during validation | Too slow (>1 minute) | Make optional in v1.0 |

---

### Assumptions

1. User has `agent-os-enhanced` repository cloned locally
2. Source repository is on `main` branch (or specified branch)
3. Python 3.8+ and pip are available
4. Sufficient disk space (2x current `.agent-os` size)
5. User has write permissions to `.agent-os/` directory
6. Network access for pip installs
7. MCP server can be restarted without breaking other processes

---

### Constraints

1. Must use existing `safe-upgrade.py` (no re-implementation)
2. Must follow meta-workflow three-tier architecture
3. Must persist state to disk (no database dependency)
4. Phase files must be ≤ 200 lines
5. Task files must be 100-170 lines
6. Must work with copy-based installation (not symlink)
7. Must handle MCP server restart within workflow

---

## 9. Success Metrics

### Key Performance Indicators (KPIs)

| Metric | Baseline | Target | Timeline |
|--------|----------|--------|----------|
| Manual upgrade time | ~10 min | < 2 min | Immediate |
| Upgrade-related support tickets | ~5/week | < 1/week | 30 days |
| Users on latest version | ~40% | > 80% | 60 days |
| Failed upgrade rate | Unknown | < 5% | 30 days |
| Rollback usage rate | N/A | < 10% | 30 days |
| User satisfaction (NPS) | Unknown | > 50 | 60 days |

---

### Validation Checkpoints

Each phase has explicit validation gates (see Phase Design in supporting docs):

- **Phase 0:** Source valid, target valid, disk space, no lock
- **Phase 1:** Backup created, integrity verified, lock acquired
- **Phase 2:** Content upgraded, conflicts resolved, version updated
- **Phase 3:** Server copied, deps installed, server restarted, health check passed
- **Phase 4:** Tools registered, smoke tests passed, no errors
- **Phase 5:** Lock released, backups archived, reports generated

---

## 10. Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| State corruption during server restart | Low | High | Atomic writes, backup state file |
| Dependency install failure | Medium | High | Rollback automatically |
| Server fails to restart | Low | High | Health check, automatic rollback |
| Disk space exhausted mid-upgrade | Low | High | Pre-flight disk check |
| User customizations overwritten | Low | Critical | Use safe-upgrade.py, never force overwrite |
| Concurrent upgrade attempts | Medium | Medium | Lock file prevents concurrent runs |
| Network failure during pip install | Medium | Medium | Retry logic, fallback to rollback |
| Playwright install fails (large download) | Medium | Low | Post-install step, can retry manually |

---

## 11. References

### Supporting Documents

- [Design Document](supporting-docs/agent-os-upgrade-workflow-design.md) - Complete architecture and design
- [Document Index](supporting-docs/INDEX.md) - All supporting documents catalog
- [Extracted Insights](supporting-docs/INSIGHTS.md) - Requirements, design, implementation insights

---

### Related Specs

- `.agent-os/specs/2025-10-07-manifest-based-upgrade-system/` - Safe upgrade implementation
- `mcp_server/workflow_engine.py` - Workflow orchestration
- `mcp_server/state_manager.py` - State persistence
- `universal/usage/mcp-server-update-guide.md` - Manual upgrade guide (to be replaced)

---

## 12. Approval & Sign-Off

| Role | Name | Date | Status |
|------|------|------|--------|
| Requirements Author | AI Assistant | 2025-10-08 | ✅ Complete |
| Reviewer | TBD | TBD | ⏳ Pending |
| Approver | Josh (Human) | TBD | ⏳ Pending |

---

## Changelog

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-10-08 | Initial SRD created from design document | AI Assistant |

---

**Status:** ✅ Requirements Complete  
**Next Phase:** Phase 2 - Technical Specifications (specs.md)

---

_This document defines **WHAT** needs to be built. See `specs.md` for **HOW** it will be built._

