"""
Unit tests for ReportGenerator.

Tests report generation and documentation update functionality.
"""

import json
from datetime import datetime
from pathlib import Path

import pytest

from mcp_server.report_generator import ReportGenerator


@pytest.fixture
def report_generator(tmp_path):
    """Create ReportGenerator with temporary directory."""
    return ReportGenerator(base_path=tmp_path)


@pytest.fixture
def mock_workflow_state():
    """Create mock workflow state."""
    return {
        "session_id": "test-session-123",
        "workflow_type": "agent_os_upgrade_v1",
        "current_phase": 5,
        "completed_phases": [0, 1, 2, 3, 4],
        "phase_artifacts": {
            "0": {"source_version": "1.0.0", "source_commit": "abc123"},
            "1": {"backup_path": "/backup/path"},
        },
        "metadata": {"started_at": "2025-10-09T10:00:00Z"},
    }


class TestGenerateUpgradeSummary:
    """Tests for generate_upgrade_summary method."""

    def test_generate_upgrade_summary_creates_file(
        self, report_generator, mock_workflow_state
    ):
        """Test that upgrade summary file is created."""
        report_path = report_generator.generate_upgrade_summary(
            "test-session-123", mock_workflow_state
        )

        assert report_path is not None
        assert Path(report_path).exists()
        assert Path(report_path).suffix == ".md"

    def test_generate_upgrade_summary_content(
        self, report_generator, mock_workflow_state
    ):
        """Test upgrade summary content."""
        report_path = report_generator.generate_upgrade_summary(
            "test-session-123", mock_workflow_state
        )

        content = Path(report_path).read_text()

        # Check for expected sections
        assert "# Agent OS Upgrade Summary" in content
        assert "test-session-123" in content
        assert "agent_os_upgrade_v1" in content
        assert "Phase 0" in content or "Phase" in content

    def test_generate_upgrade_summary_with_artifacts(
        self, report_generator, mock_workflow_state
    ):
        """Test upgrade summary includes phase artifacts."""
        report_path = report_generator.generate_upgrade_summary(
            "test-session-123", mock_workflow_state
        )

        content = Path(report_path).read_text()

        # Check artifacts are included
        assert "1.0.0" in content or "source_version" in content
        assert "backup_path" in content or "/backup/path" in content


class TestGenerateValidationReport:
    """Tests for generate_validation_report method."""

    def test_generate_validation_report_creates_file(self, report_generator):
        """Test that validation report file is created."""
        validation_results = {
            "server_version": "1.0.0",
            "tools_registered": 8,
            "tests_passed": True,
        }

        report_path = report_generator.generate_validation_report(validation_results)

        assert report_path is not None
        assert Path(report_path).exists()
        assert Path(report_path).suffix == ".json"

    def test_generate_validation_report_content(self, report_generator):
        """Test validation report JSON content."""
        validation_results = {
            "server_version": "1.0.0",
            "tools_registered": 8,
            "tests_passed": True,
        }

        report_path = report_generator.generate_validation_report(validation_results)

        with open(report_path) as f:
            content = json.load(f)

        assert "generated_at" in content
        assert "validation_results" in content
        assert content["validation_results"]["server_version"] == "1.0.0"
        assert content["validation_results"]["tools_registered"] == 8

    def test_generate_validation_report_timestamp(self, report_generator):
        """Test validation report includes timestamp."""
        validation_results = {"test": "data"}

        report_path = report_generator.generate_validation_report(validation_results)

        with open(report_path) as f:
            content = json.load(f)

        # Check timestamp is valid ISO format
        assert "generated_at" in content
        datetime.fromisoformat(content["generated_at"])  # Should not raise


class TestUpdateInstallationSummary:
    """Tests for update_installation_summary method."""

    def test_update_installation_summary_creates_file(self, report_generator, tmp_path):
        """Test that installation summary file is created."""
        upgrade_info = {
            "from_version": "0.9.0",
            "to_version": "1.0.0",
            "status": "completed",
        }

        report_generator.update_installation_summary(upgrade_info)

        summary_path = tmp_path / ".agent-os" / "INSTALLATION_SUMMARY.md"
        assert summary_path.exists()

    def test_update_installation_summary_content(self, report_generator, tmp_path):
        """Test installation summary content."""
        upgrade_info = {
            "from_version": "0.9.0",
            "to_version": "1.0.0",
            "status": "completed",
        }

        report_generator.update_installation_summary(upgrade_info)

        summary_path = tmp_path / ".agent-os" / "INSTALLATION_SUMMARY.md"
        content = summary_path.read_text()

        assert "0.9.0" in content
        assert "1.0.0" in content
        assert "completed" in content
        assert "Upgrade:" in content

    def test_update_installation_summary_appends(self, report_generator, tmp_path):
        """Test that multiple upgrades are appended."""
        upgrade_info_1 = {
            "from_version": "0.9.0",
            "to_version": "1.0.0",
            "status": "completed",
        }

        upgrade_info_2 = {
            "from_version": "1.0.0",
            "to_version": "1.1.0",
            "status": "completed",
        }

        report_generator.update_installation_summary(upgrade_info_1)
        report_generator.update_installation_summary(upgrade_info_2)

        summary_path = tmp_path / ".agent-os" / "INSTALLATION_SUMMARY.md"
        content = summary_path.read_text()

        # Both upgrades should be present
        assert "0.9.0" in content
        assert "1.0.0" in content
        assert "1.1.0" in content


class TestAppendToUpdateLog:
    """Tests for append_to_update_log method."""

    def test_append_to_update_log_creates_file(self, report_generator, tmp_path):
        """Test that update log file is created."""
        changes = {"new_files": 3, "updated_files": 12}

        report_generator.append_to_update_log("1.0.0", changes)

        log_path = tmp_path / ".agent-os" / "UPDATE_LOG.txt"
        assert log_path.exists()

    def test_append_to_update_log_content(self, report_generator, tmp_path):
        """Test update log content."""
        changes = {"new_files": 3, "updated_files": 12, "conflicts_resolved": 0}

        report_generator.append_to_update_log("1.0.0", changes)

        log_path = tmp_path / ".agent-os" / "UPDATE_LOG.txt"
        content = log_path.read_text()

        assert "1.0.0" in content
        assert "New files: 3" in content
        assert "Updated files: 12" in content
        assert "Conflicts resolved: 0" in content

    def test_append_to_update_log_multiple_entries(self, report_generator, tmp_path):
        """Test multiple log entries are appended."""
        changes_1 = {"new_files": 3}
        changes_2 = {"new_files": 5}

        report_generator.append_to_update_log("1.0.0", changes_1)
        report_generator.append_to_update_log("1.1.0", changes_2)

        log_path = tmp_path / ".agent-os" / "UPDATE_LOG.txt"
        content = log_path.read_text()

        # Both entries should be present
        assert "1.0.0" in content
        assert "1.1.0" in content
        assert content.count("Upgrade to") == 2


class TestIntegration:
    """Integration tests for ReportGenerator."""

    def test_generate_all_reports(
        self, report_generator, mock_workflow_state, tmp_path
    ):
        """Test generating all report types."""
        # Generate upgrade summary
        summary_path = report_generator.generate_upgrade_summary(
            "test-session", mock_workflow_state
        )
        assert Path(summary_path).exists()

        # Generate validation report
        validation_path = report_generator.generate_validation_report(
            {"tests_passed": True}
        )
        assert Path(validation_path).exists()

        # Update installation summary
        report_generator.update_installation_summary(
            {"from_version": "0.9.0", "to_version": "1.0.0", "status": "completed"}
        )
        assert (tmp_path / ".agent-os" / "INSTALLATION_SUMMARY.md").exists()

        # Append to update log
        report_generator.append_to_update_log("1.0.0", {"new_files": 3})
        assert (tmp_path / ".agent-os" / "UPDATE_LOG.txt").exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
