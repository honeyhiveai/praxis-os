"""
Unit tests for migration script.

Tests script structure, workflow scanning, and statistics tracking.
"""

# Import after adding to path
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.migrate_checkpoints_to_gates import MigrationScript


class TestMigrationScript:
    """Tests for MigrationScript class."""

    @pytest.fixture
    def temp_workflows(self, tmp_path):
        """Create temporary workflows directory structure."""
        workflows_dir = tmp_path / "workflows"
        workflows_dir.mkdir()

        # Create workflow 1 with 2 phases
        workflow1 = workflows_dir / "test_workflow_v1"
        (workflow1 / "phases" / "0").mkdir(parents=True)
        (workflow1 / "phases" / "1").mkdir(parents=True)
        (workflow1 / "phases" / "0" / "phase.md").write_text("Phase 0")
        (workflow1 / "phases" / "1" / "phase.md").write_text("Phase 1")

        # Create workflow 2 with 1 phase
        workflow2 = workflows_dir / "test_workflow_v2"
        (workflow2 / "phases" / "0").mkdir(parents=True)
        (workflow2 / "phases" / "0" / "phase.md").write_text("Phase 0")

        return workflows_dir

    def test_init(self, temp_workflows):
        """Test MigrationScript initialization."""
        script = MigrationScript(temp_workflows, dry_run=True, force=True)

        assert script.workflows_path == temp_workflows
        assert script.dry_run is True
        assert script.force is True
        assert script.stats["workflows_scanned"] == 0
        assert script.stats["phases_scanned"] == 0
        assert script.stats["gates_created"] == 0

    def test_scan_workflows(self, temp_workflows):
        """Test workflow scanning."""
        script = MigrationScript(temp_workflows)
        workflows = script.scan_workflows()

        assert len(workflows) == 2
        assert "test_workflow_v1" in workflows
        assert "test_workflow_v2" in workflows
        assert workflows == sorted(workflows)  # Should be sorted

    def test_scan_workflows_nonexistent_path(self, tmp_path):
        """Test scanning non-existent workflows path."""
        nonexistent = tmp_path / "nonexistent"
        script = MigrationScript(nonexistent)
        workflows = script.scan_workflows()

        assert workflows == []

    def test_scan_workflows_ignores_hidden(self, tmp_path):
        """Test that hidden directories are ignored."""
        workflows_dir = tmp_path / "workflows"
        workflows_dir.mkdir()

        # Create hidden directory
        (workflows_dir / ".hidden").mkdir()
        (workflows_dir / "visible").mkdir()

        script = MigrationScript(workflows_dir)
        workflows = script.scan_workflows()

        assert "visible" in workflows
        assert ".hidden" not in workflows

    def test_process_workflow(self, temp_workflows):
        """Test processing a single workflow."""
        script = MigrationScript(temp_workflows)
        script.process_workflow("test_workflow_v1")

        # Should have scanned 1 workflow, 2 phases
        assert script.stats["workflows_scanned"] == 1
        assert script.stats["phases_scanned"] == 2

    def test_process_workflow_no_phases_dir(self, tmp_path):
        """Test processing workflow without phases directory."""
        workflows_dir = tmp_path / "workflows"
        workflows_dir.mkdir()
        (workflows_dir / "no_phases").mkdir()

        script = MigrationScript(workflows_dir)
        script.process_workflow("no_phases")

        assert script.stats["workflows_scanned"] == 1
        assert script.stats["phases_scanned"] == 0

    def test_process_phase_skip_existing_gate(self, temp_workflows):
        """Test that existing gates are skipped when force=False."""
        phase_path = temp_workflows / "test_workflow_v1" / "phases" / "0"

        # Create existing gate
        gate_path = phase_path / "gate-definition.yaml"
        gate_path.write_text("existing gate")

        script = MigrationScript(temp_workflows, force=False)
        script.process_phase("test_workflow_v1", 0, phase_path)

        assert script.stats["gates_skipped"] == 1
        assert script.stats["gates_created"] == 0

    def test_process_phase_overwrite_with_force(self, temp_workflows):
        """Test that existing gates are overwritten when force=True."""
        phase_path = temp_workflows / "test_workflow_v1" / "phases" / "0"
        gate_path = phase_path / "gate-definition.yaml"
        gate_path.write_text("old gate")

        script = MigrationScript(temp_workflows, force=True)

        # Mock parse_checkpoint to return None (no checkpoint)
        with patch.object(script, "parse_checkpoint", return_value=None):
            script.process_phase("test_workflow_v1", 0, phase_path)

        # Should not skip, but won't create gate (no checkpoint)
        assert script.stats["gates_skipped"] == 0

    def test_dry_run_mode(self, temp_workflows):
        """Test that dry-run doesn't create files."""
        script = MigrationScript(temp_workflows, dry_run=True)

        # Mock methods to return values
        with (
            patch.object(script, "parse_checkpoint") as mock_parse,
            patch.object(script, "generate_gate", return_value="gate content"),
        ):

            # Return non-None to proceed with generation
            from mcp_server.config.checkpoint_loader import CheckpointRequirements

            mock_parse.return_value = CheckpointRequirements(
                evidence_schema={},
                validators={},
                cross_field_rules=[],
                strict=False,
                allow_override=True,
                source="test",
            )

            phase_path = temp_workflows / "test_workflow_v1" / "phases" / "0"
            script.process_phase("test_workflow_v1", 0, phase_path)

        # Should count as created but not write file
        assert script.stats["gates_created"] == 1
        gate_path = phase_path / "gate-definition.yaml"
        assert not gate_path.exists()  # Not created in dry-run

    def test_run_statistics(self, temp_workflows):
        """Test that run() returns correct statistics."""
        script = MigrationScript(temp_workflows, dry_run=True)

        results = script.run()

        assert results["workflows_scanned"] == 2
        assert results["phases_scanned"] == 3  # 2 + 1 phases
        assert results["errors"] == 0

    def test_run_with_error_handling(self, temp_workflows):
        """Test that errors are caught and counted."""
        script = MigrationScript(temp_workflows)

        # Mock process_workflow to raise error
        with patch.object(
            script, "process_workflow", side_effect=Exception("test error")
        ):
            results = script.run()

        assert results["errors"] == 2  # 2 workflows both error
        assert results["workflows_scanned"] == 0  # Never incremented

    def test_write_gate(self, temp_workflows):
        """Test writing gate file."""
        script = MigrationScript(temp_workflows)
        gate_path = temp_workflows / "test_gate.yaml"
        content = "test: content"

        script.write_gate(gate_path, content)

        assert gate_path.exists()
        assert gate_path.read_text() == content

    def test_log_statistics(self, temp_workflows, caplog):
        """Test statistics logging."""
        script = MigrationScript(temp_workflows)
        script.stats["workflows_scanned"] = 5
        script.stats["phases_scanned"] = 20
        script.stats["gates_created"] = 18
        script.stats["gates_skipped"] = 2
        script.stats["errors"] = 0

        with caplog.at_level("INFO"):
            script.log_statistics()

        assert "Migration Complete" in caplog.text
        assert "Workflows scanned: 5" in caplog.text
        assert "Phases scanned: 20" in caplog.text
        assert "Gates created: 18" in caplog.text


class TestMainFunction:
    """Tests for main() entry point."""

    def test_main_with_dry_run(self, tmp_path, monkeypatch):
        """Test main function with dry-run flag."""
        workflows_dir = tmp_path / "workflows"
        workflows_dir.mkdir()

        # Mock sys.argv
        test_args = [
            "migrate-checkpoints-to-gates.py",
            "--workflows-path",
            str(workflows_dir),
            "--dry-run",
        ]
        monkeypatch.setattr("sys.argv", test_args)

        from scripts.migrate_checkpoints_to_gates import main

        exit_code = main()

        assert exit_code == 0  # Success

    def test_main_with_errors(self, tmp_path, monkeypatch):
        """Test main function returns error code on failures."""
        # Non-existent path will cause scan to fail
        nonexistent = tmp_path / "nonexistent"

        test_args = [
            "migrate-checkpoints-to-gates.py",
            "--workflows-path",
            str(nonexistent),
        ]
        monkeypatch.setattr("sys.argv", test_args)

        from scripts.migrate_checkpoints_to_gates import main

        # Should succeed even with no workflows (not an error condition)
        exit_code = main()
        assert exit_code == 0


class TestCheckpointParsing:
    """Tests for checkpoint parsing functionality."""

    @pytest.fixture
    def script(self, tmp_path):
        """Create MigrationScript instance."""
        return MigrationScript(tmp_path)

    def test_parse_checkpoint_no_phase_md(self, script, tmp_path):
        """Test parsing when phase.md doesn't exist."""
        phase_path = tmp_path / "phase_dir"
        phase_path.mkdir()

        result = script.parse_checkpoint(phase_path)

        assert result is None

    def test_parse_checkpoint_no_checkpoint_section(self, script, tmp_path):
        """Test parsing when no checkpoint section in phase.md."""
        phase_path = tmp_path / "phase_dir"
        phase_path.mkdir()

        phase_md = phase_path / "phase.md"
        phase_md.write_text("# Phase 1\n\nNo checkpoint here")

        result = script.parse_checkpoint(phase_path)

        assert result is None

    def test_parse_checkpoint_with_fields(self, script, tmp_path):
        """Test successful checkpoint parsing with evidence fields."""
        phase_path = tmp_path / "phase_dir"
        phase_path.mkdir()

        phase_md = phase_path / "phase.md"
        phase_md.write_text(
            """
# Phase 1

## Checkpoint

Evidence required:
- **business_goals**: Number of business goals defined
- **user_stories**: Count of user stories created
- **test_strategy**: Description of testing approach
"""
        )

        result = script.parse_checkpoint(phase_path)

        assert result is not None
        assert len(result.evidence_schema) == 3
        assert "business_goals" in result.evidence_schema
        assert "user_stories" in result.evidence_schema
        assert "test_strategy" in result.evidence_schema

        # Check types inferred correctly
        assert result.evidence_schema["business_goals"].type == "integer"
        assert result.evidence_schema["user_stories"].type == "integer"
        assert result.evidence_schema["test_strategy"].type == "string"

    def test_extract_checkpoint_section_variants(self, script):
        """Test extracting checkpoint section with different headers."""
        test_cases = [
            ("## Checkpoint\nfield: value", "field: value"),
            ("## Phase Checkpoint\nfield: value", "field: value"),
            ("## Validation Gate\nfield: value", "field: value"),
            ("## Evidence Required\nfield: value", "field: value"),
        ]

        for content, expected in test_cases:
            result = script._extract_checkpoint_section(content)
            assert result is not None
            assert expected in result

    def test_parse_evidence_fields_formats(self, script):
        """Test parsing evidence fields in different formats."""
        checkpoint_text = """
**business_goals**: Number of goals
- **user_stories**: Story count
- functional_requirements: List of requirements
`test_coverage`: Coverage percentage
"""

        result = script._parse_evidence_fields(checkpoint_text)

        assert len(result) >= 3  # Should parse at least 3 fields
        assert "business_goals" in result
        assert "user_stories" in result

    def test_infer_field_type_integer(self, script):
        """Test type inference for integer fields."""
        descriptions = [
            "Number of goals",
            "Count of items",
            "Total files",
            "Sum of values",
            "Quantity needed",
        ]

        for desc in descriptions:
            assert script._infer_field_type(desc) == "integer"

    def test_infer_field_type_boolean(self, script):
        """Test type inference for boolean fields."""
        descriptions = [
            "True/false flag",
            "Yes/no indicator",
            "Whether tests pass",
            "If coverage sufficient",
        ]

        for desc in descriptions:
            assert script._infer_field_type(desc) == "boolean"

    def test_infer_field_type_list(self, script):
        """Test type inference for list fields."""
        descriptions = [
            "List of items",
            "Array of values",
            "Collection of tests",
            "Multiple entries",
        ]

        for desc in descriptions:
            assert script._infer_field_type(desc) == "list"

    def test_infer_field_type_object(self, script):
        """Test type inference for object fields."""
        descriptions = [
            "Dictionary of settings",
            "Mapping of values",
            "Object structure",
            "Configuration dict",
        ]

        for desc in descriptions:
            assert script._infer_field_type(desc) == "object"

    def test_infer_field_type_default_string(self, script):
        """Test type inference defaults to string."""
        descriptions = ["Some description", "Path to file", "Name of component"]

        for desc in descriptions:
            assert script._infer_field_type(desc) == "string"

    def test_is_field_required_optional(self, script):
        """Test required detection for optional fields."""
        descriptions = [
            "Optional field",
            "May be provided if applicable",
            "This is optional",
        ]

        for desc in descriptions:
            assert script._is_field_required(desc) is False

    def test_is_field_required_mandatory(self, script):
        """Test required detection for mandatory fields."""
        descriptions = ["Required field", "Must be provided", "Mandatory input"]

        for desc in descriptions:
            assert script._is_field_required(desc) is True

    def test_is_field_required_default_true(self, script):
        """Test required defaults to True."""
        assert script._is_field_required("Some field description") is True


class TestGateGeneration:
    """Tests for gate generation functionality."""

    @pytest.fixture
    def script(self, tmp_path):
        """Create MigrationScript instance."""
        return MigrationScript(tmp_path)

    @pytest.fixture
    def sample_requirements(self):
        """Create sample CheckpointRequirements."""
        from mcp_server.config.checkpoint_loader import (
            CheckpointRequirements,
            FieldSchema,
        )

        return CheckpointRequirements(
            evidence_schema={
                "tests_written": FieldSchema(
                    name="tests_written",
                    type="integer",
                    required=True,
                    validator=None,
                    validator_params=None,
                    description="Number of tests",
                ),
                "coverage": FieldSchema(
                    name="coverage",
                    type="integer",
                    required=True,
                    validator="in_range",
                    validator_params={"min": 0, "max": 100},
                    description="Coverage percentage",
                ),
            },
            validators={},
            cross_field_rules=[],
            strict=False,
            allow_override=True,
            source="parsed",
        )

    def test_generate_gate_basic(self, script, sample_requirements):
        """Test basic gate generation."""
        yaml_content = script.generate_gate(sample_requirements)

        assert yaml_content is not None
        assert len(yaml_content) > 0
        assert "checkpoint:" in yaml_content
        assert "evidence_schema:" in yaml_content
        assert "tests_written:" in yaml_content
        assert "coverage:" in yaml_content

    def test_generate_gate_includes_comments(self, script, sample_requirements):
        """Test that generated YAML includes helpful comments."""
        yaml_content = script.generate_gate(sample_requirements)

        assert "# Gate Definition" in yaml_content
        assert "# Auto-generated" in yaml_content
        assert "# Fields: 2" in yaml_content

    def test_generate_gate_valid_yaml(self, script, sample_requirements):
        """Test that generated content is valid YAML."""
        import yaml

        yaml_content = script.generate_gate(sample_requirements)

        # Parse YAML (should not raise exception)
        parsed = yaml.safe_load(yaml_content)

        assert parsed is not None
        assert "checkpoint" in parsed
        assert "evidence_schema" in parsed

    def test_generate_gate_preserves_structure(self, script, sample_requirements):
        """Test that gate preserves CheckpointRequirements structure."""
        import yaml

        yaml_content = script.generate_gate(sample_requirements)
        parsed = yaml.safe_load(yaml_content)

        # Check checkpoint settings
        assert parsed["checkpoint"]["strict"] is False
        assert parsed["checkpoint"]["allow_override"] is True

        # Check evidence schema
        assert "tests_written" in parsed["evidence_schema"]
        assert "coverage" in parsed["evidence_schema"]

        # Check field details
        tests_field = parsed["evidence_schema"]["tests_written"]
        assert tests_field["type"] == "integer"
        assert tests_field["required"] is True

        coverage_field = parsed["evidence_schema"]["coverage"]
        assert coverage_field["validator"] == "in_range"
