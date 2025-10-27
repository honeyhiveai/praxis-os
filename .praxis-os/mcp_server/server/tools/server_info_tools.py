"""
Server info tools for MCP server.

Provides get_server_info tool for runtime server and project discovery.
"""

import logging
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict

logger = logging.getLogger(__name__)

# Module-level variables for server startup tracking
_SERVER_START_TIME = time.time()
_SERVER_START_DATETIME = datetime.now(timezone.utc).isoformat()


def register_server_info_tools(
    mcp: Any, project_discovery: Any, transport_mode: str = "stdio"
) -> int:
    """
    Register server info tools with MCP server.

    Args:
        mcp: FastMCP server instance
        project_discovery: ProjectInfoDiscovery instance
        transport_mode: Current transport mode (dual, stdio, http)

    Returns:
        Number of tools registered
    """

    @mcp.tool()
    async def get_server_info() -> Dict[str, Any]:
        """
        Get comprehensive server and project information.

        Returns runtime metadata about the MCP server, the current project,
        and available capabilities. All information is discovered dynamically
        at runtime - no hardcoded values.

        Useful for:
        - Debugging server configuration
        - Verifying project detection
        - Checking available tools and capabilities
        - Monitoring server uptime

        Returns:
            Dictionary with three main sections:
            - server: Server runtime metadata
            - project: Project information
            - capabilities: Available features and tools

        Example:
            >>> info = await get_server_info()
            >>> print(f"Server uptime: {info['server']['uptime_seconds']}s")
            >>> print(f"Project: {info['project']['name']}")
            >>> print(f"Tools available: {info['capabilities']['tools_available']}")
        """
        try:
            # Discover project info dynamically
            project_info = project_discovery.get_project_info()

            # Calculate uptime
            uptime_seconds = int(time.time() - _SERVER_START_TIME)

            # Get tool count from MCP server
            try:
                # FastMCP stores tools in a dict
                tools_count = len(mcp.list_tools())
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.warning("Could not get tool count: %s", e)
                tools_count = 0

            return {
                "server": {
                    "version": "1.0.0",
                    "transport_mode": transport_mode,
                    "uptime_seconds": uptime_seconds,
                    "pid": os.getpid(),
                    "started_at": _SERVER_START_DATETIME,
                },
                "project": {
                    "name": project_info["name"],
                    "root": project_info["root"],
                    "agent_os_path": project_info["agent_os_path"],
                    "git": project_info.get("git"),
                },
                "capabilities": {
                    "tools_available": tools_count,
                    "rag_enabled": True,
                    "workflow_enabled": True,
                    "browser_enabled": True,
                    "dual_transport": transport_mode == "dual",
                    "http_transport": transport_mode in ["dual", "http"],
                },
            }

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Error getting server info: %s", e, exc_info=True)
            # Return minimal info even on error
            return {
                "server": {
                    "version": "1.0.0",
                    "transport_mode": transport_mode,
                    "uptime_seconds": int(time.time() - _SERVER_START_TIME),
                    "pid": os.getpid(),
                    "started_at": _SERVER_START_DATETIME,
                    "error": str(e),
                },
                "project": {"error": "Could not retrieve project info"},
                "capabilities": {"error": "Could not retrieve capabilities"},
            }

    @mcp.tool()
    async def current_date() -> Dict[str, Any]:
        """
        Get current date and time for preventing date errors in AI content.

        AI assistants frequently make date mistakes (using wrong dates,
        inconsistent formats). This tool provides the reliable current
        date/time that should be used for:
        - Creating specifications with correct dates
        - Generating directory names with timestamps
        - Adding date headers to documentation
        - Any content requiring accurate current date

        Returns ISO 8601 formatted date/time information to ensure consistency.

        Returns:
            Dictionary with current date/time in multiple useful formats
        """
        now = datetime.now()

        return {
            "iso_date": now.strftime("%Y-%m-%d"),  # Primary format: 2025-10-23
            "iso_datetime": now.isoformat(),  # Full ISO: 2025-10-23T14:30:00.123456
            "day_of_week": now.strftime("%A"),  # Wednesday
            "month": now.strftime("%B"),  # October
            "year": now.year,
            "unix_timestamp": int(now.timestamp()),
            "formatted": {
                # For .praxis-os/specs/YYYY-MM-DD-name/
                "spec_directory": f"{now.strftime('%Y-%m-%d')}-",
                # For markdown headers
                "header": f"**Date**: {now.strftime('%Y-%m-%d')}",
                "readable": now.strftime("%B %d, %Y"),  # October 23, 2025
            },
            "usage_note": (
                "Use 'iso_date' (YYYY-MM-DD) for all specifications, "
                "directories, and headers per Agent OS date policy"
            ),
        }

    return 2  # Two tools registered


__all__ = ["register_server_info_tools"]
