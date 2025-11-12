"""Tests for PhaseGates."""

import pytest
from ouroboros.subsystems.workflow.evidence_validator import EvidenceValidator
from ouroboros.subsystems.workflow.hidden_schemas import (
    EvidenceSchema,
    FieldSchema,
    HiddenSchemas,
)
from ouroboros.subsystems.workflow.models import CheckpointStatus, WorkflowState
from ouroboros.subsystems.workflow.phase_gates import PhaseGates


class TestPhaseGates:
    """Tests for PhaseGates."""

    @pytest.fixture
    def temp_workflows_dir(self, tmp_path):
        """Create temporary workflows directory."""
        workflows_dir = tmp_path / "workflows"
        workflows_dir.mkdir()
        return workflows_dir

    @pytest.fixture
    def hidden_schemas(self, temp_workflows_dir):
        """Create HiddenSchemas instance."""
        return HiddenSchemas(temp_workflows_dir)

    @pytest.fixture
    def evidence_validator(self, tmp_path):
        """Create EvidenceValidator instance."""
        return EvidenceValidator(workspace_root=tmp_path)

    @pytest.fixture
    def phase_gates(self, hidden_schemas, evidence_validator):
        """Create PhaseGates instance."""
        return PhaseGates(hidden_schemas, evidence_validator, max_phase=3)

    @pytest.fixture
    def sample_state(self):
        """Create sample workflow state."""
        return WorkflowState(
            session_id="test-123",
            workflow_type="test_workflow",
            target_file="/path/to/file.py",
            current_phase=0,
            completed_phases=[],
        )

    def test_can_advance_to_next_phase(self, phase_gates, sample_state):
        """Test can advance to next phase after completing current."""
        # Complete phase 0
        state = sample_state.with_phase_completed(
            0, {"done": True}, CheckpointStatus.PASSED
        )

        # After completing phase 0, current_phase is now 1
        # Check if we can "advance" to phase 1 (already there)
        allowed, reason = phase_gates.can_advance(state, 1)

        assert allowed is True  # Already at phase 1
        assert "allowed" in reason.lower() or "already" in reason.lower()

    def test_cannot_skip_phases(self, phase_gates, sample_state):
        """Test cannot skip phases."""
        allowed, reason = phase_gates.can_advance(sample_state, 2)

        assert allowed is False
        assert "skip" in reason.lower()

    def test_cannot_go_backwards(self, phase_gates, sample_state):
        """Test cannot go backwards in phases."""
        state = sample_state.with_phase_completed(
            0, {"done": True}, CheckpointStatus.PASSED
        )
        state = state.with_phase_completed(1, {"done": True}, CheckpointStatus.PASSED)

        allowed, reason = phase_gates.can_advance(state, 0)

        assert allowed is False
        assert "backwards" in reason.lower()

    def test_cannot_advance_without_checkpoint_pass(self, phase_gates, sample_state):
        """Test cannot advance without passing checkpoint."""
        # Manually create state with phase 0 completed BUT checkpoint FAILED
        state = sample_state.model_copy(
            update={
                "completed_phases": [0],  # Phase IS completed
                "checkpoints": {0: CheckpointStatus.FAILED},  # But checkpoint FAILED
                "evidence_submitted": {0: {"done": False}},
            }
        )

        # Try to advance to phase 1 (should fail because phase 0 checkpoint failed)
        allowed, reason = phase_gates.can_advance(state, 1)

        assert allowed is False
        assert "checkpoint" in reason.lower()

    def test_cannot_exceed_max_phase(self, phase_gates, sample_state):
        """Test cannot exceed max phase."""
        # Complete phases 0, 1, 2, 3
        state = sample_state
        for phase in range(4):  # Complete phases 0-3
            state = state.with_phase_completed(
                phase, {"done": True}, CheckpointStatus.PASSED
            )
        # Now at phase 4 with phases 0-3 complete

        # Try to advance to 4 (we're already at phase 4, so this should say "already there")
        # Instead, try to advance to 5
        # But wait, first need to check if we're properly at phase 4
        # After completing phase 3, current_phase becomes 4
        # But to check "exceeds max_phase" we need previous phase (3) complete
        # Actually no - after the loop, current_phase=4, completed=[0,1,2,3]
        # To advance to 5, check if phase 4 is complete - it's not!
        # So we get "phase 4 incomplete" not "exceeds"

        # The issue is that max_phase check happens AFTER the "previous phase complete" check
        # So we can never hit it unless we're trying to advance to max_phase + 1
        # when AT max_phase+1

        # Let me re-approach: at phase 3 (with 0-2 complete), try to advance to 4
        # max_phase=3, so phase 4 exceeds. But phase 3 isn't complete yet!

        # Correct approach: at phase 3 (with 0-2 complete + phase 3 complete), try advance to 4
        state = sample_state
        for phase in range(3):  # Complete phases 0-2
            state = state.with_phase_completed(
                phase, {"done": True}, CheckpointStatus.PASSED
            )
        # Now at phase 3, complete it
        state = state.with_phase_completed(3, {"done": True}, CheckpointStatus.PASSED)
        # Now at phase 4 with 0-3 complete

        # But we're now at phase 4, which is already beyond max_phase!
        # The real question: when does the max_phase check trigger?
        # Answer: When trying to advance to a phase > max_phase, IF previous phase is complete

        # So: at phase 3 (with 0-3 complete), try to advance to 4
        # This should fail with "exceeds max_phase"
        # But we just completed phase 3, so current_phase=4!

        # OK final understanding: max_phase is checked when can_advance is called
        # If to_phase > max_phase, fail
        # So: be at phase 3, with phase 2 complete, try to advance to 4
        # But that means phase 3 needs to be complete too...

        # Let me just try: state at phase 3, try advance to 4
        state = sample_state
        for phase in range(3):
            state = state.with_phase_completed(
                phase, {"done": True}, CheckpointStatus.PASSED
            )
        # At phase 3, phases 0-2 complete
        # Complete phase 3
        state = state.with_phase_completed(3, {"done": True}, CheckpointStatus.PASSED)
        # At phase 4, phases 0-3 complete

        # Try advance to 5 (but phase 4 not complete, so will fail with "phase 4 incomplete")
        # Try advance to 4 (already there, will say "already at 4")

        # The only way to hit max_phase is to be in a state where:
        # - current_phase <= max_phase
        # - previous phases complete
        # - try to advance to max_phase + 1

        # So: current_phase=3, phases 0-2 complete, phase 3 complete, try advance to 4
        # But completing phase 3 makes current_phase=4!

        # Solution: manually set state
        state = sample_state.model_copy(
            update={
                "current_phase": 3,
                "completed_phases": [0, 1, 2, 3],
                "checkpoints": {i: CheckpointStatus.PASSED for i in range(4)},
            }
        )

        # Try to advance to 4 (which exceeds max_phase=3)
        allowed, reason = phase_gates.can_advance(state, 4)

        assert allowed is False
        assert "exceeds" in reason.lower()

    def test_complete_phase_with_valid_evidence(
        self, phase_gates, sample_state, temp_workflows_dir
    ):
        """Test completing phase with valid evidence."""
        # Create permissive schema (no gate-definition.yaml)
        result = phase_gates.complete_phase(sample_state, 0, {"task_completed": True})

        assert result.allowed is True
        assert result.new_state is not None
        assert result.new_state.current_phase == 1
        assert 0 in result.new_state.completed_phases

    def test_complete_phase_wrong_phase_fails(self, phase_gates, sample_state):
        """Test completing wrong phase fails."""
        result = phase_gates.complete_phase(sample_state, 1, {"task_completed": True})

        assert result.allowed is False
        assert "Cannot complete phase 1" in result.reason

    def test_complete_phase_with_schema_validation(
        self, phase_gates, sample_state, temp_workflows_dir
    ):
        """Test completing phase with schema validation."""
        import yaml

        # Create gate-definition.yaml
        workflow_dir = temp_workflows_dir / "test_workflow" / "phases" / "0"
        workflow_dir.mkdir(parents=True)

        gate_content = {
            "checkpoint": {"enabled": True, "strict": True},
            "evidence_schema": {
                "task_completed": {"type": "boolean", "required": True}
            },
            "validators": {},
        }

        gate_file = workflow_dir / "gate-definition.yaml"
        gate_file.write_text(yaml.dump(gate_content))

        # Try with invalid evidence (missing required field)
        result = phase_gates.complete_phase(sample_state, 0, {})

        assert result.allowed is False
        assert "validation failed" in result.reason.lower()
        assert result.validation_result is not None
        assert len(result.validation_result.errors) > 0

    def test_complete_phase_non_strict_allows_warnings(
        self, phase_gates, sample_state, temp_workflows_dir
    ):
        """Test non-strict mode allows completion with warnings."""
        import yaml

        # Create gate-definition.yaml (non-strict)
        workflow_dir = temp_workflows_dir / "test_workflow" / "phases" / "0"
        workflow_dir.mkdir(parents=True)

        gate_content = {
            "checkpoint": {"enabled": True, "strict": False},
            "evidence_schema": {
                "task_completed": {"type": "boolean", "required": True}
            },
            "validators": {},
        }

        gate_file = workflow_dir / "gate-definition.yaml"
        gate_file.write_text(yaml.dump(gate_content))

        # Try with invalid evidence
        result = phase_gates.complete_phase(sample_state, 0, {})

        # Non-strict should allow (but log warnings)
        assert result.new_state is not None

    def test_get_phase_status_current_phase(self, phase_gates, sample_state):
        """Test getting status of current phase."""
        status = phase_gates.get_phase_status(sample_state, 0)

        assert status["phase"] == 0
        assert status["is_current"] is True
        assert status["is_completed"] is False
        assert status["accessible"] is True
        assert status["checkpoint_status"] == CheckpointStatus.PENDING.value

    def test_get_phase_status_completed_phase(self, phase_gates, sample_state):
        """Test getting status of completed phase."""
        state = sample_state.with_phase_completed(
            0, {"done": True}, CheckpointStatus.PASSED
        )

        status = phase_gates.get_phase_status(state, 0)

        assert status["is_completed"] is True
        assert status["checkpoint_status"] == CheckpointStatus.PASSED.value
        assert status["accessible"] is True

    def test_get_phase_status_future_phase(self, phase_gates, sample_state):
        """Test getting status of future phase."""
        status = phase_gates.get_phase_status(sample_state, 2)

        assert status["is_current"] is False
        assert status["is_completed"] is False
        assert status["accessible"] is False

    def test_phase_advance_result_to_dict(self, phase_gates, sample_state):
        """Test serializing PhaseAdvanceResult to dict."""
        result = phase_gates.complete_phase(sample_state, 0, {"done": True})

        data = result.to_dict()

        assert "allowed" in data
        assert "reason" in data
