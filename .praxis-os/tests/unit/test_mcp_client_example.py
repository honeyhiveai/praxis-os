"""
Unit tests for MCP client example.

Tests the sub-agent integration example functionality.
"""

import asyncio
import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mcp_server.sub_agents.mcp_client_example import (
    _mock_list_tools,
    _mock_search_standards,
    connect_and_use_mcp_server,
    get_mcp_config_for_aider,
    get_mcp_config_for_cline,
    get_mcp_config_for_python_sdk,
)


class TestConnectAndUseMCPServer:
    """Test suite for connect_and_use_mcp_server function."""

    @pytest.mark.asyncio
    async def test_successful_connection(self, tmp_path):
        """Test successful connection to MCP server."""
        # Create valid state file
        agent_os = tmp_path / ".praxis-os"
        agent_os.mkdir()
        state = {
            "transport": "dual",
            "url": "http://127.0.0.1:4242/mcp",
            "port": 4242,
            "pid": os.getpid(),
            "project": {"name": "test-project"},
        }
        state_file = agent_os / ".mcp_server_state.json"
        with open(state_file, "w") as f:
            json.dump(state, f)

        # Run connection
        result = await connect_and_use_mcp_server(agent_os)

        # Verify success
        assert result["success"] is True
        assert result["url"] == "http://127.0.0.1:4242/mcp"
        assert result["tools_count"] == 10
        assert "search_standards" in result["tools"]
        assert "start_workflow" in result["tools"]
        assert result["search_result"]["query"] == "production code checklist"

    @pytest.mark.asyncio
    async def test_server_not_found(self, tmp_path):
        """Test handling when server is not found."""
        # No state file created
        agent_os = tmp_path / ".praxis-os"
        agent_os.mkdir()

        result = await connect_and_use_mcp_server(agent_os)

        assert result["success"] is False
        assert "error" in result
        assert "MCP server not found" in result["error"]
        assert "Server not started" in result["error"]

    @pytest.mark.asyncio
    async def test_stale_pid(self, tmp_path):
        """Test handling of stale PID in state file."""
        # Create state file with non-existent PID
        agent_os = tmp_path / ".praxis-os"
        agent_os.mkdir()
        state = {
            "transport": "dual",
            "url": "http://127.0.0.1:4242/mcp",
            "port": 4242,
            "pid": 99999999,
            "project": {"name": "test-project"},
        }
        state_file = agent_os / ".mcp_server_state.json"
        with open(state_file, "w") as f:
            json.dump(state, f)

        with patch(
            "mcp_server.sub_agents.discovery._is_process_alive", return_value=False
        ):
            result = await connect_and_use_mcp_server(agent_os)

        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_stdio_only_mode(self, tmp_path):
        """Test handling when server is in stdio-only mode."""
        # Create state file with stdio transport
        agent_os = tmp_path / ".praxis-os"
        agent_os.mkdir()
        state = {
            "transport": "stdio",
            "url": None,
            "port": None,
            "pid": os.getpid(),
            "project": {"name": "test-project"},
        }
        state_file = agent_os / ".mcp_server_state.json"
        with open(state_file, "w") as f:
            json.dump(state, f)

        result = await connect_and_use_mcp_server(agent_os)

        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_connection_error_handling(self, tmp_path):
        """Test handling of connection errors."""
        agent_os = tmp_path / ".praxis-os"
        agent_os.mkdir()
        state = {
            "transport": "dual",
            "url": "http://127.0.0.1:4242/mcp",
            "port": 4242,
            "pid": os.getpid(),
            "project": {"name": "test-project"},
        }
        state_file = agent_os / ".mcp_server_state.json"
        with open(state_file, "w") as f:
            json.dump(state, f)

        # Mock _mock_list_tools to raise ConnectionError
        with patch(
            "mcp_server.sub_agents.mcp_client_example._mock_list_tools",
            side_effect=ConnectionError("Connection refused"),
        ):
            result = await connect_and_use_mcp_server(agent_os)

        assert result["success"] is False
        assert "error" in result
        assert "Connection failed" in result["error"]

    @pytest.mark.asyncio
    async def test_unexpected_error_handling(self, tmp_path):
        """Test handling of unexpected errors."""
        agent_os = tmp_path / ".praxis-os"
        agent_os.mkdir()
        state = {
            "transport": "dual",
            "url": "http://127.0.0.1:4242/mcp",
            "port": 4242,
            "pid": os.getpid(),
            "project": {"name": "test-project"},
        }
        state_file = agent_os / ".mcp_server_state.json"
        with open(state_file, "w") as f:
            json.dump(state, f)

        # Mock _mock_list_tools to raise unexpected error
        with patch(
            "mcp_server.sub_agents.mcp_client_example._mock_list_tools",
            side_effect=RuntimeError("Unexpected error"),
        ):
            result = await connect_and_use_mcp_server(agent_os)

        assert result["success"] is False
        assert "error" in result
        assert "Unexpected error" in result["error"]


class TestMockFunctions:
    """Test suite for mock functions."""

    @pytest.mark.asyncio
    async def test_mock_list_tools(self):
        """Test mock list_tools implementation."""
        tools = await _mock_list_tools("http://test")

        assert isinstance(tools, list)
        assert len(tools) == 10
        assert "search_standards" in tools
        assert "start_workflow" in tools
        assert "get_server_info" in tools

    @pytest.mark.asyncio
    async def test_mock_search_standards(self):
        """Test mock search_standards implementation."""
        result = await _mock_search_standards("http://test")

        assert isinstance(result, dict)
        assert "results" in result
        assert "query" in result
        assert "retrieval_method" in result
        assert len(result["results"]) > 0
        assert result["query"] == "production code checklist"


class TestConfigHelpers:
    """Test suite for configuration helper functions."""

    def test_get_mcp_config_for_cline_success(self, tmp_path):
        """Test Cline config generation with running server."""
        agent_os = tmp_path / ".praxis-os"
        agent_os.mkdir()
        state = {
            "transport": "dual",
            "url": "http://127.0.0.1:4242/mcp",
            "port": 4242,
            "pid": os.getpid(),
        }
        state_file = agent_os / ".mcp_server_state.json"
        with open(state_file, "w") as f:
            json.dump(state, f)

        with patch(
            "mcp_server.sub_agents.mcp_client_example.discover_mcp_server",
            return_value="http://127.0.0.1:4242/mcp",
        ):
            config = get_mcp_config_for_cline()

        assert config is not None
        assert "mcpServers" in config
        assert "agent-os-rag" in config["mcpServers"]
        assert (
            config["mcpServers"]["agent-os-rag"]["url"] == "http://127.0.0.1:4242/mcp"
        )
        assert config["mcpServers"]["agent-os-rag"]["transport"] == "streamable-http"

    def test_get_mcp_config_for_cline_not_found(self):
        """Test Cline config generation when server not found."""
        with patch(
            "mcp_server.sub_agents.mcp_client_example.discover_mcp_server",
            return_value=None,
        ):
            config = get_mcp_config_for_cline()

        assert config is None

    def test_get_mcp_config_for_aider_success(self):
        """Test Aider config generation with running server."""
        with patch(
            "mcp_server.sub_agents.mcp_client_example.discover_mcp_server",
            return_value="http://127.0.0.1:4242/mcp",
        ):
            config = get_mcp_config_for_aider()

        assert config is not None
        assert "url" in config
        assert config["url"] == "http://127.0.0.1:4242/mcp"
        assert config["transport"] == "http"

    def test_get_mcp_config_for_aider_not_found(self):
        """Test Aider config generation when server not found."""
        with patch(
            "mcp_server.sub_agents.mcp_client_example.discover_mcp_server",
            return_value=None,
        ):
            config = get_mcp_config_for_aider()

        assert config is None

    def test_get_mcp_config_for_python_sdk_success(self):
        """Test Python SDK config generation with running server."""
        with patch(
            "mcp_server.sub_agents.mcp_client_example.discover_mcp_server",
            return_value="http://127.0.0.1:4242/mcp",
        ):
            config = get_mcp_config_for_python_sdk()

        assert config is not None
        assert "url" in config
        assert config["url"] == "http://127.0.0.1:4242/mcp"
        assert config["transport"] == "streamable-http"

    def test_get_mcp_config_for_python_sdk_not_found(self):
        """Test Python SDK config generation when server not found."""
        with patch(
            "mcp_server.sub_agents.mcp_client_example.discover_mcp_server",
            return_value=None,
        ):
            config = get_mcp_config_for_python_sdk()

        assert config is None


class TestDocumentation:
    """Test documentation quality."""

    def test_module_has_docstring(self):
        """Test that the module has a docstring."""
        import mcp_server.sub_agents.mcp_client_example

        assert mcp_server.sub_agents.mcp_client_example.__doc__ is not None
        assert len(mcp_server.sub_agents.mcp_client_example.__doc__) > 0

    def test_connect_function_has_docstring(self):
        """Test that connect_and_use_mcp_server has comprehensive docstring."""
        assert connect_and_use_mcp_server.__doc__ is not None
        assert "Args:" in connect_and_use_mcp_server.__doc__
        assert "Returns:" in connect_and_use_mcp_server.__doc__
        assert "Example:" in connect_and_use_mcp_server.__doc__

    def test_config_helpers_have_docstrings(self):
        """Test that config helper functions have docstrings."""
        assert get_mcp_config_for_cline.__doc__ is not None
        assert get_mcp_config_for_aider.__doc__ is not None
        assert get_mcp_config_for_python_sdk.__doc__ is not None
