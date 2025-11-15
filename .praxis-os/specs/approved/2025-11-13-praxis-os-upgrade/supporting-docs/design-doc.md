# prAxIs OS Upgrade System - Design Document (DRAFT)

**Status**: 🚧 Phase 1 - Conversational Design  
**Date**: 2025-11-13  
**Purpose**: Design a robust, maintainable upgrade system for praxis-os installations

---

## 📋 TL;DR - Key Design Decisions

All 6 design questions have been resolved:

1. ✅ **Backup**: MANDATORY (5s, 50MB, excludes indexes) - Quality outcomes > speed
2. ✅ **Config**: Script copies template, LLM reconciles - Separation of concerns
3. ✅ **Rollback**: Automatic restore from mandatory backup - Defense in depth
4. ✅ **Breaking Changes**: Case-by-case detection, clear error messages - No generic migration
5. ✅ **Documentation**: docs + script + README (no video yet) - Comprehensive coverage
6. ✅ **Validation**: File-based only, user validates MCP - Script limitation

**Implementation:** `upgrade-praxis-os.py` script (~500-700 lines)  
**Time:** 3-5 minutes  
**Safety:** 6 defensive layers + mandatory backup

**Ready for Phase 2: Formal Spec Creation**

---

## 🎯 Problem Statement

The current upgrade process is broken:

### Current State Problems:
1. **Outdated Documentation**
   - References `mcp_server/` (should be `ouroboros/`)
   - References non-existent `usage/` directory
   - Manual rsync commands assume local source repo (deleted after install)

2. **Broken Workflow**
   - `praxis_os_upgrade_v1` workflow exists but has wrong paths
   - References `mcp_server.validation_module` (doesn't exist)
   - No breaking change migration logic

3. **No Clear Ownership Model**
   - Which files can be overwritten?
   - Which files must be preserved?
   - How to merge config changes?

4. **Installation Creates Snapshot**
   - `install-praxis-os.py` clones to temp → copies → deletes temp
   - No git relationship remains
   - Users have no easy update path

### Why This Is Critical:
- **Consumer installs are growing** - Need reliable upgrade path
- **Framework evolving** - Standards, workflows, server all change
- **Breaking changes happen** - Need migration strategy
- **User content preservation** - Can't lose specs/customizations

---

## 🎯 Design Goals

### Primary Goals:
1. ✅ **Preserve user content** - Never overwrite specs, custom standards
2. ✅ **Idempotent** - Safe to run multiple times
3. ✅ **Standalone** - Works without LLM/workflow complexity
4. ✅ **Maintainable** - Single script, ~500-700 lines
5. ✅ **Reuse install logic** - DRY principle, 80% code reuse
6. ✅ **Future-proof** - Ownership model in config, not hardcoded

### Secondary Goals:
7. ✅ **Fast** - Complete in 3-5 minutes
8. ✅ **Safe** - Optional backup, dry-run preview, checksums
9. ✅ **Informative** - Clear progress, detailed report
10. ✅ **Recoverable** - Easy rollback if something fails

---

## 🏗️ Proposed Architecture

### Script vs Workflow Decision:

**DECISION: Script (`upgrade-praxis-os.py`)**

**Rationale:**
- ✅ Reuses 80% of `install-praxis-os.py` logic
- ✅ Simpler to maintain (one file vs 35+ workflow files)
- ✅ No LLM required (faster, works headless)
- ✅ Can fix broken MCP server (workflow can't)
- ✅ Standard exit codes for automation
- ✅ Easier to test (unit tests vs integration only)

**Workflow would add:**
- ❌ LLM overhead (slower)
- ❌ Requires working MCP server
- ❌ State persistence complexity
- ❌ Multiple files to update for path changes
- ❌ Can't run automated/headless

---

## 📋 Ownership Model

### Framework Owns (Overwrite on Upgrade):
```
.praxis-os/standards/universal/    # Universal standards
.praxis-os/workflows/               # Phase-gated workflows
.praxis-os/ouroboros/               # MCP server code
.praxis-os/scripts/                 # Helper scripts
```

### User Owns (Never Overwrite):
```
.praxis-os/specs/                   # User's specifications
.praxis-os/standards/development/   # Language-specific standards
```

### Merge Strategy:
```
.praxis-os/config/mcp.yaml          # Preserve user customizations
.gitignore                          # Additive merge (add new patterns)
```

### Ephemeral (Skip):
```
.praxis-os/.cache/                  # Rebuild on demand
.praxis-os/workspace/               # Temporary (gitignored)
.praxis-os/venv/                    # Rebuild from requirements.txt
```

---

## 🔄 Upgrade Flow

### Phase 0: Pre-Flight Checks (30s)
```python
✓ Validate target has .praxis-os/
✓ Check .praxis-os/ouroboros/ exists (not broken install)
✓ Verify git installed
✓ Check disk space (need ~500MB for backup, excluding indexes)
✓ Validate Python version ≥ 3.9
```

### Phase 1: Backup (Mandatory, 5s)
```python
# Always create backup (unless --skip-backup)
✓ Create .praxis-os.backup.YYYYMMDD_HHMMSS/
    ✓ Backup essential files only:
        - ouroboros/ (server code)
        - standards/ (all standards)
        - workflows/ (all workflows)
        - config/ (configs)
        - specs/ (user specs)
        - scripts/ (helper scripts)
    ✗ Exclude ephemeral data:
        - .cache/ (indexes rebuild automatically)
        - workspace/ (temporary files, gitignored)
        - venv/ (rebuilt from requirements.txt)
        - *.pyc, __pycache__/ (Python bytecode)
    ✓ Generate checksum manifest
    ✓ Validate backup integrity
```

### Phase 2: Clone Source (30s)
```python
✓ Clone github.com/honeyhiveai/praxis-os to temp
✓ Extract version from source
✓ Compare with installed version
```

### Phase 3: Upgrade Framework Files (60s)
```python
# Overwrite framework-owned files
✓ rsync --delete dist/universal/standards/ → .praxis-os/standards/universal/
✓ rsync --delete dist/universal/workflows/ → .praxis-os/workflows/
✓ rsync --delete dist/ouroboros/ → .praxis-os/ouroboros/
✓ rsync --delete scripts/ → .praxis-os/scripts/

# Verify checksums
✓ Validate all copied files match source

# Generate upgrade report
✓ Show added files
✓ Show modified files
✓ Show deleted files
```

### Phase 4: Config Reconciliation Prep (15s)
```python
# Script prepares config for LLM merge
✓ Copy new template → .praxis-os/config/mcp.yaml.new
✓ Create CONFIG_RECONCILIATION_NEEDED.md prompt
✓ Detect if config changed (diff)
✓ If no changes: delete .new file, skip reconciliation
✓ If changes exist: Leave for LLM to merge

# Gitignore merge (automatic, no LLM needed)
✓ Read .gitignore patterns from standards
✓ Additive merge (add new, keep existing)
```

### Phase 5: Update Dependencies (45s)
```python
✓ Activate .praxis-os/venv
✓ pip install --upgrade -r ouroboros/requirements.txt
✓ Run post-install (playwright install if needed)
```

### Phase 6: Rebuild Indexes (Auto on next start)
```python
✓ Create .praxis-os/.rebuild_indexes flag
✓ MCP server will detect and rebuild on next start
```

### Phase 7: Validate Upgrade (30s)
```python
✓ Verify file counts match expected
✓ Check Python imports work (ouroboros package)
✓ Validate config schema
✓ Generate upgrade summary report
```

### Phase 8: Cleanup (15s)
```python
✓ Delete temp clone
if --archive-old-backups:
    ✓ Keep last 3 backups, delete older
✓ Print success message with next steps
```

**Total Time: 3-5 minutes**

---

## 🎛️ Command-Line Interface

### Basic Usage:
```bash
# Simple upgrade (backup is automatic)
python upgrade-praxis-os.py

# Dry-run preview (see what would change)
python upgrade-praxis-os.py --dry-run

# Quiet mode (CI/CD)
python upgrade-praxis-os.py --quiet

# Help
python upgrade-praxis-os.py --help
```

### Advanced Options:
```bash
# From local source (not GitHub)
python upgrade-praxis-os.py --source /path/to/praxis-os

# Skip backup (dangerous, not recommended)
python upgrade-praxis-os.py --skip-backup

# Keep more backups (default: 3)
python upgrade-praxis-os.py --keep-backups 5

# Skip dependency update (faster, for standards-only changes)
python upgrade-praxis-os.py --skip-deps

# Custom target directory
python upgrade-praxis-os.py /path/to/project
```

---

## 💾 Backup Strategy - Critical Optimization

### The Problem:
RAG indexes in `.praxis-os/.cache/indexes/` can be **2GB+**:
- Standards index: ~500MB (vector embeddings)
- Code index: ~1.5GB+ (depends on codebase size)
- Backing these up would:
  - ❌ Require 2GB+ extra disk space
  - ❌ Take 2-3 minutes to copy
  - ❌ Serve no purpose (indexes rebuild automatically)

### The Solution:
**Exclude ephemeral data from backups:**

```python
# Backup these (essential):
.praxis-os/ouroboros/              # Server code (~50MB)
.praxis-os/standards/              # Standards (~10MB)
.praxis-os/workflows/              # Workflows (~5MB)
.praxis-os/config/                 # Configs (~1MB)
.praxis-os/specs/                  # User specs (varies)
.praxis-os/scripts/                # Helper scripts (~1MB)

# Skip these (ephemeral/rebuildable):
.praxis-os/.cache/                 # Indexes (2GB+) ← SKIP THIS!
.praxis-os/workspace/              # Temp files (gitignored)
.praxis-os/venv/                   # Python env (rebuild from requirements.txt)
**/__pycache__/                    # Python bytecode
**/*.pyc                           # Python bytecode
```

### Benefits:
- ✅ **Backup size: ~50MB instead of 2GB+** (40x smaller!)
- ✅ **Backup time: ~5s instead of 2-3min** (24x faster!)
- ✅ **Disk space: Need 500MB not 4GB+** (8x less!)
- ✅ **Restore time: Instant** (indexes rebuild on first query)
- ✅ **No data loss** (indexes are derived data, not source)

### Implementation:
```python
def create_backup(target: Path) -> Path:
    """Create backup excluding ephemeral data"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = target / f".praxis-os.backup.{timestamp}"
    
    # Exclusions for shutil.copytree
    ignore_patterns = shutil.ignore_patterns(
        ".cache",           # RAG indexes (2GB+)
        "workspace",        # Temporary files
        "venv",             # Python virtualenv
        "__pycache__",      # Python bytecode
        "*.pyc",            # Python bytecode
        ".DS_Store",        # macOS metadata
    )
    
    shutil.copytree(
        target / ".praxis-os",
        backup_dir,
        ignore=ignore_patterns
    )
    
    return backup_dir
```

---

## 🔐 Safety Mechanisms

### 1. Pre-Flight Validation
- Verify existing installation is valid
- Check sufficient disk space
- Ensure git/python available

### 2. Optional Backup
- Timestamped backup directory
- Excludes ephemeral data (.cache/, workspace/, venv/)
- Checksum manifest for integrity
- Quick restore if needed
- Small backup size (~50MB vs 2GB+ with indexes)

### 3. Checksums
- SHA256 for every copied file
- Validate source matches destination
- Detect corruption immediately

### 4. Dry-Run Preview
- Show what would change before doing it
- File-by-file diff report
- User can review and abort

### 5. Atomic Operations
- Use temp directories + rename
- All-or-nothing file operations
- Rollback on any error

### 6. User Content Protection
- Hard-coded preservation rules
- Refuse to overwrite specs/
- Merge configs, never replace

### 7. Detailed Logging
- Progress indicators
- Error messages with remediation
- Upgrade summary report

---

## 🔧 Future-Proofing Strategy

### Config-Driven Ownership Model:
```yaml
# .praxis-os/config/upgrade-strategy.yaml (future)
ownership:
  framework_owned:
    - standards/universal/
    - workflows/
    - ouroboros/
    - scripts/
  
  user_owned:
    - specs/
    - standards/development/
  
  merge_strategy:
    config/mcp.yaml: preserve_user_customizations
    ../.gitignore: additive_merge

  ephemeral:
    - .cache/
    - workspace/
```

**Benefits:**
- Change ownership without code changes
- Project-specific preservation rules
- Self-documenting
- Extensible for plugins/extensions

---

## 🚨 Edge Cases & Error Handling

### Edge Case 1: Broken Installation
**Scenario:** User's `.praxis-os/ouroboros/` is corrupted

**Solution:**
- Detect missing critical files in pre-flight
- Offer `--force-reinstall` flag
- Backup user content, wipe rest, fresh install

### Edge Case 2: Config Schema Changes
**Scenario:** New mcp.yaml has incompatible structure

**Solution:**
- Version config schema
- Detect old schema version
- Run migration function
- Preserve user values in new structure

### Edge Case 3: Partial Upgrade Failure
**Scenario:** Phase 4 fails mid-upgrade

**Solution:**
- Atomic operations (use temp + rename)
- If error, restore from .bak files
- If --backup, offer automatic restore
- Indexes rebuild automatically on next start
- Log exact failure point for debugging

### Edge Case 4: Concurrent Upgrades
**Scenario:** Two upgrades run simultaneously

**Solution:**
- Create upgrade lock file (.praxis-os/.upgrade_lock)
- Check lock exists, abort if found
- Include PID in lock for stale detection
- Release lock at end (or on error)

### Edge Case 5: Source Unavailable
**Scenario:** GitHub down, can't clone

**Solution:**
- Allow `--source /local/path` flag
- Validate local source structure
- Use local clone if available
- Clear error message if unavailable

### Edge Case 6: Insufficient Disk Space
**Scenario:** Mid-upgrade, disk fills up

**Solution:**
- Pre-flight check: Calculate size WITHOUT .cache/indexes/
- Need ~500MB for backup (not 2GB+)
- Check again before each phase
- Abort early if space drops too low
- Clear error message with remediation

**Note:** By excluding indexes from backup, we reduce backup size from ~2GB to ~50MB, making disk space requirements much more reasonable.

---

## 🧪 Testing Strategy

### Unit Tests:
```python
test_validate_existing_installation()
test_create_backup()
test_upgrade_files_with_preservation()
test_merge_config_non_destructive()
test_checksum_validation()
test_ownership_model_enforcement()
```

### Integration Tests:
```python
test_full_upgrade_fresh_install()
test_upgrade_with_user_customizations()
test_upgrade_with_backup_and_restore()
test_dry_run_produces_report()
test_error_rollback_mechanism()
```

### Dogfooding:
1. Test on praxis-os itself (self-upgrade)
2. Test on python-sdk install
3. Test on hive-kube install (if any)
4. Test on fresh consumer project

---

## 📊 Success Metrics

### Upgrade Successful If:
1. ✅ All framework files updated to latest
2. ✅ User specs/customizations preserved
3. ✅ Config merged correctly
4. ✅ Dependencies updated
5. ✅ MCP server starts without errors
6. ✅ RAG search works post-upgrade
7. ✅ Exit code 0, no errors in log

### Upgrade Failed If:
- ❌ Any framework files missing
- ❌ Any user files lost
- ❌ Config corrupted
- ❌ MCP server won't start
- ❌ Exit code non-zero

---

## 📝 Open Questions for Discussion

### Question 1: Backup Default Behavior? ✅ DECIDED

**Decision:** Option A - Always backup (quality outcomes > speed)

**Rationale:**
- ✅ **praxis-os is about quality outcomes** - Safety first
- ✅ **Backup is fast now** - 5s with indexes excluded
- ✅ **Minimal cost** - 50MB disk space is negligible
- ✅ **Peace of mind** - Users can experiment fearlessly
- ✅ **Professional behavior** - Production tools always backup

**Implementation:**
```python
# Backup is MANDATORY, not optional
def upgrade(...):
    # No --backup flag needed, always happens
    backup_dir = create_backup(target)
    print(f"✓ Backup created: {backup_dir}")
    
    # Provide --skip-backup for advanced users (dangerous)
    if args.skip_backup:
        print("⚠️  WARNING: Skipping backup (--skip-backup)")
```

---

### Question 2: Config Migration Strategy? ✅ DECIDED

**Decision:** Hybrid - Script copies template, LLM reconciles

**Rationale:**
- ✅ **Config is already versioned** (in git, user can see changes)
- ✅ **LLM is project expert** - Knows user's customizations
- ✅ **LLM owns the file** - Better at semantic merge than code
- ✅ **Script handles mechanics** - Copy new template to safe location
- ✅ **Human oversight** - LLM proposes, user approves

**Implementation:**
```python
# Phase 4: Config Reconciliation
def prepare_config_reconciliation(source, target):
    """Script copies new config, LLM handles merge"""
    
    # 1. Copy new template to comparison location
    new_template = source / "dist/config/mcp.yaml"
    comparison_file = target / ".praxis-os/config/mcp.yaml.new"
    shutil.copy(new_template, comparison_file)
    
    # 2. Create reconciliation prompt for LLM
    prompt_file = target / ".praxis-os/config/CONFIG_RECONCILIATION_NEEDED.md"
    write_reconciliation_prompt(prompt_file)
    
    print("""
    ✓ New config template: .praxis-os/config/mcp.yaml.new
    ✓ Current config:      .praxis-os/config/mcp.yaml
    
    🤖 ACTION REQUIRED:
    An LLM (you) should now reconcile the configs:
    1. Review changes in mcp.yaml.new
    2. Merge relevant changes into mcp.yaml
    3. Preserve user customizations (source_paths, languages, etc.)
    4. Delete mcp.yaml.new when done
    5. Delete CONFIG_RECONCILIATION_NEEDED.md
    """)

def write_reconciliation_prompt(prompt_file):
    """Write a prompt for the LLM to handle config merge"""
    content = """
    # Config Reconciliation Required
    
    The upgrade script has placed a new config template at:
    `.praxis-os/config/mcp.yaml.new`
    
    Your current config is at:
    `.praxis-os/config/mcp.yaml`
    
    ## Your Task:
    1. Read both files
    2. Identify new fields/sections in mcp.yaml.new
    3. Merge new fields into mcp.yaml
    4. Preserve user customizations:
       - source_paths (user's project structure)
       - languages (user's language stack)
       - any other custom settings
    5. Delete mcp.yaml.new after merge
    6. Delete this prompt file
    
    ## Validation:
    - Ensure merged config is valid YAML
    - Test MCP server starts without errors
    - Verify RAG search works
    """
    prompt_file.write_text(content)
```

**Benefits:**
- ✅ Script handles mechanics (safe file operations)
- ✅ LLM handles semantics (intelligent merge)
- ✅ User has oversight (can review changes)
- ✅ Clear separation of concerns

---

### Question 3: Rollback Mechanism? ✅ DECIDED

**Decision:** Option A - Automatic restore from mandatory backup

**Rationale:**
- ✅ **Backup is mandatory** - Always have restore point
- ✅ **Defensive programming** - Reduce failure risk to near-zero
- ✅ **Graceful degradation** - If upgrade fails, restore and report
- ✅ **No user action needed** - Script handles recovery

**Implementation Strategy - Defense in Depth:**

```python
def upgrade_with_defenses(target):
    """Multi-layer defense to prevent failures"""
    
    # Layer 1: Pre-flight validation (catch issues early)
    try:
        validate_prerequisites()
        validate_installation()
        validate_disk_space()
        validate_git_available()
    except ValidationError as e:
        print(f"❌ Pre-flight check failed: {e}")
        print("   Fix the issue and try again")
        sys.exit(1)
    
    # Layer 2: Mandatory backup (safety net)
    backup_dir = create_backup(target)
    
    # Layer 3: Atomic operations (all-or-nothing)
    try:
        with atomic_operation():
            # Phase 3: Upgrade files
            upgrade_framework_files()
            verify_checksums()
            
            # Phase 4: Config prep (LLM handles merge)
            prepare_config_reconciliation()
            
            # Phase 5: Dependencies
            update_venv_dependencies()
            
    except UpgradeError as e:
        # Layer 4: Automatic rollback
        print(f"❌ Upgrade failed: {e}")
        print(f"🔄 Rolling back to backup: {backup_dir}")
        
        restore_from_backup(backup_dir, target)
        
        print("✓ Rollback complete, installation restored")
        print("   Please report this issue with the error above")
        sys.exit(1)
    
    # Success path
    print("✓ Upgrade complete!")
    print("   Backup kept at:", backup_dir)
    print("   Delete after 7 days if no issues")

class atomic_operation:
    """Context manager for atomic file operations"""
    def __enter__(self):
        self.temp_dir = create_temp_staging()
        return self.temp_dir
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            cleanup_temp_staging(self.temp_dir)
        else:
            commit_temp_to_target(self.temp_dir)
```

**Defense Layers:**
1. ✅ Pre-flight validation (prevent bad upgrades)
2. ✅ Mandatory backup (safety net)
3. ✅ Atomic operations (no partial state)
4. ✅ Automatic rollback (recover from failures)
5. ✅ Checksums (detect corruption)
6. ✅ Clear error messages (user can report issues)

---

### Question 4: Breaking Change Migration? ✅ DECIDED

**Decision:** Case-by-case basis, no generic migration system

**Rationale:**
- ✅ **Limited installs** - Migration burden is low
- ✅ **Breaking changes are rare** - Not worth complex system
- ✅ **Context-specific logic** - Each change needs different handling
- ✅ **Pre-flight detection** - Catch old installs, fail gracefully
- ❌ **No dynamic migration** - Too complex, error-prone

**Implementation Strategy:**

```python
# Pre-flight check detects breaking changes
def validate_installation(target):
    """Detect breaking changes and fail gracefully"""
    
    # Check 1: Detect mcp_server → ouroboros rename
    old_server = target / ".praxis-os/mcp_server"
    new_server = target / ".praxis-os/ouroboros"
    
    if old_server.exists() and not new_server.exists():
        print("""
        ❌ BREAKING CHANGE DETECTED: Old installation format
        
        Your installation uses the old 'mcp_server' directory.
        This has been renamed to 'ouroboros' in current versions.
        
        📋 MIGRATION REQUIRED:
        
        Option A: Fresh install (recommended)
        1. Backup your specs: cp -r .praxis-os/specs /tmp/my-specs
        2. Backup your config: cp .praxis-os/config/mcp.yaml /tmp/
        3. Remove old install: rm -rf .praxis-os
        4. Run install script: curl -sSL ... | python3 -
        5. Restore specs: cp -r /tmp/my-specs .praxis-os/specs
        6. Restore config: cp /tmp/mcp.yaml .praxis-os/config/
        
        Option B: Manual migration (advanced)
        1. Rename: mv .praxis-os/mcp_server .praxis-os/ouroboros
        2. Update .cursor/mcp.json: Change "ouroboros" module name
        3. Restart Cursor
        4. Run upgrade script again
        
        🔗 See: https://honeyhiveai.github.io/praxis-os/upgrading#breaking-changes
        """)
        sys.exit(1)
    
    # Future breaking changes would be detected here
    # Each gets specific error message with migration steps
```

**Benefits:**
- ✅ Clear error messages with remediation
- ✅ Links to documentation
- ✅ Multiple migration paths (fresh vs manual)
- ✅ No fragile generic migration logic
- ✅ Easy to maintain (add new checks as needed)

---

### Question 5: Documentation Strategy? ✅ DECIDED

**Decision:** Option C (docs + script + README, no video yet)

**Rationale:**
- ✅ **Comprehensive written docs** - Cover all scenarios
- ✅ **Script inline help** - `--help` flag
- ✅ **Main README mention** - Discoverability
- ⏳ **Video walkthrough** - Way in the future, low priority

**Documentation Plan:**
1. ✅ `docs/content/how-to-guides/upgrading.md` - Complete rewrite
2. ✅ `scripts/upgrade-praxis-os.py` - Docstrings + --help
3. ✅ `README.md` - Add upgrade section
4. ⏳ Video walkthrough - Future (not now)

---

### Question 6: Validation Depth? ✅ DECIDED

**Decision:** File-based validation only (script cannot control MCP restart)

**Rationale:**
- ✅ **Script limitation** - Cannot restart Cursor/MCP server
- ✅ **User-based final validation** - User restarts, tests tools
- ✅ **File validation is sufficient** - Checksums, imports, schema
- ✅ **Clear next steps** - Tell user what to test

**Implementation:**

```python
def validate_upgrade(target, stats):
    """File-based validation only"""
    
    print("\n" + "="*60)
    print("Validating upgrade...")
    print("="*60)
    
    # 1. File count validation
    print("✓ Framework files updated:", stats['standards'], "files")
    print("✓ Workflows updated:", stats['workflows'], "files")
    print("✓ Server code updated:", stats['ouroboros'], "files")
    
    # 2. Python import validation
    print("\n📦 Validating Python imports...")
    try:
        import_result = subprocess.run(
            [venv_python, "-c", "import ouroboros; print('OK')"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if import_result.returncode == 0:
            print("✓ Python imports valid")
        else:
            raise ValidationError(f"Import failed: {import_result.stderr}")
    except Exception as e:
        raise ValidationError(f"Python validation failed: {e}")
    
    # 3. Config schema validation
    print("\n⚙️  Validating config schema...")
    try:
        config = yaml.safe_load((target / ".praxis-os/config/mcp.yaml").read_text())
        validate_config_schema(config)
        print("✓ Config schema valid")
    except Exception as e:
        raise ValidationError(f"Config validation failed: {e}")
    
    # 4. File checksums
    print("\n🔐 Verifying file integrity...")
    verify_checksums(target)
    print("✓ All checksums valid")
    
    print("\n" + "="*60)
    print("✅ FILE VALIDATION COMPLETE")
    print("="*60)
    
    # User instructions for final validation
    print("""
    📋 NEXT STEPS - User Validation Required:
    
    1. ✅ Restart Cursor (or your IDE)
       - This reloads the upgraded MCP server
    
    2. ✅ Test MCP tools:
       - Run: "Search standards for race conditions"
       - Should return relevant results
    
    3. ✅ Test workflows:
       - Run: "List available workflows"
       - Should show: spec_creation_v1, spec_execution_v1, etc.
    
    4. ✅ Check for errors:
       - View MCP server logs (Cursor: Settings → MCP)
       - No error messages should appear
    
    5. ✅ Config reconciliation (if needed):
       - Check for: .praxis-os/config/mcp.yaml.new
       - If exists: Merge changes, delete .new file
    
    ⚠️  If any issues:
    - Restore from backup: mv {backup_dir} .praxis-os
    - Report issue with error message
    
    ✅ If all tests pass:
    - Upgrade successful!
    - Keep backup for 7 days, then delete
    """)
```

**Validation Scope:**
- ✅ File counts match expected
- ✅ Python imports work
- ✅ Config schema valid
- ✅ Checksums verified
- ✅ Clear user instructions for MCP testing
- ❌ NO MCP server restart (user does this)
- ❌ NO smoke tests (user validates tools work)

---

## 🎯 Next Steps

Once we settle these questions:

1. ✅ Finalize design decisions
2. ✅ Create formal spec via `spec_creation_v1` workflow
3. ✅ Implement via `spec_execution_v1` workflow
4. ✅ Test on real consumer projects
5. ✅ Update all documentation
6. ✅ Ship it! 🚀

---

## 📚 References

- `install-praxis-os.py` - Install script to reuse logic from
- `praxis_os_upgrade_v1` workflow - Conceptual structure (outdated paths)
- Upgrade docs - Current broken state
- Ownership model - From install script structure

---

**Ready to discuss these questions and finalize the design?** 🤔

