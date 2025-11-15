# prAxIs OS Upgrade Script Safety Improvements

**Date:** 2025-11-15  
**Author:** Claude (Sonnet 4.5) + Josh Paul  
**Status:** Phase 1 - Conversational Design  
**Category:** Infrastructure / Tooling

---

## Executive Summary

The prAxIs OS upgrade script (`upgrade-praxis-os.py`) has critical safety issues that can result in **cognitive substrate loss** during upgrade failures. This design document analyzes the current implementation, identifies bugs, and proposes comprehensive safety improvements to protect the accumulated intelligence of the project.

**Core Insight:**
The user data (workspace, specs, standards) **IS** the cognitive substrate. This is the accumulated intelligence that makes the AI agent effective. Losing this data is not just "file loss" - it's **lobotomy for the AI agent**.

**Key Issues Identified:**
1. **Delete flag (root cause)** - `delete=True` + `shutil.rmtree()` nukes entire directories before copy, causing data loss
2. **Nuclear restore** - Restore deletes entire `.praxis-os/` (including venv) instead of selective restoration
3. **Workspace excluded from backup** - Active reasoning (design docs, analysis) not backed up
4. **Scripts self-upgrade** - Upgrade script modifies itself while running
5. **No backup pruning** - Old backups accumulate indefinitely
6. **No verify mode** - User can't preview changes before upgrade
7. **Requirements.txt not reinstalled** - Venv becomes stale after upgrade

**Business Impact:**
- **Cognitive Substrate Loss:** 265+ markdown files (9.6MB) of accumulated intelligence lost on upgrade failure
- **Service Downtime:** MCP server fails to start after rollback (stale/missing venv)
- **User Trust:** Upgrade failures destroy project expertise, eroding confidence in prAxIs OS
- **Disk Bloat:** Backups accumulate without pruning (500MB+ over time)

---

## Problem Statement

### Current State

**Upgrade Script Flow (8 Phases):**
1. Pre-Flight Checks - Validate installation
2. **Backup** - Create timestamped backup (with exclusions)
3. Clone Source - Get latest prAxIs OS code
4. **Upgrade Files** - DELETE then COPY framework files
5. Config Reconciliation - Stage new config for review
6. Dependencies - Update requirements.txt
7. Rebuild Index - Schedule RAG index rebuild
8. Validation - Verify upgrade success

**Ownership Model:**

| Directory | Owner | Upgrade Action | Backup? | Restore? |
|-----------|-------|----------------|---------|----------|
| `ouroboros/` | Framework | **Overwrite** (dirs_exist_ok) | ✅ YES | ✅ YES |
| `workflows/` | Framework | **Overwrite** (dirs_exist_ok) | ✅ YES | ✅ YES |
| `standards/universal/` | Framework | **Overwrite** (dirs_exist_ok) | ✅ YES | ✅ YES |
| `workspace/` | User | **NEVER TOUCH** | ✅ YES | ✅ YES |
| `specs/` | User | **NEVER TOUCH** | ✅ YES | ✅ YES |
| `standards/project/` | User | **NEVER TOUCH** | ✅ YES | ✅ YES |
| `standards/development/` | User | **NEVER TOUCH** | ✅ YES | ✅ YES |
| `config/mcp.yaml` | User | **STAGE NEW** (reconcile) | ✅ YES | ✅ YES |
| `scripts/` | Framework | **NEVER TOUCH** (avoid self-mod) | ✅ YES | ✅ YES |
| `venv/` | System | **UPDATE DEPS** (pip install) | ❌ NO | ❌ NO |
| `.cache/` | System | **NEVER TOUCH** (ephemeral) | ❌ NO | ❌ NO |
| `state/` | Runtime | **NEVER TOUCH** (sessions) | ❌ NO | ❌ NO |

**Critical Bugs:**

#### Bug 1: Delete Flag (Root Cause)

**Location:** `FileUpgrader._rsync()` (lines 1728-1734)

```python
def _rsync(self, src: Path, dst: Path, delete: bool = False) -> None:
    # ...
    if delete and dst.exists():
        shutil.rmtree(dst)  # ← BUG: Nukes entire directory FIRST
    
    shutil.copytree(src, dst, ...)  # ← Copies SECOND
```

**Impact:**
- Deletes entire destination directory before verifying source exists
- If source missing or copy fails, destination is **gone forever**
- Used in `_upgrade_ouroboros()`, `_upgrade_standards()`, `_upgrade_workflows()`
- **Data loss risk:** Framework files deleted, then copy fails → no rollback possible

**Why This Exists:**
- Flawed reasoning: "Replace" = "Delete then copy"
- **Reality:** `shutil.copytree(dirs_exist_ok=True)` already replaces files safely
- Delete flag is unnecessary and dangerous

**Root Cause:**
The delete flag is the architectural flaw that enables all other bugs. Remove it entirely.

#### Bug 2: Nuclear Restore

**Location:** `BackupManager.restore_from_backup()` (lines 1017-1022)

```python
if target_dir.exists():
    shutil.rmtree(target_dir)  # ← BUG: NUKES ENTIRE .praxis-os/
shutil.copytree(backup_dir, target_dir)  # ← Restores backup
```

**Impact:**
- Deletes **ENTIRE** `.praxis-os/` directory (including venv, .cache, state)
- Restores backup (which has no venv, .cache, state)
- **MCP server fails to start:** No venv, no indexes

**Why This Exists:**
- Assumption: "Restore" = "Delete everything, copy backup"
- **Reality:** Restore should be **selective** - only restore backed-up directories
- Venv, .cache, state are out of scope for backup/restore

**Root Cause:**
Same flawed "delete then copy" pattern as Bug #1.

#### Bug 3: Workspace Excluded from Backup

**Location:** `BackupManager.create_backup()` (lines 959-971)

```python
ignore_patterns = shutil.ignore_patterns(
    ".cache",
    "workspace",  # ← BUG: Cognitive substrate excluded
    "venv",
    "__pycache__",
    "*.pyc",
    ".DS_Store",
    "state",
    ".backups",
)
```

**Impact:**
- Workspace contains 265+ markdown files (9.6MB) of accumulated intelligence
- Design docs, analysis, investigations, discovered patterns
- **On rollback:** Backup doesn't have workspace → **cognitive substrate lost forever**

**Why This Exists:**
- Assumption: Workspace is "temporary" like `.cache/`
- **Reality:** Workspace is the **active reasoning layer** of the cognitive substrate

#### Bug 4: Scripts Self-Upgrade

**Location:** `FileUpgrader.FRAMEWORK_OWNED` (line 1459)

```python
FRAMEWORK_OWNED = [
    "standards/universal/",
    "workflows/",
    "ouroboros/",
    "scripts/",  # ← BUG: Upgrading itself while running
]
```

**Impact:**
- Upgrade script is in `.praxis-os/scripts/`
- Script deletes `.praxis-os/scripts/` (including itself)
- Script tries to copy new scripts
- **Potential corruption** if script is modified mid-execution

**Why This Exists:**
- Scripts are framework-owned (should be upgraded)
- But upgrading while running is dangerous
- Like `rm -rf /bin/bash` while bash is running

#### Bug 5: No Backup Pruning

**Location:** `BackupManager.create_backup()` (lines 959-971)

**Impact:**
- Backups accumulate indefinitely in `.praxis-os/.backups/`
- Each backup is ~50MB (full copy of workspace, specs, standards, framework files)
- After 10 upgrades: 500MB of old backups
- After 50 upgrades: 2.5GB of old backups
- **Disk bloat** over time

**Why This Exists:**
- No cleanup logic implemented
- Assumption: User will manually clean up old backups

#### Bug 6: No Verify Mode

**Location:** N/A (feature missing)

**Impact:**
- User can't preview what will be upgraded before committing
- No way to see which files will change
- No way to see config differences
- **Blind upgrade** - user doesn't know what's happening until it's done

**Why This Exists:**
- Not implemented yet

#### Bug 7: Requirements.txt Not Reinstalled

**Location:** `DependencyUpdater.update_dependencies()` (lines 1850-1900)

**Impact:**
- Upgrade copies new `requirements.txt` to `.praxis-os/ouroboros/requirements.txt`
- But doesn't run `pip install -r requirements.txt`
- Venv becomes stale (old package versions)
- **MCP server may fail** if new code requires updated dependencies

**Why This Exists:**
- Assumption: User will manually run `pip install` after upgrade
- But this is error-prone and easy to forget

---

### Desired State

**Safe Upgrade Flow:**

0. **Verify Mode (optional)** - `--verify-only` flag shows what will change
1. **Pre-Flight** - Validate installation
2. **Backup** - **Include workspace, specs, standards, config; prune old backups (keep last 5)**
3. **Clone Source** - Verify source integrity
4. **Upgrade Files** - **Use `dirs_exist_ok=True`, NO delete flag, exclude scripts/**
5. **Config Reconciliation** - Stage new config for LLM merge
6. **Dependencies** - **Update requirements.txt + reinstall packages**
7. **Rebuild Index** - Schedule RAG index rebuild
8. **Validation** - Verify upgrade success
9. **Rollback (if failure)** - **Selective restore (only backed-up dirs), venv untouched**

**Safety Guarantees:**

✅ **Cognitive substrate always backed up** - Workspace, specs, standards protected  
✅ **Selective restore** - Only restore backed-up directories, never nuke entire `.praxis-os/`  
✅ **No delete flag** - Use `dirs_exist_ok=True` for safe overwrites  
✅ **Scripts not self-upgraded** - Upgrade script stable during execution  
✅ **Venv updated** - `pip install -r requirements.txt` after copying new requirements  
✅ **Backup pruning** - Keep last 5 backups, delete older ones  
✅ **Verify mode** - Preview changes before committing

---

## Solution Overview

### Architecture

**No architecture changes needed** - Same 8-phase flow, but with fundamental safety improvements.

**Key Improvements:**

1. **Remove delete flag** - Replace all `delete=True` with `dirs_exist_ok=True`
2. **Selective restore** - Only restore backed-up directories, never nuke `.praxis-os/`
3. **Backup workspace** - Remove `workspace` from exclusions
4. **Backup pruning** - Keep last 5 backups, delete older ones
5. **Scripts exclusion** - Remove `scripts/` from `FRAMEWORK_OWNED`
6. **Requirements reinstall** - Run `pip install -r requirements.txt` after copying new requirements
7. **Verify mode** - Add `--verify-only` flag to preview changes

---

## Design Details

### 1. Remove Delete Flag (Root Fix)

**File:** `upgrade-praxis-os.py`  
**Class:** `FileUpgrader`  
**Method:** `_rsync()` (lines 1681-1747)

**Current:**
```python
def _rsync(self, src: Path, dst: Path, delete: bool = False) -> None:
    """Copy files with optional delete."""
    import shutil

    ignore = shutil.ignore_patterns(...)

    try:
        if delete and dst.exists():
            shutil.rmtree(dst)  # ← REMOVE THIS

        shutil.copytree(src, dst, dirs_exist_ok=True, ignore=ignore)
        # ...
    except Exception as e:
        raise IOError(f"Failed to copy {src} to {dst}: {e}") from e
```

**Fixed:**
```python
def _rsync(self, src: Path, dst: Path) -> None:
    """
    Copy files from source to destination with safe overwrites.
    
    Uses dirs_exist_ok=True to safely overwrite existing files without
    deleting entire directories. Preserves sibling directories (e.g., venv/).
    
    Args:
        src: Source directory
        dst: Destination directory
    
    Raises:
        FileNotFoundError: If source does not exist
        IOError: If copy operation fails
    """
    import shutil

    # Verify source exists BEFORE any operation
    if not src.exists():
        raise FileNotFoundError(
            f"Source directory does not exist: {src}\n"
            f"Cannot proceed with upgrade. Verify source path is correct."
        )

    ignore = shutil.ignore_patterns(
        "__pycache__",
        "*.pyc",
        ".DS_Store",
        ".pytest_cache",
        ".mypy_cache",
        ".praxis-os",
        ".cursor",
    )

    try:
        # NO DELETION - dirs_exist_ok=True safely overwrites files
        # This preserves sibling directories like venv/ that shouldn't be touched
        shutil.copytree(src, dst, dirs_exist_ok=True, ignore=ignore)
    except Exception as e:
        raise IOError(f"Failed to copy {src} to {dst}: {e}") from e
```

**Update all callers:**
```python
# In _upgrade_ouroboros(), _upgrade_standards(), _upgrade_workflows()
# OLD:
self._rsync(src, dst, delete=True)

# NEW:
self._rsync(src, dst)  # No delete flag
```

**Rationale:**
- `shutil.copytree(dirs_exist_ok=True)` already overwrites files safely
- No need to delete entire directories
- Preserves sibling directories (e.g., venv/, .cache/, state/)
- Eliminates root cause of data loss bugs

---

### 2. Selective Restore (Not Nuclear)

**File:** `upgrade-praxis-os.py`  
**Class:** `BackupManager`  
**Method:** `restore_from_backup()` (lines 1017-1022)

**Current:**
```python
def restore_from_backup(self, backup_dir: Path) -> None:
    if not backup_dir.exists():
        raise FileNotFoundError(f"Backup directory not found: {backup_dir}")

    target_dir = self.target / ".praxis-os"

    try:
        if target_dir.exists():
            shutil.rmtree(target_dir)  # ← REMOVE THIS
        shutil.copytree(backup_dir, target_dir)
    except Exception as e:
        raise IOError(f"Failed to restore from backup: {e}") from e

    self._validate_restore(target_dir)
```

**Fixed:**
```python
def restore_from_backup(self, backup_dir: Path) -> None:
    """
    Restore user data and framework files from backup.
    
    Selectively restores only the directories that were backed up:
    - workspace/ (user data)
    - specs/ (user data)
    - standards/ (user + framework)
    - config/ (user config)
    - ouroboros/ (framework code)
    - workflows/ (framework code)
    - scripts/ (framework code)
    
    Does NOT touch:
    - venv/ (out of scope, user manages)
    - .cache/ (ephemeral, will rebuild)
    - state/ (runtime, not backed up)
    
    Args:
        backup_dir: Path to backup directory to restore from
    
    Raises:
        FileNotFoundError: If backup directory doesn't exist
        IOError: If restore operation fails
    """
    import shutil

    if not backup_dir.exists():
        raise FileNotFoundError(f"Backup directory not found: {backup_dir}")

    target_dir = self.target / ".praxis-os"
    
    # Directories that were backed up (selective restore)
    backed_up_dirs = [
        "workspace",
        "specs", 
        "standards",
        "config",
        "ouroboros",
        "workflows",
        "scripts",
    ]

    try:
        for item in backed_up_dirs:
            src = backup_dir / item
            dst = target_dir / item
            
            if src.exists():
                print(f"  Restoring {item}/...")
                
                # Only delete what we're restoring
                if dst.exists():
                    shutil.rmtree(dst)
                
                shutil.copytree(src, dst)
        
        print("  ✓ Backup restored")
        print("  Note: venv/ not touched (run 'pip install -r requirements.txt' if needed)")
        
    except Exception as e:
        raise IOError(f"Failed to restore from backup: {e}") from e

    self._validate_restore(target_dir)
```

**Rationale:**
- Only restore directories that were backed up
- Never delete entire `.praxis-os/` directory
- Venv, .cache, state are out of scope (not backed up, not restored)
- If venv is broken, user manually reinstalls deps

---

### 3. Backup Workspace (Cognitive Substrate)

**File:** `upgrade-praxis-os.py`  
**Class:** `BackupManager`  
**Method:** `create_backup()` (lines 959-971)

**Current:**
```python
ignore_patterns = shutil.ignore_patterns(
    ".cache",
    "workspace",  # ← REMOVE THIS
    "venv",
    "__pycache__",
    "*.pyc",
    ".DS_Store",
    "state",
    ".backups",
)
```

**Fixed:**
```python
ignore_patterns = shutil.ignore_patterns(
    ".cache",      # ← Ephemeral (RAG index, rebuilt from standards)
    "venv",        # ← Rebuildable (pip install from requirements.txt)
    "state",       # ← Runtime state (browser sessions, workflow state)
    "__pycache__", # ← Build artifact
    "*.pyc",       # ← Build artifact
    ".DS_Store",   # ← macOS junk
    ".backups",    # ← Old backups (avoid recursion)
    # workspace, specs, standards, config are ALL backed up
)
```

**Rationale:**

| Directory | Backed Up? | Why? |
|-----------|------------|------|
| `workspace/` | ✅ YES | User's active work (design docs, analysis, investigations) |
| `specs/` | ✅ YES | Structured specifications |
| `standards/` | ✅ YES | Universal + development standards |
| `config/` | ✅ YES | User configuration |
| `.cache/` | ❌ NO | Ephemeral (rebuilt from standards) |
| `venv/` | ❌ NO | Rebuildable (pip install) |
| `state/` | ❌ NO | Runtime state (sessions) |

**Workspace Persistence Model:**

**For Solo Developers:**
- Workspace is **personal working memory**
- **Not committed** to git (stays local)
- **Always backed up** (protects active work)

**For Teams:**
- Workspace is **still personal** (not shared)
- Each developer has their own workspace
- **Not committed** (prevents 50MB merge conflicts)
- **Always backed up** (protects individual work)

**Why Not Commit Workspace for Teams?**

Imagine 5 developers × 10MB each = 50MB of markdown:
- 1,250 design docs
- 500 analysis reports
- 750 scratch notes
- **Merge conflicts from hell**
- **Cognitive overload** (which analysis is correct?)
- **AI confusion** (5 different recommendations)

**Workspace = Your local IDE's unsaved files**
- ❌ Don't commit unsaved files (chaos)
- ✅ Backup unsaved files (your work matters)

---

### 2. Venv Rebuild on Rollback

**File:** `upgrade-praxis-os.py`  
**Class:** `BackupManager`  
**Method:** `restore_from_backup()` (lines 1017-1022)

**Current:**
```python
def restore_from_backup(self, backup_dir: Path) -> None:
    if not backup_dir.exists():
        raise FileNotFoundError(f"Backup directory not found: {backup_dir}")

    target_dir = self.target / ".praxis-os"

    try:
        if target_dir.exists():
            shutil.rmtree(target_dir)
        shutil.copytree(backup_dir, target_dir)
    except Exception as e:
        raise IOError(f"Failed to restore from backup: {e}") from e

    self._validate_restore(target_dir)
```

**Fixed:**
```python
def restore_from_backup(self, backup_dir: Path) -> None:
    """
    Restore .praxis-os/ from backup (rollback).
    
    Removes current installation, restores from backup, and rebuilds venv.
    
    Args:
        backup_dir: Path to backup directory to restore from
    
    Raises:
        FileNotFoundError: If backup directory doesn't exist
        IOError: If restore operation fails
        RuntimeError: If venv rebuild fails
    """
    import shutil

    if not backup_dir.exists():
        raise FileNotFoundError(f"Backup directory not found: {backup_dir}")

    target_dir = self.target / ".praxis-os"

    try:
        # 1. Delete current installation
        if target_dir.exists():
            shutil.rmtree(target_dir)
        
        # 2. Restore from backup
        shutil.copytree(backup_dir, target_dir)
        
        # 3. Rebuild venv if it was excluded from backup
        venv_dir = target_dir / "venv"
        if not venv_dir.exists():
            print("\n[RESTORE] Rebuilding virtual environment...")
            self._rebuild_venv(target_dir)
        
    except Exception as e:
        raise IOError(f"Failed to restore from backup: {e}") from e

    self._validate_restore(target_dir)


def _rebuild_venv(self, praxis_dir: Path) -> None:
    """
    Rebuild virtual environment and install dependencies.
    
    Args:
        praxis_dir: Path to .praxis-os/ directory
    
    Raises:
        RuntimeError: If venv creation or pip install fails
    """
    import subprocess
    import sys
    
    venv_dir = praxis_dir / "venv"
    requirements_file = praxis_dir / "ouroboros" / "requirements.txt"
    
    print(f"  Creating venv at {venv_dir}...")
    
    try:
        # Create venv
        subprocess.run(
            [sys.executable, "-m", "venv", str(venv_dir)],
            check=True,
            capture_output=True,
            text=True,
            timeout=60,
        )
        print("  ✓ Venv created")
        
        # Install dependencies if requirements.txt exists
        if requirements_file.exists():
            # Determine pip path based on platform
            if os.name == "nt":  # Windows
                pip_path = venv_dir / "Scripts" / "pip"
            else:  # Unix-like (Linux, macOS)
                pip_path = venv_dir / "bin" / "pip"
            
            print(f"  Installing dependencies from {requirements_file}...")
            
            subprocess.run(
                [str(pip_path), "install", "-q", "-r", str(requirements_file)],
                check=True,
                capture_output=True,
                text=True,
                timeout=300,  # 5 min timeout for pip install
            )
            print("  ✓ Dependencies installed")
        else:
            print("  ⚠️  No requirements.txt found, skipping dependency install")
            
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Failed to rebuild venv: {e.stderr if e.stderr else str(e)}"
        ) from e
    except subprocess.TimeoutExpired as e:
        raise RuntimeError(f"Venv rebuild timed out: {e}") from e
```

**Rationale:**

- Venv is large (~250MB), correctly excluded from backup
- But MCP server requires venv to start
- Rollback must rebuild venv from `requirements.txt`
- Same pattern as install script (lines 417-468)

---

### 4. Backup Pruning (Keep Last 5)

**File:** `upgrade-praxis-os.py`  
**Class:** `BackupManager`  
**Method:** `create_backup()` (lines 959-971)

**Add new method:**
```python
def _prune_old_backups(self, max_backups: int = 5) -> None:
    """
    Prune old backups, keeping only the most recent N backups.
    
    Args:
        max_backups: Maximum number of backups to keep (default: 5)
    """
    import shutil
    from pathlib import Path
    
    backup_root = self.target / ".praxis-os" / ".backups"
    
    if not backup_root.exists():
        return
    
    # Get all backup directories sorted by modification time (newest first)
    backups = sorted(
        [d for d in backup_root.iterdir() if d.is_dir()],
        key=lambda d: d.stat().st_mtime,
        reverse=True
    )
    
    # Keep the most recent max_backups, delete the rest
    backups_to_delete = backups[max_backups:]
    
    if backups_to_delete:
        print(f"\n[BACKUP PRUNING] Removing {len(backups_to_delete)} old backups (keeping last {max_backups}):")
        for backup in backups_to_delete:
            print(f"  Deleting: {backup.name}")
            shutil.rmtree(backup)
        print(f"  ✓ Old backups pruned")
```

**Update `create_backup()` to call pruning:**
```python
def create_backup(self) -> Path:
    """Create timestamped backup of .praxis-os/ directory."""
    # ... existing backup logic ...
    
    # Prune old backups (keep last 5)
    self._prune_old_backups(max_backups=5)
    
    return backup_dir
```

**Rationale:**
- Backups accumulate over time (~50MB each)
- Keep last 5 for safety (recent rollback history)
- Delete older ones to prevent disk bloat
- User can adjust `max_backups` if needed

---

### 5. Scripts Exclusion from Upgrade

**File:** `upgrade-praxis-os.py`  
**Class:** `FileUpgrader`  
**Constant:** `FRAMEWORK_OWNED` (line 1456-1462)

**Current:**
```python
FRAMEWORK_OWNED = [
    "standards/universal/",
    "workflows/",
    "ouroboros/",
    "scripts/",  # ← REMOVE THIS
]
```

**Fixed:**
```python
FRAMEWORK_OWNED = [
    "standards/universal/",  # ← Framework standards
    "workflows/",            # ← Framework workflows
    "ouroboros/",            # ← MCP server code
    # scripts/ excluded - don't upgrade while running
]
```

**Method:** `upgrade_framework_files()` (line 1509-1515)

**Current:**
```python
def upgrade_framework_files(self) -> UpgradeReport:
    self._upgrade_standards()
    self._upgrade_workflows()
    self._upgrade_ouroboros()
    self._upgrade_scripts()  # ← REMOVE THIS
    self._verify_checksums()
    return self.changes
```

**Fixed:**
```python
def upgrade_framework_files(self) -> UpgradeReport:
    """
    Upgrade all framework-owned files.
    
    Upgrades standards, workflows, and ouroboros directories.
    Scripts are NOT upgraded (to avoid self-modification).
    Verifies checksums after copy.
    
    Returns:
        UpgradeReport with all changes tracked
    
    Raises:
        IOError: If upgrade operation fails
    """
    self._upgrade_standards()
    self._upgrade_workflows()
    self._upgrade_ouroboros()
    # scripts/ NOT upgraded - avoid self-modification while running
    self._verify_checksums()
    return self.changes
```

**User Instructions (added to validation phase):**

```python
def _display_user_instructions(self) -> None:
    """
    Display user instructions for MCP testing.
    """
    print("\n" + "=" * 70)
    print("✅ Upgrade validation passed!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Restart your MCP server")
    print("2. Test the upgraded system")
    print("3. Verify all functionality works as expected")
    print()
    print("⚠️  IMPORTANT: Scripts were not auto-upgraded.")
    print("   To upgrade scripts, run:")
    print("   curl -sSL https://raw.githubusercontent.com/honeyhiveai/praxis-os/main/dist/scripts/upgrade-praxis-os.py | python3 - .")
    print()
    print("If you encounter issues, you can restore from backup:")
    print("   See .praxis-os/.backups/ directory")
    print("=" * 70 + "\n")
```

**Rationale:**

- Scripts contain the running upgrade script
- Upgrading while running = potential corruption
- User can manually upgrade scripts after main upgrade completes
- Curl pattern downloads fresh script, then runs it

---

### 6. Requirements Reinstall (Keep Venv Fresh)

**File:** `upgrade-praxis-os.py`  
**Class:** `DependencyUpdater`  
**Method:** `update_dependencies()` (lines 1850-1900)

**Current:**
```python
def update_dependencies(self, skip_install: bool = False) -> None:
    self._update_requirements_txt()
    self._update_package_json()
    
    if not skip_install:
        self._reinstall_python_packages()  # ← Already exists!
```

**The `_reinstall_python_packages()` method already exists (added in commit 9a5ac82):**
```python
def _reinstall_python_packages(self) -> None:
    """
    Reinstall Python packages from requirements.txt.
    
    Runs pip install --upgrade -r requirements.txt in the existing venv.
    """
    import subprocess
    import sys
    
    venv_dir = self.target / ".praxis-os" / "venv"
    requirements_file = self.target / ".praxis-os" / "ouroboros" / "requirements.txt"
    
    if not venv_dir.exists():
        print("  ⚠️  Virtual environment not found, skipping package reinstall")
        print("  Note: User should recreate venv after upgrade")
        return
    
    if not requirements_file.exists():
        print("  ⚠️  No requirements.txt found, skipping package reinstall")
        return
    
    # Determine pip path based on platform
    if os.name == "nt":  # Windows
        pip_path = venv_dir / "Scripts" / "pip"
    else:  # Unix-like (Linux, macOS)
        pip_path = venv_dir / "bin" / "pip"
    
    print(f"\n[DEPENDENCIES] Reinstalling Python packages...")
    print(f"  Running: {pip_path} install --upgrade -r {requirements_file}")
    
    try:
        subprocess.run(
            [str(pip_path), "install", "--upgrade", "-r", str(requirements_file)],
            check=True,
            capture_output=True,
            text=True,
            timeout=300,  # 5 min timeout
        )
        print("  ✓ Python packages reinstalled")
    except subprocess.CalledProcessError as e:
        print(f"  ⚠️  Package reinstall failed: {e.stderr if e.stderr else str(e)}")
        print("  Note: User may need to manually run 'pip install -r requirements.txt'")
    except subprocess.TimeoutExpired:
        print("  ⚠️  Package reinstall timed out (>5 minutes)")
        print("  Note: User may need to manually run 'pip install -r requirements.txt'")
```

**Status:** ✅ **Already implemented!** Just needs to ensure `skip_install=False` by default.

**Rationale:**
- Upgrade copies new `requirements.txt` to `.praxis-os/ouroboros/requirements.txt`
- Must run `pip install --upgrade -r requirements.txt` to update venv
- Otherwise venv becomes stale (old package versions)
- MCP server may fail if new code requires updated dependencies

---

### 7. Verify Mode (Preview Changes)

**File:** `upgrade-praxis-os.py`  
**Class:** `UpgradeOrchestrator`  
**Method:** `run()` (lines 2700-2850)

**Add new method:**
```python
def verify_only(self) -> None:
    """
    Verify mode: Show what would be upgraded without making changes.
    
    Displays:
    - Framework files that would be upgraded
    - User files that would NOT be touched
    - Config changes detected
    - Backup size estimate
    """
    print("=" * 70)
    print("UPGRADE VERIFICATION (--verify-only mode)")
    print("=" * 70)
    print("\nThis is a dry-run. No changes will be made.\n")
    
    # Phase 1: Pre-flight checks
    print("Phase 1: Pre-Flight Checks")
    validator = PreFlightValidator(self.target)
    validator.validate_installation()
    print("✓ Installation valid\n")
    
    # Phase 2: Estimate backup size
    print("Phase 2: Backup Estimate")
    backup_mgr = BackupManager(self.target)
    backup_size = self._estimate_backup_size()
    print(f"  Estimated backup size: {backup_size:.1f} MB")
    print(f"  Backup would include: workspace/, specs/, standards/, config/, ouroboros/, workflows/, scripts/")
    print(f"  Backup would exclude: venv/, .cache/, state/\n")
    
    # Phase 3: Framework files to upgrade
    print("Phase 3: Framework Files to Upgrade")
    source_dir = self._get_source_directory()
    self._show_framework_changes(source_dir)
    
    # Phase 4: User files (never touched)
    print("\nPhase 4: User Files (Never Touched)")
    self._show_user_files()
    
    # Phase 5: Config changes
    print("\nPhase 5: Config Changes")
    reconciler = ConfigReconciler(source_dir, self.target)
    self._show_config_changes(reconciler)
    
    # Phase 6: Dependencies
    print("\nPhase 6: Dependencies")
    self._show_dependency_changes(source_dir)
    
    print("\n" + "=" * 70)
    print("VERIFICATION COMPLETE")
    print("=" * 70)
    print("\nTo perform the upgrade, run without --verify-only flag:")
    print(f"  python3 upgrade-praxis-os.py {self.target}")
    print()

def _estimate_backup_size(self) -> float:
    """Estimate backup size in MB."""
    from pathlib import Path
    
    praxis_dir = self.target / ".praxis-os"
    backed_up_dirs = ["workspace", "specs", "standards", "config", "ouroboros", "workflows", "scripts"]
    
    total_size = 0
    for dir_name in backed_up_dirs:
        dir_path = praxis_dir / dir_name
        if dir_path.exists():
            total_size += sum(f.stat().st_size for f in dir_path.rglob("*") if f.is_file())
    
    return total_size / (1024 * 1024)  # Convert to MB

def _show_framework_changes(self, source_dir: Path) -> None:
    """Show which framework files would be upgraded."""
    framework_dirs = ["ouroboros", "workflows", "standards/universal"]
    
    for dir_name in framework_dirs:
        src = source_dir / "dist" / dir_name
        dst = self.target / ".praxis-os" / dir_name
        
        if src.exists():
            src_files = list(src.rglob("*.py"))
            print(f"  {dir_name}/ - {len(src_files)} Python files would be upgraded")

def _show_user_files(self) -> None:
    """Show user files that would NOT be touched."""
    praxis_dir = self.target / ".praxis-os"
    user_dirs = ["workspace", "specs", "standards/project", "standards/development"]
    
    for dir_name in user_dirs:
        dir_path = praxis_dir / dir_name
        if dir_path.exists():
            files = list(dir_path.rglob("*"))
            files = [f for f in files if f.is_file()]
            size_mb = sum(f.stat().st_size for f in files) / (1024 * 1024)
            print(f"  {dir_name}/ - {len(files)} files ({size_mb:.1f} MB) - NEVER TOUCHED")

def _show_config_changes(self, reconciler: ConfigReconciler) -> None:
    """Show config changes detected."""
    new_template = reconciler.source / "dist" / "config" / "mcp.yaml"
    current_config = reconciler.target / ".praxis-os" / "config" / "mcp.yaml"
    
    if not new_template.exists():
        print("  No config changes detected")
        return
    
    if current_config.exists() and reconciler._configs_identical(new_template, current_config):
        print("  Config unchanged (no reconciliation needed)")
    else:
        print("  Config changes detected - would stage for LLM merge")

def _show_dependency_changes(self, source_dir: Path) -> None:
    """Show dependency changes."""
    new_req = source_dir / "dist" / "ouroboros" / "requirements.txt"
    current_req = self.target / ".praxis-os" / "ouroboros" / "requirements.txt"
    
    if not new_req.exists():
        print("  No requirements.txt changes")
        return
    
    if current_req.exists():
        new_deps = set(new_req.read_text().strip().split("\n"))
        current_deps = set(current_req.read_text().strip().split("\n"))
        
        added = new_deps - current_deps
        removed = current_deps - new_deps
        
        if added or removed:
            print(f"  requirements.txt changes detected:")
            if added:
                print(f"    Added: {len(added)} packages")
            if removed:
                print(f"    Removed: {len(removed)} packages")
            print(f"  Would run: pip install --upgrade -r requirements.txt")
        else:
            print("  requirements.txt unchanged")
```

**Update `main()` to support `--verify-only` flag:**
```python
def main():
    parser = argparse.ArgumentParser(description="Upgrade prAxIs OS installation")
    parser.add_argument("target", type=Path, help="Target directory containing .praxis-os/")
    parser.add_argument("--source", type=Path, help="Source directory (optional)")
    parser.add_argument("--skip-deps", action="store_true", help="Skip dependency updates")
    parser.add_argument("--verify-only", action="store_true", help="Preview changes without upgrading")
    
    args = parser.parse_args()
    
    orchestrator = UpgradeOrchestrator(args.target, args.source)
    orchestrator.args = args
    
    if args.verify_only:
        orchestrator.verify_only()
    else:
        orchestrator.run()
```

**Rationale:**
- User can see what will change before committing
- Reduces fear of upgrade ("what will it do?")
- Helps debug upgrade issues (preview before running)
- No side effects (read-only mode)

---

### 8. Source Verification Before Delete

**File:** `upgrade-praxis-os.py`  
**Class:** `FileUpgrader`  
**Method:** `_rsync()` (lines 1681-1747)

**Current:**
```python
def _rsync(self, src: Path, dst: Path, delete: bool = False) -> None:
    import shutil

    # ... debug output ...

    ignore = shutil.ignore_patterns(...)

    try:
        if delete and dst.exists():
            shutil.rmtree(dst)  # ← Deletes FIRST

        shutil.copytree(src, dst, dirs_exist_ok=True, ignore=ignore)  # ← Copies SECOND
        
        # ... count files ...
    except Exception as e:
        raise IOError(f"Failed to copy {src} to {dst}: {e}") from e
```

**Fixed:**
```python
def _rsync(self, src: Path, dst: Path, delete: bool = False) -> None:
    """
    Copy files from source to destination with ignore patterns.
    
    Verifies source exists before deleting destination (safety check).
    
    Args:
        src: Source directory
        dst: Destination directory
        delete: If True, delete destination before copying
    
    Raises:
        FileNotFoundError: If source does not exist
        IOError: If copy operation fails
    """
    import shutil

    print(f"\n[DEBUG] _rsync:")
    print(f"  src={src}")
    print(f"  dst={dst}")
    print(f"  delete={delete}")
    print(f"  src.exists()={src.exists()}")
    print(f"  dst.exists()={dst.exists()}")

    # ✅ VERIFY SOURCE EXISTS BEFORE DELETING DESTINATION
    if not src.exists():
        raise FileNotFoundError(
            f"Source directory does not exist: {src}\n"
            f"Cannot proceed with upgrade. Verify source path is correct."
        )

    # Ignore patterns matching install-praxis-os.py
    ignore = shutil.ignore_patterns(
        "__pycache__",
        "*.pyc",
        ".DS_Store",
        ".pytest_cache",
        ".mypy_cache",
        ".praxis-os",
        ".cursor",
    )

    try:
        # ✅ ONLY DELETE AFTER VERIFYING SOURCE EXISTS
        if delete and dst.exists():
            print(f"  [ACTION] Deleting {dst}")
            shutil.rmtree(dst)
            print(f"  [DONE] Deleted {dst}")

        print(f"  [ACTION] Copying {src} -> {dst}")
        shutil.copytree(src, dst, dirs_exist_ok=True, ignore=ignore)
        print(f"  [DONE] Copy complete")

        # Count what was copied
        if dst.exists():
            copied_files = list(dst.rglob("*"))
            copied_files = [f for f in copied_files if f.is_file()]
            copied_py = [f for f in copied_files if f.suffix == ".py"]
            print(
                f"  [RESULT] Copied {len(copied_files)} total files, {len(copied_py)} Python files"
            )
    except Exception as e:
        print(f"  [ERROR] Copy failed: {e}")
        raise IOError(f"Failed to copy {src} to {dst}: {e}") from e
```

**Rationale:**

- Source path might be incorrect (typo, wrong directory)
- Deleting before verifying = data loss
- Raise clear error if source missing
- User can fix source path and retry

---

### 5. Config Versioning

**File:** `upgrade-praxis-os.py`  
**Class:** `ConfigReconciler`  
**Method:** `prepare_reconciliation()` (lines 1977-2025)

**Current:**
```python
def prepare_reconciliation(self) -> str:
    new_template = self.source / "dist" / "config" / "mcp.yaml"
    current_config = self.target / ".praxis-os" / "config" / "mcp.yaml"
    comparison_file = self.target / ".praxis-os" / "config" / "mcp.yaml.new"
    
    if not new_template.exists():
        return "NO_CHANGES"

    # Copy new template
    shutil.copy(new_template, comparison_file)
    
    # Check if identical
    if current_config.exists() and self._configs_identical(new_template, current_config):
        comparison_file.unlink()
        return "NO_CHANGES"
    
    # Create reconciliation prompt
    self._create_reconciliation_prompt()
    
    return "RECONCILIATION_NEEDED"
```

**Fixed:**
```python
def prepare_reconciliation(self, new_version: str) -> str:
    """
    Prepare config for LLM merge.
    
    Copies new template with version number, detects changes, and creates 
    reconciliation prompt if needed.
    
    Args:
        new_version: Version string (e.g., "1.2.3") from source
    
    Returns:
        "NO_CHANGES" if configs are identical, "RECONCILIATION_NEEDED" otherwise
    """
    import shutil

    new_template = self.source / "dist" / "config" / "mcp.yaml"
    current_config = self.target / ".praxis-os" / "config" / "mcp.yaml"
    
    # ✅ VERSION CONFIG FILES
    comparison_file = self.target / ".praxis-os" / "config" / f"mcp-v{new_version}.yaml"

    if not new_template.exists():
        return "NO_CHANGES"  # No template to reconcile

    # Copy new template with version
    shutil.copy(new_template, comparison_file)

    # Check if configs are identical
    if current_config.exists() and self._configs_identical(
        new_template, current_config
    ):
        comparison_file.unlink()
        return "NO_CHANGES"

    # Create reconciliation prompt
    self._create_reconciliation_prompt(new_version)

    return "RECONCILIATION_NEEDED"


def _create_reconciliation_prompt(self, new_version: str) -> None:
    """
    Create CONFIG_RECONCILIATION_NEEDED.md prompt file.
    
    Args:
        new_version: Version string for the new config
    """
    prompt_file = (
        self.target / ".praxis-os" / "config" / "CONFIG_RECONCILIATION_NEEDED.md"
    )

    prompt_content = f"""# Configuration Reconciliation Needed

The upgrade process has detected changes to the MCP configuration template.

## Files

- **Current config:** `.praxis-os/config/mcp.yaml`
- **New template:** `.praxis-os/config/mcp-v{new_version}.yaml`

## Action Required

Please review the differences between your current configuration and the new template.
Merge any new settings or changes that are relevant to your setup.

## Steps

1. Compare the two files:
   ```bash
   diff .praxis-os/config/mcp.yaml .praxis-os/config/mcp-v{new_version}.yaml
   ```

2. Merge changes manually or use a merge tool

3. Delete the versioned file when done:
   ```bash
   rm .praxis-os/config/mcp-v{new_version}.yaml
   ```

4. Delete this prompt file:
   ```bash
   rm .praxis-os/config/CONFIG_RECONCILIATION_NEEDED.md
   ```

## Notes

- Your current configuration has been preserved
- The new template is provided as `mcp-v{new_version}.yaml` for reference
- No changes have been made to your active configuration
- Version {new_version} may include new features or breaking changes
"""

    prompt_file.write_text(prompt_content)
```

**Orchestrator Update:**

```python
# Phase 4: Config reconciliation (line 2768)
reconciler = ConfigReconciler(source_dir, self.target)
status = reconciler.prepare_reconciliation(new_version)  # ← Pass version
reconciler.merge_gitignore()
if status == "RECONCILIATION_NEEDED":
    print(f"⚠️  Config reconciliation required (v{new_version})")
    print(f"   See: .praxis-os/config/mcp-v{new_version}.yaml")
else:
    print("✓ Config unchanged, no reconciliation needed")
print()
```

**Rationale:**

- Versioned config files are easier to track
- User can see which version is new
- Multiple upgrades don't overwrite same `.new` file
- Clear audit trail of config changes

---

## Implementation Plan

### Phase 1: Root Cause Fix (CRITICAL - 4 hours)

**Goal:** Remove delete flag and implement selective restore

**Tasks:**
- [ ] Remove `delete` parameter from `_rsync()` signature
- [ ] Remove all `shutil.rmtree()` calls before `copytree` in `_rsync()`
- [ ] Add source existence check to `_rsync()` (raise `FileNotFoundError` if missing)
- [ ] Update all callers: remove `delete=True` arguments
- [ ] Rewrite `restore_from_backup()` to be selective (only restore backed-up dirs)
- [ ] Test upgrade with `dirs_exist_ok=True` (no delete)
- [ ] Test rollback with selective restore (venv untouched)

**Acceptance Criteria:**
- [ ] No `delete` flag in `_rsync()` signature
- [ ] No `shutil.rmtree()` before `copytree` in `_rsync()`
- [ ] Source verified before any copy operation
- [ ] Restore only touches backed-up directories
- [ ] Venv preserved during rollback
- [ ] All tests pass

---

### Phase 2: Cognitive Substrate Protection (CRITICAL - 2 hours)

**Goal:** Backup workspace and prune old backups

**Tasks:**
- [ ] Remove `workspace` from backup exclusion list (line 964)
- [ ] Add `_prune_old_backups()` method to `BackupManager`
- [ ] Call `_prune_old_backups(max_backups=5)` after backup creation
- [ ] Test workspace included in backup
- [ ] Test backup pruning (keep last 5, delete older)
- [ ] Test workspace restored on rollback

**Acceptance Criteria:**
- [ ] Workspace files present in backup
- [ ] Old backups pruned (keep last 5)
- [ ] Workspace restored on rollback
- [ ] All tests pass

---

### Phase 3: Scripts Safety (MEDIUM - 2 hours)

**Goal:** Prevent self-modification during upgrade

**Tasks:**
- [ ] Remove `scripts/` from `FRAMEWORK_OWNED` (line 1459)
- [ ] Remove `_upgrade_scripts()` call from `upgrade_framework_files()`
- [ ] Update `_display_user_instructions()` with manual upgrade steps
- [ ] Test upgrade completes without scripts upgrade
- [ ] Verify upgrade script not corrupted

**Acceptance Criteria:**
- [ ] Scripts directory unchanged after upgrade
- [ ] Upgrade completes successfully
- [ ] User instructions displayed
- [ ] All tests pass

---

### Phase 4: Requirements Reinstall (HIGH - 1 hour)

**Goal:** Keep venv fresh with updated dependencies

**Tasks:**
- [ ] Verify `_reinstall_python_packages()` exists (already implemented)
- [ ] Ensure `skip_install=False` by default in `update_dependencies()`
- [ ] Test requirements.txt copied and reinstalled
- [ ] Test MCP server starts with new dependencies

**Acceptance Criteria:**
- [ ] Requirements.txt copied to `.praxis-os/ouroboros/`
- [ ] `pip install --upgrade -r requirements.txt` runs successfully
- [ ] Venv has updated packages
- [ ] MCP server starts
- [ ] All tests pass

---

### Phase 5: Verify Mode (MEDIUM - 3 hours)

**Goal:** Add `--verify-only` flag to preview changes

**Tasks:**
- [ ] Add `verify_only()` method to `UpgradeOrchestrator`
- [ ] Add `_estimate_backup_size()` helper
- [ ] Add `_show_framework_changes()` helper
- [ ] Add `_show_user_files()` helper
- [ ] Add `_show_config_changes()` helper
- [ ] Add `_show_dependency_changes()` helper
- [ ] Update `main()` to support `--verify-only` flag
- [ ] Test verify mode (no changes made)

**Acceptance Criteria:**
- [ ] `--verify-only` flag works
- [ ] Shows framework files to upgrade
- [ ] Shows user files (never touched)
- [ ] Shows config changes
- [ ] Shows dependency changes
- [ ] No side effects (read-only)
- [ ] All tests pass

---

### Phase 6: Integration Testing (4 hours)

**Goal:** Validate all changes work together

**Tasks:**
- [ ] Test complete upgrade flow (success case)
- [ ] Test upgrade failure + rollback
- [ ] Test workspace preserved on rollback
- [ ] Test venv untouched during rollback
- [ ] Test MCP server starts after rollback
- [ ] Test backup pruning (keep last 5)
- [ ] Test scripts not upgraded
- [ ] Test requirements reinstalled
- [ ] Test verify mode

**Acceptance Criteria:**
- [ ] All success cases pass
- [ ] All failure cases handled gracefully
- [ ] No data loss in any scenario
- [ ] MCP server functional after all scenarios
- [ ] All tests pass

---

### Phase 7: Documentation (2 hours)

**Goal:** Document changes and usage

**Tasks:**
- [ ] Update upgrade script docstrings
- [ ] Update user-facing messages
- [ ] Document `--verify-only` flag
- [ ] Document backup pruning (keep last 5)
- [ ] Document venv management (out of scope)
- [ ] Update troubleshooting guide

**Deliverables:**
- Updated docstrings
- User guide for `--verify-only`
- Troubleshooting guide

---

## Success Metrics

### Functional Metrics

- [ ] **Zero cognitive substrate loss** - Workspace, specs, standards preserved on rollback
- [ ] **No delete flag** - All `delete=True` removed, use `dirs_exist_ok=True` everywhere
- [ ] **Selective restore** - Only backed-up directories restored, venv untouched
- [ ] **MCP server starts** - Venv kept fresh with `pip install --upgrade -r requirements.txt`
- [ ] **Scripts stable** - Upgrade script not corrupted during upgrade
- [ ] **Backup pruning** - Keep last 5 backups, delete older ones
- [ ] **Verify mode works** - `--verify-only` shows changes without side effects

### Quality Metrics

- [ ] **Test coverage ≥ 80%** - All critical paths tested (functional testing > unit tests)
- [ ] **No regressions** - Existing upgrade functionality preserved
- [ ] **Performance maintained** - Upgrade time ~5-10 minutes (pip install adds ~2 min)

### User Experience Metrics

- [ ] **User confidence** - No fear of cognitive substrate loss during upgrades
- [ ] **Clear guidance** - User knows what will change before upgrading (verify mode)
- [ ] **Rollback works** - User can recover from failed upgrades (selective restore)

---

## Risks and Mitigations

### Risk 1: Backup Size Increase

**Description:** Including workspace in backup increases backup size  
**Likelihood:** High  
**Impact:** Low  
**Mitigation:**
- Workspace typically 10-50MB (acceptable)
- Backup pruning keeps last 5 (delete older)
- Document backup size expectations
- Verify mode shows estimated backup size

### Risk 2: Pip Install Failures

**Description:** `pip install --upgrade -r requirements.txt` might fail (network issues, pip errors)  
**Likelihood:** Medium  
**Impact:** Medium  
**Mitigation:**
- Comprehensive error handling (already implemented)
- Clear error messages with remediation steps
- Non-blocking: Upgrade continues, user manually reinstalls if needed
- 5-minute timeout to prevent hanging

### Risk 3: Scripts Manual Upgrade Friction

**Description:** Users might forget to upgrade scripts manually  
**Likelihood:** Medium  
**Impact:** Low  
**Mitigation:**
- Clear instructions in validation output
- Document curl command for easy execution
- Scripts change infrequently (low friction)

### Risk 4: `dirs_exist_ok=True` Behavior

**Description:** `dirs_exist_ok=True` might not overwrite files as expected  
**Likelihood:** Low  
**Impact:** Medium  
**Mitigation:**
- Test thoroughly with existing installations
- Verify files are overwritten (not skipped)
- Document behavior in docstrings
- Fallback: User can manually delete and re-upgrade

### Risk 5: Selective Restore Complexity

**Description:** Selective restore (only backed-up dirs) might miss edge cases  
**Likelihood:** Low  
**Impact:** Medium  
**Mitigation:**
- Explicit list of backed-up directories (no wildcards)
- Test with various directory structures
- Document what is/isn't restored
- Verify mode shows what would be restored

---

## Dependencies

### Internal Dependencies

- **Install Script** - Reference implementation for venv creation
- **Backup Manager** - Core class being modified
- **File Upgrader** - Core class being modified
- **Config Reconciler** - Core class being modified

### External Dependencies

- **Python 3.9+** - Required for venv creation
- **pip** - Required for dependency installation
- **Git** - Required for source cloning
- **shutil** - File operations

---

## Open Questions

1. **Should we add a pre-upgrade validation that checks disk space for backup?**
   - Pro: Prevents backup failures mid-upgrade
   - Con: More complexity
   - **Decision:** ✅ YES - Add to pre-flight checks (show estimated backup size)

2. **Should verify mode show a diff of config changes?**
   - Pro: User can see exact changes without running `diff` manually
   - Con: More complexity
   - **Decision:** ⏸️ DEFER - Nice-to-have, not critical for MVP

3. **Should we make `max_backups` configurable via CLI flag?**
   - Pro: Power users can adjust (e.g., `--max-backups 10`)
   - Con: More complexity
   - **Decision:** ⏸️ DEFER - Default to 5, add flag later if needed

4. **Should we add a `--force-scripts-upgrade` flag?**
   - Pro: Power users can upgrade scripts if needed
   - Con: Dangerous, potential corruption
   - **Decision:** ❌ NO - Use curl pattern instead (safer)

---

## Future Enhancements

### Beyond MVP

1. **Incremental Backup** - Only backup changed files (faster, smaller)
2. **Backup Compression** - Compress backups to save disk space
3. **Backup Verification** - Verify backup integrity before upgrade
4. **Rollback Testing** - Automated rollback testing in CI
5. **Upgrade Preview** - Show what will change before upgrade
6. **Dry Run Mode** - Simulate upgrade without making changes
7. **Upgrade Notifications** - Notify user when new version available
8. **Auto-Cleanup** - Automatically clean up old backups and configs

---

## Appendix A: Workspace Persistence Model

### Why Workspace is Not Committed (Even for Teams)

**Solo Developer:**
- Workspace is personal working memory
- Not committed (unnecessary)
- Backed up (protects active work)

**Team (5 developers):**
- 5 × 10MB = 50MB of markdown
- 1,250 design docs
- 500 analysis reports
- 750 scratch notes

**Problems if Committed:**
- **Merge conflicts from hell** - Every design doc conflicts
- **Cognitive overload** - Which analysis is correct?
- **AI confusion** - 5 different recommendations
- **Git pollution** - Repo becomes unusable

**Solution:**
- Workspace stays local (each developer's own)
- Specs are shared (structured, reviewed)
- No collision, no chaos

**Workspace = Your local IDE's unsaved files**
- ❌ Don't commit unsaved files (chaos)
- ✅ Backup unsaved files (your work matters)

---

## Appendix B: Comparison with Install Script

### Install Script (Clean Slate)

**File:** `install-praxis-os.py`

**8-Step Process:**
1. Prerequisites - Git, Python 3.9+, disk space
2. Clone - Shallow clone to temp dir
3. Create Directories - Full structure
4. Copy Files - Workflows, standards, ouroboros, scripts, config
5. Create Venv - Isolated venv with dependencies
6. Configure .gitignore - Add prAxIs OS patterns
7. Schedule RAG Index - Create `.rebuild_index` flag
8. Validate - Check structure, file counts

**Key Characteristics:**
- ✅ Clean slate (no existing installation)
- ✅ Simple copy (no delete)
- ✅ Full structure created
- ✅ Venv always created
- ✅ Gitignore additive

### Upgrade Script (Existing Installation)

**File:** `upgrade-praxis-os.py`

**8-Phase Process:**
0. Pre-Flight - Check existing installation
1. Backup - Create timestamped backup
2. Clone Source - Clone or use local source
3. Upgrade Files - **DELETE then COPY** (dangerous)
4. Config Reconciliation - Stage `.new` config
5. Dependencies - Update requirements.txt
6. Rebuild Index - Create `.rebuild_indexes` flag
7. Validation - Check file counts, imports, config
8. Cleanup - Remove temp clone, archive backups

**Key Characteristics:**
- ⚠️ Existing installation (must preserve user data)
- ⚠️ Delete + Copy (dangerous if source missing)
- ⚠️ Selective backup (excludes ephemeral data)
- ⚠️ Rollback (can restore from backup)
- ⚠️ Config staging (doesn't overwrite user config)

### Key Differences

| Aspect | Install | Upgrade |
|--------|---------|---------|
| **Target** | Clean slate | Existing installation |
| **User Data** | None | Workspace, specs, standards |
| **Venv** | Always create | Preserve or rebuild |
| **Config** | Copy template | Stage for reconciliation |
| **Rollback** | N/A | Must restore + rebuild |
| **Safety** | Simple | Complex |

---

## Appendix C: Test Scenarios

### Success Cases

1. **Clean Upgrade** - No config changes, all files upgrade successfully
2. **Config Changes** - New config staged, user reconciles
3. **Workspace Preserved** - Design docs, analysis preserved after upgrade
4. **Venv Preserved** - Existing venv works after upgrade

### Failure Cases

1. **Source Missing** - Source directory doesn't exist, upgrade aborts
2. **Copy Failure** - Disk full, copy fails, rollback triggered
3. **Validation Failure** - File counts mismatch, rollback triggered
4. **Network Failure** - Git clone fails, upgrade aborts

### Rollback Cases

1. **Workspace Restored** - All design docs present after rollback
2. **Venv Rebuilt** - MCP server starts after rollback
3. **Specs Restored** - All specs present after rollback
4. **Standards Restored** - All standards present after rollback
5. **Config Restored** - User config preserved after rollback

### Edge Cases

1. **Multiple Upgrades** - Multiple versioned configs don't conflict
2. **Large Workspace** - 100MB+ workspace backs up successfully
3. **Slow Network** - Venv rebuild completes despite slow pip install
4. **Disk Full** - Backup fails gracefully with clear error

---

## Appendix D: Error Messages

### Before (Unclear)

```
✗ Copy failed: [Errno 2] No such file or directory: '/path/to/source'
```

### After (Actionable)

```
✗ Source directory does not exist: /path/to/source
  Cannot proceed with upgrade. Verify source path is correct.
  
  Troubleshooting:
  1. Check that source repository is cloned
  2. Verify path in command: ../praxis-os/
  3. Ensure dist/ directory exists in source
  
  Rollback: Your installation has been restored from backup.
```

---

## Appendix E: Validation Checklist

### Pre-Upgrade Validation

- [ ] prAxIs OS directory exists
- [ ] Ouroboros directory exists
- [ ] Python version >= 3.9
- [ ] Git is installed
- [ ] Disk space >= 500MB
- [ ] **NEW:** Disk space sufficient for backup (workspace + specs + standards)
- [ ] No breaking changes detected

### Post-Upgrade Validation

- [ ] File counts match expected
- [ ] Python imports work
- [ ] Config file exists and readable
- [ ] Checksums verified
- [ ] **NEW:** Workspace files present
- [ ] **NEW:** Venv exists and functional
- [ ] **NEW:** MCP server starts

### Rollback Validation

- [ ] Backup restored successfully
- [ ] **NEW:** Workspace files restored
- [ ] **NEW:** Venv rebuilt
- [ ] **NEW:** MCP server starts
- [ ] All user data intact

---

**End of Design Document**

**Next Steps:**
1. Review this design with stakeholders
2. Create formal spec (Phase 2)
3. Implement changes (Phase 3)
4. Test thoroughly
5. Deploy to production

**Questions or Feedback:**
- Contact: Josh Paul
- AI Assistant: Claude (Sonnet 4.5)
- Date: 2025-11-15

