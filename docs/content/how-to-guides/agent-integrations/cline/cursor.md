---
sidebar_position: 5
doc_type: how-to
---

# Cline in Cursor Integration (Secondary)

Configure Cline to connect to Cursor's MCP server as a secondary agent via HTTP.

## Prerequisites

- ✅ **Cursor configured as primary agent** (see [cursor.md](./cursor.md))
- ✅ Cursor's MCP server running
- ✅ Cline extension installed in Cursor
- ✅ `.praxis-os/` directory exists

## Overview

In this setup:
- **Cursor** = Primary agent (owns MCP server)
- **Cline** = Secondary agent (connects to Cursor's MCP via HTTP)

**Use cases:**
- Multi-agent workflow (Cursor for main dev, Cline for specialized tasks)
- Testing different LLM models on same tools
- Specialized agent for specific operations

## Architecture

```
Cursor (Primary)
    ├─ Runs MCP server (native connection)
    └─ Exposes HTTP endpoint: http://localhost:8765
        └─ Cline (Secondary) connects here
```

**Key difference from primary**: Cline doesn't start/stop the MCP server - it just connects to Cursor's.

## Step 1: Enable Dual Transport Mode in Cursor's MCP Server

Edit `.cursor/mcp.json` to use dual transport mode:

```json
{
  "mcpServers": {
    "praxis-os-rag": {
      "command": "${workspaceFolder}/.praxis-os/venv/bin/python",
      "args": [
        "-m",
        "mcp_server",
        "--transport",
        "dual",
        "--log-level",
        "INFO"
      ],
      "env": {
        "PROJECT_ROOT": "${workspaceFolder}",
        "PYTHONPATH": "${workspaceFolder}/.praxis-os",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

**What this does:**
- `--transport dual` → Enables both stdio (IDE) + HTTP (sub-agents)
- Port automatically allocated (4242-5242 range)
- Port written to `.praxis-os/.mcp_server_state.json` for secondary agents

**Windows users**: Change `venv/bin/python` to `venv\Scripts\python.exe`

## Step 2: Restart Cursor

```bash
# Close and reopen Cursor (Cmd+Q / Alt+F4)
```

After restart:
- Cursor starts MCP server with dual transport enabled
- HTTP endpoint automatically allocated (check `.praxis-os/.mcp_server_state.json`)
- Cursor continues working normally (native stdio MCP connection)

**Verify HTTP is running**:
```bash
# Read port from state file
PORT=$(cat .praxis-os/.mcp_server_state.json | grep -o '"port": [0-9]*' | grep -o '[0-9]*')
echo "HTTP endpoint: http://127.0.0.1:${PORT}/mcp"

# Or manually check state file
cat .praxis-os/.mcp_server_state.json
```

## Step 3: Install Cline Extension in Cursor

```bash
# Via Cursor extensions marketplace
# Search "Cline" and install
```

**Note**: Cline can run in both VS Code and Cursor. This guide is for Cline **inside Cursor**.

## Step 4: Configure Cline to Connect via HTTP

### Option A: Automatic Setup (Helper Script)

Copy and run the helper script:

```bash
# Copy helper script (if not already present)
cp .praxis-os/scripts/update-cline-mcp.py .praxis-os/bin/
chmod +x .praxis-os/bin/update-cline-mcp.py

# Run helper (reads MCP server port from state file)
python .praxis-os/bin/update-cline-mcp.py
```

The script will:
- Read the dynamically allocated port from `.praxis-os/.mcp_server_state.json`
- Find Cline's config file automatically (Cursor/VS Code locations)
- Update configuration with correct HTTP endpoint (`http://127.0.0.1:PORT/mcp`)
- Use `streamableHttp` transport type (required for MCP Streamable HTTP protocol)

### Option B: Manual Setup

Open Cline settings in Cursor:

1. Click Cline icon in sidebar
2. Click settings/gear icon
3. Navigate to "MCP Servers"
4. Add HTTP connection:

```json
{
  "agent-os-rag": {
    "type": "streamableHttp",
    "url": "http://127.0.0.1:4242/mcp",
    "alwaysAllow": [
      "search_standards",
      "get_current_phase",
      "get_workflow_state",
      "get_server_info"
    ]
  }
}
```

**Important**:
- Must specify `"type": "streamableHttp"` explicitly!
- Replace `4242` with actual port from `.praxis-os/.mcp_server_state.json`
- Use `127.0.0.1` (not `localhost`) for consistency
- Include `/mcp` path in URL

## Step 5: Reload Cursor Window

```bash
# Command Palette (Cmd+Shift+P)
> Developer: Reload Window
```

After reload:
- Cursor: Connected to MCP server natively ✅
- Cline: Connected to MCP server via HTTP ✅
- Both agents share the same MCP server instance

## Step 6: Validate Multi-Agent Setup

### Test 1: Cursor Connection (Primary)

In Cursor chat:
```
"Use search_standards to query: orientation bootstrap"
```

**Expected**: Native MCP connection works

### Test 2: Cline Connection (Secondary)

In Cline panel:
```
"Use search_standards to query: python testing patterns"
```

**Expected**: HTTP connection works, returns same results as Cursor

### Test 3: Shared State

1. In Cursor: Start a workflow
2. In Cline: Query workflow state

Both agents should see the same workflow state (shared MCP server).

## Differences from Primary Cline

| Aspect | Cline (Primary) | Cline (Secondary) |
|--------|----------------|-------------------|
| **MCP Server** | Cline starts/stops | Cursor starts/stops |
| **Connection** | Direct/STDIO | HTTP (Streamable HTTP) |
| **Port** | N/A | Dynamic (4242-5242 range, from state file) |
| **Independence** | Standalone | Depends on Cursor running |
| **Performance** | Slightly faster | Minimal HTTP overhead (~10-50ms) |
| **Restart** | Reload Cline | Reload Cursor + Cline |
| **Configuration** | Manual setup | Helper script reads state file |

## Troubleshooting

### Cline Can't Connect to HTTP Endpoint

**Symptom**: "Failed to connect to MCP server" in Cline

**Check**:
```bash
# Read port from state file
PORT=$(cat .praxis-os/.mcp_server_state.json | grep -o '"port": [0-9]*' | grep -o '[0-9]*')
echo "Testing: http://127.0.0.1:${PORT}/mcp"

# Verify HTTP endpoint is running
curl http://127.0.0.1:${PORT}/mcp

# Check Cursor's MCP server logs
# (View → Output → select "Cursor MCP" or similar)
```

**Solutions**:
- Verify Cursor is running and MCP server started
- Check port allocation: `cat .praxis-os/.mcp_server_state.json`
- Verify port not in use: `lsof -i :${PORT}` (Mac/Linux) or `netstat -ano | findstr :${PORT}` (Windows)
- Ensure using `--transport dual` (not `--http`)
- Restart Cursor to restart MCP server with dual transport

### Port Already in Use

**Symptom**: MCP server fails to start or logs show port conflict

**Check**:
```bash
# Server automatically tries ports 4242-5242
# Check what port was allocated
cat .praxis-os/.mcp_server_state.json

# See what's using the allocated port
PORT=$(cat .praxis-os/.mcp_server_state.json | grep -o '"port": [0-9]*' | grep -o '[0-9]*')
lsof -i :${PORT}  # Mac/Linux
netstat -ano | findstr :${PORT}  # Windows
```

**Solutions**:
- Server automatically finds next available port (no manual config needed)
- If all ports 4242-5242 are in use, close other MCP server instances
- Check for stale processes: `ps aux | grep mcp_server`
- Restart Cursor to retry port allocation

### Both Agents See Different State

**Symptom**: Cursor and Cline show different workflow states or search results

**Root cause**: They're not connected to the same MCP server instance

**Check**:
```bash
# Count Python processes running mcp_server
ps aux | grep mcp_server
# Should see only ONE process
```

**Solutions**:
- Only one agent should be PRIMARY (controlling MCP server)
- If Cline also running as primary elsewhere, close that instance
- Restart Cursor to ensure single MCP server instance

### Slow Performance in Cline

**Symptom**: Cline queries much slower than Cursor

**Expected behavior**: HTTP adds minimal latency (~10-50ms per request)

**If significantly slower**:
- Check network/firewall: Ensure localhost not blocked
- Verify Cursor's MCP server healthy (test via Cursor first)
- Check system resources (CPU, RAM)
- Get port from state file and test: `PORT=$(cat .praxis-os/.mcp_server_state.json | grep -o '"port": [0-9]*' | grep -o '[0-9]*') && curl http://127.0.0.1:${PORT}/mcp` (should be instant)

### Cursor Works, Cline Doesn't

**Symptom**: Cursor can use tools, Cline cannot

**Check**:
```bash
# Get port from state file
PORT=$(cat .praxis-os/.mcp_server_state.json | grep -o '"port": [0-9]*' | grep -o '[0-9]*')

# Verify Cline's HTTP config
cat ~/Library/Application\ Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json | grep -A 5 agent-os-rag

# Test HTTP endpoint directly
curl -X POST http://127.0.0.1:${PORT}/mcp -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

**Solutions**:
- Ensure dual transport enabled in Cursor's mcp.json (`--transport dual`)
- Verify URL in Cline config matches state file: `http://127.0.0.1:${PORT}/mcp`
- Must include `/mcp` path in URL
- Check Cline output panel for connection errors
- Run helper script: `python .praxis-os/bin/update-cline-mcp.py`
- Restart both Cursor and reload Cline

## When to Use Secondary vs Primary Cline

### Use Secondary (Cline in Cursor) When:
- ✅ Already using Cursor as main IDE
- ✅ Want specialized agent for specific tasks
- ✅ Need different LLM model for comparison
- ✅ Multi-agent workflow (handoff between agents)

### Use Primary (Cline in VS Code) When:
- ✅ VS Code is your main IDE
- ✅ Don't use Cursor
- ✅ Want Cline to fully control MCP server
- ✅ Single-agent workflow

## Multi-Agent Workflow Patterns

### Pattern 1: Handoff

1. **Cursor**: Plan architecture, create spec
2. **Cline**: Implement specific module
3. **Cursor**: Review, integrate, test

### Pattern 2: Parallel

1. **Cursor**: Work on frontend
2. **Cline**: Work on backend (same project, shared tools)

### Pattern 3: Specialized

1. **Cursor**: General development
2. **Cline**: Browser testing via `pos_browser` tool
3. **Cursor**: Process results

## Security Considerations

### HTTP Endpoint Exposure

The HTTP endpoint (`http://127.0.0.1:PORT/mcp`) is:
- **Local only** - Not accessible from network (127.0.0.1 binding)
- **No authentication** - Anyone on localhost can connect
- **Same machine** - Both agents must run on same computer
- **Dynamic port** - Port allocated automatically (4242-5242 range)

**Risk**: Other local processes can connect to your MCP server

**Mitigation**:
- Only enable dual transport when using secondary agents (use `stdio` mode otherwise)
- Port binding restricted to 127.0.0.1 (not 0.0.0.0)
- Stop MCP server when not in use (close Cursor)

### Shared Workflow State

Both agents share workflow state. This means:
- Cline can modify Cursor's workflows
- Cursor can see Cline's workflows
- Coordinate to avoid conflicts

**Best practice**: Designate one agent as "workflow owner"

## Next Steps

✅ **Multi-agent setup complete!**

Now:
1. **Test both agents**: Verify both can search_standards
2. **Define roles**: Decide which agent does what
3. **Coordinate**: Use shared workflow state effectively
4. **Iterate**: Refine multi-agent workflow based on experience

See also:
- [Cursor Integration (Primary)](./cursor.md)
- [Cline in VS Code (Primary)](./cline-vscode.md)
- [Understanding Workflows](../../tutorials/understanding-praxis-os-workflows.md)

