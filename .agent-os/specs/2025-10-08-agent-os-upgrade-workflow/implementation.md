# Implementation Guide

## Agent OS Upgrade Workflow

**Version:** 1.0  
**Date:** 2025-10-08  
**Status:** Implementation Guidance  
**Workflow ID:** `agent_os_upgrade_v1`

---

## 1. Implementation Philosophy

### Core Principles

1. **State First:** Always persist state before risky operations
2. **Fail Fast:** Catch problems early with pre-flight checks
3. **Rollback Always:** Every failure can be recovered from
4. **Clear Feedback:** Users know what's happening at each step
5. **Atomic Operations:** Use temp files + rename for critical writes

### Development Approach

- **Test-Driven:** Write tests before implementation
- **Incremental:** Build one phase at a time
- **Dogfood Early:** Test on real environments frequently
- **Document As You Go:** Don't leave docs for the end

---

## 2. Code Patterns

### 2.1 State Persistence Pattern

**Use Case:** Saving workflow state to survive server restart

**Implementation:**

```python
# mcp_server/state_manager.py

import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional
import tempfile
import os

class StateManager:
    """Manages persistent workflow state."""
    
    STATE_DIR = Path(".agent-os/.cache/state/")
    
    def __init__(self):
        self.STATE_DIR.mkdir(parents=True, exist_ok=True)
    
    def create_session(
        self,
        workflow_type: str,
        target_file: str,
        metadata: dict
    ) -> str:
        """
        Create new workflow session.
        
        Example:
            session_id = state_mgr.create_session(
                workflow_type="agent_os_upgrade_v1",
                target_file="mcp_server",
                metadata={"source_path": "/path/to/source"}
            )
        """
        session_id = str(uuid.uuid4())
        
        state = {
            "session_id": session_id,
            "workflow_type": workflow_type,
            "target_file": target_file,
            "current_phase": 0,
            "completed_phases": [],
            "phase_artifacts": {},
            "metadata": metadata,
            "started_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self._atomic_write(session_id, state)
        return session_id
    
    def _atomic_write(self, session_id: str, state: dict) -> None:
        """
        Atomically write state to disk.
        
        Pattern: Write to temp file, then rename.
        This ensures state is never corrupted mid-write.
        """
        state_path = self.STATE_DIR / f"{session_id}.json"
        
        # Write to temporary file first
        with tempfile.NamedTemporaryFile(
            mode='w',
            dir=self.STATE_DIR,
            delete=False,
            suffix='.tmp'
        ) as tmp:
            json.dump(state, tmp, indent=2)
            tmp_path = tmp.name
        
        # Atomic rename (POSIX guarantee)
        os.rename(tmp_path, state_path)
    
    def load_state(self, session_id: str) -> dict:
        """
        Load workflow state from disk.
        
        Critical for resume after server restart.
        """
        state_path = self.STATE_DIR / f"{session_id}.json"
        
        if not state_path.exists():
            raise StateNotFoundError(f"Session {session_id} not found")
        
        try:
            with open(state_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise StateCorruptedError(f"State corrupted: {e}")
    
    def update_phase(
        self,
        session_id: str,
        phase: int,
        artifacts: dict
    ) -> None:
        """
        Update current phase and save artifacts.
        """
        state = self.load_state(session_id)
        
        state["current_phase"] = phase
        state["completed_phases"].append(phase - 1)
        state["phase_artifacts"][str(phase - 1)] = artifacts
        state["updated_at"] = datetime.now().isoformat()
        
        self._atomic_write(session_id, state)


class StateNotFoundError(Exception):
    """Raised when session state not found."""
    pass


class StateCorruptedError(Exception):
    """Raised when state JSON is corrupted."""
    pass
```

**Key Takeaways:**
- Use `tempfile` + `os.rename()` for atomic writes
- Always include timestamps for debugging
- Handle missing/corrupted state gracefully
- Use structured exceptions

---

### 2.2 Backup with Checksum Pattern

**Use Case:** Creating verifiable backups

**Implementation:**

```python
# mcp_server/backup_manager.py

import shutil
import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import Dict

class BackupManager:
    """Manages backup creation and verification."""
    
    BACKUP_DIR = Path(".agent-os/.backups/")
    
    def create_backup(self) -> Dict:
        """
        Create timestamped backup with checksum manifest.
        
        Returns:
            {
                "backup_path": str,
                "files_backed_up": int,
                "backup_size_bytes": int,
                "manifest_path": str
            }
        """
        # Create timestamped backup directory
        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        backup_path = self.BACKUP_DIR / timestamp
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # Backup critical directories and files
        directories = [
            "mcp_server",
            "standards",
            "usage",
            "workflows"
        ]
        files = ["config.json"]
        
        total_size = 0
        file_count = 0
        
        for dir_name in directories:
            source = Path(".agent-os") / dir_name
            if source.exists():
                dest = backup_path / dir_name
                shutil.copytree(source, dest)
                file_count += sum(1 for _ in dest.rglob("*") if _.is_file())
                total_size += sum(
                    f.stat().st_size 
                    for f in dest.rglob("*") 
                    if f.is_file()
                )
        
        for file_name in files:
            source = Path(".agent-os") / file_name
            if source.exists():
                dest = backup_path / file_name
                shutil.copy2(source, dest)
                file_count += 1
                total_size += dest.stat().st_size
        
        # Generate checksum manifest
        manifest = self._generate_manifest(backup_path)
        manifest_path = backup_path / "MANIFEST.json"
        
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        return {
            "backup_path": str(backup_path),
            "files_backed_up": file_count,
            "backup_size_bytes": total_size,
            "manifest_path": str(manifest_path)
        }
    
    def _generate_manifest(self, backup_path: Path) -> Dict:
        """
        Generate SHA256 checksums for all files.
        """
        manifest = {
            "timestamp": datetime.now().isoformat(),
            "files": {}
        }
        
        for file_path in backup_path.rglob("*"):
            if file_path.is_file() and file_path.name != "MANIFEST.json":
                relative_path = str(file_path.relative_to(backup_path))
                checksum = self._sha256_file(file_path)
                manifest["files"][relative_path] = checksum
        
        return manifest
    
    @staticmethod
    def _sha256_file(file_path: Path) -> str:
        """Calculate SHA256 hash of file."""
        sha256 = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        
        return sha256.hexdigest()
    
    def verify_backup_integrity(self, backup_path: Path) -> bool:
        """
        Verify backup integrity using manifest checksums.
        
        Returns True if all files match checksums.
        """
        manifest_path = backup_path / "MANIFEST.json"
        
        if not manifest_path.exists():
            return False
        
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        for relative_path, expected_checksum in manifest["files"].items():
            file_path = backup_path / relative_path
            
            if not file_path.exists():
                return False
            
            actual_checksum = self._sha256_file(file_path)
            if actual_checksum != expected_checksum:
                return False
        
        return True
    
    def restore_from_backup(self, backup_path: Path) -> None:
        """
        Restore installation from backup.
        
        Used for rollback operation.
        """
        # Verify integrity first
        if not self.verify_backup_integrity(backup_path):
            raise BackupIntegrityError("Backup integrity check failed")
        
        # Restore directories
        directories = ["mcp_server", "standards", "usage", "workflows"]
        
        for dir_name in directories:
            source = backup_path / dir_name
            if source.exists():
                dest = Path(".agent-os") / dir_name
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(source, dest)
        
        # Restore files
        files = ["config.json"]
        
        for file_name in files:
            source = backup_path / file_name
            if source.exists():
                dest = Path(".agent-os") / file_name
                shutil.copy2(source, dest)


class BackupIntegrityError(Exception):
    """Raised when backup integrity check fails."""
    pass
```

**Key Takeaways:**
- Always generate checksums for verification
- Use SHA256 for file integrity
- Verify before restore
- Structure manifest as JSON

---

### 2.3 Validation with Structured Results Pattern

**Use Case:** Validating system state with clear feedback

**Implementation:**

```python
# mcp_server/validation_module.py

import subprocess
import shutil
from pathlib import Path
from typing import Dict

class ValidationModule:
    """Validates system state at various checkpoints."""
    
    @staticmethod
    def validate_source_repo(source_path: str) -> Dict:
        """
        Validate source repository.
        
        Example result:
            {
                "valid": True,
                "path_exists": True,
                "is_agent_os_repo": True,
                "git_clean": True,
                "version": "1.2.0",
                "commit": "abc123def",
                "errors": []
            }
        """
        result = {
            "valid": False,
            "path_exists": False,
            "is_agent_os_repo": False,
            "git_clean": False,
            "version": None,
            "commit": None,
            "errors": []
        }
        
        source = Path(source_path)
        
        # Check path exists
        if not source.exists():
            result["errors"].append(f"Path does not exist: {source_path}")
            return result
        
        result["path_exists"] = True
        
        # Check is agent-os-enhanced repo
        if not (source / "mcp_server").exists():
            result["errors"].append("Not an agent-os-enhanced repository")
            return result
        
        result["is_agent_os_repo"] = True
        
        # Check git status
        try:
            git_result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=source,
                capture_output=True,
                text=True,
                check=True
            )
            
            if git_result.stdout.strip():
                result["errors"].append("Git repository has uncommitted changes")
                return result
            
            result["git_clean"] = True
            
        except subprocess.CalledProcessError as e:
            result["errors"].append(f"Git check failed: {e}")
            return result
        
        # Extract version
        version_file = source / "VERSION.txt"
        if version_file.exists():
            result["version"] = version_file.read_text().strip()
        
        # Extract commit hash
        try:
            commit_result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=source,
                capture_output=True,
                text=True,
                check=True
            )
            result["commit"] = commit_result.stdout.strip()[:10]
        except subprocess.CalledProcessError:
            pass
        
        # All checks passed
        result["valid"] = True
        return result
    
    @staticmethod
    def check_disk_space(
        path: str = ".agent-os/",
        required_multiplier: float = 2.0
    ) -> Dict:
        """
        Check available disk space.
        
        Example result:
            {
                "sufficient": True,
                "available_bytes": 2684354560,
                "required_bytes": 524288000,
                "available_gb": "2.5",
                "required_gb": "0.5"
            }
        """
        disk = shutil.disk_usage(path)
        
        # Calculate current size
        current_size = sum(
            f.stat().st_size 
            for f in Path(path).rglob("*") 
            if f.is_file()
        )
        
        required = int(current_size * required_multiplier)
        
        return {
            "sufficient": disk.free > required,
            "available_bytes": disk.free,
            "required_bytes": required,
            "available_gb": f"{disk.free / 1e9:.1f}",
            "required_gb": f"{required / 1e9:.1f}"
        }
    
    @staticmethod
    def check_server_health() -> Dict:
        """
        Check MCP server health after restart.
        
        Example result:
            {
                "healthy": True,
                "responding": True,
                "tools_registered": 8,
                "response_time_ms": 125
            }
        """
        import time
        import requests
        
        start = time.time()
        
        try:
            # Try to connect to server (adjust URL as needed)
            # This is a placeholder - actual implementation depends on
            # how MCP server exposes health check
            
            # For now, assume server is healthy if this module loads
            result = {
                "healthy": True,
                "responding": True,
                "tools_registered": 8,  # Would query actual tools
                "response_time_ms": int((time.time() - start) * 1000)
            }
            
        except Exception as e:
            result = {
                "healthy": False,
                "responding": False,
                "error": str(e)
            }
        
        return result
```

**Key Takeaways:**
- Return structured dicts, not booleans
- Include error messages for failures
- Provide both raw and human-readable values
- Use subprocess for external commands
- Handle errors gracefully

---

### 2.4 Workflow Engine Phase Execution Pattern

**Use Case:** Orchestrating phase execution with validation gates

**Implementation:**

```python
# mcp_server/workflow_engine.py (additions)

from typing import Dict, Optional
from .state_manager import StateManager
from .validation_module import ValidationModule
from .backup_manager import BackupManager

class WorkflowEngine:
    """Orchestrates workflow execution."""
    
    def __init__(self):
        self.state_manager = StateManager()
        self.validator = ValidationModule()
        self.backup_manager = BackupManager()
    
    def complete_phase(
        self,
        session_id: str,
        phase: int,
        evidence: Dict
    ) -> Dict:
        """
        Validate evidence and advance to next phase.
        
        Example:
            result = engine.complete_phase(
                session_id="abc-123",
                phase=0,
                evidence={
                    "source_path": "/path/to/source",
                    "source_git_clean": True,
                    ...
                }
            )
        """
        # Load current state
        state = self.state_manager.load_state(session_id)
        
        if state["current_phase"] != phase:
            raise PhaseError(
                f"Expected phase {state['current_phase']}, got {phase}"
            )
        
        # Validate evidence against phase requirements
        validation_result = self._validate_phase_evidence(phase, evidence)
        
        if not validation_result["passed"]:
            return {
                "checkpoint_passed": False,
                "phase_completed": phase,
                "errors": validation_result["errors"],
                "missing_evidence": validation_result["missing"]
            }
        
        # Update state
        self.state_manager.update_phase(
            session_id=session_id,
            phase=phase + 1,
            artifacts=evidence
        )
        
        # Load next phase content
        next_phase_content = self._load_phase_content(phase + 1)
        
        return {
            "checkpoint_passed": True,
            "phase_completed": phase,
            "next_phase": phase + 1,
            "next_phase_content": next_phase_content
        }
    
    def _validate_phase_evidence(
        self,
        phase: int,
        evidence: Dict
    ) -> Dict:
        """
        Validate evidence against phase-specific requirements.
        
        Returns:
            {
                "passed": bool,
                "errors": list,
                "missing": list
            }
        """
        # Define required evidence for each phase
        requirements = {
            0: [
                "source_path",
                "source_git_clean",
                "target_exists",
                "disk_space_available",
                "no_concurrent_workflows"
            ],
            1: [
                "backup_path",
                "files_backed_up",
                "integrity_verified",
                "lock_acquired"
            ],
            # ... more phases
        }
        
        required = requirements.get(phase, [])
        missing = [k for k in required if k not in evidence]
        errors = []
        
        # Additional validation logic here
        if phase == 0:
            if not evidence.get("source_git_clean"):
                errors.append("Source repository has uncommitted changes")
        
        return {
            "passed": len(missing) == 0 and len(errors) == 0,
            "errors": errors,
            "missing": missing
        }
    
    def get_workflow_state(self, session_id: str) -> Dict:
        """
        Resume workflow from persisted state.
        
        Critical for resuming after server restart.
        
        Example:
            state = engine.get_workflow_state("abc-123")
            print(f"Resume from phase {state['current_phase']}")
        """
        state = self.state_manager.load_state(session_id)
        
        # Add current phase content for resume
        state["phase_content"] = self._load_phase_content(
            state["current_phase"]
        )
        
        return state


class PhaseError(Exception):
    """Raised when phase execution error occurs."""
    pass
```

**Key Takeaways:**
- Validate evidence before advancing
- Provide clear error messages
- Use state manager for persistence
- Return next phase content immediately
- Handle phase mismatches

---

## 3. Testing Strategy

### 3.1 Unit Testing Approach

**Philosophy:** Mock external dependencies, test logic in isolation.

**Example: Testing State Manager**

```python
# tests/unit/test_state_manager.py

import pytest
import json
from pathlib import Path
from mcp_server.state_manager import StateManager, StateNotFoundError

@pytest.fixture
def temp_state_dir(tmp_path):
    """Create temporary state directory."""
    state_dir = tmp_path / ".agent-os" / ".cache" / "state"
    state_dir.mkdir(parents=True)
    return state_dir

@pytest.fixture
def state_manager(temp_state_dir, monkeypatch):
    """Create StateManager with temporary directory."""
    monkeypatch.setattr(
        "mcp_server.state_manager.StateManager.STATE_DIR",
        temp_state_dir
    )
    return StateManager()

def test_create_session(state_manager):
    """Test session creation."""
    session_id = state_manager.create_session(
        workflow_type="agent_os_upgrade_v1",
        target_file="mcp_server",
        metadata={"source_path": "/test/path"}
    )
    
    assert session_id is not None
    assert len(session_id) == 36  # UUID length
    
    # Verify state file created
    state_file = state_manager.STATE_DIR / f"{session_id}.json"
    assert state_file.exists()
    
    # Verify state content
    with open(state_file) as f:
        state = json.load(f)
    
    assert state["session_id"] == session_id
    assert state["workflow_type"] == "agent_os_upgrade_v1"
    assert state["current_phase"] == 0
    assert state["completed_phases"] == []

def test_load_state(state_manager):
    """Test loading state from disk."""
    # Create session
    session_id = state_manager.create_session(
        workflow_type="test_workflow",
        target_file="test",
        metadata={}
    )
    
    # Load state
    state = state_manager.load_state(session_id)
    
    assert state["session_id"] == session_id
    assert state["workflow_type"] == "test_workflow"

def test_load_nonexistent_state(state_manager):
    """Test loading non-existent state raises error."""
    with pytest.raises(StateNotFoundError):
        state_manager.load_state("nonexistent-id")

def test_update_phase(state_manager):
    """Test updating phase and artifacts."""
    # Create session
    session_id = state_manager.create_session(
        workflow_type="test_workflow",
        target_file="test",
        metadata={}
    )
    
    # Update to phase 1
    artifacts = {"backup_path": "/test/backup"}
    state_manager.update_phase(session_id, 1, artifacts)
    
    # Load and verify
    state = state_manager.load_state(session_id)
    
    assert state["current_phase"] == 1
    assert 0 in state["completed_phases"]
    assert state["phase_artifacts"]["0"] == artifacts

def test_atomic_write_doesnt_corrupt(state_manager, monkeypatch):
    """Test that atomic write prevents corruption."""
    # Create session
    session_id = state_manager.create_session(
        workflow_type="test_workflow",
        target_file="test",
        metadata={}
    )
    
    # Simulate crash during write by raising exception
    original_rename = os.rename
    call_count = [0]
    
    def failing_rename(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 2:  # Fail on second call
            raise Exception("Simulated crash")
        return original_rename(*args, **kwargs)
    
    monkeypatch.setattr("os.rename", failing_rename)
    
    # Try to update (will fail)
    with pytest.raises(Exception):
        state_manager.update_phase(session_id, 1, {})
    
    # Original state should still be intact
    state = state_manager.load_state(session_id)
    assert state["current_phase"] == 0  # Not updated
```

**Coverage Target:** > 90% for StateManager

---

### 3.2 Integration Testing Approach

**Philosophy:** Test component interactions in realistic scenarios.

**Example: Testing Phase 0-1 Execution**

```python
# tests/integration/test_upgrade_phases_0_1.py

import pytest
import shutil
from pathlib import Path
from mcp_server.workflow_engine import WorkflowEngine
from mcp_server.validation_module import ValidationModule

@pytest.fixture
def test_environment(tmp_path):
    """Create test environment with source and target."""
    # Create source repo
    source = tmp_path / "source"
    source.mkdir()
    (source / "mcp_server").mkdir()
    (source / "VERSION.txt").write_text("1.2.0")
    
    # Initialize git
    subprocess.run(["git", "init"], cwd=source, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=source,
        check=True
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=source,
        check=True
    )
    subprocess.run(["git", "add", "."], cwd=source, check=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial"],
        cwd=source,
        check=True
    )
    
    # Create target
    target = tmp_path / ".agent-os"
    target.mkdir()
    (target / "mcp_server").mkdir()
    (target / "config.json").write_text("{}")
    
    return {"source": source, "target": target}

def test_phases_0_1_happy_path(test_environment):
    """Test successful execution of Phases 0 and 1."""
    engine = WorkflowEngine()
    
    # Start workflow
    session_id = engine.start_workflow(
        workflow_type="agent_os_upgrade_v1",
        target_file="mcp_server",
        options={"source_path": str(test_environment["source"])}
    )["session_id"]
    
    # Complete Phase 0 (Pre-Flight)
    phase_0_evidence = {
        "source_path": str(test_environment["source"]),
        "source_git_clean": True,
        "target_exists": True,
        "disk_space_available": "10 GB",
        "no_concurrent_workflows": True
    }
    
    result = engine.complete_phase(session_id, 0, phase_0_evidence)
    
    assert result["checkpoint_passed"]
    assert result["next_phase"] == 1
    
    # Complete Phase 1 (Backup)
    # ... backup operations ...
    
    phase_1_evidence = {
        "backup_path": ".agent-os/.backups/2025-10-08-100000/",
        "files_backed_up": 100,
        "integrity_verified": True,
        "lock_acquired": True
    }
    
    result = engine.complete_phase(session_id, 1, phase_1_evidence)
    
    assert result["checkpoint_passed"]
    assert result["next_phase"] == 2
    
    # Verify backup exists
    backup_path = Path(phase_1_evidence["backup_path"])
    assert backup_path.exists()
    assert (backup_path / "MANIFEST.json").exists()
    
    # Verify lock file
    assert Path(".agent-os/.upgrade-lock").exists()
```

---

### 3.3 Testing Checklist

**Before committing code:**

- [ ] All unit tests pass
- [ ] Code coverage > 85%
- [ ] Integration tests pass
- [ ] Linting passes (flake8, mypy)
- [ ] No print statements (use logging)
- [ ] Error paths tested
- [ ] Edge cases covered

---

## 4. Deployment Guidance

### 4.1 File Organization

```
mcp_server/
├── backup_manager.py          (NEW)
├── validation_module.py       (NEW)
├── dependency_installer.py    (NEW)
├── server_manager.py          (NEW)
├── report_generator.py        (NEW)
├── state_manager.py           (MODIFIED)
├── workflow_engine.py         (MODIFIED)
└── models/
    └── upgrade_models.py      (NEW)

universal/workflows/
└── agent_os_upgrade_v1/
    ├── metadata.json
    ├── phases/
    │   ├── 0-pre-flight-checks.md
    │   ├── 1-backup-preparation.md
    │   ├── 2-content-upgrade.md
    │   ├── 3-mcp-server-upgrade.md
    │   ├── 4-post-upgrade-validation.md
    │   └── 5-cleanup-documentation.md
    └── supporting-docs/
        ├── rollback-procedure.md
        ├── troubleshooting.md
        └── validation-criteria.md

tests/
├── unit/
│   ├── test_state_manager_enhanced.py
│   ├── test_backup_manager.py
│   ├── test_validation_module.py
│   ├── test_dependency_installer.py
│   ├── test_server_manager.py
│   ├── test_report_generator.py
│   └── test_upgrade_models.py
└── integration/
    ├── test_upgrade_phases_0_1.py
    ├── test_upgrade_with_restart.py
    ├── test_full_upgrade_workflow.py
    └── test_rollback_scenarios.py
```

---

### 4.2 Deployment Steps

**Step 1: Deploy Core Components (Week 1)**

```bash
# Create new component files
touch mcp_server/backup_manager.py
touch mcp_server/validation_module.py
touch mcp_server/dependency_installer.py
touch mcp_server/server_manager.py
touch mcp_server/report_generator.py
touch mcp_server/models/upgrade_models.py

# Write implementations (follow code patterns above)

# Run tests
pytest tests/unit/ -v --cov=mcp_server --cov-report=term-missing

# Coverage should be > 85%
```

**Step 2: Create Workflow Structure (Week 1)**

```bash
# Create workflow directory
mkdir -p universal/workflows/agent_os_upgrade_v1/{phases,supporting-docs}

# Create metadata.json
cat > universal/workflows/agent_os_upgrade_v1/metadata.json << 'EOF'
{
  "name": "agent_os_upgrade_v1",
  "version": "1.0.0",
  ...
}
EOF

# Create phase markdown files
# (Write each phase file following three-tier architecture)
```

**Step 3: Integration Testing (Week 2-4)**

```bash
# Run integration tests
pytest tests/integration/ -v

# Test with server restart simulation
pytest tests/integration/test_upgrade_with_restart.py -v

# Test rollback scenarios
pytest tests/integration/test_rollback_scenarios.py -v
```

**Step 4: Dogfooding (Week 4-5)**

```bash
# Test on agent-os-enhanced itself
# (Manual test, documented in Task 5.1)

# Test on customer project
# (Manual test, documented in Task 5.2)

# Refine based on feedback
# (Task 5.3)
```

**Step 5: Documentation & Release (Week 5)**

```bash
# Create user documentation
# Update guides
# Prepare release notes

# Final verification
pytest tests/ -v --cov=mcp_server --cov-report=html

# Tag release
git tag -a v1.0.0 -m "Agent OS Upgrade Workflow v1.0.0"
```

---

### 4.3 Rollout Strategy

**Phase 1: Internal Testing (Week 4)**
- Test on agent-os-enhanced dev environment
- Fix critical issues
- Document edge cases

**Phase 2: Beta Testing (Week 5)**
- Release to select users
- Gather feedback
- Monitor for issues

**Phase 3: General Availability (Week 6)**
- Announce to all users
- Update documentation
- Provide migration guide

---

## 5. Troubleshooting Guide

### 5.1 Common Issues

#### Issue 1: State File Corrupted

**Symptoms:**
```
StateCorruptedError: State corrupted: Expecting value: line 1 column 1 (char 0)
```

**Cause:** State file partially written (disk full, crash during write)

**Solution:**
```bash
# Check if temp file exists
ls .agent-os/.cache/state/*.tmp

# If temp file exists, it may have valid data
# Manually inspect and rename if valid

# Otherwise, rollback to last known good state
# (If backup exists from Phase 1)
```

**Prevention:** Atomic writes (already implemented)

---

#### Issue 2: Backup Integrity Check Fails

**Symptoms:**
```
BackupIntegrityError: Backup integrity check failed
```

**Cause:** File corruption, disk issues, partial backup

**Solution:**
```bash
# Check backup manifest
cat .agent-os/.backups/2025-10-08-100000/MANIFEST.json

# Manually verify checksums
sha256sum .agent-os/.backups/2025-10-08-100000/mcp_server/workflow_engine.py

# If corruption confirmed, use previous backup
ls -la .agent-os/.backups/

# Rollback to older backup if available
```

**Prevention:**
- Verify backup immediately after creation
- Keep multiple backups (Phase 5 archives old ones)

---

#### Issue 3: Server Won't Restart After Phase 3

**Symptoms:**
```
Server health check failed after 30 seconds
```

**Cause:** Dependency issues, port already in use, configuration error

**Solution:**
```bash
# Check if server process is running
ps aux | grep "python -m mcp_server"

# Check if port is in use
lsof -i :PORT_NUMBER

# Check server logs
tail -f .agent-os/logs/mcp_server.log

# Manual restart
cd .agent-os
python -m mcp_server

# If error, rollback
# (Workflow should auto-rollback if health check fails)
```

**Prevention:**
- Health check with timeout
- Automatic rollback on failure (implemented in Phase 3)

---

#### Issue 4: Disk Space Exhausted

**Symptoms:**
```
OSError: [Errno 28] No space left on device
```

**Cause:** Insufficient disk space, pre-flight check missed

**Solution:**
```bash
# Check disk space
df -h .agent-os/

# Free up space
rm -rf .agent-os/.backups/OLD_BACKUP/
rm -rf /tmp/*

# Re-run upgrade
```

**Prevention:**
- Pre-flight check (Phase 0) should catch this
- If check failed, improve disk space calculation

---

### 5.2 Debugging Tips

**Enable Debug Logging:**

```python
import logging

logging.basicConfig(level=logging.DEBUG)
```

**Inspect State:**

```bash
# View current state
cat .agent-os/.cache/state/SESSION_ID.json | jq

# View phase artifacts
cat .agent-os/.cache/state/SESSION_ID.json | jq '.phase_artifacts'
```

**Trace Execution:**

```python
# Add strategic logging
logger.debug(f"Phase {phase} starting")
logger.debug(f"Evidence: {evidence}")
logger.debug(f"State before: {state}")
# ... operation ...
logger.debug(f"State after: {new_state}")
```

**Verify File Operations:**

```bash
# Check backup exists
ls -la .agent-os/.backups/

# Verify checksums
cat .agent-os/.backups/2025-10-08-100000/MANIFEST.json | jq

# Check lock file
cat .agent-os/.upgrade-lock
```

---

### 5.3 Recovery Procedures

**If Upgrade Fails Mid-Phase:**

1. Check current phase: `cat .agent-os/.cache/state/SESSION_ID.json | jq '.current_phase'`
2. If Phase 0-1: No changes made, safe to restart
3. If Phase 2-4: Trigger rollback
4. If Phase 5: Complete manually

**Manual Rollback:**

```bash
# Load backup path from state
BACKUP_PATH=$(cat .agent-os/.cache/state/SESSION_ID.json | jq -r '.phase_artifacts."1".backup_path')

# Stop server
pkill -f "python -m mcp_server"

# Restore files
cp -r $BACKUP_PATH/mcp_server .agent-os/
cp $BACKUP_PATH/config.json .agent-os/

# Restore dependencies (if snapshot exists)
pip install -r $BACKUP_PATH/requirements-snapshot.txt

# Restart server
cd .agent-os
python -m mcp_server &

# Verify
sleep 5
curl localhost:PORT/health  # Adjust as needed
```

---

## 6. Performance Optimization

### 6.1 Bottleneck Identification

**Profile Slow Operations:**

```python
import time
import cProfile
import pstats

def profile_operation(func):
    """Decorator to profile function."""
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        
        profiler.disable()
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')
        stats.print_stats(10)
        
        print(f"{func.__name__} took {duration:.2f}s")
        return result
    
    return wrapper

@profile_operation
def create_backup():
    # ... backup code ...
```

**Common Bottlenecks:**
- Checksum calculation (large files)
- File copying (many files)
- Dependency installation (network bound)

---

### 6.2 Optimization Strategies

**1. Parallel Checksum Calculation:**

```python
from concurrent.futures import ThreadPoolExecutor

def generate_manifest_parallel(backup_path: Path) -> Dict:
    """Generate checksums using thread pool."""
    files = list(backup_path.rglob("*"))
    files = [f for f in files if f.is_file()]
    
    manifest = {"files": {}}
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(_sha256_file, f): f 
            for f in files
        }
        
        for future in futures:
            file_path = futures[future]
            checksum = future.result()
            relative = str(file_path.relative_to(backup_path))
            manifest["files"][relative] = checksum
    
    return manifest
```

**2. Delta Backups (Future v1.1):**

Only backup changed files, compare with last backup.

**3. Async Archival (Future v1.1):**

Archive old backups in background during Phase 5.

---

## 7. Security Considerations

### 7.1 Input Validation

**Always validate user input:**

```python
def validate_source_path(source_path: str) -> None:
    """Validate source path for security."""
    path = Path(source_path).resolve()
    
    # Prevent directory traversal
    if ".." in str(path):
        raise SecurityError("Path traversal not allowed")
    
    # Must be absolute path
    if not path.is_absolute():
        raise SecurityError("Must provide absolute path")
    
    # Must exist
    if not path.exists():
        raise SecurityError("Path does not exist")
```

---

### 7.2 File Operation Safety

**Stay within boundaries:**

```python
def safe_file_operation(target_path: str) -> None:
    """Ensure file operations stay within .agent-os/."""
    target = Path(target_path).resolve()
    base = Path(".agent-os").resolve()
    
    try:
        target.relative_to(base)
    except ValueError:
        raise SecurityError("Operation outside .agent-os/ not allowed")
```

---

## 8. Best Practices Checklist

**Before submitting code:**

- [ ] Follows code patterns from this guide
- [ ] All edge cases handled
- [ ] Error messages are clear and actionable
- [ ] Logging at appropriate levels
- [ ] Unit tests written (> 85% coverage)
- [ ] Integration tests pass
- [ ] Type hints added
- [ ] Docstrings complete
- [ ] No hardcoded paths
- [ ] Security checks in place
- [ ] Performance acceptable
- [ ] Code reviewed

---

## 9. References

- [srd.md](srd.md) - Requirements
- [specs.md](specs.md) - Technical Design
- [tasks.md](tasks.md) - Implementation Tasks
- [supporting-docs/](supporting-docs/) - Additional Documentation

---

## Approval & Sign-Off

| Role | Name | Date | Status |
|------|------|------|--------|
| Implementation Guide Author | AI Assistant | 2025-10-08 | ✅ Complete |
| Reviewer | TBD | TBD | ⏳ Pending |
| Approver | Josh (Human) | TBD | ⏳ Pending |

---

**Status:** ✅ Implementation Guide Complete  
**Next Phase:** Phase 5 - Final Review & Polish

