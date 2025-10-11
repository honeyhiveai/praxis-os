"""
Unit tests for WorkflowEngine session-scoped refactor.

Tests session factory pattern, session caching, delegation to WorkflowSession,
and cleanup on workflow completion.
"""

from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock, call, patch

import pytest

from mcp_server.core.session import WorkflowSession
from mcp_server.models import (
    CheckpointStatus,
    PhaseMetadata,
    WorkflowMetadata,
    WorkflowState,
)
from mcp_server.rag_engine import RAGEngine
from mcp_server.state_manager import StateManager
from mcp_server.workflow_engine import WorkflowEngine


@pytest.fixture
def mock_state_manager():
    """Mock StateManager."""
    mock = Mock(spec=StateManager)
    return mock


@pytest.fixture
def mock_rag_engine():
    """Mock RAGEngine."""
    mock = Mock(spec=RAGEngine)
    return mock


@pytest.fixture
def mock_workflows_path(tmp_path):
    """Create temporary workflows directory with metadata."""
    workflows_dir = tmp_path / "workflows"
    workflows_dir.mkdir()

    # Create spec_execution_v1 workflow directory with metadata
    spec_exec_dir = workflows_dir / "spec_execution_v1"
    spec_exec_dir.mkdir()

    metadata = {
        "workflow_type": "spec_execution_v1",
        "version": "1.0.0",
        "description": "Test workflow",
        "total_phases": 4,
        "estimated_duration": "2 hours",
        "primary_outputs": ["test output"],
        "phases": [
            {
                "phase_number": i,
                "phase_name": f"Phase {i}",
                "purpose": f"Test phase {i}",
                "estimated_effort": "30 min",
                "key_deliverables": [],
                "validation_criteria": [],
            }
            for i in range(4)
        ],
        "dynamic_phases": False,
    }

    import json

    metadata_file = spec_exec_dir / "metadata.json"
    metadata_file.write_text(json.dumps(metadata, indent=2))

    return workflows_dir


@pytest.fixture
def engine(mock_state_manager, mock_rag_engine, mock_workflows_path):
    """Create WorkflowEngine instance."""
    return WorkflowEngine(
        state_manager=mock_state_manager,
        rag_engine=mock_rag_engine,
        workflows_base_path=mock_workflows_path,
    )


@pytest.fixture
def sample_state():
    """Create sample WorkflowState."""
    return WorkflowState(
        session_id="test-session-123",
        workflow_type="spec_execution_v1",
        target_file="test.py",
        current_phase=0,
        completed_phases=[],
        phase_artifacts={},
        checkpoints={},
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


class TestWorkflowEngineSessionFactory:
    """Test session factory pattern and caching."""

    def test_get_session_creates_new_session(
        self, engine, mock_state_manager, sample_state
    ):
        """Test get_session creates new WorkflowSession."""
        # Setup
        mock_state_manager.load_state.return_value = sample_state

        # Execute
        session = engine.get_session("test-session-123")

        # Verify
        assert isinstance(session, WorkflowSession)
        assert session.session_id == "test-session-123"
        assert session.workflow_type == "spec_execution_v1"
        mock_state_manager.load_state.assert_called_once_with("test-session-123")

    def test_get_session_caches_session(self, engine, mock_state_manager, sample_state):
        """Test get_session caches WorkflowSession instances."""
        # Setup
        mock_state_manager.load_state.return_value = sample_state

        # Execute - call twice
        session1 = engine.get_session("test-session-123")
        session2 = engine.get_session("test-session-123")

        # Verify - same instance returned, state only loaded once
        assert session1 is session2
        mock_state_manager.load_state.assert_called_once_with("test-session-123")

    def test_get_session_raises_on_not_found(self, engine, mock_state_manager):
        """Test get_session raises ValueError if session not found."""
        # Setup
        mock_state_manager.load_state.return_value = None

        # Execute & Verify
        with pytest.raises(ValueError, match="Session not-found not found"):
            engine.get_session("not-found")

    def test_get_session_loads_metadata(self, engine, mock_state_manager, sample_state):
        """Test get_session loads workflow metadata."""
        # Setup
        mock_state_manager.load_state.return_value = sample_state

        # Execute
        session = engine.get_session("test-session-123")

        # Verify - metadata was loaded and cached
        assert "spec_execution_v1" in engine._metadata_cache
        assert session.metadata.workflow_type == "spec_execution_v1"


class TestStartWorkflowRefactor:
    """Test start_workflow session creation."""

    def test_start_workflow_creates_session_immediately(
        self, engine, mock_state_manager, sample_state
    ):
        """Test start_workflow creates WorkflowSession immediately."""
        # Setup
        mock_state_manager.get_active_session.return_value = None
        mock_state_manager.create_session.return_value = sample_state

        # Execute
        with patch.object(WorkflowSession, "get_current_phase") as mock_get_phase:
            mock_get_phase.return_value = {
                "phase_number": 0,
                "content": "test content",
            }
            result = engine.start_workflow("spec_execution_v1", "test.py")

        # Verify - session created and cached
        assert "test-session-123" in engine._sessions
        session = engine._sessions["test-session-123"]
        assert isinstance(session, WorkflowSession)
        assert session.session_id == "test-session-123"

    def test_start_workflow_resumes_existing_session(
        self, engine, mock_state_manager, sample_state
    ):
        """Test start_workflow resumes existing session."""
        # Setup
        mock_state_manager.get_active_session.return_value = sample_state
        mock_state_manager.load_state.return_value = sample_state

        # Execute
        with patch.object(WorkflowSession, "get_current_phase") as mock_get_phase:
            mock_get_phase.return_value = {
                "phase_number": 0,
                "content": "test content",
            }
            result = engine.start_workflow("spec_execution_v1", "test.py")

        # Verify - existing session reused
        assert "test-session-123" in engine._sessions
        assert not mock_state_manager.create_session.called

    def test_start_workflow_includes_workflow_overview(
        self, engine, mock_state_manager, sample_state
    ):
        """Test start_workflow includes workflow overview in response."""
        # Setup
        mock_state_manager.get_active_session.return_value = None
        mock_state_manager.create_session.return_value = sample_state

        # Execute
        with patch.object(WorkflowSession, "get_current_phase") as mock_get_phase:
            mock_get_phase.return_value = {
                "phase_number": 0,
                "content": "test content",
            }
            result = engine.start_workflow("spec_execution_v1", "test.py")

        # Verify
        assert "workflow_overview" in result
        assert result["workflow_overview"]["workflow_type"] == "spec_execution_v1"
        assert result["workflow_overview"]["total_phases"] == 4


class TestDelegationToSession:
    """Test delegation to WorkflowSession methods."""

    def test_get_current_phase_delegates(
        self, engine, mock_state_manager, sample_state
    ):
        """Test get_current_phase delegates to session."""
        # Setup
        mock_state_manager.load_state.return_value = sample_state

        # Execute
        with patch.object(WorkflowSession, "get_current_phase") as mock_method:
            mock_method.return_value = {"phase": 0, "content": "test"}
            result = engine.get_current_phase("test-session-123")

        # Verify
        mock_method.assert_called_once()
        # Check that core fields are present (may have additional workflow metadata)
        assert result["phase"] == 0
        assert result["content"] == "test"

    def test_get_task_delegates(self, engine, mock_state_manager, sample_state):
        """Test get_task delegates to session."""
        # Setup
        mock_state_manager.load_state.return_value = sample_state

        # Execute
        with patch.object(WorkflowSession, "get_task") as mock_method:
            mock_method.return_value = {"task": "test task"}
            result = engine.get_task("test-session-123", 0, 1)

        # Verify
        mock_method.assert_called_once_with(0, 1)
        # Check that core field is present (may have additional workflow metadata)
        assert result["task"] == "test task"

    def test_complete_phase_delegates(self, engine, mock_state_manager, sample_state):
        """Test complete_phase delegates to session."""
        # Setup
        mock_state_manager.load_state.return_value = sample_state
        evidence = {"test": "evidence"}

        # Execute
        with patch.object(WorkflowSession, "complete_phase") as mock_method:
            mock_method.return_value = {
                "checkpoint_passed": True,
                "next_phase": 1,
            }
            result = engine.complete_phase("test-session-123", 0, evidence)

        # Verify
        mock_method.assert_called_once_with(0, evidence)
        assert result["checkpoint_passed"] is True


class TestSessionCleanup:
    """Test session cleanup on workflow completion."""

    def test_complete_phase_cleans_up_on_completion(
        self, engine, mock_state_manager, sample_state
    ):
        """Test complete_phase cleans up session when workflow completes."""
        # Setup
        sample_state.current_phase = 3  # Last phase
        mock_state_manager.load_state.return_value = sample_state
        evidence = {"final": "evidence"}

        # Execute
        with patch.object(WorkflowSession, "complete_phase") as mock_complete:
            with patch.object(WorkflowSession, "cleanup") as mock_cleanup:
                mock_complete.return_value = {
                    "checkpoint_passed": True,
                    "workflow_complete": True,
                }
                result = engine.complete_phase("test-session-123", 3, evidence)

        # Verify - cleanup was called
        mock_cleanup.assert_called_once()

        # Verify - session removed from cache
        assert "test-session-123" not in engine._sessions

    def test_complete_phase_keeps_session_on_incomplete(
        self, engine, mock_state_manager, sample_state
    ):
        """Test complete_phase keeps session when workflow not complete."""
        # Setup
        mock_state_manager.load_state.return_value = sample_state
        evidence = {"test": "evidence"}

        # Execute
        with patch.object(WorkflowSession, "complete_phase") as mock_complete:
            with patch.object(WorkflowSession, "cleanup") as mock_cleanup:
                mock_complete.return_value = {
                    "checkpoint_passed": True,
                    "workflow_complete": False,
                    "next_phase": 1,
                }
                result = engine.complete_phase("test-session-123", 0, evidence)

        # Verify - cleanup not called
        mock_cleanup.assert_not_called()

        # Verify - session still in cache
        assert "test-session-123" in engine._sessions


class TestDynamicWorkflowIntegration:
    """Test dynamic workflow integration through sessions."""

    def test_dynamic_workflow_creates_registry(
        self, engine, mock_state_manager, mock_workflows_path, tmp_path
    ):
        """Test dynamic workflow initializes DynamicContentRegistry."""
        # Setup - create dynamic workflow metadata
        dynamic_workflow_dir = mock_workflows_path / "dynamic_test"
        dynamic_workflow_dir.mkdir()

        # Create spec tasks.md
        spec_dir = tmp_path / "spec"
        spec_dir.mkdir()
        tasks_file = spec_dir / "tasks.md"
        tasks_file.write_text(
            """# Test Spec Tasks

### Phase 1: Test Phase

**Goal:** Test dynamic content

**Estimated Duration:** 1 hour

#### Tasks

##### Task 1.1: Test Task
- **Description:** Test task description
- **Estimated Time:** 30 minutes
- **Dependencies:** None
- **Acceptance Criteria:**
  - [ ] Criterion 1

#### Validation Gate
- [ ] Gate 1
"""
        )

        metadata = {
            "workflow_type": "dynamic_test",
            "version": "1.0.0",
            "description": "Dynamic test workflow",
            "total_phases": 2,
            "estimated_duration": "2 hours",
            "primary_outputs": ["test output"],
            "phases": [
                {
                    "phase_number": i,
                    "phase_name": f"Phase {i}",
                    "purpose": f"Test phase {i}",
                    "estimated_effort": "30 min",
                    "key_deliverables": [],
                    "validation_criteria": [],
                }
                for i in range(2)
            ],
            "dynamic_phases": True,
            "dynamic_config": {
                "source_type": "spec_tasks_md",
                "source_path_key": "spec_path",
                "templates": {
                    "phase": "phases/dynamic/phase-template.md",
                    "task": "phases/dynamic/task-template.md",
                },
                "parser": "spec_tasks_parser",
            },
        }

        import json

        metadata_file = dynamic_workflow_dir / "metadata.json"
        metadata_file.write_text(json.dumps(metadata, indent=2))

        # Create templates
        phases_dir = dynamic_workflow_dir / "phases" / "dynamic"
        phases_dir.mkdir(parents=True)
        (phases_dir / "phase-template.md").write_text("Phase [PHASE_NUMBER] template")
        (phases_dir / "task-template.md").write_text("Task [TASK_ID] template")

        # Create state with spec_path
        state = WorkflowState(
            session_id="dynamic-session",
            workflow_type="dynamic_test",
            target_file="test.py",
            current_phase=0,
            completed_phases=[],
            phase_artifacts={},
            checkpoints={},
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={"spec_path": str(tasks_file.parent)},
        )

        mock_state_manager.load_state.return_value = state

        # Execute
        session = engine.get_session("dynamic-session")

        # Verify - session is dynamic
        assert session._is_dynamic()
        assert session.dynamic_registry is not None


class TestBackwardCompatibility:
    """Test backward compatibility with existing workflows."""

    def test_static_workflows_still_work(
        self, engine, mock_state_manager, sample_state
    ):
        """Test static (non-dynamic) workflows continue to work."""
        # Setup
        mock_state_manager.load_state.return_value = sample_state

        # Execute
        session = engine.get_session("test-session-123")

        # Verify - session created successfully
        assert isinstance(session, WorkflowSession)
        assert not session._is_dynamic()
        assert session.dynamic_registry is None

    def test_existing_methods_still_callable(
        self, engine, mock_state_manager, sample_state
    ):
        """Test all existing public methods still work."""
        # Setup
        mock_state_manager.load_state.return_value = sample_state

        # Verify all methods are still accessible
        assert hasattr(engine, "start_workflow")
        assert hasattr(engine, "get_current_phase")
        assert hasattr(engine, "get_task")
        assert hasattr(engine, "complete_phase")
        assert hasattr(engine, "get_workflow_state")
        assert hasattr(engine, "get_phase_content")
        assert hasattr(engine, "load_workflow_metadata")


class TestMetadataLoading:
    """Test workflow metadata loading and caching."""

    def test_load_workflow_metadata_from_file(self, engine, mock_workflows_path):
        """Test loading metadata from metadata.json."""
        # Execute
        metadata = engine.load_workflow_metadata("spec_execution_v1")

        # Verify
        assert metadata.workflow_type == "spec_execution_v1"
        assert metadata.version == "1.0.0"
        assert metadata.total_phases == 4
        assert len(metadata.phases) == 4

    def test_metadata_caching(self, engine, mock_workflows_path):
        """Test metadata is cached after first load."""
        # Execute - load twice
        metadata1 = engine.load_workflow_metadata("spec_execution_v1")
        metadata2 = engine.load_workflow_metadata("spec_execution_v1")

        # Verify - same instance from cache
        assert metadata1 is metadata2
        assert "spec_execution_v1" in engine._metadata_cache
