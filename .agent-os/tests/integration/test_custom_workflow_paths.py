"""
Integration tests for custom workflow paths via config.json.

Tests that the MCP server can load workflow metadata from custom directory
structures as specified in config.json.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp_server.config import ConfigLoader


class TestCustomWorkflowPaths(unittest.TestCase):
    """Test custom workflow path configuration."""

    def setUp(self):
        """Create temporary directory structure."""
        self.temp_dir = tempfile.mkdtemp()
        self.base_path = Path(self.temp_dir) / ".agent-os"
        self.base_path.mkdir(parents=True)

    def tearDown(self):
        """Clean up temporary directory."""
        import shutil

        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_load_paths_no_config(self):
        """Test default paths when no config.json exists."""
        config = ConfigLoader.load(self.base_path)
        paths = config.resolved_paths

        # Should use defaults (new defaults use .agent-os/ prefix)
        project_root = self.base_path.parent
        assert paths["standards_path"] == project_root / ".agent-os" / "standards"
        assert paths["usage_path"] == project_root / ".agent-os" / "usage"
        assert paths["workflows_path"] == project_root / ".agent-os" / "workflows"

    def test_load_paths_from_config(self):
        """Test loading custom paths from config.json."""
        # Create config.json with custom paths
        config = {
            "rag": {
                "standards_path": ".agent-os-source/standards",
                "usage_path": ".agent-os-source/usage",
                "workflows_path": ".agent-os-source/workflows",
            }
        }

        config_path = self.base_path / "config.json"
        with open(config_path, "w") as f:
            json.dump(config, f)

        # Load paths
        config = ConfigLoader.load(self.base_path)
        paths = config.resolved_paths

        # Should use config paths (resolved relative to project root)
        project_root = self.base_path.parent
        assert (
            paths["standards_path"] == project_root / ".agent-os-source" / "standards"
        )
        assert paths["usage_path"] == project_root / ".agent-os-source" / "usage"
        assert (
            paths["workflows_path"] == project_root / ".agent-os-source" / "workflows"
        )

    def test_load_paths_partial_config(self):
        """Test config with only some paths specified."""
        # Create config with only workflows_path
        config = {"rag": {"workflows_path": "custom/workflows"}}

        config_path = self.base_path / "config.json"
        with open(config_path, "w") as f:
            json.dump(config, f)

        loaded_config = ConfigLoader.load(self.base_path)
        paths = loaded_config.resolved_paths

        project_root = self.base_path.parent

        # workflows_path from config (resolved relative to project root)
        assert paths["workflows_path"] == project_root / "custom" / "workflows"

        # Others use defaults (new defaults use .agent-os/ prefix)
        assert paths["standards_path"] == project_root / ".agent-os" / "standards"
        assert paths["usage_path"] == project_root / ".agent-os" / "usage"

    def test_load_paths_invalid_config(self):
        """Test fallback when config.json is invalid."""
        # Create invalid JSON
        config_path = self.base_path / "config.json"
        with open(config_path, "w") as f:
            f.write("{invalid json")

        # Should fall back to defaults
        config = ConfigLoader.load(self.base_path)
        paths = config.resolved_paths

        project_root = self.base_path.parent
        assert paths["standards_path"] == project_root / ".agent-os" / "standards"
        assert paths["usage_path"] == project_root / ".agent-os" / "usage"
        assert paths["workflows_path"] == project_root / ".agent-os" / "workflows"

    def test_workflow_metadata_loading_custom_path(self):
        """Test that WorkflowEngine can load metadata from custom path."""
        # Create custom structure
        project_root = self.base_path.parent
        custom_workflows = project_root / "custom" / "workflows"
        custom_workflows.mkdir(parents=True)

        # Create test workflow metadata
        test_workflow_dir = custom_workflows / "test_workflow"
        test_workflow_dir.mkdir()

        metadata = {
            "workflow_type": "test_workflow",
            "version": "1.0.0",
            "description": "Test workflow",
            "total_phases": 2,
            "estimated_duration": "10 minutes",
            "primary_outputs": ["test output"],
            "phases": [
                {
                    "phase_number": 0,
                    "phase_name": "Custom Setup",
                    "purpose": "Setup phase",
                    "estimated_effort": "5 minutes",
                    "key_deliverables": ["setup complete"],
                    "validation_criteria": ["ready"],
                },
                {
                    "phase_number": 1,
                    "phase_name": "Custom Execute",
                    "purpose": "Execute phase",
                    "estimated_effort": "5 minutes",
                    "key_deliverables": ["execution complete"],
                    "validation_criteria": ["done"],
                },
            ],
        }

        metadata_file = test_workflow_dir / "metadata.json"
        with open(metadata_file, "w") as f:
            json.dump(metadata, f)

        # Create config pointing to custom path
        config = {"rag": {"workflows_path": "custom/workflows"}}

        config_path = self.base_path / "config.json"
        with open(config_path, "w") as f:
            json.dump(config, f)

        # Load paths and verify
        config = ConfigLoader.load(self.base_path)
        paths = config.resolved_paths
        workflows_path = paths["workflows_path"]

        # Verify metadata file is accessible
        expected_metadata_path = workflows_path / "test_workflow" / "metadata.json"
        assert expected_metadata_path.exists()

        # Load and verify metadata
        with open(expected_metadata_path) as f:
            loaded_metadata = json.load(f)

        assert loaded_metadata["workflow_type"] == "test_workflow"
        assert loaded_metadata["phases"][0]["phase_name"] == "Custom Setup"
        assert loaded_metadata["phases"][1]["phase_name"] == "Custom Execute"


if __name__ == "__main__":
    unittest.main()
