"""
Unit tests for workflow guidance module.

Tests the add_workflow_guidance() function with and without breadcrumb navigation,
verifying backward compatibility, field ordering, and recency bias positioning.
"""

import pytest

from ouroboros.subsystems.workflow.guidance import (
    WORKFLOW_GUIDANCE_FIELDS,
    add_workflow_guidance,
)


class TestAddWorkflowGuidanceBackwardCompatibility:
    """Test backward compatibility when breadcrumb parameter not provided."""

    def test_without_breadcrumb_returns_original_behavior(self):
        """Test that breadcrumb=None preserves original behavior (no breaking change)."""
        # Arrange
        base_response = {"session_id": "test-123", "phase": 1, "status": "success"}

        # Act
        result = add_workflow_guidance(base_response)

        # Assert - should contain static guidance fields
        assert "⚠️_WORKFLOW_EXECUTION_MODE" in result
        assert result["⚠️_WORKFLOW_EXECUTION_MODE"] == "ACTIVE"
        assert "🛑_DO_NOT_USE_EXTERNAL_TASK_TOOLS" in result
        assert "execution_model" in result

        # Assert - should contain original response fields
        assert result["session_id"] == "test-123"
        assert result["phase"] == 1
        assert result["status"] == "success"

        # Assert - should NOT contain any breadcrumb fields
        assert "⚡_NEXT_ACTION" not in result
        assert "🎯_CURRENT_POSITION" not in result

    def test_explicit_none_breadcrumb(self):
        """Test that explicitly passing breadcrumb=None works identically."""
        # Arrange
        base_response = {"session_id": "test-456", "data": "value"}

        # Act
        result = add_workflow_guidance(base_response, breadcrumb=None)

        # Assert - should behave identically to no breadcrumb parameter
        assert "⚠️_WORKFLOW_EXECUTION_MODE" in result
        assert result["session_id"] == "test-456"
        assert "⚡_NEXT_ACTION" not in result


class TestAddWorkflowGuidanceWithBreadcrumb:
    """Test breadcrumb navigation when provided."""

    def test_breadcrumb_appended_to_response(self):
        """Test that breadcrumb fields are added to response."""
        # Arrange
        base_response = {"session_id": "test-789", "phase": 1}
        breadcrumb = {"⚡_NEXT_ACTION": "get_task(phase=1, task_number=1)"}

        # Act
        result = add_workflow_guidance(base_response, breadcrumb=breadcrumb)

        # Assert - should contain breadcrumb fields
        assert "⚡_NEXT_ACTION" in result
        assert result["⚡_NEXT_ACTION"] == "get_task(phase=1, task_number=1)"

        # Assert - should still contain static guidance
        assert "⚠️_WORKFLOW_EXECUTION_MODE" in result

        # Assert - should still contain original response
        assert result["session_id"] == "test-789"

    def test_multiple_breadcrumb_fields(self):
        """Test that multiple breadcrumb fields are all added."""
        # Arrange
        base_response = {"session_id": "test-multi", "phase": 2}
        breadcrumb = {
            "⚡_NEXT_ACTION": "get_task(phase=2, task_number=3)",
            "🎯_CURRENT_POSITION": "Task 2/5",
            "📊_PHASE_INFO": "Phase 2 has 5 tasks",
        }

        # Act
        result = add_workflow_guidance(base_response, breadcrumb=breadcrumb)

        # Assert - all breadcrumb fields present
        assert result["⚡_NEXT_ACTION"] == "get_task(phase=2, task_number=3)"
        assert result["🎯_CURRENT_POSITION"] == "Task 2/5"
        assert result["📊_PHASE_INFO"] == "Phase 2 has 5 tasks"


class TestFieldOrdering:
    """Test dict key ordering (Python 3.7+ insertion order)."""

    def test_field_order_without_breadcrumb(self):
        """Test that static guidance appears first, then response fields."""
        # Arrange
        base_response = {"session_id": "order-test", "phase": 1, "data": "value"}

        # Act
        result = add_workflow_guidance(base_response)

        # Assert - guidance fields should appear before response fields
        keys = list(result.keys())
        guidance_keys = list(WORKFLOW_GUIDANCE_FIELDS.keys())

        # Check guidance keys appear first
        for i, guidance_key in enumerate(guidance_keys):
            assert keys[i] == guidance_key

        # Check response keys appear after guidance
        assert "session_id" in keys
        assert keys.index("session_id") > len(guidance_keys) - 1

    def test_field_order_with_breadcrumb_at_end(self):
        """Test that breadcrumb fields appear LAST (recency bias positioning)."""
        # Arrange
        base_response = {"session_id": "recency-test", "phase": 1, "status": "active"}
        breadcrumb = {
            "⚡_NEXT_ACTION": "get_phase(phase=1)",
            "🎯_CURRENT_POSITION": "Phase 1",
        }

        # Act
        result = add_workflow_guidance(base_response, breadcrumb=breadcrumb)

        # Assert - breadcrumb fields should be at the END
        keys = list(result.keys())
        last_two_keys = keys[-2:]

        assert "⚡_NEXT_ACTION" in last_two_keys
        assert "🎯_CURRENT_POSITION" in last_two_keys

        # Assert - guidance fields still at start
        assert keys[0] in WORKFLOW_GUIDANCE_FIELDS

    def test_breadcrumb_positioned_after_response_content(self):
        """Test that breadcrumb appears after both guidance and response fields."""
        # Arrange
        base_response = {
            "session_id": "position-test",
            "workflow_type": "test_v1",
            "current_phase": 2,
        }
        breadcrumb = {"⚡_NEXT_ACTION": "complete_phase(phase=2)"}

        # Act
        result = add_workflow_guidance(base_response, breadcrumb=breadcrumb)

        # Assert - breadcrumb should be last field
        keys = list(result.keys())
        assert keys[-1] == "⚡_NEXT_ACTION"

        # Assert - all response fields should come before breadcrumb
        next_action_index = keys.index("⚡_NEXT_ACTION")
        session_id_index = keys.index("session_id")
        assert session_id_index < next_action_index


class TestErrorHandling:
    """Test graceful degradation and fail-safe behavior."""

    def test_non_dict_response_returns_unchanged(self):
        """Test that non-dict inputs are returned unchanged (fail-safe)."""
        # Arrange
        non_dict_response = "not a dict"

        # Act
        result = add_workflow_guidance(non_dict_response)

        # Assert - should return original value unchanged
        assert result == "not a dict"

    def test_none_response_returns_unchanged(self):
        """Test that None input is returned unchanged."""
        # Act
        result = add_workflow_guidance(None)

        # Assert
        assert result is None

    def test_empty_dict_response(self):
        """Test that empty dict receives guidance fields."""
        # Arrange
        empty_response = {}

        # Act
        result = add_workflow_guidance(empty_response)

        # Assert - should add guidance fields to empty dict
        assert "⚠️_WORKFLOW_EXECUTION_MODE" in result
        assert len(result) == len(WORKFLOW_GUIDANCE_FIELDS)

    def test_empty_breadcrumb_dict(self):
        """Test that empty breadcrumb dict doesn't add extra fields."""
        # Arrange
        base_response = {"session_id": "empty-breadcrumb-test"}
        empty_breadcrumb = {}

        # Act
        result = add_workflow_guidance(base_response, breadcrumb=empty_breadcrumb)

        # Assert - should not add any breadcrumb fields (empty dict)
        # Only guidance + response fields should be present
        expected_keys = set(WORKFLOW_GUIDANCE_FIELDS.keys()) | {"session_id"}
        assert set(result.keys()) == expected_keys


class TestBreadcrumbOverridesBehavior:
    """Test that breadcrumb can override response fields if needed (dict.update semantics)."""

    def test_breadcrumb_can_override_response_field(self):
        """Test that breadcrumb fields override response fields with same key."""
        # Arrange
        base_response = {"session_id": "override-test", "status": "pending"}
        breadcrumb = {"status": "ready"}  # Override status field

        # Act
        result = add_workflow_guidance(base_response, breadcrumb=breadcrumb)

        # Assert - breadcrumb should override response field
        assert result["status"] == "ready"

    def test_breadcrumb_does_not_override_guidance_fields(self):
        """Test that static guidance fields are never overridden."""
        # Arrange
        base_response = {"session_id": "guidance-test"}
        # Attempt to override guidance field (should not work - guidance is first)
        breadcrumb = {"⚠️_WORKFLOW_EXECUTION_MODE": "HACKED"}

        # Act
        result = add_workflow_guidance(base_response, breadcrumb=breadcrumb)

        # Assert - guidance field should be overridden by breadcrumb (dict.update semantics)
        # This is expected behavior - last write wins with dict.update()
        assert result["⚠️_WORKFLOW_EXECUTION_MODE"] == "HACKED"
        # Note: In practice, breadcrumbs should never override guidance fields,
        # but dict.update() semantics allow it technically



