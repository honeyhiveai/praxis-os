"""Tests for StateManager."""

import json
import time
from pathlib import Path

import pytest
from ouroboros.foundation.state_manager import StateManager, StateManagerError
from ouroboros.subsystems.workflow.models import CheckpointStatus, WorkflowState


class TestStateManager:
    """Tests for StateManager."""

    @pytest.fixture
    def temp_state_dir(self, tmp_path):
        """Create temporary state directory."""
        state_dir = tmp_path / "workflow_states"
        return state_dir

    @pytest.fixture
    def state_manager(self, temp_state_dir):
        """Create state manager with temp directory."""
        return StateManager(temp_state_dir, cleanup_days=7)

    @pytest.fixture
    def sample_state(self):
        """Create sample workflow state."""
        return WorkflowState(
            session_id="test-session-123",
            workflow_type="test_workflow",
            target_file="/path/to/file.py",
            current_phase=0,
            completed_phases=[],
        )

    def test_state_manager_init_creates_directory(self, temp_state_dir):
        """Test that state manager creates state directory."""
        assert not temp_state_dir.exists()

        manager = StateManager(temp_state_dir)

        assert temp_state_dir.exists()
        assert temp_state_dir.is_dir()

    def test_save_state(self, state_manager, sample_state):
        """Test saving workflow state."""
        state_manager.save_state(sample_state)

        state_file = state_manager._get_state_file(sample_state.session_id)
        assert state_file.exists()

        # Verify JSON content
        with open(state_file, "r") as f:
            data = json.load(f)

        assert data["session_id"] == "test-session-123"
        assert data["workflow_type"] == "test_workflow"
        assert data["current_phase"] == 0

    def test_load_state(self, state_manager, sample_state):
        """Test loading workflow state."""
        # Save state first
        state_manager.save_state(sample_state)

        # Load state
        loaded_state = state_manager.load_state(sample_state.session_id)

        assert loaded_state is not None
        assert loaded_state.session_id == sample_state.session_id
        assert loaded_state.workflow_type == sample_state.workflow_type
        assert loaded_state.current_phase == sample_state.current_phase

    def test_load_nonexistent_state_returns_none(self, state_manager):
        """Test loading nonexistent state returns None."""
        loaded_state = state_manager.load_state("nonexistent-session")

        assert loaded_state is None

    def test_load_corrupted_state_raises_error(self, state_manager, temp_state_dir):
        """Test loading corrupted state file raises error."""
        # Create corrupted JSON file
        state_file = temp_state_dir / "corrupted-session.json"
        temp_state_dir.mkdir(parents=True, exist_ok=True)
        state_file.write_text("{ invalid json }}")

        with pytest.raises(StateManagerError, match="invalid JSON"):
            state_manager.load_state("corrupted-session")

    def test_create_session(self, state_manager):
        """Test creating a new session."""
        state = state_manager.create_session(
            workflow_type="test_workflow",
            target_file="/path/to/file.py",
            metadata={"key": "value"},
        )

        assert state.workflow_type == "test_workflow"
        assert state.target_file == "/path/to/file.py"
        assert state.current_phase == 0
        assert state.metadata == {"key": "value"}

        # Verify state was persisted
        loaded_state = state_manager.load_state(state.session_id)
        assert loaded_state is not None
        assert loaded_state.session_id == state.session_id

    def test_create_session_with_custom_id(self, state_manager):
        """Test creating session with custom ID."""
        state = state_manager.create_session(
            workflow_type="test_workflow",
            target_file="/path/to/file.py",
            session_id="custom-id-123",
        )

        assert state.session_id == "custom-id-123"

    def test_create_session_rejects_duplicate_id(self, state_manager, sample_state):
        """Test that creating session with existing ID fails."""
        # Create first session
        state_manager.save_state(sample_state)

        # Try to create duplicate
        with pytest.raises(StateManagerError, match="already exists"):
            state_manager.create_session(
                workflow_type="test_workflow",
                target_file="/path/to/file.py",
                session_id=sample_state.session_id,
            )

    def test_list_sessions(self, state_manager):
        """Test listing all sessions."""
        # Create multiple sessions
        state1 = state_manager.create_session("workflow1", "/file1.py")
        state2 = state_manager.create_session("workflow2", "/file2.py")

        # List sessions
        sessions = state_manager.list_sessions()

        assert len(sessions) == 2
        session_ids = {s["session_id"] for s in sessions}
        assert state1.session_id in session_ids
        assert state2.session_id in session_ids

    def test_list_sessions_filter_active(self, state_manager):
        """Test listing only active sessions."""
        # Create active session (current_phase = 0)
        active_state = state_manager.create_session("workflow1", "/file1.py")

        # Create completed session (current_phase > max completed)
        completed_state = state_manager.create_session("workflow2", "/file2.py")
        completed_state = completed_state.with_phase_completed(
            0, {"done": True}, CheckpointStatus.PASSED
        )
        state_manager.save_state(completed_state)

        # List only active
        active_sessions = state_manager.list_sessions(status="active")

        assert len(active_sessions) == 1
        assert active_sessions[0]["session_id"] == active_state.session_id

    def test_list_sessions_filter_completed(self, state_manager):
        """Test listing only completed sessions."""
        # Create active session
        state_manager.create_session("workflow1", "/file1.py")

        # Create completed session
        completed_state = state_manager.create_session("workflow2", "/file2.py")
        completed_state = completed_state.with_phase_completed(
            0, {"done": True}, CheckpointStatus.PASSED
        )
        state_manager.save_state(completed_state)

        # List only completed
        completed_sessions = state_manager.list_sessions(status="completed")

        assert len(completed_sessions) == 1
        assert completed_sessions[0]["session_id"] == completed_state.session_id
        assert completed_sessions[0]["is_complete"] is True

    def test_delete_session(self, state_manager, sample_state):
        """Test deleting a session."""
        # Create session
        state_manager.save_state(sample_state)
        assert state_manager.load_state(sample_state.session_id) is not None

        # Delete session
        result = state_manager.delete_session(sample_state.session_id)

        assert result is True
        assert state_manager.load_state(sample_state.session_id) is None

    def test_delete_nonexistent_session_returns_false(self, state_manager):
        """Test deleting nonexistent session returns False."""
        result = state_manager.delete_session("nonexistent-session")

        assert result is False

    def test_cleanup_completed(self, state_manager):
        """Test cleanup of old completed sessions."""
        import json
        from datetime import datetime, timedelta

        # Create old completed session
        old_state = state_manager.create_session("workflow1", "/file1.py")
        # Complete phase 0, which advances current_phase to 1
        old_state = old_state.with_phase_completed(
            0, {"done": True}, CheckpointStatus.PASSED
        )

        # Manually backdate the updated_at timestamp and write directly to file
        # (can't use save_state as it overwrites timestamp)
        old_state = old_state.model_copy(
            update={"updated_at": datetime.now() - timedelta(days=31)}
        )
        state_file = state_manager._get_state_file(old_state.session_id)
        state_file.write_text(
            json.dumps(old_state.model_dump(mode="json"), indent=2, default=str)
        )

        # Create recent completed session
        recent_state = state_manager.create_session("workflow2", "/file2.py")
        recent_state = recent_state.with_phase_completed(
            0, {"done": True}, CheckpointStatus.PASSED
        )
        state_manager.save_state(recent_state)

        # Verify old_state is considered complete
        is_complete = len(
            old_state.completed_phases
        ) > 0 and old_state.current_phase > max(old_state.completed_phases)
        assert (
            is_complete
        ), f"old_state should be complete: completed_phases={old_state.completed_phases}, current_phase={old_state.current_phase}"

        # Run cleanup (30 days threshold)
        deleted_count = state_manager.cleanup_completed(older_than_days=30)

        assert deleted_count == 1
        assert state_manager.load_state(old_state.session_id) is None
        assert state_manager.load_state(recent_state.session_id) is not None

    def test_cleanup_completed_preserves_active_sessions(self, state_manager):
        """Test that cleanup doesn't delete active sessions."""
        # Create old active session
        old_active = state_manager.create_session("workflow1", "/file1.py")

        # Manually backdate
        from datetime import datetime, timedelta

        old_active = old_active.model_copy(
            update={"updated_at": datetime.now() - timedelta(days=31)}
        )
        state_manager.save_state(old_active)

        # Run cleanup
        deleted_count = state_manager.cleanup_completed(older_than_days=30)

        assert deleted_count == 0
        assert state_manager.load_state(old_active.session_id) is not None

    def test_save_state_updates_timestamp(self, state_manager, sample_state):
        """Test that saving state updates the timestamp."""
        # Save first time
        state_manager.save_state(sample_state)
        first_load = state_manager.load_state(sample_state.session_id)

        # Wait a bit
        time.sleep(0.01)

        # Save again
        state_manager.save_state(sample_state)
        second_load = state_manager.load_state(sample_state.session_id)

        assert second_load.updated_at > first_load.updated_at
