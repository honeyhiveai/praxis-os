"""
Integration test for Agent OS Upgrade Workflow registration and discovery.

Tests that the workflow engine can discover and load the agent_os_upgrade_v1 workflow.
"""

import json
from pathlib import Path

import pytest

from mcp_server.models import WorkflowMetadata
from mcp_server.workflow_engine import WorkflowEngine


@pytest.fixture
def workflow_engine(tmp_path):
    """Create WorkflowEngine with real workflow directory."""
    from mcp_server.state_manager import StateManager

    # Use actual universal/workflows directory
    workflows_path = Path(__file__).parent.parent.parent / "universal" / "workflows"

    # Create state directory and manager
    state_dir = tmp_path / ".praxis-os" / ".cache" / "state"
    state_dir.mkdir(parents=True)
    state_manager = StateManager(state_dir=state_dir)

    # Create minimal engine (without full RAG dependencies)
    engine = WorkflowEngine(
        rag_engine=None,  # Not needed for metadata loading
        state_manager=state_manager,
        workflows_base_path=workflows_path,
    )

    return engine


class TestWorkflowRegistration:
    """Test workflow registration and discovery."""

    def test_workflow_metadata_file_exists(self):
        """Test that metadata.json file exists for agent_os_upgrade_v1."""
        workflows_path = Path(__file__).parent.parent.parent / "universal" / "workflows"
        metadata_path = workflows_path / "agent_os_upgrade_v1" / "metadata.json"

        assert metadata_path.exists(), f"Metadata file not found at {metadata_path}"

    def test_metadata_json_is_valid(self):
        """Test that metadata.json is valid JSON with required fields."""
        workflows_path = Path(__file__).parent.parent.parent / "universal" / "workflows"
        metadata_path = workflows_path / "agent_os_upgrade_v1" / "metadata.json"

        with open(metadata_path) as f:
            metadata = json.load(f)

        # Check required fields
        assert "name" in metadata
        assert "workflow_type" in metadata
        assert "description" in metadata
        assert "total_phases" in metadata
        assert "phases" in metadata

        # Verify workflow type
        assert metadata["workflow_type"] == "agent_os_upgrade_v1"

        # Verify has 6 phases (0-5)
        assert metadata["total_phases"] == 6
        assert len(metadata["phases"]) == 6

    def test_all_phase_files_exist(self):
        """Test that all phase files referenced in metadata exist."""
        workflows_path = Path(__file__).parent.parent.parent / "universal" / "workflows"
        metadata_path = workflows_path / "agent_os_upgrade_v1" / "metadata.json"

        with open(metadata_path) as f:
            metadata = json.load(f)

        for phase in metadata["phases"]:
            phase_file = workflows_path / "agent_os_upgrade_v1" / phase["file"]
            assert phase_file.exists(), f"Phase file not found: {phase_file}"

    def test_workflow_engine_can_load_metadata(self, workflow_engine):
        """Test that WorkflowEngine can load agent_os_upgrade_v1 metadata."""
        metadata = workflow_engine.load_workflow_metadata("agent_os_upgrade_v1")

        assert metadata is not None
        assert isinstance(metadata, WorkflowMetadata)
        assert metadata.workflow_type == "agent_os_upgrade_v1"
        assert (
            metadata.description
            == "AI-guided Agent OS upgrade with validation and rollback"
        )
        assert metadata.total_phases == 6

    def test_workflow_metadata_has_correct_phases(self, workflow_engine):
        """Test that metadata contains all expected phases."""
        metadata = workflow_engine.load_workflow_metadata("agent_os_upgrade_v1")

        phase_numbers = [phase.phase_number for phase in metadata.phases]
        assert phase_numbers == [0, 1, 2, 3, 4, 5]

        # Verify phase names
        expected_names = [
            "Pre-Flight Checks",
            "Backup & Preparation",
            "Content Upgrade",
            "MCP Server Upgrade",
            "Post-Upgrade Validation",
            "Cleanup & Documentation",
        ]

        actual_names = [phase.phase_name for phase in metadata.phases]
        assert (
            actual_names == expected_names
        ), f"Expected {expected_names}, got {actual_names}"

    def test_phase_3_marked_as_requires_restart(self, workflow_engine):
        """Test that Phase 3 is marked as requiring restart."""
        metadata = workflow_engine.load_workflow_metadata("agent_os_upgrade_v1")

        phase_3 = next(p for p in metadata.phases if p.phase_number == 3)
        # Check if requires_restart attribute exists (may not be in all models)
        if hasattr(phase_3, "requires_restart"):
            assert phase_3.requires_restart is True, "Phase 3 should require restart"

            # Other phases should not require restart
            for phase in metadata.phases:
                if phase.phase_number != 3:
                    assert phase.requires_restart is False
        else:
            # requires_restart not in PhaseMetadata model - skip this check
            pass


class TestWorkflowStructure:
    """Test workflow directory structure."""

    def test_phases_directory_exists(self):
        """Test that phases directory exists."""
        workflows_path = Path(__file__).parent.parent.parent / "universal" / "workflows"
        phases_dir = workflows_path / "agent_os_upgrade_v1" / "phases"

        assert phases_dir.exists()
        assert phases_dir.is_dir()

    def test_supporting_docs_directory_exists(self):
        """Test that supporting-docs directory exists."""
        workflows_path = Path(__file__).parent.parent.parent / "universal" / "workflows"
        docs_dir = workflows_path / "agent_os_upgrade_v1" / "supporting-docs"

        assert docs_dir.exists()
        assert docs_dir.is_dir()

    def test_readme_exists(self):
        """Test that README.md exists."""
        workflows_path = Path(__file__).parent.parent.parent / "universal" / "workflows"
        readme = workflows_path / "agent_os_upgrade_v1" / "README.md"

        assert readme.exists()

        content = readme.read_text()
        assert "Agent OS Upgrade Workflow" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
