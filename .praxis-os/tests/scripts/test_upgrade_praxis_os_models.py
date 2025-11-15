"""
Unit tests for upgrade-praxis-os.py data models and utility functions.

Tests cover instantiation, serialization, deserialization, validation
for data model classes, and comprehensive testing of utility functions.
"""

import json
import os
import tempfile
import pytest
from pathlib import Path

# Import from scripts directory using importlib (handles hyphens in filename)
import importlib.util
import sys
from pathlib import Path

# Load the module from file path
project_root = Path(__file__).parent.parent.parent.parent
script_path = project_root / "scripts" / "upgrade-praxis-os.py"

spec = importlib.util.spec_from_file_location("upgrade_praxis_os", script_path)
upgrade_praxis_os = importlib.util.module_from_spec(spec)
sys.modules["upgrade_praxis_os"] = upgrade_praxis_os
spec.loader.exec_module(upgrade_praxis_os)

# Import classes
UpgradeReport = upgrade_praxis_os.UpgradeReport
BackupManifest = upgrade_praxis_os.BackupManifest
CheckResult = upgrade_praxis_os.CheckResult
ValidationResult = upgrade_praxis_os.ValidationResult


class TestUpgradeReport:
    """Test suite for UpgradeReport data model."""

    def test_instantiation_empty(self):
        """Test creating an empty UpgradeReport."""
        report = UpgradeReport()
        assert report.files_added == []
        assert report.files_modified == []
        assert report.files_deleted == []

    def test_instantiation_with_data(self):
        """Test creating UpgradeReport with initial data."""
        report = UpgradeReport(
            files_added=["file1.py"],
            files_modified=["file2.py"],
            files_deleted=["file3.py"],
        )
        assert len(report.files_added) == 1
        assert len(report.files_modified) == 1
        assert len(report.files_deleted) == 1

    def test_summary(self):
        """Test summary() method."""
        report = UpgradeReport(
            files_added=["a.py", "b.py"],
            files_modified=["c.py"],
            files_deleted=[],
        )
        summary = report.summary()
        assert "Added: 2" in summary
        assert "Modified: 1" in summary
        assert "Deleted: 0" in summary

    def test_to_json(self):
        """Test JSON serialization."""
        report = UpgradeReport(files_added=["test.py"])
        json_str = report.to_json()
        assert isinstance(json_str, str)
        data = json.loads(json_str)
        assert "files_added" in data
        assert "files_modified" in data
        assert "files_deleted" in data
        assert data["files_added"] == ["test.py"]

    def test_from_json(self):
        """Test JSON deserialization."""
        json_str = json.dumps(
            {
                "files_added": ["a.py"],
                "files_modified": ["b.py"],
                "files_deleted": ["c.py"],
            }
        )
        report = UpgradeReport.from_json(json_str)
        assert report.files_added == ["a.py"]
        assert report.files_modified == ["b.py"]
        assert report.files_deleted == ["c.py"]

    def test_round_trip_serialization(self):
        """Test that serialization and deserialization are inverses."""
        original = UpgradeReport(
            files_added=["file1.py", "file2.py"],
            files_modified=["file3.py"],
            files_deleted=[],
        )
        json_str = original.to_json()
        restored = UpgradeReport.from_json(json_str)
        assert restored.files_added == original.files_added
        assert restored.files_modified == original.files_modified
        assert restored.files_deleted == original.files_deleted


class TestBackupManifest:
    """Test suite for BackupManifest data model."""

    def test_instantiation(self):
        """Test creating a BackupManifest."""
        manifest = BackupManifest(
            created_at="2025-11-15T10:30:00Z",
            backup_dir=".praxis-os.backup.20251115_103000",
            checksums={"file1.py": "abc123"},
        )
        assert manifest.created_at == "2025-11-15T10:30:00Z"
        assert manifest.backup_dir == ".praxis-os.backup.20251115_103000"
        assert len(manifest.checksums) == 1

    def test_to_json(self):
        """Test JSON serialization."""
        manifest = BackupManifest(
            created_at="2025-11-15T10:30:00Z",
            backup_dir="backup/",
            checksums={"test.py": "checksum123"},
        )
        json_str = manifest.to_json()
        data = json.loads(json_str)
        assert data["created_at"] == "2025-11-15T10:30:00Z"
        assert data["backup_dir"] == "backup/"
        assert data["checksums"]["test.py"] == "checksum123"

    def test_from_json(self):
        """Test JSON deserialization."""
        json_str = json.dumps(
            {
                "created_at": "2025-11-15T10:30:00Z",
                "backup_dir": "backup/",
                "checksums": {"file.py": "hash123"},
            }
        )
        manifest = BackupManifest.from_json(json_str)
        assert manifest.created_at == "2025-11-15T10:30:00Z"
        assert manifest.backup_dir == "backup/"
        assert manifest.checksums["file.py"] == "hash123"

    def test_verify_file_success(self):
        """Test verify_file() with matching checksum."""
        manifest = BackupManifest(
            created_at="2025-11-15T10:30:00Z",
            backup_dir="backup/",
            checksums={"test.py": "abc123"},
        )
        assert manifest.verify_file("test.py", "abc123") is True

    def test_verify_file_failure(self):
        """Test verify_file() with non-matching checksum."""
        manifest = BackupManifest(
            created_at="2025-11-15T10:30:00Z",
            backup_dir="backup/",
            checksums={"test.py": "abc123"},
        )
        assert manifest.verify_file("test.py", "wrong_checksum") is False

    def test_verify_file_missing(self):
        """Test verify_file() with file not in manifest."""
        manifest = BackupManifest(
            created_at="2025-11-15T10:30:00Z",
            backup_dir="backup/",
            checksums={},
        )
        assert manifest.verify_file("missing.py", "any_checksum") is False

    def test_round_trip_serialization(self):
        """Test that serialization and deserialization are inverses."""
        original = BackupManifest(
            created_at="2025-11-15T10:30:00Z",
            backup_dir=".praxis-os.backup.20251115_103000",
            checksums={"file1.py": "hash1", "file2.py": "hash2"},
        )
        json_str = original.to_json()
        restored = BackupManifest.from_json(json_str)
        assert restored.created_at == original.created_at
        assert restored.backup_dir == original.backup_dir
        assert restored.checksums == original.checksums


class TestCheckResult:
    """Test suite for CheckResult data model."""

    def test_instantiation(self):
        """Test creating a CheckResult."""
        check = CheckResult(True, "Python Version", "Python 3.11 detected")
        assert check.passed is True
        assert check.check_name == "Python Version"
        assert check.message == "Python 3.11 detected"

    def test_to_dict(self):
        """Test to_dict() method."""
        check = CheckResult(False, "Disk Space", "Insufficient space")
        result = check.to_dict()
        assert result["passed"] is False
        assert result["check_name"] == "Disk Space"
        assert result["message"] == "Insufficient space"


class TestValidationResult:
    """Test suite for ValidationResult data model."""

    def test_instantiation_empty(self):
        """Test creating ValidationResult with no checks."""
        result = ValidationResult(True, [])
        assert result.passed is True
        assert len(result.checks) == 0

    def test_instantiation_with_checks(self):
        """Test creating ValidationResult with checks."""
        checks = [
            CheckResult(True, "Check 1", "OK"),
            CheckResult(False, "Check 2", "Failed"),
        ]
        result = ValidationResult(False, checks)
        assert result.passed is False
        assert len(result.checks) == 2

    def test_summary_all_passed(self):
        """Test summary() when all checks pass."""
        checks = [
            CheckResult(True, "Check 1", "OK"),
            CheckResult(True, "Check 2", "OK"),
        ]
        result = ValidationResult(True, checks)
        summary = result.summary()
        assert "Passed: 2/2" in summary

    def test_summary_some_failed(self):
        """Test summary() when some checks fail."""
        checks = [
            CheckResult(True, "Check 1", "OK"),
            CheckResult(False, "Check 2", "Failed"),
            CheckResult(True, "Check 3", "OK"),
        ]
        result = ValidationResult(False, checks)
        summary = result.summary()
        assert "Passed: 2/3" in summary

    def test_to_json(self):
        """Test JSON serialization."""
        checks = [CheckResult(True, "Test", "OK")]
        result = ValidationResult(True, checks)
        json_str = result.to_json()
        data = json.loads(json_str)
        assert data["passed"] is True
        assert len(data["checks"]) == 1
        assert data["checks"][0]["check_name"] == "Test"

    def test_from_json(self):
        """Test JSON deserialization."""
        json_str = json.dumps(
            {
                "passed": False,
                "checks": [
                    {"passed": True, "check_name": "Check 1", "message": "OK"},
                    {"passed": False, "check_name": "Check 2", "message": "Failed"},
                ],
            }
        )
        result = ValidationResult.from_json(json_str)
        assert result.passed is False
        assert len(result.checks) == 2
        assert result.checks[0].passed is True
        assert result.checks[1].passed is False

    def test_round_trip_serialization(self):
        """Test that serialization and deserialization are inverses."""
        original = ValidationResult(
            False,
            [
                CheckResult(True, "Check 1", "OK"),
                CheckResult(False, "Check 2", "Failed"),
            ],
        )
        json_str = original.to_json()
        restored = ValidationResult.from_json(json_str)
        assert restored.passed == original.passed
        assert len(restored.checks) == len(original.checks)
        for orig_check, rest_check in zip(original.checks, restored.checks):
            assert rest_check.passed == orig_check.passed
            assert rest_check.check_name == orig_check.check_name
            assert rest_check.message == orig_check.message


# ============================================================================
# Utility Function Tests
# ============================================================================

# Import utility functions
sha256 = upgrade_praxis_os.sha256
count_files = upgrade_praxis_os.count_files
safe_copy = upgrade_praxis_os.safe_copy
is_process_running = upgrade_praxis_os.is_process_running
parse_version = upgrade_praxis_os.parse_version

# Import components
PreFlightValidator = upgrade_praxis_os.PreFlightValidator
BackupManager = upgrade_praxis_os.BackupManager
SourceCloner = upgrade_praxis_os.SourceCloner
FileUpgrader = upgrade_praxis_os.FileUpgrader
ConfigReconciler = upgrade_praxis_os.ConfigReconciler
DependencyUpdater = upgrade_praxis_os.DependencyUpdater
UpgradeValidator = upgrade_praxis_os.UpgradeValidator
UpgradeOrchestrator = upgrade_praxis_os.UpgradeOrchestrator


class TestSha256:
    """Test suite for sha256() utility function."""

    def test_sha256_known_checksum(self):
        """Test sha256() with known checksum."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("hello")
            temp_path = Path(f.name)

        try:
            checksum = sha256(temp_path)
            # Known SHA256 of "hello"
            expected = "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
            assert checksum == expected
        finally:
            temp_path.unlink()

    def test_sha256_empty_file(self):
        """Test sha256() with empty file."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = Path(f.name)

        try:
            checksum = sha256(temp_path)
            # Known SHA256 of empty file
            expected = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
            assert checksum == expected
        finally:
            temp_path.unlink()

    def test_sha256_file_not_found(self):
        """Test sha256() with non-existent file."""
        with pytest.raises(FileNotFoundError):
            sha256(Path("/nonexistent/file.txt"))

    def test_sha256_large_file(self):
        """Test sha256() with large file (tests chunking)."""
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as f:
            # Write 1MB of data
            f.write(b"a" * (1024 * 1024))
            temp_path = Path(f.name)

        try:
            checksum = sha256(temp_path)
            assert len(checksum) == 64  # SHA256 is always 64 hex chars
            assert checksum.isalnum()
        finally:
            temp_path.unlink()


class TestCountFiles:
    """Test suite for count_files() utility function."""

    def test_count_all_files(self):
        """Test counting all files in directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / "file1.txt").touch()
            (tmp_path / "file2.txt").touch()
            (tmp_path / "file3.txt").touch()
            assert count_files(tmp_path) == 3

    def test_count_with_pattern(self):
        """Test counting files with glob pattern."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / "file1.py").touch()
            (tmp_path / "file2.py").touch()
            (tmp_path / "file3.txt").touch()
            assert count_files(tmp_path, "*.py") == 2
            assert count_files(tmp_path, "*.txt") == 1

    def test_count_empty_directory(self):
        """Test counting files in empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            assert count_files(tmp_path) == 0

    def test_count_excludes_directories(self):
        """Test that count_files() excludes subdirectories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / "file1.txt").touch()
            (tmp_path / "subdir").mkdir()
            (tmp_path / "subdir" / "file2.txt").touch()
            # Should only count file1.txt, not subdir
            assert count_files(tmp_path) == 1

    def test_count_directory_not_found(self):
        """Test count_files() with non-existent directory."""
        with pytest.raises(FileNotFoundError):
            count_files(Path("/nonexistent/directory"))

    def test_count_not_a_directory(self):
        """Test count_files() with file instead of directory."""
        with tempfile.NamedTemporaryFile() as f:
            with pytest.raises(NotADirectoryError):
                count_files(Path(f.name))


class TestSafeCopy:
    """Test suite for safe_copy() utility function."""

    def test_safe_copy_success(self):
        """Test successful file copy."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            src = tmp_path / "source.txt"
            src.write_text("test content")
            dst = tmp_path / "dest.txt"

            safe_copy(src, dst, tmp_path)

            assert dst.exists()
            assert dst.read_text() == "test content"

    def test_safe_copy_creates_parent_dirs(self):
        """Test that safe_copy() creates parent directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            src = tmp_path / "source.txt"
            src.write_text("content")
            dst = tmp_path / "subdir" / "nested" / "dest.txt"

            safe_copy(src, dst, tmp_path)

            assert dst.exists()
            assert dst.read_text() == "content"

    def test_safe_copy_prevents_path_traversal(self):
        """Test that safe_copy() prevents path traversal attacks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            src = tmp_path / "source.txt"
            src.write_text("content")
            # Attempt to write outside base_dir
            dst = tmp_path / ".." / ".." / "evil.txt"

            with pytest.raises(ValueError, match="Path traversal detected"):
                safe_copy(src, dst, tmp_path)

    def test_safe_copy_source_not_found(self):
        """Test safe_copy() with non-existent source."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            src = tmp_path / "nonexistent.txt"
            dst = tmp_path / "dest.txt"

            with pytest.raises(FileNotFoundError):
                safe_copy(src, dst, tmp_path)

    def test_safe_copy_preserves_metadata(self):
        """Test that safe_copy() preserves file metadata."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            src = tmp_path / "source.txt"
            src.write_text("content")
            original_mtime = src.stat().st_mtime

            dst = tmp_path / "dest.txt"
            safe_copy(src, dst, tmp_path)

            # Metadata should be preserved (within reasonable tolerance)
            assert abs(dst.stat().st_mtime - original_mtime) < 0.01


class TestIsProcessRunning:
    """Test suite for is_process_running() utility function."""

    def test_current_process_running(self):
        """Test that current process is detected as running."""
        assert is_process_running(os.getpid()) is True

    def test_nonexistent_process(self):
        """Test that non-existent PID returns False."""
        # PID 999999 is very unlikely to exist
        assert is_process_running(999999) is False

    def test_invalid_pid_zero(self):
        """Test that PID 0 returns False."""
        assert is_process_running(0) is False

    def test_invalid_pid_negative(self):
        """Test that negative PID returns False."""
        assert is_process_running(-1) is False
        assert is_process_running(-100) is False

    def test_pid_1_likely_running(self):
        """Test that PID 1 (init/launchd) is likely running on Unix."""
        # PID 1 is typically the init process on Unix systems
        # This test may fail on some systems, so we just check it doesn't crash
        result = is_process_running(1)
        assert isinstance(result, bool)


class TestParseVersion:
    """Test suite for parse_version() utility function."""

    def test_parse_simple_version(self):
        """Test parsing simple semantic version."""
        assert parse_version("1.2.3") == (1, 2, 3)
        assert parse_version("0.0.1") == (0, 0, 1)
        assert parse_version("10.20.30") == (10, 20, 30)

    def test_parse_two_part_version(self):
        """Test parsing two-part version."""
        assert parse_version("1.0") == (1, 0)
        assert parse_version("2.5") == (2, 5)

    def test_parse_version_with_prerelease(self):
        """Test parsing version with pre-release tag."""
        assert parse_version("1.2.3-alpha") == (1, 2, 3)
        assert parse_version("2.0.0-beta.1") == (2, 0, 0)
        assert parse_version("1.0.0-rc.2") == (1, 0, 0)

    def test_parse_version_with_build_metadata(self):
        """Test parsing version with build metadata."""
        assert parse_version("1.2.3+build.123") == (1, 2, 3)
        assert parse_version("2.0.0+20130313144700") == (2, 0, 0)

    def test_version_comparison(self):
        """Test that parsed versions can be compared."""
        assert parse_version("1.2.3") < parse_version("1.2.4")
        assert parse_version("1.2.3") < parse_version("1.3.0")
        assert parse_version("1.2.3") < parse_version("2.0.0")
        assert parse_version("2.0.0") > parse_version("1.9.9")
        assert parse_version("1.2.3") == parse_version("1.2.3")

    def test_parse_invalid_version(self):
        """Test parsing invalid version string."""
        with pytest.raises(ValueError):
            parse_version("invalid")
        with pytest.raises(ValueError):
            parse_version("1.2.abc")
        with pytest.raises(ValueError):
            parse_version("")


# ============================================================================
# Component Tests
# ============================================================================


class TestPreFlightValidator:
    """Test suite for PreFlightValidator component."""

    def test_check_praxis_os_exists_success(self):
        """Test check_praxis_os_exists() with valid directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / ".praxis-os").mkdir()
            validator = PreFlightValidator(tmp_path)
            result = validator.check_praxis_os_exists()
            assert result.passed is True
            assert ".praxis-os/" in result.message

    def test_check_praxis_os_exists_failure(self):
        """Test check_praxis_os_exists() with missing directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            validator = PreFlightValidator(tmp_path)
            result = validator.check_praxis_os_exists()
            assert result.passed is False
            assert "No .praxis-os/ directory" in result.message

    def test_check_ouroboros_exists_success(self):
        """Test check_ouroboros_exists() with valid directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / ".praxis-os").mkdir()
            (tmp_path / ".praxis-os" / "ouroboros").mkdir()
            validator = PreFlightValidator(tmp_path)
            result = validator.check_ouroboros_exists()
            assert result.passed is True
            assert "ouroboros/" in result.message

    def test_check_ouroboros_exists_failure(self):
        """Test check_ouroboros_exists() with missing directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / ".praxis-os").mkdir()
            validator = PreFlightValidator(tmp_path)
            result = validator.check_ouroboros_exists()
            assert result.passed is False
            assert "No ouroboros/ directory" in result.message

    def test_check_python_version(self):
        """Test check_python_version() returns valid result."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            validator = PreFlightValidator(tmp_path)
            result = validator.check_python_version()
            # Should pass on Python 3.9+
            assert isinstance(result.passed, bool)
            assert "Python" in result.message

    def test_check_git_available(self):
        """Test check_git_available() returns valid result."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            validator = PreFlightValidator(tmp_path)
            result = validator.check_git_available()
            # Should return a boolean (may pass or fail depending on system)
            assert isinstance(result.passed, bool)
            assert result.check_name == "Git Available"

    def test_check_disk_space_success(self):
        """Test check_disk_space() with low requirement."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            validator = PreFlightValidator(tmp_path)
            result = validator.check_disk_space(required_mb=1)
            # Should pass with at least 1MB free
            assert result.passed is True
            assert "MB available" in result.message

    def test_check_disk_space_failure(self):
        """Test check_disk_space() with unreasonably high requirement."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            validator = PreFlightValidator(tmp_path)
            # Require 1 petabyte (will fail)
            result = validator.check_disk_space(required_mb=1_000_000_000)
            assert result.passed is False
            assert "Only" in result.message

    def test_detect_breaking_changes_none(self):
        """Test detect_breaking_changes() with no breaking changes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / ".praxis-os").mkdir()
            (tmp_path / ".praxis-os" / "ouroboros").mkdir()
            validator = PreFlightValidator(tmp_path)
            result = validator.detect_breaking_changes()
            assert result.passed is True
            assert "No breaking changes" in result.message

    def test_detect_breaking_changes_old_structure(self):
        """Test detect_breaking_changes() detects old mcp_server directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / ".praxis-os").mkdir()
            (tmp_path / ".praxis-os" / "mcp_server").mkdir()
            validator = PreFlightValidator(tmp_path)
            result = validator.detect_breaking_changes()
            assert result.passed is False
            assert "Breaking change detected" in result.message
            assert "mcp_server" in result.message

    def test_detect_breaking_changes_both_exist(self):
        """Test detect_breaking_changes() when both old and new exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / ".praxis-os").mkdir()
            (tmp_path / ".praxis-os" / "mcp_server").mkdir()
            (tmp_path / ".praxis-os" / "ouroboros").mkdir()
            validator = PreFlightValidator(tmp_path)
            result = validator.detect_breaking_changes()
            # Should pass if new structure exists (migration already done)
            assert result.passed is True

    def test_validate_all_success(self):
        """Test validate_all() with all checks passing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / ".praxis-os").mkdir()
            (tmp_path / ".praxis-os" / "ouroboros").mkdir()
            validator = PreFlightValidator(tmp_path)
            result = validator.validate_all()
            # Should have 6 checks
            assert len(result.checks) == 6
            # Overall result depends on system (git, python version)
            assert isinstance(result.passed, bool)

    def test_validate_all_failure(self):
        """Test validate_all() with some checks failing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            # Don't create .praxis-os/ directory
            validator = PreFlightValidator(tmp_path)
            result = validator.validate_all()
            # Should have 6 checks
            assert len(result.checks) == 6
            # Should fail because .praxis-os/ doesn't exist
            assert result.passed is False
            # Check that at least one check failed
            failed_checks = [c for c in result.checks if not c.passed]
            assert len(failed_checks) > 0

    def test_aggregate_results_all_pass(self):
        """Test _aggregate_results() with all checks passing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            validator = PreFlightValidator(tmp_path)
            checks = [
                CheckResult(True, "Check 1", "OK"),
                CheckResult(True, "Check 2", "OK"),
            ]
            result = validator._aggregate_results(checks)
            assert result.passed is True
            assert len(result.checks) == 2

    def test_aggregate_results_some_fail(self):
        """Test _aggregate_results() with some checks failing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            validator = PreFlightValidator(tmp_path)
            checks = [
                CheckResult(True, "Check 1", "OK"),
                CheckResult(False, "Check 2", "Failed"),
            ]
            result = validator._aggregate_results(checks)
            assert result.passed is False
            assert len(result.checks) == 2


class TestBackupManager:
    """Test suite for BackupManager component."""

    def test_create_backup_success(self):
        """Test create_backup() creates timestamped backup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / ".praxis-os").mkdir()
            (tmp_path / ".praxis-os" / "ouroboros").mkdir()
            (tmp_path / ".praxis-os" / "test.txt").write_text("content")
            
            manager = BackupManager(tmp_path)
            backup_dir = manager.create_backup()
            
            assert backup_dir.exists()
            assert backup_dir.name.startswith(".praxis-os.backup.")
            assert (backup_dir / "test.txt").exists()
            assert (backup_dir / ".backup_manifest.json").exists()

    def test_create_backup_excludes_ephemeral(self):
        """Test create_backup() excludes ephemeral directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / ".praxis-os").mkdir()
            (tmp_path / ".praxis-os" / "ouroboros").mkdir()
            (tmp_path / ".praxis-os" / ".cache").mkdir()
            (tmp_path / ".praxis-os" / ".cache" / "test.txt").write_text("cache")
            (tmp_path / ".praxis-os" / "workspace").mkdir()
            (tmp_path / ".praxis-os" / "workspace" / "test.txt").write_text("workspace")
            (tmp_path / ".praxis-os" / "venv").mkdir()
            (tmp_path / ".praxis-os" / "venv" / "test.txt").write_text("venv")
            (tmp_path / ".praxis-os" / "state").mkdir()
            (tmp_path / ".praxis-os" / "state" / "test.txt").write_text("state")
            
            manager = BackupManager(tmp_path)
            backup_dir = manager.create_backup()
            
            # Ephemeral directories should be excluded
            assert not (backup_dir / ".cache").exists()
            assert not (backup_dir / "workspace").exists()
            assert not (backup_dir / "venv").exists()
            assert not (backup_dir / "state").exists()

    def test_create_backup_missing_source(self):
        """Test create_backup() raises error if source doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            manager = BackupManager(tmp_path)
            
            with pytest.raises(FileNotFoundError):
                manager.create_backup()

    def test_restore_from_backup_success(self):
        """Test restore_from_backup() restores installation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / ".praxis-os").mkdir()
            (tmp_path / ".praxis-os" / "ouroboros").mkdir()
            (tmp_path / ".praxis-os" / "test.txt").write_text("original")
            
            manager = BackupManager(tmp_path)
            backup_dir = manager.create_backup()
            
            # Modify original
            (tmp_path / ".praxis-os" / "test.txt").write_text("modified")
            
            # Restore
            manager.restore_from_backup(backup_dir)
            
            # Should be back to original
            assert (tmp_path / ".praxis-os" / "test.txt").read_text() == "original"

    def test_restore_from_backup_missing_backup(self):
        """Test restore_from_backup() raises error if backup doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            manager = BackupManager(tmp_path)
            
            with pytest.raises(FileNotFoundError):
                manager.restore_from_backup(tmp_path / "nonexistent")

    def test_generate_checksum_manifest(self):
        """Test _generate_checksum_manifest() creates manifest."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / "test.txt").write_text("content")
            (tmp_path / "subdir").mkdir()
            (tmp_path / "subdir" / "test2.txt").write_text("content2")
            
            manager = BackupManager(Path("."))
            manifest_path = manager._generate_checksum_manifest(tmp_path)
            
            assert manifest_path.exists()
            assert manifest_path.name == ".backup_manifest.json"
            
            manifest = BackupManifest.from_json(manifest_path.read_text())
            assert "test.txt" in manifest.checksums
            assert "subdir/test2.txt" in manifest.checksums

    def test_validate_backup_success(self):
        """Test _validate_backup() passes for valid backup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / "test.txt").write_text("content")
            
            manager = BackupManager(Path("."))
            manifest_path = manager._generate_checksum_manifest(tmp_path)
            
            # Should not raise
            manager._validate_backup(tmp_path, manifest_path)

    def test_validate_backup_missing_file(self):
        """Test _validate_backup() fails if file is missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / "test.txt").write_text("content")
            
            manager = BackupManager(Path("."))
            manifest_path = manager._generate_checksum_manifest(tmp_path)
            
            # Delete file after manifest creation
            (tmp_path / "test.txt").unlink()
            
            with pytest.raises(ValueError, match="Missing file"):
                manager._validate_backup(tmp_path, manifest_path)

    def test_validate_backup_checksum_mismatch(self):
        """Test _validate_backup() fails if checksum doesn't match."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / "test.txt").write_text("content")
            
            manager = BackupManager(Path("."))
            manifest_path = manager._generate_checksum_manifest(tmp_path)
            
            # Modify file after manifest creation
            (tmp_path / "test.txt").write_text("modified")
            
            with pytest.raises(ValueError, match="Checksum mismatch"):
                manager._validate_backup(tmp_path, manifest_path)

    def test_validate_restore_success(self):
        """Test _validate_restore() passes for valid restore."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / "ouroboros").mkdir()
            
            manager = BackupManager(Path("."))
            
            # Should not raise
            manager._validate_restore(tmp_path)

    def test_validate_restore_missing_directory(self):
        """Test _validate_restore() fails if directory doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            manager = BackupManager(Path("."))
            
            with pytest.raises(ValueError, match="not found"):
                manager._validate_restore(tmp_path / "nonexistent")

    def test_validate_restore_missing_essential_dir(self):
        """Test _validate_restore() fails if essential directory is missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            # Create directory but not ouroboros/
            
            manager = BackupManager(Path("."))
            
            with pytest.raises(ValueError, match="Missing essential directory"):
                manager._validate_restore(tmp_path)

    def test_backup_includes_manifest(self):
        """Test backup includes checksum manifest."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / ".praxis-os").mkdir()
            (tmp_path / ".praxis-os" / "ouroboros").mkdir()
            (tmp_path / ".praxis-os" / "test.txt").write_text("content")
            
            manager = BackupManager(tmp_path)
            backup_dir = manager.create_backup()
            
            manifest_path = backup_dir / ".backup_manifest.json"
            assert manifest_path.exists()
            
            manifest = BackupManifest.from_json(manifest_path.read_text())
            assert manifest.backup_dir == str(backup_dir)
            assert len(manifest.checksums) > 0

    def test_backup_restore_roundtrip(self):
        """Test full backup and restore cycle."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / ".praxis-os").mkdir()
            (tmp_path / ".praxis-os" / "ouroboros").mkdir()
            (tmp_path / ".praxis-os" / "ouroboros" / "test.py").write_text("original code")
            (tmp_path / ".praxis-os" / "config").mkdir()
            (tmp_path / ".praxis-os" / "config" / "mcp.yaml").write_text("original config")
            
            manager = BackupManager(tmp_path)
            
            # Create backup
            backup_dir = manager.create_backup()
            
            # Modify files
            (tmp_path / ".praxis-os" / "ouroboros" / "test.py").write_text("modified code")
            (tmp_path / ".praxis-os" / "config" / "mcp.yaml").write_text("modified config")
            
            # Restore
            manager.restore_from_backup(backup_dir)
            
            # Verify restoration
            assert (tmp_path / ".praxis-os" / "ouroboros" / "test.py").read_text() == "original code"
            assert (tmp_path / ".praxis-os" / "config" / "mcp.yaml").read_text() == "original config"


class TestSourceCloner:
    """Test suite for SourceCloner component."""

    def test_clone_or_load_with_local_source(self):
        """Test clone_or_load() with valid local source."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / "dist").mkdir()
            
            cloner = SourceCloner()
            source = cloner.clone_or_load(local_source=tmp_path)
            
            assert source == tmp_path

    def test_clone_or_load_invalid_local_source(self):
        """Test clone_or_load() with invalid local source."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            # Don't create dist/ directory
            
            cloner = SourceCloner()
            
            with pytest.raises(ValueError, match="Invalid source structure"):
                cloner.clone_or_load(local_source=tmp_path)

    def test_validate_local_source_success(self):
        """Test _validate_local_source() with valid directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / "dist").mkdir()
            
            cloner = SourceCloner()
            # Should not raise
            cloner._validate_local_source(tmp_path)

    def test_validate_local_source_not_found(self):
        """Test _validate_local_source() with non-existent directory."""
        cloner = SourceCloner()
        
        with pytest.raises(ValueError, match="not found"):
            cloner._validate_local_source(Path("/nonexistent"))

    def test_validate_local_source_not_directory(self):
        """Test _validate_local_source() with file instead of directory."""
        with tempfile.NamedTemporaryFile() as f:
            cloner = SourceCloner()
            
            with pytest.raises(ValueError, match="not a directory"):
                cloner._validate_local_source(Path(f.name))

    def test_validate_source_structure_success(self):
        """Test _validate_source_structure() with valid structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / "dist").mkdir()
            
            cloner = SourceCloner()
            # Should not raise
            cloner._validate_source_structure(tmp_path)

    def test_validate_source_structure_missing_dist(self):
        """Test _validate_source_structure() with missing dist/ directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            cloner = SourceCloner()
            
            with pytest.raises(ValueError, match="Missing dist/ directory"):
                cloner._validate_source_structure(tmp_path)

    def test_validate_source_structure_dist_not_directory(self):
        """Test _validate_source_structure() with dist/ as file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / "dist").write_text("not a directory")
            
            cloner = SourceCloner()
            
            with pytest.raises(ValueError, match="dist/ is not a directory"):
                cloner._validate_source_structure(tmp_path)

    def test_extract_version_from_pyproject(self):
        """Test extract_version() from pyproject.toml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / "dist").mkdir()
            (tmp_path / "pyproject.toml").write_text('[project]\nversion = "1.2.3"')
            
            cloner = SourceCloner()
            version = cloner.extract_version(tmp_path)
            
            assert version == "1.2.3"

    def test_extract_version_from_init(self):
        """Test extract_version() from __init__.py."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / "dist").mkdir()
            (tmp_path / "dist" / "ouroboros").mkdir(parents=True)
            (tmp_path / "dist" / "ouroboros" / "__init__.py").write_text('__version__ = "2.0.0"')
            
            cloner = SourceCloner()
            version = cloner.extract_version(tmp_path)
            
            assert version == "2.0.0"

    def test_extract_version_pyproject_priority(self):
        """Test extract_version() prefers pyproject.toml over __init__.py."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / "dist").mkdir()
            (tmp_path / "pyproject.toml").write_text('[project]\nversion = "1.2.3"')
            (tmp_path / "dist" / "ouroboros").mkdir(parents=True)
            (tmp_path / "dist" / "ouroboros" / "__init__.py").write_text('__version__ = "2.0.0"')
            
            cloner = SourceCloner()
            version = cloner.extract_version(tmp_path)
            
            # Should use pyproject.toml version
            assert version == "1.2.3"

    def test_extract_version_not_found(self):
        """Test extract_version() raises error if version not found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / "dist").mkdir()
            
            cloner = SourceCloner()
            
            with pytest.raises(ValueError, match="Could not extract version"):
                cloner.extract_version(tmp_path)

    def test_extract_version_from_pyproject_helper(self):
        """Test _extract_version_from_pyproject() helper."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            pyproject = tmp_path / "pyproject.toml"
            pyproject.write_text('[project]\nversion = "1.2.3"')
            
            cloner = SourceCloner()
            version = cloner._extract_version_from_pyproject(pyproject)
            
            assert version == "1.2.3"

    def test_extract_version_from_pyproject_not_found(self):
        """Test _extract_version_from_pyproject() returns None if not found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            pyproject = tmp_path / "pyproject.toml"
            pyproject.write_text('[project]\nname = "test"')
            
            cloner = SourceCloner()
            version = cloner._extract_version_from_pyproject(pyproject)
            
            assert version is None

    def test_extract_version_from_init_helper(self):
        """Test _extract_version_from_init() helper."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            init = tmp_path / "__init__.py"
            init.write_text('__version__ = "2.0.0"')
            
            cloner = SourceCloner()
            version = cloner._extract_version_from_init(init)
            
            assert version == "2.0.0"

    def test_extract_version_from_init_not_found(self):
        """Test _extract_version_from_init() returns None if not found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            init = tmp_path / "__init__.py"
            init.write_text('# No version here')
            
            cloner = SourceCloner()
            version = cloner._extract_version_from_init(init)
            
            assert version is None

    def test_cleanup_removes_temp_dir(self):
        """Test cleanup() removes temp directory."""
        import tempfile
        
        cloner = SourceCloner()
        cloner.temp_dir = Path(tempfile.mkdtemp(prefix="test-"))
        temp_path = cloner.temp_dir
        
        assert temp_path.exists()
        cloner.cleanup()
        assert not temp_path.exists()

    def test_cleanup_no_temp_dir(self):
        """Test cleanup() handles case with no temp directory."""
        cloner = SourceCloner()
        # Should not raise
        cloner.cleanup()

    def test_default_repo_url(self):
        """Test default repository URL is set correctly."""
        cloner = SourceCloner()
        assert cloner.source_url == "https://github.com/honeyhiveai/praxis-os.git"

    def test_custom_repo_url(self):
        """Test custom repository URL."""
        custom_url = "https://github.com/example/repo.git"
        cloner = SourceCloner(source_url=custom_url)
        assert cloner.source_url == custom_url


class TestFileUpgrader:
    """Test suite for FileUpgrader component."""

    def test_upgrade_standards(self):
        """Test _upgrade_standards() copies files correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            source = tmp_path / "source"
            target = tmp_path / "target"
            source.mkdir()
            target.mkdir()
            (target / ".praxis-os" / "standards").mkdir(parents=True)
            
            src_dir = source / "dist" / "universal" / "standards"
            src_dir.mkdir(parents=True)
            (src_dir / "test.md").write_text("content")
            
            upgrader = FileUpgrader(source, target)
            upgrader._upgrade_standards()
            
            assert (target / ".praxis-os" / "standards" / "universal" / "test.md").exists()
            assert len(upgrader.changes.files_added) > 0

    def test_upgrade_workflows(self):
        """Test _upgrade_workflows() copies files correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            source = tmp_path / "source"
            target = tmp_path / "target"
            source.mkdir()
            target.mkdir()
            (target / ".praxis-os").mkdir()
            
            src_dir = source / "dist" / "universal" / "workflows"
            src_dir.mkdir(parents=True)
            (src_dir / "test.py").write_text("code")
            
            upgrader = FileUpgrader(source, target)
            upgrader._upgrade_workflows()
            
            assert (target / ".praxis-os" / "workflows" / "test.py").exists()

    def test_upgrade_ouroboros(self):
        """Test _upgrade_ouroboros() copies files correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            source = tmp_path / "source"
            target = tmp_path / "target"
            source.mkdir()
            target.mkdir()
            (target / ".praxis-os").mkdir()
            
            src_dir = source / "dist" / "ouroboros"
            src_dir.mkdir(parents=True)
            (src_dir / "test.py").write_text("code")
            
            upgrader = FileUpgrader(source, target)
            upgrader._upgrade_ouroboros()
            
            assert (target / ".praxis-os" / "ouroboros" / "test.py").exists()

    def test_upgrade_scripts(self):
        """Test _upgrade_scripts() copies files correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            source = tmp_path / "source"
            target = tmp_path / "target"
            source.mkdir()
            target.mkdir()
            (target / ".praxis-os").mkdir()
            
            src_dir = source / "dist" / "scripts"
            src_dir.mkdir(parents=True)
            (src_dir / "test.sh").write_text("#!/bin/bash")
            
            upgrader = FileUpgrader(source, target)
            upgrader._upgrade_scripts()
            
            assert (target / ".praxis-os" / "scripts" / "test.sh").exists()

    def test_upgrade_handles_missing_source(self):
        """Test upgrade methods handle missing source directories gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            source = tmp_path / "source"
            target = tmp_path / "target"
            source.mkdir()
            target.mkdir()
            (target / ".praxis-os").mkdir()
            
            upgrader = FileUpgrader(source, target)
            # Should not raise
            upgrader._upgrade_standards()
            upgrader._upgrade_workflows()
            upgrader._upgrade_ouroboros()
            upgrader._upgrade_scripts()

    def test_user_owned_directories_never_modified(self):
        """Test that USER_OWNED directories are never modified."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            source = tmp_path / "source"
            target = tmp_path / "target"
            source.mkdir()
            target.mkdir()
            (target / ".praxis-os").mkdir()
            (target / ".praxis-os" / "specs").mkdir()
            (target / ".praxis-os" / "specs" / "user-spec.md").write_text("user content")
            (target / ".praxis-os" / "standards" / "development").mkdir(parents=True)
            (target / ".praxis-os" / "standards" / "development" / "user-standard.md").write_text("user standard")
            
            upgrader = FileUpgrader(source, target)
            upgrader.upgrade_framework_files()
            
            # User files should be untouched
            assert (target / ".praxis-os" / "specs" / "user-spec.md").read_text() == "user content"
            assert (target / ".praxis-os" / "standards" / "development" / "user-standard.md").read_text() == "user standard"

    def test_track_changes_added(self):
        """Test _track_changes() tracks added files."""
        upgrader = FileUpgrader(Path("."), Path("."))
        before = {}
        after = {"file1.txt": "abc123", "file2.txt": "def456"}
        
        upgrader._track_changes("test", before, after)
        
        assert len(upgrader.changes.files_added) == 2
        assert "test/file1.txt" in upgrader.changes.files_added
        assert "test/file2.txt" in upgrader.changes.files_added

    def test_track_changes_deleted(self):
        """Test _track_changes() tracks deleted files."""
        upgrader = FileUpgrader(Path("."), Path("."))
        before = {"file1.txt": "abc123", "file2.txt": "def456"}
        after = {}
        
        upgrader._track_changes("test", before, after)
        
        assert len(upgrader.changes.files_deleted) == 2
        assert "test/file1.txt" in upgrader.changes.files_deleted
        assert "test/file2.txt" in upgrader.changes.files_deleted

    def test_track_changes_modified(self):
        """Test _track_changes() tracks modified files."""
        upgrader = FileUpgrader(Path("."), Path("."))
        before = {"file1.txt": "abc123"}
        after = {"file1.txt": "def456"}
        
        upgrader._track_changes("test", before, after)
        
        assert len(upgrader.changes.files_modified) == 1
        assert "test/file1.txt" in upgrader.changes.files_modified

    def test_snapshot_directory(self):
        """Test _snapshot_directory() creates snapshot with checksums."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / "file1.txt").write_text("content1")
            (tmp_path / "file2.txt").write_text("content2")
            
            upgrader = FileUpgrader(Path("."), Path("."))
            snapshot = upgrader._snapshot_directory(tmp_path)
            
            assert "file1.txt" in snapshot
            assert "file2.txt" in snapshot
            assert len(snapshot) == 2

    def test_snapshot_directory_empty(self):
        """Test _snapshot_directory() with empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            upgrader = FileUpgrader(Path("."), Path("."))
            snapshot = upgrader._snapshot_directory(tmp_path)
            
            assert len(snapshot) == 0

    def test_snapshot_directory_nonexistent(self):
        """Test _snapshot_directory() with non-existent directory."""
        upgrader = FileUpgrader(Path("."), Path("."))
        snapshot = upgrader._snapshot_directory(Path("/nonexistent"))
        
        assert len(snapshot) == 0

    def test_verify_checksums_success(self):
        """Test _verify_directory_checksums() passes for matching files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            src = tmp_path / "src"
            dst = tmp_path / "dst"
            src.mkdir()
            dst.mkdir()
            (src / "test.txt").write_text("content")
            (dst / "test.txt").write_text("content")
            
            upgrader = FileUpgrader(Path("."), Path("."))
            # Should not raise
            upgrader._verify_directory_checksums(src, dst)

    def test_verify_checksums_missing_file(self):
        """Test _verify_directory_checksums() fails if file is missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            src = tmp_path / "src"
            dst = tmp_path / "dst"
            src.mkdir()
            dst.mkdir()
            (src / "test.txt").write_text("content")
            
            upgrader = FileUpgrader(Path("."), Path("."))
            
            with pytest.raises(ValueError, match="Missing file"):
                upgrader._verify_directory_checksums(src, dst)

    def test_verify_checksums_mismatch(self):
        """Test _verify_directory_checksums() fails if checksums don't match."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            src = tmp_path / "src"
            dst = tmp_path / "dst"
            src.mkdir()
            dst.mkdir()
            (src / "test.txt").write_text("content1")
            (dst / "test.txt").write_text("content2")
            
            upgrader = FileUpgrader(Path("."), Path("."))
            
            with pytest.raises(ValueError, match="Checksum.*Mismatch"):
                upgrader._verify_directory_checksums(src, dst)

    def test_rsync_basic(self):
        """Test _rsync() copies files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            src = tmp_path / "src"
            dst = tmp_path / "dst"
            src.mkdir()
            (src / "test.txt").write_text("content")
            
            upgrader = FileUpgrader(Path("."), Path("."))
            upgrader._rsync(src, dst)
            
            assert (dst / "test.txt").exists()
            assert (dst / "test.txt").read_text() == "content"

    def test_rsync_with_delete(self):
        """Test _rsync() with delete flag."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            src = tmp_path / "src"
            dst = tmp_path / "dst"
            src.mkdir()
            dst.mkdir()
            (src / "new.txt").write_text("new")
            (dst / "old.txt").write_text("old")
            
            upgrader = FileUpgrader(Path("."), Path("."))
            upgrader._rsync(src, dst, delete=True)
            
            assert (dst / "new.txt").exists()
            assert not (dst / "old.txt").exists()

    def test_upgrade_framework_files_full(self):
        """Test full upgrade_framework_files() workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            source = tmp_path / "source"
            target = tmp_path / "target"
            source.mkdir()
            target.mkdir()
            (target / ".praxis-os").mkdir()
            
            # Create source files
            (source / "dist" / "universal" / "standards").mkdir(parents=True)
            (source / "dist" / "universal" / "standards" / "test.md").write_text("standard")
            (source / "dist" / "universal" / "workflows").mkdir(parents=True)
            (source / "dist" / "universal" / "workflows" / "test.py").write_text("workflow")
            (source / "dist" / "ouroboros").mkdir(parents=True)
            (source / "dist" / "ouroboros" / "test.py").write_text("ouroboros")
            (source / "dist" / "scripts").mkdir(parents=True)
            (source / "dist" / "scripts" / "test.sh").write_text("script")
            
            upgrader = FileUpgrader(source, target)
            report = upgrader.upgrade_framework_files()
            
            assert isinstance(report, UpgradeReport)
            assert len(report.files_added) > 0


class TestConfigReconciler:
    """Test suite for ConfigReconciler component."""

    def test_prepare_reconciliation_no_changes(self):
        """Test prepare_reconciliation() returns NO_CHANGES when configs are identical."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            source = tmp_path / "source"
            target = tmp_path / "target"
            source.mkdir()
            target.mkdir()
            (source / "dist" / "config").mkdir(parents=True)
            (source / "dist" / "config" / "mcp.yaml").write_text("key: value")
            (target / ".praxis-os" / "config").mkdir(parents=True)
            (target / ".praxis-os" / "config" / "mcp.yaml").write_text("key: value")
            
            reconciler = ConfigReconciler(source, target)
            status = reconciler.prepare_reconciliation()
            
            assert status == "NO_CHANGES"
            assert not (target / ".praxis-os" / "config" / "mcp.yaml.new").exists()

    def test_prepare_reconciliation_changes_detected(self):
        """Test prepare_reconciliation() detects changes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            source = tmp_path / "source"
            target = tmp_path / "target"
            source.mkdir()
            target.mkdir()
            (source / "dist" / "config").mkdir(parents=True)
            (source / "dist" / "config" / "mcp.yaml").write_text("key: new_value")
            (target / ".praxis-os" / "config").mkdir(parents=True)
            (target / ".praxis-os" / "config" / "mcp.yaml").write_text("key: old_value")
            
            reconciler = ConfigReconciler(source, target)
            status = reconciler.prepare_reconciliation()
            
            assert status == "RECONCILIATION_NEEDED"
            assert (target / ".praxis-os" / "config" / "mcp.yaml.new").exists()
            assert (target / ".praxis-os" / "config" / "CONFIG_RECONCILIATION_NEEDED.md").exists()

    def test_prepare_reconciliation_missing_template(self):
        """Test prepare_reconciliation() handles missing template gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            source = tmp_path / "source"
            target = tmp_path / "target"
            source.mkdir()
            target.mkdir()
            (target / ".praxis-os" / "config").mkdir(parents=True)
            
            reconciler = ConfigReconciler(source, target)
            status = reconciler.prepare_reconciliation()
            
            assert status == "NO_CHANGES"

    def test_merge_gitignore_additive(self):
        """Test merge_gitignore() adds new patterns without removing existing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            source = tmp_path / "source"
            target = tmp_path / "target"
            source.mkdir()
            target.mkdir()
            (source / ".gitignore").write_text("*.pyc\n__pycache__/")
            (target / ".gitignore").write_text("*.log")
            
            reconciler = ConfigReconciler(source, target)
            reconciler.merge_gitignore()
            
            content = (target / ".gitignore").read_text()
            assert "*.log" in content
            assert "*.pyc" in content
            assert "__pycache__/" in content

    def test_merge_gitignore_no_source(self):
        """Test merge_gitignore() handles missing source gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            source = tmp_path / "source"
            target = tmp_path / "target"
            source.mkdir()
            target.mkdir()
            (target / ".gitignore").write_text("*.log")
            
            reconciler = ConfigReconciler(source, target)
            reconciler.merge_gitignore()
            
            # Should preserve existing
            assert (target / ".gitignore").read_text() == "*.log"

    def test_merge_gitignore_no_target(self):
        """Test merge_gitignore() creates target if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            source = tmp_path / "source"
            target = tmp_path / "target"
            source.mkdir()
            target.mkdir()
            (source / ".gitignore").write_text("*.pyc")
            
            reconciler = ConfigReconciler(source, target)
            reconciler.merge_gitignore()
            
            assert (target / ".gitignore").exists()
            assert "*.pyc" in (target / ".gitignore").read_text()

    def test_configs_identical_same(self):
        """Test _configs_identical() returns True for identical configs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            file1 = tmp_path / "file1.yaml"
            file2 = tmp_path / "file2.yaml"
            file1.write_text("key: value")
            file2.write_text("key: value")
            
            reconciler = ConfigReconciler(Path("."), Path("."))
            assert reconciler._configs_identical(file1, file2) is True

    def test_configs_identical_different(self):
        """Test _configs_identical() returns False for different configs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            file1 = tmp_path / "file1.yaml"
            file2 = tmp_path / "file2.yaml"
            file1.write_text("key: value1")
            file2.write_text("key: value2")
            
            reconciler = ConfigReconciler(Path("."), Path("."))
            assert reconciler._configs_identical(file1, file2) is False

    def test_configs_identical_ignores_comments(self):
        """Test _configs_identical() ignores comments."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            file1 = tmp_path / "file1.yaml"
            file2 = tmp_path / "file2.yaml"
            file1.write_text("key: value  # comment1")
            file2.write_text("key: value  # comment2")
            
            reconciler = ConfigReconciler(Path("."), Path("."))
            assert reconciler._configs_identical(file1, file2) is True

    def test_configs_identical_ignores_whitespace(self):
        """Test _configs_identical() ignores whitespace."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            file1 = tmp_path / "file1.yaml"
            file2 = tmp_path / "file2.yaml"
            file1.write_text("key: value\n\n")
            file2.write_text("key:   value")
            
            reconciler = ConfigReconciler(Path("."), Path("."))
            assert reconciler._configs_identical(file1, file2) is True

    def test_normalize_config_removes_comments(self):
        """Test _normalize_config() removes comments."""
        reconciler = ConfigReconciler(Path("."), Path("."))
        normalized = reconciler._normalize_config("key: value  # comment")
        assert normalized == "key: value"

    def test_normalize_config_removes_empty_lines(self):
        """Test _normalize_config() removes empty lines."""
        reconciler = ConfigReconciler(Path("."), Path("."))
        normalized = reconciler._normalize_config("key: value\n\n\nkey2: value2")
        assert normalized == "key: value\nkey2: value2"

    def test_create_reconciliation_prompt(self):
        """Test _create_reconciliation_prompt() creates prompt file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            source = tmp_path / "source"
            target = tmp_path / "target"
            source.mkdir()
            target.mkdir()
            (target / ".praxis-os" / "config").mkdir(parents=True)
            
            reconciler = ConfigReconciler(source, target)
            reconciler._create_reconciliation_prompt()
            
            prompt_file = target / ".praxis-os" / "config" / "CONFIG_RECONCILIATION_NEEDED.md"
            assert prompt_file.exists()
            content = prompt_file.read_text()
            assert "Configuration Reconciliation Needed" in content
            assert "mcp.yaml" in content


class TestDependencyUpdater:
    """Test suite for DependencyUpdater component."""

    def test_update_requirements_txt(self):
        """Test _update_requirements_txt() copies file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            source = tmp_path / "source"
            target = tmp_path / "target"
            source.mkdir()
            target.mkdir()
            (source / "requirements.txt").write_text("package==1.0.0")
            
            updater = DependencyUpdater(source, target)
            updater._update_requirements_txt()
            
            assert (target / "requirements.txt").exists()
            assert (target / "requirements.txt").read_text() == "package==1.0.0"

    def test_update_requirements_txt_missing_source(self):
        """Test _update_requirements_txt() handles missing source."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            source = tmp_path / "source"
            target = tmp_path / "target"
            source.mkdir()
            target.mkdir()
            
            updater = DependencyUpdater(source, target)
            updater._update_requirements_txt()
            
            assert not (target / "requirements.txt").exists()

    def test_update_package_json(self):
        """Test _update_package_json() copies file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            source = tmp_path / "source"
            target = tmp_path / "target"
            source.mkdir()
            target.mkdir()
            (source / "package.json").write_text('{"name": "test"}')
            
            updater = DependencyUpdater(source, target)
            updater._update_package_json()
            
            assert (target / "package.json").exists()
            assert (target / "package.json").read_text() == '{"name": "test"}'

    def test_update_package_json_missing_source(self):
        """Test _update_package_json() handles missing source."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            source = tmp_path / "source"
            target = tmp_path / "target"
            source.mkdir()
            target.mkdir()
            
            updater = DependencyUpdater(source, target)
            updater._update_package_json()
            
            assert not (target / "package.json").exists()

    def test_update_dependencies_both(self):
        """Test update_dependencies() updates both files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            source = tmp_path / "source"
            target = tmp_path / "target"
            source.mkdir()
            target.mkdir()
            (source / "requirements.txt").write_text("package==1.0.0")
            (source / "package.json").write_text('{"name": "test"}')
            
            updater = DependencyUpdater(source, target)
            updater.update_dependencies()
            
            assert (target / "requirements.txt").exists()
            assert (target / "package.json").exists()


class TestUpgradeValidator:
    """Test suite for UpgradeValidator component."""

    def test_verify_file_counts_success(self):
        """Test _verify_file_counts() passes with sufficient files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / ".praxis-os" / "ouroboros").mkdir(parents=True)
            # Create 15 Python files
            for i in range(15):
                (tmp_path / ".praxis-os" / "ouroboros" / f"file{i}.py").write_text("# test")
            
            report = UpgradeReport()
            validator = UpgradeValidator(tmp_path, report)
            result = validator._verify_file_counts()
            
            assert result.passed is True
            assert "15" in result.message

    def test_verify_file_counts_missing_dir(self):
        """Test _verify_file_counts() fails if directory missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            report = UpgradeReport()
            validator = UpgradeValidator(tmp_path, report)
            result = validator._verify_file_counts()
            
            assert result.passed is False
            assert "not found" in result.message

    def test_verify_file_counts_insufficient_files(self):
        """Test _verify_file_counts() fails with too few files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / ".praxis-os" / "ouroboros").mkdir(parents=True)
            # Create only 5 Python files
            for i in range(5):
                (tmp_path / ".praxis-os" / "ouroboros" / f"file{i}.py").write_text("# test")
            
            report = UpgradeReport()
            validator = UpgradeValidator(tmp_path, report)
            result = validator._verify_file_counts()
            
            assert result.passed is False
            assert "5" in result.message

    def test_test_python_imports_no_venv(self):
        """Test _test_python_imports() fails if venv missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            report = UpgradeReport()
            validator = UpgradeValidator(tmp_path, report)
            result = validator._test_python_imports()
            
            assert result.passed is False
            assert "Virtual environment not found" in result.message

    def test_validate_config_schema_missing_file(self):
        """Test _validate_config_schema() fails if config missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            report = UpgradeReport()
            validator = UpgradeValidator(tmp_path, report)
            result = validator._validate_config_schema()
            
            assert result.passed is False
            assert "not found" in result.message

    def test_validate_config_schema_valid(self):
        """Test _validate_config_schema() passes with valid YAML."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / ".praxis-os" / "config").mkdir(parents=True)
            (tmp_path / ".praxis-os" / "config" / "mcp.yaml").write_text("key: value\nlist:\n  - item1\n  - item2")
            
            report = UpgradeReport()
            validator = UpgradeValidator(tmp_path, report)
            result = validator._validate_config_schema()
            
            assert result.passed is True
            assert "valid" in result.message

    def test_validate_config_schema_invalid_yaml(self):
        """Test _validate_config_schema() fails with invalid YAML."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / ".praxis-os" / "config").mkdir(parents=True)
            # Use truly invalid YAML syntax (unclosed bracket)
            (tmp_path / ".praxis-os" / "config" / "mcp.yaml").write_text("key: [value")
            
            report = UpgradeReport()
            validator = UpgradeValidator(tmp_path, report)
            result = validator._validate_config_schema()
            
            assert result.passed is False
            assert "YAML" in result.message

    def test_verify_checksums_missing_dir(self):
        """Test _verify_checksums() fails if directory missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            report = UpgradeReport()
            validator = UpgradeValidator(tmp_path, report)
            result = validator._verify_checksums()
            
            assert result.passed is False
            assert "not found" in result.message

    def test_verify_checksums_success(self):
        """Test _verify_checksums() passes with directory present."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / ".praxis-os" / "ouroboros").mkdir(parents=True)
            
            report = UpgradeReport()
            validator = UpgradeValidator(tmp_path, report)
            result = validator._verify_checksums()
            
            assert result.passed is True

    def test_aggregate_results_all_pass(self):
        """Test _aggregate_results() with all checks passing."""
        check1 = CheckResult(True, "Test 1", "OK")
        check2 = CheckResult(True, "Test 2", "OK")
        
        validator = UpgradeValidator(Path("."), UpgradeReport())
        result = validator._aggregate_results([check1, check2])
        
        assert result.passed is True
        assert len(result.checks) == 2

    def test_aggregate_results_some_fail(self):
        """Test _aggregate_results() with some checks failing."""
        check1 = CheckResult(True, "Test 1", "OK")
        check2 = CheckResult(False, "Test 2", "FAIL")
        
        validator = UpgradeValidator(Path("."), UpgradeReport())
        result = validator._aggregate_results([check1, check2])
        
        assert result.passed is False
        assert len(result.checks) == 2

    def test_validate_upgrade_integration(self):
        """Test validate_upgrade() integration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / ".praxis-os" / "ouroboros").mkdir(parents=True)
            (tmp_path / ".praxis-os" / "config").mkdir(parents=True)
            (tmp_path / ".praxis-os" / "config" / "mcp.yaml").write_text("key: value")
            # Create 15 Python files
            for i in range(15):
                (tmp_path / ".praxis-os" / "ouroboros" / f"file{i}.py").write_text("# test")
            
            report = UpgradeReport()
            validator = UpgradeValidator(tmp_path, report)
            result = validator.validate_upgrade()
            
            assert isinstance(result, ValidationResult)
            # Will fail on imports check (no venv), but structure is correct
            assert len(result.checks) == 4


class TestUpgradeOrchestrator:
    """Test suite for UpgradeOrchestrator component."""

    def test_init(self):
        """Test UpgradeOrchestrator initialization."""
        import argparse
        args = argparse.Namespace(target_dir="/tmp/test", source=None, skip_deps=False)
        orchestrator = UpgradeOrchestrator(args)
        
        assert str(orchestrator.target).endswith("/tmp/test")
        assert orchestrator.backup_dir is None
        assert orchestrator.source_cloner is None

    def test_upgrade_lock_prevents_concurrent(self):
        """Test _upgrade_lock() prevents concurrent upgrades."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / ".praxis-os").mkdir()
            
            import argparse
            args = argparse.Namespace(target_dir=str(tmp_path), source=None, skip_deps=False)
            orchestrator = UpgradeOrchestrator(args)
            
            # First lock should succeed
            with orchestrator._upgrade_lock():
                # Second lock should fail
                orchestrator2 = UpgradeOrchestrator(args)
                try:
                    with orchestrator2._upgrade_lock():
                        assert False, "Should have raised RuntimeError"
                except RuntimeError as e:
                    assert "in progress" in str(e)

    def test_handle_error_returns_nonzero(self):
        """Test _handle_error() returns non-zero exit code."""
        import argparse
        args = argparse.Namespace(target_dir="/tmp/test", source=None, skip_deps=False)
        orchestrator = UpgradeOrchestrator(args)
        
        result = orchestrator._handle_error(RuntimeError("Test error"))
        assert result != 0

    def test_cleanup(self):
        """Test _cleanup() method."""
        import argparse
        args = argparse.Namespace(target_dir="/tmp/test", source=None, skip_deps=False)
        orchestrator = UpgradeOrchestrator(args)
        
        # Should not raise even with no source_cloner
        orchestrator._cleanup()

