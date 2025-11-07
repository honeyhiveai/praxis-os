"""
Unit tests for ouroboros.config.schemas.workflow.

Tests WorkflowConfig validation including:
    - Default values
    - Custom values
    - Field constraints (min/max ranges)
    - Adversarial design enforcement (evidence_schemas_exposed)
    - Error message quality
"""

from pathlib import Path

import pytest
from ouroboros.config.schemas.workflow import WorkflowConfig
from pydantic import ValidationError


class TestWorkflowConfigDefaults:
    """Test WorkflowConfig default values."""

    def test_workflow_config_defaults(self):
        """WorkflowConfig should have sensible defaults for all fields."""
        config = WorkflowConfig()

        assert config.workflows_dir == Path(".praxis-os/workflows")
        assert config.state_dir == Path(".praxis-os/workflow_states")
        assert config.session_timeout_minutes == 1440  # 24 hours
        assert config.cleanup_completed_after_days == 30
        assert config.evidence_schemas_exposed is False

    def test_workflow_config_immutable(self):
        """WorkflowConfig should be immutable (frozen)."""
        config = WorkflowConfig()

        with pytest.raises(ValidationError, match="frozen"):
            config.session_timeout_minutes = 2880


class TestWorkflowConfigCustomValues:
    """Test WorkflowConfig with custom values."""

    def test_workflow_config_custom_paths(self):
        """WorkflowConfig should accept custom directory paths."""
        config = WorkflowConfig(
            workflows_dir=Path("custom/workflows"),
            state_dir=Path("custom/states"),
        )

        assert config.workflows_dir == Path("custom/workflows")
        assert config.state_dir == Path("custom/states")

    def test_workflow_config_custom_timeouts(self):
        """WorkflowConfig should accept custom timeout values within valid ranges."""
        config = WorkflowConfig(
            session_timeout_minutes=720,  # 12 hours
            cleanup_completed_after_days=7,  # 1 week
        )

        assert config.session_timeout_minutes == 720
        assert config.cleanup_completed_after_days == 7

    def test_workflow_config_minimum_timeouts(self):
        """WorkflowConfig should accept minimum valid timeout values."""
        config = WorkflowConfig(
            session_timeout_minutes=60,  # 1 hour (minimum)
            cleanup_completed_after_days=1,  # 1 day (minimum)
        )

        assert config.session_timeout_minutes == 60
        assert config.cleanup_completed_after_days == 1

    def test_workflow_config_maximum_timeouts(self):
        """WorkflowConfig should accept maximum valid timeout values."""
        config = WorkflowConfig(
            session_timeout_minutes=10080,  # 7 days (maximum)
            cleanup_completed_after_days=365,  # 1 year (maximum)
        )

        assert config.session_timeout_minutes == 10080
        assert config.cleanup_completed_after_days == 365


class TestWorkflowConfigConstraints:
    """Test WorkflowConfig field constraints and validation rules."""

    def test_session_timeout_too_low(self):
        """WorkflowConfig should reject session_timeout_minutes < 60."""
        with pytest.raises(ValidationError, match="greater than or equal to 60"):
            WorkflowConfig(session_timeout_minutes=30)

    def test_session_timeout_too_high(self):
        """WorkflowConfig should reject session_timeout_minutes > 10080."""
        with pytest.raises(ValidationError, match="less than or equal to 10080"):
            WorkflowConfig(session_timeout_minutes=20000)

    def test_cleanup_days_too_low(self):
        """WorkflowConfig should reject cleanup_completed_after_days < 1."""
        with pytest.raises(ValidationError, match="greater than or equal to 1"):
            WorkflowConfig(cleanup_completed_after_days=0)

    def test_cleanup_days_too_high(self):
        """WorkflowConfig should reject cleanup_completed_after_days > 365."""
        with pytest.raises(ValidationError, match="less than or equal to 365"):
            WorkflowConfig(cleanup_completed_after_days=400)


class TestAdversarialDesignEnforcement:
    """Test adversarial design principle enforcement for evidence_schemas_exposed."""

    def test_evidence_schemas_exposed_false_accepted(self):
        """WorkflowConfig should accept evidence_schemas_exposed=False (required value)."""
        config = WorkflowConfig(evidence_schemas_exposed=False)
        assert config.evidence_schemas_exposed is False

    def test_evidence_schemas_exposed_true_rejected(self):
        """WorkflowConfig should reject evidence_schemas_exposed=True (adversarial design)."""
        with pytest.raises(
            ValidationError,
            match=r"evidence_schemas_exposed MUST be False",
        ):
            WorkflowConfig(evidence_schemas_exposed=True)

    def test_evidence_schemas_error_message_quality(self):
        """Error message for evidence_schemas_exposed=True should be actionable."""
        with pytest.raises(ValidationError) as exc_info:
            WorkflowConfig(evidence_schemas_exposed=True)

        error_str = str(exc_info.value)
        assert "MUST be False" in error_str
        assert "adversarial design" in error_str
        assert "Remediation" in error_str
        assert "standards/development/adversarial-design-for-ai-systems.md" in error_str


class TestWorkflowConfigSerialization:
    """Test WorkflowConfig serialization and deserialization."""

    def test_workflow_config_to_dict(self):
        """WorkflowConfig should serialize to dict with correct structure."""
        config = WorkflowConfig(
            workflows_dir=Path("custom/workflows"),
            session_timeout_minutes=720,
        )

        data = config.model_dump()
        assert data["workflows_dir"] == Path("custom/workflows")
        assert data["session_timeout_minutes"] == 720
        assert data["evidence_schemas_exposed"] is False

    def test_workflow_config_from_dict(self):
        """WorkflowConfig should deserialize from dict correctly."""
        data = {
            "workflows_dir": "custom/workflows",
            "state_dir": "custom/states",
            "session_timeout_minutes": 720,
            "cleanup_completed_after_days": 7,
            "evidence_schemas_exposed": False,
        }

        config = WorkflowConfig(**data)
        assert config.workflows_dir == Path("custom/workflows")
        assert config.state_dir == Path("custom/states")
        assert config.session_timeout_minutes == 720
        assert config.cleanup_completed_after_days == 7
        assert config.evidence_schemas_exposed is False


class TestErrorMessages:
    """Test error message quality and actionability."""

    def test_session_timeout_error_message(self):
        """Error message for invalid session_timeout_minutes should be clear."""
        with pytest.raises(ValidationError) as exc_info:
            WorkflowConfig(session_timeout_minutes=30)

        error_str = str(exc_info.value)
        assert "session_timeout_minutes" in error_str.lower()
        assert "60" in error_str

    def test_cleanup_days_error_message(self):
        """Error message for invalid cleanup_completed_after_days should be clear."""
        with pytest.raises(ValidationError) as exc_info:
            WorkflowConfig(cleanup_completed_after_days=0)

        error_str = str(exc_info.value)
        assert "cleanup_completed_after_days" in error_str.lower()
        assert "1" in error_str

    def test_adversarial_design_error_comprehensive(self):
        """Error message for evidence schema exposure should explain WHY it's forbidden."""
        with pytest.raises(ValidationError) as exc_info:
            WorkflowConfig(evidence_schemas_exposed=True)

        error_str = str(exc_info.value)
        # Should explain the problem
        assert "MUST be False" in error_str
        # Should explain the reason
        assert "adversarial design" in error_str
        # Should explain the impact
        assert any(
            word in error_str.lower()
            for word in ["game", "validation", "expected", "work"]
        )
        # Should provide remediation
        assert "Remediation" in error_str
        # Should reference documentation
        assert "adversarial-design-for-ai-systems.md" in error_str
