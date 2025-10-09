"""
Integration tests for Agent OS Upgrade Workflow Phases 0-1.

Tests the complete flow from pre-flight checks through backup creation.
"""

import pytest
import json
import subprocess
from pathlib import Path
from mcp_server.backup_manager import BackupManager
from mcp_server.validation_module import ValidationModule
from mcp_server.models import Phase0Evidence, Phase1Evidence


@pytest.fixture
def mock_source_repo(tmp_path):
    """Create a complete mock source repository."""
    source = tmp_path / "agent-os-enhanced"
    source.mkdir()
    
    # Create required directories
    (source / "mcp_server").mkdir()
    (source / "universal").mkdir()
    (source / "universal" / "standards").mkdir()
    (source / "universal" / "usage").mkdir()
    (source / "universal" / "workflows").mkdir()
    
    # Create VERSION.txt
    (source / "VERSION.txt").write_text("1.0.0")
    
    # Create some content files
    (source / "universal" / "standards" / "test.md").write_text("# Test Standard")
    (source / "universal" / "usage" / "guide.md").write_text("# Usage Guide")
    
    # Initialize git
    subprocess.run(["git", "init"], cwd=source, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=source,
        capture_output=True
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=source,
        capture_output=True
    )
    subprocess.run(["git", "add", "."], cwd=source, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=source,
        capture_output=True
    )
    
    return source


@pytest.fixture
def mock_target_installation(tmp_path):
    """Create a complete mock .agent-os installation."""
    target = tmp_path / "project" / ".agent-os"
    target.mkdir(parents=True)
    
    # Create required directories
    (target / "mcp_server").mkdir()
    (target / "standards").mkdir()
    (target / "usage").mkdir()
    (target / "workflows").mkdir()
    
    # Create config.json
    config = {
        "version": "0.9.0",
        "features": {
            "browser_tools": True,
            "rag_search": True
        }
    }
    (target / "config.json").write_text(json.dumps(config, indent=2))
    
    # Create some existing content
    (target / "mcp_server" / "__init__.py").write_text("# MCP Server")
    (target / "standards" / "existing.md").write_text("# Existing Standard")
    
    return target


class TestPhase0PreFlightChecks:
    """Test Phase 0: Pre-Flight Checks."""
    
    def test_complete_phase_0_validation(self, mock_source_repo, mock_target_installation):
        """Test complete Phase 0 pre-flight validation."""
        validator = ValidationModule()
        
        # Task 1: Validate source repository
        source_result = validator.validate_source_repo(str(mock_source_repo))
        assert source_result["valid"] is True
        assert source_result["git_clean"] is True
        assert source_result["version"] == "1.0.0"
        
        # Task 2: Validate target structure
        target_result = validator.validate_target_structure(str(mock_target_installation))
        assert target_result["valid"] is True
        assert all(target_result["required_dirs"].values())
        
        # Task 3: Check disk space
        disk_result = validator.check_disk_space(str(mock_target_installation))
        assert disk_result["sufficient"] is True
        
        # Task 4: Check for concurrent upgrades
        lock_file = mock_target_installation.parent / ".upgrade-lock"
        concurrent_result = validator.check_for_concurrent_upgrades(str(lock_file))
        assert concurrent_result["no_concurrent_workflows"] is True
        
        # Collect Phase 0 evidence
        phase0_evidence = Phase0Evidence(
            source_path=str(mock_source_repo),
            source_version=source_result["version"],
            source_commit=source_result["commit"],
            source_git_clean=source_result["git_clean"],
            target_exists=target_result["target_exists"],
            target_structure_valid=target_result["valid"],
            disk_space_available=disk_result["available_gb"],
            disk_space_required=disk_result["required_gb"],
            no_concurrent_workflows=concurrent_result["no_concurrent_workflows"]
        )
        
        # Verify evidence can be serialized
        evidence_dict = phase0_evidence.to_dict()
        assert evidence_dict["source_version"] == "1.0.0"
        assert evidence_dict["source_git_clean"] is True
    
    def test_phase_0_fails_on_dirty_git(self, mock_source_repo, mock_target_installation):
        """Test Phase 0 fails when source has uncommitted changes."""
        # Create uncommitted file
        (mock_source_repo / "uncommitted.txt").write_text("test")
        
        validator = ValidationModule()
        source_result = validator.validate_source_repo(str(mock_source_repo))
        
        assert source_result["valid"] is False
        assert source_result["git_clean"] is False
        # Phase 0 should not proceed


class TestPhase1BackupPreparation:
    """Test Phase 1: Backup & Preparation."""
    
    def test_complete_phase_1_backup(self, mock_target_installation):
        """Test complete Phase 1 backup creation."""
        backup_mgr = BackupManager(base_path=mock_target_installation.parent)
        
        # Task 1: Create timestamped backup
        backup_result = backup_mgr.create_backup()
        assert "backup_path" in backup_result
        assert backup_result["files_backed_up"] > 0
        assert backup_result["backup_size_bytes"] > 0
        
        backup_path = Path(backup_result["backup_path"])
        assert backup_path.exists()
        
        # Task 2: Verify backup integrity
        integrity_ok = backup_mgr.verify_backup_integrity(backup_path)
        assert integrity_ok is True
        
        # Task 3: Acquire upgrade lock
        lock_file = mock_target_installation.parent / ".upgrade-lock"
        lock_data = {
            "session_id": "test-session-123",
            "started_at": "2025-10-09T10:00:00Z",
            "backup_path": str(backup_path)
        }
        lock_file.write_text(json.dumps(lock_data, indent=2))
        assert lock_file.exists()
        
        # Collect Phase 1 evidence
        phase1_evidence = Phase1Evidence(
            backup_path=backup_result["backup_path"],
            backup_timestamp=backup_result["backup_timestamp"],
            files_backed_up=backup_result["files_backed_up"],
            backup_size_bytes=backup_result["backup_size_bytes"],
            backup_manifest=backup_result["backup_manifest"],
            integrity_verified=integrity_ok,
            lock_acquired=lock_file.exists()
        )
        
        # Verify evidence can be serialized
        evidence_dict = phase1_evidence.to_dict()
        assert evidence_dict["files_backed_up"] > 0
        assert evidence_dict["integrity_verified"] is True
        assert evidence_dict["lock_acquired"] is True
    
    def test_backup_preserves_all_content(self, mock_target_installation):
        """Test that backup includes all required content."""
        backup_mgr = BackupManager(base_path=mock_target_installation.parent)
        backup_result = backup_mgr.create_backup()
        backup_path = Path(backup_result["backup_path"])
        
        # Verify all directories were backed up
        assert (backup_path / "mcp_server").exists()
        assert (backup_path / "standards").exists()
        assert (backup_path / "usage").exists()
        assert (backup_path / "workflows").exists()
        
        # Verify config was backed up
        assert (backup_path / "config.json").exists()
        
        # Verify manifest was created
        assert (backup_path / "MANIFEST.json").exists()


class TestPhases0And1Integration:
    """Integration tests combining Phases 0 and 1."""
    
    def test_complete_phases_0_and_1_flow(self, mock_source_repo, mock_target_installation):
        """Test complete flow through Phases 0 and 1."""
        validator = ValidationModule()
        backup_mgr = BackupManager(base_path=mock_target_installation.parent)
        
        # === PHASE 0: Pre-Flight Checks ===
        
        # Validate source
        source_result = validator.validate_source_repo(str(mock_source_repo))
        assert source_result["valid"] is True, "Phase 0 source validation failed"
        
        # Validate target
        target_result = validator.validate_target_structure(str(mock_target_installation))
        assert target_result["valid"] is True, "Phase 0 target validation failed"
        
        # Check disk space
        disk_result = validator.check_disk_space(str(mock_target_installation))
        assert disk_result["sufficient"] is True, "Phase 0 disk space check failed"
        
        # Check no concurrent upgrades
        lock_file = mock_target_installation.parent / ".upgrade-lock"
        concurrent_result = validator.check_for_concurrent_upgrades(str(lock_file))
        assert concurrent_result["no_concurrent_workflows"] is True, "Phase 0 concurrent check failed"
        
        # Create Phase 0 evidence
        phase0_evidence = Phase0Evidence(
            source_path=str(mock_source_repo),
            source_version=source_result["version"],
            source_commit=source_result["commit"],
            source_git_clean=source_result["git_clean"],
            target_exists=target_result["target_exists"],
            target_structure_valid=target_result["valid"],
            disk_space_available=disk_result["available_gb"],
            disk_space_required=disk_result["required_gb"],
            no_concurrent_workflows=concurrent_result["no_concurrent_workflows"]
        )
        
        # === PHASE 1: Backup & Preparation ===
        
        # Create backup
        backup_result = backup_mgr.create_backup()
        assert backup_result["files_backed_up"] > 0, "Phase 1 backup creation failed"
        
        backup_path = Path(backup_result["backup_path"])
        
        # Verify integrity
        integrity_ok = backup_mgr.verify_backup_integrity(backup_path)
        assert integrity_ok is True, "Phase 1 backup integrity check failed"
        
        # Acquire lock
        lock_data = {
            "session_id": "test-session-123",
            "started_at": "2025-10-09T10:00:00Z",
            "backup_path": str(backup_path),
            "source_version": phase0_evidence.source_version
        }
        lock_file.write_text(json.dumps(lock_data, indent=2))
        
        # Create Phase 1 evidence
        phase1_evidence = Phase1Evidence(
            backup_path=backup_result["backup_path"],
            backup_timestamp=backup_result["backup_timestamp"],
            files_backed_up=backup_result["files_backed_up"],
            backup_size_bytes=backup_result["backup_size_bytes"],
            backup_manifest=backup_result["backup_manifest"],
            integrity_verified=integrity_ok,
            lock_acquired=lock_file.exists()
        )
        
        # === VERIFY COMPLETE FLOW ===
        
        # Both phases should have valid evidence
        assert phase0_evidence.source_git_clean is True
        assert phase0_evidence.target_structure_valid is True
        assert phase1_evidence.integrity_verified is True
        assert phase1_evidence.lock_acquired is True
        
        # Backup should be retrievable
        latest_backup = backup_mgr.get_latest_backup()
        assert latest_backup == backup_path
        
        # Lock should contain Phase 0 information
        lock_content = json.loads(lock_file.read_text())
        assert lock_content["source_version"] == "1.0.0"
    
    def test_rollback_capability_after_phase_1(self, mock_target_installation):
        """Test that rollback is possible after Phase 1."""
        backup_mgr = BackupManager(base_path=mock_target_installation.parent)
        
        # Create initial backup
        backup_result = backup_mgr.create_backup()
        backup_path = Path(backup_result["backup_path"])
        
        # Simulate some changes to target (as if Phase 2 started)
        (mock_target_installation / "mcp_server" / "new_file.py").write_text("# New file")
        
        # Verify backup can restore
        backup_mgr.restore_from_backup(backup_path)
        
        # Verify new file is gone (restored to backup state)
        assert not (mock_target_installation / "mcp_server" / "new_file.py").exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

