"""
Unit tests for TransportManager.

Tests transport orchestration, threading, and error handling.
"""

import socket
import threading
import time
from unittest.mock import MagicMock, patch

import pytest

from mcp_server.transport_manager import TransportManager


@pytest.fixture
def mock_mcp_server():
    """Mock FastMCP server for testing."""
    server = MagicMock()
    server.run = MagicMock()
    return server


@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    config = MagicMock()
    config.http_host = "127.0.0.1"
    config.http_port = 4242
    config.http_path = "/mcp"
    return config


@pytest.fixture
def transport_manager(mock_mcp_server, mock_config):
    """Create TransportManager instance with mocks."""
    return TransportManager(mock_mcp_server, mock_config)


class TestInitialization:
    """Test TransportManager initialization."""

    def test_init_stores_server_and_config(self, mock_mcp_server, mock_config):
        """Test initialization stores MCP server and config."""
        manager = TransportManager(mock_mcp_server, mock_config)

        assert manager.mcp_server is mock_mcp_server
        assert manager.config is mock_config
        assert manager.http_thread is None


class TestStdioMode:
    """Test stdio-only mode."""

    def test_run_stdio_mode_calls_mcp_run(self, transport_manager):
        """Test run_stdio_mode calls MCP run with stdio transport."""
        transport_manager.run_stdio_mode()

        transport_manager.mcp_server.run.assert_called_once_with(
            transport="stdio", show_banner=False
        )

    def test_run_stdio_mode_no_http_thread(self, transport_manager):
        """Test run_stdio_mode doesn't create HTTP thread."""
        transport_manager.run_stdio_mode()

        assert transport_manager.http_thread is None


class TestHttpMode:
    """Test HTTP-only mode."""

    def test_run_http_mode_calls_mcp_run(self, transport_manager):
        """Test run_http_mode calls MCP run with HTTP transport."""
        transport_manager.run_http_mode(host="127.0.0.1", port=4242, path="/mcp")

        transport_manager.mcp_server.run.assert_called_once_with(
            transport="streamable-http",
            host="127.0.0.1",
            port=4242,
            path="/mcp",
            show_banner=False,
        )


class TestDualMode:
    """Test dual transport mode."""

    def test_run_dual_mode_starts_http_thread(self, transport_manager):
        """Test run_dual_mode creates HTTP daemon thread."""
        # Mock HTTP readiness check to succeed immediately
        with patch.object(transport_manager, "_wait_for_http_ready", return_value=True):
            # Mock stdio run to exit immediately
            transport_manager.mcp_server.run = MagicMock()

            transport_manager.run_dual_mode(
                http_host="127.0.0.1", http_port=4242, http_path="/mcp"
            )

            # Verify HTTP thread was created
            assert transport_manager.http_thread is not None
            assert isinstance(transport_manager.http_thread, threading.Thread)

    def test_run_dual_mode_waits_for_http_ready(self, transport_manager):
        """Test run_dual_mode waits for HTTP readiness."""
        wait_for_ready_called = False

        def mock_wait(host, port, timeout):
            nonlocal wait_for_ready_called
            wait_for_ready_called = True
            return True

        with patch.object(
            transport_manager, "_wait_for_http_ready", side_effect=mock_wait
        ):
            transport_manager.mcp_server.run = MagicMock()

            transport_manager.run_dual_mode(
                http_host="127.0.0.1", http_port=4242, http_path="/mcp"
            )

            assert wait_for_ready_called

    def test_run_dual_mode_raises_if_http_fails(self, transport_manager):
        """Test run_dual_mode raises RuntimeError if HTTP fails to start."""
        # Mock HTTP readiness check to fail
        with patch.object(
            transport_manager, "_wait_for_http_ready", return_value=False
        ):
            with pytest.raises(RuntimeError) as exc_info:
                transport_manager.run_dual_mode(
                    http_host="127.0.0.1", http_port=4242, http_path="/mcp"
                )

            assert "failed to start" in str(exc_info.value).lower()
            assert "5 seconds" in str(exc_info.value)

    def test_run_dual_mode_runs_stdio_after_http_ready(self, transport_manager):
        """Test run_dual_mode runs stdio in main thread after HTTP ready."""
        call_order = []

        def mock_wait(host, port, timeout):
            call_order.append("wait_http")
            return True

        def mock_run(**kwargs):
            call_order.append(f"run_{kwargs.get('transport', 'unknown')}")

        with patch.object(
            transport_manager, "_wait_for_http_ready", side_effect=mock_wait
        ):
            transport_manager.mcp_server.run = mock_run

            transport_manager.run_dual_mode(
                http_host="127.0.0.1", http_port=4242, http_path="/mcp"
            )

            # Verify stdio runs after HTTP wait
            assert "wait_http" in call_order
            assert "run_stdio" in call_order
            assert call_order.index("wait_http") < call_order.index("run_stdio")


class TestHttpThreadManagement:
    """Test HTTP thread creation and management."""

    def test_start_http_thread_creates_daemon_thread(self, transport_manager):
        """Test _start_http_thread creates daemon thread."""
        # Mock mcp_server.run to block briefly so we can check thread
        run_event = threading.Event()

        def mock_run(**kwargs):
            run_event.wait(timeout=2)

        transport_manager.mcp_server.run = mock_run

        thread = transport_manager._start_http_thread(
            host="127.0.0.1", port=4242, path="/mcp"
        )

        # Give thread a moment to start
        time.sleep(0.1)

        assert isinstance(thread, threading.Thread)
        assert thread.daemon is True
        assert thread.name == "http-transport"
        assert thread.is_alive()

        # Cleanup: signal thread to finish and wait
        run_event.set()
        thread.join(timeout=1)

    def test_start_http_thread_calls_mcp_run_with_http(self, transport_manager):
        """Test HTTP thread calls mcp_server.run with correct params."""
        run_called = threading.Event()
        run_args = {}

        def mock_run(**kwargs):
            run_args.update(kwargs)
            run_called.set()

        transport_manager.mcp_server.run = mock_run

        thread = transport_manager._start_http_thread(
            host="127.0.0.1", port=4242, path="/mcp"
        )

        # Wait for thread to call run
        run_called.wait(timeout=2)

        assert run_args["transport"] == "streamable-http"
        assert run_args["host"] == "127.0.0.1"
        assert run_args["port"] == 4242
        assert run_args["path"] == "/mcp"
        assert run_args["show_banner"] is False

        # Cleanup
        thread.join(timeout=1)

    def test_start_http_thread_handles_exceptions(self, transport_manager, caplog):
        """Test HTTP thread handles exceptions gracefully."""

        def mock_run(**kwargs):
            raise RuntimeError("Test error in HTTP thread")

        transport_manager.mcp_server.run = mock_run

        thread = transport_manager._start_http_thread(
            host="127.0.0.1", port=4242, path="/mcp"
        )

        # Wait for thread to finish
        thread.join(timeout=2)

        # Thread should have logged error but not crashed
        assert not thread.is_alive()


class TestHttpReadinessCheck:
    """Test HTTP server readiness checking."""

    def test_wait_for_http_ready_returns_true_when_ready(self, transport_manager):
        """Test _wait_for_http_ready returns True when server ready."""
        # Create a real socket server to simulate HTTP server
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(("127.0.0.1", 0))  # Bind to any available port
        port = server_socket.getsockname()[1]
        server_socket.listen(1)

        try:
            result = transport_manager._wait_for_http_ready(
                host="127.0.0.1", port=port, timeout=2
            )

            assert result is True
        finally:
            server_socket.close()

    def test_wait_for_http_ready_returns_false_on_timeout(self, transport_manager):
        """Test _wait_for_http_ready returns False on timeout."""
        # Use a port that nothing is listening on
        result = transport_manager._wait_for_http_ready(
            host="127.0.0.1",
            port=54321,  # Unlikely to be in use
            timeout=1,  # Short timeout for fast test
        )

        assert result is False

    def test_wait_for_http_ready_retries_connection(self, transport_manager):
        """Test _wait_for_http_ready retries connection multiple times."""
        # Find an available port
        temp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        temp_sock.bind(("127.0.0.1", 0))
        port = temp_sock.getsockname()[1]
        temp_sock.close()

        server_started = threading.Event()

        def delayed_server():
            """Start server after a delay to test retries."""
            time.sleep(0.8)  # Delay server startup
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind(("127.0.0.1", port))
            server.listen(1)
            server_started.set()
            time.sleep(2)  # Keep server alive
            server.close()

        # Start server in background after delay
        server_thread = threading.Thread(target=delayed_server, daemon=True)
        server_thread.start()

        # This should retry and eventually succeed
        result = transport_manager._wait_for_http_ready(
            host="127.0.0.1", port=port, timeout=3
        )

        # Should succeed after retries
        assert result is True
        assert server_started.is_set()


class TestShutdown:
    """Test graceful shutdown."""

    def test_shutdown_safe_when_no_thread(self, transport_manager):
        """Test shutdown safe to call when no HTTP thread exists."""
        # Should not raise error
        transport_manager.shutdown()

    def test_shutdown_safe_when_thread_not_alive(self, transport_manager):
        """Test shutdown safe when thread exists but not alive."""
        # Create mock thread that's not alive
        transport_manager.http_thread = MagicMock(spec=threading.Thread)
        transport_manager.http_thread.is_alive.return_value = False

        # Should not raise error
        transport_manager.shutdown()


class TestDocstringsAndTypeHints:
    """Verify code quality requirements."""

    def test_all_methods_have_docstrings(self):
        """Test all public methods have docstrings."""
        methods = [
            TransportManager.run_dual_mode,
            TransportManager.run_stdio_mode,
            TransportManager.run_http_mode,
            TransportManager.shutdown,
        ]

        for method in methods:
            assert method.__doc__ is not None
            assert len(method.__doc__) > 20  # Substantive docstring

    def test_class_has_docstring(self):
        """Test TransportManager class has comprehensive docstring."""
        assert TransportManager.__doc__ is not None
        assert "Manages transport mode" in TransportManager.__doc__
        assert "Example:" in TransportManager.__doc__

    def test_module_has_docstring(self):
        """Test module has docstring."""
        import mcp_server.transport_manager as tm

        assert tm.__doc__ is not None
        assert "Transport mode management" in tm.__doc__
