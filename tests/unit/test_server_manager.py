"""
Unit tests for ServerManager.

Tests server restart and health check functionality.
"""

import pytest
import subprocess
import time
from unittest.mock import Mock, patch, MagicMock
from mcp_server.server_manager import ServerManager


@pytest.fixture
def server_manager():
    """Create ServerManager instance."""
    return ServerManager()


class TestRestartServer:
    """Tests for restart_server method."""
    
    @patch('subprocess.run')
    @patch('subprocess.Popen')
    @patch('time.sleep')
    def test_restart_server_success(self, mock_sleep, mock_popen, mock_run, server_manager):
        """Test successful server restart."""
        # Mock pkill success
        mock_run.return_value = Mock(returncode=0)
        
        # Mock Popen for server start
        mock_process = Mock()
        mock_process.pid = 12345
        mock_popen.return_value = mock_process
        
        result = server_manager.restart_server()
        
        assert result["stopped"] is True
        assert result["started"] is True
        assert result["pid"] == 12345
        assert result["restart_time_seconds"] > 0
        assert result["error"] is None
    
    @patch('subprocess.run')
    def test_restart_server_stop_timeout(self, mock_run, server_manager):
        """Test server restart when stop times out."""
        # Mock timeout on pkill
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="pkill", timeout=10)
        
        result = server_manager.restart_server()
        
        assert result["stopped"] is False
        assert result["started"] is False
        assert "timeout" in result["error"].lower()
    
    @patch('subprocess.run')
    @patch('subprocess.Popen')
    @patch('time.sleep')
    def test_restart_server_start_failure(self, mock_sleep, mock_popen, mock_run, server_manager):
        """Test server restart when start fails."""
        # Mock successful stop
        mock_run.return_value = Mock(returncode=0)
        
        # Mock Popen failure
        mock_popen.side_effect = Exception("Failed to start server")
        
        result = server_manager.restart_server()
        
        assert result["stopped"] is True
        assert result["started"] is False
        assert "failed to start" in result["error"].lower()


class TestWaitForServerReady:
    """Tests for wait_for_server_ready method."""
    
    @patch('subprocess.run')
    @patch('time.sleep')
    def test_wait_for_server_ready_immediate(self, mock_sleep, mock_run, server_manager):
        """Test waiting when server is immediately ready."""
        # Mock pgrep success (server running)
        mock_run.return_value = Mock(returncode=0)
        
        result = server_manager.wait_for_server_ready(timeout=10)
        
        assert result is True
    
    @patch('subprocess.run')
    @patch('time.sleep')
    @patch('time.time')
    def test_wait_for_server_ready_timeout(self, mock_time, mock_sleep, mock_run, server_manager):
        """Test waiting when server never becomes ready."""
        # Mock time to simulate timeout
        mock_time.side_effect = [0, 5, 10, 15, 20, 25, 31]  # Simulate time passing
        
        # Mock pgrep always failing
        mock_run.return_value = Mock(returncode=1)
        
        result = server_manager.wait_for_server_ready(timeout=30)
        
        assert result is False
    
    @patch('subprocess.run')
    @patch('time.sleep')
    @patch('time.time')
    def test_wait_for_server_ready_eventually(self, mock_time, mock_sleep, mock_run, server_manager):
        """Test waiting when server becomes ready after delay."""
        # Mock time progression
        mock_time.side_effect = [0, 1, 2, 3]
        
        # Mock pgrep failing twice, then succeeding
        mock_run.side_effect = [
            Mock(returncode=1),  # Not ready
            Mock(returncode=1),  # Still not ready
            Mock(returncode=0),  # Ready!
        ]
        
        result = server_manager.wait_for_server_ready(timeout=30)
        
        assert result is True


class TestStopServer:
    """Tests for stop_server method."""
    
    @patch('subprocess.run')
    def test_stop_server_success(self, mock_run, server_manager):
        """Test successful server stop."""
        mock_run.return_value = Mock(returncode=0)
        
        result = server_manager.stop_server()
        
        assert result is True
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_stop_server_failure(self, mock_run, server_manager):
        """Test server stop failure."""
        mock_run.side_effect = Exception("Failed to stop")
        
        result = server_manager.stop_server()
        
        assert result is False


class TestIsServerRunning:
    """Tests for is_server_running method."""
    
    @patch('subprocess.run')
    def test_is_server_running_true(self, mock_run, server_manager):
        """Test when server is running."""
        mock_run.return_value = Mock(returncode=0)
        
        result = server_manager.is_server_running()
        
        assert result is True
    
    @patch('subprocess.run')
    def test_is_server_running_false(self, mock_run, server_manager):
        """Test when server is not running."""
        mock_run.return_value = Mock(returncode=1)
        
        result = server_manager.is_server_running()
        
        assert result is False
    
    @patch('subprocess.run')
    def test_is_server_running_exception(self, mock_run, server_manager):
        """Test when check raises exception."""
        mock_run.side_effect = Exception("Check failed")
        
        result = server_manager.is_server_running()
        
        assert result is False


class TestIntegration:
    """Integration tests for ServerManager."""
    
    @patch('subprocess.run')
    @patch('subprocess.Popen')
    @patch('time.sleep')
    def test_full_restart_cycle(self, mock_sleep, mock_popen, mock_run, server_manager):
        """Test complete restart cycle."""
        # Setup mocks for full restart
        mock_process = Mock()
        mock_process.pid = 54321
        mock_popen.return_value = mock_process
        
        # Mock different calls to subprocess.run
        def run_side_effect(*args, **kwargs):
            cmd = args[0]
            if "pkill" in cmd:
                return Mock(returncode=0)
            elif "pgrep" in cmd:
                return Mock(returncode=0)
            return Mock(returncode=0)
        
        mock_run.side_effect = run_side_effect
        
        # Restart server
        restart_result = server_manager.restart_server()
        assert restart_result["started"] is True
        assert restart_result["pid"] == 54321
        
        # Verify running
        is_running = server_manager.is_server_running()
        assert is_running is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

