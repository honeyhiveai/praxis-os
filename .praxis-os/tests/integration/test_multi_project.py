"""
Integration tests for multi-project scenarios.

Tests that multiple MCP servers can run simultaneously without conflicts,
each with unique ports and independent state.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest


class TestMultiProjectIntegration:
    """Integration tests for multiple concurrent MCP servers."""

    @pytest.fixture
    def three_projects(self, tmp_path):
        """Create 3 separate project directories with .praxis-os structure."""
        projects = []

        for i in range(3):
            project_root = tmp_path / f"project_{i}"
            agent_os = project_root / ".praxis-os"
            agent_os.mkdir(parents=True)

            # Create minimal config for each
            config_path = agent_os / "config.yaml"
            config_path.write_text(
                f"""
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
  max_tools_warning: 20
  http_port: {4242 + i}
  http_host: 127.0.0.1
  http_path: /mcp
"""
            )

            # Create required directories
            (agent_os / "standards").mkdir()
            (agent_os / "workflows").mkdir()
            (agent_os / "usage").mkdir()
            (agent_os / ".cache").mkdir()

            # Create test standards file
            standards_content = f"""# Test Standard for Project {i}

## Overview

This is test content for project {i} to ensure each project has unique
content and independent RAG indices.

## Project-Specific Content

Project {i} has its own standards, workflows, and configuration.
Each project operates independently with its own port and state file.

### Implementation

Projects should be isolated:
- Separate ports (4242, 4243, 4244, etc.)
- Separate state files
- Separate RAG indices
- No interference between projects

## Testing

This content ensures the RAG index can be built successfully.
"""
            (agent_os / "standards" / "test.md").write_text(standards_content)

            projects.append(
                {
                    "root": project_root,
                    "agent_os": agent_os,
                    "expected_port": 4242 + i,
                }
            )

        return projects

    def test_three_servers_start_simultaneously(self, three_projects):
        """Test that 3 servers can start and run concurrently without conflicts."""
        project_root = Path(__file__).parent.parent.parent
        processes = []
        original_dir = os.getcwd()

        try:
            # Start all 3 servers
            for i, project in enumerate(three_projects):
                os.chdir(project["root"])

                cmd = [
                    sys.executable,
                    "-m",
                    "mcp_server",
                    "--transport",
                    "http",  # Use HTTP mode for easier testing
                    "--log-level",
                    "INFO",
                ]

                env = os.environ.copy()
                env["PYTHONPATH"] = str(project_root)

                process = subprocess.Popen(
                    cmd,
                    stdin=subprocess.DEVNULL,  # HTTP mode doesn't need stdin
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=str(project["root"]),
                    env=env,
                )

                processes.append({"process": process, "project": project, "index": i})

                # Small stagger to avoid overwhelming system during RAG index builds
                # (3 embedding models loading simultaneously can exhaust resources)
                if i < len(three_projects) - 1:
                    time.sleep(1.0)

            # Wait for all state files to appear
            max_wait = 45  # Longer timeout for 3 servers building indices
            start_time = time.time()
            all_ready = False

            while time.time() - start_time < max_wait:
                ready_count = 0
                for proc_info in processes:
                    state_file = (
                        proc_info["project"]["agent_os"] / ".mcp_server_state.json"
                    )
                    if state_file.exists():
                        ready_count += 1

                if ready_count == 3:
                    all_ready = True
                    break

                time.sleep(0.5)

                # Check if any process died early
                for proc_info in processes:
                    if proc_info["process"].poll() is not None:
                        stdout, stderr = proc_info["process"].communicate(timeout=1)
                        pytest.fail(
                            f"Server {proc_info['index']} exited early with code "
                            f"{proc_info['process'].returncode}.\n"
                            f"STDERR: {stderr[-500:]}"
                        )

            assert all_ready, "All 3 servers should have created state files"

            # Verify all servers are still running
            for proc_info in processes:
                assert (
                    proc_info["process"].poll() is None
                ), f"Server {proc_info['index']} should still be running"

            # Read and validate state files
            ports = []
            for proc_info in processes:
                state_file = proc_info["project"]["agent_os"] / ".mcp_server_state.json"

                with open(state_file) as f:
                    state = json.load(f)

                # Validate state structure
                assert "port" in state
                assert "transport" in state
                assert state["transport"] == "http"
                assert isinstance(state["port"], int)

                ports.append(state["port"])

                # Verify port matches expected or is nearby
                # (may differ if preferred port is taken)
                assert 4242 <= state["port"] <= 5242

            # Verify all ports are different
            assert len(set(ports)) == 3, f"All ports should be unique: {ports}"

            # Give servers a moment to fully start
            time.sleep(1)

            # Verify all processes still running (didn't crash after startup)
            for proc_info in processes:
                assert (
                    proc_info["process"].poll() is None
                ), f"Server {proc_info['index']} crashed after startup"

        finally:
            # Cleanup - terminate all processes
            os.chdir(original_dir)

            for proc_info in processes:
                if proc_info["process"].poll() is None:
                    proc_info["process"].terminate()
                    try:
                        proc_info["process"].wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        proc_info["process"].kill()
                        proc_info["process"].wait()

    def test_port_reuse_after_shutdown(self, three_projects):
        """Test that ports can be reused after server shutdown."""
        project_root = Path(__file__).parent.parent.parent
        original_dir = os.getcwd()

        # Use first project
        project = three_projects[0]

        try:
            os.chdir(project["root"])

            # Start server, record port, shut down
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

            # First run
            process1 = subprocess.Popen(
                cmd,
                stdin=subprocess.DEVNULL,  # HTTP mode doesn't need stdin
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(project["root"]),
                env=env,
            )

            # Wait for state file
            state_file = project["agent_os"] / ".mcp_server_state.json"
            max_wait = 30
            start_time = time.time()

            while time.time() - start_time < max_wait:
                if state_file.exists():
                    break
                time.sleep(0.1)
                if process1.poll() is not None:
                    stdout, stderr = process1.communicate(timeout=1)
                    pytest.fail(f"First server exited early. STDERR: {stderr[-500:]}")

            assert state_file.exists(), "State file should be created"

            # Read port from first run
            with open(state_file) as f:
                state1 = json.load(f)
            port1 = state1["port"]

            # Shutdown first server
            process1.terminate()
            process1.wait(timeout=5)

            # Wait for cleanup
            time.sleep(1)

            # Start server again - should get same port
            process2 = subprocess.Popen(
                cmd,
                stdin=subprocess.DEVNULL,  # HTTP mode doesn't need stdin
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(project["root"]),
                env=env,
            )

            # Wait for state file again
            start_time = time.time()
            while time.time() - start_time < max_wait:
                if state_file.exists():
                    break
                time.sleep(0.1)
                if process2.poll() is not None:
                    stdout, stderr = process2.communicate(timeout=1)
                    pytest.fail(f"Second server exited early. STDERR: {stderr[-500:]}")

            # Read port from second run
            with open(state_file) as f:
                state2 = json.load(f)
            port2 = state2["port"]

            # Should get same port since it was released
            assert port2 == port1, f"Port should be reused: {port1} vs {port2}"

            # Cleanup
            process2.terminate()
            process2.wait(timeout=5)

        finally:
            os.chdir(original_dir)

    def test_state_files_are_independent(self, three_projects):
        """Test that each project has independent state files."""
        from mcp_server.port_manager import PortManager
        from mcp_server.project_info import ProjectInfoDiscovery

        # Create state for all 3 projects
        for i, project in enumerate(three_projects):
            discovery = ProjectInfoDiscovery(project["agent_os"])
            port_mgr = PortManager(project["agent_os"], discovery)

            # Write state with different ports
            port_mgr.write_state("http", 4242 + i)

        # Verify all state files exist and are independent
        for i, project in enumerate(three_projects):
            state_file = project["agent_os"] / ".mcp_server_state.json"
            assert state_file.exists()

            with open(state_file) as f:
                state = json.load(f)

            # Each should have its own port
            assert state["port"] == 4242 + i

            # Each should have its own project info
            assert "project" in state
            assert f"project_{i}" in state["project"]["name"]

        # Cleanup
        for project in three_projects:
            discovery = ProjectInfoDiscovery(project["agent_os"])
            port_mgr = PortManager(project["agent_os"], discovery)
            port_mgr.cleanup_state()


class TestMultiProjectDocumentation:
    """Test documentation quality."""

    def test_module_has_docstring(self):
        """Test that module has comprehensive docstring."""
        import tests.integration.test_multi_project as module

        assert module.__doc__ is not None
        assert len(module.__doc__.strip()) > 50
