"""
Integration test for evidence validation system.

Tests complete validation flow from WorkflowEngine through CheckpointLoader
and ValidatorExecutor.
"""

from pathlib import Path

import pytest

from mcp_server.config.checkpoint_loader import CheckpointLoader
from mcp_server.rag_engine import RAGEngine
from mcp_server.state_manager import StateManager
from mcp_server.workflow_engine import WorkflowEngine


class TestEvidenceValidationIntegration:
    """Integration tests for complete validation system."""

    @pytest.fixture
    def temp_workflows_path(self, tmp_path):
        """Create temporary workflows directory with test gate."""
        workflows_dir = tmp_path / "workflows"
        workflow_dir = workflows_dir / "test_workflow" / "phases" / "1"
        workflow_dir.mkdir(parents=True)

        # Create test gate-definition.yaml
        gate_file = workflow_dir / "gate-definition.yaml"
        gate_file.write_text(
            """
checkpoint:
  strict: false
  allow_override: true

evidence_schema:
  business_goals:
    type: integer
    required: true
    validator: positive
    description: "Number of business goals"
  
  user_stories:
    type: integer
    required: true
    validator: positive
    description: "Number of user stories"

validators:
  positive: "lambda x: x > 0"
"""
        )

        return workflows_dir

    def test_validation_with_valid_evidence(self, temp_workflows_path):
        """Test validation passes with valid evidence."""
        # Create engine with test workflows path
        engine = WorkflowEngine(
            state_manager=None,  # type: ignore  # Not needed for validation test
            rag_engine=None,  # type: ignore  # Not needed for validation test
            workflows_base_path=temp_workflows_path,
        )

        # Valid evidence
        evidence = {"business_goals": 4, "user_stories": 7}

        # Validate
        passed, result = engine._validate_checkpoint("test_workflow", 1, evidence)

        assert passed is True
        assert result["checkpoint_passed"] is True
        assert len(result["errors"]) == 0
        assert result["diagnostics"]["gate_source"] == "yaml"

    def test_validation_with_missing_field(self, temp_workflows_path):
        """Test validation fails with missing required field."""
        engine = WorkflowEngine(
            state_manager=None,  # type: ignore
            rag_engine=None,  # type: ignore
            workflows_base_path=temp_workflows_path,
        )

        # Missing user_stories
        evidence = {"business_goals": 4}

        passed, result = engine._validate_checkpoint("test_workflow", 1, evidence)

        # Lenient mode (strict: false) - errors become warnings
        assert passed is True  # Lenient mode passes
        assert len(result["warnings"]) > 0
        assert any("user_stories" in w for w in result["warnings"])

    def test_validation_with_invalid_type(self, temp_workflows_path):
        """Test validation fails with wrong field type."""
        engine = WorkflowEngine(
            state_manager=None,  # type: ignore
            rag_engine=None,  # type: ignore
            workflows_base_path=temp_workflows_path,
        )

        # Wrong type (string instead of integer)
        evidence = {"business_goals": "not a number", "user_stories": 7}

        passed, result = engine._validate_checkpoint("test_workflow", 1, evidence)

        # Lenient mode - errors become warnings
        assert passed is True  # Lenient mode
        assert len(result["warnings"]) > 0
        # Check for type error in warnings (should mention "must be integer" or "type")
        assert any(
            "integer" in w.lower() or "type" in w.lower() for w in result["warnings"]
        )

    def test_validation_with_failed_validator(self, temp_workflows_path):
        """Test validation fails when validator fails."""
        engine = WorkflowEngine(
            state_manager=None,  # type: ignore
            rag_engine=None,  # type: ignore
            workflows_base_path=temp_workflows_path,
        )

        # Zero (fails positive validator)
        evidence = {"business_goals": 0, "user_stories": 7}

        passed, result = engine._validate_checkpoint("test_workflow", 1, evidence)

        # Lenient mode - errors become warnings
        assert passed is True  # Lenient mode
        assert len(result["warnings"]) > 0
        assert any("validator" in w.lower() for w in result["warnings"])

    def test_fallback_to_permissive_gate(self, tmp_path):
        """Test fallback to permissive gate when YAML missing."""
        # Empty workflows directory (no gates)
        empty_dir = tmp_path / "empty_workflows"
        empty_dir.mkdir()

        engine = WorkflowEngine(
            state_manager=None,  # type: ignore
            rag_engine=None,  # type: ignore
            workflows_base_path=empty_dir,
        )

        # Any evidence should pass with permissive gate
        evidence = {"anything": "goes"}

        passed, result = engine._validate_checkpoint("nonexistent", 1, evidence)

        assert passed is True
        assert result["checkpoint_passed"] is True
        assert result["diagnostics"]["gate_source"] == "permissive"
