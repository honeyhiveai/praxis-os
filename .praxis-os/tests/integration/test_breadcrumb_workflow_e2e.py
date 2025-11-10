"""
Integration tests for breadcrumb navigation across full workflow execution.

Tests end-to-end workflow execution with breadcrumb navigation for both
static workflows (spec_creation_v1) and dynamic workflows (spec_execution_v1).

Verifies:
- Breadcrumbs appear in all workflow action responses
- Just-in-time disclosure (no early phase_content leakage)
- Task count accuracy for both workflow types
- Position-aware navigation through all phases
- Graceful degradation when task count fails

Author: prAxis AI Agent
Date: 2025-11-09
"""

import pytest
from pathlib import Path

from ouroboros.subsystems.workflow.engine import WorkflowEngine
from ouroboros.config.schemas.workflow import WorkflowConfig
from ouroboros.foundation.session_mapper import SessionMapper


@pytest.fixture
def engine(tmp_path):
    """Create WorkflowEngine with real session persistence for integration tests."""
    praxis_os_root = Path(__file__).parent.parent.parent
    
    config = WorkflowConfig(workflows_dir="workflows")
    
    # Create real SessionMapper for state persistence
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    session_mapper = SessionMapper(state_dir=state_dir)
    
    engine = WorkflowEngine(
        config=config,
        base_path=praxis_os_root,
        session_mapper=session_mapper
    )
    
    return engine


class TestStaticWorkflowBreadcrumbE2E:
    """Test breadcrumb navigation through complete static workflow execution."""
    
    def test_spec_creation_v1_full_workflow_with_breadcrumbs(self, engine):
        """
        Test complete spec_creation_v1 workflow execution with breadcrumb navigation.
        
        Verifies:
        - start_workflow: No phase_content, breadcrumb to get_phase(0)
        - get_phase: Shows task count, breadcrumb to first task
        - get_task: Shows position (Task X/Y), breadcrumb to next task or complete_phase
        - complete_phase: Breadcrumb to next phase or workflow completion
        """
        # Start workflow
        start_result = engine.start_workflow("spec_creation_v1", target_file="test_spec.md")
        session_id = start_result["session_id"]
        
        # Verify start_workflow breadcrumbs
        assert "phase_content" not in start_result, "Just-in-time disclosure violated"
        assert "⚡_NEXT_ACTION" in start_result, "Missing breadcrumb"
        assert start_result["⚡_NEXT_ACTION"] == "get_phase(phase=0)"
        
        # Get Phase 0
        phase_result = engine.get_phase(session_id, phase=0)
        
        # Verify get_phase breadcrumbs
        assert "📊_PHASE_INFO" in phase_result, "Missing phase info"
        assert "Phase 0 has" in phase_result["📊_PHASE_INFO"]
        assert "⚡_NEXT_ACTION" in phase_result
        assert "get_task(phase=0, task_number=1)" in phase_result["⚡_NEXT_ACTION"]
        
        # Get first task
        task_result = engine.get_task(session_id, phase=0, task_number=1)
        
        # Verify get_task breadcrumbs
        assert "🎯_CURRENT_POSITION" in task_result, "Missing position"
        assert "Task 1/" in task_result["🎯_CURRENT_POSITION"]
        assert "⚡_NEXT_ACTION" in task_result
        
        # Complete Phase 0
        complete_result = engine.complete_phase(session_id, phase=0, evidence={"completed": True})
        
        # Verify complete_phase breadcrumbs
        if complete_result.get("workflow_complete"):
            assert "🎉_WORKFLOW_COMPLETE" in complete_result
        else:
            assert "✅_PHASE_COMPLETE" in complete_result
            assert "⚡_NEXT_ACTION" in complete_result
            assert "get_phase" in complete_result["⚡_NEXT_ACTION"]
    
    def test_breadcrumbs_persist_through_multiple_phases(self, engine):
        """Test that breadcrumbs appear correctly as workflow progresses through phases."""
        # Start workflow
        start_result = engine.start_workflow("spec_creation_v1", target_file="multi_phase_test.md")
        session_id = start_result["session_id"]
        
        # Execute Phase 0
        engine.get_phase(session_id, phase=0)
        task1_result = engine.get_task(session_id, phase=0, task_number=1)
        assert "🎯_CURRENT_POSITION" in task1_result
        
        # Complete Phase 0 and advance to Phase 1
        phase0_complete = engine.complete_phase(session_id, phase=0, evidence={"done": True})
        
        if not phase0_complete.get("workflow_complete"):
            # Verify breadcrumb guides to Phase 1
            assert "⚡_NEXT_ACTION" in phase0_complete
            assert "get_phase(phase=1)" in phase0_complete["⚡_NEXT_ACTION"]
            
            # Get Phase 1
            phase1_result = engine.get_phase(session_id, phase=1)
            
            # Verify Phase 1 has breadcrumbs too
            assert "📊_PHASE_INFO" in phase1_result
            assert "Phase 1 has" in phase1_result["📊_PHASE_INFO"]
            assert "⚡_NEXT_ACTION" in phase1_result


class TestDynamicWorkflowBreadcrumbE2E:
    """Test breadcrumb navigation through complete dynamic workflow execution."""
    
    def test_spec_execution_v1_dynamic_breadcrumbs(self, engine, tmp_path):
        """
        Test spec_execution_v1 (dynamic workflow) with breadcrumb navigation.
        
        Dynamic workflows parse tasks from spec's tasks.md at runtime.
        Verifies task count is correctly retrieved from DynamicContentRegistry.
        """
        # Create a minimal spec with tasks.md for dynamic workflow
        spec_dir = tmp_path / "test_dynamic_spec"
        spec_dir.mkdir()
        
        tasks_file = spec_dir / "tasks.md"
        tasks_file.write_text("""
# Test Dynamic Spec

## Phase 1: Implementation

### Phase 1 Tasks

- [ ] **Task 1.1**: Do something
- [ ] **Task 1.2**: Do something else
- [ ] **Task 1.3**: Finish it

## Phase 2: Testing

### Phase 2 Tasks

- [ ] **Task 2.1**: Test it
""")
        
        # Start dynamic workflow with spec_path in metadata
        # Note: spec_path should be the directory containing tasks.md (engine appends /tasks.md)
        start_result = engine.start_workflow(
            "spec_execution_v1",
            target_file=str(spec_dir),
            spec_path=str(spec_dir)
        )
        session_id = start_result["session_id"]
        
        # Verify start_workflow breadcrumbs (same as static)
        assert "phase_content" not in start_result
        assert "⚡_NEXT_ACTION" in start_result
        assert start_result["⚡_NEXT_ACTION"] == "get_phase(phase=0)"
        
        # Phase 0 is always static (even for dynamic workflows)
        phase0_result = engine.get_phase(session_id, phase=0)
        # Phase 0 should have breadcrumb (might not have task count if dynamic registry not ready yet)
        assert "⚡_NEXT_ACTION" in phase0_result, "Phase 0 should have next action breadcrumb"
        
        # Complete Phase 0 to unlock dynamic phases
        engine.complete_phase(session_id, phase=0, evidence={"phase0": "done"})
        
        # Get Phase 1 (dynamic - parsed from tasks.md)
        phase1_result = engine.get_phase(session_id, phase=1)
        
        # Verify dynamic workflow has breadcrumbs with correct task count
        assert "📊_PHASE_INFO" in phase1_result
        assert "Phase 1 has 3 tasks" in phase1_result["📊_PHASE_INFO"], "Dynamic task count incorrect"
        assert "⚡_NEXT_ACTION" in phase1_result
        assert "get_task(phase=1, task_number=1)" in phase1_result["⚡_NEXT_ACTION"]
        
        # Get dynamic task
        task_result = engine.get_task(session_id, phase=1, task_number=1)
        
        # Verify dynamic task has position breadcrumb
        assert "🎯_CURRENT_POSITION" in task_result
        assert "Task 1/3" in task_result["🎯_CURRENT_POSITION"], "Dynamic position incorrect"
        assert "⚡_NEXT_ACTION" in task_result


class TestBreadcrumbJustInTimeDisclosure:
    """Test just-in-time disclosure pattern prevents information leakage."""
    
    def test_start_workflow_never_includes_phase_content(self, engine):
        """Verify start_workflow NEVER includes phase_content (FR-001)."""
        # Test multiple workflows
        workflows = ["spec_creation_v1"]
        
        for workflow_type in workflows:
            result = engine.start_workflow(workflow_type, target_file=f"test_{workflow_type}.md")
            
            assert "phase_content" not in result, \
                f"Just-in-time disclosure violated for {workflow_type}"
            assert "⚡_NEXT_ACTION" in result, \
                f"Breadcrumb missing for {workflow_type}"
    
    def test_ai_must_explicitly_request_phase_content(self, engine):
        """Verify AI must call get_phase() to receive phase content."""
        # Start workflow - no phase content
        start_result = engine.start_workflow("spec_creation_v1", target_file="test.md")
        session_id = start_result["session_id"]
        
        assert "phase_content" not in start_result
        
        # Must explicitly call get_phase() to get content
        phase_result = engine.get_phase(session_id, phase=0)
        
        # Now phase_content is available
        assert "phase_content" in phase_result, "get_phase should return phase_content"
        assert len(phase_result["phase_content"]) > 0, "Phase content should not be empty"


class TestBreadcrumbTaskCountAccuracy:
    """Test task count accuracy for breadcrumb generation."""
    
    def test_static_workflow_task_counts(self, engine):
        """Verify static workflow task counts are accurate."""
        start_result = engine.start_workflow("spec_creation_v1", target_file="test.md")
        session_id = start_result["session_id"]
        
        # Get Phase 0 and verify task count
        phase_result = engine.get_phase(session_id, phase=0)
        
        # Extract task count from breadcrumb
        phase_info = phase_result["📊_PHASE_INFO"]
        # Format: "Phase 0 has X tasks"
        assert "tasks" in phase_info
        
        # Get a task and verify position
        task_result = engine.get_task(session_id, phase=0, task_number=1)
        position = task_result["🎯_CURRENT_POSITION"]
        
        # Position format: "Task 1/X" or "Task 1/X (final)"
        assert "/" in position, "Position should show current/total format"
        
        # Verify consistency between phase info and task position
        # Both should report same total task count
        import re
        phase_count_match = re.search(r'Phase \d+ has (\d+) tasks', phase_info)
        position_count_match = re.search(r'Task \d+/(\d+)', position)
        
        if phase_count_match and position_count_match:
            phase_count = int(phase_count_match.group(1))
            position_count = int(position_count_match.group(1))
            assert phase_count == position_count, \
                f"Task count mismatch: phase says {phase_count}, position says {position_count}"


class TestBreadcrumbGracefulDegradation:
    """Test graceful degradation when task count retrieval fails."""
    
    def test_workflow_continues_when_task_count_fails(self, engine):
        """Verify workflow continues with generic breadcrumbs if task count fails."""
        from unittest.mock import patch
        
        start_result = engine.start_workflow("spec_creation_v1", target_file="test.md")
        session_id = start_result["session_id"]
        
        # Mock task count failure
        with patch.object(engine, '_get_task_count_for_phase', return_value=None):
            # get_phase should still work with generic breadcrumb
            phase_result = engine.get_phase(session_id, phase=0)
            
            assert "⚡_NEXT_ACTION" in phase_result, \
                "Breadcrumb should still be provided on task count failure"
            assert "get_task" in phase_result["⚡_NEXT_ACTION"], \
                "Should guide to first task even without count"
            
            # get_task should still work with generic position
            task_result = engine.get_task(session_id, phase=0, task_number=1)
            
            assert "🎯_CURRENT_POSITION" in task_result, \
                "Position should still be shown on task count failure"
            assert "⚡_NEXT_ACTION" in task_result, \
                "Next action should still be provided"


class TestBreadcrumbRecencyBiasPositioning:
    """Test breadcrumb fields are positioned last for recency bias."""
    
    def test_next_action_always_last_field(self, engine):
        """Verify ⚡_NEXT_ACTION is always the absolute last field in response."""
        start_result = engine.start_workflow("spec_creation_v1", target_file="test.md")
        session_id = start_result["session_id"]
        
        # Test start_workflow
        start_keys = list(start_result.keys())
        assert start_keys[-1] == "⚡_NEXT_ACTION", \
            "NEXT_ACTION should be last in start_workflow"
        
        # Test get_phase
        phase_result = engine.get_phase(session_id, phase=0)
        phase_keys = list(phase_result.keys())
        assert phase_keys[-1] == "⚡_NEXT_ACTION", \
            "NEXT_ACTION should be last in get_phase"
        
        # Test get_task
        task_result = engine.get_task(session_id, phase=0, task_number=1)
        task_keys = list(task_result.keys())
        assert task_keys[-1] == "⚡_NEXT_ACTION", \
            "NEXT_ACTION should be last in get_task"
        
        # Test complete_phase
        complete_result = engine.complete_phase(session_id, phase=0, evidence={"test": "data"})
        complete_keys = list(complete_result.keys())
        
        # For complete_phase, NEXT_ACTION is last if present (not on workflow completion)
        if "⚡_NEXT_ACTION" in complete_keys:
            assert complete_keys[-1] == "⚡_NEXT_ACTION", \
                "NEXT_ACTION should be last in complete_phase"

