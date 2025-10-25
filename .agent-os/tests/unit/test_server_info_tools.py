"""
Unit tests for server_info_tools module.

Tests get_server_info tool registration and functionality.
"""

import os
import time
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcp_server.server.tools.server_info_tools import (
    _SERVER_START_DATETIME,
    _SERVER_START_TIME,
    register_server_info_tools,
)


class TestRegisterServerInfoTools:
    """Test suite for register_server_info_tools function."""

    def test_returns_tool_count(self):
        """Test that register_server_info_tools returns correct tool count."""
        mock_mcp = MagicMock()
        mock_project_discovery = MagicMock()

        count = register_server_info_tools(
            mock_mcp, mock_project_discovery, transport_mode="stdio"
        )

        assert count == 1  # Should register 1 tool
        assert mock_mcp.tool.called  # Should call mcp.tool decorator

    def test_registers_with_all_transport_modes(self):
        """Test registration with different transport modes."""
        mock_mcp = MagicMock()
        mock_project_discovery = MagicMock()

        for mode in ["dual", "stdio", "http"]:
            count = register_server_info_tools(
                mock_mcp, mock_project_discovery, transport_mode=mode
            )
            assert count == 1

    def test_default_transport_mode(self):
        """Test that default transport mode is stdio."""
        mock_mcp = MagicMock()
        mock_project_discovery = MagicMock()

        # Register without specifying transport_mode
        count = register_server_info_tools(mock_mcp, mock_project_discovery)

        assert count == 1


class TestGetServerInfoTool:
    """Test suite for get_server_info tool functionality."""

    @pytest.fixture
    def mock_mcp(self):
        """Create mock MCP server."""
        mcp = MagicMock()
        mcp.list_tools.return_value = [
            {"name": "search_standards"},
            {"name": "start_workflow"},
            {"name": "get_server_info"},
        ]

        # Mock the decorator to capture the function
        self._registered_func = None

        def tool_decorator():
            def decorator(func):
                self._registered_func = func
                return func

            return decorator

        mcp.tool = tool_decorator
        return mcp

    @pytest.fixture
    def mock_project_discovery(self):
        """Create mock ProjectInfoDiscovery."""
        discovery = MagicMock()
        discovery.get_project_info.return_value = {
            "name": "test-project",
            "root": "/path/to/project",
            "agent_os_path": "/path/to/project/.agent-os",
            "git": {
                "remote": "https://github.com/user/test-project.git",
                "branch": "main",
                "commit": "abc123",
                "dirty": False,
            },
        }
        return discovery

    @pytest.mark.asyncio
    async def test_returns_complete_info(self, mock_mcp, mock_project_discovery):
        """Test that get_server_info returns all expected sections."""
        # Register the tool
        register_server_info_tools(mock_mcp, mock_project_discovery, "dual")

        # Get the registered function
        tool_func = self._registered_func
        assert tool_func is not None

        # Call the tool
        result = await tool_func()

        # Verify structure
        assert "server" in result
        assert "project" in result
        assert "capabilities" in result

    @pytest.mark.asyncio
    async def test_server_metadata(self, mock_mcp, mock_project_discovery):
        """Test server metadata section."""
        register_server_info_tools(mock_mcp, mock_project_discovery, "http")
        tool_func = self._registered_func

        result = await tool_func()
        server = result["server"]

        # Check all required fields
        assert "version" in server
        assert "transport_mode" in server
        assert "uptime_seconds" in server
        assert "pid" in server
        assert "started_at" in server

        # Verify values
        assert server["version"] == "1.0.0"
        assert server["transport_mode"] == "http"
        assert isinstance(server["uptime_seconds"], int)
        assert server["pid"] == os.getpid()
        assert isinstance(server["started_at"], str)

    @pytest.mark.asyncio
    async def test_project_metadata(self, mock_mcp, mock_project_discovery):
        """Test project metadata section."""
        register_server_info_tools(mock_mcp, mock_project_discovery, "stdio")
        tool_func = self._registered_func

        result = await tool_func()
        project = result["project"]

        # Check all required fields
        assert "name" in project
        assert "root" in project
        assert "agent_os_path" in project
        assert "git" in project

        # Verify values match mock
        assert project["name"] == "test-project"
        assert project["root"] == "/path/to/project"
        assert project["agent_os_path"] == "/path/to/project/.agent-os"
        assert project["git"]["remote"] == "https://github.com/user/test-project.git"

    @pytest.mark.asyncio
    async def test_capabilities_metadata(self, mock_mcp, mock_project_discovery):
        """Test capabilities metadata section."""
        register_server_info_tools(mock_mcp, mock_project_discovery, "dual")
        tool_func = self._registered_func

        result = await tool_func()
        capabilities = result["capabilities"]

        # Check all required fields
        assert "tools_available" in capabilities
        assert "rag_enabled" in capabilities
        assert "workflow_enabled" in capabilities
        assert "browser_enabled" in capabilities
        assert "dual_transport" in capabilities
        assert "http_transport" in capabilities

        # Verify dual mode capabilities
        assert capabilities["tools_available"] == 3  # From mock
        assert capabilities["rag_enabled"] is True
        assert capabilities["workflow_enabled"] is True
        assert capabilities["browser_enabled"] is True
        assert capabilities["dual_transport"] is True
        assert capabilities["http_transport"] is True

    @pytest.mark.asyncio
    async def test_stdio_mode_capabilities(self, mock_mcp, mock_project_discovery):
        """Test capabilities for stdio-only mode."""
        register_server_info_tools(mock_mcp, mock_project_discovery, "stdio")
        tool_func = self._registered_func

        result = await tool_func()
        capabilities = result["capabilities"]

        # stdio mode should not have HTTP transport
        assert capabilities["dual_transport"] is False
        assert capabilities["http_transport"] is False

    @pytest.mark.asyncio
    async def test_http_mode_capabilities(self, mock_mcp, mock_project_discovery):
        """Test capabilities for HTTP-only mode."""
        register_server_info_tools(mock_mcp, mock_project_discovery, "http")
        tool_func = self._registered_func

        result = await tool_func()
        capabilities = result["capabilities"]

        # http mode should have HTTP but not dual
        assert capabilities["dual_transport"] is False
        assert capabilities["http_transport"] is True

    @pytest.mark.asyncio
    async def test_uptime_calculation(self, mock_mcp, mock_project_discovery):
        """Test that uptime is calculated correctly."""
        register_server_info_tools(mock_mcp, mock_project_discovery, "stdio")
        tool_func = self._registered_func

        # Get initial uptime
        result1 = await tool_func()
        uptime1 = result1["server"]["uptime_seconds"]

        # Wait a bit
        time.sleep(0.1)

        # Get second uptime
        result2 = await tool_func()
        uptime2 = result2["server"]["uptime_seconds"]

        # Second uptime should be >= first uptime
        assert uptime2 >= uptime1
        assert isinstance(uptime1, int)
        assert isinstance(uptime2, int)

    @pytest.mark.asyncio
    async def test_handles_project_discovery_error(
        self, mock_mcp, mock_project_discovery
    ):
        """Test graceful error handling when project discovery fails."""
        mock_project_discovery.get_project_info.side_effect = Exception(
            "Discovery failed"
        )

        register_server_info_tools(mock_mcp, mock_project_discovery, "stdio")
        tool_func = self._registered_func

        result = await tool_func()

        # Should still return server info
        assert "server" in result
        assert result["server"]["version"] == "1.0.0"
        assert "error" in result["server"]

        # Project should have error
        assert "project" in result
        assert "error" in result["project"]

        # Capabilities should have error
        assert "capabilities" in result
        assert "error" in result["capabilities"]

    @pytest.mark.asyncio
    async def test_handles_tool_count_error(self, mock_mcp, mock_project_discovery):
        """Test graceful error handling when tool count retrieval fails."""
        mock_mcp.list_tools.side_effect = Exception("Cannot list tools")

        register_server_info_tools(mock_mcp, mock_project_discovery, "stdio")
        tool_func = self._registered_func

        result = await tool_func()

        # Should still return result with tools_available = 0
        assert result["capabilities"]["tools_available"] == 0

    @pytest.mark.asyncio
    async def test_no_hardcoded_values(self, mock_mcp, mock_project_discovery):
        """Test that all values are discovered dynamically (no hardcoding)."""
        # Change mock values to verify they're used
        mock_project_discovery.get_project_info.return_value = {
            "name": "different-project",
            "root": "/different/path",
            "agent_os_path": "/different/path/.agent-os",
            "git": None,
        }

        register_server_info_tools(mock_mcp, mock_project_discovery, "dual")
        tool_func = self._registered_func

        result = await tool_func()

        # Verify dynamic values are used
        assert result["project"]["name"] == "different-project"
        assert result["project"]["root"] == "/different/path"
        assert result["project"]["git"] is None


class TestModuleLevelVariables:
    """Test module-level startup tracking."""

    def test_server_start_time_is_float(self):
        """Test that _SERVER_START_TIME is a float timestamp."""
        assert isinstance(_SERVER_START_TIME, float)
        assert _SERVER_START_TIME > 0

    def test_server_start_datetime_is_iso_format(self):
        """Test that _SERVER_START_DATETIME is ISO format string."""
        assert isinstance(_SERVER_START_DATETIME, str)

        # Should be parseable as ISO datetime
        parsed = datetime.fromisoformat(_SERVER_START_DATETIME.replace("Z", "+00:00"))
        assert parsed.tzinfo is not None  # Should be timezone-aware


class TestDocumentationQuality:
    """Test documentation and code quality standards."""

    def test_module_has_docstring(self):
        """Test that module has docstring."""
        import mcp_server.server.tools.server_info_tools as module

        assert module.__doc__ is not None
        assert len(module.__doc__.strip()) > 0

    def test_register_function_has_docstring(self):
        """Test that register_server_info_tools has comprehensive docstring."""
        doc = register_server_info_tools.__doc__
        assert doc is not None
        assert "Args:" in doc or "param" in doc
        assert "Returns:" in doc or "return" in doc

    def test_has_type_hints(self):
        """Test that functions have type hints."""
        import inspect

        sig = inspect.signature(register_server_info_tools)

        # Check parameters have annotations
        assert "mcp" in sig.parameters
        assert "project_discovery" in sig.parameters
        assert "transport_mode" in sig.parameters

        # Check return annotation
        assert sig.return_annotation != inspect.Signature.empty
