# Implementation Guide: praxis-os Upgrade System

**Spec ID:** 2025-11-13-praxis-os-upgrade  
**Status:** 🚧 In Review  
**Version:** 1.0.0  
**Last Updated:** 2025-11-13  
**Author:** AI Agent (Claude)

---

## 🎯 Implementation Overview

**Deliverable:** `scripts/upgrade-praxis-os.py`  
**Language:** Python 3.9+  
**Estimated Lines:** 500-700 lines  
**Estimated Time:** 12-16 hours

---

## 📋 Code Organization

### File Structure

```
scripts/
└── upgrade-praxis-os.py          # Single-file implementation
    ├── imports
    ├── data models (dataclasses)
    ├── utility functions
    ├── component classes
    │   ├── PreFlightValidator
    │   ├── BackupManager
    │   ├── SourceCloner
    │   ├── FileUpgrader
    │   ├── ConfigReconciler
    │   ├── DependencyUpdater
    │   ├── UpgradeValidator
    │   └── UpgradeOrchestrator
    ├── CLI argument parsing
    └── main() entry point
```

---

## 🎨 Code Patterns & Best Practices

### Pattern 1: Component-Based Design

**DO THIS:**
```python
class BackupManager:
    """Single responsibility: Manage backups"""
    def __init__(self, target: Path):
        self.target = target
    
    def create_backup(self) -> Path:
        """One method, one purpose"""
        ...
```

**NOT THIS:**
```python
def do_everything(target, source, args):
    """❌ God function that does backup + upgrade + validate"""
    ...
```

**Rationale:** Component-based design enables unit testing, reusability, and maintainability.

---

### Pattern 2: Explicit Error Handling

**DO THIS:**
```python
def check_disk_space(self) -> CheckResult:
    """Return explicit success/failure"""
    available = get_disk_space(self.target)
    required = 500_000_000  # 500MB
    
    if available < required:
        return CheckResult.failure(
            f"Insufficient disk space: {available / 1e6:.0f}MB available, "
            f"need {required / 1e6:.0f}MB.\n\n"
            "Free up space:\n"
            "  - Delete old backups: rm -rf .praxis-os.backup.*\n"
            "  - Clear cache: rm -rf .praxis-os/.cache/"
        )
    
    return CheckResult.success(f"Disk space OK: {available / 1e6:.0f}MB available")
```

**NOT THIS:**
```python
def check_disk_space(self):
    """❌ Vague error handling"""
    if get_disk_space() < 500_000_000:
        raise Exception("Not enough space")  # No remediation
```

**Rationale:** Clear error messages with remediation steps reduce support burden.

---

### Pattern 3: Dataclasses for Structured Data

**DO THIS:**
```python
@dataclass
class UpgradeReport:
    """Type-safe, self-documenting data"""
    files_added: List[str] = field(default_factory=list)
    files_modified: List[str] = field(default_factory=list)
    files_deleted: List[str] = field(default_factory=list)
    
    def summary(self) -> str:
        return f"+{len(self.files_added)} ~{len(self.files_modified)} -{len(self.files_deleted)}"
```

**NOT THIS:**
```python
changes = {  # ❌ Untyped dictionary
    "added": [],
    "modified": [],
    "deleted": []
}
```

**Rationale:** Dataclasses provide type safety, auto-generated `__init__`, and IDE autocomplete.

---

### Pattern 4: Context Managers for Resources

**DO THIS:**
```python
@contextmanager
def _upgrade_lock(self):
    """Prevent concurrent upgrades"""
    lock_file = self.target / ".praxis-os/.upgrade_lock"
    
    if lock_file.exists():
        pid = int(lock_file.read_text().strip())
        if self._is_process_running(pid):
            raise UpgradeError(f"Another upgrade is running (PID {pid})")
        else:
            lock_file.unlink()  # Stale lock
    
    lock_file.write_text(str(os.getpid()))
    try:
        yield
    finally:
        lock_file.unlink()  # Always release
```

**NOT THIS:**
```python
def create_lock():
    ...  # ❌ Manual lock management (easy to forget cleanup)

def release_lock():
    ...
```

**Rationale:** Context managers ensure cleanup happens even on exceptions.

---

### Pattern 5: Type Hints Everywhere

**DO THIS:**
```python
def sha256(file_path: Path) -> str:
    """Compute SHA256 checksum"""
    hasher = hashlib.sha256()
    with file_path.open('rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()
```

**NOT THIS:**
```python
def sha256(file_path):  # ❌ No type hints
    ...
```

**Rationale:** Type hints enable mypy checking, IDE autocomplete, and self-documentation.

---

### Pattern 6: Security-First Path Operations

**DO THIS:**
```python
def safe_copy(src: Path, dst: Path, base_dir: Path) -> None:
    """Copy with path traversal prevention"""
    resolved_dst = dst.resolve()
    if not resolved_dst.is_relative_to(base_dir):
        raise SecurityError(f"Path traversal detected: {dst}")
    shutil.copy(src, dst)
```

**NOT THIS:**
```python
def copy_file(src, dst):
    shutil.copy(src, dst)  # ❌ No validation
```

**Rationale:** Prevents malicious source from writing outside `.praxis-os/`.

---

## 🧪 Testing Strategy

### Unit Testing

**Approach:** Test each component in isolation with mocked dependencies.

**Example:**
```python
def test_backup_manager_excludes_cache(tmp_path):
    # Setup: Create test .praxis-os/ with .cache/
    (tmp_path / ".praxis-os/.cache").mkdir(parents=True)
    (tmp_path / ".praxis-os/ouroboros").mkdir(parents=True)
    (tmp_path / ".praxis-os/.cache/indexes/big.db").write_text("2GB")
    (tmp_path / ".praxis-os/ouroboros/server.py").write_text("code")
    
    # Execute: Create backup
    backup_mgr = BackupManager(tmp_path)
    backup_dir = backup_mgr.create_backup()
    
    # Verify: .cache/ excluded, ouroboros/ included
    assert not (backup_dir / ".cache").exists()
    assert (backup_dir / "ouroboros").exists()
    assert (backup_dir / "ouroboros/server.py").exists()
```

**Coverage Target:** > 80%

---

### Integration Testing

**Approach:** Test full upgrade flow with real file operations.

**Example:**
```python
def test_full_upgrade_from_fresh_install(tmp_path):
    # Setup: Run install-praxis-os.py
    run_install_script(tmp_path)
    
    # Add user content
    (tmp_path / ".praxis-os/specs/my-spec.md").write_text("User's spec")
    
    # Execute: Run upgrade-praxis-os.py
    result = subprocess.run(
        ["python", "scripts/upgrade-praxis-os.py", str(tmp_path)],
        capture_output=True,
        text=True
    )
    
    # Verify
    assert result.returncode == 0
    assert "UPGRADE COMPLETE" in result.stdout
    assert (tmp_path / ".praxis-os/specs/my-spec.md").exists()  # Preserved
    assert (tmp_path / ".praxis-os.backup." in os.listdir(tmp_path))  # Backup created
```

---

### Property-Based Testing

**Approach:** Test invariants across many random scenarios.

**Example:**
```python
from hypothesis import given, strategies as st

@given(st.lists(st.text(min_size=1), min_size=1, max_size=50))
def test_backup_restore_is_lossless(tmp_path, file_list):
    # Setup: Create random files
    for filename in file_list:
        (tmp_path / ".praxis-os" / filename).write_text(f"content-{filename}")
    
    # Backup + Wipe + Restore
    backup_mgr = BackupManager(tmp_path)
    backup_dir = backup_mgr.create_backup()
    shutil.rmtree(tmp_path / ".praxis-os")
    backup_mgr.restore_from_backup(backup_dir)
    
    # Verify: All files restored with same content
    for filename in file_list:
        assert (tmp_path / ".praxis-os" / filename).exists()
        assert (tmp_path / ".praxis-os" / filename).read_text() == f"content-{filename}"
```

---

### Manual Testing (Dogfooding)

**Checklist:**
1. ✅ Upgrade praxis-os itself (self-upgrade)
2. ✅ Upgrade python-sdk installation
3. ✅ Upgrade fresh consumer project
4. ✅ Inject failure at each phase, verify rollback
5. ✅ Test --dry-run mode
6. ✅ Test --source flag with local path
7. ✅ Test concurrent upgrade prevention
8. ✅ Test breaking change detection

---

## 🚀 Deployment Guidance

### Pre-Deployment Checklist

- [ ] All unit tests pass (`pytest tests/`)
- [ ] mypy type checking passes (`mypy scripts/upgrade-praxis-os.py`)
- [ ] Integration tests pass
- [ ] Manual dogfooding completed (self-upgrade successful)
- [ ] Documentation updated (`docs/content/how-to-guides/upgrading.md`)
- [ ] README.md mentions upgrade
- [ ] Breaking change migration guide written

---

### Deployment Steps

**Step 1: Merge to main**
```bash
git checkout -b feat/upgrade-system
git add scripts/upgrade-praxis-os.py
git add docs/content/how-to-guides/upgrading.md
git add README.md
git commit -m "feat: Add upgrade-praxis-os.py script

- Implements 8-phase upgrade with automatic rollback
- Mandatory backup (excluding indexes - 50MB, 5s)
- Preserves user specs and customizations
- Breaking change detection (mcp_server → ouroboros)
- CLI with --dry-run, --source, --skip-deps flags
- Comprehensive error messages with remediation
- Self-tested via dogfooding

Closes #XXX"
git push origin feat/upgrade-system
```

**Step 2: PR Review**
- Code review by at least one maintainer
- Test on reviewer's local praxis-os install
- Verify documentation is clear

**Step 3: Merge & Tag**
```bash
git checkout main
git merge feat/upgrade-system
git tag v1.0.0 -m "Release v1.0.0 with upgrade system"
git push origin main --tags
```

**Step 4: Announce**
- Post in project channels (Slack, Discord, etc.)
- Update CHANGELOG.md
- Link to upgrading.md in announcement

---

### Rollback Procedure (If Issues Found)

**If upgrade script has critical bug:**

```bash
# Option 1: Hotfix
git checkout -b hotfix/upgrade-script-fix
# Fix bug
git commit -m "fix: Correct upgrade script issue"
git push origin hotfix/upgrade-script-fix
# Merge via emergency PR

# Option 2: Revert
git revert <commit-hash>
git push origin main

# Option 3: User manual restore (if script broken)
# Users restore from backup:
mv .praxis-os.backup.YYYYMMDD_HHMMSS .praxis-os
```

---

## 🛠️ Troubleshooting Guide

### Issue 1: "Pre-flight check failed: mcp_server directory found"

**Symptom:**
```
❌ Pre-flight check failed:
Breaking change detected: Old 'mcp_server' directory found.
```

**Cause:** User's installation uses old directory structure before ouroboros rename.

**Solution:**
```bash
# Option A: Fresh install (recommended)
cp -r .praxis-os/specs /tmp/my-specs
cp .praxis-os/config/mcp.yaml /tmp/
rm -rf .praxis-os
curl -sSL https://raw.githubusercontent.com/honeyhiveai/praxis-os/main/scripts/install-praxis-os.py | python3 -
cp -r /tmp/my-specs .praxis-os/specs
cp /tmp/mcp.yaml .praxis-os/config/

# Option B: Manual migration (advanced)
mv .praxis-os/mcp_server .praxis-os/ouroboros
# Update .cursor/mcp.json: Change module name to "ouroboros"
# Restart Cursor
python scripts/upgrade-praxis-os.py
```

---

### Issue 2: "Insufficient disk space"

**Symptom:**
```
❌ Pre-flight check failed:
Insufficient disk space: 200MB available, need 500MB.
```

**Cause:** Not enough disk space for backup.

**Solution:**
```bash
# Delete old backups
rm -rf .praxis-os.backup.*

# Clear RAG cache (will rebuild on next query)
rm -rf .praxis-os/.cache/

# Remove old virtualenv (will rebuild during upgrade)
rm -rf .praxis-os/venv/

# Check space
df -h .
```

---

### Issue 3: Upgrade fails mid-process

**Symptom:**
```
❌ UPGRADE FAILED: FileNotFoundError: ...
🔄 Rolling back to backup: .praxis-os.backup.20251113_140530
✓ Rollback complete, installation restored
```

**Cause:** Unexpected error during upgrade (network issue, permission problem, etc.)

**Solution:**
1. ✅ Rollback already completed automatically
2. Check error message for root cause
3. Fix root cause (internet, permissions, disk space)
4. Run upgrade again

**If rollback failed:**
```bash
# Manual restore
mv .praxis-os.backup.YYYYMMDD_HHMMSS .praxis-os
# Restart Cursor
```

---

### Issue 4: Config reconciliation prompt appears but I don't see it

**Symptom:**
Upgrade completes but MCP server errors due to old config.

**Cause:** `CONFIG_RECONCILIATION_NEEDED.md` exists but user didn't see it.

**Solution:**
```bash
# Check for reconciliation prompt
ls .praxis-os/config/CONFIG_RECONCILIATION_NEEDED.md

# If exists, read it
cat .praxis-os/config/CONFIG_RECONCILIATION_NEEDED.md

# Manually reconcile
diff .praxis-os/config/mcp.yaml .praxis-os/config/mcp.yaml.new

# Use LLM to help merge
# In Cursor: "Reconcile .praxis-os/config/mcp.yaml with mcp.yaml.new"

# After merge, cleanup
rm .praxis-os/config/mcp.yaml.new
rm .praxis-os/config/CONFIG_RECONCILIATION_NEEDED.md
```

---

### Issue 5: Import errors after upgrade

**Symptom:**
```
ModuleNotFoundError: No module named 'ouroboros'
```

**Cause:** Virtual environment not updated or corrupted.

**Solution:**
```bash
# Rebuild virtualenv
rm -rf .praxis-os/venv
python3 -m venv .praxis-os/venv
source .praxis-os/venv/bin/activate
pip install -r .praxis-os/ouroboros/requirements.txt

# Restart Cursor
```

---

### Issue 6: RAG search not working after upgrade

**Symptom:**
MCP tools return "No results" or error.

**Cause:** Indexes need rebuilding.

**Solution:**
```bash
# Check if rebuild flag exists
ls .praxis-os/.rebuild_indexes

# If yes, restart Cursor (triggers rebuild)
# If no, manually rebuild
source .praxis-os/venv/bin/activate
python .praxis-os/scripts/build_rag_index.py

# Restart Cursor
```

---

### Issue 7: Concurrent upgrade error

**Symptom:**
```
❌ Pre-flight check failed:
Another upgrade is running (PID 12345)
```

**Cause:** Previous upgrade still running or stale lock file.

**Solution:**
```bash
# Check if process still running
ps aux | grep 12345

# If not running (stale lock):
rm .praxis-os/.upgrade_lock

# Try upgrade again
python scripts/upgrade-praxis-os.py
```

---

## 📊 Performance Optimization

### Optimization 1: Backup Excludes Indexes

**Why:** RAG indexes can be 2GB+, taking 2-3 minutes to copy.

**How:** Use `shutil.ignore_patterns()` to exclude `.cache/`, `workspace/`, `venv/`.

**Impact:**
- Backup size: 2GB+ → 50MB (40x smaller)
- Backup time: 2-3 min → 5s (24x faster)
- Disk space: 4GB+ → 500MB (8x less)

---

### Optimization 2: Rsync for Efficient Copying

**Why:** Only copy changed files.

**How:** Use `--delete` flag for clean sync, rsync checks timestamps/checksums.

**Impact:**
- File copy time: 3-5 min → 60s (typical)

---

### Optimization 3: Parallel Dependency Installation

**Why:** pip downloads can be slow.

**How:** pip automatically parallelizes downloads.

**Impact:**
- Dependency update: 2-3 min → 45s (typical)

---

## 🔍 Code Quality Checks

### Pre-Commit Checklist

```bash
# Type checking
mypy scripts/upgrade-praxis-os.py

# Linting
pylint scripts/upgrade-praxis-os.py

# Code formatting
black scripts/upgrade-praxis-os.py

# Unit tests
pytest tests/test_upgrade_praxis_os.py

# Integration tests
pytest tests/integration/test_upgrade_flow.py

# Test coverage
pytest --cov=scripts --cov-report=html
# Open htmlcov/index.html, verify > 80%
```

---

## 📚 References

- **SRD:** `srd.md` - Requirements
- **Specs:** `specs.md` - Technical design
- **Tasks:** `tasks.md` - Implementation breakdown
- **Testing:** `testing/` - Comprehensive test plans
- **Install Script:** `scripts/install-praxis-os.py` - Code to reuse

---

## 🔄 Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-11-13 | AI Agent (Claude) | Initial implementation guide |

---

**Next Steps:** Review comprehensive test plans in `testing/` directory.

