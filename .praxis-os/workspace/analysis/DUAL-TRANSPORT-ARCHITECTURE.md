# Dual Transport Architecture for Multi-Agent Support

## Problem Statement

Multiple agents need access to the same MCP server:
- **Cursor Agent** (primary) - needs stdio for IDE integration
- **Sub-agents** (Cline, Aider, custom agents) - need HTTP for remote access
- **Multiple projects** - each with its own prAxIs OS instance
- **Port conflicts** - can't all use the same port

## Solution: Dual Transport with Dynamic Ports

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Project A: /Users/josh/project-a/                          │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Cursor Agent                                          │  │
│  │  - Launches: python -m mcp_server                     │  │
│  │  - Uses: stdio transport (for IDE integration)       │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                  │
│                           ├─── stdio (JSON-RPC) ───>        │
│                           │                                  │
│  ┌────────────────────────▼─────────────────────────────┐  │
│  │ MCP Server (DUAL MODE)                               │  │
│  │  - Thread 1: stdio transport (main thread)           │  │
│  │  - Thread 2: HTTP on port 4242 (background)          │  │
│  │  - RAG Engine (project-specific)                     │  │
│  │  - File Watchers (.praxis-os/standards/, etc.)        │  │
│  │                                                       │  │
│  │  Writes: .praxis-os/.mcp_server_state.json            │  │
│  │    {                                                  │  │
│  │      "port": 4242,                                    │  │
│  │      "url": "http://127.0.0.1:4242/mcp"              │  │
│  │    }                                                  │  │
│  └────────────────────────┬─────────────────────────────┘  │
│                           │                                  │
│                           ├─── HTTP (streamable) ───>       │
│                           │                                  │
│  ┌──────────────────┬────▼────────┬────────────────────┐  │
│  │ Cline Agent      │ Aider Agent │ Custom Sub-Agent   │  │
│  │  Reads state file│  Reads file │  Reads file        │  │
│  │  Connects to     │  Connects   │  Connects          │  │
│  │  :4242/mcp       │  to :4242   │  to :4242          │  │
│  └──────────────────┴─────────────┴────────────────────┘  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Project B: /Users/josh/project-b/  (Different window!)     │
│                                                              │
│  Cursor Agent → MCP Server (DUAL MODE)                      │
│                 - Port 4243 (4242 was taken!)               │
│                 - Writes: .praxis-os/.mcp_server_state.json  │
│                   { "port": 4243, ... }                     │
│                                                              │
│  Sub-agents read their own .praxis-os/.mcp_server_state.json │
│  and connect to port 4243                                   │
└─────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. Port Manager (`port_manager.py`)

```python
port_manager = PortManager(base_path)

# Find available port (try 4242, then 4243, 4244, etc.)
port = port_manager.find_available_port(preferred_port=4242)

# Write state file for sub-agents
port_manager.write_state(port, host="127.0.0.1", path="/mcp")
# Creates: .praxis-os/.mcp_server_state.json

# Sub-agents read it
state = PortManager.read_state(base_path)
# Returns: {"port": 4242, "url": "http://127.0.0.1:4242/mcp", ...}
```

### 2. Dual Transport Server (`__main__.py`)

**Auto-detects mode:**
- Non-interactive (launched by Cursor) → **dual mode** (stdio + HTTP)
- Interactive terminal → **HTTP only**

**Dual mode implementation:**
```python
# Start HTTP in background thread
http_thread = run_http_server_background(mcp, host, port, path)

# Run stdio in main thread (for Cursor)
mcp.run(transport="stdio")
```

### 3. Cursor Configuration (`.cursor/mcp.json`)

```json
{
  "mcpServers": {
    "agent-os-rag": {
      "command": "${workspaceFolder}/.praxis-os/venv/bin/python",
      "args": ["-m", "mcp_server"],
      "transport": "stdio",
      "autoApprove": ["search_standards", "..."]
    }
  }
}
```

**Key change:** Only `stdio` transport, no HTTP config needed for Cursor!

### 4. Sub-Agent Discovery (`sub_agents/mcp_client_example.py`)

```python
# Sub-agent discovers the server
client = SubAgentMCPClient(project_root)
config = client.get_connection_config()

# Returns:
# {
#   "transport": "streamable-http",
#   "url": "http://127.0.0.1:4242/mcp",
#   "port": 4242,
#   ...
# }

# Sub-agent connects to that URL
```

## Port Conflict Resolution

### Scenario: Multiple Cursor Windows

```
Window 1 (project-a):
  1. Cursor launches mcp_server
  2. Port manager tries 4242 → ✅ Available
  3. Writes state: {"port": 4242}
  4. Server runs on 4242

Window 2 (project-b):
  1. Cursor launches mcp_server
  2. Port manager tries 4242 → ❌ In use
  3. Port manager tries 4243 → ✅ Available
  4. Writes state: {"port": 4243}
  5. Server runs on 4243

Each project's sub-agents read their own state file!
```

## Benefits

✅ **No port conflicts** - Dynamic allocation per project  
✅ **Cursor integration** - Works seamlessly with stdio  
✅ **Multi-agent support** - Sub-agents connect via HTTP  
✅ **Project isolation** - Each project has its own server + RAG + file watchers  
✅ **Simple discovery** - State file makes it easy for sub-agents  
✅ **Zero configuration** - Works automatically  

## State File Format

**Location:** `.praxis-os/.mcp_server_state.json`

```json
{
  "port": 4242,
  "host": "127.0.0.1",
  "path": "/mcp",
  "url": "http://127.0.0.1:4242/mcp",
  "transport": "streamable-http"
}
```

This file is:
- ✅ Written by server on startup
- ✅ Read by sub-agents for discovery
- ✅ Cleaned up on server shutdown
- ✅ Gitignored (project-specific runtime state)

## Migration Path

1. **Replace `__main__.py`** with dual-transport version
2. **Add `port_manager.py`** module
3. **Update `.cursor/mcp.json`** to use stdio only
4. **Add `.mcp_server_state.json` to `.gitignore`**
5. **Update sub-agents** to use discovery client

## Testing

```bash
# Terminal 1: Start server (will use HTTP-only mode)
cd /path/to/project
.praxis-os/venv/bin/python -m mcp_server

# Terminal 2: Discover server
cd /path/to/project
python -m mcp_server.sub_agents.mcp_client_example

# Output:
# ✅ MCP Server found!
# {
#   "transport": "streamable-http",
#   "url": "http://127.0.0.1:4242/mcp",
#   ...
# }
```

## Future Enhancements

- **Health checks** - Sub-agents can ping server before connecting
- **Reconnection** - Auto-reconnect if server restarts on different port
- **Remote access** - Expose via ngrok/cloudflare for remote agents
- **Multi-server** - Sub-agents could connect to multiple MCP servers

