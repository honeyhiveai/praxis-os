"""Tests for EvidenceValidator."""

from pathlib import Path

import pytest
from ouroboros.subsystems.workflow.evidence_validator import (
    EvidenceValidator,
    ValidationResult,
)
from ouroboros.subsystems.workflow.hidden_schemas import (
    CrossFieldRule,
    EvidenceSchema,
    FieldSchema,
)


class TestEvidenceValidator:
    """Tests for EvidenceValidator."""

    @pytest.fixture
    def validator(self, tmp_path):
        """Create evidence validator."""
        return EvidenceValidator(workspace_root=tmp_path)

    @pytest.fixture
    def sample_schema(self):
        """Sample evidence schema."""
        return EvidenceSchema(
            evidence_fields={
                "task_completed": FieldSchema(
                    name="task_completed",
                    type="boolean",
                    required=True,
                    validator=None,
                    validator_params=None,
                    description="Task completed",
                ),
                "description": FieldSchema(
                    name="description",
                    type="string",
                    required=True,
                    validator=None,
                    validator_params=None,
                    description="Task description",
                ),
                "line_count": FieldSchema(
                    name="line_count",
                    type="integer",
                    required=False,
                    validator="positive",
                    validator_params=None,
                    description="Line count",
                ),
            },
            validators={"positive": "lambda x: x > 0"},
            cross_field_rules=[],
            strict=True,
            allow_override=False,
            source="yaml",
        )

    def test_validate_passes_with_valid_evidence(self, validator, sample_schema):
        """Test validation passes with valid evidence."""
        evidence = {
            "task_completed": True,
            "description": "Completed task",
            "line_count": 100,
        }

        result = validator.validate(evidence, sample_schema)

        assert result.passed is True
        assert len(result.errors) == 0

    def test_validate_fails_missing_required_field(self, validator, sample_schema):
        """Test validation fails when required field missing."""
        evidence = {"task_completed": True}  # Missing description

        result = validator.validate(evidence, sample_schema)

        assert result.passed is False
        assert any("description" in err and "required" in err for err in result.errors)

    def test_validate_fails_wrong_type(self, validator, sample_schema):
        """Test validation fails when field has wrong type."""
        evidence = {
            "task_completed": "not a boolean",
            "description": "Test description",
        }

        result = validator.validate(evidence, sample_schema)

        assert result.passed is False
        assert any(
            "task_completed" in err and "boolean" in err for err in result.errors
        )

    def test_validate_custom_validator_passes(self, validator, sample_schema):
        """Test custom validator passes."""
        evidence = {
            "task_completed": True,
            "description": "Test description",
            "line_count": 50,
        }

        result = validator.validate(evidence, sample_schema)

        assert result.passed is True

    def test_validate_custom_validator_fails(self, validator, sample_schema):
        """Test custom validator fails."""
        evidence = {
            "task_completed": True,
            "description": "Test description",
            "line_count": -10,
        }

        result = validator.validate(evidence, sample_schema)

        assert result.passed is False
        assert any("line_count" in err and "validation" in err for err in result.errors)

    def test_validate_cross_field_rule_passes(self, validator, sample_schema):
        """Test cross-field rule passes."""
        # Create new schema with cross-field rule (schemas are immutable)
        schema = EvidenceSchema(
            evidence_fields=sample_schema.evidence_fields,
            validators=sample_schema.validators,
            cross_field_rules=[
                CrossFieldRule(
                    rule="lambda e: e.get('line_count', 1) > 0",
                    error_message="Line count must be positive",
                )
            ],
            strict=sample_schema.strict,
            allow_override=sample_schema.allow_override,
            source=sample_schema.source,
        )

        evidence = {
            "task_completed": True,
            "description": "Test description",
            "line_count": 100,
        }

        result = validator.validate(evidence, schema)

        assert result.passed is True

    def test_validate_cross_field_rule_fails(self, validator, sample_schema):
        """Test cross-field rule fails."""
        # Create new schema with cross-field rule (schemas are immutable)
        schema = EvidenceSchema(
            evidence_fields=sample_schema.evidence_fields,
            validators=sample_schema.validators,
            cross_field_rules=[
                CrossFieldRule(
                    rule="lambda e: e.get('line_count', 1) > 0",
                    error_message="Line count must be positive",
                )
            ],
            strict=sample_schema.strict,
            allow_override=sample_schema.allow_override,
            source=sample_schema.source,
        )

        evidence = {
            "task_completed": True,
            "description": "Test description",
            "line_count": 0,
        }

        result = validator.validate(evidence, schema)

        assert result.passed is False
        assert any("Line count must be positive" in err for err in result.errors)

    def test_validate_artifact_path_exists(self, validator, sample_schema, tmp_path):
        """Test artifact path validation when file exists."""
        # Create artifact file
        artifact_file = tmp_path / "test_artifact.txt"
        artifact_file.write_text("test content")

        # Add artifact field to schema (create new schema)
        new_fields = dict(sample_schema.evidence_fields)
        new_fields["artifact_path"] = FieldSchema(
            name="artifact_path",
            type="string",
            required=True,
            validator=None,
            validator_params=None,
            description="Artifact path",
        )
        schema = EvidenceSchema(
            evidence_fields=new_fields,
            validators=sample_schema.validators,
            cross_field_rules=sample_schema.cross_field_rules,
            strict=sample_schema.strict,
            allow_override=sample_schema.allow_override,
            source=sample_schema.source,
        )

        evidence = {
            "task_completed": True,
            "description": "Test description",
            "artifact_path": "test_artifact.txt",
        }

        result = validator.validate(evidence, schema)

        assert result.passed is True

    def test_validate_artifact_path_missing(self, validator, sample_schema, tmp_path):
        """Test artifact path validation when file missing."""
        # Add artifact field to schema (create new schema)
        new_fields = dict(sample_schema.evidence_fields)
        new_fields["artifact_path"] = FieldSchema(
            name="artifact_path",
            type="string",
            required=True,
            validator=None,
            validator_params=None,
            description="Artifact path",
        )
        schema = EvidenceSchema(
            evidence_fields=new_fields,
            validators=sample_schema.validators,
            cross_field_rules=sample_schema.cross_field_rules,
            strict=sample_schema.strict,
            allow_override=sample_schema.allow_override,
            source=sample_schema.source,
        )

        evidence = {
            "task_completed": True,
            "description": "Test description",
            "artifact_path": "nonexistent.txt",
        }

        result = validator.validate(evidence, schema)

        assert result.passed is False
        assert any(
            "Artifact file" in err and "not found" in err for err in result.errors
        )

    def test_validate_multiple_errors(self, validator, sample_schema):
        """Test validation collects multiple errors."""
        evidence = {
            # Missing task_completed
            # Missing description
            "line_count": -5,  # Invalid value
        }

        result = validator.validate(evidence, sample_schema)

        assert result.passed is False
        assert len(result.errors) >= 3  # At least 3 errors

    def test_validate_permissive_schema_allows_anything(self, validator):
        """Test that permissive schema allows any evidence."""
        schema = EvidenceSchema(
            evidence_fields={},
            validators={},
            cross_field_rules=[],
            strict=False,
            allow_override=True,
            source="permissive",
        )

        evidence = {"random_field": "random_value"}

        result = validator.validate(evidence, schema)

        assert result.passed is True
        assert len(result.errors) == 0


class TestValidationResult:
    """Tests for ValidationResult."""

    def test_validation_result_creation(self):
        """Test creating validation result."""
        result = ValidationResult(passed=True)

        assert result.passed is True
        assert result.errors == []
        assert result.warnings == []
        assert result.field_errors == {}

    def test_add_error(self):
        """Test adding error."""
        result = ValidationResult(passed=True)
        result.add_error("Test error", field_name="test_field")

        assert result.passed is False
        assert "Test error" in result.errors
        assert "test_field" in result.field_errors
        assert "Test error" in result.field_errors["test_field"]

    def test_add_warning(self):
        """Test adding warning."""
        result = ValidationResult(passed=True)
        result.add_warning("Test warning")

        assert result.passed is True  # Warnings don't fail
        assert "Test warning" in result.warnings

    def test_to_dict(self):
        """Test serialization to dictionary."""
        result = ValidationResult(passed=False)
        result.add_error("Error 1", field_name="field1")
        result.add_warning("Warning 1")

        data = result.to_dict()

        assert data["passed"] is False
        assert "Error 1" in data["errors"]
        assert "Warning 1" in data["warnings"]
        assert "field1" in data["field_errors"]
