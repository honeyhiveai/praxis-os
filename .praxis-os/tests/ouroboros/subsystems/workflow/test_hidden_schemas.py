"""Tests for HiddenSchemas."""

from pathlib import Path

import pytest
import yaml
from ouroboros.subsystems.workflow.hidden_schemas import (
    CrossFieldRule,
    EvidenceSchema,
    FieldSchema,
    HiddenSchemas,
)


class TestHiddenSchemas:
    """Tests for HiddenSchemas loader."""

    @pytest.fixture
    def temp_workflows_dir(self, tmp_path):
        """Create temporary workflows directory."""
        workflows_dir = tmp_path / "workflows"
        workflows_dir.mkdir()
        return workflows_dir

    @pytest.fixture
    def hidden_schemas(self, temp_workflows_dir):
        """Create HiddenSchemas instance."""
        return HiddenSchemas(temp_workflows_dir)

    @pytest.fixture
    def sample_gate_yaml(self):
        """Sample gate-definition.yaml content."""
        return {
            "checkpoint": {"enabled": True, "strict": True, "allow_override": False},
            "evidence_schema": {
                "task_completed": {
                    "type": "boolean",
                    "required": True,
                    "description": "Task completed",
                },
                "file_created": {
                    "type": "string",
                    "required": True,
                    "description": "File path created",
                },
                "line_count": {
                    "type": "integer",
                    "required": False,
                    "validator": "positive",
                    "description": "Number of lines",
                },
            },
            "validators": {"positive": "lambda x: x > 0"},
            "cross_field_validation": [
                {
                    "rule": "lambda e: e.get('line_count', 1) > 0",
                    "error_message": "Line count must be positive",
                }
            ],
        }

    def create_workflow_with_gate(
        self, workflows_dir, workflow_type, phase, gate_content
    ):
        """Helper to create workflow directory with gate definition."""
        workflow_dir = workflows_dir / workflow_type / "phases" / str(phase)
        workflow_dir.mkdir(parents=True)

        gate_file = workflow_dir / "gate-definition.yaml"
        gate_file.write_text(yaml.dump(gate_content))

        return gate_file

    def test_load_schema_from_yaml(
        self, hidden_schemas, temp_workflows_dir, sample_gate_yaml
    ):
        """Test loading schema from YAML file."""
        self.create_workflow_with_gate(
            temp_workflows_dir, "test_workflow", 0, sample_gate_yaml
        )

        schema = hidden_schemas.get_schema("test_workflow", 0)

        assert schema.source == "yaml"
        assert schema.strict is True
        assert schema.allow_override is False
        assert "task_completed" in schema.evidence_fields
        assert "file_created" in schema.evidence_fields
        assert "line_count" in schema.evidence_fields

    def test_schema_caching(self, hidden_schemas, temp_workflows_dir, sample_gate_yaml):
        """Test that schemas are cached."""
        self.create_workflow_with_gate(
            temp_workflows_dir, "test_workflow", 0, sample_gate_yaml
        )

        # Load twice
        schema1 = hidden_schemas.get_schema("test_workflow", 0)
        schema2 = hidden_schemas.get_schema("test_workflow", 0)

        # Should be same instance (cached)
        assert schema1 is schema2

    def test_missing_gate_returns_permissive_schema(self, hidden_schemas):
        """Test that missing gate-definition.yaml returns permissive schema."""
        schema = hidden_schemas.get_schema("nonexistent_workflow", 0)

        assert schema.source == "permissive"
        assert schema.strict is False
        assert schema.allow_override is True
        assert len(schema.evidence_fields) == 0

    def test_disabled_gate_returns_permissive_schema(
        self, hidden_schemas, temp_workflows_dir
    ):
        """Test that disabled gate returns permissive schema."""
        gate_content = {
            "checkpoint": {"enabled": False, "strict": True},
            "evidence_schema": {
                "task_completed": {"type": "boolean", "required": True}
            },
        }
        self.create_workflow_with_gate(
            temp_workflows_dir, "test_workflow", 0, gate_content
        )

        schema = hidden_schemas.get_schema("test_workflow", 0)

        assert schema.source == "permissive"
        assert schema.strict is False

    def test_parse_field_schemas(
        self, hidden_schemas, temp_workflows_dir, sample_gate_yaml
    ):
        """Test parsing field schemas."""
        self.create_workflow_with_gate(
            temp_workflows_dir, "test_workflow", 0, sample_gate_yaml
        )

        schema = hidden_schemas.get_schema("test_workflow", 0)

        task_field = schema.evidence_fields["task_completed"]
        assert task_field.name == "task_completed"
        assert task_field.type == "boolean"
        assert task_field.required is True
        assert task_field.validator is None

        line_count_field = schema.evidence_fields["line_count"]
        assert line_count_field.validator == "positive"

    def test_parse_validators(
        self, hidden_schemas, temp_workflows_dir, sample_gate_yaml
    ):
        """Test parsing validators."""
        self.create_workflow_with_gate(
            temp_workflows_dir, "test_workflow", 0, sample_gate_yaml
        )

        schema = hidden_schemas.get_schema("test_workflow", 0)

        assert "positive" in schema.validators
        assert schema.validators["positive"] == "lambda x: x > 0"

    def test_parse_cross_field_rules(
        self, hidden_schemas, temp_workflows_dir, sample_gate_yaml
    ):
        """Test parsing cross-field rules."""
        self.create_workflow_with_gate(
            temp_workflows_dir, "test_workflow", 0, sample_gate_yaml
        )

        schema = hidden_schemas.get_schema("test_workflow", 0)

        assert len(schema.cross_field_rules) == 1
        rule = schema.cross_field_rules[0]
        assert "lambda e:" in rule.rule
        assert "Line count must be positive" in rule.error_message

    def test_get_required_fields(
        self, hidden_schemas, temp_workflows_dir, sample_gate_yaml
    ):
        """Test getting required fields."""
        self.create_workflow_with_gate(
            temp_workflows_dir, "test_workflow", 0, sample_gate_yaml
        )

        schema = hidden_schemas.get_schema("test_workflow", 0)
        required = schema.get_required_fields()

        assert "task_completed" in required
        assert "file_created" in required
        assert "line_count" not in required

    def test_is_schema_exposed_always_false(self, hidden_schemas):
        """Test that schemas are never exposed."""
        assert hidden_schemas.is_schema_exposed() is False

    def test_corrupted_yaml_returns_permissive(
        self, hidden_schemas, temp_workflows_dir
    ):
        """Test that corrupted YAML falls back to permissive."""
        workflow_dir = temp_workflows_dir / "test_workflow" / "phases" / "0"
        workflow_dir.mkdir(parents=True)

        gate_file = workflow_dir / "gate-definition.yaml"
        gate_file.write_text("{ invalid yaml }")

        schema = hidden_schemas.get_schema("test_workflow", 0)

        assert schema.source == "permissive"


class TestCrossFieldRule:
    """Tests for CrossFieldRule."""

    def test_cross_field_rule_evaluate_passes(self):
        """Test cross-field rule evaluation (passing)."""
        rule = CrossFieldRule(
            rule="lambda e: e['a'] > e['b']", error_message="A must be greater than B"
        )

        assert rule.evaluate({"a": 10, "b": 5}) is True

    def test_cross_field_rule_evaluate_fails(self):
        """Test cross-field rule evaluation (failing)."""
        rule = CrossFieldRule(
            rule="lambda e: e['a'] > e['b']", error_message="A must be greater than B"
        )

        assert rule.evaluate({"a": 5, "b": 10}) is False

    def test_cross_field_rule_invalid_syntax_raises_error(self):
        """Test that invalid syntax raises error."""
        rule = CrossFieldRule(rule="invalid python", error_message="Error")

        with pytest.raises(ValueError, match="evaluation failed"):
            rule.evaluate({"a": 1})
