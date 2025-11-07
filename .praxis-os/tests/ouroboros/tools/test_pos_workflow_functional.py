"""
Functional tests for pos_workflow tool.

These tests validate the tool as AI agents use it - testing the complete
action dispatch flow, parameter handling, and integration with WorkflowEngine.

Reference: Critical interface for AI agents (identified 2025-11-05)
"""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from ouroboros.tools.pos_workflow import WorkflowTool


class TestPosWorkflowFunctional:
    """Functional tests for pos_workflow tool (end-to-end)."""
    
    @pytest.fixture
    def mock_workflow_engine(self):
        """Create mock WorkflowEngine for testing."""
        engine = Mock()
        engine.start_workflow = Mock(return_value={
            "session_id": "func-test-001",
            "workflow_type": "spec_execution_v1",
            "current_phase": 0,
            "status": "active"
        })
        # Fix: Use get_phase instead of get_current_phase
        engine.get_phase = Mock(return_value={
            "phase_number": 1,
            "phase_name": "Foundation & Utilities",
            "tasks": [{"task_number": 1, "name": "Review supporting docs"}]
        })
        engine.complete_phase = Mock(return_value={
            "phase_completed": 1,
            "next_phase": 2,
            "status": "success"
        })
        engine.get_state = Mock(return_value={
            "session_id": "func-test-001",
            "workflow_type": "spec_execution_v1",
            "current_phase": 1,
            "phases_completed": []
        })
        # Mock state helper for _handle_get_state (needs proper dict-like structure)
        engine._state_helper = Mock()
        mock_state = Mock()
        mock_state.workflow_type = "spec_execution_v1"
        mock_state.current_phase = 1
        mock_state.target_file = "test-spec"
        mock_state.metadata = {}
        mock_state.checkpoints = {}  # Empty dict, not Mock
        mock_state.phase_artifacts = {}  # Empty dict, not Mock
        mock_state.created_at = Mock()
        mock_state.created_at.isoformat = Mock(return_value="2025-01-01T00:00:00")
        mock_state.updated_at = Mock()
        mock_state.updated_at.isoformat = Mock(return_value="2025-01-01T00:00:00")
        engine._state_helper.load = Mock(return_value=mock_state)
        return engine
    
    @pytest.fixture
    def workflow_tool(self, mock_workflow_engine):
        """Create WorkflowTool instance with mock engine."""
        mock_mcp = Mock()
        return WorkflowTool(mock_mcp, mock_workflow_engine)
    
    # ========================================================================
    # CRITICAL: Start Workflow Tests
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_start_workflow_basic(self, workflow_tool, mock_workflow_engine):
        """
        Test starting a workflow with minimal parameters.
        
        This is the most common use case for AI agents.
        """
        result = await workflow_tool._handle_start(
            workflow_type="spec_execution_v1",
            target_file="rag-index-refactor"
        )
        
        # Assert: Engine called correctly
        mock_workflow_engine.start_workflow.assert_called_once_with(
            workflow_type="spec_execution_v1",
            target_file="rag-index-refactor"
        )
        
        # Assert: Result includes session info
        assert result["session_id"] == "func-test-001"
        assert result["workflow_type"] == "spec_execution_v1"
    
    @pytest.mark.asyncio
    async def test_start_workflow_with_options_dict(self, workflow_tool, mock_workflow_engine):
        """
        Test starting workflow with options as dict (normal case).
        """
        options = {"spec_path": ".praxis-os/specs/approved/rag-refactor"}
        
        result = await workflow_tool._handle_start(
            workflow_type="spec_execution_v1",
            target_file="rag-refactor",
            options=options
        )
        
        # Assert: Options unpacked to engine
        mock_workflow_engine.start_workflow.assert_called_once_with(
            workflow_type="spec_execution_v1",
            target_file="rag-refactor",
            spec_path=".praxis-os/specs/approved/rag-refactor"
        )
    
    @pytest.mark.asyncio
    async def test_start_workflow_with_options_json_string(self, workflow_tool, mock_workflow_engine):
        """
        Test starting workflow with options as JSON string (MCP serialization).
        
        CRITICAL: This is the bug Composer hit. Must work!
        """
        options_json = '{"spec_path": ".praxis-os/specs/approved/rag-refactor", "debug": true}'
        
        result = await workflow_tool._handle_start(
            workflow_type="spec_execution_v1",
            target_file="rag-refactor",
            options=options_json
        )
        
        # Assert: JSON parsed and unpacked
        mock_workflow_engine.start_workflow.assert_called_once_with(
            workflow_type="spec_execution_v1",
            target_file="rag-refactor",
            spec_path=".praxis-os/specs/approved/rag-refactor",
            debug=True
        )
    
    @pytest.mark.asyncio
    async def test_start_workflow_missing_workflow_type(self, workflow_tool):
        """Test error handling when workflow_type is missing."""
        with pytest.raises(ValueError, match="start action requires workflow_type"):
            await workflow_tool._handle_start(
                workflow_type=None,
                target_file="rag-refactor"
            )
    
    @pytest.mark.asyncio
    async def test_start_workflow_missing_target_file(self, workflow_tool):
        """Test error handling when target_file is missing."""
        with pytest.raises(ValueError, match="start action requires target_file"):
            await workflow_tool._handle_start(
                workflow_type="spec_execution_v1",
                target_file=None
            )
    
    @pytest.mark.asyncio
    async def test_start_workflow_path_traversal_prevention(self, workflow_tool):
        """Test security: path traversal prevention."""
        with pytest.raises(ValueError, match="Invalid target_file"):
            await workflow_tool._handle_start(
                workflow_type="spec_execution_v1",
                target_file="../../../etc/passwd"
            )
        
        with pytest.raises(ValueError, match="Invalid target_file"):
            await workflow_tool._handle_start(
                workflow_type="spec_execution_v1",
                target_file="/absolute/path"
            )
    
    # ========================================================================
    # CRITICAL: Get Phase Tests
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_get_phase_current(self, workflow_tool, mock_workflow_engine):
        """Test getting current phase content."""
        result = await workflow_tool._handle_get_phase(
            session_id="func-test-001"
        )
        
        # Assert: Engine called correctly (get_phase uses positional args)
        mock_workflow_engine.get_phase.assert_called_once_with(
            "func-test-001", 1  # Positional args, not keyword args
        )
        
        # Assert: Phase content returned
        assert result["phase_number"] == 1
        assert result["phase_name"] == "Foundation & Utilities"
        assert len(result["tasks"]) > 0
    
    @pytest.mark.asyncio
    async def test_get_phase_specific(self, workflow_tool, mock_workflow_engine):
        """Test getting specific phase by number."""
        result = await workflow_tool._handle_get_phase(
            session_id="func-test-001",
            phase=2
        )
        
        # Assert: Specific phase requested (positional args)
        mock_workflow_engine.get_phase.assert_called_once_with(
            "func-test-001", 2  # Positional args
        )
    
    # ========================================================================
    # CRITICAL: Complete Phase Tests
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_complete_phase_with_evidence(self, workflow_tool, mock_workflow_engine):
        """Test completing a phase with evidence."""
        evidence = {
            "files_created": 5,
            "tests_written": 12,
            "code_reviewed": True
        }
        
        result = await workflow_tool._handle_complete_phase(
            session_id="func-test-001",
            phase=1,
            evidence=evidence
        )
        
        # Assert: Engine called with evidence (positional args)
        mock_workflow_engine.complete_phase.assert_called_once_with(
            "func-test-001", 1, evidence  # Positional args: session_id, phase, evidence
        )
        
        # Assert: Completion confirmed
        assert result["phase_completed"] == 1
        assert result["next_phase"] == 2
    
    # ========================================================================
    # Session Management Tests
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_get_state(self, workflow_tool, mock_workflow_engine):
        """Test getting workflow state."""
        result = await workflow_tool._handle_get_state(
            session_id="func-test-001"
        )
        
        # Assert: State returned
        assert result["session_id"] == "func-test-001"
        assert result["workflow_type"] == "spec_execution_v1"
        assert "current_phase" in result
    
    # ========================================================================
    # Integration: Full Workflow Lifecycle
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_full_workflow_lifecycle(self, workflow_tool, mock_workflow_engine):
        """
        Test complete workflow lifecycle: start → get_phase → complete → get_state.
        
        This simulates how an AI agent actually uses the tool.
        """
        # Step 1: Start workflow
        start_result = await workflow_tool._handle_start(
            workflow_type="spec_execution_v1",
            target_file="test-spec"
        )
        session_id = start_result["session_id"]
        
        # Step 2: Get current phase
        phase_result = await workflow_tool._handle_get_phase(
            session_id=session_id
        )
        assert phase_result["phase_number"] == 1
        
        # Step 3: Complete phase
        complete_result = await workflow_tool._handle_complete_phase(
            session_id=session_id,
            phase=1,
            evidence={"completed": True}
        )
        assert complete_result["phase_completed"] == 1
        
        # Step 4: Get state
        state_result = await workflow_tool._handle_get_state(
            session_id=session_id
        )
        assert state_result["session_id"] == session_id
        
        # Assert: All actions executed in sequence
        assert mock_workflow_engine.start_workflow.called
        assert mock_workflow_engine.get_phase.called  # Fixed: get_phase not get_current_phase
        assert mock_workflow_engine.complete_phase.called
        # Note: _handle_get_state uses _state_helper.load, not engine.get_state()
        assert mock_workflow_engine._state_helper.load.called


class TestPosWorkflowEdgeCases:
    """Test edge cases and error conditions."""
    
    @pytest.fixture
    def workflow_tool(self):
        """Create WorkflowTool with mock engine."""
        mock_mcp = Mock()
        mock_engine = Mock()
        return WorkflowTool(mock_mcp, mock_engine)
    
    @pytest.mark.asyncio
    async def test_options_empty_dict(self, workflow_tool):
        """Test handling empty options dict."""
        workflow_tool.workflow_engine.start_workflow = Mock(
            return_value={"session_id": "test"}
        )
        
        result = await workflow_tool._handle_start(
            workflow_type="test",
            target_file="test",
            options={}  # Empty dict
        )
        
        # Assert: Empty dict handled gracefully
        workflow_tool.workflow_engine.start_workflow.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_options_empty_json_string(self, workflow_tool):
        """Test handling empty JSON string."""
        workflow_tool.workflow_engine.start_workflow = Mock(
            return_value={"session_id": "test"}
        )
        
        result = await workflow_tool._handle_start(
            workflow_type="test",
            target_file="test",
            options="{}"  # Empty JSON
        )
        
        # Assert: Empty JSON handled gracefully
        workflow_tool.workflow_engine.start_workflow.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_options_complex_nested_json(self, workflow_tool):
        """Test handling complex nested JSON structures."""
        workflow_tool.workflow_engine.start_workflow = Mock(
            return_value={"session_id": "test"}
        )
        
        complex_json = json.dumps({
            "spec_path": ".praxis-os/specs/approved/test",
            "config": {
                "debug": True,
                "features": ["feature1", "feature2"],
                "nested": {"level": 2, "value": "test"}
            }
        })
        
        result = await workflow_tool._handle_start(
            workflow_type="test",
            target_file="test",
            options=complex_json
        )
        
        # Assert: Complex JSON parsed correctly
        call_args = workflow_tool.workflow_engine.start_workflow.call_args[1]
        assert call_args["config"]["debug"] is True
        assert len(call_args["config"]["features"]) == 2
        assert call_args["config"]["nested"]["level"] == 2


# Mark all tests as functional
pytestmark = [pytest.mark.functional, pytest.mark.tools]

