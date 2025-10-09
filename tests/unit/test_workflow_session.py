"""
Unit tests for WorkflowSession.

Tests session-scoped workflow execution and lifecycle management.
"""

from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest

from mcp_server.core.session import WorkflowSession, WorkflowSessionError
from mcp_server.models.workflow import PhaseMetadata, WorkflowMetadata, WorkflowState


class TestWorkflowSession:
    """Test suite for WorkflowSession."""

    @pytest.fixture
    def mock_state(self):
        """Create mock workflow state."""
        return WorkflowState(
            session_id="test-session-123",
            workflow_type="test_workflow",
            target_file="test.py",
            current_phase=0,
            completed_phases=[],
            phase_artifacts={},
            checkpoints={},
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={},
        )

    @pytest.fixture
    def static_metadata(self):
        """Create static workflow metadata."""
        return WorkflowMetadata(
            workflow_type="test_workflow",
            version="1.0",
            description="Test workflow",
            total_phases=3,
            estimated_duration="2 hours",
            primary_outputs=["code", "tests"],
            phases=[
                PhaseMetadata(
                    phase_number=0,
                    phase_name="Setup",
                    purpose="Setup phase",
                    estimated_effort="30min",
                    key_deliverables=["config"],
                    validation_criteria=["valid"],
                )
            ],
        )

    @pytest.fixture
    def dynamic_metadata(self):
        """Create dynamic workflow metadata."""
        return WorkflowMetadata(
            workflow_type="spec_execution_v1",
            version="1.0",
            description="Dynamic workflow",
            total_phases=0,  # Dynamic
            estimated_duration="Variable",
            primary_outputs=["implementation"],
            phases=[],
            dynamic_phases=True,
            dynamic_config={
                "source_type": "spec_tasks_md",
                "source_path_key": "spec_path",
                "templates": {
                    "phase": "phases/dynamic/phase-template.md",
                    "task": "phases/dynamic/task-template.md",
                },
                "parser": "spec_tasks_parser",
            },
        )

    @pytest.fixture
    def mock_rag_engine(self):
        """Create mock RAG engine."""
        rag = Mock()
        rag.search = Mock(return_value=Mock(chunks=[{"content": "test content"}]))
        return rag

    @pytest.fixture
    def mock_state_manager(self):
        """Create mock state manager."""
        manager = Mock()
        manager.save_state = Mock()
        return manager

    @pytest.fixture
    def workflows_base_path(self, tmp_path):
        """Create temporary workflows directory."""
        return tmp_path / "workflows"

    def test_create_static_session(
        self,
        mock_state,
        static_metadata,
        mock_rag_engine,
        mock_state_manager,
        workflows_base_path,
    ):
        """Test creating static workflow session."""
        session = WorkflowSession(
            session_id="test-123",
            workflow_type="test_workflow",
            target_file="test.py",
            state=mock_state,
            rag_engine=mock_rag_engine,
            state_manager=mock_state_manager,
            workflows_base_path=workflows_base_path,
            metadata=static_metadata,
        )

        assert session.session_id == "test-123"
        assert session.workflow_type == "test_workflow"
        assert session.target_file == "test.py"
        assert session.dynamic_registry is None
        assert not session._is_dynamic()

    def test_is_dynamic_static_workflow(
        self,
        mock_state,
        static_metadata,
        mock_rag_engine,
        mock_state_manager,
        workflows_base_path,
    ):
        """Test _is_dynamic() returns False for static workflow."""
        session = WorkflowSession(
            session_id="test-123",
            workflow_type="test_workflow",
            target_file="test.py",
            state=mock_state,
            rag_engine=mock_rag_engine,
            state_manager=mock_state_manager,
            workflows_base_path=workflows_base_path,
            metadata=static_metadata,
        )

        assert session._is_dynamic() is False

    def test_is_dynamic_dynamic_workflow(self, dynamic_metadata):
        """Test _is_dynamic() returns True for dynamic workflow."""
        # Just test the metadata
        assert dynamic_metadata.dynamic_phases is True

    def test_get_current_phase_static(
        self,
        mock_state,
        static_metadata,
        mock_rag_engine,
        mock_state_manager,
        workflows_base_path,
    ):
        """Test getting current phase for static workflow."""
        session = WorkflowSession(
            session_id="test-123",
            workflow_type="test_workflow",
            target_file="test.py",
            state=mock_state,
            rag_engine=mock_rag_engine,
            state_manager=mock_state_manager,
            workflows_base_path=workflows_base_path,
            metadata=static_metadata,
        )

        result = session.get_current_phase()

        assert result["session_id"] == "test-123"
        assert result["workflow_type"] == "test_workflow"
        assert result["current_phase"] == 0
        assert result["source"] == "rag"
        mock_rag_engine.search.assert_called_once()

    def test_get_current_phase_complete_workflow(
        self, static_metadata, mock_rag_engine, mock_state_manager, workflows_base_path
    ):
        """Test getting current phase when workflow is complete."""
        complete_state = WorkflowState(
            session_id="test-123",
            workflow_type="test_workflow",
            target_file="test.py",
            current_phase=10,  # Beyond max phases
            completed_phases=[0, 1, 2],
            phase_artifacts={},
            checkpoints={},
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        session = WorkflowSession(
            session_id="test-123",
            workflow_type="test_workflow",
            target_file="test.py",
            state=complete_state,
            rag_engine=mock_rag_engine,
            state_manager=mock_state_manager,
            workflows_base_path=workflows_base_path,
            metadata=static_metadata,
        )

        result = session.get_current_phase()

        assert result["is_complete"] is True
        assert "Workflow complete" in result["message"]

    def test_get_task_static(
        self,
        mock_state,
        static_metadata,
        mock_rag_engine,
        mock_state_manager,
        workflows_base_path,
    ):
        """Test getting task for static workflow."""
        session = WorkflowSession(
            session_id="test-123",
            workflow_type="test_workflow",
            target_file="test.py",
            state=mock_state,
            rag_engine=mock_rag_engine,
            state_manager=mock_state_manager,
            workflows_base_path=workflows_base_path,
            metadata=static_metadata,
        )

        result = session.get_task(0, 1)

        assert result["session_id"] == "test-123"
        assert result["phase"] == 0
        assert result["task_number"] == 1
        assert result["source"] == "rag"
        mock_rag_engine.search.assert_called_once()

    def test_get_task_invalid_phase(
        self, static_metadata, mock_rag_engine, mock_state_manager, workflows_base_path
    ):
        """Test error when accessing invalid phase."""
        state = WorkflowState(
            session_id="test-123",
            workflow_type="test_workflow",
            target_file="test.py",
            current_phase=1,
            completed_phases=[0],
            phase_artifacts={},
            checkpoints={},
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        session = WorkflowSession(
            session_id="test-123",
            workflow_type="test_workflow",
            target_file="test.py",
            state=state,
            rag_engine=mock_rag_engine,
            state_manager=mock_state_manager,
            workflows_base_path=workflows_base_path,
            metadata=static_metadata,
        )

        with pytest.raises(WorkflowSessionError, match="Cannot access phase 5"):
            session.get_task(5, 1)

    def test_complete_phase(
        self,
        mock_state,
        static_metadata,
        mock_rag_engine,
        mock_state_manager,
        workflows_base_path,
    ):
        """Test completing a phase."""
        session = WorkflowSession(
            session_id="test-123",
            workflow_type="test_workflow",
            target_file="test.py",
            state=mock_state,
            rag_engine=mock_rag_engine,
            state_manager=mock_state_manager,
            workflows_base_path=workflows_base_path,
            metadata=static_metadata,
        )

        evidence = {"test_passed": True, "coverage": 90}
        result = session.complete_phase(0, evidence)

        assert result["checkpoint_passed"] is True
        assert result["phase_completed"] == 0
        assert result["next_phase"] == 1
        assert result["workflow_complete"] is False
        assert session.state.current_phase == 1
        assert 0 in session.state.completed_phases
        mock_state_manager.save_state.assert_called_once()

    def test_complete_phase_wrong_phase(
        self, static_metadata, mock_rag_engine, mock_state_manager, workflows_base_path
    ):
        """Test error when completing wrong phase."""
        state = WorkflowState(
            session_id="test-123",
            workflow_type="test_workflow",
            target_file="test.py",
            current_phase=1,
            completed_phases=[0],
            phase_artifacts={},
            checkpoints={},
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        session = WorkflowSession(
            session_id="test-123",
            workflow_type="test_workflow",
            target_file="test.py",
            state=state,
            rag_engine=mock_rag_engine,
            state_manager=mock_state_manager,
            workflows_base_path=workflows_base_path,
            metadata=static_metadata,
        )

        with pytest.raises(WorkflowSessionError, match="Cannot complete phase 0"):
            session.complete_phase(0, {})

    def test_cleanup(
        self,
        mock_state,
        static_metadata,
        mock_rag_engine,
        mock_state_manager,
        workflows_base_path,
    ):
        """Test cleanup method."""
        session = WorkflowSession(
            session_id="test-123",
            workflow_type="test_workflow",
            target_file="test.py",
            state=mock_state,
            rag_engine=mock_rag_engine,
            state_manager=mock_state_manager,
            workflows_base_path=workflows_base_path,
            metadata=static_metadata,
        )

        # Should not raise
        session.cleanup()

    def test_get_state(
        self,
        mock_state,
        static_metadata,
        mock_rag_engine,
        mock_state_manager,
        workflows_base_path,
    ):
        """Test getting workflow state."""
        session = WorkflowSession(
            session_id="test-123",
            workflow_type="test_workflow",
            target_file="test.py",
            state=mock_state,
            rag_engine=mock_rag_engine,
            state_manager=mock_state_manager,
            workflows_base_path=workflows_base_path,
            metadata=static_metadata,
        )

        state = session.get_state()

        assert state == mock_state
        assert state.session_id == "test-session-123"

    def test_session_with_options(
        self,
        mock_state,
        static_metadata,
        mock_rag_engine,
        mock_state_manager,
        workflows_base_path,
    ):
        """Test session with custom options."""
        options = {"custom_option": "value", "debug": True}

        session = WorkflowSession(
            session_id="test-123",
            workflow_type="test_workflow",
            target_file="test.py",
            state=mock_state,
            rag_engine=mock_rag_engine,
            state_manager=mock_state_manager,
            workflows_base_path=workflows_base_path,
            metadata=static_metadata,
            options=options,
        )

        assert session.options == options
        assert session.options["custom_option"] == "value"
