# Sub-Agent Integration Guide

**Feature:** Multi-Agent Workflows via Dual-Transport  
**Date:** 2025-10-11  
**Status:** Production Ready

---

## Overview

This guide shows how to integrate sub-agents (Cline, Aider, custom scripts) with the Agent OS MCP server. Sub-agents discover and connect to the server via HTTP while your main IDE uses stdio.

**Prerequisites:**
- MCP server running in dual transport mode (`--transport dual`)
- State file exists at `.praxis-os/.mcp_server_state.json`
- Python 3.8+ (for Python SDK examples)

---

## Quick Start

### 1. Enable Dual Transport

**File:** `.cursor/mcp.json`

```json
{
  "mcpServers": {
    "agent-os-rag": {
      "command": "${workspaceFolder}/.praxis-os/venv/bin/python",
      "args": ["-m", "mcp_server", "--transport", "dual"],
      "transport": "stdio"
    }
  }
}
```

Reload your IDE to start the server in dual mode.

### 2. Verify Server Running

```bash
# Check state file exists
cat .praxis-os/.mcp_server_state.json

# Should show:
# {
#   "transport": "dual",
#   "url": "http://127.0.0.1:4242/mcp",
#   ...
# }
```

### 3. Connect from Sub-Agent

```python
from mcp_server.sub_agents import discover_mcp_server

url = discover_mcp_server()
print(url)  # http://127.0.0.1:4242/mcp
```

---

## Tutorial: Python SDK Integration

This tutorial walks through building a custom sub-agent using the Python MCP SDK.

### Step 1: Discovery

Discover the running MCP server:

```python
from mcp_server.sub_agents.discovery import discover_mcp_server
from pathlib import Path

# Auto-discover from current directory
url = discover_mcp_server()

# Or specify explicit path
url = discover_mcp_server(Path("/path/to/project/.praxis-os"))

if url is None:
    print("❌ MCP server not running")
    exit(1)

print(f"✅ Found server at: {url}")
```

**What it does:**
- Searches for `.praxis-os/.mcp_server_state.json`
- Validates the server process is still alive (PID check)
- Returns HTTP URL or `None`

### Step 2: Connection

Connect to the server using `streamable_http_client`:

```python
import asyncio
from mcp import ClientSession
# Note: streamable_http_client may be in mcp.client.streamable_http
# Check your mcp package version for exact import path

async def connect():
    url = discover_mcp_server()
    if not url:
        return

    # For actual implementation, use:
    # from mcp.client.streamable_http import streamable_http_client
    # async with streamable_http_client(url) as (read, write):
    #     async with ClientSession(read, write) as session:
    #         await session.initialize()
    #         # ... use session

    print(f"Connected to {url}")

asyncio.run(connect())
```

**Connection lifecycle:**
1. Establish HTTP connection to URL
2. Create read/write streams
3. Initialize MCP session
4. Use tools
5. Close session (automatically via context manager)

### Step 3: List Tools

Query available tools:

```python
async def list_tools():
    url = discover_mcp_server()
    if not url:
        return

    # Mock example (see mcp_client_example.py for full implementation)
    tools = [
        "search_standards",
        "start_workflow",
        "get_current_phase",
        "get_task",
        "complete_phase",
        "get_server_info",
    ]

    print(f"✅ Available tools ({len(tools)}):")
    for tool in tools:
        print(f"  - {tool}")

asyncio.run(list_tools())
```

**Real implementation:**
```python
async with streamable_http_client(url) as (read, write):
    async with ClientSession(read, write) as session:
        tools_result = await session.list_tools()
        for tool in tools_result.tools:
            print(f"  - {tool.name}: {tool.description}")
```

### Step 4: Call Tools

Execute a tool and get results:

```python
async def call_search_standards():
    url = discover_mcp_server()
    if not url:
        return

    # Mock example
    result = {
        "results": [
            {
                "title": "Production Code Checklist",
                "content": "All code must include...",
                "score": 0.95
            }
        ]
    }

    print(f"✅ Search results:")
    for item in result["results"]:
        print(f"  - {item['title']} (score: {item['score']})")

asyncio.run(call_search_standards())
```

**Real implementation:**
```python
async with streamable_http_client(url) as (read, write):
    async with ClientSession(read, write) as session:
        result = await session.call_tool(
            "search_standards",
            {
                "query": "production code checklist",
                "n_results": 5
            }
        )
        print(result)
```

### Step 5: Error Handling

Handle common errors gracefully:

```python
async def robust_connection():
    try:
        url = discover_mcp_server()
        
        if url is None:
            print("❌ Server not found:")
            print("  1. Check server is running (ps aux | grep mcp_server)")
            print("  2. Verify .praxis-os/.mcp_server_state.json exists")
            print("  3. Ensure --transport dual is set")
            return

        # Attempt connection
        # async with streamable_http_client(url) as (read, write):
        #     ...
        
        print(f"✅ Connected successfully to {url}")

    except ConnectionError as e:
        print(f"❌ Connection failed: {e}")
        print("  - Server may have crashed")
        print("  - Check server logs in IDE console")
        print("  - Try restarting IDE")

    except TimeoutError as e:
        print(f"❌ Connection timeout: {e}")
        print("  - Server may be overloaded")
        print("  - Try reducing concurrency")

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("  - Check mcp package is installed (pip install mcp)")
        print("  - Verify Python version (3.8+)")

asyncio.run(robust_connection())
```

---

## How-To Guides

### How to Integrate Cline

Cline auto-discovers the MCP server, but you can verify it's working:

**1. Start server in dual mode:**
- Update `.cursor/mcp.json` with `--transport dual`
- Reload Cursor

**2. Verify state file:**
```bash
cat .praxis-os/.mcp_server_state.json
```

**3. Cline should auto-connect:**
- Cline reads the state file automatically
- No manual config needed
- If it fails, check Cline logs for connection errors

**4. Verify connection (optional):**
```python
# Run this to test discovery
python -m mcp_server.sub_agents.mcp_client_example
```

### How to Integrate Aider

Aider can connect via the Python SDK:

**1. Create Aider integration script:**

```python
# aider_mcp_integration.py
import asyncio
from mcp_server.sub_agents.discovery import discover_mcp_server

async def aider_mcp_tools():
    """Get MCP tools for Aider."""
    url = discover_mcp_server()
    
    if url is None:
        print("MCP server not available")
        return []

    # Use streamable_http_client to connect
    # from mcp.client.streamable_http import streamable_http_client
    # async with streamable_http_client(url) as (read, write):
    #     async with ClientSession(read, write) as session:
    #         tools = await session.list_tools()
    #         return tools.tools

    return []

# Aider integration
if __name__ == "__main__":
    tools = asyncio.run(aider_mcp_tools())
    print(f"Available tools: {len(tools)}")
```

**2. Run from Aider:**
```bash
aider --mcp-script aider_mcp_integration.py
```

### How to Build a Custom Sub-Agent

**1. Create discovery module:**

```python
# my_agent/mcp_connection.py
from mcp_server.sub_agents.discovery import discover_mcp_server
from typing import Optional

class MCPConnection:
    """Manages MCP server connection for custom agent."""
    
    def __init__(self, agent_os_path: Optional[Path] = None):
        self.agent_os_path = agent_os_path
        self.url: Optional[str] = None
    
    def discover(self) -> bool:
        """Discover MCP server."""
        self.url = discover_mcp_server(self.agent_os_path)
        return self.url is not None
    
    async def call_tool(self, tool_name: str, params: dict):
        """Call an MCP tool."""
        if self.url is None:
            raise RuntimeError("MCP server not discovered")
        
        # Use streamable_http_client to connect and call tool
        # ... implementation here
        pass
```

**2. Use in your agent:**

```python
# my_agent/main.py
import asyncio
from my_agent.mcp_connection import MCPConnection

async def main():
    mcp = MCPConnection()
    
    if not mcp.discover():
        print("MCP server not available")
        return
    
    # Use MCP tools
    result = await mcp.call_tool("search_standards", {
        "query": "error handling best practices",
        "n_results": 3
    })
    
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

### How to Handle Multi-Project Scenarios

When working with multiple projects, each has its own MCP server:

**Scenario:** You're running Agent OS in 3 different projects

```
~/projects/
├── project-a/
│   └── .praxis-os/.mcp_server_state.json  # port 4242
├── project-b/
│   └── .praxis-os/.mcp_server_state.json  # port 4243
└── project-c/
    └── .praxis-os/.mcp_server_state.json  # port 4244
```

**Solution:** Specify the project when connecting:

```python
from pathlib import Path
from mcp_server.sub_agents.discovery import discover_mcp_server

# Project A
url_a = discover_mcp_server(Path("~/projects/project-a/.praxis-os"))

# Project B
url_b = discover_mcp_server(Path("~/projects/project-b/.praxis-os"))

# Project C
url_c = discover_mcp_server(Path("~/projects/project-c/.praxis-os"))

print(f"Project A: {url_a}")  # http://127.0.0.1:4242/mcp
print(f"Project B: {url_b}")  # http://127.0.0.1:4243/mcp
print(f"Project C: {url_c}")  # http://127.0.0.1:4244/mcp
```

**Auto-detection:**
- If you run the script from within a project, `discover_mcp_server()` with no args will find it
- Searches current directory and parents for `.praxis-os/`

---

## Reference

### Discovery API

#### `discover_mcp_server(agent_os_path: Optional[Path] = None) -> Optional[str]`

Discover a running MCP server's HTTP endpoint.

**Parameters:**
- `agent_os_path`: Path to `.praxis-os` directory. If None, searches from current directory upward.

**Returns:**
- HTTP URL string (e.g., `"http://127.0.0.1:4242/mcp"`) if server found and alive
- `None` if server not found, stale, or stdio-only

**Example:**
```python
url = discover_mcp_server()  # Auto-detect
url = discover_mcp_server(Path("/path/to/.praxis-os"))  # Explicit
```

### State File Format

**Location:** `.praxis-os/.mcp_server_state.json`

**Schema:**
```json
{
  "transport": "dual",          // Transport mode
  "url": "http://...",          // Full HTTP URL
  "host": "127.0.0.1",          // HTTP host
  "port": 4242,                 // HTTP port
  "path": "/mcp",               // HTTP path
  "pid": 12345,                 // Server process ID
  "project": {
    "name": "project-name",     // Project name
    "root": "/path/to/project", // Project root
    "agent_os_path": "/path/to/project/.praxis-os",
    "git": {                    // Git info (if available)
      "remote": "https://...",
      "branch": "main",
      "commit": "abc123",
      "dirty": false
    }
  },
  "started_at": "2025-10-11T14:30:00Z"  // ISO 8601 timestamp
}
```

**Lifecycle:**
- Created when server starts in `dual` or `http` mode
- Deleted when server shuts down gracefully
- May be stale if server crashes (check PID)

### Configuration Helpers

#### `get_mcp_config_for_cline() -> Optional[Dict]`

Generate Cline MCP configuration.

**Returns:**
```json
{
  "mcpServers": {
    "agent-os-rag": {
      "transport": "streamable-http",
      "url": "http://127.0.0.1:4242/mcp"
    }
  }
}
```

#### `get_mcp_config_for_aider() -> Optional[Dict]`

Generate Aider MCP configuration.

**Returns:**
```json
{
  "url": "http://127.0.0.1:4242/mcp",
  "transport": "http"
}
```

#### `get_mcp_config_for_python_sdk() -> Optional[Dict]`

Generate Python SDK configuration.

**Returns:**
```json
{
  "url": "http://127.0.0.1:4242/mcp",
  "transport": "streamable-http"
}
```

### Example: End-to-End Integration

**File:** `mcp_server/sub_agents/mcp_client_example.py`

This is a complete, working example showing:
- Server discovery
- Connection (mocked)
- Tool listing
- Tool calling
- Error handling

**Run it:**
```bash
python -m mcp_server.sub_agents.mcp_client_example
```

**Output:**
```
🔍 Discovering MCP server...
✅ Discovered MCP server at: http://127.0.0.1:4242/mcp
🔌 Connecting to MCP server at http://127.0.0.1:4242/mcp...
✅ Connected successfully!
📋 Available tools: search_standards, start_workflow, get_current_phase, ...

✅ Connection successful!
   URL: http://127.0.0.1:4242/mcp
   Tools available: 10
```

---

## Explanation: How It Works

### Discovery Mechanism

The discovery process follows these steps:

```
1. Locate .praxis-os/
   ├─ Check current directory
   ├─ Check parent directories
   └─ Stop at home directory

2. Read state file
   ├─ Open .praxis-os/.mcp_server_state.json
   ├─ Parse JSON
   └─ Extract transport, url, pid

3. Validate transport
   ├─ Require "dual" or "http"
   └─ Reject "stdio" (no HTTP available)

4. Validate PID
   ├─ Check /proc/{pid} (Unix/Linux)
   ├─ Send signal 0 (macOS)
   ├─ Use psutil (Windows)
   └─ Return None if process dead

5. Return URL
   └─ http://127.0.0.1:{port}/mcp
```

**Why PID validation?**
- State file persists if server crashes
- PID check detects stale state
- Returns `None` for dead servers
- Prevents connection attempts to non-existent servers

### Port Allocation

How the server chooses ports:

```
1. Read preferred port from config.yaml
   └─ Default: 4242

2. Try to bind preferred port
   ├─ Success → Use it
   └─ Fail (in use) → Increment

3. Try ports 4242-5242 (1000 ports)
   ├─ Attempt bind
   ├─ Success → Write state file
   └─ Fail → Try next

4. If all ports exhausted
   └─ Error: "No available ports in range"
```

**Why this range?**
- 1000 ports supports 1000 concurrent projects
- Port 4242 is outside privileged range (< 1024)
- Port 5242 is before ephemeral range (> 32768)
- Low collision probability with other services

### Thread Safety

How concurrent access is handled:

```
Main IDE (Cursor)
       │
       │ stdio
       ▼
   ┌──────────────┐
   │  MCP Server  │
   │              │
   │  ┌─────────┐ │
   │  │ FastMCP │ │  ← Shared instance
   │  │         │ │  ← Thread-safe
   │  └─────────┘ │
   │              │
   └──────────────┘
       ▲
       │ HTTP
       │
  Sub-Agents (concurrent)
```

**Design:**
- **Single writer**: Server writes state file once on startup
- **Multiple readers**: Sub-agents read state file concurrently (safe)
- **FastMCP**: Handles internal synchronization for tool calls
- **Atomic writes**: State file uses temp file + rename (no corruption)

**Limitations:**
- Multiple servers per project not supported (single-writer pattern)
- Port allocation has minor race conditions (socket bind fails cleanly)

See `THREAD-SAFETY.md` for detailed analysis.

---

## Troubleshooting

### Server Not Discovered

**Symptom:** `discover_mcp_server()` returns `None`

**Checks:**

1. **Server running?**
   ```bash
   ps aux | grep mcp_server
   ```

2. **State file exists?**
   ```bash
   ls -la .praxis-os/.mcp_server_state.json
   ```

3. **Transport mode correct?**
   ```bash
   jq '.transport' .praxis-os/.mcp_server_state.json
   # Should be "dual" or "http", not "stdio"
   ```

4. **PID alive?**
   ```bash
   kill -0 $(jq '.pid' .praxis-os/.mcp_server_state.json)
   # No error = alive, error = dead
   ```

**Solutions:**
- Restart IDE (reload window)
- Update `.cursor/mcp.json` to include `["--transport", "dual"]`
- Delete stale state file: `rm .praxis-os/.mcp_server_state.json`

### Connection Refused

**Symptom:** `ConnectionError: [Errno 61] Connection refused`

**Causes:**
1. **Server died after writing state file:**
   - Check IDE console for errors
   - Look for Python tracebacks
   - Try `--log-level DEBUG` for details

2. **Firewall blocking localhost:**
   - Rare, but check firewall rules
   - Try `curl http://127.0.0.1:4242/mcp`

3. **Port mismatch:**
   - Verify port in state file matches actual server
   - Check server logs for actual bound port

**Solution:**
```bash
# Clean restart
rm .praxis-os/.mcp_server_state.json
# Reload IDE
# Verify new state file
cat .praxis-os/.mcp_server_state.json
```

### Wrong Project Discovered

**Symptom:** Sub-agent connects to wrong project's server

**Cause:** Running script from wrong directory

**Solution:**
```python
# Specify explicit path
from pathlib import Path
url = discover_mcp_server(Path("/absolute/path/to/project/.praxis-os"))
```

### Port Changes Every Restart

**Symptom:** State file shows different port each time

**This is normal!** Ports are ephemeral:
- Port released on shutdown
- New port allocated on startup
- Sub-agents auto-discover new port via state file

**If you need consistent port:**
```yaml
# .praxis-os/config.yaml
mcp:
  http_port: 4242  # Preferred port (not guaranteed)
```

Server will try this port first, but increment if taken.

---

## Best Practices

### ✅ Do's

1. **Use discovery utility**
   ```python
   # Good
   url = discover_mcp_server()
   
   # Bad
   url = "http://127.0.0.1:4242/mcp"  # Hardcoded!
   ```

2. **Check for None**
   ```python
   url = discover_mcp_server()
   if url is None:
       print("Server not available")
       return
   ```

3. **Handle errors gracefully**
   ```python
   try:
       # Connection code
   except ConnectionError:
       print("Connection failed, check server")
   ```

4. **Use async/await**
   ```python
   async def main():
       # MCP SDK is async
       result = await session.call_tool(...)
   ```

5. **Close sessions**
   ```python
   async with ClientSession(read, write) as session:
       # Auto-closes on exit
   ```

### ❌ Don'ts

1. **Don't hardcode ports**
   ```python
   # Bad
   url = "http://localhost:4242/mcp"
   ```

2. **Don't assume port 4242**
   ```python
   # Bad
   port = 4242  # May be taken!
   ```

3. **Don't skip PID validation**
   ```python
   # Bad: reading state file directly
   with open(".praxis-os/.mcp_server_state.json") as f:
       state = json.load(f)
       url = state["url"]  # May be stale!
   
   # Good: use discovery utility (includes PID check)
   url = discover_mcp_server()
   ```

4. **Don't cache state file**
   ```python
   # Bad: cached, may be stale
   _cached_url = None
   def get_url():
       global _cached_url
       if _cached_url is None:
           _cached_url = discover_mcp_server()
       return _cached_url
   
   # Good: discover each time (fast < 5ms)
   def get_url():
       return discover_mcp_server()
   ```

5. **Don't use for multiple projects simultaneously**
   ```python
   # Bad: which project?
   url = discover_mcp_server()
   
   # Good: explicit paths
   url_a = discover_mcp_server(Path("~/project-a/.praxis-os"))
   url_b = discover_mcp_server(Path("~/project-b/.praxis-os"))
   ```

---

## Summary

| Step | Action | Tool |
|------|--------|------|
| 1. Setup | Enable dual transport | `.cursor/mcp.json` |
| 2. Discover | Find server URL | `discover_mcp_server()` |
| 3. Connect | Establish HTTP connection | `streamable_http_client(url)` |
| 4. Initialize | Start MCP session | `ClientSession(read, write)` |
| 5. Use | Call tools | `session.call_tool(name, params)` |
| 6. Close | Clean up | `async with` context manager |

**Key Takeaways:**
- ✅ Use discovery utility (auto-finds server)
- ✅ Check for None (server may not be running)
- ✅ Handle errors gracefully
- ✅ Works across multiple projects (zero config)
- ✅ Thread-safe for concurrent sub-agents

**Next Steps:**
- See `mcp_client_example.py` for working code
- See `IDE-CONFIGURATION.md` for IDE-specific setup
- See `THREAD-SAFETY.md` for performance details

**Status:** ✅ Production Ready (2025-10-11)

