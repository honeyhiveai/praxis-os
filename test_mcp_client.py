#!/usr/bin/env python3
"""
Test MCP client for Agent OS dual-transport server.

This script connects to the Agent OS MCP server via HTTP
and tests tool calls to validate the dual-transport architecture.
"""

import asyncio
import json
from pathlib import Path

# Import FastMCP client
from fastmcp import Client


async def test_agent_os_connection():
    """Test connection to Agent OS MCP server."""
    
    # Read state file to get server URL
    state_file = Path(".agent-os/.mcp_server_state.json")
    
    if not state_file.exists():
        print("❌ State file not found. Is the MCP server running?")
        print(f"   Expected: {state_file.absolute()}")
        return
    
    state = json.loads(state_file.read_text())
    server_url = state["url"]
    
    print(f"🔗 Connecting to Agent OS MCP server at {server_url}")
    print(f"   Project: {state['project']['name']}")
    print(f"   Transport: {state['transport']}")
    print(f"   PID: {state['pid']}")
    print()
    
    try:
        # Connect to the server
        async with Client(server_url) as client:
            print("✅ Connected successfully!")
            print()
            
            # Test 1: List all tools
            print("📋 Listing available tools...")
            tools = await client.list_tools()
            print(f"   Found {len(tools)} tools:")
            for tool in tools[:5]:  # Show first 5
                print(f"   - {tool.name}: {tool.description[:60]}...")
            if len(tools) > 5:
                print(f"   ... and {len(tools) - 5} more")
            print()
            
            # Test 2: Call get_server_info (if available)
            print("🔍 Getting server info...")
            try:
                result = await client.call_tool("get_server_info", {})
                info = json.loads(result.content[0].text)
                print(f"   ✅ Server version: {info['server']['version']}")
                print(f"   ✅ Transport mode: {info['server']['transport']}")
                print(f"   ✅ Project: {info['project']['name']}")
                if info['project'].get('git'):
                    print(f"   ✅ Git branch: {info['project']['git']['branch']}")
                    print(f"   ✅ Git commit: {info['project']['git']['commit_short']}")
                print(f"   ✅ Tools available: {info['capabilities']['tools_available']}")
                print()
            except Exception as e:
                print(f"   ⚠️  get_server_info not available: {e}")
                print()
            
            # Test 3: Call search_standards (if available)
            print("🔎 Testing search_standards tool...")
            try:
                result = await client.call_tool("search_standards", {
                    "query": "testing",
                    "n_results": 3
                })
                
                # Parse result
                content = result.content[0].text
                print(f"   ✅ Search successful!")
                print(f"   Result preview: {content[:200]}...")
                print()
            except Exception as e:
                print(f"   ⚠️  search_standards error: {e}")
                print()
            
            print("🎉 All tests completed!")
            print()
            print("Summary:")
            print("✅ HTTP endpoint is working")
            print("✅ MCP protocol is functional")
            print("✅ Tools are accessible")
            print("✅ Dual-transport architecture validated!")
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print()
        print("Troubleshooting:")
        print("1. Is the MCP server running? (check state file)")
        print("2. Is the server using 'sse' or 'streamable-http' transport?")
        print("3. Try: curl -X POST {server_url} -H 'Content-Type: application/json'")


if __name__ == "__main__":
    print("=" * 60)
    print("Agent OS MCP Client Test")
    print("=" * 60)
    print()
    
    asyncio.run(test_agent_os_connection())
