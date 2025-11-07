---
sidebar_position: 3
doc_type: how-to
---

# Claude Code in Cursor Integration (Secondary)

Configure Claude Code to connect to Cursor's MCP server as a secondary agent via HTTP.

## Prerequisites

- ✅ **Cursor configured as primary agent** (see [../cursor/](../cursor/))
- ✅ Cursor's MCP server running with HTTP mode
- ✅ Claude Code extension installed in Cursor (if available) OR running externally
- ✅ `.praxis-os/` directory exists

## Overview

In this setup:
- **Cursor** = Primary agent (owns MCP server)
- **Claude Code** = Secondary agent (connects via HTTP)

**Use cases:**
- Multi-agent workflow (Cursor for planning, Claude Code for implementation)
- Testing different approaches with different models
- Specialized agent for specific operations

## Architecture

```
Cursor (Primary)
    ├─ Runs MCP server (native connection)
    └─ Exposes HTTP endpoint: http://127.0.0.1:PORT/mcp (dynamic port)
        └─ Claude Code (Secondary) connects here
```

## Step 1: Enable Dual Transport Mode in Cursor's MCP Server

Edit `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "project-name": {
      "command": "/absolute/path/to/project/.praxis-os/venv/bin/python",
      "args": [
        "-m",
        "ouroboros",
        "--transport",
        "dual",
        "--log-level",
        "INFO"
      ],
      "env": {
        "PROJECT_ROOT": "/absolute/path/to/project",
        "PYTHONPATH": "/absolute/path/to/project/.praxis-os",
        "PYTHONUNBUFFERED": "1"
      },
      "autoApprove": [
        "pos_search_project",
        "pos_workflow",
        "pos_browser",
        "pos_filesystem",
        "get_server_info",
        "current_date"
      ]
    }
  }
}
```

**⚠️ CRITICAL**: Cursor does **NOT** expand `${workspaceFolder}` variables. You must use absolute paths:
- Replace `"project-name"` with your actual project name (e.g., `"python-sdk"`)
- Replace `/absolute/path/to/project/` with your actual project path (e.g., `/Users/josh/src/github.com/honeyhiveai/python-sdk`)

**What this does:**
- `--transport dual` → Enables both stdio (IDE) + HTTP (sub-agents)
- Port automatically allocated (4242-5242 range)
- Port written to `.praxis-os/.mcp_server_state.json` for secondary agents

**Windows**: 
- Use forward slashes or double backslashes: `C:/Users/...` or `C:\\Users\\...`
- Change `venv/bin/python` to `venv\\Scripts\\python.exe`

## Step 2: Restart Cursor

Close and reopen Cursor (Cmd+Q / Alt+F4).

After restart:
- Cursor starts MCP server with dual transport enabled
- HTTP endpoint automatically allocated (check `.praxis-os/.mcp_server_state.json`)
- Cursor works normally (native stdio MCP)

**Verify HTTP**:
```bash
# Read port from state file
PORT=$(cat .praxis-os/.mcp_server_state.json | grep -o '"port": [0-9]*' | grep -o '[0-9]*')
echo "HTTP endpoint: http://127.0.0.1:${PORT}/mcp"

# Or manually check state file
cat .praxis-os/.mcp_server_state.json
```

## Step 3: Configure Claude Code to Use HTTP

### Option A: Automatic Setup (Helper Script - Recommended)

Copy and run the helper script:

```bash
# Copy helper script (if not already present)
cp .praxis-os/scripts/configure-claude-code-mcp.py .praxis-os/bin/
chmod +x .praxis-os/bin/configure-claude-code-mcp.py

# Run helper (reads MCP server port from state file)
python .praxis-os/bin/configure-claude-code-mcp.py
```

The script will:
- Read the dynamically allocated port from `.praxis-os/.mcp_server_state.json`
- Create/update `.mcp.json` in project root (if needed)
- Enable project MCP servers in Claude Code settings
- Configure VS Code workspace settings if needed
- Use `streamableHttp` transport type (required for MCP Streamable HTTP protocol)

### Option B: Manual Setup

#### If Claude Code Extension in Cursor

In Cursor settings or Claude Code config:
```json
{
  "claude-code.mcpServers": {
    "praxis-os": {
      "type": "streamableHttp",
      "url": "http://localhost:8765",
      "transport": "http"
    }
  }
}
```

#### If Claude Code CLI (External)

Edit `~/.config/claude-code/mcp.json` or project `.mcp.json`:
```json
{
  "mcpServers": {
    "praxis-os": {
      "type": "streamableHttp",
      "url": "http://127.0.0.1:4242/mcp",
      "transport": "http"
    }
  }
}
```

**Important**:
- Replace `4242` with actual port from `.praxis-os/.mcp_server_state.json`
- Use `127.0.0.1` (not `localhost`)
- Include `/mcp` path in URL

#### If Claude Code in VS Code (External)

Edit VS Code's `.vscode/settings.json`:
```json
{
  "claude-code.mcpServers": {
    "praxis-os": {
      "type": "streamableHttp",
      "url": "http://127.0.0.1:4242/mcp",
      "transport": "http"
    }
  }
}
```

**Important**:
- Must specify `"type": "streamableHttp"` explicitly!
- Replace `4242` with actual port from `.praxis-os/.mcp_server_state.json`
- Use `127.0.0.1` (not `localhost`) for consistency
- Include `/mcp` path in URL

## Step 4: Start/Reload Claude Code

- **If extension in Cursor**: Reload Cursor window
- **If CLI**: `claude-code` in terminal
- **If VS Code**: Reload VS Code window

## Step 5: Validate Multi-Agent Setup

### Test 1: Cursor (Primary)

In Cursor:
```
"Use pos_search_project to query: orientation bootstrap"
```

**Expected**: Native MCP works

### Test 2: Claude Code (Secondary)

In Claude Code:
```
"Use pos_search_project to query: python testing patterns"
```

**Expected**: HTTP connection works, same results as Cursor

### Test 3: Shared State

1. **Cursor**: Start a workflow
2. **Claude Code**: Query workflow state

Both should see same state (shared MCP server).

## Differences from Primary Claude Code

| Aspect | Primary | Secondary |
|--------|---------|-----------|
| **MCP Server** | Claude Code starts/stops | Cursor starts/stops |
| **Connection** | Direct | HTTP (Streamable HTTP) |
| **Port** | N/A | Dynamic (4242-5242 range, from state file) |
| **Independence** | Standalone | Depends on Cursor |
| **Performance** | Slightly faster | Minimal HTTP overhead (~10-50ms) |
| **Configuration** | Manual setup | Helper script reads state file |

## Troubleshooting

### Claude Code Can't Connect

**Symptom**: "Failed to connect to MCP server"

**Check**:
```bash
# Read port from state file
PORT=$(cat .praxis-os/.mcp_server_state.json | grep -o '"port": [0-9]*' | grep -o '[0-9]*')
echo "Testing: http://127.0.0.1:${PORT}/mcp"

# Verify HTTP endpoint
curl http://127.0.0.1:${PORT}/mcp

# Check Cursor's MCP server logs
```

**Solutions**:
- Ensure Cursor is running
- **Check Cursor configuration** - Ensure `.cursor/mcp.json` uses absolute paths (not `${workspaceFolder}`)
- Verify dual transport in `.cursor/mcp.json` (`--transport dual`)
- Check port allocation: `cat .praxis-os/.mcp_server_state.json`
- Verify port not blocked: `lsof -i :${PORT}` (Mac/Linux) or `netstat -ano | findstr :${PORT}` (Windows)
- Check Cursor logs at `~/Library/Application Support/Cursor/logs/` for actual errors
- Try different port (server automatically finds next available)
- Restart Cursor

### Port Conflict

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
- Check for stale processes: `ps aux | grep ouroboros`
- Restart Cursor to retry port allocation

### Both Agents Show Different State

**Symptom**: Cursor and Claude Code see different workflows

**Root cause**: Not connected to same MCP server

**Check**:
```bash
# Should see only ONE ouroboros process
ps aux | grep ouroboros
```

**Solutions**:
- Only one agent should be primary
- Close other Claude Code instances running as primary
- Restart Cursor to ensure single MCP instance

### Slow HTTP Performance

**Expected**: HTTP adds ~10-50ms latency

**If much slower**:
- Check localhost not firewalled
- Verify Cursor's MCP server healthy (test via Cursor first)
- Check system resources

### Cursor Works, Claude Code Doesn't

**Symptom**: Cursor can use tools, Claude Code cannot

**Check**:
```bash
# Get port from state file
PORT=$(cat .praxis-os/.mcp_server_state.json | grep -o '"port": [0-9]*' | grep -o '[0-9]*')

# Test HTTP endpoint
curl -X POST http://127.0.0.1:${PORT}/mcp -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'

# Verify Claude Code config
cat ~/.config/claude-code/mcp.json  # or appropriate path
```

**Solutions**:
- Ensure `--transport dual` in Cursor's mcp.json (not `--http`)
- Verify URL: `http://127.0.0.1:${PORT}/mcp` (use port from state file, include `/mcp` path)
- Check Claude Code logs/output
- Restart both Cursor and Claude Code

## When to Use Secondary vs Primary

### Use Secondary (Claude Code in Cursor) When:
- ✅ Already using Cursor as main IDE
- ✅ Want specialized agent for specific tasks
- ✅ Multi-agent workflow with handoffs

### Use Primary (Claude Code standalone) When:
- ✅ Claude Code is your main agent
- ✅ Don't use Cursor
- ✅ Single-agent workflow

## Multi-Agent Workflow Patterns

### Pattern 1: Role-Based

1. **Cursor**: Architecture, planning, high-level design
2. **Claude Code**: Detailed implementation, testing
3. **Cursor**: Review, integration

### Pattern 2: Specialized Tools

1. **Cursor**: General development
2. **Claude Code**: Browser testing via `pos_browser`
3. **Cursor**: Process results

### Pattern 3: Parallel Development

1. **Cursor**: Frontend development
2. **Claude Code**: Backend development
3. Shared: Both use same `pos_workflow` and `pos_search_project`

## Security Considerations

### HTTP Endpoint

`http://127.0.0.1:PORT/mcp` is:
- **Local only** - Not accessible from network (127.0.0.1 binding)
- **No authentication** - Anyone on localhost can connect
- **Same machine required** - Both agents on same computer
- **Dynamic port** - Port allocated automatically (4242-5242 range)

**Risk**: Other local processes can connect

**Mitigation**:
- Only enable dual transport when using secondary agents (use `stdio` mode otherwise)
- Port binding restricted to 127.0.0.1 (not 0.0.0.0)
- Stop MCP server when not in use (close Cursor)

### Shared State

Both agents share workflow state:
- Claude Code can modify Cursor's workflows
- Coordinate to avoid conflicts
- Designate one agent as "workflow owner"

## Next Steps

✅ **Multi-agent setup complete!**

Now:
1. **Test both agents**: Verify both can access prAxIs OS tools
2. **Define roles**: Decide which agent does what
3. **Coordinate**: Use shared workflow state effectively
4. **Iterate**: Refine workflow based on experience

See also:
- [Cursor Integration](../cursor/) - Primary agent setup
- [Claude Code Terminal](./terminal.md) - CLI mode
- [Claude Code in VS Code](./vscode.md) - VS Code integration
- [Understanding Workflows](../../../tutorials/understanding-praxis-os-workflows.md)

