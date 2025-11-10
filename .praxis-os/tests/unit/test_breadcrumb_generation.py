"""
Unit tests for workflow breadcrumb navigation generation.

Tests FR-001 through FR-004: Breadcrumb generation in all workflow action handlers.
Verifies just-in-time disclosure, task count awareness, position awareness, and next phase guidance.

Author: prAxis AI Agent
Date: 2025-11-09
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from ouroboros.subsystems.workflow.engine import WorkflowEngine
from ouroboros.config.schemas.workflow import WorkflowConfig


@pytest.fixture
def engine(tmp_path):
    """Create WorkflowEngine instance for testing with real session persistence."""
    # Use real workflows directory from project
    praxis_os_root = Path(__file__).parent.parent.parent
    
    config = WorkflowConfig(workflows_dir="workflows")
    
    # Create real SessionMapper with file-based state persistence
    from ouroboros.foundation.session_mapper import SessionMapper
    
    # Create test state directory
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    session_mapper = SessionMapper(state_dir=state_dir)
    
    engine = WorkflowEngine(
        config=config,
        base_path=praxis_os_root,
        session_mapper=session_mapper
    )
    
    return engine


class TestStartWorkflowBreadcrumb:
    """Test FR-001: start_workflow() just-in-time disclosure and breadcrumb."""
    
    def test_start_workflow_removes_phase_content(self, engine):
        """Test that start_workflow() does not include phase_content field."""
        result = engine.start_workflow("spec_creation_v1", target_file="test.txt")
        
        # Verify phase_content is NOT in response
        assert "phase_content" not in result, "phase_content should not be in start_workflow response"
        
    def test_start_workflow_includes_breadcrumb(self, engine):
        """Test that start_workflow() includes breadcrumb to get_phase(phase=0)."""
        result = engine.start_workflow("spec_creation_v1", target_file="test.txt")
        
        # Verify breadcrumb fields present
        assert "⚡_NEXT_ACTION" in result, "Breadcrumb should include NEXT_ACTION"
        assert result["⚡_NEXT_ACTION"] == "get_phase(phase=0)", "Should guide to phase 0"
        
    def test_start_workflow_breadcrumb_positioned_last(self, engine):
        """Test that breadcrumb appears at end of response (recency bias)."""
        result = engine.start_workflow("spec_creation_v1", target_file="test.txt")
        
        # Get keys as list to check order
        keys = list(result.keys())
        
        # Verify ⚡_NEXT_ACTION is in the response
        assert "⚡_NEXT_ACTION" in keys, "NEXT_ACTION should be in response"
        
        # Should be near the end (after standard fields)
        next_action_index = keys.index("⚡_NEXT_ACTION")
        assert next_action_index >= len(keys) - 3, "Breadcrumb should be in last 3 positions"


class TestGetPhaseBreadcrumb:
    """Test FR-002: get_phase() task count aware breadcrumb."""
    
    def test_get_phase_shows_task_count(self, engine):
        """Test get_phase() breadcrumb shows task count."""
        # Start workflow
        start_result = engine.start_workflow("spec_creation_v1", target_file="test.txt")
        session_id = start_result["session_id"]
        
        # Get phase 0
        result = engine.get_phase(session_id, phase=0)
        
        # Verify task count info present (specific count may vary based on workflow)
        assert "📊_PHASE_INFO" in result, "Should include phase info"
        assert "Phase 0 has" in result["📊_PHASE_INFO"], "Should show phase number"
        assert "tasks" in result["📊_PHASE_INFO"], "Should mention tasks"
        
    def test_get_phase_guides_to_first_task(self, engine):
        """Test get_phase() breadcrumb points to first task."""
        # Start workflow
        start_result = engine.start_workflow("spec_creation_v1", target_file="test.txt")
        session_id = start_result["session_id"]
        
        # Get phase 0
        result = engine.get_phase(session_id, phase=0)
        
        # Verify next action guides to first task
        assert "⚡_NEXT_ACTION" in result, "Should include next action"
        assert "get_task(phase=0, task_number=1)" in result["⚡_NEXT_ACTION"], "Should guide to task 1"
        
    def test_get_phase_breadcrumb_positioned_last(self, engine):
        """Test that breadcrumb appears at end of response (recency bias)."""
        # Start workflow
        start_result = engine.start_workflow("spec_creation_v1", target_file="test.txt")
        session_id = start_result["session_id"]
        
        # Get phase
        result = engine.get_phase(session_id, phase=0)
        
        # Get keys as list to check order
        keys = list(result.keys())
        
        # Verify breadcrumb fields are at the end
        assert "📊_PHASE_INFO" in keys, "Phase info should be present"
        assert "⚡_NEXT_ACTION" in keys, "Next action should be present"
        
        # Both should be in last few positions
        next_action_index = keys.index("⚡_NEXT_ACTION")
        assert next_action_index == len(keys) - 1, "NEXT_ACTION should be absolute last"


class TestGetTaskBreadcrumb:
    """Test FR-003: get_task() position-aware breadcrumb."""
    
    def test_get_task_shows_position(self, engine):
        """Test get_task() breadcrumb shows current position."""
        # Start workflow
        start_result = engine.start_workflow("spec_creation_v1", target_file="test.txt")
        session_id = start_result["session_id"]
        
        # Get task 1
        result = engine.get_task(session_id, phase=0, task_number=1)
        
        # Verify position info present
        assert "🎯_CURRENT_POSITION" in result, "Should show current position"
        assert "Task 1/" in result["🎯_CURRENT_POSITION"], "Should show task number"
        
    def test_get_task_guides_to_next_task(self, engine):
        """Test get_task() breadcrumb points to next task."""
        # Start workflow
        start_result = engine.start_workflow("spec_creation_v1", target_file="test.txt")
        session_id = start_result["session_id"]
        
        # Get task 1
        result = engine.get_task(session_id, phase=0, task_number=1)
        
        # Verify next action (should guide to task 2 or complete_phase depending on if it's final)
        assert "⚡_NEXT_ACTION" in result, "Should include next action"
        # Next action will be either next task or complete_phase
        assert ("get_task" in result["⚡_NEXT_ACTION"] or 
                "complete_phase" in result["⚡_NEXT_ACTION"]), "Should guide to next step"
        
    def test_get_task_breadcrumb_positioned_last(self, engine):
        """Test that breadcrumb appears at end of response (recency bias)."""
        # Start workflow
        start_result = engine.start_workflow("spec_creation_v1", target_file="test.txt")
        session_id = start_result["session_id"]
        
        result = engine.get_task(session_id, phase=0, task_number=1)
        
        # Get keys as list to check order
        keys = list(result.keys())
        
        # Verify breadcrumb fields are at the end
        assert "🎯_CURRENT_POSITION" in keys, "Position should be present"
        assert "⚡_NEXT_ACTION" in keys, "Next action should be present"
        
        # NEXT_ACTION should be absolute last
        next_action_index = keys.index("⚡_NEXT_ACTION")
        assert next_action_index == len(keys) - 1, "NEXT_ACTION should be absolute last"


class TestCompletePhaseBreadcrumb:
    """Test FR-004: complete_phase() next phase breadcrumb."""
    
    def test_complete_phase_guides_to_next_phase(self, engine):
        """Test complete_phase() breadcrumb points to next phase."""
        # Start workflow
        start_result = engine.start_workflow("spec_creation_v1", target_file="test.txt")
        session_id = start_result["session_id"]
        
        # Complete phase 0
        result = engine.complete_phase(session_id, phase=0, evidence={"test": "data"})
        
        # Verify next action (should guide to next phase if not last)
        if result.get("workflow_complete"):
            # Workflow complete case
            assert "🎉_WORKFLOW_COMPLETE" in result, "Should show completion"
        else:
            # More phases remain case
            assert "✅_PHASE_COMPLETE" in result, "Should show phase completion"
            assert "⚡_NEXT_ACTION" in result, "Should include next action"
            assert "get_phase" in result["⚡_NEXT_ACTION"], "Should guide to next phase"
        
    def test_complete_phase_breadcrumb_positioned_last(self, engine):
        """Test that breadcrumb appears at end of response (recency bias)."""
        # Start workflow
        start_result = engine.start_workflow("spec_creation_v1", target_file="test.txt")
        session_id = start_result["session_id"]
        
        # Complete phase 0
        result = engine.complete_phase(session_id, phase=0, evidence={"test": "data"})
        
        # Get keys as list to check order
        keys = list(result.keys())
        
        # Verify breadcrumb is near the end
        if "⚡_NEXT_ACTION" in keys:
            next_action_index = keys.index("⚡_NEXT_ACTION")
            assert next_action_index == len(keys) - 1, "NEXT_ACTION should be absolute last"


class TestBreadcrumbGracefulDegradation:
    """Test graceful degradation when task count retrieval fails."""
    
    def test_get_phase_task_count_failure_still_provides_breadcrumb(self, engine):
        """Test get_phase() provides generic breadcrumb if task count fails."""
        # Start workflow
        start_result = engine.start_workflow("spec_creation_v1", target_file="test.txt")
        session_id = start_result["session_id"]
        
        # Mock _get_task_count_for_phase to return None (failure)
        with patch.object(engine, '_get_task_count_for_phase', return_value=None):
            result = engine.get_phase(session_id, phase=0)
        
        # Verify generic breadcrumb still provided
        assert "⚡_NEXT_ACTION" in result, "Should still provide next action"
        assert "get_task" in result["⚡_NEXT_ACTION"], "Should guide to first task"
        
    def test_get_task_task_count_failure_still_provides_breadcrumb(self, engine):
        """Test get_task() provides generic breadcrumb if task count fails."""
        # Start workflow
        start_result = engine.start_workflow("spec_creation_v1", target_file="test.txt")
        session_id = start_result["session_id"]
        
        # Mock _get_task_count_for_phase to return None (failure)
        with patch.object(engine, '_get_task_count_for_phase', return_value=None):
            result = engine.get_task(session_id, phase=0, task_number=1)
        
        # Verify generic breadcrumb still provided
        assert "🎯_CURRENT_POSITION" in result, "Should still show position"
        assert "Task 1" in result["🎯_CURRENT_POSITION"], "Should show task number"
        assert "⚡_NEXT_ACTION" in result, "Should still provide next action"
