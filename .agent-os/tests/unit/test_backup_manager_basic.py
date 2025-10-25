"""
Basic unit tests for BackupManager.

Tests the backup creation and verification functionality.
"""

import time
from pathlib import Path

import pytest

from mcp_server.backup_manager import BackupIntegrityError, BackupManager


@pytest.fixture
def backup_manager(tmp_path):
    """Create BackupManager with temporary directory."""
    return BackupManager(base_path=tmp_path)


@pytest.fixture
def mock_agent_os_dir(tmp_path):
    """Create a mock .agent-os directory structure."""
    agent_os = tmp_path / ".agent-os"
    agent_os.mkdir(exist_ok=True)

    # Create mock directories
    (agent_os / "mcp_server").mkdir()
    (agent_os / "standards").mkdir()
    (agent_os / "usage").mkdir()
    (agent_os / "workflows").mkdir()

    # Create mock files
    (agent_os / "config.json").write_text('{"test": "config"}')
    (agent_os / "mcp_server" / "test.py").write_text('print("test")')
    (agent_os / "standards" / "readme.md").write_text("# Standards")

    return agent_os


def test_backup_manager_init(backup_manager):
    """Test BackupManager initialization."""
    assert backup_manager.backup_dir.exists()
    assert backup_manager.backup_dir.name == ".backups"


def test_create_backup_structure(backup_manager, mock_agent_os_dir):
    """Test backup creation creates proper structure."""
    result = backup_manager.create_backup()

    # Check result structure
    assert "backup_path" in result
    assert "backup_timestamp" in result
    assert "files_backed_up" in result
    assert "backup_size_bytes" in result
    assert "backup_manifest" in result
    assert "integrity_verified" in result

    # Check backup was created
    backup_path = Path(result["backup_path"])
    assert backup_path.exists()
    assert backup_path.is_dir()

    # Check MANIFEST.json exists
    manifest_path = backup_path / "MANIFEST.json"
    assert manifest_path.exists()


def test_backup_integrity_verification(backup_manager, mock_agent_os_dir):
    """Test backup integrity verification."""
    result = backup_manager.create_backup()
    backup_path = Path(result["backup_path"])

    # Verify integrity
    integrity_ok = backup_manager.verify_backup_integrity(backup_path)
    assert integrity_ok is True


def test_list_backups(backup_manager, mock_agent_os_dir):
    """Test listing available backups."""
    # Create two backups with delay to ensure different timestamps
    backup_manager.create_backup()
    time.sleep(1.1)  # Ensure different timestamp
    backup_manager.create_backup()

    # List backups
    backups = backup_manager.list_backups()

    assert len(backups) >= 2
    assert all("path" in b for b in backups)
    assert all("timestamp" in b for b in backups)


def test_archive_old_backups(backup_manager, mock_agent_os_dir):
    """Test archiving old backups."""
    # Create multiple backups with delays
    for i in range(5):
        backup_manager.create_backup()
        if i < 4:  # Don't delay after last one
            time.sleep(1.1)  # Ensure different timestamps

    # Archive, keeping only 2
    result = backup_manager.archive_old_backups(keep=2)

    assert result["archived_count"] >= 3
    assert len(result["kept_backups"]) == 2

    # Verify only 2 remain
    backups = backup_manager.list_backups()
    assert len(backups) == 2


def test_get_latest_backup(backup_manager, mock_agent_os_dir):
    """Test getting the latest backup."""
    # Create backups with delay to ensure different timestamps
    backup_manager.create_backup()
    time.sleep(1.1)  # Ensure different timestamp
    result2 = backup_manager.create_backup()

    # Get latest
    latest = backup_manager.get_latest_backup()

    assert latest is not None
    assert str(latest) == result2["backup_path"]


def test_backup_manager_with_empty_target(backup_manager):
    """Test backup manager handles empty target gracefully."""
    # Create backup with no .agent-os content
    result = backup_manager.create_backup()

    # Should still create backup structure
    assert "backup_path" in result
    assert result["files_backed_up"] >= 0


def test_phase_evidence_models():
    """Test that upgrade evidence models can be created."""
    from mcp_server.models import Phase0Evidence, Phase1Evidence

    # Test Phase 0 evidence
    phase0 = Phase0Evidence(
        source_path="/test/path",
        source_version="1.0.0",
        source_commit="abc123",
        source_git_clean=True,
        target_exists=True,
        target_structure_valid=True,
        disk_space_available="10 GB",
        disk_space_required="5 GB",
        no_concurrent_workflows=True,
    )

    assert phase0.source_path == "/test/path"
    assert phase0.source_git_clean is True

    # Test serialization
    phase0_dict = phase0.to_dict()
    assert phase0_dict["source_path"] == "/test/path"

    # Test deserialization
    phase0_restored = Phase0Evidence.from_dict(phase0_dict)
    assert phase0_restored.source_path == "/test/path"

    # Test Phase 1 evidence
    phase1 = Phase1Evidence(
        backup_path="/backup/path",
        backup_timestamp="2025-10-09",
        files_backed_up=100,
        backup_size_bytes=1024,
        backup_manifest="/backup/manifest.json",
        integrity_verified=True,
        lock_acquired=True,
    )

    assert phase1.files_backed_up == 100
    assert phase1.integrity_verified is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
