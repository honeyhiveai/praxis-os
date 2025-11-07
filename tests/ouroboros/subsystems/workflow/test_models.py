"""Tests for workflow models (WorkflowState, PhaseArtifact, etc.)."""

from datetime import datetime

import pytest
from ouroboros.subsystems.workflow.models import (
    CheckpointStatus,
    PhaseArtifact,
    WorkflowMetadata,
    WorkflowState,
)
from pydantic import ValidationError


class TestPhaseArtifact:
    """Tests for PhaseArtifact model."""

    def test_phase_artifact_creation(self):
        """Test creating a phase artifact."""
        artifact = PhaseArtifact(
            phase=1,
            artifact_type="tests",
            file_path="/path/to/tests.py",
            metadata={"lines": 100},
        )

        assert artifact.phase == 1
        assert artifact.artifact_type == "tests"
        assert artifact.file_path == "/path/to/tests.py"
        assert artifact.metadata == {"lines": 100}
        assert isinstance(artifact.timestamp, datetime)

    def test_phase_artifact_immutable(self):
        """Test that phase artifacts are immutable."""
        artifact = PhaseArtifact(
            phase=1, artifact_type="tests", file_path="/path/to/tests.py"
        )

        with pytest.raises(ValidationError, match="Instance is frozen"):
            artifact.phase = 2  # type: ignore

    def test_phase_artifact_rejects_negative_phase(self):
        """Test that negative phase numbers are rejected."""
        with pytest.raises(ValidationError, match="greater than or equal to 0"):
            PhaseArtifact(
                phase=-1, artifact_type="tests", file_path="/path/to/tests.py"
            )

    def test_phase_artifact_rejects_empty_type(self):
        """Test that empty artifact_type is rejected."""
        with pytest.raises(ValidationError, match="at least 1 character"):
            PhaseArtifact(phase=1, artifact_type="", file_path="/path/to/tests.py")

    def test_phase_artifact_rejects_empty_path(self):
        """Test that empty file_path is rejected."""
        with pytest.raises(ValidationError, match="at least 1 character"):
            PhaseArtifact(phase=1, artifact_type="tests", file_path="")


class TestWorkflowState:
    """Tests for WorkflowState model."""

    def test_workflow_state_creation(self):
        """Test creating a workflow state."""
        state = WorkflowState(
            session_id="test-123",
            workflow_type="test_workflow",
            target_file="/path/to/file.py",
            current_phase=0,
        )

        assert state.session_id == "test-123"
        assert state.workflow_type == "test_workflow"
        assert state.target_file == "/path/to/file.py"
        assert state.current_phase == 0
        assert state.completed_phases == []
        assert state.phase_artifacts == {}
        assert state.checkpoints == {}
        assert isinstance(state.created_at, datetime)
        assert isinstance(state.updated_at, datetime)

    def test_workflow_state_immutable(self):
        """Test that workflow state is immutable."""
        state = WorkflowState(
            session_id="test-123",
            workflow_type="test_workflow",
            target_file="/path/to/file.py",
            current_phase=0,
        )

        with pytest.raises(ValidationError, match="Instance is frozen"):
            state.current_phase = 1  # type: ignore

    def test_workflow_state_with_phase_completed(self):
        """Test completing a phase creates new state."""
        state = WorkflowState(
            session_id="test-123",
            workflow_type="test_workflow",
            target_file="/path/to/file.py",
            current_phase=0,
        )

        evidence = {"task_completed": True}
        new_state = state.with_phase_completed(0, evidence, CheckpointStatus.PASSED)

        # Original state unchanged
        assert state.current_phase == 0
        assert state.completed_phases == []

        # New state updated
        assert new_state.current_phase == 1
        assert new_state.completed_phases == [0]
        assert new_state.checkpoints[0] == CheckpointStatus.PASSED
        assert new_state.evidence_submitted[0] == evidence
        assert new_state.updated_at > state.updated_at

    def test_workflow_state_with_multiple_phases_completed(self):
        """Test completing multiple phases."""
        state = WorkflowState(
            session_id="test-123",
            workflow_type="test_workflow",
            target_file="/path/to/file.py",
            current_phase=0,
        )

        # Complete phase 0
        state = state.with_phase_completed(0, {"task1": True}, CheckpointStatus.PASSED)
        assert state.current_phase == 1
        assert state.completed_phases == [0]

        # Complete phase 1
        state = state.with_phase_completed(1, {"task2": True}, CheckpointStatus.PASSED)
        assert state.current_phase == 2
        assert state.completed_phases == [0, 1]

        # Verify evidence preserved
        assert state.evidence_submitted[0] == {"task1": True}
        assert state.evidence_submitted[1] == {"task2": True}

    def test_workflow_state_with_artifact(self):
        """Test adding an artifact creates new state."""
        state = WorkflowState(
            session_id="test-123",
            workflow_type="test_workflow",
            target_file="/path/to/file.py",
            current_phase=0,
        )

        artifact = PhaseArtifact(
            phase=0, artifact_type="tests", file_path="/path/to/tests.py"
        )
        new_state = state.with_artifact(artifact)

        # Original state unchanged
        assert state.phase_artifacts == {}

        # New state has artifact
        assert new_state.phase_artifacts[0] == artifact
        assert new_state.updated_at > state.updated_at

    def test_workflow_state_rejects_negative_phase(self):
        """Test that negative phase numbers are rejected."""
        with pytest.raises(ValidationError, match="greater than or equal to 0"):
            WorkflowState(
                session_id="test-123",
                workflow_type="test_workflow",
                target_file="/path/to/file.py",
                current_phase=-1,
            )

    def test_workflow_state_rejects_empty_session_id(self):
        """Test that empty session_id is rejected."""
        with pytest.raises(ValidationError, match="at least 1 character"):
            WorkflowState(
                session_id="",
                workflow_type="test_workflow",
                target_file="/path/to/file.py",
                current_phase=0,
            )


class TestWorkflowMetadata:
    """Tests for WorkflowMetadata model."""

    def test_workflow_metadata_creation(self):
        """Test creating workflow metadata."""
        metadata = WorkflowMetadata(
            workflow_type="test_workflow",
            version="1.0",
            description="Test workflow",
            max_phase=3,
            metadata={"category": "testing"},
        )

        assert metadata.workflow_type == "test_workflow"
        assert metadata.version == "1.0"
        assert metadata.description == "Test workflow"
        assert metadata.max_phase == 3
        assert metadata.metadata == {"category": "testing"}

    def test_workflow_metadata_immutable(self):
        """Test that workflow metadata is immutable."""
        metadata = WorkflowMetadata(
            workflow_type="test_workflow",
            version="1.0",
            description="Test workflow",
            max_phase=3,
        )

        with pytest.raises(ValidationError, match="Instance is frozen"):
            metadata.max_phase = 5  # type: ignore

    def test_workflow_metadata_rejects_empty_workflow_type(self):
        """Test that empty workflow_type is rejected."""
        with pytest.raises(ValidationError, match="at least 1 character"):
            WorkflowMetadata(
                workflow_type="", version="1.0", description="Test", max_phase=3
            )

    def test_workflow_metadata_rejects_negative_max_phase(self):
        """Test that negative max_phase is rejected."""
        with pytest.raises(ValidationError, match="greater than or equal to 0"):
            WorkflowMetadata(
                workflow_type="test", version="1.0", description="Test", max_phase=-1
            )
