#!/usr/bin/env python3
"""
CLI wrapper for Agent OS MCP tools.

Allows Cline to call Agent OS MCP tools via command line
until native streamable-http support is added to Cline.

Usage:
    python mcp_tool_cli.py search_standards '{"query": "testing", "n_results": 5}'
    python mcp_tool_cli.py get_server_info '{}'
"""

import asyncio
import json
import sys
from pathlib import Path

from fastmcp import Client


async def call_tool(tool_name: str, arguments: dict):
    """Call an Agent OS MCP tool and return the result."""
    
    # Read state file to get server URL
    state_file = Path(".agent-os/.mcp_server_state.json")
    
    if not state_file.exists():
        return {
            "error": "MCP server not running",
            "details": "State file not found at .agent-os/.mcp_server_state.json"
        }
    
    state = json.loads(state_file.read_text())
    server_url = state["url"]
    
    try:
        # Connect and call tool
        async with Client(server_url) as client:
            result = await client.call_tool(tool_name, arguments)
            
            # Return result as JSON
            return {
                "success": True,
                "tool": tool_name,
                "result": result.content[0].text if result.content else None
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "tool": tool_name
        }


def main():
    """Main CLI entry point."""
    
    if len(sys.argv) < 3:
        print(json.dumps({
            "error": "Usage: python mcp_tool_cli.py TOOL_NAME ARGUMENTS_JSON"
        }))
        sys.exit(1)
    
    tool_name = sys.argv[1]
    
    try:
        arguments = json.loads(sys.argv[2])
    except json.JSONDecodeError as e:
        print(json.dumps({
            "error": f"Invalid JSON arguments: {e}"
        }))
        sys.exit(1)
    
    # Call the tool
    result = asyncio.run(call_tool(tool_name, arguments))
    
    # Print result as JSON
    print(json.dumps(result, indent=2))
    
    # Exit with error code if failed
    if not result.get("success", False):
        sys.exit(1)


if __name__ == "__main__":
    main()
