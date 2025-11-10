"""
Unit tests for WorkflowEngine._get_task_count_for_phase() helper method.

Tests task count retrieval routing for both static and dynamic workflows,
including graceful degradation on errors.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from ouroboros.subsystems.workflow.engine import WorkflowEngine
from ouroboros.subsystems.workflow.models import WorkflowState, WorkflowMetadata
from ouroboros.subsystems.workflow.workflow_renderer import RendererError
from ouroboros.subsystems.workflow.dynamic_registry import DynamicRegistryError
from ouroboros.config.schemas.workflow import WorkflowConfig


class TestGetTaskCountForPhase:
    """Test _get_task_count_for_phase() routing logic."""

    @pytest.fixture
    def mock_engine(self, tmp_path):
        """Create WorkflowEngine with mocked components."""
        # Create minimal workflow directory structure
        workflows_dir = tmp_path / "workflows"
        workflows_dir.mkdir()
        
        config = WorkflowConfig(workflows_dir="workflows")
        
        # Mock session mapper
        mock_session_mapper = Mock()
        
        with patch('ouroboros.subsystems.workflow.engine.WorkflowRenderer'), \
             patch('ouroboros.subsystems.workflow.engine.HiddenSchemas'), \
             patch('ouroboros.subsystems.workflow.engine.SessionStateHelper'):
            
            engine = WorkflowEngine(
                config=config,
                base_path=tmp_path,
                session_mapper=mock_session_mapper
            )
            
            return engine

    @pytest.fixture
    def static_workflow_state(self):
        """Create workflow state for static workflow."""
        return WorkflowState(
            session_id="test-static-123",
            workflow_type="spec_creation_v1",
            target_file="test_spec",
            current_phase=1,
            metadata={}
        )

    @pytest.fixture
    def dynamic_workflow_state(self):
        """Create workflow state for dynamic workflow."""
        return WorkflowState(
            session_id="test-dynamic-456",
            workflow_type="spec_execution_v1",
            target_file="test_dynamic_spec",
            current_phase=1,
            metadata={"spec_path": "/path/to/spec"}
        )

    def test_static_workflow_routes_to_renderer(self, mock_engine, static_workflow_state):
        """Test that static workflows route to WorkflowRenderer.get_task_count()."""
        # Arrange
        phase = 1
        expected_count = 5
        
        # Mock _is_dynamic to return False (static workflow)
        mock_engine._is_dynamic = Mock(return_value=False)
        
        # Mock renderer.get_task_count
        mock_engine._renderer.get_task_count = Mock(return_value=expected_count)
        
        # Act
        count = mock_engine._get_task_count_for_phase(static_workflow_state, phase)
        
        # Assert
        assert count == expected_count
        mock_engine._is_dynamic.assert_called_once_with(static_workflow_state)
        mock_engine._renderer.get_task_count.assert_called_once_with("spec_creation_v1", phase)

    def test_dynamic_workflow_routes_to_registry(self, mock_engine, dynamic_workflow_state):
        """Test that dynamic workflows route to DynamicContentRegistry.get_phase_metadata()."""
        # Arrange
        phase = 2
        expected_count = 3
        
        # Mock _is_dynamic to return True (dynamic workflow)
        mock_engine._is_dynamic = Mock(return_value=True)
        
        # Mock _get_or_create_dynamic_registry
        mock_registry = Mock()
        mock_registry.get_phase_metadata.return_value = {"task_count": expected_count}
        mock_engine._get_or_create_dynamic_registry = Mock(return_value=mock_registry)
        
        # Act
        count = mock_engine._get_task_count_for_phase(dynamic_workflow_state, phase)
        
        # Assert
        assert count == expected_count
        mock_engine._is_dynamic.assert_called_once_with(dynamic_workflow_state)
        mock_engine._get_or_create_dynamic_registry.assert_called_once_with(
            dynamic_workflow_state.session_id, dynamic_workflow_state
        )
        mock_registry.get_phase_metadata.assert_called_once_with(phase)

    def test_graceful_degradation_on_renderer_error(self, mock_engine, static_workflow_state):
        """Test that RendererError returns None (graceful degradation)."""
        # Arrange
        phase = 1
        
        # Mock _is_dynamic to return False
        mock_engine._is_dynamic = Mock(return_value=False)
        
        # Mock renderer to raise RendererError
        mock_engine._renderer.get_task_count = Mock(
            side_effect=RendererError(
                what_failed="Task count retrieval",
                why_failed="Phase directory not found",
                how_to_fix="mkdir -p /path/to/phase"
            )
        )
        
        # Act
        count = mock_engine._get_task_count_for_phase(static_workflow_state, phase)
        
        # Assert - should return None, not raise exception
        assert count is None

    def test_graceful_degradation_on_registry_error(self, mock_engine, dynamic_workflow_state):
        """Test that DynamicRegistryError returns None (graceful degradation)."""
        # Arrange
        phase = 1
        
        # Mock _is_dynamic to return True
        mock_engine._is_dynamic = Mock(return_value=True)
        
        # Mock registry creation to raise DynamicRegistryError
        mock_engine._get_or_create_dynamic_registry = Mock(
            side_effect=DynamicRegistryError("Failed to parse tasks.md")
        )
        
        # Act
        count = mock_engine._get_task_count_for_phase(dynamic_workflow_state, phase)
        
        # Assert - should return None, not raise exception
        assert count is None

    def test_graceful_degradation_on_unexpected_exception(self, mock_engine, static_workflow_state):
        """Test that any unexpected exception returns None (fail-safe)."""
        # Arrange
        phase = 1
        
        # Mock _is_dynamic to raise unexpected exception
        mock_engine._is_dynamic = Mock(side_effect=RuntimeError("Unexpected error"))
        
        # Act
        count = mock_engine._get_task_count_for_phase(static_workflow_state, phase)
        
        # Assert - should return None, not raise exception
        assert count is None

    def test_returns_none_when_task_count_missing_in_metadata(self, mock_engine, dynamic_workflow_state):
        """Test that missing task_count in phase metadata returns None."""
        # Arrange
        phase = 1
        
        # Mock _is_dynamic to return True
        mock_engine._is_dynamic = Mock(return_value=True)
        
        # Mock registry with missing task_count
        mock_registry = Mock()
        mock_registry.get_phase_metadata.return_value = {}  # No task_count key
        mock_engine._get_or_create_dynamic_registry = Mock(return_value=mock_registry)
        
        # Act
        count = mock_engine._get_task_count_for_phase(dynamic_workflow_state, phase)
        
        # Assert - dict.get() returns None for missing key
        assert count is None

    def test_returns_integer_for_valid_static_workflow(self, mock_engine, static_workflow_state):
        """Test that method returns integer type for static workflows."""
        # Arrange
        phase = 0
        
        # Mock _is_dynamic to return False
        mock_engine._is_dynamic = Mock(return_value=False)
        
        # Mock renderer with integer count
        mock_engine._renderer.get_task_count = Mock(return_value=8)
        
        # Act
        count = mock_engine._get_task_count_for_phase(static_workflow_state, phase)
        
        # Assert
        assert isinstance(count, int)
        assert count == 8

    def test_returns_integer_for_valid_dynamic_workflow(self, mock_engine, dynamic_workflow_state):
        """Test that method returns integer type for dynamic workflows."""
        # Arrange
        phase = 1
        
        # Mock _is_dynamic to return True
        mock_engine._is_dynamic = Mock(return_value=True)
        
        # Mock registry with integer task_count
        mock_registry = Mock()
        mock_registry.get_phase_metadata.return_value = {"task_count": 4}
        mock_engine._get_or_create_dynamic_registry = Mock(return_value=mock_registry)
        
        # Act
        count = mock_engine._get_task_count_for_phase(dynamic_workflow_state, phase)
        
        # Assert
        assert isinstance(count, int)
        assert count == 4


class TestTaskCountLogging:
    """Test logging behavior for task count retrieval."""

    @pytest.fixture
    def mock_engine(self, tmp_path):
        """Create WorkflowEngine with mocked components."""
        workflows_dir = tmp_path / "workflows"
        workflows_dir.mkdir()
        
        config = WorkflowConfig(workflows_dir="workflows")
        mock_session_mapper = Mock()
        
        with patch('ouroboros.subsystems.workflow.engine.WorkflowRenderer'), \
             patch('ouroboros.subsystems.workflow.engine.HiddenSchemas'), \
             patch('ouroboros.subsystems.workflow.engine.SessionStateHelper'):
            
            engine = WorkflowEngine(
                config=config,
                base_path=tmp_path,
                session_mapper=mock_session_mapper
            )
            
            return engine

    @pytest.fixture
    def static_workflow_state(self):
        """Create workflow state for static workflow."""
        return WorkflowState(
            session_id="test-logging-123",
            workflow_type="spec_creation_v1",
            target_file="test_spec_logging",
            current_phase=1,
            metadata={}
        )

    def test_error_logged_on_exception(self, mock_engine, static_workflow_state, caplog):
        """Test that errors are logged at ERROR level when task count fails."""
        import logging
        caplog.set_level(logging.ERROR)
        
        # Arrange
        phase = 1
        
        # Mock to raise exception
        mock_engine._is_dynamic = Mock(side_effect=RuntimeError("Test error"))
        
        # Act
        count = mock_engine._get_task_count_for_phase(static_workflow_state, phase)
        
        # Assert
        assert count is None
        assert "Failed to retrieve task count" in caplog.text
        assert "breadcrumb navigation disabled" in caplog.text

