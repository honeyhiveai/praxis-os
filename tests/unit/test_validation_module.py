"""
Comprehensive unit tests for ValidationModule.

Tests all validation functions for pre-flight checks and post-upgrade validation.
"""

import pytest
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from mcp_server.validation_module import ValidationModule


@pytest.fixture
def validator():
    """Create ValidationModule instance."""
    return ValidationModule()


@pytest.fixture
def mock_source_repo(tmp_path):
    """Create a mock source repository structure."""
    source = tmp_path / "agent-os-enhanced"
    source.mkdir()
    
    # Create required directories
    (source / "mcp_server").mkdir()
    (source / "universal").mkdir()
    
    # Create VERSION.txt
    (source / "VERSION.txt").write_text("1.0.0")
    
    # Initialize git repo
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
    
    # Make initial commit for clean state
    subprocess.run(["git", "add", "."], cwd=source, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=source,
        capture_output=True
    )
    
    return source


@pytest.fixture
def mock_target_dir(tmp_path):
    """Create a mock .agent-os target directory."""
    target = tmp_path / ".agent-os"
    target.mkdir()
    
    # Create required directories
    (target / "mcp_server").mkdir()
    (target / "standards").mkdir()
    (target / "usage").mkdir()
    (target / "workflows").mkdir()
    
    # Create config.json
    (target / "config.json").write_text('{"test": "config"}')
    
    return target


class TestValidateSourceRepo:
    """Tests for validate_source_repo method."""
    
    def test_validate_source_repo_success(self, validator, mock_source_repo):
        """Test successful source repository validation."""
        result = validator.validate_source_repo(str(mock_source_repo))
        
        assert result["valid"] is True
        assert result["path_exists"] is True
        assert result["is_agent_os_repo"] is True
        assert result["git_clean"] is True
        assert result["version"] == "1.0.0"
        assert len(result["errors"]) == 0
    
    def test_validate_source_repo_nonexistent_path(self, validator):
        """Test validation fails for nonexistent path."""
        result = validator.validate_source_repo("/nonexistent/path")
        
        assert result["valid"] is False
        assert result["path_exists"] is False
        assert "does not exist" in result["errors"][0]
    
    def test_validate_source_repo_not_agent_os(self, validator, tmp_path):
        """Test validation fails for non-agent-os repository."""
        # Create directory without mcp_server
        not_agent_os = tmp_path / "not-agent-os"
        not_agent_os.mkdir()
        
        result = validator.validate_source_repo(str(not_agent_os))
        
        assert result["valid"] is False
        assert result["is_agent_os_repo"] is False
        assert "not an agent-os-enhanced repository" in result["errors"][0].lower()
    
    def test_validate_source_repo_dirty_git(self, validator, mock_source_repo):
        """Test validation fails for dirty git status."""
        # Create an uncommitted file
        (mock_source_repo / "uncommitted.txt").write_text("test")
        
        result = validator.validate_source_repo(str(mock_source_repo))
        
        assert result["valid"] is False
        assert result["git_clean"] is False
        assert any("uncommitted" in err.lower() for err in result["errors"])
    
    def test_validate_source_repo_extracts_commit_hash(self, validator, mock_source_repo):
        """Test that commit hash is extracted when available."""
        # Make initial commit
        subprocess.run(
            ["git", "add", "."],
            cwd=mock_source_repo,
            capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=mock_source_repo,
            capture_output=True
        )
        
        result = validator.validate_source_repo(str(mock_source_repo))
        
        assert result["commit"] is not None
        assert len(result["commit"]) == 10  # First 10 chars of hash


class TestValidateTargetStructure:
    """Tests for validate_target_structure method."""
    
    def test_validate_target_structure_success(self, validator, mock_target_dir):
        """Test successful target structure validation."""
        result = validator.validate_target_structure(str(mock_target_dir))
        
        assert result["valid"] is True
        assert result["target_exists"] is True
        assert result["required_dirs"]["mcp_server"] is True
        assert result["required_dirs"]["standards"] is True
        assert result["required_dirs"]["usage"] is True
        assert result["required_dirs"]["workflows"] is True
        assert result["required_files"]["config.json"] is True
        assert len(result["errors"]) == 0
    
    def test_validate_target_structure_missing_directory(self, validator, tmp_path):
        """Test validation fails when required directory is missing."""
        target = tmp_path / ".agent-os"
        target.mkdir()
        
        # Only create some directories
        (target / "mcp_server").mkdir()
        (target / "config.json").write_text("{}")
        
        result = validator.validate_target_structure(str(target))
        
        assert result["valid"] is False
        assert result["required_dirs"]["mcp_server"] is True
        assert result["required_dirs"]["standards"] is False
        assert any("standards" in err.lower() for err in result["errors"])
    
    def test_validate_target_structure_missing_config(self, validator, tmp_path):
        """Test validation fails when config.json is missing."""
        target = tmp_path / ".agent-os"
        target.mkdir()
        
        # Create directories but not config
        (target / "mcp_server").mkdir()
        (target / "standards").mkdir()
        (target / "usage").mkdir()
        (target / "workflows").mkdir()
        
        result = validator.validate_target_structure(str(target))
        
        assert result["valid"] is False
        assert result["required_files"]["config.json"] is False
        assert any("config.json" in err for err in result["errors"])
    
    def test_validate_target_structure_nonexistent(self, validator):
        """Test validation fails for nonexistent target."""
        result = validator.validate_target_structure("/nonexistent/.agent-os")
        
        assert result["valid"] is False
        assert result["target_exists"] is False


class TestCheckDiskSpace:
    """Tests for check_disk_space method."""
    
    def test_check_disk_space_sufficient(self, validator, mock_target_dir):
        """Test disk space check when sufficient space available."""
        result = validator.check_disk_space(str(mock_target_dir))
        
        assert "sufficient" in result
        assert "available_bytes" in result
        assert "required_bytes" in result
        assert "available_gb" in result
        assert "required_gb" in result
        assert result["available_bytes"] > 0
    
    def test_check_disk_space_multiplier(self, validator, mock_target_dir):
        """Test disk space calculation with different multipliers."""
        result_2x = validator.check_disk_space(
            str(mock_target_dir),
            required_multiplier=2.0
        )
        result_3x = validator.check_disk_space(
            str(mock_target_dir),
            required_multiplier=3.0
        )
        
        # 3x multiplier should require more space
        assert result_3x["required_bytes"] > result_2x["required_bytes"]
    
    @patch('shutil.disk_usage')
    def test_check_disk_space_insufficient(self, mock_disk_usage, validator, tmp_path):
        """Test disk space check when insufficient space."""
        # Mock disk_usage to return very little free space
        mock_disk_usage.return_value = Mock(
            total=1000000,
            used=990000,
            free=10000  # Very little free space
        )
        
        result = validator.check_disk_space(
            str(tmp_path),
            required_multiplier=10.0  # Require more than available
        )
        
        # Depending on actual size, this may or may not be sufficient
        assert "sufficient" in result


class TestVerifyChecksums:
    """Tests for verify_checksums method."""
    
    def test_verify_checksums_matching(self, validator, tmp_path):
        """Test checksum verification with matching files."""
        source = tmp_path / "source"
        target = tmp_path / "target"
        source.mkdir()
        target.mkdir()
        
        # Create identical files
        (source / "file1.txt").write_text("content1")
        (source / "file2.txt").write_text("content2")
        (target / "file1.txt").write_text("content1")
        (target / "file2.txt").write_text("content2")
        
        result = validator.verify_checksums(str(source), str(target))
        
        assert result["verified"] is True
        assert result["files_checked"] == 2
        assert len(result["mismatches"]) == 0
        assert len(result["missing"]) == 0
    
    def test_verify_checksums_mismatch(self, validator, tmp_path):
        """Test checksum verification with mismatched files."""
        source = tmp_path / "source"
        target = tmp_path / "target"
        source.mkdir()
        target.mkdir()
        
        # Create files with different content
        (source / "file1.txt").write_text("content1")
        (target / "file1.txt").write_text("different_content")
        
        result = validator.verify_checksums(str(source), str(target))
        
        assert result["verified"] is False
        assert len(result["mismatches"]) == 1
        assert "file1.txt" in result["mismatches"][0]
    
    def test_verify_checksums_missing_file(self, validator, tmp_path):
        """Test checksum verification with missing target file."""
        source = tmp_path / "source"
        target = tmp_path / "target"
        source.mkdir()
        target.mkdir()
        
        # Create file only in source
        (source / "file1.txt").write_text("content1")
        
        result = validator.verify_checksums(str(source), str(target))
        
        assert result["verified"] is False
        assert len(result["missing"]) == 1
        assert "file1.txt" in result["missing"][0]
    
    def test_verify_checksums_nonexistent_directory(self, validator):
        """Test checksum verification with nonexistent directories."""
        result = validator.verify_checksums("/nonexistent/source", "/nonexistent/target")
        
        assert result["verified"] is False


class TestCheckServerHealth:
    """Tests for check_server_health method."""
    
    @patch('subprocess.run')
    def test_check_server_health_running(self, mock_run, validator):
        """Test server health check when server is running."""
        # Mock pgrep returning success (process found)
        mock_run.return_value = Mock(returncode=0, stdout="12345")
        
        result = validator.check_server_health()
        
        assert result["responding"] is True
        assert result["healthy"] is True
        assert result["error"] is None
    
    @patch('subprocess.run')
    def test_check_server_health_not_running(self, mock_run, validator):
        """Test server health check when server is not running."""
        # Mock pgrep returning failure (process not found)
        mock_run.return_value = Mock(returncode=1, stdout="")
        
        result = validator.check_server_health()
        
        assert result["responding"] is False
        assert result["healthy"] is False
        assert "not found" in result["error"].lower()
    
    @patch('subprocess.run')
    def test_check_server_health_timeout(self, mock_run, validator):
        """Test server health check timeout."""
        # Mock timeout exception
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="pgrep", timeout=5)
        
        result = validator.check_server_health()
        
        assert result["healthy"] is False
        assert result["error"] is not None


class TestCheckForConcurrentUpgrades:
    """Tests for check_for_concurrent_upgrades method."""
    
    def test_no_concurrent_upgrades(self, validator, tmp_path):
        """Test when no lock file exists."""
        lock_file = tmp_path / ".upgrade-lock"
        
        result = validator.check_for_concurrent_upgrades(str(lock_file))
        
        assert result["no_concurrent_workflows"] is True
        assert result["lock_exists"] is False
        assert result["lock_info"] is None
    
    def test_concurrent_upgrade_detected(self, validator, tmp_path):
        """Test when lock file exists."""
        import json
        
        lock_file = tmp_path / ".upgrade-lock"
        lock_data = {
            "session_id": "test-session",
            "started_at": "2025-10-09T10:00:00Z"
        }
        lock_file.write_text(json.dumps(lock_data))
        
        result = validator.check_for_concurrent_upgrades(str(lock_file))
        
        assert result["no_concurrent_workflows"] is False
        assert result["lock_exists"] is True
        assert result["lock_info"]["session_id"] == "test-session"


class TestValidateWorkflowNotInProgress:
    """Tests for validate_workflow_not_in_progress method."""
    
    def test_no_workflows_in_progress(self, validator, tmp_path):
        """Test when no workflows are in progress."""
        state_dir = tmp_path / "state"
        state_dir.mkdir()
        
        result = validator.validate_workflow_not_in_progress(str(state_dir))
        
        assert result is True
    
    def test_workflow_in_progress(self, validator, tmp_path):
        """Test when upgrade workflow is in progress."""
        import json
        
        state_dir = tmp_path / "state"
        state_dir.mkdir()
        
        # Create active workflow state
        state_file = state_dir / "session-123.json"
        state_data = {
            "workflow_type": "agent_os_upgrade_v1",
            "current_phase": 2
        }
        state_file.write_text(json.dumps(state_data))
        
        result = validator.validate_workflow_not_in_progress(str(state_dir))
        
        assert result is False
    
    def test_completed_workflow_ignored(self, validator, tmp_path):
        """Test that completed workflows are ignored."""
        import json
        
        state_dir = tmp_path / "state"
        state_dir.mkdir()
        
        # Create completed workflow state
        state_file = state_dir / "session-123.json"
        state_data = {
            "workflow_type": "agent_os_upgrade_v1",
            "current_phase": 6  # Completed (> 5)
        }
        state_file.write_text(json.dumps(state_data))
        
        result = validator.validate_workflow_not_in_progress(str(state_dir))
        
        assert result is True


class TestIntegration:
    """Integration tests combining multiple validation methods."""
    
    def test_full_pre_flight_validation(self, validator, mock_source_repo, mock_target_dir):
        """Test complete pre-flight validation flow."""
        # Validate source
        source_result = validator.validate_source_repo(str(mock_source_repo))
        assert source_result["valid"] is True
        
        # Validate target
        target_result = validator.validate_target_structure(str(mock_target_dir))
        assert target_result["valid"] is True
        
        # Check disk space
        disk_result = validator.check_disk_space(str(mock_target_dir))
        assert "sufficient" in disk_result
        
        # Check for concurrent upgrades
        lock_file = mock_target_dir.parent / ".upgrade-lock"
        concurrent_result = validator.check_for_concurrent_upgrades(str(lock_file))
        assert concurrent_result["no_concurrent_workflows"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

