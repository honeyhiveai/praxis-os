"""
Backward compatibility tests for breadcrumb navigation changes.

Verifies that the breadcrumb navigation enhancements do not break:
- Existing workflow sessions
- Existing code calling add_workflow_guidance() without breadcrumb parameter
- Static guidance fields in responses
- Compliant AI workflows

Author: prAxis AI Agent
Date: 2025-11-09
"""

import pytest
from pathlib import Path

from ouroboros.subsystems.workflow.engine import WorkflowEngine
from ouroboros.subsystems.workflow.guidance import add_workflow_guidance
from ouroboros.config.schemas.workflow import WorkflowConfig
from ouroboros.foundation.session_mapper import SessionMapper


@pytest.fixture
def engine(tmp_path):
    """Create WorkflowEngine for backward compatibility testing."""
    praxis_os_root = Path(__file__).parent.parent.parent
    
    config = WorkflowConfig(workflows_dir="workflows")
    
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    session_mapper = SessionMapper(state_dir=state_dir)
    
    engine = WorkflowEngine(
        config=config,
        base_path=praxis_os_root,
        session_mapper=session_mapper
    )
    
    return engine


class TestAddWorkflowGuidanceBackwardCompatibility:
    """Test add_workflow_guidance() function backward compatibility."""
    
    def test_guidance_function_works_without_breadcrumb_parameter(self):
        """Test add_workflow_guidance() can be called without breadcrumb (no breaking change)."""
        # Old calling pattern (pre-breadcrumb)
        response = {
            "session_id": "test-123",
            "workflow_type": "test_workflow",
            "data": "some data"
        }
        
        # Should work without breadcrumb parameter
        result = add_workflow_guidance(response)
        
        # Verify static guidance fields present
        assert "⚠️_WORKFLOW_EXECUTION_MODE" in result
        assert "🛑_DO_NOT_USE_EXTERNAL_TASK_TOOLS" in result
        
        # Verify original response data preserved
        assert result["session_id"] == "test-123"
        assert result["workflow_type"] == "test_workflow"
        assert result["data"] == "some data"
    
    def test_guidance_function_preserves_static_fields(self):
        """Test static guidance fields are always present."""
        response = {"test": "data"}
        
        # Call without breadcrumb
        result_without = add_workflow_guidance(response)
        
        # Call with breadcrumb
        result_with = add_workflow_guidance(response, breadcrumb={"⚡_NEXT_ACTION": "test"})
        
        # Both should have static fields
        for result in [result_without, result_with]:
            assert "⚠️_WORKFLOW_EXECUTION_MODE" in result
            assert result["⚠️_WORKFLOW_EXECUTION_MODE"] == "ACTIVE"
            assert "🛑_DO_NOT_USE_EXTERNAL_TASK_TOOLS" in result
            assert "execution_model" in result


class TestWorkflowEngineBackwardCompatibility:
    """Test WorkflowEngine backward compatibility with existing workflows."""
    
    def test_existing_workflow_sessions_continue_to_work(self, engine):
        """Test that existing workflow execution patterns still work."""
        # Standard workflow execution pattern (pre-breadcrumb)
        result = engine.start_workflow("spec_creation_v1", target_file="test.md")
        session_id = result["session_id"]
        
        # Verify workflow still works (returns expected fields)
        assert "session_id" in result
        assert "workflow_type" in result
        assert "workflow_overview" in result
        
        # Can still get phase
        phase_result = engine.get_phase(session_id, phase=0)
        assert "phase_content" in phase_result
        assert "phase_status" in phase_result
        
        # Can still get task
        task_result = engine.get_task(session_id, phase=0, task_number=1)
        assert "task_content" in task_result
        assert "phase_status" in task_result
        
        # Can still complete phase
        complete_result = engine.complete_phase(session_id, phase=0, evidence={"test": "data"})
        assert "success" in complete_result
        assert "current_phase" in complete_result
    
    def test_static_guidance_fields_always_present(self, engine):
        """Test that static workflow guidance fields are never removed."""
        result = engine.start_workflow("spec_creation_v1", target_file="test.md")
        session_id = result["session_id"]
        
        # All workflow responses should have static guidance
        responses = [
            result,  # start_workflow
            engine.get_phase(session_id, phase=0),  # get_phase
            engine.get_task(session_id, phase=0, task_number=1),  # get_task
        ]
        
        for response in responses:
            assert "⚠️_WORKFLOW_EXECUTION_MODE" in response, \
                "Static guidance field missing"
            assert "🛑_DO_NOT_USE_EXTERNAL_TASK_TOOLS" in response, \
                "Static guidance field missing"
            assert "execution_model" in response, \
                "Static guidance field missing"
    
    def test_compliant_ai_workflow_not_disrupted(self, engine):
        """Test that compliant AI workflows (that read breadcrumbs) still work."""
        # Simulate compliant AI workflow behavior
        
        # Step 1: Start workflow
        start_result = engine.start_workflow("spec_creation_v1", target_file="test.md")
        session_id = start_result["session_id"]
        
        # AI reads breadcrumb (optional for backward compat, but should work if present)
        if "⚡_NEXT_ACTION" in start_result:
            next_action = start_result["⚡_NEXT_ACTION"]
            assert "get_phase" in next_action
        
        # Step 2: Get phase
        phase_result = engine.get_phase(session_id, phase=0)
        
        # AI reads breadcrumb
        if "⚡_NEXT_ACTION" in phase_result:
            next_action = phase_result["⚡_NEXT_ACTION"]
            assert "get_task" in next_action
        
        # Step 3: Get task
        task_result = engine.get_task(session_id, phase=0, task_number=1)
        
        # AI reads breadcrumb
        if "⚡_NEXT_ACTION" in task_result:
            next_action = task_result["⚡_NEXT_ACTION"]
            # Should guide to either next task or complete_phase
            assert "get_task" in next_action or "complete_phase" in next_action
        
        # Workflow execution is not disrupted
        assert task_result["phase_status"]["is_current"]


class TestNoBreakingChanges:
    """Test that no breaking changes were introduced."""
    
    def test_response_dict_structure_preserved(self, engine):
        """Test that response dictionary keys are preserved (only additions, no removals)."""
        result = engine.start_workflow("spec_creation_v1", target_file="test.md")
        session_id = result["session_id"]
        
        # Expected core fields (must always be present)
        core_fields_start = ["session_id", "workflow_type", "current_phase", "workflow_overview"]
        core_fields_get_phase = ["session_id", "workflow_type", "phase", "current_phase", "phase_status", "phase_content"]
        core_fields_get_task = ["session_id", "workflow_type", "phase", "task_number", "current_phase", "phase_status", "task_content"]
        
        # start_workflow
        for field in core_fields_start:
            assert field in result, f"Core field '{field}' missing from start_workflow"
        
        # get_phase
        phase_result = engine.get_phase(session_id, phase=0)
        for field in core_fields_get_phase:
            assert field in phase_result, f"Core field '{field}' missing from get_phase"
        
        # get_task
        task_result = engine.get_task(session_id, phase=0, task_number=1)
        for field in core_fields_get_task:
            assert field in task_result, f"Core field '{field}' missing from get_task"
    
    def test_function_signatures_unchanged(self):
        """Test that public function signatures have not changed (breaking change check)."""
        from inspect import signature
        
        # Test add_workflow_guidance signature
        sig = signature(add_workflow_guidance)
        params = list(sig.parameters.keys())
        
        # First parameter must be 'response' (required)
        assert params[0] == "response"
        
        # Second parameter must be 'breadcrumb' (optional, default None)
        assert params[1] == "breadcrumb"
        assert sig.parameters["breadcrumb"].default is None
        
        # No other required parameters added
        required_params = [p for p in sig.parameters.values() if p.default == p.empty]
        assert len(required_params) == 1, "No additional required parameters should be added"

