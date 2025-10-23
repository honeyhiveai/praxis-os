"""Tests for consolidated workflow tool."""

import json
import os
from unittest.mock import Mock

import pytest


class TestWorkflowToolsModule:
    """Test module structure and imports."""

    def test_module_imports(self):
        """Verify module can be imported without errors."""
        from mcp_server.server.tools import workflow_tools

        assert workflow_tools is not None

    def test_can_import_workflow_engine(self):
        """Verify WorkflowEngine can be imported."""
        from mcp_server.workflow_engine import WorkflowEngine

        assert WorkflowEngine is not None

    def test_can_import_state_manager(self):
        """Verify StateManager can be imported."""
        from mcp_server.state_manager import StateManager

        assert StateManager is not None

    def test_no_circular_imports(self):
        """Verify no circular import errors."""
        # If we got this far, no circular imports exist
        from mcp_server.server.tools.workflow_tools import register_workflow_tools

        assert callable(register_workflow_tools)

    def test_constants_defined(self):
        """Verify VALID_ACTIONS constant is properly defined."""
        from mcp_server.server.tools.workflow_tools import VALID_ACTIONS

        assert len(VALID_ACTIONS) == 14
        assert "list_workflows" in VALID_ACTIONS
        assert "start" in VALID_ACTIONS
        assert "get_phase" in VALID_ACTIONS
        assert "get_task" in VALID_ACTIONS
        assert "complete_phase" in VALID_ACTIONS
        assert "get_state" in VALID_ACTIONS


class TestToolRegistration:
    """Test tool registration function."""

    def test_register_returns_one(self):
        """Verify registration function returns 1 (one tool registered)."""
        from mcp_server.server.tools.workflow_tools import register_workflow_tools

        # Create mock dependencies
        mock_mcp = Mock()
        mock_workflow_engine = Mock()
        mock_framework_generator = Mock()
        mock_workflow_validator = Mock()

        # Register tools
        tool_count = register_workflow_tools(
            mcp=mock_mcp,
            workflow_engine=mock_workflow_engine,
            framework_generator=mock_framework_generator,
            workflow_validator=mock_workflow_validator,
        )

        # Verify exactly 1 tool registered
        assert tool_count == 1

    def test_register_calls_mcp_tool_decorator(self):
        """Verify registration uses @mcp.tool() decorator."""
        from mcp_server.server.tools.workflow_tools import register_workflow_tools

        # Create mock MCP server
        mock_mcp = Mock()
        mock_tool_decorator = Mock(return_value=lambda f: f)
        mock_mcp.tool = Mock(return_value=mock_tool_decorator)

        mock_workflow_engine = Mock()
        mock_framework_generator = Mock()
        mock_workflow_validator = Mock()

        # Register tools
        register_workflow_tools(
            mcp=mock_mcp,
            workflow_engine=mock_workflow_engine,
            framework_generator=mock_framework_generator,
            workflow_validator=mock_workflow_validator,
        )

        # Verify @mcp.tool() was called
        mock_mcp.tool.assert_called_once()


class TestActionDispatcher:
    """Test action dispatcher logic."""

    @pytest.mark.asyncio
    async def test_unknown_action_returns_error(self):
        """Verify unknown action returns proper error response."""
        from mcp_server.server.tools.workflow_tools import register_workflow_tools

        # Create mock dependencies
        mock_mcp = Mock()
        captured_tool_func = None

        def capture_tool(func):
            nonlocal captured_tool_func
            captured_tool_func = func
            return func

        mock_mcp.tool = Mock(return_value=capture_tool)
        mock_workflow_engine = Mock()

        # Register to capture the tool function
        register_workflow_tools(
            mcp=mock_mcp,
            workflow_engine=mock_workflow_engine,
            framework_generator=Mock(),
            workflow_validator=Mock(),
        )

        # Call with unknown action
        result = await captured_tool_func(action="invalid_action")

        # Verify error response
        assert result["status"] == "error"
        assert result["action"] == "invalid_action"
        assert "Unknown action" in result["error"]
        assert "error_type" in result
        assert result["error_type"] == "ValueError"
        assert "valid_actions" in result
        assert len(result["valid_actions"]) == 14

    @pytest.mark.asyncio
    async def test_unimplemented_action_returns_error(self):
        """Verify valid but unimplemented action returns NotImplementedError."""
        from mcp_server.server.tools.workflow_tools import register_workflow_tools

        # Create mock dependencies
        mock_mcp = Mock()
        captured_tool_func = None

        def capture_tool(func):
            nonlocal captured_tool_func
            captured_tool_func = func
            return func

        mock_mcp.tool = Mock(return_value=capture_tool)
        mock_workflow_engine = Mock()

        # Register to capture the tool function
        register_workflow_tools(
            mcp=mock_mcp,
            workflow_engine=mock_workflow_engine,
            framework_generator=Mock(),
            workflow_validator=Mock(),
        )

        # Call with valid but unimplemented action (pause not yet implemented - recovery action)
        result = await captured_tool_func(action="pause")

        # Verify error response
        assert result["status"] == "error"
        assert result["action"] == "pause"
        assert "not implemented" in result["error"].lower()
        assert result["error_type"] == "NotImplementedError"

    @pytest.mark.asyncio
    async def test_action_echoed_in_response(self):
        """Verify action parameter is always echoed in response."""
        from mcp_server.server.tools.workflow_tools import register_workflow_tools

        # Create mock dependencies
        mock_mcp = Mock()
        captured_tool_func = None

        def capture_tool(func):
            nonlocal captured_tool_func
            captured_tool_func = func
            return func

        mock_mcp.tool = Mock(return_value=capture_tool)
        mock_workflow_engine = Mock()

        # Register to capture the tool function
        register_workflow_tools(
            mcp=mock_mcp,
            workflow_engine=mock_workflow_engine,
            framework_generator=Mock(),
            workflow_validator=Mock(),
        )

        # Test with various actions
        result1 = await captured_tool_func(action="invalid_action")
        assert result1["action"] == "invalid_action"

        result2 = await captured_tool_func(action="start")
        assert result2["action"] == "start"


class TestInputValidation:
    """Test input validation helper functions."""

    def test_validate_session_id_valid(self):
        """Verify valid UUID session IDs pass validation."""
        from mcp_server.server.tools.workflow_tools import validate_session_id

        # Valid UUID formats
        assert validate_session_id("550e8400-e29b-41d4-a716-446655440000")
        assert validate_session_id("123e4567-e89b-12d3-a456-426614174000")

    def test_validate_session_id_invalid_format(self):
        """Verify invalid session ID formats raise ValueError."""
        from mcp_server.server.tools.workflow_tools import validate_session_id

        # Invalid formats
        with pytest.raises(ValueError, match="Invalid session_id format"):
            validate_session_id("invalid-id")

        with pytest.raises(ValueError, match="Invalid session_id format"):
            validate_session_id("12345")

        with pytest.raises(ValueError, match="Invalid session_id format"):
            validate_session_id("UPPERCASE-550E8400-E29B-41D4-A716-446655440000")

    def test_validate_session_id_empty(self):
        """Verify empty session ID raises ValueError."""
        from mcp_server.server.tools.workflow_tools import validate_session_id

        with pytest.raises(ValueError, match="session_id is required"):
            validate_session_id("")

    def test_validate_target_file_valid(self):
        """Verify valid relative paths pass validation."""
        from mcp_server.server.tools.workflow_tools import validate_target_file

        # Valid relative paths
        assert validate_target_file("src/module.py")
        assert validate_target_file("tests/test_file.py")
        assert validate_target_file("README.md")

    def test_validate_target_file_directory_traversal(self):
        """Verify directory traversal attempts are blocked."""
        from mcp_server.server.tools.workflow_tools import validate_target_file

        # Directory traversal attempts
        with pytest.raises(ValueError, match="directory traversal"):
            validate_target_file("../../../etc/passwd")

        with pytest.raises(ValueError, match="directory traversal"):
            validate_target_file("../../secret.txt")

    def test_validate_target_file_absolute_path(self):
        """Verify absolute paths are blocked."""
        from mcp_server.server.tools.workflow_tools import validate_target_file

        with pytest.raises(ValueError, match="directory traversal"):
            validate_target_file("/etc/passwd")

        with pytest.raises(ValueError, match="directory traversal"):
            validate_target_file("/usr/bin/python")

    def test_validate_target_file_empty(self):
        """Verify empty target file raises ValueError."""
        from mcp_server.server.tools.workflow_tools import validate_target_file

        with pytest.raises(ValueError, match="target_file is required"):
            validate_target_file("")

    def test_validate_evidence_size_small(self):
        """Verify small evidence passes validation."""
        from mcp_server.server.tools.workflow_tools import validate_evidence_size

        # Small evidence
        assert validate_evidence_size({"test": "data"})
        assert validate_evidence_size({"files": ["a.py", "b.py"], "count": 2})

    def test_validate_evidence_size_empty(self):
        """Verify empty/None evidence is allowed."""
        from mcp_server.server.tools.workflow_tools import validate_evidence_size

        assert validate_evidence_size({})
        assert validate_evidence_size(None)

    def test_validate_evidence_size_too_large(self):
        """Verify oversized evidence raises ValueError."""
        from mcp_server.server.tools.workflow_tools import validate_evidence_size

        # Create evidence larger than 10MB
        large_evidence = {"data": "x" * (11 * 1024 * 1024)}

        with pytest.raises(ValueError, match="Evidence too large"):
            validate_evidence_size(large_evidence)

    def test_validate_evidence_size_non_serializable(self):
        """Verify non-JSON-serializable evidence raises ValueError."""
        from mcp_server.server.tools.workflow_tools import validate_evidence_size

        # Non-serializable object
        non_serializable = {"func": lambda x: x}

        with pytest.raises(ValueError, match="not JSON-serializable"):
            validate_evidence_size(non_serializable)


class TestListWorkflowsAction:
    """Test list_workflows action handler."""

    @pytest.mark.asyncio
    async def test_list_workflows_returns_workflows(self, tmp_path, monkeypatch):
        """Verify list_workflows returns workflow metadata."""
        from mcp_server.server.tools import workflow_tools

        # Create mock workflow directory structure
        workflows_dir = tmp_path / "workflows" / "test_workflow_v1"
        workflows_dir.mkdir(parents=True)

        metadata = {
            "workflow_type": "test_workflow_v1",
            "version": "1.0.0",
            "category": "testing",
            "description": "Test workflow",
        }

        metadata_file = workflows_dir / "metadata.json"
        metadata_file.write_text(json.dumps(metadata))

        # Mock os.path.exists to return True for our test path
        original_exists = os.path.exists

        def mock_exists(path):
            if ".agent-os/workflows/" in path:
                return str(tmp_path / "workflows") == path.replace(
                    ".agent-os/workflows/", ""
                )
            return original_exists(path)

        # Mock glob.glob to return our test metadata file
        def mock_glob(pattern):
            if "metadata.json" in pattern:
                return [str(metadata_file)]
            return []

        monkeypatch.setattr(
            "os.path.exists", lambda p: str(tmp_path / "workflows") in p
        )
        monkeypatch.setattr("glob.glob", mock_glob)
        monkeypatch.setattr(
            "builtins.open",
            lambda f, *args, **kwargs: open(metadata_file, *args, **kwargs),
        )

        # Clear cache
        from mcp_server.server.tools.workflow_tools.handlers import discovery

        discovery._workflow_metadata_cache = None

        # Call handler
        result = await workflow_tools._handle_list_workflows()

        # Verify response structure
        assert result["status"] == "success"
        assert result["action"] == "list_workflows"
        assert "workflows" in result
        assert "count" in result
        assert isinstance(result["workflows"], list)
        assert result["count"] >= 0

    @pytest.mark.asyncio
    async def test_list_workflows_with_category_filter(self):
        """Verify category filtering works."""
        import mcp_server.server.tools.workflow_tools as wf_tools
        from mcp_server.server.tools.workflow_tools import _handle_list_workflows
        from mcp_server.server.tools.workflow_tools.handlers import discovery

        # Mock cached workflows with different categories
        discovery._workflow_metadata_cache = [
            {"workflow_type": "test_gen_v3", "category": "testing"},
            {"workflow_type": "spec_creation_v1", "category": "documentation"},
            {"workflow_type": "code_review_v1", "category": "testing"},
        ]

        # Test with category filter
        result = await _handle_list_workflows(category="testing")

        assert result["status"] == "success"
        assert result["count"] == 2
        assert all(w["category"] == "testing" for w in result["workflows"])

    @pytest.mark.asyncio
    async def test_list_workflows_integration_with_dispatcher(self):
        """Verify list_workflows works through the dispatcher."""
        import mcp_server.server.tools.workflow_tools as wf_tools
        from mcp_server.server.tools.workflow_tools import register_workflow_tools
        from mcp_server.server.tools.workflow_tools.handlers import discovery

        # Set up mock cache
        discovery._workflow_metadata_cache = [
            {"workflow_type": "test1", "category": "testing"}
        ]

        # Create mock MCP and capture the tool function
        mock_mcp = Mock()
        captured_tool_func = None

        def capture_tool(func):
            nonlocal captured_tool_func
            captured_tool_func = func
            return func

        mock_mcp.tool = Mock(return_value=capture_tool)

        # Register tools
        register_workflow_tools(
            mcp=mock_mcp,
            workflow_engine=Mock(),
            framework_generator=Mock(),
            workflow_validator=Mock(),
        )

        # Call through dispatcher
        result = await captured_tool_func(action="list_workflows")

        # Verify it worked
        assert result["status"] == "success"
        assert result["action"] == "list_workflows"
        assert "workflows" in result


class TestStartAction:
    """Test start action handler."""

    @pytest.mark.asyncio
    async def test_start_success(self):
        """Verify start action creates new workflow session."""
        from mcp_server.server.tools.workflow_tools import _handle_start

        # Mock workflow engine
        mock_engine = Mock()
        mock_engine.start_workflow = Mock(
            return_value={
                "session_id": "test-session-123",
                "workflow_type": "test_generation_v3",
                "phase": 1,
                "phase_content": {"test": "data"},
            }
        )

        # Call handler
        result = await _handle_start(
            workflow_type="test_generation_v3",
            target_file="src/module.py",
            workflow_engine=mock_engine,
        )

        # Verify response
        assert result["status"] == "success"
        assert result["action"] == "start"
        assert result["session_id"] == "test-session-123"
        assert result["workflow_type"] == "test_generation_v3"

        # Verify engine was called correctly (options not passed - engine doesn't support it)
        mock_engine.start_workflow.assert_called_once_with(
            workflow_type="test_generation_v3",
            target_file="src/module.py",
        )

    @pytest.mark.asyncio
    async def test_start_missing_workflow_type(self):
        """Verify start requires workflow_type parameter."""
        from mcp_server.server.tools.workflow_tools import _handle_start

        with pytest.raises(ValueError, match="workflow_type parameter"):
            await _handle_start(
                target_file="src/module.py",
                workflow_engine=Mock(),
            )

    @pytest.mark.asyncio
    async def test_start_missing_target_file(self):
        """Verify start requires target_file parameter."""
        from mcp_server.server.tools.workflow_tools import _handle_start

        with pytest.raises(ValueError, match="target_file parameter"):
            await _handle_start(
                workflow_type="test_generation_v3",
                workflow_engine=Mock(),
            )

    @pytest.mark.asyncio
    async def test_start_invalid_target_file(self):
        """Verify start validates target_file for security."""
        from mcp_server.server.tools.workflow_tools import _handle_start

        # Directory traversal attempt
        with pytest.raises(ValueError, match="directory traversal"):
            await _handle_start(
                workflow_type="test_generation_v3",
                target_file="../../../etc/passwd",
                workflow_engine=Mock(),
            )

    @pytest.mark.asyncio
    async def test_start_with_options(self):
        """Verify start accepts options parameter (for future use, not currently passed to engine)."""
        from mcp_server.server.tools.workflow_tools import _handle_start

        mock_engine = Mock()
        mock_engine.start_workflow = Mock(
            return_value={"session_id": "test-123", "workflow_type": "test"}
        )

        options = {"test_framework": "pytest", "coverage": True}

        result = await _handle_start(
            workflow_type="test_generation_v3",
            target_file="src/module.py",
            options=options,
            workflow_engine=mock_engine,
        )

        # Verify options were NOT passed (WorkflowEngine doesn't support it yet)
        mock_engine.start_workflow.assert_called_once_with(
            workflow_type="test_generation_v3",
            target_file="src/module.py",
        )

    @pytest.mark.asyncio
    async def test_start_integration_with_dispatcher(self):
        """Verify start works through the full dispatcher."""
        from mcp_server.server.tools.workflow_tools import register_workflow_tools

        # Create mock workflow engine
        mock_engine = Mock()
        mock_engine.start_workflow = Mock(
            return_value={
                "session_id": "integration-test-123",
                "workflow_type": "test_generation_v3",
            }
        )

        # Create mock MCP and capture the tool function
        mock_mcp = Mock()
        captured_tool_func = None

        def capture_tool(func):
            nonlocal captured_tool_func
            captured_tool_func = func
            return func

        mock_mcp.tool = Mock(return_value=capture_tool)

        # Register tools
        register_workflow_tools(
            mcp=mock_mcp,
            workflow_engine=mock_engine,
            framework_generator=Mock(),
            workflow_validator=Mock(),
        )

        # Call through dispatcher
        result = await captured_tool_func(
            action="start",
            workflow_type="test_generation_v3",
            target_file="src/test.py",
        )

        # Verify it worked
        assert result["status"] == "success"
        assert result["action"] == "start"
        assert "session_id" in result
        mock_engine.start_workflow.assert_called_once()


class TestGetPhaseAction:
    """Test get_phase action handler."""

    @pytest.mark.asyncio
    async def test_get_phase_success(self):
        """Verify get_phase returns current phase content."""
        from mcp_server.server.tools.workflow_tools import _handle_get_phase

        # Mock workflow engine
        mock_engine = Mock()
        mock_engine.get_current_phase = Mock(
            return_value={
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "current_phase": 2,
                "phase_name": "Implementation",
                "phase_content": {"tasks": [], "requirements": "..."},
            }
        )

        # Call handler
        result = await _handle_get_phase(
            session_id="550e8400-e29b-41d4-a716-446655440000",
            workflow_engine=mock_engine,
        )

        # Verify response
        assert result["status"] == "success"
        assert result["action"] == "get_phase"
        assert result["current_phase"] == 2
        assert result["phase_name"] == "Implementation"

        # Verify engine was called correctly
        mock_engine.get_current_phase.assert_called_once_with(
            session_id="550e8400-e29b-41d4-a716-446655440000"
        )

    @pytest.mark.asyncio
    async def test_get_phase_missing_session_id(self):
        """Verify get_phase requires session_id parameter."""
        from mcp_server.server.tools.workflow_tools import _handle_get_phase

        with pytest.raises(ValueError, match="session_id parameter"):
            await _handle_get_phase(workflow_engine=Mock())

    @pytest.mark.asyncio
    async def test_get_phase_invalid_session_id(self):
        """Verify get_phase validates session_id format."""
        from mcp_server.server.tools.workflow_tools import _handle_get_phase

        # Invalid session ID format
        with pytest.raises(ValueError, match="Invalid session_id format"):
            await _handle_get_phase(
                session_id="not-a-valid-uuid",
                workflow_engine=Mock(),
            )

    @pytest.mark.asyncio
    async def test_get_phase_integration_with_dispatcher(self):
        """Verify get_phase works through the full dispatcher."""
        from mcp_server.server.tools.workflow_tools import register_workflow_tools

        # Create mock workflow engine
        mock_engine = Mock()
        mock_engine.get_current_phase = Mock(
            return_value={
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "current_phase": 1,
                "phase_name": "Setup",
            }
        )

        # Create mock MCP and capture the tool function
        mock_mcp = Mock()
        captured_tool_func = None

        def capture_tool(func):
            nonlocal captured_tool_func
            captured_tool_func = func
            return func

        mock_mcp.tool = Mock(return_value=capture_tool)

        # Register tools
        register_workflow_tools(
            mcp=mock_mcp,
            workflow_engine=mock_engine,
            framework_generator=Mock(),
            workflow_validator=Mock(),
        )

        # Call through dispatcher
        result = await captured_tool_func(
            action="get_phase",
            session_id="550e8400-e29b-41d4-a716-446655440000",
        )

        # Verify it worked
        assert result["status"] == "success"
        assert result["action"] == "get_phase"
        assert "current_phase" in result
        mock_engine.get_current_phase.assert_called_once()


class TestGetTaskAction:
    """Test get_task action handler."""

    @pytest.mark.asyncio
    async def test_get_task_success(self):
        """Verify get_task returns specific task content."""
        from mcp_server.server.tools.workflow_tools import _handle_get_task

        # Mock workflow engine
        mock_engine = Mock()
        mock_engine.get_task = Mock(
            return_value={
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "phase": 1,
                "task_number": 2,
                "task_content": "# Task 1.2\n\nImplement feature...",
                "task_metadata": {"estimated_time": "2 hours"},
            }
        )

        # Call handler
        result = await _handle_get_task(
            session_id="550e8400-e29b-41d4-a716-446655440000",
            phase=1,
            task_number=2,
            workflow_engine=mock_engine,
        )

        # Verify response
        assert result["status"] == "success"
        assert result["action"] == "get_task"
        assert result["phase"] == 1
        assert result["task_number"] == 2
        assert "task_content" in result

        # Verify engine was called correctly
        mock_engine.get_task.assert_called_once_with(
            session_id="550e8400-e29b-41d4-a716-446655440000",
            phase=1,
            task_number=2,
        )

    @pytest.mark.asyncio
    async def test_get_task_missing_session_id(self):
        """Verify get_task requires session_id parameter."""
        from mcp_server.server.tools.workflow_tools import _handle_get_task

        with pytest.raises(ValueError, match="session_id parameter"):
            await _handle_get_task(phase=1, task_number=1, workflow_engine=Mock())

    @pytest.mark.asyncio
    async def test_get_task_missing_phase(self):
        """Verify get_task requires phase parameter."""
        from mcp_server.server.tools.workflow_tools import _handle_get_task

        with pytest.raises(ValueError, match="phase parameter"):
            await _handle_get_task(
                session_id="550e8400-e29b-41d4-a716-446655440000",
                task_number=1,
                workflow_engine=Mock(),
            )

    @pytest.mark.asyncio
    async def test_get_task_missing_task_number(self):
        """Verify get_task requires task_number parameter."""
        from mcp_server.server.tools.workflow_tools import _handle_get_task

        with pytest.raises(ValueError, match="task_number parameter"):
            await _handle_get_task(
                session_id="550e8400-e29b-41d4-a716-446655440000",
                phase=1,
                workflow_engine=Mock(),
            )

    @pytest.mark.asyncio
    async def test_get_task_invalid_phase(self):
        """Verify get_task validates phase is non-negative integer."""
        from mcp_server.server.tools.workflow_tools import _handle_get_task

        # Negative phase
        with pytest.raises(ValueError, match="non-negative integer"):
            await _handle_get_task(
                session_id="550e8400-e29b-41d4-a716-446655440000",
                phase=-1,
                task_number=1,
                workflow_engine=Mock(),
            )

    @pytest.mark.asyncio
    async def test_get_task_invalid_task_number(self):
        """Verify get_task validates task_number is positive integer."""
        from mcp_server.server.tools.workflow_tools import _handle_get_task

        # Zero task number
        with pytest.raises(ValueError, match="positive integer"):
            await _handle_get_task(
                session_id="550e8400-e29b-41d4-a716-446655440000",
                phase=1,
                task_number=0,
                workflow_engine=Mock(),
            )

    @pytest.mark.asyncio
    async def test_get_task_integration_with_dispatcher(self):
        """Verify get_task works through the full dispatcher."""
        from mcp_server.server.tools.workflow_tools import register_workflow_tools

        # Create mock workflow engine
        mock_engine = Mock()
        mock_engine.get_task = Mock(
            return_value={
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "phase": 2,
                "task_number": 3,
                "task_content": "# Task content here",
            }
        )

        # Create mock MCP and capture the tool function
        mock_mcp = Mock()
        captured_tool_func = None

        def capture_tool(func):
            nonlocal captured_tool_func
            captured_tool_func = func
            return func

        mock_mcp.tool = Mock(return_value=capture_tool)

        # Register tools
        register_workflow_tools(
            mcp=mock_mcp,
            workflow_engine=mock_engine,
            framework_generator=Mock(),
            workflow_validator=Mock(),
        )

        # Call through dispatcher
        result = await captured_tool_func(
            action="get_task",
            session_id="550e8400-e29b-41d4-a716-446655440000",
            phase=2,
            task_number=3,
        )

        # Verify it worked
        assert result["status"] == "success"
        assert result["action"] == "get_task"
        assert result["phase"] == 2
        assert result["task_number"] == 3
        mock_engine.get_task.assert_called_once()


class TestCompletePhaseAction:
    """Test complete_phase action handler."""

    @pytest.mark.asyncio
    async def test_complete_phase_success(self):
        """Verify complete_phase validates evidence and advances phase."""
        from mcp_server.server.tools.workflow_tools import _handle_complete_phase

        # Mock workflow engine
        mock_engine = Mock()
        mock_engine.complete_phase = Mock(
            return_value={
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "checkpoint_passed": True,
                "phase_completed": 1,
                "next_phase": 2,
                "next_phase_content": {"phase_name": "Phase 2"},
            }
        )

        evidence = {"tests_passing": 42, "coverage": 85.5, "files_modified": ["a.py"]}

        # Call handler
        result = await _handle_complete_phase(
            session_id="550e8400-e29b-41d4-a716-446655440000",
            phase=1,
            evidence=evidence,
            workflow_engine=mock_engine,
        )

        # Verify response
        assert result["status"] == "success"
        assert result["action"] == "complete_phase"
        assert result["checkpoint_passed"] is True
        assert result["next_phase"] == 2

        # Verify engine was called correctly
        mock_engine.complete_phase.assert_called_once_with(
            session_id="550e8400-e29b-41d4-a716-446655440000",
            phase=1,
            evidence=evidence,
        )

    @pytest.mark.asyncio
    async def test_complete_phase_missing_session_id(self):
        """Verify complete_phase requires session_id parameter."""
        from mcp_server.server.tools.workflow_tools import _handle_complete_phase

        with pytest.raises(ValueError, match="session_id parameter"):
            await _handle_complete_phase(
                phase=1, evidence={"test": "data"}, workflow_engine=Mock()
            )

    @pytest.mark.asyncio
    async def test_complete_phase_missing_phase(self):
        """Verify complete_phase requires phase parameter."""
        from mcp_server.server.tools.workflow_tools import _handle_complete_phase

        with pytest.raises(ValueError, match="phase parameter"):
            await _handle_complete_phase(
                session_id="550e8400-e29b-41d4-a716-446655440000",
                evidence={"test": "data"},
                workflow_engine=Mock(),
            )

    @pytest.mark.asyncio
    async def test_complete_phase_missing_evidence(self):
        """Verify complete_phase requires evidence parameter."""
        from mcp_server.server.tools.workflow_tools import _handle_complete_phase

        with pytest.raises(ValueError, match="evidence parameter"):
            await _handle_complete_phase(
                session_id="550e8400-e29b-41d4-a716-446655440000",
                phase=1,
                workflow_engine=Mock(),
            )

    @pytest.mark.asyncio
    async def test_complete_phase_invalid_phase(self):
        """Verify complete_phase validates phase is non-negative integer."""
        from mcp_server.server.tools.workflow_tools import _handle_complete_phase

        with pytest.raises(ValueError, match="non-negative integer"):
            await _handle_complete_phase(
                session_id="550e8400-e29b-41d4-a716-446655440000",
                phase=-1,
                evidence={"test": "data"},
                workflow_engine=Mock(),
            )

    @pytest.mark.asyncio
    async def test_complete_phase_invalid_evidence_type(self):
        """Verify complete_phase validates evidence is a dictionary."""
        from mcp_server.server.tools.workflow_tools import _handle_complete_phase

        # Evidence is not a dict
        with pytest.raises(ValueError, match="evidence must be a dictionary"):
            await _handle_complete_phase(
                session_id="550e8400-e29b-41d4-a716-446655440000",
                phase=1,
                evidence="not-a-dict",
                workflow_engine=Mock(),
            )

    @pytest.mark.asyncio
    async def test_complete_phase_evidence_too_large(self):
        """Verify complete_phase validates evidence size."""
        from mcp_server.server.tools.workflow_tools import _handle_complete_phase

        # Create oversized evidence (>10MB)
        large_evidence = {"data": "x" * (11 * 1024 * 1024)}

        with pytest.raises(ValueError, match="Evidence too large"):
            await _handle_complete_phase(
                session_id="550e8400-e29b-41d4-a716-446655440000",
                phase=1,
                evidence=large_evidence,
                workflow_engine=Mock(),
            )

    @pytest.mark.asyncio
    async def test_complete_phase_integration_with_dispatcher(self):
        """Verify complete_phase works through the full dispatcher."""
        from mcp_server.server.tools.workflow_tools import register_workflow_tools

        # Create mock workflow engine
        mock_engine = Mock()
        mock_engine.complete_phase = Mock(
            return_value={
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "checkpoint_passed": True,
                "phase_completed": 1,
                "next_phase": 2,
            }
        )

        # Create mock MCP and capture the tool function
        mock_mcp = Mock()
        captured_tool_func = None

        def capture_tool(func):
            nonlocal captured_tool_func
            captured_tool_func = func
            return func

        mock_mcp.tool = Mock(return_value=capture_tool)

        # Register tools
        register_workflow_tools(
            mcp=mock_mcp,
            workflow_engine=mock_engine,
            framework_generator=Mock(),
            workflow_validator=Mock(),
        )

        # Call through dispatcher
        result = await captured_tool_func(
            action="complete_phase",
            session_id="550e8400-e29b-41d4-a716-446655440000",
            phase=1,
            evidence={"tests": 10, "coverage": 80},
        )

        # Verify it worked
        assert result["status"] == "success"
        assert result["action"] == "complete_phase"
        assert result["checkpoint_passed"] is True
        mock_engine.complete_phase.assert_called_once()


class TestGetStateAction:
    """Test get_state action handler."""

    @pytest.mark.asyncio
    async def test_get_state_success(self):
        """Verify get_state returns complete workflow state."""
        from mcp_server.server.tools.workflow_tools import _handle_get_state

        # Mock workflow engine
        mock_engine = Mock()
        mock_engine.get_workflow_state = Mock(
            return_value={
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "workflow_type": "test_generation_v3",
                "current_phase": 2,
                "phases_completed": [0, 1],
                "workflow_state": {
                    "progress": "50%",
                    "artifacts": ["test_file.py"],
                },
            }
        )

        # Call handler
        result = await _handle_get_state(
            session_id="550e8400-e29b-41d4-a716-446655440000",
            workflow_engine=mock_engine,
        )

        # Verify response
        assert result["status"] == "success"
        assert result["action"] == "get_state"
        assert "workflow_state" in result
        # Data is now nested under workflow_state key
        assert result["workflow_state"]["current_phase"] == 2
        assert result["workflow_state"]["workflow_type"] == "test_generation_v3"

        # Verify engine was called correctly
        mock_engine.get_workflow_state.assert_called_once_with(
            session_id="550e8400-e29b-41d4-a716-446655440000"
        )

    @pytest.mark.asyncio
    async def test_get_state_missing_session_id(self):
        """Verify get_state requires session_id parameter."""
        from mcp_server.server.tools.workflow_tools import _handle_get_state

        with pytest.raises(ValueError, match="session_id parameter"):
            await _handle_get_state(workflow_engine=Mock())

    @pytest.mark.asyncio
    async def test_get_state_invalid_session_id(self):
        """Verify get_state validates session_id format."""
        from mcp_server.server.tools.workflow_tools import _handle_get_state

        # Invalid session ID format
        with pytest.raises(ValueError, match="Invalid session_id format"):
            await _handle_get_state(
                session_id="not-a-valid-uuid",
                workflow_engine=Mock(),
            )

    @pytest.mark.asyncio
    async def test_get_state_integration_with_dispatcher(self):
        """Verify get_state works through the full dispatcher."""
        from mcp_server.server.tools.workflow_tools import register_workflow_tools

        # Create mock workflow engine
        mock_engine = Mock()
        mock_engine.get_workflow_state = Mock(
            return_value={
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "workflow_type": "test_generation_v3",
                "current_phase": 3,
            }
        )

        # Create mock MCP and capture the tool function
        mock_mcp = Mock()
        captured_tool_func = None

        def capture_tool(func):
            nonlocal captured_tool_func
            captured_tool_func = func
            return func

        mock_mcp.tool = Mock(return_value=capture_tool)

        # Register tools
        register_workflow_tools(
            mcp=mock_mcp,
            workflow_engine=mock_engine,
            framework_generator=Mock(),
            workflow_validator=Mock(),
        )

        # Call through dispatcher
        result = await captured_tool_func(
            action="get_state",
            session_id="550e8400-e29b-41d4-a716-446655440000",
        )

        # Verify it worked
        assert result["status"] == "success"
        assert result["action"] == "get_state"
        assert "workflow_state" in result
        # Data is now nested under workflow_state key
        assert result["workflow_state"]["current_phase"] == 3
        mock_engine.get_workflow_state.assert_called_once()


class TestListSessionsAction:
    """Test list_sessions action handler."""

    @pytest.mark.asyncio
    async def test_list_sessions_success(self):
        """Verify list_sessions returns all sessions."""
        from mcp_server.server.tools.workflow_tools import _handle_list_sessions

        # Mock workflow engine with state manager
        mock_state_manager = Mock()
        mock_state_manager.list_sessions = Mock(
            return_value=[
                {
                    "session_id": "session-1",
                    "status": "active",
                    "workflow_type": "test_gen",
                },
                {
                    "session_id": "session-2",
                    "status": "paused",
                    "workflow_type": "spec_creation",
                },
            ]
        )

        mock_engine = Mock()
        mock_engine.state_manager = mock_state_manager

        # Call handler
        result = await _handle_list_sessions(workflow_engine=mock_engine)

        # Verify response
        assert result["status"] == "success"
        assert result["action"] == "list_sessions"
        assert result["count"] == 2
        assert len(result["sessions"]) == 2

        # Verify state manager was called (with active_only parameter, not status)
        mock_state_manager.list_sessions.assert_called_once_with(active_only=False)

    @pytest.mark.asyncio
    async def test_list_sessions_with_status_filter(self):
        """Verify list_sessions filters by status."""
        from mcp_server.server.tools.workflow_tools import _handle_list_sessions

        # Mock workflow engine with state manager
        mock_state_manager = Mock()
        mock_state_manager.list_sessions = Mock(
            return_value=[
                {
                    "session_id": "session-1",
                    "status": "active",
                    "workflow_type": "test_gen",
                },
            ]
        )

        mock_engine = Mock()
        mock_engine.state_manager = mock_state_manager

        # Call handler with status filter
        result = await _handle_list_sessions(
            status="active", workflow_engine=mock_engine
        )

        # Verify response
        assert result["status"] == "success"
        assert result["count"] == 1

        # Verify state manager was called with filter (active_only=True, not status)
        mock_state_manager.list_sessions.assert_called_once_with(active_only=True)

    @pytest.mark.asyncio
    async def test_list_sessions_invalid_status(self):
        """Verify list_sessions validates status filter."""
        from mcp_server.server.tools.workflow_tools import _handle_list_sessions

        mock_engine = Mock()
        mock_engine.state_manager = Mock()

        # Invalid status
        with pytest.raises(ValueError, match="Invalid status filter"):
            await _handle_list_sessions(
                status="invalid-status", workflow_engine=mock_engine
            )

    @pytest.mark.asyncio
    async def test_list_sessions_integration_with_dispatcher(self):
        """Verify list_sessions works through the full dispatcher."""
        from mcp_server.server.tools.workflow_tools import register_workflow_tools

        # Create mock workflow engine with state manager
        mock_state_manager = Mock()
        mock_state_manager.list_sessions = Mock(
            return_value=[
                {"session_id": "test-session", "status": "active"},
            ]
        )

        mock_engine = Mock()
        mock_engine.state_manager = mock_state_manager

        # Create mock MCP and capture the tool function
        mock_mcp = Mock()
        captured_tool_func = None

        def capture_tool(func):
            nonlocal captured_tool_func
            captured_tool_func = func
            return func

        mock_mcp.tool = Mock(return_value=capture_tool)

        # Register tools
        register_workflow_tools(
            mcp=mock_mcp,
            workflow_engine=mock_engine,
            framework_generator=Mock(),
            workflow_validator=Mock(),
        )

        # Call through dispatcher
        result = await captured_tool_func(action="list_sessions")

        # Verify it worked
        assert result["status"] == "success"
        assert result["action"] == "list_sessions"
        assert "sessions" in result
        mock_state_manager.list_sessions.assert_called_once()


class TestGetSessionAction:
    """Test get_session action handler."""

    @pytest.mark.asyncio
    async def test_get_session_success(self):
        """Verify get_session returns session details."""
        from mcp_server.server.tools.workflow_tools import _handle_get_session

        # Mock workflow engine with state manager
        mock_state_manager = Mock()
        # Handler calls load_state, not get_session
        mock_state_manager.load_state = Mock(
            return_value={
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "workflow_type": "test_generation_v3",
                "status": "active",
                "current_phase": 2,
                "created_at": "2025-10-23T10:00:00Z",
                "session_info": {"target_file": "test.py"},
            }
        )

        mock_engine = Mock()
        mock_engine.state_manager = mock_state_manager

        # Call handler
        result = await _handle_get_session(
            session_id="550e8400-e29b-41d4-a716-446655440000",
            workflow_engine=mock_engine,
        )

        # Verify response
        assert result["status"] == "success"
        assert result["action"] == "get_session"
        assert result["workflow_type"] == "test_generation_v3"
        assert result["current_phase"] == 2
        # Status renamed to session_status to avoid collision
        assert result["session_status"] == "active"

        # Verify state manager was called correctly (load_state, not get_session)
        mock_state_manager.load_state.assert_called_once_with(
            session_id="550e8400-e29b-41d4-a716-446655440000"
        )

    @pytest.mark.asyncio
    async def test_get_session_missing_session_id(self):
        """Verify get_session requires session_id parameter."""
        from mcp_server.server.tools.workflow_tools import _handle_get_session

        with pytest.raises(ValueError, match="session_id parameter"):
            await _handle_get_session(workflow_engine=Mock())

    @pytest.mark.asyncio
    async def test_get_session_invalid_session_id(self):
        """Verify get_session validates session_id format."""
        from mcp_server.server.tools.workflow_tools import _handle_get_session

        # Invalid session ID format
        with pytest.raises(ValueError, match="Invalid session_id format"):
            await _handle_get_session(
                session_id="not-a-valid-uuid",
                workflow_engine=Mock(),
            )

    @pytest.mark.asyncio
    async def test_get_session_integration_with_dispatcher(self):
        """Verify get_session works through the full dispatcher."""
        from mcp_server.server.tools.workflow_tools import register_workflow_tools

        # Create mock workflow engine with state manager
        mock_state_manager = Mock()
        # Handler calls load_state, not get_session
        mock_state_manager.load_state = Mock(
            return_value={
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "workflow_type": "spec_creation_v1",
                "status": "active",
            }
        )

        mock_engine = Mock()
        mock_engine.state_manager = mock_state_manager

        # Create mock MCP and capture the tool function
        mock_mcp = Mock()
        captured_tool_func = None

        def capture_tool(func):
            nonlocal captured_tool_func
            captured_tool_func = func
            return func

        mock_mcp.tool = Mock(return_value=capture_tool)

        # Register tools
        register_workflow_tools(
            mcp=mock_mcp,
            workflow_engine=mock_engine,
            framework_generator=Mock(),
            workflow_validator=Mock(),
        )

        # Call through dispatcher
        result = await captured_tool_func(
            action="get_session",
            session_id="550e8400-e29b-41d4-a716-446655440000",
        )

        # Verify it worked
        assert result["status"] == "success"
        assert result["action"] == "get_session"
        assert result["workflow_type"] == "spec_creation_v1"
        # Status renamed to session_status
        assert result["session_status"] == "active"
        mock_state_manager.load_state.assert_called_once()


class TestDeleteSessionAction:
    """Test delete_session action handler."""

    @pytest.mark.asyncio
    async def test_delete_session_success(self):
        """Verify delete_session deletes a session."""
        from mcp_server.server.tools.workflow_tools import _handle_delete_session

        # Mock workflow engine with state manager
        mock_state_manager = Mock()
        mock_state_manager.delete_session = Mock()

        mock_engine = Mock()
        mock_engine.state_manager = mock_state_manager

        # Call handler
        result = await _handle_delete_session(
            session_id="550e8400-e29b-41d4-a716-446655440000",
            workflow_engine=mock_engine,
        )

        # Verify response
        assert result["status"] == "success"
        assert result["action"] == "delete_session"
        assert result["session_id"] == "550e8400-e29b-41d4-a716-446655440000"
        assert result["deleted"] is True

        # Verify state manager was called correctly
        mock_state_manager.delete_session.assert_called_once_with(
            session_id="550e8400-e29b-41d4-a716-446655440000"
        )

    @pytest.mark.asyncio
    async def test_delete_session_missing_session_id(self):
        """Verify delete_session requires session_id parameter."""
        from mcp_server.server.tools.workflow_tools import _handle_delete_session

        with pytest.raises(ValueError, match="session_id parameter"):
            await _handle_delete_session(workflow_engine=Mock())

    @pytest.mark.asyncio
    async def test_delete_session_invalid_session_id(self):
        """Verify delete_session validates session_id format."""
        from mcp_server.server.tools.workflow_tools import _handle_delete_session

        # Invalid session ID format
        with pytest.raises(ValueError, match="Invalid session_id format"):
            await _handle_delete_session(
                session_id="not-a-valid-uuid",
                workflow_engine=Mock(),
            )

    @pytest.mark.asyncio
    async def test_delete_session_integration_with_dispatcher(self):
        """Verify delete_session works through the full dispatcher."""
        from mcp_server.server.tools.workflow_tools import register_workflow_tools

        # Create mock workflow engine with state manager
        mock_state_manager = Mock()
        mock_state_manager.delete_session = Mock()

        mock_engine = Mock()
        mock_engine.state_manager = mock_state_manager

        # Create mock MCP and capture the tool function
        mock_mcp = Mock()
        captured_tool_func = None

        def capture_tool(func):
            nonlocal captured_tool_func
            captured_tool_func = func
            return func

        mock_mcp.tool = Mock(return_value=capture_tool)

        # Register tools
        register_workflow_tools(
            mcp=mock_mcp,
            workflow_engine=mock_engine,
            framework_generator=Mock(),
            workflow_validator=Mock(),
        )

        # Call through dispatcher
        result = await captured_tool_func(
            action="delete_session",
            session_id="550e8400-e29b-41d4-a716-446655440000",
        )

        # Verify it worked
        assert result["status"] == "success"
        assert result["action"] == "delete_session"
        assert result["deleted"] is True
        mock_state_manager.delete_session.assert_called_once()
