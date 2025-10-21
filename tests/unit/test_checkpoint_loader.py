"""
Unit tests for CheckpointLoader.

Tests three-tier fallback strategy, caching, thread safety, and YAML parsing.
"""

import threading
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import yaml

from mcp_server.config.checkpoint_loader import (
    CheckpointLoader,
    CheckpointLoaderError,
    CheckpointRequirements,
    CrossFieldRule,
    FieldSchema,
)


class TestFieldSchema:
    """Tests for FieldSchema dataclass."""

    def test_validate_type_boolean(self):
        """Test boolean type validation."""
        schema = FieldSchema("test", "boolean", True, None, None, "Test field")

        assert schema.validate_type(True) is True
        assert schema.validate_type(False) is True
        assert schema.validate_type("not bool") is False
        assert schema.validate_type(42) is False

    def test_validate_type_integer(self):
        """Test integer type validation."""
        schema = FieldSchema("test", "integer", True, None, None, "Test field")

        assert schema.validate_type(42) is True
        assert schema.validate_type(0) is True
        assert schema.validate_type(-1) is True
        assert schema.validate_type("42") is False
        assert schema.validate_type(42.0) is False  # float != int in Python

    def test_validate_type_string(self):
        """Test string type validation."""
        schema = FieldSchema("test", "string", True, None, None, "Test field")

        assert schema.validate_type("hello") is True
        assert schema.validate_type("") is True
        assert schema.validate_type(42) is False

    def test_validate_type_object(self):
        """Test object (dict) type validation."""
        schema = FieldSchema("test", "object", True, None, None, "Test field")

        assert schema.validate_type({"key": "value"}) is True
        assert schema.validate_type({}) is True
        assert schema.validate_type([]) is False
        assert schema.validate_type("not dict") is False

    def test_validate_type_list(self):
        """Test list type validation."""
        schema = FieldSchema("test", "list", True, None, None, "Test field")

        assert schema.validate_type([1, 2, 3]) is True
        assert schema.validate_type([]) is True
        assert schema.validate_type({}) is False
        assert schema.validate_type("not list") is False

    def test_to_dict(self):
        """Test serialization to dictionary."""
        schema = FieldSchema(
            name="test_field",
            type="integer",
            required=True,
            validator="positive",
            validator_params={"min": 1},
            description="Test description",
        )

        result = schema.to_dict()

        assert result["name"] == "test_field"
        assert result["type"] == "integer"
        assert result["required"] is True
        assert result["validator"] == "positive"
        assert result["validator_params"] == {"min": 1}
        assert result["description"] == "Test description"


class TestCrossFieldRule:
    """Tests for CrossFieldRule dataclass."""

    def test_evaluate_simple_rule(self):
        """Test simple cross-field rule evaluation."""
        rule = CrossFieldRule(
            rule="lambda e: e.get('a', 0) > e.get('b', 0)",
            error_message="a must be greater than b",
        )

        assert rule.evaluate({"a": 5, "b": 3}) is True
        assert rule.evaluate({"a": 3, "b": 5}) is False

    def test_evaluate_with_defaults(self):
        """Test rule evaluation with missing fields."""
        rule = CrossFieldRule(
            rule="lambda e: e.get('count', 0) > 0",
            error_message="count must be positive",
        )

        assert rule.evaluate({"count": 5}) is True
        assert rule.evaluate({}) is False  # missing, defaults to 0

    def test_evaluate_invalid_syntax_raises(self):
        """Test that invalid rule syntax raises error."""
        rule = CrossFieldRule(rule="invalid syntax!", error_message="error")

        with pytest.raises(ValueError, match="evaluation failed"):
            rule.evaluate({})

    def test_to_dict(self):
        """Test serialization to dictionary."""
        rule = CrossFieldRule(rule="lambda e: True", error_message="Test error")

        result = rule.to_dict()

        assert result["rule"] == "lambda e: True"
        assert result["error_message"] == "Test error"


class TestCheckpointRequirements:
    """Tests for CheckpointRequirements dataclass."""

    def test_get_required_fields(self):
        """Test extracting required field names."""
        requirements = CheckpointRequirements(
            evidence_schema={
                "field1": FieldSchema("field1", "boolean", True, None, None, "Req"),
                "field2": FieldSchema("field2", "integer", False, None, None, "Opt"),
                "field3": FieldSchema("field3", "string", True, None, None, "Req"),
            },
            validators={},
            cross_field_rules=[],
            strict=False,
            allow_override=True,
            source="yaml",
        )

        required = requirements.get_required_fields()

        assert len(required) == 2
        assert "field1" in required
        assert "field3" in required
        assert "field2" not in required

    def test_to_dict(self):
        """Test serialization to dictionary."""
        requirements = CheckpointRequirements(
            evidence_schema={
                "test": FieldSchema("test", "boolean", True, None, None, "Test")
            },
            validators={"positive": "lambda x: x > 0"},
            cross_field_rules=[CrossFieldRule("lambda e: True", "error")],
            strict=False,
            allow_override=True,
            source="yaml",
        )

        result = requirements.to_dict()

        assert "evidence_schema" in result
        assert "test" in result["evidence_schema"]
        assert result["validators"] == {"positive": "lambda x: x > 0"}
        assert len(result["cross_field_rules"]) == 1
        assert result["strict"] is False
        assert result["source"] == "yaml"


class TestCheckpointLoader:
    """Tests for CheckpointLoader."""

    @pytest.fixture
    def loader(self, tmp_path):
        """Create CheckpointLoader with temporary workflows directory."""
        return CheckpointLoader(tmp_path)

    @pytest.fixture
    def sample_gate_yaml(self):
        """Sample gate-definition.yaml content."""
        return """
checkpoint:
  strict: false
  allow_override: true

evidence_schema:
  business_goals:
    type: integer
    required: true
    validator: positive
    description: "Number of business goals"
  
  optional_field:
    type: string
    required: false
    description: "Optional field"

validators:
  positive: "lambda x: x > 0"

cross_field_validation:
  - rule: "lambda e: e.get('business_goals', 0) > 0"
    error_message: "business_goals must be positive"
"""

    def test_load_from_yaml_success(self, loader, tmp_path, sample_gate_yaml):
        """Test successful YAML loading."""
        # Create gate file
        gate_dir = tmp_path / "test_workflow" / "phases" / "1"
        gate_dir.mkdir(parents=True)
        (gate_dir / "gate-definition.yaml").write_text(sample_gate_yaml)

        # Load requirements
        requirements = loader.load_checkpoint_requirements("test_workflow", 1)

        assert requirements.source == "yaml"
        assert requirements.strict is False
        assert requirements.allow_override is True
        assert "business_goals" in requirements.evidence_schema
        assert "positive" in requirements.validators
        assert len(requirements.cross_field_rules) == 1

    def test_load_from_yaml_file_not_found(self, loader):
        """Test YAML loading when file doesn't exist."""
        # Should fall back to permissive gate
        requirements = loader.load_checkpoint_requirements("nonexistent", 1)

        assert requirements.source == "permissive"
        assert requirements.strict is False
        assert len(requirements.evidence_schema) == 0

    def test_load_from_yaml_invalid_yaml(self, loader, tmp_path):
        """Test YAML loading with invalid syntax."""
        # Create invalid YAML file
        gate_dir = tmp_path / "test_workflow" / "phases" / "1"
        gate_dir.mkdir(parents=True)
        (gate_dir / "gate-definition.yaml").write_text("invalid: yaml: syntax:")

        # Should fall back to permissive gate
        requirements = loader.load_checkpoint_requirements("test_workflow", 1)

        assert requirements.source == "permissive"

    def test_load_from_yaml_missing_required_section(self, loader, tmp_path):
        """Test YAML loading with missing required section."""
        gate_dir = tmp_path / "test_workflow" / "phases" / "1"
        gate_dir.mkdir(parents=True)
        (gate_dir / "gate-definition.yaml").write_text(
            """
checkpoint:
  strict: false
# Missing evidence_schema!
"""
        )

        # Should fall back to permissive gate
        requirements = loader.load_checkpoint_requirements("test_workflow", 1)

        assert requirements.source == "permissive"

    def test_caching_second_load_uses_cache(self, loader, tmp_path, sample_gate_yaml):
        """Test that second load uses cached result."""
        # Create gate file
        gate_dir = tmp_path / "test_workflow" / "phases" / "1"
        gate_dir.mkdir(parents=True)
        gate_file = gate_dir / "gate-definition.yaml"
        gate_file.write_text(sample_gate_yaml)

        # First load
        req1 = loader.load_checkpoint_requirements("test_workflow", 1)

        # Modify file (cache should prevent re-reading)
        gate_file.write_text("checkpoint: {}\nevidence_schema: {}")

        # Second load (should use cache, not see modification)
        req2 = loader.load_checkpoint_requirements("test_workflow", 1)

        # Should be same cached instance
        assert req1 is req2
        assert "business_goals" in req2.evidence_schema  # Still has original data

    def test_cache_key_different_workflows(self, loader, tmp_path, sample_gate_yaml):
        """Test that different workflows have different cache keys."""
        # Create gates for two workflows
        for workflow in ["workflow1", "workflow2"]:
            gate_dir = tmp_path / workflow / "phases" / "1"
            gate_dir.mkdir(parents=True)
            (gate_dir / "gate-definition.yaml").write_text(sample_gate_yaml)

        req1 = loader.load_checkpoint_requirements("workflow1", 1)
        req2 = loader.load_checkpoint_requirements("workflow2", 1)

        # Should be different instances
        assert req1 is not req2

    def test_cache_key_different_phases(self, loader, tmp_path, sample_gate_yaml):
        """Test that different phases have different cache keys."""
        # Create gates for two phases
        for phase in [1, 2]:
            gate_dir = tmp_path / "test_workflow" / "phases" / str(phase)
            gate_dir.mkdir(parents=True)
            (gate_dir / "gate-definition.yaml").write_text(sample_gate_yaml)

        req1 = loader.load_checkpoint_requirements("test_workflow", 1)
        req2 = loader.load_checkpoint_requirements("test_workflow", 2)

        # Should be different instances
        assert req1 is not req2

    def test_thread_safety(self, loader, tmp_path, sample_gate_yaml):
        """Test thread-safe concurrent access to loader."""
        # Create gate file
        gate_dir = tmp_path / "test_workflow" / "phases" / "1"
        gate_dir.mkdir(parents=True)
        (gate_dir / "gate-definition.yaml").write_text(sample_gate_yaml)

        results = []

        def load():
            req = loader.load_checkpoint_requirements("test_workflow", 1)
            results.append(req)

        # Create 10 threads that all load concurrently
        threads = [threading.Thread(target=load) for _ in range(10)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All should get the same cached instance
        assert len(results) == 10
        assert all(r is results[0] for r in results)

    def test_permissive_gate_accepts_any_evidence(self, loader):
        """Test that permissive gate has empty schema."""
        requirements = loader._get_permissive_gate()

        assert requirements.source == "permissive"
        assert requirements.strict is False
        assert requirements.allow_override is True
        assert len(requirements.evidence_schema) == 0
        assert len(requirements.validators) == 0
        assert len(requirements.cross_field_rules) == 0

    def test_parse_gate_content_with_validators(self, loader):
        """Test parsing gate content with validators."""
        content = {
            "checkpoint": {"strict": True, "allow_override": False},
            "evidence_schema": {
                "count": {
                    "type": "integer",
                    "required": True,
                    "validator": "in_range",
                    "validator_params": {"min": 1, "max": 10},
                    "description": "Count field",
                }
            },
            "validators": {"in_range": "lambda x, min, max: min <= x <= max"},
        }

        requirements = loader._parse_gate_content(content, "yaml")

        assert requirements.strict is True
        assert requirements.allow_override is False
        assert "count" in requirements.evidence_schema

        schema = requirements.evidence_schema["count"]
        assert schema.validator == "in_range"
        assert schema.validator_params == {"min": 1, "max": 10}
        assert "in_range" in requirements.validators

    def test_parse_gate_content_with_cross_field_rules(self, loader):
        """Test parsing gate content with cross-field validation."""
        content = {
            "checkpoint": {"strict": False, "allow_override": True},
            "evidence_schema": {},
            "cross_field_validation": [
                {
                    "rule": "lambda e: e['a'] > e['b']",
                    "error_message": "a must be greater than b",
                }
            ],
        }

        requirements = loader._parse_gate_content(content, "yaml")

        assert len(requirements.cross_field_rules) == 1
        rule = requirements.cross_field_rules[0]
        assert rule.error_message == "a must be greater than b"
