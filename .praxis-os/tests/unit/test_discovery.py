"""
Unit tests for sub-agent discovery utilities.

Tests the discover_mcp_server() function and its helper functions.
"""

import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mcp_server.sub_agents.discovery import (
    _find_agent_os_directory,
    _is_process_alive,
    discover_mcp_server,
)


class TestDiscoverMCPServer:
    """Test suite for discover_mcp_server() function."""

    @pytest.fixture
    def agent_os_path(self, tmp_path):
        """Create a temporary .praxis-os directory."""
        agent_os = tmp_path / ".praxis-os"
        agent_os.mkdir()
        return agent_os

    @pytest.fixture
    def valid_state_file(self, agent_os_path):
        """Create a valid state file with HTTP transport."""
        state = {
            "transport": "dual",
            "url": "http://127.0.0.1:4242/mcp",
            "port": 4242,
            "pid": os.getpid(),  # Use current process PID (always alive)
            "project": {"name": "test-project"},
            "started_at": "2023-10-27T10:00:00Z",
        }
        state_file = agent_os_path / ".mcp_server_state.json"
        with open(state_file, "w") as f:
            json.dump(state, f)
        return state_file

    def test_discover_mcp_server_success(self, agent_os_path, valid_state_file):
        """Test successful discovery of running MCP server."""
        url = discover_mcp_server(agent_os_path)
        assert url == "http://127.0.0.1:4242/mcp"

    def test_discover_mcp_server_http_mode(self, agent_os_path):
        """Test discovery with HTTP-only transport mode."""
        state = {
            "transport": "http",
            "url": "http://127.0.0.1:5000/mcp",
            "port": 5000,
            "pid": os.getpid(),
            "project": {"name": "test-project"},
        }
        state_file = agent_os_path / ".mcp_server_state.json"
        with open(state_file, "w") as f:
            json.dump(state, f)

        url = discover_mcp_server(agent_os_path)
        assert url == "http://127.0.0.1:5000/mcp"

    def test_discover_mcp_server_state_file_missing(self, agent_os_path):
        """Test discovery when state file does not exist."""
        url = discover_mcp_server(agent_os_path)
        assert url is None

    def test_discover_mcp_server_stdio_only(self, agent_os_path):
        """Test discovery returns None for stdio-only transport."""
        state = {
            "transport": "stdio",
            "url": None,
            "port": None,
            "pid": os.getpid(),
            "project": {"name": "test-project"},
        }
        state_file = agent_os_path / ".mcp_server_state.json"
        with open(state_file, "w") as f:
            json.dump(state, f)

        url = discover_mcp_server(agent_os_path)
        assert url is None

    def test_discover_mcp_server_stale_pid(self, agent_os_path):
        """Test discovery returns None for stale PID (process not running)."""
        state = {
            "transport": "dual",
            "url": "http://127.0.0.1:4242/mcp",
            "port": 4242,
            "pid": 99999999,  # Very unlikely to be a real PID
            "project": {"name": "test-project"},
        }
        state_file = agent_os_path / ".mcp_server_state.json"
        with open(state_file, "w") as f:
            json.dump(state, f)

        with patch(
            "mcp_server.sub_agents.discovery._is_process_alive", return_value=False
        ):
            url = discover_mcp_server(agent_os_path)
            assert url is None

    def test_discover_mcp_server_corrupted_json(self, agent_os_path):
        """Test discovery handles corrupted JSON gracefully."""
        state_file = agent_os_path / ".mcp_server_state.json"
        state_file.write_text("{ corrupted json")

        url = discover_mcp_server(agent_os_path)
        assert url is None

    def test_discover_mcp_server_invalid_format(self, agent_os_path):
        """Test discovery handles invalid state format (not a dict)."""
        state_file = agent_os_path / ".mcp_server_state.json"
        with open(state_file, "w") as f:
            json.dump(["not", "a", "dict"], f)

        url = discover_mcp_server(agent_os_path)
        assert url is None

    def test_discover_mcp_server_missing_required_fields(self, agent_os_path):
        """Test discovery handles missing required fields."""
        # Missing 'url' and 'pid'
        state = {
            "transport": "dual",
        }
        state_file = agent_os_path / ".mcp_server_state.json"
        with open(state_file, "w") as f:
            json.dump(state, f)

        url = discover_mcp_server(agent_os_path)
        assert url is None

    def test_discover_mcp_server_missing_transport_field(self, agent_os_path):
        """Test discovery handles missing transport field."""
        state = {
            "url": "http://127.0.0.1:4242/mcp",
            "pid": os.getpid(),
        }
        state_file = agent_os_path / ".mcp_server_state.json"
        with open(state_file, "w") as f:
            json.dump(state, f)

        url = discover_mcp_server(agent_os_path)
        assert url is None

    def test_discover_mcp_server_file_read_error(self, agent_os_path):
        """Test discovery handles file read errors gracefully."""
        state_file = agent_os_path / ".mcp_server_state.json"
        state_file.write_text('{"transport": "dual", "url": "http://test", "pid": 1}')

        # Simulate read error by removing read permissions
        state_file.chmod(0o000)

        try:
            url = discover_mcp_server(agent_os_path)
            assert url is None
        finally:
            # Restore permissions for cleanup
            state_file.chmod(0o600)

    def test_discover_mcp_server_auto_find_agent_os(self, tmp_path, monkeypatch):
        """Test discovery automatically finds .praxis-os in current directory."""
        project_dir = tmp_path / "my_project"
        project_dir.mkdir()
        agent_os = project_dir / ".praxis-os"
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

        # Change to project directory
        monkeypatch.chdir(project_dir)

        url = discover_mcp_server()  # No explicit path
        assert url == "http://127.0.0.1:4242/mcp"

    def test_discover_mcp_server_auto_find_agent_os_not_found(
        self, tmp_path, monkeypatch
    ):
        """Test discovery returns None when .praxis-os not found."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        monkeypatch.chdir(empty_dir)

        url = discover_mcp_server()  # No .praxis-os in hierarchy
        assert url is None


class TestFindAgentOsDirectory:
    """Test suite for _find_agent_os_directory() helper."""

    def test_find_in_current_directory(self, tmp_path, monkeypatch):
        """Test finding .praxis-os in current directory."""
        agent_os = tmp_path / ".praxis-os"
        agent_os.mkdir()
        monkeypatch.chdir(tmp_path)

        result = _find_agent_os_directory()
        assert result == agent_os

    def test_find_in_parent_directory(self, tmp_path, monkeypatch):
        """Test finding .praxis-os in parent directory."""
        agent_os = tmp_path / ".praxis-os"
        agent_os.mkdir()

        subdir = tmp_path / "subdir" / "nested"
        subdir.mkdir(parents=True)
        monkeypatch.chdir(subdir)

        result = _find_agent_os_directory()
        assert result == agent_os

    def test_not_found(self, tmp_path, monkeypatch):
        """Test returns None when .praxis-os not found."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        monkeypatch.chdir(empty_dir)

        result = _find_agent_os_directory()
        assert result is None

    def test_stops_at_home_directory(self, tmp_path, monkeypatch):
        """Test search stops at home directory."""
        # Create a directory structure outside of home
        test_dir = tmp_path / "outside_home" / "nested"
        test_dir.mkdir(parents=True)
        monkeypatch.chdir(test_dir)

        # Mock Path.home() to return a directory that doesn't contain .praxis-os
        mock_home = tmp_path / "fake_home"
        mock_home.mkdir()
        monkeypatch.setattr(Path, "home", lambda: mock_home)

        result = _find_agent_os_directory()
        # Should not find .praxis-os (it doesn't exist in the test hierarchy)
        assert result is None


class TestIsProcessAlive:
    """Test suite for _is_process_alive() helper."""

    def test_current_process_is_alive(self):
        """Test that current process PID returns True."""
        pid = os.getpid()
        assert _is_process_alive(pid) is True

    def test_invalid_pid_negative(self):
        """Test that negative PID returns False."""
        assert _is_process_alive(-1) is False

    def test_invalid_pid_zero(self):
        """Test that PID 0 returns False."""
        assert _is_process_alive(0) is False

    def test_invalid_pid_non_integer(self):
        """Test that non-integer PID returns False."""
        assert _is_process_alive("not_an_int") is False  # type: ignore

    def test_very_large_pid_likely_not_running(self):
        """Test that very large PID returns False (unlikely to exist)."""
        with patch("mcp_server.sub_agents.discovery.Path.exists", return_value=False):
            with patch("os.kill", side_effect=OSError):
                with patch(
                    "mcp_server.sub_agents.discovery.psutil", create=True
                ) as mock_psutil:
                    mock_psutil.pid_exists.return_value = False
                    assert _is_process_alive(99999999) is False

    def test_proc_filesystem_check(self):
        """Test PID validation via /proc filesystem."""
        pid = os.getpid()
        proc_path = Path(f"/proc/{pid}")

        # On Unix/Linux, /proc/{pid} should exist for current process
        if proc_path.exists():
            assert _is_process_alive(pid) is True

    def test_signal_check_fallback(self):
        """Test PID validation via signal 0."""
        pid = os.getpid()

        # Mock /proc to not exist, force signal check
        with patch("mcp_server.sub_agents.discovery.Path.exists", return_value=False):
            assert _is_process_alive(pid) is True

    def test_psutil_fallback(self):
        """Test PID validation via psutil."""
        pid = os.getpid()

        # Mock /proc and os.kill to fail, force psutil check
        with patch("mcp_server.sub_agents.discovery.Path.exists", return_value=False):
            with patch("os.kill", side_effect=Exception("Mock failure")):
                # Psutil should return True for current process
                try:
                    import psutil

                    assert _is_process_alive(pid) is True
                except ImportError:
                    # If psutil not installed, conservative check returns True
                    assert _is_process_alive(pid) is True

    def test_no_psutil_conservative_assumption(self):
        """Test that without psutil, function conservatively assumes alive."""
        pid = 12345

        # Mock everything to fail except the conservative fallback
        with patch("mcp_server.sub_agents.discovery.Path.exists", return_value=False):
            with patch("os.kill", side_effect=Exception("Mock failure")):
                with patch.dict("sys.modules", {"psutil": None}):
                    # Should return True (conservative assumption)
                    result = _is_process_alive(pid)
                    assert result is True


class TestDiscoveryDocumentation:
    """Test documentation quality."""

    def test_module_has_docstring(self):
        """Test that the module has a docstring."""
        import mcp_server.sub_agents.discovery

        assert mcp_server.sub_agents.discovery.__doc__ is not None
        assert len(mcp_server.sub_agents.discovery.__doc__) > 0

    def test_discover_mcp_server_has_docstring(self):
        """Test that discover_mcp_server has a comprehensive docstring."""
        assert discover_mcp_server.__doc__ is not None
        assert "Args:" in discover_mcp_server.__doc__
        assert "Returns:" in discover_mcp_server.__doc__
        assert "Example:" in discover_mcp_server.__doc__

    def test_helper_functions_have_docstrings(self):
        """Test that helper functions have docstrings."""
        assert _find_agent_os_directory.__doc__ is not None
        assert _is_process_alive.__doc__ is not None
