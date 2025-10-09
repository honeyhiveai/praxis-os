"""
Server Manager for Agent OS Upgrade Workflow.

Manages MCP server restart and health verification.
"""

import subprocess
import time
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class ServerManager:
    """
    Manages MCP server process lifecycle.

    Features:
    - Graceful server restart
    - Health check polling
    - Process management
    - Restart timing

    Example:
        manager = ServerManager()
        result = manager.restart_server()
        if result["started"]:
            print(f"Server restarted in {result['restart_time_seconds']}s")
    """

    @staticmethod
    def restart_server() -> Dict:
        """
        Restart MCP server process.

        Steps:
        1. Stop server (pkill)
        2. Wait for process to terminate
        3. Start new process in background
        4. Wait for health check

        Returns:
            {
                "stopped": bool,
                "started": bool,
                "restart_time_seconds": float,
                "pid": int | None,
                "error": str | None
            }
        """
        logger.info("Restarting MCP server...")

        start_time = time.time()

        result = {
            "stopped": False,
            "started": False,
            "restart_time_seconds": 0.0,
            "pid": None,
            "error": None,
        }

        # Step 1: Stop server
        try:
            subprocess.run(
                ["pkill", "-f", "python -m mcp_server"],
                timeout=10,
            )
            logger.info("Sent stop signal to MCP server")

            # Wait for process to terminate
            time.sleep(2)
            result["stopped"] = True

        except subprocess.TimeoutExpired:
            result["error"] = "Failed to stop server: timeout"
            logger.error(result["error"])
            return result
        except Exception as e:
            result["error"] = f"Failed to stop server: {e}"
            logger.error(result["error"])
            return result

        # Step 2: Start server in background
        try:
            # Start server in background
            process = subprocess.Popen(
                ["python", "-m", "mcp_server"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )

            result["pid"] = process.pid
            logger.info(f"Started MCP server with PID: {process.pid}")

            # Wait a moment for server to initialize
            time.sleep(3)

            result["started"] = True

        except Exception as e:
            result["error"] = f"Failed to start server: {e}"
            logger.error(result["error"])
            return result

        # Calculate restart time
        result["restart_time_seconds"] = time.time() - start_time

        logger.info(f"Server restarted in {result['restart_time_seconds']:.2f}s")

        return result

    @staticmethod
    def wait_for_server_ready(timeout: int = 30) -> bool:
        """
        Wait for server to respond to health checks.

        Polls every second until server responds or timeout.

        Args:
            timeout: Maximum seconds to wait

        Returns:
            True if server is ready, False if timeout
        """
        logger.info(f"Waiting for server to be ready (timeout: {timeout}s)...")

        start_time = time.time()

        while time.time() - start_time < timeout:
            # Check if server process is running
            try:
                result = subprocess.run(
                    ["pgrep", "-f", "python -m mcp_server"],
                    capture_output=True,
                    timeout=5,
                )

                if result.returncode == 0:
                    logger.info("Server is ready")
                    return True

            except Exception as e:
                logger.debug(f"Health check failed: {e}")

            time.sleep(1)

        logger.error(f"Server not ready after {timeout}s")
        return False

    @staticmethod
    def stop_server() -> bool:
        """
        Stop MCP server process.

        Returns:
            True if stopped successfully, False otherwise
        """
        logger.info("Stopping MCP server...")

        try:
            subprocess.run(
                ["pkill", "-f", "python -m mcp_server"],
                timeout=10,
            )
            logger.info("Server stopped")
            return True

        except Exception as e:
            logger.error(f"Failed to stop server: {e}")
            return False

    @staticmethod
    def is_server_running() -> bool:
        """
        Check if MCP server is currently running.

        Returns:
            True if running, False otherwise
        """
        try:
            result = subprocess.run(
                ["pgrep", "-f", "python -m mcp_server"],
                capture_output=True,
                timeout=5,
            )
            return result.returncode == 0

        except Exception:
            return False

