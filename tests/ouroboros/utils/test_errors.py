"""
Unit tests for ouroboros.utils.errors.

Tests actionable error classes including:
    - ActionableError base class
    - ConfigValidationError
    - EvidenceValidationError
    - IndexError
    - WorkflowExecutionError
    - Error formatting and serialization
"""

import pytest
from ouroboros.utils.errors import (
    ActionableError,
    ConfigValidationError,
    EvidenceValidationError,
    IndexError,
    WorkflowExecutionError,
)


class TestActionableError:
    """Test ActionableError base class."""

    def test_actionable_error_creation(self):
        """ActionableError should initialize with all required fields."""
        error = ActionableError(
            what_failed="Operation failed",
            why_failed="Resource not found",
            how_to_fix="Create resource: touch /path/to/file",
        )

        assert error.what_failed == "Operation failed"
        assert error.why_failed == "Resource not found"
        assert error.how_to_fix == "Create resource: touch /path/to/file"
        assert error.field_path is None

    def test_actionable_error_with_field_path(self):
        """ActionableError should accept optional field_path."""
        error = ActionableError(
            what_failed="Validation failed",
            why_failed="Invalid value",
            how_to_fix="Fix value",
            field_path="config.indexes.vector.chunk_size",
        )

        assert error.field_path == "config.indexes.vector.chunk_size"

    def test_actionable_error_message_format(self):
        """ActionableError message should be well-formatted."""
        error = ActionableError(
            what_failed="Test failed",
            why_failed="Assertion error",
            how_to_fix="Fix test",
        )

        message = str(error)
        assert "ERROR: Test failed" in message
        assert "Reason: Assertion error" in message
        assert "Remediation: Fix test" in message

    def test_actionable_error_message_with_field_path(self):
        """ActionableError message should include field_path when provided."""
        error = ActionableError(
            what_failed="Validation failed",
            why_failed="Invalid value",
            how_to_fix="Fix value",
            field_path="config.field",
        )

        message = str(error)
        assert "Field: config.field" in message

    def test_actionable_error_to_dict(self):
        """ActionableError.to_dict() should return structured dict."""
        error = ActionableError(
            what_failed="Operation failed",
            why_failed="Resource missing",
            how_to_fix="Create resource",
            field_path="path.to.field",
        )

        data = error.to_dict()
        assert data == {
            "what_failed": "Operation failed",
            "why_failed": "Resource missing",
            "how_to_fix": "Create resource",
            "field_path": "path.to.field",
        }

    def test_actionable_error_to_dict_without_field_path(self):
        """ActionableError.to_dict() should include None for field_path when not provided."""
        error = ActionableError(
            what_failed="Operation failed",
            why_failed="Resource missing",
            how_to_fix="Create resource",
        )

        data = error.to_dict()
        assert data["field_path"] is None

    def test_actionable_error_is_exception(self):
        """ActionableError should be a valid Exception."""
        error = ActionableError(
            what_failed="Test",
            why_failed="Test",
            how_to_fix="Test",
        )

        assert isinstance(error, Exception)

    def test_actionable_error_raises(self):
        """ActionableError should be raiseable."""
        with pytest.raises(ActionableError) as exc_info:
            raise ActionableError(
                what_failed="Test failure",
                why_failed="Test reason",
                how_to_fix="Test fix",
            )

        error = exc_info.value
        assert error.what_failed == "Test failure"


class TestConfigValidationError:
    """Test ConfigValidationError subclass."""

    def test_config_validation_error_creation(self):
        """ConfigValidationError should inherit from ActionableError."""
        error = ConfigValidationError(
            what_failed="Invalid chunk_size",
            why_failed="Value below minimum",
            how_to_fix="Set chunk_size >= 100",
            field_path="indexes.vector.chunk_size",
        )

        assert isinstance(error, ActionableError)
        assert error.what_failed == "Invalid chunk_size"
        assert error.field_path == "indexes.vector.chunk_size"

    def test_config_validation_error_message(self):
        """ConfigValidationError message should follow ActionableError format."""
        error = ConfigValidationError(
            what_failed="Config validation failed",
            why_failed="Missing required field",
            how_to_fix="Add field to config.yaml",
            field_path="config.required_field",
        )

        message = str(error)
        assert "ERROR: Config validation failed" in message
        assert "Field: config.required_field" in message

    def test_config_validation_error_raises(self):
        """ConfigValidationError should be raiseable."""
        with pytest.raises(ConfigValidationError) as exc_info:
            raise ConfigValidationError(
                what_failed="Test",
                why_failed="Test",
                how_to_fix="Test",
            )

        assert isinstance(exc_info.value, ActionableError)


class TestEvidenceValidationError:
    """Test EvidenceValidationError subclass."""

    def test_evidence_validation_error_creation(self):
        """EvidenceValidationError should inherit from ActionableError."""
        error = EvidenceValidationError(
            what_failed="Phase gate validation failed",
            why_failed="Missing required evidence field",
            how_to_fix="Provide evidence.tests_passing=True",
            field_path="evidence.tests_passing",
        )

        assert isinstance(error, ActionableError)
        assert error.what_failed == "Phase gate validation failed"

    def test_evidence_validation_error_raises(self):
        """EvidenceValidationError should be raiseable."""
        with pytest.raises(EvidenceValidationError) as exc_info:
            raise EvidenceValidationError(
                what_failed="Gate failed",
                why_failed="Missing evidence",
                how_to_fix="Provide evidence",
            )

        assert isinstance(exc_info.value, ActionableError)


class TestIndexError:
    """Test IndexError subclass."""

    def test_index_error_creation(self):
        """IndexError should inherit from ActionableError."""
        error = IndexError(
            what_failed="Index search failed",
            why_failed="Table not found",
            how_to_fix="Rebuild index: python -m ouroboros rebuild_index",
            field_path="indexes.standards",
        )

        assert isinstance(error, ActionableError)
        assert error.what_failed == "Index search failed"

    def test_index_error_raises(self):
        """IndexError should be raiseable."""
        with pytest.raises(IndexError) as exc_info:
            raise IndexError(
                what_failed="Index failed",
                why_failed="Corruption",
                how_to_fix="Rebuild",
            )

        assert isinstance(exc_info.value, ActionableError)


class TestWorkflowExecutionError:
    """Test WorkflowExecutionError subclass."""

    def test_workflow_execution_error_creation(self):
        """WorkflowExecutionError should inherit from ActionableError."""
        error = WorkflowExecutionError(
            what_failed="Cannot advance phase",
            why_failed="Gate validation failed",
            how_to_fix="Fix evidence and retry",
            field_path="workflow.phase_1.evidence",
        )

        assert isinstance(error, ActionableError)
        assert error.what_failed == "Cannot advance phase"

    def test_workflow_execution_error_raises(self):
        """WorkflowExecutionError should be raiseable."""
        with pytest.raises(WorkflowExecutionError) as exc_info:
            raise WorkflowExecutionError(
                what_failed="Workflow failed",
                why_failed="Invalid state",
                how_to_fix="Reset workflow",
            )

        assert isinstance(exc_info.value, ActionableError)


class TestErrorInteroperability:
    """Test error interoperability and exception handling."""

    def test_catch_actionable_error_as_exception(self):
        """ActionableError should be catchable as Exception."""
        with pytest.raises(Exception):
            raise ActionableError(
                what_failed="Test",
                why_failed="Test",
                how_to_fix="Test",
            )

    def test_catch_subclass_as_actionable_error(self):
        """Subclass errors should be catchable as ActionableError."""
        with pytest.raises(ActionableError):
            raise ConfigValidationError(
                what_failed="Test",
                why_failed="Test",
                how_to_fix="Test",
            )

    def test_error_chaining(self):
        """Errors should support exception chaining."""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise ActionableError(
                    what_failed="Wrapper error",
                    why_failed="Original failed",
                    how_to_fix="Fix original",
                ) from e
        except ActionableError as error:
            assert error.__cause__ is not None
            assert isinstance(error.__cause__, ValueError)


class TestErrorSerialization:
    """Test error serialization for JSON responses."""

    def test_to_dict_json_serializable(self):
        """Error dict should be JSON-serializable."""
        import json

        error = ActionableError(
            what_failed="Test",
            why_failed="Test reason",
            how_to_fix="Test fix",
            field_path="test.field",
        )

        # Should not raise
        json_str = json.dumps(error.to_dict())
        assert "Test" in json_str

    def test_to_dict_structure(self):
        """Error dict should have consistent structure."""
        error = ConfigValidationError(
            what_failed="Validation failed",
            why_failed="Invalid value",
            how_to_fix="Fix value",
            field_path="config.field",
        )

        data = error.to_dict()
        required_keys = {"what_failed", "why_failed", "how_to_fix", "field_path"}
        assert set(data.keys()) == required_keys
