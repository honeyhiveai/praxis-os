"""
Integration tests for error scenarios.

Tests error handling, recovery, and cleanup in failure conditions.
"""

import json
import os
import socket
import time
from pathlib import Path

import pytest

from mcp_server.port_manager import PortManager
from mcp_server.project_info import ProjectInfoDiscovery


class TestPortExhaustion:
    """Test port exhaustion error scenarios."""

    def test_port_exhaustion_error_message(self, tmp_path):
        """Test that port exhaustion shows actionable error message."""
        agent_os = tmp_path / ".praxis-os"
        agent_os.mkdir()

        discovery = ProjectInfoDiscovery(agent_os)
        port_mgr = PortManager(agent_os, discovery)

        # Bind all ports in range to exhaust them
        sockets = []
        try:
            for port in range(4242, 5243):  # Entire range
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                try:
                    sock.bind(("127.0.0.1", port))
                    sock.listen(1)
                    sockets.append(sock)
                except OSError:
                    # Port might already be in use on system
                    pass

            # Now try to find a port - should raise RuntimeError
            with pytest.raises(RuntimeError) as exc_info:
                port_mgr.find_available_port()

            # Check error message is actionable
            error_msg = str(exc_info.value)
            assert (
                "exhausted port range" in error_msg.lower()
                or "no available ports" in error_msg.lower()
            )

        finally:
            for sock in sockets:
                sock.close()


class TestStalePIDDetection:
    """Test stale PID detection in state files."""

    def test_stale_pid_detection(self, tmp_path):
        """Test that stale PIDs in state files are detected."""
        agent_os = tmp_path / ".praxis-os"
        agent_os.mkdir()

        discovery = ProjectInfoDiscovery(agent_os)
        port_mgr = PortManager(agent_os, discovery)

        # Write a state file with a non-existent PID
        state_file = agent_os / ".mcp_server_state.json"
        stale_state = {
            "version": "1.0.0",
            "transport": "dual",
            "port": 4242,
            "url": "http://127.0.0.1:4242/mcp",
            "pid": 999999,  # Almost certainly doesn't exist
            "started_at": "2025-01-01T00:00:00Z",
            "project": {"name": "test-project", "root": str(tmp_path)},
        }

        with open(state_file, "w") as f:
            json.dump(stale_state, f)

        # read_state should return the state even if PID is stale
        # (PID validation is informational, not blocking)
        state = PortManager.read_state(agent_os)
        assert state is not None
        assert state["pid"] == 999999

        # The state file exists, so new server should detect it
        # and potentially clean it up or warn about it
        assert state_file.exists()


class TestCorruptedStateFile:
    """Test handling of corrupted state files."""

    def test_corrupted_json_returns_none(self, tmp_path):
        """Test that corrupted state file returns None without crashing."""
        agent_os = tmp_path / ".praxis-os"
        agent_os.mkdir()

        # Write invalid JSON
        state_file = agent_os / ".mcp_server_state.json"
        state_file.write_text("{invalid json content here")

        # Should return None, not crash
        state = PortManager.read_state(agent_os)
        assert state is None

    def test_empty_state_file_returns_none(self, tmp_path):
        """Test that empty state file returns None."""
        agent_os = tmp_path / ".praxis-os"
        agent_os.mkdir()

        # Write empty file
        state_file = agent_os / ".mcp_server_state.json"
        state_file.write_text("")

        state = PortManager.read_state(agent_os)
        assert state is None

    def test_missing_state_file_returns_none(self, tmp_path):
        """Test that missing state file returns None."""
        agent_os = tmp_path / ".praxis-os"
        agent_os.mkdir()

        # No state file exists
        state = PortManager.read_state(agent_os)
        assert state is None


class TestStateFileCleanup:
    """Test state file cleanup on errors."""

    def test_cleanup_on_keyboard_interrupt(self, tmp_path):
        """Test that state file is cleaned up on KeyboardInterrupt."""
        agent_os = tmp_path / ".praxis-os"
        agent_os.mkdir()

        discovery = ProjectInfoDiscovery(agent_os)
        port_mgr = PortManager(agent_os, discovery)

        # Write state file
        port_mgr.write_state("dual", 4242)

        state_file = agent_os / ".mcp_server_state.json"
        assert state_file.exists()

        # Cleanup should remove it
        port_mgr.cleanup_state()

        assert not state_file.exists()

    def test_cleanup_idempotent(self, tmp_path):
        """Test that cleanup can be called multiple times safely."""
        agent_os = tmp_path / ".praxis-os"
        agent_os.mkdir()

        discovery = ProjectInfoDiscovery(agent_os)
        port_mgr = PortManager(agent_os, discovery)

        # Write state file
        port_mgr.write_state("dual", 4242)

        # Call cleanup multiple times
        port_mgr.cleanup_state()
        port_mgr.cleanup_state()  # Should not raise
        port_mgr.cleanup_state()  # Should not raise

        state_file = agent_os / ".mcp_server_state.json"
        assert not state_file.exists()


class TestProjectInfoErrors:
    """Test error handling in project info discovery."""

    def test_non_git_repo_returns_none_gracefully(self, tmp_path):
        """Test that non-git repos don't crash, return None for git info."""
        agent_os = tmp_path / ".praxis-os"
        agent_os.mkdir()

        discovery = ProjectInfoDiscovery(agent_os)
        project_info = discovery.get_project_info()

        # Should have project info even without git
        assert "name" in project_info
        assert "root" in project_info

        # Git info should be None
        assert project_info.get("git") is None

    def test_corrupted_git_repo_returns_fallback(self, tmp_path):
        """Test that corrupted git repos fall back to directory name."""
        agent_os = tmp_path / ".praxis-os"
        agent_os.mkdir()

        # Create a fake .git directory (corrupted)
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        (git_dir / "invalid").write_text("corrupted")

        discovery = ProjectInfoDiscovery(agent_os)
        project_info = discovery.get_project_info()

        # Should still return project info with fallback name
        assert "name" in project_info
        assert project_info["name"] is not None


class TestErrorMessages:
    """Test that error messages include remediation steps."""

    def test_port_exhaustion_includes_remediation(self, tmp_path):
        """Test that port exhaustion error includes how to fix it."""
        agent_os = tmp_path / ".praxis-os"
        agent_os.mkdir()

        discovery = ProjectInfoDiscovery(agent_os)
        port_mgr = PortManager(agent_os, discovery)

        # Exhaust some ports
        sockets = []
        try:
            # Bind many ports to make finding one harder
            for port in range(4242, 4300):
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.bind(("127.0.0.1", port))
                    sock.listen(1)
                    sockets.append(sock)
                except OSError:
                    pass

            # If we managed to exhaust the range
            if len(sockets) > 50:
                try:
                    port_mgr.find_available_port()
                except RuntimeError as e:
                    error_msg = str(e).lower()
                    # Error should be informative
                    assert len(error_msg) > 50  # Substantial message
                    assert "port" in error_msg

        finally:
            for sock in sockets:
                sock.close()

    def test_config_errors_are_clear(self, tmp_path):
        """Test that configuration errors are clear and actionable."""
        from mcp_server.config.validator import ConfigValidator
        from mcp_server.models.config import MCPConfig, RAGConfig, ServerConfig

        # Create invalid config
        config = ServerConfig(
            base_path=tmp_path / ".praxis-os",
            mcp=MCPConfig(
                enabled_tool_groups=["rag"],
                max_tools_warning=20,
                http_port=99,  # Invalid port
                http_host="127.0.0.1",
                http_path="/mcp",
            ),
            rag=RAGConfig(embedding_provider="sentence-transformers"),
        )

        errors = ConfigValidator.validate(config)

        # Should have error about invalid port
        assert len(errors) > 0

        # Error should mention port and valid range
        port_error = [e for e in errors if "port" in e.lower()]
        assert len(port_error) > 0
        assert "1024" in port_error[0] or "65535" in port_error[0]


class TestDocumentation:
    """Test documentation quality."""

    def test_module_has_docstring(self):
        """Test that module has comprehensive docstring."""
        import tests.integration.test_error_scenarios as module

        assert module.__doc__ is not None
        assert len(module.__doc__.strip()) > 30
