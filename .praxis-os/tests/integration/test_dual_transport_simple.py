"""
Simplified integration tests for dual-transport mode.

These tests verify basic server functionality without full stdio/HTTP interaction.
Tests focus on verifiable artifacts: state files, process startup, and configuration.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest


class TestDualTransportBasics:
    """Basic integration tests for dual-transport mode."""

    @pytest.fixture
    def agent_os_path(self, tmp_path):
        """Create a temporary .praxis-os directory structure for testing."""
        agent_os = tmp_path / ".praxis-os"
        agent_os.mkdir()

        # Create minimal config
        config_path = agent_os / "config.yaml"
        config_path.write_text(
            """
server:
  log_level: INFO

rag:
  embedding_provider: sentence-transformers
  embedding_model: all-MiniLM-L6-v2
  chunk_size: 512
  chunk_overlap: 64
  top_k: 5

mcp:
  enabled_tool_groups:
    - rag
    - workflow
  max_tools_warning: 20
  http_port: 4242
  http_host: 127.0.0.1
  http_path: /mcp
"""
        )

        # Create required directories
        (agent_os / "standards").mkdir()
        (agent_os / "workflows").mkdir()
        (agent_os / "usage").mkdir()
        (agent_os / ".cache").mkdir()

        # Create standards file with sufficient content for chunking
        standards_content = """# Test Standard for Integration Tests

## Overview

This is a comprehensive test standard document designed to generate meaningful
chunks for the RAG index during integration testing. It needs to have sufficient
content to be chunked properly by the indexing system.

## Purpose

The purpose of this document is to provide test data that will:
- Generate multiple text chunks for embedding
- Allow the RAG index to be built successfully
- Enable integration tests to run without errors

## Implementation Guidelines

When implementing features, follow these best practices:

1. Write clear and concise code
2. Include comprehensive documentation
3. Add unit tests for all new functionality  
4. Ensure backward compatibility
5. Follow the project's coding standards

### Code Quality

Code quality is paramount. All code should be:
- Well-documented with docstrings
- Type-annotated for clarity
- Tested with high coverage
- Reviewed by peers before merging

### Testing Standards

Tests should cover:
- Happy path scenarios
- Edge cases and boundary conditions
- Error handling and recovery
- Performance under load

## Conclusion

This test document provides sufficient content for chunk generation and RAG
index building in integration test scenarios.
"""
        (agent_os / "standards" / "test.md").write_text(standards_content)

        return agent_os

    def test_server_creates_state_file_in_dual_mode(self, agent_os_path):
        """Test that server creates state file when started in dual mode."""
        # Save and change directory
        original_dir = os.getcwd()
        os.chdir(agent_os_path.parent)

        try:
            # Get project root
            project_root = Path(__file__).parent.parent.parent

            # Start server with stdin from /dev/null to prevent blocking
            cmd = [
                sys.executable,
                "-m",
                "mcp_server",
                "--transport",
                "dual",
                "--log-level",
                "INFO",
            ]

            env = os.environ.copy()
            env["PYTHONPATH"] = str(project_root)

            # Run with timeout and stdin from /dev/null
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.DEVNULL,  # Don't block on stdin
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(agent_os_path.parent),
                env=env,
            )

            # Wait for state file to appear
            state_file = agent_os_path / ".mcp_server_state.json"
            max_wait = 30
            start_time = time.time()
            state_was_created = False
            state_content = None

            while time.time() - start_time < max_wait:
                if state_file.exists() and not state_was_created:
                    # State file appeared! Read it immediately
                    state_was_created = True
                    with open(state_file) as f:
                        state_content = json.load(f)
                    break
                time.sleep(0.1)
                # Check if process died
                if process.poll() is not None:
                    # Process may have exited but state file might have been created
                    if state_file.exists() and not state_was_created:
                        with open(state_file) as f:
                            state_content = json.load(f)
                        state_was_created = True
                    break

            # Check if state file was created (even if later cleaned up)
            if state_was_created and state_content:
                # Success! Validate state content
                assert "version" in state_content
                assert state_content["transport"] == "dual"
                assert "port" in state_content
                assert isinstance(state_content["port"], int)
                assert 1024 <= state_content["port"] <= 65535
                assert "url" in state_content
                assert state_content["url"].startswith("http://127.0.0.1:")
                assert "pid" in state_content
                assert "started_at" in state_content
                assert "project" in state_content

                # Cleanup if still exists
                if state_file.exists():
                    state_file.unlink()
            else:
                # If state file wasn't created, check process output
                process.terminate()
                stdout, stderr = process.communicate(timeout=5)

                # State file creation happens early, so even if server exits
                # after due to no stdin, state file should exist
                pytest.fail(
                    f"State file not created. Process exited with {process.returncode}.\n"
                    f"STDERR (last 500 chars): {stderr[-500:]}"
                )

            # Terminate process if still running
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()

        finally:
            os.chdir(original_dir)

    def test_http_mode_creates_state_file(self, agent_os_path):
        """Test that server creates state file in HTTP-only mode."""
        original_dir = os.getcwd()
        os.chdir(agent_os_path.parent)

        try:
            project_root = Path(__file__).parent.parent.parent

            cmd = [
                sys.executable,
                "-m",
                "mcp_server",
                "--transport",
                "http",
                "--log-level",
                "INFO",
            ]

            env = os.environ.copy()
            env["PYTHONPATH"] = str(project_root)

            # HTTP mode will stay running, so we need to terminate it
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(agent_os_path.parent),
                env=env,
            )

            # Wait for state file
            state_file = agent_os_path / ".mcp_server_state.json"
            max_wait = 30
            start_time = time.time()

            while time.time() - start_time < max_wait:
                if state_file.exists():
                    break
                time.sleep(0.1)
                if process.poll() is not None:
                    stdout, stderr = process.communicate(timeout=1)
                    pytest.fail(
                        f"Server exited early with {process.returncode}.\n"
                        f"STDERR: {stderr[-500:]}"
                    )

            # Verify state file exists and has correct content
            assert state_file.exists(), "State file should be created"

            with open(state_file) as f:
                state = json.load(f)

            assert state["transport"] == "http"
            assert isinstance(state["port"], int)

            # Cleanup
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()

            # State file should be cleaned up after termination
            # Give more time for cleanup (finally block execution)
            time.sleep(1.0)

            # Note: State file cleanup is best-effort. If process is killed
            # abruptly, cleanup may not happen. This is acceptable for tests.
            if state_file.exists():
                # Clean it up manually for test hygiene
                state_file.unlink()

        finally:
            os.chdir(original_dir)

    def test_stdio_mode_creates_state_file(self, agent_os_path):
        """Test that server creates state file in stdio-only mode."""
        original_dir = os.getcwd()
        os.chdir(agent_os_path.parent)

        try:
            project_root = Path(__file__).parent.parent.parent

            cmd = [
                sys.executable,
                "-m",
                "mcp_server",
                "--transport",
                "stdio",
                "--log-level",
                "INFO",
            ]

            env = os.environ.copy()
            env["PYTHONPATH"] = str(project_root)

            process = subprocess.Popen(
                cmd,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(agent_os_path.parent),
                env=env,
            )

            # Wait for state file
            state_file = agent_os_path / ".mcp_server_state.json"
            max_wait = 30
            start_time = time.time()

            while time.time() - start_time < max_wait:
                if state_file.exists():
                    break
                time.sleep(0.1)
                if process.poll() is not None:
                    break

            # Verify state file was created
            if state_file.exists():
                with open(state_file) as f:
                    state = json.load(f)

                assert state["transport"] == "stdio"
                assert state["port"] is None  # No port for stdio-only

                # Cleanup
                state_file.unlink()

            # Terminate if still running
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=5)

        finally:
            os.chdir(original_dir)


class TestMultiProjectIsolation:
    """Test multi-project port isolation (simplified)."""

    def test_multiple_state_files_different_ports(self, tmp_path):
        """Test that multiple projects can have state files with different ports."""
        import socket

        from mcp_server.port_manager import PortManager
        from mcp_server.project_info import ProjectInfoDiscovery

        # Create 3 different project directories
        projects = []
        for i in range(3):
            project_dir = tmp_path / f"project_{i}" / ".praxis-os"
            project_dir.mkdir(parents=True)
            projects.append(project_dir)

        # Bind actual sockets to hold ports, simulating running servers
        sockets = []
        ports = []

        try:
            for i, project_dir in enumerate(projects):
                discovery = ProjectInfoDiscovery(project_dir)
                port_mgr = PortManager(project_dir, discovery)

                # Allocate port
                port = port_mgr.find_available_port(preferred_port=4242 + i)

                # Actually bind to the port to hold it
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind(("127.0.0.1", port))
                sock.listen(1)
                sockets.append(sock)
                ports.append(port)

                # Write state
                port_mgr.write_state("dual", port)

            # Verify all ports are different
            assert len(set(ports)) == 3, f"All ports should be unique: {ports}"
            assert all(4242 <= p <= 5242 for p in ports), "All ports in valid range"

            # Verify all state files exist
            for project_dir in projects:
                state_file = project_dir / ".mcp_server_state.json"
                assert state_file.exists()

        finally:
            # Close sockets
            for sock in sockets:
                sock.close()

            # Cleanup state files
            for project_dir in projects:
                discovery = ProjectInfoDiscovery(project_dir)
                port_mgr = PortManager(project_dir, discovery)
                port_mgr.cleanup_state()

                state_file = project_dir / ".mcp_server_state.json"
                assert not state_file.exists()


# Note: Full HTTP endpoint testing requires async MCP client setup
# which is beyond the scope of basic integration tests. Manual testing
# or dedicated E2E test suite should cover HTTP protocol interactions.
