"""
Unit tests for PortManager.

Tests port allocation, state file management, and error handling.
"""

import json
import os
import socket
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from mcp_server.port_manager import PortManager


@pytest.fixture
def mock_project_discovery():
    """Mock ProjectInfoDiscovery for testing."""
    discovery = MagicMock()
    discovery.get_project_info.return_value = {
        "name": "test-project",
        "root": "/path/to/project",
        "praxis_os_path": "/path/to/project/.praxis-os",
        "git": None,
    }
    return discovery


@pytest.fixture
def port_manager(tmp_path, mock_project_discovery):
    """Create PortManager instance with temp directory."""
    return PortManager(tmp_path, mock_project_discovery)


class TestPortAllocation:
    """Test port allocation functionality."""

    def test_find_available_port_prefers_first_port(self, port_manager, monkeypatch):
        """Test that find_available_port tries preferred port first."""

        # Mock all ports as available
        def mock_is_available(port):
            return True

        monkeypatch.setattr(port_manager, "_is_port_available", mock_is_available)

        port = port_manager.find_available_port(preferred_port=4242)
        assert port == 4242

    def test_find_available_port_increments_if_taken(self, port_manager, monkeypatch):
        """Test that port allocation increments if port is taken."""
        # Mock: first 3 ports taken, 4th available
        call_count = 0

        def mock_is_available(port):
            nonlocal call_count
            call_count += 1
            return call_count > 3

        monkeypatch.setattr(port_manager, "_is_port_available", mock_is_available)

        port = port_manager.find_available_port(preferred_port=4242)
        assert port == 4245  # 4242 + 3

    def test_find_available_port_raises_on_exhaustion(self, port_manager, monkeypatch):
        """Test that RuntimeError raised if range exhausted."""
        # Mock all ports as unavailable
        monkeypatch.setattr(port_manager, "_is_port_available", lambda port: False)

        with pytest.raises(RuntimeError) as exc_info:
            port_manager.find_available_port(preferred_port=5240)

        assert "No available ports" in str(exc_info.value)
        assert "5240-5242" in str(exc_info.value)
        assert "Close some" in str(exc_info.value)

    def test_is_port_available_detects_free_port(self, port_manager):
        """Test _is_port_available returns True for free port."""
        # Find an actually available port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", 0))
            free_port = sock.getsockname()[1]

        assert port_manager._is_port_available(free_port) is True

    def test_is_port_available_detects_used_port(self, port_manager):
        """Test _is_port_available returns False for used port."""
        # Bind a port to make it unavailable
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", 0))
            used_port = sock.getsockname()[1]

            # Port should be unavailable while socket is bound
            assert port_manager._is_port_available(used_port) is False


class TestStateFileOperations:
    """Test state file write, read, and cleanup."""

    def test_write_state_creates_file(self, port_manager, tmp_path):
        """Test write_state creates file with correct content."""
        port_manager.write_state(
            transport="dual", port=4242, host="127.0.0.1", path="/mcp"
        )

        state_file = tmp_path / ".mcp_server_state.json"
        assert state_file.exists()

    def test_write_state_has_correct_fields(
        self, port_manager, tmp_path, mock_project_discovery
    ):
        """Test write_state includes all required fields."""
        port_manager.write_state(
            transport="dual", port=4242, host="127.0.0.1", path="/mcp"
        )

        state_file = tmp_path / ".mcp_server_state.json"
        state = json.loads(state_file.read_text())

        # Check required fields
        assert state["version"] == "1.0.0"
        assert state["transport"] == "dual"
        assert state["port"] == 4242
        assert state["host"] == "127.0.0.1"
        assert state["path"] == "/mcp"
        assert state["url"] == "http://127.0.0.1:4242/mcp"
        assert state["pid"] == os.getpid()
        assert "started_at" in state
        assert state["project"]["name"] == "test-project"
        assert state["project"]["root"] == "/path/to/project"

    def test_write_state_stdio_only_null_url(self, port_manager, tmp_path):
        """Test write_state sets url to None for stdio-only."""
        port_manager.write_state(transport="stdio", port=None)

        state_file = tmp_path / ".mcp_server_state.json"
        state = json.loads(state_file.read_text())

        assert state["transport"] == "stdio"
        assert state["port"] is None
        assert state["url"] is None

    def test_write_state_sets_permissions(self, port_manager, tmp_path):
        """Test write_state sets 0o600 permissions."""
        port_manager.write_state(transport="dual", port=4242)

        state_file = tmp_path / ".mcp_server_state.json"
        # Get file permissions (last 3 octal digits)
        perms = oct(state_file.stat().st_mode)[-3:]

        assert perms == "600"

    def test_write_state_atomic_write(self, port_manager, tmp_path):
        """Test write_state uses temp file + rename pattern."""
        # Write state
        port_manager.write_state(transport="dual", port=4242)

        # Verify final file exists (atomic write succeeded)
        state_file = tmp_path / ".mcp_server_state.json"
        assert state_file.exists()

        # Verify no temp file left behind (rename completed)
        temp_file = tmp_path / ".mcp_server_state.tmp"
        assert not temp_file.exists()

    def test_read_state_returns_dict_for_valid_file(self, port_manager, tmp_path):
        """Test read_state returns dict for valid state file."""
        # Write state first
        port_manager.write_state(transport="dual", port=4242)

        # Read it back
        state = PortManager.read_state(tmp_path)

        assert isinstance(state, dict)
        assert state["port"] == 4242
        assert state["transport"] == "dual"

    def test_read_state_returns_none_for_missing_file(self, tmp_path):
        """Test read_state returns None if file doesn't exist."""
        state = PortManager.read_state(tmp_path)
        assert state is None

    def test_read_state_returns_none_for_corrupted_json(self, tmp_path):
        """Test read_state returns None for corrupted JSON."""
        # Write invalid JSON
        state_file = tmp_path / ".mcp_server_state.json"
        state_file.write_text("{invalid json}")

        state = PortManager.read_state(tmp_path)
        assert state is None

    def test_read_state_returns_none_for_unreadable_file(self, tmp_path, monkeypatch):
        """Test read_state returns None for unreadable file."""
        # Create a file
        state_file = tmp_path / ".mcp_server_state.json"
        state_file.write_text('{"test": "data"}')

        # Mock read_text to raise OSError
        def mock_read_text(*args, **kwargs):
            raise OSError("Permission denied")

        monkeypatch.setattr(Path, "read_text", mock_read_text)

        state = PortManager.read_state(tmp_path)
        assert state is None

    def test_cleanup_state_deletes_file(self, port_manager, tmp_path):
        """Test cleanup_state removes state file."""
        # Create state file
        port_manager.write_state(transport="dual", port=4242)

        state_file = tmp_path / ".mcp_server_state.json"
        assert state_file.exists()

        # Cleanup
        port_manager.cleanup_state()

        assert not state_file.exists()

    def test_cleanup_state_safe_when_no_file(self, port_manager):
        """Test cleanup_state safe to call when file doesn't exist."""
        # Should not raise error
        port_manager.cleanup_state()


class TestDocstringsAndTypeHints:
    """Verify code quality requirements."""

    def test_all_methods_have_docstrings(self):
        """Test all public methods have docstrings."""
        methods = [
            PortManager.find_available_port,
            PortManager.write_state,
            PortManager.read_state,
            PortManager.cleanup_state,
        ]

        for method in methods:
            assert method.__doc__ is not None
            assert len(method.__doc__) > 20  # Substantive docstring

    def test_class_has_docstring(self):
        """Test PortManager class has comprehensive docstring."""
        assert PortManager.__doc__ is not None
        assert "Manages dynamic port allocation" in PortManager.__doc__
        assert "Example:" in PortManager.__doc__

    def test_module_has_docstring(self):
        """Test module has docstring."""
        import mcp_server.port_manager as pm

        assert pm.__doc__ is not None
        assert "Port allocation" in pm.__doc__
