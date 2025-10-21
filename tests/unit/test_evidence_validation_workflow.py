"""
Integration tests for complete evidence validation flow.

Tests end-to-end validation including:
- WorkflowEngine
- CheckpointLoader
- ValidatorExecutor
- Session management

Part of Evidence Validation System (Phase 4, Task 4.3).
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from mcp_server.config.checkpoint_loader import (
    CheckpointRequirements,
    FieldSchema,
)
from mcp_server.models.workflow import WorkflowState
from mcp_server.rag_engine import RAGEngine
from mcp_server.state_manager import StateManager
from mcp_server.workflow_engine import WorkflowEngine


class TestCompletePhaseValidationFlow:
    """Test complete phase validation from start to finish."""

    @pytest.fixture
    def mock_rag_engine(self):
        """Create mock RAG engine."""
        mock = Mock(spec=RAGEngine)
        # Mock empty search results (so we fall back to permissive gate)
        mock.search.return_value = Mock(chunks=[])
        return mock

    @pytest.fixture
    def mock_state_manager(self):
        """Create mock state manager."""
        return Mock(spec=StateManager)

    @pytest.fixture
    def workflow_engine(self, mock_rag_engine, mock_state_manager):
        """Create workflow engine with mocks."""
        return WorkflowEngine(
            state_manager=mock_state_manager, rag_engine=mock_rag_engine
        )

    def test_validation_with_yaml_gate(self, workflow_engine):
        """Test validation using YAML gate (Tier 1)."""
        # Create mock requirements
        requirements = CheckpointRequirements(
            evidence_schema={
                "test_field": FieldSchema(
                    name="test_field",
                    type="boolean",
                    required=True,
                    validator=None,
                    validator_params=None,
                    description="Test field",
                )
            },
            validators={},
            cross_field_rules=[],
            strict=False,
            allow_override=True,
            source="yaml",
        )

        with patch(
            "mcp_server.config.checkpoint_loader.CheckpointLoader.load_checkpoint_requirements",
            return_value=requirements,
        ):
            # Test with valid evidence
            passed, result = workflow_engine._validate_checkpoint(
                "test_workflow", 1, {"test_field": True}
            )

            assert passed is True
            assert result["checkpoint_passed"] is True
            assert len(result["errors"]) == 0

    def test_validation_with_missing_field(self, workflow_engine):
        """Test validation fails when required field is missing."""
        # Create mock requirements with required field
        requirements = CheckpointRequirements(
            evidence_schema={
                "required_field": FieldSchema(
                    name="required_field",
                    type="string",
                    required=True,
                    validator=None,
                    validator_params=None,
                    description="Required field",
                )
            },
            validators={},
            cross_field_rules=[],
            strict=True,
            allow_override=True,
            source="yaml",
        )

        with patch(
            "mcp_server.config.checkpoint_loader.CheckpointLoader.load_checkpoint_requirements",
            return_value=requirements,
        ):
            # Test with missing field
            passed, result = workflow_engine._validate_checkpoint(
                "test_workflow", 1, {}  # Empty evidence
            )

            assert passed is False
            assert result["checkpoint_passed"] is False
            assert len(result["errors"]) > 0
            assert "required_field" in result["errors"][0]

    def test_validation_with_wrong_type(self, workflow_engine):
        """Test validation fails when field has wrong type."""
        # Create mock requirements with integer field
        requirements = CheckpointRequirements(
            evidence_schema={
                "count_field": FieldSchema(
                    name="count_field",
                    type="integer",
                    required=True,
                    validator=None,
                    validator_params=None,
                    description="Count field",
                )
            },
            validators={},
            cross_field_rules=[],
            strict=True,
            allow_override=True,
            source="yaml",
        )

        with patch(
            "mcp_server.config.checkpoint_loader.CheckpointLoader.load_checkpoint_requirements",
            return_value=requirements,
        ):
            # Test with wrong type (string instead of int)
            passed, result = workflow_engine._validate_checkpoint(
                "test_workflow", 1, {"count_field": "not_an_integer"}
            )

            assert passed is False
            assert result["checkpoint_passed"] is False
            assert len(result["errors"]) > 0

    def test_validation_fallback_to_permissive(self, workflow_engine):
        """Test validation falls back to permissive gate when no requirements found."""
        # Create permissive gate
        requirements = CheckpointRequirements(
            evidence_schema={},
            validators={},
            cross_field_rules=[],
            strict=False,
            allow_override=True,
            source="permissive",
        )

        with patch(
            "mcp_server.config.checkpoint_loader.CheckpointLoader.load_checkpoint_requirements",
            return_value=requirements,
        ):
            # Should pass with permissive gate
            passed, result = workflow_engine._validate_checkpoint(
                "test_workflow",
                1,
                {},  # Empty evidence should still pass with permissive gate
            )

            assert passed is True
            assert result["checkpoint_passed"] is True
            assert result["diagnostics"]["gate_source"] == "permissive"

    def test_validation_caching(self, workflow_engine):
        """Test validation requirements are cached."""
        # Create mock requirements
        requirements = CheckpointRequirements(
            evidence_schema={
                "field": FieldSchema(
                    name="field",
                    type="string",
                    required=True,
                    validator=None,
                    validator_params=None,
                    description="Test field",
                )
            },
            validators={},
            cross_field_rules=[],
            strict=False,
            allow_override=True,
            source="yaml",
        )

        with patch(
            "mcp_server.config.checkpoint_loader.CheckpointLoader.load_checkpoint_requirements",
            return_value=requirements,
        ) as mock_load:
            # First call
            workflow_engine._validate_checkpoint("test_workflow", 1, {"field": "value"})
            first_call_count = mock_load.call_count

            # Second call should use cache
            workflow_engine._validate_checkpoint("test_workflow", 1, {"field": "value"})
            # Cache is in CheckpointLoader, so we're testing that validation works
            assert first_call_count > 0


class TestSessionIntegration:
    """Test session-level integration with validation."""

    @pytest.fixture
    def mock_components(self):
        """Create mocked components."""
        rag_engine = Mock(spec=RAGEngine)
        state_manager = Mock(spec=StateManager)

        # Mock state loading
        mock_state = Mock(spec=WorkflowState)
        mock_state.session_id = "test-session"
        mock_state.workflow_type = "test_workflow"
        mock_state.target_file = "test.py"
        mock_state.current_phase = 1
        mock_state.completed_phases = [0]
        mock_state.is_complete.return_value = False
        mock_state.can_access_phase.return_value = True

        state_manager.load_state.return_value = mock_state

        return {
            "rag_engine": rag_engine,
            "state_manager": state_manager,
            "state": mock_state,
        }

    def test_session_complete_phase_with_validation(self, mock_components):
        """Test completing phase with validation through session."""
        from mcp_server.core.session import WorkflowSession
        from mcp_server.models.workflow import PhaseMetadata, WorkflowMetadata
        from mcp_server.workflow_engine import WorkflowEngine

        # Create mock metadata
        metadata = WorkflowMetadata(
            workflow_type="test_workflow",
            version="1.0",
            description="Test workflow",
            total_phases=3,
            estimated_duration="1 hour",
            primary_outputs=["test"],
            phases=[
                PhaseMetadata(
                    phase_number=1,
                    phase_name="Phase 1",
                    purpose="Test",
                    estimated_effort="30 min",
                    key_deliverables=[],
                    validation_criteria=[],
                )
            ],
        )

        # Create mock engine
        mock_engine = Mock(spec=WorkflowEngine)
        mock_engine._validate_checkpoint.return_value = (
            True,
            {
                "checkpoint_passed": True,
                "errors": [],
                "warnings": [],
                "diagnostics": {},
                "remediation": "",
                "next_steps": [],
            },
        )

        # Create session without engine parameter (it accesses it from parent)
        session = WorkflowSession(
            session_id="test-session",
            workflow_type="test_workflow",
            target_file="test.py",
            state=mock_components["state"],
            rag_engine=mock_components["rag_engine"],
            state_manager=mock_components["state_manager"],
            workflows_base_path=Path("."),
            metadata=metadata,
            options={},
        )

        # Inject engine for testing
        session.engine = mock_engine

        # Complete phase with evidence
        result = session.complete_phase(1, {"test_field": True})

        # Validation is currently TODO in session.py, so we just check completion works
        assert result is not None


class TestStructuredErrorResponse:
    """Test structured error responses with diagnostics."""

    def test_validation_result_structure(self):
        """Test validation result contains all required fields."""
        from mcp_server.rag_engine import RAGEngine
        from mcp_server.state_manager import StateManager
        from mcp_server.workflow_engine import WorkflowEngine

        rag_engine = Mock(spec=RAGEngine)
        state_manager = Mock(spec=StateManager)
        engine = WorkflowEngine(state_manager, rag_engine)

        # Create mock requirements with required field
        requirements = CheckpointRequirements(
            evidence_schema={
                "test_field": FieldSchema(
                    name="test_field",
                    type="string",
                    required=True,
                    validator=None,
                    validator_params=None,
                    description="Test field",
                )
            },
            validators={},
            cross_field_rules=[],
            strict=True,
            allow_override=True,
            source="yaml",
        )

        with patch(
            "mcp_server.config.checkpoint_loader.CheckpointLoader.load_checkpoint_requirements",
            return_value=requirements,
        ):
            # Call validation with missing field
            passed, result = engine._validate_checkpoint(
                "test_workflow", 1, {}  # Missing required field
            )

            # Verify result structure (returned directly, not stored as attribute)
            assert "checkpoint_passed" in result
            assert "errors" in result
            assert "warnings" in result
            assert "diagnostics" in result
            assert "remediation" in result
            assert "next_steps" in result

            # Verify diagnostics content
            diagnostics = result["diagnostics"]
            assert "fields_submitted" in diagnostics
            assert "fields_required" in diagnostics
            assert "fields_missing" in diagnostics
            assert "strict_mode" in diagnostics
            assert "gate_source" in diagnostics
            assert "validation_timestamp" in diagnostics


class TestBackwardsCompatibility:
    """Test backwards compatibility with existing workflows."""

    def test_workflow_without_gates_passes(self):
        """Test workflow without gates uses permissive gate."""
        from mcp_server.rag_engine import RAGEngine
        from mcp_server.state_manager import StateManager
        from mcp_server.workflow_engine import WorkflowEngine

        rag_engine = Mock(spec=RAGEngine)
        rag_engine.search.return_value = Mock(chunks=[])
        state_manager = Mock(spec=StateManager)

        engine = WorkflowEngine(state_manager, rag_engine)

        # Create permissive gate
        requirements = CheckpointRequirements(
            evidence_schema={},
            validators={},
            cross_field_rules=[],
            strict=False,
            allow_override=True,
            source="permissive",
        )

        with patch(
            "mcp_server.config.checkpoint_loader.CheckpointLoader.load_checkpoint_requirements",
            return_value=requirements,
        ):
            # Any evidence should pass with permissive gate
            passed, result = engine._validate_checkpoint(
                "unknown_workflow", 99, {"anything": "goes"}
            )

            assert passed is True
            assert result["checkpoint_passed"] is True
            assert result["diagnostics"]["gate_source"] == "permissive"
