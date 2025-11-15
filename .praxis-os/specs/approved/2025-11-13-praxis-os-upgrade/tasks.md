# Implementation Tasks: praxis-os Upgrade System

**Spec ID:** 2025-11-13-praxis-os-upgrade  
**Status:** 🚧 In Review  
**Version:** 1.0.0  
**Last Updated:** 2025-11-13  
**Author:** AI Agent (Claude)

---

## 🎯 Implementation Overview

**Deliverable:** `scripts/upgrade-praxis-os.py` (~500-700 lines)  
**Estimated Time:** 12-16 hours  
**Phases:** 4 implementation phases  
**Total Tasks:** 23 tasks

---

## 📋 Phase Breakdown

### Phase 1: Core Infrastructure (4-5 hours, 7 tasks)
Build foundational components and data models

### Phase 2: Component Implementation (5-6 hours, 10 tasks)
Implement 8 components (validators, backup, upgrader, etc.)

### Phase 3: Integration & CLI (2-3 hours, 4 tasks)
Wire components together with orchestrator and CLI

### Phase 4: Testing & Documentation (1-2 hours, 2 tasks)
Write tests and update documentation

---

## 📊 Phase 1: Core Infrastructure

**Duration:** 4-5 hours  
**Objective:** Build foundational classes and utilities

---

### Task 1.1: Create Data Models

**File:** `scripts/upgrade-praxis-os.py` (models section)  
**Duration:** 30 minutes  
**Dependencies:** None  
**Priority:** P0

**Implementation:**
```python
@dataclass
class UpgradeReport:
    """Track file changes during upgrade"""
    files_added: List[str] = field(default_factory=list)
    files_modified: List[str] = field(default_factory=list)
    files_deleted: List[str] = field(default_factory=list)

@dataclass
class BackupManifest:
    """Checksum manifest for backup validation"""
    created_at: str
    backup_dir: str
    checksums: Dict[str, str]

@dataclass
class ValidationResult:
    """Result of validation checks"""
    passed: bool
    checks: List[CheckResult]

@dataclass
class CheckResult:
    """Individual check result"""
    passed: bool
    check_name: str
    message: str
```

**Acceptance Criteria:**
- [ ] All data models defined with type hints
- [ ] Methods implemented (summary(), to_json(), etc.)
- [ ] Docstrings added for each class
- [ ] Type checking passes (mypy)

**Testing:**
- Unit test: Instantiate each model
- Unit test: Serialize/deserialize (JSON)

**Traceability:** Specs section "Data Models"

---

### Task 1.2: Implement Utility Functions

**File:** `scripts/upgrade-praxis-os.py` (utils section)  
**Duration:** 45 minutes  
**Dependencies:** Task 1.1  
**Priority:** P0

**Implementation:**
```python
def sha256(file_path: Path) -> str:
    """Compute SHA256 checksum of file"""
    ...

def count_files(directory: Path, pattern: str = "*") -> int:
    """Count files matching pattern"""
    ...

def safe_copy(src: Path, dst: Path, base_dir: Path) -> None:
    """Copy file with path traversal prevention"""
    ...

def is_process_running(pid: int) -> bool:
    """Check if process is still running"""
    ...

def parse_version(version_str: str) -> tuple:
    """Parse version string into comparable tuple"""
    ...
```

**Acceptance Criteria:**
- [ ] All utility functions implemented
- [ ] Type hints on all functions
- [ ] Docstrings with examples
- [ ] Security checks (path traversal prevention)
- [ ] Error handling for edge cases

**Testing:**
- Unit test: sha256() matches known checksums
- Unit test: safe_copy() prevents path traversal
- Unit test: is_process_running() detects stale PIDs

**Traceability:** Specs sections "Security", "Component Specification"

---

### Task 1.3: Implement PreFlightValidator

**File:** `scripts/upgrade-praxis-os.py`  
**Duration:** 60 minutes  
**Dependencies:** Task 1.2  
**Priority:** P0

**Implementation:**
```python
class PreFlightValidator:
    def __init__(self, target: Path):
        self.target = target
    
    def validate_all(self) -> ValidationResult:
        """Run all pre-flight checks"""
        checks = [
            self.check_praxis_os_exists(),
            self.check_ouroboros_exists(),
            self.check_python_version(),
            self.check_git_available(),
            self.check_disk_space(),
            self.detect_breaking_changes(),
        ]
        return self._aggregate_results(checks)
    
    def check_praxis_os_exists(self) -> CheckResult:
        """Verify .praxis-os/ directory exists"""
        ...
    
    def detect_breaking_changes(self) -> CheckResult:
        """Detect mcp_server → ouroboros rename"""
        old_server = self.target / ".praxis-os/mcp_server"
        new_server = self.target / ".praxis-os/ouroboros"
        
        if old_server.exists() and not new_server.exists():
            return CheckResult.failure(
                "Breaking change detected: Old 'mcp_server' directory found.\n\n"
                "Migration required - see: https://..."
            )
        return CheckResult.success("No breaking changes detected")
```

**Acceptance Criteria:**
- [ ] All 6 pre-flight checks implemented
- [ ] Breaking change detection for mcp_server → ouroboros
- [ ] Clear error messages with remediation
- [ ] Disk space check calculates correct size (exclude .cache/)
- [ ] Returns ValidationResult with all check results

**Testing:**
- Unit test: check_praxis_os_exists() detects missing dir
- Unit test: detect_breaking_changes() finds old structure
- Unit test: check_disk_space() calculates correctly
- Integration test: validate_all() aggregates results

**Traceability:** FR-1.1 through FR-1.7

---

### Task 1.4: Implement BackupManager

**File:** `scripts/upgrade-praxis-os.py`  
**Duration:** 75 minutes  
**Dependencies:** Task 1.2  
**Priority:** P0

**Implementation:**
```python
class BackupManager:
    def __init__(self, target: Path):
        self.target = target
    
    def create_backup(self) -> Path:
        """Create timestamped backup excluding ephemeral data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.target / f".praxis-os.backup.{timestamp}"
        
        ignore_patterns = shutil.ignore_patterns(
            ".cache", "workspace", "venv", "__pycache__", "*.pyc", ".DS_Store"
        )
        
        shutil.copytree(
            self.target / ".praxis-os",
            backup_dir,
            ignore=ignore_patterns
        )
        
        manifest_path = self._generate_checksum_manifest(backup_dir)
        self._validate_backup(backup_dir, manifest_path)
        
        return backup_dir
    
    def restore_from_backup(self, backup_dir: Path) -> None:
        """Restore .praxis-os/ from backup (rollback)"""
        shutil.rmtree(self.target / ".praxis-os")
        shutil.copytree(backup_dir, self.target / ".praxis-os")
        self._validate_restore(self.target / ".praxis-os")
    
    def _generate_checksum_manifest(self, backup_dir: Path) -> Path:
        """Generate SHA256 checksums for all files"""
        ...
    
    def _validate_backup(self, backup_dir: Path, manifest_path: Path) -> None:
        """Verify backup integrity using checksums"""
        ...
```

**Acceptance Criteria:**
- [ ] create_backup() creates timestamped directory
- [ ] Excludes .cache/, workspace/, venv/, __pycache__/
- [ ] Generates checksum manifest (.backup_manifest.json)
- [ ] Validates backup integrity
- [ ] restore_from_backup() fully restores installation
- [ ] Backup completes in < 10 seconds
- [ ] Backup size < 100MB

**Testing:**
- Unit test: create_backup() excludes .cache/
- Unit test: Backup includes all essential files
- Unit test: Checksum manifest is valid JSON
- Unit test: restore_from_backup() restores all files
- Performance test: Backup time < 10s

**Traceability:** FR-2.1 through FR-2.8

---

### Task 1.5: Implement SourceCloner

**File:** `scripts/upgrade-praxis-os.py`  
**Duration:** 45 minutes  
**Dependencies:** Task 1.2  
**Priority:** P0

**Implementation:**
```python
class SourceCloner:
    DEFAULT_REPO_URL = "https://github.com/honeyhiveai/praxis-os.git"
    
    def __init__(self, source_url: str = DEFAULT_REPO_URL):
        self.source_url = source_url
        self.temp_dir: Optional[Path] = None
    
    def clone_or_load(self, local_source: Optional[Path] = None) -> Path:
        """Clone from GitHub or use local source"""
        if local_source:
            self._validate_local_source(local_source)
            return local_source
        else:
            return self._clone_from_github()
    
    def _clone_from_github(self) -> Path:
        """Clone latest from GitHub to temp directory"""
        self.temp_dir = Path(tempfile.mkdtemp(prefix="praxis-os-upgrade-"))
        subprocess.run(
            ["git", "clone", self.source_url, str(self.temp_dir)],
            check=True,
            capture_output=True,
            timeout=120  # 2 min timeout
        )
        self._validate_source_structure(self.temp_dir)
        return self.temp_dir
    
    def extract_version(self, source_dir: Path) -> str:
        """Extract version from source"""
        # Try pyproject.toml first, then __init__.py
        ...
    
    def cleanup(self) -> None:
        """Delete temp clone"""
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
```

**Acceptance Criteria:**
- [ ] Clones from GitHub to temp directory
- [ ] Supports --source flag for local path
- [ ] Validates source has dist/ structure
- [ ] Extracts version from pyproject.toml or __init__.py
- [ ] Cleanup deletes temp directory
- [ ] Clone completes in < 60 seconds
- [ ] Handles network errors gracefully

**Testing:**
- Unit test: _validate_local_source() checks structure
- Unit test: extract_version() parses version correctly
- Integration test: Clone from GitHub succeeds
- Integration test: --source uses local path

**Traceability:** FR-3.1 through FR-3.7

---

### Task 1.6: Implement FileUpgrader

**File:** `scripts/upgrade-praxis-os.py`  
**Duration:** 90 minutes  
**Dependencies:** Task 1.1, Task 1.2  
**Priority:** P0

**Implementation:**
```python
class FileUpgrader:
    FRAMEWORK_OWNED = [
        "standards/universal/",
        "workflows/",
        "ouroboros/",
        "scripts/",
    ]
    
    USER_OWNED = [
        "specs/",
        "standards/development/",
    ]
    
    def __init__(self, source: Path, target: Path):
        self.source = source
        self.target = target
        self.changes = UpgradeReport()
    
    def upgrade_framework_files(self) -> UpgradeReport:
        """Upgrade all framework-owned files"""
        self._upgrade_standards()
        self._upgrade_workflows()
        self._upgrade_ouroboros()
        self._upgrade_scripts()
        self._verify_checksums()
        return self.changes
    
    def _upgrade_standards(self) -> None:
        """Rsync dist/universal/standards/ → .praxis-os/standards/universal/"""
        src = self.source / "dist/universal/standards"
        dst = self.target / ".praxis-os/standards/universal"
        
        before_snapshot = self._snapshot_directory(dst)
        self._rsync(src, dst, delete=True)
        after_snapshot = self._snapshot_directory(dst)
        
        self.changes.add_diff("standards", before_snapshot, after_snapshot)
    
    def _rsync(self, src: Path, dst: Path, delete: bool = False) -> None:
        """Wrapper around rsync for file copying"""
        if delete:
            # Delete destination, copy fresh
            if dst.exists():
                shutil.rmtree(dst)
        shutil.copytree(src, dst, dirs_exist_ok=True)
    
    def _verify_checksums(self) -> None:
        """Verify all copied files match source"""
        ...
```

**Acceptance Criteria:**
- [ ] Upgrades standards/, workflows/, ouroboros/, scripts/
- [ ] Never touches specs/ or standards/development/
- [ ] Tracks added/modified/deleted files in UpgradeReport
- [ ] Verifies checksums after copy
- [ ] Completes in < 90 seconds
- [ ] Handles missing source directories gracefully

**Testing:**
- Unit test: _upgrade_standards() copies files correctly
- Unit test: USER_OWNED directories never modified
- Unit test: UpgradeReport tracks changes accurately
- Integration test: Full upgrade preserves user files

**Traceability:** FR-4.1 through FR-4.10

---

### Task 1.7: Implement ConfigReconciler

**File:** `scripts/upgrade-praxis-os.py`  
**Duration:** 60 minutes  
**Dependencies:** Task 1.2  
**Priority:** P0

**Implementation:**
```python
class ConfigReconciler:
    def __init__(self, source: Path, target: Path):
        self.source = source
        self.target = target
    
    def prepare_reconciliation(self) -> str:
        """Prepare config for LLM merge"""
        new_template = self.source / "dist/config/mcp.yaml"
        current_config = self.target / ".praxis-os/config/mcp.yaml"
        comparison_file = self.target / ".praxis-os/config/mcp.yaml.new"
        
        shutil.copy(new_template, comparison_file)
        
        if self._configs_identical(new_template, current_config):
            comparison_file.unlink()
            return "NO_CHANGES"
        
        self._create_reconciliation_prompt()
        self._display_instructions()
        
        return "RECONCILIATION_NEEDED"
    
    def merge_gitignore(self) -> None:
        """Additive merge of .gitignore patterns"""
        ...
    
    def _configs_identical(self, file1: Path, file2: Path) -> bool:
        """Check if configs are identical (ignoring whitespace/comments)"""
        ...
    
    def _create_reconciliation_prompt(self) -> None:
        """Create CONFIG_RECONCILIATION_NEEDED.md"""
        ...
```

**Acceptance Criteria:**
- [ ] Copies mcp.yaml template to .new file
- [ ] Detects if config changed (diff)
- [ ] Creates CONFIG_RECONCILIATION_NEEDED.md prompt
- [ ] Skips reconciliation if no changes
- [ ] Merges .gitignore additively
- [ ] Completes in < 15 seconds

**Testing:**
- Unit test: _configs_identical() detects changes
- Unit test: merge_gitignore() adds new patterns
- Unit test: Reconciliation skipped if identical
- Unit test: Prompt file created correctly

**Traceability:** FR-5.1 through FR-5.7, FR-6.1 through FR-6.6

---

## 📊 Phase 2: Component Implementation

**Duration:** 5-6 hours  
**Objective:** Complete remaining components

---

### Task 2.1: Implement DependencyUpdater

**File:** `scripts/upgrade-praxis-os.py`  
**Duration:** 45 minutes  
**Dependencies:** Task 1.2  
**Priority:** P0

**Implementation:**
```python
class DependencyUpdater:
    def __init__(self, target: Path, skip_deps: bool = False):
        self.target = target
        self.skip_deps = skip_deps
        self.venv_python = target / ".praxis-os/venv/bin/python"
    
    def update_dependencies(self) -> None:
        """Update Python dependencies in venv"""
        if self.skip_deps:
            print("⏩ Skipping dependency update (--skip-deps)")
            return
        
        requirements = self.target / ".praxis-os/ouroboros/requirements.txt"
        
        subprocess.run(
            [str(self.venv_python), "-m", "pip", "install", "--upgrade", "pip"],
            check=True
        )
        
        subprocess.run(
            [str(self.venv_python), "-m", "pip", "install", "--upgrade", "-r", str(requirements)],
            check=True
        )
        
        self._run_post_install_hooks()
        self._verify_imports()
```

**Acceptance Criteria:**
- [ ] Upgrades pip first
- [ ] Installs/upgrades requirements
- [ ] Runs post-install hooks (playwright)
- [ ] Verifies imports work
- [ ] Supports --skip-deps flag
- [ ] Completes in < 60 seconds

**Testing:**
- Unit test: _verify_imports() detects broken imports
- Integration test: Dependencies updated successfully

**Traceability:** FR-7.1 through FR-7.6

---

### Task 2.2: Implement UpgradeValidator

**File:** `scripts/upgrade-praxis-os.py`  
**Duration:** 60 minutes  
**Dependencies:** Task 1.1, Task 1.2  
**Priority:** P0

**Implementation:**
```python
class UpgradeValidator:
    def __init__(self, target: Path, changes: UpgradeReport):
        self.target = target
        self.changes = changes
    
    def validate_upgrade(self) -> ValidationResult:
        """Run all validation checks"""
        checks = [
            self._verify_file_counts(),
            self._test_python_imports(),
            self._validate_config_schema(),
            self._verify_checksums(),
        ]
        
        result = self._aggregate_results(checks)
        
        if result.passed:
            self._display_user_instructions()
        
        return result
```

**Acceptance Criteria:**
- [ ] All 4 validation checks implemented
- [ ] Displays user instructions for MCP testing
- [ ] Returns ValidationResult
- [ ] Completes in < 30 seconds

**Testing:**
- Unit test: Each check function
- Integration test: validate_upgrade() aggregates correctly

**Traceability:** FR-9.1 through FR-9.7

---

### Task 2.3: Implement UpgradeOrchestrator (Part 1: Structure)

**File:** `scripts/upgrade-praxis-os.py`  
**Duration:** 45 minutes  
**Dependencies:** All Phase 1 tasks  
**Priority:** P0

**Implementation:**
```python
class UpgradeOrchestrator:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.target = Path(args.target_dir).resolve()
        self.backup_dir: Optional[Path] = None
        self.source_cloner: Optional[SourceCloner] = None
    
    def run(self) -> int:
        """Main upgrade flow with rollback on error"""
        try:
            with self._upgrade_lock():
                return self._execute_upgrade()
        except Exception as e:
            return self._handle_error(e)
        finally:
            self._cleanup()
    
    def _execute_upgrade(self) -> int:
        """Execute 8-phase upgrade"""
        # Phase 0: Pre-flight
        # Phase 1: Backup
        # Phase 2: Clone
        # Phase 3: Upgrade files
        # Phase 4: Config
        # Phase 5: Dependencies
        # Phase 6: Index rebuild trigger
        # Phase 7: Validate
        # Phase 8: Cleanup
        ...
```

**Acceptance Criteria:**
- [ ] Class structure defined
- [ ] run() method with try/except/finally
- [ ] _upgrade_lock() context manager
- [ ] _execute_upgrade() stub
- [ ] _handle_error() with rollback

**Testing:**
- Unit test: _upgrade_lock() prevents concurrent upgrades

**Traceability:** FR-11, FR-14

---

### Task 2.4: Implement UpgradeOrchestrator (Part 2: Phases 0-2)

**File:** `scripts/upgrade-praxis-os.py`  
**Duration:** 30 minutes  
**Dependencies:** Task 2.3  
**Priority:** P0

**Implementation:**
```python
def _execute_upgrade(self) -> int:
    # Phase 0: Pre-flight
    print("\n" + "="*60)
    print("Phase 0: Pre-Flight Checks")
    print("="*60)
    validator = PreFlightValidator(self.target)
    result = validator.validate_all()
    if not result:
        print(f"❌ Pre-flight failed: {result.error_messages()}")
        return 1
    print("✓ All pre-flight checks passed\n")
    
    # Phase 1: Backup
    print("="*60)
    print("Phase 1: Creating Backup")
    print("="*60)
    backup_mgr = BackupManager(self.target)
    self.backup_dir = backup_mgr.create_backup()
    print(f"✓ Backup created: {self.backup_dir}\n")
    
    # Phase 2: Clone source
    print("="*60)
    print("Phase 2: Cloning Source")
    print("="*60)
    self.source_cloner = SourceCloner()
    source_dir = self.source_cloner.clone_or_load(self.args.source)
    old_version = "0.9.0"  # Extract from current install
    new_version = self.source_cloner.extract_version(source_dir)
    print(f"✓ Upgrading: {old_version} → {new_version}\n")
    
    return source_dir
```

**Acceptance Criteria:**
- [ ] Phase 0 runs pre-flight checks
- [ ] Phase 1 creates backup
- [ ] Phase 2 clones source
- [ ] Progress printed for each phase
- [ ] Versions displayed

**Testing:**
- Integration test: Phases 0-2 execute correctly

**Traceability:** FR-1, FR-2, FR-3

---

### Task 2.5: Implement UpgradeOrchestrator (Part 3: Phases 3-5)

**File:** `scripts/upgrade-praxis-os.py`  
**Duration:** 30 minutes  
**Dependencies:** Task 2.4  
**Priority:** P0

**Implementation:**
```python
# Phase 3: Upgrade files
print("="*60)
print("Phase 3: Upgrading Framework Files")
print("="*60)
upgrader = FileUpgrader(source_dir, self.target)
changes = upgrader.upgrade_framework_files()
print(f"✓ Files upgraded: {changes.summary()}\n")

# Phase 4: Config reconciliation
print("="*60)
print("Phase 4: Config Reconciliation")
print("="*60)
reconciler = ConfigReconciler(source_dir, self.target)
status = reconciler.prepare_reconciliation()
reconciler.merge_gitignore()
if status == "RECONCILIATION_NEEDED":
    print("⚠️  Config reconciliation required (see instructions)")
else:
    print("✓ Config unchanged, no reconciliation needed")
print()

# Phase 5: Dependencies
print("="*60)
print("Phase 5: Updating Dependencies")
print("="*60)
dep_updater = DependencyUpdater(self.target, self.args.skip_deps)
dep_updater.update_dependencies()
print("✓ Dependencies updated\n")
```

**Acceptance Criteria:**
- [ ] Phase 3 upgrades files
- [ ] Phase 4 prepares config
- [ ] Phase 5 updates dependencies
- [ ] Progress printed for each phase

**Testing:**
- Integration test: Phases 3-5 execute correctly

**Traceability:** FR-4, FR-5, FR-6, FR-7

---

### Task 2.6: Implement UpgradeOrchestrator (Part 4: Phases 6-8)

**File:** `scripts/upgrade-praxis-os.py`  
**Duration:** 30 minutes  
**Dependencies:** Task 2.5  
**Priority:** P0

**Implementation:**
```python
# Phase 6: Rebuild index trigger
print("="*60)
print("Phase 6: Scheduling Index Rebuild")
print("="*60)
(self.target / ".praxis-os/.rebuild_indexes").touch()
print("✓ Index rebuild scheduled (on next MCP start)\n")

# Phase 7: Validate
print("="*60)
print("Phase 7: Validating Upgrade")
print("="*60)
validator = UpgradeValidator(self.target, changes)
result = validator.validate_upgrade()
if not result:
    raise UpgradeError(f"Validation failed: {result.error_messages()}")
print("✓ Validation passed\n")

# Phase 8: Cleanup
print("="*60)
print("Phase 8: Cleanup")
print("="*60)
if self.source_cloner:
    self.source_cloner.cleanup()
self._archive_old_backups()
print("✓ Cleanup complete\n")

print("="*60)
print("✅ UPGRADE COMPLETE!")
print("="*60)
return 0
```

**Acceptance Criteria:**
- [ ] Phase 6 creates index rebuild flag
- [ ] Phase 7 validates upgrade
- [ ] Phase 8 cleans up temp files
- [ ] Success message printed

**Testing:**
- Integration test: Phases 6-8 execute correctly
- Integration test: Full upgrade succeeds

**Traceability:** FR-8, FR-9, FR-10

---

### Task 2.7: Implement Error Handling & Rollback

**File:** `scripts/upgrade-praxis-os.py`  
**Duration:** 45 minutes  
**Dependencies:** Task 2.6  
**Priority:** P0

**Implementation:**
```python
def _handle_error(self, error: Exception) -> int:
    """Handle upgrade failure with automatic rollback"""
    print(f"\n❌ UPGRADE FAILED: {error}")
    
    if self.backup_dir and self.backup_dir.exists():
        print(f"🔄 Rolling back to backup: {self.backup_dir}")
        
        try:
            backup_mgr = BackupManager(self.target)
            backup_mgr.restore_from_backup(self.backup_dir)
            
            print("✓ Rollback complete, installation restored")
            print("   Please report this issue with the error above")
        except Exception as rollback_error:
            print(f"❌ ROLLBACK FAILED: {rollback_error}")
            print(f"   Manual restore needed from: {self.backup_dir}")
    else:
        print("⚠️  No backup available for rollback")
        print("   Installation may be in inconsistent state")
    
    return 1

def _cleanup(self) -> None:
    """Cleanup temp files (runs always)"""
    if self.source_cloner:
        try:
            self.source_cloner.cleanup()
        except Exception:
            pass  # Best effort
```

**Acceptance Criteria:**
- [ ] Catches all exceptions
- [ ] Displays error message
- [ ] Triggers automatic rollback
- [ ] Handles rollback failure gracefully
- [ ] Cleanup runs even on error

**Testing:**
- Unit test: _handle_error() triggers rollback
- Integration test: Inject failure, verify rollback

**Traceability:** FR-11

---

### Task 2.8: Implement Dry-Run Mode

**File:** `scripts/upgrade-praxis-os.py`  
**Duration:** 30 minutes  
**Dependencies:** Task 2.6  
**Priority:** P1

**Implementation:**
```python
def run_dry_run(self) -> int:
    """Preview upgrade without modifications"""
    print("\n🔍 DRY-RUN MODE - No files will be modified\n")
    
    # Phase 0: Pre-flight (read-only)
    validator = PreFlightValidator(self.target)
    result = validator.validate_all()
    if not result:
        print(f"❌ Pre-flight would fail: {result.error_messages()}")
        return 1
    
    # Phase 2: Clone source (read-only)
    source_cloner = SourceCloner()
    source_dir = source_cloner.clone_or_load(self.args.source)
    
    # Simulate Phase 3: Show what would change
    print("Files that would be upgraded:")
    for framework_dir in FileUpgrader.FRAMEWORK_OWNED:
        src = source_dir / "dist" / framework_dir
        dst = self.target / ".praxis-os" / framework_dir
        # Diff and show
    
    print("\n✓ DRY-RUN COMPLETE (no changes made)")
    return 0
```

**Acceptance Criteria:**
- [ ] No files modified
- [ ] Shows what would change
- [ ] Displays disk space needed
- [ ] Runs pre-flight checks
- [ ] Exit code 0

**Testing:**
- Integration test: Dry-run makes no changes
- Integration test: Dry-run output accurate

**Traceability:** FR-12

---

### Task 2.9: Implement CLI Argument Parsing

**File:** `scripts/upgrade-praxis-os.py`  
**Duration:** 30 minutes  
**Dependencies:** None  
**Priority:** P0

**Implementation:**
```python
def parse_args() -> argparse.Namespace:
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="Upgrade praxis-os installation safely",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple upgrade
  python upgrade-praxis-os.py

  # Dry-run preview
  python upgrade-praxis-os.py --dry-run

  # From local source
  python upgrade-praxis-os.py --source /path/to/praxis-os
  
  # Custom target
  python upgrade-praxis-os.py /path/to/project
"""
    )
    
    parser.add_argument(
        "target_dir",
        nargs="?",
        default=".",
        help="Target directory (default: current)"
    )
    
    parser.add_argument("--source", type=Path, help="Local source directory")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes")
    parser.add_argument("--skip-backup", action="store_true", help="Skip backup (DANGEROUS)")
    parser.add_argument("--skip-deps", action="store_true", help="Skip dependency update")
    parser.add_argument("--keep-backups", type=int, default=3, help="Backups to keep")
    parser.add_argument("--quiet", action="store_true", help="Minimal output")
    
    return parser.parse_args()
```

**Acceptance Criteria:**
- [ ] All CLI flags defined
- [ ] Help text with examples
- [ ] Default values set
- [ ] Type conversions correct

**Testing:**
- Unit test: Parse valid arguments
- Unit test: --help displays correctly

**Traceability:** Specs section "API Specification"

---

### Task 2.10: Implement Main Entry Point

**File:** `scripts/upgrade-praxis-os.py`  
**Duration:** 15 minutes  
**Dependencies:** Task 2.9, Task 2.6  
**Priority:** P0

**Implementation:**
```python
def main() -> int:
    """Main entry point"""
    args = parse_args()
    
    orchestrator = UpgradeOrchestrator(args)
    
    if args.dry_run:
        return orchestrator.run_dry_run()
    else:
        return orchestrator.run()

if __name__ == "__main__":
    sys.exit(main())
```

**Acceptance Criteria:**
- [ ] Calls parse_args()
- [ ] Creates orchestrator
- [ ] Routes to dry-run or normal mode
- [ ] Returns exit code

**Testing:**
- Integration test: Script runs end-to-end

**Traceability:** All FRs

---

## 📊 Phase 3: Integration & CLI

**Duration:** 2-3 hours  
**Objective:** Wire everything together and polish UX

---

### Task 3.1: Implement Progress Indicators

**File:** `scripts/upgrade-praxis-os.py`  
**Duration:** 45 minutes  
**Dependencies:** Task 2.10  
**Priority:** P1

**Implementation:**
```python
class ProgressIndicator:
    """Show progress during long operations"""
    def __init__(self, quiet: bool = False):
        self.quiet = quiet
    
    def phase_start(self, phase: int, name: str) -> None:
        """Print phase header"""
        if not self.quiet:
            print(f"\n{'='*60}")
            print(f"Phase {phase}: {name}")
            print('='*60)
    
    def step(self, message: str) -> None:
        """Print step completion"""
        if not self.quiet:
            print(f"✓ {message}")
    
    def spinner(self, operation: str) -> ContextManager:
        """Show spinner for long operation"""
        # Implement simple spinner or use tqdm
        ...
```

**Acceptance Criteria:**
- [ ] Phase headers printed
- [ ] Step completions shown
- [ ] Spinner for long operations
- [ ] Respects --quiet flag

**Testing:**
- Manual test: Verify output looks good

**Traceability:** NFR-4.2

---

### Task 3.2: Add Colorized Output

**File:** `scripts/upgrade-praxis-os.py`  
**Duration:** 30 minutes  
**Dependencies:** Task 3.1  
**Priority:** P2

**Implementation:**
```python
class Colors:
    """ANSI color codes"""
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    
    @classmethod
    def success(cls, text: str) -> str:
        return f"{cls.GREEN}{text}{cls.RESET}"
    
    @classmethod
    def error(cls, text: str) -> str:
        return f"{cls.RED}{text}{cls.RESET}"
    
    @classmethod
    def warning(cls, text: str) -> str:
        return f"{cls.YELLOW}{text}{cls.RESET}"
```

**Acceptance Criteria:**
- [ ] Success messages in green
- [ ] Error messages in red
- [ ] Warnings in yellow
- [ ] Disables colors if not TTY

**Testing:**
- Manual test: Verify colors display correctly

**Traceability:** NFR-4.3

---

### Task 3.3: Add Upgrade Summary Report

**File:** `scripts/upgrade-praxis-os.py`  
**Duration:** 45 minutes  
**Dependencies:** Task 2.6  
**Priority:** P0

**Implementation:**
```python
def _generate_upgrade_summary(
    self,
    changes: UpgradeReport,
    old_version: str,
    new_version: str,
    duration: float
) -> str:
    """Generate upgrade summary report"""
    summary = f"""
═══════════════════════════════════════════════════════════════
✅ UPGRADE COMPLETE
═══════════════════════════════════════════════════════════════

Version:     {old_version} → {new_version}
Duration:    {duration:.1f} seconds
Backup:      {self.backup_dir}

Files Changed:
  Added:     {len(changes.files_added)}
  Modified:  {len(changes.files_modified)}
  Deleted:   {len(changes.files_deleted)}

Next Steps:
  1. Restart Cursor/IDE (reload MCP server)
  2. Test MCP tools work
  3. Config reconciliation (if needed)
  4. Keep backup for 7 days

═══════════════════════════════════════════════════════════════
"""
    return summary
```

**Acceptance Criteria:**
- [ ] Shows version change
- [ ] Shows duration
- [ ] Shows file change counts
- [ ] Shows backup location
- [ ] Shows next steps

**Testing:**
- Integration test: Summary generated correctly

**Traceability:** FR-10

---

### Task 3.4: Polish Error Messages

**File:** `scripts/upgrade-praxis-os.py`  
**Duration:** 60 minutes  
**Dependencies:** All components  
**Priority:** P0

**Implementation:**
- Review all error messages
- Ensure they follow "actionable with remediation" pattern
- Add links to documentation
- Add examples of fixes

**Acceptance Criteria:**
- [ ] All errors have clear messages
- [ ] All errors suggest remediation
- [ ] Breaking change errors link to docs
- [ ] Disk space errors show cleanup commands

**Testing:**
- Manual test: Trigger each error, verify message quality

**Traceability:** NFR-4.4

---

## 📊 Phase 4: Testing & Documentation

**Duration:** 1-2 hours  
**Objective:** Write tests and update docs

---

### Task 4.1: Write Unit Tests

**File:** `tests/test_upgrade_praxis_os.py`  
**Duration:** 60 minutes  
**Dependencies:** All Phase 2 tasks  
**Priority:** P0

**Test Coverage:**
```python
class TestPreFlightValidator:
    def test_detects_missing_praxis_os(self):
        ...
    
    def test_detects_breaking_changes(self):
        ...

class TestBackupManager:
    def test_creates_backup_excluding_cache(self):
        ...
    
    def test_restore_from_backup(self):
        ...

class TestFileUpgrader:
    def test_preserves_user_specs(self):
        ...
    
    def test_tracks_file_changes(self):
        ...

# ... more test classes
```

**Acceptance Criteria:**
- [ ] Unit tests for all components
- [ ] Test coverage > 80%
- [ ] All tests pass
- [ ] CI integration ready

**Testing:**
- Run: `pytest tests/test_upgrade_praxis_os.py`

**Traceability:** NFR-3.5

---

### Task 4.2: Update Documentation

**File:** `docs/content/how-to-guides/upgrading.md`  
**Duration:** 45 minutes  
**Dependencies:** Task 2.10  
**Priority:** P0

**Content:**
- Complete rewrite of upgrading.md
- Usage examples
- Common issues & troubleshooting
- Breaking change migration guide
- FAQ

**Acceptance Criteria:**
- [ ] upgrading.md completely rewritten
- [ ] Examples for all CLI flags
- [ ] Breaking change section complete
- [ ] Links to upgrade script
- [ ] README.md mentions upgrade

**Testing:**
- Manual review: Documentation is clear

**Traceability:** Specs section "Documentation Strategy"

---

## 🚦 Validation Gates

### Phase 1 Gate: Core Infrastructure Complete

**Criteria:**
- [ ] All 7 data models and components implemented
- [ ] Type hints on all functions
- [ ] Docstrings on all classes/methods
- [ ] Security checks in place (path traversal)
- [ ] Unit tests passing for each component

**Evidence:**
- mypy passes with no errors
- pytest shows all Phase 1 tests passing
- Manual review of component implementations

---

### Phase 2 Gate: Component Implementation Complete

**Criteria:**
- [ ] All 10 tasks completed
- [ ] UpgradeOrchestrator wires all components
- [ ] CLI arguments parsed correctly
- [ ] Dry-run mode works
- [ ] Error handling with rollback implemented

**Evidence:**
- Integration test: Full upgrade succeeds
- Integration test: Rollback works on error
- Integration test: Dry-run shows accurate preview

---

### Phase 3 Gate: Integration Complete

**Criteria:**
- [ ] Progress indicators working
- [ ] Colors display correctly
- [ ] Upgrade summary generated
- [ ] Error messages polished
- [ ] UX feels professional

**Evidence:**
- Manual test: Run upgrade, verify output
- Manual test: Trigger errors, verify messages
- User feedback: "This feels reliable"

---

### Phase 4 Gate: Testing & Documentation Complete

**Criteria:**
- [ ] Unit test coverage > 80%
- [ ] All tests passing
- [ ] upgrading.md rewritten
- [ ] README.md updated
- [ ] Ready to ship

**Evidence:**
- pytest --cov shows > 80%
- Documentation review complete
- Dogfooding: Upgrade praxis-os itself successfully

---

## 📊 Dependencies Map

```
Phase 1: Core Infrastructure
├── Task 1.1 (Data Models) ── [No deps]
├── Task 1.2 (Utils) ── depends on ── 1.1
├── Task 1.3 (PreFlightValidator) ── depends on ── 1.2
├── Task 1.4 (BackupManager) ── depends on ── 1.2
├── Task 1.5 (SourceCloner) ── depends on ── 1.2
├── Task 1.6 (FileUpgrader) ── depends on ── 1.1, 1.2
└── Task 1.7 (ConfigReconciler) ── depends on ── 1.2

Phase 2: Component Implementation
├── Task 2.1 (DependencyUpdater) ── depends on ── 1.2
├── Task 2.2 (UpgradeValidator) ── depends on ── 1.1, 1.2
├── Task 2.3 (Orchestrator Part 1) ── depends on ── All Phase 1
├── Task 2.4 (Orchestrator Part 2) ── depends on ── 2.3
├── Task 2.5 (Orchestrator Part 3) ── depends on ── 2.4
├── Task 2.6 (Orchestrator Part 4) ── depends on ── 2.5
├── Task 2.7 (Error Handling) ── depends on ── 2.6
├── Task 2.8 (Dry-Run) ── depends on ── 2.6
├── Task 2.9 (CLI) ── depends on ── [No deps]
└── Task 2.10 (Main) ── depends on ── 2.9, 2.6

Phase 3: Integration & CLI
├── Task 3.1 (Progress) ── depends on ── 2.10
├── Task 3.2 (Colors) ── depends on ── 3.1
├── Task 3.3 (Summary) ── depends on ── 2.6
└── Task 3.4 (Error Polish) ── depends on ── All components

Phase 4: Testing & Documentation
├── Task 4.1 (Tests) ── depends on ── All Phase 2
└── Task 4.2 (Docs) ── depends on ── 2.10
```

---

## ⏱️ Time Estimates Summary

| Phase | Duration | Tasks |
|-------|----------|-------|
| Phase 1: Core Infrastructure | 4-5 hours | 7 |
| Phase 2: Component Implementation | 5-6 hours | 10 |
| Phase 3: Integration & CLI | 2-3 hours | 4 |
| Phase 4: Testing & Documentation | 1-2 hours | 2 |
| **TOTAL** | **12-16 hours** | **23** |

---

## 🔄 Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-11-13 | AI Agent (Claude) | Initial task breakdown |

---

**Next Phase:** Implementation (via spec_execution_v1 workflow)

