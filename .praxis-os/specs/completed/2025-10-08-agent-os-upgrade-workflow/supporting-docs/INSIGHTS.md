# Extracted Insights - Agent OS Upgrade Workflow

**Source:** agent-os-upgrade-workflow-design.md  
**Date:** 2025-10-08  
**Extraction Status:** ✅ Complete

---

## Requirements Insights

### Functional Requirements (12 total)

| ID | Requirement | Priority | Implementation Notes |
|----|-------------|----------|---------------------|
| FR-1 | Validate source repo before upgrade | MUST | Check git status, version, commit hash |
| FR-2 | Create timestamped backups | MUST | Format: `.praxis-os/.backups/YYYY-MM-DD-HHMMSS/` |
| FR-3 | Use safe-upgrade.py for content | MUST | Leverage existing conflict detection |
| FR-4 | Sync MCP server code to .praxis-os/ | MUST | Copy `mcp_server/` directory |
| FR-5 | Install dependencies from requirements.txt | MUST | Include post-install steps |
| FR-6 | Handle post-install steps | MUST | Playwright, other system deps |
| FR-7 | Restart MCP server gracefully | MUST | pkill + restart, health check |
| FR-8 | Persist workflow state across restart | MUST | **Critical innovation** |
| FR-9 | Validate upgrade succeeded | MUST | Smoke tests, tool registration |
| FR-10 | Rollback on failure | SHOULD | Target < 30 seconds |
| FR-11 | Generate upgrade report | SHOULD | Document changes |
| FR-12 | Support dry-run mode | SHOULD | Preview before apply |

### Safety Requirements (6 total)

| ID | Requirement | Implementation |
|----|-------------|----------------|
| SR-1 | Never delete user content | Preserve customizations |
| SR-2 | Never overwrite config without prompt | Preserve user settings |
| SR-3 | Create backup before destructive ops | Enable rollback |
| SR-4 | Validate checksums after copy | Detect corruption |
| SR-5 | Require clean git state in source | Prevent partial upgrades |
| SR-6 | Lock workflow to prevent concurrent upgrades | Use `.praxis-os/.upgrade-lock` |

### Non-Functional Requirements (5 total)

| ID | Target | Measurement |
|----|--------|-------------|
| NFR-1 | Upgrade time < 2 minutes (typical) | Timer |
| NFR-2 | Upgrade time < 5 minutes (with conflicts) | Timer |
| NFR-3 | Rollback time < 30 seconds | Timer |
| NFR-4 | Success rate > 95% (no conflicts) | Telemetry |
| NFR-5 | Documentation quality = 100% phase coverage | Review |

### User Needs

1. **Automation:** Eliminate manual upgrade steps
2. **Safety:** Rollback capability if upgrade fails
3. **Reliability:** Validate each step, catch failures early
4. **Resumability:** Survive MCP server restart
5. **Transparency:** Clear reporting of what changed

---

## Design Insights

### Architecture Patterns

**Three-Tier Architecture:**
1. **Workflow Definition** (`metadata.json`, `phases/*.md`)
2. **Workflow Engine** (`workflow_engine.py` - orchestration)
3. **State Manager** (`state_manager.py` - persistence)

**Key Design Decisions:**

1. **State Persistence Strategy**
   - Location: `.praxis-os/.cache/state/{session-id}.json`
   - Contents: Session metadata, current phase, completed phases, phase artifacts
   - **Critical:** Enables workflow to survive MCP server restart
   - Resume via: `get_workflow_state(session_id)` → reads from disk

2. **Phase Structure (6 phases)**
   ```
   Phase 0: Pre-Flight Checks (30s)
   Phase 1: Backup & Preparation (20s)
   Phase 2: Content Upgrade (45s)
   Phase 3: MCP Server Upgrade (60s) ⚠️ Server restart
   Phase 4: Post-Upgrade Validation (30s)
   Phase 5: Cleanup & Documentation (15s)
   Total: ~3m 20s
   ```

3. **Rollback Architecture**
   - Trigger: Phase 2, 3, or 4 failure
   - Mechanism: Restore from timestamped backup
   - Target time: < 30 seconds
   - Preserves: User content, config, customizations

4. **Validation Gates**
   - Each phase has checkpoint evidence requirements
   - Must pass validation before advancing
   - Structured JSON evidence format

5. **Component Interactions**
   ```
   User → AI → Workflow → StateManager → SafeUpgrade
                      ↓
                  MCPServer (restart)
                      ↓
                  Resume workflow from state
   ```

### Technical Approaches

**Backup Strategy:**
- Timestamped directories: `YYYY-MM-DD-HHMMSS`
- Manifest with checksums (integrity verification)
- Keep last 3 backups, archive older ones

**Content Upgrade:**
- Use existing `safe-upgrade.py` script
- Dry-run preview before actual upgrade
- Interactive conflict resolution
- Update VERSION.txt and UPDATE_LOG.txt

**MCP Server Upgrade:**
- Copy files with checksum verification
- Detect post-install requirements (scan requirements.txt)
- Auto-run post-install steps (playwright install, etc.)
- Health check after restart

**Validation:**
- Tool registration check (count expected tools)
- Smoke tests (RAG search, workflow list, browser)
- File watcher status
- RAG index currency
- Optional: full unit test suite

### Error Handling Strategies

| Scenario | Detection | Handling |
|----------|-----------|----------|
| Source uncommitted changes | Phase 0 git check | ❌ Abort |
| Insufficient disk space | Phase 0 disk check | ❌ Abort |
| Backup fails | Phase 1 verify | ❌ Abort |
| Content conflicts | Phase 2 safe-upgrade | ⚠️ Prompt AI |
| Dependency install fails | Phase 3 pip | 🔄 Rollback |
| Server won't restart | Phase 3 health check | 🔄 Rollback |
| Validation fails | Phase 4 smoke tests | 🔄 Rollback |
| Concurrent upgrade | Phase 0 lock check | ❌ Abort |
| State corrupted | Resume | 🔄 Rollback to checkpoint |

---

## Implementation Insights

### Phase 0: Pre-Flight Checks

**Commands:**
```python
# Validate source
os.path.exists(source_path)
subprocess.run(["git", "status", "--porcelain"], cwd=source_path)
subprocess.run(["git", "rev-parse", "HEAD"], cwd=source_path)

# Check target
os.path.exists(".praxis-os/")
validate_directory_structure()

# Disk space
shutil.disk_usage(".praxis-os/")

# Lock check
not os.path.exists(".praxis-os/.upgrade-lock")
```

**Evidence:**
```json
{
  "source_path": "/path/to/praxis-os",
  "source_version": "1.2.0",
  "source_commit": "abc123def",
  "source_git_clean": true,
  "target_exists": true,
  "target_structure_valid": true,
  "disk_space_available": "2.5 GB",
  "disk_space_required": "500 MB",
  "no_concurrent_workflows": true
}
```

### Phase 1: Backup & Preparation

**Commands:**
```python
# Create backup
timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
backup_path = f".praxis-os/.backups/{timestamp}/"
shutil.copytree(".praxis-os/mcp_server", f"{backup_path}/mcp_server")
shutil.copy(".praxis-os/config.json", backup_path)

# Generate manifest
generate_checksums(backup_path)

# Acquire lock
Path(".praxis-os/.upgrade-lock").touch()
```

**Evidence:**
```json
{
  "backup_path": ".praxis-os/.backups/2025-10-08-103045/",
  "backup_timestamp": "2025-10-08T10:30:45Z",
  "files_backed_up": 487,
  "backup_size_bytes": 47483648,
  "backup_manifest": ".praxis-os/.backups/2025-10-08-103045/MANIFEST.json",
  "integrity_verified": true,
  "lock_acquired": true
}
```

### Phase 2: Content Upgrade

**Commands:**
```python
# Dry run preview
subprocess.run([
    "python", "scripts/safe-upgrade.py",
    "--source", source_path,
    "--target", ".praxis-os",
    "--dry-run"
])

# Actual upgrade
subprocess.run([
    "python", "scripts/safe-upgrade.py",
    "--source", source_path,
    "--target", ".praxis-os"
])

# Update version
update_version_file(new_version)
append_update_log(changes)
```

**Evidence:**
```json
{
  "safe_upgrade_executed": true,
  "dry_run_preview": {
    "new_files": 3,
    "updated_files": 12,
    "unchanged_files": 145,
    "conflicts": 0,
    "local_only": 2
  },
  "actual_upgrade": {
    "new_files": 3,
    "updated_files": 12,
    "conflicts_resolved": 0,
    "user_prompts": 0
  },
  "version_updated": "1.2.0",
  "update_log_appended": true
}
```

### Phase 3: MCP Server Upgrade (⚠️ Critical)

**Commands:**
```python
# Copy MCP server
shutil.copytree(
    f"{source_path}/mcp_server",
    ".praxis-os/mcp_server",
    dirs_exist_ok=True
)
verify_checksums()

# Install dependencies
subprocess.run([
    "pip", "install", "-r",
    ".praxis-os/mcp_server/requirements.txt"
])

# Post-install steps
subprocess.run(["playwright", "install", "chromium"])

# Restart server
subprocess.run(["pkill", "-f", "python -m mcp_server"])
subprocess.Popen(["python", "-m", "mcp_server"], cwd=".praxis-os")

# Wait for health check
wait_for_server_ready()
```

**Evidence:**
```json
{
  "mcp_server_copied": true,
  "files_copied": 42,
  "checksums_verified": true,
  "dependencies_installed": true,
  "post_install_steps": [
    {
      "command": "playwright install chromium",
      "status": "success",
      "size_downloaded": "129.7 MB"
    }
  ],
  "server_restarted": true,
  "server_restart_time": "2025-10-08T10:32:15Z",
  "server_health_check": "passed"
}
```

**Resume Logic:**
```python
# After restart, AI continues workflow
state = get_workflow_state(session_id)
current_phase = state["current_phase"]  # Should be 4
# Continue to Phase 4
```

### Phase 4: Post-Upgrade Validation

**Commands:**
```python
# Check tools
tools = list_mcp_tools()
assert len(tools) == expected_count

# Smoke tests
test_rag_search()
test_workflow_list()
test_browser_session()

# File watcher
check_file_watcher_status()

# RAG index
check_rag_index_current()

# Unit tests (optional)
subprocess.run(["pytest", "tests/"])
```

**Evidence:**
```json
{
  "server_version": "1.2.0",
  "tools_registered": 8,
  "expected_tools": 8,
  "browser_tools_enabled": true,
  "browser_smoke_test": "passed",
  "rag_search_test": "passed",
  "workflow_engine_test": "passed",
  "file_watchers_active": true,
  "rag_index_current": true,
  "unit_tests_passed": true,
  "validation_report": ".praxis-os/.cache/upgrade-validation-2025-10-08.json"
}
```

### Phase 5: Cleanup & Documentation

**Commands:**
```python
# Release lock
os.remove(".praxis-os/.upgrade-lock")

# Archive old backups
archive_old_backups(keep=3)

# Generate reports
generate_upgrade_summary()
update_installation_summary()
append_to_update_log()

# Optional git commit
if config.get("git_commit_after"):
    subprocess.run(["git", "add", ".praxis-os/"])
    subprocess.run(["git", "commit", "-m", "Upgrade Agent OS to v1.2.0"])
```

**Evidence:**
```json
{
  "lock_released": true,
  "old_backups_archived": 2,
  "upgrade_summary": ".praxis-os/.cache/upgrade-summary-2025-10-08.md",
  "installation_summary_updated": true,
  "update_log_appended": true,
  "git_changes_committed": false
}
```

### Rollback Procedure

**Commands:**
```python
# Get backup path from state
backup_path = state["phase_artifacts"]["1"]["backup_path"]

# Stop server
subprocess.run(["pkill", "-f", "python -m mcp_server"])

# Restore files
shutil.copytree(f"{backup_path}/mcp_server", ".praxis-os/mcp_server", dirs_exist_ok=True)
shutil.copy(f"{backup_path}/config.json", ".praxis-os/")
# ... restore other directories ...

# Restore dependencies
subprocess.run(["pip", "install", "-r", f"{backup_path}/requirements-snapshot.txt"])

# Restart server
subprocess.Popen(["python", "-m", "mcp_server"], cwd=".praxis-os")

# Verify
wait_for_server_ready()

# Update state
update_workflow_state(status="rolled_back", reason="...")
```

### Testing Patterns

**Unit Tests:**
- Mock file operations
- Mock subprocess calls
- Test each phase independently
- Test checkpoint validation
- Test state persistence

**Integration Tests:**
- Create test environment
- Run full workflow end-to-end
- Simulate failures at each phase
- Verify rollback works
- Test resume after restart

**Validation Criteria:**
```python
def validate_upgrade_success():
    checks = [
        all_phases_completed(),
        server_responds(),
        tools_registered(),
        smoke_tests_pass(),
        no_errors_in_log(),
        version_updated_correctly()
    ]
    return all(checks)
```

---

## Key Innovations

1. **State Persistence Across Restart**
   - First workflow to survive MCP server restart
   - Enables server upgrade within workflow
   - Uses disk-based state storage

2. **Integrated Rollback**
   - Automatic on failure detection
   - Sub-30-second target
   - Preserves user customizations

3. **Comprehensive Validation**
   - Pre-flight checks prevent bad upgrades
   - Post-upgrade validation catches failures
   - Checkpoint evidence at each phase

4. **Safe Content Handling**
   - Uses existing safe-upgrade.py
   - Dry-run preview
   - Interactive conflict resolution

---

## Future Considerations

1. **Partial Upgrades** (v1.1)
   - Content-only or MCP-only options
   - Faster for targeted updates
   - Need version compatibility checks

2. **Auto-Update** (v2.0)
   - Cron job for scheduled upgrades
   - Canary deployments
   - Cloud backup

3. **Custom Modification Handling**
   - Detect user changes to MCP server
   - Three-way merge for conflicts
   - Preserve customizations

---

## Summary Statistics

**Total Insights Extracted:**
- Requirements: 23 (12 FR + 6 SR + 5 NFR)
- Design Patterns: 5 major architectural decisions
- Implementation Details: 6 phases with complete command patterns
- Test Strategies: 3 levels (unit, integration, dogfooding)
- Error Scenarios: 9 edge cases with handling strategies

**High Priority Items:**
1. State persistence mechanism (enables restart)
2. Rollback procedure (safety net)
3. Validation gates (quality assurance)
4. Safe-upgrade integration (conflict handling)

**Conflicts/Risks Identified:** 0

**Status:** ✅ Ready for Phase 1 (Requirements Gathering)

---

**Extracted by:** AI Assistant  
**Date:** 2025-10-08  
**Version:** 1.0

